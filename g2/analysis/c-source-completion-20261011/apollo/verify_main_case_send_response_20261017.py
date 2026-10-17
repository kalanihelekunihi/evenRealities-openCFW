#!/usr/bin/env python3
"""Bounded stock/C oracle for Case nanopb response encoder 0x510c70."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[4]
SOURCE=ROOT/'g2/components/audio/uart_thread_source_candidate/display_case_send_response_510c70_20261017.c'
STOCK=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=ROOT/'g2/build/c-firmware/20261017/main-case-send-response/oracle-receipt.json'
PAYLOAD=STOCK.read_bytes()[32:]
NAMES=['audio_uart_checksum_copy','audio_ring_pb_assert_509b48',
       'audio_pb_ostream_from_buffer','audio_uart_buffer_zero','audio_pb_encode',
       'audio_uart_case_status','audio_ring_pb_tx_ble_475b14',
       'audio_log_level','audio_log_extended','compressed_log_output']
STOCK_ADDR=[0x439c04,0x509b48,0x4905f4,0x43c0e4,0x490c32,0x4acad0,
            0x475b14,0x43d0ce,0x43d574,0x43ce9e]
GETTERS=[('audio_uart_case_local_soc_4ac726',0x4ac726),
         ('audio_uart_case_local_charge_4ac73c',0x4ac73c),
         ('audio_uart_case_local_lid_4ac752',0x4ac752)]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory() as td:
    elf=Path(td)/'response.elf';new=[0x120001+i*0x20 for i in range(len(NAMES))]
    cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-O2',
         '-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-nostdlib',
         '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_case_send_response_510c70',
         '-Wl,--defsym=audio_uart_case_tx_frame_200f5a9c=0x200f5a9c',
         '-Wl,--defsym=audio_uart_case_tx_encoded_2037c5a0=0x2037c5a0',
         '-Wl,--defsym=audio_uart_case_descriptor_77793c=0x77793c',
         '-Wl,--defsym=g2_uart_service_nonce=0x20074928']
    cmd += [f'-Wl,--defsym={name}=0x{addr:x}' for name,addr in zip(NAMES,new)]
    subprocess.run([*cmd,str(SOURCE),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
    with elf.open('rb') as f:
        e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
        syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
    def run(native,packet,seq,nonce,status,flags,encode_result,error_ptr):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,PAYLOAD)
        u.mem_map(0x100000,0x40000)
        for addr,data in segs:u.mem_write(addr,data)
        u.mem_map(0x20000000,0x100000);u.mem_map(0x20370000,0x20000)
        u.mem_write(0x20074928,nonce)
        u.mem_write(0x200f5a9c,b'\xaa'*10)
        u.mem_write(0x20082000,b'encode-error\0')
        if packet:u.mem_write(0x20081000,b'\x01\x02\x03\x04')
        effects=[];hooks=dict(zip(STOCK_ADDR if native else [x&~1 for x in new],NAMES))
        hooks.update({(addr if native else syms[name]&~1):name for name,addr in GETTERS})
        def word(v):return int.from_bytes(v,'little')
        def cstr(a):return bytes(u.mem_read(a,160)).split(b'\0')[0].decode('utf-8','replace') if a else ''
        def hook(uc,addr,size,_):
            name=hooks.get(addr)
            if name is None:return
            r0,r1,r2,r3=(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
            if name in (x[0] for x in GETTERS):
                i=[x[0] for x in GETTERS].index(name)
                effects.append(('getter',i));uc.reg_write(UC_ARM_REG_R0,nonce[i])
            elif name==NAMES[0]:effects.append(('copy',r2));uc.mem_write(r0,bytes(uc.mem_read(r1,r2)));uc.reg_write(UC_ARM_REG_R0,r0)
            elif name==NAMES[1]:
                d=bytes(uc.mem_read(r0,20));effects.append(('assert',word(d[:4]),word(d[4:8]),
                    cstr(word(d[8:12])),cstr(word(d[12:16])),word(d[16:20])))
            elif name==NAMES[2]:
                effects.append(('ostream',r1==0x2037c5a0,r2))
                uc.mem_write(r0,(0x11111111).to_bytes(4,'little')+r1.to_bytes(4,'little')+r2.to_bytes(4,'little')+bytes(8))
            elif name==NAMES[3]:effects.append(('zero',r1,r2));uc.mem_write(r0,bytes(r1))
            elif name==NAMES[4]:
                effects.append(('encode',r1==0x77793c,bytes(uc.mem_read(r2,10))))
                uc.mem_write(r0+12,(5).to_bytes(4,'little'))
                uc.mem_write(r0+16,(0x20082000 if error_ptr else 0).to_bytes(4,'little'))
                uc.mem_write(0x2037c5a0,b'abcde');uc.reg_write(UC_ARM_REG_R0,encode_result)
            elif name==NAMES[5]:effects.append(('status',));uc.reg_write(UC_ARM_REG_R0,status)
            elif name==NAMES[6]:effects.append(('tx',r0,r1,r2==0x2037c5a0,r3))
            elif name==NAMES[7]:effects.append(('level',));uc.reg_write(UC_ARM_REG_R0,flags)
            elif name==NAMES[8]:effects.append(('extended',r0,cstr(r1),cstr(r3)))
            else:effects.append(('compact',r0,cstr(r1)))
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        u.reg_write(UC_ARM_REG_R0,seq);u.reg_write(UC_ARM_REG_R1,0x20081000 if packet else 0)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x130001)
        entry=0x510c70 if native else syms['audio_uart_case_send_response_510c70']&~1
        u.emu_start(entry|1,0x130000,count=30000)
        return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x200f5a9c,10)),effects
    count=0
    for packet in (0,1):
     for seq in (0,1,255,256):
      for nonce in (b'\x00\x00\x00\x00',b'\x40\x01\x01\x00',b'\xff\x02\x03\x04'):
       for status in (0,1,2):
        for flags,encode_result,error_ptr in ((0,0,0),(1,0,1),(2,1,0),(4,256,1),(7,1,1)):
         args=(packet,seq,nonce,status,flags,encode_result,error_ptr)
         stock=run(True,*args);rebuilt=run(False,*args)
         if stock!=rebuilt:raise AssertionError((args,stock,rebuilt))
         count+=1
    rec={'status':'PASS_BOUNDED_MAIN_CASE_SEND_RESPONSE_C','cases':count,
         'source_sha256':sha(SOURCE),'stock_package_sha256':sha(STOCK),
         'scope':'frame bytes, local getters, encoded output call, return and logging decisions over bounded inputs',
         'remaining_gate':'Final shared frame/encoded-buffer placement, nanopb descriptor linking and BLE transport remain separate.'}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(rec,indent=2,sort_keys=True)+'\n')
    print(rec['status'],count,sha(OUT))
