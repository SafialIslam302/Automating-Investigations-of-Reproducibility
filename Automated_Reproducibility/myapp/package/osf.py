import os
import subprocess
import zipfile
import shutil


def check_folder_exists(folder_path):
    # Check if the folder exists
    return os.path.exists(folder_path)


def unzip_folder(zip_path, destination_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(destination_path)

    print(f"Unzipped folder: {zip_path} to {destination_path}")


def process_zip_files(zip_file_path, unzip_directory):
    try:
        # Extract the contents of the zip file in the same folder
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(unzip_directory)

        # Delete the zip file
        os.remove(zip_file_path)

        # Check for any nested zip files and unzip them recursively
        for root, dirs, files in os.walk(unzip_directory):
            for file in files:
                if file.endswith('.zip'):
                    nested_zip_file_path = os.path.join(root, file)
                    nested_unzip_directory = os.path.join(root, os.path.splitext(file)[0])
                    process_zip_files(nested_zip_file_path, nested_unzip_directory)

    except Exception as e:
        print(f'Error unzipping {zip_file_path}: {e}')


def osf_file_downloads(osf_id, pdf_folder_path):
    if os.path.exists(osf_id):
        shutil.rmtree(osf_id)

    config_data_template = """
            [osf]
            username = SAFIALISLAM
            project = {osf_id}

            # token auth
            token = TDZaMi3rnRRbE8uiBU5KIp3g3DgJnh7g1yUA32CNIQGNC0uQ1PcCuanpusQjKp5YUBCCgU
                    
        """
    config_data = config_data_template.format(osf_id=osf_id)

    # Specify the file path for the .osfcli.config file
    config_file_path = ".osfcli.config"
    # config_file = ".osfcli.config"
    # config_file_path = os.path.join(pdf_folder_path, config_file)

    # Write the config data to the file
    with open(config_file_path, "w") as config_file:
        config_file.write(config_data)

    print(f"Created .osfcli.config file for project ID '{osf_id}' at '{config_file_path}'")

    # Build the osf clone command
    osf_clone_command = ["osf", "-u", "SAFIALISLAM", "-p", osf_id, "clone"]

    try:
        build_output = subprocess.check_output(osf_clone_command, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print(f"Error cloning project {osf_id}: {e.stdout.decode()}")
    else:
        # Print success message if the command executed successfully
        print(f"Successfully cloned project {osf_id}")

    # Move the cloned project folder to the destination folder
    cloned_folder_name = osf_id.split("/")[-1]  # Extract the folder name from the project URL
    cloned_folder_path = os.path.join(os.getcwd(), cloned_folder_name)  # Get the full path to the cloned folder
    destination_path = os.path.join(pdf_folder_path, cloned_folder_name)
    # print(destination_path)

    try:
        # Move subfolders of osfstorage to osf_id folder
        osfstorage_folder = os.path.join(cloned_folder_path, "osfstorage")

        # Create the directory if it doesn't exist
        os.makedirs(destination_path, exist_ok=True)

        for item in os.listdir(osfstorage_folder):
            item_path = os.path.join(osfstorage_folder, item)
            shutil.move(item_path, destination_path)

        # Delete the osfstorage folder
        shutil.rmtree(cloned_folder_path)
        print(f"Deleted osfstorage folder: {cloned_folder_path}")

        os.remove(config_file_path)
        print(".osfcli.config file deleted successfully.")

        # After downloading all files, find and extract zip files
        for root, _, files in os.walk(destination_path):
            for file in files:
                if file.endswith('.zip'):
                    zip_file_path = os.path.join(root, file)
                    nested_unzip_directory = os.path.join(root, os.path.splitext(file)[0])
                    process_zip_files(zip_file_path, nested_unzip_directory)

        # Delete all zip files within the cloned project folder
        for root, _, files in os.walk(destination_path):
            for file in files:
                if file.endswith('.zip'):
                    zip_file_path = os.path.join(root, file)
                    os.remove(zip_file_path)

        return destination_path
    except Exception as e:
        print(f"Error moving the cloned project folder: {str(e)}")
        return 0
