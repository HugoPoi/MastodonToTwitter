#!/usr/bin/env python3
# coding: utf-8

"""
Config default for MastodonToTwitter
"""

import re
import twitter

# Enable repost on services
POST_ON_MASTODON = True
POST_ON_TWITTER = True

# Should we slice long messages from Mastodon on Twitter, or cut them
SPLIT_ON_TWITTER = True

# Manage visibility of your toot. Value are "private", "unlisted" or "public"
TOOT_VISIBILITY = "unlisted"

# How long to wait between polls to the APIs, in seconds
API_POLL_DELAY = 30

# How often to retry when posting fails
MASTODON_RETRIES = 3
TWITTER_RETRIES = 3

# How long to wait between retries, in seconds
MASTODON_RETRY_DELAY = 20
TWITTER_RETRY_DELAY = 20

# The text to prepend to tweets, if the corresponding toot has a
# content warning. {} is the spoiler text.
# To disable content warnings from Mastodon to Twitter, set to None.
TWEET_CW_PREFIX = '[TW ⋅ {}]\n\n'

# The regex to match against tweet to extract a content warning.
# The CW spoiler text should be in the first capture group.
# The matching parts of the tweets will be removed and the CW found
# in the capture group #1 will be displayed as a CW in Mastodon.
# If multiple CW are found into the tweet, all will be added, separated
# by the separator below, in the Mastodon CW, and all will be removed from
# the original tweet. Except if TWEET_CW_ALLOW_MULTI is set to False, then
# only the first one will be considered.
# To disable content warnings from Twitter to Mastodon, set to None.
TWEET_CW_REGEXP = re.compile(r'\[(?:(?:(?:C|T)W)|SPOIL(?:ER)?)(?:[\s\-\.⋅,:–—]+)([^\]]+)\]', re.IGNORECASE)
TWEET_CW_ALLOW_MULTI = True
TWEET_CW_SEPARATOR = ', '

# The text to prepend to tweets, it the corresponding toot is a
# boost/reblog. {} is the full username (acct) user@instance
# To disable prefixed boost from Mastodon to Twitter, set to None.
TWEET_BOOST_PREFIX = 'BOOST {}:\n'

# Some helpers copied out from python-twitter, because they're broken there
URL_REGEXP = re.compile((
    r'('
    r'(?!(https?://|www\.)?\.|ftps?://|([0-9]+\.){{1,3}}\d+)'  # exclude urls that start with "."
    r'(?:https?://|www\.)*(?!.*@)(?:[\w+-_]+[.])'              # beginning of url
    r'(?:{0}\b|'                                               # all tlds
    r'(?:[:0-9]))'                                             # port numbers & close off TLDs
    r'(?:[\w+\/]?[a-z0-9!\*\'\(\);:&=\+\$/%#\[\]\-_\.,~?])*'   # path/query params
    r')').format(r'\b|'.join(twitter.twitter_utils.TLDS)), re.U | re.I | re.X)

try:
    from mtt_config import *
    print('Configuration from mtt_config.py loaded.')
except ImportError:
    pass
