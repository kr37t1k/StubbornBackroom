import winsound
import time
import pyaudio
import wave
import os

def play_pyaudio(filename, loop=False):
    """
    Loads, plays a WAV file using PyAudio.
    """
    # Open the wave file
    try:
        wf = wave.open(filename, 'rb')
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return
    except wave.Error as e:
        print(f"Error opening wave file: {e}")
        return

    # Create an interface to PortAudio
    p = pyaudio.PyAudio()

    # Open a stream
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # Read data in chunks
    chunk = 1024
    data = wf.readframes(chunk)

    # Play the sound in a loop
    try:
        while True:
            stream.write(data)
            data = wf.readframes(chunk)
            if data == b'':  # If file is over, rewind
                wf.rewind()
                data = wf.readframes(chunk)
    except KeyboardInterrupt:
        print("Playback stopped by user.")
    finally:
        # Stop and close the stream and PyAudio interface
        stream.stop_stream()
        stream.close()
        p.terminate()
        wf.close()

def play_winsound(filename, loop=False):
    """
    Plays a file using the Windows-specific winsound module.
    """
    try:
        # SND_FILENAME specifies a file name
        # SND_LOOP makes the sound loop continuously
        # SND_ASYNC plays the sound in the background
        if not loop: winsound.PlaySound(filename, winsound.SND_FILENAME | winsound.SND_ASYNC) #for once
        else: winsound.PlaySound(filename, winsound.SND_FILENAME | winsound.SND_LOOP | winsound.SND_ASYNC) #for loop

        # Keep the script running so the background sound continues
        # while True:
        #     time.sleep(1)

    except KeyboardInterrupt:
        print("Playback stopped by user.")
        # Stop the sound when the loop is exited
        winsound.PlaySound(None, winsound.SND_FILENAME)
    except Exception as e:
        print(f"An error occurred: {e}")


# # Example usage (Windows only):
# if __name__ == "__main__":
#     sound_file = "my_sound.wav"
#     play_and_loop_winsound(sound_file)
#
