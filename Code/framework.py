from Animation import *
from interface import *
import copy

# This class stores information about fields of an object
# including how it is presented in the menu
class psm_field(Object):
    def __init__(self, name, value = 0, 
        value_type = int,
        value_max = None):
        self.name = name
        self.value = value
        self.icon = None

        self.value_type = value_type
        self.value_max = value_max

    def set_value(self, value):
        self.value = value

    def get_value(self, value):
        return self.value

    def set_icon(self, icon):
        self.icon = icon

class psm_object(Object):
    def __init__(self, name, index):
        # A list of all the field names
        # Which are keys to the attributes dictionary
        self.fields = ["NAME", "INDEX"]

        # A dictionary that stores all of the object's attributes
        self.attributes = dict()

        # Whether this object will be rendered in the final presentation
        self.is_visible = True

        self.is_selected = False

    def set_value(self, field, value):
        if field not in self.fields:
            raise Exception("""Field \"" + field + "\" 
does not belong to object!""")
        else:
            self.attributes[field].set_value(value)

    def get_value(self, field):
        if field not in self.fields:
            raise Exception("""Field \"" + field + "\" 
does not belong to object!""")
        else:
            return self.attributes[field].get_value()

    # Returns true if point (x,y) counts as "on" the object
    def mouse_on(self, x, y):
        pass

    def draw(self, canvas, startx, starty):
        pass

    def get_hashables(self):
        return (self.name, self.index)

    def __eq__(self, other):
        if not isinstance(other, psm_object):
            raise Exception("""Comparing an instance of psm_object
with another object""")
        # We might change this if we allow object aliases
        # i.e. two objects that have the same name and index
        return self.name == other.name and self.index == other.index

    def __hash__(self, other):
        return hash(self.get_hashables())

class psm_circle(psm_object):
    def __init__(self, name, index):
        super().__init__(name, index)
        self.fields.extend (["CENTER_X", "CENTER_Y", "RADIUS", 
                             "FILL_COLOR", "BORDER_COLOR",
                             "BORDER_WIDTH"])
        self.init_attributes()

    def init_attributes(self):
        # Only temporary
        # Finally we will have to customize each of the fields
        for i in range(len(self.fields)):
            field_name = self.fields[i]
            self.attributes[field_name] = psm_field(field_name)

    # The x and y should be in the canvas coodrinate system
    def mouse_on(self, x, y):
        center_x = self.get_value("CENTER_X")
        center_y = self.get_value("CENTER_Y")
        radius = self.get_value("RADIUS")
        border = self.get_value("BORDER_WIDTH")
        return ((x - center_x) ** 2 + (y - center_y) ** 2 
               <= (radius + border / 2) ** 2)

    def draw(self, canvas, startx, starty):
        center_x = self.get_value("CENTER_X")
        center_y = self.get_value("CENTER_Y")
        radius = self.get_value("RADIUS")
        x1 = startx + center_x - radius
        x2 = startx + center_x + radius
        # Note the the +y direction on the canvas is up
        # Because it is convinient for a coordinate system 
        y1 = starty - center_y - radius
        y2 = starty - center_y + radius
        canvas.create_oval(x1, y1, x2, y2)

class psm_tool(Object):
    def __init__(self): pass

class slide(Object):
    def __init__(self):
        self.objects = None

    # Render is specific to slides
    # Has a more professional feel
    def render(self, canvas, startx, starty, edit = True):
        for user_object in self.objects:
            if edit or user_object.is_visible:
                user_object.draw(canvas, startx, starty)

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

    def mousePressed(self, event):
        for GUI_object in GUI_objects:
            GUI_object.mouse_down(event.x, event.y)
        if self.mode == "EDIT":
            # Process the mouse down event for user objects
            for user_object in self.current_slide.slides:
                pressed = user_object.mouse_down(event.x, event.y)
                if pressed:
                    # Only one object can be pressed
                    break

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
