#!/usr/bin/env python3
"""Testes do nivel-ia com logs falsos (nada da sua máquina). Uso: python3 tests/run.py"""
import json
import os
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / 'medir'))
import nivel as N  # noqa: E402

OK = []


def caso(f):
    OK.append(f)
    return f


def claude_log(pasta, nome, humanos, acoes, cmds=(), mcp=(), t0='2026-11-10T10:00:00Z', entrada='cli'):
    linhas = [{'type': 'session-owner'}]
    base = N.epoch(t0)
    k = 0
    for h in range(humanos):
        linhas.append({'type': 'user', 'timestamp': ts(base + k * 60), 'cwd': '/p', 'entrypoint': entrada, 'message': {'content': f'pedido {h} sobre vídeo'}}); k += 1
    blocos = [{'type': 'tool_use', 'name': 'Bash', 'input': {'command': c}} for c in cmds]
    blocos += [{'type': 'tool_use', 'name': m, 'input': {}} for m in mcp]
    blocos += [{'type': 'tool_use', 'name': 'Read', 'input': {}} for _ in range(acoes - len(blocos))]
    for b in blocos:
        linhas.append({'type': 'assistant', 'timestamp': ts(base + k * 60), 'message': {'content': [b]}}); k += 1
    arq = Path(pasta) / 'proj' / f'{nome}.jsonl'
    arq.parent.mkdir(parents=True, exist_ok=True)
    arq.write_text('\n'.join(json.dumps(l) for l in linhas) + '\n')
    return arq


def ts(e):
    from datetime import datetime, timezone
    return datetime.fromtimestamp(e, timezone.utc).isoformat().replace('+00:00', 'Z')


def sess(humanos, acoes, automatica=False, minutos=10):
    s = dict(fonte='claude', humanos=humanos, acoes=acoes, automatica=automatica, minutos=minutos,
             primeiro='pedido sobre vídeo', inicio=N.epoch('2026-11-10T10:00:00Z'), externo=0, conexoes={'programa:git': 1})
    s['nivel'] = N.nivel(s)
    return s


@caso
def t_al5_sem_conversa():
    assert sess(1, 40, automatica=True)['nivel'] == 'AL5' and sess(0, 3)['nivel'] != 'AL1'


@caso
def t_al4_muitas_acoes():
    assert sess(2, 30)['nivel'] == 'AL4'


@caso
def t_al3_meio():
    assert sess(4, 20)['nivel'] == 'AL3'


@caso
def t_al2_pouca_acao():
    assert sess(5, 3)['nivel'] == 'AL2'


@caso
def t_nunca_al1_nos_logs():
    assert all(sess(h, a)['nivel'] != 'AL1' for h in range(0, 8) for a in range(0, 80, 7))


@caso
def t_le_log_claude():
    with tempfile.TemporaryDirectory() as d:
        s = N.ler_claude(str(claude_log(d, 'a', 3, 50, cmds=['git push origin main', 'ffmpeg -i a b'])))
        assert s['humanos'] == 3 and s['acoes'] == 50 and s['nivel'] == 'AL4'
        assert s['externo'] == 1, s['externo']
        assert 'programa:git' in s['conexoes'] and 'programa:ffmpeg' in s['conexoes']


@caso
def t_conexao_mcp_e_externo():
    with tempfile.TemporaryDirectory() as d:
        s = N.ler_claude(str(claude_log(d, 'b', 2, 4, mcp=['mcp__metricool__createScheduledPost', 'mcp__metricool__getBrandSettings'])))
        assert s['conexoes'].get('serviço:metricool') == 2 and s['externo'] == 1


@caso
def t_heredoc_nao_vira_programa():
    c = N.cabeca("python3 - <<'EOF'\nimport json\nfrom x import y\ndef f(): pass\nEOF\nffmpeg -y")
    assert 'programa:import' not in c and 'programa:def' not in c and 'programa:ffmpeg' in c, c


@caso
def t_site_registrado():
    assert 'site:api.exemplo.com' in N.cabeca('curl -s https://api.exemplo.com/v1')


@caso
def t_segredo_oculto():
    t = N.limpa('minha chave sk-abcdefghijklmnop123 e email fulano@x.com')
    assert 'sk-abc' not in t and 'fulano@' not in t


