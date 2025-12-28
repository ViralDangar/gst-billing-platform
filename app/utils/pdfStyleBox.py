from reportlab.platypus import Flowable
from reportlab.lib import colors

class PillBox(Flowable):
    def __init__(self, width, height, fill_color=colors.black, stroke_color=colors.black):
        super().__init__()
        self.width = width
        self.height = height
        self.radius = height / 2
        self.fill_color = fill_color
        self.stroke_color = stroke_color

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
        c = self.canv
        r = self.radius

        c.setFillColor(self.fill_color)
        c.setStrokeColor(self.stroke_color)

        # roundRect with radius = height/2 gives pill shape
        c.roundRect(0, 0, self.width, self.height, r, stroke=1, fill=1)
