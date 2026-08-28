#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Verify the ring-gesture GPL provenance using checked-in evidence only.

The verifier reconstructs the selected Git commit and its root/``patches``
tree chain with ``hashlib``. It deliberately does not invoke Git, access the
network, build firmware, or communicate with hardware.
"""

from __future__ import annotations

import difflib
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent

EXPECTED_REPOSITORY = "https://github.com/jimrandomh/g2flash"
EXPECTED_COMMIT = "6d5c58598e047ca5980065a9ee7570ce2d172ca7"
EXPECTED_ROOT_TREE = "5509f7a353824a92ea5f4cf33ed1646d543404b8"
EXPECTED_PATCHES_TREE = "a6dd12ff9d04000e752a0ef6d0624565c1feb4f8"
EXPECTED_UPSTREAM_PATH = "patches/gesture_fwd.c"
EXPECTED_UPSTREAM_BLOB = "4997b81d4afa1ede5bd15c79957509f65ec75828"
EXPECTED_LICENSE_BLOB = "e72bfddabc15be5718a7cc061ac10e47741d8219"
EXPECTED_UPSTREAM_CLAIM = {
    "repository": EXPECTED_REPOSITORY,
    "local_clone_remote_observed": "ssh://git@ssh.github.com:443/jimrandomh/g2flash.git",
    "selected_commit": EXPECTED_COMMIT,
    "selected_path": EXPECTED_UPSTREAM_PATH,
    "evidence_capture_date": "2026-08-28",
    "evidence_origin": "pre-existing local clone; no network access used",
    "commit_signature_present": False,
    "repository_account_control_authenticated": False,
    "qualification": (
        "The retained Git objects prove commit-to-tree-to-path-to-blob identity "
        "offline. The unsigned commit and local evidence do not independently "
        "authenticate GitHub account control."
    ),
}

EXPECTED_FILES: dict[str, dict[str, Any]] = {
    "upstream_source": {
        "path": "upstream/gesture_fwd.c",
        "upstream_path": EXPECTED_UPSTREAM_PATH,
        "size": 4029,
        "sha256": "cae873922fc1dd64bb59dc80e41fe6dd3b44dea2d082648948dca2233bacfc69",
        "git_blob_sha1": EXPECTED_UPSTREAM_BLOB,
    },
    "checked_in_source": {
        "path": "ring_gesture.c",
        "size": 2264,
        "sha256": "e7824afc0f4d3f567b6b6247df3c0198e2af18275644313da9b199fd3b33605f",
        "git_blob_sha1": "b07ee5a4eab39bce6e9d4fc353099779093219b7",
        "byte_identical_to_upstream": False,
    },
    "derivation_diff": {
        "path": "DERIVATION.patch",
        "size": 6436,
        "sha256": "423fce1e286dad2601158ce3d065d43e8f3a0d1de380e634170e2ffdecc29041",
        "format": "canonical Python difflib unified diff of exact endpoint bytes",
    },
    "component_license": {
        "path": "LICENSE",
        "size": 35149,
        "sha256": "3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986",
        "git_blob_sha1": "f288702d2fa16d3cdf0035b15a9fcbc552cd88e7",
        "upstream_size": 35148,
        "upstream_sha256": "8b1ba204bb69a0ade2bfcf65ef294a920f6bb361b317dba43c7ef29d96332b9b",
        "upstream_git_blob_sha1": EXPECTED_LICENSE_BLOB,
        "normalization": "one terminal LF added to the exact upstream blob",
    },
    "notice": {
        "path": "NOTICE.md",
        "size": 2000,
        "sha256": "5b3b3e05629f583fcac05f04dcc8c722639cb7051329c9e2da553ad2bec5cf31",
    },
}


class ProvenanceError(RuntimeError):
    """Raised when checked-in provenance evidence no longer authenticates."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ProvenanceError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_object_id(kind: str, payload: bytes) -> str:
    require(kind in {"blob", "tree", "commit"}, f"unsupported Git object {kind}")
    header = f"{kind} {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload, usedforsecurity=False).hexdigest()


def encode_tree(entries: list[dict[str, str]]) -> bytes:
    payload = bytearray()
    seen: set[str] = set()
    for entry in entries:
        require(set(entry) == {"mode", "name", "object_id"}, "tree entry schema changed")
        mode = entry["mode"]
        name = entry["name"]
        object_id = entry["object_id"]
        require(mode in {"100644", "100755", "40000"}, f"invalid tree mode for {name}")
        require(name and "/" not in name and "\0" not in name, "invalid tree entry name")
        require(name not in seen, f"duplicate tree entry {name}")
        require(len(object_id) == 40, f"invalid object id for {name}")
        try:
            raw_object_id = bytes.fromhex(object_id)
            raw_name = name.encode("utf-8")
        except (UnicodeEncodeError, ValueError) as error:
            raise ProvenanceError(f"invalid tree entry encoding for {name!r}") from error
        require(len(raw_object_id) == 20, f"invalid object id for {name}")
        payload.extend(mode.encode("ascii") + b" " + raw_name + b"\0" + raw_object_id)
        seen.add(name)
    return bytes(payload)


