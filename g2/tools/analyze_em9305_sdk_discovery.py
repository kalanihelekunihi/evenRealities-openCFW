#!/usr/bin/env python3
"""Validate and summarize the expanded EM9305 SDK archive match census."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = ROOT / "blobs/official/g2-2.2.6.10/firmware_ble_em9305.bin"
DEFAULT_MANIFEST = ROOT / "tools/manifests/em9305-sdk-discovery.tsv"
DEFAULT_ROUND2_MANIFEST = ROOT / "tools/manifests/em9305-sdk-discovery-round2.tsv"
DEFAULT_COMPARATOR = ROOT / "tools/compare_em9305_sdk_archive.py"
DEFAULT_RUNNER = ROOT / "tools/run_em9305_sdk_archive_batch.py"
IMAGE_SHA256 = "91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9"
APP_BASE = 0x0030_2400
APP_FILE_OFFSET = 0x424
APP_SIZE = 210_888
EXPECTED_INPUTS_SHA256 = "4cd26a8f8a8843d4b9e8321b30bfc1c92b9c77aceab8bbce22719b9e35d6a6ae"
EXPECTED_CONFIG_SHA256 = "aca2b78f5db46a399dbb6080ea9157ca6d3a8c48cb97ebd7a599af74388dff50"
EXPECTED_REPORT_SHA256 = {
    "app_entry": "89f51de5cd749f3f49b63ad07c47b5f11ea8750955898146d0f867815d33332b",
    "em_core": "6f49ee753cba0882a0eb40fc66cf00c485a789275f6a5829f9698548f9b05e9e",
    "em_hw_api": "8c501926a8950b2086106144a03283eea7641143f4c4aeb57bc56496dcd3fd77",
    "em_system": "b0f868849611b734c2a573f0c8373a4d4121572cdf6c625a73299bb996777708",
    "em_system_stack": "d02ed501ebf6e4a81f3a1dc5d038d900c3b3a7d46e96bd5e0f2ae62ffd5aaedc",
    "memory_manager": "d4b12043265376f580858259894b021d843c26f14def95ba9c1ba84c4f7e45b9",
    "nvm_fix": "5acb80e3dee07e408c5234dd98121e85852699ab9bcff7ad397102fb828805ab",
    "nvm_entry": "331a110b0a4bffa90e6822b525eeae1fbad3f7091ad77b25bf423dfd65ebb054",
    "radio": "e3bb729a1ee7c47b46cf84347e0b0cc3c94ece6d0c3d90cec390e757fb69f55f",
    "rc_calib": "032badc6aa95a14705b8db74b0e53ab3fa2116f2ce72c027a66c68cae012274a",
    "rtc": "48e58d68f0ebf48af194a36f1b0b704dea38a7a1db5dabe3fb27cb3b85853665",
    "emb_controller": "d9320ce9cc048ff7adc88252aa4886810a3e9f0935eca8012c3de8fc6e6ad0ba",
    "emb_database": "cf4e1f227e30084f428721d8f2b3c40b99b161b31de47fd6bef632c5bba4d877",
    "emb_ll_pal": "1565c05cdf96d901b86e0362e6f29bfda9b6fcb690125a60544b6b27efe609a8",
    "emb_peripheral": "56625d6bc61fbc9671a9714a740b388ab4518e6927bd068b606cbf23cfd455de",
    "transport": "6ba1e79739e7887d72f73b848e03dc704f58ecf6bacff2b95e1599f676806dbe",
}
EXPECTED_RECORD_COUNTS = {
    "app_entry": 3,
    "em_core": 3,
    "em_hw_api": 37,
    "em_system": 27,
    "em_system_stack": 2,
    "memory_manager": 0,
    "nvm_fix": 3,
    "nvm_entry": 1,
    "radio": 34,
    "rc_calib": 2,
    "rtc": 0,
    "emb_controller": 1057,
    "emb_database": 0,
    "emb_ll_pal": 30,
    "emb_peripheral": 980,
    "transport": 1,
}
EXPECTED_CRITICAL_NAMES = {
    0x0030_2AE8: "BOOT_BootUp",
    0x0030_32CC: "BbBleInit",
    0x0030_B974: "LlExtCreateConnV2",
    0x0030_FB4C: "PalBbBleSetChannelParam",
    0x0031_028C: "PalRadioInit",
    0x0031_3F54: "WsfCsEnter",
    0x0031_40D0: "WsfOsStartOnly",
    0x0033_3C44: "wsfDispatcherThread",
}
EXPECTED_DISTINCT_FUNCTIONS = 1_146
EXPECTED_FUNCTION_BYTES = 132_610
KNOWN_ENFORCED_FUNCTIONS = 98
KNOWN_ENFORCED_BYTES = 7_172
EXPECTED_ROUND2_INPUTS_SHA256 = "5213cd19fb8d5aa2fcb895a750a5c77e345ff0fc4116a0580994c85d2015f755"
EXPECTED_ROUND2_REPORT_SHA256 = {
    "adc": "3bedc8f286471d28fb9fcd54db5dec6138bbbed5b13487c50072b9c6ecb46ce2",
    "aoad": "1dd19b799df30c2fb8d989758ad0fce1f19d811550fcd2bbc7417b7b92e6d96d",
    "dma": "7eeaaa3b4cdbacadf614e0b465b43ea1a9ef4bac2464879246c922a9039c4b03",
    "em_hw_api_di03": "db05b01ddbcedd4186000be61ed482fa76c99ba13f5517c62d64246fc3efe022",
    "em_system_di03": "ee3c81752dce574a3b6b147578dd81d12add7ae2a3fbb366a5fc8ccfb35c2149",
    "em_system_di04": "04d2540c12cd0c0f2321e7bb50d90b06a9f06d1fedd2cf51cccd648a1cc17724",
    "em_system_emcore": "7d622b90c114587c3617eef454d2f2ec2a51c59ec942dfda6806a90fe19b74a3",
    "firmware_update_core": "786cdbcc097f3ac8a9d9700dccf478b14bca12e0236d39bca905d69ebae29a04",
    "firmware_update_crypto": "db2927de58aab4100f0e5961d40e05bc360d6ac97969cfd4f300976102429656",
    "gpio": "fe17db0705e8ab1a2a97274aa57efc90dce77238b913c58e31b3945512c24a0b",
    "i2c": "fedd8f1d124d390798bfc6c551b86c4332fc2800b7aa3b64f7114ace25cf66ad",
    "i2s": "1fbab9ef86534eaa34df2e39602a11619208d5e125a8fbc816dff922e845b631",
    "nvm_op_sched": "1b1eb2fec5b257101c4c68dc0a93f56f24b70f828cd2b16ec3f42719bfcde266",
    "pml_di03": "99f23bae581422185362e6f11ed0afa0fd923a0d6c4f4f9e1582b43400650d4f",
    "qdec": "ff72bc5f9192466f12ec716ab18e13c201fa3ae411231748608059c7eaa589ec",
    "hw_security": "cde0aea5eab1e3e52206ed07a38b8152cfd31f53e8fa31f12367eec111477d89",
    "spi_master": "a82c16c2e132f7732cccb105a69be5cb6b31068e0a6b6ea3cb4db51980289417",
    "spi_slave": "e979614ecbd011ff97972967e04cbbe3701cec1880e4d4b2a3822dab5e54f465",
    "spi_slave_dma": "4bdf33cc17c8c9bcac8870e329afa0c503a6fb24fb6705a425a0306d64ee4ef9",
    "temperature_indicator": "636b1e2d7c78746fa156347ef1e7ebe0bfc64aa02d965fcc98674bc1e9c5c305",
    "emb_audio": "c0dba798d2b5f95f36b0090dcbe8eec028c977a1930e9d73d3868af050dc0033",
    "emb_central": "738705f587d22cf6baf6c8660398abf577b2170cdc9b8a34049b7c1230d977c4",
    "emb_central_advext": "ac8ae657a4f9b1a7fd87d5199b084674058c1834d09af725c0a23cd38aa44a8f",
    "emb_controller_iso": "26b727f717ff948229d6a455378355ece727635d77af20c83dc11ab5b6e57c69",
    "emb_cte_transmitter": "4c2eaab9184258a5970f6cce2b69da2c0dd643962370a9debe0199a6d66256c1",
    "emb_pawr_advertiser": "f37bd0932ccf2923d6886a7102824f63fa55dc219d5c4fa4da2d599290faaedb",
    "emb_pawr_synchronizer": "7715cc810ba89ef8365216cc4c7808f6d63861f8a7ee8ff6745f4e2c8340eed9",
    "emb_peripheral_advext": "1b8e913c4e39a9c4f43d1a76e8d8d7d977f6eaf128ea86faa964dff63b0fa96d",
    "emb_peripheral_legacy": "dbc0d288c8cd1cc4d3922a85ea765eaa69ceaac3de30033f8edd826e0b88ae8b",
    "printf": "390e80da6070dc0f200e9ab801c5677c4bec5bb56e04e9199edf47912aeae252",
    "uart": "8458098bd32d78e2d2ef27235bfc900ce53ffb4a2015a4e68e53ca8119e18062",
    "uart_dma": "c972ba6331b4a7880582f34d2d30ab86b9be94e0d4dbfca794c40adbefecc566",
}
EXPECTED_ROUND2_RECORD_COUNTS = {
    "adc": 0, "aoad": 1, "dma": 0, "em_hw_api_di03": 36,
    "em_system_di03": 31, "em_system_di04": 27, "em_system_emcore": 26,
    "firmware_update_core": 0, "firmware_update_crypto": 0, "gpio": 0,
    "i2c": 0, "i2s": 0, "nvm_op_sched": 0, "pml_di03": 32,
    "qdec": 0, "hw_security": 0, "spi_master": 0, "spi_slave": 0,
    "spi_slave_dma": 0, "temperature_indicator": 0, "emb_audio": 1025,
    "emb_central": 980, "emb_central_advext": 980,
    "emb_controller_iso": 1119, "emb_cte_transmitter": 669,
    "emb_pawr_advertiser": 1041, "emb_pawr_synchronizer": 1041,
    "emb_peripheral_advext": 980, "emb_peripheral_legacy": 554,
    "printf": 0, "uart": 0, "uart_dma": 0,
}
EXPECTED_ENFORCED_REPORT_SHA256 = {
    "pml": "45ed3f1c6ea9527d599dfce60198154f3186106facc4f95dcea151610794422e",
    "prot_timer": "6b24754690f579d5620bec1d0dcc9ec0dcf6a866d1f4d8290d900dee05ec66e0",
    "qpc": "3c7681fd4f3c9c1bfd35991a92b000a5728c832d4b4ab890fed228850e0a369f",
    "sleep_manager": "3b735acf3ae18c788dab38740d0ba6a68fd314cbd9551b80e28f6b6a4128b729",
    "sleep_timer": "5cbacaac491684368ad6db5fa00e71b3045cf4d58b5e6e7dcf9b1da9bf591bb5",
    "unitimer": "248eac075bbe4845f316eb19f0762fdcafb796635a34aa1e02645a49b8415d27",
}
EXPECTED_ROUND2_DISTINCT_FUNCTIONS = 1_201
EXPECTED_ROUND2_FUNCTION_BYTES = 144_740
EXPECTED_ROUND2_NEW_FUNCTIONS = 67
EXPECTED_ROUND2_NEW_BYTES = 13_078
EXPECTED_ALL_FUNCTIONS = 1_311
EXPECTED_ALL_BYTES = 152_860
EXPECTED_MIN8_CONFIG_SHA256 = "7f77b2c1ee63b5d84a1775aaca1491dcb9624cb61852ec3371cf05d401d15b9d"
EXPECTED_ROUND1_MIN8_INPUTS_SHA256 = "49f2342424c6691dfa2b585ed4430a624d4c3dbdbbf085107f25643e5f710c50"
EXPECTED_ROUND1_MIN8_CHECKSUMS_SHA256 = "6df037edc55e1b3419147d13c57eddd8f33826ca9f718c98391e6577944e87f7"
EXPECTED_ROUND2_MIN8_INPUTS_SHA256 = "148aef0872acd533995c0dd3b9d9ff8e91947dc6b856300cc508b84c5e2fd68e"
EXPECTED_ROUND2_MIN8_CHECKSUMS_SHA256 = "34a29df939004dc1d38bcaefd1bbb9800c0ce189ac9678298342be307a484db9"
EXPECTED_APPLICATION_OBJDUMP_SHA256 = "13d1e9c7c0d2c2d3db9436d21ec6d90a39622446cb8ab96de5c2c01ba752916f"
EXPECTED_ROUND1_MIN8_RECORDS = 2_441
EXPECTED_ROUND2_MIN8_RECORDS = 9_607
EXPECTED_LOW_FLOOR_CANDIDATES = 129
EXPECTED_LOW_FLOOR_CANDIDATE_BYTES = 2_196
EXPECTED_LOW_FLOOR_PROMOTED = 124
EXPECTED_LOW_FLOOR_PROMOTED_BYTES = 2_106
EXPECTED_LOW_FLOOR_REJECTED = {
    0x0031_2260: "TI_RegisterModule",
    0x0031_9958: "lctrExtAdvActAdvTerm",
    0x0032_CA90: "lctrStoreDisconnectReason",
    0x0032_CFF2: "lctrCisLlcpActIntPeerDisc",
    0x0032_D0F4: "lctrTransferSyncActCancel",
}
EXPECTED_LOW_FLOOR_ALL_FUNCTIONS = 1_435
EXPECTED_LOW_FLOOR_ALL_BYTES = 154_966
EXPECTED_LOW_FLOOR_ALL_INTERVALS = 867
PACKAGE_MAP_BASE = 0x0030_1FDC


class AuditError(RuntimeError):
    """Raised when an evidence identity or map invariant changes."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_manifest(path: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    with path.open(newline="") as stream:
        for fields in csv.reader(stream, delimiter="\t"):
            if not fields or fields[0].startswith("#"):
                continue
            label, source_path, git_blob, digest, size = fields
            result[label] = {
                "path": source_path,
                "git_blob": git_blob,
                "sha256": digest,
                "size": int(size),
            }
    return result


