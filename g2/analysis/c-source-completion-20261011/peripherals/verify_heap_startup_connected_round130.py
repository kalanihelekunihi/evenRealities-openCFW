from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-memory-config-connected-round130';D.mkdir(exist_ok=True);paths=['file_pool_allocate_candidate/pool_allocate.c','tlsf_adjust_request_candidate/adjust.c','tlsf_locate_free_candidate/locate.c','file_pool_free_candidate/tlsf_mapping.c','file_pool_free_candidate/tlsf_absorb_leaves.c','file_pool_free_candidate/tlsf_free_lists.c','tlsf_prepare_allocation_candidate/prepare.c','tlsf_split_block_candidate/split.c','file_pool_free_candidate/tlsf_block_next.c','file_pool_free_candidate/tlsf_mark_free.c','file_pool_free_candidate/tlsf_lists.c','file_pool_free_candidate/tlsf_align.c','file_pool_free_candidate/tlsf_leaf.c'];S=[R/'components/audio'/p for p in paths]+[R/'components/audio/uart_thread_source_candidate'/p for p in ['display_font_alloc.c','tlsf_reallocate.c']];blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';W=lambda *v:struct.pack('<'+'I'*len(v),*v);ram=[0x200007bc,0x200007d4,0x20000630,0x20000c20];barriers={bytes.fromhex('bff35f8f'):'dmb',bytes.fromhex('bff34f8f'):'dsb',bytes.fromhex('bff36f8f'):'isb'}
with tempfile.TemporaryDirectory() as t:
 t=Path(t);shim=t/'shim.c';shim.write_text('void audio_uart_checksum_copy(void*a,const void*b,unsigned c){} void audio_ble_privacy_cache_maintenance(const void*a,unsigned char b){} void g2_file_close_error(const char*a,const char*b,unsigned c){} void audio_ble_hci_boot_log_4733ee(const char*p,...){} void g2_file_heap_error_log(const char*p){} void *audio_uart_mutex_dynamic_create(unsigned a){return 0;}');e=t/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_heap_initialize_4842e6',*[str(p) for p in S],str(shim),'-o',str(e)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(e)],text=True).splitlines() if len(v:=line.split())==3}
 with e.open('rb') as f:segs=[(p['p_vaddr'],p.data()) for p in ELFFile(f).iter_segments() if p['p_type']=='PT_LOAD']
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x400000);u.mem_map(0xe000e000,4096)
  for a,b in segs:u.mem_write(a,b)
  cuts={(syms[s] if isc else a)&~1:op for op,s,a in [('mutex','audio_uart_mutex_dynamic_create',0x4416d6),('log','audio_ble_hci_boot_log_4733ee',0x4733ee),('heaplog','g2_file_heap_error_log',0x4733ee),('error','g2_file_close_error',0x4d09b4),('copy','audio_uart_checksum_copy',0x439c04),('cache','audio_ble_privacy_cache_maintenance',0x475014)]};engines.append((u,cuts,isc))
 count=0
 for mutation,control,seed in itertools.product([0,1,2],[0,1,0xffffffff],[0,0xa5a5a5a5]):
  outs=[]
  for u,cuts,isc in engines:
   arenas=[(0x20279670,0x2d000),(0x2013be70,0xcd000),(0x20378d9c,4096)]
   for a,n in arenas:u.mem_write(a,bytes([seed&255])*n)
   u.mem_write(0x20000338,bytes([seed&255])*88);u.mem_write(0x78f4b4,W(1,2,4,8,12,0x40000000));u.mem_write(0xe000ed24,W(seed))
   for i,a in enumerate(ram):u.mem_write(a,W(i if seed==0 else 17,0x20001001+i*256,0x10101,0x200010ff+i*256,1,1))
   u.mem_write(0xe000ed90,W(*[(seed+i)&0xffffffff for i in range(32)]));u.mem_write(0xe000ed94,W(control));events=[];mutexes=[]
   def code(uc,a,n,user):
    if n==4 and (op:=barriers.get(bytes(uc.mem_read(a,4)))):events.append((op,))
    if a not in cuts:return
    op=cuts[a];r=[uc.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]]
    if op=='copy':
     data=bytes(uc.mem_read(r[1],r[2]));events.append((op,data.hex(),r[2]));uc.mem_write(r[0],data)
     if mutation==1:uc.mem_write(r[0]+4,W(0x12345678))
     if mutation==2:uc.mem_write(0xe000ed94,W(1))
    elif op=='mutex':
     events.append((op,r[0]));mutexes.append(0x20007000+len(mutexes)*32);uc.reg_write(UC_ARM_REG_R0,mutexes[-1]);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
    elif op in ['log','heaplog']:events.append(('log',*r[:3 if r[0]==0x710764 else 2]))
    else:events.append((op,*r[:2]))
    uc.reg_write(UC_ARM_REG_R0,0x12345678);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   def memory(uc,access,a,n,value,user):
    if not (0xe000ed90<=a<0xe000ee10 or a==0xe000ed24):return
    events.append(('read',a,n,struct.unpack('<I',uc.mem_read(a,4))[0]) if access==16 else ('write',a,n,value))
   h=u.hook_add(UC_HOOK_CODE,code);m=u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,memory);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((syms['audio_uart_heap_initialize_4842e6'] if isc else 0x4842e6)|1,0x600000,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
   outs.append((events,u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(0xe000ed90,128)),[bytes(u.mem_read(a,24)) for a in ram],bytes(u.mem_read(0x20000338,88)),[hashlib.sha256(bytes(u.mem_read(a,n))).hexdigest() for a,n in arenas],bytes(u.mem_read(0xe000ed24,4))));u.hook_del(h);u.hook_del(m)
  assert outs[0]==outs[1],(mutation,control,seed,outs);count+=1
 receipt={'status':'PASS_COMPILED_ARM_CONNECTED_HEAP_STARTUP_NATIVE','cases':count,'source_sha256':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in S},'payload_sha256':hashlib.sha256(blob).hexdigest(),'limits':['Actual three-pool startup, TLSF control/add-pool/insertion and MPU root/helpers execute; mutex/logger/error/copy/cache are controlled cuts.','Full arena hashes, pool cells, modeled register/barrier trace, valid/invalid RAM descriptors and copy mutations compared. Physical MPU alias semantics,cache effects and hardware startup remain unproved.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
