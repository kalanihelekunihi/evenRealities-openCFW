# SPDX-License-Identifier: MIT
"""Verify selected offset12 reads target runtime/OTP fields, not record+12."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode

def verify():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='drivers_lib/mtd/spinor/flash_spi.o';path=sdk/rel;blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();data=authenticated_blob(path,blob);elf=Elf32(data,'SPI NOR');pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');rows=[]
    specifications=(
      ('sflash_getinfo',0x48,[(0x16,'lrw','r3, 0x0'),(0x18,'ld.w','r3, (r3, 0xc)'),(0x1a,'ld.w','r0, (r3, 0x0)'),(0x1e,'lrw','r3, 0x0'),(0x20,'ld.w','r3, (r3, 0xc)'),(0x22,'ld.w','r0, (r3, 0x4)')],{'0x18':'runtime record pointer','0x20':'runtime record pointer'}),
      ('sflash_otp_get_region',0x10,[(0,'lrw','r3, 0x0'),(2,'ld.w','r3, (r3, 0xc)'),(4,'ld.w','r3, (r3, 0x14)'),(6,'ld.w','r3, (r3, 0xc)')],{'0x2':'runtime record pointer','0x6':'OTP descriptor region field'}),
      ('sflash_quad_read',0xa4,[(0x30,'lrw','r1, 0x0'),(0x34,'ld.w','r1, (r1, 0xc)'),(0x3a,'ld.w','r0, (r1, 0x4)')],{'0x34':'runtime record pointer'}),
      ('gx_spinor_flash_getuid',0x88,[(2,'lrw','r3, 0x0'),(6,'ld.w','r3, (r3, 0xc)'),(8,'ld.b','r3, (r3, 0x6)')],{'0x6':'runtime record pointer'}))
    specifications += (
      ('sflash_write_protect_mode',0x20,[(0,'lrw','r3, 0x0'),(2,'ld.w','r3, (r3, 0xc)'),(4,'ld.w','r3, (r3, 0x10)')],{'0x2':'runtime record pointer'}),
      ('sflash_otp_set_region',0x24,[(0,'lrw','r3, 0x0'),(2,'ld.w','r3, (r3, 0xc)'),(4,'ld.w','r2, (r3, 0x14)'),(6,'ld.w','r3, (r2, 0xc)')],{'0x2':'runtime record pointer','0x6':'OTP descriptor region count'}),
      ('sflash_otp_get_current_region',0x14,[(0,'lrw','r3, 0x0'),(2,'ld.w','r3, (r3, 0xc)'),(4,'ld.w','r3, (r3, 0x14)'),(6,'ld.w','r3, (r3, 0x10)')],{'0x2':'runtime record pointer'}),
      ('sflash_otp_get_region_size',0x10,[(0,'lrw','r3, 0x0'),(2,'ld.w','r3, (r3, 0xc)'),(4,'ld.w','r3, (r3, 0x14)'),(6,'ld.w','r3, (r3, 0x8)')],{'0x2':'runtime record pointer'}),
      ('sflash_gettype',8,[(0,'lrw','r3, 0x0'),(2,'ld.w','r3, (r3, 0xc)'),(4,'ld.w','r0, (r3, 0x0)')],{'0x2':'runtime record pointer'}),
      ('gx_spinor_flash_gettype',8,[(0,'lrw','r3, 0x0'),(2,'ld.w','r3, (r3, 0xc)'),(4,'ld.w','r0, (r3, 0x0)')],{'0x2':'runtime record pointer'}))
    specifications += (
      ('sflash_otp_status',0x40,[(2,'lrw','r5, 0x0'),(6,'ld.w','r3, (r5, 0xc)'),(8,'ld.w','r3, (r3, 0x14)'),(0x10,'ld.w','r3, (r5, 0xc)'),(0x16,'ld.hs','r3, (r3, 0x6)')],{'0x6':'runtime record pointer','0x10':'runtime record pointer; r5 preserved by helper ABI'}),
      ('sflash_otp_lock',0x60,[(4,'lrw','r5, 0x0'),(6,'ld.w','r3, (r5, 0xc)'),(8,'ld.w','r3, (r3, 0x14)'),(0x10,'ld.w','r3, (r5, 0xc)'),(0x16,'ld.hs','r3, (r3, 0x6)')],{'0x6':'runtime record pointer','0x10':'runtime record pointer; r5 preserved by helper ABI'}),
      ('sflash_otp_erase',0x50,[(2,'lrw','r4, 0x0'),(4,'ld.w','r3, (r4, 0xc)'),(6,'ld.hs','r2, (r3, 0x6)')],{'0x4':'runtime record pointer'}))
    specifications += (
      ('sflash_write_protect_status',0x90,[(2,'lrw','r5, 0x0'),(8,'ld.w','r3, (r5, 0xc)'),(0xc,'ld.w','r3, (r3, 0x10)'),(0xe,'mov','r6, r5'),(0x1e,'ld.w','r3, (r5, 0xc)'),(0x20,'ld.h','r3, (r3, 0x6)'),(0x38,'ld.w','r3, (r6, 0xc)'),(0x3c,'ld.w','r18, (r3, 0x10)')],{'0x8':'runtime record pointer','0x1e':'runtime record pointer; preserved r5','0x38':'runtime record pointer; copied/preserved r6'}),
      ('sflash_wp_lock',0xc8,[(4,'lrw','r5, 0x0'),(0x10,'ld.w','r3, (r5, 0xc)'),(0x14,'ld.w','r2, (r3, 0x10)'),(0x3e,'ld.w','r3, (r5, 0xc)'),(0x42,'ld.w','r2, (r3, 0x10)')],{'0x10':'runtime record pointer','0x3e':'runtime record pointer; preserved r5'}))
    specifications += (
      ('sflash_otp_write',0xe0,[(4,'lrw','r8, 0x0'),(0xa,'ld.w','r12, (r8, 0xc)'),(0x10,'ld.w','r3, (r12, 0x14)')],{'0xa':'runtime record pointer'}),
      ('sflash_otp_read',0x154,[(6,'lrw','r10, 0x0'),(0xc,'ld.w','r12, (r10, 0xc)'),(0x12,'ld.w','r3, (r12, 0x14)')],{'0xc':'runtime record pointer'}),
      ('sflash_init',0x160,[(0x5c,'lrw','r5, 0x0'),(0x68,'ld.w','r3, (r5, 0xc)'),(0x6a,'ld.w','r4, (r3, 0x4)')],{'0x68':'runtime record pointer; preserved r5'}),
      ('xip_sflash_init',0xb8,[(0x50,'lrw','r4, 0x0'),(0x54,'ld.w','r3, (r4, 0xc)'),(0x56,'ld.w','r3, (r3, 0x4)'),(0x78,'ld.w','r3, (r4, 0xc)'),(0x7a,'ld.w','r2, (r3, 0x4)')],{'0x54':'runtime record pointer','0x78':'runtime record pointer; preserved r4'}))
    for name,pool,steps,classification in specifications:
        section=next(s for s in elf.sections if s['name']=='.text.'+name);code=decode(subprocess.check_output([pre,'-d','-j',section['name'],str(path)],text=True));relocation=next(r for r in elf.relocations(section['index']) if r['offset']==pool);symbol=elf.symbols()[relocation['symbol']]
        assert relocation['type']==1 and relocation['addend']==0 and elf.sections[symbol['section']]['name']=='.data' and symbol['value']==0
        for pc,op,args in steps:assert code[pc][:2]==(op,args),(name,pc,code[pc])
        rows.append({'symbol':name,'section_sha256':sha(elf.contents(section)),'pool_offset':pool,'relocation':relocation,'verified_steps':steps,'classified_reads':classification})
    return {'sdk_commit':SDK_COMMIT,'object_blob':blob,'object_sha256':sha(data),'paths':rows,'classified_reads':sum(len(r['classified_reads']) for r in rows),'source_admitted':False,'limits':['Selected candidate reads ruled out as device-record+12 consumers by local instruction/relocation paths. Not a whole-program or indirect access proof. Remaining fields and consumers unresolved.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-flash-record-field-paths.json').write_text(json.dumps(r,indent=2)+'\n');print(r['classified_reads'])
