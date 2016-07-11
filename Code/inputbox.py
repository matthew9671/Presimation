import string

class inputBox(psm_GUI_object):

  FLASH_INTERVAL = 5

  def __init__(self, x1, y1, x2, y2):
    super().__init__(x1,y1,x2,y2)
    self.cursor_x = 0    # set the position of the cursor
    self.text = ""
    self.time = 0
    self.cursor_visible = True

  def update(self):
    self.time += 1
    if (self.time == FLASH_INTERVAL)
      self.time = 0
      self.cursor_visible = not self.cursor_visible

  def keyPressed(self, event):
      if (event.keysym == "BackSpace")  # delete the last character
        if (len(self.text) > 0)
          self.text = self.text[:-1]
          self.cursor_x -= 1
      else if (event.keysym == "Return")  # exit the box
        self.is_enabled = False
      else
        self.text += chr(event.keysym)
        self.cursor_x += 1

  def return_value(self):
    return self.text

  def draw(self, canvas):
    super().draw(canvas)
    self.display_text(self, canvas)

  def display_text(self, canvas):
    canvas.create_text(self.x1,
                       self.y1 + self.height / 2,
                       text = self.text,
                       anchor = W,
                       fill = "black",
                       font = "Gothic 10")
