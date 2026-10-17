#!/usr/bin/env python3
"""Stock/C Cordio MTU request sender and expanded warning-trace contract."""
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
SOURCE=G2/'components/audio/uart_thread_source_candidate/display_ble_attc_send_mtu_530f08_20261017.c'
STOCK=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261017/main-ble-attc-send-mtu'
PAYLOAD_SHA='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    payload=STOCK.read_bytes()[32:]
    assert sha(payload)==PAYLOAD_SHA
    obj,elf_path=OUT/'mtu.o',OUT/'oracle.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-c',str(SOURCE),'-o',str(obj)],check=True)
    defsyms={'audio_ble_attc_free_pkt_531ac0':0x531ac1,'audio_ble_attc_send_simple_530e30':0x530e31,'audio_ble_hci_vendor_log_enabled_4c9c50':0x4c9c51,'audio_ble_hci_vendor_compare_44b610':0x44b611,'audio_log_flags':0x43d0cf,'audio_log_extended':0x43d575,'audio_ble_hci_wsf_trace':0x52a63d}
    subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000']+[f'--defsym={key}={value}' for key,value in defsyms.items()]+[str(obj),'-o',str(elf_path)],check=True,capture_output=True)
    with elf_path.open('rb') as stream:
        elf=ELFFile(stream)
        segments=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD' and p['p_vaddr']<0x20000000]
        symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
    def run(stock,control,enabled,flags,slot,operation):
        cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000,(len(payload)+4095)&~4095)
        cpu.mem_write(0x438000,payload)
        cpu.mem_map(0x100000,0x20000)
        cpu.mem_map(0x20000000,0x100000)
        if not stock:
            for address,data in segments:
                if data:cpu.mem_write(address,data)
        ccb,main_ccb=0x20011000,0x20012000
        cpu.mem_write(ccb,bytes([0xa5]*64))
        cpu.mem_write(ccb,main_ccb.to_bytes(4,'little'))
        cpu.mem_write(ccb+6,bytes([operation]))
        cpu.mem_write(ccb+0xe,bytes([slot]))
        cpu.mem_write(main_ccb,bytes([0xa5]*64))
        cpu.mem_write(main_ccb+slot*4+2,bytes([control]))
        cpu.reg_write(A.UC_ARM_REG_R0,ccb)
        cpu.reg_write(A.UC_ARM_REG_SP,0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR,0x101f01)
        calls,done=[],[False]
        def reg(machine,n):return machine.reg_read((A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)[n])
        def string(machine,address):return bytes(machine.mem_read(address,180)).split(b'\0')[0].decode('ascii')
        def hook(machine,pc,_size,_user):
            if pc==0x101f00:
                done[0]=True;machine.emu_stop();return
            value=0
            if pc==0x531ac0:calls.append(('free',reg(machine,0)))
            elif pc==0x530e30:calls.append(('simple',reg(machine,0)))
            elif pc==0x4c9c50:
                calls.append(('enabled',));value=enabled
            elif pc==0x44b610:
                left,right,count=reg(machine,0),reg(machine,1),reg(machine,2)
                calls.append(('compare',bytes(machine.mem_read(left,count)),bytes(machine.mem_read(right,count))))
                value=0 if machine.mem_read(left,count)==machine.mem_read(right,count) else 1
            elif pc==0x43d0ce:
                calls.append(('flags',));value=flags
            elif pc==0x43d574:
                stack=machine.reg_read(A.UC_ARM_REG_SP)
                line=int.from_bytes(machine.mem_read(stack,4),'little')
                message_ptr=int.from_bytes(machine.mem_read(stack+4,4),'little')
                calls.append(('extended',reg(machine,0),string(machine,reg(machine,1)),string(machine,reg(machine,2)),string(machine,reg(machine,3)),line,string(machine,message_ptr)))
            elif pc==0x52a63c:
                calls.append(('trace',string(machine,reg(machine,0)),string(machine,reg(machine,1))))
            else:return
            machine.reg_write(A.UC_ARM_REG_R0,value)
            machine.reg_write(A.UC_ARM_REG_PC,machine.reg_read(A.UC_ARM_REG_LR))
        cpu.hook_add(UC_HOOK_CODE,hook)
        entry=0x530f08 if stock else symbols['audio_ble_attc_send_mtu_530f08']
        cpu.emu_start(entry|1,0,count=1000)
        assert done[0],(stock,control,enabled,flags,slot,operation,calls)
        return calls,bytes(cpu.mem_read(ccb,64)),bytes(cpu.mem_read(main_ccb,64))
    cases=list(itertools.product((0,1,2,3,0x80,0xff),(0,1),(0,1,2,3),(0,1,2),(0,1,7,255)))
    cases=cases[::8]+[(control,enabled,flags,slot,operation) for control,enabled,flags,slot,operation in itertools.product((0,1,2,3),(0,1),(0,2),(0,1),(0,7))]
    for case in cases:
        native,compiled=run(True,*case),run(False,*case)
        if native!=compiled:raise RuntimeError(f'ATT MTU mismatch {case}: {native} != {compiled}')
    record={'status':'PASS_BOUNDED_MAIN_BLE_ATTC_SEND_MTU_C','cases':len(cases),'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE.read_bytes()),'stock_payload_sha256':PAYLOAD_SHA,'oracle_elf_sha256':sha(elf_path.read_bytes()),'source_complete':False,'flashable':False,'hardware_proof':False,'limits':['Packet free, simple send, logger enable, compare, flags, extended log and WSF trace are controlled call boundaries.']}
    receipt=OUT/'oracle-receipt.json';receipt.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(record['status'],record['cases'],sha(receipt.read_bytes()))
if __name__=='__main__':main()
