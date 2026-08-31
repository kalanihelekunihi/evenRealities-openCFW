from __future__ import annotations

import ctypes
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
import test_cmbacktrace_get_cur_thread_name_candidate as candidate_contract

sys.path.insert(0, str(ROOT / "tools"))
import apollo_overlay


SOURCE = (
    ROOT / "components/shared/cmbacktrace"
    / "runtime_cmbacktrace_get_cur_thread_name.c"
)
HEADER = SOURCE.with_suffix(".h")
ADAPTER = (
    ROOT / "components/apollo_main/core_overlay"
    / "runtime_cmbacktrace_pc_task_get_name_current.c"
)
ADAPTER_HEADER = ADAPTER.with_suffix(".h")
LICENSE = (
    ROOT / "components/apollo_main/core_overlay/LICENSE-CmBacktrace-MIT"
)
UPSTREAM_LICENSE = ROOT / "third_party/cmbacktrace/LICENSE"
HOST_FIXTURE = (
    ROOT / "tests/fixtures"
    / "runtime_cmbacktrace_get_cur_thread_name_production_host.c"
)
CANDIDATE = (
    ROOT / "components/shared/cmbacktrace"
    / "runtime_cmbacktrace_get_cur_thread_name_candidate.c"
)
UPSTREAM = ROOT / "third_party/cmbacktrace/cm_backtrace/cm_backtrace.c"
PROVENANCE = ROOT / "third_party/cmbacktrace/PROVENANCE.json"
VERIFIER = ROOT / "third_party/cmbacktrace/verify_snapshot.py"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
MAKEFILE = ROOT / "Makefile"
NOTICE = ROOT / "components/apollo_main/core_overlay/NOTICE.md"
EVIDENCE = ROOT / "components/apollo_main/core_overlay/EVIDENCE.md"
AUDIT = ROOT / "docs/research/cmbacktrace-get-cur-thread-name-source-candidate-audit.md"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"

FUNCTION = "open_cfw_cmbacktrace_get_cur_thread_name"
FUNCTION_SEAM = "open_cfw_cmbacktrace_pc_task_get_name_current"
FUNCTION_SECTION = ".text." + FUNCTION
ADAPTER_FUNCTION = "open_cfw_cmbacktrace_pc_task_get_name_current"
ADAPTER_SECTION = ".text." + ADAPTER_FUNCTION
HOST_CURRENT_TCB_SEAM = "open_cfw_cmbacktrace_host_test_current_tcb"
CANDIDATE_FUNCTION = "open_cfw_cmbacktrace_get_cur_thread_name_candidate"
CANDIDATE_PATH = CANDIDATE.relative_to(ROOT).as_posix()

