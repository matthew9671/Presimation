from Animation import Animation
from tkinter import *

import string

DO_NOTHING = lambda: 42

# From course notes
def rgbString(red, green, blue):
    return "#%02x%02x%02x" % (red, green, blue)

class Rect(object):
    def __init__(self, x1, y1, x2, y2, color = "white", border = 0,
        active_fill = None):
        self.resize(x1, y1, x2, y2)
        self.color = color
        self.border = border
        if active_fill == None: self.active_fill = color
        else: self.active_fill = active_fill

    # get the position of the top-left corner
    def get_pos(self):
        return (self.x1,self.y1)

    # This is very handy
    # Since it can also reposition objects
    # when you leave the last 2 fields empty
    def resize(self, x1, y1, x2 = None, y2 = None):
        self.x1 = x1
        self.y1 = y1
        if x2 != None and y2 != None:
            self.x2 = x2
            self.y2 = y2
            self.width = x2 - x1
            self.height = y2 - y1
        else:
            assert(x2 == None and y2 == None)
            self.x2 = x1 + self.width
            self.y2 = y1 + self.height

    def in_borders(self, x, y):
        x1, y1 = self.get_pos()
        return (x >= x1 and x <= x1 + self.width 
            and y >= y1 and y <= y1 + self.height)

    def constrain_in_borders(self,x,y):
        x1, y1 = self.get_pos()
        if x < x1: x = x1
        elif x > x1 + self.width: x = x1 + self.width
        if y < y1: y = y1
        elif y > y1 + self.height: y = y1 + self.height
        return (x,y)

    def get_center(self):
        return (self.get_pos()[0] + self.width / 2, 
                self.get_pos()[1] + self.height / 2)

    def draw(self,canvas):
        x1, y1 = self.get_pos()
        x2, y2 = x1 + self.width, y1 + self.height
        canvas.create_rectangle(x1, y1, x2, y2,
            fill = self.color, activefill = self.active_fill, 
            width = self.border)

WORLD = Rect(0,0,0,0)

# The most general GUI object
# Hold shared methods like add children and onclick and stuff
# Can be used as an invisible "panel" that holds and aligns other GUI objects

# ATTENTION: The coordinates (x1, x2, y1, y2) of a GUI object
# are relative to it parent.
# Too get its position relative to the world, use get_pos()
class psm_GUI_object(Rect):
    def __init__(self, x1, y1, x2, y2, 
            color = "white", border = 0, parent = WORLD, 
            active_fill = None):
        super().__init__(x1,y1,x2,y2,color,border,active_fill)
        self.parent = parent
        if parent != WORLD: parent.add_child(self)
        self.is_visible = True
        self.is_enabled = True
        self.children = []
        self.mouse_on = False

    # Get the position of the top-left corner
    # Relative to the WORLD
    def get_pos(self):
        parentPos = self.parent.get_pos()
        return (parentPos[0] + self.x1, parentPos[1] + self.y1)

    def add_child(self, child):
        if isinstance(child, psm_GUI_object):
            self.children.append(child)
            child.parent = self
        else:
            raise Exception("Child is not GUI object")

    # Some objects (like buttons) require this to keep track of time
    def update(self):
        for child in self.children:
            child.update()

    def draw(self, canvas, active_fill = "white"):
        super().draw(canvas)
        for child in self.children:
            child.draw(canvas)

    def on_mouse_down(self, x, y):
        for child in self.children:
            child.on_mouse_down(x,y)

    def on_mouse_up(self, x, y):
        for child in self.children:
            child.on_mouse_up(x,y)

    def on_mouse_move(self, x, y):
        for child in self.children:
            # Update the mouse_on field for all children
            if child.in_borders(x, y):
                child.set_mouse_on(True)
            else:
                child.set_mouse_on(False)
            child.on_mouse_move(x, y)

    def set_mouse_on(self, value):
        self.mouse_on = value

