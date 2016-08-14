from Animation import *
from interface import *
import copy
import math
import string

import os

# From-- *drum roll* STACKOVERFLOW!
# http://stackoverflow.com/questions/4060221/how-to-reliably-open-a-file-in-the-same-directory-as-a-python-script
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

##############################
# Global GUI layout constants
##############################

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600

WORKSPACE_SIDES_R = 1/6
TOOLBAR_WIDTH = SCREEN_WIDTH * WORKSPACE_SIDES_R

# This ratio is pretty important
# Width/height
CANVAS_RATIO = 4/3
CANVAS_TO_SLIDE = 1/3

# I moved these to the top level for convenience
# independent ratio and size
WORKSPACE_WIDTH_R = 1 - WORKSPACE_SIDES_R * 2  # width of the workspace
WORKSPACE_HEIGHT_R = 3/4
TMLINE_HEIGHT_R = 1 - WORKSPACE_HEIGHT_R # ratio of height of the timeline
TMLINE_HEIGHT = SCREEN_HEIGHT * TMLINE_HEIGHT_R
TMLINE_MARGIN_W = 5
TMLINE_MARGIN_H = 5

WORKSPACE_LEFT = SCREEN_WIDTH * WORKSPACE_SIDES_R
WORKSPACE_RIGHT = SCREEN_WIDTH - WORKSPACE_LEFT
WORKSPACE_TOP = 0
WORKSPACE_BOTTOM = SCREEN_HEIGHT * (1 - TMLINE_HEIGHT_R)

# Canvas dimensions
CANVAS_MARGIN_HORIZONTAL = 1/20 * SCREEN_WIDTH
CANVAS_WIDTH = SCREEN_WIDTH * (WORKSPACE_WIDTH_R) - 2 * CANVAS_MARGIN_HORIZONTAL
CANVAS_HEIGHT = CANVAS_WIDTH / CANVAS_RATIO
# Vertical margin is calculated according to canvas_ratio
CANVAS_MARGIN_VERTICAL = (WORKSPACE_HEIGHT_R * SCREEN_HEIGHT 
    - CANVAS_HEIGHT) / 2

# Origin = Bottom left
# In global coordinates
CANVAS_ORIGIN_X = SCREEN_WIDTH * WORKSPACE_SIDES_R + CANVAS_MARGIN_HORIZONTAL
CANVAS_ORIGIN_Y = (SCREEN_HEIGHT * WORKSPACE_HEIGHT_R - CANVAS_MARGIN_VERTICAL)

# Users can always see 1/4 of the rest snapshots
TMLINE_UNCOVER = 0.25

############################
# Global helper functions
############################

# A function that packs and returns lambda functions
def get_lambda(func, *args):
    return lambda: func(*args)

def test_func(a, b):
    print(a, b)

def is_num_type(number):
    try:
        result = int(number)
        return True
    except:
        return False

f = get_lambda(test_func, 1, 2)
#f()

# Convert global coordinates to coordinates in the workspace
# Just for reference
def global_to_canvas(x, y = None):
    if y == None:
        y = x[1]
        x = x[0]
    return (x - CANVAS_ORIGIN_X, CANVAS_ORIGIN_Y - y)

def canvas_to_global(x, y = None):
    if y == None:
        y = x[1]
        x = x[0]
    return (x + CANVAS_ORIGIN_X, CANVAS_ORIGIN_Y - y)

# colors
lightGrey = rgbString(200,200,200)
offWhite = rgbString(250, 250, 235)

def double_click_debug(): print("Registered double click!")

def insert_field_in_2d_array(array, field, position):
    row, col = position
    if len(array) <= row:
        n = len(array)
        for i in range(n, row + 1):
            array.append([])
    if len(array[row]) <= col:
        n = len(array[row])
        for i in range(n, col + 1):
            array[row].append(None)
    array[row][col] = field        

# This class stores information about fields of an object
# including how it is presented in the menu
class psm_field(object):

    ICON_SIZE = 32
    MARGIN = 10
    ICON_BOX_SPACING = 5
    ITEM_SPACING = 15
    BOX_HEIGHT = 30

    # TODO: LARGE input boxes
    BOX_WIDTH = {"NONE": 0,
                 "SMALL": 50,
                 "MEDIUM": 150}


    def __init__(self, name, master, position = None, parent = None,
        value = 0, 
        value_type = float,
        value_max = 10000,
        value_min = 0,
        # "NONE" "SMALL" "MEDIUM" "LARGE"
        input_size = "SMALL"):

        self.name = name
        # The real value of the field
        self.value = value
        # The value shown
        self.expression = str(value)
        # If this field is False the value depends on other things
        self.is_independent = True
        # Type<psm_object>
        self.master = master

        test_img_file = os.path.join(__location__, "../Images/name_icon.gif")
        test_icon = PhotoImage(file = test_img_file)
        # We will set the icons of the fields all at once using set_icon()
        self.icon = test_icon

        self.button = None
        self.inputbox = None

        self.value_type = value_type
        self.value_max = value_max
        self.value_min = value_min

        # Hidden fields must have a parent
        self.is_hidden = False
        self.children = None
        self.input_size = input_size
        # (row, col)
        self.position = position
        # "BASIC" "COLOR" "DIMENSIONS" and so on
        self.tab = "BASIC"

    @classmethod
    # A linear interpolation
    # Returns a value instead of a psm_field object
    def interpolate_value(self, from_field, to_field, ratio):
        assert(from_field.value_type == to_field.value_type)
        if from_field.value_type not in [float, int]:
            return from_field.get_value()
        else:
            from_value = from_field.get_value()
            to_value = to_field.get_value()
            return from_value + ratio * (to_value - from_value)

    # Checks if the value is matches the correct type
    # If it is, convert the value to the type
    # For example "1" matches int type
    def type_check(self, value):
        # From stackoverflow
        # Lol
        try:
            result = self.value_type(value)
            return result, True
        except:
            return None, False

    # Attempt to set the value of the field
    # If it fails, returns false to the caller
    def set_value(self, value, update_inputbox = True):
        # You cannot set the value directly when it depends on something else
        if not self.is_independent and update_inputbox: 
            print("Field", self.name, "is not independent!")
            return False

        # Many times the value is in string format
        value, passed = self.type_check(value)
        # The value is not of the correct type
        if not passed: 
            print(value, ": Typecheck failed! Should be ", self.value_type)
            return False

        if (type(value) not in [float, int] 
            or (value <= self.value_max 
                and value >= self.value_min)):
            # print("Value of", self.name, "field set to", value)
            self.value = value
            if self.is_independent: self.expression = str(value)
        else:
            print(value, ": Range check failed! Max:%d, Min:%d"
             % (self.value_max, self.value_min))
            # The value inputted is invalid
            return False

        if self.inputbox != None and update_inputbox:
            self.master.update_fields()
            self.inputbox.update_value()
        # Successfully set value
        return True

    def get_value(self):
        return self.value

    def update(self):
        if not self.is_independent: self.set_expression(self.expression)

    # Input boxes set the expression first
    # Then the expression gets evaluated
    # And this method calls set_value
    def set_expression(self, expr, update_fields = False):
        #print("Set_expression called on", self.name, "field!")
        assert (type(expr) == str)
        self.expression = expr

        # Strings are easy to handle
        if self.value_type == str: 
            self.set_value(expr, update_inputbox = False)
            return True

        result = self.master.slide.evaluate(expr, self.master)
        if result != None:
            if is_num_type(expr):
                print(expr)
                print("Field", self.name, "becomes independent!")
                # If it's just a number the field is independent
                self.is_independent = True
            else:
                self.is_independent = False

            self.set_value(result, update_inputbox = False)

            if update_fields: self.master.update_fields()

            return True
        else:
            print("Expression:", expr)
            print("Error evaluating expression in field ", self.name)
            return False

    def get_expression(self):
        return self.expression

    def set_icon(self, icon):
        self.icon = icon

