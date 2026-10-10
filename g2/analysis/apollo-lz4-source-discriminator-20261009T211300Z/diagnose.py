from pathlib import Path
import hashlib,json,ctypes,ast,struct
from unicorn import *
from unicorn.arm_const import *
r=Path('/repo');d=Path('/out');raw=(r/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];libs={}
for v in ['v1.9.4','v1.10.0']:
 l=ctypes.CDLL(str(d/v/'liblz4.so'));l.LZ4_decompress_safe.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_int];l.LZ4_decompress_safe.restype=ctypes.c_int;l.LZ4_compress_default.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_int];libs[v]=l
emu=Path('/emu/src/g2emu/device.py');txt=emu.read_text();node=next(n for n in ast.parse(txt).body if isinstance(n,ast.FunctionDef) and n.name=='_lz4_block_decompress');scope={'DeviceProtocolError':type('DeviceProtocolError',(Exception,),{})};exec(compile(ast.Module(body=[node],type_ignores=[]),str(emu),'exec'),scope)
fixtures=[]
def add(n,b,cap):fixtures.append({'name':n,'compressed_hex':b.hex(),'capacity':cap})
def literal(b):
 n=len(b);return bytes([min(n,15)<<4])+(bytes([255])*((n-15)//255)+bytes([(n-15)%255]) if n>=15 else b'')+b
for n in [0,1,4,5,14,15,16,20,270]:
 b=bytes((i*17+3)%256 for i in range(n))
 for cap in sorted(set([n,n+8,max(0,n-1)])):add('literal'+str(n)+'-cap'+str(cap),literal(b),cap)
for cap in [0,1,16]:add('zero-input-cap'+str(cap),b'',cap)
for name,b,cap in [('literal-token-only',b'\x10',32),('literal-missing-extension',b'\xf0',32),('literal-truncated-255-extension',b'\xf0\xff',512),('literal-claimed-six-have-five',b'\x60HELLO',32),('one-offset-byte',b'\x10A\x01',32),('offset-past-history',b'\x1fA\x02\x00\x01\x50abcde',26),('zero-offset',b'\x1fA\x00\x00\x01\x50abcde',26),('match-no-last-literals',b'\x1fA\x01\x00\x01',26),('match-four-last-literals',b'\x1fA\x01\x00\x01\x40abcd',25),('match-three-last-literals',b'\x1fA\x01\x00\x01\x30abc',24),('last-match-too-late',b'\x10A\x01\x00\x50abcde',10),('overlap-valid',b'\x1fA\x01\x00\x01\x50abcde',26),('overlap-small-cap',b'\x1fA\x01\x00\x01\x50abcde',25),('match-missing-extension',b'\x1fA\x01\x00',32),('match-truncated-255-extension',b'\x1fA\x01\x00\xff',512)]:add(name,b,cap)
for name,b in [('zeroes',bytes(128)),('repeat',b'ABCD'*64),('ramp',bytes(range(256))),('sparse',bytes([1])+bytes(126)+bytes([2]))]:
 src=ctypes.create_string_buffer(b);out=ctypes.create_string_buffer(len(b)+64);n=libs['v1.10.0'].LZ4_compress_default(src,out,len(b),len(out));assert n>0
 for cap in [len(b)-1,len(b),len(b)+8]:add('official-compressed-'+name+'-cap'+str(cap),out.raw[:n],cap)
SRC=0x20020020;DST=0x20030020;STOP=0x20080000
allowed=[(0x54ee3e,0x54f356),(0x439710,0x4397a6),(0x439be4,0x439c8a)]
def stock(data,cap):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,((len(raw)+4095)//4096)*4096);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x100000);u.mem_write(SRC-16,b'\x6b'*16+data+b'\x6c'*32);u.mem_write(DST-16,b'\x7b'*16+b'\xa5'*cap+b'\x7c'*32);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,STOP|1)
 for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[SRC,DST,len(data),cap]):u.reg_write(reg,value)
 pcs=set();bad=[];done=[];writes=[];trace=[];entry_calls=[]
 def hook(uc,pc,size,user):
  if pc==STOP:done.append(True);uc.emu_stop();return
  if not any(a<=pc<b for a,b in allowed):bad.append(hex(pc));uc.emu_stop();return
  pcs.add(pc)
  trace.append([hex(pc),*[hex(uc.reg_read(reg)) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR]]]);trace[:]=trace[-20:]
  if pc in [0x439be4,0x439710]:entry_calls.append([hex(pc),*[hex(uc.reg_read(reg)) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR]]])
 def write(uc,access,a,n,v,user):
  if DST-16<=a<DST+cap+32:writes.append([hex(a-DST),n,v])
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,write)
 try:u.emu_start(0x54f339,0,count=200000)
 except UcError as e:return {'infrastructure_error':str(e),'pc':hex(u.reg_read(UC_ARM_REG_PC)),'bad_pc':bad}
 if not done or bad:
  problem={'pc':hex(u.reg_read(UC_ARM_REG_PC)),'bad':bad,'entry_calls':entry_calls,'trace_tail':trace}
  (d/'first_execution_blocker.json').write_text(json.dumps(problem,indent=2)+'\n')
  raise AssertionError(problem)
 ret=u.reg_read(UC_ARM_REG_R0);ret=ret if ret<0x80000000 else ret-0x100000000
 guards={'source_unchanged':bytes(u.mem_read(SRC,len(data)))==data,'source_before':bytes(u.mem_read(SRC-16,16))==b'\x6b'*16,'source_after':bytes(u.mem_read(SRC+len(data),32))==b'\x6c'*32,'destination_before':bytes(u.mem_read(DST-16,16))==b'\x7b'*16,'destination_after':bytes(u.mem_read(DST+cap,32))==b'\x7c'*32}
 return {'return':ret,'output_capacity_hex':bytes(u.mem_read(DST,cap)).hex(),'guards':guards,'writes':writes,'visited_pcs':[hex(x) for x in sorted(pcs)]}
def native(l,data,cap):
 src=ctypes.create_string_buffer(data+b'\x6c'*32);out=ctypes.create_string_buffer(b'\x7b'*16+b'\xa5'*cap+b'\x7c'*32);ret=l.LZ4_decompress_safe(src,ctypes.byref(out,16),len(data),cap)
 return {'return':ret,'output_capacity_hex':out.raw[16:16+cap].hex(),'destination_before':out.raw[:16]==b'\x7b'*16,'destination_after':out.raw[16+cap:16+cap+32]==b'\x7c'*32}
print(json.dumps(stock(literal(bytes([3,20,37,54,71])),5),indent=2))
