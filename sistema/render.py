"""Renderiza o painel como HTML estático (sem depender de JavaScript).
Semanas e detalhes dos produtos abrem com CSS puro (radio/checkbox), para funcionar mesmo
quando a área de membros bloqueia scripts dentro do iframe."""
import re
from html import escape as _e
from urllib.parse import quote

MESES = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']

def esc(s): return _e('' if s is None else str(s), quote=True)

def _br(n, dec=0):
    s = f'{n:,.{dec}f}'
    return s.replace(',', 'X').replace('.', ',').replace('X', '.')

def fmt(n): return '—' if n is None else _br(n)
def usd(n): return '—' if n is None else 'US$ ' + _br(n, 2)

def label_date(d):
    dd, mm, yy = d.split('/'); return f'{int(dd)} {MESES[int(mm) - 1]} {yy}'

def trend(v):
    if not v or not v.get('values'): return 'flat', '—'
    a, b = v['values'][0], v['values'][-1]
    if a is None or b is None: return 'flat', '—'
    if not a: return ('up', '▲ novo') if b > 0 else ('flat', '—')
    p = (b - a) / a * 100
    if abs(p) < 5: return 'flat', '● estável'
    if p >= 300: return 'up', f'▲ {_br(b / a)}x'
    return ('up' if p > 0 else 'down'), ('▲ ' if p > 0 else '▼ ') + _br(abs(p)) + '%'

def last(v): return v['values'][-1] if v and v.get('values') else None

def cap(s): return s[:1].upper() + s[1:] if s else s

def chart(v, months):
    if not v or not v.get('values'): return ''
    mx = max([x or 0 for x in v['values']] + [1])
    bars = ''.join(f'<div class="bar"><b>{fmt(x)}</b><i style="height:{max(4, (x or 0) / mx * 80):.0f}%"></i><span>{esc(months[i] if i < len(months) else "")}</span></div>'
                   for i, x in enumerate(v['values']))
    return f'<div class="chart">{bars}</div>'

def copy_box(txt, label='Copiar'):
    return f'<div class="copy"><code>{esc(txt)}</code><button type="button" class="cbtn" data-copy="{esc(txt)}">{label}</button></div>'

def traffic_block(title, v, months):
    if not v: return ''
    c, t = trend(v)
    note = f'<div class="note">{esc(v.get("note"))}</div>' if v.get('note') else ''
    return f'<div><div class="subt">{title}<span class="tr {c}">{t}</span></div>{chart(v, v.get("months") or months)}{note}</div>'

