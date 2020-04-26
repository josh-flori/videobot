import praw, requests


# TODO - if 'mods' in text, ignore that image entirely.

def connect_to_reddit():
    """ Returns credentialled connection to reddit api. """
    reddit_conn = praw.Reddit(client_id='eZ0qCk4LGFmlvg',
                              client_secret='ObVykPZwUf6AtmvQyh-HFIlhn8I',
                              user_agent='myApp',
                              username='',
                              password='')
    return reddit_conn


def get_image_data(output_path, subreddit, time_limit, limit, reddit_conn):
    """ Returns top n images from specified sub to specified path. """
    submissions = reddit_conn.subreddit(subreddit).top(time_limit, limit=limit)
    i = 0
    for s in submissions:
        r = requests.get(s.url, allow_redirects=True)
        if ".gif" not in s.url:
            open(output_path + str(i) + '.jpg', 'wb').write(r.content)
            i += 1


def get_images(output_path, subreddit, time_limit, limit):
    reddit_conn = connect_to_reddit()
    get_image_data(output_path, subreddit, time_limit, limit, reddit_conn)