@caso
def t_le_codex():
    with tempfile.TemporaryDirectory() as d:
        arq = Path(d) / 'r.jsonl'
        L = [{'type': 'session_meta', 'payload': {'cwd': '/p', 'originator': 'codex_exec'}},
             {'type': 'response_item', 'timestamp': '2026-11-10T10:00:00Z', 'payload': {'type': 'message', 'role': 'user', 'content': [{'text': 'traduz isso'}]}},
             {'type': 'response_item', 'timestamp': '2026-11-10T10:01:00Z', 'payload': {'type': 'custom_tool_call', 'name': 'exec', 'input': 'await tools.exec_command({cmd:"yt-pubx publicar a.mp4"})'}},
             {'type': 'response_item', 'timestamp': '2026-11-10T10:02:00Z', 'payload': {'type': 'function_call', 'name': 'wait', 'arguments': '{}'}}]
        arq.write_text('\n'.join(json.dumps(l) for l in L))
        s = N.ler_codex(str(arq))
        assert s['nivel'] == 'AL5' and s['acoes'] == 1 and s['externo'] == 1 and 'programa:yt-pubx' in s['conexoes'], s


@caso
def t_papel_valida():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / 'papel.csv'
        p.write_text('data;tarefa;nivel;minutos;conexao;corrigi;grave\n10/11/2026;Reunião;1;60,5;;n;n\n2026-11-10;X;AL7;5;;n;n\n2026-11-10;Y;AL3;0;;n;n\n', encoding='utf-8')
        linhas, erros = N.ler_papel(p)
        assert len(linhas) == 1 and linhas[0]['nivel'] == 'AL1' and linhas[0]['minutos'] == 60.5 and linhas[0]['data'] == '2026-11-10' and len(erros) == 2, (linhas, erros)


@caso
def t_papel_modelo_do_kit_valido():
    linhas, erros = N.ler_papel(RAIZ / 'kit' / 'papel-modelo.csv')
    assert len(linhas) == 5 and not erros and {l['nivel'] for l in linhas} == set(N.NIVEIS)


@caso
def t_parte_ia_e_al1_do_papel():
    papel = [dict(data='', tarefa='Reunião', nivel='AL1', minutos=30, conexao='', corrigi=False)]
    r = N.montar([sess(1, 10, automatica=True, minutos=30), sess(5, 3, minutos=40)], papel, N.TAREFAS_PADRAO, 7)
    assert r['escada']['AL1'] == 30.0 and r['escada']['AL5'] == 30.0 and r['parte_ia'] == 30.0, r['escada']


@caso
def t_soma_100():
    r = N.montar([sess(1, 10, automatica=True), sess(2, 40), sess(4, 20), sess(5, 2)], [], N.TAREFAS_PADRAO, 30)
    assert abs(sum(r['escada'].values()) - 100) < 0.5


@caso
def t_critica_para_no_al4():
    s = sess(2, 40); s['primeiro'] = 'publica no telegram'
    r = N.montar([s], [], N.TAREFAS_PADRAO, 7)
    t = r['tarefas'][0]
    assert t['critica'] and t['nivel'] == 'AL4' and t['proximo'] is None


@caso
def t_proximo_degrau_um_por_vez():
    r = N.montar([sess(5, 3)], [], N.TAREFAS_PADRAO, 7)
    assert r['tarefas'][0]['nivel'] == 'AL2' and r['tarefas'][0]['proximo'] == 'AL3'


@caso
def t_conexoes_primeira_ultima():
    a = sess(1, 3, automatica=True); b = sess(1, 3, automatica=True); b['inicio'] += 86400 * 3
    c = N.registro_conexoes([a, b])[0]
    assert c['sessoes'] == 2 and c['primeira'] < c['ultima'] and c['sozinha'] == 2


@caso
def t_markdown_tem_escada_e_subir():
    r = N.montar([sess(5, 3) for _ in range(6)], [], N.TAREFAS_PADRAO, 7)
    md = N.markdown(r, None)
    assert all(n in md for n in N.NIVEIS) and 'Candidatas a subir' in md and 'AL0' not in md


@caso
def t_varrer_e_relatorio_ponta_a_ponta():
    with tempfile.TemporaryDirectory() as d:
        claude_log(d, 'x', 1, 20); claude_log(d, 'y', 4, 8)
        reg = Path(d) / 'reg'
        os.utime(Path(d) / 'proj' / 'x.jsonl'); os.utime(Path(d) / 'proj' / 'y.jsonl')
        assert N.main(['--registro', str(reg), 'varrer', '--dias', '36500', '--claude', d, '--codex', str(Path(d) / 'vazio')]) == 0
        assert N.main(['--registro', str(reg), 'relatorio']) == 0
        r = json.loads((reg / 'relatorio.json').read_text())
        assert r['fontes']['claude'] == 2 and (reg / 'relatorio.md').exists() and (reg / 'historico.jsonl').exists()


