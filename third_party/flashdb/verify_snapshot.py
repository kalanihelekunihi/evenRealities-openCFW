#!/usr/bin/env python3
"""Fail-closed offline verification for the FlashDB 2.1.1 snapshot."""

from __future__ import annotations

import hashlib
import json
import stat
import struct
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROVENANCE = HERE / "PROVENANCE.json"
EXPECTED_PROVENANCE_SIZE = 10351
EXPECTED_PROVENANCE_SHA256 = "1c619c46d197c1648893ac5ab3187b62ff63323d3ef839cb04c7550e36fbe791"
EXPECTED_RECORDS_SHA256 = "4685bc7cd1b6ac2078d7c9308a84419dfcdab8c018efe7deb30e9fc75a3a5076"
EXPECTED_COMMIT = "714d6159e7e6afb267a3953756abca445c350e61"
EXPECTED_TREE = "3410ae8111e4dbf6ae22d995bfcf37274abf89ea"
EXPECTED_PARENT = "f0af0eeda4d43732c620451ef6b5fff4e31dfc82"
EXPECTED_COMMIT_SIZE = 1122
EXPECTED_COMMIT_SHA256 = "c8aa69a97bdbaebdc283abd3e46fb025270654e4104de7b5caf9981528122ee5"
EXPECTED_TREE_CLOSURE_SIZE = 4972
EXPECTED_TREE_CLOSURE_SHA256 = "358dd855154c58cd8e4f0d90f69f89860e3f800b5289ea2d92be5771dd3fb464"
EXPECTED_TREE_OBJECTS = {
    "3410ae8111e4dbf6ae22d995bfcf37274abf89ea",
    "fcaba9b63c930bd5570a71213b3246f4de075539",
    "7a3c5f5b04b61a6152ff4adb3d96fa8b29582692",
    "c673add62cadc838bcc0810a1886e1f3edc84516",
    "35429be4c0f405f508018b7ceb27340f32b10e40",
    "2257eb9244eb8111612faa77b6310c037c2360b6",
    "fbff2c58f502640d910208a43a35cb5b9b647d09",
}
EXPECTED_CONFIG_SIZE = 918
EXPECTED_CONFIG_SHA256 = "9445f7c81d7a7ee55fd45868bc64733d0bb6e3f295b48ef7cda7c1346cc11cd6"
EXPECTED_IMAGE_SIZE = 3523396
EXPECTED_IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
IMAGE = ROOT / "blobs" / "official" / "g2-2.2.6.10" / "ota_s200_firmware_ota.bin"
LOAD_BASE = 0x00437FE0

