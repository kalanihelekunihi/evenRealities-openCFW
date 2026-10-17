#!/usr/bin/env python3
"""Stock/C Cordio ATT client connection callback contract."""
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
SOURCE=G2/'components/audio/uart_thread_source_candidate/display_ble_attc_conn_53135a_20261017.c'
STOCK=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261017/main-ble-attc-conn'
PAYLOAD_SHA='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    payload=STOCK.read_bytes()[32:]
    assert sha(payload)==PAYLOAD_SHA
    obj,elf_path=OUT/'conn.o',OUT/'oracle.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-c',str(SOURCE),'-o',str(obj)],check=True)
    defsyms={'audio_ble_attc_state':0x2006f904,'audio_ble_att_cfg_ptr_200004b4':0x200004b4,'DmConnRole':0x4b73c5,'audio_ble_hci_max_rx_acl_len_530d4c':0x530d4d,'audio_ble_attc_mtu_request':0x4b57fb,'audio_ble_attc_req_clear_531af2':0x531af3,'audio_ble_attc_write_cmd_callback_530de6':0x530de7,'WsfTimerStop':0x52a4d3}
    subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000']+[f'--defsym={key}={value}' for key,value in defsyms.items()]+[str(obj),'-o',str(elf_path)],check=True,capture_output=True)
    with elf_path.open('rb') as stream:
        elf=ELFFile(stream)
        segments=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD' and p['p_vaddr']<0x20000000]
        symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
    def run(stock,event_kind,connection,role,rx_len,mtu,close_status,reason,on_deck_event,outgoing,sign):
        cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000,(len(payload)+4095)&~4095)
        cpu.mem_write(0x438000,payload)
        cpu.mem_map(0x100000,0x20000)
        cpu.mem_map(0x20000000,0x100000)
        if not stock:
            for address,data in segments:
                if data:cpu.mem_write(address,data)
        ccb,event,state,sign_table=0x20011000,0x20012000,0x2006f904,0x20013000
        cpu.mem_write(ccb,bytes([0xa5]*64))
        cpu.mem_write(ccb+0xe,bytes([connection]))
        cpu.mem_write(event,bytes([0xa5]*16))
        cpu.mem_write(event+2,bytes([event_kind,close_status]))
        cpu.mem_write(event+8,bytes([reason]))
        cpu.mem_write(state,bytes([0]*0x300))
        on_deck=state+0x180+connection*12
        cpu.mem_write(on_deck,bytes([0x5a]*12))
        cpu.mem_write(on_deck+2,bytes([on_deck_event]))
        for slot in range(3):
            client=state+(connection-1)*0x84+slot*0x2c
            cpu.mem_write(client,bytes([0xa5]*0x2c))
            cpu.mem_write(client+6,bytes([outgoing if slot!=1 else 0]))
            cpu.mem_write(client+0x29,bytes([connection]))
        cpu.mem_write(state+0x1b0,(sign_table if sign else 0).to_bytes(4,'little'))
        cpu.mem_write(sign_table,bytes(8))
        cpu.mem_write(sign_table+4,(0x101e01).to_bytes(4,'little'))
        cpu.mem_write(0x200004b4,(0x20000414).to_bytes(4,'little'))
        cpu.mem_write(0x20000414+4,mtu.to_bytes(2,'little'))
        cpu.reg_write(A.UC_ARM_REG_R0,ccb)
        cpu.reg_write(A.UC_ARM_REG_R1,event)
        cpu.reg_write(A.UC_ARM_REG_SP,0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR,0x101f01)
        calls,done=[],[False]
        def reg(machine,n):return machine.reg_read((A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2)[n])
        def hook(machine,pc,_size,_user):
            if pc==0x101f00:done[0]=True;machine.emu_stop();return
            if pc==0x101e00:
                calls.append(('sign',reg(machine,0),reg(machine,1)))
                machine.reg_write(A.UC_ARM_REG_PC,machine.reg_read(A.UC_ARM_REG_LR));return
            value=0
            if pc==0x4b73c4:calls.append(('role',reg(machine,0)));value=role
            elif pc==0x530d4c:calls.append(('rx',));value=rx_len
            elif pc==0x4b57fa:calls.append(('mtu',reg(machine,0),reg(machine,1)))
            elif pc==0x531af2:calls.append(('clear',reg(machine,0),reg(machine,1),reg(machine,2)))
            elif pc==0x52a4d2:calls.append(('timer',reg(machine,0)))
            elif pc==0x530de6:calls.append(('write',reg(machine,0),reg(machine,1),reg(machine,2)))
            else:return
            machine.reg_write(A.UC_ARM_REG_R0,value)
            machine.reg_write(A.UC_ARM_REG_PC,machine.reg_read(A.UC_ARM_REG_LR))
        cpu.hook_add(UC_HOOK_CODE,hook)
        entry=0x53135a if stock else symbols['audio_ble_attc_conn_53135a']
        cpu.emu_start(entry|1,0,count=1000)
        assert done[0],(stock,event_kind,connection,role,rx_len,mtu,close_status,reason,on_deck_event,outgoing,sign,calls)
        return calls,bytes(cpu.mem_read(ccb,64)),bytes(cpu.mem_read(event,16)),bytes(cpu.mem_read(state,0x1b4))
    cases=[]
    for event_kind,connection,role,rx_len,mtu in itertools.product((0x27,0x29),(1,2),(0,1),(27,251,512),(23,247,400)):
        cases.append((event_kind,connection,role,rx_len,mtu,0,0,0,0,False))
    for connection,close_status,reason,on_deck_event,outgoing,sign in itertools.product((1,2),(0,1,0x65),(0,2,0x13),(0,2),(0,1,2),(False,True)):
        cases.append((0x28,connection,0,251,247,close_status,reason,on_deck_event,outgoing,sign))
    cases=cases[::4]+[
        (0x28,1,0,251,247,0,0x13,2,2,True),
        (0x28,2,0,251,247,1,0x13,0,1,False),
        (0x28,1,0,251,247,0,0,0,0,False),
        (0x27,1,0,251,23,0,0,0,0,False),
        (0x27,1,0,251,247,0,0,0,0,False),
    ]
    for case in cases:
        native,compiled=run(True,*case),run(False,*case)
        if native!=compiled:raise RuntimeError(f'ATT connection mismatch {case}: {native[0]} != {compiled[0]}')
    record={'status':'PASS_BOUNDED_MAIN_BLE_ATTC_CONN_C','cases':len(cases),'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE.read_bytes()),'stock_payload_sha256':PAYLOAD_SHA,'oracle_elf_sha256':sha(elf_path.read_bytes()),'source_complete':False,'flashable':False,'hardware_proof':False,'limits':['DM role, HCI ACL length, MTU request, request clear, timer, signed close and pending Write Command callbacks are controlled; valid connection IDs 1-2 and no invalid-ID diagnostic.']}
    receipt=OUT/'oracle-receipt.json';receipt.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(record['status'],record['cases'],sha(receipt.read_bytes()))
if __name__=='__main__':main()
