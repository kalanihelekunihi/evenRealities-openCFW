#!/usr/bin/env python3
"""Compare Apollo Ambiq image core lower calls on untransformed draw paths."""
from pathlib import Path
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UcError, UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_SP, UC_ARM_REG_S0, UC_ARM_REG_S1, UC_ARM_REG_S2, UC_ARM_REG_S3, UC_ARM_REG_S4, UC_ARM_REG_S5, UC_ARM_REG_S6, UC_ARM_REG_S7

root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/image_core.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
lower=[('audio_queue_copy_bytes',0x439be4),
 ('audio_uart_ambiq_color_resolve_4b06a8',0x4b06a8),
 ('audio_uart_ambiq_decode_image_4b0f50',0x4b0f50),
 ('audio_uart_ambiq_image_options_4b0d38',0x4b0d38),
 ('audio_uart_ambiq_mask_options_4b0ea6',0x4b0ea6),
 ('audio_uart_ambiq_image_color_513e4c',0x513e4c),
 ('audio_uart_nema_stencil_save_52266e',0x52266e),
 ('audio_uart_nema_stencil_restore_5226b2',0x5226b2),
 ('display_driver_gpu_enable_4b0748',0x4b0748),
 ('display_driver_gpu_position_4b1b48',0x4b1b48),
 ('audio_uart_nema_cl_get_bound_5144fa',0x5144fa),
 ('audio_uart_nema_cl_submit_514cf2',0x514cf2),
 ('audio_uart_nema_cl_wait_514d00',0x514d00),
 ('audio_uart_nema_cl_rewind_514384',0x514384),
 ('audio_uart_lv_image_decoder_close_48908c',0x48908c),
 ('audio_uart_lvgl_log',0x44d25c),
 ('audio_uart_lv_area_width_451598',0x451598),
 ('audio_uart_lv_area_height_4515a4',0x4515a4),
 ('audio_uart_checksum_copy',0x439c04),
 ('audio_uart_lv_rect_set_width_450b6c',0x450b6c),
 ('audio_uart_lv_rect_set_height_450b76',0x450b76),
 ('audio_uart_lv_area_intersect_450bcc',0x450bcc),
 ('audio_uart_nema_matrix_identity_561810',0x561810),
 ('audio_uart_nema_matrix_translate_561856',0x561856),
 ('audio_uart_nema_matrix_scale_5618b8',0x5618b8),
 ('audio_uart_nema_matrix_rotate_561964',0x561964),
 ('audio_uart_nema_matrix_shear_561902',0x561902),
 ('audio_uart_nema_matrix_copy_561830',0x561830),
 ('audio_uart_nema_matrix_finalize_561b38',0x561b38),
 ('audio_uart_nema_matrix_upload_5226e8',0x5226e8),
 ('audio_uart_nema_matrix_point_561ad4',0x561ad4),
 ('audio_uart_nema_draw_quad_522db4',0x522db4)]
