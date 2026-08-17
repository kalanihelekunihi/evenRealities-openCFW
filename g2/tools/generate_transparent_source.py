#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Generate a transparent C codebase from the merged G2 function database.

Every byte of the Apollo main image becomes a declared, human-readable source
artifact:

  * a code region becomes a C translation unit -- the recovered decompilation
    where one exists, and an explicit ``OPENG2_UNRECOVERED`` trap where the
    corpus establishes no behavior;
  * a data region becomes a provenanced byte array with its classification and
    hash recorded alongside it.

Nothing is copied forward as an unexplained blob.  What the generator cannot
justify it marks, rather than quietly emitting vendor bytes.

Each function is compiled as its own translation unit against declarations
derived from its own body, so decompiler type disagreements between functions
cannot cascade.  A unit that fails to compile keeps its source in tree -- it is
still evidence -- but contributes a trap to the image instead of code.

Usage:
    tools/generate_transparent_source.py --output build/transparent/source
    tools/generate_transparent_source.py --output ... --compile --jobs 8
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNTIME_HEADER = REPO_ROOT / "tools/transparent/openg2_decompiled_runtime.h"
DEFAULT_DB = REPO_ROOT / "build/transparent"
DEFAULT_BUNDLES = REPO_ROOT / "research/corpus/apollo-main/ghidra/decomp/bundles"

#: Functions are grouped into shard directories so no single directory holds
#: several thousand files.
SHARD_SIZE = 256

BUNDLE_HEADER = re.compile(
    r"^/\* FUN 0x([0-9a-fA-F]+) (\S+) bytes=(\d+) sha256=(\S*) \*/$"
)

#: Symbols Ghidra invents and never defines.
SYMBOL_PATTERN = re.compile(
    r"\b((?:thunk_)?FUN_[0-9a-fA-F]{6,8}"
    r"|SUB_[0-9a-fA-F]{6,8}"
    r"|_?_?DAT_[0-9a-fA-F]{6,8}"
    r"|PTR_[A-Za-z0-9_]*[0-9a-fA-F]{6,8}"
    r"|UNK_[0-9a-fA-F]{6,8}"
    r"|(?:s|u|e|a)_[A-Za-z0-9_]*_[0-9a-fA-F]{6,8}"
    r"|stack0x[0-9a-fA-F]+)\b"
)

#: A Ghidra prototype, split so the return type can be reused with an
#: unprototyped parameter list.
SIGNATURE_PATTERN = re.compile(r"^(.*?)\b([A-Za-z_][A-Za-z0-9_]*)\s*\(")

LABEL_PATTERN = re.compile(r"\b((?:LAB|code|joined|switchD|caseD)_[0-9a-zA-Z_]+)\b")

#: Names the runtime header already provides; never re-declare them.
RUNTIME_PROVIDED = {
    "halt_baddata", "switchD", "memcpy", "memmove", "memset", "memcmp",
    "strlen", "strcpy", "strcmp", "openg2_unrecovered",
}

COMPILE_FLAGS = [
    "--target=armv8.1m.main-none-eabi",
    "-mcpu=cortex-m55",
    "-mthumb",
    "-mfloat-abi=soft",
    "-std=gnu11",
    "-Oz",
    "-ffreestanding",
    "-fno-builtin",
    "-ffunction-sections",
    "-fdata-sections",
    "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables",
    # Decompiler output is type-loose by nature.  Clang promotes several of
    # these to errors by default, which -Wno-everything does not undo, so the
    # ones that recovered code legitimately trips are named explicitly.
    "-Wno-everything",
    "-Wno-int-conversion",
    "-Wno-incompatible-pointer-types",
    "-Wno-incompatible-function-pointer-types",
    "-Wno-implicit-function-declaration",
    "-Wno-implicit-int",
    "-Wno-return-type",
]


class GenerateError(RuntimeError):
    pass


def load_bundles(bundle_dir: Path) -> dict[int, str]:
    """Split the harvested decompilation bundles back into function bodies."""
    if not bundle_dir.is_dir():
        raise GenerateError(f"no decompilation bundles at {bundle_dir}")
    bodies: dict[int, str] = {}
    for path in sorted(bundle_dir.glob("*.c")):
        current: int | None = None
        collected: list[str] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            match = BUNDLE_HEADER.match(line)
            if match:
                if current is not None:
                    bodies[current] = "\n".join(collected).strip("\n")
                current = int(match.group(1), 16)
                collected = []
                continue
            if current is not None:
                collected.append(line)
        if current is not None:
            bodies[current] = "\n".join(collected).strip("\n")
    return bodies


#: Ghidra encodes the address in the symbol name; split labels may carry a
#: trailing disambiguator (``LAB_0046ee70_1``).
TRAILING_ADDRESS = re.compile(r"_([0-9a-fA-F]{6,8})(?:_\d+)?$")


