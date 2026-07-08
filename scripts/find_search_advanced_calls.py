from curl_cffi import requests

s = requests.Session(impersonate="chrome")
text = s.get("https://casadosdados.com.br/assets-v2/kfmOOr3p.js", timeout=60).text
needle = "searchAdvanced("
pos = 0
while True:
    pos = text.find(needle, pos)
    if pos < 0:
        break
    print("---", pos, "---")
    print(text[max(0, pos - 250): pos + 350])
    pos += len(needle)
