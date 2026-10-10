from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[3];D=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
x=json.loads((D/'stock-receipts.json').read_text())
raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
assert sha(raw)==x['payload_sha256']
for r in x['ranges']:
 a=int(r['payload_offset'],16);b=raw[a:a+r['size']]
 assert b.hex()==r['original_bytes_hex'] and sha(b)==r['sha256']
image=raw[32:]
def bytes_at(a,n):return image[a-0x438000:a-0x438000+n].hex()
assert bytes_at(0x55c57a,2)=='7568' # module load handle+4
assert bytes_at(0x55c57c,4)=='96f83c08' # old bHP byte load +0x83c
assert bytes_at(0x55c582,2)=='7cd0' # direct zero branch to +0x55c67e
assert bytes_at(0x55cf6e,4)=='99f81400' # transaction direction byte +20
assert bytes_at(0x55d0c8,4)=='50f00400' # FULLDUP bit 2 set
assert bytes_at(0x55d0d0,4)=='c1f88002' # MSPICFG store +0x280
assert bytes_at(0x55d0d8,4)=='c0f82021' # CMD store +0x120
z=zipfile.ZipFile(Path.home()/'Downloads/AmbiqSuite_5.2.0.zip')
p='AmbiqSuite_5.2.0/AmbiqSuite_5.2.0/mcu/apollo510/hal/mcu/'
old=(R/'third-party/upstream/ambiqhal-apollo510/mcu/apollo510/hal/mcu/am_hal_iom.c').read_text()
new=z.read(p+'am_hal_iom.c').decode()
assert sha(old.encode())==x['source_hashes']['old_c'] and sha(new.encode())==x['source_hashes']['new_c']
def body(s,name):
 a=s.index(name+'(');b=s.index('{',a);depth=1;b+=1
 while depth:depth+=(s[b]=='{')-(s[b]=='}');b+=1
 return s[a:b]
assert body(old,'am_hal_iom_spi_blocking_fullduplex')==body(new,'am_hal_iom_spi_blocking_fullduplex')
assert 'am_hal_iom_spi_nonblocking_fullduplex(' not in old
assert 'am_hal_iom_spi_nonblocking_fullduplex(' in new
print('PASS: authenticated stock envelopes, seven instruction receipts, unchanged blocking source body, new-only FDNB definition')
