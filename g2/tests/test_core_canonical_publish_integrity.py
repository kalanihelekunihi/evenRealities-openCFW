# SPDX-License-Identifier: MIT
"""Fail-closed publication tests for the canonical Apollo core wrapper."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest import mock


G2_ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = (
    G2_ROOT / "components/apollo_main/core_overlay/build_component.py"
)
CONFIG_PATH = G2_ROOT / "components/apollo_main/core_overlay/overlay.json"
SPECIFICATION = importlib.util.spec_from_file_location(
    "open_cfw_core_canonical_publish_test", BUILDER_PATH
)
if SPECIFICATION is None or SPECIFICATION.loader is None:
    raise RuntimeError(f"cannot import canonical core builder: {BUILDER_PATH}")
BUILDER = importlib.util.module_from_spec(SPECIFICATION)
SPECIFICATION.loader.exec_module(BUILDER)


def _report(generation: str, overlay: bytes, component: bytes) -> dict:
    return {
        "generation": generation,
        "overlay": {
            "size": len(overlay),
            "sha256": BUILDER.sha256(overlay),
        },
        "component": {
            "size": len(component),
            "sha256": BUILDER.sha256(component),
        },
    }


class CoreCanonicalPublishIntegrityTests(unittest.TestCase):
    def test_snapshot_covers_declared_and_recursive_build_inputs(self) -> None:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        paths = {
            path.relative_to(G2_ROOT).as_posix()
            for path in BUILDER._canonical_input_paths(
                G2_ROOT, CONFIG_PATH, config
            )
        }
        self.assertIn(
            "components/apollo_main/core_overlay/overlay.json", paths
        )
        self.assertIn(
            "components/apollo_main/core_overlay/build_component.py", paths
        )
        self.assertIn("tools/apollo_overlay.py", paths)
        self.assertIn(
            "components/apollo_main/liblc3_ltpf/build_component.py", paths
        )
        self.assertIn(
            "components/apollo_main/liblc3_ltpf/overlay.json", paths
        )
        self.assertIn(
            "components/apollo_main/pt_protocol/build_component.py", paths
        )
        self.assertIn(
            "components/apollo_main/core_overlay/pt_protocol_board_backend.h",
            paths,
        )
        self.assertTrue(
            any(path.startswith("components/shared/") for path in paths)
        )
        self.assertFalse(any("/__pycache__/" in path for path in paths))
        self.assertFalse(any("/build/" in path for path in paths))

    def test_input_drift_preserves_preexisting_generation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            overlay_path = output / "overlay.bin"
            component_path = output / "component.bin"
            report_path = output / "build-report.json"
            overlay_path.write_bytes(b"old-overlay")
            component_path.write_bytes(b"old-component")
            report_path.write_bytes(b"old-report\n")
            original = {
                overlay_path: overlay_path.read_bytes(),
                component_path: component_path.read_bytes(),
                report_path: report_path.read_bytes(),
            }
            new_overlay = b"new-overlay"
            new_component = b"new-component"
            with mock.patch.object(
                BUILDER,
                "_canonical_input_snapshot",
                return_value={"changed": (7, "different")},
            ):
                with self.assertRaisesRegex(
                    BUILDER.BuildError,
                    "^canonical build inputs changed during build$",
                ):
                    BUILDER._publish_canonical_outputs(
                        root=G2_ROOT,
                        config_path=CONFIG_PATH,
                        config={},
                        input_snapshot={"stable": (6, "expected")},
                        overlay_path=overlay_path,
                        final_overlay=new_overlay,
                        component_path=component_path,
                        final_component=new_component,
                        report_path=report_path,
                        report=_report("new", new_overlay, new_component),
                    )
            for path, payload in original.items():
                self.assertEqual(path.read_bytes(), payload)

    def test_invalid_preexisting_report_blocks_publication(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            overlay_path = output / "overlay.bin"
            component_path = output / "component.bin"
            report_path = output / "build-report.json"
            overlay_path.write_bytes(b"old-overlay")
            component_path.write_bytes(b"old-component")
            report_path.write_text(
                json.dumps({
                    "overlay": {"size": 1, "sha256": "not-valid"},
                    "component": {"size": 1, "sha256": "not-valid"},
                }),
                encoding="utf-8",
            )
            original = {
                overlay_path: overlay_path.read_bytes(),
                component_path: component_path.read_bytes(),
                report_path: report_path.read_bytes(),
            }
            expected_snapshot = {"stable": (6, "expected")}
            with mock.patch.object(
                BUILDER,
                "_canonical_input_snapshot",
                return_value=expected_snapshot,
            ):
                with self.assertRaisesRegex(
                    BUILDER.BuildError,
                    "^canonical existing generation identity changed$",
                ):
                    BUILDER._publish_canonical_outputs(
                        root=G2_ROOT,
                        config_path=CONFIG_PATH,
                        config={},
                        input_snapshot=expected_snapshot,
                        overlay_path=overlay_path,
                        final_overlay=b"new-overlay",
                        component_path=component_path,
                        final_component=b"new-component",
                        report_path=report_path,
                        report=_report(
                            "new", b"new-overlay", b"new-component"
                        ),
                    )
            for path, payload in original.items():
                self.assertEqual(path.read_bytes(), payload)

    def test_stable_snapshot_publishes_report_last_and_reads_back(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            overlay_path = output / "overlay.bin"
            component_path = output / "component.bin"
            report_path = output / "build-report.json"
            overlay = b"stable-overlay"
            component = b"stable-component"
            report = _report("stable", overlay, component)
            old_overlay = b"old-overlay"
            old_component = b"old-component"
            overlay_path.write_bytes(old_overlay)
            component_path.write_bytes(old_component)
            report_path.write_text(
                json.dumps(_report("old", old_overlay, old_component)),
                encoding="utf-8",
            )
            expected_snapshot = {"stable": (6, "expected")}
            real_atomic_write = BUILDER.atomic_write
            publication_order: list[str] = []

            def recording_atomic_write(path: Path, payload: bytes) -> None:
                if path in (overlay_path, component_path):
                    self.assertFalse(report_path.exists())
                publication_order.append(path.name)
                real_atomic_write(path, payload)

            with (
                mock.patch.object(
                    BUILDER,
                    "_canonical_input_snapshot",
                    return_value=expected_snapshot,
                ),
                mock.patch.object(
                    BUILDER, "atomic_write", side_effect=recording_atomic_write
                ),
            ):
                BUILDER._publish_canonical_outputs(
                    root=G2_ROOT,
                    config_path=CONFIG_PATH,
                    config={},
                    input_snapshot=expected_snapshot,
                    overlay_path=overlay_path,
                    final_overlay=overlay,
                    component_path=component_path,
                    final_component=component,
                    report_path=report_path,
                    report=report,
                )

            self.assertEqual(
                publication_order,
                ["overlay.bin", "component.bin", "build-report.json"],
            )
            self.assertEqual(overlay_path.read_bytes(), overlay)
            self.assertEqual(component_path.read_bytes(), component)
            self.assertEqual(
                json.loads(report_path.read_text(encoding="utf-8")), report
            )

    def test_late_input_drift_restores_preexisting_generation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            overlay_path = output / "overlay.bin"
            component_path = output / "component.bin"
            report_path = output / "build-report.json"
            old_overlay = b"old-overlay"
            old_component = b"old-component"
            old_report = _report("old", old_overlay, old_component)
            overlay_path.write_bytes(old_overlay)
            component_path.write_bytes(old_component)
            report_path.write_text(
                json.dumps(old_report, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            original = {
                overlay_path: overlay_path.read_bytes(),
                component_path: component_path.read_bytes(),
                report_path: report_path.read_bytes(),
            }
            expected_snapshot = {"stable": (6, "expected")}
            new_overlay = b"new-overlay"
            new_component = b"new-component"
            with mock.patch.object(
                BUILDER,
                "_canonical_input_snapshot",
                side_effect=[
                    expected_snapshot,
                    {"changed": (7, "different")},
                ],
            ) as snapshot:
                with self.assertRaisesRegex(
                    BUILDER.BuildError,
                    "^canonical build inputs changed during build$",
                ):
                    BUILDER._publish_canonical_outputs(
                        root=G2_ROOT,
                        config_path=CONFIG_PATH,
                        config={},
                        input_snapshot=expected_snapshot,
                        overlay_path=overlay_path,
                        final_overlay=new_overlay,
                        component_path=component_path,
                        final_component=new_component,
                        report_path=report_path,
                        report=_report("new", new_overlay, new_component),
                    )
            self.assertEqual(snapshot.call_count, 2)
            for path, payload in original.items():
                self.assertEqual(path.read_bytes(), payload)

    def test_atomic_writes_are_whole_and_leave_no_temporary_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            target = output / "artifact.bin"
            payloads = [bytes([index]) * (4096 + index) for index in range(16)]
            with ThreadPoolExecutor(max_workers=8) as executor:
                list(executor.map(lambda payload: BUILDER.atomic_write(
                    target, payload
                ), payloads))
            self.assertIn(target.read_bytes(), payloads)
            self.assertEqual(list(output.glob(".artifact.bin.*")), [])

    def test_concurrent_publishers_leave_one_whole_generation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            overlay_path = output / "overlay.bin"
            component_path = output / "component.bin"
            report_path = output / "build-report.json"
            expected_snapshot = {"stable": (6, "expected")}
            generations = {
                "alpha": (b"alpha-overlay", b"alpha-component"),
                "beta": (b"beta-overlay", b"beta-component"),
            }
            barrier = threading.Barrier(len(generations))
            state_lock = threading.Lock()
            active_snapshots = 0
            maximum_active_snapshots = 0

            def snapshot(*_args, **_kwargs):
                nonlocal active_snapshots, maximum_active_snapshots
                with state_lock:
                    active_snapshots += 1
                    maximum_active_snapshots = max(
                        maximum_active_snapshots, active_snapshots
                    )
                time.sleep(0.01)
                with state_lock:
                    active_snapshots -= 1
                return expected_snapshot

            def publish(item: tuple[str, tuple[bytes, bytes]]) -> None:
                generation, (overlay, component) = item
                barrier.wait()
                BUILDER._publish_canonical_outputs(
                    root=G2_ROOT,
                    config_path=CONFIG_PATH,
                    config={},
                    input_snapshot=expected_snapshot,
                    overlay_path=overlay_path,
                    final_overlay=overlay,
                    component_path=component_path,
                    final_component=component,
                    report_path=report_path,
                    report=_report(generation, overlay, component),
                )

            with mock.patch.object(
                BUILDER, "_canonical_input_snapshot", side_effect=snapshot
            ):
                with ThreadPoolExecutor(max_workers=2) as executor:
                    list(executor.map(publish, generations.items()))

            report = json.loads(report_path.read_text(encoding="utf-8"))
            overlay, component = generations[report["generation"]]
            self.assertEqual(overlay_path.read_bytes(), overlay)
            self.assertEqual(component_path.read_bytes(), component)
            self.assertEqual(report["overlay"]["sha256"], BUILDER.sha256(overlay))
            self.assertEqual(
                report["component"]["sha256"], BUILDER.sha256(component)
            )
            self.assertEqual(maximum_active_snapshots, 1)
            self.assertEqual(list(output.glob(".*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
