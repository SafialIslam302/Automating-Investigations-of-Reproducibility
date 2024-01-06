import os
import subprocess


def file_create(path):
    # Content for the main_file.py
    main_file_content = """import os
import subprocess
from multiprocessing import Process
import time
import re

def delete_existing_output_error_files(path):
    # Check if output.txt and error.txt files exist and delete them if present
    if os.path.isfile(os.path.join(path, 'output_py.txt')):
        os.remove(os.path.join(path, 'output_py.txt'))
    if os.path.isfile(os.path.join(path, 'error_py.txt')):
        os.remove(os.path.join(path, 'error_py.txt'))
    if os.path.isfile(os.path.join(path, 'error_requirement.txt')):
        os.remove(os.path.join(path, 'error_requirement.txt'))
    if os.path.isfile(os.path.join(path, 'requirements_new.txt')):
        os.remove(os.path.join(path, 'requirements_new.txt'))

def run_python_scripts_in_directory(directory):
    # Get a list of all .py files in the directory and its subdirectories
    python_files = []
    current_script = os.path.abspath(__file__)
    excluded_files = [current_script, os.path.abspath("main_file_python.py")]

    for root, _, files in os.walk(directory):
        python_files += [os.path.join(root, file) for file in files if file.endswith('.py') and os.path.abspath(file) not in excluded_files]

    # Loop through each .py file and run it
    for python_file in python_files:
        print(f"Running Python script: {python_file}")

        # Set the working directory to the directory of the Python script
        script_directory = os.path.dirname(python_file)
        
        cmd = ['python', os.path.basename(python_file)]
        timeout_s = 3600

        # Execute the Python script using subprocess and capture the output and errors
        try:
            completed_process = subprocess.Popen(cmd, text=True, cwd=script_directory, shell = True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # Wait for the process to finish and get the return code
            completed_process.wait()
            
            # Capture stdout and stderr content
            output, error = completed_process.communicate(timeout = timeout_s)
                               
        except Exception as e:
            output = ""
            error = str(e)

        out_file = os.path.join(directory, "output_py.txt")
        # Save the output and errors to respective files
        with open(out_file, "a", encoding="utf-8") as out_file:
            out_file.write(f"===== Output for {python_file} =====\\n")
            out_file.write(output)
            out_file.write("\\n\\n")

        err_file = os.path.join(directory, "error_py.txt")
        # Check if 'error' contains any error messages
        if error:
            with open(err_file, "a", encoding="utf-8") as err_file:
                err_file.write(f"===== Errors for {python_file} =====\\n")
                err_file.write(error)
                err_file.write("\\n\\n")

        print(f"Python script execution finished: {python_file}")

def find_requirements_files(root_dir):
    requirements_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower() in ['requirement.txt', 'requirements.txt', 'requirements_new.txt']:
                requirements_files.append(os.path.normpath(os.path.join(dirpath, filename)))
    return requirements_files

def install_requirements(requirements_files, path):
    for file in requirements_files:
        requirements_file = os.path.abspath(file)
        
        with open(requirements_file) as f:
            requirements = f.readlines()
        
        for requirement in requirements:
            try:
                subprocess.run(['pip', 'install', requirement.strip()], shell=True, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            except subprocess.CalledProcessError as e:
                error_log_file = os.path.join(path, "error_requirement.txt")
                with open(error_log_file, "w") as error_file:
                    error_message = e.stderr.decode()
                    error_file.write(f"Error installing libraries from {file}:\\n")
                    error_file.write(f"Failed to install {requirement.strip()}: {e}\\n")
                    error_file.write(error_message)
                    error_file.write("\\n")
        '''cmd = f'pip install -r "{os.path.abspath(file)}"'
        try:
            subprocess.run(cmd, shell=True, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            error_log_file = os.path.join(path, "error_requirement.txt")
            with open(error_log_file, "w") as error_file:
                error_message = e.stderr.decode()
                error_file.write(f"Error installing libraries from {file}:\\n")
                error_file.write(error_message)
                error_file.write("\\n")'''

def find_python_files(directory):
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') and file != 'main_file_python.py':
                python_files.append(os.path.join(root, file))
    return python_files

# Function to remove leading dots from library names
def remove_leading_dot(library_name):
    if library_name.startswith('.'):
        return library_name[1:]
    return library_name

# Function to clean up library names
def clean_library_name(library_name): 
    # Check if the library name contains special characters
    if re.search(r'[,_"-]', library_name):
        return None  # Skip library names with special characters
    else:
        return library_name
        
def extract_libraries_from_python_file(python_file):
    libraries = set()
    with open(python_file, 'r', encoding='ISO-8859-1') as file:
        lines = file.readlines()
        for line in lines:
            # Split the line into words
            words = line.strip().split()
            
            if 'import' in line and words[0] == 'import':
                # Extract libraries from import statements
                line = line.strip().split('import ')[-1]
                for lib in line.split(', '):
                    if ' as ' in lib:
                        libraries.add(lib.split(' as ')[0])
                    else:
                        libraries.add(lib)
            elif 'from ' in line and words[0] == 'from':
                # Extract libraries from from ... import ... statements
                line = line.strip().split('from ')[-1].split(' import ')[0]
                libraries.add(line)
    
    # Clean the list of libraries
    temp_libraries = [remove_leading_dot(library) for library in libraries]
    
    # Clean the list of libraries
    final_libraries = [clean_library_name(library) for library in temp_libraries]
    
    # Filter out None values (library names with special characters)
    final_libraries = [library for library in final_libraries if library is not None]

    return final_libraries
    
def generate_requirements_file(directory):
    python_files = find_python_files(directory)
    libraries = set()
    for python_file in python_files:
        libraries.update(extract_libraries_from_python_file(python_file))
    
    requirements_file = os.path.join(directory, 'requirements_new.txt')
    with open(requirements_file, 'w') as file:
        for library in libraries:
            file.write(f"{library}\\n")
    
    # print(f"Generated {requirements_file} based on Python script dependencies.")
                  
if __name__ == "__main__":
    # Get the current directory where the Python script is located
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Delete existing output.txt and error.txt files (if present)
    delete_existing_output_error_files(current_directory)
    
    # Find the requirement file
    requirements_files = find_requirements_files(current_directory)
    
    if not requirements_files:
        print("No requirements.txt files found.")
        generate_requirements_file(current_directory)
    else:
        install_requirements(requirements_files, current_directory)

    # Run the Python scripts in the current directory and its subdirectories
    run_python_scripts_in_directory(current_directory)
"""

    output_file_path = os.path.join(path, "main_file_python.py")

    # Save the content to main_file.py
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(main_file_content)

    # Run main_file.py
    subprocess.run(["python", output_file_path])

    # Delete the main_file_python.py file
    os.remove(output_file_path)
