import bson
import json
from pathlib import Path
from PIL import Image as PIL


def parse_col_img(context,snapshot):
    # Loading the image from the path provided

    print(' @@@ Debug requesting image from context')
    image = context.get_encoded_image(snapshot.col_img_path)
    print(' @@@ Debug GOT image from context')

    def split3(data):
        ''' A generator which returns the image RGB values in triplets '''
        for i in range(0,image.width*image.height*3,3):
            yield tuple(data[i:i+3])
    print(f' @@@ Debug writing a picture of dimension: {image.width}x{image.height}')
    pil_image = PIL.new('RGB', (image.width, image.height))
    finaldata = tuple(split3(image.data))
    pil_image.putdata(finaldata)
    save_path = context.get_storage_path() / f'{snapshot.user_info.uid}_{snapshot.datetime}_color_image.jpg'
    print(save_path)
    pil_image.save(save_path)
    print(f' @@@ Debug writing a picture of dimension: {image.width}x{image.height} -- done')
    return {'path':str(save_path)}
parse_col_img.field = 'color_image'
