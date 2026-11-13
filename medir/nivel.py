#!/usr/bin/env python3
"""nivel-ia: mede em que degrau da escada AL1–AL5 está o seu trabalho com IA
e registra TODAS as conexões que a IA usou (programas, sites, serviços, agentes, skills).

Só lê arquivos da sua máquina: logs do Claude Code (~/.claude/projects) e do Codex
(~/.codex*/sessions). Não chama API, não manda nada para fora. Só biblioteca padrão.

A escada (o nível vem do que ficou registrado no log, não de opinião):
  AL1  você faz sozinho, a IA não entra ........ só no papel (registro/papel.csv)
  AL2  a IA ajuda: você pergunta, ela responde .. conversa com menos de 5 ações da IA por mensagem sua
  AL3  a IA colabora, passo a passo com você .... 5 a 14 ações por mensagem sua
  AL4  a IA conduz e você só revisa ............. 15 ou mais ações por mensagem sua, ou pedido seu feito pelo bot (Telegram)
  AL5  a IA roda sozinha ......................... sessão aberta por script, bot ou timer (claude -p, codex exec) com até 2 mensagens

Uso:
  nivel.py varrer    [--dias 30]          lê os logs e grava registro/sessoes.json
  nivel.py relatorio [--json]              escada, tarefas, conexões, quem pode subir → registro/relatorio.md
  nivel.py conexoes                        lista todas as conexões (primeira e última vez)
  nivel.py papel                           confere registro/papel.csv (a ficha de papel digitada)
"""
import argparse
import collections
import csv
import glob
import io
import json
import os
import re
import signal
import sys
import time
from datetime import date, datetime, timezone
from multiprocessing import Pool
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
REGISTRO = RAIZ / 'registro'
PAUSA = 10 * 60          # intervalo maior que 10 min entre duas mensagens não conta como tempo ativo
LIMITE_AL4 = 15          # ações da IA por mensagem sua
LIMITE_AL3 = 5
CONVERSA_MIN = 3        # mensagens humanas a partir das quais uma sessão por SDK conta como conversa
NOMES = {'AL1': 'Você faz sozinho', 'AL2': 'A IA ajuda', 'AL3': 'A IA colabora',
         'AL4': 'A IA conduz, você revisa', 'AL5': 'A IA roda sozinha'}
NIVEIS = list(NOMES)
IDIOMAS = ('pt', 'en', 'es')
FONTE = {'claude': 'Claude Code', 'codex': 'Codex'}


def idioma(lang='pt'):
    """textos do relatório e do certificado (medir/idiomas_<lang>.json); pt é a fonte, en/es saem do tradutor"""
    lang = lang if lang in IDIOMAS else 'pt'
    return json.loads((Path(__file__).resolve().parent / f'idiomas_{lang}.json').read_text(encoding='utf-8'))


_PT = None


def _d(acao, chave, **p):
    """decisão com o motivo em português (compatível) + chave e parâmetros para traduzir no relatório"""
    global _PT
    _PT = _PT or idioma('pt')
    q = dict(p)
    if chave == 'grave_em' and not q.get('data'):
        q['data'] = _PT['motivos']['grave_alguma']
    return {'acao': acao, 'motivo': _PT['motivos'][chave].format(**q), 'chave': chave, 'p': p}

SEGREDO = re.compile(r'(sk-[A-Za-z0-9_\-]{12,}|gh[pousr]_[A-Za-z0-9]{20,}|xox[abp]-[A-Za-z0-9\-]{10,}|AIza[0-9A-Za-z_\-]{20,}'
                     r'|[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[a-z]{2,}|\b\d{9,}\b)')
MOLDURA = re.compile(r'^\s*(# AGENTS\.md instructions|<command-(name|message)>|<environment_context>|<user_instructions>|This session is being continued|Caveat: The messages below)')  # texto que o programa injeta, não é o pedido
BASTIDORES = ('claude-mem', 'observer tool', 'you are a claude-mem')

# efeito fora da máquina: publicar, enviar, subir, mexer em servidor
EXTERNO = re.compile(
    r'(git\s+push|gh\s+(pr|issue|release|repo)\s+(create|merge|close|edit|delete)|gh\s+api\s+.*-X\s*(POST|PUT|PATCH|DELETE)|'
    r'curl\s+[^|;]*(-X\s*(POST|PUT|PATCH|DELETE)|\s-d\s|--data|-F\s)|yt-pubx\s+publicar|scp\s|rsync\s.*:|ssh\s|'
    r'sendMessage|send_message|wrangler\s+(deploy|publish)|npm\s+publish|docker\s+push)', re.I)
LEITURA_MCP = re.compile(r'(^|_)(get|list|read|search|show|query|status|view|fetch|describe|whoami|stats|doctor|find|check|preview|wait)', re.I)
# comandos de bastidor que não contam como conexão (são o "mexer no arquivo" de todo dia)
RUIDO = set('ls cat head tail grep rg find wc echo pwd stat du df jq sort uniq cut tr file which date env printf test [ type ps diff tree '
            'for do done if then fi while cd sed awk xargs timeout bash sh until sleep pgrep kill nohup set export source mkdir cp mv '
            'touch chmod ln rm true false read wait trap exit return local tee basename dirname realpath readlink seq'.split())

