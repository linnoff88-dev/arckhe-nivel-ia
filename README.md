# nivel-ia: em que degrau a IA estÃ¡ no seu trabalho?

[![Escada da IA: AL1 a AL5](guia/assets/banner.jpg)](https://inematds.github.io/nivel-ia/guia/)

**ðŸ‡§ðŸ‡· [PortuguÃªs](README.md) Â· ðŸ‡ºðŸ‡¸ [English](README.en.md) Â· ðŸ‡ªðŸ‡¸ [EspaÃ±ol](README.es.md)**

## O que Ã©

Sem medir, vocÃª nÃ£o sabe o que ainda faz na mÃ£o, o que a IA jÃ¡ faz sozinha e quais portas abriu para ela. Este kit dÃ¡ uma rÃ©gua de cinco degraus, do AL1 (vocÃª faz sozinho) ao AL5 (a IA roda sozinha), e duas formas de medir: uma ficha de papel, que serve para qualquer pessoa e qualquer IA, e um programa que lÃª os registros do Claude Code e do Codex no seu computador e anota cada conexÃ£o usada. No fim, vocÃª sabe em que degrau estÃ¡ cada tarefa, qual pode subir agora e quando descer. Para comeÃ§ar, basta imprimir a ficha.

## ðŸ“– Guia de uso

Guia completo (landing + passo a passo): **https://inematds.github.io/nivel-ia/guia/**

## Em detalhe

Kit aberto e gratuito para medir quanto do seu trabalho a IA jÃ¡ faz, tarefa por tarefa, na **escada AL1 a AL5**. VocÃª mede **no papel** (uma ficha para imprimir) ou **automaticamente** (um programa lÃª os registros do Claude Code e do Codex na sua mÃ¡quina). Os dois anotam **todas as conexÃµes** que a IA usou e dizem **quem pode subir um degrau** e quando descer.

| Degrau | O que Ã© |
|---|---|
| AL1 | VocÃª faz sozinho. A IA nÃ£o entra. |
| AL2 | A IA ajuda: vocÃª pergunta, ela responde, vocÃª faz. |
| AL3 | A IA colabora: juntos, passo a passo, vocÃª conduz. |
| AL4 | A IA conduz e vocÃª sÃ³ revisa antes de sair. |
| AL5 | A IA roda sozinha, com horÃ¡rio, regra e alarme. |

A escada completa, com **como subir cada degrau e quando descer**, estÃ¡ em [ESCADA.md](ESCADA.md).

## O processo, do inÃ­cio ao fim

Quem faz: ðŸ§  vocÃª Â· âš™ï¸ script ou timer

1. ðŸ§  **Leia a escada** e escolha 3 tarefas que vocÃª faz toda semana: [ESCADA.md](ESCADA.md).
2. ðŸ§  **No papel:** imprima a ficha (https://inematds.github.io/nivel-ia/kit/ficha-papel.html) e anote uma linha por tarefa (data, tarefa, crÃ­tica? s/n, degrau 1 a 5, minutos, conexÃ£o usada, corrigi? n/p/g, erro grave? s/n). Serve para qualquer IA e para o que vocÃª faz sem IA (AL1).
3. ðŸ§  **Digite a ficha** (opcional): copie `kit/papel-modelo.csv` para `registro/papel.csv`, abra numa planilha, digite as linhas e salve como CSV. Confira com `python3 medir/nivel.py papel`. Quem sÃ³ usa a ficha pode pular os passos 4 e 6: o relatÃ³rio sai sÃ³ com ela.
4. âš™ï¸ **AutomÃ¡tico:** `python3 medir/nivel.py varrer --dias 30` lÃª os logs do Claude Code e do Codex desta mÃ¡quina e grava `registro/sessoes.json`.
5. âš™ï¸ **RelatÃ³rio:** `python3 medir/nivel.py relatorio` monta a escada, as tarefas, o prÃ³ximo degrau de cada uma, as conexÃµes e "quem pode subir agora" em `registro/relatorio.md` (junta a ficha de papel se existir).
6. âš™ï¸ **Todas as conexÃµes:** `python3 medir/nivel.py conexoes` lista cada programa, site, serviÃ§o, agente e skill, com a primeira e a Ãºltima vez.
7. âš™ï¸ **Todo dia sozinho:** `sh systemd/instalar.sh` liga um timer Ã s 06:20 que repete os passos 4 e 5 e guarda o histÃ³rico em `registro/historico.jsonl`.
8. âš™ï¸ **Certificado:** `python3 medir/certificado.py --nome "Seu Nome"` gera `registro/certificado-AAAA-MM-DD.html`: degrau, escada AL1â€“AL5, tarefas, evoluÃ§Ã£o semana a semana e projeÃ§Ã£o (1, 3 e 6 meses). Abre no navegador e vira PDF no botÃ£o. PerÃ­odo maior: `nivel.py --registro /tmp/n90 varrer --dias 90`, `nivel.py --registro /tmp/n90 relatorio` e `certificado.py --nome "Seu Nome" --registro /tmp/n90`.
9. ðŸ§  **Uma vez por semana:** leia o relatÃ³rio, escolha UMA tarefa para subir um degrau (critÃ©rios em ESCADA.md) e desÃ§a a que errou feio.

## ðŸŽ“ Certificado: passo a passo

Uma pÃ¡gina com o % do seu trabalho conduzido pela IA, a escada AL1â€“AL5, as tarefas principais, a evoluÃ§Ã£o semana a semana e a projeÃ§Ã£o para 1, 3 e 6 meses. Ã‰ HTML: abre em qualquer navegador e vira PDF no botÃ£o "Salvar em PDF".

**Jeito mais fÃ¡cil (forma B): peÃ§a Ã  sua IA.** Abra o Claude Code ou o Codex e cole (troque o nome). Dados confidenciais? Use o jeito do terminal, logo abaixo (veja Privacidade).

> Baixe o kit https://github.com/inematds/nivel-ia numa pasta nivel-ia (se jÃ¡ existir, use ela), meÃ§a os meus Ãºltimos 30 dias com `python3 medir/nivel.py varrer --dias 30` e `python3 medir/nivel.py relatorio`, gere o meu certificado com `python3 medir/certificado.py --nome "Seu Nome"` e abra o certificado no navegador. No fim, me diga onde ficaram o certificado e o relatÃ³rio e resuma em 3 linhas o que deu. NÃ£o abra o arquivo registro/sessoes.json e nÃ£o envie os meus dados para nenhum outro serviÃ§o nem site.

**VocÃª mesmo, comando por comando** (Linux ou Mac; no Windows, WSL; Python 3.9+; ter usado o Claude Code ou o Codex nesta mÃ¡quina):

```bash
git clone https://github.com/inematds/nivel-ia && cd nivel-ia
python3 medir/nivel.py varrer --dias 30          # 1. mede os Ãºltimos 30 dias (nada sai da mÃ¡quina)
python3 medir/nivel.py relatorio                 # 2. monta o relatÃ³rio
python3 medir/certificado.py --nome "Seu Nome"   # 3. gera o certificado (em inglÃªs/espanhol: --lang en / --lang es)
xdg-open registro/certificado-*.html             # 4. abre (no Mac: open) â†’ botÃ£o "Salvar em PDF"
```

PerÃ­odo maior (ex.: 90 dias), sem mexer no registro diÃ¡rio: `python3 medir/nivel.py --registro /tmp/n90 varrer --dias 90`, `python3 medir/nivel.py --registro /tmp/n90 relatorio` e `python3 medir/certificado.py --nome "Seu Nome" --registro /tmp/n90`. O Claude Code apaga registros com mais de 30 dias, a nÃ£o ser que vocÃª aumente o `cleanupPeriodDays`; o que jÃ¡ foi apagado nÃ£o volta. Se os registros cobrirem menos dias do que o pedido, o medidor avisa no terminal, no relatÃ³rio e no certificado.

**Onde ficam os arquivos**

| Arquivo | O que Ã© |
|---|---|
| `registro/certificado-AAAA-MM-DD.html` | O certificado (abra no navegador â†’ "Salvar em PDF") |
| `registro/relatorio.md` | O relatÃ³rio completo: escada, tarefas, prÃ³ximo degrau, quem pode subir, conexÃµes |
| `registro/relatorio.json` | Os mesmos nÃºmeros em dados (o certificado lÃª daqui) |
| `registro/sessoes.json` | A mediÃ§Ã£o sessÃ£o por sessÃ£o (sÃ³ na sua mÃ¡quina, fora do git) |

## Requisitos

Terminal, Python 3.9 ou mais novo (sÃ³ biblioteca padrÃ£o, sem instalar nada) e git para baixar (ou baixe o ZIP: https://github.com/inematds/nivel-ia/archive/refs/heads/main.zip). Linux ou macOS (no Windows, use o WSL). O timer usa systemd (Linux). Sem rede, sem API: nada sai da sua mÃ¡quina.

## O que a mediÃ§Ã£o automÃ¡tica vÃª e nÃ£o vÃª

- **VÃª:** sessÃµes do Claude Code (`~/.claude/projects`) e do Codex (`~/.codex*/sessions`), quantas mensagens suas, quantas aÃ§Ãµes da IA, quanto tempo, que programas, sites, serviÃ§os (MCP), agentes e skills ela usou, e quais aÃ§Ãµes tiveram efeito fora da mÃ¡quina (publicar, enviar, subir).
- **NÃ£o vÃª:** o que vocÃª faz sem IA (AL1: sÃ³ na ficha), outras IAs (ChatGPT no navegador: ficha), se vocÃª aprovou no prompt, e se a IA acertou (coluna "corrigi?" da ficha).
- **Como decide o degrau:** sessÃ£o aberta por script, bot ou horÃ¡rio (`claude -p`, `codex exec`) com atÃ© 2 mensagens = AL5 (3 ou mais = conversa); pedido seu feito pelo bot (Telegram) = AL4; conversa sua no terminal: 15 ou mais aÃ§Ãµes da IA por mensagem sua = AL4, 5 a 14 = AL3, menos = AL2 (uma pergunta solta Ã© AL2).
- **Subir e descer:** conferidos pelas colunas "corrigi?" (n/p/g) e "erro grave?" (s/n) da ficha. AL1â†’AL2 sem critÃ©rio; AL2â†’AL3: no mÃ¡ximo 1 correÃ§Ã£o grande nas Ãºltimas 10 vezes; AL3â†’AL4: no mÃ¡ximo 2 em 20; AL4â†’AL5: no mÃ¡ximo 2 em 50 e nenhum erro grave. Descer: 1 erro grave ou 3 correÃ§Ãµes grandes nas Ãºltimas 10. SÃ³ contam as vezes do degrau atual (mudou de degrau, a conta recomeÃ§a). Tarefa crÃ­tica (marcada na ficha ou reconhecida pelas palavras: publicar, cliente, servidor, e-mailâ€¦) para no AL4. Sem ficha, o relatÃ³rio lista a tarefa como candidata e diz quantas vezes anotar. Detalhes em [ESCADA.md](ESCADA.md). Os limites ficam no topo de `medir/nivel.py`.
- **Tarefas:** agrupadas por palavras-chave do primeiro pedido. Para usar as suas, copie `medir/tarefas.exemplo.json` para `medir/tarefas.json` e edite (formato `[["Nome da tarefa", crÃ­tica true/false, ["palavra", "outra"]]]`). Tarefa crÃ­tica para no AL4.

## Exemplo real

[exemplo/relatorio-agregado.json](exemplo/relatorio-agregado.json): a mediÃ§Ã£o do trabalho do Nei Maldaner (INEMA) em 30 dias, sÃ³ com totais (sem pedidos, pastas nem sites).

## Testes

`python3 tests/run.py` (46 testes com logs falsos, nada da sua mÃ¡quina).

## Privacidade

**Duas formas de rodar.** O medidor Ã© Python puro e roda sÃ³ na sua mÃ¡quina, sem internet. **A. Pelo terminal**: vocÃª roda os comandos e abre o certificado; nada sai do computador. **B. Pedindo Ã  sua IA**: o Claude Code ou o Codex roda os comandos e lÃª o relatÃ³rio para resumir, e essa leitura passa pelo servidor do provedor (Anthropic ou OpenAI), como qualquer sessÃ£o. O relatÃ³rio traz os nomes das tarefas e as conexÃµes (programas, agentes, skills e sites). Esses nomes podem revelar o nome de um cliente ou de um projeto. **Dados confidenciais (trabalho de cliente, sigilo): use a forma A.**

`registro/` fica fora do git. O primeiro pedido de cada sessÃ£o Ã© guardado curto e com chaves, e-mails e nÃºmeros longos trocados por `[oculto]`.

LicenÃ§a MIT Â· kit aberto e gratuito Â· [inema.club](https://inema.club)

---

Projeto adaptado da comunidade INEMA TDS - Marca Arckhe