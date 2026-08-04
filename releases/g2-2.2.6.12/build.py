#!/usr/bin/env python3
"""Build SybilSight G2 CFW 2.2.6.12 from its authenticated vendor base.

The release layers the reviewed canvas480 source patch over the complete pinned
g2flash CFW patch set, then changes the embedded SybilSight CFW identity from
2.2.6.10 to 2.2.6.12 and repairs the EvenOTA checksums. It never downloads or
flashes firmware.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import zlib


RELEASE_DIR = Path(__file__).resolve().parent
OPENCFW_ROOT = RELEASE_DIR.parents[1]
DEFINITION_PATH = RELEASE_DIR / "release.json"
CANVAS_DIR = OPENCFW_ROOT / "components" / "apollo_main" / "canvas480"
GENERIC_BUILDER = CANVAS_DIR / "build_stock_canvas480.py"
SOURCE_PATCH = CANVAS_DIR / "g2flash-canvas480.patch"
OLD_VERSION = b"2.2.6.10"
NEW_VERSION = b"2.2.6.12"
PACKAGE_IDENTITY_OFFSET = 48
PACKAGE_IDENTITY_PREFIX = b"s200_v"
EXPECTED_MAIN_VERSION_OFFSETS = (
    4048831,
    4056103,
    4259599,
    4260391,
    4261063,
    4264963,
    4265539,
    4265983,
    4266955,
    4267771,
    4269307,
    4269511,
)
RUNTIME_VERSION_OFFSETS = (
    4265539,  # sid=0x09 settings-reported firmware version
    4266955,  # product-test command 0x24 firmware version
    4267771,  # inter-lens identity copied into sid=0x09's left-version field
)

# Faceclaw was added after the pinned g2flash revision used by this release. Keep
# these stock-code assertions in the release builder so a future source rebase
# cannot silently restore its private settings lease, idle double-tap takeover,
# or native Even AI entry trampoline. Addresses are MRAM addresses from the
# authenticated 2.2.6.10 Apollo image; DELTA maps them into the EvenOTA bundle.
APOLLO_FILE_DELTA = 0x37A179
STOCK_FACECLAW_SITES = (
    (0x49B268, bytes.fromhex("f4 f7 5a ff"), "settings decoder"),
    (0x45C65A, bytes.fromhex("08 f0 68 fa"), "local idle double-tap"),
    (0x45C71A, bytes.fromhex("08 f0 08 fa"), "mirrored idle double-tap"),
    (0x4E1FD2, bytes.fromhex("7f b5 06 00"), "native Even AI entry"),
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_mainapp(image: bytes | bytearray) -> tuple[int, int, int]:
    count = struct.unpack_from("<I", image, 8)[0]
    for index in range(count):
        _, offset, _, _ = struct.unpack_from("<IIII", image, 0x40 + index * 16)
        name = bytes(image[offset + 48:offset + 128]).split(b"\0", 1)[0]
        if name.endswith(b"s200_firmware_ota.bin"):
            payload_size = struct.unpack_from("<I", image, offset + 8)[0]
            return index, offset, payload_size
    raise RuntimeError("main-app component ota/s200_firmware_ota.bin was not found")


def find_occurrences(data: bytes, needle: bytes, start: int, end: int) -> list[int]:
    offsets: list[int] = []
    cursor = start
    while True:
        cursor = data.find(needle, cursor, end)
        if cursor < 0:
            return offsets
        offsets.append(cursor)
        cursor += len(needle)


def verify_faceclaw_removed(stock_image: bytes, release_image: bytes) -> list[dict[str, object]]:
    """Prove the release preserves stock behavior at every Faceclaw hook site."""
    verified: list[dict[str, object]] = []
    for address, expected, label in STOCK_FACECLAW_SITES:
        offset = address - APOLLO_FILE_DELTA
        stock_bytes = stock_image[offset:offset + len(expected)]
        release_bytes = release_image[offset:offset + len(expected)]
        if stock_bytes != expected:
            raise RuntimeError(
                f"authenticated base changed at the Faceclaw {label} site "
                f"{address:#010x}: expected {expected.hex()} got {stock_bytes.hex()}"
            )
        if release_bytes != expected:
            raise RuntimeError(
                f"Faceclaw {label} hook is present in the release at "
                f"{address:#010x}: expected stock {expected.hex()} got {release_bytes.hex()}"
            )
        verified.append({
            "label": label,
            "mram_address": f"0x{address:08x}",
            "bundle_offset": offset,
            "stock_bytes": expected.hex(),
        })
    return verified


def crc32c_msb(data: bytes, table: list[int] = []) -> int:
    if not table:
        for byte in range(256):
            crc = byte << 24
            for _ in range(8):
                crc = (
                    ((crc << 1) ^ 0x1EDC6F41) & 0xFFFFFFFF
                    if crc & 0x80000000
                    else (crc << 1) & 0xFFFFFFFF
                )
            table.append(crc)
    crc = 0
    for byte in data:
        crc = ((crc << 8) & 0xFFFFFFFF) ^ table[((crc >> 24) ^ byte) & 0xFF]
    return crc


def relabel_release(generic_image: bytes, stock_image: bytes) -> tuple[bytes, dict[str, object]]:
    stock_index, stock_offset, stock_size = find_mainapp(stock_image)
    generic_index, component_offset, payload_size = find_mainapp(generic_image)
    if generic_index != stock_index or component_offset != stock_offset:
        raise RuntimeError("the compiled CFW unexpectedly changed the main-app component location")

    payload_start = stock_offset + 128
    stock_payload_end = payload_start + stock_size
    offsets = find_occurrences(stock_image, OLD_VERSION, payload_start, stock_payload_end)
    if tuple(offsets) != EXPECTED_MAIN_VERSION_OFFSETS:
        raise RuntimeError(
            "the authenticated base has an unexpected firmware-version layout: "
            + repr(offsets)
        )

    data = bytearray(generic_image)
    old_package_identity = PACKAGE_IDENTITY_PREFIX + OLD_VERSION
    new_package_identity = PACKAGE_IDENTITY_PREFIX + NEW_VERSION
    if bytes(data[PACKAGE_IDENTITY_OFFSET:PACKAGE_IDENTITY_OFFSET + len(old_package_identity)]) != old_package_identity:
        raise RuntimeError("the authenticated package identity is not the expected stock value")
    data[PACKAGE_IDENTITY_OFFSET:PACKAGE_IDENTITY_OFFSET + len(new_package_identity)] = new_package_identity

    for offset in RUNTIME_VERSION_OFFSETS:
        if bytes(data[offset:offset + len(OLD_VERSION)]) != OLD_VERSION:
            raise RuntimeError(f"compiled CFW changed the version identity at {offset:#x}")
        data[offset:offset + len(NEW_VERSION)] = NEW_VERSION

    payload_end = component_offset + 128 + payload_size
    preamble_crc = zlib.crc32(bytes(data[component_offset + 128 + 8:payload_end])) & 0xFFFFFFFF
    struct.pack_into("<I", data, component_offset + 128 + 4, preamble_crc)
    component_crc = crc32c_msb(bytes(data[component_offset + 128:payload_end]))
    struct.pack_into("<I", data, 0x40 + generic_index * 16 + 12, component_crc)
    struct.pack_into("<I", data, component_offset + 12, component_crc)

    expected_preserved = sorted(set(EXPECTED_MAIN_VERSION_OFFSETS) - set(RUNTIME_VERSION_OFFSETS))
    if find_occurrences(bytes(data), OLD_VERSION, payload_start, stock_payload_end) != expected_preserved:
        raise RuntimeError("the release changed a vendor-provenance version string")
    if find_occurrences(bytes(data), NEW_VERSION, payload_start, stock_payload_end) != list(RUNTIME_VERSION_OFFSETS):
        raise RuntimeError("the release version strings did not land at the reviewed offsets")
    if bytes(data[PACKAGE_IDENTITY_OFFSET:PACKAGE_IDENTITY_OFFSET + len(new_package_identity)]) != new_package_identity:
        raise RuntimeError("the release package identity was not updated")
    return bytes(data), {
        "package_offset": PACKAGE_IDENTITY_OFFSET,
        "runtime_offsets": list(RUNTIME_VERSION_OFFSETS),
        "preserved_vendor_offsets": expected_preserved,
    }


def direct_patch_ops(base: bytes, output: bytes) -> list[dict[str, object]]:
    if len(output) < len(base):
        raise RuntimeError("release output unexpectedly shrank below its vendor base")
    operations: list[dict[str, object]] = []
    cursor = 0
    while cursor < len(base):
        if base[cursor] == output[cursor]:
            cursor += 1
            continue
        start = cursor
        while cursor < len(base) and base[cursor] != output[cursor]:
            cursor += 1
        operations.append({
            "offset": start,
            "old": base[start:cursor].hex(),
            "new": output[start:cursor].hex(),
            "desc": "compiled CFW or 2.2.6.12 release-identity update",
        })
    if len(output) > len(base):
        operations.append({
            "offset": len(base),
            "old": "",
            "new": output[len(base):].hex(),
            "desc": "append compiled SybilSight CFW code to main-app payload",
        })
    return operations


def replay(base: bytes, operations: list[dict[str, object]]) -> bytes:
    data = bytearray(base)
    for operation in operations:
        offset = int(operation["offset"])
        old = bytes.fromhex(str(operation["old"]))
        new = bytes.fromhex(str(operation["new"]))
        if old:
            if bytes(data[offset:offset + len(old)]) != old:
                raise RuntimeError(f"replay mismatch at {offset:#x}")
            data[offset:offset + len(new)] = new
        else:
            if offset != len(data):
                raise RuntimeError(f"append offset {offset:#x} is not current EOF {len(data):#x}")
            data.extend(new)
    return bytes(data)


def output_paths(output: Path, patch_json: Path | None) -> tuple[Path, Path, Path]:
    generated_json = patch_json or output.with_name(output.stem + ".patches.json")
    manifest = output.with_name(output.stem + ".manifest.json")
    return output, generated_json, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--g2flash", required=True, type=Path, help="clean pinned g2flash checkout")
    parser.add_argument("--stock", required=True, type=Path, help="authenticated stock 2.2.6.10 EvenOTA package")
    parser.add_argument("--output", required=True, type=Path, help="2.2.6.12 CFW output")
    parser.add_argument("--patch-json", type=Path, help="generated replayable patch JSON")
    parser.add_argument("--force", action="store_true", help="replace existing output artifacts")
    args = parser.parse_args()

    definition = json.loads(DEFINITION_PATH.read_text(encoding="utf-8"))
    stock = args.stock.expanduser().resolve()
    g2flash = args.g2flash.expanduser().resolve()
    output, patch_json, manifest = output_paths(
        args.output.expanduser().resolve(),
        args.patch_json.expanduser().resolve() if args.patch_json else None,
    )
    expected_base_hash = definition["vendor_base"]["sha256"]
    if not stock.is_file():
        parser.error(f"--stock does not exist: {stock}")
    if sha256(stock) != expected_base_hash:
        parser.error("--stock is not the authenticated 2.2.6.10 vendor base (SHA-256 mismatch)")
    if sha256(SOURCE_PATCH) != definition["source_patch_sha256"]:
        parser.error("the canvas480 source patch does not match the reviewed release pin")
    if len(OLD_VERSION) != len(NEW_VERSION):
        raise RuntimeError("release identity replacement must preserve byte length")

    artifacts = (output, patch_json, manifest)
    if not args.force:
        existing = [str(path) for path in artifacts if path.exists()]
        if existing:
            parser.error("refusing to overwrite existing artifact(s): " + ", ".join(existing))
    for path in artifacts:
        path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="sybilsight-cfw-2.2.6.12-") as temp_name:
        temp = Path(temp_name)
        generic_output = temp / "g2-canvas480.bin"
        generic_patch = temp / "g2-canvas480.patches.json"
        command = [
            sys.executable,
            str(GENERIC_BUILDER),
            "--g2flash", str(g2flash),
            "--stock", str(stock),
            "--output", str(generic_output),
            "--patch-json", str(generic_patch),
        ]
        subprocess.run(command, check=True)
        base_data = stock.read_bytes()
        release_data, version_identity = relabel_release(generic_output.read_bytes(), base_data)
        faceclaw_sites = verify_faceclaw_removed(base_data, release_data)
        capability = definition["capability_marker"].encode("ascii")
        if capability not in release_data:
            raise RuntimeError("compiled release does not contain its declared capability marker")
        if b"wakelease" in release_data:
            raise RuntimeError("removed Faceclaw wakelease capability remains in the release image")

        operations = direct_patch_ops(base_data, release_data)
        if replay(base_data, operations) != release_data:
            raise RuntimeError("generated direct patch does not reproduce the release image")
        output_hash = sha256_bytes(release_data)
        expected_output = definition["expected_output"]
        if len(release_data) != expected_output["size"] or output_hash != expected_output["sha256"]:
            raise RuntimeError(
                "compiled output does not match the reviewed 2.2.6.12 release pin: "
                f"size={len(release_data)} sha256={output_hash}"
            )
        spec = {
            "format": "sybilsight-g2-cfw-patches-v1",
            "release_version": definition["release_version"],
            "vendor_base_version": definition["vendor_base"]["version"],
            "base": stock.name,
            "base_sha256": expected_base_hash,
            "output_sha256": output_hash,
            "patches": operations,
        }
        generated_manifest = {
            "format": "sybilsight-g2-cfw-release-v1",
            "release_name": definition["release_name"],
            "release_version": definition["release_version"],
            "vendor_base_version": definition["vendor_base"]["version"],
            "vendor_base_sha256": expected_base_hash,
            "g2flash_commit": definition["g2flash"]["commit"],
            "source_patch": definition["source_patch"],
            "source_patch_sha256": definition["source_patch_sha256"],
            "capability_marker": definition["capability_marker"],
            "features": definition["features"],
            "virtual_canvas": definition["virtual_canvas"],
            "version_identity": {
                "from": OLD_VERSION.decode("ascii"),
                "to": NEW_VERSION.decode("ascii"),
                **version_identity,
            },
            "faceclaw_removed": {
                "native_even_ai_behavior": "stock",
                "verified_stock_sites": faceclaw_sites,
            },
            "patch_json": patch_json.name,
            "output": output.name,
            "output_size": len(release_data),
            "output_sha256": output_hash,
            "flashed": False,
        }

        output.write_bytes(release_data)
        patch_json.write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
        manifest.write_text(json.dumps(generated_manifest, indent=2) + "\n", encoding="utf-8")

    print(f"built {output}")
    print(f"sha256 {sha256(output)}")
    print("vendor base 2.2.6.10; SybilSight CFW release 2.2.6.12")
    print("not flashed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
