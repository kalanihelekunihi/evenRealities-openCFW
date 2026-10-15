#!/usr/bin/env python3
"""Compare native and C FreeType outline scale on valid descriptor inputs."""
from pathlib import Path
import hashlib,itertools,json,struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *

root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/font_outline_scale.c'
out=Path(__file__).resolve().parent/'root-font-outline-scale-round809';out.mkdir(exist_ok=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
font,descriptor,face=0x20012000,0x20013000,0x20014000
W=lambda n:struct.pack('<I',n&0xffffffff)
with tempfile.TemporaryDirectory() as tmp:
    elf_path=Path(tmp)/'scale.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                    '-O2','-ffreestanding','-fno-builtin','-nostdlib',
                    '-Wl,-Ttext=0x110000','-Wl,--defsym=audio_uart_lvgl_log=0x180001',
                    str(source),'-o',str(elf_path)],check=True)
    with elf_path.open('rb') as fp:
        elf=ELFFile(fp)
        segments=[(seg['p_vaddr'],seg.data()) for seg in elf.iter_segments()
                  if seg['p_type']=='PT_LOAD']
        symbols={sym.name:sym['st_value'] for sym in elf.get_section_by_name('.symtab').iter_symbols()}
    def run(original,metric,divisor,seed):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
        uc.mem_map(0x100000,0x100000)
        for address,data in segments:uc.mem_write(address,data)
        uc.mem_map(0x20000000,0x200000)
        for address in (font,descriptor,face):uc.mem_write(address,bytes([seed])*0x100)
        uc.mem_write(font+0x18,W(descriptor))
        uc.mem_write(descriptor,W(0x5f5f4654))
        uc.mem_write(descriptor+0x28,W(metric))
        uc.mem_write(descriptor+0x34,W(face))
        uc.mem_write(face+8,W(divisor))
        uc.reg_write(UC_ARM_REG_CPSR,0x33)
        uc.reg_write(UC_ARM_REG_R0,font)
        uc.reg_write(UC_ARM_REG_SP,0x201ff000)
        uc.reg_write(UC_ARM_REG_LR,0x600001)
        entry=0x529bfe if original else symbols['audio_uart_ambiq_font_units_529bfe']
        uc.emu_start(entry|1,0x600000,count=100)
        assert uc.reg_read(UC_ARM_REG_PC)==0x600000
        return (uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_SP),
                bytes(uc.mem_read(font,0x100)),bytes(uc.mem_read(descriptor,0x100)),
                bytes(uc.mem_read(face,0x100)))
    cases=0
    for metric,divisor,seed in itertools.product(
        (0,1,64,1024,0xffff,0x7fffffff,0xffffffff),
        (0,1,2,64,127,65535,0xffffffff),(0,0x5a)):
        actual=run(True,metric,divisor,seed)
        candidate=run(False,metric,divisor,seed)
        if actual!=candidate:
            (out/'mismatch.json').write_text(json.dumps({'metric':metric,'divisor':divisor,'seed':seed,
                'native_result':actual[0],'candidate_result':candidate[0],
                'native_sp':actual[1],'candidate_sp':candidate[1]},indent=2)+'\n')
            raise AssertionError((metric,divisor,seed))
        cases+=1
receipt={'status':'PASS_NATIVE_FONT_OUTLINE_SCALE_VALID','cases':cases,
         'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
         'native_blob_sha256':hashlib.sha256(blob).hexdigest(),
         'bounds':'Valid magic and pointers; result, SP, and entire fixture memory equal.',
         'limits':['Assertion diagnostics and fail-stop branches are source-backed but not dynamically compared.',
                   'No runtime font lifecycle or hardware proof.']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],cases)
