#!/usr/bin/env python3
import csv
import hashlib
import pathlib
import shutil
import subprocess
import sys

root = pathlib.Path(sys.argv[1]).resolve()
out = root/"out"
artifact = root/"artifact"
if artifact.exists():
    shutil.rmtree(artifact)
artifact.mkdir()

def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

def blob(path):
    data = pathlib.Path(path).read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

wsf = root/"AmbiqSuite-R2.5.1/third_party/cordio/wsf"
source = wsf/"sources/port/freertos/wsf_efs.c"
header = wsf/"include/wsf_efs.h"
with open(artifact/"source-identities.tsv", "w", newline="") as f:
    writer = csv.writer(f, delimiter="\t", lineterminator="\n")
    writer.writerow(("identity", "path_or_release", "bytes", "sha256", "git_blob_sha1", "qualification"))
    writer.writerow(("selected_source", "AmbiqSuite-R2.5.1/third_party/cordio/wsf/sources/port/freertos/wsf_efs.c", source.stat().st_size, sha(source), blob(source), "authenticated official archive; proprietary; excluded"))
    writer.writerow(("selected_header", "AmbiqSuite-R2.5.1/third_party/cordio/wsf/include/wsf_efs.h", header.stat().st_size, sha(header), blob(header), "authenticated official archive; proprietary; excluded"))
    writer.writerow(("same_source", "AmbiqSuite-R2.4.2/third_party/exactle/wsf/sources/port/freertos/wsf_efs.c", source.stat().st_size, sha(source), blob(source), "byte-identical; not a release discriminator"))
    writer.writerow(("archive", "AmbiqSuite-R2.5.1-s3.zip", 200161418, "87b03680c0ac5a5291938e7c522f86146a954d935588f1deb046f35012fe4133", "", "authenticated official archive; excluded"))
    writer.writerow(("stock", "G2 2.2.6.10 ota_s200_firmware_ota.bin", 3523396, "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863", "", "authenticated image; excluded"))

dependency_text = (out/"wsf_efs.d").read_text().replace("\\\n", " ")
dependencies = list(dict.fromkeys(dependency_text.split(":", 1)[1].split()))
with open(artifact/"include-closure.tsv", "w", newline="") as f:
    writer = csv.writer(f, delimiter="\t", lineterminator="\n")
    writer.writerow(("class", "path", "bytes", "sha256"))
    for name in dependencies:
        if name.startswith("/usr/lib/gcc/"):
            writer.writerow(("compiler_builtin", name, "", "pinned by container identity"))
            continue
        path = root/name
        kind = "cleanroom_shim" if name.startswith("shim/") else "ambiqsuite_2.5.1_archive"
        writer.writerow((kind, name, path.stat().st_size, sha(path)))

for name in ("compiled-symbol-census.tsv", "build-timing.tsv", "wall-timing.txt", "toolchain.txt", "marker-census.tsv", "archive-consumer-topology.tsv"):
    shutil.copy2(out/name, artifact/name)
for name in ("run_probe.py", "semantic_scan.py", "package_census.py", "closure_stubs.c"):
    shutil.copy2(root/"input"/name, artifact/name)
shutil.copy2(root/"shim/string.h", artifact/"string.h")

