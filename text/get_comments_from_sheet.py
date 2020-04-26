from googleapiclient.discovery import build
from oauth2client import file
from oauth2client.service_account import ServiceAccountCredentials


def get_comments(column,service,_id):
    comment_list=service.spreadsheets().values().get(spreadsheetId=_id, range='AskReddit!'+column+'2:'+column).execute().get(
    'values', [])
    
    split_out=[i[0].split('^^^^^^^^^^^^^^^^^^^^^^^^^^') for i in comment_list]

    
    cleaned_comment_list=[i[0] for i in split_out]
    users=[i[1] for i in split_out]
    age_list=[i[2] for i in split_out]
    age_type_list=[i[3] for i in split_out]
    updoots=[i[4] for i in split_out]
    thread_title=split_out[0][5]
    op=split_out[0][6]


    return cleaned_comment_list,users,age_list,age_type_list,updoots,thread_title,op
