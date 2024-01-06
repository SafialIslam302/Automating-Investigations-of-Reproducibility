import os
import subprocess


def file_create(path):
    # Content for the main_file.py
    main_file_content = """from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert import NotebookExporter
import nbformat
import os
import ansi2html
import subprocess
import shlex
import base64
from bs4 import BeautifulSoup
from nbconvert.preprocessors import ExecutePreprocessor, ClearOutputPreprocessor

def delete_existing_output_error_files(path):
    # Check if output.txt and error.txt files exist and delete them if present
    if os.path.isfile(os.path.join(path, 'output_ipynb.txt')):
        os.remove(os.path.join(path, 'output_ipynb.txt'))
    if os.path.isfile(os.path.join(path, 'error_ipynb.txt')):
        os.remove(os.path.join(path, 'error_ipynb.txt'))
    if os.path.isfile(os.path.join(path, 'error_requirement.txt')):
        os.remove(os.path.join(path, 'error_requirement.txt'))

def run_notebooks_in_directory(directory):
    # Get a list of all .ipynb files in the directory and its subdirectories
    notebook_files = []
    for root, _, files in os.walk(directory):
        notebook_files += [os.path.join(root, file) for file in files if file.endswith('.ipynb')]

    # Loop through each .ipynb file and run it
    for notebook_file in notebook_files:
        print(f"Running notebook: {notebook_file}")

        # Read the notebook file
        with open(notebook_file, 'r', encoding='utf-8') as f:
            nb_content = f.read()

        # Execute the notebook
        nb_node = nbformat.reads(nb_content, as_version=4)
        clear_output = ClearOutputPreprocessor()
        nb_node, _ = clear_output.preprocess(nb_node, {'metadata': {'path': os.path.dirname(notebook_file)}})
        
        ep = ExecutePreprocessor(timeout=600, kernel_name='python')  # Adjust the timeout as needed
        try:
            ep.preprocess(nb_node, {'metadata': {'path': os.path.dirname(notebook_file)}})
        except Exception as e:
            # If an error occurs during execution, save the error to "error.txt"
            err_file = os.path.join(directory, "error_ipynb.txt")
            with open(err_file, "a", encoding="utf-8") as err_file:
                ansi_converter = ansi2html.Ansi2HTMLConverter()
                error_html = ansi_converter.convert(str(e), full=False)
                
                # Use BeautifulSoup to remove HTML tags
                soup = BeautifulSoup(error_html, 'html.parser')
                error_text = soup.get_text()
                
                err_file.write(f"===== Error in {notebook_file} =====\\n")
                err_file.write(error_text)
                err_file.write("\\n\\n")

        # Export the executed notebook to a new file
        exporter = NotebookExporter()
        (body, resources) = exporter.from_notebook_node(nb_node)
        new_notebook_file = os.path.basename(notebook_file).replace('.ipynb', '_executed.ipynb')
        new_notebook_path = os.path.join(os.path.dirname(notebook_file), new_notebook_file)
        with open(new_notebook_path, 'w', encoding='utf-8') as f:
            f.write(body)

        print(f"Executed notebook saved as: {new_notebook_path}")

        # Save the output of the executed notebook to "output.txt"
        out_file = os.path.join(directory, "output_ipynb.txt")
        
        # Save the figure in this folder
        figure_folder = os.path.join(current_directory, "Figures")
        os.makedirs(figure_folder, exist_ok=True)
       
        with open(out_file, "a", encoding="utf-8") as out_file:
            out_file.write(f"===== Output for {notebook_file} =====\\n")
            for cell in nb_node['cells']:
                if 'outputs' in cell:
                    for output in cell['outputs']:
                        if 'text' in output:
                            out_file.write(output['text'] + "\\n\\n")
                        elif 'data' in output and 'text/plain' in output['data']:
                            out_file.write(output['data']['text/plain']+ "\\n\\n")
                        
                        if 'data' in output and 'image/png' in output['data']:
                            image_data_temp = output['data']['image/png']

                            figure_number = len([name for name in os.listdir(figure_folder) if name.startswith('Figure_')])
                            figure_filename = f"Figure_{figure_number + 1}.jpeg"
                            figure_path = os.path.join(figure_folder, figure_filename)

                            decode_figure = open(figure_path, 'wb')
                            decode_figure.write(base64.b64decode((image_data_temp)))
                            decode_figure.close()
            out_file.write("\\n")

def find_requirements_files(root_dir):
    requirements_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower() in ['requirement.txt', 'requirements.txt']:
                requirements_files.append(os.path.normpath(os.path.join(dirpath, filename)))
    return requirements_files

def install_requirements(requirements_files, path):
    for file in requirements_files:
        cmd = f'pip install -r "{os.path.abspath(file)}"'
        try:
            subprocess.run(cmd, shell=True, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            error_log_file = os.path.join(path, "error_requirement.txt")
            with open(error_log_file, "w") as error_file:
                error_message = e.stderr.decode()
                error_file.write(f"Error installing libraries from {file}:\\n")
                error_file.write(error_message)
                error_file.write("\\n")
                
if __name__ == "__main__":
    # Get the current directory where the Python script is located
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Delete existing output.txt and error.txt files (if present)
    delete_existing_output_error_files(current_directory)
    
    # Find the requirement file
    # root_directory = "."
    requirements_files = find_requirements_files(current_directory)
    
    if not requirements_files:
        print("No requirements.txt files found.")
    else:
        install_requirements(requirements_files, current_directory)

    # Run the notebooks in the current directory and its subdirectories
    run_notebooks_in_directory(current_directory)
"""

    # Concatenate the output path with the filename
    output_file_path = os.path.join(path, "main_file_ipynb.py")

    # Save the content to main_file.py
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(main_file_content)

    # Run main_file.py
    subprocess.run(["python", output_file_path])

    # Delete the main_file_ipynb.py file
    os.remove(output_file_path)
