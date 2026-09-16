# SPDX-License-Identifier: MIT
"""Compile upstream system initialization with the recovered backup BSS decision."""
import json
import subprocess
import shlex
import re
from pathlib import Path
from analyze_gx8002_upstream_objects import ROOT, SDK_COMMIT, authenticated_blob, sha
from build_gx8002_backup_cfft import FLAGS, Elf32


def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='arch/soc/grus/system.c'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
    original=authenticated_blob(sdk/rel,blob).decode()
    out=ROOT/'build/gx8002-backup-system-initialize';out.mkdir(exist_ok=True)
    (out/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    (out/'stdlib.h').write_text('/* No libc declarations used by this freestanding initializer. */\n')
    # This backup tests the recovered preservation predicate, not start-mode enum.
    source=original.replace('#include <driver/gx_pmu_ctrl.h>', 'extern int open_cfw_gx8002_backup_preserve_memory(void);')
    old='if (gx_pmu_get_start_mode() == GX_START_MODE_ROM)'
    assert source.count(old)==1
    source=source.replace(old,'if (!open_cfw_gx8002_backup_preserve_memory())')
    # Specialize the upstream generic MPU helper to the one recovered region.
    # Preserve volatile control-register read/write order and all unaffected bits.
    source,count=re.subn(r'static inline void system_mpu_init\(void\)\n\{.*?\n\}', '''static inline void system_mpu_init(void)
{
    uint32_t capr = __get_CAPR();
    uint32_t pacr = __get_PACR();
    uint32_t prsr = __get_PRSR();
    __set_PRSR(prsr & ~7u);
    __set_CAPR((capr & 0xfefffcfeu) | 0x300u);
    __set_PACR((pacr & 0xfc0u) | 63u);
    csi_mpu_enable();
}''',source,flags=re.S)
    assert count==1
    path=out/'system.c';path.write_text(source)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');obj=out/'system.o'
    command=[pre+'gcc',*FLAGS,'-Os','-U__CK803__','-U__CK803S__','-D__CK804__=1','-I'+str(out),*[flag for p in (sdk/'arch/soc/grus/include',sdk/'include',sdk/'include/utility') for flag in ('-isystem',str(p))],'-MD','-MF',str(out/'system.d'),'-c',str(path),'-o',str(obj)]
    subprocess.run(command,check=True)
    e=Elf32(obj.read_bytes(),'system initializer')
    dependency_text=(out/'system.d').read_text().replace('\\\n',' ')
    dependencies=[]
    for filename in shlex.split(dependency_text.split(':',1)[1]):
        header=Path(filename)
        item={'path':str(header),'sha256':sha(header.read_bytes())}
        if header.is_relative_to(sdk):
            relative=header.relative_to(sdk).as_posix()
            identity=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+relative],text=True).strip()
            authenticated_blob(header,identity);item['upstream_blob']=identity
        else:
            assert header.is_relative_to(out) or header.is_relative_to(ROOT/'build/csky-macos/install')
            item['kind']='generated_binding' if header.is_relative_to(out) else 'toolchain_header'
        dependencies.append(item)
    bindings={'clk_init':0x3bbd4,'open_cfw_gx8002_backup_preserve_memory':0x3c93c,'clear_bss':0x3ba68,'board_init':0x3be14}
    delta=0x10003000-0x3b940
    ld=out/'system.ld';ld.write_text('SECTIONS { .text 0x1000314c : { *(.text*) } }\n'+''.join(f'{name} = {off+delta:#x};\n' for name,off in bindings.items())+'__Vectors = 0x10003000;\n')
    linked=out/'system.elf';subprocess.run([pre+'ld','-T',str(ld),str(obj),'-o',str(linked)],check=True)
    elf=Elf32(linked.read_bytes(),'linked system initializer')
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    section=next(s for s in elf.sections if s['name']=='.text')
    (out/'system.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(linked)],text=True))

    return {'dependency_headers':dependencies,'elf_sha256':sha(linked.read_bytes()),'linked_bytes':section['size'],'stock_envelope_bytes':164,'fits':section['size']<=164,'absolute_bindings':bindings,'upstream_commit':SDK_COMMIT,'upstream_blob':blob,'adaptation':'Specialize generic MPU setup to recovered region with explicit masks and unchanged volatile order. Use recovered backup preserve-memory predicate instead of upstream ROM-only BSS-clear decision; remove unused incompatible PMU header.','source_sha256':sha(path.read_bytes()),'command':command,'object_sha256':sha(obj.read_bytes()),'sections':[{'name':s['name'],'bytes':s['size']} for s in e.sections if s['flags']&2 and s['size']],'undefined_symbols':[s['name'] for s in e.symbols() if s['name'] and s['section']==0],'source_admitted':False,'limits':['Complete adapted upstream system_init linked to absolute backup entries; these bindings do not authenticate or execute the dependencies. Header closure authenticated against the pinned SDK or recorded toolchain files. Independent execution verifier checks MPU effects and startup control flow; full startup composition and hardware admission remain pending.']}


if __name__=='__main__':
    result=build();(ROOT/'docs/research/gx8002-backup-system-initialize.json').write_text(json.dumps(result,indent=2)+'\n');print(result['sections'],result['undefined_symbols'])
