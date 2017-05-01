from g4ti.helpers.config_helper import ConfigHelper


class TokenizerHelper:
    def __init__(self):
        self.config_helper = ConfigHelper()

    def pattern_token(self, word):
        pattern_tag = ''
        if self.config_helper.IP_PATTERN.match(word):
            pattern_tag = 'B-IP'
        elif self.config_helper.EMAIL_PATTERN.match(word):
            pattern_tag = 'B-EMAIL'
        elif self.config_helper.REGKEY_PATTERN.match(word):
            pattern_tag = 'B-REGKEY'
        elif self.config_helper.HASH_PATTERN.match(word) and (len(word) % 32 == 0 or len(word) % 40 == 0):
            pattern_tag = 'B-HASH'
        elif self.config_helper.URL_PATTERN.match(word):
            pattern_tag = 'B-URL'
        elif self.config_helper.DOMAIN_PATTERN.match(word):
            pattern_tag = 'B-DOMAIN'
        elif self.config_helper.CVE_PATTERN.match(word):
            pattern_tag = 'B-CVE'
        return pattern_tag

    def get_tags(self, filename):
        text = open(filename).read()
        dic = {}
        lines = text.splitlines()
        for line in lines:
            col = line.split("\t")
            if col[1] != "O":
                dic.__setitem__(col[0], col[1])
        return dic
