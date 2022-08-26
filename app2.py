import threading
import time
import cv2
import os
import pandas as pd
import numpy as np
from PIL import ImageFont, ImageDraw, Image as Img, ImageTk
from tkinter import *
from tkinter.tix import *

off_flag = False
White = (255, 255, 255)
Black = (0, 0, 0)
Green = (0, 255, 0)
Red = (0, 0, 255)
Blue = (255, 0, 0)
Orange = (0, 127, 255)
X = 1600
Y = 210
max_character = 13
waitKey = True

root = Tk()
root.title("운동정보 입력 프로그램")
root.resizable(True, True)
frame = Frame(root)

win_scroll = ScrolledWindow(frame, width = 1000, height = 1000)
text = Text(win_scroll.window, width=100, height=5)


def bye_bye():
    text.delete(1.0, "end")
    text.insert(1.0, "아무키나 입력하시면 종료됩니다!")
    text.config(state="disabled")
    global off_flag
    off_flag = True


quit_button = Button(root, text="EXIT", padx=20, pady=10, bg="#000000", fg="#ffffff", command=bye_bye)
label = Label(win_scroll.window)
label_number_text = Label(win_scroll.window)


def draw_rectangle(image, location, details):
    rec_start = (location * int(X / 10) + 10, 5)
    rec_end = (rec_start[0] + 135, 200)

    if details[4] == "WHITE":
        cv2.rectangle(image, rec_start, rec_end, Black, 2)
    elif details[4] == "RED":
        cv2.rectangle(image, rec_start, rec_end, Red, 2)
    elif details[4] == "ORANGE":
        cv2.rectangle(image, rec_start, rec_end, Orange, 2)
    elif details[4] == "BLUE":
        cv2.rectangle(image, rec_start, rec_end, Blue, 2)
    elif details[4] == "GREEN":
        cv2.rectangle(image, rec_start, rec_end, Green, 2)

    image_for_text = Img.fromarray(image)
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


def check_flag():
    if off_flag:
        exit(0)


def free_key(e):
    global waitKey
    waitKey = False
    check_flag()


def lock_key():
    global waitKey
    waitKey = True


def image_process():
    for filename in os.listdir('exercise'):
        imagecount = 0
        read_data = pd.read_csv("exercise/{}".format(filename), sep=",", engine='c')
        read_data.drop(read_data.columns[-1], axis=1, inplace=True)
        read_data.fillna('NaN', inplace=True)
        read_data["result"] = 'NaN'

        row_num = len(read_data.index)

        img = np.zeros((Y, X, 3), np.uint8)
        img = cv2.rectangle(img, (0, 0), (X, Y), White, -1)
        # 각 파일 에서 한 줄마다..
        for index, row in read_data.iterrows():
            lock_key()
            label_number_text.config(text="{}/{}".format(index + 1, row_num))
            col = 0
            img = np.zeros((Y, X, 3), np.uint8)
            img = cv2.rectangle(img, (0, 0), (X, Y), White, -1)
            # 각 줄의 데이터 하나 마다...
            for data in row:
                check_flag()
                # 만약 데이터 가 있다면
                if data != 'NaN':
                    details = data.split(':')
                    img = draw_rectangle(img, col, details)
                    col += 1

            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = Img.fromarray(img)
            img_tk = ImageTk.PhotoImage(image=img)
            label.config(image=img_tk)
            label.image = img_tk

            while waitKey:
                check_flag()
                time.sleep(0.1)

            check_flag()
            body = text.get(1.0, "end").strip()
            if body != "":
                read_data["result"][imagecount] = body
            else:
                read_data["result"][imagecount] = 'NaN'

            text.delete(1.0, "end")
            imagecount += 1

        read_data.to_csv("result/{}_output".format(filename), sep=",", na_rep="NaN", index=False)


def any_key_func(e):
    check_flag()


def esc_key_func(e):
    bye_bye()
    root.destroy()
    free_key(1)
    exit(0)


if __name__ == "__main__":
    t = threading.Thread(target=image_process, daemon=True)
    t.start()

    label_number_text.pack()
    label.pack()
    text.pack()
    quit_button.pack()
    root.bind('<Shift-Return>', free_key)
    root.bind('<Escape>', esc_key_func)
    root.bind('<Key>', any_key_func)
    win_scroll.pack()
    mainloop()
