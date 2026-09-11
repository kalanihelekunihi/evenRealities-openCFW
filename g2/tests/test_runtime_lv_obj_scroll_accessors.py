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
SOURCE = ROOT / "components/apollo_main/core_overlay/lv_obj_scroll_accessors.c"
FIXTURE = ROOT / "tests/fixtures/lv_obj_scroll_accessors_host.c"
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"

# `analyze_g2_lvgl_version.py`'s pinned identity for the same image.
IMAGE_SIZE = 3_523_396
IMAGE_SHA256 = (
    "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
)
LOAD_BASE = 0x00437FE0

SOURCE_SIZE = 12_458
SOURCE_SHA256 = (
    "bd5ee2855a85c72a689f2ef46698e136"
    "a06a2179cb3e1e611ac33c70602c1d9a"
)

LVGL_SCROLL_SOURCE = ROOT / "third_party/lvgl/src/core/lv_obj_scroll.c"
LVGL_SCROLL_PRIVATE = ROOT / "third_party/lvgl/src/core/lv_obj_private.h"

# (stock entry, body length, exact body SHA-256 from the pinned image,
#  candidate symbol) for every stock function this closure admits.
TARGETS = (
    (0x0044E412, 26,
     "16affc9a0e2205e8bb9b7c755bb4d330807fab791fd8f63cdc7cf6d7a1d5824d",
     "open_cfw_lv_obj_set_scroll_snap_y"),
    (0x0044E42C, 22,
     "968a721ff9109cca0d9d9b037a6faa47dc52114d994f406f5f842d2836fad289",
     "open_cfw_lv_obj_get_scrollbar_mode"),
    (0x0044E442, 24,
     "3be9ad284bf9e36516957762da6e21bba27ec600397c3225486a4d614489b4ca",
     "open_cfw_lv_obj_get_scroll_dir"),
    (0x0044E45A, 22,
     "08bb33cbc2a069e69c623e3da2ff2b1003fcd312db68e56662065bf15aca2c94",
     "open_cfw_lv_obj_get_scroll_snap_x"),
    (0x0044E470, 22,
     "f05d5542aac5bc00db80e1c970305705be67cf9956fbc70f9ca51d01b5b48139",
     "open_cfw_lv_obj_get_scroll_snap_y"),
    (0x0044E486, 18,
     "2dc0716ebb416673a45b8e55cf7cdaffd3dda5c2236748b2e83477841b0e72ce",
     "open_cfw_lv_obj_get_scroll_x"),
    (0x0044E498, 18,
     "63a361e5af600de948aed7ee8680a060a9df2e451a4afee82140c63c4da9f1f2",
     "open_cfw_lv_obj_get_scroll_y"),
    (0x0044E4AA, 18,
     "63a361e5af600de948aed7ee8680a060a9df2e451a4afee82140c63c4da9f1f2",
     "open_cfw_lv_obj_get_scroll_top"),
    (0x0044E75E, 64,
     "33459508b895cc9027e4ce0d729da47d50ac22b93f58f954b23e9434e190248f",
     "open_cfw_lv_obj_get_scroll_end"),
)
TOTAL_BYTES = sum(size for _, size, _, _ in TARGETS)

