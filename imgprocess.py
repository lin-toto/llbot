#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import print_function

import numpy as np
import cv2
import sys
import random
import math
import json
from collections import OrderedDict

from moviepy.editor import VideoFileClip
from rmborder import remove_black_border
from constants import *

DEBUG = True
VISUAL = True
START_WAIT = 0.18

video_name = 'LL Videos/ラブライブ！ スクフェス 僕らのLIVE 君とのLIFE [MASTER] Full Combo 判定強化なし (All N cards).mp4'

def pause(): raw_input("Press Enter to continue")
def dpause():
    if DEBUG: pause()

player_initial_brightness = [None, None, None, None, None, None, None, None, None]
player_control_point_gray = [None, None, None, None, None, None, None, None, None]
player_control_point_status = [0,0,0,0,0,0,0,0,0]
player_hold_start_frame = [None, None, None, None, None, None, None, None, None]
player_click_status = [False, False, False, False, False, False, False, False, False]
player_detect_point = (
    [],[],[],
    [],[],[],
    [],[],[]
)

action_serie = []

cap = cv2.VideoCapture(video_name)
cap_moviepy = VideoFileClip(video_name)
frame_rate = cap.get(5)
frame_count = cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
print("Frame rate: " + `frame_rate`)
print("Frame count: " + `frame_count`)

audio_start_time = None
audio_start_frame = None
audio_end_time = None
audio_end_frame = None
for i in range(60, int(cap_moviepy.duration)):
    audio_clip = cap_moviepy.audio.subclip(i, i+1).to_soundarray(fps=frame_rate)
    end_position = next((i for i, x in enumerate(audio_clip) if list(x) == [0, 0]), None)
    if end_position is not None:
        audio_end_time = i + end_position * 1.0 / frame_rate
        audio_end_frame = int(i * frame_rate + end_position)
        break


print("Audio end time: " + `audio_end_time`)
assert(audio_end_time is not None)

cap.set(1, frame_count - 10)
(top, bottom, left, right) = remove_black_border(cap.read()[1])
print("Border clip: " + `(top, bottom, left, right)`)

for i, (player_x, player_y) in enumerate(player_center):
    for x in range(player_x - circle_radius, player_x + circle_radius + 1):
        for y in range(player_y - circle_radius, player_y + circle_radius + 1):
            if (x - player_x)**2 + (y - player_y)**2 <= circle_radius**2:
                if random.random() < 0.1:
                    player_detect_point[i].append((x,y))
    '''for _ in range(500):
    radius = int(circle_radius * random.random())
    angle = random.random() * 2 * math.pi
    (x, y) = (player_x + int(radius * math.sin(angle)), player_y + int(radius * math.cos(angle)))
    player_detect_point[i].append((x,y))'''

frame_id = 0

cap.set(1, 0)

while True:

    ret, frame = cap.read()

    frame = frame[top:bottom, left:right]

    frame = cv2.resize(frame, (450,300))
    frame_id += 1

    if VISUAL:
        cv2.imwrite('img/' + `frame_id` + '.png', frame)
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    #cv2.circle(frame, (433, 16), 5, (0,0,255), -1)

    if sum(list(frame[16,438])) >= 600:
        audio_start_frame = frame_id
        break


print("Load start frame: " + `audio_start_frame`)
assert(audio_start_frame is not None)

dpause()

while True:

    ret, frame = cap.read()

    if frame is None or frame_id >= audio_end_frame + frame_rate * 3:
        break

    frame = frame[top:bottom, left:right]

    frame = cv2.resize(frame, (450,300))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    for i, player in enumerate(player_center):
        brightness = 0
        white_count = 0
        for x, y in player_detect_point[i]:
            brightness += gray[y,x]
            rgb = list(frame[y,x])
            control_point = 250
            is_white = [x > control_point for x in rgb]
            if is_white[0] and is_white[1] and is_white[2]:
                white_count += 1

        control_point_grayscale = 0
        for x_,y_ in ring_control_point[i]:
            control_point_grayscale += gray[y_,x_]
            cv2.circle(frame, (x_,y_),1,(180,230,110),-1)
        #print(control_point_grayscale)

        if player_initial_brightness[i] is None:
            player_initial_brightness[i] = brightness
            player_click_status[i] = brightness
            player_control_point_gray[i] = control_point_grayscale
        else:
            #print(`white_count`, `len(player_detect_point[i])`)
            if brightness - player_click_status[i] > player_initial_brightness[i] * 0.15 and white_count > len(player_detect_point[i]) * 0.1:
                if player_control_point_status[i] < 3:
                    print("Frame " + `frame_id` + " click " + `i + 1`)
                    action_serie.append(OrderedDict([
                        ("timing_sec", float("%.3f" % ((frame_id - 1 - audio_start_frame + 0.0) / frame_rate + START_WAIT))),
                        ("notes_attribute", 1),
                        ("notes_level", 1),
                        ("effect", 1),
                        ("effect_value", 2),
                        ("position", 9 - i)
                    ]))
                else:
                    print("Frame " + `frame_id` + " endhold " + `i + 1`)
                    action_serie.append(OrderedDict([
                        ("timing_sec", float("%.3f" % ((player_hold_start_frame[i] - audio_start_frame + 0.0) / frame_rate + START_WAIT))),
                        ("notes_attribute", 1),
                        ("notes_level", 1),
                        ("effect", 3),
                        ("effect_value", float("%.3f" % ((frame_id - 1 - player_hold_start_frame[i] + 0.0) / frame_rate))),
                        ("position", 9 - i)
                    ]))
                    player_hold_start_frame[i] = None
                    player_control_point_status[i] = 0
                if VISUAL:
                    cv2.circle(frame, player_center[i], circle_radius, (0, 0, 255), -1)

        if brightness < player_click_status[i] or white_count > len(player_detect_point[i]) * 0.1:
            player_click_status[i] = brightness

        if control_point_grayscale < player_control_point_gray[i] * 0.93:
            player_control_point_status[i] += 1
            if player_control_point_status[i] == 3:
                print("Frame " + `frame_id` + " hold " + `i + 1`)
                player_hold_start_frame[i] = frame_id - 2

            if player_control_point_status[i] >= 3:
                cv2.circle(frame, player_center[i], circle_radius, (180, 230, 120), -1)
        else:
            if player_control_point_status[i] < 3:
                player_control_point_status[i] = 0

    if VISUAL:
        cv2.imwrite('img/' + `frame_id` + '.png', gray)

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    #dpause()

    frame_id += 1

cap.release()
cv2.destroyAllWindows()

file_name = raw_input("Song ID: ")
def compare(a, b):
    if a['timing_sec'] < b['timing_sec']:
        return -1
    return 1
action_serie.sort(compare)
open("songdata/" + file_name + ".json", "w").write(json.dumps(action_serie))
