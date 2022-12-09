import requests
import json
from urllib.parse import unquote 


headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0",
    "X-Requested-With": "XMLHttpRequest"
}

url = 'https://www.aliprice.com/Index/searchImage.html?modal=1'
resp = requests.post(
    url,
    data={'filename': 'canvas.png', 'name': 'image'},
    headers=headers,
    allow_redirects=False,
    files={'image': open('canvas.png', 'rb')}
    ).text
url = 


print(resp, type(resp))
print(json.loads(resp.encode('utf-8')))
