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

point = toponym_point.copy()
marks = []

for i in range(10):
    organization = json_response["features"][i]
    org_name = organization["properties"]["CompanyMetaData"]["name"]
    org_address = organization["properties"]["CompanyMetaData"]["address"]
    org_hours = organization["properties"]["CompanyMetaData"]["Hours"]

    org_point = organization["geometry"]["coordinates"]
    point = [point[0] + org_point[0], point[1] + org_point[1]]

    if not org_hours["Availabilities"]:
        marks.append("{0},{1},pm2grl".format(*org_point))
    elif "TwentyFourHours" in org_hours["Availabilities"][0] and "Everyday" in org_hours["Availabilities"][0]:
        marks.append("{0},{1},pm2gnl".format(*org_point))
    else:
        marks.append("{0},{1},pm2bll".format(*org_point))

    print(f"Аптека №{i + 1}")
    print("\tАдрес:", org_address)
    print("\tНазвание:", org_name)
    print("\tВремя работы:", org_hours["text"])
    print(f"\tРасстояние от исходной точки: {round(lonlat_distance(toponym_point, org_point), 3)}м")

point = [point[0] / 11, point[1] / 11]

map_params = {
    "ll": ",".join(map(str, point)),
    "l": "map",
    "pt": "~".join([",".join([*map(str, toponym_point), "flag"]), *marks])
}
map_api_server = "http://static-maps.yandex.ru/1.x/"
response = requests.get(map_api_server, params=map_params)
Image.open(BytesIO(
    response.content)).show()
