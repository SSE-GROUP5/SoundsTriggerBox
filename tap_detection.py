#https://github.com/xSparfuchs/clap-detection/blob/master/clap-detection.py
import pyaudio
import struct
import math

INITIAL_TAP_THRESHOLD = 0.03
FORMAT = pyaudio.paInt16 
SHORT_NORMALIZE = (1.0/32768.0)
CHANNELS = 1
RATE = 44100  
INPUT_BLOCK_TIME = 0.05
INPUT_FRAMES_PER_BLOCK = int(RATE*INPUT_BLOCK_TIME)
# if we get this many noisy blocks in a row, increase the threshold
OVERSENSITIVE = 15.0/INPUT_BLOCK_TIME                    
# if we get this many quiet blocks in a row, decrease the threshold
UNDERSENSITIVE = 120.0/INPUT_BLOCK_TIME 
# if the noise was longer than this many blocks, it's not a 'tap'
MAX_TAP_BLOCKS = 0.15/INPUT_BLOCK_TIME

def get_rms( block ):
    # RMS amplitude is defined as the square root of the 
    # mean over time of the square of the amplitude.
    # so we need to convert this string of bytes into 
    # a string of 16-bit samples...

    # we will get one short out for each 
    # two chars in the string.
    count = len(block)/2
    format = "%dh"%(count)
    shorts = struct.unpack( format, block )

    # iterate over the block.
    sum_squares = 0.0
    for sample in shorts:
        # sample is a signed short in +/- 32768. 
        # normalize it to 1.0
        n = sample * SHORT_NORMALIZE
        sum_squares += n*n

    return math.sqrt( sum_squares / count )

class TapTester(object):
    def __init__(self):
        print("Initializing TapTester...")
        self.pa = pyaudio.PyAudio()
        self.stream = self.open_mic_stream()
        self.tap_threshold = INITIAL_TAP_THRESHOLD
        self.noisycount = MAX_TAP_BLOCKS + 1
        self.quietcount = 0
        self.errorcount = 0
        print("TapTester initialized with tap threshold:", self.tap_threshold)

    def stop(self):
        print("Closing the stream.")
        self.stream.close()

    def find_input_device(self):
        print("Searching for an input device...")
        device_index = None
        for i in range(self.pa.get_device_count()):
            devinfo = self.pa.get_device_info_by_index(i)
            print("Device {}: {}".format(i, devinfo["name"]))

            for keyword in ["mic", "input"]:
                if keyword in devinfo["name"].lower():
                    print("Found an input: device {} - {}".format(i, devinfo["name"]))
                    device_index = i
                    return device_index

        if device_index is None:
            print("No preferred input found; using default input device.")
        return device_index

    def open_mic_stream(self):
        print("Opening microphone stream...")
        device_index = self.find_input_device()
        stream = self.pa.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            input_device_index=device_index,
                            frames_per_buffer=INPUT_FRAMES_PER_BLOCK)
        print("Microphone stream opened.")
        return stream

    def tapDetected(self):
        print("Tap detected!")

    def listen(self):
        try:
            block = self.stream.read(INPUT_FRAMES_PER_BLOCK)
            print("Reading a block of audio data.")
        except Exception as e:
            self.errorcount += 1
            print("({}) Error recording: {}".format(self.errorcount, e))
            self.noisycount = 1
            return

        amplitude = get_rms(block)
        print("Amplitude: {:.2f}, Threshold: {:.2f}".format(amplitude, self.tap_threshold))
        if amplitude > self.tap_threshold:
            self.quietcount = 0
            self.noisycount += 1
            print("Noisy block detected. Noisy count:", self.noisycount)
        else:
            print(f"max tap blocks:{MAX_TAP_BLOCKS}")
            if 1 <= self.noisycount <= MAX_TAP_BLOCKS:
                self.tapDetected()
            self.noisycount = 0
            self.quietcount += 1
            print("Quiet block detected. Quiet count:", self.quietcount)


if __name__ == "__main__":
    tt = TapTester()

    for i in range(1000):
        tt.listen()