#!/usr/bin/env python3
"""Pin the exact Nordic BLE advertising module cluster in the R1 application."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x27000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"

NORDIC_ADVERTISING_FUNCTIONS = (
    {
        "entry": 0x51710,
        "end_exclusive": 0x51716,
        "size": 6,
        "extent_size": 6,
        "symbol": "ble_advertising_conn_cfg_tag_set",
        "source": "components/ble/ble_advertising/ble_advertising.c",
        "extent_sha256": "fa3e2d00b9b20169cfe840228d491dd26092eb80dec02ab831785d0b4b4af13d",
        "callsites": (0x48AB4,),
    },
    {
        "entry": 0x51716,
        "end_exclusive": 0x517FE,
        "size": 232,
        "extent_size": 232,
        "symbol": "ble_advertising_init",
        "source": "components/ble/ble_advertising/ble_advertising.c",
        "extent_sha256": "6b9e719a23c0bc7a3b71b17fe7eceabd6ce098eece3e3d18be9c86d49c4eff08",
        "callsites": (0x48AA4,),
    },
    {
        "entry": 0x517FE,
        "end_exclusive": 0x51806,
        "size": 8,
        "extent_size": 8,
        "symbol": "ble_advertising_modes_config_set",
        "source": "components/ble/ble_advertising/ble_advertising.c",
        "extent_sha256": "20b25156b24161de89c9fd22c2032854b61e5ccac913c5a7ab1f2c8e8be07e9e",
        "callsites": (0x523AE,),
    },
    {
        "entry": 0x51806,
        "end_exclusive": 0x51870,
        "size": 106,
        "extent_size": 106,
        "symbol": "ble_advertising_on_ble_evt",
        "source": "components/ble/ble_advertising/ble_advertising.c",
        "extent_sha256": "12e46ab4b53d2b029fe4dcf9322583ed61354924652b09ba33a6f488ca2f967a",
        "callsites": (),
    },
    {
        "entry": 0x51870,
        "end_exclusive": 0x51AA0,
        "size": 554,
        "extent_size": 560,
        "symbol": "ble_advertising_start",
        "source": "components/ble/ble_advertising/ble_advertising.c",
        "body_sha256": "6e76f1577ea6f6dcb1e42015e5d26835b78f9fa9efc8268c38bab8276a70e6e7",
        "extent_sha256": "f25cc50c7ea0c022fe253571d9e9a0eea8885c5ceb06bfaeb60d4bc027b76a2c",
        "callsites": (0x4C852, 0x4D12C, 0x51832, 0x53284),
        "inline_data": {
            "entry": 0x519A2,
            "end_exclusive": 0x519A8,
            "size": 6,
            "sha256": "ce1673f6fe175339d6d2959f905c3a5d81ac80f17056048bbd0f372114fe8bfd",
            "role": "Thumb TBB advertising-mode jump table",
        },
    },
    {
        "entry": 0x64F1A,
        "end_exclusive": 0x64F42,
        "size": 40,
        "extent_size": 40,
        "symbol": "flags_set",
        "source": "components/ble/ble_advertising/ble_advertising.c",
        "extent_sha256": "b6dfd509fc9baa3b3fc82bfaf5755eb2827453428797a0b771a45da1c2a2ffcb",
        "callsites": (0x51A12, 0x51A52),
    },
    {
        "entry": 0x7F0C8,
        "end_exclusive": 0x7F0DE,
        "size": 22,
        "extent_size": 22,
        "symbol": "phy_is_valid",
        "source": "components/ble/ble_advertising/ble_advertising.c",
        "extent_sha256": "6b70e2128c7717798503ef943a89265235996ea6550cacb66c5dfcabbebb4676",
        "callsites": (0x51948, 0x51974),
    },
    {
        "entry": 0x94DD8,
        "end_exclusive": 0x94DF0,
        "size": 24,
        "extent_size": 24,
        "symbol": "use_whitelist",
        "source": "components/ble/ble_advertising/ble_advertising.c",
        "extent_sha256": "9e1e2214acc2b0a96161cc7371ede0e26d80202506715e37091664245dcaf8c3",
        "callsites": (0x51A04, 0x51A44),
    },
)


def flash_bytes(image: bytes, address: int, length: int) -> bytes:
    offset = address - LOAD_BASE
    if offset < 0 or offset + length > len(image):
        raise ValueError(f"address outside image: 0x{address:08x}")
    return image[offset:offset + length]


def summarize(path: Path) -> dict[str, object]:
    image = path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected application image SHA-256: {digest}")

    output: list[dict[str, object]] = []
    for function in NORDIC_ADVERTISING_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        extent = flash_bytes(image, entry, end - entry)
        calls = tuple(address for address, _ in direct_thumb_branches_to(image, LOAD_BASE, entry))
        if len(extent) != function["extent_size"] or \
                hashlib.sha256(extent).hexdigest() != function["extent_sha256"] or \
                calls != function["callsites"]:
            raise ValueError(f"Nordic advertising function changed at 0x{entry:08x}")

        item = dict(function)
        if "inline_data" in function:
            inline = dict(function["inline_data"])
            inline_entry = int(inline["entry"])
            inline_end = int(inline["end_exclusive"])
            inline_bytes = flash_bytes(image, inline_entry, inline_end - inline_entry)
            if hashlib.sha256(inline_bytes).hexdigest() != inline["sha256"]:
                raise ValueError("Nordic advertising inline jump table changed")
            body = (flash_bytes(image, entry, inline_entry - entry) +
                    flash_bytes(image, inline_end, end - inline_end))
            if len(body) != function["size"] or \
                    hashlib.sha256(body).hexdigest() != function["body_sha256"]:
                raise ValueError("Nordic advertising Ghidra body changed")
            inline.update(entry=f"0x{inline_entry:08x}",
                          end_exclusive=f"0x{inline_end:08x}")
            item["inline_data"] = inline

        item.update(
            entry=f"0x{entry:08x}",
            end_exclusive=f"0x{end:08x}",
            callsites=[f"0x{address:08x}" for address in calls],
        )
        output.append(item)

    return {
        "analysis": "Nordic SDK 17.1.0 BLE advertising module closure",
        "image_sha256": digest,
        "function_count": len(output),
        "function_bytes": sum(int(item["size"]) for item in NORDIC_ADVERTISING_FUNCTIONS),
        "extent_bytes": sum(int(item["extent_size"]) for item in NORDIC_ADVERTISING_FUNCTIONS),
        "functions": output,
        "provider": {
            "family": "nordic_nrf5_sdk_17_1_0",
            "source": "components/ble/ble_advertising/ble_advertising.c",
            "local_reimplementation_authorized": False,
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))