class psm_menu(psm_GUI_object):

    # Light orange
    BG_COLOR_NORMAL = rgbString(237, 171, 113)

    def __init__(self, attributes_dict):
        self.is_visible = False
        self.current_tab = "BASIC"
        self.attributes = attributes_dict
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
                for col in range(len(self.tabs[tab][row])):
                    # Type <psm_field>
                    item = self.tabs[tab][row][col]
                    x1, y1 = self.get_item_topleft_position(row, col)
                    # TODO: I guess we can put more of this into the class
                    item.button = psm_menu_icon(x1,
                                           y1,
                                           x1 + psm_field.ICON_SIZE,
                                           y1 + psm_field.ICON_SIZE,
                                           image = item.icon,
                                           color = None,
                                           parent = panel,
                                           border = 0)
                    item.inputbox = psm_menu_inputbox(x1 + psm_field.ICON_SIZE+\
                                    psm_field.ICON_BOX_SPACING,
                                    y1,
                                    x1 + psm_field.ICON_SIZE +\
                                    psm_field.ICON_BOX_SPACING +\
                                    psm_field.BOX_WIDTH["SMALL"],
                                    y1 + psm_field.BOX_HEIGHT,
                                    field = item,
                                    entry_update_func = self.entry_update,
                                    color = None,
                                    border = 0,
                                    parent = panel)
            self.panels[tab] = panel

    @classmethod
    def copy(self, instance):
        return copy.copy(instance)

    def entry_update(self, sv, field_name, active_change):
        #print(active_change)
        if not active_change: 
            return
        field = self.attributes[field_name]
        success = field.set_expression(sv.get(), update_fields = True)
        # If the value enter is not valid
        # The inputbox will be notified
        field.inputbox.set_error(not success)

    def hide_inputbox(self):
        c_tab = self.current_tab
        for row in range(len(self.tabs[c_tab])):
            for col in range(len(self.tabs[c_tab][row])):
                self.tabs[c_tab][row][col].inputbox.hide()

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
                                fill = psm_menu.BG_COLOR_NORMAL,
                                width = 0)
        self.panels[self.current_tab].resize(startx, starty)
        # Icon buttons and inputboxes are children of the panel
        self.panels[self.current_tab].draw(canvas)

# The master class of all user-created objects
class psm_object(object):

    select_color = "orange"

    def __init__(self, name, slide):
        # The slide that the object lives in
        self.slide = slide
        # A list of all the field names
        # Which are keys to the attributes dictionary
        self.fields = ["NAME", "INDEX"]

        # A dictionary that stores all of the object's attributes
        # dict<string, psm_field>
        self.attributes = dict()

        # Whether this object will be rendered in the final presentation
        self.is_visible = True

        self.dbclick_listener = psm_double_click_listener(self.toggle_menu)
        self.mouse_on = False
        self.is_selected = False
        self.menu_on = False
        # We'll generate the corresponding menu in the specific classes
        self.menu = None

        # TODO: These can be further specified
        name_field = psm_field("NAME", self, position = [0,0], 
            value = name, value_type = str)
        index_field = psm_field("INDEX", self, position = [0,1])
        self.attributes["NAME"] = name_field
        self.attributes["INDEX"] = index_field
        # Generate the handles(control points)(type: psm_button)
        # for the user to manipulate the object
        self.handle_holder = psm_GUI_object(0,0,0,0)
        self.handles = None

    @classmethod
    def copy(self, instance, master = None):
        if master == None: master = instance.slide
        # First make a copy with some aliasing
        result = copy.copy(instance)
        result.fields = copy.copy(instance.fields)
        result.attributes = dict()
        for key in instance.attributes.keys():
            field = copy.copy(instance.attributes[key])
            # Change the field's master
            field.master = result
            result.attributes[key] = field
        # This might require fixing
        result.handle_holder = psm_GUI_object(0,0,0,0)
        result.generate_handles()
        result.menu = psm_menu(result.attributes)
        result.dbclick_listener = psm_double_click_listener(result.toggle_menu)
        result.master = master
        return result

    @classmethod
    # Returns a psm_object that is in between of two objects
    # This interpolation is linear
    def interpolate(self, from_object, to_object, ratio):
        result = psm_object.copy(from_object, from_object.master)
        for name in result.fields:
            from_field = from_object.attributes[name]
            to_field = to_object.attributes[name]
            value = psm_field.interpolate_value(from_field, to_field, ratio)
            result.set_value(name, value)
        return result

    def toggle_menu(self):
        #print("Menu on!")
        self.menu_on = True
        self.menu.is_visible = True

    def update_fields(self):
        for field in self.fields:
            self.attributes[field].update()

    def generate_handles(self): pass

    def update_handles(self):
        if self.handles == None:
            self.generate_handles()

    def set_value(self, field, value):
        if field not in self.fields:
            raise Exception(
                """Field \"" + field + "\" does not belong to object!""")
        else:
            self.attributes[field].set_value(value)

    def get_value(self, field):
        if field not in self.fields:
            raise Exception(
            """Field \"" + field + "\" does not belong to object!""")
        else:
            return self.attributes[field].get_value()

    # Returns true if point (x,y) counts as "on" the object
    def in_borders(self, x, y): pass

    def get_menu_position(self): pass

    def on_mouse_down(self, x, y):
        # The mainloop calls mouse_down
        # only when the object is being clicked upon
        self.dbclick_listener.on_mouse_down(x, y)
        assert(self.in_borders(x, y))
        if self.is_selected:
            # Pass the mouse_down event to the object's children
            # Namely the handles
            self.handle_holder.on_mouse_down(x, y)
        else:
            self.is_selected = True

    def on_mouse_up(self, x, y):
        self.handle_holder.on_mouse_up(x, y)
        self.dbclick_listener.on_mouse_up(x, y)

    def update(self):
        self.dbclick_listener.update()

    # Useful when we are drag-selecting objects
    def set_selected(self, value):
        self.is_selected = value
        if value == False: 
            #print("Menu off")
            self.menu_on = False
            self.menu.is_visible = False
            self.menu.hide_inputbox()

    # Pass in the ratio for drawing miniture slides
    def draw(self, canvas, startx, starty, ratio = 1):
        if ratio == 1 and self.is_selected:
            # We are not displaying a thumbnail
            if self.handles == None: self.generate_handles()
            self.handle_holder.draw(canvas)
        # We don't want to display the menu in the thumbnail
        if self.menu_on and self.menu != None and ratio == 1:
            x, y = self.get_menu_position()
            self.menu.draw(canvas, x, y)

    def get_hashables(self):
        return (self.name, self.index)

    def __eq__(self, other):
        if other == None: return False
        if not isinstance(other, psm_object):
            raise Exception(
                """Comparing an instance of psm_object with another object""")
        # We might change this if we allow object aliases
        # i.e. two objects that have the same name and index
        return self.name == other.name and self.index == other.index

    def __hash__(self, other):
        return hash(self.get_hashables())

