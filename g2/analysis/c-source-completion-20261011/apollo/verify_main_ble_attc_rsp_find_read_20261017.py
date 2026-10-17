#!/usr/bin/env python3
"""Bounded stock/C ATT Find Information and Read By Type/Group response oracle."""
import hashlib
import itertools
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_attc_rsp_find_read_4b52c2_20261017.c'
STOCK = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261017/main-ble-attc-rsp-find-read'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'

def sha(data): return hashlib.sha256(data).hexdigest()
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / 'find-read.o', OUT / 'oracle.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-c',str(SOURCE),'-o',str(obj)],check=True)
    subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',str(obj),'-o',str(elf_path)],check=True,capture_output=True)
    with elf_path.open('rb') as stream:
        elf=ELFFile(stream)
        segments=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD' and p['p_vaddr']<0x20000000]
        symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
    def run(stock, op, continuing, start, end, status, body, length):
        cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000,(len(payload)+4095)&~4095)
        cpu.mem_write(0x438000,payload)
        cpu.mem_map(0x100000,0x20000)
        cpu.mem_map(0x20000000,0x100000)
        if not stock:
            for address,data in segments:
                if data: cpu.mem_write(address,data)
        ccb,packet,event=0x20011000,0x20012000,0x20013000
        cpu.mem_write(ccb,bytes([0xa5]*64))
        cpu.mem_write(ccb+6,bytes([op,continuing]))
        cpu.mem_write(ccb+0x12,start.to_bytes(2,'little'))
        cpu.mem_write(ccb+0x14,end.to_bytes(2,'little'))
        cpu.mem_write(event,bytes([0xa5,0xa5,0xa5,status])+bytes([0xa5]*60))
        data=bytearray([0x5a]*128)
        data[9:9+len(body)]=body
        cpu.mem_write(packet,bytes(data))
        for reg,value in ((A.UC_ARM_REG_R0,ccb),(A.UC_ARM_REG_R1,length),(A.UC_ARM_REG_R2,packet),(A.UC_ARM_REG_R3,event),(A.UC_ARM_REG_SP,0x200ff000),(A.UC_ARM_REG_LR,0x101f01)):
            cpu.reg_write(reg,value)
        done=[False]
        def hook(machine,pc,_size,_user):
            if pc==0x101f00:
                done[0]=True
                machine.emu_stop()
        cpu.hook_add(UC_HOOK_CODE,hook)
        entry=0x4b52c2 if stock else symbols['audio_attc_rsp_find_read_4b52c2']
        cpu.emu_start(entry|1,0,count=500)
        assert done[0],(stock,op,continuing,start,end,status,body,length)
        return bytes(cpu.mem_read(ccb,64)),bytes(cpu.mem_read(event,64))
    cases=[]
    for op,continuing,start,end,status,handle,second in itertools.product((2,4,8),(0,1),(0,1,3,0xffff),(2,4,0xffff),(0,1),(0,1,2,3,4,0xffff),(0,1,2,3,4,0xffff)):
        if len(cases)>1600: break
        field=1 if op==2 else 4 if op==4 else 6
        body=bytes([field])+handle.to_bytes(2,'little')+(second.to_bytes(2,'little') if op==8 else b'')+bytes([0x44,0x55,0x66,0x77])
        for length in (1,1+2+(2 if op==8 else 0)+2,len(body)):
            cases.append((op,continuing,start,end,status,body,length))
    cases=cases[::11]
    for case in cases:
        native,compiled=run(True,*case),run(False,*case)
        if native!=compiled:
            raise RuntimeError(f'ATT find/read mismatch {case}: {native} != {compiled}')
    record={'status':'PASS_BOUNDED_MAIN_BLE_ATTC_RSP_FIND_READ_C','cases':len(cases),'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE.read_bytes()),'stock_payload_sha256':PAYLOAD_SHA,'oracle_elf_sha256':sha(elf_path.read_bytes()),'source_complete':False,'flashable':False,'hardware_proof':False,'limits':['Selected ATT response method, continuing state, handle bounds, and truncated packet cases; packet bytes beyond stated length remain mapped.']}
    receipt=OUT/'oracle-receipt.json'
    receipt.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(record['status'],record['cases'],sha(receipt.read_bytes()))
if __name__=='__main__': main()
