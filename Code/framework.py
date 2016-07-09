from Animation import *
from interface import *
import copy

# TODO: Right now the ratios and lengths are mixed up
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

WORKSPACE_SIDES = 1/6
WORKSPACE_BOTTOM = 1/3
CANVAS_MARGIN = 1/20

# Origin = Bottom left
CANVAS_ORIGIN_X = SCREEN_WIDTH * (WORKSPACE_SIDES + CANVAS_MARGIN)
CANVAS_ORIGIN_Y = SCREEN_HEIGHT * (1 - WORKSPACE_BOTTOM - CANVAS_MARGIN)

# I moved these to the top level for convenience
# independent ratio and size
WORKSPACE_WIDTH = 1 - WORKSPACE_SIDES * 2  # width of the workspace
TMLINE_HEIGHT = 0.25  # height of the timeline
TMLINE_MARGIN_W = 5
TMLINE_MARGIN_H = 5

WORKSPACE_LEFT = SCREEN_WIDTH * WORKSPACE_SIDES
WORKSPACE_RIGHT = SCREEN_WIDTH - WORKSPACE_LEFT
WORKSPACE_TOP = 0
WORKSPACE_BOTTOM = SCREEN_HEIGHT * (1 - TMLINE_HEIGHT)

# Users can always see 1/4 of the rest snapshots
TMLINE_UNCOVER = 0.25

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

# This class stores information about fields of an object
# including how it is presented in the menu
class psm_field(object):

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

    def get_value(self):
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
                for col in range(len(self.tabs[tab][row])):
                    item = self.tabs[tab][row][col]
                    x1, y1 = get_item_topleft_position(row, col)
                    button = psm_menu_icon(x1,
                                           y1,
                                           x1 + psm_field.ICON_SIZE,
                                           y1 + psm_field.ICON_SIZE,
                                           image = item.icon,
                                           parent = panel)
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


class psm_object(object):
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

        # TODO: These can be further specified
        name_field = psm_field(name)
        index_field = psm_field(index)
        self.attributes["NAME"] = name_field
        self.attributes["INDEX"] = index_field

        # Generate the handles(control points)(type: psm_button)
        # for the user to manipulate the object
        self.handle_holder = psm_GUI_object(0,0,0,0)
        self.handles = None

    def generate_handles(self): pass

    def update_handles(self):
        if self.handles == None:
            self.generate_handles()

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

    def on_mouse_down(self, x, y):
        # The mainloop calls mouse_down
        # only when the object is being clicked upon
        assert(self.in_borders(x, y))
        if self.is_selected:
            # Pass the mouse_down event to the object's children
            # Namely the handles
            self.handle_holder.on_mouse_down(x, y)
        else:
            self.is_selected = True
            self.menu_on = True

    # Useful when we are drag-selecting objects
    def set_selected(self, value):
        self.is_selected = value

    # Pass in the ratio for drawing miniture slides
    def draw(self, canvas, startx, starty, ratio = 1):
        # We don't want to display the menu in the thumbnail
        if self.menu_on and self.menu != None and ratio == 1:
            self.menu.draw(canvas, startx, starty)

    def get_hashables(self):
        return (self.name, self.index)

    def __eq__(self, other):
        if other == None: return False
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
            assert(prev_r != 0)
        else:
            prev_r = (dx ** 2 + dy ** 2) ** 0.5
            x, y = dx, dy
            if prev_r == 0: return

        curr_r = self.get_value("RADIUS")
        new_x = x * curr_r / prev_r
        new_y = - y * curr_r / prev_r
        rim_handle.move_to(new_x, new_y)

    def on_mouse_move(self, x, y):
        self.handle_holder.on_mouse_move(x, y)
        x, y = global_to_canvas(x, y)
        center_x = self.get_value("CENTER_X")
        center_y = self.get_value("CENTER_Y")
        self.update_handles(x - center_x, y - center_y)

    def on_mouse_down(self, x, y):
        super().on_mouse_down(x, y)
        print("Object %s Selected" % self.get_value("NAME"))

    def on_mouse_up(self, x, y):
        self.handle_holder.on_mouse_up(x, y)

    def draw(self, canvas, startx, starty, ratio = 1):
        super().draw(canvas, startx, starty, ratio)
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
        canvas.create_oval(x1, y1, x2, y2, fill = fill_color, 
                                           width = border_width, 
                                           outline = border_color)
        if ratio == 1 and self.is_selected:
            # We are not displaying a thumbnail
            if self.handles == None: self.generate_handles()
            self.handle_holder.draw(canvas)