class psm_circle(psm_object):

    SELECTED_EXTRA_WIDTH = 8

    def __init__(self, name, slide):
        super().__init__(name, slide)
        self.fields.extend (["CENTER_X", "CENTER_Y", "RADIUS", 
                             "FILL_COLOR", "BORDER_COLOR",
                             "BORDER_WIDTH"])
        self.init_attributes()

    def init_attributes(self):
        # Only temporary
        # Finally we will have to customize each of the fields
        fields_per_row = 3
        # Start with 2 since name and index are always the first 2
        for i in range(2, len(self.fields)):
            field_name = self.fields[i]
            position = [i // fields_per_row,
                        i % fields_per_row]
            if field_name in ["FILL_COLOR", "BORDER_COLOR"]:
                value_type = str
            else:
                value_type = int
            self.attributes[field_name] = psm_field(field_name, self,
                                                    position = position, 
                                                    value_type = value_type)
        self.menu = psm_menu(self.attributes)

    # The x and y should be in the canvas coodrinate system
    def in_borders(self, x, y):
        x, y = global_to_canvas(x, y)
        center_x = self.get_value("CENTER_X")
        center_y = self.get_value("CENTER_Y")
        radius = self.get_value("RADIUS")
        border = self.get_value("BORDER_WIDTH")
        return ((x - center_x) ** 2 + (y - center_y) ** 2 
               <= (radius + border / 2) ** 2)

    def change_center(self, x, y):
        x, y = global_to_canvas(x, y)
        self.set_value("CENTER_X", x)
        self.set_value("CENTER_Y", y)
        self.update_handles()

    def change_radius(self, x, y):
        x, y = global_to_canvas(x, y)
        center_x = self.get_value("CENTER_X")
        center_y = self.get_value("CENTER_Y")

        r = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
        self.set_value("RADIUS", r)
        self.update_handles()

    def generate_handles(self):
        r = self.get_value("RADIUS")

        center_handle = psm_object_handle(0, 0, 
            return_func = self.change_center,
            parent = self.handle_holder)
        rim_handle = psm_object_handle(-r, 0,
            return_func = self.change_radius,
            parent = self.handle_holder)
        print("Holder:", self.handle_holder.get_center())
        print("Rim:", rim_handle.get_center())
        self.handles = [center_handle, rim_handle]

    def update_handles(self, dx = None, dy = None):
        if self.handles == None:
            self.generate_handles()

        x = self.get_value("CENTER_X")
        y = self.get_value("CENTER_Y")
        x, y = canvas_to_global(x, y)
        self.handle_holder.resize(x, y)

        rim_handle = self.handles[1]

        if dx == None:
            global_x, global_y = rim_handle.get_center()
            holder_x, holder_y = self.handle_holder.get_center()
            x, y = global_x - holder_x, global_y - holder_y
            prev_r = (x ** 2 + y ** 2) ** 0.5
            if prev_r == 0: print(global_x, global_y, dx, dy)
            assert(prev_r != 0)
        else:
            prev_r = (dx ** 2 + dy ** 2) ** 0.5
            x, y = dx, dy
            if prev_r == 0: return

        curr_r = self.get_value("RADIUS")
        new_x = x * curr_r / prev_r
        new_y = - y * curr_r / prev_r
        rim_handle.move_to(new_x, new_y)

    def get_menu_position(self):
        x, y = self.get_value("CENTER_X"), self.get_value("CENTER_Y")
        return canvas_to_global(x, y)

    def on_mouse_move(self, x, y):
        self.handle_holder.on_mouse_move(x, y)
        x, y = global_to_canvas(x, y)
        center_x = self.get_value("CENTER_X")
        center_y = self.get_value("CENTER_Y")
        self.update_handles(x - center_x, y - center_y)

    def on_mouse_down(self, x, y):
        super().on_mouse_down(x, y)
        #print("Object %s Selected" % self.get_value("NAME"))

    def draw(self, canvas, startx, starty, ratio = 1):
        center_x = self.get_value("CENTER_X")
        center_y = self.get_value("CENTER_Y")
        radius = self.get_value("RADIUS")
        fill_color = self.get_value("FILL_COLOR")
        border_color = self.get_value("BORDER_COLOR")
        border_width = self.get_value("BORDER_WIDTH")

        x1 = startx + (center_x - radius) * ratio
        x2 = startx + (center_x + radius) * ratio
        # Note the the +y direction on the canvas is up
        # Because it is convinient for a coordinate system 
        y1 = starty - (center_y + radius) * ratio
        y2 = starty - (center_y - radius) * ratio

        if self.is_selected and ratio == 1:
            selected_width = border_width + psm_circle.SELECTED_EXTRA_WIDTH
            canvas.create_oval(x1, y1, x2, y2, fill = fill_color, 
                                           width = selected_width, 
                                           outline = psm_object.select_color)
        # Draw the circle itself
        canvas.create_oval(x1, y1, x2, y2, fill = fill_color, 
                                           width = border_width, 
                                           outline = border_color)
        # Draw handles and the pop-up menu
        super().draw(canvas, startx, starty, ratio)

