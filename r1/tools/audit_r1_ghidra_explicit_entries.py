#!/usr/bin/env python3
"""Audit function entries explicitly named by the R1 Ghidra scripts.

The function-ownership ledger is built primarily from Ghidra's functions.csv.
Several analysis scripts also create or request functions that the CSV export can
omit.  This census prevents those explicit entries from disappearing behind an
otherwise clean ledger classification count.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = ROOT / "tools" / "ghidra_scripts"
DEFAULT_OWNERSHIP = ROOT / "docs" / "reference" / "FUNCTION-OWNERSHIP.csv"
DEFAULT_OUTPUT = ROOT / "docs" / "reference" / "GHIDRA-EXPLICIT-ENTRY-CENSUS.json"

# Only arrays used as function-entry seeds belong here.  Data, string, pointer,
# and reference-address arrays are deliberately excluded.  Despite its name,
# R1BootloaderExfilEvidence operates on a different application revision, not
# the bootloader despite its name.  Version-specific entries must never be
# reconciled against an address range from another application build.
ENTRY_ARRAYS = (
    ("R1AuthEvidence.java", "FUNCTION_ENTRIES", "application"),
    ("R1BleTxFlow.java", "ENTRIES", "application"),
    (
        "R1BootloaderExfilEvidence.java",
        "ENTRIES",
        "application_2.2.7.0005",
    ),
    ("R1BootloaderSeedKnownFunctions.java", "TAIL_TARGETS", "bootloader"),
    ("R1DfuRoute.java", "SEED_ADDRESSES", "application"),
    ("R1FactoryRoute.java", "ADDRESSES", "application"),
    ("R1FlashWriteBoundary.java", "SEED_FUNCTIONS", "application"),
    ("R1Functions.java", "ADDRESSES", "application"),
    ("R1GATTSecurityEvidence.java", "FUNCTION_ENTRIES", "application"),
    ("R1GattCacheRoute.java", "SEED_ADDRESSES", "application"),
    ("R1HRVEvidence.java", "FUNCTION_ENTRIES", "application"),
    ("R1HealthEventEvidence.java", "FUNCTION_ENTRIES", "application"),
    ("R1HealthHistoryEvidence.java", "FUNCTION_ENTRIES", "application"),
    ("R1MotionEvidence.java", "FUNCTION_ENTRIES", "application"),
    ("R1NFCEvidence.java", "FUNCTION_ENTRIES", "application"),
    ("R1NFCTEvidence.java", "ENTRIES", "application_2.2.7.0005"),
    ("R1NVEvidence.java", "FUNCTION_ENTRIES", "application"),
    ("R1OpticalResultEvidence.java", "FUNCTION_ENTRIES", "application"),
    ("R1PowerEvidence.java", "FUNCTION_ENTRIES", "application"),
    (
        "R1ProtocolRegistrationEvidence.java",
        "MODULE_DISPATCHER_ADDRESSES",
        "application",
    ),
    ("R1RadioEvidence.java", "FUNCTION_ENTRIES", "application"),
    ("R1SleepEvidence.java", "FUNCTION_ENTRIES", "application"),
    ("R1SoftDeviceConfig.java", "SEED_ADDRESSES", "application"),
    ("R1StressEvidence.java", "FUNCTION_ENTRIES", "application"),
    (
        "R1TemperatureAlgorithmEvidence.java",
        "FUNCTION_ENTRIES",
        "application",
    ),
    ("R1TouchControllerEvidence.java", "FUNCTION_ENTRIES", "application"),
    ("R1TouchEvidence.java", "FUNCTION_ENTRIES", "application"),
    ("R1TouchLifecycleEvidence.java", "FUNCTION_ENTRIES", "application"),
)

# Script arrays are analysis seeds, not infallible function inventories. These
# addresses are conclusively data operands in the preserved 2.2.6 listing:
# each is either inside a named literal word or is the named literal loaded by
# the cited instruction. Keeping the adjudication here preserves the bad seed
# without inventing an ownership-ledger function or a C implementation.
ADJUDICATED_NON_FUNCTIONS = {
    ("application", 0x00047F10): {
        "status": "adjudicated_non_function_secondary_segment",
        "classification_basis": (
            "secondary executable segment 0x00047F10..<0x00047F9A of the "
            "single Ghidra function entered at 0x00096CC8; the main segment "
            "transfers here only through B.W at 0x00096D66, and the pinned "
            "two-range composite is 374 bytes with SHA-256 "
            "a00d2417c36d598e48d0372052fabccf0444ea0ced5a0252ba33983ad912a34f"
        ),
    },
    ("application", 0x00042D26): {
        "status": "adjudicated_non_function_data",
        "classification_basis": (
            "two bytes into DAT_00042D24; the preceding function returns at "
            "0x00042D20 and the next executable entry begins at 0x00042D28"
        ),
    },
    ("application", 0x00045078): {
        "status": "adjudicated_non_function_data",
        "classification_basis": (
            "named DAT_00045078 literal loaded by the instruction at "
            "0x00045056; the next function begins at 0x00045084"
        ),
    },
    ("application", 0x00045C78): {
        "status": "adjudicated_non_function_data",
        "classification_basis": (
            "named literal word 0x000992D0 loaded by the thread-creation "
            "instruction at 0x00045C56; the executable function returns at "
            "0x00045C76 and the next function begins at 0x00045C84"
        ),
    },
    ("application", 0x00042974): {
        "status": "adjudicated_non_function_instruction_interior",
        "classification_basis": (
            "second halfword of the 32-bit Thumb branch at 0x00042972; "
            "the containing gate begins at 0x0004296A and returns at "
            "0x00042976 before the next function at 0x00042978"
        ),
    },
    ("application", 0x00046920): {
        "status": "adjudicated_non_function_data",
        "classification_basis": (
            "named DAT_00046920 literal loaded by the instruction at "
            "0x0004690E; the next function begins at 0x00046924"
        ),
    },
    ("application", 0x00046908): {
        "status": "adjudicated_non_function_data",
        "classification_basis": (
            "four-byte word 0x00000052 immediately before the independently "
            "exported 20-byte function at 0x0004690C; the script comment "
            "describes that real timer-cancel function and is off by four bytes"
        ),
    },
    ("application", 0x0004EFF8): {
        "status": "adjudicated_non_function_data",
        "classification_basis": (
            "named DAT_0004EFF8 literal loaded by the instruction at "
            "0x0004EF92 inside the 0x0004EF8C function"
        ),
    },
    ("application", 0x00052090): {
        "status": "adjudicated_non_function_data",
        "classification_basis": (
            "named DAT_00052090 literal loaded by the instruction at "
            "0x0005207C; the next function begins at 0x00052094"
        ),
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strip_java_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return re.sub(r"//[^\r\n]*", "", text)


def parse_array(path: Path, array_name: str) -> list[int]:
    text = strip_java_comments(path.read_text(encoding="utf-8"))
    match = re.search(
        rf"\b{re.escape(array_name)}\b\s*=\s*\{{(?P<body>.*?)\}}\s*;",
        text,
        flags=re.DOTALL,
    )
    if match is None:
        raise ValueError(f"{path}: array {array_name} not found")
    constants = {
        name: int(value, 16)
        for name, value in re.findall(
            r"\bstatic\s+final\s+long\s+([A-Za-z_$][\w$]*)\s*=\s*"
            r"0[xX]([0-9a-fA-F]+)[lL]?\s*;",
            text,
        )
    }
    values: list[int] = []
    for item in match.group("body").split(","):
        token = item.strip()
        if not token:
            continue
        literal = re.fullmatch(r"0[xX]([0-9a-fA-F]+)[lL]?", token)
        if literal is not None:
            values.append(int(literal.group(1), 16))
        elif token in constants:
            values.append(constants[token])
        else:
            raise ValueError(
                f"{path}: unsupported {array_name} entry expression: {token}"
            )
    if not values:
        raise ValueError(f"{path}: array {array_name} contains no hexadecimal entries")
    return values


def load_ownership(path: Path) -> dict[str, list[dict[str, object]]]:
    by_image: dict[str, list[dict[str, object]]] = defaultdict(list)
    with path.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            image = row["image"]
            by_image[image].append(
                {
                    "entry": int(row["entry"], 16),
                    # Some symbol-authentication supplements establish only an
                    # entry point, not a recovered extent.  They can satisfy an
                    # exact census hit but must not cover later addresses.
                    "end": int(row["end"], 16) if row["end"] else int(row["entry"], 16),
                    "size": int(row["size"]) if row["size"] else None,
                    "recovered_name": row["recovered_name"],
                    "provider_family": row["provider_family"],
                    "source_disposition": row["source_disposition"],
                }
            )
    for rows in by_image.values():
        rows.sort(key=lambda row: (int(row["entry"]), int(row["end"])))
    return by_image


def format_address(value: int) -> str:
    return f"0x{value:08X}"


def build_report(ownership_path: Path) -> dict[str, object]:
    ownership = load_ownership(ownership_path)
    provenance: dict[tuple[str, int], list[dict[str, str]]] = defaultdict(list)
    sources: list[dict[str, object]] = []

    for filename, array_name, image in ENTRY_ARRAYS:
        path = SCRIPT_ROOT / filename
        values = parse_array(path, array_name)
        sources.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "array": array_name,
                "image": image,
                "entry_reference_count": len(values),
                "sha256": sha256(path),
            }
        )
        source = {"path": path.relative_to(ROOT).as_posix(), "array": array_name}
        for value in values:
            if source not in provenance[(image, value)]:
                provenance[(image, value)].append(source)

    entries: list[dict[str, object]] = []
    for (image, address), entry_sources in sorted(provenance.items()):
        adjudication = ADJUDICATED_NON_FUNCTIONS.get((image, address))
        exact = [row for row in ownership.get(image, []) if row["entry"] == address]
        bounding = [
            row
            for row in ownership.get(image, [])
            if int(row["entry"]) < address <= int(row["end"])
        ]
        containing = [
            row
            for row in bounding
            if row["size"] is not None and
            int(row["end"]) - int(row["entry"]) + 1 == int(row["size"])
        ]
        if len(exact) > 1:
            raise ValueError(
                f"{image} {format_address(address)} has duplicate exact ownership entries"
            )

        item: dict[str, object] = {
            "image": image,
            "entry": format_address(address),
            "sources": sorted(entry_sources, key=lambda source: (source["path"], source["array"])),
        }
        matches = [] if adjudication is not None else (
            exact if exact else sorted(
                containing if containing else bounding,
                key=lambda row: (
                    int(row["end"]) - int(row["entry"]),
                    int(row["entry"]),
                ),
            )
        )
        match = matches[0] if matches else None
        if image not in ownership:
            item["status"] = "analysis_only_no_ownership_inventory"
        elif exact:
            item["status"] = "exact_ledger_entry"
        elif adjudication is not None:
            item.update(adjudication)
        elif containing:
            item["status"] = "contained_in_contiguous_ledger_extent"
        elif bounding:
            item["status"] = "within_noncontiguous_bounding_range_unproven"
        else:
            item["status"] = "missing_ledger_entry"
        if match is not None:
            item["ledger_entry"] = format_address(int(match["entry"]))
            item["ledger_end"] = format_address(int(match["end"]))
            item["ledger_recovered_name"] = match["recovered_name"]
            item["ledger_provider_family"] = match["provider_family"]
            item["ledger_source_disposition"] = match["source_disposition"]
            if len(matches) > 1:
                item["additional_containing_extents"] = [
                    {
                        "ledger_entry": format_address(int(other["entry"])),
                        "ledger_end": format_address(int(other["end"])),
                        "ledger_recovered_name": other["recovered_name"],
                    }
                    for other in matches[1:]
                ]
        entries.append(item)

    status_counts = defaultdict(int)
    image_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for item in entries:
        status = str(item["status"])
        image = str(item["image"])
        status_counts[status] += 1
        image_counts[image][status] += 1
        image_counts[image]["unique_entry_count"] += 1

    return {
        "schema_version": 2,
        "purpose": "Census and adjudication of function entries explicitly requested or created by curated R1 Ghidra analysis scripts.",
        "image_inventory": {
            "application": {
                "revision": "2.2.6.0009",
                "ownership_inventory_available": True,
            },
            "application_2.2.7.0005": {
                "revision": "2.2.7.0005",
                "ownership_inventory_available": False,
            },
            "bootloader": {
                "revision": "retail_bootloader_from_2.2.6_evidence_set",
                "ownership_inventory_available": True,
            },
        },
        "ownership_ledger": {
            "path": ownership_path.relative_to(ROOT).as_posix(),
            "sha256": sha256(ownership_path),
        },
        "source_count": len(sources),
        "entry_reference_count": sum(int(source["entry_reference_count"]) for source in sources),
        "unique_entry_count": len(entries),
        "status_counts": dict(sorted(status_counts.items())),
        "image_counts": {
            image: dict(sorted(counts.items()))
            for image, counts in sorted(image_counts.items())
        },
        "sources": sources,
        "entries": entries,
    }


def render(report: dict[str, object]) -> str:
    return json.dumps(report, indent=2, sort_keys=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ownership", type=Path, default=DEFAULT_OWNERSHIP)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail unless the checked-in report exactly matches current inputs",
    )
    args = parser.parse_args()

    ownership_path = args.ownership.resolve()
    output_path = args.output.resolve()
    expected = render(build_report(ownership_path))
    if args.check:
        if not output_path.exists() or output_path.read_text(encoding="utf-8") != expected:
            print(
                f"stale Ghidra explicit-entry census: regenerate {output_path}",
                file=sys.stderr,
            )
            return 1
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(expected, encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
