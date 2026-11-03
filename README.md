# Painel Divisor e Divisor PRO

- Divisor (semanal): https://caio-calderaro.github.io/divisor-painel/
- Divisor PRO (quinzenal, só Pós-Formação): https://caio-calderaro.github.io/divisor-painel/pro/

Os dois painéis saem do mesmo gerador. O nome do arquivo separa os relatórios: arquivos com "PRO"
(ex.: `Relatório_divisorPRO_30.10.docx`) entram só no PRO; os outros, só no Divisor.
Gerar o PRO: `python3 sistema/build_panel.py <pasta> pro/index.html --pro` (visual em `sistema/template_pro.html`).
Para a Hubla do PRO, cole `pro/hubla_embed.html`.

O `index.html` é gerado automaticamente toda segunda por uma tarefa agendada do Claude,
a partir dos relatórios na pasta "Relatório" do Google Drive. Não edite os `.html` à mão.

## Colocar na área de membros (Hubla)

Cole o conteúdo de `hubla_embed.html` no bloco de iframe/código da aula, uma vez só:

```html
<iframe title="Painel Divisor" src="https://caio-calderaro.github.io/divisor-painel/" style="width:100%;height:88vh;min-height:680px;border:0;border-radius:16px;display:block" allow="clipboard-write" loading="lazy"></iframe>
```

A Hubla só aceita iframe com link público (confirmado pelo suporte deles). Esse link é o GitHub Pages,
que a tarefa de segunda atualiza; o iframe mostra sempre a versão mais nova, sem colar de novo.

## Sistema

- `sistema/parse_divisor.py` lê cada relatório (Word ou Google Docs exportado), nos dois formatos de tabela já usados
- `sistema/render.py` monta o HTML estático do painel
- `sistema/build_panel.py` junta todas as semanas e gera `index.html` e `hubla_embed.html`
- `sistema/template.html` é o visual do Divisor e `sistema/template_pro.html` o do PRO; `sistema/fonte/` tem as fontes Plus Jakarta Sans e Fraunces (licença OFL)
