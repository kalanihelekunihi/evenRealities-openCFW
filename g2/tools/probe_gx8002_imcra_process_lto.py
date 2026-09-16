# SPDX-License-Identifier: MIT
"""Measure complete processing source under native C-SKY link-time optimization."""
import json,subprocess,re
from build_gx8002_imcra_process import build,ROOT
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS

def probe():
    baseline=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    report={'baseline_bytes':baseline['bytes'],'source_admitted':False,'experiments':[]}
    for label,extra in [('lto',[]),('lto-no-caller-saves',['-fno-caller-saves']),('lto-no-loop',['-fno-tree-loop-optimize']),('lto-no-loop-no-caller',['-fno-tree-loop-optimize','-fno-caller-saves']),('lto-no-loop-no-iv',['-fno-tree-loop-optimize','-fno-ivopts']),('lto-register-barriers',['-fno-tree-loop-optimize']),('lto-register-barriers-no-schedule',['-fno-tree-loop-optimize','-fno-schedule-insns','-fno-schedule-insns2']),('lto-register-barriers-no-reorder',['-fno-tree-loop-optimize','-fno-reorder-blocks']),('lto-register-barriers-no-guess',['-fno-tree-loop-optimize','-fno-guess-branch-probability']),('lto-register-barriers-no-inline-once',['-fno-tree-loop-optimize','-fno-inline-functions-called-once']),('lto-register-barriers-shared-min',['-fno-tree-loop-optimize','-fno-guess-branch-probability',*[f'-ffixed-vr{i}' for i in range(8,16)]])]:
        out=ROOT/f'build/gx8002-imcra-process-{label}';out.mkdir(exist_ok=True)
        objects=[];flags=['-Os',*FLAGS[1:],'-flto',*extra]
        for relative in baseline['stage_sources']:
            path=ROOT/relative;obj=out/(path.stem+'.o')
            if label.startswith('lto-register-barriers'):
                # Preserve each explicit intermediate in a floating register,
                # blocking contraction/reassociation across the source boundary.
                original=path.read_text()
                modified=re.sub(r'volatile float (\w+) = ([^;]+);',
                    lambda m:f'float {m[1]} = {m[2]}; __asm__("" : "+v"({m[1]}));',original)
                if label.endswith('shared-min'):
                    pattern=r'for \(int32_t i = 0; i < bins; \+\+i\) \{\s*float previous = minimum\[i\];\s*float current = (smooth|masked)\[i\];\s*if \(previous < current\) current = previous;\s*minimum\[i\] = current;\s*\}'
                    modified,n=re.subn(pattern,lambda m:f'open_cfw_imcra_min_scan(minimum, {m[1]}, bins);',modified)
                    if n:
                        modified=modified.replace('#include <stdint.h>','#include <stdint.h>\nextern void open_cfw_imcra_min_scan(volatile float *, const volatile float *, int32_t);')
                generated=out/path.name;generated.write_text(modified);path=generated
            subprocess.run([pre+'gcc',*flags,'-I',str(ROOT/'build/gx8002-source-rfft-generated-reverse-cluster'),'-c',str(path),'-o',str(obj)],check=True)
            objects.append(str(obj))
        if label.endswith('shared-min'):
            helper=out/'shared_min.c'
            helper.write_text('#include <stdint.h>\n__attribute__((noinline)) void open_cfw_imcra_min_scan(volatile float *minimum, const volatile float *values, int32_t bins) {\n while (bins > 0) {\n  --bins;\n  float previous=*minimum; float current=*values++;\n  if (previous<current) current=previous;\n  *minimum++=current;\n }\n}\n')
            obj=out/'shared_min.o'
            subprocess.run([pre+'gcc',*flags,'-c',str(helper),'-o',str(obj)],check=True)
            objects.append(str(obj))
        script=(ROOT/'build/gx8002-imcra-process/prepare.ld').read_text()
        script='ENTRY(open_cfw_gx8002_imcra_process)\n'+script
        if label.endswith('shared-min'):
            script=script.replace('*(.text*)','*(.text.open_cfw_gx8002_imcra_process) *(.text*)')
        (out/'process.ld').write_text(script);target=out/'process.elf'
        subprocess.run([pre+'gcc',*flags,'-nostdlib','-Wl,-u,open_cfw_gx8002_imcra_process',
                        '-Wl,-T,'+str(out/'process.ld'),*objects,'-o',str(target)],check=True)
        elf=Elf32(target.read_bytes(),label)
        sections=[s for s in elf.sections if s['flags']&2 and s['size']]
        assert len(sections)==1
        assert not any(elf.relocations(s['index']) for s in elf.sections)
        symbols={s['name']:s for s in elf.symbols()}
        assert not any(s['name'] and s['section']==0 for s in elf.symbols())
        assert symbols['open_cfw_gx8002_imcra_process']['section'] not in (0,0xfff1)
        for name,address in baseline['helper_bindings'].items():assert symbols[name]['value']==address
        (out/'process.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(target)],text=True))
        report['experiments'].append({'label':label,'bytes':sections[0]['size'],'flags':flags,'elf':str(target.relative_to(ROOT))})
    report['limits']=['Size experiments only; no stock equivalence or hardware qualification.', 'All stages provided as source. Internal calls may be inlined; external source helpers remain address bindings.', 'No placement or startup integration.']
    (ROOT/'docs/research/gx8002-imcra-process-lto.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(probe(),indent=2))
