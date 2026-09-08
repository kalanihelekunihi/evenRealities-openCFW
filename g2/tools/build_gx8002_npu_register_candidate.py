#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build native register routines plus a portable C comparison-only image."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
FUNCTIONS=[('get_bit',0xeb4c,12),('set_bit',0xeb58,16),('clear_bit',0xeb68,16),('get_value',0xeb78,4),('set_value',0xeb7c,4)]
DELTA=0x101f6a74

def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';rel='drivers_lib/snpu/grus/snpu_hw.o';blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();oracle=authenticated_blob(sdk/rel,blob);stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('NPU register stock')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_npu_registers.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]];rows=[];portable=[]
    for mode in ('native','portable'):
        extra=['-DOPEN_CFW_GX8002_NATIVE_SHIFTS'] if mode=='native' else []
        obj=out/f'npu-register-{mode}.o';subprocess.run([pre+'gcc',*flags,*extra,'-c',str(source),'-o',str(obj)],check=True)
        script=out/f'npu-register-{mode}.ld';script.write_text('SECTIONS {\n'+''.join(f'.text.{n} {(o+DELTA if mode=="native" else 0x10300000+i*0x100):#x} : {{ *(.text.open_cfw_gx8002_reg_{n}) }}\n' for i,(n,o,size) in enumerate(FUNCTIONS))+'}\n')
        p=out/f'npu-register-{mode}.elf';subprocess.run([pre+'ld','-T',str(script),str(obj),'-o',str(p)],check=True);e=Elf32(p.read_bytes(),str(p))
        if any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('NPU register unresolved')
        for n,o,size in FUNCTIONS:
            sec=next(s for s in e.sections if s['name']=='.text.'+n);payload=e.contents(sec)
            if e.relocations(sec['index']):raise ValueError('NPU register relocation')
            row={'symbol':'open_cfw_gx8002_reg_'+n,'section_name':sec['name'],'runtime_address':sec['address'],'compiled_bytes':len(payload),'compiled_sha256':sha(payload)}
            if mode=='native':
                row.update({'package_offset':o,'stock_envelope_bytes':size,'stock_sha256':sha(stock[o:o+size]),'fits':len(payload)<=size,'ownership_kind':'compiled_assembly' if n.endswith('bit') else 'compiled_c'});rows.append(row)
            else:portable.append(row)
        (out/f'npu-register-{mode}.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    manual=ROOT/'build/csky-isa-manual.pdf'
    report={'sdk_commit':SDK_COMMIT,'oracle':{'path':rel,'blob':blob,'sha256':sha(oracle)},'source_sha256':sha(source.read_bytes()),'flags':flags,'native_define':'OPEN_CFW_GX8002_NATIVE_SHIFTS','isa_manual_sha256':sha(manual.read_bytes()),'regions':rows,'portable_comparison_only':portable,'source_admitted':False,'limits':['Candidate only. Three native instruction-wrapper functions accounted as compiled_assembly; ordinary read/write compiled_c. Portable C is an independent compilation oracle and never emitted into firmware. Need full count/MMIO/ABI qualification.']}
    (ROOT/'docs/research/gx8002-npu-register-linked-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
