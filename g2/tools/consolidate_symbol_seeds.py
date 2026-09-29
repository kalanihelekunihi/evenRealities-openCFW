#!/usr/bin/env python3
"""Consolidate legacy G2 function-naming evidence into per-payload symbol seeds.

The legacy G2 manifests, research reports and corpus files record function
boundaries and names in many different table shapes. This tool reads them,
normalizes every row to one schema, attributes it to a firmware payload,
deduplicates by start address, and writes one address-sorted TSV per payload
plus a conflicts table.

The output is a naming seed for pseudocode review. It is not reviewed
pseudocode, it is not a source-ownership claim, and nothing in it proves byte
equality.

Usage:
    python3 consolidate_symbol_seeds.py --repo /path/to/evenRealities-openCFW \
        --out /path/to/output/symbols

Output is deterministic: rows are sorted, inputs are enumerated in sorted
order, and no timestamps are written.
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

csv.field_size_limit(sys.maxsize)

# --------------------------------------------------------------------------
# Payload geometry (s200_v2.2.6.10). Sources: g2/manifests/g2-2.2.6.10.json,
# g2/docs/memory-map.md, touch relocation note, codec section maps.
# --------------------------------------------------------------------------
PAYLOAD_RANGES = [
    # name, start, end_exclusive
    ("ble_em9305", 0x00300000, 0x00335BC8),   # records 0..3; app 0x302400 + 210,888
    ("bootloader", 0x00410000, 0x00434477),   # 148,599-byte bootloader image
    ("apollo_main", 0x00438000, 0x00794324),  # 3,523,364-byte application at run base
    ("case", 0x08000000, 0x0800D9C8),         # 55,752-byte STM32G0 application
]
PAYLOADS = ["apollo_main", "bootloader", "ble_em9305", "codec", "touch", "case"]

TOUCH_LINK_BASE = 0x3300          # touch payload offset 0 is linked at flash 0x3300
TOUCH_PAYLOAD_SIZE = 34432

# Codec FWPK package-offset windows -> (region label, runtime base, package base).
CODEC_MAIN = 0x958C  # main_image package offset (external SPI NOR offset 0)
CODEC_WINDOWS = [
    # package start, package end, region, runtime base address for package start
    (0x00050, 0x02850, "uart_boot_stage1", 0x10000000),
    (0x02850, 0x0958C, "uart_boot_stage2", 0x10002800),
    (CODEC_MAIN + 0x00000, CODEC_MAIN + 0x03000, "image_a_stage1", None),
    (CODEC_MAIN + 0x03004, CODEC_MAIN + 0x0BE88, "image_a_xip", 0x10203004),
    (CODEC_MAIN + 0x0BE88, CODEC_MAIN + 0x0F804, "image_a_sram", 0x10023400),
    (CODEC_MAIN + 0x2F3B0, CODEC_MAIN + 0x323B0, "image_b_stage1", None),
    (CODEC_MAIN + 0x323B4, CODEC_MAIN + 0x46440, "image_b_sram", 0x10003000),
]

CONFIDENCE_RANK = {"Proven": 4, "Strong": 3, "Inferred": 2, "Unverified": 1}

PLACEHOLDER_RE = re.compile(
    r"^(?:FUN|SUB|LAB|thunk_FUN|sub|touch_sub|case_sub)_[0-9A-Fa-f]+$"
)
IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.$@]*$")
HEX_RE = re.compile(r"^\s*0x([0-9A-Fa-f]+)\s*$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")

NAME_KEYS = ["stock_name", "function", "name", "symbol", "admitted_symbol",
             "evidence_name", "proposed_name"]
START_KEYS = ["stock_start", "entry", "start", "stock_address", "body_start",
              "start_or_entry", "stock_entry", "body_entry"]
END_KEYS = ["stock_end_exclusive", "end_exclusive", "body_end_exclusive",
            "end", "end-exclusive"]
SIZE_KEYS = ["stock_bytes", "size", "bytes", "interval_bytes", "envelope_bytes",
             "instruction_bytes"]
SHA_KEYS = ["stock_sha256", "sha256", "interval_sha256", "body_sha256",
            "instruction_sha256"]
CONF_KEYS = ["naming_confidence", "name_confidence", "identification", "identity",
             "confidence", "name_status", "classification", "stock_status",
             "status", "disposition", "mapping_origin", "readiness", "recovery",
             "ownership_category", "source_status", "provenance"]
NOTE_KEYS = ["evidence", "qualification", "entry_evidence", "recovery_evidence",
             "behavior", "provenance", "detail", "role", "assessment", "reason",
             "contract", "notes", "action", "ownership_category", "bucket",
             "family", "kind"]
MODULE_KEYS = ["source_path_anchor", "path_anchor", "retained_path", "source_file",
               "module", "object", "source", "family_hint", "attribution",
               "provider_family", "subsystem", "concrete_source", "source_or_provider",
               "owner_or_contract", "ownership_category", "bucket", "family"]
NON_MODULE_VALUES = {"", "-", "yes", "no", "true", "false", "none", "n/a"}


def clean(text) -> str:
    if text is None:
        return ""
    return re.sub(r"\s+", " ", str(text)).strip()


def parse_hex(value) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    m = HEX_RE.match(str(value))
    return int(m.group(1), 16) if m else None


def parse_int(value) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    v = str(value).strip()
    if re.fullmatch(r"\d+", v):
        return int(v)
    return parse_hex(v)


def neutral_name(name: str) -> str:
    """Strip the project's descriptive-name prefix; keep upstream names intact."""
    name = clean(name)
    for prefix in ("open_cfw_", "opencfw_"):
        if name.startswith(prefix):
            name = name[len(prefix):]
    return name


