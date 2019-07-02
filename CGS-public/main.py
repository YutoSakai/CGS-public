# -*- coding: utf-8 -*-
import sys, os.path
from consts import *
import tkinter as tk
from tkinter import filedialog as tkFileDialog
import str_convert as sc
from tkinter import *
from PIL import Image, ImageDraw
import re
import copy
import pickle
import manga109api
import random as rand
from tategaki import draw_text
import math
from normalize_neologd import normalize_neologd
import time


class Area:
    def __init__(self, start_x, start_y, end_x, end_y):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y

    def area(self):
        return self.start_x, self.start_y, self.end_x, self.end_y

    def start_point(self):  # クリックした座標
        return self.start_x, self.start_y

    def end_point(self):    # マウス離した座標
        return self.end_x, self.end_y

    def lu(self):   # 枠の左上
        return min(self.start_x, self.end_x), min(self.start_y, self.end_y)

    def rd(self):   # 枠の右下
        return max(self.start_x, self.end_x), max(self.start_y, self.end_y)

    def width(self):
        return int(abs(self.start_x - self.end_x))

    def height(self):
        return int(abs(self.start_y - self.end_y))

    def vector(self):
        return int(self.end_x - self.start_x), int(self.end_y - self.start_y)

    def center_point(self):
        return int((self.rd()[0] - self.lu()[0])/2)+self.lu()[0], int((self.rd()[1] - self.lu()[1])/2)+self.lu()[1]

    def center_distance(self, target_point):
        return math.sqrt(abs(target_point[0]-self.center_point()[0])**2 + abs(target_point[1]-self.center_point()[1])**2)


    def S(self):
        return self.width() * self.height()


class Element:
    def __init__(self, filename, area, kind, fontsize=FONT.size):   # テキストの場合はfilenameにテキストの内容が入る
        self.filename = filename
        self.area = area
        self.kind = kind
        self.fontsize = fontsize

    def include(self, point):
        return self.area.lu()[0] <= point[0] <= self.area.rd()[0] and self.area.lu()[1] <= point[1] <= self.area.rd()[1]

    def width_len_line(self):
        return self.area.width() // self.fontsize

    def height_len_line(self):
        return self.area.height() // self.fontsize

    @staticmethod
    def insert_enter(target_string, insert_interval):
        return_string = ""
        for num in range(0, len(target_string), insert_interval):
            return_string = return_string + target_string[num:num+insert_interval] + "\n"
        return return_string

    def show_element(self, canvas, koma):
        if self.kind == "texttate" or self.kind == "textyoko":
            # ImageDraw.Draw(canvas).text((self.area.lu()), self.filename,
            #                             font=ImageFont.truetype(FONT_NAME, self.fontsize), fill=(0, 0, 0))
            if self.kind == "texttate":
                draw_text(canvas, self.fontsize, FONT_NAME, self.filename, self.area.rd()[0], self.area.lu()[1],
                          '#000000', self.kind)
            else:
                draw_text(canvas, self.fontsize, FONT_NAME, self.filename, self.area.lu()[0], self.area.lu()[1],
                          '#000000', self.kind)
            return
        insert_pic = Image.open(self.filename, "r")
        if self.kind == "pic":
            re_insert_pic = insert_pic.resize((self.area.width(), self.area.height()))
            canvas.paste(re_insert_pic, (self.area.lu()))
        elif self.kind == "character" or self.kind == "balloon":
            if self.kind == "character":
                resize_height = self.area.height()
                resize_width = int(self.area.height() * insert_pic.width / insert_pic.height)
            else:
                resize_height = self.area.height()
                resize_width = self.area.width()
            re_insert_pic = insert_pic.resize((resize_width, resize_height))
            lux, luy = copy.deepcopy(self.area.lu())
            self.area.start_x = lux
            self.area.start_y = luy
            self.area.end_x = lux + resize_width
            self.area.end_y = luy + resize_height
            lux, luy = copy.deepcopy(self.area.lu())
            rdx, rdy = copy.deepcopy(self.area.rd())
            if koma.include(self.area.lu()) and koma.include(self.area.rd()):    # コマ内に範囲が含まれていたらトリミングしない
                crop_lux, crop_luy = 0, 0
            else:
                crop_lux = max(lux, koma.area.lu()[0]) - lux
                crop_luy = max(luy, koma.area.lu()[1]) - luy
                crop_rdx = min(rdx, koma.area.rd()[0]) - lux
                crop_rdy = min(rdy, koma.area.rd()[1]) - luy
                re_insert_pic = re_insert_pic.crop((crop_lux, crop_luy, crop_rdx, crop_rdy))
                # コマの枠を消さないためのif文
                if crop_lux > 0:
                    lux += 1
                if crop_luy > 0:
                    luy += 1
                if crop_rdx < self.area.width():
                    lux -= 1
                if crop_rdy < self.area.height():
                    luy -= 1
            canvas.paste(re_insert_pic, (crop_lux + lux, crop_luy + luy), re_insert_pic.split()[3])
        elif self.kind == "background":
            if self.area.width() / self.area.height() <= insert_pic.width / insert_pic.height:
                # print("縦長やで")
                crop_insert_pic = insert_pic.crop(
                    ((insert_pic.width - (self.area.width() * insert_pic.height / self.area.height())) / 2,
                     0,
                     (insert_pic.width + (self.area.width() * insert_pic.height / self.area.height())) / 2,
                     insert_pic.height))
                re_insert_pic = crop_insert_pic.resize((self.area.width(), self.area.height()))
            else:
                # print("横長やで")
                crop_insert_pic = insert_pic.crop(
                    (0,
                     insert_pic.height - (self.area.height() * insert_pic.width / self.area.width()),
                     insert_pic.width,
                     insert_pic.height))
                re_insert_pic = crop_insert_pic.resize((self.area.width(), self.area.height()))
            ImageDraw.Draw(re_insert_pic).rectangle((0, 0, re_insert_pic.width-1, re_insert_pic.height-1),
                                                    outline=(0, 0, 0))
            ImageDraw.Draw(re_insert_pic).rectangle((1, 1, re_insert_pic.width - 2, re_insert_pic.height - 2),
                                                    outline=(0, 0, 0))
            canvas.paste(re_insert_pic, (self.area.lu()))


