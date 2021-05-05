#!/usr/bin/env python3

import os
import sys
import json
import time
import dotenv
import tweepy

dotenv.load_dotenv()
e = os.environ.get

auth = tweepy.OAuthHandler(
    e('CONSUMER_KEY'),
    e('CONSUMER_SECRET')
)

auth.set_access_token(
    e('ACCESS_TOKEN'),
    e('ACCESS_TOKEN_SECRET')
)

t = tweepy.API(auth)

def handle_limit(cursor):
    while True:
        try:
            yield next(cursor)
        except tweepy.RateLimitError:
            time.sleep(15 * 60)

def friends(user):
    if not os.path.isfile('friends.json'):
        users = []
        for user in handle_limit(tweepy.Cursor(t.friends, user.id).items()):
            users.append(user._json)
            json.dump(users, open('friends.json', 'w'), indent=2)
    return json.load(open('friends.json'))

def check(user, friend):
    print()
    print(f'{friend["name"]} @{friend["screen_name"]} [{friend["friends_count"]}/{friend["followers_count"]}')
    print(friend['description'])
    print()
    answer = input('Unfollow? [Y/n] ')
    if answer == '' or answer.lower() == 'y':
        t.destroy_friendship(user_id=friend['id'])
        open('last-checked', 'w').write(friend['screen_name'])

def main():
    username = sys.argv[1]
    user = t.get_user(username)
    if os.path.isfile('last-checked'):
        last_checked = open('last-checked').read().strip()
    else:
        last_checked = None
    for friend in friends(user):
        if last_checked and friend['screen_name'] != last_checked:
            print(f"skipping {friend['screen_name']}")
            continue
        last_checked = None
        check(username, friend)

if __name__ == "__main__":
    main()