with tempfile.TemporaryDirectory() as directory:
    stub=Path(directory)/'lower.c'
    stub.write_text('typedef unsigned u32;\n'+'\n'.join(
        f'u32 {name}(u32 a,u32 b,u32 c,u32 d,u32 e,u32 f,u32 g,u32 h){{return 0;}}'
        for name,_ in lower))
    image=Path(directory)/'core.elf'
    flags=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
           '-mfpu=fpv4-sp-d16','-mfloat-abi=hard','-std=c11','-ffreestanding',
           '-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000']
    subprocess.run(flags+[str(source),str(stub),'-o',str(image)],
                   check=True,capture_output=True)
    with image.open('rb') as file:
        elf=ELFFile(file)
        segments=[(segment['p_vaddr'],segment.data()) for segment in elf.iter_segments()
                  if segment['p_type']=='PT_LOAD']
        symbols={sym.name:sym['st_value']
                 for sym in elf.get_section_by_name('.symtab').iter_symbols()}

    def run(compiled,main_ok,mask_mode,fmt,blend,alpha,stencil,tile,
            transformed=False,small_tile=False):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
        uc.mem_map(0x100000,0x200000);uc.mem_map(0x20000000,0x100000)
        for address,data in segments:uc.mem_write(address,data)
        unit,d,area,layer,source_ptr,mask_ptr,buffer,mask_buffer=tuple(
            0x20005000+i*0x1000 for i in range(8))
        desc=bytearray(108);width,height=(3,4) if small_tile else (16,16)
        def put(off,val):desc[off:off+4]=val.to_bytes(4,'little')
        put(0x1c,source_ptr);put(0x20,fmt<<8);put(0x24,(height<<16)|width)
        put(0x30,10 if transformed else 0)
        put(0x34,0x100);put(0x38,0x100)
        if small_tile:
            for off,val in ((0x58,10),(0x5c,20),(0x60,12),(0x64,23)):
                put(off,val)
        put(0x68,mask_ptr if mask_mode else 0)
        desc[0x4c:0x4f]=bytes([0x11,0x22,0x33]);desc[0x4f]=alpha
        desc[0x50]=0x80;desc[0x51]=blend|(8 if stencil else 0)|(16 if tile else 0)
        uc.mem_write(d,bytes(desc))
        uc.mem_write(unit+72,layer.to_bytes(4,'little'))
        uc.mem_write(unit+76,(0x77).to_bytes(4,'little'))
        uc.mem_write(layer+4,(2).to_bytes(4,'little'))
        uc.mem_write(layer+8,(3).to_bytes(4,'little'))
        uc.mem_write(layer+20,(16).to_bytes(4,'little'))
        for i,value in enumerate((10,20,25,35)):
            uc.mem_write(area+4*i,value.to_bytes(4,'little'))
        uc.mem_write(buffer+4,((height<<16)|width).to_bytes(4,'little'))
        uc.mem_write(mask_buffer+4,(((height+1 if mask_mode==3 else height)<<16)|width).to_bytes(4,'little'))
        calls=[];decode_outputs=[]
        def word(emu,addr):return int.from_bytes(emu.mem_read(addr,4),'little')
        def rect(emu,addr):return tuple(word(emu,addr+4*i) for i in range(4))
        def cstr(emu,addr):return bytes(emu.mem_read(addr,180)).split(b'\0',1)[0]
        def hook(emu,address,size,user):
            name=next(name for name,native in lower
                      if (symbols[name]&~1 if compiled else native)==address)
            r=[emu.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,
                                               UC_ARM_REG_R2,UC_ARM_REG_R3)]
            sp=emu.reg_read(UC_ARM_REG_SP);value=0
            if name==lower[0][0] or name==lower[18][0]:
                calls.append(('copy',r[2],bytes(emu.mem_read(r[1],r[2]))))
                emu.mem_write(r[0],bytes(emu.mem_read(r[1],r[2])));value=r[0]
            elif name==lower[1][0]:
                calls.append(('color',r[0]&0xffffff,r[1]));value=0x123
            elif name==lower[2][0]:
                is_mask=r[0]==mask_ptr
                calls.append(('decode',is_mask,r[1],r[3]))
                decode_outputs.append((r[2],is_mask))
                emu.mem_write(r[2],bytes(76))
                emu.mem_write(r[2]+44,(mask_buffer if is_mask else buffer).to_bytes(4,'little'))
                value=1 if (mask_mode>=2 if is_mask else main_ok) else 0
            elif name==lower[3][0]:
                calls.append(('options',r[0]==buffer,r[1],r[2]));value=0x200
            elif name==lower[4][0]:
                calls.append(('mask_options',r[0]==mask_buffer,r[1]));value=0x400
            elif name==lower[5][0]:calls.append(('image_color',r[0]));value=0
            elif name==lower[6][0]:calls.append(('save',tuple(r)));value=0x66
            elif name==lower[7][0]:calls.append(('restore',r[0]));value=0
            elif name==lower[8][0]:calls.append(('enable',r[0],r[1]));value=0
            elif name==lower[9][0]:calls.append(('position',r[0],r[1]));value=0
            elif name==lower[10][0]:calls.append(('get_command',));value=0x88
            elif name in (lower[11][0],lower[12][0],lower[13][0]):
                calls.append((name,r[0]));value=0
            elif name==lower[14][0]:
                calls.append(('close',next((is_mask for ptr,is_mask in decode_outputs if ptr==r[0]),None)))
            elif name==lower[15][0]:
                calls.append(('log',r[0],cstr(emu,r[1]),r[2],cstr(emu,r[3]),cstr(emu,word(emu,sp))))
            elif name==lower[16][0]:
                calls.append(('width',r[0]==area,r[0]==d+0x58,rect(emu,r[0])))
                a=rect(emu,r[0]);value=(a[2]-a[0]+1)&0xffffffff
            elif name==lower[17][0]:
                calls.append(('height',r[0]==area,r[0]==d+0x58,rect(emu,r[0])))
                a=rect(emu,r[0]);value=(a[3]-a[1]+1)&0xffffffff
            elif name==lower[19][0]:
                calls.append(('set_width',r[1]));emu.mem_write(r[0]+8,((word(emu,r[0])+r[1]-1)&0xffffffff).to_bytes(4,'little'))
            elif name==lower[20][0]:
                calls.append(('set_height',r[1]));emu.mem_write(r[0]+12,((word(emu,r[0]+4)+r[1]-1)&0xffffffff).to_bytes(4,'little'))
            elif name==lower[21][0]:
                tile_rect=rect(emu,r[1]);calls.append(('intersect',tile_rect,rect(emu,r[2])))
                value=int(not(tile_rect[2]<10 or tile_rect[0]>25 or tile_rect[3]<20 or tile_rect[1]>35))
            elif name==lower[22][0]:
                calls.append(('matrix_identity',));emu.mem_write(r[0],bytes(36))
            elif name in (lower[23][0],lower[24][0],lower[25][0],lower[26][0]):
                f=(emu.reg_read(UC_ARM_REG_S0),emu.reg_read(UC_ARM_REG_S1))
                calls.append((name,f if name!=lower[25][0] else f[:1]))
            elif name==lower[27][0]:
                calls.append(('matrix_copy',));emu.mem_write(r[0],bytes(emu.mem_read(r[1],36)))
            elif name==lower[28][0]:calls.append(('matrix_finalize',))
            elif name==lower[29][0]:calls.append(('matrix_upload',))
            elif name==lower[30][0]:
                calls.append(('matrix_point',word(emu,r[1]),word(emu,r[2])))
            elif name==lower[31][0]:
                regs=(UC_ARM_REG_S0,UC_ARM_REG_S1,UC_ARM_REG_S2,UC_ARM_REG_S3,
                      UC_ARM_REG_S4,UC_ARM_REG_S5,UC_ARM_REG_S6,UC_ARM_REG_S7)
                calls.append(('draw_quad',tuple(emu.reg_read(z) for z in regs)))
            else:raise AssertionError(('unexpected lower',name))
            emu.reg_write(UC_ARM_REG_R0,value)
            emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
        for name,native in lower:
            target=symbols[name]&~1 if compiled else native
            uc.hook_add(UC_HOOK_CODE,hook,begin=target,end=target)
        uc.reg_write(UC_ARM_REG_SP,0x200ff000);uc.reg_write(UC_ARM_REG_LR,0x600001)
        for reg,value in ((UC_ARM_REG_R0,unit),(UC_ARM_REG_R1,d),(UC_ARM_REG_R2,area)):
            uc.reg_write(reg,value)
        start=symbols['audio_uart_ambiq_draw_image_core_53f548'] if compiled else 0x53f548
        try:uc.emu_start(start|1,0x600000,count=3000);terminal='return'
        except UcError:terminal='fault'
        return calls,terminal

    cases=0
    for main_ok in (0,1):
     for mask_mode in (0,1,2,3):
      for fmt in (6,11,14,20):
       for blend in (0,1):
        for alpha in (2,3):
         for stencil in (False,True):
          for tile in (False,True):
           args=(main_ok,mask_mode,fmt,blend,alpha,stencil,tile)
           native=run(False,*args);candidate=run(True,*args)
           assert native==candidate,(args,native,candidate)
           cases+=1
    print('PASS_AMBIQ_IMAGE_CORE_NATIVE_BASIC',cases)
    extra=0
    for transformed,small_tile in ((True,False),(False,True)):
     for main_ok,mask_mode,stencil in ((0,0,False),(1,0,False),(1,2,True)):
      args=(main_ok,mask_mode,11,0,3,stencil,small_tile,transformed,small_tile)
      native=run(False,*args);candidate=run(True,*args)
      assert native==candidate,(args,native,candidate)
      extra+=1
    print('PASS_AMBIQ_IMAGE_CORE_NATIVE_EXTRA',extra)
