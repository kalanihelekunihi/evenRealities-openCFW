#!/usr/bin/env python3
"""Validate the R1 PPG respiratory-rate and motion/step algorithm domains.

This version-pinned, read-only parser connects the complete GoMore I/O ABI to the internal
resampler, periodicity estimator, motion classifier, and stock step accumulator. It establishes
algorithmic units and ranges without executing vendor code, reading live SRAM, or treating an
undocumented result as a clinically validated measurement.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
from pathlib import Path
from typing import Any

from summarize_r1_adc_registry import DEFAULT_BASE, mapped_offset
from summarize_r1_gomore_call_graph import direct_thumb_branches_to
from summarize_r1_gomore_output_abi import FIELDS, IMAGE_SHA256


# Half-open code-only ranges. Literal constants are validated separately below.
EXPECTED_RANGE_SHA256 = {
    (0x00060A14, 0x00060ADC): "713f3edee450b41bc42c1e03614a6b0c734b81c7dde98f7c3cfad68d166d109c",
    (0x0008247E, 0x000824A0): "56d908ecf435762995f15ab709bc7eda434df7e298ac106117c2a5a8eca3bacb",
    (0x00060680, 0x00060960): "cfc99e785d7b1636fae425a7dcddd06623517bdfe0c63f2fb8e720899b52980f",
    (0x00069834, 0x00069C50): "cc4afba99d15e84367104fbbc83935393babb701ac7ccf2b25ef3d65edb24bec",
    (0x000948D8, 0x00094934): "93e7a0448605648e17470aba5610b68b7cdc01f8cbf1009ce42dfc766bcf0190",
    (0x00068840, 0x00068C68): "8ddfaa560776752cc68317018701b59e8b9a119e089d59b8f1f5fa3c68a6bc1c",
    (0x00056C54, 0x00056CD0): "6680dcb6c17fdbba31e78be65d21246fc462490e9a0f0b2a952b3cdf90295e3f",
    (0x00056DC0, 0x00056F6C): "043ad69ea401642e4e21e055c845f7a0c9ac9ce3a9041dc0cc42940883a375ce",
    (0x000647C4, 0x000649B8): "91087307067553eb27a0da80bf762f3bd9793b5923875f102819533ff7e08546",
    (0x00064380, 0x00064740): "c3aa38cbb7fdb6d2d2bffbf11e17377b790b111ea9475553b816a3514878442a",
    (0x0004857C, 0x0004892C): "892d36f777ce7ff81f89df9369cecc9a1257083e43da039222b0831904ce4f2d",
    (0x00076120, 0x00076174): "859b46ac53fdf772c1b24d07fdd46e473a74f2f1cd3750842cd45ca493a7adad",
    (0x000967A0, 0x000967C4): "d22ee7fbf0db00d0248b4b01f853503608aad34cf73fe1b4a1ec52c1a58f2d97",
    (0x0005ED14, 0x0005EF1C): "398023d9c119c2c485b3883ad5c039ba31dbc3e9e2e558fa51b5710a14a104e9",
    (0x0005F4B6, 0x0005F56C): "994a48c19b1c037a5452fb4c88585b83316b2146714ce55461333d2bffae689d",
    (0x00093DCC, 0x00093E0C): "a13c583663e6dad43b8f5107d8506c4d621cfb23c5ff43d36df4db266e8927de",
    (0x0009413C, 0x0009424C): "bfac2d9309c795151b73cf4ac2d203003b0040159b277684a6703a33dc6bf45e",
    (0x00057F8C, 0x00058050): "c694786a4f493ebed736d9414ede59659bca7689f6586d4715c67f319093f51e",
    (0x00058060, 0x000581E8): "22d69de6cdd4474912a122a8d741a42cfba398e486e621de289ee552d2803da7",
    (0x00067A40, 0x00067B24): "abd8b0f791495248d03a6a58e2b7baf0006cfb10aebfc937e16136c490c3f07e",
    (0x00061198, 0x00061260): "fe7762ba8660177034b10b718e3744a2d7c9dfc07a291548cff3787ba9f3a2d4",
    (0x00048960, 0x0004898C): "c9acd8eb8bd7d17f13080547426093ef7f5456c7616336d716d2887ddbad1e2c",
    (0x00071D9E, 0x00071DB6): "2d28c408af88e4672aa89bce4c19275ee3e507cdd7e850420f3cfdf2a17a8f96",
    (0x000710D4, 0x000710FC): "e51cd34837a398ad3ce1a3a8c54f2ba9d2393bd9a8c92be588b796a3e7224e00",
    (0x0004834A, 0x000484A8): "01d4adf85d968202c36d7370bd647d2cbd73137be616967b9e4a4ee29225e6eb",
    (0x000484FC, 0x0004857A): "fff2c0fdf8beefcc393436ed211fd2d627dc68b4bb5ddbc96aad98ae75878c6e",
    (0x00067E4C, 0x0006807A): "7f00b5e9a95dc2faf5dde95a632f56c31c390b587d1be505a8501a169a808705",
    (0x00058480, 0x000584A8): "4f218ad60f023e12e4737fe13136b51237d0d3aa95ec18412c65caaa2dcdf151",
    (0x000722EC, 0x0007230E): "f4ffcde6d287e58a3933f14a49e40155212e5264d6e2437ad24c0586bae3cab5",
    (0x000723B6, 0x000723EA): "ea4262b55852786e59c6133366ba7e33041a4868d99cf765dac2a64616cae041",
    (0x000568F0, 0x00056920): "a0cc4d9d91f96708d93386ed4d25784b6eab8944c98d1101f70d85adf8f69e02",
    (0x0008F4B4, 0x0008F4E6): "19314632f3f9bce17a75bff1c8f2ea7323cc77bb65b0536aeb660d6edcb7c0aa",
    (0x00056980, 0x000569B8): "02c01f9f99424ed61a01abb0df7accdf9568c5e72a9ab3c48f120002cf8533f3",
    (0x000569BC, 0x00056A0C): "7d2d134d064d33c61c1c0e21f27089b4ea6ecbabef95fb4f61a3d7c31277195d",
    (0x00058256, 0x000582C4): "fa8ee4a9c35656cc229da0d095343258263f84883518112bf050b162366f2b2b",
    (0x00056A0C, 0x00056B92): "624f20b0e8d75f62ce684df4221ca9c8fcae97995fd3ec915d1491b61db0dad7",
    (0x000583C8, 0x0005845E): "90e334314f24d5562e7b8d36d8efac5b53f670aebda7a791368f1427703156c6",
    (0x000582C4, 0x000583C8): "ad49c4813fc0643d713d121478e379c1885e2d03d523ebca4b4d6aa46474f9ec",
    (0x0005C5F0, 0x0005CB1E): "751b1991279337f88b5558ea7a287b930d9e7452df7a229489cb90abf7bb2ca0",
    (0x0008F4E8, 0x0008F66E): "bf787f214effe8a9fdc6c8cc62ee846e426419e5c205940e4fcccc4c3c532aef",
    (0x00074880, 0x000748CC): "f228fd39c677f7248590ec9d1238f2d42a1909f61c48a4082e653211312960c3",
    (0x00056920, 0x00056976): "45c0d7e749d77588d583e8c026acfae681c0c3fac791f94e20a3ef2c430395b1",
    (0x00056D78, 0x00056DBA): "035934221eb22e66e34d50da422ad6094b0c465e8efc7d1ff81d39d718ed6023",
    (0x00056CF4, 0x00056D70): "e99286a607e88e565a55c26e031f92fe252d6ca7b4fc8490e8eaade2fca3c4a9",
    (0x00056F94, 0x000575B4): "10619cf14c4a1ba49ebe63924728a5d738414c86331b36c932d8ec3fe3d7efe2",
    (0x0008F3C8, 0x0008F496): "ac0d4c25e3e3b40a544b4824301c3cd60305ae76aa94098ec6446ad6197cf5cb",
    (0x00058AEE, 0x00058B6E): "f0e0bb437769059e98f261907e4ff569fe8a2d856e627d7fb397353613889e3b",
    (0x0007EAF6, 0x0007EB30): "0622ba4fb1f29f46ece7772677ac81c5376c0309a44b04babf01d4127ba47c1e",
    (0x000761F8, 0x000763A2): "ac2dd941b173e24534b28f6fc94f4b1a94a53c698072742e7905a606835f726f",
    (0x00071188, 0x000711AA): "6987bf73fc63cf799c9b18b9e5bff535b94660f504ffac55c78cb4d7ee4b6784",
    (0x00094250, 0x00094270): "b2869a81694844044146a56478adcbfa0d6b0255b8f3eff6c518d852befc2d4a",
    (0x0005A40E, 0x0005A442): "7dcd47e2af07de3bdf1820d866c2e31355a7e246413dbb978c4a945ab1867741",
    (0x00080FF4, 0x0008103E): "6e92827f7d68781052cfa51f461de024ae97bc17a0f6f93dbd679440fd344498",
    (0x00057C20, 0x00057C44): "cb1a42bbf6c1cdc6f797079f3ecc86ee0d9c43f4e47860bd79296cafdd4418ff",
    (0x00067B24, 0x00067BB8): "95b6f4965107033e145c76a8c775e61b79d99e4906593fc7a9f95541d8765e89",
    (0x00070AF8, 0x00070B5A): "ec51fc10a3411c838dc1152e2645e733bedaff46e7311a05d75bf53c8d1e2113",
    (0x00077162, 0x0007719A): "78006568e8357eb5f2a763eae4bf54ae3a2f963b24b9dfa3665fcfd05f991860",
    (0x000484E8, 0x000484FC): "75561bc0d0204f1cbf87d293bf69ed3f7c12cf25e1e9fa0116c3ada92dc2ba18",
    (0x000484CA, 0x000484E8): "3c13dc08b552ee4a631a346c1412e2bbfe98c294e9fc361b392ceca5b5b25e03",
}

EXPECTED_DIRECT_BRANCHES = {
    0x00060A14: [0x000945BC],
    0x0008247E: [0x00060A72],
    0x00060680: [0x0005FFD2, 0x0005FFE2],
    0x00069834: [0x00060746],
    0x000948D8: [0x000698A6, 0x000698C8, 0x000698E0, 0x00069916],
    0x00068840: [0x00056F62, 0x00069B50],
    0x00056C54: [0x00068D04],
    0x00056DC0: [0x00069A68, 0x00069A86],
    0x000647C4: [0x000688C0, 0x00069940],
    0x00064380: [0x0006995A],
    0x0004857C: [0x0006996C],
    0x00076120: [0x000608D2, 0x000608F6],
    0x000967A0: [0x000608AA],
    0x0005ED14: [0x00060026, 0x00060036],
    0x0005F4B6: [0x0006007C, 0x00060092],
    0x00093DCC: [0x0005A43A],
    0x0009413C: [0x0005F562],
    0x00057F8C: [0x0009416A],
    0x00058060: [0x00094190],
    0x00067A40: [0x00094238],
    0x00061198: [0x0006053C, 0x00060550],
    0x00048960: [0x000611BA],
    0x00071D9E: [0x00071AFE],
    0x000710D4: [0x0005EE80, 0x00071A4E],
    0x0004834A: [0x0005EE34],
    0x000484FC: [0x0005EE9E],
    0x00067E4C: [0x0005EF12],
    0x00058480: [0x0005EE7A, 0x0005EEEA, 0x0005EF08],
    0x000722EC: [0x0004835C, 0x00048366, 0x00048370, 0x0004837A],
    0x000723B6: [0x000483A8, 0x000483C4, 0x000483E2, 0x0004840C],
    0x000568F0: [0x00048426],
    0x0008F4B4: [0x0004843E, 0x00048452, 0x00048466, 0x0004847A],
    0x00056980: [0x00067E6A, 0x00067E76, 0x00067E80, 0x00067E8E],
    0x000569BC: [0x00067EBC, 0x00068048],
    0x00058256: [0x00067FF8],
    0x00056A0C: [0x00068022],
    0x000583C8: [0x0006802A],
    0x000582C4: [0x00068068],
    0x0005C5F0: [0x00056DB2],
    0x0008F4E8: [0x0005C8F8],
    0x00074880: [0x0005CA1E, 0x0005CAD6],
    0x00056920: [0x00067FD0],
    0x00056D78: [0x00067EEC],
    0x00056CF4: [0x00067F0C],
    0x00056F94: [0x00056D2C, 0x00056D3C],
    0x0008F3C8: [0x000570F8, 0x0005713A, 0x000571FE],
    0x00058AEE: [0x00056D1A],
    0x0007EAF6: [0x00067EFE],
    0x000761F8: [0x00057324, 0x0005737C],
    0x00071188: [0x00071A58],
    0x00094250: [0x0005F538],
    0x0005A40E: [0x0005F548],
    0x00080FF4: [0x0005F550],
    0x00057C20: [0x0005F558],
    0x00067B24: [0x00094214],
    0x00070AF8: [0x00067A88, 0x00067AF8, 0x00067B8A],
    0x00077162: [0x00067B10, 0x00067BA2],
    0x000484E8: [0x00094206],
    0x000484CA: [0x0005F4FA, 0x00094222, 0x00094260],
}

PRODUCTION_THUMB_STEP_FIXTURES = {
    "steady_100_candidate": "0x3fd77777",
    "steady_100_fifth_emission": "0x4106aaaa",
    "steady_100_sixth_emission": "0x3fd77777",
    "one_missing_update_return_candidate": "0x40577777",
    "one_missing_update_fifth_emission": "0x41219999",
    "two_missing_updates_return_candidate": "0x40a19999",
    "two_missing_updates_fifth_emission": "0x413c8888",
    "cadence_120_elapsed_3_candidate": "0x40c1999a",
    "cadence_120_elapsed_3_fifth_emission": "0x41f20000",
    "cadence_120_elapsed_4_candidate": "0x40011111",
}

PRODUCTION_THUMB_LOCOMOTION_FIXTURES = {
    "fourth_update_base_feature_bits": [
        "0x422d0000", "0x424c0000", "0x449e5800", "0x43210000"
    ],
    "fifth_update_base_feature_bits": [
        "0x422f3333", "0x424c0000", "0x44a43333", "0x431c0000"
    ],
    "first_delayed_update_history_head": [
        1063, 1068, 1073, 1079, 1084, 1090, 1095, 1101, 1106, 1112, 1118, 1123
    ],
    "invalid_after_short_gap_reversed_history_tail": [
        1495, 1488, 1482, 1476, 1469, 1463, 1457, 1451, 1444, 1438, 1432, 1426
    ],
    "autocorrelation_sine_period_12_bits": [
        "0x3f800000", "0x3f800000", "0x42fa0000", "0x42fabdf3", "0x42fabdf3"
    ],
    "autocorrelation_sine_period_20_bits": [
        "0x3f800000", "0x3f800000", "0x42960000", "0x4295ffcf", "0x4295ffcf"
    ],
    "autocorrelation_sine_period_35_bits": [
        "0x3f800000", "0x3f800000", "0x00000000", "0x00000000", "0x00000000"
    ],
}

EXPECTED_FLOAT32 = {
    0x00060968: 25.0,
    0x00056CD0: 5.0,
    0x00056CD4: 0.7,
    0x00056CD8: 0.0,
    0x00061260: 0.0,
    0x00061264: 60.0,
    0x00093E0C: 200.0,
    0x00093E10: 180.0,
    0x0009424C: 80.0,
    0x000575B8: 70.0,
    0x000575D0: 0.3,
    0x000575D4: 60.0,
    0x000763C8: 0.6,
    0x000763CC: 0.7,
    0x00058200: 80.0,
    0x00058204: 10.0,
    0x00058208: 15.0,
    0x00058214: 6.0,
    0x00067BB8: 80.0,
}

EXPECTED_FLOAT64 = {
    0x00068C74: 12.5,
    0x00068C7C: 60.0,
    0x00068C84: 115.0,
    0x00056CDC: 0.7,
    0x00056CE4: 0.5,
    0x00056CEC: 1.0,
    0x00057400: 6.25,
    0x00057408: 0.8,
    0x00057410: 20.0,
    0x000575C0: 0.25,
    0x000575C8: 0.75,
    0x000763A4: 0.9,
    0x000763AC: 1.1,
    0x000763B4: 0.25,
    0x000763BC: 0.75,
    0x000763D0: 2.5,
    0x00058058: 10.0,
    0x000581F8: 10.0,
    0x0005820C: 15.0,
}

EXPECTED_INT16 = {
    0x000710FC: -5000,
}

EXPECTED_INT32 = {
    0x00058460: -500,
    0x00056BA4: -32000,
}

EXPECTED_UINT32 = {
    0x000584A8: 0,
    0x00056B94: 0x000BD27C,
    0x00056978: 0x000BD26C,
    0x0008F498: 0x000BD2BC,
    0x00058050: 0xBD0FFFFF,
    0x00058054: 0x006BFFFF,
    0x000581E8: 0xBDB7FFFF,
    0x000581EC: 0x00C3FFFF,
    0x000581F0: 0xBDDFFFFF,
    0x000581F4: 0x00EBFFFF,
}

EXPECTED_INT32_SEQUENCES = {
    0x000BD294: [
        1_000, -3_722, 5_276, -3_374, 822,
        434, 0, -869, 0, 434,
        1_000, -2_595, 2_746, -1_459, 347,
        9_131, 0, -18_262, 0, 9_131,
    ],
}

EXPECTED_FLOAT32_BITS = {
    0x000BD27C: 0xBA8E0D9F,
    0x000BD280: 0x3C5D639E,
    0x000BD284: 0xBA815EE5,
    0x000BD288: 0xBCA9FB3C,
    0x000BD28C: 0xBC0BEFEE,
    0x000BD290: 0x3C2C7C80,
    0x00056B98: 0x3F8F797D,
    0x00056B9C: 0x447A0000,
    0x0005CB20: 0x3F0CCCCD,
    0x0005CB24: 0x3ECCCCCD,
    0x0005CB28: 0x3CF5C28F,
    0x0005CB2C: 0x3E2E147B,
    0x0005CB30: 0x3EB33333,
    0x0005CB34: 0x3E99999A,
    0x0005CB38: 0x3EE66666,
    0x0005CB3C: 0xBDCCCCCD,
    0x0005CB40: 0x358637BD,
    0x0005CB44: 0x44BB8000,
    0x0005CB48: 0x00000000,
    0x000748CC: 0x358637BD,
    0x000748D0: 0x00000000,
    0x000BD26C: 0xBE445123,
    0x000BD270: 0x3F697FE1,
    0x000BD274: 0xBC00B405,
    0x000BD278: 0x3F7237E0,
    0x0005697C: 0xBF4485EE,
    0x00056DBC: 0x00000000,
}


def flash_bytes(image: bytes, base: int, start: int, end: int) -> bytes:
    offset = mapped_offset(start, base, len(image))
    return image[offset:offset + (end - start)]


def unpack(image: bytes, base: int, address: int, kind: str) -> float:
    width = 4 if kind == "f" else 8
    return struct.unpack("<" + kind, flash_bytes(image, base, address, address + width))[0]


def output_coordinate(engine_offset: int, io_offset: int, width: int) -> bool:
    return any(
        field["engine_offset"] == engine_offset
        and field["io_offset"] == io_offset
        and field["width"] == width
        for field in FIELDS
    )


def summarize(image_path: Path, base: int) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != IMAGE_SHA256:
        raise ValueError(f"unexpected image SHA-256: {digest}")

    verified_ranges = []
    for (start, end), expected_digest in EXPECTED_RANGE_SHA256.items():
        actual_digest = hashlib.sha256(flash_bytes(image, base, start, end)).hexdigest()
        if actual_digest != expected_digest:
            raise ValueError(
                f"unexpected algorithm range 0x{start:08x}...0x{end:08x}: {actual_digest}"
            )
        verified_ranges.append({
            "start": f"0x{start:08x}",
            "end_exclusive": f"0x{end:08x}",
            "sha256": actual_digest,
        })

    branches: dict[str, list[str]] = {}
    for target, expected_callsites in EXPECTED_DIRECT_BRANCHES.items():
        actual = [address for address, _ in direct_thumb_branches_to(image, base, target)]
        if actual != expected_callsites:
            raise ValueError(
                f"unexpected branches to 0x{target:08x}: {actual} != {expected_callsites}"
            )
        branches[f"0x{target:08x}"] = [f"0x{item:08x}" for item in actual]

    constants: dict[str, Any] = {}
    for address, expected in EXPECTED_FLOAT32.items():
        actual = unpack(image, base, address, "f")
        if not math.isclose(actual, expected, rel_tol=0, abs_tol=1e-6):
            raise ValueError(f"unexpected Float32 at 0x{address:08x}: {actual}")
        constants[f"0x{address:08x}"] = actual
    for address, expected in EXPECTED_FLOAT64.items():
        actual = unpack(image, base, address, "d")
        if not math.isclose(actual, expected, rel_tol=0, abs_tol=1e-12):
            raise ValueError(f"unexpected Float64 at 0x{address:08x}: {actual}")
        constants[f"0x{address:08x}"] = actual
    for address, expected in EXPECTED_INT16.items():
        actual = struct.unpack("<h", flash_bytes(image, base, address, address + 2))[0]
        if actual != expected:
            raise ValueError(f"unexpected Int16 at 0x{address:08x}: {actual}")
        constants[f"0x{address:08x}"] = actual
    for address, expected in EXPECTED_INT32.items():
        actual = struct.unpack("<i", flash_bytes(image, base, address, address + 4))[0]
        if actual != expected:
            raise ValueError(f"unexpected Int32 at 0x{address:08x}: {actual}")
        constants[f"0x{address:08x}"] = actual
    for address, expected in EXPECTED_UINT32.items():
        actual = struct.unpack("<I", flash_bytes(image, base, address, address + 4))[0]
        if actual != expected:
            raise ValueError(f"unexpected UInt32 at 0x{address:08x}: {actual}")
        constants[f"0x{address:08x}"] = actual
    for address, expected in EXPECTED_FLOAT32_BITS.items():
        actual = struct.unpack("<I", flash_bytes(image, base, address, address + 4))[0]
        if actual != expected:
            raise ValueError(f"unexpected Float32 bits at 0x{address:08x}: 0x{actual:08x}")
        constants[f"0x{address:08x}"] = struct.unpack("<f", struct.pack("<I", actual))[0]
    for address, expected in EXPECTED_INT32_SEQUENCES.items():
        width = len(expected) * 4
        actual = list(struct.unpack(
            "<" + "i" * len(expected),
            flash_bytes(image, base, address, address + width),
        ))
        if actual != expected:
            raise ValueError(f"unexpected Int32 sequence at 0x{address:08x}: {actual}")
        constants[f"0x{address:08x}"] = actual

    expected_outputs = [(0x184, 0xA0, 4), (0x188, 0xA4, 4), (0x219, 0x33, 1), (0x21A, 0x54, 1)]
    if not all(output_coordinate(*coordinate) for coordinate in expected_outputs):
        raise ValueError("algorithm-domain fields no longer match the complete output ABI")

    periodicity_grid_hz = EXPECTED_FLOAT64[0x00068C74]
    seconds_per_minute = EXPECTED_FLOAT64[0x00068C7C]
    rate_numerator = periodicity_grid_hz * seconds_per_minute
    if rate_numerator != 750.0:
        raise ValueError(f"unexpected periodic-rate numerator: {rate_numerator}")

    return {
        "image": str(image_path),
        "image_sha256": digest,
        "load_base": f"0x{base:08x}",
        "ppg_respiratory_rate": {
            "output": {
                "rate_engine_offset": "0x184",
                "rate_io_offset": "0xa0",
                "confidence_engine_offset": "0x188",
                "confidence_io_offset": "0xa4",
            },
            "source_resampled_values_per_update": 25,
            "source_window_values": 250,
            "nominal_update_seconds": 1,
            "periodicity_grid_hz": periodicity_grid_hz,
            "rate_formula": "12.5 * 60 / periodic_sample_spacing",
            "rate_formula_numerator": rate_numerator,
            "accepted_breaths_per_minute": {"minimum": 7.0, "maximum": 25.0},
            "invalid_rate_sentinel": -1.0,
            "warmup_updates": 10,
            "confidence_formula": "1 - 0.5 * (dispersion_0 / 5 + dispersion_1 / 0.7)",
            "confidence_algorithm_range": {"minimum": 0.0, "maximum": 1.0},
            "algorithm_domain_proven": True,
            "stock_public_label_found": False,
            "stock_host_reader_found": False,
            "clinically_validated": False,
        },
        "motion": {
            "output": {
                "smoothed_state_engine_offset": "0x219",
                "smoothed_state_io_offset": "0x33",
                "step_cadence_engine_offset": "0x21a",
                "step_cadence_io_offset": "0x54",
            },
            "input_accelerometer_values_per_axis_per_update": 25,
            "locomotion_window": {
                "initializer": "0x000710d4",
                "preprocessor": "0x0005ed14",
                "summary_function": "0x0004834a",
                "missing_interval_function": "0x000484fc",
                "base_feature_function": "0x00067e4c",
                "state_bytes": 622,
                "axis_count": 3,
                "samples_per_axis_per_update": 25,
                "summary_slots": 8,
                "magnitude_history_samples": 200,
                "maximum_recoverable_elapsed_seconds": 8,
                "invalid_when_zero_magnitude_mean_slots_at_least": 5,
                "summary_arrays": 13,
                "missing_interval_cleared_summary_arrays": 9,
                "missing_interval_retained_absolute_difference_arrays": 4,
                "missing_interval_mirrors_previous_25_magnitudes_in_reverse": True,
                "delayed_first_sample_backfills_prior_7_magnitude_blocks": True,
                "base_features": [
                    "mean magnitude standard deviation",
                    "mean x standard deviation",
                    "mean magnitude",
                    "mean z",
                ],
                "production_thumb_fixtures": PRODUCTION_THUMB_LOCOMOTION_FIXTURES,
                "simple_predicates": {
                    "feature_record_offsets": [56, 57, 58, 59, 60],
                    "accepted_raw": 1,
                    "rejected_raw": 255,
                    "moderate_magnitude_range_open": [130, 20000],
                    "high_magnitude_range_open": [1900, 20000],
                    "last_five_minimum_matches": 3,
                    "magnitude_range_and_axis_deviation_thresholds": [200, 180],
                    "dual_axis_deviation_threshold": 400,
                    "linear_model_summary_updates": 3,
                    "linear_model_coefficient_bits": [
                        "0xba8e0d9f", "0x3c5d639e", "0xba815ee5",
                        "0xbca9fb3c", "0xbc0befee", "0x3c2c7c80",
                    ],
                    "linear_model_bias_bits": "0x3f8f797d",
                    "linear_model_scale": 1000,
                    "linear_model_clamp": [-32000, 32000],
                    "linear_model_score_history": 5,
                    "production_fixture_scores": [1401, 1411],
                },
                "autocorrelation": {
                    "source_history_slice": [75, 175],
                    "samples": 100,
                    "correlation_lags": 100,
                    "strict_peak_limit": 10,
                    "candidate_peak_limit": 11,
                    "candidate_lag_upper_exclusive": 51,
                    "third_peak_rate_numerator": 4500,
                    "interpolated_rate_numerator": 1500,
                    "parabolic_interpolation": True,
                    "turning_shape_descriptor": True,
                    "feature_record_float_indexes": [8, 10, 11, 12, 13],
                    "shape_predicate_record_offset": 61,
                    "production_fixture_periods": [12, 15, 20, 25, 30, 35],
                    "production_fixture_bit_exact": True,
                },
                "crossing_estimator": {
                    "source_history_samples": 200,
                    "baseline_summary_slots": 8,
                    "mode_1_centered_windows": [20, 10],
                    "mode_2_centered_windows": [12, 6],
                    "mode_1_filter": {
                        "denominator": [1000, -3722, 5276, -3374, 822],
                        "numerator": [434, 0, -869, 0, 434],
                    },
                    "mode_2_filter": {
                        "denominator": [1000, -2595, 2746, -1459, 347],
                        "numerator": [9131, 0, -18262, 0, 9131],
                    },
                    "mode_1_interval_range": [20, 50],
                    "mode_2_interval_range": [6.25, 25],
                    "mode_1_adaptive_short_interval_maximum": 16,
                    "mode_1_adaptive_amplitude_ratio": 0.6,
                    "mode_1_adaptive_interval_ratio": 0.7,
                    "mode_1_adaptive_second_difference_maximum": 2,
                    "mode_1_adaptive_reference_range": [0.9, 1.1],
                    "mode_1_adaptive_reference_weights": [0.25, 0.75],
                    "mode_1_adaptive_pruning_ratio": 0.7,
                    "quartiles": [0.25, 0.75],
                    "maximum_quartile_dispersion": 0.3,
                    "wrapper_rate_range_inclusive": [60, 240],
                    "feature_record_float_indexes": [4, 5],
                    "production_fixture_integer_period_range_inclusive": [8, 55],
                    "production_fixture_bit_exact": True,
                },
                "periodicity_features_implemented": True,
                "crossing_features_implemented": True,
                "final_motion_classifier": {
                    "initializer": "0x00071188",
                    "classifier": "0x0005f4b6",
                    "raw_state": "0x00093dcc",
                    "state_1_cadence_estimator": "0x00058060",
                    "state_2_cadence_estimator": "0x00057f8c",
                    "finalizer": "0x0009413c",
                    "history_smoother": "0x00067a40",
                    "state_bytes": 17,
                    "state_layout": {
                        "raw_state_history": [0, 5],
                        "cadence_history": [5, 10],
                        "preliminary_cadence_history": [10, 15],
                        "state_1_enable_offset": 15,
                        "state_2_enable_offset": 16,
                    },
                    "history_samples": 5,
                    "insufficient_state_sentinel": 254,
                    "rejected_state_sentinel": 255,
                    "reset_elapsed_seconds": 6,
                    "state_1_estimator_open_ranges": [[50, 140], [40, 140], [50, 140]],
                    "state_2_estimator_open_range": [120, 220],
                    "adjacent_consensus_difference_strictly_below": 10,
                    "state_1_final_cadence_inclusive": [51, 149],
                    "state_2_final_cadence_inclusive": [121, 219],
                    "state_2_high_candidate_threshold": 140,
                    "history_bucket_widths": {"state_2": 50, "other": 35, "high_state_2": 80},
                    "steady_state_1_fixture_outputs": [[1, 255, 0], [1, 255, 0], [1, 1, 100]],
                    "steady_state_2_fixture_outputs": [[2, 255, 0], [2, 255, 0], [2, 2, 150]],
                    "production_thumb_bit_exact": True,
                },
                "state_and_cadence_classifier_implemented": True,
            },
            "state_1_step_cadence_per_minute": {"minimum": 51, "maximum": 149},
            "state_2_step_cadence_per_minute": {"minimum": 121, "maximum": 219},
            "step_accumulator": {
                "initializer": "0x00071d9e",
                "function": "0x00061198",
                "transition_history_function": "0x00048960",
                "state_bytes": 28,
                "state_layout": {
                    "pending_float32_offset": 4,
                    "consecutive_nonzero_uint32_offset": 8,
                    "consecutive_zero_uint32_offset": 12,
                    "emission_threshold_uint32_offset": 16,
                    "cadence_history_uint8_offset": 20,
                    "cadence_history_count": 5,
                },
                "initial_emission_threshold_updates": 5,
                "candidate_formula": (
                    "(cadence + 1) / 60 * (compensated_zero_updates + 1) "
                    "* (elapsed_seconds if elapsed_seconds < 4 else 1)"
                ),
                "maximum_compensated_zero_updates": 2,
                "elapsed_multiplier_cutoff_seconds_exclusive": 4,
                "zero_cadence_clears_pending_and_acceptance_run": True,
                "after_threshold_emits_each_positive_update": True,
                "production_thumb_float32_fixtures": PRODUCTION_THUMB_STEP_FIXTURES,
            },
            "captured_raw_to_steps_pipeline": {
                "orchestrator": "0x0005ff94",
                "production_callsites_in_order": [
                    {"stage": "locomotion_window", "callsite": "0x00060026"},
                    {"stage": "final_motion_classifier", "callsite": "0x0006007c"},
                    {"stage": "step_accumulator", "callsite": "0x0006053c"},
                ],
                "common_accelerometer_adapter": "0x00060990",
                "classifier_result_cadence_byte_offset": 2,
                "same_elapsed_value_forwarded_to_all_three_stages": True,
                "phone_side_composition_implemented": True,
                "starts_or_configures_accelerometer": False,
                "reads_live_sram": False,
                "writes_health_store": False,
            },
            "unit_steps_per_minute_proven_by_stock_step_accumulator": True,
            "state_1_and_2_vendor_labels_found": False,
            "state_1_interpretation": "lower-cadence locomotion candidate",
            "state_2_interpretation": "higher-cadence locomotion candidate",
            "walking_running_labels_are_inference_only": True,
            "stock_host_reader_found": False,
            "derived_cumulative_steps_are_stock_consumed": True,
        },
        "constants": constants,
        "verified_ranges": verified_ranges,
        "direct_branches": branches,
        "safety": {
            "static_read_only": True,
            "offline_snapshot_requires_health_consent": True,
            "live_sram_reader_exposed": False,
            "vendor_engine_execution_exposed": False,
            "medical_claim_exposed": False,
            "raw_values_preserved": True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--base", type=lambda value: int(value, 0), default=DEFAULT_BASE)
    args = parser.parse_args()
    print(json.dumps(summarize(args.image, args.base), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