def is_placeholder(name: str) -> bool:
    return bool(PLACEHOLDER_RE.match(name))


def classify_confidence(text: str, named: bool) -> str:
    """Map heterogeneous legacy confidence wording onto four levels."""
    t = text.lower()
    if not named:
        if "high" in t.split() or t.startswith("high"):
            return "Strong"
        if "medium" in t:
            return "Inferred"
        return "Unverified"
    proven_markers = (
        "exact retained", "retained diagnostic", "retained function string",
        "retained assertion", "retained symbol", "exact_sdk_archive",
        "opcode_sequence_exact", "exact definition", "exact upstream",
        "exact sdk", "archive-exact", "exact-archive", "exact archive",
        "exact 2.5.1", "exact implementation", "linked_official",
        "exact-official-body-hash",
    )
    if any(m in t for m in proven_markers):
        return "Proven"
    unverified_markers = ("ghidra-discovered address label", "unresolved_shipped_prefix",
                          "typed_batch_only", "vector_seed_unresolved", "placeholder")
    if any(m in t for m in unverified_markers):
        return "Unverified"
    strong_markers = ("exact", "linked", "upstream", "public", "prior-g2",
                      "prior g2", "vector", "link-order", "link_order",
                      "evidence_named", "high")
    if any(m in t for m in strong_markers):
        return "Strong"
    if re.search(r"\blow\b", t) or "none" == t.strip():
        return "Unverified"
    return "Inferred"


def rel(repo: Path, path: Path) -> str:
    try:
        return str(path.relative_to(repo))
    except ValueError:
        return str(path)


def read_tsv(path: Path, header: list[str] | None = None) -> list[dict]:
    with path.open(newline="", encoding="utf-8", errors="replace") as fh:
        lines = [ln for ln in fh if ln.strip() and not ln.startswith("#")]
    if header is not None:
        return [dict(zip(header, ln.rstrip("\n").split("\t"))) for ln in lines]
    return list(csv.DictReader(lines, delimiter="\t"))


def first(row: dict, keys: list[str]) -> str:
    for k in keys:
        v = clean(row.get(k))
        if v and v.lower() not in ("-", "n/a"):
            return v
    return ""


