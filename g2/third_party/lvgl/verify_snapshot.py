#!/usr/bin/env python3
"""Fail-closed, offline verification for the openCFW LVGL snapshot."""

from __future__ import annotations

import base64
import hashlib
import json
import stat
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
PROVENANCE = HERE / "PROVENANCE.json"

EXPECTED_COMMIT = "344c7c318047b7348e1be8572a9fd4260c251cfa"
EXPECTED_TREE = "2c76db856ec570f3ee12565181e5cf52bdd33d78"
EXPECTED_PARENT = "9f090d2353073e6709acacdf8bc1e36252187ca7"
EXPECTED_PROVENANCE_SIZE = 119250
EXPECTED_PROVENANCE_SHA256 = (
    "ed516ba0027c33688cadd5915c7baed5a93b6a691a1c8bc57c88b53952df243d"
)
EXPECTED_RECORDS_SHA256 = (
    "00a2d8eb9c47223c2bd3ff41568ed7921e42d29aae1f171ba0023fcf8242759f"
)
EXPECTED_SOURCE_PATHS_SHA256 = (
    "f93e5300f92c7fccdb003b04a37f223727166064b5bd2f3b2913e744197e401c"
)
EXPECTED_HEADER_PATHS_SHA256 = (
    "902b5c498fd091fd1f2e48be9d75c04b9c4c1047e1faa63d7bbc15f56b580eb7"
)
EXPECTED_COMMIT_RECORD_SIZE = 1634
EXPECTED_COMMIT_RECORD_SHA256 = (
    "acb765f0389ebfe50ff7ff1f834a31d8088e118dd176dac0362c3d97feea797a"
)
EXPECTED_COMMIT_PAYLOAD_SIZE = 1103
EXPECTED_COMMIT_PAYLOAD_SHA256 = (
    "497870227fbf435ee248b7a7aff082afe3db93690735a430a34bd69152e77eda"
)
EXPECTED_TREE_CLOSURE_SIZE = 149312
EXPECTED_TREE_CLOSURE_SHA256 = (
    "9aa5b7adccc1e74492a02858859ae9abf4f8b05468adeb45ae3e9dde9df80a17"
)
EXPECTED_CONFIG_SIZE = 1125
EXPECTED_CONFIG_SHA256 = (
    "2876e2abb3821103d0f8dd7dda71e2b1cea70ab194ffe5c4955a194798d86b5b"
)
EXPECTED_ABI_SIZE = 3691
EXPECTED_ABI_SHA256 = (
    "6e45a77ae37a9715bbf8dcc31440a845116a30ed5ff6b0de275cc04cafccef91"
)
EXPECTED_LICENSE_SIZE = 1072
EXPECTED_LICENSE_SHA256 = (
    "27a80bd36832ab42d35ad60c08b2b230a807a9bc0d58e94ec1531543dc49cbe8"
)
EXPECTED_LICENSE_BLOB = "690d2dfd7e97ca8e06535a496761c5e81aece439"

