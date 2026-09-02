#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,io,json
from pathlib import Path
R=Path(__file__).resolve().parent.parent;O=R/'components/bootloader/core_overlay/overlay.json';C=R/'tools/manifests/g2-bootloader-post-mspi-frontier.tsv';B=R/'blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin';S=R/'components/bootloader/core_overlay/runtime_spotmgr_trim_helpers_42adb8.c';SH='c4cbf548a28eb5ea192392ae0c48a6d6c671e18e9b1c53fe10a903699cb7b1d7';FL=['-mcpu=cortex-m55','-mthumb','-Oz','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-Wall','-Wextra','-Werror','-fno-ident','-mllvm','-enable-machine-outliner=never'];SS=(('open_cfw_bootloader_spotmgr_trim_enable_42adb8','spotmgr_trim_enable_42adb8',0x42ADB8,0x42AE24,'7b25d7dae842d5787345a5360a32fbf21f4adadc88e216b2eaa272cc77d7feda'),('open_cfw_bootloader_spotmgr_profile_trim_42ae24','spotmgr_profile_trim_42ae24',0x42AE24,0x42AE6C,'73da1f0b69f23d583009d5dfbc2f46007ee0f8b9f56a5c8a3b4fccd58136f538'),('open_cfw_bootloader_spotmgr_trim_restore_42ae6c','spotmgr_trim_restore_42ae6c',0x42AE6C,0x42AE9C,'fbc7ca52270345ca6b251d1c8c805a06e33af456500f9b17e05cfa7743af79f8'))
def h(b):return hashlib.sha256(b).hexdigest()
def main():
 s=S.read_bytes();assert(len(s),h(s))==(4349,SH);boot=B.read_bytes();entries=[]
 for f,n,a,z,x in SS:
  assert h(boot[a-0x410000:z-0x410000])==x;p={'size':z-a,'sha256':x,'unrelocated_sha256':x};entries.append({'function':f,'runtime_address':a,'source':{'path':S.relative_to(R).as_posix(),'size':len(s),'sha256':SH,'license':'BSD-3-Clause','origin':'Apollo510-compatible SPOT-manager trim register helpers','upstream':'AmbiqSuite SDK 5.1.0 Apollo510 SPOT manager','upstream_commit':'5efc0228528a8adce5eae0d226fac85d2551eb3b','evidence':'docs/research/g2-bootloader-spotmgr-trim-helpers-42adb8-source-closure.md'},'toolchain':{'target':'arm-none-eabi','reviewed_version_prefix':'Apple clang version 21.0.0','flags':FL},'strict_relocation_contract':True,'expected':p,'stock':{'size':z-a,'sha256':x},'relocations':[],'allow_discarded_alloc_sections':True,'toolchain_profiles':{'linux-clang':{'reviewed_version_prefix':'Homebrew clang version 22.1.8','expected':p,'stock':{'size':z-a,'sha256':x},'relocations':[]}}})
 o=json.loads(O.read_text());names={x[0]for x in SS};o['in_place_leaves']=sorted([x for x in o['in_place_leaves']if x.get('function')not in names]+entries,key=lambda x:int(x['runtime_address']));t=O.with_name('.overlay.json.tmp');t.write_text(json.dumps(o,indent=2)+'\n');t.replace(O)
 with C.open(newline='')as f:r=csv.DictReader(f,delimiter='\t');fs=r.fieldnames;rows=list(r)
 found=set()
 for x in rows:
  for _f,n,a,z,hh in SS:
   if int(x['start'],16)==a:x.update(kind='source_function',name=n,disposition='source_owned_production',provider='AmbiqSuite Apollo510 SPOT-manager trim helper',license_status='BSD-3-Clause',evidence='exact dual-toolchain and Apollo-main body with host bitfield semantics');found.add(a)
 assert len(found)==3;q=io.StringIO(newline='');w=csv.DictWriter(q,fieldnames=fs,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows);C.write_text(q.getvalue());print('registered three SPOT-manager trim helpers')
if __name__=='__main__':main()
