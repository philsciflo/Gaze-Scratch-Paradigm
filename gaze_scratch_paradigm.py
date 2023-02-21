
"""

Created on Mon Sep  6 14:54:56 2021

@author: Florian Bednarski (fteichmann@cbs.mpg.de)

"""

#This script runs the gaze scratch paradigm with a tobii eye tracker (eye tracker has to be compatible with tobii SDK) on a Windows operating system (Windows 7 and up).

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

#Several differnt stimuli files are required to run the experiment. Those files need to be stored in individual folders and named correctly. 
#If you download the stimuli from the repository the naming and folder structure should be correct. 
#If you want to run this experiment with your own stimuli you will have to change the script in some places and you might have to adjust the timing.


# List all images of experiment
#images_path = #insert path to image files#
#trial_images = os.listdir(images_path)

#attention_path = #insert path to attention getter files#
#attention_video = os.listdir(attention_path)

#video_path = #insert path to video files#
#trial_video = os.listdir(video_path)

#list of attention getter videos
attention_video = ['Candy.mp4', 'Rainbow.mp4', 'Star.mp4', 'Sun.mp4']

#list of videos for baseline and transition to contingent phase
trial_video = ['1sand_drop.m4v', '2grass_rise.m4v', '3sky_drop.m4v', '4stars_rise.m4v', '5beach_drop.m4v',
               '6lawn_rise.m4v', '7heaven_drop.m4v', '8night_rise.m4v', '9earth_drop.m4v', '10meadow_rise.m4v',
               '11cloud_drop.m4v', '12dream_rise.m4v', '13play_drop.m4v', '14toy_rise.m4v', '15blue_drop.m4v',
               '16space_rise.m4v',
               '17sand_rise.m4v', '18grass_drop.m4v', '19sky_rise.m4v', '20stars_drop.m4v',
               '21beach_rise.m4v', '22lawn_drop.m4v', '23heaven_rise.m4v', '24night_drop.m4v', '25earth_rise.m4v',
               '26meadow_drop.m4v', '27cloud_rise.m4v', '28dream_drop.m4v', '29play_rise.m4v', '30toy_drop.m4v',
               '31blue_rise.m4v', '32space_drop.m4v']

#list of images shown in contingent phase
trial_images = ['1sand_drop.png', '2grass_rise.png', '3sky_drop.png', '4stars_rise.png', '5beach_drop.png',
                '6lawn_rise.png', '7heaven_drop.png', '8night_rise.png', '9earth_drop.png', '10meadow_rise.png',
                '11cloud_drop.png', '12dream_rise.png', '13play_drop.png', '14toy_rise.png', '15blue_drop.png',
                '16space_rise.png',
                '17sand_rise.png', '18grass_drop.png', '19sky_rise.png', '20stars_drop.png',
                '21beach_rise.png', '22lawn_drop.png', '23heaven_rise.png', '24night_drop.png', '25earth_rise.png',
                '26meadow_drop.png', '27cloud_rise.png', '28dream_drop.png', '29play_rise.png', '30toy_drop.png',
                '31blue_rise.png', '32space_drop.png']

#this is the script that runs the experiment

class App:

    def __init__(self, image_idx: int, video_attention_idx: int, video_trial_idx: int, trial_idx: int, child_idx: int):

        self.root = tk.Tk()
        # Load trial image
        self.trial_img = trial_images[image_idx]
        self.attention_video = attention_video[video_attention_idx]
        self.trial_video = trial_video[video_trial_idx]

        self.w_screen = 1280 #adjust to your screen
        self.h_screen = 1024 #adjust to your screen
        self.data_gaze = []
        self.co_ordinate_list = []
        self.global_gaze_data = []
        self.w_tiles = self.w_screen // 16 #adjust to your screen
        self.h_tiles = self.w_tiles  # quadratic version
        # self.h_tiles = self.h_screen // 16  # perfect fit dependent on screen size

        self.blocks = {}
        self.n_block_removed = 0
        self.n_blocks = 0

        self.time_start = perf_counter()
        self.time_end = 0
        self.time_at_scratching_end = None

        #connect to tobii tracker - this might change if you are using another eye tracking system
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

        self.imagepanel = tk.Frame(self.container)
        self.imagepanel.grid(row=0, column=0, sticky="nsew")

        self.canvas = tk.Canvas(self.imagepanel, width=self.w_screen, height=self.h_screen)
        img = ImageTk.PhotoImage(file="welcome.png")
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
        self.canvas.pack()

        args = []
        self.Instance = vlc.Instance(args)
        self.player = self.Instance.media_player_new()
    
    

        # call trial flow
        # these lines manage the timing of the trial.
        # if you want to ajust the lenght of the trial or certain phase or if you are using other stimuli you need to adjust the timing below.
        self.imagepanel.tkraise()
        self.root.after(1000, self.catch_video)   #attention getter
        self.root.after(4000, self.music)         #baseline phase 5 seconds
        self.root.after(4000, self.phase_video)   #transition 3 second
        self.root.after(12500, self.show_image)   #contingent phase and disruption phase 
        self.root.after(12500, self.fill_image)   #trial end is dependent on contingent phase length which is dependent on participant interaction

        self.root.mainloop()

        self.write_data()   
        
