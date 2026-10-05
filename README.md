# Painel Divisor

Página: https://caio-calderaro.github.io/divisor-painel/

O `index.html` é gerado automaticamente toda segunda por uma tarefa agendada do Claude,
a partir dos relatórios na pasta "Relatório" do Google Drive. Não edite os `.html` à mão.

## Colocar na área de membros (Hubla)

Abra `hubla_embed.html`, copie **todo** o conteúdo e cole no bloco de código/HTML da aula.
É um `<iframe srcdoc="...">` com o painel inteiro dentro: não busca nada em servidor nenhum
(fonte, dados e gráficos do Google Trends vão embutidos).

- Funciona mesmo se a Hubla bloquear JavaScript no iframe: semanas e detalhes dos produtos abrem só com CSS.
  Sem JavaScript, só os botões "Copiar" somem (a palavra-chave continua selecionável).
- Se a Hubla remover o atributo `srcdoc`, use `hubla_embed_alternativo.html` (mesmo painel via `data:`).
- O código é uma "foto" do painel: quando sair relatório novo, cole o código novo.

## Sistema

- `sistema/parse_divisor.py` lê cada relatório (Word ou Google Docs exportado), nos dois formatos de tabela já usados
- `sistema/render.py` monta o HTML estático do painel
- `sistema/build_panel.py` junta todas as semanas e gera `index.html`, `hubla_embed.html` e `hubla_embed_alternativo.html`
- `sistema/template.html` é o visual; `sistema/fonte/` é a fonte Plus Jakarta Sans (licença OFL)
