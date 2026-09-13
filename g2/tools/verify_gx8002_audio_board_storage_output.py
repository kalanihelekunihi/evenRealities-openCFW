# SPDX-License-Identifier: MIT
"""Exercise consecutive PCM1/logfbank setup on compiled deployed defaults."""
import json,subprocess
from itertools import product
from build_gx8002_audio_board_storage import build,ROOT,IMAGE_SHA,sha,Elf32
import verify_gx8002_audio_input_output as engine
import gx8002_audio_input_output_oracle as oracle
from verify_gx8002_memcpy_source import decode

def verify():
    candidate=build();path=ROOT/'build/gx8002-audio-board-storage/storage.elf';elf=Elf32(path.read_bytes(),'defaults');section=next(s for s in elf.sections if s['name']=='.board');body=elf.contents(section);base=section['address']
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x105fc','--stop-address=0x107c0',str(path)],text=True))
    path=ROOT/'build/gx8002-source-candidate/audio-input-output/output.elf';elf=Elf32(path.read_bytes(),'output');row=json.loads((ROOT/'docs/research/gx8002-audio-input-output-source-verification.json').read_text())['functions'][0];section=next(s for s in elf.sections if s['name']==row['section_name']);assert sha(elf.contents(section))==row['compiled_sha256']
    new=decode(subprocess.check_output([pre,'-d',str(path)],text=True));cases=0
    prior=(engine.BOARD,oracle.BOARD)
    try:
        engine.BOARD=oracle.BOARD=base
        for buffer,size,seed in product((0x20030400,0x20030417),(256,7680),(0,91,0xffffffff)):
            states=[body,body,body]
            for channel in (2,4):
                memories=[{base+i:v for i,v in enumerate(s)} for s in states]
                wanted=oracle.expected(2,channel,buffer,size,160,memories[0])
                a=engine.execute(old,0x105fc,2,channel,buffer,size,160,memories[1],seed)
                b=engine.execute(new,section['address'],2,channel,buffer,size,160,memories[2],seed)
                assert a==b==wanted, (channel,buffer,size,seed)
                states=[wanted[1],a[1],b[1]]
                cases+=2
            # The logfbank operation must preserve the populated PCM1 descriptor.
            assert states[0][148:172]==bytes(memories[0][base+i] for i in range(148,172))
    finally:engine.BOARD,oracle.BOARD=prior
    return {'candidate':candidate,'decoded_executions':cases,'output_elf_sha256':sha(path.read_bytes()),'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in ('verify_gx8002_audio_board_storage_output.py','build_gx8002_audio_board_storage.py','verify_gx8002_audio_input_output.py','gx8002_audio_input_output_oracle.py','verify_gx8002_memcpy_source.py')},'source_admitted':False,'hardware_qualified':False,'limits':['Consecutive PCM1 and logfbank configuration on original-address compiled defaults, compared with independent SDK-field oracle and stock instructions.','Buffer address/size and frame count supplied as stimuli; selectors, drivers and memcpy modeled. No physical audio execution.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-board-storage-output.json').write_text(json.dumps(r,indent=2)+'\n');print('Audio default output executions:',r['decoded_executions'])
