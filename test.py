import threading
import pyaudio
import wave
import time
from pynput import keyboard as kb
import msvcrt
import sys

def clear_input_buffer():
    while msvcrt.kbhit():
        msvcrt.getch()

class controll_recorder:
    def __init__(self) -> None:
        self.recording = False
        self.audio_frames = []
        self.listener = None
        self.audio = None
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.RECORD_SECONDS = 5
        self.OUTPUT_FILENAME = "input.wav"
        self.listener = None
        self.first_list = False

    def on_press(self, key):
        try:
            if key.char == 'v':
                if not self.recording:
                    print("Recording started.")
                    self.recording = True
                    self.audio_frames = []
                    threading.Thread(target=self.start_recording).start()
            elif key == kb.Key.esc:
                clear_input_buffer()
                return False

        except AttributeError:
            clear_input_buffer()
            if self.first_list == True:
                sys.stdout.write('\r' + ' '*50 + '\r')
                
            print('请长按V输入语音'.format(key, key.value.vk))
            self.first_list = True

    def on_release(self, key):
        try:
            if key.char == 'v':
                if self.recording:
                    print("Recording stopped.")
                    self.recording = False
                    threading.Thread(target=self.stop_recording).start()

            elif key == kb.Key.esc:
                clear_input_buffer()
                return False
        except AttributeError:
            clear_input_buffer()
            pass
    def start_recording(self):
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=self.FORMAT,
                            channels=self.CHANNELS,
                            rate=self.RATE,
                            input=True,
                            frames_per_buffer=self.CHUNK)

        while self.recording:
            data = self.stream.read(self.CHUNK)
            self.audio_frames.append(data)

        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

    def stop_recording(self):
        wave_file = wave.open(self.OUTPUT_FILENAME, 'wb')
        wave_file.setnchannels(self.CHANNELS)
        wave_file.setsampwidth(self.audio.get_sample_size(self.FORMAT))    # Returns the size (in bytes) for the specified sample format.
        wave_file.setframerate(self.RATE)
        wave_file.writeframes(b''.join(self.audio_frames))
        wave_file.close()
        self.listener.stop()



def main():
    controller = controll_recorder()
    while 1:
        controller.listener = kb.Listener(on_press=controller.on_press, on_release=controller.on_release)
        controller.listener.start()
        controller.listener.join()
        print(1)

if __name__ == "__main__":
    main()
