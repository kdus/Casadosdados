from curl_cffi import requests
import time
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from services.nuxt_parser import mapear_html_para_empresa, montar_url_detalhe

s = requests.Session(impersonate="chrome120")
s.get("https://casadosdados.com.br/solucao/cnpj/pesquisa-avancada", timeout=60)
s.headers.update({
    "Origin": "https://casadosdados.com.br",
    "Referer": "https://casadosdados.com.br/solucao/cnpj/pesquisa-avancada",
})

termo = "condominio"
matches = []
pagina = 1
while pagina <= 5 and len(matches) < 5:
    r = s.get(
        "https://api.casadosdados.com.br/v4/public/pesquisa/nome",
        params={"q": termo, "pagina": pagina},
        timeout=30,
    )
    d = r.json()
    print("pagina", pagina, "items", len(d.get("cnpjs", [])))
    for item in d.get("cnpjs", []):
        cnpj = item["cnpj"]
        razao = item.get("razao_social", "")
        sit = item.get("situacao_cadastral", {})
        if isinstance(sit, dict) and sit.get("situacao_atual") != "ATIVA":
            continue
        url = montar_url_detalhe(cnpj, razao)
        html = s.get(url, timeout=60).text
        if "__NUXT_DATA__" not in html:
            print("SKIP sem NUXT", cnpj, len(html), "CF", "Just a moment" in html)
            continue
        emp = mapear_html_para_empresa(html)
        if emp.bairro.upper() == "VILA CARRAO" and emp.municipio.upper() == "SAO PAULO" and emp.uf.upper() == "SP":
            matches.append(emp)
            print("MATCH", emp.cnpj, emp.razao_social)
        time.sleep(1)
    pagina += 1

print("total matches", len(matches))
