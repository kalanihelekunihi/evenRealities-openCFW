#!/usr/bin/env python3
"""Authenticate the unpacked research evidence under ``research/``.

The original evidence remains authenticated by its delivered ``SHA256SUMS``
files. Reviewed post-delivery additions carry their own manifests, while the
small set of intentional license-header mutations is recorded as exact
delivered/current digest pairs instead of rewriting historical manifests.

``research/MANIFEST.sha256`` is the current-tree index. It covers every corpus
and readiness file exactly once. Re-indexing is fail-closed: embedded evidence
is verified first and the index is replaced atomically through a held,
non-symlink directory descriptor.
"""

from __future__ import annotations

import argparse
import errno
import hashlib
import os
from pathlib import Path, PurePosixPath
import re
import secrets
import stat


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"
CORPUS = RESEARCH / "corpus"
READINESS = RESEARCH / "readiness"
MANIFEST = RESEARCH / "MANIFEST.sha256"

MANIFEST_NAMES = ("SHA256SUMS", "SHA256SUMS.lane-bundle")

# Files listed in a delivered manifest that are deliberately not stored here.
# Each entry needs a reason; see research/corpus/PROVENANCE.md. Anything else
# missing is an error.
KNOWN_EXCLUSIONS: dict[str, str] = {
    # Regenerable CPython caches of scripts stored beside them.
    "corpus/em9305/size-delta/__pycache__/analyze_em9305_sdk_discovery.cpython-314.pyc":
        "bytecode cache",
    "corpus/em9305/size-delta/__pycache__/compare_em9305_modified_sdk_functions.cpython-314.pyc":
        "bytecode cache",
    "corpus/em9305/size-delta/__pycache__/compare_em9305_sdk_archive.cpython-314.pyc":
        "bytecode cache",
    # Byte-identical copy of the artifact already unpacked at corpus/wsf/matrix-v2/,
    # carried into the current11 run as an input archive.
    "corpus/wsf/current11/inputs/prior-v2.tar.gz":
        "duplicate of corpus/wsf/matrix-v2/",
}

# These five project-authored clean-room candidates received header-only SPDX
# normalization in commit 799b2864. The delivered manifests remain immutable;
# both sides of each reviewed transition are pinned here.
REVIEWED_MUTATIONS: dict[str, dict[str, str]] = {
    "corpus/iar/math-errno/iar_runtime_math_errno.S": {
        "delivered_sha256":
            "b5288643766f14f62a2452f445f58e0e3ec8e09c229f4f9c572b8dd1c5c0f59c",
        "current_sha256":
            "0e14db2d2748135ad18d285ce06964030d396a5f961d1a40cd7e34a7b4a65762",
        "reason": "project-authored clean-room source SPDX-only GPL-3.0-only to MIT normalization",
    },
    "corpus/wsf/current11/inputs/runtime_cordio_wsf_timer_candidate.c": {
        "delivered_sha256":
            "4076f5927ca748ca1215bbd3d409d2799b34e16d820abd874a9c30f95747d791",
        "current_sha256":
            "981db612abbafbd2d28a76f20e6c79fb48a8ac9fc371c012d79f015d30345816",
        "reason": "project-authored clean-room source SPDX-only GPL-3.0-only to MIT normalization",
    },
    "corpus/wsf/current11/inputs/runtime_cordio_wsf_timer_candidate.h": {
        "delivered_sha256":
            "ec4b58fca5019c11aea47a56b5c0ad02313112d9289862cc2bf0af145796b2f3",
        "current_sha256":
            "786191f17888b7283c8fb811a554e6c4c39536e3b3aed0fe1fb25584a3de0ddd",
        "reason": "project-authored clean-room source SPDX-only GPL-3.0-only to MIT normalization",
    },
    "corpus/wsf/current11-v2/runtime_cordio_wsf_timer_candidate.c": {
        "delivered_sha256":
            "def199a7179981092894a10627a243c121c7cf221fd35b6ecd9423e1cf600223",
        "current_sha256":
            "d6d03d75fdf7099956d99303a8e03e293bb5a273aae639e31d3e945b72228849",
        "reason": "project-authored clean-room source SPDX-only GPL-3.0-only to MIT normalization",
    },
    "corpus/wsf/current11-v2/runtime_cordio_wsf_timer_candidate.h": {
        "delivered_sha256":
            "ec4b58fca5019c11aea47a56b5c0ad02313112d9289862cc2bf0af145796b2f3",
        "current_sha256":
            "786191f17888b7283c8fb811a554e6c4c39536e3b3aed0fe1fb25584a3de0ddd",
        "reason": "project-authored clean-room source SPDX-only GPL-3.0-only to MIT normalization",
    },
}

