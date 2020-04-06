import json
import matplotlib.pyplot as plt
import numpy as np


def parse_dep_img(context, snapshot):
    ''' Parses the depth image out of the snapshot '''
    # Loading the image from the path provided
    image = context.get_encoded_image(snapshot.dep_img_path)

    x = np.array(image.data)
    x = x.reshape(image.height, image.width)
    plt.imshow(x, cmap='hot', interpolation='nearest')

    save_path = context.get_storage_path(
    ) / f'{snapshot.user_info.uid}_{snapshot.datetime}_depth_image.jpg'
    save_path = save_path.absolute()
    plt.savefig(save_path)

    res_dict = {'data_path': str(save_path)}
    j = json.dumps(res_dict)
    return j


parse_dep_img.field = 'depth_image'
