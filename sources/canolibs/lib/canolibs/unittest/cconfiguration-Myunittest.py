import unittest
import cconfiguration
import os
import time

TEST_FILE = 'cconfiguration.conf'
TEST_FILE_PATH = os.path.join(
    cconfiguration.CONFIGURATION_DIRECTORY, TEST_FILE)


class CconfigurationTest(unittest.TestCase):

    def setUp(self):
        cconfiguration.manual_reconfiguration(False)
        self.has_been_updated = False

    def _observes(self, src_path):
        self.has_been_updated = True

    def testObserver(self):

        cconfiguration.register_observer(TEST_FILE, self._observes, True)

        self.assertTrue(self.has_been_updated)

        self.has_been_updated = False

        cconfiguration.register_observer(TEST_FILE, self._observes)

        self.assertFalse(self.has_been_updated)

        if os.path.exists(TEST_FILE_PATH):
            os.remove(TEST_FILE_PATH)

        with open(TEST_FILE_PATH, 'w') as test_file:
            test_file.write('test')

        #time.sleep(.5)

        self.assertTrue(self.has_been_updated)

        pass

if __name__ == '__main__':
    unittest.main()
