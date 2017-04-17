import codecs, os, hashlib, time, re, traceback, spacy
from sre_parse import Tokenizer

from g4ti.api import corpus_file_util
from nltk import word_tokenize, sent_tokenize, pos_tag
from nltk.chunk import tree2conlltags
from nltk.corpus.reader import ConllChunkCorpusReader, pickle

from g4ti import constants

from unidecode import unidecode

TRAIN_DATA_PATH = constants.G4TI_TRAINING_DIR

RAW_DATA_PATH = constants.G4TI_RAW_DIR

TEST_PATH = constants.TEST_DIR

TRAIN_MODEL_PICKLE = constants.TRAIN_MODEL

digest = hashlib.md5()

last_pending_check = round(time.time() * 1000)

troublesome_tags = ["REGKEY", "URL", "DOMAIN", "FILE"]

IP_PATTERN = re.compile(
    '((?<![0-9])(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2})[.](?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2})[.](?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2})[.](?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2})(?![0-9]))')

EMAIL_PATTERN = re.compile('((?:[a-zA-Z0-9.]+)@(?:[a-z]+.)(?:[a-z]{2,62}.[a-z]{2}|[a-z]{2,62}))')

REGKEY_PATTERN = re.compile('((?:[HK][A-Z\_]+|[A-Z]+)\+\s+(?:.*)\+[a-zA-Z]+)')

URL_PATTERN = re.compile('(?:[a-z0-9\-]+\.)(?:[a-z]{2,18}\.[a-z]{2}|[a-z]{2,18})')

DOMAIN_PATTERN = re.compile('[a-zA-Z0-9\_\-]+(?:\.|\[(?:dot|\.)])+[a-zA-Z+\.\[\]]+')

CVE_PATTERN = re.compile('CVE-\d{4}-\d{4}')

HASH_PATTERN = re.compile('[a-fA-F0-9]')

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
    """
    Get current system time in milliseconds
    :return: system time in milliseconds
    """
    return round(time.time() * 1000)


def get_file_name(content):
    """
    Get file name by caclulating content hash
    """
    digest.update(content.encode('utf-8'))
    return digest.hexdigest()


def get_tags(filename):
    text = open(filename).read()
    dic = {}
    lines = text.splitlines()
    for line in lines:
        col = line.split("\t")
        if col[1] != "O":
            dic.__setitem__(col[0], col[1])
    return dic


def get_sentences(content):
    """
    Sentence generator
    :param content:
    :return:
    """
    # remove pesky unicode characters
    decoded_content = unidecode(content)
    doc = tokenizer.__call__(decoded_content)
    sentences = doc.sents
    for s in sentences:
        yield s.string


# Temp function, kind of defective
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
    if IP_PATTERN.match(word):
        pattern_tag = 'B-IP'
    elif EMAIL_PATTERN.match(word):
        pattern_tag = 'B-EMAIL'
    elif REGKEY_PATTERN.match(word):
        pattern_tag = 'B-REGKEY'
    elif HASH_PATTERN.match(word) and (len(word) % 32 == 0 or len(word) % 40 == 0):
        pattern_tag = 'B-HASH'
    elif URL_PATTERN.match(word):
        pattern_tag = 'B-URL'
    elif DOMAIN_PATTERN.match(word):
        pattern_tag = 'B-DOMAIN'
    elif CVE_PATTERN.match(word):
        pattern_tag = 'B-CVE'
    return pattern_tag


# Might be deprecated now, after integrating spacy
def tokenize_with_patterns(sentence):
    print(sentence)
    words = tokenizer.tokenize(sentence)
    # TODO: add check for sentence being empty or None?!
    # particularly for the troublesome patterns.json
    pattern_matches = []
    if URL_PATTERN.search(sentence):
        pattern_matches = URL_PATTERN.findall(sentence)
    if DOMAIN_PATTERN.search(sentence):
        pattern_matches.append(DOMAIN_PATTERN.findall(sentence))
    if REGKEY_PATTERN.search(sentence):
        pattern_matches.append(REGKEY_PATTERN.findall(sentence))
    tokens = []
    i = 0
    while i < words.__len__():
        word = words[i]
        print(word)
        if not word.isalpha():
            found = False
            for match in pattern_matches:
                if word in match:
                    print('This here word %s has a match %s' % (word, match))
                    found = True
                    y = 1
                    w = ''
                    while word in match:
                        try:
                            w += word[i + y]
                            y += 1
                        except IndexError:
                            print('Yikes! Index error.')
                            break

                    if w == match:
                        print("Woohoo!")
                        i += y - 1
                        pattern_matches.remove(match)
                        tokens.append(w)
                        break
                    else:
                        continue
            if not found:
                print('Word %s not found' % word)
                tokens.append(word)
        else:
            tokens.append(word)
        i += 1
    print('***************')
    print(tokens)
    return tokens


def create_tokenizer(nlp):
    # TODO: make it configurable
    custom_infix_regexes = (r'(\S+\.\S+)', r'(\S+\-\S+)') + nlp.Defaults.infixes

    prefix_re = spacy.util.compile_prefix_regex(nlp.Defaults.prefixes)
    suffix_re = spacy.util.compile_suffix_regex(nlp.Defaults.suffixes)
    infix_re = spacy.util.compile_infix_regex(custom_infix_regexes)

    tokenizer = Tokenizer(nlp.vocab,
                          nlp.Defaults.tokenizer_exceptions,
                          prefix_re.search,
                          suffix_re.search,
                          infix_re.finditer,
                          token_match=None)
    make_doc = lambda text: tokenizer(text)
    return make_doc


tokenizer = spacy.load('en', create_make_doc=create_tokenizer)


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
    try:
        if corpus_file_util.upload_file(drive_folder, file_name + ext, file_path):
            print("File %s uploaded" % file_name + ext)
            # TODO: OK to remove file, when in production
            # os.remove(file_path)
            # check for pending uploads, if 15 min have passed since last check
            if (current_milli_time() - last_pending_check) > 900000:
                upload_pending_files(path, drive_folder)
    except:
        print(traceback.format_exc())


def upload_pending_files(path, uplink_folder_id):
    pending_files = os.listdir(path)
    if pending_files:
        for f in pending_files:
            file = path + os.sep + f
            is_uploaded = corpus_file_util.upload_file(folder_id=uplink_folder_id, file_name=f, file=file)
            if is_uploaded:
                os.remove(file)





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
