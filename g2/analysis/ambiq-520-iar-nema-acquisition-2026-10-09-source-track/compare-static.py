from pathlib import Path
import struct,hashlib,json
p=Path(__file__).parent
ar=(p/'extracted/third_party/ThinkSi/config/apollo510_nemagfx/iar/bin/lib_nema_apollo510_nemagfx.a').read_bytes();off=8;obj=None
while off+60<=len(ar):
 h=ar[off:off+60];n=int(h[48:58]);name=h[:16].decode().strip().rstrip('/');b=ar[off+60:off+60+n]
 if name=='nema_cmdlist.o':obj=b
 off+=60+n+(n&1)
assert obj and obj[:6]==b'\x7fELF\x01\x01'
shoff=struct.unpack_from('<I',obj,32)[0];shsize,shnum,shstr=struct.unpack_from('<HHH',obj,46)
ss=[struct.unpack_from('<10I',obj,shoff+i*shsize) for i in range(shnum)]
def data(s):return obj[s[4]:s[4]+s[5]]
def cstr(b,i):return b[i:b.find(b'\0',i)].decode(errors='replace')
strings=data(ss[shstr]);names=[cstr(strings,s[0]) for s in ss];syms=[]
for i,s in enumerate(ss):
 if s[1]==2:
  st=data(ss[s[6]])
  syms=[{'name':cstr(st,x[0]),'value':x[1],'size':x[2],'info':x[3],'section':x[5]} for x in struct.iter_unpack('<IIIBBH',data(s))]
target=[s for s in syms if s['name']=='nema_cl_bind_sectored_circular'];assert len(target)==1
sym=target[0];section=ss[sym['section']];text=data(section);begin=sym['value']&~1;body=text[begin:begin+sym['size']];rel=[]
for i,s in enumerate(ss):
 if s[1] in [9,4] and s[7]==sym['section']:
  for x in struct.iter_unpack('<II' if s[1]==9 else '<IIi',data(s)):
   rel.append({'offset':x[0],'type':x[1]&255,'symbol':syms[x[1]>>8]['name'],'addend':x[2] if len(x)>2 else None})
stockp=Path('g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin');allstock=stockp.read_bytes();stock=allstock[0x20:];start=0x5143d4;end=0x5144ba;sb=stock[start-0x438000:end-0x438000];assert hashlib.sha256(sb).hexdigest()=='1b72806af461fbd44dc0a8928e9a4b4493d124242f8f89f7d5820d0c8c692b6d'
r={'object':'nema_cmdlist.o','symbol':sym,'section_name':names[sym['section']],'complete_section_bytes':len(text),'symbol_bytes':len(body),'section_sha256':hashlib.sha256(text).hexdigest(),'symbol_sha256':hashlib.sha256(body).hexdigest(),'relocations':rel,'stock_package_sha256':hashlib.sha256(allstock).hexdigest(),'stock_start':hex(start),'stock_end':hex(end),'stock_bytes':len(sb),'stock_sha256':hashlib.sha256(sb).hexdigest(),'unlinked_symbol_byte_equality':body==sb,'unlinked_section_byte_equality':text==sb,'no_relocation_normalization':True,'code_executed':False}
(p/'STATIC-COMPARISON.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
