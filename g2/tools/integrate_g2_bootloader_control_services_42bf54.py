#!/usr/bin/env python3
"""Register source-owned readiness, event-wait, guarded-dispatch, and power controls."""
from __future__ import annotations
import csv,hashlib,io,json
from pathlib import Path
R=Path(__file__).resolve().parent.parent;O=R/"components/bootloader/core_overlay/overlay.json";S=R/"components/bootloader/core_overlay/runtime_control_services_42bf54.c";B=R/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";C=R/"tools/manifests/g2-bootloader-post-mspi-frontier.tsv";BASE=0x410000
SS=5976;SH="9dde955e64abee4a26392122fc0a85572791a5a3c7b09e17e00d7c97f298788b";FL=["-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never"]
ITEMS=(("open_cfw_bootloader_hardware_readiness_gate_42bf54",0x42BF54,0x42BFA4,"ea709a4b368ad40d8d1cc341d60deb5b3a84f33f0c7b080832f667538266c878","33f339eb82333f369613a9c61ca88edc397cd53acec61d1c5eccf06c8ef782fb",((0x14,"open_cfw_bootloader_mode_query_41bf84",0x41BF84),(0x26,"open_cfw_bootloader_float_probe_41ca2c",0x41CA2C),(0x38,"open_cfw_bootloader_delay_status_change_41d21c",0x41D21C))),("open_cfw_bootloader_event_wait_mask_42e2a2",0x42E2A2,0x42E2EA,"f7d5ce722b09295e04d5c2525cb58137a589a07472efd03673b559a8291cc085","4cb7aa4f0eee6a8f24c5b089cd03a53dd47fb0e07726c03696acb3ba3a73b007",((0x0E,"open_cfw_bootloader_runtime_transfer_41623a",0x41623A),(0x1E,"open_cfw_bootloader_runtime_flags_wait_416590",0x416590),(0x40,"open_cfw_bootloader_log_4176ce",0x4176CE))),("open_cfw_bootloader_aligned_guarded_dispatch_42e4a0",0x42E4A0,0x42E4F4,"d0924cd0559fc057d2a0eb2aa7558f1ef4a237b073daad60d1e80bab754b317e","9d909667005fac9e5860e1e3d64146fc43bfab6d21479ea9dbab8b24682eb0f2",((0x1C,"open_cfw_bootloader_critical_enter_41b8ec",0x41B8EC),(0x22,"open_cfw_bootloader_runtime_lock_41bd92",0x41BD92),(0x30,"open_cfw_bootloader_guarded_call_cleanup_42e8a4",0x42E8A4),(0x36,"open_cfw_bootloader_runtime_unlock_41bde4",0x41BDE4))),("open_cfw_bootloader_register_power_toggle_42f1c8",0x42F1C8,0x42F204,"938e0f238204451a2aff50fd378808f5f3d2780c3627018935d2e382e94f9361","3a7d939562c4ed98e8b8a506ec3835ba2e13fe65fc0063caa9f5882347627696",((0x16,"open_cfw_bootloader_delay_cycles_41d1c0",0x41D1C0),(0x1C,"open_cfw_bootloader_power_control_41c838",0x41C838),(0x24,"open_cfw_bootloader_power_control_41c838",0x41C838),(0x2A,"open_cfw_bootloader_delay_cycles_41d1c0",0x41D1C0))))
def sha(x:bytes)->str:return hashlib.sha256(x).hexdigest()
def main()->int:
 source=S.read_bytes();boot=B.read_bytes()
 if (len(source),sha(source))!=(SS,SH):raise SystemExit("control-services source changed")
 record={"path":S.relative_to(R).as_posix(),"size":SS,"sha256":SH,"license":"MIT","origin":"clean-room readiness, event wait, guarded dispatch, and register-power controls","evidence":"docs/research/g2-bootloader-control-services-42bf54-source-closure.md"};entries=[]
 for fn,a,z,h,u,rs in ITEMS:
  if sha(boot[a-BASE:z-BASE])!=h:raise SystemExit(f"body changed: {fn}")
  rr=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":s,"symbol_type":"STT_NOTYPE","target_address":t} for o,s,t in rs];pins={"size":z-a,"sha256":h,"unrelocated_sha256":u};entries.append({"function":fn,"runtime_address":a,"source":record,"toolchain":{"target":"arm-none-eabi","reviewed_version_prefix":"Apple clang version 21.0.0","flags":FL},"strict_relocation_contract":True,"expected":pins,"stock":{"size":z-a,"sha256":h},"relocations":rr,"allow_discarded_alloc_sections":True,"toolchain_profiles":{"linux-clang":{"reviewed_version_prefix":"Homebrew clang version 22.1.8","expected":pins,"stock":{"size":z-a,"sha256":h},"relocations":rr}}})
 overlay=json.loads(O.read_text());names={x[0] for x in ITEMS};overlay["in_place_leaves"]=sorted([x for x in overlay["in_place_leaves"] if x.get("function") not in names]+entries,key=lambda x:int(x["runtime_address"]));tmp=O.with_name(f".{O.name}.tmp");tmp.write_text(json.dumps(overlay,indent=2)+"\n");tmp.replace(O)
 with C.open(newline="") as f:reader=csv.DictReader(f,delimiter="\t");fields=list(reader.fieldnames or ());rows=list(reader)
 by={int(x["start"],16):x for x in rows}
 for fn,a,z,*_ in ITEMS:
  row=by.get(a)
  if row is None or int(row["end"],16)!=z:raise SystemExit(f"census changed: {fn}")
  row.update({"kind":"source_function","name":fn.removeprefix("open_cfw_bootloader_"),"disposition":"source_owned_production","provider":"clean-room runtime control service","license_status":"MIT","evidence":"exact dual-toolchain body with portable behavioral model"})
 out=io.StringIO(newline="");writer=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n");writer.writeheader();writer.writerows(rows);C.write_text(out.getvalue());print("registered runtime control services");return 0
if __name__=="__main__":raise SystemExit(main())