def verify_checksum_manifest(output: Path) -> None:
    for line in (output / "SHA256SUMS").read_text().splitlines():
        digest, relative = line.split("  ", 1)
        path = output / relative
        if output not in path.resolve().parents or not path.is_file():
            raise AuditError(f"unsafe or missing batch artifact: {relative}")
        if sha256_file(path) != digest:
            raise AuditError(f"batch artifact checksum mismatch: {relative}")


def merge_intervals(intervals: Sequence[tuple[int, int]]) -> list[tuple[int, int]]:
    merged: list[list[int]] = []
    for start, end in sorted(intervals):
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    return [(start, end) for start, end in merged]


def add_function(
    functions: dict[int, dict[str, Any]],
    *,
    address: int,
    size: int,
    normalized_sha256: str,
    name: str,
    archive: str,
) -> bool:
    """Add an address/body identity, rejecting ambiguous cross-archive claims."""
    if address < APP_BASE or address + size > APP_BASE + APP_SIZE:
        raise AuditError(f"SDK match outside application: {archive}/{name}")
    existing = functions.get(address)
    if existing is None:
        functions[address] = {
            "address": address,
            "end": address + size,
            "size": size,
            "normalized_sha256": normalized_sha256,
            "names": {name},
            "archives": {archive},
        }
        return True
    if (existing["size"], existing["normalized_sha256"]) != (
        size,
        normalized_sha256,
    ):
        raise AuditError(f"conflicting SDK bodies at 0x{address:08X}")
    existing["names"].add(name)
    existing["archives"].add(archive)
    return False