# TODO: WRITE ALL OF THESE!!!

class psm_rect(psm_object): pass

# Selection and timer?
class psm_object_abstract(psm_object):

    SIZE = 20

    def __init__(self, name, img):
        super.__init__(name)
        self.img = img

    def draw(self, canvas, startx, starty, ratio = 1):
        if ratio == 1:

            canvas.create_image(x, y, image = self.image)

class psm_selection(psm_object_abstract):
    def __init__(self, name):
        super().__init__(name, 0)
        self.fields.extend (["CENTER_X", "CENTER_Y", 
            "TARGET_NAME", "START_INDEX", "END_INDEX"])
        self.init_attributes()

    def init_attributes(self): pass

class psm_timer(psm_object_abstract): pass

# Tools respond to mouse events and creates corresponding objects
# and returns them to the mainloop
class psm_tool(object):

    # The minimum size (width and height) that an object can have
    MIN_ELEM_SIZE = 10

    def __init__(self, tool_name, object_name):
        # True when the mouse is pressed
        self.mouse_pressed = False
        self.current_object = None
        # A list (x, y) of position coordinates
        # Canvas coordinates
        self.drag_start = None
        self.tool_name = tool_name
        self.object_name = object_name

    def __eq__(self, other):
        if other == None: return False
        if not isinstance(other, psm_tool): 
            raise Exception(
                "Comparing an instance of psm_tool with another object")
        return self.tool_name == other.tool_name

    @classmethod
    def in_workspace(self, x, y):
        return (x > WORKSPACE_LEFT 
            and x < WORKSPACE_RIGHT
            and y > WORKSPACE_TOP
            and y < WORKSPACE_BOTTOM)

    def on_mouse_down(self, x, y, object_name, slide = None):
        if not psm_tool.in_workspace(x, y): return
        x, y = global_to_canvas(x, y)
        if not self.mouse_pressed:
            self.drag_start = (x, y)
            self.mouse_pressed = True
            self.generate_object(object_name, slide)

    def on_mouse_up(self, x, y):
        self.mouse_pressed = False
        # Pass the "ownership" of the object being generated
        # from itself to the main loop
        current_object = self.current_object
        self.current_object = None
        return current_object

    # This is in global coordinates!
    def on_mouse_move(self, x, y):
        x, y = global_to_canvas(x, y)
        if self.mouse_pressed:
            width = x - self.drag_start[0]
            height = y - self.drag_start[1]
            if width >= 0:
                width = max(width, psm_tool.MIN_ELEM_SIZE)
            else:
                width = min(width, -psm_tool.MIN_ELEM_SIZE)
            if height >= 0: 
                height = max(height, psm_tool.MIN_ELEM_SIZE)
            else:
                height = min(height, -psm_tool.MIN_ELEM_SIZE)
            self.resize_object(width, height)

    def generate_object(self, object_name, slide):
        pass

    def resize_object(self, width, height):
        pass

    def draw_object(self, canvas):
        if self.current_object != None:
            self.current_object.draw(canvas, CANVAS_ORIGIN_X, 
                                             CANVAS_ORIGIN_Y)

    def get_object_name(self):
        return self.object_name

# TODO: Change this name
SELECTION_TOOL = psm_tool("Selection tool", None)

class psm_copy_tool(psm_tool):

    def __init__(self):
        super().__init__("Copy tool", None)

    def reset(self):
        print("RESET!")
        # lol
        self.on_mouse_up(0, 0)

    # This time we're passing in a copy of an object
    # Technically speaking the copying is done in the mainloop 
    # instead of in the tool itself
    def on_mouse_down(self, x, y, obj):
        super().on_mouse_down(x, y, None)
        if obj != None:
            print("Copied object!")
            self.current_object = obj
            object_x = obj.get_value("CENTER_X")
            object_y = obj.get_value("CENTER_Y")
            self.original_pos = (object_x, object_y)

    def resize_object(self, dx, dy):
        # We're assuming that every object has the "CENTER" fields
        x = self.original_pos[0] + dx
        y = self.original_pos[1] + dy
        self.current_object.set_value("CENTER_X", x)
        self.current_object.set_value("CENTER_Y", y)

# Copy tool is activated with "D"
# and it's not on the toolbar, so we're defining it globally
COPY_TOOL = psm_copy_tool()

class psm_circle_tool(psm_tool):

    MIN_RADIUS = 5

    def __init__(self):
        super().__init__(tool_name = "Circle tool", object_name = "Circle")
        self.default_values = {
            "FILL_COLOR": "white",
            "BORDER_COLOR": "black",
            "BORDER_WIDTH": 3
        }

    def generate_object(self, object_name, slide):
        x, y = self.drag_start[0], self.drag_start[1]
        self.current_object = psm_circle(object_name, slide)
        self.current_object.set_value("CENTER_X", x)
        self.current_object.set_value("CENTER_Y", y)
        self.current_object.set_value("RADIUS", psm_circle_tool.MIN_RADIUS)
        self.current_object.update_handles()
        for field_name in self.default_values:
            self.current_object.set_value(field_name,
                                          self.default_values[field_name])

    def resize_object(self, dx, dy):
        r = (dx ** 2 + dy ** 2) ** 0.5
        self.current_object.set_value("RADIUS", r)
        self.current_object.update_handles()

class psm_selection_tool(psm_tool):
    def __init__(self):
        super().__init__(tool_name = "Selection tool", 
            object_name = "Selection")

