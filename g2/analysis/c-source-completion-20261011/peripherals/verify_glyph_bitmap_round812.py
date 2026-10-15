#!/usr/bin/env python3
"""Compare native and C font bitmap wrapper with a controlled callback."""
from pathlib import Path
import hashlib,itertools,json,struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *

root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/glyph_bitmap.c'
out=Path(__file__).resolve().parent/'root-glyph-bitmap-round812';out.mkdir(exist_ok=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
glyph,font,callback=0x20012000,0x20013000,0x20015000
W=lambda n:struct.pack('<I',n&0xffffffff)
with tempfile.TemporaryDirectory() as tmp:
    elf_path=Path(tmp)/'bitmap.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                    '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x110000',
                    '-Wl,--defsym=audio_uart_lvgl_log=0x180021',
                    '-Wl,--defsym=g2_norflash_lock_46f65e=0x180001',
                    '-Wl,--defsym=g2_norflash_unlock_46f674=0x180011',
                    str(source),'-o',str(elf_path)],check=True)
    with elf_path.open('rb') as fp:
        elf=ELFFile(fp)
        segments=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD']
        symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
    def run(original,address_after,seed,user_data):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
        u.mem_map(0x100000,0x100000)
        for a,data in segments:u.mem_write(a,data)
        u.mem_map(0x20000000,0x200000)
        u.mem_write(glyph,bytes([seed])*0x100)
        u.mem_write(font,bytes([seed^0xa5])*0x100)
        u.mem_write(glyph,W(font))
        u.mem_write(font+4,W(callback|1))
        u.mem_write(font+0x18,W(0x80000001 if seed&1 else 0x7fffffff))
        events=[]
        hooks={0x46f65e:'lock',0x46f674:'unlock',callback:'callback'} if original else {
            0x180000:'lock',0x180010:'unlock',callback:'callback'}
        def hook(emu,address,size,user):
            if address not in hooks:return
            event=hooks[address]
            if event=='callback':
                events.append((event,emu.reg_read(UC_ARM_REG_R0),emu.reg_read(UC_ARM_REG_R1)))
                emu.mem_write(font+0x18,W(address_after))
                emu.reg_write(UC_ARM_REG_R0,0x20019000)
            else:events.append((event,))
            emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        u.reg_write(UC_ARM_REG_CPSR,0x33)
        u.reg_write(UC_ARM_REG_R0,glyph)
        u.reg_write(UC_ARM_REG_R1,user_data)
        u.reg_write(UC_ARM_REG_SP,0x201ff000)
        u.reg_write(UC_ARM_REG_LR,0x600001)
        entry=0x4d5612 if original else symbols['audio_uart_ambiq_glyph_bitmap_4d5612']
        u.emu_start(entry|1,0x600000,count=300)
        assert u.reg_read(UC_ARM_REG_PC)==0x600000
        return (events,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),
                bytes(u.mem_read(glyph,0x100)),bytes(u.mem_read(font,0x100)))
    cases=0
    for address_after,seed,user_data in itertools.product(
        (0x7fffffff,0x80000001,0xffffffff),(0,1,0x5a,0xff),(0,0x12345678)):
        actual=run(True,address_after,seed,user_data)
        candidate=run(False,address_after,seed,user_data)
        if actual!=candidate:
            (out/'mismatch.json').write_text(json.dumps({'address_after':address_after,
                'seed':seed,'user_data':user_data,'native_events':actual[0],
                'candidate_events':candidate[0],'native_result':actual[1],
                'candidate_result':candidate[1],'native_sp':actual[2],
                'candidate_sp':candidate[2]},indent=2)+'\n')
            raise AssertionError((address_after,seed,user_data))
        cases+=1
receipt={'status':'PASS_NATIVE_GLYPH_BITMAP_VALID','cases':cases,
         'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
         'native_blob_sha256':hashlib.sha256(blob).hexdigest(),
         'bounds':'Callback arguments, lock order, return, full glyph/font memory, SP.',
         'limits':['Null font assertion not dynamically compared.',
                   'No bitmap callback implementation or hardware proof.']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],cases)
