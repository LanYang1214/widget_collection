from pathlib import Path
import subprocess

FILTER = {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a",
          ".wma", ".opus", ".aiff", ".alac", ".mp4", ".webm"}
SIGNATURES = [b"ID3", b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"]
TARGET = "/home/lan-yang/Music/tag_parsing"

def is_media(check_path):
    # give a rough filter, only return true for music format
    return check_path.suffix.lower() in FILTER

def is_mp3(music_path):
    with music_path.open("rb") as f:
        head = f.read(3)
    return any(head.startswith(sig) for sig in SIGNATURES)

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

def main(target, safe_mode):
    """
    :param target: Path of the base folder, contains "type_dirty/" and "tag_processed/" sub-
    directories. musics before type align are in "type_dirty/".
    :param safe_mode: boolean, true means check before conversion (do not convert real .mp3
    files, just move them), false means just convert every file.
    :return: none.
    """
    success_count = 0
    all_failed = {}
    in_path = Path(target) / "type_dirty"
    out_path = Path(target) / "tag_processed"
    out_path.mkdir(parents=True, exist_ok=True)
    for i in walkthrough(in_path):
        if safe_mode:
            if not is_mp3(i):
                success, err_log = convert(i, out_path)
                if success:
                    success_count += 1
                else:
                    all_failed[str(i)] = err_log.strip()
            else:
                i = i.rename(out_path / i.name)
                success_count += 1
        else:
            success, err_log = convert(i, out_path)
            if success:
                success_count += 1
            else:
                all_failed[str(i)] = err_log.strip()
    print(f"\nConversion complete. Successfully converted: {success_count}")
    if all_failed:
        print(all_failed)


if __name__ == "__main__":
    main(TARGET, True)

