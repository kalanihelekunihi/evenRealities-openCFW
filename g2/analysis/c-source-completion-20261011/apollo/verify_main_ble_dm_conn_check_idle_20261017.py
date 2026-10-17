#!/usr/bin/env python3
"""Stock/C Cordio DM connection idle-mask accessor contract."""
import hashlib
import itertools
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/display_ble_dm_conn_check_idle_4b73a2_20261017.c'
STOCK=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261017/main-ble-dm-conn-check-idle'
PAYLOAD_SHA='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    payload=STOCK.read_bytes()[32:]
    assert sha(payload)==PAYLOAD_SHA
    obj,elf_path=OUT/'idle.o',OUT/'oracle.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-c',str(SOURCE),'-o',str(obj)],check=True)
    subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=audio_dm_connection_records=0x200712a4','--defsym=WsfTaskLock=0x52b8c9','--defsym=WsfTaskUnlock=0x52b8d1',str(obj),'-o',str(elf_path)],check=True,capture_output=True)
    with elf_path.open('rb') as stream:
        elf=ELFFile(stream)
        segments=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD' and p['p_vaddr']<0x20000000]
        symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
    def run(stock,connection,mask,pattern):
        cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000,(len(payload)+4095)&~4095)
        cpu.mem_write(0x438000,payload)
        cpu.mem_map(0x100000,0x20000)
        cpu.mem_map(0x20000000,0x100000)
        if not stock:
            for address,data in segments:
                if data:cpu.mem_write(address,data)
        base=0x200712a4
        cpu.mem_write(base-0x40,bytes([pattern]*0x3100))
        slot=base+connection*0x30-0x22
        cpu.mem_write(slot,mask.to_bytes(2,'little'))
        cpu.reg_write(A.UC_ARM_REG_R0,connection)
        cpu.reg_write(A.UC_ARM_REG_SP,0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR,0x101f01)
        calls,done=[],[False]
        def hook(machine,pc,_size,_user):
            if pc==0x101f00:done[0]=True;machine.emu_stop();return
            if pc in (0x52b8c8,0x52b8d0):
                calls.append('lock' if pc==0x52b8c8 else 'unlock')
                machine.reg_write(A.UC_ARM_REG_PC,machine.reg_read(A.UC_ARM_REG_LR))
        cpu.hook_add(UC_HOOK_CODE,hook)
        entry=0x4b73a2 if stock else symbols['audio_ble_dm_conn_check_idle_4b73a2']
        cpu.emu_start(entry|1,0,count=120)
        assert done[0],(stock,connection,mask,pattern,calls)
        return calls,cpu.reg_read(A.UC_ARM_REG_R0),bytes(cpu.mem_read(slot,2))
    cases=list(itertools.product((0,1,2,3,16,255),(0,1,4,5,0x1234,0xffff),(0,0xa5,0xff)))
    for case in cases:
        native,compiled=run(True,*case),run(False,*case)
        if native!=compiled:raise RuntimeError(f'DM idle-mask mismatch {case}: {native} != {compiled}')
    record={'status':'PASS_BOUNDED_MAIN_BLE_DM_CONN_CHECK_IDLE_C','cases':len(cases),'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE.read_bytes()),'stock_payload_sha256':PAYLOAD_SHA,'oracle_elf_sha256':sha(elf_path.read_bytes()),'source_complete':False,'flashable':False,'hardware_proof':False,'limits':['Task lock and unlock are controlled call boundaries; out-of-range connection IDs test address calculation only.']}
    receipt=OUT/'oracle-receipt.json';receipt.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(record['status'],record['cases'],sha(receipt.read_bytes()))
if __name__=='__main__':main()
