# SPDX-License-Identifier: MIT
"""Measure unchanged adapted shift source with native compiler options."""
import json,subprocess
from build_gx8002_beam_shift_q15 import build,ROOT,FLAGS,Elf32

def probe():
    baseline=build();out=ROOT/'build/gx8002-beam-shift-q15';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');rows=[]
    for label,extra in [('no-loop',['-fno-tree-loop-optimize']),('no-guess',['-fno-guess-branch-probability']),('no-loop-no-guess',['-fno-tree-loop-optimize','-fno-guess-branch-probability']),('no-crossjump',['-fno-crossjumping']),('no-inline',['-fno-inline']),('O2',['-O2'])]:
        obj=out/(label+'.o');elfpath=out/(label+'.elf')
        subprocess.run([pre+'gcc','-Os',*FLAGS[1:],*extra,'-DCSKY_MATH_NO_SIMD','-Dcsky_shift_q15=beam_shift_q15','-I',str(out),'-c',str(out/'csky_shift_q15.c'),'-o',str(obj)],check=True)
        subprocess.run([pre+'ld','-T',str(out/'shift.ld'),str(obj),'-o',str(elfpath)],check=True)
        elf=Elf32(elfpath.read_bytes(),label);size=sum(s['size'] for s in elf.sections if s['flags']&2)
        rows.append({'label':label,'flags':extra,'bytes':size,'fits':size<=116})
    report={'baseline':baseline,'experiments':rows,'limits':['Size measurements only; experimental flags not behaviorally qualified or integrated.']}
    (ROOT/'docs/research/gx8002-beam-shift-size.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(probe()['experiments'])
