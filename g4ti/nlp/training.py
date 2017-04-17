from nltk.corpus.reader import ConllChunkCorpusReader, pickle

from g4ti import constants
from g4ti.nlp import custom_trainer


class Training:
    TRAIN_DATA_PATH = constants.G4TI_TRAINING_DIR
    TRAIN_MODEL_PICKLE = constants.TRAIN_MODEL

    def __int__(self):
        print("")

    def get_training_samples(self):
        """
        Get training samples
        :return:
        """
        _reader = ConllChunkCorpusReader(self.TRAIN_DATA_PATH, r'.*\.tsv$', chunk_types='LP')
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
        chunker_pickle = open(self.TRAIN_MODEL_PICKLE, 'wb')
        pickle.dump(chunker, chunker_pickle)
        chunker_pickle.close()
