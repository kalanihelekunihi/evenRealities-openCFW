#!/usr/bin/env python3
"""Build each R1 profile twice and record byte-for-byte reproducibility."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
EVIDENCE = PROJECT / "verification" / "reproducibility.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(project: Path, profile: str, toolchain_root: Path, *, verify: bool) -> dict[str, str]:
    variables = [f"PROFILE={profile}", f"GNU_INSTALL_ROOT={toolchain_root.as_posix().rstrip('/')}/"]
    subprocess.run(["make", "clean", *variables], cwd=project, check=True)
    subprocess.run(["make", "verify" if verify else "r1_bootloader", *variables], cwd=project, check=True)
    directory = project / "build" / profile
    return {
        name: digest(directory / name)
        for name in ("r1_bootloader.out", "r1_bootloader.hex", "r1_bootloader.bin")
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--toolchain-root", type=Path, required=True)
    args = parser.parse_args()
    results: dict[str, object] = {}
    for profile in ("captured", "hardened"):
        first = build(PROJECT, profile, args.toolchain_root.resolve(), verify=True)
        second = build(PROJECT, profile, args.toolchain_root.resolve(), verify=True)
        if first != second:
            raise SystemExit(f"non-reproducible {profile} outputs: {first} != {second}")
        manifest = json.loads(
            (PROJECT / "build" / profile / "build-manifest.json").read_text(encoding="utf-8")
        )
        results[profile] = {
            "rebuilds_match": True,
            "artifacts": first,
            "metrics": {
                key: manifest[key]
                for key in (
                    "source_objects",
                    "flash_function_addresses",
                    "text_bytes",
                    "data_bytes",
                    "bss_bytes",
                    "bootloader_bin_bytes",
                    "bootloader_used_bytes",
                    "initial_stack_pointer",
                    "reset_vector",
                    "public_key_address",
                    "signed_updates_required",
                )
            },
        }
    with tempfile.TemporaryDirectory(prefix="r1-firmware-project-") as temporary:
        relocated = Path(temporary) / "firmware-project"
        shutil.copytree(PROJECT, relocated, ignore=shutil.ignore_patterns("build", "__pycache__"))
        for profile in ("captured", "hardened"):
            relocated_hashes = build(
                relocated,
                profile,
                args.toolchain_root.resolve(),
                verify=False,
            )
            expected = results[profile]["artifacts"]
            if relocated_hashes != expected:
                raise SystemExit(
                    f"path-dependent {profile} outputs: {relocated_hashes} != {expected}"
                )
            results[profile]["relocated_rebuild_matches"] = True
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"verified reproducible captured and hardened builds; wrote {EVIDENCE}")


if __name__ == "__main__":
    main()
