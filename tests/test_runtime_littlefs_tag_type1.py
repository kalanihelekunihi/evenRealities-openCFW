from __future__ import annotations

import ctypes
import hashlib
import io
import json
import os
import random
import stat
import struct
import subprocess
import sys
import tarfile
import tempfile
import unicodedata
import unittest
from copy import deepcopy
from pathlib import Path, PurePosixPath
from unittest import mock


sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/shared/littlefs/runtime_littlefs_tag_type1.c"
HEADER = SOURCE.with_suffix(".h")
SOURCE_PATH = SOURCE.relative_to(ROOT).as_posix()
HEADER_PATH = HEADER.relative_to(ROOT).as_posix()
LITTLEFS = ROOT / "third_party/littlefs"
UPSTREAM = LITTLEFS / "lfs.c"
PROVENANCE = LITTLEFS / "PROVENANCE.json"
MAIN_PACKAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BOOT_IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
MAIN_OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
BOOT_OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
FUNCTION = "open_cfw_littlefs_tag_type1"
SECTION = ".text." + FUNCTION
MAIN_BASE = 0x0043_8000
BOOT_BASE = 0x0041_0000
MAIN_START = 0x004C_AE88
MAIN_END = 0x004C_AE90
BOOT_START = 0x0041_0B90
BOOT_END = 0x0041_0B98
PACKAGE_PREAMBLE = 32

MAIN_PACKAGE_PIN = (
    3_523_396,
    "36c5b0e499a68ac2493a497bdab9740fd"
    "3e7027730c26a9094eca47268a27863",
)
MAIN_PAYLOAD_PIN = (
    3_523_364,
    "19044a72bdfeb04c6b1b104d87da7b98"
    "e13cc18928528d84d999b6bcc0ba9701",
)
BOOT_PIN = (
    148_599,
    "f89a4c4657537cec6bfc572bdb831886"
    "6309b90a5d180c4307680d39824167b5",
)
SOURCE_PIN = (
    857,
    "7c0df44bd2ebce1eae4cacbfa174c0f9"
    "63dd03dcc5719ab386c0400201357b46",
)
HEADER_PIN = (
    893,
    "0993093546ead7b159179c7aaebbef926"
    "be24b39ca5202d04b17f0569ca830f6",
)
UPSTREAM_PIN = (
    196_753,
    "81a209e8551754d13b24fc0a2b6707fb"
    "3b2475e14feba00bf0df722b98a31398",
)
UPSTREAM_COMMIT = "0494ce7169f06a734a7bd7585f49a9fa91fa7318"
UPSTREAM_DEFINITION = (10_232, 10_326)
UPSTREAM_DEFINITION_PIN = (
    94,
    "ebf0229d6e0f78175c43641b09906fea"
    "19575fc3f34ac8862ae60159df1ec743",
)
UPSTREAM_TAG_TYPEDEF = (9_602, 9_629)
UPSTREAM_TAG_TYPEDEF_PIN = (
    27,
    "cb4dcd6212b1a269371d86dddf98ed7"
    "4853e2eb43753c5d8f8659abbca167ce2",
)

STOCK = bytes.fromhex("000d10f4e0607047")
STOCK_SHA256 = (
    "fc26e04a6784b91dc07f170f8a3bd230"
    "96f7caa92c15430a179edf215b509fdd"
)
MAIN_CALLERS = [
    (0x004C_AF32, "fff7a9ff"),
    (0x004C_AF64, "fff790ff"),
    (0x004C_B2F0, "fff7cafd"),
    (0x004C_B560, "fff792fc"),
    (0x004C_BC94, "fff7f8f8"),
    (0x004C_BCBA, "fff7e5f8"),
    (0x004C_BD12, "fff7b9f8"),
    (0x004C_CBA2, "fef771f9"),
]
BOOT_CALLERS = [
    (0x0041_0C3A, "fff7a9ff"),
    (0x0041_0C6C, "fff790ff"),
    (0x0041_0FF8, "fff7cafd"),
    (0x0041_1268, "fff792fc"),
    (0x0041_199C, "fff7f8f8"),
    (0x0041_19C2, "fff7e5f8"),
    (0x0041_1A1A, "fff7b9f8"),
    (0x0041_27A6, "fef7f3f9"),
]
CALLER_PINS = {
    "main": {
        "addresses": "f97e68b63d92a74c55f1eba09ecd3b109d1516555cc4666d4c03617c45f2e3ba",
        "encodings": "bb64df215a7ffa78053cf7f9172109bfc216753948ce7c9386a775e1507ac505",
        "records": "9c93a65bd664e28f8b4ed69a036955ccd3cafece93aed8078f639913f505033e",
    },
    "boot": {
        "addresses": "83c9e58936e433cb5491e391d3c44831d1d6f06fb1190b3111a326a74ba0ceaf",
        "encodings": "bdd585ae5c81bc94ec15fe578f41a1d0b4920868b5a9edd986c92c7e5c1c18de",
        "records": "29e1dbc1961092225a777207bce451b4f1e168256148830c21f21a6b9b89afb0",
    },
}

TARGET_FLAGS = (
    "--target=thumbv7em-none-eabi",
    "-mthumb",
    "-O2",
    "-ffreestanding",
    "-fno-jump-tables",
    "-fomit-frame-pointer",
    "-fno-builtin",
    "-mno-unaligned-access",
    "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables",
    "-fropi",
    "-ffunction-sections",
    "-fdata-sections",
    "-Wall",
    "-Wextra",
    "-Werror",
    "-fno-ident",
)
APPLE_CLANG = "/usr/bin/clang"
APPLE_CLANG_VERSION = "Apple clang version 21.0.0 (clang-2100.3.27.1)"
TARGET_OBJECT_PIN = (
    788,
    "42e5702fb7cb30ad327459f6b143207e"
    "ef8442d645860e12fcc80100044e3a48",
)
TARGET_TEXT = bytes.fromhex("4ff4e06101ea10507047")
TARGET_TEXT_PIN = (
    10,
    "079f868da6ae04c0d4ace93e9e9d913"
    "2247224f81903b57fba51d407f49ddfcf",
)

