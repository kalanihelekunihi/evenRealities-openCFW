#!/usr/bin/env python3
"""Compare image draw descriptor initialization against pinned Apollo stock."""
import hashlib
import itertools
import json
import struct
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_lv_image_draw_dsc_init_452a34.c'
OUT = G2 / 'build/c-firmware/20261016/main-lv-image-dsc-init-452a34'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PIN = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
CALLS = [('audio_uart_lv_style_image_opa_4524a4',0x4524a4),('audio_uart_lv_draw_task_opacity_452df0',0x452df0),('audio_uart_lv_area_width_451598',0x451598),('audio_uart_lv_area_height_4515a4',0x4515a4),('audio_uart_lv_style_image_recolor_4524b0',0x4524b0),('audio_uart_lv_style_image_recolor_opa_4524d0',0x4524d0),('audio_uart_lv_draw_color_variant_452e68',0x452e68),('audio_uart_page_441068',0x441068),('audio_queue_copy_bytes',0x439be4),('audio_uart_lv_style_image_blend_45260a',0x45260a)]
OBJ, DSC = 0x20001000, 0x20002000

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def build():
    OUT.mkdir(parents=True, exist_ok=True)
    obj, elf = OUT/'oracle.o', OUT/'oracle.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
    subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={n}=0x{a|1:x}' for n,a in CALLS],str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
    with elf.open('rb') as f:
        e=ELFFile(f)
        seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
        symbols={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
    return elf,seg,symbols

def main():
    blob=PAYLOAD.read_bytes()[32:]
    assert hashlib.sha256(blob).hexdigest()==PIN
    elf,seg,sym=build()
    cuts={a:i for i,(_,a) in enumerate(CALLS)}
    def run(compiled, part, opacity, layer, width, height, color, recolor_opa, variant, rgb, blend, seed):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
        u.mem_map(0x100000,0x100000)
        for a,data in seg:u.mem_write(a,data)
        u.mem_map(0x20000000,0x100000)
        u.mem_write(OBJ,bytes((i*3+7)&255 for i in range(128)))
        u.mem_write(DSC,bytes((i*17+seed)&255 for i in range(0x70)))
        trace=[]
        values=(opacity,layer,width,height,color,recolor_opa,variant,rgb,0,blend)
        def hook(cpu,pc,size,_):
            if pc not in cuts:return
            i=cuts[pc]
            regs=[cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
            if i==6:
                fifth=struct.unpack('<I',cpu.mem_read(cpu.reg_read(A.UC_ARM_REG_SP),4))[0]
                trace.append((i,regs[0],regs[1],regs[2],regs[3],fifth))
            elif i==8:
                trace.append((i,regs[0],bytes(cpu.mem_read(regs[1],3)),regs[2]))
                cpu.mem_write(regs[0],bytes(cpu.mem_read(regs[1],regs[2])))
            else:trace.append((i,*regs[:3 if i in (1,7) else 2 if i in (0,4,5,9) else 1]))
            cpu.reg_write(A.UC_ARM_REG_R0,values[i]&0xffffffff)
            cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        u.reg_write(A.UC_ARM_REG_SP,0x200ff000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
        for r,v in ((A.UC_ARM_REG_R0,OBJ),(A.UC_ARM_REG_R1,part),(A.UC_ARM_REG_R2,DSC),(A.UC_ARM_REG_R3,0x1234abcd)) :u.reg_write(r,v)
        entry=sym['audio_uart_lv_obj_init_draw_image_452a34'] if compiled else 0x452a34
        u.emu_start(entry|1,0x600000,count=1000)
        return trace,bytes(u.mem_read(DSC,0x70)),u.reg_read(A.UC_ARM_REG_R0)
    cases=[]
    for part,opacity,layer,seed in itertools.product((0,1,0x40000),(0,1,2,3,128,255),(0,1,100,252,253,255),(0,57)):
        cases.append((part,opacity,layer,13,-7,0x12345678,0xab,0x9abcdef0,0x11223344,0x0f,seed))
    for idx,args in enumerate(cases):
        a,b=run(False,*args),run(True,*args)
        if a!=b:
            diff=[(j,x,y) for j,(x,y) in enumerate(zip(a[1],b[1])) if x!=y]
            raise RuntimeError(f'mismatch {idx} {args} traces={a[0]} vs {b[0]} bytes={diff[:12]} ret={a[2]:x}/{b[2]:x}')
    result={'status':'PASS_EXPERIMENTAL_MAIN_LV_IMAGE_DSC_INIT_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PIN,'oracle_elf_sha256':sha(elf),'cases':len(cases),'scope':'Descriptor bytes, lower call sequence and arguments, return value across opacity, part and layer boundaries','limits':['Lower provider effects isolated; final placement remains open.']}
    path=OUT/'oracle-receipt.json';path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'],len(cases),sha(path))
if __name__=='__main__': main()
