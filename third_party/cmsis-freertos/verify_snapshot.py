#!/usr/bin/env python3
"""Verify the pinned CMSIS-FreeRTOS constructor compile-input closure."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
PROVENANCE = HERE / "PROVENANCE.json"

EXPECTED_PROVENANCE_SHA256 = (
    "a134880fab25682fbfe463cf8d34c0454990a3f189e2720bc690212403bee1b8"
)
EXPECTED_LOCAL_FILES = {
    ".gitattributes",
    "PROVENANCE.json",
    "README.openCFW.md",
    "verify_snapshot.py",
}
EXPECTED_UPSTREAMS = {
    "cmsis_freertos": {
        "repository": "https://github.com/ARM-software/CMSIS-FreeRTOS.git",
        "tag": "v10.5.1",
        "tag_object": "34e6e4c403c17de35ec0acf29610e374dc938604",
        "commit": "d213f261b5be6bb29a7cce8b84071706b72f4d53",
        "tree": "d3689a816acc77a3f0b7d35439d666ad8434b6ba",
    },
    "cmsis_5": {
        "repository": "https://github.com/ARM-software/CMSIS_5.git",
        "tag": "5.9.0",
        "tag_object": "61e36449f53c25ef7825c40f7dd93685736f457f",
        "commit": "2b7495b8535bdcb306dac29b9ded4cfb679d7e5c",
        "tree": "b88e747b2a2309b81ea77831481a58393465cd7b",
    },
}
EXPECTED_CMSIS_OS2_SHA256 = (
    "8a0d60b56ad30c4f7957f64fa581158017b6812ec94b832d974c773ae4f2bc36"
)
EXPECTED_DIRECT_INCLUDES = {
    "string.h",
    "cmsis_os2.h",
    "cmsis_compiler.h",
    "os_tick.h",
    "FreeRTOS.h",
    "task.h",
    "event_groups.h",
    "semphr.h",
    "timers.h",
    "freertos_mpool.h",
    "freertos_os2.h",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            f"CMSIS-FreeRTOS snapshot verification failed: {message}"
        )


def load_provenance() -> dict[str, Any]:
    data = PROVENANCE.read_bytes()
    require(digest(data) == EXPECTED_PROVENANCE_SHA256, "provenance changed")
    value = json.loads(data)
    require(value["schema_version"] == 1, "unknown provenance schema")
    require(
        value["component"]
        == "CMSIS-FreeRTOS-v10.5.1-constructor-compile-closure",
        "component name changed",
    )
    require(value["license"] == "Apache-2.0", "source license changed")

    for key, expected in EXPECTED_UPSTREAMS.items():
        actual = value["upstreams"][key]
        require(actual["repository"] == expected["repository"], f"{key}: repository changed")
        require(actual["selected_tag"] == expected["tag"], f"{key}: tag changed")
        require(
            actual["annotated_tag_object"] == expected["tag_object"],
            f"{key}: tag object changed",
        )
        require(
            actual["tag_peeled_commit"] == expected["commit"],
            f"{key}: peeled commit changed",
        )
        require(
            actual["selected_commit"] == expected["commit"],
            f"{key}: commit changed",
        )
        require(actual["selected_tree"] == expected["tree"], f"{key}: tree changed")
        require(
            actual["tag_cryptographically_signed"] is False,
            f"{key}: unsigned-tag qualification changed",
        )

    selection = value["selection"]
    require(
        selection["reviewed_constructor_roots"]
        == ["osMessageQueueNew", "osMutexNew", "osSemaphoreNew"],
        "constructor root set changed",
    )
    require(
        selection["cmsis_pack_dependency"]
        == {
            "vendor": "ARM",
            "name": "CMSIS",
            "version": "5.9.0",
            "evidence": "CMSIS-FreeRTOS/ARM.CMSIS-FreeRTOS.pdsc",
        },
        "CMSIS pack dependency changed",
    )
    safety = value["safety"]
    require(safety["compile_inputs_only"] is True, "not compile-input-only")
    require(safety["production_ready"] is False, "production status changed")
    require(
        safety["integrated_into_firmware_build"] is False,
        "firmware integration status changed",
    )
    require(
        safety["hardware_operations"] == [],
        "snapshot unexpectedly declares hardware operations",
    )
    return value


def verify_files(provenance: dict[str, Any]) -> None:
    records = provenance["files"]
    require(len(records) == 10, "dependency file count changed")
    actual_paths = {
        path.relative_to(HERE).as_posix()
        for path in HERE.rglob("*")
        if path.is_file()
    }
    require(
        actual_paths == set(records) | EXPECTED_LOCAL_FILES,
        "snapshot subtree inventory changed",
    )
    for relative_path, record in records.items():
        data = (HERE / relative_path).read_bytes()
        require(len(data) == record["size"], f"{relative_path}: size changed")
        require(
            digest(data) == record["sha256"],
            f"{relative_path}: SHA-256 changed",
        )
        require(
            git_blob(data) == record["git_blob_sha1"],
            f"{relative_path}: Git blob identity changed",
        )
        require(b"\r" not in data, f"{relative_path}: line endings changed")
        require(data.endswith(b"\n"), f"{relative_path}: terminal LF missing")
        require(
            record["upstream"] in EXPECTED_UPSTREAMS,
            f"{relative_path}: unknown upstream",
        )
        require(record["source_path"], f"{relative_path}: source path missing")


def quoted_includes(text: str) -> set[str]:
    return set(
        re.findall(r'^\s*#\s*include\s*[<"]([^">]+)[">]', text, re.MULTILINE)
    )


def verify_compile_closure_markers() -> None:
    source = (
        HERE
        / "CMSIS-FreeRTOS/CMSIS/RTOS2/FreeRTOS/Source/cmsis_os2.c"
    )
    source_data = source.read_bytes()
    require(
        digest(source_data) == EXPECTED_CMSIS_OS2_SHA256,
        "cmsis_os2.c root changed",
    )
    source_text = source_data.decode("utf-8")
    require(
        quoted_includes(source_text) == EXPECTED_DIRECT_INCLUDES,
        "cmsis_os2.c direct include set changed",
    )
    for return_type, constructor in (
        ("osMessageQueueId_t", "osMessageQueueNew"),
        ("osMutexId_t", "osMutexNew"),
        ("osSemaphoreId_t", "osSemaphoreNew"),
    ):
        require(
            re.search(
                rf"^\s*{return_type}\s+{constructor}\s*\(",
                source_text,
                re.MULTILINE,
            )
            is not None,
            f"{constructor} definition missing",
        )

    pdsc = (
        HERE / "CMSIS-FreeRTOS/ARM.CMSIS-FreeRTOS.pdsc"
    ).read_text(encoding="utf-8")
    require(
        '<package vendor="ARM" name="CMSIS" version="5.9.0"/>' in pdsc,
        "exact CMSIS 5.9.0 dependency missing",
    )

    private_config = (
        HERE
        / "CMSIS-FreeRTOS/CMSIS/RTOS2/FreeRTOS/Include/freertos_os2.h"
    ).read_text(encoding="utf-8")
    require("#if defined(_RTE_)" in private_config, "_RTE_ guard missing")
    require(
        '#include "RTE_Components.h"' in private_config,
        "RTE conditional include marker missing",
    )
    require(
        "#include CMSIS_device_header" in private_config,
        "device-header conditional include marker missing",
    )

    compiler = (
        HERE / "CMSIS_5/CMSIS/Core/Include/cmsis_compiler.h"
    ).read_text(encoding="utf-8")
    require(
        re.search(
            r"#elif\s+defined\s*\(\s*__GNUC__\s*\)\s*"
            r'#include\s+"cmsis_gcc\.h"',
            compiler,
            re.DOTALL,
        )
        is not None,
        "GNU-compatible compiler branch changed",
    )


def verify_licenses() -> None:
    apache = (HERE / "CMSIS_5/LICENSE.txt").read_text(encoding="utf-8")
    require("Apache License" in apache, "Apache license heading missing")
    require("Version 2.0, January 2004" in apache, "Apache version changed")

    kernel_notice = (
        HERE / "CMSIS-FreeRTOS/License/license.txt"
    ).read_text(encoding="utf-8")
    require(
        "The FreeRTOS kernel is released under the MIT open source license"
        in kernel_notice,
        "FreeRTOS kernel license qualification missing",
    )
    require(
        "Permission is hereby granted, free of charge" in kernel_notice,
        "MIT grant marker missing",
    )


def main() -> int:
    provenance = load_provenance()
    verify_files(provenance)
    verify_compile_closure_markers()
    verify_licenses()
    print(
        "CMSIS-FreeRTOS v10.5.1 constructor compile-input closure, "
        "CMSIS 5.9.0 dependency, licenses, Git blobs, and SHA-256 pins: OK"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
