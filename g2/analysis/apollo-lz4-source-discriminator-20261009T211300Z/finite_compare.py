from pathlib import Path
import hashlib,json,ctypes,ast,struct
from unicorn import *
from unicorn.arm_const import *
r=Path('/repo');d=Path('/out');raw=(r/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];libs={}
for v in ['v1.9.4','v1.10.0']:
 l=ctypes.CDLL(str(d/v/'liblz4.so'));l.LZ4_decompress_safe.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_int];l.LZ4_decompress_safe.restype=ctypes.c_int;l.LZ4_compress_default.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_int];libs[v]=l
emu=Path('/emu/src/g2emu/device.py');txt=emu.read_text();node=next(n for n in ast.parse(txt).body if isinstance(n,ast.FunctionDef) and n.name=='_lz4_block_decompress');scope={'DeviceProtocolError':type('DeviceProtocolError',(Exception,),{})};exec(compile(ast.Module(body=[node],type_ignores=[]),str(emu),'exec'),scope)
fixtures=[{'name':name,'compressed_hex':data.hex(),'capacity':cap} for name,data,cap in [
('empty-input',b'',16),('encoded-empty',b'\x00',0),('literal-exact',b'\x50HELLO',5),('literal-short-cap',b'\x50HELLO',4),('truncated-literal-extension',b'\xf0',16),('truncated-literal-payload',b'\x60HELLO',6),('truncated-offset',b'\x1fA\x01',26),('zero-offset',b'\x1fA\x00\x00\x01\x50abcde',26),('offset-past-history',b'\x1fA\x02\x00\x01\x50abcde',26),('truncated-match-extension',b'\x1fA\x01\x00',26),('overlap-valid',b'\x1fA\x01\x00\x01\x50abcde',26),('overlap-short-cap',b'\x1fA\x01\x00\x01\x50abcde',25)]]
(d/'frozen-fixtures.json').write_text(json.dumps({'cases':fixtures,'scope':'12 reviewed semantic branch cases; safe API and separately locked caller; input/output guards at capacity','extra_exploratory_fixture_set':'not resumed after execution-profile failure; no result count claimed'},indent=2)+'\n')
SRC=0x20020020;DST=0x20030020;STOP=0x20080000
allowed=[(0x4e0c0c,0x4e0c34),(0x54ee18,0x54f356),(0x439710,0x4397a6),(0x439be4,0x439c8a)]
def stock(data,cap,caller=False):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,((len(raw)+4095)//4096)*4096);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x100000);u.mem_write(SRC-16,b'\x6b'*16+data+b'\x6c'*32);u.mem_write(DST-16,b'\x7b'*16+b'\xa5'*cap+b'\x7c'*32);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,STOP|1)
 for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],([SRC,len(data),DST,cap] if caller else [SRC,DST,len(data),cap])):u.reg_write(reg,value)
 pcs=set();bad=[];done=[];writes=[]
 def hook(uc,pc,size,user):
  if pc==STOP:done.append(True);uc.emu_stop();return
  if not any(a<=pc<b for a,b in allowed):bad.append(hex(pc));uc.emu_stop();return
  pcs.add(pc)
 def write(uc,access,a,n,v,user):
  if DST-16<=a<DST+cap+32:writes.append([hex(a-DST),n,v])
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,write)
 try:
  u.reg_write(UC_ARM_REG_PC,0x4e0c0d if caller else 0x54f339)
  for _ in range(20000):
   if done or bad:break
   u.emu_start(u.reg_read(UC_ARM_REG_PC)|1,0,count=1)
 except UcError as e:return {'infrastructure_error':str(e),'pc':hex(u.reg_read(UC_ARM_REG_PC)),'bad_pc':bad}
 assert done and not bad,{'pc':hex(u.reg_read(UC_ARM_REG_PC)),'bad':bad}
 ret=u.reg_read(UC_ARM_REG_R0);ret=ret if ret<0x80000000 else ret-0x100000000
 guards={'source_unchanged':bytes(u.mem_read(SRC,len(data)))==data,'source_before':bytes(u.mem_read(SRC-16,16))==b'\x6b'*16,'source_after':bytes(u.mem_read(SRC+len(data),32))==b'\x6c'*32,'destination_before':bytes(u.mem_read(DST-16,16))==b'\x7b'*16,'destination_after':bytes(u.mem_read(DST+cap,32))==b'\x7c'*32}
 return {'return':ret,'output_capacity_hex':bytes(u.mem_read(DST,cap)).hex(),'guards':guards,'writes':writes,'visited_pcs':[hex(x) for x in sorted(pcs)]}
def native(l,data,cap):
 src=ctypes.create_string_buffer(data+b'\x6c'*32);out=ctypes.create_string_buffer(b'\x7b'*16+b'\xa5'*cap+b'\x7c'*32);ret=l.LZ4_decompress_safe(src,ctypes.byref(out,16),len(data),cap)
 return {'return':ret,'output_capacity_hex':out.raw[16:16+cap].hex(),'destination_before':out.raw[:16]==b'\x7b'*16,'destination_after':out.raw[16+cap:16+cap+32]==b'\x7c'*32}
rows=[]
for f in fixtures:
 data=bytes.fromhex(f['compressed_hex']);a=stock(data,f['capacity']);assert 'infrastructure_error' not in a,a;assert all(a['guards'].values()),(f,a['guards']);wrapper=stock(data,f['capacity'],caller=True);assert 'infrastructure_error' not in wrapper and all(wrapper['guards'].values());assert wrapper['return']==max(a['return'],0),(f,a['return'],wrapper['return']);cs={v:native(l,data,f['capacity']) for v,l in libs.items()};assert all(x['destination_before'] and x['destination_after'] for x in cs.values())
 try:out=scope['_lz4_block_decompress'](data,max_output_size=f['capacity']);py={'status':'accepted','output_hex':out.hex()}
 except Exception as e:py={'status':'rejected','exception':type(e).__name__,'message':str(e)}
 match={v:{'return_equal':x['return']==a['return'],'full_capacity_equal':x['output_capacity_hex']==a['output_capacity_hex'],'success_bytes_equal':a['return']>=0 and x['return']==a['return'] and x['output_capacity_hex'][:2*a['return']]==a['output_capacity_hex'][:2*a['return']]} for v,x in cs.items()};rows.append({'fixture':f,'stock':a,'locked_caller':wrapper,'C':cs,'C_matches':match,'emulator_python':py});print(f['name'],a['return'],py['status'],flush=True)
(d/'finite-results.json').write_text(json.dumps({'fixtures':len(rows),'original_instructions':'All reached code executes locked stock bytes, including two IAR copy bodies and five LZ4 helpers; fixed instruction-by-instruction Unicorn profile after bounded provider verification. No external call stubs. Only return sentinel intercept. Guarded allowed-PC ranges.','rows':rows,'emulator_source_sha256':hashlib.sha256(emu.read_bytes()).hexdigest(),'emulator_function_sha256':hashlib.sha256(ast.get_source_segment(txt,node).encode()).hexdigest()},indent=2)+'\n')
