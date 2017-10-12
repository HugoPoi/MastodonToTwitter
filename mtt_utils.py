#!/usr/bin/env python3
# coding: utf-8

"""
Utils functions for MastodonToTwitter
"""

import re
from mtt_config_provider import *

def calc_expected_status_length(status, short_url_length = 23):
    replaced_chars = 0
    status_length = len(status)
    match = re.findall(URL_REGEXP, status)
    if len(match) >= 1:
        replaced_chars = len(''.join(map(lambda x: x[0], match)))
        status_length = status_length - replaced_chars + (short_url_length * len(match))
    return status_length

def split_toot(content_clean, max_url_length, multi_split = False):
    content_parts = []
    current_part = ""
    for next_word in content_clean.split(" "):
        # Need to split here?
        if calc_expected_status_length(current_part + " " + next_word, short_url_length = max_url_length) > 135:
            print("new part")
            space_left = 135 - calc_expected_status_length(current_part, short_url_length = max_url_length) - 1


            if multi_split:
                # Want to split word?
                if len(next_word) > 30 and space_left > 5 and not twitter.twitter_utils.is_url(next_word):
                    current_part = current_part + " " + next_word[:space_left]
                    content_parts.append(current_part)
                    current_part = next_word[space_left:]
                else:
                    content_parts.append(current_part)
                    current_part = next_word

                # Split potential overlong word in current_part
                while len(current_part) > 135:
                    content_parts.append(current_part[:135])
                    current_part = current_part[135:]
            else:
                print('In fact we just cut')
                space_for_suffix = len('… ') + max_url_length
                content_parts.append(current_part[:-space_for_suffix] + '… ')
                current_part = ''
                break
        else:
            # Just plop next word on
            current_part = current_part + " " + next_word
    # Insert last part
    if len(current_part.strip()) != 0 or len(content_parts) == 0:
        content_parts.append(current_part.strip())
    return content_parts

