import praw
import requests


def get_images(subreddit):

    ############################
    # DEFINE REDDIT CONNECTION #
    ############################
    reddit = praw.Reddit(client_id='eZ0qCk4LGFmlvg',
                             client_secret= 'ObVykPZwUf6AtmvQyh-HFIlhn8I',
                             user_agent= 'myApp',
                             username= '',
                             password= '')

    ##################
    #  DO THE STUFF  #
    ##################
submissions = reddit.subreddit('BlackPeopleTwitter').hot(limit=15)
    
i=0
for submission in submissions:
    print(submission.url)
    url = submission.url
    r = requests.get(url, allow_redirects=True)
    open('/users/josh.flori/desktop/'+str(i)+'.jpg', 'wb').write(r.content)
    i+=1

    