def analyze_round2(
    baseline_output: Path,
    enforced_output: Path,
    round2_output: Path,
    *,
    image: Path = DEFAULT_IMAGE,
    baseline_manifest_path: Path = DEFAULT_MANIFEST,
    round2_manifest_path: Path = DEFAULT_ROUND2_MANIFEST,
    include_functions: bool = False,
) -> dict[str, Any]:
    """Authenticate and deduplicate the two discovery rounds plus six enforced lanes."""
    baseline = analyze(
        baseline_output,
        image=image,
        manifest_path=baseline_manifest_path,
        include_functions=True,
    )
    functions: dict[int, dict[str, Any]] = {}
    for item in baseline["functions"]:
        add_function(
            functions,
            address=item["address"],
            size=item["size"],
            normalized_sha256=item["normalized_sha256"],
            name=item["names"][0],
            archive=f"round1:{item['archives'][0]}",
        )

    enforced_output = enforced_output.resolve()
    enforced_count = 0
    enforced_bytes = 0
    for label, expected_digest in EXPECTED_ENFORCED_REPORT_SHA256.items():
        report_path = enforced_output / f"{label}.json"
        if sha256_file(report_path) != expected_digest:
            raise AuditError(f"enforced SDK deterministic report changed: {label}")
        report = json.loads(report_path.read_text())
        if not report["identity"]["compiler_anchors_matched"]:
            raise AuditError(f"enforced SDK compiler identity mismatch: {label}")
        for match in report["functions"]:
            if (
                match.get("expected_match_kind") != "exact"
                or not match.get("expected_address_matched")
            ):
                continue
            enforced_count += 1
            enforced_bytes += match["size"]
            add_function(
                functions,
                address=match["expected_stock_address"],
                size=match["size"],
                normalized_sha256=match["normalized_sha256"],
                name=match["name"],
                archive=f"enforced:{label}",
            )
    if (enforced_count, enforced_bytes) != (
        KNOWN_ENFORCED_FUNCTIONS,
        KNOWN_ENFORCED_BYTES,
    ):
        raise AuditError("six-lane enforced SDK coverage changed")
    if len(functions) != EXPECTED_DISTINCT_FUNCTIONS + KNOWN_ENFORCED_FUNCTIONS:
        raise AuditError("round-one/enforced function sets unexpectedly overlap")

    round2_output = round2_output.resolve()
    round2_manifest_path = round2_manifest_path.resolve()
    if sha256_file(round2_output / "INPUTS.tsv") != EXPECTED_ROUND2_INPUTS_SHA256:
        raise AuditError("round-two SDK batch input ledger changed")
    if sha256_file(round2_output / "CONFIG.json") != EXPECTED_CONFIG_SHA256:
        raise AuditError("round-two SDK batch configuration changed")
    verify_checksum_manifest(round2_output)
    config = json.loads((round2_output / "CONFIG.json").read_text())
    if config["minimum_compared_bytes"] != 16 or config["jobs"] != 16:
        raise AuditError("round-two SDK batch must use 16-byte/16-job configuration")
    manifest = parse_manifest(round2_manifest_path)
    if set(manifest) != set(EXPECTED_ROUND2_REPORT_SHA256):
        raise AuditError("round-two SDK archive manifest membership changed")
    inputs = dict(
        line.split("\t", 1)[::-1]
        for line in (round2_output / "INPUTS.tsv").read_text().splitlines()
    )
    expected_inputs = {
        "runner": sha256_file(DEFAULT_RUNNER),
        "comparator": sha256_file(DEFAULT_COMPARATOR),
        "firmware": IMAGE_SHA256,
        "manifest": sha256_file(round2_manifest_path),
        "configuration": EXPECTED_CONFIG_SHA256,
    }
    expected_inputs.update(
        {f"archive:{label}": item["sha256"] for label, item in manifest.items()}
    )
    if inputs != expected_inputs:
        raise AuditError("round-two batch inputs do not match authenticated sources")

    round2_functions: dict[int, dict[str, Any]] = {}
    archive_counts: dict[str, int] = {}
    record_count = 0
    for label, expected_digest in EXPECTED_ROUND2_REPORT_SHA256.items():
        report_path = round2_output / "reports" / f"{label}.json"
        if sha256_file(report_path) != expected_digest:
            raise AuditError(f"round-two deterministic report changed: {label}")
        report = json.loads(report_path.read_text())
        identity = report["identity"]
        if (
            identity["archive_path"] != manifest[label]["path"]
            or identity["archive_git_blob"] != manifest[label]["git_blob"]
            or identity["archive_sha256"] != manifest[label]["sha256"]
            or not identity["compiler_anchors_matched"]
        ):
            raise AuditError(f"round-two report identity mismatch: {label}")
        matches = report["unique_discovered_matches"]
        if len(matches) != EXPECTED_ROUND2_RECORD_COUNTS[label]:
            raise AuditError(f"round-two match count changed: {label}")
        archive_counts[label] = len(matches)
        record_count += len(matches)
        for match in matches:
            if len(match["matches"]) != 1 or match["compared_byte_count"] < 16:
                raise AuditError(f"weak or non-unique round-two match: {label}/{match['name']}")
            add_function(
                round2_functions,
                address=match["matches"][0],
                size=match["size"],
                normalized_sha256=match["normalized_sha256"],
                name=match["name"],
                archive=label,
            )
    if record_count != sum(EXPECTED_ROUND2_RECORD_COUNTS.values()):
        raise AuditError("round-two raw match count changed")
    round2_merged = merge_intervals(
        [(item["address"], item["end"]) for item in round2_functions.values()]
    )
    if (
        len(round2_functions) != EXPECTED_ROUND2_DISTINCT_FUNCTIONS
        or sum(item["size"] for item in round2_functions.values())
        != EXPECTED_ROUND2_FUNCTION_BYTES
        or sum(end - start for start, end in round2_merged)
        != EXPECTED_ROUND2_FUNCTION_BYTES
    ):
        raise AuditError("round-two exact function coverage changed or overlaps")

    baseline_addresses = set(functions)
    new_functions: list[dict[str, Any]] = []
    for address, item in sorted(round2_functions.items()):
        is_new = address not in baseline_addresses
        add_function(
            functions,
            address=address,
            size=item["size"],
            normalized_sha256=item["normalized_sha256"],
            name=sorted(item["names"])[0],
            archive=f"round2:{sorted(item['archives'])[0]}",
        )
        if is_new:
            new_functions.append(item)
    if (
        len(new_functions) != EXPECTED_ROUND2_NEW_FUNCTIONS
        or sum(item["size"] for item in new_functions) != EXPECTED_ROUND2_NEW_BYTES
    ):
        raise AuditError("round-two incremental coverage changed")
    combined_merged = merge_intervals(
        [(item["address"], item["end"]) for item in functions.values()]
    )
    combined_union_bytes = sum(end - start for start, end in combined_merged)
    if len(functions) != EXPECTED_ALL_FUNCTIONS or combined_union_bytes != EXPECTED_ALL_BYTES:
        raise AuditError("combined SDK coverage changed or overlaps")

    def public(item: dict[str, Any]) -> dict[str, Any]:
        return {
            **{key: value for key, value in item.items() if key not in {"names", "archives"}},
            "names": sorted(item["names"]),
            "archives": sorted(item["archives"]),
        }

    return {
        "round2_archive_count": len(manifest),
        "round2_match_record_count": record_count,
        "round2_distinct_function_count": len(round2_functions),
        "round2_exact_function_bytes": EXPECTED_ROUND2_FUNCTION_BYTES,
        "round2_baseline_duplicate_function_count": len(round2_functions) - len(new_functions),
        "round2_new_function_count": len(new_functions),
        "round2_new_function_bytes": EXPECTED_ROUND2_NEW_BYTES,
        "combined_exact_function_count": len(functions),
        "combined_exact_function_bytes": combined_union_bytes,
        "combined_application_percent": combined_union_bytes / APP_SIZE * 100.0,
        "application_bytes_not_exact_function_matched": APP_SIZE - combined_union_bytes,
        "application_percent_not_exact_function_matched": (APP_SIZE - combined_union_bytes) / APP_SIZE * 100.0,
        "combined_merged_interval_count": len(combined_merged),
        "archive_match_record_counts": archive_counts,
        "functions": [public(item) for _address, item in sorted(functions.items())]
        if include_functions else [],
        "new_functions": [public(item) for item in new_functions] if include_functions else [],
    }


