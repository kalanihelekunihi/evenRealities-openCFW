#!/usr/bin/env python3
"""Fail-closed offline verification for the DaveGamble/cJSON v1.7.12 snapshot."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROVENANCE = HERE / "PROVENANCE.json"
EXPECTED = {
    "cJSON.c": (74184, "f5e77e3f11f9d9dc0a5f25f0517c1d643dddb4f437d9ad7e87f96aaa091cafac", "60b72c01823c671b310008bf10690e5be39b036a"),
    "cJSON.h": (14882, "42775342bd0cf687de0c35d34b4190d3ed5ad990946db6b63152a6247d8b3e1f", "592986b86e9fc0cb03af06f753c39b8c831b91a2"),
    "LICENSE": (1084, "a36dda207c36db5818729c54e7ad4e8b0c6fba847491ba64f372c1a2037b6d5c", "78deb0406d713ab9730e3c2447be1abdbd70b9a2"),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data, usedforsecurity=False).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"cJSON snapshot verification failed: {message}")


def main() -> int:
    value = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    require(value["schema_version"] == 1, "schema changed")
    require(value["component"] == "DaveGamble/cJSON", "component changed")
    require(value["license"] == "MIT", "license changed")
    upstream = value["upstream"]
    require(upstream["repository"] == "https://github.com/DaveGamble/cJSON.git", "repository changed")
    require(upstream["selected_ref"] == "refs/tags/v1.7.12", "selected ref changed")
    require(upstream["tag_type"] == "lightweight", "tag type changed")
    require(
        upstream["selected_commit"] == "3c8935676a97c7c97bf006db8312875b4f292f6c",
        "selected commit changed",
    )
    require(
        upstream["selected_tree"] == "6c770a14e7d9ac1a8fd452a32c51fa4462cf2b45",
        "selected tree changed",
    )
    require(
        upstream["parent_commits"]
        == ["08d2bc766a82cd75764d036f9efef444590d1cf9", "b93fd34044a3ab3d956b1a6c733d609853ada854"],
        "parent commits changed",
    )
    selection = value["selection"]
    require(
        selection["compatible_floor_commit"] == "f110bd2e585394bf47baca34a06df2569a9232b6",
        "compatible floor changed",
    )
    require(
        selection["compatible_ceiling_commit"] == upstream["selected_commit"],
        "compatible ceiling changed",
    )
    require(
        selection["first_excluded_successor_commit"] == "39853e5148dad8dc5d32ea2b00943cf4a0c6f120",
        "first excluded successor changed",
    )
    require(selection["exact_g2_checkout_proven"] is False, "historical checkout overclaimed")
    boundary = value["g2_boundary"]
    require(boundary["production_routed"] is True, "production routing changed")
    require(boundary["linked_functions"] == 21, "linked function count changed")
    require(boundary["stock_body_bytes"] == 2572, "stock body byte count changed")
    require(boundary["stock_span"] == "[0x004D798C,0x004D83D8)", "stock span changed")
    require(
        boundary["analyzer"] == "tools/analyze_g2_json_parser.py"
        and boundary["evidence"] == "docs/research/g2-json-parser-source-candidate-audit.md",
        "boundary evidence changed",
    )
    require(
        "21 strict dual-profile relocated leaves" in boundary["production_decision"],
        "production admission decision missing",
    )
    production = boundary["production_source"]
    production_path = HERE.parents[1] / production["path"]
    production_data = production_path.read_bytes()
    require(
        (len(production_data), sha256(production_data))
        == (production["size"], production["sha256"]),
        "production source changed",
    )

    records = {record["path"]: record for record in value["files"]}
    require(set(records) == set(EXPECTED), "file inventory changed")
    for path, (size, digest, blob_oid) in EXPECTED.items():
        data = (HERE / path).read_bytes()
        require((len(data), sha256(data)) == (size, digest), f"{path} changed")
        require(git_blob(data) == blob_oid, f"{path} upstream Git blob changed")
        record = records[path]
        require(record["git_blob_sha1"] == blob_oid, f"{path} provenance blob changed")
        require(record["size"] == size and record["sha256"] == digest, f"{path} provenance pin changed")

    print("DaveGamble/cJSON snapshot verification passed")
    print("selected tag: v1.7.12 (lightweight)")
    print("selected commit: 3c8935676a97c7c97bf006db8312875b4f292f6c")
    print("compatible interval: v1.7.9 f110bd2e585394bf47baca34a06df2569a9232b6 .. v1.7.12 3c8935676a97c7c97bf006db8312875b4f292f6c")
    print("production: routed (21 strict leaves replace all 2,572 stock body bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
