#!/usr/bin/env python3
"""Verify/extract official IAR Base and install into isolated amd64 Ubuntu."""
import argparse,hashlib,json,os,shutil,subprocess,tarfile,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
CACHE=HERE.parents[1]/'third-party/local-vendor'
NAME='cxarm-10.10.2-linux-x86_64-base.tar.bz2'
SHA='b4fe2e43ec6e40e574f15a624e3c41f855cddf1e816ce852b1811bf10353cdb0'
EULA='8351c09200a37728cc60abc92a052268a6dbef32a2c8ba3a91e00504b89f8a4c'
IMAGE='opencfw/iar-base:10.10.2-local'
LMSC='iar-lmsc-tools_1.14_amd64.deb'
LMSC_SHA='0bb55aafd8ed02400c494827279149e115fc1b3ae593a4b4841f9073baf99db1'
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1024*1024):h.update(b)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--apply',action='store_true');a=ap.parse_args()
 if not a.apply:
  print('Dry run: verify official Base; safe local extraction; build isolated linux/amd64 Ubuntu24.04 image. No license key/token access or activation.');return
 manifest=json.loads((HERE/'manifest.json').read_text())
 if not manifest.get('acceptance_evidence'):ap.error('Prior user acceptance evidence required')
 archive=CACHE/'artifacts'/NAME
 if archive.is_symlink() or not archive.is_file() or digest(archive)!=SHA:ap.error('Archive missing or hash mismatch')
 lmsc=CACHE/'artifacts'/LMSC
 if lmsc.is_symlink() or not lmsc.is_file() or digest(lmsc)!=LMSC_SHA:ap.error('LMSC package missing or hash mismatch')
 target=CACHE/'toolchains/iar-linux-x86_64';target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():
  if target.is_symlink() or (target/'.archive-sha256').read_text().strip()!=SHA:ap.error('Existing extraction provenance mismatch')
 else:
  with tempfile.TemporaryDirectory(dir=target.parent) as tmp:
   staging=Path(tmp)/'sdk';staging.mkdir()
   with tarfile.open(archive,'r:bz2') as t:
    members=t.getmembers()
    if len(members)>20000 or sum(m.size for m in members)>2*1024**3:ap.error('Archive expansion bounds exceeded')
    t.extractall(staging,filter='data')
   eula=staging/'cxarm-10.10.2/common/doc/licenses/IAR_EndUserLicenseAgreement.pdf'
   if digest(eula)!=EULA:ap.error('Bundled agreement differs from reviewed/accepted agreement')
   (staging/'.archive-sha256').write_text(SHA+'\n');os.rename(staging,target)
 context=CACHE/'iar-base-container-build';context.mkdir(exist_ok=True)
 allowed={'cxarm-10.10.2','Dockerfile','.dockerignore',LMSC}
 if any(p.name not in allowed for p in context.iterdir()):ap.error('Unexpected build-context entry')
 # Only the authenticated vendor tree enters this image, never the repo/home.
 tree=context/'cxarm-10.10.2'
 if not tree.exists():
  with tempfile.TemporaryDirectory(dir=context) as tmp:
   staging=Path(tmp)/'tree';shutil.copytree(target/'cxarm-10.10.2',staging,symlinks=True)
   os.rename(staging,tree)
 if tree.is_symlink() or digest(tree/'common/doc/licenses/IAR_EndUserLicenseAgreement.pdf')!=EULA:ap.error('Context agreement provenance mismatch')
 shutil.copy2(lmsc,context/LMSC)
 (context/'.dockerignore').write_text('*\n!Dockerfile\n!'+LMSC+'\n!cxarm-10.10.2/**\n')
 (context/'Dockerfile').write_text('FROM --platform=linux/amd64 ubuntu:24.04@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55\nCOPY '+LMSC+' /tmp/iar-lmsc.deb\nRUN apt-get update && apt-get install -y --no-install-recommends libstdc++6 libgcc-s1 libxml2 libglib2.0-0t64 /tmp/iar-lmsc.deb && rm -rf /var/lib/apt/lists/* /tmp/iar-lmsc.deb\nCOPY cxarm-10.10.2 /opt/iar/cxarm-10.10.2\nENV PATH="/opt/iar/cxarm-10.10.2/arm/bin:/opt/iar/cxarm-10.10.2/common/bin:${PATH}"\nWORKDIR /work\n')
 docker=['docker']
 probe=subprocess.run(docker+['buildx','version'],capture_output=True,text=True)
 if probe.returncode:
  plugins=Path('/opt/homebrew/lib/docker/cli-plugins')
  if not (plugins/'docker-buildx').is_file():ap.error('Docker Buildx required; install docker-buildx first')
  config=CACHE/'docker-build-config';config.mkdir(exist_ok=True)
  # Never read or modify the user's credential-bearing Docker config.
  (config/'config.json').write_text(json.dumps({'cliPluginsExtraDirs':[str(plugins)]})+'\n')
  endpoint=subprocess.check_output(['docker','context','inspect','colima','--format','{{(index .Endpoints "docker").Host}}'],text=True).strip()
  if not endpoint.startswith('unix://'):ap.error('Expected local Colima Unix socket')
  docker=['docker','--host',endpoint,'--config',str(config)]
 subprocess.run(docker+['buildx','build','--platform','linux/amd64','--load','-t',IMAGE,str(context)],check=True)
 print('IAR Base image installed locally; activation and licensed compilation remain unverified. No key/token accessed.')
if __name__=='__main__':main()