def load_min8_batch(
    output: Path,
    manifest_path: Path,
    *,
    expected_inputs_sha256: str,
    expected_checksums_sha256: str,
    expected_record_count: int,
    batch_label: str,
) -> tuple[dict[int, dict[str, Any]], int]:
    """Authenticate one eight-byte-floor batch and return address/body identities."""
    output = output.resolve()
    manifest_path = manifest_path.resolve()
    if sha256_file(output / "INPUTS.tsv") != expected_inputs_sha256:
        raise AuditError(f"{batch_label} min8 input ledger changed")
    if sha256_file(output / "CONFIG.json") != EXPECTED_MIN8_CONFIG_SHA256:
        raise AuditError(f"{batch_label} min8 configuration changed")
    if sha256_file(output / "SHA256SUMS") != expected_checksums_sha256:
        raise AuditError(f"{batch_label} min8 checksum ledger changed")
    verify_checksum_manifest(output)
    config = json.loads((output / "CONFIG.json").read_text())
    if config["minimum_compared_bytes"] != 8 or config["jobs"] != 16:
        raise AuditError(f"{batch_label} min8 batch must use 8-byte/16-job configuration")
    manifest = parse_manifest(manifest_path)
    inputs = dict(
        line.split("\t", 1)[::-1]
        for line in (output / "INPUTS.tsv").read_text().splitlines()
    )
    expected_inputs = {
        "runner": sha256_file(DEFAULT_RUNNER),
        "comparator": sha256_file(DEFAULT_COMPARATOR),
        "firmware": IMAGE_SHA256,
        "manifest": sha256_file(manifest_path),
        "configuration": EXPECTED_MIN8_CONFIG_SHA256,
    }
    expected_inputs.update(
        {f"archive:{label}": item["sha256"] for label, item in manifest.items()}
    )
    if inputs != expected_inputs:
        raise AuditError(f"{batch_label} min8 inputs do not match authenticated sources")

    functions: dict[int, dict[str, Any]] = {}
    record_count = 0
    for label, item in manifest.items():
        report = json.loads((output / "reports" / f"{label}.json").read_text())
        identity = report["identity"]
        if (
            identity["archive_path"] != item["path"]
            or identity["archive_git_blob"] != item["git_blob"]
            or identity["archive_sha256"] != item["sha256"]
            or not identity["compiler_anchors_matched"]
        ):
            raise AuditError(f"{batch_label} min8 report identity mismatch: {label}")
        for match in report["unique_discovered_matches"]:
            record_count += 1
            if len(match["matches"]) != 1 or match["compared_byte_count"] < 8:
                raise AuditError(f"weak/non-unique {batch_label} min8 match: {label}/{match['name']}")
            add_function(
                functions,
                address=match["matches"][0],
                size=match["size"],
                normalized_sha256=match["normalized_sha256"],
                name=match["name"],
                archive=f"{batch_label}:{label}",
            )
    if record_count != expected_record_count:
        raise AuditError(f"{batch_label} min8 raw match count changed")
    return functions, record_count


