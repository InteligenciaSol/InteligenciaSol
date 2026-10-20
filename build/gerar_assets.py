"""Gera os SVGs animados do perfil (banner, pilares, fluxo) com a identidade Sol Vinil.

Uso: python build/gerar_assets.py
Entrada: Manual de Marca em ../Orbita/identidade-visual (logo PNG e fontes Poppins).
Saida: assets/*.svg (autocontidos: fonte e logo embutidos, sem dependencia externa).
"""
import base64
import io
import math
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
MARCA = RAIZ.parent / "Orbita" / "identidade-visual" / "Manual de Marca Sol Vinil"
SAIDA = RAIZ / "assets"

AMARELO, LARANJA, VERMELHO = "#FBCF39", "#EC933B", "#AE4132"
TEXTO, FUNDO = "#231E21", "#F8F6F6"

CARACTERES = "".join(chr(c) for c in range(0x20, 0x7F)) + "".join(chr(c) for c in range(0xC0, 0x100)) + "·•→"


def fonte_b64(arquivo):
    f = TTFont(MARCA / "Fontes" / arquivo)
    opts = subset.Options()
    opts.flavor = "woff"
    opts.layout_features = ["kern", "liga"]
    sub = subset.Subsetter(opts)
    sub.populate(text=CARACTERES)
    sub.subset(f)
    f.flavor = "woff"
    buf = io.BytesIO()
    f.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


