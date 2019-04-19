# /users/josh.flori/desktop/test/bin/python3 /users/josh.flori/documents/josh-flori/video-creator/test.py --url="https://www.reddit.com/r/dataisbeautiful/comments/beq4up/how_reliable_is_that_article_you_just_read_media"

#####################
# IMPORT SOME STUFF #
#####################
import praw
import time
from nltk.tokenize import word_tokenize
import nltk
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from oauth2client.service_account import ServiceAccountCredentials
import collections
import numpy as np
import tqdm
import time
from googleapiclient.errors import HttpError
import operator
sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
from nltk.tokenize import SpaceTokenizer
import operator
import sys
import argparse




########################################
# CREATE ARGUMENT PARSER FOR INPUT URL #
########################################
parser = argparse.ArgumentParser(description='Input Reddit URL')
parser.add_argument('--url')




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



##############################
#  GET COMMENTS AND REPLIES  #
##############################

""" This function will process every comment for a given submission.
    It returns an 1) author list and 2) a corresponding body text (comment) list for each top-level comment 
        (top level comment means it's an original comment to the OP as opposed to a nested reply to someone elses comment).
    It will also return the 3) author list and 4) corresponding body text list for each lower-level comment (reply).
    Later functions will then loop over every top-level author and find matches in lower-level comments in order to return the entire tree for each author"""

# i haven't figured out a good way to actually work with this data because this comment queue just returns everything in a difficult-to-understand format.
# praw also returns a list of comments which is easier to understand but i cannot figure out how to get any comments deeper than 2nd layer. so we are creating our own
# gosh darn lists. we are not going to worry about the structure. we only need to search for the authors in sub-first level comments (replies)

# comment_queue loops through EVERY comment (to my knowledge.) it returns all 1st level comments, then all 2nd level comments, then all 3rd and so-on.  There is no delineation. 
# how does "pop" work? so if you have 5 comments via: submission.comments[0:5], pop(0) will return all 5, pop(1) will return 4, dropping off the first then moving downward. 

# took like 45 seconds to hit 2,500 comments. times may vary. any thread over 10k comments is gonna take a while. I think the highest comment thread ive seen is like 25k comments and it took maybe 35 minutes.

def get_raw_comments(some_submission):
    # define our lists
    top_level_authors=[]
    top_level_bodies=[]
    top_level_permalinks=[]
    lower_level_authors=[]
    lower_level_bodies=[]
    some_submission.comments.replace_more(limit=None) # id what this does, something about flattening the comments, idk
    # get top level only
    comment_queue = some_submission.comments[:]
    while comment_queue:
        comment = comment_queue.pop(0)
        # the purpose of this next part is to remove bulleted lists, which are not stories and not something we want.
        first_characters = "".join([i.lstrip()[0] for i in comment.body.split("\n") if len(i.lstrip())!=0])
        # if the occurance of lines that start with a bulleted item is greater than 4, then we assume it to be a list and skip it.
        if first_characters.count("*") < 4 and first_characters.count("-") < 4 and first_characters.count(">") < 4 and first_characters.count("+") < 4 and "123" not in first_characters:
            top_level_authors.append(comment.author)
            top_level_bodies.append(comment.body)
            top_level_permalinks.append(comment.permalink)
    # reset and loop through all comments, not just top level....
    comment_queue = some_submission.comments[:]
    while comment_queue:
        comment = comment_queue.pop(0)
        lower_level_authors.append(comment.author)
        lower_level_bodies.append(comment.body)
        # now this loops through all of the replies to the top level comments
        comment_queue.extend(comment.replies)
    # remove top level comments so we just have lower level. AMAZING CODING AMIR?
    lower_level_authors=lower_level_authors[len(top_level_authors):]
    lower_level_bodies=lower_level_bodies[len(top_level_bodies):]
    return top_level_authors, top_level_bodies, top_level_permalinks, lower_level_authors, lower_level_bodies
    
    
        
    
    
    
#######################################################
#  GET THE SET OF ALL COMMENTS FOR ALL GIVEN AUTHORS  #
#######################################################


# """ returns dictionary of form: author: [[top level comment(s) + all lower level comments from same author, regardless of whether they correspond to top level comments],[top level permalinks],[length of top comment per author, length of top comment+lower level comments per author]]
#    comments are automatically returned by 'best' desc """

def get_comment_dict(top_level_authors, top_level_bodies, top_level_permalinks, lower_level_authors, lower_level_bodies):
    comment_dict={}
    for author in top_level_authors:
        # for each author we return an index of their comments, top level and lower level. they may have multiple top level
        top=[top_level_bodies[i] for i in range(0,len(top_level_bodies)) if top_level_authors[i] == author][0] # arbitrarily just return the first comment. they may have several, but this is rare and i don't want to deal with the complexity of it and will just assume the top rated comment (the first one to appear in the list) is going to be the one we are looking for and the others are not important.
        link=[top_level_permalinks[i] for i in range(0,len(top_level_bodies)) if top_level_authors[i] == author]
        lower_level_bodies_if_any=[lower_level_bodies[i] for i in range(0,len(lower_level_bodies))  if lower_level_authors[i] == author]
        # append all lower level bodies into the top level body, with visual separation. We will paste the entire output into a google sheet cell
        top_plus_lower=top
        if len(lower_level_bodies_if_any)>0:         
            for body in lower_level_bodies_if_any:
                top_plus_lower=top_plus_lower+"\n\n------------------------------\n\n"+str(body)
        else:
            top_plus_lower=top
        # the primary determinate of whether a comment will be good is the length of the top level comment. so we log that information and will use when outputing useable comments for the content team.
        char_length_of_first_comment=len(top)
      #  print(top+"\n\n"+word_tokenize(top)[0]+"\n"+str(len(word_tokenize(top)))+"\n\n\n---------------------\n\n\n")
        word_length_of_first_comment=len(SpaceTokenizer().tokenize(top))
        # but the length of subcomments also matters, and will be of second priority (do they really tho?)
        length_of_all_comments=len(word_tokenize(top_plus_lower.replace("------------------------------","")))
        comment_dict[str(author)]=[[top_plus_lower],link,[char_length_of_first_comment,word_length_of_first_comment,length_of_all_comments]]
    return comment_dict











######### -----------------------  MAIN ----------------------------- ###########

args = parser.parse_args()
input_url=args.url


reddit_id = input_url.split("/")[6]

some_submission = get_submission(reddit_id,reddit)

top_level_authors, top_level_bodies, top_level_permalinks, lower_level_authors, lower_level_bodies=get_raw_comments(some_submission)

print(top_level_bodies)
#
# if len(top_level_bodies)==0:
#     print("\n\nEither the function or the api failed to return any data for this submission. Look into it. Shutting down now.\n\n")
#     sys.exit()
#
#
# # returns dictionary of author, of form: [[top level comment(s) + all lower level comments from same author, regardless of whether they correspond to top level comments],[top level permalinks],[length of top comment per author, length of top comment+lower level comments per author]]. The lower level comments may not necessarily be children of the parent. they may come from completely unique replies to another redditors comment. subcomments are sorted by level. so all 2nd levels come first. then all third levels, and so on for all levels. for both of these reasons, there will not necessarily be a logical order to them.
# comment_dict = get_comment_dict(top_level_authors, top_level_bodies, top_level_permalinks, lower_level_authors, lower_level_bodies)
#
#
#
#
#
#
#
#
#
#
#
