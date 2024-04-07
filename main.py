import sys
from io import BytesIO

import requests
from PIL import Image

from functions import lonlat_distance

toponym_to_find = " ".join(sys.argv[1:])

geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

geocoder_params = {
    "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
    "geocode": toponym_to_find,
    "format": "json"}

response = requests.get(geocoder_api_server, params=geocoder_params)

if not response:
    exit()

json_response = response.json()
toponym = json_response["response"]["GeoObjectCollection"][
    "featureMember"][0]["GeoObject"]
toponym_coodrinates = toponym["Point"]["pos"]
toponym_point = list(map(float, toponym_coodrinates.split(" ")))

search_api_server = "https://search-maps.yandex.ru/v1/"
api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

search_params = {
    "apikey": api_key,
    "text": "аптека",
    "lang": "ru_RU",
    "ll": ",".join(map(str, toponym_point)),
    "type": "biz"
}

response = requests.get(search_api_server, params=search_params)

json_response = response.json()

organization = json_response["features"][0]
org_name = organization["properties"]["CompanyMetaData"]["name"]
org_address = organization["properties"]["CompanyMetaData"]["address"]
org_hours = organization["properties"]["CompanyMetaData"]["Hours"]["text"]

org_point = organization["geometry"]["coordinates"]
point = [(org_point[0] + toponym_point[0]) / 2, (org_point[1] + toponym_point[1]) / 2]

print("Адрес:", org_address)
print("Название:", org_name)
print("Время работы:", org_hours)
print(f"Расстояние от исходной точки: {round(lonlat_distance(toponym_point, org_point), 3)}м")

map_params = {
    "ll": ",".join(map(str, point)),
    "l": "map",
    "pt": "~".join([",".join([*map(str, toponym_point), "flag"]), "{0},{1},pm2dgl".format(*org_point)])
}
map_api_server = "http://static-maps.yandex.ru/1.x/"
response = requests.get(map_api_server, params=map_params)
Image.open(BytesIO(
    response.content)).show()
