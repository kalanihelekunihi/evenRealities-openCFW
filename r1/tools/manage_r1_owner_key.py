#!/usr/bin/env python3
"""Generate and verify the local R1 owner-signing recovery key.

The encrypted PKCS#8 private key is deliberately duplicated into SybilSight and
the local APIs repository.  Its random passphrase is stored in macOS Keychain;
the passphrase is never printed or written to either repository.
"""

from __future__ import annotations

import argparse
import base64
import getpass
import hashlib
import json
import os
import secrets
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


KEYCHAIN_SERVICE = "com.sybilsight.r1-owner-signing"
PRIVATE_NAME = "r1-owner-private.key"
PUBLIC_NAME = "r1-owner-public.pem"
RAW_PUBLIC_NAME = "r1-owner-public-x-y-le.bin"
MANIFEST_NAME = "manifest.json"


def destinations(repo_root: Path, apis_root: Path) -> tuple[Path, Path]:
    return (
        repo_root / "config" / "r1-owner-signing",
        apis_root / "secrets" / "r1-owner-signing",
    )


def keychain_account() -> str:
    return getpass.getuser()


def keychain_store(passphrase: str) -> None:
    subprocess.run(
        [
            "security",
            "add-generic-password",
            "-U",
            "-a",
            keychain_account(),
            "-s",
            KEYCHAIN_SERVICE,
            "-w",
            passphrase,
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def keychain_load() -> str:
    completed = subprocess.run(
        [
            "security",
            "find-generic-password",
            "-a",
            keychain_account(),
            "-s",
            KEYCHAIN_SERVICE,
            "-w",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.rstrip("\n")


def raw_public_little_endian(public_key: ec.EllipticCurvePublicKey) -> bytes:
    numbers = public_key.public_numbers()
    return numbers.x.to_bytes(32, "little") + numbers.y.to_bytes(32, "little")


def write_private(path: Path, data: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(data)
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def write_public(path: Path, data: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(data)
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def generate(repo_root: Path, apis_root: Path) -> dict[str, object]:
    target_directories = destinations(repo_root, apis_root)
    target_files = [
        directory / name
        for directory in target_directories
        for name in (PRIVATE_NAME, PUBLIC_NAME, RAW_PUBLIC_NAME, MANIFEST_NAME)
    ]
    existing = [str(path) for path in target_files if path.exists()]
    if existing:
        raise SystemExit("refusing to overwrite owner-key material: " + ", ".join(existing))

    private_key = ec.generate_private_key(ec.SECP256R1())
    passphrase = base64.urlsafe_b64encode(secrets.token_bytes(48)).decode("ascii")
    encrypted_private = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.BestAvailableEncryption(passphrase.encode("ascii")),
    )
    public_pem = private_key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    raw_public = raw_public_little_endian(private_key.public_key())
    created = datetime.now(timezone.utc).isoformat()
    manifest = {
        "schema": 1,
        "created_utc": created,
        "curve": "secp256r1",
        "private_key_format": "encrypted PKCS#8 PEM",
        "private_key_encrypted": True,
        "private_key_git_policy": "ignored; never commit",
        "passphrase_store": f"macOS Keychain service {KEYCHAIN_SERVICE}",
        "public_key_format": "64-byte little-endian X || Y",
        "public_key_hex": raw_public.hex(),
        "public_key_sha256": hashlib.sha256(raw_public).hexdigest(),
        "public_pem_sha256": hashlib.sha256(public_pem).hexdigest(),
        "private_ciphertext_sha256": hashlib.sha256(encrypted_private).hexdigest(),
    }

    created_paths: list[Path] = []
    try:
        keychain_store(passphrase)
        for directory in target_directories:
            directory.mkdir(parents=True, exist_ok=True)
            private_path = directory / PRIVATE_NAME
            public_path = directory / PUBLIC_NAME
            raw_path = directory / RAW_PUBLIC_NAME
            manifest_path = directory / MANIFEST_NAME
            write_private(private_path, encrypted_private)
            created_paths.append(private_path)
            write_public(public_path, public_pem)
            created_paths.append(public_path)
            write_public(raw_path, raw_public)
            created_paths.append(raw_path)
            write_public(
                manifest_path,
                (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8"),
            )
            created_paths.append(manifest_path)
    except BaseException:
        for path in created_paths:
            path.unlink(missing_ok=True)
        raise

    return {
        "generated": True,
        "public_key_sha256": manifest["public_key_sha256"],
        "destinations": [str(path) for path in target_directories],
        "private_key_encrypted": True,
        "passphrase_written_to_repositories": False,
    }


def verify(repo_root: Path, apis_root: Path) -> dict[str, object]:
    passphrase = keychain_load().encode("ascii")
    target_directories = destinations(repo_root, apis_root)
    copies: list[dict[str, object]] = []
    reference_public: bytes | None = None
    reference_private_ciphertext: bytes | None = None

    for directory in target_directories:
        private_path = directory / PRIVATE_NAME
        public_path = directory / PUBLIC_NAME
        raw_path = directory / RAW_PUBLIC_NAME
        manifest_path = directory / MANIFEST_NAME
        private_ciphertext = private_path.read_bytes()
        private_key = serialization.load_pem_private_key(
            private_ciphertext,
            password=passphrase,
        )
        if not isinstance(private_key, ec.EllipticCurvePrivateKey) or not isinstance(
            private_key.curve, ec.SECP256R1
        ):
            raise SystemExit(f"unexpected private-key type in {private_path}")
        public_pem = public_path.read_bytes()
        public_key = serialization.load_pem_public_key(public_pem)
        if not isinstance(public_key, ec.EllipticCurvePublicKey):
            raise SystemExit(f"unexpected public-key type in {public_path}")
        raw_public = raw_public_little_endian(public_key)
        if raw_path.read_bytes() != raw_public:
            raise SystemExit(f"raw public key mismatch in {directory}")
        if private_key.public_key().public_numbers() != public_key.public_numbers():
            raise SystemExit(f"private/public key mismatch in {directory}")
        manifest = json.loads(manifest_path.read_text())
        if manifest["public_key_sha256"] != hashlib.sha256(raw_public).hexdigest():
            raise SystemExit(f"manifest public-key mismatch in {directory}")
        if manifest["private_ciphertext_sha256"] != hashlib.sha256(
            private_ciphertext
        ).hexdigest():
            raise SystemExit(f"manifest private-key ciphertext mismatch in {directory}")
        mode = private_path.stat().st_mode & 0o777
        if mode != 0o600:
            raise SystemExit(f"private key permissions are {mode:o}, expected 600: {private_path}")
        if reference_public is None:
            reference_public = raw_public
            reference_private_ciphertext = private_ciphertext
        elif raw_public != reference_public or private_ciphertext != reference_private_ciphertext:
            raise SystemExit("repository key copies are not byte-identical")
        copies.append(
            {
                "directory": str(directory),
                "private_mode": f"{mode:04o}",
                "public_key_sha256": hashlib.sha256(raw_public).hexdigest(),
                "private_ciphertext_sha256": hashlib.sha256(private_ciphertext).hexdigest(),
            }
        )

    assert reference_public is not None
    return {
        "verified": True,
        "copies_identical": True,
        "public_key_sha256": hashlib.sha256(reference_public).hexdigest(),
        "copies": copies,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("generate", "verify"))
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument(
        "--apis-root",
        type=Path,
        default=Path.home() / "Repo" / "apis",
    )
    args = parser.parse_args()
    action = generate if args.command == "generate" else verify
    print(json.dumps(action(args.repo_root.resolve(), args.apis_root.expanduser().resolve()), indent=2))


if __name__ == "__main__":
    main()
