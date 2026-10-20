"""Renderiza os SVGs no Chromium (Playwright) em instantes diferentes, para conferir o visual."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

raiz = Path(__file__).resolve().parent.parent
saida = Path(sys.argv[1]) if len(sys.argv) > 1 else raiz / "build" / "previa"
saida.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 900})
    for nome in ["banner", "pilares", "fluxo"]:
        for t in (500, 3000):
            pg.goto((raiz / "assets" / f"{nome}.svg").as_uri())
            pg.wait_for_timeout(t)
            pg.screenshot(path=str(saida / f"{nome}_{t}.png"))
    erros = []
    pg.on("console", lambda m: erros.append(m.text) if m.type == "error" else None)
    b.close()
print("ok", saida)
