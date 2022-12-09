import json
from urllib.parse import unquote 

a = '{"success":1,"url":"https:\/\/www.aliprice.com\/Index\/searchimage.html?phash=KNmwNZgjiDE%252B1HxS%252BBM8AISLMEWHlv%252FCithoQP78SHTPQJtlEOwWUb9GcsC7kjt1yQf80r5n9TlIcuNXOGvRUQ%253D%253D&picture=%2Fupload%2Fpics%2F2022-10-26%2F20221026%2F9c70b2b5d9e91cf795b23b807fb715e2.png"}'

print(
    unquote(json.loads(a)['url'])
)