#!/usr/bin/env python3
"""Find already written C provider definitions for the current Main imports."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OBJ = ROOT / "g2/build/c-firmware/20261017/main-conn-param-profiles/candidate.o"
OUT = ROOT / "g2/analysis/c-source-completion-20261011/apollo/main-unresolved-provider-sources-20261016.json"


def main():
    names = sorted({line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(OBJ)], text=True).splitlines() if line.strip()})
    if len(names) != 83:
        raise RuntimeError(f"current Main import count changed: {len(names)}")
    sources = list((ROOT / "g2/components").rglob("*.c"))
    definitions = {}
    for path in sources:
        data = path.read_text(errors="replace")
        for name in names:
            if name not in data:
                continue
            # This finds ordinary global function bodies, not macros or generated providers.
            pattern = rf"(?m)^\s*(?!extern\b|static\b)[A-Za-z_][\w \t*]*\b{re.escape(name)}\s*\([^;]*\)\s*\{{"
            if re.search(pattern, data):
                definitions.setdefault(name, []).append(str(path.relative_to(ROOT)))
    record = {
        "status": "PASS_MAIN_CURRENT_IMPORT_PROVIDER_SOURCE_INVENTORY",
        "candidate_object": str(OBJ.relative_to(ROOT)),
        "candidate_sha256": hashlib.sha256(OBJ.read_bytes()).hexdigest(),
        "unresolved_count": len(names), "unresolved_symbols": names,
        "exact_global_function_definitions": definitions,
        "scope": "g2/components/**/*.c ordinary global function definitions",
        "limits": ["No exact definition does not exclude a provider under another name or generated source.",
                   "Data objects, C aliases, and functions outside the scanned component tree need separate review.",
                   "This inventory is a search result, not source completeness or executable behavior."],
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(names), len(definitions), hashlib.sha256(OUT.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
