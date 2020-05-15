from PIL import Image

im = Image.open('testdata.png')
rgb_im = im.convert('RGB')

def get_ch(rbg_im,ch):
    ar=[]
    for x in range(0,1200,10):
        v = 0
        for y in range(0,500,1):
            if v<1 and rgb_im.getpixel((x, y))[ch]>127:
                v=(500-y)
        ar.append(v/500.0)
    return ar

with open("fake-sensors.csv", 'w') as f:
    t = get_ch(rgb_im,0)
    a = get_ch(rgb_im,1)
    m = get_ch(rgb_im,2)
    for i in range(0,len(t)):
        # give them realistic ranges
        f.write(str((t[i]*5)+10)+","+str(int(a[i]*100))+","+str(int((m[i]*200)+700))+"\n")
