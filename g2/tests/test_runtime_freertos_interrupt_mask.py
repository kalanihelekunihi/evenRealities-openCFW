from __future__ import annotations

import os

import hashlib
import json
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = (
    ROOT
    / "components"
    / "apollo_main"
    / "core_overlay"
    / "runtime_freertos_interrupt_mask.S"
)
CONFIG = (
    ROOT
    / "components"
    / "apollo_main"
    / "core_overlay"
    / "overlay.json"
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

APPLICATION_BASE = 0x0043_8000
PACKAGE_PREAMBLE_SIZE = 32
SET_START = 0x005F_A0A4
CLEAR_START = 0x005F_A0BA
PAIR_END = 0x005F_A0C8
PREDECESSOR_START = 0x005F_A08C
SUCCESSOR_END = 0x005F_A0E0

SOURCE_SHA256 = (
    "28f16b37970b5529fe63cf250365b955b"
    "0c65fe2a016efda1ba718ee3b768de5"
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

OFFICIAL_PACKAGE_SHA256 = (
    "36c5b0e499a68ac2493a497bdab9740fd"
    "3e7027730c26a9094eca47268a27863"
)
OFFICIAL_APPLICATION_SHA256 = (
    "19044a72bdfeb04c6b1b104d87da7b98"
    "e13cc18928528d84d999b6bcc0ba9701"
)
GENERATED_COMPONENT_SHA256 = (
    "5cef32ba7350e7f6476336fa6a087010"
            "e6143e3e692205215c271430aa110d22"
)
GENERATED_APPLICATION_SHA256 = (
    "4db039a4769b3b68943f5fb626408444b"
    "cf2a21cc46dffeb08dded08a1f72a73"
)

SET_BYTES = bytes.fromhex(
    "eff31180"
    "4ff03001"
    "81f31188"
    "bff34f8f"
    "bff36f8f"
    "7047"
)
CLEAR_BYTES = bytes.fromhex(
    "80f31188"
    "bff34f8f"
    "bff36f8f"
    "7047"
)
PAIR_BYTES = SET_BYTES + CLEAR_BYTES
SET_SHA256 = (
    "f6bd0708e653c8e8880e33e298f9dc8"
    "ede1305c9386ea4ca5ff554d4022dc323"
)
CLEAR_SHA256 = (
    "97532a7902b38e1551198dd647d0fcdc"
    "3a6f19315b6491058a813c7643e0028a"
)
PAIR_SHA256 = (
    "422a4cac7b1abe90c7c7b0c431e2d85e"
    "f4d733cffb2da3b2708311f183cce849"
)
PREDECESSOR_BYTES = bytes.fromhex(
    "2a480068006880f3088862b661b6bff34f8fbff36f8f02df"
)
PREDECESSOR_SHA256 = (
    "44ba0097fbbc1d0691837d5c51bee83e"
    "6b61509c9d89efffee9c202d930e6347"
)
SUCCESSOR_BYTES = bytes.fromhex(
    "eff309801ef0100f08bf20ed108aeff30b82734620e9fc0f"
)
SUCCESSOR_SHA256 = (
    "f9b30a74beaef07eceb4faf2136bdeeb"
    "d4ba261164db2d589e304b1e96dd4aa7"
)

OFFICIAL_TOPOLOGY = {
    "set": {
        "count": 181,
        "address_sha256": (
            "f0187e62c4c399694d4fdd8e64a2e238"
            "724f6fb0ec89a6520c3020156eb9c106"
        ),
        "encoding_sha256": (
            "02798afeb2822409c0b56eb5f9499415"
            "cacc2a7a565b5320e41a88491547f5d8"
        ),
    },
    "clear": {
        "count": 12,
        "address_sha256": (
            "5047082ba3888cae8330f9276620611cd"
            "f412c86fee71d1cd0ffc97447fd2746"
        ),
        "encoding_sha256": (
            "9ff37cdde2fa4a0eaf5426d785483828"
            "1cc22fb96e74f682e104b2e8c51716ec"
        ),
    },
}
GENERATED_TOPOLOGY = {
    "set": {
        "count": 120,
        "address_sha256": (
            "b753da41d7757b732ba560d893f88ff13"
            "1f5803434c6a2c10bfe4671a0b48ca3"
        ),
        "encoding_sha256": (
            "0f3b9114861d8027d3c3531119d38204"
            "295e166a1e2c52917a1417b05dc11148"
        ),
    },
    "clear": {
        "count": 9,
        "address_sha256": (
            "abc7d58fa8f53aa94904c3804253fdbd"
            "5e9d2ed1c6170d2aee7ee158c4271acc"
        ),
        "encoding_sha256": (
            "4e5e0641ca9e3011ec2eba1d13c166f1"
            "27ba0ea345ec0b7d5db9e291b9bebeb4"
        ),
    },
}

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


_APPLE_ONLY = unittest.skipUnless(
    (os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang") == "apple-clang",
    "byte-exact / toolchain-specific Apple-clang assertion; Linux byte "
    "reproduction is verified end-to-end by tests/test_toolchain_profiles.py",
)


class RuntimeFreeRTOSInterruptMaskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        sys.path.insert(0, str(ROOT / "tools"))
        import analyze_g2_freertos_assert_port_seam
        import apollo_overlay

        cls.seam = analyze_g2_freertos_assert_port_seam
        cls.apollo_overlay = apollo_overlay
        cls.config = json.loads(CONFIG.read_text(encoding="utf-8"))

        build_root = ROOT / "build"
        build_root.mkdir(exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="test-runtime-freertos-interrupt-mask-",
            dir=build_root,
        )
        temporary = Path(cls.temporary.name)
        cls.target_object = temporary / "runtime_freertos_interrupt_mask.o"
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

        cls.report = apollo_overlay.build(
            root=ROOT,
            config_path=CONFIG,
            output_dir=temporary / "component",
            clang=os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
        )
        cls.overlay = (
            ROOT / cls.report["overlay"]["artifact"]
        ).read_bytes()
        cls.generated_package = (
            ROOT / cls.report["component"]["artifact"]
        ).read_bytes()
        cls.official_package = OFFICIAL.read_bytes()
        cls.official = cls.official_package[PACKAGE_PREAMBLE_SIZE:]
        cls.generated = cls.generated_package[PACKAGE_PREAMBLE_SIZE:]
        cls.topologies = {
            "official": cls.scan_topology(cls.official),
            "generated": cls.scan_topology(cls.generated),
        }

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @staticmethod
    def span(image: bytes, start: int, end: int) -> bytes:
        return image[
            start - APPLICATION_BASE:
            end - APPLICATION_BASE
        ]

    @classmethod
    def section_bytes(cls, name: str) -> bytes:
        section = cls.section_by_name[name]
        start = int(section["offset"])
        return cls.object_data[start:start + int(section["size"])]

    @classmethod
    def scan_topology(cls, image: bytes) -> dict[str, object]:
        calls: dict[str, list[tuple[int, bytes]]] = {
            "set": [],
            "clear": [],
        }
        wide_jumps: list[tuple[int, int, bytes]] = []
        interior: list[tuple[int, int, bool, bytes]] = []
        narrow: list[tuple[int, int, int]] = []

        for offset in range(0, len(image) - 3, 2):
            address = APPLICATION_BASE + offset
            first, second = struct.unpack_from("<HH", image, offset)
            encoding = image[offset:offset + 4]
            for link in (True, False):
                target = cls.seam.thumb_wide_branch_target(
                    address,
                    first,
                    second,
                    link=link,
                )
                if target is None:
                    continue
                if link and target == SET_START:
                    calls["set"].append((address, encoding))
                elif link and target == CLEAR_START:
                    calls["clear"].append((address, encoding))
                elif not link and target in (SET_START, CLEAR_START):
                    wide_jumps.append((address, target, encoding))
                for start, end in (
                    (SET_START, CLEAR_START),
                    (CLEAR_START, PAIR_END),
                ):
                    if (
                        start < target < end
                        and not start <= address < end
                    ):
                        interior.append(
                            (address, target, link, encoding)
                        )

        for offset in range(0, len(image) - 1, 2):
            address = APPLICATION_BASE + offset
            halfword = struct.unpack_from("<H", image, offset)[0]
            for target in cls.seam.narrow_branch_targets(
                address,
                halfword,
            ):
                if (
                    SET_START <= target < PAIR_END
                    and not SET_START <= address < PAIR_END
                ):
                    narrow.append((address, target, halfword))

        stored: list[tuple[int, int]] = []
        targets = {
            address | thumb
            for address in range(SET_START, PAIR_END, 2)
            for thumb in (0, 1)
        }
        for offset in range(0, len(image) - 3):
            value = struct.unpack_from("<I", image, offset)[0]
            if value in targets:
                stored.append((APPLICATION_BASE + offset, value))

        result: dict[str, object] = {
            "wide_jumps": wide_jumps,
            "interior": interior,
            "narrow": narrow,
            "stored": stored,
        }
        for name, entries in calls.items():
            result[name] = {
                "count": len(entries),
                "address_sha256": hashlib.sha256(
                    b"".join(
                        struct.pack("<I", address)
                        for address, _encoding in entries
                    )
                ).hexdigest(),
                "encoding_sha256": hashlib.sha256(
                    b"".join(encoding for _address, encoding in entries)
                ).hexdigest(),
            }
        return result

    def test_source_upstream_and_snapshot_provenance_are_pinned(
        self,
    ) -> None:
        self.assertEqual(len(SOURCE.read_bytes()), 2443)
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            SOURCE_SHA256,
        )
        source = SOURCE.read_text(encoding="utf-8")
        for fragment in (
            "SPDX-License-Identifier: MIT",
            "Permission is hereby granted",
            "FreeRTOS Kernel V10.5.1",
            UPSTREAM_COMMIT,
            "portable/IAR/ARM_CM55_NTZ/non_secure/portasm.s",
            "configMAX_SYSCALL_INTERRUPT_PRIORITY = 0x30",
            '.section .text.ulSetInterruptMask, "ax", %progbits',
            '.section .text.vClearInterruptMask, "ax", %progbits',
        ):
            self.assertIn(fragment, source)

        self.assertEqual(len(UPSTREAM.read_bytes()), 11686)
        self.assertEqual(
            hashlib.sha256(UPSTREAM.read_bytes()).hexdigest(),
            UPSTREAM_SHA256,
        )
        upstream = UPSTREAM.read_text(encoding="utf-8")
        set_start = upstream.index("ulSetInterruptMask:")
        clear_start = upstream.index("vClearInterruptMask:", set_start)
        block_end = upstream.index("PendSV_Handler:", clear_start)
        block = upstream[set_start:block_end]
        for fragment in (
            "mrs r0, basepri",
            "mov r1, #configMAX_SYSCALL_INTERRUPT_PRIORITY",
            "msr basepri, r1",
            "msr basepri, r0",
            "dsb",
            "isb",
            "bx lr",
        ):
            self.assertIn(fragment, block)

        self.assertEqual(
            hashlib.sha256(PROVENANCE.read_bytes()).hexdigest(),
            PROVENANCE_SHA256,
        )
        provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        self.assertEqual(provenance["license"], "MIT")
        self.assertEqual(provenance["upstream"]["selected_tag"], "V10.5.1")
        self.assertEqual(
            provenance["upstream"]["selected_commit"],
            UPSTREAM_COMMIT,
        )
        self.assertEqual(
            provenance["upstream"]["selected_tree"],
            UPSTREAM_TREE,
        )
        boundary = provenance["g2_boundary"]
        self.assertIs(boundary["snapshot_selects_portable_variant"], False)
        self.assertEqual(
            boundary["g2_selected_portable_variant"],
            "portable/IAR/ARM_CM55_NTZ/non_secure",
        )
        self.assertIn(
            "unequivocally selects",
            boundary["g2_port_selection_status"],
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

    def test_target_object_has_two_dedicated_aligned_exact_sections(
        self,
    ) -> None:
        self.assertEqual(
            {
                name: {
                    key: int(self.section_by_name[name][key])
                    for key in ("type", "flags", "size", "alignment")
                }
                for name in (
                    ".text.ulSetInterruptMask",
                    ".text.vClearInterruptMask",
                )
            },
            {
                ".text.ulSetInterruptMask": {
                    "type": 1,
                    "flags": 6,
                    "size": 22,
                    "alignment": 2,
                },
                ".text.vClearInterruptMask": {
                    "type": 1,
                    "flags": 6,
                    "size": 14,
                    "alignment": 2,
                },
            },
        )
        self.assertEqual(int(self.section_by_name[".text"]["size"]), 0)
        set_body = self.section_bytes(".text.ulSetInterruptMask")
        clear_body = self.section_bytes(".text.vClearInterruptMask")
        self.assertEqual(set_body, SET_BYTES)
        self.assertEqual(clear_body, CLEAR_BYTES)
        self.assertEqual(hashlib.sha256(set_body).hexdigest(), SET_SHA256)
        self.assertEqual(
            hashlib.sha256(clear_body).hexdigest(),
            CLEAR_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(set_body + clear_body).hexdigest(),
            PAIR_SHA256,
        )

        function_symbols = {
            str(symbol["name"]): {
                "value": int(symbol["value"]),
                "size": int(symbol["size"]),
                "binding": int(symbol["binding"]),
                "type": int(symbol["type"]),
                "section": str(
                    self.sections[int(symbol["section_index"])]["name"]
                ),
            }
            for symbol in self.symbols
            if int(symbol["type"]) == 2
        }
        self.assertEqual(
            function_symbols,
            {
                "ulSetInterruptMask": {
                    "value": 1,
                    "size": 22,
                    "binding": 1,
                    "type": 2,
                    "section": ".text.ulSetInterruptMask",
                },
                "vClearInterruptMask": {
                    "value": 1,
                    "size": 14,
                    "binding": 1,
                    "type": 2,
                    "section": ".text.vClearInterruptMask",
                },
            },
        )

    def test_target_sections_have_zero_relocations_and_undefined_symbols(
        self,
    ) -> None:
        target_indices = {
            int(self.section_by_name[name]["index"])
            for name in (
                ".text.ulSetInterruptMask",
                ".text.vClearInterruptMask",
            )
        }
        relocations = [
            str(section["name"])
            for section in self.sections
            if (
                int(section["type"]) == 9
                and int(section["info"]) in target_indices
            )
        ]
        self.assertEqual(relocations, [])
        self.assertEqual(
            [
                str(symbol["name"])
                for symbol in self.symbols
                if (
                    symbol["name"]
                    and int(symbol["section_index"]) == 0
                )
            ],
            [],
        )
        self.assertEqual(
            {
                str(symbol["name"])
                for symbol in self.symbols
                if (
                    int(symbol["type"]) == 2
                    and int(symbol["section_index"]) != 0
                )
            },
            {"ulSetInterruptMask", "vClearInterruptMask"},
        )

    @_APPLE_ONLY
    def test_official_and_generated_in_place_boundaries_are_exact(
        self,
    ) -> None:
        self.assertEqual(len(self.official_package), 3_523_396)
        self.assertEqual(
            hashlib.sha256(self.official_package).hexdigest(),
            OFFICIAL_PACKAGE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.official).hexdigest(),
            OFFICIAL_APPLICATION_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.generated_package).hexdigest(),
            GENERATED_COMPONENT_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.generated).hexdigest(),
            GENERATED_APPLICATION_SHA256,
        )

        for name, image in (
            ("official", self.official),
            ("generated", self.generated),
        ):
            with self.subTest(image=name):
                predecessor = self.span(
                    image,
                    PREDECESSOR_START,
                    SET_START,
                )
                pair = self.span(image, SET_START, PAIR_END)
                successor = self.span(image, PAIR_END, SUCCESSOR_END)
                self.assertEqual(predecessor, PREDECESSOR_BYTES)
                self.assertEqual(pair, PAIR_BYTES)
                self.assertEqual(successor, SUCCESSOR_BYTES)
                self.assertEqual(
                    hashlib.sha256(predecessor).hexdigest(),
                    PREDECESSOR_SHA256,
                )
                self.assertEqual(
                    hashlib.sha256(pair).hexdigest(),
                    PAIR_SHA256,
                )
                self.assertEqual(
                    hashlib.sha256(successor).hexdigest(),
                    SUCCESSOR_SHA256,
                )
                self.assertEqual(pair[:CLEAR_START - SET_START], SET_BYTES)
                self.assertEqual(pair[CLEAR_START - SET_START:], CLEAR_BYTES)

    def test_official_direct_call_and_reference_topology_is_exact(
        self,
    ) -> None:
        topology = self.topologies["official"]
        self.assertEqual(topology["set"], OFFICIAL_TOPOLOGY["set"])
        self.assertEqual(topology["clear"], OFFICIAL_TOPOLOGY["clear"])
        self.assertEqual(topology["wide_jumps"], [])
        self.assertEqual(topology["interior"], [])
        self.assertEqual(topology["narrow"], [])
        self.assertEqual(
            topology["stored"],
            [(0x0062_FCDF, CLEAR_START)],
        )
        self.assertNotEqual(0x0062_FCDF & 0x3, 0)

    def test_generated_direct_call_and_reference_topology_is_exact(
        self,
    ) -> None:
        topology = self.topologies["generated"]
        self.assertEqual(topology["set"], GENERATED_TOPOLOGY["set"])
        self.assertEqual(topology["clear"], GENERATED_TOPOLOGY["clear"])
        self.assertEqual(topology["wide_jumps"], [])
        self.assertEqual(topology["interior"], [])
        self.assertEqual(topology["narrow"], [])
        self.assertEqual(
            topology["stored"],
            [(0x0062_FCDF, CLEAR_START)],
        )

    def test_production_config_pins_isolated_leaves_and_copy_sites(
        self,
    ) -> None:
        leaves = {
            leaf["function"]: leaf
            for leaf in self.config["isolated_leaves"]
            if leaf["function"] in (
                "ulSetInterruptMask",
                "vClearInterruptMask",
            )
        }
        self.assertEqual(set(leaves), {
            "ulSetInterruptMask",
            "vClearInterruptMask",
        })
        expected_source = {
            "path": (
                "components/apollo_main/core_overlay/"
                "runtime_freertos_interrupt_mask.S"
            ),
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
            "evidence": (
                "docs/research/"
                "freertos-assert-port-seam-source-boundary-audit.md"
            ),
        }
        for name, size, digest in (
            ("ulSetInterruptMask", 22, SET_SHA256),
            ("vClearInterruptMask", 14, CLEAR_SHA256),
        ):
            leaf = leaves[name]
            self.assertEqual(leaf["source"], expected_source)
            self.assertEqual(leaf["toolchain"], {
                "target": "arm-none-eabi",
                "reviewed_version_prefix": "Apple clang version 21.0.0",
                "flags": TARGET_FLAGS[1:],
            })
            self.assertEqual(
                leaf["expected"],
                {"size": size, "sha256": digest},
            )
            self.assertIn(name, self.config["functions"])

        sites = {
            site["name"]: site
            for site in self.config["patch_sites"]
            if "interrupt_mask" in site["name"]
        }
        self.assertEqual(
            sites,
            {
                "replace_freertos_ul_set_interrupt_mask": {
                    "name": "replace_freertos_ul_set_interrupt_mask",
                    "runtime_address": SET_START,
                    "expected_size": 22,
                    "expected_sha256": SET_SHA256,
                    "branch": "copy",
                    "target_function": "ulSetInterruptMask",
                },
                "replace_freertos_v_clear_interrupt_mask": {
                    "name": "replace_freertos_v_clear_interrupt_mask",
                    "runtime_address": CLEAR_START,
                    "expected_size": 14,
                    "expected_sha256": CLEAR_SHA256,
                    "branch": "copy",
                    "target_function": "vClearInterruptMask",
                },
            },
        )
        self.assertEqual(
            self.config["expected"],
            {
                "overlay_size": 142578,
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

    @_APPLE_ONLY
    def test_production_report_pins_leaf_extraction_placement_and_copy(
        self,
    ) -> None:
        leaves = {
            leaf["extraction"]["function"]: leaf
            for leaf in self.report["isolated_leaves"]
            if leaf["extraction"]["function"] in (
                "ulSetInterruptMask",
                "vClearInterruptMask",
            )
        }
        self.assertEqual(set(leaves), {
            "ulSetInterruptMask",
            "vClearInterruptMask",
        })
        expected_placements = {
            "ulSetInterruptMask": {
                "alignment": 2,
                "offset": 113636,
                "padding_before": 0,
                "size": 22,
            },
            "vClearInterruptMask": {
                "alignment": 2,
                "offset": 113658,
                "padding_before": 0,
                "size": 14,
            },
        }
        configured_sources = {
            leaf["function"]: leaf["source"]
            for leaf in self.config["isolated_leaves"]
        }
        for name, size, digest, other_size in (
            ("ulSetInterruptMask", 22, SET_SHA256, 14),
            ("vClearInterruptMask", 14, CLEAR_SHA256, 22),
        ):
            leaf = leaves[name]
            self.assertEqual(
                {
                    key: leaf["extraction"][key]
                    for key in (
                        "alignment",
                        "discarded_alloc_section_bytes",
                        "discarded_alloc_section_count",
                        "function",
                        "relocation_count",
                        "section",
                        "sha256",
                        "size",
                    )
                },
                {
                    "alignment": 2,
                    "discarded_alloc_section_bytes": other_size,
                    "discarded_alloc_section_count": 1,
                    "function": name,
                    "relocation_count": 0,
                    "section": f".text.{name}",
                    "sha256": digest,
                    "size": size,
                },
            )
            self.assertEqual(leaf["placement"], expected_placements[name])
            self.assertEqual(
                leaf["source"],
                {
                    **configured_sources[name],
                    "size": 2443,
                },
            )
            function = self.report["overlay"]["functions"][name]
            self.assertEqual(
                function,
                {
                    "offset": expected_placements[name]["offset"],
                    "size": size,
                },
            )
            body = self.overlay[
                function["offset"]:function["offset"] + function["size"]
            ]
            self.assertEqual(hashlib.sha256(body).hexdigest(), digest)

        sites = {
            site["name"]: site
            for site in self.report["overlay"]["patched_sites"]
            if "interrupt_mask" in site["name"]
        }
        for name, address, size, digest, function, body in (
            (
                "replace_freertos_ul_set_interrupt_mask",
                SET_START,
                22,
                SET_SHA256,
                "ulSetInterruptMask",
                SET_BYTES,
            ),
            (
                "replace_freertos_v_clear_interrupt_mask",
                CLEAR_START,
                14,
                CLEAR_SHA256,
                "vClearInterruptMask",
                CLEAR_BYTES,
            ),
        ):
            site = sites[name]
            self.assertEqual(site["branch"], "copy")
            self.assertEqual(site["runtime_address"], address)
            self.assertEqual(site["target_address"], address)
            self.assertEqual(site["payload_offset"], 32 + address - APPLICATION_BASE)
            self.assertEqual(site["expected_size"], size)
            self.assertEqual(site["expected_sha256"], digest)
            self.assertEqual(site["target_function"], function)
            self.assertEqual(site["replacement_hex"], body.hex())

        self.assertEqual(
            self.report["component"]["sha256"],
            GENERATED_COMPONENT_SHA256,
        )
        self.assertEqual(self.report["component"]["size"], 3_665_974)
        self.assertEqual(self.report["overlay"]["size"], 142_578)
        self.assertEqual(
            self.report["overlay"]["sha256"],
            self.config["expected"]["overlay_sha256"],
        )


if __name__ == "__main__":
    unittest.main()
