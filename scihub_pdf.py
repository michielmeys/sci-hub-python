import rispy
import os
import requests
from bs4 import BeautifulSoup
import wget
import csv

# rispy from https://github.com/MrTango/rispy
# Sci-Hub bulk download as in https://www.youtube.com/watch?v=7W2tolKDU1s&list=WL&index=26


def get_pdf(filepath, base_url='https://sci-hub.ru/', max_char=100):
    """
    Tries to download articles as PDFs by searching their DOI on Sci-Hub.
    Found articles are stored in new folder, info files are also saved.

    :param filepath: path to list of wanted articles in EndNote format
    :param base_url: base URL of preferred (and working) Sci-Hub domain
    :param max_char: max length of output PDF names (excluding extension)
    :return: None
    """

    # import reference data from EndNote format
    with open(filepath, 'r') as bibliography_file:
        entries = rispy.load(bibliography_file)
    n_entries = len(entries)

    # derive modality type
    mod = filepath.split('_')[0]

    # prepare output folders
    output_folder = f'{mod}/Downloaded PDFs'
    if not os.path.isdir(output_folder):
        os.makedirs(output_folder)

    # initiate info file on PDFs
    f_all_pdf = open(f'{mod}/PDFs_All.csv', 'w')
    csv.writer(f_all_pdf, delimiter=';').writerow(['#', 'Downloaded', 'Year', 'Author', 'DOI', 'Title'])
    csv.writer(f_all_pdf, delimiter=';').writerow([])

    # initiate info file on PDFs not found
    f_no_pdf = open(f'{mod}/PDFs_Not_Found.csv', 'w')
    csv.writer(f_no_pdf, delimiter=';').writerow(['#', 'Downloaded', 'Year', 'Author', 'DOI', 'Title'])
    csv.writer(f_no_pdf, delimiter=';').writerow([])

    # search for each article using DOI
    for idx, entry in enumerate(entries):

        print(f'Processing article {idx + 1}/{n_entries} ...')

        # select DOI
        doi = entry['doi']
        if doi.startswith('https'):
            doi = doi.split('org/')[1]

        # other relevant information
        name = entry.get('authors', ['(author)'])[0].split(',')[0]
        year = entry.get('year', '(year)')
        title = entry.get('title', '(title)').replace('/', ' ')

        # try finding article on Sci-Hub
        try:
            response = requests.get(base_url + doi)
            soup = BeautifulSoup(response.content, 'html.parser')
            content = soup.find('embed').get('src').replace('#navpanes=0&view=FitH', '').replace('//', '/')
            if content.startswith(('/downloads', '/tree', '/uptodate')):
                pdf = base_url[:-1] + content
            else:
                pdf = 'https:/' + content

            # save PDF
            filename = f'{name}-{year}-{title}'[:max_char]
            wget.download(pdf, out=f'{output_folder}/{filename}.pdf')

            # write to info file
            csv.writer(f_all_pdf, delimiter=';').writerow([idx + 1, 'x', year, name, doi, title])

        except AttributeError:
            # write to info files
            csv.writer(f_all_pdf, delimiter=';').writerow([idx + 1, '', year, name, doi, title])
            csv.writer(f_no_pdf, delimiter=';').writerow([idx + 1, '', year, name, doi, title])

    # close info files
    f_all_pdf.close()
    f_no_pdf.close()
