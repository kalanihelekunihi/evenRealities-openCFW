#!/usr/bin/env python3
"""Bounded stock/C oracle for BoxDetect_ReceiveCaseInfoFromPeer 0x4ac890."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[4]
SOURCE=ROOT/'g2/components/audio/uart_thread_source_candidate/display_case_sync_response_4ac890_20261017.c'
STOCK=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=ROOT/'g2/build/c-firmware/20261017/main-case-sync-response/oracle-receipt.json'
PAYLOAD=STOCK.read_bytes()[32:]
NAMES=['audio_uart_device_role_get','audio_uart_buffer_zero','audio_uart_service_nonce',
       'audio_uart_case_display_refresh_4abf86','audio_uart_case_notify_4abec8',
       'audio_uart_service_prepare3','audio_uart_display_housekeep',
       'audio_uart_case_in_case_side_effect_5130a6','audio_log_level',
       'audio_log_extended','compressed_log_output']
STOCK_ADDR=[0x45a568,0x43c0e4,0x4ac776,0x4abf86,0x4abec8,
            0x4ac828,0x47243a,0x5130a6,0x43d0ce,0x43d574,0x43ce9e]
DATA={'audio_uart_case_peer_raw_20074188':0x20074188,
      'audio_uart_case_soc_cell_2007418c':0x2007418c,
      'audio_uart_case_charge_cell_2007418d':0x2007418d,
      'audio_uart_case_sensor_b':0x2007418e,
      'audio_uart_case_sensor_a':0x2007418f,
      'audio_uart_case_status_disabled':0x20075012}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory() as td:
    elf=Path(td)/'response.elf';new=[0x120001+i*0x20 for i in range(len(NAMES))]
    cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-O2',
         '-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-nostdlib',
         '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_case_sync_response_4ac890']
    cmd += [f'-Wl,--defsym={name}=0x{addr:x}' for name,addr in DATA.items()]
    cmd += [f'-Wl,--defsym={name}=0x{addr:x}' for name,addr in zip(NAMES,new)]
    subprocess.run([*cmd,str(SOURCE),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
    with elf.open('rb') as f:
        e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
        syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
    def run(native,msg,current,nonce,disabled,flags):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,PAYLOAD)
        u.mem_map(0x100000,0x40000)
        for addr,data in segs:u.mem_write(addr,data)
        u.mem_map(0x20000000,0x100000)
        u.mem_write(0x20074188,bytes((0xaa,)*4)+current)
        u.mem_write(0x20075012,bytes((disabled,)))
        if msg is not None:u.mem_write(0x20001000,msg)
        effects=[];hooks=dict(zip(STOCK_ADDR if native else [x&~1 for x in new],NAMES))
        def cstr(a):return bytes(u.mem_read(a,180)).split(b'\0')[0].decode('utf-8','replace')
        def hook(uc,addr,size,_):
            name=hooks.get(addr)
            if name is None:return
            r0,r1,r2,r3=(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
            if name==NAMES[0]:effects.append(('role',));uc.reg_write(UC_ARM_REG_R0,0)
            elif name==NAMES[1]:
                effects.append(('zero',r1,r2));uc.mem_write(r0,bytes((r2&255,))*r1)
            elif name==NAMES[2]:effects.append(('nonce',));uc.mem_write(r0,nonce);uc.reg_write(UC_ARM_REG_R0,0)
            elif name==NAMES[5]:effects.append(('prepare',r0))
            elif name==NAMES[8]:effects.append(('level',));uc.reg_write(UC_ARM_REG_R0,flags)
            elif name==NAMES[9]:
                sp=uc.reg_read(UC_ARM_REG_SP)
                effects.append(('extended',r0,cstr(r3),int.from_bytes(uc.mem_read(sp,4),'little'),cstr(int.from_bytes(uc.mem_read(sp+4,4),'little'))))
            elif name==NAMES[10]:effects.append(('compact',r0,cstr(r1)))
            else:effects.append((name,))
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        u.reg_write(UC_ARM_REG_R0,0 if msg is None else 0x20001000)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x130001)
        entry=0x4ac890 if native else syms['audio_uart_case_sync_response_4ac890']&~1
        u.emu_start(entry|1,0x130000,count=30000)
        return bytes(u.mem_read(0x20074188,8)),effects
    messages=[None]+[bytes((x,0,0,0,a,b,c,d)) for x,a,b,c,d in [
        (0,0,0,0,0),(1,20,1,1,1),(2,99,0,1,0),(3,255,1,1,1),
        (3,1,0,0,1),(4,50,2,2,2),(255,0,1,1,1)]]
    currents=[bytes(x) for x in [(0,0,0,0),(20,1,1,1),(99,1,1,0),(255,0,0,1)]]
    nonces=[bytes(x) for x in [(0,0,0,0),(20,1,1,1),(99,1,1,1),(255,2,2,2)]]
    count=0
    for msg in messages:
     for current in currents:
      for nonce in nonces:
       for disabled in (0,1):
        for flags in (0,1,2,4,7):
         args=(msg,current,nonce,disabled,flags)
         stock=run(True,*args);rebuilt=run(False,*args)
         if stock!=rebuilt:raise AssertionError((args,stock,rebuilt))
         count+=1
    rec={'status':'PASS_BOUNDED_MAIN_CASE_SYNC_RESPONSE_C','cases':count,
         'source_sha256':sha(SOURCE),'stock_package_sha256':sha(STOCK),
         'scope':'8-byte Case state, lower call order, display side effects and logging branch over bounded messages/state',
         'remaining_gate':'Four raw peer status bytes at stock 0x20074188 and in-case side effect 0x5130a6 need source ownership.'}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(rec,indent=2,sort_keys=True)+'\n')
    print(rec['status'],count,sha(OUT))
