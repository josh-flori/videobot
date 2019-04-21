import praw
import re
from praw.models import MoreComments
import datetime
from dateutil.relativedelta import relativedelta


def get_comments(url):

    ############################
    # DEFINE REDDIT CONNECTION #
    ############################
    reddit = praw.Reddit(client_id='eZ0qCk4LGFmlvg',
                             client_secret= 'ObVykPZwUf6AtmvQyh-HFIlhn8I',
                             user_agent= 'myApp',
                             username= '',
                             password= '')

    ####################
    #  GET SUBMISSION  #
    ####################
    # submission stores information like comments, authors, title, id, etc
    def get_submission(submission_id,reddit):
        return reddit.submission(id=submission_id)



    ######################
    #  GET COMMENT DATA  #
    ######################
    def get_comment_data(some_submission):
    
        # define now 
        now = datetime.datetime.now(datetime.timezone.utc)
        # initialize lists
        comments=[]
        users=[]
        age_list=[]
        age_type_list=[]
        updoots=[]
    
        # loop through all comment entities
        for top_level_comment in some_submission.comments:
            # skip if error
            if isinstance(top_level_comment, MoreComments) or top_level_comment.author is None:
                continue
            
            # figure out age
            dif=relativedelta(now.replace(tzinfo=None),datetime.datetime.utcfromtimestamp(top_level_comment.created_utc))
        
            # figure out the maximum unit
            found_age=False
            if dif.years>0:
                age=dif.years
                age_type="years"
                found_age=True
            elif dif.months>0:
                age=dif.months
                age_type="months"
                found_age=True
            elif dif.days>0:
                age=dif.days
                age_type="days"
                found_age=True
            # make sure it was found
            assert found_age==True
        

            # start appending
            comments.append(top_level_comment.body)
            users.append(top_level_comment.author.name)
            age_list.append(age)
            age_type_list.append(age_type)
            updoots.append(top_level_comment.score)
    
        assert len(comments)==len(users)==len(age_list)==len(age_type_list)==len(updoots)
    
        return comments,users,age_list,age_type,updoots
        

    
    ####################
    #  CLEAN COMMENTS  #
    ####################
    def clean_comments(comments):
        cleaned_comment_list=[re.sub(r'[^A-Za-z0-9,’.!?()"\':)(]', ' ', comment) for comment in comments]
        return cleaned_comment_list


    ##################
    #  DO THE STUFF  #
    ##################
    reddit_id = url.split("/")[6]

    some_submission = get_submission(reddit_id,reddit)
    comments,users,age_list,age_type_list,updoots=get_comment_data(some_submission)


    cleaned_comment_list = clean_comments(comments)
    
    return cleaned_comment_list,users,age_list,age_type_list,updoots,some_submission.title









