#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
# Unit tests

# builds on stuff from ImageD11.test.testpeaksearch
"""
import unittest, sys, os, logging
logger = logging.getLogger("testmar345image")
force_build = False

for opts in sys.argv[:]:
    if opts in ["-d", "--debug"]:
        logging.basicConfig(level=logging.DEBUG)
        sys.argv.pop(sys.argv.index(opts))
    elif opts in ["-i", "--info"]:
        logging.basicConfig(level=logging.INFO)
        sys.argv.pop(sys.argv.index(opts))
    elif opts in ["-f", "--force"]:
        force_build = True
        sys.argv.pop(sys.argv.index(opts))
try:
    logger.debug("Tests loaded from file: %s" % __file__)
except:
    __file__ = os.getcwd()

from utilstest import UtilsTest
if force_build:
    UtilsTest.forceBuild()
import fabio
from fabio.mar345image import mar345image

# filename dim1 dim2 min max mean stddev
TESTIMAGES = """example.mar2300     2300 2300 0 999999 180.15 4122.67
                example.mar2300.bz2 2300 2300 0 999999 180.15 4122.67
                example.mar2300.gz  2300 2300 0 999999 180.15 4122.67"""


class testMAR345(unittest.TestCase):
    def setUp(self):
        """
        download images
        """
        self.mar = UtilsTest.getimage("example.mar2300.bz2")[:-4]

    def test_read(self):
        """
        Test the reading of Mar345 images 
        """
        for line in TESTIMAGES.split(os.linesep):
            vals = line.split()
            name = vals[0]
            dim1, dim2 = [int(x) for x in vals[1:3]]
            mini, maxi, mean, stddev = [float(x) for x in vals[3:]]
            obj = mar345image()
            obj.read(os.path.join("testimages", name))

            self.assertAlmostEqual(mini, obj.getmin(), 2, "getmin")
            self.assertAlmostEqual(maxi, obj.getmax(), 2, "getmax")
            self.assertAlmostEqual(mean, obj.getmean(), 2, "getmean")
            self.assertAlmostEqual(stddev, obj.getstddev(), 2, "getstddev")
            self.assertEqual(dim1, obj.dim1, "dim1")
            self.assertEqual(obj.dim1, obj.dim2, "dim2!=dim1")



def test_suite_all_mar345():
    testSuite = unittest.TestSuite()
    testSuite.addTest(testMAR345("test_read"))
    return testSuite

if __name__ == '__main__':
    mysuite = test_suite_all_mar345()
    runner = unittest.TextTestRunner()
    runner.run(mysuite)
