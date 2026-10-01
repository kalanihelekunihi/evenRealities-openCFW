#!/usr/bin/env python3
# Instruction-derived finite trace model; device values are controlled, not emulated hardware.
def wait(words, mask, want_set, events, label):
    for word in words:
        word &= 0xffffffff
        events.append({'kind':label,'address':'0xA2000028' if label.startswith('bit') else ('0xA2000020' if label=='completion' else '0xA2000028'),'word':f'0x{word:08X}','mask':mask,'predicate':bool(word & mask) if mask else (word==0)})
        if (bool(word & mask) == want_set) if mask else (word==0): return True
    return False

def run(mode, ptr, count, data_words, pre_words, ready_per_byte, completion_words, post_words):
    ev=[]; writes=[]; bytes_stored=[]; ptr &= 0xffffffff; count &= 0xffffffff; end=(ptr+count)&0xffffffff
    ev.append({'kind':'call','target':'0x10000B4C','phase':'before setup'})
    if not wait(pre_words,1,False,ev,'bit0-pre'):
        return {'events':ev,'writes':writes,'bytes_stored':bytes_stored,'result':'still polling in initial B4C'}
    ctrl=0xa2000000
    setup=[(ctrl+8,0),(ctrl+0x4c,0),(ctrl,3079), (ctrl+4,(count-1)&0xffffffff),(ctrl+0x10,1),(ctrl+0x18,0),(0xa20000f4,0),(ctrl+8,1),(ctrl+0x60,mode&0xffffffff)]
    for a,v in setup: writes.append([a,v]); ev.append({'kind':'write32','address':f'0x{a:08X}','value':f'0x{v:08X}'})
    if len(data_words)<count:
        # Missing test data is recorded, not fabricated.
        return {'events':ev,'writes':writes,'bytes_stored':bytes_stored,'result':'fixture data words do not cover count'}
    current=ptr
    for idx in range(count):
        ready=ready_per_byte[idx] if idx<len(ready_per_byte) else []
        before=len(ev)
        if not wait(ready,8,True,ev,'bit3-ready'):
            return {'events':ev,'writes':writes,'bytes_stored':bytes_stored,'result':f'still polling for ready before byte {idx}'}
        # The source has a 32-bit load from controller+0x60, then STBI.B to output.
        word=data_words[idx]&0xffffffff; b=word&0xff
        ev.append({'kind':'read32','address':'0xA2000060','word':f'0x{word:08X}'})
        ev.append({'kind':'store8','address':f'0x{current:08X}','value':f'0x{b:02X}'})
        bytes_stored.append({'address':f'0x{current:08X}','byte':b,'source_word':f'0x{word:08X}'})
        current=(current+1)&0xffffffff
    if not wait(completion_words,0,False,ev,'completion'):
        return {'events':ev,'writes':writes,'bytes_stored':bytes_stored,'result':'still polling for full completion word zero'}
    ev.append({'kind':'call','target':'0x10000B4C','phase':'after completion'})
    if not wait(post_words,1,False,ev,'bit0-post'):
        return {'events':ev,'writes':writes,'bytes_stored':bytes_stored,'result':'still polling in final B4C'}
    ev.append({'kind':'return','R0':'0x00000000'})
    return {'events':ev,'writes':writes,'bytes_stored':bytes_stored,'final_R1':f'0x{current:08X}','result':'returns R0=0'}