def module_of(row: dict, fallback: str) -> str:
    for k in MODULE_KEYS:
        v = clean(row.get(k))
        if v.lower() in NON_MODULE_VALUES:
            continue
        return v.replace("\\", "/")
    return fallback


class Collector:
    def __init__(self, repo: Path):
        self.repo = repo
        self.rows: dict[str, list[dict]] = defaultdict(list)
        self.rejected = Counter()
        self.sources = Counter()

    # -- payload attribution ------------------------------------------------
    @staticmethod
    def payload_for(address: int) -> str | None:
        for name, lo, hi in PAYLOAD_RANGES:
            if lo <= address < hi:
                return name
        return None

    def add(self, *, payload: str | None, address: int, end: int | None,
            size: int | None, name: str, module: str, confidence: str,
            source: str, note: str, sha: str = "", key: str = "") -> None:
        if payload is None:
            payload = self.payload_for(address)
        if payload is None:
            self.rejected[source] += 1
            return
        if end is not None and end <= address:
            end = None
        if size is not None and size <= 0:
            size = None
        if end is None and size is not None:
            end = address + size
        if size is None and end is not None:
            size = end - address
        name = neutral_name(name)
        if name and not IDENT_RE.match(name):
            name = re.sub(r"[^A-Za-z0-9_.$@]+", "_", name).strip("_")
        sha = sha if SHA_RE.match(sha or "") else ""
        self.rows[payload].append({
            "key": key or f"0x{address:08X}",
            "address": address, "end": end, "size": size, "name": name,
            "module": clean(module), "confidence": confidence,
            "source": source, "note": clean(note)[:180], "sha": sha,
        })
        self.sources[source] += 1

    # -- generic TSV --------------------------------------------------------
    def generic_tsv(self, path: Path, *, payload: str | None = None,
                    coord=None, header: list[str] | None = None,
                    kinds: set[str] | None = None, default_conf_text: str = "",
                    module_fallback: str | None = None) -> None:
        source = rel(self.repo, path)
        stem = path.name
        for suffix in ("-function-map.tsv", ".tsv"):
            if stem.endswith(suffix):
                stem = stem[: -len(suffix)]
                break
        for row in read_tsv(path, header):
            if kinds is not None and clean(row.get("kind")) not in kinds:
                continue
            start = None
            for k in START_KEYS:
                start = parse_hex(row.get(k))
                if start is not None:
                    break
            if start is None:
                continue  # dead-stripped/source-only rows carry no stock address
            end = None
            for k in END_KEYS:
                end = parse_hex(row.get(k))
                if end is not None:
                    break
            size = None
            for k in SIZE_KEYS:
                size = parse_int(row.get(k))
                if size is not None:
                    break
            name = ""
            for k in NAME_KEYS:
                cand = neutral_name(row.get(k, ""))
                if cand and cand not in ("-",) and IDENT_RE.match(cand):
                    if not name or (is_placeholder(name) and not is_placeholder(cand)):
                        name = cand
                    if not is_placeholder(name):
                        break
            conf_text = " ".join(clean(row.get(k)) for k in CONF_KEYS if row.get(k))
            conf_text = (conf_text + " " + default_conf_text).strip()
            named = bool(name) and not is_placeholder(name)
            confidence = classify_confidence(conf_text, named)
            if name and is_placeholder(name):
                confidence = "Unverified"
            note_bits = [clean(row.get(k)) for k in NOTE_KEYS if clean(row.get(k))]
            note = "; ".join(dict.fromkeys(note_bits))
            if conf_text:
                note = f"[{conf_text[:60]}] {note}"
            sha = first(row, SHA_KEYS)
            address = start
            pl = payload
            if coord is not None:
                address, end, pl, extra = coord(start, end)
                if address is None:
                    self.rejected[source] += 1
                    continue
                if extra:
                    note = f"{extra}; {note}"
            self.add(payload=pl, address=address, end=end, size=size,
                     name=name, module=module_of(row, module_fallback or stem),
                     confidence=confidence, source=source, note=note, sha=sha)


