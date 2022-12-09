import requests

url = "https://img.icu/uploads/GSkP1iUwK6.jpeg"
req = requests.get(url, headers={"User-Agent": "Poshel Suka v zhopu ya sizhu na Iphone 16 suka"})

print(req.status_code)