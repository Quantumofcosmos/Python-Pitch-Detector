# Python-Pitch-Detector

This application is aimed to detect the music note when a sound is played to it.

The app uses pyaudio for processing audio. fft function of numpy module to detect the frequency and tkinter for GUI.

**Demo:**

![Demo](pitch_detect.gif)

The GUI shows the detected frequency, Nearest musical note and octave, by how many cents the sound is in detune to the displayed note and a visual representation of the detune amount.