# --------------------------------------------------------------------------
# Coordinate transforms
# --------------------------------------------------------------------------
def touch_coord(start: int, end: int | None):
    if start >= TOUCH_PAYLOAD_SIZE:
        return None, None, None, ""
    linked = TOUCH_LINK_BASE + start
    lend = TOUCH_LINK_BASE + end if end is not None else None
    return linked, lend, "touch", f"payload+0x{start:04X}"


def codec_coord_from_package(pkg: int):
    for lo, hi, region, base in CODEC_WINDOWS:
        if lo <= pkg < hi:
            if base is None:
                # BINH stage1 block: 24-byte header, vectors at +0x18; runtime
                # mapping is unresolved, so place relative to IRAM 0x10000000.
                return 0x10000000 + (pkg - lo - 0x18), region, False
            return base + (pkg - lo), region, True
    return None, None, False


# --------------------------------------------------------------------------
# Specialised readers
# --------------------------------------------------------------------------
def read_function_maps(c: Collector, manifests: Path) -> None:
    for path in sorted(manifests.glob("*-function-map.tsv")):
        if path.name.startswith("g2-touch-"):
            c.generic_tsv(path, coord=touch_coord)
        else:
            c.generic_tsv(path)


def read_named_manifests(c: Collector, manifests: Path) -> None:
    plain = [
        "g2-apollo-unanchored-census-functions.tsv",
        "g2-lvgl-vendor-fork-census.tsv",
        "g2-cordio-ll-sea-census.tsv",
        "g2-freetype-engine-census.tsv",
        "em9305-controller-cluster-map.tsv",
        "em9305-residual-provenance-map.tsv",
        "g2-box-ghidra-functions.tsv",
        "g2-box-task-helper-map.tsv",
        "g2-box-task-entry-bodies.tsv",
        "g2-case-final-function-frontier.tsv",
    ]
    for name in plain:
        p = manifests / name
        if p.exists():
            c.generic_tsv(p)
    for p in sorted(manifests.glob("g2-case-*-admission.tsv")):
        c.generic_tsv(p)
    kinds = {"function", "source_function", "provider", "caller", "entry", "hook"}
    for pattern in ("g2-bootloader-*.tsv", "em9305-*-boundary.tsv",
                    "em9305-qpc-hook-provider-closure.tsv"):
        for p in sorted(manifests.glob(pattern)):
            c.generic_tsv(p, kinds=kinds)
    ghidra_header = ["name", "entry", "start", "end-exclusive"]
    for p in sorted(manifests.glob("em9305-ghidra-*.tsv")):
        c.generic_tsv(p, header=ghidra_header,
                      default_conf_text="ghidra-discovered address label")
    touch_files = [
        "g2-touch-relocated-functions.tsv",
        "g2-touch-relocated-semantic-batches.tsv",
        "g2-touch-prefix-helper-evidence.tsv",
        "g2-touch-software-readiness-functions.tsv",
        "g2-touch-capsense-provider-boundary.tsv",
        "g2-touch-application-clean-room-contracts.tsv",
        "g2-touch-relocated-vectors.tsv",
        "g2-touch-i2c-command-map.tsv",
        "g2-touch-source-admission.tsv",
        "g2-touch-policy-helper-source-closure.tsv",
    ]
    for name in touch_files:
        p = manifests / name
        if p.exists():
            c.generic_tsv(p, coord=touch_coord)
    for p in sorted(manifests.glob("g2-touch-*-admission*.tsv")):
        if p.name.endswith("-unavailable.tsv") or "project-license" in p.name:
            continue
        c.generic_tsv(p, coord=touch_coord)
    anchors = manifests / "g2-touch-prefix-evidence-anchors.tsv"
    if anchors.exists():
        c.generic_tsv(anchors, coord=touch_coord, kinds={"authenticated_code_region",
                                                         "function", "handler"})


