# SPDX-FileCopyrightText: 2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import subprocess
from pathlib import Path

TEST_VERSIONS = {
    "4.2",
    "4.3",
    "4.4",
    "4.5",
}

# Color codes
RED = "\033[91m"
GREEN = "\033[92m"
INVERSE = "\033[7m"
RESET = "\033[0m"


def input_test_perf() -> bool:
    _input = input(
        "█ TEST PERFORMANCE?\n"
        "\n"
        "[ y ] Yes\n"
        "[ n ] No\n"
        "\n"
        "> "
    )
    return _input.strip().lower() == "y"


def main() -> None:
    use_test_perf = input_test_perf()
    os.system("cls")

    blender_apps = []
    for entry in Path().home().iterdir():
        if entry.is_dir() and entry.name.startswith("blender") and entry.name.split("-")[1] in TEST_VERSIONS:
            blender_apps.append(entry)

    tests = []
    for entry in Path(__file__).parent.iterdir():
        if entry.is_file() and entry.suffix == ".py" and entry.name.startswith("test") and entry.stem != "test_performance":
            tests.append(entry)

    if use_test_perf:
        tests = [Path(__file__).parent / "test_performance.py"]

    print(INVERSE + "BEGIN" + RESET)

    for blender in blender_apps:
        for test in tests:
            cmd = [blender / "blender.exe", "-b", "-P", test]
            proc = subprocess.run(cmd, capture_output=True)
            if proc.returncode:
                print(f"{RED + blender.name} {test.stem} {INVERSE}FAILED{RESET}")
                print(proc.stderr.decode().strip())
                return
            else:
                print(f"{blender.name} {test.stem} {GREEN + INVERSE}PASSED{RESET}")

    print(INVERSE + "END" + RESET)


main()
input()
