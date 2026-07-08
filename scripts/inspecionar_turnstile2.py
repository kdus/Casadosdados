from curl_cffi import requests

s = requests.Session(impersonate="chrome")
r = s.get("https://casadosdados.com.br/assets-v2/kfmOOr3p.js", timeout=60)
text = r.text
key = "0x4AAAAAAAHDvOVlOi2CeG0s"
idx = text.find(key)
print("idx", idx)
if idx >= 0:
    print(text[max(0, idx-400):idx+800])
