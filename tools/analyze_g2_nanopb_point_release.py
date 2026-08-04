#!/usr/bin/env python3
"""Fail-closed nanopb 0.4.4--0.4.9 point-release audit for G2.

The default audit is read-only and authenticates the official Apollo-main
image before inspecting two release-discriminating instruction sequences.
Optional modes authenticate an existing checkout of the official nanopb
repository and reproduce the 0.4.7/0.4.8/0.4.9 object-code collision.  The
tool has no device, debugger, serial, or flash-writing path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "blobs" / "official" / "g2-2.2.6.10" / "ota_s200_firmware_ota.bin"
MAIN_SIZE = 3_523_396
MAIN_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
LOAD_BASE = 0x00437FE0

NANOPB_REGION = (0x0048F000, 0x00491400)
PB_READ = (0x0048F3BE, 0x0048F454)
PB_DECODE_VARINT = (0x0048F5B8, 0x0048F628)
PINNED_REGION_SHA256 = {
    "nanopb_region": "ff42ff15a4574a6485b8b3e16de986679f059f2358d5d354b29f713760f43ea2",
    "pb_read": "69aecb900c749fd98bd2d05e2229e9a3d6829bd36f3e393f624e3579a9b4af7f",
    "pb_decode_varint": "f93d678981f92603982c9afc6c6f9976ca14d1a7a7e0bfc949d3ff73f2791ff2",
}

# IAR Thumb bytes at 0x0048F43C implement:
#     if (stream->bytes_left < count) stream->bytes_left = 0;
#     else stream->bytes_left -= count;
# This source change first appears in the pristine nanopb-0.4.7 tag.
PB_READ_SATURATING_CLAMP = bytes.fromhex(
    "a868"      # ldr  r0, [r5, #8]
    "a042"      # cmp  r0, r4
    "02d2"      # bhs  subtraction
    "0020"      # movs r0, #0
    "a860"      # str  r0, [r5, #8]
    "02e0"      # b    complete
    "a868"      # ldr  r0, [r5, #8]
    "041b"      # subs r4, r0, r4
    "ac60"      # str  r4, [r5, #8]
)
PB_READ_SATURATING_CLAMP_ADDRESS = 0x0048F43C

# The 64-bit guard first appears in pristine nanopb-0.4.6, correcting the
# older audit's weak 0.4.4 attribution.  It corroborates, but does not improve,
# the stronger pb_read lower bound.
PB_VARINT_63BIT_GUARD = bytes.fromhex(
    "b8f13f0f"  # cmp.w r8, #63
    "04d3"      # blo   accept
    "9df80000"  # ldrb.w r0, [sp]
    "10f0fe0f"  # tst.w r0, #0xfe
)
PB_VARINT_63BIT_GUARD_ADDRESS = 0x0048F5D4

UPSTREAM_REPOSITORY = "https://github.com/nanopb/nanopb.git"
UPSTREAM_LICENSE = "Zlib"
UPSTREAM_LICENSE_SHA256 = "e2f2fc8fe3faa7dcb09dbe995db48c6ec5c1f72705db915101e4a83fed44f66d"
UPSTREAM_FILES = (
    "pb.h",
    "pb_common.c",
    "pb_common.h",
    "pb_decode.c",
    "pb_decode.h",
    "pb_encode.c",
    "pb_encode.h",
    "LICENSE.txt",
)

# Git object identities and SHA-256 file identities from the official tags.
# Both tag spellings (0.4.x and nanopb-0.4.x) resolve to these same commits.
UPSTREAM_RELEASES: dict[str, dict[str, Any]] = {
    "0.4.4": {
        "commit": "2b48a361786dfb1f63d229840217a93aae064667",
        "tree": "5483fd3823bda3c30671d85a8919633f98309e1e",
        "date": "2020-11-25T14:19:36+02:00",
        "files": {
            "pb.h": "5bc0b5c1b3fecdef88fb79869292f8ff39442f6a5f5a30a79b35299b64bb3d5a",
            "pb_common.c": "8d2ec28baaaf2b7a5e90e4cb2fa9700d21cef7f826f051a637c30b7a1e6a0516",
            "pb_common.h": "6495a691aca68d6973f2274b5dd54b74fbb57f6b019c45fff255a857fe1abcfd",
            "pb_decode.c": "3d1088312350c64be8899e0c8c0d27c670b13124a08daf865441b8e4f0874619",
            "pb_decode.h": "ddd9fe7c027f4a9cdb6cb4c74959eb916dd19a06a0ff48909c3612d313e0b445",
            "pb_encode.c": "531fed13672bcaa0e8fca11371510508345a4c53efdf216cf4ff3e12933b3b6b",
            "pb_encode.h": "f9dacdb1dce5c6998234f2c7c6677ad03d36fbb11efa8d8676581fc868d862e7",
            "LICENSE.txt": UPSTREAM_LICENSE_SHA256,
        },
    },
    "0.4.5": {
        "commit": "c9124132a604047d0ef97a09c0e99cd9bed2c818",
        "tree": "27e977c6c2e809a42fa07692e72d6f3dbfee78d0",
        "date": "2021-03-22T16:44:15+02:00",
        "files": {
            "pb.h": "0ce6ebe57b88e10231dff1fd8025422f43c6d0ac5f21fd484f0e74540e157691",
            "pb_common.c": "8d2ec28baaaf2b7a5e90e4cb2fa9700d21cef7f826f051a637c30b7a1e6a0516",
            "pb_common.h": "6495a691aca68d6973f2274b5dd54b74fbb57f6b019c45fff255a857fe1abcfd",
            "pb_decode.c": "9549975a276ae36f65f5523d30cf204118a4a1016a5adf3db25bb78caf05eb21",
            "pb_decode.h": "ddd9fe7c027f4a9cdb6cb4c74959eb916dd19a06a0ff48909c3612d313e0b445",
            "pb_encode.c": "531fed13672bcaa0e8fca11371510508345a4c53efdf216cf4ff3e12933b3b6b",
            "pb_encode.h": "f9dacdb1dce5c6998234f2c7c6677ad03d36fbb11efa8d8676581fc868d862e7",
            "LICENSE.txt": UPSTREAM_LICENSE_SHA256,
        },
    },
    "0.4.6": {
        "commit": "afc499f9a410fc9bbf6c9c48cdd8d8b199d49eb4",
        "tree": "a0e54e9fe89eb1b42ee0931bec5d39570efc6ed7",
        "date": "2022-05-30T20:30:35+03:00",
        "files": {
            "pb.h": "3d3a1cfc343a9345394f2fc6fa5a4bddba76066af065df11e393ee837bdfcff5",
            "pb_common.c": "8d2ec28baaaf2b7a5e90e4cb2fa9700d21cef7f826f051a637c30b7a1e6a0516",
            "pb_common.h": "6495a691aca68d6973f2274b5dd54b74fbb57f6b019c45fff255a857fe1abcfd",
            "pb_decode.c": "d58772c57ac1fe62ff5b7841436d30d9d61b4f836fd53936c06745df9149ffbb",
            "pb_decode.h": "ddd9fe7c027f4a9cdb6cb4c74959eb916dd19a06a0ff48909c3612d313e0b445",
            "pb_encode.c": "f85be395be8c34a732eea12f64358110e5b0836f0a120a7c20982edec129a996",
            "pb_encode.h": "0715c9e289c1c49d3cb3128bdb81e1d40d1efeefe695c19ce1730f8103e54cbb",
            "LICENSE.txt": UPSTREAM_LICENSE_SHA256,
        },
    },
    "0.4.7": {
        "commit": "b97aa657a706d3ba4a9a6ccca7043c9d6fe41cba",
        "tree": "2eb286236013d6d82f12383aa0e6fa316a78172e",
        "date": "2022-12-11T11:51:56+02:00",
        "files": {
            "pb.h": "a990cfe2d8a19a0addd941a26812799fad39fc8d79bbe2a79a82b62a4a73ca37",
            "pb_common.c": "8d2ec28baaaf2b7a5e90e4cb2fa9700d21cef7f826f051a637c30b7a1e6a0516",
            "pb_common.h": "6495a691aca68d6973f2274b5dd54b74fbb57f6b019c45fff255a857fe1abcfd",
            "pb_decode.c": "9ed9e255e433324fc28557adb03bf494a3711c2a0480c97b3690a6871ce29c66",
            "pb_decode.h": "e0bed3f14db30b24c036b93920291ca9e661a13bda38fa4244f6294e704f3fad",
            "pb_encode.c": "f85be395be8c34a732eea12f64358110e5b0836f0a120a7c20982edec129a996",
            "pb_encode.h": "0715c9e289c1c49d3cb3128bdb81e1d40d1efeefe695c19ce1730f8103e54cbb",
            "LICENSE.txt": UPSTREAM_LICENSE_SHA256,
        },
    },
    "0.4.8": {
        "commit": "6cfe48d6f1593f8fa5c0f90437f5e6522587745e",
        "tree": "0197a003666f5fd44eb73d565aabe24ef8e11543",
        "date": "2023-11-11T09:55:45+02:00",
        "files": {
            "pb.h": "6afe4758a2a98b6244d78cb318fd7e6585334d2b7d0c9260b1fd68ff752f221d",
            "pb_common.c": "8d2ec28baaaf2b7a5e90e4cb2fa9700d21cef7f826f051a637c30b7a1e6a0516",
            "pb_common.h": "6495a691aca68d6973f2274b5dd54b74fbb57f6b019c45fff255a857fe1abcfd",
            "pb_decode.c": "9ed9e255e433324fc28557adb03bf494a3711c2a0480c97b3690a6871ce29c66",
            "pb_decode.h": "e0bed3f14db30b24c036b93920291ca9e661a13bda38fa4244f6294e704f3fad",
            "pb_encode.c": "f85be395be8c34a732eea12f64358110e5b0836f0a120a7c20982edec129a996",
            "pb_encode.h": "0715c9e289c1c49d3cb3128bdb81e1d40d1efeefe695c19ce1730f8103e54cbb",
            "LICENSE.txt": UPSTREAM_LICENSE_SHA256,
        },
    },
    "0.4.9": {
        "commit": "98bf4db69897b53434f3d0ba72e0a3ab1a902824",
        "tree": "2c4c260bcff3f9f7081238d377274dd385d76582",
        "date": "2024-09-19T13:56:19+03:00",
        "files": {
            "pb.h": "8cceb4abf46bc1df7f2e7ccb9ab87f84e509f9bfa5733f5ce1f70e7dbc82d18f",
            "pb_common.c": "8d2ec28baaaf2b7a5e90e4cb2fa9700d21cef7f826f051a637c30b7a1e6a0516",
            "pb_common.h": "6495a691aca68d6973f2274b5dd54b74fbb57f6b019c45fff255a857fe1abcfd",
            "pb_decode.c": "e980f2a41d9abe37b7e6fb4c9ba1ebfd68507a6fd2653f8d755e1947a9c84b1a",
            "pb_decode.h": "1747746e5961de5789bcf0795588da0790cd18b2e4e706ad9c7099a0fa1cc83f",
            "pb_encode.c": "d8dff2a1acc58683095a41b0dc3103ba46248e4a8d8c4e20f5810be04127b650",
            "pb_encode.h": "9aa00fee4ff08adf0da16e33a55be08810ea657800a648dc78f82e89c60c10cf",
            "LICENSE.txt": UPSTREAM_LICENSE_SHA256,
        },
    },
}

REFERENCE_BUILD_FLAGS = (
    "-target", "arm-none-eabi",
    "-mcpu=cortex-m55", "-mthumb", "-Os",
    "-ffunction-sections", "-fdata-sections", "-fno-ident",
    "-ffreestanding", "-fno-builtin",
)
REFERENCE_APPLE_CLANG_VERSION = "Apple clang version 21.0.0 (clang-2100.3.27.1)"
REFERENCE_APPLE_CLANG_OBJECTS = {
    "0.4.4": (
        "8e4be109e2f6816dedfbdb3b8d8a95192487d95748d594c2d971b1f6095f9185",
        "69b793dfa1d935e45d0b429b502f122fc3ed50b04dcb796e7f935309945d9592",
        "9358ae483a7a1b62f05db9d6da6e7dc1a535cc4ad719395beb835a26a022e08c",
    ),
    "0.4.5": (
        "8e4be109e2f6816dedfbdb3b8d8a95192487d95748d594c2d971b1f6095f9185",
        "61d84b44707d60c49b660018cb9eb738ca2e1d6972e7681edde59520506cd7b4",
        "9358ae483a7a1b62f05db9d6da6e7dc1a535cc4ad719395beb835a26a022e08c",
    ),
    "0.4.6": (
        "8e4be109e2f6816dedfbdb3b8d8a95192487d95748d594c2d971b1f6095f9185",
        "534518b875092903f7d47af043e5cb1cd4ffbdba6cb43273f47c21fb7675988a",
        "1b8296fe62275038936bca7dec840b5c3d898a5f6cace00dd684ca8727541c5a",
    ),
    "0.4.7": (
        "8e4be109e2f6816dedfbdb3b8d8a95192487d95748d594c2d971b1f6095f9185",
        "bd829ad3f7220884c3abd53b3a241a51d27b0064b88c687cd75d10e5eb762a12",
        "1b8296fe62275038936bca7dec840b5c3d898a5f6cace00dd684ca8727541c5a",
    ),
    "0.4.8": (
        "8e4be109e2f6816dedfbdb3b8d8a95192487d95748d594c2d971b1f6095f9185",
        "bd829ad3f7220884c3abd53b3a241a51d27b0064b88c687cd75d10e5eb762a12",
        "1b8296fe62275038936bca7dec840b5c3d898a5f6cace00dd684ca8727541c5a",
    ),
    "0.4.9": (
        "8e4be109e2f6816dedfbdb3b8d8a95192487d95748d594c2d971b1f6095f9185",
        "bd829ad3f7220884c3abd53b3a241a51d27b0064b88c687cd75d10e5eb762a12",
        "1b8296fe62275038936bca7dec840b5c3d898a5f6cace00dd684ca8727541c5a",
    ),
}


class AuditError(RuntimeError):
    """Raised when authenticated binary or upstream evidence drifts."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(data: bytes, start: int, end: int) -> bytes:
    offset = start - LOAD_BASE
    size = end - start
    if offset < 0 or size < 0 or offset + size > len(data):
        raise AuditError(f"run range 0x{start:08x}--0x{end:08x} is outside image")
    return data[offset : offset + size]


