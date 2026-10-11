from pathlib import Path
from io import BytesIO
import hashlib, json, subprocess
from elftools.elf.elffile import ELFFile

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
archive=ROOT/'g2/components/touch/source_candidate_20261010/build/touch-source-candidate.a'
firmware=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes()
assert hashlib.sha256(firmware).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d'
payload=firmware[32:];stock=payload[0xb58c-0x3300:0xb950-0x3300]
members=subprocess.check_output(['arm-none-eabi-ar','t',str(archive)],text=True).splitlines()
rows=[]
for member in members:
    elf=ELFFile(BytesIO(subprocess.check_output(['arm-none-eabi-ar','p',str(archive),member])))
    syms=elf.get_section_by_name('.symtab')
    for idx,section in enumerate(elf.iter_sections()):
        if not section.name.startswith(('.data','.rodata')) or not section.data_size:continue
        data=section.data()
        full=[];start=0
        while (at:=stock.find(data,start))>=0:
            full.append(hex(0xb58c+at));start=at+1
        informative=[]
        for off in range(max(0,len(data)-7)):
            window=data[off:off+8]
            if sum(byte!=0 for byte in window)<3:continue
            at=stock.find(window)
            if at>=0:informative.append({'object_offset':off,'flash':hex(0xb58c+at)})
        symbols=[{'name':sym.name,'offset':sym['st_value'],'size':sym['st_size']}
                 for sym in syms.iter_symbols() if sym['st_shndx']==idx and sym.name]
        relocations=[]
        for rel in elf.iter_sections():
            if rel['sh_type'] not in ('SHT_REL','SHT_RELA') or rel['sh_info']!=idx:continue
            target=elf.get_section(rel['sh_link'])
            for entry in rel.iter_relocations():
                relocations.append({'offset':entry['r_offset'],'symbol':target.get_symbol(entry['r_info_sym']).name})
        rows.append({'member':member,'section':section.name,'size':len(data),'nonzero_bytes':sum(x!=0 for x in data),
                     'symbols':symbols,'relocations':relocations,'full_stock_matches':full,
                     'informative_8byte_matches':informative[:8],
                     'informative_match_count':len(informative)})
receipt={'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
         'data_rodata_sections':len(rows),'sections_with_relocations':sum(bool(r['relocations']) for r in rows),
         'full_nonzero_matches':[{'member':r['member'],'section':r['section'],'stock':r['full_stock_matches']}
                                 for r in rows if r['full_stock_matches'] and r['nonzero_bytes']>=3],
         'informative_sections':[{'member':r['member'],'section':r['section'],'matches':r['informative_match_count']}
                                 for r in rows if r['informative_match_count']]}
(HERE/'archive_init_section_scan.json').write_text(json.dumps({'receipt':receipt,'sections':rows},indent=2)+'\n')
print(json.dumps(receipt))
