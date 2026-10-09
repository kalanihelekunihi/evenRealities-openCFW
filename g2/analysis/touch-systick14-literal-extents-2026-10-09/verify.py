"""Read-only comparison of two preselected authentic-source object extents."""
from pathlib import Path
import hashlib, json
from elftools.elf.elffile import ELFFile
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_LITTLE_ENDIAN

R = Path(__file__).resolve().parents[3]
O = Path(__file__).resolve().parent
payload = R / 'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin'
obj = R / 'g2/analysis/touch-pdl14-system-interface-2026-10-09/outputs/cy_systick.c/public.o'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(payload) == '0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d'
rows = []
with obj.open('rb') as f:
    elf = ELFFile(f)
    for name, address, code_bytes in [('Cy_SysTick_Enable', 0xA620, 20), ('Cy_SysTick_SetClockSource', 0xA638, 18)]:
        section = elf.get_section_by_name('.text.' + name)
        assert section is not None
        index = next(i for i,s in enumerate(elf.iter_sections()) if s.name == section.name)
        relocations = [s.name for s in elf.iter_sections() if s['sh_type'] in ('SHT_REL','SHT_RELA') and s['sh_info'] == index]
        assert not relocations
        data = section.data()
        assert len(data) == 24
        offset = 32 + address - 0x3300
        stock = payload.read_bytes()[offset:offset+len(data)]
        assert stock == data
        instructions = [{'address':hex(i.address),'bytes':i.bytes.hex(),'mnemonic':i.mnemonic,'operands':i.op_str} for i in Cs(CS_ARCH_ARM, CS_MODE_THUMB|CS_MODE_LITTLE_ENDIAN).disasm(stock[:code_bytes],address)]
        refs = []
        for i in instructions:
            if i['mnemonic']=='ldr' and '[pc,' in i['operands']:
                immediate=int(i['operands'].split('#')[1].split(']')[0],0)
                target=((int(i['address'],16)+4)&~3)+immediate
                assert target==address+20
                refs.append({'instruction':i['address'],'literal':hex(target),'value':hex(int.from_bytes(stock[20:24],'little'))})
        assert refs
        rows.append({'function':name,'runtime_extent':[hex(address),hex(address+24)],'absolute_payload_offset':offset,'historical_code_bytes':code_bytes,'alignment_bytes':stock[code_bytes:20].hex(),'literal_bytes':stock[20:24].hex(),'literal_references':refs,'instructions':instructions,'sha256':hashlib.sha256(stock).hexdigest(),'matches':True})
result={'status':'PASS','payload_sha256':sha(payload),'object_sha256':sha(obj),'functions':rows,'new_candidate_functions':2,'new_candidate_bytes':48,'independent_review':'pending','denominator':54,'prior_reviewed_functions':23,'limits':'Existing unchanged authentic public-source object; static bytes and literal references only. No timer execution, time units, interrupt delivery or unique producing BSP/toolchain established.'}
(O/'results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
