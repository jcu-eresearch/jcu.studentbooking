import unittest
from Testing import ZopeTestCase as ztc

from uwosh.timeslot.tests.base import FunctionalTestCase
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(ztc.FunctionalDocFileSuite(
                      'browser.txt', package='uwosh.timeslot.tests',
                      test_class=FunctionalTestCase))
    return suite
