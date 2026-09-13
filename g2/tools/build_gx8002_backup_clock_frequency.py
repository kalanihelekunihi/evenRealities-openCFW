# SPDX-License-Identifier: MIT
"""Compile upstream frequency logic with the backup's inline divider path."""
import json,subprocess
from build_gx8002_backup_platform_gate import build as authenticate,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_analog_source import FLAGS


def build():
    evidence=authenticate();out=ROOT/'build/gx8002-backup-clock-frequency';out.mkdir(exist_ok=True)
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    # The backup inlines divider reads. Use the authenticated upstream header
    # directly rather than the primary image's two-register divider adapter.
    header=(sdk/'arch/soc/grus/include/clk_priv.h').read_bytes()
    (out/'clk_priv_frequency.h').write_bytes(header)
    (out/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_clock_frequency.c'
    flags=['-Os',*FLAGS[1:],'-fno-tree-loop-optimize','-fno-delete-null-pointer-checks']
    subprocess.run([pre+'gcc',*flags,'-isystem',str(out),'-isystem',str(sdk/'arch/soc/grus/include'),'-isystem',str(sdk/'include'),'-c',str(source),'-o',str(out/'frequency.o')],check=True)
    subprocess.run([pre+'objcopy','--globalize-symbol=__module_get_info',str(out/'frequency.o'),str(out/'global.o')],check=True)
    (out/'frequency.ld').write_text('''SECTIONS {
.text 0x10003cf0 : { *(.text.open_cfw_gx8002_clock_frequency) }
.rodata 0x100129f0 : { *(.rodata.open_cfw_gx8002_clock_frequency) }
/DISCARD/ : { *(.text*) *(.data*) *(.rodata*) }
}
__module_get_info = 0x100034e0;
''')
    subprocess.run([pre+'ld','-T',str(out/'frequency.ld'),str(out/'global.o'),'-o',str(out/'frequency.elf')],check=True)
    elf=Elf32((out/'frequency.elf').read_bytes(),'backup frequency');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    rows=[]
    for name,address,size in (('.text',0x10003cf0,492),('.rodata',0x100129f0,76)):
        section=next(s for s in elf.sections if s['name']==name);body=elf.contents(section)
        assert section['address']==address and not elf.relocations(section['index'])
        rows.append({'section':name,'address':address,'compiled_bytes':len(body),'compiled_sha256':sha(body),
                     'envelope_bytes':size,'fits':len(body)<=size})
    (out/'frequency.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(out/'frequency.elf')],text=True))
    report={'upstream_evidence':evidence,'header_sha256':sha(header),'source_sha256':sha(source.read_bytes()),'flags':flags,
            'sections':rows,'source_admitted':False,'hardware_qualified':False,
            'limits':['Candidate only: unchanged authenticated upstream frequency arithmetic with inline divider.',
                      'Lookup at original backup binding; frequency/PLL behavior, switch references and loader not qualified.']}
    (ROOT/'docs/research/gx8002-backup-clock-frequency-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':print(json.dumps(build()['sections'],indent=2))