def tree_entry(tree: dict[str, Any], name: str) -> dict[str, str]:
    matches = [entry for entry in tree["entries"] if entry["name"] == name]
    require(len(matches) == 1, f"tree must contain exactly one {name!r} entry")
    return matches[0]


def reconstruct_commit(commit: dict[str, Any]) -> bytes:
    require(
        set(commit)
        == {"object_id", "payload_size", "tree", "parents", "author", "committer", "message"},
        "commit evidence schema changed",
    )
    lines = [f"tree {commit['tree']}\n"]
    lines.extend(f"parent {parent}\n" for parent in commit["parents"])
    lines.extend(
        (
            f"author {commit['author']}\n",
            f"committer {commit['committer']}\n",
            "\n",
            commit["message"],
        )
    )
    try:
        return "".join(lines).encode("utf-8")
    except (TypeError, UnicodeEncodeError) as error:
        raise ProvenanceError("commit payload is not valid UTF-8 text") from error


def read_pinned_file(component_root: Path, record: dict[str, Any], label: str) -> bytes:
    path = component_root / record["path"]
    require(path.is_file(), f"missing {label}: {record['path']}")
    data = path.read_bytes()
    require(len(data) == record["size"], f"{label} size changed")
    require(sha256(data) == record["sha256"], f"{label} SHA-256 changed")
    return data


def canonical_derivation_diff(upstream: bytes, checked_in: bytes) -> bytes:
    try:
        old_lines = upstream.decode("utf-8").splitlines(keepends=True)
        new_lines = checked_in.decode("utf-8").splitlines(keepends=True)
    except UnicodeDecodeError as error:
        raise ProvenanceError("source endpoints are not UTF-8") from error
    text = "".join(
        difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile="upstream/patches/gesture_fwd.c",
            tofile="components/apollo_main/ring_gesture/ring_gesture.c",
        )
    )
    return text.encode("utf-8")


