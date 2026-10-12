#!/usr/bin/env python3
"""Actual compiled C/native event emission for the self-contained BLE cases."""
from pathlib import Path
import re,struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *

R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_comm_proc_msg.c'
source=S.read_text()
names=re.findall(r'^extern\s+[^;]+?\b([A-Za-z_]\w*)\(',source,re.M)
data='const unsigned char audio_ble_comm_profile_table[32]={9};\nunsigned int audio_ble_encrypt_tick_200742f4;\nunsigned char audio_ble_comm_state[256];\n'
stubs=data+''.join('__attribute__((naked)) void '+name+'(void){__asm volatile("bx lr");}\n' for name in names)
with tempfile.TemporaryDirectory() as td:
    mock=Path(td)/'mock.c';mock.write_text(stubs)
    elf=Path(td)/'candidate.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_comm_message_release',str(S),str(mock),'-o',str(elf)],check=True)
    with elf.open('rb') as f:
        x=ELFFile(f)
        segments=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD']
        sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
    cases=0
    mapping={0x4bd054:'audio_ble_slave_event_state',
             0x4d0c36:'audio_ble_tx_complete_notify',
             0x52c6c0:'attsCsfSetHashUpdateStatus',
             0x5348ec:'DmSecGenerateEccKeyReq',
             0x53527c:'AttsCalculateDbHash',
             0x4b73c4:'DmConnRole',
             0x4bb9b4:'pairMgrSecAuthFlagSet',
             0x4bbf44:'PB_LastTxEncodeRingConnectInfoTimeSet',
             0x4bb07c:'audio_ble_pair_record',
             0x476ace:'audio_event_loop_remove_delayed',
             0x47697e:'audio_event_loop_push_delayed',
             0x4b82e8:'audio_ble_slave_security_state',
             0x4bb9bc:'pairMgrSecAuthFlagGet',
             0x4490cc:'g2_flashdb_candidate_tick',
             0x4c543e:'Thread_SendEvtToRingTask',
             0x47c568:'audio_ble_pair_failure',
             0x4bafda:'audio_ble_pair_key_process',
             0x5348fc:'DmSecSetEccKey',
             0x52c914:'attsCsfGetHashUpdateStatus',
             0x4bb030:'audio_ble_pair_key_ready',
             0x531d60:'audio_ble_service_discovery_start',
             0x4b48a6:'HciDrvRadioBoot',
             0x4b3026:'DmDevReset'}
    for event in (0x00,0x12,0x15,0x20,0x27,0x28,0x2a,0x2b,0x2c,0x2d,
                  0x2e,0x34,0x35,0x79,0xa5,0xa6):
      for flags in (0,1,2):
        for conn in (0,1,0xff):
            pair=[]
            for is_c in (False,True):
                u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
                u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
                u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
                u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
                for a,d in segments:u.mem_write(a,d)
                u.mem_write(0x20010000,bytes((conn,0,event))+b'\0'*20)
                u.mem_write(0x200742f4,struct.pack('<I',0x1234))
                if is_c:u.mem_write(sym['audio_ble_encrypt_tick_200742f4'],struct.pack('<I',0x1234))
                u.reg_write(UC_ARM_REG_SP,0x200ff000)
                u.reg_write(UC_ARM_REG_LR,0x600001)
                u.reg_write(UC_ARM_REG_R0,0x20010000)
                seen=[]
                def hook(uc,a,size,_):
                    if a in (0x43d0ce,sym['audio_log_flags']&~1):
                        uc.reg_write(UC_ARM_REG_R0,flags)
                        uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
                    if a in (0x43ce9e,sym['compressed_log_output']&~1):
                        p=uc.reg_read(UC_ARM_REG_R1)
                        text=bytes(uc.mem_read(p,200)).split(b'\0')[0]
                        seen.append(('log',uc.reg_read(UC_ARM_REG_R0),text))
                        uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
                    if a in (0x43d574,sym['audio_log_extended']&~1):
                        sp=uc.reg_read(UC_ARM_REG_SP)
                        line,p=struct.unpack('<II',bytes(uc.mem_read(sp,8)))
                        seen.append(('extended',uc.reg_read(UC_ARM_REG_R0),line,
                          bytes(uc.mem_read(p,200)).split(b'\0')[0]))
                        uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
                    if a in (0x4b848c,sym['audio_ble_disconnect_reason']&~1,
                             0x4b8390,sym['audio_ble_pair_failure_reason']&~1):
                        uc.reg_write(UC_ARM_REG_R0,0)
                        uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
                    for native,symbol in mapping.items():
                        if a in (native,sym[symbol]&~1):
                            seen.append((symbol,uc.reg_read(UC_ARM_REG_R0)&255,uc.reg_read(UC_ARM_REG_R1)&255)
                                if symbol=='audio_ble_pair_failure' else
                                (symbol,uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2))
                                if symbol=='audio_event_loop_push_delayed' else
                                (symbol,uc.reg_read(UC_ARM_REG_R0)&255)
                                if symbol in ('audio_ble_slave_event_state','attsCsfSetHashUpdateStatus',
                                              'DmConnRole','pairMgrSecAuthFlagSet','PB_LastTxEncodeRingConnectInfoTimeSet',
                                              'audio_ble_pair_record','audio_ble_slave_security_state',
                                              'Thread_SendEvtToRingTask','audio_ble_service_discovery_start',
                                              'HciDrvRadioBoot')
                                else (symbol,))
                            if symbol=='DmConnRole':uc.reg_write(UC_ARM_REG_R0,0 if conn==0 else 1)
                            if symbol=='audio_ble_pair_record':uc.reg_write(UC_ARM_REG_R0,0)
                            if symbol=='pairMgrSecAuthFlagGet':uc.reg_write(UC_ARM_REG_R0,0)
                            if symbol=='g2_flashdb_candidate_tick':uc.reg_write(UC_ARM_REG_R0,1234)
                            if symbol=='attsCsfGetHashUpdateStatus':uc.reg_write(UC_ARM_REG_R0,0)
                            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
                            return
                u.hook_add(UC_HOOK_CODE,hook)
                u.emu_start((sym['audio_ble_comm_message_release'] if is_c else 0x4b75ce)|1,0x600000,count=500)
                tick=struct.unpack('<I',u.mem_read(sym['audio_ble_encrypt_tick_200742f4'] if is_c else 0x200742f4,4))[0]
                pair.append((seen,tick))
            assert pair[0]==pair[1],(event,conn,pair)
            cases+=1
    print('PASS_BLE_COMM_PROC_MINIMAL_NATIVE',cases)
