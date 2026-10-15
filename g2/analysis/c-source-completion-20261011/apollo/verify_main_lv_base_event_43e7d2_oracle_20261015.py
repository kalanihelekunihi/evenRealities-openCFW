#!/usr/bin/env python3
"""Controlled native/C comparison for every observed LV base event branch."""
import hashlib,json,re,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2"
SRC=G2/"components/audio/uart_thread_source_candidate/display_lv_base_event_43e7d2.c"
OUT=G2/"build/c-firmware/20261015/main-lv-base-event-43e7d2"
ARGCOUNT={
 '43dd52':2,'43dd5c':2,'43dd66':2,'43de76':2,'43e046':2,'43e086':2,
 '43e0e0':2,'43e156':1,'43e1be':1,'43e442':1,'43f648':1,'43fd9e':1,
 '43fdda':1,'4405d4':2,'44d19a':1,'44d5a4':1,'44ddea':1,'44e42c':1,
 '44e442':1,'44e486':1,'44e498':1,'44e586':1,'44e67a':1,'44e9da':3,
 '44ea04':3,'44ea56':2,'44eb28':3,'450286':1,'451670':3,'4518d8':1,
 '4519a0':1,'4519fa':2,'452c66':2,'452ef8':0,'452f00':1,'452fae':1,
}
DEFAULT={"flag8":0,"flag810":0,"flag400":0,"scroll_obj":1,"state":0,
         "children":0,"direction":0,"scrolling":1,"left":0,"right":0,
         "scroll_dir":0,"x":12,"y":20,"width":16,"height":24,
         "group":0x20016000,"editing":0,"active":0x20017000,"reset":0x20017000,
         "input_type":0,"scrollbar_mode":0,"metric1":0,"metric2":0,
         "metric10":0,"metric16":0,"compass":0x1234}
