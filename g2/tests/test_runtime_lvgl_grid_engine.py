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

# (address, size, stock body SHA-256, symbol, LV_STYLE_* property ID,
#  narrows-to-byte)
GETTERS = [
    (0x48C81A, 10, "d130aa374d18864937c42206f57cc1ae758dabeae0c8fc8a0def346d94a56e89", "open_cfw_lvgl_get_style_width", 0x01, False),
    (0x48C824, 10, "1375d228d40adef9593ce8a64446b415135ce5cc53fc65ac4ff34e1d1b27e43d", "open_cfw_lvgl_get_style_height", 0x02, False),
    (0x48C82E, 10, "11d408c0ae3b843214347d8d96f6193d1869fa71febbfb145c628cdbf512ceda", "open_cfw_lvgl_get_style_translate_x", 0x6C, False),
    (0x48C838, 10, "bc08a636bc6ec2f00ebc97b38f77b59c29f2c170b7c4c2c2a3436aae343f4a14", "open_cfw_lvgl_get_style_translate_y", 0x6D, False),
    (0x48C842, 10, "5f8c836b00e9a17f00aa0d8a72ba42ed003058f077e38c96f5c3f8afff74aa60", "open_cfw_lvgl_get_style_pad_top", 0x10, False),
    (0x48C84C, 10, "9ebc7b9748a2b7a74bdee4c8313878cd09656dd5ba93d92483f5c19e2f1c4b8f", "open_cfw_lvgl_get_style_pad_left", 0x12, False),
    (0x48C856, 10, "f16078dc017c205f363b070839a22e3bcff0e038a4eca154d8427bb54a745cf5", "open_cfw_lvgl_get_style_pad_row", 0x14, False),
    (0x48C860, 10, "90db0ebae72e3b69ce2c8bcc1d0ee8198d29f8a8b0030b4a1e72d2002de8fa0c", "open_cfw_lvgl_get_style_pad_column", 0x15, False),
    (0x48C86A, 10, "46fd180724eaf70d0cde2cd77a040871f0b2adb8c1ffe5145f4d2ced45de866f", "open_cfw_lvgl_get_style_margin_top", 0x18, False),
    (0x48C874, 10, "1fe9f0f06db8a3ff9cb12988c641aae8fd8ba081cff37af634c576341296e5e7", "open_cfw_lvgl_get_style_margin_bottom", 0x19, False),
    (0x48C87E, 10, "223c350bd61a4252438cbadb40f8a6a79e422a733ab8b68094799ed9f1a5ef2f", "open_cfw_lvgl_get_style_margin_left", 0x1A, False),
    (0x48C888, 10, "b8f3e67ae191b91b39add6a3fd71381ddbcaa68e94ae5567c10ab7d7bbce8406", "open_cfw_lvgl_get_style_margin_right", 0x1B, False),
    (0x48C892, 10, "81bc5be45f4ac10c0204b44572e2c84d2257fc57a7a8c0cec9359a9c3b494084", "open_cfw_lvgl_get_style_border_width", 0x30, False),
    (0x48C89C, 12, "e3431a6c8e4986209d3174e9e21be751abf19035435fdc0a2177309f593791e8", "open_cfw_lvgl_get_style_border_side", 0x34, True),
    (0x48C8A8, 12, "88d91ba68e179265fa686937f6322d60e6896ac12f6140c4447e6f3eacc6484a", "open_cfw_lvgl_get_style_base_dir", 0x27, True),
    (0x48C8B4, 10, "ba0a16d9807b9ce58e365294bec600bb01b69ecf87b9f79b45209b16053f765a", "open_cfw_lvgl_get_style_grid_column_dsc_array", 0x82, False),
    (0x48C8BE, 12, "0252503627231159cb2fae3bf8d37ca1470e009e31d11f3fe2dc57529bbf9218", "open_cfw_lvgl_get_style_grid_column_align", 0x7F, True),
    (0x48C8CA, 10, "245e9a5104de354c02ecc080dbdf8df1e2428c00a87db575595bfd765c673d42", "open_cfw_lvgl_get_style_grid_row_dsc_array", 0x81, False),
    (0x48C8D4, 12, "2dbc32e3a550464c6011aa389b6d9f6868de05befb04ac466fb6d397a0828444", "open_cfw_lvgl_get_style_grid_row_align", 0x80, True),
    (0x48C8E0, 10, "c353b84d18f06b886553db4f83e931692d38f463d887d74f4f48995d9c0b130d", "open_cfw_lvgl_get_style_grid_cell_column_pos", 0x83, False),
    (0x48C8EA, 12, "f620cbb432c04a3471aaa4acdf3c14d547c901be9c3469203f7b5e0792700ff8", "open_cfw_lvgl_get_style_grid_cell_x_align", 0x85, True),
    (0x48C8F6, 10, "49a1adae0a8a72163a21a5f0b2849bdab6ada5f88805140f53a4d8494e6a3759", "open_cfw_lvgl_get_style_grid_cell_column_span", 0x84, False),
    (0x48C900, 10, "c757d823282472c02297d0a833f7b3d4898d07eaff977b08e05013df4000892d", "open_cfw_lvgl_get_style_grid_cell_row_pos", 0x86, False),
    (0x48C90A, 12, "64d1dec03235998919bc1d31db1ffd9f1a3f5a82505f184e155d66fac6ef5c22", "open_cfw_lvgl_get_style_grid_cell_y_align", 0x88, True),
    (0x48C916, 10, "cff20649b47374922ee77b914b5320c36d961fae44a04681536df1ae709f85a0", "open_cfw_lvgl_get_style_grid_cell_row_span", 0x87, False),
]