class Koma:
    def __init__(self, area):
        self.elements = list()
        self.area = area

    def show_koma(self, canvas):
        for element in self.elements:
            element.show_element(canvas, self)

    def include(self, point):
        return self.area.lu()[0] <= point[0] <= self.area.rd()[0] and self.area.lu()[1] <= point[1] <= self.area.rd()[1]


class Page:
    def __init__(self):
        self.komas = list()

    def show_page(self, canvas):
        for koma in self.komas:
            koma.show_koma(canvas)


class Memory:
    def __init__(self):
        self.states = list()
        self.next_index = 0     # 次入れるべき位置

    def redo(self, state):
        if self.next_index < len(self.states):  # next_indexが最新より昔を指していたら
            state = copy.deepcopy(self.states[self.next_index])     # next_indexの状態をreturn
            self.next_index += 1            # next_indexをインクリメント
        return state    # next_indexが最新を指していた場合、最新の状態をreturn

    def push(self, state):
        if self.next_index < len(self.states):  # next_indexが最新より昔を指していたら、next_index以降の記憶を削除
            del(self.states[self.next_index: -1])
        self.states.append(copy.deepcopy(state))    # next_indexのところに現在のstateを追加
        self.next_index += 1    # next_indexをインクリメント

    def undo(self, state):
        if self.next_index < 1:     # next_indexが0のときは起こってはいけない
            print("next_indexは初期化でshow()してない場合以外は0にならんで")
            return state
        elif self.next_index == 1:      # next_indexが1のときは初期状態なのでそれ以下にならないよう初期状態をstateにreturn
            return copy.deepcopy(self.states[self.next_index - 1])
        self.next_index -= 1    # next_indexが2以上のときは指すnext_indexをデクリメント、その一個前の状態をstateにreturn
        return copy.deepcopy(self.states[self.next_index - 1])