# A slide is a set of user objects
# It holds methods like generate_name 
# which finds an appropriate name for a new object in the slide
class slide(object):

    OPERATORS = ["+", "-", "*", "/", "^", "%"]
    OPERATOR_PRIORITIES = [["^"],
                           ["*", "/", "%"],
                           ["+", "-"]]

    def __init__(self):
        # Debug only
        # self.test_eval()

        self.objects = []
        self.object_dict = dict()

    def test_eval(self):
        print("Testing Parse()...")
        print(self.parse("1+2+3+4"))
        print(self.parse("1+2*3+4"))
        print(self.parse("(1+2)*(3+4)"))
        print(self.parse("(1+(2+3)*(4))"))
        print("Testing Evaluate()...")
        print("1+2+3+4=", end = "")
        print(self.evaluate("1+2+3+4", None))
        print("(1+(2+3)*(4))=", end = "")
        print(self.evaluate("(1+(2+3)*(4))", None))
        print(self.evaluate("0", None))

    @classmethod
    def copy(self, instance):
        result = slide()
        for obj in instance.objects:
            obj_copy = psm_object.copy(obj, result)
            result.add_object(obj_copy)
            print(obj.get_value("NAME"))
        return result

    @classmethod
    def interpolate(self, from_slide, to_slide, ratio):
        result = slide()
        for name in from_slide.object_dict.keys():
            n = len(from_slide.object_dict[name])
            for i in range(n):
                from_object = from_slide.object_dict[name][i]
                to_object = to_slide.object_dict[name][i]
                # This ratio we pass on might change
                # Depending on which interpolation mode we're using
                # right now it's just linear
                obj = psm_object.interpolate(from_object, to_object, ratio)
                result.add_object(obj)
        return result

    def add_object(self, user_object):
        self.objects.append(user_object)
        name = user_object.get_value("NAME")
        if name in self.object_dict:
            # We're adding a copy of an existing object
            user_object.set_value("INDEX", 
                int(len(self.object_dict[name])))
            self.object_dict[name].append(user_object)
        else:
            self.object_dict[name] = [user_object]

    # Returns an object name that is unique in the slide
    def generate_object_name(self, name):
        temp_name = name
        index = 1
        while temp_name in self.object_dict.keys():
            # Add a number after the object's name
            temp_name = "%s%d" % (name, index)
            index += 1
        return temp_name

    def update(self):
        for obj in self.objects:
            obj.update()

    # One of the most important methods
    # Evaluates an expression in the context of the slide
    # Return False if there's an error
    def evaluate(self, expr, obj):
        if expr == "": return None
        # Parse the expression
        ast = self.parse(expr)
        # Evaluate it
        result = self.eval_expr(ast, obj)
        return result

    # This is the core of the evaluation process
    def parse(self, expr):
        expr = expr.strip().upper()
        # Two steps:
        expr_list = self.generate_expr_list(expr)
        return self.generate_ast(expr_list)

    # #1 Separate operators and operands, get rid of all parentheses
    # E.g (1 + 2) + 3 + 4 =>[["1",'+',"2"], '+', "3", '+', "4"]
    def generate_expr_list(self, expr):
        result = []
        start_index = 0
        i = 0

        while i < len(expr):
            char = expr[i]

            # Assumption: All operators are only one character long
            if char in slide.OPERATORS:
                # No start_index indicates we have already added the operand
                # Because the operand is an expression in parentheses
                if start_index != None:
                    # Add an operand
                    result.append(expr[start_index:i])

                # Add the operator
                result.append(expr[i])
                start_index = i + 1
            elif char == "(":
                right_index = self.find_right_parenthesis(expr, i)

                if right_index == None: return None

                # Parse the contents in the parentheses recursively
                sub_list = self.parse(expr[i+1:right_index])

                if sub_list == None: return None
                
                result.append(sub_list)
                start_index = None
                i = right_index
            else:
                pass

            i += 1

        # Add the last operand
        if start_index != None: result.append(expr[start_index:])

        # Edge case: no operators
        if result == []: return expr

        return result

    # #2 Organize into proper ast format according to operator priority
    # E.g [[2], '+', [2], '*', [2]] => ['+', 2, ['*', 2, 2]]
    def generate_ast(self, expr_list):
        # Either False or just a string
        if type(expr_list) != list: return expr_list

        result = expr_list

        # Get rid of outer parentheses:
        flag = False
        while type(result) == list and len(result) == 1:
            flag = True
            result = result[0]
        # If the original list has only one element
        # then it is already turned into ast format
        if flag: return result

        for operators in self.OPERATOR_PRIORITIES:
            i = 0
            while i < len(result):
                if result[i] in operators:
                    # The operator is not the last item
                    assert(i + 1 < len(result))
                    # The operator is not the first item
                    assert(i > 0)

                    # Collapse the 3 items in the list
                    result = (result[:i-1]
                              + [[result[i], result[i-1], result[i+1]]]
                              + result[i+2:])
                else:
                    i += 1

        # Get rid of the outer list
        result = result[0]

        return result

    # Find the index of the right parenthesis 
    # given the index of the corresponding left parenthesis
    def find_right_parenthesis(self, string, i):
        matching_number = 0
        assert(string[i] == "(")
        for index in range(i, len(string)):
            if string[index] == "(": 
                matching_number += 1
            elif string[index] == ")":
                matching_number -= 1
            # There are same numbers of left and right parentheses
            if matching_number == 0:
                return index
        # There is no corresponding right parenthesis
        return None

    # The following 3 methods are copied and edited 
    # from "ourGrossLittleLanguage.py" by David Kosbie
    # Optional content of the course 15-112 at CMU
    def eval_list(self, ast, obj):
        if ast == None: return None
        assert(type(ast) == list)
        operator = ast[0]
        try:
            operand1 = self.eval_expr(ast[1], obj)
            operand2 = self.eval_expr(ast[2], obj)
            if (operator == '+'): return operand1 + operand2
            elif (operator == '-'): return operand1 - operand2
            elif (operator == '*'): return operand1 * operand2
            elif (operator == '/'): return operand1 / operand2
            elif (operator == '^'): return operand1 ** operand2
            elif (operator == '%'): return operand1 % operand2
            else: raise Exception("wnkn opreator: " + operator)
        except Exception as error:
            raise Exception(
                "Error in function %s: %s" % (str(operator), str(error)))

    def eval_expr(self, ast, obj):
        if ast == None: return None
        if (is_num_type(ast)):
            return int(ast)
        elif (type(ast) == list):
            return self.eval_list(ast, obj)
        elif (type(ast) == str):
            return self.eval_str(ast, obj)
        else:
            raise Exception("Unknown stuff or thing: " + str(ast) )

    def eval_str(self, ast, obj):
        if ast == None:
            return None

        index = ast.find(".")
        if index == -1:
            object_referenced = obj
            field = ast
        else:
            object_name = ast[:index]
            if object_name not in self.object_dict: return None
            object_referenced = self.object_dict[object_name]
            field = ast[i+1:]

        if field not in object_referenced.fields: return None
        return object_referenced.get_value(field)

    # Render is specific to slides
    # Has a more professional feel
    def render(self, canvas, startx, starty, edit = True, display_ratio = 1):
        for user_object in self.objects:
            if edit or user_object.is_visible:
                user_object.draw(canvas, startx, starty, display_ratio)