EXPECTED_SOURCE_PATHS = [
    "src/core/lv_group.c",
    "src/core/lv_obj.c",
    "src/core/lv_obj_class.c",
    "src/core/lv_obj_draw.c",
    "src/core/lv_obj_event.c",
    "src/core/lv_obj_pos.c",
    "src/core/lv_obj_scroll.c",
    "src/core/lv_obj_style.c",
    "src/core/lv_obj_tree.c",
    "src/core/lv_refr.c",
    "src/display/lv_display.c",
    "src/draw/lv_draw.c",
    "src/draw/lv_draw_arc.c",
    "src/draw/lv_draw_buf.c",
    "src/draw/lv_draw_image.c",
    "src/draw/lv_draw_label.c",
    "src/draw/lv_draw_line.c",
    "src/draw/lv_draw_mask.c",
    "src/draw/lv_draw_rect.c",
    "src/draw/lv_image_decoder.c",
    "src/font/lv_font.c",
    "src/font/lv_font_fmt_txt.c",
    "src/layouts/flex/lv_flex.c",
    "src/layouts/grid/lv_grid.c",
    "src/libs/bin_decoder/lv_bin_decoder.c",
    "src/libs/bmp/lv_bmp.c",
    "src/libs/freetype/lv_freetype.c",
    "src/libs/freetype/lv_freetype_glyph.c",
    "src/libs/freetype/lv_freetype_image.c",
    "src/libs/freetype/lv_freetype_outline.c",
    "src/libs/fsdrv/lv_fs_littlefs.c",
    "src/lv_init.c",
    "src/misc/cache/lv_cache.c",
    "src/misc/cache/lv_cache_entry.c",
    "src/misc/cache/lv_cache_lru_rb.c",
    "src/misc/lv_anim.c",
    "src/misc/lv_array.c",
    "src/misc/lv_event.c",
    "src/misc/lv_fs.c",
    "src/misc/lv_iter.c",
    "src/misc/lv_palette.c",
    "src/misc/lv_rb.c",
    "src/misc/lv_style.c",
    "src/misc/lv_text.c",
    "src/misc/lv_timer.c",
    "src/osal/lv_freertos.c",
    "src/stdlib/lv_mem.c",
    "src/widgets/animimage/lv_animimage.c",
    "src/widgets/arc/lv_arc.c",
    "src/widgets/bar/lv_bar.c",
    "src/widgets/buttonmatrix/lv_buttonmatrix.c",
    "src/widgets/calendar/lv_calendar.c",
    "src/widgets/calendar/lv_calendar_header_arrow.c",
    "src/widgets/chart/lv_chart.c",
    "src/widgets/dropdown/lv_dropdown.c",
    "src/widgets/image/lv_image.c",
    "src/widgets/keyboard/lv_keyboard.c",
    "src/widgets/label/lv_label.c",
    "src/widgets/menu/lv_menu.c",
    "src/widgets/roller/lv_roller.c",
    "src/widgets/span/lv_span.c",
    "src/widgets/spinbox/lv_spinbox.c",
    "src/widgets/switch/lv_switch.c",
    "src/widgets/tabview/lv_tabview.c",
    "src/widgets/textarea/lv_textarea.c",
]

EXPECTED_AMBIQ_DRAW_EXCLUSIONS = [
    "src/draw/ambiq/lv_draw_ambiq.c",
    "src/draw/ambiq/lv_draw_ambiq_arc.c",
    "src/draw/ambiq/lv_draw_ambiq_box_shadow.c",
    "src/draw/ambiq/lv_draw_ambiq_buffer.c",
    "src/draw/ambiq/lv_draw_ambiq_fill.c",
    "src/draw/ambiq/lv_draw_ambiq_img.c",
    "src/draw/ambiq/lv_draw_ambiq_letter.c",
    "src/draw/ambiq/lv_draw_ambiq_mask_rect.c",
    "src/draw/ambiq/lv_draw_ambiq_private.c",
    "src/draw/ambiq/lv_draw_ambiq_triangle.c",
    "src/draw/ambiq/lv_draw_ambiq_vector_font.c",
]

METADATA_PATHS = {
    ".gitattributes",
    "PROVENANCE.json",
    "README.openCFW.md",
    "verify_snapshot.py",
    "g2-config/lv_conf_recovered.h",
    "g2-config/lvgl_g2_abi.json",
    f"upstream/{EXPECTED_COMMIT}.commit.json",
    "upstream/trees.json",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_object_sha1(kind: str, data: bytes) -> str:
    header = f"{kind} {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data, usedforsecurity=False).hexdigest()


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return sha256(encoded)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"LVGL snapshot verification failed: {message}")


