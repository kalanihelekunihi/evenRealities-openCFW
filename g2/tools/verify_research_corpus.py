#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Authenticate the retained G2 research corpus under ``research/``.

Two checks, both fail-closed:

1. Every delivery manifest (``SHA256SUMS`` in a corpus subdirectory) must
   verify completely against the files beside it. The top-level
   ``corpus/SHA256SUMS.lane-bundle`` records the original bundle, part of
   which was pruned on 2026-09-29. Its entries are verified when the file is
   present and counted as pruned when it is not.
2. ``research/MANIFEST.sha256`` must list every other file under
   ``research/`` exactly once, with matching digests, and nothing else.

``--write-manifest`` runs check 1 and then regenerates ``MANIFEST.sha256``.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path

G2_ROOT = Path(__file__).resolve().parents[1]
RESEARCH = G2_ROOT / "research"
INDEX_NAME = "MANIFEST.sha256"
PARTIAL_MANIFESTS = {"corpus/SHA256SUMS.lane-bundle"}

# A project-authored file that received a header-only SPDX normalization in
# commit 799b2864. The delivery manifest stays immutable, so both sides of
# the reviewed transition are pinned here.
REVIEWED_MUTATIONS: dict[str, tuple[str, str]] = {
    "corpus/iar/math-errno/iar_runtime_math_errno.S": (
        "b5288643766f14f62a2452f445f58e0e3ec8e09c229f4f9c572b8dd1c5c0f59c",
        "0e14db2d2748135ad18d285ce06964030d396a5f961d1a40cd7e34a7b4a65762",
    ),
}


class CorpusError(Exception):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_sums(path: Path) -> list[tuple[str, str]]:
    entries = []
    for number, line in enumerate(path.read_text(encoding="utf8").splitlines(), 1):
        if not line.strip():
            continue
        digest, sep, name = line.partition("  ")
        if not sep or len(digest) != 64:
            raise CorpusError(f"{path}:{number}: malformed line")
        entries.append((digest, name.lstrip("*")))
    return entries


def tree_files(root: Path) -> list[str]:
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for name in sorted(filenames):
            full = Path(dirpath) / name
            if full.is_symlink():
                raise CorpusError(f"symlink not allowed: {full.relative_to(root)}")
            files.append(full.relative_to(root).as_posix())
    return files


def verify_delivery_manifests(root: Path) -> tuple[int, int]:
    verified = pruned = 0
    for rel in tree_files(root):
        name = rel.rsplit("/", 1)[-1]
        if not (name == "SHA256SUMS" or name.startswith("SHA256SUMS.")):
            continue
        manifest = root / rel
        partial = rel in PARTIAL_MANIFESTS
        for digest, target in parse_sums(manifest):
            path = manifest.parent / target
            if not path.is_file():
                if partial:
                    pruned += 1
                    continue
                raise CorpusError(f"{rel}: missing {target}")
            actual = sha256(path)
            if actual != digest:
                key = path.relative_to(root).as_posix()
                if REVIEWED_MUTATIONS.get(key) != (digest, actual):
                    raise CorpusError(f"{rel}: digest mismatch for {target}")
            verified += 1
    return verified, pruned


def index_entries(root: Path) -> dict[str, str]:
    return {rel: sha256(root / rel) for rel in tree_files(root) if rel != INDEX_NAME}


def verify_index(root: Path) -> int:
    index = root / INDEX_NAME
    if not index.is_file():
        raise CorpusError(f"{INDEX_NAME} is missing")
    listed: dict[str, str] = {}
    for digest, rel in parse_sums(index):
        if rel in listed:
            raise CorpusError(f"{INDEX_NAME}: duplicate entry {rel}")
        listed[rel] = digest
    actual = index_entries(root)
    missing = sorted(set(actual) - set(listed))
    extra = sorted(set(listed) - set(actual))
    if missing:
        raise CorpusError(f"{INDEX_NAME}: unlisted files: {', '.join(missing[:5])}")
    if extra:
        raise CorpusError(f"{INDEX_NAME}: listed files absent: {', '.join(extra[:5])}")
    changed = sorted(rel for rel in actual if actual[rel] != listed[rel])
    if changed:
        raise CorpusError(f"{INDEX_NAME}: digest mismatch: {', '.join(changed[:5])}")
    return len(actual)


def write_index(root: Path) -> int:
    entries = index_entries(root)
    body = "".join(f"{digest}  {rel}\n" for rel, digest in sorted(entries.items()))
    tmp = root / (INDEX_NAME + ".tmp")
    tmp.write_text(body, encoding="utf8")
    tmp.replace(root / INDEX_NAME)
    return len(entries)


def main(argv: list[str] | None = None, root: Path = RESEARCH) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write-manifest", action="store_true", help="regenerate MANIFEST.sha256 after verifying delivery manifests")
    args = parser.parse_args(argv)
    try:
        verified, pruned = verify_delivery_manifests(root)
        if args.write_manifest:
            count = write_index(root)
            print(f"wrote {INDEX_NAME}: {count} files")
        count = verify_index(root)
    except CorpusError as error:
        print(f"research corpus verification failed: {error}", file=sys.stderr)
        return 1
    print(f"research corpus verified: {count} files indexed, {verified} delivery digests checked, {pruned} pruned bundle entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
