# Painel Divisor

Página: https://caio-calderaro.github.io/divisor-painel/

O `index.html` é gerado automaticamente toda segunda por uma tarefa agendada do Claude,
a partir dos relatórios na pasta "Relatório" do Google Drive. Não edite o `index.html` à mão.

- `sistema/parse_divisor.py` lê cada relatório (Word ou Google Docs exportado)
- `sistema/build_panel.py` junta todas as semanas e gera o `index.html`
- `sistema/template.html` é o visual do painel
