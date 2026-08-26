#!/usr/bin/env python3
"""Offline fail-closed verification of the TDK ICM45608 source snapshot."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXPECTED_REPOSITORY = "https://github.com/tdk-invn-oss/motion.arduino.ICM45608.git"
EXPECTED_COMMIT = "b79ae575f7f310e5ae2e1164096d1a858bb74662"
EXPECTED_TAG = "1.1.2"
EXPECTED_FILE_COUNT = 52
EXPECTED_TOTAL_BYTES = 594_177
EXPECTED_AGGREGATE = "cc6088eed9f14a02af419a29856064ab62e4b79e2860a135e1d84ba22e1c9570"
EXPECTED_PINS = {
    "LICENSE": (1503, "68bed9c72222b77b8744add292f524000661c6537d960adeaf740722b0b2637f"),
    "src/imu/inv_imu_driver.c": (22499, "5c376ad072ed547c8e76666921174263f0301dc06cd711adac8aeb862bea056c"),
    "src/imu/inv_imu_driver_advanced.c": (47074, "1fbccba412f07f11cefdf96004c249693edc3389c12abf54fe771332a5610435"),
    "src/imu/inv_imu_edmp.c": (74658, "373083ef6e4e8be3a56e78c3c2c67b5babdc61b3b58f66dcd58dca607e7a5543"),
    "src/imu/inv_imu_edmp_extended_features.c": (22540, "3ec33b2261fdbb05dffcb099cfaa2ca3e5117d8c0a8a5503db29f4ddaa037dc7"),
    "src/invn_mag.c": (7380, "fdbd5967bbca8d8b1d8896333ca3920021434b024059a8d000afbe439ba5a334"),
    "src/Ict1531x/Ict1531x.c": (8029, "f7270007d9976766ad8944160b15c3fa11301dc109aa43f9cdb0502b309343c2"),
    "src/Ict1531x/Ict1531x.h": (7758, "fb6425ab33bed148d55ca9ce44b08cb66edff21fc5002d7ddab1eef30d41605a"),
    "src/Invn/InvError.h": (2340, "01478bb0209c1e502ce2c8a4cf66dea8cbf3930953da834135cb2faa5007c896"),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"ICM45608 snapshot verification failed: {message}")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def upstream_files() -> list[Path]:
    files = [HERE / "LICENSE", *(HERE / "src").rglob("*")]
    return sorted(path for path in files if path.is_file())


def aggregate(files: list[Path]) -> tuple[int, str]:
    result = hashlib.sha256()
    total = 0
    for path in files:
        relative = path.relative_to(HERE).as_posix().encode("utf-8")
        data = path.read_bytes()
        total += len(data)
        result.update(len(relative).to_bytes(4, "little"))
        result.update(relative)
        result.update(len(data).to_bytes(8, "little"))
        result.update(data)
    return total, result.hexdigest()


def main() -> int:
    provenance = json.loads((HERE / "PROVENANCE.json").read_text(encoding="utf-8"))
    upstream = provenance["upstream"]
    selection = provenance["selection"]
    require(provenance["schema_version"] == 1, "schema changed")
    require(provenance["license"] == "BSD-3-Clause", "license changed")
    require(upstream["repository"] == EXPECTED_REPOSITORY, "repository changed")
    require(upstream["tag"] == EXPECTED_TAG, "tag changed")
    require(upstream["commit"] == EXPECTED_COMMIT, "commit changed")
    require(upstream["driver_version"] == "1.1.0", "driver version changed")
    files = upstream_files()
    total, tree_digest = aggregate(files)
    require(len(files) == EXPECTED_FILE_COUNT, "file inventory changed")
    require(total == EXPECTED_TOTAL_BYTES, "source byte count changed")
    require(tree_digest == EXPECTED_AGGREGATE, "source aggregate changed")
    require(selection["file_count"] == EXPECTED_FILE_COUNT, "recorded file count changed")
    require(selection["total_bytes"] == EXPECTED_TOTAL_BYTES, "recorded byte count changed")
    require(selection["aggregate_sha256"] == EXPECTED_AGGREGATE, "recorded aggregate changed")
    for name, expected in EXPECTED_PINS.items():
        data = (HERE / name).read_bytes()
        require((len(data), digest(data)) == expected, f"{name} changed")

    transport = (HERE / "src/imu/inv_imu_transport.h").read_text(encoding="utf-8")
    driver = (HERE / "src/imu/inv_imu_driver.h").read_text(encoding="utf-8")
    edmp = (HERE / "src/imu/inv_imu_edmp.c").read_text(encoding="utf-8")
    extended = (HERE / "src/imu/inv_imu_edmp_extended_features.c").read_text(encoding="utf-8")
    require("void *              context" not in transport, "newer context ABI appeared")
    for marker in ("inv_imu_read_reg_t  read_reg", "inv_imu_write_reg_t write_reg",
                   "uint32_t            serif_type", "void (*sleep_us)(uint32_t us)"):
        require(marker in transport, f"transport marker missing: {marker}")
    for marker in ("uint8_t fifo_frame_size", "uint8_t endianness_data",
                   "uint8_t edmp_gaf_mode", "uint64_t adv_var[6]"):
        require(marker in driver, f"device marker missing: {marker}")
    for marker in ("inv_imu_edmp_gaf_decode_fifo", "inv_imu_edmp_set_gaf_mode",
                   "inv_imu_edmp_start_gaf_fifo_push"):
        require(marker in edmp, f"GAF marker missing: {marker}")
    for marker in ("inv_imu_edmp_aid_enable", "inv_imu_edmp_b2s_enable"):
        require(marker in extended, f"extended-feature marker missing: {marker}")
    license_text = (HERE / "LICENSE").read_text(encoding="utf-8")
    require("BSD 3-Clause License" in license_text, "BSD license marker missing")
    print("TDK ICM45608 1.1.2 snapshot: PASS")
    print(f"files={len(files)} bytes={total} aggregate={tree_digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
