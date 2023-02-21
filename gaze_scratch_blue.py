
"""

Created on Mon Sep  6 14:54:56 2021

@author: Florian Bednarski (fteichmann@cbs.mpg.de)

"""

# %% Import

import glob
import os
import time
from time import perf_counter
import tkinter as tk
import tobii_research as tr
from PIL import Image, ImageTk
import imageio
import threading
import math
import pygame
import csv
import vlc
import itertools
import pandas as pd
import sys
import mss


# List all images of experiment
#images_path = "D:/Conda_Python/gaze_scratch_code_files/images/"
#trial_images = os.listdir(images_path)

#attention_path = "D:/Conda_Python/gaze_scratch_code_files/attention/"
#attention_video = os.listdir(attention_path)

#video_path = "D:/Conda_Python/gaze_scratch_code_files/videos/"
#trial_video = os.listdir(video_path)

#background_path = "D:/Conda_Python/gaze_scratch_code_files/background/"
#trial_images_trick = os.listdir(background_path)

#attention getter video
attention_video = ['Candy.mp4', 'Rainbow.mp4', 'Star.mp4', 'Sun.mp4']
#image shown in contingent phase
trial_images = ['1sand_drop.png', '2grass_rise.png', '3sky_drop.png', '4stars_rise.png', '5beach_drop.png',
                '6lawn_rise.png', '7heaven_drop.png', '8night_rise.png', '9earth_drop.png', '10meadow_rise.png',
                '11cloud_drop.png', '12dream_rise.png', '13play_drop.png', '14toy_rise.png', '15blue_drop.png',
                '16space_rise.png',
                '17sand_rise.png', '18grass_drop.png', '19sky_rise.png', '20stars_drop.png',
                '21beach_rise.png', '22lawn_drop.png', '23heaven_rise.png', '24night_drop.png', '25earth_rise.png',
                '26meadow_drop.png', '27cloud_rise.png', '28dream_drop.png', '29play_rise.png', '30toy_drop.png',
                '31blue_rise.png', '32space_drop.png']

#video for baseline and transition
trial_video = ['1sand_drop.m4v', '2grass_rise.m4v', '3sky_drop.m4v', '4stars_rise.m4v', '5beach_drop.m4v',
               '6lawn_rise.m4v', '7heaven_drop.m4v', '8night_rise.m4v', '9earth_drop.m4v', '10meadow_rise.m4v',
               '11cloud_drop.m4v', '12dream_rise.m4v', '13play_drop.m4v', '14toy_rise.m4v', '15blue_drop.m4v',
               '16space_rise.m4v',
               '17sand_rise.m4v', '18grass_drop.m4v', '19sky_rise.m4v', '20stars_drop.m4v',
               '21beach_rise.m4v', '22lawn_drop.m4v', '23heaven_rise.m4v', '24night_drop.m4v', '25earth_rise.m4v',
               '26meadow_drop.m4v', '27cloud_rise.m4v', '28dream_drop.m4v', '29play_rise.m4v', '30toy_drop.m4v',
               '31blue_rise.m4v', '32space_drop.m4v']

#background image shown in disruption phase
#trial_images_trick = ['sand.png', 'sky.png', 'lawn.png', 'night.png']


