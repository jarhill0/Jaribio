import shutil
import os
import time
import prawcore
import praw

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


# load sensitive data (and total user log number)
password = read_resource('password.txt')
client_id = read_resource('client_id.txt')
client_secret = read_resource('client_secret.txt')
username = read_resource('username.txt')
total_user_logs = int(read_resource('TotalUserLogs.txt'))

# log in to Reddit
reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent='Private Sub Manager',
    username=username,
    password=password)


# function sets a flair to test if a user exists or not
def is_user_deleted(user):
    try:
        reddit.redditor(user).fullname
    except prawcore.excpetions.NotFound:
        return True
    else:
        return False


shutil.copyfile(
    os.path.abspath("UserList.txt"),
    os.path.abspath("UserList %s.txt" % time_string))

user_list = map(str.strip, read_resource("user_list").split("\n"))

# find which users posted and commented
participated = {
    submission.author.strip()
    for submission in reddit.subreddit(target_sub).submissions(week_ago, now)
}
to_remove = set()
old_comments = False
for comment in reddit.subreddit(target_sub).comments(limit=600):
    if comment.created_utc > week_ago:
        participated.add(comment.author.strip())
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
to_remove = set(filter(lambda x: is_user_deleted(user) or x not in participated, user_list))

# attempt to flair and remove NotParticipated users
for user in to_remove:
    try:
        reddit.subreddit(target_sub).flair.set(
            redditor=user,  # commentOutToTest
            text='Removed',
            css_class='kicked')
        print('Flaired %s' % user)
        reddit.subreddit(target_sub).contributor.remove(
            user.strip())  # commentOutToTest
        print('Removed %s' % user)
    except prawcore.excpetions.BadRequest:
        print(
            'Removed user %s does not exist. Everything should proceed as planned.'
            % user.strip())
    else:
        print('Flaired %s as removed.' % user.strip())

# log kicked users
with open(os.path.abspath('Removed %s.txt' % time_string, 'w+') as f:
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
            reddit.subreddit(target_sub).flair.set(
                redditor=user.strip(),  # commentOutToTest
                text='#1',
                css_class='goldnumber')
            print("Flaired %s." % user)
        elif i == 1:
            reddit.subreddit(target_sub).flair.set(
                redditor=user.strip(),  # commentOutToTest
                text='#2',
                css_class='silver')
            print("Flaired %s." % user)
        elif i == 2:
            reddit.subreddit(target_sub).flair.set(
                redditor=user.strip(),  # commentOutToTest
                text='#3',
                css_class='bronze')
            print("Flaired %s." % user)
        else:
            reddit.subreddit(target_sub).flair.set(
                redditor=user.strip(),  # commentOutToTest
                text='#%d' % (i + 1),
                css_class='number')
            print("Flaired %s." % user)


flair_existing_users()

# Determine how many users must be added, create a file named after the time, and get that many users and save to file
num_to_add = max(min(len(to_remove), 25), 10)

# get 30 comments and put their authors in RawNewComments
raw_new_comments = []
for comment in reddit.subreddit('all').comments(limit=30):
    raw_new_comments.append(comment.author.name)

# open a file; add users from raw_new_comments if we still need users and they are not already in user_list
with open('New users %s.txt' % time_string, 'w+') as f:
    n = 0
    for user in raw_new_comments:
        if n < num_to_add and not user_list.__contains__(user.strip()):
            # open the new user file and read it line by line
            f.write(str(user.strip()) + '\n')
            n += 1

new_users = open('New users %s.txt' % time_string, 'r').readlines()
for i, user in enumerate(new_users):
    new_users[i] = user.strip()

num_old_users = len(user_list)
# add the new users to selftext, then post it.
selftext += '\n#Users added\n\n'
for i, user in enumerate(new_users):
    selftext += ('\\#%s - /u/%s  \n' %
                 (str(num_old_users + i + 1), user.strip()))
reddit.subreddit(target_sub).submit(  # commentOutToTest the submit block
    'Jaribio user log #%s' % str(total_user_logs + 1),
    selftext=selftext,
    resubmit=False)
print("Submitted")
print(selftext)
# sticky it
for submission in reddit.redditor(name=username).submissions.new(
        limit=1):  # commentOutToTest this and the following
    new_post = submission.id
reddit.submission(id=new_post).mod.distinguish(how='yes', sticky=True)
print("Distinguished")
reddit.submission(id=new_post).mod.sticky()
print("Stickied")
# after posting, increment the total number of user logs
with open('Resources/TotalUserLogs.txt', 'w+') as f:
    f.write(str(total_user_logs + 1))

# for each new user in the file, add then as approved submitters and flair them.
for i, user in enumerate(new_users):
    reddit.subreddit(target_sub).flair.set(
        redditor=user.strip(),  # commentOutToTest
        text='#%d' % (num_old_users + i + 1),
        css_class='numbernew')
    print('Flaired ' + user.strip() + ' as new.')
    reddit.subreddit(target_sub).contributor.add(
        user.strip())  # commentOutToTest
    print('Removed %s.' % user)

# rewrite UserList.txt with all removed users gone
with open('UserList.txt', 'w+') as f:
    for user in user_list:
        f.write(user.strip() + '\n')
# open UserList.txt and add the new users to it
with open('UserList.txt', 'a+') as f:
    for user in new_users:
        f.write(user.strip() + '\n')
