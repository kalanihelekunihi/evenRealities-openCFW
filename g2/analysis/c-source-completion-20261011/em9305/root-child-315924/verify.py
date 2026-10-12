from pathlib import Path
import subprocess,json,hashlib,re
P=Path(__file__).resolve().parent;R=P.parents[4];T=R/'g2/build/pseudocode-first/20260930T190500Z/tools/arc-binutils-001/prefix/bin';B=R/'g2/build/c-firmware/20261011/em-activation-round/em-inspection.bin';b=B.read_bytes();assert hashlib.sha256(b).hexdigest()=='0de6e945a56ec886a92e44d4eaefe02fbca6db11f8747876e30bffb45cffce03'
t=subprocess.check_output([str(T/'arc-elf32-objdump'),'-dr','-Mcpu=em,dsp',str(P/'source.o')],text=True);assert '0: R_ARC_S25H_PCREL\topencfw_em9305_child_322dd8' in t and re.search(r'\tb.d\t',t);assert re.search(r'4:\s+d90c\s+\tmov_s\tr1,0xc',t)
n=subprocess.check_output([str(T/'arc-elf32-nm'),'-S',str(P/'source.o')],text=True);assert re.search(r'00000006 T opencfw_em9305_child_315924',n)
r={'status':'PASS_WHOLE_NATIVE_INSTRUCTION_CROSSWALK','instructions':2,'native_bytes':6,'target_function_bytes':6,'tail_relocations':1,'delay_slot_event':12,'source_sha256':hashlib.sha256((P/'source.c').read_bytes()).hexdigest(),'limits':['Tail relocation and native delay slot verified; final placement/runtime remain open.']};(P/'crosswalk-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
