# SPDX-License-Identifier: MIT
"""Decoded fourth DRC constructor comparison with explicit numeric helper ABI."""
import json,math,struct,subprocess
from build_gx8002_drc_stage4_initialize import build,ROOT,IMAGE
from build_transparent_image import Elf32
from execute_gx8002_imcra_process import execute
from verify_gx8002_memcpy_source import decode

def verify(startup=False):
    evidence=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==IMAGE.read_bytes()
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x476bc','--stop-address=0x477a4',str(path)],text=True))
    new=decode((ROOT/'build/gx8002-drc-stage4-initialize/spectrums.disassembly.txt').read_text())
    if startup:
        from analyze_gx8002_upstream_objects import sha
        target=ROOT/'build/gx8002-backup-startup-cluster/cluster.elf'
        integrated=Elf32(target.read_bytes(),'startup')
        symbols={s['name']:s for s in integrated.symbols()}
        for name in ('open_cfw_gx8002_drc_stage4_initialize',*evidence['helper_bindings']):
            assert symbols[name]['section'] not in (0,0xfff1)
        evidence['startup_elf_sha256']=sha(target.read_bytes())
        new=decode((target.parent/'cluster.disassembly.txt').read_text())
    def bits(v):return struct.unpack('<I',struct.pack('<f',v))[0]
    def val(v):return struct.unpack('<f',struct.pack('<I',v))[0]
    cases=0
    for rate in (8000.,16000.,48000.5):
     for threshold in (-50.,-15.,0.):
      for attack,release,duration in ((.005,.02,.01),(.1,.2,0.),(1.,2.,.5)):
       base=0x21000000;mem={base+i:0xa5 for i in range(80)}
       for i in range(4):mem[0x8000+i]=(bits(rate)>>(8*i))&255
       def helper(name):
        def run(r,f,m,trace,read,write):
         result=0;second=0;floating=0
         if name=='clear':
            trace.append((name,r['r0'],r['r1'],r['r2']))
            for i in range(r['r2']):write(r['r0']+i,r['r1'],1)
            result=r['r0']
         elif name in ('pow','log','widen'):
            trace.append((name,f['fr0'],f['fr1']) if name=='pow' else (name,f['fr0']))
            value=val(f['fr0'])
            if name=='pow':floating=bits(math.pow(value,val(f['fr1'])))
            elif name=='log':floating=bits(math.log(value))
            else:result,second=struct.unpack('<II',struct.pack('<d',value))
         else:
            trace.append((name,r['r0'],r['r1']))
            value=struct.unpack('<d',struct.pack('<II',r['r0'],r['r1']))[0]
            if name=='exp':result,second=struct.unpack('<II',struct.pack('<d',math.exp(value)))
            else:floating=bits(value)
         for i in (0,1,2,3,12,13,*range(18,32)):r[f'r{i}']=0xdead0000+i
         for i in range(8):f[f'fr{i}']=0xdead1000+i
         r['r0']=result;r['r1']=second;f['fr0']=floating
        return run
       results=[]
       for source,code,entry in ((False,old,0x476bc),(True,new,0x1000ed7c)):
        helpers={(a-0x38940+0x10000000 if source else a):helper(n) for a,n in ((0x49d04,'clear'),(0x489e4,'pow'),(0x489ec,'log'),(0x4a434,'widen'),(0x4818c,'exp'),(0x4acd8,'narrow'))}
        results.append(execute(code,entry,mem,[base],helpers,float_arguments=list(map(bits,(threshold,attack,release,duration)))))
       assert results[0]==results[1],(rate,threshold,attack,release,duration)
       cases+=1
    report={'startup':startup,'build':evidence,'cases':cases,'source_admitted':False,'limits':['Decoded constructor return/final memory/ordered writes/helper arguments and saved ABI compared on finite inputs.','Numeric helpers use host arithmetic and explicit float/double register transfers; source math bodies and exceptional inputs not qualified here.']}
    (ROOT/('docs/research/gx8002-drc-stage4-initialize-verification'+('-startup' if startup else '')+'.json')).write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
