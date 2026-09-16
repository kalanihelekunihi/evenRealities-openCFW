# SPDX-License-Identifier: MIT
"""Link source initialization, trimming, board hook and trim setters together."""
import json,subprocess
from build_gx8002_stage1_clock_tables import build as tables_build
from build_gx8002_stage1_clock_trim import build as trim_build,ROOT,Elf32,sha


def build():
    lookup_evidence=tables_build();evidence=trim_build();out=ROOT/'build/gx8002-stage1-clock-cluster';out.mkdir(exist_ok=True)
    init_dir=ROOT/'build/gx8002-stage1-clock-initialize';trim_dir=ROOT/'build/gx8002-stage1-clock-trim'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    init_obj=out/'init-input.o';trim_obj=out/'trim-input.o'
    subprocess.run([pre+'objcopy','--globalize-symbol=__module_get_info',str(init_dir/'global.o'),str(init_obj)],check=True)
    subprocess.run([pre+'objcopy','--weaken-symbol=__module_get_info',str(trim_dir/'global.o'),str(trim_obj)],check=True)
    ld=(init_dir/'initialize.ld').read_text()
    ld=ld.replace('SECTIONS {','SECTIONS {\n.lookup 0x10000138 : { *init-input.o(.text.__module_get_info) }\n.clock_trim 0x100004f4 : { *(.text.spl_clk_trim) }\n.data.low 0x20001668 : { *(.data.clk_low_table*) }\n.data.high 0x20001678 : { *(.data.clk_src_high_table*) }',1)
    for name in ('param','dto','div'):
        ld=ld.replace(f'*(.data.gx_clock_{name}_table)',f'*init-input.o(.data.gx_clock_{name}_table)')
    ld=ld.replace('*(.text.__module_get_info .text.open_cfw_stage1_lookup_contract)', '*(.text.__module_get_info .text.open_cfw_stage1_lookup_contract) *trim-input.o(.data.gx_clock_*) *lookup-input.o(.data* .text* .rodata*)')
    ld=ld.replace('open_cfw_gx8002_stage1_clock_trim = 0x100004f4;', 'open_cfw_gx8002_stage1_clock_trim = spl_clk_trim;')
    ld=ld.replace('__module_get_info = 0x10000138;\n','')
    ld+='sflash_readdata = 0x10000fdc;\n'
    (out/'cluster.ld').write_text(ld);path=out/'cluster.elf'
    subprocess.run([pre+'ld','-T',str(out/'cluster.ld'),str(init_obj),str(trim_obj),str(init_dir/'board.o'),str(ROOT/'build/gx8002-stage1-trim-setters/setters.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'clock cluster');assert not any(s['name'] and s['section']==0 for s in elf.symbols());assert not any(elf.relocations(s['index']) for s in elf.sections)
    for original_path,mapping in ((init_dir/'initialize.elf',{}),(trim_dir/'trim.elf',{'.text':'.clock_trim'})):
        original=Elf32(original_path.read_bytes(),'standalone')
        for section in original.sections:
            if section['flags']&2 and section['size']:
                name=mapping.get(section['name'],section['name']);linked=next(s for s in elf.sections if s['name']==name)
                assert linked['address']==section['address'] and elf.contents(linked)==original.contents(section),name
    lookup_section=next(s for s in elf.sections if s['name']=='.lookup');assert lookup_section['size']<=192
    from compare_gx8002_stage1_clock_lookup import execute as lookup_execute
    from verify_gx8002_memcpy_source import decode
    import struct
    linked_code=decode(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    independent_code=decode((ROOT/'build/gx8002-stage1-clock-tables/lookup.disassembly.txt').read_text())
    table=elf.contents(next(s for s in elf.sections if s['name']=='.data.gx_clock_param_table'))
    ids=[struct.unpack_from('<I',table,i*16)[0] for i in range(26)]
    for module in (*range(28),0x7fffffff,0x80000000,0xffffffff):
        for pointer in (0,0x1000):
            assert lookup_execute(linked_code,0x10000138,module,pointer,ids)==lookup_execute(independent_code,0x10000138,module,pointer,ids)
    symbol=next(s for s in elf.symbols() if s['name']=='__module_get_info');assert symbol['section'] not in (0,0xfff1)
    ranges=sorted((s['address']&0xfffffff,(s['address']&0xfffffff)+s['size']) for s in elf.sections if s['flags']&2 and s['size'])
    assert all(a[1]<=b[0] for a,b in zip(ranges,ranges[1:]))
    (out/'cluster.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'lookup_build':lookup_evidence,'trim_build':evidence,'elf_sha256':sha(path.read_bytes()),'sections':[{'name':s['name'],'address':s['address'],'bytes':s['size']} for s in elf.sections if s['flags']&2 and s['size']],'source_admitted':False,'limits':['Existing component bodies match independent builds; linked lookup fits and passes62 comparisons against independently qualified lookup, with physical SRAM overlap check. Lookup is linked source; flash read remains the only absolute implementation in this component. Full initialization behavior, references and firmware integration pending.']}
    (ROOT/'docs/research/gx8002-stage1-clock-cluster.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(build()['sections'])
