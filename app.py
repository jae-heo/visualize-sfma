import cv2
import os
import pandas as pd
import numpy as np
from PIL import ImageFont, ImageDraw, Image

White = (255, 255, 255)
Black = (0, 0, 0)
Green = (0, 255, 0)
Red = (0, 0, 255)
Orange = (0, 127, 255)
X = 1600
Y = 900
max_character = 13


def draw_rectangle(image, location, details):
    rec_start = (location[0] * int(X / 10) + 10, location[1] * int(Y / 5) + 10)
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


if __name__ == "__main__":
    for filename in os.listdir('data1'):
        imagecount = 0
        data = pd.read_csv("data1/{}".format(filename), sep=",", engine='c')
        data.drop(data.columns[-1], axis=1, inplace=True)
        data.fillna(0, inplace=True)
        img = np.zeros((Y, X, 3), np.uint8)
        img = cv2.rectangle(img, (0, 0), (X, Y), White, -1)

        # 각 파일 에서 한 줄마다..
        for index, row in data.iterrows():
            col = 0
            if index > 0 and index % 5 == 0:
                cv2.imwrite(f'images/{filename}{imagecount}.jpg', img)
                imagecount += 1
                img = np.zeros((Y, X, 3), np.uint8)
                img = cv2.rectangle(img, (0, 0), (X, Y), White, -1)

            # 각 줄의 데이터 하나 마다...
            for data in row:
                # 만약 데이터 가 있다면
                if data != 0:
                    details = data.split(':')
                    img = draw_rectangle(img, (col, index % 5), details)
                    col += 1

        cv2.imwrite(f'images/{filename}{imagecount}.jpg', img)
