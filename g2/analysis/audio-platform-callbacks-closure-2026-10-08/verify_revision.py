from pathlib import Path
exec(Path(__file__).with_name('verify.py').read_text().split('# Independent expected registration model')[0])
rows=[]
for cached,null,cfg,power in itertools.product([0,1,2,3,0xffffffff],[0,1],[0,8],[0,1<<27]):
 vals=[]
 for entry in [0x47ef38,sym['audio_platform_get_revision']]:
  u=machine();w(u,0x200001e8,cached);w(u,0x20006000,0xa5a5a5a5);w(u,0x400201bc,cfg);w(u,0x40021008,power);boundary=[]
  def invalid(u,access,address,size,value,d):
   assert access==UC_MEM_FETCH_UNMAPPED and address==0x48;boundary.append(dict(address='0x48',source=hex(u.reg_read(UC_ARM_REG_R0)),destination=hex(u.reg_read(UC_ARM_REG_R1)),word_count=u.reg_read(UC_ARM_REG_R2)));return False
  u.hook_add(UC_HOOK_MEM_INVALID,invalid);u.reg_write(UC_ARM_REG_R0,0 if null else 0x20006000)
  try:u.emu_start(entry|1,0x2007f000,count=100000)
  except UcError as error:assert error.errno==UC_ERR_FETCH_UNMAPPED and boundary
  assert boundary or u.reg_read(UC_ARM_REG_PC)==0x2007f000
  after=word(u,0x200001e8);dst=word(u,0x20006000);rv=None if boundary else u.reg_read(UC_ARM_REG_R0)
  if cached!=0xffffffff:assert after==cached and not boundary and rv==(6 if null else 0) and dst==(0xa5a5a5a5 if null else cached)
  elif cfg&8 and not power:assert after==0 and not boundary and rv==(6 if null else 0) and dst==(0xa5a5a5a5 if null else 0)
  else:assert boundary==[dict(address='0x48',source='0x42006910' if cfg&8 else '0x42003310',destination='0x200001e8',word_count=1)] and after==cached and dst==0xa5a5a5a5
  vals.append(dict(return_value=rv,boundary=boundary,cached_after=hex(after),destination_after=hex(dst)))
 assert vals[0]==vals[1];rows.append(dict(initial_cached=hex(cached),null_destination=null,config=hex(cfg),power=hex(power),**vals[0]))
(D/'revision-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Cached and read-error branches complete; successful reads stop at actual uninitialized ITCM0x48 in this negative fixture.','No actual revision value, live reachability, external word contents or ROM return fabricated.','Read can precede checking caller destination NULL.']),indent=2)+'\n');print('PASS',len(rows),'revision getter comparisons')