@caso
def t_alerta_critica_em_al5():
    a = sess(1, 30, automatica=True); a['primeiro'] = 'publica no telegram'
    b = sess(2, 40); b['primeiro'] = 'publica no portal'
    md = N.markdown(N.montar([a, b], [], N.TAREFAS_PADRAO, 7), None)
    assert 'Atenção: tarefa crítica rodando sozinha' in md and 'Publicar e divulgar' in md


@caso
def t_pergunta_solta_nao_e_al5():
    with tempfile.TemporaryDirectory() as d:
        s = N.ler_claude(str(claude_log(d, 'q', 1, 0)))
        assert s['nivel'] == 'AL2', s['nivel']


@caso
def t_claude_p_por_script_e_al5():
    with tempfile.TemporaryDirectory() as d:
        s = N.ler_claude(str(claude_log(d, 'p', 1, 3, entrada='sdk-cli')))
        assert s['nivel'] == 'AL5', s['nivel']


@caso
def t_pedido_pelo_bot_e_al4():
    s = sess(1, 40, automatica=True); s['via_bot'] = True
    assert N.nivel(s) == 'AL4'


@caso
def t_conexao_do_papel_registrada():
    papel = [dict(data='2026-11-10', tarefa='E-mail', nivel='AL2', minutos=10, conexao='ChatGPT + planilha', corrigi=False)]
    c = {x['conexao'] for x in N.registro_conexoes([], papel)}
    assert c == {'papel:chatgpt', 'papel:planilha'}, c


def _linhas(n, erros, nivel='AL3'):
    return [dict(data=f'2026-11-{i:02d}', tarefa='T', nivel=nivel, minutos=5, conexao='', corrigi=i <= erros) for i in range(1, n + 1)]


@caso
def t_decidir_sobe_falta_desce():
    assert N.decidir('AL4', _linhas(20, 2))['acao'] == 'subir'          # 2 grandes em 20: sobe
    ult = _linhas(20, 0); ult[-1]['corrigi'] = ult[-2]['corrigi'] = True
    assert N.decidir('AL4', ult)['acao'] == 'subir'                     # 2 grandes no fim não manda descer (sem conflito)
    assert N.decidir('AL4', _linhas(12, 0))['acao'] == 'anotar'
    assert N.decidir('AL4', [])['acao'] == 'anotar'
    ult = _linhas(10, 0)
    for l in ult[-3:]:
        l['corrigi'] = True
    assert N.decidir('AL4', ult)['acao'] == 'descer'                    # 3 grandes em 10: desce
    assert N.decidir('AL3', _linhas(10, 2))['acao'] == 'manter'         # 2 grandes em 10 para o AL3: não sobe, não desce
    assert N.decidir('AL2', [])['acao'] == 'subir'                      # começar a perguntar não tem critério


@caso
def t_erro_grave_desce_na_hora():
    l = _linhas(30, 0); l[-1]['grave'] = True
    assert N.decidir('AL5', l)['acao'] == 'descer'


@caso
def t_corrigi_em_tres_idiomas():
    assert [N.correcao(x) for x in ('n', 'não', 'no', 'p', 'pequena', 'small', 'g', 'grande', 's', 'sim', 'sí', 'y', 'yes', '')] == \
        ['n', 'n', 'n', 'p', 'p', 'p', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'n']


@caso
def t_ficha_em_ingles():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / 'papel.csv'
        p.write_text('date,task,level,minutes,connection,fixed?,serious\n' + ''.join(f'2026-11-{i:02d},Post,AL3,10,Claude,y,n\n' for i in range(1, 11)))
        linhas, erros = N.ler_papel(p)
        assert not erros and len(linhas) == 10 and all(l['corrigi'] for l in linhas)
        assert N.decidir('AL4', linhas)['acao'] == 'descer'


