# SPDX-License-Identifier: MIT
"""Bounded primary-image reference census for three retained return-zero leaves."""
import json,subprocess,struct
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha,SDK_COMMIT,authenticated_blob
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode

def analyze():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA;path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock');assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    targets={p+0x1000dfec:p for p in (0x181c0,0x181c4,0x181c8)}
    assert all(stock[p:p+4]==bytes.fromhex('00303c78') for p in targets.values())
    references=[];pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    for lo,hi,delta,name in ((0xc590,0x15414,0x101f6a74,'xip'),(0x15414,0x184f8,0x1000dfec,'sram')):
        code=decode(subprocess.check_output([pre,'-D','--start-address='+hex(lo),'--stop-address='+hex(hi),str(path)],text=True))
        for pc,(op,args,width) in code.items():
            if op not in ('bsr','br'):continue
            try:target=(int(args,0)+delta)&0xffffffff
            except ValueError:continue
            if target in targets:references.append({'package_offset':pc,'region':name,'instruction':op,'target_runtime':target,'target_package':targets[target]})
    literals=[]
    for target,p in targets.items():
        needle=struct.pack('<I',target);start=0
        while True:
            at=stock.find(needle,start)
            if at<0:break
            literals.append({'package_offset':at,'target_runtime':target,'target_package':p});start=at+1
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='lvp/common/snpu_engine/lvp_kws.c';blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();source=authenticated_blob(sdk/rel,blob)
    return {'stock_sha256':IMAGE_SHA,'sdk_commit':SDK_COMMIT,'upstream_blob':blob,'upstream_sha256':sha(source),'leaves':[{'package_offset':p,'runtime_address':t} for t,p in targets.items()],'decoded_branch_candidates':references,'literal_candidates':literals,'source_admitted':False,'limits':['Linear disassembly can interpret embedded data as instructions; candidates require caller-boundary validation. Literal matches are byte occurrences, not pointer-use proof.','Primary text branch sweep and whole-package exact runtime-address occurrences only; indirect/computed references and original function identities remain unresolved. SDK conditional zero-return functions are hypotheses, not assigned names.']}
if __name__=='__main__':
    r=analyze();(ROOT/'docs/research/gx8002-kws-zero-leaf-references.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'branches':r['decoded_branch_candidates'],'literals':r['literal_candidates']},indent=2))
