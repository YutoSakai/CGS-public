#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.getcwd())
import csv
import CaboChaWrapper as cw

def form_convert(str_class, conj, form, orig):

    '''単語を目的の活用形に変換
      str_class:品詞
      conj:活用の種類
      form:活用形
      orig:原形
    '''

    # MeCab辞書を読み込み
    f = ""
    if str_class == u"動詞":
        f = open('library/Verb.csv', 'rt', encoding='shift_jis')
    elif str_class == u"形容詞":
        f = open('library/Adj.csv', 'rt', encoding='shift_jis')
    dataReader = csv.reader(f)

    # 活用の種類、活用形、原形が同じ行を探す
    after_str = ""
    for row in dataReader:
        for (i, s) in enumerate(row):
            if i == 8:
                conj_tmp = s
            elif i == 9:
                form_tmp = s
            elif i == 10:
                orig_tmp = s
        if (orig_tmp == orig) and (form_tmp == form) and (conj_tmp == conj):
            after_str = row[0]
            break
        # conjが「サ変・－スル」の場合は例外処理
        if (orig_tmp == orig) and (form_tmp == form) and ((u"サ変" in conj_tmp) and (u"サ変" in conj)):
            after_str = row[0]
            break

    if (not after_str) and (form == u"連用タ接続"):
        form = u"連用形"
        after_str = form_convert(str_class, conj, form, orig)
    if (not after_str) and (form == u"連用形"):
        form = u"未然形"
        after_str = form_convert(str_class, conj, form, orig)

    # 改行を除去
    after_str = after_str.replace("\n", "")

    return after_str

if __name__ == "__main__":

    str_class = u"動詞"
    conj = u"サ変・－スル"
    # conj = u"五段・マ行"
    orig = u"征する"
    after_str = form_convert(str_class, conj, u"連用形", orig)
    # print(after_str)
