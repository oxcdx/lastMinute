#!/usr/bin/env python

#import twitter
import subprocess
import time
from time import sleep
import urllib2
import picamera
from picamera import PiCamera
import datetime
from datetime import timedelta
#from pymouse import PyMouseEvent
import os
import string

# time stuff
def unix_time(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()

def unix_time_millis(dt):
    return unix_time(dt) * 1000.0
            
# file name and directory stuff
newdir1 = '/home/pi/Pictures/autoImages/'
newfile = 'img{timestamp:%Y-%m-%d-%H-%M}.jpg'
newfull = newdir1 + newfile

# initial clean up of jpgs and any other remaining files from folder on local machine
filelist = [ f for f in os.listdir(newdir1) if f.endswith((".jpg", ".mp4", ".h264")) ]
for f in filelist:
    os.remove(os.path.join(newdir1, f))

camera = picamera.PiCamera()

while True:

    # start camera with desired settings
    camera.vflip = True
    camera.exposure_mode = 'night'
    camera.awb_mode = 'incandescent'
    camera.iso = 100
    #camera.shutter_speed = 1000
    camera.resolution = (1280, 960)
    camera.start_recording('/home/pi/Pictures/autoImages/my_video.h264')
    camera.wait_recording(60)
    camera.stop_recording()
    
    # clean all files except .h264
    filelist = [ f for f in os.listdir(newdir1) if f.endswith((".jpg", ".png", ".mp4")) ]

    
    for f in filelist:
        os.remove(os.path.join(newdir1, f))
    
    from subprocess import call
    
    # create normal video (not reversed)
    #call (["MP4Box -fps 30 -add /home/pi/Pictures/autoImages/my_video.h264 /home/pi/Pictures/autoImages/myvid.mp4"], shell=True)
    
    # convert .h264 to jpg sequence
    call (["ffmpeg -i /home/pi/Pictures/autoImages/my_video.h264 -an -qscale:v 1 /home/pi/Pictures/autoImages/%06d.jpg"], shell=True)

    # navigate to desired folder
    call (["cd /home/pi/Pictures/autoImages/"], shell=True)

    # make mp4 from jpegs in reverse order
    call (["cat $(ls -t *jpg) | ffmpeg -y -f image2pipe -vcodec mjpeg -r 30 -i - -vcodec libx264 -qscale:v 1 -preset slow myvidRev.mp4"], shell=True)

    # filenames for Dropbox Uploader
    photofile = "/home/pi/Dropbox-Uploader/dropbox_uploader.sh upload " + "/home/pi/Pictures/autoImages/myvid.mp4" + " myvid.mp4"
    photofileRev = "/home/pi/Dropbox-Uploader/dropbox_uploader.sh upload /home/pi/Pictures/autoImages/myvidRev.mp4 myvidRev.mp4"

    # call Dropbox upload string for normal video 
    #call ([photofile], shell=True)

    # call Dropbox upload string for reverse video
    call ([photofileRev], shell=True)

    time.sleep(60)

    # clean .h264 file before starting process again
    filelist = [ f for f in os.listdir(newdir1) if f.endswith((".h264")) ]
    for f in filelist:
        os.remove(os.path.join(newdir1, f))

