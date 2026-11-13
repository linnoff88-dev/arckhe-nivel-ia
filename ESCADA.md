# A escada de domínio da IA: AL1 a AL5

O nível é de **uma tarefa**, não da pessoa nem da IA. A mesma pessoa pode estar no AL5 em "traduzir legendas" e no AL2 em "responder cliente".

| Degrau | O que é | Quem faz o quê | Exemplo: responder e-mail de cliente |
|---|---|---|---|
| **AL1** | Você faz sozinho | A IA não entra. | Você lê, pensa, escreve e envia. |
| **AL2** | A IA ajuda | Você pergunta, ela responde, você faz. | Você pergunta "como respondo isso?" e escreve a resposta. |
| **AL3** | A IA colabora | Trabalham juntos, passo a passo. Você conduz cada passo. | A IA escreve o rascunho com você, você ajusta e envia. |
| **AL4** | A IA conduz, você revisa | Ela prepara tudo; você confere antes de sair. | A IA deixa a resposta pronta; você lê, aprova e ela envia. |
| **AL5** | A IA roda sozinha | Sistema com horário, regra e alarme, sem você no meio. | As perguntas de rotina são respondidas sozinhas; você só vê o resumo e as exceções. |

Na dúvida, faça três perguntas sobre a tarefa:
1. **A IA entrou?** Não → AL1.
2. **Quem fez o trabalho?** Você, com a resposta dela → AL2. Os dois, passo a passo → AL3. Ela, e você conferiu antes de sair → AL4.
3. **Você estava lá?** Não, rodou sozinha → AL5.

## Como anotar (a mesma regra na ficha e no programa)

Cada vez que fizer a tarefa, uma linha na ficha (data como dd/mm/aaaa ou aaaa-mm-dd) com o degrau em que você **fez** a tarefa naquela vez, se a tarefa é **crítica** (s/n; em branco, o programa decide pelas palavras do nome: publicar, post, cliente, pagamento, dinheiro, servidor, e-mail) e duas colunas de acerto:

- **corrigi?** `n` = não precisei mexer · `p` = correção pequena (vírgula, tom) · `g` = correção grande (refiz um pedaço, ou a resposta não ajudou).
- **erro grave?** `s` quando saiu errado para fora, perdeu dado ou gastou o que não devia; senão `n`.

Só as correções **grandes** e os erros **graves** entram nas contas abaixo, e só as vezes do **degrau atual**: quando você sobe ou desce, a conta daquela tarefa recomeça. A ficha em inglês ou espanhol pode usar y/yes/sí no lugar de `g`/`s`.

## Como subir de nível

Uma tarefa por vez, **um degrau por vez**. **Quem decide é você.** O relatório confere as contas abaixo na sua ficha e diz "pode subir", "anote mais N vezes", "continue no degrau" ou "descer"; se você discordar dele, vale a sua decisão, anotada com o motivo. Os números são ponto de partida: ajuste ao risco da sua tarefa.

### AL1 → AL2: comece a perguntar
- **Escolha:** uma tarefa que você repete pelo menos 3 vezes por mês e que não tem dado sigiloso.
- **Faça:** antes de fazer na mão, pergunte à IA como ela faria e compare com o seu jeito. A partir daí você já está no AL2: anote AL2 na ficha.
- **Critério:** nenhum. Perguntar tem risco baixo; a régua começa a contar no AL2.

### AL2 → AL3: dê o contexto e trabalhe junto
- **Sinal:** você copia a resposta e faz sempre os mesmos ajustes.
- **Faça:** escreva uma vez o contexto fixo (quem é o cliente, o tom, exemplos bons, onde ficam os arquivos) e entregue junto com o pedido.
- **Pronto para subir quando:** nas últimas **10 vezes** no AL2, no máximo **1** teve correção grande.

### AL3 → AL4: deixe a IA conduzir, você revisa
- **Sinal:** você aprova quase tudo que ela propõe sem mudar.
- **Faça:** escreva o que é "pronto" (uma lista de conferência curta). A IA faz a tarefa inteira e para antes do efeito externo (enviar, publicar, pagar). Você confere pela lista e aprova.
- **Pronto para subir quando:** nas últimas **20 vezes** no AL3, no máximo **2** tiveram correção grande.

### AL4 → AL5: ponha para rodar sozinha, com trava
- **Só para tarefa não crítica.** Tarefa em que um erro causa prejuízo público, financeiro ou de segurança (publicar, dinheiro, servidor, cliente) **para no AL4**: a IA conduz, você revisa.
- **Antes de soltar:** horário fixo, teto de tempo e de custo, alarme quando der erro, registro de tudo que ela fez e um jeito de voltar ao AL4 em um minuto.
- **Pronto para subir quando:** nas últimas **50 vezes** no AL4, no máximo **2** tiveram correção grande e nenhuma teve erro grave.
- **Depois de subir:** abra 3 resultados por semana e anote na ficha, para não dormir no ponto.

## Quando descer

- **Um erro grave** → desce **um degrau** naquela tarefa na hora.
- **Três correções grandes nas últimas 10 vezes** → desce um degrau. (Como subir aceita no máximo 2, as duas regras nunca se contradizem.)
- A ferramenta, o modelo ou o processo mudou → volte um degrau por conta própria até medir de novo (o relatório não sabe disso: é decisão sua).
- Vale para qualquer degrau, inclusive o que já roda sozinho no AL5.
- Anote o motivo. Descer não é fracasso: é o registro funcionando.

## O que medir para decidir

| Pergunta | Onde ver |
|---|---|
| Em que degrau está cada tarefa? | `relatorio.md` → "Suas tarefas" (ou a coluna nível da ficha) |
| O que já roda sozinho e eu nem lembrava? | AL5 no relatório: sessões abertas por script, bot ou horário, com até 2 mensagens |
| Quais portas eu abri para a IA? | "Conexões registradas": programa, site, serviço, agente, skill e o que você anotou na ficha, com a primeira e a última vez (pastas e arquivos só na ficha) |
| Quem pode subir ou descer agora? | "Pode subir" e "Descer um degrau" no relatório, conferidos pelas colunas "corrigi?" e "erro grave?" da ficha |
| A IA acertou? | Só a ficha diz: colunas "corrigi?" e "erro grave?". O medidor mede liberdade, não acerto. |

## De onde vem esta escada

A escada AL1–AL5 é a do vídeo do Nei Maldaner "Qual o nível que você domina a IA?" (INEMA, 12/11/2026), em que ele mostra a própria medição: 64% do trabalho dele já conduzido pela IA (AL4 + AL5) num mês. É a mesma escada do kit [relogio-2027](https://inematds.github.io/relogio-2027/guia/).
