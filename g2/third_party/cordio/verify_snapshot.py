#!/usr/bin/env python3
"""Fail-closed offline verification for the Packetcraft Cordio source oracle."""

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
EXPECTED_PROVENANCE_SIZE = 20246
EXPECTED_PROVENANCE_SHA256 = "1fffca2937f4ec8f0937f947e0d6e0c14110ea36c561826be21b67d0c7bab07a"
EXPECTED_RECORDS_SHA256 = "2d9ba02bd31e3784789af3ddb3f2bbcaa9e7187f12eb76506b4b2d14a2d55d9a"
EXPECTED_COMMIT = "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6"
EXPECTED_TREE = "0a76c7dde46d3b94bb9185a4a5327d0e3f38ec97"
EXPECTED_PARENT = "eb4282c7abe78dad8fb3984791b9c193fe904052"
EXPECTED_COMMIT_SIZE = 222
EXPECTED_COMMIT_SHA256 = "5dab57d27af0548331378a1b5fcda9bf89724aeecd1b3b92a8df19b516c24c80"
EXPECTED_TREE_CLOSURE_SIZE = 46490
EXPECTED_TREE_CLOSURE_SHA256 = "ff5cfc9516ad240bef69c72df42486dfa82fa54eaa4e5e4dca74cc62917ae5da"
EXPECTED_TREE_OBJECTS = {
    "062769d651f2ff9b740e585d8bcd90dc85dcabef",
    "0a76c7dde46d3b94bb9185a4a5327d0e3f38ec97",
    "150eedefa037805a45d7b2c4d3dc40739d2ff994",
    "17786ee74a20a3b90587dd41b013d8468361a1cd",
    "2023fdd8a1aa3f1a49745a4f61a1af0eff0dee2b",
    "376629d79339e79f8152b290a4c966c0c6b15ce4",
    "52851063425147d1f978963a674e92ac674e8043",
    "67a37e3efcd969375f88f782a5cc40c5eced0b43",
    "93d955317dc6b9afda3c5bdde913e8b1a7698173",
    "9cb897dafee585110af7a8f35483337354260d3d",
    "ae95b912d20ab7793467d3c4c329438d80b6b8b9",
    "aea4d8618dfeb509a3db4d8283721e37f66cee04",
    "b05f619801e343c8e026104f763fc7323d1358a1",
    "bfdb7ba37213ccac8046849c7109442268156e07",
    "c3b7f6ec6fd91d0bccef246629db3a3036e833c0",
    "c5faf0c6732ca1a36ad6db3c1b55c1b16668fc47",
    "c8670c6fdf6008807fe22675330928ceb4d8b51c",
    "ecb4b2024b69e629ae83d0abaecb3043b657e3be",
    "ee1818e85ace6a3d730168d36db01d5341acf09a",
    "fc02ee8c9544694cfa5c1da0b29d279928d674c1",
    "fdc54d7b8ae3aed3fa409a74c4b64334b250b80c",
}
EXPECTED_CONFIG_SIZE = 574
EXPECTED_CONFIG_SHA256 = "a908d4d003392c4fa2cfceef0e5d000bb448a67dbb4cf94fcb431c14366e68a2"
EXPECTED_IMAGE_SIZE = 3_523_396
EXPECTED_IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
IMAGE = ROOT / "blobs" / "official" / "g2-2.2.6.10" / "ota_s200_firmware_ota.bin"
LOAD_BASE = 0x00437FE0

