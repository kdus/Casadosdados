import re
from curl_cffi import requests

s = requests.Session(impersonate="chrome")
r = s.get("https://casadosdados.com.br/assets-v2/kfmOOr3p.js", timeout=60)
text = r.text

for term in ["turnstile", "cf-turnstile", "headerApiWAF", "token"]:
    idx = text.find("turnstile") if term == "turnstile" else text.find(term)
    count = text.count(term)
    print(term, count)
    if term == "turnstile":
        pos = 0
        shown = 0
        while shown < 5:
            pos = text.find("turnstile", pos)
            if pos < 0:
                break
            if "pesquisa" in text[pos:pos+300].lower() or "search" in text[pos:pos+300].lower():
                print(text[max(0,pos-200):pos+400])
                shown += 1
            pos += 8
