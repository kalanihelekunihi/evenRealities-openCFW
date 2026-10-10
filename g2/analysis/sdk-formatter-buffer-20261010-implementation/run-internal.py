from pathlib import Path
import subprocess,json
D=Path(__file__).parent;SDK=D.parent/'sdk-runtime-link-20261010-implementation';cmd=['/usr/bin/clang','-O1','-g','-fno-builtin','-fsanitize=address,undefined','-fno-sanitize-recover=all','-DAM_PART_APOLLO5_API','-I'+str(SDK),str(D/'internal-guard.c'),'-o',str(D/'internal-guard')];r=subprocess.run(cmd,capture_output=True,text=True);(D/'internal-guard-compile.txt').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr;rows=[]
for length in [1024,2049]:
 r=subprocess.run([str(D/'internal-guard'),str(length)],capture_output=True,text=True);(D/f'internal-guard-{length}.stdout').write_text(r.stdout);(D/f'internal-guard-{length}.stderr').write_text(r.stderr);rows.append({'length':length,'exit':r.returncode,'asan_use_after_poison':'use-after-poison' in r.stderr})
assert rows[0]['exit']==0 and rows[1]['exit']!=0 and rows[1]['asan_use_after_poison'];(D/'internal-guard-results.json').write_text(json.dumps({'compile':cmd,'private_buffer_size':2048,'explicit_shadow_guard_bytes':64,'cases':rows,'limitation':'Single translation unit includes unchanged SDK source; test-only shadow guard, not separate production compilation'},indent=2)+'\n')
