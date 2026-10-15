#!/usr/bin/env python3
"""Direct native/C checks for five Apollo Nema state and paint setters."""
from pathlib import Path
import hashlib, itertools, json, struct, subprocess, tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import *

root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/vector_path_state.c'
out=Path(__file__).resolve().parent/'root-vector-path-state-round808'
out.mkdir(exist_ok=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native={'command':0x51566c,'mode':0x515634,'width':0x515640,'select':0x5150ea,'color':0x515136}
names={'command':'audio_uart_ambiq_vector_command_51566c',
       'mode':'audio_uart_ambiq_vector_fill_mode_515634',
       'width':'audio_uart_ambiq_vector_stroke_width_515640',
       'select':'audio_uart_ambiq_vector_path_select_5150ea',
       'color':'audio_uart_ambiq_vector_path_color_515136'}
context_cell=0x20074f04
context=0x20010000
path=0x20011000
helper=out/'selected-error-fixture.c'
helper.write_text('#include <stdint.h>\nextern volatile uint32_t audio_uart_nema_vg_context_cell;\n'
                  'void audio_uart_nema_vg_set_error_51565c(uint32_t e) {'
                  'volatile uint8_t *c=(void *)(uintptr_t)audio_uart_nema_vg_context_cell;'
                  '*(volatile uint32_t *)(c+0x80u)|=e;}\n')
with tempfile.TemporaryDirectory() as tmp:
    elf_path=Path(tmp)/'state.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                    '-mfpu=fpv4-sp-d16','-mfloat-abi=softfp','-O2','-ffreestanding',
                    '-fno-builtin','-nostdlib','-Wl,-Ttext=0x110000',
                    '-Wl,--defsym=audio_uart_nema_vg_context_cell='+hex(context_cell),
                    str(source),str(helper),'-o',str(elf_path)],check=True)
    with elf_path.open('rb') as fp:
        elf=ELFFile(fp)
        segments=[(seg['p_vaddr'],seg.data()) for seg in elf.iter_segments()
                  if seg['p_type']=='PT_LOAD']
        symbols={sym.name:sym['st_value'] for sym in elf.get_section_by_name('.symtab').iter_symbols()}

    def run(which,original,a,b,seed):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        uc.mem_map(0x400000,0x400000)
        uc.mem_write(0x438000,blob)
        uc.mem_map(0x100000,0x100000)
        for address,data in segments:uc.mem_write(address,data)
        uc.mem_map(0x20000000,0x200000)
        uc.mem_write(context_cell,struct.pack('<I',context))
        uc.mem_write(context,bytes([seed])*0x400)
        uc.mem_write(path,bytes([seed^0xa5])*0x200)
        uc.reg_write(UC_ARM_REG_C1_C0_2,0xf00000)
        uc.reg_write(UC_ARM_REG_FPEXC,1<<30)
        uc.reg_write(UC_ARM_REG_CPSR,0x33)
        uc.reg_write(UC_ARM_REG_R0,a)
        uc.reg_write(UC_ARM_REG_R1,b)
        if which=='width':uc.reg_write(UC_ARM_REG_S0,a)
        uc.reg_write(UC_ARM_REG_SP,0x201ff000)
        uc.reg_write(UC_ARM_REG_LR,0x600001)
        entry=native[which] if original else symbols[names[which]]
        uc.emu_start(entry|1,0x600000,count=200)
        assert uc.reg_read(UC_ARM_REG_PC)==0x600000,(which,original)
        return (bytes(uc.mem_read(context,0x400)),bytes(uc.mem_read(path,0x200)),
                uc.reg_read(UC_ARM_REG_SP))

    cases=[]
    for which in native:
        if which in ('command','mode','width'):
            pairs=[(a,0) for a in (0,1,0x3f800000,0x7f800000,0xffffffff)]
        elif which=='select':
            pairs=list(itertools.product((0,path),(0,1,2,3,4,5,255,0xffffffff)))
        else:
            pairs=list(itertools.product((0,path),(0,1,0x12345678,0xffffffff)))
        for a,b in pairs:
            for seed in (0,0x5a):
                observed=run(which,True,a,b,seed)
                candidate=run(which,False,a,b,seed)
                if observed!=candidate:
                    mismatch={'which':which,'a':a,'b':b,'seed':seed,
                              'native_context':observed[0].hex(),
                              'candidate_context':candidate[0].hex(),
                              'native_path':observed[1].hex(),
                              'candidate_path':candidate[1].hex(),
                              'native_sp':observed[2],'candidate_sp':candidate[2]}
                    (out/'mismatch.json').write_text(json.dumps(mismatch,indent=2)+'\n')
                    raise AssertionError((which,a,b,seed))
                cases.append((which,a,b,seed))
receipt={'status':'PASS_NATIVE_VECTOR_PATH_STATE','cases':len(cases),
         'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
         'native_blob_sha256':hashlib.sha256(blob).hexdigest(),
         'functions':names,'bounds':'Full context and paint snapshots plus SP; default FPSCR only.',
         'limits':['State initialization and runtime ownership remain separate.',
                   'No whole-image or hardware proof.']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],receipt['cases'])
