#!/usr/bin/env python3
"""Synchronize reviewed bootloader runtime production tranches.

This tool only reconciles local JSON ownership metadata with the already built
bootloader provider contract.  It never assembles a signed package and never
communicates with hardware.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
CONTRACT = (
    ROOT / "components" / "bootloader" / "core_overlay" / "build"
    / "provider-contract.json"
)
OVERLAY_CONFIG = (
    ROOT / "components" / "bootloader" / "core_overlay" / "overlay.json"
)
MANIFEST = ROOT / "manifests" / "g2-2.2.6.10-core-source.json"


def write_json(path: Path, value: Any) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def ownership_key(region: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(
        region[key]
        for key in ("file_offset", "size", "target_address", "address_status")
    )


def new_region(contract_region: dict[str, Any]) -> dict[str, Any]:
    name = contract_region["name"]
    address = int(contract_region["target_address"])
    descriptions = {
        "opaque_before_replace_bootloader_redirect_init": (
            "bootloader_opaque_before_redirect_init",
            "Official Apollo bootloader bytes before recovered redirect_init",
        ),
        "replace_bootloader_redirect_init_source_redirect": (
            "bootloader_redirect_init_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "S200 bootloader redirect_init mutex initializer",
        ),
        "opaque_before_replace_bootloader_aeabi_memset": (
            "bootloader_opaque_between_redirect_init_and_aeabi_memset",
            "Official Apollo bootloader bytes between redirect_init and the "
            "source-replaced Arm EABI byte-fill primitive",
        ),
        "replace_bootloader_aeabi_memset_source_redirect": (
            "bootloader_aeabi_memset_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "Arm EABI byte-fill primitive",
        ),
        "opaque_before_replace_bootloader_aeabi_memcpy": (
            "bootloader_opaque_between_aeabi_memset_and_aeabi_memcpy",
            "Official Apollo bootloader bytes between the Arm EABI byte-fill "
            "and forward-copy primitives",
        ),
        "replace_bootloader_aeabi_memcpy_source_redirect": (
            "bootloader_aeabi_memcpy_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "Arm EABI forward-copy primitive",
        ),
        "opaque_before_replace_bootloader_memcmp": (
            "bootloader_opaque_between_aeabi_memcpy_and_memcmp",
            "Official Apollo bootloader bytes between the Arm EABI forward-copy "
            "and bounded byte-comparison primitives",
        ),
        "replace_bootloader_memcmp_source_redirect": (
            "bootloader_memcmp_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "bounded byte-comparison primitive",
        ),
        "replace_bootloader_crc32_source_redirect": (
            "bootloader_crc32_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "reflected CRC-32 update primitive",
        ),
        "opaque_before_replace_bootloader_strcspn": (
            "bootloader_opaque_between_memcmp_and_strcspn",
            "Official Apollo bootloader bytes between the bounded byte "
            "comparison and reject-set span primitives",
        ),
        "replace_bootloader_strcspn_source_redirect": (
            "bootloader_strcspn_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "reject-set string-span primitive",
        ),
        "replace_bootloader_strspn_source_redirect": (
            "bootloader_strspn_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "accept-set string-span primitive",
        ),
        "replace_bootloader_store_200270cc_source_redirect": (
            "bootloader_store_200270cc_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "SRAM-word setter at 0x200270CC",
        ),
        "replace_bootloader_udiv10_source_redirect": (
            "bootloader_udiv10_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "unsigned 64-bit divide-by-ten helper",
        ),
        "replace_bootloader_udec_digits_source_redirect": (
            "bootloader_udec_digits_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "unsigned decimal digit-count helper",
        ),
        "replace_bootloader_sdec_digits_source_redirect": (
            "bootloader_sdec_digits_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "signed-magnitude decimal digit-count helper",
        ),
        "replace_bootloader_hex_digits_source_redirect": (
            "bootloader_hex_digits_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "hexadecimal digit-count helper",
        ),
        "replace_bootloader_parse_dec_source_redirect": (
            "bootloader_parse_dec_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "wrapping decimal parser",
        ),
        "replace_bootloader_u64_to_dec_source_redirect": (
            "bootloader_u64_to_dec_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "unsigned 64-bit decimal output helper",
        ),
        "replace_bootloader_u64_to_hex_source_redirect": (
            "bootloader_u64_to_hex_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "unsigned 64-bit hexadecimal output helper",
        ),
        "replace_bootloader_nullable_strlen_source_redirect": (
            "bootloader_nullable_strlen_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "nullable string-length helper",
        ),
        "replace_bootloader_repeat_char_source_redirect": (
            "bootloader_repeat_char_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "null-output-aware repeated-character helper",
        ),
        "replace_bootloader_float_to_fixed_source_redirect": (
            "bootloader_float_to_fixed_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "fixed-point float formatter",
        ),
        "opaque_before_replace_easylogger_get_fmt_enabled": (
            "bootloader_opaque_between_strspn_and_easylogger",
            "Official Apollo bootloader bytes between the accept-set string "
            "span primitive and the source-replaced EasyLogger formatter",
        ),
        "open_cfw_bootloader_redirect_init_alignment_padding": (
            "bootloader_redirect_init_alignment_padding",
            "Generated two-byte alignment before the redirect_init closure",
        ),
        "open_cfw_bootloader_redirect_init_source_leaf": (
            "bootloader_redirect_init_source_leaf",
            "Compiled clean-room redirect_init function and authenticated "
            "diagnostic read-only-data closure",
        ),
        "open_cfw_bootloader_aeabi_memset_alignment_padding": (
            "bootloader_aeabi_memset_alignment_padding",
            "Generated one-byte alignment before the Arm EABI byte-fill leaf",
        ),
        "open_cfw_bootloader_aeabi_memset_source_leaf": (
            "bootloader_aeabi_memset_source_leaf",
            "Compiled clean-room Arm EABI byte-fill primitive",
        ),
        "open_cfw_bootloader_aeabi_memcpy_source_leaf": (
            "bootloader_aeabi_memcpy_source_leaf",
            "Compiled clean-room Arm EABI forward-copy primitive",
        ),
        "open_cfw_bootloader_memcmp_source_leaf": (
            "bootloader_memcmp_source_leaf",
            "Compiled clean-room bounded byte-comparison primitive",
        ),
        "open_cfw_bootloader_crc32_alignment_padding": (
            "bootloader_crc32_alignment_padding",
            "Generated two-byte alignment before the reflected CRC-32 leaf",
        ),
        "open_cfw_bootloader_crc32_source_leaf": (
            "bootloader_crc32_source_leaf",
            "Compiled clean-room reflected CRC-32 update primitive",
        ),
        "open_cfw_bootloader_strcspn_source_leaf": (
            "bootloader_strcspn_source_leaf",
            "Compiled clean-room reject-set string-span primitive",
        ),
        "open_cfw_bootloader_strspn_source_leaf": (
            "bootloader_strspn_source_leaf",
            "Compiled clean-room accept-set string-span primitive",
        ),
        "open_cfw_bootloader_store_200270cc_source_leaf": (
            "bootloader_store_200270cc_source_leaf",
            "Compiled clean-room SRAM-word setter for 0x200270CC",
        ),
        "open_cfw_bootloader_udiv10_source_leaf": (
            "bootloader_udiv10_source_leaf",
            "Compiled clean-room unsigned 64-bit divide-by-ten helper",
        ),
        "open_cfw_bootloader_udec_digits_source_leaf": (
            "bootloader_udec_digits_source_leaf",
            "Compiled clean-room unsigned decimal digit-count helper",
        ),
        "open_cfw_bootloader_sdec_digits_source_leaf": (
            "bootloader_sdec_digits_source_leaf",
            "Compiled clean-room signed-magnitude decimal digit-count helper",
        ),
        "open_cfw_bootloader_hex_digits_source_leaf": (
            "bootloader_hex_digits_source_leaf",
            "Compiled clean-room hexadecimal digit-count helper",
        ),
        "open_cfw_bootloader_parse_dec_source_leaf": (
            "bootloader_parse_dec_source_leaf",
            "Compiled clean-room wrapping decimal parser",
        ),
        "open_cfw_bootloader_u64_to_dec_source_leaf": (
            "bootloader_u64_to_dec_source_leaf",
            "Compiled clean-room unsigned 64-bit decimal output helper",
        ),
        "open_cfw_bootloader_u64_to_hex_source_leaf": (
            "bootloader_u64_to_hex_source_leaf",
            "Compiled clean-room unsigned 64-bit hexadecimal output helper",
        ),
        "open_cfw_bootloader_nullable_strlen_source_leaf": (
            "bootloader_nullable_strlen_source_leaf",
            "Compiled clean-room nullable string-length helper",
        ),
        "open_cfw_bootloader_repeat_char_source_leaf": (
            "bootloader_repeat_char_source_leaf",
            "Compiled clean-room null-output-aware repeated-character helper",
        ),
        "open_cfw_bootloader_float_to_fixed_source_leaf": (
            "bootloader_float_to_fixed_source_leaf",
            "Compiled clean-room fixed-point float formatter",
        ),
    }
    if name not in descriptions:
        raise ValueError(f"no reviewed manifest identity for new region {name}")
    manifest_name, function = descriptions[name]
    return {
        "address_status": contract_region["address_status"],
        "file_offset": int(contract_region["file_offset"]),
        "function": function,
        "name": manifest_name,
        "output": (
            f"apollo510b/{manifest_name.replace('_', '-')}-"
            f"0x{address:08x}.bin"
        ),
        "size": int(contract_region["size"]),
        "target": "apollo510b_internal_mram",
        "target_address": address,
    }


def sync_manifest() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    overlay_config = json.loads(OVERLAY_CONFIG.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    override = manifest["component_overrides"]["apollo_bootloader"]
    old_regions = {
        ownership_key(region): region for region in override["regions"]
    }
    regions = []
    for contract_region in contract["regions"]:
        old = old_regions.get(ownership_key(contract_region))
        regions.append(dict(old) if old is not None else new_region(contract_region))

    provider = override["provider"]
    provider.update(contract["provider"])
    linux_expected = overlay_config["toolchain_profiles"]["linux-clang"][
        "expected"
    ]
    provider.setdefault("profiles", {})["linux-clang"] = {
        "size": linux_expected["component_size"],
        "sha256": linux_expected["component_sha256"],
    }
    for profile_name in (
        "apple-font-manager-record",
        "apple-product-rtos-record",
    ):
        if profile_name in provider.get("profiles", {}):
            provider["profiles"][profile_name] = {
                "size": provider["size"],
                "sha256": provider["sha256"],
            }
    suffixes = (
        "recovered S200 redirect_init two-mutex initialization entry",
        "recovered Arm EABI byte-fill primitive",
        "recovered Arm EABI forward-copy primitive",
        "recovered bounded byte-comparison primitive",
        "recovered reflected CRC-32 update primitive",
        "recovered reject-set string-span primitive",
        "recovered accept-set string-span primitive",
        "recovered SRAM-word setter at 0x200270CC",
        "recovered unsigned 64-bit divide-by-ten helper",
        "recovered unsigned decimal digit-count helper",
        "recovered signed-magnitude decimal digit-count helper",
        "recovered hexadecimal digit-count helper",
        "recovered wrapping decimal parser",
        "recovered unsigned 64-bit decimal output helper",
        "recovered unsigned 64-bit hexadecimal output helper",
        "recovered nullable string-length helper",
        "recovered null-output-aware repeated-character helper",
        "recovered fixed-point float formatter",
    )
    parts = [part.strip() for part in override["function"].split(";")]
    for suffix in suffixes:
        if suffix not in parts:
            parts.append(suffix)
    override["function"] = "; ".join(parts)
    override["regions"] = regions
    write_json(MANIFEST, manifest)


def verify() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    override = manifest["component_overrides"]["apollo_bootloader"]
    provider = override["provider"]
    for key in ("kind", "path", "size", "sha256"):
        if provider[key] != contract["provider"][key]:
            raise ValueError(f"bootloader provider {key} is stale")
    if [ownership_key(item) for item in override["regions"]] != [
        ownership_key(item) for item in contract["regions"]
    ]:
        raise ValueError("bootloader manifest ownership regions are stale")
    print(
        "Verified bootloader runtime manifest: "
        f"{provider['size']} bytes/{provider['sha256']}"
    )
    print("  hardware operations: none")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("sync-manifest", "verify"))
    args = parser.parse_args()
    if args.action == "sync-manifest":
        sync_manifest()
    verify()


if __name__ == "__main__":
    main()
