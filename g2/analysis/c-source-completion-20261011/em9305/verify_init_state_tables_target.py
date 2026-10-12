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
action=lookup['opencfw_em9305_init_state_actions_334f20'];assert action[2]==64;rel={}
transition=lookup['opencfw_em9305_init_state_transitions_334f60'];assert transition[2]==16
assert raw(sections[transition[3]])[transition[1]:transition[1]+16]==native[0x334f60-0x302400:0x334f70-0x302400]
for section in sections:
 if section[1]==4 and section[7]==action[3]:
  for offset in range(section[4],section[4]+section[5],section[9]):
   off,info,addend=u('IIi',offset)
   if action[1]<=off<action[1]+64:
    assert addend==0 and info&255==4;rel[(off-action[1])//4]=syms[info>>8][0]
words=struct.unpack_from('<16I',native,0x334f20-0x302400)
source_bytes=raw(sections[action[3]])[action[1]:action[1]+64]
for i,address in enumerate(words):
 if address==0:
  assert i not in rel and source_bytes[i*4:i*4+4]==b'\0'*4
 else:
  assert rel[i]==f'opencfw_em9305_init_state_action_{address:x}'
r={'status':'PASS','transition_bytes_exact':16,'genuine_function_relocations':len(rel),'authenticated_null_slots':16-len(rel),'target_object_sha256':hashlib.sha256(b).hexdigest(),'scope':'native action/transition identities and typed source relocations; not runtime placement or child behavior'}
Path(__file__).with_name('init-state-tables-target-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
