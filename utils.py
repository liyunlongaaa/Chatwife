import logging
from json import loads
from torch import load, FloatTensor
from numpy import float32
import librosa
import threading
import pyaudio
import wave
import time
from pynput import keyboard as kb
import sys
import msvcrt

class HParams():
  def __init__(self, **kwargs):
    for k, v in kwargs.items():
      if type(v) == dict:
        v = HParams(**v)
      self[k] = v

  def keys(self):
    return self.__dict__.keys()

  def items(self):
    return self.__dict__.items()

  def values(self):
    return self.__dict__.values()

  def __len__(self):
    return len(self.__dict__)

  def __getitem__(self, key):
    return getattr(self, key)

  def __setitem__(self, key, value):
    return setattr(self, key, value)

  def __contains__(self, key):
    return key in self.__dict__

  def __repr__(self):
    return self.__dict__.__repr__()


def load_checkpoint(checkpoint_path, model):
  checkpoint_dict = load(checkpoint_path, map_location='cpu')
  iteration = checkpoint_dict['iteration']
  saved_state_dict = checkpoint_dict['model']
  if hasattr(model, 'module'):
    state_dict = model.module.state_dict()
  else:
    state_dict = model.state_dict()
  new_state_dict= {}
  for k, v in state_dict.items():
    try:
      new_state_dict[k] = saved_state_dict[k]
    except:
      logging.info("%s is not in the checkpoint" % k)
      new_state_dict[k] = v
  if hasattr(model, 'module'):
    model.module.load_state_dict(new_state_dict)
  else:
    model.load_state_dict(new_state_dict)
  logging.info("Loaded checkpoint '{}' (iteration {})" .format(
    checkpoint_path, iteration))


def get_hparams_from_file(config_path):
  with open(config_path, "r") as f:
    data = f.read()
  config = loads(data)

  hparams = HParams(**config)
  return hparams


def load_audio_to_torch(full_path, target_sampling_rate):
  audio, sampling_rate = librosa.load(full_path, sr=target_sampling_rate, mono=True)
  return FloatTensor(audio.astype(float32))


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
        self.out_AttributeError = False
        self.terminate = False
    def on_press(self, key):
        try:
            if key == kb.Key.esc:
                clear_input_buffer()
                self.terminate = True
                exit()
            elif key.char == 'v':
                if not self.recording:
                    if self.out_AttributeError == True:
                      sys.stdout.write('\r' + ' '*50 + '\r')
                      self.out_AttributeError == False
                    sys.stdout.write('\r' + "Recording....")
                    self.recording = True
                    self.audio_frames = []
                    threading.Thread(target=self.start_recording).start()
        except AttributeError:
            clear_input_buffer()

    def on_release(self, key):
        try:
            if key == kb.Key.esc:
                clear_input_buffer()
                self.terminate = True
                exit()
            elif key.char == 'v':
                if self.recording:
                    self.recording = False
                    threading.Thread(target=self.stop_recording).start()
        except AttributeError:
            clear_input_buffer()
            sys.stdout.write('\r' + '主人请长按V输入语音与我对话哦~')
            sys.stdout.flush()
            self.out_AttributeError = True

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
        sys.stdout.write('\r' + ' '*50 + '\r')
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
