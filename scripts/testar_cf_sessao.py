import time
from curl_cffi import requests
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from services.nuxt_parser import mapear_html_para_empresa, montar_url_detalhe

s = requests.Session(impersonate="chrome")
s.headers.update({
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9",
})

# aquece sessao
s.get("https://casadosdados.com.br/solucao/cnpj/pesquisa-avancada", timeout=60)
time.sleep(1)

urls = [
    "https://casadosdados.com.br/solucao/cnpj/condominio-edificio-matisse-96512355000139",
    "https://casadosdados.com.br/solucao/cnpj/condominio-edificio-bela-vista-ii-97553800000171",
]

for url in urls:
    r = s.get(url, timeout=60)
    print(url.split('/')[-1][:40], "len", len(r.text), "cf", "Just a moment" in r.text, "nuxt", "__NUXT_DATA__" in r.text)
    time.sleep(2)
