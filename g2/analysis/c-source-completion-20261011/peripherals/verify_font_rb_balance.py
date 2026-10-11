"""Bounded native/compiled C RB transition comparison on controlled 32-bit trees."""
from pathlib import Path
import struct, subprocess, tempfile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP, UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
    source=ROOT/'components/audio/uart_thread_source_candidate/display_font_rb_balance.c'
    shim=Path(d)/'shim.c'
    shim.write_text('#include <stdint.h>\nvoid audio_uart_lvgl_log(uint32_t a,const char*b,uint32_t c,const char*d,const char*e,...){(void)a;(void)b;(void)c;(void)d;(void)e;}\n')
    elf=Path(d)/'balance.elf'; binary=Path(d)/'balance.bin'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_rb_fix_insert',str(source),str(shim),'-o',str(elf)],check=True)
    symbols=dict((parts[2],int(parts[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(parts:=line.split())==3)
    subprocess.run(['arm-none-eabi-objcopy','--only-section=.text','-O','binary',str(elf),str(binary)],check=True)
    COMPILED=binary.read_bytes()
TREE=0x20010000
NODES=[0x20011000+0x20*i for i in range(5)]
RETURN=0x600000

def image(spec):
    tree=struct.pack('<III',NODES[spec['root']],0,0)
    nodes=b''
    for i in range(5):
        n=spec['nodes'].get(i,(None,None,None,1))
        nodes+=struct.pack('<IIIB3xI',*(NODES[v] if v is not None else 0 for v in n[:3]),n[3],0)
        nodes+=b'\0'*12
    return tree,nodes

def run(addr,args,tree,nodes):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
    u.mem_map(0x100000,0x10000);u.mem_write(0x100000,COMPILED)
    u.mem_map(0x20000000,0x100000)
    u.mem_write(TREE,tree);u.mem_write(NODES[0],nodes)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,RETURN|1)
    for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),args):u.reg_write(reg,value)
    
    try:u.emu_start(addr|1,RETURN,count=10000)
    except Exception:
        print("FAULT",hex(addr),hex(u.reg_read(UC_ARM_REG_PC)))
        raise
    return bytes(u.mem_read(TREE,12)),bytes(u.mem_read(NODES[0],len(nodes)))

cases={
    'insert_LL': ('insert',{'root':0,'nodes':{0:(None,1,None,1),1:(0,2,None,0),2:(1,None,None,0)}},2),
    'insert_LR': ('insert',{'root':0,'nodes':{0:(None,1,None,1),1:(0,None,2,0),2:(1,None,None,0)}},2),
    'insert_RR': ('insert',{'root':0,'nodes':{0:(None,None,1,1),1:(0,None,2,0),2:(1,None,None,0)}},2),
    'insert_RL': ('insert',{'root':0,'nodes':{0:(None,None,1,1),1:(0,2,None,0),2:(1,None,None,0)}},2),
    'insert_recolor': ('insert',{'root':0,'nodes':{0:(None,1,3,1),1:(0,2,None,0),2:(1,None,None,0),3:(0,None,None,0)}},2),
    'remove_left_black_sibling':('remove',{'root':0,'nodes':{0:(None,None,1,1),1:(0,None,None,1)}},None),
    'remove_right_black_sibling':('remove',{'root':0,'nodes':{0:(None,1,None,1),1:(0,None,None,1)}},None),
    'remove_left_red_sibling':('remove',{'root':0,'nodes':{0:(None,None,1,1),1:(0,2,3,0),2:(1,None,None,1),3:(1,None,None,1)}},None),
    'remove_right_red_sibling':('remove',{'root':0,'nodes':{0:(None,1,None,1),1:(0,2,3,0),2:(1,None,None,1),3:(1,None,None,1)}},None),
}
for name,(kind,spec,node) in cases.items():
    tree,nodes=image(spec)
    if kind=='insert':
        native=0x5c38cc;source=symbols['audio_uart_font_rb_fix_insert'];args=(TREE,NODES[node])
    else:
        native=0x5c3976;source=symbols['audio_uart_font_rb_fix_remove'];args=(TREE,0,NODES[0])
    a=run(native,args,tree,nodes)
    b=run(source,args,tree,nodes)
    if a!=b:
        for label,x,y in zip(('tree','nodes'),a,b):
            if x!=y:
                print(name,label,'native',x.hex(),'compiled',y.hex())
        raise SystemExit(1)
    print('PASS',name)
