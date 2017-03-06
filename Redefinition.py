import shutil
import os
import time
import prawcore
import praw

# Configuration
target_sub = 'Redefinition'
testing = False
# set a time string for file saving and access; find now and a week ago in seconds since epoch
local_time = time.localtime()
time_string = time.strftime('%Y-%m-%d', local_time)
now = time.time()
week_ago = now - 604800
# define selftext
selftext = 'Kicked users:\n\n'


# opens, reads, and returns a resource
def read_resource(resource_filename):
    return open(os.path.abspath(os.path.join('Resources',
                                             resource_filename))).read()


# load total user log number
total_user_logs = int(read_resource('TotalUserLogs.txt'))

# log in to Reddit
reddit = praw.Reddit('Redefinition', user_agent='Private Sub Manager')


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
for comment in reddit.subreddit(target_sub).comments(limit=1000):
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
            'The bot failed due to not retrieving all comments from the past week. Up the limit and retry.'
        )
    exit()

# Add all non-participators to a list
to_remove = list(filter(lambda x: is_user_deleted(x) or x not in participated, user_list))

# attempt to flair and remove NotParticipated users
for user in to_remove:
    try:
        if not testing:
            reddit.subreddit(target_sub).flair.set(
                redditor=user,
                text='Removed',
                css_class='kicked')
        print('Flaired %s.' % user)
        if not testing:
            reddit.subreddit(target_sub).contributor.remove(
                user.strip())
        print('Removed %s' % user)
    except prawcore.exceptions.BadRequest:
        print(
            'Removed user %s does not exist. Everything should proceed as planned.' % user.strip())
    else:
        print('Flaired and removed %s.' % user.strip())

# log kicked users
with open(os.path.abspath('Removed %s.txt' % time_string), 'w+') as f:
    for user in to_remove:
        f.write(user.strip() + '\n')
# update selftext with kicked users and their numbers *before* they are removed from the user list.
for user in to_remove:
    selftext += ('- \\#%s /u/%s  \n' % (str((user_list.index(user)) + 1), user.strip()))
# remove users, THE RIGHT WAY, without skipping over some of them randomly
user_list_copy = user_list[:]
for user in user_list_copy:
    if to_remove.__contains__(user.strip()):
        user_list.remove(user.strip())


# flair existing users with green flair or special flair class
def flair_existing_users():
    for i, user in enumerate(user_list):
        if not testing:
            reddit.subreddit(target_sub).flair.set(
                redditor=user.strip(),
                text='#%d' % (i + 1),
                css_class='number')
        print('Flaired %s.' % user)


flair_existing_users()

# Determine how many users must be added, create a file named after the time, and get that many users and save to file
num_to_add = max(min(len(to_remove), 25), 10)

# get 30 comments and put their authors in RawNewComments
raw_new_comment_authors = []
for comment in reddit.subreddit('all').comments(limit=40):
    raw_new_comment_authors.append(comment.author.name)

# open a file; add users from raw_new_comments if we still need users and they are not already in user_list
with open('New users %s.txt' % time_string, 'w+') as f:
    n = 0
    for i, user in enumerate(raw_new_comment_authors):
        if n < num_to_add and not user_list.__contains__(user.strip()):
            # open the new user file and read it line by line
            f.write(str(user.strip()) + '\n')
            n += 1

new_users = open('New users %s.txt' % time_string, 'r').readlines()
for i, user in enumerate(new_users):
    new_users[i] = user.strip()
if new_users[-1] == '':
    del new_users[-1]

num_old_users = len(user_list)
# add the new users to selftext, then post it.
selftext += '\nAdded users:\n\n'
for i, user in enumerate(new_users):
    selftext += ('- \\#%s /u/%s  \n' % (str(num_old_users + i + 1), user.strip()))

# add stats section and a link to the source code at the bottom of the post
num_users_change = ''
if len(new_users) - len(to_remove) >= 0:
    num_users_change = '+%s' % str(len(new_users) - len(to_remove))
else:
    num_users_change = str(len(new_users) - len(to_remove))
selftext += ('\nInfo:\n\n- %s users kicked\n- %s users added\n- Membercap: %s (%s)' % (
    str(len(to_remove)), str(len(new_users)), str(len(user_list) + len(new_users)), num_users_change))

if not testing:
    new_post = reddit.subreddit(target_sub).submit(time_string + ' - Bot Recap', selftext=selftext, resubmit=False)
print('Submitted')
print(selftext)
# distinguish it
if not testing:
    reddit.submission(id=new_post.id).mod.distinguish(how='yes', sticky=True)
print('Distinguished')

# after posting, increment the total number of user logs
with open('Resources/TotalUserLogs.txt', 'w+') as f:
    f.write(str(total_user_logs + 1))

# for each new user in the file, add then as approved submitters and flair them.
for i, user in enumerate(new_users):
    if not testing:
        reddit.subreddit(target_sub).flair.set(
            redditor=user.strip(),
            text='#%d' % (num_old_users + i + 1),
            css_class='numbernew')
    print('Flaired ' + user.strip() + ' as new.')
    if not testing:
        reddit.subreddit(target_sub).contributor.add(user.strip())
    print('Added %s.' % user)

# rewrite UserList.txt with all removed users gone
with open('UserList.txt', 'w+') as f:
    for user in user_list:
        f.write(user.strip() + '\n')
# open UserList.txt and add the new users to it
with open('UserList.txt', 'a+') as f:
    for user in new_users:
        f.write(user.strip() + '\n')
