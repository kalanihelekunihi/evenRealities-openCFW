#!/usr/bin/env python3
"""Differentially execute stock SPOT callback 42A878 and its fixed-ABI C body."""
from __future__ import annotations
from pathlib import Path
import argparse, hashlib, importlib.util, itertools, json, struct
from unicorn import Uc, UcError, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as a

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/"AGENTS.md").exists())
IMAGE = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
EXPECTED_IMAGE = "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
ENTRY, END = 0x42A878, 0x42AB6E
EXPECTED_BODY = "83deb1cccedcf7dab0c986deaacc2f94baea6d1f74b7e7e387fbdb9f77527079"
TABLE_RECEIPT = ROOT / "g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize/gx-native/scatter-selector-table.json"
table_receipt = json.loads(TABLE_RECEIPT.read_text())
assert table_receipt["status"] == "PASS" and table_receipt["original_sha256"] == EXPECTED_IMAGE
selectors = table_receipt["selectors"]
actual_targets = [int(x["thumb_target"],16) for x in selectors]
BINDINGS=json.loads((HERE/"native-selector-bindings.json").read_text())["slots"]
STOP = 0x08000000
RAM_STACK = (0x2003D000, 0x20040000)

spec = importlib.util.spec_from_file_location(
    "elf_reader", ROOT / "g2/components/bootloader/update_core/elf_reader.py")
elf_reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(elf_reader)

ap = argparse.ArgumentParser()
ap.add_argument("--elf", type=Path, required=True)
ap.add_argument("--output", type=Path, required=True)
args = ap.parse_args()
blob = IMAGE.read_bytes()
assert hashlib.sha256(blob).hexdigest() == EXPECTED_IMAGE
original = blob[ENTRY - 0x410000:END - 0x410000]
assert len(original) == 758 and hashlib.sha256(original).hexdigest() == EXPECTED_BODY
_, segments, symbols = elf_reader.elf_info(args.elf)
assert "opencfw_boot_spotmgr_power_state_update_a" in symbols

symbols["event_a_transition_sequence_8_timer_disabled"]=symbols["event_a_transition_sequence_8_timer_native"]
SOURCE_NAMES = ["event_a_state_transition_sequence",
                "event_a_temperature_transition_separate",
                "event_a_transition_sequence_24",
                "event_a_transition_sequence_8_timer_disabled"]
assert all(n in symbols for n in SOURCE_NAMES), [n for n in SOURCE_NAMES if n not in symbols]
source_entries = {n: symbols[n] & ~1 for n in SOURCE_NAMES}

def pack(v): return struct.pack("<I", int(v) & 0xffffffff)
def read32(u,p): return struct.unpack("<I",u.mem_read(p,4))[0]
def write32(u,p,v): u.mem_write(p,pack(v))
def snapshot(u,p):
    return [read32(u,p+i*4) for i in range(4)] + [
        int(u.mem_read(p+0x10,1)[0]), int(u.mem_read(p+0x11,1)[0]),
        int(u.mem_read(p+0x12,1)[0])]