def analyze_low_floor(
    baseline_output: Path,
    enforced_output: Path,
    round2_output: Path,
    round1_min8_output: Path,
    round2_min8_output: Path,
    application_objdump: Path,
    *,
    image: Path = DEFAULT_IMAGE,
    baseline_manifest_path: Path = DEFAULT_MANIFEST,
    round2_manifest_path: Path = DEFAULT_ROUND2_MANIFEST,
    include_functions: bool = False,
) -> dict[str, Any]:
    """Promote low-floor matches only with independent boundary/xref evidence."""
    authoritative = analyze_round2(
        baseline_output,
        enforced_output,
        round2_output,
        image=image,
        baseline_manifest_path=baseline_manifest_path,
        round2_manifest_path=round2_manifest_path,
        include_functions=True,
    )
    known = {
        item["address"]: {
            **item,
            "names": set(item["names"]),
            "archives": set(item["archives"]),
        }
        for item in authoritative["functions"]
    }
    round1_min8, round1_records = load_min8_batch(
        round1_min8_output,
        baseline_manifest_path,
        expected_inputs_sha256=EXPECTED_ROUND1_MIN8_INPUTS_SHA256,
        expected_checksums_sha256=EXPECTED_ROUND1_MIN8_CHECKSUMS_SHA256,
        expected_record_count=EXPECTED_ROUND1_MIN8_RECORDS,
        batch_label="round1",
    )
    round2_min8, round2_records = load_min8_batch(
        round2_min8_output,
        round2_manifest_path,
        expected_inputs_sha256=EXPECTED_ROUND2_MIN8_INPUTS_SHA256,
        expected_checksums_sha256=EXPECTED_ROUND2_MIN8_CHECKSUMS_SHA256,
        expected_record_count=EXPECTED_ROUND2_MIN8_RECORDS,
        batch_label="round2",
    )
    low_floor: dict[int, dict[str, Any]] = {}
    for batch in (round1_min8, round2_min8):
        for address, item in batch.items():
            if address in known:
                if (known[address]["size"], known[address]["normalized_sha256"]) != (
                    item["size"],
                    item["normalized_sha256"],
                ):
                    raise AuditError(f"min8 body conflicts with authoritative map at 0x{address:08X}")
                continue
            for name in item["names"]:
                add_function(
                    low_floor,
                    address=address,
                    size=item["size"],
                    normalized_sha256=item["normalized_sha256"],
                    name=name,
                    archive=sorted(item["archives"])[0],
                )
    if (
        len(low_floor) != EXPECTED_LOW_FLOOR_CANDIDATES
        or sum(item["size"] for item in low_floor.values())
        != EXPECTED_LOW_FLOOR_CANDIDATE_BYTES
    ):
        raise AuditError("low-floor candidate census changed")

    application_objdump = application_objdump.resolve()
    if sha256_file(application_objdump) != EXPECTED_APPLICATION_OBJDUMP_SHA256:
        raise AuditError("authenticated whole-application ARC objdump changed")
    targets: set[int] = set()
    instruction = re.compile(
        r"\s*[0-9a-f]+:\s+(?:[0-9a-f]{4}\s+)+\s*[A-Za-z0-9_.]+\s+(.*)"
    )
    for line in application_objdump.read_text().splitlines():
        match = instruction.match(line)
        if match:
            values = re.findall(r"(?:0x)?([0-9a-f]{6,8})", match.group(1))
            if values:
                targets.add(int(values[-1], 16))

    image_bytes = image.resolve().read_bytes()
    known_ends = {item["end"] for item in known.values()}
    confirmed = {
        address
        for address in low_floor
        if address in known_ends
        or image_bytes[address - PACKAGE_MAP_BASE - 2:address - PACKAGE_MAP_BASE].hex()
        == "e078"
        or address in targets
    }
    changed = True
    while changed:
        changed = False
        confirmed_ends = {low_floor[address]["end"] for address in confirmed}
        for address in low_floor:
            if address not in confirmed and address in confirmed_ends:
                confirmed.add(address)
                changed = True

    known_intervals = sorted((item["address"], item["end"]) for item in known.values())

    def overlaps_known(item: dict[str, Any]) -> bool:
        return any(
            start < item["end"] and item["address"] < end
            for start, end in known_intervals
        )

    promoted = {
        address: item
        for address, item in low_floor.items()
        if address in confirmed and not overlaps_known(item)
    }
    rejected = {address: item for address, item in low_floor.items() if address not in promoted}
    if (
        len(promoted) != EXPECTED_LOW_FLOOR_PROMOTED
        or sum(item["size"] for item in promoted.values())
        != EXPECTED_LOW_FLOOR_PROMOTED_BYTES
        or {
            address: sorted(item["names"])[0]
            for address, item in rejected.items()
        }
        != EXPECTED_LOW_FLOOR_REJECTED
    ):
        raise AuditError("low-floor boundary/xref acceptance set changed")
    combined = {**known, **promoted}
    merged = merge_intervals(
        [(item["address"], item["end"]) for item in combined.values()]
    )
    combined_bytes = sum(end - start for start, end in merged)
    if (
        len(combined) != EXPECTED_LOW_FLOOR_ALL_FUNCTIONS
        or combined_bytes != EXPECTED_LOW_FLOOR_ALL_BYTES
        or len(merged) != EXPECTED_LOW_FLOOR_ALL_INTERVALS
    ):
        raise AuditError("low-floor combined map changed or overlaps")

    def public(item: dict[str, Any]) -> dict[str, Any]:
        return {
            **{key: value for key, value in item.items() if key not in {"names", "archives"}},
            "names": sorted(item["names"]),
            "archives": sorted(item["archives"]),
        }

    return {
        **{key: value for key, value in authoritative.items() if key not in {"functions", "new_functions"}},
        "min8_match_record_count": round1_records + round2_records,
        "min8_new_candidate_count": len(low_floor),
        "min8_new_candidate_bytes": sum(item["size"] for item in low_floor.values()),
        "min8_promoted_function_count": len(promoted),
        "min8_promoted_function_bytes": sum(item["size"] for item in promoted.values()),
        "min8_rejected_candidate_count": len(rejected),
        "combined_exact_function_count": len(combined),
        "combined_exact_function_bytes": combined_bytes,
        "combined_application_percent": combined_bytes / APP_SIZE * 100.0,
        "application_bytes_not_exact_function_matched": APP_SIZE - combined_bytes,
        "application_percent_not_exact_function_matched": (APP_SIZE - combined_bytes) / APP_SIZE * 100.0,
        "combined_merged_interval_count": len(merged),
        "functions": [public(item) for _address, item in sorted(combined.items())]
        if include_functions else [],
        "min8_promoted_functions": [public(item) for _address, item in sorted(promoted.items())]
        if include_functions else [],
        "min8_rejected_candidates": [public(item) for _address, item in sorted(rejected.items())],
    }


