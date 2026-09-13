# SPDX-License-Identifier: MIT
"""Decode backup startup MPU region-0 setup; do not assume other regions reset."""
import json,random,re,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32,SDK_COMMIT,authenticated_blob
from verify_gx8002_memcpy_source import decode

def verify():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-D','--start-address=0x3b940','--stop-address=0x4f9cc',str(wrapper)],text=True))
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='arch/soc/grus/include/core_ck804.h'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
    header=authenticated_blob(sdk/rel,blob).decode()
    assert 'attr.nx << idx' in header and 'REGION_SIZE_4GB' in header
    writes=[{'pc':pc,'arguments':args} for pc,(op,args,_) in code.items() if op=='mtcr' and re.search(r'cr<(18|19|20|21), 0>',args)]
    assert [r['pc'] for r in writes]==[0x3baa4,0x3baba,0x3bac4,0x3bad0]
    rng=random.Random(804);cases=0
    for initial in [(0,)*4,(0xffffffff,)*4]+[tuple(rng.getrandbits(32) for _ in range(4)) for _ in range(1000)]:
        control=dict(zip((18,19,20,21),initial));r={f'r{i}':0 for i in range(32)}
        for pc,(op,args,width) in code.items():
            if not 0x3ba8e<=pc<=0x3bad0:continue
            if op in ('mfcr','mtcr'):
                m=re.fullmatch(r'(r\d+), cr<(\d+), 0>',args);assert m,(hex(pc),op,args)
                reg,cr=m.group(1),int(m.group(2))
                if op=='mfcr':r[reg]=control[cr]
                else:control[cr]=r[reg]
            else:
                p=[x.strip() for x in args.split(',')]
                if op in ('movi','lrw'):r[p[0]]=int(p[1],0)
                elif op=='ins':
                    high,low=int(p[2]),int(p[3]);mask=((1<<(high-low+1))-1)<<low
                    r[p[0]]=(r[p[0]]&~mask)|((r[p[1]]<<low)&mask)
                elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
                elif op=='ori':r[p[0]]=r[p[1]]|int(p[2],0)
                elif op=='and':r[p[0]]&=r[p[1]]
                else:raise ValueError((hex(pc),op,args))
        assert control[21]&7==0
        assert control[20]>>12==0 and (control[20]>>1)&31==31 and control[20]&1
        assert control[19]&1==0 and (control[19]>>8)&3==3 and control[19]&(1<<24)==0
        assert control[18]&3==3
        cases+=1
    result={'stock_sha256':IMAGE_SHA,'sdk_commit':SDK_COMMIT,'upstream_header_blob':blob,'upstream_header_sha256':sha(header.encode()),
            'initial_register_cases':cases,'backup_text_mpu_writes':writes,'region0':{'base':0,'size_bytes':1<<32,'enabled':True,'nx':0,'access_permission':3},
            'source_admitted':False,'hardware_qualified':False,'limits':['Proves decoded backup startup region-0 setup for tested initial control values. Covers the former table address through a 4GB region permitting execution.','Other region state is not cleared by this slice. Higher-priority regions, writes outside scanned backup text, hardware/cache behavior and startup reachability are not excluded.']}
    (ROOT/'docs/research/gx8002-backup-fft-mpu.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify()['initial_register_cases'],'MPU initialization cases')
