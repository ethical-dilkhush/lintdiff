import json
import subprocess
import sys
from pathlib import Path

import lintdiff


def _write_report(path: Path, issues):
    path.write_text(json.dumps(issues), encoding="utf-8")


def test_added_rule_is_reported():
    before = {
        "files": [
            {
                "path": "a.py",
                "issues": [{"path": "a.py", "line": 1, "code": "E101", "message": "old"}],
            }
        ]
    }
    after = {
        "files": [
            {
                "path": "a.py",
                "issues": [
                    {"path": "a.py", "line": 1, "code": "E101", "message": "old"},
                    {"path": "a.py", "line": 2, "code": "F401", "message": "new"},
                ],
            }
        ]
    }
    before_path = Path("/tmp") / "lintdiff-before.json"
    after_path = Path("/tmp") / "lintdiff-after.json"
    _write_report(before_path, before)
    _write_report(after_path, after)
    out = subprocess.check_output([sys.executable, "-m", "lintdiff", str(before_path), str(after_path)], text=True)
    assert "F401" in out
    assert "E101" not in out


def test_removed_rule_is_reported():
    before = {
        "files": [
            {
                "path": "a.py",
                "issues": [{"path": "a.py", "line": 1, "code": "E101", "message": "old"}],
            }
        ]
    }
    after = {"files": [{"path": "a.py", "issues": []}]}
    before_path = Path("/tmp") / "lintdiff-before-removed.json"
    after_path = Path("/tmp") / "lintdiff-after-removed.json"
    _write_report(before_path, before)
    _write_report(after_path, after)
    out = subprocess.check_output([sys.executable, "-m", "lintdiff", str(before_path), str(after_path)], text=True)
    assert "E101" in out


def test_malformed_report_returns_nonzero():
    bad = Path("/tmp") / "lintdiff-bad.json"
    bad.write_text("{not-json}", encoding="utf-8")
    proc = subprocess.run([sys.executable, "-m", "lintdiff", str(bad), str(bad)], capture_output=True, text=True)
    assert proc.returncode == 1


def test_no_changes_returns_message():
    report = {
        "files": [
            {
                "path": "a.py",
                "issues": [{"path": "a.py", "line": 1, "code": "E101", "message": "same"}],
            }
        ]
    }
    before_path = Path("/tmp") / "lintdiff-before-same.json"
    after_path = Path("/tmp") / "lintdiff-after-same.json"
    _write_report(before_path, report)
    _write_report(after_path, report)
    out = subprocess.check_output([sys.executable, "-m", "lintdiff", str(before_path), str(after_path)], text=True)
    assert "No lint rule changes detected" in out


def test_only_added_filters_output():
    before = {
        "files": [
            {
                "path": "a.py",
                "issues": [{"path": "a.py", "line": 1, "code": "E101", "message": "old"}],
            }
        ]
    }
    after = {
        "files": [
            {
                "path": "a.py",
                "issues": [
                    {"path": "a.py", "line": 1, "code": "E101", "message": "old"},
                    {"path": "a.py", "line": 2, "code": "F401", "message": "new"},
                ],
            }
        ]
    }
    before_path = Path("/tmp") / "lintdiff-before-filter.json"
    after_path = Path("/tmp") / "lintdiff-after-filter.json"
    _write_report(before_path, before)
    _write_report(after_path, after)
    out = subprocess.check_output([sys.executable, "-m", "lintdiff", "--only", "added", str(before_path), str(after_path)], text=True)
    assert "F401" in out
    assert "E101" not in out