class App:

    def __init__(self, image_idx: int, video_attention_idx: int, video_trial_idx: int, trial_idx: int, child_idx: int):

        self.root = tk.Tk()
        # Load trial image
        self.trial_img = trial_images[image_idx]
        self.attention_video = attention_video[video_attention_idx]
        self.trial_video = trial_video[video_trial_idx]
        #self.trial_img_trick = trial_images_trick[image_idx_trick]
        #self.label = tk.Label(self.root, text="")

        self.w_screen = 1280
        self.h_screen = 1024
        self.data_gaze = []
        self.co_ordinate_list = []
        self.global_gaze_data = []
        self.w_tiles = self.w_screen // 16
        self.h_tiles = self.w_tiles  # quadratic version
        # self.h_tiles = self.h_screen // 16  # perfect fit

        self.blocks = {}
        self.n_block_removed = 0
        self.n_blocks = 0

        self.time_start = perf_counter()
        #print("trial start ", self.time_start)
        self.time_end = 0
        #self.time_trick = tk.IntVar()
        self.time_at_scratching_end = None

        tr.find_all_eyetrackers()
        self.found_eyetrackers = tr.find_all_eyetrackers()
        self.my_eyetracker = self.found_eyetrackers[0]
        self.my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, self.gaze_data_callback_baseline, as_dictionary=True)

        self.root.geometry("%dx%d+%d+%d" % (self.w_screen, self.h_screen, 1280, 0))

        container = tk.Frame(self.root)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.container = container

        self.videopanel = tk.Frame(self.container)
        self.videopanel.grid(row=0, column=0, sticky="nsew")

        #self.videopanel2 = tk.Frame(self.container)
        #self.videopanel2.grid(row=0, column=0, sticky="nsew")

        self.imagepanel = tk.Frame(self.container)
        self.imagepanel.grid(row=0, column=0, sticky="nsew")

        #self.eyetrackerpanel = tk.Frame(self.container)
        #self.eyetrackerpanel.grid(row=0, column=0, sticky="nsew")

        self.canvas = tk.Canvas(self.imagepanel, width=self.w_screen, height=self.h_screen)
        img = ImageTk.PhotoImage(file="welcome.png")
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
        self.canvas.pack()

        args = []
        self.Instance = vlc.Instance(args)
        self.player = self.Instance.media_player_new()
        #self.player2 = self.Instance.media_player_new()

        # call trial flow
        self.imagepanel.tkraise()
        self.root.after(1000, self.catch_video)
        # self.root.after(4000, self.show_image)
        self.root.after(4000, self.music)
        self.root.after(4000, self.phase_video)
        self.root.after(12500, self.show_image)
        self.root.after(12500, self.fill_image)

        #self.root.after(self.time_trick.get()*1000, self.show_image_trick)

        self.root.mainloop()

        self.write_data()

    def write_data(self):

        file_tobii = str(trial_idx) + "_" + str(child_idx) + "_GSP_tobii_blue_" + self.trial_img.split(".")[0]
        print(file_tobii)
        file_screen = str(trial_idx) + "_" + str(child_idx) + "_GSP_screen_blue_" + self.trial_img.split(".")[0]
        print(file_screen)
        file_global = str(trial_idx) + "_" + str(child_idx) + "_GSP_global_blue_" + self.trial_img.split(".")[0]
        print(file_global)

        global_data = pd.DataFrame(self.global_gaze_data)
        global_data.to_csv("%s.csv" % file_global, index=False, header=True)

        with open("%s.csv" % file_tobii, "w", newline="") as file_a:
            fieldnames_a = ['time', 'gaze_point_lx', 'gaze_point_rx', 'gaze_point_ly', 'gaze_point_ry']
            writer_a = csv.DictWriter(file_a, fieldnames=fieldnames_a)
            writer_a.writeheader()
            for t, lx, rx, ly, ry in self.data_gaze:
                writer_a.writerow({'time': t,
                                   'gaze_point_lx': lx, 'gaze_point_rx': rx,
                                   'gaze_point_ly': ly, 'gaze_point_ry': ry})

        with open("%s.csv" % file_screen, "w", newline="") as file_b:
            fieldnames_b = ['time', 'gaze_point_x', 'gaze_point_y']
            writer_b = csv.DictWriter(file_b, fieldnames=fieldnames_b)
            writer_b.writeheader()
            for t, rx, lx in self.co_ordinate_list:
                writer_b.writerow({'time': t, 'gaze_point_x': rx, 'gaze_point_y': lx})

    def key(self, event):
        if event.char == 't':
            self.my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, self.gaze_data_callback, as_dictionary=True)
        if event.char == 's':
            self.my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, self.gaze_data_callback)

    def close_win(self, e):
        self.root.destroy()

    def music(self):
        pygame.mixer.init()
        pygame.mixer.music.load("sound_A.mp3")
        pygame.mixer.music.play()

    def show_image(self):

        self.new_image = ImageTk.PhotoImage(file=self.trial_img)
        self.canvas.itemconfig(self.image_on_canvas, image=self.new_image)
        self.imagepanel.tkraise()
        print('Trial Image Raise:', str(perf_counter()))

    #def show_image_trick(self):

        #self.new_image_trick = ImageTk.PhotoImage(file=self.trial_img_trick)
        #self.canvas.itemconfig(self.image_on_canvas, image=self.new_image_trick)
        #self.imagepanel.tkraise()
        #print('Trial Image Trick Raise:', str(perf_counter()))
        #self.my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, self.gaze_data_callback_disruption, as_dictionary=True)

    def catch_video(self):

        video = self.attention_video
        m = self.Instance.media_new(str(video))  # Path, unicode
        self.player.set_media(m)
        # self.root.title("tkVLCplayer - %s" % (basename(video),))
        # set the window id where to render VLC's video output
        h = self.videopanel.winfo_id()  # .winfo_visualid()?
        self.player.set_hwnd(h)
        #self.player.play()
        self.player.play()
        self.videopanel.tkraise()

    def phase_video(self):

        video = self.trial_video
        m = self.Instance.media_new(str(video))  # Path, unicode
        self.player.set_media(m)
        # self.root.title("tkVLCplayer - %s" % (basename(video),))
        # set the window id where to render VLC's video output
        h = self.videopanel.winfo_id()  # .winfo_visualid()?
        self.player.set_hwnd(h)
        #self.player.play()
        self.player.play()
        self.videopanel.tkraise()

    def fill_image(self, color="blue"):
        #print('starting filling image 1 at ' + str(perf_counter()))

        cols = {"green": "#00CC33",
                "pink": "#FF00FF",
                "black": "#000000",
                "blue": "#3399FF",
                "grey": "#999999",}

        self.my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, self.gaze_data_callback_contingent, as_dictionary=True)
        self.time_at_fill_image = perf_counter()
        for x1 in range(0, self.w_screen, self.w_tiles):
            x2 = x1 + self.w_tiles
            for y1 in range(0, self.h_screen, self.h_tiles):
                y2 = y1 + self.h_tiles
                self.blocks[(x1, y1)] = self.canvas.create_rectangle(x1, y1, x2, y2, fill=cols[color])

        self.n_blocks = len(self.blocks)
        #print("In fill_image, self.n_blocks =",  self.n_blocks)

    def gaze_data_callback_baseline(self, gaze_data):
        self.global_gaze_data.append(gaze_data)
        #print('starting baseline eyetracker:', str(perf_counter()))
        self.lx = gaze_data['left_gaze_point_on_display_area'][0]
        self.ly = gaze_data['left_gaze_point_on_display_area'][1]
        self.rx = gaze_data['right_gaze_point_on_display_area'][0]
        self.ry = gaze_data['right_gaze_point_on_display_area'][1]
        self.time = gaze_data['device_time_stamp']

        self.data_gaze.append((self.time, self.lx, self.rx, self.ly, self.ry))

        rx = (self.lx + ((self.rx - self.lx) / 2)) * self.w_screen
        lx = (self.ly + ((self.ry - self.ly) / 2)) * self.h_screen
        self.co_ordinate_list.append((perf_counter(), rx, lx))

        # print(self.co_ordinate_list)
        # print(len(self.co_ordinate_list))
        self.time_at_base_line = time.perf_counter() - self.time_start
        if self.time_at_base_line > 9:
            self.my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, self.gaze_data_callback_baseline)
            # print(self.time_at_base_line)
            print('Stop Baseline ET:', str(perf_counter()))

    def gaze_data_callback_contingent(self, gaze_data):
        self.global_gaze_data.append(gaze_data)
        #print("starting contingent eyetracker:", str(perf_counter()))

        # Receive eye-tracker data (in Tobii format)
        self.lx = gaze_data['left_gaze_point_on_display_area'][0]
        self.ly = gaze_data['left_gaze_point_on_display_area'][1]
        self.rx = gaze_data['right_gaze_point_on_display_area'][0]
        self.ry = gaze_data['right_gaze_point_on_display_area'][1]
        self.time = gaze_data['device_time_stamp']
        # Collect eye-tracker data
        self.data_gaze.append((self.time, self.lx, self.rx, self.ly, self.ry))

        # Convert eye-tracker data to screen
        rx = (self.lx + ((self.rx - self.lx) / 2)) * self.w_screen
        lx = (self.ly + ((self.ry - self.ly) / 2)) * self.h_screen
        self.co_ordinate_list.append((perf_counter(), rx, lx))

        #print(f"{self.n_block_removed} out of {self.n_blocks} ({self.n_block_removed/self.n_blocks} %) "f"blocks are removed till now")

        self.time_at_scratching_end = perf_counter()
        # print('time_contingent_end', self.time_at_scratching_end)
        if self.n_block_removed/self.n_blocks < 0.2:
            # print('total number of block on screen are :', self.n_blocks)
            # print(n_block_removed , 'blocks are removed till now B')
            # if self.time_end < 37:

            # print('scratching at ', perf_counter())
            if math.isnan(self.co_ordinate_list[-1][1]) or math.isnan(self.co_ordinate_list[-1][2]):
                # print('nan error')
                pass
            else:
                self.update_clock(self.co_ordinate_list[-1][1], self.co_ordinate_list[-1][2])

        if self.n_block_removed/self.n_blocks >= 0.2 or self.time_at_scratching_end - self.time_at_fill_image > 30:
            self.my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, self.gaze_data_callback_contingent)
            print('Stop Contingent ET:', str(perf_counter()))
            print('blocks removed:', self.n_block_removed)
            print('blocks on screen:', self.n_blocks)
            self.time_end = perf_counter()

            # take screenshot of scratch result
            with mss.mss() as sct:
                monitor_number = 1
                mon = sct.monitors[monitor_number]
                output = "Screenshot_Contingent" + self.trial_img.split(".")[0] + "_" + str(child_idx) + "_" + str(trial_idx) + ".png"
                monitor = {"top": mon["top"], "left": mon["left"], "width": mon["width"], "height": mon["height"],
                           "mon": monitor_number}
                sct_img = sct.grab(monitor)
                mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)
            #Trick for Exp_Control
            #self.root(self.show_image_trick())
            self.my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, self.gaze_data_callback_disruption, as_dictionary=True)

    def gaze_data_callback_disruption(self, gaze_data):
        self.global_gaze_data.append(gaze_data)
        #print('starting disruption eyetracker: ' + str(perf_counter()))
        self.lx = gaze_data['left_gaze_point_on_display_area'][0]
        self.ly = gaze_data['left_gaze_point_on_display_area'][1]
        self.rx = gaze_data['right_gaze_point_on_display_area'][0]
        self.ry = gaze_data['right_gaze_point_on_display_area'][1]
        self.time = gaze_data['device_time_stamp']

        self.data_gaze.append((self.time, self.lx, self.rx, self.ly, self.ry))

        rx = (self.lx + ((self.rx - self.lx) / 2)) * self.w_screen
        lx = (self.ly + ((self.ry - self.ly) / 2)) * self.h_screen
        self.co_ordinate_list.append((perf_counter(), rx, lx))

        # print(self.co_ordinate_list)
        # print(len(self.co_ordinate_list))
        # self.time_at_base_line = time.perf_counter()
        # if self.time_at_base_line > 8:
        #    self.my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, self.gaze_data_callback_baseline)
        #    print(self.time_at_base_line)
        #    print('stopping baseline eye_tracker')

        self.time_end = perf_counter()
        # print('self time end', self.time_end)
        # print('the difference is', (self.time_end - self.time_at_scratching_end))
        if self.time_end - self.time_at_scratching_end > 5:
            print('Stop Disruption ET:', perf_counter())
            self.my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, self.gaze_data_callback_disruption)
            # print('time ends time ', self.time_end)
            #print('end of third phase', perf_counter())
            # print(int(perf_counter())*1000-9000)
            # take screenshot of disruption result
            with mss.mss() as sct:
                monitor_number = 1
                mon = sct.monitors[monitor_number]
                output = "Screenshot_Disruption" + self.trial_img.split(".")[0] + "_" + str(child_idx) + "_" + str(trial_idx) + ".png"
                monitor = {"top": mon["top"], "left": mon["left"], "width": mon["width"], "height": mon["height"],
                           "mon": monitor_number}
                sct_img = sct.grab(monitor)
                mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)
            self.canvas.destroy()
            time.sleep(3)  # time until the background image is removed, too
            self.root.destroy()

    def update_clock(self, eye_point_x, eye_point_y):

        # now = time.strftime("%H:%M:%S")
        # self.label.configure(text=now)

        # print("update_clock", self.w_tiles, self.h_tiles)
        x_rounded = eye_point_x - eye_point_x % self.w_tiles
        y_rounded = eye_point_y - eye_point_y % self.h_tiles
        # self.blocks.append(x_rounded, y_rounded)

        oval = self.blocks.pop((x_rounded, y_rounded), None)
        if oval is not None:
            # print("remove", x_rounded, y_rounded)
            self.canvas.delete(oval)
            self.n_block_removed += 1
            self.canvas.update()


