#!/usr/bin/env python3
"""Pin the first-party Android AOT evidence for R1 user-info mediation.

This is a read-only source audit. It does not contact Even's API, read a user profile, connect to
a ring, or construct/transmit a live command.
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
    proto_path = (
        args.aot_root
        / "even_connect/ring1/ble_ring1_cmd_proto.dart"
    )
    wire_model_path = (
        args.aot_root
        / "even_connect/ring1/models/system/ble_ring1_system_user_info.dart"
    )
    unit_path = (
        args.aot_root
        / "even/common/api/models/enums/user_health_metric.dart"
    )
    api_path = args.aot_root / "even/common/api/api_service.dart"
    paths = [home_path, proto_path, wire_model_path, unit_path, api_path]
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise SystemExit("missing AOT source files:\n" + "\n".join(missing))

    home = home_path.read_text(errors="replace")
    proto = proto_path.read_text(errors="replace")
    wire_model = wire_model_path.read_text(errors="replace")
    unit = unit_path.read_text(errors="replace")
    api = api_path.read_text(errors="replace")

    flow_markers = [
        require(home, "0x14905e4: r0 = HomeCtlPublicExt.updateRing1UserInfo()",
                "incoming userInfo dispatch"),
        require(home, "0x1491c88: EnterFrame", "profile response function"),
        require(home, "0x1491cd0: r0 = isConnected()", "ring-connected gate"),
        require(home, "0x1491d28: cmp             w0, NULL",
                "cached global profile gate"),
        require(home, "0x1491d48: LoadField: r2 = r1->field_7",
                "cached gender enum read"),
        require(home, "0x1491d70: sub             x2, x1, #1",
                "gender mapping to wire codes zero through two"),
        require(home, "0x1491d8c: r0 = getAgeFromDateString()",
                "birthday-to-age conversion"),
        require(home, "0x1491d98: r3 = 0", "missing age fallback"),
        require(home, "0x1491e38: d0 = 2.540000", "inch-to-centimeter factor"),
        require(home, "0x1491e54: CallRuntime_LibcRound(double) -> double",
                "height rounding"),
        require(home, "0x1491f08: r2 = 0", "missing weight fallback"),
        require(home, "0x1491f28: r0 = lbToKg()", "pound-to-kilogram conversion"),
        require(home, "0x1491f48: r0 = setUserInfo()", "typed ring sender call"),
    ]
    sender_markers = [
        require(proto, "0x1491f80: EnterFrame", "setUserInfo function"),
        require(proto, "0x1491fc8: r0 = BleRing1SystemUserInfo()",
                "typed wire model allocation"),
        require(proto, "0x1491ff0: StoreField: r1->field_27 = rZR",
                "first reserved UInt16 zero"),
        require(proto, "0x1491ff4: StoreField: r1->field_2f = rZR",
                "second reserved UInt16 zero"),
        require(proto, "0x1491ff8: StoreField: r1->field_37 = rZR",
                "third reserved UInt16 zero"),
        require(proto, "0x1492028: r0 = BleRing1CmdPublicExt.sendCmd()",
                "normal command send"),
    ]
    wire_markers = [
        require(
            wire_model,
            "0x1492060: r4 = 24",
            "tagged Smi 12 supplied to Uint8List allocation",
        ),
        require(wire_model, "0x14920c8: strb            w4, [x1]",
                "gender byte zero"),
        require(wire_model, "0x14920ec: strb            w3, [x1, x0]",
                "age byte one"),
        require(wire_model, "0x149210c: strh            w3, [x1, x0]",
                "height UInt16 at two"),
        require(wire_model, "0x149212c: strh            w3, [x1, x0]",
                "weight UInt16 at four"),
        require(wire_model, "0x1492148: strh            wzr, [x1, x0]",
                "reserved UInt16 at six"),
        require(wire_model, "0x1492164: strh            wzr, [x1, x0]",
                "reserved UInt16 at eight"),
        require(wire_model, "0x1492180: strh            wzr, [x1, x0]",
                "reserved UInt16 at ten"),
    ]
    unit_markers = [
        require(unit, "0x1492228: d0 = 0.453592",
                "pound-to-kilogram factor"),
        require(unit, "0x149223c: stp             fp, lr, [SP, #-0x10]!",
                "pound conversion round setup"),
        require(unit, "0x13dbb70: r0 = Instance_UserHealthMetric",
                "unknown unit defaults to metric"),
        require(unit, "0x13dbbb0: r1 = 2",
                "imperial JSON code"),
    ]
    api_markers = [
        require(api, "0x148e7b8: EnterFrame", "getUserHealth function"),
        require(api, '0x148e7f4: r16 = "/v2/g/health/get_info"',
                "cached health-profile upstream endpoint"),
        require(api, "0x148e804: r0 = evenGet()", "authenticated health-profile GET"),
    ]

    result = {
        "analysis": "R1 first-party phone-mediated user profile",
        "source": "Even Android 2.2.0 AOT disassembly",
        "files": [
            {"path": str(path), "sha256": sha256(path)}
            for path in paths
        ],
        "flowMarkers": flow_markers,
        "senderMarkers": sender_markers,
        "wireMarkers": wire_markers,
        "unitMarkers": unit_markers,
        "apiMarkers": api_markers,
        "wireContract": {
            "length": 12,
            "genderOffset": 0,
            "ageOffset": 1,
            "heightCentimetersUInt16LEOffset": 2,
            "weightKilogramsUInt16LEOffset": 4,
            "reservedUInt16LEOffsets": [6, 8, 10],
            "bytesSixThroughElevenZeroInitialized": True,
        },
        "conversions": {
            "genderEnumToWire": {"male": 0, "female": 1, "preferNotToSay": 2},
            "missingAge": 0,
            "missingHeight": 0,
            "missingWeight": 0,
            "inchesToCentimeters": 2.54,
            "poundsToKilograms": 0.453592,
            "rounding": "libc round",
        },
        "conclusions": {
            "incomingNotificationTriggersResponseAttempt": True,
            "requiresCurrentRingConnection": True,
            "requiresCachedGlobalProfile": True,
            "networkFetchDuringIncomingHandlerProven": False,
            "normalCommandSenderUsed": True,
            "explicitSenderTimeoutProven": False,
            "networkContactPerformed": False,
            "liveCommandConstructed": False,
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
