"""Gera o painel do Divisor a partir de todos os relatórios (.docx ou .html exportado do Google Docs) de uma pasta.
Uso: python3 build_panel.py <pasta_com_relatorios> <saida.html> [--artifact]
"""
import sys, os, glob, json
from datetime import datetime
from parse_divisor import parse

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
tpl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template.html'), encoding='utf-8').read()
html = tpl.replace('/*__DATA__*/[]', json.dumps(reports, ensure_ascii=False))
if '--artifact' in sys.argv:
    # versão para publicar como Artifact: sem doctype/html/head/body (o publicador adiciona)
    import re
    html = re.sub(r'(?is)<!doctype html>|</?html[^>]*>|</?head>|<meta[^>]*>|</?body>', '', html).strip()
open(out, 'w', encoding='utf-8').write(html)
print(f'{len(reports)} relatório(s) -> {out}')
