#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPECTED = {
    "LICENSE.md": (562, "682ae5978019e4ee9d439b300efb125525b2e4cc4181ebd1e676dd60dc69d7cd", "5fe50d5491f1166292380f46c8beae44ca83cadb"),
    "app_disc.c": (30467, "3fd6e00fe14e903441c151b990f045ad3790a796cb2f19067e45cb8189d654c9", "c9bc68c9e82d07b6d5887d33aa9d02a40f8d885b"),
    "app_main.c": (13634, "40226fef44b937e45c5a0030fc64af502710a4f8eb7d4eb758d2188516b9da35", "8afd083f2798ba4c2fcf559ed92f0c2a325315ef"),
    "app_master.c": (30265, "712c0cde3cb0591df48a0204d17d07accbced73656822f9ad48eee384f176a9b", "0bb507e74107a7f959034f48e1d5ce2e93c3a052"),
    "app_master_leg.c": (3937, "d09e4a15cedd3f3983a04c7af6b566cca863ebe52f23c7be4f82abcb9f616563", "2d6d01f16ebae3d7ae332bc26078e06274eef1f4"),
    "app_server.c": (8689, "24454f150cd4f988e1a6032eea243c0729cd25f4136364a3d1240063aaec778c", "ead2a1da76b047b84e27921d82bbf1519d44d8d5"),
    "app_slave.c": (55381, "075a8ce18bf5bd04e27d7f97f5dcde02055e1a0b0e4eedfd086653e0b370652f", "71cae1f71385f72a7f46f9ed555e965cffbf586d"),
    "app_slave_leg.c": (12338, "6d3ea912468ef488f181fbd7f453e35e2cb7d604b27981d7cb1af1c549e259c4", "6a0fe8d6f8ce4a4cba6feaae70eed6aa52d6e54a"),
    "common/app_db.c": (33371, "2b7d3b4d35adf9783966215134c3a62cc9ae1016204f150c0a3a9bf9f58ee646", "15dc1a189a7715649588ecfdd4b8faf06a89616f"),
    "common/app_ui.c": (9951, "d02a478cf431b8a5693d5a833659d106190166609b6b805d9f6d766342f657ec", "de657c3e82fa6d806bb00cebb5b6a63f928d4588"),
}
EXPECTED_HARDWARE_POLICY = {
    "hardware_validation": "blocked by unavailable physical evidence",
    "hardware_blocker": (
        "Hardware validation is intentionally blocked by unavailable physical evidence and "
        "remains required for future qualification."
    ),
}


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git_blob(raw: bytes) -> str:
    header = f"blob {len(raw)}\0".encode()
    return hashlib.sha1(header + raw, usedforsecurity=False).hexdigest()


def _verify_hardware_policy(provenance: dict[str, object]) -> None:
    boundary = provenance["g2_boundary"]
    assert isinstance(boundary, dict)
    assert {
        key: boundary.get(key) for key in EXPECTED_HARDWARE_POLICY
    } == EXPECTED_HARDWARE_POLICY


def verify() -> dict[str, object]:
    provenance = json.loads((HERE / "PROVENANCE.json").read_text())
    upstream = provenance["upstream"]
    _verify_hardware_policy(provenance)
    assert upstream["selected_commit"] == "de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f"
    assert upstream["selected_tree"] == "3a06dca6e2222fdc2058e9587596e22325a6f024"
    assert upstream["historical_g2_generating_commit"] is None
    records = {item["path"]: item for item in provenance["files"]}
    assert set(records) == set(EXPECTED)
    for name, expected in EXPECTED.items():
        raw = (HERE / name).read_bytes()
        assert (len(raw), sha256(raw), git_blob(raw)) == expected
        record = records[name]
        assert (record["size"], record["sha256"], record["git_blob_sha1"]) == expected

    required_tokens = {
        "app_main.c": ("appExtConnCb_t appExtConnCb[DM_CONN_MAX]",),
        "app_master.c": ("AppDbNewRecord(DmConnPeerAddrType(connId), DmConnPeerAddr(connId), TRUE)",),
        "app_slave.c": ("AppDbNewRecord(DmConnPeerAddrType(pCb->connId), DmConnPeerAddr(pCb->connId), FALSE)",),
        "app_slave_leg.c": ("appSlaveCb.advState[DM_ADV_HANDLE_DEFAULT] = APP_ADV_STATE1",),
        "common/app_db.c": ("#ifdef AM_BLE_USE_NVM", "AppDbNewRecord(uint8_t addrType, uint8_t *pAddr, bool_t master_role)"),
    }
    for name, tokens in required_tokens.items():
        source = (HERE / name).read_text()
        assert all(token in source for token in tokens)

    allowed = set(EXPECTED) | {"PROVENANCE.json", "README.openCFW.md", "verify_snapshot.py"}
    present = {str(path.relative_to(HERE)) for path in HERE.rglob("*") if path.is_file()}
    assert present == allowed
    return {
        "files": len(EXPECTED),
        "source_files": 9,
        "selected_release": "2.5.1",
        "selected_commit": upstream["selected_commit"],
        "historical_g2_generating_commit": None,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
    print("AmbiqSuite Cordio application-framework snapshot: PASS")
