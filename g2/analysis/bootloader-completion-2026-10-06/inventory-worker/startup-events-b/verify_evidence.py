#!/usr/bin/env python3
"""Authenticate locked SPOT callback 42ba00 and its installed table slot."""
from pathlib import Path
import hashlib
import json
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
IMAGE = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
FUNCTIONS = ROOT / "g2/research/corpus/apollo-bootloader/ghidra/open-2026-09-29/functions-000.jsonl"
RUNTIME_SOURCE = ROOT / "g2/components/bootloader/initializer_callbacks/startup_runtime.c"
RUNTIME_RESULT = ROOT / "g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize/runtime-comparison.json"
HAL_HEADER = ROOT / "g2/analysis/bootloader-completion-2026-10-06/upstream-worker/ambiqhal-apollo510/ambiqhal/mcu/apollo510/hal/am_hal_spotmgr.h"
EXPECTED_IMAGE = "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
ENTRY, END = 0x42BA00, 0x42BD8C
EXPECTED_BODY = "1a5659a51222d91d03686766dd6caf89fcb4a813088e80095f61d554cc575450"
DESCENDANTS = {
    0x42AD40: (0x42ADB8, "89f71050cf7850205a7a5ef9ccfb09dfadaadd5a6046355844d800589b65607d"),
    0x42AEF0: (0x42B010, "7a54959ea8247c505df0f3139ce607b4d1fabb5d0015054b89bd44b5d79cc31b"),
    0x42B014: (0x42B068, "b3da01a94a3c08eb7eb0d7d344b6760d929296878e2dfbf9c4770373aedd3d88"),
    0x42B6B8: (0x42B9BA, "74f4304f6e3aa59022a29eb5e5f5479c77072b33355825b7c9409897001bb9d1"),
}
TRANSITION_CHILDREN = {
    0x42B294: (0x42B69C, "0393f03222d8b7e8c67ed0e7ffbba640f8030dac259a909ec7dbb20846325c2b"),
    0x42B06C: (0x42B294, "44271365df4592f33c91286690e4e75e328a8dd11127aa934bec2c571292c377"),
    0x42ADB8: (0x42AE24, "7b25d7dae842d5787345a5360a32fbf21f4adadc88e216b2eaa272cc77d7feda"),
    0x42AE24: (0x42AE6C, "73da1f0b69f23d583009d5dfbc2f46007ee0f8b9f56a5c8a3b4fccd58136f538"),
    0x42AE6C: (0x42AE9C, "fbc7ca52270345ca6b251d1c8c805a06e33af456500f9b17e05cfa7743af79f8"),
    0x41CC48: (0x41CC92, "aef74a1657eee6d89e50c7452789a0aff1c7e25bb9dd81f3a1db74ed173d5e49"),
    0x41CC92: (0x41CCD6, "bcbc39a968d90e534a70b68e4dcda7a2bf30bcd02725a4a4ecf539b8d50cfbc6"),
    0x41CCD6: (0x41CD1A, "53ecf1cc50f77949e880de53ecfed6a2d18c3ea803c457a13e77d1b2ac548a3a"),
    0x41D1C0: (0x41D210, "c336d5c93475c6521bab00509a8ad8aaa1078b3bdc313ae43107777520af1895"),
    0x41E1E8: (0x41E22E, "4f10536463c4fd13679ef30c2fabc9876f052bcc90cb6100837d849e19fc09dd"),
    0x41E22E: (0x41E266, "0e250a57f88ce12c21f0691cc8de447aa6a9808529c3668c6e54d653fe6dec45"),
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


image = IMAGE.read_bytes()
assert digest(image) == EXPECTED_IMAGE
functions = {int(d["entry"], 16): d for d in
             map(json.loads, FUNCTIONS.read_text(encoding="utf-8").splitlines())}
record = functions[ENTRY]
assert int(record["body_start"], 16) == ENTRY
assert int(record["body_end_inclusive"], 16) + 1 == END
assert int(record["body_bytes"]) == END - ENTRY == 908
raw = image[ENTRY - 0x410000:END - 0x410000]
assert len(raw) == 908 and digest(raw) == EXPECTED_BODY == record["body_sha256"]
for child, (child_end, child_digest) in DESCENDANTS.items():
    child_record = functions[child]
    child_raw = image[child - 0x410000:child_end - 0x410000]
    assert int(child_record["body_end_inclusive"], 16) + 1 == child_end
    assert int(child_record["body_bytes"]) == child_end - child
    assert digest(child_raw) == child_digest == child_record["body_sha256"]
for child, (child_end, child_digest) in TRANSITION_CHILDREN.items():
    child_record = functions[child]
    child_raw = image[child - 0x410000:child_end - 0x410000]
    assert int(child_record["body_end_inclusive"], 16) + 1 == child_end
    assert int(child_record["body_bytes"]) == child_end - child
    assert digest(child_raw) == child_digest == child_record["body_sha256"]

# Resolve the function's literal-pool pointer words from the authenticated image.
literal_addresses = [0x42BFC8, 0x42BFCC, 0x42BFD0, 0x42BFD4, 0x42BFD8,
                     0x42BFDC, 0x42BFE0, 0x42BFE4, 0x42BFE8, 0x42BFEC,
                     0x42BFF0, 0x42BFF4, 0x42BFF8, 0x42BFFC, 0x42C000,
                     0x42C004, 0x42C008, 0x42C00C, 0x42C010, 0x42C014,
                     0x42C018, 0x42C01C]
literals = {f"0x{address:08x}": f"0x{struct.unpack_from('<I', image, address - 0x410000)[0]:08x}"
            for address in literal_addresses}

runtime_source = RUNTIME_SOURCE.read_text(encoding="utf-8")
assert "slot(4,0x42ba01)" in runtime_source
assert "REV==34&&VAR==2" in runtime_source
assert "REV==35&&VAR==1" in runtime_source
runtime = json.loads(RUNTIME_RESULT.read_text(encoding="utf-8"))
assert runtime["status"] == "PASS" and runtime["cases"] == 832
route_cases = [c for c in runtime["comparisons"] if c.get("name") == "dispatch"
               and (c.get("fixture", {}).get("revision"),
                    c.get("fixture", {}).get("variant")) in ((34, 2), (35, 1))]
assert route_cases
for case in route_cases:
    assert case["result"]["table"][8:16] == "01ba4200", case["fixture"]

hal = HAL_HEADER.read_text(encoding="utf-8")
assert "am_hal_spotmgr_power_state_update(am_hal_spotmgr_stimulus_e eStimulus, bool bOn, void *pArgs)" in hal
assert "AM_HAL_SPOTMGR_STIM_DEVPWR" in hal and "AM_HAL_SPOTMGR_STIM_TEMP" in hal

decoder_config = struct.unpack_from("<I", image, 0x434164 - 0x410000)[0]

scanner_predicate = (0x41F3F0, 0x41F424,
                     "2629a71d82c78f7602d8f37273ae02bcf42f237cdaab9da0d4db6d57a1045692")
predicate_record = functions[scanner_predicate[0]]
predicate_raw = image[scanner_predicate[0] - 0x410000:scanner_predicate[1] - 0x410000]
assert int(predicate_record["body_end_inclusive"], 16) + 1 == scanner_predicate[1]
assert len(predicate_raw) == scanner_predicate[1] - scanner_predicate[0] == 52
assert digest(predicate_raw) == scanner_predicate[2] == predicate_record["body_sha256"]
scanner_literals = {0x42B9D4: 0x400204D8, 0x42B9D8: 0x200271C0,
                    0x42B9DC: 0x40008800, 0x42B9E0: 0x40008000,
                    0x42B9E4: 0x40008010}
for address, value in scanner_literals.items():
    assert struct.unpack_from("<I", image, address - 0x410000)[0] == value

disassembly = subprocess.run([
    "arm-none-eabi-objdump", "-D", "-b", "binary", "-m", "arm",
    "-M", "force-thumb", "--adjust-vma=0x410000",
    f"--start-address=0x{ENTRY:x}", f"--stop-address=0x{END:x}", str(IMAGE)
], check=True, capture_output=True, text=True).stdout
# Recover the decoder's byte window and outputs from original call-site code.
for instruction in ("add\tr2, sp, #24", "mov\tr1, sp", "add\tr0, sp, #4",
                    "strb.w\tr1, [sp, #20]", "strb.w\tr1, [sp, #21]",
                    "strb.w\tr1, [sp, #22]", "bl\t0x42b6b8"):
    assert instruction in disassembly, instruction
for instruction in ("strb.w\tr0, [sp, #20]", "ldrb.w\tr0, [sp, #20]",
                    "add\tr0, sp, #4", "bl\t0x42aef0"):
    assert instruction in disassembly, instruction
(HERE / "stock-disassembly.txt").write_text(disassembly, encoding="utf-8")

result = {
    "status": "PASS",
    "image": {"path": str(IMAGE.relative_to(ROOT)), "sha256": EXPECTED_IMAGE,
              "load_address": "0x410000", "state": "Thumb"},
    "function": {"entry": "0x42ba00", "end_exclusive": "0x42bd8c",
                 "bytes": 908, "sha256": EXPECTED_BODY,
                 "ghidra_signature": record["signature"],
                 "direct_callees": [f"0x{int(c,16):08x}" for c in record["callees"]]},
    "installed_slot": {
        "table": "0x20026e38", "offset": "0x04", "stored_thumb_target": "0x42ba01",
        "routes": ["revision 34 / trim 2", "revision 35 / trim 1"],
        "runtime_source": str(RUNTIME_SOURCE.relative_to(ROOT)),
        "runtime_comparison": {"path": str(RUNTIME_RESULT.relative_to(ROOT)),
                               "status": runtime["status"], "cases": runtime["cases"]},
    },
    "abi": {
        "registers": {"r0": "stimulus/event (low 8 bits)",
                      "r1": "on/option (low 8 bits)",
                      "r2": "argument pointer"},
        "corroboration": "Pinned Apollo510 SPOT HAL declares am_hal_spotmgr_power_state_update(stimulus, bOn, pArgs); the locked Ghidra record separately supplies byte/char/pointer types.",
        "header_path": str(HAL_HEADER.relative_to(ROOT)),
    },
    "literal_pool_words": literals,
    "decoder_contract": {
        "entry": "0x42b6b8", "body_end_exclusive": "0x42b9ba",
        "hash": DESCENDANTS[0x42B6B8][1],
        "caller_stack_frame_bytes": 32,
        "input_pointer": "sp+4", "major_output_pointer": "sp+0",
        "minor_output_pointer": "sp+24",
        "input_offset_16": "sp+20: temp category saved from 0x200271ba",
        "input_offset_17": "sp+21: state byte copied from 0x200271bb or requested transition",
        "input_offset_18": "sp+22: auxiliary category computed in wrapper, or input for SYSTEM stimulus",
        "config_word_address": "0x434164", "locked_image_config_word": f"0x{decoder_config:08x}",
        "hardware_control_word": "0x40021000", "mode_byte": "0x2002708c",
        "call_site_instruction_evidence": "0x42bce6 add r2,sp,#24; 0x42bce8 mov r1,sp; 0x42bcea add r0,sp,#4; 0x42bcec bl 0x42b6b8",
    },
    "scanner_contract": {
        "entry": "0x42aef0", "end_exclusive": "0x42b010", "bytes": 288,
        "sha256": DESCENDANTS[0x42AEF0][1],
        "predicate": {"entry": "0x41f3f0", "end_exclusive": "0x41f424",
                      "bytes": 52, "sha256": scanner_predicate[2],
                      "independent_comparison": "startup-spot-handlers/events-comparison.json"},
        "literal_pool": {f"0x{a:08x}": f"0x{v:08x}" for a, v in scanner_literals.items()},
        "channel_table": "16 words at 0x40008200 + index*0x20; active bitmap at 0x40008010",
        "caller_stack_input": "0x42bb6c stores the temperature category at sp+20; 0x42bc06 passes sp+4, so scanner input byte +16 is that category",
    },
    "transition_contract": {
        "entry": "0x42b294", "end_exclusive": "0x42b69c", "bytes": 1032,
        "sha256": TRANSITION_CHILDREN[0x42B294][1],
        "profile": "Apollo510 SPOT SRAM structure at 0x20026ba0: locked transition instructions index 21 packed state words at +4..+0x54 and consume trim fields through +0x68",
        "rank_tables": ["0x200000a4", "0x200000f4"],
        "current_index": "0x20000148", "syspll_bit": "bit 0 at 0x400083e0",
        "return": "old minor value in r0; caller ignores it",
        "nested_extents_authenticated": len(TRANSITION_CHILDREN) - 1,
        "direct_comparison": "transition-comparison-corrected.json: 30 cases; 858/1032 original bytes visited; exact remaining addresses recorded",
    },
    "limits": ["HAL header names corroborate the public API concepts; no public HAL body is claimed as an exact stock match.",
               "The transition direct harness uses seeded SPOT profile/rank state and a void ROM cycle-wait timing service; it does not establish hardware behavior.",
               "No hardware or production linker behavior is claimed."],
}
(HERE / "evidence.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print("PASS", result["function"], result["installed_slot"])
