#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Audit the contributor-owned Touch I2C/sensing dual-license boundary."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
TOUCH = ROOT / "components/shared/touch"
MANIFEST_DIR = TOOLS / "manifests"
NOTICE = ROOT.parent / "NOTICE"
ANALYZERS = {
    "i2c": TOOLS / "analyze_g2_touch_i2c_source.py",
    "sensing": TOOLS / "analyze_g2_touch_sensing_source.py",
}
FILES = {
    "i2c": (
        (TOUCH / "runtime_touch_i2c_protocol.c", 7314,
         "e9cbb38deb85e593de051cdbe5a27c81b50eb22c944a7b6c8c9223c1c9fdd538"),
        (TOUCH / "runtime_touch_i2c_protocol.h", 2838,
         "0eba5e33eb45e3c360409357cd811a963877378cae2080841d87de18e6f81d53"),
    ),
    "sensing": (
        (TOUCH / "runtime_touch_sensing.c", 4629,
         "30d7fd3e9c2c9d0a02b1ae4a5737cdf66a17d0f0aebab7b61531326373e9c811"),
        (TOUCH / "runtime_touch_sensing.h", 2461,
         "9fc6c523ba0fa7fa06aa6afb0a46385c326a246e1de4273732e4f8c9ca477f52"),
    ),
}
EXPECTED_ROW_DIGEST = "109b55fe659802b7377f2f64a060d909699368daef9eed53523fbbb53788e094"


class AuditError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot load {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def analyze(*, enforce_expected: bool = True) -> dict:
    notice = NOTICE.read_text()
    require("Additional MIT license grant" in notice,
            "repository additional MIT grant disappeared")
    require("To the extent that copyright in a file is held by the openCFW contributors" in notice,
            "contributor-ownership limit disappeared")
    require("grant does not apply to material derived from another GPL" in notice,
            "upstream/GPL-derived exclusion disappeared")

    rows = []
    for component, paths in FILES.items():
        source_text = paths[0][0].read_text()
        require("Clean-room" in source_text,
                f"{component} clean-room provenance marker disappeared")
        file_rows = []
        for path, expected_size, expected_digest in paths:
            data = path.read_bytes()
            require(len(data) == expected_size, f"{path.name} size changed")
            require(sha256(data) == expected_digest, f"{path.name} digest changed")
            require("SPDX-License-Identifier: MIT OR GPL-3.0-only" in data.decode(),
                    f"{path.name} dual-license SPDX changed")
            file_rows.append({
                "path": str(path.relative_to(ROOT)), "bytes": len(data),
                "sha256": expected_digest,
            })
        audit = _load(ANALYZERS[component], f"touch_license_{component}").audit()
        require(audit["license"] == "MIT OR GPL-3.0-only",
                f"{component} source audit license changed")
        rows.append({
            "component": component,
            "license": "MIT OR GPL-3.0-only",
            "mit_basis": "repository additional grant for contributor-owned original work",
            "gpl_option_preserved": True,
            "upstream_or_gpl_derived_material_relicensed": False,
            "provider_licenses_preserved": True,
            "files": file_rows,
            "evidence": "project clean-room provenance marker plus exact source/header pins; no third-party source body admitted",
        })

    row_digest = sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode())
    if enforce_expected:
        require(row_digest == EXPECTED_ROW_DIGEST,
                f"license readiness rows changed: {row_digest}")
    return {
        "schema_version": 1,
        "component": "G2 Touch project-source license readiness",
        "analysis_mode": "offline license/provenance/source-hash audit; no hardware or firmware operation",
        "metrics": {
            "dual_licensed_project_components": len(rows),
            "dual_licensed_project_files": sum(len(row["files"]) for row in rows),
            "upstream_or_gpl_derived_files_relicensed": 0,
            "provider_license_changes": 0,
            "row_digest": row_digest,
        },
        "rows": rows,
        "notice": str(NOTICE.relative_to(ROOT.parent)),
        "decision": "MIT option supported for these contributor-owned clean-room pairs; GPL option retained; upstream/provider/evidence terms unchanged",
    }


def write_manifests(result: dict) -> list[Path]:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    table = MANIFEST_DIR / "g2-touch-project-license-readiness.tsv"
    with table.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["component", "license", "files", "mit_basis",
                         "gpl_option_preserved", "upstream_material_relicensed",
                         "provider_licenses_preserved", "evidence"])
        for row in result["rows"]:
            writer.writerow([
                row["component"], row["license"],
                ",".join(item["path"] for item in row["files"]), row["mit_basis"],
                str(row["gpl_option_preserved"]).lower(),
                str(row["upstream_or_gpl_derived_material_relicensed"]).lower(),
                str(row["provider_licenses_preserved"]).lower(), row["evidence"],
            ])
    summary = MANIFEST_DIR / "g2-touch-project-license-readiness-summary.json"
    summary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return [table, summary]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-manifests", action="store_true")
    args = parser.parse_args()
    result = analyze()
    if args.write_manifests:
        for path in write_manifests(result):
            print(f"wrote {path.relative_to(ROOT)}")
    print(result["decision"])
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Touch project license audit failed: {exc}") from exc
