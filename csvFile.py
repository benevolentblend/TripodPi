class csvFile:

    """
    Holds and manges the file data
    """

    def __init__(self, fn):
        self.filename = fn
        self.file = None
        self.opened = False
        self.closed = False

    def open(self):
        if self.opened:
            raise Exception('Can not open file, file already opened. "{}"'.format(self.filename))
            return
        self.file = open(self.filename, 'w')
        self.opened = True

    def write(self, content):
        if not self.opened:
            raise Exception('Can not write to file, file not opened. "{}"'.format(self.filename))
            return
        if self.closed:
            raise Exception('Can not write to file, file already closed. "{}"'.format(self.filename))
            return

        self.file.write(content)

    def close(self):
        if not self.opened:
            raise Exception('Can not close file, file not opened. "%s"'.format(self.filename))
            return
        if self.closed:
            raise Exception('Can not close file, file already closed. "%s"'.format(self.filename))
            return

        self.file.close()

        self.closed = True
