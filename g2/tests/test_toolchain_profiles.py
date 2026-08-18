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
        with self.assertRaisesRegex(
            apollo_overlay.BuildError,
            r"^toolchain\.flags cannot use response files$",
        ):
            apollo_overlay.compiler_source_prefix_flags(
                Path("/actual/worktree/openCFW"),
                {"flags": ["@compiler-flags.rsp"]},
            )

    def test_maps_actual_source_root_to_reviewed_source_root(self) -> None:
        self.assertEqual(
            apollo_overlay.compiler_source_prefix_flags(
                Path("/actual/worktree/openCFW"),
                {"reviewed_source_root": "/reviewed/openCFW", "flags": []},
            ),
            [
                "-ffile-prefix-map=/actual/worktree/openCFW="
                "/reviewed/openCFW"
            ],
        )

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
        with self.assertRaisesRegex(
            apollo_overlay.BuildError,
            "toolchain.flags cannot set -ffile-prefix-map",
        ):
            apollo_overlay.compiler_source_prefix_flags(
                Path("/actual/worktree/openCFW"),
                {
                    "reviewed_source_root": "/reviewed/openCFW",
                    "flags": ["-ffile-prefix-map=/somewhere=/reviewed/openCFW"],
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
            with self.assertRaises(SystemExit):
                detect_toolchain.detect(unknown, RING_CONFIG)


class CoreLz4ProfilePinTests(unittest.TestCase):
    """The active LZ4 closure is independently pinned in both profiles."""

    def test_component_package_and_three_leaf_profile_pins(self) -> None:
        config = json.loads(CORE_CONFIG.read_text(encoding="utf-8"))
        manifest = json.loads(CORE_MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(
            config["expected"],
            {
                "overlay_size": 142986,
                "overlay_sha256": (
                    "1b0fc521cc8964da6525b7f7dce99060d07f5671f0038f37bcd998a56422a49f"
                ),
                "component_size": 3666382,
                "component_sha256": (
                    "a4552ff210b6af33b7826a6b9aaefa6e01c7e6e976c9a852498570ededcf058f"
                ),
            },
        )
        self.assertEqual(
            config["toolchain_profiles"]["linux-clang"]["expected"],
            {
                "overlay_size": 144266,
                "overlay_sha256": (
                    "4c95f20608c70a065b05837415d2d4471fc7eeeb61fa30ce1c1c9f07f717ddb9"
                ),
                "component_size": 3667662,
                "component_sha256": (
                    "686ea217db2837bffd8a190485f0a6f719242e927fba17281c6f54aa066767f6"
                ),
            },
        )
        self.assertEqual(
            (
                manifest["package"]["expected_size"],
                manifest["package"]["expected_sha256"],
            ),
            (
                4444468,
                "53b240df100153c5453697fb3ce8ac66663ca82484a1d69f88345e1e7c3cd3c6",
            ),
        )
        self.assertEqual(
            manifest["package"]["profiles"]["linux-clang"],
            {
                "expected_size": 4446156,
                "expected_sha256": "2cca0fbac8da01ede95a3cecd55dd0706f6dad3a8437605f8a68949cee3c6bc3",
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
            [118052, 119808, 119812],
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
                "offset": 126796,
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
                "offset": 127036,
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
    """The appended-source region coarsening under a non-canonical profile."""

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
        base = [r for r in component["regions"] if r["file_offset"] < boundary]
        data_len = boundary + 123456
        regions = open_cfw.effective_component_regions(
            component, data_len, "linux-clang"
        )
        # Base regions are preserved; the appended tail is one coarse region.
        self.assertEqual(len(regions), len(base) + 1)
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
                1_834_576,
                "540c8bf67144c8822ca3d4982ba5b77062d14f71a3f8bbe6a3b7b564881baa21",
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
                    2_322,
                    "3d0f0968f5f26a550719240a12a0e6f4e083f2ea566940f215f84b2a5f382a9a",
                ),
            )
            plan_path = tmp / "flash-plan.json"
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            self.assertEqual(
                (plan_path.stat().st_size, open_cfw.sha256_file(plan_path)),
                (
                    640188,
                    "4480ca9a4a4f237a477ccccdc9cb039f071fb2f6547298595e98a91098302a20",
                ),
            )
            self.assertEqual(
                (
                    len(plan["flash_regions"]),
                    len(plan["unresolved_flash_regions"]),
                    len(plan["container_only_regions"]),
                ),
                (896, 2, 5),
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
            main_preamble_bytes = next(
                region["size"]
                for region in main_component["regions"]
                if region["name"] == "ota_preamble"
            )
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
                (136709, 94408, 4206615),
            )
        self.assertEqual(report["package"]["size"], package_pin["expected_size"])
        self.assertEqual(
            report["package"]["sha256"], package_pin["expected_sha256"]
        )


if __name__ == "__main__":
    unittest.main()
