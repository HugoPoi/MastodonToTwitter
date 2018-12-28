#!/usr/bin/env python3
# coding: utf-8

"""
Mastodon -> Twitter cross-poster
"""

import time
import re
import html
import tempfile
import os
import mimetypes
import sys
import getpass
import json
from builtins import input
import requests

from mastodon import Mastodon
import twitter

from mtt_config_provider import *
import mtt_utils import *

# Boot-strap app and user information
if not os.path.isfile("mtt_twitter.secret") or os.stat("mtt_twitter.secret").st_size is 0:
    print("This appears to be your first time running MastodonToTwitter.")
    print("After some configuration, you'll be up and running in no time.")
    print("First of all, to talk to twitter, you'll need a twitter API key.")
    print("\n")
    print("Usually, the application creator is supposed to make that, but with")
    print("an application that isn't a hosted service or a binary blob, with")
    print("the key in plain text, this is not easily possible.")
    print("\n")
    print("You'll need to register an app on https://apps.twitter.com/ .")
    print("You may have to add a phone number to your twitter account to be able")
    print("to do this.")
    print("\n")
    print("Once you are done (make sure to allow your app write permissions),")
    print("go to your apps 'Keys and Tokens' page and enter the info from there")
    print("here.")
    print("\n")

    twitter_works = False
    while not twitter_works:
        TWITTER_CONSUMER_KEY = input("Twitter Consumer Key (API Key): ").strip()
        TWITTER_CONSUMER_SECRET = input("Twitter Consumer Secret (API Secret): ").strip()
        TWITTER_ACCESS_KEY = input("Twitter Access Token: ").strip()
        TWITTER_ACCESS_SECRET = input("Twitter Access Token Secret: ").strip()

        print("\n")
        print("Alright, trying to connect to twitter with those credentials...")
        print("\n")

        try:
            twitter_works = True
            twitter_api = twitter.Api(
                consumer_key = TWITTER_CONSUMER_KEY,
                consumer_secret = TWITTER_CONSUMER_SECRET,
                access_token_key = TWITTER_ACCESS_KEY,
                access_token_secret = TWITTER_ACCESS_SECRET
            )
            twitter_api.VerifyCredentials()
        except:
            twitter_works = False

        if twitter_works == False:
            print("Hmm, that didn't work. Check if you copied everything correctly")
            print("and make sure you are connected to the internet.")
            print("\n")

    print("Great! Twitter access works! With mastodon, the situation is a bit easier,")
    print("all you'll have to do is enter your username (that you log in to mastodon")
    print("with, this is usually your e-mail) and password.")
    print("\n")

    mastodon_works = False
    while mastodon_works == False:
        MASTODON_BASE_URL = 'https://' + input("Mastodon server (press Enter for mastodon.social): https://").strip()
        MASTODON_USERNAME = input("Mastodon Username (e-mail): ").strip()
        MASTODON_PASSWORD = getpass.getpass("Mastodon Password: ").strip()

        if MASTODON_BASE_URL == 'https://':
            # The Mastodon instance base URL. By default, https://mastodon.social/
            MASTODON_BASE_URL = "https://mastodon.social"

        print("\n")
        if os.path.isfile("mtt_mastodon_server.secret") and os.stat("mtt_mastodon_server.secret").st_size is not 0:
            print("You already have Mastodon server set up, so we're skipping that step.")
        else:
            print("Recording Mastodon server...")
            try:
                with open("mtt_mastodon_server.secret", "w") as mastodon_server:
                    mastodon_server.write(MASTODON_BASE_URL)
            except OSError as e:
                print("... but it failed.", e)
                sys.exit(-1)
                mastodon_works = False

        print("\n")
        if os.path.isfile("mtt_mastodon_client.secret") and os.stat("mtt_mastodon_client.secret").st_size is not 0:
            print("You already have an app set up, so we're skipping that step.")
        else:
            print("App creation should be automatic...")
            try:
                Mastodon.create_app(
                    "MastodonToTwitter",
                    to_file = "mtt_mastodon_client.secret",
                    scopes = ["read", "write"],
                    api_base_url = MASTODON_BASE_URL
                )
            except Exception as e:
                print("... but it failed. That shouldn't really happen. Please retry ")
                print("from the start, and if it keeps not working, submit a bug report at")
                print("http://github.com/halcy/MastodonToTwitter .")
                print(e)
                sys.exit(-1)
            print("...done! Next up, lets verify your login data.")
        print("\n")

        try:
            mastodon_works = True
            mastodon_api = Mastodon(
                client_id = "mtt_mastodon_client.secret",
                api_base_url = MASTODON_BASE_URL
            )
            mastodon_api.log_in(
                username = MASTODON_USERNAME,
                password = MASTODON_PASSWORD,
                to_file = "mtt_mastodon_user.secret",
                scopes = ["read", "write"]
            )
        except:
            mastodon_works = False

        if mastodon_works == False:
            print("Logging in didn't work. Check if you typed something wrong")
            print("and make sure you are connected to the internet.")
            print("\n")

    print("Alright, then, looks like you're all set!")
    print("\n")
    print("Your credentials have been saved to three files ending in .secret in the")
    print("current directory. While none of the files contain any of your passwords,")
    print("the keys inside will allow people to access your Twitter and Mastodon")
    print("accounts, so make sure other people cannot accces them!")
    print("\n")
    print("The cross-poster will now start, and should post all your mastodon posts")
    print("from this moment on to twitter while it is running! For future runs, you")
    print("won't see any of these messages. To start over, simply delete all the .secret")
    print("files. Have fun tooting!")
    print("\n")

    with open("mtt_twitter.secret", 'w') as secret_file:
        secret_file.write(TWITTER_CONSUMER_KEY + '\n')
        secret_file.write(TWITTER_CONSUMER_SECRET + '\n')
        secret_file.write(TWITTER_ACCESS_KEY + '\n')
        secret_file.write(TWITTER_ACCESS_SECRET + '\n')

