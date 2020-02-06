import tweepy
import requests
import zipfile
import tempfile
import csv
import os
import sys

# add twitter API keys to keys.py in cwd
from keys import *

# twitter keys
consumer_key = CONSUMER_KEY
consumer_secret = CONSUMER_SECRET
access_token = ACCESS_TOKEN
access_token_secret = ACCESS_TOKEN_SECRET

# customize block list
bot_data = {
  'categories[]': 'trollbot',
  'date_pref': '0',
  'daterange': '',
  'zip': '1',
  'access-code': '',
  'download': '1'
}

# botsentinel url
url = 'https://botsentinel.com/blocklist'

# twitter api auth
print("[*] Authenticating to twitter")
try:
  auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(access_token, access_token_secret)
  api = tweepy.API(auth)
except tweepy.TweepError as error:
  print(error.reason.message)
  sys.exit(1)

# get list of accounts already blocked on twitter
print("[*] Getting list of your current blocks from twitter")
try:
  blocks = api.blocks_ids()
  with open('current_blocks.csv', 'w') as f:
    for block in blocks:
      w = csv.writer(f, delimiter=',')
      w.writerow(str(block).split('\n')) 
    f.close()
except tweepy.TweepError as error:
  print(error.reason)
  sys.exit(1)

# get block list from botsentinel.com
print("[*] Getting latest blocklist from botsentinel")
try:
  r = requests.post(url, data=bot_data)
  r.raise_for_status()
except requests.exceptions.HTTPError as err:
  print(err)
  sys.exit(1)
print("[*] Got new zip file from botsentinel")
open('blocklist.zip', 'wb').write(r.content)
print("[*] Saved blocklist.zip")

# extract the zip to temporary dir
with zipfile.ZipFile("blocklist.zip","r") as zip_ref:
  with tempfile.TemporaryDirectory() as directory:
    zip_ref.extractall(directory)
    print("[*] Extracted blocklist.zip to temporary directory: "+directory)

    # iterate through each row of each list
    print("[*] Updating twitter blocklist...this will take a long time")
    for file in os.scandir(directory):
      if (file.path.endswith(".csv") and file.is_file()):
        old = open('current_blocks.csv', 'r')
        with open(file) as new:
          fresh = set(new) - set(old)
          if not fresh:
            print("[*] No changes in this file; moving to the next file")
          for line in fresh:
            try:
              try:
                user = api.get_user(line)
              except tweepy.TweepError as error:
                print(error.reason)
              print("[*] Blocking "+user.screen_name)
              api.create_block(line)
            except tweepy.TweepError as error:
              print(error.reason)
        f.close()
    print("[*] Twitter blocklist successfully updated.")

# clean up zip file
print("[*] Cleaning up")
try:
    os.remove("blocklist.zip")
except OSError:
    print ("[*] Deletion of blocklist.zip file failed")
else:
    print ("[*] Successfully deleted blocklist.zip file")

# done
print("[*] Done!")
sys.exit(0)