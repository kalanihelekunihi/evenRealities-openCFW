#!/usr/bin/env python3
"""Offline verification for the pinned CmBacktrace compatibility snapshot."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import posixpath
from pathlib import Path
import re
import stat
from typing import Any


HERE = Path(__file__).resolve().parent
OPENCFW_ROOT = HERE.parents[1]
PROVENANCE = HERE / "PROVENANCE.json"

EXPECTED_COMMIT = "73714489f9d8af130aacb515586b397b604a5768"
EXPECTED_TREE = "541c20dbeb1165f9b2862e2b84cdc63b3d7c718f"
EXPECTED_PARENTS = [
    "6013293ced1fc2a1fd5544472a53c7bc0bce3ab6",
    "a300d9030b139267291a45b1def460c940890ad0",
]
EXPECTED_PROVENANCE_SIZE = 13064
EXPECTED_PROVENANCE_SHA256 = "2ed8ad33ae5d59f565956cb4aeadfc4897dfb690b96f26ae845132084a76af88"
EXPECTED_RECORDS_SHA256 = "85f08955771a380589634c50fe2771aa38d0f2cc3acc5c3251c0d3b12b2184ae"
EXPECTED_PRODUCTION_RECORDS_SHA256 = "87791a565fa7d0242848ee90b0023bde03d395297c3b1f16f9dee748d5d17596"
EXPECTED_COMMIT_RECORD_SIZE = 1706
EXPECTED_COMMIT_RECORD_SHA256 = "0d623e61ed39db44d15560dd9070dcc962c243a0cd4d8799d71ddd0f0cd12baa"
EXPECTED_COMMIT_PAYLOAD_SIZE = 1158
EXPECTED_COMMIT_PAYLOAD_SHA256 = "54cebc708aa0910efbed7b1792f5265a2f629bb3e5c592262e9f8c63db5520d6"
EXPECTED_TREE_CLOSURE_SIZE = 4705
EXPECTED_TREE_CLOSURE_SHA256 = "63f740fb3f10c83793f10ae74e1666fdad36433003fc50e03e2f309c1b1bc718"
EXPECTED_TREE_OBJECTS = {
    "541c20dbeb1165f9b2862e2b84cdc63b3d7c718f",
    "b15d56e9c1b60fec704e9661299a45a795a36721",
    "8e80649e3024a59ee129f995126a673222b68a2d",
    "b4dc5ea5a8f63eeed2e6c99888d2b9241c96db27",
    "ec67e766c0fadc61f181759ca5201120e8991286",
    "795de9d1d8fcf56fd7d6464b89bedcbb45bf75ca",
}
EXPECTED_TREE_PATHS = {
    "": "541c20dbeb1165f9b2862e2b84cdc63b3d7c718f",
    "cm_backtrace": "b15d56e9c1b60fec704e9661299a45a795a36721",
    "cm_backtrace/Languages": "8e80649e3024a59ee129f995126a673222b68a2d",
    "cm_backtrace/fault_handler": "b4dc5ea5a8f63eeed2e6c99888d2b9241c96db27",
    "cm_backtrace/Languages/en-US": "ec67e766c0fadc61f181759ca5201120e8991286",
    "cm_backtrace/fault_handler/iar": "795de9d1d8fcf56fd7d6464b89bedcbb45bf75ca",
}
EXPECTED_CONFIG_SIZE = 1776
EXPECTED_CONFIG_SHA256 = "9599205cc01589927c5384a316c8fd0919d2fb238f094c9f1b1933c55f85c411"
EXPECTED_LICENSE_SIZE = 1100
EXPECTED_LICENSE_SHA256 = "e8ed0e84184d2130bd1fcf5a52ce8c16b5bf338c272cab6bbd7993a9d723934e"

EXPECTED_PRODUCTION_PATHS = [
    "components/shared/cmbacktrace/runtime_cmbacktrace_get_cur_thread_name.c",
    "components/shared/cmbacktrace/runtime_cmbacktrace_get_cur_thread_name.h",
    "components/apollo_main/core_overlay/runtime_cmbacktrace_pc_task_get_name_current.c",
    "components/apollo_main/core_overlay/runtime_cmbacktrace_pc_task_get_name_current.h",
    "components/apollo_main/core_overlay/LICENSE-CmBacktrace-MIT",
]
EXPECTED_CANDIDATE_PATHS = [
    "components/shared/cmbacktrace/runtime_cmbacktrace_get_cur_thread_name_candidate.c",
    "components/shared/cmbacktrace/runtime_cmbacktrace_get_cur_thread_name_candidate.h",
]
EXPECTED_CANDIDATE_SYMBOLS = [
    "open_cfw_cmbacktrace_get_cur_thread_name_candidate",
    "open_cfw_cmbacktrace_pc_task_get_name_current_candidate",
]
EXPECTED_ALLOWED_PRODUCTION_SOURCE_PATHS = EXPECTED_PRODUCTION_PATHS[:4]
EXPECTED_ALLOWED_PRODUCTION_SYMBOLS = [
    "open_cfw_cmbacktrace_get_cur_thread_name",
    "open_cfw_cmbacktrace_pc_task_get_name_current",
]
EXPECTED_ALLOWED_MAKEFILE_SNAPSHOT_LINES = [
    "CMBACKTRACE_DIR := third_party/cmbacktrace",
    "$(PYTHON) $(CMBACKTRACE_DIR)/verify_snapshot.py",
]

EXPECTED_SOURCE_PATHS = [
    "LICENSE",
    "cm_backtrace/cm_backtrace.c",
    "cm_backtrace/cm_backtrace.h",
    "cm_backtrace/cmb_cfg.h",
    "cm_backtrace/cmb_def.h",
    "cm_backtrace/Languages/en-US/cmb_en_US.h",
    "cm_backtrace/fault_handler/iar/cmb_fault.S",
]
METADATA_PATHS = {
    ".gitattributes",
    "PROVENANCE.json",
    "README.openCFW.md",
    "verify_snapshot.py",
    "g2-config/cmb_user_cfg.h",
    "upstream/commit.json",
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
        raise SystemExit(f"CmBacktrace snapshot verification failed: {message}")


def verify_provenance() -> dict[str, Any]:
    raw = PROVENANCE.read_bytes()
    require(len(raw) == EXPECTED_PROVENANCE_SIZE, "provenance size changed")
    require(sha256(raw) == EXPECTED_PROVENANCE_SHA256, "provenance bytes changed")
    value = json.loads(raw)
    require(
        set(value) == {
            "schema_version", "component", "license", "upstream",
            "selection", "production_integration", "g2_boundary", "files",
        },
        "provenance schema changed",
    )
    require(value["schema_version"] == 2, "schema version changed")
    require(value["component"] == "CmBacktrace", "component changed")
    require(value["license"] == "MIT", "license changed")

    upstream = value["upstream"]
    require(upstream["repository"] == "https://github.com/armink/CmBacktrace.git", "repository changed")
    require(upstream["selected_ref"] == EXPECTED_COMMIT, "selected ref changed")
    require(upstream["selected_commit"] == EXPECTED_COMMIT, "selected commit changed")
    require(upstream["selected_tree"] == EXPECTED_TREE, "selected tree changed")
    require(upstream["parent_commits"] == EXPECTED_PARENTS, "commit parents changed")
    require(upstream["declared_library_version"] == "1.4.2", "declared version changed")
    require(upstream["official_version_tag"] is None, "untagged 1.4.2 state was mislabeled")
    require(upstream["commit_signature"]["present"] is True, "pinned commit signature missing")
    require(upstream["commit_signature"]["signer_trust_verified"] is False, "unsupported signer-trust claim")

    selection = value["selection"]
    require(selection["selected_file_count"] == 7, "selected file count changed")
    require(selection["exact_g2_checkout_proven"] is False, "unsupported exact-G2 checkout claim")
    require(selection["compatible_floor_commit"] == "4abadfa0c4f86f22352aa5ab9ebbb4f687125a1c", "compatible floor changed")
    require(selection["compatible_ceiling_commit"] == EXPECTED_COMMIT, "compatible ceiling changed")
    require(selection["first_incompatible_commit"] == "55e7b6990640c481e83ae8a3c0f3af2092b9f7a6", "incompatible boundary changed")
    require(selection["source_records_sha256"] == EXPECTED_RECORDS_SHA256, "stored source-record digest changed")
    require(
        selection["integration_status"]
        == "snapshot remains unregistered; selected commit authenticates the bounded production get_cur_thread_name source adaptation",
        "bounded production-integration status changed",
    )
    return value


def verify_commit_object(provenance: dict[str, Any]) -> None:
    upstream = provenance["upstream"]
    path = HERE / upstream["commit_object_record_path"]
    raw_record = path.read_bytes()
    require(len(raw_record) == EXPECTED_COMMIT_RECORD_SIZE, "commit record size changed")
    require(sha256(raw_record) == EXPECTED_COMMIT_RECORD_SHA256, "commit record bytes changed")
    record = json.loads(raw_record)
    require(
        set(record) == {"schema_version", "oid", "object_type", "payload_encoding", "payload_base64"},
        "commit record schema changed",
    )
    require(record["schema_version"] == 1, "commit record schema version changed")
    require(record["oid"] == EXPECTED_COMMIT, "commit record object ID changed")
    require(record["object_type"] == "commit", "commit record type changed")
    require(record["payload_encoding"] == "base64", "commit record encoding changed")
    try:
        payload = base64.b64decode(record["payload_base64"], validate=True)
    except (ValueError, TypeError) as exc:
        raise SystemExit(f"CmBacktrace snapshot verification failed: invalid commit payload encoding: {exc}") from exc
    require(len(payload) == EXPECTED_COMMIT_PAYLOAD_SIZE, "commit payload size changed")
    require(sha256(payload) == EXPECTED_COMMIT_PAYLOAD_SHA256, "commit payload bytes changed")
    require(git_object_sha1("commit", payload) == EXPECTED_COMMIT, "commit object ID changed")
    prefix = (
        f"tree {EXPECTED_TREE}\n"
        f"parent {EXPECTED_PARENTS[0]}\n"
        f"parent {EXPECTED_PARENTS[1]}\n"
    ).encode("ascii")
    require(payload.startswith(prefix), "commit tree/parent chain changed")
    require(b"gpgsig -----BEGIN PGP SIGNATURE-----\n" in payload, "commit OpenPGP signature bytes missing")
    require(b"Merge pull request #84 from andeyqi/master\n" in payload, "commit message changed")


def verify_tree_closure(
    provenance: dict[str, Any], closure: dict[str, Any] | None = None
) -> None:
    upstream = provenance["upstream"]
    if closure is None:
        raw = (HERE / upstream["tree_closure_path"]).read_bytes()
        require(len(raw) == EXPECTED_TREE_CLOSURE_SIZE, "tree closure size changed")
        require(sha256(raw) == EXPECTED_TREE_CLOSURE_SHA256, "tree closure bytes changed")
        closure = json.loads(raw)

    require(set(closure) == {"schema_version", "root_tree", "trees"}, "tree closure schema changed")
    require(closure["schema_version"] == 1, "tree closure schema version changed")
    require(closure["root_tree"] == EXPECTED_TREE, "tree closure root changed")

    trees: dict[str, list[dict[str, str]]] = {}
    tree_paths: dict[str, str] = {}
    for tree in closure["trees"]:
        require(set(tree) == {"oid", "path", "entries"}, "tree record schema changed")
        oid = tree["oid"]
        path = tree["path"]
        require(isinstance(oid, str) and len(oid) == 40, "invalid tree object ID")
        require(isinstance(path, str), "invalid tree path")
        require(oid not in trees, f"duplicate tree object {oid}")
        require(path not in tree_paths, f"duplicate tree path {path!r}")
        payload = bytearray()
        names: set[str] = set()
        for entry in tree["entries"]:
            require(set(entry) == {"mode", "type", "oid", "name"}, f"tree entry schema changed in {oid}")
            mode = entry["mode"]
            kind = entry["type"]
            child_oid = entry["oid"]
            name = entry["name"]
            require((mode, kind) in {("040000", "tree"), ("100644", "blob")}, f"unsupported tree entry in {oid}")
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
        tree_paths[path] = oid

    require(set(trees) == EXPECTED_TREE_OBJECTS, "required tree object set changed")
    require(tree_paths == EXPECTED_TREE_PATHS, "required tree path map changed")
    for source in provenance["files"]:
        tree_oid = EXPECTED_TREE
        parts = source["upstream_path"].split("/")
        for index, part in enumerate(parts):
            matches = [entry for entry in trees[tree_oid] if entry["name"] == part]
            require(len(matches) == 1, f"path absent from commit tree: {source['upstream_path']}")
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
        require(set(item) == {"local_path", "upstream_path", "git_mode", "size", "sha256", "git_blob_sha1"}, f"source record schema changed for {item['local_path']}")
        require(item["local_path"] == item["upstream_path"], f"path remapping changed for {item['local_path']}")
        require(item["git_mode"] == "100644", f"Git mode changed for {item['local_path']}")
        path = HERE / item["local_path"]
        require(path.is_file(), f"source file missing: {item['local_path']}")
        data = path.read_bytes()
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
    require((HERE / ".gitattributes").read_bytes() == b"* -text whitespace=-trailing-space\n", "snapshot byte attributes changed")


def verify_license_and_upstream_markers() -> None:
    license_data = (HERE / "LICENSE").read_bytes()
    require(len(license_data) == EXPECTED_LICENSE_SIZE, "MIT license size changed")
    require(sha256(license_data) == EXPECTED_LICENSE_SHA256, "MIT license bytes changed")
    license_text = license_data.decode("ascii")
    for marker in (
        "The MIT License (MIT)",
        "Copyright (c) 2016-2019 Armink",
        "Permission is hereby granted, free of charge",
        "THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND",
    ):
        require(marker in license_text, f"MIT license lost {marker!r}")

    definitions = (HERE / "cm_backtrace" / "cmb_def.h").read_text(encoding="utf-8")
    core = (HERE / "cm_backtrace" / "cm_backtrace.c").read_text(encoding="utf-8")
    english = (HERE / "cm_backtrace" / "Languages" / "en-US" / "cmb_en_US.h").read_text(encoding="utf-8")
    iar_fault = (HERE / "cm_backtrace" / "fault_handler" / "iar" / "cmb_fault.S").read_text(encoding="utf-8")
    require('#define CMB_SW_VERSION                "1.4.2"' in definitions, "declared 1.4.2 version marker changed")
    require("#define CMB_CALL_STACK_MAX_DEPTH       32" in definitions, "upstream call-stack default changed")
    require("#define CMB_DUMP_STACK_DEPTH_SIZE     (16)" in definitions, "upstream dump-stack default changed")
    require("CMB_CPU_ARM_CORTEX_M33" in core and "PRINT_UFSR_STKOF" in english, "M33-class source closure changed")
    require(english.count("[PRINT_") == 39, "English message inventory changed")
    require("IMPORT cm_backtrace_fault" in iar_fault and "EXPORT HardFault_Handler" in iar_fault, "IAR fault entry changed")
    require("saved_regs_addr[7]" not in core, "post-55e7b699 stack-realignment behavior appeared")


def verify_g2_config(provenance: dict[str, Any]) -> None:
    boundary = provenance["g2_boundary"]
    path = HERE / boundary["recovered_config_header"]
    data = path.read_bytes()
    require(len(data) == EXPECTED_CONFIG_SIZE, "G2 config size changed")
    require(sha256(data) == EXPECTED_CONFIG_SHA256, "G2 config bytes changed")
    text = data.decode("ascii")
    for marker in (
        "#define CMB_USING_OS_PLATFORM\n",
        "#define CMB_OS_PLATFORM_TYPE CMB_OS_PLATFORM_FREERTOS\n",
        "#define CMB_USING_DUMP_STACK_INFO\n",
        "#define CMB_NAME_MAX 40\n",
        "#define CMB_CALL_STACK_MAX_DEPTH 32\n",
        "#define CMB_DUMP_STACK_DEPTH_SIZE 16\n",
        "#define CMB_CPU_PLATFORM_TYPE CMB_CPU_ARM_CORTEX_M33\n",
        "#define CMB_PRINT_LANGUAGE CMB_PRINT_LANGUAGE_ENGLISH\n",
        "#error \"Define OPENCFW_CMB_PRINTLN(...) for an explicit CmBacktrace logging port\"\n",
    ):
        require(text.count(marker) == 1, f"G2 config lost exact marker {marker!r}")
    proven = boundary["proven_effective_configuration"]
    require(proven["CMB_OS_PLATFORM_TYPE"] == "CMB_OS_PLATFORM_FREERTOS", "recovered OS changed")
    require(proven["compiler_branch"] == "IAR / __ICCARM__", "recovered compiler branch changed")
    require(proven["effective_language_content"] == "English", "effective language changed")
    require(proven["cpu_behavior"] == "M33-class", "CPU behavior boundary changed")
    require(boundary["explicit_compatibility_choices"] == {
        "CMB_CPU_PLATFORM_TYPE": "CMB_CPU_ARM_CORTEX_M33",
        "CMB_PRINT_LANGUAGE": "CMB_PRINT_LANGUAGE_ENGLISH",
    }, "compatibility-choice boundary changed")
    require(len(boundary["unresolved"]) == 5, "unresolved configuration inventory changed")


def verify_production_integration(provenance: dict[str, Any]) -> None:
    integration = provenance["production_integration"]
    require(
        set(integration) == {
            "scope", "aggregate_registration_scope", "upstream_compatibility_baseline",
            "stock_g2_boundary", "production_files", "candidate_separation",
            "registration_exclusion",
        },
        "production-integration schema changed",
    )
    require(
        integration["scope"]
        == "bounded CmBacktrace FreeRTOS get_cur_thread_name source adaptation",
        "production-integration scope changed",
    )

    baseline = integration["upstream_compatibility_baseline"]
    require(
        set(baseline) == {
            "commit", "source_path", "function", "selected_platform",
            "selected_branch", "qualification",
        },
        "production upstream-baseline schema changed",
    )
    require(baseline["commit"] == EXPECTED_COMMIT, "production baseline commit changed")
    require(baseline["source_path"] == "cm_backtrace/cm_backtrace.c", "production baseline source changed")
    require(baseline["function"] == "get_cur_thread_name", "production baseline function changed")
    require(baseline["selected_platform"] == "CMB_OS_PLATFORM_FREERTOS", "production platform changed")
    require(baseline["selected_branch"] == "return vTaskName();", "production upstream branch changed")
    require(
        "does not define the G2 fixed address" in baseline["qualification"],
        "upstream/local evidence boundary was lost",
    )

    stock = integration["stock_g2_boundary"]
    require(
        stock == {
            "get_cur_thread_name_span": "[0x00593AF6,0x00593AFE)",
            "get_cur_thread_name_size": 8,
            "get_cur_thread_name_hex": "80b5c2f699fa02bd",
            "get_cur_thread_name_sha256": "75f860b4a8f7d60464eeb5216946dbefe0875c65fb0c7a6641abdd9f9daa979b",
            "vtask_name_adapter_span": "[0x0045602E,0x00456036)",
            "vtask_name_adapter_size": 8,
            "vtask_name_adapter_hex": "0b48006834307047",
            "vtask_name_adapter_sha256": "a4150246c7816b7ffab201b6ae3bc6da8c6147e9a5541a921733369dd1e6c09b",
            "current_tcb_word_address": "0x20074A20",
            "task_name_offset": "0x34",
            "null_current_tcb_result": "0x34",
            "classification": "local recovered Even G2 integration evidence; not upstream CmBacktrace source or configuration",
        },
        "recovered stock G2 adapter boundary changed",
    )

    records = integration["production_files"]
    require(
        [record["local_path"] for record in records] == EXPECTED_PRODUCTION_PATHS,
        "bounded production path set/order changed",
    )
    require(
        canonical_sha256(records) == EXPECTED_PRODUCTION_RECORDS_SHA256,
        "bounded production records changed",
    )
    for record in records:
        require(
            set(record) == {"local_path", "classification", "size", "sha256"},
            f"production record schema changed for {record['local_path']}",
        )
        require("_candidate" not in record["local_path"], "candidate entered production records")
        path = OPENCFW_ROOT / record["local_path"]
        require(path.is_file(), f"bounded production file missing: {record['local_path']}")
        data = path.read_bytes()
        require(not (path.stat().st_mode & stat.S_IXUSR), f"production source became executable: {record['local_path']}")
        require(len(data) == record["size"], f"size changed: {record['local_path']}")
        require(sha256(data) == record["sha256"], f"SHA-256 changed: {record['local_path']}")

    production_source = (OPENCFW_ROOT / EXPECTED_PRODUCTION_PATHS[0]).read_text(encoding="utf-8")
    production_header = (OPENCFW_ROOT / EXPECTED_PRODUCTION_PATHS[1]).read_text(encoding="utf-8")
    adapter_source = (OPENCFW_ROOT / EXPECTED_PRODUCTION_PATHS[2]).read_text(encoding="utf-8")
    adapter_header = (OPENCFW_ROOT / EXPECTED_PRODUCTION_PATHS[3]).read_text(encoding="utf-8")
    component_license = (OPENCFW_ROOT / EXPECTED_PRODUCTION_PATHS[4]).read_bytes()
    require("Copyright (c) 2016-2019, Armink" in production_source, "production helper lost MIT attribution")
    require(EXPECTED_COMMIT in production_source, "production helper lost compatibility baseline")
    require("open_cfw_cmbacktrace_pc_task_get_name_current()" in production_source, "production helper seam changed")
    require("open_cfw_cmbacktrace_get_cur_thread_name" in production_header, "production helper interface changed")
    require("OPEN_CFW_CMBACKTRACE_CURRENT_TCB_WORD_ADDRESS 0x20074A20U" in adapter_source, "adapter current-TCB address changed")
    require("OPEN_CFW_CMBACKTRACE_TASK_NAME_OFFSET 0x34U" in adapter_source, "adapter task-name offset changed")
    require("current_tcb + OPEN_CFW_CMBACKTRACE_TASK_NAME_OFFSET" in adapter_source, "adapter null/offset semantics changed")
    require("open_cfw_freertos_pc_task_get_name" not in adapter_source, "adapter gained non-stock pcTaskGetName behavior")
    require("null-TCB result of 0x34" in adapter_header, "adapter interface lost null behavior")
    require(component_license == (HERE / "LICENSE").read_bytes() + b"\n", "component MIT license copy changed")

    separation = integration["candidate_separation"]
    require(
        set(separation) == {"status", "candidate_paths", "candidate_symbols"},
        "candidate-separation schema changed",
    )
    require(separation["candidate_paths"] == EXPECTED_CANDIDATE_PATHS, "candidate path set changed")
    require(separation["candidate_symbols"] == EXPECTED_CANDIDATE_SYMBOLS, "candidate symbol set changed")
    require(
        all((OPENCFW_ROOT / path).is_file() for path in EXPECTED_CANDIDATE_PATHS),
        "production-excluded candidate source/header missing",
    )
    require(
        set(EXPECTED_CANDIDATE_PATHS).isdisjoint(EXPECTED_PRODUCTION_PATHS),
        "candidate and production paths overlap",
    )

    exclusion = integration["registration_exclusion"]
    require(
        set(exclusion) == {
            "scan_scope", "forbidden_snapshot_prefix", "allowed_production_source_paths",
            "allowed_production_symbols", "allowed_makefile_snapshot_lines", "qualification",
            "path_normalization", "generated_directory_exclusions",
        },
        "registration-exclusion schema changed",
    )
    require(
        exclusion["scan_scope"] == [
            "components/**/overlay.json excluding directories named build or build-*",
            "manifests/**/*.json excluding directories named build or build-*",
            "Makefile",
        ],
        "registration scan scope changed",
    )
    require(
        exclusion["path_normalization"]
        == "POSIX lexical normalization is applied to path-like JSON strings and Makefile path tokens before exclusion and allowlist checks.",
        "registration path-normalization policy changed",
    )
    require(
        exclusion["generated_directory_exclusions"] == ["build", "build-*"],
        "generated-directory exclusion policy changed",
    )
    require(exclusion["forbidden_snapshot_prefix"] == "third_party/cmbacktrace", "snapshot exclusion prefix changed")
    require(
        exclusion["allowed_production_source_paths"] == EXPECTED_ALLOWED_PRODUCTION_SOURCE_PATHS,
        "allowed bounded production path set changed",
    )
    require(
        exclusion["allowed_production_symbols"] == EXPECTED_ALLOWED_PRODUCTION_SYMBOLS,
        "allowed bounded production symbol set changed",
    )
    require(
        exclusion["allowed_makefile_snapshot_lines"] == EXPECTED_ALLOWED_MAKEFILE_SNAPSHOT_LINES,
        "allowed Makefile snapshot recipe changed",
    )


def iter_json_strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from iter_json_strings(item)
    elif isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from iter_json_strings(item)


def normalized_path_like(value: str) -> str:
    if "/" not in value or any(character.isspace() for character in value):
        return value
    return posixpath.normpath(value)


def generated_directory(name: str) -> bool:
    return name == "build" or name.startswith("build-")


def source_tree_files(root: Path, filename: str) -> list[Path]:
    matches: list[Path] = []
    if not root.is_dir():
        return matches
    for directory, child_directories, files in os.walk(root):
        child_directories[:] = sorted(
            child for child in child_directories if not generated_directory(child)
        )
        if filename in files:
            matches.append(Path(directory) / filename)
    return sorted(matches)


def verify_registration_exclusion(
    provenance: dict[str, Any], root: Path = OPENCFW_ROOT
) -> None:
    integration = provenance["production_integration"]
    exclusion = integration["registration_exclusion"]
    forbidden_snapshot = exclusion["forbidden_snapshot_prefix"]
    forbidden_candidates = tuple(
        integration["candidate_separation"]["candidate_paths"]
        + integration["candidate_separation"]["candidate_symbols"]
    )
    allowed_paths = set(exclusion["allowed_production_source_paths"])
    allowed_symbols = set(exclusion["allowed_production_symbols"])

    component_root = root / "components"
    manifest_root = root / "manifests"
    overlays = source_tree_files(component_root, "overlay.json")
    manifests = []
    if manifest_root.is_dir():
        for directory, child_directories, files in os.walk(manifest_root):
            child_directories[:] = sorted(
                child for child in child_directories if not generated_directory(child)
            )
            manifests.extend(
                Path(directory) / filename
                for filename in sorted(files)
                if filename.endswith(".json")
            )
    require(bool(overlays), "no source-controlled component overlay configuration found")
    require(bool(manifests), "no source-controlled manifest configuration found")

    for path in overlays + manifests:
        relative = path.relative_to(root).as_posix()
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            require(False, f"cannot parse production configuration {relative}: {exc}")
        for string in iter_json_strings(value):
            normalized = normalized_path_like(string)
            require(
                forbidden_snapshot not in string and forbidden_snapshot not in normalized,
                f"direct CmBacktrace snapshot registration in {relative}: {string}",
            )
            for candidate in forbidden_candidates:
                require(
                    candidate not in string and candidate not in normalized,
                    f"CmBacktrace candidate registration in {relative}: {candidate}",
                )
            if (
                normalized.startswith("components/")
                and "cmbacktrace" in normalized.lower()
                and normalized.endswith((".c", ".h"))
            ):
                require(
                    normalized in allowed_paths,
                    f"unapproved CmBacktrace production source path in {relative}: {normalized}",
                )
            if string.startswith("open_cfw_cmbacktrace_"):
                require(
                    string in allowed_symbols,
                    f"unapproved CmBacktrace production symbol in {relative}: {string}",
                )

    makefile = root / "Makefile"
    require(makefile.is_file(), "source-controlled Makefile missing")
    allowed_makefile_lines = set(exclusion["allowed_makefile_snapshot_lines"])
    for line_number, line in enumerate(makefile.read_text(encoding="utf-8").splitlines(), 1):
        stripped = line.strip()
        for candidate in forbidden_candidates:
            require(
                candidate not in line,
                f"CmBacktrace candidate registration in Makefile:{line_number}: {candidate}",
            )
        if stripped in allowed_makefile_lines:
            continue
        for token in re.findall(r"[A-Za-z0-9_.+-]+(?:/+[A-Za-z0-9_.+-]+)+", line):
            normalized = normalized_path_like(token)
            require(
                forbidden_snapshot not in normalized,
                f"direct CmBacktrace snapshot registration in Makefile:{line_number}: {normalized}",
            )
            if (
                normalized.startswith("components/")
                and "cmbacktrace" in normalized.lower()
                and normalized.endswith((".c", ".h"))
            ):
                require(
                    normalized in allowed_paths,
                    f"unapproved CmBacktrace production source path in Makefile:{line_number}: {normalized}",
                )
        for symbol in re.findall(r"\bopen_cfw_cmbacktrace_[A-Za-z0-9_]+\b", line):
            require(
                symbol in allowed_symbols,
                f"unapproved CmBacktrace production symbol in Makefile:{line_number}: {symbol}",
            )
        if forbidden_snapshot in line or "CMBACKTRACE_DIR" in line:
            require(
                stripped in allowed_makefile_lines,
                f"direct CmBacktrace snapshot registration in Makefile:{line_number}: {stripped}",
            )


def main() -> None:
    provenance = verify_provenance()
    verify_commit_object(provenance)
    verify_tree_closure(provenance)
    verify_source_files(provenance)
    verify_license_and_upstream_markers()
    verify_g2_config(provenance)
    verify_production_integration(provenance)
    verify_registration_exclusion(provenance)
    print("CmBacktrace compatibility snapshot verification passed")


if __name__ == "__main__":
    main()