def verify_provenance() -> dict[str, Any]:
    raw = PROVENANCE.read_bytes()
    require(len(raw) == EXPECTED_PROVENANCE_SIZE, "provenance size changed")
    require(sha256(raw) == EXPECTED_PROVENANCE_SHA256, "provenance bytes changed")
    value = json.loads(raw)
    require(
        set(value)
        == {
            "schema_version",
            "component",
            "license",
            "upstream",
            "selection",
            "exclusions",
            "g2_boundary",
            "files",
        },
        "provenance schema changed",
    )
    require(value["schema_version"] == 1, "schema version changed")
    require(value["component"] == "LVGL", "component changed")
    require(value["license"] == "MIT", "license changed")

    upstream = value["upstream"]
    require(upstream["repository"] == "https://github.com/lvgl/lvgl.git", "repository changed")
    require(upstream["selected_ref"] == EXPECTED_COMMIT, "selected ref changed")
    require(upstream["selected_commit"] == EXPECTED_COMMIT, "selected commit changed")
    require(upstream["selected_tree"] == EXPECTED_TREE, "selected tree changed")
    require(upstream["parent_commits"] == [EXPECTED_PARENT], "commit parent changed")
    require(upstream["declared_version"] == {"major": 9, "minor": 3, "patch": 0, "info": "dev"}, "declared development version changed")
    require(upstream["released_v9_3_0_commit"] == "c033a98afddd65aaafeebea625382a94020fe4a7", "release comparison changed")
    require(upstream["commit_signature"]["present"] is True, "commit signature missing")
    require(upstream["commit_signature"]["signer_trust_verified"] is False, "unsupported signer-trust claim")

    selection = value["selection"]
    require(selection["exact_g2_checkout_proven"] is False, "unsupported exact-G2 checkout claim")
    require(selection["released_v9_3_0_selected"] is False, "snapshot mislabeled as release")
    require(selection["compatible_floor_commit"] == "60d976c466e8619326edfbd193fd2a046c10113f", "compatibility floor changed")
    require(selection["compatible_ceiling_commit"] == EXPECTED_COMMIT, "compatibility ceiling changed")
    require(selection["first_incompatible_commit"] == "f35f0859eb477c79906cf531ed394306119097f8", "first incompatible commit changed")
    require(selection["selected_translation_unit_count"] == 65, "translation-unit count changed")
    require(selection["selected_core_optional_translation_unit_count"] == 61, "core/optional count changed")
    require(selection["selected_freetype_wrapper_translation_unit_count"] == 4, "FreeType-wrapper count changed")
    require(selection["compiler_resolved_header_count"] == 251, "compiler header count changed")
    require(selection["reference_only_header_count"] == 1, "reference-only header count changed")
    require(selection["selected_header_count"] == 252, "header count changed")
    require(selection["selected_licensed_file_count"] == 318, "upstream file count changed")
    require(selection["selected_upstream_bytes"] == 2503751, "upstream byte count changed")
    require(selection["translation_unit_paths_sha256"] == EXPECTED_SOURCE_PATHS_SHA256, "stored translation-unit path digest changed")
    require(selection["header_paths_sha256"] == EXPECTED_HEADER_PATHS_SHA256, "stored header path digest changed")
    require(selection["source_records_sha256"] == EXPECTED_RECORDS_SHA256, "stored source-record digest changed")
    require(selection["integration_status"] == "authenticated and verified offline; no production registration", "production-exclusion boundary changed")

    exclusions = value["exclusions"]
    require(exclusions["ambiq_draw_backend_count"] == 11, "Ambiq exclusion count changed")
    require(exclusions["ambiq_draw_backend_translation_units"] == EXPECTED_AMBIQ_DRAW_EXCLUSIONS, "Ambiq exclusion inventory changed")
    require(exclusions["ambiq_display_port"] == "lvgl_ambiq_porting/lv_ambiq_display.c", "Ambiq display boundary changed")
    require(exclusions["ambiq_freetype_system_glue"] == "lvgl_ambiq_demo/lvgl_ttf/src/am_ftsystem.c", "FreeType system-glue boundary changed")
    return value


