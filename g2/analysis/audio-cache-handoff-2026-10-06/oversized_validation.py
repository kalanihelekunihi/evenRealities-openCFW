#!/usr/bin/env python3
"""Retain valid huge inputs as bounded-prefix tests, not completed-path passes."""
import argparse, hashlib, importlib.util, json, struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('cache',ROOT/'g2/components/foundation/cache_maintenance/verify.py')
cache=importlib.util.module_from_spec(spec);spec.loader.exec_module(cache)


def probe(segments,entry,address,length,clean,flag):
    import unicorn as u
    import unicorn.arm_const as a
    cpu=u.Uc(u.UC_ARCH_ARM,u.UC_MODE_THUMB|u.UC_MODE_MCLASS)
    cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M4);pages=set()
    for s in segments:
        for p in range(s['address']&~4095,(s['address']+s['memory_size']+4095)&~4095,4096):
            if p not in pages:cpu.mem_map(p,4096);pages.add(p)
        cpu.mem_write(s['address'],s['data'])
    for start,n in [(0x20000000,0x10000),(0xe000e000,8192),(cache.STOP,4096)]:cpu.mem_map(start,n)
    cpu.mem_write(cache.H,struct.pack('<II',address,length));cpu.mem_write(cache.CCR,struct.pack('<I',0x10000))
    for r,v in [(a.UC_ARM_REG_R0,cache.H),(a.UC_ARM_REG_R1,flag),(a.UC_ARM_REG_SP,cache.SP),(a.UC_ARM_REG_LR,cache.STOP|1)]:cpu.reg_write(r,v)
    writes=[];barriers=[];instructions=[0]
    op=0xe000ef68 if clean else (0xe000ef70 if flag&255 else 0xe000ef5c)
    def code(uc,pc,size,_):
        instructions[0]+=1
        if pc==cache.STOP:uc.emu_stop();return
        raw=bytes(uc.mem_read(pc,size))
        if raw==bytes.fromhex('bff34f8f'):barriers.append('dsb')
        if raw==bytes.fromhex('bff36f8f'):barriers.append('isb')
    def memory(uc,access,at,size,value,_):
        if at==op:
            assert size==4
            writes.append(value&0xffffffff)
    cpu.hook_add(u.UC_HOOK_CODE,code);cpu.hook_add(u.UC_HOOK_MEM_WRITE,memory)
    cpu.emu_start(entry|1,cache.STOP,count=30000)
    assert cpu.reg_read(a.UC_ARM_REG_PC)!=cache.STOP
    assert writes and barriers==['dsb']
    assert all(value==(address+32*i)&0xffffffff for i,value in enumerate(writes))
    assert bytes(cpu.mem_read(cache.H,8))==struct.pack('<II',address,length)
    return {'classification':'execution_budget','completed':False,'instruction_budget':30000,'instructions':instructions[0],
            'writes_observed':len(writes),'first_values':writes[:8],'last_values':writes[-8:],
            'prefix_sha256':hashlib.sha256(b''.join(struct.pack('<I',v) for v in writes)).hexdigest(),
            'first_barrier':barriers,'pc_at_budget':hex(cpu.reg_read(a.UC_ARM_REG_PC))}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    blob=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';assert cache.sha(blob)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
    raw=blob.read_bytes()[32:];stock=[dict(address=0x475000,memory_size=4096,data=raw[0x475000-cache.BASE:0x476000-cache.BASE],flags=5)]
    _,segments,symbols=cache.elf_reader.elf_info(a.elf);cases=[]
    for clean,flag in [(False,0),(False,1),(True,0)]:
        for align in [0,1,15,31]:
            address,length=0x20008000+align,0x7fffffff
            original=probe(stock,0x47510e if clean else 0x475014,address,length,clean,flag)
            source=probe(segments,symbols['opencfw_cache_clean' if clean else 'opencfw_cache_invalidate']&~1,address,length,clean,flag)
            # Both independently match the same linear command formula; completed execution is not inferred.
            cases.append({'address':hex(address),'length':length,'clean':clean,'flag':flag,
                          'initial_adjusted_counter':hex(length+align),'mathematical_write_count':(length+align+31)//32,
                          'signed_boundary_crossed':length+align>=0x80000000,'unsigned_addition_overflow':False,
                          'original':original,'source':source,'stock_source_prefix_mismatch':False})
    report={'status':'PASS_BOUNDED_PREFIX_ONLY','cases':cases,'classification':'execution budget, not demonstrated stock/source mismatch or unsupported input',
            'legitimate_raw_inputs_retained':True,'completed_huge_paths_verified':False,
            'arithmetic_contract':'For1<=length<=INT32_MAX and offset0..31, total commands ceil((length+offset)/32). Sum never overflows uint32. A signed-boundary crossing is followed by subtraction32 before the continuation comparison; it does not imply early return.',
            'elf_sha256':cache.sha(a.elf),'firmware_sha256':cache.sha(blob),'script_sha256':cache.sha(__file__)}
    with a.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print('PASS bounded prefixes',len(cases),'completed huge paths NOT VERIFIED')


if __name__=='__main__':main()
