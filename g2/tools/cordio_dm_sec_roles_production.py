"""Shared fail-closed production-route audit for Cordio DM role wrappers."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/cordio_dm_sec_roles.c"
SOURCE_SIZE = 5_640
SOURCE_SHA256 = "95636a5ef5a28805aef2467868c3e0551d1da6c7d889c11d01fe32c3255810ad"
COMMIT = "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6"

ROUTES = {
    "slave": {
        "open_cfw_cordio_dm_sec_slave_pair_response": (
            0x52BACC, 52,
            "51d88a9a4c1f5cbefe18ac0aa4d38e370e5d1b0c82bb283fcf930f7b09f1a994",
            2, 167_088, 58,
            "39b40d97e25ee2af4aea2401c85db181b6719c7a91f26411f72e40a537aed48b",
            "3d128d207309735fcb905f99f8141af82ad33d7066fe0c484a9ef6486b991655",
        ),
        "open_cfw_cordio_dm_sec_slave_request": (
            0x52BB00, 32,
            "03f00894b62705485ce6b488c58600f9dea84754fa336768c44c64d77e3b28e3",
            2, 167_148, 34,
            "a857cb5a60cebb0093435e14e29665907f47a45f97e0d235c57844bceffc9605",
            "434e5f3ff94eae65939d9335c788f59f4ba31bcdc783749d29c47be48a5ef80b",
        ),
        "open_cfw_cordio_dm_sec_slave_ltk_response": (
            0x52BB20, 64,
            "72922857d5608ffb10cf738c0051c2272e950fed5c65948109bd40a571e47fe4",
            3, 167_184, 68,
            "c3610ca8699208e0b87e44cbeeb06320150234394176b5531d89d4be00b094b9",
            "59a61a6fd89255791fdb2cb5d635ba4cb0b04ba897c640b256e285db502404f9",
        ),
    },
    "master": {
        "open_cfw_cordio_dm_sec_master_smp_encrypt_request": (
            0x55BBC4, 38,
            "878fbf663cc2445b7d03395bf9cb8ab7944658da6a7a8cffac71d70683cbd795",
            2, 167_252, 52,
            "4d49089442eaf61c1e72978ff77c24e57a40ad83e53af0a12794e0468c0e692c",
            "639fdcd4636e4afdab9da9d4c48e40dc649cf72a804ca4ba5994e7fe5e7f8a2b",
        ),
        "open_cfw_cordio_dm_sec_master_pair_request": (
            0x55BBEA, 52,
            "e290734ff914383453ae27304f2bc1710cb86357808d8023ee16818e994578ad",
            2, 167_304, 58,
            "1cec4612ef6646804170e61f9f659fdcb74aeeca9ece2a43a60c7ec3694c0d69",
            "be2c0a45f45e194342609e24f9b776cb6a26e08b3c49fe0ffa9023aec133eb99",
        ),
        "open_cfw_cordio_dm_sec_master_encrypt_request": (
            0x55BC1E, 54,
            "cb65fa971d10bb1e237b38c5a69fa5de850cacd6d6a12ad171ebed98edaa94f7",
            3, 167_364, 62,
            "c731146942c03868d24f80c442a9233c8aecdaae7bef1c46cf4b40841ee52ac3",
            "3d5a9c9b17b23c47e5ea1a17ca37a8284874f259a4bc2dc611c6107c53a6958c",
        ),
    },
}


def audit(kind: str) -> dict[str, Any]:
    if kind not in ROUTES:
        raise RuntimeError(f"unknown DM security role {kind}")
    source = SOURCE.read_bytes()
    if len(source) != SOURCE_SIZE or hashlib.sha256(source).hexdigest() != SOURCE_SHA256:
        raise RuntimeError("dm_sec role production source identity changed")

    overlay = json.loads(
        (ROOT / "components/apollo_main/core_overlay/overlay.json").read_text()
    )
    all_functions = set(ROUTES["slave"]) | set(ROUTES["master"])
    leaves = {
        row["function"]: row for row in overlay.get("relocated_leaves", [])
        if row.get("function") in all_functions
    }
    patches = {
        row["target_function"]: row for row in overlay.get("patch_sites", [])
        if row.get("target_function") in all_functions
    }
    if set(leaves) != all_functions or set(patches) != all_functions:
        raise RuntimeError("dm_sec role production registration is incomplete")

    source_path = SOURCE.relative_to(ROOT).as_posix()
    for function, route in {**ROUTES["slave"], **ROUTES["master"]}.items():
        (stock_start, stock_size, stock_sha, relocation_count, offset,
         size, digest, unrelocated) = route
        leaf = leaves[function]
        patch = patches[function]
        source_record = leaf.get("source", {})
        if (
            leaf.get("profiles") != ["apple-clang"]
            or source_record.get("path") != source_path
            or source_record.get("size") != SOURCE_SIZE
            or source_record.get("sha256") != SOURCE_SHA256
            or source_record.get("license") != "Apache-2.0"
            or source_record.get("upstream_commit") != COMMIT
        ):
            raise RuntimeError(f"{function} production source contract changed")
        if leaf.get("expected") != {
            "size": size,
            "sha256": digest,
            "alignment": 4,
            "offset": offset,
            "unrelocated_sha256": unrelocated,
        }:
            raise RuntimeError(f"{function} production output pins changed")
        if len(leaf.get("relocations", [])) != relocation_count:
            raise RuntimeError(f"{function} relocation closure changed")
        if (
            patch.get("profiles") != ["apple-clang"]
            or patch.get("runtime_address") != stock_start
            or patch.get("expected_size") != stock_size
            or patch.get("expected_sha256") != stock_sha
            or patch.get("branch") != "b_w"
        ):
            raise RuntimeError(f"{function} production patch changed")

    routes = ROUTES[kind]
    return {
        "candidate": source_path,
        "source_sha256": SOURCE_SHA256,
        "production_routed": True,
        "live_functions": len(routes),
        "compiled_leaf_bytes": sum(route[5] for route in routes.values()),
        "source_owned_bytes_added": 164 if kind == "slave" else 174,
        "stock_bytes_replaced": sum(route[1] for route in routes.values()),
        "hardware_validation": (
            "blocked by unavailable authorized G2/EM9305 pairing evidence"
        ),
    }