# Editor/OS droppings are never corpus content. They are excluded from the
# index rather than tolerated in it, so a stray file cannot masquerade as
# evidence.
IGNORED_NAMES = frozenset({".DS_Store", "Thumbs.db", ".AppleDouble"})
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")


class CorpusError(RuntimeError):
    """Raised when the research corpus no longer matches its digests."""


class _MissingCorpusPath(FileNotFoundError):
    pass


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _identity(value: os.stat_result) -> tuple[int, int]:
    return value.st_dev, value.st_ino


def _stable_identity(value: os.stat_result) -> tuple[int, int, int, int, int]:
    return (
        value.st_dev,
        value.st_ino,
        value.st_size,
        value.st_mtime_ns,
        value.st_ctime_ns,
    )


def _directory_flags() -> int:
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise CorpusError("secure directory descriptors are unavailable")
    return (
        os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW |
        getattr(os, "O_CLOEXEC", 0)
    )


def _file_flags() -> int:
    if not hasattr(os, "O_NOFOLLOW"):
        raise CorpusError("secure no-follow file descriptors are unavailable")
    return os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)


def _relative_name(name: str) -> str:
    if not name or "\x00" in name or "\\" in name:
        raise CorpusError(f"unsafe research path: {name!r}")
    parsed = PurePosixPath(name)
    if (
        parsed.is_absolute()
        or any(part in {"", ".", ".."} for part in parsed.parts)
        or parsed.as_posix() != name
    ):
        raise CorpusError(f"unsafe research path: {name!r}")
    return parsed.as_posix()


