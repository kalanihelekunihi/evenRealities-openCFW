#!/usr/bin/env python3
"""Bounded stock/source LittleFS file sync child ABI and flags."""
from pathlib import Path
import subprocess,json,hashlib
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent;S=R/'g2/components/audio/file_sync_candidate/file_sync.c';O=D/'file-sync-m4.o';E=D/'file-sync-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(O)],check=True)
names=['g2_lfs_file_flush','g2_lfs_pair_isnull','g2_lfs_bd_sync','g2_lfs_ctz_tole32','g2_lfs_dir_commit'];addr={k:0x101000+16*i for i,k in enumerate(names)}
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={k}={v+1:#x}' for k,v in addr.items()],'-o',str(E),str(O)],check=True)
with E.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
old={0x4cde54:'flush',0x4cadd0:'isnull',0x4cabbc:'bdsync',0x4cb000:'tole',0x4cd388:'commit'};new={addr[n]:s for n,s in zip(names,['flush','isnull','bdsync','tole','commit'])}
def run(stock,flags,flush,pair_null,bd,commit):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x80000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in seg:u.mem_write(a,d)
 fs=0x20010000;file=0x20011000;cfg=0x20012000
 for a,v in ((file+0x30,flags),(file+0x28,0x12345678),(file+0x2c,4),(file+0x4c,0x20013000),(file+0x50,cfg),(cfg+4,0x20014000),(cfg+8,3)):
  u.mem_write(a,v.to_bytes(4,'little'))
 u.mem_write(file+4,(7).to_bytes(2,'little'))
 for reg,v in ((A.UC_ARM_REG_R0,fs),(A.UC_ARM_REG_R1,file),(A.UC_ARM_REG_SP,0x2007f000),(A.UC_ARM_REG_LR,0x100f01)):u.reg_write(reg,v)
 events=[];done=[False]
 def hook(cpu,pc,size,user):
  if pc==0x100f00:done[0]=True;cpu.emu_stop();return
  n=(old if stock else new).get(pc)
  if n:
   r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
   if n=='commit':
    raw=cpu.mem_read(r[2],16);tags=[int.from_bytes(raw[i:i+4],'little') for i in (0,8)];buffers=[int.from_bytes(raw[i:i+4],'little') for i in (4,12)];
    events.append([n,r[0],r[1],tags,['stack' if 0x2007e000<=x<0x2007f000 else x for x in buffers],r[3]])
   else:events.append([n,['stack' if n=='tole' and 0x2007e000<=x<0x2007f000 else x for x in r[:4 if n=='bdsync' else 2 if n in ('flush',) else 1]]])
   ret={'flush':flush,'isnull':pair_null,'bdsync':bd,'tole':0,'commit':commit}[n]
   cpu.reg_write(A.UC_ARM_REG_R0,ret);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4cdf74 if stock else sy['g2_lfs_file_sync'])|1,0,count=450)
 assert done[0]
 return {'result':u.reg_read(A.UC_ARM_REG_R0),'flags':int.from_bytes(u.mem_read(file+0x30,4),'little'),'events':events,'sp':u.reg_read(A.UC_ARM_REG_SP)}
rows=[]
for flags in (0,0x80000,0x10000,0x110000):
 for flush,pair,bd,commit in ((0,0,0,0),(0xffffffff,0,0,0),(0,1,0,0),(0,0,0xffffffff,0),(0,0,0,0xffffffff)):
  a=run(True,flags,flush,pair,bd,commit);b=run(False,flags,flush,pair,bd,commit)
  if a!=b:print(json.dumps({'fixture':[flags,flush,pair,bd,commit],'stock':a,'source':b},indent=2));raise AssertionError('mismatch')
  rows.append([flags,flush,pair,bd,commit])
out={'status':'PASS_FILE_SYNC_BOUNDED','cases':len(rows),'rows':rows,'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':'File-flush, pair-null, bd-sync, ctz endian and commit child effects cut; synthetic file/config, no storage writes.'}
(D/'file-sync-results.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
