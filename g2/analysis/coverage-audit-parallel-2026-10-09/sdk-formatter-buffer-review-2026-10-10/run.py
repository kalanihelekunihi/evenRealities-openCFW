from pathlib import Path
import subprocess,json,hashlib
D=Path(__file__).parent;SDK=Path('g2/analysis/sdk-runtime-link-20261010-implementation');rows=[];compiles=[]
for variant in ['plain','apollo5-aligned']:
 cmd=['/usr/bin/clang','-O1','-g','-fno-builtin','-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-omit-frame-pointer','-I'+str(SDK),str(D/'harness.c'),str(SDK/'am_util_stdio.c'),'-o',str(D/variant)]+(['-DAM_PART_APOLLO5_API'] if variant!='plain' else [])
 r=subprocess.run(cmd,capture_output=True,text=True);(D/f'{variant}-compile.txt').write_text(r.stdout+r.stderr);compiles.append({'command':cmd,'exit':r.returncode});assert r.returncode==0,r.stderr
 # Both public snprintf and va_list entry; exact-size destination ends at PROT_NONE.
 cases=[(0,n) for n in [0,1,3,4,5,6,1023,1024,0xffffffff]]+[(i,64) for i in range(1,9)]+[(5,n) for n in [0,1]]+[(6,n) for n in [1,2]]+[(11,n) for n in [1024,0xffffffff]]
 for case,n in cases:
  for mode in [0,1]:
   r=subprocess.run([str(D/variant),str(case),str(n),str(mode)],capture_output=True,text=True);receipt=f'{variant}-{case}-{n}-{mode}';(D/(receipt+'.stdout')).write_text(r.stdout);(D/(receipt+'.stderr')).write_text(r.stderr)
   rows.append({'variant':variant,'case':case,'n':n,'mode':mode,'exit':r.returncode,'stdout_receipt':receipt+'.stdout','stderr_receipt':receipt+'.stderr','expected_normal_completion':True})
   if r.returncode:print('FAILED',receipt,r.stdout,r.stderr[:600])
 # Deliberately oversized internal formatting is isolated per process; no target/hardware.
 for case,n in [(9,1),(9,0),(10,1)]:
  r=subprocess.run([str(D/variant),str(case),str(n),'0'],capture_output=True,text=True);receipt=f'{variant}-internal-{case}-{n}';(D/(receipt+'.stdout')).write_text(r.stdout);(D/(receipt+'.stderr')).write_text(r.stderr);rows.append({'variant':variant,'case':case,'n':n,'exit':r.returncode,'stdout_receipt':receipt+'.stdout','stderr_receipt':receipt+'.stderr','internal_boundary_probe':True,'asan_global_overflow':'global-buffer-overflow' in r.stderr})
(D/'results.json').write_text(json.dumps({'compiles':compiles,'unchanged_sdk_source_sha256':hashlib.sha256((SDK/'am_util_stdio.c').read_bytes()).hexdigest(),'cases':rows,'scope':'native macOS arm64 sanitized source; exact-size mmap destination guards; independent process per case; no SDK source edits'},indent=2)+'\n');print('Recorded',len(rows),'cases; normal failures',sum(bool(r['exit']) for r in rows if r.get('expected_normal_completion')))