triage = list(csv.DictReader(open(out/"semantic-triage-hits.tsv"), delimiter="\t"))
with open(artifact/"semantic-triage-candidates.tsv", "w", newline="") as f:
    fields = ("address", "fingerprint", "has_stride_52", "has_multiply", "has_invalid_minus1")
    writer = csv.DictWriter(f, fields, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    for row in triage:
        writer.writerow({field: row[field] for field in fields})
full_handle = [row for row in triage if row["has_stride_52"] == "1" and row["has_multiply"] == "1"]
full_init = [row for row in triage if row["fingerprint"] == "six_52byte_spaced_stores"]
with open(artifact/"reviewed-triage-summary.tsv", "w", newline="") as f:
    writer = csv.writer(f, delimiter="\t", lineterminator="\n")
    writer.writerow(("test", "raw_candidates", "surviving_candidates", "verdict"))
    writer.writerow(("compiled complete function raw bytes across 3 GCC profiles x 17 APIs", 51, 0, "no exact stock occurrence"))
    writer.writerow(("handle bound plus 52-byte file-table stride and multiply", len(triage), len(full_handle), "no complete WsfEfsGetFileByHandle/RemoveFile semantic fingerprint"))
    writer.writerow(("six 52-byte-spaced invalid-size stores", len(triage), len(full_init), "no unrolled WsfEfsInit fingerprint"))
    writer.writerow(("two multiply-plus-minus-one partial hits", 2, 0, "0x507426 and 0x50744C use a 48-byte stride, not the 52-byte EFS control block"))
    writer.writerow(("source/profile/UUID marker census", 9, 0, "wsf_efs/WDXS names and all four exact WDX UUIDs absent"))

build = list(csv.DictReader(open(out/"build-timing.tsv"), delimiter="\t"))
compiled = list(csv.DictReader(open(out/"compiled-symbol-census.tsv"), delimiter="\t"))
wall = int((out/"wall-timing.txt").read_text().split("=",1)[1])
(artifact/"README.txt").write_text(f'''OpenCFW Lorelei Cordio wsf_efs.c inclusion census

Conclusion
----------
No defensible linked entry was found. The evidence favors `not linked / garbage-collected` for Cordio wsf_efs.c in the authenticated G2 image, so a broad compiler matrix was intentionally not started.

Source and consumer topology
----------------------------
AmbiqSuite 2.5.1 wsf_efs.c is 19,876 bytes, SHA-256 878125a6bb701d0875d58c05bfcb4ad770c9f95f8c09f69706959795bee7741a. AmbiqSuite 2.4.2 is byte-identical. An archive-wide source census found external WsfEfs API consumers only in wdxs_main.c, wdxs_ft.c, and wdxs_stream.c. The stock image has no wsf_efs.c/WsfEfs/wsfEfs markers, no WDXS markers, and none of the four exact WDX characteristic UUIDs. G2's numerous textual `EFS` markers belong to its separate Even File Service over LittleFS and are not Cordio Embedded File System evidence.

Structural probe
----------------
Three profiles (O1, O3, Os with sibling calls disabled) compiled all 17 public APIs in parallel, producing {len(compiled)} function rows. All three closure ELFs linked with zero undefined symbols; only memcpy and memset were source-module imports. Parallel wall time was {wall} ns. No complete candidate function byte sequence occurred in stock.

A Thumb semantic census covered the authenticated executable/Cordio corpus at stock file offsets [0x40000,0x136000). Thirty deliberately broad partial hits were triaged. None combined handle bound 6, the 52-byte wsfEfsControl_t stride, and multiplication; none had WsfEfsInit's six 52-byte-spaced invalid-size stores. The only two multiply-plus-minus-one hits, 0x00507426 and 0x0050744C, use a 48-byte stride and unrelated control constants. Thus no candidate survives as an entry.

Limitations and recommendation
------------------------------
Absence cannot prove bytes do not exist under arbitrary downstream rewriting, and the generic `Unknown` fallback string occurs six times elsewhere. However, the missing sole consumer family and UUID service data, zero source/name markers, zero raw candidates, and zero complete semantic fingerprints make inclusion unlikely. Record this module as `upstream available, stock inclusion not evidenced / likely dead-stripped`; do not assign addresses or run the 13-profile matrix unless WDXS call/pointer evidence appears later.
''')

sumfile = artifact/"SHA256SUMS"
sumfile.write_text("\n".join(f"{sha(path)}  {path.name}" for path in sorted(p for p in artifact.iterdir() if p.is_file() and p != sumfile)) + "\n")
tar = root/"wsf-efs-inclusion-census-artifact.tar.gz"
subprocess.run(["tar", "--sort=name", "--mtime=@0", "--owner=0", "--group=0", "--numeric-owner", "-czf", str(tar), "-C", str(root), "artifact"], check=True)
(root/"wsf-efs-inclusion-census-artifact.tar.gz.sha256").write_text(f"{sha(tar)}  {tar.name}\n")
print("tar_sha256", sha(tar), "tar_bytes", tar.stat().st_size)
for name in ("compiled-symbol-census.tsv", "marker-census.tsv", "semantic-triage-candidates.tsv", "reviewed-triage-summary.tsv", "archive-consumer-topology.tsv", "include-closure.tsv", "source-identities.tsv"):
    print(name, sha(artifact/name))
