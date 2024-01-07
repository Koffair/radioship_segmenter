"""This is the CLI of the segmenter tool.

The tool requeires an input and an ouput folder to be specified.
The input folder should contain mp3 files. """

import radioship_segmenter.utils as utils

import os
import argparse
import logging
import sys
import datetime

from huggingsound import SpeechRecognitionModel  # type: ignore


def do_segmentation(in_path: str, out_path: str) -> None:
    """Set up logger and interim folders, create transcriptions."""

    if not os.path.isdir(out_path):
        print(f"Output dir [{out_path}] does not exist!")
        create_q = input("Would you like to create it? y/n: ")
        if create_q == "y":
            os.mkdir(out_path)
            print(f"Output dir [{out_path}] created!\n")
        else:
            return

    # test if the output folder is writable
    if not os.access(out_path, os.W_OK):
        raise PermissionError(
            f"""Output dir [{out_path}] is not writable!

                              
You do not have the necessary permissions to access or modify the specified folders. To resolve this issue:

- On Unix (Linux/Mac):
  - Use the 'chmod' command to change permissions on the folders. For example:

  chmod +rw /path/to/folder

- On Windows:
  - Right-click on the folder, choose 'Properties.'
  - Go to the 'Security' tab and click 'Edit' to change permissions.
  - Add your user account and grant 'Read' and 'Write' permissions.
  
If you're not sure how to do this, consider seeking assistance from your system administrator or referring to your operating system's documentation.
"""
        )

    # test if the input folder is readable
    if not os.access(in_path, os.R_OK):
        raise PermissionError(
            f"""Input dir [{in_path}] is not readable!

                              
You do not have the necessary permissions to access or modify the specified folders. To resolve this issue:

- On Unix (Linux/Mac):
  - Use the 'chmod' command to change permissions on the folders. For example:

  chmod +rw /path/to/folder

- On Windows:
  - Right-click on the folder, choose 'Properties.'
  - Go to the 'Security' tab and click 'Edit' to change permissions.
  - Add your user account and grant 'Read' and 'Write' permissions.
  
If you're not sure how to do this, consider seeking assistance from your system administrator or referring to your operating system's documentation.
"""
        )

    # set up logger
    LOGS_FOLDER = os.path.join(out_path, "logs")
    if not os.path.isdir(LOGS_FOLDER):
        os.mkdir(LOGS_FOLDER)
    now = datetime.datetime.now().strftime("%Y.%m.%d_%H:%M:%S")
    log_name = os.path.join(LOGS_FOLDER, now + "_transcriber_tool.log")

    logging.basicConfig(
        filename=log_name,
        filemode="a",
        force=True,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.DEBUG,
    )
    numba_logger = logging.getLogger("numba")
    numba_logger.setLevel(logging.WARNING)
    pydub_logger = logging.getLogger("pydub")
    pydub_logger.setLevel(logging.WARNING)
    urllib3_logger = logging.getLogger("urllib3")
    urllib3_logger.setLevel(logging.WARNING)

    # show logs on the console as well (for now). this may get behind a -v flag
    root = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)


    # create interim folders for processing slices & segments
    slices_path = os.path.join(out_path, "interim_data/slices")
    segments_path = os.path.join(out_path, "interim_data/segments")
    if not os.path.isdir(slices_path):
        os.makedirs(os.path.abspath(slices_path))
    if not os.path.isdir(segments_path):
        os.makedirs(os.path.abspath(segments_path))

    # get file_list
    logging.info("Loading input .mp3 files from: %s", in_path)
    full_paths = [
        os.path.abspath(os.path.join(in_path, f)) for f in os.listdir(in_path)
    ]
    mp3s = [e for e in full_paths if os.path.isfile(e) and e[-4:] == ".mp3"]
    for mp3 in mp3s:
        # create segmentation
        utils.make_sections(mp3, out_path)


def main():
    """This is the entry point for the CLI of the radioship segmenter tool."""
    parser = argparse.ArgumentParser("Create segments from mp3 files.")
    parser.add_argument(
        "-i",
        "--in_path",
        type=str,
        metavar="",
        required=True,
        help="Path to input file or directory",
    )
    parser.add_argument(
        "-o",
        "--out_path",
        type=str,
        metavar="",
        required=True,
        help="Path to output directory",
    )
    args = parser.parse_args()

    do_segmentation(args.in_path, args.out_path)


if __name__ == "__main__":
    main()
