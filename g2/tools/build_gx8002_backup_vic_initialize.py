# SPDX-License-Identifier: MIT
"""Build the complete pinned upstream VIC initializer with explicit ABI bindings."""
import json
import subprocess
from analyze_gx8002_upstream_objects import ROOT, SDK_COMMIT, authenticated_blob, sha
from build_gx8002_backup_cfft import FLAGS, Elf32


def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='arch/soc/grus/system.c'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
    original=authenticated_blob(sdk/rel,blob).decode()
    start=original.index('static inline void system_vic_init(void)')
    end=original.index('\nextern void clear_bss',start)
    function=original[start:end]
    out=ROOT/'build/gx8002-backup-vic-initialize';out.mkdir(exist_ok=True)
    # Names and offsets are the bindings used by the original stock sequence.
    prefix='''#include <stdint.h>
#include <stddef.h>
typedef struct {
    uint8_t reserved0[0x180];
    volatile uint32_t ICPR[4];
    uint8_t reserved1[0x70];
    volatile uint32_t IABR[4];
    uint8_t reserved2[0x900];
    volatile uint32_t TSPR;
} vic_binding;
_Static_assert(offsetof(vic_binding, ICPR)==0x180, "pending offset");
_Static_assert(offsetof(vic_binding, IABR)==0x200, "active offset");
_Static_assert(offsetof(vic_binding, TSPR)==0xb10, "threshold offset");
#define VIC ((vic_binding *)(uintptr_t)0xe000e100)
extern uint32_t __Vectors[];
static inline void __set_VBR(uint32_t value) { __asm__ volatile("mtcr %0, cr<1, 0>" :: "r"(value) : "memory"); }
static inline void __enable_excp_irq(void) { __asm__ volatile("psrset ee, ie" ::: "memory"); }
'''
    source=out/'vic.c';source.write_text(prefix+function+'\nvoid open_cfw_gx8002_backup_vic_initialize(void) { system_vic_init(); }\n')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');obj=out/'vic.o'
    subprocess.run([pre+'gcc',*FLAGS,'-Os','-c',str(source),'-o',str(obj)],check=True)
    ld=out/'vic.ld';ld.write_text('SECTIONS { .text 0x10018000 : { *(.text*) } }\n__Vectors = 0x10003000;\n')
    path=out/'vic.elf';subprocess.run([pre+'ld','-T',str(ld),str(obj),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'VIC source');sec=next(s for s in elf.sections if s['name']=='.text')
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    (out/'vic.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    return {'upstream_commit':SDK_COMMIT,'upstream_path':rel,'upstream_blob':blob,'upstream_function_sha256':sha(function.encode()),'binding_source_sha256':sha(source.read_bytes()),'elf_sha256':sha(path.read_bytes()),'code_bytes':sec['size'],'source_admitted':False,'limits':['Complete upstream static initializer extracted unchanged with explicit register-layout and control-register bindings. Standalone analysis address, not firmware placement. Decoded ordered behavior, integration and physical interrupt acceptance still need qualification.']}


if __name__=='__main__':
    result=build();(ROOT/'docs/research/gx8002-backup-vic-initialize.json').write_text(json.dumps(result,indent=2)+'\n');print(result['code_bytes'],'upstream VIC initializer bytes')
