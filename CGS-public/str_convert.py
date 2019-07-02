#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

sys.path.append(os.getcwd())
import codecs
import random
import constants
import CaboChaWrapper as cw
import form_convert as fc
from datetime import datetime
import re


def split_str(s, n):
    '''文を固定長で分割
      s:分割したい文
      n:分割したい長さ
    '''
    length = len(s.decode('utf-8'))
    return [s[i:i + n] for i in range(0, length, n)]


def str_convert_explain(input_sentence):
    '''1コマ目の文章を生成(ですます)'''

    # 「～について説明します/しましょう」をつなげる

    flag = random.randint(0, 1)
    if flag == 0:
        input_sentence = "「" + input_sentence + "」" + u"について説明します"
    else:
        input_sentence = "「" + input_sentence + "」" + u"について説明しましょう"

    return input_sentence


def str_convert(sent):
    '''文体をですますに変換'''

    # CaboChaで構文解析を実施
    # 句点を含んだ文を入力しないと意図した結果が得られない
    # →句点を考慮するためにインデックスを-2まで参照
    cab = cw.CaboChaWrapper(constants.CHAR_CODE)
    cab.parse(sent, True)
    flag = 0

    tmp = ""
    str_tmp0 = str_tmp1 = ""
    subclass01 = subclass11 = subclass21 = subclass31 = ""

    sq_bracket = 0  # 文末がかぎ括弧の途中に存在するかどうか
    ro_bracket = 0  # 文末が丸括弧の途中に存在するかどうか

    for i, chunk in enumerate(cab.chunks):  # 文節単位
        # print(tmp)
        # 係り受け関係を調べる
        id = chunk.id  # 文節番号
        link = chunk.link  # 係り先文節番号
        if (id + 1) == link:  # 1つ次の文節に係っているかどうか
            link_flag = 1
        else:
            link_flag = 0

        flag = 0  # 文体変換したかどうかを表すフラグ
        for j, token in enumerate(chunk.tokens):  # 形態素単位
            str_class0 = token.features["class"]  # 品詞
            conj0 = token.features["conj"]  # 活用の種類
            form0 = token.features["form"]  # 活用形
            orig0 = token.features["orig"]  # 原形
            subclass01 = token.features["subclass1"]  # 品詞細分類1
            str_tmp0 = token.surface  # 表層文字列

            str_class1 = str_class2 = str_class3 = ""
            orig1 = orig2 = orig3 = orig4 = orig5 = ""
            subclass11 = subclass21 = subclass31 = subclass41 = subclass51 = ""
            str_tmp1 = ""
            form2 = ""

            if j < (len(chunk.tokens) - 1):  # 1つ次の形態素
                str_class1 = chunk.tokens[j + 1].features["class"]  # 品詞
                form1 = chunk.tokens[j + 1].features["form"]  # 活用形
                orig1 = chunk.tokens[j + 1].features["orig"]  # 原形
                subclass11 = chunk.tokens[j + 1].features["subclass1"]  # 品詞細分類1
                str_tmp1 = chunk.tokens[j + 1].surface  # 表層文字列
            if j < (len(chunk.tokens) - 2):  # 2つ次の形態素
                str_class2 = chunk.tokens[j + 2].features["class"]  # 品詞
                form2 = chunk.tokens[j + 2].features["form"]  # 活用形
                orig2 = chunk.tokens[j + 2].features["orig"]  # 原形
                subclass21 = chunk.tokens[j + 2].features["subclass1"]  # 品詞細分類1
            if j < (len(chunk.tokens) - 3):  # 3つ次の形態素
                str_class3 = chunk.tokens[j + 3].features["class"]  # 品詞
                form3 = chunk.tokens[j + 3].features["form"]  # 活用形
                orig3 = chunk.tokens[j + 3].features["orig"]  # 原形
                subclass31 = chunk.tokens[j + 3].features["subclass1"]  # 品詞細分類1
            if j < (len(chunk.tokens) - 4):  # 4つ次の形態素
                orig4 = chunk.tokens[j + 4].features["orig"]  # 原形
                subclass41 = chunk.tokens[j + 4].features["subclass1"]  # 品詞細分類1
            if j < (len(chunk.tokens) - 5):  # 5つ次の形態素
                str_class5 = chunk.tokens[j + 5].features["class"]  # 品詞
                form5 = chunk.tokens[j + 5].features["form"]  # 活用形
                orig5 = chunk.tokens[j + 5].features["orig"]  # 原形
                subclass51 = chunk.tokens[j + 5].features["subclass1"]  # 品詞細分類1

            if (str_tmp0 == u"\n") or (str_tmp0 == u"\\n"):
                # print("yes")
                tmp += str_tmp0
                flag = 0

            if (flag == 0):  # まだ変換していないとき

                # 形態素が括弧内に存在するかどうかを判定
                if "「" in str_tmp0:
                    sq_bracket = 1
                if "」" in str_tmp0:
                    sq_bracket = 0
                if "(" in str_tmp0:
                    ro_bracket = 1
                if ")" in str_tmp0:
                    ro_bracket = 0

                # 括弧内は処理しない
                if (sq_bracket == 1) or (ro_bracket == 1):
                    tmp += str_tmp0
                    continue

                # 「です」「ます」を含む場合、フラグを3に(変換しない)
                if flag != 1:
                    if (orig0 == "です") or (orig0 == "ます"):
                        flag = 3
                    if j < (len(chunk.tokens) - 1) and ((orig1 == "です") or (orig1 == "ます")):
                        flag = 3
                    if j < (len(chunk.tokens) - 2) and ((orig2 == "です") or (orig2 == "ます")):
                        flag = 3

                # 追加ルール：接続詞「だが」→「しかし」
                if (str_class0 == u"接続詞") and (orig0 == u"だが"):
                    tmp += u"しかし"
                    flag = 2

                # 追加ルール：「という」→「といいます」
                if (i == (len(cab.chunks) - 1)) and (str_tmp0.endswith("という")):
                    tmp += u"といいます"
                    flag = 1

                if (flag != 1) and (link_flag != 1) and (
                        (i == (len(cab.chunks) - 1) and j == (len(chunk.tokens) - 2)) or (
                        subclass11 == u"接続助詞" and orig2 == u"、")):
                    # ルール1：動詞基本形 → 動詞連用形 ＋「ます」
                    if (str_class0 == u"動詞") and (form0 == u"基本形"):
                        conv = fc.form_convert(str_class0, conj0, u"連用形", orig0)
                        tmp += conv + u"ます"
                        flag = 1

                    # ルール5：助動詞「だ」基本形 →「です」
                    elif (str_class0 == u"助動詞") and (form0 == u"基本形") and (orig0 == u"だ"):
                        tmp += u"です"
                        flag = 1

                    # ルール7：助動詞「ない」基本形 →「ありません」
                    elif (str_class0 == u"助動詞") and (form0 == u"基本形") and (orig0 == u"ない"):
                        tmp += u"ありません"
                        flag = 1

                    # 追加ルール：動詞「いる」基本形 →「います」
                    elif (str_class0 == u"動詞") and (form0 == u"基本形") and (orig0 == u"いる"):
                        tmp += u"います"
                        flag = 1

                    # ルール13：形容詞「ない」基本形 →「ありません」
                    elif (str_class0 == u"形容詞") and (form0 == u"基本形") and (orig0 == u"ない"):
                        tmp += u"ありません"
                        flag = 1

                if (flag != 1) and (link_flag != 1) and (
                        (i == (len(cab.chunks) - 1) and j == (len(chunk.tokens) - 3)) or (
                        subclass21 == u"接続助詞" and orig3 == u"、")):
                    # ルール2：動詞連用形/連用タ接続＋助動詞「た」基本形 → 動詞連用形/連用タ接続 ＋「ました」
                    # ルール2：動詞連用形/連用タ接続＋助動詞「た／だ」基本形 → 動詞連用形/連用タ接続 ＋「ました」
                    if ((str_class0 == u"動詞") and ((form0 == u"連用形") or (form0 == u"連用タ接続"))) \
                            and ((str_class1 == u"助動詞") and ((orig1 == u"た") or (orig1 == u"だ")) and (form1 == u"基本形")):
                        conv = fc.form_convert(str_class0, conj0, u"連用形", orig0)
                        tmp += conv + u"ました"
                        flag = 1

                    # ルール3：動詞未然形＋助動詞「ない」基本形 → 動詞連用形 ＋「ません」
                    elif ((str_class0 == u"動詞") and (form0 == u"未然形")) \
                            and ((str_class1 == u"助動詞") and (orig1 == u"ない") and (form1 == u"基本形")):
                        conv = fc.form_convert(str_class0, conj0, u"連用形", orig0)
                        tmp += conv + u"ません"
                        flag = 1

                    # ルール6：助動詞「だ」連用タ接続＋助動詞「た」基本形 →「でした」
                    elif ((str_class0 == u"助動詞") and (orig0 == u"だ") and (form0 == u"連用タ接続")) \
                            and ((str_class1 == u"助動詞") and (orig1 == u"た") and (form1 == u"基本形")):
                        tmp += u"でした"
                        flag = 1

                    # ルール8：助動詞「だ」連用タ接続＋助動詞「ある」基本形 →「です」
                    elif ((str_class0 == u"助動詞") and (orig0 == u"だ") and (form0 == u"連用形")) \
                            and ((str_class1 == u"助動詞") and (orig1 == u"ある") and (form1 == u"基本形")):
                        tmp += u"です"
                        flag = 1

                    # ルール11：助動詞「だ」未然形＋助動詞「う」基本形 →「でしょう」
                    elif ((str_class0 == u"助動詞") and (orig0 == u"だ") and (form0 == u"未然形")) \
                            and ((str_class1 == u"助動詞") and (orig1 == u"う") and (form1 == u"基本形")):
                        tmp += u"でしょう"
                        flag = 1

                    # ルール14：形容詞「ない」連用タ接続＋助動詞「た」基本形 →「ありませんでした」
                    elif ((str_class0 == u"形容詞") and (orig0 == u"ない") and (form0 == u"連用タ接続")) \
                            and ((str_class1 == u"助動詞") and (orig1 == u"た") and (form1 == u"基本形")):
                        tmp += u"ありませんでした"
                        flag = 1

                    # 追加ルール：名詞以外＋助動詞「らしい」基本形 →「そうです」
                    elif (str_class0 != u"名詞") and ((str_class1 == u"助動詞") and (orig1 == u"らしい") and (form1 == u"基本形")):
                        tmp += str_tmp0 + u"そうです"
                        flag = 1

                    # 追加ルール：助動詞「ない」基本形＋助詞「か」 →「ないでしょうか」
                    elif ((str_class0 == u"助動詞") and (form0 == u"基本形") and (orig0 == u"ない")) \
                            and ((str_class1 == u"助詞") and (orig1 == u"か")):
                        tmp += u"ないでしょうか"
                        flag = 1

                    # 追加ルール：動詞「みる」未然ウ接続＋助動詞「う」基本形 →「みましょう」
                    elif ((str_class0 == u"動詞") and (form0 == u"未然ウ接続") and (orig0 == u"みる")) \
                            and ((str_class1 == u"助動詞") and (orig1 == u"う")):
                        tmp += u"みましょう"
                        flag = 1

                    # 追加ルール：形容詞「ない」基本形＋助詞「か」 →「ないでしょうか」
                    elif ((str_class0 == u"形容詞") and (form0 == u"基本形") and (orig0 == u"ない")) \
                            and ((str_class1 == u"助詞") and (orig1 == u"か")):
                        tmp += u"ないでしょうか"
                        flag = 1

                if (flag != 1) and (link_flag != 1) and (
                        (i == (len(cab.chunks) - 1) and j == (len(chunk.tokens) - 4)) or (
                        subclass31 == u"接続助詞" and orig4 == u"、")):
                    # ルール4：動詞未然形＋助動詞「ない」連用タ接続＋助動詞「た」基本形 → 動詞連用形 ＋「ませんでした」
                    if ((str_class0 == u"動詞") and (form0 == u"未然形")) \
                            and ((str_class1 == u"助動詞") and (orig1 == u"ない") and (form1 == u"連用タ接続")) \
                            and ((str_class2 == u"助動詞") and (orig2 == u"た") and (form2 == u"基本形")):
                        conv = fc.form_convert(str_class0, conj0, u"連用形", orig0)
                        tmp += conv + u"ませんでした"
                        flag = 1


                    # ルール9：助動詞「だ」連用形＋助動詞「ある」連用タ接続＋助動詞「た」基本形 →「でした」
                    elif ((str_class0 == u"助動詞") and (orig0 == u"だ") and (form0 == u"連用形")) \
                            and ((str_class1 == u"助動詞") and (orig1 == u"ある") and (form1 == u"連用タ接続")) \
                            and ((str_class2 == u"助動詞") and (orig2 == u"た") and (form2 == u"基本形")):
                        tmp += u"でした"
                        flag = 1

                    # ルール10：助動詞「だ」連用形＋助動詞「ある」未然ウ接続＋助動詞「う」基本形 →「でしょう」
                    elif ((str_class0 == u"助動詞") and (orig0 == u"だ") and (form0 == u"連用形")) \
                            and ((str_class1 == u"助動詞") and (orig1 == u"ある") and (form1 == u"未然ウ接続")) \
                            and ((str_class2 == u"助動詞") and (orig2 == u"う") and (form2 == u"基本形")):
                        tmp += u"でしょう"
                        flag = 1

                    # 追加ルール：助動詞「だ」未然形＋助動詞「う」基本形＋助詞「か」 →「でしょうか」
                    elif ((str_class0 == u"助動詞") and (orig0 == u"だ") and (form0 == u"未然形")) \
                            and ((str_class1 == u"助動詞") and (orig1 == u"う") and (form1 == u"基本形")) \
                            and ((str_class2 == u"助詞") and (orig2 == u"か")):
                        tmp += u"でしょうか"
                        flag = 1

                if (flag != 1) and (link_flag != 1) and (
                        (i == (len(cab.chunks) - 1) and j == (len(chunk.tokens) - 5)) or (
                        subclass41 == u"接続助詞" and orig5 == u"、")):
                    # 追加ルール：助動詞「だ」連用形＋助動詞「う」基本形＋助詞「か」 →「でしょうか」
                    if ((str_class0 == u"助動詞") and (orig0 == u"だ") and (form0 == u"連用形")) \
                         and ((str_class1 == u"助動詞") and (orig1 == u"ある") and (form1 == u"未然ウ接続")) \
                         and ((str_class2 == u"助動詞") and (orig2 == u"う") and (form2 == u"基本形")) \
                         and ((str_class3 == u"助詞") and (orig3 == u"か")):
                        tmp += u"でしょうか"
                        flag = 1

                # # 追加ルール:動詞連用形＋助詞「て」接続助詞＋動詞「いる」基本形 → 動詞連用形 ＋「ています」
                # if ((str_class0 == u"動詞") and (form0 == u"連用形")) \
                #         and ((str_class1 == u"助詞") and (orig1 == u"て") and (form1 == u"接続助詞")) \
                #         and ((str_class2 == u"動詞") and (orig2 == u"いる") and (form2 == u"基本形")):
                #     conv = fc.form_convert(str_class0, conj0, u"動詞連用形", orig0)
                #     tmp += conv + u"ています"
                #     flag = 1

                # ルール12：接続詞「だが」「が」→「です(が)」
                if (flag != 1) and (subclass01 == u"接続助詞") and ((orig0 == u"だが") or (orig0 == u"が")) and (
                        orig1 == u"、"):
                    tmp += u"です"

                if (flag == 0) or (flag == 3):
                    tmp += str_tmp0
                if flag == 2:
                    flag = 0

            elif (subclass01 == u"接続助詞") or ((flag == 3) and (j == (len(chunk.tokens) - 2))):
                tmp += str_tmp0
                flag = 0

            elif flag == 3:
                tmp += str_tmp0

    # 変換を行ったかを表すフラグも返す
    # 返すtmpには句点を含まない
    return tmp, flag