def read_freetype(c: Collector, manifests: Path) -> None:
    for path in sorted(manifests.glob("g2-freetype-*-function-map.json")):
        data = json.loads(path.read_text())
        source = rel(c.repo, path)
        upstream = data.get("upstream", {})
        lib = f"FreeType {upstream.get('version', '')}".strip()
        for fn in data.get("functions", []):
            start = parse_hex(fn.get("start"))
            if start is None:
                continue
            conf = clean(fn.get("confidence"))
            corr = ",".join(fn.get("identity_corroboration", []) or [])
            confidence = {"high": "Strong", "medium": "Inferred"}.get(conf, "Unverified")
            module = fn.get("source") or fn.get("module") or ""
            c.add(payload=None, address=start, end=parse_hex(fn.get("end_exclusive")),
                  size=fn.get("bytes"), name=fn.get("symbol", ""),
                  module=f"{lib} {module}".strip(), confidence=confidence,
                  source=source,
                  note=f"[{conf}] {fn.get('mapping_origin', '')} {corr}",
                  sha=fn.get("body_sha256", ""))


def read_em9305_corpus(c: Collector, corpus: Path) -> None:
    root = corpus / "em9305"
    if not root.exists():
        return
    # Exact SDK archive comparisons: relocation-normalized byte identity.
    for path in sorted(root.glob("sdk-comparison/*/reports/*.json")) + \
            sorted(root.glob("sdk-comparison/fast-enforced/*.json")):
        data = json.loads(path.read_text())
        source = rel(c.repo, path)
        archive = clean(data.get("identity", {}).get("archive_path"))
        seen = set()
        for fn in data.get("unique_discovered_matches", []) + data.get("functions", []):
            addrs = []
            if fn.get("expected_address_matched") and fn.get("expected_stock_address") is not None:
                addrs = [fn["expected_stock_address"]]
            elif len(fn.get("matches") or []) == 1:
                addrs = fn["matches"]
            for a in addrs:
                if (a, fn.get("name")) in seen:
                    continue
                seen.add((a, fn.get("name")))
                c.add(payload=None, address=int(a), end=None, size=fn.get("size"),
                      name=fn.get("name", ""),
                      module=f"{archive}:{fn.get('object', '')}".strip(":"),
                      confidence="Proven", source=source,
                      note=(f"unique relocation-normalized SDK archive match; "
                            f"{fn.get('compared_byte_count')} bytes compared, "
                            f"{fn.get('relocation_count')} relocations masked"),
                      sha="")
    # Link-order, NOP-aware and vector placements between exact anchors.
    for path in sorted(root.glob("nop-aware/*link-order*.json")) + \
            sorted(root.glob("size-delta/*link-order*.json")):
        data = json.loads(path.read_text())
        source = rel(c.repo, path)
        for key, label in (("placements", "link-order placement between exact anchors"),
                           ("nop_aware_placements", "NOP-aware link-order placement"),
                           ("vector_handler_placements", "vector-table resolved handler")):
            for fn in data.get(key, []) or []:
                a = fn.get("address")
                if a is None:
                    continue
                c.add(payload=None, address=int(a), end=fn.get("end"), size=None,
                      name=fn.get("name", ""), module=fn.get("object", ""),
                      confidence="Strong", source=source,
                      note=(f"{label}; anchors {fn.get('left_anchor', '')}"
                            f"..{fn.get('right_anchor', '')}"))
    # Vendor-modified comparisons (same SDK role, bytes diverge).
    for path in sorted(root.glob("nop-aware/*modified-comparison*.json")) + \
            sorted(root.glob("size-delta/*size-delta-comparison*.json")):
        data = json.loads(path.read_text())
        source = rel(c.repo, path)
        for fn in data.get("functions", []) or []:
            a = fn.get("address")
            if a is None:
                continue
            pct = fn.get("matching_compared_percent")
            c.add(payload=None, address=int(a), end=None, size=fn.get("stock_size"),
                  name=fn.get("name", ""), module=fn.get("object", ""),
                  confidence="Inferred", source=source,
                  note=f"vendor-modified SDK function (partial match{'' if pct is None else f' {pct}%'})")


