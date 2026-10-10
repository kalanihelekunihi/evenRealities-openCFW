from pathlib import Path
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
import hashlib,json
r=Path('/repo');d=Path('/out');raw=(r/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS);rows=[];calls=[];lines=[]
for start,end,name in [(0x54ee90,0x54ef06,'read_variable_length'),(0x54ef08,0x54f338,'LZ4_decompress_generic'),(0x54f338,0x54f356,'LZ4_decompress_safe')]:
 b=raw[start-0x438000:end-0x438000];row={'name':name,'start':hex(start),'end':hex(end),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()};rows.append(row);lines.append('\n'+name)
 for ins in md.disasm(b,start):
  lines.append(f'{ins.address:08x}: {ins.bytes.hex()} {ins.mnemonic} {ins.op_str}')
  if ins.mnemonic in ['bl','blx']:calls.append({'caller':hex(ins.address),'instruction':ins.mnemonic+' '+ins.op_str})
(d/'original-disassembly.txt').write_text('\n'.join(lines)+'\n');(d/'stock-bindings.json').write_text(json.dumps({'raw_sha256':hashlib.sha256(raw).hexdigest(),'base':'0x438000','functions':rows,'calls':calls},indent=2)+'\n');print(json.dumps(calls));print('\n'.join(lines[-18:]))
