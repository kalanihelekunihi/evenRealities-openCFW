#!/usr/bin/env python3
"""Verify and compile the bounded QP/C 6.5.1 EM9305 source snapshot."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
FILES = {
    "LICENSE": "3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986",
    "include/qassert.h": "dbd2a14e09e36ecbaaa74deee76d17dedbc770350a24ff7927aa8447987d0c54",
    "include/qep.h": "cdfb4eb5b8eefac500de5fa6c495c2bb82de7198791a92e45a51bd63a4849a4e",
    "include/qequeue.h": "71cdaa5b5ee6689e19bc0bff08ddd687a05e50dc689a09c3230d98f00f4678b3",
    "include/qf.h": "4fcf41e59b9eef6e9d80d19b9607475fa64ff37661de231d39a53abbcc85fc4d",
    "include/qk.h": "e2698fc122de900cb6bec40b66c91a1afac5d04d734e731707f3c932a37e8b33",
    "include/qmpool.h": "7bb443825008e3c9706497c87aa044bc3ab25b203a080207db7ff63072a3fbea",
    "include/qpc.h": "8bb42b22ee8671238f6f99cb2ef1cb2a3ed79a38ceabc79d1c6ac796d32a399a",
    "include/qpset.h": "d0be48d45c905639cbd1d942473d06c2c42ac980c3b2da1f4c441d2c5bfcde54",
    "include/qs.h": "5c4ad275a59a8c1086d410a799ef0cece740684ff07fbf1c06be39e868e0a66d",
    "include/qs_dummy.h": "20aaff74d036862f5c6d9e837cf1c7a396cac51859548c82e6b375d34f140b08",
    "include/qv.h": "8ada11a26c4008604a725e63c4ccca1f6970bd021c06b9430ec0ba213d6b1808",
    "include/qxk.h": "60eabeba02217a9ed2f137124ddb60b7157304e7865457a496e6d3aa9bfd0884",
    "include/qxthread.h": "a7b3fa05a2d565b4860d8602f79618a1cfd3996e59bf413ee89b9be90e109df9",
    "include/stdint_c.h": "7b16ade5d0ae2cdd2d3acc4b97f6bfe3938840b25e317c3ce5b56cfc3b842c91",
    "ports/em9305/qep_port.h": "f65441ffda6182085287d593a6a1820ab8d5bca4f88ff04ca7ad398476197c41",
    "ports/em9305/qf_port.h": "4cab803a0c0a5e83189bad5a8745a6320f7331f68ac723ff6be794c9bb7811e5",
    "ports/em9305/qk_port.h": "8837dd1f7c4295162ac4556f317dae5d7867b1d0b3cd3a8744f9d99d5de96645",
    "src/qf/qep_hsm.c": "aa5eba0513db3dc6ba134329f73620540c5e9157f7f0687314925d1abf135d3b",
    "src/qf/qf_act.c": "2c38d958b2a50029ac5000f6f636e5b244778f6138a93c873140b2d0e012f6e2",
    "src/qf/qf_actq.c": "a1cd93ab313c3a00237be6947be68ab35ab02a2cc53fe52047a328e29d916cbb",
    "src/qf/qf_dyn.c": "568523fcd3927eff0d6407deca20b3b1465020b423b8c179936aa7b051ef790b",
    "src/qf/qf_mem.c": "0bd3bf03b04f7007063d4c9b054ea36b8382600f1196a56afc7cf5c0e7807f48",
    "src/qf/qf_qact.c": "5f2e2e455cd44d44cf7b07f488ce7af27998a552424b8fba391556452c90886c",
    "src/qf/qf_qeq.c": "861ef89f8cdb5025fda5dde3f36d090ef50094864a39b13611dd62655f02be10",
    "src/qf_pkg.h": "fdc1f772969b36e67ac1413733a65733eb6b78df7ef7a5c446833f4695f6f08f",
    "src/qk/qk.c": "f1b069a535260c1a23d66d3dfe3373259b5068fc94bccef078bd55bf2bdfed0a",
}
SOURCES = (
    "src/qf/qep_hsm.c", "src/qf/qf_act.c", "src/qf/qf_actq.c",
    "src/qf/qf_dyn.c", "src/qf/qf_mem.c", "src/qf/qf_qact.c",
    "src/qf/qf_qeq.c", "src/qk/qk.c",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compile_sources(compiler: str, arc: bool = False) -> None:
    flags = ["-std=gnu99", "-Os", "-ffreestanding", "-fno-builtin", "-fno-common", "-ffunction-sections", "-fdata-sections"]
    if arc:
        flags.insert(0, "-mcpu=em")
    else:
        flags += ["-Wall", "-Wextra", "-Werror"]
    includes = ["-I" + str(ROOT / "ports/em9305"), "-I" + str(ROOT / "include"), "-I" + str(ROOT / "src")]
    with tempfile.TemporaryDirectory(prefix="opencfw-qpc-") as directory:
        for relative in SOURCES:
            output = Path(directory) / (Path(relative).stem + ".o")
            subprocess.run([compiler, *flags, *includes, "-c", str(ROOT / relative), "-o", str(output)], check=True, capture_output=True)


def verify() -> dict:
    actual = {path.relative_to(ROOT).as_posix() for path in ROOT.rglob("*") if path.is_file() and "__pycache__" not in path.parts and path.name not in {"README.openCFW.md", "PROVENANCE.json", "verify_snapshot.py"}}
    if actual != set(FILES):
        raise SystemExit("QP/C snapshot file inventory changed")
    for relative, expected in FILES.items():
        if sha(ROOT / relative) != expected:
            raise SystemExit(f"QP/C snapshot hash changed: {relative}")
    provenance = json.loads((ROOT / "PROVENANCE.json").read_text())
    if provenance.get("commit") != "416dcec8820b9cdb5827497e645d0d9375db53c6" or provenance.get("version") != "6.5.1":
        raise SystemExit("QP/C provenance changed")
    qep = (ROOT / "include/qep.h").read_text()
    if '#define QP_VERSION      651U' not in qep or '#define QP_VERSION_STR  "6.5.1"' not in qep or '#define QP_RELEASE      0x8E7055B4U' not in qep:
        raise SystemExit("QP/C release macros changed")
    for relative in SOURCES:
        source = (ROOT / relative).read_text()
        if "GNU General Public License" not in source or "version 3" not in source:
            raise SystemExit(f"QP/C license notice missing: {relative}")
    license_text = (ROOT / "LICENSE").read_text()
    if (
        "GNU GENERAL PUBLIC LICENSE\n                       Version 3, 29 June 2007" not in license_text
        or "Everyone is permitted to copy and distribute verbatim copies" not in license_text
        or "END OF TERMS AND CONDITIONS" not in license_text
    ):
        raise SystemExit("QP/C GPL-3.0 license text changed")
    port = (ROOT / "ports/em9305/qf_port.h").read_text()
    for fact in ("QF_MAX_ACTIVE 16", "QF_MAX_EPOOL 2", "QF_MAX_TICK_RATE 0", "QF_EQUEUE_CTR_SIZE 1", "QF_MPOOL_SIZ_SIZE 2", "QF_MPOOL_CTR_SIZE 2"):
        if fact not in port:
            raise SystemExit(f"QP/C EM9305 port configuration changed: {fact}")
    compile_sources("/usr/bin/clang")
    arc_compiler = os.environ.get("OPENCFW_ARC_GCC") or shutil.which("arc-elf32-gcc")
    target = "blocked_unavailable_reviewed_arc_compiler"
    if arc_compiler:
        compile_sources(arc_compiler, arc=True)
        target = "arc_objects_compiled_not_integrated"
    return {"files": len(FILES), "portable_sources": len(SOURCES), "version": "6.5.1", "host_compile": "pass", "arc_target": target, "production_routed": False}


if __name__ == "__main__":
    result = verify()
    print(json.dumps(result, indent=2, sort_keys=True))
    print("QP/C 6.5.1 EM9305 source snapshot: PASS")
