#!/usr/bin/env python3
"""FreeType 2.9.1 engine census of the 0x51/0x52xxxx Apollo-main frontier.

The Apollo unanchored-function provenance census
(``analyze_g2_apollo_unanchored_census.py``) leaves 342 no-evidence Ghidra
functions (75,016 official opaque bytes) in the ``0x51xxxx``/``0x52xxxx``
ranges, hypothesized to be the FreeType 2.9.1 engine, plus 2 functions already
bucketed ``freetype`` (the byte-exact ``FT_Done_Face`` envelope and the
``FT_Open_Face`` envelope that calls it).  This analyzer attributes those 344
functions to FreeType 2.9.1 modules where distinctive evidence supports it.

Evidence tiers, applied in strict priority order:

1. ``recovery-audit-anchor`` (high) -- the function entry is an exact code
   anchor proven by ``docs/research/freetype-recovery-audit.md`` and pinned by
   the fail-closed configuration audit (``FT_Done_Face``, ``FT_Open_Face``,
   ``destroy_face``, ``FT_Init_FreeType``, ``FT_Add_Default_Modules``,
   ``FT_Add_Module``, ``FT_New_Library``, and the smooth three-pass LCD
   fallback renderer body).
2. ``module-string-signature`` (high) -- the function references, through a
   code-region literal-pool cell, a string literal of at least six characters
   that appears in exactly one G2-linked module's sources in the
   authenticated FreeType 2.9.1 snapshot (string literals used only inside
   ``FT_TRACE*``/``FT_ERROR``/``FT_ASSERT`` macros are excluded -- they
   compile to nothing in a release build; shorter literals are excluded
   because generic words such as ``"true"`` collide with non-FreeType
   providers in the image).
3. ``module-class-callback`` / ``raster-funcs-callback`` (high) -- the
   function entry is stored as a callback pointer inside one of the ten
   module class structs of the authenticated ``ft_default_modules[]`` table,
   or inside the smooth renderer's ``FT_Raster_Funcs`` table.
4. ``service-record-callback`` (medium) -- the function entry is stored
   inside a FreeType service record reachable from a service-description
   table whose service-id list uniquely matches one module's
   ``FT_DEFINE_SERVICEDESCRECn`` variant in the snapshot.
5. ``call-topology-single-module`` (medium) -- every closed-world call target
   (token equal to a seed-labelled corpus function entry) collapses to one
   FreeType module.
6. ``call-topology-multi-module`` (low) -- call targets span several FreeType
   modules; the function is FreeType but its module stays unresolved.
7. ``link-order-sandwich`` (low) -- the nearest seed-labelled functions on
   both sides in address order share one module.  Link order groups
   translation units, so this is a low-confidence triage signal only.
8. ``investigation-required`` (none) -- no corroborating evidence.

Seeds are the union of tiers 1-4 over the whole image (most FreeType modules
link outside the census ranges; they still serve as topology and sandwich
references).  Only the 344 census functions receive census rows.  When tiers
disagree on a seed's module, the higher tier wins and the conflict is
reported; a same-tier cross-module conflict raises ``CensusError``.

The analyzer is read-only and deterministic.  It re-derives every seed from
the authenticated official image, the authenticated 64-shard corpus, the
authenticated FreeType 2.9.1 snapshot, and the checked-in parent census
manifest on every run; any drift in the pinned sets raises ``CensusError``.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
import struct
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PATH_ANALYZER = ROOT / "tools/analyze_apollo_embedded_source_paths.py"
MANIFESTS = ROOT / "tools/manifests"
PARENT_MANIFEST = MANIFESTS / "g2-apollo-unanchored-census-functions.tsv"
FREETYPE_SNAPSHOT = ROOT / "third_party/freetype"
PROVENANCE = FREETYPE_SNAPSHOT / "PROVENANCE.json"
G2_FTMODULE = FREETYPE_SNAPSHOT / "g2-config/freetype/config/ftmodule.h"
SERVICE_HEADERS = FREETYPE_SNAPSHOT / "include/freetype/internal/services"

PARENT_MANIFEST_SHA256 = "a36c51c0084e51b6e64fc902ab58be16fa76f2c3b361c3ae543f378a8c1f7b96"
PROVENANCE_SHA256 = "2be8717625bceddee3aa95663186c0629247304c951c4790bc26cd372e3794bf"
G2_FTMODULE_SHA256 = "522c1d358dce8a141b2f8afec7020f66bf800d3d829a1ad22f3418ebf3f05d74"
EXPECTED_IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
EXPECTED_IMAGE_SIZE = 3_523_396

EXPECTED_CORPUS_FUNCTIONS = 7_370
EXPECTED_OVERSIZED_ENTRIES = (
    0x0047CC60,
    0x0048949C,
    0x00509708,
    0x00513E2E,
    0x00514F3C,
    0x00541B74,
    0x0055F994,
    0x005FA120,
)
MAX_TRUSTWORTHY_FUNCTION_ENVELOPE = 16_384

# Census ranges: the parent census's FreeType frontier.
SEA_START = 0x00510000
SEA_END_EXCLUSIVE = 0x00530000
EXPECTED_FRONTIER_FUNCTIONS = 342
EXPECTED_FRONTIER_OFFICIAL_BYTES = 75_016
EXPECTED_PARENT_FREETYPE_ENTRIES = (0x005264A6, 0x00526814)
EXPECTED_PARENT_FREETYPE_BYTES = 946
EXPECTED_CENSUS_FUNCTIONS = 344
EXPECTED_CENSUS_OFFICIAL_BYTES = 75_962

# Code region (functions and embedded literal pools) versus static rodata.
# The lowest module class struct (cff, 0x006DCB74) sits below 0x006D0000;
# nothing at or above 0x006D0000 is a literal-pool cell.
CODE_REGION = (0x00438000, 0x006D0000)
DATA_REGION = (0x006D0000, 0x007A0000)

# G2-linked FreeType modules, in the compiled ft_default_modules[] order
# proven by the recovery audit; recovered from g2-config ftmodule.h on every
# run and checked against this pinned class-name list.
EXPECTED_FTMODULE_CLASSES = (
    "autofit_module_class",
    "tt_driver_class",
    "cff_driver_class",
    "psaux_module_class",
    "psnames_module_class",
    "pshinter_module_class",
    "sfnt_module_class",
    "ft_smooth_renderer_class",
    "ft_smooth_lcd_renderer_class",
    "ft_smooth_lcdv_renderer_class",
)
FTMODULE_CLASS_MODULE = {
    "autofit_module_class": "autofit",
    "tt_driver_class": "truetype",
    "cff_driver_class": "cff",
    "psaux_module_class": "psaux",
    "psnames_module_class": "psnames",
    "pshinter_module_class": "pshinter",
    "sfnt_module_class": "sfnt",
    "ft_smooth_renderer_class": "smooth",
    "ft_smooth_lcd_renderer_class": "smooth",
    "ft_smooth_lcdv_renderer_class": "smooth",
}

MODULES: dict[str, dict[str, str]] = {
    "autofit": {"label": "FreeType 2.9.1 auto-fitter (src/autofit)"},
    "base": {"label": "FreeType 2.9.1 base layer (src/base)"},
    "cff": {"label": "FreeType 2.9.1 CFF driver (src/cff)"},
    "psaux": {"label": "FreeType 2.9.1 PostScript aux module (src/psaux)"},
    "pshinter": {"label": "FreeType 2.9.1 PostScript hinter (src/pshinter)"},
    "psnames": {"label": "FreeType 2.9.1 PostScript glyph names (src/psnames)"},
    "sfnt": {"label": "FreeType 2.9.1 SFNT wrapper (src/sfnt)"},
    "smooth": {"label": "FreeType 2.9.1 smooth rasterizer/renderers (src/smooth)"},
    "truetype": {"label": "FreeType 2.9.1 TrueType driver (src/truetype)"},
}
CENSUS_BUCKETS = tuple(MODULES) + ("freetype-multi-module", "investigation-required")

# FT_Module_Class has 9 words (include/freetype/ftmodapi.h);
# FT_Driver_ClassRec adds 13 (include/freetype/internal/ftdriver.h);
# FT_Renderer_Class adds 6 (include/freetype/internal/ftrend1.h);
# FT_Raster_Funcs has 6 words (include/freetype/ftimage.h).
MODULE_CLASS_WORDS = 9
DRIVER_CLASS_WORDS = MODULE_CLASS_WORDS + 13
RENDERER_CLASS_WORDS = MODULE_CLASS_WORDS + 6
RASTER_FUNCS_WORDS = 6
RASTER_CLASS_OFFSET = (MODULE_CLASS_WORDS + 5) * 4  # FT_Renderer_Class.raster_class

# Module class struct addresses, proven by the recovery audit's decode of
# ft_default_modules[] at 0x0073EEF8 and pinned by the fail-closed
# configuration audit.  Validated against the image on every run: the table
# pointers, the NULL terminator, and each class's module_name string.
FT_DEFAULT_MODULES_TABLE = 0x0073EEF8
MODULE_CLASS_STRUCTS = (
    ("autofitter", 0x00752520, MODULE_CLASS_WORDS * 4, "autofit"),
    ("truetype", 0x006DED34, DRIVER_CLASS_WORDS * 4, "truetype"),
    ("cff", 0x006DCB74, DRIVER_CLASS_WORDS * 4, "cff"),
    ("psaux", 0x00758A18, MODULE_CLASS_WORDS * 4, "psaux"),
    ("psnames", 0x00758A60, MODULE_CLASS_WORDS * 4, "psnames"),
    ("pshinter", 0x00758A3C, MODULE_CLASS_WORDS * 4, "pshinter"),
    ("sfnt", 0x0075A3F8, MODULE_CLASS_WORDS * 4, "sfnt"),
    ("smooth", 0x00718D9C, RENDERER_CLASS_WORDS * 4, "smooth"),
    ("smooth-lcd", 0x00718DD8, RENDERER_CLASS_WORDS * 4, "smooth"),
    ("smooth-lcdv", 0x00718E14, RENDERER_CLASS_WORDS * 4, "smooth"),
)

# Tier-1 anchors: exact code pins from docs/research/freetype-recovery-audit.md.
# Every entry must be a corpus function whose body_start equals the anchor;
# the pinned body span is validated against the corpus on every run.
RECOVERY_AUDIT_ANCHORS = (
    # (entry, module, api label, audit citation)
    (0x005242FC, "base", "FT_Add_Default_Modules",
     "freetype-recovery-audit.md section 1: FT_Add_Default_Modules at 0x5242FC"),
    (0x0052431C, "base", "FT_Init_FreeType",
     "freetype-recovery-audit.md section 1: FT_Init_FreeType at 0x52431C"),
    (0x005258A8, "base", "destroy_face",
     "freetype-recovery-audit.md section 4: private destroy_face body at 0x005258A8"),
    (0x005264A6, "base", "FT_Open_Face",
     "freetype-recovery-audit.md section 4: FT_Done_Face cleanup calls at "
     "0x0052659C and 0x005267D0 sit inside this envelope"),
    (0x00526814, "base", "FT_Done_Face",
     "freetype-recovery-audit.md section 4: exact FT_Done_Face at [0x00526814,0x0052687E)"),
    (0x0052729C, "base", "FT_Add_Module",
     "freetype-recovery-audit.md section 1: FT_Add_Module at 0x52729C"),
    (0x005274B2, "base", "FT_New_Library",
     "freetype-recovery-audit.md section 1: FT_New_Library version stores at 0x5274DA-0x5274E2"),
    (0x005E22E0, "smooth", "ft_smooth_render_generic (three-pass LCD fallback)",
     "freetype-recovery-audit.md section 3: smooth renderer 0x005E22E0..0x005E2636 is "
     "the authenticated 2.9.1 fallback body"),
)

# Tier-2 pins: (entry, module, matched single-module literals).  Re-derived
# from the snapshot and the image on every run; any drift raises CensusError.
EXPECTED_STRING_SIGNATURES = (
    (0x00525574, "base", ("Type 1",)),
    (0x00527F0A, "base", ("hinting-engine", "random-seed")),
    (0x00527FF2, "base", ("hinting-engine",)),
    (0x005285D4, "base", ("/..namedfork/rsrc",)),
    (0x0052862C, "base", ("resource.frk/",)),
    (0x00577D7C, "sfnt", ("missing",)),
    (0x005A6856, "autofit", ("0 1 2 3 4 5 6 7 8 9",)),
    (0x005A9628, "autofit", ("0 1 2 3 4 5 6 7 8 9",)),
    (0x005AB758, "autofit",
     ("default-script", "fallback-script", "increase-x-height", "warping")),
    (0x005AB896, "autofit",
     ("default-script", "fallback-script", "glyph-to-script-map",
      "increase-x-height", "warping")),
    (0x005CFEFA, "psaux", ("StartFontMetrics",)),
    (0x005F289E, "truetype", ("OpticalSize",)),
)

# Tier-3 pins: callbacks decoded from the ten module class structs and from
# the smooth FT_Raster_Funcs table.  Re-derived from the image on every run.
EXPECTED_CLASS_CALLBACKS = (
    (0x005AB98C, "autofit"),
    (0x005F881C, "truetype"),
    (0x005F89BC, "truetype"),
    (0x005AF576, "cff"),
    (0x005AF88C, "cff"),
    (0x005ABFF2, "cff"),
    (0x005AC02A, "cff"),
)
EXPECTED_RASTER_CALLBACKS = (
    (0x005E2052, "smooth"),
    (0x005E2224, "smooth"),
    (0x005E2248, "smooth"),
)

# Tier-4 pins: the five service-description tables decoded from the image,
# each uniquely matched to one module's FT_DEFINE_SERVICEDESCRECn variant.
EXPECTED_SERVICE_TABLES = (
    (0x006E2750, "cff",
     ("font-format", "multi-masters", "metrics-variations", "postscript-info",
      "postscript-font-name", "glyph-dict", "tt-cmaps", "CID", "properties",
      "cff-load")),
    (0x00725060, "truetype",
     ("font-format", "multi-masters", "metrics-variations", "truetype-engine",
      "tt-glyf", "properties")),
    (0x00738B04, "sfnt",
     ("sfnt-table", "postscript-font-name", "glyph-dict", "bdf", "tt-cmaps")),
    (0x00785370, "autofit", ("properties",)),
    (0x00788430, "psnames", ("postscript-cmaps",)),
)
# (callback entry, table-owning module, service id).  The cff ``properties``
# record points at ps_property_set/ps_property_get, which live in
# src/base/ftpsprop.c; the higher-priority string tier already labels those
# two functions ``base`` and wins the conflict (reported in the summary).
EXPECTED_SERVICE_CALLBACKS = (
    (0x00527F0A, "cff", "properties"),
    (0x00527FF2, "cff", "properties"),
    (0x005AB758, "autofit", "properties"),
    (0x005AB896, "autofit", "properties"),
    (0x005AC140, "cff", "glyph-dict"),
    (0x005AC1BC, "cff", "glyph-dict"),
    (0x005ADDB8, "cff", "cff-load"),
    (0x005AE5F0, "cff", "cff-load"),
    (0x005AE7FA, "cff", "multi-masters"),
    (0x005AEA90, "cff", "cff-load"),
    (0x005D9580, "psnames", "postscript-cmaps"),
    (0x005D9716, "psnames", "postscript-cmaps"),
    (0x005D9840, "psnames", "postscript-cmaps"),
    (0x005D9890, "psnames", "postscript-cmaps"),
    (0x005D9EE4, "truetype", "tt-glyf"),
    (0x005D9FC2, "truetype", "tt-glyf"),
    (0x005DAA9C, "sfnt", "postscript-font-name"),
    (0x005DF484, "sfnt", "sfnt-table"),
    (0x005F225E, "truetype", "metrics-variations"),
    (0x005F289E, "truetype", "multi-masters"),
    (0x005F309E, "truetype", "multi-masters"),
    (0x005F32CC, "truetype", "multi-masters"),
    (0x005F3FF0, "truetype", "multi-masters"),
    (0x005F40D6, "truetype", "multi-masters"),
    (0x005F919C, "truetype", "tt-glyf"),
)
SERVICE_RECORD_MAX_BYTES = 0x40

# Final census pins (re-derived on every run).
EXPECTED_SEED_COUNT = 50
EXPECTED_BUCKET_CENSUS = {
    # bucket: (functions, official_opaque_bytes)
    "base": (128, 16_570),
    "investigation-required": (216, 59_392),
}
EXPECTED_EVIDENCE_COUNTS = {
    "recovery-audit-anchor": 7,
    "module-string-signature": 5,
    "call-topology-single-module": 3,
    "link-order-sandwich": 113,
    "none": 216,
}

FUNCTION_BEGIN_RE = re.compile(
    r"OPENCFW_FUNCTION_BEGIN entry=([0-9a-f]+) "
    r"body_start=([0-9a-f]+) body_end=([0-9a-f]+) name=(\S+)",
    re.IGNORECASE,
)
FUNCTION_END_RE = re.compile(r"OPENCFW_FUNCTION_END entry=([0-9a-f]+)", re.IGNORECASE)
ADDRESS_TOKEN_RE = re.compile(r"(?<![0-9a-fA-F])([0-9a-f]{8})(?![0-9a-fA-F])")
STRING_LITERAL_RE = re.compile(r'"((?:[^"\\]|\\.)*)"')
BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
LINE_COMMENT_RE = re.compile(r"//[^\n]*")
SERVICE_ID_RE = re.compile(r'#define\s+(FT_SERVICE_ID_\w+)\s+"([^"]+)"')
SERVICEDESC_RE = re.compile(
    r"FT_DEFINE_SERVICEDESCREC(\d+)\s*\(\s*(\w+)\s*,(.*?)\)", re.DOTALL
)
SERVICEDESC_PAIR_RE = re.compile(r"(FT_SERVICE_ID_\w+)\s*,\s*(&?\w+)")
FT_USE_MODULE_RE = re.compile(r"FT_USE_MODULE\(\s*\w+\s*,\s*(\w+)\s*\)")
TRACE_ONLY_MARKERS = ("FT_TRACE", "FT_ERROR", "FT_ASSERT")
MIN_SIGNATURE_LITERAL = 6

TIER_PRIORITY = {
    "recovery-audit-anchor": 0,
    "module-string-signature": 1,
    "module-class-callback": 2,
    "raster-funcs-callback": 2,
    "service-record-callback": 3,
}


class CensusError(RuntimeError):
    """Raised when authenticated evidence or a closed census changes."""


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _load_path_analyzer():
    spec = importlib.util.spec_from_file_location(
        "apollo_paths_for_freetype_census", PATH_ANALYZER
    )
    if spec is None or spec.loader is None:
        raise CensusError(f"cannot load {PATH_ANALYZER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _strip_comments(text: str) -> str:
    return LINE_COMMENT_RE.sub(" ", BLOCK_COMMENT_RE.sub(" ", text))


class Snapshot:
    """Authenticated read access to the vendored FreeType 2.9.1 snapshot."""

    def __init__(self, root: Path = FREETYPE_SNAPSHOT, provenance_path: Path = PROVENANCE):
        provenance_bytes = provenance_path.read_bytes()
        if _sha256_bytes(provenance_bytes) != PROVENANCE_SHA256:
            raise CensusError("FreeType PROVENANCE.json identity changed")
        records = json.loads(provenance_bytes.decode("utf-8"))["files"]
        self._by_local_path = {record["local_path"]: record for record in records}
        if len(self._by_local_path) != 297:
            raise CensusError("FreeType snapshot file census changed")
        self._root = root

    def read_text(self, local_path: str) -> str:
        record = self._by_local_path.get(local_path)
        if record is None:
            raise CensusError(f"snapshot file not in PROVENANCE.json: {local_path}")
        raw = (self._root / local_path).read_bytes()
        if len(raw) != record["size"] or _sha256_bytes(raw) != record["sha256"]:
            raise CensusError(f"snapshot file drifted: {local_path}")
        return raw.decode("latin-1")

    def module_sources(self, module: str) -> dict[str, str]:
        prefix = f"src/{module}/"
        out = {}
        for local_path in sorted(self._by_local_path):
            if local_path.startswith(prefix) and local_path.endswith((".c", ".h")):
                out[local_path] = self.read_text(local_path)
        if not out:
            raise CensusError(f"no snapshot sources for module {module}")
        return out

    def service_headers(self) -> dict[str, str]:
        prefix = "include/freetype/internal/services/"
        out = {}
        for local_path in sorted(self._by_local_path):
            if local_path.startswith(prefix) and local_path.endswith(".h"):
                out[local_path] = self.read_text(local_path)
        if not out:
            raise CensusError("no FreeType service headers in snapshot")
        return out


def load_g2_modules(ftmodule_path: Path = G2_FTMODULE) -> tuple[str, ...]:
    """G2-linked module directories in compiled ft_default_modules[] order."""

    raw = ftmodule_path.read_bytes()
    if _sha256_bytes(raw) != G2_FTMODULE_SHA256:
        raise CensusError("recovered g2-config ftmodule.h identity changed")
    classes = tuple(FT_USE_MODULE_RE.findall(raw.decode("latin-1")))
    if classes != EXPECTED_FTMODULE_CLASSES:
        raise CensusError(f"G2 ftmodule.h class list changed: {classes!r}")
    modules: list[str] = []
    for name in classes:
        module = FTMODULE_CLASS_MODULE.get(name)
        if module is None:
            raise CensusError(f"ftmodule.h class has no module rule: {name}")
        modules.append(module)
    return tuple(dict.fromkeys(modules))


def parse_corpus_functions(logs: list[Path]) -> dict[int, dict[str, Any]]:
    functions: dict[int, dict[str, Any]] = {}
    current: dict[str, Any] | None = None
    for log in logs:
        for line in log.read_text(encoding="utf-8", errors="strict").splitlines():
            begin = FUNCTION_BEGIN_RE.search(line)
            if begin:
                entry, body_start, body_end = (int(value, 16) for value in begin.groups()[:3])
                if entry in functions:
                    raise CensusError(f"duplicate Ghidra function entry 0x{entry:08x}")
                current = {
                    "entry": entry,
                    "body_start": body_start,
                    "body_end_inclusive": body_end,
                    "name": begin.group(4),
                    "tokens": set(),
                }
                functions[entry] = current
                continue
            end = FUNCTION_END_RE.search(line)
            if end:
                entry = int(end.group(1), 16)
                if current is None or current["entry"] != entry:
                    raise CensusError(f"unbalanced Ghidra function marker 0x{entry:08x}")
                current = None
                continue
            if current is not None:
                current["tokens"].update(
                    int(token, 16) for token in ADDRESS_TOKEN_RE.findall(line)
                )
    if current is not None:
        raise CensusError("unterminated Ghidra function at end of corpus")
    if len(functions) != EXPECTED_CORPUS_FUNCTIONS:
        raise CensusError(
            f"expected {EXPECTED_CORPUS_FUNCTIONS} Ghidra functions, "
            f"found {len(functions)}"
        )
    return functions


def load_census_set(manifest_path: Path = PARENT_MANIFEST) -> dict[int, dict[str, Any]]:
    """The 344 census functions from the parent provenance census manifest."""

    raw = manifest_path.read_bytes()
    if _sha256_bytes(raw) != PARENT_MANIFEST_SHA256:
        raise CensusError("parent unanchored-census functions manifest identity changed")
    lines = [
        line
        for line in raw.decode("utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    reader = csv.DictReader(lines, delimiter="\t")
    census: dict[int, dict[str, Any]] = {}
    frontier_functions = 0
    frontier_bytes = 0
    freetype_entries: list[int] = []
    freetype_bytes = 0
    for row in reader:
        entry = int(row["entry"], 16)
        bucket = row["bucket"]
        in_sea = SEA_START <= entry < SEA_END_EXCLUSIVE
        if bucket == "investigation-required-no-evidence" and in_sea:
            frontier_functions += 1
            frontier_bytes += int(row["official_opaque_bytes"])
        elif bucket == "freetype":
            freetype_entries.append(entry)
            freetype_bytes += int(row["official_opaque_bytes"])
        else:
            continue
        census[entry] = {
            "entry": entry,
            "body_start": int(row["body_start"], 16),
            "body_end_exclusive": int(row["body_end_exclusive"], 16),
            "envelope_bytes": int(row["envelope_bytes"]),
            "official_opaque_bytes": int(row["official_opaque_bytes"]),
            "parent_bucket": bucket,
        }
    if frontier_functions != EXPECTED_FRONTIER_FUNCTIONS:
        raise CensusError(
            f"FreeType frontier census changed: {frontier_functions} != "
            f"{EXPECTED_FRONTIER_FUNCTIONS}"
        )
    if frontier_bytes != EXPECTED_FRONTIER_OFFICIAL_BYTES:
        raise CensusError(
            f"FreeType frontier bytes changed: {frontier_bytes} != "
            f"{EXPECTED_FRONTIER_OFFICIAL_BYTES}"
        )
    if tuple(sorted(freetype_entries)) != EXPECTED_PARENT_FREETYPE_ENTRIES:
        raise CensusError("parent freetype-bucket membership changed")
    if freetype_bytes != EXPECTED_PARENT_FREETYPE_BYTES:
        raise CensusError("parent freetype-bucket bytes changed")
    if len(census) != EXPECTED_CENSUS_FUNCTIONS:
        raise CensusError(
            f"census set changed: {len(census)} != {EXPECTED_CENSUS_FUNCTIONS}"
        )
    return census


class Image:
    def __init__(self, blob: bytes, load_base: int):
        if len(blob) != EXPECTED_IMAGE_SIZE:
            raise CensusError("official image size changed")
        if _sha256_bytes(blob) != EXPECTED_IMAGE_SHA256:
            raise CensusError("official image identity changed")
        self.blob = blob
        self.load_base = load_base

    def rd32(self, address: int) -> int:
        return struct.unpack_from("<I", self.blob, address - self.load_base)[0]

    def cstr(self, address: int) -> str:
        offset = address - self.load_base
        end = self.blob.index(b"\x00", offset)
        return self.blob[offset:end].decode("ascii")

    def find_nul_string(self, text: str) -> list[int]:
        needle = text.encode("ascii") + b"\x00"
        out = []
        cursor = 0
        while True:
            offset = self.blob.find(needle, cursor)
            if offset < 0:
                return out
            out.append(self.load_base + offset)
            cursor = offset + 1

    def find_pointer_cells(self, target: int, region: tuple[int, int]) -> list[int]:
        needle = struct.pack("<I", target)
        out = []
        cursor = 0
        while True:
            offset = self.blob.find(needle, cursor)
            if offset < 0:
                return out
            address = self.load_base + offset
            if region[0] <= address < region[1]:
                out.append(address)
            cursor = offset + 1


def validate_module_table(image: Image) -> None:
    """Re-derive ft_default_modules[] and every class module_name string."""

    for index, (name, class_address, _size, _module) in enumerate(MODULE_CLASS_STRUCTS):
        pointer = image.rd32(FT_DEFAULT_MODULES_TABLE + index * 4)
        if pointer != class_address:
            raise CensusError(
                f"ft_default_modules[{index}] changed: 0x{pointer:08X} != "
                f"0x{class_address:08X}"
            )
        if image.cstr(image.rd32(class_address + 8)) != name:
            raise CensusError(f"module class 0x{class_address:08X} name changed")
    terminator = image.rd32(FT_DEFAULT_MODULES_TABLE + len(MODULE_CLASS_STRUCTS) * 4)
    if terminator != 0:
        raise CensusError("ft_default_modules[] NULL terminator changed")


def derive_string_signatures(
    snapshot: Snapshot, image: Image, functions: dict[int, dict[str, Any]]
) -> dict[int, tuple[str, tuple[str, ...]]]:
    """Functions referencing a single-module, image-unique string literal."""

    literal_modules: dict[str, set[str]] = {}
    for module in MODULES:
        for text in snapshot.module_sources(module).values():
            for line in _strip_comments(text).splitlines():
                if any(marker in line for marker in TRACE_ONLY_MARKERS):
                    continue
                for match in STRING_LITERAL_RE.finditer(line):
                    literal = match.group(1)
                    if (
                        len(literal) < MIN_SIGNATURE_LITERAL
                        or "\\" in literal
                        or not literal.isprintable()
                        or not literal.isascii()
                    ):
                        continue
                    literal_modules.setdefault(literal, set()).add(module)
    hits: dict[int, dict[str, set[str]]] = {}
    for literal, modules in sorted(literal_modules.items()):
        if len(modules) != 1:
            continue
        module = next(iter(modules))
        for address in image.find_nul_string(literal):
            for cell in image.find_pointer_cells(address, CODE_REGION):
                for entry, row in functions.items():
                    if cell in row["tokens"]:
                        hits.setdefault(entry, {}).setdefault(module, set()).add(literal)
    result: dict[int, tuple[str, tuple[str, ...]]] = {}
    for entry, by_module in hits.items():
        if len(by_module) != 1:
            raise CensusError(
                f"string-signature conflict at 0x{entry:08X}: {sorted(by_module)}"
            )
        module = next(iter(by_module))
        result[entry] = (module, tuple(sorted(by_module[module])))
    expected = {
        entry: (module, tuple(strings))
        for entry, module, strings in EXPECTED_STRING_SIGNATURES
    }
    if result != expected:
        raise CensusError(
            "module string-signature census changed: "
            f"derived {sorted((f'0x{e:08X}', v[0]) for e, v in result.items())}"
        )
    return result


def derive_class_callbacks(
    image: Image, functions: dict[int, dict[str, Any]]
) -> tuple[dict[int, str], dict[int, str]]:
    class_callbacks: dict[int, str] = {}
    raster_callbacks: dict[int, str] = {}
    raster_tables: set[int] = set()
    for _name, class_address, size, module in MODULE_CLASS_STRUCTS:
        for offset in range(0, size, 4):
            word = image.rd32(class_address + offset)
            if (word & 1) and (word & ~1) in functions:
                entry = word & ~1
                if class_callbacks.setdefault(entry, module) != module:
                    raise CensusError(f"class-callback conflict at 0x{entry:08X}")
            if size == RENDERER_CLASS_WORDS * 4 and offset == RASTER_CLASS_OFFSET:
                raster_tables.add(word)
    for table in sorted(raster_tables):
        if not (DATA_REGION[0] <= table < DATA_REGION[1]):
            raise CensusError(f"raster-funcs table outside rodata: 0x{table:08X}")
        for offset in range(4, RASTER_FUNCS_WORDS * 4, 4):
            word = image.rd32(table + offset)
            if (word & 1) and (word & ~1) in functions:
                entry = word & ~1
                if raster_callbacks.setdefault(entry, "smooth") != "smooth":
                    raise CensusError(f"raster-callback conflict at 0x{entry:08X}")
    expected_class = {entry: module for entry, module in EXPECTED_CLASS_CALLBACKS}
    if class_callbacks != expected_class:
        raise CensusError("module class callback census changed")
    expected_raster = {entry: module for entry, module in EXPECTED_RASTER_CALLBACKS}
    if raster_callbacks != expected_raster:
        raise CensusError("raster-funcs callback census changed")
    return class_callbacks, raster_callbacks


def derive_service_callbacks(
    snapshot: Snapshot, image: Image, functions: dict[int, dict[str, Any]]
) -> tuple[dict[int, tuple[str, str]], list[dict[str, Any]]]:
    """Service-record callbacks behind snapshot-matched service tables."""

    macro_to_id: dict[str, str] = {}
    for text in snapshot.service_headers().values():
        for match in SERVICE_ID_RE.finditer(text):
            macro_to_id[match.group(1)] = match.group(2)
    if len(macro_to_id) != 21:
        raise CensusError("FT_SERVICE_ID census changed")

    variants: list[tuple[str, tuple[str, ...]]] = []
    for module in MODULES:
        for local_path, text in snapshot.module_sources(module).items():
            if not local_path.endswith(".c"):
                continue
            for match in SERVICEDESC_RE.finditer(_strip_comments(text)):
                count = int(match.group(1))
                pairs = SERVICEDESC_PAIR_RE.findall(match.group(3))
                if len(pairs) != count:
                    raise CensusError(
                        f"servicedesc pair drift in {local_path}: {match.group(2)}"
                    )
                ids = tuple(macro_to_id.get(pair[0]) for pair in pairs)
                if any(service_id is None for service_id in ids):
                    raise CensusError(f"unknown FT_SERVICE_ID in {local_path}")
                variants.append((module, ids))

    # Image service-description tables: rodata cells holding a service-id
    # string pointer, grouped into contiguous 8-byte entries.
    slots: dict[int, str] = {}
    for service_id in sorted(macro_to_id.values()):
        for address in image.find_nul_string(service_id):
            for cell in image.find_pointer_cells(address, DATA_REGION):
                slots[cell] = service_id
    tables: list[list[int]] = []
    consumed: set[int] = set()
    for cell in sorted(slots):
        if cell in consumed:
            continue
        start = cell
        while start - 8 in slots:
            start -= 8
        run = []
        cursor = start
        while cursor in slots:
            run.append(cursor)
            consumed.add(cursor)
            cursor += 8
        tables.append(run)

    boundaries = set(slots)
    table_reports: list[dict[str, Any]] = []
    callbacks: dict[int, tuple[str, str]] = {}
    for run in tables:
        ids = tuple(slots[cell] for cell in run)
        owners = {module for module, variant_ids in variants if variant_ids == ids}
        if len(owners) != 1:
            raise CensusError(
                f"service table at 0x{run[0]:08X} matches {sorted(owners)} modules"
            )
        module = next(iter(owners))
        table_reports.append(
            {"address": run[0], "module": module, "service_ids": list(ids)}
        )
        for cell in run:
            record = image.rd32(cell + 4)
            boundaries.add(record)
        for cell in run:
            service_id = slots[cell]
            record = image.rd32(cell + 4)
            end = record + SERVICE_RECORD_MAX_BYTES
            for boundary in boundaries:
                if record < boundary < end:
                    end = boundary
            for offset in range(0, max(0, end - record), 4):
                word = image.rd32(record + offset)
                if (word & 1) and (word & ~1) in functions:
                    entry = word & ~1
                    previous = callbacks.setdefault(entry, (module, service_id))
                    if previous != (module, service_id):
                        raise CensusError(f"service-callback conflict at 0x{entry:08X}")

    expected_tables = sorted(
        (address, module, tuple(ids)) for address, module, ids in EXPECTED_SERVICE_TABLES
    )
    derived_tables = sorted(
        (row["address"], row["module"], tuple(row["service_ids"]))
        for row in table_reports
    )
    if derived_tables != expected_tables:
        raise CensusError("service-description table census changed")
    expected_callbacks = {
        entry: (module, service_id)
        for entry, module, service_id in EXPECTED_SERVICE_CALLBACKS
    }
    if callbacks != expected_callbacks:
        raise CensusError("service-record callback census changed")
    return callbacks, sorted(table_reports, key=lambda row: row["address"])


def analyze(
    corpus_root: Path,
    manifests_dir: Path = MANIFESTS,
    snapshot_root: Path = FREETYPE_SNAPSHOT,
) -> dict[str, Any]:
    path_module = _load_path_analyzer()
    logs = path_module.verify_corpus(corpus_root)
    functions = parse_corpus_functions(logs)
    blob = path_module.DEFAULT_IMAGE.read_bytes()
    image = Image(blob, path_module.LOAD_BASE)
    validate_module_table(image)
    modules = load_g2_modules()
    # ``base`` is not a registered module: it is linked unconditionally, and
    # its presence is proven by the recovery-audit anchors (FT_New_Library
    # etc.); the registered table names the other eight source modules.
    if set(modules) != set(MODULES) - {"base"}:
        raise CensusError("G2 module set drifted from the census module table")
    snapshot = Snapshot(
        snapshot_root, provenance_path=snapshot_root / PROVENANCE.name
    )

    census = load_census_set(manifests_dir / PARENT_MANIFEST.name)
    for entry, row in census.items():
        corpus_row = functions.get(entry)
        if corpus_row is None:
            raise CensusError(f"census function 0x{entry:08X} missing from corpus")
        if (
            corpus_row["body_start"] != row["body_start"]
            or corpus_row["body_end_inclusive"] + 1 != row["body_end_exclusive"]
        ):
            raise CensusError(f"census function 0x{entry:08X} body range changed")

    oversized = sorted(
        entry
        for entry, row in functions.items()
        if row["body_end_inclusive"] - row["body_start"] + 1
        > MAX_TRUSTWORTHY_FUNCTION_ENVELOPE
    )
    if tuple(oversized) != EXPECTED_OVERSIZED_ENTRIES:
        raise CensusError("oversized envelope census changed")
    oversized_set = set(oversized)

    # Tier 1: recovery-audit anchors.
    seeds: dict[int, tuple[str, str]] = {}
    anchor_details: dict[int, str] = {}
    for entry, module, label, citation in RECOVERY_AUDIT_ANCHORS:
        corpus_row = functions.get(entry)
        if corpus_row is None or corpus_row["body_start"] != entry:
            raise CensusError(f"recovery-audit anchor 0x{entry:08X} is not a corpus function")
        seeds[entry] = (module, "recovery-audit-anchor")
        anchor_details[entry] = f"{label}; docs/research/{citation}"

    # Tier 2: module string signatures.
    string_signatures = derive_string_signatures(snapshot, image, functions)
    for entry, (module, literals) in string_signatures.items():
        seeds[entry] = (module, "module-string-signature")

    # Tier 3: module class and raster-funcs callbacks.
    class_callbacks, raster_callbacks = derive_class_callbacks(image, functions)
    for entry, module in class_callbacks.items():
        seeds[entry] = (module, "module-class-callback")
    for entry, module in raster_callbacks.items():
        seeds[entry] = (module, "raster-funcs-callback")

    # Tier 4: service-record callbacks.  Lower priority: on a cross-module
    # conflict with an existing higher-tier seed the earlier label wins and
    # the conflict is reported; a same-tier conflict fails closed.
    service_callbacks, service_tables = derive_service_callbacks(
        snapshot, image, functions
    )
    conflicts: list[dict[str, Any]] = []
    for entry, (module, service_id) in sorted(service_callbacks.items()):
        existing = seeds.get(entry)
        if existing is not None and existing[0] != module:
            existing_module, existing_tier = existing
            if TIER_PRIORITY[existing_tier] < TIER_PRIORITY["service-record-callback"]:
                conflicts.append(
                    {
                        "entry": entry,
                        "service_table_module": module,
                        "service_id": service_id,
                        "kept_module": existing_module,
                        "kept_evidence": existing_tier,
                    }
                )
                continue
            raise CensusError(
                f"seed conflict at 0x{entry:08X}: {existing_module}/{existing_tier} "
                f"vs {module}/service-record-callback"
            )
        seeds[entry] = (module, "service-record-callback")
    if len(seeds) != EXPECTED_SEED_COUNT:
        raise CensusError(f"seed census changed: {len(seeds)} != {EXPECTED_SEED_COUNT}")

    # Address-ordered accepted envelopes for the sandwich tier.
    accepted_order = sorted(
        (entry for entry in functions if entry not in oversized_set),
        key=lambda entry: functions[entry]["body_start"],
    )
    position = {entry: index for index, entry in enumerate(accepted_order)}

    records: list[dict[str, Any]] = []
    for entry in sorted(census, key=lambda value: census[value]["body_start"]):
        row = census[entry]
        record: dict[str, Any] = {
            "entry": entry,
            "body_start": row["body_start"],
            "body_end_exclusive": row["body_end_exclusive"],
            "envelope_bytes": row["envelope_bytes"],
            "official_opaque_bytes": row["official_opaque_bytes"],
            "bucket": None,
            "evidence": None,
            "confidence": None,
            "detail": "",
        }
        seed = seeds.get(entry)
        if seed is not None:
            module, tier = seed
            record["bucket"] = module
            record["evidence"] = tier
            if tier == "recovery-audit-anchor":
                record["confidence"] = "high"
                record["detail"] = anchor_details[entry]
            elif tier == "module-string-signature":
                record["confidence"] = "high"
                literals = ", ".join(repr(value) for value in string_signatures[entry][1])
                record["detail"] = f"references single-module literal(s) {literals}"
            elif tier in ("module-class-callback", "raster-funcs-callback"):
                record["confidence"] = "high"
                record["detail"] = f"callback pointer in the {module} module data structures"
            else:
                service_id = service_callbacks[entry][1]
                record["confidence"] = "medium"
                record["detail"] = (
                    f"callback in the {module} service record for '{service_id}'"
                )
            records.append(record)
            continue
        target_modules = {
            seeds[token][0] for token in functions[entry]["tokens"] if token in seeds
        }
        if len(target_modules) == 1:
            module = next(iter(target_modules))
            record.update(
                bucket=module,
                evidence="call-topology-single-module",
                confidence="medium",
                detail="every closed-world call target is " + module,
            )
            records.append(record)
            continue
        if len(target_modules) > 1:
            record.update(
                bucket="freetype-multi-module",
                evidence="call-topology-multi-module",
                confidence="low",
                detail="call targets span " + "|".join(sorted(target_modules)),
            )
            records.append(record)
            continue
        index = position[entry]
        previous_module = next_module = None
        cursor = index - 1
        while cursor >= 0:
            candidate = accepted_order[cursor]
            if candidate in seeds:
                previous_module = seeds[candidate][0]
                break
            cursor -= 1
        cursor = index + 1
        while cursor < len(accepted_order):
            candidate = accepted_order[cursor]
            if candidate in seeds:
                next_module = seeds[candidate][0]
                break
            cursor += 1
        if previous_module is not None and previous_module == next_module:
            record.update(
                bucket=previous_module,
                evidence="link-order-sandwich",
                confidence="low",
                detail="bracketed in link order by " + previous_module,
            )
            records.append(record)
            continue
        record.update(
            bucket="investigation-required",
            evidence="none",
            confidence="none",
            detail="no FreeType module evidence",
        )
        records.append(record)

    buckets: dict[str, dict[str, Any]] = {}
    evidence_counts: Counter[str] = Counter()
    for record in records:
        bucket = buckets.setdefault(
            record["bucket"], {"functions": 0, "official_opaque_bytes": 0}
        )
        bucket["functions"] += 1
        bucket["official_opaque_bytes"] += record["official_opaque_bytes"]
        evidence_counts[record["evidence"]] += 1
    bucket_census = {
        name: (row["functions"], row["official_opaque_bytes"])
        for name, row in buckets.items()
    }
    if bucket_census != EXPECTED_BUCKET_CENSUS:
        raise CensusError(f"FreeType engine bucket census changed: {bucket_census}")
    if dict(evidence_counts) != EXPECTED_EVIDENCE_COUNTS:
        raise CensusError(f"FreeType engine evidence census changed: {dict(evidence_counts)}")

    total_bytes = sum(record["official_opaque_bytes"] for record in records)
    if total_bytes != EXPECTED_CENSUS_OFFICIAL_BYTES:
        raise CensusError("census official-byte reconciliation changed")

    seed_summary = []
    for entry in sorted(seeds, key=lambda value: functions[value]["body_start"]):
        module, tier = seeds[entry]
        seed_summary.append(
            {
                "entry": entry,
                "module": module,
                "evidence": tier,
                "in_census_set": entry in census,
            }
        )

    return {
        "schema_version": 1,
        "analysis_mode": "read-only; no signing, flashing, erase, or hardware operation",
        "target": "official G2 s200_v2.2.6.10 Apollo main FreeType 2.9.1 engine",
        "inputs": {
            "image_sha256": EXPECTED_IMAGE_SHA256,
            "parent_manifest_sha256": PARENT_MANIFEST_SHA256,
            "freetype_provenance_sha256": PROVENANCE_SHA256,
            "g2_ftmodule_sha256": G2_FTMODULE_SHA256,
        },
        "reconciliation": {
            "parent_frontier_functions": EXPECTED_FRONTIER_FUNCTIONS,
            "parent_frontier_official_bytes": EXPECTED_FRONTIER_OFFICIAL_BYTES,
            "parent_freetype_bucket_functions": len(EXPECTED_PARENT_FREETYPE_ENTRIES),
            "parent_freetype_bucket_official_bytes": EXPECTED_PARENT_FREETYPE_BYTES,
            "census_functions": len(records),
            "census_official_bytes": total_bytes,
        },
        "g2_modules_in_link_order": list(modules),
        "seeds": seed_summary,
        "service_tables": [
            {
                "address": f"0x{row['address']:08X}",
                "module": row["module"],
                "service_ids": row["service_ids"],
            }
            for row in service_tables
        ],
        "resolved_seed_conflicts": [
            {
                "entry": f"0x{row['entry']:08X}",
                "service_table_module": row["service_table_module"],
                "service_id": row["service_id"],
                "kept_module": row["kept_module"],
                "kept_evidence": row["kept_evidence"],
            }
            for row in conflicts
        ],
        "buckets": [
            {
                "bucket": name,
                "functions": buckets[name]["functions"],
                "official_opaque_bytes": buckets[name]["official_opaque_bytes"],
            }
            for name in CENSUS_BUCKETS
            if name in buckets
        ],
        "evidence_counts": dict(sorted(evidence_counts.items())),
        "limitations": [
            "module buckets are evidence triage, not per-function source ownership or behavioral reconstruction",
            "link-order-sandwich labels are low-confidence hypotheses for queue ordering, never proof of ownership",
            "only the base module has seed anchors inside the 0x51/0x52xxxx ranges; everything below the first base anchor (0x005242FC) cannot sandwich and mostly stays investigation-required",
            "identical string literals merged by the linker across providers could in principle mislabel a string-signature seed; every derived seed is pinned and re-validated on every run",
            "functions whose code Ghidra covered only inside the eight rejected oversized envelopes cannot seed function-level topology",
        ],
        "functions": records,
    }


FUNCTIONS_TSV_HEADER = (
    "entry\tbody_start\tbody_end_exclusive\tenvelope_bytes\t"
    "official_opaque_bytes\tbucket\tevidence\tconfidence\tdetail"
)


def functions_tsv(report: dict[str, Any]) -> str:
    lines = [
        "# G2 FreeType 2.9.1 engine census; regenerated by "
        "tools/analyze_g2_freetype_engine_census.py",
        FUNCTIONS_TSV_HEADER,
    ]
    for record in report["functions"]:
        lines.append(
            "\t".join(
                (
                    f"0x{record['entry']:08X}",
                    f"0x{record['body_start']:08X}",
                    f"0x{record['body_end_exclusive']:08X}",
                    str(record["envelope_bytes"]),
                    str(record["official_opaque_bytes"]),
                    record["bucket"],
                    record["evidence"],
                    record["confidence"],
                    record["detail"],
                )
            )
        )
    return "\n".join(lines) + "\n"


def summary_json(report: dict[str, Any]) -> str:
    summary = {key: value for key, value in report.items() if key != "functions"}
    return json.dumps(summary, indent=2, sort_keys=True) + "\n"


def _text(report: dict[str, Any]) -> str:
    reconciliation = report["reconciliation"]
    lines = [
        "G2 FreeType 2.9.1 engine census: PASS",
        f"  parent frontier: {reconciliation['parent_frontier_functions']} functions, "
        f"{reconciliation['parent_frontier_official_bytes']} official bytes",
        f"  census set: {reconciliation['census_functions']} functions, "
        f"{reconciliation['census_official_bytes']} official bytes",
        f"  seeds: {len(report['seeds'])}",
        "  buckets:",
    ]
    for bucket in report["buckets"]:
        lines.append(
            f"    {bucket['bucket']}: {bucket['functions']} functions, "
            f"{bucket['official_opaque_bytes']} official bytes"
        )
    lines.append("hardware/flash operations: none")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ghidra-corpus", type=Path, required=True)
    parser.add_argument("--manifests", type=Path, default=MANIFESTS)
    parser.add_argument("--snapshot", type=Path, default=FREETYPE_SNAPSHOT)
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--write-manifests",
        type=Path,
        metavar="DIRECTORY",
        help="write g2-freetype-engine-census.tsv and "
        "g2-freetype-engine-census-summary.json into DIRECTORY",
    )
    args = parser.parse_args()
    report = analyze(
        args.ghidra_corpus,
        manifests_dir=args.manifests,
        snapshot_root=args.snapshot,
    )
    if args.write_manifests is not None:
        directory = args.write_manifests
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "g2-freetype-engine-census.tsv").write_text(
            functions_tsv(report), encoding="utf-8"
        )
        (directory / "g2-freetype-engine-census-summary.json").write_text(
            summary_json(report), encoding="utf-8"
        )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
