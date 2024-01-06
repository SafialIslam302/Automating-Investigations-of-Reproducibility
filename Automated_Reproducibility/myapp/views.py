import time

from django.shortcuts import render
from .models import FileUpload
from django.utils.text import get_valid_filename
from django.conf import settings
import os
import re
import subprocess
import shutil
from urllib.parse import urlsplit

import requests
from .package import github, osf, pdflink, zenodo, checkrepository, pdftitle, file_generator_ipynb, \
    file_generator_python, file_generator_matlab, file_generator_R


# Check the status of the link
def check_url_access(url):
    try:
        response = requests.get(url)
        return response.status_code
    except requests.exceptions.RequestException as e:
        return None


# Remove special characters
def remove_special_characters(links):
    # List to store modified links
    modified_links = []

    # Iterate over each link
    for link_tuple in links:
        # Convert link tuple to string
        link = str(link_tuple)

        # Remove special characters from the end of the link
        modified_link = link.rstrip('.;,\#+:)}]?´|%!')  # Add any other special characters you want to remove

        # Append the modified link to the list
        modified_links.append(modified_link)

    return modified_links


# Check the folder exists
def check_folder_exists(folder_path):
    # Check if the folder exists
    return os.path.exists(folder_path)


def get_folder_size(folder_path):
    total_size = 0

    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            total_size += os.path.getsize(file_path)

    return total_size / (1024 * 1024)  # Convert to megabytes


def file_search(folder_path):
    present_files = []

    for root, _, files in os.walk(folder_path):
        if any(file.endswith('.py') for file in files):
            present_files.append('Python')
        if any(file.endswith('.ipynb') for file in files):
            present_files.append('Jupyter-Notebook')
        if any(file.endswith('.m') for file in files):
            present_files.append('Matlab')
        if any(file.endswith('.R') or file.endswith('.r') for file in files):
            present_files.append('RStudio')

    return present_files


def has_readme_file(folder_path):
    readme_filenames = ['readme.txt', 'readme.md']

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower() in readme_filenames:
                return True

    return False


def format_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    return f"{int(minutes)} minute{'s' if minutes != 1 else ''} {int(seconds)} second{'s' if seconds != 1 else ''}"


def check_files_in_folder(folder_path, file_names):
    file_paths = {}
    for file_name in file_names:
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            file_paths[file_name] = os.path.abspath(file_path)
        # else:
        # file_paths[file_name] = False
    return file_paths


# Find requirement.txt file in the folder
def find_requirements_files(root_dir):
    requirements_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower() in ['requirement.txt', 'requirements.txt']:
                requirements_files.append(os.path.normpath(os.path.join(dirpath, filename)))
    return requirements_files


