# Изучить список открытых API (https://www.programmableweb.com/category/all/apis).
# Найти среди них любое, требующее авторизацию (любого типа). Выполнить запросы к нему, пройдя авторизацию.
# Ответ сервера записать в файл.+

import requests
import datetime

date_ = datetime.date(2020, 6, 12)

link_api = 'https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?'

params = {'api_key': 'bD57aRUc2Lc3G071eVcbioM7DsmP2wXaYjoSSUme',
          'earth_date': date_,
          'camera': 'fhaz'}

get_ = requests.get(link_api, params=params)
info_ = get_.json()

url_image = info_['photos'][1]['img_src']

get_image = requests.get(url_image)

with open('mars.jpg', 'wb') as file_foto:
    file_foto.write(get_image.content)
