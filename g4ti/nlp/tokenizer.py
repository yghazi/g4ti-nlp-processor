import codecs
import os
import hashlib
import time
import re
import unicodedata

from g4ti.api import corpus_file_util

from nltk import word_tokenize, sent_tokenize, pos_tag
from nltk.chunk import tree2conlltags
from nltk.corpus.reader import ConllChunkCorpusReader, pickle

from g4ti.nlp import custom_trainer

from g4ti import constants

TRAIN_DATA_PATH = constants.G4TI_TRAINING_DIR

RAW_DATA_PATH = constants.G4TI_RAW_DIR

TEST_PATH = constants.TEST_DIR

TRAIN_MODEL_PICKLE = constants.TRAIN_MODEL

digest = hashlib.sha1()

last_pending_check = round(time.time() * 1000)

dic = {
    "text": "First, you need a web server like Nginx or Apache. You should configure your web server so that it sends "
            "all appropriate requests to one PHP file. You instantiate and run your Slim app in this PHP file.",
    "metadata": {
        "Nginx": {
            "tag": "SERVER"},
        "Apache": {
            "tag": "SERVER"},
        "PHP": {
            "tag": "LANGUAGE",
            "nextWords": "file"}
    }
}


def current_milli_time():
    return round(time.time() * 1000)


def get_file_name(content):
    digest.update(content.encode('utf-8'))
    return digest.hexdigest()


def save_train_file(text):
    """
    Save file in the req training format
    :param text:
    :return:
    """
    sentences = sent_tokenize(text)
    file = open(TRAIN_DATA_PATH + get_file_name(text), 'w')
    file_content = ''
    for sentence in sentences:
        tokens = word_tokenize(sentence)
        tags = pos_tag(tokens)
        for w, t in tags:
            file_content += "{}\t{}\tO\n".format(w, t)
    file.write(file_content)
    file.close()


def get_training_samples():
    _reader = ConllChunkCorpusReader(TRAIN_DATA_PATH, r'.*\.tsv$', chunk_types='LP')
    l = []
    for x in _reader.iob_sents():
        y = []
        for w, t, ne in list(x):
            y.append(((w, t), ne))
        l.append(y)
    return l


def get_tags(filename):
    text = open(filename).read()
    dic = {}
    lines = text.splitlines()
    for line in lines:
        col = line.split("\t")
        if col[1] != "O":
            dic.__setitem__(col[0], col[1])
    return dic


# Temp function
def stanford_to_conll():
    ROOT_ADDRESS = "~/Downloads/ner-training/carbanak-training-data/"
    # read from prev files
    for file in os.listdir(ROOT_ADDRESS):
        if file.endswith(".txt"):
            text = ''
            with codecs.open(ROOT_ADDRESS + file, "r", encoding='utf-8', errors='ignore') as f:
                text = f.read()
            file = str(file).replace("txt", "tsv")
            tags = get_tags(ROOT_ADDRESS + file)
            content = ''
            for sentence in sent_tokenize(text):
                pos_tagged = pos_tag(word_tokenize(sentence))
                for w, t in pos_tagged:
                    ne = tags.get(w, "O")
                    content += "{}\t{}\t{}\n".format(w, t, ne)
            open(TRAIN_DATA_PATH + "/" + get_file_name(text) + ".tags", 'w').write(content)


def pattern_token(word):
    pattern_tag = ''
    if re.match(
            '((?<![0-9])(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2})[.](?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2})[.](?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2})[.](?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2})(?![0-9]))',
            word):
        pattern_tag = 'B-IP'
    elif re.match('((?:[a-zA-Z0-9.]+)@(?:[a-z]+.)(?:[a-z]{2,62}.[a-z]{2}|[a-z]{2,62}))', word):
        pattern_tag = 'B-EMAIL'
    elif re.match('((?:[HK][A-Z\_]+|[A-Z]+)\+\s+(?:.*)\+[a-zA-Z]+)', word):
        pattern_tag = 'B-REGKEY'
    elif re.match('[a-hA-H0-9]', word) and (len(word) % 32 == 0 or len(word) % 40 == 0):
        pattern_tag = 'B-HASH'
    elif re.match('(?:[a-z0-9\-]+\.)(?:[a-z]{2,18}\.[a-z]{2}|[a-z]{2,18})', word):
        pattern_tag = 'B-URL'
    elif re.match('[a-zA-Z0-9\_\-]+(?:\.|\[(?:dot|\.)])+[a-zA-Z+\.\[\]]+', word):
        pattern_tag = 'B-DOMAIN'
    elif re.match('CVE-\d{4}-\d{4}', word):
        pattern_tag = 'B-CVE'
    return pattern_tag


