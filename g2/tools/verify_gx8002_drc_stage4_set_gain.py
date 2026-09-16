# SPDX-License-Identifier: MIT
"""Decoded fourth DRC gain setter comparison with explicit power-helper ABI."""
import json,math,struct,subprocess
from build_gx8002_drc_stage4_set_gain import build,ROOT,IMAGE
from build_transparent_image import Elf32
from execute_gx8002_imcra_process import execute
from verify_gx8002_memcpy_source import decode

def verify(startup=False):
    evidence=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==IMAGE.read_bytes()
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x4766c','--stop-address=0x476bc',str(path)],text=True))
    new=decode((ROOT/'build/gx8002-drc-stage4-set-gain/spectrums.disassembly.txt').read_text())
    if startup:
        from analyze_gx8002_upstream_objects import sha
        target=ROOT/'build/gx8002-backup-startup-cluster/cluster.elf'
        integrated=Elf32(target.read_bytes(),'startup')
        symbols={s['name']:s for s in integrated.symbols()}
        for name in ('open_cfw_gx8002_drc_stage4_set_gain',*evidence['helper_bindings']):
            assert symbols[name]['section'] not in (0,0xfff1)
        evidence['startup_elf_sha256']=sha(target.read_bytes())
        new=decode((target.parent/'cluster.disassembly.txt').read_text())
    def bits(v):return struct.unpack('<I',struct.pack('<f',v))[0]
    def val(v):return struct.unpack('<f',struct.pack('<I',v))[0]
    cases=0
    for gain_db in (1.,1.401298464324817e-45,0.,-1.401298464324817e-45,-.25,-10.,-79.99999,-80.,-80.00001,-100.):
        base=0x21000000;mem={base+i:0xa5 for i in range(80)}
        def helper(name):
            def run(r,f,m,trace,read,write):
                trace.append((name,f['fr0'],f['fr1']))
                f['fr0']=bits(math.pow(val(f['fr0']),val(f['fr1'])))
                for i in (0,1,2,3,12,13,*range(18,32)):r[f'r{i}']=0xdead0000+i
                for i in range(1,8):f[f'fr{i}']=0xdead1000+i
            return run
        results=[]
        for source,code,entry in ((False,old,0x4766c),(True,new,0x1000ed2c)):
            helpers={(a-0x38940+0x10000000 if source else a):helper(n) for a,n in ((0x489e4,'pow'),)}
            results.append(execute(code,entry,mem,[base],helpers,float_arguments=[bits(gain_db)]))
        assert results[0]==results[1],gain_db
        cases+=1
    report={'startup':startup,'build':evidence,'cases':cases,'source_admitted':False,'limits':['Decoded gain setter return/final memory/ordered writes/power arguments and saved ABI compared on finite inputs.','Power helper uses host arithmetic; source power body and exceptional inputs are not qualified here.']}
    (ROOT/('docs/research/gx8002-drc-stage4-set-gain-verification'+('-startup' if startup else '')+'.json')).write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
