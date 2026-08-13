#!/usr/bin/env python3
"""Emit the exact stock software-TWI provider-function census.

This parser is static and read-only. It does not expose a live GPIO/I2C sender
and intentionally makes no source-ownership claim for the recovered engine.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x00027000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"


def _family(role: str, extents: list[tuple[int, int, str]]) -> list[dict[str, object]]:
    return [
        {
            "bus_index": index,
            "role": role,
            "entry": entry,
            "end_exclusive": end,
            "size": end - entry,
            "sha256": digest,
            "symbol": f"software_twi_i2c_{index}_{role}_provider_candidate",
        }
        for index, (entry, end, digest) in zip(range(2, 6), extents)
    ]


SOFTWARE_TWI_FUNCTIONS = sum((
    _family("open", [
        (0x00055330, 0x0005535C, "ae987b72c8e3f883ab25cb0bee73dd4e94768cdd4fdb96f5407d9273928a68a0"),
        (0x00055360, 0x0005538C, "ae987b72c8e3f883ab25cb0bee73dd4e94768cdd4fdb96f5407d9273928a68a0"),
        (0x00055390, 0x000553DE, "ecad3b4aa8ffd9c91a9c0f4e401e51f2cdf7f5281315c8bba14dd945b452bdbb"),
        (0x000553E4, 0x00055410, "ae987b72c8e3f883ab25cb0bee73dd4e94768cdd4fdb96f5407d9273928a68a0"),
    ]),
    _family("read_adapter", [
        (0x0005547C, 0x000554AA, "f5545c4edfcf8c42edaab6e4f589cba39e5ce88568ddd10a910b52a37ebe24c2"),
        (0x000554B0, 0x000554DE, "039e872f1e46ccf738051a01ae65a63a69e55b86c7e803869c39e9375fbeec3b"),
        (0x000554E4, 0x00055512, "fdc0312b5d41c0c6526ea7572e6c5b14cfc3fd157c08f537d9263aaff0f5cda8"),
        (0x00055518, 0x00055542, "7298b0974354be6ba7e7b66c2a00c3efc691c45184ca88aed9cccdc5bf8e7cf4"),
    ]),
    _family("read_byte", [
        (0x00055548, 0x000555F4, "ed476b7e4b80725d5a2dce742b3d44fb7d7d61cff69c63b123a17b894e013037"),
        (0x000555F4, 0x000556A0, "ed476b7e4b80725d5a2dce742b3d44fb7d7d61cff69c63b123a17b894e013037"),
        (0x000556A0, 0x0005574C, "ed476b7e4b80725d5a2dce742b3d44fb7d7d61cff69c63b123a17b894e013037"),
        (0x0005574C, 0x000557F8, "ed476b7e4b80725d5a2dce742b3d44fb7d7d61cff69c63b123a17b894e013037"),
    ]),
    _family("read_transaction", [
        (0x000557F8, 0x00055878, "1ab8cc64b1d3c323e0ea9852a5b8e8e3aeb6864362da35328c6b42a41946864a"),
        (0x00055878, 0x000558F8, "6857c5f945a53df2f49b644d10c52ea6dd376de85917ea0749a3a392636da048"),
        (0x000558F8, 0x00055988, "d288d96802baa478f375c8f7a7950df3273a796e2ecc67cdaa00c02b132b85a6"),
        (0x00055988, 0x00055A18, "c76cbe10cb7f3f1f2087a477476a975e16082b91994e0f5511ca88dbdb97026c"),
    ]),
    _family("start", [
        (0x00055A18, 0x00055A56, "21f539c364445a67e8500adfb1af50ea549030d38965c46761ef2411f8f74588"),
        (0x00055A56, 0x00055A94, "21f539c364445a67e8500adfb1af50ea549030d38965c46761ef2411f8f74588"),
        (0x00055A94, 0x00055AD2, "21f539c364445a67e8500adfb1af50ea549030d38965c46761ef2411f8f74588"),
        (0x00055AD2, 0x00055B10, "21f539c364445a67e8500adfb1af50ea549030d38965c46761ef2411f8f74588"),
    ]),
    _family("stop", [
        (0x00055B10, 0x00055B3C, "1131625b0644f8ecf495acc4c39d8dc47b45fdc069f3f9a702f33cd7967c4b31"),
        (0x00055B3C, 0x00055B68, "1131625b0644f8ecf495acc4c39d8dc47b45fdc069f3f9a702f33cd7967c4b31"),
        (0x00055B68, 0x00055B94, "1131625b0644f8ecf495acc4c39d8dc47b45fdc069f3f9a702f33cd7967c4b31"),
        (0x00055B94, 0x00055BC0, "1131625b0644f8ecf495acc4c39d8dc47b45fdc069f3f9a702f33cd7967c4b31"),
    ]),
    _family("ack", [
        (0x00055BC0, 0x00055C08, "938d09350b68849b9f2baaeef5e6f2ba5a280aacf491e0e322ad2ed20b0bef25"),
        (0x00055C08, 0x00055C50, "938d09350b68849b9f2baaeef5e6f2ba5a280aacf491e0e322ad2ed20b0bef25"),
        (0x00055C50, 0x00055C98, "938d09350b68849b9f2baaeef5e6f2ba5a280aacf491e0e322ad2ed20b0bef25"),
        (0x00055C98, 0x00055CE0, "938d09350b68849b9f2baaeef5e6f2ba5a280aacf491e0e322ad2ed20b0bef25"),
    ]),
    _family("write_adapter", [
        (0x00055DBC, 0x00055E3C, "a45a5f1f82b44739047a8a36252d43b753ed894eff803f08f4c0a68da71d36ec"),
        (0x00055E40, 0x00055EC0, "99642bdb5c49f81b733303f7a3bd5ce21f1b9fbd5db2706249174e5099ad363b"),
        (0x00055EC4, 0x00055F58, "e00749fc10866a86d9d280be1de3ccbad48d56b9853231a61d1b24644cf39303"),
        (0x00055F5C, 0x00055F9E, "5a5ba24a361f23ae01e7c85cbf1d438bbf3d9dd532e387047d5e932a5dbbfdfd"),
    ]),
    _family("write_byte", [
        (0x00055FA4, 0x00055FF2, "4eff68ec24a1ff28a472d99b7d97ae574a6d4bb2093ad9ab275cf58a44da1c47"),
        (0x00055FF2, 0x00056040, "4eff68ec24a1ff28a472d99b7d97ae574a6d4bb2093ad9ab275cf58a44da1c47"),
        (0x00056040, 0x0005608E, "4eff68ec24a1ff28a472d99b7d97ae574a6d4bb2093ad9ab275cf58a44da1c47"),
        (0x0005608E, 0x000560DC, "4eff68ec24a1ff28a472d99b7d97ae574a6d4bb2093ad9ab275cf58a44da1c47"),
    ]),
    _family("write_transaction", [
        (0x000560DC, 0x0005613E, "c076fc65c0072c70a0fec809e8dff1ab4ca78e3bd9d61a0248887a0c3cb19631"),
        (0x0005613E, 0x000561A0, "1bf6956f2aba753ef25da7321617b1ff4cad1a7c638d878bf3a99bb87310b501"),
        (0x000561A0, 0x00056202, "436d13d1457c56184758375e87de4c3d5783fc4c905193439beed36724404ddb"),
        (0x00056202, 0x00056274, "63bc30ff257bfaa10a9ce3bb20a3043f34edaadaa668f70e2ee2e8e2b3261c24"),
    ]),
), [])


def summarize(image_path: Path) -> dict[str, object]:
    image = image_path.read_bytes()
    image_digest = hashlib.sha256(image).hexdigest()
    if image_digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected application image SHA-256: {image_digest}")

    functions = []
    for function in SOFTWARE_TWI_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[entry - LOAD_BASE:end - LOAD_BASE]
        digest = hashlib.sha256(body).hexdigest()
        if len(body) != function["size"] or digest != function["sha256"]:
            raise ValueError(f"software-TWI function changed at 0x{entry:08x}")
        functions.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
        })

    return {
        "analysis": "R1 software-TWI provider boundary census",
        "image": str(image_path),
        "image_sha256": image_digest,
        "load_base": f"0x{LOAD_BASE:08x}",
        "function_count": len(functions),
        "function_bytes": sum(int(item["size"]) for item in functions),
        "bus_indices": [2, 3, 4, 5],
        "roles_per_bus": sorted({str(item["role"]) for item in functions}),
        "source_lineage": {
            "status": "unidentified_provider_candidate",
            "local_implementation_authorized": False,
            "reason": (
                "Wire semantics and compiler-instantiated family structure are recovered, "
                "but no exact attributable source, version, or license is established."
            ),
        },
        "functions": functions,
        "safety": {
            "static_parser_only": True,
            "live_gpio_or_i2c_access": False,
            "wire_sender_exposed": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    args = parser.parse_args()
    print(json.dumps(summarize(args.image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
