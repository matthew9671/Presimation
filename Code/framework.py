class psm_object(Object):
    def __init__(self):
        self.attributes = None
        self.name = None

    def setValue(self, field, value):
        pass

    def draw(self, canvas):
        pass

    def gethashables(self):
        return 42

    def __eq__(self, other):
        pass

    def __hash__(self, other):
        pass

class snapshot(Object):
    def __init__(self):
        self.objects = None

    def render(self, canvas):
        pass

class Presimation(Animation):
    def __init__(Object):
        # "EDIT" "PLAYBACK"
        self.mode = "EDIT"