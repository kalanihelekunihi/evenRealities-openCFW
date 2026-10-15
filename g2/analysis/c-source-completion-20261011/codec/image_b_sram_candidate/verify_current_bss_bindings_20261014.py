#!/usr/bin/env python3
"""Bind authenticated CRT limits in a current experimental image-B object.

This is a relocatable-link check, not a final layout or loadable firmware.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
TOOL = ROOT / "g2/build/offline-nationalchip-dsp-c-compiler-successor-20261009T195245Z/toolchain"
BOUNDS = {"gx8002_image_b_bss_start": 0x20017090,
          "gx8002_image_b_bss_end": 0x2002d79c}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(out, program, *args):
    cmd = ["docker", "run", "--rm", "--network=none", "--read-only",
           "--platform", "linux/amd64",
           "--mount", f"type=bind,src={TOOL},dst=/tool,readonly",
           "--mount", f"type=bind,src={ROOT},dst=/repo,readonly",
           "--mount", f"type=bind,src={out},dst=/out",
           "--tmpfs", "/tmp:rw", "opencfw/iar-base:10.10.2-local",
           f"/tool/bin/csky-abiv2-elf-{program}", *args]
    return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    receipt = json.loads(args.source_receipt.read_text())
    if not receipt["sample_app_experiment"] or receipt["sample_app_callbacks_qualified"]:
        raise RuntimeError("expected the unqualified sample-app source experiment")
    if sorted(receipt["undefined_symbols"]) != sorted(BOUNDS):
        raise RuntimeError("unexpected source imports")
    if len(receipt["units"]) != 319:
        raise RuntimeError("source graph changed; review boundaries before binding")
    for unit in receipt["units"]:
        if sha(ROOT / unit["source"]) != unit["source_sha256"]:
            raise RuntimeError(f"source drift: {unit['source']}")
        if sha(Path(unit["object"])) != unit["object_sha256"]:
            raise RuntimeError(f"object drift: {unit['object']}")
    source = Path(receipt["linked_object"])
    if sha(source) != receipt["linked_object_sha256"]:
        raise RuntimeError("linked object drift")
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    bound = out / "image_b_bss_bound.o"
    relative = source.resolve().relative_to(ROOT)
    defs = [f"--defsym={name}=0x{value:08x}" for name, value in BOUNDS.items()]
    run(out, "ld", "-r", *defs, "-o", "/out/" + bound.name,
        "/repo/" + str(relative))
    undefined = run(out, "nm", "-u", "/out/" + bound.name).strip()
    if undefined:
        raise RuntimeError(f"bound object retains imports: {undefined}")
    symbols = run(out, "nm", "/out/" + bound.name)
    for name, address in BOUNDS.items():
        if f"{address:08x} A {name}" not in symbols:
            raise RuntimeError(f"bound address mismatch: {name}")
    result = {
        "status": "PASS_EXPERIMENTAL_IMAGE_B_BSS_BINDINGS",
        "source_receipt": str(args.source_receipt.resolve().relative_to(ROOT)),
        "source_receipt_sha256": sha(args.source_receipt),
        "source_units": len(receipt["units"]),
        "boundaries": {name: hex(address) for name, address in BOUNDS.items()},
        "bound_object": str(bound.relative_to(ROOT)),
        "bound_object_sha256": sha(bound),
        "undefined_symbols": [],
        "source_complete": False,
        "final_layout_proven": False,
        "callbacks_qualified": False,
        "bootable": False,
    }
    path = out / "bss-bindings-receipt.json"
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(path)


if __name__ == "__main__":
    main()
