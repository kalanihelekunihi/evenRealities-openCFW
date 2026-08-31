#!/usr/bin/env python3
"""Target-compile and relocatably link the EM9305 QP/C software component."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
QPC = ROOT / "third_party/qpc"
PORT = ROOT / "components/shared/em9305/qpc_port"
QPC_SOURCES = (
    "src/qf/qep_hsm.c",
    "src/qf/qf_act.c",
    "src/qf/qf_actq.c",
    "src/qf/qf_dyn.c",
    "src/qf/qf_mem.c",
    "src/qf/qf_qact.c",
    "src/qf/qf_qeq.c",
    "src/qk/qk.c",
)
PORT_SOURCES = (
    "components/shared/em9305/qpc_port/runtime_arc_gcc_helpers.c",
    "components/shared/em9305/qpc_port/runtime_qpc_port.c",
)
FLAGS = (
    "-mcpu=em", "-std=gnu99", "-Os", "-ffreestanding", "-fno-builtin",
    "-fno-common", "-ffunction-sections", "-fdata-sections", "-Wall",
    "-Wextra", "-Werror", "-Wno-array-bounds",
)
FORBIDDEN_IMPORTS = frozenset({
    "memcpy", "memmove", "memset", "__mulsi3", "__divsi3", "__udivsi3",
    "__modsi3", "__umodsi3", "__divdi3", "__udivdi3", "__moddi3",
    "__umoddi3",
})
HARDWARE_VALIDATION = "blocked by unavailable physical evidence"


class BuildError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def report_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def run(command: list[str]) -> str:
    completed = subprocess.run(
        command, cwd=ROOT, check=False, capture_output=True, text=True,
    )
    if completed.returncode != 0:
        raise BuildError(
            f"command failed ({completed.returncode}): {' '.join(command)}\n"
            f"{completed.stdout}{completed.stderr}"
        )
    return completed.stdout


def undefined_symbols(nm: str, path: Path) -> list[str]:
    symbols = []
    for line in run([nm, "-u", str(path)]).splitlines():
        fields = line.split()
        if fields:
            symbols.append(fields[-1])
    return sorted(set(symbols))


def build(
    gcc: str,
    ld: str,
    ar: str,
    nm: str,
    readelf: str,
    output_dir: Path,
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    includes = (
        f"-I{QPC / 'ports/em9305'}",
        f"-I{QPC / 'include'}",
        f"-I{QPC / 'src'}",
        f"-I{PORT}",
    )
    source_paths = tuple(QPC / relative for relative in QPC_SOURCES) + tuple(
        ROOT / relative for relative in PORT_SOURCES
    )

    with tempfile.TemporaryDirectory(prefix="opencfw-em9305-qpc-") as temporary:
        staging = Path(temporary)
        objects: list[Path] = []
        records = []
        for index, source in enumerate(source_paths):
            if not source.is_file():
                raise BuildError(f"missing QP/C component source: {source}")
            output = staging / f"{index:02d}-{source.stem}.o"
            run([gcc, *FLAGS, *includes, "-c", str(source), "-o", str(output)])
            objects.append(output)
            records.append({
                "source": str(source.relative_to(ROOT)),
                "source_size": source.stat().st_size,
                "source_sha256": sha256(source),
                "object_size": output.stat().st_size,
                "object_sha256": sha256(output),
                "undefined_symbols_before_link": undefined_symbols(nm, output),
            })

        linked_staging = staging / "em9305-qpc-component.o"
        archive_staging = staging / "libem9305-qpc-component.a"
        run([ld, "-r", *(str(path) for path in objects), "-o", str(linked_staging)])
        run([ar, "rcD", str(archive_staging), *(str(path) for path in objects)])

        unresolved = undefined_symbols(nm, linked_staging)
        forbidden = sorted(set(unresolved) & FORBIDDEN_IMPORTS)
        if unresolved:
            raise BuildError(f"linked QP/C component has undefined symbols: {unresolved}")
        if forbidden:
            raise BuildError(f"linked QP/C component has runtime imports: {forbidden}")
        header = run([readelf, "-h", str(linked_staging)])
        if "ARC" not in header or "REL (Relocatable file)" not in header:
            raise BuildError("linked QP/C component is not a relocatable ARC ELF")

        linked = output_dir / linked_staging.name
        archive = output_dir / archive_staging.name
        shutil.copyfile(linked_staging, linked)
        shutil.copyfile(archive_staging, archive)

    return {
        "schema_version": 1,
        "status": "arcv2-em-qpc-component-target-linked",
        "target": "ARCv2 EM",
        "compiler": run([gcc, "--version"]).splitlines()[0],
        "flags": list(FLAGS),
        "translation_units": records,
        "translation_unit_count": len(records),
        "qpc_translation_unit_count": len(QPC_SOURCES),
        "port_translation_unit_count": len(PORT_SOURCES),
        "linked_object": {
            "path": report_path(linked),
            "size": linked.stat().st_size,
            "sha256": sha256(linked),
            "undefined_symbols": [],
            "forbidden_runtime_imports": [],
        },
        "archive": {
            "path": report_path(archive),
            "size": archive.stat().st_size,
            "sha256": sha256(archive),
            "deterministic_mode": "ar rcD",
        },
        "software_link_complete": True,
        "install_placement_resolved": False,
        "production_routed": False,
        "required_hardware_providers": [
            "critical_entry", "critical_exit", "interrupt_disable",
            "interrupt_enable", "isr_context", "PalUartResume",
            "VoltMon_DoMeasurement",
        ],
        "hardware_operations": [],
        "hardware_validation": HARDWARE_VALIDATION,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gcc", default=os.environ.get("OPENCFW_ARC_GCC", "arc-linux-gnu-gcc"))
    parser.add_argument("--ld", default=os.environ.get("OPENCFW_ARC_LD", "arc-linux-gnu-ld"))
    parser.add_argument("--ar", default=os.environ.get("OPENCFW_ARC_AR", "arc-linux-gnu-ar"))
    parser.add_argument("--nm", default=os.environ.get("OPENCFW_ARC_NM", "arc-linux-gnu-nm"))
    parser.add_argument("--readelf", default=os.environ.get("OPENCFW_ARC_READELF", "arc-linux-gnu-readelf"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--write-summary", type=Path)
    args = parser.parse_args()
    report = build(
        args.gcc, args.ld, args.ar, args.nm, args.readelf,
        args.output_dir.resolve(),
    )
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.write_summary is not None:
        args.write_summary.resolve().write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BuildError as error:
        raise SystemExit(f"EM9305 QP/C component build failed: {error}") from error
