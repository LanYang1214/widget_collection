import type_convert as tc
from pathlib import Path
import pyloudnorm as pyln
import numpy as np
from pedalboard import Pedalboard, Limiter
from pedalboard.io import AudioFile

LOUDNESS = -14.0


def silence_trim(processing, sample_rate):
    # trim the long silence at the beginning or ending
    # written by ChatGPT, not much checked
    # really, DON'T USE IT directly. recheck and re-edit it before use
    if processing.ndim > 1:
        energy = np.max(np.abs(processing), axis=1)
    else:
        energy = np.abs(processing)
    threshold = 0.01
    indices = np.where(energy > threshold)[0]
    start = indices[0]
    end = indices[-1]
    padding = int(sample_rate * 0.2)
    start = max(0, start - padding)
    end = min(len(processing), end + padding)
    trimmed = processing[start:end]
    if trimmed.ndim > 1:
        trimmed_audio = trimmed.T
    else:
        trimmed_audio = np.expand_dims(trimmed, axis=0)
    return trimmed_audio

def peak_limit(processing, sample_rate):
    # load, compress too loud peak, and save with pedalboard
    board = Pedalboard([Limiter(threshold_db=-0.5, release_ms=50)])
    limited_audio = board(processing, sample_rate)
    return limited_audio

def volume_norm(waveflow, sample_rate, target_loudness):
    # adjust the LUFS to a preset level
    meter = pyln.Meter(sample_rate)
    loudness = meter.integrated_loudness(waveflow)
    gain = target_loudness - loudness
    normalized_audio = waveflow * (10.0 ** (gain / 20.0))
    return normalized_audio

def main(target, set_loudness):
    workingdesk = Path(target) / "tag_processed"
    for i in tc.walkthrough(workingdesk):
        with AudioFile(str(i)) as f:
            process = f.read(f.frames)
            rate = f.samplerate
        process = silence_trim(process, rate)
        process = peak_limit(process, rate)
        process = volume_norm(process, rate, set_loudness)
        if len(process.shape) > 1:
            num_channels = process.shape[0]
        else:
            num_channels = 1
        # here, it'd better not be saved here, or saved as .flac
        # because this script can run on various media format, it should be ran before unifying format
        # ideal workflow should be, volume treatment, type convert, finally tagging
        with AudioFile(str(i), "w", rate, num_channels) as f:
            # here it has some problem with the num_channels argument. DON'T RUN IT
            f.write(process)


if __name__ == "__main__":
    main(tc.TARGET, LOUDNESS)
