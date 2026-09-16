# SPDX-License-Identifier: MIT
"""Build authenticated divider/DTO setters with inlined backup register helpers."""
import json,subprocess
from build_gx8002_clock_module_divider_set_candidate import build as divider_build,ROOT,Elf32,sha
from build_gx8002_clock_module_dto_set_candidate import build as dto_build


def build():
    evidence={'divider':divider_build(),'dto':dto_build()};out=ROOT/'build/gx8002-backup-clock-rate-setters';out.mkdir(exist_ok=True)
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    header=(sdk/'arch/soc/grus/include/clk_priv.h').read_text()
    # The preceding candidate builders authenticate this exact upstream header.
    assert sha(header.encode())==evidence['divider']['oracle']['sha256']==evidence['dto']['oracle']['sha256']
    helper='''static inline __attribute__((always_inline)) void __reg_set_val(unsigned int address, unsigned int offset, unsigned int value, unsigned int mask)
{
    volatile uint32_t *reg=(volatile uint32_t *)(uintptr_t)address;
    *reg=(*reg & ~(mask<<offset)) | (value<<offset);
}'''
    rows=[]
    for name,address,limit in (('divider',0x10003788,352),('dto',0x100038e8,268)):
        stem='clock-module-'+name+'-set';source=(ROOT/'build/gx8002-board'/f'{stem}.c').read_text()
        declaration='extern void __reg_set_val(unsigned int,unsigned int,int,unsigned int);';assert declaration in source
        source=source.replace(declaration,helper)
        if name=='divider':
            getter=header[header.index('static int __module_get_div'):header.index('static int __module_get_dto')]
            getter=getter.replace('static int __module_get_div','static inline __attribute__((always_inline)) int __module_get_div')
            source=source.replace('extern int __module_get_div(GX_CLOCK_MODULE_INFO);',getter)
        (out/f'{name}.c').write_text(source)
        subprocess.run([pre+'gcc',*evidence[name]['flags'],'-I'+str(ROOT/'build/gx8002-board'/f'{stem}-config'),'-isystem',str(sdk/'arch/soc/grus/include'),'-isystem',str(sdk/'include'),'-isystem',str(sdk/'include/utility'),'-c',str(out/f'{name}.c'),'-o',str(out/f'{name}.o')],check=True)
        (out/f'{name}.ld').write_text(f'SECTIONS {{ .text {address:#x} : {{ *(.text*) *(.rodata*) }} }}\n__module_get_info = 0x100034e0;\n')
        path=out/f'{name}.elf';subprocess.run([pre+'ld','-T',str(out/f'{name}.ld'),str(out/f'{name}.o'),'-o',str(path)],check=True)
        elf=Elf32(path.read_bytes(),name);assert not any(s['name'] and s['section']==0 for s in elf.symbols());assert not any(elf.relocations(s['index']) for s in elf.sections)
        size=next(s['size'] for s in elf.sections if s['name']=='.text')
        (out/f'{name}.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
        rows.append({'name':name,'address':address,'bytes':size,'envelope_bytes':limit,'fits':size<=limit,'source_sha256':sha(source.encode()),'elf_sha256':sha(path.read_bytes())})
    report={'upstream_evidence':evidence,'functions':rows,'source_admitted':False,'limits':['Source register helper and divider getter inlined; lookup remains an explicit backup binding. Backup-specific behavior and placement qualification pending. Unsigned shifts require valid bit offsets.']}
    (ROOT/'docs/research/gx8002-backup-clock-rate-setters.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(build()['functions'])
