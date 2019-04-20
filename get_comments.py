import praw
import re


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
    
    
        
    ####################
    #  CLEAN COMMENTS  #
    ####################
    def clean_comments(comment_list):
        cleaned_comment_list=[re.sub(r'[^A-Za-z0-9.!?()]', ' ', comment) for comment in comment_list]
        return cleaned_comment_list
    



    reddit_id = url.split("/")[6]

    some_submission = get_submission(reddit_id,reddit)

    top_level_authors, top_level_bodies, top_level_permalinks, lower_level_authors, lower_level_bodies=get_raw_comments(some_submission)


    cleaned_comment_list = clean_comments(top_level_bodies)
    return cleaned_comment_list









