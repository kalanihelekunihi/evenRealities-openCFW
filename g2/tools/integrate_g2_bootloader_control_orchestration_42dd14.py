#!/usr/bin/env python3
"""Register source-owned control orchestration and critical dispatch transaction."""
from __future__ import annotations
import csv,hashlib,io,json
from pathlib import Path
R=Path(__file__).resolve().parent.parent;O=R/"components/bootloader/core_overlay/overlay.json";S=R/"components/bootloader/core_overlay/runtime_control_orchestration_42dd14.c";B=R/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";C=R/"tools/manifests/g2-bootloader-post-mspi-frontier.tsv";BASE=0x410000
SS=3424;SH="96814607130a7fbac6b8c8c974b22302457c796715930fad6df4943b342f58cd";FL=["-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never"]
ITEMS=(("open_cfw_bootloader_control_orchestrator_42dd14",0x42DD14,0x42DD68,"bed813bc7b04b8ac8dffe02c444a4ac57d3d2d95af223d02cad46acde08ff524","c69f469c3ed42dd95b6493d1c3a0f97f7f0c47b0486c23219164169f7f453caa",((0x02,"open_cfw_bootloader_control_one_wrapper_42dd9a",0x42DD9A),(0x06,"open_cfw_bootloader_runtime_queue_context_init_42dd70",0x42DD70),(0x0A,"open_cfw_bootloader_runtime_context_wrapper_42dd68",0x42DD68),(0x0E,"open_cfw_bootloader_noop_callback_42dd98",0x42DD98),(0x12,"open_cfw_bootloader_control_two_wrapper_42dda4",0x42DDA4),(0x18,"open_cfw_bootloader_control_bits_dispatch_42e1c4",0x42E1C4),(0x26,"open_cfw_bootloader_event_wait_4162c4",0x4162C4),(0x4E,"open_cfw_bootloader_log_4176ce",0x4176CE))),("open_cfw_bootloader_critical_dispatch_transaction_42de0e",0x42DE0E,0x42DE58,"ac57a9b6547160c8259307f2400e572680d610c2d7d8913fe30f29b21c1e28f0","df0a8dfa30390dd20818f35e9c91213538e151d35b97eaaf1a55e40049650524",((0x16,"open_cfw_bootloader_log_4176ce",0x4176CE),(0x1C,"open_cfw_bootloader_critical_enter_41b8ec",0x41B8EC),(0x28,"open_cfw_bootloader_memcpy_words_4156ac",0x4156AC),(0x34,"open_cfw_bootloader_alignment_dispatch_42e4f4",0x42E4F4),(0x42,"open_cfw_bootloader_terminal_mode_42e514",0x42E514))))
def sha(x:bytes)->str:return hashlib.sha256(x).hexdigest()
def main()->int:
 source=S.read_bytes();boot=B.read_bytes()
 if (len(source),sha(source))!=(SS,SH):raise SystemExit("control-orchestration source changed")
 record={"path":S.relative_to(R).as_posix(),"size":SS,"sha256":SH,"license":"MIT","origin":"clean-room event/control orchestration and critical dispatch transaction","evidence":"docs/research/g2-bootloader-control-orchestration-42dd14-source-closure.md"};entries=[]
 for fn,a,z,h,u,rs in ITEMS:
  if sha(boot[a-BASE:z-BASE])!=h:raise SystemExit(f"body changed: {fn}")
  rr=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":s,"symbol_type":"STT_NOTYPE","target_address":t} for o,s,t in rs];pins={"size":z-a,"sha256":h,"unrelocated_sha256":u};entries.append({"function":fn,"runtime_address":a,"source":record,"toolchain":{"target":"arm-none-eabi","reviewed_version_prefix":"Apple clang version 21.0.0","flags":FL},"strict_relocation_contract":True,"expected":pins,"stock":{"size":z-a,"sha256":h},"relocations":rr,"allow_discarded_alloc_sections":True,"toolchain_profiles":{"linux-clang":{"reviewed_version_prefix":"Homebrew clang version 22.1.8","expected":pins,"stock":{"size":z-a,"sha256":h},"relocations":rr}}})
 overlay=json.loads(O.read_text());names={x[0] for x in ITEMS};overlay["in_place_leaves"]=sorted([x for x in overlay["in_place_leaves"] if x.get("function") not in names]+entries,key=lambda x:int(x["runtime_address"]));tmp=O.with_name(f".{O.name}.tmp");tmp.write_text(json.dumps(overlay,indent=2)+"\n");tmp.replace(O)
 with C.open(newline="") as f:reader=csv.DictReader(f,delimiter="\t");fields=list(reader.fieldnames or ());rows=list(reader)
 by={int(x["start"],16):x for x in rows}
 for fn,a,z,*_ in ITEMS:
  row=by.get(a)
  if row is None or int(row["end"],16)!=z:raise SystemExit(f"census changed: {fn}")
  row.update({"kind":"source_function","name":fn.removeprefix("open_cfw_bootloader_"),"disposition":"source_owned_production","provider":"clean-room control orchestration service","license_status":"MIT","evidence":"exact dual-toolchain body with portable behavioral model"})
 out=io.StringIO(newline="");writer=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n");writer.writeheader();writer.writerows(rows);C.write_text(out.getvalue());print("registered control orchestration services");return 0
if __name__=="__main__":raise SystemExit(main())
