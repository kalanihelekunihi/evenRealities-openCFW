"""Host differential tests for the AM-040 trailing string/state helpers.

Builds g2/tests/fixtures/runtime_str_state_helpers_host.c (which
includes the two production translation units with host-substituted
providers) and checks behavior plus stock-body SHA-256 pins for all
eleven functions at 0x0048D540..0x0048D558 and 0x0048D558..0x0048D866.
"""

from __future__ import annotations

import ctypes
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "tests" / "fixtures" / "runtime_str_state_helpers_host.c"
OFFICIAL = ROOT / "blobs" / "official" / "g2-2.2.6.10" / "ota_s200_firmware_ota.bin"
BASE = 0x438000

# (address, size, stock body SHA-256, port symbol)
LEAVES = [
    (0x48D540, 24, "40fc73584b7ab2d723eb1b08d7d80789e31599de9b6eceb2749666ddf0d1e1d1", "open_cfw_libc_strcpy"),
    (0x48D558, 16, "191f8628d69bae38912787fa17ab342cc4c4a97069c8f7e83d5c620feacec814", "open_cfw_state_init_params"),
    (0x48D570, 24, "bed13e9966795b345004a55eb81a55e8af4cc322eeb2491c8fdcb0b0acf4360c", "open_cfw_state_nibble_to_mode"),
    (0x48D588, 152, "66dc0be5a4192c755d16663c320d986cae93259ac903e49aad7e5c5d90f020ce", "open_cfw_state_mode_switch"),
    (0x48D620, 52, "2629a71d82c78f7602d8f37273ae02bcf42f237cdaab9da0d4db6d57a1045692", "open_cfw_state_flag_get"),
    (0x48D654, 28, "6eb814fc999a7dcc3d3162f2cf41e3f42c82fcb54cddfd7b29518423412fd4df", "open_cfw_state_sample_vote"),
    (0x48D670, 108, "8cd6a123b59adde655f757e17f2ff020a19fb7ea71dd899d63332a559b60ecb5", "open_cfw_state_sample_retry"),
    (0x48D6DC, 10, "fd98de39e7062501b0d1ff5b9727543177dc3a975d72c80aa12b15453f5f1c9e", "open_cfw_state_flag_or"),
    (0x48D6E6, 10, "35f4dae195f172d4bd59e69be0399a735154582b611df34c768d345f7fabeca7", "open_cfw_state_latch_store"),
    (0x48D6F0, 20, "cdffe8f30b75d3cc7d6a924f5b4e50051a3ece1d68543003fae0049efcfeb364", "open_cfw_state_value_get"),
    # span is 322 bytes: 318 code bytes plus the 4-byte PC-relative
    # digit-table delta literal at 0x0048D7DC (the recorded body hash
    # covers the whole span).
    (0x48D724, 322, "35605c54e52dd1c91aed210b77e88743db4671ca679546c2c68bf7f03cc1fd8d", "open_cfw_libc_strtoul"),
]


def stock_slice(address: int, size: int) -> bytes:
    application = OFFICIAL.read_bytes()[32:]
    return application[address - BASE:address - BASE + size]


class StrStateHelperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        image = OFFICIAL.read_bytes()[32:]
        for address, size, digest, _symbol in LEAVES:
            body = image[address - BASE:address - BASE + size]
            assert len(body) == size
            assert hashlib.sha256(body).hexdigest() == digest, hex(address)
        cls.temp = tempfile.TemporaryDirectory()
        library = Path(cls.temp.name) / (
            "a.dylib" if sys.platform == "darwin" else "a.so"
        )
        command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(FIXTURE),
        ]
        command += (
            ["-dynamiclib", "-o", str(library)]
            if sys.platform == "darwin"
            else ["-shared", "-fPIC", "-o", str(library)]
        )
        proc = subprocess.run(command, capture_output=True, text=True)
        if proc.returncode != 0:
            raise AssertionError(f"fixture build failed:\n{proc.stderr}")
        cls.lib = ctypes.CDLL(str(library))
        lib = cls.lib
        lib.open_cfw_libc_strcpy.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        lib.open_cfw_libc_strcpy.restype = ctypes.c_void_p
        lib.open_cfw_libc_strtoul.argtypes = [
            ctypes.c_char_p, ctypes.POINTER(ctypes.c_char_p),
            ctypes.c_int, ctypes.POINTER(ctypes.c_uint32),
        ]
        lib.open_cfw_libc_strtoul.restype = ctypes.c_uint32
        lib.open_cfw_state_init_params.argtypes = [
            ctypes.POINTER(ctypes.c_uint32)] * 3
        lib.open_cfw_state_init_params.restype = None
        lib.open_cfw_state_nibble_to_mode.argtypes = [ctypes.c_uint32]
        lib.open_cfw_state_nibble_to_mode.restype = ctypes.c_uint32
        lib.open_cfw_state_mode_switch.argtypes = [ctypes.c_uint32] * 4
        lib.open_cfw_state_mode_switch.restype = ctypes.c_uint32
        lib.open_cfw_state_flag_get.argtypes = []
        lib.open_cfw_state_flag_get.restype = ctypes.c_uint8
        lib.open_cfw_state_sample_vote.argtypes = []
        lib.open_cfw_state_sample_vote.restype = ctypes.c_uint32
        lib.open_cfw_state_sample_retry.argtypes = [ctypes.c_uint32] * 3
        lib.open_cfw_state_sample_retry.restype = ctypes.c_uint32
        lib.open_cfw_state_flag_or.argtypes = [ctypes.c_uint32]
        lib.open_cfw_state_flag_or.restype = None
        lib.open_cfw_state_latch_store.argtypes = [ctypes.c_uint32]
        lib.open_cfw_state_latch_store.restype = ctypes.c_uint32
        lib.open_cfw_state_value_get.argtypes = [ctypes.c_uint8]
        lib.open_cfw_state_value_get.restype = ctypes.c_uint32
        lib.open_cfw_test_holder.argtypes = [ctypes.c_uint32]
        lib.open_cfw_test_holder.restype = ctypes.c_void_p
        lib.open_cfw_test_sample_push.argtypes = [ctypes.c_uint32] * 3
        lib.open_cfw_test_sample_push.restype = None
        for name in ("open_cfw_test_irq_disable_calls",
                     "open_cfw_test_irq_restore_calls",
                     "open_cfw_test_irq_restore_value",
                     "open_cfw_test_channel_a_calls",
                     "open_cfw_test_channel_b_calls"):
            getattr(lib, name).argtypes = []
            getattr(lib, name).restype = ctypes.c_uint32
        lib.open_cfw_test_str_errno_calls_fn.argtypes = []
        lib.open_cfw_test_str_errno_calls_fn.restype = ctypes.c_int

    def setUp(self) -> None:
        reset = self.lib.open_cfw_test_state_reset
        reset.argtypes = []
        reset.restype = None
        reset()

    # ---------- strcpy ----------

    def test_strcpy_basic_and_empty(self) -> None:
        lib = self.lib
        dst = ctypes.create_string_buffer(16)
        ret = lib.open_cfw_libc_strcpy(dst, b"hello")
        assert ret == ctypes.addressof(dst)
        assert dst.value == b"hello"
        dst2 = ctypes.create_string_buffer(16)
        lib.open_cfw_libc_strcpy(dst2, b"")
        assert dst2.value == b""

    # ---------- strtoul ----------

    def call_strtoul(self, text: bytes, base: int):
        end = ctypes.c_char_p()
        flag = ctypes.c_uint32(0xDEAD)
        keep = ctypes.create_string_buffer(text + b"\x00tail")
        value = self.lib.open_cfw_libc_strtoul(
            keep, ctypes.byref(end), base, ctypes.byref(flag))
        consumed = (
            ctypes.addressof(keep)
            and (ctypes.cast(end, ctypes.c_void_p).value
                 - ctypes.addressof(keep))
        )
        return value, consumed, flag.value

    def test_strtoul_decimal(self) -> None:
        value, consumed, flag = self.call_strtoul(b"123", 10)
        assert (value, consumed, flag) == (123, 3, 0)

    def test_strtoul_spaces_sign(self) -> None:
        value, consumed, flag = self.call_strtoul(b" \t-42 end", 10)
        assert (value, consumed, flag) == (0xFFFFFFD6, 5, 0)

    def test_strtoul_base_detect(self) -> None:
        assert self.call_strtoul(b"0x1f", 0)[:2] == (31, 4)
        assert self.call_strtoul(b"0X1F", 0)[:2] == (31, 4)
        assert self.call_strtoul(b"017", 0)[:2] == (15, 3)
        assert self.call_strtoul(b"19", 0)[:2] == (19, 2)
        assert self.call_strtoul(b"0x1f", 16)[:2] == (31, 4)
        assert self.call_strtoul(b"1f", 16)[:2] == (31, 2)
        assert self.call_strtoul(b"19", 8)[:2] == (1, 1)

    def test_strtoul_invalid_and_empty(self) -> None:
        for base in (1, 37, -2):
            value, consumed, flag = self.call_strtoul(b"123", base)
            assert (value, consumed, flag) == (0, 0, 0), base
        value, consumed, flag = self.call_strtoul(b"xyz", 10)
        assert (value, consumed, flag) == (0, 0, 0)
        value, consumed, flag = self.call_strtoul(b"", 10)
        assert (value, consumed, flag) == (0, 0, 0)

    def test_strtoul_overflow_and_max(self) -> None:
        value, consumed, flag = self.call_strtoul(b"4294967295", 10)
        assert (value, flag) == (0xFFFFFFFF, 0)
        assert consumed == 10
        value, consumed, flag = self.call_strtoul(b"4294967296", 10)
        assert value == 0xFFFFFFFF and flag == 1
        assert self.lib.open_cfw_test_str_errno_calls_fn() == 1
        value, _consumed, flag = self.call_strtoul(b"0xFFFFFFFFF", 16)
        assert value == 0xFFFFFFFF and flag == 1
        value, _consumed, flag = self.call_strtoul(b"0xFFFFFFFF", 16)
        assert value == 0xFFFFFFFF and flag == 0

    def test_strtoul_null_out_params(self) -> None:
        lib = self.lib
        keep = ctypes.create_string_buffer(b"77\x00")
        value = lib.open_cfw_libc_strtoul(keep, None, 10, None)
        assert value == 77
        assert lib.open_cfw_test_str_errno_calls_fn() == 0
        keep2 = ctypes.create_string_buffer(b"99999999999999999999\x00")
        value2 = lib.open_cfw_libc_strtoul(keep2, None, 10, None)
        assert value2 == 0xFFFFFFFF
        assert lib.open_cfw_test_str_errno_calls_fn() == 1

    # ---------- params / nibble map ----------

    def test_init_params(self) -> None:
        first = ctypes.c_uint32(0)
        second = ctypes.c_uint32(0)
        third = ctypes.c_uint32(0)
        self.lib.open_cfw_state_init_params(
            ctypes.byref(first), ctypes.byref(second), ctypes.byref(third))
        assert (first.value, second.value, third.value) == (
            0x20071E30, 0x2005F154, 0x400)

    def test_nibble_to_mode(self) -> None:
        lib = self.lib
        assert [lib.open_cfw_state_nibble_to_mode(n) for n in range(8)] == [
            7, 4, 4, 7, 7, 7, 0, 7]

    # ---------- state helpers reach through the fixture cells ----------

    def poke_cells(self, control: int, dirty: int, mask: int, value: int):
        lib = self.lib
        holder = lib.open_cfw_test_holder
        ctypes.cast(holder(0x0048D704),
                    ctypes.POINTER(ctypes.c_uint32)).contents.value = control
        ctypes.cast(holder(0x0048D708),
                    ctypes.POINTER(ctypes.c_uint8)).contents.value = dirty
        ctypes.cast(holder(0x0048D710),
                    ctypes.POINTER(ctypes.c_uint32)).contents.value = mask
        ctypes.cast(holder(0x0048D714),
                    ctypes.POINTER(ctypes.c_uint32)).contents.value = value

    def test_flag_get_branches(self) -> None:
        lib = self.lib
        self.poke_cells(0x40008801, 0, 0, 0)
        assert lib.open_cfw_state_flag_get() == 0  # dirty clear
        self.poke_cells(0x40008800, 1, 0, 0)
        assert lib.open_cfw_state_flag_get() == 0  # nibble zero
        self.poke_cells(0x80000001, 1, 0, 0)
        assert lib.open_cfw_state_flag_get() == 0  # negative
        self.poke_cells(0x40000001, 1, 0, 0)
        assert lib.open_cfw_state_flag_get() == 0  # bit30 set -> 1^1
        self.poke_cells(0x00000001, 1, 0, 0)
        assert lib.open_cfw_state_flag_get() == 1  # bit30 clear -> 0^1

    def test_mode_switch_transitions(self) -> None:
        lib = self.lib
        # old mode nibble 1 (mode 4), new nibble 2 (mode 4): equal -> no calls
        self.poke_cells(0x00000001, 0, 0, 0)
        old = lib.open_cfw_state_mode_switch(0x00000002, 0, 0, 0)
        assert old == 0x00000001
        assert lib.open_cfw_test_channel_a_calls() == 0
        assert lib.open_cfw_test_channel_b_calls() == 0
        # new nibble 3 (mode 7) differs -> both channels fire
        old = lib.open_cfw_state_mode_switch(0x00000003, 0, 0, 0)
        assert old == 0x00000002
        assert lib.open_cfw_test_channel_a_calls() == 1
        assert lib.open_cfw_test_channel_b_calls() == 1
        # high-bit set on next: only old channel fires
        old = lib.open_cfw_state_mode_switch(0x80000003, 0, 0, 0)
        assert old == 0x00000003
        assert lib.open_cfw_test_channel_a_calls() == 1
        assert lib.open_cfw_test_channel_b_calls() == 2

    def test_sample_vote(self) -> None:
        lib = self.lib
        lib.open_cfw_test_sample_push(7, 7, 9)
        assert lib.open_cfw_state_sample_vote() == 7
        lib.open_cfw_test_sample_push(7, 8, 9)
        assert lib.open_cfw_state_sample_vote() == 9

    def test_sample_retry_bad_lane(self) -> None:
        lib = self.lib
        # stock takes the first vote before the lane check, so one
        # triple is consumed even on this path.
        lib.open_cfw_test_sample_push(1, 1, 1)
        assert lib.open_cfw_state_sample_retry(8, 100, 0) == 5
        assert lib.open_cfw_test_irq_disable_calls() == 0

    def test_sample_retry_sequence(self) -> None:
        lib = self.lib
        holder = lib.open_cfw_test_holder
        shadow = ctypes.cast(holder(0x0048D720),
                             ctypes.POINTER(ctypes.c_uint32 * 8)).contents
        lanes = ctypes.cast(holder(0x0048D70C),
                            ctypes.POINTER(ctypes.c_uint32 * 8)).contents
        shadow[0] = 100
        # first=50; resample 100 (==shadow, spin), 101 (==shadow+1, spin),
        # then 60; post-irq fresh=55 within limit -> target=50+(200-55)-3
        lib.open_cfw_test_sample_push(50, 50, 50)
        lib.open_cfw_test_sample_push(100, 100, 100)
        lib.open_cfw_test_sample_push(101, 101, 101)
        lib.open_cfw_test_sample_push(60, 60, 60)
        lib.open_cfw_test_sample_push(55, 55, 55)
        lib.open_cfw_test_sample_push(70, 70, 70)
        status = lib.open_cfw_state_sample_retry(0, 200, 0)
        assert status == 0
        assert lanes[0] == 50 + (200 - 55) - 3
        assert shadow[0] == 70
        assert lib.open_cfw_test_irq_disable_calls() == 1
        assert lib.open_cfw_test_irq_restore_calls() == 1
        assert lib.open_cfw_test_irq_restore_value() == 1

    def test_sample_retry_clamp(self) -> None:
        lib = self.lib
        holder = lib.open_cfw_test_holder
        shadow = ctypes.cast(holder(0x0048D720),
                             ctypes.POINTER(ctypes.c_uint32 * 8)).contents
        lanes = ctypes.cast(holder(0x0048D70C),
                            ctypes.POINTER(ctypes.c_uint32 * 8)).contents
        shadow[1] = 0
        lib.open_cfw_test_sample_push(10, 10, 10)
        lib.open_cfw_test_sample_push(50, 50, 50)
        lib.open_cfw_test_sample_push(12, 12, 12)
        lib.open_cfw_test_sample_push(13, 13, 13)
        status = lib.open_cfw_state_sample_retry(1, 5, 0)
        assert status == 0x8000000
        assert lanes[1] == 1
        assert shadow[1] == 13

    def test_flag_or_latch_value(self) -> None:
        lib = self.lib
        self.poke_cells(0, 0, 0x0F00, 0x1234)
        lib.open_cfw_state_flag_or(0x00F0)
        assert lib.open_cfw_state_value_get(0) == 0x1234
        assert lib.open_cfw_state_value_get(1) == (0x1234 & 0x0FF0)
        # uxtb narrowing: 0x100 truncates to 0 -> unmasked path
        assert lib.open_cfw_state_value_get(0x100) == 0x1234
        assert lib.open_cfw_state_latch_store(0xABCD) == 0x1234


if __name__ == "__main__":
    unittest.main()
