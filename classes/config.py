import json
import platform


class Config:
    def __init__(self, filename):

        x86 = ['i686', 'x86_64']
        arm = ['arm', 'armv6h', 'armv7h', 'armv8h']

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
            temp_var = data['only_architecture']
            if isinstance(temp_var, list):
                self.arch = temp_var
            else:
                self.arch = [temp_var]
        except KeyError:
            if platform.machine() in x86:
                index = x86.index(platform.machine())
                self.arch = x86[:index+1]
            elif platform.machine() in arm:
                index = arm.index(platform.machine())
                self.arch = arm[:index+1]
            else:
                exit()

        self.reponame = data['repo_name']
        #self.check_script = data['check_script']
