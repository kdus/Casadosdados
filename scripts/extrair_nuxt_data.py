import re
import json
from curl_cffi import requests

s = requests.Session(impersonate="chrome")
r = s.get(
    "https://casadosdados.com.br/solucao/cnpj/condominio-edificio-matisse-96512355000139",
    timeout=60,
)
html = r.text

# Nuxt 3 payload
m = re.search(r'<script type="application/json" id="__NUXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
if m:
    raw = m.group(1)
    print("NUXT_DATA len:", len(raw))
    print(raw[:2000])
else:
    print("NUXT_DATA not found")
    # try alternate patterns
    for pat in [r'__NUXT_DATA__', r'window\.__NUXT__']:
        print(pat, html.find(pat))
