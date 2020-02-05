import tweepy
import requests
import zipfile
import tempfile
import csv
import os
import sys

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
  print(error.reason)

print("[*] Getting latest blocklist")

# get block list
try:
  r = requests.post(url, data=bot_data)
  r.raise_for_status()
except requests.exceptions.HTTPError as err:
  print(err)
  sys.exit(1)
print("[*] Got new zip file from botsentinel")
open('blocklist.zip', 'wb').write(r.content)
print("[*] Saved new zip file")

# extract the zip to temporary dir
with zipfile.ZipFile("blocklist.zip","r") as zip_ref:
  with tempfile.TemporaryDirectory() as directory:
    zip_ref.extractall(directory)
    print("[*] Extracted new zip file to temporary directory: "+directory)

    # iterate through each row of each list
    print("[*] Updating twitter blocklist")
    for file in os.scandir(directory):
      if (file.path.endswith(".csv") and file.is_file()):
        for line in open(file):
          try:
            api.create_block(line)
          except tweepy.TweepError as error:
            print(error.reason)

    print("[*] Twitter blocklist successfully updated.")

print("[*] Cleaning up")
# clean up zip file
try:
    os.remove("blocklist.zip")
except OSError:
    print ("[*] Deletion of blocklist.zip file failed")
else:
    print ("[*] Successfully deleted blocklist.zip file")

# done
print("[*] Done!")