def verify(component_root: Path = HERE) -> dict[str, Any]:
    provenance_path = component_root / "PROVENANCE.json"
    require(provenance_path.is_file(), "PROVENANCE.json is missing")
    try:
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ProvenanceError("PROVENANCE.json is not valid UTF-8 JSON") from error

    require(provenance["schema_version"] == 1, "provenance schema changed")
    require(provenance["component"] == "openCFW ring gesture overlay", "component changed")
    require(provenance["license"] == "GPL-3.0-only", "license classification changed")

    upstream_claim = provenance["upstream"]
    require(upstream_claim == EXPECTED_UPSTREAM_CLAIM, "upstream evidence claim changed")

    git_objects = provenance["git_objects"]
    require(set(git_objects) == {"commit", "root_tree", "patches_tree"}, "Git proof changed")
    commit = git_objects["commit"]
    root_tree = git_objects["root_tree"]
    patches_tree = git_objects["patches_tree"]

    root_payload = encode_tree(root_tree["entries"])
    patches_payload = encode_tree(patches_tree["entries"])
    require(root_tree["object_id"] == EXPECTED_ROOT_TREE, "root tree claim changed")
    require(patches_tree["object_id"] == EXPECTED_PATCHES_TREE, "patches tree claim changed")
    require(git_object_id("tree", root_payload) == EXPECTED_ROOT_TREE, "root tree proof failed")
    require(
        git_object_id("tree", patches_payload) == EXPECTED_PATCHES_TREE,
        "patches tree proof failed",
    )
    require(
        tree_entry(root_tree, "patches")
        == {"mode": "40000", "name": "patches", "object_id": EXPECTED_PATCHES_TREE},
        "root-to-patches tree link failed",
    )
    require(
        tree_entry(patches_tree, "gesture_fwd.c")
        == {"mode": "100644", "name": "gesture_fwd.c", "object_id": EXPECTED_UPSTREAM_BLOB},
        "patches tree-to-source blob link failed",
    )
    require(
        tree_entry(root_tree, "LICENSE")
        == {"mode": "100644", "name": "LICENSE", "object_id": EXPECTED_LICENSE_BLOB},
        "root tree-to-license blob link failed",
    )

    commit_payload = reconstruct_commit(commit)
    require(commit["object_id"] == EXPECTED_COMMIT, "commit object claim changed")
    require(commit["tree"] == EXPECTED_ROOT_TREE, "commit-to-root tree link failed")
    require(commit["payload_size"] == 281, "commit payload size claim changed")
    require(len(commit_payload) == 281, "reconstructed commit payload size changed")
    require(git_object_id("commit", commit_payload) == EXPECTED_COMMIT, "commit proof failed")

    records = provenance["files"]
    require(set(records) == set(EXPECTED_FILES), "provenance file inventory changed")
    for name, expected in EXPECTED_FILES.items():
        require(records[name] == expected, f"{name} provenance record changed")

    upstream_source = read_pinned_file(component_root, records["upstream_source"], "upstream source")
    checked_in_source = read_pinned_file(
        component_root, records["checked_in_source"], "checked-in source"
    )
    derivation_diff = read_pinned_file(
        component_root, records["derivation_diff"], "derivation diff"
    )
    license_text = read_pinned_file(component_root, records["component_license"], "license")
    notice = read_pinned_file(component_root, records["notice"], "notice")

    require(git_object_id("blob", upstream_source) == EXPECTED_UPSTREAM_BLOB, "upstream blob failed")
    require(
        git_object_id("blob", checked_in_source)
        == records["checked_in_source"]["git_blob_sha1"],
        "checked-in source Git identity changed",
    )
    require(upstream_source != checked_in_source, "derivative incorrectly became byte-identical")
    require(
        canonical_derivation_diff(upstream_source, checked_in_source) == derivation_diff,
        "derivation diff does not match source endpoints",
    )

    require(license_text.endswith(b"\n"), "component license normalization changed")
    upstream_license = license_text[:-1]
    license_record = records["component_license"]
    require(len(upstream_license) == license_record["upstream_size"], "upstream license size changed")
    require(
        sha256(upstream_license) == license_record["upstream_sha256"],
        "upstream license SHA-256 changed",
    )
    require(
        git_object_id("blob", upstream_license) == EXPECTED_LICENSE_BLOB,
        "upstream license Git identity changed",
    )
    require(
        b"GNU GENERAL PUBLIC LICENSE\n                       Version 3, 29 June 2007"
        in license_text,
        "GPLv3 license marker missing",
    )

    source_text = checked_in_source.decode("utf-8")
    require("SPDX-License-Identifier: GPL-3.0-only" in source_text, "source SPDX marker changed")
    require(EXPECTED_UPSTREAM_PATH in source_text, "source upstream path claim missing")
    require(EXPECTED_COMMIT in source_text, "source upstream commit claim missing")

    notice_text = notice.decode("utf-8")
    for token in (
        EXPECTED_REPOSITORY,
        EXPECTED_UPSTREAM_PATH,
        EXPECTED_COMMIT,
        "not a byte-identical copy",
        "no embedded signature",
    ):
        require(token in notice_text, f"notice provenance token missing: {token}")

    overlay = json.loads((component_root / "overlay.json").read_text(encoding="utf-8"))
    expected_integration = provenance["integration_claim"]
    require(
        expected_integration
        == {
            "overlay_metadata_path": "overlay.json",
            "source_path": "components/apollo_main/ring_gesture/ring_gesture.c",
            "license": "GPL-3.0-only",
            "upstream": EXPECTED_REPOSITORY,
            "upstream_commit": EXPECTED_COMMIT,
        },
        "integration claim changed",
    )
    require(
        overlay["source"]
        == {
            "path": expected_integration["source_path"],
            "sha256": records["checked_in_source"]["sha256"],
            "license": expected_integration["license"],
            "upstream": expected_integration["upstream"],
            "upstream_commit": expected_integration["upstream_commit"],
        },
        "overlay source provenance changed",
    )

    boundary = provenance["offline_boundary"]
    require(
        boundary
        == {
            "network_required": False,
            "hardware_required": False,
            "upstream_blob_byte_identity_proven": True,
            "checked_in_source_byte_identity_to_upstream": False,
            "commit_path_blob_binding_proven": True,
            "repository_owner_identity_proven": False,
        },
        "offline proof boundary changed",
    )
    return {
        "commit": EXPECTED_COMMIT,
        "upstream_path": EXPECTED_UPSTREAM_PATH,
        "upstream_blob": EXPECTED_UPSTREAM_BLOB,
        "checked_in_sha256": records["checked_in_source"]["sha256"],
        "license_blob": EXPECTED_LICENSE_BLOB,
        "network_used": False,
        "hardware_used": False,
    }


def main() -> int:
    try:
        report = verify()
    except (KeyError, OSError, TypeError, ProvenanceError) as error:
        print(f"ring gesture provenance verification failed: {error}", file=sys.stderr)
        return 1
    print("ring gesture provenance verified offline")
    print(f"commit/path: {report['commit']}:{report['upstream_path']}")
    print(f"upstream blob: {report['upstream_blob']}")
    print(f"checked-in SHA-256: {report['checked_in_sha256']} (modified derivative)")
    print("network: not used; hardware: not used")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
