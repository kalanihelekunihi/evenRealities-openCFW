#!/usr/bin/env python3
"""Bind DM registry name to the already C-owned 196-byte dmConnCb block."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2"
SOURCE=G2/"components/audio/master_dispatch_candidate_20261014/pair_runtime_state.c"
PAIR=G2/"build/c-firmware/20261014/main-master-pair-runtime-state/receipt.json"
UPSTREAM=ROOT/"third-party/upstream/cordio/ble-host/sources/stack/dm/dm_conn.h"
BASE=G2/"build/c-firmware/20261015/main-dm-conn2-actions-remaining-4b6afa/apollo-main-dm-conn2-actions-remaining-4b6afa.o"
OUT=G2/"build/c-firmware/20261015/main-dm-conn-cb-storage-200712a4"
OLD="audio_dm_connection_records";ALIAS="audio_ble_dm_connection_registry"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def symbols(p,flag):
 return {line.split()[-1] for line in subprocess.check_output(["arm-none-eabi-nm","-g",flag,str(p)],text=True).splitlines()}
def entry(p,name):
 lines=subprocess.check_output(["arm-none-eabi-readelf","-sW",str(p)],text=True)
 rows=[]
 for line in lines.splitlines():
  parts=line.split()
  if parts and parts[-1]==name and len(parts)>=8:
   rows.append((int(parts[1],16),int(parts[2]),parts[3],parts[4],parts[5],parts[6]))
 if len(rows)!=1:raise RuntimeError(f"{name} symbol missing/duplicate")
 return rows[0]
def main():
 pair=json.loads(PAIR.read_text())
 if pair["status"]!="PASS_EXPERIMENTAL_MAIN_MASTER_PAIR_RUNTIME_STATE_C" or \
    pair["dm_cb_storage_bytes"]!=196 or pair["source_sha256"]!=sha(SOURCE):
  raise RuntimeError("current DM connection block evidence changed")
 upstream=UPSTREAM.read_text()
 for term in ("dmConnCcb_t     ccb[DM_CONN_MAX]","dmCback_t       connCback[DM_CLIENT_ID_MAX]",
              "hciConnSpec_t   connSpec[DM_NUM_PHYS]","uint16_t        scanWindow[DM_NUM_PHYS]"):
  if term not in upstream:raise RuntimeError("Cordio DM layout source changed")
 before=symbols(BASE,"-u")
 old=entry(BASE,OLD)
 if ALIAS not in before or old[1:4]!=(196,"OBJECT","GLOBAL"):
  raise RuntimeError("current C-owned DM block contract changed")
 OUT.mkdir(parents=True,exist_ok=True)
 linked=OUT/"apollo-main-dm-conn-cb-storage-200712a4.o"
 subprocess.run(["arm-none-eabi-ld","-r",str(BASE),
                 f"--defsym={ALIAS}={OLD}","-o",str(linked)],check=True)
 after=symbols(linked,"-u")
 alias=entry(linked,ALIAS);new_old=entry(linked,OLD)
 if before-after!={ALIAS} or after-before or len(before)!=201 or len(after)!=200 or \
    new_old[0]!=alias[0] or new_old[1]!=196:
  raise RuntimeError("DM registry alias link frontier changed")
 receipt={"status":"PASS_EXPERIMENTAL_MAIN_DM_CONN_CB_STORAGE_ALIAS_C",
          "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
          "pair_receipt":str(PAIR.relative_to(ROOT)),"pair_receipt_sha256":sha(PAIR),
          "upstream_source":str(UPSTREAM.relative_to(ROOT)),"upstream_sha256":sha(UPSTREAM),
          "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
          "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
          "source_owned_symbols":[ALIAS],"shared_bss_bytes":196,
          "alias_target":OLD,"alias_address":hex(alias[0]),
          "unresolved_before":len(before),"unresolved_after":len(after),
          "imports_resolved":[ALIAS],"imports_added":[],
          "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
          "limits":["The pair-runtime C source owns the bounded 196-byte dmConnCb block; this stage adds only its registry linker alias.",
                    "Final RAM placement, startup initialization and hardware behavior remain open."]}
 path=OUT/"receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
 print(receipt["status"],len(before),len(after),sha(path))
if __name__=="__main__":main()
