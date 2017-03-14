# Configuration #

We assume you have installed python 3.x and it's configured in your bin path as well.

### To install dependencies execute the following command, where you might want to provide the path to the project's `requirements.txt` file: ###

```
#!python

pip install -r /path/to/requirements.txt

```
### To download data dependencies for NLTK, run the commands below:  ###

```
#!python

python -m nltk.downloader punkt
```


```
#!python

python -m nltk.downloader averaged_perceptron_tagger
```

### To run the server, execute the command: ###
```
#!python

python /path/to/g4ti-nlp-processor/api/tator.py
```