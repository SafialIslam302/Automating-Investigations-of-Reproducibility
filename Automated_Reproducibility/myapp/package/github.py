from git import Repo, GitCommandError
import os
import shutil


def unzip_file(zip_file_path, unzip_directory):
    try:
        shutil.unpack_archive(zip_file_path, unzip_directory)
        os.remove(zip_file_path)  # Remove the original zip file
    except Exception as e:
        print(f'Error unzipping {zip_file_path}: {e}')


def handle_zip_files(root, files):
    for file in files:
        if file.endswith('.zip'):
            zip_file_path = os.path.join(root, file)
            unzip_directory = os.path.splitext(zip_file_path)[0]
            unzip_file(zip_file_path, unzip_directory)
            handle_zip_files(unzip_directory, os.listdir(unzip_directory))


def download_repository(repo_url, destination):
    # Clone the repository using GitPython
    try:
        print("Repo URL: ", repo_url)
        # Clone the repository using GitPython
        Repo.clone_from(repo_url, destination)

        # Check for zip files and unzip them
        for root, dirs, files in os.walk(destination):
            handle_zip_files(root, files)
    except GitCommandError as e:
        print(f'Error downloading folder {destination}: {e.stderr}')


def subtract_last_part(link):
    parts = link.split('/')
    filename = parts[-1].split('.')[0]
    return filename
