from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-nema-buffer-cache-round208';S=D/'candidate.c';P=0x20001000;W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as t:
 selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text()
 if '--selected' in sys.argv:
  a=selected.index('/* Native5140ea..51411a:');S=Path(t)/'selected.c';S.write_text((D/'candidate.c').read_text().split('/* Native5140ea')[0]+selected[a:])
 selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('void *audio_uart_nema_pool_select_514050(uint32_t pool_id) {');z=selected.index('/* Native5140c6',a);pool=Path(t)/'pool.c';pool.write_text('#include <stdint.h>\n'+selected[a:z]);e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_nema_buffer_flush_5140ea','-Wl,--defsym=audio_uart_cache_clean_range_47510e=0x101011','-Wl,--defsym=audio_ble_privacy_cache_maintenance=0x101021',str(S),str(pool),'-o',str(e)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,which,id,flag,size,address,base,length,seed):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(P,bytes([seed])*64);u.mem_write(P,W(size)+W(id)+W(0x20002000)+W(address));p=0x20000370 if id==2 else 0x20000338 if id==3 else 0x20000354;u.mem_write(p,bytes([seed])*28);u.mem_write(p+16,W(length)+W(base));u.mem_write(p+24,bytes([flag]));events=[];trace=[];barriers=[]
  def hook(uc,a,n,user):
   code=bytes(uc.mem_read(a,n))
   if code==bytes.fromhex('bff34f8f'):barriers.append('DSB')
   if a not in ([0x101010,0x101020] if isc else [0x47510e,0x475014]):return
   r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);kind=0 if a==(0x101010 if isc else 0x47510e) else 1;events.append((kind,bytes(uc.mem_read(r0,8)).hex(),r1 if kind else None));uc.reg_write(UC_ARM_REG_R0,0xa5a5a5a5);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def mem(uc,access,a,n,v,user):
   if P<=a<P+64 or p<=a<p+28:trace.append((access,a,n,v if access==17 else bytes(uc.mem_read(a,n)).hex()))
  names=['audio_uart_nema_buffer_flush_5140ea','audio_uart_nema_buffer_invalidate_51411a','audio_uart_nema_pool_contains_514148'];entries=[0x5140ea,0x51411a,0x514148];u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,id if which==2 else P);u.reg_write(UC_ARM_REG_R1,address);u.reg_write(UC_ARM_REG_R2,size);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym[names[which]] if isc else entries[which])|1,0x600000,count=1000);assert u.reg_read(UC_ARM_REG_PC)==0x600000;return events,trace,barriers,u.reg_read(UC_ARM_REG_R0) if which==2 else None,u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(P,64)),bytes(u.mem_read(p,28))
 cases=[]
 for which,id,flag,size,address,seed in itertools.product([0,1],[0,2,3,0xffffffff],[0,1,255],[0,1,32,0xffffffff],[0,0xffffffff],[0,165]):cases.append((which,id,flag,size,address,0,0,seed))
 for id,address,size,base,length in itertools.product([0,2,3,0xffffffff],[0,1,0x40001000,0xfffffff0,0xffffffff],[0,1,32,0xffffffff],[0,0x1000,0xfffffff0],[0,16,0xffffffff]):cases.append((2,id,0,size,address,base,length,165))
 for c in cases:
  a=run(False,*c);b=run(True,*c)
  if a!=b:
   (D/'mismatch.json').write_text(json.dumps({'case':c,'native':a[:-2],'source':b[:-2]},indent=2)+'\n');raise AssertionError(c)
 receipt={'status':'PASS_NATIVE_BUFFER_CACHE_RANGE_WITH_REAL_POOL_SELECTOR','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'pool_selector_sha256':hashlib.sha256(pool.read_bytes()).hexdigest(),'child_cuts':2,'limits':['Conditional maintenance/range field order, explicit DSB opcode observed in flush only, pool IDs/flags/wrapped unsigned interval boundaries/ordered accesses/full92bytes/result/SP compared.','Actual cache children/hardware DSB effects/invalid pointers/pool data ownership remain open.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
