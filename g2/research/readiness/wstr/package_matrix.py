#!/usr/bin/env python3
import csv
import hashlib
import pathlib
import shutil
import subprocess
import sys

root=pathlib.Path(sys.argv[1]).resolve(); out=root/"out"; artifact=root/"artifact"
if artifact.exists(): shutil.rmtree(artifact)
artifact.mkdir()

def sha(path): return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
def blob(path):
    data=pathlib.Path(path).read_bytes(); return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()

source=root/"AmbiqSuite-R2.5.1/third_party/cordio/wsf/sources/util/wstr.c"
header=root/"AmbiqSuite-R2.5.1/third_party/cordio/wsf/sources/util/wstr.h"
with open(artifact/"source-identities.tsv","w",newline="") as f:
    writer=csv.writer(f,delimiter="\t",lineterminator="\n");writer.writerow(("identity","path_or_release","bytes","sha256","git_blob_sha1","commit_or_tree","qualification"))
    writer.writerow(("ambiq_source","AmbiqSuite-R2.5.1/third_party/cordio/wsf/sources/util/wstr.c",source.stat().st_size,sha(source),blob(source),"archive 87b03680c0ac5a5291938e7c522f86146a954d935588f1deb046f35012fe4133","authenticated proprietary wrapper; excluded"))
    writer.writerow(("ambiq_header","AmbiqSuite-R2.5.1/third_party/cordio/wsf/sources/util/wstr.h",header.stat().st_size,sha(header),blob(header),"archive 87b03680c0ac5a5291938e7c522f86146a954d935588f1deb046f35012fe4133","authenticated proprietary wrapper; excluded"))
    writer.writerow(("public_source","Packetcraft Cordio wsf/sources/util/wstr.c",5049,"70ccac28b66c3337ff78acf3a857f821d578016cef04d72e818ec64e34f2559a","581cf30505aa65b690e558628ea2647b12d1cab0","commit 86372d84ef0386d8834ed036e613c8f2ded1ff16; tree b398806b4472aa738b6bfd771b583ad2e9fd179f; util tree d9b548ca795a3f80654d77635d0282ea531fabe7","official Apache-2.0 r19.02 route; first three function bodies exact"))
    writer.writerow(("body","WStrReverseCpy",152,"52fc33c9ca8b1c3220ff8179c985a46e9b3a190fbe6605e7eb4b549bd2fabb49","","same in Ambiq and Packetcraft r19.02","exact textual body including signature"))
    writer.writerow(("body","WStrReverse",177,"306939ddef49a0a9228611548ff21b5cf41ca9cb89fc3b3caf58627cbdfd8f0e","","same in Ambiq and Packetcraft r19.02","exact textual body including signature"))

dep=(out/"deps/wstr.d").read_text().replace("\\\n"," "); names=list(dict.fromkeys(dep.split(":",1)[1].split()))
with open(artifact/"include-closure.tsv","w",newline="") as f:
    writer=csv.writer(f,delimiter="\t",lineterminator="\n");writer.writerow(("class","path","bytes","sha256"))
    for name in names:
        if name.startswith("/usr/lib/gcc/"): writer.writerow(("compiler_builtin",name,"","pinned by container identity")); continue
        path=root/name; writer.writerow(("cleanroom_shim" if name.startswith("shim/") else "ambiqsuite_2.5.1_archive",name,path.stat().st_size,sha(path)))

callers={
"WStrReverseCpy":[0x5363BE,0x5363C8,0x5366F0,0x5366FE,0x53672A,0x5367A8,0x5367B4,0x56D022,0x56D034,0x56D088,0x56D0DC,0x56D130,0x5E26B2,0x5E26C4,0x5E26E4,0x5E26F6,0x5E2736,0x5E2748,0x5E2768,0x5E277A,0x5E2B80,0x5E2B90,0x5E2FF8,0x5E34DE,0x5E351C,0x5E359A,0x5E35AA,0x5E35FA,0x5E3652,0x5E37A4,0x5E37CC,0x5E3DB8,0x5E3DC8,0x5E3E66,0x5E3EA8,0x5E3F58,0x5E401A,0x5E40FA,0x5E4138],
"WStrReverse":[0x534D8A,0x5362AA],
}
with open(artifact/"stock-callers.tsv","w",newline="") as f:
    writer=csv.writer(f,delimiter="\t",lineterminator="\n");writer.writerow(("function","direct_bl_callers","caller_addresses","stored_entry_pointers"))
    for name,addresses in callers.items(): writer.writerow((name,len(addresses),";".join(f"0x{x:08X}" for x in addresses),0))

for name in ("comparison-ledger.tsv","config-summary.tsv","best-size-per-function.tsv","build-results.tsv","matrix-timing.txt","dependency-timing.txt","toolchain.txt","source-api-build-sizes.tsv"):
    shutil.copy2(out/name,artifact/name)
