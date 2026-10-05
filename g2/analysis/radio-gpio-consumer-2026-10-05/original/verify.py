#!/usr/bin/env python3
"""Bounded static authentication of the radio GPIO callback path."""
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
TARGETS = {
    0x4810B0: (582, "be21713c06a339f82b208a72294f0c9d573a7822128b69e06ae5a4fe2770f5a6"),
    0x4812F6: (370, "73b2b09e9d4c7337ae845699102cffefbf3c3cb3883d797c633656842ec1f352"),
    0x4B4768: (30, "1035348ab98d999ddd9ad2f9a2f77fb3cd32ac1ea0d27ba67e9add9babec3208"),
    0x4B4786: (40, "750578da18c9e9167c290dedf7885699f8350b18ff6f52fe1c09a1a171882c8a"),
    0x4B4888: (30, "2774f80d74892f0f41d3c702d129eba85b5d23434cedd97632de1c0db96b80d4"),
    0x4B48A6: (296, "6521b6ef083e2d005e890c922bcd93b2271e7d256b0543e2471f5e797cda09bd"),
    0x4B49CE: (52, "8dd1286b093dcbe9b7049d56a221024568bc5c91d61545b60ba66c0516a44a9c"),
    0x4B4A98: (26, "8aaad9561f503147d8dab516f5dcbed5b36fdef2ad0dc7965c8e1dc2a136ca28"),
    0x52B91E: (64, "62fda22da8f5aec6255e52e820a4570a593fa4637a710ce93ebfbdca428f7db8"),
    0x52DD58: (18, "aedb4ffba6805e45177f09ff5349fd999e30f76fa040aef376aeeb76c55e8f54"),
    0x52DD6A: (18, "cf43eac442b7bf5ad96666ee22a31ebcb70eb5e547de39644e18d115abbb681a"),
    0x4B80BE: (44, "853386f3b04b6575390704f2a8a5defabe043bcf472e4dc6487b83ca973ae685"),
    0x4B80F0: (50, "ece886f3aa5074e050e6949a234dd80215ebf46126d5ef5d78690e6fc19d8faa"),
}
LITERALS = {0x481768: 0x40010530, 0x4B4D30: 0xE000E100, 0x4B4D34: 0xE000E400, 0x4B4D38: 0xE000ED18,
            0x4B4D94: 0x20074640, 0x4B4DA4: 0x20074FCB}


def sha(data):
    return hashlib.sha256(data).hexdigest()


ota = OTA.read_bytes()
image = ota[32:]
assert sha(ota) == "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
assert sha(image) == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
run = json.loads((GH / "RUN.json").read_text())
assert run["base"] == "0x00438000" and run["image_sha256"] == sha(image)
rows = [json.loads(line) for line in (GH / "functions-000.jsonl").read_text().splitlines() if line.strip()]
by_entry = {int(row["entry"], 16): row for row in rows}

from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS

md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
md.detail = True
functions = {}
calls = {}
listing = [f"OTA sha256={sha(ota)}", f"decoded image sha256={sha(image)} base=0x{BASE:08x}"]
for entry, (size, expected) in TARGETS.items():
    body = image[entry - BASE:entry - BASE + size]
    record = by_entry[entry]
    assert len(body) == size and sha(body) == expected
    assert record["body_bytes"] == size and record["body_sha256"] == expected
    assert int(record["body_end_inclusive"], 16) == entry + size - 1
    instructions = []
    calls[entry] = []
    for ins in md.disasm(body, entry):
        row = {"pc": f"0x{ins.address:08x}", "bytes": ins.bytes.hex(), "mnemonic": ins.mnemonic, "operands": ins.op_str}
        if ins.mnemonic.startswith("ldr") and "[pc," in ins.op_str:
            match = re.search(r"\[pc, #(-?0x[0-9a-f]+|-?\d+)\]", ins.op_str)
            if match:
                lit = ((ins.address + 4) & ~3) + int(match.group(1), 0)
                value = struct.unpack_from("<I", image, lit - BASE)[0]
                row["literal_address"] = f"0x{lit:08x}"
                row["literal_value"] = f"0x{value:08x}"
        if ins.mnemonic in ("bl", "blx"):
            try:
                target = int(ins.op_str.split()[0].lstrip("#"), 0)
                calls[entry].append({"pc": f"0x{ins.address:08x}", "target": f"0x{target:08x}"})
            except ValueError:
                pass
        instructions.append(row)
        listing.append(f"{ins.address:08x}: {ins.bytes.hex():<8} {ins.mnemonic:<10} {ins.op_str}" + (f" ; [{row['literal_address']}]={row['literal_value']}" if "literal_address" in row else ""))
    functions[entry] = {"name": record["name"], "size": size, "sha256": expected, "body_hex": body.hex(), "instructions": instructions}

