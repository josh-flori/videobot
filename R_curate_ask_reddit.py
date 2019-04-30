# /users/josh.flori/desktop/test/bin/python3 /users/josh.flori/desktop/test/lib/python3.6/site-packages/videobot/R_curate.py

from videobot import get_comments_from_reddit
from videobot import write_to_sheets
from googleapiclient.discovery import build
from oauth2client import file
from httplib2 import Http
from string import ascii_lowercase
from oauth2client.service_account import ServiceAccountCredentials
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
store = file.Storage('credentials.json')
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    '/users/josh.flori/drive_backup/drive_backup/python_scripts/client_secret.json', scope)
service = build('sheets', 'v4', http=creds.authorize(Http()))                
_id='1sIS1r-vtHNVRll_NR3vMr8Pbdt91B34vRrvAe20Ym9g'
threads = service.spreadsheets().values().get(spreadsheetId=_id, range='Sheet1!A2:A').execute().get(
    'values', [])
    

i=1
for thread in threads:
    
    column=ascii_lowercase[i]
    
    # get comment data
    total_list = get_comments_from_reddit.get_comments(thread[0])

    write_to_sheets.write_to_sheet(total_list,column,service,_id,'AskReddit',2)
    
    i+=1