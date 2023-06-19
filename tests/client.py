from asyncio.subprocess import PIPE
from subprocess import Popen, PIPE


class Client:
    def __init__(self, path, host, port, filename, text=True):
        self.path = str(path)
        self.host = str(host)
        self.port = str(port)
        self.filename = str(filename)
        self.text = text

    def __enter__(self):
        return self.run()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        return self.terminate()

    def run(self):
        self.process = Popen([self.path, self.host, self.port,
                             self.filename], stdout=PIPE, stderr=PIPE, cwd="..", text=self.text, bufsize=0)
        return self.process

    def terminate(self):
        self.process.terminate()

    def get(self):
        return self.process
