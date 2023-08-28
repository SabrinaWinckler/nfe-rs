from itertools import product
from nfe import NFe
from product import Product
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googlesearch import search

def update():
    update_range = ''
    new_record = ["str(query)", "qnt", "title", "price"]
    range_to_update = f'{sheet_name}!A{num_rows + 1}:D{num_rows + 1}'
    request_body = {
        'values': [new_record]
        }
    request = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=range_to_update, valueInputOption='RAW', body=request_body)
    response = request.execute()
    print(response)


keyfile = './secretes.json'
scope = ['https://www.googleapis.com/auth/spreadsheets']
credentials = service_account.Credentials.from_service_account_file(keyfile, scopes=scope)
service = build('sheets', 'v4', credentials=credentials)
spreadsheet_id = '1bPyum8hlQddBfn4yloaBDt6OrTinjLTGwOot-hV6OJ0'
sheet_name = 'Entrada'

result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_name).execute()
records = result.get('values', [])
num_rows = len(records)

import pytest
pytest.set_trace()

products = []
product = Product(code="code",description="description",price=1.5,ean_13="1234")
products.append(product)
products.append(product)
nf = NFe()
nf.set_cliente()
nf.create_nf()
nf.include_products(products=products)
nf.view_note()