def drawer(p, i, pid):
    m = p.get('months') or []
    steps = [s.strip() for s in (p.get('aff_process') or '').split('+') if s.strip()]
    stop = p.get('stop') or ''
    sm = re.match(r'^(.*?)\s*(?:\((.*)\)|[—–-]\s*(.*))$', stop)
    stop_val = sm.group(1).strip() if sm else stop
    stop_why = (sm.group(2) or sm.group(3) or '').strip() if sm else ''
    kws = p.get('keywords') or []
    kw0 = kws[0]['term'] if kws else ''
    lock = ' <span class="lock">🔒 Exclusivo</span>' if p.get('hidden') else ''
    site_lbl = re.sub(r'/$', '', re.sub(r'^https?://', '', p.get('site') or ''))
    trends_chart = traffic_block('Interesse no Google Trends (0–100)', p.get('trends'), m)
    trends_img = (f'<div><div class="subt">Google Trends (EUA)</div><img class="timg" src="{p["trends_img"]}" '
                  f'alt="Gráfico do Google Trends para {esc(p.get("name"))}"></div>') if p.get('trends_img') else ''
    trends_link = (f'<a class="btn ghost" href="https://trends.google.com/trends/explore?date=today%203-m&amp;geo=US&amp;q={quote(kw0)}" '
                   f'target="_blank" rel="noopener">Ver “{esc(kw0)}” no Google Trends (EUA, 90 dias) ↗</a>') if kw0 else ''
    resumo = (f"{p.get('name')}\nPlataforma: {p.get('platform')}\nComissão: {usd(p.get('commission_usd'))}\n"
              f"Palavra-chave: {', '.join('[' + k['term'] + '] (' + k['match'] + ')' for k in kws)}\n"
              f"CPA: {p.get('cpa')}\nSTOP: {stop}\nAfiliação: {p.get('aff_process')} — {p.get('aff_link')}")
    return f'''<div class="drawer" role="dialog" aria-label="{esc(p.get('name'))}">
  <div class="dh"><div class="rank">{i + 1}</div><div><h2>{esc(p.get('name'))}{lock}</h2><div class="plat">{esc(p.get('platform'))} · {esc(p.get('country') or '')} · {usd(p.get('commission_usd'))} por venda</div></div><label for="{pid}" class="x" aria-label="Fechar">✕</label></div>
  <div class="db">
    <div class="blk"><h5><em>1</em>Identificação</h5>
      <div class="rowk"><span>Plataforma</span><b>{esc(p.get('platform'))}</b></div>
      <div class="rowk"><span>Produto</span><b>{esc(p.get('name'))}</b></div>
      <div class="rowk"><span>País</span><b>{esc(p.get('country'))}</b></div>
      <div class="rowk"><span>Comissão</span><b style="color:var(--brand-ink)">{usd(p.get('commission_usd'))}</b></div>
      <div class="rowk"><span>Site do produtor</span><b><a href="{esc(p.get('site'))}" target="_blank" rel="noopener">{esc(site_lbl)} ↗</a></b></div>
    </div>
    <div class="blk"><h5><em>2</em>Tráfego · últimos 3 meses</h5><div class="tw">
      {traffic_block('Volume de buscas (palavra-chave)', p.get('searches'), m)}
      {traffic_block('Acessos ao site do produtor', p.get('visits'), m)}
      {trends_chart}{trends_img}{trends_link}
    </div></div>
    <div class="blk"><h5><em>3</em>Palavra-chave</h5>
      {''.join(f'<div class="rowk"><span>Correspondência</span><b>{esc(k["match"])}</b></div>' + copy_box('[' + k['term'] + ']') for k in kws)}
    </div>
    <div class="blk"><h5><em>4</em>Configuração da campanha</h5>
      <div class="rowk"><span>Estratégia de lance</span><b>CPA desejado</b></div>
      <div class="cpa"><b>{esc(p.get('cpa') or '—')}</b></div>
      {''.join(f'<div class="rowk"><span>{esc(k)}</span><b>{esc(v)}</b></div>' for k, v in (p.get('campaign_extra') or []))}
      <div class="stop"><span>⛔</span><div><b>STOP em {esc(stop_val)}</b><br>{esc(cap(stop_why))}</div></div>
    </div>
    <div class="blk"><h5><em>5</em>Afiliação</h5>
      <div class="rowk"><span>Plataforma</span><b>{esc(p.get('aff_platform'))}</b></div>
      <div class="steps">{''.join(f'<div class="step"><i>{j + 1}</i>{esc(cap(s))}</div>' for j, s in enumerate(steps))}</div>
      <div class="all"><a class="btn" href="{esc(p.get('aff_link'))}" target="_blank" rel="noopener">Abrir site do produto ↗</a></div>
    </div>
    <button type="button" class="btn ghost cbtn" data-copy="{esc(resumo)}">Copiar resumo da campanha</button>
  </div>
</div>'''