def check_year(str_year, base_year):
    '''年 str_yearが過去か未来か調べる'''

    year = datetime.now().year  # 現在の年
    if str_year < 100:  # 省略されている場合
        str_year += base_year
    year_dif = str_year - year  # 差を計算

    if year_dif < 0:  # 対象の年＜現在の年：過去
        return "past"
    else:  # 対象の年＞現在の年：未来
        return "present"


def check_baseYear(sent):
    '''文章中の省略された基準年を調べる'''

    cab = cw.CaboChaWrapper(constants.CHAR_CODE)
    cab.parse(sent, True)

    base_year = 2000
    for i, chunk in enumerate(cab.chunks):
        for j, token in enumerate(chunk.tokens):
            orig0 = token.features["orig"]  # 原形
            subclass01 = token.features["subclass1"]  # 品詞細分類1
            str_tmp0 = token.surface  # 表層文字列
            if j < (len(chunk.tokens) - 1):
                orig1 = chunk.tokens[j + 1].features["orig"]  # 1つ次の原形

            # 文中に「～年」という記述があった場合、
            if (subclass01 == "数") and (orig0 == "*") and (orig1 == "年"):
                y = int(str_tmp0)
                if 1900 <= y and y < 2000:
                    base_year = 1900
                if 1800 <= y and y < 1900:
                    base_year = 1800

    return base_year


