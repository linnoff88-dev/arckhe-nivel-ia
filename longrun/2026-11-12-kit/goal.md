# Goal — nivel-ia (kit novo, substitui niveis-autonomia)

- **Início:** 2026-11-12 14:38 · **Agente:** Claude (sessão wifi) · **Tetos:** 4 h · memória 8 G por varredura

## Resultado
Repo `inematds/nivel-ia`, autônomo: escada AL1–AL5 do vídeo do Nei, medição no papel e automática (Claude Code + Codex) com registro de TODAS as conexões, seção clara "como subir de nível" (cada degrau: o que precisa ser verdade, quem decide, quando descer), guia PT/EN/ES no Pages, portal, INEMA.AGENTES, vídeo com avatar no lives3.

## Ordens do Nei (citadas)
- Telegram 12/11 03:10: "projeto com kit sobre os 5 níveis de autonomia do seu trabalho ... ensinar as pessoas a medir seja fazendo uma lista no papel ou seja monitorando ... importante todas as conexões que você tem que seja registrado ... publique no portal e coloca no lives3 e no inema.agentes"
- Terminal 12/11: "os níveis é de 1 a 5 e não 0 a 4", "não está muito claro como se evolui", "o vídeo foi criado sem avatar", "criar um projeto novo ... nivel-ia e crie tudo novamente".

## Critérios de pronto
**Função**
- [ ] `python3 tests/run.py` → todos passam, ≥ 15 testes (contagem conferida no fim do run)
- [ ] `python3 medir/nivel.py varrer --dias 30 && python3 medir/nivel.py relatorio` nos logs do Nei → parte AL4+AL5 entre 55% e 72% (FATOS: 64%) e lista de conexões com ≥ 20 itens
- [ ] `grep -c "AL[0]" guia/index.html` → 0 ; `grep -o "AL[1-5]" guia/index.html | sort -u | wc -l` → 5
- [ ] guia tem `id="subir"` com 4 degraus (AL1→2, 2→3, 3→4, 4→5) e um bloco "quando descer"
- [ ] `curl -s -o /dev/null -w '%{http_code}' https://inematds.github.io/nivel-ia/guia/` (e /en/ /es/) → 200

**Regressão / limite**
- [ ] `git ls-files registro/` → só `.gitkeep` (nada pessoal no repo público)
- [ ] repo/portal/vídeo/post do niveis-autonomia intocados (`git -C ~/projetos/niveis-autonomia status --short` vazio)
- [ ] nada de API paga; avatar só pelo estúdio HeyGen; nenhum número de terceiros (Anthropic 26%) no guia

**Teste rápido:** `python3 tests/run.py` · **Completo:** critérios acima + revisor independente
