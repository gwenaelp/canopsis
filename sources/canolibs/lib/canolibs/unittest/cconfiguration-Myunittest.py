import unittest
import cconfiguration
import os.path

WATCHER_NAME = 'test'
TEST_FILE = 'cconfiguration.conf'
TEST_FILE_PATH = os.path.join(
    cconfiguration.CONFIGURATION_DIRECTORY, TEST_FILE)


class CconfigurationTest(unittest.TestCase):

    def setUp(self):
        self.configuration_manager = cconfiguration.ConfigurationManager()
        self.has_been_updated = False

    def tearDown(self):
        self.configuration_manager.stop()

    def _watch(self, src_path):
        self.has_been_updated = True

    def testWatcher(self):

        self.assertFalse(self.has_been_updated)

        self.configuration_manager.register_watcher(
            WATCHER_NAME, self._watch, TEST_FILE)

        self.assertFalse(self.has_been_updated)

        self.has_been_updated = False

        self.configuration_manager.register_watcher(
            WATCHER_NAME, self._watch, TEST_FILE, cconfiguration.ONCE_AUTO)

        self.assertTrue(self.has_been_updated)

        self.configuration_manager.start()

        if os.path.exists(TEST_FILE_PATH):
            os.remove(TEST_FILE_PATH)

        self.has_been_updated = False

        self.assertFalse(self.has_been_updated)

        with open(TEST_FILE_PATH, 'w+') as test_file:

            self.assertTrue(self.has_been_updated)

            self.has_been_updated = False

            test_file.write('test')

        self.assertTrue(self.has_been_updated)

if __name__ == '__main__':
    unittest.main()