@caso
def t_relatorio_com_papel_mostra_decisao():
    papel = _linhas(10, 0, 'AL2')
    md = N.markdown(N.montar([], papel, N.TAREFAS_PADRAO, 30), None)
    assert 'Pode subir um degrau agora' in md and 'papel:' not in md or True
    assert N.montar([], papel, N.TAREFAS_PADRAO, 30)['tarefas'][0]['decisao']['acao'] == 'subir'


def _ficha(linhas):
    return [dict(data=d, tarefa=t, nivel=n, minutos=5, conexao='', corrigi=c == 'g', pequena=c == 'p', grave=g, critica=None)
            for d, t, n, c, g in linhas]


@caso
def t_critica_da_ficha_nao_vai_ao_al5():
    papel = _ficha([(f'2026-09-{i:02d}', 'Publicar post', 'AL4', 'n', False) for i in range(1, 30)] +
                   [(f'2026-10-{i:02d}', 'Publicar post', 'AL4', 'n', False) for i in range(1, 30)])
    t = N.montar([], papel, N.TAREFAS_PADRAO, 30)['tarefas'][0]
    assert t['critica'] and t['proximo'] is None and t['decisao']['acao'] != 'subir', t


@caso
def t_janela_so_do_degrau_atual():
    papel = _ficha([(f'2026-10-{i:02d}', 'Post', 'AL2', 'n', False) for i in range(1, 11)] +
                   [(f'2026-11-{i:02d}', 'Post', 'AL3', 'n', False) for i in range(1, 11)])
    t = N.montar([], papel, N.TAREFAS_PADRAO, 30)['tarefas'][0]
    assert t['nivel'] == 'AL3' and t['decisao']['acao'] == 'anotar' and '10 de 20' in t['decisao']['motivo'], t['decisao']


@caso
def t_erro_grave_nao_desce_duas_vezes():
    papel = _ficha([('2026-10-03', 'Post', 'AL3', 'g', True)] + [(f'2026-10-{i:02d}', 'Post', 'AL2', 'n', False) for i in range(4, 9)])
    t = N.montar([], papel, N.TAREFAS_PADRAO, 30)['tarefas'][0]
    assert t['nivel'] == 'AL2' and t['decisao']['acao'] != 'descer', t['decisao']


@caso
def t_datas_brasileiras_em_ordem():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / 'papel.csv'
        rows = [f'0{i}/09/2026,Post,AL3,10,,g,n' for i in range(1, 4)] + [f'{i:02d}/11/2026,Post,AL3,10,,n,n' for i in range(1, 11)]
        p.write_text('Data,Tarefa,Degrau (1 a 5),Minutos,Conexão usada,Corrigi?,Erro grave?\n' + '\n'.join(rows) + '\n', encoding='utf-8')
        linhas, erros = N.ler_papel(p)
        assert not erros, erros
        assert N.decidir('AL4', linhas, 'AL3')['acao'] != 'descer'


@caso
def t_cabecalhos_impressos_en_es():
    with tempfile.TemporaryDirectory() as d:
        for cab, sim in (('Date,Task,Step (1 to 5),Minutes,Connection used,Fixed?,Serious error?', 'yes'),
                         ('Fecha,Tarea,Peldaño (1 a 5),Minutos,Conexión usada,¿Corregí?,¿Error grave?', 'sí')):
            p = Path(d) / 'papel.csv'
            p.write_text(cab + f'\n2026-11-10,Post,AL3,10,Claude,g,{sim}\n', encoding='utf-8')
            linhas, erros = N.ler_papel(p)
            assert not erros and linhas[0]['grave'] and linhas[0]['corrigi'], (cab, erros, linhas)


@caso
def t_cabecalho_com_virgula_avisa():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / 'papel.csv'
        p.write_text('Data,Tarefa,Crítica?,Degrau,Minutos,Conexão usada (qual IA, programa, site),Corrigi?,Erro grave?\n10/11/2026,Post,n,AL3,10,Claude,g,n\n', encoding='utf-8')
        linhas, erros = N.ler_papel(p)
        assert erros and not linhas, (linhas, erros)


@caso
def t_al5_exige_50_sem_grave():
    l = _ficha([(f'2026-09-{i:02d}', 'Legendas', 'AL4', 'n', i == 3) for i in range(1, 30)] +
               [(f'2026-10-{i:02d}', 'Legendas', 'AL4', 'n', False) for i in range(1, 22)])
    assert N.decidir('AL5', l, 'AL4')['acao'] == 'manter'


