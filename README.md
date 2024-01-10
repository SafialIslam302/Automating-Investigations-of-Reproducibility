# Master Thesis
## Title: Automating investigations on the reproducibility of scientific publications based on their digital artifacts
## Abstract
In the world of scientific research, it is very crucial to reproduce any scientific exper-iment and get the exact results. This thesis looks closely at this challenge and sug-gests a solution: a smart system that can check if scientific papers can be reproduced reliably. It specifically focuses on the ease of accessing the data, the availability of the data, and the reproducibility of the code employed in the study. As scientists struggle to make their work reproducible, this thesis points the way to a stronger and clearer path for research techniques. This research introduces an automation approach to improving consistency, scalability, and efficiency in examining research outputs. It presents a three-step automated technique for evaluating data accessibility, availa-bility, and reproducibility, providing a systematic approach to reproducibility evalua-tions. To evaluate the performance of the automated approach, the study compares its findings to manual investigations using a dataset of 104 articles. Findings show the ability of the system to determine data accessibility and availability, including notable instances of partial reproducibility. The study looks at how researchers, sci-entific journals, and data repositories might include automated reproducibility checks in their workflows. This investigation explores automated assessments to enhance research reproducibility, offering a user-friendly platform and insights for a more transparent and collaborative scientific environment.
### Safial Islam Ayon
### Prüfer
1. Prof. Dr. Ulrike Lucke
2. Dr. Christian Riedel
### Betreuer
  Jan Bernoth
## How to Run the Code
To run the code, you must install Anaconda, Python, and PyCharm. Additionally, as the platform checks papers for Matlab and RStudio, so install them as well. 

Download the folder <b>Automated_Reproducibility</b> and import it into the PyCharm. 

Here is a "requirements.txt" file, run the file using the "pip install -r requirements.txt" command. Then in the command line run the command `python manage.py runserver`. You can clear the cache using the command `python manage.py clearcache`

## Folder Description
- `static` includes the CSS file and the picture used in the platform.
- `autoreproducibility` all the settings and URLs in the project.
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