def declaration_for(symbol: str, body: str, signatures: dict[str, str]) -> str:
    """Choose a declaration for an undefined symbol from how this unit uses it."""
    if symbol.startswith(("FUN_", "thunk_FUN_", "SUB_")):
        # Ghidra's recorded prototype and its individual call sites routinely
        # disagree on arity: the same callee is analyzed independently at each
        # site.  Keep the recovered return type -- callers assign from it --
        # but leave the parameter list unprototyped so a disagreement between
        # two analyses of the same callee cannot fail the unit.
        signature = signatures.get(symbol)
        return_type = None
        if signature:
            match = SIGNATURE_PATTERN.match(signature.strip())
            if match and match.group(2) == symbol:
                return_type = match.group(1).strip()
        # A callee recorded as returning nothing is still assigned from at some
        # call sites: Ghidra analyzes callers independently of callees.  The
        # widest common recovery is a machine word.
        if not return_type or return_type == "void":
            return_type = "undefined4"
        return f"{return_type} {symbol}();"

    escaped = re.escape(symbol)
    # Ghidra names a data symbol after the address it lives at, so the symbol
    # can be resolved here rather than left as an undefined extern.  That keeps
    # each unit self-contained: only calls need relocating later.
    address_match = TRAILING_ADDRESS.search(symbol)
    if not address_match:
        return f"extern undefined4 {symbol};"
    address = f"0x{int(address_match.group(1), 16):08X}u"

    # The declaration form follows this unit's own use of the symbol.
    if re.search(rf"\(\s*\*\s*{escaped}\s*\)\s*\(", body):
        return f"#define {symbol} (*(code **){address})"
    if re.search(rf"(?<![\w.>]){escaped}\s*\(", body):
        return f"#define {symbol} (*(code *){address})"
    if re.search(rf"\b{escaped}\s*\[", body):
        return f"#define {symbol} ((undefined4 *){address})"
    if re.search(rf"(?<![\w>])\*\s*{escaped}\b", body) or re.search(
        rf"\b{escaped}\s*->", body
    ):
        return f"#define {symbol} (*(undefined4 **){address})"
    return f"#define {symbol} (*(undefined4 *){address})"


