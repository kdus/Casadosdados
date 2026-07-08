from curl_cffi import requests

s = requests.Session(impersonate="chrome")
r = s.get("https://casadosdados.com.br/assets-v2/kfmOOr3p.js", timeout=60)
text = r.text
idx = text.find("searchCnpjByQuery")
print(text[idx:idx+1200])
