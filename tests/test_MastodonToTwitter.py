#!/usr/bin/env python3
# coding: utf-8

"""
Mastodon -> Twitter cross-poster
"""

import unittest

import mtt_utils

class TestMastodonToTwitter(unittest.TestCase):

    def test_split_toot(self):
        self.assertEqual(mtt_utils.split_toot('FOO', max_url_length = 24), ['FOO'])
        self.assertEqual(mtt_utils.split_toot('Ceci est un test de toot très long type roman pour tester la longueur avec multi-split désactivé, ce toot devrait être coupé vers cet emplacement.', max_url_length = 24), ['Ceci est un test de toot très long type roman pour tester la longueur avec ', 'multi-split désactivé.'])
        self.assertEqual(mtt_utils.split_toot('BOOST hugopoi@mastodon.hugopoi.net:\nTrying a longgggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg message for twitter !', max_url_length = 24), ['FOO'])


if __name__ == '__main__':
    unittest.main()
