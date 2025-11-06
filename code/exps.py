import pdfplumber
import unicodedata
import re
import os
import getpass
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings


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
file_name = "en_fatawahajj.pdf"
    # Get the directory of the script
script_dir = os.path.dirname(__file__)
    # Go up one level to the project root and then down to the 'files' directory
files_dir = os.path.join(os.path.dirname(script_dir), 'files')
file_path = os.path.join(files_dir, file_name)

out_path = os.path.join(files_dir, "processed book.txt")

# Read file and process pages
pdf = pdfplumber.open(file_path)
pages = pdf.pages[2:95]

with open(out_path, "w", encoding="utf-8") as file:
    for page in pages:
        text = page.extract_text()
        filtered_text = filter_text(text)
        # filtered_text = re.sub(r'\d[^\n^\\]+[\s\S\n]*', '', filtered_text) # remove footers, WORKING!!!
        # filtered_text = re.sub(r"\[Fatwas of[^]\—\n]*\]", '', filtered_text, flags=re.DOTALL)
        # filtered_text = re.sub(r'[ \w]*Fatwas[ \w]+', '', filtered_text)
        # filtered_text = re.sub(r'\[.*\]', '', filtered_text, flags=re.DOTALL)  # Remove any remaining brackets content
        match = re.search(r'\d+[a-zA-Z_]+', filtered_text) # search for footers
        pls = match.start() if match else -1
        # pls2 = filtered_text.find('1Selected')
        # print(f"pls: {pls}, pls2: {pls2}")
        filtered_text = filtered_text[:pls] # remove footers
        filtered_text = re.sub(r'\d\n', '', filtered_text) # remove numbers
        # filtered_text = re.sub(r'\n{3,}', '\n\n', filtered_text)  # Limit to two consecutive newlines
        if filtered_text.strip():  # Only write if there's non-empty text
            file.write(filtered_text + '\n')  # Add extra newline between pages

# Remove non questions
with open(out_path, "r+", encoding="utf-8") as file:
    content = file.read()
    queastions = content.split('***')
    # Move the file pointer to the beginning and truncate the file
    file.seek(0)
    for q in queastions:
        q = q.strip()
        if q:
            index = q.find('Question:')
            file.write(q[index:] + '\n\n')

# Split by questions
with open(out_path, "r+", encoding="utf-8") as file:
    content = file.read()
    queastions = content.split('Question:')
    # Move the file pointer to the beginning and truncate the file
    file.seek(0)
    for q in queastions:
        q = q.strip()
        if q:
            file.write("Question: " + q + '\n\n')
            file.write('***\n\n')

# # Setup Google Gemini Embeddings
# if not os.environ.get("GOOGLE_API_KEY"): 
#     os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter API key for Google Gemini: ")

# embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

# Setup Chroma vector store
vector_store = Chroma(
    collection_name="onsinization_collection",
    embedding_function=embeddings,
    persist_directory="./chroma_langchain_db",  # Where to save data locally, remove if not necessary
)

# Create documents
docs = []
with open(out_path, "r+", encoding="utf-8") as file:
    content = file.read()
    queastions = content.split('***')

    for q in queastions:
        q = q.strip()
        if q:
            docs.append(Document(
                page_content=q,
                metadata={
                    'source': file_name
                }))


document_ids = vector_store.add_documents(documents=docs)

print(document_ids[:3])

def get_relative(query):
    retrieved_docs = vector_store.similarity_search(query, k=1)
    return retrieved_docs


qen = "What is the ruling on performing Hajj on behalf of a deceased person?"

dcs = get_relative(qen)
print(dcs)

# with open("eng book exps5.txt", "r", encoding="utf-8") as ifile:
#     with open("eng book exps6.txt", "w", encoding="utf-8") as ofile:
#         content = ifile.read()
#         queastions = content.split('***')

#         for q in queastions:
#             q = q.strip()
#             if q:
#                 index = q.find('Question:')
#                 ofile.write(q[index:] + '\n\n')
#                 # ofile.write('************************\n')

# with open("eng book exps6.txt", "r", encoding="utf-8") as ifile:
#     with open("eng book exps7.txt", "w", encoding="utf-8") as ofile:

#         content = ifile.read()
#         queastions = content.split('Question:')

#         for q in queastions:
#             q = q.strip()
#             if q:
#                 ofile.write("Question: " + q + '\n\n')
#                 ofile.write('***\n\n')



# with open("eng book exps4.txt", "r+", encoding="utf-8") as file:
#     content = file.read()
#     # Replace multiple consecutive newlines with a maximum of two
#     cleaned_content = re.sub(r'\d', '', content)
#     # Use re.DOTALL flag to make dot match newlines, and make the pattern more specific
    # cleaned_content = re.sub(r"\[Fatwas of[^]]*?\]", '', cleaned_content, flags=re.DOTALL)
#     # Move the file pointer to the beginning and truncate the file
#     file.seek(0)
#     file.write(cleaned_content)
#     file.truncate()
 

# out_path = "C:/Users/mokar/KAUST Camp/Onsinization/eng book exps.txt"

# with open(out_path, "w", encoding="utf-8") as file:
#     for p in page:
#         text = p.extract_text()
#         # text_rev = algorithm.get_display(text)
#         # shadda = chr(0x0651)
#         # text_rev_dediac = text_rev.replace(" "+shadda, '')
#         # file.write(text_rev_dediac)
#         file.write(text)
        # print(text)
        # break

# # Reverse text with bidi
# from bidi import algorithm

# text_rev = algorithm.get_display(text)
# print('2 \n\n'+text_rev+'\n\n\n')

# # Strip most common diacritic — in real use you would need to get all of them
# shadda = chr(0x0651)
# text_rev_dediac = text_rev.replace(" "+shadda, '')
# print('3 \n\n'+text_rev_dediac)

# reader = PdfReader(path)
# page = reader.pages[342]

# # Extract text and process it for proper Arabic display
# text = page.extract_text()
# reshaped_text = arabic_reshaper.reshape(text)
# bidi_text = get_display(reshaped_text)
# print("\nExtracted and processed text:\n" + bidi_text + '\n')

# # extract text preserving horizontal positioning without excess vertical
# # whitespace (removes blank and "whitespace only" lines)
# print("2 \n" + page.extract_text(extraction_mode="layout", layout_mode_space_vertically=False) + '\n\n\n')

# # adjust horizontal spacing
# print("2 \n" + page.extract_text(extraction_mode="layout", layout_mode_scale_weight=1.0) + '\n\n\n')

# # exclude (default) or include (as shown below) text rotated w.r.t. the page
# print("2 \n" + page.extract_text(extraction_mode="layout", layout_mode_strip_rotated=False) + '\n\n\n')