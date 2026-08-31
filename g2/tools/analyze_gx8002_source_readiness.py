#!/usr/bin/env python3
"""Exhaustive, fail-closed GX8002 codec/DSP source-readiness accounting."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from analyze_g2_codec_fwpk_segments import analyze as analyze_fwpk
from analyze_g2_codec_stage2_sections import analyze as analyze_stage2

ROOT = Path(__file__).resolve().parents[1]
BLOB = ROOT / "blobs/official/g2-2.2.6.10/firmware_codec.bin"
MANIFEST = ROOT / "tools/manifests/gx8002-source-readiness.tsv"
CANDIDATE = ROOT / "components/shared/gx8002/runtime_gx8002_kws_model_boundary.c"
HEADER = CANDIDATE.with_suffix(".h")
BACKUP_CANDIDATE = ROOT / "components/shared/gx8002/runtime_gx8002_backup_runtime_boundary.c"
BACKUP_HEADER = BACKUP_CANDIDATE.with_suffix(".h")
XIP_CANDIDATE = ROOT / "components/shared/gx8002/runtime_gx8002_image_a_xip_boundary.c"
XIP_HEADER = XIP_CANDIDATE.with_suffix(".h")
BOOT2_CANDIDATE = ROOT / "components/shared/gx8002/runtime_gx8002_uart_boot_stage2_boundary.c"
BOOT2_HEADER = BOOT2_CANDIDATE.with_suffix(".h")
SRAM_A_CANDIDATE = ROOT / "components/shared/gx8002/runtime_gx8002_image_a_sram_text_boundary.c"
SRAM_A_HEADER = SRAM_A_CANDIDATE.with_suffix(".h")
STAGE1_A_CANDIDATE = ROOT / "components/shared/gx8002/runtime_gx8002_image_a_stage1_boundary.c"
STAGE1_A_HEADER = STAGE1_A_CANDIDATE.with_suffix(".h")
STAGE1_B_CANDIDATE = ROOT / "components/shared/gx8002/runtime_gx8002_image_b_stage1_boundary.c"
STAGE1_B_HEADER = STAGE1_B_CANDIDATE.with_suffix(".h")
BOOT1_CANDIDATE = ROOT / "components/shared/gx8002/runtime_gx8002_uart_boot_stage1_boundary.c"
BOOT1_HEADER = BOOT1_CANDIDATE.with_suffix(".h")
COMMAND_CANDIDATE = ROOT / "components/shared/gx8002/runtime_gx8002_kws_command_boundary.c"
COMMAND_HEADER = COMMAND_CANDIDATE.with_suffix(".h")
DATA_A_CANDIDATE = ROOT / "components/shared/gx8002/runtime_gx8002_image_a_sram_data_boundary.c"
DATA_A_HEADER = DATA_A_CANDIDATE.with_suffix(".h")
DATA_B_CANDIDATE = ROOT / "components/shared/gx8002/runtime_gx8002_image_b_sram_data_boundary.c"
DATA_B_HEADER = DATA_B_CANDIDATE.with_suffix(".h")

BLOB_SIZE = 326092
BLOB_SHA256 = "b06dfef7faa2f1e52d2aacd07958d4b96ffc36dca5077ac9149e48f19fc9c4d0"
WEIGHT_START = 0x1B15C
WEIGHT_END = 0x3893C
WEIGHT_SIZE = 120800
WEIGHT_SHA256 = "397971427d7097180d07eb63f9822904a555e51f7643d946ebb38d71a967f8cf"
BACKUP_START = 0x3B940
BACKUP_END = 0x4EE5C
BACKUP_SIZE = 79132
BACKUP_SHA256 = "cd2ccdc2bca9decff0cc514d3cca6317c28ebdbe22891660f5d9ba00276ecdb3"
XIP_START = 0xC590
XIP_END = 0x15414
XIP_SIZE = 36484
XIP_SHA256 = "49c9aed0126493220a3e48827c267d5e94f64d51d9ede0ccc3e84b8946744584"
BOOT2_START = 0x2850
BOOT2_END = 0x958C
BOOT2_SIZE = 27964
BOOT2_SHA256 = "4aacc9e5bf45001bef99785b62302e88bd0b5e6bf4d6186fd7033b1eaeb05b0d"
SRAM_A_START = 0x15414
SRAM_A_END = 0x184F8
SRAM_A_SIZE = 12516
SRAM_A_SHA256 = "3780ea0bd9c11bb94cd72bfc6a1e8924f2f3e72e9a31ec49a185a18799c9a5f8"
STAGE1_A_START = 0x958C
STAGE1_A_END = 0xC58C
STAGE1_A_SIZE = 12288
STAGE1_A_SHA256 = "9546164f32680de47fa99ba85ba08a3c538822260957de6c1baee772638da464"
STAGE1_B_START = 0x3893C
STAGE1_B_END = 0x3B93C
STAGE1_B_SIZE = 12288
STAGE1_B_SHA256 = "a80924ccf78205ef1761c4f568d4ce31f909635bf3ad7eecfaed250ad801626c"
BOOT1_START = 0x50
BOOT1_END = 0x2850
BOOT1_SIZE = 10240
BOOT1_SHA256 = "cbbe85a2d60f5bb805dddb45fa2eac1632bdf0ab80665c040c0892c64074133f"
COMMAND_START = 0x18D90
COMMAND_END = 0x1B15C
COMMAND_SIZE = 9164
COMMAND_SHA256 = "c38ed6d22c7c0b6178288678364acd10bd5730aa382c1e19a32f6cf2bd1430b9"
DATA_A_START = 0x184FC
DATA_A_END = 0x18D90
DATA_A_SIZE = 2196
DATA_A_SHA256 = "e0a88003909bb45ae966bfedcbf6e21a5bc83137d26bd36c7f81114fa0034384"
DATA_B_START = 0x4EE5C
DATA_B_END = 0x4F9CC
DATA_B_SIZE = 2928
DATA_B_SHA256 = "4b694344b50969d1e2114d9324cbd53374af3dd07375614a5257f18f3213f884"

PINS = {
    CANDIDATE: (7811, "42a00acfa7a40e66e1513dfe0d4423858e7127ca51722e81515f681bb124d3ae"),
    HEADER: (1704, "68b74c515663de2f13ac9ed63f5957a919f7a6da03e7e70bb69ed4c039e246e4"),
    BACKUP_CANDIDATE: (842, "600d5614545b9300d0d4380161e3146a046c42c708613f449876ce295d3e6b2a"),
    BACKUP_HEADER: (690, "25e4e402bb6fccd563f4c5d673f61e0478b5fef0d88e965379a426566c702114"),
    XIP_CANDIDATE: (832, "6bba79a358f79bbb1716d3cf2971e9b4312d095a1bf72b7c3a35a30c5e92eae4"),
    XIP_HEADER: (666, "1a0d71ebd6b773496ee9b3a351a1171f65e62477fe0b726dd5c3bbdc18432586"),
    BOOT2_CANDIDATE: (863, "cd1ce61a33b1ddd484026236c5ceaa3910aae35093dbc7b5ef48dafe4444e85d"),
    BOOT2_HEADER: (706, "c8560bbfea45037d09cbc08ffc9ab4bca81e6db472879f7107abd73922e738c3"),
    SRAM_A_CANDIDATE: (778, "3b4537dcec3782a47e3a7f734cb58cff16e32a323d22f61c2789165ca4926fe4"),
    SRAM_A_HEADER: (714, "999cda33501cc0b34089637456f767848cfee78f86e46879e6d66bfa13611d34"),
    STAGE1_A_CANDIDATE: (769, "abf52a68ac2748de56d24ce0a1a2b76360ff7962b11fcf6db40a1553750c9f55"),
    STAGE1_A_HEADER: (690, "b90b8ac0083460155c0d05717ea65efb8c7f493ee93ef76e839bfebf8d4f7be6"),
    STAGE1_B_CANDIDATE: (769, "76c0014d8ed6d986b58864b167595b20a35d47323467c7a00a540b0f75f48c79"),
    STAGE1_B_HEADER: (690, "f59ac23cb25c3bfad55241974715a63251075824f0dfc3c26b3041086baa7bd7"),
    BOOT1_CANDIDATE: (775, "4de180c3e3a4e68f6c1350ec28857219c5f48b89ab7cde0a8d52411ed50a0a87"),
    BOOT1_HEADER: (706, "461b88431ec8bcb73eece105f31e7c52d66b13341f6f66285bc7d581b33faccb"),
    COMMAND_CANDIDATE: (744, "36d97762f223f69e6d97d59e48496c39abefd694323254ea7d9919514b691875"),
    COMMAND_HEADER: (688, "2798717c2f5902f391712460d96d4901041d465699bad802d461823798865142"),
    DATA_A_CANDIDATE: (725, "3929cf7a80cac9c6e8ae0b12dad08857e5a458f4700ed2b3fa1d6e94c33d28ca"),
    DATA_A_HEADER: (698, "e87623b1728b975cbc3ae8507c736183533b2874ce87b84b2efce8d003f71d65"),
    DATA_B_CANDIDATE: (725, "eb26f7f716feabd1b5141d92fd28537ce62550bf1b7c1d1c0e618de99eae562c"),
    DATA_B_HEADER: (698, "99b8e13b8a4de0ce6faf52ebb952990259f63d0cb4cc751a4e8e97f21f5aaf3c"),
    MANIFEST: (6051, "d89d6c7b26d7e4453bc1bab436868d554a9f39ab52308931c0fb5ceea485b32e"),
}

HEADER_FIELDS = [
    "region", "start", "end_exclusive", "size", "sha256", "byte_class",
    "readiness", "source_provider", "source_license", "payload_redistribution",
    "production_route", "evidence",
]

READINESS = {
    "reconstructible_mit_format_metadata",
    "typed_unsupported_external_boundary",
    "unavailable_proprietary_codec_firmware",
}


class ReadinessError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReadinessError(message)


def _read_pinned_files() -> dict[Path, bytes]:
    result: dict[Path, bytes] = {}
    for path, expected in PINS.items():
        data = path.read_bytes()
        require((len(data), sha256(data)) == expected, f"{path}: identity drift")
        result[path] = data
    return result


def _read_rows(data: bytes) -> list[dict[str, str]]:
    text = data.decode("utf-8")
    reader = csv.DictReader(text.splitlines(), delimiter="\t")
    require(reader.fieldnames == HEADER_FIELDS, "readiness manifest header drift")
    rows = list(reader)
    require(len(rows) == 17, "readiness manifest must have exactly 17 spans")
    return rows


def _check_candidate(candidate: bytes, header: bytes, backup_candidate: bytes,
                     backup_header: bytes, xip_candidate: bytes, xip_header: bytes,
                     boot2_candidate: bytes, boot2_header: bytes,
                     sram_a_candidate: bytes, sram_a_header: bytes,
                     stage1_a_candidate: bytes, stage1_a_header: bytes,
                     stage1_b_candidate: bytes, stage1_b_header: bytes,
                     boot1_candidate: bytes, boot1_header: bytes,
                     command_candidate: bytes, command_header: bytes,
                     data_a_candidate: bytes, data_a_header: bytes,
                     data_b_candidate: bytes, data_b_header: bytes,
                     blob: bytes) -> None:
    sources = (candidate, header, backup_candidate, backup_header,
               xip_candidate, xip_header, boot2_candidate, boot2_header,
               sram_a_candidate, sram_a_header, stage1_a_candidate, stage1_a_header,
               stage1_b_candidate, stage1_b_header, boot1_candidate, boot1_header,
               command_candidate, command_header, data_a_candidate, data_a_header,
               data_b_candidate, data_b_header)
    combined = "".join(source.decode("utf-8") for source in sources)
    require(combined.count("SPDX-License-Identifier: MIT") == 22,
            "boundary SPDX identity drift")
    for token in (
        "OPEN_CFW_GX8002_KWS_WEIGHT_SIZE",
        "OPEN_CFW_GX8002_KWS_WEIGHT_SHA256_HEX",
        "open_cfw_gx8002_kws_model_provider_fn",
        "open_cfw_gx8002_kws_model_load",
        "open_cfw_gx8002_authenticated_segment_load",
        "OPEN_CFW_GX8002_BACKUP_RUNTIME_SIZE",
        "OPEN_CFW_GX8002_BACKUP_RUNTIME_SHA256_HEX",
        "open_cfw_gx8002_backup_runtime_load",
        "OPEN_CFW_GX8002_IMAGE_A_XIP_SIZE",
        "OPEN_CFW_GX8002_IMAGE_A_XIP_SHA256_HEX",
        "open_cfw_gx8002_image_a_xip_load",
        "OPEN_CFW_GX8002_UART_BOOT_STAGE2_SIZE",
        "OPEN_CFW_GX8002_UART_BOOT_STAGE2_SHA256_HEX",
        "open_cfw_gx8002_uart_boot_stage2_load",
        "OPEN_CFW_GX8002_IMAGE_A_SRAM_TEXT_SIZE",
        "OPEN_CFW_GX8002_IMAGE_A_SRAM_TEXT_SHA256_HEX",
        "open_cfw_gx8002_image_a_sram_text_load",
        "OPEN_CFW_GX8002_IMAGE_A_STAGE1_SIZE",
        "OPEN_CFW_GX8002_IMAGE_A_STAGE1_SHA256_HEX",
        "open_cfw_gx8002_image_a_stage1_load",
        "OPEN_CFW_GX8002_IMAGE_B_STAGE1_SIZE",
        "OPEN_CFW_GX8002_IMAGE_B_STAGE1_SHA256_HEX",
        "open_cfw_gx8002_image_b_stage1_load",
        "OPEN_CFW_GX8002_UART_BOOT_STAGE1_SIZE",
        "OPEN_CFW_GX8002_UART_BOOT_STAGE1_SHA256_HEX",
        "open_cfw_gx8002_uart_boot_stage1_load",
        "OPEN_CFW_GX8002_KWS_COMMAND_SIZE",
        "OPEN_CFW_GX8002_KWS_COMMAND_SHA256_HEX",
        "open_cfw_gx8002_kws_command_load",
        "OPEN_CFW_GX8002_IMAGE_A_SRAM_DATA_SIZE",
        "open_cfw_gx8002_image_a_sram_data_load",
        "OPEN_CFW_GX8002_IMAGE_B_SRAM_DATA_SIZE",
        "open_cfw_gx8002_image_b_sram_data_load",
        "OPEN_CFW_GX8002_MODEL_UNSUPPORTED",
        "OPEN_CFW_GX8002_MODEL_IDENTITY_MISMATCH",
        "sha256_update(&hash, destination, bytes_written)",
        "clear_segment(destination, expected_size)",
    ):
        require(token in combined, f"boundary contract drift: {token}")
    require(WEIGHT_SHA256 in combined, "expected model digest missing from boundary")
    require(BACKUP_SHA256 in combined, "expected backup-runtime digest missing")
    require(XIP_SHA256 in combined, "expected XIP digest missing")
    require(BOOT2_SHA256 in combined, "expected UART boot-stage2 digest missing")
    require(SRAM_A_SHA256 in combined, "expected image-A SRAM-text digest missing")
    require(STAGE1_A_SHA256 in combined, "expected image-A stage1 digest missing")
    require(STAGE1_B_SHA256 in combined, "expected image-B stage1 digest missing")
    require(BOOT1_SHA256 in combined, "expected UART boot-stage1 digest missing")
    require(COMMAND_SHA256 in combined, "expected gxNPU command digest missing")
    require(DATA_A_SHA256 in combined, "expected image-A SRAM-data digest missing")
    require(DATA_B_SHA256 in combined, "expected image-B SRAM-data digest missing")
    # No source file may contain a literal 16-byte run from any proprietary span.
    for name, segment in (
        ("model", blob[WEIGHT_START:WEIGHT_END]),
        ("backup runtime", blob[BACKUP_START:BACKUP_END]),
        ("image-A XIP", blob[XIP_START:XIP_END]),
        ("UART boot stage two", blob[BOOT2_START:BOOT2_END]),
        ("image-A SRAM text", blob[SRAM_A_START:SRAM_A_END]),
        ("image-A stage one", blob[STAGE1_A_START:STAGE1_A_END]),
        ("image-B stage one", blob[STAGE1_B_START:STAGE1_B_END]),
        ("UART boot stage one", blob[BOOT1_START:BOOT1_END]),
        ("gxNPU command stream", blob[COMMAND_START:COMMAND_END]),
        ("image-A SRAM data", blob[DATA_A_START:DATA_A_END]),
        ("image-B SRAM data", blob[DATA_B_START:DATA_B_END]),
    ):
        for offset in range(0, len(segment) - 15, 16):
            require(all(segment[offset:offset + 16] not in source for source in sources),
                    f"candidate embeds proprietary {name} bytes")


def run_audit() -> dict[str, Any]:
    pinned = _read_pinned_files()
    blob = BLOB.read_bytes()
    require((len(blob), sha256(blob)) == (BLOB_SIZE, BLOB_SHA256),
            "official GX8002 codec blob changed")
    rows = _read_rows(pinned[MANIFEST])

    cursor = 0
    totals: dict[str, dict[str, int]] = {
        state: {"spans": 0, "bytes": 0} for state in sorted(READINESS)
    }
    normalized = []
    for row in rows:
        start = int(row["start"], 16)
        end = int(row["end_exclusive"], 16)
        size = int(row["size"])
        require(start == cursor, f"gap or overlap before {row['region']}")
        require(end > start and end - start == size, f"bad extent: {row['region']}")
        require(end <= len(blob), f"extent escapes blob: {row['region']}")
        require(sha256(blob[start:end]) == row["sha256"],
                f"body identity drift: {row['region']}")
        readiness = row["readiness"]
        require(readiness in READINESS, f"unknown readiness: {readiness}")
        require(row["production_route"] == "none", "production route must remain absent")
        totals[readiness]["spans"] += 1
        totals[readiness]["bytes"] += size
        normalized.append({**row, "start": start, "end_exclusive": end, "size": size})
        cursor = end
    require(cursor == len(blob), "readiness partition does not end at EOF")
    require(sum(item["bytes"] for item in totals.values()) == BLOB_SIZE,
            "readiness byte accounting does not close")
    require(totals == {
        "reconstructible_mit_format_metadata": {"spans": 6, "bytes": 92},
        "typed_unsupported_external_boundary": {"spans": 11, "bytes": 326000},
        "unavailable_proprietary_codec_firmware": {"spans": 0, "bytes": 0},
    }, "readiness totals drift")

    weight = next(row for row in normalized if row["region"] == "image_a_kws_weights")
    require((weight["start"], weight["end_exclusive"], weight["size"], weight["sha256"]) ==
            (WEIGHT_START, WEIGHT_END, WEIGHT_SIZE, WEIGHT_SHA256),
            "typed model boundary extent drift")
    require(weight["source_license"] == "MIT boundary; payload NOASSERTION" and
            weight["payload_redistribution"] == "unresolved",
            "model source/redistribution distinction drift")
    backup = next(row for row in normalized if row["region"] == "image_b_sram_text")
    require((backup["start"], backup["end_exclusive"], backup["size"], backup["sha256"]) ==
            (BACKUP_START, BACKUP_END, BACKUP_SIZE, BACKUP_SHA256),
            "typed backup-runtime boundary extent drift")
    require(backup["source_license"] == "MIT boundary; payload NOASSERTION" and
            backup["payload_redistribution"] == "unresolved",
            "backup-runtime source/redistribution distinction drift")
    xip = next(row for row in normalized if row["region"] == "image_a_xip_text")
    require((xip["start"], xip["end_exclusive"], xip["size"], xip["sha256"]) ==
            (XIP_START, XIP_END, XIP_SIZE, XIP_SHA256),
            "typed image-A XIP boundary extent drift")
    require(xip["source_license"] == "MIT boundary; payload NOASSERTION" and
            xip["payload_redistribution"] == "unresolved",
            "XIP source/redistribution distinction drift")
    boot2 = next(row for row in normalized if row["region"] == "boot_stage2")
    require((boot2["start"], boot2["end_exclusive"], boot2["size"], boot2["sha256"]) ==
            (BOOT2_START, BOOT2_END, BOOT2_SIZE, BOOT2_SHA256),
            "typed UART boot-stage2 boundary extent drift")
    require(boot2["source_license"] == "MIT boundary; payload NOASSERTION" and
            boot2["payload_redistribution"] == "unresolved",
            "UART boot-stage2 source/redistribution distinction drift")
    sram_a = next(row for row in normalized if row["region"] == "image_a_sram_text")
    require((sram_a["start"], sram_a["end_exclusive"], sram_a["size"],
             sram_a["sha256"]) == (SRAM_A_START, SRAM_A_END, SRAM_A_SIZE, SRAM_A_SHA256),
            "typed image-A SRAM-text boundary extent drift")
    require(sram_a["source_license"] == "MIT boundary; payload NOASSERTION" and
            sram_a["payload_redistribution"] == "unresolved",
            "image-A SRAM-text source/redistribution distinction drift")
    stage1_a = next(row for row in normalized if row["region"] == "image_a_stage1")
    require((stage1_a["start"], stage1_a["end_exclusive"], stage1_a["size"],
             stage1_a["sha256"]) ==
            (STAGE1_A_START, STAGE1_A_END, STAGE1_A_SIZE, STAGE1_A_SHA256),
            "typed image-A stage1 boundary extent drift")
    require(stage1_a["source_license"] == "MIT boundary; payload NOASSERTION" and
            stage1_a["payload_redistribution"] == "unresolved",
            "image-A stage1 source/redistribution distinction drift")
    stage1_b = next(row for row in normalized if row["region"] == "image_b_stage1")
    require((stage1_b["start"], stage1_b["end_exclusive"], stage1_b["size"],
             stage1_b["sha256"]) ==
            (STAGE1_B_START, STAGE1_B_END, STAGE1_B_SIZE, STAGE1_B_SHA256),
            "typed image-B stage1 boundary extent drift")
    require(stage1_b["source_license"] == "MIT boundary; payload NOASSERTION" and
            stage1_b["payload_redistribution"] == "unresolved",
            "image-B stage1 source/redistribution distinction drift")
    boot1 = next(row for row in normalized if row["region"] == "boot_stage1")
    require((boot1["start"], boot1["end_exclusive"], boot1["size"], boot1["sha256"]) ==
            (BOOT1_START, BOOT1_END, BOOT1_SIZE, BOOT1_SHA256),
            "typed UART boot-stage1 boundary extent drift")
    require(boot1["source_license"] == "MIT boundary; payload NOASSERTION" and
            boot1["payload_redistribution"] == "unresolved",
            "UART boot-stage1 source/redistribution distinction drift")
    for region, expected in (
        ("image_a_kws_command", (COMMAND_START, COMMAND_END, COMMAND_SIZE, COMMAND_SHA256)),
        ("image_a_sram_data", (DATA_A_START, DATA_A_END, DATA_A_SIZE, DATA_A_SHA256)),
        ("image_b_sram_data", (DATA_B_START, DATA_B_END, DATA_B_SIZE, DATA_B_SHA256)),
    ):
        item = next(row for row in normalized if row["region"] == region)
        require((item["start"], item["end_exclusive"], item["size"], item["sha256"]) == expected,
                f"typed {region} boundary extent drift")
        require(item["source_license"] == "MIT boundary; payload NOASSERTION" and
                item["payload_redistribution"] == "unresolved",
                f"{region} source/redistribution distinction drift")

    fwpk = analyze_fwpk()
    stage2 = analyze_stage2()
    kws = stage2["kws_model_payload"]["weight"]
    require((fwpk["blob"]["size"], fwpk["blob"]["sha256"]) ==
            (BLOB_SIZE, BLOB_SHA256), "FWPK analyzer identity disagreement")
    require((kws["flash"], kws["size"], kws["sha256"], kws["dram_staging"]) ==
            ("[0x11BD0, 0x2F3B0)", WEIGHT_SIZE, WEIGHT_SHA256,
             "0x200056D0 (decoded)"), "stage2 analyzer model evidence disagreement")
    backup_stage = stage2["image_b"]["stage2"]["sram_text"]
    require((backup_stage["flash"], backup_stage["size"], backup_stage["iram"],
             backup_stage["sha256"]) ==
            ("[0x323B4, 0x458D0)", BACKUP_SIZE, "[0x10003000, 0x1001651C)",
             BACKUP_SHA256), "stage2 analyzer backup-runtime evidence disagreement")
    xip_stage = stage2["image_a"]["stage2"]["xip_text"]
    require((xip_stage["flash"], xip_stage["size"], xip_stage["sha256"]) ==
            ("[0x3004, 0xBE88)", XIP_SIZE, XIP_SHA256),
            "stage2 analyzer image-A XIP evidence disagreement")
    boot2_stage = fwpk["boot_image"]["stage2"]
    require((boot2_stage["size"], boot2_stage["sha256"],
             boot2_stage["load_address"], boot2_stage["reset_vector"],
             boot2_stage["distinct_handlers"]) ==
            (BOOT2_SIZE, BOOT2_SHA256, "0x10002800", "0x10002900",
             ["0x10002994", "0x10003124"]),
            "FWPK analyzer UART boot-stage2 evidence disagreement")
    sram_a_stage = stage2["image_a"]["stage2"]["sram_text"]
    require((sram_a_stage["flash"], sram_a_stage["size"], sram_a_stage["iram"],
             sram_a_stage["sha256"]) ==
            ("[0xBE88, 0xEF6C)", SRAM_A_SIZE, "[0x10023400, 0x100264E4)",
             SRAM_A_SHA256), "stage2 analyzer image-A SRAM-text evidence disagreement")
    stage1_a_image = fwpk["main_image"]["image_a"]
    require((stage1_a_image["stage1_block_size"], stage1_a_image["stage1_block_sha256"],
             stage1_a_image["stage1_block_crc32_mpeg2"]) ==
            (STAGE1_A_SIZE, STAGE1_A_SHA256, "0x21c58edb"),
            "FWPK analyzer image-A stage1 evidence disagreement")
    stage1_b_image = fwpk["main_image"]["image_b"]
    require((stage1_b_image["stage1_block_size"], stage1_b_image["stage1_block_sha256"],
             stage1_b_image["stage1_block_crc32_mpeg2"]) ==
            (STAGE1_B_SIZE, STAGE1_B_SHA256, "0xa582510c"),
            "FWPK analyzer image-B stage1 evidence disagreement")
    boot1_stage = fwpk["boot_image"]["stage1"]
    require((boot1_stage["size"], boot1_stage["sha256"], boot1_stage["load_address"],
             boot1_stage["reset_vector"], boot1_stage["trap_vectors"]) ==
            (BOOT1_SIZE, BOOT1_SHA256, "0x10000000", "0x10000100",
             ["0x10000130", "0x10000134"]),
            "FWPK analyzer UART boot-stage1 evidence disagreement")
    command_stage = stage2["kws_model_payload"]["cmd"]
    require((command_stage["flash"], command_stage["size"], command_stage["dram_staging"],
             command_stage["sha256"]) ==
            ("[0xF804, 0x11BD0)", COMMAND_SIZE, "0x20003304 (decoded)", COMMAND_SHA256),
            "stage2 analyzer gxNPU-command evidence disagreement")
    data_a_stage = stage2["image_a"]["stage2"]["sram_data"]
    require((data_a_stage["flash"], data_a_stage["size"], data_a_stage["iram"],
             data_a_stage["sha256"]) ==
            ("[0xEF70, 0xF804)", DATA_A_SIZE, "[0x100264E8, 0x10026D7C)", DATA_A_SHA256),
            "stage2 analyzer image-A SRAM-data evidence disagreement")
    data_b_stage = stage2["image_b"]["stage2"]["sram_data"]
    require((data_b_stage["flash"], data_b_stage["size"], data_b_stage["iram"],
             data_b_stage["sha256"]) ==
            ("[0x458D0, 0x46440)", DATA_B_SIZE, "[0x1001651C, 0x1001708C)", DATA_B_SHA256),
            "stage2 analyzer image-B SRAM-data evidence disagreement")
    require(not fwpk["production"]["production_routed"] and
            not stage2["production"]["production_routed"],
            "existing codec analysis unexpectedly production-routed")

    _check_candidate(pinned[CANDIDATE], pinned[HEADER], pinned[BACKUP_CANDIDATE],
                     pinned[BACKUP_HEADER], pinned[XIP_CANDIDATE], pinned[XIP_HEADER],
                     pinned[BOOT2_CANDIDATE], pinned[BOOT2_HEADER],
                     pinned[SRAM_A_CANDIDATE], pinned[SRAM_A_HEADER],
                     pinned[STAGE1_A_CANDIDATE], pinned[STAGE1_A_HEADER],
                     pinned[STAGE1_B_CANDIDATE], pinned[STAGE1_B_HEADER],
                     pinned[BOOT1_CANDIDATE], pinned[BOOT1_HEADER],
                     pinned[COMMAND_CANDIDATE], pinned[COMMAND_HEADER],
                     pinned[DATA_A_CANDIDATE], pinned[DATA_A_HEADER],
                     pinned[DATA_B_CANDIDATE], pinned[DATA_B_HEADER], blob)
    blocking = {
        "spans": totals["typed_unsupported_external_boundary"]["spans"] +
                 totals["unavailable_proprietary_codec_firmware"]["spans"],
        "bytes": totals["typed_unsupported_external_boundary"]["bytes"] +
                 totals["unavailable_proprietary_codec_firmware"]["bytes"],
    }
    external_detail = {
        "opaque_executable": sum(
            row["size"] for row in normalized
            if row["readiness"] == "typed_unsupported_external_boundary"
            and row["byte_class"] == "opaque_executable"
        ),
        "opaque_runtime_data": sum(
            row["size"] for row in normalized
            if row["readiness"] == "typed_unsupported_external_boundary"
            and row["byte_class"] == "opaque_runtime_data"
        ),
        "opaque_npu_commands": sum(
            row["size"] for row in normalized
            if row["readiness"] == "typed_unsupported_external_boundary"
            and row["byte_class"] == "opaque_npu_commands"
        ),
        "proprietary_model_data": sum(
            row["size"] for row in normalized
            if row["readiness"] == "typed_unsupported_external_boundary"
            and row["byte_class"] == "proprietary_model_data"
        ),
    }
    require(external_detail == {
        "opaque_executable": 190_912,
        "opaque_runtime_data": 5_124,
        "opaque_npu_commands": 9_164,
        "proprietary_model_data": 120_800,
    }, "typed external-provider detail changed")
    require(sum(external_detail.values()) == blocking["bytes"],
            "typed external-provider detail does not conserve")
    return {
        "schema_version": 1,
        "status": "candidate-qualified-fail-closed",
        "component": "GX8002 codec/DSP firmware",
        "read_only": True,
        "hardware_operations": False,
        "hardware_validation": "blocked by unavailable physical evidence",
        "blob": {"path": "blobs/official/g2-2.2.6.10/firmware_codec.bin",
                 "size": BLOB_SIZE, "sha256": BLOB_SHA256},
        "partition": {"spans": len(rows), "bytes": cursor, "contiguous": True,
                      "overlaps": 0, "gaps": 0},
        "readiness": totals,
        "source_owned_bytes": 0,
        "format_reconstructible": totals["reconstructible_mit_format_metadata"],
        "blocking_residual": blocking,
        "external_provider_detail": {
            "bytes_by_class": external_detail,
            "bytes": sum(external_detail.values()),
            "open_source_available": False,
            "payload_redistribution_authority": "unresolved",
            "provider_contract": (
                "an external user-supplied provider must authenticate exact "
                "payload identity; the boundary does not claim open availability"
            ),
        },
        "selected_cluster": {
            "name": "image_a_kws_weights",
            "start": WEIGHT_START,
            "end_exclusive": WEIGHT_END,
            "size": WEIGHT_SIZE,
            "sha256": WEIGHT_SHA256,
            "stage2_segment_relative": "[0x11BD0, 0x2F3B0)",
            "dram_staging": "0x200056D0 (decoded)",
            "readiness": "typed_unsupported_external_boundary",
            "boundary_license": "MIT",
            "payload_source_license": "NOASSERTION",
            "payload_redistribution_authority": "unresolved",
            "production_routed": False,
        },
        "prior_cluster": {
            "name": "image_b_sram_text",
            "start": BACKUP_START,
            "end_exclusive": BACKUP_END,
            "size": BACKUP_SIZE,
            "sha256": BACKUP_SHA256,
            "stage2_segment_relative": "[0x323B4, 0x458D0)",
            "iram": "[0x10003000, 0x1001651C)",
            "entry": "0x10003100",
            "readiness": "typed_unsupported_external_boundary",
            "boundary_license": "MIT",
            "payload_source_license": "NOASSERTION",
            "payload_redistribution_authority": "unresolved",
            "production_routed": False,
        },
        "prior_cluster_wave3": {
            "name": "image_a_xip_text",
            "start": XIP_START,
            "end_exclusive": XIP_END,
            "size": XIP_SIZE,
            "sha256": XIP_SHA256,
            "stage2_segment_relative": "[0x3004, 0xBE88)",
            "runtime_mapping": "public default XIP base only; build-specific mapping deferred",
            "internal_abi": "unresolved; no signature invented",
            "readiness": "typed_unsupported_external_boundary",
            "boundary_license": "MIT",
            "payload_source_license": "NOASSERTION",
            "payload_redistribution_authority": "unresolved",
            "production_routed": False,
        },
        "prior_cluster_wave4": {
            "name": "boot_stage2",
            "start": BOOT2_START,
            "end_exclusive": BOOT2_END,
            "size": BOOT2_SIZE,
            "sha256": BOOT2_SHA256,
            "boot_image_relative": "[0x2820, 0x955C)",
            "load_address": "0x10002800",
            "reset_vector": "0x10002900",
            "handler_set": ["0x10002994", "0x10003124"],
            "internal_abi": "unresolved; no signature invented",
            "readiness": "typed_unsupported_external_boundary",
            "boundary_license": "MIT",
            "payload_source_license": "NOASSERTION",
            "payload_redistribution_authority": "unresolved",
            "production_routed": False,
        },
        "prior_cluster_wave5_primary": {
            "name": "image_a_sram_text",
            "start": SRAM_A_START,
            "end_exclusive": SRAM_A_END,
            "size": SRAM_A_SIZE,
            "sha256": SRAM_A_SHA256,
            "stage2_segment_relative": "[0xBE88, 0xEF6C)",
            "iram": "[0x10023400, 0x100264E4)",
            "entry": "0x10023500",
            "handler_set": ["0x10023640", "0x10025574"],
            "internal_abi": "unresolved; no signature invented",
            "readiness": "typed_unsupported_external_boundary",
            "boundary_license": "MIT",
            "payload_source_license": "NOASSERTION",
            "payload_redistribution_authority": "unresolved",
            "production_routed": False,
        },
        "prior_cluster_wave5_additional": {
            "name": "image_a_stage1",
            "start": STAGE1_A_START,
            "end_exclusive": STAGE1_A_END,
            "size": STAGE1_A_SIZE,
            "sha256": STAGE1_A_SHA256,
            "main_image_relative": "[0x0000, 0x3000)",
            "stage1_block_crc32_mpeg2": "0x21C58EDB",
            "runtime_mapping": "unresolved; no mapping invented",
            "internal_abi": "unresolved; no signature invented",
            "readiness": "typed_unsupported_external_boundary",
            "boundary_license": "MIT",
            "payload_source_license": "NOASSERTION",
            "payload_redistribution_authority": "unresolved",
            "production_routed": False,
        },
        "prior_cluster_wave6_primary": {
            "name": "image_b_stage1",
            "start": STAGE1_B_START,
            "end_exclusive": STAGE1_B_END,
            "size": STAGE1_B_SIZE,
            "sha256": STAGE1_B_SHA256,
            "main_image_relative": "[0x2F3B0, 0x323B0)",
            "stage1_block_crc32_mpeg2": "0xA582510C",
            "runtime_mapping": "unresolved; no mapping invented",
            "internal_abi": "unresolved; no signature invented",
            "readiness": "typed_unsupported_external_boundary",
            "boundary_license": "MIT",
            "payload_source_license": "NOASSERTION",
            "payload_redistribution_authority": "unresolved",
            "production_routed": False,
        },
        "prior_cluster_wave6_additional": {
            "name": "boot_stage1",
            "start": BOOT1_START,
            "end_exclusive": BOOT1_END,
            "size": BOOT1_SIZE,
            "sha256": BOOT1_SHA256,
            "boot_image_relative": "[0x0020, 0x2820)",
            "load_address": "0x10000000",
            "reset_vector": "0x10000100",
            "trap_vector_set": ["0x10000130", "0x10000134"],
            "internal_abi": "unresolved; no signature invented",
            "readiness": "typed_unsupported_external_boundary",
            "boundary_license": "MIT",
            "payload_source_license": "NOASSERTION",
            "payload_redistribution_authority": "unresolved",
            "production_routed": False,
        },
        "latest_cluster": {
            "name": "image_a_kws_command",
            "start": COMMAND_START,
            "end_exclusive": COMMAND_END,
            "size": COMMAND_SIZE,
            "sha256": COMMAND_SHA256,
            "stage2_segment_relative": "[0xF804, 0x11BD0)",
            "dram_staging": "0x20003304 (decoded)",
            "semantics": "unresolved gxNPU command format; no reconstruction claimed",
            "readiness": "typed_unsupported_external_boundary",
            "boundary_license": "MIT",
            "payload_source_license": "NOASSERTION",
            "payload_redistribution_authority": "unresolved",
            "production_routed": False,
        },
        "additional_clusters": [
            {"name": "image_b_sram_data", "start": DATA_B_START,
             "end_exclusive": DATA_B_END, "size": DATA_B_SIZE, "sha256": DATA_B_SHA256,
             "stage2_segment_relative": "[0x458D0, 0x46440)",
             "boundary_confidence": "derived text/data split; exact authenticated bytes",
             "boundary_license": "MIT", "payload_source_license": "NOASSERTION",
             "payload_redistribution_authority": "unresolved", "production_routed": False},
            {"name": "image_a_sram_data", "start": DATA_A_START,
             "end_exclusive": DATA_A_END, "size": DATA_A_SIZE, "sha256": DATA_A_SHA256,
             "stage2_segment_relative": "[0xEF70, 0xF804)",
             "boundary_confidence": "authenticated text tail/fill/data head and exact fit",
             "boundary_license": "MIT", "payload_source_license": "NOASSERTION",
             "payload_redistribution_authority": "unresolved", "production_routed": False},
        ],
        "classification_delta": {
            "baseline": {
                "reconstructible_mit_format_metadata": {"spans": 6, "bytes": 92},
                "typed_unsupported_external_boundary": {"spans": 0, "bytes": 0},
                "unavailable_proprietary_codec_firmware": {"spans": 11, "bytes": 326000},
            },
            "typed_external": {"spans": 11, "bytes": 326000},
            "proprietary_unavailable": {"spans": -11, "bytes": -326000},
            "source_owned_bytes": 0,
            "blocking_bytes": 0,
        },
        "latest_wave_delta": {
            "typed_external": {"spans": 3, "bytes": COMMAND_SIZE + DATA_A_SIZE + DATA_B_SIZE},
            "proprietary_unavailable": {"spans": -3, "bytes": -(COMMAND_SIZE + DATA_A_SIZE + DATA_B_SIZE)},
            "source_owned_bytes": 0,
            "blocking_bytes": 0,
        },
        "production": {
            "production_routed": False,
            "official_binary_redistribution_authority": "unresolved",
            "model_provider_required": True,
            "model_provider_must_authenticate_exact_identity": True,
            "backup_runtime_provider_required": True,
            "backup_runtime_provider_must_authenticate_exact_identity": True,
            "image_a_xip_provider_required": True,
            "image_a_xip_provider_must_authenticate_exact_identity": True,
            "uart_boot_stage2_provider_required": True,
            "uart_boot_stage2_provider_must_authenticate_exact_identity": True,
            "image_a_sram_text_provider_required": True,
            "image_a_sram_text_provider_must_authenticate_exact_identity": True,
            "image_a_stage1_provider_required": True,
            "image_a_stage1_provider_must_authenticate_exact_identity": True,
            "image_b_stage1_provider_required": True,
            "image_b_stage1_provider_must_authenticate_exact_identity": True,
            "uart_boot_stage1_provider_required": True,
            "uart_boot_stage1_provider_must_authenticate_exact_identity": True,
            "kws_command_provider_required": True,
            "image_a_sram_data_provider_required": True,
            "image_b_sram_data_provider_required": True,
        },
        "future_hardware_acceptance": [
            "GX8002 model staging and inference behavior",
            "XIP and SRAM runtime mappings",
            "dual-firmware selection policy",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = run_audit()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("GX8002 readiness: candidate-qualified-fail-closed; "
              "17 spans / 326092 bytes; zero unclassified proprietary spans")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
