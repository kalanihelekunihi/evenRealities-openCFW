from __future__ import annotations

import ctypes
import hashlib
import os
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "tests" / "fixtures" / "runtime_lvgl_grid_engine_host.c"
OFFICIAL = ROOT / "blobs" / "official" / "g2-2.2.6.10" / "ota_s200_firmware_ota.bin"
BASE = 0x438000

FR_BASE = 0x1FFFFF9B
CONTENT = 0x1FFFFF9A
TEMPLATE_LAST = 0x1FFFFFFF


def FR(n: int) -> int:
    return FR_BASE + n


# (address, size, stock body SHA-256, port symbol)
LEAVES = [
    (0x48CBF8, 500, "1314d4b999e55840d5a31877e094e2e9fdfce7aa2574366cdae736de93cf0e98", "open_cfw_lvgl_grid_calc_cols"),
    (0x48CDEC, 500, "b98ac9e2e0c1101ec6f982620333abf29fcacf31af21334c820afa3c5eeea2e1", "open_cfw_lvgl_grid_calc_rows"),
    (0x48CFE0, 960, "7ba85b52cc205f75f81d91e43f2a56e70fdbfb5c9e561d662d2f5103f0b4182a", "open_cfw_lvgl_grid_item_repos"),
    (0x48D3C8, 264, "ee2d6e690db8be2973e8e8a7faf9af7bfcd8afcfa28af27678fc4be4fcb13c81", "open_cfw_lvgl_grid_align"),
]


class Calc(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_void_p),
        ("y", ctypes.c_void_p),
        ("w", ctypes.c_void_p),
        ("h", ctypes.c_void_p),
        ("col_num", ctypes.c_uint32),
        ("row_num", ctypes.c_uint32),
        ("grid_w", ctypes.c_int32),
        ("grid_h", ctypes.c_int32),
    ]


class Hint(ctypes.Structure):
    _fields_ = [
        ("col", ctypes.c_uint32),
        ("row", ctypes.c_uint32),
        ("grid_abs_x", ctypes.c_int32),
        ("grid_abs_y", ctypes.c_int32),
    ]


class GridCalcTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        cls.buffers: list = []
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
        cls.loaded = ctypes.CDLL(str(library))
        lib = cls.loaded
        lib.open_cfw_test_grid_reset.argtypes = []
        lib.open_cfw_test_grid_reset.restype = None
        lib.open_cfw_test_grid_register.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
        lib.open_cfw_test_grid_register.restype = None
        lib.open_cfw_lvgl_grid_calc_cols.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
        lib.open_cfw_lvgl_grid_calc_cols.restype = None
        lib.open_cfw_lvgl_grid_calc_rows.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
        lib.open_cfw_lvgl_grid_calc_rows.restype = None
        lib.open_cfw_lvgl_grid_item_repos.argtypes = [
            ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p
        ]
        lib.open_cfw_lvgl_grid_item_repos.restype = None
        lib.open_cfw_lvgl_grid_align.argtypes = [
            ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_int32,
            ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32,
        ]
        lib.open_cfw_lvgl_grid_align.restype = ctypes.c_int32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def setUp(self) -> None:
        self.loaded.open_cfw_test_grid_reset()
        type(self).buffers = []
        self._next_id = 0x1000

    def fresh_id(self) -> int:
        obj_id = self._next_id
        self._next_id += 1
        return obj_id

    def uint(self, name: str) -> int:
        return ctypes.c_uint32.in_dll(self.loaded, name).value

    def sint(self, name: str) -> int:
        return ctypes.c_int32.in_dll(self.loaded, name).value

    def set_prop(self, prop: int, value: int) -> None:
        table = (ctypes.c_uint32 * 256).in_dll(
            self.loaded, "open_cfw_test_grid_prop_value"
        )
        table[prop & 0xFF] = value & 0xFFFFFFFF

    def set_global_u32(self, name: str, value: int) -> None:
        ctypes.c_uint32.in_dll(self.loaded, name).value = value & 0xFFFFFFFF

    def set_global_s32(self, name: str, value: int) -> None:
        ctypes.c_int32.in_dll(self.loaded, name).value = value

    def set_ptr_global(self, name: str, buf) -> None:
        ctypes.c_void_p.in_dll(self.loaded, name).value = (
            ctypes.addressof(buf) if buf is not None else 0
        )

    def make_buffer(self, size: int) -> ctypes.Array:
        buf = (ctypes.c_uint8 * size)()
        type(self).buffers.append(buf)
        return buf

    def register(self, obj_id: int, buf) -> int:
        self.loaded.open_cfw_test_grid_register(obj_id, ctypes.addressof(buf))
        type(self).buffers.append(buf)
        return obj_id

    def make_item(self, obj_id: int, x1=0, y1=0, x2=0, y2=0, flags_half=0):
        buf = self.make_buffer(64)
        struct.pack_into("<i", buf, 0x14, x1)
        struct.pack_into("<i", buf, 0x18, y1)
        struct.pack_into("<i", buf, 0x1C, x2)
        struct.pack_into("<i", buf, 0x20, y2)
        struct.pack_into("<H", buf, 0x2A, flags_half)
        return self.register(obj_id, buf), buf

    def item_coords(self, buf) -> list[int]:
        return list(struct.unpack_from("<4i", buf, 0x14))

    def item_flags(self, buf) -> int:
        return struct.unpack_from("<H", buf, 0x2A)[0]

    def set_child_list(self, ids: list[int]) -> None:
        table = (ctypes.c_uint32 * 8).in_dll(
            self.loaded, "open_cfw_test_grid_child_list"
        )
        for i, value in enumerate(ids):
            table[i] = value
        self.set_global_u32("open_cfw_test_grid_child_list_len", len(ids))

    def set_width_map(self, pairs: list[tuple[int, int]]) -> None:
        ids = (ctypes.c_uint32 * 8).in_dll(
            self.loaded, "open_cfw_test_grid_width_ids"
        )
        vals = (ctypes.c_int32 * 8).in_dll(
            self.loaded, "open_cfw_test_grid_width_vals"
        )
        for i, (obj_id, value) in enumerate(pairs):
            ids[i] = obj_id
            vals[i] = value
        self.set_global_u32("open_cfw_test_grid_width_list_len", len(pairs))

    def set_height_map(self, pairs: list[tuple[int, int]]) -> None:
        ids = (ctypes.c_uint32 * 8).in_dll(
            self.loaded, "open_cfw_test_grid_height_ids"
        )
        vals = (ctypes.c_int32 * 8).in_dll(
            self.loaded, "open_cfw_test_grid_height_vals"
        )
        for i, (obj_id, value) in enumerate(pairs):
            ids[i] = obj_id
            vals[i] = value
        self.set_global_u32("open_cfw_test_grid_height_list_len", len(pairs))

    def malloc_ptrs(self) -> list:
        return list(
            (ctypes.c_void_p * 10).in_dll(
                self.loaded, "open_cfw_test_grid_malloc_ptrs"
            )
        )

    def free_ptrs(self) -> list:
        return list(
            (ctypes.c_void_p * 8).in_dll(
                self.loaded, "open_cfw_test_grid_free_ptrs"
            )
        )

    def test_stock_body_hashes_are_pinned(self) -> None:
        application = OFFICIAL.read_bytes()[32:]
        for address, size, expected_sha256, _ in LEAVES:
            with self.subTest(address=hex(address)):
                body = application[address - BASE:address - BASE + size]
                self.assertEqual(len(body), size)
                self.assertEqual(
                    hashlib.sha256(body).hexdigest(), expected_sha256
                )

    def test_spans_do_not_overlap(self) -> None:
        spans = sorted((address, size) for address, size, _, _ in LEAVES)
        for first, second in zip(spans, spans[1:]):
            self.assertLessEqual(first[0] + first[1], second[0])

    def run_calc_cols(self, templ_vals, content_w, gap, children=(),
                      widths=(), flags=0, child_count=None):
        templ = (ctypes.c_int32 * len(templ_vals))(*templ_vals)
        self.buffers.append(templ)
        self.set_ptr_global("open_cfw_test_grid_col_templ_cont", templ)
        self.set_global_s32("open_cfw_test_grid_content_w_value", content_w)
        self.set_prop(0x15, gap)
        self.set_global_u32("open_cfw_test_grid_has_flag_value", flags)
        self.set_child_list(list(children))
        self.set_global_u32(
            "open_cfw_test_grid_child_count_value",
            len(children) if child_count is None else child_count,
        )
        self.set_width_map(list(widths))
        calc = Calc()
        self.buffers.append(calc)
        self.loaded.open_cfw_lvgl_grid_calc_cols(0x1000, ctypes.byref(calc))
        return calc

    def read_int_array(self, ptr, n: int) -> list[int]:
        return [(ctypes.c_int32 * n).from_address(ptr)[i] for i in range(n)]

    def test_calc_cols_fixed_and_fr_distribution(self) -> None:
        calc = self.run_calc_cols([100, FR(2), 50, TEMPLATE_LAST], 500, 10)
        self.assertEqual(calc.col_num, 3)
        self.assertEqual(self.uint("open_cfw_test_grid_malloc_count"), 2)
        self.assertEqual(self.uint("open_cfw_test_grid_free_count"), 0)
        self.assertEqual(self.read_int_array(calc.w, 3), [100, 330, 50])

    def test_calc_cols_content_takes_widest_visible_child(self) -> None:
        self.set_prop(0x84, 1)
        self.set_prop(0x83, 0)
        calc = self.run_calc_cols(
            [CONTENT, 80, TEMPLATE_LAST], 500, 0,
            children=[0x5001, 0x5002],
            widths=[(0x5001, 60), (0x5002, 90)],
        )
        self.assertEqual(self.read_int_array(calc.w, 2), [90, 80])

    def test_calc_cols_hidden_children_measure_zero(self) -> None:
        self.set_prop(0x84, 1)
        self.set_prop(0x83, 0)
        calc = self.run_calc_cols(
            [CONTENT, 80, TEMPLATE_LAST], 500, 0,
            children=[0x5001], widths=[(0x5001, 90)], flags=1,
        )
        self.assertEqual(self.read_int_array(calc.w, 2), [0, 80])

    def test_calc_cols_span_and_pos_filters(self) -> None:
        for span, pos, expected in ((2, 0, 0), (1, 1, 0)):
            with self.subTest(span=span, pos=pos):
                self.loaded.open_cfw_test_grid_reset()
                self.set_prop(0x84, span)
                self.set_prop(0x83, pos)
                calc = self.run_calc_cols(
                    [CONTENT, TEMPLATE_LAST], 500, 0,
                    children=[0x5001], widths=[(0x5001, 90)],
                )
                self.assertEqual(self.read_int_array(calc.w, 1), [expected])

    def test_calc_cols_subgrid_borrows_parent_slice(self) -> None:
        parent_templ = (ctypes.c_int32 * 3)(30, 40, TEMPLATE_LAST)
        self.buffers.append(parent_templ)
        self.set_ptr_global("open_cfw_test_grid_col_templ_cont", None)
        self.set_ptr_global(
            "open_cfw_test_grid_col_templ_parent", parent_templ
        )
        self.set_global_u32("open_cfw_test_grid_parent_value", 0x2000)
        self.set_prop(0x83, 1)
        self.set_prop(0x84, 1)
        self.set_global_s32("open_cfw_test_grid_content_w_value", 500)
        self.set_prop(0x15, 0)
        calc = Calc()
        self.buffers.append(calc)
        self.loaded.open_cfw_lvgl_grid_calc_cols(0x1000, ctypes.byref(calc))
        self.assertEqual(calc.col_num, 1)
        self.assertEqual(self.uint("open_cfw_test_grid_malloc_count"), 3)
        self.assertEqual(self.uint("open_cfw_test_grid_memcpy_calls"), 1)
        self.assertEqual(self.read_int_array(calc.w, 1), [40])
        # The borrowed slice is freed; the x/w outputs are not.
        self.assertEqual(self.uint("open_cfw_test_grid_free_count"), 1)
        self.assertEqual(self.free_ptrs()[0], self.malloc_ptrs()[0])

    def test_calc_cols_double_null_warns_and_returns(self) -> None:
        calc = Calc()
        calc.col_num = 0xBEEF
        self.buffers.append(calc)
        self.set_ptr_global("open_cfw_test_grid_col_templ_cont", None)
        self.set_ptr_global("open_cfw_test_grid_col_templ_parent", None)
        self.loaded.open_cfw_lvgl_grid_calc_cols(0x1000, ctypes.byref(calc))
        self.assertEqual(self.uint("open_cfw_test_grid_log_calls"), 1)
        self.assertEqual(self.sint("open_cfw_test_grid_log_level"), 2)
        self.assertEqual(self.sint("open_cfw_test_grid_log_line"), 0x11D)
        self.assertEqual(self.uint("open_cfw_test_grid_malloc_count"), 0)
        self.assertEqual(calc.col_num, 0xBEEF)

    def test_calc_rows_mirrors_cols(self) -> None:
        templ = (ctypes.c_int32 * 3)(CONTENT, FR(1), TEMPLATE_LAST)
        self.buffers.append(templ)
        self.set_ptr_global("open_cfw_test_grid_row_templ_cont", templ)
        self.set_global_s32("open_cfw_test_grid_content_h_value", 300)
        self.set_prop(0x14, 5)
        self.set_prop(0x87, 1)
        self.set_prop(0x86, 0)
        self.set_child_list([0x5001])
        self.set_global_u32("open_cfw_test_grid_child_count_value", 1)
        self.set_height_map([(0x5001, 70)])
        calc = Calc()
        self.buffers.append(calc)
        self.loaded.open_cfw_lvgl_grid_calc_rows(0x1000, ctypes.byref(calc))
        self.assertEqual(calc.row_num, 2)
        self.assertEqual(self.uint("open_cfw_test_grid_malloc_count"), 2)
        self.assertEqual(self.read_int_array(calc.h, 2), [70, 225])

    def test_calc_rows_double_null_warns(self) -> None:
        calc = Calc()
        self.buffers.append(calc)
        self.set_ptr_global("open_cfw_test_grid_row_templ_cont", None)
        self.set_ptr_global("open_cfw_test_grid_row_templ_parent", None)
        self.loaded.open_cfw_lvgl_grid_calc_rows(0x1000, ctypes.byref(calc))
        self.assertEqual(self.uint("open_cfw_test_grid_log_calls"), 1)
        self.assertEqual(self.sint("open_cfw_test_grid_log_line"), 0x179)

    def run_item_repos(self, col_align=0, row_align=0, base_dir=0,
                       margins=(2, 3, 4, 5), flags_half=0x0C00,
                       coords=(0, 0, 9, 9), tr=(0, 0), size=(10, 10),
                       parent=0x2000):
        self.set_prop(0x83, 0)
        self.set_prop(0x84, 1)
        self.set_prop(0x86, 0)
        self.set_prop(0x87, 1)
        self.set_prop(0x85, col_align)
        self.set_prop(0x88, row_align)
        self.set_prop(0x27, base_dir)
        self.set_prop(0x1A, margins[0])
        self.set_prop(0x1B, margins[1])
        self.set_prop(0x18, margins[2])
        self.set_prop(0x19, margins[3])
        self.set_prop(0x6C, tr[0])
        self.set_prop(0x6D, tr[1])
        self.set_global_s32("open_cfw_test_grid_width_value", size[0])
        self.set_global_s32("open_cfw_test_grid_height_value", size[1])
        self.set_global_u32("open_cfw_test_grid_parent_value", parent)
        item_id = self.fresh_id()
        _, buf = self.make_item(item_id, *coords, flags_half=flags_half)
        x = (ctypes.c_int32 * 2)(10, 60)
        w = (ctypes.c_int32 * 2)(40, 40)
        y = (ctypes.c_int32 * 1)(30)
        h = (ctypes.c_int32 * 1)(20)
        self.buffers.extend([x, w, y, h])
        calc = Calc(
            x=ctypes.addressof(x), y=ctypes.addressof(y),
            w=ctypes.addressof(w), h=ctypes.addressof(h),
        )
        hint = Hint(col=0, row=0, grid_abs_x=100, grid_abs_y=200)
        self.buffers.extend([calc, hint])
        self.loaded.open_cfw_lvgl_grid_item_repos(
            item_id, ctypes.byref(calc), ctypes.byref(hint)
        )
        return buf, item_id

    def test_item_repos_start_places_at_margin(self) -> None:
        buf, item_id = self.run_item_repos()
        self.assertEqual(self.item_coords(buf), [112, 234, 121, 243])
        self.assertEqual(self.item_flags(buf), 0x0000)
        self.assertEqual(self.uint("open_cfw_test_grid_area_set_w_calls"), 0)
        self.assertEqual(self.uint("open_cfw_test_grid_area_set_h_calls"), 0)
        self.assertEqual(self.uint("open_cfw_test_grid_event_calls"), 0)
        self.assertEqual(self.uint("open_cfw_test_grid_invalidate_calls"), 2)
        self.assertEqual(self.uint("open_cfw_test_grid_move_children_calls"), 1)
        self.assertEqual(
            self.uint("open_cfw_test_grid_move_children_obj"), item_id
        )
        self.assertEqual(self.sint("open_cfw_test_grid_move_children_dx"), 112)
        self.assertEqual(self.sint("open_cfw_test_grid_move_children_dy"), 234)
        self.assertEqual(
            self.uint("open_cfw_test_grid_move_children_ignore"), 0
        )
        self.assertEqual(self.uint("open_cfw_test_grid_misses"), 0)

    def test_item_repos_stretch_resizes_and_events(self) -> None:
        buf, _ = self.run_item_repos(col_align=3, flags_half=0)
        self.assertEqual(self.uint("open_cfw_test_grid_area_set_w_calls"), 1)
        self.assertEqual(self.sint("open_cfw_test_grid_area_set_w_value"), 35)
        # The stock body rewrites both axes whenever either one changes.
        self.assertEqual(self.uint("open_cfw_test_grid_area_set_h_calls"), 1)
        self.assertEqual(self.sint("open_cfw_test_grid_area_set_h_value"), 10)
        self.assertEqual(self.uint("open_cfw_test_grid_event_calls"), 2)
        self.assertEqual(self.uint("open_cfw_test_grid_event_code"), 0x2A)
        self.assertEqual(self.uint("open_cfw_test_grid_event_obj"), 0x2000)
        self.assertEqual(self.uint("open_cfw_test_grid_invalidate_calls"), 4)
        self.assertEqual(self.item_flags(buf), 0x0800)
        # x2 was resized to x1+35-1 before the grid-origin move.
        self.assertEqual(self.item_coords(buf), [112, 234, 146, 243])

    def test_item_repos_center_and_end(self) -> None:
        buf, _ = self.run_item_repos(col_align=1, row_align=1)
        coords = self.item_coords(buf)
        self.assertEqual(coords[0], 100 + 25)
        self.assertEqual(coords[1], 200 + 35)
        buf, _ = self.run_item_repos(col_align=2, row_align=2)
        coords = self.item_coords(buf)
        self.assertEqual(coords[0], 100 + 37)
        self.assertEqual(coords[1], 200 + 35)

    def test_item_repos_rtl_mirrors_start_end(self) -> None:
        buf, _ = self.run_item_repos(col_align=0, base_dir=1)
        self.assertEqual(self.item_coords(buf)[0], 100 + 37)
        buf, _ = self.run_item_repos(col_align=2, base_dir=1)
        self.assertEqual(self.item_coords(buf)[0], 100 + 12)

    def test_item_repos_guards_return_early(self) -> None:
        self.set_global_u32("open_cfw_test_grid_has_flag_value", 1)
        self.make_item(0x1000)
        calc, hint = Calc(), Hint()
        self.buffers.extend([calc, hint])
        self.loaded.open_cfw_lvgl_grid_item_repos(
            0x1000, ctypes.byref(calc), ctypes.byref(hint)
        )
        self.assertEqual(self.uint("open_cfw_test_grid_core_calls"), 0)
        self.loaded.open_cfw_test_grid_reset()
        self.set_prop(0x84, 0)
        self.set_prop(0x87, 1)
        self.make_item(0x1000)
        calc, hint = Calc(), Hint()
        self.buffers.extend([calc, hint])
        self.loaded.open_cfw_lvgl_grid_item_repos(
            0x1000, ctypes.byref(calc), ctypes.byref(hint)
        )
        # Only the two span reads happen before the zero-span guard.
        self.assertEqual(self.uint("open_cfw_test_grid_core_calls"), 2)
        self.assertEqual(self.uint("open_cfw_test_grid_invalidate_calls"), 0)

    def test_item_repos_percent_translate(self) -> None:
        pct_pos = 0x20000000 | 50
        buf, _ = self.run_item_repos(tr=(pct_pos, 0))
        self.assertEqual(self.item_coords(buf)[0], 100 + 12 + 5)
        pct_neg = 0x20000000 | (0x0FFFFFFF + 20)
        buf, _ = self.run_item_repos(tr=(pct_neg, 0))
        self.assertEqual(self.item_coords(buf)[0], 100 + 12 - 2)
        buf, _ = self.run_item_repos(tr=(7, 0))
        self.assertEqual(self.item_coords(buf)[0], 100 + 12 + 7)

    def run_align(self, cont_size=100, auto=0, align=0, gap=5,
                  sizes=(10, 20, 30), reverse=0):
        sizes_buf = (ctypes.c_int32 * len(sizes))(*sizes)
        pos_buf = (ctypes.c_int32 * len(sizes))(0)
        self.buffers.extend([sizes_buf, pos_buf])
        total = self.loaded.open_cfw_lvgl_grid_align(
            cont_size, auto, align, gap, len(sizes),
            sizes_buf, pos_buf, reverse,
        )
        return total, list(pos_buf)

    def test_grid_align_modes(self) -> None:
        total, pos = self.run_align(align=0)
        self.assertEqual((total, pos), (70, [0, 15, 40]))
        total, pos = self.run_align(align=1)
        self.assertEqual((total, pos), (70, [15, 30, 55]))
        total, pos = self.run_align(align=2)
        self.assertEqual((total, pos), (70, [30, 45, 70]))
        total, pos = self.run_align(align=6)
        self.assertEqual((total, pos), (100, [0, 30, 70]))
        total, pos = self.run_align(align=5)
        self.assertEqual((total, pos), (86, [6, 29, 62]))
        total, pos = self.run_align(align=4)
        self.assertEqual((total, pos), (80, [10, 30, 60]))

    def test_grid_align_auto_reverse_and_single_track(self) -> None:
        total, pos = self.run_align(auto=1)
        self.assertEqual((total, pos), (70, [0, 15, 40]))
        total, pos = self.run_align(reverse=1)
        self.assertEqual((total, pos), (70, [90, 65, 30]))
        total, pos = self.run_align(align=6, sizes=(10,))
        self.assertEqual((total, pos), (10, [45]))


if __name__ == "__main__":
    unittest.main()
