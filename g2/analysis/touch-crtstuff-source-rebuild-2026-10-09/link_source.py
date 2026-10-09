from pathlib import Path
import json,hashlib,subprocess
from elftools.elf.elffile import ELFFile
O=Path(__file__).resolve().parent;R=O.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();m=json.loads((R/'g2/analysis/touch-compiler14-successor-2026-10-09/acquisition.json').read_text())[0];T=(R/'g2/analysis/touch-compiler14-successor-2026-10-09'/m['gcc']).parents[1];prev=R/'g2/analysis/touch-crt-array-binding-2026-10-09';out=O/'outputs'
def relocations(e,name):
 s=e.get_section_by_name('.rel'+name);rows=[]
 if s:
  for v in s.iter_relocations():
   sym=e.get_section(s['sh_link']).get_symbol(v['r_info_sym']);section=sym['st_shndx'];rows.append({'offset':v['r_offset'],'type':v['r_info_type'],'symbol':sym.name,'symbol_value':sym['st_value'],'symbol_section':e.get_section(section).name if isinstance(section,int) else section})
 return rows
installed=T/'lib/gcc/arm-none-eabi/14.2.1/thumb/v6-m/nofp/crtbegin.o';checks=[]
with installed.open('rb') as f,(out/'crtbegin.o').open('rb') as g:
 a=ELFFile(f);e=ELFFile(g)
 for s in a.iter_sections():
  if s.name.startswith('.text.') or s.name in ['.init_array','.fini_array']:
   x=relocations(a,s.name);y=relocations(e,s.name);checks.append({'section':s.name,'relocations_identical':x==y,'source_relocations':y})
argv=['docker','run','--rm','--platform','linux/amd64','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','-v',f'{T}:/tool:ro','-v',f'{prev}/outputs:/bindings:ro','-v',f'{out}:/out','ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55','/tool/bin/arm-none-eabi-ld','-T','/bindings/bindings.ld','/out/crtbegin.o','-o','/out/linked-source.elf'];p=subprocess.run(argv,capture_output=True,text=True)
result={'argv':argv,'exit_code':p.returncode,'diagnostics':p.stdout+p.stderr,'relocation_checks':checks,'inputs':{str(x.relative_to(R)):sha(x) for x in [installed,out/'crtbegin.o',prev/'outputs/bindings.ld']},'independent_review':'pending','runtime_source_subtotal_before_review':922,'source_upgrade_pending_bytes':152,'array_data_bytes_separate':8,'limits':'Focused genuine source-produced provider bytes, not complete compiler/vendor object/debug build reproduction or campaign admission. Prior32instruction cases reused only if source-linked sections equal audited provider-linked sections.'}
if not p.returncode:
 fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';assert sha(fw)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';b=fw.read_bytes()[32:];rows=[]
 with (out/'linked-source.elf').open('rb') as f,(prev/'outputs/linked.elf').open('rb') as g:
  e=ELFFile(f);a=ELFFile(g)
  for s in e.iter_sections():
   if s.name.startswith('.text.') or s.name in ['.init_array','.fini_array']:
    d=s.data();address=s['sh_addr'];flash=address if address<0x20000000 else 0xb58c+(address-0x200004c0);stock=b[flash-0x3300:flash-0x3300+len(d)];provider=a.get_section_by_name(s.name);rows.append({'section':s.name,'address':hex(address),'image_flash':hex(flash),'bytes':len(d),'exact_stock':d==stock,'exact_audited_provider':provider['sh_addr']==address and provider.data()==d,'sha256':hashlib.sha256(d).hexdigest()})
 result.update(sections=rows,all_stock_and_provider_equal=all(x['exact_stock'] and x['exact_audited_provider'] for x in rows),linked_source_elf_sha256=sha(out/'linked-source.elf'),reused_original_cases=32,reused_original_receipt_sha256=sha(prev/'original-results.json'))
(O/'linked-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'relocations_identical':all(x['relocations_identical'] for x in checks),'all_stock_and_provider_equal':result.get('all_stock_and_provider_equal'),'sections':result.get('sections')},indent=2))
