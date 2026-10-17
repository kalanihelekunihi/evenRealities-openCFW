#!/usr/bin/env python3
"""Replay the six Main root stages from the combined corrected archive."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
EARLY = G2 / "build/c-firmware/20261016/main-settings-font-early-replay/receipt.json"
PRIOR = G2 / "build/c-firmware/20261014/main-corrected-archive-root-replay/receipt.json"
OUT = G2 / "build/c-firmware/20261016/main-settings-font-root-replay"
REMOVED = {"audio_uart_ring_secondary_active"}
PROVIDERS = {"audio_uart_font_primary_active", "audio_uart_font_secondary_active"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *options):
    return {row.split()[-1] for row in subprocess.check_output(
        ["arm-none-eabi-nm", *options, str(path)], text=True).splitlines()}


def checked(name, digest):
    path = ROOT / name
    if sha(path) != digest:
        raise RuntimeError("root replay input changed: " + name)
    return path


def link(target, base, objects=(), options=()):
    subprocess.run(["arm-none-eabi-ld", "-r", *options, str(base),
                    *(str(path) for path in objects), "-o", str(target)], check=True)
    return target


def main():
    early, prior = json.loads(EARLY.read_text()), json.loads(PRIOR.read_text())
    if early["status"] != "PASS_EXPERIMENTAL_MAIN_SETTINGS_FONT_EARLY_REPLAY_C" or \
            prior["status"] != "PASS_EXPERIMENTAL_MAIN_CORRECTED_ARCHIVE_ROOT_REPLAY_C":
        raise RuntimeError("root replay evidence status changed")
    current = checked(early["linked_object"], early["linked_object_sha256"])
    OUT.mkdir(parents=True, exist_ok=True)
    stages = []
    for index, row in enumerate(prior["stages"], 1):
        old = checked(row["new_object"], row["new_sha256"])
        inputs = [checked(name, digest) for name, digest in row["inputs"].items()]
        extras = {}
        if row["stage"] == "hci_composed":
            upstream = checked(row["upstream_receipt"], row["upstream_receipt_sha256"])
            intermediate = {Path(name).name: checked(name, digest)
                            for name, digest in json.loads(upstream.read_text())["objects"].items()}
            current = link(OUT / f"{index:02d}-hci-decoder.o", current,
                           [intermediate["refresh-hci-decoders.o"]])
            extras[str(current.relative_to(ROOT))] = sha(current)
            aliases = [f"--defsym={name}={provider}"
                       for name, provider in row["hci_aliases"].items()]
            current = link(OUT / f"{index:02d}-hci-joins.o", current,
                           options=aliases)
            extras[str(current.relative_to(ROOT))] = sha(current)
            current = link(OUT / f"{index:02d}-hci-vendor.o", current,
                           [intermediate["refresh-hci-vendor-complete.o"]])
            extras[str(current.relative_to(ROOT))] = sha(current)
        new = link(OUT / f"{index:02d}-{row['stage']}.o", current, inputs,
                   row["link_options"])
        old_u, new_u = names(old, "-u"), names(new, "-u")
        old_d, new_d = names(old, "-g", "--defined-only"), \
                       names(new, "-g", "--defined-only")
        if old_u - new_u != REMOVED or new_u - old_u or \
                new_d - old_d != PROVIDERS or old_d - new_d:
            raise RuntimeError("font correction not preserved at " + row["stage"])
        stages.append({"stage": row["stage"], "prior_object": row["new_object"],
                       "prior_sha256": sha(old), "inputs": row["inputs"],
                       "link_options": row["link_options"],
                       "intermediate_inputs": row.get("intermediate_objects", {}),
                       "hci_aliases": row.get("hci_aliases", {}),
                       "intermediate_outputs": extras,
                       "new_object": str(new.relative_to(ROOT)),
                       "new_sha256": sha(new),
                       "unresolved_before": len(old_u),
                       "unresolved_after": len(new_u)})
        current = new
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_SETTINGS_FONT_ROOT_REPLAY_C",
               "early_receipt": str(EARLY.relative_to(ROOT)),
               "early_receipt_sha256": sha(EARLY),
               "prior_receipt": str(PRIOR.relative_to(ROOT)),
               "prior_receipt_sha256": sha(PRIOR),
               "stages": stages,
               "linked_object": str(current.relative_to(ROOT)),
               "linked_object_sha256": sha(current),
               "unresolved_after": stages[-1]["unresolved_after"],
               "imports_resolved": sorted(REMOVED),
               "providers_added": sorted(PROVIDERS),
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["Six Main root stages carry the font repair; library, runtime and later feature waves still require replay."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], len(stages), receipt["unresolved_after"], sha(path))


if __name__ == "__main__":
    main()
