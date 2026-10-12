#!/usr/bin/env python3
"""Recompile source-bound non-suffix XIP units with the selected target flags at Os."""

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
READELF = ROOT / "g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin/csky-elfabiv2-readelf"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def section_sizes(path):
    output = subprocess.run([str(READELF), "-SW", str(path)], check=True, capture_output=True, text=True).stdout
    values = {}
    for line in output.splitlines():
        found = re.search(r"^\s*\[\s*\d+\]\s+(\.text\S*)\s+PROGBITS\s+[0-9a-f]+\s+[0-9a-f]+\s+([0-9a-f]+)", line)
        if found:
            values[found[1]] = int(found[2], 16)
    return values


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-receipt", required=True, type=Path)
    parser.add_argument("--eligibility", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    image = json.loads(args.build_receipt.read_text())["images"]["codec"]
    eligibility = json.loads(args.eligibility.read_text())
    source_paths = sorted({slot["source_binding"]["candidate_source"]
                           for slot in eligibility["native_function_slots"]
                           if slot["placement_status"] == "no_direct_named_symbol" and slot["source_binding"]})
    commands = image["build_commands"]
    rows = []
    for source in source_paths:
        matches = [row for row in commands if "/repo/" + source in row["argv"]]
        assert len(matches) == 1, (source, len(matches))
        original = matches[0]["argv"]
        old_output = next(value for value in original if value.startswith("type=bind,src=") and value.endswith(",dst=/out"))
        adapted = [value.replace("-O2", "-Os") if value == "-O2" else
                   f"type=bind,src={args.output.resolve()},dst=/out" if value == old_output else value
                   for value in original]
        assert "-Os" in adapted
        old_object_name = original[original.index("-o") + 1].removeprefix("/out/")
        old_object = ROOT / "g2/build/c-firmware/20261011/codec-fenv-shift-coherent-round/codec" / old_object_name
        new_object = args.output / old_object_name
        assert old_object.is_file()
        outcome = subprocess.run(adapted, capture_output=True, text=True)
        assert outcome.returncode == 0, (source, outcome.stderr[-1000:])
        o2 = section_sizes(old_object)
        os = section_sizes(new_object)
        direct_sections = [symbol["section"] for slot in eligibility["native_function_slots"]
                           if slot["source_binding"] and slot["source_binding"]["candidate_source"] == source
                           for symbol in slot["direct_symbols"]]
        # No direct native-bound section may grow into an unprobed overflow.
        newly_grown = [name for name in direct_sections if os.get(name, 0) > o2.get(name, 0)]
        rows.append({"source": source, "source_sha256": sha(ROOT / source),
                     "O2_object_sha256": sha(old_object), "Os_object_sha256": sha(new_object),
                     "O2_text_section_bytes": sum(o2.values()), "Os_text_section_bytes": sum(os.values()),
                     "direct_native_sections": direct_sections, "direct_sections_grown": newly_grown})
    result = {"build_receipt_sha256": sha(args.build_receipt), "eligibility_sha256": sha(args.eligibility),
              "target": "C-SKY CK804EF hard-float, selected flags with O2 changed to Os",
              "source_count": len(rows), "O2_text_bytes_sum": sum(row["O2_text_section_bytes"] for row in rows),
              "Os_text_bytes_sum": sum(row["Os_text_section_bytes"] for row in rows),
              "rows": rows,
              "limits": ["Object text sums include all functions in each selected source, not only a native-bound function.",
                         "Section size is not native behavior equality or final XIP placement.",
                         "Any source file with a grown direct section needs separate fixed-slot review before policy admission."]}
    (args.output / "receipt.json").write_text(json.dumps(result, indent=2) + "\n")
    print({key: result[key] for key in ("source_count", "O2_text_bytes_sum", "Os_text_bytes_sum")})


if __name__ == "__main__":
    main()
