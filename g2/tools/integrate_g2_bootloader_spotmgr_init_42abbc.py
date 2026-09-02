#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,io,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent; OVERLAY=ROOT/'components/bootloader/core_overlay/overlay.json'; CENSUS=ROOT/'tools/manifests/g2-bootloader-post-mspi-frontier.tsv'; BOOT=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'; SOURCE=ROOT/'components/bootloader/core_overlay/runtime_spotmgr_init_42abbc.c'
START=0x42ABBC;END=0x42AC4E;STOCK='1f0bfec6f59efe752ea106db7f7b7144fcd9b0df306919a7e03a7f2d550bca2d';RAW='d62bfd5f7ca5b79c01d63f55da969f21f422c5503ded4857cf20312f5cfc4a7a';SRC='c52963c37e84313c830e60254df242b5619685ff71e1a80a7ade1b4136264361';FUNCTION='open_cfw_bootloader_spotmgr_init_42abbc'
RELOCS=((0x3A,'open_cfw_bootloader_mram_read_421548',0x421548),(0x4C,'open_cfw_bootloader_mram_read_421548',0x421548),(0x72,'open_cfw_bootloader_mram_read_421548',0x421548),(0x88,'open_cfw_bootloader_spotmgr_runtime_init_41cc04',0x41CC04))
FLAGS=['-mcpu=cortex-m55','-mthumb','-Oz','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-Wall','-Wextra','-Werror','-fno-ident','-mllvm','-enable-machine-outliner=never']
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 source=SOURCE.read_bytes();assert (len(source),sha(source))==(3818,SRC);assert sha(BOOT.read_bytes()[START-0x410000:END-0x410000])==STOCK
 rr=[{'offset':o,'type':'R_ARM_THM_CALL','symbol':s,'symbol_type':'STT_NOTYPE','target_address':t} for o,s,t in RELOCS];pins={'size':146,'sha256':STOCK,'unrelocated_sha256':RAW}
 entry={'function':FUNCTION,'runtime_address':START,'source':{'path':SOURCE.relative_to(ROOT).as_posix(),'size':len(source),'sha256':SRC,'license':'BSD-3-Clause','origin':'Apollo510-compatible SPOT-manager initialization','upstream':'AmbiqSuite SDK 5.1.0 Apollo510 SPOT manager','upstream_commit':'5efc0228528a8adce5eae0d226fac85d2551eb3b','evidence':'docs/research/g2-bootloader-spotmgr-init-42abbc-source-closure.md'},'toolchain':{'target':'arm-none-eabi','reviewed_version_prefix':'Apple clang version 21.0.0','flags':FLAGS},'strict_relocation_contract':True,'expected':pins,'stock':{'size':146,'sha256':STOCK},'relocations':rr,'allow_discarded_alloc_sections':True,'toolchain_profiles':{'linux-clang':{'reviewed_version_prefix':'Homebrew clang version 22.1.8','expected':pins,'stock':{'size':146,'sha256':STOCK},'relocations':rr}}}
 ov=json.loads(OVERLAY.read_text());ov['in_place_leaves']=sorted([x for x in ov['in_place_leaves'] if x.get('function')!=FUNCTION]+[entry],key=lambda x:int(x['runtime_address']));tmp=OVERLAY.with_name('.overlay.json.tmp');tmp.write_text(json.dumps(ov,indent=2)+'\n');tmp.replace(OVERLAY)
 with CENSUS.open(newline='') as f:r=csv.DictReader(f,delimiter='\t');fields=r.fieldnames;rows=list(r)
 found=False
 for row in rows:
  if int(row['start'],16)==START:
   assert int(row['end'],16)==END and row['sha256']==STOCK;row.update(kind='source_function',name='spotmgr_init_42abbc',disposition='source_owned_production',provider='AmbiqSuite Apollo510 SPOT-manager initialization',license_status='BSD-3-Clause',evidence='exact dual-toolchain initialization with authenticated dispatch pointer, three MRAM reads, runtime-init edge, and host error paths');found=True
 assert found
 out=io.StringIO(newline='');w=csv.DictWriter(out,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows);CENSUS.write_text(out.getvalue());print('registered SPOT-manager init at 0x0042ABBC')
if __name__=='__main__':main()