# (address, size, stock body SHA-256, port symbol, forwarded getter symbol)
WRAPPERS = [
    (0x48C97C, 10, "85c8ca8ef896ba65998e5b220c432e3efc91401bd9d60779a0175815f577c52c", "open_cfw_lvgl_grid_get_col_dsc", "open_cfw_lvgl_get_style_grid_column_dsc_array"),
    (0x48C986, 10, "4a13a0fa0340e9695f22cb7a013589cf7091f431bef8695e3cf31f4806fab8bd", "open_cfw_lvgl_grid_get_row_dsc", "open_cfw_lvgl_get_style_grid_row_dsc_array"),
    (0x48C990, 10, "36c58accd79b63c08fd7159db7ce0e6ea9efbd5d463ce611aad406422a23a39b", "open_cfw_lvgl_grid_get_col_pos", "open_cfw_lvgl_get_style_grid_cell_column_pos"),
    (0x48C99A, 10, "b44f8ef4d80c823d47a1a401ce8ce1825a5fc0926beeb33081e496774503404a", "open_cfw_lvgl_grid_get_row_pos", "open_cfw_lvgl_get_style_grid_cell_row_pos"),
    (0x48C9A4, 10, "3c0baee07dbe48678585de88cf7a9e0a5506c40626813ab8a1a7bc704560af02", "open_cfw_lvgl_grid_get_col_span", "open_cfw_lvgl_get_style_grid_cell_column_span"),
    (0x48C9AE, 10, "1c2eee170f777591969250d264e0dcdc19a79f5b539867b00c24296a933fed83", "open_cfw_lvgl_grid_get_row_span", "open_cfw_lvgl_get_style_grid_cell_row_span"),
    (0x48C9B8, 10, "d8743aecb470d4c82f8079ebc70e544edfcebbf74b5f490e7466e6ca9212a16c", "open_cfw_lvgl_grid_get_cell_col_align", "open_cfw_lvgl_get_style_grid_cell_x_align"),
    (0x48C9C2, 10, "58e0afb093ad10dab09953aa19dc42d16e46f3ea50db9814a424d43bc66c18ad", "open_cfw_lvgl_grid_get_cell_row_align", "open_cfw_lvgl_get_style_grid_cell_y_align"),
    (0x48C9CC, 10, "1574a28cc152598264945ec44484ff8e4805d839279953d1bf970d477bdcbafc", "open_cfw_lvgl_grid_get_grid_col_align", "open_cfw_lvgl_get_style_grid_column_align"),
    (0x48C9D6, 10, "75f2d4272345c7aca6e79bd16c93e03f4a76d79bf8a3e4e547e228b7ae4ad227", "open_cfw_lvgl_grid_get_grid_row_align", "open_cfw_lvgl_get_style_grid_row_align"),
]

