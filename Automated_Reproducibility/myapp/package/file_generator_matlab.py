import os
import subprocess


def file_create(path):
    # Content for the main_file.py
    main_file_content = r"""import os
import subprocess
import time

def delete_existing_output_error_files(path):
    # Check if output.txt and error.txt files exist and delete them if present
    if os.path.isfile(os.path.join(path, 'output_matlab.txt')):
        os.remove(os.path.join(path, 'output_matlab.txt'))
    if os.path.isfile(os.path.join(path, 'error_matlab.txt')):
        os.remove(os.path.join(path, 'error_matlab.txt'))
        
def find_all_matlab_files(root_folder):
    # print("Root: ", root_folder)
    matlab_files = []
    for root, _, files in os.walk(root_folder):
        for file in files:
            if file.endswith('.m'):
                relative_path = os.path.relpath(os.path.join(root, file), root_folder)
                matlab_files.append(relative_path)
    return matlab_files

def sanitize_path(path):
    # Encode the path using 'ascii' encoding and ignore characters that cannot be encoded
    sanitized_path = path.encode('ascii', 'ignore').decode('ascii')
    return sanitized_path

def generate_run_all_scripts(matlab_files, directory):
    run_script = os.path.join(directory, "run_all_scripts.m")
    with open(run_script, "w", encoding="utf-8") as f:
        f.write("% run_all_scripts.m\n\n")
        f.write("% Clear any existing variables and close all figures\n")
        f.write("clearvars;\n")
        f.write("close all;\n\n")

        for matlab_file in matlab_files:
            sanitized_path = sanitize_path(matlab_file)

            if sanitized_path.startswith('.\\'):
                script_name = sanitized_path[2:]
            else:
                script_name = sanitized_path

            if "run_all_scripts" in script_name:
                continue  # Skip the run_all_scripts.m file itself

            f.write(f"% Run {script_name}\n")
            f.write(f"try\n")
            f.write(f"    diary('output_matlab.txt');\n")  # Start capturing output to a file
            f.write(f"    disp(' ');\n")
            f.write(f"    disp('Output in {script_name}:');\n")
            f.write(f"    run('{script_name}');\n")
            f.write(f"    disp(' ');\n")
            f.write(f"    diary off;\n")  # Stop capturing output to a file
            f.write(f"catch ME\n")
            f.write(f"    diary('error_matlab.txt');\n")  # Start capturing error output to a file
            f.write(f"    disp('Error in {script_name}:');\n")
            f.write(f"    disp(ME.message);\n")
            f.write(f"    disp(' ');\n")
            f.write(f"    diary off;\n")  # Stop capturing error output to a file
            f.write(f"end\n\n")
            f.write(f"pause(10);\n\n")

        f.write("disp('All MATLAB scripts have been executed.');\n")
        f.write("exit;")

def run_matlab_scripts(directory):
    # Change the current working directory to the directory where MATLAB scripts are located
    all_matlab_files = find_all_matlab_files(directory)

    if all_matlab_files:
        generate_run_all_scripts(all_matlab_files, directory)
        os.chdir(directory)
        
        # Construct the MATLAB command to run the 'run_all_scripts.m' script
        matlab_command = f"matlab -r \"run_all_scripts\""
    
        try:
            # Run the MATLAB script using subprocess and capture the output and errors
            completed_process = subprocess.Popen(matlab_command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            while True:
                output = subprocess.check_output('tasklist', shell=True, text=True)
                if 'MATLAB.exe' not in output:
                    break
            
        except Exception as e:
            # Exception handling code
            print("An error occurred:", e)
            
        print("Finish running all MATLAB scripts")
    else:
        return 0

if __name__ == "__main__":
    # Get the current directory where the Python script is located
    current_directory = os.path.dirname(os.path.abspath(__file__))
    
    # Delete existing output_matlab.txt and error_matlab.txt files (if present)
    delete_existing_output_error_files(current_directory)

    # Run the MATLAB scripts in the current directory
    run_matlab_scripts(current_directory)
"""

    def find_all_files(root_folder, file_list):
        found_files = []
        for root, _, files in os.walk(root_folder):
            for file in files:
                if file in file_list:
                    found_files.append(os.path.join(root, file))
        return found_files

    def delete_files(file_list):
        for file_name in file_list:
            if os.path.exists(file_name):
                os.remove(file_name)

    root_folder = "."  # Replace this with the root folder path you want to search
    file_list = ["main_file_R.py", "run_all_scripts.m"]

    # Create the full path for each file
    full_path_files = [os.path.join(path, filename) for filename in file_list]

    # Search for the files in the root folder and its subfolders
    found_files = find_all_files(root_folder, full_path_files)

    # Delete the files if found
    delete_files(found_files)

    output_file_path = os.path.join(path, "main_file_R.py")

    # Save the content to main_file_R.py
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(main_file_content)

    # Run main_file.py
    subprocess.run(["python", output_file_path])

    os.remove(output_file_path)
