import json
from pathlib import Path
from PIL import Image as PIL


def parse_col_img(context,snapshot):
    save_path = context.get_storage_path() / 'color_image.jpg'
    image = snapshot.col_img
    def split3(data):
        for i in range(0,image.width*image.height*3,3):
            yield tuple(data[i:i+3])
    print(f' @@@ Debug writing a picture of dimension: {image.width}x{image.height}')
    pil_image = PIL.new('RGB', (image.width, image.height))
    finaldata = tuple(split3(image.data))
    pil_image.putdata(finaldata)
    pil_image.save(save_path)
    print(f' @@@ Debug writing a picture of dimension: {image.width}x{image.height} -- done')
    img_location = json.dumps({'path':save_path.absolute().name})
    print(f' @@@ DEBUG Saving image location json : {img_location}')
    context.save('col_img_location.txt',img_location)
parse_col_img.field = 'color_image'