HEREDOC = re.compile(r"<<-?\s*['\"]?(\w+)['\"]?.*?\n.*?\n\s*\1\b", re.S)  # corpo de script embutido não é programa
PALAVRAS_CODIGO = set('import from def class return assert with as in is not and or print const let var function async await '
                      'elif else try except finally raise pass lambda yield global del break continue new end '
                      'select insert update delete where por para'.split())

# tarefas por palavra-chave do primeiro pedido; troque à vontade em medir/tarefas.json
TAREFAS_PADRAO = [
    ['Traduzir conteúdo', False, ['traduz', 'translate', 'espanhol', 'inglês', 'spanish', 'english']],
    ['Produzir vídeos', False, ['vídeo', 'video', 'reel', 'short', 'avatar', 'roteiro', 'youtu', 'legenda']],
    ['Clientes e dinheiro', True, ['cliente', 'customer', 'orçamento', 'cobran', 'pagar', 'pagamento', 'pago', 'dinheiro', 'money', 'payment', 'invoice', 'fatura', 'factura']],
    ['Publicar e divulgar', True, ['publica', 'publish', 'telegram', 'postar', 'post ', 'portal', 'instagram', 'tiktok', 'metricool']],
    ['Criar cursos e aulas', False, ['curso', 'aula', 'trilha', 'módulo']],
    ['Criar guias, kits e sites', False, ['guia', 'kit', 'repo', 'projeto', 'landing', 'site', 'página']],
    ['Pesquisar e resumir', False, ['resum', 'pesquis', 'analis', 'notícia', 'artigo', 'relatório', 'classifi']],
    ['Imagens e design', False, ['imagem', 'thumb', 'capa', 'banner', 'logo', 'design']],
    ['Manter sistemas e bots', True, ['bot', 'servidor', 'server', 'vps', 'timer', 'painel', 'deploy', 'backup']],
    ['E-mail e agenda', True, ['e-mail', 'email', 'gmail', 'correo', 'agenda', 'calendar']],
]


# ---------------------------------------------------------------- leitura dos logs
MARCA_BOT = re.compile(r'\[Mensagem do usuário via [^\]]*\]\s*')


def limpa(texto):
    texto = MARCA_BOT.split(str(texto))[-1]  # pedido que veio pelo bot: só a mensagem da pessoa, sem a identidade do bot
    return SEGREDO.sub('[oculto]', ' '.join(str(texto).split()))[:200]


def epoch(s):
    try:
        return datetime.fromisoformat(str(s).replace('Z', '+00:00')).timestamp()
    except ValueError:
        return None


def ativo(tempos):
    tempos.sort()
    return sum(b - a for a, b in zip(tempos, tempos[1:]) if b - a <= PAUSA) / 60