def _unique_address(data: bytes, needle: bytes, expected_address: int, label: str) -> int:
    offsets: list[int] = []
    cursor = 0
    while True:
        offset = data.find(needle, cursor)
        if offset < 0:
            break
        offsets.append(offset)
        cursor = offset + 1
    addresses = [LOAD_BASE + offset for offset in offsets]
    if addresses != [expected_address]:
        rendered = ", ".join(f"0x{address:08x}" for address in addresses) or "none"
        raise AuditError(f"{label}: expected unique 0x{expected_address:08x}, found {rendered}")
    return addresses[0]


def audit_image(data: bytes) -> dict[str, Any]:
    if len(data) != MAIN_SIZE:
        raise AuditError(f"official image size mismatch: {len(data)} != {MAIN_SIZE}")
    digest = sha256(data)
    if digest != MAIN_SHA256:
        raise AuditError(f"official image SHA-256 mismatch: {digest}")

    pinned = {
        "nanopb_region": sha256(image_slice(data, *NANOPB_REGION)),
        "pb_read": sha256(image_slice(data, *PB_READ)),
        "pb_decode_varint": sha256(image_slice(data, *PB_DECODE_VARINT)),
    }
    if pinned != PINNED_REGION_SHA256:
        raise AuditError(f"pinned nanopb code hashes drifted: {pinned}")

    clamp = _unique_address(
        data,
        PB_READ_SATURATING_CLAMP,
        PB_READ_SATURATING_CLAMP_ADDRESS,
        "pb_read saturating clamp",
    )
    varint_guard = _unique_address(
        data,
        PB_VARINT_63BIT_GUARD,
        PB_VARINT_63BIT_GUARD_ADDRESS,
        "pb_decode_varint 63-bit guard",
    )

    embedded_versions = [
        version
        for version in UPSTREAM_RELEASES
        if f"nanopb-{version}".encode("ascii") in data
    ]
    if embedded_versions:
        raise AuditError(f"unexpected embedded nanopb version strings: {embedded_versions}")

    return {
        "status": "point release unresolved",
        "exact_point_release": None,
        "candidate_releases_if_pristine_upstream": ["0.4.7", "0.4.8", "0.4.9"],
        "excluded_pristine_upstream_releases": ["0.4.4", "0.4.5", "0.4.6"],
        "qualification": (
            "The lower bound assumes the vendor used an unmodified official runtime; "
            "a backport can reproduce either instruction discriminator."
        ),
        "image": {
            "path": str(MAIN.relative_to(ROOT)),
            "size": len(data),
            "sha256": digest,
            "load_mapping": "run_addr = file_offset + 0x00437FE0",
        },
        "code": {
            "nanopb_region": [*NANOPB_REGION],
            "pb_read": [*PB_READ],
            "pb_decode_varint": [*PB_DECODE_VARINT],
            "sha256": pinned,
        },
        "discriminators": {
            "pb_read_saturating_clamp": {
                "address": clamp,
                "introduced": "0.4.7",
                "meaning": "clamp bytes_left to zero if callback consumed more than count",
            },
            "pb_decode_varint_63bit_guard": {
                "address": varint_guard,
                "introduced": "0.4.6",
                "meaning": "reject high bits when bit position is at least 63",
            },
        },
        "embedded_candidate_version_strings": embedded_versions,
        "runtime_collision": {
            "releases": ["0.4.7", "0.4.8", "0.4.9"],
            "source_observation": (
                "0.4.7 and 0.4.8 runtime C differs only in non-runtime pb.h text; "
                "0.4.9 changes types/annotations that preprocess identically on this target"
            ),
            "reference_build_result": "all three runtime object triplets byte-identical",
        },
        "upstream": {
            "repository": UPSTREAM_REPOSITORY,
            "license": UPSTREAM_LICENSE,
            "license_sha256": UPSTREAM_LICENSE_SHA256,
            "releases": UPSTREAM_RELEASES,
        },
    }


