# g4ti-nlp-processor
This is the back-end of an annotation tool that allows you to annotate text documents with threat intelligence vocabulary, which is saved into a dataset. This dataset is later used to train an NER model which tags documents to extract high-level threat intelligence indicators like Actor, Targeted Application, Targeted Location, TTPs, etc.

## Configuration #

### Clone git repo ###
```
git clone https://github.com/yghazi/g4ti-tator.git
```
### Setup
We assume you have installed python 3.x and its in path as well.

### To install dependencies execute the below command ###

```
#!python

pip install -r requirements.txt

```

### To download nltk models in use: ###

```
#!python

python -m nltk.downloader punkt
python -m nltk.downloader averaged_perceptron_tagger
```
### To run server, execute the following command: ###
```
#!python

python tator.py
```