class psm_menu_inputbox(psm_GUI_object):
    def __init__(self, x1, y1, x2, y2, field = None, color = "white",
                 border = 0, parent = WORLD,
                 entry_update_func = None):
        super().__init__(x1, y1, x2, y2, color, border, parent)
        self.x1 = x1
        self.y1 = y1
        self.width = self.x2 - self.x1
        self.height = self.y2 - self.y1
        self.generated = False
        self.text = None
        assert(field != None)
        self.field = field
        assert(entry_update_func != None)
        self.entry_update = entry_update_func
        self.sv = StringVar()
        self.sv.trace("w", lambda name, index, mode, 
            var = self.sv, field_name = self.field.name:
                self.entry_update(var, field_name))

    def hide(self):
        if self.generated:
            self.text.place_forget()

    def draw(self, canvas):
        if not self.generated:
            self.text = Entry(canvas, textvariable = self.sv)
            self.generated = True
            
        abs_x, abs_y = self.get_pos()
        self.text.place(x = abs_x,
                        y = abs_y,
                        width = self.width,
                        height = self.height)


# The most general button object
class psm_button(psm_GUI_object):

    DOUBLE_CLICK_INTERVAL = 10

    def __init__(self, x1, y1, x2, y2, color = "white", enabled = True,
                 border = 1, parent = WORLD, 
                 alt_text = "Button", active_fill = "white", 
                 click_func = DO_NOTHING, double_click_func = DO_NOTHING,
                 image = None, active_outline = None):
        super().__init__(x1,y1,x2,y2,color,border,parent,active_fill)

        # Button states

        # The timer that distinguishes between single and double clicks
        self.timer = 0
        # A button only becomes active when mouse down event occurs
        self.active = False
        # Usually a button is chosen when clicked (mousedown + mouseup)
        self.chosen = False
        self.single_clicked = False

        self.click_func = click_func
        self.double_click_func = double_click_func

        # Button appearance
        self.alt_text = alt_text
        self.image = image
        self.active_outline = active_outline

    def set_chosen(self, value):
        self.chosen = value

    def on_click(self):
        self.chosen = True
        self.click_func()

    def on_double_click(self):
        self.double_click_func()

    def on_mouse_down(self, x, y):
        super().on_mouse_down(x, y)
        if self.in_borders(x, y):
            self.active = True

    def on_mouse_up(self, x, y):
        super().on_mouse_up(x, y)
        if self.active:
            self.active = False
            if self.in_borders(x, y):
                if not self.single_clicked:
                    self.on_click()
                    self.single_clicked = True
                else:
                    # Notice that the second click in a double click
                    # does not trigger on_click() again
                    self.on_double_click()
                    self.single_clicked = False

    def set_mouse_on(self, value):
        super().set_mouse_on(value)
        # When mouse leaves the button it becomes deactivated
        if not value: self.active = False

    def update(self):
        super().update()
        if self.single_clicked:
            self.timer += 1
            if self.timer > psm_button.DOUBLE_CLICK_INTERVAL:
                # Debug only
                #print("Just a single click")
                self.single_clicked = False
                self.timer = 0

    def draw(self, canvas):
        super().draw(canvas)
        x, y = self.get_center()
        if self.image != None:
            canvas.create_image(x, y, image = self.image)

class psm_toolbar_btn_small(psm_button):

    BUTTON_SIZE = 25
    
    def __init__(self, x, y, tool_name, toggle = False,
                 color = "white", enabled = True,
                 border = 1, parent = WORLD, 
                 alt_text = "Button", active_fill = "orange",
                 click_func = DO_NOTHING, double_click_func = DO_NOTHING,
                 image = None):
        x1, y1 = x, y
        x2, y2 = x + psm_toolbar_btn_small.BUTTON_SIZE,\
        y + psm_toolbar_btn_small.BUTTON_SIZE
        super().__init__(x1, y1, x2, y2, color, enabled,
                 border, parent, 
                 alt_text, active_fill,
                 click_func, double_click_func,
                 image)
        # Should be all-caps
        self.tool_name = tool_name

        # Determines if the button is an on/off button
        self.toggle = toggle
        assert(isinstance(parent,psm_toolbar_btn_large))
        parent.add_sub_tool(self)

    def on_click(self):
        # The click_func should be something like select_tool(tool_name)
        if self.toggle:
            self.chosen = not self.chosen
        else:
            self.chosen = True
        self.click_func()

