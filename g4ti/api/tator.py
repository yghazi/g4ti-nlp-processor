import json

import PyPDF2
import docx
from flask import Flask, request
from flask_cors import CORS

from g4ti import constants
from g4ti.helpers.drive_helper import DriveHelper
from g4ti.nlp.annotator import Annotator

app = Flask(__name__)
CORS(app)

annotator = Annotator()
drive_helper = DriveHelper()

@app.route('/')
def welcome():
    return "Welcome to tator api"


@app.route('/api/oauth-url')
def oauth_for_drive():
    return drive_helper.get_authentication_url()


@app.route('/api/oauth-code', methods=['POST'])
def oauth_set_code():
    code = request.get_data()
    is_auth = drive_helper.set_authentication_code(code)
    return "{'auth': %r }" % is_auth


@app.route("/api/tags")
def tags():
    with open(constants.BASE_DIR + '/tags.json') as f:
        return f.read()
    return '[{"tags":"null"}]'


@app.route("/api/train/", methods=['POST'])
def train():
    annotated_content = request.get_data()
    annotated_content = annotated_content.decode('UTF-8')
    annotated_content = json.loads(annotated_content)
    annotator.annotate_conll(annotated_content)
    return "{'submitted':true}"


@app.route('/api/content/upload', methods=['POST'])
def upload():
    f = request.files['file']
    if f.content_type == "application/pdf":
        pdfReader = PyPDF2.PdfFileReader(f)
        pages = []
        for page in range(pdfReader.numPages):
            pageobj = pdfReader.getPage(page)
            pages.append(pageobj.extractText())

        content = "\n".join(pages).decode('utf-8')
        # tags = tokenizer.ner_tag_text(content)
        return json.dumps({"document": content})
    elif f.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(f)
        documentText = []
        for para in doc.paragraphs:
            if para.text != "":
                documentText.append(para.text)
        content = "\n".join(documentText);
        # print(content)
        # tags = tokenizer.ner_tag_text(content)
        return json.dumps({"document": content})
    elif f.content_type == "text/plain":
        content = f.read().decode('UTF-8')
        # tags = tokenizer.ner_tag_text(content)
        # print(tags)
        return json.dumps({"document": content})
    else:
        return "Content type %s not supported" % (f.content_type)


def run():
    """ Run app """
    app.run(host='0.0.0.0')
