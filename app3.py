import os
import sys

import cv2
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import *
from PyQt5 import uic
import pandas as pd
import numpy as np
from PIL import ImageFont, ImageDraw, Image

X = 1600
Y = 2100
White = (255, 255, 255)
Black = (0, 0, 0)
Green = (0, 255, 0)
Red = (0, 0, 255)
Orange = (0, 127, 255)
max_character = 13

# 파일 로드시 초기화되는 변수들
form_class = uic.loadUiType("ui/smfa.ui")[0]

read_file = None
row_num = 0
page_num = 0
current_page = 0
last_page = 0
current_filename = None


def make_content(contents):
    temp_str = []
    for i, content in enumerate(contents):
        temp_str.append(f"{str(i + 1)}. ")
        temp = content
        temp = temp.replace("$$", "\n")
        temp_str.append(temp)
        temp_str.append("\n")
    return "".join(temp_str)


def divide_content(content: str):
    contents = []
    if current_page != last_page or row_num == last_page * 10:
        last_index = 10
    else:
        last_index = row_num % 10

    for i in range(2, 2 + last_index):
        temp = content.split("{}.".format(i))
        if len(temp) == 1:
            contents.append(temp[0].replace("1.", "").strip())
            break
        temp = temp[0].replace("1.", "")
        temp = temp.strip()
        temp = temp.replace("\n", "$$")
        contents.append(temp)
        content = content.split("{}.".format(i))[1]
    return contents


def draw_rectangle(image, location, details):
    rec_start = (location[0] * int(X / 10) + 20, location[1] * int(Y / 10) + 10)
    rec_end = (rec_start[0] + 135, rec_start[1] + 160)
    cv2.rectangle(image, rec_start, rec_end, Black, 2)

    image_for_text = Image.fromarray(image)
    draw = ImageDraw.Draw(image_for_text)
    font_for_des = ImageFont.truetype("fonts/gulim.ttc", 11)
    text = details[0]

    if len(text) < max_character:
        des_start = (rec_start[0] + 5, rec_end[1] - 60)
        draw.text(des_start, text, font=font_for_des, fill=Black)
    else:
        des_start1 = (rec_start[0] + 5, rec_end[1] - 60)
        des_start2 = (rec_start[0] + 5, rec_end[1] - 45)
        draw.text(des_start1, text[0:max_character], font=font_for_des, fill=Black)
        draw.text(des_start2, text[max_character:], font=font_for_des, fill=Black)
    if details[3] == "true":
        font_for_info = ImageFont.truetype("fonts/gulim.ttc", 18)
        info_start = (rec_start[0] + 55, rec_end[1] - 27)
        draw.text(info_start, "결과기록", font=font_for_info, fill=Orange)

    image = np.array(image_for_text)

    image_exercise = cv2.imread(f'pics/{details[2]}.png', cv2.IMREAD_COLOR)
    image_exercise = cv2.resize(image_exercise, (100, 80))
    image[rec_start[1] + 5:rec_start[1] + 85, rec_start[0] + 5:rec_start[0] + 105] = image_exercise

    selection = details[1]
    des_start = (rec_start[0] + 8, rec_end[1] - 8)
    color = Green
    if "X" in selection or "P" in selection:
        color = Red
    elif "O" in selection:
        color = Green
    cv2.putText(image, details[1], des_start, cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)
    return image


def set_current_page(index):
    global current_page
    current_page = index


class WindowClass(QMainWindow, form_class):
    q_label = None
    q_text_edit = None

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        for filename in os.listdir('exercise'):
            self.testList.addItem(filename)

        self.goButton.clicked.connect(self.go_button_clicked)
        self.prevButton.clicked.connect(self.prev_button_clicked)
        self.nextButton.clicked.connect(self.next_button_clicked)
        self.saveButton.triggered.connect(self.save_button_clicked)
        self.exitButton.triggered.connect(self.exit_button_clicked)
        self.testList.itemDoubleClicked.connect(self.test_list_double_clicked)
        self.savePageButton.clicked.connect(self.save_page_button_clicked)

    def save_page_button_clicked(self):
        save_page(current_page, contents=divide_content(self.q_text_edit.toPlainText()))

    def go_button_clicked(self):
        num = int(self.goEditText.toPlainText())
        if num <= last_page:
            self.open_page(num)

    def prev_button_clicked(self):
        if current_page > 1:
            self.open_page(current_page - 1)

    def next_button_clicked(self):
        if current_page < last_page:
            self.open_page(current_page+1)

    def save_button_clicked(self):
        save_file(current_filename)

    def exit_button_clicked(self):
        print("나가기 버튼")

    def test_list_double_clicked(self):
        selected_items = self.testList.selectedItems()
        for selected_item in selected_items:
            self.open_file(selected_item.text())

    def open_page(self, index):
        set_current_page(index)
        self.currentPage.setText("{} / {}".format(index, last_page))
        img, loaded_results = load_page(index)
        self.q_label.setPixmap(img)
        self.q_text_edit.setText(make_content(loaded_results))

    def open_file(self, filename):
        load_file(filename)
        print("LOAD FILE : {} file load complete".format(filename))
        self.q_label = QLabel()
        self.scroll1.setWidget(self.q_label)
        self.q_text_edit = QTextEdit()
        self.q_text_edit.setGeometry(0, 0, 200, 200)
        self.scroll2.setWidget(self.q_text_edit)
        self.open_page(1)


def load_file(filename):
    global read_file
    global row_num
    global page_num
    global current_page
    global last_page
    global current_filename
    current_filename = filename
    read_file = pd.read_csv("exercise/{}".format(filename), sep=",", engine='c')
    read_file.fillna('NaN', inplace=True)
    row_num = len(read_file.index)
    page_num = int(row_num / 10)
    current_page = 1
    if row_num % 10 == 0:
        last_page = int(row_num / 10)
    else:
        last_page = int(row_num / 10) + 1


def save_page(index, contents):
    current_index = (index - 1) * 10
    print(contents)
    for i, content in enumerate(contents):
        read_file.result.iloc[current_index + i] = content


def load_page(index):
    start_index = (index - 1) * 10
    if index != last_page or row_num == last_page * 10:
        end_index = int(start_index + 10)
    else:
        end_index = int(start_index + row_num % 10)

    img = make_image(read_file.iloc[start_index:end_index, 0:-1])
    return img, read_file.iloc[start_index: end_index, -1]


def make_image(rows):
    img = np.zeros((Y, X, 3), np.uint8)
    img = cv2.rectangle(img, (0, 0), (X, Y), White, -1)

    # 각 줄마다
    for index, row in rows.iterrows():
        row_index = index % 10
        col = 0
        for data in row:
            # 만약 데이터 가 있다면
            if data != 'NaN':
                details = data.split(':')
                img = draw_rectangle(img, (col, row_index), details)
                col += 1

    q_bitmap = convert_img_to_q_bitmap(img)
    return q_bitmap


def convert_img_to_q_bitmap(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    height, width, channel = img.shape
    bytes_per_line = 3 * width
    q_img = QImage(img.data, width, height, bytes_per_line, QImage.Format_RGB888)
    return QPixmap.fromImage(q_img)


def save_file(filename):
    read_file.to_csv("exercise/{}".format(filename), sep=",", na_rep="NaN", index=False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()
