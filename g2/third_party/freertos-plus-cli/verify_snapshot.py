#!/usr/bin/env python3
"""Fail-closed offline verification for the FreeRTOS+CLI source snapshot."""

from __future__ import annotations

import base64
import hashlib
import json
import stat
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROVENANCE = HERE / "PROVENANCE.json"
OBJECTS = HERE / "upstream" / "objects.json"
PATCH = HERE / "g2-patches" / "0001-suppress-unknown-command-for-blank-input.patch"
IMAGE = ROOT / "blobs" / "official" / "g2-2.2.6.10" / "ota_s200_firmware_ota.bin"

EXPECTED_PROVENANCE_SIZE = 8336
EXPECTED_PROVENANCE_SHA256 = "4ccf6f4f904cff75a6d166425167aa79678083175247086597b60c9b3645547e"
EXPECTED_OBJECTS_SIZE = 9480
EXPECTED_OBJECTS_SHA256 = "d5dd36c97cb1f2fb0a285e3e3345a1bdf4d71007ce40916ac390724bab015872"
EXPECTED_PATCH_SIZE = 1077
EXPECTED_PATCH_SHA256 = "ada47a9141d44e465be3be4b878e61b1056c65986dd728003c169d9383491d70"
EXPECTED_IMAGE_SIZE = 3523396
EXPECTED_IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
LOAD_BASE = 0x00437FE0

SELECTED_COMMIT = "43defa566cc440251dbd6b48d1fcca27f88cfcdd"
SELECTED_TREE = "1244875832c8ef8a39ee5b97a9dad657f7ea13ec"
SELECTED_PARENT = "4f71a94a7001f9cdf2c7a0a2572d376f1c6d14af"
SELECTED_COMMIT_SIZE = 1919
SELECTED_COMMIT_SHA256 = "4cfa2d11824e0becc99f4ce83f628860a1597dd27d6ffa33356342d2357bed19"
CEILING_COMMIT = "1309654d6f5d1342b4a9d3d7ae0824e8fcaefaf2"
CEILING_TREE = "6d95fe580646a9f12b9cc2f37bd1e9c4d72fbad7"
CEILING_PARENT = "d57e2b746b6ae086719d8e68f12f3665c08a0452"
CEILING_COMMIT_SIZE = 1119
CEILING_COMMIT_SHA256 = "76dee2077a0e872fb3c576420b0cab5c14eda34832a101621767aa345b01c744"
EXPECTED_TREE_OBJECTS = {
    "1244875832c8ef8a39ee5b97a9dad657f7ea13ec",
    "4955f456146d747bacde4b6fa40ade3aee4984e8",
    "b19d9b04908c5ac8ccbabd1057da3c3845dc3ac3",
    "284c56d7961863ab6408bd439e16c0ae22b306d7",
    "6d95fe580646a9f12b9cc2f37bd1e9c4d72fbad7",
    "5573b298103c581addbf74f8b4b2a2cd63616517",
    "5c776f52388100bbf302af9c2db0ebb49d8906e1",
}
EXPECTED_SOURCE_PATHS = [
    "FreeRTOS_CLI.c",
    "FreeRTOS_CLI.h",
    "History.txt",
    "LICENSE_INFORMATION.txt",
]
EXPECTED_SUBTREE = {
    ".gitattributes",
    "FreeRTOS_CLI.c",
    "FreeRTOS_CLI.h",
    "History.txt",
    "LICENSE_INFORMATION.txt",
    "PROVENANCE.json",
    "README.openCFW.md",
    "g2-patches/0001-suppress-unknown-command-for-blank-input.patch",
    "upstream/objects.json",
    "verify_snapshot.py",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_object_sha1(kind: str, data: bytes) -> str:
    header = f"{kind} {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data, usedforsecurity=False).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FreeRTOS+CLI snapshot verification failed: {message}")


def normalize_registration_text(value: str) -> str:
    """Canonicalize path separators used by source-controlled registrations."""
    value = value.replace("\\", "/")
    while "//" in value:
        value = value.replace("//", "/")
    while "/./" in value:
        value = value.replace("/./", "/")
    return value


def is_generated_build_path(path: Path, root: Path) -> bool:
    """Return true for generated component directories named build/build-*.*"""
    return any(
        part == "build" or part.startswith("build-")
        for part in path.relative_to(root).parts[:-1]
    )


