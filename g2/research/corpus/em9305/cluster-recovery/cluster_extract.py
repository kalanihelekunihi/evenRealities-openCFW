#!/usr/bin/env python3
"""Extract authenticated SDK object disassemblies for EM9305 cluster recovery.

Runs on lorelei.  Authenticates the ISO controller archive and the
whole-application objdump, extracts the seven candidate objects, disassembles
every function label (global and static) with GNU ARC binutils in ARCv2 EM
mode, records compiler-comment anchors, and emits a deterministic JSON plus
SHA256SUMS ledger.  All boundary/alignment decisions are made locally by the
repository analyzer; this script only exports deterministic facts.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ARCHIVE = Path("/var/tmp/opencfw-em9305-residual-preflight.tDJNgX/lib_emb_controller_iso.a")
ARCHIVE_SHA256 = "87af23b9b6a582137a02759c4af2344f7160a8b88197dd540ef8268aa55f6cfa"
ARCHIVE_GIT_BLOB = "b9433012b264da2210f602395b144a6d21795f01"
BIN = Path("/var/tmp/opencfw-arc-binutils/root/usr/bin")
APP_OBJDUMP = Path("application-objdump.txt")
APP_OBJDUMP_SHA256 = "13d1e9c7c0d2c2d3db9436d21ec6d90a39622446cb8ab96de5c2c01ba752916f"

OBJECTS = (
    "lctr_isr_conn_slave.c.obj",
    "lctr_main_conn_slave.c.obj",
    "lctr_sm_conn_slave.c.obj",
    "lctr_isr_adv_master_ae.c.obj",
    "lctr_main_adv_master_ae.c.obj",
    "lctr_isr_adv_central_pawr.c.obj",
    "lctr_main_adv_central_pawr.c.obj",
)

COMPILER_COMMENT_ANCHORS = (
    "LLVM 14.0.6/T-2022.09. (build 004)",
    "(EM-Micro)",
    "-arcv2em",
    "-Os",
)

FUNCTION_LABEL = re.compile(r"^\s*([0-9a-f]+)\s+<([^>]+)>:\s*$")
LINE_RE = re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2,8}\s+)+)\s*(\S+)(.*)$")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw).stdout


def main() -> int:
    out = Path("output")
    out.mkdir(exist_ok=False)
    archive_bytes = ARCHIVE.resolve().read_bytes()
    if sha256(archive_bytes) != ARCHIVE_SHA256:
        raise SystemExit("ISO controller archive identity mismatch")
    app_objdump = APP_OBJDUMP.resolve().read_bytes()
    if sha256(app_objdump) != APP_OBJDUMP_SHA256:
        raise SystemExit("whole-application objdump identity mismatch")
    for tool in ("ar", "objdump", "readelf"):
        if not (BIN / f"arc-linux-gnu-{tool}").is_file():
            raise SystemExit(f"missing ARC binutils tool: {tool}")

    work = Path("objects")
    work.mkdir(exist_ok=False)
    run((str(BIN / "arc-linux-gnu-ar"), "x", str(ARCHIVE.resolve())), cwd=work)

    objects = {}
    ledger = {}
    comments = set()
    for name in OBJECTS:
        path = work / name
        if not path.is_file():
            raise SystemExit(f"candidate object missing from archive: {name}")
        obj_bytes = path.read_bytes()
        text = run((str(BIN / "arc-linux-gnu-objdump"), "-d", "-M", "cpu=em", str(path)))
        comment = run((str(BIN / "arc-linux-gnu-readelf"), "-p", ".comment", str(path)))
        comments.add(comment.strip())
        # split into per-function instruction streams in object order
        functions = []
        current = None
        for line in text.splitlines():
            label = FUNCTION_LABEL.match(line)
            if label:
                if current is not None:
                    functions.append(current)
                current = {"name": label.group(2), "offset": int(label.group(1), 16),
                           "instructions": []}
                continue
            m = LINE_RE.match(line)
            if m and current is not None:
                current["instructions"].append(
                    {"address": int(m.group(1), 16), "mnemonic": m.group(3),
                     "operands": m.group(4).strip()}
                )
        if current is not None:
            functions.append(current)
        functions = [f for f in functions if f["instructions"]]
        if not functions:
            raise SystemExit(f"no functions decoded in {name}")
        objects[name] = {
            "object": name,
            "object_sha256": sha256(obj_bytes),
            "object_size": len(obj_bytes),
            "disassembly_sha256": sha256(text.encode()),
            "functions": functions,
        }
        ledger[name] = sha256(obj_bytes)

    comments_text = "\n".join(sorted(comments))
    for anchor in COMPILER_COMMENT_ANCHORS:
        if anchor not in comments_text:
            raise SystemExit(f"compiler comment anchor missing: {anchor}")

    report = {
        "identity": {
            "archive_path": str(ARCHIVE),
            "archive_sha256": ARCHIVE_SHA256,
            "archive_git_blob": ARCHIVE_GIT_BLOB,
            "application_objdump_sha256": APP_OBJDUMP_SHA256,
            "binutils_objdump": str(BIN / "arc-linux-gnu-objdump"),
            "binutils_objdump_sha256": sha256((BIN / "arc-linux-gnu-objdump").read_bytes()),
            "compiler_comment_anchors": list(COMPILER_COMMENT_ANCHORS),
        },
        "objects": objects,
    }
    (out / "cluster-objects.json").write_text(
        json.dumps(report, indent=1, sort_keys=True) + "\n"
    )
    sums = []
    for path in sorted(out.rglob("*")):
        if path.is_file():
            sums.append(f"{sha256(path.read_bytes())}  {path.relative_to(out)}")
    (out / "SHA256SUMS").write_text("\n".join(sums) + "\n")
    print(json.dumps({
        "objects": {name: len(entry["functions"]) for name, entry in objects.items()},
        "report_sha256": sha256((out / "cluster-objects.json").read_bytes()),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
