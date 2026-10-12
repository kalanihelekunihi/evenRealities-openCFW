"""Native-attributed channel state maps/typed relocations in ARC ELF32."""
import argparse,hashlib,json,struct
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('object');a=ap.parse_args()
b=Path(a.object).read_bytes();assert b[:6]==b'\x7fELF\x01\x01'
u=lambda fmt,o:struct.unpack_from('<'+fmt,b,o)
o=u('I',32)[0];sz,count,ss=u('HHH',46);sections=[u('10I',o+i*sz) for i in range(count)]
raw=lambda s:b[s[4]:s[4]+s[5]]
z=lambda buf,o:buf[o:buf.index(0,o)].decode()
st=next(s for s in sections if s[1]==2);strings=raw(sections[st[6]]);syms=[]
for o in range(st[4],st[4]+st[5],st[9]):
 name,value,size,info,other,sec=u('IIIBBH',o);syms.append((z(strings,name),value,size,sec))
lookup={s[0]:s for s in syms}
native=Path('g2/build/c-firmware/20261011/em-activation-round/em-inspection.bin').read_bytes();assert hashlib.sha256(native).hexdigest()=='0de6e945a56ec886a92e44d4eaefe02fbca6db11f8747876e30bffb45cffce03'
prefix='opencfw_em9305_associated_channel_'
for name,address,size in [('event_kind',0x3344a4,6),('event_action',0x3344aa,6),('transitions',0x334b18,8)]:
 s=lookup[prefix+name];assert s[2]==size;assert raw(sections[s[3]])[s[1]:s[1]+size]==native[address-0x302400:address-0x302400+size]
action=lookup[prefix+'actions'];assert action[2]==24;rel={}
for s in sections:
 if s[1]==4 and s[7]==action[3]:
  for o in range(s[4],s[4]+s[5],s[9]):
   off,info,addend=u('IIi',o)
   if action[1]<=off<action[1]+24:
    assert addend==0 and info&255==4;rel[(off-action[1])//4]=syms[info>>8][0]
expected=['channel_apply_3279d0','channel_reset_3279c4','channel_notify_3279a4','phy_notify_3279b4','phy_apply_327a04','phy_reset_327a3c']
words=struct.unpack_from('<6I',native,0x334b00-0x302400)
for i,name in enumerate(expected):
 assert rel[i]=='opencfw_em9305_associated_'+name
 assert int(name[-6:],16)==words[i]
r={'status':'PASS','map_transition_bytes_exact':20,'genuine_function_relocations':6,'target_object_sha256':hashlib.sha256(b).hexdigest(),'scope':'native table bytes and typed action identity; not runtime placement'}
Path(__file__).with_name('associated-channel-tables-target-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