if __name__ == "__main__":

    trial_idx = input(f"Type number of trial: ")
    if trial_idx.isnumeric():
        trial_idx = int(trial_idx)

    child_idx = input(f"Type number of child: ")
    if child_idx.isnumeric():
        child_idx = int(child_idx)

    video_attention_idx = input(f"Type number of attention video (0-{len(attention_video)}): ")
    if video_attention_idx.isnumeric():
        video_attention_idx = int(video_attention_idx)
    else:
        print(f"Given number '{video_attention_idx}' not understood!")

    img_idx = input(f"Type number of trial image (0-{len(trial_images)}): ")
    if img_idx.isnumeric():
        img_idx = int(img_idx)
    else:
        print(f"Given number '{img_idx}' not understood!")

    video_trial_idx = input(f"Type number of trial video (0-{len(trial_video)}): ")
    if video_trial_idx.isnumeric():
        video_trial_idx = int(video_trial_idx)
    else:
        print(f"Given number '{video_trial_idx}' not understood!")

    #img_idx_trick = input(f"Type number of background image (0-{len(trial_images_trick)}): ")
    #if img_idx_trick.isnumeric():
        #img_idx_trick = int(img_idx_trick)
    #else:
        #print(f"Given number '{img_idx_trick}' not understood!")


    print(f"Run image number {img_idx}")
    print(f"Run attention video number {video_attention_idx}")
    print(f"Run trial video number {video_trial_idx}")
    #print(f"Run image2 number {img_idx_trick}")

    app = App(img_idx, video_attention_idx, video_trial_idx, trial_idx, child_idx)

