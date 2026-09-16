# SPDX-License-Identifier: MIT
"""Compose OTP identification with the decoded source string helpers."""
import json
import subprocess
from build_gx8002_backup_strings import build as strings_build
from build_gx8002_backup_flash_otp_configuration import build, ROOT, IMAGE, IMAGE_SHA, sha
from verify_gx8002_backup_flash_otp_configuration import execute
from verify_gx8002_stage2_libc import execute as leaf, base_registers, load_buffer
from verify_gx8002_memcpy_source import decode
from build_transparent_image import Elf32


def verify():
    evidence={'otp':build(),'strings':strings_build()}
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    wrapped=Elf32(path.read_bytes(),'stock')
    assert sha(IMAGE.read_bytes())==IMAGE_SHA
    assert sha(wrapped.contents(next(s for s in wrapped.sections if s['name']=='.data')))==IMAGE_SHA
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x4e014','--stop-address=0x4e08c',str(path)],text=True))
    new=decode((ROOT/'build/gx8002-backup-flash-otp-configuration/configuration.disassembly.txt').read_text())
    strings=decode((ROOT/'build/gx8002-backup-strings/strings.disassembly.txt').read_text())
    samples=[b'8003A'[:n] for n in range(6)]
    for position in range(5):
        for value in range(256):
            content=bytearray(b'8003A');content[position]=value;samples.append(bytes(content))
    calls=0
    def hook(target,args,memory):
        nonlocal calls
        state=dict(memory)
        load_buffer(state,0x10012aa4,b'8003A\0')
        registers=base_registers()
        registers.update({f'r{i}':value for i,value in enumerate(args)})
        calls+=1
        return leaf(strings,target,registers,state,preserved=(*range(4,12),14,15,16,17))
    for content in samples:
        results=[]
        for code,entry in ((old,0x4e014),(new,0x100156d4)):
            results.append(execute(code,entry,24576000,0x20016d80,0,content,0xffffffff,string_hook=hook))
        assert results[0]==results[1]
        assert results[0][0]==0 and results[0][1]==(0x8003a if content==b'8003A' else 0x8002)
    assert calls==4*len(samples)
    report={'build':evidence,'cases':len(samples),'decoded_string_calls':calls,'source_admitted':False,
            'hardware_qualified':False,'limits':['Both stock and candidate OTP policies execute source strlen and strncmp with real stack contents. Clock, flash probe, OTP IO and logging remain modeled; no complete nested flash or hardware qualification.']}
    (ROOT/'docs/research/gx8002-backup-otp-strings.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':print(verify()['cases'])
