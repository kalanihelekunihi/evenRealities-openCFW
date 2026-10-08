from pathlib import Path
exec(Path(__file__).with_name('verify.py').read_text().split('# Independent expected registration model')[0].replace('UC_CPU_ARM_CORTEX_M4','UC_CPU_ARM_CORTEX_M33'))
from itcm_record import decode_itcm
itcm=decode_itcm(raw)
def initialized():
 u=machine();u.mem_map(0,0x1000);u.mem_write(0x40,itcm);u.mem_map(0xe000e000,0x2000);w(u,0xe000ed88,0xf00000);return u
# Execute the actual decoder for the ITCM record, independently checking its output.
u=machine();u.mem_map(0,0x1000);u.mem_write(0,b'\xa5'*0x100);u.reg_write(UC_ARM_REG_R0,0x75d3e4);u.emu_start(0x43a11f,0x2007f000,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000 and u.reg_read(UC_ARM_REG_R0)==0x75d3f0;assert bytes(u.mem_read(0x40,24))==itcm and bytes(u.mem_read(0,64))==b'\xa5'*64 and bytes(u.mem_read(0x58,16))==b'\xa5'*16
record=dict(status='PASS',record='0x75d3e4',compressed_source='0x79430e',compressed_bytes=22,destination='0x40',decoded_bytes=24,decoded_sha256=hashlib.sha256(itcm).hexdigest(),next_record='0x75d3f0',method='Actual0x43A11E decoder versus independent Python token decoder and guards.')
delay=[]
for count in [1,2,17,59,100,1000]:
 vals=[]
 for entry in [0x40,sym['audio_itcm_delay_iterations']]:
  u=initialized();trace=[]
  def hook(u,a,n,d):
   if a==0x40:trace.append(u.reg_read(UC_ARM_REG_R0))
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_R0,count);u.emu_start(entry|1,0x2007f000,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000 and u.reg_read(UC_ARM_REG_R0)==0
  if entry==0x40:assert trace==list(range(count,0,-1))
  vals.append(u.reg_read(UC_ARM_REG_R0))
 assert vals[0]==vals[1];delay.append(dict(iterations=count,returned_counter=0))
copies=[]
for count,salt in itertools.product([1,2,5,20],[0,0xa5a5a5a5]):
 values=[(salt+i)&0xffffffff for i in range(count)];vals=[]
 for entry in [0x48,sym['audio_itcm_read_words']]:
  u=initialized();u.mem_write(0x20005000,struct.pack('<'+'I'*count,*values));u.mem_write(0x20006000,b'\xa5'*128);writes=[]
  def write(u,access,a,n,v,d):writes.append([a-0x20006000,n,v])
  u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0x20006000,end=0x2000607f);u.reg_write(UC_ARM_REG_R0,0x20005000);u.reg_write(UC_ARM_REG_R1,0x20006000);u.reg_write(UC_ARM_REG_R2,count);u.emu_start(entry|1,0x2007f000,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000;assert u.reg_read(UC_ARM_REG_R0)==0x20005000+4*count;assert writes==[[i*4,4,v] for i,v in enumerate(values)];assert bytes(u.mem_read(0x20006000,128))==struct.pack('<'+'I'*count,*values)+b'\xa5'*(128-4*count);vals.append(writes)
 assert vals[0]==vals[1];copies.append(dict(words=count,salt=hex(salt),writes=vals[0]))
full_delay=[]
for us,clock in itertools.product([0,1,2,5,100],[0,1,2,3]):
 vals=[]
 for entry in [0x4807a0,sym['audio_delay_us_selected']]:
  u=initialized();w(u,0x40021000,clock<<3);trace=[]
  def hook(u,a,n,d):
   if a==0x40:trace.append(u.reg_read(UC_ARM_REG_R0))
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_R0,us);u.emu_start(entry|1,0x2007f000,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000;assert word(u,0x40021000)==clock<<3;vals.append(trace)
 assert vals[0]==vals[1];iterations=(int(us*32*250/96)-24 if clock==2 else us*32-15) if us else 0;assert vals[0]==list(range(max(iterations,0),0,-1));full_delay.append(dict(requested_us=us,clock_selector=clock,iterations=len(vals[0]),first_counter=vals[0][0] if vals[0] else None,status='returned'))
initializes=[];power_words=[0x11000000+i for i in range(20)];ton_words=[0x22000000+i for i in range(5)];mem_word=0x33445566
for cfg,power in itertools.product([0,8,16,24],[0,1<<27]):
 vals=[]
 for entry in [0x5a4d48,sym['audio_platform_newer_initialize']]:
  u=initialized();u.mem_map(0x40008000,0x1000);u.mem_map(0x42000000,0x10000);w(u,0x400201bc,cfg);w(u,0x40021008,power);u.mem_write(0x2005665c,b'\xa5'*108)
  for base in [0x42003370,0x42006970]:u.mem_write(base,struct.pack('<20I',*power_words));u.mem_write(base+(0x270-0x25c)*4,struct.pack('<5I',*ton_words));w(u,base+(0x278-0x25c)*4,mem_word)
  boundary=[];copies_trace=[]
  def hook(u,a,n,d):
   if a==0x48086a:copies_trace.append(dict(source=hex(u.reg_read(UC_ARM_REG_R0)),words=u.reg_read(UC_ARM_REG_R2)))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start(entry|1,0x2007f000,count=100000)
  after=bytes(u.mem_read(0x2005665c,108))
  if cfg&8 and not power:assert not boundary and u.reg_read(UC_ARM_REG_PC)==0x2007f000 and u.reg_read(UC_ARM_REG_R0)==7 and after==b'\xa5'*108
  else:assert not boundary and u.reg_read(UC_ARM_REG_PC)==0x2007f000 and u.reg_read(UC_ARM_REG_R0)==0 and after==struct.pack('<27I',0x1f01600d,*power_words,*ton_words,mem_word) and len(copies_trace)==3 and word(u,0x400083e0)==0x110 and word(u,0x400083e8)==0xffffffff and word(u,0x40008060)==0x40000000
  vals.append(dict(boundary=boundary,return_value=u.reg_read(UC_ARM_REG_R0),calibration_after=after.hex(),copies=copies_trace))
 assert vals[0]==vals[1];initializes.append(dict(config=hex(cfg),otp_power=hex(power),**vals[0]))
revisions=[]
for cfg,power,null,value in itertools.product([0,8],[0,1<<27],[0,1],[0,1,2,3]):
 vals=[]
 for entry in [0x47ef38,sym['audio_platform_get_revision']]:
  u=initialized();u.mem_map(0x42000000,0x10000);w(u,0x400201bc,cfg);w(u,0x40021008,power);w(u,0x200001e8,0xffffffff);w(u,0x20006000,0xa5a5a5a5);w(u,0x42003310,value);w(u,0x42006910,value);u.reg_write(UC_ARM_REG_R0,0 if null else 0x20006000);u.emu_start(entry|1,0x2007f000,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000;actual_value=0 if cfg&8 and not power else value;assert word(u,0x200001e8)==actual_value and word(u,0x20006000)==(0xa5a5a5a5 if null else actual_value) and u.reg_read(UC_ARM_REG_R0)==(6 if null else 0);vals.append(dict(cached=actual_value,returned=u.reg_read(UC_ARM_REG_R0),destination=hex(word(u,0x20006000))))
 assert vals[0]==vals[1];revisions.append(dict(config=hex(cfg),otp_power=hex(power),null_destination=null,synthetic_trim_word=value,**vals[0]))
# Original-only bounded prefix: count0 is not a safe no-op in this do/while helper.
u=initialized();u.mem_write(0x20005000,struct.pack('<4I',1,2,3,4));u.mem_write(0x20006000,b'\xa5'*32);counts=[]
def zero_hook(u,a,n,d):
 if a==0x48:
  counts.append(u.reg_read(UC_ARM_REG_R2))
  if len(counts)==4:u.emu_stop()
u.hook_add(UC_HOOK_CODE,zero_hook);u.reg_write(UC_ARM_REG_R0,0x20005000);u.reg_write(UC_ARM_REG_R1,0x20006000);u.reg_write(UC_ARM_REG_R2,0);u.emu_start(0x49,0x2007f000,count=10000);assert counts==[0,0xffffffff,0xfffffffe,0xfffffffd] and bytes(u.mem_read(0x20006000,12))==struct.pack('<3I',1,2,3)
zero=dict(status='ORIGINAL_ONLY_BOUNDED_PREFIX',initial_words=0,counters=[hex(x) for x in counts],words_copied_before_stop=3,limit='Stopped before fourth iteration; no complete execution or live defect claim.')
(D/'itcm-results.json').write_text(json.dumps(dict(status='PASS',cases=len(delay)+len(copies)+len(full_delay)+len(initializes)+len(revisions),record_comparisons=1,record=record,delay_helper=delay,copy_helper=copies,full_delay=full_delay,initialize_with_synthetic_info1=initializes,revision_with_synthetic_info1=revisions,zero_count_original_only=zero,elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['0x40/0x48 are authenticated OTA-initialized ITCM, not missing ROM.','Positive helper counts; zero-count original prefix demonstrates wrap, not a live failure.','Delay input is intended microseconds per corroborated public implementation; no physical timing or cycle-equivalent C claim.','Synthetic INFO1/OTP memory supplies data, not fake call returns. Complete selected initializer and timer-register writes; real calibration, physical timer effects and full boot not established.','M33-compatible selected M55 integer/FPU instruction subset; no exception return.']),indent=2)+'\n');print('PASS',len(delay)+len(copies)+len(full_delay)+len(initializes)+len(revisions),'ITCM/provider comparisons +1 record +1 original-only zero prefix')
