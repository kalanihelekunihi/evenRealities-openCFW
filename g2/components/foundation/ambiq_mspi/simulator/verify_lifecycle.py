#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare MSPI lifecycle state changes with explicit external CQ/delay stubs."""
import argparse
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

if not __debug__:
    raise RuntimeError('optimized Python is rejected for simulator evidence')
ROOT = Path(__file__).resolve().parents[5]
PARSER = ROOT/'g2/components/foundation/touch_scb/simulator/verify.py'
spec = importlib.util.spec_from_file_location('lifecycle_elf', PARSER)
loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loader)
HANDLE, MSPI, STOP, BASE = 0x20001000, 0x40060000, 0x08000000, 0x438000
FUNCTIONS = {
    'disable': (0x4c0ea8, 118, 'ed26e7d54404bbf50b8edbe0b10fd5f264caef39b8aed9fe466f3d41233f794d'),
    'deinitialize': (0x4c0f24, 56, '17e2e38a57e5a1669a591cf61ad92ff4b5ca8a1747673512410737ac452d689b'),
}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def state_bytes(case):
    state = bytearray(b'\xa5' * 0x8d0)
    for offset, key in [(0,'prefix'),(4,'module'),(0x18,'tcb'),(0x20,'cq'),
                        (0x840,'hp'),(0x8cc,'delay')]:
        struct.pack_into('<I', state, offset, case[key])
    return bytes(state)

