"""Connected file facade, LittleFS membership wrapper, and core cut oracle."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
FUN={'read':('audio_file_read',0x474634),'seek':('audio_file_seek',0x474814),
     'seek_end':('audio_file_seek',0x474814),'seek_bound':('audio_file_seek',0x474814),
     'tell':('audio_file_tell',0x474870),
     'open_core':('audio_file_lfs_open_core',0x4cdcc8),
     'dir_get':('audio_file_lfs_dir_get',0x4cb3c8),
     'dir_find_empty':('audio_file_lfs_dir_find',0x4cc04a),
     'dir_find_missing':('audio_file_lfs_dir_find',0x4cc04a),
     'force_no_move':('audio_file_lfs_forceconsistency',0x4cf9e0),
     'move_fetch_failure':('audio_file_lfs_consistency_move',0x4cf6e8),
     'recover_fetch_failure':('audio_file_lfs_consistency_recover',0x4cf648),
     'recover_commit':('audio_file_lfs_consistency_recover',0x4cf648),
     'open_existing_trunc':('audio_file_lfs_opencfg',0x4cda36),
     'open_create':('audio_file_lfs_opencfg',0x4cda36),
     'callback_short':('audio_file_lfs_dir_find_match',0x4cbfec),
     'callback_equal':('audio_file_lfs_dir_find_match',0x4cbfec),
     'callback_long':('audio_file_lfs_dir_find_match',0x4cbfec)}
CUTS={0x4497b6:0,0x44981c:0,0x4ce042:8,0x4cde54:0,0x4cb23a:0,0x4cb968:0xfffffffe,0x4cf7ac:0,0x4733ee:0,0x4cbedc:0xfffffffb,0x4cd388:0,0x474cd2:0x20070000,0x4caa04:0}
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
uint8_t audio_file_lfs_context[64];void *audio_file_api_mutex;
void *codec_allocate(uint32_t n){(void)n;return (void *)0x20070000u;}
void audio_file_heap_free(void *p){(void)p;}
int32_t audio_file_mutex_acquire(void *p,uint32_t t){(void)p;(void)t;return 0;}
int32_t audio_file_mutex_release(void *p){(void)p;return 0;}
void g2_file_close_error(const char *a,const char *b,uint32_t c){(void)a;(void)b;(void)c;}
int32_t g2_log_transport_queue_failure(const char *a,...){(void)a;return 0;}
int32_t g2_lfs_file_flushedread(void *a,void *b,void *c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 8;}
uint32_t g2_lfs_ctz_index(void *a,uint32_t *b){(void)a;(void)b;return 0;}
int32_t g2_lfs_file_flush(void *a,void *b){(void)a;(void)b;return 0;}
int32_t g2_lfs_dir_fetchmatch(void *a,void *b,const uint32_t *c,uint32_t d,uint32_t e,uint16_t *f,int32_t (*g)(void *,uint32_t,const void *),void *h){(void)b;(void)c;(void)d;(void)e;(void)f;(void)g;(void)h;return *(uint32_t *)((uint8_t *)a+0x7c)==2u?0x00100000:-2;}
int32_t g2_lfs_bd_cmp(void *a,void *b,void *c,uint32_t d,uint32_t e,uint32_t f,const void *g,uint32_t h){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;(void)g;(void)h;return 0;}
int32_t g2_lfs_dir_fetch(void *a,void *b,const uint32_t *c){(void)b;(void)c;return *(uint32_t *)((uint8_t *)a+0x7c)?0:-5;}
'''+''.join('__attribute__((naked,used)) void '+n+'(void){__asm__ volatile("movs r0, #0\\n bx lr");}\n' for n in [
 'g2_lfs_fs_deorphan','g2_lfs_fs_prepmove','g2_lfs_dir_commit',
 'g2_lfs_dir_getslice',
 'g2_lfs_file_close']))
 elf=Path(td)/'file.elf'
 sources=['display_file_api.c','display_file_lfs_wrappers.c','display_file_lfs_seek_core.c','display_file_lfs_read_core.c','display_file_lfs_open_core.c','display_file_lfs_opencfg.c','display_file_lfs_simple_helpers.c','display_file_lfs_dir_find.c','display_file_lfs_demove.c','display_file_lfs_desuperblock.c']
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_file_read',*[str(ROOT/'components/audio/uart_thread_source_candidate'/s) for s in sources],str(ROOT/'components/audio/file_backend_close_candidate/mlist_isopen.c'),str(ROOT/'components/audio/file_sync_candidate/bd_flush_leaves.c'),str(ROOT/'components/audio/file_sync_candidate/cache_fill.c'),str(shim),'-o',str(elf)],check=True)
 syms=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(candidate,kind):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
  u.mem_map(0x100000,0x100000)
  for v,d in segs:u.mem_write(v,d)
  u.mem_map(0x20000000,0x100000)
  F=0x20010000;CTX=0x20020000
  u.mem_write(F,b'\0'*96);u.mem_write(CTX,b'\0'*64)
  u.mem_write(F,struct.pack('<I',CTX));u.mem_write(F+4+0x34,struct.pack('<I',15))
  u.mem_write(F+4+0x30,struct.pack('<I',1))
  u.mem_write(F+4+0x2c,struct.pack('<I',20))
  u.mem_write(CTX+0x28,struct.pack('<I',F+4))
  u.mem_write(CTX+0x74,struct.pack('<I',8 if kind=='seek_bound' else 0x10000))
  if kind in ('open_core','recover_fetch_failure','recover_commit'):
   u.mem_write(CTX+0x30,struct.pack('<I',0x200))
  if kind=='recover_commit':
   u.mem_write(CTX+0x7c,struct.pack('<I',1))
   u.mem_write(CTX+0x68,struct.pack('<I',0x20060000))
   u.mem_write(0x2006001c,struct.pack('<I',4096))
  if kind in ('open_existing_trunc','open_create'):
   if kind=='open_existing_trunc':u.mem_write(CTX+0x7c,struct.pack('<I',2))
   u.mem_write(CTX+0x68,struct.pack('<I',0x20060000))
   u.mem_write(CTX+0x20,struct.pack('<II',0,1))
   u.mem_write(0x20060028,struct.pack('<I',16))
   u.mem_write(0x20040000,b'x\0')
   u.mem_write(0x20050000,b'\0'*16)
  if kind.startswith('callback_'):
   n={'callback_short':2,'callback_equal':3,'callback_long':4}[kind]
   u.mem_write(0x20030000,struct.pack('<III',CTX,0x20050000,n))
   u.mem_write(0x20040000,struct.pack('<II',4,8))
  if kind=='move_fetch_failure':u.mem_write(CTX+0x3c,struct.pack('<III',0x4ff00000,5,6))
  if kind.startswith('dir_find_'):
   u.mem_write(0x20030000,struct.pack('<I',0x20040000));u.mem_write(0x20040000,b'\0' if kind=='dir_find_empty' else b'x\0')
  args={'read':(0x20030000,2,4,F),'seek':(F,3,0,0),
        'seek_end':(F,3,2,0),'seek_bound':(F,9,0,0),'tell':(F,0,0,0),
        'open_core':(CTX,F+4,0x20030000,2),
        'dir_get':(CTX,F+4,0x700ffc00,0x200008),
        'dir_find_empty':(CTX,F+4,0x20030000,0x20050000),
        'dir_find_missing':(CTX,F+4,0x20030000,0x20050000),
        'force_no_move':(CTX,0,0,0),
        'move_fetch_failure':(CTX,0,0,0),
        'recover_fetch_failure':(CTX,0,0,0),
        'recover_commit':(CTX,0,0,0),
        'open_existing_trunc':(CTX,F+4,0x20040000,0x401),
        'open_create':(CTX,F+4,0x20040000,0x101),
        'callback_short':(0x20030000,3,0x20040000,0),
        'callback_equal':(0x20030000,3,0x20040000,0),
        'callback_long':(0x20030000,3,0x20040000,0)}[kind]
  for reg,val in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,val)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  if kind=='dir_get':u.mem_write(0x200ff000,struct.pack('<I',0x20040000))
  if kind in ('open_existing_trunc','open_create'):u.mem_write(0x200ff000,struct.pack('<I',0x20050000))
  if not candidate:
   def bypass(uc,address,size,_):
    if address in CUTS:
     value=0 if address==0x4cbedc and kind=='recover_commit' else CUTS[address]
     if address==0x4cb968 and kind=='open_existing_trunc':value=0x00100000
     uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,bypass)
  name,stock=FUN[kind];u.emu_start((syms[name] if candidate else stock)|1,0x600000,count=10000)
  return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(F,96)),bytes(u.mem_read(CTX,64)),bytes(u.mem_read(0x20070000,16))
 for kind in FUN:
  a=run(False,kind);b=run(True,kind)
  assert a==b,(kind,a[0],b[0]);print('PASS connected file',kind)
