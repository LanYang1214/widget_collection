from pathlib import Path
import subprocess

# TARGET = "/home/lan-yang/Music/tag_parsing"
TARGET = "/mnt/bighouse/Music/Pure"
FILTER = {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a",
          ".wma", ".opus", ".aiff", ".alac", ".mp4", ".webm"}


def is_media(check_path):
    # give a rough filter, only return true for music format
    return check_path.suffix.lower() in FILTER

def walkthrough(target_path):
    # walk through the target directory, only returns media files
    # is a generator, returns one media file path a time.
    root_path = Path(target_path)
    for file_path in root_path.iterdir():
        if is_media(file_path):
            yield file_path
        else:
            continue

def convert(input_file_path, output_path):
    # convert the input file to mp3
    file_name = input_file_path.with_suffix(".mp3").name
    output_file_path = output_path / file_name
    process_cmd = ["ffmpeg",
                  "-y",
                  "-i", str(input_file_path),
                  "-vn",
                  "-acodec", "libmp3lame",
                  "-ab", "128k",
                  "-ar", "44100",
                  str(output_file_path)]
    process_run = subprocess.run(process_cmd,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True)
    result = process_run.returncode == 0
    message = process_run.stderr
    return result, message

def main(target):
    success_count = 0
    failed_log = {}
    out_path = Path(target) / "tag_processed"
    out_path.mkdir(parents=True, exist_ok=True)
    for i in walkthrough(target):
        # walk through every media file
        success, failed = convert(i, out_path)
        # convert into mp3
        if success:
            success_count += 1
        else:
            failed_log[str(i)] = failed.strip()
    # casting report
    print(f"process complete. Successfully converted: {success_count}")
    if failed_log:
        print(failed_log)


if __name__ == "__main__":
    main(TARGET)
