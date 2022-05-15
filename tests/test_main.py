import csv
import os
from tempfile import TemporaryDirectory

import pytest
from click.testing import CliRunner
from qdc_converter import main as converter_main
from qdc_converter.utils import get_files_recursively


@pytest.fixture(scope='module')
def runner():
    return CliRunner()


def compare_two_csv(csv_one, csv_two):
    """Compare 2 CSV files.

    Args:
        csv_one (str): Path to 1st csv.
        csv_two (str): Path to 2nd csv.
    """
    with open(csv_one, 'r') as f1, open(csv_two, 'r') as f2:
        data1 = list(csv.reader(f1))
        data2 = list(csv.reader(f2))
        assert len(data1) == len(data2)
        for v1, v2 in zip(data1, data2):
            assert v1 == v2


def test_main(runner):
    """Convert test qdc and compare csv output with validated sample."""
    with TemporaryDirectory() as tmpdir:
        result_csv = os.path.join(tmpdir, 'output.csv')
        here = os.path.dirname(os.path.abspath(__file__))
        test_path = os.path.join(here, 'data', 'main')

        csv_files = get_files_recursively(test_path, '.csv')
        qdc_files = get_files_recursively(test_path, '.qdc')

        assert len(csv_files) == 1
        csv_sample_file = csv_files[0]

        assert qdc_files
        qdc_path = os.path.dirname(qdc_files[0])

        runner.invoke(converter_main, [
            '--qdc-folder-path', qdc_path,
            '--output-path', result_csv,
            '--layer', '1',
            '--quite',
        ])

        # Compare output with sample
        compare_two_csv(csv_sample_file, result_csv)
