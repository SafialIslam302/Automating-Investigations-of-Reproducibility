import os
import subprocess


def file_create(path):
    # Content for the main_file.py
    main_file_content = r"""import os
import subprocess
import re

def delete_existing_output_error_files(path):
    # Check if output.txt and error.txt files exist and delete them if present
    # Check if output.txt and error.txt files exist and delete them if present
    if os.path.isfile(os.path.join(path, 'output_R.txt')):
        os.remove(os.path.join(path, 'output_R.txt'))
    if os.path.isfile(os.path.join(path, 'error_R.txt')):
        os.remove(os.path.join(path, 'error_R.txt'))

def find_r_files(folder_path):
    r_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.r'):  # Check for lowercase ".r"
                r_files.append(os.path.join(root, file))
            elif file.lower().endswith('.R'):  # Check for uppercase ".R"
                r_files.append(os.path.join(root, file))
    return r_files

def run_r_script(script_path, path):
    # print(script_path)
    output_file = os.path.join(path, "output_R.txt")
    error_file = os.path.join(path, "error_R.txt")
    
    try:
        with open(output_file, "a") as out:
            os.chdir(path)
            process = subprocess.run(['Rscript', script_path], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
            
            out.write(f"--- {script_path} ---\n")
            out.write(process.stdout)
            out.write("\n\n")
            # print(f"{script_path} executed successfully.")
    except subprocess.CalledProcessError as e:
        # Extract package name from the error message using regular expression
        package_name_match = re.search(r"there is no package called '(\S+)'", e.stderr)
        if package_name_match:
            package_name = package_name_match.group(1)
            # Install the missing package using Rscript command
            install_cmd = f'Rscript -e "options(repos = \'https://cran.rstudio.com/\'); install.packages(\'{package_name}\')"'
            try:
                subprocess.run(install_cmd, shell=True, check=True)
                # print(f"Package '{package_name}' installed successfully.")
            except subprocess.CalledProcessError:
                print(f"Error installing package '{package_name}'.")
                
        print(f"Error executing {script_path}. Check {error_file} for details.")
        with open(error_file, "a") as err:
            err.write(f"--- {script_path} ---\n")
            err.write(e.stderr)
            err.write("\n\n")
       

if __name__ == "__main__":
    # Get the current directory where the Python script is located
    current_directory = os.path.dirname(os.path.abspath(__file__))
    
    # Delete existing output.txt and error.txt files (if present)
    delete_existing_output_error_files(current_directory)

    r_files = find_r_files(current_directory)

    if not r_files:
        print("No .R files found in the current working directory and its subfolders.")
    else:
        # print("Running R scripts...")
        for r_file in r_files:
            # print(f"Running {r_file}...")
            run_r_script(r_file, current_directory)
            # print(f"{r_file} executed successfully.")
"""

    # Concatenate the output path with the filename
    output_file_path = os.path.join(path, "main_file_R.py.py")

    # Save the content to main_file.py
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(main_file_content)

    # Run main_file.py
    subprocess.run(["python", output_file_path])

    # Delete the main_file_R.py file
    os.remove(output_file_path)