EXPECTED_SOURCE_PATHS = [
    "LICENSE",
    "inc/fdb_cfg.h",
    "inc/fdb_def.h",
    "inc/fdb_low_lvl.h",
    "inc/flashdb.h",
    "src/fdb.c",
    "src/fdb_kvdb.c",
    "src/fdb_utils.c",
    "port/fal/LICENSE",
    "port/fal/inc/fal.h",
    "port/fal/inc/fal_def.h",
    "port/fal/src/fal.c",
    "port/fal/src/fal_flash.c",
    "port/fal/src/fal_partition.c",
]
METADATA_PATHS = {
    ".gitattributes",
    "PROVENANCE.json",
    "README.openCFW.md",
    "verify_snapshot.py",
    "g2-config/fdb_cfg.h",
    f"upstream/{EXPECTED_COMMIT}.commit",
    "upstream/trees.json",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_object_sha1(kind: str, data: bytes) -> str:
    header = f"{kind} {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data, usedforsecurity=False).hexdigest()


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(encoded)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FlashDB snapshot verification failed: {message}")


def image_slice(image: bytes, start: int, end: int) -> bytes:
    first = start - LOAD_BASE
    last = end - LOAD_BASE
    require(0 <= first < last <= len(image), "G2 run span is outside the image")
    return image[first:last]


def verify_provenance() -> dict[str, Any]:
    raw = PROVENANCE.read_bytes()
    require(len(raw) == EXPECTED_PROVENANCE_SIZE, "provenance size changed")
    require(sha256(raw) == EXPECTED_PROVENANCE_SHA256, "provenance bytes changed")
    value = json.loads(raw)
    require(
        set(value) == {"schema_version", "component", "license", "upstream", "selection", "g2_boundary", "files"},
        "provenance schema changed",
    )
    require(value["schema_version"] == 1, "schema version changed")
    require(value["component"] == "FlashDB", "component changed")
    require(value["license"] == "Apache-2.0", "license changed")
    upstream = value["upstream"]
    require(upstream["selected_ref"] == "refs/tags/2.1.1", "selected ref changed")
    require(upstream["tag_type"] == "lightweight", "tag type changed")
    require(upstream["selected_commit"] == EXPECTED_COMMIT, "commit changed")
    require(upstream["selected_tree"] == EXPECTED_TREE, "tree changed")
    require(upstream["tree_closure_path"] == "upstream/trees.json", "tree closure path changed")
    require(upstream["tree_closure_size"] == EXPECTED_TREE_CLOSURE_SIZE, "stored tree closure size changed")
    require(upstream["tree_closure_sha256"] == EXPECTED_TREE_CLOSURE_SHA256, "stored tree closure digest changed")
    require(upstream["tree_object_count"] == len(EXPECTED_TREE_OBJECTS), "tree object count changed")
    require(upstream["parent_commit"] == EXPECTED_PARENT, "parent changed")
    require(upstream["commit_signature"]["present"] is True, "commit signature claim changed")
    require(upstream["commit_signature"]["signer_trust_verified"] is False, "unsupported signer trust claim")
    selection = value["selection"]
    require(selection["selected_file_count"] == 14, "selected file count changed")
    require(selection["source_records_sha256"] == EXPECTED_RECORDS_SHA256, "stored records digest changed")
    require(selection["integration_status"] == "authenticated and verified offline; no production registration", "integration boundary changed")
    return value


def verify_commit_object(provenance: dict[str, Any]) -> None:
    record = provenance["upstream"]
    payload = (HERE / record["commit_object_payload_path"]).read_bytes()
    require(len(payload) == EXPECTED_COMMIT_SIZE, "commit payload size changed")
    require(sha256(payload) == EXPECTED_COMMIT_SHA256, "commit payload changed")
    require(git_object_sha1("commit", payload) == EXPECTED_COMMIT, "commit object ID changed")
    require(payload.startswith(f"tree {EXPECTED_TREE}\nparent {EXPECTED_PARENT}\n".encode()), "commit tree/parent chain changed")
    require(b"gpgsig -----BEGIN PGP SIGNATURE-----\n" in payload, "pinned signature missing")


def verify_tree_closure(
    provenance: dict[str, Any], closure: dict[str, Any] | None = None
) -> None:
    """Rebuild the required Git trees and prove every selected path membership."""
    if closure is None:
        record = provenance["upstream"]
        raw = (HERE / record["tree_closure_path"]).read_bytes()
        require(len(raw) == EXPECTED_TREE_CLOSURE_SIZE, "tree closure size changed")
        require(sha256(raw) == EXPECTED_TREE_CLOSURE_SHA256, "tree closure bytes changed")
        closure = json.loads(raw)

    require(set(closure) == {"schema_version", "root_tree", "trees"}, "tree closure schema changed")
    require(closure["schema_version"] == 1, "tree closure schema version changed")
    require(closure["root_tree"] == EXPECTED_TREE, "tree closure root changed")

    trees: dict[str, list[dict[str, str]]] = {}
    for tree in closure["trees"]:
        require(set(tree) == {"oid", "entries"}, "tree record schema changed")
        oid = tree["oid"]
        require(isinstance(oid, str) and len(oid) == 40, "invalid tree object ID")
        require(oid not in trees, f"duplicate tree object {oid}")
        payload = bytearray()
        names: set[str] = set()
        for entry in tree["entries"]:
            require(
                set(entry) == {"mode", "type", "oid", "name"},
                f"tree entry schema changed in {oid}",
            )
            mode = entry["mode"]
            kind = entry["type"]
            child_oid = entry["oid"]
            name = entry["name"]
            require(
                (mode, kind) in {("040000", "tree"), ("100644", "blob")},
                f"unsupported tree entry kind in {oid}",
            )
            require(
                isinstance(child_oid, str)
                and len(child_oid) == 40
                and all(ch in "0123456789abcdef" for ch in child_oid),
                f"invalid child object ID in {oid}",
            )
            require(
                isinstance(name, str)
                and name
                and "/" not in name
                and "\0" not in name,
                f"invalid tree entry name in {oid}",
            )
            require(name not in names, f"duplicate tree entry {name!r} in {oid}")
            names.add(name)
            raw_mode = "40000" if mode == "040000" else mode
            payload.extend(f"{raw_mode} {name}".encode("utf-8"))
            payload.append(0)
            payload.extend(bytes.fromhex(child_oid))
        require(git_object_sha1("tree", bytes(payload)) == oid, f"tree object ID mismatch: {oid}")
        trees[oid] = tree["entries"]

    require(set(trees) == EXPECTED_TREE_OBJECTS, "required tree object set changed")
    for source in provenance["files"]:
        tree_oid = EXPECTED_TREE
        parts = source["upstream_path"].split("/")
        for index, part in enumerate(parts):
            matches = [entry for entry in trees[tree_oid] if entry["name"] == part]
            require(len(matches) == 1, f"path is absent from commit tree: {source['upstream_path']}")
            entry = matches[0]
            if index < len(parts) - 1:
                require(entry["type"] == "tree", f"non-tree path component: {source['upstream_path']}")
                require(entry["oid"] in trees, f"missing path tree object: {source['upstream_path']}")
                tree_oid = entry["oid"]
            else:
                require(entry["type"] == "blob", f"selected path is not a blob: {source['upstream_path']}")
                require(entry["mode"] == source["git_mode"], f"tree mode mismatch: {source['upstream_path']}")
                require(entry["oid"] == source["git_blob_sha1"], f"tree blob mismatch: {source['upstream_path']}")


def verify_source_files(provenance: dict[str, Any]) -> None:
    records = provenance["files"]
    require([item["local_path"] for item in records] == EXPECTED_SOURCE_PATHS, "source order/path set changed")
    require(canonical_sha256(records) == EXPECTED_RECORDS_SHA256, "source records changed")
    for item in records:
        require(set(item) == {"local_path", "upstream_path", "git_mode", "size", "sha256", "git_blob_sha1"}, f"record schema changed for {item['local_path']}")
        require(item["local_path"] == item["upstream_path"], f"path remapping changed for {item['local_path']}")
        require(item["git_mode"] == "100644", f"Git mode changed for {item['local_path']}")
        path = HERE / item["local_path"]
        data = path.read_bytes()
        require(path.is_file(), f"source file missing: {item['local_path']}")
        require(not (path.stat().st_mode & stat.S_IXUSR), f"source became executable: {item['local_path']}")
        require(len(data) == item["size"], f"size changed: {item['local_path']}")
        require(sha256(data) == item["sha256"], f"SHA-256 changed: {item['local_path']}")
        require(git_object_sha1("blob", data) == item["git_blob_sha1"], f"Git blob changed: {item['local_path']}")
    actual = {
        path.relative_to(HERE).as_posix()
        for path in HERE.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }
    require(actual == set(EXPECTED_SOURCE_PATHS) | METADATA_PATHS, "snapshot file set changed")
    require(
        (HERE / ".gitattributes").read_bytes()
        == b"* -text whitespace=-trailing-space\n",
        "snapshot byte/whitespace attributes changed",
    )


def verify_g2_config(provenance: dict[str, Any]) -> None:
    boundary = provenance["g2_boundary"]
    config = (HERE / boundary["recovered_config_header"]).read_bytes()
    require(len(config) == EXPECTED_CONFIG_SIZE, "G2 config size changed")
    require(sha256(config) == EXPECTED_CONFIG_SHA256, "G2 config changed")
    for macro in (
        b"#define FDB_USING_KVDB\n",
        b"#define FDB_USING_FAL_MODE\n",
        b"#define FDB_WRITE_GRAN 1\n",
        b"#define FDB_KV_CACHE_TABLE_SIZE 64\n",
        b"#define FDB_SECTOR_CACHE_TABLE_SIZE 64\n",
    ):
        require(config.count(macro) == 1, f"missing exact config macro {macro!r}")
    cfg = boundary["configuration"]
    require("FDB_USING_TSDB" not in cfg, "unsupported original TSDB macro claim")
    require(cfg["FDB_WRITE_GRAN"] == 1 and cfg["sec_size"] == 4096, "storage config changed")
    require(cfg["FDB_KV_CACHE_TABLE_SIZE"] == 64, "KV cache changed")
    require(cfg["FDB_SECTOR_CACHE_TABLE_SIZE"] == 64, "sector cache changed")
    require(cfg["compiler_short_enums"] is True, "short-enum ABI changed")
    feature = boundary["feature_evidence"]
    require(feature["retained_tsdb_subsystem"] is False, "retained TSDB evidence changed")
    require(
        feature["original_FDB_USING_TSDB_macro_state"] == "not statically proven",
        "unsupported original TSDB macro claim",
    )
    require(feature["minimal_recovered_config_uses_tsdb"] is False, "minimal TSDB selection changed")


def verify_g2_image() -> None:
    image = IMAGE.read_bytes()
    require(len(image) == EXPECTED_IMAGE_SIZE, "official image size changed")
    require(sha256(image) == EXPECTED_IMAGE_SHA256, "official image changed")
    pinned = {
        (0x004D96D8, 0x004D9A84): "9fa5ed5c2df612cdd46667b4f9f4a536f884c44484c65c629ba20becb238190a",
        (0x0051079C, 0x00510992): "34674ed6155198d4ae3db6e87ecf98fa5039a7709970867f74a4c9b5b0424957",
        (0x00544000, 0x0054418E): "1afc3c8acc4d095995d504e4c6b7ae68c0face093fe5c0c23b0a6299a8863c28",
        (0x005453FE, 0x0054552C): "c40571f5f8710c17ca10a713ec7dd6fa7a32da2fac0e2c1571806ff33cd03aad",
        (0x00541232, 0x00541240): "a6ce82abb413ebb05e36f957ec398e3503a2d9fa7eea371b40fe09e2d052d40d",
        (0x00597D34, 0x00597D72): "bd8aef1675f28c9b51abfd974f1bc7d3ed9cf3d64a0dba974f6d2ad9876d6c50",
        (0x00597D72, 0x00597DB0): "2f1b6688f627b068ba062edf1b985c268ba805a803b1b51b003c6a3d693510dd",
        (0x00597DB0, 0x00597DEA): "9f34d5139292961ffe7f117181feddf1fe51c686c43f3feea855ca21abde6047",
    }
    for (start, end), expected in pinned.items():
        require(sha256(image_slice(image, start, end)) == expected, f"G2 body at 0x{start:08x} changed")
    binding_pointers = {
        0x004D9AD4: 0x0078E594,
        0x004D9AB8: 0x0078E58C,
        0x005109D0: 0x0078E60C,
        0x005109D4: 0x0078E614,
    }
    for pool, target in binding_pointers.items():
        require(struct.unpack("<I", image_slice(image, pool, pool + 4))[0] == target, f"binding literal at 0x{pool:08x} changed")
    part0 = struct.unpack("<I24s24sIII", image_slice(image, 0x006D5358, 0x006D5398))
    part1 = struct.unpack("<I24s24sIII", image_slice(image, 0x006D5398, 0x006D53D8))
    require(part0[0] == 0x45503130 and part0[1].startswith(b"kvdb\0") and part0[3:5] == (0x01FC0000, 0x38000), "kvdb partition changed")
    require(part1[0] == 0x45503130 and part1[1].startswith(b"NVdb\0") and part1[3:5] == (0x01FF8000, 0x8000), "NVdb partition changed")
    device = struct.unpack("<24sIIIIIIII", image_slice(image, 0x00722B30, 0x00722B68))
    require(device[0].startswith(b"norflash\0"), "FAL device name changed")
    require(device[1:4] == (0x01FC0000, 0x02000000, 0x1000), "FAL device geometry changed")
    require(device[4:9] == (0x00540ED1, 0x00540ED5, 0x00540F2D, 0x00540F85, 1), "FAL callbacks/write granularity changed")


def verify_upstream_semantics() -> None:
    definition = (HERE / "inc/fdb_def.h").read_text(encoding="utf-8")
    kvdb = (HERE / "src/fdb_kvdb.c").read_text(encoding="utf-8")
    require('#define FDB_SW_VERSION                 "2.1.1"' in definition, "version macro changed")
    require("#if defined(FDB_USING_KVDB)" in kvdb, "KVDB feature guard changed")
    require("#ifdef FDB_KV_AUTO_UPDATE" in kvdb, "auto-update boundary changed")


def main() -> int:
    provenance = verify_provenance()
    verify_commit_object(provenance)
    verify_tree_closure(provenance)
    verify_source_files(provenance)
    verify_g2_config(provenance)
    verify_g2_image()
    verify_upstream_semantics()
    print("FlashDB 2.1.1 snapshot verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