class psm_tool(object):

    # The minimum size (width and height) that an object can have
    MIN_ELEM_SIZE = 10

    def __init__(self, tool_name, object_name):
        # True when the mouse is pressed
        self.mouse_pressed = False
        self.current_object = None
        # A tuple (x, y) of position coordinates
        self.drag_start = None
        self.tool_name = tool_name
        self.object_name = object_name

    @classmethod
    def in_workspace(self, x, y):
        return (x > WORKSPACE_LEFT 
            and x < WORKSPACE_RIGHT
            and y > WORKSPACE_TOP
            and y < WORKSPACE_BOTTOM)

    def on_mouse_down(self, x, y, object_name):
        if not psm_tool.in_workspace(x, y): return
        if not self.mouse_pressed:
            self.drag_start = (x, y)
            self.mouse_pressed = True
            self.generate_object(object_name)

    def mouse_up(self, x, y):
        self.mouse_pressed = False
        # Pass the "ownership" of the object being generated
        # from itself to the main loop
        current_object = self.current_object
        self.current_object = None
        return current_object

    def mouse_move(self, x, y):
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

    def generate_object(self, object_name):
        pass

    def resize_object(self, width, height):
        pass

    def draw_object(self, canvas):
        if self.current_object != None:
            self.current_object.draw(canvas, CANVAS_ORIGIN_X, 
                                             CANVAS_ORIGIN_Y)

    def get_object_name(self):
        return self.object_name

class psm_circle_tool(psm_tool):

    MIN_RADIUS = 5

    def __init__(self):
        super().__init__(tool_name = "Circle tool", object_name = "Circle")
        self.default_values = {
            "FILL_COLOR": "white",
            "BORDER_COLOR": "black",
            "BORDER_WIDTH": 3
        }

    def generate_object(self, object_name):
        x, y = global_to_canvas(self.drag_start)
        self.current_object = psm_circle(object_name, 0)
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