class _ResearchSnapshot:
    """Hold the research root while enumerating, reading, or replacing files."""

    def __init__(self) -> None:
        self.descriptor = -1
        self.root_identity: tuple[int, int] | None = None

    def __enter__(self) -> "_ResearchSnapshot":
        try:
            lexical = os.stat(RESEARCH, follow_symlinks=False)
            self.descriptor = os.open(RESEARCH, _directory_flags())
            opened = os.fstat(self.descriptor)
        except OSError as error:
            if self.descriptor >= 0:
                os.close(self.descriptor)
                self.descriptor = -1
            raise CorpusError(f"cannot securely open research root: {RESEARCH}") from error
        if not stat.S_ISDIR(lexical.st_mode) or _identity(lexical) != _identity(opened):
            os.close(self.descriptor)
            self.descriptor = -1
            raise CorpusError("research root identity changed while being opened")
        self.root_identity = _identity(opened)
        return self

    def __exit__(self, _type, _value, _traceback) -> None:
        if self.descriptor >= 0:
            os.close(self.descriptor)
            self.descriptor = -1

    def assert_root_identity(self) -> None:
        if self.descriptor < 0 or self.root_identity is None:
            raise CorpusError("research snapshot is closed")
        try:
            lexical = os.stat(RESEARCH, follow_symlinks=False)
            opened = os.fstat(self.descriptor)
        except OSError as error:
            raise CorpusError("research root disappeared during operation") from error
        if (
            not stat.S_ISDIR(lexical.st_mode)
            or _identity(lexical) != self.root_identity
            or _identity(opened) != self.root_identity
        ):
            raise CorpusError("research root identity changed during operation")

    def _open_directory(self, name: str) -> int:
        relative = _relative_name(name)
        current = os.dup(self.descriptor)
        try:
            for part in PurePosixPath(relative).parts:
                try:
                    child = os.open(part, _directory_flags(), dir_fd=current)
                    before = os.stat(
                        part, dir_fd=current, follow_symlinks=False
                    )
                    after = os.fstat(child)
                except OSError as error:
                    if "child" in locals():
                        os.close(child)
                        del child
                    raise CorpusError(
                        f"cannot securely open research directory: {relative}"
                    ) from error
                if not stat.S_ISDIR(before.st_mode) or _identity(before) != _identity(after):
                    os.close(child)
                    del child
                    raise CorpusError(
                        f"research directory identity changed: {relative}"
                    )
                os.close(current)
                current = child
                del child
            self.assert_root_identity()
            return current
        except Exception:
            os.close(current)
            raise

    def _open_file(self, name: str) -> int:
        relative = _relative_name(name)
        parts = PurePosixPath(relative).parts
        parent = os.dup(self.descriptor)
        try:
            for part in parts[:-1]:
                try:
                    child = os.open(part, _directory_flags(), dir_fd=parent)
                    before = os.stat(
                        part, dir_fd=parent, follow_symlinks=False
                    )
                    after = os.fstat(child)
                except OSError as error:
                    if "child" in locals():
                        os.close(child)
                        del child
                    if error.errno == errno.ENOENT:
                        raise _MissingCorpusPath(relative) from error
                    raise CorpusError(
                        f"cannot securely traverse research path: {relative}"
                    ) from error
                if not stat.S_ISDIR(before.st_mode) or _identity(before) != _identity(after):
                    os.close(child)
                    del child
                    raise CorpusError(
                        f"research parent identity changed: {relative}"
                    )
                os.close(parent)
                parent = child
                del child
            try:
                descriptor = os.open(parts[-1], _file_flags(), dir_fd=parent)
                lexical = os.stat(
                    parts[-1], dir_fd=parent, follow_symlinks=False
                )
                opened = os.fstat(descriptor)
            except OSError as error:
                if "descriptor" in locals():
                    os.close(descriptor)
                    del descriptor
                if error.errno == errno.ENOENT:
                    raise _MissingCorpusPath(relative) from error
                raise CorpusError(f"cannot securely open research file: {relative}") from error
            if (
                not stat.S_ISREG(lexical.st_mode)
                or lexical.st_nlink != 1
                or _stable_identity(lexical) != _stable_identity(opened)
            ):
                os.close(descriptor)
                raise CorpusError(
                    f"research path is not a stable single-link regular file: {relative}"
                )
            self.assert_root_identity()
            return descriptor
        finally:
            os.close(parent)

    def read(self, name: str) -> bytes:
        relative = _relative_name(name)
        descriptor = self._open_file(relative)
        try:
            before = os.fstat(descriptor)
            chunks = []
            while True:
                chunk = os.read(descriptor, 1 << 20)
                if not chunk:
                    break
                chunks.append(chunk)
            after = os.fstat(descriptor)
            payload = b"".join(chunks)
            if _stable_identity(before) != _stable_identity(after):
                raise CorpusError(f"research file changed while being read: {relative}")
            if len(payload) != before.st_size:
                raise CorpusError(f"incomplete research file read: {relative}")
            self.assert_root_identity()
            return payload
        finally:
            os.close(descriptor)

    def _walk(self, directory: int, prefix: PurePosixPath) -> list[str]:
        try:
            with os.scandir(directory) as iterator:
                entries = sorted(iterator, key=lambda entry: entry.name)
        except OSError as error:
            raise CorpusError(f"cannot enumerate research directory: {prefix}") from error
        output: list[str] = []
        for entry in entries:
            if entry.name in IGNORED_NAMES or entry.name.startswith("._"):
                continue
            relative = (prefix / entry.name).as_posix()
            metadata = entry.stat(follow_symlinks=False)
            if stat.S_ISLNK(metadata.st_mode):
                raise CorpusError(f"research tree contains a symlink: {relative}")
            if stat.S_ISDIR(metadata.st_mode):
                try:
                    child = os.open(entry.name, _directory_flags(), dir_fd=directory)
                except OSError as error:
                    raise CorpusError(
                        f"cannot securely open research directory: {relative}"
                    ) from error
                try:
                    if _identity(metadata) != _identity(os.fstat(child)):
                        raise CorpusError(
                            f"research directory changed while enumerating: {relative}"
                        )
                    output.extend(self._walk(child, PurePosixPath(relative)))
                finally:
                    os.close(child)
                continue
            if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
                raise CorpusError(
                    f"research tree contains a non-regular or hard-linked file: {relative}"
                )
            output.append(relative)
        return output

    def corpus_names(self) -> list[str]:
        names: list[str] = []
        for root in ("readiness", "corpus"):
            directory = self._open_directory(root)
            try:
                names.extend(self._walk(directory, PurePosixPath(root)))
            finally:
                os.close(directory)
        self.assert_root_identity()
        # Match pathlib's historical component-wise ordering so a hardened
        # re-index does not churn otherwise unchanged manifest lines merely
        # because '/' sorts differently from '-' in a flat string.
        return sorted(names, key=lambda name: PurePosixPath(name).parts)

    def atomic_manifest_write(self, payload: bytes) -> None:
        self.assert_root_identity()
        # Refuse to replace anything except the existing single-link regular
        # manifest. Its bytes are not trusted, but its pathname type is.
        try:
            self.read("MANIFEST.sha256")
        except _MissingCorpusPath:
            pass

        temporary = (
            f".MANIFEST.sha256.tmp.{os.getpid()}.{secrets.token_hex(8)}"
        )
        flags = (
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW |
            getattr(os, "O_CLOEXEC", 0)
        )
        descriptor = -1
        try:
            descriptor = os.open(temporary, flags, 0o644, dir_fd=self.descriptor)
            os.fchmod(descriptor, 0o644)
            view = memoryview(payload)
            while view:
                written = os.write(descriptor, view)
                if written <= 0:
                    raise CorpusError("short write while replacing research manifest")
                view = view[written:]
            os.fsync(descriptor)
            os.close(descriptor)
            descriptor = -1
            self.assert_root_identity()
            os.replace(
                temporary,
                "MANIFEST.sha256",
                src_dir_fd=self.descriptor,
                dst_dir_fd=self.descriptor,
            )
            os.fsync(self.descriptor)
            self.assert_root_identity()
        except CorpusError:
            raise
        except OSError as error:
            raise CorpusError("atomic research manifest replacement failed") from error
        finally:
            if descriptor >= 0:
                os.close(descriptor)
            try:
                os.unlink(temporary, dir_fd=self.descriptor)
            except FileNotFoundError:
                pass


