#!/usr/bin/env python3
# Bounded state trace model transcribed from pinned instructions; external reads are controlled.
def poll_bit0(words,events,label):
 for x in words:
  events.append(f'{label} u32[0xA2000028]={x&0xffffffff:#010x}; bit0={x&1}')
  if not x&1:return True
 return False
def run(mode,ptr,count,data,pre,ready,completion,post):
 ctrl=0xa2000000; ev=[]; stored=[]; ptr&=0xffffffff; count&=0xffffffff
 ev.append('call B4C before setup')
 if not poll_bit0(pre,ev,'B4C read'): return {'events':ev,'bytes_loaded':stored,'result':'still waiting in pre-setup B4C','writes':[]}
 writes=[(ctrl+8,0),(ctrl+0x4c,0),(ctrl,0x407),(ctrl+4,count),(ctrl+0x10,1),(ctrl+0x18,(count<<16)&0xffffffff),(0xa20000f4,0),(ctrl+8,1),(ctrl+0x60,mode&0xffffffff)]
 for a,v in writes: ev.append(f'u32[{a:#010x}]={v:#010x}')
 writes=[[a,v] for a,v in writes]
 end=(ptr+count)&0xffffffff; cur=ptr; idx=0
 while cur!=end:
  ready_ok=False
  for x in ready:
   ev.append(f'ready read u32[0xA2000028]={x&0xffffffff:#010x}; bit1={bool(x&2)}')
   if x&2: ready_ok=True; break
  if not ready_ok:return {'events':ev,'bytes_loaded':stored,'writes':writes,'result':'still waiting for byte-ready bit1'}
  if idx>=len(data): return {'events':ev,'bytes_loaded':stored,'writes':writes,'result':'fixture input bytes exhausted'}
  b=data[idx]&0xff; idx+=1; ev.append(f'u8[{cur:#010x}] -> {b:#04x}; R1 becomes {(cur+1)&0xffffffff:#010x}')
  ev.append(f'u32[0xA2000060]={b:#010x}'); writes.append([0xa2000060,b]); stored.append({'address':f'{cur:#010x}','byte':b,'register_word':f'0x{b:08X}'})
  cur=(cur+1)&0xffffffff
 done=False
 for x in completion:
  ev.append(f'completion read u32[0xA2000020]={x&0xffffffff:#010x}')
  if (x&0xffffffff)==0: done=True; break
 if not done:return {'events':ev,'bytes_loaded':stored,'writes':writes,'result':'still waiting for full completion word zero'}
 ev.append('call B4C after completion')
 if not poll_bit0(post,ev,'B4C read'): return {'events':ev,'bytes_loaded':stored,'writes':writes,'result':'still waiting in post-completion B4C'}
 ev.append('return R0=0; restore R4-R6,LR')
 return {'events':ev,'bytes_loaded':stored,'writes':writes,'final_R1':f'{cur:#010x}','result':'returns R0=0'}
