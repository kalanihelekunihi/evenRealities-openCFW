#!/usr/bin/env python3
"""Public-entry stock/source comparison for three codec.host control wrappers."""
from pathlib import Path
import hashlib, itertools, json, struct, subprocess
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2,
    UC_ARM_REG_R3, UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC)
from elftools.elf.elffile import ELFFile

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
IMAGE=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
blob=IMAGE.read_bytes(); assert hashlib.sha256(blob).hexdigest()==SHA
stock_bodies={0x57d6b4:(208,'56540991b704b13032b8ac121d329c6ebb0caeb99e6b95cf67aef1dde91bf230'),
              0x57d794:(204,'20a4386b6eee6fe5ff07c3647e1a23e26647c1678352efc16e6c5f19d6640a85'),
              0x57d93c:(224,'03cab817428fe78aaec4fcaf086af61577f32048e966fc75b94de75462bf152f')}
for address,(size,digest) in stock_bodies.items():
    assert hashlib.sha256(blob[address-0x437fe0:address-0x437fe0+size]).hexdigest()==digest
compiler=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
elf_path=Path('/tmp/audio_dsp_control.elf')
providers={'audio_log_flags':0x43d0cf,'audio_dmic_request':0x57ce79,
           'audio_i2s_output_request':0x57d025,'audio_log_extended':0x43d575,
           'audio_log_simple':0x43ce9f}
flags=(['-mcpu=cortex-m55','-mthumb','-O0','-ffreestanding','-fno-builtin','-nostdlib',
        '-Wl,-Ttext=0x10001000','-Wl,-e,audio_dsp_enable'] +
       [f'-Wl,--defsym={name}={address:#x}' for name,address in providers.items()])
subprocess.run([str(compiler),*flags,str(HERE/'dsp_control.c'),'-o',str(elf_path)],check=True)
with elf_path.open('rb') as stream:
    elf=ELFFile(stream)
    symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
    segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']

def run(entry,enable,status,response,log_bits,source):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
    u.mem_map(0x437000,((len(blob)+0xfe0+0xfff)//0x1000)*0x1000)
    u.mem_write(0x437fe0,blob)
    u.mem_map(0x10000000,0x40000)
    for address,data in segments:u.mem_write(address,data)
    u.mem_map(0x20000000,0x800000)
    u.reg_write(UC_ARM_REG_SP,0x207ff000)
    u.reg_write(UC_ARM_REG_LR,0x10000001)
    u.reg_write(UC_ARM_REG_R0,enable)
    calls=[]
    def word(address):return struct.unpack('<I',u.mem_read(address,4))[0]
    def string(address):
        assert address
        out=bytearray()
        for i in range(256):
            b=u.mem_read(address+i,1)[0]
            if b==0:return out.decode('ascii')
            out.append(b)
        raise AssertionError(hex(address))
    def hook(emu,pc,size,data):
        regs=[emu.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
        sp=emu.reg_read(UC_ARM_REG_SP)
        if pc in (0x57ce78,0x57d024):
            width=2 if pc==0x57ce78 else 1
            initial=int.from_bytes(emu.mem_read(regs[1],width),'little')
            calls.append(['dmic' if width==2 else 'i2s',regs[0],regs[2],initial])
            emu.mem_write(regs[1],response.to_bytes(width,'little'))
            emu.reg_write(UC_ARM_REG_R0,status & 0xffffffff)
            emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
        elif pc==0x43d0ce:
            calls.append(['flags'])
            emu.reg_write(UC_ARM_REG_R0,log_bits)
            emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
        elif pc==0x43d574:
            line=word(sp); fmt=string(word(sp+4))
            args=[word(sp+8),word(sp+12)] if regs[0]==1 else ([string(word(sp+8))] if '%s' in fmt else [])
            calls.append(['extended',regs[0],string(regs[1]),string(regs[2]),string(regs[3]),line,fmt,args])
            emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
        elif pc==0x43ce9e:
            fmt=string(regs[1]); assert fmt==string(regs[2])
            args=[regs[3],word(sp)] if 'failed' in fmt else ([string(regs[3])] if '%s' in fmt else [])
            calls.append(['simple',regs[0],fmt,args])
            emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start((symbols[entry] if source else {'audio_dsp_enable':0x57d6b4,
         'audio_dsp_disable':0x57d794,'audio_dsp_gate':0x57d93c}[entry])|1,
         0x10000000,count=30000)
    assert u.reg_read(UC_ARM_REG_PC)==0x10000000
    return dict(result=u.reg_read(UC_ARM_REG_R0),calls=calls)

rows=[]
for entry in ('audio_dsp_enable','audio_dsp_disable','audio_dsp_gate'):
  enables=(0,1,0x100,0x1ff) if entry=='audio_dsp_gate' else (0,)
  responses=(0,1,2,0xff) if entry=='audio_dsp_gate' else (0,1,2,0xffff)
  for enable,status,response,log_bits in itertools.product(enables,(0,1,0xffffffff),responses,(0,1,2,4,7)):
    original=run(entry,enable,status,response,log_bits,False)
    compiled=run(entry,enable,status,response,log_bits,True)
    assert original==compiled,(entry,enable,status,response,log_bits,original,compiled)
    rows.append(dict(entry=entry,enable=hex(enable),status=hex(status),response=hex(response),
                     log_bits=hex(log_bits),result=hex(original['result']),calls=original['calls']))
receipt=dict(status='PASS',cases=len(rows),image_sha256=SHA,stock_bodies={hex(k):v[1] for k,v in stock_bodies.items()},
             source_sha256=hashlib.sha256((HERE/'dsp_control.c').read_bytes()).hexdigest(),
             elf_sha256=hashlib.sha256(elf_path.read_bytes()).hexdigest(),compiler=str(compiler),
             compiler_sha256=hashlib.sha256(compiler.read_bytes()).hexdigest(),flags=flags,provider_bindings={k:hex(v) for k,v in providers.items()},
             rows=rows,limits='Driver responses/status and logger flags synthetic; lower calls intercepted at public ABI, logger formatting/output not executed; no hardware or scheduler.')
(HERE/'control-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS',len(rows))
