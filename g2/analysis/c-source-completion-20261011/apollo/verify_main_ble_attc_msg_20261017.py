#!/usr/bin/env python3
"""Stock/C Cordio ATT client message callback contract."""
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
SOURCE=G2/'components/audio/uart_thread_source_candidate/display_ble_attc_msg_5315b4_20261017.c'
PENDING=G2/'components/audio/uart_thread_source_candidate/display_ble_attc_pend_write_cmd_530d74_20261017.c'
STOCK=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261017/main-ble-attc-msg'
PAYLOAD_SHA='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    payload=STOCK.read_bytes()[32:]
    assert sha(payload)==PAYLOAD_SHA
    obj,pend_obj,elf_path=OUT/'msg.o',OUT/'pend.o',OUT/'oracle.elf'
    flags=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-c']
    subprocess.run(flags+[str(SOURCE),'-o',str(obj)],check=True)
    subprocess.run(flags+[str(PENDING),'-o',str(pend_obj)],check=True)
    defsyms={'audio_ble_attc_state':0x2006f904,'audio_ble_attc_ccb_by_conn_id_531820':0x531821,'audio_ble_attc_free_pkt_531ac0':0x531ac1,'audio_ble_attc_req_clear_531af2':0x531af3,'audio_ble_attc_setup_req_531160':0x531161,'WsfTimerStop':0x52a4d3,'audio_ble_hci_vendor_log_enabled_4c9c50':0x4c9c51,'audio_ble_hci_vendor_compare_44b610':0x44b611,'audio_log_flags':0x43d0cf,'audio_log_extended':0x43d575,'audio_ble_hci_wsf_trace':0x52a63d}
    subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000']+[f'--defsym={key}={value}' for key,value in defsyms.items()]+[str(obj),str(pend_obj),'-o',str(elf_path)],check=True,capture_output=True)
    with elf_path.open('rb') as stream:
        elf=ELFFile(stream)
        segments=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD' and p['p_vaddr']<0x20000000]
        symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
    def run(stock,event,slot,on_deck_event,outgoing,pending_handle,lookup,sign,enabled,flags):
        cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000,(len(payload)+4095)&~4095)
        cpu.mem_write(0x438000,payload)
        cpu.mem_map(0x100000,0x20000)
        cpu.mem_map(0x20000000,0x100000)
        if not stock:
            for address,data in segments:
                if data:cpu.mem_write(address,data)
        msg,ccb,state,sign_table=0x20011000,0x20012000,0x2006f904,0x20013000
        cpu.mem_write(msg,bytes([0xa5]*12))
        cpu.mem_write(msg,(1).to_bytes(2,'little'))
        cpu.mem_write(msg+2,bytes([event]))
        cpu.mem_write(msg+8,(0x1234).to_bytes(2,'little'))
        cpu.mem_write(msg+10,bytes([slot]))
        cpu.mem_write(ccb,bytes([0xa5]*64))
        cpu.mem_write(ccb+6,bytes([outgoing]))
        cpu.mem_write(ccb+0x28,bytes([slot,1]))
        cpu.mem_write(ccb+0x2a,pending_handle.to_bytes(2,'little'))
        cpu.mem_write(state,bytes([0]*0x300))
        on_deck=state+0x180+12
        cpu.mem_write(on_deck,bytes([0x5a]*12))
        cpu.mem_write(on_deck+2,bytes([on_deck_event]))
        cpu.mem_write(state+0x1b0,(sign_table if sign else 0).to_bytes(4,'little'))
        cpu.mem_write(sign_table,(0x101e01).to_bytes(4,'little'))
        cpu.reg_write(A.UC_ARM_REG_R0,msg)
        cpu.reg_write(A.UC_ARM_REG_SP,0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR,0x101f01)
        calls,done=[],[False]
        def reg(machine,n):return machine.reg_read((A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)[n])
        def string(machine,address):return bytes(machine.mem_read(address,180)).split(b'\0')[0].decode('ascii')
        def hook(machine,pc,_size,_user):
            if pc==0x101f00:done[0]=True;machine.emu_stop();return
            if pc==0x101e00:
                calls.append(('signed',reg(machine,0),reg(machine,1)))
                machine.reg_write(A.UC_ARM_REG_PC,machine.reg_read(A.UC_ARM_REG_LR));return
            value=0
            if pc==0x531820:
                calls.append(('lookup',reg(machine,0),reg(machine,1)))
                value=ccb if lookup else 0
            elif pc==0x531ac0:calls.append(('free',reg(machine,0)))
            elif pc==0x531af2:calls.append(('clear',reg(machine,0),reg(machine,1),reg(machine,2)))
            elif pc==0x531160:calls.append(('setup',reg(machine,0),reg(machine,1)))
            elif pc==0x52a4d2:calls.append(('timer',reg(machine,0)))
            elif pc==0x4c9c50:calls.append(('enabled',));value=enabled
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
        entry=0x5315b4 if stock else symbols['audio_ble_attc_msg_5315b4']
        cpu.emu_start(entry|1,0,count=1500)
        assert done[0],(stock,event,slot,on_deck_event,outgoing,pending_handle,lookup,sign,enabled,flags,calls)
        return calls,bytes(cpu.mem_read(msg,12)),bytes(cpu.mem_read(ccb,64)),bytes(cpu.mem_read(state,0x1b4))
    cases=[]
    for event in (0,1,2,10,11,16,17,18,19,20,21):
        for slot in (0,1):
            for lookup in (False,True):
                for enabled,flags in ((0,0),(1,0),(1,2)):
                    cases.append((event,slot,0,0,0,lookup,False,enabled,flags))
    cases += [(event,slot,on_deck,outgoing,pending,True,False,enabled,flags)
              for event,slot,on_deck,outgoing,pending,enabled,flags in itertools.product(
                  (1,10,16,19,20),(0,1),(0,3),(0,1,2),(0,0x1234),(0,1),(0,2))]
    cases=cases[::9]+[(17,0,0,0,0,True,True,enabled,flags) for enabled,flags in ((0,0),(1,0),(1,2))]
    cases += [
        (1,0,3,0,0,True,False,0,0),  # request already on deck
        (1,1,0,2,0,True,False,1,2),  # outgoing request in progress
        (10,1,0,0,0x1234,True,False,0,0),  # pending Write Command
        (1,0,0,1,0,True,False,1,2),  # queue on deck
        (1,1,0,1,0,True,False,0,0),  # setup directly
        (19,0,0,2,0,True,False,1,2),  # cancel outgoing request
        (19,0,3,0,0,True,False,0,0),  # cancel on-deck request
        (19,1,3,0,0,True,False,1,0),  # cancel on other slot
        (20,0,3,2,0,True,False,0,0),  # stock timeout dispatch no-op
    ]
    for case in cases:
        native,compiled=run(True,*case),run(False,*case)
        if native!=compiled:raise RuntimeError(f'ATT message mismatch {case}: {native[0]} != {compiled[0]}')
    record={'status':'PASS_BOUNDED_MAIN_BLE_ATTC_MSG_C','cases':len(cases),'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE.read_bytes()),'pending_source':str(PENDING.relative_to(ROOT)),'pending_source_sha256':sha(PENDING.read_bytes()),'stock_payload_sha256':PAYLOAD_SHA,'oracle_elf_sha256':sha(elf_path.read_bytes()),'source_complete':False,'flashable':False,'hardware_proof':False,'limits':['Connection lookup, free, clear, setup, timer, sign callback, and logger calls are controlled; source-level timeout branch is absent from stock at this entry.']}
    receipt=OUT/'oracle-receipt.json';receipt.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(record['status'],record['cases'],sha(receipt.read_bytes()))
if __name__=='__main__':main()
