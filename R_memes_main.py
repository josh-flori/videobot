# /users/josh.flori/desktop/test/bin/python3 /users/josh.flori/desktop/test/lib/python3.6/site-packages/videobot/R_memes_main.py

from videobot import get_audio
from videobot import get_image_data_from_sheet
from videobot import initialize_folder
from googleapiclient.discovery import build
from oauth2client import file
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
from string import ascii_lowercase
from videobot import split_image


SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
store = file.Storage('credentials.json')
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    '/users/josh.flori/drive_backup/drive_backup/python_scripts/client_secret.json', scope)
service = build('sheets', 'v4', http=creds.authorize(Http()))                
_id='1sIS1r-vtHNVRll_NR3vMr8Pbdt91B34vRrvAe20Ym9g'
urls = service.spreadsheets().values().get(spreadsheetId=_id, range='Memes!A:A').execute().get(
    'values', [])
text = service.spreadsheets().values().get(spreadsheetId=_id, range='Memes!C:C').execute().get(
    'values', [])


# clear out memes folder
initialize_folder.initialize_folder('/users/josh.flori/desktop/memes/',"second")

# download only curated images from sheet
get_image_data_from_sheet.get_image_data(urls)

# split out into individual images
for image_num in range(len(text)):
    split_image.split_image(image_num)