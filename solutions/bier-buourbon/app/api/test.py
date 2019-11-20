# for testing the api

import requests

from app.api.main import update_item,read_item

external_data = {
    "id": "123",
    "copper_percentage":0.01
}

url = 'http://127.0.0.1:8000/copper'

r = requests.post(url, json=external_data)

r = requests.get(url)
print(r.json())

a = update_item('5',10)

print(a)
