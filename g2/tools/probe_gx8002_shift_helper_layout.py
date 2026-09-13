# SPDX-License-Identifier: MIT
"""Measure helper inlining choices without changing the source candidate."""
import json,subprocess
from build_gx8002_backup_shift_q15 import ROOT,FLAGS,Elf32,sha

def probe():
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_shift_q15.c';original=source.read_text()
    out=ROOT/'build/gx8002-shift-helper-probe';out.mkdir(exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');rows=[]
    variants={'baseline':original,
              'word_noinline':original.replace('static inline uint32_t shift_word','static __attribute__((noinline)) uint32_t shift_word'),
              'sample_always_inline':original.replace('static inline uint16_t shift_sample','static inline __attribute__((always_inline)) uint16_t shift_sample'),
              'word_noinline_sample_inline':original.replace('static inline uint32_t shift_word','static __attribute__((noinline)) uint32_t shift_word').replace('static inline uint16_t shift_sample','static inline __attribute__((always_inline)) uint16_t shift_sample')}
    for name,text in variants.items():
        path=out/(name+'.c');path.write_text(text);obj=out/(name+'.o')
        subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-fno-tree-loop-optimize','-c',str(path),'-o',str(obj)],check=True)
        elf=Elf32(obj.read_bytes(),name)
        rows.append({'variant':name,'source_sha256':sha(path.read_bytes()),'object_sha256':sha(obj.read_bytes()),'code_bytes':sum(s['size'] for s in elf.sections if s['flags']&4)})
    report={'baseline_source_sha256':sha(source.read_bytes()),'variants':rows,'source_admitted':False}
    (ROOT/'docs/research/gx8002-shift-helper-probe.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(probe()['variants'])
