#!/usr/bin/env python3
"""Build one ARCv2 EM object set for each authenticated QP/C source epoch."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import tarfile
from pathlib import Path
from typing import Sequence

from analyze_em9305_qpc import (
    PORTABLE_SOURCE_FILES,
    SOURCE_EPOCH_TAG_GROUPS,
    STOCK_COMPATIBLE_SOURCE_EPOCH_TAG_GROUPS,
    STOCK_COMPATIBLE_SOURCE_TAGS,
    run_qpc_source_epoch_audit,
)


MODULE_SOURCES = {
    "qf_actq": "src/qf/qf_actq.c",
    "qf_dyn": "src/qf/qf_dyn.c",
    "qf_act": "src/qf/qf_act.c",
    "qep_hsm": "src/qf/qep_hsm.c",
    "qf_mem": "src/qf/qf_mem.c",
    "qk": "src/qk/qk.c",
    "qf_qact": "src/qf/qf_qact.c",
    "qf_qeq": "src/qf/qf_qeq.c",
}
COMMON_FLAGS = (
    "-mcpu=em",
    "-Os",
    "-ffreestanding",
    "-fno-builtin",
    "-fno-common",
    "-ffunction-sections",
    "-fdata-sections",
    "-std=c99",
)


class BuildError(RuntimeError):
    """Raised when the controlled source-epoch build cannot be reproduced."""


def run(*arguments: str | Path, input_bytes: bytes | None = None) -> bytes:
    return subprocess.run(
        [str(argument) for argument in arguments],
        input=input_bytes,
        check=True,
        capture_output=True,
    ).stdout


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def patch_port_configuration(text: str) -> str:
    replacements = {
        "QF_MAX_ACTIVE": 16,
        "QF_MAX_EPOOL": 2,
        "QF_EVENT_SIZ_SIZE": 2,
        "QF_EQUEUE_CTR_SIZE": 1,
        "QF_MPOOL_SIZ_SIZE": 2,
        "QF_MPOOL_CTR_SIZE": 2,
    }
    for macro, value in replacements.items():
        pattern = rf"(^\s*#define\s+{macro}\s+)[0-9]+(?=\s*(?:/\*|$))"
        text, count = re.subn(pattern, rf"\g<1>{value}", text, flags=re.MULTILINE)
        if count != 1:
            raise BuildError(f"expected one {macro} definition, found {count}")
    return text


def normalize_objdump(text: str) -> str:
    lines = []
    for line in text.splitlines():
        if not line or "file format" in line:
            continue
        line = re.sub(r"^[0-9a-f]+ <[^>]+>:$", "<FUNCTION>:", line)
        line = re.sub(r"^\s*[0-9a-f]+:", "ADDR:", line).rstrip()
        lines.append(line)
    return "\n".join(lines) + "\n"


def extract_tag(checkout: Path, tag: str, destination: Path) -> None:
    archive = run("git", "-C", checkout, "archive", "--format=tar", tag)
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as source:
        source.extractall(destination, filter="data")


def build_epoch(
    checkout: Path,
    tag: str,
    destination: Path,
    gcc: Path,
    binutils_dir: Path,
) -> dict[str, object]:
    source_root = destination / "source"
    objects = destination / "objects"
    port = destination / "candidate-port"
    source_root.mkdir(parents=True)
    objects.mkdir()
    port.mkdir()
    extract_tag(checkout, tag, source_root)

    shutil.copy2(source_root / "ports/lint/qep_port.h", port / "qep_port.h")
    shutil.copy2(source_root / "ports/lint/qk/qk_port.h", port / "qk_port.h")
    qf_port = source_root / "ports/lint/qk/qf_port.h"
    (port / "qf_port.h").write_text(
        patch_port_configuration(qf_port.read_text()),
        encoding="utf-8",
    )

    include_flags = (
        f"-I{port}",
        f"-I{source_root / 'include'}",
        f"-I{source_root / 'src'}",
        f"-I{source_root / 'src/qf'}",
        f"-I{source_root / 'src/qk'}",
    )
    assembler_prefix = f"-B{binutils_dir}/"
    objdump = binutils_dir / "objdump"
    module_reports = {}
    for module, relative_source in MODULE_SOURCES.items():
        output = objects / f"{module}.o"
        run(
            gcc,
            assembler_prefix,
            *COMMON_FLAGS,
            *include_flags,
            "-c",
            source_root / relative_source,
            "-o",
            output,
        )
        disassembly = run(objdump, "-dr", "-M", "cpu=em", output).decode()
        normalized = normalize_objdump(disassembly)
        module_reports[module] = {
            "source": relative_source,
            "object_size": output.stat().st_size,
            "object_sha256": sha256(output),
            "normalized_disassembly_sha256": hashlib.sha256(normalized.encode()).hexdigest(),
        }
    return {"tag": tag, "modules": module_reports}


def build_matrix(
    checkout: Path,
    output: Path,
    gcc: Path,
    binutils_dir: Path,
    jobs: int,
    stock_compatible_only: bool = False,
) -> dict[str, object]:
    if output.exists() and any(output.iterdir()):
        raise BuildError(f"output directory is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    source_audit = run_qpc_source_epoch_audit(checkout)
    if jobs < 1:
        raise BuildError("jobs must be positive")
    selected_groups = (
        STOCK_COMPATIBLE_SOURCE_EPOCH_TAG_GROUPS
        if stock_compatible_only else SOURCE_EPOCH_TAG_GROUPS
    )
    representatives = [group[-1] for group in selected_groups]
    with ThreadPoolExecutor(max_workers=min(jobs, len(representatives))) as executor:
        pending = {
            representative: executor.submit(
                build_epoch,
                checkout,
                representative,
                output / representative.replace("+", "_plus"),
                gcc,
                binutils_dir,
            )
            for representative in representatives
        }
        built = {representative: pending[representative].result() for representative in representatives}
    epochs = []
    for group in selected_groups:
        epoch = built[group[-1]]
        epoch["equivalent_source_tags"] = group
        epoch["stock_portable_semantics_compatible"] = any(
            tag in STOCK_COMPATIBLE_SOURCE_TAGS for tag in group
        )
        epochs.append(epoch)
    report = {
        "format": "openCFW.em9305-qpc-arcv2-em-source-epoch-matrix.v1",
        "status": "comparison_only_not_stock_equivalent",
        "source_audit": source_audit,
        "compiler": run(gcc, "--version").decode().splitlines()[0],
        "objdump": run(binutils_dir / "objdump", "--version").decode().splitlines()[0],
        "flags": COMMON_FLAGS,
        "parallel_epoch_jobs": min(jobs, len(representatives)),
        "selection": "stock_compatible_only" if stock_compatible_only else "all_authenticated_epochs",
        "stock_compatible_source_epoch_count": len(STOCK_COMPATIBLE_SOURCE_EPOCH_TAG_GROUPS),
        "portable_sources": PORTABLE_SOURCE_FILES,
        "epochs": epochs,
    }
    (output / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qpc-checkout", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--gcc", type=Path, required=True)
    parser.add_argument(
        "--binutils-dir",
        type=Path,
        required=True,
        help="directory containing ARC objdump and the assembler selected by GCC -B",
    )
    parser.add_argument(
        "--stock-compatible-only",
        action="store_true",
        help="build only the six source epochs surviving stock semantic discriminators",
    )
    parser.add_argument(
        "--jobs",
        type=int,
        default=min(4, len(SOURCE_EPOCH_TAG_GROUPS), os.cpu_count() or 1),
        help="parallel source epochs (default: four or available CPU/epoch count)",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_matrix(
        args.qpc_checkout,
        args.output,
        args.gcc,
        args.binutils_dir,
        args.jobs,
        args.stock_compatible_only,
    )
    print(
        f"QP/C ARCv2 EM epoch matrix: PASS "
        f"({len(report['epochs'])} epochs, {len(MODULE_SOURCES)} modules each)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
