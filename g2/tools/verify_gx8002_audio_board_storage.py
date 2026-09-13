# SPDX-License-Identifier: MIT
"""Qualify typed audio defaults through placement, modeled load and consumers."""
import json,re,subprocess
from build_gx8002_audio_board_storage import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from analyze_gx8002_gsensor_state_references import mapped_offset,section_map,SDK_EVIDENCE
from verify_gx8002_uart_loader_setup import execute as loader
from compare_gx8002_clear_bss import execute as clear,START,END
from execute_gx8002_audio_board_control import execute as board
from verify_gx8002_memcpy_source import decode

def verify():
    candidate=build();path=ROOT/'build/gx8002-audio-board-storage/storage.elf';elf=Elf32(path.read_bytes(),'defaults');section=next(s for s in elf.sections if s['name']=='.board');data=elf.contents(section);base=section['address']
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    layout=section_map();sdk=ROOT/'build/upstream-nationalchip-lvp-kws'
    for i in range(0,240,4):assert mapped_offset(base+i,layout,sdk)==0x189b8+i
    references=[];checked=0
    for kind,artifact in re.findall(r"\('([^']+)',\s*\w+,\s*'([^']+)',\s*'gx8002-[^']+\.json'\)",(ROOT/'tools/build_gx8002_source_candidate.py').read_text()):
        if kind=='audio-board-storage':continue
        p=ROOT/'build/gx8002-source-candidate'/kind/artifact;assert p.exists(),kind;e=Elf32(p.read_bytes(),kind);checked+=1
        for s in e.sections:
            if s['flags']&2 and s['size'] and s['address']:assert not (s['address']<base+240 and base<s['address']+s['size']),(kind,s['name'])
        for symbol in e.symbols():
            if symbol['name']=='open_cfw_audio_board_state':
                assert symbol['value']==base
                references.append({'kind':kind,'artifact_sha256':sha(p.read_bytes())})
    assert references
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    p=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(p.read_bytes(),'stock');assert e.contents(next(s for s in e.sections if s['name']=='.data'))==stock
    code=decode(subprocess.check_output([pre,'-D','--start-address=0x9fd0','--stop-address=0xa04c',str(p)],text=True))
    p=ROOT/'build/gx8002-clear-bss/clear.elf';e=Elf32(p.read_bytes(),'clear');r=json.loads((ROOT/'docs/research/gx8002-clear-bss-verification.json').read_text())['functions'][0];s=next(s for s in e.sections if s['name']==r['section_name']);assert sha(e.contents(s))==r['compiled_sha256']
    writes=clear(decode(subprocess.check_output([pre,'-d',str(p)],text=True)),s['address'],91);assert writes==[[a,0] for a in range(START,END,4)]
    clear_sha=sha(p.read_bytes())
    p=ROOT/'build/gx8002-source-candidate/audio-board-control/audio-board-control.elf';e=Elf32(p.read_bytes(),'board');report=json.loads((ROOT/'docs/research/gx8002-audio-board-control-source-verification.json').read_text())
    for row in report['functions']:
        s=next(s for s in e.sections if s['name']==row['section_name']);assert sha(e.contents(s))==row['compiled_sha256']
    consumer=decode(subprocess.check_output([pre,'-d',str(p)],text=True));consumer_sha=sha(p.read_bytes());cases=0
    for mode in (0,1,0xffffffff,0xaabbccdc):
        for seed in (0,91,0xffffffff):
            result,calls,memory=loader(code,stock,mode,seed)
            assert result==0 and calls==[('read',0x3000,0x2000ffec,4),('read',0xbe88,0x10023400,0x397c),('entry',0x10023500)]
            # Model the SDK-authenticated IRAM/DRAM alias for this initialized span.
            words={base+i:memory[base-0x10000000+i] for i in range(0,240,4)}
            assert b''.join(words[base+i].to_bytes(4,'little') for i in range(0,240,4))==data
            for a,v in writes:words[a]=v
            assert all(words[base+i]==int.from_bytes(data[i:i+4],'little') for i in range(0,240,4))
            ram={base+i:v for i,v in enumerate(data)}
            def reject(*args):raise AssertionError('Unexpected accessor helper')
            ret,after,events=board(consumer,0x10203004,[],ram,reject)
            assert ret[1]==base and after==ram and not events
            seen=[]
            def helper(target,args,state,events):
                if target==0x1020300c:
                    ret,after,ev=board(consumer,target,args,state,reject);assert after==state and not ev;return ret[1]
                assert target==0x10206c24;seen.append(tuple(args[:2]));return 0
            ret,after,events=board(consumer,0x10203024,[],ram,helper)
            assert after==ram and seen==[(0x1020a8b3,2),(0x1020a8d3,12)]
            cases+=1
    return {'candidate':candidate,'checked_artifacts':checked,'references':references,'sdk_mapping_sha256':SDK_EVIDENCE,'clear_elf_sha256':clear_sha,'consumer_elf_sha256':consumer_sha,'startup_cases':cases,'clear_writes':len(writes),'preserved_words':60,'source_admitted':False,'hardware_qualified':False,'limits':['Primary loader instructions use modeled flash reads; alias uses authenticated SDK mapping, not physical measurement.','Registered board accessor and diagnostic initialization execute on typed defaults; remaining audio configuration/buffer consumers and registry admission still pending.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-board-storage-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Audio defaults startup/consumer cases:',r['startup_cases'])
