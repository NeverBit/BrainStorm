import bson
import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from PIL import Image as PIL


def parse_col_img(context,snapshot):
    # Loading the image from the path provided

    print(' @@@ Debug requesting DEPTH image from context')
    image = context.get_image(snapshot.dep_img_path)
    print(' @@@ Debug GOT image from context')

    x = np.array(image.data)
    x = x.reshape(image.height, image.width)  # or
    plt.imshow(x, cmap='hot', interpolation='nearest')
    
    
    print(' @@@ Debug PLOTTING')
    save_path = context.get_storage_path() / f'{snapshot.uid}_{snapshot.datetime}_depth_image.jpg'
    plt.savefig(save_path)
    print(' @@@ Debug PLOTTEEDDDD')
    print(f' @@@ Debug writing a picture of dimension: {image.width}x{image.height} to {save_path} -- done')
    return {'path':str(save_path)}
parse_col_img.field = 'depth_image'
