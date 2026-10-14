#!/usr/bin/env python3
"""Compare Main MSPI transfer selector 34 with locked native code."""
import argparse, hashlib, itertools, json, random
from collections import Counter
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as R

ROOT=Path(__file__).resolve().parents[4]
BLOB=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
blob=BLOB.read_bytes();assert hashlib.sha256(blob).hexdigest()==SHA
p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args()
with a.elf.open('rb') as f:
    elf=ELFFile(f)
    segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD' and s['p_filesz']]
    syms={s.name:s['st_value']&~1 for s in elf.get_section_by_name('.symtab').iter_symbols()}
HANDLE,CFG,PAIRS,OUT,QUEUE,SLOTS,MMIO,RET=0x20006000,0x20008000,0x20008100,0x20008200,0x20009000,0x2000a000,0x40060000,0x200ff000
NATIVE={0x538ece:'reserve',0x538fb4:'commit',0x538f82:'rollback',
        0x4bfa10:'flags',0x4bfd44:'start',0x473940:'critical'}
SOURCE={syms[name]:label for name,label in (
    ('g2_main_cq_reserve_538ece','reserve'),('g2_main_cq_commit_538fb4','commit'),
    ('g2_main_cq_rollback_538f82','rollback'),('g2_main_mspi_queue_flags_4bfa10','flags'),
    ('g2_main_mspi_queue_start_4bfd44','start'),('g2_main_critical_save_473940','critical'))}

