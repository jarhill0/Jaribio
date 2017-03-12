import shutil
import os
import time
import prawcore
import praw
import post_gist
from update_sidebar import update_sidebar

# Configuration
target_sub = 'Jaribio'
# set a time string for file saving and access; find now and a week ago in seconds since epoch
local_time = time.localtime()
time_string = time.strftime('%Y-%m-%d', local_time)
now = time.time()
week_ago = now - 604800
# define selftext
selftext = '#Users removed\n\n'


# opens, reads, and returns a resource
def read_resource(resource_filename):
    return open(os.path.abspath(os.path.join('Resources',
                                             resource_filename))).read()


# load total user log number
total_user_logs = int(read_resource('TotalUserLogs.txt'))

# log in to Reddit
reddit = praw.Reddit('Jaribio',
                     user_agent='Private Sub Manager', )


# function gets a user's fullname to test if a user exists or not
def is_user_deleted(new_user_var):
    try:
        reddit.redditor(name=new_user_var).fullname
    except prawcore.exceptions.NotFound:
        return True
    else:
        return False


shutil.copyfile(
    os.path.abspath('UserList.txt'),
    os.path.abspath('UserList %s.txt' % time_string))

user_list = list(map(str.strip, open(os.path.abspath('UserList.txt')).read().split('\n')))
if user_list[-1] == '':
    del user_list[-1]

# find which users posted and commented
participated = {
    submission.author.name.strip()
    for submission in reddit.subreddit(target_sub).submissions(start=week_ago, end=now)
    }

old_comments = False
for comment in reddit.subreddit(target_sub).comments(limit=600):
    if comment.created_utc > week_ago:
        try:
            participated.add(comment.author.name.strip())
        except AttributeError:
            print('Bot detected a comment from a deleted user. Skipping over.')
    else:
        old_comments = True
if not old_comments:
    print(
        'Not all comments from the past week have been retrieved. Exiting. Raise number of comments fetched.'
    )
    with open('Bot failed at %s.txt' % time_string, 'w+') as f:
        f.write(
            'The bot failed due to not retrieving all comments from the past week. Up the limit in line 48 and retry.'
        )
    exit()

# Add all non-participators to a list
to_remove = list(filter(lambda x: is_user_deleted(x) or x not in participated, user_list))

# attempt to flair and remove NotParticipated users
for user in to_remove:
    try:
        reddit.subreddit(target_sub).flair.set(  # commentOutToTest
            redditor=user,
            text='Removed',
            css_class='kicked')
        print('Flaired %s.' % user)
        reddit.subreddit(target_sub).contributor.remove(  # commentOutToTest
            user.strip())
        print('Removed %s' % user)
    except prawcore.exceptions.BadRequest:
        print(
            'Removed user %s does not exist. Everything should proceed as planned.'
            % user.strip())
    else:
        print('Flaired and removed %s.' % user.strip())

# log kicked users
with open(os.path.abspath('Removed %s.txt' % time_string), 'w+') as f:
    for user in to_remove:
        f.write(user.strip() + '\n')
# update selftext with kicked users and their numbers *before* they are removed from the user list.
for user in to_remove:
    selftext += ('\\#%s - /u/%s  \n' %
                 (str((user_list.index(user)) + 1), user.strip()))
# remove users, THE RIGHT WAY, without skipping over some of them randomly
user_list_copy = user_list[:]
for user in user_list_copy:
    if to_remove.__contains__(user.strip()):
        user_list.remove(user.strip())


# flair existing users with green flair or special flair class
def flair_existing_users():
    for i, user in enumerate(user_list):
        if i == 0:
            reddit.subreddit(target_sub).flair.set(  # commentOutToTest
                redditor=user.strip(),
                text='#1',
                css_class='goldnumber')
            print('Flaired %s.' % user)
        elif i == 1:
            reddit.subreddit(target_sub).flair.set(  # commentOutToTest
                redditor=user.strip(),
                text='#2',
                css_class='silver')
            print('Flaired %s.' % user)
        elif i == 2:
            reddit.subreddit(target_sub).flair.set(  # commentOutToTest
                redditor=user.strip(),
                text='#3',
                css_class='bronze')
            print('Flaired %s.' % user)
        else:
            reddit.subreddit(target_sub).flair.set(  # commentOutToTest
                redditor=user.strip(),
                text='#%d' % (i + 1),
                css_class='number')
            print('Flaired %s.' % user)


flair_existing_users()

# Determine how many users must be added, create a file named after the time, and get that many users and save to file
num_to_add = max(min(len(to_remove), 25), 10)

# get 30 comments and put their authors in RawNewComments
raw_new_comment_authors = []
raw_new_comment_urls = []
for comment in reddit.subreddit('all').comments(limit=40):
    raw_new_comment_authors.append(comment.author.name)
    raw_new_comment_urls.append('https://reddit.com' + comment.permalink(fast=True))

# open a file; add users from raw_new_comments if we still need users and they are not already in user_list
comments_for_entry = []
with open('New users %s.txt' % time_string, 'w+') as f:
    n = 0
    for i, user in enumerate(raw_new_comment_authors):
        if n < num_to_add and not user_list.__contains__(user.strip()):
            # open the new user file and read it line by line
            f.write(str(user.strip()) + '\n')
            comments_for_entry.append(raw_new_comment_urls[i])
            n += 1

new_users = open('New users %s.txt' % time_string, 'r').readlines()
for i, user in enumerate(new_users):
    new_users[i] = user.strip()
if new_users[-1] == '':
    del new_users[-1]

gist_body = '#Comments for entry on %s\n\n' % time_string
for i, user in enumerate(new_users):
    gist_body += '%s: %s  \n' % (user, comments_for_entry[i])
gist_url = post_gist.make_gist(gist_body, time_string)

num_old_users = len(user_list)
# add the new users to selftext, then post it.
selftext += '\n#Users added\n\n[Comments for entry](%s)\n\n' % gist_url
for i, user in enumerate(new_users):
    selftext += ('\\#%s - /u/%s  \n' %
                 (str(num_old_users + i + 1), user.strip()))
new_post = reddit.subreddit(target_sub).submit(  # commentOutToTest
    'Jaribio user log #%s' % str(total_user_logs + 1),
    selftext=selftext,
    resubmit=False)
print('Submitted')
print(selftext)
# sticky it
reddit.submission(id=new_post.id).mod.distinguish(how='yes', sticky=True)  # commentOutToTest
print('Distinguished')
reddit.submission(id=new_post.id).mod.sticky()  # commentOutToTest
print('Stickied')
# after posting, increment the total number of user logs
with open('Resources/TotalUserLogs.txt', 'w+') as f:
    f.write(str(total_user_logs + 1))

# for each new user in the file, add then as approved submitters and flair them.
for i, user in enumerate(new_users):
    reddit.subreddit(target_sub).flair.set(  # commentOutToTest
        redditor=user.strip(),
        text='#%d' % (num_old_users + i + 1),
        css_class='numbernew')
    print('Flaired ' + user.strip() + ' as new.')
    reddit.subreddit(target_sub).contributor.add(  # commentOutToTest
        user.strip())
    print('Added %s.' % user)

# rewrite UserList.txt with all removed users gone
with open('UserList.txt', 'w+') as f:
    for user in user_list:
        f.write(user.strip() + '\n')
# open UserList.txt and add the new users to it
with open('UserList.txt', 'a+') as f:
    for user in new_users:
        f.write(user.strip() + '\n')

# must be called after writing out UserList.txt, because it pulls the user list from there.
update_sidebar(target_sub)  # commentOutToTest
