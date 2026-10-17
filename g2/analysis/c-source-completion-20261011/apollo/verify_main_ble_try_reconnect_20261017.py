#!/usr/bin/env python3
"""Bounded stock/C oracle for APP_MasterTryReconnectRingByScene 0x4a316c."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[4]
SOURCE=ROOT/'g2/components/audio/uart_thread_source_candidate/ble_master_try_reconnect_4a316c_20261017.c'
STOCK=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=ROOT/'g2/build/c-firmware/20261017/main-ble-try-reconnect/oracle-receipt.json'
PAYLOAD=STOCK.read_bytes()[32:]
NAMES=['audio_uart_ring_active','audio_setting_unit_record_get_466010','audio_queue_copy_bytes',
       'audio_ble_master_is_connected_4a22c6','audio_ble_ring_link_state_name',
       'audio_ble_master_cancel_retry','audio_ble_master_set_target_hand_4a2068',
       'audio_ble_master_auth_mode_set','audio_event_loop_push_delayed',
       'audio_log_level','audio_log_extended','compressed_log_output']
STOCK_ADDR=[0x4a2914,0x466010,0x439be4,0x4a22c6,0x49f828,0x4a17f4,
            0x4a2068,0x4a2168,0x47697e,0x43d0ce,0x43d574,0x43ce9e]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory() as td:
    elf=Path(td)/'try.elf';new=[0x120001+i*0x20 for i in range(len(NAMES))]
    cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-O2',
         '-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-nostdlib',
         '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_box_reconnect_attempt_4a316c',
         '-Wl,--defsym=audio_ble_master_connect_state=0x20074f87',
         '-Wl,--defsym=audio_ble_ring_link_state=0x20074f85',
         '-Wl,--defsym=audio_ble_master_connect_wait=0x20074f18',
         '-Wl,--defsym=audio_ble_master_connect_event=0x120f01']
    cmd += [f'-Wl,--defsym={name}=0x{address:x}' for name,address in zip(NAMES,new)]
    subprocess.run([*cmd,str(SOURCE),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
    with elf.open('rb') as f:
        e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
        syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
    def run(native,scene,owner,unset,connected,connect_state,link_state,wait,flags):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,PAYLOAD)
        u.mem_map(0x100000,0x40000)
        for addr,data in segs:u.mem_write(addr,data)
        u.mem_map(0x20000000,0x100000)
        u.mem_write(0x20074f87,bytes((connect_state,)))
        u.mem_write(0x20074f85,bytes((link_state,)))
        u.mem_write(0x20074f18,wait.to_bytes(2,'little'))
        u.mem_write(0x200736d4+12,b'\xff'*6 if unset else b'\x01\x02\x03\x04\x05\x06')
        u.mem_write(0x20001000,b'LINK_STATE\0')
        effects=[];hooks=dict(zip(STOCK_ADDR if native else [x&~1 for x in new],NAMES))
        def cstr(a):return bytes(u.mem_read(a,180)).split(b'\0')[0].decode('utf-8','replace')
        def hook(uc,addr,size,_):
            name=hooks.get(addr)
            if name is None:return
            r0,r1,r2,r3=(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
            if name==NAMES[0]:effects.append(('owner',));uc.reg_write(UC_ARM_REG_R0,owner)
            elif name==NAMES[1]:effects.append(('record',));uc.reg_write(UC_ARM_REG_R0,0x200736d4)
            elif name==NAMES[2]:
                effects.append(('copy',r2,bytes(uc.mem_read(r1,r2))))
                uc.mem_write(r0,bytes(uc.mem_read(r1,r2)))
            elif name==NAMES[3]:effects.append(('connected',));uc.reg_write(UC_ARM_REG_R0,connected)
            elif name==NAMES[4]:effects.append(('state_name',r0));uc.reg_write(UC_ARM_REG_R0,0x20001000)
            elif name==NAMES[5]:effects.append(('cancel',))
            elif name==NAMES[6]:effects.append(('target',bytes(uc.mem_read(r0,6)),bytes(uc.mem_read(r1,15)),r2))
            elif name==NAMES[7]:effects.append(('auth',r0));uc.reg_write(UC_ARM_REG_R0,1)
            elif name==NAMES[8]:effects.append(('delay',r1,r2))
            elif name==NAMES[9]:effects.append(('level',));uc.reg_write(UC_ARM_REG_R0,flags)
            elif name==NAMES[10]:effects.append(('extended',r0,cstr(r3)))
            else:effects.append(('compact',r0,cstr(r1)))
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        u.reg_write(UC_ARM_REG_R0,scene);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x130001)
        entry=0x4a316c if native else syms['audio_uart_box_reconnect_attempt_4a316c']&~1
        u.emu_start(entry|1,0x130000,count=30000)
        return (u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20074f18,2)),
                bytes(u.mem_read(0x20074f85,3)),effects)
    count=0
    for scene in (0,1,255,256):
     for owner,unset,connected,connect_state,link_state,wait,flags in [
       (0,0,0,0,0,0,0),(0,0,0,0,0,0,7),
       (1,1,0,0,0,0,0),(1,1,0,0,0,0,7),
       (1,0,1,0,0,0,0),(1,0,1,0,0,0,7),
       *[(1,0,0,3,x,0,7) for x in (0,1,2,6,7)],
       *[(1,0,0,0,x,0,7) for x in range(8)],
       *[(1,0,0,0,0,w,f) for w in (0,10,11,12) for f in (0,1,2,4,7)]]:
      args=(scene,owner,unset,connected,connect_state,link_state,wait,flags)
      stock=run(True,*args);rebuilt=run(False,*args)
      if stock!=rebuilt:raise AssertionError((args,stock,rebuilt))
      count+=1
    rec={'status':'PASS_BOUNDED_MAIN_BLE_TRY_RECONNECT_C','cases':count,
         'source_sha256':sha(SOURCE),'stock_package_sha256':sha(STOCK),
         'scope':'owner, address, connection and link-state branches; lower call order, return, state bytes and delay over bounded cases',
         'remaining_gate':'Connected predicate 0x4a22c6 and exact startup/state ownership remain separate contracts.'}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(rec,indent=2,sort_keys=True)+'\n')
    print(rec['status'],count,sha(OUT))