# Read in twitter credentials
with open("mtt_twitter.secret", 'r') as secret_file:
    TWITTER_CONSUMER_KEY = secret_file.readline().rstrip()
    TWITTER_CONSUMER_SECRET = secret_file.readline().rstrip()
    TWITTER_ACCESS_KEY = secret_file.readline().rstrip()
    TWITTER_ACCESS_SECRET = secret_file.readline().rstrip()

# Read in Mastodon server
with open("mtt_mastodon_server.secret", 'r') as secret_file:
    MASTODON_BASE_URL = secret_file.readline().rstrip()

# Log in and start up
mastodon_api = Mastodon(
    client_id = "mtt_mastodon_client.secret",
    access_token = "mtt_mastodon_user.secret",
    ratelimit_method="wait",
    api_base_url = MASTODON_BASE_URL
)
twitter_api = twitter.Api(
    consumer_key = TWITTER_CONSUMER_KEY,
    consumer_secret = TWITTER_CONSUMER_SECRET,
    access_token_key = TWITTER_ACCESS_KEY,
    access_token_secret = TWITTER_ACCESS_SECRET,
    tweet_mode = 'extended' # Allow tweets longer than 140 raw characters
)

ma_account_id = mastodon_api.account_verify_credentials()["id"]
tw_account_id = twitter_api.VerifyCredentials().id
try:
    since_toot_id = mastodon_api.account_statuses(ma_account_id)[0]["id"]
except:
    since_toot_id = 0
print("Tweeting any toots after toot " + str(since_toot_id))
since_tweet_id = twitter_api.GetUserTimeline()[0].id
print("Tooting any tweets after tweet " + str(since_tweet_id))

# Set "last URL length update" time to 1970
last_url_len_update = 0

# Loads tweets/toots associations to be able to mirror threads
# This links the toots and tweets. For links from Mastodon to
# Twitter, the toot listed is the last one of the generated thread
# if the toot is too long to fit into a single tweet.
status_associations = {'m2t': {}, 't2m': {}}
try:
    with open('mtt_status_associations.json', 'r') as f:
        status_associations['m2t'] = json.load(f, object_hook=lambda d: {int(k): v for k, v in d.items()})
        status_associations['t2m'] = {tweet_id: toot_id for toot_id, tweet_id in status_associations['m2t'].items()}
except:
    pass