def run(source,module,count,callback,mode,queue_mode,threshold,previous,reserve_result,commit_result,start_result,saved,output_present,pattern,valid=True,enabled=True,config=True,queue_present=True):
    cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    cpu.mem_map(0x430000,0x380000);cpu.mem_write(0x437fe0,blob)
    cpu.mem_map(0x800000,0x10000)
    for address,body in segments:cpu.mem_write(address,body)
    cpu.mem_map(0x20000000,0x100000);cpu.mem_map(MMIO,0x4000)
    cpu.mem_write(MMIO,bytes([pattern])*0x4000)
    for address,size in ((HANDLE,0x900),(CFG,0x40),(PAIRS,0x80),(OUT,0x20),(SLOTS,0x100)):
        cpu.mem_write(address,bytes([pattern])*size)
    cpu.mem_write(HANDLE,(0x01bebebe if valid else 0).to_bytes(4,'little'))
    cpu.mem_write(HANDLE+4,module.to_bytes(4,'little'))
    cpu.mem_write(HANDLE+8,bytes([int(enabled)]))
    cpu.mem_write(HANDLE+0x20,previous.to_bytes(4,'little'))
    cpu.mem_write(HANDLE+0x828,(QUEUE if queue_present else 0).to_bytes(4,'little'))
    cpu.mem_write(HANDLE+0x82c,bytes([queue_mode]))
    cpu.mem_write(HANDLE+0x82d,bytes([1]))
    cpu.mem_write(HANDLE+0x838,mode.to_bytes(4,'little'))
    cpu.mem_write(HANDLE+0x858,(2).to_bytes(4,'little'))
    cpu.mem_write(HANDLE+0x85c,threshold.to_bytes(4,'little'))
    values=(0x21,0x1234,PAIRS,count,callback,0xdeadbeef,OUT if output_present else 0)
    for i,value in enumerate(values):cpu.mem_write(CFG+i*4,value.to_bytes(4,'little'))
    for i in range(12):cpu.mem_write(PAIRS+i*4,(0x10100000+i*0x111).to_bytes(4,'little'))
    cpu.reg_write(R.UC_ARM_REG_R0,HANDLE)
    cpu.reg_write(R.UC_ARM_REG_R1,34)
    cpu.reg_write(R.UC_ARM_REG_R2,CFG if config else 0)
    cpu.reg_write(R.UC_ARM_REG_SP,0x200fe000)
    cpu.reg_write(R.UC_ARM_REG_LR,RET|1)
    helpers=SOURCE if source else NATIVE;events=[]
    def hook(machine,pc,_size,_user):
        if pc==RET:machine.emu_stop();return
        if pc not in helpers:return
        label=helpers[pc];r0=machine.reg_read(R.UC_ARM_REG_R0);r1=machine.reg_read(R.UC_ARM_REG_R1)
        events.append((label,r0 if label!='critical' else None,
                       r1 if label in ('reserve','commit','flags') else None))
        if label=='reserve':
            result=reserve_result
            if result==0:
                machine.mem_write(machine.reg_read(R.UC_ARM_REG_R2),SLOTS.to_bytes(4,'little'))
                machine.mem_write(machine.reg_read(R.UC_ARM_REG_R3),(7).to_bytes(4,'little'))
        elif label=='flags':result=0x4100|r1
        elif label=='critical':result=saved
        elif label=='commit':result=commit_result
        elif label=='rollback':result=0
        else:result=start_result
        machine.reg_write(R.UC_ARM_REG_R0,result)
        machine.reg_write(R.UC_ARM_REG_PC,machine.reg_read(R.UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE,hook)
    entry=syms['g2_main_mspi_transfer_descriptor_candidate'] if source else 0x4c0f78
    cpu.emu_start(entry|1,RET+2,count=20000)
    assert cpu.reg_read(R.UC_ARM_REG_PC)==RET
    return (cpu.reg_read(R.UC_ARM_REG_R0),events,
            bytes(cpu.mem_read(HANDLE,0x900)),bytes(cpu.mem_read(SLOTS,0x100)),
            bytes(cpu.mem_read(OUT,0x20)),bytes(cpu.mem_read(MMIO,0x4000)))

all_cases=list(itertools.product((0,2),(0,1,2),(0,0x4c0701),(0,1),(0,1),
                                 (0,1),(0,1,0x100),(0,5),(0,7),(0,4),(0,1),
                                 (False,True),(0,0xa5)))
fixtures=random.Random(526).sample(all_cases,1200)
fixtures += [(0,2,0,0,0,1,0,0,0,0,0,True,0),
             (0,1,0x4c0701,0,0,0,0,0,0,0,0,False,0)]
paths=Counter()
for index,fixture in enumerate(fixtures):
    native=run(False,*fixture);candidate=run(True,*fixture)
    paths['>'.join(event[0] for event in native[1]) or 'validation_only']+=1
    if native!=candidate:
        diff=[(field,hex(i),hex(x),hex(y)) for field in range(2,6)
              for i,(x,y) in enumerate(zip(native[field],candidate[field])) if x!=y]
        raise AssertionError((index,fixture,native[:2],candidate[:2],diff[:16]))
validation=[(0,0,0,0,0,0,0,0,0,0,0,False,0,False,True,True,True),
            (0,0,0,0,0,0,0,0,0,0,0,False,0,True,False,True,True),
            (0,0,0,0,0,0,0,0,0,0,0,False,0,True,True,False,True),
            (0,0,0,0,0,0,0,0,0,0,0,False,0,True,True,True,False)]
for fixture in validation:
    native=run(False,*fixture);candidate=run(True,*fixture)
    paths['>'.join(event[0] for event in native[1]) or 'validation_only']+=1
    if native!=candidate:raise AssertionError(('validation',fixture,native[:2],candidate[:2]))
assert paths['validation_only']>0
assert any('reserve>flags>critical>commit>start' in path for path in paths)
assert any('rollback' in path for path in paths)
report={'status':'PASS_MAIN_MSPI_TRANSFER_SELECTOR34_NATIVE_SOURCE','cases':len(fixtures)+len(validation),
        'provider_event_paths':dict(sorted(paths.items())),'stock_sha256':SHA,
        'source_elf_sha256':hashlib.sha256(a.elf.read_bytes()).hexdigest(),
        'limits':['Queue reserve, flags, commit, rollback, start and critical providers intercepted; each independently source-owned.',
                  'Synthetic SRAM/MMIO; concurrent and physical operation unverified.',
                  'Selector 34 only; full transfer dispatcher remains unresolved.']}
a.receipt.parent.mkdir(parents=True,exist_ok=True)
a.receipt.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(report['status'],report['cases'])
