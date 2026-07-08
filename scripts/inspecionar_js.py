import re
from curl_cffi import requests

s = requests.Session(impersonate="chrome")
r = s.get("https://casadosdados.com.br/assets-v2/kfmOOr3p.js", timeout=60)
text = r.text

idx = text.find("v5/public/cnpj/pesquisa")
print("idx:", idx)
if idx >= 0:
    print(text[max(0, idx - 500): idx + 800])

# find detail endpoint patterns near public/cnpj
for m in re.finditer(r"public/cnpj/[a-zA-Z0-9_\-/{}]+", text):
    val = m.group(0)
    if "bloquear" not in val and "atualizar" not in val and "filiai" not in val:
        print("PATH:", val)