def init_memory(u, f, stock):
    write32(u,0x40021108,f.get("mode",0x30))
    write32(u,0x40021000,f.get("cpu_global",2))
    write32(u,0x40008800,f.get("sleep_mode",0))
    write32(u,0x400204d8,f.get("buck_flags",0))
    write32(u,0x40008010,f.get("descriptor_enable",0))
    callback_targets = actual_targets[:]
    if not stock:
        for i,name in BINDINGS.items():callback_targets[int(i)]=symbols[name]|1
    if stock:
        for i,target in enumerate(callback_targets):write32(u,0x20000158+4*i,target|1)
    write32(u,0x20026bf4,f.get("trim_cfg54",0x00123456))
    write32(u,0x20026bf8,f.get("trim_cfg58",0x000fedcb))
    write32(u,0x20026bfc,f.get("trim_cfg5c",0x000abcde))
    write32(u,0x20026c00,f.get("trim_cfg60",0x00013579))
    write32(u,0x40020344,f.get("trim_reg44",0x01020304))
    write32(u,0x40020354,f.get("trim_reg54",0x00543210))
    write32(u,0x40020358,f.get("trim_reg58",0x87654321))
    descriptors=f.get("descriptors",[])
    for slot in range(16):
        value=descriptors[slot] if slot<len(descriptors) else 0
        write32(u,0x40008200+slot*0x20,value)
    u.mem_write(0x200271bf,bytes([f.get("sleep_allowed",0)&255]))
    write32(u,0x20026ba0,f.get("profile",0x1f01600d))
    write32(u,0x40021008,f.get("device",0x00000400))
    write32(u,0x40021010,f.get("audio",0x00000020))
    write32(u,0x40021018,f.get("memory",0x00000008))
    write32(u,0x40021028,f.get("ssram",0x00000002))
    write32(u,0x20000150,f.get("old_major",1))
    write32(u,0x200001c4,f.get("old_minor",2))
    write32(u,0x20000144,f.get("aux_mode",9))
    u.mem_write(0x2002708c,bytes([f.get("state_flag",0)&255]))
    u.mem_write(0x200271be,bytes([f.get("current_cpu",0)&255]))
    u.mem_write(0x200271bd,bytes([f.get("current_temp",2)&255]))
    u.mem_write(0x200271a5,bytes([f.get("gpu_aux",0)&255]))
    u.mem_write(0x2000055a,bytes([f.get("simobuck",0)&255]))
    u.mem_write(0x200271af,bytes([f.get("trigger_flag",0xa5)&255]))
    u.mem_write(0x200271b0,bytes([f.get("power_domain_flag",0xa5)&255]))
    vals=f.get("args_words")
    if vals is None: vals=[f.get("arg",0),0xaaaaaaaa,0x55555555]
    if len(vals)<3: vals=list(vals)+[0xaaaaaaaa,0x55555555][:3-len(vals)]
    u.mem_write(0x20001000,b"".join(pack(v) for v in vals))

def provider_logs(u, state_records, sleep_records, trim_records):
    state = state_records[0] if state_records else None
    sleep = sleep_records[0] if sleep_records else None
    trim = trim_records[0] if trim_records else None
    return {
        "deepsleep": {"calls":len(sleep_records),
                      "before":sleep["snapshot"] if sleep else [0]*7,
                      "after":sleep["snapshot"] if sleep else [0]*7,
                      "flag_after":sleep["flag_after"] if sleep else 0},
        "determine": {"calls":len(state_records),
                      "snapshot":state["snapshot"] if state else [0]*7,
                      "outputs":[state["status"],state["major"],state["minor"]] if state else [0]*3},
        "trim": {"calls":len(trim_records),"args":trim["args"] if trim else [0]*4,
                 "config_registers":[read32(u,p) for p in (0x40020344,0x40020358)]},
        "temperature_transition":{"native":True},
        "state_sequence":{"native":True},
        "dispatch":{"native_table":True},
    }

