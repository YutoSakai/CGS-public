# coding: utf-8
from PIL import Image, ImageFont, ImageDraw
import re


def draw_text(frame_image, font_size, font_file_path, target_string, draw_start_x, draw_start_y, font_color='#000000', kind="texttate"):
    """
    テキストの縦書き描画
    :param frame_image        Image:  フレームのImageオブジェクト
    :param font_size          int:    フォントサイズ
    :param font_file_path     string: OTFファイルまでのパス
    :param target_string      string: 対象の文字列
    :param draw_start_x       int:    描画開始位置_X
    :param draw_start_y       int:    描画開始位置_Y
    :param font_color         string: 描画する文字の色 (デフォルト: "#000000")
    """
    if kind == "texttate":
        # print("draw_textのtate")
        # 描画用データを取得
        draw = ImageDraw.Draw(frame_image)

        # フォントデータを取得
        image_font = ImageFont.truetype(font_file_path, font_size)

        # 各文字の描画管理変数
        ix, iy = 1, 0

        for c in target_string:
            if c == '\n':
                ix += 1
                iy = 0
                continue
            x = draw_start_x - ix * font_size
            y = draw_start_y + (iy * font_size)
            if re.match('[0-9]', c):
                x += int(font_size / 4)
                draw.text((x, y), c, font=image_font, fill=font_color)
                x -= int(font_size / 4)
                iy += 1
                continue

            if c == ',' or c == '.' or c == '、' or c == '。':
                x += int(font_size / 2)
                y -= int(font_size / 2)
                draw.text((x, y), c, font=image_font, fill=font_color)
                x -= int(font_size / 2)
                y += int(font_size / 2)
                iy += 1
                continue
            # 今回描画する1文字の詳細なX, Yを設定
            # char_width, char_height = image_font.getsize(c)
            # x += (font_size - char_width) / 2
            # y += draw_start_y
            if c == 'ー' or c == '〜' or c == '(' or c == ')' or c == '「' or c == '」' or c == '[' or c == ']' or\
                    c == '（' or c == '）' or c == '{' or c == '}' or c == '｛' or c == '｝':
                text_image = Image.new("RGBA", (font_size, font_size), (255, 255, 255, 255))
                tmpDraw = ImageDraw.Draw(text_image)
                tmpDraw.text((0, 0), c, font=image_font, fill=font_color)
                text_image = text_image.rotate(270)
                frame_image.paste(text_image, (x, y))
                iy += 1
                continue
                # x += int(font_size / 2.5)
                # c = '|'

            # 指定の場所へ文字を描画
            draw.text((x, y), c, font=image_font, fill=font_color)
            iy += 1

    else:
        # print("draw_textのyoko")
        ImageDraw.Draw(frame_image).text((draw_start_x, draw_start_y), target_string,
                                     font=ImageFont.truetype(font_file_path, font_size), fill=font_color)
    return True
