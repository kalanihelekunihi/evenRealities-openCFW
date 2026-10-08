"""Bounded generic formatter hypothesis: native SDK versus stock Thumb parser.
No firmware source import. Integer-only ABI fixtures; host compilation is not
stock code generation. Sink printf, float and 64-bit variadic ABI untested.
"""
import ctypes,hashlib,importlib.util,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]
p=ROOT/'g2/components/bootloader/initializer_callbacks/verify_context_interrupt.py'
s=importlib.util.spec_from_file_location('base',p);v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
lib=ctypes.CDLL('/tmp/opencfw-ambiq-printf.dylib');fn=lib.am_util_stdio_sprintf;fn.argtypes=[ctypes.c_void_p,ctypes.c_char_p];fn.restype=ctypes.c_uint32
cases=[('plain',()),('%d',(0,)),('%d',(-42,)),('%u',(4294967295,)),('%x',(0xabcdef,)),('%X',(0xabcdef,)),('%08x',(0x123,)),('%8d',(42,)),('%05d',(-42,)),('%c',(65,)),('a\nb',()),('%%',()),('%d:%u:%x',(-7,8,9)),('%q',(7,))]
rows=[];trace={}
for fmt,args in cases:
 m=v.Machine(False);cpu=m.cpu;fmtp=0x20001000;bufp=0x20002000;argp=0x20003000
 cpu.mem_write(fmtp,fmt.encode()+b'\0');cpu.mem_write(argp,b''.join(struct.pack('<I',a&0xffffffff) for a in args)+bytes(32));cpu.reg_write(v.a.UC_ARM_REG_SP,v.SP);cpu.reg_write(v.a.UC_ARM_REG_LR,v.STOP|1)
 for reg,val in [(v.a.UC_ARM_REG_R0,bufp),(v.a.UC_ARM_REG_R1,fmtp),(v.a.UC_ARM_REG_R2,argp)]:cpu.reg_write(reg,val)
 cpu.emu_start(0x415bf7,v.STOP+2,count=100000);assert m.done,fmt
 stock=bytes(cpu.mem_read(bufp,256)).split(b'\0')[0];count=cpu.reg_read(v.a.UC_ARM_REG_R0);out=ctypes.create_string_buffer(256);native=fn(out,fmt.encode(),*[ctypes.c_uint32(a&0xffffffff) for a in args]);matched=stock==out.value and count==native
 rows.append({'format':fmt,'arguments':args,'stock_bytes':stock.hex(),'sdk_bytes':out.value.hex(),'stock_count':count,'sdk_count':native,'match':matched});trace.update(m.trace)
out=ctypes.create_string_buffer(256);wrong=fn(out,b'%d',ctypes.c_uint32(43))
known=next(r for r in rows if r['format']=='%8d')
negative_controls={'changed_argument_rejected':out.value.hex()!=next(r for r in rows if r['format']=='%d' and r['arguments']==(-42,))['stock_bytes'],'changed_count_rejected':known['stock_count']!=known['sdk_count']+1}
assert all(negative_controls.values())
source=ROOT/'third-party/local-vendor/sources/AmbiqSuite_R3.2.0/utils/am_util_stdio.c'
r={'status':'PASS' if all(x['match'] for x in rows) else 'COUNTEREXAMPLE','cases':len(rows),'matches':sum(x['match'] for x in rows),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'stock_sha256':hashlib.sha256(v.BLOB.read_bytes()).hexdigest(),'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'original_trace':{hex(p):b for p,b in trace.items()},'comparisons':rows,'negative_controls':negative_controls,'host_library_sha256':hashlib.sha256(Path('/tmp/opencfw-ambiq-printf.dylib').read_bytes()).hexdigest(),'limits':['Host SDK integer sprintf compared to stock original Thumb vsprintf; not a stock compiler/byte match.','Synthetic argument memory; newline translation initialized false; no external sink.','Float, 64-bit, pointer/string and width-star behavior not certified.']}
Path(__file__).with_name('comparison.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['status','cases','matches']}))
