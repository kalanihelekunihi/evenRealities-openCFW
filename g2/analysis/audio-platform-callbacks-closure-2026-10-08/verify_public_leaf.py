from pathlib import Path
exec(Path(__file__).with_name('verify.py').read_text().split('# Independent expected registration model')[0].replace('UC_CPU_ARM_CORTEX_M4','UC_CPU_ARM_CORTEX_M33'))
receipts=json.loads((D/'public-leaf-receipt.json').read_text());rows=[]
for build in receipts['builds']:
 p=Path(build['elf']);assert hashlib.sha256(p.read_bytes()).hexdigest()==build['elf_sha256'];seg=[]
 with p.open('rb') as f:
  e=ELFFile(f);symbols={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
  for s in e.iter_segments():
   if s['p_type']=='PT_LOAD':seg.append((s['p_vaddr'],s.data()))
 short=build['mode']!='wide';float_rows=[];selector=[]
 def new():
  u=machine();u.mem_map(0x110000,0x10000);u.mem_map(0xe000e000,0x2000);w(u,0xe000ed88,0xf00000)
  for a,b in seg:u.mem_write(a,b)
  return u
 for row in json.loads((D/'classify-results.json').read_text())['comparisons']:
  bit=int(row['float_bits'],16);vals=[]
  for entry in [0x5a1e8c,symbols['spotmgr_temp_to_range']]:
   u=new();u.reg_write(UC_ARM_REG_S0,bit);u.emu_start(entry|1,0x2007f000,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000;vals.append(u.reg_read(UC_ARM_REG_R0))
  assert vals[0]==vals[1]==row['classification'];float_rows.append(dict(float_bits=hex(bit),classification=vals[0]))
 for next_,old in itertools.product(range(20),range(20)):
  vals=[]
  for entry in [0x5a4334,symbols['spotmgr_state_transition_sequence_determine']]:
   u=new();u.mem_write(0x20006000,b'\xa5'*12);u.reg_write(UC_ARM_REG_R0,next_);u.reg_write(UC_ARM_REG_R1,old);u.reg_write(UC_ARM_REG_R2,0x20006004);u.emu_start(entry|1,0x2007f000,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000;vals.append(dict(return_value=u.reg_read(UC_ARM_REG_R0),index=u.mem_read(0x20006004,1)[0],output_region=bytes(u.mem_read(0x20006000,12)).hex()))
  assert vals[0]['return_value']==vals[1]['return_value'] and vals[0]['index']==vals[1]['index']
  if short:assert vals[0]==vals[1]
  else:
   index=vals[0]['index'];assert vals[0]['output_region']==(b'\xa5'*4+bytes([index])+b'\xa5'*7).hex();assert vals[1]['output_region']==(b'\xa5'*4+struct.pack('<I',index)+b'\xa5'*4).hex(),(next_,old,vals)
  selector.append(dict(next=next_,old=old,stock=vals[0],public=vals[1]))
 rows.append(dict(mode=build['mode'],short_enums=short,numeric_agreement_cases=len(float_rows)+len(selector),selector_output_footprint_mismatches=0 if short else len(selector),float_comparisons=float_rows,selector_comparisons=selector,elf_sha256=build['elf_sha256']))
(D/'public-leaf-results.json').write_text(json.dumps(dict(status='PASS',compatible_input_cases=441,compatible_builds=2,wide_numeric_only_cases=441,build_comparisons=rows,limits=['Public selected leaves agree, not a whole HAL or byte-identical source claim.','Forced wide-enum selector writes4 bytes; stock, explicit short-enum and this toolchain default write1.','The flag experiment establishes a compatible ABI for selected leaves, not the exact historical compiler option.','Other public module behavior has drift; do not substitute without instruction-level checks.']),indent=2)+'\n');print('PASS441 compatible public leaf cases; wide441 numeric agreements with400 selector footprint mismatches')
