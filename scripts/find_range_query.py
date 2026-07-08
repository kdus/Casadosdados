from curl_cffi import requests

s = requests.Session(impersonate="chrome")
text = s.get("https://casadosdados.com.br/assets-v2/kfmOOr3p.js", timeout=60).text
needle = "range_query"
pos = 0
count = 0
while count < 5:
    pos = text.find(needle, pos)
    if pos < 0:
        break
    print("---", pos, "---")
    print(text[max(0, pos - 200): pos + 500])
    pos += len(needle)
    count += 1
