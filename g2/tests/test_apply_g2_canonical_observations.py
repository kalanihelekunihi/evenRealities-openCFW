# SPDX-License-Identifier: MIT
from __future__ import annotations

import copy
import importlib.util
import inspect
import json
import os
import sys
import tempfile
import unittest
from unittest import mock
from hashlib import sha256
from pathlib import Path


G2_ROOT = Path(__file__).resolve().parents[1]
TOOL = G2_ROOT / "tools/apply_g2_canonical_observations.py"
CORE_BUILDER = G2_ROOT / "components/apollo_main/core_overlay/build_component.py"
APOLLO_OVERLAY = G2_ROOT / "tools/apollo_overlay.py"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


admission = load(TOOL, "apply_g2_canonical_observations_test")
core_builder = load(CORE_BUILDER, "core_canonical_observation_test")
apollo_overlay = load(APOLLO_OVERLAY, "apollo_overlay_observation_test")


def digest(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def reviewed_pt_sources() -> list[dict[str, object]]:
    config = json.loads(
        (G2_ROOT / "components/apollo_main/core_overlay/overlay.json").read_text(
            encoding="utf-8"
        )
    )
    return copy.deepcopy(
        config["post_link_providers"]["pt_protocol"]["sources"]
    )


def write_observation(root: Path, profile: str, run: str) -> Path:
    directory = root / f"{profile}-{run}"
    directory.mkdir()
    overlay = b"observed-overlay"
    component = b"observed-component"
    overlay_path = directory / "apollo_core_overlay.bin"
    component_path = directory / "ota_s200_firmware_ota.bin"
    overlay_path.write_bytes(overlay)
    component_path.write_bytes(component)
    intermediate_payloads = {
        "core_stage_overlay": b"C",
        "core_stage_component": b"BC",
        "liblc3_payload": b"l",
        "liblc3_component": b"m",
    }
    intermediate_names = {
        "core_stage_overlay": "core-stage-overlay.bin",
        "core_stage_component": "core-stage-component.bin",
        "liblc3_payload": "liblc3-payload.bin",
        "liblc3_component": "liblc3-component.bin",
    }
    for key, payload in intermediate_payloads.items():
        (directory / intermediate_names[key]).write_bytes(payload)
    entries = [{"path": "source.c", "size": 1, "sha256": digest(b"s")}]
    source_inputs = {
        "entries": entries,
        "sha256": digest(json.dumps(
            entries, sort_keys=True, separators=(",", ":")
        ).encode()),
    }
    version = "Apple clang exact" if profile == "apple-clang" else "Linux clang exact"
    compiler = root / f"{profile}-compiler.bin"
    linker = root / f"{profile}-linker.bin"
    symbol_reader = root / f"{profile}-nm.bin"
    resource_dir = root / f"{profile}-resource"
    include_dir = resource_dir / "include"
    include_dir.mkdir(parents=True, exist_ok=True)
    header = b"#define FIXTURE 1\n"
    (include_dir / "fixture.h").write_bytes(header)
    header_entries = [
        {"path": "fixture.h", "size": len(header), "sha256": digest(header)}
    ]

    def write_tool(path: Path, executable_version: str, resource: Path | None = None):
        script = (
            "#!/usr/bin/env python3\n"
            "import sys\n"
            f"version = {executable_version!r}\n"
            f"resource = {str(resource) if resource is not None else ''!r}\n"
            "if sys.argv[1:] == ['--no-default-config', "
            "'-print-resource-dir'] and resource:\n"
            "    print(resource)\n"
            "elif sys.argv[1:] == (['--no-default-config', '--version'] "
            "if resource else ['--version']):\n"
            "    print(version)\n"
            "else:\n"
            "    raise SystemExit(2)\n"
        ).encode()
        path.write_bytes(script)
        path.chmod(0o755)

    write_tool(compiler, version + "\nfixture compiler detail", resource_dir.resolve())
    write_tool(linker, f"{profile} linker")
    write_tool(symbol_reader, f"{profile} nm")

    def executable_record(path, executable_version):
        payload = path.read_bytes()
        return {
            "invocation_path": str(path),
            "resolved_path": str(path.resolve()),
            "size": len(payload),
            "sha256": digest(payload),
            "version": executable_version,
        }

    observation = {
        "schema_version": 2,
        "complete": True,
        "profile": profile,
        "source_inputs": source_inputs,
        "toolchain": {
            "executable": str(compiler),
            "profile": profile,
            "version": version,
            "target": "thumbv7em-none-eabi",
            "flags": ["-O2"],
        },
        "toolchain_identity": {
            "schema_version": 2,
            "executables": {
                "compiler": executable_record(compiler, version),
                "pt_linker": executable_record(linker, f"{profile} linker"),
                "pt_nm": executable_record(symbol_reader, f"{profile} nm"),
            },
            "compiler_resource_headers": {
                "resource_dir": str(resource_dir.resolve()),
                "entry_count": 1,
                "total_size": len(header),
                "sha256": digest(json.dumps(
                    header_entries, sort_keys=True, separators=(",", ":")
                ).encode()),
                "entries": header_entries,
            },
        },
        "image_mapping": {"base_size": 1, "run_base": 1, "preamble_bytes": 0},
        "core_stage": {
            "expected": {
                "overlay_size": 1,
                "overlay_sha256": digest(b"C"),
                "component_size": 2,
                "component_sha256": digest(b"BC"),
            },
            "functions": {},
            "isolated_leaves": [],
            "relocated_leaves": [],
            "in_place_leaves": [],
            "in_place_data": [],
        },
        "liblc3_ltpf": {
            "license": "Apache-2.0",
            "payload_size": 1,
            "payload_sha256": digest(b"l"),
            "component_size": 1,
            "component_sha256": digest(b"m"),
            "placement": {
                "entry": 1,
                "entry_hex": "0x00000001",
                "file_offset": 1,
                "runtime_address": 1,
                "runtime_address_hex": "0x00000001",
            },
            "historical_non_corpus_routing": {
                "0x00438400": False,
                "0x00438604": False,
            },
        },
        "pt_protocol": {
            "license": admission.PT_AGGREGATE_LICENSE,
            "sources": reviewed_pt_sources(),
            "payload_size": 1,
            "payload_sha256": digest(b"p"),
            "interval_sha256": digest(b"i"),
            "placement": {"sections": {}},
        },
        "final": {
            "overlay_size": len(overlay),
            "overlay_sha256": digest(overlay),
            "component_size": len(component),
            "component_sha256": digest(component),
        },
        "final_artifacts": {
            "overlay": {
                "artifact": overlay_path.name,
                "size": len(overlay),
                "sha256": digest(overlay),
            },
            "component": {
                "artifact": component_path.name,
                "size": len(component),
                "sha256": digest(component),
            },
        },
        "intermediate_artifacts": {
            key: {
                "artifact": intermediate_names[key],
                "size": len(payload),
                "sha256": digest(payload),
            }
            for key, payload in intermediate_payloads.items()
        },
    }
    report = {
        "canonical_observation": observation,
        "overlay": {
            "artifact": str(overlay_path),
            "size": len(overlay),
            "sha256": digest(overlay),
        },
        "component": {
            "artifact": str(component_path),
            "size": len(component),
            "sha256": digest(component),
        },
    }
    report_path = directory / "build-report.json"
    report_path.write_text(json.dumps(report), encoding="utf-8")
    return report_path


class ObservationAdmissionTests(unittest.TestCase):
    def test_make_canonical_gate_includes_recorder_security_transitively(self):
        makefile = (G2_ROOT / "Makefile").read_text(encoding="utf-8")
        canonical_target = makefile.split("core-canonical-test:\n", 1)[1].split(
            "\n\n", 1
        )[0]
        self.assertIn("tests.test_apply_g2_canonical_observations", canonical_target)
        self.assertIn("tests.test_core_canonical_recorder_security", canonical_target)
        community_prerequisites = makefile.split(
            "community-distribution-gate:", 1
        )[1].split("\n\tPYTHONDONTWRITEBYTECODE", 1)[0]
        self.assertIn("core-canonical-test", community_prerequisites)
        self.assertIn(
            "community-source-bundle: community-distribution-gate", makefile
        )
        self.assertIn(
            "source-release: community-distribution-gate release-license-gate source",
            makefile,
        )

    @staticmethod
    def identity_observation(root: Path, run: str) -> dict:
        keys = (
            "overlay", "component", "core_stage_overlay",
            "core_stage_component", "liblc3_payload", "liblc3_component",
        )
        directory = root / run
        directory.mkdir()
        report = directory / "build-report.json"
        report.write_bytes(b"same reproducible report fixture")
        artifacts = {}
        for key in keys:
            path = directory / f"{key}.bin"
            path.write_bytes(b"same reproducible artifact fixture")
            artifacts[key] = path

        def identity(path: Path) -> tuple[int, int, int, int, int]:
            observed = path.stat()
            return (
                observed.st_dev, observed.st_ino, observed.st_size,
                observed.st_mtime_ns, observed.st_ctime_ns,
            )

        return {
            "paths": {"report": report, **artifacts},
            "report_identity": identity(report),
            "artifact_identities": {
                key: identity(path) for key, path in artifacts.items()
            },
        }

    def test_all_four_observations_require_cross_profile_inode_independence(self):
        roles = (
            "report", "overlay", "component", "core_stage_overlay",
            "core_stage_component", "liblc3_payload", "liblc3_component",
        )
        for role in roles:
            with self.subTest(cross_profile_hardlink=role), \
                    tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                observations = tuple(
                    self.identity_observation(root, run)
                    for run in ("apple-a", "apple-b", "linux-a", "linux-b")
                )
                source = observations[0]["paths"][role]
                alias = observations[2]["paths"][role]
                alias.unlink()
                os.link(source, alias)
                aliased = copy.deepcopy(observations)
                identity = source.stat()
                shared = (
                    identity.st_dev, identity.st_ino, identity.st_size,
                    identity.st_mtime_ns, identity.st_ctime_ns,
                )
                if role == "report":
                    aliased[2]["report_identity"] = shared
                else:
                    aliased[2]["artifact_identities"][role] = shared
                with self.assertRaisesRegex(
                    admission.AdmissionError, "distinct inodes"
                ):
                    admission.validate_observation_independence(aliased)

    def test_equal_artifact_bytes_on_independent_inodes_remain_admissible(self):
        # Inode independence is orthogonal to reproducibility: equal bytes from
        # separately recorded runs must continue to pass this boundary.
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            observations = tuple(
                self.identity_observation(root, run)
                for run in ("apple-a", "apple-b", "linux-a", "linux-b")
            )
            admission.validate_observation_independence(observations)

    def test_all_four_independence_precedes_both_dry_run_and_apply_work(self):
        for apply in (False, True):
            with self.subTest(apply=apply), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                observations = [
                    self.identity_observation(root, run)
                    for run in ("apple-a", "apple-b", "linux-a", "linux-b")
                ]
                observations[2]["report_identity"] = observations[0][
                    "report_identity"
                ]
                arguments = mock.Mock(
                    apple_observation=[Path("apple-a"), Path("apple-b")],
                    linux_observation=[Path("linux-a"), Path("linux-b")],
                    apply=apply,
                )
                with (
                    mock.patch.object(
                        admission, "admit_reproducible_pair",
                        side_effect=(
                            tuple(observations[:2]), tuple(observations[2:]),
                        ),
                    ),
                    mock.patch.object(admission, "validate_generation") as generation,
                    mock.patch.object(admission, "_admission_lock") as lock,
                    mock.patch.object(admission, "_run_locked") as run_locked,
                ):
                    with self.assertRaisesRegex(
                        admission.AdmissionError, "distinct inodes"
                    ):
                        admission.run(arguments)
                generation.assert_not_called()
                lock.assert_not_called()
                run_locked.assert_not_called()

    def test_two_matching_observations_are_admitted(self):
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            root = Path(temporary)
            pair = [
                write_observation(root, "apple-clang", "one"),
                write_observation(root, "apple-clang", "two"),
            ]
            admitted = admission.admit_pair(pair, "apple-clang")
            self.assertEqual(admitted["observation"]["profile"], "apple-clang")

    def test_cross_profile_pair_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            root = Path(temporary)
            pair = [
                write_observation(root, "linux-clang", "one"),
                write_observation(root, "linux-clang", "two"),
            ]
            with self.assertRaisesRegex(admission.AdmissionError, "not 'apple-clang'"):
                admission.admit_pair(pair, "apple-clang")

    def test_hardlinked_observation_is_not_an_independent_run(self):
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            root = Path(temporary)
            first = write_observation(root, "apple-clang", "one")
            second = first.parent / "build-report-hardlink.json"
            os.link(first, second)
            with self.assertRaisesRegex(admission.AdmissionError, "exactly one hard link"):
                admission.admit_pair([first, second], "apple-clang")

    def test_observation_outside_g2_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = write_observation(Path(temporary), "apple-clang", "one")
            with self.assertRaisesRegex(admission.AdmissionError, "inside the G2 tree"):
                admission.load_observation(path, "apple-clang")

    def test_partial_generation_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            path = write_observation(Path(temporary), "apple-clang", "one")
            (path.parent / "ota_s200_firmware_ota.bin").unlink()
            with self.assertRaisesRegex(
                admission.AdmissionError, "cannot (?:read|resolve)"
            ):
                admission.load_observation(path, "apple-clang")

    def test_intra_generation_artifact_inode_reuse_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            path = write_observation(Path(temporary), "apple-clang", "one")
            report = json.loads(path.read_text())
            observation = report["canonical_observation"]
            observation["intermediate_artifacts"]["core_stage_overlay"] = copy.deepcopy(
                observation["final_artifacts"]["overlay"]
            )
            path.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaisesRegex(admission.AdmissionError, "distinct inodes"):
                admission.load_observation(path, "apple-clang")

    def test_v2_intermediate_and_final_pin_mutations_are_rejected(self):
        mutations = (
            ("core_stage", "expected", "overlay_size"),
            ("core_stage", "expected", "overlay_sha256"),
            ("core_stage", "expected", "component_size"),
            ("core_stage", "expected", "component_sha256"),
            ("liblc3_ltpf", "payload_size"),
            ("liblc3_ltpf", "payload_sha256"),
            ("liblc3_ltpf", "component_size"),
            ("liblc3_ltpf", "component_sha256"),
            ("final", "overlay_size"),
            ("final", "overlay_sha256"),
            ("final", "component_size"),
            ("final", "component_sha256"),
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory(
                dir=G2_ROOT
            ) as temporary:
                path = write_observation(Path(temporary), "apple-clang", "one")
                report = json.loads(path.read_text())
                target = report["canonical_observation"]
                for key in mutation[:-1]:
                    target = target[key]
                field = mutation[-1]
                value = target[field]
                target[field] = (
                    value + 1 if isinstance(value, int) else digest(field.encode())
                )
                path.write_text(json.dumps(report), encoding="utf-8")
                with self.assertRaises(admission.AdmissionError):
                    admission.load_observation(path, "apple-clang")

    def test_v2_unknown_field_and_intermediate_symlink_are_rejected(self):
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            path = write_observation(Path(temporary), "apple-clang", "one")
            report = json.loads(path.read_text())
            report["canonical_observation"]["unexpected"] = True
            path.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaisesRegex(admission.AdmissionError, "incomplete"):
                admission.load_observation(path, "apple-clang")
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            path = write_observation(Path(temporary), "apple-clang", "one")
            artifact = path.parent / "core-stage-overlay.bin"
            replacement = path.parent / "replacement.bin"
            replacement.write_bytes(artifact.read_bytes())
            artifact.unlink()
            artifact.symlink_to(replacement)
            with self.assertRaisesRegex(admission.AdmissionError, "symlink"):
                admission.load_observation(path, "apple-clang")

    def test_v2_nested_unknown_fields_and_unlisted_header_are_rejected(self):
        for container in ("source_inputs", "toolchain", "core_stage", "liblc3_ltpf"):
            with self.subTest(container=container), tempfile.TemporaryDirectory(
                dir=G2_ROOT
            ) as temporary:
                path = write_observation(Path(temporary), "apple-clang", "one")
                report = json.loads(path.read_text())
                report["canonical_observation"][container]["unexpected"] = True
                path.write_text(json.dumps(report), encoding="utf-8")
                with self.assertRaises(admission.AdmissionError):
                    admission.load_observation(path, "apple-clang")
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            path = write_observation(Path(temporary), "apple-clang", "one")
            report = json.loads(path.read_text())
            resource = Path(
                report["canonical_observation"]["toolchain_identity"]
                ["compiler_resource_headers"]["resource_dir"]
            )
            (resource / "include/unlisted.h").write_bytes(b"unlisted")
            with self.assertRaisesRegex(admission.AdmissionError, "entries changed"):
                admission.load_observation(path, "apple-clang")

    def test_compiler_resource_root_and_include_symlinks_are_rejected(self):
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            root = Path(temporary)
            path = write_observation(root, "apple-clang", "one")
            resource = root / "apple-clang-resource"
            include = resource / "include"
            real_include = resource / "real-include"
            include.rename(real_include)
            include.symlink_to(real_include.name, target_is_directory=True)
            with self.assertRaisesRegex(admission.AdmissionError, "symlink"):
                admission.load_observation(path, "apple-clang")

        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            root = Path(temporary)
            path = write_observation(root, "apple-clang", "one")
            report = json.loads(path.read_text(encoding="utf-8"))
            resource = root / "apple-clang-resource"
            resource_alias = root / "resource-alias"
            resource_alias.symlink_to(resource.name, target_is_directory=True)
            report["canonical_observation"]["toolchain_identity"][
                "compiler_resource_headers"
            ]["resource_dir"] = str(resource_alias)
            path.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaisesRegex(admission.AdmissionError, "symlink"):
                admission.load_observation(path, "apple-clang")

    def test_liblc3_license_and_historical_route_claims_are_bound(self):
        for field, value in (
            ("license", "BSD-3-Clause"),
            ("historical_non_corpus_routing", {"0x00438400": True}),
        ):
            with self.subTest(field=field), tempfile.TemporaryDirectory(
                dir=G2_ROOT
            ) as temporary:
                path = write_observation(Path(temporary), "apple-clang", "one")
                report = json.loads(path.read_text())
                report["canonical_observation"]["liblc3_ltpf"][field] = value
                path.write_text(json.dumps(report), encoding="utf-8")
                with self.assertRaises(admission.AdmissionError):
                    admission.load_observation(path, "apple-clang")

    def test_tool_versions_and_compiler_resource_query_are_independently_bound(self):
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            path = write_observation(Path(temporary), "apple-clang", "one")
            report = json.loads(path.read_text())
            report["canonical_observation"]["toolchain_identity"]["executables"][
                "pt_nm"
            ]["version"] = "fabricated nm version"
            path.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaisesRegex(admission.AdmissionError, "version differs"):
                admission.load_observation(path, "apple-clang")
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            path = write_observation(Path(temporary), "apple-clang", "one")
            report = json.loads(path.read_text())
            report["canonical_observation"]["toolchain"]["executable"] = (
                "/fabricated/compiler-entry"
            )
            path.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaisesRegex(
                admission.AdmissionError, "compiler toolchain receipts disagree"
            ):
                admission.load_observation(path, "apple-clang")
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            path = write_observation(Path(temporary), "apple-clang", "one")
            report = json.loads(path.read_text())
            report["canonical_observation"]["toolchain_identity"]["executables"][
                "compiler"
            ]["version"] = "Apple clang exact\nfixture compiler detail"
            path.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaisesRegex(admission.AdmissionError, "version differs"):
                admission.load_observation(path, "apple-clang")
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            root = Path(temporary)
            path = write_observation(root, "apple-clang", "one")
            report = json.loads(path.read_text())
            alternate = root / "alternate-resource"
            include = alternate / "include"
            include.mkdir(parents=True)
            payload = b"#define ALTERNATE 1\n"
            (include / "alternate.h").write_bytes(payload)
            entries = [{
                "path": "alternate.h",
                "size": len(payload),
                "sha256": digest(payload),
            }]
            closure = report["canonical_observation"]["toolchain_identity"][
                "compiler_resource_headers"
            ]
            closure.update({
                "resource_dir": str(alternate.resolve()),
                "entry_count": 1,
                "total_size": len(payload),
                "sha256": digest(json.dumps(
                    entries, sort_keys=True, separators=(",", ":")
                ).encode()),
                "entries": entries,
            })
            path.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaisesRegex(
                admission.AdmissionError, "resource directory differs"
            ):
                admission.load_observation(path, "apple-clang")

    def test_noncanonical_tool_and_resource_paths_are_rejected(self):
        mutations = (
            ("relative-invocation", "compiler", "invocation_path"),
            ("dot-invocation", "compiler", "invocation_path"),
            ("redundant-invocation", "compiler", "invocation_path"),
            ("double-root-invocation", "compiler", "invocation_path"),
            ("relative-resolved", "compiler", "resolved_path"),
            ("dot-resolved", "compiler", "resolved_path"),
            ("redundant-resolved", "compiler", "resolved_path"),
            ("double-root-resolved", "compiler", "resolved_path"),
            ("symlink-resolved", "compiler", "resolved_path"),
            ("dot-resource", None, "resource_dir"),
            ("redundant-resource", None, "resource_dir"),
            ("double-root-resource", None, "resource_dir"),
        )
        for mutation, executable, field in mutations:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory(
                dir=G2_ROOT
            ) as temporary:
                root = Path(temporary)
                path = write_observation(root, "apple-clang", "one")
                report = json.loads(path.read_text(encoding="utf-8"))
                identity = report["canonical_observation"]["toolchain_identity"]
                if executable is None:
                    record = identity["compiler_resource_headers"]
                else:
                    record = identity["executables"][executable]
                original = record[field]
                original_path = Path(original)
                if mutation.startswith("relative-"):
                    record[field] = str(original_path.relative_to(G2_ROOT))
                elif mutation.startswith("dot-"):
                    record[field] = (
                        str(original_path.parent) + "/./" + original_path.name
                    )
                elif mutation.startswith("redundant-"):
                    record[field] = str(original_path.parent) + "//" + original_path.name
                elif mutation.startswith("double-root-"):
                    record[field] = "/" + original
                else:
                    alias = root / "compiler-resolved-alias"
                    alias.symlink_to(original_path)
                    record[field] = str(alias)
                path.write_text(json.dumps(report), encoding="utf-8")
                with self.assertRaisesRegex(
                    admission.AdmissionError,
                    "absolute and normalized|not canonical|directory is unsafe",
                ):
                    admission.load_observation(path, "apple-clang")

    def test_relative_tool_path_is_rejected_before_cwd_dependent_query(self):
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            path = write_observation(Path(temporary), "apple-clang", "one")
            report = json.loads(path.read_text(encoding="utf-8"))
            compiler = report["canonical_observation"]["toolchain_identity"][
                "executables"
            ]["compiler"]
            compiler["invocation_path"] = str(
                Path(compiler["invocation_path"]).relative_to(G2_ROOT)
            )
            path.write_text(json.dumps(report), encoding="utf-8")
            with mock.patch.object(admission.subprocess, "run") as query:
                with self.assertRaisesRegex(
                    admission.AdmissionError, "absolute and normalized"
                ):
                    admission.load_observation(path, "apple-clang")
            query.assert_not_called()

    def test_absolute_tool_entry_symlink_remains_authenticated(self):
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            root = Path(temporary)
            path = write_observation(root, "apple-clang", "one")
            report = json.loads(path.read_text(encoding="utf-8"))
            compiler = report["canonical_observation"]["toolchain_identity"][
                "executables"
            ]["compiler"]
            alias = root / "compiler-invocation-alias"
            alias.symlink_to(Path(compiler["resolved_path"]))
            compiler["invocation_path"] = str(alias)
            report["canonical_observation"]["toolchain"]["executable"] = str(alias)
            path.write_text(json.dumps(report), encoding="utf-8")
            admitted = admission.load_observation(path, "apple-clang")
            self.assertEqual(admitted["observation"]["profile"], "apple-clang")

    def test_authenticated_multilink_tool_executable_is_accepted(self):
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            root = Path(temporary)
            path = write_observation(root, "apple-clang", "one")
            report = json.loads(path.read_text(encoding="utf-8"))
            symbol_reader = Path(
                report["canonical_observation"]["toolchain_identity"]
                ["executables"]["pt_nm"]["resolved_path"]
            )
            alias = root / "pt-nm-platform-hardlink"
            os.link(symbol_reader, alias)
            self.assertEqual(symbol_reader.stat().st_nlink, 2)

            admitted = admission.load_observation(path, "apple-clang")

            self.assertEqual(admitted["observation"]["profile"], "apple-clang")

    def test_authenticated_multilink_resource_header_is_accepted(self):
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            root = Path(temporary)
            path = write_observation(root, "apple-clang", "one")
            report = json.loads(path.read_text(encoding="utf-8"))
            resource = Path(
                report["canonical_observation"]["toolchain_identity"]
                ["compiler_resource_headers"]["resource_dir"]
            )
            header = resource / "include/fixture.h"
            os.link(header, root / "fixture-platform-hardlink.h")
            self.assertEqual(header.stat().st_nlink, 2)

            admitted = admission.load_observation(path, "apple-clang")

            self.assertEqual(admitted["observation"]["profile"], "apple-clang")

    def test_artifact_and_profile_provider_hardlinks_remain_rejected(self):
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            root = Path(temporary)
            path = write_observation(root, "apple-clang", "one")
            artifact = path.parent / "ota_s200_firmware_ota.bin"
            os.link(artifact, path.parent / "component-hardlink.bin")
            with self.assertRaisesRegex(
                admission.AdmissionError, "exactly one hard link"
            ):
                admission.load_observation(path, "apple-clang")

        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            root = Path(temporary)
            provider = root / "linux-boot-provider.bin"
            provider.write_bytes(b"authenticated provider")
            os.link(provider, root / "linux-boot-provider-hardlink.bin")
            with self.assertRaisesRegex(
                admission.AdmissionError, "exactly one hard link"
            ):
                admission.load_profile_provider_inputs([
                    ("linux-clang", "apollo_bootloader", provider)
                ])

    def test_byte_identical_tool_inode_swap_during_query_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            root = Path(temporary)
            path = write_observation(root, "apple-clang", "one")
            report = json.loads(path.read_text(encoding="utf-8"))
            compiler = Path(
                report["canonical_observation"]["toolchain_identity"]
                ["executables"]["compiler"]["resolved_path"]
            )
            original_query = admission._tool_query
            replaced = False

            def replace_after_query(invocation, arguments, role):
                nonlocal replaced
                result = original_query(invocation, arguments, role)
                if role == "compiler version" and not replaced:
                    replaced = True
                    replacement = compiler.with_name("replacement-compiler")
                    replacement.write_bytes(compiler.read_bytes())
                    replacement.chmod(compiler.stat().st_mode)
                    os.replace(replacement, compiler)
                return result

            with mock.patch.object(
                admission, "_tool_query", side_effect=replace_after_query
            ):
                with self.assertRaisesRegex(
                    admission.AdmissionError, "changed during identity query"
                ):
                    admission.load_observation(path, "apple-clang")

    def test_byte_identical_resource_root_swap_during_query_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            root = Path(temporary)
            path = write_observation(root, "apple-clang", "one")
            report = json.loads(path.read_text(encoding="utf-8"))
            resource = Path(
                report["canonical_observation"]["toolchain_identity"]
                ["compiler_resource_headers"]["resource_dir"]
            )
            original_query = admission._tool_query
            replaced = False

            def replace_after_query(invocation, arguments, role):
                nonlocal replaced
                result = original_query(invocation, arguments, role)
                if role == "compiler resource directory" and not replaced:
                    replaced = True
                    displaced = resource.with_name("displaced-resource")
                    resource.rename(displaced)
                    (resource / "include").mkdir(parents=True)
                    (resource / "include/fixture.h").write_bytes(
                        (displaced / "include/fixture.h").read_bytes()
                    )
                return result

            with mock.patch.object(
                admission, "_tool_query", side_effect=replace_after_query
            ):
                with self.assertRaisesRegex(
                    admission.AdmissionError, "resource-header directory changed"
                ):
                    admission.load_observation(path, "apple-clang")

    def test_resource_header_change_between_authentication_scans_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            root = Path(temporary)
            path = write_observation(root, "apple-clang", "one")
            report = json.loads(path.read_text(encoding="utf-8"))
            resource = Path(
                report["canonical_observation"]["toolchain_identity"]
                ["compiler_resource_headers"]["resource_dir"]
            )
            header = resource / "include/fixture.h"
            original_read = (
                admission._read_authenticated_resource_header_with_identity
            )
            reads = 0

            def change_after_first_read(candidate, role):
                nonlocal reads
                result = original_read(candidate, role)
                if candidate == header:
                    reads += 1
                    if reads == 1:
                        header.write_bytes(b"#define FIXTURE 2\n")
                return result

            with mock.patch.object(
                admission,
                "_read_authenticated_resource_header_with_identity",
                side_effect=change_after_first_read,
            ):
                with self.assertRaisesRegex(
                    admission.AdmissionError,
                    "changed during authentication",
                ):
                    admission.load_observation(path, "apple-clang")

    def test_tool_identity_queries_remove_ambient_include_environment(self):
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            path = write_observation(Path(temporary), "apple-clang", "one")
            observed_environments = []
            real_run = admission.subprocess.run

            def capture_environment(*args, **kwargs):
                observed_environments.append(kwargs.get("env"))
                return real_run(*args, **kwargs)

            with mock.patch.dict(os.environ, {
                "CPATH": "/untrusted/include",
                "C_INCLUDE_PATH": "/untrusted/c-include",
                "SDKROOT": "/untrusted/sdk",
                "CCC_OVERRIDE_OPTIONS": "^--sysroot=/untrusted+",
            }), mock.patch.object(
                admission.subprocess, "run", side_effect=capture_environment
            ):
                admitted = admission.load_observation(path, "apple-clang")
            self.assertEqual(admitted["observation"]["profile"], "apple-clang")
            self.assertEqual(len(observed_environments), 4)
            for environment in observed_environments:
                self.assertIsInstance(environment, dict)
                for key in apollo_overlay._COMPILER_INCLUDE_ENVIRONMENT:
                    self.assertNotIn(key, environment)

    def test_stale_source_generation_is_rejected(self):
        entries = [{"path": "source.c", "size": 1, "sha256": digest(b"s")}]
        expected = {
            "entries": entries,
            "sha256": digest(json.dumps(
                entries, sort_keys=True, separators=(",", ":")
            ).encode()),
        }
        with self.assertRaisesRegex(admission.AdmissionError, "stale"):
            admission.validate_current_inputs(
                expected, {"source.c": (1, digest(b"changed"))}
            )

    def test_only_artifact_proven_final_and_pt_pins_are_updated(self):
        config = {
            "sentinel": {"curated": True},
            "source": {"path": "source.c"},
            "toolchain": {
                "reviewed_version_prefix": "apple-clang-exact",
                "cflags": ["-O2", "-ffreestanding"],
            },
            "core_stage_expected": {
                "overlay_size": 1,
                "overlay_sha256": digest(b"apple-clang"),
                "component_size": 2,
                "component_sha256": digest(b"apple-clangc"),
            },
            "expected": {},
            "toolchain_profiles": {
                "linux-clang": {
                    "reviewed_version_prefix": "linux-clang-exact",
                    "core_stage_expected": {
                        "overlay_size": 1,
                        "overlay_sha256": digest(b"linux-clang"),
                        "component_size": 2,
                        "component_sha256": digest(b"linux-clangc"),
                    },
                    "expected": {},
                }
            },
            "post_link_providers": {
                "liblc3_ltpf": {
                    "profiles": {
                        profile: {
                            "overlay": {
                                "size": 3,
                                "sha256": digest((profile + "l").encode()),
                            },
                            "component": {
                                "size": 4,
                                "sha256": digest((profile + "m").encode()),
                            },
                        }
                        for profile in ("apple-clang", "linux-clang")
                    }
                },
                "pt_protocol": {
                    "profiles": {"apple-clang": {}, "linux-clang": {}}
                },
            },
            "isolated_leaves": [],
            "relocated_leaves": [],
            "in_place_leaves": [],
            "in_place_data": [],
        }
        projected_before = core_builder._canonical_config_projection(config)

        def observed(profile):
            return {
                "toolchain": {"profile": profile, "version": f"{profile}-exact"},
                "core_stage": {
                    "expected": {
                        "overlay_size": 1,
                        "overlay_sha256": digest(profile.encode()),
                        "component_size": 2,
                        "component_sha256": digest((profile + "c").encode()),
                    },
                    "functions": {},
                    "isolated_leaves": [],
                    "relocated_leaves": [],
                    "in_place_leaves": [],
                    "in_place_data": [],
                },
                "liblc3_ltpf": {
                    "payload_size": 3,
                    "payload_sha256": digest((profile + "l").encode()),
                    "component_size": 4,
                    "component_sha256": digest((profile + "m").encode()),
                    "placement": {},
                },
                "pt_protocol": {
                    "payload_size": 5,
                    "payload_sha256": digest((profile + "p").encode()),
                    "interval_sha256": digest((profile + "i").encode()),
                },
                "final": {
                    "overlay_size": 6,
                    "overlay_sha256": digest((profile + "o").encode()),
                    "component_size": 7,
                    "component_sha256": digest((profile + "f").encode()),
                },
            }

        reviewed_before = copy.deepcopy(config)
        admission.update_profile_pins(config, "apple-clang", observed("apple-clang"))
        admission.update_profile_pins(config, "linux-clang", observed("linux-clang"))
        self.assertEqual(config["sentinel"], {"curated": True})
        self.assertEqual(
            config["core_stage_expected"], reviewed_before["core_stage_expected"]
        )
        self.assertEqual(
            config["post_link_providers"]["liblc3_ltpf"],
            reviewed_before["post_link_providers"]["liblc3_ltpf"],
        )
        self.assertEqual(
            set(config["post_link_providers"]["pt_protocol"]["profiles"]
                ["apple-clang"]),
            {"payload_size", "payload_sha256", "interval_sha256"},
        )
        self.assertEqual(
            core_builder._canonical_config_projection(config), projected_before
        )
        semantic_path_edit = copy.deepcopy(config)
        semantic_path_edit["source"]["path"] = "other-source.c"
        self.assertNotEqual(
            core_builder._canonical_config_projection(semantic_path_edit),
            projected_before,
        )
        semantic_toolchain_edit = copy.deepcopy(config)
        semantic_toolchain_edit["toolchain"]["cflags"].append("-fno-builtin")
        self.assertNotEqual(
            core_builder._canonical_config_projection(semantic_toolchain_edit),
            projected_before,
        )

        for family, field in (
            ("core_stage", "overlay_size"),
            ("core_stage", "overlay_sha256"),
            ("core_stage", "component_size"),
            ("core_stage", "component_sha256"),
            ("liblc3_ltpf", "payload_size"),
            ("liblc3_ltpf", "payload_sha256"),
            ("liblc3_ltpf", "component_size"),
            ("liblc3_ltpf", "component_sha256"),
        ):
            with self.subTest(frozen_family=family, field=field):
                changed = observed("apple-clang")
                target = (
                    changed[family]["expected"]
                    if family == "core_stage" else changed[family]
                )
                target[field] = (
                    target[field] + 1
                    if isinstance(target[field], int)
                    else digest((field + "changed").encode())
                )
                with self.assertRaisesRegex(
                    admission.AdmissionError, "future explicit"
                ):
                    admission.update_profile_pins(
                        copy.deepcopy(reviewed_before), "apple-clang", changed
                    )

    def test_all_reviewed_leaf_pin_families_are_reject_only(self):
        version = "reviewed compiler exact"
        reloc_expected = {
            "size": 4,
            "sha256": digest(b"TEXT"),
            "alignment": 4,
            "offset": 8,
            "unrelocated_sha256": digest(b"text"),
            "closure_size": 8,
            "closure_sha256": digest(b"TEXTRODA"),
            "rodata_offset": 4,
        }
        relocations = [
            {
                "offset": 0,
                "type": "R_ARM_THM_CALL",
                "symbol": "target",
                "target_address": 0x1234,
            }
        ]
        rodata = {
            "alignment": 4,
            "section": ".rodata",
            "size": 4,
            "sha256": digest(b"RODA"),
            "symbols": [{"name": "table", "offset": 0, "size": 4}],
        }
        text_runtime = 0x1108
        rodata_runtime = text_runtime + reloc_expected["rodata_offset"]
        enriched_rodata = {
            **copy.deepcopy(rodata),
            "offset": reloc_expected["rodata_offset"],
            "runtime_address": rodata_runtime,
            "runtime_address_hex": f"0x{rodata_runtime:08X}",
            "symbols": [{
                **copy.deepcopy(rodata["symbols"][0]),
                "closure_offset": reloc_expected["rodata_offset"],
                "runtime_address": rodata_runtime,
                "runtime_address_hex": f"0x{rodata_runtime:08X}",
            }],
        }
        config = {
            "run_base": 0x1000,
            "preamble_bytes": 0,
            "base": {"size": 0x100},
            "isolated_leaves": [{
                "function": "isolated", "expected": {
                    "size": 2, "sha256": digest(b"IS")
                }, "toolchain": {"reviewed_version": version},
            }],
            "relocated_leaves": [{
                "function": "relocated", "expected": reloc_expected,
                "relocations": relocations,
                "closure": {"text_section": ".text.relocated", "rodata": rodata},
                "toolchain": {"reviewed_version": version},
            }],
            "in_place_leaves": [{
                "function": "in_place", "expected": {
                    "size": 2, "sha256": digest(b"IP")
                }, "toolchain": {"reviewed_version": version},
            }],
            "in_place_data": [{
                "symbol": "data", "expected": {
                    "size": 4, "sha256": digest(b"DATA"), "alignment": 4
                }, "toolchain": {"reviewed_version": version},
            }],
        }
        stage = {
            "isolated_leaves": [{
                "extraction": {"function": "isolated"},
                "pins": copy.deepcopy(config["isolated_leaves"][0]["expected"]),
                "toolchain": {"version": version},
            }],
            "relocated_leaves": [{
                "extraction": {
                    "function": "relocated", "section": ".text.relocated",
                    "rodata": copy.deepcopy(enriched_rodata),
                },
                "pins": {
                    **copy.deepcopy(reloc_expected),
                    "relocations": copy.deepcopy(relocations),
                    "rodata": copy.deepcopy(enriched_rodata),
                },
                "placement": {
                    "alignment": 4,
                    "offset": 8,
                    "padding_before": 0,
                    "runtime_address": text_runtime,
                    "runtime_address_hex": f"0x{text_runtime:08X}",
                    "size": 8,
                    "text_size": 4,
                },
                "toolchain": {"version": version},
            }],
            "in_place_leaves": [{
                "extraction": {"function": "in_place"},
                "pins": copy.deepcopy(config["in_place_leaves"][0]["expected"]),
                "toolchain": {"version": version},
            }],
            "in_place_data": [{
                "extraction": {"symbol": "data"},
                "pins": copy.deepcopy(config["in_place_data"][0]["expected"]),
                "toolchain": {"version": version},
            }],
        }
        admission._require_reviewed_core_leaf_pins(
            config, "apple-clang", {"core_stage": stage}
        )
        mutations = [
            ("isolated_leaves", 0, "pins", "size"),
            ("in_place_leaves", 0, "pins", "sha256"),
            ("in_place_data", 0, "pins", "alignment"),
            ("relocated_leaves", 0, "pins", "offset"),
            ("relocated_leaves", 0, "pins", "unrelocated_sha256"),
            ("relocated_leaves", 0, "pins", "closure_sha256"),
        ]
        for key, index, container, field in mutations:
            changed = copy.deepcopy(stage)
            value = changed[key][index][container][field]
            changed[key][index][container][field] = (
                value + 1 if isinstance(value, int) else digest(field.encode())
            )
            with self.subTest(key=key, field=field):
                with self.assertRaises(admission.AdmissionError):
                    admission._require_reviewed_core_leaf_pins(
                        config, "apple-clang", {"core_stage": changed}
                    )
        changed = copy.deepcopy(stage)
        changed["relocated_leaves"][0]["pins"]["relocations"][0]["offset"] = 2
        with self.assertRaises(admission.AdmissionError):
            admission._require_reviewed_core_leaf_pins(
                config, "apple-clang", {"core_stage": changed}
            )
        invariant_mutations = (
            ("section", ".rodata.changed"),
            ("size", 8),
            ("sha256", digest(b"changed-rodata")),
            ("alignment", 8),
        )
        for field, value in invariant_mutations:
            changed = copy.deepcopy(stage)
            for container in ("pins", "extraction"):
                changed["relocated_leaves"][0][container]["rodata"][field] = value
            with self.subTest(rodata_field=field):
                with self.assertRaises(admission.AdmissionError):
                    admission._require_reviewed_core_leaf_pins(
                        config, "apple-clang", {"core_stage": changed}
                    )
        for field, value in (("name", "other"), ("offset", 1), ("size", 3)):
            changed = copy.deepcopy(stage)
            for container in ("pins", "extraction"):
                changed["relocated_leaves"][0][container]["rodata"]["symbols"][0][
                    field
                ] = value
            with self.subTest(rodata_symbol_field=field):
                with self.assertRaises(admission.AdmissionError):
                    admission._require_reviewed_core_leaf_pins(
                        config, "apple-clang", {"core_stage": changed}
                    )
        for container, field in (
            ("rodata", "offset"),
            ("rodata", "runtime_address"),
            ("symbol", "closure_offset"),
            ("symbol", "runtime_address"),
            ("placement", "offset"),
            ("placement", "runtime_address"),
        ):
            changed = copy.deepcopy(stage)
            leaf = changed["relocated_leaves"][0]
            if container == "placement":
                leaf["placement"][field] += 1
            elif container == "symbol":
                for receipt in (leaf["pins"], leaf["extraction"]):
                    receipt["rodata"]["symbols"][0][field] += 1
            else:
                for receipt in (leaf["pins"], leaf["extraction"]):
                    receipt["rodata"][field] += 1
            with self.subTest(derived_container=container, derived_field=field):
                with self.assertRaises(admission.AdmissionError):
                    admission._require_reviewed_core_leaf_pins(
                        config, "apple-clang", {"core_stage": changed}
                    )
        changed = copy.deepcopy(stage)
        changed["relocated_leaves"][0]["pins"]["unknown"] = 1
        with self.assertRaisesRegex(admission.AdmissionError, "fields changed"):
            admission._require_reviewed_core_leaf_pins(
                config, "apple-clang", {"core_stage": changed}
            )

    def test_three_file_update_rolls_back_on_third_write_failure(self):
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            root = Path(temporary)
            config_path = root / "config.json"
            manifest_path = root / "manifest.json"
            provider_path = root / "provider.bin"
            config_path.write_text('{"old":"config"}\n', encoding="utf-8")
            manifest_path.write_text('{"old":"manifest"}\n', encoding="utf-8")
            provider_path.write_bytes(b"old-provider")
            original_atomic = admission._atomic_write_publication
            calls = 0

            def fail_third(*arguments, **keywords):
                nonlocal calls
                calls += 1
                if calls == 3:
                    raise OSError("injected third write failure")
                return original_atomic(*arguments, **keywords)

            with mock.patch.object(
                admission, "_atomic_write_publication", side_effect=fail_third
            ):
                with self.assertRaises(OSError):
                    admission._atomic_generation(
                        config_path,
                        {"new": "config"},
                        manifest_path,
                        {"new": "manifest"},
                        provider_path,
                        b"new-provider",
                    )
            self.assertEqual(config_path.read_text(), '{"old":"config"}\n')
            self.assertEqual(manifest_path.read_text(), '{"old":"manifest"}\n')
            self.assertEqual(provider_path.read_bytes(), b"old-provider")

    def test_live_report_normalizes_paths_and_removes_observation_receipt(self):
        overlay_payload = b"new-overlay"
        provider_payload = b"new-provider"
        overlay_path = G2_ROOT / "tmp-live-report" / "apollo_core_overlay.bin"
        provider_path = G2_ROOT / "tmp-live-report" / "ota_s200_firmware_ota.bin"
        admitted = {
            "artifacts": {
                "overlay": overlay_payload,
                "component": provider_payload,
            },
            "report": {
                "canonical_observation": {"complete": True},
                "overlay": {
                    "artifact": "observation/apollo_core_overlay.bin",
                    "size": len(overlay_payload),
                    "sha256": admission._digest(overlay_payload),
                },
                "component": {
                    "artifact": "observation/ota_s200_firmware_ota.bin",
                    "size": len(provider_payload),
                    "sha256": admission._digest(provider_payload),
                },
            },
        }
        normalized = json.loads(admission._canonical_live_report(
            admitted, overlay_path, provider_path
        ))
        self.assertNotIn("canonical_observation", normalized)
        self.assertEqual(
            normalized["overlay"]["artifact"],
            "tmp-live-report/apollo_core_overlay.bin",
        )
        self.assertEqual(
            normalized["component"]["artifact"],
            "tmp-live-report/ota_s200_firmware_ota.bin",
        )

    def test_five_file_generation_rolls_back_on_manifest_failure(self):
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            root = Path(temporary)
            config_path = root / "config.json"
            manifest_path = root / "manifest.json"
            provider_path = root / "provider.bin"
            overlay_path = root / "overlay.bin"
            report_path = root / "build-report.json"
            original = {
                config_path: b'{"old":"config"}\n',
                manifest_path: b'{"old":"manifest"}\n',
                provider_path: b"old-provider",
                overlay_path: b"old-overlay",
                report_path: b"old-report",
            }
            for path, payload in original.items():
                path.write_bytes(payload)
            original_atomic = admission._atomic_write_publication
            calls = 0

            def fail_manifest(*arguments, **keywords):
                nonlocal calls
                calls += 1
                if calls == 5:
                    raise OSError("injected manifest write failure")
                return original_atomic(*arguments, **keywords)

            with mock.patch.object(
                admission, "_atomic_write_publication", side_effect=fail_manifest
            ):
                with self.assertRaisesRegex(OSError, "manifest write failure"):
                    admission._atomic_generation(
                        config_path,
                        {"new": "config"},
                        manifest_path,
                        {"new": "manifest"},
                        provider_path,
                        b"new-provider",
                        overlay_path=overlay_path,
                        overlay_payload=b"new-overlay",
                        expected_overlay_payload=b"old-overlay",
                        report_path=report_path,
                        report_payload=b"new-report",
                        expected_report_payload=b"old-report",
                    )
            for path, payload in original.items():
                self.assertEqual(path.read_bytes(), payload)

    def test_five_file_generation_rejects_stale_report_before_mutation(self):
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            root = Path(temporary)
            config_path = root / "config.json"
            manifest_path = root / "manifest.json"
            provider_path = root / "provider.bin"
            overlay_path = root / "overlay.bin"
            report_path = root / "build-report.json"
            original = {
                config_path: b'{"old":"config"}\n',
                manifest_path: b'{"old":"manifest"}\n',
                provider_path: b"old-provider",
                overlay_path: b"old-overlay",
                report_path: b"concurrent-report",
            }
            for path, payload in original.items():
                path.write_bytes(payload)
            with self.assertRaisesRegex(
                admission.AdmissionError,
                "publication inputs changed during admission",
            ):
                admission._atomic_generation(
                    config_path,
                    {"new": "config"},
                    manifest_path,
                    {"new": "manifest"},
                    provider_path,
                    b"new-provider",
                    overlay_path=overlay_path,
                    overlay_payload=b"new-overlay",
                    expected_overlay_payload=b"old-overlay",
                    report_path=report_path,
                    report_payload=b"new-report",
                    expected_report_payload=b"old-report",
                )
            for path, payload in original.items():
                self.assertEqual(path.read_bytes(), payload)

    def test_three_file_update_rolls_back_on_readback_failure(self):
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            root = Path(temporary)
            config_path = root / "config.json"
            manifest_path = root / "manifest.json"
            provider_path = root / "provider.bin"
            config_path.write_text('{"old":"config"}\n', encoding="utf-8")
            manifest_path.write_text('{"old":"manifest"}\n', encoding="utf-8")
            provider_path.write_bytes(b"old-provider")
            original_read = admission._read_publication_file
            corrupted = False

            def corrupt_readback(directory_fd, name, role):
                nonlocal corrupted
                payload, identity = original_read(directory_fd, name, role)
                if (
                    not corrupted
                    and role == "canonical publication output"
                    and name == provider_path.name
                ):
                    corrupted = True
                    return b"forged-readback", identity
                return payload, identity

            with mock.patch.object(
                admission, "_read_publication_file", side_effect=corrupt_readback
            ):
                with self.assertRaisesRegex(
                    admission.AdmissionError, "readback changed"
                ):
                    admission._atomic_generation(
                        config_path,
                        {"new": "config"},
                        manifest_path,
                        {"new": "manifest"},
                        provider_path,
                        b"new-provider",
                    )
            self.assertEqual(config_path.read_text(), '{"old":"config"}\n')
            self.assertEqual(manifest_path.read_text(), '{"old":"manifest"}\n')
            self.assertEqual(provider_path.read_bytes(), b"old-provider")

    def test_conditional_rollback_preserves_concurrent_edit(self):
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            root = Path(temporary)
            config_path = root / "config.json"
            manifest_path = root / "manifest.json"
            provider_path = root / "provider.bin"
            config_path.write_text('{"old":"config"}\n', encoding="utf-8")
            manifest_path.write_text('{"old":"manifest"}\n', encoding="utf-8")
            provider_path.write_bytes(b"old-provider")
            original_atomic = admission._atomic_write_publication
            calls = 0

            def concurrent_third_write(*arguments, **keywords):
                nonlocal calls
                calls += 1
                if calls == 3:
                    provider_path.write_bytes(b"third-party-edit")
                    raise OSError("injected manifest publication failure")
                return original_atomic(*arguments, **keywords)

            with mock.patch.object(
                admission,
                "_atomic_write_publication",
                side_effect=concurrent_third_write,
            ):
                with self.assertRaisesRegex(
                    admission.AdmissionError, "conditional rollback refused"
                ):
                    admission._atomic_generation(
                        config_path,
                        {"new": "config"},
                        manifest_path,
                        {"new": "manifest"},
                        provider_path,
                        b"new-provider",
                    )
            self.assertEqual(config_path.read_text(), '{"old":"config"}\n')
            self.assertEqual(manifest_path.read_text(), '{"old":"manifest"}\n')
            self.assertEqual(provider_path.read_bytes(), b"third-party-edit")

    @staticmethod
    def publication_fixture(root: Path):
        config_dir = root / "config"
        manifest_dir = root / "manifest"
        provider_dir = root / "provider"
        for directory in (config_dir, manifest_dir, provider_dir):
            directory.mkdir()
        config_path = config_dir / "config.json"
        manifest_path = manifest_dir / "manifest.json"
        provider_path = provider_dir / "provider.bin"
        config_path.write_bytes(b'{"old":"config"}\n')
        manifest_path.write_bytes(b'{"old":"manifest"}\n')
        provider_path.write_bytes(b"old-provider")
        return config_path, manifest_path, provider_path

    def test_descriptor_relative_publication_succeeds_and_cleans_temporaries(self):
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            root = Path(temporary)
            config_path, manifest_path, provider_path = self.publication_fixture(root)
            paths = (config_path, manifest_path, provider_path)
            modes = (0o640, 0o600, 0o644)
            for path, mode in zip(paths, modes):
                path.chmod(mode)
            old_inodes = tuple(path.stat().st_ino for path in paths)
            admission._atomic_generation(
                config_path,
                {"new": "config"},
                manifest_path,
                {"new": "manifest"},
                provider_path,
                b"new-provider",
            )
            self.assertEqual(config_path.read_bytes(), b'{\n  "new": "config"\n}\n')
            self.assertEqual(
                manifest_path.read_bytes(), b'{\n  "new": "manifest"\n}\n'
            )
            self.assertEqual(provider_path.read_bytes(), b"new-provider")
            self.assertTrue(all(
                path.stat().st_ino != old_inode
                for path, old_inode in zip(paths, old_inodes)
            ))
            self.assertEqual(
                tuple(path.stat().st_mode & 0o777 for path in paths), modes
            )
            self.assertFalse(any(
                item.name.startswith(f".{path.name}.")
                for path in paths
                for item in path.parent.iterdir()
            ))

    def test_publication_rejects_outside_targets_before_mutation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config_path = root / "config.json"
            manifest_path = root / "manifest.json"
            provider_path = root / "provider.bin"
            config_path.write_bytes(b'{"old":"config"}\n')
            manifest_path.write_bytes(b'{"old":"manifest"}\n')
            provider_path.write_bytes(b"old-provider")
            with self.assertRaisesRegex(
                admission.AdmissionError, "not strictly below the G2 tree"
            ):
                admission._atomic_generation(
                    config_path,
                    {"new": "config"},
                    manifest_path,
                    {"new": "manifest"},
                    provider_path,
                    b"new-provider",
                )
            self.assertEqual(config_path.read_bytes(), b'{"old":"config"}\n')
            self.assertEqual(manifest_path.read_bytes(), b'{"old":"manifest"}\n')
            self.assertEqual(provider_path.read_bytes(), b"old-provider")

    def test_publication_rejects_mixed_outside_root_and_traversal_targets(self):
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as inside, \
                tempfile.TemporaryDirectory() as outside:
            config_path, manifest_path, provider_path = self.publication_fixture(
                Path(inside)
            )
            outside_provider = Path(outside) / "provider.bin"
            outside_provider.write_bytes(b"outside-provider")
            for invalid in (
                outside_provider,
                G2_ROOT,
                G2_ROOT / "root-parent-target.json",
                G2_ROOT / "nested" / ".." / ".." / "outside-target.json",
            ):
                with self.subTest(invalid=invalid):
                    with self.assertRaisesRegex(
                        admission.AdmissionError,
                        "not strictly below the G2 tree|absolute and normalized",
                    ):
                        admission._atomic_generation(
                            config_path,
                            {"new": "config"},
                            manifest_path,
                            {"new": "manifest"},
                            invalid,
                            b"new-provider",
                        )
                    self.assertEqual(
                        config_path.read_bytes(), b'{"old":"config"}\n'
                    )
                    self.assertEqual(
                        manifest_path.read_bytes(), b'{"old":"manifest"}\n'
                    )
                    self.assertEqual(provider_path.read_bytes(), b"old-provider")
                    self.assertEqual(
                        outside_provider.read_bytes(), b"outside-provider"
                    )
                    self.assertFalse((G2_ROOT / "root-parent-target.json").exists())

            nested = provider_path.parent / "nested"
            nested.mkdir()
            in_tree_traversal = nested / ".." / provider_path.name
            with self.assertRaisesRegex(
                admission.AdmissionError, "absolute and normalized"
            ):
                admission._atomic_generation(
                    config_path,
                    {"new": "config"},
                    manifest_path,
                    {"new": "manifest"},
                    in_tree_traversal,
                    b"new-provider",
                )
            self.assertEqual(config_path.read_bytes(), b'{"old":"config"}\n')
            self.assertEqual(manifest_path.read_bytes(), b'{"old":"manifest"}\n')
            self.assertEqual(provider_path.read_bytes(), b"old-provider")

        with tempfile.TemporaryDirectory(dir=G2_ROOT) as inside, \
                tempfile.TemporaryDirectory() as outside:
            config_path, manifest_path, provider_path = self.publication_fixture(
                Path(inside)
            )
            outside_provider = Path(outside) / "provider.bin"
            outside_provider.write_bytes(b"outside-provider")
            provider_path.unlink()
            provider_path.symlink_to(outside_provider)
            with self.assertRaisesRegex(admission.AdmissionError, "contains a symlink"):
                admission._atomic_generation(
                    config_path,
                    {"new": "config"},
                    manifest_path,
                    {"new": "manifest"},
                    provider_path,
                    b"new-provider",
                )
            self.assertEqual(config_path.read_bytes(), b'{"old":"config"}\n')
            self.assertEqual(manifest_path.read_bytes(), b'{"old":"manifest"}\n')
            self.assertEqual(outside_provider.read_bytes(), b"outside-provider")

    def test_publication_rejects_symlink_and_hardlink_targets_without_mutation(self):
        for kind in ("symlink", "hardlink"):
            for role in ("config", "manifest", "provider"):
                with self.subTest(kind=kind, role=role), tempfile.TemporaryDirectory(
                    dir=G2_ROOT
                ) as temporary:
                    root = Path(temporary)
                    config_path, manifest_path, provider_path = (
                        self.publication_fixture(root)
                    )
                    paths = {
                        "config": config_path,
                        "manifest": manifest_path,
                        "provider": provider_path,
                    }
                    selected = paths[role]
                    original = selected.read_bytes()
                    alias = selected.parent / f"{kind}-alias"
                    if kind == "symlink":
                        protected = selected.parent / "protected"
                        selected.rename(protected)
                        selected.symlink_to(protected.name)
                        protected_path = protected
                    else:
                        os.link(selected, alias)
                        protected_path = selected
                    with self.assertRaisesRegex(
                        admission.AdmissionError,
                        "contains a symlink|regular single-link file|cannot read",
                    ):
                        admission._atomic_generation(
                            config_path,
                            {"new": "config"},
                            manifest_path,
                            {"new": "manifest"},
                            provider_path,
                            b"new-provider",
                        )
                    self.assertEqual(protected_path.read_bytes(), original)
                    if kind == "symlink":
                        self.assertTrue(selected.is_symlink())
                    else:
                        self.assertEqual(alias.read_bytes(), original)
                    for name, path in paths.items():
                        if name != role:
                            self.assertEqual(
                                path.read_bytes(),
                                {
                                    "config": b'{"old":"config"}\n',
                                    "manifest": b'{"old":"manifest"}\n',
                                    "provider": b"old-provider",
                                }[name],
                            )
                    self.assertFalse(any(
                        item.name.startswith(".config.json.")
                        or item.name.startswith(".manifest.json.")
                        or item.name.startswith(".provider.bin.")
                        for directory in (
                            config_path.parent,
                            manifest_path.parent,
                            provider_path.parent,
                        )
                        for item in directory.iterdir()
                    ))

    def test_each_publication_phase_rejects_parent_redirection_and_rolls_back(self):
        for phase in ("provider", "config", "manifest"):
            with self.subTest(phase=phase), tempfile.TemporaryDirectory(
                dir=G2_ROOT
            ) as temporary:
                root = Path(temporary)
                config_path, manifest_path, provider_path = (
                    self.publication_fixture(root)
                )
                paths = {
                    "config": config_path,
                    "manifest": manifest_path,
                    "provider": provider_path,
                }
                selected = paths[phase]
                displaced = root / f"{phase}-authenticated"
                redirected = root / f"{phase}-redirected"
                redirected.mkdir()
                redirected_target = redirected / selected.name
                redirected_target.write_bytes(selected.read_bytes())
                real_atomic = admission._atomic_write_publication
                swapped = False

                def redirect_parent(*arguments, **keywords):
                    nonlocal swapped
                    parent = arguments[0]
                    validates_name = keywords.get("validate_named_parent", True)
                    if parent == selected.parent and validates_name and not swapped:
                        swapped = True
                        os.replace(selected.parent, displaced)
                        selected.parent.symlink_to(
                            redirected.name, target_is_directory=True
                        )
                    return real_atomic(*arguments, **keywords)

                with mock.patch.object(
                    admission,
                    "_atomic_write_publication",
                    side_effect=redirect_parent,
                ):
                    with self.assertRaisesRegex(
                        admission.AdmissionError, "publication parent changed"
                    ):
                        admission._atomic_generation(
                            config_path,
                            {"new": "config"},
                            manifest_path,
                            {"new": "manifest"},
                            provider_path,
                            b"new-provider",
                        )
                self.assertTrue(swapped)
                self.assertEqual(
                    (displaced / selected.name).read_bytes(),
                    {
                        "config": b'{"old":"config"}\n',
                        "manifest": b'{"old":"manifest"}\n',
                        "provider": b"old-provider",
                    }[phase],
                )
                self.assertEqual(
                    redirected_target.read_bytes(),
                    {
                        "config": b'{"old":"config"}\n',
                        "manifest": b'{"old":"manifest"}\n',
                        "provider": b"old-provider",
                    }[phase],
                )
                for name, path in paths.items():
                    if name != phase:
                        self.assertEqual(
                            path.read_bytes(),
                            {
                                "config": b'{"old":"config"}\n',
                                "manifest": b'{"old":"manifest"}\n',
                                "provider": b"old-provider",
                            }[name],
                        )

    def test_parent_swap_during_descriptor_relative_replace_cannot_redirect(self):
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            root = Path(temporary)
            config_path, manifest_path, provider_path = self.publication_fixture(root)
            displaced = root / "provider-authenticated"
            redirected = root / "provider-redirected"
            redirected.mkdir()
            redirected_target = redirected / provider_path.name
            redirected_target.write_bytes(b"old-provider")
            real_replace = admission.os.replace
            swapped = False

            def swap_before_replace(source, destination, *arguments, **keywords):
                nonlocal swapped
                if not swapped and keywords.get("src_dir_fd") is not None:
                    swapped = True
                    real_replace(provider_path.parent, displaced)
                    provider_path.parent.symlink_to(
                        redirected.name, target_is_directory=True
                    )
                return real_replace(source, destination, *arguments, **keywords)

            with mock.patch.object(
                admission.os, "replace", side_effect=swap_before_replace
            ):
                with self.assertRaisesRegex(
                    admission.AdmissionError, "publication parent changed"
                ):
                    admission._atomic_generation(
                        config_path,
                        {"new": "config"},
                        manifest_path,
                        {"new": "manifest"},
                        provider_path,
                        b"new-provider",
                    )
            self.assertTrue(swapped)
            self.assertEqual((displaced / provider_path.name).read_bytes(), b"old-provider")
            self.assertEqual(redirected_target.read_bytes(), b"old-provider")
            self.assertEqual(config_path.read_bytes(), b'{"old":"config"}\n')
            self.assertEqual(manifest_path.read_bytes(), b'{"old":"manifest"}\n')

    def test_rollback_uses_held_parent_after_parent_redirection(self):
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            root = Path(temporary)
            config_path, manifest_path, provider_path = self.publication_fixture(root)
            displaced = root / "config-authenticated"
            redirected = root / "config-redirected"
            redirected.mkdir()
            redirected_target = redirected / config_path.name
            redirected_target.write_bytes(b"outside-unchanged")
            real_atomic = admission._atomic_write_publication
            swapped = False

            def fail_manifest_then_redirect_rollback(*arguments, **keywords):
                nonlocal swapped
                parent = arguments[0]
                validates_name = keywords.get("validate_named_parent", True)
                if validates_name and parent == manifest_path.parent:
                    raise OSError("injected manifest write failure")
                if not validates_name and parent == config_path.parent and not swapped:
                    swapped = True
                    os.replace(config_path.parent, displaced)
                    config_path.parent.symlink_to(
                        redirected.name, target_is_directory=True
                    )
                return real_atomic(*arguments, **keywords)

            with mock.patch.object(
                admission,
                "_atomic_write_publication",
                side_effect=fail_manifest_then_redirect_rollback,
            ):
                with self.assertRaisesRegex(OSError, "manifest write failure"):
                    admission._atomic_generation(
                        config_path,
                        {"new": "config"},
                        manifest_path,
                        {"new": "manifest"},
                        provider_path,
                        b"new-provider",
                    )
            self.assertTrue(swapped)
            self.assertEqual(
                (displaced / config_path.name).read_bytes(), b'{"old":"config"}\n'
            )
            self.assertEqual(redirected_target.read_bytes(), b"outside-unchanged")
            self.assertEqual(manifest_path.read_bytes(), b'{"old":"manifest"}\n')
            self.assertEqual(provider_path.read_bytes(), b"old-provider")
            for directory in (displaced, redirected, manifest_path.parent, provider_path.parent):
                self.assertFalse(any(
                    item.name.startswith(".config.json.")
                    or item.name.startswith(".manifest.json.")
                    or item.name.startswith(".provider.bin.")
                    for item in directory.iterdir()
                ))

    def test_current_snapshot_rejects_concurrent_semantic_config_edit(self):
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            config_path = Path(temporary) / "config.json"
            initial = {"source": {"path": "tools/open_cfw.py"}}
            initial_payload = json.dumps(initial).encode()
            config_path.write_bytes(initial_payload)
            _payload, _config, expected = core_builder._canonical_input_state(
                G2_ROOT, config_path
            )
            config_path.write_text(
                json.dumps({"source": {"path": "tools/apollo_overlay.py"}}),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                core_builder.BuildError, "inputs changed during build"
            ):
                core_builder._require_canonical_inputs_unchanged(
                    G2_ROOT, config_path, initial, expected
                )
            with mock.patch.object(admission, "PROJECT_ROOT", G2_ROOT):
                with self.assertRaisesRegex(
                    admission.AdmissionError, "config changed during admission"
                ):
                    admission._current_input_state(
                        core_builder, config_path, initial_payload
                    )

    def test_live_provider_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            real = root / "real.bin"
            link = root / "live.bin"
            real.write_bytes(b"old")
            link.symlink_to(real)
            raw = {
                "component_overrides": {
                    "apollo_main": {"provider": {"path": "live.bin"}}
                }
            }
            with mock.patch.object(admission, "PROJECT_ROOT", root):
                with self.assertRaisesRegex(
                    admission.AdmissionError, "contains a symlink"
                ):
                    admission._apollo_provider_path(raw)

    def test_admission_lock_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            parent = root / "components/apollo_main/core_overlay"
            parent.mkdir(parents=True)
            elsewhere = root / "elsewhere"
            elsewhere.mkdir()
            (parent / "build").symlink_to(elsewhere, target_is_directory=True)
            with mock.patch.object(admission, "PROJECT_ROOT", root):
                with self.assertRaisesRegex(
                    admission.AdmissionError, "lock directory contains a symlink"
                ):
                    with admission._admission_lock():
                        self.fail("unsafe lock unexpectedly acquired")

    def test_admission_lock_hardlink_and_replacement_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            lock_dir = root / "components/apollo_main/core_overlay/build"
            lock_dir.mkdir(parents=True)
            lock_path = lock_dir / ".open-cfw-canonical-admission.lock"
            lock_path.write_bytes(b"")
            hardlink = lock_dir / "second-lock-name"
            os.link(lock_path, hardlink)
            with mock.patch.object(admission, "PROJECT_ROOT", root):
                with self.assertRaisesRegex(
                    admission.AdmissionError, "multiple lock domains"
                ):
                    with admission._admission_lock():
                        self.fail("hardlinked lock unexpectedly acquired")
            hardlink.unlink()
            with mock.patch.object(admission, "PROJECT_ROOT", root):
                with self.assertRaisesRegex(
                    admission.AdmissionError, "multiple lock domains"
                ):
                    with admission._admission_lock():
                        displaced = lock_dir / "displaced-lock"
                        os.replace(lock_path, displaced)
                        lock_path.write_bytes(b"replacement")

    def test_admission_lock_parent_swap_cannot_redirect_lock_domain(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            lock_dir = root / "components/apollo_main/core_overlay/build"
            lock_dir.mkdir(parents=True)
            redirected = root / "redirected-lock-domain"
            redirected.mkdir()
            displaced = lock_dir.with_name("displaced-build")
            original_open = os.open
            swapped = False

            def swap_parent(path, flags, mode=0o777, *, dir_fd=None):
                nonlocal swapped
                if (
                    path == ".open-cfw-canonical-admission.lock"
                    and dir_fd is not None
                    and not swapped
                ):
                    swapped = True
                    lock_dir.rename(displaced)
                    lock_dir.symlink_to(redirected, target_is_directory=True)
                return original_open(path, flags, mode, dir_fd=dir_fd)

            with mock.patch.object(admission, "PROJECT_ROOT", root), \
                    mock.patch.object(admission.os, "open", side_effect=swap_parent):
                with self.assertRaisesRegex(
                    admission.AdmissionError, "lock directory changed"
                ):
                    with admission._admission_lock():
                        self.fail("redirected lock domain unexpectedly acquired")
            self.assertFalse(
                (redirected / ".open-cfw-canonical-admission.lock").exists()
            )

    def test_inherited_manifest_and_provider_snapshot_detects_drift(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifests = root / "manifests"
            manifests.mkdir()
            provider = root / "provider.bin"
            provider.write_bytes(b"provider-one")
            parent_path = manifests / "base.json"
            parent = {
                "components": [
                    {
                        "name": "apollo_bootloader",
                        "provider": {"path": "provider.bin"},
                    }
                ]
            }
            parent_path.write_text(json.dumps(parent), encoding="utf-8")
            child_path = manifests / "child.json"
            child = {"extends": "base.json"}
            child_path.write_text(json.dumps(child), encoding="utf-8")
            with mock.patch.object(admission, "PROJECT_ROOT", root):
                first = admission._dependency_snapshot(child_path, child)
                provider.write_bytes(b"provider-two")
                second = admission._dependency_snapshot(child_path, child)
                self.assertFalse(admission._same_dependencies(first, second))
                provider.write_bytes(b"provider-one")
                parent["sentinel"] = True
                parent_path.write_text(json.dumps(parent), encoding="utf-8")
                third = admission._dependency_snapshot(child_path, child)
                self.assertFalse(admission._same_dependencies(first, third))

    def test_manifest_verification_accepts_stale_live_apple_provider(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "live.bin").write_bytes(b"stale-live-provider")
            donor = b"DONOR"
            (root / "donor.bin").write_bytes(donor)
            raw = {
                "component_overrides": {
                    "apollo_main": {
                        "source_appended_boundary": len(donor),
                        "provider": {
                            "kind": "source_build",
                            "path": "live.bin",
                            "size": 1,
                            "sha256": digest(b"x"),
                            "profiles": {"linux-clang": {}},
                        },
                        "regions": [],
                    }
                },
                "package": {"profiles": {"linux-clang": {}}},
            }
            config = {
                "base": {
                    "path": "donor.bin",
                    "size": len(donor),
                    "sha256": digest(donor),
                }
            }
            apple = {
                "observation": {},
                "artifacts": {"component": b"APPLE"},
                "intermediate_artifacts": {
                    "core_stage_component": b"CORE",
                    "liblc3_component": b"LIBLC3",
                },
            }
            linux = {
                "observation": {},
                "artifacts": {"component": b"LINUX"},
                "intermediate_artifacts": {
                    "core_stage_component": b"LINUX-CORE",
                    "liblc3_component": b"LINUX-LIBLC3",
                },
            }

            with (
                mock.patch.object(admission, "PROJECT_ROOT", root),
                mock.patch.object(
                    admission, "synchronize_apollo_regions", return_value=[]
                ),
                mock.patch.object(
                    admission, "_linux_profile_region_replacements", return_value=[]
                ),
                mock.patch.object(admission, "_merged_manifest", return_value={}),
                mock.patch.object(
                    admission,
                    "select_profile_payloads",
                    side_effect=(
                        {"apollo_main": b"APPLE"},
                        {"apollo_main": b"LINUX"},
                    ),
                ),
                mock.patch.object(
                    admission, "_assemble_validated_package", return_value=b"PKG"
                ),
                mock.patch.object(admission, "_validate_pt_contract"),
            ):
                updated = admission.synchronize_manifest(
                    raw,
                    root / "manifest.json",
                    config,
                    apple,
                    linux,
                    {},
                    {"inheritance": {}, "providers": {}},
                )
            provider = updated["component_overrides"]["apollo_main"]["provider"]
            self.assertEqual(provider["sha256"], digest(b"APPLE"))
            self.assertEqual((root / "live.bin").read_bytes(), b"stale-live-provider")

    def test_pt_fixed_interval_legacy_ingress_and_section_contract_is_strict(self):
        config = {
            "run_base": 0,
            "preamble_bytes": 0,
            "base": {"size": 100},
            "patch_sites": [{
                "branch": "b_w",
                "expected_sha256": (
                    "8cf6dda5fc9dd79b3f28467c08eb9272255de756ecddfaccbec74399e53cc2d1"
                ),
                "expected_size": 750,
                "name": "replace_box_uart_mgr_05",
                "profiles": ["apple-clang"],
                "runtime_address": admission.PT_SOURCE_UART_ENTRY_REDIRECT,
                "target_function": "open_cfw_box_uart_handle",
            }],
            "post_link_providers": {
                "pt_protocol": {
                    "license": admission.PT_AGGREGATE_LICENSE,
                    "sources": reviewed_pt_sources(),
                    "placement": {
                        "runtime_start": 180,
                        "runtime_end_exclusive": 260,
                        "capacity": 80,
                    },
                    "legacy_ingress": {
                        "entry": admission.PT_LEGACY_ENTRY,
                        "postprocess": admission.PT_LEGACY_POSTPROCESS,
                    },
                    "hardware": {
                        "validation": "blocked by unavailable physical evidence",
                        "qualification_complete": False,
                    },
                }
            },
            "relocated_leaves": [{
                "function": "open_cfw_box_uart_handle",
                "profiles": ["apple-clang"],
                "strict_relocation_contract": True,
                "expected": {
                    "size": 158,
                    "sha256": "pending",
                    "unrelocated_sha256": digest(b"u"),
                    "alignment": 4,
                    "offset": 1000,
                },
                "relocations": [
                    {
                        "symbol": "open_cfw_retained_box_uart_product_test",
                        "type": "R_ARM_THM_CALL",
                        "target_address": admission.PT_LEGACY_ENTRY,
                        "offset": 88,
                    },
                    {
                        "symbol": "open_cfw_retained_box_uart_execute",
                        "type": "R_ARM_THM_CALL",
                        "target_address": admission.PT_LEGACY_POSTPROCESS,
                        "offset": 148,
                    },
                ],
            }],
        }
        leaf_runtime = (
            config["run_base"] + config["base"]["size"] + 1000
            - config["preamble_bytes"]
        )
        self.assertEqual(
            0x00438000 + 3523396 + 264028 - 32,
            0x007D4A80,
        )
        component = bytearray(b"\0" * (admission.PT_LEGACY_POSTPROCESS + 8))
        site_specs = (
            (
                admission.PT_STOCK_DIRECT_SITE, admission.PT_LEGACY_ENTRY,
                "stock_direct_call", "open_cfw_pt_protocol_legacy_entry",
                admission.PT_DONOR_INGRESS_EVIDENCE,
            ),
            (
                leaf_runtime + 88, admission.PT_LEGACY_ENTRY,
                "source_uart_relocation", "open_cfw_pt_protocol_legacy_entry",
                admission.PT_SOURCE_UART_EVIDENCE,
            ),
            (
                leaf_runtime + 148, admission.PT_LEGACY_POSTPROCESS,
                "source_uart_relocation",
                "open_cfw_pt_protocol_legacy_postprocess",
                admission.PT_SOURCE_UART_EVIDENCE,
            ),
        )
        ingress = []
        for runtime, target, route, function, evidence in site_specs:
            encoded = apollo_overlay.encode_thumb_branch(runtime, target, link=True)
            component[runtime:runtime + 4] = encoded
            ingress.append({
                "runtime_address": runtime,
                "target_address": target,
                "target_function": function,
                "route": route,
                "evidence": evidence,
                "authenticated_size": 4,
                "authenticated_sha256": digest(encoded),
            })
        component[
            admission.PT_SOURCE_UART_ENTRY_REDIRECT:
            admission.PT_SOURCE_UART_ENTRY_REDIRECT + 4
        ] = apollo_overlay.encode_thumb_branch(
            admission.PT_SOURCE_UART_ENTRY_REDIRECT, leaf_runtime, link=False
        )
        for retired in admission.PT_RETIRED_SOURCE_UART_SITES:
            component[retired:retired + 4] = admission.PT_THUMB_NOP_PAIR
        leaf = bytes(component[leaf_runtime:leaf_runtime + 158])
        config["relocated_leaves"][0]["expected"]["sha256"] = digest(leaf)
        ingress[0]["authenticated_sha256"] = (
            admission.PT_DONOR_INGRESS_SHA256[admission.PT_STOCK_DIRECT_SITE]
        )
        # The reviewed donor digest is exact, so use its canonical instruction.
        self.assertEqual(
            digest(component[
                admission.PT_STOCK_DIRECT_SITE:
                admission.PT_STOCK_DIRECT_SITE + 4
            ]),
            ingress[0]["authenticated_sha256"],
        )
        component = bytes(component)
        sections = {
            ".pt_legacy_entry": {
                "runtime_address": admission.PT_LEGACY_ENTRY, "size": 4,
                "sha256": digest(component[
                    admission.PT_LEGACY_ENTRY:admission.PT_LEGACY_ENTRY + 4
                ]),
            },
            ".pt_legacy_postprocess": {
                "runtime_address": admission.PT_LEGACY_POSTPROCESS, "size": 4,
                "sha256": digest(component[
                    admission.PT_LEGACY_POSTPROCESS:
                    admission.PT_LEGACY_POSTPROCESS + 4
                ]),
            },
            ".text": {
                "runtime_address": admission.PT_LEGACY_POSTPROCESS + 4, "size": 4,
                "sha256": digest(component[
                    admission.PT_LEGACY_POSTPROCESS + 4:
                    admission.PT_LEGACY_POSTPROCESS + 8
                ]),
            },
        }
        source_payload = b"".join(
            component[item["runtime_address"]:item["runtime_address"] + item["size"]]
            for item in sections.values()
        )
        observation = {
            "image_mapping": {
                "base_size": 100, "run_base": 0, "preamble_bytes": 0,
            },
            "final": {
                "component_size": len(component),
                "component_sha256": digest(component),
            },
            "core_stage": {
                "expected": {
                    "component_size": len(component),
                    "component_sha256": digest(component),
                    "overlay_size": len(component) - 100,
                    "overlay_sha256": digest(component[100:]),
                },
                "relocated_leaves": [{
                    "extraction": {"function": "open_cfw_box_uart_handle"},
                    "pins": {
                        "size": 158,
                        "sha256": digest(leaf),
                        "unrelocated_sha256": digest(b"u"),
                        "alignment": 4,
                        "offset": 1000,
                    },
                }],
            },
            "liblc3_ltpf": {
                "component_size": len(component),
                "component_sha256": digest(component),
            },
            "pt_protocol": {
                "license": admission.PT_AGGREGATE_LICENSE,
                "sources": reviewed_pt_sources(),
                "payload_size": len(source_payload),
                "payload_sha256": digest(source_payload),
                "interval_sha256": digest(component[180:260]),
                "placement": {
                    "runtime_start": 180,
                    "runtime_end_exclusive": 260,
                    "capacity": 80,
                    "linked_start": 200,
                    "linked_end_exclusive": 228,
                    "loadable_size": len(source_payload),
                    "padding_size": 80 - len(source_payload),
                    "writable_bytes": 0,
                    "payload_sha256": digest(source_payload),
                    "interval_sha256": digest(component[180:260]),
                    "sections": sections,
                },
                "source_provider_routes": 40,
                "patch_sites": 0,
                "writable_bytes": 0,
                "hardware": {
                    "validation": "blocked by unavailable physical evidence",
                    "qualification_complete": False,
                },
                "ingress_sites": ingress,
                "source_uart_route_receipt": {
                    "profile": "apple-clang",
                    "strict_relocation_contract": True,
                    "profile_route_active": True,
                    "mode": "source_overlay_relocation",
                    "function": "open_cfw_box_uart_handle",
                    "stage_overlay": {
                        "size": len(component) - 100,
                        "sha256": digest(component[100:]),
                    },
                    "leaf": {
                        "size": 158,
                        "sha256": digest(leaf),
                        "unrelocated_sha256": digest(b"u"),
                        "alignment": 4,
                        "offset": 1000,
                    },
                    "relocations": [
                        {
                            "symbol": "open_cfw_retained_box_uart_product_test",
                            "type": "R_ARM_THM_CALL",
                            "target_address": admission.PT_LEGACY_ENTRY,
                            "offset": 88,
                            "type_id": 10,
                        },
                        {
                            "symbol": "open_cfw_retained_box_uart_execute",
                            "type": "R_ARM_THM_CALL",
                            "target_address": admission.PT_LEGACY_POSTPROCESS,
                            "offset": 148,
                            "type_id": 10,
                        },
                    ],
                },
            }
        }
        admission._validate_pt_contract(
            config, "apple-clang", observation, component, component, component
        )
        mutations = []
        changed = copy.deepcopy(observation)
        changed["pt_protocol"]["placement"]["runtime_end_exclusive"] += 2
        mutations.append(changed)
        changed = copy.deepcopy(observation)
        changed["pt_protocol"]["placement"]["sections"]["../evil"] = (
            changed["pt_protocol"]["placement"]["sections"].pop(".text")
        )
        mutations.append(changed)
        changed = copy.deepcopy(observation)
        changed["pt_protocol"]["placement"]["sections"]
        changed["pt_protocol"]["placement"]["sections"][".pt_legacy_entry"][
            "runtime_address"
        ] += 2
        mutations.append(changed)
        changed = copy.deepcopy(observation)
        changed["pt_protocol"]["ingress_sites"][0]["authenticated_sha256"] = digest(b"x")
        mutations.append(changed)
        changed = copy.deepcopy(observation)
        changed["pt_protocol"]["unknown"] = True
        mutations.append(changed)
        changed = copy.deepcopy(observation)
        changed["pt_protocol"]["hardware"]["qualification_complete"] = True
        mutations.append(changed)
        changed = copy.deepcopy(observation)
        changed["pt_protocol"]["license"] = "BSD-3-Clause"
        mutations.append(changed)
        changed = copy.deepcopy(observation)
        changed["pt_protocol"]["sources"][0]["license"] = "Apache-2.0"
        mutations.append(changed)
        changed = copy.deepcopy(observation)
        changed["pt_protocol"]["source_uart_route_receipt"]["stage_overlay"][
            "sha256"
        ] = digest(b"forged-stage")
        mutations.append(changed)
        changed = copy.deepcopy(observation)
        changed["pt_protocol"]["source_uart_route_receipt"]["leaf"][
            "sha256"
        ] = digest(b"forged-leaf")
        mutations.append(changed)
        for field in ("source_provider_routes", "patch_sites", "writable_bytes"):
            changed = copy.deepcopy(observation)
            changed["pt_protocol"][field] += 1
            mutations.append(changed)
        changed = copy.deepcopy(observation)
        changed["pt_protocol"]["placement"]["payload_sha256"] = digest(
            b"forged-placement"
        )
        mutations.append(changed)
        for relocation_index in range(2):
            changed = copy.deepcopy(observation)
            changed["pt_protocol"]["source_uart_route_receipt"]["relocations"][
                relocation_index
            ]["offset"] += 2
            mutations.append(changed)
        for index, changed in enumerate(mutations):
            with self.subTest(mutation=index):
                with self.assertRaises(admission.AdmissionError):
                    admission._validate_pt_contract(
                        config, "apple-clang", changed, component, component, component
                    )

        active_sites = (leaf_runtime + 88, leaf_runtime + 148)
        for stage_name in ("core", "liblc3", "final"):
            for site in active_sites:
                changed_component = bytearray(component)
                changed_component[site] ^= 1
                stage_components = [component, component, component]
                stage_components[("core", "liblc3", "final").index(stage_name)] = (
                    bytes(changed_component)
                )
                with self.subTest(active_bl_stage=stage_name, site=site):
                    with self.assertRaises(admission.AdmissionError):
                        admission._validate_pt_contract(
                            config, "apple-clang", observation,
                            stage_components[2], stage_components[0], stage_components[1],
                        )

        for site in (
            admission.PT_SOURCE_UART_ENTRY_REDIRECT,
            *admission.PT_RETIRED_SOURCE_UART_SITES,
        ):
            for stage_name in ("core", "liblc3", "final"):
                changed_component = bytearray(component)
                changed_component[site] ^= 1
                stage_components = [component, component, component]
                stage_components[("core", "liblc3", "final").index(stage_name)] = (
                    bytes(changed_component)
                )
                with self.subTest(fixed_site_stage=stage_name, site=site):
                    with self.assertRaises(admission.AdmissionError):
                        admission._validate_pt_contract(
                            config, "apple-clang", observation,
                            stage_components[2], stage_components[0], stage_components[1],
                        )

        for mutation in (
            ("ingress_runtime", lambda value: value["pt_protocol"]["ingress_sites"][1].__setitem__("runtime_address", admission.PT_RETIRED_SOURCE_UART_SITES[0])),
            ("ingress_target", lambda value: value["pt_protocol"]["ingress_sites"][1].__setitem__("target_address", admission.PT_LEGACY_ENTRY + 2)),
            ("ingress_evidence", lambda value: value["pt_protocol"]["ingress_sites"][1].__setitem__("evidence", "unreviewed")),
            ("image_base_bool", lambda value: value["image_mapping"].__setitem__("base_size", True)),
            ("leaf_offset_bool", lambda value: value["pt_protocol"]["source_uart_route_receipt"]["leaf"].__setitem__("offset", True)),
        ):
            name, mutate = mutation
            changed = copy.deepcopy(observation)
            mutate(changed)
            with self.subTest(receipt_mutation=name):
                with self.assertRaises(admission.AdmissionError):
                    admission._validate_pt_contract(
                        config, "apple-clang", changed, component, component, component
                    )

        for field, value in (
            ("strict_relocation_contract", False),
            ("profiles", ["apple-clang", "linux-clang"]),
        ):
            changed_config = copy.deepcopy(config)
            changed_config["relocated_leaves"][0][field] = value
            with self.subTest(config_leaf_field=field):
                with self.assertRaises(admission.AdmissionError):
                    admission._validate_pt_contract(
                        changed_config, "apple-clang", observation,
                        component, component, component,
                    )

        changed_config = copy.deepcopy(config)
        changed_config["patch_sites"][0]["expected_size"] = 748
        with self.assertRaises(admission.AdmissionError):
            admission._validate_pt_contract(
                changed_config, "apple-clang", observation,
                component, component, component,
            )

        changed_config = copy.deepcopy(config)
        changed_observation = copy.deepcopy(observation)
        for value in (
            changed_config["post_link_providers"]["pt_protocol"],
            changed_observation["pt_protocol"],
        ):
            value["sources"][-1]["license"] = "Apache-2.0"
        with self.assertRaisesRegex(
            admission.AdmissionError, "source license"
        ):
            admission._validate_pt_contract(
                changed_config, "apple-clang", changed_observation,
                component, component, component,
            )

        wrong_kind = bytearray(component)
        for site, target in (
            (leaf_runtime + 88, admission.PT_LEGACY_ENTRY),
            (leaf_runtime + 148, admission.PT_LEGACY_POSTPROCESS),
        ):
            wrong_kind[site:site + 4] = apollo_overlay.encode_thumb_branch(
                site, target, link=False
            )
        wrong_kind = bytes(wrong_kind)
        wrong_observation = copy.deepcopy(observation)
        wrong_observation["final"]["component_sha256"] = digest(wrong_kind)
        wrong_observation["core_stage"]["expected"]["component_sha256"] = digest(
            wrong_kind
        )
        wrong_observation["core_stage"]["expected"]["overlay_sha256"] = digest(
            wrong_kind[100:]
        )
        wrong_observation["liblc3_ltpf"]["component_sha256"] = digest(wrong_kind)
        wrong_observation["pt_protocol"]["source_uart_route_receipt"][
            "stage_overlay"
        ]["sha256"] = digest(wrong_kind[100:])
        wrong_leaf = wrong_kind[leaf_runtime:leaf_runtime + 158]
        wrong_observation["pt_protocol"]["source_uart_route_receipt"]["leaf"][
            "sha256"
        ] = digest(wrong_leaf)
        wrong_observation["core_stage"]["relocated_leaves"][0]["pins"][
            "sha256"
        ] = digest(wrong_leaf)
        for index, site in enumerate(active_sites, 1):
            wrong_observation["pt_protocol"]["ingress_sites"][index][
                "authenticated_sha256"
            ] = digest(wrong_kind[site:site + 4])
        wrong_config = copy.deepcopy(config)
        wrong_config["relocated_leaves"][0]["expected"]["sha256"] = digest(
            wrong_leaf
        )
        with self.assertRaises(admission.AdmissionError):
            admission._validate_pt_contract(
                wrong_config, "apple-clang", wrong_observation,
                wrong_kind, wrong_kind, wrong_kind,
            )

        linux_component = bytearray(component)
        linux_sites = (
            (
                admission.PT_STOCK_DIRECT_SITE, admission.PT_LEGACY_ENTRY,
                "stock_direct_call", "open_cfw_pt_protocol_legacy_entry",
            ),
            (
                admission.PT_RETIRED_SOURCE_UART_SITES[0],
                admission.PT_LEGACY_ENTRY, "source_uart_relocation",
                "open_cfw_pt_protocol_legacy_entry",
            ),
            (
                admission.PT_RETIRED_SOURCE_UART_SITES[1],
                admission.PT_LEGACY_POSTPROCESS, "source_uart_relocation",
                "open_cfw_pt_protocol_legacy_postprocess",
            ),
        )
        linux_ingress = []
        for runtime, target, route_name, function in linux_sites:
            encoded = apollo_overlay.encode_thumb_branch(runtime, target, link=True)
            linux_component[runtime:runtime + 4] = encoded
            self.assertEqual(
                digest(encoded), admission.PT_DONOR_INGRESS_SHA256[runtime]
            )
            linux_ingress.append({
                "runtime_address": runtime,
                "target_address": target,
                "target_function": function,
                "route": route_name,
                "evidence": admission.PT_DONOR_INGRESS_EVIDENCE,
                "authenticated_size": 4,
                "authenticated_sha256": digest(encoded),
            })
        linux_component = bytes(linux_component)
        linux_config = copy.deepcopy(config)
        linux_config["base"]["size"] = len(linux_component)
        linux_observation = copy.deepcopy(observation)
        linux_observation["image_mapping"]["base_size"] = len(linux_component)
        linux_observation["final"]["component_sha256"] = digest(linux_component)
        linux_observation["core_stage"]["expected"]["component_sha256"] = digest(
            linux_component
        )
        linux_observation["core_stage"]["expected"]["overlay_size"] = 1
        linux_observation["core_stage"]["expected"]["overlay_sha256"] = digest(
            linux_component[-1:]
        )
        linux_observation["core_stage"]["relocated_leaves"] = []
        linux_observation["liblc3_ltpf"]["component_sha256"] = digest(
            linux_component
        )
        linux_observation["pt_protocol"]["ingress_sites"] = linux_ingress
        linux_route = linux_observation["pt_protocol"]["source_uart_route_receipt"]
        linux_route.update({
            "profile": "linux-clang",
            "profile_route_active": False,
            "mode": "authenticated_donor_direct",
            "stage_overlay": {"size": 1, "sha256": digest(linux_component[-1:])},
        })
        admission._validate_pt_contract(
            linux_config, "linux-clang", linux_observation,
            linux_component, linux_component, linux_component,
        )
        cff_final = linux_component + b"\xff" * 2000
        cff_observation = copy.deepcopy(linux_observation)
        cff_observation["schema_version"] = 3
        cff_observation["final"].update({
            "component_size": len(cff_final),
            "component_sha256": digest(cff_final),
        })
        cff_observation["intermediate_artifacts"] = {
            "pt_component": {
                "artifact": "pt-component.bin",
                "size": len(linux_component),
                "sha256": digest(linux_component),
            },
        }
        admission._validate_pt_contract(
            linux_config, "linux-clang", cff_observation,
            cff_final, linux_component, linux_component, linux_component,
        )
        oversized_pt = linux_component + b"\xff" * 1001
        oversized_observation = copy.deepcopy(cff_observation)
        oversized_observation["intermediate_artifacts"]["pt_component"].update({
            "size": len(oversized_pt),
            "sha256": digest(oversized_pt),
        })
        with self.assertRaisesRegex(
            admission.AdmissionError,
            "Linux component unexpectedly contains Apple source-UART leaf",
        ):
            admission._validate_pt_contract(
                linux_config, "linux-clang", oversized_observation,
                cff_final, linux_component, linux_component, oversized_pt,
            )
        for runtime, _target, _route, _function in linux_sites:
            for stage_index, stage_name in enumerate(("core", "liblc3", "final")):
                changed_stage = bytearray(linux_component)
                changed_stage[runtime] ^= 1
                stages = [linux_component, linux_component, linux_component]
                stages[stage_index] = bytes(changed_stage)
                with self.subTest(linux_drift=stage_name, runtime=runtime):
                    with self.assertRaises(admission.AdmissionError):
                        admission._validate_pt_contract(
                            linux_config, "linux-clang", linux_observation,
                            stages[2], stages[0], stages[1],
                        )


class AuxiliaryProfileProviderTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(dir=G2_ROOT)
        self.root = Path(self.temporary.name)
        self.apple_boot = b"A"
        self.linux_boot = b"LINUX-BOOT"
        self.linux_main = b"LINUX-MAIN"
        (self.root / "boot.bin").write_bytes(self.apple_boot)
        self.manifest = {
            "components": [
                {
                    "name": "apollo_main",
                    "provider": {
                        "kind": "source_build",
                        "path": "main.bin",
                        "size": 1,
                        "sha256": digest(b"M"),
                        "profiles": {
                            "linux-clang": {
                                "size": len(self.linux_main),
                                "sha256": digest(self.linux_main),
                            }
                        },
                    },
                    "regions": [{"file_offset": 0, "size": 1, "output": "m.bin"}],
                },
                {
                    "name": "apollo_bootloader",
                    "provider": {
                        "kind": "source_build",
                        "path": "boot.bin",
                        "size": len(self.apple_boot),
                        "sha256": digest(self.apple_boot),
                        "profiles": {
                            "linux-clang": {
                                "size": len(self.linux_boot),
                                "sha256": digest(self.linux_boot),
                            }
                        },
                    },
                    "regions": [{"file_offset": 0, "size": 1, "output": "b.bin"}],
                },
            ]
        }

    def tearDown(self):
        self.temporary.cleanup()

    def select(self, auxiliary):
        consumed = set()
        with (mock.patch.object(admission, "PROJECT_ROOT", self.root),
              mock.patch.object(admission.open_cfw, "validate_component_payload"),
              mock.patch.object(admission.open_cfw, "validate_region_partition")):
            payloads = admission.select_profile_payloads(
                self.manifest,
                "linux-clang",
                self.linux_main,
                auxiliary,
                consumed,
            )
        return payloads, consumed

    def test_exact_linux_bootloader_auxiliary_succeeds(self):
        path = self.root / "linux-boot.bin"
        path.write_bytes(self.linux_boot)
        with mock.patch.object(admission, "PROJECT_ROOT", self.root):
            auxiliary = admission.load_profile_provider_inputs([
                ("linux-clang", "apollo_bootloader", path)
            ])
        payloads, consumed = self.select(auxiliary)
        self.assertEqual(payloads["apollo_bootloader"], self.linux_boot)
        self.assertEqual(consumed, {("linux-clang", "apollo_bootloader")})

    def test_missing_or_wrong_hash_auxiliary_fails(self):
        with self.assertRaisesRegex(admission.AdmissionError, "explicit auxiliary"):
            self.select({})
        path = self.root / "wrong.bin"
        path.write_bytes(b"WRONG")
        with mock.patch.object(admission, "PROJECT_ROOT", self.root):
            auxiliary = admission.load_profile_provider_inputs([
                ("linux-clang", "apollo_bootloader", path)
            ])
        with self.assertRaisesRegex(admission.AdmissionError, "manifest pins"):
            self.select(auxiliary)

    def test_wrong_profile_or_component_name_fails(self):
        path = self.root / "linux-boot.bin"
        path.write_bytes(self.linux_boot)
        with mock.patch.object(admission, "PROJECT_ROOT", self.root):
            with self.assertRaisesRegex(admission.AdmissionError, "unknown.*profile"):
                admission.load_profile_provider_inputs([
                    ("unknown", "apollo_bootloader", path)
                ])
            auxiliary = admission.load_profile_provider_inputs([
                ("linux-clang", "touch", path)
            ])
        with self.assertRaisesRegex(admission.AdmissionError, "no manifest component"):
            self.select(auxiliary)

    def test_outside_or_symlink_auxiliary_fails(self):
        with tempfile.TemporaryDirectory() as outside:
            outside_path = Path(outside) / "boot.bin"
            outside_path.write_bytes(self.linux_boot)
            with mock.patch.object(admission, "PROJECT_ROOT", self.root):
                with self.assertRaisesRegex(admission.AdmissionError, "escapes"):
                    admission.load_profile_provider_inputs([
                        ("linux-clang", "apollo_bootloader", outside_path)
                    ])
        target = self.root / "linux-boot.bin"
        target.write_bytes(self.linux_boot)
        link = self.root / "linux-boot-link.bin"
        link.symlink_to(target)
        with mock.patch.object(admission, "PROJECT_ROOT", self.root):
            with self.assertRaisesRegex(admission.AdmissionError, "symlink"):
                admission.load_profile_provider_inputs([
                    ("linux-clang", "apollo_bootloader", link)
                ])

    def test_source_boundary_and_release_gate_fail_closed(self):
        override = {"source_appended_boundary": 10}
        admission._preserve_source_appended_boundary(
            override, {"base": {"size": 10}}
        )
        self.assertEqual(override["source_appended_boundary"], 10)
        with self.assertRaisesRegex(admission.AdmissionError, "boundary"):
            admission._preserve_source_appended_boundary(
                {"source_appended_boundary": 9}, {"base": {"size": 10}}
            )
        with mock.patch.object(
            admission.open_cfw,
            "validate_release_manifest",
            side_effect=admission.open_cfw.OpenCFWError("unsafe output"),
        ):
            with self.assertRaisesRegex(admission.open_cfw.OpenCFWError, "unsafe"):
                admission._assemble_validated_package({}, "linux-clang", {})


class ProfileRegionReplacementSchemaTests(unittest.TestCase):
    def component(self, replacements):
        return {
            "name": "test_component",
            "source_appended_boundary": 8,
            "regions": [
                {"name": "a", "file_offset": 0, "size": 2, "output": "a.bin"},
                {"name": "b", "file_offset": 2, "size": 2, "output": "b.bin"},
                {"name": "c", "file_offset": 4, "size": 4, "output": "c.bin"},
                {"name": "tail", "file_offset": 8, "size": 2, "output": "t.bin"},
            ],
            "profile_region_replacements": {"linux-clang": replacements},
        }

    def test_exact_profile_replacement_precedes_coarse_tail(self):
        replacement = {
            "start": 2,
            "end_exclusive": 4,
            "regions": [
                {"name": "linux-b", "file_offset": 2, "size": 2,
                 "output": "linux-b.bin"}
            ],
        }
        regions = admission.open_cfw.effective_component_regions(
            self.component([replacement]), 12, "linux-clang"
        )
        self.assertEqual([row["name"] for row in regions[:3]], ["a", "linux-b", "c"])
        self.assertEqual(regions[-1]["file_offset"], 8)
        self.assertEqual(regions[-1]["size"], 4)

    def test_partial_overlap_duplicate_or_gap_fails(self):
        cases = [
            [{"start": 3, "end_exclusive": 4, "regions": [
                {"file_offset": 3, "size": 1}
            ]}],
            [
                {"start": 2, "end_exclusive": 4, "regions": [
                    {"file_offset": 2, "size": 2}
                ]},
                {"start": 3, "end_exclusive": 4, "regions": [
                    {"file_offset": 3, "size": 1}
                ]},
            ],
            [{"start": 2, "end_exclusive": 4, "regions": [
                {"file_offset": 2, "size": 1}
            ]}],
        ]
        for replacements in cases:
            with self.subTest(replacements=replacements):
                with self.assertRaises(admission.open_cfw.OpenCFWError):
                    admission.open_cfw.effective_component_regions(
                        self.component(replacements), 12, "linux-clang"
                    )


class LegacyTailIdempotenceTests(unittest.TestCase):
    def patches(self):
        return (
            mock.patch.object(admission, "LEGACY_RODATA_ALIASES", {}),
            mock.patch.object(admission, "LEGACY_SPECIAL_RODATA_ALIASES", {}),
            mock.patch.object(admission, "LEGACY_COALESCED_CLOSURE_ALIASES", {}),
            mock.patch.object(admission, "LEGACY_MULTI_OWNER_ALIASES", {}),
            mock.patch.object(
                admission, "LEGACY_RETIRED_ALIGNMENT_ALIASES", {"retired_alignment"}
            ),
        )

    def test_retired_alias_transition_is_idempotent_but_fail_closed(self):
        config = {"run_base": 0x1000, "preamble_bytes": 0}
        segments = [{
            "identity": "leaf", "part": "text", "status": "source_compiled",
            "file_offset": 0x200, "size": 4,
        }]
        legacy = [
            {
                "name": "retired_alignment",
                "address_status": "generated_alignment",
                "file_offset": 0x100,
                "size": 2,
            },
            {
                "name": "leaf_source_text",
                "address_status": "source_compiled",
                "file_offset": 0x102,
                "size": 2,
                "target_address": 0x1102,
            },
        ]
        with self.patches()[0], self.patches()[1], self.patches()[2], \
                self.patches()[3], self.patches()[4]:
            canonical = admission._legacy_compatible_tail(
                legacy, segments, config
            )
            self.assertEqual(canonical, [{
                "name": "leaf_source_text",
                "address_status": "source_compiled",
                "file_offset": 0x200,
                "size": 4,
                "target_address": 0x1200,
            }])
            self.assertEqual(
                admission._legacy_compatible_tail(canonical, segments, config),
                canonical,
            )

            stale_without_retired = copy.deepcopy(legacy[1:])
            with self.assertRaisesRegex(
                admission.AdmissionError, "retired legacy alignment"
            ):
                admission._legacy_compatible_tail(
                    stale_without_retired, segments, config
                )

            wrong_retired = copy.deepcopy(legacy)
            wrong_retired[0]["address_status"] = "source_compiled"
            with self.assertRaisesRegex(
                admission.AdmissionError, "retired legacy alignment"
            ):
                admission._legacy_compatible_tail(wrong_retired, segments, config)

            tampered_canonical = copy.deepcopy(canonical)
            tampered_canonical[0]["target_address"] += 2
            with self.assertRaisesRegex(
                admission.AdmissionError, "retired legacy alignment"
            ):
                admission._legacy_compatible_tail(
                    tampered_canonical, segments, config
                )


class RegionSynchronizationTests(unittest.TestCase):
    def setUp(self):
        for name in (
            "LEGACY_RODATA_ALIASES",
            "LEGACY_SPECIAL_RODATA_ALIASES",
            "LEGACY_COALESCED_CLOSURE_ALIASES",
            "LEGACY_MULTI_OWNER_ALIASES",
            "LEGACY_RETIRED_ALIGNMENT_ALIASES",
        ):
            patcher = mock.patch.object(
                admission,
                name,
                set() if name == "LEGACY_RETIRED_ALIGNMENT_ALIASES" else {},
            )
            patcher.start()
            self.addCleanup(patcher.stop)
        # start = preamble + runtime_start - run_base = 8.  The required
        # 0x3094-byte stock interval therefore ends at 12444.
        self.config = {
            "run_base": admission.IMU_RUNTIME_START - 4,
            "preamble_bytes": 4,
            "base": {"size": 14000},
            "post_link_providers": {
                "liblc3_ltpf": {
                    "profiles": {
                        "apple-clang": {
                            "placement": {
                                "text": {
                                    "file_offset": 12444,
                                    "runtime_address": admission.IMU_RUNTIME_START + 12436,
                                    "capacity": 8,
                                    "expected_sha256": digest(b"\x00\xbf\x00\xbf"),
                                },
                                "rodata": {
                                    "file_offset": 12452,
                                    "runtime_address": admission.IMU_RUNTIME_START + 12444,
                                    "capacity": 8,
                                    "expected_sha256": digest(b"\x00\xbf\x00\xbf"),
                                },
                            }
                        }
                    }
                }
            },
        }
        self.boundary = self.config["base"]["size"]
        donor = bytearray((index % 251 for index in range(self.boundary)))
        donor[12444:12452] = b"DTEXTtxt"
        donor[12452:12460] = b"DRODATAx"
        donor[13000:13016] = b"\xff" * 16
        donor[13002:13004] = b"PE"
        donor[13008:13011] = b"TXT"
        donor[13011:13012] = b"R"
        self.donor = bytes(donor)
        component = bytearray(self.donor)
        component[12444:12448] = b"LTXT"
        component[12448:12452] = b"\x00\xbf\x00\xbf"
        component[12452:12456] = b"LROD"
        component[12456:12460] = b"\x00\xbf\x00\xbf"
        self.component = bytes(component) + b"P" * 4 + b"LL"
        core_component = bytearray(self.component)
        core_component[12444:12460] = b"\x00\xbf" * 8
        self.core_component = bytes(core_component)
        runtime = lambda offset: (
            self.config["run_base"] + offset - self.config["preamble_bytes"]
        )
        pt_sections = {
            ".pt_legacy_entry": {
                "runtime_address": runtime(13002),
                "size": 2,
                "sha256": digest(b"PE"),
            },
            ".text": {
                "runtime_address": runtime(13008),
                "size": 3,
                "sha256": digest(b"TXT"),
            },
            ".rodata": {
                "runtime_address": runtime(13011),
                "size": 1,
                "sha256": digest(b"R"),
            },
        }
        self.observation = {
            "final": {
                "component_size": len(self.component),
                "component_sha256": digest(self.component),
            },
            "core_stage": {
                "expected": {
                    "component_size": len(self.core_component),
                    "overlay_size": 6,
                    "component_sha256": digest(self.core_component),
                    "overlay_sha256": digest(self.core_component[-6:]),
                },
                "isolated_leaves": [
                    {
                        "extraction": {
                            "function": "retained_leaf",
                            "size": 2,
                            "sha256": digest(b"LL"),
                        },
                        "pins": {"size": 2, "sha256": digest(b"LL")},
                        "placement": {
                            "offset": 4,
                            "padding_before": 0,
                            "size": 2,
                        },
                    }
                ],
                "relocated_leaves": [],
            },
            "liblc3_ltpf": {
                "payload_size": 8,
                "payload_sha256": digest(b"LTXTLROD"),
                "component_size": len(self.component),
                "component_sha256": digest(self.component),
                "placement": {
                    "sections": {
                        "text": {
                            "file_offset": 12444,
                            "runtime_address": runtime(12444),
                            "capacity": 8,
                            "size": 4,
                            "sha256": digest(b"LTXT"),
                        },
                        "rodata": {
                            "file_offset": 12452,
                            "runtime_address": runtime(12452),
                            "capacity": 8,
                            "size": 4,
                            "sha256": digest(b"LROD"),
                        },
                    }
                },
            },
            "pt_protocol": {
                "payload_size": 6,
                "payload_sha256": digest(b"PETXTR"),
                "interval_sha256": digest(self.donor[13000:13016]),
                "placement": {
                    "runtime_start": runtime(13000),
                    "runtime_end_exclusive": runtime(13016),
                    "capacity": 16,
                    "loadable_size": 6,
                    "padding_size": 10,
                    "writable_bytes": 0,
                    "linked_start": runtime(13002),
                    "linked_end_exclusive": runtime(13012),
                    "sections": pt_sections,
                },
            },
        }
        start, end = admission._derived_imu_span(self.config)
        self.assertEqual((start, end), (8, 12444))
        self.regions = [
            {
                "name": "before",
                "function": "before",
                "file_offset": 0,
                "size": start,
                "address_status": "official_blob",
                "output": "before.bin",
            },
            {
                "name": "old_imu_redirects",
                "function": "old redirect map",
                "file_offset": start,
                "size": end - start,
                "address_status": "generated_source_entry_replacement",
                "output": "old-imu.bin",
            },
            {
                "name": "liblc3_ltpf_source_text",
                "function": (
                    "Apache-2.0 Google liblc3 v1.1.3 LTPF text closure placed "
                    "in the authenticated reclaimed _fileCmdParse tail"
                ),
                "file_offset": end,
                "size": 4,
                "address_status": "source_compiled",
                "output": (
                    "apollo510b/main-source-liblc3-ltpf-text-0x00445664.bin"
                ),
                "target": "apollo510b_internal_mram",
                "target_address": runtime(end),
            },
            {
                "name": "liblc3_ltpf_text_cave_tail",
                "function": (
                    "Unused generated NOP fill remaining after the bounded "
                    "liblc3 LTPF text closure"
                ),
                "file_offset": end + 4,
                "size": 4,
                "address_status": "generated_alignment",
                "output": "apollo510b/main-source-liblc3-ltpf-text-tail.bin",
                "target": "apollo510b_internal_mram",
                "target_address": runtime(end + 4),
            },
            {
                "name": "liblc3_ltpf_source_rodata",
                "function": (
                    "Apache-2.0 Google liblc3 v1.1.3 LTPF dispatch and filter "
                    "tables placed in the authenticated reclaimed health-detail tail"
                ),
                "file_offset": end + 8,
                "size": 4,
                "address_status": "source_compiled",
                "output": (
                    "apollo510b/main-source-liblc3-ltpf-rodata-0x004fc648.bin"
                ),
                "target": "apollo510b_internal_mram",
                "target_address": runtime(end + 8),
            },
            {
                "name": "liblc3_ltpf_rodata_cave_tail",
                "function": (
                    "Unused generated NOP fill remaining after the bounded "
                    "liblc3 LTPF table closure"
                ),
                "file_offset": end + 12,
                "size": 4,
                "address_status": "generated_alignment",
                "output": "apollo510b/main-source-liblc3-ltpf-rodata-tail.bin",
                "target": "apollo510b_internal_mram",
                "target_address": runtime(end + 12),
            },
            {
                "name": "between",
                "function": "between",
                "file_offset": end + 16,
                "size": 13000 - end - 16,
                "address_status": "official_blob",
                "output": "between.bin",
            },
            {
                "name": "old_pt_interval",
                "function": "old PT map",
                "file_offset": 13000,
                "size": 16,
                "address_status": "generated_padding",
                "output": "old-pt.bin",
            },
            {
                "name": "after_pt",
                "function": "after PT",
                "file_offset": 13016,
                "size": self.boundary - 13016,
                "address_status": "official_blob",
                "output": "after-pt.bin",
                "target_address": runtime(13016),
            },
            {
                "name": "apollo_core_source_overlay",
                "function": "core, and IMU source; pristine TDK ICM45608 1.1.2 transport, FIFO, eDMP, I2CM, MRM, SIF, and GAF implementation",
                "file_offset": self.boundary,
                "size": 4,
                "address_status": "source_compiled",
                "output": "core-0x004a0000.bin",
                "target": "apollo510b_internal_mram",
                "target_address": 1,
            },
            {
                "name": "imu_icm45608_removed_source_text",
                "function": "removed",
                "file_offset": self.boundary + 4,
                "size": 4,
                "address_status": "source_compiled",
                "output": "removed.bin",
                "target": "apollo510b_internal_mram",
                "target_address": 2,
            },
            {
                "name": "retained_leaf_source_text",
                "function": "retained",
                "file_offset": self.boundary + 8,
                "size": 2,
                "address_status": "source_compiled",
                "output": "retained-0x00500000.bin",
                "target": "apollo510b_internal_mram",
                "target_address": 3,
            },
        ]

    def synchronize(self, regions=None):
        return admission.synchronize_apollo_regions(
            self.regions if regions is None else regions,
            self.config,
            self.observation,
            self.donor,
            self.component,
            self.component,
            self.core_component,
            self.component,
        )

    def test_stock_interval_and_dynamic_tail_are_derived(self):
        result = self.synchronize()
        stock = [row for row in result if row["name"] == "apollo_main_stock_imu_donor"]
        self.assertEqual(len(stock), 1)
        self.assertEqual(stock[0]["file_offset"], 8)
        self.assertEqual(stock[0]["size"], admission.IMU_RUNTIME_END - admission.IMU_RUNTIME_START)
        self.assertFalse(any(
            row["name"].startswith("imu_icm45608_") for row in result
        ))
        pt_rows = [
            row for row in result
            if row["name"].startswith("pt_protocol_in_place_")
        ]
        self.assertEqual(
            sum(row["size"] for row in pt_rows
                if row["address_status"].startswith("source_compiled")),
            6,
        )
        self.assertEqual(
            sum(row["size"] for row in pt_rows
                if row["address_status"] == "generated_padding"),
            10,
        )
        self.assertIn("source_compiled_rodata", {
            row["address_status"] for row in pt_rows
        })
        admission._partition(result, len(self.component), "test result")

    def test_duplicate_or_overlap_is_rejected(self):
        regions = copy.deepcopy(self.regions)
        regions[1]["file_offset"] = 0
        with self.assertRaisesRegex(admission.AdmissionError, "duplicate, gap, or overlap"):
            self.synchronize(regions)

    def test_wrong_donor_offset_is_rejected(self):
        regions = copy.deepcopy(self.regions)
        regions[0]["size"] += 1
        regions[1]["file_offset"] += 1
        regions[1]["size"] -= 1
        with self.assertRaisesRegex(admission.AdmissionError, "wrong offset|exactly tile"):
            self.synchronize(regions)

    def test_changed_donor_bytes_are_rejected(self):
        changed = bytearray(self.component)
        changed[8] ^= 1
        with self.assertRaisesRegex(admission.AdmissionError, "donor IMU bytes"):
            admission.synchronize_apollo_regions(
                self.regions,
                self.config,
                self.observation,
                self.donor,
                bytes(changed),
                self.component,
                self.core_component,
                self.component,
            )

    def test_stale_curated_tail_status_is_rejected(self):
        regions = copy.deepcopy(self.regions)
        regions[-1]["address_status"] = "generated_alignment"
        with self.assertRaisesRegex(admission.AdmissionError, "bijectively"):
            self.synchronize(regions)

    def test_duplicate_or_unsafe_leaf_identity_is_rejected(self):
        for identity in ("retained_leaf", "../../escape"):
            observation = copy.deepcopy(self.observation)
            duplicate = copy.deepcopy(
                observation["core_stage"]["isolated_leaves"][0]
            )
            duplicate["extraction"]["function"] = identity
            duplicate["placement"]["offset"] = 5
            observation["core_stage"]["relocated_leaves"].append(duplicate)
            with self.subTest(identity=identity):
                with self.assertRaisesRegex(
                    admission.AdmissionError, "duplicated|safe C symbol"
                ):
                    admission.synchronize_apollo_regions(
                        self.regions,
                        self.config,
                        observation,
                        self.donor,
                        self.component,
                        self.component,
                        self.core_component,
                        self.component,
                    )

    def test_leaf_overlap_is_rejected(self):
        observation = copy.deepcopy(self.observation)
        duplicate = copy.deepcopy(
            observation["core_stage"]["isolated_leaves"][0]
        )
        duplicate["extraction"]["function"] = "other_leaf"
        duplicate["placement"]["offset"] = 5
        observation["core_stage"]["relocated_leaves"].append(duplicate)
        with self.assertRaisesRegex(
            admission.AdmissionError, "duplicate, overlap, or contain a gap"
        ):
            admission.synchronize_apollo_regions(
                self.regions,
                self.config,
                observation,
                self.donor,
                self.component,
                self.component,
                self.core_component,
                self.component,
            )

    def test_leaf_artifact_hash_mismatch_is_rejected(self):
        observation = copy.deepcopy(self.observation)
        observation["core_stage"]["isolated_leaves"][0]["pins"][
            "sha256"
        ] = digest(b"XX")
        observation["core_stage"]["isolated_leaves"][0]["extraction"][
            "sha256"
        ] = digest(b"XX")
        with self.assertRaisesRegex(admission.AdmissionError, "artifact bytes"):
            admission.synchronize_apollo_regions(
                self.regions,
                self.config,
                observation,
                self.donor,
                self.component,
                self.component,
                self.core_component,
                self.component,
            )

    def test_pt_source_sum_mismatch_is_rejected(self):
        observation = copy.deepcopy(self.observation)
        observation["pt_protocol"]["placement"]["loadable_size"] = 7
        observation["pt_protocol"]["placement"]["padding_size"] = 9
        with self.assertRaisesRegex(admission.AdmissionError, "source-section sum"):
            admission.synchronize_apollo_regions(
                self.regions,
                self.config,
                observation,
                self.donor,
                self.component,
                self.component,
                self.component,
                self.component,
            )

    def test_liblc3_cave_status_mismatch_is_rejected(self):
        regions = copy.deepcopy(self.regions)
        next(row for row in regions if row["name"] == "liblc3_ltpf_source_rodata")[
            "address_status"
        ] = "official_blob"
        with self.assertRaisesRegex(admission.AdmissionError, "cave row changed"):
            self.synchronize(regions)

    def test_liblc3_generated_nop_tails_are_stage_bound_and_strict(self):
        def synchronize_liblc3(
            *, regions=None, observation=None, final=None, core=None, liblc3=None
        ):
            return admission._synchronize_liblc3_cave_regions(
                self.regions if regions is None else regions,
                self.config,
                self.observation if observation is None else observation,
                self.component if final is None else final,
                self.core_component if core is None else core,
                self.component if liblc3 is None else liblc3,
            )

        result = synchronize_liblc3()
        tails = [
            row for row in result
            if row["name"] in {
                "liblc3_ltpf_text_cave_tail",
                "liblc3_ltpf_rodata_cave_tail",
            }
        ]
        self.assertEqual(len(tails), 2)
        self.assertEqual(
            {row["address_status"] for row in tails}, {"generated_alignment"}
        )

        for stage in ("core", "liblc3", "final"):
            changed = bytearray(
                self.core_component if stage == "core" else self.component
            )
            changed[12448] = 1
            kwargs = {stage: bytes(changed)}
            observation = copy.deepcopy(self.observation)
            if stage == "core":
                observation["core_stage"]["expected"]["component_sha256"] = digest(
                    bytes(changed)
                )
                kwargs["observation"] = observation
            elif stage == "liblc3":
                observation["liblc3_ltpf"]["component_sha256"] = digest(
                    bytes(changed)
                )
                kwargs["observation"] = observation
            else:
                observation["final"]["component_sha256"] = digest(bytes(changed))
                kwargs["observation"] = observation
            with self.subTest(non_nop_stage=stage):
                with self.assertRaisesRegex(
                    admission.AdmissionError, "Thumb-NOP padding"
                ):
                    synchronize_liblc3(**kwargs)

        regions = copy.deepcopy(self.regions)
        observation = copy.deepcopy(self.observation)
        observation["liblc3_ltpf"]["placement"]["sections"]["text"][
            "capacity"
        ] += 1
        next(row for row in regions if row["name"] == "liblc3_ltpf_text_cave_tail")[
            "size"
        ] += 1
        with self.assertRaises(admission.AdmissionError):
            synchronize_liblc3(regions=regions, observation=observation)

        for field, value in (
            ("file_offset", 12449),
            ("target_address", self.regions[3]["target_address"] + 1),
            ("function", "unreviewed generated bytes"),
            ("address_status", "official_blob"),
        ):
            regions = copy.deepcopy(self.regions)
            tail = next(
                row for row in regions
                if row["name"] == "liblc3_ltpf_text_cave_tail"
            )
            tail[field] = value
            with self.subTest(tail_field=field):
                with self.assertRaisesRegex(
                    admission.AdmissionError, "span/address/ownership"
                ):
                    synchronize_liblc3(regions=regions)

        regions = copy.deepcopy(self.regions)
        next(
            row for row in regions
            if row["name"] == "liblc3_ltpf_rodata_cave_tail"
        )["unexpected"] = True
        with self.assertRaisesRegex(admission.AdmissionError, "fields changed"):
            synchronize_liblc3(regions=regions)

        for stage in ("core", "liblc3", "final"):
            original = self.core_component if stage == "core" else self.component
            changed = bytearray(original)
            changed[12444] ^= 1
            observation = copy.deepcopy(self.observation)
            kwargs = {stage: bytes(changed), "observation": observation}
            if stage == "core":
                observation["core_stage"]["expected"]["component_sha256"] = digest(
                    bytes(changed)
                )
            elif stage == "liblc3":
                observation["liblc3_ltpf"]["component_sha256"] = digest(
                    bytes(changed)
                )
            else:
                observation["final"]["component_sha256"] = digest(bytes(changed))
            with self.subTest(source_stage=stage):
                with self.assertRaises(admission.AdmissionError):
                    synchronize_liblc3(**kwargs)

        for field, value in (
            ("function", "unreviewed source ownership"),
            ("output", "unreviewed.bin"),
            ("target", "external_flash"),
            ("target_address", True),
            ("size", True),
        ):
            regions = copy.deepcopy(self.regions)
            source = next(
                row for row in regions if row["name"] == "liblc3_ltpf_source_text"
            )
            source[field] = value
            with self.subTest(source_metadata=field):
                with self.assertRaises(admission.AdmissionError):
                    synchronize_liblc3(regions=regions)

        regions = copy.deepcopy(self.regions)
        unexpected = copy.deepcopy(regions[2])
        unexpected["name"] = "liblc3_ltpf_unreviewed_source"
        unexpected["output"] = "unreviewed-liblc3.bin"
        regions.append(unexpected)
        with self.assertRaisesRegex(admission.AdmissionError, "unexpected liblc3"):
            synchronize_liblc3(regions=regions)

        observation = copy.deepcopy(self.observation)
        observation["liblc3_ltpf"]["placement"]["sections"]["text"]["size"] = True
        with self.assertRaisesRegex(admission.AdmissionError, "pin is incomplete"):
            synchronize_liblc3(observation=observation)

        observation = copy.deepcopy(self.observation)
        observation["liblc3_ltpf"]["payload_sha256"] = digest(b"wrong ordering")
        with self.assertRaisesRegex(admission.AdmissionError, "reconstruct"):
            synchronize_liblc3(observation=observation)

    def test_linux_liblc3_and_pt_base_attribution_is_profile_exact(self):
        observation = copy.deepcopy(self.observation)
        observation["liblc3_ltpf"] = {
            "payload_size": 2,
            "payload_sha256": digest(b"LL"),
            "placement": {"file_offset": self.boundary + 4},
        }
        linux_component = bytearray(self.component)
        linux_component[12444:12460] = self.donor[12444:12460]
        replacements = admission._linux_profile_region_replacements(
            self.synchronize(),
            self.config,
            observation,
            self.donor,
            bytes(linux_component),
        )
        self.assertEqual(len(replacements), 3)
        cave_rows = [
            item["regions"][0] for item in replacements[:2]
        ]
        self.assertTrue(all(
            row["address_status"] == "official_blob" for row in cave_rows
        ))
        pt_rows = replacements[2]["regions"]
        self.assertEqual(
            sum(row["size"] for row in pt_rows
                if row["address_status"].startswith("source_compiled")),
            6,
        )

    def test_closure_internal_rodata_alignment_is_explicit(self):
        component = b"P" * 108 + b"\x00\x00TEXT\x00\x00RO"
        text_hash = digest(b"TEXT")
        rodata_hash = digest(b"RO")
        closure_hash = digest(b"TEXT\x00\x00RO")
        stage = {
            "expected": {
                "component_size": len(component),
                "component_sha256": digest(component),
                "overlay_size": len(component) - 100,
                "overlay_sha256": digest(component[100:]),
            },
            "isolated_leaves": [],
            "relocated_leaves": [
                {
                    "extraction": {
                        "function": "closure",
                        "size": 4,
                        "sha256": text_hash,
                        "closure_size": 8,
                        "closure_sha256": closure_hash,
                        "rodata": {
                            "offset": 6,
                            "size": 2,
                            "sha256": rodata_hash,
                        },
                    },
                    "pins": {
                        "size": 4,
                        "sha256": text_hash,
                        "closure_size": 8,
                        "closure_sha256": closure_hash,
                        "rodata_offset": 6,
                        "rodata": {
                            "offset": 6,
                            "size": 2,
                            "sha256": rodata_hash,
                        },
                    },
                    "placement": {
                        "offset": 10,
                        "padding_before": 2,
                        "size": 8,
                        "text_size": 4,
                    },
                }
            ],
        }
        self.assertEqual(
            admission._leaf_segments(stage, 100, component),
            [
                {
                    "status": "generated_alignment",
                    "file_offset": 108,
                    "size": 2,
                    "identity": "closure",
                    "kind": "relocated",
                    "part": "alignment_before",
                },
                {
                    "status": "source_compiled",
                    "file_offset": 110,
                    "size": 4,
                    "identity": "closure",
                    "kind": "relocated",
                    "part": "text",
                    "sha256": text_hash,
                },
                {
                    "status": "generated_alignment",
                    "file_offset": 114,
                    "size": 2,
                    "identity": "closure",
                    "kind": "relocated",
                    "part": "alignment_internal",
                },
                {
                    "status": "source_compiled_rodata",
                    "file_offset": 116,
                    "size": 2,
                    "identity": "closure",
                    "kind": "relocated",
                    "part": "rodata",
                    "sha256": rodata_hash,
                },
            ],
        )

    def test_closure_rodata_overlap_or_escape_is_rejected(self):
        component = b"P" * 104 + b"TEXT" + b"RODA"
        text_hash = digest(b"TEXT")
        rodata_hash = digest(b"RODA")
        closure_hash = digest(b"TEXTRODA")
        item = {
            "extraction": {
                "function": "closure",
                "size": 4,
                "sha256": text_hash,
                "closure_size": 8,
                "closure_sha256": closure_hash,
                "rodata": {"offset": 4, "size": 4, "sha256": rodata_hash},
            },
            "pins": {
                "size": 4,
                "sha256": text_hash,
                "closure_size": 8,
                "closure_sha256": closure_hash,
                "rodata_offset": 3,
                "rodata": {"offset": 4, "size": 4, "sha256": rodata_hash},
            },
            "placement": {
                "offset": 4,
                "padding_before": 0,
                "size": 8,
                "text_size": 4,
            },
        }
        for invalid_offset in (3, 8, 9):
            malformed = copy.deepcopy(item)
            malformed["pins"]["rodata_offset"] = invalid_offset
            with self.subTest(rodata_offset=invalid_offset):
                with self.assertRaisesRegex(
                    admission.AdmissionError, "overlaps or escapes"
                ):
                    admission._leaf_segments(
                        {
                            "expected": {
                                "component_size": len(component),
                                "component_sha256": digest(component),
                                "overlay_size": len(component) - 100,
                                "overlay_sha256": digest(component[100:]),
                            },
                            "isolated_leaves": [],
                            "relocated_leaves": [malformed],
                        },
                        100,
                        component,
                    )


class RecorderContractTests(unittest.TestCase):
    def test_recording_mode_is_internal_and_normal_final_check_remains(self):
        parameters = inspect.signature(apollo_overlay.build).parameters
        self.assertIn("observe_unpinned", parameters)
        with self.assertRaises(core_builder.BuildError):
            core_builder._verify_final(
                {
                    "overlay_size": 1,
                    "overlay_sha256": "a",
                    "component_size": 1,
                    "component_sha256": "b",
                },
                {},
                record=False,
            )
        core_builder._verify_final(
            {
                "overlay_size": 1,
                "overlay_sha256": "a",
                "component_size": 1,
                "component_sha256": "b",
            },
            {},
            record=True,
        )

    def test_input_report_is_order_independent(self):
        first = {"b": (2, "b" * 64), "a": (1, "a" * 64)}
        second = {"a": (1, "a" * 64), "b": (2, "b" * 64)}
        self.assertEqual(
            core_builder._canonical_input_report(first),
            core_builder._canonical_input_report(second),
        )

    def test_real_contract_derives_required_imu_file_offset(self):
        config = json.loads(
            (G2_ROOT / "components/apollo_main/core_overlay/overlay.json").read_text()
        )
        start, end = admission._derived_imu_span(config)
        self.assertEqual(start, 0x6B5D0)
        self.assertEqual(end - start, 0x3094)

    def test_stage_receipt_retains_leaf_and_in_place_data_toolchains(self):
        def item(identity, *, data=False):
            return {
                "extraction": {
                    "symbol" if data else "function": identity,
                    "size": 2,
                },
                "pins": {"size": 2, "sha256": digest(identity.encode())},
                "toolchain": {"version": "exact compiler"},
                "placement": {"offset": 0, "size": 2, "padding_before": 0},
            }

        report = {
            "overlay": {"size": 2, "sha256": digest(b"o"), "functions": {}},
            "component": {"size": 3, "sha256": digest(b"c")},
            "isolated_leaves": [item("leaf")],
            "relocated_leaves": [],
            "in_place_leaves": [],
            "in_place_data": [item("table", data=True)],
        }
        receipt = core_builder._canonical_stage_pin_report(report)
        self.assertEqual(
            receipt["isolated_leaves"][0]["toolchain"]["version"],
            "exact compiler",
        )
        self.assertEqual(
            receipt["in_place_data"][0]["extraction"]["symbol"], "table"
        )


if __name__ == "__main__":
    unittest.main()
