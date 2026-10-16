#!/usr/bin/env python3
"""Replace only the stock-proven 104-byte settings RAM member in corrected Main archive."""
import hashlib,json,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2"
OLD=G2/"build/c-firmware/20261014/main-input-archive-member-refresh"
AUDIO=OLD/"libaudio-input-corrected.a"
BASE=OLD/"candidate-input-corrected.o"
MAIN=G2/"build/c-firmware/20261014/main-root-refresh/apollo_main/main/main-candidates.a"
MANIFEST=G2/"build/c-firmware/20261014/main-root-source-refresh2/apollo_main/audio/compile-results.json"
SOURCE=G2/"components/audio/uart_thread_source_candidate/settings_live_buffers.c"
EVIDENCE=G2/"build/c-firmware/settings-live-buffers-round1007/receipt.json"
OUT=G2/"build/c-firmware/20261016/main-settings-ram-archive-refresh"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def names(p,*args):
 return {line.split()[-1] for line in subprocess.check_output(["arm-none-eabi-nm",*args,str(p)],text=True).splitlines() if line.strip()}
def size(p,name):
 rows=[line.split() for line in subprocess.check_output(["arm-none-eabi-nm","-S",str(p)],text=True).splitlines() if line.endswith(" "+name)]
 if len(rows)!=1:raise RuntimeError("settings symbol missing/duplicate")
 return int(rows[0][1],16)
def main():
 evidence=json.loads(EVIDENCE.read_text())
 if evidence["status"]!="PASS_SETTINGS_LIVE_BUFFER_MINIMA_BINDING" or evidence["source_sha256"]!=sha(SOURCE):
  raise RuntimeError("settings source evidence changed")
 if size(BASE,"audio_settings_last_message_state")!=13:
  raise RuntimeError("corrected Main base no longer has prior 13-byte span")
 OUT.mkdir(parents=True,exist_ok=True)
 rows={str((ROOT/r["source"]).resolve()):r for r in json.loads(MANIFEST.read_text())["rows"]}
 row=rows[str(SOURCE.resolve())]
 member=Path(row["object_path"]).name
 old_members=subprocess.check_output(["arm-none-eabi-ar","t",str(AUDIO)],text=True).splitlines()
 if old_members.count(member)!=1:raise RuntimeError("settings archive member missing/duplicate")
 obj=OUT/member;command=list(row["command"])
 command[command.index("-MF")+1]=str(OUT/(member+".d"))
 command[command.index("-o")+1]=str(obj)
 subprocess.run(command,check=True)
 if size(obj,"audio_settings_last_message_state")!=104:
  raise RuntimeError("refreshed settings object lacks 104-byte span")
 archive=OUT/"libaudio-input-settings-ram-corrected.a"
 shutil.copyfile(AUDIO,archive)
 subprocess.run(["arm-none-eabi-ar","rcsD",str(archive),str(obj)],check=True)
 if subprocess.check_output(["arm-none-eabi-ar","t",str(archive)],text=True).splitlines()!=old_members:
  raise RuntimeError("archive member order changed")
 linked=OUT/"candidate-input-settings-ram-corrected.o"
 subprocess.run(["arm-none-eabi-ld","-r","--whole-archive",str(archive),str(MAIN),
                 "--no-whole-archive","-o",str(linked)],check=True)
 if names(BASE,"-u")!=names(linked,"-u") or names(BASE,"-g","--defined-only")!=names(linked,"-g","--defined-only"):
  raise RuntimeError("archive provider/import sets changed")
 if size(linked,"audio_settings_last_message_state")!=104:
  raise RuntimeError("linked corrected Main lacks 104-byte settings RAM span")
 receipt={"status":"PASS_EXPERIMENTAL_MAIN_SETTINGS_RAM_ARCHIVE_REFRESH_C",
          "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
          "evidence":str(EVIDENCE.relative_to(ROOT)),"evidence_sha256":sha(EVIDENCE),
          "prior_archive":str(AUDIO.relative_to(ROOT)),"prior_archive_sha256":sha(AUDIO),
          "prior_object":str(BASE.relative_to(ROOT)),"prior_object_sha256":sha(BASE),
          "compile_manifest":str(MANIFEST.relative_to(ROOT)),"compile_manifest_sha256":sha(MANIFEST),
          "member":member,"object":str(obj.relative_to(ROOT)),"object_sha256":sha(obj),
          "command":command,"archive":str(archive.relative_to(ROOT)),"archive_sha256":sha(archive),
          "linked_object":str(linked.relative_to(ROOT)),"linked_object_sha256":sha(linked),
          "archive_members":len(old_members),"provider_set_preserved":True,
          "import_set_preserved":True,"prior_bytes":13,"refreshed_bytes":104,
          "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
          "limits":["Only the settings RAM archive member was refreshed; replay of downstream Main stages, final RAM layout and hardware behavior remain open."]}
 path=OUT/"receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
 print(receipt["status"],len(old_members),size(linked,"audio_settings_last_message_state"),sha(path))
if __name__=="__main__":main()