def execute(segments, entry, case, symbols=None):
    import unicorn
    import capstone
    from unicorn.arm_const import (UC_ARM_REG_R0,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC)
    cpu = unicorn.Uc(unicorn.UC_ARCH_ARM, unicorn.UC_MODE_THUMB | unicorn.UC_MODE_MCLASS)
    pages = set()
    for s in segments:
        for address in range(s['address'] & ~4095, (s['address']+s['memory_size']+4095) & ~4095, 4096):
            if address not in pages:
                cpu.mem_map(address,4096); pages.add(address)
        cpu.mem_write(s['address'],s['data'])
    for address in range(0x20000000,0x20010000,4096):
        if address not in pages: cpu.mem_map(address,4096)
    cpu.mem_map(MSPI,3*4096); cpu.mem_map(STOP,4096)
    for module in range(3):
        cpu.mem_write(MSPI+module*4096+0x90,struct.pack('<I',case['xip']))
    initial=state_bytes(case); cpu.mem_write(HANDLE-8,b'\xcc'*8+initial+b'\xcc'*8)
    calls, timeline, writes, trace = [],[],[],[]
    source = symbols is not None
    if source:
        fixture=symbols['ambiq_lifecycle_fixture']
        cpu.mem_write(fixture,struct.pack('<11I',case['cq_status'],*([0]*10)))
        seams={symbols['mspi_cq_disable']&~1:1,symbols['mspi_cq_term']&~1:2,symbols['am_hal_delay_us']&~1:3}
    else:
        seams={0x4bfd62:1,0x4bfc86:2,0x4807a0:3}
        for address in seams:
            page=address&~4095
            if page not in pages:cpu.mem_map(page,4096);pages.add(page)
            cpu.mem_write(address,b'\x70\x47')
    disassembler=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB|capstone.CS_MODE_MCLASS)

    def instruction(uc,address,size,_):
        if address in seams:
            kind=seams[address];argument=uc.reg_read(UC_ARM_REG_R0)
            prefix=struct.unpack('<I',uc.mem_read(HANDLE,4))[0] if kind!=3 else 0
            event=[kind,argument,prefix];calls.append(event);timeline.append({'call':event})
            if not source:
                uc.reg_write(UC_ARM_REG_R0,case['cq_status'] if kind==1 else 0)
                uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
                return
        matches=[s for s in segments if s['flags']&1 and s['address']<=address<address+size<=s['address']+len(s['data'])]
        assert len(matches)==1,hex(address)
        s=matches[0];raw=bytes(uc.mem_read(address,size));off=address-s['address']
        assert raw==s['data'][off:off+size]
        ins=list(disassembler.disasm(raw,address));assert len(ins)==1 and ins[0].size==size
        trace.append({'pc':address,'bytes':raw.hex()})

    def memory(uc,access,address,size,value,_):
        if MSPI<=address<MSPI+3*4096:
            assert access==unicorn.UC_MEM_READ and size==4
            assert address==MSPI+case['module']*4096+0x90
            timeline.append({'xip_read':case['xip']})
        if access==unicorn.UC_MEM_WRITE and HANDLE-8<=address<HANDLE+0x8d0+8:
            assert HANDLE<=address and address+size<=HANDLE+8,'unexpected sparse-state write'
            old=bytearray(uc.mem_read(HANDLE,8));offset=address-HANDLE
            old[offset:offset+size]=value.to_bytes(size,'little')
            # Prefix bitfield stores can differ in width. Preserve raw evidence,
            # compare resulting serialized state/order, never claim atomic equivalence.
            slot=0 if offset<4 else 4
            resulting=struct.unpack_from('<I',old,slot)[0]
            writes.append({'offset':offset,'size':size,'value':value})
            timeline.append({'state_word_offset':slot,'result':resulting})

    cpu.hook_add(unicorn.UC_HOOK_CODE,instruction)
    cpu.hook_add(unicorn.UC_HOOK_MEM_READ|unicorn.UC_HOOK_MEM_WRITE,memory)
    cpu.reg_write(UC_ARM_REG_SP,0x2000f000);cpu.reg_write(UC_ARM_REG_LR,STOP|1)
    cpu.reg_write(UC_ARM_REG_R0,0 if case['null'] else HANDLE)
    cpu.emu_start(entry|1,STOP,count=10000)
    assert cpu.reg_read(UC_ARM_REG_PC)==STOP
    final=bytes(cpu.mem_read(HANDLE,0x8d0))
    assert bytes(cpu.mem_read(HANDLE-8,8))==bytes(cpu.mem_read(HANDLE+0x8d0,8))==b'\xcc'*8
    if source:
        values=list(struct.unpack('<11I',cpu.mem_read(fixture,44)))
        assert values[1]==len(calls)<=3
        assert [values[2+i*3:5+i*3] for i in range(values[1])]==calls
    return {'return':cpu.reg_read(UC_ARM_REG_R0),'calls':calls,'timeline':timeline,
            'raw_state_writes':writes,'final_state_sha256':sha(final),'final_state':final.hex(),'trace':trace}

