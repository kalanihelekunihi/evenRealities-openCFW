from pathlib import Path
import subprocess,tempfile,json,hashlib,re
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];SRC=Path(__file__).parent/'root-bin-open-round65/open_candidate.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);names=re.findall(r'extern[^;]*?\b(audio_\w+)\(',SRC.read_text());shim=td/'shim.c';shim.write_text('\n'.join('unsigned '+n+'(void){return 0;}' for n in names));elf=td/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_bin_decoder_open_4c7b24',str(SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']

 count=0
 cases=[(16,0,0,1,1,0,0,1,premult,adjust,enabled,nocache,entry) for premult in [0,1] for adjust in [0,1,2] for enabled in [0,1] for nocache in [0,1] for entry in [0,1]]
 fallback={'audio_uart_lv_malloc':0x44f718,'audio_uart_lv_heap_free':0x44f758,'audio_uart_lvgl_log':0x44d25c,'audio_uart_checksum_copy':0x439c04}
 for cf,compressed,indexed,dataok,allocok,cmp,fs,result,premult,adjust,enabled,nocache,entry in cases:
  outputs=[]
  for isc in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   dsc=0x20003000;src=0x20004000;data=0x20005000;file=0x20006000;decoder=0x20007000;extension=0x20008000
   def put(a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
   def word(a):return int.from_bytes(u.mem_read(a,4),'little')
   def string(a):
    out=bytearray()
    while (v:=bytes(u.mem_read(a+len(out),1)))!=b'\0':out.extend(v)
    return out.decode()
   put(dsc+12,src);u.mem_write(dsc+16,b'\1');u.mem_write(dsc+7,bytes([indexed]));put(dsc+32,(cf<<8)|(compressed<<19)|(premult<<16));u.mem_write(dsc+6,bytes([nocache]));decoded=0x20009000;adjusted=0x2000a000;put(decoded+12,123);put(adjusted+12,456);u.mem_write(extension,b'bin\0');calls=[];cuts={}
   for name in names:
    native=fallback[name] if name in fallback else int(name.rsplit('_',1)[1],16)
    cuts[(syms[name] if isc else native)&~1]=name
   def hook(uc,a,size,user):
    if a not in cuts:return
    name=cuts[a];args=[uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=0
    if name=='audio_uart_lv_fs_extension_4c70e4':calls.append(('ext',args[0]));ret=extension
    elif name=='audio_uart_lv_string_compare_4547be':calls.append(('cmp',string(args[0]),string(args[1])));ret=cmp
    elif name=='audio_uart_lv_bin_decoder_data_get_4c81a2':calls.append(('get',args[0]));ret=data if dataok else 0
    elif name=='audio_uart_lv_malloc':calls.append(('malloc',args[0]));ret=file if allocok else 0
    elif name=='audio_uart_lv_fs_file_open_4c6d9a':calls.append(('open',*args[:3]));ret=fs
    elif name=='audio_uart_lv_bin_decoder_data_free_4c8210':calls.append(('cleanup',args[0]));put(dsc+72,0)
    elif name=='audio_uart_lv_heap_free':calls.append(('free',args[0]))
    elif name=='audio_uart_lvgl_log':
     sp=uc.reg_read(UC_ARM_REG_SP);calls.append(('log',args[0],string(args[1]),args[2],string(args[3]),string(word(sp)),word(sp+4)))
    elif name=='audio_uart_lv_draw_buf_set_flag_48b750':calls.append(('flag',*args[:2]))
    elif name=='audio_uart_lv_decoder_postprocess_489168':calls.append(('postprocess',*args[:2]));ret=0 if adjust==0 else (decoded if adjust==1 else adjusted)
    elif name=='audio_uart_lv_image_cache_enabled_4d4b24':calls.append(('enabled',));ret=enabled
    elif name=='audio_uart_lv_decoder_add_cache_48911a':calls.append(('cache',args[0],word(args[1]),word(args[1]+4),bytes(u.mem_read(args[1]+8,1)),args[2],args[3]));ret=0x2000b000 if entry else 0
    elif name.startswith('audio_uart_lv_bin_decode_') or name=='audio_uart_lv_bin_load_indexed_4c8570':calls.append((name,*args[:2]));ret=result;put(dsc+44,decoded)
    else:raise AssertionError(('unexpected child',name,args))
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,decoder);u.reg_write(UC_ARM_REG_R1,dsc);u.emu_start((syms['audio_uart_lv_bin_decoder_open_4c7b24'] if isc else 0x4c7b24)|1,0x600000,count=10000);outputs.append((calls,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(dsc,80)),bytes(u.mem_read(data,68)),u.reg_read(UC_ARM_REG_SP)))
  assert outputs[0]==outputs[1],(cf,compressed,indexed,dataok,allocok,cmp,fs,result,outputs);count+=1
 r={'status':'PASS_POSTPROCESS_CACHE_PATHS_NOT_FULL_OPEN_QUALIFICATION','cases':count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'limits':['Child operations are controlled cuts; no production substitutes supplied.','Covers premultiply flag, failed/same/new postprocess, cleanup ownership transfer, disabled cache, no-cache argument and insertion success/failure.','Cache key compares native-defined fields only; three padding bytes remain unspecified. Variable-image conversion still requires comparison.','Candidate remains unselected.']};(SRC.parent/'open-postprocess-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
