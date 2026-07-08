import re
from curl_cffi import requests

s = requests.Session(impersonate="chrome")
r = s.get("https://casadosdados.com.br/assets-v2/kfmOOr3p.js", timeout=60)
text = r.text

for pat in [
    r"/v\d+/[^\"'`\\s]{5,80}",
    r"api\.casadosdados\.com\.br[^\"'`\\s]*",
]:
    matches = re.findall(pat, text)
    for m in sorted(set(matches)):
        if "cnpj" in m.lower() or "query" in m.lower() or "pesquis" in m.lower():
            print(m)
