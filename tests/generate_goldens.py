
import sys
import os
import datetime
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.scenarios import scenarios
import dl2_reports.report
from dl2_reports.components.base import ReportTreeComponent
import gzip

# Mock datetime to ensure consistent outputs
class MockDatetime(datetime.datetime):
    @classmethod
    def now(cls, tz=None):
        return datetime.datetime(2024, 1, 1, 12, 0, 0)

# Mock gzip.compress to use fixed mtime
def mock_gzip_compress(data, compresslevel=9, *, mtime=None):
    return gzip.GzipFile(fileobj=None, mode='wb', compresslevel=compresslevel, mtime=0).write(data) or gzip.compress(data, compresslevel=compresslevel, mtime=0)
    # Actually gzip.compress is just a wrapper around GzipFile. 
    # But recursively calling gzip.compress might cause issues if I patch the original function reference.
    # The real gzip.compress implementation:
    # def compress(data, compresslevel=9, *, mtime=None):
    #     buf = io.BytesIO()
    #     with GzipFile(fileobj=buf, mode='wb', compresslevel=compresslevel, mtime=mtime) as f:
    #         f.write(data)
    #     return buf.getvalue()

    # So I can just use a lambda that calls the REAL gzip.compress with mtime=0.
    # But if I replaced dl2_reports.report.gzip.compress, how do I call the real one?
    # I can capture it before patching.

real_gzip_compress = gzip.compress

def deterministic_gzip_compress(data, compresslevel=9, *, mtime=None):
    return real_gzip_compress(data, compresslevel, mtime=0)

# Patch the datetime module where it is used
# Note: we need to patch 'dl2_reports.report.datetime' because that's what the module uses
def generate():
    output_dir = os.path.join(os.path.dirname(__file__), 'data', 'expected')
    os.makedirs(output_dir, exist_ok=True)
    
    # We need to patch the datetime class inside the datetime module that dl2_reports.report imported
    # But checking the code: "import datetime" in report.py.
    # So we patch dl2_reports.report.datetime.datetime
    
    with patch('dl2_reports.report.datetime.datetime', MockDatetime):
        with patch('dl2_reports.report.gzip.compress', side_effect=deterministic_gzip_compress):
            for name, scenario_func in scenarios.items():
                print(f"Generating golden files for {name}...")
                
                # 1. Compressed
                ReportTreeComponent.BASE_ID = 1
                report = scenario_func()
                report.compress_visuals = True
                html_content = report.compile()
                
                file_path = os.path.join(output_dir, f"{name}_compressed.html")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                
                # 2. Uncompressed
                ReportTreeComponent.BASE_ID = 1
                report = scenario_func()
                report.compress_visuals = False
                html_content = report.compile()
                
                file_path = os.path.join(output_dir, f"{name}_uncompressed.html")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                    
                print(f"Saved {name} (compressed & uncompressed)")

if __name__ == "__main__":
    generate()
