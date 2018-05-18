import xml.etree.ElementTree as ET
from shapes import Line, Rect, Polygon

class Drawing:
    # Either submit the code in plain text or submit a filename to read
    def __init__(self, filename=False, raw=False):
        if filename:
            f = open(filename, 'r')  # We only need reading permissions
            contents = f.read()
            f.close()

            # Remove some metadata illustrator generates that isn't really
            # standard XML
            contents = contents.replace(
                'xmlns="http://www.w3.org/2000/svg"', '')
            contents = contents.replace(
                'xmlns:xlink="http://www.w3.org/1999/xlink"', '')

            self.root = ET.fromstring(contents)
        elif raw:
            self.root = ET.fromstring(raw)

        self.processedroot = []
        self.process(self.root)

    # The actual processing of self.root happens in a dedicated method, that's
    # useful to recursively call the method on a <g> tag (svg tag purely for
    # grouping other tags)
    def process(self, root):
        # We just ignore the tags that aren't interesting for us
        for child in root:
            if child.tag == 'line':
                self.addLine(child)
            elif child.tag == 'rect':
                self.addRect(child)
            elif child.tag == 'polygon':
                self.addPolygon(child)
            elif child.tag == 'g':
                self.process(child)

    def addLine(self, t):
        self.processedroot.append(Line(t.get('x1'), t.get('y1'),
                                       t.get('x2'), t.get('y2')))

    def addRect(self, t):
        rect = Rect(t.get('x'), t.get('y'), t.get('width'), t.get('height'))
        self.processedroot.append(rect)

    def addPolygon(self, t):
        polygon = Polygon(t.get('points'))
        self.processedroot.append(polygon)

    def instructions(self):
        # Use sum() to "flatten" instructions list: [a, b, [c, d]] -> [a, b, c, d]
        instructions = sum([shape.instruction() for shape in self.processedroot], [])
        instructions.append('M 7500 7500')
        return instructions
