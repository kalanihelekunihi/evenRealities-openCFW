# SPDX-License-Identifier: MIT
"""Adversarial checks for canonical recorder evidence and publication safety."""

from __future__ import annotations

import importlib.util
import fcntl
import json
import os
import select
import tempfile
import unittest
from pathlib import Path
from unittest import mock


G2_ROOT = Path(__file__).resolve().parents[1]


def load(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


CORE = load(
    G2_ROOT / "components/apollo_main/core_overlay/build_component.py",
    "open_cfw_core_recorder_security_test",
)
PT = load(
    G2_ROOT / "components/apollo_main/pt_protocol/build_component.py",
    "open_cfw_pt_recorder_security_test",
)
CONFIG = G2_ROOT / "components/apollo_main/core_overlay/overlay.json"


def record(name: str, payload: bytes) -> dict:
    return {"artifact": name, "size": len(payload), "sha256": CORE.sha256(payload)}


def report(overlay: bytes, component: bytes, intermediates: dict[str, bytes]) -> dict:
    return {
        "overlay": {"size": len(overlay), "sha256": CORE.sha256(overlay)},
        "component": {
            "size": len(component),
            "sha256": CORE.sha256(component),
        },
        "canonical_observation": {
            "schema_version": 2,
            "final_artifacts": {
                "overlay": record("overlay.bin", overlay),
                "component": record("component.bin", component),
            },
            "intermediate_artifacts": {
                key: record(CORE._CANONICAL_INTERMEDIATE_NAMES[key], payload)
                for key, payload in intermediates.items()
            },
        },
    }


class CanonicalRecorderSecurityTests(unittest.TestCase):
    def test_record_cli_does_not_resolve_away_output_symlink(self) -> None:
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            root = Path(temporary)
            target = root / "target"
            target.mkdir()
            link = root / "output"
            link.symlink_to(target.name, target_is_directory=True)

            def enforce_output_boundary(**arguments):
                CORE._prepare_canonical_output_dir(
                    arguments["output_dir"], boundary=arguments["root"]
                )
                self.fail("record CLI resolved away the output symlink")

            with mock.patch.object(CORE, "build", side_effect=enforce_output_boundary):
                with self.assertRaisesRegex(CORE.BuildError, "symlink"):
                    CORE.main([
                        "--record-canonical",
                        "--output-dir", str(link),
                        "--config", str(CONFIG),
                    ])

    def test_record_cli_rejects_symlinked_parent_and_outside_path(self) -> None:
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            root = Path(temporary)
            real_parent = root / "real-parent"
            real_parent.mkdir()
            linked_parent = root / "linked-parent"
            linked_parent.symlink_to(real_parent.name, target_is_directory=True)

            def enforce_output_boundary(**arguments):
                CORE._prepare_canonical_output_dir(
                    arguments["output_dir"], boundary=arguments["root"]
                )
                self.fail("unsafe record output path was accepted")

            with mock.patch.object(CORE, "build", side_effect=enforce_output_boundary):
                with self.assertRaisesRegex(CORE.BuildError, "symlink"):
                    CORE.main([
                        "--record-canonical",
                        "--output-dir", str(linked_parent / "observation"),
                    ])

        with tempfile.TemporaryDirectory() as outside:
            with mock.patch.object(CORE, "build", side_effect=enforce_output_boundary):
                with self.assertRaisesRegex(CORE.BuildError, "escapes"):
                    CORE.main([
                        "--record-canonical",
                        "--output-dir", str(Path(outside) / "observation"),
                    ])

        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            root = Path(temporary)
            traversal = root / "nested" / ".." / "observation"
            with mock.patch.object(CORE, "build", side_effect=enforce_output_boundary):
                with self.assertRaisesRegex(CORE.BuildError, "traversal"):
                    CORE.main([
                        "--record-canonical", "--output-dir", str(traversal),
                    ])
            self.assertFalse((root / "observation").exists())

        with mock.patch.object(CORE, "build", side_effect=enforce_output_boundary):
            with self.assertRaisesRegex(CORE.BuildError, "strictly below"):
                CORE.main([
                    "--record-canonical", "--output-dir", str(G2_ROOT),
                ])

    def test_record_cli_accepts_one_independent_g2_local_directory(self) -> None:
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            output = Path(temporary) / "independent-observation"

            def accept_output(**arguments):
                prepared = CORE._prepare_canonical_output_dir(
                    arguments["output_dir"], boundary=arguments["root"]
                )
                self.assertEqual(prepared, output)
                return {
                    "name": "fixture",
                    "overlay": {"size": 1, "sha256": "a" * 64},
                    "component": {"size": 2, "sha256": "b" * 64},
                    "toolchain": {"profile": "apple-clang"},
                }

            with mock.patch.object(CORE, "build", side_effect=accept_output):
                self.assertEqual(CORE.main([
                    "--record-canonical", "--output-dir", str(output)
                ]), 0)
            self.assertTrue(output.is_dir())

    def test_record_cli_rejects_multiply_linked_publication_lock(self) -> None:
        with tempfile.TemporaryDirectory(dir=G2_ROOT) as temporary:
            output = Path(temporary) / "observation"
            output.mkdir()
            lock = output / ".open-cfw-canonical.lock"
            lock.write_bytes(b"")
            os.link(lock, output / "lock-alias")

            def acquire_only(**arguments):
                with CORE._canonical_output_lock(
                    arguments["output_dir"],
                    boundary=arguments["root"],
                    lock_anchor=Path(temporary),
                ):
                    self.fail("multiply linked publication lock was acquired")

            with mock.patch.object(CORE, "build", side_effect=acquire_only):
                with self.assertRaisesRegex(CORE.BuildError, "identity changed"):
                    CORE.main([
                        "--record-canonical", "--output-dir", str(output)
                    ])

    def test_multiply_linked_output_artifact_is_rejected_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            artifact = output / "overlay.bin"
            artifact.write_bytes(b"protected")
            alias = output / "overlay-alias.bin"
            os.link(artifact, alias)
            directory_fd = os.open(
                output,
                os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                | getattr(os, "O_NOFOLLOW", 0),
            )
            try:
                with self.assertRaisesRegex(
                    CORE.BuildError, "publication target is unsafe"
                ):
                    CORE._atomic_write_canonical(
                        directory_fd, artifact, b"replacement"
                    )
            finally:
                os.close(directory_fd)
            self.assertEqual(artifact.read_bytes(), b"protected")
            self.assertEqual(alias.read_bytes(), b"protected")

    def test_output_directory_symlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "target"
            target.mkdir()
            link = root / "output"
            link.symlink_to(target, target_is_directory=True)
            with self.assertRaisesRegex(CORE.BuildError, "directory is unsafe"):
                CORE._prepare_canonical_output_dir(link)

    def test_record_output_rejects_parent_symlink_before_creation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / "g2"
            outside = root / "outside"
            project.mkdir()
            outside.mkdir()
            linked_parent = project / "linked-parent"
            linked_parent.symlink_to(outside, target_is_directory=True)
            redirected = linked_parent / "observation"
            with self.assertRaisesRegex(CORE.BuildError, "contains a symlink"):
                CORE._prepare_canonical_output_dir(
                    redirected, boundary=project
                )
            self.assertFalse((outside / "observation").exists())

    def test_record_output_parent_swap_cannot_redirect_creation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / "g2"
            parent = project / "parent"
            displaced = project / "displaced-parent"
            outside = root / "outside"
            parent.mkdir(parents=True)
            outside.mkdir()
            output = parent / "observation"
            original_mkdir = os.mkdir
            swapped = False

            def swap_parent(path, mode=0o777, *, dir_fd=None):
                nonlocal swapped
                if path == "observation" and dir_fd is not None and not swapped:
                    swapped = True
                    parent.rename(displaced)
                    parent.symlink_to(outside, target_is_directory=True)
                return original_mkdir(path, mode, dir_fd=dir_fd)

            with mock.patch.object(CORE.os, "mkdir", side_effect=swap_parent):
                with self.assertRaisesRegex(
                    CORE.BuildError, "symlink|identity changed"
                ):
                    CORE._prepare_canonical_output_dir(
                        output, boundary=project
                    )
            self.assertFalse((outside / "observation").exists())
            self.assertTrue(swapped)

    def test_record_output_must_remain_inside_project_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / "g2"
            outside = root / "outside"
            project.mkdir()
            with self.assertRaisesRegex(CORE.BuildError, "escapes the G2"):
                CORE._prepare_canonical_output_dir(
                    outside, boundary=project
                )
            self.assertFalse(outside.exists())

    def test_lock_symlink_and_special_file_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            lock = output / ".open-cfw-canonical.lock"
            target = output / "target"
            target.write_bytes(b"target")
            lock.symlink_to(target)
            with self.assertRaisesRegex(
                CORE.BuildError, r"lock (?:is unsafe|identity changed)"
            ):
                with CORE._canonical_output_lock(output):
                    self.fail("unsafe lock was acquired")
            lock.unlink()
            os.mkfifo(lock)
            with self.assertRaisesRegex(
                CORE.BuildError, r"lock (?:is unsafe|identity changed)"
            ):
                with CORE._canonical_output_lock(output):
                    self.fail("special-file lock was acquired")

    def test_existing_artifact_symlink_is_rejected_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            target = output / "target"
            target.write_bytes(b"protected")
            overlay = output / "overlay.bin"
            overlay.symlink_to(target)
            component = output / "component.bin"
            report_path = output / "build-report.json"
            expected = {"stable": (1, "identity")}
            with mock.patch.object(
                CORE, "_canonical_input_snapshot", return_value=expected
            ):
                with self.assertRaisesRegex(
                    CORE.BuildError, "not a safe regular file"
                ):
                    CORE._publish_canonical_outputs(
                        root=output,
                        config_path=CONFIG,
                        config={},
                        input_snapshot=expected,
                        overlay_path=overlay,
                        final_overlay=b"new-overlay",
                        component_path=component,
                        final_component=b"new-component",
                        report_path=report_path,
                        report=report(b"new-overlay", b"new-component", {}),
                    )
            self.assertTrue(overlay.is_symlink())
            self.assertEqual(target.read_bytes(), b"protected")

    def test_output_directory_replacement_cannot_redirect_publication(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            output = parent / "observation"
            displaced = parent / "displaced-observation"
            output.mkdir()
            overlay = output / "overlay.bin"
            component = output / "component.bin"
            report_path = output / "build-report.json"
            expected = {"stable": (1, "identity")}
            real_atomic_write = CORE._atomic_write_canonical
            replaced = False

            def replace_directory_then_write(
                directory_fd: int, path: Path, payload: bytes
            ) -> None:
                nonlocal replaced
                if not replaced:
                    replaced = True
                    os.replace(output, displaced)
                    output.mkdir()
                real_atomic_write(directory_fd, path, payload)

            with (
                mock.patch.object(
                    CORE, "_canonical_input_snapshot", return_value=expected
                ),
                mock.patch.object(
                    CORE,
                    "_atomic_write_canonical",
                    side_effect=replace_directory_then_write,
                ),
            ):
                with self.assertRaisesRegex(
                    CORE.BuildError, "output directory identity changed"
                ):
                    CORE._publish_canonical_outputs(
                        root=parent,
                        config_path=CONFIG,
                        config={},
                        input_snapshot=expected,
                        overlay_path=overlay,
                        final_overlay=b"new-overlay",
                        component_path=component,
                        final_component=b"new-component",
                        report_path=report_path,
                        report=report(b"new-overlay", b"new-component", {}),
                    )

            self.assertEqual(list(output.iterdir()), [])
            self.assertFalse((displaced / "overlay.bin").exists())
            self.assertFalse((displaced / "component.bin").exists())
            self.assertFalse((displaced / "build-report.json").exists())

    @unittest.skipUnless(hasattr(os, "fork"), "requires POSIX process locks")
    def test_fixed_boundary_lock_blocks_replacement_lock_domain(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            boundary = Path(temporary).resolve()
            output = boundary / "observation"
            displaced = boundary / "displaced-observation"
            output.mkdir()
            anchor = boundary / (
                ".open-cfw-canonical-output-"
                + CORE.sha256(b"observation")
                + ".lock"
            )
            read_fd, write_fd = os.pipe()
            child = -1
            try:
                with self.assertRaisesRegex(
                    CORE.BuildError, "output directory identity changed"
                ):
                    with CORE._canonical_output_lock(
                        output, boundary=boundary
                    ):
                        os.replace(output, displaced)
                        output.mkdir()
                        child = os.fork()
                        if child == 0:
                            try:
                                os.close(read_fd)
                                descriptor = os.open(anchor, os.O_RDWR)
                                try:
                                    fcntl.flock(descriptor, fcntl.LOCK_EX)
                                    os.write(write_fd, b"acquired")
                                finally:
                                    os.close(descriptor)
                            finally:
                                os._exit(0)
                        ready, _writable, _errors = select.select(
                            [read_fd], [], [], 0.25
                        )
                        self.assertEqual(
                            ready, [],
                            "replacement created a concurrent boundary lock domain",
                        )
                ready, _writable, _errors = select.select(
                    [read_fd], [], [], 2.0
                )
                self.assertEqual(ready, [read_fd])
                self.assertEqual(os.read(read_fd, 8), b"acquired")
            finally:
                os.close(read_fd)
                os.close(write_fd)
                if child > 0:
                    _pid, status = os.waitpid(child, 0)
                    self.assertEqual(status, 0)

    def test_preopen_output_and_anchor_replacement_are_rejected(self) -> None:
        for replaced_role in ("output", "anchor"):
            with self.subTest(replaced_role=replaced_role), \
                    tempfile.TemporaryDirectory() as temporary:
                boundary = Path(temporary).resolve()
                output = boundary / "observation"
                anchor = boundary / "locks"
                output.mkdir()
                anchor.mkdir()
                target = output if replaced_role == "output" else anchor
                displaced = boundary / f"displaced-{replaced_role}"
                real_prepare = CORE._prepare_canonical_output_dir
                replaced = False

                def replace_after_prepare(path: Path, **arguments):
                    nonlocal replaced
                    resolved = real_prepare(path, **arguments)
                    if not replaced and Path(path).resolve() == target:
                        replaced = True
                        os.replace(target, displaced)
                        target.mkdir()
                    return resolved

                with mock.patch.object(
                    CORE,
                    "_prepare_canonical_output_dir",
                    side_effect=replace_after_prepare,
                ):
                    with self.assertRaisesRegex(
                        CORE.BuildError, "identity changed before lock acquisition"
                    ):
                        with CORE._canonical_output_lock(
                            output,
                            boundary=boundary,
                            lock_anchor=anchor,
                        ):
                            self.fail("replaced prepared directory was accepted")
                self.assertTrue(replaced)
                self.assertEqual(list(target.iterdir()), [])

    def test_incomplete_intermediate_artifact_set_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            values = {
                key: key.encode("ascii")
                for key in CORE._CANONICAL_INTERMEDIATE_NAMES
            }
            paths = {
                output / CORE._CANONICAL_INTERMEDIATE_NAMES[key]: payload
                for key, payload in values.items()
            }
            paths.pop(next(iter(paths)))
            with self.assertRaisesRegex(
                CORE.BuildError, "intermediate artifact identity changed"
            ):
                CORE._publish_canonical_outputs(
                    root=output,
                    config_path=CONFIG,
                    config={},
                    input_snapshot={},
                    overlay_path=output / "overlay.bin",
                    final_overlay=b"overlay",
                    component_path=output / "component.bin",
                    final_component=b"component",
                    report_path=output / "build-report.json",
                    report=report(b"overlay", b"component", values),
                    additional_artifacts=paths,
                )

    def test_partial_existing_generation_is_rejected_without_repair(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            overlay, component = b"old-overlay", b"old-component"
            values = {
                key: f"old-{key}".encode()
                for key in CORE._CANONICAL_INTERMEDIATE_NAMES
            }
            overlay_path = output / "overlay.bin"
            component_path = output / "component.bin"
            report_path = output / "build-report.json"
            overlay_path.write_bytes(overlay)
            component_path.write_bytes(component)
            additional = {
                output / CORE._CANONICAL_INTERMEDIATE_NAMES[key]: payload
                for key, payload in values.items()
            }
            for path, payload in additional.items():
                path.write_bytes(payload)
            missing = next(iter(additional))
            missing.unlink()
            old_report = report(overlay, component, values)
            report_path.write_text(
                json.dumps(old_report, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            expected = {"stable": (1, "identity")}
            with mock.patch.object(
                CORE, "_canonical_input_snapshot", return_value=expected
            ):
                with self.assertRaisesRegex(
                    CORE.BuildError, "existing generation identity changed"
                ):
                    CORE._publish_canonical_outputs(
                        root=output,
                        config_path=CONFIG,
                        config={},
                        input_snapshot=expected,
                        overlay_path=overlay_path,
                        final_overlay=b"new-overlay",
                        component_path=component_path,
                        final_component=b"new-component",
                        report_path=report_path,
                        report=report(b"new-overlay", b"new-component", values),
                        additional_artifacts=additional,
                    )
            self.assertFalse(missing.exists())
            self.assertEqual(overlay_path.read_bytes(), overlay)
            self.assertEqual(component_path.read_bytes(), component)

    def test_intermediate_write_failure_restores_complete_generation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            old_overlay, old_component = b"old-overlay", b"old-component"
            new_overlay, new_component = b"new-overlay", b"new-component"
            old_values = {
                key: f"old-{key}".encode() for key in CORE._CANONICAL_INTERMEDIATE_NAMES
            }
            new_values = {
                key: f"new-{key}".encode() for key in CORE._CANONICAL_INTERMEDIATE_NAMES
            }
            overlay_path = output / "overlay.bin"
            component_path = output / "component.bin"
            report_path = output / "build-report.json"
            additional = {
                output / CORE._CANONICAL_INTERMEDIATE_NAMES[key]: payload
                for key, payload in new_values.items()
            }
            overlay_path.write_bytes(old_overlay)
            component_path.write_bytes(old_component)
            for key, payload in old_values.items():
                (output / CORE._CANONICAL_INTERMEDIATE_NAMES[key]).write_bytes(payload)
            old_report = report(old_overlay, old_component, old_values)
            report_path.write_text(
                json.dumps(old_report, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            original = {
                path: path.read_bytes()
                for path in (overlay_path, component_path, *additional, report_path)
            }
            expected = {"stable": (1, "identity")}
            real_atomic_write = CORE._atomic_write_canonical
            writes = 0

            def fail_first_intermediate(
                directory_fd: int, path: Path, payload: bytes
            ) -> None:
                nonlocal writes
                writes += 1
                if writes == 3:
                    raise OSError("injected intermediate failure")
                real_atomic_write(directory_fd, path, payload)

            with (
                mock.patch.object(
                    CORE, "_canonical_input_snapshot", return_value=expected
                ),
                mock.patch.object(
                    CORE,
                    "_atomic_write_canonical",
                    side_effect=fail_first_intermediate,
                ),
            ):
                with self.assertRaisesRegex(OSError, "injected intermediate"):
                    CORE._publish_canonical_outputs(
                        root=output,
                        config_path=CONFIG,
                        config={},
                        input_snapshot=expected,
                        overlay_path=overlay_path,
                        final_overlay=new_overlay,
                        component_path=component_path,
                        final_component=new_component,
                        report_path=report_path,
                        report=report(new_overlay, new_component, new_values),
                        additional_artifacts=additional,
                    )
            for path, payload in original.items():
                self.assertEqual(path.read_bytes(), payload)

    def test_executable_drift_during_identity_capture_is_rejected(self) -> None:
        executable = Path("/fixed/compiler")
        with (
            mock.patch.object(PT, "_tool_invocation_path", return_value=executable),
            mock.patch.object(PT, "_resolve_tool_path", return_value=executable),
            mock.patch.object(PT, "_version", return_value="compiler 1"),
            mock.patch.object(PT, "_read_regular", side_effect=[b"before", b"after"]),
        ):
            with self.assertRaisesRegex(PT.BuildError, "changed while"):
                PT._executable_identity(str(executable), role="compiler executable")

    def test_pt_compile_arguments_bind_the_recorded_builtin_headers(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            include = Path(temporary).resolve()
            compiler = Path("/fixed/compiler")
            with mock.patch.object(
                PT, "_compiler_builtin_include_dir", return_value=include
            ) as selected:
                arguments = PT._hermetic_compiler_arguments(
                    compiler, expected=include
                )
            selected.assert_called_once_with(compiler, expected=include)
            self.assertEqual(
                arguments,
                [
                    "--no-default-config",
                    "-nostdinc",
                    "-isystem",
                    str(include),
                ],
            )


if __name__ == "__main__":
    unittest.main()