PROFILE_PINS = {
    "apple-clang": {
        "main_leaf": (124_576, 0x007B_29C4),
        "boot_leaf": (634, 0x0043_46F2),
        "main_patch": (
            "e7f29cbd00bf00bf",
            "cfdd737d4f3572d515bcb57cd206dd33"
            "decdb21d5be0ceafeee2386a3794678e",
        ),
        "boot_patch": (
            "23f0afbd00bf00bf",
            "a222cb65f8e026f2ee6e819193d95168"
            "2ac479742c0220702d8266d1bf2d723e",
        ),
        "main_overlay": (
            125_258,
            "1f71240bd75af28798d93eba217b99464156ee40ae353333c2fd0f449b9a8c76",
        ),
        "main_component": (
            3_648_654,
            "36b7f32f9f5f1a4c2fbf800b8cda0f48aa521bfc87638d671932b80b49f7e991",
        ),
        "boot_overlay": (
            662,
            "7cb3c17a03dda3b8576d8288ffa61df1332d89f1f24d6c5877bf0143e233902b",
        ),
        "boot_component": (
            149_262,
            "695688b7cc4d9583e9e5c854db44980acab9a58d367bc7e02fa5e51eb00e3267",
        ),
        "package": (
            4_427_148,
            "532743c6a1b96f198f0991c320bf3318eac88bc538a90a9e0b0267aaacef07b3",
        ),
        "flash_plan": (
            740_977,
            "b4b6e72d4ff7be47ca96a845a943320dfb65732c1de10d2bbb18051626cf2f95",
        ),
        "package_report": (
            2_323,
            "19972d9794b3b6ac6272b2c5d5cd782e528378fcdce4133b9f0856caf6e36f4a",
        ),
        "canonical_main_report": (
            1_525_514,
            "03e75b0fba3a82b80b7227d33a4a3af656708608e876cd37d370293a408cb6d5",
        ),
        "boot_report": (
            128_347,
            "802088e23fa8f4408db251f24f16b144ee14949c3ae13d82ae4f7ff9a86593f1",
        ),
        "boot_contract": (
            14_546,
            "36f9c1493a82992ed0112908ee4f4122174cde2cbd7e32e811b0751ab0b60d95",
        ),
    },
    "linux-clang": {
        "main_leaf": (126_396, 0x007B_30E0),
        "boot_leaf": (634, 0x0043_46F2),
        "main_patch": (
            "e8f22ab900bf00bf",
            "ee18f333cd4d3fdd38d1029d7234991"
            "f2ab78c26467da4b4535c43ef6dbb83f7",
        ),
        "boot_patch": (
            "23f0afbd00bf00bf",
            "a222cb65f8e026f2ee6e819193d95168"
            "2ac479742c0220702d8266d1bf2d723e",
        ),
        "main_overlay": (
            127_082,
            "f24cf0e060530429679df9389571ffee397819dfa2c3abc00d26deb75a3e47ad",
        ),
        "main_component": (
            3_650_478,
            "5fe58e3af2a0b7fed55c6b7c33afbd1ac5c887860721b04859e2d49d81be828c",
        ),
        "boot_overlay": (
            662,
            "e4c743531f56c190b7e3129768d410480a2f3433a5b680c7bf432ef0b05a7021",
        ),
        "boot_component": (
            149_262,
            "fc3d07c8a59e1c33f26965cdb1888114412c3ca671d6137f7c3166acc81c8d74",
        ),
        "package": (
            4_428_972,
            "22117e0cd7d0b827a8c31d22eb509edb30651fef6a6308838a8220ff80f6c702",
        ),
        "flash_plan": (
            605_604,
            "9da3d20004434bace4a5af3b88c720de1a38eb8b6cfda426f0d053309bbca327",
        ),
        "package_report": (
            2_322,
            "91c854c0a580bdd2cbc961a47b3f89943920c109b5baaa9a7e40a73ccb520fb5",
        ),
        "main_report": (
            1_545_743,
            "3e67859fefa8a82b615babb725cc662f957b3c3e902d6a26b74716841fd69182",
        ),
        "boot_report": (
            124_370,
            "80fc796f0eef34ffc94c484f1049cf5ce7608407f256a23818ecc1ca07cac6da",
        ),
        "boot_contract": (
            14_146,
            "a6bfdce05d408b09c5df8526434a2c32cd9ea238638738ae6c2659a01c3925d5",
        ),
    },
}

LINUX_BUILD_ARTIFACT_PINS = {
    "flash_plan": (
        605_604,
        "9da3d20004434bace4a5af3b88c720de1a38eb8b6cfda426f0d053309bbca327",
    ),
    "package_report": (
        2_322,
        "91c854c0a580bdd2cbc961a47b3f89943920c109b5baaa9a7e40a73ccb520fb5",
    ),
    "main_report": (
        1_545_743,
        "3e67859fefa8a82b615babb725cc662f957b3c3e902d6a26b74716841fd69182",
    ),
}

ORACLE_PREFIX = b"""\
#include <stdint.h>

typedef uint32_t lfs_tag_t;
"""
ORACLE_SUFFIX = b"""

uint16_t open_cfw_test_littlefs_tag_type1_pristine(uint32_t tag)
{
    return lfs_tag_type1(tag);
}
"""


def sha256(value: bytes | Path) -> str:
    if isinstance(value, Path):
        value = value.read_bytes()
    return hashlib.sha256(value).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(
        f"blob {len(data)}\0".encode("ascii") + data,
        usedforsecurity=False,
    ).hexdigest()


def assert_no_macos_path_aliases(paths: set[str]) -> None:
    aliases: dict[str, str] = {}
    for name in sorted(paths):
        key = unicodedata.normalize("NFD", name).casefold()
        prior = aliases.get(key)
        if prior is not None and prior != name:
            raise AssertionError(
                f"macOS path alias collision: {prior!r} and {name!r}"
            )
        aliases[key] = name


def require_real_directory(path: Path) -> None:
    metadata = path.lstat()
    if not stat.S_ISDIR(metadata.st_mode):
        raise AssertionError(f"snapshot parent is not a real directory: {path}")


