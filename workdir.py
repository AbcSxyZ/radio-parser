import os

class WorkingDirectory:
    """
    Context manager to control a working directory
    """
    def __init__(self, directory):
        if not os.path.exists(directory):
            os.mkdir(directory)

        self.origin = os.getcwd()
        self.workdir = os.path.join(self.origin, directory)

    def __enter__(self):
        os.chdir(self.workdir)
        return self

    def __exit__(self, *args, **kwargs):
        os.chdir(self.origin)

