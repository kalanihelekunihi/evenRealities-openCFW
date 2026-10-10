from pathlib import Path
import zipfile,hashlib,json,re,struct
O=Path(__file__).resolve().parent;sha=lambda b:hashlib.sha256(b).hexdigest();rows=[]
def members(a):
 assert a[:8]==b'!<arch>\n';p=8;long=b'';out=[]
 while p<len(a):
  h=a[p:p+60];n=int(h[48:58]);name=h[:16].decode().strip();b=a[p+60:p+60+n];p+=60+n+(n&1)
  if name=='//':long=b
  elif name.startswith('/') and name[1:].isdigit():name=long[int(name[1:]):].split(b'/\n',1)[0].decode()
  out.append((name.rstrip('/'),b))
 return out
with zipfile.ZipFile('/Users/kalani/Downloads/AmbiqSuite_5.2.0.zip') as z:
 for name in z.namelist():
  if '/ThinkSi/config/' not in name or not name.endswith(('.a','.lib')) or not any(x in name for x in ['/iar/bin/','/keil6/bin/','/gcc/bin/']):continue
  a=z.read(name);ms=members(a);elf=[(n,b) for n,b in ms if b[:4]==b'\x7fELF'];selected=[]
  for n,b in elf:
   if n not in ['nema_cmdlist.o','nema_matrix.o','nema_blender.o']:continue
   h=struct.unpack_from('<HHIIIIIHHHHHH',b,16);ss=[struct.unpack_from('<10I',b,h[5]+i*h[10]) for i in range(h[11])];names=ss[h[12]];st=b[names[4]:names[4]+names[5]];sects=[]
   for s in ss:
    sn=st[s[0]:].split(b'\0',1)[0].decode()
    if s[2]&4 or s[1] in [2,4,9] or sn in ['.ARM.attributes','.iar.rtmodel','.strtab']:sects.append({'name':sn,'flags':s[2],'type':s[1],'bytes':s[5],'sha256':sha(b[s[4]:s[4]+s[5]])})
   selected.append({'member':n,'sha256':sha(b),'elf_machine':h[1],'elf_type':h[0],'elf_flags':hex(h[6]),'producer_strings':sorted(set(x.decode(errors='replace') for x in re.findall(rb'(?:IAR ANSI[^\x00\r\n]+|GNU C[^\x00\r\n]+|clang version[^\x00\r\n]+|ARM Compiler[^\x00\r\n]+)',b))),'executable_sections':sects})
  rows.append({'zip_member':name,'archive_sha256':sha(a),'archive_bytes':len(a),'elf_members':len(elf),'selected':selected})
(O/'VARIANTS.json').write_text(json.dumps({'variants':rows,'scope':'In-memory ZIP/ar/ELF metadata only; no binary extraction, redistribution or code execution. No new package hash/CRC claim beyond earlier authenticated input.'},indent=2)+'\n')
print(json.dumps([{'archive':r['zip_member'].split('/config/')[1],'sha256':r['archive_sha256'],'selected':[{k:v for k,v in m.items() if k not in ['executable_sections']} for m in r['selected']]} for r in rows],indent=2))
