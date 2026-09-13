# SPDX-License-Identifier: MIT
"""Link existing source UART defaults at stock placement without binary input."""
import json,subprocess
from analyze_gx8002_uart_descriptor_data import analyze,ROOT,sha,Elf32
from analyze_gx8002_upstream_objects import SDK_COMMIT,authenticated_blob

def build():
    evidence=analyze();sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');source=ROOT/'components/shared/gx8002/runtime_gx8002_uart_storage.c';obj=out/'uart-descriptor.o';script=out/'uart-descriptor.ld';path=out/'uart-descriptor.elf'
    headers=[]
    for rel in ('arch/soc/grus/include/base_addr.h','arch/soc/grus/include/soc.h'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();data=authenticated_blob(sdk/rel,blob);headers.append({'path':rel,'blob':blob,'sha256':sha(data)})
    subprocess.run([pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-ffreestanding','-fno-builtin','-fdata-sections','-Wall','-Wextra','-Werror','-I'+str(sdk/'arch/soc/grus/include'),'-c',str(source),'-o',str(obj)],check=True)
    script.write_text('SECTIONS { .descriptors 0x20026a94 : { *(.data.open_cfw_gx8002_uart_descriptors) } }\n')
    subprocess.run([pre+'ld','-T',str(script),str(obj),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'UART');sections=[s for s in elf.sections if s['flags']&2 and s['size']];assert len(sections)==1;s=sections[0]
    assert (s['address'],s['size'],s['flags'])==(0x20026a94,256,3) and sha(elf.contents(s))==evidence['sha256'] and not elf.relocations(s['index'])
    r={'headers':headers,'provenance':evidence,'source_sha256':sha(source.read_bytes()),'elf_sha256':sha(path.read_bytes()),'compiled_bytes':s['size'],'source_admitted':False,'limits':['Existing source initializer compiled at original location; complete byte match. Fields7/8 default8/1 but semantic names unresolved; do not call them data/stop bits without evidence. SDK headers authenticated. Consumer/startup ownership qualification pending.']}
    (ROOT/'docs/research/gx8002-uart-descriptor-candidate.json').write_text(json.dumps(r,indent=2)+'\n');return r
if __name__=='__main__':print(build()['compiled_bytes'])
