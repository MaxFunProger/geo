import sys
from math import *
from io import BytesIO
# Этот класс поможет нам сделать картинку из потока байт

import requests
from PIL import Image
from geo import map_size
from PIL import ImageFont, ImageDraw

# Пусть наше приложение предполагает запуск:
# python search.py Москва, ул. Ак. Королева, 12
# Тогда запрос к геокодеру формируется следующим образом:
toponym_to_find = " ".join('Москва, ул. Ак. Королева, 12')

geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

geocoder_params = {
    "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
    "geocode": toponym_to_find,
    "format": "json"}

response = requests.get(geocoder_api_server, params=geocoder_params)

if not response:
    # обработка ошибочной ситуации
    pass

# Преобразуем ответ в json-объект
json_response = response.json()
# Получаем первый топоним из ответа геокодера.
toponym = json_response["response"]["GeoObjectCollection"][
    "featureMember"][0]["GeoObject"]
# Координаты центра топонима:
toponym_coodrinates = toponym["Point"]["pos"]
# Долгота и широта:
toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
toponym_size = map_size(toponym)

######################################
search_api_server = "https://search-maps.yandex.ru/v1/"
api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

address_ll = toponym_longitude + ',' + toponym_lattitude

search_params = {
    "apikey": api_key,
    "text": "аптека",
    "lang": "ru_RU",
    "ll": address_ll,
    "type": "biz"
}

response = requests.get(search_api_server, params=search_params)

if not response:
    pass

###################################

# Преобразуем ответ в json-объект
json_response = response.json()

# Получаем первую найденную организацию.
organization = json_response["features"][0]
# Название организации.
org_name = organization["properties"]["CompanyMetaData"]["name"]
timetable = organization["properties"]["CompanyMetaData"]["Hours"]["text"]
# Адрес организации.
org_address = organization["properties"]["CompanyMetaData"]["address"]

# Получаем координаты ответа.
point = organization["geometry"]["coordinates"]
org_point = "{0},{1}".format(point[0], point[1])
delta = "0.005"
# Собираем параметры для запроса к StaticMapsAPI:
print(toponym_coodrinates, org_point, sep='\n')
map_params = {
    "l": "map",
    "pt": ",".join([toponym_longitude, toponym_lattitude, 'pm2am']) + '~' + "{0},pm2bm".format(org_point)
}

map_api_server = "http://static-maps.yandex.ru/1.x/"
# ... и выполняем запрос
response = requests.get(map_api_server, params=map_params)
r = Image.open(BytesIO(
    response.content))
image = Image.new("RGB", (500, 25), (255, 255, 255))
draw = ImageDraw.Draw(image)
print(timetable)

lat1, lon1 = float(point[1]), float(point[0])
lat2, lon2 = float(toponym_lattitude), float(toponym_longitude)
lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
dlon = lon2 - lon1
dlat = lat2 - lat1
res = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
out = 2 * asin(sqrt(res))
out = out * 6371
timetable += ' ' + str(out) + ' km'
timetable = timetable.encode('utf-8').decode('latin-1')
draw.text((0, 0), str(timetable), (0, 0, 0))
r.paste(image, (0, 0))
r.show()
# draw.text((x, y),"Sample Text",(r,g,b))

# Создадим картинку
# и тут же ее покажем встроенным просмотрщиком операционной системы
