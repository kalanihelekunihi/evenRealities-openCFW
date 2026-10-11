#!/usr/bin/env python3
"""Census external imports and historical linker bindings without executing them."""
import collections
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
ARCHIVE = Path(sys.argv[1]).resolve()
OUTPUT = Path(sys.argv[2]).resolve()
OUTPUT.mkdir(parents=True, exist_ok=True)
nm = subprocess.check_output(["arm-none-eabi-nm", "-g", "-P", str(ARCHIVE)], text=True)
defined = collections.defaultdict(list)
undefined = collections.Counter()
member = None
for line in nm.splitlines():
    if line.endswith(":"):
        member = line.split("[")[-1].rstrip("]: ")
        continue
    fields = line.split()
    if len(fields) < 2:
        continue
    name, kind = fields[:2]
    if kind == "U":
        undefined[name] += 1
    elif kind.upper() in "TDBRCAWVS":
        defined[name].append(member)
missing = sorted(undefined.keys() - defined.keys())
census = {"defined_global_unique": len(defined),
          "undefined_global_unique_raw": len(undefined),
          "unresolved_global_unique": len(missing),
          "duplicate_global_definitions": {n: m for n, m in defined.items() if len(m) > 1},
          "unresolved_symbols": missing}
(OUTPUT / "provider-census.json").write_text(json.dumps(census, indent=2) + "\n")

bindings = collections.defaultdict(lambda: collections.defaultdict(list))
receipts = sorted((ROOT / "g2/analysis").glob("audio-*/**/*receipt*.json"))
for receipt in receipts:
    content = receipt.read_text(errors="replace")
    for name, target in re.findall(r"\b([A-Za-z_]\w*)\s*=\s*(0x[0-9A-Fa-f]+|[0-9]{6,8}|[A-Za-z_]\w*)\s*;", content):
        if name in missing:
            bindings[name][target.lower()].append(str(receipt.relative_to(ROOT)))
address_map = {name: dict(targets) for name, targets in sorted(bindings.items())}
(OUTPUT / "import-address-map.json").write_text(json.dumps(address_map, indent=2) + "\n")
direct_address = {n for n, targets in bindings.items()
                  if any(t.startswith("0x") or t.isdecimal() for t in targets)}
alias_only = {n for n in bindings if n not in direct_address}
unmapped = set(missing) - set(bindings)
conflicts = {n: list(targets) for n, targets in bindings.items() if len(targets) > 1}
numeric_conflicts = {n: sorted(t for t in targets if t.startswith("0x") or t.isdecimal())
                     for n, targets in bindings.items()
                     if sum(t.startswith("0x") or t.isdecimal() for t in targets) > 1}
callback_names = [n for n in missing if re.search(r"callback|_cb$|_handler$|_isr$|_hook$", n, re.I)]
coverage = {"unresolved_global_names": len(missing), "receipt_files_scanned": len(receipts),
            "with_direct_numeric_binding": len(direct_address),
            "with_alias_only_binding": len(alias_only), "without_receipt_binding": len(unmapped),
            "without_receipt_binding_names": sorted(unmapped),
            "conflicting_binding_names": conflicts,
            "conflicting_numeric_binding_names": numeric_conflicts,
            "callback_or_handler_named_subset": callback_names,
            "callback_or_handler_named_count": len(callback_names)}
(OUTPUT / "import-coverage.json").write_text(json.dumps(coverage, indent=2) + "\n")
print(json.dumps({k: v for k, v in coverage.items() if isinstance(v, int)}, indent=2))
