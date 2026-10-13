#!/usr/bin/env python3
"""Qualify recovered LP common configuration with genuine source providers."""
from pathlib import Path
import hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
D=ROOT/'g2/components/touch/reset_layout_candidate_20261010'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
fw=ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin'
assert sha(fw)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d'
blob=fw.read_bytes();records=[];objects=[]
for name in ['reset_generated_common_config','reset_channel_pending','reset_pin_config']:
 src=D/(name+'.c');obj=HERE/(name+'.o');dep=HERE/(name+'.d');before=sha(src)
 argv=['/usr/bin/clang','-target','armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-Wall','-Wextra','-Werror','-MD','-MF',str(dep),'-c',str(src),'-o',str(obj)]
 subprocess.run(argv,check=True);assert sha(src)==before
 paths=dep.read_text().replace('\\\n',' ').split(': ',1)[1].split()
 deps={str(Path(p).relative_to(ROOT)):sha(Path(p)) for p in paths if Path(p).is_relative_to(ROOT)}
 records.append({'source':str(src.relative_to(ROOT)),'source_sha256':before,'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),'command':argv,'dependencies':deps,'source_stable':True});objects.append(obj)
elf=HERE/'fixture.elf';argv=['arm-none-eabi-ld','-T',str(HERE/'fixture.ld'),*map(str,objects),'-o',str(elf)]
subprocess.run(argv,check=True);assert not subprocess.check_output(['arm-none-eabi-nm','-u',str(elf)],text=True).strip()
rows=[]
for section,address,n in [('common',0xb2a8,60),('electrodes',0xb2e4,72),('shield_electrodes',0xb32c,16),('shield_pins',0xb33c,16),('pins',0xb34c,40),('channel',0xb8f8,28)]:
 p=HERE/(section+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section','.'+section+'='+str(p),str(elf)],check=True)
 actual=p.read_bytes();stock=blob[32+address-0x3300:32+address-0x3300+n];assert len(actual)==n and actual==stock,section
 rows.append({'section':section,'stock_rom_start':hex(address),'end_exclusive':hex(address+n),'bytes':n,'sha256':sha(p)})
# Independent primary-header field census with only the evidenced LP platform
# branch selected. Common config has no product option-dependent fields.
h=ROOT/'g2/analysis/c-source-completion-20261011/touch/capsense-v6-reference/cy_capsense_structure.h'
s=re.sub(r'/\*.*?\*/','',h.read_text(),flags=re.S);end=s.index('} cy_stc_capsense_common_config_t;');s=s[s.rfind('typedef struct',0,end):end]+'} vendor_t;\n'
p=subprocess.check_output(['clang','-E','-P','-x','c','-','-DCY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP=1'],input=s,text=True)
fields=re.findall(r'\b(?:uint32_t|uint16_t|uint8_t)\s+(\w+)\s*;',p)
our=(D/'reset_generated_common_config.h').read_text();assert fields==re.findall(r'\b(?:uint32_t|uint16_t|uint8_t)\s+(\w+)\s*;',our.split('struct touch_common_config_lp {',1)[1].split('};',1)[0])
# Consumer-level layout assertions join to existing native-derived C consumers.
consumers={}
for f,literals in [('pin_control_offline/pins.c',['common+12','common[44]','common+8']),('base_frame_offline/base.c',['common[54]','common[55]','common[56]']),('all_slot_offline/slots.c',['w+8','sensor*8','electrode[5]'])]:
 q=ROOT/'g2/components/touch'/f;t=q.read_text();assert all(x in t for x in literals);consumers[str(q.relative_to(ROOT))]=sha(q)
rec={'status':'PASS_TYPED_COMMON_CONFIG_AND_NINE_ELECTRODES','sections':rows,'new_typed_ROM_bytes':132,'existing_provider_bytes_rechecked':100,'firmware_sha256':sha(fw),'vendor_commit':'247a9a0f79eb976f144f5fbeb29488c1c2606517','vendor_header_sha256':sha(h),'vendor_license_sha256':sha(h.parent/'LICENSE'),'records':records,'consumer_inputs':consumers,'elf_sha256':sha(elf),'link_command':argv,'linker_script_sha256':sha(HERE/'fixture.ld'),'undefined_symbols':[],'limits':['Bounded data and relocation fixture only; no full firmware placement, native-body census, package equality or hardware qualification.','LP history extent, internal context and widget configuration remain separate source gates.','Vendor layout matches evidence; producing generator/SDK version not uniquely identified.']}
(HERE/'verification.json').write_text(json.dumps(rec,indent=2)+'\n');print(rec['status'],sum(x['bytes'] for x in rows))
