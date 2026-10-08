import ctypes,hashlib,importlib.util,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5];p=ROOT/'g2/components/bootloader/initializer_callbacks/verify_context_interrupt.py';s=importlib.util.spec_from_file_location('base',p);v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
lib=ctypes.CDLL('/tmp/opencfw-ambiq-printf.dylib');fn=lib.am_util_stdio_printf;fn.argtypes=[ctypes.c_char_p];fn.restype=ctypes.c_uint32;CB=ctypes.CFUNCTYPE(None,ctypes.c_char_p);lib.am_util_stdio_printf_init.argtypes=[CB];lib.am_util_stdio_textmode_set.argtypes=[ctypes.c_bool]
class M(v.Machine):
 def __init__(self):super().__init__(False);self.events=[]
 def code(self,u,pc,n,z):
  if pc==0x08000100:
   ptr=u.reg_read(v.a.UC_ARM_REG_R0);raw=bytes(u.mem_read(ptr,512)).split(b'\0')[0];self.events.append(raw.hex());u.reg_write(v.a.UC_ARM_REG_PC,u.reg_read(v.a.UC_ARM_REG_LR));return
  super().code(u,pc,n,z)
rows=[]
for enabled in [False,True]:
 for translated in [False,True]:
  for fmt,arg in [('literal',0),('a\nb',0),('%08x',0x123),('%d',-42)]:
   m=M();u=m.cpu;u.mem_write(0x200270cc,struct.pack('<I',0x08000101 if enabled else 0));u.mem_write(0x200271c4,bytes([translated]));u.mem_write(0x20001000,fmt.encode()+b'\0');u.reg_write(v.a.UC_ARM_REG_SP,v.SP);u.reg_write(v.a.UC_ARM_REG_LR,v.STOP|1);u.reg_write(v.a.UC_ARM_REG_R0,0x20001000);u.reg_write(v.a.UC_ARM_REG_R1,arg&0xffffffff);u.emu_start(0x415faf,v.STOP+2,count=100000);assert m.done;events=[];cb=CB(lambda raw:events.append(raw.hex()));lib.am_util_stdio_printf_init(cb if enabled else CB());lib.am_util_stdio_textmode_set(translated);n=fn(fmt.encode(),ctypes.c_uint32(arg&0xffffffff));stock=u.reg_read(v.a.UC_ARM_REG_R0);rows.append(dict(enabled=enabled,translated=translated,format=fmt,stock_count=stock,sdk_count=n,stock_events=m.events,sdk_events=events,match=stock==n and m.events==events))
r={'status':'PASS' if all(x['match'] for x in rows) else 'COUNTEREXAMPLE','cases':len(rows),'comparisons':rows,'negative_controls':{'changed_sink_bytes_rejected':rows[-1]['stock_events']!=['00']},'limits':['Native original printf wrapper and parser, synthetic synchronous sink.','No concurrent/reentrant sink, long output, null strings or formatter overflow tested.','This printf API has no destination-capacity argument; no safe truncation contract implied.']};assert all(r['negative_controls'].values());Path(__file__).with_name('sinks.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],len(rows))
