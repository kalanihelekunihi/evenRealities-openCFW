#!/usr/bin/env python3
"""Differential test for locked 0x424be4 and its two direct helpers."""
import argparse
import hashlib
import importlib.util
import json
import random
import struct
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as a

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
spec = importlib.util.spec_from_file_location(
    "elf_reader", ROOT / "g2/components/bootloader/update_core/elf_reader.py")
elf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(elf)
IMAGE = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
IMAGE_SHA = "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
ENTRY, END = 0x424be4, 0x425066
STOP = 0x08000000
HANDLE, CONFIG, STACK = 0x20001000, 0x20002000, 0x2003f000
MMIO = 0x40000000
MSPI_BASE = 0x40060000
MODULE_STRIDE = 0x1000
STOCK_CUTS = {0x4222f0: "clock_request", 0x422364: "clock_release",
              0x41d1c0: "delay_us"}
SHIMS = {0x08000100: "delay_us", 0x08000120: "clock_request",
         0x08000140: "clock_release"}

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Machine:
    def __init__(self, source, segments=(), symbols=None, *, request_status=0,
                 release_status=0):
        self.source = source
        self.symbols = symbols or {}
        self.request_status = request_status
        self.release_status = release_status
        self.events, self.trace = [], {}
        self.finished = False
        self.uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        self.uc.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
        self.uc.mem_map(0x410000, 0x25000)
        if not source:
            blob = IMAGE.read_bytes()
            self.uc.mem_write(0x410000, blob)
            self.exec_ranges = [(0x410000, 0x410000 + len(blob))]
        else:
            self.exec_ranges = []
            for seg in segments:
                lo = seg["address"] & ~0xfff
                hi = (seg["address"] + seg["memory_size"] + 0xfff) & ~0xfff
                if not (0x410000 <= lo < 0x435000):
                    self.uc.mem_map(lo, hi-lo)
                self.uc.mem_write(seg["address"], seg["data"])
                if seg["flags"] & 1:
                    self.exec_ranges.append((seg["address"], seg["address"]+len(seg["data"])))
        self.uc.mem_map(0x20000000, 0x40000)
        self.uc.mem_map(STOP, 0x10000)
        self.uc.mem_map(MMIO, 0x100000)
        self.uc.hook_add(UC_HOOK_CODE, self.code)

    def u32(self, address):
        return struct.unpack("<I", self.uc.mem_read(address, 4))[0]

    def w32(self, address, value):
        self.uc.mem_write(address, struct.pack("<I", value & 0xffffffff))

    def args(self):
        return [self.uc.reg_read(r) for r in
                (a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2,a.UC_ARM_REG_R3)]

    def finish_call(self, value=0):
        self.uc.reg_write(a.UC_ARM_REG_R0, value & 0xffffffff)
        self.uc.reg_write(a.UC_ARM_REG_PC, self.uc.reg_read(a.UC_ARM_REG_LR))

    def callout(self, name, args):
        if name == "delay_us":
            self.events.append([name, args[0]])
            return 0
        if name == "clock_request":
            self.events.append([name, args[0] & 0xff, args[1] & 0xff,
                                self.request_status])
            return self.request_status
        if name == "clock_release":
            self.events.append([name, args[0] & 0xff, args[1] & 0xff,
                                self.release_status])
            return self.release_status
        raise AssertionError(name)

    def code(self, uc, pc, size, _):
        if pc == STOP:
            self.finished = True
            uc.emu_stop()
            return
        if self.source and pc in SHIMS:
            self.finish_call(self.callout(SHIMS[pc], self.args()))
            return
        if not self.source and pc in STOCK_CUTS:
            self.finish_call(self.callout(STOCK_CUTS[pc], self.args()))
            return
        if self.source:
            assert any(lo <= pc < hi for lo,hi in self.exec_ranges), ("source escaped",hex(pc))
        else:
            assert ((ENTRY <= pc < END) or (0x424120 <= pc < 0x42488e) or
                    (0x4249a0 <= pc < 0x424a18) or
                    (0x424a18 <= pc < 0x424a5a) or
                    (0x41b8ec <= pc < 0x41b8f4)), ("unexpected stock callee",hex(pc))
            self.trace[hex(pc)] = bytes(uc.mem_read(pc,size)).hex()

    def setup(self, fixture):
        self.events.clear(); self.trace.clear(); self.finished = False
        self._fixture = fixture
        module = fixture.get("module", 0)
        cfg=bytearray(fixture.get("config",bytes(24)))
        h = bytearray(0x8d0)
        struct.pack_into("<I",h,0,fixture.get("magic",0x01bebebe))
        struct.pack_into("<I",h,4,module)
        struct.pack_into("<I",h,8,fixture.get("configured",1))
        struct.pack_into("<I",h,24,fixture.get("dma_handle",0))
        # 0x424be4 copies config[0] into private handle byte 10 before calling
        # 0x424120. Seed the same derived state for direct and full-path cases.
        h[10] = fixture.get("private_mode", cfg[0]) & 0xff
        h[0x8c9] = fixture.get("old_class",4) & 0xff
        h[0x09] = fixture.get("handle_latency", fixture.get("old_frequency",9)) & 0xff
        h[0x0c] = fixture.get("old_frequency",9) & 0xff
        h[0x0d] = fixture.get("pending",0x35) & 0xff
        struct.pack_into("<I",h,0x8cc,fixture.get("old_delay",73))
        self.uc.mem_write(HANDLE,bytes(h))
        self.uc.mem_write(CONFIG,bytes(cfg))
        region=bytearray(0x300)
        rng=random.Random(fixture.get("seed",0x424be4))
        for off in range(0,len(region),4):
            struct.pack_into("<I",region,off,rng.getrandbits(32))
        self.uc.mem_write(MSPI_BASE+module*MODULE_STRIDE,bytes(region))

    def run(self, symbols):
        regs=(a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2,a.UC_ARM_REG_R3)
        handle = 0 if self._fixture.get("null_pointer") else HANDLE
        for reg,val in zip(regs,(handle,CONFIG,0,0)):
            self.uc.reg_write(reg,val)
        self.uc.reg_write(a.UC_ARM_REG_SP,STACK)
        self.uc.reg_write(a.UC_ARM_REG_LR,STOP|1)
        start=(symbols["opencfw_hal_mspi_device_configure"] & ~1) if self.source else ENTRY
        self.uc.emu_start(start|1,STOP+0x10000,count=1_000_000)
        assert self.finished,("did not return",hex(self.uc.reg_read(a.UC_ARM_REG_PC)))
        module=self.u32(HANDLE+4)
        return {"return":self.uc.reg_read(a.UC_ARM_REG_R0),
                "events":list(self.events),
                "handle":bytes(self.uc.mem_read(HANDLE,0x8d0)).hex(),
                "mmio":bytes(self.uc.mem_read(MSPI_BASE+module*MODULE_STRIDE,0x300)).hex(),
                "clkgen":bytes(self.uc.mem_read(0x40004110,4)).hex()}

    def run_private(self, symbols):
        self.events.clear(); self.trace.clear(); self.finished=False
        self.uc.reg_write(a.UC_ARM_REG_R0,HANDLE)
        self.uc.reg_write(a.UC_ARM_REG_SP,STACK)
        self.uc.reg_write(a.UC_ARM_REG_LR,STOP|1)
        start=(symbols["opencfw_bl_mspi_device_configure_private"] & ~1
               if self.source else 0x424120)
        self.uc.emu_start(start|1,STOP+0x10000,count=100000)
        assert self.finished,("private helper did not return",hex(start),
                              hex(self.uc.reg_read(a.UC_ARM_REG_PC)))
        return {"handle":bytes(self.uc.mem_read(HANDLE,0x8d0)).hex(),
                "mmio":bytes(self.uc.mem_read(MSPI_BASE,0x4000)).hex()}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--elf",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True); args=ap.parse_args()
    assert sha(IMAGE)==IMAGE_SHA
    _,segments,symbols=elf.elf_info(args.elf)
    out=[]; used=set(); trace={}
    cases=[]
    # Exercise every frequency byte for SDR and DDR, on every hardware module,
    # both unchanged and changed clock-class paths.
    for module in (0,1,2,3):
      for ddr in (0,1):
       for freq in range(256):
        cfg=bytearray((i*13+freq*7+ddr*3)&0xff for i in range(24))
        cfg[8]=freq%26; cfg[0xb]=freq; cfg[0x11]=ddr
        cfg[9]=freq%2; cfg[0x10]=(freq>>1)%2; cfg[0x12]=freq%4
        cases.append((f"all-frequencies-m{module}-d{ddr}-f{freq}",
           {"module":module,"old_class":(5 if freq%2 else 4),"config":bytes(cfg),
            "dma_handle": 1 if freq%3==0 else 0,"seed":freq+ddr*1000+module*2000},0,0))
    # Enumerate private device-mode bytes including out-of-range values with
    # representative low/high latency and wide-clock frequencies.
    for mode in range(256):
      for ddr,freq,lat in ((0,1,0),(0,16,1),(1,20,1)):
        cfg=bytearray((mode*9+i*11)&0xff for i in range(24))
        cfg[8]=mode;cfg[0xb]=freq;cfg[0x11]=ddr;cfg[9]=lat
        cases.append((f"mode-{mode}-d{ddr}-f{freq}-lat{lat}",
            {"module":0,"old_class":5,"config":bytes(cfg),"seed":mode+freq},0,0))
    # Validate fail-fast, clock request/release error propagation, module guards,
    # unchanged-class path, and 8-bit class/user truncation.
    cases += [
      ("null-pointer", {"null_pointer":1}, 0, 0),
      ("bad-magic", {"magic":0}, 0, 0),
      ("not-configured", {"configured":0}, 0, 0),
      ("module1-disallowed-freq", {"module":1}, 0, 0),
      ("release-failure", {"old_class":7,"config":bytes([0]*24)}, 0, 4),
      ("request-failure", {"old_class":7,"config":bytes([0]*24)}, 9, 0),
      ("clock-unchanged", {"old_class":4,"config":bytes([0]*24)}, 0, 0),
    ]
    # Replace minimal error configs with complete records to avoid dependent
    # random field assumptions.
    normalized=[]
    for name,f,rs,ls in cases:
        cfg=bytearray(f.get("config",bytes(24)))
        if name=="module1-disallowed-freq": cfg[0xb]=0x15
        normalized.append((name,{**f,"config":bytes(cfg)},rs,ls))

    for name,fixture,request_status,release_status in normalized:
        pair=[Machine(False,request_status=request_status,release_status=release_status),
              Machine(True,segments,symbols,request_status=request_status,
                      release_status=release_status)]
        observed=[]
        for m in pair:
            m.setup(fixture);observed.append(m.run(symbols))
        if observed[0]!=observed[1]:
            differing={k:[x[k] for x in observed] for k in observed[0]
                        if observed[0][k]!=observed[1][k]}
            if "mmio" in differing:
                left,right=(bytes.fromhex(x["mmio"]) for x in observed)
                differing["mmio_word_diffs"]=[
                    {"address":hex(MSPI_BASE+fixture.get("module",0)*MODULE_STRIDE+off),
                     "stock":hex(int.from_bytes(left[off:off+4],"little")),
                     "source":hex(int.from_bytes(right[off:off+4],"little"))}
                    for off in range(0,min(len(left),len(right)),4)
                    if left[off:off+4]!=right[off:off+4]][:16]
                del differing["mmio"]
            raise AssertionError((name,differing,pair[0].events,pair[1].events,
                                  sorted(pair[0].trace),
                                  pair[0].uc.reg_read(a.UC_ARM_REG_PC)))
        trace.update(pair[0].trace)
        used.update(int(pc,0)+n for pc,raw in pair[0].trace.items()
                    for n in range(len(bytes.fromhex(raw))))
        out.append({"name":name,"return":observed[0]["return"],
          "events":observed[0]["events"],
          "handle_sha256":hashlib.sha256(bytes.fromhex(observed[0]["handle"])).hexdigest(),
          "mmio_sha256":hashlib.sha256(bytes.fromhex(observed[0]["mmio"])).hexdigest()})

    # Directly call stock 0x424120 against byte-accurate private handle state;
    # this independently covers its selector byte and latency byte rather than
    # inferring private-helper coverage from the outer configure routine.
    private_cases = 0
    for module in range(4):
      for mode in range(32):
       for latency in (0, 1, 2, 3, 0xff):
        fixture={"module":module,"private_mode":mode,
                 "handle_latency":latency,"config":bytes(24),
                 "seed":0x424120 + module*1000 + mode*5 + latency}
        pair=[Machine(False),Machine(True,segments,symbols)]
        for m in pair: m.setup(fixture)
        observed=[m.run_private(symbols) for m in pair]
        if observed[0] != observed[1]:
            left,right=(bytes.fromhex(x["mmio"]) for x in observed)
            diffs=[]
            for offset in range(0,len(left),4):
                if left[offset:offset+4] != right[offset:offset+4]:
                    diffs.append({"address":hex(MSPI_BASE+offset),
                        "stock":hex(int.from_bytes(left[offset:offset+4],"little")),
                        "source":hex(int.from_bytes(right[offset:offset+4],"little"))})
            raise AssertionError(("private mode differential",module,mode,
                                  latency,diffs[:16]))
        trace.update(pair[0].trace)
        used.update(int(pc,0)+n for pc,raw in pair[0].trace.items()
                    for n in range(len(bytes.fromhex(raw))))
        private_cases += 1
    tracked=[ROOT/"g2/components/bootloader/nor_mspi_power/device_configure.c",
             ROOT/"g2/components/bootloader/nor_mspi_power/device_configure.h",
             ROOT/"g2/components/bootloader/nor_mspi_power/mspi_clockgen_control.c",
             HERE/"device_configure_module.ld",HERE/"verify_device_configure.py"]
    report={"status":"PASS","cases":len(out),
      "direct_private_helper_cases":private_cases,"original_sha256":IMAGE_SHA,
      "source_elf_sha256":sha(args.elf),"source_sha256":{str(p.relative_to(ROOT)):sha(p) for p in tracked},
      "distinct_original_instruction_bytes":len(used),"original_instruction_trace":trace,
      "comparisons":out,
      "limits":[
      "Original 0x424be4 and direct private helpers 0x424120/0x4249a0/0x424a18 plus critical_save 0x41b8ec execute in stock; clock request/release and delay_us are intercepted as named synthetic providers.",
        "MSPI MMIO at 0x40060000 + module*0x1000 is synthetic Unicorn memory. No physical hardware or peripheral timing is tested.",
        "The 24-byte firmware config and private handle do not use the public 52-byte Ambiq HAL config ABI.",
        "This profile validates semantic equivalence for listed cases, not firmware linkage or byte identity."]}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"status":report["status"],"cases":report["cases"],
      "direct_private_helper_cases":private_cases,
      "distinct_original_instruction_bytes":len(used)}))

if __name__=="__main__": main()
