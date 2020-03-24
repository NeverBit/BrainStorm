import bson
import json
from pathlib import Path
from PIL import Image as PIL


def parse_col_img(context, snapshot):
    ''' Parses the color image out of the snapshot '''
    # Loading the image from the path provided
    image = context.get_encoded_image(snapshot.col_img_path)

    def split3(data):
        ''' A generator which returns the image RGB values in triplets '''
        for i in range(0, image.width * image.height * 3, 3):
            yield tuple(data[i:i + 3])
    pil_image = PIL.new('RGB', (image.width, image.height))
    finaldata = tuple(split3(image.data))
    pil_image.putdata(finaldata)
    save_path = context.get_storage_path(
    ) / f'{snapshot.user_info.uid}_{snapshot.datetime}_color_image.jpg'
    save_path = save_path.absolute()
    
    pil_image.save(save_path)
    res_dict = {'data_path': str(save_path)}
    j = json.dumps(res_dict)
    return j


parse_col_img.field = 'color_image'
