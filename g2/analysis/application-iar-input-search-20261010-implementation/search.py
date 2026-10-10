from pathlib import Path
import zipfile,hashlib,json,re,subprocess
D=Path(__file__).parent;roots=[Path('/Users/kalani/Repo/evenRealities-openCFW'),Path('/Users/kalani/Repo/jimrandomh/g2-firmware-emulator')];pat=re.compile(r'__aeabi_assert|__assert_func|__iar_ReportAssert|s200_ap510b_iar_git');projects=[];hits=[];commands=[]
for root in roots:
 cmd=['rg','--files','-uuu','-g','!**/.git/**','-g','!**/node_modules/**','-g','!**/g2/build/offline-xuantie-csky-dsp-20261009T201800Z/**',str(root)];r=subprocess.run(cmd,capture_output=True,text=True);commands.append({'command':cmd,'exit':r.returncode});assert r.returncode==0
 for name in r.stdout.splitlines():
  p=Path(name)
  if p.suffix.lower() in ['.icf','.ewp','.eww','.sct']:
   b=p.read_bytes();projects.append({'path':name,'sha256':hashlib.sha256(b).hexdigest(),'size':len(b),'application_path_tokens':bool(re.search(rb's200_ap510b_iar_git|s200\.ewp|s200\.icf',b,re.I))})
 cmd=['rg','-l','-uuu','-g','*.c','-g','*.h','-g','*.icf','-g','*.ewp','-g','!**/.git/**','-g','!**/node_modules/**','-g','!**/g2/build/offline-xuantie-csky-dsp-20261009T201800Z/**','__aeabi_assert|__assert_func|__iar_ReportAssert|s200_ap510b_iar_git',str(root)];r=subprocess.run(cmd,capture_output=True,text=True);commands.append({'command':cmd,'exit':r.returncode,'stderr':r.stderr});assert r.returncode in [0,1]
 for name in r.stdout.splitlines():
  p=Path(name);b=p.read_bytes();hits.append({'path':name,'sha256':hashlib.sha256(b).hexdigest(),'tokens':sorted(set(pat.findall(b.decode('utf-8',errors='replace'))))})
zpath=Path('/Users/kalani/Downloads/AmbiqSuite_5.2.0.zip');z=zipfile.ZipFile(zpath);sdkprojects=[];sdkhits=[];count=0
for n in z.namelist():
 suffix=Path(n).suffix.lower()
 if suffix in ['.icf','.ewp','.eww','.sct']:
  b=z.read(n);sdkprojects.append({'member':n,'sha256':hashlib.sha256(b).hexdigest(),'application_path_tokens':bool(re.search(rb's200_ap510b_iar_git|s200\.ewp|s200\.icf',b,re.I))})
 if suffix not in ['.c','.h','.icf','.ewp']:continue
 if not any(x in n for x in ['/mcu/apollo510/','/mcu/apollo510b/','/boards/apollo510b_evb/','/utils/']):continue
 count+=1;b=z.read(n);tokens=sorted(set(pat.findall(b.decode('utf-8',errors='replace'))))
 if tokens:sdkhits.append({'member':n,'sha256':hashlib.sha256(b).hexdigest(),'tokens':tokens})
header=roots[0]/'third-party/local-vendor/toolchains/iar-linux-x86_64/cxarm-10.10.2/arm/inc/c/assert.h';b=header.read_bytes()
(D/'inventory.json').write_text(json.dumps({'commands':commands,'local_project_inputs':projects,'local_assert_or_application_path_hits':hits,'sdk_zip_sha256':hashlib.sha256(zpath.read_bytes()).hexdigest(),'sdk_project_inputs':sdkprojects,'sdk_scanned_relevant_text_files':count,'sdk_assert_or_application_path_hits':sdkhits,'read_only_IAR_assert_header':{'path':str(header),'sha256':hashlib.sha256(b).hexdigest(),'ICCARM_declaration_arity':3,'other_declaration_arity':4,'ICCARM_macro_arguments':['expression','file','line'],'other_macro_additional_argument':'function'},'limitations':'Exact searches over stated roots/tokens only; not source absence proof or full content inspection of every project'},indent=2)+'\n');print(json.dumps({'local_projects':len(projects),'local_hits':len(hits),'sdk_projects':len(sdkprojects),'sdk_scanned':count,'sdk_hits':sdkhits,'project_application_token_hits':[v for v in projects+sdkprojects if v['application_path_tokens']]}))
