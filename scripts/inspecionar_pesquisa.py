import re
from curl_cffi import requests

s = requests.Session(impersonate="chrome")
r = s.get("https://casadosdados.com.br/assets-v2/kfmOOr3p.js", timeout=60)
text = r.text

for term in ["searchAdvanced", "pathSearchAdvanced", "searchCnpjAdvanced"]:
    idx = 0
    while True:
        idx = text.find(term, idx)
        if idx < 0:
            break
        print(f"--- {term} @ {idx} ---")
        print(text[max(0, idx - 100): idx + 600])
        idx += len(term)
