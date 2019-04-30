# /users/josh.flori/desktop/test/bin/python3 /users/josh.flori/desktop/test/lib/python3.6/site-packages/videobot/R_curate_memes.py

from videobot import get_audio
from videobot import write_to_sheets
from videobot import get_image_data_from_sheet
from videobot import initialize_folder
from googleapiclient.discovery import build
from oauth2client import file
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
from string import ascii_lowercase


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


# if getting directly from reddit
# text_list=get_image_data_from_reddit.get_image_data('memes',5)

text_list=get_image_data_from_sheet.get_image_data(urls)


write_to_sheets.write_to_sheet(text_list,'C',service,_id,'Memes!',1)
#write_to_sheets.write_to_sheet(text_list,service,_id)

# get TITLE audio
#get_audio.get_audio(thread_title,'/users/josh.flori/desktop/demo/','thread_title.mp3','thread_title.wav')

