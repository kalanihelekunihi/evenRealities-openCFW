#!/usr/bin/env python3
"""Reconcile current six-image C evidence without promoting candidate links to firmware."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
G2 = ROOT / "g2"
BUILD = G2 / "build/c-firmware/20261014"
OUT = G2 / "analysis/c-source-completion-20261011/six-current-20261014.json"
TARGET_SHA = "7312f4b855ff41ec823cc977485a8cc5e59a7235f834880b2217bf1f3ab138ff"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def receipt(path):
    data = json.loads(path.read_text())
    return data, {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def file_checked(name, expected):
    path = ROOT / name
    actual = sha(path)
    if actual != expected:
        raise RuntimeError(f"stale artifact: {name}: {actual}")
    return {"path": name, "sha256": actual}


def undefined(path):
    output = subprocess.check_output(["arm-none-eabi-nm", "-u", str(path)], text=True)
    return sorted({line.split()[-1] for line in output.splitlines()
                   if line.strip() and line.split()[0] == "U"})


def main():
    images = {}
    for directory, name in (("codec-source-refresh", "codec"),
                            ("em9305-source-refresh", "ble_em9305"),
                            ("bootloader-root-refresh", "apollo_bootloader")):
        path = BUILD / directory / "receipt.json"
        data, ref = receipt(path)
        if data["target_sha256"] != TARGET_SHA or data["complete_source_payloads"] != 0:
            raise RuntimeError(f"stale six-image target/source gate: {directory}")
        item = data["images"][name]
        if not item["candidate_compilation_passed"] or item["source_complete"] or item["full_payload_linked"]:
            raise RuntimeError(f"component evidence classification changed: {name}")
        output = BUILD / directory / name / "candidate.o"
        expected = item["relocatable_link"].get("output_sha256", item.get("output_sha256"))
        artifact = file_checked(str(output.relative_to(ROOT)), expected)
        images[name] = {
            "receipt": ref, "candidate": artifact,
            "candidate_compilation_passed": True,
            "recorded_unresolved": item["relocatable_link"]["unresolved_symbols"],
            "source_complete": False, "full_payload_linked": False,
            "remaining_gate": item["source_gates"],
        }
    em_path = BUILD / "em9305-source-refresh/resident-rom-bindings-receipt.json"
    em, em_ref = receipt(em_path)
    if em["unresolved_before"] != 12 or em["unresolved_after"] != 0 or em["whole_image_complete"]:
        raise RuntimeError("EM resident ROM classification changed")
    images["ble_em9305"]["resident_rom_binding"] = {
        "receipt": em_ref,
        "object": file_checked(em["bound_object"], em["bound_object_sha256"]),
        "external_entries": 12, "unresolved_after_external_binding": 0,
    }
    touch_path = BUILD / "touch-default-enum-providers/receipt.json"
    touch, touch_ref = receipt(touch_path)
    if touch["strong_unresolved"] or len(touch["weak_unresolved"]) != 4 or touch["whole_image_complete"]:
        raise RuntimeError("Touch experimental link classification changed")
    images["touch"] = {
        "receipt": touch_ref,
        "candidate": file_checked(touch["linked_object"], touch["linked_object_sha256"]),
        "strong_unresolved": [], "optional_weak_unresolved": touch["weak_unresolved"],
        "lp_history_capacity_proven": False, "source_complete": False,
        "full_payload_linked": False, "remaining_gate": touch["limits"],
    }
    case_path = G2 / "analysis/c-source-completion-20261011/m0/case_current_20261014.elf.receipt.json"
    case, case_ref = receipt(case_path)
    if case["status"] != "EXPERIMENTAL_ABSOLUTE_C_ELF_LINKED" or case["undefined_symbols"]:
        raise RuntimeError("CASE experimental ELF classification changed")
    images["case"] = {
        "receipt": case_ref,
        "experimental_elf": file_checked(case["output"], case["output_sha256"]),
        "experimental_undefined": [], "source_complete": False,
        "full_payload_linked": False, "remaining_gate": case["limits"],
    }
    case_gc_path = G2 / "build/c-firmware/20261015/case-gc-size-frontier/receipt.json"
    case_gc, case_gc_ref = receipt(case_gc_path)
    if (case_gc["status"] != "PASS_EXPERIMENTAL_CASE_GC_SIZE_FRONTIER" or
            case_gc["source_receipt_sha256"] != case_ref["sha256"] or
            case_gc["gc_overflow_bytes"] != 10680 or case_gc["undefined_symbols"]):
        raise RuntimeError("CASE size frontier changed")
    images["case"]["gc_size_frontier"] = {
        "receipt": case_gc_ref,
        "experimental_elf": file_checked(case_gc["gc_elf"], case_gc["gc_elf_sha256"]),
        "stock_payload_bytes": case_gc["stock_payload_bytes"],
        "gc_load_bytes": case_gc["gc_load_bytes"],
        "overflow_bytes": case_gc["gc_overflow_bytes"],
        "native_reset_entry": case_gc["stock_reset_entry"],
        "gc_reset_entry": case_gc["gc_entry"],
    }
    case_reset_path = G2 / "build/c-firmware/20261015/case-gc-size-frontier/reset-size-receipt.json"
    case_reset, case_reset_ref = receipt(case_reset_path)
    if (case_reset["status"] != "PASS_EXPERIMENTAL_CASE_RESET_SIZE_FRONTIER" or
            case_reset["gc_receipt_sha256"] != case_gc_ref["sha256"] or
            case_reset["variants"][-1]["overflow_bytes"] != 10719 or
            len(case_reset["variants"][-1]["matching_vector_words"]) != 13):
        raise RuntimeError("CASE fixed-reset size frontier changed")
    images["case"]["fixed_reset_size_frontier"] = {
        "receipt": case_reset_ref,
        "experimental_elf": file_checked(case_reset["variants"][-1]["elf"],
                                         case_reset["variants"][-1]["elf_sha256"]),
        "entry": case_reset["variants"][-1]["entry"],
        "matching_vector_words": len(case_reset["variants"][-1]["matching_vector_words"]),
        "vector_words": 46,
        "overflow_bytes": case_reset["variants"][-1]["overflow_bytes"],
    }
    case_oz_path = G2 / "build/c-firmware/20261015/case-gc-size-frontier/mixed-oz-receipt.json"
    case_oz, case_oz_ref = receipt(case_oz_path)
    if (case_oz["status"] != "PASS_EXPERIMENTAL_CASE_MIXED_OZ_FIXED_RESET_FRONTIER" or
            case_oz["reset_frontier_receipt_sha256"] != case_reset_ref["sha256"] or
            case_oz["overflow_bytes"] != 7851 or case_oz["native_pointer_leads_present"] != 39):
        raise RuntimeError("CASE mixed -Oz frontier changed")
    images["case"]["mixed_oz_size_frontier"] = {
        "receipt": case_oz_ref,
        "experimental_elf": file_checked(case_oz["elf"], case_oz["elf_sha256"]),
        "load_bytes": case_oz["load_bytes"], "overflow_bytes": case_oz["overflow_bytes"],
        "entry": case_oz["entry"], "matching_vector_words": len(case_oz["matching_vector_words"]),
        "native_pointer_leads_present": case_oz["native_pointer_leads_present"],
    }
    main_path = BUILD / "main-post-tail-c-replay/receipt.json"
    main, main_ref = receipt(main_path)
    if main["status"] != "PASS_EXPERIMENTAL_MAIN_POST_TAIL_C_REPLAY" or main["unresolved_after"] != 232:
        raise RuntimeError("Apollo Main current replay changed")
    main_obj = file_checked(main["linked_object"], main["linked_object_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 232:
        raise RuntimeError("Apollo Main unresolved set changed")
    images["apollo_main"] = {
        "receipt": main_ref, "candidate": main_obj,
        "unresolved_count": len(actual), "unresolved_symbols": actual,
        "source_complete": False, "full_payload_linked": False,
        "remaining_gate": ["232 current imports need source ownership or attributed external contracts.",
                           "Complete data/startup/layout and physical execution remain unproved."],
    }
    if set(images) != {"codec", "ble_em9305", "touch", "case", "apollo_bootloader", "apollo_main"}:
        raise RuntimeError("six-image set changed")
    record = {
        "status": "PASS_EXPERIMENTAL_SIX_CURRENT_C_EVIDENCE_AUDIT",
        "target_id": "official-s200-v2.2.6.10", "target_sha256": TARGET_SHA,
        "images": images, "complete_source_payloads": 0,
        "limits": ["Each row is a separately qualified candidate or experimental object, not one unified final build.",
                   "Zero imports or an experimental ELF does not prove source coverage, stock layout, or hardware operation."],
    }
    OUT.write_text(json.dumps(record, indent=2) + "\n")
    print(record["status"], len(images), record["complete_source_payloads"], sha(OUT))


if __name__ == "__main__":
    main()
