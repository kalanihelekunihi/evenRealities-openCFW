from __future__ import annotations

import os

import hashlib
import json
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = (
    ROOT
    / "components"
    / "apollo_main"
    / "core_overlay"
    / "runtime_freertos_ntz_port.S"
)
UPSTREAM = (
    ROOT
    / "third_party"
    / "freertos-kernel"
    / "portable"
    / "IAR"
    / "ARM_CM55_NTZ"
    / "non_secure"
    / "portasm.s"
)
PROVENANCE = ROOT / "third_party" / "freertos-kernel" / "PROVENANCE.json"
OFFICIAL = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
CONFIG = (
    ROOT
    / "components"
    / "apollo_main"
    / "core_overlay"
    / "overlay.json"
)

APPLICATION_BASE = 0x0043_8000
PACKAGE_PREAMBLE_SIZE = 32
PACKAGE_SHA256 = (
    "36c5b0e499a68ac2493a497bdab9740fd"
    "3e7027730c26a9094eca47268a27863"
)
APPLICATION_SHA256 = (
    "19044a72bdfeb04c6b1b104d87da7b98"
    "e13cc18928528d84d999b6bcc0ba9701"
)
SOURCE_SHA256 = (
    "38c6a259ca2fbfbefb373ef5a80216f2"
    "e5f1cad998173ca2b4c9cfde6c01aee8"
)
UPSTREAM_SHA256 = (
    "eaa83b3867edec5560c69f2a21facd7a"
    "ff3c0f3bfcdfc5751722375ae328ee8f"
)
PROVENANCE_SHA256 = (
    "810d28df622a96646dd70d56311355c35"
    "31393fcf0fac1feac585f9cd799f99a"
)
UPSTREAM_COMMIT = "def7d2df2b0506d3d249334974f51e427c17a41c"
UPSTREAM_TREE = "7496dfa815c3cea2f45a090c6e92d113f494b930"
UPSTREAM_GIT_BLOB = "4d02a431e1d759f12f50e70fc55a7b0b4d368e89"

TARGET_FLAGS = [
    "--target=arm-none-eabi",
    "-mcpu=cortex-m55",
    "-mthumb",
    "-ffreestanding",
    "-fno-builtin",
    "-ffunction-sections",
    "-fdata-sections",
    "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables",
    "-Wall",
    "-Wextra",
    "-Werror",
]

PRODUCTION_SOURCE = {
    "path": (
        "components/apollo_main/core_overlay/"
        "runtime_freertos_ntz_port.S"
    ),
    "size": 5487,
    "sha256": SOURCE_SHA256,
    "license": "MIT",
    "origin": (
        "sectionized Clang-syntax adaptation of authenticated "
        "FreeRTOS-Kernel V10.5.1 IAR Cortex-M55 port assembly"
    ),
    "upstream": (
        "third_party/freertos-kernel/portable/IAR/"
        "ARM_CM55_NTZ/non_secure/portasm.s"
    ),
    "upstream_commit": UPSTREAM_COMMIT,
    "evidence": "docs/research/freertos-g2-config-port-audit.md",
}
PRODUCTION_TOOLCHAIN = {
    "target": "arm-none-eabi",
    "reviewed_version_prefix": "Apple clang version 21.0.0",
    "flags": TARGET_FLAGS[1:],
}
PRODUCTION_TOOLCHAIN_REPORT = {
    "executable": os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
    "version": "Apple clang version 21.0.0 (clang-2100.3.30.1)",
    "target": "arm-none-eabi",
    "flags": TARGET_FLAGS[1:],
}

