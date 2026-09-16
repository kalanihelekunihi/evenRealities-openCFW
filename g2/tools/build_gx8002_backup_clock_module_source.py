# SPDX-License-Identifier: MIT
"""Build recovered grouped-clock source switching for the backup address map."""
import json,subprocess
from build_gx8002_clock_module_source_fixed_candidate import build as authenticate,ROOT,Elf32,sha


def build():
    evidence=authenticate();out=ROOT/'build/gx8002-backup-clock-module-source';out.mkdir(exist_ok=True)
    original=ROOT/'build/gx8002-board/clock-module-source-fixed.c'
    source=original.read_text().replace('extern void __reg_set_val(unsigned int,unsigned int,int,unsigned int);','''static inline __attribute__((always_inline)) void __reg_set_val(unsigned int address, unsigned int offset, unsigned int value, unsigned int mask)
{
    volatile uint32_t *reg = (volatile uint32_t *)(uintptr_t)address;
    *reg = (*reg & ~(mask << offset)) | (value << offset);
}''')
    assert source!=original.read_text();(out/'source.c').write_text(source)
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc',*evidence['flags'],'-I'+str(ROOT/'build/gx8002-board/clock-module-source-fixed-config'),'-isystem',str(sdk/'arch/soc/grus/include'),'-isystem',str(sdk/'include'),'-isystem',str(sdk/'include/utility'),'-c',str(out/'source.c'),'-o',str(out/'source.o')],check=True)
    (out/'source.ld').write_text('SECTIONS { .text 0x100035c0 : { *(.text*) *(.rodata*) } }\n__module_get_info = 0x100034e0;\ngx_clock_param_table = 0x2001699c;\n')
    path=out/'source.elf';subprocess.run([pre+'ld','-T',str(out/'source.ld'),str(out/'source.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'module source');assert not any(s['name'] and s['section']==0 for s in elf.symbols());assert not any(elf.relocations(s['index']) for s in elf.sections)
    size=next(s['size'] for s in elf.sections if s['name']=='.text')
    (out/'source.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'upstream_evidence':evidence,'source_sha256':sha(source.encode()),'elf_sha256':sha(path.read_bytes()),'bytes':size,'envelope_bytes':456,'fits':size<=456,'source_admitted':False,'limits':['Grouped traversal starts at resolved parent row; unsigned register-mask helper inlined. Lookup and source parameter-table address remain explicit bindings. Backup decoded behavior and placement qualification pending; no hardware claim.']}
    (ROOT/'docs/research/gx8002-backup-clock-module-source.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(build()['bytes'])
