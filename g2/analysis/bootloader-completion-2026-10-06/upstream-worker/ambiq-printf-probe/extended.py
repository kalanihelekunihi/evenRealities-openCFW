import ctypes,hashlib,importlib.util,json,struct,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5];p=ROOT/'g2/components/bootloader/initializer_callbacks/verify_context_interrupt.py';s=importlib.util.spec_from_file_location('base',p);v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
lib=ctypes.CDLL('/tmp/opencfw-ambiq-printf.dylib');fn=lib.am_util_stdio_sprintf;fn.argtypes=[ctypes.c_void_p,ctypes.c_char_p];fn.restype=ctypes.c_uint32;lib.am_util_stdio_textmode_set.argtypes=[ctypes.c_bool]
cases=[('%s',[('s','abc')]),('%8s',[('s','abc')]),('%-8s',[('s','abc')]),('%.2s',[('s','abcdef')]),('%s',[('s','')]),('%lld',[('q',-9223372036854775808)]),('%llu',[('q',18446744073709551615)]),('%016llx',[('q',0x123456789abcdef)]),('%d:%llu',[('i',7),('q',0x123456789abcdef)]),('%f',[('f',1.25)]),('%.2f',[('f',-1.25)]),('%12.3f',[('f',12.125)]),('%f',[('f',0.)]),('%f',[('f',-0.)]),('%f',[('f',math.inf)]),('%f',[('f',-math.inf)]),('%f',[('f',math.nan)]),('%.0f',[('f',1.5)]),('%.20f',[('f',1.25)]),('%*d',[('i',5),('i',7)]),('a\nb',[]),('%s',[('s','a\nb')])]
rows=[];trace={};blob=v.BLOB.read_bytes();flag=int.from_bytes(blob[0x415fe0-v.BASE:0x415fe4-v.BASE],'little');assert flag==0x200271c4
for textmode in [False,True]:
 for fmt,args in cases:
  m=v.Machine(False);cpu=m.cpu;cpu.mem_write(flag,bytes([textmode]));cpu.mem_write(0x20001000,fmt.encode()+b'\0');words=bytearray();host=[];strings=[]
  for k,val in args:
   if k in ['q','f']:
    while len(words)%8:words+=bytes(4)
    words+=struct.pack('<Q',val&0xffffffffffffffff) if k=='q' else struct.pack('<d',val);host.append(ctypes.c_uint64(val&0xffffffffffffffff) if k=='q' else ctypes.c_double(val))
   elif k=='s':
    ptr=0x20004000+len(strings)*512;cpu.mem_write(ptr,val.encode()+b'\0');words+=struct.pack('<I',ptr);strings.append(ctypes.create_string_buffer(val.encode()));host.append(ctypes.cast(strings[-1],ctypes.c_char_p))
   else:words+=struct.pack('<I',val&0xffffffff);host.append(ctypes.c_uint32(val&0xffffffff))
  cpu.mem_write(0x20003000,bytes(words)+bytes(32));cpu.reg_write(v.a.UC_ARM_REG_SP,v.SP);cpu.reg_write(v.a.UC_ARM_REG_LR,v.STOP|1)
  for reg,val in [(v.a.UC_ARM_REG_R0,0x20002000),(v.a.UC_ARM_REG_R1,0x20001000),(v.a.UC_ARM_REG_R2,0x20003000)]:cpu.reg_write(reg,val)
  row={'format':fmt,'arguments':repr(args),'translation':textmode}
  try:
   cpu.emu_start(0x415bf7,v.STOP+2,count=300000);assert m.done,'instruction limit';raw=bytes(cpu.mem_read(0x20002000,256)).split(b'\0')[0];count=cpu.reg_read(v.a.UC_ARM_REG_R0);lib.am_util_stdio_textmode_set(textmode);out=ctypes.create_string_buffer(256);n=fn(out,fmt.encode(),*host);row.update(stock_bytes=raw.hex(),sdk_bytes=out.value.hex(),stock_count=count,sdk_count=n,match=raw==out.value and count==n)
  except Exception as e:row['blocker']=str(e);row['stop_pc']=hex(cpu.reg_read(v.a.UC_ARM_REG_PC));row['stop_bytes']=bytes(cpu.mem_read(cpu.reg_read(v.a.UC_ARM_REG_PC),4)).hex()
  rows.append(row);trace.update(m.trace)
r={'status':'COUNTEREXAMPLE' if any(x.get('match')==False for x in rows) else 'BOUNDED','cases':len(rows),'matches':sum(x.get('match',False) for x in rows),'blocked':sum('blocker' in x for x in rows),'stock_sha256':hashlib.sha256(blob).hexdigest(),'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'comparisons':rows,'original_trace':{hex(p):b for p,b in trace.items()},'limits':['Original instructions; no external helper or FP effect stubs. Host SDK code, not matching compiler. Synthetic argument layout uses ARM eight-byte alignment.','No safety claim for excessive output/null string; no truncation API equivalence implied.']}
Path(__file__).with_name('extended.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['status','cases','matches','blocked']}));print(json.dumps([x for x in rows if x.get('match')==False or 'blocker' in x]))
