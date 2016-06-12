from Animation import *
from interface import *

class psm_object(Object):
    def __init__(self):
        self.attributes = None
        self.name = None

    def setValue(self, field, value):
        pass

    def draw(self, canvas, startx, starty):
        pass

    def gethashables(self):
        return 42

    def __eq__(self, other):
        pass

    def __hash__(self, other):
        pass

class slide(Object):
    def __init__(self):
        self.objects = None

    # Render is specific to slides
    # Has a more professional feel
    def render(self, canvas, startx, starty):
        pass

class Presimation(Animation):
    def __init__(self):
        # The list of GUI objects including the toolbar and the timeline
        self.GUI_objects = []
        self.init_GUI()

        # The list of menus currently opened
        self.menus = []
        
        # The list of slides created
        self.slides = []

        # The index of the current slide
        self.current_slide = 0

        # TODO: Add a list of tools
        self.current_tool = None

        # "EDIT" "PLAYBACK"
        self.mode = "EDIT"

    def init_GUI(self):
        # TODO: Add values to these parameters
        self.canvas_start_x = None
        self.canvas_start_y = None

    def mousePressed(self, event): pass
    def keyPressed(self, event): pass
    def keyReleased(self,event):pass
    def leftMouseReleased(self,event):pass
    def mouseMotion(self,event):pass
    def timerFired(self): pass
    def redrawAll(self):
        # Draw GUI
        for GUI_object in self.GUI_objects:
            GUI_object.draw(self.canvas)

        # Draw workspace
        self.slides[self.current_slide].render(
            self.canvas,
            self.canvas_start_x,
            self.canvas_start_y)
