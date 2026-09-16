# SPDX-License-Identifier: MIT
"""Build backup PLL configuration/wait functions from authenticated source."""
import json,subprocess
from build_gx8002_clock_pll_candidate import build as pll_build,ROOT,Elf32,sha
from build_gx8002_clock_pll_wait_candidate import build as wait_build


def build():
    evidence={'pll':pll_build(),'wait':wait_build()};out=ROOT/'build/gx8002-backup-clock-pll';out.mkdir(exist_ok=True)
    sources=[ROOT/'components/shared/gx8002'/name for name in ('runtime_gx8002_clock_pll.c','runtime_gx8002_clock_pll_wait.c')]
    config=sources[0].read_text().replace('void open_cfw_gx8002_clock_pll(', 'static inline __attribute__((always_inline)) void open_cfw_gx8002_clock_pll(')
    wait=sources[1].read_text().replace('extern void open_cfw_gx8002_clock_pll(GX_CLOCK_PLL *pll);','')
    source=config+'\n'+wait;(out/'pll.c').write_text(source)
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    header=(sdk/'arch/soc/grus/include/clk_priv.h').read_text();assert sha(header.encode())==evidence['pll']['oracle']['sha256']
    header=header.replace('static inline void _clk_set_pll(', 'static inline __attribute__((always_inline)) void _clk_set_pll(')
    (out/'clk_priv.h').write_text(header)
    subprocess.run([pre+'gcc',*evidence['pll']['flags'],'-isystem',str(out),'-I'+str(ROOT/'build/gx8002-board/clock-pll-config'),'-isystem',str(sdk/'arch/soc/grus/include'),'-isystem',str(sdk/'include'),'-isystem',str(sdk/'include/utility'),'-c',str(out/'pll.c'),'-o',str(out/'pll.o')],check=True)
    (out/'pll.ld').write_text('''SECTIONS {
.timeout 0x100039f4 : { *(.text.open_cfw_gx8002_clock_pll_wait_timeout) }
.wait 0x10003b08 : { *(.text.open_cfw_gx8002_clock_pll_wait) }
}
open_cfw_gx8002_clock_time_us = 0x10005070;
''')
    path=out/'pll.elf';subprocess.run([pre+'ld','-T',str(out/'pll.ld'),str(out/'pll.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'backup PLL');assert not any(s['name'] and s['section']==0 for s in elf.symbols());assert not any(elf.relocations(s['index']) for s in elf.sections)
    assert {s['name'] for s in elf.sections if s['flags']&2 and s['size']}=={'.timeout','.wait'}
    rows=[]
    for name,limit in (('.timeout',276),('.wait',224)):
        sec=next(s for s in elf.sections if s['name']==name);rows.append({'name':name,'address':sec['address'],'bytes':sec['size'],'envelope_bytes':limit,'fits':sec['size']<=limit})
    (out/'pll.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'upstream_evidence':evidence,'source_sha256':sha(source.encode()),'elf_sha256':sha(path.read_bytes()),'functions':rows,'source_admitted':False,'limits':['Configuration forced inline in existing reconstructed wait wrappers. Timeout entry uses64-bit microseconds and32-bit timeout multiplication with strict greater-than comparison. Microsecond function remains explicit backup binding. Non-null configuration pointer required by wrapper, matching stock dereference after configuration helper. Backup behavior and full firmware integration pending.']}
    (ROOT/'docs/research/gx8002-backup-clock-pll.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(build()['functions'])