def materialize_authenticated_open_cfw_snapshot(
    source_root: Path,
    destination: Path,
) -> None:
    """Materialize exactly the committed ``HEAD:openCFW`` Git tree."""

    repository = source_root.parent
    object_format = subprocess.run(
        ["git", "rev-parse", "--show-object-format"],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if object_format != "sha1":
        raise AssertionError(
            f"unsupported Git object format for authenticated snapshot: "
            f"{object_format!r}"
        )
    tree = subprocess.run(
        ["git", "ls-tree", "-rz", "HEAD:openCFW"],
        cwd=repository,
        check=True,
        capture_output=True,
    ).stdout
    expected: dict[str, tuple[str, str]] = {}
    for raw_record in tree.split(b"\0"):
        if not raw_record:
            continue
        metadata, raw_name = raw_record.split(b"\t", 1)
        mode, object_type, object_id = metadata.decode("ascii").split()
        name = raw_name.decode("utf-8")
        if object_type != "blob" or mode not in ("100644", "100755"):
            raise AssertionError(
                f"unsupported committed openCFW entry: {mode} "
                f"{object_type} {name!r}"
            )
        if name in expected:
            raise AssertionError(f"duplicate committed openCFW path: {name!r}")
        expected[name] = (mode, object_id)
    expected_directories = {
        "/".join(PurePosixPath(name).parts[:index])
        for name in expected
        for index in range(1, len(PurePosixPath(name).parts))
    }
    assert_no_macos_path_aliases(set(expected) | expected_directories)

    archived = subprocess.run(
        ["git", "archive", "--format=tar", "HEAD:openCFW"],
        cwd=repository,
        check=True,
        capture_output=True,
    ).stdout
    if os.path.lexists(destination):
        raise AssertionError("authenticated snapshot destination already exists")
    destination.mkdir(parents=True)
    require_real_directory(destination)
    for name in sorted(
        expected_directories,
        key=lambda item: (len(PurePosixPath(item).parts), item),
    ):
        relative = PurePosixPath(name)
        target = destination.joinpath(*relative.parts)
        require_real_directory(target.parent)
        if os.path.lexists(target):
            raise AssertionError(
                f"snapshot directory alias or collision: {name!r}"
            )
        target.mkdir()
        require_real_directory(target)
    observed: set[str] = set()
    observed_directories: set[str] = set()
    with tarfile.open(fileobj=io.BytesIO(archived), mode="r:") as archive:
        for member in archive.getmembers():
            name = member.name.rstrip("/")
            relative = PurePosixPath(name)
            if (
                not name
                or relative.is_absolute()
                or str(relative) != name
                or any(part in ("", ".", "..") for part in relative.parts)
            ):
                raise AssertionError(f"unsafe Git archive path: {member.name!r}")
            target = destination.joinpath(*relative.parts)
            if member.isdir():
                if name not in expected_directories:
                    raise AssertionError(
                        f"uncommitted Git archive directory: {name!r}"
                    )
                require_real_directory(target)
                if name in observed_directories:
                    raise AssertionError(
                        f"duplicate Git archive directory: {name!r}"
                    )
                observed_directories.add(name)
                continue
            if not member.isfile():
                raise AssertionError(
                    f"unsupported Git archive member: {member.name!r}"
                )
            if name in observed:
                raise AssertionError(f"duplicate Git archive path: {name!r}")
            committed = expected.get(name)
            if committed is None:
                raise AssertionError(f"uncommitted Git archive path: {name!r}")
            stream = archive.extractfile(member)
            if stream is None:
                raise AssertionError(f"cannot read Git archive path: {name!r}")
            data = stream.read()
            blob = git_blob_sha1(data)
            mode, object_id = committed
            if len(data) != member.size or blob != object_id:
                raise AssertionError(f"Git archive blob differs: {name!r}")
            require_real_directory(target.parent)
            if os.path.lexists(target):
                raise AssertionError(
                    f"snapshot file alias or collision: {name!r}"
                )
            open_flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
            if hasattr(os, "O_NOFOLLOW"):
                open_flags |= os.O_NOFOLLOW
            descriptor = os.open(target, open_flags, 0o600)
            try:
                with os.fdopen(descriptor, "wb", closefd=False) as output:
                    output.write(data)
                    output.flush()
                os.fchmod(descriptor, 0o755 if mode == "100755" else 0o644)
            finally:
                os.close(descriptor)
            observed.add(name)
    if observed_directories != expected_directories:
        missing = sorted(expected_directories - observed_directories)
        raise AssertionError(f"Git archive omitted committed directories: {missing}")
    if observed != set(expected):
        missing = sorted(set(expected) - observed)
        raise AssertionError(f"Git archive omitted committed paths: {missing}")
    for name, (mode, object_id) in expected.items():
        target = destination.joinpath(*PurePosixPath(name).parts)
        metadata = target.lstat()
        expected_mode = 0o755 if mode == "100755" else 0o644
        if not stat.S_ISREG(metadata.st_mode):
            raise AssertionError(f"snapshot path is not a regular file: {name!r}")
        if stat.S_IMODE(metadata.st_mode) != expected_mode:
            raise AssertionError(f"snapshot mode differs: {name!r}")
        if git_blob_sha1(target.read_bytes()) != object_id:
            raise AssertionError(f"snapshot blob re-attestation failed: {name!r}")


def wide_branch_target(
    address: int,
    first: int,
    second: int,
    *,
    link: bool,
) -> int | None:
    expected = 0xD000 if link else 0x9000
    if first & 0xF800 != 0xF000 or second & 0xD000 != expected:
        return None
    sign = (first >> 10) & 1
    imm10 = first & 0x03FF
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    i1 = 1 ^ (j1 ^ sign)
    i2 = 1 ^ (j2 ^ sign)
    immediate = (
        (sign << 24)
        | (i1 << 23)
        | (i2 << 22)
        | (imm10 << 12)
        | ((second & 0x07FF) << 1)
    )
    if sign:
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFF_FFFF


def wide_conditional_target(address: int, first: int, second: int) -> int | None:
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0x8000:
        return None
    if (first >> 6) & 0x0F >= 0x0E:
        return None
    sign = (first >> 10) & 1
    immediate = (
        (sign << 20)
        | (((second >> 11) & 1) << 19)
        | (((second >> 13) & 1) << 18)
        | ((first & 0x003F) << 12)
        | ((second & 0x07FF) << 1)
    )
    if sign:
        immediate -= 1 << 21
    return (address + 4 + immediate) & 0xFFFF_FFFF


def narrow_targets(address: int, halfword: int) -> tuple[int, ...]:
    if halfword & 0xF800 == 0xE000:
        immediate = halfword & 0x07FF
        if immediate & 0x0400:
            immediate -= 0x0800
        return (address + 4 + 2 * immediate,)
    if halfword & 0xF000 == 0xD000 and (halfword >> 8) & 0x0F < 0x0E:
        immediate = halfword & 0x00FF
        if immediate & 0x0080:
            immediate -= 0x0100
        return (address + 4 + 2 * immediate,)
    if halfword & 0xF500 == 0xB100:
        immediate = (((halfword >> 9) & 1) << 5) | ((halfword >> 3) & 0x1F)
        return (address + 4 + 2 * immediate,)
    return ()


class RuntimeLittlefsTagType1LinuxProfileContractTests(unittest.TestCase):
    def test_authenticated_snapshot_excludes_dirty_and_untracked_inputs(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(
            prefix="open-cfw-tag-type1-snapshot-boundary-"
        ) as raw:
            root = Path(raw)
            repository = root / "repository"
            source_root = repository / "openCFW"
            source_root.mkdir(parents=True)
            tracked = source_root / "components/build_input.c"
            tracked.parent.mkdir(parents=True)
            tracked.write_text("committed\n", encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
            subprocess.run(["git", "add", "openCFW"], cwd=repository, check=True)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.name=openCFW test",
                    "-c",
                    "user.email=open-cfw-test@example.invalid",
                    "commit",
                    "-qm",
                    "authenticated fixture",
                ],
                cwd=repository,
                check=True,
            )
            tracked.write_text("dirty\n", encoding="utf-8")
            untracked = source_root / "components/untracked_input.c"
            untracked.write_text("untracked\n", encoding="utf-8")

            snapshot = root / "snapshot"
            materialize_authenticated_open_cfw_snapshot(
                source_root,
                snapshot,
            )
            self.assertEqual(
                (snapshot / "components/build_input.c").read_text(
                    encoding="utf-8"
                ),
                "committed\n",
            )
            self.assertFalse(
                (snapshot / "components/untracked_input.c").exists()
            )

    def test_authenticated_snapshot_rejects_macos_path_aliases(self) -> None:
        def git(
            repository: Path,
            arguments: list[str],
            *,
            input_bytes: bytes | None = None,
        ) -> str:
            return subprocess.run(
                ["git", *arguments],
                cwd=repository,
                input=input_bytes,
                check=True,
                capture_output=True,
            ).stdout.decode("ascii").strip()

        def tree(
            repository: Path,
            records: list[tuple[str, str, str, str]],
        ) -> str:
            payload = b"".join(
                f"{mode} {object_type} {object_id}\t".encode("ascii")
                + name.encode("utf-8")
                + b"\0"
                for mode, object_type, object_id, name in sorted(
                    records, key=lambda item: item[3].encode("utf-8")
                )
            )
            return git(repository, ["mktree", "-z"], input_bytes=payload)

        for label, aliases in (
            ("casefold", ("Build_Input.c", "build_input.c")),
            ("unicode", ("caf\N{LATIN SMALL LETTER E WITH ACUTE}.c", "cafe\N{COMBINING ACUTE ACCENT}.c")),
        ):
            with self.subTest(alias=label), tempfile.TemporaryDirectory(
                prefix=f"open-cfw-tag-type1-{label}-alias-"
            ) as raw:
                root = Path(raw)
                repository = root / "repository"
                repository.mkdir()
                git(repository, ["init", "-q"])
                blob = git(
                    repository,
                    ["hash-object", "-w", "--stdin"],
                    input_bytes=b"authenticated\n",
                )
                components = tree(repository, [
                    ("100644", "blob", blob, name) for name in aliases
                ])
                open_cfw = tree(repository, [
                    ("040000", "tree", components, "components")
                ])
                root_tree = tree(repository, [
                    ("040000", "tree", open_cfw, "openCFW")
                ])
                commit = git(
                    repository,
                    [
                        "-c",
                        "user.name=openCFW test",
                        "-c",
                        "user.email=open-cfw-test@example.invalid",
                        "commit-tree",
                        root_tree,
                        "-m",
                        "alias fixture",
                    ],
                )
                git(repository, ["update-ref", "HEAD", commit])
                with self.assertRaisesRegex(
                    AssertionError,
                    "macOS path alias collision",
                ):
                    materialize_authenticated_open_cfw_snapshot(
                        repository / "openCFW",
                        root / "snapshot",
                    )

    def assert_linux_profile_contract(
        self,
        manifest: dict[str, object],
        main_config: dict[str, object],
        pins: dict[str, object],
    ) -> None:
        package_profile = manifest["package"]["profiles"]["linux-clang"]
        self.assertEqual(
            (package_profile["expected_size"], package_profile["expected_sha256"]),
            pins["package"],
        )

        provider_profile = manifest["component_overrides"]["apollo_main"][
            "provider"
        ]["profiles"]["linux-clang"]
        self.assertEqual(
            (provider_profile["size"], provider_profile["sha256"]),
            pins["main_component"],
        )

        main_profile = main_config["toolchain_profiles"]["linux-clang"]["expected"]
        self.assertEqual(
            (main_profile["overlay_size"], main_profile["overlay_sha256"]),
            pins["main_overlay"],
        )
        self.assertEqual(
            (
                main_profile["component_size"],
                main_profile["component_sha256"],
            ),
            pins["main_component"],
        )
        self.assertEqual(
            {name: pins[name] for name in LINUX_BUILD_ARTIFACT_PINS},
            LINUX_BUILD_ARTIFACT_PINS,
        )

    def test_linux_build_artifact_pins_are_exact(self) -> None:
        self.assert_linux_profile_contract(
            json.loads(MANIFEST.read_text(encoding="utf-8")),
            json.loads(MAIN_OVERLAY.read_text(encoding="utf-8")),
            PROFILE_PINS["linux-clang"],
        )

    def test_each_linux_authority_chain_pin_is_non_vacuous(self) -> None:
        baseline_manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        baseline_config = json.loads(MAIN_OVERLAY.read_text(encoding="utf-8"))
        baseline_pins = PROFILE_PINS["linux-clang"]
        mutations = (
            (
                "manifest package size",
                "manifest",
                ("package", "profiles", "linux-clang", "expected_size"),
            ),
            (
                "manifest package hash",
                "manifest",
                ("package", "profiles", "linux-clang", "expected_sha256"),
            ),
            ("profile package size", "pins", ("package", 0)),
            ("profile package hash", "pins", ("package", 1)),
            (
                "manifest provider size",
                "manifest",
                (
                    "component_overrides",
                    "apollo_main",
                    "provider",
                    "profiles",
                    "linux-clang",
                    "size",
                ),
            ),
            (
                "manifest provider hash",
                "manifest",
                (
                    "component_overrides",
                    "apollo_main",
                    "provider",
                    "profiles",
                    "linux-clang",
                    "sha256",
                ),
            ),
            (
                "config overlay size",
                "config",
                ("toolchain_profiles", "linux-clang", "expected", "overlay_size"),
            ),
            (
                "config overlay hash",
                "config",
                ("toolchain_profiles", "linux-clang", "expected", "overlay_sha256"),
            ),
            ("profile overlay size", "pins", ("main_overlay", 0)),
            ("profile overlay hash", "pins", ("main_overlay", 1)),
            (
                "config component size",
                "config",
                ("toolchain_profiles", "linux-clang", "expected", "component_size"),
            ),
            (
                "config component hash",
                "config",
                ("toolchain_profiles", "linux-clang", "expected", "component_sha256"),
            ),
            ("profile component size", "pins", ("main_component", 0)),
            ("profile component hash", "pins", ("main_component", 1)),
            ("authoritative flash plan size", "artifact_pins", ("flash_plan", 0)),
            ("authoritative flash plan hash", "artifact_pins", ("flash_plan", 1)),
            ("flash plan size", "pins", ("flash_plan", 0)),
            ("flash plan hash", "pins", ("flash_plan", 1)),
            (
                "authoritative package report size",
                "artifact_pins",
                ("package_report", 0),
            ),
            (
                "authoritative package report hash",
                "artifact_pins",
                ("package_report", 1),
            ),
            ("package report size", "pins", ("package_report", 0)),
            ("package report hash", "pins", ("package_report", 1)),
            (
                "authoritative main report size",
                "artifact_pins",
                ("main_report", 0),
            ),
            (
                "authoritative main report hash",
                "artifact_pins",
                ("main_report", 1),
            ),
            ("main report size", "pins", ("main_report", 0)),
            ("main report hash", "pins", ("main_report", 1)),
        )

        for label, target_name, path in mutations:
            with self.subTest(mutation=label):
                manifest = deepcopy(baseline_manifest)
                main_config = deepcopy(baseline_config)
                pins = deepcopy(baseline_pins)
                artifact_pins = deepcopy(LINUX_BUILD_ARTIFACT_PINS)
                target = {
                    "manifest": manifest,
                    "config": main_config,
                    "pins": pins,
                    "artifact_pins": artifact_pins,
                }[target_name]
                self.mutate_authority(target, path)
                with mock.patch.dict(
                    LINUX_BUILD_ARTIFACT_PINS,
                    artifact_pins,
                    clear=True,
                ):
                    with self.assertRaises(AssertionError):
                        self.assert_linux_profile_contract(
                            manifest,
                            main_config,
                            pins,
                        )

    @staticmethod
    def mutate_authority(target: dict[str, object], path: tuple[object, ...]) -> None:
        if len(path) == 2 and isinstance(target[path[0]], tuple):
            values = list(target[path[0]])
            values[path[1]] = (
                values[path[1]] + 1
                if isinstance(values[path[1]], int)
                else ("0" if values[path[1]][0] != "0" else "1")
                + values[path[1]][1:]
            )
            target[path[0]] = tuple(values)
            return

        parent = target
        for key in path[:-1]:
            parent = parent[key]
        key = path[-1]
        value = parent[key]
        parent[key] = (
            value + 1
            if isinstance(value, int)
            else ("0" if value[0] != "0" else "1") + value[1:]
        )


class RuntimeLittlefsTagType1ProductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.main_package = MAIN_PACKAGE.read_bytes()
        cls.main = cls.main_package[PACKAGE_PREAMBLE:]
        cls.boot = BOOT_IMAGE.read_bytes()
        version = subprocess.run(
            [APPLE_CLANG, "--version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()[0]
        if version != APPLE_CLANG_VERSION:
            raise AssertionError(f"unreviewed compiler: {version!r}")

        cls.temporary = tempfile.TemporaryDirectory(
            prefix="open-cfw-littlefs-tag-type1-production-",
        )
        temporary = Path(cls.temporary.name)
        cls.shadow_root = temporary / "openCFW"
        materialize_authenticated_open_cfw_snapshot(
            ROOT,
            cls.shadow_root,
        )
        build_environment = os.environ.copy()
        build_environment["OPENCFW_CLANG"] = APPLE_CLANG
        build_environment["OPENCFW_TOOLCHAIN_PROFILE"] = "apple-clang"
        build_commands = (
            (
                "Apollo-main component",
                [
                    sys.executable,
                    "components/apollo_main/core_overlay/build_component.py",
                ],
            ),
            (
                "bootloader component",
                [
                    sys.executable,
                    "components/bootloader/core_overlay/build_component.py",
                ],
            ),
            (
                "core-source package",
                [
                    sys.executable,
                    "tools/open_cfw.py",
                    "build",
                    "--manifest",
                    "manifests/g2-2.2.6.10-core-source.json",
                    "--output-dir",
                    "build/source",
                    "--toolchain-profile",
                    "apple-clang",
                ],
            ),
        )
        for label, command in build_commands:
            completed = subprocess.run(
                command,
                cwd=cls.shadow_root,
                env=build_environment,
                check=False,
                capture_output=True,
                text=True,
            )
            if completed.returncode != 0:
                raise AssertionError(
                    f"test-owned {label} build failed:\n"
                    f"{completed.stdout}{completed.stderr}"
                )
        cls.main_build = (
            cls.shadow_root / "components/apollo_main/core_overlay/build"
        )
        cls.boot_build = (
            cls.shadow_root / "components/bootloader/core_overlay/build"
        )
        cls.package_build = cls.shadow_root / "build/source"

        definition = UPSTREAM.read_bytes()[slice(*UPSTREAM_DEFINITION)]
        oracle = temporary / "oracle.c"
        oracle.write_bytes(ORACLE_PREFIX + definition + ORACLE_SUFFIX)
        library = temporary / (
            "tag-type1.dylib" if sys.platform == "darwin" else "tag-type1.so"
        )
        command = [
            APPLE_CLANG,
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-I",
            str(SOURCE.parent),
            str(SOURCE),
            str(oracle),
        ]
        if sys.platform == "darwin":
            command.extend(("-dynamiclib", "-o", str(library)))
        else:
            command.extend(("-shared", "-fPIC", "-o", str(library)))
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.library = ctypes.CDLL(str(library))
        cls.production_adapter = cls.library.open_cfw_littlefs_tag_type1
        cls.pristine = cls.library.open_cfw_test_littlefs_tag_type1_pristine
        for function in (cls.production_adapter, cls.pristine):
            function.argtypes = [ctypes.c_uint32]
            function.restype = ctypes.c_uint16

        cls.objects = []
        for index in range(2):
            output = temporary / f"production-adapter-{index}.o"
            subprocess.run(
                [APPLE_CLANG, *TARGET_FLAGS, "-c", SOURCE_PATH, "-o", str(output)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            cls.objects.append(output)

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.apollo_overlay = apollo_overlay

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @staticmethod
    def span(image: bytes, base: int, start: int, end: int) -> bytes:
        return image[start - base:end - base]

    def test_authenticated_upstream_source_and_dual_registration_are_exact(self) -> None:
        self.assertEqual(
            (len(self.main_package), sha256(self.main_package)),
            MAIN_PACKAGE_PIN,
        )
        self.assertEqual((len(self.main), sha256(self.main)), MAIN_PAYLOAD_PIN)
        self.assertEqual((len(self.boot), sha256(self.boot)), BOOT_PIN)
        self.assertEqual((SOURCE.stat().st_size, sha256(SOURCE)), SOURCE_PIN)
        self.assertEqual((HEADER.stat().st_size, sha256(HEADER)), HEADER_PIN)
        self.assertEqual((UPSTREAM.stat().st_size, sha256(UPSTREAM)), UPSTREAM_PIN)

        upstream = UPSTREAM.read_bytes()
        definition = upstream[slice(*UPSTREAM_DEFINITION)]
        self.assertEqual(
            (len(definition), sha256(definition)),
            UPSTREAM_DEFINITION_PIN,
        )
        self.assertEqual(
            definition,
            b"static inline uint16_t lfs_tag_type1(lfs_tag_t tag) {\n"
            b"    return (tag & 0x70000000) >> 20;\n}\n\n",
        )
        typedef = upstream[slice(*UPSTREAM_TAG_TYPEDEF)]
        self.assertEqual((len(typedef), sha256(typedef)), UPSTREAM_TAG_TYPEDEF_PIN)
        self.assertEqual(typedef, b"typedef uint32_t lfs_tag_t;")

        provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        self.assertEqual(provenance["upstream"]["selected_tag"], "v2.10.1")
        self.assertEqual(provenance["upstream"]["selected_commit"], UPSTREAM_COMMIT)
        self.assertEqual(provenance["license"], "BSD-3-Clause")
        self.assertFalse(provenance["selection"]["exact_historical_checkout_proven"])

        source = SOURCE.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        self.assertIn("Production adaptation", source)
        self.assertIn("redirected atomically", source)
        self.assertIn("(tag & UINT32_C(0x70000000)) >> 20U", source)
        self.assertIn("typedef uint32_t open_cfw_littlefs_type1_tag_t", header)
        self.assertIn("sizeof(uint16_t) == 2U", header)

        integration = provenance["production_integration"]
        self.assertIn(SOURCE_PATH, integration["allowed_production_source_paths"])
        self.assertIn(HEADER_PATH, integration["allowed_production_source_paths"])
        self.assertIn(FUNCTION, integration["allowed_production_symbols"])
        leaf_provenance = integration["tag_type1_leaf"]
        self.assertEqual(leaf_provenance["upstream_function"], "lfs_tag_type1")
        self.assertEqual(leaf_provenance["upstream_definition_offset"], 10_232)
        self.assertEqual(leaf_provenance["upstream_definition_size"], 94)
        self.assertEqual(
            leaf_provenance["upstream_definition_sha256"],
            UPSTREAM_DEFINITION_PIN[1],
        )
        self.assertEqual(leaf_provenance["upstream_tag_typedef_offset"], 9_602)
        self.assertEqual(leaf_provenance["upstream_tag_typedef_size"], 27)
        self.assertEqual(
            leaf_provenance["upstream_tag_typedef_sha256"],
            UPSTREAM_TAG_TYPEDEF_PIN[1],
        )
        self.assertEqual(
            (
                leaf_provenance["local_source_size"],
                leaf_provenance["local_source_sha256"],
            ),
            SOURCE_PIN,
        )
        self.assertEqual(
            (
                leaf_provenance["local_header_size"],
                leaf_provenance["local_header_sha256"],
            ),
            HEADER_PIN,
        )
        self.assertEqual(leaf_provenance["stock_size"], len(STOCK))
        self.assertEqual(leaf_provenance["stock_sha256"], STOCK_SHA256)
        self.assertEqual(leaf_provenance["relocations"], [])
        self.assertEqual(
            leaf_provenance["stock_images"]["apollo_main"]["stock_callers"],
            [
                {"address": f"0x{address:08X}", "encoding": encoding}
                for address, encoding in MAIN_CALLERS
            ],
        )
        self.assertEqual(
            leaf_provenance["stock_images"]["apollo_bootloader"]["stock_callers"],
            [
                {"address": f"0x{address:08X}", "encoding": encoding}
                for address, encoding in BOOT_CALLERS
            ],
        )

        configs = {
            "main": json.loads(MAIN_OVERLAY.read_text(encoding="utf-8")),
            "boot": json.loads(BOOT_OVERLAY.read_text(encoding="utf-8")),
        }
        for name, config in configs.items():
            self.assertIn(FUNCTION, config["functions"])
            leaves = [
                item
                for category in ("isolated_leaves", "relocated_leaves")
                for item in config.get(category, [])
                if item["function"] == FUNCTION
            ]
            self.assertEqual(len(leaves), 1, name)
            leaf = leaves[0]
            self.assertEqual(
                {
                    key: leaf["source"][key]
                    for key in ("path", "size", "sha256", "license", "upstream_commit")
                },
                {
                    "path": SOURCE_PATH,
                    "size": SOURCE_PIN[0],
                    "sha256": SOURCE_PIN[1],
                    "license": "BSD-3-Clause",
                    "upstream_commit": UPSTREAM_COMMIT,
                },
            )
            self.assertTrue(leaf["strict_relocation_contract"])
            self.assertEqual(leaf["relocations"], [])
            expected_offset = PROFILE_PINS["apple-clang"][f"{name}_leaf"][0]
            expected_alignment = 4 if name == "main" else 2
            self.assertEqual(
                leaf["expected"],
                {
                    "size": TARGET_TEXT_PIN[0],
                    "sha256": TARGET_TEXT_PIN[1],
                    "alignment": expected_alignment,
                    "offset": expected_offset,
                    "unrelocated_sha256": TARGET_TEXT_PIN[1],
                },
            )
            linux = leaf["toolchain_profiles"]["linux-clang"]
            self.assertEqual(
                linux["reviewed_version_prefix"],
                "Homebrew clang version 22.1.8",
            )
            if name == "main":
                self.assertEqual(
                    linux["expected"],
                    {
                        "size": TARGET_TEXT_PIN[0],
                        "sha256": TARGET_TEXT_PIN[1],
                        "alignment": 4,
                        "offset": PROFILE_PINS["linux-clang"]["main_leaf"][0],
                        "unrelocated_sha256": TARGET_TEXT_PIN[1],
                    },
                )
                self.assertEqual(linux["relocations"], [])
            else:
                self.assertNotIn("expected", linux)
                self.assertEqual(
                    config["function_profiles"]["linux-clang"][FUNCTION],
                    {"expected_offset": expected_offset, "expected_size": 10},
                )

            patch = [
                item
                for item in config["patch_sites"]
                if item["target_function"] == FUNCTION
            ]
            self.assertEqual(
                patch,
                [{
                    "name": "replace_littlefs_tag_type1",
                    "runtime_address": MAIN_START if name == "main" else BOOT_START,
                    "expected_size": len(STOCK),
                    "expected_sha256": STOCK_SHA256,
                    "branch": "b_w",
                    "target_function": FUNCTION,
                }],
            )

        for profile, pins in PROFILE_PINS.items():
            for name, config in configs.items():
                aggregate = (
                    config["expected"]
                    if profile == "apple-clang"
                    else config["toolchain_profiles"][profile]["expected"]
                )
                self.assertEqual(
                    (aggregate["overlay_size"], aggregate["overlay_sha256"]),
                    pins[f"{name}_overlay"],
                )
                self.assertEqual(
                    (aggregate["component_size"], aggregate["component_sha256"]),
                    pins[f"{name}_component"],
                )
                replacement = bytes.fromhex(pins[f"{name}_patch"][0])
                self.assertEqual(sha256(replacement), pins[f"{name}_patch"][1])
                self.assertEqual(replacement[4:], bytes.fromhex("00bf") * 2)
                start = MAIN_START if name == "main" else BOOT_START
                self.assertEqual(
                    wide_branch_target(
                        start,
                        *struct.unpack("<HH", replacement[:4]),
                        link=False,
                    ),
                    pins[f"{name}_leaf"][1],
                )
            production_profile = leaf_provenance["production_profiles"][profile]
            self.assertEqual(
                production_profile["apollo_main"],
                {
                    "leaf_size": 10,
                    "overlay_offset": pins["main_leaf"][0],
                    "runtime_address": f"0x{pins['main_leaf'][1]:08X}",
                    "relocated_sha256": TARGET_TEXT_PIN[1],
                    "unrelocated_sha256": TARGET_TEXT_PIN[1],
                },
            )
            self.assertEqual(
                production_profile["apollo_bootloader"],
                {
                    "leaf_size": 10,
                    "overlay_offset": pins["boot_leaf"][0],
                    "runtime_address": f"0x{pins['boot_leaf'][1]:08X}",
                    "relocated_sha256": TARGET_TEXT_PIN[1],
                    "unrelocated_sha256": TARGET_TEXT_PIN[1],
                },
            )

        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        main = manifest["component_overrides"]["apollo_main"]
        boot = manifest["component_overrides"]["apollo_bootloader"]
        for profile, pins in PROFILE_PINS.items():
            package = (
                manifest["package"]
                if profile == "apple-clang"
                else manifest["package"]["profiles"][profile]
            )
            main_provider = (
                main["provider"]
                if profile == "apple-clang"
                else main["provider"]["profiles"][profile]
            )
            boot_provider = (
                boot["provider"]
                if profile == "apple-clang"
                else boot["provider"]["profiles"][profile]
            )
            self.assertEqual(
                (package["expected_size"], package["expected_sha256"]),
                pins["package"],
            )
            self.assertEqual(
                (main_provider["size"], main_provider["sha256"]),
                pins["main_component"],
            )
            self.assertEqual(
                (boot_provider["size"], boot_provider["sha256"]),
                pins["boot_component"],
            )

        main_regions = {item["name"]: item for item in main["regions"]}
        boot_regions = {item["name"]: item for item in boot["regions"]}
        expected_regions = {
            "littlefs_tag_type1_source_replacement": (
                main_regions, 601_768, 8, MAIN_START,
                "generated_source_entry_replacement",
            ),
            "apollo_littlefs_tag_type1_source_alignment": (
                main_regions, 3_647_970, 2, 0x007B_29C2, "generated_alignment",
            ),
            "apollo_littlefs_tag_type1_source_leaf": (
                main_regions, 3_647_972, 10, 0x007B_29C4, "source_compiled",
            ),
            "bootloader_littlefs_tag_type1_source_replacement": (
                boot_regions, 2_960, 8, BOOT_START,
                "generated_source_entry_replacement",
            ),
            "bootloader_littlefs_tag_type1_source_leaf": (
                boot_regions, 149_234, 10, 0x0043_46F2, "source_compiled",
            ),
        }
        for region_name, (regions, offset, size, address, status) in expected_regions.items():
            region = regions[region_name]
            self.assertEqual(
                (
                    region["file_offset"],
                    region["size"],
                    region["target_address"],
                    region["address_status"],
                ),
                (offset, size, address, status),
            )
        for component in (main, boot):
            regions = component["regions"]
            self.assertEqual(regions[0]["file_offset"], 0)
            for previous, current in zip(regions, regions[1:]):
                self.assertEqual(
                    previous["file_offset"] + previous["size"],
                    current["file_offset"],
                    (previous["name"], current["name"]),
                )
            self.assertEqual(
                regions[-1]["file_offset"] + regions[-1]["size"],
                component["provider"]["size"],
            )

        apple = PROFILE_PINS["apple-clang"]
        artifacts = {
            "main_overlay": self.main_build / "apollo_core_overlay.bin",
            "main_component": self.main_build / "ota_s200_firmware_ota.bin",
            "main_report": self.main_build / "build-report.json",
            "boot_overlay": self.boot_build / "bootloader_core_overlay.bin",
            "boot_component": self.boot_build / "ota_s200_bootloader.bin",
            "boot_report": self.boot_build / "build-report.json",
            "boot_contract": self.boot_build / "provider-contract.json",
            "package": self.package_build / "package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin",
            "flash_plan": self.package_build / "flash-plan.json",
            "package_report": self.package_build / "build-report.json",
        }
        for name, path in artifacts.items():
            if name == "main_report":
                continue
            self.assertEqual((path.stat().st_size, sha256(path)), apple[name], name)

        main_report = json.loads(artifacts["main_report"].read_text(encoding="utf-8"))
        boot_report = json.loads(artifacts["boot_report"].read_text(encoding="utf-8"))
        reviewed_root = configs["main"]["toolchain"]["reviewed_source_root"]
        prefix_map = (
            f"-ffile-prefix-map={self.shadow_root.resolve()}={reviewed_root}"
        )
        self.assertEqual(main_report["toolchain"]["flags"][-1], prefix_map)
        self.assertEqual(
            main_report["toolchain"]["flags"].count(prefix_map),
            1,
        )
        canonical_main_report = deepcopy(main_report)
        canonical_main_report["toolchain"]["flags"].pop()
        canonical_main_report_bytes = (
            json.dumps(canonical_main_report, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        self.assertEqual(
            (
                len(canonical_main_report_bytes),
                sha256(canonical_main_report_bytes),
            ),
            apple["canonical_main_report"],
        )
        for name, report, start in (
            ("main", main_report, MAIN_START),
            ("boot", boot_report, BOOT_START),
        ):
            reported_leaf = next(
                item
                for item in report["relocated_leaves"]
                if item["extraction"]["function"] == FUNCTION
            )
            self.assertEqual(
                reported_leaf["placement"],
                {
                    "offset": apple[f"{name}_leaf"][0],
                    "runtime_address": apple[f"{name}_leaf"][1],
                    "runtime_address_hex": f"0x{apple[f'{name}_leaf'][1]:08X}",
                    "size": 10,
                    "alignment": 4 if name == "main" else 2,
                    "padding_before": 2 if name == "main" else 0,
                },
            )
            reported_patch = next(
                item
                for item in report["overlay"]["patched_sites"]
                if item["target_function"] == FUNCTION
            )
            self.assertEqual(
                reported_patch["replacement_hex"],
                apple[f"{name}_patch"][0],
            )
            self.assertEqual(reported_patch["runtime_address"], start)
            self.assertEqual(
                reported_patch["target_address"],
                apple[f"{name}_leaf"][1],
            )
        package_report = json.loads(
            artifacts["package_report"].read_text(encoding="utf-8")
        )
        self.assertEqual(
            (
                package_report["placed_region_count"],
                package_report["unresolved_region_count"],
                package_report["container_region_count"],
            ),
            (1032, 2, 5),
        )
        flash_plan = json.loads(artifacts["flash_plan"].read_text(encoding="utf-8"))
        self.assertEqual(flash_plan["package_sha256"], apple["package"][1])
        self.assertEqual(
            (
                len(flash_plan["flash_regions"]),
                len(flash_plan["unresolved_flash_regions"]),
                len(flash_plan["container_only_regions"]),
            ),
            (1032, 2, 5),
        )

    def test_dual_image_stock_callers_and_dependency_closure_are_exact(self) -> None:
        for name, image, base, start, end, callers in (
            ("main", self.main, MAIN_BASE, MAIN_START, MAIN_END, MAIN_CALLERS),
            ("boot", self.boot, BOOT_BASE, BOOT_START, BOOT_END, BOOT_CALLERS),
        ):
            stock = self.span(image, base, start, end)
            self.assertEqual(stock, STOCK, name)
            self.assertEqual(sha256(stock), STOCK_SHA256, name)
            records = []
            for address, expected_encoding in callers:
                encoding = self.span(image, base, address, address + 4)
                self.assertEqual(encoding.hex(), expected_encoding, (name, hex(address)))
                self.assertEqual(
                    wide_branch_target(
                        address,
                        *struct.unpack("<HH", encoding),
                        link=True,
                    ),
                    start,
                )
                records.append(struct.pack("<I", address) + encoding)
            pins = CALLER_PINS[name]
            self.assertEqual(
                sha256(b"".join(struct.pack("<I", address) for address, _ in callers)),
                pins["addresses"],
            )
            self.assertEqual(
                sha256(b"".join(bytes.fromhex(value) for _, value in callers)),
                pins["encodings"],
            )
            self.assertEqual(sha256(b"".join(records)), pins["records"])

            outgoing = []
            for offset in range(0, len(stock) - 3, 2):
                address = start + offset
                first, second = struct.unpack_from("<HH", stock, offset)
                for link in (True, False):
                    target = wide_branch_target(address, first, second, link=link)
                    if target is not None:
                        outgoing.append((address, link, target))
            self.assertEqual(outgoing, [], name)

    def test_complete_dual_image_ingress_and_pointer_closure_is_exact(self) -> None:
        for name, image, base, start, end, callers in (
            ("main", self.main, MAIN_BASE, MAIN_START, MAIN_END, MAIN_CALLERS),
            ("boot", self.boot, BOOT_BASE, BOOT_START, BOOT_END, BOOT_CALLERS),
        ):
            incoming_bl = []
            incoming_bw = []
            interior = []
            conditional = []
            for offset in range(0, len(image) - 3, 2):
                address = base + offset
                first, second = struct.unpack_from("<HH", image, offset)
                for link, owner in ((True, incoming_bl), (False, incoming_bw)):
                    target = wide_branch_target(address, first, second, link=link)
                    if target is None or not start <= target < end:
                        continue
                    if target == start:
                        owner.append((address, image[offset:offset + 4].hex()))
                    elif not start <= address < end:
                        interior.append((address, target, link))
                target = wide_conditional_target(address, first, second)
                if (
                    target is not None
                    and start <= target < end
                    and not start <= address < end
                ):
                    conditional.append((address, target))

            narrow = []
            final_halfword = None
            for offset in range(0, len(image) - 1, 2):
                address = base + offset
                final_halfword = address
                if start <= address < end:
                    continue
                halfword = struct.unpack_from("<H", image, offset)[0]
                for target in narrow_targets(address, halfword):
                    if start <= target < end:
                        narrow.append((address, target))
            final_complete_halfword = base + 2 * ((len(image) - 2) // 2)
            self.assertEqual(final_halfword, final_complete_halfword, name)

            stored = []
            for canonical in range(start, end):
                for value in {canonical, canonical | 1}:
                    needle = struct.pack("<I", value)
                    cursor = 0
                    while True:
                        position = image.find(needle, cursor)
                        if position < 0:
                            break
                        stored.append((base + position, value, canonical))
                        cursor = position + 1

            self.assertEqual(incoming_bl, callers, name)
            self.assertEqual(incoming_bw, [], name)
            self.assertEqual(interior, [], name)
            self.assertEqual(conditional, [], name)
            self.assertEqual(narrow, [], name)
            self.assertEqual(stored, [], name)

    def test_production_adapter_matches_pristine_definition_exhaustively_and_randomly(
        self,
    ) -> None:
        directed = (
            0x0000_0000,
            0xFFFF_FFFF,
            0x7000_0000,
            0x8000_0000,
            0xF000_0000,
            0x1000_0000,
            0x1234_5678,
            0xA5A5_5A5A,
        )
        for tag in directed:
            expected = (tag & 0x7000_0000) >> 20
            self.assertEqual(self.production_adapter(tag), expected, hex(tag))
            self.assertEqual(self.production_adapter(tag), self.pristine(tag), hex(tag))

        # Exhaust all combinations of the complete upper 16-bit word, which
        # includes every source-relevant type bit and the ignored validity bit.
        for upper in range(1 << 16):
            lower = (upper * 0x9E37 + 0x5A5A) & 0xFFFF
            tag = (upper << 16) | lower
            self.assertEqual(self.production_adapter(tag), self.pristine(tag), hex(tag))

        rng = random.Random(0x4C_AE88)
        for _ in range(20_000):
            tag = rng.getrandbits(32)
            self.assertEqual(self.production_adapter(tag), self.pristine(tag), hex(tag))

    def test_apple_thumb_object_text_and_no_relocation_closure_are_exact(self) -> None:
        first = self.objects[0].read_bytes()
        second = self.objects[1].read_bytes()
        self.assertEqual(first, second)
        self.assertEqual((len(first), sha256(first)), TARGET_OBJECT_PIN)

        leaf, extraction = self.apollo_overlay.extract_isolated_function_section(
            self.objects[0],
            FUNCTION,
        )
        self.assertEqual(leaf, TARGET_TEXT)
        self.assertEqual((len(leaf), sha256(leaf)), TARGET_TEXT_PIN)
        self.assertEqual(
            extraction,
            {
                "function": FUNCTION,
                "section": SECTION,
                "size": TARGET_TEXT_PIN[0],
                "sha256": TARGET_TEXT_PIN[1],
                "alignment": 4,
                "relocation_count": 0,
                "discarded_alloc_section_count": 1,
                "discarded_alloc_section_bytes": 8,
                "discarded_alloc_sections": [
                    {
                        "name": ".ARM.exidx" + SECTION,
                        "size": 8,
                        "flags": 130,
                    }
                ],
            },
        )

        data, sections = self.apollo_overlay.parse_elf32(self.objects[0])
        symbols = self.apollo_overlay.parse_elf32_symbols(data, sections)
        undefined = sorted(
            symbol["name"]
            for symbol in symbols
            if symbol["name"] and symbol["section_index"] == 0
        )
        self.assertEqual(undefined, [])


if __name__ == "__main__":
    unittest.main()
