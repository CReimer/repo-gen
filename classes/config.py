import json


class Config:
    def __init__(self, filename):

        with open(filename) as data_file:
            data = json.load(data_file)

        try:
            self.skip_directories = data['skip_directories']
        except KeyError:
            self.skip_directories = []
        try:
            self.only_directories = data['only_directories']
        except KeyError:
            self.only_directories = []
        try:
            self.sign = data['sign']
        except KeyError:
            self.sign = False
        try:
            self.arch = data['only_architecture']
        except KeyError:
            self.arch = ['i686', 'x86_64']
        self.reponame = data['repo_name']
        self.check_script = data['check_script']
