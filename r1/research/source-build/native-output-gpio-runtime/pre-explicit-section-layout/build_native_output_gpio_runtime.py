#!/usr/bin/env python3
"""Compose five adapters with existing source providers; check local byte identity."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ADAPTERS={
 'r1_output_gpio_driver10':(0x54d8c,'r1_twi_gpio_high',0x79448),
 'r1_output_gpio_driver0c':(0x54d92,'r1_twi_gpio_low',0x79180),
 'r1_output_gpio_high':(0x54f3c,'nrfx_gpiote_out_set',0x7ab3c),
 'r1_output_gpio_low':(0x54f42,'nrfx_gpiote_out_clear',0x7aa2c),
 'r1_output_gpio_toggle':(0x54f8a,'nrfx_gpiote_out_toggle',0x7ab88)}
def main():
 out=BASE/'native-output-gpio-runtime';out.mkdir(exist_ok=True)
 reports={};inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))};objects=[]
 for directory,name,key in [('native-output-gpio-drivers','native_output_gpio_drivers.o',None),('native-user-profile-runtime','native-user-profile-runtime.o','linked_sha256')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());p=rp.parent/name
  assert sha(p)==(r[key] if key else r['units'][0]['object_sha256']);objects.append(p);reports[str(rp.relative_to(BASE))]=sha(rp)
  for q,h in r['inputs'].items():assert sha(ROOT/q)==h,q;inputs[q]=h
 linked=out/'native-output-gpio-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(linked)],check=True)
 u,d=undefined_symbols(linked);parent=json.loads((objects[1].parent/'report.json').read_text())['undefined_symbols']
 assert set(parent)-set(u)==set(ADAPTERS) and not(set(u)-set(parent)) and len(u)==48
 # This separate link checks wrapper encoding only. Absolute provider addresses
 # are verification boundaries, never a replacement for source provider bodies.
 exact=out/'adapters-native-placement.elf'
 cmd=['arm-none-eabi-ld','-Ttext=0x100000','-e','r1_output_gpio_high']
 for n,(a,p,t) in ADAPTERS.items():cmd += ['--section-start=.text.'+n+'='+hex(a),'--defsym='+p+'='+hex(t)]
 subprocess.run(cmd+[str(objects[0]),'-o',str(exact)],check=True)
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();checks=[]
 for n,(a,p,t) in ADAPTERS.items():
  data=out/(n+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.text.'+n,'-O','binary',str(exact),str(data)],check=True)
  expected=raw[a-0x27000:a-0x27000+6];assert data.read_bytes()==expected,n
  checks.append(dict(function=n,address=a,bytes=6,provider=p,native_provider=t,bytes_hex=expected.hex(),file_sha256=sha(data)))
 r=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},linked_sha256=sha(linked),undefined_symbols=u,closed_parent_imports=sorted(ADAPTERS),newly_exposed_imports=[],local_adapter_instruction_identity=True,identity_elf_sha256=sha(exact),adapter_checks=checks,application_sha256=hashlib.sha256(raw).hexdigest(),provider_behavior_reverified=False,metadata_callback_abi_migrated=False,hardware_write_executed=False,whole_image_complete=False,instruction_identity=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Five exact six-byte adapters; source-linked runtime:',len(u),'imports')
if __name__=='__main__':main()