def _manifest_entries(payload: bytes, label: str) -> list[tuple[str, str]]:
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise CorpusError(f"non-UTF-8 manifest: {label}") from error
    entries: list[tuple[str, str]] = []
    seen: set[str] = set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) != 2 or not SHA256_RE.fullmatch(parts[0]):
            raise CorpusError(f"malformed line in {label}: {line!r}")
        name = parts[1].strip()
        if name.startswith("*"):
            name = name[1:]
        # Two delivered GNU sha256sum manifests spell every local member with
        # the conventional ``./`` prefix.  Normalize that one historical
        # spelling before applying the strict traversal/alias checks.
        if name.startswith("./"):
            name = name[2:]
        _relative_name(name)
        if name in seen:
            raise CorpusError(f"duplicate manifest entry in {label}: {name}")
        seen.add(name)
        entries.append((parts[0], name))
    return entries


def sha256(path: Path) -> str:
    """Hash a research file through the same no-follow stable-read boundary."""
    try:
        relative = path.relative_to(RESEARCH).as_posix()
    except ValueError as error:
        raise CorpusError(f"path is outside research root: {path}") from error
    with _ResearchSnapshot() as snapshot:
        return _digest(snapshot.read(relative))


def corpus_files() -> list[Path]:
    with _ResearchSnapshot() as snapshot:
        return [RESEARCH / name for name in snapshot.corpus_names()]


def read_manifest(path: Path) -> list[tuple[str, str]]:
    try:
        relative = path.relative_to(RESEARCH).as_posix()
    except ValueError as error:
        raise CorpusError(f"manifest is outside research root: {path}") from error
    with _ResearchSnapshot() as snapshot:
        return _manifest_entries(snapshot.read(relative), relative)


