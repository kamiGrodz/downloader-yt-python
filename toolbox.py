import move_unused_files, strip_filenames, youtube_downloader

def main_menu_screen():
    print("""
  1. Download Youtube Videos
  2. Strip filenames
  3. Extract small files to other folder
  4. ...to be added...
  00. Exit
  """)

def welcome_message():
    print("""
///////////////////////////////
            PYBOX             
Your tool for everyday's needs!
///////////////////////////////""")
    main_menu_screen()

def download_from_yt():
    print("""1. Fetch videos from X days (def=3)
2. Download one video/audio from url (Best Quality)
3. Custom command (options)
    """)
    choice = input("Choice: ")

    if choice == "1":
        args = ["--fetch"]
        days = input("Days (def=3): ")
        args.append(f"--days {days}")
        youtube_downloader.main(args)

        if input("Download all? (Y/N): ").lower() == "y":
            youtube_downloader.main("--download")

    elif choice == "2":
        url = input("Url: ").split("&", 1)[0]
        args = ["--single", url]

        if input("Audio only? (Y/N): ").lower() == "y":
            args.append("--audio_only")
        else:
            qual = input("Video quality (480, 720, etc): ")
            if qual:
                args.append(f"--q {qual}")

        youtube_downloader.main(args)

    else:
        print("""Usage: youtube_downloader options
        Common options:
          --fetch              Fetch video info only
          --download           Download videos from channels  
          --single URL         Download single video from URL
          --days N             Filter videos from last N days
          --q QUALITY          Maximum quality (e.g., 720 for 720p)
          --audio_only         Download audio only
          --audio_codec CODEC  Audio codec (default: aac)
          --audio_quality N    Audio quality in kbps (default: 320)
        """)
        args_str = input("Provide arguments, delimit by space: ")
        args = args_str.split(" -")
        args_fixed = []
        for idx, arg in enumerate(args):
            if idx == 0:
                args_fixed.append(arg)
                continue
            args_fixed.append("-"+arg)

        youtube_downloader.main(args)

def strips():
    print("This tool strips filenames based on: delimiter, or number of characters")
    strip_filenames.main()

def move_them():
    print("This tool moves small files to additional folder")
    move_unused_files.main()

def main():
    welcome_message()
    allowed_options = {
    1: download_from_yt,
    2: strips,
    3: move_them}

    while (choice := input("Choice: "))[0] != "0":
        # change to int and handle errors
        try: choice = int(choice)
        except Exception as e: print(f"Error, wrong value! \n{e}\n"); continue

        # check if number is allowed
        if choice not in allowed_options:
            print("Number not allowed!\n")
            continue

        allowed_options[choice]()

        input("\tDone! Press Enter to finish...")
        main_menu_screen()

    print(choice)

if __name__ == "__main__":
    main()