def run(stock, f):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
    for lo,size in [(0,0x1000),(0x10000,0x10000),(0x30000,0x10000),(0x410000,0x25000),(0x08000000,0x1000),
                    (0x20000000,0x40000),(0x40000000,0x100000),(0xe000e000,0x1000),(0xe001e000,0x1000)]: u.mem_map(lo,size)
    if stock:
        u.mem_write(0x410000,blob)
    for seg in segments: u.mem_write(seg["address"],seg["data"])
    # Execute the actual source scatter adapter; guest table receives compiler relocations.
    if True:
        done=[False]
        def installer(cpu,pc,size,data):
            if pc==STOP:done[0]=True;cpu.emu_stop()
        handle=u.hook_add(UC_HOOK_CODE,installer)
        u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,STOP|1);u.reg_write(a.UC_ARM_REG_R0,0x433104);u.reg_write(a.UC_ARM_REG_R1,0);u.reg_write(a.UC_ARM_REG_R9,0)
        u.emu_start((0x415326 if stock else symbols["opencfw_boot_expand_adapter"])|1,0,count=200000);assert done[0];u.hook_del(handle)
        if not stock:
            for i,name in BINDINGS.items():assert read32(u,0x20000158+4*int(i))==symbols[name]|1
    init_memory(u,f,stock)
    # Run actual revision35/variant2 dispatcher; selected init takes proven OTP-unavailable return7.
    write32(u,0x4002000c,35);write32(u,0x20000098,2);write32(u,0x400201bc,8)
    registered=[False]
    def registration_hook(cpu,pc,size,data):
        if pc==STOP:registered[0]=True;cpu.emu_stop()
    rh=u.hook_add(UC_HOOK_CODE,registration_hook)
    u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,STOP|1)
    u.emu_start((0x41ce52 if stock else symbols["opencfw_boot_startup_spot_dispatch"])|1,0,count=10000)
    assert registered[0] and u.reg_read(a.UC_ARM_REG_R0)==7
    u.hook_del(rh)
    assert read32(u,0x20026e3c)==(0x42a879 if stock else symbols["opencfw_boot_spotmgr_power_state_update_a"]|1)
    assert read32(u,0x20026e64)==(0x42a04b if stock else symbols["opencfw_pcm22_timer_service"]|1)

    u.reg_write(a.UC_ARM_REG_SP,0x2003f000)
    u.reg_write(a.UC_ARM_REG_LR,STOP|1)
    u.reg_write(a.UC_ARM_REG_PRIMASK,f.get("primask",0))
    u.reg_write(a.UC_ARM_REG_R0,f.get("stimulus",0))
    u.reg_write(a.UC_ARM_REG_R1,f.get("on",0))
    u.reg_write(a.UC_ARM_REG_R2,0 if f.get("args_words") is None else 0x20001000)
    calls=[]; trace={}; finished=[False]
    state_pending={}; state_records=[]
    sleep_pending={}; sleep_records=[]
    trim_pending={}; trim_records=[]
    callback_calls=[];rom_delays=[]
    state_entry=0x42a550 if stock else (symbols["event_a_state_determine"] & ~1)
    sleep_entry=0x42a08c if stock else (symbols["event_a_deepsleep_state"] & ~1)
    trim_entry=0x42a4bc if stock else (symbols["event_a_power_trims_update"] & ~1)
    def on_code(cpu,pc,size,_):
        if pc==STOP:
            finished[0]=True;cpu.emu_stop();return
        if stock and ((ENTRY<=pc<END) or (0x427e0c<=pc<0x427e84) or
                      (0x42a19c<=pc<0x42a1b2) or (0x41b8ec<=pc<0x41b8f4) or
                      (0x42a08c<=pc<0x42a19c) or (0x41f3f0<=pc<0x41f420) or
                      (0x42a550<=pc<0x42a85e) or (0x42a4bc<=pc<0x42a550) or
                      (0x42a1bc<=pc<0x42a2a4) or (0x428d90<=pc<0x428e6a)):
            trace[pc]=bytes(cpu.mem_read(pc,size)).hex()
        if pc==0x40:
            rom_delays.append(cpu.reg_read(a.UC_ARM_REG_R0));cpu.reg_write(a.UC_ARM_REG_PC,cpu.reg_read(a.UC_ARM_REG_LR));return
        if pc == state_entry:
            ptr=cpu.reg_read(a.UC_ARM_REG_R0)
            lr=cpu.reg_read(a.UC_ARM_REG_LR)&~1
            rec={"snapshot":snapshot(cpu,ptr),
                 "major_ptr":cpu.reg_read(a.UC_ARM_REG_R1),
                 "minor_ptr":cpu.reg_read(a.UC_ARM_REG_R2),
                 "return_pc":lr}
            state_pending.setdefault(lr,[]).append(rec)
        if pc == sleep_entry:
            ptr=cpu.reg_read(a.UC_ARM_REG_R0)
            lr=cpu.reg_read(a.UC_ARM_REG_LR)&~1
            sleep_pending.setdefault(lr,[]).append({"snapshot":snapshot(cpu,ptr),"return_pc":lr})
        if pc == trim_entry:
            lr=cpu.reg_read(a.UC_ARM_REG_LR)&~1
            trim_pending.setdefault(lr,[]).append({"args":[cpu.reg_read(getattr(a,f"UC_ARM_REG_R{i}")) for i in range(4)],"return_pc":lr})
        sleeping=sleep_pending.get(pc)
        if sleeping:
            rec=sleeping.pop()
            rec["flag_after"]=int(cpu.mem_read(0x200271c0,1)[0])
            sleep_records.append(rec)
        trimming=trim_pending.get(pc)
        if trimming:
            trim_records.append(trimming.pop())
        pending=state_pending.get(pc)
        if pending:
            rec=pending.pop()
            rec.update({"status":cpu.reg_read(a.UC_ARM_REG_R0),
                        "major":read32(cpu,rec["major_ptr"]),
                        "minor":read32(cpu,rec["minor_ptr"])})
            state_records.append(rec)
        else:
            callback_targets = actual_targets[:]
            if not stock:
                for i,name in BINDINGS.items():callback_targets[int(i)]=symbols[name]|1
            for index,target in enumerate(callback_targets):
                target &= ~1
                if pc == target:
                    callback_calls.append({"selector":index,"target":hex(actual_targets[index]&~1),
                        "args":[cpu.reg_read(getattr(a,f"UC_ARM_REG_R{i}")) for i in range(4)]})
                    assert str(index) in BINDINGS,("unsupported callback",index,f)
                    break
    def forbid_stock(cpu,pc,size,data):
        if not stock and 0x410000<=pc<0x435000:raise AssertionError(("source executed locked instruction",hex(pc),f))
    u.hook_add(UC_HOOK_CODE,on_code)
    u.hook_add(UC_HOOK_CODE,forbid_stock)
    entry=0x41cd1b if stock else (symbols["power_state_wrapper"]|1)
    try:
        u.emu_start(entry,0,count=50000)
    except UcError as exc:
        raise AssertionError(("emulation fault",stock,f,hex(u.reg_read(a.UC_ARM_REG_PC)),str(exc))) from exc
    assert finished[0], (stock,f,hex(u.reg_read(a.UC_ARM_REG_PC)))
    globals_out={p:bytes(u.mem_read(p,n)).hex() for p,n in [
        (0x200271be,1),(0x200271bd,1),(0x200271af,1),(0x200271b0,1),
        (0x20000553,1),(0x20000150,4),(0x200001c4,4),(0x200271c0,1)]}
    call_output=provider_logs(u,state_records,sleep_records,trim_records)
    call_output["callbacks"]=callback_calls
    output={"status":u.reg_read(a.UC_ARM_REG_R0),"primask":u.reg_read(a.UC_ARM_REG_PRIMASK),"fpscr":u.reg_read(a.UC_ARM_REG_FPSCR),
            "args":bytes(u.mem_read(0x20001000,12)).hex(),"globals":globals_out,
            "power_registers":[read32(u,p) for p in (0x40021008,0x40021010,0x40021018,0x40021028,0x40020344,0x40020358)],
            "calls":call_output,"rom_delay_inputs":rom_delays}
    return output,trace

