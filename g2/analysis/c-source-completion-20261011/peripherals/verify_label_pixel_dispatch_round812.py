#!/usr/bin/env python3
"""Bounded native/C dispatch checks for the Apollo label pixel callback."""
from pathlib import Path
import hashlib,itertools,json,re,struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *

root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/label_pixel.c'
out=Path(__file__).resolve().parent/'root-label-pixel-dispatch-round812';out.mkdir(exist_ok=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
unit,glyph,fill,draw,gpu,fill_area=0x20012000,0x20013000,0x20014000,0x20015000,0x20016000,0x20017000
header,font,bitmap_data,glyph_area,cache=0x20018000,0x20019000,0x2001a000,0x2001b000,0x2001d000
W=lambda n:struct.pack('<I',n&0xffffffff)
with tempfile.TemporaryDirectory() as tmp:
    obj=Path(tmp)/'pixel.o';elf_path=Path(tmp)/'pixel.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                    '-O2','-ffreestanding','-fno-builtin','-c',str(source),'-o',str(obj)],check=True)
    undefined=[line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm','-u',str(obj)],text=True).splitlines()]
    addresses={}
    for name in undefined:
        match=re.search(r'_([0-9a-f]{6})$',name)
        addresses[name]=int(match.group(1),16) if match else 0x44d25c
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                    '-nostdlib','-Wl,-Ttext=0x110000']+
                    ['-Wl,--defsym='+name+'='+hex(address|1)
                     for name,address in addresses.items()]+[str(obj),'-o',str(elf_path)],
                   check=True,stderr=subprocess.DEVNULL)
    with elf_path.open('rb') as fp:
        elf=ELFFile(fp)
        segments=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD']
        symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
    hooks={a:n for n,a in addresses.items()}
    def run(original,has_glyph,has_fill,format_byte,has_area,fast,aligned,large,high,bitmap_present):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
        u.mem_map(0x100000,0x100000)
        for a,data in segments:u.mem_write(a,data)
        u.mem_map(0x20000000,0x200000)
        u.mem_map(0x80000000,0x1000)
        u.mem_write(0x80000100,bytes([0x5a])*0x100)
        for p in (unit,glyph,fill,draw,gpu,fill_area,header,font,bitmap_data,glyph_area,cache):
            u.mem_write(p,bytes([0x5a])*0x100)
        u.mem_write(unit+0x48,W(draw));u.mem_write(unit+0x4c,W(gpu))
        u.mem_write(draw+4,W(3));u.mem_write(draw+8,W(4))
        u.mem_write(fill_area,struct.pack('<4I',10,20,30,40))
        u.mem_write(glyph+8,W(glyph_area));u.mem_write(glyph+0x10,W(header))
        u.mem_write(glyph+0x2c,W(cache));u.mem_write(cache+0x10,W(0x2001c000))
        u.mem_write(glyph_area,struct.pack('<4I',10,20,30,40))
        u.mem_write(header,W(font));u.mem_write(header+6,struct.pack('<HH',512 if large else 16,8))
        u.mem_write(header+0xe,bytes([1]));u.mem_write(header+0x14,bytes([0]))
        u.mem_write(font+4,W(0x4b239d if fast else 0x4b2401))
        u.mem_write(font+0x18,W(0x80000100 if high else bitmap_data))
        u.mem_write((0x80000100 if high else bitmap_data)+0x12,struct.pack('<H',0))
        u.mem_write(glyph+4,bytes([format_byte]))
        u.mem_write(glyph+0x14,bytes([0x34,0x56,0x78,0x9a]))
        u.mem_write(fill+0x20,bytes([0xab,0x11,0x22,0x33]))
        events=[]
        def hook(emu,address,size,user):
            if address not in hooks:return
            name=hooks[address]
            regs=[emu.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,
                                             UC_ARM_REG_R2,UC_ARM_REG_R3)]
            if name=='audio_uart_ambiq_color_resolve_4b06a8':
                events.append((name,regs[0]&0xffffff,regs[1]&255))
                emu.reg_write(UC_ARM_REG_R0,0x11223344)
            elif name=='audio_uart_lvgl_log':
                events.append((name,regs[0],regs[2]))
            elif name=='audio_uart_ambiq_label_vector_dispatch_53d6ea':
                events.append((name,regs[0],regs[1]))
            elif name=='audio_uart_ambiq_image_options_init_488918':
                events.append((name,))
                emu.mem_write(regs[0],bytes([0x6d])*0x6c)
            elif name=='audio_uart_ambiq_draw_image_53f42a':
                events.append((name,regs[0],regs[2],
                               bytes(emu.mem_read(regs[1],0x6c)).hex()))
            elif name=='display_driver_gpu_mode_4b0730':
                events.append((name,regs[0],regs[1]))
            elif name=='audio_uart_ambiq_label_rect_copy_53fa94':
                events.append((name,regs[1]))
                emu.mem_write(regs[0],bytes(emu.mem_read(regs[1],16)))
            elif name=='audio_uart_ambiq_area_move_450bb2':
                events.append((name,regs[1],regs[2]))
                vals=list(struct.unpack('<4I',emu.mem_read(regs[0],16)))
                vals=[(v+regs[1 if i%2==0 else 2])&0xffffffff for i,v in enumerate(vals)]
                emu.mem_write(regs[0],struct.pack('<4I',*vals))
            elif name in ('audio_uart_lv_area_width_451598','audio_uart_lv_area_height_4515a4'):
                vals=struct.unpack('<4I',emu.mem_read(regs[0],16))
                value=((vals[2]-vals[0]+1) if 'width' in name else (vals[3]-vals[1]+1))&0xffffffff
                events.append((name,value))
                emu.reg_write(UC_ARM_REG_R0,value)
            elif name=='audio_uart_ambiq_label_fill_rectangle_4b1ab0':
                fifth=struct.unpack('<I',emu.mem_read(emu.reg_read(UC_ARM_REG_SP),4))[0]
                events.append((name,*regs,fifth))
            elif name=='audio_uart_ambiq_label_width_aligned_53faba':
                events.append((name,regs[0],regs[1]))
                emu.reg_write(UC_ARM_REG_R0,aligned)
            elif name=='audio_uart_ambiq_glyph_bitmap_4d5612':
                events.append((name,regs[0],regs[1]))
                emu.reg_write(UC_ARM_REG_R0,0x2001c000 if bitmap_present else 0)
            elif name=='audio_uart_ambiq_label_glyph_blit_53fb18':
                sp=emu.reg_read(UC_ARM_REG_SP)
                args=struct.unpack('<5I',emu.mem_read(sp,20))
                clip=struct.unpack('<4I',emu.mem_read(args[0],16))
                events.append((name,*regs,clip,*args[1:]))
            elif name=='audio_uart_nema_cl_get_bound_5144fa':
                events.append((name,))
                emu.reg_write(UC_ARM_REG_R0,0x2001e000)
            elif name in ('audio_uart_nema_cl_submit_514cf2',
                          'audio_uart_nema_cl_wait_514d00',
                          'audio_uart_nema_cl_rewind_514384'):
                events.append((name,regs[0]))
            elif name in ('g2_norflash_lock_46f65e','g2_norflash_unlock_46f674'):
                events.append((name,))
            else:events.append((name,tuple(regs)))
            emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        u.reg_write(UC_ARM_REG_CPSR,0x33)
        u.reg_write(UC_ARM_REG_R0,unit)
        u.reg_write(UC_ARM_REG_R1,glyph if has_glyph else 0)
        u.reg_write(UC_ARM_REG_R2,fill if has_fill else 0)
        u.reg_write(UC_ARM_REG_R3,fill_area if has_area else 0)
        u.reg_write(UC_ARM_REG_SP,0x201ff000)
        u.reg_write(UC_ARM_REG_LR,0x600001)
        entry=0x53fcc4 if original else symbols['audio_uart_ambiq_label_pixel_53fcc4']
        try:u.emu_start(entry|1,0x600000,count=500)
        except UcError as exc:
            raise AssertionError((original,has_glyph,has_fill,format_byte,has_area,fast,aligned,large,high,bitmap_present,
                                  hex(u.reg_read(UC_ARM_REG_PC)),events)) from exc
        assert u.reg_read(UC_ARM_REG_PC)==0x600000
        return (events,u.reg_read(UC_ARM_REG_SP),
                bytes(u.mem_read(unit,0x100)),bytes(u.mem_read(glyph,0x100)),
                bytes(u.mem_read(fill,0x100)),bytes(u.mem_read(header,0x100)))
    cases=0
    for has_glyph,has_fill,format_byte,has_area,fast,aligned,large,high,bitmap_present in itertools.product(
        (0,1),(0,1),(0,1,0x19,0x1a),(0,1),(0,1),(0,1),(0,1),(0,1),(0,1)):
        actual=run(True,has_glyph,has_fill,format_byte,has_area,fast,aligned,large,high,bitmap_present)
        candidate=run(False,has_glyph,has_fill,format_byte,has_area,fast,aligned,large,high,bitmap_present)
        if actual!=candidate:
            (out/'mismatch.json').write_text(json.dumps({'glyph':has_glyph,'fill':has_fill,
                'format':format_byte,'area':has_area,'fast':fast,'aligned':aligned,
                'large':large,'high':high,'bitmap_present':bitmap_present,'native_events':actual[0],
                'candidate_events':candidate[0],'native_sp':actual[1],
                'candidate_sp':candidate[1]},indent=2)+'\n')
            raise AssertionError((has_glyph,has_fill,format_byte,has_area,fast,aligned,large,high,bitmap_present))
        cases+=1
receipt={'status':'PASS_NATIVE_LABEL_PIXEL_BASIC_DISPATCH','cases':cases,
         'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
         'native_blob_sha256':hashlib.sha256(blob).hexdigest(),
         'bounds':'Null/glyph/fill and format 0/1/image/vector dispatch, fast/slow bitmap and fill-area; lower calls cut.',
         'limits':['Other bitmap formats and runtime allocations remain unverified.',
                   'No full native callback equivalence or hardware proof.']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],cases)