def analyze(
    output: Path,
    *,
    image: Path = DEFAULT_IMAGE,
    manifest_path: Path = DEFAULT_MANIFEST,
    include_functions: bool = False,
) -> dict[str, Any]:
    output = output.resolve()
    image = image.resolve()
    manifest_path = manifest_path.resolve()
    if sha256_file(image) != IMAGE_SHA256:
        raise AuditError("official EM9305 image identity mismatch")
    if sha256_file(output / "INPUTS.tsv") != EXPECTED_INPUTS_SHA256:
        raise AuditError("expanded SDK batch input ledger changed")
    if sha256_file(output / "CONFIG.json") != EXPECTED_CONFIG_SHA256:
        raise AuditError("expanded SDK batch configuration changed")
    verify_checksum_manifest(output)
    config = json.loads((output / "CONFIG.json").read_text())
    if config["minimum_compared_bytes"] != 16 or config["jobs"] != 16:
        raise AuditError("expanded SDK batch must use 16-byte/16-job configuration")

    manifest = parse_manifest(manifest_path)
    if set(manifest) != set(EXPECTED_REPORT_SHA256):
        raise AuditError("expanded SDK archive manifest membership changed")
    inputs = dict(
        line.split("\t", 1)[::-1]
        for line in (output / "INPUTS.tsv").read_text().splitlines()
    )
    expected_inputs = {
        "runner": sha256_file(DEFAULT_RUNNER),
        "comparator": sha256_file(DEFAULT_COMPARATOR),
        "firmware": IMAGE_SHA256,
        "manifest": sha256_file(manifest_path),
        "configuration": EXPECTED_CONFIG_SHA256,
    }
    expected_inputs.update({f"archive:{label}": item["sha256"] for label, item in manifest.items()})
    if inputs != expected_inputs:
        raise AuditError("expanded SDK batch inputs do not match current authenticated sources")

    application = image.read_bytes()[APP_FILE_OFFSET:APP_FILE_OFFSET + APP_SIZE]
    by_address: dict[int, dict[str, Any]] = {}
    record_count = 0
    archive_counts: dict[str, int] = {}
    for label, expected_report_digest in EXPECTED_REPORT_SHA256.items():
        report_path = output / "reports" / f"{label}.json"
        if sha256_file(report_path) != expected_report_digest:
            raise AuditError(f"expanded SDK deterministic report changed: {label}")
        report = json.loads(report_path.read_text())
        identity = report["identity"]
        if (
            identity["archive_path"] != manifest[label]["path"]
            or identity["archive_git_blob"] != manifest[label]["git_blob"]
            or identity["archive_sha256"] != manifest[label]["sha256"]
        ):
            raise AuditError(f"expanded SDK report identity mismatch: {label}")
        if not identity["compiler_anchors_matched"]:
            raise AuditError(f"expanded SDK compiler identity mismatch: {label}")
        matches = report["unique_discovered_matches"]
        if len(matches) != EXPECTED_RECORD_COUNTS[label]:
            raise AuditError(f"expanded SDK match count changed: {label}")
        archive_counts[label] = len(matches)
        record_count += len(matches)
        for match in matches:
            if len(match["matches"]) != 1 or match["compared_byte_count"] < 16:
                raise AuditError(f"weak or non-unique expanded SDK match: {label}/{match['name']}")
            address = match["matches"][0]
            size = match["size"]
            if address < APP_BASE or address + size > APP_BASE + APP_SIZE:
                raise AuditError(f"expanded SDK match outside application: {label}/{match['name']}")
            body_key = (size, match["normalized_sha256"])
            existing = by_address.get(address)
            if existing is None:
                offset = address - APP_BASE
                by_address[address] = {
                    "address": address,
                    "end": address + size,
                    "size": size,
                    "raw_sha256": hashlib.sha256(application[offset:offset + size]).hexdigest(),
                    "normalized_sha256": match["normalized_sha256"],
                    "names": {match["name"]},
                    "objects": {match["object"]},
                    "archives": {label},
                }
            elif (existing["size"], existing["normalized_sha256"]) != body_key:
                raise AuditError(f"conflicting SDK bodies at 0x{address:08X}")
            else:
                existing["names"].add(match["name"])
                existing["objects"].add(match["object"])
                existing["archives"].add(label)

    if len(by_address) != EXPECTED_DISTINCT_FUNCTIONS:
        raise AuditError("expanded SDK distinct function count changed")
    intervals = [(item["address"], item["end"]) for item in by_address.values()]
    merged = merge_intervals(intervals)
    raw_bytes = sum(end - start for start, end in intervals)
    union_bytes = sum(end - start for start, end in merged)
    if raw_bytes != EXPECTED_FUNCTION_BYTES or union_bytes != EXPECTED_FUNCTION_BYTES:
        raise AuditError("expanded SDK exact function byte coverage changed or overlaps")
    for address, name in EXPECTED_CRITICAL_NAMES.items():
        if name not in by_address.get(address, {}).get("names", set()):
            raise AuditError(f"critical SDK match missing: {name}@0x{address:08X}")

    functions = []
    if include_functions:
        functions = [
            {
                **{key: value for key, value in item.items() if key not in {"names", "objects", "archives"}},
                "names": sorted(item["names"]),
                "objects": sorted(item["objects"]),
                "archives": sorted(item["archives"]),
            }
            for _address, item in sorted(by_address.items())
        ]
    combined_functions = EXPECTED_DISTINCT_FUNCTIONS + KNOWN_ENFORCED_FUNCTIONS
    combined_bytes = EXPECTED_FUNCTION_BYTES + KNOWN_ENFORCED_BYTES
    return {
        "expanded_archive_count": len(manifest),
        "expanded_match_record_count": record_count,
        "expanded_distinct_function_count": EXPECTED_DISTINCT_FUNCTIONS,
        "expanded_exact_function_bytes": EXPECTED_FUNCTION_BYTES,
        "expanded_application_percent": EXPECTED_FUNCTION_BYTES / APP_SIZE * 100.0,
        "expanded_merged_interval_count": len(merged),
        "known_enforced_function_count": KNOWN_ENFORCED_FUNCTIONS,
        "known_enforced_function_bytes": KNOWN_ENFORCED_BYTES,
        "combined_exact_function_count": combined_functions,
        "combined_exact_function_bytes": combined_bytes,
        "combined_application_percent": combined_bytes / APP_SIZE * 100.0,
        "application_bytes_not_exact_function_matched": APP_SIZE - combined_bytes,
        "application_percent_not_exact_function_matched": (APP_SIZE - combined_bytes) / APP_SIZE * 100.0,
        "archive_match_record_counts": archive_counts,
        "functions": functions,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-output", type=Path, required=True)
    parser.add_argument("--enforced-output", type=Path)
    parser.add_argument("--round2-output", type=Path)
    parser.add_argument("--round1-min8-output", type=Path)
    parser.add_argument("--round2-min8-output", type=Path)
    parser.add_argument("--application-objdump", type=Path)
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--round2-manifest", type=Path, default=DEFAULT_ROUND2_MANIFEST)
    parser.add_argument("--include-functions", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if (args.round2_output is None) != (args.enforced_output is None):
        raise AuditError("--round2-output and --enforced-output must be supplied together")
    min8_values = (
        args.round1_min8_output,
        args.round2_min8_output,
        args.application_objdump,
    )
    if any(value is not None for value in min8_values) and not all(
        value is not None for value in min8_values
    ):
        raise AuditError("both min8 outputs and --application-objdump must be supplied together")
    if args.round1_min8_output is not None:
        if args.round2_output is None or args.enforced_output is None:
            raise AuditError("low-floor audit also requires enforced and round-two outputs")
        report = analyze_low_floor(
            args.batch_output,
            args.enforced_output,
            args.round2_output,
            args.round1_min8_output,
            args.round2_min8_output,
            args.application_objdump,
            image=args.image,
            baseline_manifest_path=args.manifest,
            round2_manifest_path=args.round2_manifest,
            include_functions=args.include_functions,
        )
        label = "EM9305 boundary-qualified low-floor SDK discovery audit"
    elif args.round2_output is not None:
        report = analyze_round2(
            args.batch_output,
            args.enforced_output,
            args.round2_output,
            image=args.image,
            baseline_manifest_path=args.manifest,
            round2_manifest_path=args.round2_manifest,
            include_functions=args.include_functions,
        )
        label = "EM9305 combined SDK discovery audit"
    else:
        report = analyze(
            args.batch_output,
            image=args.image,
            manifest_path=args.manifest,
            include_functions=args.include_functions,
        )
        label = "EM9305 expanded SDK discovery audit"
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"{label}: PASS")
        print(json.dumps({
            key: value for key, value in report.items()
            if key not in {
                "archive_match_record_counts", "functions", "new_functions",
                "min8_promoted_functions", "min8_rejected_candidates",
            }
        }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
