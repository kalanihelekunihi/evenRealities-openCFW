# SPDX-License-Identifier: MIT
"""Build pinned SPL SPI-NOR read source with recovered configuration."""
import json,re,subprocess
from build_gx8002_stage1_platform_gate import build as authenticate,ROOT,SDK_COMMIT,authenticated_blob,sha,Elf32
from verify_gx8002_analog_source import FLAGS


def build():
    evidence=authenticate();sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-stage1-flash-read';out.mkdir(exist_ok=True);deps=[]
    for name in ('arch/soc/grus/spl/spl_spinor.c','arch/soc/grus/spl/spl_spinor.h','include/driver/gx_flash.h'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+name],text=True).strip();data=authenticated_blob(sdk/name,blob);deps.append({'path':name,'blob':blob,'sha256':sha(data)})
        if name.endswith('.c'):body=data.decode()
        elif name.endswith('spl_spinor.h'):(out/'spl_spinor.h').write_bytes(data)
    body=re.sub(r'^#include .*\n','',body,flags=re.M)
    # Keep register transfer calls outlined; all other private wrappers may inline.
    body=re.sub(r'^static (?:inline )?(int|uint8_t) (?!sflash_read_reg\b|sflash_write_reg\b)(\w+)\(',r'static inline __attribute__((always_inline)) \1 \2(',body,flags=re.M)
    body=body.replace('static inline __attribute__((always_inline)) int wait_till_ready(', 'static __attribute__((noinline)) int wait_till_ready(')
    (out/'common.h').write_text('#include <stdint.h>\n#include <stddef.h>\n#define readl(a) (*(volatile uint32_t *)(uintptr_t)(a))\n#define writel(v,a) (*(volatile uint32_t *)(uintptr_t)(a)=(v))\n#define min(a,b) ((a)<(b)?(a):(b))\n')
    (out/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n#define CONFIG_FLASH_SPI_QUAD 1\n#define CONFIG_SF_DEFAULT_SAMPLE_DELAY 1\n#define CONFIG_SF_DEFAULT_CLKDIV 2\n')
    source=out/'flash.c';source.write_text('#include <common.h>\n#include <driver/gx_flash.h>\n#include <driver/gx_clock.h>\n#include "spl_spinor.h"\n#include <autoconf.h>\n'+body)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:],'-fno-ipa-sra','-fno-ipa-cp']
    subprocess.run([pre+'gcc',*flags,'-isystem',str(out),'-isystem',str(sdk/'include'),'-isystem',str(sdk/'arch/soc/grus/include'),'-c',str(source),'-o',str(out/'flash.o')],check=True)
    subprocess.run([pre+'objcopy','--globalize-symbol=sflash_read_reg','--globalize-symbol=sflash_write_reg',str(out/'flash.o'),str(out/'global.o')],check=True)
    ld='''SECTIONS {
.text 0x10000fdc : { *(.text.sflash_readdata) *(.text.wait_till_ready) }
.data 0x20001730 : { *(.data.flash_jedec) }
/DISCARD/ : { *(.text.sflash_read_reg .text.sflash_write_reg) }
.analysis_helpers 0x10004000 : { *(.text*) *(.rodata*) }
}
sflash_read_reg = 0x10000edc;
sflash_write_reg = 0x10000f5c;
spl_clk_set_gate_enable = 0x100001f8;
'''
    (out/'flash.ld').write_text(ld);path=out/'flash.elf';subprocess.run([pre+'ld','-T',str(out/'flash.ld'),str(out/'global.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'flash');assert not any(s['name'] and s['section']==0 for s in elf.symbols());assert not any(elf.relocations(s['index']) for s in elf.sections)
    (out/'flash.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    rows=[{'name':s['name'],'address':s['address'],'bytes':s['size']} for s in elf.sections if s['flags']&2 and s['size']]
    size=next(s['size'] for s in elf.sections if s['name']=='.text')
    assert not any(s['name']=='.analysis_helpers' and s['size'] for s in elf.sections)
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==bytes.fromhex('ffffff00')
    report={'adaptations':['Keep wait_till_ready as one source helper inside the original reader envelope; register-transfer calls keep original ABI.'],'code_envelope_bytes':600,'fits':size<=600,'upstream_evidence':evidence,'dependencies':deps,'source_sha256':sha(source.read_bytes()),'flags':flags,'sections':rows,'source_admitted':False,'limits':['Quad SPI, no XIP/DMA; sample delay1, divider2 recovered. Build only; layout/behavior qualification and register-transfer/gate closure pending.']}
    (ROOT/'docs/research/gx8002-stage1-flash-read-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(build()['sections'])
