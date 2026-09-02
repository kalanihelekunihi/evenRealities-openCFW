#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,io,json
from pathlib import Path
R=Path(__file__).resolve().parent.parent;O=R/'components/bootloader/core_overlay/overlay.json';C=R/'tools/manifests/g2-bootloader-post-mspi-frontier.tsv';B=R/'blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin';S=R/'components/bootloader/core_overlay/runtime_spotmgr_trim_commit_42ae9c.c';F='open_cfw_bootloader_spotmgr_trim_commit_42ae9c';A=0x42AE9C;Z=0x42AEEC;H='62add64b9d5850045f7f332907406c01dc5f2ac1fbe500326b99a62d84a02904';U='0b2472da4b89f3dca0a6a8b877bcbb9f116587b6e8e9b4b18d609d218344a89e';SH='896fa6e31b957ff02a793b640012fe9b9a5d0c25ca98979273aa1957aea744e9';RS=((2,'open_cfw_bootloader_critical_enter_41b8ec',0x41B8EC),(8,'open_cfw_bootloader_spotmgr_trim_restore_42ae6c',0x42AE6C),(0x3E,'open_cfw_bootloader_spotmgr_trim_finalize_41ccd6',0x41CCD6),(0x44,'open_cfw_bootloader_spotmgr_profile_trim_42ae24',0x42AE24));FL=['-mcpu=cortex-m55','-mthumb','-Oz','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-Wall','-Wextra','-Werror','-fno-ident','-mllvm','-enable-machine-outliner=never']
def h(b):return hashlib.sha256(b).hexdigest()
def main():
 s=S.read_bytes();assert(len(s),h(s))==(1468,SH);boot=B.read_bytes();assert h(boot[A-0x410000:Z-0x410000])==H;rr=[{'offset':o,'type':'R_ARM_THM_CALL','symbol':n,'symbol_type':'STT_NOTYPE','target_address':t}for o,n,t in RS];p={'size':80,'sha256':H,'unrelocated_sha256':U};e={'function':F,'runtime_address':A,'source':{'path':S.relative_to(R).as_posix(),'size':len(s),'sha256':SH,'license':'BSD-3-Clause','origin':'Apollo510-compatible SPOT-manager critical trim commit','upstream':'AmbiqSuite SDK 5.1.0 Apollo510 SPOT manager','upstream_commit':'5efc0228528a8adce5eae0d226fac85d2551eb3b','evidence':'docs/research/g2-bootloader-spotmgr-trim-commit-42ae9c-source-closure.md'},'toolchain':{'target':'arm-none-eabi','reviewed_version_prefix':'Apple clang version 21.0.0','flags':FL},'strict_relocation_contract':True,'expected':p,'stock':{'size':80,'sha256':H},'relocations':rr,'allow_discarded_alloc_sections':True,'toolchain_profiles':{'linux-clang':{'reviewed_version_prefix':'Homebrew clang version 22.1.8','expected':p,'stock':{'size':80,'sha256':H},'relocations':rr}}};o=json.loads(O.read_text());o['in_place_leaves']=sorted([x for x in o['in_place_leaves']if x.get('function')!=F]+[e],key=lambda x:int(x['runtime_address']));t=O.with_name('.overlay.json.tmp');t.write_text(json.dumps(o,indent=2)+'\n');t.replace(O)
 with C.open(newline='')as f:r=csv.DictReader(f,delimiter='\t');fs=r.fieldnames;rows=list(r)
 out=[];done=False
 for x in rows:
  a=int(x['start'],16)
  if a==A:
   x.update(kind='source_function',name='spotmgr_trim_commit_42ae9c',end=f'0x{Z:08x}',size='80',sha256=H,disposition='source_owned_production',provider='AmbiqSuite Apollo510 SPOT-manager critical trim commit',license_status='BSD-3-Clause',evidence='corrected complete function boundary, exact dual-toolchain body, four provider edges, and host gate tests');out.append(x);done=True
  elif a==0x42AEE8:
   x.update(start='0x0042aeec',end='0x0042aef0',size='4',sha256='50d2d9924afd3fc31f64de7ee1bec779c5dc09901be357d9739996c617c0906d');out.append(x)
  else:out.append(x)
 assert done;q=io.StringIO(newline='');w=csv.DictWriter(q,fieldnames=fs,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(out);C.write_text(q.getvalue());print('registered complete SPOT-manager trim commit at 0x0042AE9C')
if __name__=='__main__':main()
