#!/usr/bin/env python
# -*- coding:utf-8 -*-

import requests

from summary.summarization import summary

url = "http://xiaorui.cc"
text = requests.get(url).text
keyword = u"峰云"
summary_text = summary(text, keyword, 1, 145)

