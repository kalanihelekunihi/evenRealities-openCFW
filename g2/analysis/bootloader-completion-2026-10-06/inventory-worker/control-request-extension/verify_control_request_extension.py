#!/usr/bin/env python3
"""Differentially exercise stock 0x4251c0 requests 31/33 and source providers."""
import argparse
import hashlib
import importlib.util
import json
import struct
from pathlib import Path
from unicorn import UC_HOOK_MEM_WRITE

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
spec = importlib.util.spec_from_file_location(
    "bootverify", ROOT / "g2/components/bootloader/update_core/verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
v.ENTRIES["control"] = 0x4251C0
HANDLE, CONFIG, DESCS = 0x20006000, 0x20008000, 0x20010000
MMIO, MMIO_SIZE = 0x40060000, 0x4000


class Machine(v.Machine):
    def __init__(self, source=False, segments=(), symbols=None):
        super().__init__(source, segments, symbols)
        self.cpu.mem_map(MMIO, MMIO_SIZE)
        self.cpu.hook_add(UC_HOOK_MEM_WRITE, self.mmio_write,
                          begin=MMIO, end=MMIO + MMIO_SIZE - 1)
        self.calls = []
        # In combined source images clock_request is linked inside the image,
        # not at the original ROM callback address. Intercept that linked
        # provider entry explicitly for synthetic clock status fixtures.
        self.clock_request_pcs = {0x4222F0}
        if source and "clock_request" in self.symbols:
            self.clock_request_pcs.add(self.symbols["clock_request"] & ~1)
        if source:
            self.symbols["opencfw_boot_control"] = self.symbols["opencfw_hal_mspi_control"]

    def mmio_write(self, uc, access, address, size, value, user):
        self.events.append(["mmio-write", address, size, value])

    def code(self, uc, pc, size, user):
        if pc == 0x41D1C0:
            raw = self.args()[0]
            self.calls.append(["delay", raw])
            self.ret(0)
            return
        if pc in self.clock_request_pcs:
            args = self.args()
            self.calls.append(["clock", args[0], args[1]])
            self.ret(0)
            return
        if pc == 0x08002220:
            self.calls.append(["unrecovered", *self.args()])
            self.ret(0xDEAD0001)
            return
        super().code(uc, pc, size, user)

    def setup(self, request, module, config_data, *, null_config=False,
              busy=0, dma_status=0, slot=0, ring=4, index=0):
        h = bytearray(0x8d0)
        struct.pack_into("<II", h, 0, 0x03BEBEBE, module)
        h[8] = 1
        struct.pack_into("<I", h, 0x840, 0)
        struct.pack_into("<I", h, 0x844, 0)
        struct.pack_into("<I", h, 0x838, 0x1234)
        struct.pack_into("<I", h, 0x848, ring)
        struct.pack_into("<I", h, 0x850, index)
        struct.pack_into("<I", h, 0x854, slot if request == 31 else DESCS)
        struct.pack_into("<I", h, 0x211*4, busy)
        h[0x8c8] = 0
        self.cpu.mem_write(HANDLE, bytes(h))
        self.cpu.mem_write(CONFIG, config_data + bytes(max(0, 32-len(config_data))))
        descriptors = bytearray(0x200)
        for n in range(8):
            struct.pack_into("<4I", descriptors, n*0x18,
                             0x11110000+n, 0x22220000+n,
                             0x33330000+n, 0x44440000+n)
        self.cpu.mem_write(DESCS, bytes(descriptors))
        self.cpu.mem_write(MMIO, bytes(MMIO_SIZE))
        mb = MMIO + module*0x1000
        self.put32(mb+0x2a0, 0)
        self.put32(mb+0x2ac, 0)
        self.put32(mb+0x2b8, 0)
        self.put32(mb+0x104, dma_status)
        return [HANDLE, request, 0 if null_config else CONFIG]

    def put32(self, address, value):
        self.cpu.mem_write(address, struct.pack("<I", value & 0xffffffff))

    def observe(self, result):
        return {"return": result["return"], "events": self.events.copy(),
                "calls": self.calls.copy(),
                "handle": bytes(self.cpu.mem_read(HANDLE,0x8d0)).hex(),
                "mmio": bytes(self.cpu.mem_read(MMIO,MMIO_SIZE)).hex(),
                "descriptors": bytes(self.cpu.mem_read(DESCS,0x200)).hex()}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    assert v.sha(v.BLOB) == v.SHA
    _, segments, symbols = v.elf.elf_info(args.elf)
    cases, failures, trace = [], [], {}

    def run(request, module, cfg=b"", **kw):
        pair = [Machine(), Machine(True, segments, dict(symbols))]
        argv = [m.setup(request,module,cfg,**kw) for m in pair]
        try:
            results = [m.run("control",a) for m,a in zip(pair,argv)]
        except Exception:
            from unicorn import arm_const
            print("emulation error", request, module,
                  [(m.source, hex(m.cpu.reg_read(arm_const.UC_ARM_REG_PC)),
                    hex(m.cpu.reg_read(arm_const.UC_ARM_REG_SP))) for m in pair])
            raise
        obs = [m.observe(r) for m,r in zip(pair,results)]
        # The sentinel can appear only for a request this extension intentionally
        # does not own. Requests 31 and 33 must route here and never fall through.
        diff = [k for k in obs[0] if obs[0][k] != obs[1][k]]
        if any(c[0] == "unrecovered" for c in obs[0]["calls"] + obs[1]["calls"]):
            diff.append("unexpected-unrecovered")
        for m in pair:
            trace.update(m.trace)
        cases.append({"request":request,"module":module,"null_config":kw.get("null_config",False),
                      "config":cfg.hex(),"slot":kw.get("slot",0),"busy":kw.get("busy",0),
                      "status":obs[0]["return"],"writes":[e for e in obs[0]["events"] if e[0]=="mmio-write"]})
        if diff:
            failures.append({"request":request,"module":module,"diff_fields":diff,
                             "stock_return":obs[0]["return"],"source_return":obs[1]["return"]})

    # Request 31 null, busy, success, and nontrivial div-by-24 configuration.
    for module in range(4):
        run(31,module,null_config=True)
        run(31,module,struct.pack("<II",0x12345678,0x123),slot=0)
        run(31,module,struct.pack("<II",0x87654321,0x240),slot=1)
    # Request 33 already-paused and the actual 4240aa pause/DMA continuation.
    for module in range(4):
        run(33,module,busy=1)
        run(33,module,busy=0,slot=0)

    blob=v.BLOB.read_bytes()
    ranges={"control_dispatch":[0x4251c0,0x4262e0],
            "pause_dma_continuation":[0x423fb8,0x42411f]}
    range_hashes={n:hashlib.sha256(blob[a-v.BASE:b-v.BASE]).hexdigest()
                  for n,(a,b) in ranges.items()}
    used={int(pc,0)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))}
    source_files=[HERE/"verify_control_request_extension.py",HERE/"Makefile",HERE/"module.ld",
      ROOT/"g2/components/bootloader/nor_mspi_init/control_request_extension.c",
      ROOT/"g2/components/bootloader/nor_mspi_init/control_request_extension.h",
      ROOT/"g2/components/bootloader/nor_mspi_init/control_request_state.c",
      ROOT/"g2/components/bootloader/nor_mspi_init/control_request_clock.c",
      ROOT/"g2/components/bootloader/nor_mspi_queue/mspi_pause_dma.c",
      ROOT/"g2/components/bootloader/nor_mspi_queue/queue_descriptors.c",
      ROOT/"g2/components/bootloader/nor_mspi_power/mspi_clockgen_control.c",
      ROOT/"g2/components/bootloader/nor_mspi_power/device_configure.c",
      ROOT/"g2/components/bootloader/platform_control/critical_save.S",
      ROOT/"g2/components/bootloader/nor_mspi_init/status_poll.c",
      ROOT/"g2/components/bootloader/nor_mspi_init/control_read.c",
      ROOT/"g2/components/bootloader/nor_mspi_init/control_remaining.c"]
    output={"status":"PASS" if not failures else "FAIL","cases":len(cases),"failures":failures,
      "original_sha256":v.SHA,"source_elf_sha256":digest(args.elf),
      "source_sha256":{str(p.relative_to(ROOT)):digest(p) for p in source_files},
      "stock_range_sha256":range_hashes,"distinct_original_instruction_bytes":len(used),
      "original_trace":trace,"coverage_requests":[31,33],"comparisons":cases,
      "limits":["Original dispatch 0x4251c0 executes against synthetic RAM/MMIO; no hardware access.",
        "Request 33 calls the recovered 0x4240aa source continuation on the source side; its delay and clock callbacks are intercepted, while the 0x41d246 status poll is source.",
        "Request 34 is not implemented here. It also requires stage_two_mode_flags, 0x4279be release, and 0x423f8e first-post CQ enable beyond the already recovered 0x42790a/0x4279f0 helpers."]}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(output,indent=2)+"\n")
    print(json.dumps({k:output[k] for k in ("status","cases","distinct_original_instruction_bytes","coverage_requests","stock_range_sha256")},indent=2))
    if failures: raise SystemExit(1)

if __name__ == "__main__": main()
