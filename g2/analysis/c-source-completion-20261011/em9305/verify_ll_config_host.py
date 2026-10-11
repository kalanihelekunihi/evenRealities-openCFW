#!/usr/bin/env python3
"""Host check of sparse field contract transcribed from ARC 0x30bc60.
Not an ARC instruction execution oracle or firmware/hardware qualification.
"""
import ctypes, json, subprocess, tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[4]
source=root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c'
text=source.read_text(); start=text.index('uint32_t opencfw_em9305_controller_ll_config_seed(uintptr_t destination)')
end=text.index('\n}',start)+2
fields=[(72,4,2500),(40,4,0x06060000),(24,1,10),(14,1,6),(4,1,13),(64,2,0),(62,2,0),(68,4,0xba040032),(66,2,0xc2d8),(58,1,4),(56,2,260),(54,2,140),(50,2,950),(48,1,4),(44,4,0x00fb0100),(38,2,256),(36,1,4),(32,4,0x04040100),(26,2,251),(20,4,0x20000),(18,1,64),(16,2,256),(12,2,514),(8,4,0),(0,4,0x7be2005a),(52,2,513),(60,2,10000),(28,4,0x04060000)]
with tempfile.TemporaryDirectory() as tmp:
 c=Path(tmp)/'config.c';so=Path(tmp)/'config.so'
 c.write_text('#include <stdint.h>\n'+text[start:end]+'\n')
 subprocess.run(['clang','-std=c11','-Wall','-Wextra','-Werror','-shared','-fPIC',str(c),'-o',str(so)],check=True)
 fn=ctypes.CDLL(str(so)).opencfw_em9305_controller_ll_config_seed
 fn.argtypes=[ctypes.c_size_t];fn.restype=ctypes.c_uint32
 for seed in range(256):
  initial=bytes((seed+i*37)&255 for i in range(96));expected=bytearray(initial)
  for offset,width,value in fields:expected[offset:offset+width]=value.to_bytes(width,'little')
  buf=(ctypes.c_uint8*96).from_buffer_copy(initial);address=ctypes.addressof(buf)
  assert fn(address)==address&0xffffffff
  assert bytes(buf)==expected,(seed,bytes(buf).hex(),expected.hex())
print(json.dumps({'passed':256,'scope':'host sparse field and untouched-byte contract; no ARC runtime equality'}))
