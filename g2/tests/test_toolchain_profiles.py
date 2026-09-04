"""Tests for the dual-toolchain reproducible-build profile mechanism.

These cover the additive toolchain-profile layer that lets openCFW build and
verify its compiled overlays under a non-Apple reviewed toolchain (for example
a Linux Homebrew clang) with its own independently recorded, fail-closed pins,
while the canonical `apple-clang` reference path stays byte-for-byte
unchanged.

The unit tests run everywhere.  The integration tests only run on a host whose
available clang resolves to a *recorded* alternate profile (today the Linux
`linux-clang` profile); they skip otherwise so macOS reviewers are unaffected.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(OPENCFW_ROOT / "tools"))

import apollo_overlay  # noqa: E402
import detect_toolchain  # noqa: E402
import open_cfw  # noqa: E402


RING_CONFIG = OPENCFW_ROOT / "components/apollo_main/ring_gesture/overlay.json"
RING_MANIFEST = OPENCFW_ROOT / "manifests/g2-2.2.6.10-ring-source.json"
CORE_CONFIG = OPENCFW_ROOT / "components/apollo_main/core_overlay/overlay.json"
BOOT_CONFIG = OPENCFW_ROOT / "components/bootloader/core_overlay/overlay.json"
CORE_MANIFEST = OPENCFW_ROOT / "manifests/g2-2.2.6.10-core-source.json"
CORE_COMPONENT_BUILD = (
    OPENCFW_ROOT / "components/apollo_main/core_overlay/build"
)
BOOT_COMPONENT_BUILD = (
    OPENCFW_ROOT / "components/bootloader/core_overlay/build"
)


def _ring_config() -> dict:
    return json.loads(RING_CONFIG.read_text(encoding="utf-8"))


def _core_config() -> dict:
    return json.loads(CORE_CONFIG.read_text(encoding="utf-8"))


def _available_clang() -> str | None:
    for candidate in (
        os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
        "/home/linuxbrew/.linuxbrew/opt/llvm/bin/clang",
        shutil.which("clang") or "",
    ):
        if candidate and Path(candidate).exists():
            return candidate
    return None


def _resolved_profile(clang: str) -> str | None:
    try:
        return detect_toolchain.detect(clang, RING_CONFIG)
    except SystemExit:
        return None


class _RepoLocalTemp:
    """Temp dir under openCFW/build (the tools reject dirs outside the root)."""

    def __enter__(self) -> Path:
        base = OPENCFW_ROOT / "build"
        base.mkdir(parents=True, exist_ok=True)
        self._path = Path(tempfile.mkdtemp(dir=base, prefix="_test-profile-"))
        return self._path

    def __exit__(self, *exc: object) -> None:
        shutil.rmtree(self._path, ignore_errors=True)


class ResolveToolchainProfileTests(unittest.TestCase):
    def test_canonical_profile_returns_base_blocks_unchanged(self) -> None:
        config = _ring_config()
        toolchain, expected, resolved = (
            apollo_overlay.resolve_toolchain_profile(config, None)
        )
        self.assertEqual(resolved, "apple-clang")
        # The canonical path must hand back the config's own objects so the
        # reviewed Apple reference is never perturbed.
        self.assertIs(toolchain, config["toolchain"])
        self.assertIs(expected, config["expected"])
        self.assertEqual(
            toolchain["reviewed_version_prefix"], "Apple clang version 21.0.0"
        )

    def test_named_profile_overrides_prefix_and_expected(self) -> None:
        config = _ring_config()
        toolchain, expected, resolved = (
            apollo_overlay.resolve_toolchain_profile(config, "linux-clang")
        )
        self.assertEqual(resolved, "linux-clang")
        profile = config["toolchain_profiles"]["linux-clang"]
        self.assertEqual(
            toolchain["reviewed_version_prefix"],
            profile["reviewed_version_prefix"],
        )
        self.assertEqual(expected, profile["expected"])
        # Inherited base flags/target remain in force unless overridden.
        self.assertEqual(toolchain["flags"], config["toolchain"]["flags"])
        self.assertEqual(toolchain["target"], config["toolchain"]["target"])

    def test_unknown_profile_fails_closed(self) -> None:
        config = _ring_config()
        with self.assertRaisesRegex(apollo_overlay.BuildError, "unknown toolchain"):
            apollo_overlay.resolve_toolchain_profile(config, "no-such-profile")

    def test_record_mode_drops_version_gate_and_expected(self) -> None:
        config = _ring_config()
        toolchain, expected, resolved = (
            apollo_overlay.resolve_toolchain_profile(
                config, "linux-clang", record=True
            )
        )
        self.assertEqual(resolved, "linux-clang")
        self.assertNotIn("reviewed_version", toolchain)
        self.assertNotIn("reviewed_version_prefix", toolchain)
        self.assertEqual(expected, {})

    def test_cannot_record_canonical_profile(self) -> None:
        config = _ring_config()
        with self.assertRaisesRegex(apollo_overlay.BuildError, "canonical"):
            apollo_overlay.resolve_toolchain_profile(
                config, "apple-clang", record=True
            )

    def test_profile_may_pin_exact_version_dropping_inherited_prefix(self) -> None:
        config = _ring_config()
        config["toolchain_profiles"]["exact"] = {
            "reviewed_version": "Some clang 1.2.3",
            "expected": {},
        }
        toolchain, _expected, _resolved = (
            apollo_overlay.resolve_toolchain_profile(config, "exact")
        )
        self.assertEqual(toolchain["reviewed_version"], "Some clang 1.2.3")
        self.assertNotIn("reviewed_version_prefix", toolchain)

    def test_reviewed_source_root_is_inherited_and_profile_overridable(self) -> None:
        config = _core_config()
        config["toolchain_profiles"]["inherits-source-root"] = {
            "reviewed_version_prefix": "Some clang version",
            "expected": {},
        }

        inherited, _expected, _resolved = (
            apollo_overlay.resolve_toolchain_profile(
                config, "inherits-source-root"
            )
        )
        overridden, _expected, _resolved = (
            apollo_overlay.resolve_toolchain_profile(config, "linux-clang")
        )

        self.assertEqual(
            inherited["reviewed_source_root"],
            "/Users/kalani/Repo/SybilSight/openCFW",
        )
        self.assertEqual(
            overridden["reviewed_source_root"],
            "/Users/kalani/Repo/SybilSightABCD/openCFW",
        )


class CompilerSourcePrefixFlagsTests(unittest.TestCase):
    def test_rejects_non_list_flags(self) -> None:
        with self.assertRaisesRegex(
            apollo_overlay.BuildError,
            r"^toolchain\.flags must be a list$",
        ):
            apollo_overlay.compiler_source_prefix_flags(
                Path("/actual/worktree/openCFW"),
                {"flags": "-O2"},
            )

    def test_rejects_non_string_or_empty_flags(self) -> None:
        for flags in ([42], [""]):
            with self.subTest(flags=flags), self.assertRaisesRegex(
                apollo_overlay.BuildError,
                r"^toolchain\.flags entries must be nonempty strings$",
            ):
                apollo_overlay.compiler_source_prefix_flags(
                    Path("/actual/worktree/openCFW"),
                    {"flags": flags},
                )

    def test_rejects_response_file_flags(self) -> None:
        for helper in (
            apollo_overlay.compiler_source_prefix_flags,
            apollo_overlay.compiler_source_prefix_report_flags,
        ):
            with self.subTest(helper=helper.__name__), self.assertRaisesRegex(
                apollo_overlay.BuildError,
                r"^toolchain\.flags cannot use response files$",
            ):
                helper(
                    Path("/actual/worktree/openCFW"),
                    {"flags": ["@compiler-flags.rsp"]},
                )

    def test_maps_actual_source_root_to_reviewed_source_root(self) -> None:
        toolchain = {
            "reviewed_source_root": "/reviewed/openCFW",
            "flags": [],
        }
        for actual_root in (
            Path("/actual/worktree-a/openCFW"),
            Path("/different/worktree-b/openCFW"),
        ):
            with self.subTest(actual_root=actual_root):
                self.assertEqual(
                    apollo_overlay.compiler_source_prefix_flags(
                        actual_root,
                        toolchain,
                    ),
                    [
                        f"-ffile-prefix-map={actual_root.resolve()}="
                        "/reviewed/openCFW"
                    ],
                )
                self.assertEqual(
                    apollo_overlay.compiler_source_prefix_report_flags(
                        actual_root,
                        toolchain,
                    ),
                    [
                        "-ffile-prefix-map=/reviewed/openCFW="
                        "/reviewed/openCFW"
                    ],
                )

    def test_report_view_is_root_independent_and_discloses_no_active_path(
        self,
    ) -> None:
        toolchain = {
            "reviewed_source_root": "/reviewed/openCFW",
            "flags": ["-O2"],
        }
        roots = (
            Path("/private/tmp/build-a/openCFW"),
            Path("/workspace/build-b/openCFW"),
        )
        reports = [
            apollo_overlay.compiler_source_prefix_report_flags(root, toolchain)
            for root in roots
        ]
        self.assertEqual(reports[0], reports[1])
        encoded = json.dumps(reports, sort_keys=True)
        for root in roots:
            self.assertNotIn(str(root.resolve()), encoded)

    def test_omits_map_when_root_is_equal_or_unreviewed(self) -> None:
        self.assertEqual(
            apollo_overlay.compiler_source_prefix_flags(
                Path("/reviewed/openCFW"),
                {"reviewed_source_root": "/reviewed/openCFW", "flags": []},
            ),
            [],
        )
        self.assertEqual(
            apollo_overlay.compiler_source_prefix_flags(
                Path("/actual/worktree/openCFW"), {"flags": []}
            ),
            [],
        )

    def test_rejects_non_absolute_reviewed_source_root(self) -> None:
        with self.assertRaisesRegex(
            apollo_overlay.BuildError,
            "reviewed_source_root must be an absolute path",
        ):
            apollo_overlay.compiler_source_prefix_flags(
                Path("/actual/worktree/openCFW"),
                {"reviewed_source_root": "reviewed/openCFW", "flags": []},
            )

    def test_rejects_non_string_reviewed_source_root(self) -> None:
        with self.assertRaisesRegex(
            apollo_overlay.BuildError,
            "reviewed_source_root must be an absolute path string",
        ):
            apollo_overlay.compiler_source_prefix_flags(
                Path("/actual/worktree/openCFW"),
                {"reviewed_source_root": Path("/reviewed/openCFW"), "flags": []},
            )

    def test_rejects_hand_authored_file_prefix_map(self) -> None:
        for helper in (
            apollo_overlay.compiler_source_prefix_flags,
            apollo_overlay.compiler_source_prefix_report_flags,
        ):
            for flags in (
                ["-ffile-prefix-map=/somewhere=/reviewed/openCFW"],
                ["-ffile-prefix-map", "/somewhere=/reviewed/openCFW"],
            ):
                with (
                    self.subTest(helper=helper.__name__, flags=flags),
                    self.assertRaisesRegex(
                        apollo_overlay.BuildError,
                        "toolchain.flags cannot set -ffile-prefix-map",
                    ),
                ):
                    helper(
                        Path("/actual/worktree/openCFW"),
                        {
                            "reviewed_source_root": "/reviewed/openCFW",
                            "flags": flags,
                        },
                    )


class ResolveLeafProfileRecordTests(unittest.TestCase):
    @staticmethod
    def _canonical_leaf() -> dict:
        return {
            "function": "existing_leaf",
            "toolchain": {
                "reviewed_version_prefix": "Apple clang version 21.0.0",
                "target": "canonical-target",
                "flags": ["canonical-flag"],
                "include_dirs": ["canonical/include"],
            },
            "expected": {
                "size": 40,
                "sha256": "1" * 64,
                "alignment": 4,
                "offset": 100,
                "unrelocated_sha256": "2" * 64,
                "closure_size": 56,
                "closure_sha256": "3" * 64,
                "rodata_offset": 40,
            },
            "stock": {"size": 40, "sha256": "9" * 64},
            "relocations": [
                {
                    "offset": 2,
                    "type": "R_ARM_THM_CALL",
                    "symbol": "canonical_target",
                    "target_address": 0x1000,
                }
            ],
            "closure": {
                "text_section": ".text.canonical",
                "preserved_key": "canonical-value",
                "rodata": {
                    "section": ".rodata.canonical",
                    "size": 16,
                    "sha256": "4" * 64,
                    "alignment": 4,
                    "symbols": [],
                },
            },
            "toolchain_profiles": {
                "linux-clang": {
                    "reviewed_version_prefix": "Homebrew clang version 22.1.8",
                    "target": "profile-target",
                    "flags": ["profile-flag"],
                    "include_dirs": ["profile/include"],
                    "expected": {
                        "size": 60,
                        "sha256": "5" * 64,
                        "alignment": 8,
                        "offset": 120,
                        "unrelocated_sha256": "6" * 64,
                        "closure_size": 80,
                        "closure_sha256": "7" * 64,
                        "rodata_offset": 64,
                    },
                    "stock": {"size": 60, "sha256": "a" * 64},
                    "relocations": [
                        {
                            "offset": 10,
                            "type": "R_ARM_THM_CALL",
                            "symbol": "profile_target",
                            "target_address": 0x2000,
                        }
                    ],
                    "closure": {
                        "text_section": ".text.profile",
                        "rodata": {
                            "section": ".rodata.profile",
                            "size": 16,
                            "sha256": "8" * 64,
                            "alignment": 8,
                            "symbols": [],
                        },
                    },
                }
            },
        }

    def test_record_reuses_existing_profile_structure_and_toolchain(self) -> None:
        leaf = self._canonical_leaf()
        profile = leaf["toolchain_profiles"]["linux-clang"]

        effective = apollo_overlay.resolve_leaf_profile(
            leaf,
            "linux-clang",
            record=True,
        )

        self.assertIs(effective["expected"], profile["expected"])
        self.assertIs(effective["stock"], profile["stock"])
        self.assertIs(effective["relocations"], profile["relocations"])
        self.assertEqual(effective["closure"]["text_section"], ".text.profile")
        self.assertEqual(
            effective["closure"]["rodata"],
            profile["closure"]["rodata"],
        )
        self.assertEqual(
            effective["closure"]["preserved_key"],
            "canonical-value",
        )
        self.assertEqual(effective["toolchain"]["target"], "profile-target")
        self.assertEqual(effective["toolchain"]["flags"], ["profile-flag"])
        self.assertEqual(
            effective["toolchain"]["include_dirs"],
            ["profile/include"],
        )
        self.assertNotIn("reviewed_version", effective["toolchain"])
        self.assertNotIn("reviewed_version_prefix", effective["toolchain"])

        selected_expected = dict(profile["expected"])
        selected_relocations = json.loads(json.dumps(profile["relocations"]))
        selected_closure = json.loads(json.dumps(profile["closure"]))
        report = {
            "relocated_leaves": [
                {
                    "extraction": {
                        "function": "existing_leaf",
                        "section": ".text.profile",
                    },
                    "pins": {
                        **selected_expected,
                        "rodata": {
                            **selected_closure["rodata"],
                            "offset": selected_expected["rodata_offset"],
                        },
                        "relocations": [
                            {
                                **selected_relocations[0],
                            }
                        ],
                    },
                }
            ]
        }
        data = {"relocated_leaves": [leaf]}
        apollo_overlay.record_leaf_profile_pins(
            data,
            "linux-clang",
            "Homebrew clang version 22.1.9",
            report,
        )
        recorded = leaf["toolchain_profiles"]["linux-clang"]
        self.assertEqual(recorded["expected"], selected_expected)
        self.assertEqual(recorded["relocations"], selected_relocations)
        self.assertEqual(recorded["closure"], selected_closure)
        self.assertEqual(recorded["target"], "profile-target")
        self.assertEqual(recorded["flags"], ["profile-flag"])
        self.assertEqual(recorded["include_dirs"], ["profile/include"])
        self.assertEqual(
            recorded["reviewed_version_prefix"],
            "Homebrew clang version 22.1.9",
        )

    def test_leaf_profile_rejects_unknown_fields_and_dual_version_pins(
        self,
    ) -> None:
        leaf = self._canonical_leaf()
        leaf["toolchain_profiles"]["linux-clang"]["unexpected"] = True
        with self.assertRaisesRegex(apollo_overlay.BuildError, "unknown fields"):
            apollo_overlay.resolve_leaf_profile(leaf, "linux-clang")

        leaf = self._canonical_leaf()
        leaf["toolchain_profiles"]["linux-clang"]["reviewed_version"] = (
            "Homebrew clang version 22.1.8"
        )
        with self.assertRaisesRegex(
            apollo_overlay.BuildError,
            "cannot set both reviewed_version and reviewed_version_prefix",
        ):
            apollo_overlay.resolve_leaf_profile(
                leaf,
                "linux-clang",
                record=True,
            )

    def test_new_leaf_uses_canonical_structure_and_is_recorded(self) -> None:
        leaf = {
            "function": "new_leaf",
            "toolchain": {
                "reviewed_version_prefix": "Apple clang version 21.0.0",
                "target": "arm-none-eabi",
                "flags": ["-ffunction-sections", "-fdata-sections"],
            },
            "expected": {
                "size": 4,
                "sha256": "a" * 64,
                "alignment": 2,
                "offset": 20,
                "unrelocated_sha256": "b" * 64,
            },
            "relocations": [],
            # Another profile may already exist even though the requested one
            # has not yet been recorded for this newly added leaf.
            "toolchain_profiles": {"other-clang": {}},
        }
        effective = apollo_overlay.resolve_leaf_profile(
            leaf,
            "linux-clang",
            record=True,
        )
        self.assertIs(effective["expected"], leaf["expected"])
        self.assertIs(effective["relocations"], leaf["relocations"])
        self.assertEqual(effective["toolchain"]["target"], "arm-none-eabi")
        self.assertNotIn("reviewed_version_prefix", effective["toolchain"])

        data = {"relocated_leaves": [leaf]}
        report = {
            "relocated_leaves": [
                {
                    "extraction": {"function": "new_leaf"},
                    "pins": {
                        "size": 6,
                        "sha256": "c" * 64,
                        "alignment": 4,
                        "offset": 24,
                        "unrelocated_sha256": "d" * 64,
                        "relocations": [
                            {
                                "offset": 2,
                                "type": "R_ARM_THM_CALL",
                                "symbol": "new_target",
                                "target_function": "new_target",
                            }
                        ],
                    },
                }
            ]
        }
        apollo_overlay.record_leaf_profile_pins(
            data,
            "linux-clang",
            "Homebrew clang version 22.1.8",
            report,
        )
        recorded = data["relocated_leaves"][0]["toolchain_profiles"][
            "linux-clang"
        ]
        self.assertEqual(
            recorded["reviewed_version_prefix"],
            "Homebrew clang version 22.1.8",
        )
        self.assertEqual(recorded["expected"]["offset"], 24)
        self.assertEqual(recorded["expected"]["alignment"], 4)
        self.assertEqual(
            recorded["relocations"],
            [
                {
                    "offset": 2,
                    "type": "R_ARM_THM_CALL",
                    "symbol": "new_target",
                    "target_function": "new_target",
                }
            ],
        )
        self.assertIn("other-clang", leaf["toolchain_profiles"])

    def test_in_place_record_preserves_profile_relocation_offsets(self) -> None:
        leaf = {
            "function": "in_place_leaf",
            "expected": {
                "size": 8,
                "sha256": "a" * 64,
                "unrelocated_sha256": "b" * 64,
            },
            "relocations": [
                {
                    "offset": 2,
                    "type": "R_ARM_THM_CALL",
                    "symbol": "target",
                    "symbol_type": "STT_FUNC",
                    "target_address": 0x00420000,
                }
            ],
        }
        report = {
            "in_place_leaves": [
                {
                    "extraction": {
                        "function": "in_place_leaf",
                        "unrelocated_sha256": "d" * 64,
                        "relocations": [
                            {
                                "offset": 4,
                                "type": "R_ARM_THM_CALL",
                                "symbol": "target",
                                "symbol_type": "STT_FUNC",
                                "target_address": 0x00420000,
                            }
                        ],
                    },
                    "pins": {"size": 8, "sha256": "c" * 64},
                }
            ]
        }
        data = {"in_place_leaves": [leaf]}
        apollo_overlay.record_leaf_profile_pins(
            data,
            "linux-clang",
            "Homebrew clang version 22.1.8",
            report,
        )
        recorded = leaf["toolchain_profiles"]["linux-clang"]
        self.assertEqual(
            recorded["expected"],
            {
                "size": 8,
                "sha256": "c" * 64,
                "unrelocated_sha256": "d" * 64,
            },
        )
        self.assertEqual(recorded["relocations"][0]["offset"], 4)
        self.assertEqual(
            recorded["relocations"][0]["target_address"],
            0x00420000,
        )

    def test_in_place_record_preserves_pc8_literal_expectation(self) -> None:
        leaf = {
            "function": "pc8_leaf",
            "expected": {
                "size": 4,
                "sha256": "a" * 64,
                "unrelocated_sha256": "b" * 64,
            },
            "relocations": [{
                "offset": 0,
                "type": "R_ARM_THM_PC8",
                "symbol": "literal",
                "target_address": 0x00420000,
                "target_expected_hex": "78563412",
            }],
        }
        report = {
            "in_place_leaves": [{
                "extraction": {
                    "function": "pc8_leaf",
                    "unrelocated_sha256": "d" * 64,
                    "relocations": [{
                        "offset": 0,
                        "type": "R_ARM_THM_PC8",
                        "symbol": "literal",
                        "target_address": 0x00420000,
                    }],
                },
                "pins": {"size": 4, "sha256": "c" * 64},
            }]
        }
        data = {"in_place_leaves": [leaf]}
        apollo_overlay.record_leaf_profile_pins(
            data,
            "linux-clang",
            "Homebrew clang version 22.1.8",
            report,
        )
        relocation = leaf["toolchain_profiles"]["linux-clang"][
            "relocations"
        ][0]
        self.assertEqual(relocation["target_expected_hex"], "78563412")

    def test_record_preserves_external_prel_target_and_repairs_local_closure_target(
        self,
    ) -> None:
        external = {
            "function": "external_prel_leaf",
            "toolchain": {
                "reviewed_version_prefix": "Apple clang version 21.0.0",
                "target": "arm-none-eabi",
                "flags": [],
            },
            "expected": {
                "size": 4,
                "sha256": "a" * 64,
                "alignment": 4,
                "offset": 0,
                "unrelocated_sha256": "b" * 64,
            },
            "relocations": [],
        }
        report = {
            "relocated_leaves": [
                {
                    "extraction": {"function": "external_prel_leaf"},
                    "pins": {
                        "size": 4,
                        "sha256": "c" * 64,
                        "alignment": 4,
                        "offset": 8,
                        "unrelocated_sha256": "d" * 64,
                        "relocations": [
                            {
                                "offset": 0,
                                "type": "R_ARM_THM_MOVW_PREL_NC",
                                "symbol": "retained_object",
                                "symbol_type": "STT_NOTYPE",
                                "target_address": 0x20000000,
                            }
                        ],
                    },
                }
            ]
        }
        data = {"relocated_leaves": [external]}
        apollo_overlay.record_leaf_profile_pins(
            data,
            "linux-clang",
            "Homebrew clang version 22.1.8",
            report,
        )
        recorded = external["toolchain_profiles"]["linux-clang"]
        self.assertEqual(
            recorded["relocations"][0]["target_address"],
            0x20000000,
        )

        closure = self._canonical_leaf()
        closure["closure"]["rodata"]["symbols"] = [
            {"name": "local_table", "offset": 0, "size": 4}
        ]
        closure["toolchain_profiles"]["linux-clang"]["closure"]["rodata"][
            "symbols"
        ] = [{"name": "local_table", "offset": 0, "size": 4}]
        closure["toolchain_profiles"]["linux-clang"]["relocations"] = [
            {
                "offset": 0,
                "type": "R_ARM_THM_MOVW_PREL_NC",
                "symbol": "local_table",
                "target_address": 0x12345678,
            }
        ]
        effective = apollo_overlay.resolve_leaf_profile(
            closure,
            "linux-clang",
            record=True,
        )
        self.assertNotIn("target_address", effective["relocations"][0])

    def test_record_rejects_malformed_profile_structure(self) -> None:
        cases = (
            (
                "profiles-not-object",
                {"toolchain_profiles": []},
                "toolchain_profiles must be an object",
            ),
            (
                "profile-not-object",
                {"toolchain_profiles": {"linux-clang": []}},
                "profile 'linux-clang' must be an object",
            ),
            (
                "expected-not-object",
                {
                    "toolchain_profiles": {
                        "linux-clang": {"expected": []}
                    }
                },
                "expected must be an object",
            ),
            (
                "relocations-not-list",
                {
                    "toolchain_profiles": {
                        "linux-clang": {"relocations": {}}
                    }
                },
                "relocations must be a list",
            ),
            (
                "closure-not-object",
                {
                    "toolchain_profiles": {
                        "linux-clang": {"closure": []}
                    }
                },
                "closure must be an object",
            ),
        )
        for name, override, message in cases:
            with self.subTest(name=name):
                leaf = {
                    "function": "malformed_leaf",
                    "toolchain": {"target": "arm-none-eabi", "flags": []},
                    "expected": {"size": 1, "sha256": "0" * 64},
                    "relocations": [],
                    **override,
                }
                with self.assertRaisesRegex(apollo_overlay.BuildError, message):
                    apollo_overlay.resolve_leaf_profile(
                        leaf,
                        "linux-clang",
                        record=True,
                    )


class OpenCfwProfileHelperTests(unittest.TestCase):
    def test_profile_specific_provider_paths_select_exact_linux_artifacts(self) -> None:
        manifest = open_cfw.load_manifest(CORE_MANIFEST)
        payloads = open_cfw.read_providers(
            manifest, OPENCFW_ROOT, toolchain_profile="linux-clang"
        )
        self.assertEqual(
            (len(payloads["apollo_bootloader"]),
             open_cfw.sha256_bytes(payloads["apollo_bootloader"])),
            (163824,
             "11f12f80ce187fce53f37b2d27bf9326a8374e1b62a061394e39c511a21b1875"),
        )
        self.assertEqual(
            (len(payloads["apollo_main"]),
             open_cfw.sha256_bytes(payloads["apollo_main"])),
            (3956672,
             "dbfc7bbf1462166b04fb962e9e639ba2296c84a6e0b4f6f22d7ae5e321efc0e6"),
        )
        providers = {
            component["name"]: component["provider"]
            for component in manifest["components"]
        }
        self.assertEqual(
            open_cfw.effective_provider_path(
                providers["apollo_bootloader"], "linux-clang"
            ),
            "build/canonical-provider/linux-clang/apollo_bootloader/"
            "ota_s200_bootloader.bin",
        )
        self.assertEqual(
            open_cfw.effective_provider_path(
                providers["apollo_main"], "linux-clang"
            ),
            "build/canonical-provider/linux-clang/apollo_main-final81/ota_s200_firmware_ota.bin",
        )

    def test_profile_pins_canonical_is_none(self) -> None:
        record = {"profiles": {"linux-clang": {"size": 1}}}
        self.assertIsNone(open_cfw.profile_pins(record, "apple-clang"))

    def test_profile_pins_named_present(self) -> None:
        record = {"profiles": {"linux-clang": {"size": 7, "sha256": "ab"}}}
        self.assertEqual(
            open_cfw.profile_pins(record, "linux-clang"),
            {"size": 7, "sha256": "ab"},
        )

    def test_profile_pins_named_absent_is_none(self) -> None:
        self.assertIsNone(open_cfw.profile_pins({"profiles": {}}, "linux-clang"))
        self.assertIsNone(open_cfw.profile_pins({}, "linux-clang"))

    def test_resolve_profile_id_prefers_explicit_then_env_then_default(self) -> None:
        self.assertEqual(
            open_cfw.resolve_toolchain_profile_id("explicit"), "explicit"
        )
        saved = os.environ.get("OPENCFW_TOOLCHAIN_PROFILE")
        try:
            os.environ["OPENCFW_TOOLCHAIN_PROFILE"] = "from-env"
            self.assertEqual(
                open_cfw.resolve_toolchain_profile_id(None), "from-env"
            )
            del os.environ["OPENCFW_TOOLCHAIN_PROFILE"]
            self.assertEqual(
                open_cfw.resolve_toolchain_profile_id(None), "apple-clang"
            )
        finally:
            if saved is None:
                os.environ.pop("OPENCFW_TOOLCHAIN_PROFILE", None)
            else:
                os.environ["OPENCFW_TOOLCHAIN_PROFILE"] = saved

    def test_direct_profile_recording_is_limited_to_ring_manifest(self) -> None:
        self.assertEqual(
            open_cfw.PROFILE_RECORDING_MANIFESTS,
            frozenset({RING_MANIFEST.resolve()}),
        )
        with self.assertRaisesRegex(
            open_cfw.OpenCFWError,
            "canonical observation/admission workflow",
        ):
            open_cfw.record_manifest_profile_pins(
                CORE_MANIFEST,
                "linux-clang",
                {},
                {"expected_size": 1, "expected_sha256": "0" * 64},
            )

    def test_direct_profile_recording_rejects_hardlinked_manifest(self) -> None:
        with tempfile.TemporaryDirectory(prefix="open-cfw-record-manifest-") as raw:
            root = Path(raw)
            original = root / "ring.json"
            linked = root / "ring-hardlink.json"
            original.write_text("{}", encoding="utf-8")
            os.link(original, linked)
            saved = open_cfw.PROFILE_RECORDING_MANIFESTS
            try:
                open_cfw.PROFILE_RECORDING_MANIFESTS = frozenset({original.resolve()})
                with self.assertRaisesRegex(
                    open_cfw.OpenCFWError,
                    "independent regular file",
                ):
                    open_cfw.record_manifest_profile_pins(
                        original,
                        "linux-clang",
                        {},
                        {"expected_size": 1, "expected_sha256": "0" * 64},
                    )
            finally:
                open_cfw.PROFILE_RECORDING_MANIFESTS = saved

    def test_core_profile_recording_fails_before_provider_reads(self) -> None:
        with tempfile.TemporaryDirectory(prefix="open-cfw-record-output-") as raw:
            with mock.patch.object(open_cfw, "verify_manifest") as verify:
                with self.assertRaisesRegex(
                    open_cfw.OpenCFWError,
                    "canonical observation/admission workflow",
                ):
                    open_cfw.build(
                        CORE_MANIFEST,
                        Path(raw) / "build/output",
                        toolchain_profile="linux-clang",
                        record_profile=True,
                    )
                verify.assert_not_called()


class DetectToolchainTests(unittest.TestCase):
    @staticmethod
    def _fake_clang(tmp: Path, version_line: str) -> str:
        script = tmp / "fake-clang"
        script.write_text(
            "#!/bin/sh\n"
            f'printf "%s\\n" "{version_line}"\n',
            encoding="utf-8",
        )
        script.chmod(0o755)
        return str(script)

    def test_registry_lists_canonical_and_alternates(self) -> None:
        profiles = dict(detect_toolchain.registry_profiles(RING_CONFIG))
        self.assertEqual(profiles["apple-clang"], "Apple clang version 21.0.0")
        self.assertIn("linux-clang", profiles)

    def test_detects_apple_and_homebrew_and_rejects_unknown(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            apple = self._fake_clang(
                tmp, "Apple clang version 21.0.0 (clang-2100.1.1.101)"
            )
            self.assertEqual(
                detect_toolchain.detect(apple, RING_CONFIG), "apple-clang"
            )
            homebrew = self._fake_clang(tmp, "Homebrew clang version 22.1.8")
            self.assertEqual(
                detect_toolchain.detect(homebrew, RING_CONFIG), "linux-clang"
            )
            unknown = self._fake_clang(tmp, "gcc (GCC) 16.1.1")
            with self.assertRaises(SystemExit) as raised:
                detect_toolchain.detect(unknown, RING_CONFIG)
            guidance = str(raised.exception)
            self.assertIn("core-canonical-observation", guidance)
            self.assertIn("core-canonical-admission", guidance)
            self.assertIn("do not use direct --record-profile", guidance)
            self.assertIn("component-specific recorders", guidance)
            self.assertIn("ring-source --record-profile", guidance)


class CoreLz4ProfilePinTests(unittest.TestCase):
    """The active LZ4 closure is independently pinned in both profiles."""

    def test_component_package_and_three_leaf_profile_pins(self) -> None:
        config = json.loads(CORE_CONFIG.read_text(encoding="utf-8"))
        manifest = json.loads(CORE_MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(
            config["expected"],
            {
                "overlay_size": 380_444,
                "overlay_sha256": (
                    "21095c67c3376be1010a7bea19156bae8b1b67bb471525d196c1135d0894f622"
                ),
                "component_size": 3_956_672,
                "component_sha256": (
                    "7bfc8a60ab7b057eb98bc5d72569d6712dfada77c8bb54a8ccc22e994b39b2e6"
                ),
            },
        )
        self.assertEqual(
            config["toolchain_profiles"]["linux-clang"]["expected"],
            {
                "overlay_size": 172_828,
                "overlay_sha256": (
                    "13a12b7fc7ec3af866d4ebe9229105ce923d6842ec6e8c4b0e01564582ed8ab1"
                ),
                "component_size": 3_956_672,
                "component_sha256": (
                    "dbfc7bbf1462166b04fb962e9e639ba2296c84a6e0b4f6f22d7ae5e321efc0e6"
                ),
            },
        )
        self.assertEqual(
            (
                manifest["package"]["expected_size"],
                manifest["package"]["expected_sha256"],
            ),
            (
                4_750_780,
                "1bb3f8c84d288a30cfd252e832ec4a51ac5eca42b5de8e8817db11a938c6a771",
            ),
        )
        self.assertEqual(
            manifest["package"]["profiles"]["linux-clang"],
            {
                "expected_size": 4_750_764,
                "expected_sha256": "50f2ee3722aeaa720eed1a7c65381b02ac3ec0ceabecf9eb57d661d8e060a6d0",
            },
        )

        names = [
            "LZ4_decompress_safe",
            "open_cfw_lz4_decompress_safe",
            "open_cfw_evenhub_mode2_decompress",
        ]
        leaves = {
            leaf["function"]: leaf
            for leaf in config["relocated_leaves"]
            if leaf.get("function") in names
        }
        self.assertEqual(list(leaves), names)
        linux = {
            name: apollo_overlay.resolve_leaf_profile(
                leaves[name], "linux-clang"
            )
            for name in names
        }
        self.assertEqual(
            [linux[name]["expected"]["offset"] for name in names],
            [118_052, 119_808, 119_812],
        )
        self.assertEqual(
            linux["LZ4_decompress_safe"]["closure"]["text_section"],
            ".text.LZ4_decompress_safe",
        )
        self.assertEqual(
            [
                relocation["type"]
                for relocation in linux["LZ4_decompress_safe"]["relocations"]
            ],
            [
                "R_ARM_THM_CALL",
                "R_ARM_THM_MOVW_PREL_NC",
                "R_ARM_THM_MOVT_PREL",
                "R_ARM_THM_MOVW_PREL_NC",
                "R_ARM_THM_MOVT_PREL",
                "R_ARM_THM_CALL",
            ],
        )


class NanopbVarint32LinuxProfileContractTests(unittest.TestCase):
    """Task 7 requires independently recorded Linux pins for both new leaves."""

    def test_varint32_pair_has_complete_linux_leaf_profiles(self) -> None:
        config = json.loads(CORE_CONFIG.read_text(encoding="utf-8"))
        leaves = {
            leaf["function"]: leaf
            for leaf in config["relocated_leaves"]
            if leaf.get("function") in {
                "open_cfw_nanopb_decode_varint32_eof",
                "open_cfw_nanopb_decode_varint32",
            }
        }
        self.assertEqual(
            list(leaves),
            [
                "open_cfw_nanopb_decode_varint32_eof",
                "open_cfw_nanopb_decode_varint32",
            ],
        )
        for function, leaf in leaves.items():
            self.assertIn(
                "linux-clang",
                leaf.get("toolchain_profiles", {}),
                msg=f"{function} lacks its independently recorded Linux profile",
            )
        private = leaves["open_cfw_nanopb_decode_varint32_eof"][
            "toolchain_profiles"
        ]["linux-clang"]
        public = leaves["open_cfw_nanopb_decode_varint32"][
            "toolchain_profiles"
        ]["linux-clang"]
        self.assertEqual(private["reviewed_version_prefix"], "Homebrew clang version 22.1.8")
        self.assertEqual(
            private["expected"],
            {
                "size": 222,
                "sha256": "36bb0167f4d3407b99ed2255cc9e77dd60dc1e9070781a257bfea59abc408171",
                "alignment": 4,
                "offset": 126_796,
                "unrelocated_sha256": "5296b608c55171bca9d5f4d162cf53d0e6aa5f724e1cb82499a7311f2a6cc9ff",
                "closure_size": 238,
                "closure_sha256": "2c49567cfe23e36c504586218719c2e590163bec804353c8106680328d64a480",
                "rodata_offset": 222,
            },
        )
        self.assertEqual(public["reviewed_version_prefix"], "Homebrew clang version 22.1.8")
        self.assertEqual(
            public["expected"],
            {
                "size": 10,
                "sha256": "1f0924d25c50933e7cd5aac05d718da6d44b7a20d4af901fa833c555eca6ff1a",
                "alignment": 4,
                "offset": 127_036,
                "unrelocated_sha256": "e9ec8b612503f867aabf2467e3abfac44753c5576a247a00cbc4309e2a023f93",
            },
        )


class LinuxProfileReproductionTests(unittest.TestCase):
    """Integration: reproduce the recorded alternate profile end to end."""

    def setUp(self) -> None:
        self.clang = _available_clang()
        if self.clang is None:
            raise unittest.SkipTest("no clang available")
        self.profile = _resolved_profile(self.clang)
        if self.profile in (None, "apple-clang"):
            raise unittest.SkipTest(
                "available clang is not a recorded alternate profile"
            )

    def test_overlay_reproduces_committed_pins_and_is_deterministic(self) -> None:
        config = _ring_config()
        pins = config["toolchain_profiles"][self.profile]["expected"]
        with _RepoLocalTemp() as tmp:
            first = apollo_overlay.build(
                root=OPENCFW_ROOT,
                config_path=RING_CONFIG,
                output_dir=tmp / "a",
                clang=self.clang,
                toolchain_profile=self.profile,
            )
            second = apollo_overlay.build(
                root=OPENCFW_ROOT,
                config_path=RING_CONFIG,
                output_dir=tmp / "b",
                clang=self.clang,
                toolchain_profile=self.profile,
            )
        self.assertEqual(first["overlay"]["sha256"], pins["overlay_sha256"])
        self.assertEqual(first["component"]["sha256"], pins["component_sha256"])
        self.assertEqual(
            first["component"]["sha256"], second["component"]["sha256"]
        )
        self.assertEqual(first["toolchain"]["profile"], self.profile)

    def test_canonical_profile_rejects_non_apple_clang(self) -> None:
        with _RepoLocalTemp() as tmp:
            with self.assertRaisesRegex(
                apollo_overlay.BuildError, "reviewed toolchain family"
            ):
                apollo_overlay.build(
                    root=OPENCFW_ROOT,
                    config_path=RING_CONFIG,
                    output_dir=tmp,
                    clang=self.clang,
                    toolchain_profile="apple-clang",
                )

    def test_ring_source_package_reproduces_committed_profile_pin(self) -> None:
        manifest = json.loads(RING_MANIFEST.read_text(encoding="utf-8"))
        package_pin = manifest["package"]["profiles"][self.profile]
        component_dir = (
            OPENCFW_ROOT
            / "components/apollo_main/ring_gesture/build"
        )
        # Produce the source-build provider the manifest points at.
        apollo_overlay.build(
            root=OPENCFW_ROOT,
            config_path=RING_CONFIG,
            output_dir=component_dir,
            clang=self.clang,
            toolchain_profile=self.profile,
        )
        with _RepoLocalTemp() as tmp:
            report = open_cfw.build(
                RING_MANIFEST,
                tmp,
                toolchain_profile=self.profile,
            )
        self.assertEqual(report["package"]["size"], package_pin["expected_size"])
        self.assertEqual(
            report["package"]["sha256"], package_pin["expected_sha256"]
        )


class EffectiveRegionsTests(unittest.TestCase):
    """The admitted whole-image replacement and appended Linux source tail."""

    def _apollo_main_override(self) -> dict:
        manifest = json.loads(CORE_MANIFEST.read_text(encoding="utf-8"))
        component = dict(manifest["component_overrides"]["apollo_main"])
        component["name"] = "apollo_main"
        return component

    def test_canonical_profile_returns_regions_unchanged(self) -> None:
        component = self._apollo_main_override()
        regions = open_cfw.effective_component_regions(
            component, 10_000_000, "apple-clang"
        )
        self.assertIs(regions, component["regions"])

    def test_non_canonical_profile_coarsens_appended_tail(self) -> None:
        component = self._apollo_main_override()
        boundary = component["source_appended_boundary"]
        data_len = boundary + 123456
        regions = open_cfw.effective_component_regions(
            component, data_len, "linux-clang"
        )
        # The reviewed Linux profile replaces the canonical base partition
        # with an exact preamble plus whole-image receipt, then coarsens only
        # its compiler-owned appended source tail.
        self.assertEqual(len(regions), 3)
        self.assertEqual(
            (
                regions[0]["file_offset"],
                regions[0]["size"],
                regions[0]["address_status"],
            ),
            (0, 32, "container_only"),
        )
        self.assertEqual(
            (
                regions[1]["file_offset"],
                regions[1]["size"],
                regions[1]["target_address"],
                regions[1]["address_status"],
            ),
            (32, boundary - 32, 0x00438000,
             "generated_source_data_replacement"),
        )
        coarse = regions[-1]
        self.assertEqual(coarse["file_offset"], boundary)
        self.assertEqual(coarse["size"], data_len - boundary)
        self.assertEqual(coarse["address_status"], "source_compiled")
        # The coarse region exactly closes the partition.
        self.assertEqual(
            sum(r["size"] for r in regions), data_len
        )


class SourceProfileReproductionTests(unittest.TestCase):
    """End-to-end: the full source profile reproduces on this host."""

    def setUp(self) -> None:
        self.clang = _available_clang()
        if self.clang is None:
            raise unittest.SkipTest("no clang available")
        self.profile = _resolved_profile(self.clang)
        if self.profile in (None, "apple-clang"):
            raise unittest.SkipTest(
                "available clang is not a recorded alternate profile"
            )

    def test_core_source_package_reproduces_committed_profile_pin(self) -> None:
        manifest = json.loads(CORE_MANIFEST.read_text(encoding="utf-8"))
        package_pin = manifest["package"]["profiles"][self.profile]
        env = {
            **os.environ,
            "OPENCFW_CLANG": self.clang,
            "OPENCFW_TOOLCHAIN_PROFILE": self.profile,
        }
        for script in (
            "components/bootloader/core_overlay/build_component.py",
            "components/apollo_main/core_overlay/build_component.py",
        ):
            completed = subprocess.run(
                [sys.executable, script],
                cwd=OPENCFW_ROOT,
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                completed.returncode,
                0,
                msg=f"{script} failed: {completed.stderr}",
            )
        component_report = CORE_COMPONENT_BUILD / "build-report.json"
        self.assertEqual(
            (
                component_report.stat().st_size,
                open_cfw.sha256_file(component_report),
            ),
            (
                2_654_590,
                "b71a6ea9b5b4687134432173d563266f6902ef7ce211a8266337d607634b856f",
            ),
        )
        with _RepoLocalTemp() as tmp:
            report = open_cfw.build(
                CORE_MANIFEST,
                tmp,
                toolchain_profile=self.profile,
            )
            report_path = tmp / "build-report.json"
            self.assertEqual(
                (report_path.stat().st_size, open_cfw.sha256_file(report_path)),
                (
                    4_333,
                    "23a24fab255986238741cb7cc7d4deaea70856865a12fc0570bbe81983af41a3",
                ),
            )
            reported_providers = {
                provider["component"]: provider
                for provider in report["providers"]
            }
            self.assertEqual(
                reported_providers["apollo_bootloader"]["path"],
                "build/canonical-provider/linux-clang/apollo_bootloader/"
                "ota_s200_bootloader.bin",
            )
            self.assertEqual(
                reported_providers["apollo_main"]["path"],
                "build/canonical-provider/linux-clang/apollo_main-final81/ota_s200_firmware_ota.bin",
            )
            plan_path = tmp / "flash-plan.json"
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            self.assertEqual(
                (plan_path.stat().st_size, open_cfw.sha256_file(plan_path)),
                (
                    586_640,
                    "a12761cbc365f63d9e253c4fdd4855b9c437c8b70769cbaa1fb5d17f7098f46e",
                ),
            )
            self.assertEqual(
                (
                    len(plan["flash_regions"]),
                    len(plan["unresolved_flash_regions"]),
                    len(plan["container_only_regions"]),
                ),
                (810, 0, 6),
            )

            source_owned_bytes = sum(
                region["size"]
                for region in plan["flash_regions"]
                if region["address_status"] == "source_compiled"
            )
            generated_flash_bytes = sum(
                region["size"]
                for region in plan["flash_regions"]
                if region["address_status"].startswith("generated_")
            )
            merged_manifest = open_cfw.load_manifest(CORE_MANIFEST)
            provider_bytes = 0
            for component in merged_manifest["components"]:
                provider = component["provider"]
                selected = open_cfw.profile_pins(provider, self.profile)
                provider_bytes += int((selected or provider)["size"])
            package_envelope_bytes = (
                package_pin["expected_size"] - provider_bytes
            )
            main_component = manifest["component_overrides"]["apollo_main"]
            main_preamble_bytes = sum(
                min(region["file_offset"] + region["size"], 32)
                - region["file_offset"]
                for region in main_component["regions"]
                if region["file_offset"] < 32
            )
            self.assertEqual(main_preamble_bytes, 32)
            generated_bytes = (
                generated_flash_bytes
                + package_envelope_bytes
                + main_preamble_bytes
            )
            opaque_bytes = (
                package_pin["expected_size"]
                - source_owned_bytes
                - generated_bytes
            )
            self.assertEqual(
                (source_owned_bytes, generated_bytes, opaque_bytes),
                (493_459, 3_542_272, 715_033),
            )
        self.assertEqual(report["package"]["size"], package_pin["expected_size"])
        self.assertEqual(
            report["package"]["sha256"], package_pin["expected_sha256"]
        )


if __name__ == "__main__":
    unittest.main()