def check_tense(sent):
    '''文章の時制を調べる'''

    cab = cw.CaboChaWrapper(constants.CHAR_CODE)
    cab.parse(sent, True)

    past = 0  # 過去を表す文の数
    orig1 = ""
    sent_num = len(sent.split("。")) - 1  # 文章中の文の数
    for i, chunk in enumerate(cab.chunks):
        for j, token in enumerate(chunk.tokens):
            str_class0 = token.features["class"]  # 品詞
            form0 = token.features["form"]  # 活用形
            orig0 = token.features["orig"]  # 原形
            if j < (len(chunk.tokens) - 1):
                orig1 = chunk.tokens[j + 1].features["orig"]  # 1つ次の原形
            else:
                orig1 = ""

            if orig1 == "。":  # 文末について
                # 助動詞「た」基本形で終わる場合、過去形とみなす
                if (str_class0 == u"助動詞") and (orig0 == u"た") and (form0 == u"基本形"):
                    past += 1
                # 記号(括弧など)で終わる場合、時制なしとみなす
                if (str_class0 == u"名詞") or (str_class0 == u"記号"):
                    sent_num -= 1

    # 現在形の文の数を計算
    present = sent_num - past
    # print("present", present)
    # print("past   ", past)

    # 現在形、過去形のうち多い方を文章の時制として返す
    if past >= present:
        return "past"
    else:
        return "present"


