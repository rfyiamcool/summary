# summary

该模块用来实现计算文章的摘要.

使用的算法是应用向量空间模型，计算每句话与文档的相似度，提取摘要.

`test.py`

```
# -*- coding:utf-8 -*-

import requests

from summary.summarization import summary

url = "http://xiaorui.cc"
text = requests.get(url).text
keyword = u"峰云"
summary_text = summary(text, keyword, 1, 145)

keyword = u"python"
summary_text = summary(text, keyword, 1, 145)

keyword = u"golang"
summary_text = summary(text, keyword, 1, 145)

```