def logo_b64(largura):
    p = MARCA / "Arquivos Png" / "Logo Sol Vinil" / "Logo-Sol-Vinil-Principal.png"
    im = Image.open(p).convert("RGBA")
    im = im.crop(im.getchannel("A").getbbox())
    alt = round(im.height * largura / im.width)
    im = im.resize((largura, alt), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode(), alt


def estilo_base():
    reg, semi = fonte_b64("Poppins-Regular.ttf"), fonte_b64("Poppins-SemiBold.ttf")
    return f"""
  @font-face {{ font-family: PoppinsSV; font-weight: 400; src: url(data:font/woff;base64,{reg}) format('woff'); }}
  @font-face {{ font-family: PoppinsSV; font-weight: 600; src: url(data:font/woff;base64,{semi}) format('woff'); }}
  text {{ font-family: PoppinsSV, Poppins, 'Segoe UI', Arial, sans-serif; fill: {TEXTO}; }}
  .semi {{ font-weight: 600; }}
  .box {{ transform-box: fill-box; transform-origin: center; }}
  .left {{ transform-box: fill-box; transform-origin: left center; }}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; opacity: 1 !important; transform: none !important; }} }}
"""


def onda(base, amp, periodo, fase, largura=2560, passo=16):
    pts = []
    for x in range(0, largura + passo, passo):
        y = base + amp * math.sin(2 * math.pi * x / periodo + fase)
        pts.append(f"{x},{y:.1f}")
    return "M" + " L".join(pts)


def banner():
    logo, alt_logo = logo_b64(640)
    ondas = ""
    for i, (base, amp, fase, cor, op, dur) in enumerate([
        (322, 16, 0.0, AMARELO, 0.55, 16),
        (342, 14, 1.7, LARANJA, 0.50, 12),
        (362, 12, 3.4, VERMELHO, 0.42, 9),
    ]):
        d = onda(base, amp, 640, fase) + " L2576,400 L0,400 Z"
        ondas += f'<path d="{d}" fill="{cor}" opacity="{op}" style="animation: drift {dur}s linear infinite;"/>\n'
    raios = ""
    for ang in range(0, 360, 30):
        raios += (f'<g transform="rotate({ang})"><rect x="-4" y="-98" width="8" height="20" rx="4" fill="url(#grad)" '
                  f'style="animation: pulso 3.6s ease-in-out {ang / 360 * 3.6:.2f}s infinite;"/></g>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 400" width="1280" height="400" role="img" aria-labelledby="t d">
<title id="t">Setor de Inteligência, Sol Vinil Distribuidora</title>
<desc id="d">Banner com o logo da Sol Vinil, o título Setor de Inteligência e ondas nas cores da marca.</desc>
<defs>
  <linearGradient id="grad" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="{AMARELO}"/><stop offset=".55" stop-color="{LARANJA}"/><stop offset="1" stop-color="{VERMELHO}"/></linearGradient>
  <clipPath id="recorte"><rect width="1280" height="400"/></clipPath>
</defs>
<style>{estilo_base()}
  @keyframes drift {{ to {{ transform: translateX(-640px); }} }}
  @keyframes sobe {{ from {{ opacity: 0; transform: translateY(18px); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes cresce {{ from {{ transform: scaleX(0); }} to {{ transform: scaleX(1); }} }}
  @keyframes gira {{ to {{ transform: rotate(360deg); }} }}
  @keyframes pulso {{ 0%,100% {{ opacity: .35; }} 50% {{ opacity: 1; }} }}
  .entra {{ opacity: 0; animation: sobe .9s cubic-bezier(.2,.7,.2,1) forwards; }}
</style>
<rect width="1280" height="400" fill="{FUNDO}"/>
<g clip-path="url(#recorte)">
{ondas}</g>
<image class="entra" style="animation-delay:.1s" x="80" y="62" width="320" height="{round(alt_logo * 320 / 640)}" href="data:image/png;base64,{logo}"/>
<text class="entra semi" style="animation-delay:.45s" x="80" y="218" font-size="56">Setor de Inteligência</text>
<rect class="left" x="82" y="236" width="150" height="6" rx="3" fill="url(#grad)" style="animation: cresce 1.1s cubic-bezier(.2,.7,.2,1) .9s both;"/>
<text class="entra" style="animation-delay:.8s" x="80" y="282" font-size="22" opacity=".8">da Sol Vinil Distribuidora · dados que viram decisão</text>
<g transform="translate(1060 150)">
  <g class="box" style="animation: gira 60s linear infinite;">
    <circle r="132" fill="none" stroke="{LARANJA}" stroke-opacity=".45" stroke-width="2" stroke-dasharray="3 9"/>
    <circle cx="132" r="7" fill="{LARANJA}"/>
  </g>
  <g class="box" style="animation: gira 38s linear infinite reverse;">
    <circle r="100" fill="none" stroke="{AMARELO}" stroke-opacity=".6" stroke-width="2"/>
    <circle cx="-100" r="6" fill="{VERMELHO}"/>
  </g>
  {raios}
  <circle r="58" fill="none" stroke="url(#grad)" stroke-width="22"/>
</g>
</svg>
"""


def icone(i, cx, y):
    """Icones simples, animados, desenhados em torno de (cx, y)."""
    if i == 0:  # barras de demanda subindo
        s = ""
        for k, h in enumerate([22, 34, 28, 46]):
            s += (f'<rect class="left" x="{cx - 26 + k * 14}" y="{y + 46 - h}" width="9" height="{h}" rx="2.5" fill="{[AMARELO, LARANJA, LARANJA, VERMELHO][k]}" '
                  f'style="animation: barra 2.8s ease-in-out {k * .18:.2f}s infinite alternate; transform-origin: bottom;"/>')
        return s
    if i == 1:  # medidor de meta
        return (f'<circle cx="{cx}" cy="{y + 24}" r="22" fill="none" stroke="#EDE7E3" stroke-width="8"/>'
                f'<circle cx="{cx}" cy="{y + 24}" r="22" fill="none" stroke="url(#grad)" stroke-width="8" stroke-linecap="round" '
                f'stroke-dasharray="138" stroke-dashoffset="138" transform="rotate(-90 {cx} {y + 24})" style="animation: medidor 3.4s ease-in-out infinite;"/>'
                f'<circle cx="{cx}" cy="{y + 24}" r="4" fill="{TEXTO}"/>')
    if i == 2:  # fluxo automatico
        return (f'<path d="M{cx - 30} {y + 36} H{cx - 6} V{y + 12} H{cx + 30}" fill="none" stroke="#E4DCD7" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
                f'<circle cx="{cx - 30}" cy="{y + 36}" r="6" fill="{AMARELO}"/><circle cx="{cx + 30}" cy="{y + 12}" r="6" fill="{VERMELHO}"/>'
                f'<circle r="5" fill="{LARANJA}" style="offset-path: path(\'M{cx - 30} {y + 36} H{cx - 6} V{y + 12} H{cx + 30}\'); animation: viaja 2.6s ease-in-out infinite;"/>')
    # tendencia
    d = f"M{cx - 30} {y + 42} L{cx - 12} {y + 26} L{cx + 2} {y + 34} L{cx + 30} {y + 6}"
    return (f'<path d="{d}" fill="none" stroke="#EDE7E3" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="url(#grad)" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" pathLength="100" '
            f'stroke-dasharray="100" stroke-dashoffset="100" style="animation: traco 3.2s ease-in-out infinite;"/>')


def pilares():
    itens = [
        ("Demanda e estoque", "Previsão, cobertura e reposição", "para comprar na medida certa."),
        ("Painéis e metas", "Indicadores claros para vendedores,", "gestores e diretoria."),
        ("Automação de dados", "Rotinas que levam a informação", "certa até quem decide."),
        ("Análise comercial", "Mix, carteira e oportunidades", "lidos com método."),
    ]
    larg, gap = 290, 40
    cards = ""
    for i, (tit, l1, l2) in enumerate(itens):
        x = i * (larg + gap)
        cx = x + 62
        cards += f"""<g class="card" style="animation-delay:{i * .15:.2f}s">
  <rect x="{x}" y="0" width="{larg}" height="210" rx="22" fill="#fff" stroke="#EAE4E0"/>
  <rect x="{x + 28}" y="0" width="{larg - 56}" height="5" rx="2.5" fill="url(#grad)"/>
  {icone(i, cx, 34)}
  <text class="semi" x="{x + 28}" y="136" font-size="20">{tit}</text>
  <text x="{x + 28}" y="165" font-size="13.5" opacity=".78">{l1}</text>
  <text x="{x + 28}" y="185" font-size="13.5" opacity=".78">{l2}</text>
</g>
"""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="-40 -20 1360 250" width="1360" height="250" role="img" aria-labelledby="t">
<title id="t">Quatro frentes do setor: demanda e estoque, painéis e metas, automação de dados e análise comercial</title>
<defs><linearGradient id="grad" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="{AMARELO}"/><stop offset=".55" stop-color="{LARANJA}"/><stop offset="1" stop-color="{VERMELHO}"/></linearGradient></defs>
<style>{estilo_base()}
  @keyframes sobe {{ from {{ opacity: 0; transform: translateY(22px); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes barra {{ from {{ transform: scaleY(.45); }} to {{ transform: scaleY(1); }} }}
  @keyframes medidor {{ 0% {{ stroke-dashoffset: 138; }} 55%,80% {{ stroke-dashoffset: 34; }} 100% {{ stroke-dashoffset: 138; }} }}
  @keyframes traco {{ 0% {{ stroke-dashoffset: 100; }} 55%,85% {{ stroke-dashoffset: 0; }} 100% {{ stroke-dashoffset: 100; }} }}
  @keyframes viaja {{ 0% {{ offset-distance: 0%; }} 100% {{ offset-distance: 100%; }} }}
  .card {{ opacity: 0; animation: sobe .8s cubic-bezier(.2,.7,.2,1) forwards; }}
</style>
<rect x="-40" y="-20" width="1360" height="250" rx="28" fill="{FUNDO}"/>
{cards}</svg>
"""


def fluxo():
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 150" width="1280" height="150" role="img" aria-labelledby="t">
<title id="t">Do dado à decisão: dados, análise e decisão</title>
<defs><linearGradient id="grad" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="{AMARELO}"/><stop offset=".55" stop-color="{LARANJA}"/><stop offset="1" stop-color="{VERMELHO}"/></linearGradient></defs>
<style>{estilo_base()}
  @keyframes viaja {{ 0% {{ offset-distance: 0%; opacity: 0; }} 10%,90% {{ opacity: 1; }} 100% {{ offset-distance: 100%; opacity: 0; }} }}
  @keyframes flui {{ to {{ stroke-dashoffset: -28; }} }}
  @keyframes nasce {{ 0%,100% {{ transform: scale(1); }} 50% {{ transform: scale(1.08); }} }}
</style>
<rect width="1280" height="150" rx="28" fill="{FUNDO}"/>
<path id="trilho" d="M250 75 H1030" stroke="url(#grad)" stroke-width="4" stroke-linecap="round" stroke-dasharray="2 12" fill="none" style="animation: flui 1.6s linear infinite;"/>
<circle r="7" fill="{LARANJA}" style="offset-path: path('M250 75 H1030'); animation: viaja 4s ease-in-out infinite;"/>
<circle r="7" fill="{AMARELO}" style="offset-path: path('M250 75 H1030'); animation: viaja 4s ease-in-out 1.3s infinite;"/>
<circle r="7" fill="{VERMELHO}" style="offset-path: path('M250 75 H1030'); animation: viaja 4s ease-in-out 2.6s infinite;"/>
<g class="box" style="animation: nasce 4s ease-in-out infinite;"><circle cx="180" cy="75" r="46" fill="#fff" stroke="{AMARELO}" stroke-width="5"/><text class="semi" x="180" y="81" font-size="17" text-anchor="middle">Dados</text></g>
<g class="box" style="animation: nasce 4s ease-in-out 1.3s infinite;"><circle cx="640" cy="75" r="46" fill="#fff" stroke="{LARANJA}" stroke-width="5"/><text class="semi" x="640" y="81" font-size="17" text-anchor="middle">Análise</text></g>
<g class="box" style="animation: nasce 4s ease-in-out 2.6s infinite;"><circle cx="1100" cy="75" r="46" fill="#fff" stroke="{VERMELHO}" stroke-width="5"/><text class="semi" x="1100" y="81" font-size="17" text-anchor="middle">Decisão</text></g>
</svg>
"""


if __name__ == "__main__":
    SAIDA.mkdir(exist_ok=True)
    for nome, fn in [("banner", banner), ("pilares", pilares), ("fluxo", fluxo)]:
        (SAIDA / f"{nome}.svg").write_text(fn(), encoding="utf-8")
        print(nome, (SAIDA / f"{nome}.svg").stat().st_size // 1024, "KB")
