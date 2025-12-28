class SessionMemory:
    def __init__(self):
        self.history = []

    def add(self, data):
        self.history.append(data)

    def get(self):
        return self.history
