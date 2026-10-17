#!/usr/bin/env python3
"""Stock/C Cordio ATT server connection callback for valid connection IDs."""
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
SOURCE=G2/'components/audio/uart_thread_source_candidate/display_ble_atts_conn_534aba_20261017.c'
STOCK=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261017/main-ble-atts-conn'
PAYLOAD_SHA='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    payload=STOCK.read_bytes()[32:]
    assert sha(payload)==PAYLOAD_SHA
    obj,elf_path=OUT/'conn.o',OUT/'oracle.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-c',str(SOURCE),'-o',str(obj)],check=True)
    defs={'audio_ble_atts_state':0x2006e5f0,'audio_ble_atts_ccb_queue_cleanup_534cde':0x534cdf,'audio_ble_dm_conn_check_idle_4b73a2':0x4b73a3,'WsfTimerStop':0x52a4d3}
    subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000']+[f'--defsym={k}={v}' for k,v in defs.items()]+[str(obj),'-o',str(elf_path)],check=True,capture_output=True)
    with elf_path.open('rb') as stream:
        elf=ELFFile(stream)
        segments=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD' and p['p_vaddr']<0x20000000]
        symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
    def run(stock,event_kind,connection,idle,pattern):
        cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000,(len(payload)+4095)&~4095)
        cpu.mem_write(0x438000,payload)
        cpu.mem_map(0x100000,0x20000)
        cpu.mem_map(0x20000000,0x100000)
        if not stock:
            for address,data in segments:
                if data:cpu.mem_write(address,data)
        ccb,event,state,interface=0x20011000,0x20012000,0x2006e5f0,0x20013000
        cpu.mem_write(ccb,bytes([pattern]*64))
        cpu.mem_write(ccb+0xe,bytes([connection]))
        cpu.mem_write(event,bytes([pattern]*16))
        cpu.mem_write(event+2,bytes([event_kind]))
        cpu.mem_write(state,bytes([0xa5]*0x268))
        cpu.mem_write(state+0x260,interface.to_bytes(4,'little'))
        cpu.mem_write(interface,bytes(16))
        cpu.mem_write(interface+12,(0x101e01).to_bytes(4,'little'))
        cpu.reg_write(A.UC_ARM_REG_R0,ccb)
        cpu.reg_write(A.UC_ARM_REG_R1,event)
        cpu.reg_write(A.UC_ARM_REG_SP,0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR,0x101f01)
        calls,done=[],[False]
        def reg(machine,n):return machine.reg_read((A.UC_ARM_REG_R0,A.UC_ARM_REG_R1)[n])
        def hook(machine,pc,_size,_user):
            if pc==0x101f00:done[0]=True;machine.emu_stop();return
            if pc==0x101e00:
                calls.append(('ind',reg(machine,0),reg(machine,1)))
                machine.reg_write(A.UC_ARM_REG_PC,machine.reg_read(A.UC_ARM_REG_LR));return
            value=0
            if pc==0x534cde:calls.append(('clear',reg(machine,0)))
            elif pc==0x4b73a2:calls.append(('idle',reg(machine,0)));value=idle
            elif pc==0x52a4d2:calls.append(('timer',reg(machine,0)))
            else:return
            machine.reg_write(A.UC_ARM_REG_R0,value)
            machine.reg_write(A.UC_ARM_REG_PC,machine.reg_read(A.UC_ARM_REG_LR))
        cpu.hook_add(UC_HOOK_CODE,hook)
        entry=0x534aba if stock else symbols['audio_ble_atts_conn_534aba']
        cpu.emu_start(entry|1,0,count=800)
        assert done[0],(stock,event_kind,connection,idle,pattern,calls)
        return calls,bytes(cpu.mem_read(ccb,64)),bytes(cpu.mem_read(event,16)),bytes(cpu.mem_read(state,0x268))
    cases=list(itertools.product((0,0x27,0x28,0xff),(1,2,3),(0,1,4,5,0xffff),(0,0x5a,0xa5,0xff)))
    cases=cases[::3]+[(0x28,connection,idle,pattern) for connection,idle,pattern in itertools.product((1,2,3),(0,4,5),(0,0xa5))]
    for case in cases:
        native,compiled=run(True,*case),run(False,*case)
        if native!=compiled:raise RuntimeError(f'ATT server connection mismatch {case}: {native[0]} != {compiled[0]}')
    record={'status':'PASS_BOUNDED_MAIN_BLE_ATTS_CONN_C','cases':len(cases),'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE.read_bytes()),'stock_payload_sha256':PAYLOAD_SHA,'oracle_elf_sha256':sha(elf_path.read_bytes()),'source_complete':False,'flashable':False,'hardware_proof':False,'limits':['Prepare-write queue cleanup, idle-mask lookup, timer stop and indication callback are controlled; invalid connection ID diagnostic excluded.']}
    receipt=OUT/'oracle-receipt.json';receipt.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(record['status'],record['cases'],sha(receipt.read_bytes()))
if __name__=='__main__':main()
