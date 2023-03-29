# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 23:07:42 2023

@author: eferlius
"""
import os
import cv2
import config
import basic
import pandas as pd
import time
import datetime
import numpy as np
import shutil
import logging

def find_closest_to_value_in_array(value, array):
    idx = np.where(np.abs(array-value) == np.min(np.abs(array-value)))[0]
    min_diff = array[idx]-value
    
    if len(idx)>1 or len(min_diff)>1:
        raise Exception("more than one value found in find_closest_index")
    return idx[0], array[idx][0], min_diff[0]

def get_video_duration(filename):
    video = cv2.VideoCapture(filename)
    fps = video.get(cv2.CAP_PROP_FPS)
    frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
    seconds = frame_count / fps
    minutes = int(seconds / 60)
    rem_sec = int(seconds % 60)
    return f"{minutes}:{rem_sec}"

LOG_NAME = 'log file renamer.txt'
logging.basicConfig(format='%(asctime)s %(levelname)-8s [%(lineno)-4d] %(filename)s \n>>> %(message)s', \
                        datefmt='%Y-%m-%d %H:%M:%S',  filename = LOG_NAME, level = logging.INFO, force = True)

    
POSSIBLE_ACTIONS = ['move', 'copy2']       
ACTION = 'move' 

# all the files will be taken from INPUT_DIR
INPUT_DIR = r'C:\Users\eferlius\Desktop\to be sorted'
LIST_EXT = ['.MOV']
# and will be moved in DEST_DIR
DEST_DIR = r'G:\Shared drives\HandWash\Tests\20230327\01_raw\iphone11'
# the file will be renamed from the name they have in INPUT_DIR
TEST_DATE = '20230327'
# csv file containing 
# - the future name of each file
# - a column with the time information that will be used to find the match of the files in INPUT_DIR
CSV_FILE = os.path.join(config.D['DIR']['00_p'].replace('DUMMY',TEST_DATE),'tests log.csv')
COL_NAME_ON_CSV = 'testCode'
COL_TIME_ON_CSV = 'stop_rec'
COL_NAME_ON_CSV_FMT = '%Y-%m-%d %H-%M-%S'

# process will be executed only if the time difference between the file in INPUT_DIR
# and the value in COL_TIME_ON_CSV is lower than
VALID_THRESH = 5 #s

# list of files in INPUT_DIR to be moved 
files, dirs = basic.utils.find_files_and_dirs_in_dir(INPUT_DIR, listExt = LIST_EXT)

# list of moments on csv file
df = pd.read_csv(CSV_FILE)
list_moments = []
for moment in df[COL_TIME_ON_CSV].values:
    try:
        list_moments.append(time.mktime(datetime.datetime.strptime(moment, COL_NAME_ON_CSV_FMT).timetuple()))
    except:
        list_moments.append(0)
array_moments = np.array(list_moments)

assert ACTION in POSSIBLE_ACTIONS, 'got invalid command ({})'.format(ACTION)

counter = 0
logging.debug('='*20)
logging.debug('moving from folder {} to folder {}'.format(INPUT_DIR, DEST_DIR))
for f in files:
    
    file_name = os.path.split(f)[-1]
    #use the modified time of the file
    moment = os.path.getmtime(f) 
    idx, value, min_diff = find_closest_to_value_in_array(moment, array_moments)
    if abs(min_diff) < VALID_THRESH:
        counter+=1
        new_name = df[COL_NAME_ON_CSV].values[idx]+os.path.splitext(f)[-1]
        new_path = os.path.join(DEST_DIR,new_name)
        if ACTION == 'move':
            shutil.move(f, new_path)
            logging.info('moved ...\{} to ...\{}'.format(file_name,new_name))
        elif ACTION == 'copy2':
            shutil.copy2(f, new_path)
            logging.info('copied ...\{} to ...\{}'.format(file_name,new_name))
    else:
        logging.info('NOT moved ...\{} to ...\{} since diff = {} with threshold set at +-{}'.format(file_name, new_name, min_diff, VALID_THRESH))

    logging.debug('='*10)
    logging.debug('{} [{} s] @{}'.format(file_name, get_video_duration(new_path), format(datetime.datetime.fromtimestamp(moment))))
    logging.debug('{} @{}'.format(new_name, format(datetime.datetime.fromtimestamp(value))))
    
logging.info('tot: {} files'.format(counter))        

    
    



