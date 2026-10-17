#!/usr/bin/env python3
"""Stock/C Cordio ATT server Client Supported Features state gate."""
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
SOURCE=G2/'components/audio/uart_thread_source_candidate/display_ble_atts_csf_act_client_state_52caa8_20261017.c'
STOCK=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261017/main-ble-atts-csf-act-client-state'
PAYLOAD_SHA='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    payload=STOCK.read_bytes()[32:]
    assert sha(payload)==PAYLOAD_SHA
    obj,elf_path=OUT/'csf.o',OUT/'oracle.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-c',str(SOURCE),'-o',str(obj)],check=True)
    defs={'audio_ble_connection_state_table':0x20073e04,'audio_ble_hci_vendor_log_enabled_4c9c50':0x4c9c51,'audio_ble_hci_vendor_compare_44b610':0x44b611,'audio_log_flags':0x43d0cf,'audio_log_extended':0x43d575,'audio_ble_hci_wsf_trace':0x52a63d}
    subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000']+[f'--defsym={k}={v}' for k,v in defs.items()]+[str(obj),'-o',str(elf_path)],check=True,capture_output=True)
    with elf_path.open('rb') as stream:
        elf=ELFFile(stream)
        segments=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD' and p['p_vaddr']<0x20000000]
        symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
    def run(stock,handle,opcode,state,csf,hash_updating,callback,uuid,enabled,flags):
        cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000,(len(payload)+4095)&~4095)
        cpu.mem_write(0x438000,payload)
        cpu.mem_map(0x100000,0x20000)
        cpu.mem_map(0x20000000,0x100000)
        if not stock:
            for address,data in segments:
                if data:cpu.mem_write(address,data)
        table,packet=0x20073e04,0x20011000
        cpu.mem_write(table,bytes(16))
        cpu.mem_write(table+handle*2,bytes([csf,state]))
        cpu.mem_write(table+8,(0x101e01 if callback else 0).to_bytes(4,'little'))
        cpu.mem_write(table+12,bytes([hash_updating]))
        cpu.mem_write(packet,bytes([0x5a]*64))
        cpu.mem_write(packet+13,uuid.to_bytes(2,'little'))
        cpu.reg_write(A.UC_ARM_REG_R0,handle)
        cpu.reg_write(A.UC_ARM_REG_R1,opcode)
        cpu.reg_write(A.UC_ARM_REG_R2,packet)
        cpu.reg_write(A.UC_ARM_REG_SP,0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR,0x101f01)
        calls,done=[],[False]
        def reg(machine,n):return machine.reg_read((A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)[n])
        def string(machine,address):return bytes(machine.mem_read(address,190)).split(b'\0')[0].decode('ascii')
        def hook(machine,pc,_size,_user):
            if pc==0x101f00:done[0]=True;machine.emu_stop();return
            if pc==0x101e00:
                calls.append(('callback',reg(machine,0),reg(machine,1),reg(machine,2)))
                machine.reg_write(A.UC_ARM_REG_PC,machine.reg_read(A.UC_ARM_REG_LR));return
            value=0
            if pc==0x4c9c50:calls.append(('enabled',));value=enabled
            elif pc==0x44b610:
                left,right,count=reg(machine,0),reg(machine,1),reg(machine,2)
                calls.append(('compare',bytes(machine.mem_read(left,count)),bytes(machine.mem_read(right,count))))
                value=0 if machine.mem_read(left,count)==machine.mem_read(right,count) else 1
            elif pc==0x43d0ce:calls.append(('flags',));value=flags
            elif pc==0x43d574:
                stack=machine.reg_read(A.UC_ARM_REG_SP)
                args=[int.from_bytes(machine.mem_read(stack+i*4,4),'little') for i in range(4)]
                calls.append(('extended',reg(machine,0),string(machine,reg(machine,1)),string(machine,reg(machine,2)),string(machine,reg(machine,3)),args[0],string(machine,args[1]),args[2],args[3]))
            elif pc==0x52a63c:calls.append(('trace',string(machine,reg(machine,0)),string(machine,reg(machine,1)),reg(machine,2),reg(machine,3)))
            else:return
            machine.reg_write(A.UC_ARM_REG_R0,value)
            machine.reg_write(A.UC_ARM_REG_PC,machine.reg_read(A.UC_ARM_REG_LR))
        cpu.hook_add(UC_HOOK_CODE,hook)
        entry=0x52caa8 if stock else symbols['audio_ble_atts_csf_act_client_state_52caa8']
        cpu.emu_start(entry|1,0,count=3000)
        assert done[0],(stock,handle,opcode,state,csf,hash_updating,callback,uuid,enabled,flags,calls)
        return calls,cpu.reg_read(A.UC_ARM_REG_R0),bytes(cpu.mem_read(table,16)),bytes(cpu.mem_read(packet,64))
    cases=[]
    for handle,opcode,state,csf,hash_updating,callback,uuid,enabled,flags in itertools.product(
        (0,1,2),(2,8,0x1e,0x12,0x52),(0,1,2,3),(0,1),(0,1),(False,True),(0x2b2a,0x1234),(0,1),(0,2)):
        if len(cases)>4500:break
        cases.append((handle,opcode,state,csf,hash_updating,callback,uuid,enabled,flags))
    cases=cases[::29]
    cases += [(handle,opcode,state,csf,hash_updating,callback,uuid,enabled,flags)
              for handle,opcode,state,csf,hash_updating,callback,uuid,enabled,flags in itertools.product(
                  (0,1,2),(8,0x52),(0,1,3),(0,1),(0,1),(False,True),(0x2b2a,0x1234),(0,1),(0,2))
              if (handle+opcode+state+csf+hash_updating+int(callback)+uuid+enabled+flags)%23==0]
    cases += [
        (0,8,3,1,1,True,0x2b2a,1,2),
        (1,8,1,0,1,True,0x2b2a,0,0),
        (2,0x52,3,1,0,False,0x1234,1,2),
        (1,0x12,1,0,0,True,0x1234,1,2),
        (2,0x1e,3,1,1,True,0x2b2a,0,0),
    ]
    for case in cases:
        native,compiled=run(True,*case),run(False,*case)
        if native!=compiled:raise RuntimeError(f'ATT CSF state mismatch {case}: {native[0]} != {compiled[0]}')
    record={'status':'PASS_BOUNDED_MAIN_BLE_ATTS_CSF_ACT_CLIENT_STATE_C','cases':len(cases),'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE.read_bytes()),'stock_payload_sha256':PAYLOAD_SHA,'oracle_elf_sha256':sha(elf_path.read_bytes()),'source_complete':False,'flashable':False,'hardware_proof':False,'limits':['Logger and persistence callback are controlled; selected client states, commands, hash UUIDs and hash-update flag.']}
    receipt=OUT/'oracle-receipt.json';receipt.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(record['status'],record['cases'],sha(receipt.read_bytes()))
if __name__=='__main__':main()
