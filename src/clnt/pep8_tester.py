"""
Auto tester. Author: Ayelet Mashiah.
Runs PEP8 style checks on Python files in a folder.
"""
import glob
import os
import sys

import pep8

# Glob pattern for Python files in current directory
PYTHON_GLOB_PATTERN = ".\\*.py"


def test_pep8(folder, files):
    """Run PEP8 style guide on given files; skip the test script itself."""
    tst_f_name = os.path.basename(sys.argv[0])
    files.remove(".\\" + tst_f_name)
    print("tested files", files)
    checker = pep8.StyleGuide()
    checker.check_files(files)


def list_files(folder):
    """Return list of Python file paths in folder (current dir only)."""
    lst = glob.glob(PYTHON_GLOB_PATTERN)
    return lst


def test_folder(folder_name):
    """List Python files in folder and run PEP8 on them; output to stdout."""
    new_tested_files = list_files(folder_name)
    test_pep8(folder_name, new_tested_files)


def main():
    """Run PEP8 tests on current directory Python files."""
    test_folder(".")


if __name__ == '__main__':
    main()
