#!/usr/bin/env python3
"""Reproduce the read-only G2 littlefs MSPI/NOR transport audit.

The program reads the authenticated main and boot images, decodes only their
known IAR initialized-data records, and verifies the recovered MSPI device,
timing, pin, XIP, and initialization evidence.  It never opens a device and
has no write or flash-programming path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


class AuditError(RuntimeError):
    """Raised when an authenticated input or recovered invariant drifts."""


@dataclass(frozen=True)
class Image:
    name: str
    path: Path
    file_sha256: str
    load_address: int
    header_size: int
    scatter_record: int
    scatter_handler: int
    scatter_stream: int
    scatter_encoded_field: int
    scatter_destination: int
    scatter_output_size: int
    scatter_output_sha256: str
    serial_config: int
    quad_config: int
    timing_config: int
    timing_table: int
    pin_config_words: dict[int, int]
    spans: dict[str, tuple[int, int, str]]


IMAGES = {
    "main": Image(
        name="main",
        path=(
            ROOT
            / "blobs"
            / "official"
            / "g2-2.2.6.10"
            / "ota_s200_firmware_ota.bin"
        ),
        file_sha256=(
            "36c5b0e499a68ac2493a497bdab9740fd"
            "3e7027730c26a9094eca47268a27863"
        ),
        load_address=0x00438000,
        header_size=32,
        scatter_record=0x0075D3F0,
        scatter_handler=0x0043A11F,
        scatter_stream=0x0079189E,
        scatter_encoded_field=0x54E0,
        scatter_destination=0x20000000,
        scatter_output_size=17752,
        scatter_output_sha256=(
            "df1a1fdf7b2792a7c4ef7a2c5cc6d1423bc7833b556fdfcedb8d6d927fbbb743"
        ),
        serial_config=0x200007F0,
        quad_config=0x20000808,
        timing_config=0x20000820,
        timing_table=0x20000828,
        pin_config_words={
            49: 0x00000582,
            95: 0x00000480,
            96: 0x00000480,
            97: 0x00000C00,
            98: 0x00000C00,
            103: 0x00000C00,
            104: 0x00000C00,
        },
        spans={
            "transaction_lock": (
                0x0046F65E,
                22,
                "b415a20ac2017fe9c1e01927adb4cd950039e5b239244dcc117c0eca69b98dee",
            ),
            "transaction_unlock": (
                0x0046F674,
                22,
                "231e152d1fb28540e77498af6f9387f29908076cd73bc3822bcf45e1db4b60c8",
            ),
            "timing_scan": (
                0x0046F788,
                622,
                "f4de0ae61c913a17a5958b09d1c877f27f58f5735979a1c86b0c50246013aafd",
            ),
            "timing_auto": (
                0x0046F9F6,
                278,
                "4320a41cc7173f24a7a9b9ad43202a0a24667a484a6e1bb24767be1ad120f6c1",
            ),
            "low_level_init": (
                0x0046FB0C,
                812,
                "68c702cca39cea94a9650b5c456229c1fd46b884490bb97f04879c8b56326c21",
            ),
            "public_init": (
                0x0046FE38,
                288,
                "c00b451f0ee38c6693c279d6b982899c0752dc1df32fa4a7727af0a1537f323b",
            ),
            "quad_mode": (
                0x00470E90,
                200,
                "bc0038c5cc8a7fa2934176e6a324614fc266ab81847b42914b61fc1a063965ab",
            ),
            "serial_mode": (
                0x00470F68,
                162,
                "eb87e9d695862f147aa533bfc7fa104081d3c20e49650d637cffb8a963c28491",
            ),
        },
    ),
    "boot": Image(
        name="boot",
        path=(
            ROOT
            / "blobs"
            / "official"
            / "g2-2.2.6.10"
            / "ota_s200_bootloader.bin"
        ),
        file_sha256=(
            "f89a4c4657537cec6bfc572bdb8318866"
            "309b90a5d180c4307680d39824167b5"
        ),
        load_address=0x00410000,
        header_size=0,
        scatter_record=0x00433100,
        scatter_handler=0x00415327,
        scatter_stream=0x004341C0,
        scatter_encoded_field=0x04E2,
        scatter_destination=0x20000000,
        scatter_output_size=1371,
        scatter_output_sha256=(
            "e3bea7ccd46bc324829152b5b5a9069aecce5db243876273084d29bd7d47b843"
        ),
        serial_config=0x2000020C,
        quad_config=0x20000224,
        timing_config=0x2000023C,
        timing_table=0x20000244,
        pin_config_words={
            49: 0x00000582,
            95: 0x00000480,
            96: 0x00000480,
            97: 0x00000C00,
            98: 0x00000C00,
            103: 0x00000C00,
            104: 0x00000C00,
        },
        spans={
            "transaction_lock": (
                0x0041FF08,
                22,
                "02963ef679faf897f9108a5e1526bd79eccabb28b11192d6325dfb4165ca0dc5",
            ),
            "transaction_unlock": (
                0x0041FF1E,
                22,
                "ecb3a585f0f910e6428aa9a722ff0f2a621ca1d195b8fd8b4a9d4f2820f0dddd",
            ),
            "timing_scan": (
                0x00420002,
                440,
                "9618b6beec8ecb55dc3e00510fb11d23951d2c145521c3b418bc445451d6dcb6",
            ),
            "timing_auto": (
                0x004201BA,
                154,
                "a31a24975e2a7de11d5a42b05db91799e7e9656bca2cc22112867efdf9f2b9b7",
            ),
            "low_level_init": (
                0x00420254,
                546,
                "a3c3fab2d311bebbeb0a655aca6ee81a0afaf790008ca5bd11f23b05802bcb94",
            ),
            "public_init": (
                0x00420476,
                180,
                "5be1a86e4e5b4c50b9d8eac9043747caec7abd1ad916fc13ceace39fa5ddb662",
            ),
            "quad_mode": (
                0x00420E8C,
                128,
                "d3eeee3b649bcab6d485d604bb94fe739a753064b80b6918a4d5a9db616b86ef",
            ),
            "serial_mode": (
                0x00420F10,
                90,
                "b73005fad7b0cae8e2f2273bae21ab2877963d2d14534b5afc2918c515c26a13",
            ),
        },
    ),
}


SERIAL_CONFIG = bytes.fromhex(
    "08 03 00 00 03 00 02 00 00 00 00 14 "
    "00 01 01 01 00 00 00 00 00 00 00 00"
)
QUAD_CONFIG = bytes.fromhex(
    "08 03 00 00 6b 00 02 00 10 00 00 14 "
    "00 01 01 01 00 00 00 00 00 00 00 00"
)
DEFAULT_TIMING = bytes.fromhex("01 00 01 06 0e 08")
SERIAL_CONFIG_SHA256 = (
    "afe6fe0edd2efdb10cdc4e1dd9021916709ab9f52077eee6e8bfa3018ae46986"
)
QUAD_CONFIG_SHA256 = (
    "bae2c3ff93a23cefbdb43825a67be78b67a6ab47f090616d16a0a694b0b3d598"
)
DEFAULT_TIMING_SHA256 = (
    "fd3470730e23fba9e5d4c55ba67a15924ea2467786ef8ed836ccb3a86f60cccc"
)
TIMING_TABLE_SHA256 = (
    "a26d40aacdbb0889ec7da60e94af64373ba35610ca63a92b0555b718cdeae182"
)
MAIN_XIP_CONFIG_ADDRESS = 0x00785D00
MAIN_XIP_CONFIG = bytes.fromhex(
    "00 00 00 00 00 00 00 00 00 00 00 80 01 09 00 00"
)
PIN_CONFIG_ADDRESSES = {
    "main": {
        49: 0x20000184,
        95: 0x20000188,
        96: 0x2000018C,
        97: 0x20000190,
        98: 0x20000194,
        103: 0x200001A8,
        104: 0x200001AC,
    },
    "boot": {
        49: 0x2000004C,
        95: 0x20000050,
        96: 0x20000054,
        97: 0x20000058,
        98: 0x2000005C,
        103: 0x20000070,
        104: 0x20000074,
    },
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(image: Image, payload: bytes, address: int, size: int) -> bytes:
    offset = address - image.load_address
    if offset < 0 or offset + size > len(payload):
        raise AuditError(
            f"{image.name}: address 0x{address:08x}+0x{size:x} is outside image"
        )
    return payload[offset : offset + size]


def sram_slice(image: Image, sram: bytes, address: int, size: int) -> bytes:
    offset = address - image.scatter_destination
    if offset < 0 or offset + size > len(sram):
        raise AuditError(
            f"{image.name}: SRAM address 0x{address:08x}+0x{size:x} "
            "is outside decoded initialized data"
        )
    return sram[offset : offset + size]


def decode_iar_record(image: Image, payload: bytes) -> tuple[bytes, dict[str, int]]:
    """Decode the exact byte-run/back-reference format used by the IAR record."""

    record = image_slice(image, payload, image.scatter_record, 16)
    handler_delta = struct.unpack_from("<i", record, 0)[0]
    handler = (image.scatter_record + handler_delta) & 0xFFFFFFFF
    args = image.scatter_record + 4
    stream_delta, encoded_field, destination = struct.unpack_from("<iII", record, 4)
    stream = (args + stream_delta) & 0xFFFFFFFF

    recovered = {
        "record": image.scatter_record,
        "handler": handler,
        "stream": stream,
        "encoded_field": encoded_field,
        "destination": destination,
    }
    expected = {
        "record": image.scatter_record,
        "handler": image.scatter_handler,
        "stream": image.scatter_stream,
        "encoded_field": image.scatter_encoded_field,
        "destination": image.scatter_destination,
    }
    if recovered != expected:
        raise AuditError(
            f"{image.name}: initialized-data record drift: "
            f"{recovered!r} != {expected!r}"
        )

    source = image_slice(
        image,
        payload,
        stream,
        encoded_field >> 1,
    )
    cursor = 0
    output = bytearray()

    while cursor < len(source):
        token = source[cursor]
        cursor += 1

        low = token & 0x03
        if low:
            literal_count = low - 1
        else:
            if cursor >= len(source):
                raise AuditError(f"{image.name}: truncated literal count")
            literal_count = source[cursor] + 2
            cursor += 1

        match_count = token >> 4
        if match_count == 15:
            if cursor >= len(source):
                raise AuditError(f"{image.name}: truncated match count")
            match_count = source[cursor] + 15
            cursor += 1

        literal_end = cursor + literal_count
        if literal_end > len(source):
            raise AuditError(f"{image.name}: truncated literal run")
        output.extend(source[cursor:literal_end])
        cursor = literal_end

        if match_count:
            if cursor >= len(source):
                raise AuditError(f"{image.name}: truncated match offset")
            offset = source[cursor]
            cursor += 1
            high = (token >> 2) & 0x03
            if high == 3:
                if cursor >= len(source):
                    raise AuditError(f"{image.name}: truncated wide match offset")
                high = source[cursor]
                cursor += 1
            offset |= high << 8
            if offset == 0 or offset > len(output):
                raise AuditError(
                    f"{image.name}: invalid back-reference "
                    f"offset {offset} at encoded byte {cursor}"
                )
            for _ in range(match_count + 2):
                output.append(output[-offset])

    decoded = bytes(output)
    if len(decoded) != image.scatter_output_size:
        raise AuditError(
            f"{image.name}: decoded size {len(decoded)} != "
            f"{image.scatter_output_size}"
        )
    if sha256(decoded) != image.scatter_output_sha256:
        raise AuditError(f"{image.name}: decoded initialized-data hash drift")
    return decoded, recovered


def timing_rows(table: bytes) -> list[dict[str, int]]:
    if len(table) != 36 * 6:
        raise AuditError("timing table must contain 36 six-byte rows")
    fields = (
        "tx_neg",
        "rx_neg",
        "rx_cap",
        "tx_dqs_delay",
        "rx_dqs_seed",
        "turnaround_seed",
    )
    return [
        dict(zip(fields, table[offset : offset + 6]))
        for offset in range(0, len(table), 6)
    ]


def run_audit() -> dict[str, Any]:
    image_results: dict[str, Any] = {}
    common_objects: dict[str, bytes] = {}

    for name, image in IMAGES.items():
        file_data = image.path.read_bytes()
        if sha256(file_data) != image.file_sha256:
            raise AuditError(f"{name}: authenticated image hash drift")
        payload = file_data[image.header_size :]
        sram, scatter = decode_iar_record(image, payload)

        serial = sram_slice(image, sram, image.serial_config, 24)
        quad = sram_slice(image, sram, image.quad_config, 24)
        timing = sram_slice(image, sram, image.timing_config, 6)
        table = sram_slice(image, sram, image.timing_table, 36 * 6)
        for label, value, expected, expected_hash in (
            ("serial", serial, SERIAL_CONFIG, SERIAL_CONFIG_SHA256),
            ("quad", quad, QUAD_CONFIG, QUAD_CONFIG_SHA256),
            ("timing", timing, DEFAULT_TIMING, DEFAULT_TIMING_SHA256),
        ):
            if value != expected or sha256(value) != expected_hash:
                raise AuditError(f"{name}: {label} configuration drift")
            if label in common_objects and common_objects[label] != value:
                raise AuditError(f"main/boot {label} configurations differ")
            common_objects[label] = value
        if sha256(table) != TIMING_TABLE_SHA256:
            raise AuditError(f"{name}: timing table drift")
        if "table" in common_objects and common_objects["table"] != table:
            raise AuditError("main/boot timing tables differ")
        common_objects["table"] = table

        pins: dict[str, str] = {}
        for pin, address in PIN_CONFIG_ADDRESSES[name].items():
            word = struct.unpack(
                "<I", sram_slice(image, sram, address, 4)
            )[0]
            if word != image.pin_config_words[pin]:
                raise AuditError(
                    f"{name}: GPIO {pin} config 0x{word:08x} drift"
                )
            pins[str(pin)] = f"0x{word:08x}"

        spans: dict[str, Any] = {}
        for label, (address, size, expected_hash) in image.spans.items():
            body = image_slice(image, payload, address, size)
            actual_hash = sha256(body)
            if actual_hash != expected_hash:
                raise AuditError(f"{name}: {label} body hash drift")
            spans[label] = {
                "address": address,
                "size": size,
                "sha256": actual_hash,
            }

        image_results[name] = {
            "file": str(image.path.relative_to(ROOT)),
            "file_sha256": image.file_sha256,
            "scatter": scatter
            | {
                "decoded_size": len(sram),
                "decoded_sha256": sha256(sram),
            },
            "config_addresses": {
                "serial": image.serial_config,
                "quad": image.quad_config,
                "timing": image.timing_config,
                "timing_table": image.timing_table,
            },
            "pin_config_words": pins,
            "spans": spans,
        }

    main = IMAGES["main"]
    main_payload = main.path.read_bytes()[main.header_size :]
    xip = image_slice(
        main,
        main_payload,
        MAIN_XIP_CONFIG_ADDRESS,
        len(MAIN_XIP_CONFIG),
    )
    if xip != MAIN_XIP_CONFIG:
        raise AuditError("main: XIP configuration drift")

    rows = timing_rows(common_objects["table"])
    expected_rows = [
        {
            "tx_neg": 1,
            "rx_neg": rx_neg,
            "rx_cap": rx_cap,
            "tx_dqs_delay": tx_dqs,
            "rx_dqs_seed": 1,
            "turnaround_seed": 32,
        }
        for rx_neg in range(2)
        for rx_cap in range(2)
        for tx_dqs in range(1, 10)
    ]
    if rows != expected_rows:
        raise AuditError("timing table no longer has the recovered 2x2x9 sweep")

    return {
        "status": "ok",
        "read_only": True,
        "images": image_results,
        "common_device_config": {
            "instance": 1,
            "chip_select": 0,
            "clock_hz": 96_000_000,
            "spi_mode": 0,
            "address_bytes": 4,
            "instruction_bytes": 1,
            "serial_read_instruction": "0x03",
            "quad_template_read_instruction": "0x6b",
            "runtime_quad_read_instruction": "0x6c",
            "write_instruction": "0x02",
            "turnaround_cycles": 8,
            "serial_raw_hex": SERIAL_CONFIG.hex(),
            "quad_raw_hex": QUAD_CONFIG.hex(),
        },
        "fallback_timing": {
            "tx_neg": DEFAULT_TIMING[0],
            "rx_neg": DEFAULT_TIMING[1],
            "rx_cap": DEFAULT_TIMING[2],
            "tx_dqs_delay": DEFAULT_TIMING[3],
            "rx_dqs_delay": DEFAULT_TIMING[4],
            "turnaround": DEFAULT_TIMING[5],
        },
        "timing_sweep": {
            "coarse_rows": rows,
            "fine_rx_dqs_values_per_row": 32,
            "read_id_attempts": 36 * 32,
            "expected_packed_id": "0x002539c2",
        },
        "main_xip": {
            "config_address": MAIN_XIP_CONFIG_ADDRESS,
            "scrambling_start": 0,
            "scrambling_end": 0,
            "aperture_base": 0x80000000,
            "aperture_mode": "read-only",
            "aperture_size": 0x02000000,
            "raw_hex": xip.hex(),
        },
        "littlefs_partition": {
            "nor_offset_start": 0x01400000,
            "nor_offset_end_exclusive": 0x01FC0000,
            "main_xip_start": 0x81400000,
            "main_xip_end_exclusive": 0x81FC0000,
            "bytes_after_partition": 0x00040000,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit complete machine-readable evidence",
    )
    args = parser.parse_args()

    try:
        result = run_audit()
    except (AuditError, FileNotFoundError) as error:
        raise SystemExit(f"littlefs MSPI transport audit: FAIL: {error}") from error

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("littlefs MSPI transport audit: OK")
        print("main/boot initialized MSPI objects: byte-identical")
        print("transport: Apollo510B MSPI1, CE0, 96 MHz, 4-byte addressing")
        print("main XIP: 0x80000000..0x82000000 read-only")
        print("boot XIP: not enabled by recovered NOR initialization")
        print("analysis mode: read-only; no device or flash operation performed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
