#!/usr/bin/env python
# coding: utf8

"""
2011: Jerome Kieffer for ESRF.

Unit tests for CBF images based on references images taken from:
http://pilatus.web.psi.ch/DATA/DATASETS/insulin_0.2/

"""
import unittest, sys, os, logging
logger = logging.getLogger("testcbfimage")
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
from fabio.cbfimage import cbfimage
import time

class test_cbfimage_reader(unittest.TestCase):
    """ test cbf image reader """

    def __init__(self, methodName):
        "Constructor of the class"
        unittest.TestCase.__init__(self, methodName)
        testimgdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "testimages")
        self.edf_filename = os.path.join(testimgdir, "run2_1_00148.edf")
        self.cbf_filename = os.path.join(testimgdir, "run2_1_00148.cbf")


    def setUp(self):
        """Download images"""

        UtilsTest.getimage(os.path.basename(self.edf_filename + ".bz2"))
        UtilsTest.getimage(os.path.basename(self.cbf_filename))


    def test_read(self):
        """ check whole reader"""
        times = []
        times.append(time.time())
        cbf = fabio.open(self.cbf_filename)
        times.append(time.time())
        edf = fabio.open(self.edf_filename)
        times.append(time.time())

        self.assertAlmostEqual(0, abs(cbf.data - edf.data).max())
        logger.info("Reading CBF took %.3fs whereas the same EDF took %.3fs" % (times[1] - times[0], times[2] - times[1]))

    def test_byte_offset(self):
        """ check byte offset algorythm"""
        cbf = fabio.open(self.cbf_filename)
        starter = "\x0c\x1a\x04\xd5"
        startPos = cbf.cif["_array_data.data"].find(starter) + 4
        data = cbf.cif["_array_data.data"][ startPos: startPos + int(cbf.header["X-Binary-Size"])]
        startTime = time.time()
        numpyRes = cbfimage.analyseNumpy(data, size=cbf.dim1 * cbf.dim2)
        tNumpy = time.time() - startTime
        logger.info("Timing for Numpy method : %.3fs" % tNumpy)

#        startTime = time.time()
#        weaveRes = cbfimage.analyseWeave(data, size=cbf.dim1 * cbf.dim2)
#        tWeave = time.time() - startTime
#        delta = abs(numpyRes - weaveRes).max()
#        self.assertAlmostEqual(0, delta)
#        logger.info("Timing for Weave method : %.3fs, max delta=%s" % (tWeave, delta))

        startTime = time.time()
        pythonRes = cbfimage.analysePython(data, size=cbf.dim1 * cbf.dim2)
        tPython = time.time() - startTime
        delta = abs(numpyRes - pythonRes).max()
        self.assertAlmostEqual(0, delta)
        logger.info("Timing for Python method : %.3fs, max delta= %s" % (tPython, delta))

        from fabio.byte_offset import analyseCython
        startTime = time.time()
        cythonRes = analyseCython(stream=data, size=cbf.dim1 * cbf.dim2)
        tCython = time.time() - startTime
        delta = abs(numpyRes - cythonRes).max()
        self.assertAlmostEqual(0, delta)
        logger.info("Timing for Cython method : %.3fs, max delta= %s" % (tCython, delta))


def test_suite_all_cbf():
    testSuite = unittest.TestSuite()
    testSuite.addTest(test_cbfimage_reader("test_read"))
    testSuite.addTest(test_cbfimage_reader("test_byte_offset"))
    return testSuite

if __name__ == '__main__':

    mysuite = test_suite_all_cbf()
    runner = unittest.TextTestRunner()
    runner.run(mysuite)

