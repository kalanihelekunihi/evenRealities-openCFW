#!/usr/bin/env python3
"""Execute the locked scatter expander and extract the runtime NOR profile bytes."""
import argparse
import hashlib
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
spec = importlib.util.spec_from_file_location(
    "startup_verify", ROOT / "g2/components/bootloader/startup/verify.py")
startup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(startup)
v = startup.v
v.ENTRIES["expand_record"] = 0x415326

RECORD = 0x433104
STREAM = 0x4341C0
STREAM_SIZE = 625
DESTINATION = 0x20000000
EXPANDED_SIZE = 1371
PROFILE_OFFSET = 0x244
PROFILE_SIZE = 36 * 6


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    assert v.sha(v.BLOB) == v.SHA
    image = v.BLOB.read_bytes()
    m = startup.Machine()
    m.cpu.mem_write(RECORD, image[RECORD - v.BASE:RECORD - v.BASE + 12])
    m.cpu.mem_write(STREAM, image[STREAM - v.BASE:STREAM - v.BASE + STREAM_SIZE])
    result = m.run("expand_record", [RECORD, 0])
    expanded = bytes(m.cpu.mem_read(DESTINATION, EXPANDED_SIZE))
    table = expanded[PROFILE_OFFSET:PROFILE_OFFSET + PROFILE_SIZE]
    assert len(table) == PROFILE_SIZE
    assert result["return"] == RECORD + 12
    assert m.cpu.reg_read(v.a.UC_ARM_REG_R3) == STREAM + STREAM_SIZE
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(table)
    print({"status": "PASS", "locked_sha256": v.SHA,
           "scatter_record": hex(RECORD), "compressed_stream": [hex(STREAM), hex(STREAM + STREAM_SIZE)],
           "destination": [hex(DESTINATION), hex(DESTINATION + EXPANDED_SIZE)],
           "profile_bytes": [hex(DESTINATION + PROFILE_OFFSET), PROFILE_SIZE],
           "expanded_sha256": hashlib.sha256(expanded).hexdigest(),
           "table_sha256": hashlib.sha256(table).hexdigest(),
           "table_path": str(args.output)})


if __name__ == "__main__":
    main()
