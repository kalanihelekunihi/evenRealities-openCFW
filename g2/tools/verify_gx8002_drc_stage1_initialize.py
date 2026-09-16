# SPDX-License-Identifier: MIT
"""Decoded DRC constructor ABI/state comparison with explicit math models."""
import json,math,struct,subprocess
from build_gx8002_drc_stage1_initialize import build,ROOT
from execute_gx8002_imcra_process import execute
from verify_gx8002_memcpy_source import decode

def verify(concrete_math=False,startup=False):
    evidence=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    from build_transparent_image import Elf32
    from analyze_gx8002_upstream_objects import IMAGE
    wrapper=Elf32((ROOT/'build/gx8002-board/padmux-get-stock.elf').read_bytes(),'stock')
    assert wrapper.contents(next(s for s in wrapper.sections if s['name']=='.data'))==IMAGE.read_bytes()
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x473b4','--stop-address=0x47488',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-drc-stage1-initialize/spectrums.disassembly.txt').read_text())
    def bits(x):return struct.unpack('<I',struct.pack('<f',x))[0]
    def value(x):return struct.unpack('<f',struct.pack('<I',x))[0]
    if startup:
        from analyze_gx8002_upstream_objects import sha
        target=ROOT/'build/gx8002-backup-startup-cluster/cluster.elf'
        integrated=Elf32(target.read_bytes(),'startup')
        symbols={s['name']:s for s in integrated.symbols()}
        for name in ('open_cfw_gx8002_drc_stage1_initialize',*evidence['helper_bindings'],'__ieee754_logf','__ieee754_expf'):
            assert symbols[name]['section'] not in (0,0xfff1)
        evidence['startup_elf_sha256']=sha(target.read_bytes())
        new=decode((target.parent/'cluster.disassembly.txt').read_text())
    if concrete_math:
        from build_gx8002_log_exp_placed import build as math_build
        from verify_gx8002_double_pack_target import execute as math_execute
        from gx8002_binary32_rational import operation
        evidence['math']=math_build()
        math_path=target if startup else ROOT/'build/gx8002-log-exp-placed/math.elf'
        math_elf=Elf32(math_path.read_bytes(),'math')
        math_code=new if startup else decode((math_path.parent/'math.disassembly.txt').read_text())
        stock_math=decode(subprocess.check_output([pre,'-D','--start-address=0x490a8','--stop-address=0x4950c',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
        source_memory={sec['address']+i:b for sec in math_elf.sections if sec['flags']&2 for i,b in enumerate(math_elf.contents(sec))}
        stock_memory={0x10003000+i:b for i,b in enumerate(IMAGE.read_bytes()[0x3b940:0x4f9cc])}
    cases=0
    for rate in (8000.,16000.,48000.5):
     for attack,release in ((.005,.1),(.01,.02),(1.,2.)):
      for control in (0,15,0x41700000):
       for mutate in (False,True):
        base=0x21000000;memory={base+i:0xa5 for i in range(64)}
        for address,v in ((0x8000,control),(0x8004,bits(rate))):
            for i in range(4):memory[address+i]=(v>>(8*i))&255
        def helper(name):
         def run(r,f,mem,trace,read,write):
            if name=='clear':
                trace.append((name,r['r0'],r['r1'],r['r2']))
                for i in range(r['r2']):write(r['r0']+i,r['r1'],1)
                result=r['r0'];floating=0
            else:
                arg=f['fr0'];trace.append((name,arg))
                if concrete_math:
                    entry=0x490a8 if name=='log' else 0x49300
                    floating=math_execute(math_code if source else stock_math,entry-0x38940+0x10000000 if source else entry,bytes(20),float_arguments=[arg]+[0]*15,return_float=True,float_operation=operation,readonly=source_memory if source else stock_memory)
                else:floating=bits(math.log(value(arg)) if name=='log' else math.exp(value(arg)))
                result=0xdeadbeef
                if mutate and name=='exp':write(base+44,1,1)
            for i in (0,1,2,3,12,13,*range(18,32)):r[f'r{i}']=0xdead0000+i
            for i in range(8):f[f'fr{i}']=0xdead1000+i
            r['r0']=result;f['fr0']=floating
         return run
        results=[]
        for source,code,entry in ((False,old,0x473b4),(True,new,0x1000ea74)):
            helpers={(a-0x38940+0x10000000 if source else a):helper(n) for a,n in ((0x49d04,'clear'),(0x489ec,'log'),(0x489f4,'exp'))}
            results.append(execute(code,entry,memory,[base],helpers,float_arguments=[bits(-15.),bits(5.),bits(attack),bits(release)]))
        assert results[0]==results[1],(rate,attack,release,control,mutate)
        cases+=1
    report={'startup':startup,'concrete_math':concrete_math,'build':evidence,'cases':cases,'source_admitted':False,'limits':['Decoded stock/C constructor compare return, final memory, ordered writes/math arguments and saved ABI, with caller clobbers and helper flag mutation.','Log/exp and memset modeled; finite sampled inputs only. Null clear, exceptional floats and real math implementation remain unqualified.']}
    if concrete_math:report['limits']=['Decoded constructor comparison with distinct compiled Newlib and decoded stock log/exp bodies at helper boundaries.', 'Math wrapper dispatch and memset modeled; math uses a separate register/stack executor. Finite sampled inputs, no hardware or full DRC qualification.']
    (ROOT/('docs/research/gx8002-drc-stage1-initialize-verification'+('-math' if concrete_math else '')+('-startup' if startup else '')+'.json')).write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
