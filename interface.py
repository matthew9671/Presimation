# The most general GUI object
# Hold shared methods like add children and onclick and stuff
class psm_GUI_object(Object):
    def __init__(self):
        pass

class psm_button(psm_GUI_object):
    def __init__(self, event):
        pass


# A panel for holding stuff
class psm_panel(psm_GUI_object):
    def __init__(self):
        pass

class psm_menu(psm_panel):
    def __init__(self):
        pass
