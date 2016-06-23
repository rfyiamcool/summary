#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from math import sqrt

from summary.config import JIEBA_SEG_SERVER_IP
from summary.config import LIMIT_SEG_SERVER_SECONDS

def cos_sim(a_dict, b_dict):
    result = 0
    sum_a = 0
    for key in a_dict:
        if key in b_dict:
            result += a_dict[key] * b_dict[key]
        sum_a += a_dict[key] ** 2
    sqrt_a = sqrt(sum_a)
    sqrt_b = sqrt(sum([b_dict[key] ** 2 for key in b_dict]))
    if sqrt_a and sqrt_b:
        return result / (sqrt_a * sqrt_b)
    return 0
