#!/usr/bin/env python3
"""Stock/C oracle for APP_MasterIsConnected 0x4a22c6."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[4]
SOURCE=ROOT/'g2/components/audio/uart_thread_source_candidate/ble_master_is_connected_4a22c6_20261017.c'
STOCK=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=ROOT/'g2/build/c-firmware/20261017/main-ble-is-connected/oracle-receipt.json'
PAYLOAD=STOCK.read_bytes()[32:]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory() as td:
    elf=Path(td)/'connected.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
        '-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin',
        '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_master_is_connected_4a22c6',
        '-Wl,--defsym=audio_ble_master_context=0x200742fc',str(SOURCE),'-o',str(elf)],check=True)
    with elf.open('rb') as f:
        e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
        syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
    def run(native,value):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,PAYLOAD)
        u.mem_map(0x100000,0x40000)
        for addr,data in segs:u.mem_write(addr,data)
        u.mem_map(0x20000000,0x100000)
        u.mem_write(0x200742fc,(0x20002000).to_bytes(4,'little'))
        u.mem_write(0x20002055,bytes((value,)))
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x130001)
        entry=0x4a22c6 if native else syms['audio_ble_master_is_connected_4a22c6']&~1
        u.emu_start(entry|1,0x130000,count=1000)
        return u.reg_read(UC_ARM_REG_R0)
    cases=0
    for value in range(256):
        stock=run(True,value);rebuilt=run(False,value)
        if stock!=rebuilt:raise AssertionError((value,stock,rebuilt))
        cases+=1
    rec={'status':'PASS_BOUNDED_MAIN_BLE_IS_CONNECTED_C','cases':cases,
         'source_sha256':sha(SOURCE),'stock_package_sha256':sha(STOCK),
         'scope':'all 256 values of context byte +0x55 with pointer cell at stock RAM 0x200742fc',
         'remaining_gate':'Live master-context allocation and pointer initialization remain separate contracts.'}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(rec,indent=2,sort_keys=True)+'\n')
    print(rec['status'],cases,sha(OUT))
