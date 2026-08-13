#!/usr/bin/env python3
"""Authenticate the unpacked research evidence under ``research/``.

The corpus was delivered as compressed bundles carrying embedded ``SHA256SUMS``
manifests. It is now stored unpacked, so authentication has two independent
layers:

* every embedded ``SHA256SUMS`` (and the lane bundle's manifest) must still
  verify in place, which proves the unpacked bytes are the delivered bytes; and
* ``research/MANIFEST.sha256`` must cover every file in the corpus exactly once,
  which proves nothing was added, removed, or edited afterwards.

Both layers fail closed. Run with ``--write-manifest`` only when deliberately
re-indexing after a reviewed change.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

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

# Manifests that authenticate the corpus itself are not indexed by MANIFEST.sha256.
SELF_DESCRIBING = frozenset({"MANIFEST.sha256"})

# Editor/OS droppings are never corpus content. They are excluded from the index
# rather than tolerated in it, so a stray file cannot masquerade as evidence.
IGNORED_NAMES = frozenset({".DS_Store", "Thumbs.db", ".AppleDouble"})


class CorpusError(RuntimeError):
    """Raised when the research corpus no longer matches its delivered digests."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def corpus_files() -> list[Path]:
    files: list[Path] = []
    for base in (READINESS, CORPUS):
        if not base.is_dir():
            raise CorpusError(f"missing research tree: {base.relative_to(ROOT)}")
        files.extend(
            p
            for p in base.rglob("*")
            if p.is_file()
            and p.name not in IGNORED_NAMES
            and not p.name.startswith("._")
        )
    return sorted(files)


def read_manifest(path: Path) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            raise CorpusError(f"malformed line in {path.relative_to(ROOT)}: {line!r}")
        entries.append((parts[0], parts[1].lstrip("*").strip()))
    return entries


def verify_embedded() -> tuple[int, int]:
    """Verify every delivered SHA256SUMS in place."""
    manifests = sorted(
        p
        for name in MANIFEST_NAMES
        for p in RESEARCH.rglob(name)
    )
    if not manifests:
        raise CorpusError("no embedded SHA256SUMS manifests found")

    checked = 0
    for manifest in manifests:
        for expected, name in read_manifest(manifest):
            target = manifest.parent / name
            relative = target.resolve().relative_to(RESEARCH.resolve()).as_posix()
            if not target.is_file():
                if relative in KNOWN_EXCLUSIONS:
                    continue
                raise CorpusError(
                    f"{manifest.relative_to(ROOT)} references missing file {relative}"
                )
            actual = sha256(target)
            if actual != expected:
                raise CorpusError(
                    f"{relative} does not match its delivered digest "
                    f"(expected {expected}, found {actual})"
                )
            checked += 1
    return len(manifests), checked


def verify_index() -> int:
    """Verify research/MANIFEST.sha256 covers the corpus exactly."""
    if not MANIFEST.is_file():
        raise CorpusError("research/MANIFEST.sha256 is missing")

    indexed = {}
    for expected, name in read_manifest(MANIFEST):
        if name in indexed:
            raise CorpusError(f"duplicate MANIFEST.sha256 entry: {name}")
        indexed[name] = expected

    present = {
        p.relative_to(RESEARCH).as_posix()
        for p in corpus_files()
        if p.name not in SELF_DESCRIBING
    }

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
        actual = sha256(RESEARCH / name)
        if actual != expected:
            raise CorpusError(
                f"{name} does not match MANIFEST.sha256 "
                f"(expected {expected}, found {actual})"
            )
    return len(indexed)


def write_index() -> int:
    lines = []
    for path in corpus_files():
        if path.name in SELF_DESCRIBING:
            continue
        lines.append(f"{sha256(path)}  {path.relative_to(RESEARCH).as_posix()}")
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-manifest",
        action="store_true",
        help="regenerate research/MANIFEST.sha256 instead of verifying it",
    )
    args = parser.parse_args()

    if args.write_manifest:
        count = write_index()
        print(f"research/MANIFEST.sha256 rewritten: {count} files")
        return 0

    try:
        manifests, checked = verify_embedded()
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
