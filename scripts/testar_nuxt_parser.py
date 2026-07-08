from curl_cffi import requests
from services.nuxt_parser import mapear_html_para_empresa

s = requests.Session(impersonate="chrome")
html = s.get(
    "https://casadosdados.com.br/solucao/cnpj/condominio-edificio-matisse-96512355000139",
    timeout=60,
).text

empresa = mapear_html_para_empresa(html)
print(empresa.cnpj)
print(empresa.razao_social)
print(empresa.bairro)
print(empresa.municipio)
print(empresa.situacao_cadastral)
print(empresa.email)
