# SPDX-License-Identifier: MIT
"""Link the pinned SPL reader and both register helpers as source definitions."""
import json,subprocess
from build_gx8002_stage1_flash_registers import build as registers_build,ROOT,Elf32,sha


def build():
    evidence=registers_build();out=ROOT/'build/gx8002-stage1-flash-cluster';out.mkdir(exist_ok=True)
    reader=ROOT/'build/gx8002-stage1-flash-read';registers=ROOT/'build/gx8002-stage1-flash-registers'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    ld=(reader/'flash.ld').read_text().replace('SECTIONS {','SECTIONS {\n.read 0x10000edc : { *(.text.sflash_read_reg) }\n.write 0x10000f5c : { *(.text.sflash_write_reg) }',1)
    ld=ld.replace('sflash_read_reg = 0x10000edc;\n','').replace('sflash_write_reg = 0x10000f5c;\n','')
    (out/'cluster.ld').write_text(ld);path=out/'cluster.elf'
    subprocess.run([pre+'ld','-T',str(out/'cluster.ld'),str(reader/'global.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'flash cluster')
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    for original_path in (reader/'flash.elf',registers/'registers.elf'):
        original=Elf32(original_path.read_bytes(),'independent')
        for section in original.sections:
            if section['flags']&2 and section['size']:
                linked=next(s for s in elf.sections if s['name']==section['name'])
                assert linked['address']==section['address'] and elf.contents(linked)==original.contents(section)
    for name,limit in (('.read',128),('.write',128),('.text',600),('.data',4)):
        assert next(s['size'] for s in elf.sections if s['name']==name)<=limit
    absolute=[s['name'] for s in elf.symbols() if s['section']==0xfff1 and s['type']!=4 and s['name']]
    assert absolute==['spl_clk_set_gate_enable'],absolute
    for name in ('sflash_readdata','sflash_read_reg','sflash_write_reg','wait_till_ready'):
        symbol=next(s for s in elf.symbols() if s['name']==name)
        assert symbol['section'] not in (0,0xfff1),name
    ranges=sorted((s['address']&0xfffffff,(s['address']&0xfffffff)+s['size']) for s in elf.sections if s['flags']&2 and s['size'])
    assert all(a[1]<=b[0] for a,b in zip(ranges,ranges[1:]))
    (out/'cluster.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'registers_build':evidence,'elf_sha256':sha(path.read_bytes()),'sections':[{'name':s['name'],'address':s['address'],'bytes':s['size']} for s in elf.sections if s['flags']&2 and s['size']],'source_admitted':False,'limits':['Reader and register helper bodies match separately qualified builds; all flash functions are section-defined source. Clock gate remains an absolute dependency. Composed execution and full firmware integration pending.']}
    (ROOT/'docs/research/gx8002-stage1-flash-cluster.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(build()['sections'])