EXPECTED_SOURCE_PATHS = [
    "LICENSE.md",
    "ble-host/include/att_api.h",
    "ble-host/include/att_defs.h",
    "ble-host/include/att_uuid.h",
    "ble-host/include/dm_api.h",
    "ble-host/include/hci_api.h",
    "ble-host/include/l2c_api.h",
    "ble-host/include/l2c_defs.h",
    "ble-host/include/sec_api.h",
    "ble-host/include/smp_api.h",
    "ble-host/include/smp_defs.h",
    "ble-host/sources/stack/att/att_main.h",
    "ble-host/sources/stack/att/atts_csf.c",
    "ble-host/sources/stack/att/atts_main.h",
    "ble-host/sources/stack/cfg/cfg_stack.h",
    "ble-host/sources/stack/dm/dm_conn.h",
    "ble-host/sources/stack/dm/dm_conn_sm.c",
    "ble-host/sources/stack/dm/dm_main.h",
    "ble-host/sources/stack/smp/smp_db.c",
    "ble-host/sources/stack/smp/smp_main.h",
    "ble-profiles/include/app_api.h",
    "ble-profiles/include/app_cfg.h",
    "ble-profiles/include/app_db.h",
    "ble-profiles/sources/af/app_main.h",
    "ble-profiles/sources/af/common/app_db.c",
    "ble-profiles/sources/services/svc_core.h",
    "wsf/include/hci_defs.h",
    "wsf/include/util/bda.h",
    "wsf/include/util/bstream.h",
    "wsf/include/wsf_assert.h",
    "wsf/include/wsf_buf.h",
    "wsf/include/wsf_cs.h",
    "wsf/include/wsf_heap.h",
    "wsf/include/wsf_math.h",
    "wsf/include/wsf_nvm.h",
    "wsf/include/wsf_os.h",
    "wsf/include/wsf_queue.h",
    "wsf/include/wsf_timer.h",
    "wsf/include/wsf_trace.h",
    "wsf/include/wsf_types.h",
    "wsf/sources/targets/baremetal/wsf_buf.c",
]
ROOT_SOURCE_PATHS = [
    "ble-host/sources/stack/att/atts_csf.c",
    "ble-host/sources/stack/dm/dm_conn_sm.c",
    "ble-host/sources/stack/smp/smp_db.c",
    "ble-profiles/sources/af/common/app_db.c",
    "wsf/sources/targets/baremetal/wsf_buf.c",
]
METADATA_PATHS = {
    ".gitattributes",
    "PROVENANCE.json",
    "README.openCFW.md",
    "verify_snapshot.py",
    "g2-config/cordio_recovered_config.h",
    "g2-patches/smp_main-ambiq-aes-queue-cleanup.patch",
    f"upstream/{EXPECTED_COMMIT}.commit",
    "upstream/trees.json",
}
EXPECTED_RELEASES = {
    "r20.05": {
        "commit": "eeb34839755da1c19cc85b8795cc863483c16ef0",
        "tree": "906eb9beaf5e8c3b39ab445f6522f7febeda38b5",
    },
    "r20.05a": {
        "commit": "5e21ee596a80a3dc75ae5ef0938712a6042b2ac3",
        "tree": "5001d075e93220d66ae1340208046c0526b0dc3a",
    },
    "r20.05b": {
        "commit": "eb4282c7abe78dad8fb3984791b9c193fe904052",
        "tree": "c8204fcb39847aa6d3cae3ec49772a70f6097765",
    },
    "r20.05c": {
        "commit": EXPECTED_COMMIT,
        "tree": EXPECTED_TREE,
    },
}
EXPECTED_ORACLE_BLOBS = {
    "ble-host/sources/stack/att/atts_csf.c": "ed4f051194b77827ec991f0d5c0c38969ea7548a",
    "ble-host/sources/stack/dm/dm_conn_sm.c": "58c5c6e1e4df5744c9a41902634cdd23a1aef906",
    "ble-host/sources/stack/smp/smp_db.c": "cbd056aaab32eab0838b2bd9bbaac872012ca06b",
    "ble-profiles/sources/af/common/app_db.c": "789f4c9bac29a5b7eb92c2cb22a221cdd720fe83",
    "wsf/sources/targets/baremetal/wsf_buf.c": "be2ab9cfc03b65390ba25d8d97321fa2d304fc64",
}
EXPECTED_CODE_SPANS = {
    "AttsCsfSetClientChangeAwareState": (
        0x0052D090,
        0x0052D0DC,
        "3d8ce46d70a13f0a62d6693355310733d09cf623fa61018f825956a8feb56070",
    ),
    "AttsCsfWriteFeatures_core": (
        0x0052D628,
        0x0052D674,
        "2e11f9d1dfa9b76ebfd7d92902439df111292ba781151196eca08280184d5bd9",
    ),
    "AttsCsfWriteFeatures_callback_tail": (
        0x0052D79E,
        0x0052D7B6,
        "27aa2fb64353776ed629c906e6c6466d6fdcf0ae9d5f02efa1a5650229afa124",
    ),
    "dmConnSmExecute_event_table_core": (
        0x00534024,
        0x005340A0,
        "decb00baeedd9291a19c1746fb58d8114c979e3f622c78567143f19b515d89b1",
    ),
    "dmConnSmExecute_dispatch_tail": (
        0x005344FA,
        0x00534532,
        "80294c9e8e8462f412813b8fb7711f795d654d9dd6344b2cda45e8c88e145dd1",
    ),
    "WsfBufAlloc": (
        0x00530446,
        0x005304D4,
        "307ff7ddc2830031087eff4c703949a9974deb2e81efe9cd4334b06c35d57d48",
    ),
    "WsfBufFree": (
        0x005304D4,
        0x00530512,
        "6148f827458d86f257dc4ac8eab53f4eeb9372912249d1181fc835861b5a058f",
    ),
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
        raise SystemExit(f"Cordio snapshot verification failed: {message}")


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
    require(value["component"] == "Packetcraft Cordio", "component changed")
    require(value["license"] == "Apache-2.0", "license changed")

    upstream = value["upstream"]
    require(upstream["selected_release"] == "r20.05c", "release choice changed")
    require(upstream["selected_ref"] == EXPECTED_COMMIT, "selected ref changed")
    require(upstream["tag_object"] is None, "unsupported tag-object claim")
    require(upstream["selected_commit"] == EXPECTED_COMMIT, "commit changed")
    require(upstream["selected_tree"] == EXPECTED_TREE, "tree changed")
    require(upstream["parent_commit"] == EXPECTED_PARENT, "parent changed")
    require(upstream["commit_subject"] == "r20.05c", "release subject changed")
    require(upstream["commit_signature"]["present"] is False, "unsupported signature claim")
    require(upstream["tree_closure_path"] == "upstream/trees.json", "tree closure path changed")
    require(upstream["tree_closure_size"] == EXPECTED_TREE_CLOSURE_SIZE, "stored tree closure size changed")
    require(upstream["tree_closure_sha256"] == EXPECTED_TREE_CLOSURE_SHA256, "stored tree closure digest changed")
    require(upstream["tree_object_count"] == len(EXPECTED_TREE_OBJECTS), "tree object count changed")

    selection = value["selection"]
    require(selection["exact_g2_checkout_proven"] is False, "unsupported whole-tree claim")
    require(selection["selected_file_count"] == 41, "selected file count changed")
    require(selection["selected_c_source_count"] == 5, "source count changed")
    require(selection["selected_header_count"] == 35, "header count changed")
    require(selection["selected_license_count"] == 1, "license count changed")
    require(selection["root_source_paths"] == ROOT_SOURCE_PATHS, "root source set changed")
    require(selection["source_records_sha256"] == EXPECTED_RECORDS_SHA256, "stored records digest changed")
    require(selection["integration_status"] == "authenticated and verified offline; no production registration", "integration boundary changed")
    exclusions = "\n".join(selection["excluded_features"])
    for phrase in ("Ambiq FreeRTOS", "Even platform/ble", "controller and radio"):
        require(phrase in exclusions, f"required exclusion missing: {phrase}")

    boundary = value["g2_boundary"]
    require(boundary["whole_stack_identity"] == "unresolved", "whole-stack identity overclaimed")
    require(boundary["bounded_equivalence_interval"]["releases"] == EXPECTED_RELEASES, "release interval changed")
    require("complete G2 Cordio vendor tree" in boundary["bounded_equivalence_interval"]["not_an_upper_bound_for"], "interval qualification changed")
    port = boundary["port_boundary"]
    require(port["g2_source_path"] == "wsf/sources/port/freertos/wsf_buf.c", "G2 WSF port changed")
    require(port["vendored_comparator"] == "wsf/sources/targets/baremetal/wsf_buf.c", "WSF comparator changed")
    require(port["ambiq_hci_port"] == "excluded and unresolved", "Ambiq HCI boundary changed")
    require(port["even_mram_platform_glue"] == "excluded and unresolved", "Even glue boundary changed")
    return value


def verify_commit_object(provenance: dict[str, Any]) -> None:
    record = provenance["upstream"]
    payload = (HERE / record["commit_object_payload_path"]).read_bytes()
    require(len(payload) == EXPECTED_COMMIT_SIZE, "commit payload size changed")
    require(sha256(payload) == EXPECTED_COMMIT_SHA256, "commit payload changed")
    require(git_object_sha1("commit", payload) == EXPECTED_COMMIT, "commit object ID changed")
    require(payload.startswith(f"tree {EXPECTED_TREE}\nparent {EXPECTED_PARENT}\n".encode()), "commit tree/parent chain changed")
    require(payload.endswith(b"\n\nr20.05c\n"), "commit subject changed")
    require(b"\ngpgsig " not in payload, "unexpected signature appeared")


def verify_tree_closure(
    provenance: dict[str, Any], closure: dict[str, Any] | None = None
) -> None:
    """Rebuild required Git trees and prove every selected path membership."""
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
            require(set(entry) == {"mode", "type", "oid", "name"}, f"tree entry schema changed in {oid}")
            mode = entry["mode"]
            kind = entry["type"]
            child_oid = entry["oid"]
            name = entry["name"]
            require((mode, kind) in {("040000", "tree"), ("100644", "blob")}, f"unsupported tree entry kind in {oid}")
            require(isinstance(child_oid, str) and len(child_oid) == 40 and all(ch in "0123456789abcdef" for ch in child_oid), f"invalid child object ID in {oid}")
            require(isinstance(name, str) and name and "/" not in name and "\0" not in name, f"invalid tree entry name in {oid}")
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
    by_path = {item["local_path"]: item for item in records}
    require({path: by_path[path]["git_blob_sha1"] for path in ROOT_SOURCE_PATHS} == EXPECTED_ORACLE_BLOBS, "source-oracle blob set changed")
    for item in records:
        require(set(item) == {"local_path", "upstream_path", "git_mode", "size", "sha256", "git_blob_sha1"}, f"record schema changed for {item['local_path']}")
        require(item["local_path"] == item["upstream_path"], f"path remapping changed for {item['local_path']}")
        require(item["git_mode"] == "100644", f"Git mode changed for {item['local_path']}")
        path = HERE / item["local_path"]
        require(path.is_file(), f"source file missing: {item['local_path']}")
        data = path.read_bytes()
        require(not (path.stat().st_mode & stat.S_IXUSR), f"source became executable: {item['local_path']}")
        require(len(data) == item["size"], f"size changed: {item['local_path']}")
        require(sha256(data) == item["sha256"], f"SHA-256 changed: {item['local_path']}")
        require(git_object_sha1("blob", data) == item["git_blob_sha1"], f"Git blob changed: {item['local_path']}")

    license_record = by_path["LICENSE.md"]
    require(license_record["size"] == 562, "license size changed")
    require(license_record["sha256"] == "682ae5978019e4ee9d439b300efb125525b2e4cc4181ebd1e676dd60dc69d7cd", "license SHA-256 changed")
    require(license_record["git_blob_sha1"] == "5fe50d5491f1166292380f46c8beae44ca83cadb", "license Git blob changed")

    actual = {
        path.relative_to(HERE).as_posix()
        for path in HERE.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }
    require(actual == set(EXPECTED_SOURCE_PATHS) | METADATA_PATHS, "snapshot file set changed")
    require((HERE / ".gitattributes").read_bytes() == b"* -text whitespace=-trailing-space\n", "snapshot byte/whitespace attributes changed")


def verify_configuration_and_firmware(provenance: dict[str, Any]) -> None:
    boundary = provenance["g2_boundary"]
    config = (HERE / boundary["recovered_config_header"]).read_bytes()
    require(len(config) == EXPECTED_CONFIG_SIZE, "G2 config size changed")
    require(sha256(config) == EXPECTED_CONFIG_SHA256, "G2 config changed")
    for macro in (
        b"#define DM_CONN_MAX 3\n",
        b"#define WSF_BUF_FREE_CHECK_ASSERT 1\n",
        b"#define WSF_BUF_STATS 0\n",
        b"#define WSF_BUF_STATS_HIST 0\n",
        b"#define WSF_OS_DIAG 0\n",
    ):
        require(config.count(macro) == 1, f"missing exact config macro {macro!r}")

    cfg = boundary["proven_configuration"]
    require(cfg["DM_CONN_MAX"] == 3 and cfg["DM_CONN_ID_NONE"] == 0, "DM connection config changed")
    require(cfg["ATT_client_record_stride"] == 2, "ATT client record layout changed")
    require(cfg["WSF_BUF_FREE_CHECK_ASSERT"] is True, "WSF free check changed")
    require(cfg["WSF_BUF_STATS"] is False and cfg["WSF_BUF_STATS_HIST"] is False, "WSF stats config changed")
    require(cfg["WSF_OS_DIAG"] is False, "WSF diagnostic config changed")
    require(cfg["WSF_buffer_pool_descriptor_bytes"] == 12, "WSF descriptor layout changed")
    require(cfg["WSF_buffer_free_list_pointer_offset"] == 8, "WSF free-list offset changed")
    require(cfg["WSF_buffer_free_marker"] == "0xFAABD00D", "WSF free marker changed")

    require(b"#define DM_CONN_MAX              3\n" in (HERE / "ble-host/sources/stack/cfg/cfg_stack.h").read_bytes(), "upstream DM_CONN_MAX template changed")
    require(b"#define APP_DB_NUM_RECS 3\n" in (HERE / "ble-profiles/include/app_cfg.h").read_bytes(), "upstream app DB template changed")
    require(b"#define WSF_BUF_FREE_CHECK_ASSERT TRUE\n" in (HERE / "wsf/include/wsf_buf.h").read_bytes(), "upstream WSF free-check template changed")
    require(b"#define WSF_BUF_STATS FALSE\n" in (HERE / "wsf/include/wsf_buf.h").read_bytes(), "upstream WSF stats template changed")
    require(b"#define WSF_OS_DIAG                             FALSE\n" in (HERE / "wsf/include/wsf_os.h").read_bytes(), "upstream WSF OS template changed")

    image = IMAGE.read_bytes()
    require(len(image) == EXPECTED_IMAGE_SIZE, "official G2 image size changed")
    require(sha256(image) == EXPECTED_IMAGE_SHA256, "official G2 image identity changed")
    for label, (start, end, expected) in EXPECTED_CODE_SPANS.items():
        require(sha256(image_slice(image, start, end)) == expected, f"{label} firmware evidence changed")
    marker = struct.unpack("<I", image_slice(image, 0x00530534, 0x00530538))[0]
    require(marker == 0xFAABD00D, "WsfBufFree marker evidence changed")
    require(image_slice(image, 0x0053049C, 0x005304A0) == bytes.fromhex("40f24110"), "WsfBufAlloc source-line evidence changed")


def verify_production_exclusion() -> None:
    reference_tokens = (
        "third_party/cordio",
        "CORDIO_DIR",
        "atts_csf.c",
        "dm_conn_sm.c",
        "smp_db.c",
        "app_db.c",
        "wsf_buf.c",
    )

    # Verification-only registration is permitted.  Keep it exact so any use
    # of the snapshot directory or its source-oracle leaves by a compiler,
    # linker, component, or firmware recipe still fails closed.
    makefile = ROOT / "Makefile"
    if makefile.is_file():
        allowed_makefile_references = {
            "CORDIO_DIR := third_party/cordio",
            "\t$(PYTHON) $(CORDIO_DIR)/verify_snapshot.py",
        }
        for line_number, line in enumerate(
            makefile.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            if any(token in line for token in reference_tokens):
                require(
                    line in allowed_makefile_references,
                    f"snapshot is production-configured by Makefile:{line_number}",
                )

    configured: set[Path] = set()
    manifests = ROOT / "manifests"
    if manifests.is_dir():
        configured.update(path for path in manifests.rglob("*") if path.is_file())

    component_suffixes = {
        ".asm",
        ".c",
        ".h",
        ".json",
        ".ld",
        ".lds",
        ".mk",
        ".py",
        ".s",
    }
    components = ROOT / "components"
    if components.is_dir():
        configured.update(
            path
            for path in components.rglob("*")
            if path.is_file()
            and (path.suffix.lower() in component_suffixes or path.name == "Makefile")
        )

    configured.update(
        {
            ROOT / "tools" / "apollo_overlay.py",
            ROOT / "tools" / "open_cfw.py",
        }
    )
    for path in sorted(configured):
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        require(
            not any(token in content for token in reference_tokens),
            f"snapshot is production-configured by {path.relative_to(ROOT)}",
        )


def main() -> int:
    provenance = verify_provenance()
    verify_commit_object(provenance)
    verify_tree_closure(provenance)
    verify_source_files(provenance)
    verify_configuration_and_firmware(provenance)
    verify_production_exclusion()
    print("Packetcraft Cordio r20.05c source-oracle snapshot verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
