# Jaribio
Python code for /u/Jaribio, the bot who runs /r/Jaribio

## Guide to configuration (may not be complete):

1. set `target_sub` in the script
2. place `UserList.txt` in the directory you plan to run the script from (I run the script from the same directory that I save it in, but you could theoretically run it from somewhere else), and format it as follows:

`name1
name2
name3`

(list Reddit usernames followed imediately by newlines (no spaces). Make sure the file ends in a newline.
3. In the directory you plan to run the script from, create a directory named `Resources`
4. In resources, create the following files (each with no spaces or newlines at the end of the file):
- `username.txt` which contains your bot account's username
- `password.txt` which contains your bot account's password
- `TotalUserLogs.txt` which is an integer that represents the total number of logs *already* posted.
- `client_id.txt` and `client_secret.txt` which contain your client id and client secret from the reddit API ([instructions here](https://github.com/reddit/reddit/wiki/OAuth2))


I *think* this should get you up and running, but I'm not positive…

You of course also need to create a subreddit that your bot is moderator of, with flair css classes for `number`, `numbernew`, and `kicked`