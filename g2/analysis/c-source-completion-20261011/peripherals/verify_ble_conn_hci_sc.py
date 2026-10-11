"""Bounded compiled-C/native checks of four Cordio startup leaves."""
from pathlib import Path
import struct, subprocess, tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_SP, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2

ROOT = Path(__file__).resolve().parents[3]
BLOB = (ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
    shim = Path(td)/'shim.c'
    shim.write_text('''#include <stdint.h>
uint8_t audio_ble_dm_config[0x40],audio_ble_dm_master_state_a[4],audio_ble_dm_master_state_b[4];
uint8_t audio_ble_dm_conn_table_a[1],audio_ble_dm_conn_table_b[1],audio_ble_dm_conn_table_c[1];
uint8_t audio_ble_dm_conn_state_table_a[1],audio_ble_dm_conn_state_table_b[1];
uint32_t audio_ble_hci_le_supported_features[2];
uint8_t audio_ble_smp_handler_state[0xfc],audio_ble_smp_sc_rows[0x54];
void audio_ble_smp_sc_handler_5e2784(void){} void audio_ble_smp_sc_callback_5e2aba(void){}
void WsfTaskLock(void){} void WsfTaskUnlock(void){} void audio_wsf_timer_remove(void *p){(void)p;}
''')
    elf = Path(td)/'a.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
        '-Wl,-Ttext=0x100000','-Wl,-e,DmConnInit',
        str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_conn_hci_sc_init.c'),str(shim),'-o',str(elf)],check=True)
    syms = {p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
    with elf.open('rb') as f: segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    cases=[('DmConnInit',0x4b6c28,()),('HciSetLeSupFeat',0x52acd6,(0x30501020,0x01020408,0)),
           ('HciSetLeSupFeat',0x52acd6,(0x30501020,0x01020408,1)),('SmpScInit',0x56cf74,()),
           ('WsfTimerStop',0x52a4d2,(0x20070100,))]
    maps={'audio_ble_dm_config':0x20000694,'audio_ble_dm_master_state_a':0x20073fe4,
          'audio_ble_dm_master_state_b':0x20073fd8,'audio_ble_hci_le_supported_features':0x20000028,
          'audio_ble_smp_handler_state':0x20070aec,'audio_ble_smp_sc_rows':0x200728f4}
    for name,native,args in cases:
        observations=[]
        for compiled in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
            u.mem_map(0x100000,0x100000)
            for a,d in segs:u.mem_write(a,d)
            u.mem_map(0x20000000,0x100000)
            state=lambda k:syms[k] if compiled else maps[k]
            if name=='HciSetLeSupFeat':u.mem_write(state('audio_ble_hci_le_supported_features'),struct.pack('<II',0xf0f0f0f0,0xaaaaaaaa))
            calls=[]
            cuts={0x52b8c8:'lock',0x52b8d0:'unlock',0x52a3fc:'remove'} if not compiled else {
                syms['WsfTaskLock']&~1:'lock',syms['WsfTaskUnlock']&~1:'unlock',syms['audio_wsf_timer_remove']&~1:'remove'}
            def hook(uc,a,size,_):
                if a in cuts:
                    calls.append((cuts[a],uc.reg_read(UC_ARM_REG_R0) if cuts[a]=='remove' else None))
                    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
            for reg,arg in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),args):u.reg_write(reg,arg)
            u.emu_start((syms[name] if compiled else native)|1,0x600000,count=5000)
            rd=lambda a:struct.unpack('<I',u.mem_read(a,4))[0]
            if name=='DmConnInit':
                fields=[rd(state('audio_ble_dm_config')+i) for i in (0xc,0x10,0x38)] + [rd(state('audio_ble_dm_master_state_a')),rd(state('audio_ble_dm_master_state_b'))]
                if compiled:
                    rev={syms[k]:v for k,v in {'audio_ble_dm_conn_table_a':0x78a820,'audio_ble_dm_conn_table_b':0x78a82c,'audio_ble_dm_conn_table_c':0x78a838,'audio_ble_dm_conn_state_table_a':0x776a84,'audio_ble_dm_conn_state_table_b':0x78efec}.items()}
                    fields=[rev.get(v,v) for v in fields]
                obs=(fields,calls)
            elif name=='HciSetLeSupFeat':obs=([rd(state('audio_ble_hci_le_supported_features')+i) for i in (0,4)],calls)
            elif name=='SmpScInit':
                base=state('audio_ble_smp_handler_state');fields=[rd(base+i) for i in (0x48,0x94,0xe0,0xf0,0xf4)]
                if compiled:
                    rev={syms['audio_ble_smp_sc_rows']+i*0x1c:0x200728f4+i*0x1c for i in range(3)}
                    rev[syms['audio_ble_smp_sc_handler_5e2784']|1]=0x5e2785
                    rev[syms['audio_ble_smp_sc_callback_5e2aba']|1]=0x5e2abb
                    fields=[rev.get(v,v) for v in fields]
                obs=(fields,u.mem_read(base+0xf8,1),calls)
            else:obs=calls
            observations.append(obs)
        assert observations[0]==observations[1],(name,args,observations)
        print('PASS',name,args)
