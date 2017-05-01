from nltk.corpus.reader import ConllChunkCorpusReader, pickle

from g4ti.helpers.config_helper import ConfigHelper
from g4ti.nlp import custom_trainer


class Training:
    def __int__(self):
        self.config_helper = ConfigHelper()

    def get_training_samples(self):
        """
        Get training samples
        :return:
        """
        _reader = ConllChunkCorpusReader(self.config_helper.TRAIN_DATA_PATH, r'.*\.tsv$', chunk_types='LP')
        l = []
        for x in _reader.iob_sents():
            y = []
            for w, t, ne in list(x):
                y.append(((w, t), ne))
            l.append(y)
        return l

    def train_and_pickle(self):
        """
        Train model on provided corpus and save serialized corpus as pickle
        :return:
        """
        # TODO: change to crf training.. might want to change features and lemmatize before training
        samples = self.get_training_samples()
        chunker = custom_trainer.NamedEntityChunker(samples)
        chunker_pickle = open(self.config_helper.TRAIN_MODEL_PICKLE, 'wb')
        pickle.dump(chunker, chunker_pickle)
        chunker_pickle.close()
