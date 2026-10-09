from pathlib import Path
import json,hashlib
from elftools.elf.elffile import ELFFile
O=Path(__file__).resolve().parent;R=O.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prior=R/'g2/analysis/touch-pdl14-finite-census-2026-10-09';sel=json.loads((prior/'selection.json').read_text());fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';b=fw.read_bytes()[32:]
names='Cy_Flash_ClockBackup Cy_Flash_ClockConfig Cy_Flash_ClockRestore Cy_Flash_WriteRow Cy_SysClk_IloStartMeasurement Cy_SysClk_IloStopMeasurement Cy_SysClk_IloCompensate Cy_SysPm_ExecuteCallback'.split();rows=[]
for t in sel['functions']:
 if t['function'] not in names:continue
 obj=prior/'outputs'/t['source_unit']/'public.o';source=R/'g2/analysis/touch-compiler14-successor-2026-10-09/tools/pdl-input/drivers/source'/t['source_unit']
 with obj.open('rb') as f:
  e=ELFFile(f);s=e.get_section_by_name('.text.'+t['function']);d=s.data();mask=set();relocs=[];q=e.get_section_by_name('.rel'+s.name)
  if q:
   for v in q.iter_relocations():
    mask.update(range(v['r_offset'],v['r_offset']+4));symbol=e.get_section(q['sh_link']).get_symbol(v['r_info_sym']);relocs.append({'offset':v['r_offset'],'type':v['r_info_type'],'symbol':symbol.name,'source_symbol_section':e.get_section(symbol['st_shndx']).name if isinstance(symbol['st_shndx'],int) else symbol['st_shndx']})
  offset=t['address']-0x3300;stock=b[offset:offset+len(d)];diff=[{'offset':i,'object_byte':d[i],'stock_byte':stock[i]} for i in range(len(d)) if i not in mask and d[i]!=stock[i]]
  rows.append({'function':t['function'],'runtime_address':hex(t['address']),'historical_code_bytes':t['historical_code_bytes'],'compiled_section_bytes':len(d),'object_bytes':d.hex(),'stock_window_bytes':stock.hex(),'relocations':relocs,'non_relocated_differences':diff,'object_sha256':sha(obj),'source_sha256':sha(source),'stock_window_is_not_verified_function_extent':True})
result={'scope':'Eight remaining selected entries against current pinned source and fixed comparator flags; not whole-project exhaustion','payload_sha256':sha(fw),'entries':rows,'unresolved_count':8,'source_or_lowering_mismatch':True,'limits':'No relocation byte patched or source/build flags changed. A compiled-length stock window is comparison evidence, not function-extent proof.'}
(O/'results.json').write_text(json.dumps(result,indent=2)+'\n');print([(x['function'],len(x['non_relocated_differences'])) for x in rows])