class CGS:
    def __init__(self):
        self.memory = Memory()
        self.current_state = list()
        self.current_state.append(Page())
        self.select_element = (0, -1, -1)
        self.font = FONT
        self.tateyoko = "tate"
        self.now_img = Image.new('RGB', (WIDTH, HEIGHT), (255, 255, 255))
        self.now_img.save(NOW_IMAGE_PATH, 'PNG', quality=100)
        self.mouse_select = Area(0, 0, 0, 0)
        self.path_name = ""
        self.root = tk.Tk()
        self.root.option_add('*font', 'FixedSys 10')
        self.root.title("漫画生成支援システム")
        self.root.geometry(str(ROOT_WIDTH)+"x"+str(ROOT_HEIGHT))
        self.menubar = Menu(self.root)
        self.file = Menu(self.menubar, tearoff=False)
        self.edit = Menu(self.menubar, tearoff=False)
        self.im = tk.PhotoImage(file=NOW_IMAGE_PATH)
        self.frame_menu_1 = tk.LabelFrame(self.root, bd=2, relief="ridge", text="menu1")
        self.frame_text = tk.LabelFrame(self.root, bd=2, relief="ridge", text="テキスト")
        self.frame_picture = tk.LabelFrame(self.root, bd=2, relief="ridge", text="Picture", width=WIDTH, height=HEIGHT)
        self.scroll_len = 0
        self.canvas = Canvas(self.frame_picture, width=self.now_img.width, height=self.now_img.height,
                             scrollregion=(0, 0, self.now_img.width, self.now_img.height))
        self.xscroll = Scrollbar(self.frame_picture, orient=HORIZONTAL, command=self.canvas.xview)
        self.xscroll.grid(row=1, column=0, sticky=E + W)
        self.yscroll = Scrollbar(self.frame_picture, orient=VERTICAL, command=self.canvas.yview)
        self.yscroll.grid(row=0, column=1, sticky=N + S)
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor=NW, image=self.im)
        self.text_before_widget = tk.Text(self.frame_text, font=20, height=14, width=90)
        # self.text_after_widget = tk.Text(self.frame_text, font=20, height=14, width=90)
        self.manga109_root_dir = MANGA_109_PATH
        self.manga109_parse = manga109api.Parser(root_dir=self.manga109_root_dir)
        self.show()

    @staticmethod
    def str_split_function(string):
        string = normalize_neologd(string)
        # print(string)
        # string = string.strip()
        # print(string)
        if string[-1] == '。' or string[-1] == '\n':
            string = string[:-1]
        split_str = re.split('[,.、。\n]', string)
        return split_str

    def auto_komawari(self):
        text = self.text_before_widget.get('1.0', 'end -1c')
        text = text.replace("\n", "")
        text = text.replace("\\n", "")
        if text == "":
            return
        font_size = 30
        min_score = 1e10
        min_title = ""
        min_page = -1
        text_list = self.str_split_function(text)
        for text_num, text in enumerate(text_list):
            text_list[text_num] = self.str_convert_function(text + "。")
            if text_list[text_num][-1] == '。':
                text_list[text_num]= text_list[text_num][:-1]
        print(text_list)
        title_list = self.manga109_parse.books
        for title in title_list:
            for page_num, square_list in enumerate(self.square_read(title)):
                if len(square_list) != len(text_list):
                    continue
                score = 0
                for j in range(len(text_list)):
                    score += pow(len(text_list[j]) * pow(font_size, 2) - square_list[j], 2)
                if score < min_score:
                    min_score = score
                    min_title = title
                    min_page = page_num

        print("score = ", min_score, ", title = ", min_title, ", page_num = ", min_page)
        if min_page == -1:
            print("長すぎ")
        else:
            self.imitate_page(min_title, min_page, False, text_list)

    def text_read(self, title):
        page_text_list = []
        pages = self.manga109_parse.annotations[title]["book"]["pages"]["page"]
        for i, page in enumerate(pages):
            page_text_list.append(list())
            if page.get('text') == None:
                page_text_list[i].append([])
                # print("textがないページやで")
                continue
            elif type(page["text"]) is dict:
                page["text"] = [page["text"]]
            for roi in page["text"]:
                page_text_list[i].append(roi["#text"])
                # ['どこへ行きやがった!?', 'ティーザー＝電気ショックによる麻痺銃', 'えーいちょろちょろと', 'あつっ', 'そこだ!', '出て来て正々堂々と戦え!', '!', '私を生捕りにする気!?', '卑怯者っ', 'ティーザー!!', 'やろォ', 'キャア', 'あっまた逃げた', 'わーっ']
                # こんな感じのリストがappendされる。これがページ数分
        return page_text_list

    def square_read(self, title):
        page_S_list = []
        pages = self.manga109_parse.annotations[title]["book"]["pages"]["page"]
        for i, page in enumerate(pages):
            page_S_list.append(list())
            if page.get('text') == None:
                page_S_list[i].append([])
                # print("textがないページやで")
                continue
            elif type(page["text"]) is dict:
                page["text"] = [page["text"]]
            for roi in page["text"]:
                frame = Area(roi["@xmin"], roi["@ymin"], roi["@xmax"], roi["@ymax"])
                page_S_list[i].append(frame.S())
        return page_S_list

    @staticmethod
    def insert_enter(target_string, insert_interval):
        return_string = ""
        for num in range(0, len(target_string), insert_interval):
            return_string = return_string + target_string[num:num+insert_interval] + "\n"
        return return_string

    @staticmethod
    def end_function():
        elapsed_time_min = int(time.time() - start_time - 6) // 60
        elapsed_time_sec = int(time.time() - start_time - 6) % 60
        print("elapsed_time:{0}".format(elapsed_time_min) + "分" + "{0}".format(elapsed_time_sec) + "秒")
        exit()

    def show(self, push_bool=True):
        if push_bool:
            self.memory.push(self.current_state)
        canvas = Image.new('RGB', (WIDTH, HEIGHT + HEIGHT * (len(self.current_state) - 1)), (255, 255, 255))
        for page in self.current_state:
            page.show_page(canvas)
        canvas.save(NOW_IMAGE_PATH, 'PNG', quality=100)
        self.im["file"] = NOW_IMAGE_PATH
        self.canvas.itemconfig(self.image_on_canvas, image=self.im)
        self.canvas["scrollregion"] = (0, 0, canvas.width, canvas.height)
        return canvas

    def scroll_len_function(self):
        now_image = Image.open(NOW_IMAGE_PATH)
        self.scroll_len = int(now_image.height * self.yscroll.get()[0])

    def file_open_function(self):
        open_filename = tkFileDialog.askopenfilename(filetypes=[('Image Files', '.png')], initialdir=COMPLETE_PATH)
        if open_filename == "":
            return
        open_text_filename = open_filename[:-4] + '.txt'
        data_file = open(open_text_filename, 'rb')
        self.memory = pickle.load(data_file)
        self.current_state = self.memory.undo(self.current_state)
        for i in self.memory.states:
            self.current_state = self.memory.redo(self.current_state)
        self.show(False)

    def save_function(self):
        save_filename = tkFileDialog.asksaveasfilename(filetypes=[('Image Files', '.png')], initialdir=COMPLETE_PATH)
        if save_filename == "":
            return
        self.path_name = os.path.dirname(save_filename)
        now_image = Image.open(NOW_IMAGE_PATH)
        now_image.save(save_filename, 'PNG', quality=100)
        save_txt_filename = save_filename[:-4] + '.txt'
        data_file = open(save_txt_filename, 'wb')
        pickle.dump(self.memory, data_file)

    def undo_function(self):
        self.current_state = self.memory.undo(self.current_state)
        self.show(False)

    def redo_function(self):
        self.current_state = self.memory.redo(self.current_state)
        self.show(False)

    def width_len_line(self):
        return self.mouse_select.width() // self.font.size

    def height_len_line(self):
        return self.mouse_select.height() // self.font.size

    def click_press_function(self, event):
        self.scroll_len_function()
        self.mouse_select.start_x = event.x
        self.mouse_select.start_y = event.y + self.scroll_len

    def click_release_function(self, event):
        self.scroll_len_function()
        self.mouse_select.end_x = event.x
        self.mouse_select.end_y = event.y + self.scroll_len

    def double_click_function(self, event):
        page_index, koma_index, element_index = self.select_element_function()
        self.select_element = page_index, koma_index, element_index
        element = self.current_state[page_index].komas[koma_index].elements[element_index]
        if koma_index == -1 or element_index == -1:
            return
        # print(self.select_element)
        canvas = Image.open(NOW_IMAGE_PATH)
        ImageDraw.Draw(canvas).rectangle((element.area.area()), outline=(255, 0, 0))
        canvas.save(NOW_IMAGE_DOUBLE_CLICK_PATH, 'PNG', quality=100)
        self.im["file"] = NOW_IMAGE_DOUBLE_CLICK_PATH
        self.canvas.itemconfig(self.image_on_canvas, image=self.im)
        self.canvas["scrollregion"] = (0, 0, canvas.width, canvas.height)

        if element.kind == "texttate" or element.kind == "textyoko":
            self.text_before_widget.delete(1.0, tk.END)
            self.text_before_widget.insert(tk.END, element.filename.replace('\n', ''))

    def click_motion_function(self, event):
        canvas = Image.open(NOW_IMAGE_PATH)
        ImageDraw.Draw(canvas).rectangle((min(event.x, self.mouse_select.start_x),
                                          min(event.y + self.scroll_len, self.mouse_select.start_y),
                                          max(event.x, self.mouse_select.start_x),
                                          max(event.y + self.scroll_len, self.mouse_select.start_y)), outline=(0, 0, 255))
        ImageDraw.Draw(canvas).line((self.mouse_select.start_x,
                                     self.mouse_select.start_y,
                                     event.x,
                                     event.y + self.scroll_len,), fill=(0, 255, 0), width=2)
        canvas.save(NOW_IMAGE_CLICK_MOTION_PATH, 'PNG', quality=100)
        self.im["file"] = NOW_IMAGE_CLICK_MOTION_PATH
        self.canvas.itemconfig(self.image_on_canvas, image=self.im)
        self.canvas["scrollregion"] = (0, 0, canvas.width, canvas.height)

    def select_element_function(self):
        mouse_select = copy.deepcopy(self.mouse_select)
        page_index = mouse_select.start_y // HEIGHT
        koma_index = self.koma_index(mouse_select)
        element_index = -1
        for j, element in enumerate(self.current_state[page_index].komas[koma_index].elements):
            if element.include(mouse_select.start_point()):
                element_index = j

        return page_index, koma_index, element_index

    @staticmethod
    def str_convert_function(text):
        insert_text = ""
        split_sent = re.split('。', text)
        for i in split_sent:
            # print(i+"。")
            if i != "\n":
                # print(sc.str_convert(i + "。")[0])
                if sc.str_convert(i + "。")[0][-1] == "。" or sc.str_convert(i + "。")[0][-1] == "\n":
                    insert_text += sc.str_convert(i+"。")[0]
                else:
                    insert_text += sc.str_convert(i+"。")[0]+"。"
        if insert_text[-1] == '。':
            insert_text = insert_text[:-1]
        return insert_text

    # def text_convert_function(self):
    #     text = self.text_before_widget.get('1.0', 'end -1c')
    #     insert_text = self.str_convert_function(text)
    #     self.text_after_widget.insert(tk.END, insert_text)

    def text_move_function(self):
        page_index, koma_index, element_index = self.select_element
        mouse_select = copy.deepcopy(self.mouse_select)
        if koma_index == -1 or element_index == -1:     # もしコマが選択されていなかったら
            return
        elements = self.current_state[page_index].komas[koma_index].elements
        print(elements[element_index].filename)
        text = copy.deepcopy(elements[element_index].filename).replace("\n", "")
        print(text)
        elements.pop(element_index)
        self.font_decide_function(mouse_select.width(), mouse_select.height(), text)
        insert_text = self.insert_enter(text, (mouse_select.height() // self.font.size))
        print(insert_text)
        elements.append(Element(insert_text, mouse_select, "texttate", self.font.size))
        self.show()

    def element_function(self, option):
        page_index, koma_index, element_index = self.select_element
        mouse_select = copy.deepcopy(self.mouse_select)
        if koma_index == -1 or element_index == -1:     # もしコマが選択されていなかったら
            return
        if option == "koma_delete":
            self.current_state[page_index].komas.pop(koma_index)
        elif option == "koma_to_head":
            head = copy.deepcopy(self.current_state[page_index].komas[koma_index])
            self.current_state[page_index].komas.pop(koma_index)
            self.current_state[page_index].komas.append(head)
        elif option == "koma_move":
            # print("マウスセレクトエリア")
            # print(mouse_select.area())
            # print("マウスセレクトベクトル")
            # print(mouse_select.vector())
            self.current_state[page_index].komas[koma_index].area.start_x += mouse_select.vector()[0]
            self.current_state[page_index].komas[koma_index].area.start_y += mouse_select.vector()[1]
            self.current_state[page_index].komas[koma_index].area.end_x += mouse_select.vector()[0]
            self.current_state[page_index].komas[koma_index].area.end_y += mouse_select.vector()[1]
            # print("コマエリア")
            # print(self.pages.pages[page_index].komas[koma_index].area.area())
            for j, element in enumerate(self.current_state[page_index].komas[koma_index].elements):
                if element.kind == "background":
                    self.current_state[page_index].komas[koma_index].elements[j].area.start_x = \
                        self.current_state[page_index].komas[koma_index].area.start_x
                    self.current_state[page_index].komas[koma_index].elements[j].area.start_y = \
                        self.current_state[page_index].komas[koma_index].area.start_y
                    self.current_state[page_index].komas[koma_index].elements[j].area.end_x = \
                        self.current_state[page_index].komas[koma_index].area.end_x
                    self.current_state[page_index].komas[koma_index].elements[j].area.end_y = \
                        self.current_state[page_index].komas[koma_index].area.end_y
                    # print("背景エリア")
                    # print(self.pages.pages[page_index].komas[koma_index].elements[j].area.area())
                    continue
                else:
                    self.current_state[page_index].komas[koma_index].elements[j].area.start_x += mouse_select.vector()[0]
                    self.current_state[page_index].komas[koma_index].elements[j].area.start_y += mouse_select.vector()[1]
                    self.current_state[page_index].komas[koma_index].elements[j].area.end_x += mouse_select.vector()[0]
                    self.current_state[page_index].komas[koma_index].elements[j].area.end_y += mouse_select.vector()[1]
                # print("エレメントエリア")
                # print(self.pages.pages[page_index].komas[koma_index].elements[j].area.area())
        elif option == "koma_size_change":
            self.current_state[page_index].komas[koma_index].area.start_x = mouse_select.start_x
            self.current_state[page_index].komas[koma_index].area.start_y = mouse_select.start_y
            self.current_state[page_index].komas[koma_index].area.end_x = mouse_select.end_x
            self.current_state[page_index].komas[koma_index].area.end_y = mouse_select.end_y
        elif option == "element_delete":
            self.current_state[page_index].komas[koma_index].elements.pop(element_index)
        elif option == "element_to_head":
            head = copy.deepcopy(self.current_state[page_index].komas[koma_index].elements[element_index])
            self.current_state[page_index].komas[koma_index].elements.pop(element_index)
            self.current_state[page_index].komas[koma_index].elements.append(head)
        elif option == "element_change":
            change_filename = tkFileDialog.askopenfilename(filetypes=[('Image Files', '.png')],
                                                           initialdir=MATERIAL_PATH)
            if change_filename == "":  # キャンセルならリターン
                return
            self.current_state[page_index].komas[koma_index].elements[element_index].filename = change_filename
        elif option == "element_move":
            # print(mouse_select.area())
            # print(mouse_select.vector())
            self.current_state[page_index].komas[koma_index].elements[element_index].area.start_x += mouse_select.vector()[0]
            self.current_state[page_index].komas[koma_index].elements[element_index].area.start_y += mouse_select.vector()[1]
            self.current_state[page_index].komas[koma_index].elements[element_index].area.end_x += mouse_select.vector()[0]
            self.current_state[page_index].komas[koma_index].elements[element_index].area.end_y += mouse_select.vector()[1]
        elif option == "element_size_change":
            self.current_state[page_index].komas[koma_index].elements[element_index].area.start_x = mouse_select.start_x
            self.current_state[page_index].komas[koma_index].elements[element_index].area.start_y = mouse_select.start_y
            self.current_state[page_index].komas[koma_index].elements[element_index].area.end_x = mouse_select.end_x
            self.current_state[page_index].komas[koma_index].elements[element_index].area.end_y = mouse_select.end_y

        self.show()

    def koma_delete_function(self):
        self.element_function("koma_delete")

    def koma_to_head_function(self):
        self.element_function("koma_to_head")

    def koma_move_function(self):
        self.element_function("koma_move")

    def koma_size_change_function(self):
        self.element_function("koma_size_change")
        
    def element_delete_function(self):
        self.element_function("element_delete")

    def element_to_head_function(self):
        self.element_function("element_to_head")

    def element_change_function(self):
        self.element_function("element_change")

    def element_move_function(self):
        self.element_function("element_move")

    def element_size_change_function(self):
        self.element_function("element_size_change")

    def text_tategaki_function(self):
        self.tateyoko = "tate"

    def text_yokogaki_function(self):
        self.tateyoko = "yoko"

    def insert_function(self, kind):
        if kind == "background":
            insert_filename = tkFileDialog.askopenfilename(filetypes=[('Image Files', '.png')],
                                                           initialdir=BACKGROUND_PATH)
        elif kind == "pic":
            insert_filename = tkFileDialog.askopenfilename(filetypes=[('Image Files', '*.png ; *.jpg ; *.JPG' )],
                                                           initialdir=PICTURE_PATH)
        elif kind == "character":
            insert_filename = tkFileDialog.askopenfilename(filetypes=[('Image Files', '.png')],
                                                           initialdir=CHARACTER_PATH)
        elif kind == "balloon":
            insert_filename = tkFileDialog.askopenfilename(filetypes=[('Image Files', '.png')],
                                                           initialdir=BALLOON_PATH)
        elif kind == "texttate" or kind == "textyoko":    # insert_filenameにテキストの内容を書き込み
            insert_filename = self.str_convert_function(self.text_before_widget.get('1.0', 'end -1c'))
        else:
            insert_filename = tkFileDialog.askopenfilename(filetypes=[('Image Files', '.png')],
                                                           initialdir=self.path_name)
        if insert_filename == "":   # キャンセルならリターン
            return
        if self.mouse_select.area() == (0, 0, 0, 0):    # マウス選択なしならリターン
            return

        # 今の状態をmemoryにコピー
        # self.memory.push(self.current_state)

        # 以下でself.current_stateを更新

        page_index = self.mouse_select.start_y // HEIGHT
        koma_index = -1
        mouse_select = copy.deepcopy(self.mouse_select)
        if kind == "background":
            self.current_state[page_index].komas.append(Koma(mouse_select))
            koma_index = len(self.current_state[page_index].komas) - 1      # 背景挿入ならコマリストに新たに追加し、koma_indexをそのリスト番号にする
        else:
            for i, koma in enumerate(self.current_state[page_index].komas):     # マウスで選択した範囲にコマがあればそれを選択
                if koma.include(mouse_select.start_point()):
                    koma_index = i
                    break
        if kind == "texttate" or kind == "textyoko":
            self.font_decide_function(mouse_select.width(), mouse_select.height(), insert_filename)
            if kind == "texttate":
                insert_filename = self.insert_enter(insert_filename, self.height_len_line())
            else:
                insert_filename = self.insert_enter(insert_filename, self.width_len_line())
        self.current_state[page_index].komas[koma_index].elements.append(Element(insert_filename, mouse_select, kind, self.font.size))
        self.show()

    def font_decide_function(self, width, height, string):
        font_size = int(math.sqrt(width * height / len(string)))
        if font_size <= 1:
            font_size = 1
        else:
            while (width // font_size) * (height // font_size) < len(string):
                if font_size <= 1:
                    font_size = 1
                    break
                font_size -= 1
        if font_size <= 1:
            font_size = 1
        elif font_size > 400:
            font_size = 400
        self.font = ImageFont.truetype(FONT_NAME, font_size)

    def pic_insert_function(self):
        self.insert_function("pic")

    def text_insert_function(self):
        tateyoko = copy.deepcopy(self.tateyoko)
        self.insert_function("text" + tateyoko)

    def balloon_insert_function(self):
        self.insert_function("balloon")

    def character_insert_function(self):
        self.insert_function("character")

    def background_insert_function(self):
        self.insert_function("background")

    def page_integration_function(self):
        open_filename = tkFileDialog.askopenfilename(filetypes=[('Image Files', '.png')], initialdir=COMPLETE_PATH)
        if open_filename == "":
            return
        open_text_filename = open_filename[:-4] + '.txt'
        data_file = open(open_text_filename, 'rb')
        insert_memory = pickle.load(data_file)      # 挿入するmemory
        insert_current_state = insert_memory.states[-1]    # 挿入するmemoryの最新の記憶
        current_page_num = len(self.current_state)  # 現在のページ数
        for page_index, page in enumerate(insert_current_state):
            for koma_index, koma in enumerate(page.komas):
                for element_index, element in enumerate(koma.elements):
                    element.area.start_y += HEIGHT * (page_index + current_page_num)
                    element.area.end_y += HEIGHT * (page_index + current_page_num)
            self.current_state.append(page)
        self.show(False)

    def new_function(self):
        self.current_state.clear()
        self.current_state.append(Page())
        self.show()

    def koma_index(self, area):
        index = -1
        for j, koma in enumerate(self.current_state[0].komas):
            if koma.include(area.start_point()):
                index = j
                break
        if index == -1:
            for j, koma in enumerate(self.current_state[0].komas):
                if koma.include(area.end_point()):
                    index = j
                    break
        if index == -1:
            print("indexが-1のもの", area.start_point(), area.end_point())

        return index

    def imitate_page(self, title, page_number, only_frame=False, text_list=[]):
        page = self.manga109_parse.annotations[title]["book"]["pages"]["page"][int(page_number)]
        page_height, page_width = page['@height'], page['@width']
        magnification_height = HEIGHT / page_height
        magnification_width = WIDTH / page_width
        expand_num = 30
        text_num = 0
        panda_flag_list = list()
        teacher_flag_list = list()
        for annotation_type in ["frame", "body", "text", "face"]:
            if page.get(annotation_type) is None:
                continue
            elif type(page[annotation_type]) is dict:
                page[annotation_type] = [page[annotation_type]]
            rois = page[annotation_type]

            for i, roi in enumerate(rois):
                kind = {"frame": "background", "body": "character", "text": "balloon", "face": "face"}[annotation_type]
                frame = Area(int(roi["@xmin"]*magnification_width), int(roi["@ymin"]*magnification_height),
                             int(roi["@xmax"]*magnification_width), int(roi["@ymax"]*magnification_height))
                if annotation_type == "frame":
                    panda_flag_list.append(0)
                    teacher_flag_list.append(0)
                    random_num = rand.randint(0, 100) % len(BACKGROUND_PATH_LIST)
                    self.current_state[0].komas.append(Koma(frame))
                    self.current_state[0].komas[i].elements.append(
                        Element(BACKGROUND_PATH + "/" + BACKGROUND_PATH_LIST[random_num] + ".png", frame, kind, self.font.size))
                    if only_frame:
                        continue
                elif annotation_type == "body":
                    koma_index = self.koma_index(frame)

                    if self.current_state[0].komas[koma_index].area.center_point()[0] > frame.center_point()[0] and panda_flag_list[koma_index] == 0:
                        random_num = rand.randint(0, 100) % len(PANDA_HASU_WAIST_RIGHT_PATH_LIST)
                        self.current_state[0].komas[koma_index].elements.append(
                            Element(CHARACTER_PATH + "/pandahasu/waist/right/" + PANDA_HASU_WAIST_RIGHT_PATH_LIST[random_num] + ".png", frame, kind, self.font.size))
                        panda_flag_list[koma_index] = 1
                    elif teacher_flag_list[koma_index] == 0:
                        random_num = rand.randint(0, 100) % len(TEACHER_HASU_WAIST_LEFT_PATH_LIST)
                        self.current_state[0].komas[koma_index].elements.append(
                            Element(CHARACTER_PATH + "/teacherhasu/waist/left/" + TEACHER_HASU_WAIST_LEFT_PATH_LIST[random_num] + ".png", frame, kind, self.font.size))
                        teacher_flag_list[koma_index] = 1
                    else:
                        continue
                elif annotation_type == "text":
                    koma_index = self.koma_index(frame)
                    koma = self.current_state[0].komas[koma_index]
                    if koma_index == -1:
                        self.current_state[0].komas.append(Koma(frame))
                        self.current_state[0].komas[len(self.current_state[0].komas)-1].elements.append(
                            Element(BACKGROUND_PATH + "/white.png", frame, kind,
                                    self.font.size))
                        continue
                    balloon_frame = copy.deepcopy(frame)
                    balloon_frame.start_x -= expand_num
                    balloon_frame.start_y -= expand_num
                    balloon_frame.end_x += expand_num
                    balloon_frame.end_y += expand_num
                    koma.elements.append(
                        Element(BALLOON_PATH + "/center/maru.png", balloon_frame, "balloon", self.font.size))

                    # self.font_decide_function(frame.width(), frame.height(), text_list[text_num])
                    # insert_text = self.insert_enter(text_list[text_num], (frame.height() // self.font.size))
                    # self.current_state[0].komas[koma_index].elements.append(
                    #     Element(insert_text, frame, "texttate", self.font.size))
                    # text_num += 1
                elif annotation_type == "face":
                    continue

        self.current_state[0].komas.sort(key=lambda element: element.area.center_distance(
                                [WIDTH, 0]) if element.area.start_x >= WIDTH / 2
                            else 1e8 + element.area.center_distance([WIDTH / 2, 0]))
        for koma in self.current_state[0].komas:
            koma.elements.sort(key=lambda element: element.area.center_point()[0] if element.kind == "balloon"
                                else 1e8, reverse=True)
        if only_frame:
            print("フレームオンリーやで")
            self.show()
            return

        for koma in self.current_state[0].komas:
            for element in koma.elements:
                if element.kind != "balloon":
                    continue
                frame = copy.deepcopy(element.area)
                frame.start_x += expand_num
                frame.start_y += expand_num
                frame.end_x -= expand_num
                frame.end_y -= expand_num
                lux, luy = copy.deepcopy(frame.lu())
                rdx, rdy = copy.deepcopy(frame.rd())
                if koma.include(frame.lu()) and koma.include(frame.rd()):  # コマ内に範囲が含まれていたらトリミングしない
                    crop = Area(lux, luy, rdx, rdy)
                else:
                    crop = Area(max(lux, koma.area.lu()[0]), max(luy, koma.area.lu()[1]),
                                min(rdx, koma.area.rd()[0]), min(rdy, koma.area.rd()[1]))
                self.font_decide_function(crop.width(), crop.height(), text_list[text_num])
                insert_text = self.insert_enter(text_list[text_num], (frame.height() // self.font.size))
                koma.elements.append(Element(insert_text, crop, "texttate", self.font.size))
                text_num += 1

        for i, koma in enumerate(self.current_state[0].komas):
            for j, element in enumerate(koma.elements):
                if element.kind == "background":
                    element_copy = copy.deepcopy(element)
                    koma.elements.pop(j)
                    koma.elements.insert(0, element_copy)
        self.show()

    def manga109_all_function(self, random=False, only_frame=False):
        if random:
            title = "Donburakokko"
            page_number = rand.randint(2, 50)
            # print("ランダム結果:どんぶらこっこ", page_number, "ページ")
        else :
            open_filename = tkFileDialog.askopenfilename(filetypes=[('Image Files', '.jpg')], initialdir=MANGA_109_IMAGE_PATH)
            if open_filename == "":
                return
            title = os.path.basename(os.path.dirname(open_filename))   # 親ディレクトリ（漫画の名前を取得）
            root_ext_pair = os.path.splitext(open_filename) # ファイル名と拡張子を分ける
            page_number = os.path.basename(root_ext_pair[0])  # ページ数を取得
        self.imitate_page(title, page_number, only_frame)
        # self.show()

    def manga109_all_random_function(self):
        self.manga109_all_function(True)

    def manga109_koma_random_function(self):
        self.manga109_all_function(True, True)

    def manga109_koma_function(self):
        self.manga109_all_function(False, True)

    def GUI(self, start_time):
        # メニューバーを生成
        self.root.configure(menu=self.menubar)
        self.menubar.add_cascade(label="ファイル", underline=0, menu=self.file)
        self.file.add_command(label="新規作成", under=0, command=self.new_function)
        self.file.add_command(label="ファイルを開く", under=0, command=self.file_open_function)
        self.file.add_command(label="既存漫画のコマ配置を取得", under=0, command=self.manga109_koma_function)
        self.file.add_command(label="既存漫画のコマ配置をランダムで取得", under=0, command=self.manga109_koma_random_function)
        self.file.add_command(label="既存漫画の要素配置を取得", under=0, command=self.manga109_all_function)
        self.file.add_command(label="既存漫画の要素配置をランダムで取得", under=0, command=self.manga109_all_random_function)
        self.file.add_command(label="図を挿入", under=0, command=self.pic_insert_function)
        self.file.add_command(label="背景を挿入", under=0, command=self.background_insert_function)
        self.file.add_command(label="キャラクターを挿入", under=0, command=self.character_insert_function)
        self.file.add_command(label="吹き出しを挿入", under=0, command=self.balloon_insert_function)
        self.file.add_command(label="ファイルを保存", under=0, command=self.save_function)
        self.file.add_command(label="ページを統合", under=0, command=self.page_integration_function)
        self.file.add_command(label="終了", under=0, command=self.end_function)
        self.menubar.add_cascade(label="編集", underline=0, menu=self.edit)
        self.edit.add_command(label="Undo", under=0, command=self.undo_function)
        self.edit.add_command(label="Redo", under=0, command=self.redo_function)
        self.edit.add_command(label="コマを削除", under=0, command=self.koma_delete_function)
        self.edit.add_command(label="コマを最前に", under=0, command=self.koma_to_head_function)
        self.edit.add_command(label="コマを移動", under=0, command=self.koma_move_function)
        self.edit.add_command(label="コマの大きさ・場所を変更", under=0, command=self.koma_size_change_function)
        self.edit.add_command(label="要素を削除", under=0, command=self.element_delete_function)
        self.edit.add_command(label="要素をコマ内で最前に", under=0, command=self.element_to_head_function)
        self.edit.add_command(label="要素を変更", under=0, command=self.element_change_function)
        self.edit.add_command(label="要素を移動", under=0, command=self.element_move_function)
        self.edit.add_command(label="要素の大きさ・場所を変更", under=0, command=self.element_size_change_function)
        self.edit.add_command(label="テキストを縦書きにする", under=0, command=self.text_tategaki_function)
        self.edit.add_command(label="テキストを横書きにする", under=0, command=self.text_yokogaki_function)

        # フレーム（メニュー1）1を作成
        self.frame_menu_1.pack(fill="x")
        # self.font_size_widget.pack(side="left")
        # font_size_button = tk.Button(self.frame_menu_1, text="フォントサイズを変更", command=self.font_size_function)
        # font_size_button.pack(side="left")
        undo_button = tk.Button(self.frame_menu_1, text="Undo", command=self.undo_function)
        undo_button.pack(side="left")
        redo_button = tk.Button(self.frame_menu_1, text="Redo", command=self.redo_function)
        redo_button.pack(side="left")
        undo_button = tk.Button(self.frame_menu_1, text="テキストを縦書きにする", command=self.text_tategaki_function)
        undo_button.pack(side="left")
        redo_button = tk.Button(self.frame_menu_1, text="テキストを横書きにする", command=self.text_yokogaki_function)
        redo_button.pack(side="left")
        koma_delete_button = tk.Button(self.frame_menu_1, text="コマを削除", command=self.koma_delete_function)
        koma_delete_button.pack(side="left")
        element_delete_button = tk.Button(self.frame_menu_1, text="要素を削除", command=self.element_delete_function)
        element_delete_button.pack(side="left")
        element_change_button = tk.Button(self.frame_menu_1, text="要素を変更", command=self.element_change_function)
        element_change_button.pack(side="left")
        element_move_button = tk.Button(self.frame_menu_1, text="要素を移動", command=self.element_move_function)
        element_move_button.pack(side="left")
        element_size_change_button = tk.Button(self.frame_menu_1, text="要素領域変更", command=self.element_size_change_function)
        element_size_change_button.pack(side="left")
        end_button = tk.Button(self.frame_menu_1, text="終了", command=self.end_function)
        end_button.pack(side="right")

        # フレーム2を作成(テキスト)
        self.frame_text.pack(fill="x")

        # 変換前テキストエリアを設定
        self.text_before_widget.pack(side="left")

        # # フレーム2に語尾変換ボタンを配置
        # text_convert_button = tk.Button(self.frame_text, text="語尾変換", command=self.text_convert_function)
        # text_convert_button.pack(side="left")


        # # 変換後テキストエリアを設定
        # self.text_after_widget.pack(side="left")

        # フレーム2にテキスト挿入ボタンを配置
        text_insert_button = tk.Button(self.frame_text, text="テキスト挿入", command=self.text_insert_function)
        text_insert_button.pack(side="left")
        auto_komawari_button = tk.Button(self.frame_text, text="コマセリフ自動配置", command=self.auto_komawari)
        auto_komawari_button.pack(side="left")
        text_move_button = tk.Button(self.frame_text, text="セリフ再配置", command=self.text_move_function)
        text_move_button.pack(side="left")
        text_area_delete_button = tk.Button(self.frame_text, text="テキストエリアをクリア",
                                            command=lambda: self.text_before_widget.delete(1.0, tk.END))
        text_area_delete_button.pack(side="left")

        # スクロールバー関連
        self.canvas.config(xscrollcommand=self.xscroll.set, yscrollcommand=self.yscroll.set)
        self.canvas.grid(row=0, column=0, sticky=N + E + W + S)

        self.canvas.bind("<ButtonPress-1>", lambda e: self.canvas.scan_mark(e.x, e.y))
        self.canvas.bind("<B1-Motion>", lambda e: self.canvas.scan_dragto(e.x, e.y, gain=1))
        self.canvas.bind("<Button-1>", self.click_press_function)
        self.canvas.bind("<ButtonRelease-1>", self.click_release_function)
        self.canvas.bind("<Double-Button-1>", self.double_click_function)
        self.canvas.bind("<B1-Motion>", self.click_motion_function)
        # self.yscroll.bind('<MouseWheel>', lambda e: self.canvas.yview_scroll(-1 * (1 if e.delta > 0 else -1), UNITS))
        # self.yscroll.bind('<Enter>', lambda e: self.yscroll.focus_set())
        # self.canvas.bind('<Enter>', lambda e: self.yscroll.focus_set())       # マウスホイールでスクロールしたい。

        # フレーム3を作成(画像)
        self.frame_picture.pack()

        self.root.mainloop()


if __name__ == '__main__':
    start_time = time.time()    #起動時間計測用
    CGS = CGS()
    CGS.GUI(start_time)