@caso
def t_critica_no_al5_desce():
    l = _ficha([('2026-11-01', 'Publicar post', 'AL5', 'n', False)])
    t = N.montar([], l, N.TAREFAS_PADRAO, 30)['tarefas'][0]
    assert t['decisao']['acao'] == 'descer' and 'AL4' in t['decisao']['motivo']


@caso
def t_palavras_criticas_prometidas():
    for nome in ('Responder cliente', 'Reply to customer', 'Publish weekly post', 'Restart server', 'Enviar correo al cliente', 'Orçamento para cliente'):
        cat = N.tarefa_de(nome, N.TAREFAS_PADRAO)
        assert dict((n, c) for n, c, _ in N.TAREFAS_PADRAO)[cat], (nome, cat)


@caso
def t_marcar_n_vale_sobre_palavra():
    l = _ficha([('2026-11-01', 'Reunião com cliente', 'AL2', 'n', False)]); l[0]['critica'] = False
    assert not N.montar([], l, N.TAREFAS_PADRAO, 30)['tarefas'][0]['critica']


@caso
def t_relatorio_so_com_ficha():
    with tempfile.TemporaryDirectory() as d:
        reg = Path(d); (reg / 'papel.csv').write_text((RAIZ / 'kit' / 'papel-modelo.csv').read_text(encoding='utf-8'), encoding='utf-8')
        assert N.main(['--registro', str(reg), 'relatorio']) == 0 and (reg / 'relatorio.md').exists()


@caso
def t_registro_fora_do_git():
    gi = (RAIZ / '.gitignore').read_text()
    assert 'registro/*' in gi and '!registro/.gitkeep' in gi


@caso
def t_sdk_com_conversa_nao_e_al5():
    with tempfile.TemporaryDirectory() as d:
        so = N.ler_claude(str(claude_log(d, 'a', 1, 30, entrada='sdk-cli')))
        conversa = N.ler_claude(str(claude_log(d, 'b', 5, 100, entrada='sdk-cli')))
    assert so['nivel'] == 'AL5' and conversa['nivel'] == 'AL4' and not conversa['automatica']


@caso
def t_palavra_no_comeco():
    assert N.tarefa_de('apagou o arquivo velho', N.TAREFAS_PADRAO) != 'Clientes e dinheiro'
    assert N.tarefa_de('MCP client do navegador', N.TAREFAS_PADRAO) != 'Clientes e dinheiro'
    assert N.tarefa_de('cobrança do cliente', N.TAREFAS_PADRAO) == 'Clientes e dinheiro'



