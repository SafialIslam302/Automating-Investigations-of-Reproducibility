import PyPDF2 as pypdf
import re
import fitz
import requests
import operator
import threading


## get all links from PDF
def get_split(numtosplit):
    '''Split a number into four equal(ish) sections. Number of pages must be greater than 13.'''
    if numtosplit > 4:
        sections = []
        breaksize = int(numtosplit / 4)
        sec1_start = 0
        sec1_end = breaksize
        sec2_start = breaksize + 1
        sec2_end = breaksize * 2
        sec3_start = sec2_end + 1
        sec3_end = breaksize * 3
        sec4_start = sec3_end + 1
        sec4_end = numtosplit

        sections = [(sec1_start, sec1_end),
                    (sec2_start, sec2_end),
                    (sec3_start, sec3_end),
                    (sec4_start, sec4_end)]

        return sections

    raise ValueError("Number too small to split into four sections.")


def get_links_from_page(indexstart, indexend, reportlist, pdf):
    ''' - Extract pages from the PDF using the incoming range.
        - For each page, find annotations, and URIs in the annotations.
            - Get the URIs.
                - For each URI try to make a web request and get the response code.
                - Record the page number, URI, and response code result or NA for
                  timeouts.
    '''

    for i in range(indexstart, indexend):
        page_obj = pdf.getPage(i)
        page_no = i + 1
        try:
            annots = page_obj["/Annots"]
            for a in annots:
                u = a.getObject()
                if "/A" in u:
                    uris = u["/A"]
                    if "/URI" in uris:
                        raw_url = uris["/URI"]
                        try:
                            x = requests.get(raw_url, timeout=5, stream=True)
                            code = x.status_code
                            x.close()
                            request_error = "NA"
                        except Exception as e:
                            # print(e)
                            code = "NA"
                            request_error = str(e)
                        # print("{} : {} : {}".format(page_no, raw_url, code))
                        record = [page_no, raw_url, code, request_error]
                        reportlist.append(record)
        except KeyError:
            continue
    return reportlist


def check_pdf_links(infilepath):
    ''' - Get the number of pages, and split into four equal sections
        - Get the range for each section, and send each section range to the parser running its own thread.
        - return a list of lists [[]] with report data.'''
    print(infilepath)
    pdf = pypdf.PdfFileReader(infilepath)
    pages = pdf.numPages
    link_report = []
    if pages < 80:
        get_links_from_page(0, pages, link_report, pdf)
    else:
        split = get_split(pages)
        threads = []
        for i in range(4):
            th = threading.Thread(target=get_links_from_page, args=(split[i][0], split[i][1], link_report, pdf))
            th.start()
            threads.append(th)
        [th.join() for th in threads]
    link_report.sort(key=operator.itemgetter(0))
    link_report.insert(0, ["page", "uri", "status", "request-error"])
    return link_report


# Using Regular Expression
def extract_urls_from_pdf(pdf_file_temp):
    urls = []
    url_pattern = re.compile(
        r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=\n]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)")
    # 1. r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    # 2. r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=\n]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"

    with open(pdf_file_temp, 'rb') as file:
        reader = pypdf.PdfFileReader(file)
        for page_num in range(reader.numPages):
            page = reader.getPage(page_num)
            text = page.extractText()
            urls.extend(re.findall(url_pattern, text))

    return urls


# Broken URL links
def create_link_from_pdf(string):
    lines = string.split("\n")
    link_parts = [lines[0]]

    all_strings = []
    all_strings.append(str(link_parts[0]))

    for line in lines[1:]:
        if "\n" not in line:
            all_strings.append(str(link_parts[0]) + line)
        else:
            break

    return all_strings


def broken_urls_from_pdf(pdf_file_temp):
    # A regular expression of URLs
    url_regex = r"(https?://(?:\S+|\n)+)"

    # Open the PDF file
    with fitz.open(pdf_file_temp) as pdf:
        text = ""
        for page in pdf:
            # Extract text of each PDF page
            text += page.get_text()

        # Find URLs using regex
        urls = re.findall(url_regex, text, re.MULTILINE)

        # Create a list to store all links
        all_links = []

        # Print the URLs
        for url in urls:
            link = create_link_from_pdf(url)
            all_links.extend(link)

        return all_links
