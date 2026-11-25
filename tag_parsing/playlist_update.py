from pathlib import Path
import shutil

PLAYLIST_DIR = "/home/lan-yang/Music"
PROCESSED_DIR = "/home/lan-yang/Music/tag_parsing/tag_processed"
STORAGE_DIR = "/mnt/bighouse/Music"
SKIP_DIRS = {"@ Ongoing"}

def find_lists(lists_path):
    avail_playlists = sorted(lists_path.glob("*.m3u"))
    if not avail_playlists:
        print(f"\nNo m3u playlist found in {lists_path}")
        return []
    return avail_playlists

def find_folders(storage_path):
    subfolders = sorted(
        p for p in storage_path.iterdir()
        if p.is_dir() and not p.name.startswith(".") and p.name not in SKIP_DIRS
    )
    return [storage_path] + subfolders

def print_menu(playlist_or_folder, avail_lists):
    if playlist_or_folder =="playlist":
        print("\navailable playlists menu:")
        for i, playlist in enumerate(avail_lists, start=1):
            print(f"{i}. {playlist.stem}")
    elif playlist_or_folder =="folder":
        print("\navailable folders menu:")
        for i, folder in enumerate(avail_lists, start=1):
            print(f"{i}. {folder.name}")
    print("(enter 0 whenever to print again)\n")

def category_music(lists, music):
    answer = input(f"\nenter number to category {music.stem}: ").strip()
    if answer == "0":
        print_menu("playlist", lists)
        answer = input(f"\nenter number to category {music.stem}: ").strip()
    if not answer.isdigit() or not 0 < int(answer) <= len(lists):
        print(f"{music.stem} skipped.")
    else:
        playlist = lists[int(answer) - 1]
        with playlist.open("a", encoding="utf-8") as f:
            f.write(f"{music.resolve()}\n")
        print(f"added to {playlist.stem}")

def move_music(options_path, music) -> Path | None:
    answer = input(f"\nenter number to move {music.stem}: ").strip()
    if answer == "0":
        print_menu("folder",options_path)
        answer = input(f"\nenter number to move {music.stem}: ").strip()
    if not answer.isdigit() or not 0 < int(answer) <= len(options_path):
        print(f"{music.stem} skipped.")
        return None
    else:
        folder = options_path[int(answer) - 1]
        targeted_path = folder / music.name
        if targeted_path.exists():
            print(f"{music.name} already exists in {folder.name}, kept in place.")
            return None
        else:
            shutil.move(music, targeted_path)
            music = Path(targeted_path).resolve()
            print(f"moved music: {music}")
            return music

def main(lists_dir, processed_dir, storage_dir):
    playlists = find_lists(Path(lists_dir))
    folders = find_folders(Path(storage_dir))
    print_menu("playlist", playlists)
    print_menu("folder", folders)
    for processed_music in sorted(Path(processed_dir).glob("*.mp3")):
        new_path = move_music(folders, processed_music)
        if new_path is not None: category_music(playlists, new_path)


if __name__ == "__main__":
    main(PLAYLIST_DIR, PROCESSED_DIR, STORAGE_DIR)