def verify_commit_object(provenance: dict[str, Any]) -> None:
    path = HERE / provenance["upstream"]["commit_object_record_path"]
    raw = path.read_bytes()
    require(len(raw) == EXPECTED_COMMIT_RECORD_SIZE, "commit record size changed")
    require(sha256(raw) == EXPECTED_COMMIT_RECORD_SHA256, "commit record bytes changed")
    record = json.loads(raw)
    require(set(record) == {"schema_version", "oid", "object_type", "payload_encoding", "payload_base64"}, "commit record schema changed")
    require(record["schema_version"] == 1, "commit record schema version changed")
    require(record["oid"] == EXPECTED_COMMIT, "commit record ID changed")
    require(record["object_type"] == "commit", "commit record type changed")
    require(record["payload_encoding"] == "base64", "commit record encoding changed")
    try:
        payload = base64.b64decode(record["payload_base64"], validate=True)
    except (TypeError, ValueError) as exc:
        raise SystemExit(f"LVGL snapshot verification failed: invalid commit payload: {exc}") from exc
    require(len(payload) == EXPECTED_COMMIT_PAYLOAD_SIZE, "commit payload size changed")
    require(sha256(payload) == EXPECTED_COMMIT_PAYLOAD_SHA256, "commit payload bytes changed")
    require(git_object_sha1("commit", payload) == EXPECTED_COMMIT, "commit object ID changed")
    require(payload.startswith(f"tree {EXPECTED_TREE}\nparent {EXPECTED_PARENT}\n".encode()), "commit tree/parent chain changed")
    require(b"gpgsig -----BEGIN PGP SIGNATURE-----\n" in payload, "commit OpenPGP signature bytes missing")
    require(payload.endswith(b"fix(area): test and fix lv_area_diff edge case (#7907)\n\n"), "commit subject changed")


def verify_tree_closure(provenance: dict[str, Any]) -> None:
    raw = (HERE / provenance["upstream"]["tree_closure_path"]).read_bytes()
    require(len(raw) == EXPECTED_TREE_CLOSURE_SIZE, "tree closure size changed")
    require(sha256(raw) == EXPECTED_TREE_CLOSURE_SHA256, "tree closure bytes changed")
    closure = json.loads(raw)
    require(set(closure) == {"schema_version", "root_tree", "trees"}, "tree closure schema changed")
    require(closure["schema_version"] == 1, "tree closure schema version changed")
    require(closure["root_tree"] == EXPECTED_TREE, "tree closure root changed")
    require(len(closure["trees"]) == 107, "tree closure object count changed")

    by_oid: dict[str, list[dict[str, str]]] = {}
    by_path: dict[str, str] = {}
    for tree in closure["trees"]:
        require(set(tree) == {"oid", "path", "entries"}, "tree record schema changed")
        oid = tree["oid"]
        tree_path = tree["path"]
        require(oid not in by_oid, f"duplicate tree object: {oid}")
        require(tree_path not in by_path, f"duplicate tree path: {tree_path}")
        payload = bytearray()
        names: set[str] = set()
        for entry in tree["entries"]:
            require(set(entry) == {"mode", "type", "oid", "name"}, f"tree entry schema changed: {oid}")
            mode, kind = entry["mode"], entry["type"]
            require((mode, kind) in {("040000", "tree"), ("100644", "blob"), ("100755", "blob")}, f"unsupported tree entry: {oid}")
            require(entry["name"] not in names, f"duplicate tree entry: {oid}")
            names.add(entry["name"])
            encoded_mode = "40000" if mode == "040000" else mode
            payload.extend(f"{encoded_mode} {entry['name']}".encode())
            payload.append(0)
            payload.extend(bytes.fromhex(entry["oid"]))
        require(git_object_sha1("tree", bytes(payload)) == oid, f"tree object ID mismatch: {oid}")
        by_oid[oid] = tree["entries"]
        by_path[tree_path] = oid
    require(by_path.get("") == EXPECTED_TREE, "root tree path mapping changed")

    for record in provenance["files"]:
        tree_oid = EXPECTED_TREE
        parts = record["upstream_path"].split("/")
        for index, part in enumerate(parts):
            matches = [entry for entry in by_oid[tree_oid] if entry["name"] == part]
            require(len(matches) == 1, f"path absent from selected tree: {record['upstream_path']}")
            entry = matches[0]
            if index < len(parts) - 1:
                require(entry["type"] == "tree", f"non-tree path component: {record['upstream_path']}")
                require(entry["oid"] in by_oid, f"missing ancestor tree: {record['upstream_path']}")
                tree_oid = entry["oid"]
            else:
                require(entry["type"] == "blob", f"selected path is not a blob: {record['upstream_path']}")
                require(entry["mode"] == record["git_mode"], f"tree mode mismatch: {record['upstream_path']}")
                require(entry["oid"] == record["git_blob_sha1"], f"tree blob mismatch: {record['upstream_path']}")


