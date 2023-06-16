import io
from pathlib import Path
from argparse import Namespace

import pytest
from flake8.violation import Violation

from flake8_json_reporter.reporters import FormattedJSON


@pytest.fixture
def snapshot(snapshot):
    snapshot.snapshot_dir = Path(__file__).parent / 'snapshots'
    return snapshot


@pytest.fixture
def formatter(monkeypatch):
    """Return a ``FormattedJSON`` instance which writes to a StringIO buffer."""
    def get_output(self):
        return self.output_fd.getvalue()

    monkeypatch.setattr(FormattedJSON, 'output', property(get_output), raising=False)
    options = Namespace(output_file=None, color=False, tee=False)
    formatter = FormattedJSON(options)
    formatter.output_fd = io.StringIO()
    return formatter


@pytest.fixture
def dummy_violation():
    return Violation(
        code='XXX01',
        filename='main.py',
        line_number=42,
        column_number=80,
        text='    print("Hello, world!")',
        physical_line=42
    )


def run(formatter, violations):
    formatter.start()
    for filename in violations:
        formatter.beginning(filename)
        for violation in violations[filename]:
            formatter.format(violation)
        formatter.finished(filename)
    formatter.stop()


def test_no_files(snapshot, formatter):
    run(formatter, {})
    snapshot.assert_match(formatter.output, 'no_files.json')


def test_single_file_no_violations(snapshot, formatter):
    run(formatter, {
        'main.py': []
    })
    snapshot.assert_match(formatter.output, 'single_file_no_violations.json')


def test_multiple_files_no_violations(snapshot, formatter):
    run(formatter, {
        'main.py': [],
        '__init__.py': []
    })
    snapshot.assert_match(formatter.output, 'multiple_files_no_violations.json')


def test_single_file_single_violation(snapshot, formatter, dummy_violation):
    run(formatter, {
        'main.py': [dummy_violation],
    })
    snapshot.assert_match(formatter.output, 'single_file_single_violation.json')


def test_single_file_multiple_violations(snapshot, formatter, dummy_violation):
    run(formatter, {
        'main.py': [dummy_violation, dummy_violation, dummy_violation],
    })
    snapshot.assert_match(formatter.output, 'single_file_multiple_violations.json')


def test_multiple_files_multiple_violations_1(snapshot, formatter, dummy_violation):
    run(formatter, {
        'main.py': [],
        '__init__.py': [dummy_violation, dummy_violation, dummy_violation],
    })
    snapshot.assert_match(formatter.output, 'multiple_files_multiple_violations_1.json')


def test_multiple_files_multiple_violations_2(snapshot, formatter, dummy_violation):
    run(formatter, {
        'main.py': [dummy_violation, dummy_violation, dummy_violation],
        '__init__.py': [],
    })
    snapshot.assert_match(formatter.output, 'multiple_files_multiple_violations_2.json')


def test_multiple_files_multiple_violations_3(snapshot, formatter, dummy_violation):
    run(formatter, {
        'main.py': [dummy_violation, dummy_violation, dummy_violation],
        '__init__.py': [dummy_violation, dummy_violation, dummy_violation],
    })
    snapshot.assert_match(formatter.output, 'multiple_files_multiple_violations_3.json')
