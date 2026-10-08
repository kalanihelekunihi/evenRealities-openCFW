import ctypes,hashlib,importlib.util,json,struct,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5];p=ROOT/'g2/components/bootloader/initializer_callbacks/verify_context_interrupt.py';s=importlib.util.spec_from_file_location('base',p);v=importlib.util.module_from_spec(s);s.loader.exec_module(v);old=v.Uc
model=__import__('sys').argv[1] if len(__import__('sys').argv)>1 else 'A9'
def oracle(arch,mode):
 u=old(arch,mode & ~v.UC_MODE_MCLASS);u.ctl_set_cpu_model(getattr(v.a,'UC_CPU_ARM_CORTEX_'+model));u.reg_write(v.a.UC_ARM_REG_C1_C0_2,0xf<<20);u.reg_write(v.a.UC_ARM_REG_FPEXC,0x40000000);u.reg_write(v.a.UC_ARM_REG_FPSCR,0);return u
v.Uc=oracle
lib=ctypes.CDLL('/tmp/opencfw-ambiq-precision.dylib');fn=lib.am_util_stdio_printf;fn.argtypes=[ctypes.c_char_p];fn.restype=ctypes.c_uint32;CB=ctypes.CFUNCTYPE(None,ctypes.c_char_p);lib.am_util_stdio_printf_init.argtypes=[CB]
class M(v.Machine):
 def __init__(self):super().__init__(False);self.events=[];self.fp=[]
 def code(self,u,pc,n,z):
  if pc==0x415f52:self.fp.append({'double_bits':hex(u.reg_read(v.a.UC_ARM_REG_D0)),'fpscr_before':hex(u.reg_read(v.a.UC_ARM_REG_FPSCR))})
  if pc==0x415ab6:self.fp[-1].update(single_bits=hex(u.reg_read(v.a.UC_ARM_REG_S0)),precision=u.reg_read(v.a.UC_ARM_REG_R1))
  if pc==0x08000100:
   ptr=u.reg_read(v.a.UC_ARM_REG_R0);self.events.append(bytes(u.mem_read(ptr,512)).split(b'\0')[0].hex());u.reg_write(v.a.UC_ARM_REG_PC,u.reg_read(v.a.UC_ARM_REG_LR));return
  super().code(u,pc,n,z)
rows=[]
for fmt in ['%f','%.0f','%.2f','%.6f']:
 for value in [1.25,-1.25,0.,-0.,1.363995,1.996,math.inf,-math.inf,math.nan]:
  for prefix in [False,True]:
   format=('%d:'+fmt) if prefix else fmt;m=M();u=m.cpu;u.mem_write(0x200270cc,struct.pack('<I',0x08000101));u.mem_write(0x20001000,format.encode()+b'\0');u.reg_write(v.a.UC_ARM_REG_SP,v.SP);u.reg_write(v.a.UC_ARM_REG_LR,v.STOP|1);u.reg_write(v.a.UC_ARM_REG_R0,0x20001000);u.reg_write(v.a.UC_ARM_REG_R1,7 if prefix else 0);bits=int.from_bytes(struct.pack('<d',value),'little');u.reg_write(v.a.UC_ARM_REG_R2,bits&0xffffffff);u.reg_write(v.a.UC_ARM_REG_R3,bits>>32);u.emu_start(0x415faf,v.STOP+2,count=300000);assert m.done;events=[];cb=CB(lambda b:events.append(b.hex()));lib.am_util_stdio_printf_init(cb);n=fn(format.encode(),*([ctypes.c_uint32(7)] if prefix else []),ctypes.c_double(value));assert m.fp[0]['double_bits']==hex(bits);assert m.events==events and u.reg_read(v.a.UC_ARM_REG_R0)==n,(format,value,m.events,events)
   rows.append({'format':format,'value':repr(value),'original':m.events,'count':n,'conversion':m.fp})
r={'status':'PASS','cases':len(rows),'model':model,'comparisons':rows,'negative_controls':{'incorrect_double_bits_rejected':rows[0]['conversion'][0]['double_bits']!=hex(0)},'limits':['Native original variadic printf wrapper executes; synthetic synchronous sink only. ARM R2/R3 double alignment checked via observed D0; prefix int in R1 tested.','A9/A15 instruction oracle with FPSCR default round-nearest, not M-profile scheduling or hardware proof.','NaN payloads/exception flags and concurrent sinks not certified.']};Path(__file__).with_name('float-wrapper-'+model.lower()+'.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS',model,len(rows))