# A slibe_btn (aka snapshot) is a button that represents a slide
class slide_btn(psm_button):

    HEIGHT = CANVAS_HEIGHT * CANVAS_TO_SLIDE
    WIDTH = CANVAS_WIDTH * CANVAS_TO_SLIDE

    def __init__(self, x, y, slide, func = None, 
            parent = None,
            stipple = False):
        # Stipple is on for the "take snapshot" button
        # which shows the current working slide
        self.stipple = stipple
        self.slide = slide
        x1 = x - slide_btn.WIDTH / 2
        x2 = x + slide_btn.WIDTH / 2
        y1 = y - slide_btn.HEIGHT / 2
        y2 = y + slide_btn.HEIGHT / 2
        super().__init__(x1, y1, x2, y2, parent = parent, click_func = func)

    def draw(self, canvas):
        x, y = self.get_center()
        #print("Drawn center:", self.get_center())
        x1 = x - self.width / 2
        x2 = x + self.width / 2
        y1 = y - self.height / 2
        y2 = y + self.height / 2
        if self.stipple:
            canvas.create_rectangle(x1, y1, x2, y2, fill = "white",
                dash = (4,4))
        else:
            canvas.create_rectangle(x1, y1, x2, y2, fill = "white")

        self.slide.render(canvas, x1, y2, display_ratio = CANVAS_TO_SLIDE)

# Play/stop button
class play_btn(psm_button):
    
    RADIUS = 50
    BG_COLOR = "red"
    CENTER_COLOR = "black"

    def __init__(self, x, y, func, parent):
        x1 = x - play_btn.RADIUS
        x2 = x + play_btn.RADIUS
        y1 = y - play_btn.RADIUS
        y2 = y + play_btn.RADIUS
        super().__init__(x1, y1, x2, y2, click_func = func, parent = parent)
        # "PLAY" "STOP"
        self.mode = "PLAY"

    def on_click(self):
        if self.mode == "STOP":
            self.mode = "PLAY"
        elif self.mode == "PLAY":
            self.mode = "STOP"
        self.click_func()

    def draw(self, canvas):
        x, y = self.get_center()
        x1 = x - play_btn.RADIUS
        x2 = x + play_btn.RADIUS
        y1 = y - play_btn.RADIUS
        y2 = y + play_btn.RADIUS
        canvas.create_oval(x1, y1, x2, y2, 
            fill = play_btn.BG_COLOR, width = 0)
        if self.mode == "STOP":
            x1 = x - play_btn.RADIUS * 2/5
            x2 = x + play_btn.RADIUS * 2/5
            y1 = y - play_btn.RADIUS * 2/5
            y2 = y + play_btn.RADIUS * 2/5
            canvas.create_rectangle(x1, y1, x2, y2,
                fill = play_btn.CENTER_COLOR)
        elif self.mode == "PLAY":
            x1 = x - play_btn.RADIUS * 1/3
            x2 = x - play_btn.RADIUS * 1/3
            x3 = x + play_btn.RADIUS * 1/2
            y1 = y - play_btn.RADIUS * 1/2
            y2 = y + play_btn.RADIUS * 1/2 
            y3 = y
            canvas.create_polygon([(x1,y1),
                                   (x2,y2),
                                   (x3,y3)],
                                   fill = play_btn.CENTER_COLOR)    

class Presimation(Animation):

    # Defining the toolsets and tools here improves clarity
    # Every item should be a tuple of name(key) and instance of a class

    # TODO: This is only temporary
    TOOLS = [["Objects",
                [("CIRCLE", psm_circle_tool())]
             ],
             ["Drawing",
                []
             ],
             ["Animation", 
                [("SELECTION", psm_selection_tool())]
             ]
            ]

