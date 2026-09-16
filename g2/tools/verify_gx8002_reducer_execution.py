# SPDX-License-Identifier: MIT
"""Execute full reducer via a C stack-local output wrapper."""
import json,re,subprocess,math
from build_gx8002_backup_cfft import ROOT,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute
from verify_gx8002_double_addsub_target import bits,floating
from verify_gx8002_analog_source import FLAGS


def verify():
    base=ROOT/'build/gx8002-reduction-source-closure';prior=json.loads((ROOT/'docs/research/gx8002-reduction-source-closure.json').read_text())
    assert sha((base/'reduction.elf').read_bytes())==prior['elf_sha256']
    out=ROOT/'build/gx8002-reducer-execution';out.mkdir(exist_ok=True)
    source=out/'wrapper.c';source.write_text('extern int __ieee754_rem_pio2(double,double *);\ndouble reduction_probe(double x,int selector) { double y[2]; int n=__ieee754_rem_pio2(x,y); return selector==0?y[0]:selector==1?y[1]:(double)n; }\n')
    obj=out/'wrapper.o';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc',*FLAGS,'-Os','-c',str(source),'-o',str(obj)],check=True)
    script=(base/'reduction.ld').read_text();inputs=list(dict.fromkeys(re.findall(r'(/[^\s()]+\.o)\(',script)))
    script+='SECTIONS { .probe 0x1001a000 : { '+str(obj)+'(.text*) } }\n'
    ld=out/'probe.ld';ld.write_text(script);path=out/'probe.elf'
    subprocess.run([pre+'ld','-T',str(ld),*inputs,str(obj),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'probe');old=Elf32((base/'reduction.elf').read_bytes(),'base')
    for s in old.sections:
        if s['flags']&2 and s['size']:
            new=next(t for t in elf.sections if t['name']==s['name']);assert new['address']==s['address'] and elf.contents(new)==old.contents(s)
    code=decode(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    memory={s['address']+i:b for s in elf.sections if s['flags']&2 and s['size'] and s['type']!=8 for i,b in enumerate(elf.contents(s))}
    values=[0.0,-0.0,0.5,-0.5,1.0,-1.0,2.0,-2.0,100.0,-100.0,1e10,-1e10,1e100,-1e100,1e300,-1e300]
    rows=[]
    for x in values:
        b=bits(x);results=[]
        for selector in (0,1,2):
            result=execute(code,0x1001a000,bytes(20),arguments=[b&0xffffffff,b>>32,selector],readonly=memory,return_pair=True,max_steps=100000,stack_bytes=2048)
            results.append(result)
        high,low,n=map(floating,results)
        assert math.isfinite(high) and math.isfinite(low) and abs(high+low)<=math.pi/4+1e-15
        assert n==int(n)
        rows.append({'input':hex(b),'high':hex(results[0]),'low':hex(results[1]),'quadrant_integer':int(n)})
    report={'source_elf_sha256':prior['elf_sha256'],'wrapper_source_sha256':sha(source.read_bytes()),'execution_elf_sha256':sha(path.read_bytes()),'cases':rows,'source_admitted':False,'limits':['Complete decoded reducer execution and ABI checks, including large-argument kernel. Only output range and integer quotient checked here; high-precision remainder/quadrant oracle, placement and hardware pending.']}
    (ROOT/'docs/research/gx8002-reducer-execution.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(len(verify()['cases']))
