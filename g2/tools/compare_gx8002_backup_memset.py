# SPDX-License-Identifier: MIT
"""Verify backup-placement memset against stock and independent store oracle."""
import json,struct,subprocess
from build_gx8002_backup_memset import build,ROOT,IMAGE
from compare_gx8002_memset import execute,expected
from verify_gx8002_memcpy_source import decode

def verify():
    evidence=build();out=ROOT/'build/gx8002-backup-memset';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');w=out/'memset-stock.elf'
    subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True)
    b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x49d04','--stop-address=0x49da4',str(w)],text=True));new=decode((out/'memset-candidate.disassembly.txt').read_text());cases=0;prefixes=0
    def check(address,value,count,seed,prefix=None):
        want=expected(address,value,count,prefix)
        for code,pc in ((old,evidence['package_offset']),(new,evidence['runtime_address'])):
            if execute(code,pc,address,value,count,seed,prefix)!=want:raise ValueError('memset trace mismatch')
    for alignment in range(4):
     for count in (*range(36),63,64,65,160,164,255,256,257):
      for byte in range(256):
       check(0x20010000+alignment,0xdead0000|byte,count,byte);cases+=1
    for address in (0x20010000,0x20010001,0x20010002,0x20010003):
     for count in (1024,4095,4096,4097,25536,65536):
      for value in (0,0xffffffff,0x12345678):check(address,value,count,value);cases+=1
    for address in (0,1,2,3,0xfffffffc,0xfffffffd,0xfffffffe,0xffffffff):
     for count in (0,1,2,3,4,15,16,17,0x80000003,0x80000004,0xfffffffe,0xffffffff):
      check(address,0xffffffff,count,0xffffffff);cases+=1
     for count in (0x7fffffff,0x80000000,0x80000001,0x80000002):
      check(address,0x12345678,count,0xabcdef,32);prefixes+=1
    report={'build':evidence,'cases':cases,'large_count_prefix_cases':prefixes,'frame_bytes':0,'source_admitted':False,
      'limits':['Decoded ordered byte/word traces, normal lengths and wraparound arithmetic. Huge positive loop paths use32-store checkpoints, not full execution or valid-memory claims. No hardware/MMIO/timing qualification; arbitrary addresses in arithmetic cases are synthetic.']}
    (ROOT/'docs/research/gx8002-backup-memset-comparison.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(verify(),indent=2))
