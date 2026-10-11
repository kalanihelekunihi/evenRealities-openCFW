#!/usr/bin/env python3
"""Match all 26 SDK Grus clock-module rows to pinned image-B data."""
import hashlib
import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
STOCK = ROOT / "g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage2.bin"
SDK = ROOT / "third-party/upstream/nationalchip-lvp-kws/arch/soc/grus/include/clk_priv.h"
ENUM = ROOT / "third-party/upstream/nationalchip-lvp-kws/include/driver/gx_clock/gx_clock_v2.h"


def main():
    image = STOCK.read_bytes()
    assert hashlib.sha256(image).hexdigest() == "d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941"
    enums = dict((name, int(value)) for name, value in re.findall(
        r"(CLOCK_MODULE_\w+)\s*=\s*(\d+)", ENUM.read_text()))
    table = SDK.read_text().split("static GX_CLOCK_MODULE_PARAM gx_clock_param_table[] = {", 1)[1].split("};", 1)[0]
    pattern = re.compile(r"\{\s*(CLOCK_MODULE_\w+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(gx_clock_div_table\s*\+\s*\d+|NULL)\s*,\s*(gx_clock_dto_table\s*\+\s*\d+|NULL)\s*\}")
    sdk_rows = pattern.findall(table)
    assert len(sdk_rows) == 26, len(sdk_rows)
    result = []
    base = 0x1001699c - 0x10003000
    for i, (name, high, all_gate, clock, div, dto) in enumerate(sdk_rows):
        actual = image[base + i * 16:base + (i + 1) * 16]
        mod = struct.unpack_from("<I", actual)[0]
        offsets = list(actual[4:7])
        div_addr, dto_addr = struct.unpack_from("<II", actual, 8)
        expected_div = 0 if div == "NULL" else 0x20016b40 + 4 * int(div.rsplit("+", 1)[1])
        expected_dto = 0 if dto == "NULL" else 0x20016b3c + int(dto.rsplit("+", 1)[1])
        expected = (enums[name], [int(high) & 255, int(all_gate) & 255, int(clock) & 255],
                    expected_div, expected_dto)
        observed = (mod, offsets, div_addr, dto_addr)
        result.append({"row": i, "module": name, "match": observed == expected})
    receipt = {"stock_image_sha256": hashlib.sha256(image).hexdigest(),
               "sdk_header_sha256": hashlib.sha256(SDK.read_bytes()).hexdigest(),
               "sdk_enum_sha256": hashlib.sha256(ENUM.read_bytes()).hexdigest(),
               "rows": result, "matching_rows": sum(r["match"] for r in result),
               "total_rows": len(result),
               "scope": "source table fields/pointers versus stock initialized data; no final relocation or hardware trace proof"}
    (HERE / "clock-table-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"{receipt['matching_rows']}/{receipt['total_rows']} SDK clock rows match")
    if receipt["matching_rows"] != receipt["total_rows"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
