from PIL import Image
from BrainStorm import mindreader


rr = mindreader.reader(open('../Desktop/sample.mind', 'rb'))

print(rr)
for i in range(0, 1000):
    print(i)
    snap = rr.read_snapshot()

    def split3():
        for i in range(0, snap.col_img.w * snap.col_img.h * 3, 3):
            yield tuple(snap.col_img.data[i:i + 3])

    image = Image.new('RGB', (snap.col_img.w, snap.col_img.h))
    finaldata = tuple(split3())
    image.putdata(finaldata)
    image.save(f'../Desktop/my_img{i}.bmp')