def put(c,a,v):c.mem_write(a,(v&0xffffffff).to_bytes(4,"little"))
def config(code,**kwargs):return {**DEFAULT,"code":code,**kwargs}
def cases():
    result=[config(code) for code in (0,1,3,0xb,0xc,0xe,0x11,0x13,0x14,
                                      0x17,0x18,0x19,0x1a,0x1b,0x1d,0x20,
                                      0x2a,0x2c,0x31,0x32,0xff)]
    result += [config(0xb,scroll_obj=0,flag8=1,state=s) for s in (0,1)]
    result += [config(0x32,children=2),config(0x31,children=2,metric10=1),
               config(0x31,metric16=1),config(0x2a,metric1=0x3fffffff),
               config(0x2a,metric2=0x3fffffff),config(0x2a,metric10=1),
               config(0x2a,metric16=1)]
    result += [config(0x11,flag8=1,direction=d) for d in (0xa,0x11,0x12,0x13,0x14)]
    result += [config(0x11,flag810=1,scrolling=0,direction=d,scroll_dir=sd,
                      left=left,right=right) for d in (0x11,0x12,0x13,0x14)
               for sd,left,right in ((0,0,0),(3,2,2))]
    result += [config(0x13,flag400=flag,editing=edit,active=active,input_type=kind)
               for flag,edit,active,kind in ((0,0,0x20017000,0),
                                              (1,1,0x20017000,2),
                                              (0,0,0,4),(1,1,0,4))]
    result += [config(0xe,scrollbar_mode=2)]
    return result
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    blob=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest=hashlib.sha256(blob).hexdigest()
    if digest!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":raise RuntimeError("Apollo payload changed")
    with tempfile.TemporaryDirectory() as td:
        td=Path(td);obj,shim,elf=td/"event.o",td/"shim.c",td/"oracle.elf"
        subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb","-std=c11","-ffreestanding","-fno-builtin","-O2","-c",str(SRC),"-o",str(obj)],check=True)
        providers=[line.split()[-1] for line in subprocess.check_output(["arm-none-eabi-nm","-u",str(obj)],text=True).splitlines()]
        if len(providers)!=len(ARGCOUNT) or {re.search(r'_([0-9a-f]{6})$',s).group(1) for s in providers}!=set(ARGCOUNT):raise RuntimeError("event provider list changed")
        shim.write_text("#include <stdint.h>\n"+"\n".join(f"uint32_t {name}(void){{return 0;}}" for name in providers)+"\n")
        subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb","-std=c11","-ffreestanding","-fno-builtin","-O2","-nostdlib","-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_lv_base_event_43e7d2",str(SRC),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(["arm-none-eabi-nm",str(elf)],text=True).splitlines() if len(p:=line.split())==3}
        with elf.open("rb") as f:segs=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments() if s["p_type"]=="PT_LOAD"]
        def run(compiled,cfg):
            c=Uc(UC_ARCH_ARM,UC_MODE_THUMB);c.mem_map(0x400000,0x400000);c.mem_write(0x438000,blob)
            c.mem_map(0x100000,0x100000)
            for a,data in segs:c.mem_write(a,data)
            c.mem_map(0x20000000,0x400000)
            event,object,spec,rows=0x20011000,0x20012000,0x20013000,0x20014000
            c.mem_write(event,bytes([0xa5])*0x40);c.mem_write(object,bytes([0x55])*0x80)
            put(c,event,object);put(c,event+0x10,0x20018000)
            put(c,object+8,spec);put(c,spec,rows)
            for i in range(2):put(c,rows+i*4,0x20015000+i*0x100)
            targets={(syms[name] if compiled else int(re.search(r'_([0-9a-f]{6})$',name).group(1),16))&~1:re.search(r'_([0-9a-f]{6})$',name).group(1) for name in providers}
            trace=[]
            def hook(c,address,size,_):
                op=targets.get(address)
                if op is None:return
                r0,r1,r2=(c.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2))
                args=(r0,r1,r2)[:ARGCOUNT[op]]
                if op=='44eb28':
                    c.mem_write(r1,b'first-area-12345');c.mem_write(r2,b'second-area-1234')
                    args=(r0,)
                elif op=='4405d4':args=(r0,bytes(c.mem_read(r1,16)))
                trace.append((op,*args))
                value=0
                if op=='450286':value=cfg['code']
                elif op=='43e0e0':value=cfg['flag8' if r1==8 else ('flag810' if r1==0x810 else 'flag400')]
                elif op=='452fae':value=cfg['scroll_obj']
                elif op=='43e156':value=cfg['state']
                elif op=='44ddea':value=cfg['children']
                elif op=='4519a0':value=cfg['direction']
                elif op=='44d19a':value=cfg['scrolling']
                elif op=='44e586':value=cfg['left']
                elif op=='44e67a':value=cfg['right']
                elif op=='44e442':value=cfg['scroll_dir']
                elif op=='44e486':value=cfg['x']
                elif op=='44e498':value=cfg['y']
                elif op=='43fd9e':value=cfg['width']
                elif op=='43fdda':value=cfg['height']
                elif op=='43e1be':value=cfg['group']
                elif op=='44d5a4':value=cfg['editing']
                elif op=='452ef8':value=cfg['active']
                elif op=='4518d8':value=cfg['reset']
                elif op=='452f00':value=cfg['input_type']
                elif op=='44e42c':value=cfg['scrollbar_mode']
                elif op=='43dd52':value=cfg['metric1']
                elif op=='43dd5c':value=cfg['metric2']
                elif op=='43dd66':value=cfg['metric10']
                elif op=='43de76':value=cfg['metric16']
                elif op=='452c66':value=cfg['compass']
                c.reg_write(A.UC_ARM_REG_R0,value&0xffffffff)
                c.reg_write(A.UC_ARM_REG_PC,c.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE,hook)
            c.reg_write(A.UC_ARM_REG_R0,0x12345678);c.reg_write(A.UC_ARM_REG_R1,event)
            c.reg_write(A.UC_ARM_REG_SP,0x203ff000);c.reg_write(A.UC_ARM_REG_LR,0x600001)
            c.emu_start((syms['audio_uart_lv_base_event_43e7d2'] if compiled else 0x43e7d2)|1,0x600000,count=100000)
            return trace,bytes(c.mem_read(object,0x40)),bytes(c.mem_read(event,0x20))
        suite=cases()
        for i,case in enumerate(suite):
            native,source=run(False,case),run(True,case)
            if native!=source:raise AssertionError((i,case,native,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_BASE_EVENT_ORACLE","source":str(SRC.relative_to(ROOT)),"source_sha256":hashlib.sha256(SRC.read_bytes()).hexdigest(),"official_payload_sha256":digest,"native_span":"0x43e7d2..0x43ebeb","cases":len(suite),"controlled_provider_count":len(providers),"limits":["Lower calls are controlled; live callback mutations, asynchronous input, stack scratch areas and final descriptor layout remain open."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt['status'],len(suite),len(providers))
if __name__=='__main__':main()