TARGET_FLAGS = candidate_contract.TARGET_FLAGS
PROFILE_PINS = {
    "apple-clang": {
        "compiler": "/usr/bin/clang",
        "version": "Apple clang version 21.0.0 (clang-2100.3.33.1)",
        "adapter_offset": 123_596,
        "adapter_runtime": 0x007B_25F0,
        "get_offset": 123_612,
        "get_runtime": 0x007B_2600,
        "patch_hex": "1ef283bd00bf00bf",
        "patch_sha256": (
            "dbdba3b98e92adbd3518efb8e13509c"
            "0fd3ac0a8497cff70f6886c0901274ed0"
        ),
        "final_overlay": (
            360_578,
            "6f1f38ff89e350a1e104f09fd9278056ac6b8884d0bc21c8357c845ba82035a7",
        ),
        "core_overlay": (
            360_578,
            "6f1f38ff89e350a1e104f09fd9278056ac6b8884d0bc21c8357c845ba82035a7",
        ),
        "final_component": (
            3_883_974,
            "a3d36ad784519c7193976e1bbfe1b5dc7c6a07fd3bba185166e12fce2a0f19d9",
        ),
        "core_component": (
            3_883_974,
            "71d4e2b8011cc1e7503bdbe9e7251963f04b0092a80934d00e5a5ad181c651eb",
        ),
        "package": (
            4_677_046,
            "46733920d307a3830513b7f492de5345f552e27de65679eb4fde2b54dfca4ab4",
        ),
    },
    "linux-clang": {
        "compiler": "/home/linuxbrew/.linuxbrew/bin/clang",
        "version": "Homebrew clang version 22.1.8",
        "adapter_offset": 125_416,
        "adapter_runtime": 0x007B_2D0C,
        "get_offset": 125_432,
        "get_runtime": 0x007B_2D1C,
        "patch_hex": "1ff211b900bf00bf",
        "patch_sha256": (
            "7faa6dcd6eb772b5368352c1f72af3d5"
            "06efa4c0bdbfa7a8135b4810f09f41d1"
        ),
        "final_overlay": (
            152_912,
            "e045351065be7c01ff3bc4666940e0b536c2b114df0681169bd37031139d7c20",
        ),
        "core_overlay": (
            145_314,
            "2bea2be98b0154fa117e9a6e6cedc61a41c7b980279398657af3722cb96c8c19",
        ),
        "final_component": (
            3_676_308,
            "dc726a1c6187357c6c9a6b39152957bf3772fa06bc30d8bdd6db662af7c3dee7",
        ),
        "core_component": (
            3_668_710,
            "dc7f8a490c731da02850abec1d214f59c79c55062379f5100199e9999e5b28e8",
        ),
        "package": (
            4_469_364,
            "79e0ecab05996ac4d1bd71483b1045544a9bdc767abb6bff51a2cc700f89333e",
        ),
    },
}
OBJECT_PINS = {
    "get": {
        "source": SOURCE,
        "function": FUNCTION,
        "section": FUNCTION_SECTION,
        "object": (
            968,
            "94c3ef151c1d5519c90926739bbe401885cb3222b3d17c6e1e22d6a06a48ebf2",
        ),
        "text": (
            4,
            "fff7febf",
            "90a54a1f68a806a1795bd044856908235426b3c0f67be605fb94d3d5344a747f",
        ),
        "undefined": [FUNCTION_SEAM],
        "relocations": [(0, 30, FUNCTION_SEAM)],
    },
    "adapter": {
        "source": ADAPTER,
        "function": ADAPTER_FUNCTION,
        "section": ADAPTER_SECTION,
        "object": (
            828,
            "ecbe9064a048fb75f8d58731da8738aac5c8e478d99d05cfb266e288214a64f5",
        ),
        "text": (
            14,
            "44f62020c2f20700006834307047",
            "945d7e5d1ab31ee41e7f7e29c5f742602825b3bd792146d93d31bec8294671c2",
        ),
        "undefined": [],
        "relocations": [],
    },
}
EXIDX = (
    "0000000001000000",
    "01acecb507abfe1a354aa8064f4af5d3f1acd019e37db3c11c97523b71c76e9d",
)
LOCAL_PINS = {
    SOURCE: (
        2_089,
        "4b1141957314acb9c3a8846bd9b893ba1d3a7c14227949b670ca024e9761e1ea",
    ),
    HEADER: (
        669,
        "fccc238707db04730ad288c419c283208344d9da34019e5b7e6ba374492f7d0c",
    ),
    ADAPTER: (
        1_581,
        "80db039fbca9128059f625bd00066673857256e73fbe104998c4053f905ceaf6",
    ),
    ADAPTER_HEADER: (
        316,
        "0d3cd2a900e053f9b2358da8e50c4755c2574ca738dcaa871930ae771fcfbc7a",
    ),
    LICENSE: (
        1_101,
        "32ff92a2e9392b6acbcc734dd7c1e9f3c2e097b320b3cd87b3d7c01daf4a661a",
    ),
    HOST_FIXTURE: (
        1_982,
        "c9ba5a6b3c63aabab83431ffcf0afc616ed8f9461d0ff3bfed4c06de148a6181",
    ),
}


def sha256(value: bytes | Path) -> str:
    if isinstance(value, Path):
        value = value.read_bytes()
    return hashlib.sha256(value).hexdigest()


