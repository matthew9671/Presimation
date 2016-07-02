# Edited from CMU 15-112 F15 course website
from tkinter import *

class Animation(object):

    DELAY = 10
    # Override these methods when creating your own animation
    def mouse_down(self, event): pass
    def mouse_up(self,event):pass
    def mouse_move(self,event):pass
    def timer_fired(self): pass
    def init(self): pass
    def redraw_all(self): pass

    # We are not using these yet
    # When we use them we should change their names for consistency
    def keyPressed(self, event): pass
    def keyReleased(self,event):pass
    
    # Call app.run(width,height) to get your app started
    def run(self, width = 800, height = 600):
        # create the root and the canvas
        root = Tk()
        root.title("Presimation(Demo)")
        m1 = PanedWindow()
        m1.pack(fill=BOTH, expand = 1)
        self.width = width
        self.height = height
        self.canvas = Canvas(root, width = width, height = height)
        self.canvas.pack()
        self.toolbar = Canvas(root, width=width/2, height=height)
        self.toolbar
        m1.add(self.canvas)
        self.window = m1

        # set up events
        def redrawAllWrapper():
            self.canvas.delete(ALL)
            self.redraw_all()
            self.canvas.update()

        def keyPressedWrapper(event):
            self.keyPressed(event)
            redrawAllWrapper()

        root.bind("<Key>", keyPressedWrapper)
        root.bind("<KeyRelease>", self.keyReleased)

        root.bind("<Button-1>", self.mouse_down)
        root.bind("<Motion>", self.mouse_move)
        root.bind("<B1-ButtonRelease>", self.mouse_up)

        # set up timerFired events
        self.timerFiredDelay = Animation.DELAY # milliseconds
        def timerFiredWrapper():
            self.timer_fired()
            redrawAllWrapper()
            # pause, then call timerFired again
            self.canvas.after(self.timerFiredDelay, timerFiredWrapper)
            
        # init and get timerFired running
        self.init()
        timerFiredWrapper()
        # and launch the app
        root.mainloop()
        print("Bye")



