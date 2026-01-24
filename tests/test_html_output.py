
import sys
import os
import gzip
import datetime
import unittest
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.scenarios import scenarios
import dl2_reports.report
from dl2_reports.components.base import ReportTreeComponent

real_gzip_compress = gzip.compress

def deterministic_gzip_compress(data, compresslevel=9, *, mtime=None):
    return real_gzip_compress(data, compresslevel, mtime=0)

class MockDatetime(datetime.datetime):
    @classmethod
    def now(cls, tz=None):
        return datetime.datetime(2024, 1, 1, 12, 0, 0)

class TestHTMLOutput(unittest.TestCase):
    maxDiff = None  # Show full diff on failure

    def setUp(self):
        self.expected_dir = os.path.join(os.path.dirname(__file__), 'data', 'expected')

def make_test_function(scenario_name, scenario_func, compress, suffix):
    """Factory to create a test method for a specific scenario."""
    def test_func(self):
        # Patch datetime and gzip to match golden generation
        with patch('dl2_reports.report.datetime.datetime', MockDatetime):
            with patch('dl2_reports.report.gzip.compress', side_effect=deterministic_gzip_compress):
                # Reset component ID counter before each test
                ReportTreeComponent.BASE_ID = 1
                
                report = scenario_func()
                report.compress_visuals = compress
                generated_html = report.compile()
                
                expected_file = os.path.join(self.expected_dir, f"{scenario_name}{suffix}")
                if not os.path.exists(expected_file):
                    self.fail(f"Golden file not found: {expected_file}. Run generate_goldens.py first.")
                
                with open(expected_file, "r", encoding="utf-8") as f:
                    expected_html = f.read()
                
                self.assertEqual(generated_html.strip(), expected_html.strip())
    
    return test_func

# Dynamically add test methods to the class
for name, func in scenarios.items():
    # Compressed test
    test_name_comp = f"test_{name}_compressed"
    setattr(TestHTMLOutput, test_name_comp, make_test_function(name, func, True, "_compressed.html"))
    
    # Uncompressed test
    test_name_uncomp = f"test_{name}_uncompressed"
    setattr(TestHTMLOutput, test_name_uncomp, make_test_function(name, func, False, "_uncompressed.html"))

if __name__ == '__main__':
    unittest.main()
