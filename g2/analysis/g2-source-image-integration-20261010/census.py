#!/usr/bin/env python3
"""Read-only selected G2 archive architecture and relocatable-link census."""
from pathlib import Path
import collections,datetime,hashlib,json,re,subprocess,tempfile
R=Path(__file__).resolve().parents[3]
D=Path(__file__).resolve().parent
archives={
 'bootloader':D/'bootloader-snapshot-build/libbootloader_source_candidate_m55.a',
 'audio_main':R/'g2/components/audio/source_candidate_20261010/build/libaudio-source-candidates.a',
 'case':R/'g2/components/case/source_candidate_20261010/build/libcase_source_candidate.a',
 'touch':R/'g2/components/touch/source_candidate_20261010/build/touch-source-candidate.a',
}
def tool(*args):return subprocess.check_output(args,text=True)
def analyze(name,path):
 members=tool('arm-none-eabi-ar','t',str(path)).splitlines()
 attrs=tool('arm-none-eabi-readelf','-A',str(path))
 cpu=collections.Counter(re.findall(r'Tag_CPU_arch: ([^\n]+)',attrs))
 cpu_name=collections.Counter(re.findall(r'Tag_CPU_name: "([^"]+)"',attrs))
 fp_abi=collections.Counter(re.findall(r'Tag_ABI_VFP_args: ([^\n]+)',attrs))
 defs=collections.defaultdict(list);undef=collections.defaultdict(list);current=None
 for line in tool('arm-none-eabi-nm','-g','-P',str(path)).splitlines():
  if line.endswith(']:'):
   current=line.split('[')[-1][:-2];continue
  parts=line.split()
  if len(parts)<2 or current is None:continue
  sym,typ=parts[0],parts[1]
  if typ.upper()=='U' or typ in ('w','v'):undef[sym].append(current)
  elif typ.isalpha() and typ.upper()==typ:defs[sym].append(dict(member=current,type=typ))
 strong={s:[x for x in xs if x['type'] not in ('W','V')] for s,xs in defs.items()}
 duplicates={s:xs for s,xs in strong.items() if len(xs)>1}
 return dict(path=str(path.relative_to(R)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),member_count=len(members),cpu_arch=dict(cpu),cpu_name=dict(cpu_name),vfp_args=dict(fp_abi),defined_symbol_count=len(defs),undefined_symbol_count=len(undef),external_unresolved=sorted(set(undef)-set(defs)),duplicate_strong_definitions=duplicates),defs,undef
report={};all_defs={};all_undef={}
for name,p in archives.items():report[name],all_defs[name],all_undef[name]=analyze(name,p)
pairs={}
for a,b in [('bootloader','audio_main'),('case','touch')]:
 da,db=all_defs[a],all_defs[b];ua,ub=all_undef[a],all_undef[b]
 cross=sorted(set(da)&set(db))
 strong=sorted(s for s in cross if any(x['type'] not in ('W','V') for x in da[s]) and any(x['type'] not in ('W','V') for x in db[s]))
 pairs[f'{a}+{b}']=dict(shared_export_count=len(cross),shared_exports=cross,strong_collision_count=len(strong),strong_collisions=strong,a_imports_satisfied_by_b=sorted((set(ua)-set(da))&set(db)),b_imports_satisfied_by_a=sorted((set(ub)-set(db))&set(da)),combined_unresolved=sorted((set(ua)|set(ub))-(set(da)|set(db))))
with tempfile.TemporaryDirectory(prefix='g2-source-link-census-') as td:
 for names in [('bootloader',),('audio_main',),('case',),('touch',),('bootloader','audio_main'),('case','touch')]:
  key='+'.join(names);out=Path(td)/(key+'.o')
  cmd=['arm-none-eabi-ld','-r','--whole-archive',*[str(archives[n]) for n in names],'--no-whole-archive','-o',str(out)]
  p=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60)
  target=report[names[0]] if len(names)==1 else pairs[key]
  target['whole_archive_relocatable_link']=dict(exit_code=p.returncode,diagnostic=p.stderr[:5000],output_sha256=hashlib.sha256(out.read_bytes()).hexdigest() if out.exists() and p.returncode==0 else None)
receipt=dict(status='READ_ONLY_RELOCATABLE_FEASIBILITY_CENSUS',captured_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),bootloader_build_inventory_sha256=hashlib.sha256((D/'bootloader-snapshot-build/inventory.json').read_bytes()).hexdigest(),archives=report,pairs=pairs,scope=['Relocatable -r links only; no absolute image, vector table, startup placement, memory map or checksum was produced.','Bootloader and audio are distinct Apollo image ownership despite common Cortex-M55; case and Touch are distinct Cortex-M0+ firmware images. Pair links are collision diagnostics only; separate image archives must not be paired for a production link.','Archive imports are names, not proof of matching product ABI or behavior.'])
(D/'archive-feasibility-census.json').write_text(json.dumps(receipt,indent=2)+'\n')
for n,x in report.items():print(n,x['member_count'],x['defined_symbol_count'],x['undefined_symbol_count'],len(x['external_unresolved']),len(x['duplicate_strong_definitions']),x['whole_archive_relocatable_link']['exit_code'])
for n,x in pairs.items():print(n,'shared',x['shared_export_count'],'strong',x['strong_collision_count'],'combined unresolved',len(x['combined_unresolved']),'link',x['whole_archive_relocatable_link']['exit_code'])
