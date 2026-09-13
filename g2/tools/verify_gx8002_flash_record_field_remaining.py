# SPDX-License-Identifier: MIT
"""Classify final four reads from the initial immediate-offset12 census."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode

def verify():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');rows=[]
    for object_name,specs in (
      ('generic_spi_nor.o',(('gx_generic_spi_norflash_readdata',0x188,[(0xc,'lrw','r11, 0x0'),(0x34,'ld.w','r3, (r11, 0xc)'),(0x38,'cmphs','r3, r7')]),('gx_generic_spi_norflash_erasedata',0xa0,[(2,'lrw','r2, 0x0'),(4,'ld.w','r3, (r2, 0xc)'),(6,'cmphs','r0, r3')]),('gx_gereric_spi_norflash_pageprogram',0x70,[(0x12,'lrw','r2, 0x0'),(0x14,'ld.w','r2, (r2, 0xc)'),(0x16,'cmphs','r2, r3')]))),
      ('flash_spi.o',(('gx_xip_init',None,[(0x18,'ld.w','r13, (r14, 0xc)')]),))):
        rel='drivers_lib/mtd/spinor/'+object_name;path=sdk/rel;blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();data=authenticated_blob(path,blob);elf=Elf32(data,rel)
        for name,pool,steps in specs:
            section=next(s for s in elf.sections if s['name']=='.text.'+name);code=decode(subprocess.check_output([pre,'-d','-j',section['name'],str(path)],text=True))
            for pc,op,args in steps:assert code[pc][:2]==(op,args)
            if pool is not None:
                relocation=next(r for r in elf.relocations(section['index']) if r['offset']==pool);symbol=elf.symbols()[relocation['symbol']]
                assert relocation['type']==1 and relocation['addend']==0 and elf.sections[symbol['section']]['name']=='.data' and symbol['value']==0
                info=next(s for s in elf.symbols() if s['name']=='g_flash_info');assert info['section']==symbol['section'] and info['value']==0
                classification='generic driver local g_flash_info+12 bounds value; not spinor_list record'
            else:
                assert not any('r14' in args.split(',')[0] or op=='push' for pc,(op,args,w) in code.items() if pc<0x18)
                classification='incoming stack argument at SP+12'
            rows.append({'object':rel,'object_sha256':sha(data),'blob':blob,'symbol':name,'section_sha256':sha(elf.contents(section)),'verified_steps':steps,'classification':classification})
    return {'sdk_commit':SDK_COMMIT,'paths':rows,'classified_reads':4,'source_admitted':False,'limits':['Completes classification of initial32 immediate word-load candidates together with28-path report. Does not cover indexed/byte/halfword accesses, pointer arithmetic, other objects or stock-only consumers; no unused-field proof.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-flash-record-field-remaining.json').write_text(json.dumps(r,indent=2)+'\n');print(r['classified_reads'])