# (address, size, stock body SHA-256, port symbol)
LEAVES = [
    (0x48C7B4, 36, "3ebd13a74a860e2778ddb6329b3a2eddb33384e64f9a20a1a60957f0abdf5922", "open_cfw_lvgl_obj_get_width_with_margin"),
    (0x48C7D8, 36, "bc71e5dd41807ad1fb3bf1c28c30323fc3888d146801177520e918662715d36d", "open_cfw_lvgl_obj_get_height_with_margin"),
    (0x48C7FC, 18, "f73e45d66d1de715a1cb3942d89782eb1b96f870340fc063782c50ee367fc9a6", "open_cfw_lvgl_area_copy"),
    (0x48C80E, 12, "8ebfea69619b4c79986e2199b360c7f84ab47f6f062f7b811a36d7b8a26cf4c9", "open_cfw_lvgl_memzero"),
    (0x48C920, 46, "d864297772df46eb580d8c3927e5d86a4093680da9512072f4fc841064de6008", "open_cfw_lvgl_get_style_space_left"),
    (0x48C94E, 46, "bb77d63c96d9cf3e69d8b935f9295559178558f4a6e565e6eb28c4d699752733", "open_cfw_lvgl_get_style_space_top"),
    (0x48C9E0, 28, "ca0fbfec13a51be12fbac6bee1ad96d722b77b27069d8e149126c2cbbdb34f6c", "open_cfw_lvgl_grid_get_margin_hor"),
    (0x48C9FC, 28, "d5cbcedc4cd8620d5811fc22c20af8897ac1dc6793e70be4ba61ff37c69a5001", "open_cfw_lvgl_grid_get_margin_ver"),
    (0x48CA18, 14, "015d5e36e063f3dabf2cbcb91038b8f72d9cbaa923893460e5226f76a72c9dba", "open_cfw_lvgl_grid_div_round_closest"),
    (0x48CA26, 20, "fc7b2969e91adc5c310f855749394e0be1b25ddd158df1d94ff007cbae58b36e", "open_cfw_lvgl_grid_init"),
    (0x48CA3C, 156, "e468bf9012ffee3624144df6b945aa1271abf0681203c25fb25a89797488d1a4", "open_cfw_lvgl_grid_update"),
    (0x48CAD8, 258, "1beed69748ac9ad61c62013330426d1092f0f576732d083740be6ce835d7782f", "open_cfw_lvgl_grid_calc"),
    (0x48CBDA, 30, "8f749b0d78234162cffa5faa66e076c2b10cfb243ab8c2039a569230191d2736", "open_cfw_lvgl_grid_calc_free"),
    (0x48D4D0, 22, "2b65221b1e207b520cc666835bafa78c16bf4b684c2e9d8b34ca7842ba8f4b1d", "open_cfw_lvgl_grid_count_tracks"),
]

ALL_SPANS = (
    [(address, size, sha) for address, size, sha, _, _, _ in GETTERS]
    + [(address, size, sha) for address, size, sha, _, _ in WRAPPERS]
    + [(address, size, sha) for address, size, sha, _ in LEAVES]
)


