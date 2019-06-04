# /users/josh.flori/desktop/test/bin/python3 /users/josh.flori/desktop/test/lib/python3.6/site-packages/videobot/R_ask_reddit_main.py

from videobot import get_audio
from videobot import get_comments_from_sheet
from videobot import get_chunks_comments
from videobot import create_frames
from videobot import create_joined_audio
from videobot import create_video
from videobot import create_title_slide
from videobot import get_chunks_title
from videobot import initialize_folder
from videobot import concat_videos
from googleapiclient.discovery import build
from oauth2client import file
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
import os
from string import ascii_lowercase
import os
import shutil

        
        

SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
store = file.Storage('credentials.json')
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    '/users/josh.flori/drive_backup/drive_backup/python_scripts/client_secret.json', scope)
service = build('sheets', 'v4', http=creds.authorize(Http()))                
_id='1sIS1r-vtHNVRll_NR3vMr8Pbdt91B34vRrvAe20Ym9g'
threads = service.spreadsheets().values().get(spreadsheetId=_id, range='AskReddit!A2:A').execute().get(
    'values', [])



        
# loop through all threads
col=1
for i in range(len(threads)):
    column=ascii_lowercase[col]
    col+=1
    
    
    directory='/users/josh.flori/desktop/demo'+str(column)
    
    initialize_folder.initialize_folder(directory,'first')



    ######################
    # CREATE TITLE VIDEO #
    ######################

    # get comment data
    cleaned_comment_list,users,age_list,age_type_list,updoots,thread_title,op = get_comments_from_sheet.get_comments(column,service,_id)

    # get TITLE audio
    get_audio.get_audio(thread_title,'/thread_title.mp3','thread_title.wav',directory)

    parameters,num_lines = get_chunks_title.get_chunks(thread_title,'/thread_title.mp3',.5,directory)

    # create TITLE slide (video)
    create_title_slide.create_title_slide(parameters,num_lines,'/thread_title.mp3',thread_title,op,age_list[0],age_type_list[0],directory)






    #########################
    # CREATE COMMENT VIDEOS #
    #########################

    for i in range(len(users))[0:3]:
    
        print(len(cleaned_comment_list[i]))
    
        # get COMMENT audio
        if not len(cleaned_comment_list[i]) >1500 and 'http' not in cleaned_comment_list[i]:    
        
        
            get_audio.get_audio(cleaned_comment_list[i],'/single_comment'+str(i)+'.mp3','/single_comment'+str(i)+'.wav',directory)


            # get COMMENT chunk information
            parameters,num_lines,exceeds_limit = get_chunks_comments.get_chunks(cleaned_comment_list[i],'/single_comment'+str(i)+'.mp3',.5,directory)
            print(exceeds_limit)

            # if the text is not too long...
            if not exceeds_limit:

                # get COMMENT frames
                image_paths = create_frames.create_frames(parameters,num_lines,exceeds_limit,users[i],age_list[i],age_type_list[i],updoots[i],i,directory)

                # create COMMENT video
                create_video.create_video(image_paths,parameters,'/single_comment'+str(i)+'.mp3',i,directory)




    #################
    # CONCAT VIDEOS #
    #################

    concat_videos.concat_videos(directory)
    initialize_folder.initialize_folder(directory,'second')