def missing_labels(body: str) -> set[str]:
    """Labels a body jumps to but never defines (a broken recovered flow)."""
    targets = set()
    for match in re.finditer(r"goto\s+([A-Za-z_][A-Za-z0-9_]*)\s*;", body):
        targets.add(match.group(1))
    defined = set()
    for match in re.finditer(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:(?!:)", body, re.M):
        defined.add(match.group(1))
    return targets - defined


def render_unit(
    record: dict[str, Any],
    body: str | None,
    signatures: dict[str, str],
) -> tuple[str, str]:
    """Return (source text, disposition) for one function."""
    entry = record["entry"]
    name = record.get("name") or record.get("ghidra_name") or f"FUN_{entry:08x}"
    header_lines = [
        "/* SPDX-License-Identifier: GPL-3.0-only",
        " *",
        f" * 0x{entry:08X}  {name}",
        f" *   size        {record.get('size')} bytes"
        f" (covered {record.get('covered_bytes')})",
        f" *   evidence    tier={record['tier']}"
        f" sources={','.join(record.get('sources', []))}",
    ]
    if record.get("bucket"):
        header_lines.append(
            f" *   provider    {record['bucket']}"
            f" (census confidence {record.get('census_confidence')})"
        )
    if record.get("families"):
        header_lines.append(f" *   families    {','.join(record['families'])}")
    if record.get("candidate_symbol"):
        header_lines.append(f" *   candidate   {record['candidate_symbol']}")
    if record.get("body_sha256"):
        header_lines.append(f" *   stock bytes sha256:{record['body_sha256']}")
    header_lines.append(
        " *"
    )
    header_lines.append(
        " * Generated by tools/generate_transparent_source.py from the harvested"
    )
    header_lines.append(
        " * Ghidra corpus.  Recovered structure, not reviewed behavior."
    )
    header_lines.append(" */")
    header = "\n".join(header_lines)

    prologue = f'{header}\n\n#include "openg2_decompiled_runtime.h"\n'

    if body is None:
        trap = (
            f"\n/* No decompilation exists for this address in the corpus. */\n"
            f"void {name}(void)\n{{\n"
            f"    OPENG2_UNRECOVERED(0x{entry:08X}u);\n}}\n"
        )
        return prologue + trap, "trap-no-decompilation"

    unresolved = missing_labels(body)
    if unresolved:
        trap = (
            f"\n/* Recovered control flow leaves "
            f"{', '.join(sorted(unresolved))} undefined; the decompilation is\n"
            f" * kept below for review but cannot stand in for the stock code. */\n"
            f"void {name}(void)\n{{\n"
            f"    OPENG2_UNRECOVERED(0x{entry:08X}u);\n}}\n\n"
            "#if 0\n" + body + "\n#endif\n"
        )
        return prologue + trap, "trap-unresolved-flow"

    referenced: set[str] = set()
    for match in SYMBOL_PATTERN.finditer(body):
        referenced.add(match.group(1))

    # A code label this unit references but does not define is an address in
    # another function -- typically taken with `&` and handed to a helper.  It
    # resolves to its own address, same as a data symbol.
    defined_labels = {
        match.group(1)
        for match in re.finditer(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:(?!:)", body, re.M)
    }
    for match in LABEL_PATTERN.finditer(body):
        label = match.group(1)
        if label not in defined_labels and TRAILING_ADDRESS.search(label):
            referenced.add(label)

    referenced -= RUNTIME_PROVIDED
    referenced.discard(name)
    referenced.discard(record.get("ghidra_name") or "")

    declarations = sorted(
        declaration_for(symbol, body, signatures) for symbol in referenced
    )
    declaration_block = ""
    if declarations:
        declaration_block = (
            "\n/* Referenced by this unit; declared from its own usage. */\n"
            + "\n".join(declarations)
            + "\n"
        )

    return prologue + declaration_block + "\n" + body + "\n", "decompiled"


#: Roughly how many bytes of image data go into one generated data unit.
DATA_SHARD_BYTES = 64 * 1024


def emit_data_sources(
    data_regions: list[dict[str, Any]],
    image_meta: dict[str, Any],
    output_dir: Path,
) -> None:
    """Write every non-code region out as a declared, provenanced C array.

    These bytes are vendor-derived: fonts, bitmaps, tables and string pools
    cannot be reconstructed from a decompiler.  Emitting them as source does
    not make them recovered -- it makes them *visible and editable*, with the
    address, classification and hash of each region stated next to it, instead
    of an unexplained span inside a binary.
    """
    blob = REPO_ROOT / image_meta["path"]
    image = blob.read_bytes()
    load_base = image_meta["load_base"]

    data_root = output_dir / "data"
    data_root.mkdir(parents=True, exist_ok=True)

    index: list[dict[str, Any]] = []
    shard_index = 0
    shard_bytes = 0
    chunks: list[str] = []

    def flush() -> None:
        nonlocal shard_bytes, chunks, shard_index
        if not chunks:
            return
        path = data_root / f"data-shard-{shard_index:03d}.c"
        path.write_text(
            "/* SPDX-License-Identifier: GPL-3.0-only\n"
            " *\n"
            " * Non-code regions of the Apollo main image, emitted as source.\n"
            " * Generated by tools/generate_transparent_source.py -- do not edit;\n"
            " * edit the region map and regenerate.\n"
            " *\n"
            " * These are vendor-derived bytes rendered as declared data, not\n"
            " * reconstructed content.  Each array states where it belongs, what\n"
            " * the classifier made of it, and the hash it must reproduce.\n"
            " */\n\n"
            + "\n".join(chunks),
            encoding="utf-8",
        )
        shard_index += 1
        shard_bytes = 0
        chunks = []

    for region in data_regions:
        start = region["start"]
        size = region["size"]
        offset = start - load_base
        data = image[offset:offset + size]
        symbol = f"openg2_data_{start:08x}"
        rows = []
        for position in range(0, len(data), 16):
            row = ", ".join(f"0x{byte:02X}" for byte in data[position:position + 16])
            rows.append(f"    {row},")
        chunks.append(
            f"/* 0x{start:08X}..0x{region['end']:08X}  {region['classification']}\n"
            f" *   {size} bytes  sha256:{region['sha256']} */\n"
            f"const unsigned char {symbol}[{size}] = {{\n"
            + "\n".join(rows)
            + "\n};\n"
        )
        index.append({
            "symbol": symbol,
            "start": start,
            "end": region["end"],
            "size": size,
            "classification": region["classification"],
            "sha256": region["sha256"],
            "shard": shard_index,
        })
        shard_bytes += size
        if shard_bytes >= DATA_SHARD_BYTES:
            flush()
    flush()

    (data_root / "data-index.json").write_text(
        json.dumps({"schema_version": 1, "regions": index}, indent=1, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )


def compile_unit(
    clang: str, source: Path, object_path: Path, include_dir: Path
) -> tuple[bool, str]:
    completed = subprocess.run(
        [
            clang,
            *COMPILE_FLAGS,
            "-I",
            str(include_dir),
            "-c",
            str(source),
            "-o",
            str(object_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.returncode == 0, completed.stderr


def classify_error(stderr: str) -> str:
    for line in stderr.splitlines():
        marker = next(
            (token for token in (": error: ", ": fatal error: ") if token in line),
            None,
        )
        if marker is None:
            continue
        message = line.split(marker, 1)[1]
        message = re.sub(r"'[^']*'", "'X'", message)
        return message.strip()[:120]
    return "unknown"


def generate(
    database_dir: Path,
    bundle_dir: Path,
    output_dir: Path,
    clang: str | None,
    jobs: int,
) -> dict[str, Any]:
    database = json.loads((database_dir / "function-db.json").read_text(encoding="utf-8"))
    regions = json.loads((database_dir / "region-map.json").read_text(encoding="utf-8"))
    bodies = load_bundles(bundle_dir)

    signatures = {
        record["ghidra_name"]: record["signature"]
        for record in database["functions"]
        if record.get("ghidra_name") and record.get("signature")
    }

    if output_dir.exists():
        shutil.rmtree(output_dir)
    code_root = output_dir / "code"
    code_root.mkdir(parents=True)
    shutil.copy2(RUNTIME_HEADER, output_dir / RUNTIME_HEADER.name)

    units: list[dict[str, Any]] = []
    dispositions: Counter[str] = Counter()
    for index, record in enumerate(database["functions"]):
        entry = record["entry"]
        body = bodies.get(entry)
        text, disposition = render_unit(record, body, signatures)
        shard = f"shard-{index // SHARD_SIZE:03d}"
        shard_dir = code_root / shard
        shard_dir.mkdir(exist_ok=True)
        source_path = shard_dir / f"fn_{entry:08x}.c"
        source_path.write_text(text, encoding="utf-8")
        dispositions[disposition] += 1
        units.append({
            "entry": entry,
            "name": record.get("name") or record.get("ghidra_name"),
            "tier": record["tier"],
            "size": record.get("size"),
            "covered_bytes": record.get("covered_bytes"),
            "source": str(source_path.relative_to(output_dir)),
            "disposition": disposition,
        })

    data_regions = [
        region for region in regions["regions"] if region["kind"] != "function"
    ]
    emit_data_sources(data_regions, database["image"], output_dir)

    manifest = {
        "schema_version": 1,
        "generator": "tools/generate_transparent_source.py",
        "image": database["image"],
        "units": units,
        "data_regions": data_regions,
        "dispositions": dict(sorted(dispositions.items())),
    }

    compile_report: dict[str, Any] = {}
    if clang:
        object_root = output_dir / "objects"
        object_root.mkdir(parents=True, exist_ok=True)
        compilable = [unit for unit in units if unit["disposition"] != "trap-no-decompilation"]
        results: list[tuple[dict[str, Any], bool, str]] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
            futures = {}
            for unit in compilable:
                source = output_dir / unit["source"]
                object_path = object_root / f"{Path(unit['source']).stem}.o"
                futures[
                    pool.submit(compile_unit, clang, source, object_path, output_dir)
                ] = (unit, object_path)
            for future in concurrent.futures.as_completed(futures):
                unit, object_path = futures[future]
                ok, stderr = future.result()
                unit["compiled"] = ok
                if ok:
                    unit["object"] = str(object_path.relative_to(output_dir))
                results.append((unit, ok, stderr))

        failures = Counter()
        for unit, ok, stderr in results:
            if not ok:
                failures[classify_error(stderr)] += 1
        compiled_count = sum(1 for _, ok, _ in results if ok)
        compile_report = {
            "attempted": len(results),
            "compiled": compiled_count,
            "failed": len(results) - compiled_count,
            "compiled_bytes": sum(
                unit["covered_bytes"] or 0 for unit, ok, _ in results if ok
            ),
            "top_failures": dict(failures.most_common(25)),
        }
        manifest["compile"] = compile_report

    (output_dir / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=1, sort_keys=True) + "\n", encoding="utf-8"
    )

    summary = {
        "units": len(units),
        "dispositions": dict(sorted(dispositions.items())),
        "data_regions": len(data_regions),
        "data_bytes": sum(region["size"] for region in data_regions),
    }
    if compile_report:
        summary["compile"] = compile_report
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=DEFAULT_DB)
    parser.add_argument("--bundles", type=Path, default=DEFAULT_BUNDLES)
    parser.add_argument("--output", type=Path, default=DEFAULT_DB / "source")
    parser.add_argument("--compile", action="store_true")
    parser.add_argument("--clang", default="/usr/bin/clang")
    parser.add_argument("--jobs", type=int, default=8)
    args = parser.parse_args(argv)

    try:
        summary = generate(
            args.database.resolve(),
            args.bundles.resolve(),
            args.output.resolve(),
            args.clang if args.compile else None,
            args.jobs,
        )
    except GenerateError as failure:
        print(f"error: {failure}", file=sys.stderr)
        return 2

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
