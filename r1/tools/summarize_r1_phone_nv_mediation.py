#!/usr/bin/env python3
"""Pin the first-party Android AOT evidence for R1 NV phone mediation.

This is a read-only source audit. It does not contact Even's API, use credentials, connect to a
ring, or construct a restore command.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


DEFAULT_AOT_ROOT = (
    Path(__file__).resolve().parents[3]
    / "SybilSight-v2"
    / "firmware"
    / "blutter_output_2.2.0"
    / "asm"
)


def require(text: str, marker: str, label: str) -> dict[str, object]:
    if marker not in text:
        raise SystemExit(f"missing {label}: {marker!r}")
    return {
        "label": label,
        "marker": marker,
        "line": text[: text.index(marker)].count("\n") + 1,
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aot-root", type=Path, default=DEFAULT_AOT_ROOT)
    args = parser.parse_args()

    home_path = (
        args.aot_root
        / "even/pages/main_screen/tab_page/home/home_controller.dart"
    )
    model_path = (
        args.aot_root
        / "even_connect/ring1/models/system/ble_ring1_system_nv_recover.dart"
    )
    cache_path = (
        args.aot_root
        / "even/pages/main_screen/tab_page/home/cache/ring_nv_recover_disk_cache.dart"
    )
    cache_model_path = (
        args.aot_root
        / "even/pages/main_screen/tab_page/home/cache/ring_nv_recover_cache_models.dart"
    )
    api_path = args.aot_root / "even/common/api/api_service.dart"
    paths = [home_path, model_path, cache_path, cache_model_path, api_path]
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise SystemExit("missing AOT source files:\n" + "\n".join(missing))

    home = home_path.read_text(errors="replace")
    model = model_path.read_text(errors="replace")
    cache = cache_path.read_text(errors="replace")
    cache_model = cache_model_path.read_text(errors="replace")
    api = api_path.read_text(errors="replace")

    flow_markers = [
        require(home, "0x1492aa0: r0 = ApiServiceCommonExt.uploadRingNv()",
                "ring report upload"),
        require(home, "0x1492dd4: r0 = ApiServiceCommonExt.getRingNv()",
                "ring backup download"),
        require(home, "0x1493158: r0 = BleRing1SystemNvRecover.fromBytes()",
                "download envelope parse"),
        require(home, "0x14931ac: r0 = toBytes()", "download envelope reserialize"),
        require(home, "0x14931b0: r16 = Instance_BleRing1StatusMethod",
                "status method argument"),
        require(home, "0x14931bc: r16 = 3000", "restore send timeout"),
        require(home, "[pp+0x24268] Obj!BleRing1SubCmd@20b18d1",
                "NV recovery subcommand object"),
        require(home, "0x14931ec: r0 = BleRing1CmdPublicExt.sendCmd()",
                "phone-to-ring command send"),
    ]
    envelope_markers = [
        require(model, "0x149106c: cmp             x3, #5",
                "fromBytes minimum length"),
        require(model, "0x149110c: ldrh            w7, [x1, x0]",
                "declared uint16 length"),
        require(model, "0x149112c: ldrh            w5, [x1, x0]",
                "declared uint16 CRC"),
        require(model, "0x1491144: cmp             x7, x1",
                "payload length bounded by availability"),
        require(model, "0x1491278: add             x6, x5, #5",
                "toBytes five-byte header allocation"),
        require(model, "0x14912c4: ArrayStore: r4[0] = r0",
                "toBytes command byte"),
        require(model, "0x14912fc: strh            w5, [x1, x0]",
                "toBytes uint16 length"),
        require(model, "0x149131c: strh            w5, [x1, x0]",
                "toBytes uint16 CRC"),
    ]
    cache_markers = [
        require(cache, '"ring_nv_recover_records"', "disk cache key"),
        require(cache, '"ring_nv_recover"', "disk cache prefix/config"),
        require(cache, "RingNvRecoverLogRecord::toJson", "disk cache JSON serialization"),
        require(cache, "RingNvRecoverLogRecord::fromJson", "disk cache JSON decoding"),
    ]
    json_fields = [
        "id",
        "tsMs",
        "type",
        "method",
        "sn",
        "nvLen",
        "nvCrc",
        "bytesLen",
        "bytesBase64",
        "success",
        "httpCode",
        "message",
    ]
    field_markers = [
        require(cache_model, f'"{field}"', f"cache JSON field {field}")
        for field in json_fields
    ]
    api_markers = [
        require(api, "0x1493468: EnterFrame", "getRingNv function"),
        require(api, '0x1493574: r16 = "/v2/g/get_nv\\?sn="',
                "encoded GET URL"),
        require(api, "0x1493588: r0 = encodeQueryComponent()",
                "GET serial URL encoding"),
        require(api, '0x14935f4: r1 = "/v2/g/get_nv"', "GET endpoint"),
        require(api, "0x149360c: r0 = commonHeaders()", "GET authenticated headers"),
        require(api, '0x1493644: r16 = "ring_nv_"', "download filename prefix"),
        require(api, '0x1493658: r16 = ".bin"', "download filename suffix"),
        require(api, "0x1493684: r0 = evenDownload()", "authenticated binary download"),
        require(api, "0x14937d8: EnterFrame", "uploadRingNv function"),
        require(api, "0x1493898: r0 = commonHeaders()", "upload authenticated headers"),
        require(api, '0x14938dc: r16 = "sn"', "multipart serial field"),
        require(api, '0x14938f0: r16 = "nv"', "multipart binary field"),
        require(api, "0x1493904: r0 = MultipartFile.fromBytes()",
                "multipart binary construction"),
        require(api, "0x1493954: r0 = FormData.fromMap()", "multipart form construction"),
        require(api, '0x1493960: r16 = "/v2/g/upload_nv"', "upload endpoint"),
        require(api, "0x149397c: r0 = post()", "upload POST"),
    ]

    result = {
        "analysis": "R1 first-party phone-mediated NV recovery",
        "source": "Even Android 2.2.0 AOT disassembly",
        "files": [
            {"path": str(path), "sha256": sha256(path)}
            for path in paths
        ],
        "flowMarkers": flow_markers,
        "envelopeMarkers": envelope_markers,
        "cacheMarkers": cache_markers,
        "cacheJSONFields": field_markers,
        "apiMarkers": api_markers,
        "apiContract": {
            "downloadMethod": "GET",
            "downloadPath": "/v2/g/get_nv",
            "downloadQuery": ["sn"],
            "downloadFilenameTemplate": "ring_nv_<sn>.bin",
            "uploadMethod": "POST multipart/form-data",
            "uploadPath": "/v2/g/upload_nv",
            "uploadFields": ["sn", "nv"],
            "usesCommonAuthenticatedHeaders": True,
        },
        "conclusions": {
            "localReportIsUploadedByPhone": True,
            "missingLocalStateIsDownloadedByPhone": True,
            "downloadIsParsedAndReserializedBeforeSend": True,
            "sendTimeoutMilliseconds": 3000,
            "minimumEnvelopeBytes": 5,
            "envelopeHeaderBytes": 5,
            "payloadIsLengthBounded": True,
            "diskCacheStoresRawBytesAsBase64": True,
            "diskCacheIsDiagnosticHistoryNotProofOfAuthoritativeBackup": True,
            "networkContactPerformed": False,
            "restoreCommandConstructed": False,
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
