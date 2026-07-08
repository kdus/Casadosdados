from curl_cffi import requests
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from services.nuxt_parser import montar_url_detalhe

s = requests.Session(impersonate="chrome")
r = s.get("https://api.casadosdados.com.br/v4/public/pesquisa/nome", params={"q":"condominio","pagina":1}, timeout=30)
item = r.json()["cnpjs"][0]
cnpj = item["cnpj"]
razao = item["razao_social"]
url = montar_url_detalhe(cnpj, razao)
print("url", url)
html = s.get(url, timeout=60).text
print("status len", len(html), "NUXT", "__NUXT_DATA__" in html, "404" in html[:500])