class RuntimeCmBacktraceGetCurThreadNameProductionTests(unittest.TestCase):
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
        if (cls.clang, version) != (
            PROFILE_PINS[cls.profile]["compiler"],
            PROFILE_PINS[cls.profile]["version"],
        ):
            raise AssertionError((cls.clang, version, PROFILE_PINS[cls.profile]))

        verification = subprocess.run(
            [sys.executable, str(VERIFIER)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        if verification.stdout != (
            "CmBacktrace compatibility snapshot verification passed\n"
        ):
            raise AssertionError("CmBacktrace verifier did not authenticate snapshot")

        upstream = UPSTREAM.read_bytes()
        cls.upstream_slice = candidate_contract.extract_upstream_function(upstream)
        if (
            len(upstream) != candidate_contract.UPSTREAM_SIZE
            or sha256(upstream) != candidate_contract.UPSTREAM_SHA256
            or len(cls.upstream_slice) != candidate_contract.UPSTREAM_SLICE_SIZE
            or sha256(cls.upstream_slice)
            != candidate_contract.UPSTREAM_SLICE_SHA256
        ):
            raise AssertionError("unauthenticated CmBacktrace source/configuration")

        (ROOT / "build").mkdir(exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="open-cfw-cmbacktrace-get-name-production-",
            dir=ROOT / "build",
        )
        temporary = Path(cls.temporary.name)
        cls.objects: dict[str, list[Path]] = {}
        for key, contract in OBJECT_PINS.items():
            source_path = contract["source"].relative_to(ROOT).as_posix()
            outputs = [temporary / f"{key}-a.o", temporary / f"{key}-b.o"]
            for output in outputs:
                subprocess.run(
                    [
                        cls.clang,
                        *TARGET_FLAGS,
                        "-c",
                        source_path,
                        "-o",
                        str(output),
                    ],
                    cwd=ROOT,
                    check=True,
                    capture_output=True,
                    text=True,
                )
            cls.objects[key] = outputs

        oracle = temporary / "upstream-oracle.c"
        prefix = b"""\
#define CMB_OS_PLATFORM_RTT 1
#define CMB_OS_PLATFORM_UCOSII 2
#define CMB_OS_PLATFORM_UCOSIII 3
#define CMB_OS_PLATFORM_FREERTOS 4
#define CMB_OS_PLATFORM_RTX5 5
#define CMB_OS_PLATFORM_THREADX 6
#define CMB_OS_PLATFORM_TYPE CMB_OS_PLATFORM_FREERTOS
const char *vTaskName(void);
"""
        renamed = cls.upstream_slice.replace(
            candidate_contract.UPSTREAM_MARKER,
            (
                b"const char *"
                b"open_cfw_cmbacktrace_get_cur_thread_name_upstream_oracle"
                b"(void) {"
            ),
            1,
        )
        oracle.write_bytes(prefix + renamed)
        library = temporary / (
            "cmbacktrace-get-name-production.dylib"
            if sys.platform == "darwin"
            else "cmbacktrace-get-name-production.so"
        )
        command = [
            cls.clang,
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-DOPEN_CFW_CMBACKTRACE_HOST_TEST_CURRENT_TCB=1",
            "-I",
            str(ROOT),
            str(SOURCE),
            str(ADAPTER),
            str(CANDIDATE),
            str(HOST_FIXTURE),
            str(oracle),
        ]
        if sys.platform == "darwin":
            command.extend(("-dynamiclib", "-o", str(library)))
        else:
            command.extend(("-shared", "-fPIC", "-o", str(library)))
        subprocess.run(command, check=True, capture_output=True, text=True)

        cls.library = ctypes.CDLL(str(library))
        cls.reset = (
            cls.library.open_cfw_test_cmbacktrace_get_cur_thread_name_production_reset
        )
        cls.reset.argtypes = [ctypes.c_size_t]
        cls.reset.restype = None
        cls.runners = []
        for name in (
            "open_cfw_test_cmbacktrace_get_cur_thread_name_production",
            "open_cfw_test_cmbacktrace_get_cur_thread_name_candidate",
            "open_cfw_test_cmbacktrace_get_cur_thread_name_upstream",
        ):
            function = getattr(cls.library, name)
            function.argtypes = []
            function.restype = ctypes.c_void_p
            cls.runners.append(function)
        cls.call_counts = []
        for name in (
            "open_cfw_test_cmbacktrace_production_calls",
            "open_cfw_test_cmbacktrace_candidate_calls",
            "open_cfw_test_cmbacktrace_upstream_calls",
        ):
            function = getattr(cls.library, name)
            function.argtypes = []
            function.restype = ctypes.c_uint32
            cls.call_counts.append(function)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def calls(self) -> tuple[int, int, int]:
        return tuple(function() for function in self.call_counts)

    def test_production_sources_license_and_compatibility_are_pinned(self) -> None:
        for path, (size, digest) in LOCAL_PINS.items():
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertEqual(path.stat().st_size, size)
                self.assertEqual(sha256(path), digest)

        provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        self.assertEqual(provenance["license"], "MIT")
        self.assertEqual(
            provenance["upstream"]["selected_commit"],
            candidate_contract.SELECTED_COMMIT,
        )
        self.assertEqual(
            provenance["selection"]["compatible_ceiling_commit"],
            candidate_contract.SELECTED_COMMIT,
        )
        self.assertFalse(provenance["selection"]["exact_g2_checkout_proven"])
        self.assertEqual(LICENSE.read_bytes(), UPSTREAM_LICENSE.read_bytes() + b"\n")

        source = SOURCE.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        adapter = ADAPTER.read_text(encoding="utf-8")
        for token in (
            "Copyright (c) 2016-2019, Armink",
            "SPDX-License-Identifier: MIT",
            candidate_contract.SELECTED_COMMIT,
            "not a claim that Even used that exact checkout",
            "[0x00593AF6,0x00593AFE)",
            FUNCTION_SEAM + "()",
        ):
            self.assertIn(token, source)
        self.assertIn("current TCB word", header)
        self.assertIn("incoming register", header)
        self.assertIn("__attribute__((used, noinline))", adapter)
        self.assertIn("0x20074A20U", adapter)
        self.assertIn("0x34U", adapter)
        self.assertIn("OPEN_CFW_CMBACKTRACE_HOST_TEST_CURRENT_TCB", adapter)
        self.assertIn(HOST_CURRENT_TCB_SEAM, adapter)
        self.assertNotIn("open_cfw_freertos_pc_task_get_name", adapter)
        self.assertNotIn("_candidate", source + header + adapter)

    def test_candidate_remains_absent_from_production_registrations(self) -> None:
        for path in (OVERLAY, MANIFEST, MAKEFILE):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn(CANDIDATE_PATH, text, path)
            self.assertNotIn(CANDIDATE_FUNCTION, text, path)

    def test_null_normal_empty_idle_and_40_byte_names_match_oracles(self) -> None:
        cases = [
            ("normal", b"worker"),
            ("empty", b""),
            ("idle", b"IDLE"),
            ("forty-byte", b"C" * 40),
        ]
        for label, name in cases:
            tcb = ctypes.create_string_buffer(0x34 + len(name) + 1)
            current_tcb = ctypes.addressof(tcb)
            expected = current_tcb + 0x34
            ctypes.memmove(expected, name + b"\0", len(name) + 1)
            observed = []
            for index, runner in enumerate(self.runners):
                self.reset(current_tcb)
                observed.append(runner())
                expected_calls = [0, 0, 0]
                expected_calls[index] = 1
                self.assertEqual(self.calls(), tuple(expected_calls), label)
            self.assertEqual(observed, [expected, expected, expected], label)
            self.assertEqual(ctypes.string_at(observed[0], len(name)), name, label)

        for index, runner in enumerate(self.runners):
            self.reset(0)
            self.assertEqual(runner(), 0x34)
            expected_calls = [0, 0, 0]
            expected_calls[index] = 1
            self.assertEqual(self.calls(), tuple(expected_calls), "null TCB")

    def test_apple_and_linux_raw_object_contracts_are_exact(self) -> None:
        for key, contract in OBJECT_PINS.items():
            objects = self.objects[key]
            self.assertEqual(objects[0].read_bytes(), objects[1].read_bytes())
            for path in objects:
                with self.subTest(profile=self.profile, leaf=key, object=path.name):
                    self.assertEqual(path.stat().st_size, contract["object"][0])
                    self.assertEqual(sha256(path), contract["object"][1])
                    data, sections = apollo_overlay.parse_elf32(path)
                    section = apollo_overlay.section_named(
                        sections, contract["section"]
                    )
                    text = data[
                        int(section["offset"]):
                        int(section["offset"]) + int(section["size"])
                    ]
                    self.assertEqual(int(section["alignment"]), 4)
                    self.assertEqual(len(text), contract["text"][0])
                    self.assertEqual(text.hex(), contract["text"][1])
                    self.assertEqual(sha256(text), contract["text"][2])

                    executable = [
                        item["name"]
                        for item in sections
                        if int(item["size"]) > 0 and int(item["flags"]) & 0x4
                    ]
                    self.assertEqual(executable, [contract["section"]])
                    symbols = apollo_overlay.parse_elf32_symbols(data, sections)
                    by_name = {item["name"]: item for item in symbols if item["name"]}
                    self.assertEqual(
                        int(by_name[contract["function"]]["size"]),
                        contract["text"][0],
                    )
                    self.assertEqual(
                        [
                            item["name"]
                            for item in symbols
                            if item["name"] and int(item["section_index"]) == 0
                        ],
                        contract["undefined"],
                    )

                    text_relocations = []
                    exidx_relocations = []
                    for relocation_section in sections:
                        if int(relocation_section["type"]) != 9:
                            continue
                        target = sections[int(relocation_section["info"])]
                        for index in range(int(relocation_section["size"]) // 8):
                            offset, information = struct.unpack_from(
                                "<II",
                                data,
                                int(relocation_section["offset"]) + index * 8,
                            )
                            record = (
                                offset,
                                information & 0xFF,
                                symbols[information >> 8]["name"],
                            )
                            if target["name"] == contract["section"]:
                                text_relocations.append(record)
                            elif target["name"] == ".ARM.exidx" + contract["section"]:
                                exidx_relocations.append(record)
                    self.assertEqual(text_relocations, contract["relocations"])
                    self.assertEqual(exidx_relocations, [(0, 42, "")])

                    exidx = apollo_overlay.section_named(
                        sections, ".ARM.exidx" + contract["section"]
                    )
                    exidx_bytes = data[
                        int(exidx["offset"]):
                        int(exidx["offset"]) + int(exidx["size"])
                    ]
                    self.assertEqual(exidx_bytes.hex(), EXIDX[0])
                    self.assertEqual(sha256(exidx_bytes), EXIDX[1])

    def test_registration_placement_patch_and_whole_component_ingress(self) -> None:
        config = json.loads(OVERLAY.read_text(encoding="utf-8"))
        self.assertGreater(len(config["functions"]), 0)
        self.assertGreater(len(config["patch_sites"]), 0)
        self.assertGreater(len(config["relocated_leaves"]), 0)
        self.assertEqual(config["functions"].count(ADAPTER_FUNCTION), 1)
        self.assertEqual(config["functions"].count(FUNCTION), 1)

        adapter = next(
            item for item in config["relocated_leaves"]
            if item["function"] == ADAPTER_FUNCTION
        )
        get_name = next(
            item for item in config["relocated_leaves"]
            if item["function"] == FUNCTION
        )
        patch = next(
            item for item in config["patch_sites"]
            if item["name"] == "replace_cmbacktrace_get_cur_thread_name"
        )
        self.assertTrue(adapter["strict_relocation_contract"])
        self.assertTrue(get_name["strict_relocation_contract"])
        self.assertEqual(adapter["relocations"], [])
        self.assertEqual(
            get_name["relocations"],
            [{
                "offset": 0,
                "type": "R_ARM_THM_JUMP24",
                "symbol": ADAPTER_FUNCTION,
                "symbol_type": "STT_NOTYPE",
                "target_function": ADAPTER_FUNCTION,
            }],
        )
        self.assertEqual(
            patch,
            {
                "name": "replace_cmbacktrace_get_cur_thread_name",
                "runtime_address": candidate_contract.START,
                "expected_size": candidate_contract.END - candidate_contract.START,
                "expected_sha256": candidate_contract.STOCK_SHA256,
                "branch": "b_w",
                "target_function": FUNCTION,
            },
        )

        for profile, pins in PROFILE_PINS.items():
            adapter_expected = (
                adapter["expected"] if profile == "apple-clang"
                else adapter["toolchain_profiles"][profile]["expected"]
            )
            get_expected = (
                get_name["expected"] if profile == "apple-clang"
                else get_name["toolchain_profiles"][profile]["expected"]
            )
            aggregate = (
                config["expected"] if profile == "apple-clang"
                else config["toolchain_profiles"][profile]["expected"]
            )
            self.assertEqual(adapter_expected["offset"], pins["adapter_offset"])
            self.assertEqual(adapter_expected["size"], 14)
            self.assertEqual(adapter_expected["sha256"], OBJECT_PINS["adapter"]["text"][2])
            self.assertEqual(get_expected["offset"], pins["get_offset"])
            self.assertEqual(get_expected["size"], 4)
            self.assertEqual(get_expected["sha256"], "cdcdfc75bb08504fce75a95fac5acf2c8f9502c9eecc7c886198f721cf321b0b")
            self.assertEqual(
                (aggregate["overlay_size"], aggregate["overlay_sha256"]),
                pins["final_overlay"],
            )
            self.assertEqual(
                (aggregate["component_size"], aggregate["component_sha256"]),
                pins["final_component"],
            )

        stage_config = json.loads(OVERLAY.read_text(encoding="utf-8"))
        stage_config["expected"] = stage_config["core_stage_expected"]
        for profile in stage_config.get("toolchain_profiles", {}).values():
            if "core_stage_expected" in profile:
                profile["expected"] = profile["core_stage_expected"]
        stage_config_path = Path(self.temporary.name) / "core-stage-overlay.json"
        stage_config_path.write_text(
            json.dumps(stage_config, indent=2) + "\n", encoding="utf-8"
        )
        output = Path(self.temporary.name) / "component"
        report = apollo_overlay.build(
            root=ROOT,
            config_path=stage_config_path,
            output_dir=output,
            clang=self.clang,
            toolchain_profile=self.profile,
        )
        pins = PROFILE_PINS[self.profile]
        self.assertEqual(
            (report["overlay"]["size"], report["overlay"]["sha256"]),
            pins["core_overlay"],
        )
        self.assertEqual(
            (report["component"]["size"], report["component"]["sha256"]),
            pins["core_component"],
        )
        by_function = {
            item["extraction"]["function"]: item
            for item in report["relocated_leaves"]
        }
        adapter_report = by_function[ADAPTER_FUNCTION]
        get_report = by_function[FUNCTION]
        self.assertEqual(adapter_report["placement"], {
            "alignment": 4,
            "offset": pins["adapter_offset"],
            "padding_before": 0,
            "runtime_address": pins["adapter_runtime"],
            "runtime_address_hex": f"0x{pins['adapter_runtime']:08X}",
            "size": 14,
        })
        self.assertEqual(adapter_report["extraction"]["relocations"], [])
        self.assertEqual(get_report["placement"]["offset"], pins["get_offset"])
        self.assertEqual(get_report["placement"]["runtime_address"], pins["get_runtime"])
        self.assertEqual(get_report["placement"]["padding_before"], 2)
        self.assertEqual(get_report["extraction"]["sha256"], "cdcdfc75bb08504fce75a95fac5acf2c8f9502c9eecc7c886198f721cf321b0b")
        self.assertEqual(get_report["extraction"]["relocation_count"], 1)
        self.assertEqual(
            get_report["extraction"]["relocations"][0]["target_address"],
            pins["adapter_runtime"],
        )

        patch_report = next(
            item for item in report["overlay"]["patched_sites"]
            if item["name"] == "replace_cmbacktrace_get_cur_thread_name"
        )
        replacement = bytes.fromhex(patch_report["replacement_hex"])
        self.assertEqual(replacement.hex(), pins["patch_hex"])
        self.assertEqual(sha256(replacement), pins["patch_sha256"])
        self.assertEqual(patch_report["target_address"], pins["get_runtime"])
        self.assertEqual(
            apollo_overlay.decode_thumb_branch(
                candidate_contract.START, replacement[:4], link=False
            ),
            pins["get_runtime"],
        )
        self.assertEqual(replacement[4:], b"\x00\xbf\x00\xbf")

        component = (output / "ota_s200_firmware_ota.bin").read_bytes()
        official = OFFICIAL.read_bytes()
        application = component[candidate_contract.PACKAGE_PREAMBLE:]
        stock_offset = (
            candidate_contract.PACKAGE_PREAMBLE
            + candidate_contract.START
            - candidate_contract.APPLICATION_BASE
        )
        self.assertEqual(component[stock_offset:stock_offset + 8], replacement)
        self.assertEqual(component[stock_offset - 8:stock_offset], official[stock_offset - 8:stock_offset])
        self.assertEqual(component[stock_offset + 8:stock_offset + 16], official[stock_offset + 8:stock_offset + 16])
        overlay_offset = report["overlay"]["overlay_payload_offset"]
        self.assertEqual(
            component[overlay_offset + pins["adapter_offset"]:overlay_offset + pins["adapter_offset"] + 14].hex(),
            OBJECT_PINS["adapter"]["text"][1],
        )
        self.assertEqual(
            component[overlay_offset + pins["adapter_offset"] + 14:overlay_offset + pins["get_offset"]],
            b"\0\0",
        )
        self.assertEqual(
            component[overlay_offset + pins["get_offset"]:overlay_offset + pins["get_offset"] + 4].hex(),
            "fff7f6bf",
        )

        ranges = {
            "stock": (candidate_contract.START, candidate_contract.END),
            "old_adapter": (
                candidate_contract.DEPENDENCY_START,
                candidate_contract.DEPENDENCY_END,
            ),
            "adapter": (pins["adapter_runtime"], pins["adapter_runtime"] + 14),
            "alignment": (pins["adapter_runtime"] + 14, pins["get_runtime"]),
            "get": (pins["get_runtime"], pins["get_runtime"] + 4),
        }
        wide_edges = []
        conditional_or_narrow = []
        for relative in range(0, len(application) - 3, 2):
            address = candidate_contract.APPLICATION_BASE + relative
            first, second = struct.unpack_from("<HH", application, relative)
            encoding = application[relative:relative + 4].hex()
            for link in (True, False):
                target = candidate_contract.thumb_wide_branch_target(
                    address, first, second, link=link
                )
                if target is None:
                    continue
                for name, (start, end) in ranges.items():
                    if start <= target < end:
                        wide_edges.append((address, target, link, name, encoding))
            conditional = candidate_contract.wide_conditional_target(
                address, first, second
            )
            targets = (
                *((conditional,) if conditional is not None else ()),
                *candidate_contract.narrow_targets(address, first),
            )
            for target in targets:
                for name, (start, end) in ranges.items():
                    if start <= target < end:
                        conditional_or_narrow.append((address, target, name, encoding))
        self.assertEqual(
            wide_edges,
            [
                (candidate_contract.START, pins["get_runtime"], False, "get", replacement[:4].hex()),
                *[
                    (address, candidate_contract.START, True, "stock", encoding)
                    for address, encoding in candidate_contract.CALLERS
                ],
                (pins["get_runtime"], pins["adapter_runtime"], False, "adapter", "fff7f6bf"),
            ],
        )
        self.assertEqual(conditional_or_narrow, [])

        stored = []
        for name, (start, end) in ranges.items():
            for canonical in range(start, end):
                for value in {canonical, canonical | 1}:
                    needle = struct.pack("<I", value)
                    position = application.find(needle)
                    while position >= 0:
                        stored.append((name, candidate_contract.APPLICATION_BASE + position, value))
                        position = application.find(needle, position + 1)
        self.assertEqual(stored, [])

    def test_manifest_tiling_ownership_package_and_documentation_are_exact(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        component = manifest["component_overrides"]["apollo_main"]
        provider = component["provider"]
        self.assertEqual(
            (provider["size"], provider["sha256"]),
            PROFILE_PINS["apple-clang"]["final_component"],
        )
        self.assertEqual(
            (
                provider["profiles"]["linux-clang"]["size"],
                provider["profiles"]["linux-clang"]["sha256"],
            ),
            PROFILE_PINS["linux-clang"]["final_component"],
        )
        regions = component["regions"]
        self.assertGreater(len(regions), 0)
        self.assertEqual(regions[0]["file_offset"], 0)
        for left, right in zip(regions, regions[1:]):
            self.assertEqual(left["file_offset"] + left["size"], right["file_offset"])
        self.assertEqual(regions[-1]["file_offset"] + regions[-1]["size"], provider["size"])
        by_name = {item["name"]: item for item in regions}
        self.assertEqual(
            by_name["cmbacktrace_get_cur_thread_name_source_replacement"]["address_status"],
            "generated_source_entry_replacement",
        )
        self.assertEqual(
            by_name["apollo_cmbacktrace_current_task_name_adapter_source_leaf"]["target_address"],
            PROFILE_PINS["apple-clang"]["adapter_runtime"],
        )
        self.assertEqual(
            by_name["apollo_cmbacktrace_get_cur_thread_name_source_alignment"]["size"],
            2,
        )
        self.assertEqual(
            by_name["apollo_cmbacktrace_get_cur_thread_name_source_leaf"]["target_address"],
            PROFILE_PINS["apple-clang"]["get_runtime"],
        )
        accounting: dict[str, tuple[int, int]] = {}
        for status in {item["address_status"] for item in regions}:
            selected = [item for item in regions if item["address_status"] == status]
            accounting[status] = (len(selected), sum(item["size"] for item in selected))
        self.assertEqual(sum(count for count, _ in accounting.values()), len(regions))
        self.assertEqual(sum(size for _, size in accounting.values()), provider["size"])
        self.assertIn("official_blob", accounting)
        self.assertIn("source_compiled", accounting)
        package = manifest["package"]
        self.assertEqual(
            (package["expected_size"], package["expected_sha256"]),
            PROFILE_PINS["apple-clang"]["package"],
        )
        self.assertEqual(
            (
                package["profiles"]["linux-clang"]["expected_size"],
                package["profiles"]["linux-clang"]["expected_sha256"],
            ),
            PROFILE_PINS["linux-clang"]["package"],
        )
        for path, tokens in {
            NOTICE: ("CmBacktrace", "MIT", "73714489f9d8af130aacb515586b397b604a5768"),
            EVIDENCE: ("0x00593AF6", "0x007B25F4", "null-to-0x34"),
            AUDIT: ("Production promotion", "stock entry", "0x007B2D1C"),
            ROOT / "docs/memory-map.md": ("0x007B25F0", "0x007B2D0C", "CmBacktrace"),
            ROOT / "docs/source-coverage.md": ("0x00593AF6", "123,763", "CmBacktrace"),
            ROOT / "docs/upstream-inventory.md": ("CmBacktrace", "production", "73714489"),
            ROOT / "components/README.md": ("CmBacktrace", "123,620", "125,440"),
            ROOT / "docs/linux-reproducible-build.md": ("CmBacktrace", "125,440", "exact-root"),
        }.items():
            text = path.read_text(encoding="utf-8")
            for token in tokens:
                self.assertIn(token, text, (path, token))


if __name__ == "__main__":
    unittest.main()
