"""Gera o painel do Divisor a partir de todos os relatórios (.docx ou .html exportado do Google Docs) de uma pasta.
Uso: python3 build_panel.py <pasta_com_relatorios> <saida.html> [--artifact] [--pro]

Sem --pro: painel do Divisor (semanal). Usa só os relatórios SEM "PRO" no nome do arquivo.
Com --pro: painel do Divisor PRO (quinzenal, Pós-Formação). Usa só os relatórios com "PRO" no nome
(ex.: Relatório_divisorPRO_30.10.docx) e o visual de template_pro.html. Saída padrão: pro/index.html.

Além do <saida.html> (página completa, usada no GitHub Pages), grava na mesma pasta:
  - hubla_embed.html -> código para colar na Hubla (uma vez só): <iframe> apontando para o GitHub Pages.
"""
import sys, os, glob, json, base64, re
from datetime import datetime
from parse_divisor import parse
from render import render

HERE = os.path.dirname(os.path.abspath(__file__))
src, out = sys.argv[1], sys.argv[2]
PRO = '--pro' in sys.argv
# O time às vezes salva os dois relatórios na mesma pasta: o nome do arquivo separa Divisor e Divisor PRO.
IS_PRO = re.compile(r'divisor[\s_.-]*pro', re.I)
reports = []
for f in glob.glob(os.path.join(src, '*.docx')) + glob.glob(os.path.join(src, '*.html')):
    if os.path.basename(f).startswith('~$'): continue
    if bool(IS_PRO.search(os.path.basename(f))) != PRO: continue
    r = parse(f)
    if r['products'] and r['date']:
        reports.append(r)
# O painel mostra cada relatório pela SEGUNDA-FEIRA em que ele é entregue (a mais próxima da data
# escrita no Word): o relatório feito na sexta 09/10 aparece como "12 out". A data original fica em
# report_date. Se dois relatórios caírem na mesma segunda, vale o mais recente.
from datetime import timedelta
def monday(d):
    dt = datetime.strptime(d, '%d/%m/%Y'); wd = dt.weekday()  # 0 = segunda
    return dt - timedelta(days=wd) if wd <= 3 else dt + timedelta(days=7 - wd)
by_date = {}
for r in sorted(reports, key=lambda r: datetime.strptime(r['date'], '%d/%m/%Y')):
    r['report_date'] = r['date']; r['date'] = monday(r['date']).strftime('%d/%m/%Y')
    by_date[r['date']] = r
reports = sorted(by_date.values(), key=lambda r: datetime.strptime(r['date'], '%d/%m/%Y'), reverse=True)
# numeração sequencial dos relatórios: o mais antigo é o nº 1
for i, r in enumerate(reports): r['num'] = len(reports) - i

tpl = open(os.path.join(HERE, 'template_pro.html' if PRO else 'template.html'), encoding='utf-8').read()
def font64(name): return 'data:font/woff2;base64,' + base64.b64encode(open(os.path.join(HERE, 'fonte', name), 'rb').read()).decode()
font = font64('plus-jakarta-sans-latin.woff2')[len('data:font/woff2;base64,'):]
if PRO: tpl = tpl.replace('__FONT_SERIF__', font64('fraunces-latin-600.woff2'))
week_css, body = render(reports, 'pro' if PRO else 'divisor')  # HTML pronto: funciona mesmo se o iframe bloquear JavaScript
html = (tpl.replace('__FONT__', 'data:font/woff2;base64,' + font)
           .replace('/*__WEEK_CSS__*/', week_css).replace('<!--__BODY__-->', body))

if '--artifact' in sys.argv:
    # versão para publicar como Artifact: sem doctype/html/head/body (o publicador adiciona)
    html = re.sub(r'(?is)<!doctype html>|</?html[^>]*>|</?head>|<meta[^>]*>|</?body>', '', html).strip()
open(out, 'w', encoding='utf-8').write(html)

# ---- código de incorporação para a área de membros (Hubla) ----
# A Hubla só aceita iframe apontando para um link público. O GitHub Pages publica o index.html
# nesse link e a tarefa de segunda o atualiza, então o código abaixo é colado UMA vez e não muda.
URL = 'https://caio-calderaro.github.io/divisor-painel/' + ('pro/' if PRO else '')
TITLE = 'Painel Divisor PRO' if PRO else 'Painel Divisor'
STYLE = 'width:100%;height:88vh;min-height:680px;border:0;border-radius:16px;display:block'
d = os.path.dirname(os.path.abspath(out))
open(os.path.join(d, 'hubla_embed.html'), 'w', encoding='utf-8').write(
    f'<iframe title="{TITLE}" src="{URL}" style="{STYLE}" allow="clipboard-write" loading="lazy"></iframe>\n')
alt = os.path.join(d, 'hubla_embed_alternativo.html')
if os.path.exists(alt): os.remove(alt)

print(f'{len(reports)} relatório(s) -> {out} (+ hubla_embed.html)')
