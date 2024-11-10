class Addon:
    def __init__(self, id=None):
        self.id = id

    def getAddonInfo(self, key):
        return "mock_value"

    def getSetting(self, key):
        if key == "CacheTTL":
            return "4"
        else:
            return "mock_setting"