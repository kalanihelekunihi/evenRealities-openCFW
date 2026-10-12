"""Compiled ARM/native close and cleanup comparisons with resource child cuts."""
from pathlib import Path
import subprocess,tempfile,json,hashlib
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_lv_init_children.c'
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('void audio_uart_lv_heap_free(void*p){} void audio_uart_font_bitmap_release(void*p){} unsigned audio_uart_lv_fs_file_close_4c6ee0(void*p){return 0;}')
 elf=td/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-fno-inline','-ffunction-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_bin_decoder_close_4c7e28',str(SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 count=0
 for entry,native in [('audio_uart_lv_bin_decoder_close_4c7e28',0x4c7e28),('audio_uart_lv_bin_decoder_data_free_4c8210',0x4c8210)]:
  for mask in range(33):
   for mutate in [False,True]:
    outputs=[]
    for isc in [False,True]:
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
     for a,d in segs:u.mem_write(a,d)
     dsc=0x20003000;data=0x20004000
     def put(a,v):u.mem_write(a,v.to_bytes(4,'little'))
     put(dsc+72,0 if mask==32 else data)
     for bit,off in enumerate([0,4,28,32,64]):put(data+off,0x20005000+bit*0x100 if mask&(1<<bit) else 0)
     cuts={(syms[name] if isc else addr)&~1:kind for name,addr,kind in [('audio_uart_lv_heap_free',0x44f758,'free'),('audio_uart_font_bitmap_release',0x48b216,'destroy'),('audio_uart_lv_fs_file_close_4c6ee0',0x4c6ee0,'fs_close')]};calls=[]
     def hook(uc,address,size,user):
      if address not in cuts:return
      kind=cuts[address];arg=uc.reg_read(UC_ARM_REG_R0);calls.append((kind,arg))
      if mutate and kind=='fs_close':put(data,0x20006000)
      if mutate and kind=='destroy':put(data+64,0x20006100)
      uc.reg_write(UC_ARM_REG_R0,0x87654321);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0xdeadbeef if native==0x4c7e28 else dsc);u.reg_write(UC_ARM_REG_R1,dsc)
     u.emu_start((syms[entry] if isc else native)|1,0x600000,count=10000)
     outputs.append((calls,bytes(u.mem_read(dsc,80)),bytes(u.mem_read(data,68)),u.reg_read(UC_ARM_REG_SP)))
    assert outputs[0]==outputs[1],(entry,mask,mutate,outputs)
    count+=1
 receipt={'status':'PASS_BOUNDED_COMPILED_ARM_NATIVE_CLOSE_AND_CLEANUP','cases':count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'native_payload_sha256':hashlib.sha256(BLOB).hexdigest(),'limits':['Filesystem close, draw-buffer destroy and heap free are controlled child cuts, not implementations provided by this test.','Tests include all five resource-presence bits, null user_data and child mutation with fresh field reloads.','Void scratch R0 is not compared; full image placement and hardware remain unproven.']}
 out=Path(__file__).parent/'root-bin-decoder-round58';out.mkdir(exist_ok=True);(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt)
