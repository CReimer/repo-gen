import json


class Config:
    def __init__(self, filename):

        with open(filename) as data_file:
            data = json.load(data_file)

        self.skip_directories = data['skip_directories']
        self.reponame = data['repo_name']
