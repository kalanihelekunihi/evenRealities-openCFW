# SPDX-License-Identifier: MIT
"""Nested decoded source record callback on live IRQ word-backed byte RAM."""
import itertools,json,subprocess
from verify_gx8002_audio_irq import build,ROOT,IMAGE_SHA,sha,Elf32,decode,execute,BASE
from execute_gx8002_audio_irq_record import execute as record_execute
from verify_gx8002_audio_record import expected_state,CTRL,HEADER
class Bytes:
    def __init__(self,words):self.words=words
    def __getitem__(self,a):return (self.words[a&~3]>>(8*(a&3)))&255
    def __setitem__(self,a,v):
        base=a&~3;assert base in self.words or 0x2006fe00<=base<0x20070000,hex(a);shift=8*(a&3);self.words[base]=(self.words.get(base,0)&~(255<<shift))|((v&255)<<shift)

def verify():
    evidence=build();out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');path=ROOT/'build/gx8002-source-candidate/audio-record/audio-record.elf';elf=Elf32(path.read_bytes(),'record');report=json.loads((ROOT/'docs/research/gx8002-audio-record-source-verification.json').read_text());row=report['functions'][0];section=next(s for s in elf.sections if s['name']==row['section_name']);assert sha(elf.contents(section))==row['compiled_sha256']
    bindings=json.loads((ROOT/'docs/research/gx8002-audio-record-candidate.json').read_text())['bindings']
    record=decode(subprocess.check_output([pre,'-d',str(path)],text=True));wrapper=out/'padmux-get-stock.elf';stock=Elf32(wrapper.read_bytes(),'stock');assert sha(stock.contents(next(s for s in stock.sections if s['name']=='.data')))==IMAGE_SHA
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x17e5c','--stop-address=0x180e4',str(wrapper)],text=True));new=decode((out/'audio-irq.disassembly.txt').read_text());cases=0
    for channel,index,flags,vad,read,write,invalid in itertools.product(range(1,8),(0,3,12),(0,0x10),(0,1),(0,14),(0,14),(0,23,24,25)):
        def setup(memory):
            for base,length in ((CTRL,20),(HEADER,112),(0x2002dfa0,12)):
                for a in range(base,base+length,4):memory[a]=0
            memory.update({CTRL:read,CTRL+4:write,0x2002dfa8:invalid,CTRL+16:flags,HEADER+36:1,HEADER+108:40,0x2002dfa0:0x10210000,BASE+0x168:index*80})
        def nested(memory,kind,mask,address,sp):
            assert kind==0 and address==sp
            result,events=record_execute(record,section['address'],bindings,mask,Bytes(memory),address,sp,vad,91)
            state,records=expected_state(mask,read,write,flags,vad,invalid,index)
            assert tuple(memory[a] for a in (CTRL,CTRL+4,CTRL+8,CTRL+12,CTRL+16,0x2002dfa8))==state
            assert [e for e in events if e[0]=='record']==[('record',r[1],address+8) for r in records]
            # Every nested write went directly to the IRQ's backing memory.
        args=(channel,channel,1,91)
        a=execute(new,0x10025e48,*args,setup_hook=setup,raw_callback_hook=nested,callback_targets=(section['address'],0x10220004,0x10220008,0x1022000c))
        b=execute(old,0x17e5c,*args,setup_hook=setup,raw_callback_hook=nested,callback_targets=(section['address'],0x10220004,0x10220008,0x1022000c))
        assert a==b
        cases+=1
    return {'candidate':evidence,'record_elf_sha256':sha(path.read_bytes()),'cases':cases,'source_admitted':False,'limits':['Decoded source record callback executes on IRQ word-backed byte RAM with actual SDC stack pointer, nested SP and real linked record entry dispatch. Byte writes restricted to mapped memory or nested stack. Independent control/emitted-frame oracle. Record helpers modeled; physical execution and other callback bodies pending.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-irq-record.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
