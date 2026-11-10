"""Tests for bibcheck CLI startup edge cases (slot 812)."""

import bibcheck.main as main_module
from bibcheck.main import run


def test_run_with_missing_path_reports_and_returns(capsys):
    assert run(["/nonexistent-path-xyz-123"]) is None
    out = capsys.readouterr().out
    assert "Invalid path" in out


def test_run_with_empty_directory_reports_and_returns(tmp_path, capsys):
    assert run([str(tmp_path)]) is None
    out = capsys.readouterr().out
    assert "No PDF files" in out


def test_module_exposes_console_entry_point():
    assert callable(main_module.run)
