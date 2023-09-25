#!/usr/bin/env python3
#
# Filename: gaze_contingent_window.py
# Author: Zhiguo Wang
# Date: 2/6/2021
#
# Description:
# A script that displays a Cookie Monster image at the top center of the screen
# and shows a red pointer at the gaze position using PsychoPy and EyeLink.

import pylink
from psychopy import visual, core, event, clock
from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy

# Connect to the tracker
tk = pylink.EyeLink('100.1.1.1')

# Open an EDF data file
tk.openDataFile('psychopy.edf')

# Put the tracker in offline mode before we change tracking parameters
tk.setOfflineMode()

# Make all types of sample data available over the link
sample_flags = 'LEFT,RIGHT,GAZE,GAZERES,PUPIL,HREF,AREA,STATUS,INPUT'
tk.sendCommand(f'link_sample_data  = {sample_flags}')

# Screen resolution
SCN_W, SCN_H = (1280, 800)

# Open a Psychopy window with the "allowStencil" option 
win = visual.Window((SCN_W, SCN_H), fullscr=False, units='pix', allowStencil=True)

# Pass the display pixel coordinates (left, top, right, bottom) to the tracker
coords = f"screen_pixel_coords = 0 0 {SCN_W - 1} {SCN_H - 1}"
tk.sendCommand(coords)

# Request Pylink to use the custom EyeLinkCoreGraphicsPsychoPy library
# to draw calibration graphics (target, camera image, etc.)
genv = EyeLinkCoreGraphicsPsychoPy(tk, win)
pylink.openGraphicsEx(genv)

# Calibrate the tracker
calib_msg = visual.TextStim(win, text='Press ENTER to calibrate')
calib_msg.draw()
win.flip()
tk.doTrackerSetup()

# Load the Cookie Monster image
cookie_monster_img = visual.ImageStim(win, image='cookie_monster.jpg', size=(200, 200))
cookie_monster_img.pos = (0, SCN_H / 2 - 100)  # Position at the top center

# Create a red pointer stimulus
red_pointer = visual.Circle(win, radius=5, fillColor='red', lineColor='red')

# Create a "Welcome" text stimulus
welcome_text = visual.TextStim(win, text='Welcome', pos=(0, -50), height=40, color='white')

# Create two different sentences of text
sentence1 = visual.TextStim(win, text='Sentence 1', pos=(0, -50), height=40, color='white')
sentence2 = visual.TextStim(win, text='Sentence 2', pos=(0, -50), height=40, color='white')

# Define the bounding box around the Cookie Monster image
cookie_monster_bbox = visual.Rect(win, width=200, height=200, pos=cookie_monster_img.pos)

# Put tracker in Offline mode before we start recording
tk.setOfflineMode()

# Start recording
tk.startRecording(1, 1, 1, 1)

# Cache some samples
pylink.msecDelay(100)

# Initialize a variable to track whether the "Welcome" text is displayed
welcome_displayed = False

# Initialize a variable to track whether the gaze is on the Cookie Monster
gaze_on_cookie_monster = False

# Initialize a clock to measure the duration of gaze on the Cookie Monster
gaze_start_time = None

# Initialize a variable to track the state of the program
program_state = 'running'

# Show the Cookie Monster image at the beginning of the experiment
cookie_monster_img.draw()
win.flip()

# Show the red pointer at the gaze coordinates
while program_state == 'running':
    # Check for new samples 
    smp = tk.getNewestSample() 
    if smp is not None:
        if smp.isRightSample():
            gaze_x, gaze_y = smp.getRightEye().getGaze()
        elif smp.isLeftSample():
            gaze_x, gaze_y = smp.getLeftEye().getGaze()
        
        # Calculate PsychoPy coordinates
        psycho_x = gaze_x - SCN_W / 2.0
        psycho_y = SCN_H / 2.0 - gaze_y
        
        # Draw the red pointer at the gaze position
        red_pointer.pos = (psycho_x, psycho_y)
        red_pointer.draw()
        
        # Check if gaze is within the bounding box of the Cookie Monster image
        if cookie_monster_bbox.contains(psycho_x, psycho_y):
            # Start timing the gaze duration on the Cookie Monster
            if not gaze_on_cookie_monster:
                gaze_start_time = clock.getTime()
            gaze_on_cookie_monster = True
        else:
            gaze_on_cookie_monster = False
        
        # If gaze has been on the Cookie Monster for more than 2 seconds, display "Welcome" text
        if gaze_on_cookie_monster and (clock.getTime() - gaze_start_time >= 2):
            # Display the "Welcome" text and change program state
            if not welcome_displayed:
                welcome_text.draw()
                win.flip()
                welcome_displayed = True
                program_state = 'welcome'
        else:
            welcome_displayed = False
        
        win.flip()

# Display the sentences based on the program state
if program_state == 'welcome':
    core.wait(1)  # Display "Welcome" text for 1 second
    sentence1.draw()
    win.flip()
    core.wait(1)  # Display Sentence 1 for 1 second
    sentence2.draw()
    win.flip()
    core.wait(1)  # Display Sentence 2 for 1 second

# Stop recording
tk.stopRecording()

# Put the tracker to offline mode 
tk.setOfflineMode()

# Close the EDF data file on the Host 
tk.closeDataFile()

# Download the EDF data file from Host
tk.receiveDataFile('psychopy.edf', 'psychopy.edf')

# Close the link to the tracker
tk.close()

# Close the graphics
win.close()
core.quit()
