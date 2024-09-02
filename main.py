from pypdf import PdfReader
from pyresparser import ResumeParser
import pdfplumber
import fitz


reader=PdfReader('signed.pdf')

data= ResumeParser("Shreyas_resume.pdf").get_extracted_data()
print(data)
# print(len(reader.pages))
# print()
# for i in range(0,len(reader.pages)):
#     page=reader.pages[0];
#     print(page.extract_text());
