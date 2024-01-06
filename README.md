# Master Thesis
## Title: Automating investigations on the reproducibility of scientific publications based on their digital artifacts
## Abstract
In the world of scientific research, making sure experiments can be reproducible and get the same results is crucial. This thesis looks closely at this challenge and suggests a solution: a smart system that can check if scientific papers can be reproduced reliably. It pays special attention to how easy it is to get to the data, whether the data is available, and if the code used in the study can be reproduced. As scientists struggle to make their work reproducible, this thesis points the way to a stronger and clearer path for research techniques. This research introduces an automation approach to improving consistency, scalability, and efficiency in examining research outputs. It presents a three-step automated technique for evaluating data accessibility, availability, and reproducibility, providing a systematic and complete approach to reproducibility evaluations. The study compares the automated system's findings against manual investigations for a dataset of 104 publications to evaluate its performance. The findings demonstrate the ability of the system to determine data accessibility and availability, including notable instances of partial repeatability. The study examines how researchers, scientific journals, and data repositories might include automated reproducibility checks into their workflows. This investigation explores automated assessments to enhance research reproducibility, offering a user-friendly platform and insights for a more transparent and collaborative scientific environment.
### Safial Islam Ayon
### Prüfer
1. Prof. Dr. Ulrike Lucke
2. Dr. Christian Riedel
### Betreuer
  Jan Bernoth
## How to Run the Code
To run the code, you must install Anaconda, Python, and PyCharm. 

Here is a "requirements.txt" file, run the file using the "pip install -r requirements.txt" command. 

python.exe -m pip install --upgrade pip

When importing the project in PyCharm and then in the command line run the command `python manage.py runserver`. You can clear the cache using the command `python manage.py clearcache`
## Folder Description
- `static` includes the CSS file and the picture used in the platform.
- `multifileupload` all the settings and URLs in the project.
- `myapp` all the main files including the html file.
## File Description
- `views.py` main file where all the variables and tasks are done.
- `upload.html` contains the web design of the project.
- `checkrepository.py` check the original source of the paper.
- `file_generator_R.py` creates a file that will run all R files.
- `file_generator_ipynb.py` creates a file that will run all Jupyter Notebook files.
- `file_generator__matlab.py` creates a file that will run all Matlab files.
- `file_generator_python.py` creates a file that will run all Python files.
- `github.py` helps to download repository from Github.
- `osf.py` helps to download repository from OSF.
- `pdflink.py` extracts all the links from the pdf.
- `zenodo.py` helps to download repository from Zenodo.
- `pdftitle.py` gets the paper title using the `pdf2doi` library. (not used in the main project)





