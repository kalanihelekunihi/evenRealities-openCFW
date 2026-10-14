#!/usr/bin/env python3
"""Bind the UART callback record and both adjacent bodies to official data."""
from pathlib import Path
import hashlib
import struct

from verify_ble_hci_le_feature_initializer import ROOT, decoded

payload = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
blob = payload.read_bytes()
assert hashlib.sha256(blob).hexdigest() == \
    "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
record = bytes(decoded[0x658:0x668])
assert record.hex() == "53394700a53a47000000000000000000"
assert struct.unpack("<4I", record) == (0x473953, 0x473aa5, 0, 0)
raw = blob[32:]
base = 0x438000
functions = [(0x473952, 0x4739fc,
              "b19b9503ab5a6d1198759601df7eb669479a20dd180da12d19144f274146aa48"),
             (0x4739fc, 0x473aa4,
              "21db44eae1bd22a7bb43dff81d73d07a56196d8878605fed8d7af55989b7a453")]
for start, end, expected in functions:
    assert hashlib.sha256(raw[start-base:end-base]).hexdigest() == expected
print("PASS_UART_CALLBACK_RECORD", record.hex(), len(functions))
