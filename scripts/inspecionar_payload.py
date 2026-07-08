import re
from curl_cffi import requests

s = requests.Session(impersonate="chrome")
r = s.get("https://casadosdados.com.br/assets-v2/kfmOOr3p.js", timeout=60)
text = r.text

for term in ["busca_textual", "termo", "situacao_cadastral", "VILA CARRAO"]:
    count = text.count(term)
    print(term, count)

# find v5 payload builder - search for busca_textual near pesquisa
idx = text.find("busca_textual")
while idx >= 0:
    snippet = text[max(0, idx - 150): idx + 400]
    if "pesquisa" in snippet.lower() or "query" in snippet.lower() or "municipio" in snippet.lower():
        print("--- busca_textual ---")
        print(snippet)
    idx = text.find("busca_textual", idx + 1)
