#!/usr/bin/env python3
"""Direct locked/source differential for root-reachable PCM2.2 handlers 0 and 2."""
from __future__ import annotations
from pathlib import Path
import argparse, hashlib, importlib.util, json, struct
from unicorn import Uc, UcError, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn import arm_const as a

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
IMAGE = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
TABLE = ROOT / "g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize/gx-native/scatter-selector-table.json"
REACH = ROOT / "g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize/pcm2_2-native/stock-root-targets.json"
IMAGE_SHA = "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
STOP = 0x08000000
PROFILE = 0x20026ba0
TABLE_ADDR = 0x20000158

spec = importlib.util.spec_from_file_location(
    "elf_reader", ROOT / "g2/components/bootloader/update_core/elf_reader.py")
elf_reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(elf_reader)

ap = argparse.ArgumentParser()
ap.add_argument("--elf", type=Path, required=True)
ap.add_argument("--output", type=Path, required=True)
args = ap.parse_args()
blob = IMAGE.read_bytes()
assert hashlib.sha256(blob).hexdigest() == IMAGE_SHA
table = json.loads(TABLE.read_text())
reach = json.loads(REACH.read_text())
assert table["status"] == "PASS" and table["original_sha256"] == IMAGE_SHA
assert reach["status"] == "OBSERVED" and reach["original_sha256"] == IMAGE_SHA
target_by_selector = {int(x["selector"]): x for x in table["selectors"]}
vectors = {0: [7,3,6,0], 2: [3,7,0,6]}
for selector, values in vectors.items():
    entry = int(target_by_selector[selector]["thumb_target"],16) & ~1
    observed = reach["selected_targets"][str(selector)]
    assert int(observed["entry"],16) == entry
    assert observed["calls"] > 0
    assert set(map(tuple, observed["arguments"])) == {tuple(values)}

_, segments, symbols = elf_reader.elf_info(args.elf)
source_names = {0:"event_a_pcm22_transition_sequence_0",
                2:"event_a_pcm22_transition_sequence_2"}
assert all(name in symbols for name in source_names.values()), {
    name: symbols.get(name) for name in source_names.values()}
stock_entries = {i:int(target_by_selector[i]["thumb_target"],16)&~1
                 for i in source_names}

def pack(value): return struct.pack("<I", int(value)&0xffffffff)
def get32(u,address): return struct.unpack("<I",u.mem_read(address,4))[0]
def put32(u,address,value): u.mem_write(address,pack(value))

def seed(u, selector, timer_enabled=False, cache_enabled=False,
         service_state=0x1a, cached_current=False):
    # Match the locked target profile shape and the direct root arguments.
    info = bytearray(0x6c)
    struct.pack_into("<I",info,0,0x1f01600d)
    for index in range(21):
        vfact=(11+index*3)%128
        core=(81+index*17)%1024
        tempco=(2+index)%16
        vddc=(23+index*5)%128
        word=vfact|(core<<7)|(tempco<<17)|(vddc<<21)
        struct.pack_into("<I",info,4+4*index,word)
    for offset,value in ((0x54,0x00a952a5),(0x58,0x00123456),
                         (0x5c,0x0019b5c6),(0x60,0x0000e789),
                         (0x64,0x0000c321),(0x68,0x0002a135)):
        struct.pack_into("<I",info,offset,value)
    u.mem_write(PROFILE,bytes(info))
    for index in range(27): put32(u,TABLE_ADDR+4*index,0)
    put32(u,0x400083e0,0x111 if timer_enabled else 0x110)
    # Enabled cases report the stock ISR ready bit, exercising timer service
    # without modeling an unbounded peripheral wait.
    put32(u,0x40008064,0x40000000 if timer_enabled else 0)
    put32(u,0x40008010,0)
    put32(u,0xe000ed14,0x20000 if cache_enabled else 0)
    put32(u,0xe001e300,0)
    put32(u,0x20000154,7 if cached_current else 0xffffffff)
    u.mem_write(0x2000055a,bytes((service_state,)))
    for addr,value in ((0x40020044,0xa5000014),(0x4002004c,0x5a000026),
                       (0x40020080,0x15550000|900),(0x4002037c,0x80000000),
                       (0x40020344,0x11112222),(0x40020354,0x55556666),
                       (0x40020358,0x77778888),(0x40020380,0x90000000),
                       (0x400201b0,0x40000000)):
        put32(u,addr,value)
    for addr,value in ((0x200270b0,0),(0x200270b4,0),(0x200270b8,0),
                       (0x200270bc,0),(0x200270c0,0),(0x200270c4,0),
                       (0x200270a4,5),(0x200270a8,41),(0x200270ac,37)):
        put32(u,addr,value)
    u.mem_write(0x20026e74,bytes(56))
    u.mem_write(0x20000550,b"\x01")
    u.mem_write(0x20027030,pack(0));u.mem_write(0x20027044,pack(0))
    u.mem_write(0x2002719c,b"\x00");u.mem_write(0x2002719e,b"\x00")
    if selector == 0: return vectors[0]
    return vectors[2]