while True:
    # Fetch twitter short URL length, if needed
    if time.time() - last_url_len_update > 60 * 60 * 24:
        twitter_api._config = None
        url_length = max(twitter_api.GetShortUrlLength(False), twitter_api.GetShortUrlLength(True)) + 1
        last_url_len_update = time.time()
        print("Updated expected short URL length: Is now " + str(url_length))

    # Fetch new toots
    new_toots = []
    if POST_ON_TWITTER:
        new_toots = mastodon_api.account_statuses(ma_account_id, since_id = since_toot_id)
    if len(new_toots) != 0:
        since_toot_id = new_toots[0]["id"]
        new_toots.reverse()
        MEDIA_REGEXP = re.compile(re.escape(MASTODON_BASE_URL.rstrip("/")) + "\/media\/(\w)+(\s|$)+")

        print('Found new toots, processing:')
        for toot in new_toots:
            toot_id = toot["id"]
            content = toot["content"]
            media_attachments = toot["media_attachments"]

            # We trust mastodon to return valid HTML
            content_clean = re.sub(r'<a [^>]*href="([^"]+)">[^<]*</a>', '\g<1>', content)

            # We replace html br with new lines
            content_clean = "\n".join(re.compile(r'<br ?/?>', re.IGNORECASE).split(content_clean))
            # We must also replace new paragraphs with double line skips
            content_clean = "\n\n".join(re.compile(r'</p><p>', re.IGNORECASE).split(content_clean))
            # Then we can delete the other html contents and unescape the string
            content_clean = html.unescape(str(re.compile(r'<.*?>').sub("", content_clean).strip()))
            # Trim out media URLs
            content_clean = re.sub(MEDIA_REGEXP, "", content_clean)

            # Don't cross-post replies or only if toot is a boost (reblog)
            if len(content_clean) != 0 and content_clean[0] == '@' and not toot['reblog']:
                print('Skipping toot "' + content_clean + '" - is a reply.')
                continue

            if TWEET_CW_PREFIX and toot['spoiler_text']:
                content_clean = TWEET_CW_PREFIX.format(toot['spoiler_text']) + content_clean

            if TWEET_BOOST_PREFIX and toot['reblog']:
                content_clean = TWEET_BOOST_PREFIX.format(toot['reblog']['account']['acct']) + content_clean

            # Split toots, if need be, using Many magic numbers.
            content_parts = []
            if calc_expected_status_length(content_clean, short_url_length = url_length) > 140:
                print('Toot bigger 140 characters, need to split...')
                content_parts = split_toot(content_clean, max_url_length = url_length, multi_split = SPLIT_ON_TWITTER and not toot['reblog'])
                # Append toot url if split disable or toot is a boost (reblog)
                if not SPLIT_ON_TWITTER or toot['reblog']
                    content_parts[-1] += toot['url']
            else:
                print('Toot smaller than 140 chars, posting directly...')
                content_parts.append(content_clean)

            # Tweet all the parts. On error, give up and go on with the next toot.
            try:
                reply_to = None

                # We check if this toot is a reply to a previously sent toot.
                # If so, the first corresponding tweet will be a reply to
                # the stored tweet.
                # Unlike in the Mastodon API calls, we don't have to handle the
                # case where the tweet was deleted, as twitter will ignore
                # the in_reply_to_status_id option if the given tweet
                # does not exists.
                if toot['in_reply_to_id'] in status_associations['m2t']:
                    reply_to = status_associations['m2t'][toot['in_reply_to_id']]

                for i in range(len(content_parts)):
                    media_ids = []
                    content_tweet = content_parts[i]

                    # Last content part: Upload media, no -- at the end
                    if i == len(content_parts) - 1:
                        for attachment in media_attachments:
                            attachment_url = attachment["url"]

                            print('Downloading ' + attachment_url)
                            attachment_file = requests.get(attachment_url, stream=True)
                            attachment_file.raw.decode_content = True
                            temp_file = tempfile.NamedTemporaryFile(delete = False)
                            temp_file.write(attachment_file.raw.read())
                            temp_file.close()

                            file_extension = mimetypes.guess_extension(attachment_file.headers['Content-type'])
                            upload_file_name = temp_file.name + file_extension
                            os.rename(temp_file.name, upload_file_name)

                            temp_file_read = open(upload_file_name, 'rb')
                            print('Uploading ' + upload_file_name)
                            media_ids.append(twitter_api.UploadMediaChunked(media = temp_file_read))
                            temp_file_read.close()
                            os.unlink(upload_file_name)

                        content_tweet = content_parts[i]

                    # Some final cleaning
                    content_tweet = content_tweet.strip()

                    # Retry three times before giving up
                    retry_counter = 0
                    post_success = False
                    while post_success == False:
                        try:
                            # Tweet
                            if len(media_ids) == 0:
                                print('Tweeting "' + content_tweet + '"...')
                                reply_to = twitter_api.PostUpdate(content_tweet, in_reply_to_status_id=reply_to).id
                                since_tweet_id = reply_to
                                post_success = True
                            else:
                                print('Tweeting "' + content_tweet + '", with attachments...')
                                reply_to = twitter_api.PostUpdate(content_tweet, media=media_ids, in_reply_to_status_id=reply_to).id
                                since_tweet_id = reply_to
                                post_success = True
                        except:
                            if retry_counter < MASTODON_RETRIES:
                                retry_counter += 1
                                time.sleep(MASTODON_RETRY_DELAY)
                            else:
                                raise

                    # Only the last tweet is linked to the toot, see comment
                    # above the status_associations declaration
                    if i == len(content_parts) - 1:
                        status_associations['m2t'][toot_id] = since_tweet_id
                        status_associations['t2m'][since_tweet_id] = toot_id
            except:
                print("Encountered error after " + str(MASTODON_RETRIES) + " retries. Not retrying.")

        print('Finished toot processing, resting until next toots.')

    # Fetch new tweets
    new_tweets = []
    if POST_ON_MASTODON:
        new_tweets = twitter_api.GetUserTimeline(since_id = since_tweet_id, include_rts=False, exclude_replies=False)
    if len(new_tweets) != 0:
        since_tweet_id = new_tweets[0].id

        print('Found new tweets, processing:')
        for tweet in new_tweets:
            tweet_id = tweet.id
            content = tweet.full_text
            reply_to = None

            if tweet.in_reply_to_user_id:
                # If it's a reply, we keep the tweet if:
                # 1. it's a reply from us (in a thread);
                # 2. it's a reply from a previously transmitted tweet, so we don't sync
                #    if someone replies to someone in two or more tweets (because in this
                #    case the 2nd tweet and the ones after are replying to us)
                if tweet.in_reply_to_user_id != tw_account_id or tweet.in_reply_to_status_id not in status_associations['t2m']:
                    print('Skipping tweet "' + content + '" - is a reply.')
                    continue

                reply_to = status_associations['t2m'][tweet.in_reply_to_status_id]

            media_attachments = tweet.media
            urls = tweet.urls
            sensitive = tweet.possibly_sensitive

            content_toot = html.unescape(content)
            mentions = re.findall(r'[@]\S*', content_toot)
            cws = TWEET_CW_REGEXP.findall(content) if TWEET_CW_REGEXP else []
            warning = None
            media_ids = []

            if mentions:
                for mention in mentions:
                    # Replace all mentions for an equivalent to clearly signal their origin on Twitter
                    content_toot = re.sub(mention, mention + '@twitter.com', content_toot)

            if urls:
                for url in urls:
                    # Unshorten URLs
                    content_toot = re.sub(url.url, url.expanded_url, content_toot)

            if cws:
                warning = TWEET_CW_SEPARATOR.join([cw.strip() for cw in cws]) if TWEET_CW_ALLOW_MULTI else cws[0].strip()
                content_toot = TWEET_CW_REGEXP.sub('', content_toot, count=0 if TWEET_CW_ALLOW_MULTI else 1).strip()

            if media_attachments:
                for attachment in media_attachments:
                    # Remove the t.co link to the media
                    content_toot = re.sub(attachment.url, "", content_toot)

                    attachment_url = attachment.media_url

                    print('Downloading ' + attachment_url)
                    attachment_file = requests.get(attachment_url, stream=True)
                    attachment_file.raw.decode_content = True
                    temp_file = tempfile.NamedTemporaryFile(delete = False)
                    temp_file.write(attachment_file.raw.read())
                    temp_file.close()

                    file_extension = mimetypes.guess_extension(attachment_file.headers['Content-type'])
                    upload_file_name = temp_file.name + file_extension
                    os.rename(temp_file.name, upload_file_name)

                    print('Uploading ' + upload_file_name)
                    media_ids.append(mastodon_api.media_post(upload_file_name))
                    os.unlink(upload_file_name)

            try:
                retry_counter = 0
                post_success = False
                while post_success == False:
                    try:
                        # Toot
                        if len(media_ids) == 0:
                            print('Tooting "' + content_toot + '"...')
                            try:
                                post = mastodon_api.status_post(content_toot, visibility=TOOT_VISIBILITY, in_reply_to_id=reply_to, spoiler_text=warning)
                            except mastodon.Mastodon.MastodonAPIError:
                                # If the toot we are replying to has been deleted
                                post = mastodon_api.status_post(content_toot, visibility=TOOT_VISIBILITY, spoiler_text=warning)
                            since_toot_id = post["id"]
                            post_success = True
                        else:
                            print('Tooting "' + content_toot + '", with attachments...')
                            try:
                                post = mastodon_api.status_post(content_toot, media_ids=media_ids, visibility=TOOT_VISIBILITY, sensitive=sensitive, in_reply_to_id=reply_to, spoiler_text=warning)
                            except mastodon.Mastodon.MastodonAPIError:
                                # If the toot we are replying to has been deleted (same as before)
                                post = mastodon_api.status_post(content_toot, media_ids=media_ids, visibility=TOOT_VISIBILITY, sensitive=sensitive, spoiler_text=warning)
                            since_toot_id = post["id"]
                            post_success = True
                    except:
                        if retry_counter < TWITTER_RETRIES:
                            retry_counter += 1
                            time.sleep(TWITTER_RETRY_DELAY)
                        else:
                            raise

                status_associations['t2m'][tweet_id] = since_toot_id
                status_associations['m2t'][since_toot_id] = tweet_id
            except:
                print("Encountered error after " + str(TWITTER_RETRIES) + " retries. Not retrying.")

        print('Finished tweet processing, resting until next tweets.')

    # We save the status associations in file
    try:
        with open('mtt_status_associations.json', 'w') as f:
            json.dump(status_associations['m2t'], f)
    except:
        print('Encountered error while saving status associations file. Threads might be broken after MTT service restart. Check files permissions.')

    time.sleep(API_POLL_DELAY)
