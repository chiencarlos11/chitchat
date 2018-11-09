from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from config import SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME
from requests_oauthlib import OAuth1Session
from requests_oauthlib import OAuth1
import requests
import urllib.parse as urlparse
import json
import time, datetime

from config import client_key, client_secret, resource_owner_key, resource_owner_secret

def next_available_row(worksheet):
    str_list = filter(None, worksheet.col_values(1))  # fastest
    return str(len(str_list)+1)


def getData():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    data_dict = []
    # If modifying these scopes, delete the file token.json.
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets'

    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print('Name, Province Code, Postal Code, Country Code:')

        #Range Index starts with 2
        range_index = 2

        for row in values:
            # Print columns A and E, which correspond to indices 0 and 4.
            if len(row) < 19:
                print('%s, %s, %s, %s' % (row[0], row[3], row[4], row[5]))
                data_dict.append(row)


                UPDATE_RANGE_NAME = 'Shipments!'+ str(range_index) +':S' + str(range_index)
                
                values = [["Shipment Created"]]
                body = {'values': values}
                result = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=UPDATE_RANGE_NAME,valueInputOption="RAW",body=body).execute()
                print('{0} cells updated.'.format(result.get('updatedCells')))

            #increment range
            range_index += 1

    

    return data_dict


def EtsyOAuthSetup():

    request_token_url = "https://openapi.etsy.com/v2/oauth/request_token?scope=email_r%20listings_r"
    client_key = "r2a7ex43crs8ron8phdygf2h"
    client_secret = "32iwqw0vtq"

    oauth = OAuth1Session(client_key,client_secret=client_secret)
    # r = etsy.get(url,headers={"Content-Type":"application/json"})
    fetch_response = oauth.fetch_request_token(request_token_url)
    print(fetch_response.get('login_url'))

    resource_owner_key = fetch_response.get('oauth_token')
    resource_owner_secret = fetch_response.get('oauth_token_secret')

    verifier = input('Please input the verifier:\n')

    access_token_url = "https://openapi.etsy.com/v2/oauth/access_token"

    oauth = OAuth1(client_key,
                   client_secret=client_secret,
                   resource_owner_key=resource_owner_key,
                   resource_owner_secret=resource_owner_secret,
                   verifier=verifier)

    r = requests.post(url=access_token_url, auth=oauth)

    credentials = urlparse.parse_qs(r.content)
    print("credentials %s", str(credentials))
    resource_owner_key = credentials[b'oauth_token'][0]
    resource_owner_secret = credentials[b'oauth_token_secret'][0]

    oauth = OAuth1Session(client_key,
                          client_secret=client_secret,
                          resource_owner_key=resource_owner_key,
                          resource_owner_secret=resource_owner_secret)

    r = oauth.get(protected_url)

    oauth = OAuth1(client_key,
                   client_secret=client_secret,
                   resource_owner_key=resource_owner_key,
                   resource_owner_secret=resource_owner_secret)

    print ("client_key = " + str(client_key))
    print("client_secret = " + str(client_secret))
    print ("resource_owner_key = " + str(resource_owner_key))
    print ("resource_owner_secret = " + str(resource_owner_secret))

    r = requests.get(url=protected_url, auth=oauth)

    print (str(r.content))

def Etsy():

    today_epoch = time.mktime(datetime.date.today().timetuple())
    protected_url = "https://openapi.etsy.com/v2/shops/tophatandmonocle/receipts?includes=Transactions&&min_created=" + str(today_epoch) + "&limit=500&was_shipped=false"
    oauth = OAuth1(client_key,
                   client_secret=client_secret,
                   resource_owner_key=resource_owner_key,
                   resource_owner_secret=resource_owner_secret)

    r = requests.get(url=protected_url, auth=oauth,headers={"Content-Type":"application/json"})

    json_response = json.loads(r.content)

    return json_response

def processEtsy():

    # If modifying these scopes, delete the file token.json.
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets'

    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()

    orders = Etsy()

    for order in orders.get('results'):
        if order.get('country_id') and order.get('country_id') == 209:
            name = order.get('name')
            address = ""
            if order.get('first_line'):
                address = str(order.get('first_line'))
            if order.get('second_line'):
                address = address + " " + str(order.get('second_line'))
            city = order.get('city')
            state = order.get('state')
            zip_code = order.get('zip')
            country_id = order.get('country_id')
            title = str(order.get('Transactions')[0].get('transaction_id')) + " - " + order.get('Transactions')[0].get('title')
            total_price = order.get('total_price')

            print("name = " + str(name))
            print("address = " + str(address))
            print("city = " + str(city))
            print("state = " + str(state))
            print("zip_code = " + str(zip_code))
            print("country_id = " + str(country_id))
            print("\n")

            values = [[name,address,city,state,zip_code,"US",title,total_price,"usd","parcel","cm",10,5,2.5,"g",250,"usps_priority","today"]]
            body = {'values': values}
            APPEND_RANGE_NAME = 'Shipments'
            sheet.values().append(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                            range=APPEND_RANGE_NAME,valueInputOption="RAW",body=body).execute()


