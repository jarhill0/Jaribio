import praw
import os


def read_resource(resource_filename):
    return open(os.path.abspath(os.path.join('Resources',
                                             resource_filename))).read()


target_sub = 'Jaribio'

# load sensitive data (and total user log number)
password = read_resource('password.txt')
client_id = read_resource('client_id.txt')
client_secret = read_resource('client_secret.txt')
username = read_resource('username.txt')

# log in to Reddit
reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent='Private Sub Manager',
    username=username,
    password=password)


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