################################ initialization ################################

    def __init__(self, width, height):
        self.width = width
        self.height = height

        # (int) The index of the slide selected
        # At the start there are no slides saved
        self.current_slide = -1
        self.mouse_over_slide = -1

        # We might not need this -- we can just let objects draw their own menus
        # The list of menus currently opened
        self.menus = []
        
        # The list of slides created
        self.slides = []
        # The slide that's being worked on
        # After taking a snapshot, the working slide will be filed
        # in the "slides" list
        # When an existing slide is selected, a copy of that slide
        # will become the working slide
        self.working_slide = slide()

        self.tools = self.get_tool_dict()
        # (psm_tool)
        self.current_tool = SELECTION_TOOL

        # Now we can only select objects one at a time for simplicity's sake
        self.selected_object = None

        ####################
        # Animation stuff
        ####################
        self.time = 0
        self.slide_time_interval = 50
        # "EDIT" "PLAYBACK"
        self.mode = "EDIT"

        # There is an a reason we have to do this
        self.is_initializing = True
        self.run(width, height)

    def get_tool_dict(self):
        tool_dict = dict()
        for toolset in Presimation.TOOLS:
            tool_dict.update(toolset[1])
        return tool_dict

    def init_GUI(self):
        test_img_file = os.path.join(__location__, 
                                     "../Images/object_toolset.gif")
        self.test_icon = PhotoImage(file = test_img_file)

        self.init_size()
        self.create_outline()
        self.init_tools()
        self.create_timeline()

        self.GUI_objects = [self.toolbars[0],
                            self.toolbars[1],
                            self.timeline,
                            self.workspace]

    def init_size(self):
        # dependent ratio
        self.toolbar_w_ratio = (1 - WORKSPACE_WIDTH_R) / 2
        self.toolbar_h_ratio = self.wkspace_h_ratio = 1 - TMLINE_HEIGHT_R
        self.tmline_w_ratio = 1

        # size
        self.toolbar_w = self.width * self.toolbar_w_ratio
        self.toolbar_h = self.height * self.toolbar_h_ratio

        self.tmline_w = self.width * self.tmline_w_ratio
        self.tmline_h = self.height * TMLINE_HEIGHT_R

        self.wkspace_w = self.width * WORKSPACE_WIDTH_R
        self.wkspace_h = self.height * self.wkspace_h_ratio

        # fixed width to height ratio
        self.wkspace_w_to_h = self.wkspace_w / self.wkspace_h

    # Create GUI outlines like the toolbar and workspace
    def create_outline(self):
        # create toolbars
        left_toolbar = psm_GUI_object(0, 0, 
            self.toolbar_w, self.toolbar_h, "white")
        right_toolbar = psm_GUI_object(self.toolbar_w + self.wkspace_w, 0,
            self.width, self.toolbar_h, "white")
        self.toolbars = [left_toolbar, right_toolbar]

        # create timeline
        timeline = psm_GUI_object(0, self.toolbar_h,
            self.width, self.height, "white")
        self.timeline = timeline

        # create workspace
        workspace = psm_GUI_object(self.toolbar_w, 0,
          self.toolbar_w + self.wkspace_w, self.wkspace_h, lightGrey, 
          border = 1)

        # create canvas
        canvas_left = CANVAS_MARGIN_HORIZONTAL
        canvas_top = CANVAS_MARGIN_VERTICAL
        canvas_right = self.wkspace_w - canvas_left
        canvas_bottom = self.wkspace_h - canvas_top
        canvas = psm_GUI_object(canvas_left, 
                                canvas_top,
                                canvas_right,
                                canvas_bottom,
                                parent = workspace,
                                border = 1)

        self.workspace = workspace

    # Create toolbars, toolsets(big buttons) and tools(small buttons)
    def init_tools(self):
        # Only left toolbar
        # TODO: Add right toolbar
        toolbar = self.toolbars[0]
        toolset_count = len(Presimation.TOOLS)

        # determine the top_left corner of the tools
        top = (self.toolbar_h / toolset_count 
            - psm_toolbar_btn_large.BUTTON_SIZE) / 2
        left = 0

        for i in range(toolset_count):
            # top_left corner of the first small button
            small_btn_start_x = left + psm_toolbar_btn_large.BUTTON_SIZE
            small_btn_start_y = top + self.toolbar_h * i / toolset_count
            toolset_name = Presimation.TOOLS[i][0]

            toolset_icon = self.test_icon

            toolset = psm_toolbar_btn_large(
                left,
                small_btn_start_y,
                toolset_name,
                alt_text = toolset_name,
                orientation = "left",
                color = "white", 
                parent = toolbar,
                image = toolset_icon)  # Clarity      

            for sub_tool in Presimation.TOOLS[i][1]:
                tool_name = sub_tool[0]
                tool = sub_tool[1]

                print("Generate button for " + tool_name)

                tool_btn = psm_toolbar_btn_small(
                    0,
                    0, 
                    tool_name, 
                    color = "red",
                    parent = toolset,
                    alt_text = tool.tool_name, # A little different
                                          # Maybe I should clarify this later...
                    active_fill = "orange",
                    click_func = get_lambda(self.select_tool, tool_name),
                    double_click_func = double_click_debug)

                small_btn_start_y += psm_toolbar_btn_small.BUTTON_SIZE

    # Create the timeline, including the play/stop button and snapshot button
    def create_timeline(self):
        # camera button
        snapshot_btn = slide_btn(SCREEN_WIDTH - TOOLBAR_WIDTH / 2,
                                 TMLINE_HEIGHT / 2, 
                                 self.working_slide,
                                 self.take_snapshot,
                                 parent = self.timeline,
                                 stipple = True)

        # Playback button
        playback_btn = play_btn(TOOLBAR_WIDTH / 2,
                                TMLINE_HEIGHT / 2,
                                self.switch_mode,
                                parent = self.timeline)

        # TODO: max limit??
        self.snapshots = []

        snapshot_h = CANVAS_HEIGHT * CANVAS_TO_SLIDE
        snapshot_w = CANVAS_WIDTH * CANVAS_TO_SLIDE
        self.snapshot_uncover_w = snapshot_w * TMLINE_UNCOVER

        # set initial position of the snapshots
        self.start_x = self.toolbar_w + TMLINE_MARGIN_W
        self.end_x = self.toolbar_w + self.wkspace_w\
            - TMLINE_MARGIN_W - snapshot_w
        self.start_y = (SCREEN_HEIGHT * TMLINE_HEIGHT_R - slide_btn.HEIGHT) / 2

    # adjust the positions of the snapshots according to current_slide
    def update_snapshots(self):
        if len(self.snapshots) == 0: return
        # The index of the slide we are currently viewing in the timeline
        if self.mouse_over_slide == -1:
            slide_index = self.current_slide
        else:
            slide_index = self.mouse_over_slide

        # left stack
        y1 = self.start_y
        for i in range(slide_index + 1):
            x1 = self.start_x + self.snapshot_uncover_w * i
            self.snapshots[i].resize(x1, y1)

        # right stack
        x1 = self.end_x
        for i in range(len(self.snapshots)-1, slide_index, -1):
            self.snapshots[i].resize(x1, y1)
            x1 = x1 - self.snapshot_uncover_w

##################### helper functions used by GUI objects #####################

    # Called by specific tool buttons
    def select_tool(self, tool_name):
        print(tool_name)
        if tool_name == None:
            print("Tool changed to selection")
            self.current_tool = SELECTION_TOOL
        else:
            # substitute it with real functions
            print("Tool changed to ", tool_name)
            self.current_tool = self.tools[tool_name]

    # Called by slide buttons
    def select_slide(self, index):
        self.current_slide = index

    # Called by the play/stop button
    def switch_mode(self):
        if self.mode == "PLAYBACK":
            self.mode = "EDIT"
        elif self.mode == "EDIT":
            self.mode = "PLAYBACK"
            self.start_playing()

    def start_playing(self):
        self.time = 0

    # Called by the take snapshot button
    # Generates a new slide and a snapshot(a button that represents the slide)
    def take_snapshot(self):
        i = len(self.snapshots)
        self.slides.append(slide.copy(self.working_slide))
        width = slide_btn.WIDTH
        height = slide_btn.HEIGHT
        # This is the center coordinate, not top-left
        x = (WORKSPACE_LEFT + TMLINE_MARGIN_W + 
            i * self.snapshot_uncover_w + width / 2)
        y = SCREEN_HEIGHT * TMLINE_HEIGHT_R / 2
        self.snapshots.append(
            slide_btn(x, y,
                self.slides[i],
                lambda: self.select_slide(i),
                parent = self.timeline)
            )
        self.current_slide = i
        self.slides
        self.update_snapshots()