def read_codec(c: Collector, research_docs: Path) -> None:
    def walk(obj):
        if isinstance(obj, dict):
            if ("package_offset" in obj and isinstance(obj.get("symbol"), str)
                    and isinstance(obj.get("region"), str)):
                yield obj
            for v in obj.values():
                yield from walk(v)
        elif isinstance(obj, list):
            for v in obj:
                yield from walk(v)

    for path in sorted(research_docs.glob("gx8002-*.json")):
        try:
            data = json.loads(path.read_text())
        except (ValueError, UnicodeDecodeError):
            continue
        source = rel(c.repo, path)
        upstream_file = path.name == "gx8002-upstream-object-candidates.json"
        seen = set()
        for occ in walk(data):
            pkg = parse_int(occ.get("package_offset"))
            if pkg is None:
                continue
            key_seen = (pkg, occ.get("symbol"))
            if key_seen in seen:
                continue
            seen.add(key_seen)
            addr, region, mapped = codec_coord_from_package(pkg)
            if addr is None:
                c.rejected[source] += 1
                continue
            has_object = "object" in occ
            conf = "Strong" if has_object else "Inferred"
            if not mapped:
                conf = "Unverified"
            obj = clean(occ.get("object"))
            module = f"{region}|{obj}" if obj else region
            note = (f"package 0x{pkg:05X}; "
                    + ("relocation-free SDK .text section match (NationalChip lvp_kws 8bf9ee5c)"
                       if has_object else "descriptive name from codec function recovery")
                    + ("" if mapped else "; stage1 runtime mapping unresolved"))
            if upstream_file and not has_object:
                continue
            c.add(payload="codec", address=addr, end=None, size=occ.get("bytes"),
                  name=occ.get("symbol", ""), module=module, confidence=conf,
                  source=source, note=note, sha=occ.get("sha256", ""),
                  key=f"{region}:0x{addr:08X}")


def read_memory_map(c: Collector, doc: Path) -> None:
    if not doc.exists():
        return
    source = rel(c.repo, doc)
    pat = re.compile(r"^\|\s*`(0x[0-9A-Fa-f]+)`\s*\|\s*`(0x[0-9A-Fa-f]+)`\s*\|[^|]*\|([^|]*)\|([^|]*)\|")
    skip = re.compile(r"pool|literal|alignment|padding|fill|tail|gap|between|before|after|"
                      r"table|data|string|appended|overlay|cave|redirect entry", re.I)
    for line in doc.read_text().splitlines():
        m = pat.match(line)
        if not m:
            continue
        start, end = int(m.group(1), 16), int(m.group(2), 16)
        desc, detail = clean(m.group(3)), clean(m.group(4))
        ids = re.findall(r"`([A-Za-z_][A-Za-z0-9_]*)`", desc)
        if len(ids) != 1 or skip.search(desc):
            continue
        lib = re.sub(r"`[^`]*`", "", desc)
        lib = re.sub(r"^(Source-replaced|Source-owned|Retained stock|Bootloader|Exact|"
                     r"Complete|Official)\s+", "", lib.strip(), flags=re.I).strip()
        c.add(payload=None, address=start, end=end, size=None, name=ids[0],
              module=lib, confidence="Strong", source=source,
              note=f"{desc}; {detail}")


def read_bootloader_closures(c: Collector, research_docs: Path) -> None:
    pat = re.compile(r"^g2-bootloader-(.+?)-([0-9a-f]{6})-source-closure\.md$")
    skip = re.compile(r"cluster|tail|span|survey|recon|remaining|leaves|seam|frontier|batch")
    for path in sorted(research_docs.glob("g2-bootloader-*-source-closure.md")):
        m = pat.match(path.name)
        if not m or skip.search(m.group(1)):
            continue
        desc = m.group(1)
        if re.search(r"-[0-9a-f]{6}$", desc):
            continue  # address range: several functions
        addr = int(m.group(2), 16)
        c.add(payload=None, address=addr, end=None, size=None,
              name="bl_" + desc.replace("-", "_"), module="even-bootloader",
              confidence="Inferred", source=rel(c.repo, path),
              note="descriptive label from bootloader closure document title")


