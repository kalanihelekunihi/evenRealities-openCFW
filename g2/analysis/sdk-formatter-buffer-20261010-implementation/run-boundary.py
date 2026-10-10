from pathlib import Path
import subprocess,json
D=Path(__file__).parent;SDK=D.parent/'sdk-runtime-link-20261010-implementation';rows=[];compiles=[]
for variant in ['plain','apollo5-aligned']:
 cmd=['/usr/bin/clang','-O1','-g','-fno-builtin','-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-omit-frame-pointer','-I'+str(SDK),str(D/'harness-boundary.c'),str(SDK/'am_util_stdio.c'),'-o',str(D/(variant+'-boundary'))]+(['-DAM_PART_APOLLO5_API'] if variant!='plain' else [])
 r=subprocess.run(cmd,capture_output=True,text=True);(D/(variant+'-boundary-compile.txt')).write_text(r.stdout+r.stderr);compiles.append({'command':cmd,'exit':r.returncode});assert r.returncode==0,r.stderr
 for length in [1022,1023]:
  for n in [1022,1023]:
   for mode in [0,1]:
    cmd=[str(D/(variant+'-boundary')),str(length),str(n),str(mode)];r=subprocess.run(cmd,capture_output=True,text=True);receipt=f'{variant}-boundary-{length}-{n}-{mode}';(D/(receipt+'.stdout')).write_text(r.stdout);(D/(receipt+'.stderr')).write_text(r.stderr);rows.append({'variant':variant,'length':length,'n':n,'mode':mode,'command':cmd,'exit':r.returncode,'stdout_receipt':receipt+'.stdout','stderr_receipt':receipt+'.stderr'});assert r.returncode==0,(receipt,r.stdout,r.stderr)
(D/'boundary-results.json').write_text(json.dumps({'compiles':compiles,'cases':rows,'count':len(rows),'all_pass':True},indent=2)+'\n');print(len(rows),'max-buffer capacity cases PASS')
