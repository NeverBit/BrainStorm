from BrainStorm.image import image as im


def test__serialize_deserialize_same__color_img(tmp_path):
    img = im(2, 2, (b'\xff\x00\x00'
                    b'\x00\xff\x00'
                    b'\x20\x20\x00'
                    b'\x80\x80\xff'))
    img2 = im.fromDict(img.toDict())

    assert repr(img) == repr(img2)


def test__serialize_deserialize_same__depth_img():
    img = im(2, 2, [0.0, 1.0, 1.0, 0.0])
    img2 = im.fromDict(img.toDict())

    assert repr(img) == repr(img2)
