class Channel:
    def __init__(self, key, label):
        self.key = key
        self.label = label

    def __eq__(self, o: object) -> bool:
        return self.key == o.key


class ChannelList:
    def __init__(self):
        pass
