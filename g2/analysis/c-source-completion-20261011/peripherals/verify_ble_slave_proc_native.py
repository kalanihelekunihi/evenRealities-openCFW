#!/usr/bin/env python3
"""Compiled-C/native bounded BLE slave dispatch and live-state comparison."""
from pathlib import Path
import re,struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_slave_proc_msg.c'
source=S.read_text()
names=re.findall(r'^extern\s+[^;]+?\b([A-Za-z_]\w*)\(',source,re.M)
data='''
#include <stdint.h>
uint8_t *audio_ble_profile_connection_context;
uint8_t *audio_ble_slave_mode_context;
uint8_t *audio_ble_dm_conn_cell;
uint8_t audio_ble_subsystem_link_state_200719c8[256];
uint8_t audio_ble_slave_unpair_flag_20074f8b;
uint8_t audio_ble_slave_adv_stop_flag_20074f8d;
uint8_t audio_ble_slave_link_flags_20074f8c;
'''
stubs=data+''.join('__attribute__((naked)) void '+name+'(void){__asm volatile("bx lr");}\n' for name in names)
with tempfile.TemporaryDirectory() as td:
  mock=Path(td)/'mock.c';mock.write_text(stubs);elf=Path(td)/'candidate.elf'
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                  '-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_adv_message_preprocess',str(S),str(mock),'-o',str(elf)],check=True)
  with elf.open('rb') as f:
    x=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD']
    sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
  mapping={0x4b73c4:'DmConnRole',0x46dfd0:'dmSlaveAdvStopOnDisconnect',
           0x46db04:'audio_ble_adv_init',0x4bd054:'audio_ble_slave_event_state',
           0x46de78:'appSlaveConnOpen',0x46dedc:'audio_ble_slave_request_mtu',
           0x476ace:'audio_event_loop_remove_delayed',
           0x47697e:'audio_event_loop_push_delayed',
           0x4abe60:'audio_uart_command_pending',0x47a676:'audio_ble_pair_count',
           0x4b82e8:'audio_ble_slave_security_state',
           0x4b9984:'tpl_reset_receive_contexts_004b9984',
           0x475524:'Thread_BleMsgtxQueueClear',
           0x48f018:'Thread_BleMsgrxQueueClear'}
  cases=0
  for event in (0x05,0x09,0x0a,0x0d,0x0e,0x15,0x16,0x21,0x22,0x27,0x28,
                0x37,0x47,0x48,0xad,0xb5,0xb8,0xba,0xbb):
    for role,flags in ((0,0),(1,0),(0,1),(1,1),(0,2),(1,2)):
      pair=[]
      for is_c in (False,True):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
        u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
        for a,d in segments:u.mem_write(a,d)
        message=bytearray(24);message[0]=1;message[2]=event;message[14:16]=b'\x40\x00'
        u.mem_write(0x20010000,bytes(message))
        u.mem_write(0x2007432c,struct.pack('<I',0x20030000))
        u.mem_write(0x20074330,struct.pack('<I',0x20031000))
        u.mem_write(0x20074328,struct.pack('<I',0x20032000))
        u.mem_write(0x20032000,struct.pack('<I',0x12345678))
        u.mem_write(0x20074f8d,b'\x01')
        u.mem_write(0x20074f8c,b'\xff')
        u.mem_write(0x20030054,b'\x03' if event==0x28 else b'\x00')
        u.mem_write(0x20031020,b'\x01')
        if is_c:
          for cell,address in [('audio_ble_profile_connection_context',0x20030000),
                               ('audio_ble_slave_mode_context',0x20031000),
                               ('audio_ble_dm_conn_cell',0x20032000)]:
            u.mem_write(sym[cell],struct.pack('<I',address))
          u.mem_write(sym['audio_ble_slave_adv_stop_flag_20074f8d'],b'\x01')
          u.mem_write(sym['audio_ble_slave_link_flags_20074f8c'],b'\xff')
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        u.reg_write(UC_ARM_REG_R0,0x20010000)
        seen=[]
        def hook(uc,a,size,_):
          if a in (0x43d0ce,sym['audio_log_flags']&~1):
            uc.reg_write(UC_ARM_REG_R0,flags);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
          if a in (0x43ce9e,sym['compressed_log_output']&~1):
            p=uc.reg_read(UC_ARM_REG_R1)
            seen.append(('log',uc.reg_read(UC_ARM_REG_R0),bytes(uc.mem_read(p,220)).split(b'\0')[0]))
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
          if a in (0x43d574,sym['audio_log_extended']&~1):
            sp=uc.reg_read(UC_ARM_REG_SP)
            line,p=struct.unpack('<II',bytes(uc.mem_read(sp,8)))
            seen.append(('extended',uc.reg_read(UC_ARM_REG_R0),line,
              bytes(uc.mem_read(p,220)).split(b'\0')[0]))
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
          for native,symbol in mapping.items():
            if a in (native,sym[symbol]&~1):
              seen.append((symbol,uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2))
                if symbol=='audio_event_loop_push_delayed' else
                (symbol,uc.reg_read(UC_ARM_REG_R0)&255)
                if symbol in ('DmConnRole','audio_ble_slave_event_state','audio_ble_pair_count',
                              'audio_ble_slave_security_state') else (symbol,))
              if symbol=='DmConnRole':uc.reg_write(UC_ARM_REG_R0,role)
              if symbol=='audio_uart_command_pending':uc.reg_write(UC_ARM_REG_R0,0)
              if symbol=='audio_ble_pair_count':uc.reg_write(UC_ARM_REG_R0,2)
              uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
        u.hook_add(UC_HOOK_CODE,hook)
        try:u.emu_start((sym['audio_ble_adv_message_preprocess'] if is_c else 0x46e098)|1,0x600000,count=700)
        except Exception as exc:raise RuntimeError((event,role,is_c,hex(u.reg_read(UC_ARM_REG_PC)),seen)) from exc
        state=u.mem_read(0x20031000,40)
        conn_state=u.mem_read(0x20030054,1)
        flag=u.mem_read(sym['audio_ble_slave_adv_stop_flag_20074f8d'] if is_c else 0x20074f8d,1)
        link=u.mem_read(sym['audio_ble_slave_link_flags_20074f8c'] if is_c else 0x20074f8c,1)
        pair.append((seen,bytes(state),bytes(flag),bytes(link),bytes(conn_state)))
      assert pair[0]==pair[1],(event,role,flags,pair)
      cases+=1
  print('PASS_BLE_SLAVE_PROC_NATIVE',cases)
