from pymediainfo import MediaInfo
from pathlib import Path

import subprocess

# ---------------------------------
# Metadata Extraction
# ---------------------------------

def extract_aac_metadata(file_path: Path) -> dict:
    media_info = MediaInfo.parse(file_path)

    audio_track = next(
        (t for t in media_info.tracks if t.track_type == "Audio"),
        None,
    )
    if not audio_track:
        raise ValueError("No audio track found")

    return {
        "duration_seconds": get_duration_ffprobe(file_path),
        "bitrate": audio_track.bit_rate,
        "sample_rate": audio_track.sampling_rate,
        "channels": audio_track.channel_s,
        "file_size_bytes": file_path.stat().st_size,
    }

def get_duration_ffprobe(path):
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=duration,format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())