def cabeca(cmd):
    """Programas que o comando chamou (sem os de bastidor) e os sites citados."""
    out = []
    cmd = HEREDOC.sub('', str(cmd))
    for parte in re.split(r'\s*(?:&&|\|\||;|\||\n)\s*', cmd):
        toks = [t for t in re.sub(r'^[\s({]+', '', parte).split() if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*=', t)]
        while toks and toks[0] in ('sudo', 'timeout', 'nohup', 'env', 'time', 'exec'):
            toks = toks[1:]
            while toks and re.match(r'^-|^\d+[smh]?$', toks[0]):
                toks = toks[1:]
        if not toks:
            continue
        nome = os.path.basename(toks[0]).strip('"\'')
        if nome in ('python3', 'python', 'node', 'bash', 'sh') and len(toks) > 1 and not toks[1].startswith('-'):
            nome = f'{nome} {os.path.basename(toks[1])}'
        if re.match(r'^[a-z][\w.\-]+( [\w.\-]+)?$', nome) and nome.split()[0] not in RUIDO and nome.split()[0] not in PALAVRAS_CODIGO:
            out.append('programa:' + nome[:40])
    out += ['site:' + h.lower() for h in re.findall(r'https?://([A-Za-z0-9.\-]+)', str(cmd))[:3]]
    return out


def nova_sessao(fonte, caminho):
    return dict(fonte=fonte, arquivo=os.path.basename(caminho), pasta='', humanos=0, acoes=0, externo=0,
                primeiro='', tempos=[], conexoes=collections.Counter())


def fecha(s):
    if not s['tempos']:
        return None
    s['inicio'] = min(s['tempos'])
    s['minutos'] = round(ativo(s.pop('tempos')), 1)
    # AL5 = ninguém conversando: aberta por script, bot ou timer (claude -p / codex exec) ou sem nenhuma mensagem sua.
    # Uma pergunta solta no terminal NÃO é AL5: vai pela conta de ações por mensagem (AL2 a AL4).
    # Aberta por SDK/exec mas com 3+ mensagens humanas = alguém conversando (app, bot interativo): não é AL5.
    s['automatica'] = (bool(s.get('automatica')) and s['humanos'] < CONVERSA_MIN) or s['humanos'] == 0
    s['primeiro'] = limpa(s['primeiro'])
    s['conexoes'] = dict(s['conexoes'])
    s['nivel'] = nivel(s)
    return s


def nivel(s):
    if s.get('via_bot'):  # pedido de uma pessoa pelo bot (Telegram etc.): a IA conduz o pedido inteiro e a pessoa revisa o resultado
        return 'AL4'
    if s['automatica']:
        return 'AL5'
    k = s['acoes'] / max(s['humanos'], 1)
    return 'AL4' if k >= LIMITE_AL4 else 'AL3' if k >= LIMITE_AL3 else 'AL2'


def ler_claude(caminho):
    s = nova_sessao('claude', caminho)
    try:
        with open(caminho, 'rb') as fh:
            for bruto in fh:
                if b'"user"' not in bruto[:400] and b'"assistant"' not in bruto:
                    continue
                try:
                    d = json.loads(bruto)
                except ValueError:
                    continue
                tipo = d.get('type')
                if tipo not in ('user', 'assistant') or d.get('isSidechain'):
                    continue
                s['pasta'] = s['pasta'] or d.get('cwd') or ''
                if d.get('entrypoint') and 'automatica' not in s:
                    s['automatica'] = d['entrypoint'] != 'cli'  # sdk-cli/sdk-ts = claude -p chamado por script, bot ou timer
                x = epoch(d.get('timestamp'))
                if x:
                    s['tempos'].append(x)
                c = (d.get('message') or {}).get('content')
                if tipo == 'user':
                    texto = c if isinstance(c, str) else ''
                    if isinstance(c, list) and not any(isinstance(b, dict) and b.get('type') == 'tool_result' for b in c):
                        texto = ' '.join(str(b.get('text', '')) for b in c if isinstance(b, dict) and b.get('type') == 'text')
                    if texto and (not texto.startswith('<') or '<command-name>' in texto):
                        s['humanos'] += 1
                        if MARCA_BOT.search(texto):
                            s['via_bot'] = True
                        if not MOLDURA.match(texto):
                            s['primeiro'] = s['primeiro'] or texto
                elif isinstance(c, list):
                    for b in c:
                        if isinstance(b, dict) and b.get('type') == 'tool_use':
                            s['acoes'] += 1
                            conexoes_claude(s, b.get('name', ''), b.get('input') or {})
    except OSError:
        return None
    return fecha(s)


def conexoes_claude(s, nome, inp):
    cx = s['conexoes']
    if nome == 'Bash':
        cmd = str(inp.get('command', ''))
        for k in cabeca(cmd):
            cx[k] += 1
        if EXTERNO.search(cmd):
            s['externo'] += 1
    elif nome.startswith('mcp__'):
        partes = nome.split('__')
        cx['serviço:' + (partes[1] if len(partes) > 1 else '?')] += 1
        if not LEITURA_MCP.search(partes[-1]):
            s['externo'] += 1
    elif nome in ('Agent', 'Task'):
        cx['agente:' + str(inp.get('subagent_type') or 'geral')[:30]] += 1
    elif nome == 'Skill':
        cx['skill:' + str(inp.get('skill', '?'))[:40]] += 1
    elif nome in ('WebSearch', 'WebFetch'):
        cx['web:busca' if nome == 'WebSearch' else 'web:página'] += 1
        m = re.match(r'https?://([A-Za-z0-9.\-]+)', str(inp.get('url', '')))
        if m:
            cx['site:' + m.group(1).lower()] += 1


def ler_codex(caminho):
    s = nova_sessao('codex', caminho)
    try:
        with open(caminho, 'rb') as fh:
            for bruto in fh:
                try:
                    d = json.loads(bruto)
                except ValueError:
                    continue
                p = d.get('payload') or {}
                if d.get('type') == 'session_meta':
                    s['pasta'] = p.get('cwd') or ''
                    s['automatica'] = p.get('originator') == 'codex_exec'
                    continue
                if d.get('type') != 'response_item':
                    continue
                x = epoch(d.get('timestamp'))
                if x:
                    s['tempos'].append(x)
                t = str(p.get('type'))
                if t in ('function_call', 'custom_tool_call', 'local_shell_call'):
                    if p.get('name') == 'wait':
                        continue
                    s['acoes'] += 1
                    corpo = str(p.get('arguments') or p.get('input') or p.get('action') or '')
                    for cmd in re.findall(r'cmd"?\s*:\s*"((?:[^"\\]|\\.)*)"', corpo) or ([corpo] if t == 'local_shell_call' else []):
                        cmd = cmd.encode().decode('unicode_escape', 'ignore') if '\\' in cmd else cmd
                        for k in cabeca(cmd):
                            s['conexoes'][k] += 1
                        if EXTERNO.search(cmd):
                            s['externo'] += 1
                    for ferramenta in set(re.findall(r'tools\.(\w+)\(', corpo)) - {'exec_command', 'write_stdin', 'apply_patch', 'update_plan'}:
                        s['conexoes']['serviço:codex ' + ferramenta] += 1
                    if p.get('name') and p.get('name') not in ('exec', 'exec_command', 'shell', 'apply_patch', 'update_plan'):
                        s['conexoes']['serviço:codex ' + p['name']] += 1
                elif t == 'message' and p.get('role') == 'user':
                    texto = ' '.join(str(b.get('text', '')) for b in p.get('content') or [] if isinstance(b, dict))
                    if texto and not texto.lstrip().startswith('<') and not MOLDURA.match(texto):
                        s['humanos'] += 1
                        s['primeiro'] = s['primeiro'] or texto
    except OSError:
        return None
    return fecha(s)


def ler(item):
    fonte, caminho = item
    return ler_claude(caminho) if fonte == 'claude' else ler_codex(caminho)


# ---------------------------------------------------------------- tarefas
def carregar_tarefas():
    arq = RAIZ / 'medir' / 'tarefas.json'
    if arq.exists():
        return json.loads(arq.read_text(encoding='utf-8'))
    return TAREFAS_PADRAO


def tarefa_de(texto, tarefas):
    t = texto.lower()
    for nome, _critica, palavras in tarefas:
        if any(re.search(r'(?<!\w)' + re.escape(p), t) for p in palavras):  # palavra começa ali: 'apagou' não é 'pago'
            return nome
    return 'Outras tarefas'


# ---------------------------------------------------------------- ficha de papel
COLUNAS_PAPEL = ['data', 'tarefa', 'nivel', 'minutos', 'conexao', 'corrigi', 'grave']


def data_iso(t):
    """aaaa-mm-dd fica; dd/mm/aaaa ou dd/mm/aa vira aaaa-mm-dd (para as "últimas vezes" saírem na ordem certa)."""
    t = str(t).strip()
    m = re.match(r'^(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})$', t)
    if m:
        d, mes, a = m.groups()
        a = ('20' + a) if len(a) == 2 else a
        return f'{a}-{int(mes):02d}-{int(d):02d}'
    return t


def chave_coluna(k):
    k = re.sub(r'[¿?¡!:()]', '', (k or '').strip().lower())
    k = re.sub(r'\s+', ' ', k).strip()
    if k in SINONIMOS or k in COLUNAS_PAPEL:
        return SINONIMOS.get(k, k)
    for nome in sorted(list(SINONIMOS) + COLUNAS_PAPEL + ['critica'], key=len, reverse=True):  # "Degrau (1 a 5)", "Conexão usada (qual IA...)"
        if k.startswith(nome):
            return SINONIMOS.get(nome, nome)
    return k


SINONIMOS = {'step': 'nivel', 'degrau': 'nivel', 'peldaño': 'nivel', 'peldano': 'nivel', 'rung': 'nivel', 'degrau 1 a 5': 'nivel',
             'serious error': 'grave', 'critical': 'critica', 'crítica': 'critica', 'crítico': 'critica', 'critico': 'critica',
             'corrigi': 'corrigi', 'error grave': 'grave', 'erro grave': 'grave', 'minutes': 'minutos', 'tarefa': 'tarefa',
             'date': 'data', 'fecha': 'data', 'task': 'tarefa', 'tarea': 'tarefa', 'level': 'nivel', 'nível': 'nivel',
             'minutes': 'minutos', 'connection': 'conexao', 'conexão': 'conexao', 'conexion': 'conexao', 'conexión': 'conexao',
             'fixed': 'corrigi', 'corregí': 'corrigi', 'corregi': 'corrigi', 'serious': 'grave', 'error grave': 'grave', 'erro grave': 'grave'}


def sim(v):
    return str(v).strip().lower()[:1] in ('s', 'y')  # sim, sí, yes


def correcao(v):
    """Coluna corrigi?: n = não precisei · p = correção pequena · g = correção grande (ou não ajudou).
    Aceita sim/sí/yes/s/y como grande, e no/não/n como nenhuma."""
    t = str(v).strip().lower()
    if t[:1] == 'p' or t.startswith('small') or t.startswith('leve') or t.startswith('minor'):  # pequena, pequeña, small, leve, minor
        return 'p'
    if t[:1] in ('g', 'b', 's', 'y'):  # grande, big, sim/sí, yes
        return 'g'
    return 'n'


def ler_papel(arq):
    """CSV da ficha de papel: data,tarefa,nivel,minutos,conexao,corrigi (vírgula ou ponto e vírgula)."""
    if not arq.exists():
        return [], []
    bruto = arq.read_bytes()
    try:
        texto = bruto.decode('utf-8-sig')
    except UnicodeDecodeError:
        texto = bruto.decode('cp1252')
    sep = ';' if texto.split('\n', 1)[0].count(';') > texto.split('\n', 1)[0].count(',') else ','
    linhas, erros = [], []
    leitor = csv.DictReader(io.StringIO(texto), delimiter=sep)
    cols = {chave_coluna(c) for c in (leitor.fieldnames or [])}
    for falta in ('tarefa', 'nivel', 'minutos', 'corrigi', 'grave'):
        if falta not in cols:
            erros.append(f'coluna "{falta}" não encontrada (cabeçalho lido: {", ".join(leitor.fieldnames or [])})')
    vazias = collections.Counter()
    for i, r in enumerate(leitor, 2):
        if None in r or None in r.values():
            erros.append(f'linha {i}: número de colunas diferente do cabeçalho (vírgula dentro do nome de uma coluna? use só "Conexão usada", sem parênteses)')
            continue
        r = {chave_coluna(k): (v or '').strip() for k, v in r.items()}
        for k in ('corrigi', 'grave'):
            vazias[k] += not r.get(k)
        nv = r.get('nivel', '').upper().replace(' ', '')
        nv = nv if nv.startswith('AL') else 'AL' + nv
        try:
            minutos = float(r.get('minutos', '0').replace(',', '.') or 0)
        except ValueError:
            minutos = -1
        if nv not in NIVEIS:
            erros.append(f'linha {i}: nível "{r.get("nivel")}" (use 1 a 5 ou AL1 a AL5)')
        elif minutos <= 0:
            erros.append(f'linha {i}: minutos "{r.get("minutos")}" (número maior que zero)')
        elif not r.get('tarefa'):
            erros.append(f'linha {i}: tarefa vazia')
        else:
            linhas.append(dict(data=data_iso(r.get('data', '')), tarefa=r['tarefa'], nivel=nv, minutos=minutos, critica=(sim(r['critica']) if r.get('critica', '').strip() else None),
                               conexao=r.get('conexao', ''), corrigi=correcao(r.get('corrigi', '')) == 'g',
                               pequena=correcao(r.get('corrigi', '')) == 'p', grave=sim(r.get('grave', ''))))
    for k in ('corrigi', 'grave'):
        if linhas and vazias[k] >= len(linhas):
            erros.append(f'coluna "{k}" vazia em todas as linhas: sem ela o relatório não sabe se a IA acertou')
    return linhas, erros


# ---------------------------------------------------------------- relatório
FOLGA_DIAS = 3  # registros que começam até 3 dias depois do início pedido não geram aviso


def cobertura(sessoes, dias, agora):
    """por fonte (claude/codex): quando começam os registros, se cobrem MENOS dias do que foi pedido.
    O Claude Code apaga registros com mais de 30 dias (cleanupPeriodDays); quem começou há pouco também cai aqui."""
    out = {}
    for f in ('claude', 'codex'):
        ts = [s['inicio'] for s in sessoes if s.get('fonte') == f and s.get('inicio')]
        if not ts:
            continue
        n = int((agora - min(ts)) // 86400) + 1
        if n < dias - FOLGA_DIAS:
            out[f] = dict(desde=datetime.fromtimestamp(min(ts)).date().isoformat(), dias=n)
    return out


def montar(sessoes, papel, tarefas, dias, curta=None):
    regras = {n: c for n, c, _ in tarefas}
    sess = [s for s in sessoes if not any(b in s['primeiro'].lower() for b in BASTIDORES)]
    por_nivel = collections.Counter()
    agg = collections.defaultdict(lambda: {'min': 0.0, 'n': 0, 'niv': collections.Counter(), 'corrigi': 0, 'papel': 0})
    for s in sess:
        t = tarefa_de(s['primeiro'], tarefas)
        peso = s['minutos'] or 0.05
        por_nivel[s['nivel']] += peso
        agg[t]['min'] += peso; agg[t]['n'] += 1; agg[t]['niv'][s['nivel']] += peso
    for p in papel:
        por_nivel[p['nivel']] += p['minutos']
        g = agg[p['tarefa']]
        g['min'] += p['minutos']; g['n'] += 1; g['niv'][p['nivel']] += p['minutos']; g['papel'] += 1; g['corrigi'] += p['corrigi']
    total = sum(por_nivel.values()) or 1
    semanas = max(dias / 7, 1 / 7)
    lista = []
    for nome, g in sorted(agg.items(), key=lambda kv: -kv[1]['min']):
        nv = g['niv'].most_common(1)[0][0]
        linhas = sorted([p for p in papel if p['tarefa'] == nome], key=lambda l: l['data'])
        if linhas:
            nv = linhas[-1]['nivel']  # na ficha, o degrau atual é o da última vez anotada
        # crítica: pela lista de tarefas, pelas palavras (ex.: "Publicar post" cai em "Publicar e divulgar") ou marcada na ficha
        marcada = [l['critica'] for l in linhas if l.get('critica') is not None]
        if marcada:  # o que você marcou na ficha vale sobre as palavras
            critica = marcada[-1]
        else:
            critica = bool(regras.get(nome)) or bool(regras.get(tarefa_de(nome, tarefas)))
        teto = 'AL4' if critica else 'AL5'
        prox = None if nv >= teto else NIVEIS[NIVEIS.index(nv) + 1]
        lista.append(dict(tarefa=nome, horas_semana=round(g['min'] / 60 / semanas, 1), vezes=g['n'], nivel=nv,
                          critica=critica, proximo=prox, papel=g['papel'], corrigi=g['corrigi'],
                          decisao=decidir(prox, linhas, nv, critica),
                          mistura={k: round(v / sum(g['niv'].values()) * 100) for k, v in g['niv'].most_common()}))
    conex = registro_conexoes(sess, papel)
    return dict(gerado_em=datetime.now().astimezone().isoformat(timespec='seconds'), dias=dias, cobertura_curta=curta or {},
                escada={n: round(100 * por_nivel[n] / total, 1) for n in NIVEIS},
                parte_ia=round(100 * (por_nivel['AL4'] + por_nivel['AL5']) / total, 1),
                tem_papel=bool(papel),
                fontes=dict(claude=sum(s['fonte'] == 'claude' for s in sess), codex=sum(s['fonte'] == 'codex' for s in sess),
                            conversas=sum(not s['automatica'] for s in sess), sozinhas=sum(s['automatica'] for s in sess),
                            acoes=sum(s['acoes'] for s in sess), externos=sum(s['externo'] for s in sess), papel=len(papel)),
                tarefas=lista, conexoes=conex)


# critério para subir AO degrau indicado: (vezes anotadas no degrau atual, máximo de correções GRANDES nessas vezes).
# AL1 → AL2 não tem critério: é só começar a perguntar (o risco é baixo).
CRITERIO = {'AL3': (10, 1), 'AL4': (20, 2), 'AL5': (50, 2)}
DESCER_GRANDES = 3  # 3 correções grandes nas últimas 10 vezes = descer (1 erro grave = descer na hora)


def decidir(proximo, linhas, atual=None, critica=False):
    """Lê a ficha da tarefa (ordem de data) e diz: descer, subir, anotar ou manter. Descer vem primeiro,
    e nunca conflita com subir: subir aceita no máximo 2 correções grandes, descer pede 3 ou um erro grave."""
    linhas = sorted(linhas, key=lambda l: l['data'])
    if atual:  # só conta o que foi feito no degrau atual: depois de subir ou descer, a conta recomeça
        linhas = [l for l in linhas if l['nivel'] == atual]
    ult10 = linhas[-10:]
    pode_descer = atual != 'AL1'  # no AL1 não há para onde descer
    if critica and atual == 'AL5':
        return _d('descer', 'critica_al5')
    graves = [l for l in ult10 if l.get('grave')]
    if graves and pode_descer:
        return _d('descer', 'grave_em', data=graves[-1]['data'])
    grandes = sum(l['corrigi'] for l in ult10)
    if grandes >= DESCER_GRANDES and pode_descer:
        return _d('descer', 'grandes_ult', grandes=grandes, n=len(ult10))
    if not proximo:
        return _d('manter', 'teto')
    if proximo == 'AL2':
        return _d('subir', 'al2_sem_criterio')
    n, maxc = CRITERIO[proximo]
    if not linhas:
        return _d('anotar', 'anote_proximas', n=n)
    janela = linhas[-n:]
    erros = sum(l['corrigi'] for l in janela)
    if len(janela) < n:
        return _d('anotar', 'anotadas_falta', feitas=len(janela), n=n, falta=n - len(janela))
    if any(l.get('grave') for l in janela):
        return _d('manter', 'grave_janela', n=n)
    if erros <= maxc:
        return _d('subir', 'sobe', n=n, erros=erros, maxc=maxc)
    return _d('manter', 'mantem', n=n, erros=erros, maxc=maxc)


def registro_conexoes(sess, papel=()):
    c = {}
    for p in papel:  # a coluna "conexão" da ficha também é registrada (ChatGPT no navegador, planilha, e-mail...)
        for nome in re.split(r'\s*[+,;/]\s*', p['conexao']):
            if not nome.strip():
                continue
            dia = p['data'] or '?'
            r = c.setdefault('papel:' + nome.strip().lower()[:40], {'conexao': 'papel:' + nome.strip().lower()[:40], 'usos': 0, 'sessoes': 0,
                                                                  'primeira': dia, 'ultima': dia, 'sozinha': 0})
            r['usos'] += 1; r['sessoes'] += 1; r['sozinha'] += p['nivel'] == 'AL5'
            r['primeira'] = min(r['primeira'], dia); r['ultima'] = max(r['ultima'], dia)
    for s in sess:
        dia = datetime.fromtimestamp(s['inicio']).date().isoformat()
        for k, v in s['conexoes'].items():
            r = c.setdefault(k, {'conexao': k, 'usos': 0, 'sessoes': 0, 'primeira': dia, 'ultima': dia, 'sozinha': 0})
            r['usos'] += v; r['sessoes'] += 1; r['sozinha'] += s['automatica']
            r['primeira'] = min(r['primeira'], dia); r['ultima'] = max(r['ultima'], dia)
    return sorted(c.values(), key=lambda r: (-r['sessoes'], r['conexao']))


def markdown(r, anterior, lang='pt'):
    T = idioma(lang); R = T['rel']; N = T['nomes']; SUB = T['o_que_subir']
    tn = lambda t: T['tarefas'].get(t['tarefa'], t['tarefa'])  # tarefa do seu tarefas.json fica como você escreveu

    def mot(t):
        d = t['decisao']
        if 'chave' not in d:
            return d['motivo']
        q = dict(d.get('p', {}))
        if d['chave'] == 'grave_em' and not q.get('data'):
            q['data'] = T['motivos']['grave_alguma']
        return T['motivos'][d['chave']].format(**q)
    L = ['# ' + R['titulo'], '', R['ultimos'].format(data=r['gerado_em'][:10], dias=r['dias']), '']
    for f, c in r.get('cobertura_curta', {}).items():
        L += ['> ' + R['curta'].format(fonte=FONTE[f], desde=c['desde'], n=c['dias'], dias=r['dias']), '']
    L += ['## ' + R['conduz'].format(pct=r['parte_ia']), '']
    if anterior is not None:
        L += [R['anterior'].format(ant=anterior, dif=f"{r['parte_ia'] - anterior:+.1f}"), '']
    L += [R['tab_escada'], '--- | --- | ---']
    L += [f"{n} | {N[n]} | {r['escada'][n]}%" for n in NIVEIS]
    if not r['tem_papel']:
        L += ['', R['al1_zero']]
    L += ['', '## ' + R['suas_tarefas'], '', R['tab_tarefas'], '--- | --- | --- | --- | ---']
    for t in r['tarefas'][:12]:
        prox = R['voltar_al4'] if t['critica'] and t['nivel'] == 'AL5' else (t['proximo'] or R['no_teto'])
        L.append(f"{tn(t)}{R['critica_teto'] if t['critica'] else ''} | {t['horas_semana']} | {t['vezes']} | {t['nivel']} | {prox}")
    alerta = [t for t in r['tarefas'] if t['critica'] and t['mistura'].get('AL5', 0) >= 10]
    if alerta:
        L += ['', '## ' + R['atencao'], '']
        L += [R['atencao_linha'].format(tarefa=tn(t), pct=t['mistura']['AL5']) for t in alerta]
    desce = [t for t in r['tarefas'] if t['decisao']['acao'] == 'descer']
    sobe = [t for t in r['tarefas'] if t['decisao']['acao'] == 'subir']
    falta = [t for t in r['tarefas'] if t['decisao']['acao'] == 'anotar' and (t['papel'] or t['vezes'] >= 5)][:12]
    fica = [t for t in r['tarefas'] if t['papel'] and t['decisao']['acao'] == 'manter']
    if desce:
        L += ['', '## ' + R['descer'], '']
        L += [R['descer_linha'].format(tarefa=tn(t), de=t['nivel'], para=NIVEIS[max(NIVEIS.index(t['nivel']) - 1, 0)], motivo=mot(t)) for t in desce]
    if sobe:
        L += ['', '## ' + R['subir'], '']
        L += [f"- **{tn(t)}**: {t['nivel']} → {t['proximo']} ({mot(t)}). {SUB[t['proximo']]}" for t in sobe]
    if falta:
        L += ['', '## ' + R['candidatas'], '']
        L += [f"- **{tn(t)}**: {t['nivel']} → {t['proximo']}. {mot(t)[0].upper() + mot(t)[1:]}. {R['criterio']}: {SUB[t['proximo']]}" for t in falta if t['proximo']]
    if fica:
        L += ['', '## ' + R['continue'], '']
        L += [R['fica_linha'].format(tarefa=tn(t), nivel=t['nivel'], motivo=mot(t)) for t in fica]
    L += ['', R['quem_decide']]
    tipos = collections.Counter(c['conexao'].split(':', 1)[0] for c in r['conexoes'])
    L += ['', '## ' + R['conexoes'].format(n=len(r['conexoes'])), '',
          R['por_tipo'] + ': ' + ' · '.join(f'{k} {v}' for k, v in tipos.most_common()) + '.', '', R['tab_conexoes'],
          '--- | --- | --- | --- | --- | ---']
    L += [f"{c['conexao']} | {c['sessoes']} | {c['usos']} | {c['primeira']} | {c['ultima']} | {c['sozinha']}" for c in r['conexoes'][:40]]
    if len(r['conexoes']) > 40:
        L.append(R['e_mais'].format(n=len(r['conexoes']) - 40))
    L += ['', '## ' + R['de_onde'], '', R['fontes'].format(**r['fontes']), R['tempo_nota'], R['nivel_nota']]
    return '\n'.join(L) + '\n'


# ---------------------------------------------------------------- comandos
def cmd_varrer(a):
    corte = time.time() - a.dias * 86400
    itens = [('claude', c) for c in glob.glob(str(Path(a.claude).expanduser() / '*/*.jsonl')) if os.path.getmtime(c) >= corte]
    for raiz in a.codex or glob.glob(os.path.expanduser('~/.codex*/sessions')):
        itens += [('codex', c) for c in glob.glob(str(Path(raiz).expanduser() / '**/*.jsonl'), recursive=True) if os.path.getmtime(c) >= corte]
    with Pool(max(2, (os.cpu_count() or 4) // 2)) as pool:
        sessoes = [s for s in pool.imap_unordered(ler, itens, chunksize=16) if s and s['inicio'] >= corte]
    a.registro.mkdir(parents=True, exist_ok=True)
    tmp = a.registro / 'sessoes.json.tmp'
    tmp.write_text(json.dumps(dict(gerado_em=datetime.now(timezone.utc).isoformat(timespec='seconds'), dias=a.dias, sessoes=sessoes),
                              ensure_ascii=False), encoding='utf-8')
    tmp.replace(a.registro / 'sessoes.json')
    n = collections.Counter(s['fonte'] for s in sessoes)
    R = idioma(getattr(a, 'lang', 'pt'))['rel']
    for f, c in cobertura(sessoes, a.dias, time.time()).items():
        print('AVISO: ' + R['curta'].format(fonte=FONTE[f], desde=c['desde'], n=c['dias'], dias=a.dias), file=sys.stderr)
    print(f"{len(sessoes)} sessões ({n['claude']} Claude Code, {n['codex']} Codex) em {a.dias} dias → {a.registro / 'sessoes.json'}")


def carregar(a):
    arq = a.registro / 'sessoes.json'
    if arq.exists():
        d = json.loads(arq.read_text(encoding='utf-8'))
    elif (a.registro / 'papel.csv').exists():  # só a ficha (ChatGPT no navegador etc.): relatório sem logs
        d = {'sessoes': [], 'dias': 30}
    else:
        sys.exit('Ainda não há medição: rode  python3 medir/nivel.py varrer  ou crie registro/papel.csv a partir de kit/papel-modelo.csv')
    papel, erros = ler_papel(a.registro / 'papel.csv')
    for e in erros:
        print('Aviso na ficha de papel,', e, file=sys.stderr)
    try:
        agora = datetime.fromisoformat(d['gerado_em']).timestamp()
    except (KeyError, ValueError):
        agora = time.time()
    return montar(d['sessoes'], papel, carregar_tarefas(), d['dias'], cobertura(d['sessoes'], d['dias'], agora))


def cmd_relatorio(a):
    r = carregar(a)
    hist_arq = a.registro / 'historico.jsonl'
    hist = [json.loads(l) for l in hist_arq.read_text(encoding='utf-8').splitlines() if l.strip()] if hist_arq.exists() else []
    hoje = date.today().isoformat()
    anterior = next((h['parte_ia'] for h in reversed(hist) if h.get('data') != hoje), None)
    hist = [h for h in hist if h.get('data') != hoje] + [{'data': hoje, 'parte_ia': r['parte_ia'], 'escada': r['escada']}]
    hist_arq.write_text(''.join(json.dumps(h, ensure_ascii=False) + '\n' for h in hist[-400:]), encoding='utf-8')
    (a.registro / 'relatorio.json').write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
    md = markdown(r, anterior, a.lang)
    (a.registro / 'relatorio.md').write_text(md, encoding='utf-8')
    print(json.dumps(r, ensure_ascii=False, indent=1) if a.json else md)


def cmd_conexoes(a):
    r = carregar(a)
    print(f"{len(r['conexoes'])} conexões\n")
    for c in r['conexoes']:
        print(f"{c['conexao']:<45} {c['sessoes']:>6} sessões  {c['primeira']} → {c['ultima']}")


def cmd_papel(a):
    linhas, erros = ler_papel(a.registro / 'papel.csv')
    print(f"{len(linhas)} linhas válidas em {a.registro / 'papel.csv'}")
    for e in erros:
        print(' -', e)
    if not (a.registro / 'papel.csv').exists():
        print('Copie kit/papel-modelo.csv para registro/papel.csv e vá anotando.')
    return 1 if erros else 0


def main(argv=None):
    if hasattr(signal, 'SIGPIPE'):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--registro', type=Path, default=REGISTRO)
    sub = p.add_subparsers(dest='cmd', required=True)
    v = sub.add_parser('varrer')
    v.add_argument('--dias', type=int, default=30)
    v.add_argument('--claude', default='~/.claude/projects')
    v.add_argument('--codex', action='append', help='pasta de sessões do Codex (repita para mais de uma)')
    r = sub.add_parser('relatorio')
    r.add_argument('--json', action='store_true')
    r.add_argument('--lang', choices=IDIOMAS, default='pt', help='idioma do relatório (pt, en, es)')
    sub.add_parser('conexoes')
    sub.add_parser('papel')
    a = p.parse_args(argv)
    return {'varrer': cmd_varrer, 'relatorio': cmd_relatorio, 'conexoes': cmd_conexoes, 'papel': cmd_papel}[a.cmd](a) or 0


if __name__ == '__main__':
    sys.exit(main())
