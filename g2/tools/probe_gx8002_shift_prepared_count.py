# SPDX-License-Identifier: MIT
"""Measure moving count normalization from sample helper to buffer entry."""
import json,subprocess
from build_gx8002_backup_shift_q15 import ROOT,FLAGS,Elf32,sha

def probe():
    original=ROOT/'components/shared/gx8002/runtime_gx8002_backup_shift_q15.c';text=original.read_text()
    old='''        uint32_t magnitude = shift == INT32_MIN ? INT32_MAX : (uint32_t)-shift;
        uint32_t bits = magnitude & 31u;'''
    assert text.count(old)==1
    text=text.replace(old,'        uint32_t bits = (uint32_t)~shift;')
    marker='    const volatile alias_word *src =';assert text.count(marker)==1
    text=text.replace(marker,'''    if (shift < 0) {
        uint32_t magnitude = shift == INT32_MIN ? INT32_MAX : (uint32_t)-shift;
        shift = -(int32_t)(magnitude & 31u) - 1;
    } else if (shift > 16) {
        shift = 16;
    }
'''+marker)
    out=ROOT/'build/gx8002-shift-helper-probe';out.mkdir(exist_ok=True)
    source=out/'prepared.c';source.write_text(text);obj=out/'prepared.o'
    subprocess.run([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-gcc'),'-Os',*FLAGS[1:],'-fno-tree-loop-optimize','-c',str(source),'-o',str(obj)],check=True)
    elf=Elf32(obj.read_bytes(),'prepared shift')
    report={'baseline_source_sha256':sha(original.read_bytes()),'source_sha256':sha(source.read_bytes()),'object_sha256':sha(obj.read_bytes()),'code_bytes':sum(s['size'] for s in elf.sections if s['flags']&4),'selected':False,'limits':['Size probe only; variant is not behavior-qualified or admitted. Current candidate source unchanged.']}
    (ROOT/'docs/research/gx8002-shift-prepared-probe.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(probe()['code_bytes'])
