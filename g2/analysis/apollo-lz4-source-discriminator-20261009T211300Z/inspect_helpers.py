from pathlib import Path
from capstone import *
import json,hashlib
r=Path('/repo');d=Path('/out');raw=(r/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS);rows=[];lines=[]
for a,b in [(0x439710,0x4397a6),(0x439be4,0x439c8a),(0x54ee3e,0x54ee4e),(0x54ee4e,0x54ee6e),(0x54ee6e,0x54ee8c)]:
 code=raw[a-0x438000:b-0x438000];rows.append({'start':hex(a),'end':hex(b),'bytes':len(code),'sha256':hashlib.sha256(code).hexdigest()});lines.append('\n'+hex(a));lines += [f'{i.address:08x}: {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in md.disasm(code,a)]
(d/'helper-disassembly.txt').write_text('\n'.join(lines)+'\n');(d/'helper-bindings.json').write_text(json.dumps(rows,indent=2)+'\n');print('\n'.join(lines[:33]))
