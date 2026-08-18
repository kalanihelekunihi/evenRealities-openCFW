#!/usr/bin/env python3
"""Build and package the source-built Zephyr/MCUboot OpenR1 target."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import getpass
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Iterator

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


PROJECT = Path(__file__).resolve().parents[1]
APPLICATION = PROJECT / "platform" / "nrf52840" / "zephyr"
RECOVERY_MODULE = APPLICATION / "recovery_module"


def executable_path(value: str) -> Path:
    candidate = Path(value).expanduser()
    if candidate.parent != Path(".") or candidate.is_absolute():
        resolved = candidate.resolve()
    else:
        found = shutil.which(value)
        if found is None:
            raise ValueError(f"west executable not found: {value}")
        resolved = Path(found).resolve()
    if not resolved.is_file():
        raise ValueError(f"west executable is not a file: {resolved}")
    return resolved


def build_environment(west: Path, workspace: Path, toolchain: Path) -> dict[str, str]:
    zephyr = workspace / "zephyr"
    compiler = toolchain / "bin" / "arm-none-eabi-gcc"
    if not (zephyr / "CMakeLists.txt").is_file():
        raise ValueError(f"Zephyr source tree not found: {zephyr}")
    if not compiler.is_file():
        raise ValueError(f"GNU Arm Embedded toolchain not found: {compiler}")
    environment = os.environ.copy()
    prefixes = [os.fspath(west.parent), os.fspath(toolchain / "bin")]
    environment["PATH"] = os.pathsep.join(prefixes + [environment.get("PATH", "")])
    environment["ZEPHYR_BASE"] = os.fspath(zephyr)
    environment["ZEPHYR_TOOLCHAIN_VARIANT"] = "gnuarmemb"
    environment["GNUARMEMB_TOOLCHAIN_PATH"] = os.fspath(toolchain)

    # Sysbuild launches child-image Python processes independently. Preserve
    # the west virtual environment so those children see west's dependencies.
    virtual_environment = west.parent.parent
    if (virtual_environment / "pyvenv.cfg").is_file():
        environment["VIRTUAL_ENV"] = os.fspath(virtual_environment)
    return environment


@contextmanager
def compatible_gdb_probe(toolchain: Path) -> Iterator[None]:
    """Avoid a configure-only hang in the pinned 2020 macOS gdb-py.

    Zephyr probes ``arm-none-eabi-gdb-py --configuration`` while locating GNU
    binutils.  That x86_64 executable can enter an uninterruptible wait under
    current Apple Silicon/Rosetta, although GCC, ld, objcopy, and every tool
    used to build the image work normally.  GDB is not a firmware build input.

    Temporarily hiding only gdb-py makes Zephyr select the non-Python GDB
    fallback without executing it.  The exact file is restored in ``finally``;
    the advisory lock serializes concurrent OpenR1 builds, and an interrupted
    prior run is recovered when only the backup remains.
    """
    gdb_py = toolchain / "bin" / "arm-none-eabi-gdb-py"
    if sys.platform != "darwin" or not gdb_py.parent.is_dir():
        yield
        return

    import fcntl

    identity = hashlib.sha256(os.fspath(gdb_py).encode()).hexdigest()[:16]
    lock_path = Path(tempfile.gettempdir()) / f"openr1-gdb-probe-{identity}.lock"
    backup = gdb_py.with_name(gdb_py.name + ".openr1-disabled")
    with lock_path.open("a+b") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        if backup.exists() and not gdb_py.exists():
            backup.rename(gdb_py)
        if backup.exists():
            raise RuntimeError(
                f"refusing to overwrite existing GDB probe backup: {backup}")
        if not gdb_py.is_file():
            yield
            return
        gdb_py.rename(backup)
        try:
            yield
        finally:
            if gdb_py.exists():
                raise RuntimeError(
                    f"GDB probe path unexpectedly recreated during build: {gdb_py}")
            backup.rename(gdb_py)


@contextmanager
def resolved_signing_key(args: argparse.Namespace) -> Iterator[Path | None]:
    if args.signing_key is not None:
        signing_key = args.signing_key.expanduser().resolve()
        if not signing_key.is_file():
            raise ValueError(f"signing key not found: {signing_key}")
        yield signing_key
        return
    if args.encrypted_signing_key is None:
        yield None
        return

    encrypted = args.encrypted_signing_key.expanduser().resolve()
    if not encrypted.is_file():
        raise ValueError(f"encrypted signing key not found: {encrypted}")
    completed = subprocess.run(
        [
            "security", "find-generic-password",
            "-a", args.keychain_account,
            "-s", args.keychain_service,
            "-w",
        ],
        check=True,
        capture_output=True,
    )
    password = completed.stdout.rstrip(b"\n")
    private = serialization.load_pem_private_key(
        encrypted.read_bytes(), password=password)
    if not isinstance(private, ec.EllipticCurvePrivateKey) or not \
       isinstance(private.curve, ec.SECP256R1):
        raise ValueError("owner signing key is not ECDSA P-256")
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
                prefix="openr1-owner-mcuboot-", suffix=".pem",
                delete=False) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(private.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption()))
        temporary_path.chmod(0o600)
        yield temporary_path
    finally:
        password = b""
        private = None
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--toolchain", type=Path, required=True)
    parser.add_argument("--bma456-root", type=Path, required=True)
    parser.add_argument("--lis2dw12-root", type=Path, required=True)
    parser.add_argument("--st25dvxxkc-root", type=Path, required=True)
    parser.add_argument("--flashdb-root", type=Path, required=True)
    parser.add_argument("--goodix-democode-root", type=Path, required=True)
    parser.add_argument("--west", default="west")
    parser.add_argument("--build-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    signing = parser.add_mutually_exclusive_group()
    signing.add_argument("--signing-key", type=Path)
    signing.add_argument("--encrypted-signing-key", type=Path)
    parser.add_argument(
        "--keychain-service", default="com.sybilsight.r1-owner-signing")
    parser.add_argument("--keychain-account", default=getpass.getuser())
    parser.add_argument("--build-only", action="store_true")
    args = parser.parse_args()
    if args.build_only and args.output is not None:
        parser.error("--output cannot be combined with --build-only")
    if not args.build_only and args.output is None:
        parser.error("--output is required unless --build-only is used")

    workspace = args.workspace.expanduser().resolve()
    toolchain = args.toolchain.expanduser().resolve()
    build = args.build_dir.expanduser().resolve()
    bma456 = args.bma456_root.expanduser().resolve()
    lis2dw12 = args.lis2dw12_root.expanduser().resolve()
    st25dvxxkc = args.st25dvxxkc_root.expanduser().resolve()
    flashdb = args.flashdb_root.expanduser().resolve()
    goodix_democode = args.goodix_democode_root.expanduser().resolve()
    if not (bma456 / "bma456w.c").is_file():
        raise ValueError(f"Bosch BMA456 source root not found: {bma456}")
    if not (lis2dw12 / "lis2dw12_reg.c").is_file():
        raise ValueError(f"ST LIS2DW12 source root not found: {lis2dw12}")
    if not (st25dvxxkc / "st25dvxxkc_reg.c").is_file():
        raise ValueError(f"ST25DVxxKC source root not found: {st25dvxxkc}")
    if not (flashdb / "src" / "fdb_tsdb.c").is_file() or not \
       (flashdb / "port" / "fal" / "src" / "fal_partition.c").is_file():
        raise ValueError(f"FlashDB/FAL source root not found: {flashdb}")
    if not (goodix_democode / "LICENSE").is_file() or not \
       (goodix_democode / "demo_code" / "demo_kernel_code" / "kernel" /
        "gh_demo.c").is_file():
        raise ValueError(f"Goodix GH3X2X democode root not found: {goodix_democode}")
    west = executable_path(args.west)
    environment = build_environment(west, workspace, toolchain)
    command = [
        os.fspath(west), "build", "-p", "always", "--sysbuild",
        "-b", "openr1_nrf52840", os.fspath(APPLICATION),
        "-d", os.fspath(build), "--",
        f"-DBOARD_ROOT={APPLICATION}",
        f"-DOPENR1_BMA456_ROOT={bma456}",
        f"-DOPENR1_LIS2DW12_ROOT={lis2dw12}",
        f"-DOPENR1_ST25DVXXKC_ROOT={st25dvxxkc}",
        f"-DOPENR1_FLASHDB_ROOT={flashdb}",
        f"-DOPENR1_GOODIX_DEMOCODE_ROOT={goodix_democode}",
        f"-DEXTRA_ZEPHYR_MODULES={RECOVERY_MODULE}",
    ]
    with resolved_signing_key(args) as signing_key, \
            compatible_gdb_probe(toolchain):
        if signing_key is not None:
            # This sysbuild setting is a Kconfig string. The quote characters
            # must reach CMake (subprocess has no shell layer to add them).
            command.append(
                f'-DSB_CONFIG_BOOT_SIGNATURE_KEY_FILE="{signing_key}"')
        subprocess.run(command, check=True, env=environment)
        if args.build_only:
            print(f"openR1 source-built Zephyr images: {build}")
            return

        subprocess.run([
            sys.executable,
            os.fspath(PROJECT / "tools" / "package_zephyr_bundle.py"),
            "--build-dir", os.fspath(build),
            "--zephyr-workspace", os.fspath(workspace),
            "--bma456-root", os.fspath(bma456),
            "--lis2dw12-root", os.fspath(lis2dw12),
            "--st25dvxxkc-root", os.fspath(st25dvxxkc),
            "--flashdb-root", os.fspath(flashdb),
            "--goodix-democode-root", os.fspath(goodix_democode),
            "--output", os.fspath(args.output.expanduser().resolve()),
        ], check=True, env=environment)
        subprocess.run([
            sys.executable,
            os.fspath(PROJECT / "tools" / "verify_zephyr_bundle.py"),
            os.fspath(args.output.expanduser().resolve()),
        ], check=True, env=environment)


if __name__ == "__main__":
    main()
