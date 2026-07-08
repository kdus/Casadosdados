import re
from curl_cffi import requests

s = requests.Session(impersonate="chrome")
r = s.get("https://casadosdados.com.br/assets-v2/kfmOOr3p.js", timeout=60)
text = r.text

for term in ["baiacu", "fetchBaiacu", "apiUrl", "baseURL", "publicURL"]:
    idx = 0
    while True:
        idx = text.find(term, idx)
        if idx < 0:
            break
        print(f"--- {term} @ {idx} ---")
        print(text[max(0, idx - 200): idx + 400])
        idx += len(term)
