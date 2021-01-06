import PySimpleGUI as sg
import cv2
import numpy as np
import os

# function to create interface
def main():

	# select theme
	sg.theme('LightGray1')

	# ------ Get the filename ----- #
	filename = sg.popup_get_file('Filename to play')
	if filename == '':
		raise NameError('Please select a file')

	#retrieve useful data about the filename
	length = len(filename)
	count = 0
	for char in reversed(filename):
		if char == '/':
			break
		count += 1

	fname = filename[length - count: length - 4]
	ext = filename[length - 4:length]
	
	# depending on file type, save image in usable format
	
	# determine whether input is still or video 
	toggle = True
	if ext == '.mp4':
		rem = cv2.VideoCapture(filename)
		vidFile = rem
		num_frames = vidFile.get(cv2.CAP_PROP_FRAME_COUNT)
	elif ext == '.jpg' or ext == '.png':
		vidFile = cv2.imread(filename)
		toggle = False
		num_frames = 1
	else:
		print('Only accepting .png, .jpg, or .mp4')

	# define the window layout

	# organize the first column, which displays the image
	image = [
		[sg.Button('Separate Foreground from Background', visible=not toggle)],
		[sg.Image(filename='', key='-IMAGE-')],
		[
			sg.Button("Play/Pause", visible=toggle),
			sg.Slider(range=(0, num_frames),
					  size=(60, 10), orientation='h', visible=toggle, key='-PLAY SLIDER-')
		],
		[sg.Button('Exit', size=(10, 1)),
		sg.Button('Save', size=(10, 1), visible=not toggle),
		sg.InputText(key='-TITLE-', visible=not toggle)]

	]

	# organize the second column, which contains all the effects

	# filtering functionality
	effects = [
		[sg.Text('Effects')],
		[sg.Checkbox('Bilateral Filter', default=False, size=(10, 1), key='-BIFILTER-'),
		sg.Slider((1, 5), 3, 1, orientation='h', size=(20, 15), key='-BIFILTER SLIDER A-'),
		sg.Slider((15, 200), 100, 1, orientation='h', size=(20, 15), key='-BIFILTER SLIDER B-')],
		[sg.Checkbox('Edge Preservation', default=False, size=(10, 1), key='-EPRES-'),
		sg.Slider((0, 200), 100, 1, orientation='h', size=(20, 15), key='-EPRES SLIDER A-'),
		sg.Slider((0, 1), .5, .1, orientation='h', size=(20, 15), key='-EPRES SLIDER B-')],
		[sg.Checkbox('Pencil Sketch', default=False, size=(10, 1), key='-PENCIL-'),
		sg.Slider((0, 200), 200, 1, orientation='h', size=(13, 15), key='-PENCIL SLIDER A-'),
		sg.Slider((0, 1), .5, .1, orientation='h', size=(14, 15), key='-PENCIL SLIDER B-'),
		sg.Slider((0, 0.1), .01, .01, orientation='h', size=(13, 15), key='-PENCIL SLIDER C-')],
		[sg.Checkbox('Stylization', default=False, size=(10, 1), key='-STYLE-'),
		sg.Slider((0, 200), 100, 1, orientation='h', size=(20, 15), key='-STYLE SLIDER A-'),
		sg.Slider((0, 1), .5, .1, orientation='h', size=(20, 15), key='-STYLE SLIDER B-')],
		[sg.Checkbox('Threshold', default=False, size=(10, 1), key='-THRESH-'),
		sg.Slider((0, 255), 128, 1, orientation='h', size=(40, 15), key='-THRESH SLIDER-')],
		[sg.Checkbox('Canny', default=False, size=(10, 1), key='-CANNY-'),
		sg.Slider((0, 255), 128, 1, orientation='h', size=(20, 15), key='-CANNY SLIDER A-'),
		sg.Slider((0, 255), 128, 1, orientation='h', size=(20, 15), key='-CANNY SLIDER B-')],
		[sg.Checkbox('Guassian Blur', default=False, size=(10, 1), key='-BLUR-'),
		sg.Slider((1, 11), 1, 1, orientation='h', size=(40, 15), key='-BLUR SLIDER-')],
		[sg.Checkbox('Hue Shift', default=False, size=(10, 1), key='-HUE-'),
		sg.Slider((0, 225), 0, 1, orientation='h', size=(40, 15), key='-HUE SLIDER-')],
		[sg.Checkbox('Enhance', default=False, size=(10, 1), key='-ENHANCE-'),
		sg.Slider((0, 200), 100, 1, orientation='h', size=(20, 15), key='-ENHANCE SLIDER A-'),
		sg.Slider((0, 1), .5, .1, orientation='h', size=(20, 15), key='-ENHANCE SLIDER B-')]
	]

	# tone shifting functionality
	tone_maps = ['Autumn', 'Bone', 'Jet', 'Winter', 'Rainbow', 'Ocean', 'Summer', 'Spring',
				 'Cool', 'HSV', 'Pink', 'Hot']
	tones = [[sg.Radio(tone, 'tone', size=(10,1), key=str(i))] for i, tone in enumerate(tone_maps)]
	tone_adj = [
			[sg.Radio('Gamma Correction', 'tone', size=(10,1), key='-GAMMA-'),
			sg.Slider((.1,5), 1, .1, orientation='h', size=(40,15), key='-GAMMA PARAM-')],
			[sg.Radio('Histogram Equalization', 'tone', size=(10,1), key='-HISTO EQUAL-')],
			[sg.Radio('Constrast Stretching', 'tone', size=(10,1), key='-CONSTRAST-')]
	]

	# combine effects columns together
	layout_right = [
		[sg.Text('Color Tones')],
		[sg.Radio('None', 'tone', True, size=(10, 1))],
		[sg.Column(tones)],
		[sg.Column(tone_adj)],
		[sg.HSeparator()],
		[sg.Column(effects)]
	]

	# create final layout
	layout_f = [
		[
    		sg.Column(image),
    		sg.VSeparator(),
    		sg.Column(layout_right, size=(400,800), scrollable=True) 
    	]
    ]

	# create the window
	window = sg.Window('OpenCV Integration', layout_f, location=(800, 400))

	# locate the elements we'll be updating
	image_elem = window['-IMAGE-']
	slider_elem = None
	if toggle:
		slider_elem = window['-PLAY SLIDER-']

    # ----- LOOP through video file by frame ----- #
	cur_frame = 0
	paused = False

	# relevant data about tones
	num = [['0', cv2.COLORMAP_AUTUMN], ['1', cv2.COLORMAP_BONE], ['2', cv2.COLORMAP_JET], 
		   ['3', cv2.COLORMAP_WINTER], ['4', cv2.COLORMAP_RAINBOW], ['5', cv2.COLORMAP_OCEAN], 
		   ['6', cv2.COLORMAP_SUMMER], ['7', cv2.COLORMAP_SPRING], ['8', cv2.COLORMAP_COOL], 
		   ['9', cv2.COLORMAP_HSV], ['10', cv2.COLORMAP_PINK], ['11', cv2.COLORMAP_HOT]]   

	vid = []

	while True:
		
		# get information about window
		event, values = window.read(timeout=10)

		# separate background from foreground
		if event == 'Separate Foreground from Background':
			inname = "./Images/" + fname + ext
			outname = "./Images/" + fname + '_foreground.png'
			os.system('python3 seg.py {} {} 1'.format(inname, outname))
			vidFile = cv2.imread(outname)

		# get relevant image info, depending on type 
		if toggle:
			ret, frame = vidFile.read()

			if isinstance(frame, type(None)):
				break
		else: 
			frame = vidFile

		if event == 'Exit' or event == sg.WIN_CLOSED:
			break
		elif event == 'Play/Pause':
			if not paused:
				vidFile = frame
				paused = True
				toggle = False
			else:
				vidFile = rem
				paused = False
				toggle = True

		# apply tones
		for arr in num:
			if values[arr[0]]:
				frame = cv2.applyColorMap(frame, arr[1])

		if values['-GAMMA-']:
			gamma = values['-GAMMA PARAM-']

			invGamma = 1.0 / gamma
			table = np.array([((i / 255.0) ** invGamma) * 255
				for i in np.arange(0, 256)]).astype("uint8")

    		# apply gamma correction using the lookup table
			frame = cv2.LUT(frame, table)
		elif values['-HISTO EQUAL-']:
			img_yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)

			# equalize the histogram of the Y channel
			img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])

			# convert the YUV image back to RGB format
			frame = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2RGB)
		elif values['-CONSTRAST-']:
			norm_img1 = cv2.normalize(frame, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
			norm_img2 = cv2.normalize(frame, None, alpha=0, beta=1.2, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
			# scale to uint8
			norm_img1 = (255*norm_img1).astype(np.uint8)
			norm_img2 = np.clip(norm_img2, 0, 1)
			frame = (255*norm_img2).astype(np.uint8)

		# apply filters
		if values['-BIFILTER-']:
			frame = cv2.bilateralFilter(frame, int(values['-BIFILTER SLIDER A-']), values['-BIFILTER SLIDER B-'], values['-BIFILTER SLIDER B-'])
		if values['-EPRES-']:
			frame = cv2.edgePreservingFilter(frame, flags=1, sigma_s=values['-EPRES SLIDER A-'], sigma_r=values['-EPRES SLIDER B-'])
		if values['-PENCIL-']:
			_, frame = cv2.pencilSketch(frame, sigma_s=values['-PENCIL SLIDER A-'], sigma_r=values['-PENCIL SLIDER B-'], shade_factor=values['-PENCIL SLIDER C-'])
		if values['-STYLE-']:
			frame = cv2.stylization(frame, sigma_s=values['-STYLE SLIDER A-'], sigma_r=values['-STYLE SLIDER B-'])
		if values['-THRESH-']:
			frame = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)[:, :, 0]
			frame = cv2.threshold(frame, values['-THRESH SLIDER-'], 255, cv2.THRESH_BINARY)[1]
		if values['-CANNY-']:
			frame = cv2.Canny(frame, values['-CANNY SLIDER A-'], values['-CANNY SLIDER B-'])
		if values['-BLUR-']:
			frame = cv2.GaussianBlur(frame, (21, 21), values['-BLUR SLIDER-'])
		if values['-HUE-']:
			frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
			frame[:, :, 0] += int(values['-HUE SLIDER-'])
			frame = cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)
		if values['-ENHANCE-']:
			frame = cv2.detailEnhance(frame, sigma_s=values['-ENHANCE SLIDER A-'], sigma_r=values['-ENHANCE SLIDER B-'])
		
		# save image
		if event == 'Save':
			out = values['-TITLE-']
			if ext not in values['-TITLE-']:
				out = values['-TITLE-'] + ext
	
			cv2.imwrite(out, frame)

		# if someone moved the slider manually, the jump to that frame
		if int(values['-PLAY SLIDER-']) != cur_frame-1 and toggle:
			cur_frame = int(values['-PLAY SLIDER-'])
			vidFile.set(cv2.CAP_PROP_POS_FRAMES, cur_frame)

		if toggle:
			slider_elem.update(cur_frame)
			cur_frame += 1

			if cur_frame >= len(vid):
				vid.append(frame)
			else:
				vid.insert(cur_frame, frame)

		# update
		imgbytes = cv2.imencode('.png', frame)[1].tobytes()
		window['-IMAGE-'].update(data=imgbytes)
		image_elem.update(data=imgbytes)

	window.close()

	return vid


video = main()
video = np.array(video)
width = len(video[0])
height = len(video[0][0])
print(height, width)
out = cv2.VideoWriter('render.avi', cv2.VideoWriter_fourcc(*'DIVX'), 15, (height, width))

for i in range(len(video)):
	out.write(video[i])

out.release