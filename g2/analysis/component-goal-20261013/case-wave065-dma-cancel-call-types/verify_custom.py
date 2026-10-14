#!/usr/bin/env python3
"""Prove source custom bounds, unchanged load, protected-data and failure guards."""
from pathlib import Path
from elftools.elf.elffile import ELFFile
import json,hashlib,struct,subprocess,tempfile
R=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;O=H/'build';P=H.parent/'case-wave065-dma-cancel-call-types';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 with p.open('rb') as f:
  e=ELFFile(f);return e.header['e_entry'],{s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()},[(s['p_vaddr'],s['p_paddr'],s['p_flags'],s.data(),s['p_memsz']) for s in e.iter_segments() if s['p_type']=='PT_LOAD'],[(s.name,s['sh_size']) for s in e.iter_sections() if s['sh_flags']&2]
entry,sym,loads,sections=read(O/'case.elf');oldentry,oldsyms,oldloads,_=read(P/'final/case.elf');assert entry==oldentry==0x08000145;assert len(loads)==len(oldloads)==1;assert loads[0][:3]==oldloads[0][:3];assert loads[0][3][:len(oldloads[0][3])]==oldloads[0][3];assert loads[0][3][len(oldloads[0][3]):]==bytes([255])*2;assert all(sym[x]==oldsyms[x] for x in oldsyms if x in sym and x.startswith('case_'))
for virtual,physical,flags,data,size in loads:
 assert virtual==physical and 0x08000000<=virtual<0x0803f000 and virtual+size<=0x0803f000;assert flags==5
raw=(O/'case-custom.bin').read_bytes();assert len(raw)==63200 and len(raw)%8==0;assert raw==loads[0][3];assert struct.unpack_from('<II',raw)==(0x20002c88,0x08000145);assert sym['__case_flash_load_end']==0x08000000+len(raw);assert sym['__case_preserved_page_start']==0x0803f000;assert all(n not in ['.data','.bss'] or size==0 for n,size in sections)
base=json.loads((O/'receipt.json').read_text())['link_command'];tests=[]
with tempfile.TemporaryDirectory(prefix='case-contract-',dir='/tmp') as t:
 t=Path(t)
 # The actual current source image must fail when the permitted flash
 # region becomes smaller than it; no synthetic opcode/filler object.
 ld=t/'small.ld';ld.write_text((H/'layout.ld').read_text().replace('LENGTH = 0x3f000','LENGTH = 0xf000'));cmd=base.copy();cmd[cmd.index('-T')+1]=str(ld);cmd[-1]=str(t/'small.elf');p=subprocess.run(cmd,capture_output=True,text=True);assert p.returncode!=0 and ('overflowed' in p.stderr or 'not within region' in p.stderr),(p.returncode,p.stderr);tests.append({'test':'actual_image_flash_budget','result':'EXPECTED_REJECTION','diagnostic':p.stderr})
 # Source-only mutable-data test: a new object must not silently acquire
 # a RAM address without native binding/initialization admission.
 c=t/'mutable.c';c.write_text('volatile unsigned case_unqualified_test_variable;\n');obj=t/'mutable.o';subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-ffreestanding','-c',str(c),'-o',str(obj)],check=True)
 cmd=base.copy();cmd.insert(1,'-ucase_unqualified_test_variable');cmd[-2:-2]=[str(obj)];cmd[-1]=str(t/'mutable.elf');p=subprocess.run(cmd,capture_output=True,text=True);assert p.returncode!=0 and 'Unqualified allocated mutable.bss' in p.stderr;tests.append({'test':'unqualified_mutable_object','result':'EXPECTED_REJECTION','diagnostic':p.stderr})
 # A contradictory protected-page boundary must also fail explicitly.
 ld=t/'protected.ld';ld.write_text((H/'layout.ld').read_text().replace('__case_preserved_page_start = 0x0803f000','__case_preserved_page_start = 0x0800f000'));cmd=base.copy();cmd[cmd.index('-T')+1]=str(ld);cmd[-1]=str(t/'protected.elf');p=subprocess.run(cmd,capture_output=True,text=True);assert p.returncode!=0 and 'Factory pages overlap' in p.stderr;tests.append({'test':'protected_page_overlap','result':'EXPECTED_REJECTION','diagnostic':p.stderr})
r={'status':'PASS_SOURCE_CUSTOM_MEMORY_CONTRACT','ELF_sha256':sha(O/'case.elf'),'raw_binary_sha256':sha(O/'case-custom.bin'),'raw_binary_bytes':len(raw),'source_code_data_and_addresses_identical_to_qualified_wave065':True,'additional_erased_flash_tail_bytes':2,'inherited_qualification_ELF_sha256':sha(P/'final/case.elf'),'entry':hex(entry),'initial_SP':'0x20002c88','flash_limit':'0x0803f000','first_reserved_page':'0x0803f000','flash_headroom_bytes':0x3f000-len(raw),'LOAD_flags':'RX','unknown_mutable_sections':'rejected','negative_tests':tests,'limits':['Linker confirms emittedsection boundaries, not every absoluteRAM/MMIO reference or complete computed-root/ambient-stack/provider behavior.','Factory-page exclusion in the image does not validate OTA erase/program preservation, bank-swap or flash hardware.','Rawdiagnostic image only; noEVEN envelope, flashing authorization or accepted replacement claim.']};(H/'custom-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['flash_headroom_bytes'])
