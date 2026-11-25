# import vol_normalizing as vn
import type_convert as tc
import tag_parsing as tp
import playlist_update as pu

def flow_default():
    workingdir = "/home/lan-yang/Music"
    workingtype = ".mp3"
    tc.main(workingdir, True)
    tp.main(workingdir, workingtype)
    music_done = "/home/lan-yang/Music/tag_parsing/tag_processed"
    storage = "/mnt/bighouse/Music"
    pu.main(workingdir, music_done, storage)

def flow_trusted():
    workingdir = "/home/lan-yang/Music/tag_parsing"
    workingtype = ".mp3"
    tp.main(workingdir, workingtype)
    lists_lib = "/home/lan-yang/Music"
    music_done = "/home/lan-yang/Music/tag_parsing/tag_processed"
    storage = "/mnt/bighouse/Music"
    pu.main(lists_lib, music_done, storage)

def test_mode():
    workingdir = input("\nwhere to test musics? enter the directory, end without slash: ")
    media_count = 0
    print("")
    for i in tc.walkthrough(workingdir):
        if tc.is_mp3(i):
            print(f"media {i} is real mp3.")
        else:
            print(f"media {i} is not mp3.")
        media_count += 1
    print(f"\nmp3 test done on {media_count} files under {workingdir}/.")

def main():
    print("Menu: \n 1. default: take file from workingdir, first convert the type to mp3, then"
          " tag them. Base directory is pre-set to '/home/lan-yang/Music'. \n 2. trust: no type"
          " conversion, trust all files as real mp3. Will lead to exception if not. \n 3. test:"
          " iterate all media files in any directory, report whether they are mp3 or not.")
    option = input("\nplease choose workflow, by enter their index number: ")
    if option == "1":
        flow_default()
    elif option == "2":
        flow_trusted()
    elif option == "3":
        test_mode()
    else:
        pass


if __name__ == "__main__":
    main()
