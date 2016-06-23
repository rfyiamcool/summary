# -*- coding: utf-8 -*-

'''
自动文摘算法：应用向量空间模型，计算每句话与文档的相似度，提取摘要
'''

from __future__ import division

from math import log

import jieba

from summary.config import k1
from summary.config import b
from summary.utils import cos_sim
from summary.config import PUNC_STR
from summary.stopword import stop_words

def cal_idf(df_dict, term, n):
    """计算idf值"""
    tmp = (n - df_dict[term] + 0.5) / (df_dict[term] + 0.5)
    if tmp <= 1:
        tmp += 1
    return log(tmp, 2)


def cal_bm25(tf_dict, df_dict, term, n, avgdl):
    """计算bm25值"""
    idf = cal_idf(df_dict, term, n)
    tf = tf_dict[term]
    len_d = sum(tf_dict.values())
    return idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * len_d / avgdl))


def cal_max_value(d):
    """ 计算dict d的最大value及对于的key"""
    max_key = None
    max_value = None
    for key in d:
        value = d[key]
        if max_key is None or value > max_value:
            max_key, max_value = key, value
    return max_key


class Summarization(object):
    """ 给定text生成摘要"""
    def __init__(self, settings):
        self.text = settings["text"]
        self.key = settings.get("key", None)
        self.max_word = settings.get("max_word", 200)
        self.max_sent = settings.get("max_sent", 5)
        # 将字符串根据符号PUNC_STR分成句子
        self.sents = sentence(self.text)
        self.num_sents = len(self.sents)
        self.avgdl = len(self.text) / self.num_sents if self.num_sents else None
        self.tf_dict_list, self.df_dict, self.term_dict = summ_seg(self.sents)

    def cal_sim(self, sent_dict, ignore_term):
        """ 计算句子sent和文档的相似度"""
        vector = {}
        for term in sent_dict:
            if term not in ignore_term:
                vector[term] = cal_bm25(sent_dict,
                                        self.df_dict,
                                        term,
                                        self.num_sents,
                                        self.avgdl)
        return cos_sim(vector, self.term_dict)

    def get_score(self, top_sent_index, ignore_term):
        score_dict = {}
        for index, sent_dict in enumerate(self.tf_dict_list):
            if (self.key and self.key not in "".join(self.sents[index])) or \
               index in top_sent_index:
                continue
            sim = self.cal_sim(sent_dict, ignore_term)
            if sim:
                score_dict[index] = sim
        return score_dict

    def update(self, max_index, len_word, top_sent_index, ignore_term):
        """更新set，return True or False """
        top_sent_index.add(max_index)
        top_sent = self.sents[max_index]
        len_word += len(top_sent)
        if len_word >= self.max_word:
            return False
        for term in self.tf_dict_list[max_index]:
            ignore_term.add(term)
        if self.key in ignore_term:
            ignore_term.remove(self.key)
        return True

    def get_summary(self):
        '''输入正文content，摘要的最大字数max_word和最长句子数max_sent；输出摘要'''
        if self.num_sents == 0:
            return []
        len_sent = 0
        len_word = 0
        top_sent_index = set()
        ignore_term = set()
        while len_sent < self.max_sent:
            score_dict = self.get_score(top_sent_index, ignore_term)
            if not score_dict:
                break
            max_index = cal_max_value(score_dict)
            up = self.update(max_index, len_word,
                             top_sent_index, ignore_term)
            if up is False:
                break
            len_sent += 1
        if top_sent_index:
            return ["".join(self.sents[index]) for index in top_sent_index]
        return []


def sentence(content):
    '''将正文按句号问号感叹号分句
    对content整体分词，减少jiebasegfun的调用次数
    '''
    # 将换行符替换为句号
    sents = []
    content = content.replace(u"\n", u"。")
    # 直接调用本地jieba分词包
    term_list = list(jieba.cut(content))
    if term_list is None:
        return sents
    n_terms = len(term_list)
    start = 0
    for i in xrange(n_terms):
        if term_list[i] in PUNC_STR:
            sents.append(term_list[start: i+1])
            start = i+1
    if start < n_terms:
        sents.append(term_list[start:])
    return sents


def summ_seg(sents):
    ''' 分词,去除停用词，得到
    tf_dict_list: [tf_dict, tf_dict, ...]
    df_dict: term的df_dict
    term_dict: term 在所有文档中的term_dict
    '''
    tf_dict_list = []
    df_dict = {}
    term_dict = {}
    for sent in sents:
        tf_dict = sent_seg(sent)
        tf_dict_list.append(tf_dict)
        for term in tf_dict:
            if term in df_dict:
                df_dict[term] += 1
            else:
                df_dict[term] = 1
            if term in term_dict:
                term_dict[term] += tf_dict[term]
            else:
                term_dict[term] = tf_dict[term]
    return tf_dict_list, df_dict, term_dict


def sent_seg(sent):
    '''
    去除停用词，得到term的tf_dict
    输入：sent， 分词后的term_list
    输出：term的tf_dict
    '''
    tf_dict = {}
    for term in sent:
        if term in stop_words:
            continue
        if term in tf_dict:
            tf_dict[term] += 1
        else:
            tf_dict[term] = 1
    return tf_dict


def summary(text, key, max_word, max_sent):
    """
    Parameters
    ----------
    text: string, unicode
    key: string, unicode
    max_word: int
    max_sent: int

    Returns:
    --------
    sentence_list: array of string
    """
    summ = Summarization({"text": text,
                          "key": key,
                          "max_sent": max_sent,
                          "max_word": max_word
                          })
    return summ.get_summary()

if __name__ == '__main__':
    print summary(u"年终钜惠！锐志最高优惠2.5万元   2014年01月21日， 大连华通丰田锐志最高优惠2.5万元，感兴趣的朋友可以到店咨询购买，具体优惠信息如下：      锐志", u"丰田", 1, 150)