class GridEngineTests(unittest.TestCase):
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
        cls.getters = {}
        for _, _, _, name, _, _ in GETTERS:
            fn = getattr(lib, name)
            fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
            fn.restype = ctypes.c_uint32
            cls.getters[name] = fn
        cls.wrappers = {}
        for _, _, _, name, _ in WRAPPERS:
            fn = getattr(lib, name)
            fn.argtypes = [ctypes.c_uint32]
            fn.restype = ctypes.c_uint32
            cls.wrappers[name] = fn
        lib.open_cfw_lvgl_obj_get_width_with_margin.argtypes = [ctypes.c_uint32]
        lib.open_cfw_lvgl_obj_get_width_with_margin.restype = ctypes.c_int32
        lib.open_cfw_lvgl_obj_get_height_with_margin.argtypes = [ctypes.c_uint32]
        lib.open_cfw_lvgl_obj_get_height_with_margin.restype = ctypes.c_int32
        lib.open_cfw_lvgl_area_copy.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        lib.open_cfw_lvgl_area_copy.restype = None
        lib.open_cfw_lvgl_memzero.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        lib.open_cfw_lvgl_memzero.restype = None
        lib.open_cfw_lvgl_get_style_space_left.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        lib.open_cfw_lvgl_get_style_space_left.restype = ctypes.c_uint32
        lib.open_cfw_lvgl_get_style_space_top.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        lib.open_cfw_lvgl_get_style_space_top.restype = ctypes.c_uint32
        lib.open_cfw_lvgl_grid_get_margin_hor.argtypes = [ctypes.c_uint32]
        lib.open_cfw_lvgl_grid_get_margin_hor.restype = ctypes.c_int32
        lib.open_cfw_lvgl_grid_get_margin_ver.argtypes = [ctypes.c_uint32]
        lib.open_cfw_lvgl_grid_get_margin_ver.restype = ctypes.c_int32
        lib.open_cfw_lvgl_grid_div_round_closest.argtypes = [ctypes.c_int32, ctypes.c_int32]
        lib.open_cfw_lvgl_grid_div_round_closest.restype = ctypes.c_int32
        lib.open_cfw_lvgl_grid_init.argtypes = []
        lib.open_cfw_lvgl_grid_init.restype = None
        lib.open_cfw_lvgl_grid_update.argtypes = [ctypes.c_uint32]
        lib.open_cfw_lvgl_grid_update.restype = None
        lib.open_cfw_lvgl_grid_calc.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
        lib.open_cfw_lvgl_grid_calc.restype = None
        lib.open_cfw_lvgl_grid_calc_free.argtypes = [ctypes.c_void_p]
        lib.open_cfw_lvgl_grid_calc_free.restype = None
        lib.open_cfw_lvgl_grid_count_tracks.argtypes = [ctypes.c_void_p]
        lib.open_cfw_lvgl_grid_count_tracks.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def setUp(self) -> None:
        self.loaded.open_cfw_test_grid_reset()
        type(self).buffers = []

    def uint(self, name: str) -> int:
        return ctypes.c_uint32.in_dll(self.loaded, name).value

    def sint(self, name: str) -> int:
        return ctypes.c_int32.in_dll(self.loaded, name).value

    def ptr(self, name: str) -> int | None:
        return ctypes.c_void_p.in_dll(self.loaded, name).value

    def set_prop(self, prop: int, value: int) -> None:
        table = (ctypes.c_uint32 * 256).in_dll(
            self.loaded, "open_cfw_test_grid_prop_value"
        )
        table[prop & 0xFF] = value & 0xFFFFFFFF

    def set_global_u32(self, name: str, value: int) -> None:
        ctypes.c_uint32.in_dll(self.loaded, name).value = value & 0xFFFFFFFF

    def set_global_s32(self, name: str, value: int) -> None:
        ctypes.c_int32.in_dll(self.loaded, name).value = value

    def make_buffer(self, size: int) -> ctypes.Array:
        buf = (ctypes.c_uint8 * size)()
        type(self).buffers.append(buf)
        return buf

    def register(self, obj_id: int, buf) -> int:
        self.loaded.open_cfw_test_grid_register(obj_id, ctypes.addressof(buf))
        type(self).buffers.append(buf)
        return obj_id

    def make_obj(self, obj_id: int, x1=0, y1=0, flags_half=0, spec_id=0):
        buf = self.make_buffer(64)
        struct.pack_into("<i", buf, 0x14, x1)
        struct.pack_into("<i", buf, 0x18, y1)
        struct.pack_into("<I", buf, 0x08, spec_id)
        struct.pack_into("<H", buf, 0x2A, flags_half)
        return self.register(obj_id, buf)

    def make_spec(self, spec_id: int, children_id: int, count: int):
        buf = self.make_buffer(64)
        struct.pack_into("<I", buf, 0x00, children_id)
        struct.pack_into("<H", buf, 0x30, count)
        return self.register(spec_id, buf)

    def make_children(self, array_id: int, child_ids: list[int]):
        buf = (ctypes.c_uint32 * len(child_ids))(*child_ids)
        return self.register(array_id, buf)

    def test_stock_body_hashes_are_pinned(self) -> None:
        application = OFFICIAL.read_bytes()[32:]
        for address, size, expected_sha256 in ALL_SPANS:
            with self.subTest(address=hex(address)):
                body = application[address - BASE:address - BASE + size]
                self.assertEqual(len(body), size)
                self.assertEqual(
                    hashlib.sha256(body).hexdigest(), expected_sha256
                )

    def test_spans_do_not_overlap(self) -> None:
        spans = sorted(ALL_SPANS)
        for first, second in zip(spans, spans[1:]):
            self.assertLessEqual(first[0] + first[1], second[0])

    def test_every_getter_forwards_obj_part_and_its_property_id(self) -> None:
        for _, _, _, name, property_id, narrows in GETTERS:
            with self.subTest(getter=name):
                self.loaded.open_cfw_test_grid_reset()
                self.set_prop(property_id, 0x123456AB)
                result = self.getters[name](0xAAAA0000 | property_id, 0x03)
                self.assertEqual(
                    self.uint("open_cfw_test_grid_core_calls"), 1
                )
                self.assertEqual(
                    self.uint("open_cfw_test_grid_core_obj"),
                    0xAAAA0000 | property_id,
                )
                self.assertEqual(
                    self.uint("open_cfw_test_grid_core_part"), 0x03
                )
                self.assertEqual(
                    self.uint("open_cfw_test_grid_core_prop"), property_id
                )
                self.assertEqual(result, 0xAB if narrows else 0x123456AB)

    def test_grid_wrappers_forward_obj_with_part_zero(self) -> None:
        prop_of = {name: prop for _, _, _, name, prop, _ in GETTERS}
        trunc_of = {name: trunc for _, _, _, name, _, trunc in GETTERS}
        for _, _, _, name, getter in WRAPPERS:
            with self.subTest(wrapper=name):
                self.loaded.open_cfw_test_grid_reset()
                self.set_prop(prop_of[getter], 0x55AA)
                result = self.wrappers[name](0x1000)
                self.assertEqual(
                    self.uint("open_cfw_test_grid_core_calls"), 1
                )
                self.assertEqual(self.uint("open_cfw_test_grid_core_obj"), 0x1000)
                self.assertEqual(self.uint("open_cfw_test_grid_core_part"), 0)
                self.assertEqual(
                    self.uint("open_cfw_test_grid_core_prop"), prop_of[getter]
                )
                self.assertEqual(result, 0xAA if trunc_of[getter] else 0x55AA)

    def test_space_left_adds_border_only_when_side_set(self) -> None:
        for side, expected in ((0x04, 10 + 2), (0x02, 10), (0x00, 10), (0x0F, 12)):
            with self.subTest(side=hex(side)):
                self.loaded.open_cfw_test_grid_reset()
                self.set_prop(0x12, 10)
                self.set_prop(0x30, 2)
                self.set_prop(0x34, side)
                result = self.loaded.open_cfw_lvgl_get_style_space_left(0x1000, 7)
                self.assertEqual(result, expected)
                self.assertEqual(
                    self.uint("open_cfw_test_grid_core_calls"), 3
                )
                self.assertEqual(self.uint("open_cfw_test_grid_core_part"), 7)

    def test_space_top_adds_border_only_when_side_set(self) -> None:
        for side, expected in ((0x02, 5 + 3), (0x04, 5), (0x00, 5), (0x0F, 8)):
            with self.subTest(side=hex(side)):
                self.loaded.open_cfw_test_grid_reset()
                self.set_prop(0x10, 5)
                self.set_prop(0x30, 3)
                self.set_prop(0x34, side)
                result = self.loaded.open_cfw_lvgl_get_style_space_top(0x1000, 9)
                self.assertEqual(result, expected)

    def test_width_and_height_with_margin_sum_three_terms(self) -> None:
        self.set_prop(0x1A, 3)
        self.set_prop(0x1B, 5)
        self.set_global_s32("open_cfw_test_grid_width_value", 100)
        result = self.loaded.open_cfw_lvgl_obj_get_width_with_margin(0x1000)
        self.assertEqual(result, 108)
        self.assertEqual(self.uint("open_cfw_test_grid_width_obj"), 0x1000)
        self.set_prop(0x18, 7)
        self.set_prop(0x19, 9)
        self.set_global_s32("open_cfw_test_grid_height_value", 200)
        result = self.loaded.open_cfw_lvgl_obj_get_height_with_margin(0x1000)
        self.assertEqual(result, 216)
        self.assertEqual(self.uint("open_cfw_test_grid_height_obj"), 0x1000)

    def test_margin_hor_ver_and_div_round(self) -> None:
        self.set_prop(0x1A, 4)
        self.set_prop(0x1B, 6)
        self.set_prop(0x18, 2)
        self.set_prop(0x19, 8)
        self.assertEqual(self.loaded.open_cfw_lvgl_grid_get_margin_hor(0x1000), 10)
        self.assertEqual(self.loaded.open_cfw_lvgl_grid_get_margin_ver(0x1000), 10)
        div = self.loaded.open_cfw_lvgl_grid_div_round_closest
        self.assertEqual(div(7, 2), 4)
        self.assertEqual(div(8, 2), 4)
        self.assertEqual(div(0, 5), 0)
        self.assertEqual(div(-7, 2), -3)
        self.assertEqual(div(100, 3), 33)

    def test_area_copy_and_memzero_move_bytes(self) -> None:
        src = (ctypes.c_int32 * 4)(1, -2, 300, -400)
        dst = (ctypes.c_int32 * 4)(0, 0, 0, 0)
        self.buffers.extend([src, dst])
        self.loaded.open_cfw_lvgl_area_copy(dst, src)
        self.assertEqual(list(dst), [1, -2, 300, -400])
        self.assertEqual(list(src), [1, -2, 300, -400])
        buf = (ctypes.c_uint8 * 10)(*([0xAA] * 10))
        self.buffers.append(buf)
        self.loaded.open_cfw_lvgl_memzero(buf, 6)
        self.assertEqual(list(buf), [0] * 6 + [0xAA] * 4)
        self.assertEqual(self.uint("open_cfw_test_grid_memset_calls"), 1)
        self.assertEqual(self.uint("open_cfw_test_grid_memset_value"), 0)
        self.assertEqual(self.uint("open_cfw_test_grid_memset_len"), 6)
        self.assertEqual(self.ptr("open_cfw_test_grid_memset_dst"), ctypes.addressof(buf))

    def test_count_tracks_stops_at_template_last(self) -> None:
        templ = (ctypes.c_uint32 * 4)(10, 20, 0x1FFFFFFF, 99)
        self.buffers.append(templ)
        self.assertEqual(self.loaded.open_cfw_lvgl_grid_count_tracks(templ), 2)
        empty = (ctypes.c_uint32 * 1)(0x1FFFFFFF)
        self.buffers.append(empty)
        self.assertEqual(self.loaded.open_cfw_lvgl_grid_count_tracks(empty), 0)

    def test_calc_free_releases_xywh_in_order(self) -> None:
        blobs = [(ctypes.c_uint8 * 4)() for _ in range(4)]
        self.buffers.extend(blobs)

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

        calc = Calc()
        addrs = [ctypes.addressof(b) for b in blobs]
        calc.x, calc.y, calc.w, calc.h = addrs
        self.buffers.append(calc)
        self.loaded.open_cfw_lvgl_grid_calc_free(ctypes.byref(calc))
        self.assertEqual(self.uint("open_cfw_test_grid_free_count"), 4)
        seen = (ctypes.c_void_p * 8).in_dll(
            self.loaded, "open_cfw_test_grid_free_ptrs"
        )
        self.assertEqual([seen[i] for i in range(4)], addrs)

    def test_calc_empty_container_memzeroes_and_returns(self) -> None:
        self.set_global_u32("open_cfw_test_grid_child_value", 0)

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

        calc = Calc()
        calc.x = 0xDEAD
        calc.grid_w = 1234
        self.buffers.append(calc)
        self.loaded.open_cfw_lvgl_grid_calc(0x1000, ctypes.byref(calc))
        self.assertEqual(self.uint("open_cfw_test_grid_child_calls"), 1)
        self.assertEqual(self.uint("open_cfw_test_grid_child_idx"), 0)
        self.assertEqual(self.uint("open_cfw_test_grid_cols_calls"), 0)
        self.assertEqual(self.uint("open_cfw_test_grid_rows_calls"), 0)
        self.assertEqual(self.uint("open_cfw_test_grid_align_calls"), 0)
        self.assertEqual(self.uint("open_cfw_test_grid_memset_calls"), 1)
        self.assertEqual(
            self.uint("open_cfw_test_grid_memset_len"), ctypes.sizeof(Calc)
        )
        self.assertEqual(calc.x, None)
        self.assertEqual(calc.col_num, 0)
        self.assertEqual(calc.grid_w, 0)
        self.assertEqual(self.uint("open_cfw_test_grid_misses"), 0)

    def run_calc_scenario(self, base_dir, w_set, h_set, flags_half):
        self.loaded.open_cfw_test_grid_reset()
        self.set_global_u32("open_cfw_test_grid_child_value", 0x9999)
        self.set_global_u32("open_cfw_test_grid_cols_num", 3)
        self.set_global_u32("open_cfw_test_grid_rows_num", 2)
        self.set_prop(0x15, 11)
        self.set_prop(0x14, 13)
        self.set_prop(0x27, base_dir)
        self.set_prop(0x01, w_set)
        self.set_prop(0x02, h_set)
        self.set_prop(0x7F, 4)
        self.set_prop(0x80, 5)
        self.set_global_s32("open_cfw_test_grid_content_w_value", 1000)
        self.set_global_s32("open_cfw_test_grid_content_h_value", 800)
        self.set_global_s32("open_cfw_test_grid_align_value", 777)
        self.make_obj(0x1000, flags_half=flags_half)

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

        calc = Calc()
        x = (ctypes.c_int32 * 3)(0, 0, 0)
        y = (ctypes.c_int32 * 2)(0, 0)
        w = (ctypes.c_int32 * 3)(0, 0, 0)
        h = (ctypes.c_int32 * 2)(0, 0)
        self.buffers.extend([calc, x, y, w, h])
        calc.x = ctypes.addressof(x)
        calc.y = ctypes.addressof(y)
        calc.w = ctypes.addressof(w)
        calc.h = ctypes.addressof(h)
        self.loaded.open_cfw_lvgl_grid_calc(0x1000, ctypes.byref(calc))
        return calc, (x, y, w, h)

    def test_calc_full_sequence_and_stores(self) -> None:
        calc, (x, y, w, h) = self.run_calc_scenario(
            base_dir=0, w_set=0x3FFFFFFF, h_set=400, flags_half=0
        )
        self.assertEqual(self.uint("open_cfw_test_grid_rows_calls"), 1)
        self.assertEqual(self.uint("open_cfw_test_grid_cols_calls"), 1)
        self.assertEqual(self.uint("open_cfw_test_grid_rows_cont"), 0x1000)
        self.assertEqual(self.uint("open_cfw_test_grid_cols_cont"), 0x1000)
        self.assertEqual(self.uint("open_cfw_test_grid_align_calls"), 2)
        size = (ctypes.c_int32 * 2).in_dll(
            self.loaded, "open_cfw_test_grid_align_size"
        )
        auto = (ctypes.c_uint32 * 2).in_dll(
            self.loaded, "open_cfw_test_grid_align_auto"
        )
        align = (ctypes.c_uint32 * 2).in_dll(
            self.loaded, "open_cfw_test_grid_align_align"
        )
        gap = (ctypes.c_uint32 * 2).in_dll(
            self.loaded, "open_cfw_test_grid_align_gap"
        )
        num = (ctypes.c_uint32 * 2).in_dll(
            self.loaded, "open_cfw_test_grid_align_num"
        )
        reverse = (ctypes.c_uint32 * 2).in_dll(
            self.loaded, "open_cfw_test_grid_align_reverse"
        )
        sizes = (ctypes.c_void_p * 2).in_dll(
            self.loaded, "open_cfw_test_grid_align_sizes"
        )
        positions = (ctypes.c_void_p * 2).in_dll(
            self.loaded, "open_cfw_test_grid_align_positions"
        )
        self.assertEqual([size[i] for i in range(2)], [1000, 800])
        self.assertEqual([auto[i] for i in range(2)], [1, 0])
        self.assertEqual([align[i] for i in range(2)], [4, 5])
        self.assertEqual([gap[i] for i in range(2)], [11, 13])
        self.assertEqual([num[i] for i in range(2)], [3, 2])
        self.assertEqual([reverse[i] for i in range(2)], [0, 0])
        self.assertEqual(
            [sizes[i] for i in range(2)],
            [ctypes.addressof(w), ctypes.addressof(h)],
        )
        self.assertEqual(
            [positions[i] for i in range(2)],
            [ctypes.addressof(x), ctypes.addressof(y)],
        )
        self.assertEqual(calc.grid_w, 777)
        self.assertEqual(calc.grid_h, 777)
        self.assertEqual(self.uint("open_cfw_test_grid_misses"), 0)

    def test_calc_rtl_sets_reverse_and_layout_bit_clears_auto(self) -> None:
        calc, _ = self.run_calc_scenario(
            base_dir=1, w_set=0x3FFFFFFF, h_set=0x3FFFFFFF,
            flags_half=(1 << 11) | (1 << 10),
        )
        reverse = (ctypes.c_uint32 * 2).in_dll(
            self.loaded, "open_cfw_test_grid_align_reverse"
        )
        auto = (ctypes.c_uint32 * 2).in_dll(
            self.loaded, "open_cfw_test_grid_align_auto"
        )
        self.assertEqual([reverse[i] for i in range(2)], [1, 0])
        self.assertEqual([auto[i] for i in range(2)], [0, 0])
        self.assertEqual(calc.grid_w, 777)
        self.assertEqual(calc.grid_h, 777)

    def run_update_scenario(self, w_set, h_set):
        self.loaded.open_cfw_test_grid_reset()
        self.set_prop(0x12, 10)
        self.set_prop(0x10, 5)
        self.set_prop(0x30, 2)
        self.set_prop(0x34, 0x04)
        self.set_global_s32("open_cfw_test_grid_scroll_x_value", 7)
        self.set_global_s32("open_cfw_test_grid_scroll_y_value", 9)
        self.set_global_u32("open_cfw_test_grid_child_value", 0x9999)
        self.set_global_u32("open_cfw_test_grid_cols_num", 1)
        self.set_global_u32("open_cfw_test_grid_rows_num", 1)
        self.set_prop(0x15, 0)
        self.set_prop(0x14, 0)
        self.set_prop(0x27, 0)
        self.set_prop(0x01, w_set)
        self.set_prop(0x02, h_set)
        self.set_prop(0x7F, 0)
        self.set_prop(0x80, 0)
        self.set_global_s32("open_cfw_test_grid_content_w_value", 500)
        self.set_global_s32("open_cfw_test_grid_content_h_value", 600)
        self.set_global_s32("open_cfw_test_grid_align_value", 42)
        self.make_children(0x3000, [0x4001, 0x4002])
        self.make_spec(0x2000, 0x3000, 2)
        self.make_obj(0x1000, x1=100, y1=200, spec_id=0x2000)
        self.make_obj(0x4001)
        self.make_obj(0x4002)
        self.loaded.open_cfw_lvgl_grid_update(0x1000)

    def test_grid_update_repositions_children_and_refreshes(self) -> None:
        self.run_update_scenario(w_set=0x3FFFFFFF, h_set=300)
        self.assertEqual(self.uint("open_cfw_test_grid_repos_count"), 2)
        items = (ctypes.c_uint32 * 8).in_dll(
            self.loaded, "open_cfw_test_grid_repos_items"
        )
        self.assertEqual([items[i] for i in range(2)], [0x4001, 0x4002])
        hint_x = (ctypes.c_int32 * 8).in_dll(
            self.loaded, "open_cfw_test_grid_repos_hint_x"
        )
        hint_y = (ctypes.c_int32 * 8).in_dll(
            self.loaded, "open_cfw_test_grid_repos_hint_y"
        )
        self.assertEqual([hint_x[i] for i in range(2)], [100 + 12 - 7] * 2)
        self.assertEqual([hint_y[i] for i in range(2)], [200 + 5 - 9] * 2)
        self.assertEqual(self.uint("open_cfw_test_grid_free_count"), 4)
        self.assertEqual(self.uint("open_cfw_test_grid_refr_calls"), 1)
        self.assertEqual(self.uint("open_cfw_test_grid_refr_obj"), 0x1000)
        self.assertEqual(self.uint("open_cfw_test_grid_event_calls"), 1)
        self.assertEqual(self.uint("open_cfw_test_grid_event_obj"), 0x1000)
        self.assertEqual(self.uint("open_cfw_test_grid_event_code"), 0x33)
        self.assertEqual(self.uint("open_cfw_test_grid_event_param"), 0)
        self.assertEqual(self.uint("open_cfw_test_grid_misses"), 0)

    def test_grid_update_skips_refresh_for_fixed_size(self) -> None:
        self.run_update_scenario(w_set=320, h_set=240)
        self.assertEqual(self.uint("open_cfw_test_grid_repos_count"), 2)
        self.assertEqual(self.uint("open_cfw_test_grid_refr_calls"), 0)
        self.assertEqual(self.uint("open_cfw_test_grid_event_calls"), 1)
        self.assertEqual(self.uint("open_cfw_test_grid_event_code"), 0x33)

    def test_grid_update_empty_container_repositions_nothing(self) -> None:
        self.loaded.open_cfw_test_grid_reset()
        self.set_prop(0x12, 1)
        self.set_prop(0x10, 2)
        self.set_prop(0x30, 0)
        self.set_prop(0x34, 0)
        self.set_global_s32("open_cfw_test_grid_scroll_x_value", 0)
        self.set_global_s32("open_cfw_test_grid_scroll_y_value", 0)
        self.set_global_u32("open_cfw_test_grid_child_value", 0)
        self.set_prop(0x01, 320)
        self.set_prop(0x02, 240)
        self.make_children(0x3000, [])
        self.make_spec(0x2000, 0x3000, 0)
        self.make_obj(0x1000, x1=10, y1=20, spec_id=0x2000)
        self.loaded.open_cfw_lvgl_grid_update(0x1000)
        self.assertEqual(self.uint("open_cfw_test_grid_repos_count"), 0)
        self.assertEqual(self.uint("open_cfw_test_grid_refr_calls"), 0)
        self.assertEqual(self.uint("open_cfw_test_grid_event_calls"), 1)

    def test_grid_init_registers_update_entry(self) -> None:
        anchor = (ctypes.c_uint32 * 32)()
        slot = (ctypes.c_uint32 * 32)()
        self.buffers.extend([anchor, slot])
        anchor[0x5C // 4] = 0xA001
        self.register(0xA000, anchor)
        self.register(0xA001, slot)
        self.loaded.open_cfw_lvgl_grid_init()
        self.assertEqual(slot[0x10 // 4], 0x0048CA3D)
        self.assertEqual(slot[0x14 // 4], 0)
        self.assertEqual(self.uint("open_cfw_test_grid_misses"), 0)


if __name__ == "__main__":
    unittest.main()