def verify_files(provenance: dict[str, Any]) -> None:
    records = provenance["files"]
    require(len(records) == 318, "source record count changed")
    require(canonical_sha256(records) == EXPECTED_RECORDS_SHA256, "source records changed")
    require([item["local_path"] for item in records] == sorted(item["local_path"] for item in records), "source record order changed")
    sources = [item["local_path"] for item in records if item["role"] == "translation_unit"]
    headers = [item["local_path"] for item in records if item["role"] == "header"]
    licenses = [item["local_path"] for item in records if item["role"] == "license"]
    require(sources == EXPECTED_SOURCE_PATHS, "translation-unit membership changed")
    require(canonical_sha256(sources) == EXPECTED_SOURCE_PATHS_SHA256, "translation-unit path digest changed")
    require(len(headers) == 252, "header membership count changed")
    require(canonical_sha256(headers) == EXPECTED_HEADER_PATHS_SHA256, "header membership changed")
    require(licenses == ["LICENCE.txt"], "license membership changed")
    for item in records:
        require(set(item) == {"local_path", "upstream_path", "role", "git_mode", "size", "sha256", "git_blob_sha1"}, f"source record schema changed: {item['local_path']}")
        require(item["local_path"] == item["upstream_path"], f"path remapping changed: {item['local_path']}")
        require(item["git_mode"] in {"100644", "100755"}, f"selected file mode changed: {item['local_path']}")
        path = HERE / item["local_path"]
        require(path.is_file(), f"selected file missing: {item['local_path']}")
        data = path.read_bytes()
        require(bool(path.stat().st_mode & stat.S_IXUSR) == (item["git_mode"] == "100755"), f"selected file executable mode changed: {item['local_path']}")
        require(len(data) == item["size"], f"selected file size changed: {item['local_path']}")
        require(sha256(data) == item["sha256"], f"selected file SHA-256 changed: {item['local_path']}")
        require(git_object_sha1("blob", data) == item["git_blob_sha1"], f"selected Git blob changed: {item['local_path']}")

    actual = {
        path.relative_to(HERE).as_posix()
        for path in HERE.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }
    require(actual == {item["local_path"] for item in records} | METADATA_PATHS, "snapshot file set changed")
    require((HERE / ".gitattributes").read_bytes() == b"* -text whitespace=-trailing-space\n", "byte-preservation attributes changed")
    for excluded in EXPECTED_AMBIQ_DRAW_EXCLUSIONS:
        require(not (HERE / excluded).exists(), f"Ambiq backend entered upstream snapshot: {excluded}")


