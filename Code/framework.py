from Animation import *
from interface import *
import copy

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

WORKSPACE_SIDES = 1/6
WORKSPACE_BOTTOM = 1/3
WORKSPACE_MARGIN = 1/20

# Bottom left
WORKSPACE_ORIGIN_X = SCREEN_WIDTH * (WORKSPACE_SIDES + WORKSPACE_MARGIN)
WORKSPACE_ORIGIN_Y = SCREEN_HEIGHT * (1 - WORKSPACE_BOTTOM - WORKSPACE_MARGIN)

# Convert global coordinates to coordinates in the workspace
# Just for reference
def global_to_workspace(x, y = None):
    if y == None:
        y = x[1]
        x = x[0]
    return (x - WORKSPACE_ORIGIN_X, WORKSPACE_ORIGIN_Y - y)

# This class stores information about fields of an object
# including how it is presented in the menu
class psm_field(Object):

    ICON_SIZE = 32
    MARGIN = 10
    ICON_BOX_SPACING = 5
    ITEM_SPACING = 15
    BOX_HEIGHT = 40

    # TODO: LARGE input boxes
    BOX_WIDTH = {"NONE": 0,
                 "SMALL": 50,
                 "MEDIUM": 150}


    def __init__(self, name, position = None, parent = None,
        value = 0, 
        value_type = int,
        value_max = None,
        # "NONE" "SMALL" "MEDIUM" "LARGE"
        input_size = "SMALL"):

        self.name = name
        self.value = value
        # We will set the icons of the fields all at once using set_icon()
        self.icon = None

        self.value_type = value_type
        self.value_max = value_max

        # Hidden fields must have a parent
        self.is_hidden = False
        self.children = None
        self.input_size = input_size
        # (row, col)
        self.position = position
        # "BASIC" "COLOR" "DIMENSIONS" and so on
        self.tab = "BASIC"

    def set_value(self, value):
        self.value = value

    def get_value(self, value):
        return self.value

    def set_icon(self, icon):
        self.icon = icon

def insert_field_in_2d_array(array, field, position):
    row, col = position
    if len(array) <= row:
        n = len(array)
        for i in range(n, row + 1):
            array.append([])
    if len(array[row]) <= col:
        n = len(array[row])
        for i in range(n, row + 1):
            array[row].append(None)
    array[row][col] = field        

class psm_menu(psm_GUI_object):

    BG_COLOR_NORMAL = "grey"

    def __init__(self, attributes_dict):
        self.is_visible = False
        self.current_tab = "BASIC"
        self.tabs = dict()
        for field in attributes_dict.values():
            tab = field.tab
            if tab not in self.tabs.keys():
                self.tabs[tab] = []
            if not field.is_hidden:
                pos = field.position
                insert_field_in_2d_array(self.tabs[tab], field, pos)
        # Create the corresponding GUI items for each field
        self.init_items()

    def init_items(self):
        self.panels = dict()
        for tab in self.tabs.keys():
            # An invisible panel to hold all the buttons
            panel = psm_GUI_object(0,0,0,0)
            for row in range(len(self.tabs[tab])):
                for col in range(len(self.tabs[tab][row]))
                    item = self.tabs[tab][row][col]
                    x1, y1 = get_item_topleft_position(row, col)
                    button = psm_menu_icon(x1,
                                           y1,
                                           x1 + psm_field.ICON_SIZE,
                                           y1 + psm_field.ICON_SIZE,
                                           image = item.icon)
                    panel.add_child(button)
            self.panels[tab] = panel

    def get_item_topleft_position(self, row, col):
        row_height = psm_field.MARGIN * 2 + psm_field.ICON_SIZE
        top = row_height * row + psm_field.MARGIN
        left = psm_field.MARGIN
        for i in range(col):
            item = self.tabs[self.current_tab][row][i]
            left += psm_field.ICON_SIZE
            left += psm_field.ICON_BOX_SPACING
            left += psm_field.BOX_WIDTH[item.input_size]
            left += psm_field.ITEM_SPACING
        return left, top

    def get_dimensions(self):
        rows = len(self.tabs[self.current_tab])
        max_width = 0
        for row in range(rows):
            last_col = len(self.tabs[self.current_tab][row])
            # self.tabs[self.current_tab][row][last_col] doesn't exist
            # but it's okay - we're just calculating how wide
            # the menu should be using our item position method
            curr_width, height = self.get_item_topleft_position(row, last_col)
            if max_width < curr_width: max_width = curr_width

        # Since it's the last item in the row
        # there is no item spacing
        max_width += psm_field.MARGIN - psm_field.ITEM_SPACING
        height += psm_field.MARGIN + psm_field.ICON_SIZE

        return max_width, height

    def draw(self, canvas, startx, starty):
        width, height = self.get_dimensions()
        # Create background rectangle
        # Since we might get fancy with the shape, 
        # we will draw it here instead of in gui_rect
        canvas.create_rectangle(startx, 
                                starty,
                                startx + width,
                                starty + height, 
                                fill = psm_menu.BG_COLOR_NORMAL)
        self.panels[self.current_tab].resize_object(startx, starty)
        self.panels[self.current_tab].draw(canvas)
        # TODO: Add input fields!


