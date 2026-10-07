# Painel Divisor

Página: https://caio-calderaro.github.io/divisor-painel/

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
- `sistema/template.html` é o visual; `sistema/fonte/` é a fonte Plus Jakarta Sans (licença OFL)
