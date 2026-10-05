from pathlib import Path
import hashlib
import json
import struct
import sys

import capstone
import unicorn
from unicorn.arm_const import (
    UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1,
    UC_ARM_REG_SP,
)

if not __debug__:
    raise SystemExit("refusing to run verifier with Python optimization enabled")

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
BLOB_PATH = ROOT / "g2/blobs/official/g2-2.2.6.10/firmware_touch.bin"
blob = BLOB_PATH.read_bytes()
assert hashlib.sha256(blob).hexdigest() == "0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d"
image = blob[32:32 + 0x8680]
assert hashlib.sha256(image).hexdigest() == "371d8a61b659a33b4cad4a7d892e144aba8263ae59497b4f658afc5b0c430f87"
BASE = 0x3300
ENTRY = 0x9316
SIZE = 44
OFFSET = ENTRY - BASE
body = image[OFFSET:OFFSET + SIZE]
BODY_SHA = "1fdc6e20657ebf1efbbf7423c354904526f55af9f31d09ad5cd700d69ecdb993"
assert hashlib.sha256(body).hexdigest() == BODY_SHA

md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB | capstone.CS_MODE_MCLASS)
disassembly = [
    {"pc": hex(i.address), "bytes": i.bytes.hex(), "mnemonic": i.mnemonic, "operands": i.op_str}
    for i in md.disasm(body, ENTRY)
]
assert sum(len(bytes.fromhex(row["bytes"])) for row in disassembly) == SIZE

STOP = 0x10000000
SCB = 0x20000000
REG_CONFIG = 0x000
REG_RX_FIFO_CTRL = 0x304

def run_case(case_index, config, level, initial_ctrl):
    u = unicorn.Uc(unicorn.UC_ARCH_ARM, unicorn.UC_MODE_THUMB | unicorn.UC_MODE_MCLASS)
    u.mem_map(0x3000, 0x10000)
    u.mem_write(BASE, image)
    u.mem_map(SCB, 0x1000)
    u.mem_map(STOP, 0x1000)
    u.mem_write(SCB + REG_CONFIG, struct.pack("<I", config))
    u.mem_write(SCB + REG_RX_FIFO_CTRL, struct.pack("<I", initial_ctrl))
    trace = []
    accesses = []
    def code_hook(uc, address, size, _):
        assert ENTRY <= address < ENTRY + SIZE, hex(address)
        fetched = bytes(uc.mem_read(address, size))
        assert fetched == image[address - BASE:address - BASE + size]
        ins = list(md.disasm(fetched, address))
        assert len(ins) == 1 and ins[0].size == size
        trace.append({"pc": hex(address), "bytes": fetched.hex(), "mnemonic": ins[0].mnemonic, "operands": ins[0].op_str})
    def memory_hook(uc, access, address, size, value, _):
        if SCB <= address < SCB + 0x400:
            kind = "read" if access == unicorn.UC_MEM_READ else "write"
            accesses.append({"kind": kind, "offset": hex(address - SCB), "size": size, "value": value if kind == "write" else None})
    u.hook_add(unicorn.UC_HOOK_CODE, code_hook)
    u.hook_add(unicorn.UC_HOOK_MEM_READ | unicorn.UC_HOOK_MEM_WRITE, memory_hook)
    u.reg_write(UC_ARM_REG_SP, SCB + 0x800)
    u.reg_write(UC_ARM_REG_LR, STOP | 1)
    u.reg_write(UC_ARM_REG_R0, SCB)
    u.reg_write(UC_ARM_REG_R1, level)
    exception = None
    try:
        u.emu_start(ENTRY | 1, STOP, count=1000)
    except unicorn.UcError as exc:
        exception = str(exc)
    after = struct.unpack("<I", u.mem_read(SCB + REG_RX_FIFO_CTRL, 4))[0]
    return {
        "index": case_index,
        "config": hex(config),
        "depth": 16 if config & 0xc000 == 0 else 8,
        "level": level,
        "initial_rx_fifo_ctrl": hex(initial_ctrl),
        "final_rx_fifo_ctrl": hex(after),
        "memory_accesses": accesses,
        "executed_original_trace": trace,
        "pc_after_run": hex(u.reg_read(UC_ARM_REG_PC)),
        "exception": exception,
    }

cases = []
for idx, cfg, level in [
    (0, 0x00000000, 0), (1, 0x00000000, 15),
    (2, 0x00004000, 0), (3, 0x0000c000, 7), (7, 0x00008000, 7),
]:
    initial = 0xa5c312e7
    row = run_case(idx, cfg, level, initial)
    depth = row["depth"]
    assert level < depth
    assert row["exception"] is None and row["pc_after_run"] == hex(STOP)
    expected = (initial & ~0xff) | level
    assert int(row["final_rx_fifo_ctrl"], 16) == expected
    assert [a["offset"] for a in row["memory_accesses"]] == ["0x0", "0x304", "0x304"]
    assert [a["kind"] for a in row["memory_accesses"]] == ["read", "read", "write"]
    cases.append(row)
for idx, cfg, level in [(4, 0, 16), (5, 0x4000, 8), (6, 0xc000, 0x101),
                        (8, 0, 0xffffffff)]:
    initial = 0x87654321
    row = run_case(idx, cfg, level, initial)
    assert row["exception"] is not None
    assert int(row["final_rx_fifo_ctrl"], 16) == initial
    assert row["memory_accesses"] == [{"kind": "read", "offset": "0x0", "size": 4, "value": None}]
    assert any(t["mnemonic"] == "bkpt" for t in row["executed_original_trace"])
    cases.append(row)

report = {
    "status": "PASS",
    "firmware_sha256": hashlib.sha256(blob).hexdigest(),
    "decoded_image_sha256": hashlib.sha256(image).hexdigest(),
    "function": {"name": "Cy_SCB_SetRxFifoLevel", "runtime": hex(ENTRY), "size": SIZE,
                 "image_range": [hex(OFFSET), hex(OFFSET + SIZE)], "sha256": BODY_SHA,
                 "bytes": body.hex()},
    "tool_versions": {"python": sys.version.split()[0], "unicorn": unicorn.__version__, "capstone": capstone.__version__},
    "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "disassembly": disassembly,
    "case_count": len(cases),
    "cases": cases,
    "limits": "Original 44-byte function executed against synthetic RAM-backed register words. Read/write order and original PCs/bytes were traced. Invalid-level BKPT is observed as an emulator exception; no physical peripheral, interrupt behavior, timing, or FIFO data movement was tested.",
}
with (OUT / "results.json").open("x") as result_file:
    json.dump(report, result_file, indent=2)
    result_file.write("\n")
print(json.dumps({"status": report["status"], "case_count": report["case_count"], "results": str(OUT / "results.json")}, indent=2))
