#!/usr/bin/env python3
"""certificado.py: transforma a medição do nivel-ia num certificado em HTML (uma página A4 deitada),
para mostrar em que degrau da escada AL1–AL5 está o seu trabalho, como evoluiu e para onde vai.

Só biblioteca padrão. Não gera imagem: abre em qualquer navegador e vira PDF pelo "Imprimir".
Lê, na pasta do registro: relatorio.json (rode antes `nivel.py relatorio`), sessoes.json (curva semana a
semana) e historico.jsonl (medições anteriores, se houver).

Uso:
  python3 medir/certificado.py --nome "Seu Nome"
  # período maior (ex.: 90 dias), sem mexer no registro diário:
  python3 medir/nivel.py --registro /tmp/n90 varrer --dias 90
  python3 medir/nivel.py --registro /tmp/n90 relatorio
  python3 medir/certificado.py --nome "Seu Nome" --registro /tmp/n90
  # em inglês ou espanhol:
  python3 medir/certificado.py --nome "Your Name" --lang en
"""
import argparse, datetime as dt, html, json, math, os, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
REG = os.path.join(AQUI, '..', 'registro')
IDIOMAS = ('pt', 'en', 'es')
LANG = 'pt'
T = {}


def usar_idioma(lang):
    """carrega medir/idiomas_<lang>.json (o mesmo arquivo do relatório)"""
    global LANG, T
    LANG = lang if lang in IDIOMAS else 'pt'
    T = json.load(open(os.path.join(AQUI, f'idiomas_{LANG}.json'), encoding='utf-8'))


MIN_HORAS_SEMANA = 10      # semana com menos horas de trabalho com IA fica fora da curva (amostra pequena)
MES_DIAS = 30.44


def data_br(d, curta=False):
    if isinstance(d, str):
        d = dt.date.fromisoformat(d[:10])
    C = T['cert']
    if curta:
        return f'{d.month:02d}/{d.day:02d}' if LANG == 'en' else f'{d.day:02d}/{d.month:02d}'
    return C['data_longa'].format(dia=d.day, mes=C['meses'][d.month - 1], ano=d.year)


def num(x):
    return f'{x:,.0f}' if LANG == 'en' else f'{x:,.0f}'.replace(',', '.')


def pct(x):
    return f'{x:.1f}'.replace('.', T['cert']['decimal']) + '%'