def annotate_conll(annotated_content):
    """
    Properly formats annotated content in CONLL style
    (word  pos-tag  ner-label), and writes it to file
    to make it part of the training corpus.
    :param annotated_content: the required content dictionary
    :return:
    """
    content = annotated_content['text']
    content = unicodedata.normalize('NFKD', content).encode('ascii', 'ignore').decode()
    meta = dict(annotated_content['metadata'])
    sentences = sent_tokenize(content)
    file_content = ''
    for sentence in sentences:
        sent_tokens = word_tokenize(sentence)
        sent_pos = list(pos_tag(sent_tokens))
        i = 0
        while i < sent_tokens.__len__():
            step = 1
            subseq_tokens = ""
            token = sent_tokens[i]
            meta_token = meta.get(token, None)
            pos = sent_pos.__getitem__(i)[1]

            # if meta_token is something else
            if meta_token is not None:
                nextWords = meta_token.get('nextWords', None)
                ne_tag = meta_token.get('tag', None)
                if ne_tag is None:
                    raise Exception("What the hell? Tag is None.")
                label = "B-" + ne_tag
                # prev_label = ne_tag
                if nextWords is not None:
                    length = nextWords.__len__()
                    if length > 0:
                        # check each combination of nextwords for the presence of exactly the same subsequent words
                        y = i + 1
                        # TODO: make sure index doesn't go out of bounds
                        for combo in filter(lambda n: sent_tokens[y: y +  n.__len__()] == n, nextWords):
                            for c in combo:
                                subseq_tokens += "{}\t{}\t{}\n".format(c, sent_pos.__getitem__(y)[1], 'I-' + ne_tag)
                                y += 1
                        step = step if not subseq_tokens else combo.__len__() + step


            else:
                # if no tag assigned, check against pattern
                # or else, assign 'O'
                label = pattern_token(token)
                label = label if label else 'O'

            file_content += "{}\t{}\t{}\n".format(token, pos, label)
            if subseq_tokens:
                file_content += subseq_tokens
            i += step

    # write to file: tagged iob data in train data path and text in raw data path
    file_name = get_file_name(content)
    # save iob annotated file
    save_file(file_name, file_content)
    # save txt file
    save_file(file_name, content, False)


def save_file(file_name, file_content, train=True):
    if file_content is not None:
        drive_folder = constants.DRIVE_CORPUS_FOLDER_ID
        path = TRAIN_DATA_PATH
        ext = '.tsv'
        if not train:
            drive_folder = constants.DRIVE_RAWDOCS_FOLDER_ID
            path = RAW_DATA_PATH
            ext = '.txt'
    file_path = path + os.sep + file_name + ext
    # write temporarily to the folder
    with open(file_path, 'w') as f:
        f.write(file_content)
    if corpus_file_util.upload_file(drive_folder, file_name + ext, file_path):
        print("File %s uploaded" % file_name + ext)
        # TODO: OK to remove file, when in production
        # os.remove(file_path)
        # check for pending uploads, if 15 min have passed since last check
        if (current_milli_time() - last_pending_check) > 900000:
            upload_pending_files(path, drive_folder)
    else:
        print("what the hell?")


def upload_pending_files(path, uplink_folder_id):
    pending_files = os.listdir(path)
    if pending_files:
        for f in pending_files:
            file = path + os.sep + f
            is_uploaded = corpus_file_util.upload_file(folder_id=uplink_folder_id, file_name=f, file=file)
            if is_uploaded:
                os.remove(file)


def train_and_pickle():
    """
    Train model on provided corpus and save serialized corpus as pickle
    :return:
    """
    samples = get_training_samples()
    chunker = custom_trainer.NamedEntityChunker(samples)
    chunker_pickle = open(TRAIN_MODEL_PICKLE, 'wb')
    pickle.dump(chunker, chunker_pickle)
    chunker_pickle.close()


def test_ner():
    with open(TEST_PATH + '/carbanak-test.txt') as test:
        txt = test.read()
        print(ner_tag_text(txt))
        test.close()


def ner_tag_text(text):
    """
    NER tag text
    :param text:
    :return: CONLL IOB format text
    """
    pickle_file = open(TRAIN_MODEL_PICKLE, 'rb')
    chunker_pickle = pickle.load(pickle_file)
    pickle_file.close()
    return tree2conlltags(chunker_pickle.parse(pos_tag(word_tokenize(text))))


# train_and_pickle()
# test_ner()
# while True:
#    print("Train again...")
#    train_and_pickle()
#    time.sleep(60 * 60 * 2)
#
# upload_pending_files(TRAIN_DATA_PATH, constants.DRIVE_CORPUS_FOLDER_ID)
