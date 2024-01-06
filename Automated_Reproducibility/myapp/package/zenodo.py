import os
import requests
import zipfile


def check_folder_exists(folder_path):
    # Check if the folder exists
    return os.path.exists(folder_path) and os.path.isdir(folder_path)


def unzip_file(zip_file_path, unzip_directory):
    try:
        # Extract the contents of the zip file in the same folder
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(unzip_directory)

        # Delete the main zip file
        os.remove(zip_file_path)

        # Check for any nested zip files and unzip them recursively
        for root, dirs, files in os.walk(unzip_directory):
            for file in files:
                if file.endswith('.zip'):
                    nested_zip_file_path = os.path.join(root, file)
                    nested_unzip_directory = os.path.join(root, os.path.splitext(file)[0])
                    unzip_file(nested_zip_file_path, nested_unzip_directory)

    except Exception as e:
        print(f'Error unzipping {zip_file_path}: {e}')


def zenodo_file_downloads(url, destination_folder):
    ACCESS_TOKEN = "CGEDFd7NlBzRNvjy8JdmCQvvExT9A4ChKhWp151AjSo08le7WCLlxN1run0C"  # for zenodo

    # Split the URL by '/'
    parts = url.rsplit('/', 1)[-1]

    # Split the last part by '.' and retrieve the last element
    record_id = parts.split('.')[-1]

    # Check if the folder exists, create if it doesn't
    folder_name = os.path.join(destination_folder, str(record_id))
    # print("folder name: ", folder_name)

    try:
        # Check if the folder exists, create if it doesn't
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        # API request to retrieve record information
        r = requests.get(f"https://zenodo.org/api/records/{record_id}", params={'access_token': ACCESS_TOKEN})

        print("Check: ", r.json()['links']['archive'])

        # Extract the download URL from the response
        url = r.json()['links']['archive']
        filename = record_id

        # Construct the file path within the folder as the file is download zip so add .zip
        file_path = os.path.join(folder_name, filename) + '.zip'

        # Send a GET request to the download URL
        response = requests.get(url)  # requests.get(url, params={'access_token': ACCESS_TOKEN})

        # Open the file in binary write mode and write the content from the response
        with open(file_path, 'wb') as file:
            file.write(response.content)

        # print(f'File {file_path} downloaded successfully')
        '''for filename, url in zip(filenames, download_urls):
            # Replace forward slashes in filename with another character
            filename = filename.replace('/', '_')

            # Construct the file path within the folder
            file_path = os.path.join(folder_name, filename)

            print(filename, url)

            # print("Downloading:", file_path)  # Print the file path being downloaded

            # if check_folder_exists(file_path):
            # print(f'Folder {file_path} already exists')
            # else:
            # Send a GET request to the download URL
            r = requests.get(url, params={'access_token': ACCESS_TOKEN})

            # Open the file in binary write mode and write the content from the response
            with open(file_path, 'wb') as f:
                f.write(r.content)

            print(f'File {file_path} downloaded successfully')'''

        # After downloading all files, find and extract zip files
        for root, _, files in os.walk(folder_name):
            for file in files:
                if file.endswith('.zip'):
                    zip_file_path = os.path.join(root, file)
                    nested_unzip_directory = os.path.join(root, os.path.splitext(file)[0])
                    unzip_file(zip_file_path, nested_unzip_directory)

    except Exception as e:
        print(f"Error processing Zenodo link: {url}\nError message: {str(e)}")

    return folder_name
