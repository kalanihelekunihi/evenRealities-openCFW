#!/usr/bin/env python3
"""Compare compiled C CRC16 to all authenticated stock table entries."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[4]
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_ring_hand_checksum.c"
OTA = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
image = OTA.read_bytes()
table = 0x6C0B50 - 0x438000 + 32
with tempfile.TemporaryDirectory() as directory:
    shared = pathlib.Path(directory) / "crc.dylib"
    subprocess.run(["clang", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(shared)], check=True)
    function = ctypes.CDLL(str(shared)).audio_uart_hand_checksum_49acd4
    function.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p]
    function.restype = ctypes.c_uint16
    for index in range(256):
        one = (ctypes.c_uint8 * 1)(index)
        seed = ctypes.c_uint16(0)
        actual = function(one, 1, ctypes.byref(seed))
        expected = int.from_bytes(image[table + 2 * index:table + 2 * index + 2], "little")
        assert actual == expected, (index, actual, expected)
    for data in (b"", b"123456789", bytes(range(256)), b"\xff" * 18):
        buffer = ctypes.create_string_buffer(data)
        value = function(buffer, len(data), None)
        model = 0xFFFF
        for byte in data:
            entry = (byte ^ (model >> 8)) & 255
            model = ((model << 8) ^ int.from_bytes(image[table + 2 * entry:table + 2 * entry + 2], "little")) & 0xFFFF
        assert value == model, (data, value, model)
print("PASS_RING_HAND_CHECKSUM_STOCK_TABLE 260")
