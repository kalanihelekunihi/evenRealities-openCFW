#!/usr/bin/env python3
"""Compare stock/source event-A default path with each real data installer.

Stock runs the locked scatter decoder; source runs the compiled source-owned
scatter adapter. Neither machine receives a manually seeded callback table.
The trace executes selector 24 (stock BX LR/source equivalent) and stops at
the first still-original selector target.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, struct
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn import arm_const as a

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
IMAGE=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
EXPECTED_IMAGE='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
EXPECTED_DATA='e3bea7ccd46bc324829152b5b5a9069aecce5db243876273084d29bd7d47b843'
EXPECTED_ELF='4b1fb7505187310b0b9bcd84f1479693a313db9485d4741960a1fbdf6210c645'
ENTRY,END=0x42a878,0x42ab6e
HANDLER_START,HANDLER_END=0x42962c,0x429700
HANDLER_SHA='2b4c090e8bf6f3a2913292d2a4c7b9e1c8ef90ea746d0575bdca6c8153cdca17'
STOP=0x08000000
BASE=0x410000

spec=importlib.util.spec_from_file_location('elf_reader',ROOT/'g2/components/bootloader/update_core/elf_reader.py')
elf=importlib.util.module_from_spec(spec);spec.loader.exec_module(elf)

def w(u,p,v): u.mem_write(p,struct.pack('<I',int(v)&0xffffffff))
def r(u,p,n=4): return bytes(u.mem_read(p,n))
def r32(u,p): return struct.unpack('<I',r(u,p,4))[0]

def init_profile(u):
    # A nonuniform recovered-format profile: rank inputs are initializer data;
    # core/tempco/VDDCLV are explicit synthetic valid profile values.
    raw=r(u,0x200000a4,84);vddc=struct.unpack('<21I',raw)
    raw=r(u,0x200000f4,84);vddf=struct.unpack('<21I',raw)
    profile=bytearray(0x80);struct.pack_into('<I',profile,0,0x1f01600d)
    for i in range(21):
        core=(i*37+11)&0x3ff;tempco=(i*3+5)&0xf
        val=(vddf[i]&0x7f)|(core<<7)|(tempco<<17)|((vddc[i]&0x7f)<<21)
        struct.pack_into('<I',profile,4+4*i,val)
    struct.pack_into('<I',profile,0x64,0x0a654321)
    u.mem_write(0x20026ba0,bytes(profile))
    return hashlib.sha256(profile).hexdigest()

def run(stock, elf_path, segments, symbols, temp):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
    for lo,size in [(BASE,0x25000),(0x10000,0x10000),(0x30000,0x10000),
                    (STOP,0x1000),(0x20000000,0x40000),(0x40000000,0x100000),
                    (0xe000e000,0x1000)]:u.mem_map(lo,size)
    if stock:u.mem_write(BASE,IMAGE_BYTES)
    else:
        for seg in segments:u.mem_write(seg['address'],seg['data'])
    w(u,0x20000000+0x10000,0)
    # First run the real installer/decoder into its normal fixed destination.
    boot=[False]
    def boot_hook(cpu,pc,size,_):
        if pc==STOP:boot[0]=True;cpu.emu_stop()
    u.hook_add(UC_HOOK_CODE,boot_hook)
    u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,STOP|1)
    if stock:
        u.reg_write(a.UC_ARM_REG_R0,0x433104)
        data_entry=0x415326
    else:
        u.reg_write(a.UC_ARM_REG_R0,0x433104);u.reg_write(a.UC_ARM_REG_R1,0)
        u.reg_write(a.UC_ARM_REG_R9,0)
        data_entry=symbols['opencfw_boot_expand_adapter']&~1
    u.emu_start(data_entry|1,0,count=200000)
    assert boot[0],('installer did not return',stock,hex(u.reg_read(a.UC_ARM_REG_PC)))
    scatter=json.loads((HERE.parent.parent/'startup-initialize/gx-native/scatter-selector-table.json').read_text())
    expected_targets=[int(x['thumb_target'],16) for x in scatter['selectors']]
    bindings=json.loads((HERE.parent.parent/'startup-initialize/pcm2_2-relocated/native-selector-bindings.json').read_text())['slots']
    init_bytes=bytearray(r(u,0x20000000,1371))
    targets_now=list(struct.unpack_from('<27I',init_bytes,0x158))
    if stock:
        assert hashlib.sha256(init_bytes).hexdigest()==EXPECTED_DATA
        assert targets_now==expected_targets
    else:
        for slot,name in bindings.items():
            assert targets_now[int(slot)]==(symbols[name]|1),(slot,name,hex(targets_now[int(slot)]),hex(symbols[name]|1))
            struct.pack_into('<I',init_bytes,0x158+4*int(slot),expected_targets[int(slot)])
        assert hashlib.sha256(init_bytes).hexdigest()==EXPECTED_DATA
    assert r32(u,0x20000150)==7 and r32(u,0x20000148)==7
    assert r32(u,0x2000014c)==6 and r32(u,0x20000154)==255
    profile_hash=init_profile(u)
    # Snapshot/IO stimulus is controlled while all decoded SPOT initializer
    # words and the installed callback table stay as written by the installer.
    w(u,0x40021108,0x30);w(u,0x40021000,2);w(u,0x40008800,0)
    w(u,0x400204d8,0);w(u,0x40008010,0)
    for p in (0x40021008,0x40021010,0x40021018,0x40021028):w(u,p,0)
    # Explicit synthetic register state for selector-16 trim writes. TIMER_A
    # is disabled, so no timer service or asynchronous readiness is invented.
    for p in (0x200270b0,0x200270b4,0x200270b8,0x200270bc,0x200270c0,0x200270c4,
              0x40020044,0x40020048,0x40020080,0x400083e8,0x40008010,
              0x40008068,0x4002037c,0x40004030,0x40004044):
        w(u,p,0x5a5a0000|(p&0xffff))
    w(u,0x400083e0,0);w(u,0x40008064,0);w(u,0x40021000,0)
    u.mem_write(0x2002708c,b'\x01');u.mem_write(0x200271be,b'\x00')
    u.mem_write(0x200271bd,b'\x02');u.mem_write(0x200271a5,b'\x00')
    u.mem_write(0x200271af,b'\xa5');u.mem_write(0x200271b0,b'\xa5')
    arg=struct.unpack('<I',struct.pack('<f',temp))[0];w(u,0x20001000,arg)
    targets=[r32(u,0x20000158+4*i) for i in range(27)]
    assert len(targets)==27 and all((x&1) for x in targets)
    seen=[];done=[False];rom_wait=[];mmio_writes=[];handler_visited=set()
    entries={i:(t&~1) for i,t in enumerate(targets)}
    def hook(cpu,pc,size,_):
        if pc==STOP:done[0]=True;cpu.emu_stop();return
        if stock and HANDLER_START<=pc<HANDLER_END:
            handler_visited.update(range(pc,min(pc+size,HANDLER_END)))
        if pc==0x40:
            rom_wait.append(cpu.reg_read(a.UC_ARM_REG_R0))
            cpu.reg_write(a.UC_ARM_REG_PC,cpu.reg_read(a.UC_ARM_REG_LR));return
        for index,target in entries.items():
            if pc!=target:continue
            lr=cpu.reg_read(a.UC_ARM_REG_LR)&~1
            record={'selector':index,'pc':hex(pc),'target_thumb':hex(targets[index]),
                'caller_return':hex(lr),'args':[cpu.reg_read(getattr(a,f'UC_ARM_REG_R{k}')) for k in range(4)],
                'sp':hex(cpu.reg_read(a.UC_ARM_REG_SP)),
                'primask':cpu.reg_read(a.UC_ARM_REG_PRIMASK),
                'current_major':r32(cpu,0x20000150),'ton':r32(cpu,0x2000014c),
                'timer':r32(cpu,0x20000154)}
            seen.append(record)
            # Execute stock BX LR slots and the authenticated selector-16
            # body; source slots execute only when natively bound.
            if (stock and index in (16,24,25,26)) or (not stock and str(index) in bindings):return
            cpu.emu_stop();return
    def write_hook(cpu,access,addr,size,value,_):
        if 0x40000000<=addr<0x40100000:
            mmio_writes.append([addr,size,value&((1<<(8*size))-1)])
    u.hook_add(UC_HOOK_CODE,hook)
    u.hook_add(UC_HOOK_MEM_WRITE,write_hook,begin=0x40000000,end=0x400fffff)
    u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,STOP|1)
    u.reg_write(a.UC_ARM_REG_PRIMASK,0)
    u.reg_write(a.UC_ARM_REG_R0,2);u.reg_write(a.UC_ARM_REG_R1,0)
    u.reg_write(a.UC_ARM_REG_R2,0x20001000)
    event_entry=ENTRY if stock else symbols['opencfw_boot_spotmgr_power_state_update_a']&~1
    u.emu_start(event_entry|1,0,count=150000)
    table=[hex(x) for x in targets]
    return {'side':'stock' if stock else 'source','temp':temp,'profile_sha256':profile_hash,
        'callback_table':table,'callbacks':seen,'rom_wait_arguments':rom_wait,
        'mmio_writes':mmio_writes,
        'stock_handler16_byte_addresses':sorted(handler_visited),
        'return_regs':[u.reg_read(a.UC_ARM_REG_R0),u.reg_read(a.UC_ARM_REG_R1)],
        'callee_saved':[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4,12)],
        'sp':hex(u.reg_read(a.UC_ARM_REG_SP)),
        'completed_to_stop':done[0] or ((u.reg_read(a.UC_ARM_REG_PC)&~1)==STOP),
        'stopped_at':hex(u.reg_read(a.UC_ARM_REG_PC)&~1),
        'state':{'major':r32(u,0x20000150),'ton':r32(u,0x2000014c),
            'timer':r32(u,0x20000154),'cpu':r(u,0x200271be,1).hex(),
            'temperature_class':r(u,0x200271bd,1).hex()},
        'args_after':r(u,0x20001000,12).hex(),
        'stopped_at_unresolved':bool(not done[0] and (u.reg_read(a.UC_ARM_REG_PC)&~1)!=STOP)}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True)
    ap.add_argument('--output',type=Path,default=HERE/'default-native-comparison.json');args=ap.parse_args()
    global IMAGE_BYTES
    IMAGE_BYTES=IMAGE.read_bytes()
    assert hashlib.sha256(IMAGE_BYTES).hexdigest()==EXPECTED_IMAGE
    handler=IMAGE_BYTES[HANDLER_START-BASE:HANDLER_END-BASE]
    assert len(handler)==HANDLER_END-HANDLER_START and hashlib.sha256(handler).hexdigest()==HANDLER_SHA
    _,segments,symbols=elf.elf_info(args.elf)
    assert hashlib.sha256(args.elf.read_bytes()).hexdigest()==EXPECTED_ELF
    assert 'opencfw_boot_expand_adapter' in symbols
    assert 'opencfw_boot_spotmgr_power_state_update_a' in symbols
    rows=[]
    for temp in (0.0,49.5,50.0):
        rows.append({'stock':run(True,args.elf,segments,symbols,temp),
                     'source':run(False,args.elf,segments,symbols,temp)})
    for row in rows:
        s=row['stock'];c=row['source']
        # Normalize code addresses while enforcing the observable contract.
        assert [x['selector'] for x in s['callbacks']]==[x['selector'] for x in c['callbacks']]
        assert [x['args'] for x in s['callbacks']]==[x['args'] for x in c['callbacks']]
        assert [x['current_major'] for x in s['callbacks']]==[x['current_major'] for x in c['callbacks']]
        expected_major=4 if c['temp']==50.0 else 5
        assert s['completed_to_stop'] and c['completed_to_stop']
        assert s['state']==c['state'] and s['args_after']==c['args_after']
        assert s['return_regs'][0]==c['return_regs'][0] and s['mmio_writes']==c['mmio_writes']
        assert s['rom_wait_arguments']==c['rom_wait_arguments']
        assert s['callee_saved']==c['callee_saved'] and s['sp']==c['sp']
        assert s['state']['major']==c['state']['major']==expected_major
    handler_coverage=set()
    for row in rows:
        handler_coverage.update(row['stock']['stock_handler16_byte_addresses'])
    result={'status':'PASS','elf_sha256':hashlib.sha256(args.elf.read_bytes()).hexdigest(),
        'image_sha256':EXPECTED_IMAGE,'comparison_count':len(rows),
        'stock_selector16_range':['0x42962c','0x429700'],
        'stock_selector16_sha256':HANDLER_SHA,
        'stock_selector16_visited_bytes':len(handler_coverage),
        'method':'Original 0x415326 scatter decoder vs compiled-source expand adapter; their own installed tables drive stock/source callback implementations.',
        'limits':['Table contents are never seeded by the harness. The source table is produced by the compiled-source adapter; its relocated pointers are checked against the recorded native-slot map, then normalized to authenticate the initializer.',
                  'Selector24 and the authenticated stock selector16 body execute in both implementations. TIMER_A is initialized disabled. ROM address 0x40 is a synthetic immediate cycle-wait return if reached; each call/argument is recorded.',
                  'The uint32 callback result in R0, final state, MMIO write order, arguments, callee-saved registers, and final SP match. Caller-saved R1 differs (stock leaves 0x20000144; source leaves 6) and is recorded, not claimed equivalent.',
                  'Profile rank words come from each installed initializer; remaining profile fields are explicit synthetic recovered-format inputs.',
                  'Offline deterministic MMIO only; no physical SPOT or scheduler behavior claimed.'],
        'cases':rows}
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS',len(rows),'stock/source callback cases; selector paths',[[v['selector'] for v in x['stock']['callbacks']] for x in rows])
if __name__=='__main__':main()
