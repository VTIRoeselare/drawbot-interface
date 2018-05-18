import unittest
import xml.etree.ElementTree as ET
import drawing
import shapes

class TestLine(unittest.TestCase):
    def test_initialization(self):
        line = drawing.Line(1, 2, '3', '4.00')
        self.assertEqual(line.x1, 1)
        self.assertEqual(line.y1, 2)
        self.assertEqual(line.x2, 3)
        self.assertEqual(line.y2, 4)

    def test_float_arguments(self):
        line = drawing.Line(x1='1.1', y1='2', x2=3.14, y2=4)
        self.assertEqual(line.x1, 1.1)
        self.assertEqual(line.y1, 2)
        self.assertEqual(line.x2, 3.14)
        self.assertEqual(line.y2, 4)

    def test_equality_method(self):
        l1 = drawing.Line(0, 0, 0, 0)
        l2 = drawing.Line('0', 0, 0, 0)
        self.assertEqual(l1, l2)

        l2.x2 = 5
        self.assertNotEqual(l1, l2)

    def test_instruction(self):
        line = drawing.Line(x1=1, y1=2, x2=3, y2=4)
        self.assertEqual(line.instruction(), ['M 10.0 20.0', 'L 30.0 40.0'])


class TestRect(unittest.TestCase):
    def test_initialization(self):
        r = drawing.Rect(1, 2, '3', '4.00')
        self.assertEqual(r.x, 1)
        self.assertEqual(r.y, 2)
        self.assertEqual(r.width, 3)
        self.assertEqual(r.height, 4)

    def test_instruction(self):
        instructions = drawing.Rect(x=0, y=0, height=5, width=5).instruction()
        self.assertListEqual(instructions, [
            'M 0.0 0.0',
            'L 50.0 0.0',
            'L 50.0 50.0',
            'L 0.0 50.0',
            'L 0.0 0.0'
        ])

class TestDrawing(unittest.TestCase):
    def test_parsed_root(self):
        d = drawing.Drawing(filename='./fixtures/tests-fixture.svg')
        self.assertIsInstance(d.root, ET.Element)

    def test_string_initialization(self):
        fixture = '''<?xml version="1.0" encoding="utf-8"?>
            <svg height="300" width="300"><title>Example image</title>
            <line class="st0" x1="2000" y1="2000" x2="3000" y2="3000"/>
            </svg>'''
        d = drawing.Drawing(raw=fixture)
        self.assertEqual(len(d.processedroot), 1)

    def test_empty_initialization(self):
        drawing.Drawing(raw='<svg></svg>')
        with self.assertRaises(AttributeError):
            drawing.Drawing(raw='')

    # Empty files should just send the drawbot to (750, 750)
    def test_empty_instructions(self):
        d = drawing.Drawing(raw='<svg></svg>')
        self.assertEqual(d.instructions(), ['M 7500 7500'])

    def test_ignores_unknown_tags(self):
        d = drawing.Drawing(raw='<svg><title>abc!</title></svg>')
        self.assertEqual(d.instructions(), ['M 7500 7500'])

    def test_file_initialization(self):
        d = drawing.Drawing(filename='./fixtures/tests-fixture.svg')
        self.assertTrue(isinstance(d.processedroot[0], drawing.Rect))

    def test_instructions(self):
        d = drawing.Drawing(filename='./fixtures/tests-fixture.svg')
        expected = [
            'M 0.0 0.0',
            'L 3000.0 0.0',
            'L 3000.0 1000.0',
            'L 0.0 1000.0',
            'L 0.0 0.0',
            'M 0.0 0.0',
            'L 900.0 0.0',
            'L 900.0 900.0',
            'L 0.0 900.0',
            'L 0.0 0.0',
            'M 0.0 0.0',
            'L 500.0 1000.0',
            'M 7500 7500'
        ]
        self.assertEqual(d.instructions(), expected)

    def test_ignores_unknown_args(self):
        fixture = '''<?xml version="1.0" encoding="utf-8"?>
            <svg height="300" width="300"><title>Example image</title>
            <line class="st0" x1="200" y1="200" x2="300" y2="300"/></svg>'''
        d = drawing.Drawing(raw=fixture)
        expected = [
            'M 2000.0 2000.0',
            'L 3000.0 3000.0',
            'M 7500 7500'
        ]
        self.assertEqual(d.instructions(), expected)

    def test_g_grouping(self):
        d = drawing.Drawing(filename='./fixtures/tests-fixture2.svg')
        expected = [
            'M 0.0 0.0',
            'L 3000.0 0.0',
            'L 3000.0 1000.0',
            'L 0.0 1000.0',
            'L 0.0 0.0',
            'M 0.0 0.0',
            'L 900.0 0.0',
            'L 900.0 900.0',
            'L 0.0 900.0',
            'L 0.0 0.0',
            'M 0.0 0.0',
            'L 500.0 1000.0',
            'M 7500 7500'
        ]
        self.assertEqual(d.instructions(), expected)

if __name__ == '__main__':
    unittest.main()
