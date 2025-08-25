# Script to display PsychoPy using incoming image retrievals/reconstructions 
# from Data Analyzer to use as stimuli in (simulated) real-time

# import needed libraries
import time
from psychopy import core, visual, event
import os 
import json
import numpy as np
import pdb
import PIL
from PIL import Image
import base64
import zlib

def decode_and_decompress_image(encoded_data, shape):
    compressed_data = base64.b64decode(encoded_data)
    decompressed_data = zlib.decompress(compressed_data)
    # Ensure the decompressed data matches the expected size
    expected_size = np.prod(shape)
    if len(decompressed_data) != expected_size:
        raise ValueError(f"Decompressed data size {len(decompressed_data)} does not match expected size {expected_size}")
    image_array = np.frombuffer(decompressed_data, dtype=np.uint8).reshape(shape)
    return image_array

# function to get PIL image from nump array 
def np_to_Image(x):
    '''
    x: this is a 3D numpy array
    
    returns a PIL image
    '''
    if x.ndim == 4:
        x = x[0]
    
    if x.dtype == np.uint8:
        image_array = x
    else:
        image_array = (x.transpose(1, 2, 0) * 127.5 + 128).clip(0, 255).astype('uint8')
        
    return Image.fromarray(image_array, mode='RGB')


# Specify analysis_listener outputs folder
absolute_path = "/Volumes/norman/rsiyer/rt_mindeye" # TODO fill this in where your rt-cloud directory is cloned on your analysis listener computer
outPath = f"{absolute_path}/rt-cloud/outDir"
recons_or_retrievals = "ret"
# Setup variables
starting_TR = 0
end_TR = 192
numRuns = 11

# Setup the Window
win = visual.Window(
    size=[1080,720], fullscr=False, 
    screen=0, allowGUI=True, allowStencil=False,
    monitor='testMonitor', color=[0,0,0], colorSpace='rgb',
    blendMode='avg', useFBO=True, units='pix')
win.mouseVisible = False

# set up waiting screen
waiting = visual.TextStim(win, pos=[0, 0], text="Waiting...",
                            name="Waiting",height=100,wrapWidth=1000)
waiting.draw()
win.flip()

