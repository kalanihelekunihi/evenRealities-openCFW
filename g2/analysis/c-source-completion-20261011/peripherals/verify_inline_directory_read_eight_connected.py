#!/usr/bin/env python3
"""Native/C eight-byte inline file read through LittleFS directory lookup."""
from pathlib import Path
import hashlib,json,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/file_sync_candidate'
names=('file_flushedread','dir_getread','dir_getslice','gstate_hasmovehere',
       'bd_read','cache_fill','bd_flush_leaves','byte_copy')
sources=[S/(name+'.c') for name in names]
objects=[D/('inline-read-eight-'+name+'.o') for name in names]
E=D/'inline-directory-read-eight-connected.elf'
for src,obj in zip(sources,objects):
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-std=c11','-ffreestanding','-O2','-Wall','-Wextra','-Werror',
                 '-c',str(src),'-o',str(obj)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',
                '--defsym=g2_lfs_ctz_find=0x110001',
                '--defsym=g2_file_close_error=0x110011',
                '-o',str(E),*map(str,objects)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segments=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD']
 symbols={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
assert max(a+len(b) for a,b in segments)<0x110000
OTA=R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
blob=OTA.read_bytes()[0x20:]
tag=0x20100008;commit=0x500ffc04
disk=bytearray(b'\xff'*256)
disk[0:4]=(1).to_bytes(4,'little')
disk[4:8]=(tag^0xffffffff).to_bytes(4,'big')
disk[8:16]=b'ABCDEFGH'
disk[16:20]=(commit^tag).to_bytes(4,'big')
def run(native,start,count,read_error):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(blob)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x80000)):u.mem_map(a,n)
 if native:u.mem_write(0x438000,blob)
 else:
  for a,b in segments:u.mem_write(a,b)
 def w(a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
 def rd(a):return int.from_bytes(u.mem_read(a,4),'little')
 fs,file,out,cfg=0x20010000,0x20012000,0x20013000,0x20017000
 w(fs+0x68,cfg);w(fs+0x6c,100);w(fs,0xffffffff);w(fs+12,0x20015000)
 w(cfg+4,0x110121);w(cfg+0x14,8);w(cfg+0x1c,256);w(cfg+0x28,16)
 w(file+4,0);w(file+8,0);w(file+12,1);w(file+20,24);w(file+24,commit)
 w(file+0x30,0x100000);w(file+0x2c,8);w(file+0x34,start);w(file+0x3c,0)
 w(file+0x40,0xffffffff);w(file+0x4c,0x20014000)
 for reg,v in ((A.UC_ARM_REG_R0,fs),(A.UC_ARM_REG_R1,file),(A.UC_ARM_REG_R2,out),
               (A.UC_ARM_REG_R3,count),(A.UC_ARM_REG_SP,0x2007f000),
               (A.UC_ARM_REG_LR,0x110f01)):u.reg_write(reg,v)
 original={0x4ce042:'file',0x4cb3f0:'dir',0x4cb23a:'slice',0x4caf5c:'state',0x4ca83c:'bd'}
 source={symbols['g2_lfs_file_flushedread']&~1:'file',
         symbols['g2_lfs_dir_getread']&~1:'dir',
         symbols['g2_lfs_dir_getslice']&~1:'slice',
         symbols['g2_lfs_gstate_hasmovehere']&~1:'state',
         symbols['g2_lfs_bd_read']&~1:'bd'}
 events=[];done=[False]
 def hook(cpu,pc,sz,user):
  if pc==0x110f00:done[0]=True;cpu.emu_stop();return
  if pc==0x110120:
   sp=cpu.reg_read(A.UC_ARM_REG_SP);block=cpu.reg_read(A.UC_ARM_REG_R1)
   off=cpu.reg_read(A.UC_ARM_REG_R2);dst=cpu.reg_read(A.UC_ARM_REG_R3);length=rd(sp)
   events.append(('read',block,off,length))
   if read_error==0 and block==0 and off+length<=256:cpu.mem_write(dst,bytes(disk[off:off+length]))
   cpu.reg_write(A.UC_ARM_REG_R0,read_error&0xffffffff)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR));return
  name=(original if native else source).get(pc)
  if name:events.append((name,))
 u.hook_add(UC_HOOK_CODE,hook)
 entry=0x4ce042 if native else symbols['g2_lfs_file_flushedread']
 u.emu_start(entry|1,0,count=12000)
 assert done[0],(native,start,count,read_error,events)
 return {'result':u.reg_read(A.UC_ARM_REG_R0),'events':events,
         'output':bytes(u.mem_read(out,12)).hex(),'position':rd(file+0x34),
         'offset':rd(file+0x3c),'flags':rd(file+0x30),
         'read_cache':bytes(u.mem_read(file+0x40,16)).hex(),
         'fs_cache':bytes(u.mem_read(fs,16)).hex(),
         'dir_buffer':bytes(u.mem_read(0x20014000,16)).hex()}
rows=[]
for start,count,error in ((0,1,0),(0,8,0),(3,4,0),(6,2,0),(0,8,-5),(0,0,0)):
 a=run(True,start,count,error);b=run(False,start,count,error)
 assert a==b,(start,count,error,a,b)
 if error==0:
  assert a['result']==count and a['position']==start+count,(start,count,a)
  assert bytes.fromhex(a['output'])[:count]==b'ABCDEFGH'[start:start+count],a
 else:
  assert a['result']==(error&0xffffffff) and a['position']==start,a
 rows.append({'start':start,'count':count,'error':error,'result':a['result'],'events':a['events']})
assert any(('dir',) in row['events'] for row in rows)
result={'status':'PASS_INLINE_DIRECTORY_READ_EIGHT_CONNECTED_BOUNDED','cases':len(rows),'rows':rows,
        'source_sha256':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        'ota_sha256':hashlib.sha256(OTA.read_bytes()).hexdigest(),
        'limits':'Synthetic directory metadata and flash-read callback; no real storage, boot, or hardware proof.'}
(D/'inline-directory-read-eight-connected-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(result['status'],len(rows))
