"""Check typed ARC table relocations against authenticated native action words."""
import argparse, hashlib, json, re, struct
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('object');ap.add_argument('--slave',action='store_true');ap.add_argument('--associated',action='store_true');a=ap.parse_args()
b=Path(a.object).read_bytes();assert b[:6]==b'\x7fELF\x01\x01'
u=lambda fmt,off:struct.unpack_from('<'+fmt,b,off)
shoff=u('I',32)[0];size,count,ss=u('HHH',46)
sections=[u('10I',shoff+i*size) for i in range(count)]
raw=lambda s:b[s[4]:s[4]+s[5]]
z=lambda buf,o:buf[o:buf.index(0,o)].decode()
names=raw(sections[ss]);sn=[z(names,s[0]) for s in sections]
si=next(i for i,s in enumerate(sections) if s[1]==2);st=sections[si];strings=raw(sections[st[6]])
symbols=[]
for o in range(st[4],st[4]+st[5],st[9]):
 name,value,n,info,other,sec=u('IIIBBH',o);symbols.append((z(strings,name),value,n,sec))
lookup={s[0]:s for s in symbols}
prefix='opencfw_em9305_associated_' if a.associated else ('opencfw_em9305_slave_phy_' if a.slave else 'opencfw_em9305_phy_')
aa,ta,n=(0x335328,0x335368,16) if a.associated else ((0x33565c,0x335704,42) if a.slave else (0x33522c,0x3352cc,40))
action=lookup[prefix+'actions_'+format(aa,'x')];trans=lookup[prefix+'transitions_'+format(ta,'x')]
native=Path('g2/build/c-firmware/20261011/em-activation-round/em-inspection.bin').read_bytes()
assert hashlib.sha256(native).hexdigest()=='0de6e945a56ec886a92e44d4eaefe02fbca6db11f8747876e30bffb45cffce03'
assert trans[2]==n and action[2]==n*4
assert raw(sections[trans[3]])[trans[1]:trans[1]+n]==native[ta-0x302400:ta-0x302400+n]
rel={}
for s in sections:
 if s[1]==4 and s[7]==action[3]:
  for o in range(s[4],s[4]+s[5],s[9]):
   off,info,addend=u('IIi',o)
   if action[1]<=off<action[1]+n*4:
    assert addend==0 and info&255==4
    rel[(off-action[1])//4]=symbols[info>>8][0]
words=struct.unpack_from('<'+str(n)+'I',native,aa-0x302400)
for i,w in enumerate(words):
 if w:assert rel[i]==('opencfw_em9305_associated_action_' if a.associated else 'opencfw_em9305_phy_action_')+format(w,'x'),(i,w,rel.get(i))
 else:assert i not in rel and struct.unpack_from('<I',raw(sections[action[3]]),action[1]+i*4)[0]==0
receipt={'status':'PASS','transition_bytes_exact':n,'action_slots':n,'genuine_function_relocations':len(rel),'target_object_sha256':hashlib.sha256(b).hexdigest(),'scope':'ARC ELF32 typed action identities and exact transition bytes; not runtime placement'}
output=Path('g2/analysis/c-source-completion-20261011/em9305/'+('associated' if a.associated else ('slave' if a.slave else 'master'))+'-phy-tables-target-receipt.json');output.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
