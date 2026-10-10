from pathlib import Path
import subprocess,re,json,hashlib
r=Path(__file__).resolve().parent;repo=r.parents[3];t=repo/'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin';a=repo/'third-party/upstream/nationalchip-lvp-kws/lib/libdriver_release_v1.0.6.a';stock=(repo/'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_a_stage2_xip.bin').read_bytes()
def cmd(args):
 p=subprocess.run(list(map(str,args)),cwd=r,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);assert p.returncode==0,p.stdout;return p.stdout
cmd([t/'csky-elfabiv2-ar','x',a,'audio_in.o','snpu.o']);rows=[]
for name,addr,obj in [('gx_audio_in_exit',0x10204984,'audio_in.o'),('gx_audio_in_set_interrupt_enable',0x102047b8,'audio_in.o')]:
 section='.text.'+name;out=cmd([t/'csky-elfabiv2-objdump','-dr','-j',section,r/obj]);(r/(name+'-archive.txt')).write_text(out);target=r/(name+'.bin');cmd([t/'csky-elfabiv2-objcopy','-O','binary','-j',section,r/obj,target]);b=target.read_bytes();actual=stock[addr-0x10203004:addr-0x10203004+len(b)];rels=[(int(x,16),y,z) for x,y,z in re.findall(r'^\s*([0-9a-f]+):\s+(R_CKCORE_\S+)\s+(\S+)',out,re.M)];exclude=set()
 for off,typ,sym in rels:
  assert typ in ['R_CKCORE_PCREL_IMM26BY2','R_CKCORE_ADDR32'];exclude.update(range(off,off+4))
 rows.append({'symbol':name,'entry':addr,'section_bytes':len(b),'relocations':rels,'equal_outside_named_relocations':all(x==y for i,(x,y) in enumerate(zip(b,actual)) if i not in exclude),'sha256':hashlib.sha256(b).hexdigest()})
out=cmd([t/'csky-elfabiv2-objdump','-dr','-j','.sram_text',r/'snpu.o']);(r/'snpu-sram-archive.txt').write_text(out);target=r/'snpu-sram.bin';cmd([t/'csky-elfabiv2-objcopy','-O','binary','-j','.sram_text',r/'snpu.o',target]);allbytes=target.read_bytes()
for name,addr,off,size in [('gx_snpu_init',0x10205cf4,0x408,0x40),('gx_snpu_exit',0x10205d40,0x448,0x20)]:
 b=allbytes[off:off+size];actual=stock[addr-0x10203004:addr-0x10203004+size];rels=[(int(x,16)-off,y,z) for x,y,z in re.findall(r'^\s*([0-9a-f]+):\s+(R_CKCORE_\S+)\s+(\S+)',out,re.M) if off<=int(x,16)<off+size];exclude=set()
 for ro,typ,sym in rels:
  assert typ in ['R_CKCORE_PCREL_IMM26BY2','R_CKCORE_ADDR32'];exclude.update(range(ro,ro+4))
 rows.append({'symbol':name,'entry':addr,'section_offset':off,'section_bytes':size,'relocations':rels,'equal_outside_named_relocations':all(x==y for i,(x,y) in enumerate(zip(b,actual)) if i not in exclude),'unexcluded_differences':[i for i,(x,y) in enumerate(zip(b,actual)) if i not in exclude and x!=y],'sha256':hashlib.sha256(b).hexdigest()})
 (r/(name+'-stock.txt')).write_text(cmd([t/'csky-elfabiv2-objdump','-D','-z','-b','binary','-m','csky','--adjust-vma=0x10203004','--start-address='+hex(addr),'--stop-address='+hex(addr+size),repo/'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_a_stage2_xip.bin']))
(r/'archive-matches.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows)