def verify_provenance() -> dict[str, Any]:
    raw = PROVENANCE.read_bytes()
    require(len(raw) == EXPECTED_PROVENANCE_SIZE, "provenance size changed")
    require(sha256(raw) == EXPECTED_PROVENANCE_SHA256, "provenance bytes changed")
    value = json.loads(raw)
    require(
        set(value)
        == {"schema_version", "component", "license", "upstream", "selection", "g2_boundary", "files"},
        "provenance schema changed",
    )
    require(value["schema_version"] == 1, "schema version changed")
    require(value["component"] == "FreeRTOS-Plus-CLI", "component changed")
    require(value["license"] == "MIT", "license changed")

    upstream = value["upstream"]
    require(upstream["repository"] == "https://github.com/FreeRTOS/FreeRTOS.git", "repository changed")
    require(upstream["selected_commit"] == SELECTED_COMMIT, "selected commit changed")
    require(upstream["selected_tree"] == SELECTED_TREE, "selected tree changed")
    require(upstream["selected_parent"] == SELECTED_PARENT, "selected parent changed")
    require(upstream["selected_commit_payload_size"] == SELECTED_COMMIT_SIZE, "selected commit size pin changed")
    require(upstream["selected_commit_payload_sha256"] == SELECTED_COMMIT_SHA256, "selected commit digest pin changed")
    require(upstream["selected_commit_signature"]["present"] is True, "selected signature presence changed")
    require(upstream["selected_commit_signature"]["signer_trust_verified"] is False, "unsupported signer trust claim")
    require(upstream["object_closure_path"] == "upstream/objects.json", "object closure path changed")
    require(upstream["object_closure_size"] == EXPECTED_OBJECTS_SIZE, "object closure size pin changed")
    require(upstream["object_closure_sha256"] == EXPECTED_OBJECTS_SHA256, "object closure digest pin changed")
    ceiling = upstream["identical_file_pair_ceiling"]
    require(ceiling["commit"] == CEILING_COMMIT, "file-pair ceiling commit changed")
    require(ceiling["tree"] == CEILING_TREE, "file-pair ceiling tree changed")
    require(ceiling["parent"] == CEILING_PARENT, "file-pair ceiling parent changed")
    require(ceiling["commit_payload_size"] == CEILING_COMMIT_SIZE, "ceiling commit size pin changed")
    require(ceiling["commit_payload_sha256"] == CEILING_COMMIT_SHA256, "ceiling commit digest pin changed")
    require(ceiling["unchanged_paths"] == ["FreeRTOS_CLI.c", "FreeRTOS_CLI.h"], "file-pair ceiling scope changed")

    selection = value["selection"]
    require(selection["exact_g2_vendor_commit_proven"] is False, "vendor checkout is overclaimed")
    require(selection["selected_file_count"] == 4, "selected source count changed")
    require(selection["integration_status"] == "authenticated and verified offline; no production registration", "production boundary changed")

    boundary = value["g2_boundary"]
    abi = boundary["recovered_abi"]
    require(abi["target_pointer_bits"] == 32 and abi["size_t_bits"] == 32, "target scalar ABI changed")
    require(abi["descriptor_size"] == 16, "descriptor size changed")
    require(
        abi["descriptor_offsets"]
        == {"pcCommand": 0, "pcHelpString": 4, "pxCommandInterpreter": 8, "cExpectedNumberOfParameters": 12},
        "descriptor field ABI changed",
    )
    require(abi["registered_list_node_size"] == 8, "registered node ABI changed")
    require(abi["variable_parameter_sentinel"] == -1, "variable parameter sentinel changed")
    config = boundary["recovered_configuration"]
    require(config["effective_output_buffer_bytes"] == 128, "effective output size changed")
    require(config["safe_nul_terminated_input_payload_max"] == 127, "safe input size changed")
    require(config["observed_registration_api"] == "dynamic", "observed registration policy changed")
    require(config["dynamic_registration_count"] == 76, "registration count changed")
    require(config["configSUPPORT_STATIC_ALLOCATION"] == "not statically proven", "static policy was guessed")
    require(config["selected_openCFW_static_allocation_policy"] == "unresolved", "static policy unexpectedly selected")
    require(boundary["first_party_glue"]["included"] is False, "first-party commands entered snapshot")
    require(boundary["first_party_glue"]["registered_descriptor_count"] == 76, "excluded command census changed")
    patch = boundary["local_patch"]
    require(patch["stock_instruction_range"] == ["0x005848CA", "0x005848F4"], "G2 patch range changed")
    require(patch["stock_instruction_size"] == 42, "G2 patch span changed")
    require(patch["stock_instruction_sha256"] == "4ed35ac83ff6802181aee553929f5eadff5e6b6c797601145d1c688c88eae7c1", "G2 patch instruction hash changed")
    require(patch["present_in_official_history"] is False, "official-history patch claim changed")
    require(patch["production_status"] == "documented source delta only; not production-configured", "G2 patch unexpectedly integrated")
    return value