#in the follwing several function are defined which have specific tasks but all are called in the main loop above
#first we define how to and where to write the data (you might want to adjust this to you own needs and preferences)

    def write_data(self):
        #we collected data in three formats
        #first the gaze data in the tobii coordinate system (0/0 top left corner of the screen and 1/1 bottom right corner of the screen)
        file_tobii = str(trial_idx) + "_" + str(child_idx) + "#define some specification#" + self.trial_img.split(".")[0]
        print(file_tobii)
        #second the gaze data matching the dimensions of your screen
        file_screen = str(trial_idx) + "_" + str(child_idx) + "#define some specification#" + self.trial_img.split(".")[0]
        print(file_screen)
        #third the global tobii eveything at once file
        file_global = str(trial_idx) + "_" + str(child_idx) + "#define some specification#" + self.trial_img.split(".")[0]
        print(file_global)

        #this collects the global data
        global_data = pd.DataFrame(self.global_gaze_data)
        global_data.to_csv("%s.csv" % file_global, index=False, header=True)

        #this collects the tobii coordinates data
        with open("%s.csv" % file_tobii, "w", newline="") as file_a:
            fieldnames_a = ['time', 'gaze_point_lx', 'gaze_point_rx', 'gaze_point_ly', 'gaze_point_ry']
            writer_a = csv.DictWriter(file_a, fieldnames=fieldnames_a)
            writer_a.writeheader()
            for t, lx, rx, ly, ry in self.data_gaze:
                writer_a.writerow({'time': t,
                                   'gaze_point_lx': lx, 'gaze_point_rx': rx,
                                   'gaze_point_ly': ly, 'gaze_point_ry': ry})

        #this collects the matched to screen data
        with open("%s.csv" % file_screen, "w", newline="") as file_b:
            fieldnames_b = ['time', 'gaze_point_x', 'gaze_point_y']
            writer_b = csv.DictWriter(file_b, fieldnames=fieldnames_b)
            writer_b.writeheader()
            for t, rx, lx in self.co_ordinate_list:
                writer_b.writerow({'time': t, 'gaze_point_x': rx, 'gaze_point_y': lx})
 
#this is just a function to start the eye tracker manually / this is not really needed but nice to test equipment
    def key(self, event):
        if event.char == 't':
            self.my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, self.gaze_data_callback, as_dictionary=True)
        if event.char == 's':
            self.my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, self.gaze_data_callback)
            
#this is just a function to kill the experiment once it is running
    def close_win(self, e):
        self.root.destroy()

#function to play music throughout the experiment / especially usefull if you are working with infant to keep them engaged
    def music(self):
        pygame.mixer.init()
        pygame.mixer.music.load("sound_A.mp3")
        pygame.mixer.music.play()
        
#this raises the panel with the contingent and disruption phase image
    def show_image(self):
        self.new_image = ImageTk.PhotoImage(file=self.trial_img)
        self.canvas.itemconfig(self.image_on_canvas, image=self.new_image)
        self.imagepanel.tkraise()
        print('Trial Image Raise:', str(perf_counter()))

#this starts the attention getter video
    def catch_video(self):
        video = self.attention_video
        m = self.Instance.media_new(str(video))  
        self.player.set_media(m)
        h = self.videopanel.winfo_id() 
        self.player.set_hwnd(h)
        self.player.play()
        self.videopanel.tkraise()

       
#this starts the transition phase video       
    def phase_video(self):
        video = self.trial_video
        m = self.Instance.media_new(str(video)) 
        self.player.set_media(m)
        h = self.videopanel.winfo_id()
        self.player.set_hwnd(h)
        self.player.play()
        self.videopanel.tkraise()

#this function covers the image on the screen with the unicoler grid 
    def fill_image(self, color="blue"):
        #this are just color codes, feel free to play around and see what works best
        cols = {"green": "#00CC33",
                "pink": "#FF00FF",
                "black": "#000000",
                "blue": "#3399FF",
                "grey": "#999999",}

        #here we subscribe to the ET to collect data and enable the contingent phase scratching
        self.my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, self.gaze_data_callback_contingent, as_dictionary=True)
        #here we create rectangles on the screen in the color set above
        self.time_at_fill_image = perf_counter()
        for x1 in range(0, self.w_screen, self.w_tiles):
            x2 = x1 + self.w_tiles
            for y1 in range(0, self.h_screen, self.h_tiles):
                y2 = y1 + self.h_tiles
                self.blocks[(x1, y1)] = self.canvas.create_rectangle(x1, y1, x2, y2, fill=cols[color])
        self.n_blocks = len(self.blocks)
        
