#!/usr/bin/env python3
"""Native/C matrix shape setter checks, bounded by native M55 emulation support."""
from pathlib import Path
import hashlib,itertools,json,struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *

root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/vector_shape_matrix.c'
out=Path(__file__).resolve().parent/'root-vector-shape-matrix-round810';out.mkdir(exist_ok=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
shape,matrix,context,cell=0x20012000,0x20013000,0x20014000,0x20074f04
W=lambda n:struct.pack('<I',n&0xffffffff)
helper=out/'selected-error-fixture.c'
helper.write_text('#include <stdint.h>\nextern volatile uint32_t audio_uart_nema_vg_context_cell;\n'
                  'void audio_uart_nema_vg_set_error_51565c(uint32_t e) {'
                  'volatile uint8_t *c=(void *)(uintptr_t)audio_uart_nema_vg_context_cell;'
                  '*(volatile uint32_t *)(c+0x80u)|=e;}\n')
with tempfile.TemporaryDirectory() as tmp:
    elf_path=Path(tmp)/'shape.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                    '-mfpu=fpv5-sp-d16','-mfloat-abi=softfp','-O2',
                    '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x110000',
                    '-Wl,--defsym=audio_uart_nema_vg_context_cell='+hex(cell),
                    str(source),str(helper),'-o',str(elf_path)],check=True)
    with elf_path.open('rb') as fp:
        elf=ELFFile(fp)
        segments=[(seg['p_vaddr'],seg.data()) for seg in elf.iter_segments()
                  if seg['p_type']=='PT_LOAD']
        symbols={sym.name:sym['st_value'] for sym in elf.get_section_by_name('.symtab').iter_symbols()}
    def run(original,shape_arg,matrix_arg,words,seed):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
        uc.mem_map(0x100000,0x100000)
        for address,data in segments:uc.mem_write(address,data)
        uc.mem_map(0x20000000,0x200000)
        uc.mem_write(cell,W(context))
        for address in (shape,matrix,context):uc.mem_write(address,bytes([seed])*0x200)
        uc.mem_write(matrix,struct.pack('<9I',*words))
        uc.reg_write(UC_ARM_REG_C1_C0_2,0xf00000)
        uc.reg_write(UC_ARM_REG_FPEXC,1<<30)
        uc.reg_write(UC_ARM_REG_CPSR,0x33)
        uc.reg_write(UC_ARM_REG_R0,shape_arg)
        uc.reg_write(UC_ARM_REG_R1,matrix_arg)
        uc.reg_write(UC_ARM_REG_SP,0x201ff000)
        uc.reg_write(UC_ARM_REG_LR,0x600001)
        if original:
            loop=[3]
            def project_m55_loop(emu,address,size,user):
                if address==0x514f84:
                    emu.reg_write(UC_ARM_REG_PC,0x514f89)
                elif address==0x514f98:
                    loop[0]-=1
                    emu.reg_write(UC_ARM_REG_PC,0x514f89 if loop[0]>0 else 0x514f9d)
            uc.hook_add(UC_HOOK_CODE,project_m55_loop)
        entry=0x514f60 if original else symbols['audio_uart_ambiq_vector_shape_matrix_514f60']
        uc.emu_start(entry|1,0x600000,count=400)
        assert uc.reg_read(UC_ARM_REG_PC)==0x600000
        return (bytes(uc.mem_read(shape,0x200)),bytes(uc.mem_read(matrix,0x200)),
                bytes(uc.mem_read(context,0x200)),uc.reg_read(UC_ARM_REG_SP))
    identity=(0x3f800000,0,0,0,0x3f800000,0,0,0,0x3f800000)
    cases=0
    for shape_arg,matrix_arg,words,seed in itertools.product(
        (0,shape),(0,matrix),
        (identity,(0,)*9,(0x7fc00000,)+identity[1:],
         (0x3f800000,0,0x80000000,0,0x3f800000,0,0,0,0x3f800000),
         (0x40000000,)+identity[1:]),(0,0xa5)):
        actual=run(True,shape_arg,matrix_arg,words,seed)
        candidate=run(False,shape_arg,matrix_arg,words,seed)
        if actual!=candidate:
            (out/'mismatch.json').write_text(json.dumps({'shape':shape_arg,'matrix':matrix_arg,
                'words':words,'seed':seed,'native_shape':actual[0].hex(),
                'candidate_shape':candidate[0].hex(),'native_context':actual[2].hex(),
                'candidate_context':candidate[2].hex()},indent=2)+'\n')
            raise AssertionError((shape_arg,matrix_arg,words,seed))
        cases+=1
receipt={'status':'PASS_NATIVE_VECTOR_SHAPE_MATRIX','cases':cases,
         'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
         'native_blob_sha256':hashlib.sha256(blob).hexdigest(),
         'bounds':'Full shape, matrix and context memory plus SP; default FPSCR.',
         'limits':['Native M55 DLS/LE loop projected as three iterations because Unicorn lacks those instructions.',
                   'No shape lifecycle or hardware proof.']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],cases)
