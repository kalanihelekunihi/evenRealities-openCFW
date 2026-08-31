#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

"""Build the guarded Apollo-main FreeType CFF scatter component.

This is a post-link component stage.  It consumes an authenticated Apollo-main
EVENOTA payload, rebuilds the admitted FreeType 2.9.1 CFF translation unit for
one reviewed compiler profile, replays the exact final scatter link, and emits
one expanded Apollo-main payload.  It does not assemble or flash an OTA
package; the package layer consumes the emitted payload and region layout.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import struct
import sys
import tempfile
import zlib
from pathlib import Path
from typing import Any


G2 = Path(__file__).resolve().parents[3]
COMPONENT = Path(__file__).resolve().parent
CONFIG = COMPONENT / "overlay.json"
SCATTER_ANALYZER = G2 / "tools/analyze_g2_freetype_cff_scatter_link.py"
SCATTER_MANIFEST = G2 / "tools/manifests/g2-freetype-cff-scatter-link.json"
OPEN_CFW = G2 / "tools/open_cfw.py"

RUN_BASE = 0x00438000
PREAMBLE_BYTES = 32
UPDATE_FLAG = 0x007FE000
STOCK_INTERVAL = (0x005ABEF8, 0x005B0114)
TAIL_INTERVAL = (0x007FCEBA, UPDATE_FLAG)
TAIL_TEXT_START = 0x007FCEC0
CANDIDATE_END = 0x007FDED4
MODULE_SLOT = 0x0073EF00
STOCK_CLASS_BYTES = bytes.fromhex("74cb6d00")
REPLACEMENT_CLASS_BYTES = bytes.fromhex("14c05a00")
STOCK_INTERVAL_SHA256 = (
    "58b8b5e4c1b801d7ac4c6883dc8afeccd7cf370e3e9cccdf95f938e20b91358b"
)
ERASED_BYTE = 0xFF
SECTION_ORDER = (
    ".cff_stock_rodata", ".cff_stock_text",
    ".cff_tail_text", ".cff_tail_exidx",
)


class BuildError(RuntimeError):
    """Raised when a source, byte, placement, or receipt invariant drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BuildError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    return digest(path.read_bytes())


