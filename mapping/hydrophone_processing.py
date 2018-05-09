import numpy
from scipy.io.wavfile import read
import matplotlib.pyplot as plt

path = "C:/foam/sonic_kayaks/sandbox/sound_test_processing"
file = "audio-1-pure-fixed.wav"

#sound card corrections - created by Jo Garrett in the lab
sc_corrction_file = "correction_factor_csl_soundcard.csv"
sc_corr = numpy.genfromtxt(path + "/" + sc_corrction_file, delimiter=",")

###########
#functions#
###########

#psd to decibels
def psd_to_db(psd_array):
    db = numpy.log10(psd_array)*10
    return(db)

#pull out frequency slices of interest, sum and return as decibels
def slice_freq(psd_array, min_freq, max_freq):
    sliced_freq = psd_array[min_freq:max_freq]
    sum_freq = sum(sliced_freq)
    db_out = psd_to_db(sum_freq)
    return(db_out)



###########
#constants#
###########

#voltage range of hydrophone (can vary)
vrange = 1
int_num = 32768
sec_drop = 60 # number of seconds to drop as system starts up 

#hydrophone sensitivity
hydro_sens_db = -181.5
hydro_sens_p = 10**(hydro_sens_db/20) #micropascals

#boat range example (numbers in hz)
b_b_range = [10,100] # big boats
b_m_range = [100,1000] # medium boats

raw = read(path + "/" + file)
frate = raw[0]
total_data_points = len(raw[1])

#50% overlap between windows
window_start = range(0,total_data_points,int(frate/2))
window_end = range(frate,total_data_points,int(frate/2))

#equalise length of indexes
if len(window_start) > len(window_end):
    window_start = window_start[0:len(window_end)]
elif len(window_end) > len(window_start):
    window_end = window_end[0:len(window_start)]


    
#loop through windows
for i in range(sec_drop,len(window_start)):
    #subset data
    sub_data = numpy.array(raw[1][window_start[i]:window_end[i]],dtype=float)
    #account for hydrophone sensitivity
    sub_data = sub_data/hydro_sens_p
    #convert to float
    test = sub_data/int_num
    #account for voltage range
    test = test*vrange
    hann_win = numpy.hanning(frate)
    #plt.plot(hann_win)
    data_win = test*hann_win
    #plt.plot(data_win)

    ##fft 
    data_fft = numpy.fft.fft(data_win)
    #remove imaginary values and correct for sound card
    data_fft_corr = abs(data_fft)/sc_corr
    #return the amplitude cut off by Hann window
    data_fft_corr = data_fft_corr/0.5

    #volts to micropascals
    data_mp = data_fft_corr.conj()*data_fft_corr/(frate**2)
    #plt.plot(temp)
    data_mp_shift = numpy.fft.fftshift(data_mp)
    #subset the data
    sub_data_mp_shift = (data_mp_shift[0:int(frate/2)]*2)/1.5
    
    #slice data for frequency ranges of interest
    b_b_db = slice_freq(sub_data_mp_shift, b_b_range[0], b_b_range[1]) #big boats
    b_m_db = slice_freq(sub_data_mp_shift, b_m_range[0], b_m_range[1]) #medium boats


    ##############################
    ##############################


    #convert to decibels - only for display purposes
    data_db = numpy.log10(sub_data_mp_shift)*10
    #drop nans
    data_db = data_db[numpy.isfinite(data_db)]
    #reference pressure in water is 1 so does not need to be corrected
    #whereas in air it is 20. Decibels in water and air not directly
    #comparable.
    print(i)
    print("done")



