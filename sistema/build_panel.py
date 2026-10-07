"""Gera o painel do Divisor a partir de todos os relatórios (.docx ou .html exportado do Google Docs) de uma pasta.
Uso: python3 build_panel.py <pasta_com_relatorios> <saida.html> [--artifact]

Além do <saida.html> (página completa, usada no GitHub Pages), grava na mesma pasta:
  - hubla_embed.html -> código para colar na Hubla (uma vez só): <iframe> apontando para o GitHub Pages.
"""
import sys, os, glob, json, base64, re
from datetime import datetime
from parse_divisor import parse
from render import render

HERE = os.path.dirname(os.path.abspath(__file__))
src, out = sys.argv[1], sys.argv[2]
reports = []
for f in glob.glob(os.path.join(src, '*.docx')) + glob.glob(os.path.join(src, '*.html')):
    if os.path.basename(f).startswith('~$'): continue
    r = parse(f)
    if r['products'] and r['date']:
        reports.append(r)
# um relatório por data (o último arquivo com a mesma data vence), mais novo primeiro
by_date = {r['date']: r for r in reports}
reports = sorted(by_date.values(), key=lambda r: datetime.strptime(r['date'], '%d/%m/%Y'), reverse=True)

tpl = open(os.path.join(HERE, 'template.html'), encoding='utf-8').read()
font = base64.b64encode(open(os.path.join(HERE, 'fonte', 'plus-jakarta-sans-latin.woff2'), 'rb').read()).decode()
week_css, body = render(reports)  # HTML pronto: funciona mesmo se o iframe bloquear JavaScript
html = (tpl.replace('__FONT__', 'data:font/woff2;base64,' + font)
           .replace('/*__WEEK_CSS__*/', week_css).replace('<!--__BODY__-->', body))

if '--artifact' in sys.argv:
    # versão para publicar como Artifact: sem doctype/html/head/body (o publicador adiciona)
    html = re.sub(r'(?is)<!doctype html>|</?html[^>]*>|</?head>|<meta[^>]*>|</?body>', '', html).strip()
open(out, 'w', encoding='utf-8').write(html)

# ---- código de incorporação para a área de membros (Hubla) ----
# A Hubla só aceita iframe apontando para um link público. O GitHub Pages publica o index.html
# nesse link e a tarefa de segunda o atualiza, então o código abaixo é colado UMA vez e não muda.
URL = 'https://caio-calderaro.github.io/divisor-painel/'
STYLE = 'width:100%;height:88vh;min-height:680px;border:0;border-radius:16px;display:block'
d = os.path.dirname(os.path.abspath(out))
open(os.path.join(d, 'hubla_embed.html'), 'w', encoding='utf-8').write(
    f'<iframe title="Painel Divisor" src="{URL}" style="{STYLE}" allow="clipboard-write" loading="lazy"></iframe>\n')
alt = os.path.join(d, 'hubla_embed_alternativo.html')
if os.path.exists(alt): os.remove(alt)

print(f'{len(reports)} relatório(s) -> {out} (+ hubla_embed.html)')
