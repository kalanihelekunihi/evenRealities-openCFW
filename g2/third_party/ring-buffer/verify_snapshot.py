#!/usr/bin/env python3
"""Offline verification for the selected AndersKaloer/Ring-Buffer snapshot."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROVENANCE = HERE / "PROVENANCE.json"
EXPECTED = {
    "ringbuffer.c": (2202, "c930c1bb55d7efe1116566bacfb00b55ddf031e7df22b22e7138849068819c7f", "39fbea599e9e2c62561f1cd2e80bb08717e9e656"),
    "ringbuffer.h": (4446, "065589a731ffa8367ace4a17885968a53f35e265c7d0d45cdddbe3fa09cfa9e9", "36da6eb18805853f79f5b558714204517fd969a0"),
    "LICENSE": (1080, "d96c4b746ca4a4b8a901e8e0b4ff2ae87026055d2799dcfc58632cd02f422825", "4e5491e49deef7fce4c58480177f501d8cc8dea9"),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data, usedforsecurity=False).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"Ring-Buffer snapshot verification failed: {message}")


def main() -> int:
    value = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    require(value["schema_version"] == 1, "schema changed")
    require(value["component"] == "AndersKaloer/Ring-Buffer", "component changed")
    require(value["license"] == "MIT", "license changed")
    upstream = value["upstream"]
    require(upstream["repository"] == "https://github.com/AndersKaloer/Ring-Buffer.git", "repository changed")
    require(upstream["selected_commit"] == "190e30bebcec22d7311fd941179d70b4f439c441", "selected commit changed")
    require(upstream["selected_tree"] == "017721c429f238ebd40216c9d832866c5323dfaa", "selected tree changed")
    selection = value["selection"]
    require(selection["compatible_floor_commit"] == "cda00e1efb815bad5100757f0d10d117f633ced6", "floor changed")
    require(selection["compatible_ceiling_commit"] == upstream["selected_commit"], "ceiling changed")
    require(selection["exact_g2_checkout_proven"] is False, "historical checkout overclaimed")
    boundary = value["g2_boundary"]
    require(boundary["production_integration_percent"] == 100, "production admission changed")
    production = boundary["production"]
    require(
        production["source"] == {
            "path": "components/shared/ring_buffer/runtime_ring_buffer.c",
            "size": 5290,
            "sha256": "7357f1229ccb40cab3e23204ff7e98176d1026c5c86fbabb67a0a5067c8074b2",
        },
        "production source pin changed",
    )
    require(production["source_owned_bytes"] == 248, "production source byte count changed")
    require(production["generated_alignment_bytes"] == 4, "production alignment byte count changed")
    require(production["generated_entry_replacement_bytes"] == 252, "entry replacement byte count changed")
    production_source = ROOT / production["source"]["path"]
    production_bytes = production_source.read_bytes()
    require(
        (len(production_bytes), sha256(production_bytes))
        == (production["source"]["size"], production["source"]["sha256"]),
        "production source bytes changed",
    )
    require(
        production["apple_clang"]["package"] == {
            "size": 4432206,
            "sha256": "a5625a4bcc1ff20ff9e339f9bb0a074d999508674c7aeb315101e653c90630c2",
        },
        "production package pin changed",
    )

    records = {record["path"]: record for record in value["files"]}
    require(set(records) == set(EXPECTED), "file inventory changed")
    for path, (size, digest, blob_oid) in EXPECTED.items():
        data = (HERE / path).read_bytes()
        require((len(data), sha256(data)) == (size, digest), f"{path} changed")
        canonical = data
        if path == "ringbuffer.c":
            canonical += b"\n"
        elif path == "LICENSE":
            require(canonical.endswith(b"\n"), "LICENSE normalization changed")
            canonical = canonical[:-1]
        require(git_blob(canonical) == blob_oid, f"{path} upstream Git blob changed")
        record = records[path]
        require(record["git_blob_sha1"] == blob_oid, f"{path} provenance blob changed")
        require(record["local_size"] == size and record["local_sha256"] == digest, f"{path} provenance pin changed")

    print("AndersKaloer/Ring-Buffer snapshot verification passed")
    print("selected commit: 190e30bebcec22d7311fd941179d70b4f439c441")
    print("compatible interval: cda00e1efb815bad5100757f0d10d117f633ced6..190e30bebcec22d7311fd941179d70b4f439c441")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
