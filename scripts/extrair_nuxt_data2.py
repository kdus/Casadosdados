from curl_cffi import requests

s = requests.Session(impersonate="chrome")
r = s.get(
    "https://casadosdados.com.br/solucao/cnpj/condominio-edificio-matisse-96512355000139",
    timeout=60,
)
html = r.text
idx = html.find("__NUXT_DATA__")
print(html[idx:idx+3000])
