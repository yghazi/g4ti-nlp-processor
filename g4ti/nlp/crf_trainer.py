from itertools import chain
import nltk
import spacy
from nltk.corpus import ConllChunkCorpusReader
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelBinarizer
import sklearn
import pycrfsuite
from spacy.tokenizer import Tokenizer
from unidecode import unidecode
import re

from g4ti import constants


# train_sents = tokenizer.get_training_samples()


def get_training_samples():
    """
    Get training samples
    :return:
    """
    TRAIN_DATA_PATH = constants.G4TI_TRAINING_DIR

    _reader = ConllChunkCorpusReader(TRAIN_DATA_PATH, r'.*\.tsv$', chunk_types='LP')
    l = []
    return _reader.iob_sents()

def shape(word):
    word_shape = 'other'
    if re.match('[0-9]+(\.[0-9]*)?|[0-9]*\.[0-9]+$', word):
        word_shape = 'number'
    elif re.match('\W+$', word):
        word_shape = 'punct'
    elif re.match('[A-Z][a-z]+$', word):
        word_shape = 'capitalized'
    elif re.match('[A-Z]+$', word):
        word_shape = 'uppercase'
    elif re.match('[a-z]+$', word):
        word_shape = 'lowercase'
    elif re.match('[A-Z][a-z]+[A-Z][a-z]+[A-Za-z]*$', word):
        word_shape = 'camelcase'
    elif re.match('[A-Za-z]+$', word):
        word_shape = 'mixedcase'
    elif re.match('__.+__$', word):
        word_shape = 'wildcard'
    elif re.match('[A-Za-z0-9]+\.$', word):
        word_shape = 'ending-dot'
    elif re.match('[A-Za-z0-9]+\.[A-Za-z0-9\.]+\.$', word):
        word_shape = 'abbreviation'
    elif re.match('[A-Za-z0-9]+\-[A-Za-z0-9\-]+.*$', word):
        word_shape = 'contains-hyphen'
    elif re.match('((?<![0-9])(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2})[.](?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2})[.](?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2})[.](?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2})(?![0-9]))', word):
        word_shape = 'ip'
    elif re.match('((?:[a-zA-Z0-9.]+)@(?:[a-z]+.)(?:[a-z]{2,62}.[a-z]{2}|[a-z]{2,62}))', word):
        word_shape = 'email'
    elif re.match('((?:[HK][A-Z\_]+|[A-Z]+)\+\s+(?:.*)\+[a-zA-Z]+)', word):
        word_shape = 'registry-key'
    elif re.match('[a-hA-H0-9]{32}', word):
        word_shape = 'md5'
    elif re.match('(?:[a-z0-9\-]+\.)(?:[a-z]{2,18}\.[a-z]{2}|[a-z]{2,18})', word):
        word_shape = 'url'
    return word_shape


def word2features(sent, i):
    word = sent[i][0]
    postag = sent[i][1]
    features = [
        'bias',
        'word.lower=' + word.lower(),
        'word[-3:]=' + word[-3:],
        'word[-2:]=' + word[-2:],
        'word.isupper=%s' % word.isupper(),
        'word.istitle=%s' % word.istitle(),
        'word.isdigit=%s' % word.isdigit(),
        'postag=' + postag,
        'postag[:2]=' + postag[:2],
        'word.shape=' + shape(word)
    ]
    if i > 0:
        word1 = sent[i - 1][0]
        postag1 = sent[i - 1][1]
        features.extend([
            '-1:word.lower=' + word1.lower(),
            '-1:word.istitle=%s' % word1.istitle(),
            '-1:word.isupper=%s' % word1.isupper(),
            '-1:postag=' + postag1,
            '-1:postag[:2]=' + postag1[:2],
            'word.shape=' + shape(word1)
        ])
    else:
        features.append('BOS')

    if i < len(sent) - 1:
        word1 = sent[i + 1][0]
        postag1 = sent[i + 1][1]
        features.extend([
            '+1:word.lower=' + word1.lower(),
            '+1:word.istitle=%s' % word1.istitle(),
            '+1:word.isupper=%s' % word1.isupper(),
            '+1:postag=' + postag1,
            '+1:postag[:2]=' + postag1[:2],
            'word.shape=' + shape(word1)
        ])
    else:
        features.append('EOS')

    return features


def sent2features(sent):
    return [word2features(sent, i) for i in range(len(sent))]


def sent2labels(sent):
    return [label for token, postag, label in sent]


def sent2tokens(sent):
    return [token for token, postag, label in sent]


train_sents = get_training_samples()
print(train_sents[0])
print(sent2features(train_sents[0])[0])

X_train = [sent2features(s) for s in train_sents]
y_train = [sent2labels(s) for s in train_sents]
trainer = pycrfsuite.Trainer(verbose=False)

for xseq, yseq in zip(X_train, y_train):
    trainer.append(xseq, yseq)

trainer.set_params({
    'c1': 1.0,  # coefficient for L1 penalty
    'c2': 1e-3,  # coefficient for L2 penalty
    'max_iterations': 50,  # stop earlier

    # include transitions that are possible, but not observed
    'feature.possible_transitions': True
})


trainer.train(constants.BASE_DIR + "/" + 'my-model.crfsuite')


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


tagger = pycrfsuite.Tagger()
tagger.open(constants.BASE_DIR + "/" + 'my-model.crfsuite')


def ner_tag_text():
    """
    NER tag text
    :param text:
    :return: CONLL IOB format text
    """
    with open(constants.TEST_DIR + '/carbanak-test.txt') as f:
        text = f.read()
        f.close()

    for s in get_sentences(text):
        tokens = list(filter(lambda w: not w.isspace(), [t.text for t in tokenizer.__call__(s)]))
        labels = tagger.tag(sent2features(nltk.pos_tag(tokens)))
        for i in range(0, len(tokens)):
            print(tokens[i] + ' ' + labels[i])


ner_tag_text()

from collections import Counter

info = tagger.info()


def print_transitions(trans_features):
    for (label_from, label_to), weight in trans_features:
        print("%-6s -> %-7s %0.6f" % (label_from, label_to, weight))


print("Top likely transitions:")
print_transitions(Counter(info.transitions).most_common(15))

print("\nTop unlikely transitions:")
print_transitions(Counter(info.transitions).most_common()[-15:])
