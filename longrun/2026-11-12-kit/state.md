# Estado — nivel-ia (12/11/2026, ~23:35) — PUBLICADO (repo, Pages, portal, Telegram, vídeo lives1)

## Feito
- Bloqueio 1 resolvido: as 1.202 sessões "AL5 com conversa" eram todas Claude `sdk-cli` (app/bot interativo, até 56 mensagens). Regra nova: AL5 só se aberta por SDK/exec com até 2 mensagens humanas (`CONVERSA_MIN = 3`). Resultado: 56,2% (AL2 3,3 · AL3 40,5 · AL4 28,2 · AL5 28,0), dentro da faixa 55–72%.
- Palavras-chave das tarefas casam no começo da palavra ('apagou' ≠ 'pago'); 'client' removido. 44 testes passam.
- exemplo/relatorio-agregado.json regerado; Caso real PT reescrito e EN/ES retraduzidos pelo inema-traduz (só o trecho); regra AL5 atualizada em guia/README/ESCADA nos 3 idiomas. Commit b055839.
- systemd/instalar.sh rodado: timer nivel-ia 06:20.
- GitHub: inematds/nivel-ia público, Pages por Actions; 3 guias + 3 fichas + banners = 200.
- Portal: 9bf6c61 (card + projectUpdatesData + EN/ES 10214), inemabuscas df35321, inemapro c6af002.
- Telegram INEMA.AGENTES: tópico 7175, MENU msg 7193.
- Vídeo com avatar (escolha do Nei): lives1 OO92qphODKE (legenda não sobe nos lives), embutido no guia PT/EN/ES (#video, b7aa87e), quadro de vídeos do portal 6c807f0, link no inemaytbot (msg 3544). lives1 não tem marca no Metricool: não foi.

## Pendente (decisão do Nei)
- Card/timer/repo antigo niveis-autonomia: tirar ou manter (não mexido).
