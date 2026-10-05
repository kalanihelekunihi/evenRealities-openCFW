#!/usr/bin/env python3
"""Verify three bounded Apollo GPIO IRQ bodies and their selected consumer."""
import hashlib
import json
import re
import struct
from pathlib import Path

if not __debug__:
    raise SystemExit("run with assertions enabled")

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
BASE = 0x438000
OTA = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
GH = ROOT / "g2/research/corpus/apollo-main/ghidra/open-2026-09-29"
UP = ROOT / "g2/build/foundation/ambiq-upstream"

TARGETS = {
    0x481574: (126, "44ef85302249c0f2479542c1367427676b4d28807779c83655a65c17504f88e5"),
    0x4815F2: (58, "e1a650a0b76b4b7d1a07f3f8f895e6c6daf2f058afe4498d97ac1b7c2c7da29c"),
    0x4816C6: (116, "8cd8748a19317a5bbc241ec3cfd761d57060af842509910b05b8e42e3b4601b1"),
    0x4B80BE: (44, "853386f3b04b6575390704f2a8a5defabe043bcf472e4dc6487b83ca973ae685"),
    0x48162C: (154, "1e72c952159ac238606b02497a87e287fb939f7dacba6225669c8976b529ca5b"),
    0x4B48A6: (296, "6521b6ef083e2d005e890c922bcd93b2271e7d256b0543e2471f5e797cda09bd"),
}
LITERALS = {
    0x481768: 0x40010530,  # MCUN0INT0EN
    0x4817A0: 0x40010534,  # MCUN0INT0STAT
    0x4817D8: 0x40010538,  # MCUN0INT0CLR
    0x481810: 0x20068228,  # per-IRQ handler table
    0x481814: 0x20068928,  # per-IRQ argument table
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


ota = OTA.read_bytes()
image = ota[32:]
assert len(ota) == 3523396 and sha(ota) == "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
assert len(image) == 3523364 and sha(image) == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
run = json.loads((GH / "RUN.json").read_text())
assert run["base"] == "0x00438000" and run["image_sha256"] == sha(image)
records = [json.loads(line) for line in (GH / "functions-000.jsonl").read_text().splitlines() if line.strip()]
by_entry = {int(row["entry"], 16): row for row in records}

from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS

md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
md.detail = True
body_data = {}
disasm = [f"OTA SHA-256={sha(ota)} size={len(ota)}", f"Decoded image SHA-256={sha(image)} size={len(image)} base=0x{BASE:08x}"]
call_targets = {}
for entry, (size, expected_sha) in TARGETS.items():
    body = image[entry - BASE:entry - BASE + size]
    record = by_entry[entry]
    assert len(body) == size and sha(body) == expected_sha
    assert record["body_bytes"] == size and record["body_sha256"] == expected_sha
    assert int(record["body_end_inclusive"], 16) == entry + size - 1
    body_data[entry] = body
    instructions = []
    for ins in md.disasm(body, entry):
        item = {"pc": f"0x{ins.address:08x}", "bytes": ins.bytes.hex(), "mnemonic": ins.mnemonic, "operands": ins.op_str}
        if ins.mnemonic.startswith("ldr") and "[pc," in ins.op_str:
            match = re.search(r"\[pc, #(-?0x[0-9a-f]+|-?\d+)\]", ins.op_str)
            if match:
                literal = ((ins.address + 4) & ~3) + int(match.group(1), 0)
                value = struct.unpack_from("<I", image, literal - BASE)[0]
                item["literal_address"] = f"0x{literal:08x}"
                item["literal_value"] = f"0x{value:08x}"
        if ins.mnemonic in ("bl", "blx"):
            try:
                target = int(ins.op_str.split()[0].lstrip("#"), 0)
                call_targets.setdefault(entry, []).append({"pc": f"0x{ins.address:08x}", "target": f"0x{target:08x}"})
            except ValueError:
                pass
        instructions.append(item)
        disasm.append(f"{ins.address:08x}: {ins.bytes.hex():<8} {ins.mnemonic:<10} {ins.op_str}" + (f" ; literal {item['literal_address']}={item['literal_value']}" if "literal_address" in item else ""))
    body_data[entry] = {"bytes": body, "instructions": instructions, "ghidra_name": record["name"], "size": size, "sha256": expected_sha}

for address, expected_value in LITERALS.items():
    actual_value = struct.unpack_from("<I", image, address - BASE)[0]
    assert actual_value == expected_value, (hex(address), hex(actual_value))

irq_instructions = body_data[0x4B80BE]["instructions"]
irq_calls = [row["target"] for row in call_targets[0x4B80BE]]
assert irq_calls == ["0x004812f6", "0x00481574", "0x004815f2", "0x004816c6"]
registration_calls = [call for call in call_targets[0x4B48A6] if call["target"] == "0x0048162c"]
assert registration_calls == [{"pc": "0x004b49b2", "target": "0x0048162c"}]
registration_site = body_data[0x4B48A6]["instructions"]
site_operands = {int(item["pc"], 16): item["operands"] for item in registration_site if 0x4B49A8 <= int(item["pc"], 16) <= 0x4B49B2}
assert site_operands[0x4B49A8] == "r1, #0x75"
assert site_operands[0x4B49AA] == "r3, #0"
assert site_operands[0x4B49AC] == "r2, pc, #0xe9"
assert site_operands[0x4B49B0] == "r0, #0"

gpio_source = UP / "am_hal_gpio.c"
gpio_header = UP / "am_hal_gpio.h"
device_header = UP / "apollo510.h"
source_hashes = {p.name: sha(p.read_bytes()) for p in (gpio_source, gpio_header, device_header)}
source_text = gpio_source.read_text()
assert "release_sdk5p1p0-366b80e084" in source_text
assert "am_hal_gpio_interrupt_irq_status_get(" in source_text
assert "am_hal_gpio_interrupt_irq_clear(" in source_text
assert "am_hal_gpio_interrupt_service(" in source_text
header_text = gpio_header.read_text()
device_text = device_header.read_text()
assert "#define GPIO_IRQ2N(irq)" in header_text and "#define GPIO_IRQ2IDX(irq)" in header_text
assert "GPIO0_607F_IRQn           =  59" in device_text

result = {
    "verification": "PASS",
    "artifact": {"ota_sha256": sha(ota), "decoded_image_sha256": sha(image), "base": "0x00438000", "ota_preamble_bytes": 32},
    "functions": {f"0x{address:08x}": {"name": row["ghidra_name"], "size": row["size"], "sha256": row["sha256"], "body_hex": row["bytes"].hex(), "instructions": row["instructions"]} for address, row in body_data.items()},
    "literal_words": {f"0x{address:08x}": {"value": f"0x{value:08x}", "meaning": meaning} for address, (value, meaning) in [
        (0x481768, (LITERALS[0x481768], "MCUN0INT0EN")),
        (0x4817A0, (LITERALS[0x4817A0], "MCUN0INT0STAT")),
        (0x4817D8, (LITERALS[0x4817D8], "MCUN0INT0CLR")),
        (0x481810, (LITERALS[0x481810], "callback table")),
        (0x481814, (LITERALS[0x481814], "callback argument table")),
    ]},
    "irq_consumer": {"entry": "0x004b80be", "name": by_entry[0x4B80BE]["name"], "calls_in_order": call_targets[0x4B80BE], "static_behavior": "Reads seven channel-0 status words into a local stack buffer, then obtains IRQ 0x3b status with enabled-only false, passes that mask to clear, then passes it to service. It ignores helper return values. The first seven-word snapshot is not subsequently read in this body."},
    "callback_registration_evidence": {"registration_body": "0x0048162c", "registration_sha256": TARGETS[0x48162C][1], "selected_caller": "0x004b48a6", "selected_caller_sha256": TARGETS[0x4B48A6][1], "callsite": "0x004b49b2", "call_arguments": {"channel_r0": 0, "pin_r1": 117, "handler_r2": "0x004b4a99", "argument_r3": 0}, "derived_service_table_slot": {"row": 3, "bit": 21, "callback_address": "0x200683fc", "argument_address": "0x20068afc"}, "bounds": "Registration code validates channel values 0/1/2 but does not validate pin or physical-pad availability; this call is a statically authenticated publication site, not proof of runtime table contents."},
    "upstream": {"source": str(gpio_source.relative_to(ROOT)), "release_marker": "release_sdk5p1p0-366b80e084", "sha256": source_hashes, "matching_api_names": {"0x00481574": "am_hal_gpio_interrupt_irq_status_get", "0x004815f2": "am_hal_gpio_interrupt_irq_clear", "0x004816c6": "am_hal_gpio_interrupt_service", "0x0048162c": "am_hal_gpio_interrupt_register"}, "comparison": "Source-semantic correspondence only; no compiler-byte match is claimed."},
    "semantics": {
        "status_get": "Accepts IRQ values 0x38..0x3e or 0x7d..0x83; otherwise returns status 6 without writing output. Maps each IRQ to a GPIO bank, saves PRIMASK via 0x473940, reads its EN register only when enabledOnly is true (otherwise starts with 0xffffffff), ANDs with STAT, writes the output, and restores the saved PRIMASK. Success status is 0.",
        "clear": "Accepts the same IRQ ranges; otherwise returns 6 without the register write. Valid input writes the caller mask to the matching CLR register and returns 0. The body does not wrap this write in the PRIMASK helper.",
        "service": "Accepts the same IRQ ranges; otherwise returns 5. Computes IRQ row 0..6 for GPIO0 or 7..13 for GPIO1, repeatedly selects the least-significant set bit, clears that bit from the local working mask, loads the corresponding callback and argument from row-stride 0x80 arrays, invokes non-null callbacks, and continues after a missing callback while retaining return status 7. Empty mask returns 0.",
        "registration": "Accepts channel 0, 1, or 2 (both); computes row=pin>>5 and bit=pin&31, then stores callback and argument into the static arrays. No pin/bank bounds check is present in this routine; caller-side validation is required.",
        "irq_0x3b": "Apollo510 header names value 59 GPIO0_607F_IRQn. It maps to GPIO0 row 3; status/enable/clear word addresses are 0x40010564, 0x40010560, and 0x40010568 respectively. Service row bases are 0x200683a8 for callbacks and 0x20068aa8 for arguments; each selected bit adds 4 times its bit index."
    },
    "limits": ["Authenticated instruction bytes and static consumer order only; no GPIO hardware execution or callback behavior was exercised.", "Cached Ambiq source supports API-level semantic correspondence, not proof of the original compiler or exact build flags.", "The selected ISR ignores status, clear, and service return values. Callback registrations and runtime RAM table contents are external runtime state."],
}
with (OUT / "disassembly-final.txt").open("x") as f:
    f.write("\n".join(disasm) + "\n")
with (OUT / "results-final.json").open("x") as f:
    json.dump(result, f, indent=2, sort_keys=True)
    f.write("\n")
print("PASS authenticated three GPIO IRQ bodies, literals, and selected ISR call order")
