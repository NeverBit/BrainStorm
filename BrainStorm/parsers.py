import json
from pathlib import Path
from PIL import Image as PIL


registered_parsers = {}


def parser(name):
    def wrapper(func):
        registered_parsers[name] = func
        return func
    return wrapper

@parser('translation')
def trans_parser(context,snapshot):
    save_path = context.dir / 'translation.json'
    with open(save_path,'w') as f:
        j = json.dumps(snapshot.translation)
        f.write(j)

@parser('color_image')
def col_img_parser(context,snapshot):
    save_path = context.dir / 'color_image.jpg'
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
