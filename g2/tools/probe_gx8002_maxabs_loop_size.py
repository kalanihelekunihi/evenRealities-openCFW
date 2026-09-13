# SPDX-License-Identifier: MIT
"""Measure loop forms in the Q15 magnitude reduction without editing source."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,FLAGS,Elf32,sha

def probe():
    path=ROOT/'components/shared/gx8002/runtime_gx8002_backup_maxabs_q15.c';base=path.read_text()
    variants={'baseline':base,'guarded':base.replace('while (count--) {','if (count) do {').replace('    }\n    *output','    } while (--count);\n    *output'),'prechecked':base.replace('while (count--) {','for (; count; --count) {')}
    out=ROOT/'build/gx8002-maxabs-loop-probe';out.mkdir(exist_ok=True);rows=[]
    for name,text in variants.items():
        source=out/(name+'.c');source.write_text(text)
        for extra in ([],['-fno-tree-loop-optimize'],['-fno-tree-scev-cprop']):
            obj=out/(name+str(len(rows))+'.o')
            subprocess.run([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-gcc'),'-Os',*FLAGS[1:],*extra,'-c',str(source),'-o',str(obj)],check=True)
            elf=Elf32(obj.read_bytes(),name)
            rows.append({'variant':name,'extra_flags':extra,'source_sha256':sha(source.read_bytes()),'object_sha256':sha(obj.read_bytes()),'code_bytes':sum(s['size'] for s in elf.sections if s['flags']&4)})
    result={'baseline_source_sha256':sha(path.read_bytes()),'variants':rows,'source_admitted':False}
    (ROOT/'docs/research/gx8002-maxabs-loop-probe.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print([(r['variant'],r['extra_flags'],r['code_bytes']) for r in probe()['variants']])
