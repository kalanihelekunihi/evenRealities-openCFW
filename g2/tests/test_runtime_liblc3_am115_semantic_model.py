import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT /
    "components/apollo_main/core_overlay/runtime_liblc3_am115_semantic_model.c"
)


class Inputs546e02(ctypes.Structure):
    _fields_ = [
        ("gate_word", ctypes.c_uint32),
    ]


class Outputs546e02(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("r1", ctypes.c_uint32),
        ("call_r0", ctypes.c_uint32),
        ("call_r1", ctypes.c_uint32),
        ("call_target", ctypes.c_uint32),
        ("branch_to_call", ctypes.c_int),
        ("call_performed", ctypes.c_int),
    ]


class Outputs5455c6(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("stack_adjust_bytes", ctypes.c_uint32),
        ("restored_r4", ctypes.c_uint32),
        ("returned_via_pop_pc", ctypes.c_uint32),
        ("bounded_return_prefix_bytes", ctypes.c_uint32),
        ("post_return_boundary_bytes", ctypes.c_uint32),
    ]


class Inputs545ec4(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("r1", ctypes.c_uint32),
    ]


class Outputs545ec4(ctypes.Structure):
    _fields_ = [
        ("call_target", ctypes.c_uint32),
        ("call_r0", ctypes.c_uint32),
        ("call_r1", ctypes.c_uint32),
        ("return_register_passthrough", ctypes.c_uint32),
    ]


class RuntimeLiblc3Am115SemanticModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmpdir = tempfile.TemporaryDirectory()
        cls.lib_path = Path(cls.tmpdir.name) / "libam115_semantic.dylib"
        subprocess.run(
            [
                "clang",
                "-std=c11",
                "-shared",
                "-fPIC",
                "-O2",
                "-Wall",
                "-Wextra",
                "-Werror",
                str(SOURCE),
                "-o",
                str(cls.lib_path),
            ],
            cwd=ROOT,
            check=True,
        )
        cls.lib = ctypes.CDLL(str(cls.lib_path))
        cls.model = cls.lib.open_cfw_am115_0x546e02_semantic_model
        cls.model.argtypes = [Inputs546e02]
        cls.model.restype = Outputs546e02
        cls.model_5455c6 = cls.lib.open_cfw_am115_0x5455c6_semantic_model
        cls.model_5455c6.argtypes = []
        cls.model_5455c6.restype = Outputs5455c6
        cls.model_545ec4 = cls.lib.open_cfw_am115_0x545ec4_semantic_model
        cls.model_545ec4.argtypes = [Inputs545ec4]
        cls.model_545ec4.restype = Outputs545ec4

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmpdir.cleanup()

    def test_gate_word_one_calls_literal_target_and_returns_zero(self) -> None:
        out = self.model(Inputs546e02(1))

        self.assertEqual(out.r0, 0)
        self.assertEqual(out.r1, 0x200031B4)
        self.assertEqual(out.call_r0, 0x0078E144)
        self.assertEqual(out.call_r1, 0x200031B4)
        self.assertEqual(out.call_target, 0x0043B40E)
        self.assertEqual(out.branch_to_call, 1)
        self.assertEqual(out.call_performed, 1)

    def test_other_gate_words_skip_call_and_return_zero(self) -> None:
        for gate_word in (0, 2, 0xFFFFFFFF):
            with self.subTest(gate_word=gate_word):
                out = self.model(Inputs546e02(gate_word))

                self.assertEqual(out.r0, 0)
                self.assertEqual(out.r1, 0)
                self.assertEqual(out.call_r0, 0)
                self.assertEqual(out.call_r1, 0)
                self.assertEqual(out.call_target, 0)
                self.assertEqual(out.branch_to_call, 0)
                self.assertEqual(out.call_performed, 0)

    def test_early_return_prefix_records_post_return_boundary(self) -> None:
        out = self.model_5455c6()

        self.assertEqual(out.r0, 0)
        self.assertEqual(out.stack_adjust_bytes, 0x18)
        self.assertEqual(out.restored_r4, 1)
        self.assertEqual(out.returned_via_pop_pc, 1)
        self.assertEqual(out.bounded_return_prefix_bytes, 6)
        self.assertEqual(out.post_return_boundary_bytes, 24)

    def test_u16_tail_call_wrapper_masks_r1_and_preserves_r0(self) -> None:
        out = self.model_545ec4(Inputs545ec4(0x12345678, 0x89ABCDEF))

        self.assertEqual(out.call_target, 0x00486876)
        self.assertEqual(out.call_r0, 0x12345678)
        self.assertEqual(out.call_r1, 0xCDEF)
        self.assertEqual(out.return_register_passthrough, 1)


if __name__ == "__main__":
    unittest.main()
