import shutil
import os
import time
import prawcore
import praw
from config import testing, target_sub, style
import post_gist
from update_sidebar import update_sidebar

# Configuration double-check
print('Target sub is %s.' % target_sub)
print('Testing mode.' if testing else 'Real mode.')
print('Style is %s.' % style)

# set a time string for file saving and access; find now and a week ago in seconds since epoch
local_time = time.localtime()
time_string = time.strftime('%Y-%m-%d', local_time)
now = time.time()
week_ago = now - 604800

# define selftext
if style == 'Redefinition':
    selftext = 'Kicked users:\n\n'
elif style == 'Jaribio':
    selftext = '#Users removed\n\n'


# opens, reads, and returns a resource
def read_resource(resource_filename):
    return open(os.path.abspath(os.path.join('Resources',
                                             resource_filename))).read()


# load total user log number
total_user_logs = int(read_resource('TotalUserLogs.txt'))

# log in to Reddit
reddit = praw.Reddit(target_sub, user_agent='Private Sub Manager')


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
    if style == 'Redefinition':
        selftext += ('- \\#%s /u/%s  \n' % (str((user_list.index(user)) + 1), user.strip()))
    elif style == 'Jaribio':
        selftext += ('\\#%s - /u/%s  \n' % (str((user_list.index(user)) + 1), user.strip()))

# remove users, THE RIGHT WAY, without skipping over some of them randomly
user_list_copy = user_list[:]
for user in user_list_copy:
    if to_remove.__contains__(user.strip()):
        user_list.remove(user.strip())


# flair existing users with green flair or special flair class
def flair_existing_users():
    for i, user in enumerate(user_list):
        if not testing:

            if style == 'Redefinition':
                reddit.subreddit(target_sub).flair.set(
                    redditor=user.strip(),
                    text='#%d' % (i + 1),
                    css_class='number')

            elif style == 'Jaribio':
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
if style == 'Jaribio':
    raw_new_comment_urls = []
for comment in reddit.subreddit('all').comments(limit=40):
    raw_new_comment_authors.append(comment.author.name)
    if style == 'Jaribio':
        raw_new_comment_urls.append('https://reddit.com' + comment.permalink(fast=True))

# open a file; add users from raw_new_comments if we still need users and they are not already in user_list
if style == 'Jaribio':
    comments_for_entry = []
with open('New users %s.txt' % time_string, 'w+') as f:
    n = 0
    for i, user in enumerate(raw_new_comment_authors):
        if n < num_to_add and not user_list.__contains__(user.strip()):
            # open the new user file and read it line by line
            f.write(str(user.strip()) + '\n')
            if style == 'Jaribio':
                comments_for_entry.append(raw_new_comment_urls[i])
            n += 1

new_users = open('New users %s.txt' % time_string, 'r').readlines()
for i, user in enumerate(new_users):
    new_users[i] = user.strip()
if new_users[-1] == '':
    del new_users[-1]

if style == 'Jaribio':
    gist_body = '#Comments for entry on %s\n\n' % time_string
    for i, user in enumerate(new_users):
        gist_body += '%s : %s  \n' % (user, comments_for_entry[i])
    gist_url = post_gist.make_gist(gist_body, time_string)

num_old_users = len(user_list)
# add the new users to selftext, then post it.
if style == 'Redefinition':
    selftext += '\nAdded users:\n\n'
elif style == 'Jaribio':
    selftext += '\n#Users added\n\n[Comments for entry](%s)\n\n' % gist_url
for i, user in enumerate(new_users):
    if style == 'Redefinition':
        selftext += ('- \\#%s /u/%s  \n' % (str(num_old_users + i + 1), user.strip()))
    elif style == 'Jaribio':
        selftext += ('\\#%s - /u/%s  \n' % (str(num_old_users + i + 1), user.strip()))

# add stats section and a link to the source code at the bottom of the post
if style == 'Redefinition':
    num_users_change = ''
    if len(new_users) - len(to_remove) >= 0:
        num_users_change = '+%s' % str(len(new_users) - len(to_remove))
    else:
        num_users_change = str(len(new_users) - len(to_remove))
    selftext += ('\nInfo:\n\n- %s users kicked\n- %s users added\n- Membercap: %s (%s)' % (
        str(len(to_remove)), str(len(new_users)), str(len(user_list) + len(new_users)), num_users_change))

if not testing:
    if style == 'Redefinition':
        new_post = reddit.subreddit(target_sub).submit(
            time_string + ' - Bot Recap',
            selftext=selftext,
            resubmit=False)
    elif style == 'Jaribio':
        new_post = reddit.subreddit(target_sub).submit(
            'Jaribio user log #%s' % str(total_user_logs + 1),
            selftext=selftext,
            resubmit=False)
print('Submitted')
print(selftext)
# distinguish/sticky it
if not testing:
    reddit.submission(id=new_post.id).mod.distinguish(how='yes', sticky=True)
print('Distinguished')
if style == 'Jaribio':
    reddit.submission(id=new_post.id).mod.sticky()
    print('Stickied')

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

# must be called after writing out UserList.txt, because it pulls the user list from there.
if style == 'Jaribio' and not testing:
    update_sidebar(target_sub)

