import requests
import json


def getPartUrlCard(card_id):
    card_id = int(card_id)
    param1 = card_id//100000
    param2 = card_id//1000

    urlPart = ''
    if param1 >= 0 and param1 <= 143:
        urlPart = 'basket-01.wb.ru'
    elif param1 >= 144 and param1 <= 287:
        urlPart = 'basket-02.wb.ru'
    elif param1 >= 288 and param1 <= 431:
        urlPart = 'basket-03.wb.ru'
    elif param1 >= 432 and param1 <= 719:
        urlPart = 'basket-04.wb.ru'
    elif param1 >= 720 and param1 <= 1007:
        urlPart = 'basket-05.wb.ru'
    elif param1 >= 1008 and param1 <= 1061:
        urlPart = 'basket-06.wb.ru'
    elif param1 >= 1062 and param1 <= 1115:
        urlPart = 'basket-07.wb.ru'
    elif param1 >= 1116 and param1 <= 1169:
        urlPart = 'basket-08.wb.ru'
    elif param1 >= 1170 and param1 <= 1313:
        urlPart = 'basket-09.wb.ru'
    else:
        urlPart = 'basket-10.wb.ru'

    url = f'https://{urlPart}/vol{param1}/part{param2}/{card_id}/'
    return url


def getUrlsImages(urlPart, num, size: str = 'c516x688'):
    # size: tm, c246x328 c516x688
    return [f'{urlPart}images/{size}/{i}.jpg' for i in range(1, num+1)]


def getCard(card_id):
    urlPart = getPartUrlCard(card_id)
    url = urlPart+'info/ru/card.json'

    card = json.loads(requests.get(url).text)

    return {
        'fullname': card.get('imt_name', 'Товар'),
        'name': card['subj_name'],
        'images': getUrlsImages(
            urlPart,
            card['media']['photo_count']
        ),
        'link': f'https://www.wildberries.ru/catalog/{card_id}/detail.aspx'
    }


def searchWildberries(filename, max_objects: int = 10) -> None | list[str]:
    url = 'https://search-by-photo.wb.ru/uploadsearch'
    with open(filename, 'rb') as f:
        image = f.read()
    resp = json.loads(requests.post(url, data=image).text)
    if resp['status'] != 'ok':
        return None

    # return [f'https://wildberries.ru/catalog/{i}/detail.aspx' for i in resp['data']['detections'][0]['nm_ids']]
    return [getCard(i) for i in resp['data']['detections'][0]['nm_ids'][:max_objects]]

