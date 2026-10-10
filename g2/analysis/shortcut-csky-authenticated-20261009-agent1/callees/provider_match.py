from pathlib import Path
import subprocess,json,re,hashlib
root=Path(__file__).resolve().parent;repo=root.parents[3];tools=repo/'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin';archive=repo/'third-party/upstream/nationalchip-lvp-kws/lib/libdriver_release_v1.0.6.a'
def cmd(argv):
 r=subprocess.run([str(x) for x in argv],cwd=root,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);assert r.returncode==0,r.stdout;return r.stdout
cmd([tools/'csky-elfabiv2-ar','x',archive,'clock.o','ldo.o'])
stock=(repo/'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_a_stage2_sram.bin').read_bytes();rows=[]
for name,addr,obj in [('gx_clock_set_source',0x10024bcc,'clock.o'),('gx_clock_set_module_source',0x10024be0,'clock.o'),('gx_clock_set_div',0x10024df8,'clock.o'),('gx_clock_set_dto',0x10024f44,'clock.o'),('gx_clock_set_pll',0x10025060,'clock.o'),('gx_clock_set_module_enable',0x10025080,'clock.o'),('gx_analog_set_ldo_ana_voltage',0x100246f0,'ldo.o'),('gx_analog_set_ldo_dig_voltage',0x10024730,'ldo.o')]:
 section='.text.'+name;data=root/(name+'.bin');objpath=root/obj
 out=cmd([tools/'csky-elfabiv2-objdump','-dr','-j',section,objpath]);(root/(name+'-provider-disassembly.txt')).write_text(out)
 cmd([tools/'csky-elfabiv2-objcopy','-O','binary','-j',section,objpath,data]);candidate=data.read_bytes();actual=stock[addr-0x10023400:addr-0x10023400+len(candidate)]
 reloc=[(int(a,16),r,s) for a,r,s in re.findall(r'^\s*([0-9a-f]+):\s+(R_CKCORE_\S+)\s+(\S+)',out,re.M)];excluded=set()
 for a,r,s in reloc:
  assert r in ['R_CKCORE_PCREL_IMM26BY2','R_CKCORE_ADDR32'],r
  excluded.update(range(a,a+4))
 matches=len(candidate)==len(actual) and all(x==y for i,(x,y) in enumerate(zip(candidate,actual)) if i not in excluded)
 rows.append({'name':name,'target_runtime':addr,'object':obj,'section':section,'length':len(candidate),'relocations':reloc,'equal_outside_named_relocations':matches,'candidate_sha256':hashlib.sha256(candidate).hexdigest(),'stock_sha256':hashlib.sha256(actual).hexdigest()})
 print(name,matches,len(candidate))
(root/'provider-matches.json').write_text(json.dumps(rows,indent=2)+'\n')