class slide(object):
    def __init__(self):
        self.objects = []

    def add_object(self, user_object):
        self.objects.append(user_object)

    # Returns an object name that is unique in the slide
    # TODO: Write this
    def generate_object_name(self, name):
        return name

    # Render is specific to slides
    # Has a more professional feel
    def render(self, canvas, startx, starty, edit = True, display_ratio = 1):

        for user_object in self.objects:
            if edit or user_object.is_visible:
                user_object.draw(canvas, startx, starty, display_ratio)

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
                []
             ]
            ]

    def __init__(self, width, height):
        self.width = width
        self.height = height

        # (int) The index of the slide selected
        self.current_slide = 0

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
        self.current_tool = None

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
        test_img_file = "Presimation_demo/Images/Test2.gif"
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
        self.toolbar_w_ratio = (1 - WORKSPACE_WIDTH) / 2
        self.toolbar_h_ratio = self.wkspace_h_ratio = 1 - TMLINE_HEIGHT
        self.tmline_w_ratio = 1

        # size
        self.toolbar_w = self.width * self.toolbar_w_ratio
        self.toolbar_h = self.height * self.toolbar_h_ratio

        self.tmline_w = self.width * self.tmline_w_ratio
        self.tmline_h = self.height * TMLINE_HEIGHT

        self.wkspace_w = self.width * WORKSPACE_WIDTH
        self.wkspace_h = self.height * self.wkspace_h_ratio

        # fixed width to height ratio
        self.wkspace_w_to_h = self.wkspace_w / self.wkspace_h

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
        canvas_left = SCREEN_WIDTH * CANVAS_MARGIN
        canvas_top = SCREEN_HEIGHT * CANVAS_MARGIN
        canvas_right = self.wkspace_w - canvas_left
        canvas_bottom = self.wkspace_h - canvas_top
        canvas = psm_GUI_object(canvas_left, 
                                canvas_top,
                                canvas_right,
                                canvas_bottom,
                                parent = workspace,
                                border = 1)

        self.workspace = workspace

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
                color = "blue", 
                parent = toolbar,
                image = toolset_icon)  # Clarity      

            for sub_tool in Presimation.TOOLS[i][1]:
                tool_name = sub_tool[0]
                tool = sub_tool[1]

                tool_btn = psm_toolbar_btn_small(
                    0,
                    0, 
                    tool_name, 
                    color = "red",
                    parent = toolset,
                    alt_text = tool.tool_name, # A little different
                                          # Maybe I should clarify this later...
                    active_fill = "orange",
                    click_func = lambda : self.select_tool(tool_name),
                    double_click_func = double_click_debug)

                small_btn_start_y += psm_toolbar_btn_small.BUTTON_SIZE

    def create_timeline(self):
        # camera button
        snapshot_btn = psm_button(SCREEN_WIDTH - self.toolbar_w,
            0, self.width, self.height, "orange",
            parent = self.timeline,
            click_func = self.take_snapshot)

        # TODO: max limit??
        self.snapshots = []

        snapshot_h = self.tmline_h - TMLINE_MARGIN_H * 2
        snapshot_w = snapshot_h * self.wkspace_w_to_h
        self.snapshot_uncover_w = snapshot_w * TMLINE_UNCOVER

        # set initial position of the snapshots
        self.start_x = self.toolbar_w + TMLINE_MARGIN_W
        self.end_x = self.toolbar_w + self.wkspace_w\
            - TMLINE_MARGIN_W - snapshot_w
        self.start_y = self.toolbar_h + TMLINE_MARGIN_H

        # TODO: Create another class for this
        # create initial snapshots (5 as an example)
        for i in range(5):
            self.snapshots.append(psm_button(
                self.start_x + i * self.snapshot_uncover_w, self.start_y,
                self.start_x + i * self.snapshot_uncover_w + snapshot_w,
                self.start_y + snapshot_h, offWhite))
        self.update_snapshots()  

    # adjust the positions of the snapshots according to current_slide
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

    def select_tool(self, tool_name):
        if tool_name == None:
            print("Tool changed to selection")
            self.current_tool = None
        else:
            # substitute it with real functions
            print("Tool changed to ", tool_name)
            self.current_tool = self.tools[tool_name]

    def take_snapshot(self):pass

    def mouse_down(self, event):
        for GUI_object in self.GUI_objects:
            GUI_object.on_mouse_down(event.x, event.y)
        if self.mode == "EDIT":
            # Process the mouse down event for user objects
            # for user_object in self.slides[self.current_slide]:
            #     pressed = user_object.on_mouse_down(event.x, event.y)
            #     if pressed:
            #         # Only one object can be pressed
            #         break
            if self.current_tool == None:   # Selection tool
                count = len(self.working_slide.objects)
                selected_flag = False

                for temp in range(count):
                    index = count - temp - 1
                    obj = self.working_slide.objects[index]

                    if not selected_flag and obj.in_borders(event.x, event.y):
                        obj.on_mouse_down(event.x, event.y)
                        selected_flag = True
                    else:
                        obj.set_selected(False)
            else:
                object_name = self.current_tool.get_object_name()
                object_name = self.working_slide.generate_object_name(
                        object_name)
                self.current_tool.on_mouse_down(event.x, event.y, object_name)

    def mouse_up(self, event):
        for GUI_object in self.GUI_objects:
            GUI_object.on_mouse_up(event.x, event.y)
        if self.current_tool == None:
            for obj in self.working_slide.objects:
                if obj.is_selected:
                    obj.on_mouse_up(event.x, event.y)
        else:
            new_object = self.current_tool.mouse_up(event.x, event.y)
            if new_object != None:
                self.working_slide.add_object(new_object)
            # Change tool to "selection" every time we use it once
            # The mouseup has to happen inside the workspace
            if psm_tool.in_workspace(event.x, event.y):
                self.current_tool = None

    def keyPressed(self, event): pass
    def keyReleased(self,event): pass

    def mouse_move(self,event):
        if self.current_tool == None:
            for obj in self.working_slide.objects:
                # Currently only one object can be selected at a time
                if obj.is_selected:
                    obj.on_mouse_move(event.x, event.y)
        else:
            self.current_tool.mouse_move(event.x, event.y)

        # check if the mouse hovers on the snapshots
        # left stack
        for i in range(self.current_slide, -1, -1):
            if self.snapshots[i].in_borders(event.x, event.y):
                # Actually you have to click to change slides
                # TODO: Change this
                #self.current_slide = i
                return

        # right stack
        for i in range(len(self.snapshots)-1, self.current_slide, -1):
            if self.snapshots[i].in_borders(event.x, event.y):
                #self.current_slide = i
                return

    def timer_fired(self):
        if self.is_initializing:
            self.init_GUI()
            self.is_initializing = False
        else:
            self.update_snapshots()
            # Update all the buttons
            self.GUI_objects[0].update()

    def redraw_all(self):
        if self.is_initializing: return

        # Draw workspace
        self.workspace.draw(self.canvas)

        self.working_slide.render(
             self.canvas,
             CANVAS_ORIGIN_X,
             CANVAS_ORIGIN_Y)
        if self.current_tool != None:
            self.root.config(cursor = "hand2")
            self.current_tool.draw_object(self.canvas)
        else:
            self.root.config(cursor = "")

        # Draw other things
        self.toolbars[0].draw(self.canvas)
        self.toolbars[1].draw(self.canvas)
        self.timeline.draw(self.canvas)

        # Draw snapshots
        # right stack
        for i in range(self.current_slide+1, len(self.snapshots)):
            self.snapshots[i].draw(self.canvas)

        # left stack
        for i in range(self.current_slide+1):
            self.snapshots[i].draw(self.canvas)

psm = Presimation(SCREEN_WIDTH, SCREEN_HEIGHT)