class Game:
    def __init__(self, sio=None):
        super().__init__()
        if sio is not None:
            self.sio = sio

    def do_stuff(self, param):
        return param + 5