for address, value in LITERALS.items():
    assert struct.unpack_from("<I", image, address - BASE)[0] == value

UP = ROOT / "g2/build/foundation/ambiq-upstream"
gpio_source = (UP / "am_hal_gpio.c").read_bytes()
gpio_header = (UP / "am_hal_gpio.h").read_bytes()
device_header = (UP / "apollo510.h").read_bytes()
assert b"release_sdk5p1p0-366b80e084" in gpio_source
assert b"am_hal_gpio_interrupt_control(" in gpio_source
assert b"am_hal_gpio_interrupt_register(" in gpio_source
assert b"am_hal_gpio_interrupt_service(" in gpio_source
assert b"GPIO0_607F_IRQn           =  59" in device_header

boot_calls = [int(call["target"], 16) for call in calls[0x4B48A6]]
assert boot_calls[-3:] == [0x52DD58, 0x4B4786, 0x4B4768]
assert calls[0x52DD58] == [{"pc": "0x0052dd64", "target": "0x004810b0"}]
assert calls[0x52DD6A] == [{"pc": "0x0052dd76", "target": "0x004810b0"}]
shutdown_targets = [int(call["target"], 16) for call in calls[0x4B49CE]]
assert 0x52DD6A in shutdown_targets
assert any(call == {"pc": "0x004b49b2", "target": "0x0048162c"} for call in calls[0x4B48A6])
assert [int(call["target"], 16) for call in calls[0x4B80BE]] == [0x4812F6, 0x481574, 0x4815F2, 0x4816C6]
assert not ({0x4B4768, 0x4B4786, 0x48162C, 0x4815F2} & set(shutdown_targets))

def direct_callers(entry):
    return [{"entry": row["entry"], "name": row["name"], "sha256": row["body_sha256"]} for row in rows if entry in row.get("callees", [])]

