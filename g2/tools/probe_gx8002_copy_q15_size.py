# SPDX-License-Identifier: MIT
"""Measure native C-SKY optimization options without changing admitted code."""
import json,subprocess
from build_gx8002_backup_copy_q15 import ROOT,FLAGS,Elf32,sha

def probe(guarded=False):
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_copy_q15.c'
    out=ROOT/'build/gx8002-copy-q15-size-probe';out.mkdir(exist_ok=True)
    if guarded:
        text=source.read_text().replace('while (groups--) {','if (groups) do {').replace('        dst += 2;\n    }','        dst += 2;\n    } while (--groups);').replace('while (tail--) *half_dst++ = *half_src++;','if (tail) do { *half_dst++ = *half_src++; } while (--tail);')
        source=out/'guarded.c';source.write_text(text)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    rows=[]
    for optimization in ('-Os','-O2'):
        for extra in ([],['-fno-tree-loop-optimize'],['-fno-ivopts'],['-fno-tree-loop-optimize','-fno-ivopts'],['-fno-caller-saves'],['-fno-tree-scev-cprop']):
            path=out/f'variant{len(rows)}.o';flags=[optimization,*FLAGS[1:],*extra]
            subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(path)],check=True)
            elf=Elf32(path.read_bytes(),'copy size');size=sum(s['size'] for s in elf.sections if s['flags']&4)
            rows.append({'flags':flags,'bytes':size,'object_sha256':sha(path.read_bytes())})
    result={'source_sha256':sha(source.read_bytes()),'variants':rows,'smallest_bytes':min(r['bytes'] for r in rows),'stock_envelope_bytes':44,'source_admitted':False}
    (ROOT/('docs/research/gx8002-copy-q15-guarded-size-probe.json' if guarded else 'docs/research/gx8002-copy-q15-size-probe.json')).write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=probe();print([(v['flags'][0],v['flags'][len(FLAGS):],v['bytes']) for v in r['variants']])
