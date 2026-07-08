"""Script temporario para descobrir endpoints da API."""

import re
from curl_cffi import requests

s = requests.Session(impersonate="chrome")
r = s.get("https://casadosdados.com.br/assets-v2/kfmOOr3p.js", timeout=60)
text = r.text
print("STATUS JS:", r.status_code, "LEN:", len(text))

patterns = [
    r"https?://[^\"'`\\s]+",
    r"/v\d+/[^\"'`\\s]+",
    r"api\.casadosdados[^\"'`\\s]*",
    r"public/cnpj[^\"'`\\s]*",
]

found = set()
for pat in patterns:
    for m in re.findall(pat, text):
        if any(k in m.lower() for k in ("api", "cnpj", "search", "public", "pesquisa")):
            found.add(m)

for item in sorted(found):
    print(item)
