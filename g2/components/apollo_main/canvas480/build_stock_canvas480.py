#!/usr/bin/env python3
"""Build the reviewed canvas480 g2flash source patch on its exact stock base.

This tool only creates local artifacts. It never downloads firmware and never flashes glasses.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


G2FLASH_COMMIT = "d5eb48dd9dcda4cc630458ec365bc546036678c2"
STOCK_SHA256 = "f4dfb0b49ad3de3c2daf17f8a27a157c3dc98411d6a0d3ab2cfd0918f41b9afa"
PATCH_NAME = "g2flash-canvas480.patch"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(arguments: list[str], cwd: Path | None = None) -> None:
    subprocess.run(arguments, cwd=cwd, check=True)


def output_paths(output: Path, patch_json: Path | None) -> tuple[Path, Path, Path]:
    generated_json = patch_json or output.with_name(output.stem + ".patches.json")
    manifest = output.with_name(output.stem + ".manifest.json")
    return output, generated_json, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--g2flash", required=True, type=Path, help="clean g2flash checkout")
    parser.add_argument("--stock", required=True, type=Path, help="stock g2_2.2.6.10.bin")
    parser.add_argument("--output", required=True, type=Path, help="patched firmware output")
    parser.add_argument("--patch-json", type=Path, help="generated replayable patch JSON")
    parser.add_argument("--force", action="store_true", help="replace existing output artifacts")
    args = parser.parse_args()

    g2flash = args.g2flash.expanduser().resolve()
    stock = args.stock.expanduser().resolve()
    output, patch_json, manifest = output_paths(
        args.output.expanduser().resolve(),
        args.patch_json.expanduser().resolve() if args.patch_json else None,
    )
    source_patch = Path(__file__).resolve().with_name(PATCH_NAME)

    if not g2flash.is_dir() or not (g2flash / ".git").exists():
        parser.error(f"--g2flash is not a git checkout: {g2flash}")
    if not stock.is_file():
        parser.error(f"--stock does not exist: {stock}")
    if sha256(stock) != STOCK_SHA256:
        parser.error("--stock is not the exact supported g2_2.2.6.10 base (SHA-256 mismatch)")
    head = subprocess.check_output(
        ["git", "-C", str(g2flash), "rev-parse", "HEAD"], text=True
    ).strip()
    if head != G2FLASH_COMMIT:
        parser.error(f"g2flash must be checked out at {G2FLASH_COMMIT}; found {head}")

    artifacts = (output, patch_json, manifest)
    if not args.force:
        existing = [str(path) for path in artifacts if path.exists()]
        if existing:
            parser.error("refusing to overwrite existing artifact(s): " + ", ".join(existing))
    for path in artifacts:
        path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="sybilsight-canvas480-") as temp_name:
        temp = Path(temp_name)
        patched_checkout = temp / "g2flash"
        temporary_json = temp / "canvas480-patches.json"
        run([
            "git", "clone", "--quiet", "--no-hardlinks", "--no-checkout",
            str(g2flash), str(patched_checkout),
        ])
        run(["git", "checkout", "--quiet", "--detach", G2FLASH_COMMIT], cwd=patched_checkout)
        # The reviewed patch intentionally uses zero context so storing a patch-inside-this-git
        # tree introduces no context-only whitespace lines that fail the outer diff check.
        run([
            "git", "apply", "--unidiff-zero", "--check", str(source_patch)
        ], cwd=patched_checkout)
        run([
            "git", "apply", "--unidiff-zero", str(source_patch)
        ], cwd=patched_checkout)
        run([
            sys.executable,
            str(patched_checkout / "patches" / "gen_patches.py"),
            str(stock),
            str(temporary_json),
        ], cwd=patched_checkout)

        spec = json.loads(temporary_json.read_text(encoding="utf-8"))
        if spec.get("base_sha256") != STOCK_SHA256:
            raise RuntimeError("generated patch JSON lost the verified stock-base identity")
        run([
            sys.executable,
            str(patched_checkout / "patches" / "apply_patches.py"),
            str(stock),
            str(temporary_json),
            str(output),
        ], cwd=patched_checkout)
        if sha256(output) != spec.get("output_sha256"):
            raise RuntimeError("output firmware hash does not match generated patch JSON")
        shutil.copy2(temporary_json, patch_json)

    manifest.write_text(json.dumps({
        "format": "sybilsight-g2-canvas480-build-v1",
        "stock_sha256": STOCK_SHA256,
        "g2flash_commit": G2FLASH_COMMIT,
        "source_patch": PATCH_NAME,
        "patch_json": patch_json.name,
        "output": output.name,
        "output_sha256": sha256(output),
        "flashed": False,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"built {output}")
    print(f"sha256 {sha256(output)}")
    print("not flashed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
