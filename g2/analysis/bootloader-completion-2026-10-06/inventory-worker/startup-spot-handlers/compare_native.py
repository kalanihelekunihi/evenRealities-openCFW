#!/usr/bin/env python3
"""Compare locked startup handlers with fixed-address C hypotheses in Unicorn.

Only stock helper 0x421548 (INFO provider) is cut.  Stock 0x41cc04 executes
from the image; the source module's corresponding leaf writes the same MMIO.
The ROM 0x48 function is not reached by these callbacks once 0x421548 is cut.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, itertools, json, struct
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn import arm_const as a

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
IMAGE = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
ELF_READER = ROOT / "g2/components/bootloader/update_core/elf_reader.py"
EXPECTED = "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
spec = importlib.util.spec_from_file_location("elf_reader", ELF_READER)
elf_reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(elf_reader)

ap = argparse.ArgumentParser()
ap.add_argument("--elf", type=Path, default=Path("/tmp/startup-spot-handlers.elf"))
ap.add_argument("--output", type=Path, default=HERE / "comparison.json")
args = ap.parse_args()
blob = IMAGE.read_bytes()
image_sha = hashlib.sha256(blob).hexdigest()
assert image_sha == EXPECTED, image_sha
_, segments, symbols = elf_reader.elf_info(args.elf)
ENTRY = {
    "42abbc": (0x42abbc, "spotmgr_init_42abbc_native", 0x42ac4e),
    "42bdf0": (0x42bdf0, "hw_state_compose_42bdf0_native", 0x42bf4e),
    "42d6c0": (0x42d6c0, "bl_bl009_dispatch_native", 0x42d79e),
    "42f670": (0x42f670, "startup_noop_42f670_native", 0x42f674),
}
PROFILE = 0x20026ba0
READ = 0x421548
COMMIT = 0x41cc04
STOP = 0x08000000
PROVIDERS = {"calls": "startup_test_calls", "words": "startup_test_words",
             "status": "startup_test_status", "log": "startup_test_call_log",
             "commits": "startup_test_commits"}
base_words = []
for n, count in enumerate((20, 5, 1)):
    base_words.append([((0x81234567 + i * 0x01020304 + n * 0x11100000) & 0xffffffff)
                       for i in range(count)])
# Distinct bit fields force the averaging and rearrangement paths in 42bdf0.
base_words[0][10] = 0x10000000 | (33 << 21) | 0x4567
base_words[0][12] = 0x10000000 | (12 << 21) | (5 << 17) | (0x155 << 7) | 0x51
base_words[0][13] = 0x10000000 | (18 << 21) | (9 << 17) | (0x2aa << 7) | 0x62

def pack(v): return struct.pack("<I", v & 0xffffffff)
def read32(u, p): return struct.unpack("<I", u.mem_read(p, 4))[0]
def set32(u, p, v): u.mem_write(p, pack(v))

def initial_state(u, fixture):
    for p in range(PROFILE, PROFILE + 27 * 4, 4): set32(u, p, (0xa5a50000 + p - PROFILE) & 0xffffffff)
    set32(u, 0x400201bc, fixture.get("power", 0))
    set32(u, 0x40021008, fixture.get("kernel", 0))
    set32(u, 0x400083e0, 0x51)
    set32(u, 0x40008060, 0x100)
    set32(u, 0x4002000c, fixture.get("revision", 0))
    set32(u, 0x20000098, fixture.get("variant", 0))
    set32(u, 0x2002683c, fixture.get("state_word", 0))
    u.mem_write(0x200271b3, bytes(fixture.get("flags", [0xa5, 0xa5, 0xa5])))

def run(stock, key, fixture):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
    for lo, size in [(0,0x1000),(0x410000,0x25000),(0x08000000,0x1000),
                     (0x10000,0x10000),(0x20000000,0x40000),(0x40000000,0x100000)]:
        u.mem_map(lo, size)
    if stock:
        u.mem_write(0x410000, blob)
    else:
        for seg in segments: u.mem_write(seg["address"], seg["data"])
        # Configure the scriptable provider data/status through ELF globals.
        for n, val in enumerate(fixture.get("statuses", [0,0,0])):
            set32(u, symbols[PROVIDERS["status"]] + 4*n, val)
        for n, arr in enumerate(base_words):
            for i, val in enumerate(arr):
                set32(u, symbols[PROVIDERS["words"]] + (n*20+i)*4, val)
    initial_state(u, fixture)
    calls=[]; mmio=[]; trace={}; done=[False]
    def hook(cpu, pc, size, _):
        if pc == STOP:
            done[0]=True; cpu.emu_stop(); return
        if stock and 0x410000 <= pc < 0x435000:
            trace[pc]=bytes(cpu.mem_read(pc,size)).hex()
        if stock and pc == READ:
            n=len(calls)
            selector=cpu.reg_read(a.UC_ARM_REG_R0); offset=cpu.reg_read(a.UC_ARM_REG_R1)
            count=cpu.reg_read(a.UC_ARM_REG_R2); dst=cpu.reg_read(a.UC_ARM_REG_R3)
            calls.append([selector,offset,count,"profile" if PROFILE <= dst < PROFILE+108 else "stack"])
            for i in range(count):
                v=base_words[n][i] if i < len(base_words[n]) else 0
                cpu.mem_write(dst+4*i,pack(v))
            status=fixture.get("statuses",[0,0,0])[n]
            cpu.reg_write(a.UC_ARM_REG_R0,status)
            cpu.reg_write(a.UC_ARM_REG_PC,cpu.reg_read(a.UC_ARM_REG_LR))
        if not stock and 0x410000 <= pc < 0x435000:
            trace[pc]=bytes(cpu.mem_read(pc,size)).hex()
    def write(cpu, access, address, size, value, _):
        if address >= 0x40000000:
            mmio.append([address,size,value & ((1 << (size*8))-1)])
    u.hook_add(UC_HOOK_CODE,hook)
    u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0x40000000,end=0x400fffff)
    u.reg_write(a.UC_ARM_REG_SP,0x2003f000)
    u.reg_write(a.UC_ARM_REG_LR,STOP|1)
    if stock:
        pc=ENTRY[key][0]
    else:
        pc=symbols[ENTRY[key][1]] & ~1
    u.emu_start(pc|1, 0, count=10000)
    assert done[0], (key,fixture,"did not return",hex(u.reg_read(a.UC_ARM_REG_PC)))
    if not stock:
        n=read32(u,symbols[PROVIDERS["calls"]])
        for i in range(n):
            base=symbols[PROVIDERS["log"]]+i*16
            dst=read32(u,base+12)
            calls.append([read32(u,base),read32(u,base+4),read32(u,base+8),
                          "profile" if PROFILE <= dst < PROFILE+108 else "stack"])
    data={"ret":u.reg_read(a.UC_ARM_REG_R0),
          "profile":bytes(u.mem_read(PROFILE,108)).hex(),
          "flags":bytes(u.mem_read(0x200271b3,3)).hex(),
          "calls":calls,"mmio":mmio}
    if not stock:
        data["commits"]=read32(u,symbols[PROVIDERS["commits"]])
    else:
        data["commits"]=sum(1 for p in trace if p==COMMIT) # body-entry trace, at most once
    return data, trace

fixtures=[]
for key in ("42abbc","42bdf0"):
    fixtures.append((key,"success",dict(power=0,kernel=0,statuses=[0,0,0])))
    fixtures.append((key,"blocked",dict(power=8,kernel=0,statuses=[0,0,0])))
    for fail in range(3):
        statuses=[0,0,0]; statuses[fail]=0x31+fail
        fixtures.append((key,f"read-error-{fail+1}",dict(power=8,kernel=0x08000000,statuses=statuses)))
for rev,var,word in [(0x21,2,0),(0x21,3,0),(0x22,0,0),(0x22,1,0),
                     (0x23,0,0x2e000000),(0x23,0,0x32000000),
                     (0x23,0,0x31940000),(0x20,9,0xffffffff)]:
    fixtures.append(("42d6c0",f"rev{rev:02x}-variant{var}-word{word:08x}",
                     dict(revision=rev,variant=var,state_word=word)))
fixtures.append(("42f670","return-zero",{}))

rows=[]; traces={"stock":{},"source":{}}
for key,label,fixture in fixtures:
    stock, st=run(True,key,fixture); source, so=run(False,key,fixture)
    # The C provider logs destination categories because ABI stack addresses differ.
    if stock != source:
        args.output.with_suffix(".failure.json").write_text(json.dumps(
            {"handler":key,"fixture":label,"stock":stock,"source":source},indent=2)+"\n")
        raise SystemExit(f"MISMATCH {key} {label}: stock={stock} source={source}")
    rows.append({"handler":key,"fixture":label,"result":stock})
    for p,b in st.items(): traces["stock"][p]=b
    for p,b in so.items(): traces["source"][p]=b

# Authenticated trace checks and union coverage over the exact firmware extents.
for p,b in traces["stock"].items():
    raw=bytes.fromhex(b)
    assert blob[p-0x410000:p-0x410000+len(raw)]==raw
coverage={}
for key,(entry,_,end) in ENTRY.items():
    seen={p+i for p,b in traces["stock"].items() for i in range(len(bytes.fromhex(b)))
          if entry <= p < end}
    coverage[key]={"extent_bytes":end-entry,"visited_bytes":len(seen),
                   "unvisited_bytes":(end-entry)-len(seen)}
out={"status":"PASS","cases":len(rows),"image_sha256":image_sha,
     "source_elf_sha256":hashlib.sha256(args.elf.read_bytes()).hexdigest(),
     "runner_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
     "coverage":coverage,"comparisons":rows,
     "stock_instruction_trace":{hex(p):b for p,b in sorted(traces["stock"].items())},
     "limits":[
       "Only the stock 0x421548 INFO helper is intercepted; args/order, scripted response bytes and partial visible writes are compared. The ROM reader behind 0x4213e6/0x41d28a is outside this callback test.",
       "Stock 0x41cc04 executes from the locked image. The independently compiled helper duplicates its MMIO side effects; both write sequences are compared.",
       "Tests use deterministic memory/MMIO fixtures, not physical OTP or hardware acknowledgements. This is a bounded semantic comparison, not a full firmware build or byte-equivalence claim."]}
args.output.write_text(json.dumps(out,indent=2)+"\n")
print("PASS",len(rows),"native comparisons",coverage)
