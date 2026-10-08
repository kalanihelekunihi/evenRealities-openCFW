#!/usr/bin/env python3
"""Locked CMDQ reservation/post/cancel/term comparisons; RAM MMIO, no IRQ timing."""
import argparse,hashlib,importlib.util,itertools,json
from pathlib import Path
spec=importlib.util.spec_from_file_location('events',Path(__file__).with_name('verify_context_events.py'));v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
v.v.v.ENTRIES.update({'reserve':('opencfw_provider_42790a',0x42790a),'post':('opencfw_provider_4279f0',0x4279f0),'cancel':('opencfw_provider_4279be',0x4279be),'term':('opencfw_provider_427ad6',0x427ad6)})
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--term-elf',type=Path);args=ap.parse_args();_,segs,syms=v.v.v.v.elf.elf_info(args.elf);cases=[];trace={};Q=v.Q;B=v.v.BUFFER;OUT=v.v.CFG
 def compare(label,prepare,sequence):
  obs=[]
  term_case=any(e=='term' for e,a in sequence);original_only=term_case and not args.term_elf
  for source in ((False,) if original_only else (False,True)):
   active_segs,active_syms=segs,syms
   if source and term_case and args.term_elf:
    _,extra,extra_syms=v.v.v.v.elf.elf_info(args.term_elf);active_segs=segs+extra;active_syms=dict(syms);active_syms.update(extra_syms)
   m=v.Machine(source,active_segs,active_syms);m.setup();m.call('cqinit',[v.H,32,B]);ops=m.r(Q+36);m.w(m.r(ops+4),B);m.w(m.r(ops+8),0);prepare(m,ops);m.events.clear();m.state_writes.clear();m.writes.clear();m.trace.clear();status=[m.call(e,a) for e,a in sequence];o=m.observation(status);o['outputs']=bytes(m.cpu.mem_read(OUT,16)).hex();obs.append(o)
   if not source:trace.update({hex(pc):raw for pc,raw in m.trace.items()})
  if not original_only:assert obs[0]==obs[1],(label,obs)
  cases.append(dict(label=label,validation='original-only: term GC discarded from source image' if original_only else 'stock/source isolated-term supplement' if term_case else 'stock/source comparison',observation=obs[0]));return obs[0]
 for count in (0,1,2,8,29,30,31,32):
  compare('reserve-cancel-'+str(count),lambda m,o:None,[('reserve',[Q,count,OUT,OUT+4]),('cancel',[Q])])
 for count,kind in itertools.product((1,2,8,29),(0,1,256,257)):
  compare('reserve-post-'+str((count,kind)),lambda m,o:None,[('reserve',[Q,count,OUT,OUT+4]),('post',[Q,kind]),('cancel',[Q])])
 for force,pending in itertools.product((0,1,256,257),(0,1,255)):
  def prepare(m,o):m.w(Q+32,pending);m.call('cqon',[v.H])
  result=compare('term-'+str((force,pending)),prepare,[('term',[Q,force])]);assert result['status']==[3 if (force&255)==0 and pending!=0 else 0]
 for entry,vals in [('reserve',[Q,1,0,OUT]),('reserve',[Q,1,OUT,0]),('reserve',[0,1,OUT,OUT+4]),('post',[0,1]),('cancel',[0]),('term',[0,1]),('post',[Q,1]),('cancel',[Q])]:compare('guard-'+entry+str(vals),lambda m,o:None,[(entry,vals)])
 for delta in (254,255,256,257):compare('sequence-full-'+str(delta),lambda m,o:m.w(Q+32,delta),[('reserve',[Q,1,OUT,OUT+4])])
 for producer,consumer,count in [(B+240,B+128,1),(B+240,B+8,1),(B+64,B+80,1),(B+64,B+88,1),(B+64,B+96,1)]:
  def prepare(m,o):m.w(Q+16,producer);m.w(Q+20,producer);m.w(m.r(o+4),consumer)
  compare('space-'+str((producer,consumer,count)),prepare,[('reserve',[Q,count,OUT,OUT+4])])
 result=dict(status='PASS',cases=len(cases),elf_sha256=hashlib.sha256(args.elf.read_bytes()).hexdigest(),original_sha256=v.v.v.v.LOCKED_SHA,original_trace=trace,comparisons=cases,limits=['Fresh CPU per fixture; MMIO is mapped RAM, peripheral consumer/index values supplied by fixture.','Reserve/post/cancel execute shared-image stock/source. With --term-elf, termination executes a separate retained source module from the frozen object against stock; it is not claimed linked into the shared image.','Reservation cancellation rewinds queue pointers/sequence, not heap free. No IOM uninitialize is invented.'],term_module_sha256=hashlib.sha256(args.term_elf.read_bytes()).hexdigest() if args.term_elf else None,runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest());args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['status','cases','elf_sha256']}))
if __name__=='__main__':main()