STOCK = {
    "vRestoreContextOfFirstTask": {
        "start": 0x005F_A058,
        "body": bytes.fromhex(
            "364a1168086806c881f30b88022181f31488203080f30988"
            "bff36f8f4ff0000080f311881047"
        ),
        "sha256": (
            "10edd4871b5f0c829e38618f1003ef0c"
            "45ec3629219317e23c62a2e255b0f4f8"
        ),
    },
    "vRaisePrivilege": {
        "start": 0x005F_A07E,
        "body": bytes.fromhex("eff3148020f0010080f314887047"),
        "sha256": (
            "29bceedf776515c291813e4eecd9a836"
            "378b81550c42d08aee35cf15df3bd8db"
        ),
    },
    "vStartFirstTask": {
        "start": 0x005F_A08C,
        "body": bytes.fromhex(
            "2a480068006880f3088862b661b6bff34f8fbff36f8f02df"
        ),
        "sha256": (
            "44ba0097fbbc1d0691837d5c51bee83e"
            "6b61509c9d89efffee9c202d930e6347"
        ),
    },
    "PendSV_Handler": {
        "start": 0x005F_A0C8,
        "body": bytes.fromhex(
            "eff309801ef0100f08bf20ed108aeff30b82734620e9fc0f"
            "144a116808604ff0300080f31188bff34f8fbff36f8f"
            "5bf65df84ff0000080f311880c4a11680868b0e8fc0f"
            "13f0100f08bfb0ec108a82f30b8880f309881847"
        ),
        "sha256": (
            "d8e234bfa34805ad160e41ef54801973"
            "c9c871b36cf7ac0f365b56fe503253e3"
        ),
    },
    "SVC_Handler": {
        "start": 0x005F_A120,
        "body": bytes.fromhex(
            "1ef0040f0cbfeff30880eff3098048f601b8"
        ),
        "sha256": (
            "d0fac197473b52d6ed466462d237ddb20"
            "dd8096a6507ea559e75d4bd9d88da94"
        ),
    },
}

ADAPTER_BODY_SHA256 = {
    "vRestoreContextOfFirstTask": (
        "6cd49195f965664fa52a501576fafc8f"
        "84a77f4719cf755515ef7606b3a1d8be"
    ),
    "vRaisePrivilege": (
        "29bceedf776515c291813e4eecd9a836"
        "378b81550c42d08aee35cf15df3bd8db"
    ),
    "vStartFirstTask": (
        "28d1d6e471df04ae8476e1355225e2d"
        "4d3673d4af90b68338fc8589441ae16b7"
    ),
    "PendSV_Handler": (
        "12c7f208de16f3d5636cd00d83078475"
        "52937eb484b86b185b45b686553953ee"
    ),
    "SVC_Handler": (
        "1807cfce5ab3df565e585de5dd35011f"
        "18e5994e748363f15cb7376aa796e1c4"
    ),
}

SECTION_CONTRACT = {
    "vRestoreContextOfFirstTask": {
        "size": 38,
        "alignment": 2,
        "tail": b"",
    },
    "vRaisePrivilege": {
        "size": 14,
        "alignment": 2,
        "tail": b"",
    },
    "vStartFirstTask": {
        "size": 24,
        "alignment": 2,
        "tail": b"",
    },
    "PendSV_Handler": {
        "size": 88,
        "alignment": 2,
        "tail": b"",
    },
    "SVC_Handler": {
        "size": 18,
        "alignment": 2,
        "tail": b"",
    },
}

RELOCATION_CONTRACT = [
    {
        "section": ".text.vRestoreContextOfFirstTask",
        "offset": 0,
        "type": 11,
        "symbol": "open_cfw_freertos_px_current_tcb_literal",
    },
    {
        "section": ".text.vStartFirstTask",
        "offset": 0,
        "type": 11,
        "symbol": "open_cfw_freertos_vtor_literal",
    },
    {
        "section": ".text.PendSV_Handler",
        "offset": 0x18,
        "type": 11,
        "symbol": "open_cfw_freertos_px_current_tcb_literal",
    },
    {
        "section": ".text.PendSV_Handler",
        "offset": 0x2E,
        "type": 10,
        "symbol": "vTaskSwitchContext",
    },
    {
        "section": ".text.PendSV_Handler",
        "offset": 0x3A,
        "type": 11,
        "symbol": "open_cfw_freertos_px_current_tcb_literal",
    },
    {
        "section": ".text.SVC_Handler",
        "offset": 0x0E,
        "type": 30,
        "symbol": "vPortSVCHandler_C",
    },
]

