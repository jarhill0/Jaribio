# Jaribio
Python code for /u/Jaribio, the bot who runs /r/Jaribio

## Guide to configuration (may not be complete):

1. set `target_sub` in the script
2. place `UserList.txt` in the directory you plan to run the script from (I run the script from the same directory that I save it in, but you could theoretically run it from somewhere else), and format it as follows:

   ```
   name1
   name2
   name3
   ```

   (list Reddit usernames followed imediately by newlines (no spaces). **Make sure the file ends in a newline**.

3. In the directory you plan to run the script from, create a directory named `Resources`
4. In `Resources`, create the following files (each with no spaces or newlines at the end of the file):
  - `TotalUserLogs.txt` which is an integer that represents the total number of logs *already* posted.
  - `total_re_adds.txt` which is an integer that represents the total number of re-adds *already* performed (0 if none)
5. In the main directory, create a file named `praw.ini` that follows the example format:

    ```
    [Jaribio]
    client_id=Y4PJOclpDQy3xZ
    client_secret=UkGLTe6oqsMk5nHCJTHLrwgvHpr
    password=pni9ubeht4wd50gk
    username=fakebot1
   ```
  - `username` should be the username of the bot
  - `password` should be the password of the bot
  - `client_id` and `client_secret` should be the client id and client secret from the reddit API ([instructions here](https://github.com/reddit/reddit/wiki/OAuth2))


I *think* this should get you up and running, but I'm not positive…

You also need to create a subreddit that your bot is moderator of, with flair css classes for `number`, `numbernew`, and `kicked`