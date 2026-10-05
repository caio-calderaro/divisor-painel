"""Converte um Relatório Divisor (.docx, ou .html exportado do Google Docs) em JSON estruturado."""
import docx, re, json, sys, os
from docx.table import Table
from docx.text.paragraph import Paragraph

def iter_blocks(d):
    for el in d.element.body.iterchildren():
        tag = el.tag.split('}')[1]
        if tag == 'p': yield Paragraph(el, d)
        elif tag == 'tbl': yield Table(el, d)

def rows(t):
    return [[c.text.strip() for c in _uniq(r.cells)] for r in t.rows]

def _uniq(cells):
    seen, res = set(), []
    for c in cells:
        if id(c._tc) in seen: continue
        seen.add(id(c._tc)); res.append(c)
    return res

def kv(t):
    d = {}
    for r in rows(t):
        if len(r) >= 2 and r[0] and r[1]: d[r[0]] = r[1]
    return d

def num(s):
    s = re.sub(r'[^\d,.-]', '', s or '')
    if not s: return None
    s = s.replace('.', '').replace(',', '.')
    try: return float(s)
    except: return None

def _image(d, par):
    """Imagem embutida num parágrafo (ex.: gráfico do Google Trends) como data URI, já comprimida."""
    import base64, io
    for blip in par._p.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}blip'):
        rid = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
        part = d.part.related_parts.get(rid)
        if part is None: continue
        data, mime = part.blob, part.content_type
        try:
            from PIL import Image
            im = Image.open(io.BytesIO(data)).convert('RGB')
            if im.width > 1100: im = im.resize((1100, round(im.height * 1100 / im.width)))
            buf = io.BytesIO(); im.save(buf, 'WEBP', quality=78); data, mime = buf.getvalue(), 'image/webp'
        except Exception: pass
        return f'data:{mime};base64,' + base64.b64encode(data).decode()
    return None

def parse(path):
    if path.lower().endswith(('.html', '.htm')):
        import subprocess, tempfile
        raw = open(path, 'rb').read()
        if not raw.lstrip().startswith(b'<'):
            import base64; raw = base64.b64decode(raw)
        tmp = tempfile.mkdtemp()
        h = os.path.join(tmp, 'in.html'); open(h, 'wb').write(raw)
        out = os.path.join(tmp, os.path.basename(path).rsplit('.', 1)[0] + '.docx')
        subprocess.run(['pandoc', h, '-o', out], check=True)
        r = parse(out)
        return r
    d = docx.Document(path)
    report = {"date": None, "products": []}
    fname = os.path.basename(path)
    m = re.search(r'(\d{2})(\d{2})(\d{4})', fname)
    cur = None
    pending = None  # formato novo: título da seção numa tabela e os dados na tabela seguinte
    for b in iter_blocks(d):
        if isinstance(b, Paragraph):
            if cur is not None and pending == 'trends_img':
                img = _image(d, b)
                if img: cur['trends_img'] = img; pending = None
            tx = b.text.strip()
            m2 = re.search(r'(\d{2}/\d{2}/\d{4})', tx)
            if m2 and not report["date"]: report["date"] = m2.group(1)
            m3 = re.fullmatch(r'-{2,}\s*(.+?)\s*-{2,}', tx)
            if m3:
                cur = {"name": m3.group(1)}; report["products"].append(cur)
            continue
        if cur is None: continue
        r = rows(b); head = (r[0][0] if r and r[0] else '').upper()
        if len(r) == 1 and ('TRÁFEGO' in head or 'TRAFEGO' in head or 'PALAVRA' in head):
            pending = 'traffic' if 'PALAVRA' not in head else 'kw'; continue
        if 'GOOGLE TRENDS' in head and len(r) == 1:
            pending = 'trends_img'; continue
        if pending == 'traffic' and head.startswith('MÉTRICA'): head = 'TRÁFEGO'
        elif pending == 'kw' and head.startswith('PALAVRA'): head = 'PALAVRA'
        pending = None
        if 'PRODUTO OCULTO' in head:
            cur['hidden'] = True
        elif 'IDENTIFICA' in head:
            k = kv(b)
            cur.update(platform=k.get('Plataforma'), name=k.get('Nome do Produto', cur['name']),
                       site=k.get('Site Produtor'), country=k.get('País'),
                       commission_usd=num(k.get('Comissão')), commission_raw=k.get('Comissão'))
            if k.get('Afiliação'): cur.setdefault('aff_process', k.get('Afiliação'))
        elif 'TRÁFEGO' in head or 'TRAFEGO' in head:
            hdr = next((x for x in r if x and x[0].lower().startswith('métrica')), None)
            months = hdr[1:4] if hdr else ['M1','M2','M3']
            cur['months'] = months
            for x in r:
                if len(x) < 5: continue
                lab = x[0].lower(); key = 'trends' if 'trends' in lab else 'searches' if 'busca' in lab else 'visits' if 'acesso' in lab else None
                if key: cur[key] = {"values": [num(v) for v in x[1:4]], "note": x[4], "months": months}
        elif 'PALAVRA' in head:
            k = kv(b)
            if k.get('Palavra-chave') and k.get('Palavra-chave') != 'Tipo de Correspondência':
                # formato chave/valor: "Palavra-chave | termo" e "Tipo de Correspondência | EXATA"
                cur['keywords'] = [{"term": k['Palavra-chave'], "match": k.get('Tipo de Correspondência', '')}]
            else:
                # formato lista: cabeçalho "Palavra-chave | Tipo de Correspondência" e uma linha por termo
                kws = [x for x in r if len(x) >= 2 and x[0] and 'PALAVRA' not in x[0].upper() and 'TIPO DE CORRESP' not in x[1].upper()]
                cur['keywords'] = [{"term": x[0], "match": x[1]} for x in kws]
        elif 'CAMPANHA' in head:
            k = kv(b); cur['cpa'] = k.get('Estratégia CPA'); cur['stop'] = k.get('STOP')
            cur['campaign_extra'] = [[a, v] for a, v in k.items() if a not in ('Estratégia CPA', 'STOP') and 'CAMPANHA' not in a.upper()]
        elif 'AFILIA' in head:
            k = kv(b); cur['aff_platform'] = k.get('Plataforma'); cur['aff_process'] = k.get('Processo') or cur.get('aff_process')
            cur['aff_link'] = k.get('Link do Site')
    if not report['date'] and m: report['date'] = f"{m.group(1)}/{m.group(2)}/{m.group(3)}"
    return report

if __name__ == '__main__':
    print(json.dumps(parse(sys.argv[1]), ensure_ascii=False, indent=1))
