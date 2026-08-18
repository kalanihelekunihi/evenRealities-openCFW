#!/usr/bin/env python3
"""Package the source-built MCUboot + Zephyr OpenR1 flash image."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import struct
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec


BOOT_LIMIT = 0x0000C000
APPLICATION_LIMIT = 0x000D1000
SETTINGS_START = 0x000D1000
DATA_START = 0x000D4000
DATA_LIMIT = 0x000F8000
FLASH_LIMIT = 0x00100000

SOURCE_LOCK = {
    "zephyr": {
        "version": "3.7.2",
        "commit": "bbbf8b30094dacd0d6830946ba206bcec8af6b0c",
        "tree": "4c43ca60d6574f1532362c691f6130d7180c3bd8",
        "license": "Apache-2.0",
    },
    "hal_nordic": {
        "commit": "ab5cb2e2faeb1edfad7a25286dcb513929ae55da",
        "tree": "705157917c3e0f49c37b054d1538b5564cc42d00",
        "license": "BSD-3-Clause and Nordic component licenses",
    },
    "cmsis": {
        "commit": "4b96cbb174678dcd3ca86e11e1f24bc5f8726da0",
        "tree": "5d06438da29f90ae930b55426bb55e4f250861cc",
        "license": "Apache-2.0",
    },
    "tinycrypt": {
        "commit": "1012a3ebee18c15ede5efc8332ee2fc37817670f",
        "tree": "8cd4b1950622b35a1a7b4b5d178d882eda05f9b6",
        "license": "BSD-3-Clause",
    },
    "mcuboot": {
        "commit": "6127fc06a54d7a364626a96a33ae652703b505e4",
        "tree": "dc3f69ddf8a670943e45c7ce002cab4474c5024b",
        "license": "Apache-2.0",
    },
    "bosch_bma456": {
        "version": "2.29.0",
        "commit": "3266db2c5de15be1a00232b8c0f2fd23e07934e0",
        "archive_sha256": "8c362c3bd107d0fdc480376788d18bccf908f46576530935cb25a58213491ffb",
        "license": "BSD-3-Clause",
        "files": {
            "bma4.c": "bb2dc4a7a75774f38d39ec9242fdba1f9fc7e1a66dc6c0e8767f776e3683013d",
            "bma4.h": "79a5f967938d50acfeaa096f65759c2d9156a38f153f85800bf3b4dae25e1ef4",
            "bma4_defs.h": "b0bf49bc03c12ef94d01cc0ba43f13ba0ba127204b707b211b6559d4d1b2d9ae",
            "bma456w.c": "01fc4f47a03db4244f9d86c97ca03e5c73bdf28a2ae3385ac37a097eb6559f21",
            "bma456w.h": "30c6dd9c291a45555bb5fa428544f7fa91369b1ee518a4bc50580ef6de6dfa92",
            "LICENSE": "7d32b0d25c587b4a9c25adb882885fe63ce77533d90f26676d2edf40f5b302c9",
        },
    },
    "st_lis2dw12": {
        "version": "2.1.0-compatible",
        "commit": "8d4bd522015004a9646102702901ba5a15ec6d39",
        "archive_sha256": "cc12412b9363a371fe1eb161710c5dbe81d5b6e707f7e33187b41a722aa8f1f6",
        "license": "BSD-3-Clause",
        "files": {
            "lis2dw12_reg.c": "525e5a139e15ece3ee93f583aa4321739cd1960088e56ffe922ec4f646c19f11",
            "lis2dw12_reg.h": "8ec9712080bf855726f764303b0c2f3eb209c51b8fdada86af059a1ee70fa048",
            "LICENSE": "b54f36a43cf9b8f6292c8f0f3b4c267ebd59859587e0152c94305bc81dda68bc",
        },
    },
    "st_st25dvxxkc": {
        "version": "fp-sns-stbox1 authenticated compatible snapshot",
        "commit": "e9a35449b777699b5e1dd0f1466de0ead554893a",
        "archive_sha256": "eecdc6795d5c949874d95739403aacaf6f0527c3fd476f7f78fda31e4d35faa6",
        "license": "BSD-3-Clause",
        "files": {
            "st25dvxxkc.c": "00469629a6b6cf76127a82dd0ab198855d8c794320df7f2d2f41509a289146e9",
            "st25dvxxkc.h": "c86f94ec2bef76e3de59d2520abca7f6bf9067f4ec316bdedc3db9091a930d76",
            "st25dvxxkc_reg.c": "dff34273b0656f8d45acb751cc576bf55add248d3f02b5c6e6dde0d679463106",
            "st25dvxxkc_reg.h": "1923438b4ae90693a32e0c6247ca64f1c880ea7db088c77d2ecee6584e69bd47",
            "LICENSE.md": "da99a74bf8c60dac50d83e98cbe082cef9ff3a90c04705020c383280c8a1be8b",
        },
    },
    "flashdb": {
        "version": "2.0.0",
        "commit": "4e5677408256f82d47cd56a6b04605dcee35ed9a",
        "archive_sha256": "7758fb46976acebc754fb452bbac2144badc713a3e158bab8a8961bc112eca1b",
        "license": "Apache-2.0",
        "files": {
            "LICENSE": "c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4",
            "inc/flashdb.h": "1d54dfb54f37500e592039b024e290e7ccd71f7653e21cbff0ee6e83d0cfadea",
            "inc/fdb_def.h": "32165431cd4c03b07ef92bd0556152b8f8717a2d49cbee4bb2beb8208d49cb99",
            "inc/fdb_low_lvl.h": "2e9d04cde4c6992c0c2b88ba6cbe2affa1b6b2a8fecf28f86151dc372b452422",
            "src/fdb.c": "538856687a0c0953eb2b0689ce68fef7cd3af715e6a549290df78082af06529c",
            "src/fdb_tsdb.c": "cc75d8553fb5b4d5aba3533ca245ced57e98a154adb10270648cca1382adedcb",
            "src/fdb_utils.c": "caa16b6aa308ddbc93e962476a607f675a49b5a5849889b46bbcc0091be27833",
        },
    },
    "fal": {
        "version": "0.5.99",
        "container": "flashdb",
        "license": "Apache-2.0",
        "files": {
            "port/fal/LICENSE": "c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4",
            "port/fal/inc/fal.h": "37d28f905573c44d1b62757762b10f4091342749be9760e757de0779abce7724",
            "port/fal/inc/fal_def.h": "3cc27b18c2eaa980b5daa6a0f809b56e67d528d58a8839d5454e456e16364437",
            "port/fal/src/fal.c": "75a2066ba14315c17d18adce087163fa482478c290a105879fecf6b5712db0bb",
            "port/fal/src/fal_flash.c": "6136a96fe88f3b595961d58a89824e2c3356545b561eee5ff66d6cec59a96aed",
            "port/fal/src/fal_partition.c": "25b7ade441576561e5ebee1ef43c92c9e03c494e0a459588d82a1ebccc7c498c",
        },
    },
    "goodix_democode": {
        "version": "democode v1.6 / DrvLib v4.3.0.0",
        "commit": "2c0034a23b675a5f9a29e4a47e8b504c7a88e321",
        "archive_sha256": "48564d724f1de0004dd19ed3d8b156841400b7e652714f46dcb64d0397c76d29",
        "license": "Goodix 5-clause; use restricted to Goodix ICs",
        "license_sha256": "dfb94b7725971b1696299c6d9fd36b8a447c40c1a9c9e89a8a392377f9823226",
        "admitted_source_file_count": 59,
        "admitted_source_aggregate_sha256": "b0c421df96de26abd6c4af04de46023f7148c05bafb17da8aaa8de6a9830ec77",
    },
}

SOURCE_REPOSITORIES = {
    "zephyr": "zephyr",
    "hal_nordic": "modules/hal/nordic",
    "cmsis": "modules/hal/cmsis",
    "tinycrypt": "modules/crypto/tinycrypt",
    "mcuboot": "bootloader/mcuboot",
}

PROJECT = Path(__file__).resolve().parents[1]
RECONSTRUCTED_OBJECTS = (
    "rtc_device.c", "generic_device_registry.c", "software_twi.c",
    "sensor_stream.c", "time_calendar.c", "r1_model_data.c",
    "quantized_runtime.c", "gxt310.c", "qma6100.c", "yhm2710.c",
    "goodix_primitives.c", "goodix_heap.c", "gomore_primitives.c",
    "gomore_tensor_runtime.c",
)
MOTION_PROVIDER_OBJECTS = (
    "bma4.c", "bma456w.c", "lis2dw12_reg.c",
)
NFC_PROVIDER_OBJECTS = (
    "st25dvxxkc.c", "st25dvxxkc_reg.c",
)
HEALTH_STORAGE_PROVIDER_OBJECTS = (
    "fdb.c", "fdb_tsdb.c", "fdb_utils.c", "fal.c", "fal_flash.c",
    "fal_partition.c",
)
GOODIX_PROVIDER_OBJECTS = (
    "gh_drv_config.c", "gh_drv_control.c", "gh_drv_dump.c",
    "gh_drv_interface.c", "gh_demo.c", "gh_demo_hook.c",
    "gh_demo_reg_array.c", "gh_demo_user.c", "gh_agc.c",
    "gh_changeinttime.c", "gh_movedetect.c", "gh_multi_sen_pro.c",
    "goodix_hba_config.c", "goodix_hrv_config.c",
    "goodix_spo2_config_for_gh3x2x-v2.23_7ecd2a.c",
    "r1_gh3x2x_port.c", "r1_gh3x2x_bind.c",
    "r1_gh3x2x_provider_composer.c",
    "r1_gh3x2x_reconstructed_roots.c", "r1_gh3x2x_stubs.c",
)

GOODIX_COMPILED_SOURCES = (
    "demo_code/demo_kernel_code/driver/src/gh_drv_config.c",
    "demo_code/demo_kernel_code/driver/src/gh_drv_control.c",
    "demo_code/demo_kernel_code/driver/src/gh_drv_dump.c",
    "demo_code/demo_kernel_code/driver/src/gh_drv_interface.c",
    "demo_code/demo_kernel_code/kernel/gh_demo.c",
    "demo_code/demo_kernel_code/kernel/gh_demo_hook.c",
    "demo_code/demo_kernel_code/kernel/gh_demo_reg_array.c",
    "demo_code/demo_kernel_code/kernel/gh_demo_user.c",
    "demo_code/demo_kernel_code/module/gh_agc/gh_agc.c",
    "demo_code/demo_kernel_code/module/gh_other/gh_changeinttime.c",
    "demo_code/demo_kernel_code/module/gh_other/gh_movedetect.c",
    "demo_code/demo_kernel_code/module/gh_soft_adt/gh_multi_sen_pro.c",
    "algo_lib/algo_params/HR/04_EXCLUSIVE/goodix_hba_config.c",
    "algo_lib/algo_params/goodix_hrv_config.c",
    "algo_lib/algo_params/SPO2/goodix_spo2_config_for_gh3x2x-v2.23_7ecd2a.c",
    "LICENSE",
)
GOODIX_HEADER_DIRECTORIES = (
    "demo_code/demo_kernel_code/driver/inc",
    "demo_code/demo_kernel_code/kernel",
    "demo_code/demo_kernel_code/module/gh_agc",
    "demo_code/demo_kernel_code/module/gh_ecg",
    "demo_code/demo_kernel_code/module/gh_other",
    "demo_code/demo_kernel_code/module/gh_protocol",
    "demo_code/demo_kernel_code/module/gh_soft_adt",
    "demo_code/demo_algo_code/goodix_algo_application/inc",
    "demo_code/demo_algo_code/goodix_algo_call/inc",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_ihex(data: bytes) -> dict[int, int]:
    memory: dict[int, int] = {}
    upper = 0
    eof = False
    for number, raw in enumerate(data.decode("ascii").splitlines(), 1):
        if not raw:
            continue
        if not raw.startswith(":"):
            raise ValueError(f"Intel HEX line {number} has no record marker")
        record = bytes.fromhex(raw[1:])
        if len(record) < 5 or record[0] + 5 != len(record):
            raise ValueError(f"Intel HEX line {number} has an invalid length")
        if sum(record) & 0xFF:
            raise ValueError(f"Intel HEX line {number} has an invalid checksum")
        length = record[0]
        offset = int.from_bytes(record[1:3], "big")
        kind = record[3]
        payload = record[4 : 4 + length]
        if kind == 0:
            for index, value in enumerate(payload):
                address = upper + offset + index
                previous = memory.get(address)
                if previous is not None and previous != value:
                    raise ValueError(f"conflicting Intel HEX byte at 0x{address:08x}")
                memory[address] = value
        elif kind == 1:
            eof = True
        elif kind == 2:
            upper = int.from_bytes(payload, "big") << 4
        elif kind == 4:
            upper = int.from_bytes(payload, "big") << 16
        elif kind not in (3, 5):
            raise ValueError(f"unsupported Intel HEX record type {kind}")
    if not eof or not memory:
        raise ValueError("Intel HEX input is empty or has no EOF record")
    return memory


def ihex_record(address: int, kind: int, payload: bytes) -> str:
    record = bytes((len(payload),)) + address.to_bytes(2, "big") + bytes((kind,)) + payload
    checksum = (-sum(record)) & 0xFF
    return ":" + (record + bytes((checksum,))).hex().upper()


def write_ihex(memory: dict[int, int]) -> bytes:
    lines: list[str] = []
    current_upper = -1
    addresses = sorted(memory)
    cursor = 0
    while cursor < len(addresses):
        start = addresses[cursor]
        upper = start >> 16
        if upper != current_upper:
            lines.append(ihex_record(0, 4, upper.to_bytes(2, "big")))
            current_upper = upper
        payload = bytearray((memory[start],))
        cursor += 1
        while cursor < len(addresses) and len(payload) < 16:
            address = addresses[cursor]
            if address != start + len(payload) or address >> 16 != upper:
                break
            payload.append(memory[address])
            cursor += 1
        lines.append(ihex_record(start & 0xFFFF, 0, bytes(payload)))
    lines.append(ihex_record(0, 1, b""))
    return ("\n".join(lines) + "\n").encode("ascii")


def merge_memory(left: dict[int, int], right: dict[int, int]) -> dict[int, int]:
    merged = dict(left)
    for address, value in right.items():
        previous = merged.get(address)
        if previous is not None and previous != value:
            raise ValueError(f"firmware members overlap at 0x{address:08x}")
        merged[address] = value
    return merged


def memory_contains(memory: dict[int, int], value: bytes) -> bool:
    if not value:
        return True
    return any(
        all(memory.get(start + offset) == byte for offset, byte in enumerate(value))
        for start in memory
        if memory[start] == value[0]
    )


def require_range(memory: dict[int, int], start: int, limit: int, label: str) -> None:
    lowest, highest = min(memory), max(memory) + 1
    if lowest < start or highest > limit:
        raise ValueError(
            f"{label} range 0x{lowest:08x}..<0x{highest:08x} is outside "
            f"0x{start:08x}..<0x{limit:08x}"
        )


def fixed_zip_time() -> tuple[int, int, int, int, int, int]:
    epoch = max(int(os.environ.get("SOURCE_DATE_EPOCH", "0")), 315_532_800)
    stamp = datetime.fromtimestamp(epoch, timezone.utc)
    return stamp.year, stamp.month, stamp.day, stamp.hour, stamp.minute, stamp.second


def zip_member(archive: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, fixed_zip_time())
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    archive.writestr(info, data)


def configured_key(config: str) -> Path:
    match = re.search(r'^CONFIG_BOOT_SIGNATURE_KEY_FILE="([^"]+)"$', config, re.MULTILINE)
    if match is None:
        raise ValueError("MCUboot configuration has no signature key")
    return Path(match.group(1))


def verify_source_revisions(workspace: Path) -> None:
    for name, relative in SOURCE_REPOSITORIES.items():
        repository = workspace / relative
        expected = SOURCE_LOCK[name]
        if not (repository / ".git").exists():
            raise ValueError(f"source repository is missing: {repository}")
        commit = subprocess.run(
            ["git", "-C", os.fspath(repository), "rev-parse", "HEAD^{commit}"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        tree = subprocess.run(
            ["git", "-C", os.fspath(repository), "rev-parse", "HEAD^{tree}"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        if commit != expected["commit"] or tree != expected["tree"]:
            raise ValueError(
                f"{name} source revision differs: commit={commit}, tree={tree}"
            )
        dirty = subprocess.run(
            ["git", "-C", os.fspath(repository), "status", "--porcelain",
             "--untracked-files=all"],
            check=True, capture_output=True, text=True,
        ).stdout
        if dirty:
            raise ValueError(f"{name} source checkout is modified or has untracked files")


def verify_file_source(root: Path, name: str) -> None:
    expected = SOURCE_LOCK[name]
    files = expected.get("files")
    if not isinstance(files, dict):
        raise ValueError(f"{name} source lock has no file inventory")
    for relative, digest in files.items():
        path = root / relative
        if not path.is_file() or sha256(path.read_bytes()) != digest:
            raise ValueError(f"{name} source file differs: {path}")


def verify_goodix_source(root: Path) -> None:
    expected = SOURCE_LOCK["goodix_democode"]
    paths = {Path(relative) for relative in GOODIX_COMPILED_SOURCES}
    for relative in GOODIX_HEADER_DIRECTORIES:
        directory = root / relative
        if not directory.is_dir():
            raise ValueError(f"Goodix header directory is missing: {directory}")
        paths.update(path.relative_to(root) for path in directory.rglob("*.h"))
    records = []
    for relative in sorted(paths):
        path = root / relative
        if not path.is_file():
            raise ValueError(f"Goodix admitted source file is missing: {path}")
        records.append(
            relative.as_posix().encode("utf-8") + b"\0" +
            bytes.fromhex(sha256(path.read_bytes()))
        )
    if len(records) != expected["admitted_source_file_count"] or \
       sha256(b"".join(records)) != expected["admitted_source_aggregate_sha256"]:
        raise ValueError("Goodix admitted source subset differs from the pin")
    if sha256((root / "LICENSE").read_bytes()) != expected["license_sha256"]:
        raise ValueError("Goodix license differs from the pin")


def openr1_source_inventory() -> dict[str, object]:
    files: set[Path] = set()
    for directory, suffixes in (
        (PROJECT / "include", {".h"}),
        (PROJECT / "src", {".c", ".h"}),
        (PROJECT / "reconstructed", {".c", ".h", ".inc"}),
        (PROJECT / "port", {".c", ".h"}),
    ):
        files.update(path for path in directory.rglob("*") if path.suffix in suffixes)
    platform = PROJECT / "platform" / "nrf52840"
    files.update(path for path in platform.glob("r1_nrf52840.*") if path.is_file())
    backend = platform / "zephyr"
    build_names = {"CMakeLists.txt", "board.yml"}
    build_suffixes = {".c", ".conf", ".dts", ".h", ".ld", ".yml"}
    files.update(
        path for path in backend.rglob("*")
        if path.is_file() and (path.name in build_names or
                               path.name.startswith("Kconfig") or
                               path.name.endswith("_defconfig") or
                               path.suffix in build_suffixes)
    )
    records = {
        path.relative_to(PROJECT).as_posix(): sha256(path.read_bytes())
        for path in sorted(files)
    }
    serialized = b"".join(
        name.encode("utf-8") + b"\0" + bytes.fromhex(value)
        for name, value in sorted(records.items())
    )
    commit = subprocess.run(
        ["git", "-C", os.fspath(PROJECT), "rev-parse", "HEAD^{commit}"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    dirty = bool(subprocess.run(
        ["git", "-C", os.fspath(PROJECT), "status", "--porcelain", "--", "."],
        check=True, capture_output=True, text=True,
    ).stdout)
    return {
        "git_commit": commit,
        "dirty": dirty,
        "file_count": len(records),
        "aggregate_sha256": sha256(serialized),
        "files": records,
    }


def verify_reconstructed_map(map_text: str) -> dict[str, dict[str, int]]:
    retained: dict[str, dict[str, int]] = {}
    # Zephyr emits the KEEP directives after its loadable ROM sections and
    # before debug sections. Restrict matches to that first half so DWARF
    # offsets cannot masquerade as flash addresses.
    loadable_text = map_text.split("\nopenr1_reconstructed", 1)[0]
    for name in RECONSTRUCTED_OBJECTS:
        pattern = re.compile(
            rf"0x([0-9a-fA-F]+)\s+0x([0-9a-fA-F]+)\s+"
            rf"app/libapp\.a\({re.escape(name)}\.obj\)"
        )
        spans = []
        for match in pattern.finditer(loadable_text):
            address = int(match.group(1), 16)
            size = int(match.group(2), 16)
            if BOOT_LIMIT <= address < APPLICATION_LIMIT and size > 0:
                spans.append((address, size))
        if not spans:
            raise ValueError(f"reconstructed object has no loadable linked span: {name}")
        retained[name] = {
            "loadable_span_count": len(spans),
            "loadable_bytes": sum(size for _address, size in spans),
        }
    if "r1_model_data_words" not in map_text:
        raise ValueError("generated model-data symbol is absent from the linked application")
    return retained


def verify_motion_provider_map(map_text: str) -> dict[str, dict[str, int]]:
    retained: dict[str, dict[str, int]] = {}
    loadable_text = map_text.split("\nopenr1_reconstructed", 1)[0]
    for name in MOTION_PROVIDER_OBJECTS:
        pattern = re.compile(
            rf"0x([0-9a-fA-F]+)\s+0x([0-9a-fA-F]+)\s+"
            rf"app/libapp\.a\({re.escape(name)}\.obj\)"
        )
        spans = []
        for match in pattern.finditer(loadable_text):
            address = int(match.group(1), 16)
            size = int(match.group(2), 16)
            if BOOT_LIMIT <= address < APPLICATION_LIMIT and size > 0:
                spans.append((address, size))
        if not spans:
            raise ValueError(f"motion provider object has no linked span: {name}")
        retained[name] = {
            "loadable_span_count": len(spans),
            "loadable_bytes": sum(size for _address, size in spans),
        }
    return retained


def verify_nfc_provider_map(map_text: str) -> dict[str, dict[str, int]]:
    retained: dict[str, dict[str, int]] = {}
    loadable_text = map_text.split("\nopenr1_reconstructed", 1)[0]
    for name in NFC_PROVIDER_OBJECTS:
        pattern = re.compile(
            rf"0x([0-9a-fA-F]+)\s+0x([0-9a-fA-F]+)\s+"
            rf"app/libapp\.a\({re.escape(name)}\.obj\)"
        )
        spans = []
        for match in pattern.finditer(loadable_text):
            address = int(match.group(1), 16)
            size = int(match.group(2), 16)
            if BOOT_LIMIT <= address < APPLICATION_LIMIT and size > 0:
                spans.append((address, size))
        if not spans:
            raise ValueError(f"NFC provider object has no linked span: {name}")
        retained[name] = {
            "loadable_span_count": len(spans),
            "loadable_bytes": sum(size for _address, size in spans),
        }
    return retained


def verify_health_storage_provider_map(
    map_text: str,
) -> dict[str, dict[str, int]]:
    retained: dict[str, dict[str, int]] = {}
    loadable_text = map_text.split("\nopenr1_reconstructed", 1)[0]
    for name in HEALTH_STORAGE_PROVIDER_OBJECTS:
        pattern = re.compile(
            rf"0x([0-9a-fA-F]+)\s+0x([0-9a-fA-F]+)\s+"
            rf"app/libapp\.a\({re.escape(name)}\.obj\)"
        )
        spans = []
        for match in pattern.finditer(loadable_text):
            address = int(match.group(1), 16)
            size = int(match.group(2), 16)
            if BOOT_LIMIT <= address < APPLICATION_LIMIT and size > 0:
                spans.append((address, size))
        if not spans:
            raise ValueError(
                f"health-storage provider object has no linked span: {name}")
        retained[name] = {
            "loadable_span_count": len(spans),
            "loadable_bytes": sum(size for _address, size in spans),
        }
    return retained


def verify_goodix_provider_map(map_text: str) -> dict[str, dict[str, int]]:
    retained: dict[str, dict[str, int]] = {}
    loadable_text = map_text.split("\nopenr1_reconstructed", 1)[0]
    for name in GOODIX_PROVIDER_OBJECTS:
        pattern = re.compile(
            rf"0x([0-9a-fA-F]+)\s+0x([0-9a-fA-F]+)\s+"
            rf"app/libapp\.a\({re.escape(name)}\.obj\)"
        )
        spans = []
        for match in pattern.finditer(loadable_text):
            address = int(match.group(1), 16)
            size = int(match.group(2), 16)
            if BOOT_LIMIT <= address < APPLICATION_LIMIT and size > 0:
                spans.append((address, size))
        if not spans:
            raise ValueError(f"Goodix provider object has no linked span: {name}")
        retained[name] = {
            "loadable_span_count": len(spans),
            "loadable_bytes": sum(size for _address, size in spans),
        }
    return retained


def verify_mcuboot_signature(image: bytes, public_pem: bytes) -> None:
    """Validate an MCUboot ECDSA-P256 image without importing imgtool."""
    if len(image) < 32:
        raise ValueError("signed application is shorter than its MCUboot header")
    magic, _, header_size, protected_size, image_size = struct.unpack_from("<IIHHI", image)
    if magic != 0x96F3B83D:
        raise ValueError("application has no MCUboot image header")
    tlv_offset = header_size + image_size
    if tlv_offset + protected_size > len(image):
        raise ValueError("MCUboot protected TLV range is out of bounds")
    if protected_size:
        protected_magic, protected_total = struct.unpack_from("<HH", image, tlv_offset)
        if protected_magic != 0x6908 or protected_total != protected_size:
            raise ValueError("invalid MCUboot protected TLV info")
        tlv_offset += protected_size
    if tlv_offset + 4 > len(image):
        raise ValueError("MCUboot signature TLV is missing")
    tlv_magic, tlv_total = struct.unpack_from("<HH", image, tlv_offset)
    if tlv_magic != 0x6907 or tlv_offset + tlv_total != len(image):
        raise ValueError("invalid MCUboot signature TLV extent")
    hash_region = image[:tlv_offset]
    expected_hash = hashlib.sha256(hash_region).digest()
    recorded_hash = None
    signature = None
    cursor = tlv_offset + 4
    while cursor < len(image):
        if cursor + 4 > len(image):
            raise ValueError("truncated MCUboot TLV")
        kind, _padding, length = struct.unpack_from("<BBH", image, cursor)
        cursor += 4
        if cursor + length > len(image):
            raise ValueError("MCUboot TLV value is out of bounds")
        value = image[cursor:cursor + length]
        cursor += length
        if kind == 0x10:
            recorded_hash = value
        elif kind == 0x22:
            signature = value
    if recorded_hash != expected_hash or signature is None:
        raise ValueError("MCUboot image hash/signature TLV is invalid")
    if len(signature) < 2 or signature[0] != 0x30 or signature[1] + 2 > len(signature):
        raise ValueError("MCUboot ECDSA signature has invalid DER framing")
    public_key = serialization.load_pem_public_key(public_pem)
    if not isinstance(public_key, ec.EllipticCurvePublicKey) or \
       not isinstance(public_key.curve, ec.SECP256R1):
        raise ValueError("MCUboot public key is not ECDSA P-256")
    public_key.verify(signature[:signature[1] + 2], hash_region, ec.ECDSA(hashes.SHA256()))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-dir", type=Path, required=True)
    parser.add_argument("--zephyr-workspace", type=Path, required=True)
    parser.add_argument("--bma456-root", type=Path, required=True)
    parser.add_argument("--lis2dw12-root", type=Path, required=True)
    parser.add_argument("--st25dvxxkc-root", type=Path, required=True)
    parser.add_argument("--flashdb-root", type=Path, required=True)
    parser.add_argument("--goodix-democode-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    build = args.build_dir.resolve()
    workspace = args.zephyr_workspace.resolve()
    bma456 = args.bma456_root.resolve()
    lis2dw12 = args.lis2dw12_root.resolve()
    st25dvxxkc = args.st25dvxxkc_root.resolve()
    flashdb = args.flashdb_root.resolve()
    goodix_democode = args.goodix_democode_root.resolve()
    verify_source_revisions(workspace)
    verify_file_source(bma456, "bosch_bma456")
    verify_file_source(lis2dw12, "st_lis2dw12")
    verify_file_source(st25dvxxkc, "st_st25dvxxkc")
    verify_file_source(flashdb, "flashdb")
    verify_file_source(flashdb, "fal")
    verify_goodix_source(goodix_democode)
    boot_dir = build / "mcuboot" / "zephyr"
    app_dir = build / "zephyr" / "zephyr"
    boot_hex = (boot_dir / "zephyr.hex").read_bytes()
    app_hex = (app_dir / "zephyr.signed.hex").read_bytes()
    boot_config = (boot_dir / ".config").read_text()
    app_config = (app_dir / ".config").read_text()
    app_map = (app_dir / "zephyr.map").read_text()
    retention = verify_reconstructed_map(app_map)
    motion_retention = verify_motion_provider_map(app_map)
    nfc_retention = verify_nfc_provider_map(app_map)
    health_storage_retention = verify_health_storage_provider_map(app_map)
    goodix_retention = verify_goodix_provider_map(app_map)

    if "CONFIG_SINGLE_APPLICATION_SLOT=y" not in boot_config or \
       "CONFIG_BOOT_VALIDATE_SLOT0=y" not in boot_config or \
       "CONFIG_BOOT_SIGNATURE_TYPE_ECDSA_P256=y" not in boot_config:
        raise ValueError("MCUboot is not the required validated single-slot ECDSA build")
    required_app_config = (
        "CONFIG_BT_CTLR=y",
        "CONFIG_BT_HCI_HOST=y",
        "CONFIG_BT_SETTINGS=y",
        "CONFIG_SETTINGS_NVS=y",
        "CONFIG_SETTINGS_NVS_SECTOR_COUNT=3",
        "CONFIG_ADC=y",
        "CONFIG_ADC_NRFX_SAADC=y",
        "CONFIG_I2C=y",
        "CONFIG_I2C_NRFX=y",
        "CONFIG_I2C_NRFX_TWIM=y",
        "CONFIG_NRFX_TWIM0=y",
        "CONFIG_NRFX_TWIM1=y",
        "CONFIG_EVENTS=y",
        "CONFIG_SYS_CLOCK_TICKS_PER_SEC=1024",
        "CONFIG_WATCHDOG=y",
        "CONFIG_WDT_NRFX=y",
        "CONFIG_SOC_DCDC_NRF52X=y",
        "CONFIG_BOOTLOADER_MCUBOOT=y",
    )
    if any(value not in app_config for value in required_app_config):
        raise ValueError("application does not contain the source Bluetooth stack + MCUboot ABI")

    boot_memory = parse_ihex(boot_hex)
    app_memory = parse_ihex(app_hex)
    require_range(boot_memory, 0, BOOT_LIMIT, "MCUboot")
    require_range(app_memory, BOOT_LIMIT, APPLICATION_LIMIT, "application")
    app_start, app_limit = min(app_memory), max(app_memory) + 1
    if len(app_memory) != app_limit - app_start:
        raise ValueError("signed application HEX is not contiguous")
    app_bin = bytes(app_memory[address] for address in range(app_start, app_limit))
    merged = merge_memory(boot_memory, app_memory)
    full_hex = write_ihex(merged)
    if app_bin[:4] != bytes.fromhex("3db8f396"):
        raise ValueError("signed application has no MCUboot image header")

    key_path = configured_key(boot_config)
    private_key = serialization.load_pem_private_key(key_path.read_bytes(), password=None)
    public_pem = private_key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    public_der = private_key.public_key().public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    if not memory_contains(boot_memory, public_der):
        raise ValueError("source-built MCUboot image does not contain the configured public key")
    verify_mcuboot_signature(app_bin, public_pem)

    artifacts = {
        "openr1-mcuboot.hex": boot_hex,
        "openr1-application.signed.hex": app_hex,
        "openr1-application.signed.bin": app_bin,
        "openr1-full.hex": full_hex,
        "mcuboot-public.pem": public_pem,
    }
    manifest = {
        "schema": 1,
        "format": "openr1-transparent-full-flash",
        "target": "openr1_nrf52840/nrf52840",
        "claim": "The executable artifacts combine the recorded openR1 source inventory with provider sources pinned in source_lock; no S140 or retail bootloader image is included or required.",
        "flash_layout": {
            "mcuboot": [0, BOOT_LIMIT],
            "application": [BOOT_LIMIT, APPLICATION_LIMIT],
            "bluetooth_settings_nvs": [SETTINGS_START, DATA_START],
            "openr1_data_preserved": [DATA_START, DATA_LIMIT],
            "migration_reserve": [DATA_LIMIT, FLASH_LIMIT],
        },
        "trust": {
            "algorithm": "ECDSA-P256-SHA256",
            "public_key_sha256": sha256(public_pem),
            "development_key": key_path.name == "root-ec-p256.pem",
        },
        "source_lock": SOURCE_LOCK,
        "openr1_source": openr1_source_inventory(),
        "reconstructed_retention": retention,
        "motion_provider_retention": motion_retention,
        "nfc_provider_retention": nfc_retention,
        "health_storage_provider_retention": health_storage_retention,
        "goodix_provider_retention": goodix_retention,
        "artifacts": {
            name: {"bytes": len(data), "sha256": sha256(data)}
            for name, data in artifacts.items()
        },
        "limitations": [
            "The development key must be replaced by an owner-controlled key before deployment.",
            "Pinned MCUboot imgtool uses randomized ECDSA nonces; signed-image and ZIP bytes are not claimed reproducible, although every generated signature and artifact hash is independently verified.",
            "The exact SAADC routes and conversions are source-bound; battery sampling uses YHM2710 shared-power client bit 0, startup adopts valid persisted type/voltage compensation, and boot plus exact device-status access refresh protocol-visible voltage and the live register-6 charge state. No unsupported autonomous cadence is invented; PMIC event-driven refresh, physical calibration, and owned-hardware validation remain open.",
            "Reset-reason capture, fatal PC/LR retention, and the recovered 10-second scheduler watchdog are source-bound but require owned-hardware fault/reset validation.",
            "The monotonic/phone-synchronized wall clock, RTC2 8-Hz backend, and reconstructed exact Unix/Gregorian query/day-boundary conversion are source-bound; wall time remains unavailable until command 0x05 supplies a valid epoch and UTC offset, and physical drift/day-boundary behavior remains an owned-hardware validation gate.",
            "REG1 startup and settings writes use the source nRF POWER HAL; wear-driven automation and physical power behavior remain hardware-validation gates.",
            "The pinned Bosch/ST motion providers, exact TWIM1 route, variant probe, reconstructed 1024-Hz sensor-stream runtime, exact 188-byte acc batch with read-only persisted axis offsets, and live GoMore acc topic listener are source-bound. Accelerometer, raw-optical, direct-HR, and HRV topics cross the exact readiness barrier and execute the complete transparent 16-stage engine plus output lifecycle; physical-axis confirmation and owned-ring validation remain open.",
            "The reconstructed software-i2c_2 GXT310 path, P1.13/P0.28 pins, two-address ID probe, signed register-0 conversion, bounded paired acquisition, read-only persisted nv_r1 calibration, exact temp/two-byte one-pair stream provider, and dormant once-listener/event-9/daily-cache path are source-bound. Final-sleep timing, construction, validation, serialization, sleep.db persistence, and synchronized commit are live; the retail physical-temperature binding remains zero until its channel semantics are proven on hardware.",
            "The IQS7211E TWIM0 transport, GPIO lifecycle, IRQ worker, restart timer, touchSwitch hook, and YHM2710 client-bit-2 lease are source-bound; ring identity and wear/factory provisioning remain fail-closed, and physical touch behavior is not hardware-validated.",
            "The exact one-byte r_size class is decoded read-only with its 6...15 gate, but ring size alone is not used to infer the independent IQS7211E physical layout.",
            "The pinned ST25DVxxKC provider, bounded mailbox adapter, P0.03 GPO worker, P1.10 dock lifecycle, dock-session mutex, and motion/NFC TWIM1 handoff are source-bound; NFC starts disabled pending an explicit product activation policy.",
            "Pinned FlashDB 2.0.0/FAL 0.5.99 binds the recovered six-page health.db TSDB, exact startup/cache restore, exact 128-byte codec, local-day recovery, non-destructive slot-1 hourly appends, and the exact slot-0 tuple for recovery/reset. The 24-byte hsync class is losslessly loaded and persisted through hardened kv.bin snapshots; only the four named cursors mutate and both unresolved words are preserved. Authenticated HR/SpO2/HRV/activity daily queries bind their exact oldest-first UInt8/UInt16/packed-activity merge callbacks over the recovered 259200-second FlashDB window, merge each invalid-clock FIFO, append current RAM, advance the named hsync cursor only after matching mode-0/2 packet ACKs, and consume only the acknowledged FIFO prefix for mode 1. Dispatch composition accounts for encoded fragment cost before model admission; an activity traversal that reaches the recovered 50-record shared-queue boundary completes as an ACK-resumable page. The admitted wall-clock cadence drives the exact 10800-second automatic HR/SpO2/HRV/activity/unsynchronized-sleep order through a bounded one-leg-at-a-time service that requires an encrypted, bonded, authorized phone role and preserves the recovered 50-record queue. Public health-settings use their exact canonical planner, queue ACK before effects, persist normalized timestamp/enable transitions into dev_info while preserving REG1, and reconcile the exact seven-slot GoMore gate. The backward-clock and failure-60 reset paths now perform a typed fresh-engine reinitialization without resume state. Cumulative activity enters the exact ten-minute/daily accumulator and final sleep enters sleep.db. Temperature serializes only after an explicitly started one-shot completes, stress remains zero without a stock-live producer, and neither module-owned cache is restored by the crash record; destructive format/retry, migration, and owned-hardware power-loss behavior remain intentionally suppressed or open.",
            "The pinned source-only Goodix demo/driver subset, recovered i2c_4 transport, P0.21/P0.10/P1.04 board resources, interrupt worker, and YHM2710 client bit 1 are bound; the exact product-side raw_hr/adt/living-object record producers compile from transparent source. Binary archives are excluded and the 20-row global frame/result ABI is normalized through a bounded vendor-free provider contract. Checked constructors reproduce the independent HR/HBA mapped input, HRV direct raw/AGC/last-HR input, and SpO2 mapped raw/AGC input; the retained source composer owns their exact lifecycle and publication records: HR mask 0x003F/six words, HRV mask 0x007F/seven slots with slot 6 zero, and the retail-R1 SpO2 divergence mask 0x00FF/eight slots with slot 6 mirroring slot 0 and slot 7 zero. It also preserves the HR-to-HRV carry. Canonical retail roots are HBA 0x6C6A8, HRV 0x6D51C, and SpO2 0x6E838. All three transparent persistent root executors are target-bound; validated HR, SpO2, and HRV publications route through recovered planners into scalar storage and GoMore topics behind the persisted health gate. Optical wavelength, electrical calibration, and biometric equivalence remain owned-hardware validation gates.",
            "The reconstructed YHM2710 P1.01 transport, initialization, and three-client shared-power lease are source-bound; battery, optical, and touch clients are adopted, while all physical power behavior remains hardware-validation work; kv.bin, health.db, and sleep.db are source-bound.",
            "Zephyr NVS does not claim compatibility with retail Nordic FDS settings; migration or clearing behavior requires owned-hardware validation.",
            "The former retail bootloader window is reserved until a migration procedure is hardware-tested.",
        ],
    }
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, "w") as archive:
        zip_member(archive, "manifest.json", manifest_bytes)
        for name in sorted(artifacts):
            zip_member(archive, name, artifacts[name])
    print(
        f"openR1 source-built bundle: {args.output} "
        f"({len(boot_memory)} boot bytes, {len(app_memory)} signed application bytes)"
    )


if __name__ == "__main__":
    main()
