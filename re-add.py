import os
import praw
import prawcore
from update_sidebar import update_sidebar


def is_user_deleted(new_user_var):
    try:
        reddit.redditor(name=new_user_var).fullname
    except prawcore.exceptions.NotFound:
        return True
    else:
        return False


# opens, reads, and returns a resource
def read_resource(resource_filename):
    return open(os.path.abspath(os.path.join('Resources',
                                             resource_filename))).read()


target_sub = 'Jaribio'

# log in to Reddit
reddit = praw.Reddit('Jaribio',
                     user_agent='Private Sub Manager', )


def again():
    choice = input('Re-add another user? [y/n] ').lower()
    if choice in ['y', 'yes']:
        return True
    else:
        return False


def re_add():
    user_list = list(map(str.strip, open(os.path.abspath('UserList.txt')).read().split('\n')))
    total_re_adds = int(read_resource('total_re_adds.txt').strip())
    if user_list[-1] == '':
        del user_list[-1]
    re_add_user = input('User re-adder for /r/%s:\nUsername to re-add? ' % target_sub)
    if is_user_deleted(re_add_user):
        print('Not a valid username.')
        if again():
            re_add()
    else:
        reddit.subreddit(target_sub).flair.set(  # commentOutToTest
            redditor=re_add_user,
            text='#%d' % (len(user_list) + 1),
            css_class='number')
        reddit.subreddit(target_sub).contributor.add(
            re_add_user)  # commentOutToTest
        new_post = reddit.subreddit(target_sub).submit(  # commentOutToTest
            'User re-add #%s' % str(total_re_adds + 1),
            selftext='\\#%s — /u/%s' % (str(len(user_list) + 1), re_add_user),
            resubmit=False)
        with open('UserList.txt', 'a+') as f:
            f.write(re_add_user + '\n')
        with open('Resources/total_re_adds.txt', 'w+') as f:
            f.write(str(total_re_adds + 1))
        update_sidebar(target_sub)
        reddit.submission(id=new_post.id).mod.distinguish(how='yes', sticky=False)
        if again():
            re_add()


re_add()
