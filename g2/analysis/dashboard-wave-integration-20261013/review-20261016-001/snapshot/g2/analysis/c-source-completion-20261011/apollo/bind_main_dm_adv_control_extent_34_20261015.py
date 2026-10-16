#!/usr/bin/env python3
"""Verify the current Main replay already owns the stock-evidenced 0x34 DM advertising cell."""
import hashlib,json,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2"
SOURCE=G2/"components/audio/master_dispatch_candidate_20261014/dm_adv_control_state.c"
EVIDENCE=G2/"build/c-firmware/20261014/main-dm-adv-control-state/receipt.json"
PAYLOAD=G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE=G2/"build/c-firmware/20261015/main-dm-adv-config-lower-4b9a80/apollo-main-dm-adv-config-lower-4b9a80.o"
OUT=G2/"build/c-firmware/20261015/main-dm-adv-control-extent-34"
NAME="audio_ble_dm_adv_control"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def symbols(p,flag):
 return {line.split()[-1] for line in subprocess.check_output(["arm-none-eabi-nm","-g",flag,str(p)],text=True).splitlines()}
def size(p):
 rows=[line.split() for line in subprocess.check_output(["arm-none-eabi-nm","-g","-S",str(p)],text=True).splitlines() if line.endswith(" "+NAME)]
 if len(rows)!=1:raise RuntimeError("advertising control symbol missing/duplicate")
 return int(rows[0][1],16)
def refs(p):
 return sum(NAME in line for line in subprocess.check_output(["arm-none-eabi-readelf","-r","--wide",str(p)],text=True).splitlines())
def main():
 blob=PAYLOAD.read_bytes()[32:]
 if hashlib.sha256(blob).hexdigest()!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701" or \
    blob[0x4ba0da-0x438000:0x4ba0de-0x438000]!=bytes.fromhex("20890884") or \
    blob[0x4b313e-0x438000:0x4b3158-0x438000]!=bytes.fromhex("90f831008df80900e4b20620444301eb040010f125010df10a00"):
  raise RuntimeError("native advertising extent changed")
 evidence=json.loads(EVIDENCE.read_text())
 if evidence["status"]!="PASS_EXPERIMENTAL_MAIN_DM_ADV_CONTROL_STATE_C" or evidence["source_sha256"]!=sha(SOURCE):
  raise RuntimeError("C-owned advertising extent evidence changed")
 if size(BASE)!=0x34 or refs(BASE)!=24:
  raise RuntimeError("current Main lacks 0x34 advertising cell or its 24 relocations")
 OUT.mkdir(parents=True,exist_ok=True)
 linked=OUT/"apollo-main-dm-adv-control-extent-34.o"
 shutil.copyfile(BASE,linked)
 if sha(linked)!=sha(BASE) or symbols(linked,"-u")!=symbols(BASE,"-u"):
  raise RuntimeError("advertising extent identity changed")
 receipt={"status":"PASS_EXPERIMENTAL_MAIN_DM_ADV_CONTROL_ALREADY_C_OWNED",
          "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
          "evidence":str(EVIDENCE.relative_to(ROOT)),"evidence_sha256":sha(EVIDENCE),
          "payload_sha256":hashlib.sha256(blob).hexdigest(),
          "native_duration_write":"0x4ba0da..0x4ba0de","native_peer_read":"0x4b313e..0x4b3158",
          "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
          "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
          "source_owned_symbols":[],"old_size":0x34,"new_size":0x34,
          "relocations_verified":refs(linked),"unresolved_before":len(symbols(BASE,"-u")),
          "unresolved_after":len(symbols(linked,"-u")),"imports_resolved":[],"imports_added":[],
          "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
          "limits":["The C-owned 0x34 advertising cell was integrated upstream; this stage verifies its retained relocations.",
                    "Final RAM placement and whole-image startup remain open."]}
 path=OUT/"receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
 print(receipt["status"],refs(linked),sha(path))
if __name__=="__main__":main()
