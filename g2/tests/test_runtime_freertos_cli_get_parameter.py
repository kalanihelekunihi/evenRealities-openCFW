from __future__ import annotations

import ctypes
import hashlib
import importlib.util
import itertools
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
MAKEFILE = ROOT / "Makefile"
OFFICIAL = (
    ROOT / "blobs/official/g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
PRODUCTION_SOURCE = (
    ROOT / "components/shared/freertos_cli"
    / "runtime_freertos_cli_get_parameter.c"
)
PRODUCTION_HEADER = PRODUCTION_SOURCE.with_suffix(".h")
CANDIDATE_SOURCE = PRODUCTION_SOURCE.with_name(
    "runtime_freertos_cli_get_parameter_candidate.c"
)
CANDIDATE_HEADER = CANDIDATE_SOURCE.with_suffix(".h")
COMPONENT_NOTICE = (
    ROOT / "components/apollo_main/core_overlay/NOTICE.md"
)
CLI_LICENSE = (
    ROOT / "components/apollo_main/core_overlay"
    / "LICENSE-FreeRTOS-Plus-CLI-MIT"
)
HOST_FIXTURE = (
    ROOT / "tests/fixtures"
    / "runtime_freertos_cli_get_parameter_candidate_host.c"
)
ORACLE_INCLUDE = (
    ROOT / "tests/fixtures/freertos_cli_get_parameter_oracle"
)
UPSTREAM_SOURCE = ROOT / "third_party/freertos-plus-cli/FreeRTOS_CLI.c"

PRODUCTION_FUNCTION = "open_cfw_freertos_cli_get_parameter"
CANDIDATE_FUNCTION = "open_cfw_freertos_cli_get_parameter_candidate"
OVERLAY_RUNTIME_ADDRESS = 0x0079_4324
APPLICATION_BASE = 0x0043_8000
PREAMBLE = 32
STOCK_START = 0x0058_48FC
STOCK_END = 0x0058_4960
STOCK_SHA256 = "35c6a4ce194bbea2a6044c3ab8f1108bb6c88806bafbf196fdb88c49a983a6f4"
LEAF_BYTES_SHA256 = "7b77ccc3441cb8e725fa8a97a8197e0f993a00456925c6eb0126e77fb00f9914"

LOCAL_PINS = {
    PRODUCTION_SOURCE: (
        2_847,
        "7f04ecb4318ba255b0d65d82c5fd1fceafd7939e89c93113b5fb1f69e6ef8552",
    ),
    PRODUCTION_HEADER: (
        1_308,
        "531fbe4e2e6ecab0f32da159864ce963b40851e1ddb6e80406d99e780a80d17c",
    ),
    CANDIDATE_SOURCE: (
        2_819,
        "c31899da1a03e88d2505ce3d3ac3a1b52509f9bfab842ddd0b2cf9464e8f2930",
    ),
    CANDIDATE_HEADER: (
        1_294,
        "d05f89bb3c4b8344b81659a875cf77aec74ffc427d6f4c0ef58447fdf0d74f70",
    ),
    HOST_FIXTURE: (
        1_629,
        "441a7eac2938ba271c89d3472e591aeae7020e09a62fed89a4c0a021a4e5aa40",
    ),
    CLI_LICENSE: (
        1_114,
        "d11abdc8acfb02edd788ca59b0b94c76cbb9e30ab92052ea9f1c55f0e2331f32",
    ),
}

PRODUCTION_FLAGS = (
    "--target=thumbv7em-none-eabi",
    "-mthumb",
    "-O2",
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
)

PROFILE_PINS = {
    "apple-clang": {
        "compiler": "/usr/bin/clang",
        "version": "Apple clang version 21.0.0 (clang-2100.3.33.1)",
        "production_object": (
            1_140,
            "7aa0a8e045773df37ef2bb56666acc32c4a706ba5bebbe0dc736d7ff59dd1d05",
        ),
        "production_offset": 183_048,
        "overlay": (
            429_058,
            "0e3a5f42548a24be9c6be90f9d6a60031af69b6570e7d212815f6671bb6d7bcd",
        ),
        "component": (
            3_952_454,
            "d72288b5831087acaff95fc3aaadb9e178b755ee8ce3b64a17be24af1bfd3dcb",
        ),
        "package": (
            4_745_526,
            "4eb4b7f409e6c7023cffa70b21b2b3646a20f1bf305333cdc57b556b5fc32934",
        ),
        "replacement_sha256": (
            "725846b2fb35bfa360ede03e42d542262fbc7f74a4aea101e6d8a9d2e2bc9bf6"
        ),
        "accounting": {
            "generated_patch_site_bytes": 409_066,
            "opaque_base_bytes": 3_111_914,
            "replaced_stock_function_bytes": 409_246,
            "source_owned_bytes": 431_334,
            "source_owned_in_place_bytes": 184,
        },
    },
    "linux-clang": {
        "compiler": "/home/linuxbrew/.linuxbrew/bin/clang",
        "version": "Homebrew clang version 22.1.8",
        "production_object": (
            1_120,
            "76a9d2f7de4d6c98902b84e1ad535f6bc643ae45a4676794e8e3345f41f5b263",
        ),
        "production_offset": 184_776,
        "overlay": (
            212_664,
            "1074b19c5f24f6bb454860f53a38fdf321ae29da6762617c36b1e47925dd0b18",
        ),
        "component": (
            3_736_060,
            "fc7e2a8363e7d8a78c28c64cbaf7dcc3a03a1089c716d2d83f8d1a9bb5c10b97",
        ),
        "package": (
            4_529_116,
            "f0526433c366a85ab79e27df6d28ffc70d6a2ed93e608652885b49b404e380ef",
        ),
        "replacement_sha256": (
            "f5a86d3592c9b16fae073cfc5e9633dd5789985adb208cf02174be9aac6fc42e"
        ),
        "accounting": {
            "generated_patch_site_bytes": 99_288,
            "opaque_base_bytes": 3_423_892,
            "replaced_stock_function_bytes": 99_468,
            "source_owned_bytes": 205_144,
            "source_owned_in_place_bytes": 184,
        },
    },
}


def sha256(value: bytes | Path) -> str:
    if isinstance(value, Path):
        value = value.read_bytes()
    return hashlib.sha256(value).hexdigest()


def wide_conditional_target(address: int, encoded: bytes) -> int | None:
    first, second = struct.unpack("<HH", encoded)
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0x8000:
        return None
    if ((first >> 6) & 0x0F) >= 0x0E:
        return None
    sign = (first >> 10) & 1
    immediate = (
        sign << 20
        | ((second >> 11) & 1) << 19
        | ((second >> 13) & 1) << 18
        | (first & 0x003F) << 12
        | (second & 0x07FF) << 1
    )
    if sign:
        immediate -= 1 << 21
    return address + 4 + immediate


def narrow_targets(address: int, halfword: int) -> tuple[int, ...]:
    if halfword & 0xF800 == 0xE000:
        immediate = halfword & 0x07FF
        if immediate & 0x0400:
            immediate -= 0x0800
        return (address + 4 + (immediate << 1),)
    if halfword & 0xF000 == 0xD000 and halfword & 0x0F00 != 0x0F00:
        immediate = halfword & 0x00FF
        if immediate & 0x0080:
            immediate -= 0x0100
        return (address + 4 + (immediate << 1),)
    if halfword & 0xF500 == 0xB100:
        immediate = (
            ((halfword >> 9) & 1) << 6
            | ((halfword >> 3) & 0x1F) << 1
        )
        return (address + 4 + immediate,)
    return ()


class RuntimeFreeRTOSCLIGetParameterTests(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        version = subprocess.run(
            [cls.clang, "--version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()[0]
        if version.startswith("Apple clang version 21.0.0"):
            cls.profile = "apple-clang"
        elif version.startswith("Homebrew clang version 22.1.8"):
            cls.profile = "linux-clang"
        else:
            raise AssertionError(f"unreviewed compiler: {version!r}")
        cls.pins = PROFILE_PINS[cls.profile]
        if version != cls.pins["version"]:
            raise AssertionError((version, cls.pins["version"]))
        if cls.clang != cls.pins["compiler"]:
            raise AssertionError((cls.clang, cls.pins["compiler"]))
        configured = os.environ.get("OPENCFW_TOOLCHAIN_PROFILE")
        if configured is not None and configured != cls.profile:
            raise AssertionError((configured, cls.profile))

        (ROOT / "build").mkdir(exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="open-cfw-freertos-cli-production-",
            dir=ROOT / "build",
        )
        temporary = Path(cls.temporary.name)

        spec = importlib.util.spec_from_file_location(
            "open_cfw_apollo_overlay_cli_production",
            ROOT / "tools/apollo_overlay.py",
        )
        assert spec is not None and spec.loader is not None
        cls.apollo_overlay = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.apollo_overlay)
        cls.report = cls.apollo_overlay.build(
            root=ROOT,
            config_path=CONFIG,
            output_dir=temporary / "overlay",
            clang=cls.clang,
            toolchain_profile=cls.profile,
        )
        cls.component = (
            ROOT / cls.report["component"]["artifact"]
        ).read_bytes()

        cls.production_objects = []
        for index in range(2):
            production_object = temporary / f"production-{index}.o"
            subprocess.run(
                [
                    cls.clang,
                    *PRODUCTION_FLAGS,
                    "-c",
                    str(PRODUCTION_SOURCE),
                    "-o",
                    str(production_object),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            cls.production_objects.append(production_object)

        library = temporary / (
            "freertos-cli-production.dylib"
            if sys.platform == "darwin"
            else "freertos-cli-production.so"
        )
        command = [
            cls.clang,
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-I",
            str(ORACLE_INCLUDE),
            str(PRODUCTION_SOURCE),
            str(CANDIDATE_SOURCE),
            str(HOST_FIXTURE),
            str(UPSTREAM_SOURCE),
        ]
        if sys.platform == "darwin":
            command.extend(("-dynamiclib", "-o", str(library)))
        else:
            command.extend(("-shared", "-fPIC", "-o", str(library)))
        subprocess.run(command, check=True, capture_output=True, text=True)
        host = ctypes.CDLL(str(library))
        cls.production = host.open_cfw_test_freertos_cli_get_parameter_production
        cls.candidate = host.open_cfw_test_freertos_cli_get_parameter_candidate
        cls.upstream = host.open_cfw_test_freertos_cli_get_parameter_upstream
        for function in (cls.production, cls.candidate, cls.upstream):
            function.argtypes = (
                ctypes.c_void_p,
                ctypes.c_uint32,
                ctypes.POINTER(ctypes.c_int32),
            )
            function.restype = ctypes.c_int32

        open_cfw_spec = importlib.util.spec_from_file_location(
            "open_cfw_cli_production",
            ROOT / "tools/open_cfw.py",
        )
        assert open_cfw_spec is not None and open_cfw_spec.loader is not None
        cls.open_cfw = importlib.util.module_from_spec(open_cfw_spec)
        sys.modules[open_cfw_spec.name] = cls.open_cfw
        open_cfw_spec.loader.exec_module(cls.open_cfw)
        cls.manifest, _root, cls.payloads = cls.open_cfw.verify_manifest(
            MANIFEST,
            toolchain_profile=cls.profile,
        )
        cls.package, _entries = cls.open_cfw.assemble_evenota(
            cls.manifest,
            cls.payloads,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @staticmethod
    def invoke(function, raw: bytes, wanted: int) -> tuple[int, int]:
        buffer = ctypes.create_string_buffer(raw + b"\0")
        length = ctypes.c_int32(-1)
        offset = int(function(buffer, wanted, ctypes.byref(length)))
        return offset, int(length.value)

    def test_production_candidate_and_notice_artifacts_are_independently_pinned(self) -> None:
        for path, (size, digest) in LOCAL_PINS.items():
            with self.subTest(path=path.name):
                self.assertEqual(path.stat().st_size, size)
                self.assertEqual(sha256(path), digest)
        production = PRODUCTION_SOURCE.read_text(encoding="utf-8")
        candidate = CANDIDATE_SOURCE.read_text(encoding="utf-8")
        for text in (production, candidate):
            self.assertIn("Copyright (C) 2017 Amazon.com", text)
            self.assertIn("The above copyright notice", text)
            self.assertIn("THE SOFTWARE IS PROVIDED \"AS IS\"", text)
        self.assertIn("Production source leaf", production)
        self.assertNotIn("production-excluded", production.lower())
        self.assertIn("Production-excluded", candidate)
        notice = COMPONENT_NOTICE.read_text(encoding="utf-8")
        self.assertIn("runtime_freertos_cli_get_parameter.c", notice)
        self.assertIn("LICENSE-FreeRTOS-Plus-CLI-MIT", notice)
        self.assertIn("Copyright (C) 2017 Amazon.com", CLI_LICENSE.read_text())

    def test_production_is_exhaustively_exact_to_candidate_and_upstream(self) -> None:
        alphabet = (b"a", b"b", b" ", b"\t")
        wanted_values = (0, 1, 2, 3, 4, 5, 6, 0xFFFF_FFFF)
        compared = 0
        for size in range(7):
            for symbols in itertools.product(alphabet, repeat=size):
                raw = b"".join(symbols)
                for wanted in wanted_values:
                    expected = self.invoke(self.upstream, raw, wanted)
                    self.assertEqual(self.invoke(self.candidate, raw, wanted), expected)
                    self.assertEqual(self.invoke(self.production, raw, wanted), expected)
                    compared += 1
        self.assertEqual(compared, 43_688)

    def test_compiled_objects_and_strict_zero_relocation_leaf_are_pinned(self) -> None:
        production_records = [
            (path.stat().st_size, sha256(path))
            for path in self.production_objects
        ]
        self.assertEqual(
            production_records,
            [self.pins["production_object"]] * 2,
        )

        production_address = (
            OVERLAY_RUNTIME_ADDRESS + self.pins["production_offset"]
        )
        bodies = []
        for path in self.production_objects:
            body, extraction = (
                self.apollo_overlay.extract_in_place_function_section(
                    path,
                    PRODUCTION_FUNCTION,
                    runtime_address=production_address,
                    relocation_configs=[],
                    strict_relocation_contract=True,
                )
            )
            bodies.append(body)
            self.assertEqual(extraction["relocation_count"], 0)
            self.assertEqual(extraction["relocations"], [])
            self.assertEqual(extraction["alignment"], 4)
            self.assertEqual(
                extraction["authenticated_cantunwind_discard_count"],
                1,
            )
        self.assertEqual(bodies[0], bodies[1])
        self.assertEqual((len(bodies[0]), sha256(bodies[0])), (252, LEAF_BYTES_SHA256))

    def test_production_layout_and_redirect_are_exact(self) -> None:
        leaves = {
            item["extraction"]["function"]: item
            for item in self.report["relocated_leaves"]
        }
        production = leaves[PRODUCTION_FUNCTION]
        self.assertEqual(production["placement"]["offset"], self.pins["production_offset"])
        self.assertEqual(production["extraction"]["relocations"], [])

        patches = {
            item["name"]: item
            for item in self.report["overlay"]["patched_sites"]
        }
        redirect = patches["replace_freertos_cli_get_parameter"]
        replacement = bytes.fromhex(redirect["replacement_hex"])
        self.assertEqual(len(replacement), 100)
        self.assertEqual(sha256(replacement), self.pins["replacement_sha256"])
        self.assertEqual(replacement[4:], b"\x00\xbf" * 48)
        self.assertEqual(
            self.apollo_overlay.decode_thumb_branch(
                STOCK_START,
                replacement[:4],
                link=False,
            ),
            OVERLAY_RUNTIME_ADDRESS + self.pins["production_offset"],
        )
        self.assertEqual(
            self.component[redirect["payload_offset"]:redirect["payload_offset"] + 100],
            replacement,
        )
        self.assertNotIn("harden_freertos_cli_console_capacity", patches)
        official = OFFICIAL.read_bytes()
        stock_offset = PREAMBLE + STOCK_START - APPLICATION_BASE
        self.assertEqual(
            sha256(official[stock_offset:stock_offset + 100]),
            STOCK_SHA256,
        )

    def test_appended_cli_leaves_have_only_the_reviewed_external_ingress(self) -> None:
        leaves = {
            item["extraction"]["function"]: item
            for item in self.report["relocated_leaves"]
        }
        ranges = {
            PRODUCTION_FUNCTION: (
                OVERLAY_RUNTIME_ADDRESS
                + leaves[PRODUCTION_FUNCTION]["placement"]["offset"],
                252,
            ),
        }

        targeted_sites = {
            function: [
                site
                for site in self.report["overlay"]["patched_sites"]
                if site["target_function"] == function
            ]
            for function in ranges
        }
        self.assertEqual(
            [site["name"] for site in targeted_sites[PRODUCTION_FUNCTION]],
            ["replace_freertos_cli_get_parameter"],
        )
        self.assertEqual(targeted_sites[PRODUCTION_FUNCTION][0]["branch"], "b_w")

        linked_symbols = {
            relocation["symbol"]
            for relocation in self.report["overlay"]["link"][
                "resolved_relocations"
            ]
        }
        self.assertTrue(set(ranges).isdisjoint(linked_symbols))

        # Keep every independent decoder family live even when the current
        # image happens to contain no ingress of that kind.
        self.assertEqual(
            self.apollo_overlay.decode_thumb_branch(
                0x1000,
                self.apollo_overlay.encode_thumb_b_w(0x1000, 0x1010),
            ),
            0x1010,
        )
        self.assertEqual(
            wide_conditional_target(0x1000, bytes.fromhex("00f00080")),
            0x1004,
        )
        self.assertEqual(narrow_targets(0x1000, 0xE000), (0x1004,))
        self.assertEqual(narrow_targets(0x1000, 0xD000), (0x1004,))
        self.assertEqual(narrow_targets(0x1000, 0xB100), (0x1004,))

        branch_ingress = {function: [] for function in ranges}
        conditional_or_narrow_ingress = {function: [] for function in ranges}
        pointer_ingress = {function: [] for function in ranges}
        # The Linux placement makes one byte-sliding window in the unchanged
        # stock image numerically resemble a Thumb pointer into this leaf.
        # It is not stored data: 0x0043C171 starts one byte into the reviewed
        # `vldr d7, [pc, #0xac]` encoding at 0x0043C170 and spans the first
        # byte of the following `movs r3, #0`.  Keep the byte-granular scan,
        # but pin this instruction-overlap false positive exactly.
        reviewed_pointer_window_false_positives = {
            (0x0043_C171, 0x007B_2BED): bytes.fromhex("9fed2b7b0023"),
        }
        seen_pointer_window_false_positives = set()
        for payload_offset in range(PREAMBLE, len(self.component) - 3, 2):
            instruction_address = (
                APPLICATION_BASE + payload_offset - PREAMBLE
            )
            encoded = self.component[payload_offset:payload_offset + 4]
            try:
                target = self.apollo_overlay.decode_thumb_branch(
                    instruction_address,
                    encoded,
                )
            except self.apollo_overlay.BuildError:
                target = None
            if target is not None:
                for function, (start, size) in ranges.items():
                    if (
                        start <= target < start + size
                        and not start <= instruction_address < start + size
                    ):
                        branch_ingress[function].append(
                            (instruction_address, target, encoded.hex())
                        )

            conditional_target = wide_conditional_target(
                instruction_address,
                encoded,
            )
            narrow = narrow_targets(
                instruction_address,
                int.from_bytes(encoded[:2], "little"),
            )
            for target in (
                *((conditional_target,) if conditional_target is not None else ()),
                *narrow,
            ):
                for function, (start, size) in ranges.items():
                    if (
                        start <= target < start + size
                        and not start <= instruction_address < start + size
                    ):
                        conditional_or_narrow_ingress[function].append(
                            (instruction_address, target, encoded.hex())
                        )

        for payload_offset in range(PREAMBLE, len(self.component) - 3):
            storage_address = APPLICATION_BASE + payload_offset - PREAMBLE
            stored = int.from_bytes(
                self.component[payload_offset:payload_offset + 4],
                "little",
            )
            target = stored & ~1
            for function, (start, size) in ranges.items():
                if (
                    start <= target < start + size
                    and not start <= storage_address < start + size
                ):
                    false_positive = (storage_address, stored)
                    if false_positive in reviewed_pointer_window_false_positives:
                        self.assertEqual(
                            self.component[payload_offset - 1:payload_offset + 5],
                            reviewed_pointer_window_false_positives[false_positive],
                        )
                        seen_pointer_window_false_positives.add(false_positive)
                        continue
                    pointer_ingress[function].append(
                        (storage_address, stored)
                    )

        production_start = ranges[PRODUCTION_FUNCTION][0]
        self.assertEqual(
            branch_ingress,
            {
                PRODUCTION_FUNCTION: [
                    (
                        STOCK_START,
                        production_start,
                        targeted_sites[PRODUCTION_FUNCTION][0][
                            "replacement_hex"
                        ][:8],
                    )
                ],
            },
        )
        self.assertEqual(
            pointer_ingress,
            {PRODUCTION_FUNCTION: []},
        )
        expected_false_positives = (
            set(reviewed_pointer_window_false_positives)
            if self.profile == "linux-clang"
            else set()
        )
        self.assertEqual(
            seen_pointer_window_false_positives,
            expected_false_positives,
        )
        self.assertEqual(
            conditional_or_narrow_ingress,
            {PRODUCTION_FUNCTION: []},
        )

    def test_manifest_tiles_and_owns_accessor_fixed_span_and_appended_leaf(self) -> None:
        main = next(
            component
            for component in self.manifest["components"]
            if component["name"] == "apollo_main"
        )
        regions = main["regions"]
        cursor = 0
        for region in regions:
            self.assertEqual(region["file_offset"], cursor, region["name"])
            cursor += region["size"]
        self.assertEqual(cursor, main["provider"]["size"])

        by_name = {region["name"]: region for region in regions}
        expected = {
            "freertos_cli_get_parameter_source_replacement": (
                1_362_204, 100, STOCK_START, "generated_source_entry_replacement"
            ),
            "apollo_freertos_cli_get_parameter_source_alignment": (
                3_646_593, 3, 0x007B_2461, "generated_alignment"
            ),
            "apollo_freertos_cli_get_parameter_source_leaf": (
                3_646_596, 252, 0x007C_0E2C, "source_compiled"
            ),
        }
        for name, fields in expected.items():
            region = by_name[name]
            self.assertEqual(
                (
                    region["file_offset"],
                    region["size"],
                    region["target_address"],
                    region["address_status"],
                ),
                fields,
            )

        self.assertEqual(
            (len(self.package), sha256(self.package)),
            self.pins["package"],
        )
        self.assertEqual(
            (
                self.report["overlay"]["size"],
                self.report["overlay"]["sha256"],
            ),
            self.pins["overlay"],
        )
        self.assertEqual(
            (
                self.report["component"]["size"],
                self.report["component"]["sha256"],
            ),
            self.pins["component"],
        )
        self.assertEqual(
            {
                key: self.report["component"][key]
                for key in self.pins["accounting"]
            },
            self.pins["accounting"],
        )

    def test_candidate_remains_excluded_while_production_leaf_is_registered(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        self.assertIn(PRODUCTION_FUNCTION, config["functions"])
        self.assertNotIn(CANDIDATE_FUNCTION, config["functions"])
        registered_sources = {
            item["source"]["path"]
            for group in ("isolated_leaves", "relocated_leaves", "in_place_leaves")
            for item in config[group]
        }
        self.assertIn(PRODUCTION_SOURCE.relative_to(ROOT).as_posix(), registered_sources)
        self.assertNotIn(CANDIDATE_SOURCE.relative_to(ROOT).as_posix(), registered_sources)

        forbidden = (CANDIDATE_SOURCE.name, CANDIDATE_FUNCTION)
        for path in (CONFIG, MANIFEST, MAKEFILE):
            text = path.read_text(encoding="utf-8")
            for token in forbidden:
                self.assertNotIn(token, text, (path, token))


if __name__ == "__main__":
    unittest.main()
