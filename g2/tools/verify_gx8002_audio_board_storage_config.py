# SPDX-License-Identifier: MIT
"""Run stock and source audio configuration against compiled board defaults."""
import json,subprocess
from build_gx8002_audio_board_storage import build,ROOT,IMAGE_SHA,sha,Elf32
import verify_gx8002_audio_input_config as engine
from verify_gx8002_memcpy_source import decode

def verify():
    candidate=build();path=ROOT/'build/gx8002-audio-board-storage/storage.elf';elf=Elf32(path.read_bytes(),'defaults');section=next(s for s in elf.sections if s['name']=='.board');body=elf.contents(section)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x107c0','--stop-address=0x10920',str(path)],text=True))
    path=ROOT/'build/gx8002-source-candidate/audio-input-config/config.elf';elf=Elf32(path.read_bytes(),'config');row=json.loads((ROOT/'docs/research/gx8002-audio-input-config-source-verification.json').read_text())['functions'][0];text=next(s for s in elf.sections if s['name']==row['section_name']);assert sha(elf.contents(text))==row['compiled_sha256']
    new=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    memory={section['address']+i:v for i,v in enumerate(body)}
    # Independent expected deployed settings; driver bodies are helper boundaries.
    expected=[(0xc5b0,()),(0xc590,()),(0xd8dc,(2,1)),(0xda6c,(2,0,0,0)),
              (0xd988,(2,0,0,1)),(0xd938,(2,2)),(0xd408,(0,)),(0xd4fc,(2,0,1)),
              (0x105fc,(2,2)),(0x105fc,(2,4)),(0x10500,()),(0xdafc,(1,0,13))]
    original_base=engine.BOARD;cases=0
    try:
        engine.BOARD=section['address']
        for seed in (0,1,91,0xffffffff):
            for code,entry in ((old,0x107c0),(new,text['address'])):
                assert engine.execute(code,entry,memory,13,seed)==(0,expected)
                cases+=1
    finally:engine.BOARD=original_base
    return {'candidate':candidate,'decoded_executions':cases,'config_elf_sha256':sha(path.read_bytes()),'expected_calls':[[target,list(args)] for target,args in expected],'evidence_sha256':{name:sha((ROOT/'tools'/name).read_bytes()) for name in ('verify_gx8002_audio_board_storage_config.py','build_gx8002_audio_board_storage.py','verify_gx8002_audio_input_config.py','verify_gx8002_memcpy_source.py')},'source_admitted':False,'hardware_qualified':False,'limits':['Real compiled 240-byte defaults at original address; decoded stock and registered source configuration agree with explicit driver-argument oracle.','Driver, board accessor/init and output helper bodies modeled here. Frame count supplied as13; separate startup/board qualification exists. Buffer initialization and registry admission pending.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-board-storage-config.json').write_text(json.dumps(r,indent=2)+'\n');print('Audio default configuration executions:',r['decoded_executions'])