def verify_config_and_abi(provenance: dict[str, Any]) -> None:
    g2 = provenance["g2_boundary"]
    require(g2["configuration_template"] == {"path": "g2-config/lv_conf_recovered.h", "size": EXPECTED_CONFIG_SIZE, "sha256": EXPECTED_CONFIG_SHA256, "complete": False}, "configuration-template metadata changed")
    require(g2["abi_metadata"] == {"path": "g2-config/lvgl_g2_abi.json", "size": EXPECTED_ABI_SIZE, "sha256": EXPECTED_ABI_SHA256}, "ABI-metadata record changed")
    config = (HERE / g2["configuration_template"]["path"]).read_bytes()
    abi_raw = (HERE / g2["abi_metadata"]["path"]).read_bytes()
    require(len(config) == EXPECTED_CONFIG_SIZE and sha256(config) == EXPECTED_CONFIG_SHA256, "recovered configuration template changed")
    require(len(abi_raw) == EXPECTED_ABI_SIZE and sha256(abi_raw) == EXPECTED_ABI_SHA256, "ABI metadata changed")
    abi = json.loads(abi_raw)
    require(abi["status"] == "abi-and-gpu-dependency-identity-closed-production-source-incomplete", "ABI status changed")
    require(abi["g2_vendor_configuration"]["sizeof_lv_global_t"] == 492, "G2 global ABI changed")
    require(abi["official_ceiling_reference_compile"]["sizeof_lv_global_t"] == 504, "reference global ABI changed")
    require(abi["recovered_vendor_compile"]["sizeof_lv_global_t"] == 492, "recovered global ABI changed")
    require(abi["recovered_vendor_compile"]["draw_buffer_handler_size"] == 32, "Ambiq handler ABI changed")
    require(abi["recovered_vendor_compile"]["matches_stock_layout"] is True, "G2 LVGL ABI closure changed")
    require(abi["promotion_gate"]["closed"] is False, "unsafe production ABI promotion")
    require(abi["promotion_gate"]["abi_closed"] is True, "G2 LVGL ABI closure regressed")
    require(abi["promotion_gate"]["gpu_dependency_identity_closed"] is True, "G2 GPU dependency identity closure regressed")
    require(g2["reference_compile"]["production_abi_complete"] is False, "unsafe provenance ABI promotion")
    require(g2["recovered_vendor_compile"]["stock_layout_match"] is True, "recovered compile boundary changed")
    require(g2["ambiq_backend"]["subtree_git_tree_sha1"] == "1e774257495fa43177e04fc5c8a42a77c2d7d619", "Ambiq subtree changed")
    require(g2["nema_dependency"]["nemagfx_version"] == "1.4.12", "NemaGFX version changed")
    require(g2["nema_dependency"]["nemavg_version"] == "1.1.8", "NemaVG version changed")
    require(g2["nema_dependency"]["public_reproduction_commit"] == "b853fded7e545f005727e13bf2ce83018c7e242d", "Nema public reproduction commit changed")
    require(g2["nema_dependency"]["subtree_git_tree_sha1"] == "e690768a6e7b4d6a8d526fc75e8278a2764deff3", "Nema public subtree changed")


def verify_license_and_version(provenance: dict[str, Any]) -> None:
    record = next(item for item in provenance["files"] if item["local_path"] == "LICENCE.txt")
    data = (HERE / "LICENCE.txt").read_bytes()
    require(len(data) == EXPECTED_LICENSE_SIZE, "MIT license size changed")
    require(sha256(data) == EXPECTED_LICENSE_SHA256, "MIT license bytes changed")
    require(record["git_blob_sha1"] == EXPECTED_LICENSE_BLOB, "MIT license blob identity changed")
    text = data.decode("utf-8")
    for marker in ("MIT licence", "Copyright (c) 2025 LVGL Kft", "Permission is hereby granted, free of charge", "THE SOFTWARE IS PROVIDED"):
        require(marker in text, f"MIT license marker missing: {marker}")
    version = (HERE / "lv_version.h").read_text(encoding="utf-8")
    for marker in ("#define LVGL_VERSION_MAJOR 9", "#define LVGL_VERSION_MINOR 3", "#define LVGL_VERSION_PATCH 0", '#define LVGL_VERSION_INFO "dev"'):
        require(marker in version, f"9.3.0-dev marker missing: {marker}")


def main() -> None:
    provenance = verify_provenance()
    verify_commit_object(provenance)
    verify_tree_closure(provenance)
    verify_files(provenance)
    verify_config_and_abi(provenance)
    verify_license_and_version(provenance)
    print("LVGL 9.3.0-dev compatibility-ceiling snapshot verification passed")


if __name__ == "__main__":
    main()
