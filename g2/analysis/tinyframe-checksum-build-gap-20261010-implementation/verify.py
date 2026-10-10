from pathlib import Path
import hashlib,json,struct
D=Path(__file__).parent;R=D.resolve().parents[2];b=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();read=lambda a,n:b[a-0x438000+32:a-0x438000+32+n];sha=lambda x:hashlib.sha256(x).hexdigest()
assert sha(b)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';tableva=int.from_bytes(read(0x491ef0,4),'little');raw=read(tableva,512);table=struct.unpack('<256H',raw)
expected=[]
for i in range(256):
 c=i
 for j in range(8):c=(c>>1)^ (0xa001 if c&1 else 0)
 expected.append(c)
assert list(table)==expected
(D/'crc-table.bin').write_bytes(raw);x=read(0x491730,30);(D/'checksum-update.bin').write_bytes(x)
checks=0
for crc in [0,1,0xff,0x100,0x1234,0x8000,0xffff]:
 for byte in range(256):
  reference=crc^byte
  for j in range(8):reference=(reference>>1)^(0xa001 if reference&1 else 0)
  stockprojection=table[(crc^byte)&255]^(crc>>8);assert reference==stockprojection;checks+=1
(D/'verification.json').write_text(json.dumps(dict(table_address=hex(tableva),table_length=512,table_sha256=sha(raw),all_256_entries_match_reflected_polynomial='0xa001',update_address='0x491730',update_length=30,update_sha256=sha(x),static_arithmetic_checks=checks,original_execution=False,source_compilation=False),indent=2)+'\n');print('256 table entries and 1792 static arithmetic projections PASS')
