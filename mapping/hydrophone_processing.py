import numpy
from scipy.io.wavfile import read
import matplotlib.pyplot as plt
import time

in_path = "C:/foam/sonic_kayaks/sandbox/sound_test_processing"
out_path = "C:/foam/sonic_kayaks/sandbox/sound_test_processing"
in_file = "audio-1-pure-fixed.wav"
out_file = "foi.txt" #frequency of interest text file

#sound card corrections - created by Jo Garrett in the lab
sc_corrction_file = "correction_factor_csl_soundcard.csv"
sc_corr = numpy.genfromtxt(path + "/" + sc_corrction_file, delimiter=",")

###########
#functions#
###########

#pre Hann and Hann processing 
def hann_processing(sub_data, int_num, vrange, frate):
    #convert to float
    fl_sub = sub_data/int_num
    #account for voltage range
    fl_sub = fl_sub*vrange
    hann_win = numpy.hanning(frate)
    data_win = fl_sub*hann_win
    return(data_win)

#fft processes - takes a Hann windowed array and array of soundcard corrections
def fft_processing(windowed_array, sc_corr):
    data_fft = numpy.fft.fft(windowed_array)
    #remove imaginary values and correct for sound card
    data_fft_corr = abs(data_fft)/sc_corr
    #return the amplitude cut off by Hann window
    data_fft_corr = data_fft_corr/0.5
    return(data_fft_corr)

#volts to micropascals - takes fft data and outputs micropascals
def volts_to_mpsc(fft_array, frate):
    data_mp = fft_array.conj()*fft_array/(frate**2)
    data_mp_shift = numpy.fft.fftshift(data_mp)
    #subset the data
    sub_data_mp_shift = (data_mp_shift[0:int(frate/2)]*2)/1.5
    return(sub_data_mp_shift)

#psd to decibels
def psd_to_db(psd_array):
    db = numpy.log10(psd_array)*10
    return(db)

#pull out frequency slices of interest, sum and return as decibels, and append to a results collector
def slice_freq(psd_array, min_freq, max_freq, results_array):
    sliced_freq = psd_array[min_freq:max_freq]
    sum_freq = sum(sliced_freq)
    db_out = psd_to_db(sum_freq)
    results_array.append(round(db_out, 4))

###########
#constants#
###########

#voltage range of hydrophone (can vary)
vrange = 1
int_num = 32768
sec_drop = 60 # number of seconds to drop as system starts up 

#hydrophone sensitivity
hydro_sens_db = -181.5 #decibels
hydro_sens_p = 10**(hydro_sens_db/20) #micropascals

##################################
##DEFINE FREQUENCIES OF INTEREST##
##################################

#boat range example (numbers in hz)
b_b_range = [10,100] # big boats
b_m_range = [100,1000] # medium boats

#empty list to collect decibel results
big_boat = [] 
medium_boat = []

#########################
##read and prepare data##
#########################

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
    
#loop through 1 second windows
for i in range(sec_drop, len(window_start)):
    #subset data
    sub_data = numpy.array(raw[1][window_start[i]:window_end[i]],dtype=float)
    #account for hydrophone sensitivity
    sub_data = sub_data/hydro_sens_p
	#perform various proecessing stages
    data_win = hann_processing(sub_data, int_num, vrange, frate)
    data_fft_corr = fft_processing(data_win, sc_corr)
    mp_data = volts_to_mpsc(data_fft_corr, frate)

    #slice data for frequency ranges of interest
    slice_freq(mp_data, b_b_range[0], b_b_range[1], big_boat) #big boats
    slice_freq(mp_data, b_m_range[0], b_m_range[1], medium_boat) #medium boats
        
    #convert to decibels - only for display purposes
    #data_db = numpy.log10(sub_data_mp_shift)*10
    #drop nans
    #data_db = data_db[numpy.isfinite(data_db)]
    #reference pressure in water is 1 so does not need to be corrected
    #whereas in air it is 20. Decibels in water and air not directly
    #comparable.

##write out sum of decibels per second for each frequency slice of interest
np.savetxt(out_path + "/" + out_file, np.transpose([big_boat,medium_boat]), 
           fmt="%s", delimiter = ",", header = "big_boat,medium_boat", 
           comments='')