#this is the baseline et function 
#IMPORTANT data collection start with the onset of the trial, but we first show a welcome image and then an attention getter
#this needs to be adjusted for in the data processing
    def gaze_data_callback_baseline(self, gaze_data):
        self.global_gaze_data.append(gaze_data)
        self.lx = gaze_data['left_gaze_point_on_display_area'][0]
        self.ly = gaze_data['left_gaze_point_on_display_area'][1]
        self.rx = gaze_data['right_gaze_point_on_display_area'][0]
        self.ry = gaze_data['right_gaze_point_on_display_area'][1]
        self.time = gaze_data['device_time_stamp']
        #get data and write to list
        self.data_gaze.append((self.time, self.lx, self.rx, self.ly, self.ry))
        # Convert eye-tracker data to screen
        rx = (self.lx + ((self.rx - self.lx) / 2)) * self.w_screen
        lx = (self.ly + ((self.ry - self.ly) / 2)) * self.h_screen
        self.co_ordinate_list.append((perf_counter(), rx, lx))

        self.time_at_base_line = time.perf_counter() - self.time_start
        #this ends the baseline data collection just before the transition video starts
        if self.time_at_base_line > 9:
            self.my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, self.gaze_data_callback_baseline)
            print('Stop Baseline ET:', str(perf_counter()))
            
#this is the contingent et function
#data collections start when this function is called by 'def fill_image'
    def gaze_data_callback_contingent(self, gaze_data):
        self.global_gaze_data.append(gaze_data)
        self.lx = gaze_data['left_gaze_point_on_display_area'][0]
        self.ly = gaze_data['left_gaze_point_on_display_area'][1]
        self.rx = gaze_data['right_gaze_point_on_display_area'][0]
        self.ry = gaze_data['right_gaze_point_on_display_area'][1]
        self.time = gaze_data['device_time_stamp']
        #get data and write to list
        self.data_gaze.append((self.time, self.lx, self.rx, self.ly, self.ry))

        # Convert eye-tracker data to screen
        rx = (self.lx + ((self.rx - self.lx) / 2)) * self.w_screen
        lx = (self.ly + ((self.ry - self.ly) / 2)) * self.h_screen
        self.co_ordinate_list.append((perf_counter(), rx, lx))

        #set condition on when to move to disruptio phase
        #here either 30second or until 20% of blocks removed
        self.time_at_scratching_end = perf_counter()
        if self.n_block_removed/self.n_blocks < 0.2:
            if math.isnan(self.co_ordinate_list[-1][1]) or math.isnan(self.co_ordinate_list[-1][2]):
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
            #start disruption phase
            self.my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, self.gaze_data_callback_disruption, as_dictionary=True)
            
#this is the disruption et function
#data collections start when this function is called by 'def gaze_data_callback_contingent'
    def gaze_data_callback_disruption(self, gaze_data):
        self.global_gaze_data.append(gaze_data)
        self.lx = gaze_data['left_gaze_point_on_display_area'][0]
        self.ly = gaze_data['left_gaze_point_on_display_area'][1]
        self.rx = gaze_data['right_gaze_point_on_display_area'][0]
        self.ry = gaze_data['right_gaze_point_on_display_area'][1]
        self.time = gaze_data['device_time_stamp']
        #get data and write to list
        self.data_gaze.append((self.time, self.lx, self.rx, self.ly, self.ry))
        
        # Convert eye-tracker data to screen
        rx = (self.lx + ((self.rx - self.lx) / 2)) * self.w_screen
        lx = (self.ly + ((self.ry - self.ly) / 2)) * self.h_screen
        self.co_ordinate_list.append((perf_counter(), rx, lx))

        self.time_end = perf_counter()
        if self.time_end - self.time_at_scratching_end > 5:
            print('Stop Disruption ET:', perf_counter())
            self.my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, self.gaze_data_callback_disruption)
            
            # take screenshot of disruption result
            with mss.mss() as sct:
                monitor_number = 1
                mon = sct.monitors[monitor_number]
                output = "Screenshot_Disruption" + self.trial_img.split(".")[0] + "_" + str(child_idx) + "_" + str(trial_idx) + ".png"
                monitor = {"top": mon["top"], "left": mon["left"], "width": mon["width"], "height": mon["height"],
                           "mon": monitor_number}
                sct_img = sct.grab(monitor)
                mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)
                
            #end trial after 3 seconds
            self.canvas.destroy()
            time.sleep(3)  # time until the background image is removed
            self.root.destroy()

#this function enable the gaze scratch effect
#every last gaze point passed on from 'def gaze_data_callback_contingent' is run through this loop
#if there is still a block at this gaze point it is removed
    def update_clock(self, eye_point_x, eye_point_y):

        x_rounded = eye_point_x - eye_point_x % self.w_tiles
        y_rounded = eye_point_y - eye_point_y % self.h_tiles

        oval = self.blocks.pop((x_rounded, y_rounded), None)
        if oval is not None:
            self.canvas.delete(oval)
            self.n_block_removed += 1
            self.canvas.update()

#this loop is the main loop
#here we get a bunch of commands which need to be passed in order to start the trial
#simply put in the numbers refering to images, videos and sound you want to play in the trial
#REMEMBER python counts from 0 onwards not 1

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


    print(f"Run image number {img_idx}")
    print(f"Run attention video number {video_attention_idx}")
    print(f"Run trial video number {video_trial_idx}")
 
    app = App(img_idx, video_attention_idx, video_trial_idx, trial_idx, child_idx)

