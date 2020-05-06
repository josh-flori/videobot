import praw, requests
from memes import config


def connect_to_reddit():
    """ Returns credentialled connection to reddit api. """
    reddit_conn = praw.Reddit(client_id=config.reddit_client_id,
                              client_secret=config.reddit_client_secret,
                              user_agent='myApp')
    return reddit_conn


def get_image_data(output_path, subreddit, time_limit, limit, reddit_conn):
    """ Returns top n images from specified subreddit to specified output path. """
    submissions = reddit_conn.subreddit(subreddit).top(time_limit, limit=limit)
    i = 0
    for s in submissions:
        r = requests.get(s.url, allow_redirects=True)
        if ".gif" not in s.url:
            open(output_path + str(i) + '.jpg', 'wb').write(r.content)
            i += 1


def get_images(output_path, subreddit, time_limit, limit):
    """ A higher level function which creates credentialled connection to reddit and proceeds to pull images. In other
     words, it combines connect_to_reddit() and get_image_data(). """
    reddit_conn = connect_to_reddit()
    get_image_data(output_path, subreddit, time_limit, limit, reddit_conn)
