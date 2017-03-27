import codecs
import os
import hashlib
import time

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


def annotate_conll(annotated_content):
    """
    Properly formats annotated content in CONLL style
    (word  pos-tag  ner-label), and writes it to file
    to make it part of the training corpus.
    :param annotated_content: the required content dictionary
    :return:
    """
    content = annotated_content['text']
    meta = dict(annotated_content['metadata'])
    sentences = sent_tokenize(content)
    file_content = ''
    for sentence in sentences:
        subseq_tokens = []
        sent_tokens = word_tokenize(sentence)
        sent_pos = list(pos_tag(sent_tokens))
        for i, token in enumerate(sent_tokens):
            meta_token = meta.get(token, None)
            pos = sent_pos.__getitem__(i)[1]

            if token in subseq_tokens:
                subseq_tokens.remove(token)
                label = "I-" + prev_label
            elif meta_token is not None:
                nextWords = str(meta_token.get('nextWords', None))
                ne_tag = meta_token.get('tag', None)
                if ne_tag is None:
                    raise Exception("What the hell? Tag is None.")
                label = "B-" + ne_tag
                prev_label = ne_tag
                if nextWords is not None:
                    subseq_tokens = nextWords.split(" ")
            else:
                label = 'O'
            file_content += "{}\t{}\t{}\n".format(token, pos, label)
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
        # OK to remove file
        os.remove(file_path)
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
#  TODO: Will retrain every 2 hours.. need to make this configurable

# content = ""
# with open("APT30.txt", encoding='utf-8') as file:
#     content = file.read();
#     file.close()
#
# pos = pos_tag(word_tokenize(content))
# print(pos)

# upload_pending_files(TRAIN_DATA_PATH, constants.DRIVE_CORPUS_FOLDER_ID)