fixtures=[]
for old,target,flag in [(16,12,1)]:
 for mask in [0,1]:fixtures.append((f'natural-{old}-to-{target}-mask{mask}',dict(stimulus=3,on=0,args_words=[0],current_cpu=1,current_temp=3,state_flag=flag,gpu_aux=1,device=0,audio=0,memory=0,ssram=0,old_major=old,old_minor=1,primask=mask)))
rows=[];traces={}
for name,f in fixtures:
 x,t=run(True,f);y,_=run(False,f);assert x==y,(name,x,y);assert [v['selector'] for v in x['calls']['callbacks']]==[10],x['calls'];rows.append(dict(name=name,input=f,result=x));traces.update(t)
args.output.write_text(json.dumps(dict(status='PASS_NATIVE_SELECTOR10_CHAIN',cases=len(rows),elf_sha256=hashlib.sha256(args.elf.read_bytes()).hexdigest(),comparisons=rows,original_trace={hex(k):v for k,v in sorted(traces.items())},limits=['Synthetic state and MMIO; resident ROM delay40 stub only. Original and compiled dispatcher/updater/state/selector/TON execute.','Actual source scatter-installed slot10 points to independently compiled selector10. No guest table redirection. Offline fixture does not prove physical GPU/SDIO timing.']),indent=2));print('PASS native selector10 chains',len(rows))