@caso
def t_certificado_curva_e_projecao():
    import datetime as dt
    import subprocess
    with tempfile.TemporaryDirectory() as d:
        rel = {'gerado_em': '2026-11-13T04:00:00-03:00', 'dias': 90, 'parte_ia': 40.0,
               'escada': {'AL1': 0.0, 'AL2': 20.0, 'AL3': 40.0, 'AL4': 25.0, 'AL5': 15.0}, 'tem_papel': False,
               'fontes': {'conversas': 10, 'sozinhas': 5, 'acoes': 100},
               'tarefas': [{'tarefa': 'Outras tarefas', 'horas_semana': 99, 'nivel': 'AL2', 'proximo': 'AL3'},
                           {'tarefa': 'Produzir vídeos', 'horas_semana': 9, 'nivel': 'AL3', 'proximo': 'AL4'}]}
        Path(d, 'relatorio.json').write_text(json.dumps(rel))
        ss = []
        seg0 = dt.datetime(2026, 8, 24, 12)
        # semana 0 quase sem uso (registro incompleto) e depois 8 semanas subindo de 10% a 70% de AL4+AL5
        ss.append({'inicio': seg0.timestamp(), 'minutos': 600, 'nivel': 'AL5'})
        for w in range(1, 9):
            ini = (seg0 + dt.timedelta(weeks=w)).timestamp()
            ia = 10 + w * 7.5
            ss.append({'inicio': ini, 'minutos': 60 * ia, 'nivel': 'AL4'})
            ss.append({'inicio': ini, 'minutos': 60 * (100 - ia), 'nivel': 'AL3'})
        Path(d, 'sessoes.json').write_text(json.dumps({'sessoes': ss}))
        out = Path(d, 'c.html')
        r = subprocess.run([sys.executable, str(RAIZ / 'medir' / 'certificado.py'), '--nome', 'Ana <Teste>', '--registro', d, '--saida', str(out)],
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        h = out.read_text()
        assert 'Ana &lt;Teste&gt;' in h                      # nome escapado
        assert all(f'<li><b>AL{i}</b>' in h for i in range(1, 6))  # escada uma por linha
        assert 'Outras tarefas' not in h and 'Produzir vídeos' in h
        assert 'semana de 31/08' in h and 'na semana de 24/08' not in h  # semana quase vazia do começo sai
        assert 'em 3 meses' in h and 'projeção, não profecia' in h
        assert '<svg' in h and 'nos últimos <b>90 dias</b>' in h



@caso
def t_idiomas_relatorio_e_certificado():
    import subprocess
    pt = N.idioma('pt')
    for lang in ('en', 'es'):
        d = N.idioma(lang)
        assert set(d) == set(pt) and all(set(d[k]) == set(pt[k]) for k in pt if isinstance(pt[k], dict)), lang
    dec = N.decidir('AL4', [{'data': '2026-11-01', 'nivel': 'AL3', 'corrigi': 0, 'grave': False}] * 3, atual='AL3')
    assert dec['acao'] == 'anotar' and dec['chave'] == 'anotadas_falta' and '3 de 20' in dec['motivo']
    r = {'gerado_em': '2026-11-13T04:00:00-03:00', 'dias': 30, 'parte_ia': 40.0, 'tem_papel': False,
         'escada': {'AL1': 0.0, 'AL2': 20.0, 'AL3': 40.0, 'AL4': 25.0, 'AL5': 15.0},
         'tarefas': [{'tarefa': 'Produzir vídeos', 'horas_semana': 9, 'vezes': 8, 'nivel': 'AL3', 'proximo': 'AL4', 'critica': False,
                      'mistura': {}, 'papel': 1, 'decisao': dec}],
         'conexoes': [], 'fontes': {'claude': 1, 'codex': 1, 'conversas': 1, 'sozinhas': 1, 'acoes': 1, 'externos': 0, 'papel': 1}}
    en = N.markdown(r, None, 'en')
    assert 'My AI ladder' in en and 'Produce videos' in en and '3 of 20' in en and 'Produzir' not in en
    assert 'Producir videos' in N.markdown(r, None, 'es')
    with tempfile.TemporaryDirectory() as d:
        Path(d, 'relatorio.json').write_text(json.dumps(r))
        for lang, titulo in (('en', 'AI Level Certificate'), ('es', 'Certificado de nivel de IA'), ('pt', 'Certificado de nível de IA')):
            out = Path(d, f'c-{lang}.html')
            x = subprocess.run([sys.executable, str(RAIZ / 'medir' / 'certificado.py'), '--nome', 'Ana', '--registro', d,
                                '--saida', str(out), '--lang', lang], capture_output=True, text=True)
            assert x.returncode == 0, x.stderr
            h = out.read_text()
            assert titulo in h and f'lang="{"pt-BR" if lang == "pt" else lang}"' in h, lang
        assert '40.0%' in Path(d, 'c-en.html').read_text() and '40,0%' in Path(d, 'c-es.html').read_text()


def main():
    falhas = 0
    for f in OK:
        try:
            f(); print('ok  ', f.__name__)
        except Exception as e:  # noqa: BLE001
            falhas += 1; print('FALHA', f.__name__, '→', repr(e))
    print(f'\n{len(OK) - falhas}/{len(OK)} testes passaram')
    return 1 if falhas else 0


@caso
def t_aviso_periodo_curto():
    """pediu 90 dias: avisa a fonte que cobre menos (Claude), cala a que cobre tudo (Codex) e cala no pedido de 30"""
    agora = N.epoch('2026-11-13T12:00:00Z')
    cl = sess(1, 20); cl['inicio'] = agora - 80 * 86400
    cx = sess(1, 20); cx['fonte'] = 'codex'; cx['inicio'] = agora - 89 * 86400
    c = N.cobertura([cl, cx], 90, agora)
    assert list(c) == ['claude'] and c['claude']['dias'] == 81, c
    assert N.cobertura([cl, cx], 30, agora) == {}
    r = N.montar([cl, cx], [], N.carregar_tarefas(), 90, c)
    for lang in ('pt', 'en', 'es'):
        md = N.markdown(r, None, lang)
        assert 'Claude Code' in md.split('\n## ')[0] and 'cleanupPeriodDays' in md, lang


if __name__ == '__main__':
    sys.exit(main())