# go through a run!
for run in range(1, numRuns+1):
    print(f"run {run}")
    # go through each TR
    for TR in range(0, 191):
        # print('starting with TR 35 for debugging')
        print(f"TR {TR}")
        filename = f'{outPath}/run{run}_TR{TR}.json'
        print("filename: ", filename)
        # Wait for file to be synced
        while not os.path.exists(filename):
            keys_pressed = event.getKeys()
            if "escape" in keys_pressed: core.quit() # allow escape key to quit experiment
            time.sleep(.1) # retry every 100ms
        time.sleep(.1) # buffer to prevent opening file before fully saved
        results_not_read = True
        while results_not_read:
            try:
                with open(filename) as f:
                    results = json.load(f)
                print("read!")
                # breakpoint()
                results_not_read = False
            except:
                print("results not reading yet!")

        for key in results:
            if ((key in ('ground_truth', 'recons')) or ('attempt' in key)) \
                and isinstance(results[key], str):  # Assuming encoded image data is stored as strings
                # Provide the original shape of the image
                original_shape = (224, 224, 3)
                # breakpoint()
                results[key] = decode_and_decompress_image(results[key], original_shape)
                print(f'key {key} decoded and decompressed')

        if "pass" in results:
            win.flip()
            print("passed, not MST image")
            continue

        # save the images
        os.makedirs('images', exist_ok=True)
        ground_truth_path = f"images/ground_truth_run{run}_TR{TR}.png"
        reconstruction_path = f"images/recon_run{run}_TR{TR}.png"
        attempt1_path = f"images/attempt1_run{run}_TR{TR}.png"
        attempt2_path = f"images/attempt2_run{run}_TR{TR}.png"
        attempt3_path = f"images/attempt3_run{run}_TR{TR}.png"
        attempt4_path = f"images/attempt4_run{run}_TR{TR}.png"
        attempt5_path = f"images/attempt5_run{run}_TR{TR}.png"
        np_to_Image(np.array(results["ground_truth"])).save(ground_truth_path)
        np_to_Image(np.array(results["recons"])).save(reconstruction_path)
        np_to_Image(np.array(results["attempt1"])).save(attempt1_path)
        np_to_Image(np.array(results["attempt2"])).save(attempt2_path)
        np_to_Image(np.array(results["attempt3"])).save(attempt3_path)
        np_to_Image(np.array(results["attempt4"])).save(attempt4_path)
        np_to_Image(np.array(results["attempt5"])).save(attempt5_path)

        # now display the images
        if recons_or_retrievals == "ret":
            size = 0.2
            pos_put_x = 0.2
            text_y = 0.25
            y_retrieval = -0.15

            image_groundTruth = visual.ImageStim(
                win=win,
                name='image', units='height', 
                image=f'{ground_truth_path}', mask=None, anchor='center',
                ori=0.0, pos=(-pos_put_x, -y_retrieval), size=(size, size),
                color=[1,1,1], colorSpace='rgb', opacity=None,
                flipHoriz=False, flipVert=False,
                texRes=128.0, interpolate=True, depth=0.0)
            
            image_reconstruction = visual.ImageStim(
                win=win, name='recon', units='height', image=f'{reconstruction_path}',
                pos=(pos_put_x, -y_retrieval), size=(size, size), color=[1,1,1], colorSpace='rgb')
            
            image_ret1 = visual.ImageStim(
                win=win,
                name='image', units='height', 
                image=f'{attempt1_path}', mask=None, anchor='center',
                ori=0.0, pos=(-2*pos_put_x, y_retrieval), size=(size, size),
                color=[1,1,1], colorSpace='rgb', opacity=None,
                flipHoriz=False, flipVert=False,
                texRes=128.0, interpolate=True, depth=0.0)
            image_ret2 = visual.ImageStim(
                win=win,
                name='image', units='height', 
                image=f'{attempt2_path}', mask=None, anchor='center',
                ori=0.0, pos=(-pos_put_x, y_retrieval), size=(size, size),
                color=[1,1,1], colorSpace='rgb', opacity=None,
                flipHoriz=False, flipVert=False,
                texRes=128.0, interpolate=True, depth=0.0)
            image_ret3 = visual.ImageStim(
                win=win,
                name='image', units='height', 
                image=f'{attempt3_path}', mask=None, anchor='center',
                ori=0.0, pos=(0, y_retrieval), size=(size, size),
                color=[1,1,1], colorSpace='rgb', opacity=None,
                flipHoriz=False, flipVert=False,
                texRes=128.0, interpolate=True, depth=0.0)
            image_ret4 = visual.ImageStim(
                win=win,
                name='image', units='height', 
                image=f'{attempt4_path}', mask=None, anchor='center',
                ori=0.0, pos=(pos_put_x, y_retrieval), size=(size, size),
                color=[1,1,1], colorSpace='rgb', opacity=None,
                flipHoriz=False, flipVert=False,
                texRes=128.0, interpolate=True, depth=0.0)
            image_ret5 = visual.ImageStim(
                win=win,
                name='image', units='height', 
                image=f'{attempt5_path}', mask=None, anchor='center',
                ori=0.0, pos=(2*pos_put_x, y_retrieval), size=(size, size),
                color=[1,1,1], colorSpace='rgb', opacity=None,
                flipHoriz=False, flipVert=False,
                texRes=128.0, interpolate=True, depth=0.0)
            

            image_ret1.draw()
            image_ret2.draw()
            image_ret3.draw()
            image_ret4.draw()
            image_ret5.draw()
            # textstimlike=visual.TextBox(
            #     window=win,
            #     text="Actual Image",
            #     font_size=18,
            #     font_color=[-1,-1,1],
            #     color_space='rgb',
            #     size=(1.8,.1),
            #     pos=(0.3,.5),
            #     units='norm')
            # textstimlike.draw()

            textstimlike2=visual.TextStim(
                win,
                text="Ground Truth",
                pos=[-140,200],
                height = 20,
                wrapWidth=5000)
            

            textstimlike3=visual.TextStim(
                win,
                text="Reconstruction",
                pos=[145,200],
                height = 20,
                wrapWidth=5000)
            

            textstimlike4=visual.TextStim(
                win,
                text="Top 5 Retrievals (Descending Order)",
                pos=[0,-20],
                height = 20,
                wrapWidth=5000)


# waiting = visual.TextStim(win, pos=[0, 0], text="Waiting...",
#                             name="Waiting",height=100,wrapWidth=1000)
            image_groundTruth.draw()
            image_reconstruction.draw()
            textstimlike2.draw()
            textstimlike3.draw()
            textstimlike4.draw() 

            win.flip()
            time.sleep(8)

win.close()
core.quit()
