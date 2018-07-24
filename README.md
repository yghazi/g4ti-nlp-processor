# g4ti-nlp-processor
This is the back-end of an annotation tool that allows you to annotate text documents with threat intelligence vocabulary, which is saved into a dataset. This dataset is later used to train an NER model which tags documents to extract high-level threat intelligence indicators like Actor, Targeted Application, Targeted Location, TTPs, etc.

## Configuration #

### Clone git repo ###
Repo for front-end:
```
git clone https://github.com/yghazi/g4ti-tator.git
```
Clone this repo:
```
git clone https://github.com/yghazi/g4ti-nlp-processor.git
```
### Requirements
- Python 3.X

For Windows, you will also need the following:
- .NET framework
- Visual Studio build tools

### To install dependencies execute the below command ###

```
#!python

cd g4ti-nlp-processor # navigate to the g4ti-nlp-processor folder

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

If your front-end is also running, you should be able to now use the nlp processor through your browser.
