import re
from curl_cffi import requests

s = requests.Session(impersonate="chrome")
r = s.get(
    "https://casadosdados.com.br/solucao/cnpj/condominio-edificio-matisse-96512355000139",
    timeout=60,
)
html = r.text

for term in ["CONDOMINIO EDIFICIO MATISSE", "96512355000139", "razao_social", "capital_social", "situacao_cadastral"]:
    print(term, term.lower() in html.lower() or term in html)

# procurar JSON embebido
for pat in [r'"cnpj"\s*:\s*"96512355000139"', r'application/ld\+json', r'__NUXT_DATA__', r'window\.__']:
    m = re.search(pat, html)
    print(pat, "->", bool(m))

# salvar trecho com dados
idx = html.lower().find("condominio edificio matisse")
print("context:", html[max(0, idx - 200): idx + 400])
