#!/usr/bin/env python3
"""Register source-owned state, traversal, hardware, boot, and validation services."""
from __future__ import annotations
import csv,hashlib,io,json
from pathlib import Path
R=Path(__file__).resolve().parent.parent;O=R/"components/bootloader/core_overlay/overlay.json";S=R/"components/bootloader/core_overlay/runtime_small_services_42cea4.c";B=R/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";C=R/"tools/manifests/g2-bootloader-post-mspi-frontier.tsv";BASE=0x410000
SS=5812;SH="1434af9c297fef8ae3bd4317723aa51d6fb5e7811f36da9a6919b46baef4ef71";FL=["-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never"]
ITEMS=(("open_cfw_bootloader_state_update_critical_42cea4",0x42CEA4,0x42CED8,"5e1f4567b244b4e447b9c7adefa7e1995a8994847c42da20da7cacf0269c17e1","f4e996fb208d73eaba0069e306a1306ba73bc28b9a5acf50b43695df8a86a49b",((0x04,"open_cfw_bootloader_critical_enter_41b8ec",0x41B8EC),(0x28,"open_cfw_bootloader_state_adjust_42cdf8",0x42CDF8))),("open_cfw_bootloader_chunked_indirect_visit_42d9f0",0x42D9F0,0x42DA1E,"8094a3c36380823dea4b1d9e382fd01bfc1ada3907d83eba63f3e603f1230620","8094a3c36380823dea4b1d9e382fd01bfc1ada3907d83eba63f3e603f1230620",()),("open_cfw_bootloader_hardware_channel_normalize_42eda0",0x42EDA0,0x42EDF6,"d8c726d50ce3b131a09fbd3baf26fa0be431dc76187560db65fe8e26b81e267e","90191c215f584a81ffca65fc2a302b2d878667c0169c12c97b1acf631afcfe55",((0x46,"open_cfw_bootloader_clock_config_422364",0x422364),)),("open_cfw_bootloader_platform_boot_sequence_4301d6",0x4301D6,0x4301F4,"c1c946447d989615f057be7707475b14318dd6dc4f4db74fe603c662d579fd86","78f443c4dd221116c3a8cbd6acdc74c3038e22285eaabf79e44acd8bd84b3aef",((0x06,"open_cfw_bootloader_scb_priority_nibble_430280",0x430280),(0x0A,"open_cfw_bootloader_mode_one_apply_42fff2",0x42FFF2),(0x0E,"open_cfw_bootloader_platform_stage_430000",0x430000),(0x12,"open_cfw_bootloader_platform_prepare_41f612",0x41F612),(0x16,"open_cfw_bootloader_platform_finish_430502",0x430502))),("open_cfw_bootloader_address_validate_430a60",0x430A60,0x430A9C,"a4764c54fa357e914e1d59504315967881f056b4a078c086b0597de5c669896b","9ce9a927e722650fcc0ec7b8764a9be70b94f047c7c7c26afaab0404abcc8572",((0x1A,"open_cfw_bootloader_address_limit_query_41d792",0x41D792),)))
def sha(x:bytes)->str:return hashlib.sha256(x).hexdigest()
def main()->int:
 source=S.read_bytes();boot=B.read_bytes()
 if (len(source),sha(source))!=(SS,SH):raise SystemExit("small-services source changed")
 record={"path":S.relative_to(R).as_posix(),"size":SS,"sha256":SH,"license":"MIT","origin":"clean-room state, traversal, hardware-normalization, boot, and validation services","evidence":"docs/research/g2-bootloader-small-services-42cea4-source-closure.md"};entries=[]
 for fn,a,z,h,u,rs in ITEMS:
  if sha(boot[a-BASE:z-BASE])!=h:raise SystemExit(f"body changed: {fn}")
  rr=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":s,"symbol_type":"STT_NOTYPE","target_address":t} for o,s,t in rs];pins={"size":z-a,"sha256":h,"unrelocated_sha256":u};entries.append({"function":fn,"runtime_address":a,"source":record,"toolchain":{"target":"arm-none-eabi","reviewed_version_prefix":"Apple clang version 21.0.0","flags":FL},"strict_relocation_contract":True,"expected":pins,"stock":{"size":z-a,"sha256":h},"relocations":rr,"allow_discarded_alloc_sections":True,"toolchain_profiles":{"linux-clang":{"reviewed_version_prefix":"Homebrew clang version 22.1.8","expected":pins,"stock":{"size":z-a,"sha256":h},"relocations":rr}}})
 overlay=json.loads(O.read_text());names={x[0] for x in ITEMS};overlay["in_place_leaves"]=sorted([x for x in overlay["in_place_leaves"] if x.get("function") not in names]+entries,key=lambda x:int(x["runtime_address"]));tmp=O.with_name(f".{O.name}.tmp");tmp.write_text(json.dumps(overlay,indent=2)+"\n");tmp.replace(O)
 with C.open(newline="") as f:reader=csv.DictReader(f,delimiter="\t");fields=list(reader.fieldnames or ());rows=list(reader)
 by={int(x["start"],16):x for x in rows}
 for fn,a,z,*_ in ITEMS:
  row=by.get(a)
  if row is None or int(row["end"],16)!=z:raise SystemExit(f"census changed: {fn}")
  row.update({"kind":"source_function","name":fn.removeprefix("open_cfw_bootloader_"),"disposition":"source_owned_production","provider":"clean-room small runtime service","license_status":"MIT","evidence":"exact dual-toolchain body with portable behavioral model"})
 out=io.StringIO(newline="");writer=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n");writer.writeheader();writer.writerows(rows);C.write_text(out.getvalue());print("registered small runtime services");return 0
if __name__=="__main__":raise SystemExit(main())
