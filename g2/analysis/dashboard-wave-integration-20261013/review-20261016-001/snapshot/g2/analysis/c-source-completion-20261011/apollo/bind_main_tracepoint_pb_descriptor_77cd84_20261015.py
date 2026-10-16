#!/usr/bin/env python3
"""Authenticate and bind the four-node stock tracepoint nanopb descriptor."""
import hashlib,json,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_pb_descriptor_77cd84.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
BASE=G2/'build/c-firmware/20261015/main-tracepoint-encode-response-5eded0/apollo-main-tracepoint-encode-response-5eded0.o'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-pb-descriptor-77cd84'
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
FIELDS={'fields_7457d0':(0x7457d0,44),'fields_78c74c':(0x78c74c,12),'fields_78c758':(0x78c758,12),'fields_78ec04':(0x78ec04,8)}
DESCS={'audio_tracepoint_message_descriptor':0x77cd84,'desc_77cd3c':0x77cd3c,'desc_77cd54':0x77cd54,'desc_77cd6c':0x77cd6c}
SUBS={'sub_789c20':(0x789c20,16),'empty_78f4cc':(0x78f4cc,4),'empty_78f4d0':(0x78f4d0,4),'empty_78f4d4':(0x78f4d4,4)}
EDGES={'audio_tracepoint_message_descriptor':[(0,'fields_7457d0'),(4,'sub_789c20')],
'desc_77cd3c':[(0,'fields_78c74c'),(4,'empty_78f4cc')],
'desc_77cd54':[(0,'fields_78c758'),(4,'empty_78f4d0')],
'desc_77cd6c':[(0,'fields_78ec04'),(4,'empty_78f4d4')],
'sub_789c20':[(0,'desc_77cd3c'),(4,'desc_77cd54'),(8,'desc_77cd6c')]}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def names(p,flag):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-g',flag,str(p)],text=True).splitlines()}
def main():
 blob=PAYLOAD.read_bytes()[32:]
 if hashlib.sha256(blob).hexdigest()!=PINNED:raise RuntimeError('stock Apollo payload changed')
 def stock(a,n):return blob[a-0x438000:a-0x438000+n]
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'tracepoint_pb_descriptor_77cd84.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 with obj.open('rb') as f:
  elf=ELFFile(f);syms={s.name:s for s in elf.get_section_by_name('.symtab').iter_symbols()};ro=elf.get_section_by_name('.rodata').data()
  for name,(address,length) in FIELDS.items():
   s=syms[name];v=s['st_value']
   if s['st_size']!=length or ro[v:v+length]!=stock(address,length):raise RuntimeError(('field mismatch',name))
  for name,(address,length) in SUBS.items():
   s=syms[name];v=s['st_value']
   if s['st_size']!=length or ro[v+length-4:v+length]!=bytes(4) or stock(address+length-4,4)!=bytes(4):raise RuntimeError(('sublist mismatch',name))
  for name,address in DESCS.items():
   s=syms[name];v=s['st_value']
   if s['st_size']!=24 or ro[v+8:v+24]!=stock(address+8,16):raise RuntimeError(('descriptor metadata mismatch',name))
  rel=elf.get_section_by_name('.rel.rodata')
  actual={r['r_offset']:int.from_bytes(ro[r['r_offset']:r['r_offset']+4],'little') for r in rel.iter_relocations()}
  expected={syms[owner]['st_value']+offset:syms[target]['st_value'] for owner,edges in EDGES.items() for offset,target in edges}
  if actual!=expected:raise RuntimeError(('descriptor relocation graph changed',actual,expected))
 for owner,edges in EDGES.items():
  address=DESCS.get(owner,SUBS.get(owner,(None,))[0])
  for offset,target in edges:
   taddr=DESCS.get(target,FIELDS.get(target,SUBS.get(target,(None,)))[0])
   if int.from_bytes(stock(address+offset,4),'little')!=taddr:raise RuntimeError(('native graph edge changed',owner,offset,target))
 if names(obj,'--defined-only')!={'audio_tracepoint_message_descriptor'} or names(obj,'-u'):raise RuntimeError('descriptor object contract changed')
 before=names(BASE,'-u');linked=OUT/'apollo-main-tracepoint-pb-descriptor-77cd84.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=names(linked,'-u')
 if len(before)!=192 or len(after)!=191 or before-after!={'audio_tracepoint_message_descriptor'} or after-before:raise RuntimeError((len(before),len(after),before-after,after-before))
 receipt={'status':'PASS_AUTHENTICATED_MAIN_TRACEPOINT_PB_DESCRIPTOR_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PINNED,'field_tables':{n:{'native_address':hex(a),'bytes':sz} for n,(a,sz) in FIELDS.items()},'descriptors':{n:hex(a) for n,a in DESCS.items()},'submessage_tables':{n:hex(a) for n,(a,_) in SUBS.items()},'authenticated_relocations':len(EDGES['sub_789c20'])+2*len(DESCS),'object_sha256':sha(obj),'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'source_owned_symbols':['audio_tracepoint_message_descriptor'],'unresolved_before':192,'unresolved_after':191,'imports_resolved':['audio_tracepoint_message_descriptor'],'imports_added':[],'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Static nanopb graph matches authenticated stock ROM; final whole-image placement and live encoding behavior remain open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],len(before),len(after),sha(path))
if __name__=='__main__':main()