for name in ("functions.tsv","closure_root.c","normalize_disassembly.py","run_matrix.py","package_matrix.py"):
    shutil.copy2(root/"input"/name,artifact/name)
shutil.copy2(root/"shim/string.h",artifact/"string.h")

rows=list(csv.DictReader(open(out/"comparison-ledger.tsv"),delimiter="\t"))
with open(artifact/"stock-functions.tsv","w",newline="") as f:
    fields=("function","start","end","stock_size","stock_sha256","stock_normalized_sha256","evidence");writer=csv.DictWriter(f,fields,delimiter="\t",lineterminator="\n");writer.writeheader();seen=set()
    for row in rows:
        if row["function"] not in seen: seen.add(row["function"]);writer.writerow({field:row[field] for field in fields})
with open(artifact/"provider-closure.tsv","w",newline="") as f:
    writer=csv.writer(f,delimiter="\t",lineterminator="\n");writer.writerow(("profile","module_undefined","linked_undefined","status"))
    for row in csv.DictReader(open(out/"build-results.tsv"),delimiter="\t"): writer.writerow((row["config"],row["module_undefined"],row["linked_undefined"],"closed" if row["linked_undefined"]=="0" else "open"))

build=list(csv.DictReader(open(out/"build-results.tsv"),delimiter="\t"));summary=list(csv.DictReader(open(out/"config-summary.tsv"),delimiter="\t"));best=min(summary,key=lambda row:(int(row["aggregate_abs_size_delta"]),-int(row["exact_size"])))
elapsed=int((out/"matrix-timing.txt").read_text().split("=",1)[1]);compile_total=sum(int(row["compile_ns"]) for row in build);link_total=sum(int(row["link_ns"]) for row in build)
(artifact/"README.txt").write_text(f'''OpenCFW Lorelei Cordio wstr.c bounded structural matrix

Scope and provenance
--------------------
Only proven-linked WStrReverseCpy and WStrReverse are compared. AmbiqSuite 2.5.1 wstr.c is authenticated by SHA-256 7b226d9ebdbab4d305da843c4fd865c64f408f4376551499f94fcd0451dd6452. Their textual bodies are exact in official Apache-2.0 Packetcraft Cordio r19.02 commit 86372d84ef0386d8834ed036e613c8f2ded1ff16, supplying a license-safe source route. WstrnCpy compiles and its section size is inventoried, but it is excluded from comparison and address assignment because independent stock evidence is absent.

Stock closure
-------------
WStrReverseCpy [0x0056D8C4,0x0056D8F0) is 44 bytes, SHA-256 249d9f2b812108c61c554f67936ae7cd01ac1029b475f21deb49f55cf27e6b94, with 39 direct BL callers and no stored entry pointer. WStrReverse [0x0056D8F0,0x0056D93A) is 74 bytes, SHA-256 dd319dbd967e39a1da26a2e1393cc42aed30fcc0a96b4e43c326490b801e20a7, with two callers and no stored entry pointer. They are contiguous in exact source order.

Matrix
------
Thirteen established GCC profiles x two functions produced {len(rows)} rows in {elapsed} ns. Summed compile time was {compile_total} ns and link time {link_total} ns. Every closure link has zero undefined symbols. Best aggregate lane is {best['lane']}, absolute size delta {best['aggregate_abs_size_delta']} bytes with {best['exact_size']}/2 exact-size functions. Raw matches total {sum(row['raw_match']=='yes' for row in rows)}; strict normalized matches total {sum(row['strict_normalized_match']=='yes' for row in rows)}.

Artifact policy
---------------
Proprietary Ambiq source, stock firmware/function bytes, objects, linked ELFs, and disassembly are excluded. The artifact retains identities, exact public commit/tree/blob route, clean-room closure input, flags, full comparison/build ledgers, caller closure, timing, and checksums.
''')
sumfile=artifact/"SHA256SUMS";sumfile.write_text("\n".join(f"{sha(path)}  {path.name}" for path in sorted(p for p in artifact.iterdir() if p.is_file() and p!=sumfile))+"\n")
tar=root/"wstr-readiness-matrix-artifact.tar.gz";subprocess.run(["tar","--sort=name","--mtime=@0","--owner=0","--group=0","--numeric-owner","-czf",str(tar),"-C",str(root),"artifact"],check=True);(root/"wstr-readiness-matrix-artifact.tar.gz.sha256").write_text(f"{sha(tar)}  {tar.name}\n")
print("tar_sha256",sha(tar),"tar_bytes",tar.stat().st_size,"elapsed",elapsed,"compile_total",compile_total,"link_total",link_total,"best",best["lane"],best["aggregate_abs_size_delta"])
for name in ("comparison-ledger.tsv","config-summary.tsv","best-size-per-function.tsv","include-closure.tsv","source-api-build-sizes.tsv","provider-closure.tsv","source-identities.tsv","stock-callers.tsv"): print(name,sha(artifact/name))
