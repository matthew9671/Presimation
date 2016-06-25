from Animation import Animation
from tkinter import *

import string

DO_NOTHING = lambda: 42

# From course notes
def rgbString(red, green, blue):
    return "#%02x%02x%02x" % (red, green, blue)

class Rect(object):
    def __init__(self, x1, y1, x2, y2, color = "white", border = 0,
        activeFill = None):
        self.resize(x1, y1, x2, y2)
        self.color = color
        self.border = border
        if activeFill == None: self.activeFill = color
        else: self.activeFill = activeFill

    # get the position of the top-left corner
    def get_pos(self):
        return (self.x1,self.y1)

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
            fill = self.color, activefill = self.activeFill)

WORLD = Rect(0,0,0,0)

# The most general GUI object
# Hold shared methods like add children and onclick and stuff
# Can be used as an invisible "panel" that holds and aligns other GUI objects

# ATTENTION: The coordinates (x1, x2, y1, y2) of a GUI object
# are relative to it parent.
# Too get its position relative to the world, use get_pos()
class psm_GUI_object(Rect):
    def __init__(self, x1, y1, x2, y2, 
            color = "white", border = 0, parent = WORLD,activeFill = None):
        super().__init__(x1,y1,x2,y2,color,border,activeFill)
        self.parent = parent
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
        pass

    def draw(self, canvas, activeFill = "white"):
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

# The most general button object
class psm_button(psm_GUI_object):

    DOUBLE_CLICK_INTERVAL = 5

    def __init__(self, x1, y1, x2, y2, color = "white", enabled = True,
                 border = 0, parent = WORLD, 
                 alt_text = "Button", activeFill = "white",
                 click_func = DO_NOTHING, double_click_func = DO_NOTHING,
                 image = None):
        super().__init__(x1,y1,x2,y2,color,border,parent,activeFill)

        # Button states

        # The timer that distinguishes between single and double clicks
        self.timer = 0
        # A button only becomes active when mouse down event occurs
        self.active = False
        # Usually a button is chosen when clicked (mousedown + mouseup)
        self.chosen = False
        self.single_clicked = False

        # Button appearance
        self.alt_text = alt_text
        self.click_func = click_func
        self.double_click_func = double_click_func
        self.image = image

    def set_chosen(self, value):
        self.chosen = value

    def on_click(self):
        self.chosen = True
        self.click_func()

    def on_double_click(self):
        self.double_click_func()

    def on_mouse_down(self, x, y):
        if self.in_borders(x, y):
            self.active = True

    def on_mouse_up(self, x, y):
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
        if self.single_clicked:
            self.timer += 1
            if self.timer > psm_button.DOUBLE_CLICK_INTERVAL:
                self.single_clicked = False

    def draw(self, canvas):
        super().draw(canvas)
        x, y = self.get_center()
        if self.image != None:
            canvas.create_image(x, y, image = self.image)

class psm_toolbar_btn_small(psm_button):

    BUTTON_SIZE = 25
    
    def __init__(self, x, y, tool_name,
                 orientation = "left", toggle = False,
                 color = "white", enabled = True,
                 border = 1, parent = WORLD, 
                 alt_text = "Button", activeFill = "orange",
                 click_func = DO_NOTHING, double_click_func = DO_NOTHING,
                 image = None):
        x1, y1 = x, y
        x2, y2 = x + psm_toolbar_btn_small.BUTTON_SIZE,\
        y + psm_toolbar_btn_small.BUTTON_SIZE
        super().__init__(x1, y1, x2, y2, color, border, parent, activeFill)
        # Should be all-caps
        self.tool_name = tool_name
        # Minor detail: determines which side of the screen the button is on
        # ["left", "right"]
        self.orientation = orientation
        # Determines if the button is an on/off button
        self.toggle = toggle

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
                 alt_text = "Button", activeFill = "white",
                 click_func = DO_NOTHING, double_click_func = DO_NOTHING,
                 image = None):
        x1, y1 = x, y
        x2, y2 = x + psm_toolbar_btn_large.BUTTON_SIZE,\
        y + psm_toolbar_btn_large.BUTTON_SIZE
        super().__init__(x1, y1, x2, y2, color, border, parent, activeFill)
        self.orientation = orientation
        self.primary_tool = None
        self.sub_tools = []

    def on_click(self):
        if self.primary_tool == None:
            raise Exception("No primary tool added!")
        self.primary_tool.on_click()

    def add_sub_tool(self, tool_btn):
        if not isinstance(tool_btn, psm_toolbar_btn_small):
            raise Exception("Subtool should be an instance of\
                psm_toolbar_btn_small")

        # Reposition the newly added small button
        y = psm_toolbar_btn_small.BUTTON_SIZE * len(self.sub_tools)
        if self.orientation == "left":
            x = psm_toolbar_btn_large.BUTTON_SIZE
        else:
            assert(self.orientation == "right")
            x = -psm_toolbar_btn_small.BUTTON_SIZE
        # tool_btn.resize(x, y)
        # Add the button to sub_tools
        self.sub_tools.append(tool_btn)
        #@assert(len(self.subtools) > 0)
        self.primary_tool = self.sub_tools[0]

class psm_panel(psm_GUI_object):
    def __init__(self, x1, y1, x2, y2, 
            color = "white", border = 0, parent = WORLD,activeFill = None):
        super().__init__(x1,y1,x2,y2,color,border,parent,activeFill)

# The menu that pops when an object is selected
class psm_menu(psm_panel):
    def __init__(self):
        pass

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
