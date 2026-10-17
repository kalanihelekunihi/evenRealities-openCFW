#!/usr/bin/env python3
"""Stock/C Cordio ATT server data opcode, length and error dispatch contract."""
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
SOURCE=G2/'components/audio/uart_thread_source_candidate/display_ble_atts_data_53498c_20261017.c'
STOCK=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261017/main-ble-atts-data'
PAYLOAD_SHA='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    payload=STOCK.read_bytes()[32:]
    assert sha(payload)==PAYLOAD_SHA
    obj,elf_path=OUT/'data.o',OUT/'oracle.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-c',str(SOURCE),'-o',str(obj)],check=True)
    defs={'audio_ble_atts_ccb_by_handle_5351a8':0x5351a9,'audio_ble_atts_csf_act_client_state_52caa8':0x52caa9,'audio_ble_atts_proc_table_2000045c':0x2000045c,'attsErrRsp':0x534c9b}
    subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000']+[f'--defsym={k}={v}' for k,v in defs.items()]+[str(obj),'-o',str(elf_path)],check=True,capture_output=True)
    with elf_path.open('rb') as stream:
        elf=ELFFile(stream)
        segments=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD' and p['p_vaddr']<0x20000000]
        symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
    def run(stock,opcode,length,lookup,pending,csf_error,handler_present,connection):
        cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000,(len(payload)+4095)&~4095)
        cpu.mem_write(0x438000,payload)
        cpu.mem_map(0x100000,0x20000)
        cpu.mem_map(0x20000000,0x100000)
        if not stock:
            for address,data in segments:
                if data:cpu.mem_write(address,data)
        ccb,main_ccb,packet,table=0x20011000,0x20012000,0x20013000,0x2000045c
        cpu.mem_write(ccb,bytes([0xa5]*64))
        cpu.mem_write(ccb+0x10,main_ccb.to_bytes(4,'little'))
        cpu.mem_write(ccb+0x24,bytes([connection]))
        cpu.mem_write(main_ccb,bytes([0xa5,0xa5,pending])+bytes([0xa5]*61))
        data=bytearray([0x5a]*64);data[8]=opcode;data[9:11]=b'\x34\x12'
        cpu.mem_write(packet,bytes(data))
        cpu.mem_write(table,bytes(18*4))
        if handler_present:
            cpu.mem_write(table, b''.join((0x101e01).to_bytes(4,'little') for _ in range(18)))
        cpu.reg_write(A.UC_ARM_REG_R0,0x1234)
        cpu.reg_write(A.UC_ARM_REG_R1,length)
        cpu.reg_write(A.UC_ARM_REG_R2,packet)
        cpu.reg_write(A.UC_ARM_REG_SP,0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR,0x101f01)
        calls,done=[],[False]
        def reg(machine,n):return machine.reg_read((A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)[n])
        def hook(machine,pc,_size,_user):
            if pc==0x101f00:done[0]=True;machine.emu_stop();return
            if pc==0x101e00:
                calls.append(('handler',reg(machine,0),reg(machine,1),reg(machine,2)))
                machine.reg_write(A.UC_ARM_REG_PC,machine.reg_read(A.UC_ARM_REG_LR));return
            value=0
            if pc==0x5351a8:
                calls.append(('lookup',reg(machine,0),reg(machine,1)));value=ccb if lookup else 0
            elif pc==0x52caa8:
                calls.append(('csf',reg(machine,0),reg(machine,1),reg(machine,2)));value=csf_error
            elif pc==0x534c9a:
                stack=machine.reg_read(A.UC_ARM_REG_SP)
                reason=int.from_bytes(machine.mem_read(stack,4),'little')
                calls.append(('error',reg(machine,0),reg(machine,1),reg(machine,2),reg(machine,3),reason))
            else:return
            machine.reg_write(A.UC_ARM_REG_R0,value)
            machine.reg_write(A.UC_ARM_REG_PC,machine.reg_read(A.UC_ARM_REG_LR))
        cpu.hook_add(UC_HOOK_CODE,hook)
        entry=0x53498c if stock else symbols['audio_ble_atts_data_53498c']
        cpu.emu_start(entry|1,0,count=500)
        assert done[0],(stock,opcode,length,lookup,pending,csf_error,handler_present,connection,calls)
        return calls,bytes(cpu.mem_read(ccb,64)),bytes(cpu.mem_read(main_ccb,64)),bytes(cpu.mem_read(packet,64))
    cases=[]
    opcodes=(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,0x52,0xd2,0x40,0x80)
    for opcode,length,lookup,pending,csf_error,handler_present in itertools.product(opcodes,(0,1,2,3,5,15),(False,True),(0,8),(0,0x12),(False,True)):
        if len(cases)>1600:break
        cases.append((opcode,length,lookup,pending,csf_error,handler_present,1))
    cases=cases[::13]
    cases += [(opcode,length,True,pending,error,present,connection)
              for opcode,length,pending,error,present,connection in itertools.product(
                  (2,4,10,18,22,30,32,0x52,0xd2,0x40),(0,2,3,5,15),(0,8),(0,0x12),(False,True),(1,2))
              if (opcode+length+pending+error+int(present)+connection)%17==0]
    cases += [(opcode,length,True,0,0,present,1)
              for opcode,length,present in itertools.product(opcodes,(1,15),(False,True))]
    cases += [(opcode,5,True,8,error,True,1)
              for opcode,error in itertools.product(opcodes,(0,0x12))]
    for case in cases:
        native,compiled=run(True,*case),run(False,*case)
        if native!=compiled:raise RuntimeError(f'ATT server data mismatch {case}: {native[0]} != {compiled[0]}')
    record={'status':'PASS_BOUNDED_MAIN_BLE_ATTS_DATA_C','cases':len(cases),'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE.read_bytes()),'stock_payload_sha256':PAYLOAD_SHA,'oracle_elf_sha256':sha(elf_path.read_bytes()),'source_complete':False,'flashable':False,'hardware_proof':False,'limits':['Server CCB lookup, client-state gate, process table and error response are controlled; table owner and two helper bodies remain unresolved.']}
    receipt=OUT/'oracle-receipt.json';receipt.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(record['status'],record['cases'],sha(receipt.read_bytes()))
if __name__=='__main__':main()
