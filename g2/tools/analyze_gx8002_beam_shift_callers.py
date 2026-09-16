# SPDX-License-Identifier: MIT
"""Bounded decoded shift-argument proof for beam output normalization."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode

def analyze():
    assert sha(IMAGE.read_bytes())==IMAGE_SHA
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==IMAGE.read_bytes()
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    asm=subprocess.check_output([pre,'-D','--start-address=0x45dac','--stop-address=0x46790',str(path)],text=True)
    code=decode(asm)
    def require(pc,op,args):assert code[pc][:2]==(op,args),(hex(pc),code[pc])
    require(0x464fc,'movi','r16, 9')
    require(0x4658e,'mov','r2, r5');require(0x46590,'mov','r0, r5')
    require(0x465c2,'addu','r1, r4');require(0x465c4,'subu','r1, r16, r1')
    require(0x465cc,'sextb','r1, r1');require(0x465ce,'mov','r0, r2')
    def peak_shift(peak):
        r={'r3':peak};pc=0x46510;condition=False
        for _ in range(100):
            if pc==0x4658c:return r['r4']
            op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
            if op=='zext':r[p[0]]=(r[p[1]]>>int(p[3]))&((1<<(int(p[2])-int(p[3])+1))-1)
            elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
            elif op=='bf':
                if not condition:nxt=int(args,0)
            elif op=='bnez':
                if r[p[0]]:nxt=int(p[1],0)
            elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
            elif op=='mov':r[p[0]]=r[p[1]]
            elif op=='movi':r[p[0]]=int(p[1],0)
            elif op=='br':nxt=int(args,0)
            else:raise AssertionError((hex(pc),op,args))
            pc=nxt
        raise AssertionError('bound')
    shifts={peak_shift(v) for v in range(65536)}
    assert shifts==set(range(16))
    final={9-a-b for a in shifts for b in range(16)}
    assert min(final)==-21 and max(final)==9
    report={'stock_sha256':IMAGE_SHA,'decoded_peak_cases':65536,'peak_shift_range':[0,15],'restoration_shift_range':[-21,9],'normalization_call':0x46592,'restoration_call':0x465d0,'both_calls_exact_inplace':True,'source_admitted':False,'limits':['Restoration range assumes stored spectrum shift was written by valid spectrum preparation (0..15) and helper ABI/state integrity.','Local argument/peak-scan proof, not complete beam output execution or global state-writer/computed-reference closure.']}
    (ROOT/'docs/research/gx8002-beam-shift-callers.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(analyze())
