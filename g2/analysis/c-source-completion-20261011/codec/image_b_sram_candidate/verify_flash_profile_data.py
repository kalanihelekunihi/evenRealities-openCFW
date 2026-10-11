#!/usr/bin/env python3
"""Check typed image-B flash configuration fields against authenticated payload."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
STOCK = ROOT / "g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage2.bin"
OBJECT = HERE / "build/backup_flash_profile_data.o"
TOOL = ROOT / "g2/build/offline-nationalchip-dsp-c-compiler-successor-20261009T195245Z/toolchain"


def main():
    with tempfile.TemporaryDirectory(dir=OBJECT.parent) as tmp:
        out = Path(tmp)
        cmd = ["docker", "run", "--rm", "--network=none", "--read-only",
               "--platform", "linux/amd64",
               "--mount", f"type=bind,src={TOOL},dst=/tool,readonly",
               "--mount", f"type=bind,src={OBJECT.parent},dst=/build,readonly",
               "--mount", f"type=bind,src={out},dst=/out",
               "opencfw/iar-base:10.10.2-local",
               "/tool/bin/csky-abiv2-elf-objcopy",
               "--dump-section", ".rodata=/out/data.bin",
               "--dump-section", ".rodata.str1.4=/out/strings.bin",
               "/build/" + OBJECT.name, "/out/copied.o"]
        subprocess.run(cmd, check=True)
        compiled = (out / "data.bin").read_bytes()
        strings = (out / "strings.bin").read_bytes()
    stock = STOCK.read_bytes()
    checks = []
    for address, object_offset, size in [(0x20016dfc, 0x12c, 40),
                                         (0x20016e24, 0xf4, 56),
                                         (0x20016e5c, 0xac, 72)]:
        expected = stock[address - 0x20003000:address - 0x20003000 + size]
        actual = compiled[object_offset:object_offset + size]
        if expected != actual:
            raise AssertionError(f"protection levels differ at {address:#x}")
        checks.append({"address": hex(address), "size": size,
                       "sha256": hashlib.sha256(expected).hexdigest()})
    for index, name in enumerate(["p25q21l", "p25q40l", "p25q80l",
                                  "en25s20a", "en25s40a", "zb25wq80a"]):
        native = stock[0x20016ea4 - 0x20003000 + index * 24:
                       0x20016ea4 - 0x20003000 + (index + 1) * 24]
        source = compiled[4 + index * 24:4 + (index + 1) * 24]
        if native[4:] != source[4:]:
            raise AssertionError(f"profile fields differ at index {index}")
        name_address = int.from_bytes(native[:4], "little")
        name_offset = name_address - 0x10003000
        if not stock[name_offset:].startswith(name.encode() + b"\0"):
            raise AssertionError(f"native profile name differs: {name}")
        if name.encode() + b"\0" not in strings:
            raise AssertionError(f"compiled profile name missing: {name}")
    native_end = stock[0x20016ea4 - 0x20003000 + 6 * 24:
                       0x20016ea4 - 0x20003000 + 7 * 24]
    if native_end != compiled[4 + 6 * 24:4 + 7 * 24]:
        raise AssertionError("profile terminator differs")
    receipt = {"image_sha256": hashlib.sha256(stock).hexdigest(),
               "object_sha256": hashlib.sha256(OBJECT.read_bytes()).hexdigest(),
               "protection_tables": checks, "profiles_verified": 6,
               "terminator_verified": True,
               "limit": "Candidate DRAM mapping and final relocated name pointers remain unqualified."}
    path = HERE / "flash-profile-data-receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(path)


if __name__ == "__main__":
    main()
