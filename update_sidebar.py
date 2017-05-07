import praw
import os

target_sub = 'Jaribio'

# log in to Reddit
reddit = praw.Reddit('Jaribio',
                     user_agent='Private Sub Manager', )


def update_sidebar(target_sub):
    user_list = list(map(str.strip, open(os.path.abspath('UserList.txt')).read().split('\n')))
    if user_list[-1] == '':
        del user_list[-1]

    sidebar_1 = open(os.path.abspath('sidebar part 1.txt')).read()
    sidebar_2 = open(os.path.abspath('sidebar part 2.txt')).read()

    sidebar = sidebar_1

    for i, user in enumerate(user_list):
        sidebar += '%s | /u/%s\n' % (i + 1, user)

    sidebar += sidebar_2

    print(sidebar)
    reddit.subreddit(target_sub).mod.update(description=sidebar)


if __name__ == '__main__':
    update_sidebar(target_sub)
