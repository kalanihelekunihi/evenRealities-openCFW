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
symbol=lookup['opencfw_em9305_init_state_status_334458'];assert symbol[2]==6
actual=raw(sections[symbol[3]])[symbol[1]:symbol[1]+6]
assert actual==native[0x334458-0x302400:0x33445e-0x302400]==bytes([0,0,8,12,12,0])
assert native[0x33445e-0x302400:0x334464-0x302400]==bytes([0,0,8,0,0,0])
r={'status':'PASS','native_descriptor_bytes_checked':12,'target_emitted_descriptor_bytes_exact':6,'target_zero_status_descriptor':'optimized into instructions; not claimed as emitted object bytes','target_object_sha256':hashlib.sha256(b).hexdigest(),'scope':'native semantic constant contracts and emitted nonzero descriptor; host event tests cover both; not ARC/hardware execution'}
Path(__file__).with_name('init-state-status-target-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
