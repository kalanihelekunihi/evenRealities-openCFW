from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-tlsf-connected-create-pool-round124';D.mkdir(exist_ok=True)
paths=['file_pool_allocate_candidate/pool_allocate.c','tlsf_adjust_request_candidate/adjust.c','tlsf_locate_free_candidate/locate.c','file_pool_free_candidate/tlsf_mapping.c','file_pool_free_candidate/tlsf_absorb_leaves.c','file_pool_free_candidate/tlsf_free_lists.c','tlsf_prepare_allocation_candidate/prepare.c','tlsf_split_block_candidate/split.c','file_pool_free_candidate/tlsf_block_next.c','file_pool_free_candidate/tlsf_mark_free.c','file_pool_free_candidate/tlsf_lists.c','file_pool_free_candidate/tlsf_align.c','file_pool_free_candidate/tlsf_leaf.c'];S=[R/'components/audio'/p for p in paths]+[R/'components/audio/uart_thread_source_candidate'/p for p in ['display_font_alloc.c','tlsf_reallocate.c']];blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';P=0x20001000;N=0x20004000;W=lambda *v:struct.pack('<'+'I'*len(v),*v)
with tempfile.TemporaryDirectory() as t:
 t=Path(t);shim=t/'shim.c';shim.write_text('void g2_file_close_error(const char*a,const char*b,unsigned c){} void audio_ble_hci_boot_log_4733ee(const char*p,...){}');e=t/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,g2_tlsf_create_with_pool_4d06ec',*[str(p) for p in S],str(shim),'-o',str(e)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(e)],text=True).splitlines() if len(v:=line.split())==3}
 with e.open('rb') as f:segs=[(p['p_vaddr'],p.data()) for p in ELFFile(f).iter_segments() if p['p_type']=='PT_LOAD']
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,b in segs:u.mem_write(a,b)
  cuts={(syms[s] if isc else a)&~1:op for op,s,a in [('log','audio_ble_hci_boot_log_4733ee',0x4733ee),('error','g2_file_close_error',0x4d09b4)]};engines.append((u,cuts,isc))
 count=0;undersized_observation=None
 for size,shift in itertools.product([0,1024,3188,3200,3212,4096,8192,0xffffffff],range(4)):
  outs=[]
  for u,cuts,isc in engines:
   u.mem_write(N,bytes([0xa5])*16384);u.mem_write(0x78f4b4,W(1,2,4,8,12,0x40000000));calls=[]
   def hook(uc,a,n,user):
    if a not in cuts:return
    op=cuts[a];r=[uc.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]]
    if op=='log':calls.append((op,*r[:3 if r[0]==0x710764 else 2]))
    else:calls.append((op,*r))
    uc.reg_write(UC_ARM_REG_R0,0x12345678);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   h=u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_R0,N+shift);u.reg_write(UC_ARM_REG_R1,size);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((syms['g2_tlsf_create_with_pool_4d06ec'] if isc else 0x4d06ec)|1,0x600000,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
   outs.append((calls,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(N,16384))));u.hook_del(h)
  assert outs[0]==outs[1],(size,shift,outs);count+=1
  if size==1024 and shift==0:
   assert outs[0][1]==N and struct.unpack('<I',outs[0][3][16:20])[0]==0
   assert any(call[0]=='log' and call[1]==0x710764 for call in outs[0][0])
   undersized_observation={'control_return_nonnull':True,'add_pool_size_error_logged':True,'free_class_bitmap':0,'allocation_capacity_proven':False}
 receipt={'status':'PASS_COMPILED_ARM_CONNECTED_TLSF_CREATE_POOL','cases':count,'undersized1024_observation':undersized_observation,'source_sha256':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in S},'payload_sha256':hashlib.sha256(blob).hexdigest(),'limits':['Actual control construction/create/add-pool,size/flags/link/free-list insertion execute; logger/error only controlled cuts.','16384 arena bytes compared,including undersized1024 startup pool,unsigned wrap and misalignment. Create-with-pool returns control even when add-pool returns NULL; this does not prove usable allocation capacity or hardware startup.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
