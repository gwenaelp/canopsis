import unittest
import cconfiguration
import os.path
import shutil

WATCHER_NAME = 'test'
TEST_FILE = 'cconfiguration.conf'


class CconfigurationTest(unittest.TestCase):

    def setUp(self):
        self.configuration_manager = cconfiguration.ConfigurationManager()
        self.file_path = self.configuration_manager.get_file_path(TEST_FILE)
        open(self.file_path, 'w+').close()
        self.has_been_updated = False

    def tearDown(self):
        self.configuration_manager.stop()

    def _watch(self, src_path):
        self.has_been_updated = True

    def testWatcher(self):

        self.assertFalse(self.has_been_updated)

        self.configuration_manager.register_watcher(
            self._watch, WATCHER_NAME, TEST_FILE)

        self.assertFalse(self.has_been_updated)

        self.has_been_updated = False

        self.configuration_manager.register_watcher(
            self._watch, WATCHER_NAME, TEST_FILE, cconfiguration.ONCE_AUTO)

        self.assertTrue(self.has_been_updated)

        self.configuration_manager.start()

        self.has_been_updated = False

        import time

        with open(self.file_path, 'w+') as test_file:

            time.sleep(0.1)

            self.assertTrue(self.has_been_updated)

        self.has_been_updated = False

        with open(self.file_path, 'w+') as test_file:

            test_file.write('test')

            time.sleep(0.1)

            self.assertTrue(self.has_been_updated)

        self.has_been_updated = False

        shutil.copy(self.file_path, self.file_path+'2')

        os.rename(self.file_path+'2', self.file_path)

        time.sleep(0.1)

        self.assertTrue(self.has_been_updated)

if __name__ == '__main__':
    unittest.main()