class psm_object(Object):
    def __init__(self, name, index):
        # A list of all the field names
        # Which are keys to the attributes dictionary
        self.fields = ["NAME", "INDEX"]

        # A dictionary that stores all of the object's attributes
        self.attributes = dict()

        # Whether this object will be rendered in the final presentation
        self.is_visible = True

        self.mouse_on = False
        self.is_selected = False
        self.menu_on = False
        # We'll generate the corresponding menu in the specific classes
        self.menu = None

        self.set_value("NAME", name)
        self.set_value("INDEX", index)

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
    def in_borders(self, x, y):
        pass

    def mouse_down(self, x, y):
        if self.in_borders(x, y):
            self.is_selected = True
            self.menu_on = True
        else:
            self.is_selected = False

    # Useful when we are drag-selecting objects
    def set_selected(self, value):
        self.is_selected = value

    # TODO: Change the draw function so that we can pass in the ratio
    # for drawing miniture slides
    def draw(self, canvas, startx, starty):
        if self.menu_on and self.menu != None:
            self.menu.draw(canvas, startx, starty)

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
    def in_borders(self, x, y):
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

    # The minimum size (width and height) that an object can have
    MIN_ELEM_SIZE = 10

    def __init__(self):
        # True when the mouse is pressed
        self.mouse_pressed = False
        self.current_object = None
        # A tuple (x, y) of position coordinates
        self.drag_start = None

    def mouse_down(self, x, y, object_name):
        if not self.mouse_pressed:
            self.drag_start = (x, y)
            self.mouse_pressed = True
            self.generate_object(object_name)

    def mouse_up(self, x, y):
        self.mouse_pressed = False
        return self.current_object

    def mouse_move(self, x, y):
        if self.mouse_pressed:
            width = x - self.drag_start[0]
            height = y - self.drag_start[1]
            width = max(width, psm_tool.MIN_ELEM_SIZE)
            height = max(height, psm_tool.MIN_ELEM_SIZE)
            self.resize_object(width, height)

    def generate_object(self):
        pass

    def resize_object(self, width, height):
        pass

    def draw_object(self, canvas):
        self.current_object.draw(canvas)

class psm_circle_tool(psm_tool):

    MIN_RADIUS = 5

    def __init__(self):
        super().__init__()

    def generate_object(self, object_name):
        x, y = global_to_workspace(self.drag_start)
        self.current_object = psm_circle(object_name, 0)
        self.current_object.set_value("CENTER_X", x)
        self.current_object.set_value("CENTER_Y", y)
        self.current_object.set_value("RADIUS", psm_circle_tool.MIN_RADIUS)

    def resize_object(self, dx, dy):
        r = (dx ** 2 + dy ** 2) ** 0.5
        self.current_object.set_value("RADIUS", r)


class slide(Object):
    def __init__(self):
        self.objects = []

    def add_object(self, user_object):
        self.objects.append(user_object)

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

        # We might not need this -- we can just let objects draw their own menus
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
