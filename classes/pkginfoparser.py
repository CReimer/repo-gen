import tarfile


class PkginfoParser:
    def __init__(self, filename):
        self.values = {}

        with tarfile.open(filename) as tf:
            fileobj = tf.extractfile('.PKGINFO')
            for line in fileobj:
                try:
                    key = line.decode().split('= ')[0].rstrip()
                    value = line.decode().split('= ')[1].rstrip()
                    try:
                        self.values[key].append(value)
                    except KeyError:
                        self.values[key] = []
                        self.values[key].append(value)
                except IndexError:
                    continue
