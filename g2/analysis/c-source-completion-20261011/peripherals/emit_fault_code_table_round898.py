#!/usr/bin/env python3
"""Emit the 43 authenticated Apollo fault-code rows as relocatable C data."""
from pathlib import Path
import hashlib,json,struct

root=Path(__file__).resolve().parents[3]
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
base=0x438000;start=0x6c8e60
rows=[]
for i in range(43):
 code,pad,ptr=struct.unpack_from('<HHI',blob,start-base+8*i)
 assert pad==0 and base<=ptr<base+len(blob),(i,code,pad,ptr)
 raw=blob[ptr-base:ptr-base+256].split(b'\0')[0]
 assert raw and len(raw)<256
 message=raw.decode('ascii')
 rows.append((code,message))
assert rows[0]==(0,'Successful.') and rows[1]==(1,'Invalid parameter supplied.')
assert rows[-1]==(0x2a,'Not enough credits.')
assert struct.unpack_from('<H',blob,start-base+43*8)[0]!=0x2b
lines=['/* Apollo 0x6c8e60: 43 fault-code rows from the official image.',
       ' * Pointers are C relocations; final ROM placement remains open. */',
       '#include <stdint.h>',
       'struct audio_fault_code_row { uint16_t code, reserved; const char *message; };',
       '_Static_assert(sizeof(struct audio_fault_code_row)==8u,"fault row ABI");',
       'const struct audio_fault_code_row audio_fault_code_table[43] = {']
for code,message in rows:
 lines.append(f'    {{0x{code:04x}u, 0u, {json.dumps(message)}}},')
lines.append('};')
dest=root/'components/audio/uart_thread_source_candidate/fault_code_table_6c8e60.c'
dest.write_text('\n'.join(lines)+'\n')
print('EMITTED_FAULT_CODE_ROWS',len(rows),hashlib.sha256(dest.read_bytes()).hexdigest())
