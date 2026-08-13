import os
import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "components"
    / "shared"
    / "easylogger"
    / "runtime_easylogger_helper_seams.c"
)
HEADER_DIR = SOURCE.parent
MAIN_IMAGE = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
BOOT_IMAGE = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_bootloader.bin"
)

sys.path.insert(0, str(ROOT / "tools"))
import apollo_overlay  # noqa: E402


SOURCE_SIZE = 7_068
SOURCE_SHA256 = (
    "78dc5aa9a7eb4f072b3169ae183785500"
    "7f25e1adccec7deaefecc486c8f0823"
)
COMMON_FLAGS = [
    "-mthumb",
    "-ffreestanding",
    "-fno-jump-tables",
    "-fomit-frame-pointer",
    "-fno-builtin",
    "-mno-unaligned-access",
    "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables",
    "-fropi",
    "-ffunction-sections",
    "-fdata-sections",
    "-Wall",
    "-Wextra",
    "-Werror",
]
PROFILES = {
    "main": {
        "target_flags": ["--target=thumbv7em-none-eabi", "-O2"],
        "profile": "1",
        "leaves": {
            "open_cfw_easylogger_helpers_get_logger": {
                "macro": (
                    "OPEN_CFW_EASYLOGGER_HELPER_SEAMS_LEAF_GET_LOGGER"
                ),
                "size": 10,
                "sha256": (
                    "5970df921f43a013c1198a9d9a5fc1c1"
                    "67e7d6b104aaefa8135d94630c3aea5b"
                ),
            },
            "open_cfw_easylogger_helpers_assert_failed": {
                "macro": (
                    "OPEN_CFW_EASYLOGGER_HELPER_SEAMS_LEAF_ASSERT_FAILED"
                ),
                "size": 168,
                "sha256": (
                    "2437cde26a848cd283fbf7d67862f63f"
                    "1bdd3262f6db17dc19ffb36ba51fa3bc"
                ),
            },
        },
    },
    "boot": {
        "target_flags": [
            "--target=arm-none-eabi",
            "-mcpu=cortex-m55",
            "-Oz",
        ],
        "profile": "2",
        "leaves": {
            "open_cfw_easylogger_helpers_get_logger": {
                "macro": (
                    "OPEN_CFW_EASYLOGGER_HELPER_SEAMS_LEAF_GET_LOGGER"
                ),
                "size": 8,
                "sha256": (
                    "3f32a69299002872bb9364f79744be13"
                    "11bcb8bce47f24f43558806931990064"
                ),
            },
            "open_cfw_easylogger_helpers_assert_failed": {
                "macro": (
                    "OPEN_CFW_EASYLOGGER_HELPER_SEAMS_LEAF_ASSERT_FAILED"
                ),
                "size": 132,
                "sha256": (
                    "f57622ddc7fdbe8555760ca15bf049b8"
                    "fb68abfb3203aa290500e22bbbf82b7a"
                ),
            },
        },
    },
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_c_string(
    image: bytes,
    *,
    run_base: int,
    preamble: int,
    address: int,
) -> str:
    offset = preamble + address - run_base
    end = image.index(0, offset)
    return image[offset:end].decode("ascii")


_APPLE_ONLY = unittest.skipUnless(
    (os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang") == "apple-clang",
    "byte-exact / toolchain-specific Apple-clang assertion; Linux byte "
    "reproduction is verified end-to-end by tests/test_toolchain_profiles.py",
)


class RuntimeEasyLoggerHelperSeamTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("clang is required")

    def test_source_and_binary_seam_addresses_are_review_pinned(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        self.assertEqual((SOURCE.stat().st_size, sha256(SOURCE.read_bytes())), (
            SOURCE_SIZE,
            SOURCE_SHA256,
        ))
        for literal in (
            "0x2007456CU",
            "0x0043D575U",
            "0x0044B0AFU",
            "0x200270E4U",
            "0x004176CFU",
            "0x0041AC8BU",
            "OPEN_CFW_EASYLOGGER_HELPERS_ASSERT_GET_FMT_LINE",
            "OPEN_CFW_EASYLOGGER_HELPERS_ASSERT_STRCPY_DST_LINE",
            "OPEN_CFW_EASYLOGGER_HELPERS_STRCPY_SRC_EXPRESSION_ADDRESS",
        ):
            self.assertIn(literal, source)

    def test_retained_official_assertion_strings_are_exact(self) -> None:
        main = MAIN_IMAGE.read_bytes()
        boot = BOOT_IMAGE.read_bytes()
        expected = {
            "get_fmt": (
                "level <= ELOG_LVL_VERBOSE",
                "get_fmt_enabled",
                "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\"
                "EasyLogger-master\\easylogger\\src\\elog.c",
                "(%s) has assert failed at %s:%ld.",
                "elog",
            ),
            "strcpy": (
                "dst",
                "src",
                "elog_strcpy",
                "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\"
                "EasyLogger-master\\easylogger\\src\\elog_utils.c",
                "(%s) has assert failed at %s:%ld.",
                "elog",
            ),
        }
        main_addresses = (
            (0x0076B634, 0x00785DC0, 0x006E3098, 0x007542A8, 0x0078D4EC),
            (0x0044B70C, 0x0044B710, 0x0078A9AC, 0x006DD234, 0x00754314, 0x0078D51C),
        )
        boot_addresses = (
            (0x004335CC, 0x00433D18, 0x00430EC0, 0x00432E98, 0x0043406C),
            (0x0041B1FC, 0x0041B200, 0x00433F5C, 0x00430DA0, 0x00432EBC, 0x0043408C),
        )
        for image, run_base, preamble, addresses in (
            (main, 0x00438000, 32, main_addresses),
            (boot, 0x00410000, 0, boot_addresses),
        ):
            self.assertEqual(
                tuple(
                    image_c_string(
                        image,
                        run_base=run_base,
                        preamble=preamble,
                        address=address,
                    )
                    for address in addresses[0]
                ),
                expected["get_fmt"],
            )
            self.assertEqual(
                tuple(
                    image_c_string(
                        image,
                        run_base=run_base,
                        preamble=preamble,
                        address=address,
                    )
                    for address in addresses[1]
                ),
                expected["strcpy"],
            )

    @_APPLE_ONLY
    def test_both_image_profiles_emit_closed_relocation_free_leaves(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            for profile_name, profile in PROFILES.items():
                for function, expected in profile["leaves"].items():
                    object_path = output / f"{profile_name}-{function}.o"
                    subprocess.run(
                        [
                            self.clang,
                            *profile["target_flags"],
                            *COMMON_FLAGS,
                            f"-I{HEADER_DIR}",
                            "-DOPEN_CFW_EASYLOGGER_HELPERS_PROFILE="
                            f"{profile['profile']}",
                            "-DOPEN_CFW_EASYLOGGER_HELPER_SEAMS_BUILD_LEAF=1",
                            f"-D{expected['macro']}=1",
                            "-c",
                            str(SOURCE),
                            "-o",
                            str(object_path),
                        ],
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    body, report = (
                        apollo_overlay.extract_in_place_function_section(
                            object_path,
                            function,
                            runtime_address=0x00700000,
                            relocation_configs=[],
                        )
                    )
                    self.assertEqual(len(body), expected["size"])
                    self.assertEqual(sha256(body), expected["sha256"])
                    self.assertEqual(report["alignment"], 4)
                    self.assertEqual(report["relocation_count"], 0)
                    self.assertFalse(
                        any(
                            "rodata" in section["name"]
                            for section in report["discarded_alloc_sections"]
                        )
                    )


if __name__ == "__main__":
    unittest.main()
