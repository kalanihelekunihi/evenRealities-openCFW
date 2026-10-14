"""Controlled ARM C/native HCI event dispatcher comparison, selected branches."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_event_process.c'
NATIVE={'audio_ble_hci_event_cmd_status':0x56b150,'audio_ble_hci_event_cmd_complete':0x56b182,'audio_ble_hci_num_complete_packets':0x530c08,'audio_ble_hci_conn_open':0x52a758,'audio_ble_hci_le_adv_report':0x56a398,'audio_ble_hci_cis_by_handle':0x52adec,'audio_wsf_buffer_alloc':0x530446,'g2_wsf_candidate_buffer_free_word':0x5304d4,'audio_ble_hci_conn_close':0x52a762,'audio_ble_hci_cis_close':0x52ae2e,'audio_ble_hci_vendor_log_enabled_4c9c50':0x4c9c50,'audio_ble_hci_vendor_compare_44b610':0x44b610,'audio_log_flags':0x43d0ce,'audio_ble_hci_vendor_log_43d574':0x43d574,'audio_ble_hci_wsf_trace':0x52a63c}
OTHER='audio_ble_hci_cis_open audio_ble_hci_le_direct_adv_report audio_ble_hci_le_ext_adv_report audio_ble_hci_le_per_adv_report audio_ble_hci_le_conless_iq_report audio_ble_hci_le_conn_iq_report'.split()
DATA='audio_ble_hci_vendor_tag_78d6f4 audio_ble_hci_vendor_tag2_78d6fc audio_ble_hci_vendor_ere audio_ble_hci_vendor_app audio_ble_hci_vendor_hci audio_ble_hci_vendor_message_77f720 audio_ble_hci_vendor_file_77f70c audio_ble_hci_vendor_file_6e0518'.split()
SHIM='''#include <stdint.h>
uint8_t audio_ble_hci_stack_state_20073870[0x40];volatile uint16_t audio_ble_hci_event_counts_20073bc0[16];
uint8_t audio_ble_hci_event_sizes_6e3720[128];uint32_t audio_ble_hci_event_decoders_6c910c[128];
'''+'\n'.join('const uint8_t '+n+'[8]={0};' for n in DATA)+'\n'+'\n'.join('void '+n+'(){}' for n in list(NATIVE)+OTHER)+'\n'
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_event_process_body',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for label,code in (('unknown',0x99),('complete',0x0e),('status',0x0f),('num',0x13),('idle',0x1a),('le_conn',0x3e),('disconn',0x05),('vendor_trace',0x3e),('vendor_log',0x3e)):
  results=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   state=syms['audio_ble_hci_stack_state_20073870'] if is_c else 0x20073870
   counts=syms['audio_ble_hci_event_counts_20073bc0'] if is_c else 0x20073bc0
   u.mem_write(state,b'\x00'*0x40);u.mem_write(counts,b'\x00'*32)
   message=0x20005000;data=bytearray([code,7])+bytearray(30)
   if label in ('le_conn','disconn'):
    typ=1 if label=='le_conn' else 3
    decoder=0x100721
    u.mem_write(state+8,struct.pack('<I',0x100701))
    if is_c:
     u.mem_write(syms['audio_ble_hci_event_sizes_6e3720']+typ,bytes([36 if typ==1 else 10]))
     u.mem_write(syms['audio_ble_hci_event_decoders_6c910c']+4*typ,struct.pack('<I',decoder))
   if label=='le_conn':
    data[2]=1;data[3]=0;data[4]=0x34;data[5]=0x12
   if label.startswith('vendor_'):data[2]=0x17
   if label=='disconn':data[3]=0;data[4]=0x34;data[5]=0x12
   u.mem_write(message,bytes(data))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,message);u.reg_write(UC_ARM_REG_R2,0x12345678);u.reg_write(UC_ARM_REG_R3,0x87654321)
   calls=[];cuts={syms[k]&~1:k for k in NATIVE} if is_c else {v:k for k,v in NATIVE.items()}
   def hook(uc,a,size,_):
    if a in (0x100700,0x100720,0x569d4c,0x569e54):
     calls.append('callback' if a==0x100700 else 'decoder')
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
    if a not in cuts:return
    name=cuts[a];calls.append(name)
    val=0x20006000 if name=='audio_wsf_buffer_alloc' else 0
    if label=='vendor_log' and name=='audio_ble_hci_vendor_log_enabled_4c9c50':val=1
    if label=='vendor_log' and name=='audio_log_flags':val=2
    uc.reg_write(UC_ARM_REG_R0,val);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms['audio_ble_hci_event_process_body'] if is_c else 0x56b390)|1,0x600000,count=900)
   high=u.reg_read(UC_ARM_REG_R1)
   results.append((u.reg_read(UC_ARM_REG_R0),bool(high) if label=='vendor_log' else high,calls,bytes(u.mem_read(counts,24)),bytes(u.mem_read(0x20006000,8))))
  assert results[0]==results[1],(label,results)
  print('PASS',label,results[0])
