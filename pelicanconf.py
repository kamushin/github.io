#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Kamushin'
SITENAME = "Kamushin's blog"
SITEURL = ''

TIMEZONE = 'Asia/Shanghai'

DISQUS_SITENAME = 'kamushin'
DEFAULT_LANG = 'zh-cn'
DEFAULT_DATE_FORMAT = '%Y-%m-%d %H-%M-%S'
DEFAULT_DATE='fs'
# Feed generation is usually not desired when developing
USE_FOLDER_AS_CATEGORY = True
FILENAME_METADATA = '(?P<slug>.*)'

ARTICLE_URL = '{category}/{slug}.html'
ARTICLE_SAVE_AS = ARTICLE_URL
PAGE_URL = '{slug}.html'
PAGE_SAVE_AS = PAGE_URL
CATEGORY_URL = '{slug}/index.html'
CATEGORY_SAVE_AS = CATEGORY_URL
TAG_URL = 'tag/{slug}.html'
TAG_SAVE_AS = TAG_URL
TAGS_SAVE_AS = 'tag/index.html'

FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

# Blogroll
LINKS =  (('liaojie', 'http://liaojie.me/'),
          ('撸人', 'http://www.lulinux.com/'),
          ('ian', 'http://www.yinyien.com/'),
          ('ixindoo', 'http://ixindoo.com/'),
          )

# Social widget
SOCIAL = (('Github', 'https://github.com/kamushin'),
        ('SegmentFault', 'http://segmentfault.com/u/kamushin'),)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
#see evernote
#DELETE_OUTPUT_DIRECTORY = True
OUTPUT_RETENTION = [".hg", ".git", ".bzr"]

THEME = "pelican-themes/tuxlite_tbs"

MENUITEMS = (
        ('ABOUT', '/about.html'),
        )
