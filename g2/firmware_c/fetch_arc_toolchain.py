#!/usr/bin/env python3
"""Fetch the pinned public ARC compiler into ignored build storage."""
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[2]
CONFIG = json.loads(Path(__file__).with_name("arc-toolchain.json").read_text())


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main():
    compiler = ROOT / CONFIG["tool_path"] / "bin/arc-elf32-gcc"
    if compiler.is_file() and sha256(compiler) == CONFIG["compiler_sha256"]:
        print("Pinned ARC compiler already present")
        return
    archive = ROOT / CONFIG["archive_path"]
    archive.parent.mkdir(parents=True, exist_ok=True)
    if not archive.is_file():
        temporary = archive.with_suffix(archive.suffix + ".download")
        subprocess.run(["curl", "--fail", "--location", "--silent", "--show-error",
                        "--output", str(temporary), CONFIG["download_url"]], check=True)
        if sha256(temporary) != CONFIG["archive_sha256"]:
            raise RuntimeError("ARC release download checksum mismatch")
        temporary.replace(archive)
    if sha256(archive) != CONFIG["archive_sha256"]:
        raise RuntimeError("ARC release archive checksum mismatch")
    with tarfile.open(archive) as package:
        package.extractall(archive.parent / "toolchain", filter="data")
    if not compiler.is_file() or sha256(compiler) != CONFIG["compiler_sha256"]:
        raise RuntimeError("Extracted ARC compiler does not match the pinned release")
    print("Pinned ARC compiler verified and extracted")


if __name__ == "__main__":
    main()
