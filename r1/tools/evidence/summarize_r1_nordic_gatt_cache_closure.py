#!/usr/bin/env python3
"""Emit twelve exact Nordic Peer Manager GATT-cache functions in the R1 app."""

from __future__ import annotations
import argparse, hashlib, json, struct
from pathlib import Path
from summarize_r1_gomore_call_graph import direct_thumb_branches_to

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x27000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"

NORDIC_GATT_CACHE_CLOSURE_FUNCTIONS = [
    {"entry": 0x6EDCC, "end_exclusive": 0x6EDE2, "size": 22,
     "symbol": "gscm_db_change_notification_done", "source": "components/ble/peer_manager/gatts_cache_manager.c",
     "sha256": "a7d359db2dae3f17b78fedc61683624c461b45676fd7fc523029d27b9c819665", "callsites": (0x66F8E, 0x8AAD6)},
    {"entry": 0x6EDE8, "end_exclusive": 0x6EDF8, "size": 16,
     "symbol": "internal_state_reset", "source": "components/ble/peer_manager/gatts_cache_manager.c",
     "sha256": "6d9137c31381526561a4668016da1c5b536f2403dfdb0405d8d116828bfa25b9", "callsites": (0x806E2,)},
    {"entry": 0x6EDFC, "end_exclusive": 0x6EEA4, "size": 168,
     "symbol": "gscm_local_db_cache_apply", "source": "components/ble/peer_manager/gatts_cache_manager.c",
     "sha256": "e35ffcc97a0d3d83b87b57015f73c6600ccc74f9b0e21303400310a159823231", "callsites": (0x75A26,)},
    {"entry": 0x6F118, "end_exclusive": 0x6F194, "size": 124,
     "symbol": "gscm_service_changed_ind_send", "source": "components/ble/peer_manager/gatts_cache_manager.c",
     "sha256": "898b936e06e3f61e4fd54151b0d7b10b2dc4e670208ff840c4152ed2a869c7a9", "callsites": (0x8AA14,)},
    {"entry": 0x6F0F8, "end_exclusive": 0x6F116, "size": 30,
     "symbol": "gscm_service_changed_ind_needed", "source": "components/ble/peer_manager/gatts_cache_manager.c",
     "sha256": "b9e396556743a83502f42b9e222b39b078b6b47a1acb3813176e9f26ddbed489", "callsites": (0x672F4,)},
    {"entry": 0x75A08, "end_exclusive": 0x75AF2, "size": 234,
     "symbol": "local_db_apply_in_evt", "source": "components/ble/peer_manager/gatt_cache_manager.c",
     "sha256": "44f62890fafd703b3f9a1ea1cc6f1f9f2d7dd519bf4b3c3836b7b47c5d4226c3",
     "callsites": (0x4EC68, 0x66F70, 0x672EC, 0x8AADE)},
    {"entry": 0x75B10, "end_exclusive": 0x75B1A, "size": 10,
     "symbol": "local_db_update", "source": "components/ble/peer_manager/gatt_cache_manager.c",
     "sha256": "7bb77b4d416e8de2b02b0b3ec7ef612681a6f0b048875cd7b98f0d8338947f9b",
     "callsites": (0x66FCC, 0x6740A, 0x75BFC)},
    {"entry": 0x578F4, "end_exclusive": 0x5792A, "size": 54,
     "symbol": "car_update_pending_handle",
     "source": "components/ble/peer_manager/gatt_cache_manager.c",
     "sha256": "152f2a76cb300974f070c7a3280bcc75f434b2f3f4a5381f008d4bc8b3d61d74",
     "callsites": (), "registered_pointer": 0x94ADC,
     "inventory": "manual_provenance_supplement"},
    {"entry": 0x8A928, "end_exclusive": 0x8A934, "size": 12,
     "symbol": "service_changed_pending_flags_check",
     "source": "components/ble/peer_manager/gatt_cache_manager.c",
     "sha256": "c86f657278d80e656b8ced1554328c7990c64531aaae6ca41aecb31337101311",
     "callsites": (0x67152, 0x6743A)},
    {"entry": 0x8A93C, "end_exclusive": 0x8A9EE, "size": 178,
     "symbol": "service_changed_pending_set",
     "source": "components/ble/peer_manager/gatts_cache_manager.c",
     "sha256": "729eafce3fcd21900a06fbc640dd45445caf0cba37eb5a9ce9a490cd10c8a8bf",
     "callsites": (0x6F0EC,), "inventory": "manual_provenance_supplement"},
    {"entry": 0x8AA08, "end_exclusive": 0x8AB4C, "size": 324,
     "symbol": "service_changed_send_in_evt",
     "source": "components/ble/peer_manager/gatt_cache_manager.c",
     "sha256": "a9602bc3393b4bca50ca6d913989de429684b997dbeff4b097fd45bc93e2b6b2",
     "callsites": (0x890E4,), "inventory": "manual_provenance_supplement"},
    {"entry": 0x91084, "end_exclusive": 0x9110A, "size": 134,
     "symbol": "store_car_value", "source": "components/ble/peer_manager/gatt_cache_manager.c",
     "sha256": "1d25f5c1ba03279bbe7c7f1d784e6c28976db1a6c0331a9beaf38f7151f8d82f", "callsites": (0x6713C,)},
    {"entry": 0x94AB0, "end_exclusive": 0x94AD2, "size": 34,
     "symbol": "update_pending_flags_check", "source": "components/ble/peer_manager/gatt_cache_manager.c",
     "sha256": "de592f2ed0d9a3f81132fcb30bff830ba454a4a9e3921d4c446e49c38cd14146",
     "callsites": (0x66FD0, 0x67310, 0x67456)},
]

def summarize(path: Path) -> dict[str, object]:
    image = path.read_bytes(); digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256: raise ValueError(f"unexpected application image SHA-256: {digest}")
    out = []
    for item in NORDIC_GATT_CACHE_CLOSURE_FUNCTIONS:
        entry, end = item["entry"], item["end_exclusive"]
        body = image[entry-LOAD_BASE:end-LOAD_BASE]
        calls = tuple(a for a, _ in direct_thumb_branches_to(image, LOAD_BASE, entry))
        pointer_ok = True
        if "registered_pointer" in item:
            pointer = int(item["registered_pointer"])
            pointer_ok = struct.unpack_from("<I", image, pointer - LOAD_BASE)[0] == entry + 1
        if len(body) != item["size"] or hashlib.sha256(body).hexdigest() != item["sha256"] or calls != item["callsites"] or not pointer_ok:
            raise ValueError(f"Nordic GATT-cache closure changed at 0x{entry:08x}")
        out.append({**item, "entry": f"0x{entry:08x}", "end_exclusive": f"0x{end:08x}",
                    "callsites": [f"0x{x:08x}" for x in calls]})
    return {"analysis": "Nordic Peer Manager GATT-cache closure", "image_sha256": digest,
            "function_count": len(out), "function_bytes": sum(x["size"] for x in out), "functions": out,
            "provider": {"family": "nordic_nrf5_sdk_17_1_0", "disposition": "use_nordic_sdk",
                         "local_reimplementation_authorized": False}}

if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(p.parse_args().image), indent=2, sort_keys=True))