def expected(case,operation):
    state=bytearray(state_bytes(case));prefix=case['prefix'];calls=[];timeline=[]
    valid=not case['null'] and prefix&0x1ffffff==0x1bebebe
    if not valid:return 2,bytes(state),calls,timeline
    status=0
    if prefix&0x2000000:
        if case['hp'] or case['cq']:status=3
        else:
            if case['tcb']:
                calls.append([1,HANDLE,prefix]);timeline.append({'call':calls[-1]})
                status=case['cq_status']
                if status==0:
                    calls.append([2,HANDLE,prefix]);timeline.append({'call':calls[-1]})
            if status==0:
                prefix&=~0x2000000;struct.pack_into('<I',state,0,prefix)
                timeline.append({'state_word_offset':0,'result':prefix})
                timeline.append({'xip_read':case['xip']})
                if case['xip']&1:
                    calls.append([3,case['delay'],0]);timeline.append({'call':calls[-1]})
    if operation=='deinitialize':
        prefix&=~0x1000000;struct.pack_into('<I',state,0,prefix);struct.pack_into('<I',state,4,0)
        timeline.extend([{'state_word_offset':0,'result':prefix},{'state_word_offset':4,'result':0}])
        status=0
    return status,bytes(state),calls,timeline

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--elf',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
    assert sha(blob)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
    image=blob[32:];stock=[]
    for address,size,digest in FUNCTIONS.values():
        b=image[address-BASE:address-BASE+size];assert sha(b)==digest
        stock.append(dict(address=address,data=b,memory_size=size,flags=5))
    for address,value in [(0x4c0f68,0x1bebebe),(0x4c0f5c,MSPI)]:
        b=image[address-BASE:address-BASE+4];assert struct.unpack('<I',b)[0]==value
        stock.append(dict(address=address,data=b,memory_size=4,flags=4))
    elf,segments,symbols=loader.elf_info(args.elf)
    default=dict(prefix=0x3bebebe,module=1,tcb=0,cq=0,hp=0,xip=0,delay=17,cq_status=0,null=False)
    variations=[('disabled',{'prefix':0x1bebebe}),('disabled_busy',{'prefix':0x1bebebe,'cq':3,'hp':4}),('no_tcb',{}),('xip_delay',{'xip':1}),
                ('xip_reserved',{'xip':0x80000000}),('cq_busy',{'cq':1}),('hp_busy',{'hp':1}),
                ('both_busy',{'cq':0xffffffff,'hp':0xffffffff}),('cq_success',{'tcb':0x20008000}),
                ('cq_failure',{'tcb':0x20008000,'cq_status':13}),
                ('cq_failure_xip',{'tcb':0x20008000,'cq_status':13,'xip':1}),
                ('xip_max_delay',{'xip':1,'delay':0xffffffff}),
                ('cq_xip',{'tcb':0x20008000,'xip':0x80000001,'delay':0}),
                ('null',{'null':True}),('bad_magic',{'prefix':0x3bebebf}),
                ('not_initialized',{'prefix':0x2bebebe}),('reserved_flags',{'prefix':0xffbebebe})]
    cases=[];pc={}
    for operation,(entry,_,_) in FUNCTIONS.items():
        symbol='ambiq_sim_controller_disable' if operation=='disable' else 'ambiq_sim_deinitialize'
        for module in range(3):
            for name,changes in variations:
                case=dict(default,module=module);case.update(changes)
                a=execute(stock,entry,case);b=execute(segments,symbols[symbol],case,symbols)
                status,state,calls,timeline=expected(case,operation)
                assert a['return']==b['return']==status
                assert bytes.fromhex(a['final_state'])==bytes.fromhex(b['final_state'])==state
                assert a['calls']==b['calls']==calls
                assert a['raw_state_writes']==b['raw_state_writes']
                assert all(w['size']==4 and w['offset'] in [0,4] for w in a['raw_state_writes'])
                assert a['timeline']==b['timeline']==timeline,(operation,name,a['timeline'],b['timeline'],timeline)
                for t in a['trace']:pc[t['pc']]=t['bytes']
                cases.append(dict(operation=operation,name=name,inputs=case,original=a,source_linked=b))
    component=Path(__file__).resolve().parents[1]
    report={'status':'PASS','case_count':len(cases),'cases':cases,'functions':FUNCTIONS,
            'original_unique_instruction_bytes':sum(len(bytes.fromhex(v)) for v in pc.values()),
            'firmware_sha256':sha(blob),'script_sha256':sha(Path(__file__).read_bytes()),'parser_sha256':sha(PARSER.read_bytes()),'elf_sha256':sha(elf),
            'source_manifest':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in sorted(component.rglob('*')) if p.suffix in ['.c','.h','.ld']},
            'limits':'Original disable/deinitialize bodies execute; external CQ disable/term and delay are stubbed on BOTH sides. Tests prove call order, argument/return propagation and serialized state transformations, not queue drain, free, hardware delay or shutdown safety. Raw prefix/module store widths, offsets, values and order match this compiled target and are recorded. No concurrent RMW/atomic-equivalence claim.'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as stream:stream.write(json.dumps(report,indent=2)+'\n')
    print('PASS',len(cases),'lifecycle cases;',report['original_unique_instruction_bytes'],'original bytes; external CQ/delay stubs')

if __name__=='__main__':main()
