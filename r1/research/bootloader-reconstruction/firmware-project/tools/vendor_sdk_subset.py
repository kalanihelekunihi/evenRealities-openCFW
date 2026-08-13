#!/usr/bin/env python3
"""Create or verify the minimal licensed nRF5 SDK subset used by the R1 target."""

from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
VENDOR_ROOT = PROJECT / "vendor" / "nrf5-sdk"
FILE_LIST = PROJECT / "vendor" / "vendor-files.txt"
HASH_LIST = PROJECT / "vendor" / "vendor-sha256.txt"

EXTRAS = {
    "components/softdevice/s140/hex/s140_nrf52_7.2.0_softdevice.hex",
    "components/softdevice/s140/hex/s140_nrf52_7.2.0_licence-agreement.txt",
    "components/toolchain/gcc/Makefile.common",
    "components/toolchain/gcc/Makefile.posix",
    "components/toolchain/gcc/dump.mk",
    "documentation/licenses.txt",
    "documentation/nRF5_Nordic_license.txt",
    "examples/dfu/secure_bootloader/pca10056_s140_ble/armgcc/secure_bootloader_gcc_nrf52.ld",
    "external/nano-pb/LICENSE.txt",
    "external/nrf_cc310_bl/license.txt",
    "external/nrf_cc310_bl/lib/cortex-m4/hard-float/libnrf_cc310_bl_0.9.13.a",
    "external/nrf_oberon/license.txt",
    "external/nrf_oberon/lib/cortex-m4/hard-float/liboberon_3.0.8.a",
    "license.txt",
    "modules/nrfx/LICENSE",
    "modules/nrfx/mdk/nrf_common.ld",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_dependency_files(sdk_root: Path, dependency_dir: Path) -> set[str]:
    armgcc = sdk_root / "examples/dfu/secure_bootloader/pca10056_s140_ble/armgcc"
    result: set[str] = set(EXTRAS)
    for dependency in sorted(dependency_dir.glob("*.d")):
        text = dependency.read_text(encoding="utf-8", errors="ignore").replace("\\\n", " ")
        for token in text.split():
            token = token.rstrip(":")
            candidate = (armgcc / token).resolve() if not token.startswith("/") else Path(token).resolve()
            try:
                relative = candidate.relative_to(sdk_root.resolve())
            except ValueError:
                continue
            if candidate.is_file() and candidate.suffix in {".c", ".h", ".S"}:
                result.add(relative.as_posix())
    result.discard("examples/dfu/dfu_public_key.c")
    return result


def load_file_list() -> list[str]:
    if not FILE_LIST.is_file():
        raise SystemExit(f"missing vendor file list: {FILE_LIST}")
    return [line for line in FILE_LIST.read_text(encoding="utf-8").splitlines() if line]


def verify() -> None:
    expected: dict[str, str] = {}
    for line in HASH_LIST.read_text(encoding="utf-8").splitlines():
        checksum, relative = line.split("  ", 1)
        expected[relative] = checksum
    listed = load_file_list()
    if sorted(expected) != sorted(listed):
        raise SystemExit("vendor file and hash manifests disagree")
    for relative in listed:
        path = VENDOR_ROOT / relative
        if not path.is_file():
            raise SystemExit(f"missing vendored SDK file: {relative}")
        actual = digest(path)
        if actual != expected[relative]:
            raise SystemExit(f"vendored SDK hash mismatch: {relative}")
    actual_files = sorted(
        path.relative_to(VENDOR_ROOT).as_posix()
        for path in VENDOR_ROOT.rglob("*")
        if path.is_file()
    )
    if actual_files != sorted(listed):
        extras = sorted(set(actual_files) - set(listed))
        raise SystemExit(f"unmanifested vendored SDK file: {extras[0] if extras else 'unknown'}")
    print(f"verified {len(listed)} hash-pinned Nordic/third-party dependency files")


def create(sdk_root: Path, dependency_dir: Path | None) -> None:
    if dependency_dir is not None:
        files = sorted(parse_dependency_files(sdk_root, dependency_dir))
    elif FILE_LIST.is_file():
        files = load_file_list()
    else:
        raise SystemExit("use --dependency-dir for initial manifest creation")

    missing = [relative for relative in files if not (sdk_root / relative).is_file()]
    if missing:
        raise SystemExit(f"SDK is missing {len(missing)} required files; first: {missing[0]}")

    VENDOR_ROOT.mkdir(parents=True, exist_ok=True)
    for relative in files:
        source = sdk_root / relative
        destination = VENDOR_ROOT / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    FILE_LIST.parent.mkdir(parents=True, exist_ok=True)
    FILE_LIST.write_text("".join(f"{relative}\n" for relative in files), encoding="utf-8")
    HASH_LIST.write_text(
        "".join(f"{digest(VENDOR_ROOT / relative)}  {relative}\n" for relative in files),
        encoding="utf-8",
    )
    verify()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sdk-root", type=Path)
    parser.add_argument("--dependency-dir", type=Path)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if args.verify_only:
        verify()
        return
    if args.sdk_root is None:
        parser.error("--sdk-root is required unless --verify-only is used")
    create(args.sdk_root.resolve(), args.dependency_dir.resolve() if args.dependency_dir else None)


if __name__ == "__main__":
    main()
