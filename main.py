import requests
import json
from utils import getData,processEtsy
from config import ACCESS_TOKEN, CLIENT_ID

url = "https://chitchats.com/api/v1/clients/"+CLIENT_ID+"/shipments"
headers = {"Authorization": ACCESS_TOKEN,"Content-Type":"application/json"}
processEtsy()
datas = getData()

for row in datas:
	data = {
    "name": row[0],
    "address_1": row[1],
    "city": row[2],
    "province_code": row[3],
    "postal_code": row[4],
    "country_code": row[5],
    "description": row[6],
    "value": row[7],
    "value_currency": row[8],
    "package_type": row[9],
    "size_unit": row[10],
    "size_x": row[11],
    "size_y": row[12],
    "size_z": row[13],
    "weight_unit": row[14],
    "weight": row[15],
    "postage_type": row[16],
    "ship_date": row[17]
  }

	print ("Sending Shipment Creation")
	response = requests.post(url=url, headers=headers, data=json.dumps(data))

	print (response.status_code)
	print (response.content)