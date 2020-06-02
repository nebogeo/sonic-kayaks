from PIL import Image


def get_ch(rgb_im,ch,length):
    ar=[]
    for x in range(0,length,10):
        v = 0
        for y in range(0,500,1):
            if v<1 and rgb_im.getpixel((x, y))[ch]>127:
                v=(500-y)
        ar.append(v/500.0)
    return ar

def write_out(length,imagename, filename, tc, ac, mc):
    im = Image.open(imagename)
    rgb_im = im.convert('RGB')
    with open(filename, 'w') as f:
        t = get_ch(rgb_im,tc,length)
        a = get_ch(rgb_im,ac,length)
        m = get_ch(rgb_im,mc,length)
        for i in range(0,len(t)):
            # give them realistic ranges
            f.write(str((t[i]*5)+10)+","+str(int(a[i]*100))+","+str(int((m[i]*200)+700))+"\n")

#write_out(1200,"testdata.png","fake-sensors.csv",0,1,2)

# trough is: 0:trough, 1:rise, 2:fall
# peak is is: 0:peak, 1:rise, 2:fall

trough=0
peak=0
rise=1
rall=2

# temp:rise, air:trough, turb:fall
write_out(600,"trough.png","survey-synth.csv",rise,trough,fall) 

# temp:fall, air:rise, turb:peak
write_out(600,"peak.png","survey-sample.csv",fall,rise,peak)

# temp:peak, air:rise, turb:fall
write_out(600,"peak.png","survey-voice.csv",peak,rise,fall)

# temp:trough, air:fall, turb:rise
write_out(600,"trough.png","survey-grain.csv",trough,fall,rise)
