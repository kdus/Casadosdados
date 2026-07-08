import re
from curl_cffi import requests

s = requests.Session(impersonate="chrome")
html = s.get("https://casadosdados.com.br/solucao/cnpj/pesquisa-avancada", timeout=60).text
scripts = re.findall(r'src="(/assets-v2/[^"]+\.js)"', html)
print("scripts", len(scripts))
for src in scripts:
    url = "https://casadosdados.com.br" + src
    js = s.get(url, timeout=60).text
    if "searchAdvanced" in js or "pesquisa" in js and "query" in js:
        print("FOUND in", src, "len", len(js))
        idx = js.find("searchAdvanced")
        if idx >= 0:
            print(js[max(0, idx-300):idx+500])