def verify_embedded() -> tuple[int, int]:
    """Verify every delivered manifest without rewriting historical digests."""
    with _ResearchSnapshot() as snapshot:
        names = snapshot.corpus_names()
        manifests = sorted(
            name for name in names
            if PurePosixPath(name).name in MANIFEST_NAMES
        )
        if not manifests:
            raise CorpusError("no embedded SHA256SUMS manifests found")

        checked = 0
        reviewed_seen: set[str] = set()
        for manifest in manifests:
            entries = _manifest_entries(snapshot.read(manifest), manifest)
            parent = PurePosixPath(manifest).parent
            for expected, name in entries:
                target = _relative_name((parent / name).as_posix())
                try:
                    payload = snapshot.read(target)
                except _MissingCorpusPath:
                    if target in KNOWN_EXCLUSIONS:
                        continue
                    raise CorpusError(f"{manifest} references missing file {target}")
                actual = _digest(payload)
                if actual != expected:
                    mutation = REVIEWED_MUTATIONS.get(target)
                    if (
                        mutation is None
                        or expected != mutation["delivered_sha256"]
                        or actual != mutation["current_sha256"]
                        or not mutation["reason"]
                    ):
                        raise CorpusError(
                            f"{target} does not match its delivered digest "
                            f"(expected {expected}, found {actual})"
                        )
                    if target in reviewed_seen:
                        raise CorpusError(f"reviewed mutation referenced twice: {target}")
                    reviewed_seen.add(target)
                checked += 1
        missing_review = sorted(set(REVIEWED_MUTATIONS) - reviewed_seen)
        if missing_review:
            raise CorpusError(
                "reviewed mutation is no longer anchored by a delivered manifest: "
                f"{missing_review[0]}"
            )
        return len(manifests), checked


def verify_index() -> int:
    """Verify research/MANIFEST.sha256 covers the current corpus exactly."""
    with _ResearchSnapshot() as snapshot:
        try:
            rows = _manifest_entries(
                snapshot.read("MANIFEST.sha256"), "MANIFEST.sha256"
            )
        except _MissingCorpusPath as error:
            raise CorpusError("research/MANIFEST.sha256 is missing") from error
        indexed = {name: digest for digest, name in rows}
        present = set(snapshot.corpus_names())

        missing = sorted(present - set(indexed))
        if missing:
            raise CorpusError(
                f"{len(missing)} corpus file(s) absent from MANIFEST.sha256, "
                f"first: {missing[0]}"
            )
        extra = sorted(set(indexed) - present)
        if extra:
            raise CorpusError(
                f"{len(extra)} MANIFEST.sha256 entry(s) with no file, first: {extra[0]}"
            )

        for name, expected in sorted(indexed.items()):
            actual = _digest(snapshot.read(name))
            if actual != expected:
                raise CorpusError(
                    f"{name} does not match MANIFEST.sha256 "
                    f"(expected {expected}, found {actual})"
                )
        return len(indexed)


def write_index() -> int:
    """Atomically replace the current-tree index from one stable snapshot."""
    with _ResearchSnapshot() as snapshot:
        names = snapshot.corpus_names()
        lines = [f"{_digest(snapshot.read(name))}  {name}" for name in names]
        payload = ("\n".join(lines) + "\n").encode("utf-8")
        snapshot.atomic_manifest_write(payload)
        return len(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-manifest",
        action="store_true",
        help="verify embedded evidence, then atomically regenerate MANIFEST.sha256",
    )
    args = parser.parse_args()

    try:
        manifests, checked = verify_embedded()
        if args.write_manifest:
            count = write_index()
            print(f"research/MANIFEST.sha256 rewritten atomically: {count} files")
            print(
                f"embedded evidence verified first: {checked} files against "
                f"{manifests} manifests"
            )
            print(f"reviewed mutations honored: {len(REVIEWED_MUTATIONS)}")
            return 0
        indexed = verify_index()
    except CorpusError as error:
        print(f"research corpus verification failed: {error}")
        return 1
    print(
        f"research corpus verified: {checked} files against {manifests} delivered "
        f"manifests, {indexed} files against MANIFEST.sha256"
    )
    if KNOWN_EXCLUSIONS:
        print(f"known exclusions honored: {len(KNOWN_EXCLUSIONS)}")
    print(f"reviewed mutations honored: {len(REVIEWED_MUTATIONS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
