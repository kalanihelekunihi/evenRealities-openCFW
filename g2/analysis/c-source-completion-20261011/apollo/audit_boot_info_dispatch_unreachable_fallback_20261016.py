#!/usr/bin/env python3
"""Prove the two unvisited INFO dispatch fallback instructions are unreachable."""
import hashlib
import json
from pathlib import Path

from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
PRIOR = G2 / "build/c-firmware/20261016/boot-info-dispatch-4213e6/receipt.json"
OUT = G2 / "build/c-firmware/20261016/boot-info-dispatch-fallback"
PIN = "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = STOCK.read_bytes()
    prior = json.loads(PRIOR.read_text())
    if sha(STOCK) != PIN or prior["stock_sha256"] != PIN or \
            prior["unvisited_stock_bytes"] != ["0x42149c", "0x42149d", "0x421532", "0x421533"]:
        raise RuntimeError("boot INFO baseline changed")
    instructions = {i.address: (i.mnemonic, i.op_str, i.bytes.hex())
                    for i in Cs(CS_ARCH_ARM, CS_MODE_THUMB).disasm(
                        blob[0x4213e6-0x410000:0x421548-0x410000], 0x4213e6)}
    expected = {
        0x42141e: ("movs", "r7, r6"),
        0x421420: ("uxtb", "r7, r7"),
        0x421422: ("cmp", "r7, #0"),
        0x421424: ("beq", "#0x421438"),
        0x421426: ("cmp", "r7, #2"),
        0x421428: ("beq", "#0x421456"),
        0x42142a: ("blo", "#0x421462"),
        0x42142c: ("cmp", "r7, #4"),
        0x42142e: ("beq", "#0x42145c"),
        0x421430: ("blo", "#0x421476"),
        0x421432: ("cmp", "r7, #5"),
        0x421434: ("beq", "#0x42147c"),
        0x421436: ("b", "#0x421482"),
        0x421482: ("movs", "r0, #6"),
        0x421484: ("b", "#0x421544"),
        0x421486: ("uxtb", "r6, r6"),
        0x421488: ("cmp", "r6, #0"),
        0x42148a: ("beq", "#0x42149e"),
        0x42148c: ("cmp", "r6, #2"),
        0x42148e: ("beq", "#0x4214f4"),
        0x421490: ("blo", "#0x4214cc"),
        0x421492: ("cmp", "r6, #4"),
        0x421494: ("beq", "#0x421520"),
        0x421496: ("blo", "#0x42150a"),
        0x421498: ("cmp", "r6, #5"),
        0x42149a: ("beq", "#0x42152a"),
        0x42149c: ("b", "#0x421532"),
        0x421532: ("movs", "r5, #6"),
    }
    for address, pair in expected.items():
        if instructions.get(address, ())[:2] != pair:
            raise RuntimeError(f"INFO dispatch instruction changed at {address:#x}: {instructions.get(address)}")
    # The only second-stage fallback requires unsigned selector >= 6. The
    # first stage routes every such value to status 6 and return. Between
    # stages only UXTB writes r6, preserving its selected low byte.
    result = {"status": "PASS_STOCK_BOOT_INFO_DISPATCH_FALLBACK_UNREACHABLE",
              "stock_sha256": PIN, "prior_oracle": str(PRIOR.relative_to(ROOT)),
              "prior_oracle_sha256": sha(PRIOR), "source_body_range": ["0x4213e6", "0x421548"],
              "selector_domain_after_first_gate": [0, 1, 2, 3, 4, 5],
              "unvisited_instruction_addresses": ["0x42149c", "0x421532"],
              "unvisited_bytes_classification": "unreachable after first selector gate",
              "pinned_instructions": {hex(k): [*v[:2], v[2]] for k, v in instructions.items()
                                      if k in expected},
              "source_complete": False, "hardware_proof": False,
              "limits": ["This is a pinned static control-flow proof for the four unvisited stock bytes.",
                         "Resident ROM, production M55, MMIO timing and full boot image remain open."]}
    OUT.mkdir(parents=True, exist_ok=True)
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(receipt))


if __name__ == "__main__":
    main()
