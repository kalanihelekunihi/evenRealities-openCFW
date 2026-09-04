#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Integrate the qualified EM9305 mixed-source provider into the G2 manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
BUILD_DIR = ROOT / "components/em9305/source_overlay/build"
REPORT_PATH = BUILD_DIR / "build-report.json"
PROVIDER_PATH = BUILD_DIR / "firmware_ble_em9305.bin"
APP_ADDRESS = 0x00302400
APP_FILE_OFFSET = 1060

sys.path.insert(0, str(ROOT / "components/em9305/source_overlay"))
import build_overlay as overlay  # noqa: E402
sys.path.insert(0, str(ROOT / "tools"))
import open_cfw  # noqa: E402


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def routed_application_regions(report: dict) -> list[dict]:
    application = report["application"]
    end = application["source_end_exclusive"]
    spans: list[tuple[int, int, str]] = []

    for address, size in overlay.META_ISLANDS:
        spans.append((address, address + size, "generated"))
    for _section, address, _target in overlay.META_ENTRY_PATCHES:
        spans.append((address, address + 4, "source"))
    for _section, address, allocation in overlay.ENTRY_PATCHES:
        spans.append((address, address + allocation, "generated"))
        spans.append((address, address + 4, "source"))
    spans.extend((
        (0x00302D80, 0x00302D82, "source"),
        (0x00304EB4, 0x00304EBA, "source"),
        (0x00313778, 0x0031377A, "source"),
        (0x003137F4, 0x003137F6, "source"),
        (0x003137F6, 0x003137F8, "generated"),
        (0x003137F8, 0x003137FA, "source"),
        (application["stock_end_exclusive"], end, "source"),
    ))

    boundaries = {APP_ADDRESS, end}
    for start, stop, _kind in spans:
        boundaries.update((start, stop))
    ordered = sorted(boundaries)
    raw: list[tuple[int, int, str]] = []
    for start, stop in zip(ordered, ordered[1:]):
        kind = "retained"
        for span_start, span_stop, span_kind in spans:
            if span_start <= start and stop <= span_stop:
                if span_kind == "source" or kind == "retained":
                    kind = span_kind
        if raw and raw[-1][2] == kind and raw[-1][1] == start:
            raw[-1] = (raw[-1][0], stop, kind)
        else:
            raw.append((start, stop, kind))

    counts = {"source": 0, "generated": 0, "retained": 0}
    regions = []
    for index, (start, stop, kind) in enumerate(raw):
        size = stop - start
        counts[kind] += size
        regions.append({
            "name": f"em9305_application_{kind}_{index:03d}",
            "function": {
                "source": "ARCv2-EM C-compiled production runtime bytes",
                "generated": "Deterministic NOP fill replacing routed stock allocation",
                "retained": "Authenticated retained EM9305 controller application bytes",
            }[kind],
            "file_offset": APP_FILE_OFFSET + start - APP_ADDRESS,
            "size": size,
            "target": "em9305",
            "target_address": start,
            "address_status": {
                "source": "source_compiled",
                "generated": "generated_padding",
                "retained": "official_blob",
            }[kind],
            "output": f"em9305/application-{kind}-{index:03d}-0x{start:08x}.bin",
        })
    if counts != {"source": 1_174, "generated": 1_102, "retained": 209_648}:
        raise RuntimeError(f"EM9305 application region accounting drift: {counts}")
    return regions


def component_override(report: dict) -> dict:
    provider = report["provider"]
    regions = [
        {
            "name": "record_metadata",
            "function": "Generated EM9305 record table, erase geometry, and alignment metadata",
            "file_offset": 0,
            "size": 124,
            "address_status": "container_only",
            "output": "em9305/record-metadata.bin",
        },
        {
            "name": "record_0",
            "function": "Authenticated retained EM9305 record 0",
            "file_offset": 124,
            "size": 224,
            "target": "em9305",
            "target_address": 0x00300000,
            "address_status": "official_blob",
            "output": "em9305/record-0-0x00300000.bin",
        },
        {
            "name": "record_1",
            "function": "Authenticated retained EM9305 record 1",
            "file_offset": 348,
            "size": 656,
            "target": "em9305",
            "target_address": 0x00300400,
            "address_status": "official_blob",
            "output": "em9305/record-1-0x00300400.bin",
        },
        {
            "name": "record_2_fhdr",
            "function": "Authenticated retained EM9305 FHDR descriptor",
            "file_offset": 1004,
            "size": 56,
            "target": "em9305",
            "target_address": 0x00302000,
            "address_status": "official_blob",
            "output": "em9305/record-2-fhdr-0x00302000.bin",
        },
        *routed_application_regions(report),
    ]
    if sum(region["size"] for region in regions) != provider["size"]:
        raise RuntimeError("EM9305 manifest regions do not conserve provider bytes")
    return {
        "function": (
            "EM9305 Bluetooth controller package with production-routed clean-room "
            "MetaWare helpers and reconstructible residual-tail primitives"
        ),
        "provider": {
            "kind": "source_build",
            "path": "components/em9305/source_overlay/build/firmware_ble_em9305.bin",
            "size": provider["size"],
            "sha256": provider["sha256"],
            "profiles": {
                "linux-clang": {
                    "size": provider["size"],
                    "sha256": provider["sha256"],
                },
            },
            "source_owned_bytes": 1_174,
            "opaque_base_bytes": 210_584,
            "generated_patch_site_bytes": 1_102,
            "generated_container_bytes": 124,
        },
        "regions": regions,
    }


def assembled_identity(profile: str) -> tuple[int, str]:
    manifest = open_cfw.load_manifest(MANIFEST)
    payloads = open_cfw.read_providers(
        manifest, ROOT, toolchain_profile=profile, record=True
    )
    if profile == "linux-clang":
        payloads["apollo_bootloader"] = (
            ROOT / "build/canonical-provider/linux-clang/apollo_bootloader/ota_s200_bootloader.bin"
        ).read_bytes()
        payloads["apollo_main"] = (
            ROOT / "build/canonical-provider/linux-clang/apollo_main-final72/ota_s200_firmware_ota.bin"
        ).read_bytes()
    image, _entries = open_cfw.assemble_evenota(manifest, payloads)
    return len(image), sha256(image)


def main() -> int:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    provider = PROVIDER_PATH.read_bytes()
    if (
        report.get("status") != "em9305-runtime-production-routed"
        or report.get("production_routed") is not True
        or report["provider"] != {
            "path": "components/em9305/source_overlay/build/firmware_ble_em9305.bin",
            "size": len(provider),
            "sha256": sha256(provider),
        }
    ):
        raise RuntimeError("EM9305 production provider receipt drift")

    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    data.setdefault("component_overrides", {})["ble_em9305"] = component_override(report)
    # Preserve valid-shaped pins while computing the new component-dependent package.
    data["package"]["expected_size"] = 4_750_576
    data["package"]["profiles"]["linux-clang"]["expected_size"] = 4_750_560
    MANIFEST.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    apple_size, apple_sha = assembled_identity("apple-clang")
    linux_size, linux_sha = assembled_identity("linux-clang")
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    data["package"]["expected_size"] = apple_size
    data["package"]["expected_sha256"] = apple_sha
    data["package"]["profiles"]["linux-clang"] = {
        "expected_size": linux_size,
        "expected_sha256": linux_sha,
    }
    MANIFEST.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "provider": report["provider"],
        "apple-clang": {"size": apple_size, "sha256": apple_sha},
        "linux-clang": {"size": linux_size, "sha256": linux_sha},
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
