#!/usr/bin/env python3
"""Pin the production R1 system-settings/REG1-DC/DC route.

This audit is intentionally read-only. It validates bytes in the supplied production application
and markers in the decompiled first-party Android AOT text. It does not connect to a ring, transmit
the state-changing settings command, write nonvolatile storage, or invoke a regulator control.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from summarize_r1_adc_registry import DEFAULT_BASE, mapped_offset
from summarize_r1_gomore_call_graph import direct_thumb_branches_to
from summarize_r1_gomore_input_abi import IMAGE_SHA256


DEFAULT_AOT_ROOT = (
    Path(__file__).resolve().parents[3]
    / "SybilSight-v2"
    / "firmware"
    / "blutter_output_2.2.0"
    / "asm"
)

HANDLER_START = 0x00084524
HANDLER_END = 0x00084628
HANDLER_SHA256 = "eae704a3150d3880f21815ed4517e5a3367af3b8f7b2766106f4449998478fdc"
FLAG_GETTER_START = 0x00073750
FLAG_GETTER_END = 0x00073774
FLAG_GETTER_SHA256 = "4b581bdfcd89ec9aa1cbc931b046527cd16b61befa0edb2fdc2cabbebceb7b54"
FLAG_SETTER_START = 0x00073800
FLAG_SETTER_END = 0x00073830
FLAG_SETTER_SHA256 = "54d98394fa19b74ea1e986d8e79d6610ff07d5da41124849904a41e13477738e"
COMMIT_WRAPPER_START = 0x00073688
COMMIT_WRAPPER_END = 0x00073694
COMMIT_WRAPPER_SHA256 = "af82bebef3e2e92402f1fafa0de3873ff9fb563810886e9cb8a81d835e6cb9fa"
RECORD_READ_START = 0x00073930
RECORD_READ_END = 0x00073964
RECORD_READ_SHA256 = "e403ecf7a8d7a54c94bc191402c8a31a1099063da2483442e2c5a71fb5483b09"
RECORD_WRITE_START = 0x00073968
RECORD_WRITE_END = 0x000739A4
RECORD_WRITE_SHA256 = "9b8c40ba342144b326cb9af0905b442f78c445bb86eb7b9ec6c50b3267da5606"
PAYLOAD_HELPER_START = 0x00082BD4
PAYLOAD_HELPER_END = 0x00082BE6
PAYLOAD_HELPER_SHA256 = "1f0181948d602c0210ecae853b284d17e6b01d0e14a901c8b6548d03d81c9dac"
RESPONSE_HELPER_START = 0x00084C5E
RESPONSE_HELPER_END = 0x00084C82
RESPONSE_HELPER_SHA256 = "b58b72cd8549277a98aad5ac3aee823454e11e4107efc733c4708f25407fab8b"
BLE_BOOT_INIT_START = 0x0004DF18
BLE_BOOT_INIT_END = 0x0004DFBA
BLE_BOOT_INIT_SHA256 = "d67fbc85bf1074f4a2d6f82a4db53e4af6dc0789abfa99ab5bbda54837dbe8fe"
BLE_BOOT_CALLSITE_START = 0x00091F54
BLE_BOOT_CALLSITE_END = 0x00091F84
BLE_BOOT_CALLSITE_SHA256 = "5bd291030aa6933bf17a9414e00c5ec513faefe0ab68414fad7e6b8df7a303e3"
GLASSES_DCDC_ENABLE_CALLBACK_START = 0x0006A668
GLASSES_DCDC_ENABLE_CALLBACK_END = 0x0006A6A8
GLASSES_DCDC_ENABLE_CALLBACK_SHA256 = (
    "8c8d48a26f060436d2ab940fa443c60fdc8ab6c9899285e9eb8c04a542555428"
)
GLASSES_STATUS_HANDLER_START = 0x0006A714
GLASSES_STATUS_HANDLER_END = 0x0006A870
GLASSES_STATUS_HANDLER_SHA256 = (
    "eb3d69ee62b4c1d8d73a8d8da8d4b1d82d80c5c9a77cbc89fee1cf1b5c4fa6fe"
)
GLASSES_STATUS_INIT_START = 0x0006A95C
GLASSES_STATUS_INIT_END = 0x0006A97A
GLASSES_STATUS_INIT_SHA256 = (
    "c1817bdc957f54ca76ef8d70d797a67999d5499242401848747ce427db5b4331"
)
GLASSES_TOUCH_CLOSE_CALLBACK_START = 0x0006A988
GLASSES_TOUCH_CLOSE_CALLBACK_END = 0x0006AA10
GLASSES_TOUCH_CLOSE_CALLBACK_SHA256 = (
    "35f8c60f934c3c8947ce31876974131eea9618eaaf04bbe1f884bc4431d67d4c"
)
GLASSES_CONNECTION_HANDLE_GETTER_START = 0x0004CB34
GLASSES_CONNECTION_HANDLE_GETTER_END = 0x0004CB3A
GLASSES_CONNECTION_HANDLE_GETTER_SHA256 = (
    "e144876acc5d13f879e211a20a854160bc17ba433c0b67e296f74cd659921186"
)
GLASSES_LCD_SLOW_POLICY_START = 0x0004DD78
GLASSES_LCD_SLOW_POLICY_END = 0x0004DDDA
GLASSES_LCD_SLOW_POLICY_SHA256 = (
    "c972202c101e2e5a23d347d01e3d4b5d2b412462711990f3de2b09b4ca81377d"
)
GLASSES_LCD_FAST_POLICY_START = 0x0004E070
GLASSES_LCD_FAST_POLICY_END = 0x0004E0E6
GLASSES_LCD_FAST_POLICY_SHA256 = (
    "9345246d3cd3c253b16e4ec2967f22aa42baa82fb41ef55920eb2e221b9df487"
)

GLASSES_STATUS_STATE_ADDRESS = 0x20006C34
GLASSES_TOUCH_CLOSE_DELAY_MILLISECONDS = 0x96000
GLASSES_DCDC_ENABLE_DELAY_MILLISECONDS = 0x7800
GLASSES_LCD_SLOW_DELAY_MILLISECONDS = 0x2800

REGISTRATION_ADDRESS = 0x0009A52C
REGISTRATION_BYTES = bytes.fromhex("0f00000025450800")

# The package evidence identifies S140 7.2.0. Its public nrf_soc.h defines the unavailable-while-
# disabled SoC SVC base as 0x2c and SD_POWER_DCDC_MODE_SET as base + 19.
S140_SOC_SVC_BASE_NOT_AVAILABLE = 0x2C
S140_POWER_DCDC_MODE_SET_OFFSET = 19
S140_POWER_DCDC_MODE_SET_SVC = 0x3F


def flash_bytes(image: bytes, base: int, start: int, end: int) -> bytes:
    offset = mapped_offset(start, base, len(image))
    return image[offset : offset + end - start]


def checked_range(
    image: bytes,
    base: int,
    start: int,
    end: int,
    expected: str,
) -> dict[str, str]:
    actual = hashlib.sha256(flash_bytes(image, base, start, end)).hexdigest()
    if actual != expected:
        raise ValueError(f"unexpected range 0x{start:08x}...0x{end:08x}: {actual}")
    return {
        "start": f"0x{start:08x}",
        "end_exclusive": f"0x{end:08x}",
        "sha256": actual,
    }


def require_bytes(
    image: bytes,
    base: int,
    address: int,
    expected_hex: str,
    label: str,
) -> dict[str, str]:
    expected = bytes.fromhex(expected_hex)
    actual = flash_bytes(image, base, address, address + len(expected))
    if actual != expected:
        raise ValueError(
            f"unexpected {label} at 0x{address:08x}: {actual.hex()} != {expected.hex()}"
        )
    return {
        "label": label,
        "address": f"0x{address:08x}",
        "bytes": actual.hex(),
    }


def require_c_string(
    image: bytes,
    base: int,
    address: int,
    expected: str,
    label: str,
) -> dict[str, str]:
    encoded = expected.encode("ascii") + b"\0"
    actual = flash_bytes(image, base, address, address + len(encoded))
    if actual != encoded:
        raise ValueError(
            f"unexpected {label} at 0x{address:08x}: "
            f"{actual!r} != {encoded!r}"
        )
    return {
        "label": label,
        "address": f"0x{address:08x}",
        "string": expected,
    }


def require(text: str, marker: str, label: str) -> dict[str, object]:
    if marker not in text:
        raise ValueError(f"missing {label}: {marker!r}")
    return {
        "label": label,
        "marker": marker,
        "line": text[: text.index(marker)].count("\n") + 1,
    }


def branch_addresses(image: bytes, base: int, target: int) -> list[int]:
    return [address for address, _ in direct_thumb_branches_to(image, base, target)]


def summarize(image_path: Path, base: int, aot_root: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != IMAGE_SHA256:
        raise ValueError(f"unexpected image SHA-256: {digest}")

    proto_path = aot_root / "even_connect/ring1/ble_ring1_cmd_proto.dart"
    model_path = (
        aot_root
        / "even_connect/ring1/models/system/ble_ring1_system_settings_status.dart"
    )
    controller_path = (
        aot_root / "even/pages/devices/mine/device_mine_controller.dart"
    )
    aot_paths = [proto_path, model_path, controller_path]
    missing = [str(path) for path in aot_paths if not path.is_file()]
    if missing:
        raise ValueError("missing AOT source files:\n" + "\n".join(missing))
    proto = proto_path.read_text(errors="replace")
    model = model_path.read_text(errors="replace")
    controller = controller_path.read_text(errors="replace")

    registration = flash_bytes(
        image,
        base,
        REGISTRATION_ADDRESS,
        REGISTRATION_ADDRESS + len(REGISTRATION_BYTES),
    )
    if registration != REGISTRATION_BYTES:
        raise ValueError(f"unexpected system-settings registration: {registration.hex()}")

    expected_branches = {
        FLAG_GETTER_START: [0x0006A78C, 0x00084548, 0x00084608],
        FLAG_SETTER_START: [0x0008461A],
        PAYLOAD_HELPER_START: [
            0x00083D0C,
            0x00083FC6,
            0x00084154,
            0x000842D0,
            0x000842F4,
            0x000843D0,
            0x000844B8,
            0x000844F4,
            0x000845C2,
            0x000846EE,
            0x0008487A,
            0x00084A1A,
        ],
        RESPONSE_HELPER_START: [
            0x00083DDC,
            0x00083FBA,
            0x00084366,
            0x000845A8,
            0x00084896,
        ],
    }
    verified_branches: dict[str, list[str]] = {}
    for target, expected in expected_branches.items():
        actual = branch_addresses(image, base, target)
        if actual != expected:
            raise ValueError(
                f"unexpected direct branches to 0x{target:08x}: "
                f"{[hex(value) for value in actual]}"
            )
        verified_branches[f"0x{target:08x}"] = [
            f"0x{address:08x}" for address in actual
        ]
    if direct_thumb_branches_to(image, base, HANDLER_START):
        raise ValueError("table-dispatched system-settings handler acquired a direct branch")

    instruction_evidence = [
        require_bytes(
            image, base, 0x00084528, "48790c4640f34001",
            "method-set flag is request-header byte 5 bit 1",
        ),
        require_bytes(
            image, base, 0x00084546, "02a8eff702f9",
            "read path obtains the persisted flag",
        ),
        require_bytes(
            image, base, 0x0008454C, "04969df80800039605968df81100cdf81260adf81660",
            "read response is zero except payload byte 5",
        ),
        require_bytes(
            image, base, 0x00084596, "0c2103a8cde90001b4f8033000220f21384600f0",
            "read path sends exactly 12 payload bytes",
        ),
        require_bytes(
            image, base, 0x000845B0, "0096b4f8033001220f213846fef75ef9",
            "set path sends empty success acknowledgement first",
        ),
        require_bytes(
            image, base, 0x000845C0, "2046fef707fb0400f0d0",
            "payload helper is consulted only after acknowledgement",
        ),
        require_bytes(
            image, base, 0x00084600, "20790028d2d1",
            "only switch type zero is accepted",
        ),
        require_bytes(
            image, base, 0x00084606, "02a8eff7a2f860799df808108842cad0",
            "requested raw byte is compared with the persisted Boolean before normalization",
        ),
        require_bytes(
            image, base, 0x00084616, "00b10120eff7f1f8",
            "changed requested byte is normalized to zero or one and persisted",
        ),
        require_bytes(
            image, base, 0x0008461E, "607900b101203fdf",
            "requested byte is normalized again and passed to SVC 0x3f",
        ),
        require_bytes(
            image, base, 0x00073766, "9df81800c0f34000",
            "persistent flag is dev_info byte 24 bit 1",
        ),
        require_bytes(
            image, base, 0x00073812, "9df81800342264f341008df81800",
            "setter inserts the Boolean into dev_info byte 24 bit 1",
        ),
        require_bytes(
            image, base, 0x00073820, "6946286800f0a0f8fff72eff",
            "setter writes the record then invokes the commit wrapper",
        ),
        require_bytes(
            image, base, 0x0004DF5E, "00f0a9fa01203fdf",
            "BLE platform initialization unconditionally enables REG1 DC/DC",
        ),
        require_bytes(
            image, base, 0x00091F6A, "baf7f5fdbbf7d3ff",
            "system startup calls the BLE platform initializer",
        ),
        require_bytes(
            image, base, 0x0006A720, "3879c609c0f3801501203871",
            "glasses status byte bit 7 is wear and bit 6 is LCD, then byte is normalized",
        ),
        require_bytes(
            image, base, 0x0006A778, "99f90300b04260d089f80360",
            "automatic policy runs only when signed glasses-wear state changes",
        ),
        require_bytes(
            image, base, 0x0006A784, "00208df80000684608f0e0ff",
            "wear transition reads the persisted software-DCDC policy bit",
        ),
        require_bytes(
            image, base, 0x0006A79E, "fbf7e1fa002024f014f8",
            "glasses-worn transition cancels deferred touch close and acquires touch source zero",
        ),
        require_bytes(
            image, base, 0x0006A7A8, "9df80000002848d1",
            "persisted one suppresses automatic DCDC work while glasses are worn",
        ),
        require_bytes(
            image, base, 0x0006A7B0, "00214448fbf7d6fa",
            "automatic worn policy cancels the deferred DCDC-enable callback",
        ),
        require_bytes(
            image, base, 0x0006A7E2, "00203fdf",
            "automatic worn policy immediately disables REG1 DC/DC",
        ),
        require_bytes(
            image, base, 0x0006A7E8, "fbf7bcfa4ff4162200213348fbf7aaf9",
            "glasses-removed transition schedules touch-source-zero close after 0x96000 ms",
        ),
        require_bytes(
            image, base, 0x0006A7F8, "9df80000002820d1",
            "persisted one suppresses automatic DCDC work after glasses removal",
        ),
        require_bytes(
            image, base, 0x0006A800, "00213048fbf7aefa",
            "automatic removed policy cancels an older deferred DCDC-enable callback",
        ),
        require_bytes(
            image, base, 0x0006A836, "4ff4f04200212148fbf785f9",
            "automatic removed policy schedules REG1 DCDC enable after 0x7800 ms",
        ),
        require_bytes(
            image, base, 0x0006A6A2, "01203fdf",
            "deferred glasses callback enables REG1 DC/DC",
        ),
        require_bytes(
            image, base, 0x0006A96E, "05484ff0ff31c1700171",
            "glasses wear and LCD previous-state bytes initialize to signed minus one",
        ),
        require_bytes(
            image, base, 0x0006A994, "ea78032101eb004422b1",
            "deferred touch close rechecks current glasses-wear state",
        ),
        require_bytes(
            image, base, 0x0006A9D4, "bde87040002023f061be",
            "deferred touch callback releases source zero only while glasses remain removed",
        ),
        require_bytes(
            image, base, 0x0004CB34, "014840897047",
            "glasses LCD transition obtains the current connection handle",
        ),
        require_bytes(
            image,
            base,
            0x0004DDba,
            "24042146204817f0d0ff0db1002201e04ff420522146bde870401a4817f0b9be",
            "LCD-inactive path selects the 0x2800 ms delayed-slow connection policy",
        ),
        require_bytes(
            image,
            base,
            0x0004E0B6,
            "2104244817f053fe012000eb0441214817f04dfe022000eb04410c461e4817f046fe2146bde8104000221a4817f033bd",
            "LCD-active path cancels slow callbacks and schedules immediate fast connection policy",
        ),
    ]
    string_evidence = [
        require_c_string(
            image,
            base,
            0x0006A87C,
            "glasses_status_cmd: glass_wear_status=%d, glass_lcd_status=%d",
            "glasses status field log",
        ),
        require_c_string(
            image,
            base,
            0x0006A8C8,
            "[RING]glasses_status_cmd: disable dcdc",
            "immediate worn DCDC-disable log",
        ),
        require_c_string(
            image,
            base,
            0x0006A914,
            "[RING]glasses_status_cmd: enable dcdc",
            "deferred removed DCDC-enable schedule log",
        ),
        require_c_string(
            image,
            base,
            0x0006A6A8,
            "[RING]glasses_dcdc_deferred_enable_cb: enable dcdc",
            "deferred DCDC-enable callback log",
        ),
        require_c_string(
            image,
            base,
            0x0006AA1C,
            "[RING]glasses_touch_close_deferred_cb: close touch",
            "deferred touch-close log",
        ),
        require_c_string(
            image,
            base,
            0x0006AA84,
            "glasses_touch_close_deferred_cb: skip close, wear_status=%d",
            "deferred touch-close recheck log",
        ),
    ]

    proto_markers = [
        require(proto, "0x141a9b8: EnterFrame", "first-party read routine"),
        require(proto, "0x141aa0c: r0 = BleRing1CmdPublicExt.sendCmd()",
                "first-party settings read send"),
        require(proto, "0x141aa2c: r0 = fromBytes()", "typed read decode"),
        require(proto, "0x1571660: EnterFrame", "first-party set routine"),
        require(proto, "0x15716ac: r0 = toBytes()", "first-party set serialization"),
        require(proto, "0x15716b0: r16 = Instance_BleRing1StatusMethod",
                "set-method selection"),
        require(proto, "0x15716e0: r0 = BleRing1CmdPublicExt.sendCmd()",
                "first-party settings set send"),
        require(proto, "0x15716f0: LoadField: r1 = r0->field_b",
                "set result is protocol success Boolean"),
    ]
    model_markers = [
        require(model, "0x141a868: r4 = 24",
                "tagged Smi 12 supplied to Uint8List allocation"),
        require(model, "0x141a86c: r0 = AllocateUint8Array()",
                "12-byte first-party serializer allocation"),
        require(model, "0x141a8dc: ArrayStore: r3[4] = r1",
                "switch type at byte four"),
        require(model, "0x141a8f0: ArrayStore: r3[5] = r1",
                "switch status at byte five"),
        require(model, "0x141a914: cmp             x2, #6",
                "six reserved bytes serialized"),
        require(model, "0x141aa70: cmp             x3, #0xc",
                "read parser minimum is 12 bytes"),
        require(model, "0x141aaec: ldrb            w4, [x0, #4]",
                "read parser switch type byte"),
        require(model, "0x141ab08: ldrb            w5, [x0, #5]",
                "read parser switch status byte"),
        require(model, "0x141ab18: r16 = 24",
                "tagged Smi reserved-slice end 12"),
        require(model, "0x141ab24: r2 = 12",
                "tagged Smi reserved-slice start 6"),
        require(model, "0x1571728: r0 = _getCurrentMicros()",
                "factory derives current Unix seconds"),
        require(model, "0x1571760: tst             x0, #0x10",
                "factory maps requested Dart Boolean to zero or one"),
        require(model, "0x1571780: ldur            x3, [fp, #-0x10]",
                "factory preserves the prior switch type"),
    ]
    controller_markers = [
        require(controller, "0x15713f0: r0 = BleRing1CmdSettingsStatusExt.getSystemSettingsStatus()",
                "first-party read-before-write"),
        require(controller, "0x1571470: LoadField: r5 = r0->field_f",
                "prior switch type extracted"),
        require(controller, "0x1571484: r0 = BleRing1SystemSettingsStatus.forSwitchStatus()",
                "new settings preserve prior switch type"),
        require(controller, "0x15714a0: r0 = BleRing1CmdSettingsStatusExt.setSystemSettingsStatus()",
                "first-party settings write"),
        require(controller, "0x15714b0: r16 = true",
                "protocol success Boolean comparison"),
        require(controller, "0x15714b8: b.eq            #0x157151c",
                "success branch does not re-read settings"),
        require(controller, '0x1571554: r16 = "setRingLowPerformanceMode success, lowPerf="',
                "first-party success log"),
    ]

    if S140_SOC_SVC_BASE_NOT_AVAILABLE + S140_POWER_DCDC_MODE_SET_OFFSET \
            != S140_POWER_DCDC_MODE_SET_SVC:
        raise ValueError("internal S140 SVC mapping mismatch")

    return {
        "analysis": "R1 production system-settings and REG1 DC/DC route",
        "image": str(image_path),
        "image_sha256": digest,
        "load_base": f"0x{base:08x}",
        "registration": {
            "address": f"0x{REGISTRATION_ADDRESS:08x}",
            "bytes": registration.hex(),
            "subcommand": "0x0f",
            "handler_thumb": f"0x{HANDLER_START | 1:08x}",
        },
        "verified_ranges": [
            checked_range(image, base, HANDLER_START, HANDLER_END, HANDLER_SHA256),
            checked_range(
                image, base, FLAG_GETTER_START, FLAG_GETTER_END, FLAG_GETTER_SHA256
            ),
            checked_range(
                image, base, FLAG_SETTER_START, FLAG_SETTER_END, FLAG_SETTER_SHA256
            ),
            checked_range(
                image,
                base,
                COMMIT_WRAPPER_START,
                COMMIT_WRAPPER_END,
                COMMIT_WRAPPER_SHA256,
            ),
            checked_range(
                image, base, RECORD_READ_START, RECORD_READ_END, RECORD_READ_SHA256
            ),
            checked_range(
                image, base, RECORD_WRITE_START, RECORD_WRITE_END, RECORD_WRITE_SHA256
            ),
            checked_range(
                image, base, PAYLOAD_HELPER_START, PAYLOAD_HELPER_END,
                PAYLOAD_HELPER_SHA256,
            ),
            checked_range(
                image, base, RESPONSE_HELPER_START, RESPONSE_HELPER_END,
                RESPONSE_HELPER_SHA256,
            ),
            checked_range(
                image, base, BLE_BOOT_INIT_START, BLE_BOOT_INIT_END,
                BLE_BOOT_INIT_SHA256,
            ),
            checked_range(
                image, base, BLE_BOOT_CALLSITE_START, BLE_BOOT_CALLSITE_END,
                BLE_BOOT_CALLSITE_SHA256,
            ),
            checked_range(
                image,
                base,
                GLASSES_DCDC_ENABLE_CALLBACK_START,
                GLASSES_DCDC_ENABLE_CALLBACK_END,
                GLASSES_DCDC_ENABLE_CALLBACK_SHA256,
            ),
            checked_range(
                image,
                base,
                GLASSES_STATUS_HANDLER_START,
                GLASSES_STATUS_HANDLER_END,
                GLASSES_STATUS_HANDLER_SHA256,
            ),
            checked_range(
                image,
                base,
                GLASSES_STATUS_INIT_START,
                GLASSES_STATUS_INIT_END,
                GLASSES_STATUS_INIT_SHA256,
            ),
            checked_range(
                image,
                base,
                GLASSES_TOUCH_CLOSE_CALLBACK_START,
                GLASSES_TOUCH_CLOSE_CALLBACK_END,
                GLASSES_TOUCH_CLOSE_CALLBACK_SHA256,
            ),
            checked_range(
                image,
                base,
                GLASSES_CONNECTION_HANDLE_GETTER_START,
                GLASSES_CONNECTION_HANDLE_GETTER_END,
                GLASSES_CONNECTION_HANDLE_GETTER_SHA256,
            ),
            checked_range(
                image,
                base,
                GLASSES_LCD_SLOW_POLICY_START,
                GLASSES_LCD_SLOW_POLICY_END,
                GLASSES_LCD_SLOW_POLICY_SHA256,
            ),
            checked_range(
                image,
                base,
                GLASSES_LCD_FAST_POLICY_START,
                GLASSES_LCD_FAST_POLICY_END,
                GLASSES_LCD_FAST_POLICY_SHA256,
            ),
        ],
        "verified_direct_branches": verified_branches,
        "instruction_evidence": instruction_evidence,
        "string_evidence": string_evidence,
        "firmware_contract": {
            "read_payload_bytes": 12,
            "read_payload_layout": {
                "bytes_0_through_4": "zero",
                "byte_5": "persisted dev_info byte 24 bit 1",
                "bytes_6_through_11": "zero",
            },
            "set_acknowledgement": "empty success ACK emitted before validation or effect",
            "set_payload_pointer_rule": (
                "the shared helper returns request+12 unless total logical length equals 12; "
                "the stock 12-byte payload produces a 24-byte logical command"
            ),
            "accepted_switch_type": 0,
            "requested_status_normalization": "zero remains 0; every nonzero byte becomes 1",
            "unchanged_raw_status": "ACK only; no record write, commit, or SVC",
            "changed_raw_status": (
                "write normalized Boolean to dev_info byte 24 bit 1, invoke commit wrapper, "
                "then pass normalized Boolean to SVC 0x3f"
            ),
        },
        "automatic_glasses_policy": {
            "handler": f"0x{GLASSES_STATUS_HANDLER_START:08x}",
            "state_address": f"0x{GLASSES_STATUS_STATE_ADDRESS:08x}",
            "input_contract": {
                "record_byte_3_required": 1,
                "record_byte_4_bit_7": "glasses worn",
                "record_byte_4_bit_6": "glasses LCD active",
                "previous_wear_offset": 3,
                "previous_lcd_offset": 4,
                "initial_previous_values": -1,
            },
            "runs_only_on_wear_transition": True,
            "persisted_flag_zero": {
                "meaning": "wear-driven automatic REG1 DCDC switching enabled",
                "glasses_worn": "cancel deferred enable and disable REG1 immediately",
                "glasses_removed": (
                    "cancel older deferred enable and schedule REG1 enable after "
                    f"{GLASSES_DCDC_ENABLE_DELAY_MILLISECONDS} ms"
                ),
            },
            "persisted_flag_one": {
                "meaning": (
                    "public set forces REG1 enabled and later glasses-wear transitions "
                    "suppress automatic DCDC switching"
                ),
                "glasses_worn": "no automatic DCDC action",
                "glasses_removed": "no automatic DCDC action",
            },
            "touch_lifecycle": {
                "source": 0,
                "glasses_worn": "cancel deferred close and acquire touch service source zero",
                "glasses_removed": (
                    "cancel prior close and schedule source-zero release after "
                    f"{GLASSES_TOUCH_CLOSE_DELAY_MILLISECONDS} ms"
                ),
                "close_callback_rechecks_wear": True,
            },
            "delays_milliseconds": {
                "dcdc_enable_after_glasses_removed":
                    GLASSES_DCDC_ENABLE_DELAY_MILLISECONDS,
                "touch_close_after_glasses_removed":
                    GLASSES_TOUCH_CLOSE_DELAY_MILLISECONDS,
            },
            "boot_behavior": (
                "BLE platform initialization unconditionally calls "
                "sd_power_dcdc_mode_set(ENABLE) before any observed glasses transition"
            ),
            "lcd_transition_side_effects": {
                "lcd_active": (
                    "read connection handle and request connection-scoped fast BLE policy"
                ),
                "lcd_inactive": (
                    "read connection handle and request the slow BLE policy after "
                    f"{GLASSES_LCD_SLOW_DELAY_MILLISECONDS} ms"
                ),
                "fast_delay_milliseconds": 0,
                "slow_delay_milliseconds": GLASSES_LCD_SLOW_DELAY_MILLISECONDS,
                "classification": "connection policy, not touch sensor report rate",
            },
        },
        "s140_7_2_0_abi": {
            "soc_svc_base_not_available": f"0x{S140_SOC_SVC_BASE_NOT_AVAILABLE:02x}",
            "sd_power_dcdc_mode_set_offset": S140_POWER_DCDC_MODE_SET_OFFSET,
            "svc": f"0x{S140_POWER_DCDC_MODE_SET_SVC:02x}",
            "function": "sd_power_dcdc_mode_set",
            "argument_0": "NRF_POWER_DCDC_DISABLE",
            "argument_1": "NRF_POWER_DCDC_ENABLE",
            "regulator_stage": "REG1",
        },
        "first_party_android_2_2_0": {
            "payload_bytes": 12,
            "flow": (
                "optimistically update UI; read current settings; preserve switch type; serialize "
                "Unix seconds, switch type, requested 0/1 and six reserved bytes; send set-method; "
                "treat protocol success Boolean as success without post-write readback"
            ),
            "false_positive_case": (
                "a nonzero switch type is preserved and sent; firmware already ACKed success but "
                "silently ignores the requested state"
            ),
            "proto_markers": proto_markers,
            "model_markers": model_markers,
            "controller_markers": controller_markers,
        },
        "safety": {
            "live_command_executed": False,
            "ble_connection_attempted": False,
            "nonvolatile_state_changed": False,
            "regulator_control_invoked": False,
            "required_product_behavior": (
                "explicit authorization, exact production version, stock switch type zero, "
                "12-byte payload, and post-write readback are required"
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=Path)
    parser.add_argument("--base", type=lambda value: int(value, 0), default=DEFAULT_BASE)
    parser.add_argument("--aot-root", type=Path, default=DEFAULT_AOT_ROOT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = summarize(args.image, args.base, args.aot_root)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    print(f"R1 system-settings route: {result['image_sha256']}")
    print(
        "  read: 12 bytes, bytes 0...4/6...11 zero; "
        "byte 5 = dev_info[24].bit1"
    )
    print(
        "  set: ACK first; type 0 only; changed normalized Boolean persists then "
        "sd_power_dcdc_mode_set(Boolean)"
    )
    print(
        "  phone: 12-byte payload, read-before-write, preserves type, "
        "no post-write verification"
    )
    print(
        "  policy: boot enables REG1; stored 0 follows glasses wear "
        "(worn=disable now, removed=enable after 30,720 ms); stored 1 "
        "suppresses wear switching after forcing REG1 enabled"
    )
    print(
        f"  verified {len(result['verified_ranges'])} firmware ranges, "
        f"{len(result['instruction_evidence'])} instruction spans, and "
        f"{sum(len(result['first_party_android_2_2_0'][key]) for key in ('proto_markers', 'model_markers', 'controller_markers'))} "
        "AOT markers"
    )


if __name__ == "__main__":
    main()