IN_PLACE_RELOCATION_CONTRACT = {
    "vRestoreContextOfFirstTask": [
        {
            "offset": 0,
            "type": "R_ARM_THM_PC8",
            "symbol": "open_cfw_freertos_px_current_tcb_literal",
            "target_address": 0x005F_A134,
            "target_expected_hex": "204a0720",
        },
    ],
    "vRaisePrivilege": [],
    "vStartFirstTask": [
        {
            "offset": 0,
            "type": "R_ARM_THM_PC8",
            "symbol": "open_cfw_freertos_vtor_literal",
            "target_address": 0x005F_A138,
            "target_expected_hex": "08ed00e0",
        },
    ],
    "PendSV_Handler": [
        {
            "offset": 0x18,
            "type": "R_ARM_THM_PC8",
            "symbol": "open_cfw_freertos_px_current_tcb_literal",
            "target_address": 0x005F_A134,
            "target_expected_hex": "204a0720",
        },
        {
            "offset": 0x2E,
            "type": "R_ARM_THM_CALL",
            "symbol": "vTaskSwitchContext",
            "target_address": 0x0045_51B4,
        },
        {
            "offset": 0x3A,
            "type": "R_ARM_THM_PC8",
            "symbol": "open_cfw_freertos_px_current_tcb_literal",
            "target_address": 0x005F_A134,
            "target_expected_hex": "204a0720",
        },
    ],
    "SVC_Handler": [
        {
            "offset": 0x0E,
            "type": "R_ARM_THM_JUMP24",
            "symbol": "vPortSVCHandler_C",
            "target_address": 0x0044_2134,
        },
    ],
}

PRODUCTION_IN_PLACE_RECORDS = [
    {
        "function": name,
        "runtime_address": int(STOCK[name]["start"]),
        "source": PRODUCTION_SOURCE,
        "toolchain": PRODUCTION_TOOLCHAIN,
        "stock": {
            "size": len(STOCK[name]["body"]),
            "sha256": STOCK[name]["sha256"],
        },
        "expected": {
            "size": len(STOCK[name]["body"]),
            "sha256": STOCK[name]["sha256"],
        },
        "relocations": IN_PLACE_RELOCATION_CONTRACT[name],
        "toolchain_profiles": {
            "linux-clang": {
                "reviewed_version_prefix": (
                    "Homebrew clang version 22.1.8"
                ),
            },
        },
    }
    for name in STOCK
]

STOCK_NORMALIZATION_SITES = {
    "vRestoreContextOfFirstTask": ((0, 2),),
    "vRaisePrivilege": (),
    "vStartFirstTask": ((0, 2),),
    "PendSV_Handler": ((24, 2), (46, 4), (58, 2)),
    "SVC_Handler": ((14, 4),),
}


