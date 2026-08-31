#!/usr/bin/env python3
"""Prove the retained G2 Ambiq LVGL display port is functionally source-owned.

The retained path is private integration provenance, not evidence of a still
opaque implementation.  This read-only audit authenticates the stock image,
the seven complete stock functions, their generated redirects and replacement
sources, and the source-path boundary between the vendor display port and the
first-party input manager.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PATH_ANALYZER = ROOT / "tools/analyze_apollo_embedded_source_paths.py"
DEFAULT_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
DISPLAY_PATH = r"third_party\lvgl_v9.3\lvgl_ambiq_porting\lv_ambiq_display.c"
INPUT_MANAGER_PATH = r"platform\input\service_input_manager.c"

FUNCTIONS = {
    "open_cfw_lv_buffer_sync": (0x0047366C, 136, "ed721fed382db6ba8d3e175095290ea91698c919f4942fe3019a2a79da6caa4e"),
    "open_cfw_lv_display_sync": (0x004736F4, 142, "366105e7228b6998959b3487e079b69ebdfd55caf9d0c373633b0e8743e2a6cd"),
    "open_cfw_lv_display_setup": (0x00473782, 156, "d0f3a63dee7ba606340319bff6f4f094954e1834d3a60aac01e20e8732f13779"),
    "open_cfw_lv_display_lock": (0x0047381E, 76, "364966c0adae4984a533bd2c21ae312e3c4e9adb4d41502f63ee7cdd565b8c6f"),
    "open_cfw_lv_display_unlock": (0x0047386A, 62, "3855e4bb9e42420dcb3bdcd04b652ea3c5d21b63877b0c9d3121923f53e3c571"),
    "open_cfw_lv_display_lock_initialize": (0x004738A8, 54, "bba889445f513ff5e715afe2e98a6d5ca8e206bf4769a0fb372a6c62e4323aa8"),
    "open_cfw_lv_display_port_initialize": (0x00473928, 12, "2f750e3edcff2dae51c7dcd6885cb0b5ce3ff3e6e7ba655d496e9438def1494f"),
}
PATH_ANCHORED_ENTRIES = {0x0047366C, 0x00473782, 0x0047381E, 0x0047386A, 0x004738A8}
SOURCE_PINS = {
    "components/apollo_main/core_overlay/lv_buffer_sync.c": "03cab317fa9de8e71cba8bc207d2712e76c1af1e7de41b5d3d138cc1eabef1c5",
    "components/apollo_main/core_overlay/lv_display_sync.c": "9be2a2b934199dd455b5b8b00119eb0b687bcbcc8493d956dd8be07ab21480c7",
    "components/apollo_main/core_overlay/lv_display_setup.c": "2a22218b901a8dba707d05e5c6db2e9c1ce4d4ba94116b36a75056cf6de01c82",
    "components/apollo_main/core_overlay/lv_display_lock.c": "cf93aca0e218d49c93590e86e136b68780a64b36785cce3fcf869c50acce0e2c",
}
EXPECTED_DISPLAY_PORT_BYTES = 638


class ClosureError(RuntimeError):
    pass


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load(path: Path):
    spec = importlib.util.spec_from_file_location("apollo_paths_for_lvgl_display", path)
    if spec is None or spec.loader is None:
        raise ClosureError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def analyze_report(
    path_report: dict[str, Any], build_report: dict[str, Any], stock: bytes, load_base: int
) -> dict[str, Any]:
    if sum(size for _, size, _ in FUNCTIONS.values()) != EXPECTED_DISPLAY_PORT_BYTES:
        raise ClosureError("display-port stock byte census changed")

    stock_rows = []
    for symbol, (entry, size, expected_hash) in FUNCTIONS.items():
        offset = entry - load_base
        digest = _sha256(stock[offset:offset + size])
        if digest != expected_hash:
            raise ClosureError(f"stock span changed for {symbol}: {digest}")
        stock_rows.append({
            "symbol": symbol, "entry": entry, "size": size, "sha256": digest,
        })

    paths = {row["relative"]: row for row in path_report["paths"]}
    if DISPLAY_PATH not in paths or INPUT_MANAGER_PATH not in paths:
        raise ClosureError("display/input ownership path boundary changed")
    display_record = paths[DISPLAY_PATH]
    anchored = {
        row["entry"] for row in display_record.get("function_references", [])
    }
    if anchored != PATH_ANCHORED_ENTRIES:
        raise ClosureError(f"display-port path anchor set changed: {sorted(anchored)!r}")
    if display_record["root"] != "third_party" or display_record["third_party_dependency"] != "lvgl_v9.3":
        raise ClosureError("display-port retained path ownership changed")
    if paths[INPUT_MANAGER_PATH]["root"] != "platform":
        raise ClosureError("input manager is no longer a first-party platform path")

    # A third-party input *port* would be a separate vendor boundary.  Official
    # LVGL core indev sources are deliberately not classified as such.
    vendor_port_paths = [
        row["relative"] for row in path_report["paths"]
        if row["relative"].startswith("third_party\\lvgl_v9.3\\lvgl_ambiq_porting\\")
    ]
    if vendor_port_paths != [DISPLAY_PATH]:
        raise ClosureError(f"Ambiq LVGL port-path census changed: {vendor_port_paths!r}")

    sites = {
        row.get("target_function"): row
        for row in build_report["overlay"]["patched_sites"]
    }
    compiled = build_report["overlay"]["functions"]
    patch_rows = []
    for symbol, (entry, size, expected_hash) in FUNCTIONS.items():
        site = sites.get(symbol)
        function = compiled.get(symbol)
        if site is None or function is None:
            raise ClosureError(f"source replacement missing for {symbol}")
        if (
            site["runtime_address"] != entry
            or site["expected_size"] != size
            or site["expected_sha256"] != expected_hash
            or site["branch"] != "b_w"
            or site["target_address"] != build_report["overlay"]["overlay_runtime_address"] + function["offset"]
            or len(bytes.fromhex(site["replacement_hex"])) != size
        ):
            raise ClosureError(f"generated redirect metadata changed for {symbol}")
        patch_rows.append({
            "symbol": symbol,
            "stock_entry": entry,
            "stock_bytes": size,
            "compiled_target": site["target_address"],
            "compiled_bytes": function["size"],
            "redirect": site["branch"],
        })

    sources = {row["path"]: row for row in build_report["sources"]}
    for path, digest in SOURCE_PINS.items():
        row = sources.get(path)
        source = ROOT / path
        if row is None or not source.is_file():
            raise ClosureError(f"display-port source missing: {path}")
        actual = _sha256(source.read_bytes())
        if actual != digest or row["sha256"] != digest or row.get("origin", "").find("openCFW") < 0:
            raise ClosureError(f"display-port source identity changed: {path}")

    return {
        "schema_version": 1,
        "analysis_mode": "read-only; no hardware or flash operation",
        "display_port": {
            "retained_private_path": DISPLAY_PATH,
            "stock_functions": len(FUNCTIONS),
            "stock_executable_bytes": EXPECTED_DISPLAY_PORT_BYTES,
            "path_anchored_functions": len(PATH_ANCHORED_ENTRIES),
            "topology_or_pointer_closed_functions": len(FUNCTIONS) - len(PATH_ANCHORED_ENTRIES),
            "source_owned_functions": len(patch_rows),
            "functional_closure_percent": 100,
            "functions": patch_rows,
            "stock_spans": stock_rows,
        },
        "input_boundary": {
            "third_party_ambiq_input_port_paths": 0,
            "first_party_input_manager_path": INPUT_MANAGER_PATH,
            "qualification": "input transport and policy are first-party platform work, not an opaque third-party utility",
        },
        "provenance": {
            "origin": "private Ambiq/Even LVGL display integration glue",
            "version": None,
            "historical_generating_commit": None,
            "qualification": "no public source occurrence or producing commit is available; functionality is independently source-owned",
        },
        "remaining": [
            "historical private display-port source/commit provenance",
            "target display/DMA/mutex concurrency validation",
            "first-party input/display-manager reconstruction outside the third-party utility boundary",
        ],
    }


def analyze(image: Path, report: Path, corpus: Path) -> dict[str, Any]:
    path_module = _load(PATH_ANALYZER)
    path_report = path_module.analyze(image=image, corpus_root=corpus)
    stock = image.read_bytes()
    return analyze_report(
        path_report, json.loads(report.read_text()), stock, path_module.LOAD_BASE
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path)
    parser.add_argument("--component-report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--ghidra-corpus", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    path_module = _load(PATH_ANALYZER)
    image = args.image or path_module.DEFAULT_IMAGE
    result = analyze(image, args.component_report, args.ghidra_corpus)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        display = result["display_port"]
        print(
            "G2 LVGL Ambiq display-port closure: PASS "
            f"({display['source_owned_functions']}/{display['stock_functions']} functions; "
            f"{display['stock_executable_bytes']} stock bytes)"
        )
        print("third-party Ambiq input-port paths: 0")
        print("historical private producing commit: unobservable")
        print("hardware/flash operations: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
