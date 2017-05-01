from nltk import pos_tag

from g4ti.helpers.app_helper import AppHelper
from g4ti.helpers.config_helper import ConfigHelper
from g4ti.helpers.file_helper import FileHelper
from g4ti.helpers.tokenizer_helper import TokenizerHelper
from g4ti.nlp.default_tokenizer import DefaultTokenizer


class Annotator:
    def __init__(self):
        self.config_util = ConfigHelper()
        self.app_helper = AppHelper()
        self.default_tokenizer = DefaultTokenizer()
        self.tokenizer_helper = TokenizerHelper()
        self.file_helper = FileHelper()

    def annotate_conll(self, annotated_content):
        """
        Properly formats annotated content in CONLL style
        (word  pos-tag  ner-label), and writes it to file
        to make it part of the training corpus.
        :param annotated_content: the required content dictionary
        :return:
        """
        content = annotated_content['text']
        meta = dict(annotated_content['metadata'])
        # sentences = sent_tokenize(content)
        # sentences = tokenizer.tokenize_sents(content)
        file_content = ''
        for sentence in self.default_tokenizer.get_sentences(content):
            sent_tokens = list(filter(lambda w: not w.isspace(), [
                t.text for t in self.default_tokenizer.get_tokenizer().__call__(sentence)]))
            # sent_tokens = word_tokenize(sentence)
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
                    if any(nextWords):
                        length = nextWords.__len__()
                        # check each combination of nextwords for the presence
                        # of exactly the same subsequent words
                        y = i + 1
                        # TODO: make sure index doesn't go out of bounds
                        for combo in filter(lambda n: sent_tokens[y: y + n.__len__()] == n, nextWords):
                            if ne_tag not in self.config_util.annotator_troublesome_tags:
                                for c in combo:
                                    subseq_tokens += "{}\t{}\t{}\n".format(
                                        c, sent_pos.__getitem__(y)[1], 'I-' + ne_tag)
                                    y += 1

                            else:
                                # if tag belongs to the class of troublesome
                                # tags
                                subseq_tokens = token
                                for c in combo:
                                    subseq_tokens += c
                                subseq_tokens = "{}\t{}\t{}\n".format(subseq_tokens, sent_pos.__getattribute__(i)[1],
                                                                      label)

                        if subseq_tokens:
                            step = combo.__len__() + step
                        else:
                            label = 'O'
                else:
                    # if no tag assigned, check against pattern
                    # or else, assign 'O'
                    label = self.tokenizer_helper.pattern_token(token)
                    label = label if label else 'O'

                file_content += "{}\t{}\t{}\n".format(token, pos, label)
                if subseq_tokens:
                    file_content += subseq_tokens
                i += step

        # write to file: tagged iob data in train data path and text in raw
        # data path
        file_name = self.app_helper.get_file_name(content)
        # save iob annotated file
        self.file_helper.save_file(file_name, file_content)
        # save txt file
        self.file_helper.save_file(file_name, content, False)