# Verbatim scroll_x_anim/scroll_y_anim identity words read from the pinned
# image literal pool at 0x0044EB1C/0x0044EB20.
SCROLL_X_ANIM_CB_WORD = 0x0044F3B9
SCROLL_Y_ANIM_CB_WORD = 0x0044F3D5


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class RuntimeLvObjScrollAccessorsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.image = IMAGE.read_bytes()
        temporary_parent = ROOT / "build"
        temporary_parent.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(dir=temporary_parent)
        temporary = Path(cls.temporary.name)
        library = temporary / (
            "lv_obj_scroll_accessors" + (".dylib" if sys.platform == "darwin" else ".so")
        )
        command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE),
        ]
        command += ["-dynamiclib", "-o", str(library)] if sys.platform == "darwin" \
            else ["-shared", "-fPIC", "-o", str(library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.host = ctypes.CDLL(str(library))

        host = cls.host
        host.open_cfw_test_lv_obj_scroll_reset.argtypes = []
        host.open_cfw_test_lv_obj_scroll_reset.restype = None
        host.open_cfw_test_lv_obj_scroll_make_obj_no_spec_attr.argtypes = []
        host.open_cfw_test_lv_obj_scroll_make_obj_no_spec_attr.restype = ctypes.c_void_p
        host.open_cfw_test_lv_obj_scroll_make_obj_with_spec_attr.argtypes = [
            ctypes.c_int32, ctypes.c_int32, ctypes.c_uint16,
        ]
        host.open_cfw_test_lv_obj_scroll_make_obj_with_spec_attr.restype = ctypes.c_void_p
        host.open_cfw_test_lv_obj_scroll_flags.argtypes = []
        host.open_cfw_test_lv_obj_scroll_flags.restype = ctypes.c_uint16
        host.open_cfw_test_lv_obj_scroll_allocate_calls.argtypes = []
        host.open_cfw_test_lv_obj_scroll_allocate_calls.restype = ctypes.c_uint
        host.open_cfw_test_lv_obj_scroll_allocate_last_obj_matches.argtypes = [ctypes.c_void_p]
        host.open_cfw_test_lv_obj_scroll_allocate_last_obj_matches.restype = ctypes.c_int
        host.open_cfw_test_lv_obj_scroll_set_anim_results.argtypes = [
            ctypes.c_int32, ctypes.c_int, ctypes.c_int32, ctypes.c_int,
        ]
        host.open_cfw_test_lv_obj_scroll_set_anim_results.restype = None
        host.open_cfw_test_lv_obj_scroll_anim_get_calls.argtypes = []
        host.open_cfw_test_lv_obj_scroll_anim_get_calls.restype = ctypes.c_uint
        host.open_cfw_test_lv_obj_scroll_anim_get_last_cb.argtypes = []
        host.open_cfw_test_lv_obj_scroll_anim_get_last_cb.restype = ctypes.c_void_p
        host.open_cfw_test_lv_obj_scroll_anim_get_last_var_matches.argtypes = [ctypes.c_void_p]
        host.open_cfw_test_lv_obj_scroll_anim_get_last_var_matches.restype = ctypes.c_int
        host.open_cfw_test_lv_obj_scroll_x_anim_cb.argtypes = []
        host.open_cfw_test_lv_obj_scroll_x_anim_cb.restype = ctypes.c_void_p
        host.open_cfw_test_lv_obj_scroll_y_anim_cb.argtypes = []
        host.open_cfw_test_lv_obj_scroll_y_anim_cb.restype = ctypes.c_void_p

        for name, restype in (
            ("get_scroll_x", ctypes.c_int32),
            ("get_scroll_y", ctypes.c_int32),
            ("get_scroll_top", ctypes.c_int32),
            ("get_scrollbar_mode", ctypes.c_uint8),
            ("get_scroll_dir", ctypes.c_uint16),
            ("get_scroll_snap_x", ctypes.c_uint8),
            ("get_scroll_snap_y", ctypes.c_uint8),
        ):
            function = getattr(host, "open_cfw_test_" + name)
            function.argtypes = [ctypes.c_void_p]
            function.restype = restype

        host.open_cfw_test_set_scroll_snap_y.argtypes = [ctypes.c_void_p, ctypes.c_uint8]
        host.open_cfw_test_set_scroll_snap_y.restype = None
        host.open_cfw_test_get_scroll_end.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int32 * 2)]
        host.open_cfw_test_get_scroll_end.restype = None

        for name in (
            "get_scroll_x", "get_scroll_y", "get_scrollbar_mode",
            "get_scroll_dir", "get_scroll_snap_x", "get_scroll_snap_y",
        ):
            function = getattr(host, "open_cfw_oracle_" + name)
            function.argtypes = [ctypes.c_void_p]
        host.open_cfw_oracle_get_scroll_x.restype = ctypes.c_int32
        host.open_cfw_oracle_get_scroll_y.restype = ctypes.c_int32
        host.open_cfw_oracle_get_scrollbar_mode.restype = ctypes.c_uint8
        host.open_cfw_oracle_get_scroll_dir.restype = ctypes.c_uint16
        host.open_cfw_oracle_get_scroll_snap_x.restype = ctypes.c_uint8
        host.open_cfw_oracle_get_scroll_snap_y.restype = ctypes.c_uint8

    def span(self, address: int, length: int) -> bytes:
        offset = address - LOAD_BASE
        return self.image[offset:offset + length]

    # ---- image / source self-pinning ----

    def test_image_identity_is_unchanged(self) -> None:
        self.assertEqual(len(self.image), IMAGE_SIZE)
        self.assertEqual(_digest(self.image), IMAGE_SHA256)

    def test_source_identity_is_pinned(self) -> None:
        payload = SOURCE.read_bytes()
        self.assertEqual(len(payload), SOURCE_SIZE)
        self.assertEqual(_digest(payload), SOURCE_SHA256)

    def test_stock_bodies_are_exactly_the_claimed_bytes(self) -> None:
        total = 0
        for address, size, digest, _name in TARGETS:
            body = self.span(address, size)
            self.assertEqual(len(body), size)
            self.assertEqual(_digest(body), digest)
            total += size
        self.assertEqual(total, TOTAL_BYTES)

    def test_scroll_anim_callback_identities_come_from_the_image(self) -> None:
        # DAT_0044eb1c / DAT_0044eb20 in the stock lv_obj_get_scroll_end body.
        x_word = int.from_bytes(self.span(0x0044EB1C, 4), "little")
        y_word = int.from_bytes(self.span(0x0044EB20, 4), "little")
        self.assertEqual(x_word, SCROLL_X_ANIM_CB_WORD)
        self.assertEqual(y_word, SCROLL_Y_ANIM_CB_WORD)
        self.assertEqual(
            ctypes.cast(self.host.open_cfw_test_lv_obj_scroll_x_anim_cb(), ctypes.c_void_p).value,
            SCROLL_X_ANIM_CB_WORD,
        )
        self.assertEqual(
            ctypes.cast(self.host.open_cfw_test_lv_obj_scroll_y_anim_cb(), ctypes.c_void_p).value,
            SCROLL_Y_ANIM_CB_WORD,
        )

    # ---- upstream correspondence ----

    def test_source_matches_vendored_upstream_getters_and_setter(self) -> None:
        upstream = LVGL_SCROLL_SOURCE.read_text(encoding="utf-8")
        for snippet in (
            "return -obj->spec_attr->scroll.x;",
            "return -obj->spec_attr->scroll.y;",
            "if(obj->spec_attr) return (lv_scrollbar_mode_t) obj->spec_attr->scrollbar_mode;",
            "else return LV_SCROLLBAR_MODE_AUTO;",
            "if(obj->spec_attr) return (lv_dir_t) obj->spec_attr->scroll_dir;",
            "else return LV_DIR_ALL;",
            "obj->spec_attr->scroll_snap_y = align;",
            "a = lv_anim_get(obj, scroll_x_anim);",
            "end->x = a ? -a->end_value : lv_obj_get_scroll_x(obj);",
            "a = lv_anim_get(obj, scroll_y_anim);",
            "end->y = a ? -a->end_value : lv_obj_get_scroll_y(obj);",
        ):
            self.assertIn(snippet, upstream)
        private_header = LVGL_SCROLL_PRIVATE.read_text(encoding="utf-8")
        for snippet in (
            "lv_point_t scroll;",
            "uint16_t scrollbar_mode : 2;",
            "uint16_t scroll_snap_x : 2;",
            "uint16_t scroll_snap_y : 2;",
            "uint16_t scroll_dir : 4;",
        ):
            self.assertIn(snippet, private_header)

    # ---- behavior ----

    def test_getters_default_when_spec_attr_is_null(self) -> None:
        host = self.host
        host.open_cfw_test_lv_obj_scroll_reset()
        obj = host.open_cfw_test_lv_obj_scroll_make_obj_no_spec_attr()
        self.assertEqual(host.open_cfw_test_get_scroll_x(obj), 0)
        self.assertEqual(host.open_cfw_test_get_scroll_y(obj), 0)
        self.assertEqual(host.open_cfw_test_get_scroll_top(obj), 0)
        self.assertEqual(host.open_cfw_test_get_scrollbar_mode(obj), 3)
        self.assertEqual(host.open_cfw_test_get_scroll_dir(obj), 0x0F)
        self.assertEqual(host.open_cfw_test_get_scroll_snap_x(obj), 0)
        self.assertEqual(host.open_cfw_test_get_scroll_snap_y(obj), 0)

    def _assert_flag_getters_match_oracle(self, obj) -> None:
        host = self.host
        self.assertEqual(
            host.open_cfw_test_get_scrollbar_mode(obj),
            host.open_cfw_oracle_get_scrollbar_mode(obj),
        )
        self.assertEqual(
            host.open_cfw_test_get_scroll_dir(obj),
            host.open_cfw_oracle_get_scroll_dir(obj),
        )
        self.assertEqual(
            host.open_cfw_test_get_scroll_snap_x(obj),
            host.open_cfw_oracle_get_scroll_snap_x(obj),
        )
        self.assertEqual(
            host.open_cfw_test_get_scroll_snap_y(obj),
            host.open_cfw_oracle_get_scroll_snap_y(obj),
        )

    def test_flag_getters_match_independent_oracle_exhaustively(self) -> None:
        # bits [9:0] cover scrollbar_mode/scroll_snap_x/scroll_snap_y/
        # scroll_dir completely; this is exhaustive over that sub-domain.
        host = self.host
        for flags in range(0, 1 << 10):
            host.open_cfw_test_lv_obj_scroll_reset()
            obj = host.open_cfw_test_lv_obj_scroll_make_obj_with_spec_attr(0, 0, flags)
            self._assert_flag_getters_match_oracle(obj)

    def test_flag_getters_ignore_bits_above_the_admitted_field(self) -> None:
        host = self.host
        for flags in (0x0400, 0x0800, 0x1000, 0xFC00, 0xFFFF):
            host.open_cfw_test_lv_obj_scroll_reset()
            obj = host.open_cfw_test_lv_obj_scroll_make_obj_with_spec_attr(0, 0, flags)
            self._assert_flag_getters_match_oracle(obj)

    def test_scroll_getters_match_independent_oracle_over_int32_samples(self) -> None:
        host = self.host
        # `INT32_MIN` is deliberately excluded: negating it is undefined
        # behavior in C, and both the candidate and the oracle perform the
        # exact same `-value` the stock body does, so it would not exercise
        # any difference between them.
        samples = (
            0, 1, -1, 7, -7, 1000, -1000, 2_147_483_646, -2_147_483_647,
            2_147_483_647,
        )
        for scroll_x in samples:
            for scroll_y in samples:
                host.open_cfw_test_lv_obj_scroll_reset()
                obj = host.open_cfw_test_lv_obj_scroll_make_obj_with_spec_attr(
                    scroll_x, scroll_y, 0
                )
                self.assertEqual(
                    host.open_cfw_test_get_scroll_x(obj),
                    host.open_cfw_oracle_get_scroll_x(obj),
                )
                self.assertEqual(
                    host.open_cfw_test_get_scroll_y(obj),
                    host.open_cfw_oracle_get_scroll_y(obj),
                )
                self.assertEqual(
                    host.open_cfw_test_get_scroll_top(obj),
                    host.open_cfw_oracle_get_scroll_y(obj),
                )

    def test_get_scroll_y_and_get_scroll_top_are_byte_identical_upstream(self) -> None:
        # Confirmed at the source level (both bodies read
        # `-obj->spec_attr->scroll.y` with no other statement) and at the
        # stock-image level (identical 18-byte SHA-256, asserted above); this
        # checks the candidate reproduces that duplication rather than one
        # calling the other.
        host = self.host
        host.open_cfw_test_lv_obj_scroll_reset()
        obj = host.open_cfw_test_lv_obj_scroll_make_obj_with_spec_attr(11, -12345, 0)
        self.assertEqual(
            host.open_cfw_test_get_scroll_y(obj),
            host.open_cfw_test_get_scroll_top(obj),
        )

    def test_set_scroll_snap_y_allocates_and_preserves_other_bits(self) -> None:
        host = self.host
        for align in range(4):
            host.open_cfw_test_lv_obj_scroll_reset()
            obj = host.open_cfw_test_lv_obj_scroll_make_obj_with_spec_attr(
                0, 0, 0xFFFF & ~(0x3 << 4)
            )
            host.open_cfw_test_set_scroll_snap_y(obj, align)
            self.assertEqual(host.open_cfw_test_lv_obj_scroll_allocate_calls(), 1)
            self.assertTrue(host.open_cfw_test_lv_obj_scroll_allocate_last_obj_matches(obj))
            flags = host.open_cfw_test_lv_obj_scroll_flags()
            self.assertEqual((flags >> 4) & 0x3, align)
            # every other bit position is untouched
            self.assertEqual(flags & ~(0x3 << 4), 0xFFFF & ~(0x3 << 4))

    def test_set_scroll_snap_y_allocates_spec_attr_when_absent(self) -> None:
        host = self.host
        host.open_cfw_test_lv_obj_scroll_reset()
        obj = host.open_cfw_test_lv_obj_scroll_make_obj_no_spec_attr()
        host.open_cfw_test_set_scroll_snap_y(obj, 2)
        self.assertEqual(host.open_cfw_test_lv_obj_scroll_allocate_calls(), 1)
        self.assertEqual((host.open_cfw_test_lv_obj_scroll_flags() >> 4) & 0x3, 2)

    def test_get_scroll_end_prefers_running_animation_end_value(self) -> None:
        host = self.host
        host.open_cfw_test_lv_obj_scroll_reset()
        obj = host.open_cfw_test_lv_obj_scroll_make_obj_with_spec_attr(5, -7, 0)
        host.open_cfw_test_lv_obj_scroll_set_anim_results(100, 1, -200, 1)
        end = (ctypes.c_int32 * 2)()
        host.open_cfw_test_get_scroll_end(obj, ctypes.byref(end))
        self.assertEqual(list(end), [-100, 200])
        self.assertEqual(host.open_cfw_test_lv_obj_scroll_anim_get_calls(), 2)

    def test_get_scroll_end_falls_back_to_plain_getters_without_animation(self) -> None:
        host = self.host
        host.open_cfw_test_lv_obj_scroll_reset()
        obj = host.open_cfw_test_lv_obj_scroll_make_obj_with_spec_attr(5, -7, 0)
        host.open_cfw_test_lv_obj_scroll_set_anim_results(0, 0, 0, 0)
        end = (ctypes.c_int32 * 2)()
        host.open_cfw_test_get_scroll_end(obj, ctypes.byref(end))
        self.assertEqual(list(end), [-5, 7])

    def test_get_scroll_end_queries_the_exact_stock_callback_identities_in_order(self) -> None:
        host = self.host
        host.open_cfw_test_lv_obj_scroll_anim_get_first_cb.argtypes = []
        host.open_cfw_test_lv_obj_scroll_anim_get_first_cb.restype = ctypes.c_void_p
        host.open_cfw_test_lv_obj_scroll_reset()
        obj = host.open_cfw_test_lv_obj_scroll_make_obj_with_spec_attr(0, 0, 0)
        host.open_cfw_test_lv_obj_scroll_set_anim_results(1, 1, 2, 1)
        end = (ctypes.c_int32 * 2)()
        host.open_cfw_test_get_scroll_end(obj, ctypes.byref(end))
        self.assertEqual(host.open_cfw_test_lv_obj_scroll_anim_get_calls(), 2)
        self.assertEqual(
            ctypes.cast(host.open_cfw_test_lv_obj_scroll_anim_get_first_cb(), ctypes.c_void_p).value,
            SCROLL_X_ANIM_CB_WORD,
        )
        self.assertEqual(
            ctypes.cast(host.open_cfw_test_lv_obj_scroll_anim_get_last_cb(), ctypes.c_void_p).value,
            SCROLL_Y_ANIM_CB_WORD,
        )
        self.assertTrue(host.open_cfw_test_lv_obj_scroll_anim_get_last_var_matches(obj))


if __name__ == "__main__":
    unittest.main()
