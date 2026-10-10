from pathlib import Path
import struct,json,hashlib,re
O=Path(__file__).resolve().parent;A=Path('g2/analysis/ambiq-520-iar-nema-acquisition-2026-10-09-source-track/extracted/third_party/ThinkSi/config/apollo510_nemagfx/iar/bin/lib_nema_apollo510_nemagfx.a');a=A.read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest();assert sha(a)=='8c6204496ab53860241db9236487a0eb93badf9627be4eea55249847813827e7';p=8
while p<len(a):
 hdr=a[p:p+60];n=int(hdr[48:58]);name=hdr[:16].decode().strip();b=a[p+60:p+60+n];p+=60+n+(n&1)
 if name=='nema_cmdlist.o/':break
assert b[:4]==b'\x7fELF';h=struct.unpack_from('<HHIIIIIHHHHHH',b,16);ss=[struct.unpack_from('<10I',b,h[5]+i*h[10]) for i in range(h[11])];st=ss[h[12]];strings=b[st[4]:st[4]+st[5]];sn=lambda i:strings[ss[i][0]:].split(b'\0',1)[0].decode();sy=[]
for i,s in enumerate(ss):
 if s[1]==2:
  t=ss[s[6]];names=b[t[4]:t[4]+t[5]]
  for j in range(0,s[5],s[9]):
   nm,val,size,info,other,idx=struct.unpack_from('<IIIBBH',b,s[4]+j);nm=names[nm:].split(b'\0',1)[0].decode();sy.append({'name':nm,'value':val,'size':size,'section':idx})
rows=[]
for sym in sy:
 if sym['name'] in ['nema_cl_bind_circular','nema_cl_bind_sectored_circular','nema_cl_rewind','nema_cl_get_bound']:
  idx=sym['section'];s=ss[idx];rel=[]
  for t in ss:
   if t[1] in [4,9] and t[7]==idx:
    for z in range(0,t[5],t[9]):
     off,info=struct.unpack_from('<II',b,t[4]+z);
     if (sym['value']&~1)<=off<(sym['value']&~1)+sym['size']:rel.append({'offset':off,'function_offset':off-(sym['value']&~1),'type':info&255,'symbol':sy[info>>8]['name']})
  rows.append({**sym,'section_name':sn(idx),'section_bytes':s[5],'section_sha256':sha(b[s[4]:s[4]+s[5]]),'function_sha256':sha(b[s[4]+(sym['value']&~1):s[4]+(sym['value']&~1)+sym['size']]),'relocations':rel})
raw=Path('g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];stock=[]
for line in Path('g2/symbols/apollo_main.tsv').read_text().splitlines():
 c=line.split('\t');start=int(c[0],16) if c[0].startswith('0x') else 0
 if start in [0x514384,0x5143d4,0x5144fa]:
  end=int(c[1],16);v=raw[start-0x438000:end-0x438000];assert sha(v)==c[-1];stock.append({'start':c[0],'end':c[1],'bytes':len(v),'sha256':sha(v),'canonical_classification':c[4:6]})
r={'archive_sha256':sha(a),'member':'nema_cmdlist.o','member_sha256':sha(b),'elf_type':h[0],'elf_machine':h[1],'compiler_strings':sorted(set(s.decode() for s in re.findall(rb'IAR ANSI[^\x00\r\n]+',b))),'targets':rows,'locked_stock':stock,'scope':'In-memory static parsing only; no extraction/execution or archive-byte redistribution. Stock names are historical attribution, extent hashes independently checked.'};(O/'NEMA-TARGET-BASELINE.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
