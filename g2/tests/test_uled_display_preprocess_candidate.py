import ctypes
import hashlib
import platform
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/uled_display_preprocess.c"
FIXTURE = ROOT / "tests/fixtures"
EXPECTED_SYMBOLS = {"open_cfw_uled_buffer_sync_to_fb"}
SOURCE_SHA256 = "b288dba986ff1cabc8a8625eee2dc5d35ed21ac2c8c770c68c890590c02f66fd"


class UledDisplayPreprocessCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library = Path(cls.temporary.name) / f"uled_display_preprocess{suffix}"
        subprocess.run(
            [
                "clang", "-std=c11", "-shared", "-fPIC", "-O1",
                "-include", str(FIXTURE / "uled_display_preprocess_host.h"),
                str(SOURCE), str(FIXTURE / "uled_display_preprocess_host.c"),
                "-o", str(cls.library),
            ],
            check=True,
            cwd=ROOT,
        )
        cls.loaded = ctypes.CDLL(str(cls.library))
        cls.loaded.open_cfw_uled_buffer_sync_to_fb.argtypes = [
            ctypes.c_void_p, ctypes.c_void_p,
            ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint,
            ctypes.c_uint, ctypes.c_uint,
        ]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.loaded.open_cfw_test_uled_reset()
        self.destination = (ctypes.c_uint64 * (640 * 480 // 8))()
        self.source = (ctypes.c_uint64 * (576 * 288 // 8))()

    def uint(self, name: str) -> int:
        return ctypes.c_uint.in_dll(self.loaded, name).value

    def uints(self, name: str, length: int) -> list[int]:
        return list((ctypes.c_uint * length).in_dll(self.loaded, name))

    def call(self, **changes) -> None:
        values = {
            "destination": ctypes.addressof(self.destination),
            "source": ctypes.addressof(self.source),
            "destination_width": 640,
            "destination_height": 480,
            "source_width": 576,
            "source_height": 288,
            "offset_x": 64,
            "offset_y": 32,
        }
        values.update(changes)
        self.loaded.open_cfw_uled_buffer_sync_to_fb(*values.values())

    def test_valid_call_builds_exact_descriptors_and_sequence(self) -> None:
        self.call()
        descriptor = self.uints("open_cfw_test_uled_descriptor", 7)
        self.assertEqual(descriptor[0], 0x619)
        self.assertEqual(descriptor[1], 320 | (480 << 16))
        self.assertEqual(descriptor[2], 320)
        self.assertEqual(descriptor[3], 640 * 480 // 2)
        self.assertEqual(descriptor[4], ctypes.addressof(self.destination) & 0xFFFFFFFF)
        self.assertEqual(descriptor[5], descriptor[4])
        self.assertEqual(descriptor[6], 0)
        self.assertEqual(self.uints("open_cfw_test_uled_region", 4), [0, 0, 319, 479])
        self.assertEqual(self.uints("open_cfw_test_uled_source_args", 5), [288, 288, 9, 288, 0])
        self.assertEqual(self.uints("open_cfw_test_uled_offset", 2), [32, 32])
        self.assertEqual(
            self.uints("open_cfw_test_uled_sequence", 6),
            [0x110, 0x200, 0x310, 0x400, 0x500, 0x601],
        )
        self.assertEqual(self.uint("open_cfw_test_uled_call_count"), 6)

    def test_gpu_start_failure_only_diagnoses(self) -> None:
        ctypes.c_int.in_dll(
            self.loaded, "open_cfw_test_uled_start_result"
        ).value = -2
        self.call()
        self.assertEqual(self.uint("open_cfw_test_uled_diagnostic_count"), 1)
        self.assertEqual(self.uint("open_cfw_test_uled_call_count"), 0)
        self.assertEqual(self.uints("open_cfw_test_uled_sequence", 1), [0xFE])

    def test_each_precondition_has_the_stock_expression(self) -> None:
        cases = [
            ({"destination": None}, "ptr_des != NULL"),
            ({"source": None}, "ptr_src != NULL"),
            ({"destination_width": 576}, "des_width > src_width"),
            ({"destination_height": 288}, "des_hight > src_hight"),
            ({"offset_x": 63}, "offset_x % 2 == 0"),
            ({"source_width": 575}, "src_width % 2 == 0"),
            ({"destination_width": 641}, "des_width % 2 == 0"),
            ({"destination": ctypes.addressof(self.destination) + 1},
             "((uint32_t)ptr_des & 0x00000007) == 0"),
            ({"source": ctypes.addressof(self.source) + 1},
             "((uint32_t)ptr_src & 0x00000007) == 0"),
        ]
        for changes, expected in cases:
            self.loaded.open_cfw_test_uled_reset()
            self.call(**changes)
            expression = bytes((ctypes.c_char * 80).in_dll(
                self.loaded, "open_cfw_test_uled_assert_expression"
            )).split(b"\0", 1)[0].decode()
            self.assertEqual(expression, expected)
            self.assertEqual(self.uint("open_cfw_test_uled_assert_count"), 1)
            self.assertEqual(self.uint("open_cfw_test_uled_call_count"), 0)

    def test_thumb_compile_has_exact_global_text_surface(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "uled_display_preprocess.o"
            subprocess.run(
                [
                    "clang", "-target", "thumbv7em-none-eabi", "-mthumb", "-O2",
                    "-ffreestanding", "-fno-jump-tables", "-fomit-frame-pointer",
                    "-fno-builtin", "-mno-unaligned-access", "-fno-unwind-tables",
                    "-fno-asynchronous-unwind-tables", "-fropi", "-Wall", "-Wextra",
                    "-Werror", "-c", str(SOURCE), "-o", str(target),
                ],
                check=True,
                cwd=ROOT,
            )
            symbols = subprocess.run(
                ["nm", str(target)], check=True, capture_output=True, text=True
            ).stdout
            observed = {
                fields[2]
                for line in symbols.splitlines()
                if len(fields := line.split()) == 3 and fields[1] == "T"
            }
            self.assertEqual(observed, EXPECTED_SYMBOLS)

    def test_source_hash(self) -> None:
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(), SOURCE_SHA256)


if __name__ == "__main__":
    unittest.main()
