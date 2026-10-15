#!/usr/bin/env python3
"""Audit the experimental image-B app record without demanding native code addresses."""
import hashlib
import json
import re
import struct
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
BUILD = HERE / "build-sample-app-size-final-20261014"
STOCK = ROOT / "g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage2.bin"
NM = ROOT / "g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin/csky-elfabiv2-nm"
OBJCOPY = NM.with_name("csky-elfabiv2-objcopy")
BASE = 0x10003000
STOCK_SHA = "d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941"
FIELDS = (
    ("name", 0x10013ba0, "sample_name", b"sample app\0"),
    ("init", 0x1000c0bc, "gx8002_image_b_sample_app_init_1000c0bc", None),
    ("event", 0x1000c1c8, "gx8002_image_b_sample_app_event_1000c1c8", None),
    ("task", 0x1000bea8, "gx8002_image_b_sample_app_task_1000bea8", None),
    ("suspend", 0x1000bed0, "gx8002_image_b_sample_app_suspend_1000bed0", None),
    ("suspend_priv", 0x10013bac, "suspend_name", b"SampleAppSuspend\0"),
    ("resume", 0x1000beac, "gx8002_image_b_sample_app_resume_1000beac", None),
    ("resume_priv", 0x10013bc0, "resume_name", b"SampleAppResume\0"),
)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def at(image, address, length):
    offset = address - BASE
    return image[offset:offset + length]


def word(image, address):
    return struct.unpack("<I", at(image, address, 4))[0]


def main():
    final = json.loads((BUILD / "receipt.json").read_text())
    assert final["result"] == "PASS_LAYOUT_ONLY"
    assert final["sample_app_experiment"] and not final["sample_app_callbacks_qualified"]
    elf = ROOT / final["elf"]
    assert sha(elf.read_bytes()) == final["elf_sha256"]
    payload = (BUILD / "image_b_source_payload.bin").read_bytes()
    with tempfile.TemporaryDirectory(dir=BUILD) as temporary:
        regenerated = Path(temporary) / "payload.bin"
        subprocess.run([str(OBJCOPY), "-O", "binary", str(elf), str(regenerated)],
                       check=True, capture_output=True, text=True)
        assert regenerated.read_bytes() == payload
    stock = STOCK.read_bytes()
    assert len(payload) == len(stock) == 0x1408c
    assert sha(stock) == STOCK_SHA
    assert final["sections"][".sample_app_pointer"]["lma"] == 0x10016f74
    assert final["sections"][".sample_app_record"]["lma"] == 0x10016f78
    assert final["sections"][".sample_app_record"]["size"] == 32
    listing = subprocess.check_output([str(NM), "-S", str(elf)], text=True)
    symbols = {}
    for line in listing.splitlines():
        match = re.fullmatch(r"([0-9a-f]+) ([0-9a-f]+) [A-Za-z] (\S+)", line)
        if match:
            symbols.setdefault(match[3], []).append(int(match[1], 16))
    for name, address in (("gx8002_image_b_sample_app_selected_20016f74", 0x20016f74),
                          ("gx8002_image_b_sample_app_record_20016f78", 0x20016f78)):
        assert symbols[name] == [address]
    assert word(payload, 0x10016f74) == word(stock, 0x10016f74) == 0x20016f78
    rows = []
    for index, (field, native, symbol, string) in enumerate(FIELDS):
        address = 0x10016f78 + index * 4
        candidates = symbols[symbol]
        if string is not None:
            candidates = [candidate for candidate in candidates
                          if at(payload, candidate, len(string)) == string]
            assert at(stock, native, len(string)) == string
        assert len(candidates) == 1, (field, candidates)
        linked = candidates[0]
        assert word(stock, address) == native, field
        assert word(payload, address) == linked, field
        rows.append({"field": field, "native_pointer": hex(native),
                     "linked_source_pointer": hex(linked), "source_symbol": symbol,
                     "raw_pointer_bytes_equal": linked == native})
    receipt = {
        "result": "PASS_RELOCATION_AWARE_SAMPLE_APP_RECORD",
        "stock_sha256": STOCK_SHA,
        "source_elf_sha256": final["elf_sha256"],
        "source_payload_sha256": sha(payload),
        "payload_bytes": len(payload),
        "selector_pointer_exact": True,
        "record_pointer_fields": rows,
        "raw_record_bytes_equal": at(payload, 0x10016f78, 32) == at(stock, 0x10016f78, 32),
        "callback_behavior_qualified": False,
        "bootable": False,
    }
    path = BUILD / "sample-app-relocation-receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(path)


if __name__ == "__main__":
    main()
