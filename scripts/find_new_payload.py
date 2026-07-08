from curl_cffi import requests

s = requests.Session(impersonate="chrome")
text = s.get("https://casadosdados.com.br/assets-v2/kfmOOr3p.js", timeout=60).text
for term in ["somente_mei", "busca_textual", "codigo_atividade", "situacao_cadastral", "mais_filtros", "pagina", "limite"]:
    print(term, text.count(term))
    pos = text.find(term)
    if pos >= 0:
        print(text[max(0,pos-150):pos+300])
        print("---")
