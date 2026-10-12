#!/usr/bin/env python3
"""Conservative selected-source versus locked catalogue address crosswalk.

Address mentions are candidate leads, never evidence of semantic equivalence.
"""
import json
import pathlib
import re
import glob
import subprocess
import os

ROOT = pathlib.Path(__file__).resolve().parents[4]
CATALOGUE = ROOT / "g2/research/corpus/apollo-bootloader/ghidra/open-2026-09-29"
BUILD = pathlib.Path(os.environ.get("BOOT_INVENTORY", str(
    ROOT / "g2/build/bootloader-source-candidate-20261011-apollo-all-owned-asm/inventory.json")))
OUTPUT = pathlib.Path(os.environ.get("BOOT_CROSSWALK_OUTPUT", str(
    pathlib.Path(__file__).with_name("boot-body-crosswalk.json"))))
if not BUILD.is_absolute():
    BUILD = ROOT / BUILD
if not OUTPUT.is_absolute():
    OUTPUT = ROOT / OUTPUT


def main():
    inventory = json.loads(BUILD.read_text())
    catalogue = [json.loads(line) for line in (CATALOGUE / "functions-000.jsonl").open()]
    sources = []
    comments = []
    for unit in inventory["units"]:
        if unit["status"] == "selected":
            path = ROOT / unit["source"]
            source = path.read_text(errors="replace")
            sources.append((unit["source"], source))
            comments.append((unit["source"], "\n".join(re.findall(
                r"/\*[\s\S]*?\*/|//[^\n]*", source))))
    providers = inventory["global_weak_providers"]
    selected_paths = {path for path, _ in sources}
    receipt_leads = {}
    locked_hash = json.loads((CATALOGUE / "RUN.json").read_text())["image_sha256"]
    for receipt_path in glob.glob(str(ROOT / "g2/analysis/**/*function-provenance.json"), recursive=True):
        receipt = json.loads(pathlib.Path(receipt_path).read_text())
        if receipt.get("original_sha256", receipt.get("image_sha256")) != locked_hash:
            continue
        source = receipt.get("source")
        if source not in selected_paths:
            continue
        for function in receipt.get("functions", []):
            address = function.get("start", function.get("entry"))
            if address:
                receipt_leads.setdefault(int(address, 16), []).append(source)
    for receipt_path in glob.glob(str(ROOT / "g2/analysis/**/mapped-functions.json"), recursive=True):
        for function in json.loads(pathlib.Path(receipt_path).read_text()):
            source = function.get("source_path")
            address = function.get("original_address_start")
            if source in selected_paths and isinstance(address, int):
                receipt_leads.setdefault(address, []).append(source)
    manual = json.loads(pathlib.Path(__file__).with_name("manual_body_bindings.json").read_text())
    assert manual["locked_image_sha256"] == locked_hash
    manual_leads = {int(row["entry"], 16): row for row in manual["bindings"]
                    if row["source"] in selected_paths and
                    row["symbol"] in providers and
                    providers[row["symbol"]]["source"] == row["source"]}
    littlefs = json.loads(pathlib.Path(__file__).with_name("littlefs_static_bindings.json").read_text())
    assert littlefs["locked_image_sha256"] == locked_hash
    littlefs_unit = next(unit for unit in inventory["units"]
                         if unit["source"] == littlefs["selected_source"] and
                         unit["status"] == "selected")
    nm = subprocess.run(["arm-none-eabi-nm", "-a", str(BUILD.parent / littlefs_unit["object"])],
                        check=True, capture_output=True, text=True).stdout
    compiled_static = {match.group(1) for match in re.finditer(
        r"^[0-9a-fA-F]+\s+[tT]\s+(lfs_[A-Za-z0-9_]+)$", nm, re.M)}
    static_leads = {int(row["entry"], 16): row for row in littlefs["bindings"]
                    if row["symbol"] in compiled_static}
    source_text = (ROOT / littlefs["selected_source"]).read_text()
    static_definition_leads = {int(row["entry"], 16): row for row in littlefs["bindings"]
        if row["symbol"] not in compiled_static and re.search(
            r"\b" + re.escape(row["symbol"]) + r"\s*\([^;]*\)\s*\{",
            source_text, re.S)}
    other_static = json.loads(pathlib.Path(__file__).with_name("selected_static_bindings.json").read_text())
    assert other_static["locked_image_sha256"] == locked_hash
    other_static_leads = {}
    for row in other_static["bindings"]:
        assert row["source"] in selected_paths
        assert re.search(r"\bstatic\s+[^{;]+\b" + re.escape(row["symbol"]) +
                         r"\s*\([^;]*\)\s*\{", (ROOT / row["source"]).read_text(), re.S)
        unit = next(unit for unit in inventory["units"] if unit["source"] == row["source"])
        symbols = subprocess.run(["arm-none-eabi-nm", "-a", str(BUILD.parent / unit["object"])],
                                 check=True, capture_output=True, text=True).stdout
        row = dict(row)
        row["emitted"] = bool(re.search(r"^[0-9a-fA-F]+\s+t\s+" +
                                        re.escape(row["symbol"]) + r"$", symbols, re.M))
        other_static_leads[int(row["entry"], 16)] = row
    rows = []
    for function in catalogue:
        entry = function["entry"].lower()
        short = entry.lstrip("0")
        provider = "opencfw_provider_" + short
        pattern = re.compile(r"(?<![0-9a-f])(?:0x)?" + short + r"(?![0-9a-f])", re.I)
        header = [path for path, source in sources if pattern.search(source[:500]) or
                  any(marker + short in source[:500].lower()
                      for marker in ("locked", "stock", "original"))]
        name = function["name"]
        named = ([path for path, source in sources
                  if re.search(r"\b" + re.escape(name) + r"\s*\(", source)]
                 if not name.startswith("FUN_") else [])
        normalized_name = re.sub(r"_[0-9a-f]{6,8}$", "", name)
        native_named = ([path for path, source in sources if re.search(
            r"\b" + re.escape(normalized_name) +
            r"(?:_[0-9a-f]{6,8})?_native\s*\(", source)]
            if normalized_name != name and not name.startswith("FUN_") else [])
        comment = [path for path, source in comments if pattern.search(source)]
        if provider in providers:
            status = "exact_entry_provider_name"
            leads = [providers[provider]["source"]]
        elif int(entry, 16) in manual_leads:
            status = "reviewed_manual_source_lead"
            leads = [manual_leads[int(entry, 16)]["source"]]
        elif int(entry, 16) in static_leads:
            status = "reviewed_selected_static_function_lead"
            leads = [littlefs["selected_source"] + "::" + static_leads[int(entry, 16)]["symbol"]]
        elif int(entry, 16) in static_definition_leads:
            status = "reviewed_selected_static_definition_inlined_or_optimized_lead"
            leads = [littlefs["selected_source"] + "::" +
                     static_definition_leads[int(entry, 16)]["symbol"]]
        elif int(entry, 16) in other_static_leads:
            row = other_static_leads[int(entry, 16)]
            status = ("reviewed_selected_static_function_lead" if row["emitted"] else
                      "reviewed_selected_static_definition_inlined_or_optimized_lead")
            leads = [row["source"] + "::" + row["symbol"]]
        elif header:
            status = "selected_source_header_address_lead"
            leads = header
        elif int(entry, 16) in receipt_leads:
            status = "selected_source_receipt_address_lead"
            leads = receipt_leads[int(entry, 16)]
        elif named:
            status = "selected_source_function_name_lead"
            leads = named
        elif native_named:
            status = "selected_source_normalized_name_lead"
            leads = native_named
        elif comment:
            status = "selected_source_comment_address_lead"
            leads = comment
        else:
            status = "no_machine_crosswalk"
            leads = []
        rows.append({"entry": "0x" + entry, "name": name,
                     "body_bytes": function["body_bytes"],
                     "raw_pseudocode": (CATALOGUE / "decomp" / (entry + ".c")).is_file(),
                     "status": status, "selected_source_leads": leads})
    counts = {key: sum(row["status"] == key for row in rows) for key in
              sorted({row["status"] for row in rows})}
    result = {
        "catalogue": str((CATALOGUE / "functions-000.jsonl").relative_to(ROOT)),
        "locked_image_sha256": locked_hash,
        "selected_inventory": str(BUILD.relative_to(ROOT)),
        "catalogue_function_count": len(rows),
        "raw_pseudocode_count": sum(row["raw_pseudocode"] for row in rows),
        "raw_pseudocode_absent_count": sum(not row["raw_pseudocode"] for row in rows),
        "crosswalk_counts": counts,
        "limitations": [
            "A provider address name identifies an authored entry but does not prove semantic or image-layout equivalence.",
            "Header address and function-name matches are leads, not confirmed body mappings.",
            "No-machine-crosswalk means unresolved attribution, not proven absent C implementation.",
            "The catalogue contains recognized functions only, not a validated whole-image code/data partition."
        ],
        "functions": rows,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"catalogue": len(rows), "raw_pseudocode": result["raw_pseudocode_count"],
                      "raw_absent": result["raw_pseudocode_absent_count"], "crosswalk": counts}))


if __name__ == "__main__":
    main()