# Large buttons represents groups of tools that have a similar function
class psm_toolbar_btn_large(psm_button):

    BUTTON_SIZE = 100

    def __init__(self, x, y, toolset_name, orientation = "left",
                 color = "white", enabled = True,
                 border = 4, parent = WORLD, 
                 alt_text = "Button", active_fill = "white",
                 click_func = DO_NOTHING, double_click_func = DO_NOTHING,
                 image = None):
        x1, y1 = x, y
        x2, y2 = x + psm_toolbar_btn_large.BUTTON_SIZE,\
        y + psm_toolbar_btn_large.BUTTON_SIZE
        super().__init__(x1, y1, x2, y2, color, enabled,
                 border, parent, 
                 alt_text, active_fill,
                 click_func, double_click_func,
                 image)
        # Determines which side of the screen the button is on
        self.orientation = orientation
        self.primary_tool = None
        self.sub_tools = []

    def on_click(self):
        if self.primary_tool == None:
            raise Exception("No primary tool added!")
        self.primary_tool.on_click()

    def add_sub_tool(self, tool_btn):
        if not isinstance(tool_btn, psm_toolbar_btn_small):
            raise Exception(
                "Subtool should be an instance of psm_toolbar_btn_small")
        self.add_child(tool_btn)

        # Reposition the newly added small button
        y = psm_toolbar_btn_small.BUTTON_SIZE * len(self.sub_tools)
        if self.orientation == "left":
            x = psm_toolbar_btn_large.BUTTON_SIZE
        else:
            assert(self.orientation == "right")
            x = -psm_toolbar_btn_small.BUTTON_SIZE
        tool_btn.resize(x, y)
        # Add the button to sub_tools
        self.sub_tools.append(tool_btn)
        #@assert(len(self.subtools) > 0)
        self.primary_tool = self.sub_tools[0]

class psm_object_handle(psm_button):

    RADIUS = 4
    BORDER = 3
    COLOR = "cyan"
    BORDER_COLOR = rgbString(240, 240, 240)
    BORDER_ACTIVE = "red"

    def __init__(self, x, y, parent, return_func):
        r = psm_object_handle.RADIUS
        super().__init__(x - r, y - r , x + r, y + r,
                       parent = parent,
                       color = psm_object_handle.COLOR,
                       active_outline = psm_object_handle.BORDER_ACTIVE,
                       alt_text = None, active_fill = None)
        self.return_func = return_func
        self.on_drag = False

    # This function moves the button with respect to to its center 
    def move_to(self, x, y):
        r = psm_object_handle.RADIUS
        self.x1 = x - r
        self.x2 = x + r
        self.y1 = y - r
        self.y2 = y + r

    def draw(self, canvas):
        r = psm_object_handle.RADIUS
        x, y = self.get_center()
        x1 = x - r
        x2 = x + r
        y1 = y - r
        y2 = y + r
        canvas.create_oval(x1, y1, x2, y2,
            fill = self.color, width = psm_object_handle.BORDER,
            outline = psm_object_handle.BORDER_COLOR,
            activeoutline = self.active_outline)

    def on_mouse_down(self, x, y):
        if self.in_borders(x, y):
            self.on_drag = True
            # Report the position of the mouse to the user object
            self.return_func(x, y)

    def on_mouse_up(self, x, y):
        self.on_drag = False

    def on_mouse_move(self, x, y):
        if self.on_drag: self.return_func(x, y)

# The event listener is not used as gui element
# It's just a tool for us to get double clicks events
class psm_double_click_listener(psm_button):
    def __init__(self, double_click_func):
        super().__init__(0,0,0,0,
                         double_click_func = double_click_func)

    def in_borders(self, x, y):
        return True

# TODO: Write this
class psm_menu_icon(psm_button): pass

class Test(Animation):
    def __init__(self):
        self.buttons=[]
        self.buttons.append(psm_button(20,20,100,100,"red"))
        self.run()

    def redrawAll(self):
        for i in range(len(self.buttons)):
            self.buttons[i].draw(self.canvas)

    def mouseMotion(self,event):pass

    def mousePressed(self,event):pass

    def keyPressed(self,event):pass

    def leftMouseReleased(self,event):pass
