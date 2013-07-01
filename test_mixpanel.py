#!/usr/bin/env python
import urllib
import unittest
import mixpanel

class MixpanelTestCase(unittest.TestCase):
    def setUp(self):
        print "set up"

    def tearDown(self):
        print "tear down"

    def test_constructor(self):
        mp = mixpanel.Mixpanel("1234")

    def test_track1(self):
        mp = mixpanel.Mixpanel("1234")
        mp.track("pushed button", {"color": "blue", "weight": "5lbs"})    

if __name__ == "__main__":
    unittest.main()
