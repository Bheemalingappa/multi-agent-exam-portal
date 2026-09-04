import unittest

try:
    from app.pipeline.test_runner import HiddenTestRunner
    HAS_TEST_RUNNER = True
except (ImportError, ModuleNotFoundError):
    HAS_TEST_RUNNER = False

class TestHiddenTestRunner(unittest.TestCase):

    def test_normalize_output(self):
        if not HAS_TEST_RUNNER:
            self.skipTest("Docker / Celery dependencies not available on host environment.")
        raw_crlf = "Output line 1\r\nOutput line 2\r\n\n"
        normalized = HiddenTestRunner.normalize_output(raw_crlf)
        self.assertEqual(normalized, "Output line 1\nOutput line 2")

    def test_normalize_output_whitespace_stripping(self):
        if not HAS_TEST_RUNNER:
            self.skipTest("Docker / Celery dependencies not available on host environment.")
        raw = "   [0, 1]   \n\n"
        normalized = HiddenTestRunner.normalize_output(raw)
        self.assertEqual(normalized, "[0, 1]")

if __name__ == "__main__":
    unittest.main()
