from pathlib import Path
import type_convert as tc
from mutagen.easyid3 import EasyID3

TYPE = ".mp3"


def name_parsing(pars_path, suff_unified):
    # extract the name and artist
    song = pars_path.name.removesuffix(suff_unified)
    parts = song.split(" - ", 1)
    if len(parts) == 2:
        # if the file name can't be split as expected, it needs to be flagged
        # 0 is normal flag, 1 is exception
        split_flag = 0
        file_title = parts[0]
        file_artists = parts[1]
    else:
        split_flag = 1
        file_title = song
        file_artists = "unknown"
    # file_artists = artists_str.split(",")
    return file_title, file_artists, split_flag

def tag_attaching(audio_path, desired_title, desired_artists):
    # attach title and artists info to the music
    audio = EasyID3(audio_path)
    audio.delete()
    audio["title"] = desired_title
    audio["artist"] = desired_artists
    audio.save()

def main(target, uniform_type):
    workingdesk = Path(target) / "tag_processed"
    hold_err = []
    hold_uncertain = []
    for i in tc.walkthrough(workingdesk):
        # walk through each media files
        title, artists, flag = name_parsing(i, uniform_type)
        # parsing the file name
        if flag == 0:
            try:
                tag_attaching(i, title, artists)
                # attach the desired information to ID3 tags.
            except Exception:
                hold_err.append(i)
        else:
            hold_uncertain.append(i)
    # casting report
    print(f"auto parsing completed. Need manually settlement: {len(hold_uncertain)}")
    for j in hold_uncertain:
        print(j)
        manu_title = input("\n  please enter the title: ")
        manu_artis = input("    please enter the artists, separate with comma: ")
        try:
            tag_attaching(j, manu_title, manu_artis)
        except Exception:
            hold_err.append(j)
    print(f"\nprocess completed. Failed cases toll: {len(hold_err)}.\n    {hold_err}")


if __name__ == "__main__":
    main(tc.TARGET, TYPE)