def run(stock, selector, timer_enabled=False, cache_enabled=False,
        service_state=0x1a, cached_current=False):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
    for lo,size in ((0,0x1000),(0x410000,0x25000),(0x08000000,0x20000),
                    (0x10000,0x10000),(0x30000,0x80000),(0x20000000,0x40000),
                    (0x40000000,0x300000),(0xe0000000,0x200000),(0x47ff0000,0x10000)):
        u.mem_map(lo,size)
    if stock: u.mem_write(0x410000,blob)
    else:
        for segment in segments: u.mem_write(segment["address"],segment["data"])
    call_args=seed(u,selector,timer_enabled,cache_enabled,
                   service_state,cached_current)
    u.reg_write(a.UC_ARM_REG_SP,0x2003f000)
    u.reg_write(a.UC_ARM_REG_LR,STOP|1)
    u.reg_write(a.UC_ARM_REG_PRIMASK,0)
    for index,value in enumerate(call_args):
        u.reg_write(getattr(a,f"UC_ARM_REG_R{index}"),value)
    done=[False];rom_events=[];writes=[];trace={}
    def on_write(cpu,access,address,size,value,_):
        if (address < 0x20030000 or 0x40000000 <= address < 0x40300000 or
                0xe0000000 <= address < 0xe0020000):
            writes.append((address,size,value & ((1 << (8*size))-1)))
    def on_code(cpu,pc,size,_):
        if pc==STOP:
            done[0]=True;cpu.emu_stop();return
        if pc==0x40:
            # The absent resident ROM delay routine is the only controlled
            # service boundary; record input and return void to its caller.
            rom_events.append(cpu.reg_read(a.UC_ARM_REG_R0))
            cpu.reg_write(a.UC_ARM_REG_PC,cpu.reg_read(a.UC_ARM_REG_LR));return
        if stock and 0x410000<=pc<0x435000:
            trace[pc]=bytes(cpu.mem_read(pc,size)).hex()
        if not stock and 0x410000<=pc<0x435000:
            raise AssertionError(("source machine reached locked image",hex(pc)))
    u.hook_add(UC_HOOK_CODE,on_code)
    u.hook_add(UC_HOOK_MEM_WRITE,on_write,begin=0x20000000,end=0x2003ffff)
    u.hook_add(UC_HOOK_MEM_WRITE,on_write,begin=0x40000000,end=0x402fffff)
    u.hook_add(UC_HOOK_MEM_WRITE,on_write,begin=0xe0000000,end=0xe001ffff)
    entry=stock_entries[selector] if stock else (symbols[source_names[selector]]&~1)
    try: u.emu_start(entry|1,0,count=800000)
    except UcError as exc:
        raise AssertionError(("handler fault",stock,selector,hex(u.reg_read(a.UC_ARM_REG_PC)),str(exc))) from exc
    assert done[0],("handler did not return",stock,selector,hex(u.reg_read(a.UC_ARM_REG_PC)))
    state=[ [f"{address:08x}",size,f"{value:0{size*2}x}"]
            for address,size,value in writes ]
    return {"r0":u.reg_read(a.UC_ARM_REG_R0),"primask":u.reg_read(a.UC_ARM_REG_PRIMASK),
            "sp":u.reg_read(a.UC_ARM_REG_SP),"writes":state,"rom_delay_calls":rom_events,
            "trace":trace}

comparisons=[]
for selector in (0,2):
  modes=[(False,False,0x1a,False),(False,True,0x1a,False)]
  modes += [(True,cache,state,False) for cache in (False,True)
            for state in (0x1a,2,7,26)]
  if selector==0:
    modes += [(True,False,0x1a,True),(True,True,0x1a,True)]
  for timer_enabled,cache_enabled,service_state,cached_current in modes:
    original=run(True,selector,timer_enabled,cache_enabled,
                 service_state,cached_current)
    source=run(False,selector,timer_enabled,cache_enabled,
               service_state,cached_current)
    assert {k:v for k,v in original.items() if k!="trace"} == \
           {k:v for k,v in source.items() if k!="trace"}, (selector,timer_enabled,cache_enabled,service_state,cached_current,original,source)
    assert original["trace"]
    comparisons.append({"selector":selector,"entry":hex(stock_entries[selector]),
        "expected_arguments":vectors[selector],"timer_enabled":timer_enabled,
        "icache_enabled":cache_enabled,"service_state":service_state,
        "cached_current":cached_current,
        "stock":{k:v for k,v in original.items() if k!="trace"},
        "source":{k:v for k,v in source.items() if k!="trace"},
        "stock_trace_instructions":len(original["trace"])})

out={"status":"PASS","image_sha256":IMAGE_SHA,
     "source_elf_sha256":hashlib.sha256(args.elf.read_bytes()).hexdigest(),
     "runner_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
     "reachable_trace_receipt":str(REACH.relative_to(ROOT)),
     "callback_table_receipt":str(TABLE.relative_to(ROOT)),
     "controlled_external_boundary":"resident ROM delay at Thumb address 0x41; input captured, void return only",
     "comparisons":comparisons,
     "limits":["RAM/MMIO inputs use a deterministic root-profile fixture; the trace receipt supplies actual root argument vectors.",
               "No stock executable is loaded or entered in the source machine.",
               "ROM delay timing is outside the OTA image and is controlled at its actual call address."]}
args.output.write_text(json.dumps(out,indent=2)+"\n")
print("PASS selectors 0 and 2 across timer/cache modes",vectors)
