import pdf2doi
import json
import os
import shutil


def get_pdf_title(file_temp, folder_path):
    temp_file = os.path.join(folder_path, 'temp_file.pdf')

    shutil.copyfile(file_temp, temp_file)

    # Set verbose mode to False
    pdf2doi.config.set('verbose', False)

    # Extract DOI-related information from the PDF
    results = pdf2doi.pdf2doi(temp_file)

    try:
        # Convert results dictionary to a JSON string
        json_string = json.dumps(results)

        # Load the JSON string back into a dictionary
        data = json.loads(json_string)

        # Extract the validation_info dictionary and set a default value if it is missing
        validation_info = json.loads(data.get("validation_info", "{}"))

        # Extract the title from the validation_info dictionary and set a default value if it is missing
        title = validation_info.get("title", "")

        # Delete the copy file
        os.remove(temp_file)

        # return the extracted title
        return title
    except Exception as e:
        # Delete the copy file
        os.remove(temp_file)

        # Handle any potential errors during extraction
        print("Error in pdftitle.py:", str(e))
