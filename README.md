# Murafiq 
This project develops a question answering assistant as part of the Murafiq app for the onsinization hackathon.

# Steps to successfully run the system:
The steps shown below are all to be executed in the terminal (*command line*), and they assume a windows operating system. If this was not the case, please search for the equivalent macOS/linux commands.

1. Open visual studio on an empty folder.
2. If you have `git` installed, run `git clone https://github.com/Jana2Shata/Murafiq.git`. Else, manually download the files from this repo: from the (<> code) button -> (Open in visual studio) OR (download zip).
3. If you don't already have python installed, please download it from this website https://www.python.org/downloads/
4. Back to your terminal in visual studio, run `python -m venv .venv`
5. run `.venv\Scripts\activate`
6. run `pip install -r files\reqs.txt`. Note: I tried to include all necessary libraries in the requirements.txt file. But in case I missed some and you got errors, please inspect the error message you got and install the missing library.
7. run `streamlit run .\code\app.py`

The last step should open a website tap on your browser, but it will take time loading. It's quite normal, so please be patient.

Also note that this loading time requires that you should prepare in advance when wanting to present it.

After it finishes loading, you shall be able to ask any questions and receive responses.

Note that the user interface supports both languages (EN + AR), but the actual question-answering interactions are only supported for EN in this demo.

