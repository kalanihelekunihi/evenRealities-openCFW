#!/usr/bin/env python3
"""Bounded EM9305 DWARF inventory and v4.2 code compatibility probe.

Outputs names, extents and digests only. It deliberately omits DWARF member
lists and does not copy or export SDK code or type layouts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def exact_code_match(left: bytes, right: bytes) -> bool:
    return len(left) == len(right) and left == right


def elf_text_and_symbols(elf: Path) -> tuple[int, bytes, dict[str, tuple[int, int, str]]]:
    """Prefer section-aware pyelftools reads; no objdump text parsing/truncation."""
    try:
        from elftools.elf.elffile import ELFFile
    except ImportError as exc:
        raise RuntimeError("pyelftools is required for complete ELF section reads; use the configured opencfw venv") from exc
    with elf.open("rb") as stream:
        image = ELFFile(stream)
        section = image.get_section_by_name(".text")
        symtab = image.get_section_by_name(".symtab")
        if section is None or symtab is None:
            raise RuntimeError("ELF lacks .text or .symtab")
        text_index = image.get_section_index(".text")
        symbols = {}
        for sym in symtab.iter_symbols():
            if (sym["st_shndx"] == text_index and sym["st_info"]["type"] == "STT_FUNC"
                    and sym.name and int(sym["st_size"])):
                symbols.setdefault(sym.name, (int(sym["st_value"]), int(sym["st_size"]), ".text"))
        return int(section["sh_addr"]), section.data(), symbols


def stock_functions(symbol_file: Path) -> list[dict[str, object]]:
    funcs = []
    for line in symbol_file.read_text().splitlines()[1:]:
        cols = line.split("\t")
        if len(cols) < 8 or "QPC/lib_QPC.a" not in cols[4] or cols[5] != "Proven" or not cols[3]:
            continue
        start, end = int(cols[0], 16), int(cols[1], 16)
        funcs.append({"name": cols[3], "address": start, "size": end - start,
                      "module": cols[4], "attribution": "historical v4.2 archive attribution"})
    return funcs


def package_records(path: Path) -> list[tuple[int, bytes]]:
    # Import the repository's canonical container parser without writing files.
    parser_path = Path(__file__).resolve().parents[4] / "components/em9305/source_image/record_package.py"
    # The directory layout is fixed from this tool's assigned location.
    if not parser_path.exists():
        parser_path = Path("g2/components/em9305/source_image/record_package.py")
    import importlib.util
    spec = importlib.util.spec_from_file_location("em9305_record_package", parser_path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return [(r.address, r.payload) for r in mod.parse_package(path.read_bytes()).records]


def archive_members(path: Path) -> list[bytes]:
    """Read GNU/BSD ar members into transient memory; never persist SDK objects."""
    data = path.read_bytes()
    if not data.startswith(b"!<arch>\n"):
        raise ValueError(f"not an ar archive: {path}")
    cursor, members, names = 8, [], b""
    while cursor < len(data):
        if cursor + 60 > len(data):
            raise ValueError("truncated ar member header")
        header = data[cursor:cursor + 60]
        if header[58:60] != b"`\n":
            raise ValueError("invalid ar member header")
        name = header[:16].decode("ascii", "replace").strip()
        size = int(header[48:58].decode("ascii").strip())
        cursor += 60
        body = data[cursor:cursor + size]
        if len(body) != size:
            raise ValueError("truncated ar member body")
        cursor += size + (size & 1)
        if name == "//":
            names = body
            continue
        if name in ("/", "/SYM64/"):
            continue
        if name.startswith("#1/"):
            name_len = int(name[3:])
            body = body[name_len:]
        elif name.startswith("/") and name[1:].isdigit() and names:
            start = int(name[1:])
            end = names.find(b"/\n", start)
            if end < 0:
                end = names.find(b"\0", start)
            # Name resolution is used only to identify bookkeeping records;
            # member names are never returned or written to output.
            resolved = names[start:end].decode("ascii", "replace") if end >= 0 else ""
            if resolved == "":
                raise ValueError("unresolvable GNU ar long name")
        members.append(body)
    return members


def archive_inventory(path: Path) -> dict[str, object]:
    members = archive_members(path)
    rows = []
    with tempfile.TemporaryDirectory(prefix="em9305-archive-meta-") as td:
        for index, data in enumerate(members):
            symbols = 0
            if data.startswith(b"\x7fELF"):
                member_path = Path(td) / f"member-{index}.o"
                member_path.write_bytes(data)
                try:
                    symbols = sum(1 for line in run("nm", "-g", str(member_path)).splitlines() if line.strip())
                except subprocess.CalledProcessError:
                    symbols = 0
                finally:
                    member_path.unlink(missing_ok=True)
            rows.append({"ordinal": index, "bytes": len(data), "sha256": sha(data),
                         "elf_object": data.startswith(b"\x7fELF"), "global_symbol_count": symbols})
    return {"archive_sha256": sha(path.read_bytes()), "archive_bytes": path.stat().st_size,
            "member_count": len(rows), "members": rows}


def bytes_at(records: list[tuple[int, bytes]], address: int, size: int) -> bytes | None:
    for base, data in records:
        if base <= address and address + size <= base + len(data):
            return data[address - base:address - base + size]
    return None


def dwarf_types(elf: Path) -> list[dict[str, object]]:
    text = run("dwarfdump", "--debug-info", "--verbose", str(elf))
    # Keep only a curated QP/C interface set. Member names, offsets and type
    # references contribute to a digest in memory but are never serialized.
    selected = {"QActive", "QHsm", "QEQueue", "QTimeEvt", "QMPool",
                "QPSet", "QEvt", "QHsmVtbl", "QActiveVtable", "QF"}
    lines = text.splitlines()
    dies = []
    for i, line in enumerate(lines):
        m = re.match(r"^(\s*)0x([0-9a-fA-F]+):\s+(DW_TAG_[\w]+)", line)
        if not m:
            continue
        indent, offset, tag = len(m.group(1)), int(m.group(2), 16), m.group(3)
        j = i + 1
        while j < len(lines):
            child = re.match(r"^(\s*)0x[0-9a-fA-F]+:\s+DW_TAG_[\w]+", lines[j])
            if child and len(child.group(1)) <= indent:
                break
            j += 1
        dies.append((offset, tag, lines[i:j]))
    output = {}
    member_dies = []
    for offset, tag, block in dies:
        if tag == "DW_TAG_member":
            m = re.search(r"DW_TAG_member[^\n]*\(0x([0-9a-fA-F]+)\)", block[0])
            if m:
                member_dies.append((int(m.group(1), 16), block))
    for offset, tag, block in dies:
        if tag not in ("DW_TAG_structure_type", "DW_TAG_union_type"):
            continue
        joined = "\n".join(block)
        name_m = re.search(r'DW_AT_name[^\n]*= "([^"]+)"', joined)
        if not name_m or name_m.group(1) not in selected:
            continue
        size_m = re.search(r"DW_AT_byte_size[^\n]*\((?:0x([0-9a-fA-F]+)|(\d+))\)", joined)
        size = int(size_m.group(1), 16) if size_m and size_m.group(1) else (int(size_m.group(2)) if size_m else None)
        fields = []
        # Attribute normalization intentionally retains no source paths/lines.
        for parent, item_lines in member_dies:
            if parent != offset:
                continue
            item = "\n".join(item_lines)
            nm = re.search(r'DW_AT_name[^\n]*= "([^"]+)"', item)
            loc = re.search(r"DW_AT_data_member_location[^\n]*\(([^)]*)\)", item)
            # Field type text often embeds compilation-unit DIE offsets. Those
            # are unstable identifiers, so the digest covers the logical field
            # name and location while the total size is recorded separately.
            fields.append((nm.group(1) if nm else "?", loc.group(1).strip() if loc else "?"))
        canonical = json.dumps(fields, separators=(",", ":")).encode()
        entry = {"name": name_m.group(1), "byte_size": size, "member_count": len(fields),
                 "layout_sha256": sha(canonical), "compatibility": "unknown"}
        # Aggregate duplicate DIEs and suppress member details entirely.
        key = (entry["name"], entry["layout_sha256"], size, len(fields))
        output[key] = output.get(key, 0) + 1
    grouped = {}
    for (name, digest, size, count), die_count in output.items():
        grouped.setdefault(name, []).append({"byte_size": size, "member_count": count,
                                             "layout_sha256": digest, "die_count": die_count})
    return [{"name": name, "compatibility": "unknown", "variants": variants}
            for name, variants in sorted(grouped.items())]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--elf", type=Path, required=True, help="authorized local SDK v4.6 debug ELF")
    ap.add_argument("--stock-package", type=Path, required=True, help="locked stock EM9305 package")
    ap.add_argument("--stock-symbols", type=Path, required=True, help="attribution TSV for that firmware")
    ap.add_argument("--archive", type=Path, action="append", default=[], help="optional local SDK ar archive; output is metadata only")
    ap.add_argument("--probe-evidence", type=Path, default=Path("g2/analysis/rescan-2026-10-07/sdk-probe-evidence.json"), help="recorded SDK asset hashes")
    ap.add_argument("--expected-stock-sha256", default="91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9", help="authenticated locked stock package hash")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--limit", type=int, default=10)
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[5]
    evidence = json.loads(args.probe_evidence.read_text())
    elf_sha = sha(args.elf.read_bytes())
    expected_elves = {x["path"]: x["sha256"] for x in evidence.get("em_elf", [])}
    elf_key = next((p for p in expected_elves if (repo_root / p).resolve() == args.elf.resolve()), None)
    if not elf_key or expected_elves[elf_key] != elf_sha:
        raise ValueError("SDK ELF path/hash is not authenticated by sdk-probe-evidence.json")
    stock_sha = sha(args.stock_package.read_bytes())
    if stock_sha != args.expected_stock_sha256:
        raise ValueError("stock package hash does not match the explicit authenticated target hash")
    expected_archive = evidence.get("em_library", {})
    for archive in args.archive:
        if ((repo_root / expected_archive.get("path", "")).resolve() != archive.resolve()
                or expected_archive.get("sha256") != sha(archive.read_bytes())):
            raise ValueError("SDK archive path/hash is not authenticated by sdk-probe-evidence.json")
    text_base, text_bytes, symbols = elf_text_and_symbols(args.elf)
    records = package_records(args.stock_package)
    candidates = [f for f in stock_functions(args.stock_symbols) if int(f["size"]) >= 20]
    results = []
    mutation_controls = []
    for f in candidates:
        name, addr, size = str(f["name"]), int(f["address"]), int(f["size"])
        sym = symbols.get(name)
        status, reason, digest46, digest42 = "unknown", "no same-named v4.6 code symbol", None, None
        if sym and sym[2] == ".text" and sym[1] > 0:
            vma, vsize, _ = sym
            s = vma - text_base
            b46 = text_bytes[s:s + vsize] if s >= 0 else b""
            b42 = bytes_at(records, addr, size)
            if len(b46) == vsize and b42 is not None:
                digest46, digest42 = sha(b46), sha(b42)
                if exact_code_match(b46, b42):
                    status, reason = "validated_exact_code", "same function name, extent and bytes in locked stock package"
                    mutated = bytearray(b42)
                    mutated[0] ^= 1
                    if exact_code_match(b46, bytes(mutated)):
                        raise AssertionError("one-byte mutation did not invalidate exact code match")
                    mutation_controls.append(name)
                else:
                    status, reason = "changed", "function name matches; extent or bytes differ"
            else:
                status, reason = "unknown", "one or both function extents are unavailable in executable records"
        results.append({"name": name, "stock_address": f"0x{addr:08x}", "stock_size": size,
                        "v46_address": f"0x{sym[0]:08x}" if sym else None,
                        "v46_size": sym[1] if sym else None, "status": status,
                        "reason": reason, "v46_sha256": digest46, "stock_sha256": digest42,
                        "stock_attribution": f["attribution"], "stock_module": f["module"]})
        if len(results) >= args.limit:
            break

    args.out.mkdir(parents=True, exist_ok=True)
    report = {
        "schema": "em9305-shortcut-report-v1",
        "sdk_elf": str(args.elf), "sdk_elf_sha256": elf_sha, "sdk_elf_hash_authenticated_by": str(args.probe_evidence),
        "stock_package": str(args.stock_package), "stock_package_sha256": stock_sha,
        "stock_package_hash_authenticated_by": ("g2/blobs/official/g2-2.2.6.10/PROVENANCE.md"
                                                if args.expected_stock_sha256 == "91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9"
                                                else "caller-supplied expected hash"),
        "stock_symbols": str(args.stock_symbols),
        "method": "DWARF-enabled v4.6 ELF symbol extents compared against the locked v4.2 firmware package; names/extent/digests only",
        "function_fixtures": results,
        "negative_control": {"one_byte_mutation_rejected": mutation_controls,
                             "passed": bool(mutation_controls)},
        "type_fixtures": dwarf_types(args.elf),
        "archives": [{"path": str(p), **archive_inventory(p)} for p in args.archive],
        "type_compatibility_rule": "unknown unless an independently established stock-v4.2 layout proof exists; this run does not infer compatibility from v4.6 DWARF alone",
        "limitations": ["v4.6 FPGA/debug ELF is not the stock product image", "historical v4.2 attribution is archive evidence, not v4.6 source identity", "no MetaWare compiler is used or available for source rebuild comparison"],
    }
    (args.out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    counts = {s: sum(1 for r in results if r["status"] == s) for s in ("validated_exact_code", "changed", "unknown")}
    print(json.dumps({"functions_tested": len(results), "statuses": counts,
                      "types_inventoried": len(report["type_fixtures"]), "report": str(args.out / "report.json")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
