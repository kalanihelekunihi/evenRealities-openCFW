#!/usr/bin/env python3
"""Pin the exact Nordic unbonded buttonless-DFU cluster in the R1 application."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x27000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"

BLE_DFU_SOURCE = "components/ble/ble_services/ble_dfu/ble_dfu.c"
BLE_DFU_UNBONDED_SOURCE = \
    "components/ble/ble_services/ble_dfu/ble_dfu_unbonded.c"

NORDIC_BUTTONLESS_DFU_FUNCTIONS = (
    {
        "entry": 0x52018,
        "size": 162,
        "symbol": "ble_dfu_buttonless_async_svci_init",
        "source": BLE_DFU_UNBONDED_SOURCE,
        "segments": ((0x52018, 0x52038), (0x7876C, 0x787EE)),
        "sha256": "8d0e7bd5c4979c76ad9a2a6a995a60655868dfe568522ce96bedaa07d8d68892",
        "callsites": (0x75F8C,),
    },
    {
        "entry": 0x5203C,
        "size": 14,
        "symbol": "ble_dfu_buttonless_backend_init",
        "source": BLE_DFU_UNBONDED_SOURCE,
        "segments": ((0x5203C, 0x5204A),),
        "sha256": "d1ae97b0f886c52aacc5b46d70056ae09a51a56361f52a3effd920e6546f4c17",
        "callsites": (0x52112,),
    },
    {
        "entry": 0x52050,
        "size": 40,
        "symbol": "ble_dfu_buttonless_bootloader_start_finalize",
        "source": BLE_DFU_SOURCE,
        "segments": ((0x52050, 0x52078),),
        "sha256": "4664b0bf23c87e88eaa0e743cecc8fef14a88241a3148941443eff0726560b5b",
        "callsites": (0x5208C,),
        "inventory": "manual_provenance_supplement",
    },
    {
        "entry": 0x5207C,
        "size": 60,
        "symbol": "ble_dfu_buttonless_bootloader_start_prepare",
        "source": BLE_DFU_UNBONDED_SOURCE,
        "additional_source": BLE_DFU_SOURCE,
        "segments": ((0x5207C, 0x52090), (0x52050, 0x52078)),
        "sha256": "700b470a739cf8d1337ddfc5270e566e9fa570ad963fe6b512bdd8a179796f60",
        "callsites": (0x52182,),
        "tail_symbol": "ble_dfu_buttonless_bootloader_start_finalize",
    },
    {
        "entry": 0x52094,
        "size": 80,
        "symbol": "ble_dfu_buttonless_char_add",
        "source": BLE_DFU_UNBONDED_SOURCE,
        "segments": ((0x52094, 0x520E4),),
        "sha256": "c7fdf9bc96ae4f458132e5ea6925c6ed2613801b9cd6fe6bc4424f439242fa67",
        "callsites": (0x52140,),
    },
    {
        "entry": 0x520E4,
        "size": 98,
        "symbol": "ble_dfu_buttonless_init",
        "source": BLE_DFU_SOURCE,
        "segments": ((0x520E4, 0x52146),),
        "sha256": "b22f667515646b95e5ab245b2ae063b917a1f92901ec73dd73ee32192a4480e3",
        "callsites": (0x4C934,),
    },
    {
        "entry": 0x52154,
        "size": 128,
        "symbol": "ble_dfu_buttonless_on_ble_evt",
        "source": BLE_DFU_SOURCE,
        "segments": ((0x52154, 0x521D4),),
        "sha256": "5ddc4b4f99fdbe120c05f468aa2c5ddc22f970672e6dc348f69f1dae310423f8",
        "callsites": (),
        "inventory": "manual_provenance_supplement",
    },
    {
        "entry": 0x521D8,
        "size": 150,
        "symbol": "ble_dfu_buttonless_on_ctrl_pt_write",
        "source": BLE_DFU_UNBONDED_SOURCE,
        "segments": ((0x521D8, 0x5226E),),
        "sha256": "f9eb76118683e5907b1552865294dca624b334075b40307123e48da9bdc8fa08",
        "callsites": (0x7CE24,),
    },
    {
        "entry": 0x52278,
        "size": 88,
        "symbol": "ble_dfu_buttonless_on_sys_evt",
        "source": BLE_DFU_UNBONDED_SOURCE,
        "segments": ((0x52278, 0x522D0),),
        "sha256": "52cf952308578630fb15285ae085bdf271b38a6ff46cccbd7a5705222c9e4cf7",
        "callsites": (),
    },
    {
        "entry": 0x522D8,
        "size": 78,
        "symbol": "ble_dfu_buttonless_resp_send",
        "source": BLE_DFU_SOURCE,
        "segments": ((0x522D8, 0x52326),),
        "sha256": "645ea03f11602b94f1a7e0934ce339a49a27e69b31bd859727710ba8b2abf48f",
        "callsites": (0x521F2, 0x52218, 0x5222E, 0x522A0, 0x522BE),
    },
    {
        "entry": 0x7CDC8,
        "size": 100,
        "symbol": "on_ctrlpt_write",
        "source": BLE_DFU_SOURCE,
        "segments": ((0x7CDC8, 0x7CE2C),),
        "sha256": "cd658fe13c029d9a2379aaec192cc76ccb2e8e7dbc3684f02bb3df7e13bd4326",
        "callsites": (0x521D0,),
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
    for function in NORDIC_BUTTONLESS_DFU_FUNCTIONS:
        entry = int(function["entry"])
        segments = tuple(
            (int(start), int(end)) for start, end in function["segments"]
        )
        body = b"".join(
            flash_bytes(image, start, end - start) for start, end in segments
        )
        if len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise ValueError(f"Nordic buttonless-DFU function changed at 0x{entry:08x}")

        scanned_calls = tuple(
            address for address, _ in direct_thumb_branches_to(image, LOAD_BASE, entry)
        )
        for callsite in function["callsites"]:
            if callsite not in scanned_calls:
                raise ValueError(
                    f"Nordic buttonless-DFU caller changed at 0x{callsite:08x}"
                )

        item = dict(function)
        item.update(
            entry=f"0x{entry:08x}",
            segments=[
                {
                    "entry": f"0x{start:08x}",
                    "end_exclusive": f"0x{end:08x}",
                    "size": end - start,
                }
                for start, end in segments
            ],
            callsites=[f"0x{address:08x}" for address in function["callsites"]],
        )
        output.append(item)

    return {
        "analysis": "Nordic SDK 17.1.0 unbonded buttonless-DFU closure",
        "image_sha256": digest,
        "function_count": len(output),
        "function_bytes": sum(
            int(item["size"]) for item in NORDIC_BUTTONLESS_DFU_FUNCTIONS
        ),
        "ghidra_function_count": sum(
            item.get("inventory") != "manual_provenance_supplement"
            for item in NORDIC_BUTTONLESS_DFU_FUNCTIONS
        ),
        "ghidra_function_bytes": sum(
            int(item["size"])
            for item in NORDIC_BUTTONLESS_DFU_FUNCTIONS
            if item.get("inventory") != "manual_provenance_supplement"
        ),
        "manual_supplement_count": sum(
            item.get("inventory") == "manual_provenance_supplement"
            for item in NORDIC_BUTTONLESS_DFU_FUNCTIONS
        ),
        "functions": output,
        "provider": {
            "family": "nordic_nrf5_sdk_17_1_0",
            "variant": "NRF_DFU_BLE_BUTTONLESS_SUPPORTS_BONDS=0",
            "sources": (BLE_DFU_SOURCE, BLE_DFU_UNBONDED_SOURCE),
            "local_reimplementation_authorized": False,
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))