def read_pt_protocol(c: Collector, corpus: Path) -> None:
    base = corpus / "apollo-main/ghidra/pt-protocol"
    cmd = base / "command-map.tsv"
    if not cmd.exists():
        return
    fmap = {}
    fn_path = base / "functions.jsonl"
    if fn_path.exists():
        for line in fn_path.read_text().splitlines():
            d = json.loads(line)
            fmap[d["stock_start"]] = d
    source = rel(c.repo, cmd)
    for row in read_tsv(cmd):
        start = parse_hex(row["handler_stock_start"])
        cmd_id = int(row["command"], 16)
        d = fmap.get(row["handler_stock_start"], {})
        c.add(payload=None, address=start, end=parse_hex(d.get("stock_end_exclusive")),
              size=None, name=f"pt_cmd_{cmd_id:02X}_handler",
              module="platform/product_test/pt_protocol_procsr.c", confidence="Strong",
              source=source,
              note=f"product-test dispatch table entry for command 0x{cmd_id:02X}")
    roles = {"0x0056F4A0": "pt_protocol_dispatch", "0x0056F42A": "pt_response_prefix",
             "0x0056F46A": "pt_response_checksum", "0x0056F92C": "pt_production_mode_orchestrate",
             "0x00575428": "pt_handler_result"}
    for addr, name in roles.items():
        d = fmap.get(addr, {})
        c.add(payload=None, address=parse_hex(addr),
              end=parse_hex(d.get("stock_end_exclusive")), size=None, name=name,
              module="platform/product_test/pt_protocol_procsr.c", confidence="Inferred",
              source=rel(c.repo, fn_path), note=d.get("role", ""))


def read_apollo_decomp(c: Collector, corpus: Path) -> None:
    path = corpus / "apollo-main/ghidra/decomp/functions.jsonl"
    if not path.exists():
        return
    source = rel(c.repo, path)
    for line in path.read_text().splitlines():
        d = json.loads(line)
        start = int(d["body_start"], 16)
        end = int(d["body_end_inclusive"], 16) + 1
        name = d.get("name", "")
        c.add(payload=None, address=start, end=end, size=None,
              name=name, module="", confidence="Unverified", source=source,
              note="Ghidra function boundary (authenticated 64-shard corpus)",
              sha=d.get("body_sha256", ""))


# --------------------------------------------------------------------------
# Deduplication and output
# --------------------------------------------------------------------------
def score(row: dict) -> tuple:
    named = bool(row["name"]) and not is_placeholder(row["name"])
    return (1 if named else 0, CONFIDENCE_RANK[row["confidence"]],
            1 if row["end"] is not None else 0, row["source"])


def consolidate(rows: list[dict]):
    groups: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        groups[r["key"]].append(r)
    out, conflicts = [], []
    for key, grp in groups.items():
        grp.sort(key=lambda r: (score(r)[:3], r["source"], r["name"]), reverse=True)
        best = dict(grp[0])
        if best["end"] is None:
            for r in grp[1:]:
                if r["end"] is not None:
                    best["end"], best["size"] = r["end"], r["size"]
                    break
        if not best["sha"]:
            for r in grp:
                if r["sha"] and r["end"] == best["end"]:
                    best["sha"] = r["sha"]
                    break
        if not best["module"]:
            best["module"] = next((r["module"] for r in grp if r["module"]), "")
        others = sorted({r["source"] for r in grp if r["source"] != best["source"]})
        evidence = f"{best['source']}: {best['note']}"
        if others:
            shown = ", ".join(os.path.basename(s) for s in others[:4])
            more = f" +{len(others) - 4} more" if len(others) > 4 else ""
            evidence += f" | also: {shown}{more}"
        best["evidence"] = evidence
        out.append(best)
        names = {}
        for r in grp:
            if r["name"] and not is_placeholder(r["name"]):
                names.setdefault(r["name"], r)
        if len(names) > 1:
            for n, r in sorted(names.items()):
                chosen = n == best["name"]
                rival = (CONFIDENCE_RANK[r["confidence"]]
                         >= CONFIDENCE_RANK[best["confidence"]])
                conflicts.append({
                    "key": key, "address": best["address"], "name": n,
                    "confidence": r["confidence"], "source": r["source"],
                    "chosen": "yes" if chosen else "no",
                    "severity": "-" if chosen else ("equal-or-higher" if rival else "lower"),
                })
    out.sort(key=lambda r: (r["address"], r["key"]))
    return out, conflicts