def canonical(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def _load_module(path: Path, name: str) -> Any:
    specification = importlib.util.spec_from_file_location(name, path)
    require(specification is not None and specification.loader is not None,
            f"cannot load module: {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def _read_config(path: Path) -> dict[str, Any]:
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise BuildError(f"cannot read CFF scatter config: {error}") from error
    require(isinstance(result, dict), "CFF scatter config is not an object")
    return result


def _pin(path: Path, record: dict[str, Any], role: str) -> bytes:
    try:
        body = path.read_bytes()
    except OSError as error:
        raise BuildError(f"cannot read {role}: {error}") from error
    require(
        len(body) == record.get("size") and digest(body) == record.get("sha256"),
        f"{role} pin drift",
    )
    return body


def _extract_entry_six(package: bytes) -> tuple[bytes, dict[str, int]]:
    require(len(package) >= 0xB0 and package[:8] == b"EVENOTA\0",
            "base package is not EVENOTA")
    count = struct.unpack_from("<I", package, 8)[0]
    require(1 <= count <= 32, "base package entry count is invalid")
    found: list[tuple[int, int, int]] = []
    for index in range(count):
        entry_id, offset, size, crc = struct.unpack_from(
            "<IIII", package, 0x40 + index * 16
        )
        if entry_id == 6:
            found.append((offset, size, crc))
    require(len(found) == 1, "base package does not have exactly one entry 6")
    offset, size, crc = found[0]
    require(size >= 128 and offset + size <= len(package),
            "base entry 6 extent is invalid")
    header = package[offset:offset + 128]
    payload = package[offset + 128:offset + size]
    open_cfw = _load_module(OPEN_CFW, "g2_cff_component_open_cfw")
    require(struct.unpack_from("<I", header, 8)[0] == len(payload),
            "base entry 6 header length drift")
    require(struct.unpack_from("<I", header, 12)[0] == crc,
            "base entry 6 CRC fields disagree")
    require(open_cfw.crc32c_msb(payload) == crc,
            "base entry 6 CRC does not cover its payload")
    open_cfw.validate_apollo_main(payload)
    return payload, {"package_offset": offset, "entry_size": size, "crc32c_msb": crc}


def _runtime_offset(address: int) -> int:
    require(RUN_BASE <= address < UPDATE_FLAG, "runtime address is outside Apollo app")
    return PREAMBLE_BYTES + address - RUN_BASE


def _base_profile(config: dict[str, Any], profile: str) -> dict[str, Any]:
    profiles = config.get("profiles")
    require(isinstance(profiles, dict) and profile in profiles,
            f"unsupported CFF scatter profile: {profile}")
    result = profiles[profile]
    require(isinstance(result, dict), f"invalid CFF scatter profile: {profile}")
    return result


def _authenticate_base(
    package_path: Path, profile: str, config: dict[str, Any]
) -> tuple[bytes, dict[str, Any]]:
    expected = _base_profile(config, profile)
    package = _pin(package_path, expected["base_package"], "base package")
    component, entry = _extract_entry_six(package)
    require(
        len(component) == expected["base_component"]["size"] and
        digest(component) == expected["base_component"]["sha256"],
        f"{profile}: base Apollo component pin drift",
    )
    end = RUN_BASE + len(component) - PREAMBLE_BYTES
    require(end == expected["base_component"]["runtime_end_exclusive"],
            f"{profile}: base Apollo runtime end drift")
    stock_start = _runtime_offset(STOCK_INTERVAL[0])
    stock_end = _runtime_offset(STOCK_INTERVAL[1])
    require(digest(component[stock_start:stock_end]) == STOCK_INTERVAL_SHA256,
            f"{profile}: stock CFF interval guard drift")
    slot = _runtime_offset(MODULE_SLOT)
    require(component[slot:slot + 4] == STOCK_CLASS_BYTES,
            f"{profile}: stock CFF class-pointer guard drift")
    require(end <= TAIL_TEXT_START,
            f"{profile}: current Apollo component collides with CFF tail")
    return component, {
        "package": {
            "path": package_path.relative_to(G2).as_posix()
            if package_path.is_relative_to(G2) else str(package_path),
            "size": len(package), "sha256": digest(package),
        },
        "component": {
            "size": len(component), "sha256": digest(component),
            "runtime_end_exclusive": end,
        },
        "entry": entry,
    }


def _authenticate_component(
    component_path: Path, profile: str, config: dict[str, Any]
) -> tuple[bytes, dict[str, Any]]:
    expected = _base_profile(config, profile)
    body = _pin(component_path, expected["base_component"], "base Apollo component")
    open_cfw = _load_module(OPEN_CFW, "g2_cff_component_open_cfw_direct")
    open_cfw.validate_apollo_main(body)
    end = RUN_BASE + len(body) - PREAMBLE_BYTES
    require(end == expected["base_component"]["runtime_end_exclusive"],
            f"{profile}: base Apollo runtime end drift")
    stock_start = _runtime_offset(STOCK_INTERVAL[0])
    stock_end = _runtime_offset(STOCK_INTERVAL[1])
    require(digest(body[stock_start:stock_end]) == STOCK_INTERVAL_SHA256,
            f"{profile}: stock CFF interval guard drift")
    slot = _runtime_offset(MODULE_SLOT)
    require(body[slot:slot + 4] == STOCK_CLASS_BYTES,
            f"{profile}: stock CFF class-pointer guard drift")
    require(end <= TAIL_TEXT_START,
            f"{profile}: current Apollo component collides with CFF tail")
    return body, {
        "package": None,
        "component": {
            "path": "same-build-pre-cff-component",
            "size": len(body), "sha256": digest(body),
            "runtime_end_exclusive": end,
        },
        "entry": None,
    }


def _build_sections(profile: str, directory: Path, config: dict[str, Any]) -> tuple[dict[str, bytes], dict[str, Any]]:
    dependencies = config.get("dependencies", {})
    _pin(SCATTER_ANALYZER, dependencies["scatter_analyzer"], "scatter analyzer")
    manifest_body = _pin(
        SCATTER_MANIFEST, dependencies["scatter_manifest"], "scatter manifest"
    )
    scatter_manifest = json.loads(manifest_body)
    scatter = _load_module(SCATTER_ANALYZER, "g2_cff_component_scatter")
    size_module = scatter.load_module(
        scatter.SIZE_ANALYZER, "g2_cff_component_size_dependency"
    )
    size_report = json.loads(size_module.MANIFEST.read_text(encoding="utf-8"))
    selected = size_report["selected_candidate"]["profiles"]["apple-clang"]
    map_symbols = set(
        selected["final"]["materialized_complete_map_symbol_names"]
    ) | set(selected["final"]["inlined_only_complete_map_symbol_names"])
    require(len(map_symbols) == 101, "complete CFF source-function set drift")
    placement_builder = size_module.load_module(size_module.BUILDER)
    compiler = placement_builder.PROFILES.get(profile)
    require(compiler is not None, f"no compiler for CFF profile: {profile}")
    report = scatter._build_once(
        size_module, profile, compiler, directory, map_symbols
    )
    require(report == scatter_manifest["profiles"][profile],
            f"{profile}: final scatter build differs from admitted manifest")
    bodies: dict[str, bytes] = {}
    for section in report["sections"]:
        name = section["name"]
        path = directory / f"{name[1:]}.bin"
        body = path.read_bytes()
        require(len(body) == section["bytes"] and digest(body) == section["sha256"],
                f"{profile}: extracted {name} drift")
        bodies[name] = body
    require(tuple(bodies) == SECTION_ORDER, f"{profile}: section order drift")
    return bodies, report


def _validate_spans(report: dict[str, Any], bodies: dict[str, bytes]) -> list[dict[str, Any]]:
    result = []
    for section in report["sections"]:
        name = section["name"]
        start = int(section["start"], 16)
        end = int(section["end_exclusive"], 16)
        require(end - start == len(bodies[name]), f"{name}: address extent drift")
        require(start % section["alignment"] == 0, f"{name}: alignment drift")
        legal = (
            STOCK_INTERVAL[0] <= start < end <= STOCK_INTERVAL[1] or
            TAIL_INTERVAL[0] <= start < end <= TAIL_INTERVAL[1]
        )
        require(legal, f"{name}: placement escaped authenticated intervals")
        result.append({
            "name": name, "start": start, "end_exclusive": end,
            "size": len(bodies[name]), "alignment": section["alignment"],
            "sha256": digest(bodies[name]),
        })
    ordered = sorted(result, key=lambda row: row["start"])
    require(all(left["end_exclusive"] <= right["start"]
                for left, right in zip(ordered, ordered[1:])),
            "CFF scatter sections overlap")
    require(ordered[-1]["end_exclusive"] == CANDIDATE_END,
            "CFF scatter candidate end drift")
    return result


def _apply(
    base: bytes, spans: list[dict[str, Any]], bodies: dict[str, bytes]
) -> tuple[bytes, dict[str, Any]]:
    base_end = RUN_BASE + len(base) - PREAMBLE_BYTES
    target_size = PREAMBLE_BYTES + CANDIDATE_END - RUN_BASE
    require(target_size > len(base), "CFF scatter target does not expand component")
    output = bytearray(base)
    output.extend(bytes([ERASED_BYTE]) * (target_size - len(output)))

    # No mutation occurs until all source, base, bounds, overlap, and guard
    # checks above have completed.
    for span in spans:
        offset = _runtime_offset(span["start"])
        output[offset:offset + span["size"]] = bodies[span["name"]]
    slot = _runtime_offset(MODULE_SLOT)
    require(output[slot:slot + 4] == STOCK_CLASS_BYTES,
            "class-pointer compare-before-write guard changed")
    output[slot:slot + 4] = REPLACEMENT_CLASS_BYTES

    struct.pack_into("<I", output, 0, 0x04000000 | len(output))
    struct.pack_into("<I", output, 4, 0)
    nested_crc = zlib.crc32(output[8:]) & 0xFFFFFFFF
    struct.pack_into("<I", output, 4, nested_crc)
    open_cfw = _load_module(OPEN_CFW, "g2_cff_component_open_cfw_final")
    open_cfw.validate_apollo_main(bytes(output))

    stock_offset = _runtime_offset(STOCK_INTERVAL[0])
    require(
        output[stock_offset:stock_offset + 4] == bodies[".cff_stock_rodata"][:4],
        "stock CFF replacement readback drift",
    )
    require(output[slot:slot + 4] == REPLACEMENT_CLASS_BYTES,
            "class-pointer patch readback drift")
    require(
        output[_runtime_offset(TAIL_TEXT_START):
               _runtime_offset(TAIL_TEXT_START) + len(bodies[".cff_tail_text"])]
        == bodies[".cff_tail_text"],
        "tail CFF replacement readback drift",
    )
    return bytes(output), {
        "base_runtime_end_exclusive": base_end,
        "runtime_end_exclusive": CANDIDATE_END,
        "erased_gap_start": base_end,
        "erased_gap_end_exclusive": TAIL_TEXT_START,
        "erased_gap_size": TAIL_TEXT_START - base_end,
        "erased_gap_byte": ERASED_BYTE,
        "nested_crc32": nested_crc,
    }


def _safe_token(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def region_partition(
    base_regions: list[dict[str, Any]], base_size: int,
    spans: list[dict[str, Any]], profile: str,
) -> list[dict[str, Any]]:
    """Split a reviewed base partition around every CFF-owned output byte."""
    require(base_regions and base_regions[0].get("file_offset") == 0,
            "base region partition is missing")
    cursor = 0
    for row in base_regions:
        require(row.get("file_offset") == cursor and
                isinstance(row.get("size"), int) and row["size"] > 0,
                "base region partition has a gap or invalid row")
        cursor += row["size"]
    require(cursor == base_size, "base region partition does not tile component")

    mutations = [
        {
            "start": _runtime_offset(span["start"]),
            "end": _runtime_offset(span["end_exclusive"]),
            "name": _safe_token(span["name"]),
            "function": f"Compiled FreeType 2.9.1 CFF scatter section {span['name']}",
            "address_status": "source_compiled",
        }
        for span in spans if span["start"] < TAIL_INTERVAL[0]
    ]
    mutations.append({
        "start": _runtime_offset(MODULE_SLOT),
        "end": _runtime_offset(MODULE_SLOT) + 4,
        "name": "module-class-pointer",
        "function": "Guarded CFF module-class pointer route",
        "address_status": "generated_source_data_replacement",
    })
    mutations.sort(key=lambda row: row["start"])
    require(all(left["end"] <= right["start"]
                for left, right in zip(mutations, mutations[1:])),
            "base CFF mutations overlap")

    result: list[dict[str, Any]] = []
    for base in base_regions:
        start = base["file_offset"]
        end = start + base["size"]
        cuts = {start, end}
        for mutation in mutations:
            if mutation["start"] < end and mutation["end"] > start:
                cuts.add(max(start, mutation["start"]))
                cuts.add(min(end, mutation["end"]))
        points = sorted(cuts)
        for left, right in zip(points, points[1:]):
            mutation = next((item for item in mutations
                             if item["start"] <= left and right <= item["end"]), None)
            row = dict(base)
            row["file_offset"] = left
            row["size"] = right - left
            runtime = RUN_BASE + left - PREAMBLE_BYTES if left >= PREAMBLE_BYTES else None
            if runtime is not None and "target_address" in row:
                row["target_address"] = runtime
            suffix = f"{left:08x}-{right:08x}"
            if mutation is None:
                if left != start or right != end:
                    row["name"] = f"{base['name']}_split_{suffix}"
                    row["output"] = (
                        f"apollo510b/cff-scatter-retained-{profile}-{suffix}.bin"
                    )
            else:
                row.update({
                    "name": f"freetype_cff_{mutation['name']}_{suffix}",
                    "function": mutation["function"],
                    "address_status": mutation["address_status"],
                    "output": f"apollo510b/cff-scatter-{profile}-{mutation['name']}-{suffix}.bin",
                    "target": "apollo510b_internal_mram",
                    "target_address": runtime,
                })
            result.append(row)

    base_end = RUN_BASE + base_size - PREAMBLE_BYTES
    append = [span for span in spans if span["start"] >= TAIL_INTERVAL[0]]
    require(append and append[0]["start"] == TAIL_TEXT_START,
            "tail CFF section start drift")
    if base_end < TAIL_TEXT_START:
        result.append({
            "name": f"freetype_cff_erased_gap_{profile}",
            "function": "Generated erased MRAM padding before CFF tail text",
            "file_offset": base_size,
            "size": TAIL_TEXT_START - base_end,
            "address_status": "generated_padding",
            "output": f"apollo510b/cff-scatter-{profile}-erased-gap.bin",
            "target": "apollo510b_internal_mram",
            "target_address": base_end,
        })
    for span in append:
        start = _runtime_offset(span["start"])
        result.append({
            "name": f"freetype_cff_{_safe_token(span['name'])}_{profile}",
            "function": f"Compiled FreeType 2.9.1 CFF scatter section {span['name']}",
            "file_offset": start,
            "size": span["size"],
            "address_status": "source_compiled",
            "output": f"apollo510b/cff-scatter-{profile}-{_safe_token(span['name'])}.bin",
            "target": "apollo510b_internal_mram",
            "target_address": span["start"],
        })
    cursor = 0
    outputs: set[str] = set()
    for row in result:
        require(row["file_offset"] == cursor and row["size"] > 0,
                "CFF output region partition has a gap")
        require(row["output"] not in outputs, "CFF output region path is duplicated")
        outputs.add(row["output"])
        cursor += row["size"]
    require(cursor == PREAMBLE_BYTES + CANDIDATE_END - RUN_BASE,
            "CFF output region partition does not tile candidate")
    return result


def build(
    *, profile: str, output_dir: Path, base_package: Path | None = None,
    base_component: Path | None = None,
    config_path: Path = CONFIG, base_regions: list[dict[str, Any]] | None = None,
    observe: bool = False,
) -> dict[str, Any]:
    config = _read_config(config_path)
    require((base_package is None) != (base_component is None),
            "provide exactly one base package or base component")
    component, base = (
        _authenticate_base(base_package.resolve(), profile, config)
        if base_package is not None else
        _authenticate_component(base_component.resolve(), profile, config)
    )
    with tempfile.TemporaryDirectory(prefix="opencfw-cff-component-") as raw:
        temporary = Path(raw)
        bodies, scatter_report = _build_sections(
            profile, temporary / "link", config
        )
        spans = _validate_spans(scatter_report, bodies)
        candidate, placement = _apply(component, spans, bodies)

        expected = _base_profile(config, profile).get("expected", {})
        observed = {"size": len(candidate), "sha256": digest(candidate)}
        if not observe:
            require(observed == expected.get("component"),
                    f"{profile}: final CFF component pin drift")
        regions = (
            region_partition(base_regions, len(component), spans, profile)
            if base_regions is not None else None
        )
        report: dict[str, Any] = {
            "schema_version": 1,
            "profile": profile,
            "status": "g2-freetype-cff-scatter-component-emitted",
            "base": base,
            "component": {
                **observed,
                "runtime_start": RUN_BASE,
                "runtime_end_exclusive": CANDIDATE_END,
                "growth_bytes": len(candidate) - len(component),
                "nested_crc32": f"0x{placement['nested_crc32']:08X}",
            },
            "placement": {
                **{key: (f"0x{value:08X}" if key.endswith("start") or
                           key.endswith("end_exclusive") else value)
                   for key, value in placement.items()},
                "sections": spans,
                "unused_scattered_table_pool_bytes": 360,
                "unused_scattered_table_pool_consumed": 0,
            },
            "module_class_patch": {
                "runtime_address": f"0x{MODULE_SLOT:08X}",
                "expected_hex": STOCK_CLASS_BYTES.hex(),
                "replacement_hex": REPLACEMENT_CLASS_BYTES.hex(),
                "compare_before_write": True,
                "applied_after_all_preflight_checks": True,
            },
            "scatter_manifest": {
                "size": SCATTER_MANIFEST.stat().st_size,
                "sha256": sha256(SCATTER_MANIFEST),
                "profile_final_elf": scatter_report["final_elf"],
                "undefined_symbols": scatter_report["undefined_symbols"],
                "relocations": scatter_report["relocations"],
            },
            "regions": regions,
            "safety": {
                "all_mutations_in_apollo_entry_6": True,
                "cross_entry_atomicity_required": False,
                "hardware_validation_performed": False,
                "automatic_flashing_authorized": False,
            },
        }
        report["receipt_sha256"] = digest(canonical({
            key: report[key] for key in (
                "profile", "base", "component", "placement",
                "module_class_patch", "scatter_manifest", "safety",
            )
        }))

        require(not output_dir.exists(), "output directory already exists")
        staging = output_dir.parent / f".{output_dir.name}.staging-{os.getpid()}"
        require(not staging.exists(), "staging directory already exists")
        staging.mkdir(parents=True)
        try:
            artifacts: dict[str, bytes] = {
                "ota_s200_firmware_ota.bin": candidate,
                "build-report.json": canonical(report),
                **{
                    f"{name[1:]}.bin": body for name, body in bodies.items()
                },
            }
            for name, body in artifacts.items():
                (staging / name).write_bytes(body)
            ledger = "".join(
                f"{digest(body)}  {name}\n"
                for name, body in sorted(artifacts.items())
            ).encode()
            (staging / "SHA256SUMS").write_bytes(ledger)
            os.replace(staging, output_dir)
        finally:
            if staging.exists():
                for path in staging.iterdir():
                    path.unlink()
                staging.rmdir()
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True, choices=("apple-clang", "linux-clang"))
    parser.add_argument("--base-package", type=Path)
    parser.add_argument("--base-component", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--config", type=Path, default=CONFIG)
    parser.add_argument("--observe", action="store_true")
    args = parser.parse_args()
    try:
        config = _read_config(args.config)
        profile = _base_profile(config, args.profile)
        require(not (args.base_package and args.base_component),
                "base package and base component are mutually exclusive")
        package = (
            args.base_package or G2 / profile["base_package"]["path"]
            if args.base_component is None else None
        )
        report = build(
            profile=args.profile, base_package=package,
            base_component=args.base_component,
            output_dir=args.output_dir, config_path=args.config,
            observe=args.observe,
        )
    except (BuildError, OSError, KeyError, ValueError) as error:
        print(f"G2 FreeType CFF component build failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
