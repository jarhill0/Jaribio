import praw
import random


def update_title(target_sub):
    reddit = praw.Reddit(target_sub, user_agent='Private Sub Manager', )

    with open('Resources/titles.txt', 'r') as f:
        titles = f.read().split('\n')
    while '' in titles:
        titles.remove('')

    new_title = titles[random.randrange(len(titles))]

    reddit.subreddit(target_sub).mod.update(title=new_title)


if __name__ == '__main__':
    update_title('Jaribio')
