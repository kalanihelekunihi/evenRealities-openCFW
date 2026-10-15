#!/usr/bin/env python3
"""Check the upstream renderer's native entry and clip-reject behavior."""
from pathlib import Path
import hashlib,json,struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *

repo=Path(__file__).resolve().parents[6]
root=repo/'g2'
here=Path(__file__).resolve().parent
obj=root/'build/c-firmware/root-main-lvgl-label-source-round813/lv_draw_label_upstream.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
undefined=[x.split()[-1] for x in subprocess.check_output(
    ['arm-none-eabi-nm','-u',str(obj)],text=True).splitlines()]
with tempfile.TemporaryDirectory() as tmp:
    elf_path=Path(tmp)/'label.elf'
    subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000',
                    '-e','audio_uart_lv_draw_label_48a0be']+
                    ['--defsym='+n+'='+hex(0x2001f000 if n=='lv_global' else
                                          (0x180001 if n=='lv_area_intersect' else 0x180011))
                     for n in undefined]+[str(obj),'-o',str(elf_path)],
                   check=True,stderr=subprocess.DEVNULL)
    with elf_path.open('rb') as fp:
        elf=ELFFile(fp)
        segments=[(p['p_vaddr'],p.data()) for p in elf.iter_segments()
                  if p['p_type']=='PT_LOAD']
        symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
    task,descriptor,area=0x20012000,0x20013000,0x20014000
    def run(native,seed):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
        u.mem_map(0x100000,0x100000)
        for a,data in segments:u.mem_write(a,data)
        u.mem_map(0x20000000,0x200000)
        for p in (task,descriptor,area):u.mem_write(p,bytes([seed])*0x100)
        events=[]
        target=0x450bcc if native else 0x180000
        def hook(emu,address,size,user):
            if address!=target:return
            events.append((emu.reg_read(UC_ARM_REG_R1),emu.reg_read(UC_ARM_REG_R2)))
            emu.reg_write(UC_ARM_REG_R0,0)
            emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        u.reg_write(UC_ARM_REG_CPSR,0x33)
        for reg,val in ((UC_ARM_REG_R0,task),(UC_ARM_REG_R1,descriptor),
                        (UC_ARM_REG_R2,area),(UC_ARM_REG_R3,0x20015001),
                        (UC_ARM_REG_SP,0x201ff000),(UC_ARM_REG_LR,0x600001)):
            u.reg_write(reg,val)
        entry=0x48a0be if native else symbols['audio_uart_lv_draw_label_48a0be']
        u.emu_start(entry|1,0x600000,count=150)
        assert u.reg_read(UC_ARM_REG_PC)==0x600000
        return (events,u.reg_read(UC_ARM_REG_SP),
                bytes(u.mem_read(task,0x100)),bytes(u.mem_read(descriptor,0x100)),
                bytes(u.mem_read(area,0x100)))
    for seed in (0,1,0x5a,0xff):
        actual=run(True,seed);candidate=run(False,seed)
        if actual!=candidate:
            raise AssertionError((seed,actual[0],candidate[0],actual[1],candidate[1]))
receipt={'status':'PASS_LVGL_LABEL_CLIP_REJECT','cases':4,
         'source_commit':'344c7c318047b7348e1be8572a9fd4260c251cfa',
         'source_object_sha256':hashlib.sha256(obj.read_bytes()).hexdigest(),
         'native_blob_sha256':hashlib.sha256(blob).hexdigest(),
         'bounds':'Clip reject call arguments and full task/descriptor/area guards plus SP.',
         'limits':['Only clip-reject path; all deeper layout, text, glyph, decoration, and callback paths remain unverified.',
                   'Other lower calls linked to non-executed stubs.']}
(here/'clip-reject-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],4)