def complement_end(sent, tense, base_year):
    '''体言止めを補完
         sent     ：文章
         tense　　：時制
         base_year：基準年
    '''

    cab = cw.CaboChaWrapper(constants.CHAR_CODE)
    cab.parse(sent, True)
    flag = 0
    dnbn = 0  # 伝聞のフラグ

    end_dict = {"sahen": {"present": "します", "past": "しました"},
                "other": {"present": "です", "past": "でした"}}
    past_word = ["前年", "去年", "昨年", "年前"]

    tmp = ""
    for i, chunk in enumerate(cab.chunks):
        for j, token in enumerate(chunk.tokens):
            str_class0 = token.features["class"]  # 品詞
            orig0 = token.features["orig"]  # 原形
            subclass01 = token.features["subclass1"]  # 品詞細分類1
            subclass02 = token.features["subclass2"]  # 品詞細分類2
            str_tmp0 = token.surface  # 表層文字列
            if j < (len(chunk.tokens) - 1):
                orig1 = chunk.tokens[j + 1].features["orig"]  # 1つ次の原形

            # 文中に「～年」という記述があった場合、時制を調べて更新
            if (subclass01 == "数") and (orig0 == "*") and (orig1 == "年"):
                # tense = check_year(int(str_tmp0))
                tense = check_year(int(str_tmp0), base_year)
                # print("tense1", str_tmp0, tense)

            # 文中に助動詞「た」があった場合、時制を過去にする
            if (str_class0 == u"助動詞") and (orig0 == u"た"):
                tense = "past"
                # print("tense2", tense)

            # 文中に過去を表す単語があった場合、時制を過去にする
            if orig0 in past_word:
                tense = "past"
                # print("tense3", tense)

            # 文中に主語になりうる語句を含むか判定
            # 格助詞のうち主語になるのは「が」「の」のみとする
            if (subclass01 == u"格助詞") and ((str_tmp0 == u"が") or (str_tmp0 == u"の")):
                flag = 1

            if (str_tmp0 == u"によると") or (str_tmp0 == u"よれば") or (str_tmp0 == u"調べでは") or (str_tmp0 == u"調査では"):
                dnbn = 1

            # 文末の助動詞「たい」について
            if ((str_class0 == u"助動詞") and (str_tmp0 == u"たい")) and (i == (len(cab.chunks) - 1)) and (
                    j == (len(cab.chunks[i].tokens) - 2)):
                tmp += str_tmp0 + u"です"

            # 文末の名詞について
            elif ((str_class0 == u"名詞") or (str_class0 == u"形容詞")) and (i == (len(cab.chunks) - 1)) and (
                    j == (len(cab.chunks[i].tokens) - 2)):

                if ((str_tmp0 == u"さん") or (str_tmp0 == u"氏")) and (subclass02 == u"人名"):
                    tmp += str_tmp0
                    continue

                # 「が持たれています」：末尾の体言は「疑い」
                if str_tmp0 == u"疑い":
                    tmp += str_tmp0 + u"が持たれています"

                elif dnbn == 1:
                    tmp += str_tmp0 + u"とのことです"

                # elif subclass01 == u"サ変接続":    # 文末の名詞がサ変接続
                #     if flag == 0:   # 文中に主語になりうる語句を含まない
                #         tmp += str_tmp0 + end_dict["sahen"][tense]
                #     else:           # 文中に主語になりうる語句を含む
                #         tmp += str_tmp0 + end_dict["other"][tense]

                elif subclass01 == u"サ変接続":  # 文末の名詞がサ変接続
                    tmp += str_tmp0 + end_dict["sahen"][tense]
                else:  # 文末の名詞がサ変接続以外
                    if str_class0 == u"形容詞":
                        tense = "present"
                    tmp += str_tmp0 + end_dict["other"][tense]
                flag = 0
            else:
                tmp += str_tmp0

    return tmp