def week_section(r, w):
    P = r['products']
    top = sorted(P, key=lambda p: -(p.get('commission_usd') or 0))[0]
    growing = sum(1 for p in P if trend(p.get('visits'))[0] == 'up')
    quick = sum(1 for p in P if re.fullmatch(r'1 clique', (p.get('aff_process') or '').strip(), re.I))
    plats = list(dict.fromkeys(p.get('platform') for p in P if p.get('platform')))
    cards = []
    for i, p in enumerate(P):
        pid = f'p{w}_{i}'
        sc, st = trend(p.get('searches')); vc, vt = trend(p.get('visits'))
        lock = ' <span class="lock">🔒 Exclusivo</span>' if p.get('hidden') else ''
        cards.append(f'''<div class="pc"><input type="checkbox" class="tg" id="{pid}" aria-label="Ver campanha de {esc(p.get('name'))}">
<label for="{pid}" class="card">
  <div class="h"><div class="rank">{i + 1}</div><div><h3>{esc(p.get('name'))}{lock}</h3><div class="plat">{esc(p.get('platform'))} · {esc(p.get('country') or '')}</div></div>
    <div class="comm"><b>{usd(p.get('commission_usd'))}</b><span>comissão</span></div></div>
  <div class="metrics">
    <div class="m"><div class="l">Buscas / mês</div><div class="v"><b>{fmt(last(p.get('searches')))}</b><span class="tr {sc}">{st}</span></div></div>
    <div class="m"><div class="l">Acessos no site</div><div class="v"><b>{fmt(last(p.get('visits')))}</b><span class="tr {vc}">{vt}</span></div></div>
  </div>
  <div class="foot"><span class="tag">{esc(p.get('aff_process') or '')}</span><span class="go">Ver campanha →</span></div>
</label>
<label for="{pid}" class="scrim" aria-hidden="true"></label>
{drawer(p, i, pid)}</div>''')
    return f'''<section class="week week{w}">
  <section class="hero">
    <div class="eyb">Relatório Divisor · {label_date(r['date'])}</div>
    <h1>{len(P)} produtos validados para anunciar no Google esta semana</h1>
    <p>Mercado EUA. Cada produto já vem com palavra-chave, CPA e STOP definidos. Escolha, afilie-se e suba a campanha.</p>
    <div class="kpis">
      <div class="kpi"><b>{usd(top.get('commission_usd'))}</b><span>Maior comissão · {esc(top.get('name'))}</span></div>
      <div class="kpi"><b>{growing} de {len(P)}</b><span>Com acessos em alta</span></div>
      <div class="kpi"><b>{quick}</b><span>Afiliação em 1 clique</span></div>
      <div class="kpi"><b>{len(plats)}</b><span>{esc(' · '.join(plats))}</span></div>
    </div>
  </section>
  <div class="sec-t"><h2>Produtos da semana</h2><span>Toque em um produto para ver a campanha completa</span></div>
  <div class="grid">{''.join(cards)}</div>
  <p class="disc">Este relatório não garante resultados financeiros. Os resultados variam conforme a execução de cada aluno.</p>
</section>'''

LOGO = ('<svg viewBox="0 0 32 32"><rect x="12" y="2" width="8" height="28" rx="2" fill="var(--brand)"/>'
        '<rect x="2" y="12" width="28" height="8" rx="2" fill="var(--brand)"/><rect x="12" y="12" width="8" height="8" fill="var(--brand-ink)"/></svg>')

def render(reports):
    """Devolve (css_das_semanas, corpo_html)."""
    if not reports:
        return '', '<div class="wrap"><p style="padding:40px 0">Nenhum relatório ainda.</p></div>'
    radios = ''.join(f'<input type="radio" name="wk" class="wkr" id="w{w}"{" checked" if w == 0 else ""} aria-label="Semana {label_date(r["date"])}">'
                     for w, r in enumerate(reports))
    new = '<span class="new">NOVO</span>'
    side = ''.join(f'<label for="w{w}" class="wk wk{w}"><span class="d"></span>Semana {label_date(r["date"])}{new if w == 0 else ""}</label>'
                   for w, r in enumerate(reports))
    chips = ''.join(f'<label for="w{w}" class="chip wk{w}">{label_date(r["date"])}{" · novo" if w == 0 else ""}</label>'
                    for w, r in enumerate(reports))
    weeks = ''.join(week_section(r, w) for w, r in enumerate(reports))
    css = ''.join(f'#w{w}:checked~.layout .week{w}{{display:block}}'
                  f'#w{w}:checked~.layout .side .wk{w}{{background:var(--surface);color:var(--ink);box-shadow:var(--shadow)}}'
                  f'#w{w}:checked~.layout .side .wk{w} .d{{background:var(--brand)}}'
                  f'#w{w}:checked~.layout .chips .wk{w}{{background:var(--brand);border-color:var(--brand);color:#fff}}'
                  f'#w{w}:focus-visible~.layout .wk{w}{{outline:2px solid var(--brand);outline-offset:2px}}\n'
                  for w in range(len(reports)))
    body = f'''{radios}
<header class="top"><div class="wrap">
  <div class="logo">{LOGO}Divisor</div>
  <span class="pill"><i></i>Relatório semanal</span>
  <div class="sp"></div>
</div></header>
<div class="wrap layout">
  <aside class="side"><h4>Relatórios</h4><nav>{side}</nav></aside>
  <main><nav class="chips" aria-label="Semanas">{chips}</nav>{weeks}</main>
</div>'''
    return css, body
