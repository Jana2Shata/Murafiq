import pdfplumber
import unicodedata
import re
import os
import getpass
from bidi import algorithm
import pyarabic.araby as araby
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings
"""
وعمرته نفقة َطِّيَب ة؛
 سبب
"""

# Helper function to identify Arabic characters
def is_arabic_char(char):
    # Check if character is Arabic, but exclude specific symbols like ﷺ
    if char == 'ﷺ':  # Special handling for the PBUH symbol
        return False
    try:
        return 'ARABIC' in unicodedata.name(char)
    except ValueError:
        return False


# Helper function to filter text
def filter_text(text):
    # Process the text line by line
    lines = text.split('\n')
    filtered_lines = []
    
    for line in lines:
        filtered_line = ''
        for char in line:
            if (not is_arabic_char(char) or  # Not Arabic
                char.isspace() or            # Spaces
                char.isdigit() or           # Numbers
                unicodedata.category(char).startswith('P')):  # Punctuation
                filtered_line += char
        # Clean up multiple spaces within the line
        filtered_line = re.sub(r' +', ' ', filtered_line)
        filtered_lines.append(filtered_line.strip())
    
    # Join lines back together, preserving empty lines for spacing
    return '\n'.join(filtered_lines)


# Prepare file path
file_name = "ar_fatawa-hajj-umrah.pdf"
    # Get the directory of the script
script_dir = os.path.dirname(__file__)
    # Go up one level to the project root and then down to the 'files' directory
files_dir = os.path.join(os.path.dirname(script_dir), 'files')
file_path = os.path.join(files_dir, file_name)

out_path = os.path.join(files_dir, "processed book ar.txt")

# Read file and process pages
pdf = pdfplumber.open(file_path)
pages = pdf.pages[2:96]

with open('loop 1.txt', "w", encoding="utf-8") as file:
    for page in pages:
        filtered_text = page.extract_text()
        filtered_text = algorithm.get_display(filtered_text) # reverse
        # filtered_text = araby.strip_diacritics(filtered_text)
        diacritics_pattern = r'[\s][\u064e\u064f\u0650\u0651\u0652\u064c\u064b\u064d\u0640\ufc62]+'
        filtered_text = re.sub(diacritics_pattern, '', filtered_text)  # Remove diacritics
        filtered_text = re.sub(' ة', 'ة', filtered_text) 
        filtered_text = re.sub(r'\bيف\b', 'في', filtered_text)  
        filtered_text = re.sub(r'\)', '(', filtered_text)
        filtered_text = re.sub(r'\(', ')', filtered_text)

        # filtered_text = filter_text(text)
        # filtered_text = re.sub(r'\d[^\n^\\]+[\s\S\n]*', '', filtered_text) # remove footers, WORKING!!!
        # filtered_text = re.sub(r"\[Fatwas of[^]\—\n]*\]", '', filtered_text, flags=re.DOTALL)
        # filtered_text = re.sub(r'[ \w]*Fatwas[ \w]+', '', filtered_text)
        # filtered_text = re.sub(r'\[.*\]', '', filtered_text, flags=re.DOTALL)  # Remove any remaining brackets content
        match = re.search(r'\)\d\([\s\w]+', filtered_text) # search for footers
        pls = match.start() if match else -1
        # pls2 = filtered_text.find(')1( تم انتقاؤها ')
        # print(f"pls: {pls}, pls2: {pls2}")
        filtered_text = filtered_text[:pls] # remove footers
        # filtered_text = re.sub(r'\d\n', '', filtered_text) # remove numbers
        # filtered_text = re.sub(r'\n{3,}', '\n\n', filtered_text)  # Limit to two consecutive newlines
        if filtered_text.strip():  # Only write if there's non-empty text
            file.write(filtered_text + '\n')  # Add extra newline between pages

# Remove non questions
with open('loop 1.txt', "r", encoding="utf-8") as ifile:
    with open('loop 2.txt', "w", encoding="utf-8") as ofile:
        content = ifile.read()
        queastions = content.split('** *')
        # Move the file pointer to the beginning and truncate the file
        # file.seek(0)
        for q in queastions:
            q = q.strip()
            if q:
                index = q.find('س:')
                ofile.write(q[index:] + '\n\n')

# Split by questions

with open('loop 2.txt', "r", encoding="utf-8") as ifile:
    with open('loop 3.txt', "w", encoding="utf-8") as ofile:
        content = ifile.read()
        queastions = content.split('س:')
        # Move the file pointer to the beginning and truncate the file
        # file.seek(0)
        for q in queastions:
            q = q.strip()
            if q:
                ofile.write("س: " + q + '\n\n')
                ofile.write('***\n\n')