def decode_object_payload(record: dict[str, Any], role: str) -> bytes:
    require(set(record) == {"oid", "payload_base64"} or set(record) == {"oid", "root_tree", "role", "payload_base64"}, f"{role} object schema changed")
    try:
        payload = base64.b64decode(record["payload_base64"], validate=True)
    except Exception as exc:
        raise SystemExit(f"FreeRTOS+CLI snapshot verification failed: invalid {role} base64") from exc
    return payload


def parse_tree(payload: bytes) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    cursor = 0
    while cursor < len(payload):
        space = payload.find(b" ", cursor)
        nul = payload.find(b"\0", space + 1)
        require(space > cursor and nul > space, "malformed tree payload")
        require(nul + 21 <= len(payload), "truncated tree object ID")
        mode = payload[cursor:space].decode("ascii")
        name = payload[space + 1:nul].decode("utf-8")
        oid = payload[nul + 1:nul + 21].hex()
        require(mode in {"40000", "100644", "100755", "120000", "160000"}, f"unsupported tree mode {mode}")
        require(name and "/" not in name and "\0" not in name, "invalid tree entry name")
        entries.append({"mode": mode, "name": name, "oid": oid})
        cursor = nul + 21
    require(cursor == len(payload), "tree parser did not consume payload")
    require(len({item["name"] for item in entries}) == len(entries), "duplicate tree entry")
    return entries


def lookup_blob(trees: dict[str, list[dict[str, str]]], root: str, path: str) -> tuple[str, str]:
    tree = root
    parts = path.split("/")
    for index, name in enumerate(parts):
        require(tree in trees, f"missing path tree for {path}")
        matches = [entry for entry in trees[tree] if entry["name"] == name]
        require(len(matches) == 1, f"path is absent from tree: {path}")
        entry = matches[0]
        if index < len(parts) - 1:
            require(entry["mode"] == "40000", f"non-tree path component: {path}")
            tree = entry["oid"]
        else:
            require(entry["mode"] in {"100644", "100755"}, f"selected path is not a regular blob: {path}")
            return entry["mode"], entry["oid"]
    raise AssertionError("unreachable")


