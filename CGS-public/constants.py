#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os

NEWSDATA_FILE = "newsDict.json"
USERDATA_FILE = "userDict.json"
DATA_FILE = "dataDict.json"

'''漫画生成に必要な素材のあるフォルダ'''

OBJ_PATH = os.path.join("", "home", "yuto", "デスクトップ", "lab", "蓑谷慶應テクノモール", "5-object")
KOMIDASHI_POSTER =  os.path.join(OBJ_PATH, "comipo", "ItemImage", u"31.学校", u"貼り紙_01.png")
KOMIDASHI_ILLUST =  os.path.join(OBJ_PATH, "irasutoya", "white_manga_shinbun.png")
USER_PICT = os.path.join("user_pict")
USERDATA_DIR = os.path.join(OBJ_PATH, "user_data")
KTM_DIR = os.path.join(OBJ_PATH, "KeioTechno-Mall")

'''文に関連する定数'''

CHAR_CODE = "utf-8"

# キャラクター1
MAX_NUM_1 = 8     # 1行の最大文字数
# MAX_NUM_1 = 9     # 1行の最大文字数
MAX_LINE_1 = 6    # 1つの吹き出しの最大の行数
MAX_CNUM_BL_1 = MAX_NUM_1 * MAX_LINE_1    # 1つの吹き出しの最大文字数
MAX_CNUM_FRAME_1 = MAX_CNUM_BL_1 * 2      # 1つのコマの最大文字数

# キャラクター2
MAX_NUM_2 = 6     # 1行の最大文字数
# MAX_NUM_2 = 7     # 1行の最大文字数
MAX_LINE_2 = 3    # 1つの吹き出しの最大の行数
MAX_CHARNUM_2 = MAX_NUM_2 * MAX_LINE_2    # 1つの吹き出しの最大文字数

# タイトル
MAX_NUM_TITLE = 12  # 1行の最大文字数
MAX_LINE_TITLE = 4  # 最大行数

COLOR_DEFAULT = "black"
COLOR_TITLE = "blue"
COLOR_ORDER = "blue"

MAX_CHAR = 40
PAGENUM_FONTSIZE = 30
TITLE_FONTSIZE = 50
INFO_FONTSIZE = 40
KOMIDASHI_FONTSIZE = 40
DEFAULT_FONTSIZE = 30
A_FONTSIZE = 35
B_FONTSIZE = 32
C_FONTSIZE = 30

R_TITLE_FONTSIZE = 30
R_NUM_FONTSIZE = 20
R_URL_FONTSIZE = 25

A_RATE = 0.1
B_RATE = 0.3
# A_RATE = 0
# B_RATE = 0

# 記号リスト
SYMBOL = [u'、', u'ー', u'…', u'（', u'）', u'(', u')', u'「', u'」', u'『', u'』', u'!', u'！', u'?', u'？', u'―']
FLIP_HORIZONTAL = [u'。', u'ー', u'～', u'.', u'．']
DEGREE270 = [u'…']
DEGREE90 = [u'（', u'）', u')', u'｢', u'｣', u'「', u'」', u'『', u'』', u'【', u'】', u'-', u'－', u':', u'：', u'⇔', u'―', u'=', u'＝']
LOWER_CASE = [u'ぁ', u'ぃ', u'ぅ', u'ぇ', u'ぉ', u'っ', u'ゃ', u'ゅ', u'ょ', u'ァ', u'ィ', u'ゥ', u'ェ', u'ォ', u'ッ', u'ャ', u'ュ', u'ョ']

'''画像検索のためのAPIキー'''

BING_APIKEY = 'bd90b69d44214fc5b224c40e60588924'

# keio.jp
GOOGLE_APIKEY = "AIzaSyCT4ZGZqThDD-5oGRQ0zDIK6AyuR83Cst0"
CUSTOM_SEARCH_ENGINE = "000190493252649216208:bl7mlrr8t3u"

# ayaka
# GOOGLE_APIKEY = "AIzaSyAGJYcmAKxkhotf1xUgUeCqpd2dhWeD3F4"
# CUSTOM_SEARCH_ENGINE = "000190493252649216208:bl7mlrr8t3u"

'''漫画のサイズ'''

# 生成漫画のサイズ
COMIC_WIDTH = 1075
COMIC_HEIGHT = 797

# 1ページのサイズ
PAGE_WIDTH = 148 * 10
PAGE_HEIGHT = 210 * 10
MERGIN = 30

# UI表示用のサイズ
UI_WIDTH = int(PAGE_WIDTH * 2 / 3.0)
UI_HEIGHT = int(PAGE_HEIGHT / 3.0)

'''漫画の要素の条件'''

CHAR_SIZE = [512, 512]
CHAR_RATE = 0.9
A_CHAR_RATE = CHAR_RATE * 1.2
B_CHAR_RATE = CHAR_RATE * 1.1

BL_SIZE = [366, 488]

PICT_W_BASE = (PAGE_WIDTH - MERGIN * (2 + 1)) / 3
PICT_H_BASE = (PAGE_HEIGHT - MERGIN * (3 + 1)) / 3
