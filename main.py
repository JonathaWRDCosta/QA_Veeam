import os
import shutil
import time
import logging
import argparse

def initialize_logging(log_file):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s]: %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        datefmt="%Y-%m-%d %H:%M:%S"
    )

def folder_sync(source_folder, mirror_folder, sync_interval, log_file):
    initialize_logging(log_file)

    while True:
        # Check if source folder exists, create if not
        if not os.path.exists(source_folder):
            os.makedirs(source_folder)
            logging.info(f"Created source folder: {source_folder}")

        # Check if mirror folder exists, create if not
        if not os.path.exists(mirror_folder):
            os.makedirs(mirror_folder)
            logging.info(f"Created mirror folder: {mirror_folder}")

        # Synchronize files from source to mirror
        for root, dirs, files in os.walk(source_folder):
            relative_path = os.path.relpath(root, source_folder)
            mirror_path = os.path.join(mirror_folder, relative_path)

            # Create directories in mirror if they don't exist
            for dir_name in dirs:
                source_dir = os.path.join(root, dir_name)
                mirror_dir = os.path.join(mirror_path, dir_name)
                if not os.path.exists(mirror_dir):
                    os.makedirs(mirror_dir)
                    logging.info(f"Created folder: {mirror_dir}")

            # Copy files from source to mirror if updated
            for file_name in files:
                source_file = os.path.join(root, file_name)
                mirror_file = os.path.join(mirror_path, file_name)
                if not os.path.exists(mirror_file) or os.stat(source_file).st_mtime > os.stat(mirror_file).st_mtime:
                    shutil.copy2(source_file, mirror_file)
                    logging.info(f"Copied: {source_file} to {mirror_file}")
                elif os.path.exists(mirror_file) and os.stat(source_file).st_mtime == os.stat(mirror_file).st_mtime:
                    continue

        # Remove files and directories from mirror if not present in source
        for root, dirs, files in os.walk(mirror_folder):
            for dir_name in dirs:
                mirror_dir = os.path.join(root, dir_name)
                source_dir = os.path.join(source_folder, os.path.relpath(mirror_dir, mirror_folder))
                if not os.path.exists(source_dir):
                    shutil.rmtree(mirror_dir)
                    logging.warning(f"Deleted folder: {mirror_dir}")

            for file_name in files:
                mirror_file = os.path.join(root, file_name)
                source_file = os.path.join(source_folder, os.path.relpath(mirror_file, mirror_folder))
                if not os.path.exists(source_file):
                    os.remove(mirror_file)
                    logging.warning(f"Deleted file: {mirror_file}")

        logging.info("Synchronization completed.")
        time.sleep(sync_interval)

def start_sync():
    parser = argparse.ArgumentParser(description="Folder synchronization script.")
    parser.add_argument("source_folder", help="Path to the source folder")
    parser.add_argument("mirror_folder", help="Path to the mirror folder")
    parser.add_argument("interval_seconds", type=int, help="Synchronization interval in seconds")
    parser.add_argument("log_file", help="Path to the log file")

    args = parser.parse_args()

    folder_sync(
        args.source_folder,
        args.mirror_folder,
        args.interval_seconds,
        args.log_file
    )

if __name__ == "__main__":
    start_sync()
