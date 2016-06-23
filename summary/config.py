# -*- coding: utf-8 -*-
from settings import JIEBA_ADDR
# 结巴分词服务ip
JIEBA_SEG_SERVER_IP = JIEBA_ADDR
# 设置timeout
LIMIT_SEG_SERVER_SECONDS = 0.5

PUNC_STR = (u'。', u'？', u'！', u"?", u"!", u"\n")
# BM25参数
k1 = 2
b = 0.75
