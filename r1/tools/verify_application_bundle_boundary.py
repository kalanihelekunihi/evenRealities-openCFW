#!/usr/bin/env python3
"""Verify that the distributable DFU payload contains only the built application."""

from __future__ import annotations

import importlib.util
import json
import re
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SDK_MAKEFILE = ROOT / "platform/nrf52840/sdk/Makefile"
SIGNER = ROOT / "tools/sign_r1_firmware.py"
EXPECTED_ENTRIES = {"application.bin", "application.dat", "manifest.json"}


def load_signer():
    spec = importlib.util.spec_from_file_location("openr1_signer", SIGNER)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load owner DFU packager")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    makefile = SDK_MAKEFILE.read_text()
    forbidden = re.findall(
        r"(?im)(?:^|[\s/])[^\s\\]+\.(?:a|bin|hex|zip|lib|so|dylib)(?=\s|\\|$)",
        makefile,
    )
    if forbidden:
        raise AssertionError(f"opaque/blob SDK link inputs found: {forbidden}")
    if "s140_nrf52_7.2.0_softdevice.hex" in makefile:
        raise AssertionError("SDK application build imports a SoftDevice image")
    if "LIB_FILES += -lc -lnosys -lm" not in makefile:
        raise AssertionError("unexpected compiler-runtime library boundary")

    signer = load_signer()
    if signer.DEFAULT_SD_REQ != 0x0100:
        raise AssertionError("owner bundle SoftDevice ABI requirement changed")
    application = bytes(range(256)) * 3
    packet = b"transparent-boundary-test-packet"
    with tempfile.TemporaryDirectory() as directory:
        archive_path = Path(directory) / "application.zip"
        signer.write_package(archive_path, application, packet)
        with zipfile.ZipFile(archive_path) as archive:
            names = set(archive.namelist())
            if names != EXPECTED_ENTRIES:
                raise AssertionError(f"unexpected DFU members: {sorted(names)}")
            if archive.read("application.bin") != application:
                raise AssertionError("DFU application payload changed")
            if archive.read("application.dat") != packet:
                raise AssertionError("DFU init packet changed")
            manifest = json.loads(archive.read("manifest.json"))
    if set(manifest.get("manifest", {})) != {"application"}:
        raise AssertionError("DFU manifest includes a non-application image")

    print(
        "openR1 application bundle boundary verified: source-linked application only; "
        "no SoftDevice or bootloader image member; requires preinstalled S140 ABI 0x0100"
    )


if __name__ == "__main__":
    main()
