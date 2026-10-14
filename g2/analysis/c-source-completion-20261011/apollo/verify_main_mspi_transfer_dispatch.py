#!/usr/bin/env python3
"""Check complete Main transfer selector routing and native shared gates."""
import argparse, hashlib, itertools, json
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
HELPERS={key:syms['g2_main_mspi_transfer_'+key+'_candidate'] for key in
         ('basic','structured','aux','control','mode24','mode26','queue_state','queue_mode','submit','descriptor')}
BY_ADDRESS={address:name for name,address in HELPERS.items()}
HANDLE,CFG,RET=0x20006000,0x20008000,0x200ff000

def family(op):
    if op<=13:return 'basic'
    if op<=19:return 'structured'
    if op in (20,25,27):return 'aux'
    if op in (21,22,23,35,36,37,38,39):return 'control'
    if op==24:return 'mode24'
    if op==26:return 'mode26'
    if op in (28,31,32,33):return 'queue_state'
    if op==29:return 'queue_mode'
    if op==30:return 'submit'
    if op==34:return 'descriptor'
    return None

def run(source,selector,valid=True,enabled=True,null_handle=False):
    cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    cpu.mem_map(0x430000,0x380000);cpu.mem_write(0x437fe0,blob)
    cpu.mem_map(0x800000,0x10000)
    for address,body in segments:cpu.mem_write(address,body)
    cpu.mem_map(0x20000000,0x100000)
    cpu.mem_write(HANDLE,bytes([0xa5])*0x900)
    cpu.mem_write(HANDLE,(0x01bebebe if valid else 0).to_bytes(4,'little'))
    cpu.mem_write(HANDLE+4,(0).to_bytes(4,'little'))
    cpu.mem_write(HANDLE+8,bytes([int(enabled)]))
    cpu.mem_write(CFG,bytes(32))
    cpu.reg_write(R.UC_ARM_REG_R0,0 if null_handle else HANDLE)
    cpu.reg_write(R.UC_ARM_REG_R1,selector)
    cpu.reg_write(R.UC_ARM_REG_R2,CFG)
    cpu.reg_write(R.UC_ARM_REG_SP,0x200fe000)
    cpu.reg_write(R.UC_ARM_REG_LR,RET|1)
    events=[]
    def hook(machine,pc,_size,_user):
        if pc==RET:machine.emu_stop();return
        if source and pc in BY_ADDRESS:
            name=BY_ADDRESS[pc]
            events.append((name,machine.reg_read(R.UC_ARM_REG_R0),
                           machine.reg_read(R.UC_ARM_REG_R1),machine.reg_read(R.UC_ARM_REG_R2)))
            machine.reg_write(R.UC_ARM_REG_R0,0x100+(selector&0xff))
            machine.reg_write(R.UC_ARM_REG_PC,machine.reg_read(R.UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE,hook)
    entry=syms['g2_norflash_config_transfer_4c0f78'] if source else 0x4c0f78
    cpu.emu_start(entry|1,RET+2,count=10000)
    assert cpu.reg_read(R.UC_ARM_REG_PC)==RET
    return cpu.reg_read(R.UC_ARM_REG_R0),events

route_cases=0
for selector in list(range(256))+[0x100+i for i in range(41)]:
    op=selector&0xff
    expected=family(op)
    source_result,events=run(True,selector)
    if expected is None:
        assert source_result==6 and not events,(selector,source_result,events)
        native_result,_=run(False,selector)
        assert native_result==6,(selector,native_result)
    else:
        assert source_result==0x100+op and len(events)==1 and events[0][0]==expected,(selector,source_result,events)
        event=events[0]
        assert event[1]==HANDLE
        if expected in ('mode24','mode26'):
            assert event[2]==CFG
        else:
            assert event[2]==selector and event[3]==CFG
    route_cases+=1

gate_cases=0
for selector,valid,enabled,null_handle in itertools.product((0,16,26,30,34,39,40,41,255),
                                                              (False,True),(False,True),(False,True)):
    if valid and enabled and not null_handle and family(selector) is not None:
        continue
    native=run(False,selector,valid,enabled,null_handle)[0]
    candidate=run(True,selector,valid,enabled,null_handle)[0]
    assert native==candidate,(selector,valid,enabled,null_handle,native,candidate)
    gate_cases+=1
report={'status':'PASS_MAIN_MSPI_TRANSFER_DISPATCH_ROUTING_AND_NATIVE_GATES',
        'selector_route_cases':route_cases,'native_gate_cases':gate_cases,
        'stock_sha256':SHA,'source_elf_sha256':hashlib.sha256(a.elf.read_bytes()).hexdigest(),
        'limits':['For selectors 0..39, downstream branch bodies are intercepted here; their independent native/source oracles remain required.',
                  'Selectors 40..255 and shared validation gates compared directly with native dispatcher.',
                  'Synthetic handle; physical hardware and complete Main image unverified.']}
a.receipt.parent.mkdir(parents=True,exist_ok=True)
a.receipt.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(report['status'],route_cases,gate_cases)
