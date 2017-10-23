#!/usr/bin/env python2

import sys, os, subprocess
import time, json, random, string
from proxy2 import *
from req_handler import SIFRequestHandler

player_pos = (
    (0,0),
    (78,78),
    (94,150),
    (137,215),
    (202,257),
    (275,275),
    (351,257),
    (415,215),
    (455,150),
    (472,78)
)

if len(sys.argv) <= 1:
    print("Usage: " + sys.argv[0] + " [DeviceIPAddress]")
    sys.exit(0)

print("Connecting...")
remote_addr = sys.argv[1]

cy_log = open("cycript.log", "wb")

shell_cmd = "script -q /dev/null " + os.path.dirname(os.path.realpath(__file__)) + "/cycript -r " + remote_addr + ":8888"
cycript = subprocess.Popen([shell_cmd],bufsize=0,shell=True,stdin=subprocess.PIPE,stdout=cy_log,stderr=subprocess.STDOUT)

def cysend(str):
    #print(str)
    cycript.stdin.write(str)
    cycript.stdin.flush()

time.sleep(0.8)
status = cycript.poll()
if status is not None:
    print("Unable to connect to child!")
    sys.exit(0)

print("Connected with " + remote_addr)

cy_script = open("script.cy", "r").read()
cysend(cy_script)
print("Successfully written helper scripts to device!")
print("")
print("---------------")

test(HandlerClass=SIFRequestHandler)

while True:
    command = raw_input("Say a command (? for help): ")
    if command == "?":
        print("Help")
        print("")
        print("test -- test touch drivers")
        print("testplayer -- test player positions")
        print("play -- play a song automatically")
    elif command == "test":
        x = int(raw_input("X coordinate: "))
        y = int(raw_input("Y coordinate: "))

        cysend("touchAt(" + `x` + "," + `y` + ");\n")
        print("Testing touch drivers.")
    elif command == "testplayer":
        player = ' '
        while player != '0':
            player = raw_input("Player (End with 0): ")
            #print("Get " + player)
            if player >= '1' and player <= '9':
                (x,y) = player_pos[ord(player) - ord('0')]
                cysend("touchAt(" + `x` + "," + `y` + ");\n")
    elif command == "play":
        song_id = raw_input("SongID: ")
        song_notes = json.loads(open("songdata/" + song_id + ".json", "r").read())
        release_queue = []
        print("Initializing...")
        cysend("touchAt(468,250);\n")
        time.sleep(3)
        pause_click_start_time = time.time()
        while time.time() - pause_click_start_time <= 6:
            cysend("touchAt(496,13);\n")
            time.sleep(0.02)

        #raw_input("Enter on start")
        '''a = time.time()
        raw_input("Enter on first beat")
        b = time.time()
        print(b-a)'''
        cysend("touchAt(207,227);\n")
        time.sleep(song_notes[0]['timing_sec'])
        time.sleep(0.02)

        start_time = time.time() - song_notes[0]['timing_sec']
        while len(song_notes) != 0 or len(release_queue) != 0:
            current_time = time.time() - start_time
            #print ("Check")
            while len(song_notes) != 0 and song_notes[0]['timing_sec'] <= current_time:
                note = song_notes.pop(0)
                (x,y) = player_pos[10 - note['position']]
                if note['effect'] != 3:
                    cysend("touchAt(" + `x` + "," + `y` + ");\n")
                    print(`current_time` + " player " + `10 - note['position']`)
                else:
                    touch_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                    cysend("touch" + touch_id + " = createTouch(" + `x` + "," + `y` + ");\n")
                    cysend("startTouch(touch" + touch_id + ");\n")
                    print(`current_time` + " player hold " + `10 - note['position']`)
                    release_queue.append((note['timing_sec'] + note['effect_value'], touch_id))

                    def compare(a,b):
                        if a[0] < b[0]:
                            return -1
                        return 1

                    release_queue.sort(compare)

            while len(release_queue) != 0 and release_queue[0][0] <= current_time:
                _, touch_id = release_queue.pop(0)
                cysend("endTouch(touch" + touch_id + ");\n")
                print(`current_time` + " player release")
    else:
        print("Unrecognized command.")
