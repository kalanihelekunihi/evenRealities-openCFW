#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Original dispatcher + actual GPIO/PRIMASK vs C + independent ordered model."""
import argparse,importlib.util,json,hashlib,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
spec=importlib.util.spec_from_file_location('gpio',ROOT/'g2/components/foundation/ambiq_gpio_config/simulator/verify.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
GROUPS=[[5,7,6,50],[8,10,9,51],[25,27,26,11],[31,33,32,13],[34,36,35,16],[47,49,48,17],[61,63,62,117],[22,24,23,19]]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 blob=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';raw=blob.read_bytes()[32:];stock=[dict(address=g.BASE,memory_size=len(raw),data=raw,flags=5)]
 _,segments,symbols=g.parser.elf_info(a.elf)
 # Only a read-only configuration word is supplied outside source ELF; no code stub.
 observed={};results=[]
 config_word=struct.unpack_from('<I',raw,0x78ee48-g.BASE)[0];assert config_word==3
 def case(instance,operation,prior,cfg):
  c=dict(op='state',pin=instance,operation=operation,null=False,prior=prior,model='raw')
  original=[dict(x) for x in stock];data=bytearray(raw);struct.pack_into('<I',data,0x78ee48-g.BASE,cfg);original[0]['data']=bytes(data)
  source=segments+[dict(address=0x78e000,memory_size=4096,data=b'\x00'*0xe48+g.w(cfg),flags=4)]
  left=g.run(original,0x4c2e30,c,entries={'set':0x480f0c});right=g.run(source,symbols['opencfw_transport_pads_raw']&~1,c,entries={'set':symbols['am_hal_gpio_pinconfig']&~1})
  fresh=left['trace'].copy()
  for r in [left,right]:r.pop('status');r.pop('trace')
  assert left==right,(c,cfg,left,right)
  key=(operation&255)|(instance<<2);pins=[]
  if instance<8 and key in [4*i+j for i in range(8) for j in [0,1]]:
   group=GROUPS[key//4];pins=group if key%4==0 else [group[0],group[2]]
  regs=bytearray(g.initial_registers(c));mmio=[];calls=[]
  for pin in pins:
   calls.append(['config',pin,cfg,prior]);bank=pin//32;bit=1<<(pin%32);pull=cfg>>13&7;drive=cfg>>10&3
   valid=not ((g.EXT[bank]&bit and pull not in [0,1,6]) or (not g.EXT[bank]&bit and drive>=2 and not g.DRIVE[bank]&bit))
   if valid:
    for addr,val in [(g.GPIO+0x400,0x73),(g.GPIO+pin*4,cfg),(g.GPIO+0x400,0)]:mmio.append(['write',addr,val,1]);struct.pack_into('<I',regs,addr-g.GPIO,val)
  expected=dict(output=0xabadcafe,output_writes=[],mmio=mmio,registers=regs.hex(),primask=prior,calls=calls)
  assert left==expected,(c,cfg,left,expected)
  # Capture original only, avoiding compiled-source address credit.
  for address,word in fresh.items():assert address not in observed or observed[address]==word;observed[address]=word
  results.append(dict(instance=instance,operation=operation,prior=prior,config=cfg,pins=pins))
 for instance in list(range(9))+[255,0xffffffff]:
  for op in range(256):
   for prior in [0,1]:case(instance,op,prior,3)
 for instance in range(8):
  for cfg in [0,0xffffffff,0x1c00,0xe000,0x400,0xc001002]:
   for prior in [0,1]:case(instance,0,prior,cfg)
 for instance in range(8):
  for op in [256,257,260,0xffffffff]:case(instance,op,0,3)
 tracebytes=set()
 for address,word in observed.items():tracebytes.update(range(address,address+len(bytes.fromhex(word))))
 manifest={str(p.relative_to(ROOT)):sha(p) for root in [ROOT/'g2/components/foundation/radio_transport_pads',ROOT/'g2/components/foundation/ambiq_gpio_config'] for p in root.rglob('*') if p.suffix in ['.c','.h','.py','.ld']}
 manifest['g2/components/foundation/ambiq_mspi/ambiq_interrupt_mask.c']=sha(ROOT/'g2/components/foundation/ambiq_mspi/ambiq_interrupt_mask.c')
 report=dict(status='PASS',cases=len(results),results=results,original_trace={hex(a):b for a,b in sorted(observed.items())},unique_original_trace_bytes=len(tracebytes),source_manifest=manifest,firmware_sha256=sha(blob),elf_sha256=sha(a.elf),limits='Full dispatcher with real GPIO and PRIMASK instructions, no executable stubs. Config failure perturbations synthetic. No transport HAL release, command-queue/free, pending IRQ/NVIC, scheduling or hardware proof. Void R0 result excluded.')
 with a.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
 print('PASS',len(results),len(tracebytes))
if __name__=='__main__':main()
