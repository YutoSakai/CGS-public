import manga109api
from pprint import pprint
import re
#
manga109_root_dir = "/home/yuto/Desktop/lab/Manga109_2017_09_28"
p = manga109api.Parser(root_dir=manga109_root_dir)

# print(p.annotations["HeiseiJimen"]["book"]["pages"]["page"].get(['width']))

page = p.annotations["PrayerHaNemurenai"]["book"]["pages"]["page"]

print(page[2]['@width'])
# tateyoko = "tate"
# kind = "text"+tateyoko
# print(kind)
# tateyoko = "yoko"
# print(kind)


# def str_split_function(str):
#     if str[-1] == '。' or str[-1] == '\n':
#         str = str[:-1]
#     split_str = re.split('[,.、。\n]', str)
#     return split_str
#
# print(str_split_function("文字列に含まれないことが保証されている文字がもしあるなら、対象文字をすべてそれに置換した後に split() をかけることで、複数の文字で区切ることができます。ああああ。"))
# manga109_root_dir = "/home/yuto/Desktop/lab/Manga109_2017_09_28"
# manga109_parse = manga109api.Parser(root_dir=manga109_root_dir)

#
# def auto_komawari():
#     title_list = manga109_parse.books
#     title_page_text_list = []
#     page_text_list = []
#     for i, title in enumerate(title_list):
#         title_page_text_list.append(page_text_list)
#         title_page_text_list[i] = text_read(title)
#         print(title_page_text_list[i])
#
# # def text_read():
# #     text_list = []
# #     for roi in manga109_parse.annotations["ARMS"]["book"]["pages"]["page"][3]["text"]:
# #         print(roi)
# #         text_list.append(roi["#text"])
# #     print(text_list)
# #
# # text_read()
# def text_read(title):
#     page_text_list = []
#     pages = manga109_parse.annotations[title]["book"]["pages"]["page"]
#     for i, page in enumerate(pages):
#         page_text_list.append(list())
#         if page.get('text') == None:
#             page_text_list[i].append([])
#             print("textがないページやで")
#             continue
#         elif type(page["text"]) is dict:
#             page["text"] = [page["text"]]
#         for roi in page["text"]:
#             page_text_list[i].append(roi["#text"])
#             # ['どこへ行きやがった!?', 'ティーザー＝電気ショックによる麻痺銃', 'えーいちょろちょろと', 'あつっ', 'そこだ!', '出て来て正々堂々と戦え!', '!', '私を生捕りにする気!?', '卑怯者っ', 'ティーザー!!', 'やろォ', 'キャア', 'あっまた逃げた', 'わーっ']
#             # こんな感じのリストがappendされる。これがページ数分
#     print(page_text_list)
#     return page_text_list
# #
# if re.match('[0-9][A-Z][a-z]', '3'):
#     print("マッチしたで")

# # print(len(manga109_parse.annotations["ARMS"]["book"]["pages"]["page"]))
# auto_komawari()