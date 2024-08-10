from scipy.io import wavfile
import noisereduce as nr
import numpy as np
import os

def refine_audio(filename, times=2):
    n = filename.replace(".wav", "")
    
    for e in range(times):
        # load data
        if e == 0:
            rate, data = wavfile.read(filename)
        else:
            rate, data = wavfile.read(n+str(e-1)+".wav")

        orig_shape = data.shape
        data = np.reshape(data, (2, -1))

        # perform noise reduction
        # optimized for speech
        reduced_noise = nr.reduce_noise(
            y=data,
            sr=rate,
            stationary=True
        )

        wavfile.write(n+str(e)+".wav", rate, reduced_noise.reshape(orig_shape))
        if e != 0:
            os.system(f"rm {n+str(e-1)}.wav")
    
    os.system(f"cp {n+str(times-1)}.wav {filename}")
    os.system(f"rm {n+str(times-1)}.wav")
