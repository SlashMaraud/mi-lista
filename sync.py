import re, sys, urllib.request
from pathlib import Path

ELCANO = "https://tokyo2.elcano-ipfs.workers.dev/k51qzi5uqu5dh5qej4b9wlcr5i6vhc7rcfkekhrxqek5c9lk6gdaiik820fecs/hashes_acestream.m3u"
AMIGO = "https://raw.githubusercontent.com/diegofornite1983-lgtm/Mi-lista-/refs/heads/main/lista-amigos"
SALIDA = Path("lista.m3u")
MARCA = "# ZONA PERSONAL"
GRUPO = "⭐ ELCANO [MÁXIMA CALIDAD]"

def bajar(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8-sig", errors="replace")

def extraer(texto):
    i = texto.find(MARCA)
    if i == -1:
        return None
    return re.sub(r"#\s*Ultima sincronizacion:.*", "", texto[i:]).strip()

# 1) Zona automática: Elcano directo
try:
    lineas = bajar(ELCANO).splitlines()
except Exception as e:
    sys.exit(f"ERROR descargando Elcano: {e}")

auto = []
for i, l in enumerate(lineas):
    if not l.startswith("#EXTINF:"):
        continue
    url = None
    for x in lineas[i + 1:]:
        x = x.strip()
        if x.startswith("#EXTINF:"):
            break
        if x and not x.startswith("#"):
            url = x
            break
    if not url:
        continue
    m = re.search(r"[0-9a-fA-F]{40}", url)
    if m:
        url = f"http://127.0.0.1:6878/ace/getstream?id={m.group(0)}"
    inf = re.sub(r'group-title="[^"]*"', f'group-title="{GRUPO}"', l)
    if "group-title=" not in inf:
        inf = inf.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{GRUPO}"', 1)
    auto += [inf, url]

if not auto:
    sys.exit("ERROR: Elcano devolvió 0 canales")

# 2) Zona personal: del creador, con respaldo en tu última copia
personal = None
try:
    personal = extraer(bajar(AMIGO))
except Exception as e:
    print("Aviso: no pude bajar la lista del creador:", e)
if personal is None and SALIDA.is_file():
    personal = extraer(SALIDA.read_text(encoding="utf-8"))
if personal is None:
    sys.exit("ERROR: no hay zona personal")

cabecera = (
    '#EXTM3U url-tvg="https://raw.githubusercontent.com/davidmuma/EPG_dobleM/master/guiatv.xml,'
    'https://epgshare01.online/epgshare01/epg_ripper_NL1.xml.gz" refresh="3600"\n'
    '#EXTVLCOPT:network-caching=1000\n\n'
    '# ==========================================\n'
    f'# ZONA AUTOMATICA: {GRUPO}\n'
    '# ==========================================\n'
)
sep = "\n\n# ==========================================\n"
SALIDA.write_text(cabecera + "\n".join(auto) + sep + personal + "\n", encoding="utf-8")
print(f"OK: {len(auto) // 2} canales Elcano")
