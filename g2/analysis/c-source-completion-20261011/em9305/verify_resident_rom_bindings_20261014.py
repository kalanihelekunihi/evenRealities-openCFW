#!/usr/bin/env python3
"""Bind native-observed resident ROM calls in the current ARC C candidate."""
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/em9305-source-refresh"
ARC = OUT / "ble_em9305"
BASE_RECEIPT = OUT / "receipt.json"
BASE = ARC / "candidate.o"
BOUND = ARC / "candidate-resident-rom-bound.o"
CONFIG_PATH = G2 / "firmware_c/arc-toolchain.json"
BINDING_PATH = G2 / "components/em9305/qpc_scheduler_candidate/resident_rom_bindings.json"
RECEIPT = OUT / "resident-rom-bindings-receipt.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    base = json.loads(BASE_RECEIPT.read_text())
    image = base["images"]["ble_em9305"]
    assert image["candidate_compilation_passed"]
    assert image["arc_em_target_attributes_verified"]
    assert image["relocatable_link"]["returncode"] == 0
    config = json.loads(CONFIG_PATH.read_text())
    tool = ROOT / config["tool_path"]
    compiler = tool / "bin/arc-elf32-gcc"
    assert sha(compiler) == config["compiler_sha256"] == image["compiler_sha256"]
    assert sha(BASE) == image["relocatable_link"]["output_sha256"]
    spec = json.loads(BINDING_PATH.read_text())
    bindings = spec["bindings"]
    assert len(bindings) == 12
    assert set(bindings) == set(image["relocatable_link"]["unresolved_symbols"])
    listings = {}
    for name, address in bindings.items():
        assert name.endswith("_" + address.removeprefix("0x"))
        path = ROOT / spec["native_listings"][address]
        data = path.read_text(errors="replace")
        pattern = r"\bbl(?:\.d)?\b[^\n]*;0x" + address.removeprefix("0x") + r"\b"
        assert re.search(pattern, data), (name, path)
        listings[str(path.relative_to(ROOT))] = sha(path)
    docker = shutil.which("docker")
    assert docker
    prefix = [docker, "run", "--rm", "--network=none", "--read-only",
              "--platform", "linux/amd64", "--mount",
              f"type=bind,src={tool},dst=/tool,readonly", "--mount",
              f"type=bind,src={ROOT},dst=/repo,readonly", "--mount",
              f"type=bind,src={ARC},dst=/out", "--tmpfs", "/tmp:rw",
              config["runtime_image"]]
    def arc_tool(name, *args):
        return subprocess.check_output(prefix + ["/tool/bin/arc-elf32-" + name,
                                                 *args], text=True)
    before = {line.split()[-1] for line in arc_tool("nm", "-u", "/out/candidate.o").splitlines()}
    assert before == set(bindings)
    arguments = ["-r"] + ["--defsym=" + name + "=" + address
                          for name, address in sorted(bindings.items())]
    arc_tool("ld", *arguments, "/out/candidate.o", "-o",
             "/out/candidate-resident-rom-bound.o")
    after = arc_tool("nm", "-u", "/out/candidate-resident-rom-bound.o")
    assert not after.strip()
    defined = {}
    for line in arc_tool("nm", "-g", "--defined-only",
                         "/out/candidate-resident-rom-bound.o").splitlines():
        fields = line.split()
        if len(fields) == 3:
            defined[fields[2]] = (int(fields[0], 16), fields[1])
    for name, address in bindings.items():
        assert defined[name] == (int(address, 16), "A"), name
    attrs = arc_tool("readelf", "-h", "-A", "/out/candidate-resident-rom-bound.o")
    assert "Tag_ARC_CPU_base: ARCEM" in attrs
    receipt = {
        "status": "PASS_EXPERIMENTAL_EM9305_RESIDENT_ROM_BINDINGS",
        "base_receipt": str(BASE_RECEIPT.relative_to(ROOT)),
        "base_receipt_sha256": sha(BASE_RECEIPT),
        "binding_spec": str(BINDING_PATH.relative_to(ROOT)),
        "binding_spec_sha256": sha(BINDING_PATH),
        "native_listing_sha256": listings,
        "compiler_sha256": sha(compiler),
        "base_object": str(BASE.relative_to(ROOT)), "base_object_sha256": sha(BASE),
        "bound_object": str(BOUND.relative_to(ROOT)), "bound_object_sha256": sha(BOUND),
        "bindings": bindings,
        "unresolved_before": len(before), "unresolved_after": 0,
        "arc_em_target_attributes_verified": True,
        "whole_image_complete": False, "hardware_proof": False,
        "gates": ["These are external resident-ROM entry addresses observed in registered native listings; no ROM body was reconstructed or executed.",
                  "Controller source coverage, product data and record layout, reset path, final placement and physical behavior remain open."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), sha(RECEIPT))


if __name__ == "__main__":
    main()