def str_convert3(input_sentence):
    '''文末を次の文につながるように（動詞の連用形+"、"）変換'''

    cab = cw.CaboChaWrapper(constants.CHAR_CODE)
    cab.parse(input_sentence, True)
    tmp = ""

    str_convert = ""
    for i, chunk in enumerate(cab.chunks):
        for j, token in enumerate(chunk.tokens):
            str_class = token.features["class"]  # 品詞
            conj = token.features["conj"]  # 活用の種類
            form = token.features["form"]  # 活用形
            orig = token.features["orig"]  # 原形
            subclass1 = token.features["subclass1"]  # 品詞細分類1
            str_tmp = token.surface  # 表層文字列

            if str_tmp == u"する":
                conj = u"サ変・スル"

            # 文末の動詞について
            if (i == (len(cab.chunks) - 1)) and (j == (len(chunk.tokens) - 1)) and (str_class == u"動詞") and (
                    form == u"基本形"):
                str_convert = tmp + fc.form_convert(str_class, conj, u"連用形", orig)
            # 文末の名詞について
            elif (i == (len(cab.chunks) - 1)) and (j == (len(chunk.tokens) - 1)) and (str_class == u"名詞"):
                if str_tmp == u"とき":
                    tmp += str_tmp
                elif subclass1 == u"一般":
                    str_convert = tmp + str_tmp + "で"
                else:
                    str_convert = tmp + str_tmp + "をして"
            else:
                tmp += str_tmp

        if (i == (len(cab.chunks) - 1)) and (str_convert == u""):
            str_convert = tmp

    return str_convert + u"、"


