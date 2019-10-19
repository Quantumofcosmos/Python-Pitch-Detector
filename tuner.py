#!/usr/bin/python

import pyaudio
import struct
import numpy as np
from tkinter import *
from tkinter import ttk
from math import log2, pow, floor


class SpectrumAnalyzer():
    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.notename = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        self.initMicrophone()
        self.inittkr()
        self.nxt = 1

    def noteFromPitch( self,freq ):
        noteNum = round(12*log2(freq/440))
        return round( noteNum ) + 69

    def frequencyFromNoteNumber( self, note ):
        return 440 * pow(2,(note-69)/12)

    def breaker( self ):
        self.nxt = 0

    def centsOffFromPitch(self, frequency, note ):
        return floor( 1200 * log2( frequency / self.frequencyFromNoteNumber( note )) )

    def find_input_device(self):
        device_index = None
        for i in range(self.pa.get_device_count()):
            devinfo = self.pa.get_device_info_by_index(i)
            if devinfo["name"].lower() in ["mic","input"]:
                device_index = i
        return device_index

    def initMicrophone(self):
        device_index = self.find_input_device()
        self.stream = self.pa.open(    format = pyaudio.paInt16,
                                    channels = 1,
                                    rate = 88200,
                                    input = True,
                                    input_device_index = device_index,
                                    frames_per_buffer = 44100)

    def inittkr(self):
        self.root = Tk()
        self.note = "B"
        self.accent = "#"
        self.content = ttk.Frame(self.root, padding=(3,3,12,12))
        self.notelbl = ttk.Label(self.content, text="A", width=2,font=("Courier", 65))
        self.acntlbl = ttk.Label(self.content, text="#", width=10)
        self.ptchlbl = ttk.Label(self.content, text="#", width=6)
        self.progbar = ttk.Progressbar(self.root, orient = HORIZONTAL, length = 200, mode = 'indeterminate')
        self.content.grid(column=0, row=0)
        self.ptchlbl.grid(column=0, row=0, padx=5, pady=5)
        self.notelbl.grid(column=0, row=1, padx=5, pady=5)
        self.acntlbl.grid(column=0, row=2, padx=5, pady=5)
        self.progbar.grid(column=0, row=3, padx=0, pady=0)
        self.progbar['value'] = 20
        self.root.geometry("250x200+400+300")
        self.root.title("Pitch detector")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.bind('<Escape>', lambda e: self.breaker())

    def readData(self):
        block = self.stream.read(44100)
        count = len(block)/2
        format = "%dh"%(count)
        shorts = struct.unpack( format, block )
        return np.array(shorts)

    def close(self):
        self.stream.close()
        sys.exit()

    def get_spectrum(self, data):
        T = 1.0/44100
        data = np.pad(data, (0, 44100), 'constant', constant_values=(0))
        N = data.shape[0]
        Pxx = (1./N)*np.fft.fft(data)
        f = np.fft.fftfreq(N,T)
        Pxx = np.fft.fftshift(Pxx)
        f = np.fft.fftshift(f)
        return f.tolist(), (np.absolute(Pxx)).tolist()

    def mainLoop(self):
        while self.nxt:
            try:
                data = self.readData()
            except IOError:
                continue
            f, Pxx = self.get_spectrum(data)
            global start_time,notename
            asd = Pxx[44100:46100]
            self.pitch1 = asd.index(max(asd))
            self.notenum = self.noteFromPitch(self.pitch1)
            self.note = self.notename[self.notenum%12]
            self.note1 = self.note+str((self.notenum//12)-1)
            self.detune1 = self.centsOffFromPitch(self.pitch1,self.notenum)
            self.root.update()
            self.ptchlbl.config(text=str(self.pitch1)+"Hz", width=len(str(self.pitch1))+2)
            self.notelbl.config(text=self.note1, width=len(self.note1))
            if self.detune1>0:
                self.acntlbl.config(text=str(self.detune1)+" cents #", width=len(str(self.detune1))+8)
                self.progbar['value'] = self.detune1 + 50
            elif self.detune1<0:
                self.acntlbl.config(text=str(np.absolute(self.detune1))+" cents ♭", width=len(str(self.detune1))+8)
                self.progbar['value'] = self.detune1 + 50
            elif self.detune1==0:
                self.acntlbl.config(text="--", width=2)
                self.progbar['value'] = self.detune1 + 50
            # print(self.note1)

if __name__ == '__main__':
    sa = SpectrumAnalyzer()
    print("Press Escape to exit window.")
    sa.mainLoop()
