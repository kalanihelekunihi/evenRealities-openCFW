#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build the canonical Apollo core image and its bounded post-link providers."""

from __future__ import annotations

import argparse
import copy
import fcntl
import importlib.util
import json
import os
import secrets
import stat
import sys
import tempfile
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any


COMPONENT_ROOT = Path(__file__).resolve().parent
OPENCFW_ROOT = COMPONENT_ROOT.parents[2]
sys.path.insert(0, str(OPENCFW_ROOT / "tools"))

from apollo_overlay import (  # noqa: E402,F401
    BuildError,
    atomic_write,
    build as overlay_build,
    decode_thumb_branch,
    resolve_toolchain_profile,
    sha256,
)


_INPUT_EXCLUDED_DIRECTORIES = {"build", "__pycache__", "blobs"}
_INPUT_EXCLUDED_SUFFIXES = {
    ".a", ".bin", ".dylib", ".elf", ".map", ".o", ".pyc", ".so",
}
_CANONICAL_OUTPUT_THREAD_LOCK = threading.Lock()
_CANONICAL_INTERMEDIATE_NAMES = {
    "core_stage_overlay": "core-stage-overlay.bin",
    "core_stage_component": "core-stage-component.bin",
    "liblc3_payload": "liblc3-payload.bin",
    "liblc3_component": "liblc3-component.bin",
    "pt_component": "pt-component.bin",
    "liblc3_service_component": "liblc3-service-component.bin",
}
CFF_COMPONENT_ROOT = COMPONENT_ROOT.parent / "freetype_cff_scatter"
CFF_SHARED_ROOT = OPENCFW_ROOT / "components/shared/freetype_cff"
LC3_SERVICE_ROOT = COMPONENT_ROOT.parent / "liblc3_encoder"
PT_AGGREGATE_LICENSE = "MIT AND Apache-2.0"
PT_APACHE_SOURCE = (
    "components/apollo_main/core_overlay/pt_protocol_lc3_setup.c"
)
PT_SOURCE_LICENSE_COUNTS = {"MIT": 28, "Apache-2.0": 1}
PT_APACHE_SOURCE_METADATA = {
    "upstream": "Google/liblc3",
    "upstream_commit": "96a3af0beb5487aca3b98a4b992a539a1f6d80d1",
    "license_path": "third_party/liblc3/LICENSE",
    "license_sha256": (
        "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"
    ),
}