result = {
    "verification": "PASS",
    "artifact": {"ota_sha256": sha(ota), "decoded_image_sha256": sha(image), "main_image_base": "0x00438000", "preamble_bytes": 32},
    "pinned_source": {"release_marker": "release_sdk5p1p0-366b80e084", "files": {
        "am_hal_gpio.c": {"sha256": sha(gpio_source), "path": "g2/build/foundation/ambiq-upstream/am_hal_gpio.c"},
        "am_hal_gpio.h": {"sha256": sha(gpio_header), "path": "g2/build/foundation/ambiq-upstream/am_hal_gpio.h"},
        "apollo510.h": {"sha256": sha(device_header), "path": "g2/build/foundation/ambiq-upstream/apollo510.h"},
    }, "api_correspondences": {"0x004810b0": "am_hal_gpio_interrupt_control", "0x0048162c": "am_hal_gpio_interrupt_register", "0x004816c6": "am_hal_gpio_interrupt_service"}},
    "functions": {f"0x{entry:08x}": value for entry, value in functions.items()},
    "literal_values": {f"0x{address:08x}": f"0x{value:08x}" for address, value in LITERALS.items()},
    "registration_and_enable_order": {
        "HciDrvRadioBoot": [
            {"pc": "0x004b49b2", "action": "register channel0 pin117 callback 0x004b4a99 arg0"},
            {"pc": "0x004b49b6", "action": "call 0x0052dd58 -> 0x004810b0(channel0, INDV_ENABLE, &pin117)"},
            {"pc": "0x004b49be", "action": "call NVIC priority-byte wrapper for IRQ 0x3b with requested field 4"},
            {"pc": "0x004b49c4", "action": "call NVIC set-enable wrapper for IRQ 0x3b"},
        ],
        "nvic_register_effects_from_original_instructions": {
            "priority_base": "0xe000e400", "irq_address": "0xe000e43b", "written_byte": "0x40",
            "set_enable_base": "0xe000e100", "word_address": "0xe000e104", "written_word": "0x08000000",
        },
        "callback_tables": {"callback_table_base": "0x20068228", "argument_table_base": "0x20068928", "gpio117_row": 3, "gpio117_bit": 21, "callback_slot": "0x200683fc", "argument_slot": "0x20068afc"},
    },
    "gpio_pad_enable": {
        "control_body": "0x004810b0", "sha256": TARGETS[0x4810B0][1], "api_correspondence": "am_hal_gpio_interrupt_control",
        "boot_wrapper": {"entry": "0x0052dd58", "channel": 0, "control_enum": 1, "pin_word": "0x75", "effect": "OR bit 21 into GPIO0 interrupt-enable word at 0x40010560"},
        "shutdown_wrapper": {"entry": "0x0052dd6a", "channel": 0, "control_enum": 0, "pin_word": "0x75", "effect": "AND with complement of bit 21 in GPIO0 interrupt-enable word at 0x40010560"},
        "control_implementation": "Validates individual pin < 0xe0, maps pin 117 to register index 3 and mask 1<<21, saves/restores PRIMASK around the enable-word update.",
    },
    "callback": {
        "name": "HciDrvIntService", "entry": "0x004b4a98", "sha256": TARGETS[0x4B4A98][1],
        "operations": ["increment 32-bit counter at 0x20074640", "load byte event identifier from 0x20074fcb", "call 0x0052b91e with (event_id, 1)", "return value is not consumed by GPIO service"],
        "direct_caller_records": direct_callers("004b4a98"),
        "registration_is_pointer_based": True,
        "event_delivery_body": "0x0052b91e",
        "event_delivery_behavior": "WsfSetEvent enters WSF critical section, ORs event bit 1 into the byte at eventBase + (eventId & 0xf) + 0x28, ORs 4 into eventBase + 0x3c, exits critical section, then calls WsfSetOsSpecificEvent.",
    },
    "irq_path": {
        "irq_handler": "0x004b80be", "irq_number": 59, "name": "GPIO0_607F_IRQn",
        "call_order": calls[0x4B80BE],
        "body_effect": "Seven-word channel-0 status snapshot to local stack memory; then IRQ 0x3b status read with enabled-only false, clear returned mask, service same mask. Helper return codes ignored. The initial seven-word snapshot is not read later in this ISR body.",
        "gpio_0x3b_registers": {"enable": "0x40010560", "status": "0x40010564", "clear": "0x40010568"},
    },
    "shutdown_boundary": {
        "function": "HciDrvRadioShutdown", "direct_calls": calls[0x4B49CE],
        "direct_callers": direct_callers("004b49ce"),
        "static_observation": "Stops the timer, calls 0x0052dd6a which disables GPIO117's channel-0 interrupt through 0x004810b0, performs additional radio-side GPIO/radio calls, zeros two ring counters, and calls a radio-side operation. It contains no direct callback-unregister call or NVIC set/clear/priority wrapper call. Called helpers beyond this bounded GPIO-disable path were not expanded, so no broader shutdown guarantee is claimed.",
        "radio_boot_callers": direct_callers("004b48a6"),
    },
    "limits": [
        "Static instruction/caller evidence only; no GPIO/NVIC hardware execution or WSF event-loop behavior was tested.",
        "No claim is made about transitive side effects of unidentified or out-of-scope called functions.",
        "No direct registration call xref exists for the callback because its address is passed as data; the authenticated registration callsite supplies that pointer.",
    ],
}
outputs = {
    "disassembly-final.txt": "\n".join(listing) + "\n",
    "results-final.json": json.dumps(result, indent=2, sort_keys=True) + "\n",
}
for filename, content in outputs.items():
    path = OUT / filename
    if path.exists():
        assert path.read_text() == content, f"existing evidence differs: {filename}"
    else:
        with path.open("x") as f:
            f.write(content)
print("PASS authenticated radio GPIO registration, callback, NVIC wrappers, ISR, and shutdown boundary")