_APPLE_ONLY = unittest.skipUnless(
    (os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang") == "apple-clang",
    "byte-exact / toolchain-specific Apple-clang assertion; Linux byte "
    "reproduction is verified end-to-end by tests/test_toolchain_profiles.py",
)


class RuntimeFreeRTOSNTZPortTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
        import analyze_g2_freertos_assert_port_seam
        import apollo_overlay

        cls.seam = analyze_g2_freertos_assert_port_seam
        cls.apollo_overlay = apollo_overlay

        build_root = ROOT / "build"
        build_root.mkdir(exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="test-runtime-freertos-ntz-port-",
            dir=build_root,
        )
        cls.target_object = (
            Path(cls.temporary.name) / "runtime_freertos_ntz_port.o"
        )
        subprocess.run(
            [
                os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                *TARGET_FLAGS,
                "-c",
                str(SOURCE),
                "-o",
                str(cls.target_object),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        cls.object_data, cls.sections = apollo_overlay.parse_elf32(
            cls.target_object
        )
        cls.section_by_name = {
            str(section["name"]): section for section in cls.sections
        }
        cls.symbols = apollo_overlay.parse_elf32_symbols(
            cls.object_data,
            cls.sections,
        )
        cls.symbol_by_name = {
            str(symbol["name"]): symbol
            for symbol in cls.symbols
            if symbol["name"]
        }

        cls.relocations = []
        for section in cls.sections:
            if int(section["type"]) != apollo_overlay.SHT_REL:
                continue
            relocated = cls.sections[int(section["info"])]
            for index in range(int(section["size"]) // 8):
                offset, info = struct.unpack_from(
                    "<II",
                    cls.object_data,
                    int(section["offset"]) + index * 8,
                )
                cls.relocations.append(
                    {
                        "section": str(relocated["name"]),
                        "offset": offset,
                        "type": info & 0xFF,
                        "symbol": str(cls.symbols[info >> 8]["name"]),
                    }
                )

        package = OFFICIAL.read_bytes()
        cls.package = package
        cls.application = package[PACKAGE_PREAMBLE_SIZE:]
        cls.production_config = json.loads(CONFIG.read_text(encoding="utf-8"))
        cls.production_output = (
            Path(cls.temporary.name) / "production-component"
        )
        cls.production_report = apollo_overlay.build(
            root=ROOT,
            config_path=CONFIG,
            output_dir=cls.production_output,
            clang=os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
        )
        cls.production_overlay = (
            cls.production_output / "apollo_core_overlay.bin"
        ).read_bytes()
        cls.production_component = (
            cls.production_output / "ota_s200_firmware_ota.bin"
        ).read_bytes()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @staticmethod
    def digest(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @classmethod
    def section_bytes(cls, name: str) -> bytes:
        section = cls.section_by_name[name]
        start = int(section["offset"])
        return cls.object_data[start:start + int(section["size"])]

    @classmethod
    def function_body(cls, name: str) -> bytes:
        symbol = cls.symbol_by_name[name]
        section = cls.sections[int(symbol["section_index"])]
        start = int(section["offset"]) + (int(symbol["value"]) & ~1)
        return cls.object_data[start:start + int(symbol["size"])]

    @classmethod
    def official_span(cls, start: int, size: int) -> bytes:
        offset = start - APPLICATION_BASE
        return cls.application[offset:offset + size]

    def test_source_upstream_and_license_provenance_are_pinned(self) -> None:
        self.assertEqual(len(SOURCE.read_bytes()), 5487)
        self.assertEqual(self.digest(SOURCE.read_bytes()), SOURCE_SHA256)
        source = SOURCE.read_text(encoding="utf-8")
        for fragment in (
            "SPDX-License-Identifier: MIT",
            "Permission is hereby granted",
            "FreeRTOS Kernel V10.5.1",
            UPSTREAM_COMMIT,
            "portable/IAR/ARM_CM55_NTZ/non_secure/portasm.s",
            "configENABLE_MPU = 0",
            "configENABLE_TRUSTZONE = 0",
            "configENABLE_FPU = 1",
            "configMAX_SYSCALL_INTERRUPT_PRIORITY = 0x30",
            "runtime_freertos_interrupt_mask.S",
            "open_cfw_freertos_px_current_tcb_literal = 0x005FA134",
            "open_cfw_freertos_vtor_literal           = 0x005FA138",
            "0x20074A20 (pxCurrentTCB)",
            "0xE000ED08",
            "No section owns a local literal pool or alignment tail",
        ):
            self.assertIn(fragment, source)

        self.assertEqual(len(UPSTREAM.read_bytes()), 11686)
        self.assertEqual(self.digest(UPSTREAM.read_bytes()), UPSTREAM_SHA256)
        upstream = UPSTREAM.read_text(encoding="utf-8")
        for name in STOCK:
            self.assertIn(f"{name}:", upstream)
        for fragment in (
            "ldr  r2, =pxCurrentTCB",
            "mov r0, #configMAX_SYSCALL_INTERRUPT_PRIORITY",
            "bl vTaskSwitchContext",
            "b vPortSVCHandler_C",
            "vstmdbeq r0!, {s16-s31}",
            "vldmiaeq r0!, {s16-s31}",
        ):
            self.assertIn(fragment, upstream)

        self.assertEqual(
            self.digest(PROVENANCE.read_bytes()),
            PROVENANCE_SHA256,
        )
        provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        self.assertEqual(provenance["license"], "MIT")
        self.assertEqual(
            provenance["upstream"]["selected_commit"],
            UPSTREAM_COMMIT,
        )
        self.assertEqual(
            provenance["upstream"]["selected_tree"],
            UPSTREAM_TREE,
        )
        self.assertEqual(
            provenance["g2_boundary"]["g2_selected_portable_variant"],
            "portable/IAR/ARM_CM55_NTZ/non_secure",
        )
        self.assertEqual(
            provenance["files"][
                "portable/IAR/ARM_CM55_NTZ/non_secure/portasm.s"
            ],
            {
                "size": 11686,
                "sha256": UPSTREAM_SHA256,
                "git_blob_sha1": UPSTREAM_GIT_BLOB,
            },
        )

    def test_official_bodies_vectors_and_shared_pool_are_exact(self) -> None:
        self.assertEqual(len(self.package), 3_523_396)
        self.assertEqual(self.digest(self.package), PACKAGE_SHA256)
        self.assertEqual(
            self.digest(self.application),
            APPLICATION_SHA256,
        )

        combined = bytearray()
        for name, contract in STOCK.items():
            body = contract["body"]
            official = self.official_span(
                int(contract["start"]),
                len(body),
            )
            self.assertEqual(official, body, name)
            self.assertEqual(self.digest(official), contract["sha256"])
            combined.extend(official)
        self.assertEqual(len(combined), 182)
        self.assertEqual(
            self.digest(bytes(combined)),
            "ca6be773f86c12eea198872e73541d97"
            "ce6bb806e2d03c57c1f540ad43c1e2fd",
        )

        self.assertEqual(
            self.official_span(0x005F_A132, 10),
            bytes.fromhex("0000204a072008ed00e0"),
        )
        self.assertEqual(
            self.official_span(0x005F_A134, 4),
            bytes.fromhex("204a0720"),
        )
        self.assertEqual(
            self.official_span(0x005F_A138, 4),
            bytes.fromhex("08ed00e0"),
        )
        self.assertEqual(
            struct.unpack_from("<I", self.application, 11 * 4)[0],
            0x005F_A121,
        )
        self.assertEqual(
            struct.unpack_from("<I", self.application, 14 * 4)[0],
            0x005F_A0C9,
        )

        calls = {name: [] for name in STOCK}
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
            first, second = struct.unpack_from(
                "<HH",
                self.application,
                offset,
            )
            target = self.seam.thumb_wide_branch_target(
                address,
                first,
                second,
                link=True,
            )
            for name, contract in STOCK.items():
                if target == int(contract["start"]):
                    calls[name].append(address)
        self.assertEqual(
            calls,
            {
                "vRestoreContextOfFirstTask": [0x0044_2146],
                "vRaisePrivilege": [],
                "vStartFirstTask": [0x0044_2200],
                "PendSV_Handler": [],
                "SVC_Handler": [],
            },
        )

    def test_target_object_has_five_bounded_function_sections(self) -> None:
        self.assertEqual(int(self.section_by_name[".text"]["size"]), 0)
        for name, contract in SECTION_CONTRACT.items():
            section_name = f".text.{name}"
            section = self.section_by_name[section_name]
            self.assertEqual(
                {
                    "type": int(section["type"]),
                    "flags": int(section["flags"]),
                    "size": int(section["size"]),
                    "alignment": int(section["alignment"]),
                },
                {
                    "type": 1,
                    "flags": 6,
                    "size": contract["size"],
                    "alignment": contract["alignment"],
                },
            )

            symbol = self.symbol_by_name[name]
            self.assertEqual(int(symbol["value"]), 1)
            self.assertEqual(
                int(symbol["size"]),
                len(STOCK[name]["body"]),
            )
            self.assertEqual(int(symbol["binding"]), 1)
            self.assertEqual(int(symbol["type"]), 2)
            self.assertEqual(
                str(self.sections[int(symbol["section_index"])]["name"]),
                section_name,
            )

            section_body = self.section_bytes(section_name)
            function_body = self.function_body(name)
            self.assertEqual(
                section_body[len(function_body):],
                contract["tail"],
            )
            self.assertEqual(
                self.digest(function_body),
                ADAPTER_BODY_SHA256[name],
            )

        defined_functions = {
            str(symbol["name"])
            for symbol in self.symbols
            if (
                int(symbol["type"]) == 2
                and int(symbol["section_index"]) != 0
            )
        }
        self.assertEqual(defined_functions, set(STOCK))
        self.assertNotIn("ulSetInterruptMask", defined_functions)
        self.assertNotIn("vClearInterruptMask", defined_functions)

    @_APPLE_ONLY
    def test_target_relocation_and_undefined_symbol_surface_is_exact(
        self,
    ) -> None:
        self.assertEqual(self.relocations, RELOCATION_CONTRACT)
        self.assertEqual(
            {
                str(symbol["name"])
                for symbol in self.symbols
                if (
                    symbol["name"]
                    and int(symbol["section_index"]) == 0
                )
            },
            {
                "open_cfw_freertos_px_current_tcb_literal",
                "open_cfw_freertos_vtor_literal",
                "vTaskSwitchContext",
                "vPortSVCHandler_C",
            },
        )

    def test_adapter_instruction_bodies_normalize_to_exact_stock(
        self,
    ) -> None:
        for name, contract in STOCK.items():
            stock = contract["body"]
            normalized = bytearray(self.function_body(name))
            for offset, size in STOCK_NORMALIZATION_SITES[name]:
                normalized[offset:offset + size] = stock[
                    offset:offset + size
                ]
            self.assertEqual(bytes(normalized), stock, name)

        self.assertEqual(
            self.function_body("vRaisePrivilege"),
            STOCK["vRaisePrivilege"]["body"],
        )

    def test_every_section_is_exactly_its_function_with_no_local_pool(
        self,
    ) -> None:
        for name, contract in STOCK.items():
            self.assertEqual(
                SECTION_CONTRACT[name]["size"],
                len(contract["body"]),
            )
            self.assertEqual(SECTION_CONTRACT[name]["tail"], b"")

        source = SOURCE.read_text(encoding="utf-8")
        self.assertNotIn(".ltorg", source)
        self.assertNotIn("=pxCurrentTCB", source)
        self.assertNotIn("=0xe000ed08", source)
        self.assertEqual(
            source.count(
                ".reloc  ., R_ARM_THM_PC8, "
                "open_cfw_freertos_px_current_tcb_literal"
            ),
            3,
        )
        self.assertEqual(
            source.count(
                ".reloc  ., R_ARM_THM_PC8, "
                "open_cfw_freertos_vtor_literal"
            ),
            1,
        )
        self.assertEqual(source.count(".inst.n 0x4a00"), 3)
        self.assertEqual(source.count(".inst.n 0x4800"), 1)

    def test_approved_in_place_relocations_resolve_to_exact_stock(
        self,
    ) -> None:
        for name, contract in STOCK.items():
            linked, extraction = (
                self.apollo_overlay.extract_in_place_function_section(
                    self.target_object,
                    name,
                    runtime_address=int(contract["start"]),
                    relocation_configs=IN_PLACE_RELOCATION_CONTRACT[name],
                )
            )
            self.assertEqual(linked, contract["body"], name)
            self.assertEqual(
                self.digest(linked),
                contract["sha256"],
                name,
            )
            self.assertEqual(extraction["size"], len(linked))
            self.assertEqual(
                extraction["relocation_count"],
                len(IN_PLACE_RELOCATION_CONTRACT[name]),
            )

    @_APPLE_ONLY
    def test_production_configuration_report_and_component_are_exact(
        self,
    ) -> None:
        config = self.production_config
        report = self.production_report
        self.assertEqual(
            config["in_place_leaves"],
            PRODUCTION_IN_PLACE_RECORDS,
        )
        self.assertEqual(report["base"], config["base"])
        self.assertEqual(
            config["expected"],
            {
                "overlay_size": 123454,
                "overlay_sha256": (
                    "9e5004af49fb14a22e7e7ed7357e4c10"
                    "f87dc8da3a7fb4d7b97fcffcde804c43"
                ),
                "component_size": 3646850,
                "component_sha256": (
                    "8722e5565bf54dade66fb751155c11eb"
                    "d128d7a12853e3e4b8671c3c97807827"
                ),
            },
        )

        built_leaves = report["in_place_leaves"]
        self.assertEqual(
            [
                leaf["extraction"]["function"]
                for leaf in built_leaves
            ],
            list(STOCK),
        )
        relocation_type_ids = {
            "R_ARM_THM_CALL": 10,
            "R_ARM_THM_PC8": 11,
            "R_ARM_THM_JUMP24": 30,
        }
        for configured, built in zip(
            PRODUCTION_IN_PLACE_RECORDS,
            built_leaves,
        ):
            name = configured["function"]
            start = int(configured["runtime_address"])
            size = int(configured["stock"]["size"])
            expected_relocations = []
            literal_dependencies = []
            for relocation in configured["relocations"]:
                target = int(relocation["target_address"])
                runtime = start + int(relocation["offset"])
                expected_relocations.append(
                    {
                        **relocation,
                        "type_id": relocation_type_ids[
                            relocation["type"]
                        ],
                        "runtime_address": runtime,
                        "runtime_address_hex": f"0x{runtime:08X}",
                        "target_address_hex": f"0x{target:08X}",
                    }
                )
                if relocation["type"] == "R_ARM_THM_PC8":
                    literal_dependencies.append(
                        {
                            "runtime_address": target,
                            "runtime_address_hex": f"0x{target:08X}",
                            "expected_hex": relocation[
                                "target_expected_hex"
                            ],
                        }
                    )

            self.assertEqual(built["source"], PRODUCTION_SOURCE, name)
            self.assertEqual(
                built["toolchain"],
                PRODUCTION_TOOLCHAIN_REPORT,
                name,
            )
            self.assertEqual(built["stock"], configured["stock"], name)
            extraction = built["extraction"]
            self.assertEqual(
                {
                    key: extraction[key]
                    for key in (
                        "function",
                        "section",
                        "runtime_address",
                        "runtime_address_hex",
                        "size",
                        "sha256",
                        "alignment",
                        "relocation_count",
                        "relocations",
                    )
                },
                {
                    "function": name,
                    "section": f".text.{name}",
                    "runtime_address": start,
                    "runtime_address_hex": f"0x{start:08X}",
                    "size": size,
                    "sha256": configured["expected"]["sha256"],
                    "alignment": 2,
                    "relocation_count": len(expected_relocations),
                    "relocations": expected_relocations,
                },
                name,
            )
            self.assertEqual(
                built["placement"],
                {
                    "function": name,
                    "runtime_address": start,
                    "runtime_address_hex": f"0x{start:08X}",
                    "end_exclusive": start + size,
                    "end_exclusive_hex": f"0x{start + size:08X}",
                    "payload_offset": (
                        PACKAGE_PREAMBLE_SIZE
                        + start
                        - APPLICATION_BASE
                    ),
                    "size": size,
                    "stock_sha256": configured["stock"]["sha256"],
                    "replacement_sha256": configured[
                        "expected"
                    ]["sha256"],
                    "replacement_hex": STOCK[name]["body"].hex(),
                    "literal_dependencies": literal_dependencies,
                },
                name,
            )

        overlay = report["overlay"]
        component = report["component"]
        self.assertEqual(
            {
                "size": overlay["size"],
                "sha256": overlay["sha256"],
                "function_count": len(overlay["functions"]),
                "patch_site_count": len(overlay["patched_sites"]),
            },
            {
                "size": 123454,
                "sha256": (
                    "9e5004af49fb14a22e7e7ed7357e4c10"
                    "f87dc8da3a7fb4d7b97fcffcde804c43"
                ),
                "function_count": 615,
                "patch_site_count": 578,
            },
        )
        self.assertTrue(set(STOCK).isdisjoint(overlay["functions"]))
        self.assertEqual(
            self.digest(self.production_overlay),
            overlay["sha256"],
        )
        self.assertEqual(
            component,
            {
                "artifact": (
                    Path(self.production_output)
                    / "ota_s200_firmware_ota.bin"
                ).relative_to(ROOT).as_posix(),
                "size": 3646850,
                "sha256": (
                    "8722e5565bf54dade66fb751155c11eb"
                    "d128d7a12853e3e4b8671c3c97807827"
                ),
                "opaque_base_bytes": 3438528,
                "source_owned_bytes": 121900,
                "source_owned_in_place_bytes": 182,
                "generated_wrapper_bytes": 32,
                "generated_patch_site_bytes": 84654,
                "replaced_stock_function_bytes": 84836,
            },
        )
        self.assertEqual(
            self.digest(self.production_component),
            component["sha256"],
        )
        self.assertEqual(
            self.production_component[len(self.package):],
            self.production_overlay,
        )

        reconstructed = bytearray(self.package)
        for site in overlay["patched_sites"]:
            offset = (
                PACKAGE_PREAMBLE_SIZE
                + int(site["runtime_address"])
                - APPLICATION_BASE
            )
            replacement = bytes.fromhex(site["replacement_hex"])
            reconstructed[offset:offset + len(replacement)] = replacement
        for leaf in built_leaves:
            placement = leaf["placement"]
            offset = int(placement["payload_offset"])
            replacement = bytes.fromhex(placement["replacement_hex"])
            self.assertEqual(
                self.package[offset:offset + len(replacement)],
                replacement,
                placement["function"],
            )
            reconstructed[offset:offset + len(replacement)] = replacement
        reconstructed.extend(self.production_overlay)
        package_length_word = (
            struct.unpack_from("<I", self.package, 0)[0]
            & 0xFF00_0000
        ) | len(reconstructed)
        struct.pack_into("<I", reconstructed, 0, package_length_word)
        struct.pack_into(
            "<I",
            reconstructed,
            4,
            zlib.crc32(reconstructed[8:]) & 0xFFFF_FFFF,
        )
        self.assertEqual(bytes(reconstructed), self.production_component)

        prefix = self.production_component[:len(self.package)]
        actual_mutations = {
            index
            for index, (official, generated) in enumerate(
                zip(self.package, prefix)
            )
            if official != generated
        }
        expected_mutations = {
            index
            for index in range(8)
            if self.package[index] != prefix[index]
        }
        for site in overlay["patched_sites"]:
            offset = (
                PACKAGE_PREAMBLE_SIZE
                + int(site["runtime_address"])
                - APPLICATION_BASE
            )
            replacement = bytes.fromhex(site["replacement_hex"])
            expected_mutations.update(
                offset + index
                for index, (official, generated) in enumerate(
                    zip(
                        self.package[offset:offset + len(replacement)],
                        replacement,
                    )
                )
                if official != generated
            )
        self.assertEqual(actual_mutations, expected_mutations)
        self.assertEqual(len(actual_mutations), 79964)

        vector_start = PACKAGE_PREAMBLE_SIZE
        self.assertEqual(
            prefix[vector_start:vector_start + 0x100],
            self.package[vector_start:vector_start + 0x100],
        )
        self.assertEqual(
            struct.unpack_from("<I", prefix, vector_start + 11 * 4)[0],
            0x005F_A121,
        )
        self.assertEqual(
            struct.unpack_from("<I", prefix, vector_start + 14 * 4)[0],
            0x005F_A0C9,
        )
        pool_offset = (
            PACKAGE_PREAMBLE_SIZE
            + 0x005F_A132
            - APPLICATION_BASE
        )
        self.assertEqual(
            prefix[pool_offset:pool_offset + 10],
            self.package[pool_offset:pool_offset + 10],
        )
        self.assertEqual(
            prefix[pool_offset:pool_offset + 10],
            bytes.fromhex("0000204a072008ed00e0"),
        )


if __name__ == "__main__":
    unittest.main()
