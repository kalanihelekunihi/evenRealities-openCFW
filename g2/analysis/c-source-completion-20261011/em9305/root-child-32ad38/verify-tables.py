from pathlib import Path
import subprocess,struct,re,json,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parents[4];T=ROOT/'g2/build/pseudocode-first/20260930T190500Z/tools/arc-binutils-001/prefix/bin'
b=(ROOT/'g2/build/c-firmware/20261011/em-activation-round/em-inspection.bin').read_bytes();assert hashlib.sha256(b).hexdigest()=='0de6e945a56ec886a92e44d4eaefe02fbca6db11f8747876e30bffb45cffce03'
o=0x334db8-0x302400;native=struct.unpack('<24I',b[o:o+96]);obj=P/'tables.o';section='.rodata.opencfw_ext_adv_actions'
txt=subprocess.check_output([str(T/'arc-elf32-objdump'),'-r','-j',section,str(obj)],text=True);rel={int(a,16)//4:s for a,s in re.findall(r'^([0-9a-f]{8})\s+R_ARC_32\s+(\S+)',txt,re.M)}
assert rel=={i:f'opencfw_em9305_child_{a:x}' for i,a in enumerate(native) if a}
for sec,suffix,size in [(section,'actions',96),('.rodata.opencfw_ext_adv_transitions','transitions',24)]:
 dst=P/('compiled-'+suffix+'.bin');subprocess.run([str(T/'arc-elf32-objcopy'),'-O','binary','-j',sec,str(obj),str(dst)],check=True);raw=dst.read_bytes();assert len(raw)==size
 if suffix=='actions':assert raw==bytes(96)
 else:assert raw==b[o+96:o+120]
r={'status':'PASS_SOURCE_TABLE_EXTENT_TRANSITIONS_AND_RELOCATIONS','slots':24,'action_relocations':len(rel),'unique_targets':len(set(rel.values())),'source_sha256':hashlib.sha256((P/'tables.c').read_bytes()).hexdigest(),'object_sha256':hashlib.sha256(obj.read_bytes()).hexdigest()};(P/'tables-compile-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
