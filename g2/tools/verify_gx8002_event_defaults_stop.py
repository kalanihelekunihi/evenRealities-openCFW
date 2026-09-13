# SPDX-License-Identifier: MIT
"""Execute I2S stop with compiled shared event-state initialization."""
import json,re,subprocess
from build_gx8002_event_defaults import build,ROOT,sha,Elf32
from execute_gx8002_stop_i2s import execute
from verify_gx8002_stop_i2s import APP,PENDING
from verify_gx8002_power_initialize import word
from verify_gx8002_memcpy_source import decode


def verify():
    candidate=build();path=ROOT/'build/gx8002-event-defaults/defaults.elf';elf=Elf32(path.read_bytes(),'defaults');section=next(s for s in elf.sections if s['name']=='.event_state');data=elf.contents(section);base=section['address']
    registry=(ROOT/'tools/build_gx8002_source_candidate.py').read_text()
    artifact,report_name=re.search(r"\('stop-i2s',\s*\w+,\s*'([^']+)',\s*'([^']+)'\)",registry).groups()
    path=ROOT/'build/gx8002-source-candidate/stop-i2s'/artifact;elf=Elf32(path.read_bytes(),'stop');report=json.loads((ROOT/'docs/research'/report_name).read_text())
    for section in elf.sections:
        if section['flags']&2 and section['size']:assert any(row.get('compiled_sha256')==sha(elf.contents(section)) for row in report['functions'])
    code=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-d',str(path)],text=True));cases=0
    for enabled in (0,1):
        for handle in (7,0xffffffff):
            memory={APP+i:0xa5 for i in range(32)};memory.update({base+i:v for i,v in enumerate(data)})
            word(memory,APP+20,enabled);word(memory,APP+4,handle)
            for repeat in (False,True):
                expected=dict(memory);wanted=[('log',0x1020b431,307)]
                if enabled and not repeat:
                    word(expected,APP+20,0);expected[PENDING]=0
                    wanted.extend(('pad',pin,1) for pin in range(7,11))
                    if handle!=0xffffffff:
                        wanted.extend([('close_log',0x1020b431,329,handle),('close',handle),('shutdown',)])
                        word(expected,APP+4,0xffffffff)
                    for offset in (0,24,28):word(expected,APP+offset,0)
                def helper(target,args,mem,events,sp):
                    if target==0x10206c24:
                        name='log' if args[0]==0x1020b536 else 'close_log';events.append((name,*args[1:3 if name=='log' else 4]))
                    elif target==0x102065dc:events.append(('pad',*args[:2]))
                    elif target==0x102053b0:events.append(('close',args[0]))
                    elif target==0x10205574:events.append(('shutdown',))
                    else:raise AssertionError(hex(target))
                    return 0xffffffff
                ret,after,events=execute(code,0x1020913c,[],memory,helper)
                assert ret[0]=='return' and after==expected and [e for e in events if e[0]!='write_byte']==wanted
                assert bytes(after[base+i] for i in (0,1,2,3,5,6,7))==bytes(data[i] for i in (0,1,2,3,5,6,7))
                memory=after;cases+=1
    return {'candidate':candidate,'consumer_elf_sha256':sha(path.read_bytes()),'cases':cases,'source_admitted':False,
            'limits':['Compiled pending byte is cleared by active stop and preserved by inactive/repeated stop; full shared state, VAD sentinel and padding checked. Handles open/invalid covered.',
                      'GPIO, logging and hardware shutdown are modeled helpers; I2S start composition and physical transitions remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-event-defaults-stop.json').write_text(json.dumps(r,indent=2)+'\n');print('Event defaults I2S stop:',r['cases'],'cases')