def fmt_addr(v):
    return "" if v is None else f"0x{v:08X}"


def write_outputs(c: Collector, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    header = ["address", "end", "size", "name", "module", "confidence",
              "evidence", "stock_sha256"]
    stats = {}
    all_conflicts = []
    for payload in PAYLOADS:
        rows, conflicts = consolidate(c.rows.get(payload, []))
        path = out_dir / f"{payload}.tsv"
        with path.open("w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh, delimiter="\t", lineterminator="\n",
                           quoting=csv.QUOTE_MINIMAL)
            w.writerow(header)
            for r in rows:
                module = r["module"]
                if payload == "codec":
                    module = module  # region prefix already embedded
                w.writerow([fmt_addr(r["address"]), fmt_addr(r["end"]),
                            "" if r["size"] is None else r["size"], r["name"], module,
                            r["confidence"], r["evidence"].replace("\t", " "), r["sha"]])
        named = [r for r in rows if r["name"] and not is_placeholder(r["name"])]
        stats[payload] = {
            "rows": len(rows),
            "named": len(named),
            "by_confidence": Counter(r["confidence"] for r in named),
            "unnamed_or_placeholder": len(rows) - len(named),
            "conflict_addresses": len({x["key"] for x in conflicts}),
        }
        for x in conflicts:
            x["payload"] = payload
        all_conflicts.extend(conflicts)
    with (out_dir / "conflicts.tsv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["payload", "address", "name", "confidence", "chosen",
                    "rival_rank", "source"])
        for x in sorted(all_conflicts, key=lambda x: (x["payload"], x["key"], x["name"])):
            addr = x["key"] if ":" in x["key"] else fmt_addr(x["address"])
            w.writerow([x["payload"], addr, x["name"], x["confidence"], x["chosen"],
                        x["severity"], x["source"]])
    return stats


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", type=Path, required=True,
                    help="repository root (contains g2/)")
    ap.add_argument("--out", type=Path, required=True, help="output directory")
    ap.add_argument("--no-ghidra-boundaries", action="store_true",
                    help="omit the unnamed Apollo Ghidra boundary rows")
    args = ap.parse_args(argv)
    repo = args.repo.resolve()
    g2 = repo / "g2"
    manifests = g2 / "tools/manifests"
    research_docs = g2 / "docs/research"
    corpus = g2 / "research/corpus"
    c = Collector(repo)
    read_function_maps(c, manifests)
    read_named_manifests(c, manifests)
    read_freetype(c, manifests)
    read_em9305_corpus(c, corpus)
    read_codec(c, research_docs)
    read_memory_map(c, g2 / "docs/memory-map.md")
    read_bootloader_closures(c, research_docs)
    read_pt_protocol(c, corpus)
    if not args.no_ghidra_boundaries:
        read_apollo_decomp(c, corpus)
    stats = write_outputs(c, args.out)
    for payload in PAYLOADS:
        s = stats[payload]
        conf = ", ".join(f"{k}={s['by_confidence'].get(k, 0)}" for k in CONFIDENCE_RANK)
        print(f"{payload}: rows={s['rows']} named={s['named']} ({conf}) "
              f"unnamed={s['unnamed_or_placeholder']} conflicts={s['conflict_addresses']}")
    print(f"input rows by source files: {len(c.sources)} files, "
          f"{sum(c.sources.values())} rows; out-of-range rows rejected: "
          f"{sum(c.rejected.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
