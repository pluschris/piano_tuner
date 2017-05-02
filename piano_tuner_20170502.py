#!/usr/bin/python3
# project: piano/guitar tuner
# This code permanently records the microphone, calculates the FFT and shows the peak-frequency
# You can use it to tune a piano or guitar buy playing one (piano) string and
# check whether you see the right frequency or not
# (Hint: Normally when you play a piano key you hit several piano strings.
#  Make sure that you only listen to the sound of
#  one piano string, for example by carefully touching the other piano strings with your hand)
# 
# author: Chr. Schmitz
# version V0.3.1
# history:
# V0.3.1: cleaned code
# V0.2.1: added plt.pause to show figure
# date: 2017-05-02

#######################################################################################################################
# import solution
from scipy.fftpack import fft
import time as time
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import blackman
import sounddevice as sd
#######################################################################################################################
# config:
length = 1                              # recording time in seconds # for a 0.5 Hz resolution we need T=2s.
sample_rate = 44100                     # sample rate in Hz
n = int(length * sample_rate)           # number of sample values

#######################################################################################################################
# DEBUG: Read file:
# WAVEFILE = "/PATH/TO/FILENAME.WAV"
# sample_rate, audio = wavfile.read(WAVEFILE)
# audio=audio/32768 # Could be depending on different specs also 32767 or 32760 or whatever. Doesn't matter here.
                    # Long files show an uncertainty in the amplitude. Reason: Because of the big values?
# n=len(audio)

#######################################################################################################################
# init figures:
fig=plt.figure(0)
plt.ion()
plt.gcf().patch.set_facecolor('white')
plt.figure(1)
plt.ion()
plt.gcf().patch.set_facecolor('white')
plt.figure(2)
plt.ion()
plt.gcf().patch.set_facecolor('white')

###################################################################################################################
# read microphone continuously:
while True:
    audio= sd.rec(n, samplerate=sample_rate, channels=1, blocking=True)[:, 0] # just mono, no stereo, so only one column
    ###################################################################################################################
    # DEBUG: sine test-signal with two periods per sampling:
    # n = 100  # sample values per FFT
    # sample_rate = 10
    # t_audio = np.arange(0,n*1/sample_rate,1/sample_rate)
    # audio = np.sin(t_audio/(n*1/sample_rate)*4*np.pi)
    ###################################################################################################################
    # calc FFT: amplitude spectrum
    # filter:
    filter_window = blackman(n)
    spectrum = np.abs(fft(audio * filter_window)[0:int(n / 2)]) / n
    # for a correct amplitude: *2 except DC:
    spectrum[1:int(n/2)]=spectrum[1:int(n/2)]*2
    frequency_display = np.arange(0, n / 2 * sample_rate / n, sample_rate / n)

    # Because of the bad frequency response of the microphone, the current frequency is not the global max, but
    # a local max frequency which is at most ten times smaller than max
    threshold = max(spectrum) / 10
    current_tone=0
    harmonic_2_index=0
    f_half_index=0
    for index in range (0,len(spectrum),1):
        # find first peak:
        if spectrum[index]>(threshold):
            # find local max, top of peak:
            while True:
                if spectrum[index+1]>spectrum[index]:
                    if (index+1 <= int(n/2)):
                        index = index+1
                    else:
                        break
                else:
                    break
            current_tone = frequency_display[index]
            current_tone_index = index
            f_half_index = round(index / 2)
            harmonic_2_index = 2 * index
            break
    max_microphone = frequency_display[np.argmax(spectrum)]

    # find 2nd harmonic +-10 units:
    if harmonic_2_index<10:
        harmonic_2_index=10
    harmonic_2_index= harmonic_2_index - 10 + np.argmax(spectrum[harmonic_2_index - 10:harmonic_2_index + 10])
    harmonic_2 = frequency_display[harmonic_2_index]

    # find f/2 +-10 units:
    if f_half_index<10:
        f_half_index=10
    f_half_index= f_half_index - 10 + np.argmax(spectrum[f_half_index - 10:f_half_index + 10])
    f_half = frequency_display[f_half_index]

    ###################################################################################################################
    # plot:
    # print additionally the first harmonic (2*f) and f/2 (more precise tuning):

    title= "f= " + str(round(current_tone, 1)) + " Hz, max_mic=" + str(round(max_microphone, 1)) + " Hz"
    plt.figure(0)
    plt.clf()
    plt.title(title, fontsize=20)
    plt.semilogy(frequency_display[0:int(n / 2)], spectrum[0:int(n / 2)], '-r') # set slicing here to [0:n/2]
                                                                                # to catch odd n
    plt.xlabel("f/Hz")
    plt.ylabel("Û/V")
    plt.grid()
    plt.xlim(current_tone - 10, current_tone + 10)
    plt.ylim(spectrum[current_tone_index] / 10, spectrum[current_tone_index] * 10)
    plt.draw()
    plt.pause(0.05) # without this line you can't see any drawing (on some computers).
                    # Maybe with this line this script spends the GUI some time to draw
                    # and for the GUI-event-handling? I thought that this could be done parallel (background?)...

    title= "2.harmonic " + str(round(harmonic_2, 1)) + " Hz"
    plt.figure(1)
    plt.clf()
    plt.title(title, fontsize=20)
    plt.semilogy(frequency_display[0:int(n / 2)], spectrum[0:int(n / 2)], '-r') # set slicing here to [0:n/2]
                                                                                # to catch odd n
    plt.xlabel("f/Hz")
    plt.ylabel("Û/V")
    plt.grid()
    plt.xlim(harmonic_2 - 5, harmonic_2 + 5)
    plt.ylim(spectrum[harmonic_2_index] / 10, spectrum[harmonic_2_index] * 10)
    plt.draw()
    plt.pause(0.05)

    title= "f/2 " + str(round(f_half, 1)) + " Hz"
    plt.figure(2)
    plt.clf()
    plt.title(title, fontsize=20)
    plt.semilogy(frequency_display[0:int(n / 2)], spectrum[0:int(n / 2)], '-r') # set slicing here to [0:n/2]
                                                                                # to catch odd n
    plt.xlabel("f/Hz")
    plt.ylabel("Û/V")
    plt.grid()
    plt.xlim(f_half - 5, f_half + 5)
    plt.ylim(spectrum[f_half_index] / 10, spectrum[f_half_index] * 10)
    plt.draw()
    plt.pause(0.05)
    ###################################################################################################################