def verify_object_closure(provenance: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    raw = OBJECTS.read_bytes()
    require(len(raw) == EXPECTED_OBJECTS_SIZE, "object closure size changed")
    require(sha256(raw) == EXPECTED_OBJECTS_SHA256, "object closure bytes changed")
    closure = json.loads(raw)
    require(set(closure) == {"schema_version", "commits", "trees"}, "object closure schema changed")
    require(closure["schema_version"] == 1, "object closure version changed")

    expected_commits = {
        "selected": (SELECTED_COMMIT, SELECTED_TREE, SELECTED_PARENT, SELECTED_COMMIT_SIZE, SELECTED_COMMIT_SHA256),
        "identical_file_pair_ceiling": (CEILING_COMMIT, CEILING_TREE, CEILING_PARENT, CEILING_COMMIT_SIZE, CEILING_COMMIT_SHA256),
    }
    seen_roles: set[str] = set()
    for record in closure["commits"]:
        role = record["role"]
        require(role in expected_commits and role not in seen_roles, f"unexpected or duplicate commit role {role}")
        seen_roles.add(role)
        oid, tree, parent, size, digest = expected_commits[role]
        require(record["oid"] == oid and record["root_tree"] == tree, f"{role} identity changed")
        payload = decode_object_payload(record, role)
        require(len(payload) == size, f"{role} payload size changed")
        require(sha256(payload) == digest, f"{role} payload digest changed")
        require(git_object_sha1("commit", payload) == oid, f"{role} commit object ID changed")
        require(payload.startswith(f"tree {tree}\nparent {parent}\n".encode("ascii")), f"{role} tree/parent chain changed")
        require(b"gpgsig -----BEGIN PGP SIGNATURE-----\n" in payload, f"{role} signature payload missing")
    require(seen_roles == set(expected_commits), "commit closure changed")

    trees: dict[str, list[dict[str, str]]] = {}
    for record in closure["trees"]:
        payload = decode_object_payload(record, "tree")
        oid = record["oid"]
        require(oid not in trees, f"duplicate tree object {oid}")
        require(git_object_sha1("tree", payload) == oid, f"tree object ID changed: {oid}")
        trees[oid] = parse_tree(payload)
    require(set(trees) == EXPECTED_TREE_OBJECTS, "tree object closure changed")

    for item in provenance["files"]:
        mode, oid = lookup_blob(trees, SELECTED_TREE, item["upstream_path"])
        require(mode == item["git_mode"], f"selected tree mode changed: {item['local_path']}")
        require(oid == item["git_blob_sha1"], f"selected tree blob changed: {item['local_path']}")
    for local in ("FreeRTOS_CLI.c", "FreeRTOS_CLI.h"):
        item = next(record for record in provenance["files"] if record["local_path"] == local)
        mode, oid = lookup_blob(trees, CEILING_TREE, item["upstream_path"])
        require(mode == item["git_mode"], f"ceiling tree mode changed: {local}")
        require(oid == item["git_blob_sha1"], f"C/H pair is no longer identical at ceiling: {local}")
    return trees


def verify_source_files(provenance: dict[str, Any]) -> None:
    records = provenance["files"]
    require([item["local_path"] for item in records] == EXPECTED_SOURCE_PATHS, "source order/path set changed")
    for item in records:
        require(
            set(item) == {"local_path", "upstream_path", "git_mode", "size", "sha256", "git_blob_sha1"},
            f"source record schema changed: {item['local_path']}",
        )
        source = HERE / item["local_path"]
        data = source.read_bytes()
        require(source.is_file(), f"source missing: {item['local_path']}")
        require(not (source.stat().st_mode & stat.S_IXUSR), f"source became executable: {item['local_path']}")
        require(len(data) == item["size"], f"source size changed: {item['local_path']}")
        require(sha256(data) == item["sha256"], f"source SHA-256 changed: {item['local_path']}")
        require(git_object_sha1("blob", data) == item["git_blob_sha1"], f"source Git blob changed: {item['local_path']}")
        require(b"\r\n" in data and data.replace(b"\r\n", b"").find(b"\n") == -1, f"official CRLF bytes changed: {item['local_path']}")

    actual = {
        path.relative_to(HERE).as_posix()
        for path in HERE.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }
    require(actual == EXPECTED_SUBTREE, "snapshot subtree inventory changed")
    require(
        (HERE / ".gitattributes").read_bytes()
        == b"* -text whitespace=-trailing-space,-space-before-tab\n",
        "byte-preservation attributes changed",
    )


def verify_markers_and_patch(provenance: dict[str, Any]) -> None:
    source = (HERE / "FreeRTOS_CLI.c").read_text(encoding="utf-8")
    header = (HERE / "FreeRTOS_CLI.h").read_text(encoding="utf-8")
    history = (HERE / "History.txt").read_text(encoding="utf-8")
    license_text = (HERE / "LICENSE_INFORMATION.txt").read_text(encoding="utf-8")
    require("FreeRTOS+CLI V1.0.4" in source and "FreeRTOS+CLI V1.0.4" in header, "V1.0.4 source marker missing")
    require("Changes between V1.0.3 and V1.0.4" in history, "V1.0.4 history marker missing")
    require("FreeRTOS+CLI is released under the following MIT license." in license_text, "MIT declaration missing")
    require("Permission is hereby granted, free of charge" in license_text, "MIT grant missing")
    require('typedef BaseType_t (*pdCOMMAND_LINE_CALLBACK)( char *pcWriteBuffer, size_t xWriteBufferLen, const char *pcCommandString );' in header, "callback ABI declaration changed")
    require("int8_t cExpectedNumberOfParameters;" in header, "signed parameter-count field changed")

    patch_data = PATCH.read_bytes()
    require(len(patch_data) == EXPECTED_PATCH_SIZE, "G2 patch file size changed")
    require(sha256(patch_data) == EXPECTED_PATCH_SHA256, "G2 patch file bytes changed")
    patch_text = patch_data.decode("utf-8")
    for marker in (
        "[0x005848CA,0x005848F4)",
        "4ed35ac83ff6802181aee553929f5eadff5e6b6c797601145d1c688c88eae7c1",
        "strlen( pcCommandInput ) == 1",
        "pcCommandInput[ 0 ] == '\\r'",
        "strlen( pcCommandInput ) == 0",
        "pcCommandInput[ 0 ] == '\\0'",
    ):
        require(marker in patch_text, f"G2 patch marker missing: {marker}")
    require(patch_text.count("--- a/FreeRTOS_CLI.c") == 1, "G2 patch source boundary changed")
    require(patch_text.count("+++ b/FreeRTOS_CLI.c") == 1, "G2 patch target boundary changed")
    require("RegisterCommand" not in patch_text and "CLI_Command_Definition_t" not in patch_text, "G2 patch gained descriptor/registration content")

    patch_record = provenance["g2_boundary"]["local_patch"]
    require(patch_record["source_patch_size"] == EXPECTED_PATCH_SIZE, "patch size metadata changed")
    require(patch_record["source_patch_sha256"] == EXPECTED_PATCH_SHA256, "patch digest metadata changed")


def verify_official_image(provenance: dict[str, Any]) -> None:
    if not IMAGE.exists():
        return
    image = IMAGE.read_bytes()
    require(len(image) == EXPECTED_IMAGE_SIZE, "official image size changed")
    require(sha256(image) == EXPECTED_IMAGE_SHA256, "official image hash changed")
    boundary = provenance["g2_boundary"]
    for function in boundary["functions"]:
        start = int(function["start"], 16)
        end = int(function["end"], 16)
        span = image[start - LOAD_BASE:end - LOAD_BASE]
        require(len(span) == function["size"], f"{function['name']} stock span truncated")
        require(sha256(span) == function["sha256"], f"{function['name']} stock span changed")
    patch = boundary["local_patch"]
    start, end = (int(address, 16) for address in patch["stock_instruction_range"])
    span = image[start - LOAD_BASE:end - LOAD_BASE]
    require(len(span) == patch["stock_instruction_size"], "G2 patch instruction span truncated")
    require(sha256(span) == patch["stock_instruction_sha256"], "G2 patch instruction bytes changed")


def verify_production_exclusion() -> None:
    # The authenticated snapshot remains an oracle, not a production build
    # input.  Production may register a separately maintained, notice-bearing
    # adaptation and cite ``FreeRTOS_CLI.c`` by upstream URL or basename; only
    # a direct local snapshot path or its Makefile directory variable would
    # compile the vendored translation unit itself.
    reference_tokens = (
        "third_party/freertos-plus-cli",
        "FREERTOS_PLUS_CLI_DIR",
    )

    # Registering this verifier with ``vendor-snapshots`` is not a production
    # integration.  Keep the two required Makefile references exact so that
    # reusing the directory variable in a compiler, linker, component, or
    # firmware recipe remains fail-closed.
    makefile = ROOT / "Makefile"
    if makefile.is_file():
        allowed_makefile_references = {
            "FREERTOS_PLUS_CLI_DIR := third_party/freertos-plus-cli",
            "\t$(PYTHON) $(FREERTOS_PLUS_CLI_DIR)/verify_snapshot.py",
        }
        for line_number, line in enumerate(
            makefile.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            normalized = normalize_registration_text(line)
            if any(token in normalized for token in reference_tokens):
                require(
                    line in allowed_makefile_references,
                    f"snapshot is production-configured by Makefile:{line_number}",
                )

    configured: set[Path] = set()
    manifests = ROOT / "manifests"
    if manifests.is_dir():
        configured.update(path for path in manifests.rglob("*") if path.is_file())

    # Component JSON includes generated-patch/overlay configuration.  The
    # remaining suffixes cover source, headers, assembly, linker scripts, and
    # component build inputs without treating component documentation as a
    # firmware input.
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
            and not is_generated_build_path(path, components)
            and (path.suffix.lower() in component_suffixes or path.name == "Makefile")
        )

    # These are the production component/firmware assembly engines.  Research
    # analyzers intentionally remain outside this scan.
    configured.update(
        {
            ROOT / "tools" / "apollo_overlay.py",
            ROOT / "tools" / "open_cfw.py",
        }
    )
    for path in sorted(configured):
        if not path.is_file():
            continue
        content = normalize_registration_text(path.read_text(encoding="utf-8"))
        require(
            not any(token in content for token in reference_tokens),
            f"snapshot is production-configured by {path.relative_to(ROOT)}",
        )


def main() -> None:
    provenance = verify_provenance()
    verify_object_closure(provenance)
    verify_source_files(provenance)
    verify_markers_and_patch(provenance)
    verify_official_image(provenance)
    verify_production_exclusion()
    print("FreeRTOS+CLI source snapshot verification passed")


if __name__ == "__main__":
    main()