def semanas(caminho):
    """% conduzido pela IA (AL4+AL5) por semana, com o mesmo peso do relatório (minutos, mínimo 0,05)."""
    if not os.path.exists(caminho):
        return []
    try:
        ss = json.load(open(caminho, encoding='utf-8'))['sessoes']
    except (ValueError, KeyError):
        return []
    soma = {}
    for s in ss:
        if not s.get('inicio'):
            continue
        d = dt.date.fromtimestamp(s['inicio'])
        seg = d - dt.timedelta(days=d.weekday())
        p = s.get('minutos') or 0.05
        a = soma.setdefault(seg, [0.0, 0.0])
        a[1] += p
        a[0] += p if s.get('nivel') in ('AL4', 'AL5') else 0
    pts = [(seg, 100 * ia / tot, tot / 60) for seg, (ia, tot) in sorted(soma.items()) if tot / 60 >= MIN_HORAS_SEMANA]
    if len(pts) >= 4:  # semanas do começo com bem menos uso (registro ainda incompleto) distorcem a evolução
        med = sorted(h for _, _, h in pts)[len(pts) // 2]
        while len(pts) > 3 and pts[0][2] < 0.25 * med:
            pts.pop(0)
    return pts


def historico(caminho):
    pontos = {}
    if os.path.exists(caminho):
        for linha in open(caminho, encoding='utf-8'):
            try:
                h = json.loads(linha)
                pontos[h['data']] = h['parte_ia']
            except (ValueError, KeyError):
                pass
    return [(dt.date.fromisoformat(d), v, None) for d, v in sorted(pontos.items())]


def inclinacao(pontos):
    """reta por mínimos quadrados em logit(%) × meses, ponderada pelas horas; devolve k por mês (ou None)"""
    usa = [(d, p, h or 1) for d, p, h in pontos if 0.5 < p < 99.5]
    if len(usa) < 4:
        return None
    o = usa[0][0]
    xs = [(d - o).days / MES_DIAS for d, _, _ in usa]
    ys = [math.log(p / (100 - p)) for _, p, _ in usa]
    ws = [h for _, _, h in usa]
    W = sum(ws)
    mx = sum(w * x for w, x in zip(ws, xs)) / W
    my = sum(w * y for w, y in zip(ws, ys)) / W
    vx = sum(w * (x - mx) ** 2 for w, x in zip(ws, xs))
    if vx == 0:
        return None
    return sum(w * (x - mx) * (y - my) for w, x, y in zip(ws, xs, ys)) / vx


def projecao(hoje_pct, k):
    if k is None or k <= 0 or not 0 < hoje_pct < 100:
        return []
    z0 = math.log(hoje_pct / (100 - hoje_pct))
    return [(m, 100 / (1 + math.exp(-(z0 + k * m)))) for m in (1, 3, 6)]


def grafico(pontos):
    w, h, m, base = 560, 150, 26, 18
    xs = [m + i * (w - 2 * m) / max(len(pontos) - 1, 1) for i in range(len(pontos))]
    ys = [h - base - v / 100 * (h - base - 12) for _, v, _ in pontos]
    linha = ' '.join(f'{x:.1f},{y:.1f}' for x, y in zip(xs, ys))
    area = f'{xs[0]:.1f},{h-base} ' + linha + f' {xs[-1]:.1f},{h-base}'
    grade = ''.join(f'<line x1="{m}" x2="{w-m}" y1="{h-base-g/100*(h-base-12):.1f}" y2="{h-base-g/100*(h-base-12):.1f}" class="g"/>'
                    f'<text x="{m-4}" y="{h-base-g/100*(h-base-12)+3:.1f}" class="rot" text-anchor="end">{g}%</text>' for g in (0, 50, 100))
    marcas = ''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3"/>' for x, y in zip(xs, ys))
    passo = max(1, len(pontos) // 6)
    datas = ''.join(f'<text x="{xs[i]:.1f}" y="{h-3}" class="rot" text-anchor="middle">{data_br(pontos[i][0], True)}</text>'
                    for i in range(0, len(pontos), passo))
    fim = f'<text x="{xs[-1]:.1f}" y="{ys[-1]-8:.1f}" class="vfim" text-anchor="end">{pct(pontos[-1][1])}</text>'
    return (f'<svg viewBox="0 0 {w} {h}" class="graf" role="img" aria-label="{T['cert']['graf_aria']}">'
            f'{grade}<polygon points="{area}" class="area"/><polyline points="{linha}" class="lin"/>{marcas}{datas}{fim}</svg>')


def montar(rel, curva, nome, origem_curva):
    C, NOMES, EXPLICA = T['cert'], T['nomes'], T['explica']
    tn = lambda t: T['tarefas'].get(t, t)
    e = rel['escada']
    hoje = rel['gerado_em'][:10]
    f = rel.get('fontes', {})
    barras = ''.join(
        f'<div class="deg"><div class="al">{k}</div><div class="nm">{NOMES[k]}</div>'
        f'<div class="trilho"><div class="enche{" ia" if k in ("AL4", "AL5") else ""}" style="width:{max(e.get(k, 0), 0.6):.1f}%"></div></div>'
        f'<div class="v">{pct(e.get(k, 0))}</div></div>' for k in NOMES)
    tarefas = sorted((t for t in rel.get('tarefas', []) if not t['tarefa'].lower().startswith('outra')),
                     key=lambda t: -t.get('horas_semana', 0))[:4]
    linhas_t = ''.join(
        f'<tr><td>{html.escape(tn(t["tarefa"]))}</td><td class="c">{t["nivel"]}</td>'
        f'<td class="c">{(t.get("proximo") or C["no_teto"])}</td></tr>' for t in tarefas)
    escada = ''.join(f'<li><b>{k}</b> {EXPLICA[k]}</li>' for k in NOMES)
    # evolução
    if len(curva) >= 2:
        (d0, v0, _), (d1, v1, _) = curva[0], curva[-1]
        rotulo = C['rot_semana'] if origem_curva == 'semanas' else C['rot_medicao']
        evol = (f'<h2>{C["evol_semanas"] if origem_curva == "semanas" else C["evol_medicoes"]}</h2>{grafico(curva)}'
                '<p class="evol">' + C['evol_txt'].format(v0=pct(v0), v1=pct(v1), rot=rotulo, d0=data_br(d0, True), d1=data_br(d1, True)) + '</p>')
    else:
        evol = f'<p class="evol">{C["primeira"]}</p>'
    # projeção
    # ponto de partida = nível atual (média ponderada das 2 últimas semanas), não a média do período inteiro
    if origem_curva == 'semanas' and len(curva) >= 2:
        ult = curva[-2:]
        atual, rot_atual = sum(v * h for _, v, h in ult) / sum(h for _, _, h in ult), C['ultimas2']
    else:
        atual, rot_atual = rel['parte_ia'], C['hoje']
    proj = projecao(atual, inclinacao(curva))
    if proj:
        caixas = ''.join(f'<div class="pj"><div class="pv">{pct(v)}</div><div class="pl">{C["em_mes"] if m == 1 else C["em_meses"].format(m=m)}</div></div>' for m, v in proj)
        bloco_proj = (f'<h2>{C["projecao"]}</h2><div class="pjs"><div class="pj hoje"><div class="pv">{pct(atual)}</div><div class="pl">{rot_atual}</div></div>{caixas}</div>'
                      f'<p class="nota">{C["proj_nota"]}</p>')
    else:
        bloco_proj = f'<h2>{C["projecao"]}</h2><p class="nota">{C["sem_tendencia"]}</p>'
    inicio = dt.date.fromisoformat(hoje) - dt.timedelta(days=rel.get('dias', 30))
    periodo = C['periodo'].format(dias=rel.get('dias', 30), ini=data_br(inicio), fim=data_br(hoje))
    papel = C['papel'] if rel.get('tem_papel') else ''
    fontes_nome = {'claude': 'Claude Code', 'codex': 'Codex'}
    curta = ''.join(f'<p class="nota aviso">{C["curta"].format(fonte=fontes_nome.get(k, k), n=c["dias"], dias=rel.get("dias", 30), desde=data_br(c["desde"]))}</p>'
                    for k, c in rel.get('cobertura_curta', {}).items())
    medido = C['medido'].format(periodo=periodo, papel=papel, conversas=num(f.get('conversas', 0)),
                                sozinhas=num(f.get('sozinhas', 0)), acoes=num(f.get('acoes', 0)))
    return f'''<!doctype html>
<html lang="{C['html_lang']}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{C['titulo_pagina']} · {html.escape(nome)} · {data_br(hoje)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;600;800&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>
@page{{size:A4 landscape;margin:0}}
:root{{--tinta:#14141a;--mut:#5b5b66;--linha:#d9d3c2;--ouro:#FACC15;--ouro2:#a16207;--papel:#fbf8f1}}
*{{box-sizing:border-box}}
body{{margin:0;background:#e9e5da;font:14px/1.4 Inter,Arial,sans-serif;color:var(--tinta)}}
.folha{{width:297mm;height:210mm;margin:16px auto;background:var(--papel);padding:12mm 15mm 0;position:relative;box-shadow:0 10px 40px #0002;overflow:hidden}}
.folha:before{{content:"";position:absolute;inset:6mm;border:2px solid var(--ouro2);outline:1px solid var(--ouro2);outline-offset:3px;pointer-events:none}}
.topo{{display:flex;justify-content:space-between;font:600 11px Sora,sans-serif;letter-spacing:.14em;color:var(--mut);text-transform:uppercase}}
.topo b{{color:var(--tinta)}} .topo .ponto{{color:var(--ouro2)}}
h1{{font:800 30px/1.1 Sora,sans-serif;margin:10px 0 2px}}
.quem{{font:600 13px Sora,sans-serif;color:var(--mut);margin:0}}
.nome{{font:800 26px Sora,sans-serif;margin:0 0 4px;border-bottom:2px solid var(--ouro);display:inline-block;padding:0 4px 1px}}
.txt{{margin:4px 0 0;font-size:13.5px}}
.grade{{display:grid;grid-template-columns:1.2fr 1fr;gap:11mm;margin-top:6mm}}
.big{{display:flex;align-items:baseline;gap:10px;margin-bottom:4px}}
.big .n{{font:800 50px/1 Sora,sans-serif}} .big .l{{font:600 13px Sora,sans-serif;color:var(--mut);max-width:72mm}}
.deg{{display:grid;grid-template-columns:32px 150px 1fr 50px;align-items:center;gap:8px;margin:3px 0}}
.al{{font:800 12px Sora,sans-serif;background:var(--tinta);color:#fff;border-radius:6px;text-align:center;padding:2px 0}}
.nm{{font-size:12.5px;color:var(--mut)}} .v{{font:600 12.5px Sora,sans-serif;text-align:right}}
.trilho{{height:11px;background:#ece6d6;border-radius:6px;overflow:hidden}}
.enche{{height:100%;background:#9a958a}} .enche.ia{{background:var(--ouro)}}
h2{{font:600 11px Sora,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:var(--ouro2);margin:12px 0 4px}}
table{{width:100%;border-collapse:collapse;font-size:12.5px}} td{{border-bottom:1px solid var(--linha);padding:3px 4px}} td.c{{text-align:center;font:600 12.5px Sora,sans-serif}}
th{{font:600 10.5px Sora,sans-serif;color:var(--mut);text-align:left;padding:0 4px 2px}} th.c{{text-align:center}}
.evol{{font-size:12.5px;margin:2px 0 0}}
.graf{{width:100%;height:auto;display:block}} .graf .g{{stroke:var(--linha);stroke-width:1}}
.graf .lin{{fill:none;stroke:var(--ouro2);stroke-width:2.5}} .graf .area{{fill:#FACC1533}}
.graf circle{{fill:var(--ouro2)}} .graf .rot{{font:9.5px Inter,sans-serif;fill:var(--mut)}} .graf .vfim{{font:800 12px Sora,sans-serif;fill:var(--tinta)}}
.pjs{{display:grid;grid-template-columns:repeat(4,1fr);gap:6px}}
.pj{{border:1px solid var(--linha);border-radius:8px;padding:5px 6px;text-align:center;background:#fff8}}
.pj.hoje{{background:var(--tinta);color:#fff;border-color:var(--tinta)}} .pj.hoje .pl{{color:#ddd}}
.pv{{font:800 17px Sora,sans-serif}} .pl{{font-size:11px;color:var(--mut)}}
.nota{{font-size:11px;color:var(--mut);margin:4px 0 0}}
.aviso{{color:#9a3412;font-weight:600}}
ul.esc{{list-style:none;margin:0;padding:0;font-size:12px}} ul.esc li{{margin:2px 0}} ul.esc b{{display:inline-block;width:30px;font:800 11.5px Sora,sans-serif}}
.rodape{{position:absolute;left:15mm;right:15mm;bottom:10mm;display:flex;justify-content:space-between;gap:10mm;font-size:10.5px;color:var(--mut);border-top:1px solid var(--linha);padding-top:5px}}
.rodape b{{color:var(--tinta)}}
.botao{{display:block;width:max-content;margin:0 auto 20px;font:600 14px Sora,sans-serif;background:var(--tinta);color:#fff;border:0;border-radius:10px;padding:10px 18px;cursor:pointer}}
@media print{{body{{background:none}} .folha{{margin:0;box-shadow:none}} .botao{{display:none}}}}
@media (max-width:1150px){{.folha{{width:auto;height:auto;margin:8px;padding-bottom:8mm}} .grade{{grid-template-columns:1fr}} .rodape{{position:static;margin-top:8mm;flex-direction:column}}}}
</style></head><body>
<div class="folha">
  <div class="topo"><span><b>INEMA<span class="ponto">.</span>CLUB</b> · {C['topo_esq']}</span><span>{C['topo_dir']}</span></div>
  <h1>{C['h1']}</h1>
  <p class="quem">{C['quem']}</p>
  <div class="nome">{html.escape(nome)}</div>
  <p class="txt">{medido}</p>{curta}
  <div class="grade">
    <div>
      <div class="big"><span class="n">{pct(rel["parte_ia"])}</span><span class="l">{C['big']}</span></div>
      {barras}
      {evol}
    </div>
    <div>
      <h2 style="margin-top:0">{C['tarefas']}</h2>
      <table><tr><th>{C['th_tarefa']}</th><th class="c">{C['th_degrau']}</th><th class="c">{C['th_proximo']}</th></tr>{linhas_t}</table>
      {bloco_proj}
      <h2>{C['escada']}</h2>
      <ul class="esc">{escada}</ul>
    </div>
  </div>
  <div class="rodape">
    <span>{C['rodape']}</span>
    <span>{C['emitido'].format(data=data_br(hoje))} · <b>inema.club</b></span>
  </div>
</div>
<button class="botao" onclick="window.print()">{C['botao']}</button>
</body></html>
'''


def main():
    ap = argparse.ArgumentParser(description='Certificado de nível de IA (HTML) a partir da medição do nivel-ia')
    ap.add_argument('--nome', required=True, help='nome que aparece no certificado')
    ap.add_argument('--registro', default=REG, help='pasta do registro (a mesma do --registro do nivel.py)')
    ap.add_argument('--saida')
    ap.add_argument('--lang', choices=IDIOMAS, default='pt', help='idioma do certificado (pt, en, es)')
    a = ap.parse_args()
    usar_idioma(a.lang)
    arq = os.path.join(a.registro, 'relatorio.json')
    if not os.path.exists(arq):
        sys.exit(T['cert']['falta_rel'])
    rel = json.load(open(arq, encoding='utf-8'))
    curva, origem = semanas(os.path.join(a.registro, 'sessoes.json')), 'semanas'
    if len(curva) < 2:
        curva, origem = historico(os.path.join(a.registro, 'historico.jsonl')), 'medicoes'
    hoje = rel['gerado_em'][:10]
    saida = a.saida or os.path.join(a.registro, f'certificado-{hoje}{'' if LANG == 'pt' else '-' + LANG}.html')
    open(saida, 'w', encoding='utf-8').write(montar(rel, curva, a.nome, origem))
    print(T['cert']['saida'].format(arq=os.path.abspath(saida)))


if __name__ == '__main__':
    main()
