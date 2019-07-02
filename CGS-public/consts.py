# -*- coding: utf-8 -*-
from PIL import ImageFont

ROOT_WIDTH = 2000
ROOT_HEIGHT = 1500
WIDTH = 1654
HEIGHT = 1170
MEMORYMAX = 100

# フォントの種類とサイズを指定
FONT = ImageFont.truetype("font/GenEiAntiqueNv5-M.ttf", 30)
FONT_NAME = "font/GenEiAntiqueNv5-M.ttf"
FONT_COLOR = '#000000'

MATERIAL_PATH = "Picture/material"
BACKGROUND_PATH = "Picture/material/background"
BALLOON_PATH = "Picture/material/balloon"
CHARACTER_PATH = "Picture/material/character"
PICTURE_PATH = "Picture/material/picture"
COMPLETE_PATH = "Picture/complete"
NOW_IMAGE_PATH = "Picture/now_image.png"
NOW_IMAGE_DOUBLE_CLICK_PATH = "Picture/now_image_double_click.png"
NOW_IMAGE_CLICK_MOTION_PATH = "Picture/now_image_click_motion.png"

MANGA_109_PATH = "Manga109_2017_09_28"
MANGA_109_IMAGE_PATH = "Manga109_2017_09_28/images"
MANGA_109_ANNOTATION_PATH = "Manga109_2017_09_28/annotations"

TEACHER_HASU_WAIST_LEFT_PATH_LIST = ["angry", "angry1", "angry2",
                                     "joy", "joy1", "joy2",
                                     "normal", "normal1", "normal2",
                                     "sad", "sad1", "sad2",
                                     "surprise", "surprise1", "surprise2"]

PANDA_HASU_WAIST_RIGHT_PATH_LIST = ["angry", "angry1",
                                    "joy", "joy1",
                                    "normal", "normal1",
                                    "sad", "sad1",
                                    "surprise", "surprise1"]

BACKGROUND_PATH_LIST = ["blackboad", "classroom", "fire", "heart", "inspiration",
                        "joy", "lightning", "ray", "romantic", "silent", "suspense"]

# 第 1 章で述べたように信号には、画像や音声などさまざまな種類があり、波
# 形も複雑な場合が多い。これらは、どうすれば扱いやすくなるであろうか。そ
# こで考え出されたのが、信号を簡単な信号に分解して扱う方法である。
# フーリエ解析では、信号を周波数と位相の異なる正弦波と直流に分解し解析
# を行う。これは時間域の関数である信号を、周波数域の関数へ変換して理解を
# 深めるスペクトル解析の基礎となっている。
# 本章ではまず、信号解析の基本であるフーリエ級数について説明する。次に
# フーリエ級数を複素形式で表すことによって、その積分表現であり応用の広い
# フーリエ変換を導き、そのさまざまな特性について学ぶ。