########################### other helper functions #############################

    # Returns the length of the entire animation
    # This function will change if we allow different slides to have 
    # different lengths in time
    def get_playback_length(self):
        slide_count = len(self.slides)
        result = (slide_count - 1) * self.slide_time_interval
        if result == 0: result = 1
        return result

    # Returns the slide number the playback is currently on
    # and the ratio of interpolation [0,1)
    # Will be changed in the future, same as above
    def get_playback_progress(self):
        slide_index = self.time // self.slide_time_interval
        ratio = ((self.time % self.slide_time_interval) 
                    / self.slide_time_interval)
        return slide_index, ratio

############################### system events ##################################

    # There is an inexplicable bug
    # When you hold down a key
    def key_pressed(self, event):
        if event.keysym.upper() == "D":
            #print("Pressed D")
            if self.current_tool == SELECTION_TOOL:
                self.current_tool = COPY_TOOL
        elif event.keysym.upper() == "E":
            pass
            #print("Pressed E")

    def key_released(self, event):
        if event.keysym.upper() == "D":
            #print("Released D")
            if self.current_tool == COPY_TOOL:
                #self.current_tool.reset()
                self.current_tool = SELECTION_TOOL
        elif event.keysym.upper() == "E":
            pass
            #print("Released E")

    def mouse_down(self, event):
        for GUI_object in self.GUI_objects:
            GUI_object.on_mouse_down(event.x, event.y)
        if self.mode == "EDIT":
            if (self.current_tool == SELECTION_TOOL
                or self.current_tool == COPY_TOOL):
                # We are selecting an object
                # Process the mouse down event for user objects
                count = len(self.working_slide.objects)
                # Only one object can be selected with a mouse click
                selected_flag = False
                for temp in range(count):
                    index = count - temp - 1
                    obj = self.working_slide.objects[index]

                    if not selected_flag and obj.in_borders(event.x, event.y):
                        obj.on_mouse_down(event.x, event.y)
                        self.selected_object = obj
                        selected_flag = True
                    else:
                        obj.set_selected(False)
                if self.current_tool == COPY_TOOL and selected_flag:
                    self.selected_object.set_selected(False)
                    # This is where the object actually gets copied
                    copied_object = psm_object.copy(self.selected_object)
                    self.current_tool.on_mouse_down(event.x, event.y, 
                        copied_object)
            else:
                # The general object names like "Circle" "Line" etc.
                object_name = self.current_tool.get_object_name()
                # Specific object names like "Circle5" 
                # that can only correspond to one instance of the object
                object_name = self.working_slide.generate_object_name(
                        object_name)
                self.current_tool.on_mouse_down(event.x, 
                                                event.y, 
                                                object_name,
                                                self.working_slide)

    def mouse_up(self, event):
        for GUI_object in self.GUI_objects:
            GUI_object.on_mouse_up(event.x, event.y)
        if self.current_tool == SELECTION_TOOL:
            for obj in self.working_slide.objects:
                if obj.is_selected:
                    obj.on_mouse_up(event.x, event.y)
        else:
            new_object = self.current_tool.on_mouse_up(event.x, event.y)
            if new_object != None:
                self.working_slide.add_object(new_object)
            # Change tool to "selection" every time we use it once
            # The mouseup has to happen inside the workspace
            if psm_tool.in_workspace(event.x, event.y):
                self.current_tool = SELECTION_TOOL

    def mouse_move(self,event):
        # Selection tool
        if self.current_tool == SELECTION_TOOL:
            for obj in self.working_slide.objects:
                # Currently only one object can be selected at a time
                if obj.is_selected:
                    obj.on_mouse_move(event.x, event.y)
        else:
            self.current_tool.on_mouse_move(event.x, event.y)

        mouse_over_slide = False
        # check if the mouse hovers on the snapshots
        # left stack
        for i in range(self.current_slide, -1, -1):
            if self.snapshots[i].in_borders(event.x, event.y):
                self.mouse_over_slide = i
                mouse_over_slide = True
                break
        if not mouse_over_slide:
            # right stack
            for i in range(len(self.snapshots)-1, self.current_slide, -1):
                if self.snapshots[i].in_borders(event.x, event.y):
                    mouse_over_slide = True
                    self.mouse_over_slide = i
                    break
        # If the mouse isn't hovering on any slide, let the program know
        if not mouse_over_slide:
            self.mouse_over_slide = -1

    def timer_fired(self):
        if self.is_initializing:
            self.init_GUI()
            self.is_initializing = False
        else:
            self.update_snapshots()
            # Update all the buttons
            for GUI_object in self.GUI_objects:
                GUI_object.update()
            if self.mode == "EDIT":
                # We need the selected object in the working slide to update
                # since double clicking toggles the menu
                self.working_slide.update()
            elif self.mode == "PLAYBACK":
                self.time += 1
                self.time = self.time % self.get_playback_length()

    def redraw_all(self):
        if self.is_initializing: return

        # Draw workspace
        self.workspace.draw(self.canvas)

        # Draw canvas
        if self.mode == "EDIT":
            self.working_slide.render(self.canvas,
                                      CANVAS_ORIGIN_X,
                                      CANVAS_ORIGIN_Y)
        elif self.mode == "PLAYBACK":
            i, ratio = self.get_playback_progress()
            slide.interpolate(self.slides[i],
                              self.slides[i + 1],
                              ratio).render(self.canvas,
                                            CANVAS_ORIGIN_X,
                                            CANVAS_ORIGIN_Y)

        # Set mouse cursor for different tools
        if self.current_tool == COPY_TOOL:
            self.root.config(cursor = "hand1")
            self.current_tool.draw_object(self.canvas)
        elif self.current_tool != SELECTION_TOOL:
            self.root.config(cursor = "hand2")
            self.current_tool.draw_object(self.canvas)
        else:
            self.root.config(cursor = "")

        # Draw other GUI elements
        self.toolbars[0].draw(self.canvas)
        self.toolbars[1].draw(self.canvas)
        self.timeline.draw(self.canvas)

        # Draw snapshots
        for snapshot in self.snapshots:
            snapshot.draw(self.canvas)

psm = Presimation(SCREEN_WIDTH, SCREEN_HEIGHT)