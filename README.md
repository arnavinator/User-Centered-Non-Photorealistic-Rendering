# Image and Video Processor

Our application can take in either a .mp4, .jpg, or .png and apply a wide variety of filters and tone mappings to them. Additionally, we have implemented an automatic background remover tool. 

# Setup
Please run the code below to ensure that your branch is properly set up and trained to run our code.
>	bash setup.sh

# Images/Videos
You can use the integrated file explorer to search through any directory for your inputted image.

However, if you plan on using the foreground-background separator you must have the imaged save to the included Images folder.  

Any saved images or video will be save to the same directory that the code was run in. You can input a name for your saved file in the box next to the save button in the interface. Video will be saved under render.avi, and cannot be changed. 

Finally, we have provided an image called sample.jpg as a useful start to your exploration of our system

# Dependencies
You will require the following packages for python. Please be sure to have them installed before hand. 
>	tensorflow, PIL, PySimpleGUI, cv2, numpy, io, os, sys, datetime

If you are not sure that these packages are installed, you can run the following code to update your environement:
>	pip3 install -r requirements.txt

Note, you may also need to use pip instead

# Running
All you need to do to run the code is the following:
>	python3 interface.py										   									 

We hope you have fun playing with our application! Note, there are still some kinks within the program, which are noted in our report.