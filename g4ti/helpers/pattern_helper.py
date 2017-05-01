import re
import yaml


class PatternHelper:
    def __init__(self):
        self.patterns = []

    def getPatterns(self):
        return self.patterns;

    def load(self):
        with open("conf/patterns.yaml", 'r') as patterns:

            try:
                for item in yaml.load(patterns):
                    item["pattern"] = re.compile(item["pattern"])
                    self.patterns.append(item)
            except yaml.YAMLError as exc:
                print(exc)
                # TODO add logger
