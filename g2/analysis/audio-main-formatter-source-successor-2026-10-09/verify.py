from pathlib import Path
import json,hashlib,struct,itertools
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2];blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];receipt=json.loads((D/'reproduction-receipt.json').read_text());elf=Path(receipt['elf']);assert hashlib.sha256(elf.read_bytes()).hexdigest()==receipt['elf_sha256']
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
OUT=0x20006000;FMT=0x20007000;ARGS=0x20008000;TEXT=0x20008400;SINKBUFFER=0x2006b930

def run(native,format='hello\n',words=(),translation=0,null_output=False,operation='format',logging=True):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_A15)
 for a,n in [(0x438000,(len(raw)+4095)&~4095),(0x20000000,0x80000),(0x100000,0x10000),(0xe000e000,0x2000)]:u.mem_map(a,n)
 u.mem_write(0x438000,raw)
 for a,b in segments:u.mem_write(a,b)
 def w(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 u.cpr_write(15,0,1,0,2,0,False,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,0x40000000);u.reg_write(UC_ARM_REG_FPSCR,0)
 u.mem_write(FMT,format.encode()+b'\0');u.mem_write(TEXT,b'abcdef\0');u.mem_write(ARGS,b'\xa5'*128)
 for i,v in enumerate(words):w(ARGS+4*i,v)
 u.mem_write(OUT,b'\xa5'*1024);u.mem_write(SINKBUFFER,b'\xa5'*1024);u.mem_write(0x20074f7f,bytes([translation]));w(0x200742f0,(sym['audio_known_noop'] if native else 0x5a0a6d) if logging else 0)
 seen=[];last=[];boundary=[];sink_calls=[]
 def code(u,a,n,d):
  if operation=='failure' and last and a==last[-1]:boundary.append('nonreturning_failure_spin');u.emu_stop();return
  last.append(a)
  if native:assert 0x100000<=a<0x110000,hex(a);seen.append(a)
  if a==(sym['audio_known_noop']&~1) if native else a==0x5a0a6c:sink_calls.append(hex(u.reg_read(UC_ARM_REG_R0)))
 u.hook_add(UC_HOOK_CODE,code);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001)
 if operation=='format':args=[0 if null_output else OUT,FMT,ARGS];entry=sym['audio_heap_formatter'] if native else 0x473036
 elif operation=='log':args=[FMT,*list(words[:3])];entry=sym['audio_heap_log'] if native else 0x4733ee
 else:args=[];entry=sym['audio_heap_malloc_failed'] if native else 0x46d85e
 for reg,val in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,val)
 pc=entry
 for _ in range(100000):
  try:u.emu_start(pc|1,0x2007f000,count=1)
  except UcError as e:raise RuntimeError((str(e),native,hex(u.reg_read(UC_ARM_REG_PC)),format,words)) from e
  pc=u.reg_read(UC_ARM_REG_PC)
  if pc==0x2007f000 or boundary:break
 else:raise AssertionError('step limit')
 if operation=='format':
  expected={'literal\n':'literal\n','%d':'-1','%08x':'00abcdef','%u':'4294967295','%-8s':'abcdef        ','%8.3s':'     abc','%c %% %q':'A % q','%llx':'ffffffffffffffff','%lld':'-9223372036854775808','%d/%llu':'17/9223372036854775807'}.get(format)
  if expected is not None:
   if translation and not null_output:expected=expected.replace('\n','\r\n')
   assert u.reg_read(UC_ARM_REG_R0)==len(expected)
   if not null_output:assert bytes(u.mem_read(OUT,len(expected)+1))==expected.encode()+b'\0'
  if words==[0,0] and format in ['%f','%.2f'] and not null_output:assert bytes(u.mem_read(OUT,4))==b'0.0\0'
 if native:assert seen
 return {'result':None if boundary else u.reg_read(UC_ARM_REG_R0),'out_hex':bytes(u.mem_read(OUT,1024)).hex(),'log_hex':bytes(u.mem_read(SINKBUFFER,1024)).hex(),'sink_calls':sink_calls,'boundary':boundary,'fpscr':u.reg_read(UC_ARM_REG_FPSCR)}
rows=[]
def compare(c):
 o=run(False,**c);n=run(True,**c);assert o==n,(c,o,n);rows.append(dict(inputs=c,**o))
for format,words in [('literal\n',[]),('%d',[0xffffffff]),('%08x',[0xabcdef]),('%u',[0xffffffff]),('%-8s',[TEXT]),('%8.3s',[TEXT]),('%c %% %q',[65]),('%llx',[0xffffffff,0xffffffff]),('%lld',[0,0x80000000]),('%d/%llu',[17,0xa5a5a5a5,0xffffffff,0x7fffffff])]:
 for translation,null_output in itertools.product([0,1],[False,True]):compare(dict(format=format,words=words,translation=translation,null_output=null_output))
for value,format,translation in itertools.product([0.0,1.25,-1.25,123456.5,1e-10],['%f','%.2f','%8.3f','%F'],[0,1]):
 bits=struct.unpack('<II',struct.pack('<d',value));compare(dict(format=format,words=bits,translation=translation))
for operation,logging,translation in itertools.product(['log','failure'],[False,True],[0,1]):compare(dict(operation=operation,logging=logging,translation=translation,format='value=%u\n',words=[17]))
(D/'results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'elf_sha256':receipt['elf_sha256'],'comparisons':rows,'limits':['Adapted already preserved Ambiq utility source; integer/string/float selected cases and actual fatal message trace, not exhaustive formatter equivalence.','Known zero-return child chosen as synthetic sink; no actual UART/RTT driver or hardware output claimed.','Native guard includes every reached helper; fatal self-loop stops without pretending allocator returned.']},indent=2)+'\n');print('PASS',len(rows),'main formatter/failure comparisons')
