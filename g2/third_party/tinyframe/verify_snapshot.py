#!/usr/bin/env python3
"""Offline verification for the authenticated TinyFrame core snapshot."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
PROVENANCE_PATH = HERE / "PROVENANCE.json"
EXPECTED_REPOSITORY = "https://github.com/MightyPork/TinyFrame.git"
EXPECTED_COMMIT = "eb75483e035916ef9f3e9fce0d2ae389cb09785f"
EXPECTED_TREE = "0e166ad5f97162b1dbcbcafd2bfef144f68aff13"
EXPECTED_FILES = {
    "TinyFrame.c": (34707, "24c2712966df846fadf54067ac5ed4061e4a19adf11dab1af3f203e17bf41eab", "ac64150369dd155f26d1e47c1f5a10f92887298b"),
    "TinyFrame.h": (15554, "e70ea75c3642fff3f1b28463d4b564402efcd09824b51db7b556cf3a04319b7f", "a142b4bba086f27565bd26282055c357364616b3"),
    "TF_Config.example.h": (2927, "e5faec9f64114f99b744e48de5b1d3de631e3065129004c664197681359aa2f6", "099d026bfd4c8c7705647958127dee002f1bac88"),
    "TF_Integration.example.c": (1326, "fc3533898b58f0a350dea8e2551e1c985f1ecd5961f038f230d068e099ccca6f", "1e1b3572021629891682e49dcf50c1e4d33bbfb6"),
    "LICENSE": (1072, "eb7b9df3ca390100d31f9aac23f2d8dfe0183a63987112675fc58af9a42f6874", "22acaabc6b85723107caae262ec537e710c19aac"),
}
EXPECTED_LOCAL = {
    "g2-config/TF_Config.h": (939, "af73f59617f4f6b63f2cd924a3f38abe0091e35dc7bc374d1814cca974c1430c"),
    "g2-compat/string.h": (160, "15289bfcb93fb4fadb191cc10c78db15b1acc51fc063e0cc24fb0cc65685d391"),
    "g2-compat/stdlib.h": (155, "0f381a3c3d8d317e2b32f707e2c5db8a8548ee8f07db32a609b868c7d4906352"),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data, usedforsecurity=False).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"TinyFrame snapshot verification failed: {message}")


def verify_provenance() -> dict[str, Any]:
    value = json.loads(PROVENANCE_PATH.read_text(encoding="utf-8"))
    require(value["schema_version"] == 1, "schema changed")
    require(value["component"] == "MightyPork/TinyFrame", "component changed")
    require(value["license"] == "MIT", "license changed")
    upstream = value["upstream"]
    require(upstream["repository"] == EXPECTED_REPOSITORY, "repository changed")
    require(upstream["selected_commit"] == EXPECTED_COMMIT, "commit changed")
    require(upstream["selected_tree"] == EXPECTED_TREE, "tree changed")
    selection = value["selection"]
    require(selection["exact_historical_checkout_proven"] is False, "checkout overclaimed")
    require(selection["minimum_patch_core_commit"] == EXPECTED_COMMIT, "core pin changed")
    require(
        selection["core_identical_ceiling_commit"]
        == "a29167a69f052975b0e0134a73b4d31d03afa8fa",
        "checkout ceiling changed",
    )
    boundary = value["g2_boundary"]
    require(boundary["required_compile_option"] == "-fshort-enums", "enum ABI changed")
    require(boundary["pristine_core_size"] == 0x7158, "core size changed")
    require(boundary["vendor_object_size"] == 0x7160, "vendor size changed")
    linked = boundary["linked_translation_unit"]
    require(linked["range"] == [0x4916C8, 0x4922F6], "linked range changed")
    require(linked["linked_functions"] == 31, "linked function count changed")
    require(linked["code_bytes"] == 2994, "linked code size changed")
    require(linked["literal_pool_bytes"] == 124, "linked pool size changed")
    require(linked["physical_bytes"] == 3118, "linked physical size changed")
    require(
        linked["literal_pool_sha256"]
        == "fb922d9523d1afd800c10195240574f3fab0541a9655fd09ceab91990b2e82d0",
        "linked pool identity changed",
    )
    instance = boundary["runtime_instance"]
    require(instance["count"] == 1, "runtime instance count changed")
    require(instance["global_pointer_slot"] == "0x200749C4", "instance slot changed")
    require(instance["role_1"] == "TF_MASTER / peer bit 1", "master role changed")
    require(instance["role_2"] == "TF_SLAVE / peer bit 0", "slave role changed")
    require(instance["application_field_dereferences"] == 0, "opaque pointer claim changed")
    require(
        boundary["adapter_candidate"]
        == "components/shared/tinyframe/runtime_tinyframe_g2_adapter_candidate.c",
        "adapter path changed",
    )
    return value


def verify_files(provenance: dict[str, Any]) -> None:
    recorded = {
        item["path"]: (item["size"], item["sha256"], item["git_blob_sha1"])
        for item in provenance["files"]
    }
    require(recorded == EXPECTED_FILES, "provenance file inventory changed")
    for name, (size, digest, blob_oid) in EXPECTED_FILES.items():
        data = (HERE / name).read_bytes()
        require((len(data), sha256(data), git_blob(data)) == (size, digest, blob_oid), f"{name} changed")
    for name, (size, digest) in EXPECTED_LOCAL.items():
        data = (HERE / name).read_bytes()
        require((len(data), sha256(data)) == (size, digest), f"{name} changed")


def verify_markers() -> None:
    source = (HERE / "TinyFrame.c").read_text(encoding="utf-8")
    header = (HERE / "TinyFrame.h").read_text(encoding="utf-8")
    config = (HERE / "g2-config" / "TF_Config.h").read_text(encoding="utf-8")
    for marker in (
        "TF_Listener_Timeout ftimeout",
        "TF_SendFrame_Begin(tf, msg, listener, ftimeout, timeout)",
        "lst->fn_timeout = NULL;\n",
    ):
        require(marker in source, f"source marker missing: {marker}")
    require("bool TF_Query(TinyFrame *tf" in header, "corrected TF_Query prototype missing")
    for marker in (
        "#define TF_ID_BYTES 2",
        "#define TF_LEN_BYTES 2",
        "#define TF_TYPE_BYTES 2",
        "#define TF_MAX_PAYLOAD_RX 0x6000",
        "#define TF_SENDBUF_LEN 0x400",
        "#define TF_MAX_ID_LST 128",
        "#define TF_MAX_TYPE_LST 32",
        "#define TF_MAX_GEN_LST 10",
        "#define TF_PARSER_TIMEOUT_TICKS 100",
        "#define TF_USE_MUTEX 0",
    ):
        require(marker in config, f"G2 config marker missing: {marker}")
    require("A5A5A5A5" not in source and "5A5A5A5A" not in source, "G2 magic leaked into upstream source")
    require("TF_WriteImpl" not in config, "first-party transport leaked into config")


def main() -> int:
    provenance = verify_provenance()
    verify_files(provenance)
    verify_markers()
    print("TinyFrame snapshot verification passed")
    print(f"selected core commit: {EXPECTED_COMMIT}")
    print("historical checkout interval: eb75483e..a29167a")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
