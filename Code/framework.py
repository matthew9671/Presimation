from Animation import *
from interface import *
import copy

# This class stores information about fields of an object
# including how it is presented in the menu

# colors
lightGrey = rgbString(200,200,200)
offWhite = rgbString(250, 250, 235)

class psm_field(object):
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

class psm_object(object):
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

class psm_tool(object):
    def __init__(self): pass

class slide(object):
    def __init__(self):
        self.objects = None

    # Render is specific to slides
    # Has a more professional feel
    def render(self, canvas, startx, starty, edit = True):
        for user_object in self.objects:
            if edit or user_object.is_visible:
                user_object.draw(canvas, startx, starty)

class Presimation(Animation):
    def __init__(self, width, height):
        self.width = width
        self.height = height

        # The list of GUI objects including the toolbar and the timeline
        self.GUI_objects = []

        # The index of the current slide
        self.current_slide = 4

        self.init_GUI()

        # The list of menus currently opened
        self.menus = []
        
        # The list of slides created
        self.slides = []

        # TODO: Add a list of tools
        self.current_tool = None

        # "EDIT" "PLAYBACK"
        self.mode = "EDIT"
        self.run(width, height)

    def init_size(self):
        # dependent ratio
        self.toolbar_w_ratio = (1 - self.wkspace_w_ratio) / 2
        self.toolbar_h_ratio = self.wkspace_h_ratio = 1 - self.tmline_h_ratio
        self.tmline_w_ratio = 1

        # size
        self.toolbar_w = self.width * self.toolbar_w_ratio
        self.toolbar_h = self.height * self.toolbar_h_ratio

        self.tmline_w = self.width * self.tmline_w_ratio
        self.tmline_h = self.height * self.tmline_h_ratio

        self.wkspace_w = self.width * self.wkspace_w_ratio
        self.wkspace_h = self.height * self.wkspace_h_ratio

        # fixed width to height ratio
        self.wkspace_w_to_h = self.wkspace_w / self.wkspace_h

    def create_outline(self):
        # create workspace
        workspace = psm_GUI_object(self.toolbar_w, 0,
          self.toolbar_w+self.wkspace_w, self.wkspace_h, offWhite)
        self.GUI_objects.append(workspace)

        # create toolbars
        left_toolbar = psm_panel(0, 0, self.toolbar_w, self.toolbar_h,lightGrey)
        right_toolbar = psm_panel(self.toolbar_w + self.wkspace_w, 0,
            self.width, self.toolbar_h, lightGrey)
        self.GUI_objects.extend([left_toolbar, right_toolbar])

        # create timeline
        timeline = psm_panel(0, self.toolbar_h,
            self.width, self.height, lightGrey)
        self.GUI_objects.append(timeline)

    def create_timeline(self):
        # camera button
        self.GUI_objects.append(psm_button(self.toolbar_w + self.wkspace_w,
            self.toolbar_h, self.width, self.height, "blue"))

        # max limit??
        self.snapshots = []

        snapshot_h = self.tmline_h - self.tmline_margin_h * 2
        snapshot_w = snapshot_h * self.wkspace_w_to_h
        self.snapshot_uncover_w = snapshot_w * self.tmline_uncover_ratio

        # set initial position of the snapshots
        self.start_x = self.toolbar_w + self.tmline_margin_w
        self.end_x = self.toolbar_w + self.wkspace_w\
            - self.tmline_margin_w - snapshot_w
        self.start_y = self.toolbar_h + self.tmline_margin_h

        # create initial snapshots (5 as an example)
        for i in range(5):
            self.snapshots.append(psm_button(
                self.start_x + i * self.snapshot_uncover_w, self.start_y,
                self.start_x + i * self.snapshot_uncover_w + snapshot_w,
                self.start_y + snapshot_h, offWhite))
        self.update_snapshots()  # adjust the positions of the snapshots

    def update_snapshots(self):
        # left stack
        y1 = self.start_y
        for i in range(self.current_slide + 1):
            x1 = self.start_x + self.snapshot_uncover_w * i
            self.snapshots[i].resize(x1, y1)

        # right stack
        x1 = self.end_x
        for i in range(len(self.snapshots)-1, self.current_slide, -1):
            self.snapshots[i].resize(x1, y1)
            x1 = x1 - self.snapshot_uncover_w

    def init_tools(self):
        self.tool_sets = ["shapes", "lines", "texts"]  # large buttons
        self.num = len(self.tool_sets)
        self.tools = dict()  # small buttons
        self.tools["shapes"] = ["circle", "rectangle", "star", "custom"]
        self.tools["lines"] = ["lines", "curves"]
        self.tools["texts"] = ["fonts", "bold", "highlight"]

        # determine the top_left corner of the tools
        top = (self.toolbar_h / self.num - psm_toolbar_btn_large.BUTTON_SIZE)/2
        left = (self.toolbar_w - psm_toolbar_btn_large.BUTTON_SIZE
            - psm_toolbar_btn_small.BUTTON_SIZE)/2

        for i in range(self.num):

            # top_left corner of the first small button
            small_btn_start_x = left + psm_toolbar_btn_large.BUTTON_SIZE
            small_btn_start_y = top + self.toolbar_h * i / self.num
            toolset_name = self.tool_sets[i]
            toolset = psm_toolbar_btn_large(left,small_btn_start_y,toolset_name,
                 "left", "blue", True, 4, self.GUI_objects[1])  # toolbar      

            for tool_name in self.tools[toolset_name]:
                tool = psm_toolbar_btn_small(small_btn_start_x,
                    small_btn_start_y, tool_name, "left", False, "red", True,
                    1, self.GUI_objects[1], "Button", "orange",
                    lambda : self.select_tool(tool_name))
                self.GUI_objects[1].add_child(tool)
                toolset.add_sub_tool(tool)
                small_btn_start_y += psm_toolbar_btn_small.BUTTON_SIZE

            self.GUI_objects[1].add_child(toolset)

    def select_tool(self, tool_name):
        # substitute it with real functions
        print("Click ", tool_name)
        self.current_tool = tool_name

    def init_GUI(self):
        # TODO: Add values to these parameters
        # independent ratio and size
        self.wkspace_w_ratio = 0.6  # width of the workspace
        self.tmline_h_ratio = 0.25  # height of the timeline
        self.tmline_margin_w = 5
        self.tmline_margin_h = 5

        # users can always see 1/4 of the rest snapshots
        self.tmline_uncover_ratio = 0.25

        self.init_size()
        self.create_outline()
        self.init_tools()
        self.create_timeline()

        self.canvas_start_x = None
        self.canvas_start_y = None

    def mousePressed(self, event):
        for GUI_object in self.GUI_objects:
            GUI_object.on_mouse_down(event.x, event.y)
        if self.mode == "EDIT":
            # Process the mouse down event for user objects
            for user_object in self.current_slide.slides:
                pressed = user_object.mouse_down(event.x, event.y)
                if pressed:
                    # Only one object can be pressed
                    break

    def leftMouseReleased(self,event):
        for GUI_object in self.GUI_objects:
            GUI_object.on_mouse_up(event.x, event.y)

    def keyPressed(self, event): pass
    def keyReleased(self,event):pass
    def mouseMotion(self,event):
        # check if the mouse hovers on the snapshots
        # left stack
        for i in range(self.current_slide, -1, -1):
            if self.snapshots[i].in_borders(event.x, event.y):
                self.current_slide = i
                return

        # right stack
        for i in range(len(self.snapshots)-1, self.current_slide, -1):
            if self.snapshots[i].in_borders(event.x, event.y):
                self.current_slide = i
                return

    def timerFired(self):
        self.update_snapshots()

    def redrawAll(self):
        # Draw GUI
        for GUI_object in self.GUI_objects:
            GUI_object.draw(self.canvas)

        # Draw snapshots
        # right stack
        for i in range(self.current_slide+1, len(self.snapshots)):
            self.snapshots[i].draw(self.canvas)

        # left stack
        for i in range(self.current_slide+1):
            self.snapshots[i].draw(self.canvas)

        # Draw workspace
        self.slides[self.current_slide].render(
            self.canvas,
            self.canvas_start_x,
            self.canvas_start_y)

psm = Presimation(900, 600)