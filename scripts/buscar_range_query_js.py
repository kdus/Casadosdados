"""Busca range_query nos chunks JS do site."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from curl_cffi import requests as cf

s = cf.Session(impersonate="chrome120")
main = s.get("https://casadosdados.com.br/assets-v2/kfmOOr3p.js", timeout=60).text
chunks = sorted(set(re.findall(r"\./([A-Za-z0-9_-]+\.js)", main)))
print("chunks", len(chunks))
for name in chunks:
    url = f"https://casadosdados.com.br/assets-v2/{name}"
    try:
        js = s.get(url, timeout=30).text
    except Exception as exc:
        print(name, "ERR", exc)
        continue
    if "range_query" in js or "data_abertura" in js or "dataAbertura" in js:
        print("===", name, "===")
        for needle in ["range_query", "data_abertura", "dataAbertura"]:
            pos = js.find(needle)
            if pos >= 0:
                print(js[max(0, pos - 150) : pos + 400])
