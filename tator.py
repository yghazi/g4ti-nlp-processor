import json

import PyPDF2
import docx
from flask import Flask, request
from flask_cors import CORS

from g4ti import tokenizer

app = Flask(__name__)
CORS(app)


@app.route('/')
def welcome():
    return "Welcome to tator api"


@app.route('/api/content/upload', methods=['POST'])
def upload():
    f = request.files['file']
    if (f.content_type == "application/pdf"):
        pdfReader = PyPDF2.PdfFileReader(f)
        pages = []
        for page in range(pdfReader.numPages):
            pageobj = pdfReader.getPage(page)
            pages.append(pageobj.extractText())

        content = "\n".join(pages)
        tags = tokenizer.ner_tag_text(content)
        return json.dumps({"document": content, "tags": tags})
    elif f.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(f)
        documentText = []
        for para in doc.paragraphs:
            if para.text != "":
                documentText.append(para.text)
        content = "\n".join(documentText);
        tags = tokenizer.ner_tag_text(content)
        return json.dumps({"document": content, "tags": tags})
    elif f.content_type == "text/plain":
        content = f.read().decode('UTF-8')
        tags = tokenizer.ner_tag_text(content)
        return json.dumps({"document": content, "tags": tags})
    else:
        return "Content type %s not supported" % (f.content_type)


if __name__ == '__main__':
    app.run()
