from pathlib import Path
import subprocess,json,hashlib,re,xml.etree.ElementTree as ET
D=Path(__file__).parent;results=[]
for variant in ['plain','apollo5-aligned']:
 elf=D/f'{variant}.elf';syms={}
 for line in subprocess.check_output(['arm-none-eabi-nm','-n',str(elf)],text=True).splitlines():
  t=line.split()
  if len(t)==3:syms[t[2]]=int(t[0],16)
 assert subprocess.check_output(['arm-none-eabi-nm','-u',str(elf)],text=True).strip()==''
 assert syms['probe_itcm']==0 and 0x410000<=syms['_init_itcm_text']<0x800000
 assert syms['probe_data']==0x20000000 and syms['probe_shared']==0x20080000 and syms['probe_heap']==0x2007c000 and syms['probe_stack']==0x2007d000
 attrs=subprocess.check_output(['arm-none-eabi-readelf','-A',str(elf)],text=True);assert 'VFP registers' in attrs
 if variant=='apollo5-aligned':assert syms['g_prfbuf']%4096==0
 results.append({'variant':variant,'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'zero_undefined':True,'symbols':syms,'hard_float_attribute':True})
negative=(D/'mixed-abi-rejection.txt').read_text();assert 'uses VFP register arguments' in negative
negative=(D/'tlsf-sdk-negative.txt').read_text();assert all("undefined reference to `"+n+"'" in negative for n in ['__assert_func','printf','memcpy'])
root=ET.parse(D/'iar/hello_world.ewp').getroot();cfg=[]
for c in root.findall('configuration'):
 row={'name':c.findtext('name'),'options':{}}
 for o in c.findall('.//option'):
  name=o.findtext('name') or ''
  if name in ['RTDescription','CCOptLevel','CCPosIndRopi','CCPosIndRwpi','ILinkEntrySymbol','GRuntimeLibSelect'] or any(v in name.lower() for v in ['enum','fpu','dlib']):row['options'][name]=[v.text for v in o.findall('state')]
 cfg.append(row)
(D/'iar-option-receipt.json').write_text(json.dumps(cfg,indent=2)+'\n');(D/'verification.json').write_text(json.dumps({'positive_links':results,'mixed_abi_rejected':True,'tlsf_runtime_names_still_unresolved':['__assert_func','printf','memcpy'],'scope':'compile/link only; no startup execution or hardware I/O'},indent=2)+'\n');print('Placement, attributes, zero undefined and two negative-link boundaries verified')
