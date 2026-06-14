# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2024-2026 Mikhail Rachinskiy

import subprocess
from pathlib import Path

BL_PATH = Path("~/blender-4.5/blender.exe").expanduser()


def build(src_dir: Path, out_dir: Path) -> None:
    cmd = f"{BL_PATH} --command extension build --source-dir={src_dir} --output-dir={out_dir}"
    subprocess.run(cmd, shell=True, capture_output=True)


def find_by_ext(folder: Path, ext: str) -> str:
    for entry in folder.iterdir():
        if entry.suffix == ext:
            return entry.name

    raise FileNotFoundError


def main() -> None:
    print(" ░ ...")

    current_dir = Path(__file__).parent
    src_dir = current_dir.parent / "source"

    build(src_dir, current_dir)

    zip_name = find_by_ext(current_dir, ".zip")
    input(f" █ {zip_name}\n")


main()