def _walk_config(value: Any):
    """Yield every nested mapping in a canonical component config."""
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk_config(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_config(child)


def _resolve_input(root: Path, value: str) -> Path:
    path = (root / value).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as error:
        raise BuildError(f"canonical build input escapes repository: {value}") \
            from error
    return path


def _excluded_recursive_input(root: Path, path: Path) -> bool:
    relative = path.relative_to(root.resolve())
    if path.name == ".DS_Store" or path.suffix.lower() in _INPUT_EXCLUDED_SUFFIXES:
        return True
    return any(
        part in _INPUT_EXCLUDED_DIRECTORIES
        or part.startswith("build-")
        or part.startswith(".tmp-")
        for part in relative.parts
    )


def _canonical_input_paths(
    root: Path, config_path: Path, config: dict[str, Any]
) -> tuple[Path, ...]:
    """Return the complete declared source/config closure for a core build."""
    root = root.resolve()
    liblc3_root = COMPONENT_ROOT.parent / "liblc3_ltpf"
    pt_root = COMPONENT_ROOT.parent / "pt_protocol"
    fixed = {
        config_path.resolve(),
        Path(__file__).resolve(),
        (root / "tools/apollo_overlay.py").resolve(),
        (liblc3_root / "build_component.py").resolve(),
        (liblc3_root / "overlay.json").resolve(),
        (pt_root / "build_component.py").resolve(),
        (CFF_COMPONENT_ROOT / "build_component.py").resolve(),
        (CFF_COMPONENT_ROOT / "overlay.json").resolve(),
        (CFF_COMPONENT_ROOT / "README.md").resolve(),
        (OPENCFW_ROOT / "tools/analyze_g2_freetype_cff_scatter_link.py").resolve(),
        (OPENCFW_ROOT / "tools/analyze_g2_freetype_cff_size_optimization.py").resolve(),
        (OPENCFW_ROOT / "tools/manifests/g2-freetype-cff-scatter-link.json").resolve(),
        (OPENCFW_ROOT / "tools/manifests/g2-freetype-cff-size-optimization.json").resolve(),
    }
    liblc3_config = json.loads(
        (liblc3_root / "overlay.json").read_text(encoding="utf-8")
    )
    configs = (config, liblc3_config)
    include_dirs: set[Path] = set()
    for candidate_config in configs:
        for record in _walk_config(candidate_config):
            relative = record.get("path")
            if isinstance(relative, str):
                fixed.add(_resolve_input(root, relative))
            configured_includes = record.get("include_dirs")
            if isinstance(configured_includes, list):
                for relative_include in configured_includes:
                    if not isinstance(relative_include, str):
                        raise BuildError(
                            "canonical build include directory is not a string"
                        )
                    include_dirs.add(_resolve_input(root, relative_include))

    # The bounded PT builder carries its source list in code rather than a
    # separate JSON config. Include both its translation units and headers.
    fixed.update(COMPONENT_ROOT.glob("pt_protocol_*.c"))
    fixed.update(COMPONENT_ROOT.glob("pt_protocol_*.h"))
    for directory in (
        LC3_SERVICE_ROOT,
        OPENCFW_ROOT / "components/shared/liblc3",
        CFF_SHARED_ROOT,
        OPENCFW_ROOT / "third_party/freetype",
        OPENCFW_ROOT / "research/candidates/freetype/g2_config",
        OPENCFW_ROOT / "research/candidates/freetype/target_compat",
    ):
        fixed.update(
            path.resolve() for path in directory.rglob("*")
            if path.is_file() and not _excluded_recursive_input(root, path)
        )

    for directory in include_dirs:
        if not directory.is_dir():
            raise BuildError(
                f"canonical build include directory is missing: {directory}"
            )
        for path in directory.rglob("*"):
            if path.is_file() and not _excluded_recursive_input(root, path):
                fixed.add(path.resolve())

    missing = [path for path in fixed if not path.is_file()]
    if missing:
        raise BuildError(f"canonical build input is missing: {sorted(missing)[0]}")
    return tuple(sorted(fixed, key=lambda path: path.as_posix()))


def _canonical_input_snapshot(
    root: Path, config_path: Path, config: dict[str, Any]
) -> dict[str, tuple[int, str]]:
    root = root.resolve()
    snapshot: dict[str, tuple[int, str]] = {}
    for path in _canonical_input_paths(root, config_path, config):
        payload = (
            json.dumps(
                _canonical_config_projection(config),
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
            if path == config_path.resolve()
            else path.read_bytes()
        )
        snapshot[path.relative_to(root).as_posix()] = (len(payload), sha256(payload))
    return snapshot


def _canonical_input_state(
    root: Path, config_path: Path
) -> tuple[bytes, dict[str, Any], dict[str, tuple[int, str]]]:
    """Parse and snapshot the current on-disk config as one stable input."""
    try:
        config_payload = config_path.read_bytes()
        config = json.loads(config_payload.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise BuildError(f"canonical core config cannot be read: {error}") from error
    if not isinstance(config, dict):
        raise BuildError("canonical core config must contain a JSON object")
    snapshot = _canonical_input_snapshot(root, config_path, config)
    try:
        if config_path.read_bytes() != config_payload:
            raise BuildError("canonical build inputs changed during build")
    except OSError as error:
        raise BuildError("canonical build inputs changed during build") from error
    return config_payload, config, snapshot


def _canonical_config_projection(config: dict[str, Any]) -> dict[str, Any]:
    """Remove only admission-managed compiler observations from core config."""
    projected = copy.deepcopy(config)
    projected.pop("core_stage_expected", None)
    projected.pop("expected", None)
    toolchain = projected.get("toolchain")
    if isinstance(toolchain, dict):
        toolchain.pop("reviewed_version_prefix", None)
    for profile in projected.get("toolchain_profiles", {}).values():
        if isinstance(profile, dict):
            for key in (
                "core_stage_expected", "expected", "reviewed_version_prefix"
            ):
                profile.pop(key, None)

    providers = projected.get("post_link_providers", {})
    lib_profiles = providers.get("liblc3_ltpf", {}).get("profiles", {})
    pt_profiles = providers.get("pt_protocol", {}).get("profiles", {})
    for profile in lib_profiles.values():
        if isinstance(profile, dict):
            profile.pop("overlay", None)
            profile.pop("component", None)
    for profile in pt_profiles.values():
        if isinstance(profile, dict):
            for key in ("payload_size", "payload_sha256", "interval_sha256"):
                profile.pop(key, None)

    def project_relocations(value: Any) -> None:
        if isinstance(value, list):
            for relocation in value:
                if isinstance(relocation, dict):
                    relocation.pop("offset", None)

    for key in (
        "isolated_leaves", "relocated_leaves", "in_place_leaves", "cave_leaves"
    ):
        for leaf in projected.get(key, []):
            if not isinstance(leaf, dict):
                continue
            leaf.pop("expected", None)
            project_relocations(leaf.get("relocations"))
            leaf.pop("closure", None)
            leaf_toolchain = leaf.get("toolchain")
            if isinstance(leaf_toolchain, dict):
                leaf_toolchain.pop("reviewed_version_prefix", None)
            profiles = leaf.get("toolchain_profiles", {})
            for profile_id, profile in list(profiles.items()):
                if not isinstance(profile, dict):
                    continue
                profile.pop("expected", None)
                profile.pop("reviewed_version_prefix", None)
                profile.pop("closure", None)
                project_relocations(profile.get("relocations"))
                if not profile:
                    profiles.pop(profile_id)
            if not profiles:
                leaf.pop("toolchain_profiles", None)
    for group in projected.get("in_place_data", []):
        if not isinstance(group, dict):
            continue
        group.pop("expected", None)
        group_toolchain = group.get("toolchain")
        if isinstance(group_toolchain, dict):
            group_toolchain.pop("reviewed_version_prefix", None)
        profiles = group.get("toolchain_profiles", {})
        for profile_id, profile in list(profiles.items()):
            if isinstance(profile, dict):
                profile.pop("expected", None)
                profile.pop("reviewed_version_prefix", None)
                if not profile:
                    profiles.pop(profile_id)
        if not profiles:
            group.pop("toolchain_profiles", None)
    return projected


def _canonical_input_report(
    snapshot: dict[str, tuple[int, str]],
) -> dict[str, Any]:
    """Return one deterministic identity for the complete source closure."""
    entries = [
        {"path": path, "size": size, "sha256": digest}
        for path, (size, digest) in sorted(snapshot.items())
    ]
    payload = json.dumps(
        entries, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return {"sha256": sha256(payload), "entries": entries}


def _canonical_stage_pin_report(report: dict[str, Any]) -> dict[str, Any]:
    """Extract every compiler-dependent core pin needed for admission."""
    result: dict[str, Any] = {
        "expected": {
            "overlay_size": int(report["overlay"]["size"]),
            "overlay_sha256": report["overlay"]["sha256"],
            "component_size": int(report["component"]["size"]),
            "component_sha256": report["component"]["sha256"],
        },
        "functions": copy.deepcopy(report["overlay"]["functions"]),
    }
    for key in (
        "isolated_leaves",
        "relocated_leaves",
        "in_place_leaves",
        "in_place_data",
    ):
        records = report.get(key, [])
        if not isinstance(records, list):
            raise BuildError(f"canonical stage {key} receipt changed")
        result[key] = [
            {
                "extraction": copy.deepcopy(item.get("extraction")),
                "pins": copy.deepcopy(item.get("pins")),
                "toolchain": copy.deepcopy(item.get("toolchain")),
                **(
                    {"placement": copy.deepcopy(item["placement"])}
                    if "placement" in item
                    else {}
                ),
            }
            for item in records
        ]
        if any(
            not isinstance(item["extraction"], dict)
            or not isinstance(item["pins"], dict)
            or not isinstance(item["toolchain"], dict)
            for item in result[key]
        ):
            raise BuildError(f"canonical stage {key} pin receipt changed")
    return result


def _require_canonical_inputs_unchanged(
    root: Path,
    config_path: Path,
    config: dict[str, Any],
    expected: dict[str, tuple[int, str]],
) -> None:
    try:
        _payload, _current_config, observed = _canonical_input_state(
            root, config_path
        )
    except (BuildError, OSError):
        raise BuildError("canonical build inputs changed during build") from None
    if observed != expected:
        raise BuildError("canonical build inputs changed during build")


def _prepare_canonical_output_dir(
    output_dir: Path,
    *,
    boundary: Path | None = None,
    identity_out: list[tuple[int, int]] | None = None,
) -> Path:
    """Create a safe output directory, optionally below one symlink-free root."""
    requested_output = Path(output_dir)
    if boundary is not None and ".." in requested_output.parts:
        raise BuildError("canonical record output path contains traversal")
    output_dir = Path(os.path.abspath(requested_output))
    boundary_resolved: Path | None = None
    expected_resolved: Path | None = None
    before: os.stat_result
    if boundary is not None:
        boundary_lexical = Path(os.path.abspath(boundary))
        try:
            boundary_resolved = boundary_lexical.resolve(strict=True)
        except (OSError, RuntimeError) as error:
            raise BuildError("canonical output boundary is unsafe") from error
        try:
            relative = output_dir.relative_to(boundary_lexical)
        except ValueError as error:
            raise BuildError(
                "canonical record output escapes the G2 project"
            ) from error
        if not relative.parts:
            raise BuildError(
                "canonical record output must be strictly below the G2 project"
            )
        expected_resolved = boundary_resolved / relative
        directory_flags = (
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        )
        descriptors: list[int] = []
        try:
            descriptors.append(os.open(boundary_resolved, directory_flags))
            boundary_opened = os.fstat(descriptors[0])
            boundary_named = os.stat(boundary_resolved, follow_symlinks=False)
            if (
                not stat.S_ISDIR(boundary_opened.st_mode)
                or not stat.S_ISDIR(boundary_named.st_mode)
                or (boundary_opened.st_dev, boundary_opened.st_ino)
                != (boundary_named.st_dev, boundary_named.st_ino)
            ):
                raise BuildError("canonical output boundary identity changed")
            cursor = descriptors[0]
            for part in relative.parts:
                try:
                    child = os.open(part, directory_flags, dir_fd=cursor)
                except FileNotFoundError:
                    os.mkdir(part, 0o777, dir_fd=cursor)
                    child = os.open(part, directory_flags, dir_fd=cursor)
                descriptors.append(child)
                cursor = child
            before = os.fstat(cursor)
            named = os.stat(output_dir, follow_symlinks=False)
            if (
                not stat.S_ISDIR(before.st_mode)
                or not stat.S_ISDIR(named.st_mode)
                or (before.st_dev, before.st_ino) != (named.st_dev, named.st_ino)
            ):
                raise BuildError("canonical output directory identity changed")
        except BuildError:
            raise
        except OSError as error:
            raise BuildError(
                "canonical output path contains a symlink or special file"
            ) from error
        finally:
            for descriptor in reversed(descriptors):
                os.close(descriptor)
    else:
        try:
            before = os.lstat(output_dir)
        except FileNotFoundError:
            output_dir.mkdir(parents=True, exist_ok=False)
            before = os.lstat(output_dir)
        if stat.S_ISLNK(before.st_mode) or not stat.S_ISDIR(before.st_mode):
            raise BuildError("canonical output directory is unsafe")
    try:
        resolved = output_dir.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise BuildError("canonical output directory identity changed") from error
    if expected_resolved is not None and resolved != expected_resolved:
        raise BuildError("canonical output path contains a symlink")
    after = os.stat(resolved, follow_symlinks=False)
    if (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino):
        raise BuildError("canonical output directory identity changed")
    if identity_out is not None:
        if identity_out:
            raise BuildError("canonical output identity receiver is not empty")
        identity_out.append((after.st_dev, after.st_ino))
    return resolved


def _read_canonical_file(
    directory_fd: int, path: Path, *, role: str, missing_ok: bool = False
) -> bytes | None:
    """Read one publication file relative to the held output-directory inode."""
    name = path.name
    if name != str(path.relative_to(path.parent)):
        raise BuildError(f"{role} path is unsafe")
    try:
        path_stat = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
    except FileNotFoundError:
        if missing_ok:
            return None
        raise BuildError(f"{role} is missing") from None
    if (
        stat.S_ISLNK(path_stat.st_mode)
        or not stat.S_ISREG(path_stat.st_mode)
        or path_stat.st_nlink != 1
    ):
        raise BuildError(f"{role} is not a safe regular file")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(name, flags, dir_fd=directory_fd)
    except OSError as error:
        raise BuildError(f"{role} is not a safe regular file") from error
    try:
        before = os.fstat(descriptor)
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_nlink != 1
            or (before.st_dev, before.st_ino) != (path_stat.st_dev, path_stat.st_ino)
        ):
            raise BuildError(f"{role} identity changed")
        chunks = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(descriptor)
        if (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_mtime_ns,
        ) != (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
        ):
            raise BuildError(f"{role} changed while read")
        payload = b"".join(chunks)
        if len(payload) != before.st_size:
            raise BuildError(f"{role} changed while read")
        return payload
    finally:
        os.close(descriptor)


def _unlink_canonical_file(directory_fd: int, path: Path) -> None:
    name = path.name
    if name != str(path.relative_to(path.parent)):
        raise BuildError("canonical publication path is unsafe")
    try:
        os.unlink(name, dir_fd=directory_fd)
    except FileNotFoundError:
        pass


def _atomic_write_canonical(directory_fd: int, path: Path, payload: bytes) -> None:
    """Atomically publish one file inside the held output-directory inode."""
    name = path.name
    if name != str(path.relative_to(path.parent)):
        raise BuildError("canonical publication path is unsafe")
    mode = 0o644
    try:
        current = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
    except FileNotFoundError:
        current = None
    if current is not None:
        if not stat.S_ISREG(current.st_mode) or current.st_nlink != 1:
            raise BuildError("canonical publication target is unsafe")
        mode = stat.S_IMODE(current.st_mode)
    temporary = f".{name}.{secrets.token_hex(16)}"
    descriptor: int | None = None
    try:
        descriptor = os.open(
            temporary,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL
            | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
            0o600,
            dir_fd=directory_fd,
        )
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise BuildError("canonical publication write made no progress")
            view = view[written:]
        os.fchmod(descriptor, mode)
        os.fsync(descriptor)
        os.close(descriptor)
        descriptor = None
        os.replace(
            temporary,
            name,
            src_dir_fd=directory_fd,
            dst_dir_fd=directory_fd,
        )
        os.fsync(directory_fd)
        temporary = ""
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if temporary:
            try:
                os.unlink(temporary, dir_fd=directory_fd)
            except FileNotFoundError:
                pass


def _require_canonical_output_domain(output_dir: Path, directory_fd: int) -> None:
    """Bind the lexical publication path to the directory inode held open."""
    opened = os.fstat(directory_fd)
    try:
        named = os.stat(output_dir, follow_symlinks=False)
    except OSError as error:
        raise BuildError("canonical output directory identity changed") from error
    if (
        not stat.S_ISDIR(opened.st_mode)
        or not stat.S_ISDIR(named.st_mode)
        or (opened.st_dev, opened.st_ino) != (named.st_dev, named.st_ino)
    ):
        raise BuildError("canonical output directory identity changed")


def _require_prepared_directory_identity(
    directory_fd: int, expected: tuple[int, int], *, role: str
) -> None:
    opened = os.fstat(directory_fd)
    if (
        not stat.S_ISDIR(opened.st_mode)
        or (opened.st_dev, opened.st_ino) != expected
    ):
        raise BuildError(f"{role} identity changed before lock acquisition")


def _open_canonical_lock_at(
    directory_fd: int, name: str, *, role: str
) -> int:
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(name, flags, 0o600, dir_fd=directory_fd)
    except OSError as error:
        raise BuildError(f"{role} is unsafe") from error
    try:
        _require_canonical_lock_at(directory_fd, name, descriptor, role=role)
        return descriptor
    except Exception:
        os.close(descriptor)
        raise


def _require_canonical_lock_at(
    directory_fd: int, name: str, descriptor: int, *, role: str
) -> None:
    try:
        opened = os.fstat(descriptor)
        named = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
    except OSError as error:
        raise BuildError(f"{role} identity changed") from error
    if (
        not stat.S_ISREG(opened.st_mode)
        or not stat.S_ISREG(named.st_mode)
        or opened.st_nlink != 1
        or named.st_nlink != 1
        or (opened.st_dev, opened.st_ino) != (named.st_dev, named.st_ino)
    ):
        raise BuildError(f"{role} identity changed")


@contextmanager
def _canonical_output_lock(
    output_dir: Path,
    *,
    boundary: Path | None = None,
    lock_anchor: Path | None = None,
):
    """Serialize publication through fixed-boundary and per-output locks."""
    output_identity: list[tuple[int, int]] = []
    output_dir = _prepare_canonical_output_dir(
        output_dir, boundary=boundary, identity_out=output_identity
    )
    key_root = (
        Path(os.path.abspath(boundary)).resolve(strict=True)
        if boundary is not None else output_dir.parent.resolve(strict=True)
    )
    if lock_anchor is None:
        anchor_dir = key_root
        anchor_stat = os.stat(anchor_dir, follow_symlinks=False)
        anchor_identity = [(anchor_stat.st_dev, anchor_stat.st_ino)]
    else:
        anchor_identity: list[tuple[int, int]] = []
        anchor_dir = _prepare_canonical_output_dir(
            lock_anchor, boundary=key_root, identity_out=anchor_identity
        )
    try:
        relative_output = output_dir.relative_to(key_root).as_posix()
    except ValueError as error:
        raise BuildError("canonical output lock escapes its fixed boundary") from error
    anchor_name = (
        ".open-cfw-canonical-output-"
        + sha256(relative_output.encode("utf-8"))
        + ".lock"
    )
    lock_name = ".open-cfw-canonical.lock"
    with _CANONICAL_OUTPUT_THREAD_LOCK:
        anchor_fd: int | None = None
        anchor_descriptor: int | None = None
        directory_fd: int | None = None
        descriptor: int | None = None
        try:
            directory_fd = os.open(
                output_dir,
                os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
            )
            _require_prepared_directory_identity(
                directory_fd,
                output_identity[0],
                role="canonical output directory",
            )
            _require_canonical_output_domain(output_dir, directory_fd)
            anchor_fd = os.open(
                anchor_dir,
                os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
            )
            _require_prepared_directory_identity(
                anchor_fd,
                anchor_identity[0],
                role="canonical lock anchor",
            )
            _require_canonical_output_domain(anchor_dir, anchor_fd)
            anchor_descriptor = _open_canonical_lock_at(
                anchor_fd, anchor_name, role="canonical boundary lock"
            )
            fcntl.flock(anchor_descriptor, fcntl.LOCK_EX)
            _require_canonical_lock_at(
                anchor_fd,
                anchor_name,
                anchor_descriptor,
                role="canonical boundary lock",
            )
            _require_canonical_output_domain(anchor_dir, anchor_fd)
            _require_prepared_directory_identity(
                directory_fd,
                output_identity[0],
                role="canonical output directory",
            )
            _require_canonical_output_domain(output_dir, directory_fd)
            descriptor = _open_canonical_lock_at(
                directory_fd, lock_name, role="canonical publication lock"
            )
        except Exception as error:
            if descriptor is not None:
                os.close(descriptor)
                descriptor = None
            if directory_fd is not None:
                os.close(directory_fd)
                directory_fd = None
            if anchor_descriptor is not None:
                try:
                    fcntl.flock(anchor_descriptor, fcntl.LOCK_UN)
                finally:
                    os.close(anchor_descriptor)
                anchor_descriptor = None
            if anchor_fd is not None:
                os.close(anchor_fd)
                anchor_fd = None
            if isinstance(error, BuildError):
                raise
            raise BuildError("canonical publication lock is unsafe") from error
        try:
            if directory_fd is None or descriptor is None:
                raise BuildError("canonical publication lock is unsafe")
            handle = os.fdopen(descriptor, "r+b", closefd=False)
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                _require_canonical_lock_at(
                    anchor_fd,
                    anchor_name,
                    anchor_descriptor,
                    role="canonical boundary lock",
                )
                _require_canonical_lock_at(
                    directory_fd,
                    lock_name,
                    descriptor,
                    role="canonical publication lock",
                )
                _require_canonical_output_domain(anchor_dir, anchor_fd)
                _require_canonical_output_domain(output_dir, directory_fd)
                yield directory_fd
                _require_canonical_output_domain(output_dir, directory_fd)
                _require_canonical_output_domain(anchor_dir, anchor_fd)
                _require_canonical_lock_at(
                    directory_fd,
                    lock_name,
                    descriptor,
                    role="canonical publication lock",
                )
                _require_canonical_lock_at(
                    anchor_fd,
                    anchor_name,
                    anchor_descriptor,
                    role="canonical boundary lock",
                )
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
                handle.close()
        finally:
            if descriptor is not None:
                os.close(descriptor)
            if directory_fd is not None:
                os.close(directory_fd)
            if anchor_descriptor is not None:
                try:
                    fcntl.flock(anchor_descriptor, fcntl.LOCK_UN)
                finally:
                    os.close(anchor_descriptor)
            if anchor_fd is not None:
                os.close(anchor_fd)


def _capture_canonical_generation(
    directory_fd: int,
    overlay_path: Path,
    component_path: Path,
    report_path: Path,
    additional_paths: tuple[Path, ...] = (),
) -> dict[Path, tuple[bool, bytes]]:
    paths = (overlay_path, component_path, *additional_paths, report_path)
    previous: dict[Path, tuple[bool, bytes]] = {}
    for path in paths:
        payload = _read_canonical_file(
            directory_fd, path,
            role="canonical existing generation", missing_ok=True
        )
        previous[path] = (payload is not None, payload or b"")
    if previous[report_path][0]:
        try:
            report = json.loads(previous[report_path][1].decode("utf-8"))
            overlay = report["overlay"]
            component = report["component"]
            if not isinstance(overlay, dict) or not isinstance(component, dict):
                raise TypeError
            observed = (
                int(overlay.get("size", -1)),
                overlay.get("sha256"),
                int(component.get("size", -1)),
                component.get("sha256"),
            )
        except (
            KeyError,
            TypeError,
            ValueError,
            UnicodeDecodeError,
            json.JSONDecodeError,
        ):
            raise BuildError("canonical existing generation identity changed") \
                from None
        if (
            not previous[overlay_path][0]
            or not previous[component_path][0]
            or observed[0] != len(previous[overlay_path][1])
            or observed[1] != sha256(previous[overlay_path][1])
            or observed[2] != len(previous[component_path][1])
            or observed[3] != sha256(previous[component_path][1])
        ):
            raise BuildError("canonical existing generation identity changed")
        records = report.get("canonical_observation", {}).get(
            "intermediate_artifacts", {}
        )
        if not isinstance(records, dict):
            records = {}
        by_name = {
            item.get("artifact"): item
            for item in records.values()
            if isinstance(item, dict)
        }
        cff_records = report.get("canonical_observation", {}).get(
            "freetype_cff", {}
        ).get("section_artifacts", {})
        if isinstance(cff_records, dict):
            by_name.update({
                item.get("artifact"): item
                for item in cff_records.values()
                if isinstance(item, dict)
            })
        for path in additional_paths:
            existed, payload = previous[path]
            record = by_name.get(path.name)
            if (
                isinstance(record, dict) != existed
                or existed and (
                    record.get("size") != len(payload)
                    or record.get("sha256") != sha256(payload)
                )
            ):
                raise BuildError("canonical existing generation identity changed")
    elif any(previous[path][0] for path in paths if path != report_path):
        raise BuildError("canonical existing generation identity changed")
    return previous


def _restore_canonical_generation(
    directory_fd: int,
    previous: dict[Path, tuple[bool, bytes]],
    overlay_path: Path,
    component_path: Path,
    report_path: Path,
    additional_paths: tuple[Path, ...] = (),
) -> None:
    """Restore a prior complete generation, with its report written last."""
    _unlink_canonical_file(directory_fd, report_path)
    artifact_paths = (overlay_path, component_path, *additional_paths)
    for path in artifact_paths:
        existed, payload = previous[path]
        if existed:
            _atomic_write_canonical(directory_fd, path, payload)
        else:
            _unlink_canonical_file(directory_fd, path)
    for path in artifact_paths:
        existed, payload = previous[path]
        observed = _read_canonical_file(
            directory_fd, path,
            role="canonical rollback output", missing_ok=True
        )
        if (observed is not None) != existed or (existed and observed != payload):
            raise BuildError("canonical generation rollback failed")
    report_existed, report_payload = previous[report_path]
    if report_existed:
        _atomic_write_canonical(directory_fd, report_path, report_payload)
    observed_report = _read_canonical_file(
        directory_fd, report_path,
        role="canonical rollback report", missing_ok=True
    )
    if ((observed_report is not None) != report_existed or
            (report_existed and observed_report != report_payload)):
        _unlink_canonical_file(directory_fd, report_path)
        raise BuildError("canonical generation rollback failed")


def _publish_canonical_outputs(
    *,
    root: Path,
    config_path: Path,
    config: dict[str, Any],
    input_snapshot: dict[str, tuple[int, str]],
    overlay_path: Path,
    final_overlay: bytes,
    component_path: Path,
    final_component: bytes,
    report_path: Path,
    report: dict[str, Any],
    additional_artifacts: dict[Path, bytes] | None = None,
    publication_boundary: Path | None = None,
    publication_lock_anchor: Path | None = None,
) -> None:
    """Publish a validated artifact generation, then its report commit marker."""
    report_payload = (
        json.dumps(report, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    expected_overlay = report.get("overlay", {})
    expected_component = report.get("component", {})
    if (expected_overlay.get("size") != len(final_overlay) or
            expected_overlay.get("sha256") != sha256(final_overlay) or
            expected_component.get("size") != len(final_component) or
            expected_component.get("sha256") != sha256(final_component)):
        raise BuildError("canonical report artifact identity changed")
    additional_artifacts = additional_artifacts or {}
    observation = report.get("canonical_observation", {})
    final_records = observation.get("final_artifacts", {})
    if observation:
        expected_final_records = {
            "overlay": {
                "artifact": overlay_path.name,
                "size": len(final_overlay),
                "sha256": sha256(final_overlay),
            },
            "component": {
                "artifact": component_path.name,
                "size": len(final_component),
                "sha256": sha256(final_component),
            },
        }
        if final_records != expected_final_records:
            raise BuildError("canonical final artifact identity changed")
    records = observation.get("intermediate_artifacts", {})
    if additional_artifacts:
        if set(records) != set(_CANONICAL_INTERMEDIATE_NAMES):
            raise BuildError("canonical intermediate artifact schema changed")
        for key, name in _CANONICAL_INTERMEDIATE_NAMES.items():
            path = next(
                (candidate for candidate in additional_artifacts if candidate.name == name),
                None,
            )
            record = records.get(key)
            if (
                path is None
                or not isinstance(record, dict)
                or set(record) != {"artifact", "size", "sha256"}
                or record["artifact"] != name
                or record["size"] != len(additional_artifacts[path])
                or record["sha256"] != sha256(additional_artifacts[path])
            ):
                raise BuildError("canonical intermediate artifact identity changed")
    elif records:
        raise BuildError("canonical intermediate artifacts were not supplied")
    all_paths = (
        overlay_path, component_path, *additional_artifacts, report_path
    )
    if len(set(all_paths)) != len(all_paths):
        raise BuildError("canonical publication paths must be unique")
    for path in all_paths:
        if path.name != str(path.relative_to(path.parent)):
            raise BuildError("canonical publication artifact name is unsafe")
    parents = {
        path.parent.absolute() for path in all_paths
    }
    if len(parents) != 1:
        raise BuildError("canonical outputs must share one publication directory")
    with _canonical_output_lock(
        report_path.parent,
        boundary=publication_boundary,
        lock_anchor=publication_lock_anchor,
    ) as directory_fd:
        _require_canonical_output_domain(report_path.parent, directory_fd)
        _require_canonical_inputs_unchanged(
            root, config_path, config, input_snapshot
        )
        previous = _capture_canonical_generation(
            directory_fd,
            overlay_path,
            component_path,
            report_path,
            tuple(additional_artifacts),
        )
        # The report is the completed-generation marker.  Remove it before
        # changing either artifact so no reader can bless an in-flight pair.
        _unlink_canonical_file(directory_fd, report_path)
        try:
            _atomic_write_canonical(directory_fd, overlay_path, final_overlay)
            _atomic_write_canonical(directory_fd, component_path, final_component)
            for path, payload in additional_artifacts.items():
                _atomic_write_canonical(directory_fd, path, payload)
            if (_read_canonical_file(
                    directory_fd, overlay_path,
                    role="canonical published artifact"
                ) != final_overlay or
                    _read_canonical_file(
                        directory_fd, component_path,
                        role="canonical published artifact"
                    ) != final_component or any(
                        _read_canonical_file(
                            directory_fd, path,
                            role="canonical published artifact"
                        ) != payload
                        for path, payload in additional_artifacts.items()
                    )):
                raise BuildError("canonical published artifact readback changed")
            # Catch source drift during the two artifact renames before
            # committing the new generation with its report.
            _require_canonical_inputs_unchanged(
                root, config_path, config, input_snapshot
            )
            _require_canonical_output_domain(report_path.parent, directory_fd)
            _atomic_write_canonical(directory_fd, report_path, report_payload)
            if (_read_canonical_file(
                    directory_fd, report_path,
                    role="canonical published report"
                ) != report_payload or
                    _read_canonical_file(
                        directory_fd, overlay_path,
                        role="canonical published artifact"
                    ) != final_overlay or
                    _read_canonical_file(
                        directory_fd, component_path,
                        role="canonical published artifact"
                    ) != final_component or any(
                        _read_canonical_file(
                            directory_fd, path,
                            role="canonical published artifact"
                        ) != payload
                        for path, payload in additional_artifacts.items()
                    )):
                raise BuildError("canonical published generation readback changed")
            _require_canonical_output_domain(report_path.parent, directory_fd)
        except Exception:
            try:
                _restore_canonical_generation(
                    directory_fd,
                    previous,
                    overlay_path,
                    component_path,
                    report_path,
                    tuple(additional_artifacts),
                )
            except Exception as rollback_error:
                _unlink_canonical_file(directory_fd, report_path)
                raise BuildError("canonical generation rollback failed") \
                    from rollback_error
            raise


def _load_liblc3_builder() -> Any:
    path = COMPONENT_ROOT.parent / "liblc3_ltpf" / "build_component.py"
    specification = importlib.util.spec_from_file_location(
        "open_cfw_liblc3_ltpf_builder", path
    )
    if specification is None or specification.loader is None:
        raise BuildError(f"cannot load bounded liblc3 provider builder: {path}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def _load_pt_protocol_builder() -> Any:
    path = COMPONENT_ROOT.parent / "pt_protocol" / "build_component.py"
    specification = importlib.util.spec_from_file_location(
        "open_cfw_pt_protocol_builder", path
    )
    if specification is None or specification.loader is None:
        raise BuildError(f"cannot load bounded PT protocol builder: {path}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def _load_cff_scatter_builder() -> Any:
    path = CFF_COMPONENT_ROOT / "build_component.py"
    specification = importlib.util.spec_from_file_location(
        "open_cfw_freetype_cff_scatter_builder", path
    )
    if specification is None or specification.loader is None:
        raise BuildError(f"cannot load FreeType CFF scatter builder: {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def _load_liblc3_service_audio_builder() -> Any:
    path = LC3_SERVICE_ROOT / "build_service_audio_production_replay.py"
    specification = importlib.util.spec_from_file_location(
        "open_cfw_liblc3_service_audio_builder", path
    )
    if specification is None or specification.loader is None:
        raise BuildError(f"cannot load LC3 service-audio builder: {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def _stage_config(config: dict[str, Any], profile: str) -> dict[str, Any]:
    """Return the byte-identical pre-provider core configuration."""
    stage = copy.deepcopy(config)
    expected = stage.get("core_stage_expected")
    if not isinstance(expected, dict):
        raise BuildError("canonical core config lacks core_stage_expected")
    stage["expected"] = expected
    profiles = stage.get("toolchain_profiles", {})
    if profile != "apple-clang":
        selected = profiles.get(profile)
        if not isinstance(selected, dict):
            raise BuildError(f"unknown canonical toolchain profile {profile!r}")
        selected_expected = selected.get("core_stage_expected")
        if not isinstance(selected_expected, dict):
            raise BuildError(
                f"canonical profile {profile!r} lacks core_stage_expected"
            )
        selected["expected"] = selected_expected
    return stage


def _provider_profile(config: dict[str, Any], profile: str) -> dict[str, Any]:
    providers = config.get("post_link_providers")
    if not isinstance(providers, dict):
        raise BuildError("canonical core config lacks post_link_providers")
    provider = providers.get("liblc3_ltpf")
    if not isinstance(provider, dict):
        raise BuildError("canonical core config lacks liblc3_ltpf provider")
    profiles = provider.get("profiles")
    if not isinstance(profiles, dict) or not isinstance(profiles.get(profile), dict):
        raise BuildError(f"liblc3 provider lacks profile {profile!r}")
    return profiles[profile]


def _verify_pt_provider_profile(
    config: dict[str, Any], profile: str, report: dict[str, Any]
) -> None:
    provider = config.get("post_link_providers", {}).get("pt_protocol")
    profiles = provider.get("profiles") if isinstance(provider, dict) else None
    expected = profiles.get(profile) if isinstance(profiles, dict) else None
    if not isinstance(expected, dict):
        raise BuildError(f"PT protocol provider lacks profile {profile!r}")
    placement = report.get("placement")
    if not isinstance(placement, dict):
        raise BuildError("PT protocol provider placement report missing")
    observed = {
        "payload_size": int(placement.get("loadable_size", -1)),
        "payload_sha256": placement.get("payload_sha256"),
        "interval_sha256": placement.get("interval_sha256"),
    }
    if observed != expected:
        raise BuildError(
            f"PT protocol provider profile {profile!r} differs: "
            f"expected {expected!r}, observed {observed!r}"
        )


def _verify_pt_provider_license_contract(
    config: dict[str, Any], report: dict[str, Any]
) -> None:
    """Bind the mixed linked provider to every exact source license record."""
    provider = config.get("post_link_providers", {}).get("pt_protocol")
    source_report = report.get("source")
    if not isinstance(provider, dict) or not isinstance(source_report, dict):
        raise BuildError("PT protocol provider license contract missing")
    configured = provider.get("sources")
    observed = source_report.get("files")
    if (
        provider.get("license") != PT_AGGREGATE_LICENSE
        or source_report.get("license") != PT_AGGREGATE_LICENSE
        or not isinstance(configured, list)
        or observed != configured
        or len(configured) != 29
    ):
        raise BuildError("PT protocol provider license contract changed")
    paths: set[str] = set()
    counts = {license_id: 0 for license_id in PT_SOURCE_LICENSE_COUNTS}
    for record in configured:
        if not isinstance(record, dict):
            raise BuildError("PT protocol source license record changed")
        license_id = record.get("license")
        expected_keys = {"path", "size", "sha256", "license"}
        if license_id == "Apache-2.0":
            expected_keys.update(PT_APACHE_SOURCE_METADATA)
        if set(record) != expected_keys:
            raise BuildError("PT protocol source license record changed")
        path = record["path"]
        size = record["size"]
        source_sha256 = record["sha256"]
        if (
            not isinstance(path, str)
            or path in paths
            or type(size) is not int
            or size <= 0
            or not isinstance(source_sha256, str)
            or len(source_sha256) != 64
            or any(value not in "0123456789abcdef" for value in source_sha256)
            or license_id not in counts
        ):
            raise BuildError("PT protocol source license record changed")
        paths.add(path)
        counts[license_id] += 1
    apache_paths = {
        record["path"] for record in configured
        if record["license"] == "Apache-2.0"
    }
    if (
        counts != PT_SOURCE_LICENSE_COUNTS
        or apache_paths != {PT_APACHE_SOURCE}
        or any(
            record.get(key) != value
            for record in configured
            if record["path"] == PT_APACHE_SOURCE
            for key, value in PT_APACHE_SOURCE_METADATA.items()
        )
        or [record["path"] for record in configured] != sorted(paths)
    ):
        raise BuildError("PT protocol source license census changed")


PT_SOURCE_UART_ROUTES = (
    ("open_cfw_retained_box_uart_product_test", "R_ARM_THM_CALL",
     0x0056F4A0, 88, 10),
    ("open_cfw_retained_box_uart_execute", "R_ARM_THM_CALL", 0x0056F92C,
     148, 10),
)


def _verify_pt_source_uart_ingress(
    config: dict[str, Any], stage_report: dict[str, Any], profile: str,
    stage_expected: dict[str, Any], *, observe_unpinned: bool = False,
) -> tuple[bool, dict[str, Any]]:
    matches = [item for item in config.get("relocated_leaves", [])
               if item.get("function") == "open_cfw_box_uart_handle"]
    if len(matches) != 1 or matches[0].get("strict_relocation_contract") is not True:
        raise BuildError("canonical PT source-UART ingress contract missing")
    configured = tuple(sorted(
        (item.get("symbol"), item.get("type"),
         int(item.get("target_address", -1)), int(item.get("offset", -1)))
        for item in matches[0].get("relocations", [])
        if item.get("symbol") in {
            "open_cfw_retained_box_uart_product_test",
            "open_cfw_retained_box_uart_execute",
        }
    ))
    expected_configured = tuple(sorted(
        (symbol, kind, target, offset)
        for symbol, kind, target, offset, _type_id in PT_SOURCE_UART_ROUTES
    ))
    if configured != expected_configured:
        raise BuildError("canonical PT source-UART ingress addresses changed")
    stage_profile = stage_report.get("toolchain", {}).get("profile")
    stage_overlay = stage_report.get("overlay")
    effective_stage_expected = (
        {
            "overlay_size": int(stage_overlay.get("size", -1)),
            "overlay_sha256": stage_overlay.get("sha256"),
        }
        if observe_unpinned and isinstance(stage_overlay, dict)
        else stage_expected
    )
    if (stage_profile != profile or not isinstance(stage_overlay, dict) or
            int(stage_overlay.get("size", -1)) !=
            int(effective_stage_expected.get("overlay_size", -2)) or
            stage_overlay.get("sha256") !=
            effective_stage_expected.get("overlay_sha256")):
        raise BuildError("canonical PT source-UART stage identity changed")
    enabled_profiles = matches[0].get("profiles")
    if (enabled_profiles is not None and
            (not isinstance(enabled_profiles, list) or
             any(not isinstance(item, str) for item in enabled_profiles))):
        raise BuildError("canonical PT source-UART profile contract changed")
    routed = enabled_profiles is None or profile in enabled_profiles
    reports = [
        item for item in stage_report.get("relocated_leaves", [])
        if item.get("extraction", {}).get("function") ==
        "open_cfw_box_uart_handle"
    ]
    receipt_leaf_expected = matches[0].get("expected")
    if not isinstance(receipt_leaf_expected, dict):
        raise BuildError("canonical PT source-UART leaf pins missing")
    if routed:
        if len(reports) != 1:
            raise BuildError("canonical PT source-UART route receipt missing")
        extraction = reports[0].get("extraction", {})
        pins = reports[0].get("pins", {})
        leaf_expected = (
            pins if observe_unpinned else matches[0].get("expected")
        )
        if not isinstance(leaf_expected, dict):
            raise BuildError("canonical PT source-UART leaf pins missing")
        receipt_leaf_expected = leaf_expected
        for source in (extraction, pins):
            if any(source.get(key) != leaf_expected.get(key) for key in (
                "size", "sha256", "unrelocated_sha256", "alignment"
            )):
                raise BuildError("canonical PT source-UART leaf identity changed")
            observed = tuple(sorted(
                (item.get("symbol"), item.get("type"),
                 int(item.get("target_address", -1)),
                 int(item.get("offset", -1)),
                 int(item.get("type_id", 10 if source is pins else -1)))
                for item in source.get("relocations", [])
                if item.get("symbol") in {
                    "open_cfw_retained_box_uart_product_test",
                    "open_cfw_retained_box_uart_execute",
                }
            ))
            if observed != tuple(sorted(PT_SOURCE_UART_ROUTES)):
                raise BuildError(
                    "canonical PT source-UART route receipt changed"
                )
        if pins.get("offset") != leaf_expected.get("offset"):
            raise BuildError("canonical PT source-UART leaf identity changed")
    elif reports:
        raise BuildError("inactive PT source-UART leaf appeared in stage report")
    receipt = {
        "mode": (
            "source_overlay_relocation" if routed
            else "authenticated_donor_direct"
        ),
        "profile": profile,
        "function": "open_cfw_box_uart_handle",
        "strict_relocation_contract": True,
        "profile_route_active": routed,
        "stage_overlay": {
            "size": int(stage_overlay["size"]),
            "sha256": stage_overlay["sha256"],
        },
        "leaf": {
            "size": int(receipt_leaf_expected["size"]),
            "sha256": receipt_leaf_expected["sha256"],
            "unrelocated_sha256": receipt_leaf_expected[
                "unrelocated_sha256"
            ],
            "alignment": int(receipt_leaf_expected["alignment"]),
            "offset": int(receipt_leaf_expected["offset"]),
        },
        "relocations": [
            {
                "symbol": symbol,
                "type": kind,
                "target_address": target,
                "offset": offset,
                "type_id": type_id,
            }
            for symbol, kind, target, offset, type_id in PT_SOURCE_UART_ROUTES
        ],
    }
    return routed, receipt


def _verify_final(
    observed: dict[str, Any], expected: dict[str, Any], *, record: bool
) -> None:
    if record:
        return
    for key in (
        "overlay_size",
        "overlay_sha256",
        "component_size",
        "component_sha256",
    ):
        if observed[key] != expected.get(key):
            raise BuildError(
                f"canonical post-link {key} differs: expected "
                f"{expected.get(key)!r}, observed {observed[key]!r}"
            )


def build(
    *,
    root: Path,
    config_path: Path,
    output_dir: Path,
    clang: str,
    toolchain_profile: str | None = None,
    record_profile: bool = False,
    record_canonical: bool = False,
) -> dict[str, Any]:
    """Build the default Apollo-main provider path, including liblc3 LTPF."""
    if record_profile:
        raise BuildError(
            "recording a core-stage profile alone would bypass canonical "
            "post-link providers; review and pin both stages together"
        )
    pt_builder = _load_pt_protocol_builder()
    lc3_service_builder = _load_liblc3_service_audio_builder()
    cff_builder = _load_cff_scatter_builder()
    toolchain_identity: dict[str, Any] | None = None
    recorded_builtin_include: Path | None = None
    if record_canonical:
        pt_ld = pt_builder._tool("OPENCFW_LLD", "ld.lld", "lld")
        pt_nm = pt_builder._tool("OPENCFW_NM", "llvm-nm", "nm")
        toolchain_identity = pt_builder._toolchain_identity(clang, pt_ld, pt_nm)
        clang = toolchain_identity["executables"]["compiler"]["invocation_path"]
        recorded_builtin_include = (
            Path(toolchain_identity["compiler_resource_headers"]["resource_dir"])
            / "include"
        )
    config_payload, config, input_snapshot = _canonical_input_state(
        root, config_path
    )
    _toolchain, final_expected, profile = resolve_toolchain_profile(
        config, toolchain_profile
    )
    stage = _stage_config(config, profile)
    provider_expected = _provider_profile(config, profile)

    output_dir = _prepare_canonical_output_dir(
        output_dir, boundary=root if record_canonical else None
    )
    with tempfile.TemporaryDirectory(
        prefix=".tmp-open-cfw-apollo-canonical-", dir=root
    ) as tmp:
        temporary = Path(tmp)
        stage_output = temporary / "core-stage"
        stage_config_path = temporary / "core-stage.json"
        stage_config_path.write_text(
            json.dumps(stage, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        stage_report = overlay_build(
            root=root,
            config_path=stage_config_path,
            output_dir=stage_output,
            clang=clang,
            toolchain_profile=profile,
            record_profile=False,
            observe_unpinned=record_canonical,
            expected_builtin_include_dir=recorded_builtin_include,
        )
        stage_pin_observation = (
            _canonical_stage_pin_report(stage_report)
            if record_canonical else None
        )
        stage_expected = (
            stage["expected"] if profile == "apple-clang" else
            stage["toolchain_profiles"][profile]["expected"]
        )
        source_uart_routed, source_uart_route_receipt = (
            _verify_pt_source_uart_ingress(
                config,
                stage_report,
                profile,
                stage_expected,
                observe_unpinned=record_canonical,
            )
        )
        stage_component_path = stage_output / "ota_s200_firmware_ota.bin"
        stage_component = stage_component_path.read_bytes()
        stage_overlay = (stage_output / config["overlay_artifact"]).read_bytes()
        stage_component_pin = {
            "size": len(stage_component),
            "sha256": sha256(stage_component),
        }

        provider_output = temporary / "liblc3"
        provider_builder = _load_liblc3_builder()
        provider_report = provider_builder.build(
            config_path=COMPONENT_ROOT.parent / "liblc3_ltpf" / "overlay.json",
            output_dir=provider_output,
            clang=clang,
            profile=profile,
            record=record_canonical,
            base_path_override=stage_component_path,
            base_expected_override=stage_component_pin,
            expected_override=provider_expected,
            placement_override=provider_expected.get("placement"),
            expected_builtin_include_dir=recorded_builtin_include,
        )
        liblc3_component_path = provider_output / "ota_s200_firmware_ota.bin"
        liblc3_component = liblc3_component_path.read_bytes()
        liblc3_payload = b""
        if record_canonical:
            liblc3_payload = (
                provider_output / "liblc3_ltpf.text.bin"
            ).read_bytes()
            if (
                len(liblc3_payload) != int(provider_report["overlay"]["size"])
                or sha256(liblc3_payload) != provider_report["overlay"]["sha256"]
            ):
                raise BuildError("canonical liblc3 payload artifact changed")
        pt_output = temporary / "pt-protocol"
        pt_report = pt_builder.build(
            base_path=liblc3_component_path,
            output_dir=pt_output,
            clang=clang,
            profile=profile,
            base_expected={
                "size": len(liblc3_component),
                "sha256": sha256(liblc3_component),
            },
            ingress_authentication_base_path=root / config["base"]["path"],
            ingress_authentication_base_expected={
                "size": int(config["base"]["size"]),
                "sha256": config["base"]["sha256"],
            },
            source_uart_routed=source_uart_routed,
            source_uart_route_receipt=source_uart_route_receipt,
            record_toolchain_identity=record_canonical,
            expected_builtin_include_dir=recorded_builtin_include,
        )
        _verify_pt_provider_license_contract(config, pt_report)
        if record_canonical:
            if pt_report.get("toolchain_identity") != toolchain_identity:
                raise BuildError("canonical toolchain identity changed during build")
        if not record_canonical:
            _verify_pt_provider_profile(config, profile, pt_report)
        pt_component_path = pt_output / "ota_s200_firmware_ota.bin"
        pt_component = pt_component_path.read_bytes()
        if record_canonical:
            pt_interval = (pt_output / "pt-protocol-in-place.bin").read_bytes()
            pt_placement = pt_report["placement"]
            if (
                len(pt_interval) != int(pt_placement["capacity"])
                or sha256(pt_interval) != pt_placement["interval_sha256"]
            ):
                raise BuildError("canonical PT interval artifact changed")
        route_core_report = copy.deepcopy(stage_report)
        route_core_report["component"].update({
            "size": len(pt_component), "sha256": sha256(pt_component)
        })
        if not isinstance(provider_report["placement"].get("sections"), dict):
            route_core_report["overlay"]["overlay_end_exclusive"] = (
                int(config["run_base"]) + len(pt_component)
                - int(config["preamble_bytes"])
            )
        route_core_report["overlay"]["post_link_providers"] = {
            "liblc3_ltpf": {
                "placement": copy.deepcopy(provider_report["placement"]),
                "payload": {
                    "size": int(provider_report["overlay"]["size"]),
                    "sha256": provider_report["overlay"]["sha256"],
                },
            },
            "pt_protocol": {
                "placement": copy.deepcopy(pt_report["placement"]),
            },
        }
        lc3_service_output = temporary / "liblc3-service-audio"
        lc3_service_report = lc3_service_builder.route_component(
            base_component=pt_component_path,
            core_config=config,
            core_report=route_core_report,
            output_dir=lc3_service_output,
            profile=profile,
        )
        pre_cff_component_path = (
            lc3_service_output / "ota_s200_firmware_ota.bin"
        )
        pre_cff_component = pre_cff_component_path.read_bytes()
        if (
            int(lc3_service_report["component"]["size"])
            != len(pre_cff_component)
            or lc3_service_report["component"]["sha256"]
            != sha256(pre_cff_component)
        ):
            raise BuildError("LC3 service-audio component receipt changed")
        cff_output = temporary / "freetype-cff-scatter"
        cff_report = cff_builder.build(
            profile=profile,
            base_component=pre_cff_component_path,
            output_dir=cff_output,
            host_slots=lc3_service_report["residual_host_slots"],
            base_expected_override=lc3_service_report["component"],
            observe=record_canonical,
        )
        final_component = (
            cff_output / "ota_s200_firmware_ota.bin"
        ).read_bytes()
        cff_section_artifacts = {
            section["name"]: (
                cff_output / f"{section['name'][1:]}.bin"
            ).read_bytes()
            for section in cff_report["placement"]["sections"]
        }
        if (
            int(cff_report["component"]["size"]) != len(final_component)
            or cff_report["component"]["sha256"] != sha256(final_component)
        ):
            raise BuildError("FreeType CFF component receipt changed")
        official_size = int(stage_report["base"]["size"])
        placement_sections = provider_report["placement"].get("sections")
        final_overlay = (
            stage_overlay
            if isinstance(placement_sections, dict)
            else pt_component[official_size:]
        )

    observed = {
        "overlay_size": len(final_overlay),
        "overlay_sha256": sha256(final_overlay),
        "component_size": len(final_component),
        "component_sha256": sha256(final_component),
    }
    _verify_final(observed, final_expected, record=record_canonical)

    overlay_report = stage_report["overlay"]
    component_report = stage_report["component"]
    stage_overlay_size = int(overlay_report["size"])
    stage_component_size = int(component_report["size"])
    provider_runtime = int(provider_report["placement"]["runtime_address"])
    provider_payload_size = int(provider_report["overlay"]["size"])
    cave_placement = isinstance(placement_sections, dict)
    if cave_placement:
        if len(pt_component) != stage_component_size:
            raise BuildError("canonical cave provider changed component size")
        admitted_source_bytes = sum(
            int(item["size"]) for item in placement_sections.values()
        )
        if admitted_source_bytes != provider_payload_size:
            raise BuildError("canonical liblc3 cave byte accounting changed")
        generated_delta = -admitted_source_bytes + 4
    else:
        admitted_source_bytes = len(pt_component) - stage_component_size
        if admitted_source_bytes < provider_payload_size:
            raise BuildError("canonical appended provider accounting changed")
        generated_delta = 4
        provider_start = int(provider_report["placement"]["file_offset"])
        for name, function in provider_report["overlay"]["functions"].items():
            overlay_report["functions"][name] = {
                "offset": provider_start - official_size + int(function["offset"]),
                "size": int(function["size"]),
            }
        overlay_report["overlay_end_exclusive"] = (
            config["run_base"] + len(pt_component) - config["preamble_bytes"]
        )
        overlay_report["overlay_end_exclusive_hex"] = (
            f"0x{overlay_report['overlay_end_exclusive']:08X}"
        )
    patch = provider_report["patch_site"]
    overlay_report["patched_sites"].append(
        {
            "branch": "bl",
            **(
                {"expected_hex": patch["expected_hex"]}
                if "expected_hex" in patch
                else {
                    "expected_size": patch["expected_size"],
                    "expected_sha256": patch["expected_sha256"],
                }
            ),
            "name": patch["name"],
            "payload_offset": int(patch["file_offset"]),
            "replacement_hex": patch["replacement_hex"],
            "runtime_address": int(patch["runtime_address"]),
            "runtime_address_hex": f"0x{int(patch['runtime_address']):08X}",
            "target_address": int(patch["decoded_target"]),
            "target_address_hex": f"0x{int(patch['decoded_target']):08X}",
            "target_function": patch["target_function"],
        }
    )
    if pt_report["patch_sites"]:
        raise BuildError("canonical PT provider unexpectedly requires patch sites")
    overlay_report.update(
        {
            "size": len(final_overlay),
            "sha256": sha256(final_overlay),
            **(
                {
                    "cave_functions": {
                        name: {
                            "runtime_address": provider_runtime
                            + int(function["offset"]),
                            "runtime_address_hex": (
                                f"0x{provider_runtime + int(function['offset']):08X}"
                            ),
                            "size": int(function["size"]),
                        }
                        for name, function in provider_report["overlay"][
                            "functions"
                        ].items()
                    }
                }
                if cave_placement
                else {}
            ),
            "post_link_providers": {
                "liblc3_ltpf": {
                    "license": "Apache-2.0",
                    "placement": (
                        placement_sections
                        if cave_placement
                        else {
                            "file_offset": provider_report["placement"][
                                "file_offset"
                            ],
                            "runtime_address": provider_runtime,
                        }
                    ),
                    "payload": {
                        "size": provider_payload_size,
                        "sha256": provider_report["overlay"]["sha256"],
                    },
                    "component": provider_report["component"],
                    "link": {
                        key: provider_report["overlay"][key]
                        for key in (
                            "text_size",
                            "rodata",
                            "text_relocations",
                            "dispatch_entries",
                            "discarded_cantunwind_rows",
                            "runtime_dependencies",
                            "section_runtime_addresses",
                        )
                    },
                    "historical_non_corpus_routing": (
                        provider_report["historical_non_corpus_routing"]
                    ),
                },
                "liblc3_service_audio": {
                    "license": "Apache-2.0 AND MIT",
                    "component": copy.deepcopy(
                        lc3_service_report["component"]
                    ),
                    "suffix": copy.deepcopy(lc3_service_report["suffix"]),
                    "target_runtime": copy.deepcopy(
                        lc3_service_report["target_runtime"]
                    ),
                    "lc3_finalization": copy.deepcopy(
                        lc3_service_report["lc3_finalization"]
                    ),
                    "service_audio_entry_guards": copy.deepcopy(
                        lc3_service_report["service_audio_entry_guards"]
                    ),
                    "routing": copy.deepcopy(lc3_service_report["routing"]),
                    "hardware": copy.deepcopy(lc3_service_report["hardware"]),
                },
                "pt_protocol": {
                    "license": PT_AGGREGATE_LICENSE,
                    "sources": copy.deepcopy(pt_report["source"]["files"]),
                    "placement": pt_report["placement"],
                    "payload": {
                        "size": int(pt_report["placement"]["loadable_size"]),
                        "sha256": pt_report["placement"]["payload_sha256"],
                    },
                    "source_provider_routes": pt_report[
                        "source_provider_routes"
                    ],
                    "entry_symbols": pt_report["symbols"],
                    "ingress_sites": pt_report["ingress_sites"],
                    "source_uart_route_receipt": pt_report[
                        "source_uart_route_receipt"
                    ],
                    "hardware": pt_report["hardware"],
                },
                "freetype_cff": {
                    "license": "FTL AND MIT",
                    "component": copy.deepcopy(cff_report["component"]),
                    "placement": copy.deepcopy(cff_report["placement"]),
                    "module_class_patch": copy.deepcopy(
                        cff_report["module_class_patch"]
                    ),
                    "scatter_manifest": copy.deepcopy(
                        cff_report["scatter_manifest"]
                    ),
                    "receipt_sha256": cff_report["receipt_sha256"],
                    "hardware": {
                        "validation": "blocked by unavailable physical evidence",
                        "qualification_complete": False,
                    },
                },
            },
        }
    )
    patch_bytes = len(bytes.fromhex(patch["replacement_hex"]))
    pt_patch_bytes = 0
    pt_capacity = int(pt_report["placement"]["capacity"])
    pt_payload_size = int(pt_report["placement"]["loadable_size"])
    pt_padding_size = int(pt_report["placement"]["padding_size"])
    if pt_payload_size + pt_padding_size != pt_capacity:
        raise BuildError("canonical PT in-place byte accounting changed")
    cff_sections = cff_report["placement"]["sections"]
    cff_source_bytes = sum(int(item["size"]) for item in cff_sections)
    cff_stock_rodata_bytes = next(
        int(item["size"]) for item in cff_sections
        if item["name"] == ".cff_stock_rodata"
    )
    cff_stock_text_bytes = next(
        int(item["size"]) for item in cff_sections
        if item["name"] == ".cff_stock_text"
    )
    cff_stock_exidx_bytes = next(
        int(item["size"]) for item in cff_sections
        if item["name"] == ".cff_stock_exidx"
    )
    cff_erased_gap_bytes = int(cff_report["placement"].get(
        "erased_gap_size", 0
    ))
    cff_pointer_bytes = len(bytes.fromhex(
        cff_report["module_class_patch"]["replacement_hex"]
    ))
    lc3_source_bytes = (
        int(lc3_service_report["target_runtime"]["total_text_bytes"])
        + sum(int(row["size"]) for row in
              lc3_service_report["lc3_finalization"]["artifacts"].values())
    )
    lc3_veneer_bytes = sum(len(bytes.fromhex(row["replacement_hex"]))
                           for row in lc3_service_report[
                               "service_audio_entry_guards"])
    lc3_layout_padding_bytes = sum(
        int(row["padding_before"])
        for row in lc3_service_report["lc3_finalization"]["layout"]
    )
    lc3_suffix_padding_bytes = int(
        lc3_service_report["suffix"]["internal_padding_bytes"]
    )
    lc3_component_growth_bytes = (
        int(lc3_service_report["component"]["size"]) - len(pt_component)
    )
    lc3_source_net_growth_bytes = (
        sum(int(row["size"]) for row in
            lc3_service_report["lc3_finalization"]["artifacts"].values())
        + lc3_layout_padding_bytes
        - lc3_suffix_padding_bytes
        - int(lc3_service_report["suffix"]["payload_bytes"])
    )
    lc3_generated_extension_bytes = (
        lc3_component_growth_bytes - lc3_source_net_growth_bytes
    )
    if lc3_generated_extension_bytes < 0:
        raise BuildError("LC3 service component growth accounting changed")
    cff_host_source_bytes = sum(
        int(row["size"]) for row in cff_sections
        if row["name"].startswith(".cff_host_")
    )
    prior_accounting = {
        key: int(component_report.get(key, 0))
        for key in (
            "size",
            "source_owned_bytes",
            "generated_patch_site_bytes",
            "generated_wrapper_bytes",
            "opaque_base_bytes",
        )
    }
    component_report.update(
        {
            "size": len(final_component),
            "sha256": sha256(final_component),
            "opaque_base_bytes": int(component_report["opaque_base_bytes"])
            - patch_bytes - pt_capacity - pt_patch_bytes
            - cff_stock_rodata_bytes - cff_stock_text_bytes
            - cff_stock_exidx_bytes
            - cff_pointer_bytes - lc3_veneer_bytes,
            "source_owned_bytes": int(component_report["source_owned_bytes"])
            + admitted_source_bytes + pt_payload_size + cff_source_bytes
            + lc3_source_bytes,
            "generated_patch_site_bytes": int(
                component_report["generated_patch_site_bytes"]
            )
            + generated_delta + pt_padding_size + pt_patch_bytes
            + cff_erased_gap_bytes + cff_pointer_bytes + lc3_veneer_bytes
            + lc3_layout_padding_bytes - lc3_suffix_padding_bytes
            - int(lc3_service_report["target_runtime"]["total_text_bytes"])
            - int(lc3_service_report["suffix"]["payload_bytes"])
            - cff_host_source_bytes + lc3_generated_extension_bytes,
            "replaced_stock_data_bytes": int(
                component_report.get("replaced_stock_data_bytes", 0)
            ) + cff_stock_rodata_bytes,
            "replaced_stock_function_bytes": int(
                component_report.get("replaced_stock_function_bytes", 0)
            ) + cff_stock_text_bytes,
            "generated_erased_padding_bytes": int(
                component_report.get("generated_erased_padding_bytes", 0)
            ) + cff_erased_gap_bytes + lc3_generated_extension_bytes,
        }
    )
    if (int(component_report["source_owned_bytes"]) +
            int(component_report["generated_patch_site_bytes"]) +
            int(component_report.get("generated_wrapper_bytes", 0)) +
            int(component_report["opaque_base_bytes"]) !=
            int(component_report["size"])):
        accounted = (
            int(component_report["source_owned_bytes"])
            + int(component_report["generated_patch_site_bytes"])
            + int(component_report.get("generated_wrapper_bytes", 0))
            + int(component_report["opaque_base_bytes"])
        )
        raise BuildError(
            "canonical component byte accounting does not conserve: "
            f"accounted={accounted}, size={component_report['size']}, "
            f"delta={accounted - int(component_report['size'])}, "
            f"prior={prior_accounting}, admitted={admitted_source_bytes}, "
            f"generated_delta={generated_delta}, patch={patch_bytes}, "
            f"pt_capacity={pt_capacity}, pt_payload={pt_payload_size}, "
            f"pt_padding={pt_padding_size}, cff_source={cff_source_bytes}, "
            f"cff_host={cff_host_source_bytes}, "
            f"cff_stock={cff_stock_rodata_bytes + cff_stock_text_bytes + cff_stock_exidx_bytes}, "
            f"cff_pointer={cff_pointer_bytes}, lc3_source={lc3_source_bytes}, "
            f"lc3_veneer={lc3_veneer_bytes}, "
            f"lc3_layout_padding={lc3_layout_padding_bytes}, "
            f"lc3_suffix_padding={lc3_suffix_padding_bytes}, "
            f"lc3_generated_extension={lc3_generated_extension_bytes}, "
            f"lc3_text={lc3_service_report['target_runtime']['total_text_bytes']}, "
            f"lc3_suffix_payload={lc3_service_report['suffix']['payload_bytes']}"
        )
    stage_report["sources"].extend(provider_report["sources"])
    stage_report["sources"].extend(
        {
            **item,
            "role": "production mixed-license PT protocol provider input",
        }
        for item in pt_report["source"]["files"]
    )
    stage_report["sources"].extend([
        {
            "path": "third_party/freetype/src/cff/cff.c",
            "size": (OPENCFW_ROOT / "third_party/freetype/src/cff/cff.c").stat().st_size,
            "sha256": sha256((OPENCFW_ROOT / "third_party/freetype/src/cff/cff.c").read_bytes()),
            "license": "FTL",
            "role": "production FreeType 2.9.1 CFF translation unit",
        },
        {
            "path": "components/shared/freetype_cff/runtime_freetype_cff.c",
            "size": (CFF_SHARED_ROOT / "runtime_freetype_cff.c").stat().st_size,
            "sha256": sha256((CFF_SHARED_ROOT / "runtime_freetype_cff.c").read_bytes()),
            "license": "MIT",
            "role": "production CFF policy adapter",
        },
        {
            "path": "components/shared/freetype_cff/runtime_freetype_cff_import_providers.c",
            "size": (CFF_SHARED_ROOT / "runtime_freetype_cff_import_providers.c").stat().st_size,
            "sha256": sha256((CFF_SHARED_ROOT / "runtime_freetype_cff_import_providers.c").read_bytes()),
            "license": "MIT",
            "role": "production CFF source-owned import providers",
        },
    ])
    stage_report["canonical_stages"] = {
        "core": {
            "overlay_size": stage_overlay_size,
            "overlay_sha256": sha256(stage_overlay),
            **stage_component_pin,
        },
        "liblc3_ltpf": {
            "license": "Apache-2.0",
            "payload_size": provider_payload_size,
            "payload_sha256": provider_report["overlay"]["sha256"],
            "component_size": int(provider_report["component"]["size"]),
            "component_sha256": provider_report["component"]["sha256"],
            "placement": copy.deepcopy(provider_report["placement"]),
            "historical_non_corpus_routing": provider_report[
                "historical_non_corpus_routing"
            ],
        },
        "liblc3_service_audio": {
            "license": "Apache-2.0 AND MIT",
            "component": copy.deepcopy(lc3_service_report["component"]),
            "suffix": copy.deepcopy(lc3_service_report["suffix"]),
            "target_runtime": copy.deepcopy(
                lc3_service_report["target_runtime"]
            ),
            "lc3_finalization": copy.deepcopy(
                lc3_service_report["lc3_finalization"]
            ),
            "service_audio_entry_guards": copy.deepcopy(
                lc3_service_report["service_audio_entry_guards"]
            ),
            "routing": copy.deepcopy(lc3_service_report["routing"]),
            "hardware": copy.deepcopy(lc3_service_report["hardware"]),
        },
        "pt_protocol": {
            "license": PT_AGGREGATE_LICENSE,
            "sources": copy.deepcopy(pt_report["source"]["files"]),
            "payload_size": pt_payload_size,
            "payload_sha256": pt_report["placement"]["payload_sha256"],
            "interval_sha256": pt_report["placement"]["interval_sha256"],
            "placement": copy.deepcopy(pt_report["placement"]),
            "source_provider_routes": len(pt_report["source_provider_routes"]),
            "patch_sites": len(pt_report["patch_sites"]),
            "writable_bytes": int(pt_report["placement"]["writable_bytes"]),
            "hardware": pt_report["hardware"],
        },
        "freetype_cff": {
            "license": "FTL AND MIT",
            "component": copy.deepcopy(cff_report["component"]),
            "placement": copy.deepcopy(cff_report["placement"]),
            "module_class_patch": copy.deepcopy(
                cff_report["module_class_patch"]
            ),
            "scatter_manifest": copy.deepcopy(
                cff_report["scatter_manifest"]
            ),
            "receipt_sha256": cff_report["receipt_sha256"],
            "hardware": {
                "validation": "blocked by unavailable physical evidence",
                "qualification_complete": False,
            },
        },
        "final": copy.deepcopy(observed),
    }
    overlay_path = output_dir / config.get("overlay_artifact", "apollo_core_overlay.bin")
    component_path = output_dir / "ota_s200_firmware_ota.bin"
    try:
        overlay_report["artifact"] = str(overlay_path.relative_to(root))
        component_report["artifact"] = str(component_path.relative_to(root))
    except ValueError:
        overlay_report["artifact"] = str(overlay_path)
        component_report["artifact"] = str(component_path)
    additional_artifacts: dict[Path, bytes] = {}
    if record_canonical:
        intermediate_payloads = {
            "core_stage_overlay": stage_overlay,
            "core_stage_component": stage_component,
            "liblc3_payload": liblc3_payload,
            "liblc3_component": liblc3_component,
            "pt_component": pt_component,
            "liblc3_service_component": pre_cff_component,
        }
        intermediate_records = {}
        for key, name in _CANONICAL_INTERMEDIATE_NAMES.items():
            payload = intermediate_payloads[key]
            path = output_dir / name
            additional_artifacts[path] = payload
            intermediate_records[key] = {
                "artifact": name,
                "size": len(payload),
                "sha256": sha256(payload),
            }
        pt_observation = copy.deepcopy(
            stage_report["canonical_stages"]["pt_protocol"]
        )
        pt_observation.update({
            "ingress_sites": copy.deepcopy(pt_report["ingress_sites"]),
            "source_uart_route_receipt": copy.deepcopy(
                pt_report["source_uart_route_receipt"]
            ),
        })
        stage_report["canonical_observation"] = {
            "schema_version": 4,
            "complete": True,
            "profile": profile,
            "source_inputs": _canonical_input_report(input_snapshot),
            "image_mapping": {
                "base_size": int(config["base"]["size"]),
                "run_base": int(config["run_base"]),
                "preamble_bytes": int(config["preamble_bytes"]),
            },
            "toolchain": copy.deepcopy(stage_report["toolchain"]),
            "toolchain_identity": copy.deepcopy(toolchain_identity),
            "core_stage": stage_pin_observation,
            "liblc3_ltpf": copy.deepcopy(
                stage_report["canonical_stages"]["liblc3_ltpf"]
            ),
            "liblc3_service_audio": copy.deepcopy(
                stage_report["canonical_stages"]["liblc3_service_audio"]
            ),
            "pt_protocol": pt_observation,
            "freetype_cff": copy.deepcopy(
                stage_report["canonical_stages"]["freetype_cff"]
            ),
            "final": copy.deepcopy(observed),
            "final_artifacts": {
                "overlay": {
                    "artifact": overlay_path.name,
                    "size": len(final_overlay),
                    "sha256": sha256(final_overlay),
                },
                "component": {
                    "artifact": component_path.name,
                    "size": len(final_component),
                    "sha256": sha256(final_component),
                },
            },
            "intermediate_artifacts": intermediate_records,
        }
        cff_artifact_records = {}
        for section_name, payload in cff_section_artifacts.items():
            name = f"freetype-cff-{section_name.removeprefix('.').replace('.', '-')}.bin"
            path = output_dir / name
            additional_artifacts[path] = payload
            cff_artifact_records[section_name] = {
                "artifact": name,
                "size": len(payload),
                "sha256": sha256(payload),
            }
        stage_report["canonical_observation"]["freetype_cff"][
            "section_artifacts"
        ] = cff_artifact_records
        pt_builder._recheck_toolchain_identity(toolchain_identity)
    _publish_canonical_outputs(
        root=root,
        config_path=config_path,
        config=config,
        input_snapshot=input_snapshot,
        overlay_path=overlay_path,
        final_overlay=final_overlay,
        component_path=component_path,
        final_component=final_component,
        report_path=output_dir / "build-report.json",
        report=stage_report,
        additional_artifacts=additional_artifacts,
        publication_boundary=root if record_canonical else None,
        publication_lock_anchor=(
            COMPONENT_ROOT / "build" if record_canonical else None
        ),
    )
    return stage_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=COMPONENT_ROOT / "overlay.json")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=COMPONENT_ROOT / "build",
        help=(
            "artifact directory; --record-canonical requires a non-symlink "
            "path below the G2 root"
        ),
    )
    parser.add_argument("--clang", default=os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"))
    parser.add_argument(
        "--toolchain-profile", default=os.environ.get("OPENCFW_TOOLCHAIN_PROFILE")
    )
    parser.add_argument("--record-profile", action="store_true")
    parser.add_argument(
        "--record-canonical",
        action="store_true",
        help=(
            "write unpinned dual-stage artifacts and an authenticated "
            "observation receipt for reviewed admission"
        ),
    )
    args = parser.parse_args(argv)
    output_dir = (
        (
            args.output_dir
            if args.output_dir.is_absolute()
            else Path.cwd() / args.output_dir
        )
        if args.record_canonical
        else args.output_dir.resolve()
    )
    report = build(
        root=OPENCFW_ROOT,
        config_path=args.config.resolve(),
        output_dir=output_dir,
        clang=args.clang,
        toolchain_profile=args.toolchain_profile,
        record_profile=args.record_profile,
        record_canonical=args.record_canonical,
    )
    print(
        f"Built {report['name']} canonical source image: "
        f"{report['overlay']['size']} overlay bytes "
        f"[profile {report['toolchain']['profile']}]"
    )
    print(f"  overlay sha256: {report['overlay']['sha256']}")
    print(
        f"  component: {report['component']['size']} bytes, "
        f"sha256 {report['component']['sha256']}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (BuildError, OSError, KeyError, json.JSONDecodeError) as error:
        print(f"openCFW canonical component build: error: {error}", file=sys.stderr)
        raise SystemExit(1)