# Create your views here.
def upload(request):
    root_directory = os.getcwd()
    media_folder_path = os.path.join(root_directory, "media")
    if os.path.exists(media_folder_path) and os.path.isdir(media_folder_path):
        # Delete the media folder
        shutil.rmtree(media_folder_path)

    results = []  # Initialize the results list

    if request.method == "POST":
        files = request.FILES.getlist('file[]')

        destination_folder = 'Download'  # Destination folder
        file_path = "output.txt"

        # Create the destination folder if it doesn't exist
        if not check_folder_exists(destination_folder):
            os.makedirs(destination_folder)

        for file in files:
            start_time = time.time()  # Record the start time

            original_filename = get_valid_filename(file.name)
            instance = FileUpload.objects.create(file=file, original_filename=original_filename)
            instance.save()

            if file.name.endswith('.pdf'):
                github_check = False  # Github present check
                zenodo_check = False  # Zenodo present check
                osf_check = False  # OSF present check

                github_result = False  # Store Github link
                zenodo_result = False  # Store Zenodo result
                osf_result = False  # Store OSF result

                github_path = False  # Store the Github Repository code
                zenodo_path = False  # Store the Zenodo Repository code
                osf_path = False  # Store the OSF Repository code

                github_size = False  # Measure the Download Github folder size
                zenodo_size = False  # Measure the Download Zenodo folder size
                osf_size = False  # Measure the Download OSF folder size

                # which files (.py, .ipynb, matlab, .r) are present
                github_search = False
                zenodo_search = False
                osf_search = False

                # from the files pick the unique name only
                github_search_file = 0
                zenodo_search_file = 0
                osf_search_file = 0

                # Get the folder name
                github_folder = 0
                zenodo_folder = 0
                osf_folder = 0

                # Check readme file is present or not
                git_readme = False
                zen_readme = False
                osf_readme = False

                total_rows = False
                total_files = 0
                total_result = 0
                all_search_file = False
                folders = 0

                github_total_files = 0  # how many unique files (.py, .ipynb, matlab, .r) in that github folder
                zenodo_total_files = 0  # how many unique files (.py, .ipynb, matlab, .r) in that zenodo folder
                osf_total_files = 0  # how many unique files (.py, .ipynb, matlab, .r) in that osf folder

                # File path of output_ipynb.txt file
                git_ipynb_file = False
                zen_ipynb_file = False
                osf_ipynb_file = False

                # Details of output_ipynb.txt file
                git_ipynb_file_detail = False
                zen_ipynb_file_detail = False
                osf_ipynb_file_detail = False

                # File path of output_py.txt file
                git_py_file = False
                zen_py_file = False
                osf_py_file = False

                # Details of output_py.txt file
                git_py_file_detail = False
                zen_py_file_detail = False
                osf_py_file_detail = False

                # File path of output_matlab.txt file
                git_matlab_file = False
                zen_matlab_file = False
                osf_matlab_file = False

                # Details of output_matlab.txt file
                git_matlab_file_detail = False
                zen_matlab_file_detail = False
                osf_matlab_file_detail = False

                git_r_file = False  # File path of output_r.txt file
                zen_r_file = False
                osf_r_file = False

                # Details of output_r.txt file
                git_r_file_detail = False
                zen_r_file_detail = False
                osf_r_file_detail = False

                # File path of error_ipynb.txt file
                git_ipynb_file_err = False
                zen_ipynb_file_err = False
                osf_ipynb_file_err = False

                # Details of error_ipynb.txt file
                git_ipynb_file_err_detail = False
                zen_ipynb_file_err_detail = False
                osf_ipynb_file_err_detail = False

                # File path of error_py.txt file
                git_py_file_err = False
                zen_py_file_err = False
                osf_py_file_err = False

                # Details of error_py.txt file
                git_py_file_err_detail = False
                zen_py_file_err_detail = False
                osf_py_file_err_detail = False

                # File path of error_matlab.txt file
                git_matlab_file_err = False
                zen_matlab_file_err = False
                osf_matlab_file_err = False

                # Details of error_matlab.txt file
                git_matlab_file_err_detail = False
                zen_matlab_file_err_detail = False
                osf_matlab_file_err_detail = False

                # File path of error_r.txt file
                git_r_file_err = False
                zen_r_file_err = False
                osf_r_file_err = False

                # Details of error_r.txt file
                git_r_file_err_detail = False
                zen_r_file_err_detail = False
                osf_r_file_err_detail = False

                # In the repository any requirement.txt file present that path
                git_requirement_check = False
                zen_requirement_check = False
                osf_requirement_check = False

                # In the repository any error requirement.txt file present that path
                git_requirement = False
                zen_requirement = False
                osf_requirement = False

                # If found error in the requirement.txt file show that errors
                git_requirement_detail = False
                zen_requirement_detail = False
                osf_requirement_detail = False

                # if no requirement.txt file found then create a requirement_new.txt file and save that path
                git_create = False
                zen_create = False
                osf_create = False

                # if no requirement.txt file found then create a requirement_new.txt file
                git_create_requirement = False
                zen_create_requirement = False
                osf_create_requirement = False

                # Remove underscores
                filename_without_underscore = original_filename.replace("_", " ")
                pdf_file_name, extension = os.path.splitext(filename_without_underscore)

                # Output folder name
                output_folder = " ".join(pdf_file_name.split()[:4])

                # Create a folder for the PDF file
                pdf_folder_path = os.path.join(destination_folder, output_folder)

                if not os.path.exists(pdf_folder_path):
                    os.makedirs(pdf_folder_path)
                else:
                    os.chdir(os.getcwd())
                    cmd = f'rmdir /s /q "{pdf_folder_path}"'
                    print("CMD: ", cmd)
                    # Execute the 'rmdir /s /q' command to remove the directory and its contents recursively and quietly
                    subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    os.makedirs(pdf_folder_path, exist_ok=True)
                try:
                    # Get the root directory path
                    root_directory = settings.BASE_DIR

                    # Construct the path to the media folder
                    media_directory = os.path.join(root_directory, "media")

                    # Construct the path to the files folder inside the media folder
                    folder_path = os.path.join(media_directory, "files")

                    pdf_file = os.path.join(folder_path, original_filename)

                    link_report = pdflink.check_pdf_links(pdf_file)

                    # Select the second column (index 1) and create a new list
                    link_list = [item[1] for item in link_report[1:]]

                    # use regular expression
                    urls = pdflink.extract_urls_from_pdf(pdf_file)

                    # for broken url links
                    broken_urls = pdflink.broken_urls_from_pdf(pdf_file)

                    # merge all the list
                    merged_list = link_list + urls + broken_urls

                    # remove special characters from the end of each link in a list
                    modified_list = remove_special_characters(merged_list)

                    # Get unique list
                    unique_list = list(set(modified_list))

                    # get the pdf title name from the pdf
                    # pdf_title = pdftitle.get_pdf_title(pdf_file, folder_path).rstrip('.')

                    # Remove special characters and replace spaces with blanks
                    modify_pdf_title = re.sub(r'[^\w\s]', '', pdf_file_name)  # pdf_file_name pdf_title

                    # Convert the title into lower case for better search option
                    pdf_file_name_lowercase = re.sub(r'\s+', ' ', modify_pdf_title).lower()
                    final_title_one_lowercase = pdf_file_name.lower()
                    final_title_two_lowercase = re.sub(r'[^\w\s]', ' ', pdf_file_name).lower()
                    pdf_name = pdf_file_name_lowercase.title()

                    # Create a list to store the results
                    github_results = []

                    for url in unique_list:
                        # Check if the URL starts with "http://" or "https://"
                        if not url.startswith("http://") and not url.startswith("https://"):
                            new_url = "https://" + url
                        else:
                            new_url = url

                        lowercase_url = new_url.lower()

                        if "github" in lowercase_url and check_url_access(new_url) == 200:
                            github_results.append(new_url)

                    for result in github_results:
                        destination_path = os.path.join(pdf_folder_path, github.subtract_last_part(result))

                        git_boolean, github_url, similarity_ratio = checkrepository.check_original_repository(result,
                                                                                                              pdf_file_name_lowercase,
                                                                                                              final_title_one_lowercase,
                                                                                                              final_title_two_lowercase)
                        if git_boolean:
                            github_check = True
                            github_result = github_url
                            github_path = destination_path
                            github.download_repository(github_url, destination_path)
                            github_size = get_folder_size(github_path)
                            github_size = round(github_size, 3)
                            github_search = file_search(github_path)
                            git_readme = has_readme_file(github_path)

                    # Create a list to store the results
                    zenodo_results = []

                    for url in unique_list:
                        # convert the url into small case for better search
                        lowercase_url = url.lower()

                        # Check if the URL starts with "http://" or "https://"
                        if not url.startswith("http://") and not url.startswith("https://"):
                            new_url = "https://" + url
                        else:
                            new_url = url

                        if "zenodo" in lowercase_url and check_url_access(new_url) == 200:
                            zenodo_results.append(new_url)

                    for result in zenodo_results:
                        zen_boolean, zenodo_url, similarity_ratio = checkrepository.check_original_repository(result,
                                                                                                              pdf_file_name_lowercase,
                                                                                                              final_title_one_lowercase,
                                                                                                              final_title_two_lowercase)
                        if zen_boolean:
                            zenodo_check = True
                            zenodo_result = zenodo_url
                            zenodo_path = zenodo.zenodo_file_downloads(zenodo_url, pdf_folder_path)
                            zenodo_size = get_folder_size(zenodo_path)
                            zenodo_size = round(zenodo_size, 3)
                            zenodo_search = file_search(zenodo_path)
                            zen_readme = has_readme_file(zenodo_path)

                    # Create a list to store the results
                    osf_results = []

                    for url in unique_list:
                        # convert the url into small case for better search
                        lowercase_url = url.lower()

                        # Check if the URL starts with "http://" or "https://"
                        if not url.startswith("http://") and not url.startswith("https://"):
                            new_url = "https://" + url
                        else:
                            new_url = url

                        if "osf" in lowercase_url and check_url_access(new_url) == 200:
                            osf_results.append(new_url)

                    for osf_result in osf_results:
                        if osf_result.startswith('https://osf.io/') or osf_result.startswith('https://doi.org/'):
                            osf_id = urlsplit(osf_result).path.strip('/').split('/')[-1].lower()
                            osf_boolean, osf_url, similarity_ratio = checkrepository.check_original_repository(
                                osf_result,
                                pdf_file_name_lowercase,
                                final_title_one_lowercase,
                                final_title_two_lowercase)
                            # print(osf_boolean, osf_url, similarity_ratio)
                            if osf_boolean:
                                osf_check = True
                                osf_result = osf_url
                                osf_path = osf.osf_file_downloads(osf_id, pdf_folder_path)
                                osf_size = get_folder_size(osf_path)
                                osf_size = round(osf_size, 3)
                                osf_search = file_search(osf_path)
                                osf_readme = has_readme_file(osf_path)
                                # files = os.listdir(osf_path)
                                # print(files)

                    print("1: ", github_search)

                    if github_search:
                        github_search_file = list(set(github_search))
                    if zenodo_search:
                        zenodo_search_file = list(set(zenodo_search))
                    if osf_search:
                        osf_search_file = list(set(osf_search))

                    print("2: ", github_search_file)

                    if github_path:
                        github_folder = github_path.split('\\')[-1]
                    if zenodo_path:
                        zenodo_folder = zenodo_path.split('\\')[-1]
                    if osf_path:
                        osf_folder = osf_path.split('\\')[-1]

                    if github_folder or zenodo_folder or osf_folder:
                        folders = [github_folder, zenodo_folder, osf_folder]

                    print("Folders: ", folders)

                    folder_count = 0
                    # Check and count the presence of each variable
                    if github_folder:
                        folder_count += 1
                    if zenodo_folder:
                        folder_count += 1
                    if osf_folder:
                        folder_count += 1

                    if github_search_file:
                        github_total_files = len(github_search_file)
                    if zenodo_search_file:
                        zenodo_total_files = len(zenodo_search_file)
                    if osf_search_file:
                        osf_total_files = len(osf_search_file)

                    total_files = github_total_files + zenodo_total_files + osf_total_files

                    # print("Github: ", github_search_file, github_folder, github_total_files)
                    # print("zenodo: ", zenodo_search_file, zenodo_folder, zenodo_total_files)
                    # print("osf: ", osf_search_file, osf_folder, osf_total_files)
                    # print("Total: ", total_files)

                    files_to_check = ["output_ipynb.txt", "error_ipynb.txt", "output_py.txt", "error_py.txt",
                                      "output_matlab.txt", "error_matlab.txt", "output_R.txt", "error_R.txt",
                                      "error_requirement.txt", "requirements_new.txt"]

                    if github_path:
                        # print(github_path)
                        file_generator_ipynb.file_create(github_path)
                        file_generator_python.file_create(github_path)
                        file_generator_matlab.file_create(github_path)
                        file_generator_R.file_create(github_path)

                        new_github_path = os.path.join(root_directory, github_path)

                        # Call the function to check files in the folder
                        git_file_paths = check_files_in_folder(new_github_path, files_to_check)
                        # print(git_file_paths)

                        for file_name, file_path in git_file_paths.items():

                            print("File Name: ", file_name)

                            if file_name == "output_ipynb.txt":
                                git_ipynb_file = os.path.abspath(file_path)

                                if git_ipynb_file:
                                    with open(git_ipynb_file, 'r', encoding='utf-8') as read_file:
                                        # Read the contents of the file into a variable
                                        git_ipynb_file_detail = read_file.read()

                            if file_name == "output_py.txt":
                                git_py_file = os.path.abspath(file_path)

                                if git_py_file:
                                    with open(git_py_file, 'r', encoding='utf-8') as read_file:
                                        # Read the contents of the file into a variable
                                        git_py_file_detail = read_file.read()

                            if file_name == "output_matlab.txt":
                                git_matlab_file = os.path.abspath(file_path)

                                if git_matlab_file:
                                    with open(git_matlab_file, 'r', encoding='utf-8') as read_file:
                                        # Read the contents of the file into a variable
                                        git_matlab_file_detail = read_file.read()

                            if file_name == "output_R.txt":
                                git_r_file = os.path.abspath(file_path)

                                if git_r_file:
                                    with open(git_r_file, 'r', encoding='utf-8') as read_file:
                                        git_r_file_detail = read_file.read()

                            if file_name == "error_ipynb.txt":
                                git_ipynb_file_err = os.path.abspath(file_path)

                                if git_ipynb_file_err:
                                    with open(git_ipynb_file_err, 'r', encoding='utf-8') as read_file:
                                        git_ipynb_file_err_detail = read_file.read()

                            if file_name == "error_py.txt":
                                git_py_file_err = os.path.abspath(file_path)

                                if git_py_file_err:
                                    with open(git_py_file_err, 'r', encoding='utf-8') as read_file:
                                        git_py_file_err_detail = read_file.read()

                            if file_name == "error_matlab.txt":
                                git_matlab_file_err = os.path.abspath(file_path)

                                if git_matlab_file_err:
                                    with open(git_matlab_file_err, 'r', encoding='utf-8') as read_file:
                                        git_matlab_file_err_detail = read_file.read()

                            if file_name == "error_R.txt":
                                git_r_file_err = os.path.abspath(file_path)

                                if git_r_file_err:
                                    with open(git_r_file_err, 'r', encoding='utf-8') as read_file:
                                        git_r_file_err_detail = read_file.read()

                            if file_name == "error_requirement.txt":
                                git_requirement = os.path.abspath(file_path)

                                if git_requirement:
                                    with open(git_requirement, 'r', encoding='utf-8') as read_file:
                                        git_requirement_detail = read_file.read()

                            if file_name == "requirements_new.txt":
                                git_create = os.path.abspath(file_path)

                                if git_create:
                                    with open(git_create, 'r', encoding='utf-8') as read_file:
                                        git_create_requirement = read_file.read()

                            git_requirement_check = find_requirements_files(new_github_path)

                    if zenodo_path:
                        # print(zenodo_path)
                        file_generator_ipynb.file_create(zenodo_path)
                        file_generator_python.file_create(zenodo_path)
                        file_generator_matlab.file_create(zenodo_path)
                        file_generator_R.file_create(zenodo_path)

                        new_zenodo_path = os.path.join(root_directory, zenodo_path)

                        # Call the function to check files in the folder
                        zenodo_file_paths = check_files_in_folder(new_zenodo_path, files_to_check)

                        # Print the file paths
                        for file_name, file_path in zenodo_file_paths.items():
                            if file_name == "output_ipynb.txt":
                                zen_ipynb_file = os.path.abspath(file_path)

                                if zen_ipynb_file:
                                    with open(zen_ipynb_file, 'r', encoding='utf-8') as read_file:
                                        zen_ipynb_file_detail = read_file.read()

                            if file_name == "output_py.txt":
                                zen_py_file = os.path.abspath(file_path)

                                if zen_py_file:
                                    with open(zen_py_file, 'r', encoding='utf-8') as read_file:
                                        zen_py_file_detail = read_file.read()

                            if file_name == "output_matlab.txt":
                                zen_matlab_file = os.path.abspath(file_path)

                                if zen_matlab_file:
                                    with open(zen_matlab_file, 'r', encoding='utf-8') as read_file:
                                        zen_matlab_file_detail = read_file.read()

                            if file_name == "output_R.txt":
                                zen_r_file = os.path.abspath(file_path)

                                if zen_r_file:
                                    with open(zen_r_file, 'r', encoding='utf-8') as read_file:
                                        zen_r_file_detail = read_file.read()

                            if file_name == "error_ipynb.txt":
                                zen_ipynb_file_err = os.path.abspath(file_path)

                                if zen_ipynb_file_err:
                                    with open(zen_ipynb_file_err, 'r', encoding='utf-8') as read_file:
                                        zen_ipynb_file_err_detail = read_file.read()

                            if file_name == "error_py.txt":
                                zen_py_file_err = os.path.abspath(file_path)

                                if zen_py_file_err:
                                    with open(zen_py_file_err, 'r', encoding='utf-8') as read_file:
                                        zen_py_file_err_detail = read_file.read()

                            if file_name == "error_matlab.txt":
                                zen_matlab_file_err = os.path.abspath(file_path)

                                if zen_matlab_file_err:
                                    with open(zen_matlab_file_err, 'r', encoding='utf-8') as read_file:
                                        zen_matlab_file_err_detail = read_file.read()

                            if file_name == "error_R.txt":
                                zen_r_file_err = os.path.abspath(file_path)

                                if zen_r_file_err:
                                    with open(zen_r_file_err, 'r', encoding='utf-8') as read_file:
                                        zen_r_file_err_detail = read_file.read()

                            if file_name == "error_requirement.txt":
                                zen_requirement = os.path.abspath(file_path)

                                if zen_requirement:
                                    with open(zen_requirement, 'r', encoding='utf-8') as read_file:
                                        zen_requirement_detail = read_file.read()

                            if file_name == "requirements_new.txt":
                                zen_create = os.path.abspath(file_path)

                                if zen_create:
                                    with open(zen_create, 'r', encoding='utf-8') as read_file:
                                        zen_create_requirement = read_file.read()

                            zen_requirement_check = find_requirements_files(new_zenodo_path)

                    if osf_path:
                        # print(osf_path)
                        file_generator_ipynb.file_create(osf_path)
                        file_generator_python.file_create(osf_path)
                        file_generator_matlab.file_create(osf_path)
                        file_generator_R.file_create(osf_path)

                        new_osf_path = os.path.join(root_directory, osf_path)

                        # Call the function to check files in the folder
                        osf_file_paths = check_files_in_folder(new_osf_path, files_to_check)
                        # print(osf_file_paths)

                        # Print the file paths
                        for file_name, file_path in osf_file_paths.items():
                            if file_name == "output_ipynb.txt":
                                osf_ipynb_file = os.path.abspath(file_path)

                                if osf_ipynb_file:
                                    with open(osf_ipynb_file, 'r', encoding='utf-8') as read_file:
                                        osf_ipynb_file_detail = read_file.read()

                            if file_name == "output_py.txt":
                                osf_py_file = os.path.abspath(file_path)

                                if osf_py_file:
                                    with open(osf_py_file, 'r', encoding='utf-8') as read_file:
                                        osf_py_file_detail = read_file.read()

                            if file_name == "output_matlab.txt":
                                osf_matlab_file = os.path.abspath(file_path)

                                if osf_matlab_file:
                                    with open(osf_matlab_file, 'r', encoding='utf-8') as read_file:
                                        osf_matlab_file_detail = read_file.read()

                            if file_name == "output_R.txt":
                                osf_r_file = os.path.abspath(file_path)

                                if osf_r_file:
                                    with open(osf_r_file, 'r', encoding='utf-8') as read_file:
                                        osf_r_file_detail = read_file.read()

                            if file_name == "error_ipynb.txt":
                                osf_ipynb_file_err = os.path.abspath(file_path)

                                if osf_ipynb_file_err:
                                    with open(osf_ipynb_file_err, 'r', encoding='utf-8') as read_file:
                                        osf_ipynb_file_err_detail = read_file.read()

                            if file_name == "error_py.txt":
                                osf_py_file_err = os.path.abspath(file_path)

                                if osf_py_file_err:
                                    with open(osf_py_file_err, 'r', encoding='utf-8') as read_file:
                                        osf_py_file_err_detail = read_file.read()

                            if file_name == "error_matlab.txt":
                                osf_matlab_file_err = os.path.abspath(file_path)

                                if osf_matlab_file_err:
                                    with open(osf_matlab_file_err, 'r', encoding='utf-8') as read_file:
                                        osf_matlab_file_err_detail = read_file.read()

                            if file_name == "error_R.txt":
                                osf_r_file_err = os.path.abspath(file_path)

                                if osf_r_file_err:
                                    with open(osf_r_file_err, 'r', encoding='utf-8') as read_file:
                                        osf_r_file_err_detail = read_file.read()

                            if file_name == "error_requirement.txt":
                                osf_requirement = os.path.abspath(file_path)

                                if osf_requirement:
                                    with open(osf_requirement, 'r', encoding='utf-8') as read_file:
                                        osf_requirement_detail = read_file.read()

                            if file_name == "requirements_new.txt":
                                osf_create = os.path.abspath(file_path)

                                if osf_create:
                                    with open(osf_create, 'r', encoding='utf-8') as read_file:
                                        osf_create_requirement = read_file.read()

                            osf_requirement_check = find_requirements_files(new_osf_path)

                    end_time = time.time()  # Record the end time
                    duration_seconds = end_time - start_time  # Calculate the duration in seconds
                    formatted_duration = format_time(duration_seconds)

                    total_rows = len(github_results) + len(zenodo_results) + len(osf_results)

                    if github_check:
                        total_result += 1

                    if zenodo_check:
                        total_result += 1

                    if osf_check:
                        total_result += 1

                    result = {
                        'filename': pdf_name,
                        'filepath': pdf_file,
                        'git_results': github_results,
                        'git_check': github_check,
                        'zen_results': zenodo_results,
                        'zen_check': zenodo_check,
                        'os_results': osf_results,
                        'os_check': osf_check,
                        'os_result': osf_result,
                        'zen_result': zenodo_result,
                        'git_result': github_result,
                        'git_path': str(root_directory) + "\\" + str(github_path),
                        'zen_path': str(root_directory) + "\\" + str(zenodo_path),
                        'os_path': str(root_directory) + "\\" + str(osf_path),
                        'git_size': github_size,
                        'zen_size': zenodo_size,
                        'osf_size': osf_size,
                        'all_search_file': all_search_file,
                        'git_readme': git_readme,
                        'zen_readme': zen_readme,
                        'osf_readme': osf_readme,
                        'dur_min': formatted_duration,
                        'total_row': total_rows + 1,
                        'total_res': total_result + 1,
                        'total_file_1': total_files,
                        'total_file_2': total_files + 2,
                        'folders': folders,
                        'git_folder': github_folder,
                        'zen_folder': zenodo_folder,
                        'osf_folder': osf_folder,
                        'folder_count': folder_count,
                        'git_file': github_search_file,
                        'zen_file': zenodo_search_file,
                        'osf_file': osf_search_file,
                        'git_total': github_total_files + 1,
                        'zen_total': zenodo_total_files + 1,
                        'osf_total': osf_total_files + 1,
                        'git_ipynb_file': git_ipynb_file,
                        'git_py_file': git_py_file,
                        'git_matlab_file': git_matlab_file,
                        'git_r_file': git_r_file,
                        'git_ipynb_file_err': git_ipynb_file_err,
                        'git_py_file_err': git_py_file_err,
                        'git_matlab_file_err': git_matlab_file_err,
                        'git_r_file_err': git_r_file_err,
                        'git_requirement': git_requirement,
                        'git_create': git_create,
                        'zen_ipynb_file': zen_ipynb_file,
                        'zen_py_file': zen_py_file,
                        'zen_matlab_file': zen_matlab_file,
                        'zen_r_file': zen_r_file,
                        'zen_ipynb_file_err': zen_ipynb_file_err,
                        'zen_py_file_err': zen_py_file_err,
                        'zen_matlab_file_err': zen_matlab_file_err,
                        'zen_r_file_err': zen_r_file_err,
                        'zen_requirement': zen_requirement,
                        'zen_create': zen_create,
                        'osf_ipynb_file': osf_ipynb_file,
                        'osf_py_file': osf_py_file,
                        'osf_matlab_file': osf_matlab_file,
                        'osf_r_file': osf_r_file,
                        'osf_ipynb_file_err': osf_ipynb_file_err,
                        'osf_py_file_err': osf_py_file_err,
                        'osf_matlab_file_err': osf_matlab_file_err,
                        'osf_r_file_err': osf_r_file_err,
                        'osf_requirement': osf_requirement,
                        'osf_create': osf_create,
                        'git_ipynb_file_detail': git_ipynb_file_detail,
                        'git_py_file_detail': git_py_file_detail,
                        'git_matlab_file_detail': git_matlab_file_detail,
                        'git_r_file_detail': git_r_file_detail,
                        'git_ipynb_file_err_detail': git_ipynb_file_err_detail,
                        'git_py_file_err_detail': git_py_file_err_detail,
                        'git_matlab_file_err_detail': git_matlab_file_err_detail,
                        'git_r_file_err_detail': git_r_file_err_detail,
                        'git_requirement_detail': git_requirement_detail,
                        'git_requirement_check': git_requirement_check,
                        'git_create_requirement': git_create_requirement,
                        'zen_ipynb_file_detail': zen_ipynb_file_detail,
                        'zen_py_file_detail': zen_py_file_detail,
                        'zen_matlab_file_detail': zen_matlab_file_detail,
                        'zen_r_file_detail': zen_r_file_detail,
                        'zen_ipynb_file_err_detail': zen_ipynb_file_err_detail,
                        'zen_py_file_err_detail': zen_py_file_err_detail,
                        'zen_matlab_file_err_detail': zen_matlab_file_err_detail,
                        'zen_r_file_err_detail': zen_r_file_err_detail,
                        'zen_requirement_detail': zen_requirement_detail,
                        'zen_create_requirement': zen_create_requirement,
                        'zen_requirement_check': zen_requirement_check,
                        'osf_ipynb_file_detail': osf_ipynb_file_detail,
                        'osf_py_file_detail': osf_py_file_detail,
                        'osf_matlab_file_detail': osf_matlab_file_detail,
                        'osf_r_file_detail': osf_r_file_detail,
                        'osf_ipynb_file_err_detail': osf_ipynb_file_err_detail,
                        'osf_py_file_err_detail': osf_py_file_err_detail,
                        'osf_matlab_file_err_detail': osf_matlab_file_err_detail,
                        'osf_r_file_err_detail': osf_r_file_err_detail,
                        'osf_requirement_detail': osf_requirement_detail,
                        'osf_create_requirement': osf_create_requirement,
                        'osf_requirement_check': osf_requirement_check,
                    }

                    results.append(result)

                except Exception as e:
                    print(f'Error occurred: {str(e)}')

    return render(request, "upload.html", {'search_results': results})