def convert_sentToDesumasu(period, tense, base_year):
    '''文章の文体をですますに変換
         tense    ：文章の時制
         base_year：文章の基準年
    '''

    # 句点を含む文を渡さないとうまく形態素解析できない
    s, f = str_convert(period + "。")  # 文体変換
    if not s.endswith("。"):  # 句点を補完
        s += "。"

    # 文体変換されていない、かつ括弧で終わらない場合
    if (f != 1) and (not period.endswith("」")) and (not period.endswith(")")):
        # sent2 += complement_end(s, tense)
        result = complement_end(s, tense, base_year)  # 体言止め補完
    else:
        result = s

    return result


if __name__ == "__main__":

    # f = codecs.open('test2.txt', 'r', 'utf-8')
    # sent = f.read()
    # f.close()

    sent = u" 太平洋戦争では商船や漁船、官公庁船などが軍に徴用され、激戦地や戦地への往復航海の任務で7200隻もが戦没していった。遭難者は6万人を超える。戦中に育ち海運業界に長く身を置いてきた私は、遺族らの心の渇きを少しでも癒やせたらとの思いから、あまり語られることのなかった一隻一隻の航跡をたどり、私家本の資料集にまとめ続けている。\n 私は1936年に神戸に生まれた。父が船乗りだった影響で、子供の頃から船が好きだった。就職先に選んだのも川崎汽船。戦争の記憶がまだ生々しかった入社当時、社内報の回顧談では殉難船のことが語られていた。振り返ると、この頃から私の心の中で、知られざる戦史を本にまとめたいという思いが芽生えていたのだろう。\n † † †\n 遺族の思いに報いたい\n 開戦後、国内の商船は戦時海運管理令によって一元管理され、小型の漁船や機帆船の多くが軍に徴用された。大型船は主に輸送業務を、小型船も局地輸送や「人間レーダー」として監視任務などに当たった。民間船はほぼ無防備なため、敵に見つかれば撃沈される。船員の戦死率は4割を超え、約3割とされる軍人を上回った。\n 船員は機密保持を理由に家族にも行き先を知らせることができなかった。こうした経緯から、遺族らは確かな情報を得られないまま、大切な人の死を受け入れざるをえなかったと推測される。こうした方々に少しでも報いられたらとの思いから、定年後、本格的に調査を始めた。\n † † †\n 100点超の資料参照\n 著述の経験などないために、何から手を付けていいか分からない。何より資料をどう入手するかが最大の悩みだった。ヒントは生まれ故郷の「戦没した船と海員の資料館」(神戸市)にあった。\n ここには船名や船影などの資料がたくさん集まっていたのだ。神奈川の自宅から神戸に住む母親に会いに行く折々に、同館に通いデータをもらった。その後、東京・永田町にある日本海事センター海事図書館でも様々な資料が一般公開されていることを知り、足しげく通うことになる。\n 資料を精査していった結果、底本が定まった。まず参照するのは海上労働協会編著「日本商船隊戦時遭難史」(成山堂書店)だ。船舶の一隻一隻について、遭難した年月日、徴用の区別、船名、総トン数、船舶所有者、遭難原因、遭難場所を確認できる。\n ただ、これだけでは船の一生を追い切れない。この本で得られた情報を元に、当時の中央官庁がまとめた開戦初期の船名簿や、戦時被害記録も掲載された林寛司編「戦時日本船名録」(全11巻、戦前船舶研究会)、各船会社の社史などをひもとき、加筆・修正していく。船影も海軍省軍務局編「汽船表(別冊冩眞(しゃしん)帳)」や日本海運集会所編の雑誌「海運」などから探し出す。参考にした資料は100点を超える。\n 例えば最新刊でまとめた「北安丸」の航跡を見てみたい。船主は大東亜海事興業。同社は戦争勃発後、戦没船の引き揚げの緊急性の必要性から民間5社が出資して立ち上げた会社だ。\n 同社は1942年に別会社から北安丸を取得。同船の全長は約47メートル、幅約8メートル、深さ約4メートル、558トンで、同年初から海軍に徴用された。44年9月22日にマレー半島西岸南で敵と交戦し被弾沈没。船員1人が亡くなった。敵艦は英国の攻撃潜水艦「Taurus」だ。\n 船影は未発見のため、同じ寸法の船の写真で代用し、敵艦の艦影は雑誌「世界の艦船」(海人社)から引いてきた。そして遭難した場所にマークを入れた地図も載せた。\n † † †\n まだ全体の3割強\n 調査を開始して10年余り。これまでに2522隻について調べ、まとめた私家本「太平洋戦争に於(お)ける殉難船航跡資料集」は33冊になった。それでもまだ全体の3割強にとどまり、先は長い。\n 私家本だから製本する数に制限があるが、遺族の方々の役に立たなければ意味がない。亡き人を思って訪ねる場所にこの本があればと考え、神戸の資料館や海事図書館、日本殉職船員顕彰会などにお届けしている。私の本から情報を得て喜ばれたという話を時々耳にする。少しでも役に立てたなら望外の喜びだ。\n 80歳ともなり、あと何年生きられるか分からないが、命の続く限り調査を続け、すべての殉難船の航跡をたどりたい。そして、私の本が後生の研究の足がかりになればと思っている。(いがらし・はるひこ=川崎汽船元社員)"
    # sent = " 今後の展開としては、今日18日に予定されている小池知事とIOCのバッハ会長の会談が注目される。小池氏が計画見直しを決断し、組織委もそれを受け入れたとしても、IOCと国際競技連盟(IF)の承認が必要になるためだ。\n 東京大会の準備を指導監督するIOCのコーツ調整委員長(副会長)は計画見直しに不快感を示しているとされる。IOCは選手村を国際交流を深め、平和に寄与する五輪の象徴として重視。東京から遠い長沼ボート場への移転は抵抗が強いとみられる。国際ボート連盟のロラン会長も来日した今月3日、小池知事に現行計画の変更反対を伝えている。\n ただ、IOCやIFは競技会場を整備できず、基本的には開催都市や組織委の要望を受け入れざるを得ない立場だ。22年冬季、24年夏季の招致レースでは立候補都市の撤退に歯止めがかからない。莫大な経費がかかるというマイナスイメージの拡散に気をもむIOCにすれば、都の提案を簡単には退けられない。\n 実際、IOCは過去の大会でも計画変更を受け入れている。\n 12年ロンドン大会では開幕2年前にコスト削減のため、仮設で整備する予定のバドミントンと新体操の会場を選手村から遠く離れた既存施設に変更。リオ大会でも開幕1年2カ月前に水球会場の仮設整備を取りやめ、既存施設に変更した。\n ロンドン大会の会場見直しではIFの合意を得るまでに8カ月以上を要した。それよりも大規模な変更となる東京大会の場合はタフな交渉が待ち受けている。"
    # sent = u" 国会で審議入りした環太平洋経済連携協定(TPP)。発効すれば農業、産業分野だけでなく文学の世界にも影響を与える。小説などの著作権の保護期間が従来の50年から70年に延び、昭和の文豪作品の無料公開が先送りされる可能性が高い。著作権切れ作品を無料公開する団体からは「活用されずに死蔵される作品が増えてしまう」と懸念の声が出ている。\n 「長期間にわたって経済的利益を生む作品はごく少数。そのために他の多くの作品を社会で共有できなくなるのは問題だ」。著作権の切れた作品をネット上で無料公開している電子図書館「青空文庫」の運営に携わる翻訳家の大久保ゆうさんはため息をつく。\n三島も川端も\n 現行制度では小説などは原作者の死後50年で著作権が切れ、翌年から原則自由に利用可能。内容を全文入力してネット上で無料公開したり、新たな装丁を施して文庫で販売したりできる。\n 例えば、1965年に死去した谷崎潤一郎や江戸川乱歩は2015年が没後50年に当たり、今年から作品を自由に使えるようになった。青空文庫は今年の1月1日に谷崎の「春琴抄」や乱歩の「二銭銅貨」を公開した。\n ところが、TPP交渉の結果、著作権の保護期間を米国やEUなど海外の主要国が採用する「70年」に延長することになった。条約が発効すれば、これから死後50年を迎える作家の作品は保護期間が20年上積みされ、自由に使えない。\n 没年が67年の山本周五郎や69年の伊藤整、70年の三島由紀夫、71年の志賀直哉、72年の川端康成など、数年内に著作権が切れるはずだった作家の作品の無料利用は先延ばしになる見通しだ。\n欧米は既に70年\n 青空文庫の大久保さんは、著作権切れ作品について「無料で読めるだけでなく、朗読CDを出したり、新しいコンテンツサービスに活用したりできる」と意義を強調。保護期間延長は「世界の文化に大きな害を与える」と訴える。\n 国会図書館は古い所蔵資料をデジタル化してネットで無料公開する事業を進めている。担当者は「50年を過ぎてネット公開できたものが、館内での閲覧しかできなくなるといった影響が出そうだ」と話す。\n 著作権の保護期間は90年代に欧米の多くの国が70年に延ばした。ただ、日本では「著作権者(遺族を含む)の利益を守るため保護期間を延長すべきだ」「過去の作品を広く社会が活用するためには延長すべきでない」などと主張が対立。文化庁の審議会で議論が繰り返されたが、結論を出せない状態が続いていた。\n TPPは米議会の反対などで早期発効に黄信号がともっているが、発効すればその時点から保護期間は延長される。著作権切れ作品の公開に取り組んできた大阪大の岡島昭浩教授(国語学)は「保護期間が長いと没年を調べにくくなり、作品の利用にも支障が生じやすい。『外圧』のような形で70年に延長されてしまうとすれば残念だ」と話している。\n"
    # sent2 = u"周波数域の関数へ変換して理解を深めるスペクトル解析の基礎となっている。"
    sent2 = u"これらは、どうすれば扱いやすくなるであろうか。"
    # sent2 = convert_sentToDesumasu(sent)
    # sent2_list = convert_sentToDesumasu(sent, check_tense(sent), check_baseYear(sent))
    sent3_list = str_convert(sent2)
    # paragraph_list = split_sentToParagraph(sent)
    # split_sent = re.split('。', sent)
    # print(split_sent)
    # for i in split_sent:
        # print(i)
        # print(str_convert(i+"。")[0])
    # print("----------")
    # for i, sent in enumerate(sent3_list):
    #     print(i)
    #     print(sent)

    # with open("result.txt", "w") as f:
    #     f.write(sent2)
