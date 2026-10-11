#!/usr/bin/env python3
from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
H=Path(__file__).resolve().parent;R=H.parents[3];im=R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';blob=im.read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
body=blob[0x43cb84-0x437fe0:0x43ce9e-0x437fe0];assert hashlib.sha256(body).hexdigest()=='68f4f898f4517dfd7839203e273a7ef9c526708243db978c1a9727b4a8dd1275'
cc=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc');elfp=Path('/tmp/audio_short_formatter.elf')
providers={'audio_log_flags':0x43d0cf,'audio_log_level':0x43d0db,'audio_log_tick':0x4490cd,'audio_log_context':0x44a1c7,'audio_string_length':0x44a43d,'audio_log_emit':0x43ca51,'audio_log_sequence':0x20074f9f}
flags=['-mcpu=cortex-m55','-mthumb','-mfloat-abi=hard','-mfpu=fpv5-d16','-O0','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x10001000','-Wl,-e,audio_log_format']+[f'-Wl,--defsym={k}={v:#x}' for k,v in providers.items()]
subprocess.run([str(cc),*flags,str(R/'g2/components/audio/audio_log_format_source_candidate/format.c'),'-o',str(elfp)],check=True)
with elfp.open('rb') as f:
 e=ELFFile(f);entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='audio_log_format');segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
def run(source,case):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x437000,((len(blob)+0xfe0+0xfff)//0x1000)*0x1000);u.mem_write(0x437fe0,blob);u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x800000);u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,0x40000000);u.reg_write(UC_ARM_REG_FPSCR,case.get('fpscr',0));u.reg_write(UC_ARM_REG_SP,0x207ff000);u.reg_write(UC_ARM_REG_LR,0x10000001)
 u.mem_write(0x20040000,case['fmt'].encode()+b'\0');u.mem_write(0x20041000,case.get('str_bytes',b'abcdefghijklmnopqrs') + b'\0');u.mem_write(0x20041100,b'QRSTUV' + b'\0');u.mem_write(0x20042000,struct.pack('<32I',*([0x20041000,0x20041100,0xaabbccdd,0x01020304,0xf0f1f2f3,0x87654321,0x11111111,0x22222222]+[0x20041000]*24)));u.mem_write(0x20074f9f,bytes([case['seq']]));
 if 'fp64bits' in case:u.mem_write(0x20042000,struct.pack('<Q',case['fp64bits']))
 if case.get('null_string'):u.mem_write(0x20042000,struct.pack('<I',0))
 for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),(case['token'],0x20040000,0x20042000)):u.reg_write(reg,v)
 calls=[]
 def ret(v=None):
  if v is not None:u.reg_write(UC_ARM_REG_R0,v&0xffffffff)
  u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def hook(emu,pc,size,data):
  r=[emu.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
  if pc==0x43d0ce:
   prior=calls.count('flags');calls.append('flags');ret(case.get('flags_sequence',[case['flags']])[min(prior,len(case.get('flags_sequence',[case['flags']]))-1)]);return
  if pc==0x43d0da:calls.append('level');ret(case['level']);return
  if pc==0x4490cc:calls.append('tick');ret(case['tick']);return
  if pc==0x44a1c6:calls.append('context');ret(0x89abcdef);return
  if pc==0x44a43c:
   text=bytes(emu.mem_read(r[0],64)).split(b'\0')[0];calls.append(['strlen',text.decode()]);ret(len(text));return
  if pc==0x43ca50:calls.append(['emit',r[1],bytes(emu.mem_read(r[0],r[1])).hex()]);ret();return
 u.hook_add(UC_HOOK_CODE,hook)
 
 try:u.emu_start((entry if source else 0x43cb84)|1,0x10000000,count=10000)
 except Exception as exc:raise RuntimeError((source,case,hex(u.reg_read(UC_ARM_REG_PC)),calls)) from exc
 assert u.reg_read(UC_ARM_REG_PC)==0x10000000
 return dict(calls=calls,seq=u.mem_read(0x20074f9f,1)[0],fpscr=u.reg_read(UC_ARM_REG_FPSCR))
fmts=['%.2f','plain','%d','%x %u','%%','%s','%s %s','%llx','%hd','%+08d','%p','%q','%c','%05.3u','%. *d']
rows=[]
for fmt,flags,level,category,limit,seq,tick in itertools.product(fmts,(0,1,4,5),(0,3),(0,5,6),(0,1,3),(0,255),(0,999,1000)):
 case=dict(fmt=fmt,flags=flags,level=level,token=((category&7)<<26)|((limit&15)<<22)|0x12345,seq=seq,tick=tick)
 a=run(False,case);b=run(True,case)
 if a!=b:print('DIFF',case,a,b);break
 rows.append(case)
else:
 for fp64bits in (0,0x8000000000000000,0x3ff0000000000000,0xbff0000000000000,0x3ff8000000000000,0x7fefffffffffffff,0x0010000000000000,1,0x7ff0000000000000,0xfff0000000000000,0x7ff8000000000001,0x7ff0000000000001):
  for fpscr in (0,0x00400000,0x00800000,0x00c00000,0x01000000,0x02000000):
   for fmt in ('%f','%F','%f %d'):
    case=dict(fmt=fmt,flags=0,level=0,token=(3<<22)|0x12345,seq=0,tick=1000,fp64bits=fp64bits,fpscr=fpscr)
    a=run(False,case);b=run(True,case)
    if a!=b:raise AssertionError((case,a,b))
    rows.append(case)
 adversarial=['%','%.','%l','%ll','%h','%hh','%0','%#','%+','%q','%Q','%z','%zu','%llu','%ld','%hd','%hhd','%08d','%123d','%0-+ #12.3d','%.*d','%.*s','%1.2s','%12.1s','%#x','%#o','%02X','%C','%S','%e','%g','%a','%n','%t','%j','%%d','%%%d','%s%s','%s%s%s','%s%s%s%s','%d%d%d%d%d%d%d%d%d','%llx%llx','%f%f','%.2f','%lf','%llf']
 for fmt in adversarial:
  for limit in (0,1,2,4,15):
   case=dict(fmt=fmt,flags=0,level=0,token=(limit<<22)|0x12345,seq=255,tick=0)
   a=run(False,case);b=run(True,case)
   if a!=b:raise AssertionError((case,a,b))
   rows.append(case)
 (H/'audio-log-format-receipt.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'body_sha256':hashlib.sha256(body).hexdigest(),'source_sha256':hashlib.sha256((R/'g2/components/audio/audio_log_format_source_candidate/format.c').read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(elfp.read_bytes()).hexdigest(),'providers':{k:hex(v) for k,v in providers.items()},'formats':fmts,'adversarial_formats':adversarial,'limits':'Synthetic valid pointers and packet state; flags/level/tick/context/strlen/output intercepted. General float and format-domain correctness requires wider proof.'},indent=2)+'\n');print('PASS',len(rows))
