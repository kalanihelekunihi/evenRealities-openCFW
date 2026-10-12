"""Full info callback native/compiled ARM comparisons with explicit child cuts."""
from pathlib import Path
import subprocess,tempfile,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];SRC=Path(__file__).parent/'root-bin-info-round60/info_candidate.c'
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
names=[('audio_uart_lv_grid_copy_454738',0x454738,'copy'),('audio_uart_lv_fs_extension_4c70e4',0x4c70e4,'ext'),('audio_uart_lv_string_compare_4547be',0x4547be,'cmp'),('audio_uart_lv_fs_file_read_4c6f46',0x4c6f46,'read'),('audio_uart_lvgl_log',0x44d25c,'log')]
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('void *audio_uart_lv_grid_copy_454738(void*a,const void*b,unsigned c){return a;} const char *audio_uart_lv_fs_extension_4c70e4(const char*a){return a;} int audio_uart_lv_string_compare_4547be(const char*a,const char*b){return 0;} unsigned audio_uart_lv_fs_file_read_4c6f46(void*a,void*b,unsigned c,unsigned*d){return 0;} void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,const char*e,...){}');elf=td/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-ffunction-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_bin_decoder_info_4c79d0',str(SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 cases=[]
 for typ,magic,cf,flags in itertools.product([0,2,3,255],[0,7,25,255],[0,14,255],[0,1,0xffff]):cases.append((typ,magic,cf,flags,0,0,12))
 for magic,cf,flags,cmp,res,rn in itertools.product([0,7,25],[0,14],[0,1],[0,1],[0,1,256,0x87654321],[0,11,12,13]):cases.append((1,magic,cf,flags,cmp,res,rn))
 count=0
 for typ,magic,cf,flags,cmp,res,rn in cases:
  outputs=[]
  for isc in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   dsc=0x20003000;header=0x20004000;source=0x20005000;ext=0x20006000
   def put(a,v):u.mem_write(a,v.to_bytes(4,'little'))
   def word(a):return int.from_bytes(u.mem_read(a,4),'little')
   def string(a):
    out=bytearray()
    while (v:=bytes(u.mem_read(a+len(out),1)))!=b'\0':out.extend(v)
    return out.decode()
   initial=(magic|(cf<<8)|(flags<<16)).to_bytes(4,'little')+bytes.fromhex('123456789abcdef0');u.mem_write(header,initial);u.mem_write(source,initial+b'\0');u.mem_write(ext,b'bin\0');put(dsc+12,source);u.mem_write(dsc+16,bytes([typ]))
   cuts={(syms[n] if isc else a)&~1:k for n,a,k in names};calls=[]
   def hook(uc,address,size,user):
    if address not in cuts:return
    kind=cuts[address];a=[uc.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=0
    if kind=='copy':calls.append((kind,*a[:3]));u.mem_write(a[0],bytes(u.mem_read(a[1],a[2])));ret=a[0]
    elif kind=='ext':calls.append((kind,a[0]));ret=ext
    elif kind=='cmp':calls.append((kind,string(a[0]),string(a[1])));ret=cmp
    elif kind=='read':calls.append((kind,*a[:3]));u.mem_write(a[1],initial);put(a[3],rn);ret=res
    else:
     sp=uc.reg_read(UC_ARM_REG_SP);fmt=string(word(sp));extra=[]
     if 'Read file' in fmt:extra=[word(sp+4),word(sp+8),word(sp+12)]
     elif 'Legacy' in fmt:extra=[word(sp+4)]
     calls.append((kind,a[0],string(a[1]),a[2],string(a[3]),fmt,extra))
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0xdeadbeef);u.reg_write(UC_ARM_REG_R1,dsc);u.reg_write(UC_ARM_REG_R2,header)
   u.emu_start((syms['audio_uart_lv_bin_decoder_info_4c79d0'] if isc else 0x4c79d0)|1,0x600000,count=10000)
   outputs.append((calls,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(header,12)),u.reg_read(UC_ARM_REG_SP)))
  assert outputs[0]==outputs[1],(typ,magic,cf,flags,cmp,res,rn,outputs)
  count+=1
 receipt={'status':'PASS_BOUNDED_COMPILED_ARM_NATIVE_BIN_INFO','cases':count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'native_payload_sha256':hashlib.sha256(BLOB).hexdigest(),'limits':['Copy, extension, compare, file read and logger are controlled child cuts.','Includes all source-type branches, legacy/current headers, unknown format, flag changes, failed reads, length mismatch and 8-bit status truncation.','Provider bodies, image layout, byte equality and hardware remain separate gates.']}
 (SRC.parent/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt)
