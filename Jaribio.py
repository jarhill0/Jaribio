import praw
import time

# Configuration
TargetSub = "Jaribio"
# set a time string for file saving and access; find now and a week ago in seconds since epoch
localtime = time.localtime()
timestring = time.strftime("%Y-%m-%d %H:%M", localtime)
NowEpoch = time.time()
WeekAgoEpoch = NowEpoch - 604800
# define selftext
selftext = "#Users removed\n\n"

# load sensitive data (and total user log number)
password = open("Resources/password.txt").read()
client_id = open("Resources/client_id.txt").read()
client_secret = open("Resources/client_secret.txt").read()
username = open("Resources/username.txt").read()
TotalUserLogs = int(open("Resources/TotalUserLogs.txt").read())

# log in to Reddit
reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                         user_agent="Private Sub Manager",
                     username=username,
                     password=password)

# function sets a flair to test if a user exists or not
def IsUserDeleted(user):
    try:
        reddit.subreddit("Jaribio2").flair.set(redditor=user.strip(), text="test", css_class="")
    except:
        return True
    else:
        return False

UserList = open("UserList.txt").readlines()
open("UserList " + timestring + ".txt", "w+").writelines(UserList)
for i, user in enumerate(UserList):
    UserList[i] = user.strip()

# find which users posted and commented
Participated = []
NotParticipated = []
Oldcomments = []
for submission in reddit.subreddit(TargetSub).submissions(WeekAgoEpoch, NowEpoch):
    Participated.append(submission.author)
for comment in reddit.subreddit(TargetSub).comments(limit=600):
    if comment.created_utc > WeekAgoEpoch:
        Participated.append(comment.author)
    else:
        Oldcomments.append(comment.author)
for i, user in enumerate(Participated):
    Participated[i] = user.name.strip()
if Oldcomments == []:
    print("Not all comments from the past week have been retrieved. Exiting. Raise number of comments fetched (line 48).")
    with open("Bot failed at " + timestring + ".txt", "w+") as f:
        f.write("the bot failed due to not retrieving all comments from the past week. Up the limit in line 48 and retry.")
    exit()

# Add all non-participators to a list
for user in UserList:
    if IsUserDeleted(user) or not Participated.__contains__(user.strip()):
        NotParticipated.append(user.strip())

# attempt to flair and remove NotParticipated users
for user in NotParticipated:
    try:
        reddit.subreddit(TargetSub).flair.set(redditor=user.strip(), text="Removed", css_class="kicked")
        reddit.subreddit(TargetSub).contributor.remove(user.strip())
    except:
        print("Removed user " + user.strip() + " does not exist. Everything should proceed as planned.")
    else:
        print("Flaired " + user.strip() + " as removed.")

# log kicked users
with open("Removed " + timestring + ".txt", "w+") as f:
    for user in NotParticipated:
        f.write(user.strip() + "\n")
# update selftext with kicked users and their numbers *before* they are removed from the user list.
for user in NotParticipated:
    selftext += ("\\#" + str((UserList.index(user))+1) + " - /u/" + user.strip() + "  \n")
# remove users, THE RIGHT WAY, without skipping over some of them randomly
UserListCopy = UserList[:]
for user in UserListCopy:
    if NotParticipated.__contains__(user.strip()):
        UserList.remove(user.strip())

# flair existing users with green flair or special flair class
for i, user in enumerate(UserList):
    if i == 0:
        reddit.subreddit(TargetSub).flair.set(redditor=user.strip(), text="#1", css_class="goldnumber")
    elif i == 1:
        reddit.subreddit(TargetSub).flair.set(redditor=user.strip(), text="#2", css_class="silver")
    elif i == 2:
        reddit.subreddit(TargetSub).flair.set(redditor=user.strip(), text="#3", css_class="bronze")
    else:
        reddit.subreddit(TargetSub).flair.set(redditor=user.strip(), text="#%d" % (i + 1), css_class="number")
    print("Flaired " + user.strip() + ".")

# Determine how many users must be added, create a file named after the time, and get that many users and save to file
if len(NotParticipated) < 10:
    NumToAdd = 10
elif len(NotParticipated) > 25:
    NumToAdd = 25
else:
    NumToAdd = len(NotParticipated)
# get 30 comments and put their authors in RawNewComments
RawNewComments = []
for comment in reddit.subreddit('all').comments(limit=30):
    RawNewComments.append(comment.author.name)

# open a file; if number of users is less than the number to add, take a user from RawNewComments and put it in the file that becomes NewUsers
with open("New users " + timestring + ".txt", "w+") as f:
    n=0
    for user in RawNewComments:
        if n < NumToAdd:
            if not UserList.__contains__(user.strip()):
                f.write(str(user.strip()) + "\n")
                n += 1

# open the new user file and read it line by line
NewUsers = open("New users " + timestring + ".txt", "r").readlines()
for i, user in enumerate(NewUsers):
    NewUsers[i] = user.strip()

NumOldUsers = len(UserList)
# add the new users to selftext, then post it.
selftext += ("\n#Users added\n\n")
for i, user in enumerate(NewUsers):
    selftext += ("\\#" + str(NumOldUsers + i + 1) + " - /u/" + user.strip() + "  \n")
reddit.subreddit(TargetSub).submit("Jaribio user log #" + str(TotalUserLogs+1), selftext=selftext, resubmit=False)
# sticky it
for submission in reddit.redditor(name=username).submissions.new(limit = 1):
    NewPost = submission.id
reddit.submission(id=NewPost).mod.distinguish(how='yes', sticky=True)
reddit.submission(id=NewPost).mod.sticky()
# after posting, increment the total number of user logs
with open("Resources/TotalUserLogs.txt", "w+") as f:
    f.write(str(TotalUserLogs+1))

# for each new user in the file, add then as approved submitters and flair them.
for i, user in enumerate(NewUsers):
    reddit.subreddit(TargetSub).flair.set(redditor=user.strip(), text="#%d" % (NumOldUsers + i + 1), css_class="numbernew")
    print("Flaired " + user.strip() + " as new.")
    reddit.subreddit(TargetSub).contributor.add(user.strip())

# rewrite UserList.txt with all removed users gone
with open("UserList.txt", "w+") as f:
    for user in UserList:
        f.write(user.strip() + "\n")
# open UserList.txt and add the new users to it
with open("UserList.txt", "a+") as f:
    for user in NewUsers:
        f.write(user.strip() + "\n")