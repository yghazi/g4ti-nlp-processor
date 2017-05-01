import pickle

import spacy
from nltk import tree2conlltags, pos_tag, word_tokenize
from spacy.tokenizer import Tokenizer
from unidecode import unidecode

from g4ti.helpers.config_helper import ConfigHelper


class DefaultTokenizer:
    """ This is the default tokenizer for the tator"""

    def __init__(self):
        print("here we go to create defautl tokenizer ")
        # TODO: make it configurable
        self.custom_infix_regex = (r'(\S+\.\S+)', r'(\S+\-\S+)')
        self.tokenizer = spacy.load('en', create_make_doc=self.create_tokenizer)
        self.config_util = ConfigHelper()

    def create_tokenizer(self, nlp):
        """ This method will create the spacy tokenizer with custom infix regex """
        self.custom_infix_regex = self.custom_infix_regex + nlp.Defaults.infixes
        prefix_re = spacy.util.compile_prefix_regex(nlp.Defaults.prefixes)
        suffix_re = spacy.util.compile_suffix_regex(nlp.Defaults.suffixes)
        infix_re = spacy.util.compile_infix_regex(self.custom_infix_regex)

        tokenizer = Tokenizer(nlp.vocab, nlp.Defaults.tokenizer_exceptions, prefix_re.search, suffix_re.search,
                              infix_re.finditer, token_match=None)
        return lambda text: tokenizer(text)

    def get_tokenizer(self):
        """ This method will return the default tokenizer """
        return self.tokenizer

    def get_sentences(self, content):
        """
        Sentence generator
        :param content:
        :return:
        """
        # remove pesky unicode characters
        decoded_content = unidecode(content)
        doc = self.tokenizer.__call__(decoded_content)
        sentences = doc.sents
        for s in sentences:
            yield s.string

    def ner_tag_text(self, text):
        """
        NER tag text
        :param text:
        :return: CONLL IOB format text
        """
        pickle_file = open(self.config_util.TRAIN_MODEL_PICKLE, 'rb')
        chunker_pickle = pickle.load(pickle_file)
        pickle_file.close()
        return tree2conlltags(chunker_pickle.parse(pos_tag(word_tokenize(text))))

    def tokenize_with_patterns(self, sentence):
        """ Might be deprecated now, after integrating spacy """
        words = self.tokenizer.tokenize(sentence)
        # TODO: add check for sentence being empty or None?!
        # particularly for the troublesome patterns.json
        pattern_matches = []
        if self.config_util.URL_PATTERN.search(sentence):
            pattern_matches = self.config_util.URL_PATTERN.findall(sentence)
        if self.config_util.DOMAIN_PATTERN.search(sentence):
            pattern_matches.append(self.config_util.DOMAIN_PATTERN.findall(sentence))
        if self.config_util.REGKEY_PATTERN.search(sentence):
            pattern_matches.append(self.config_util.REGKEY_PATTERN.findall(sentence))
        tokens = []
        i = 0
        while i < words.__len__():
            word = words[i]
            print(word)
            if not word.isalpha():
                found = False
                for match in pattern_matches:
                    if word in match:
                        print('This here word %s has a match %s' %
                              (word, match))
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
