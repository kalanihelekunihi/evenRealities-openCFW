#!/usr/bin/env python3
"""Rank unattributed native Boot bodies by calls from linked, identified source.

This is a prioritization aid. A native call from an attributed entry does not
establish that the corresponding source path executes or is semantically equal.
"""
import collections
import json
import os
import pathlib
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
crosswalk = json.loads((HERE / "boot-body-crosswalk-current.json").read_text())
native = [json.loads(line) for line in (ROOT / crosswalk["catalogue"]).open()]
by_address = {int(row["entry"], 16): row for row in crosswalk["functions"]}
manual = {int(row["entry"], 16): row for row in
          json.loads((HERE / "manual_body_bindings.json").read_text())["bindings"]}
elf = pathlib.Path(os.environ.get("BOOT_ELF", str(HERE / "boot-coplacement-locale/boot.elf"))).resolve()
symbols = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(elf)], text=True)
linked = {line.split()[-1] for line in symbols.splitlines() if len(line.split()) >= 3}


def linked_entry(row):
    address = int(row["entry"], 16)
    status = by_address[address]["status"]
    if status == "exact_entry_provider_name":
        return "opencfw_provider_" + row["entry"].lstrip("0") in linked
    if status == "reviewed_manual_source_lead" and address in manual:
        return manual[address]["symbol"] in linked
    return False


references = collections.defaultdict(list)
for caller in native:
    for callee in caller["callees"]:
        try:
            address = int(str(callee), 16)
        except ValueError:
            continue
        if address in by_address:
            references[address].append(caller)

frontier = []
for function in native:
    address = int(function["entry"], 16)
    cross = by_address[address]
    if cross["status"] != "no_machine_crosswalk":
        continue
    callers = references[address]
    linked_callers = [row for row in callers if linked_entry(row)]
    frontier.append({
        "entry": "0x" + function["entry"],
        "native_name": function["name"],
        "body_bytes": function["body_bytes"],
        "native_direct_callers": ["0x" + row["entry"] for row in callers],
        "linked_identified_source_caller_leads": ["0x" + row["entry"] for row in linked_callers],
    })
frontier.sort(key=lambda row: (-len(row["linked_identified_source_caller_leads"]),
                               -len(row["native_direct_callers"]), -row["body_bytes"]))
result = {
    "locked_image_sha256": crosswalk["locked_image_sha256"],
    "source_elf": str(elf.relative_to(ROOT)),
    "catalogue_entries": len(native),
    "entries_with_source_attribution_leads": len(native) - len(frontier),
    "entries_without_machine_crosswalk": len(frontier),
    "unattributed_entries_with_linked_identified_caller_lead": sum(bool(row["linked_identified_source_caller_leads"]) for row in frontier),
    "unattributed_entries_without_linked_identified_caller_lead": sum(not row["linked_identified_source_caller_leads"] for row in frontier),
    "limits": [
        "The catalogue recognizes functions but does not establish complete firmware code extents.",
        "A linked identified source caller and a native call edge together prioritize review; they do not prove source reachability or missing implementation.",
        "Crosswalk source leads are candidate attribution, not whole-body equivalence.",
    ],
    "frontier": frontier,
}
output = HERE / "boot-native-frontier-current.json"
output.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({key: result[key] for key in (
    "catalogue_entries", "entries_with_source_attribution_leads",
    "entries_without_machine_crosswalk",
    "unattributed_entries_with_linked_identified_caller_lead",
    "unattributed_entries_without_linked_identified_caller_lead")}))