def _git(repo: Path, *arguments: str) -> bytes:
    try:
        return subprocess.run(
            ["git", "-C", str(repo), *arguments],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
    except (OSError, subprocess.CalledProcessError) as error:
        detail = getattr(error, "stderr", b"").decode("utf-8", "replace").strip()
        raise AuditError(f"git {' '.join(arguments)} failed: {detail or error}") from error


def verify_upstream_checkout(repo: Path) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for version, expected in UPSTREAM_RELEASES.items():
        tag = f"nanopb-{version}"
        commit = _git(repo, "rev-parse", f"{tag}^{{}}").decode().strip()
        tree = _git(repo, "rev-parse", f"{tag}^{{tree}}").decode().strip()
        if commit != expected["commit"] or tree != expected["tree"]:
            raise AuditError(f"{tag}: commit/tree identity drifted")
        file_hashes = {
            name: sha256(_git(repo, "show", f"{tag}:{name}")) for name in UPSTREAM_FILES
        }
        if file_hashes != expected["files"]:
            raise AuditError(f"{tag}: runtime source hashes drifted: {file_hashes}")
        result[version] = {"commit": commit, "tree": tree, "files": file_hashes}
    return result


def reference_build(repo: Path, clang: str) -> dict[str, Any]:
    """Build pristine tags and prove the surviving three-way collision.

    Object identity is pinned for the reviewed Apple Clang release.  Other
    Clang releases are accepted only when they reproduce the same relational
    evidence: 0.4.6 differs and 0.4.7--0.4.9 are mutually byte-identical.
    """

    compiler = shutil.which(clang)
    if compiler is None:
        raise AuditError(f"clang executable not found: {clang}")
    version_line = subprocess.run(
        [compiler, "--version"], check=True, text=True, stdout=subprocess.PIPE
    ).stdout.splitlines()[0]

    sources = ("pb_common", "pb_decode", "pb_encode")
    hashes: dict[str, tuple[str, ...]] = {}
    objects: dict[str, tuple[bytes, ...]] = {}
    with tempfile.TemporaryDirectory(prefix="openCFW-nanopb-reference-") as temporary:
        root = Path(temporary)
        include = root / "include"
        include.mkdir()
        (include / "string.h").write_text(
            "#ifndef OPENCFW_REFERENCE_STRING_H\n"
            "#define OPENCFW_REFERENCE_STRING_H\n"
            "#include <stddef.h>\n"
            "void *memcpy(void *, const void *, size_t);\n"
            "void *memset(void *, int, size_t);\n"
            "size_t strlen(const char *);\n"
            "#endif\n",
            encoding="ascii",
        )
        for release in UPSTREAM_RELEASES:
            release_dir = root / release
            release_dir.mkdir()
            tag = f"nanopb-{release}"
            for name in UPSTREAM_FILES[:-1]:
                (release_dir / name).write_bytes(_git(repo, "show", f"{tag}:{name}"))
            built: list[bytes] = []
            for source in sources:
                output = release_dir / f"{source}.o"
                command = [
                    compiler,
                    *REFERENCE_BUILD_FLAGS,
                    f"-I{include}",
                    f"-I{release_dir}",
                    "-c", str(release_dir / f"{source}.c"),
                    "-o", str(output),
                ]
                try:
                    subprocess.run(
                        command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                    )
                except subprocess.CalledProcessError as error:
                    raise AuditError(
                        f"reference compile failed for {release}/{source}: "
                        f"{error.stderr.decode('utf-8', 'replace').strip()}"
                    ) from error
                built.append(output.read_bytes())
            objects[release] = tuple(built)
            hashes[release] = tuple(sha256(item) for item in built)

    survivors = [objects[release] for release in ("0.4.7", "0.4.8", "0.4.9")]
    if not survivors[0] == survivors[1] == survivors[2]:
        raise AuditError("0.4.7--0.4.9 reference objects unexpectedly differ")
    if objects["0.4.6"][1] == objects["0.4.7"][1]:
        raise AuditError("0.4.6 and 0.4.7 pb_decode objects unexpectedly collide")
    if version_line == REFERENCE_APPLE_CLANG_VERSION and hashes != REFERENCE_APPLE_CLANG_OBJECTS:
        raise AuditError(f"reviewed Apple Clang object hashes drifted: {hashes}")

    return {
        "compiler": version_line,
        "flags": list(REFERENCE_BUILD_FLAGS),
        "object_order": [f"{name}.o" for name in sources],
        "object_sha256": hashes,
        "surviving_release_objects_byte_identical": True,
        "reviewed_compiler_hashes_pinned": version_line == REFERENCE_APPLE_CLANG_VERSION,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=MAIN)
    parser.add_argument("--upstream-repo", type=Path)
    parser.add_argument("--reference-build", action="store_true")
    parser.add_argument("--clang", default="clang")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    if args.reference_build and args.upstream_repo is None:
        parser.error("--reference-build requires --upstream-repo")

    try:
        report = audit_image(args.image.read_bytes())
        if args.upstream_repo is not None:
            report["verified_upstream_checkout"] = verify_upstream_checkout(
                args.upstream_repo.resolve()
            )
        if args.reference_build:
            report["reference_build"] = reference_build(
                args.upstream_repo.resolve(), args.clang
            )
    except (OSError, AuditError) as error:
        parser.exit(1, f"nanopb point-release audit failed: {error}\n")

    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
