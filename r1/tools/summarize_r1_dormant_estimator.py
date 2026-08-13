#!/usr/bin/env python3
"""Validate the stock-disabled 828-byte R1 multivariate estimator stage.

The parser is static and version-pinned. It validates the complete wrapper/scheduler composition,
initializer, per-iteration core and HR validity/carry gate, both selected-speed filters,
output-status helper, copied low byte and stock-unwritten activation state. It never executes the
engine, reads live SRAM, or enables the stage.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from summarize_r1_adc_registry import DEFAULT_BASE, mapped_offset
from summarize_r1_gomore_call_graph import direct_thumb_branches_to
from summarize_r1_gomore_input_abi import IMAGE_SHA256
from summarize_r1_gomore_output_abi import FIELDS as OUTPUT_FIELDS


EXPECTED_RANGE_SHA256 = {
    (0x0005FEB8, 0x0005FF90):
        "b410e5328af75c7a9c643b6dea01f6ff4b39d6f61ffa3b8f84eb37037e3143d7",
    (0x000715F8, 0x00071610):
        "d06d66726a39ec72436360c5cb6369c7debffb7d4d96d4953e984d6e75b4e5f3",
    (0x00096E0C, 0x00096E70):
        "5765263eb6429fea97419299f2d56b3cf6b00ab76f78def9bf9ab05c1e00c1a4",
    (0x000721B4, 0x000722E4):
        "0a740d3ca5ee6e62fd531f6f2692ede67a3913f1b709287dd24ac28fdb18da3c",
    (0x00069F80, 0x00069FA4):
        "ed379d4a20f4d255e433e9350cd268653f9895a1dd8645dd721160ca683e3c66",
    (0x0005FF94, 0x000605DA):
        "316edbabcbe75e09edbfc16176e77aa0e6938e21ba63199015b0f1f47ee993c1",
    (0x00071714, 0x000717A2):
        "3112c51e53dd2e756960eb870445b953280183300cc7b70a3c5ae25fc74940af",
    (0x00059D9C, 0x00059E5C):
        "16660063394cee6ff6305311031dea38deae059964751c1eb6d27b5336e705da",
    (0x000908E0, 0x00090A40):
        "3de28d7bbb0e6f3a7a11931a2bf786d48069109f1243fa8f81ddbd441c919851",
    (0x00090A50, 0x00090AC8):
        "fe41452ab182374026d860f1d8f3ac5a150a0c422b60c7b61341a301324d0676",
    (0x00070498, 0x0007061E):
        "430c9cc0c2c47776276c2094f2f32a13da47710dba03c0e7df4710bf69c4e7ca",
    (0x0005D2EC, 0x0005D30E):
        "68d9d676223b35ae20eddcdfb93a2f8841606a19493a68f343d1d8ffc5545e5b",
    (0x00094270, 0x000942FE):
        "c08092c6a3077cb782a1dbf46d0f55f39d3df42c64fc22b35cbec030a5ffce7e",
    (0x00096634, 0x0009678E):
        "28ba26ba1f775bc7d4df845e5ddd9d6b3b3df1ad1628178a60e09191444b787c",
    (0x00094698, 0x000947DE):
        "4d12ceeda3b48ad7ec259f6978c87f6da606d36c284d2fc15fb5d97dd63fd715",
    (0x0004C6DC, 0x0004C814):
        "59e8766752753738113c1ed8cf4756f411ba34dab40d78bc29ecd6035971efc8",
    (0x00029382, 0x0002938A):
        "1da11909d6e5e80fc931a82297514c5b2f90c4fe39fadea7d08ccf6a652a694d",
    (0x0002938A, 0x00029392):
        "c1131de7a77f7d6ff59cca21fd2efd265e6f5b826f461292801c3572133a52f7",
    (0x0006825C, 0x00068344):
        "346de4b3b4a920d11fd3aaf7dd930854b7ce8eb02fc26568f9016c9febe1cf84",
    (0x00067488, 0x0006754C):
        "b351faf207bd93a95557dd695eb7e034dfb92bb02be730ae6e118d8372602991",
    (0x000676E0, 0x00067724):
        "b594a51f0f67e97ecebcca8fdcc7df9ca260a9700f97b70e7a91de4203cb7437",
    (0x00080F88, 0x00080FEC):
        "4b10b2661b3645933d97d708291bac4c1226df76a38b97b11f7bdab4eba7a20c",
    (0x00090C54, 0x00090DA4):
        "8b9054226326f0e60650df2a2f544ec538f7a1f240c71bf0e1d716be0a95ccc4",
    (0x000888A0, 0x00088A94):
        "84c9790de07929079ed693edf245a6428c2ec328dc45e08427c79cfc89060a44",
    (0x00069D20, 0x00069D68):
        "f30d996c3085cd2a99cdb4f3342fe133db4a9e7fcf48acf605bc63c031a53af6",
    (0x00067470, 0x00067484):
        "1ae6f427fd9c90603c98de3c16dd40a391c6e8196cce3d4c122f1309eb506cdc",
    (0x00069D80, 0x00069DC0):
        "e5f8be998cf9e0bb90a6e96687ae040948b7471eb5ced03b577899f69a30a398",
    (0x000695A8, 0x00069634):
        "2da685171c6c2acb8121d3b88e5c97d12dfa00af65957548edd8f4b968abfc89",
    (0x000568AC, 0x000568E0):
        "945be3410119498edd07302b1b489c9269957bd3b188916d8978320057524206",
    (0x0006818C, 0x00068234):
        "c8ea7d473ec7a07c20ab38d2f7624729919070de7f6da265e39d38d7dfc1b19a",
    (0x00068420, 0x000684B0):
        "e759c46b15d56556c3f80ef076d84b7c17e93828c331a0270323646d60c3e3e6",
    (0x0006808C, 0x0006818C):
        "a304aa2d7fc333aa38dc641192dddb2b8cb1d0f11995831855b1e76e23e75d0c",
    (0x000675DC, 0x000676D6):
        "51df2c19304b07c0c815380fa5cc29920e5fbe14109238ce6afe72607daffa9a",
    (0x00058C7A, 0x00058CE8):
        "a44310c6cd542b08f8e504a6eca0405498e64f7abe54067ba5bbae4072b1c4ca",
    (0x00058C40, 0x00058C7A):
        "1f2f92330d87539c153143538c6dd6ea1ecf9ebb7304cede7ab92fa7359c2d0d",
    (0x00056C2A, 0x00056C54):
        "251c8849806e66cd49d7c038553e58496236e818ecb6616c4006c9f1fc7f4694",
    (0x00077E48, 0x00077E8E):
        "220a29fe3345a0ce394350707dfeeb53ca67d5df0cb531ee003ef003dfeb85c8",
    (0x000908AC, 0x000908DA):
        "4d1f6035a7168383985cabaccc6b1e5717db7e7749a01f82c969bf6a766016e6",
    (0x00090EFC, 0x00090F3E):
        "a20000237d7fa69544fa8978f55d79e752ecd1eb77ec8fb3ac718bde7d170287",
    (0x00068D18, 0x00068DC8):
        "48146d9a72a03dcfb167f6763da2f1ded3d2e9387eb198c3e29ce2147723d438",
    (0x00069DC8, 0x00069E7C):
        "e17f5cfb3f9354f3e84dc134c78fb224b31b5cee41b9dec31d95a9a9cbe961bd",
    (0x0008141C, 0x00081560):
        "9e59a2d2cba1b9b03171b2c7a58394d5b41e6035c05ff573ca7efa2523a175e3",
    (0x000384C8, 0x0003871A):
        "552fa87ab744ebb42822f89031b2ed0c358eea0c45175db07b548de3aa648d41",
    (0x00038774, 0x0003889C):
        "d93b4bec3b0c47f2cf4027e69e268174ae2c6431a5fa4de38743ae9f20ce8c4d",
    (0x00038A5C, 0x00038B74):
        "d22762c8ebb47a09562d8ac067ad23f406d5f494e44ce9a0203a487cb00bfb23",
    (0x0003AE04, 0x0003AF5C):
        "37bcdfac599bf21a810d8bd6d15af3beff67b74ad526acfdc958a47cfb086ac6",
}

EXPECTED_DIRECT_BRANCHES = {
    0x0005FEB8: [0x000602E2, 0x000602FC],
    0x000715F8: [0x00071AA4],
    0x00096E0C: [0x0005FF6E],
    0x000721B4: [0x00096E50],
    0x00069F80: [0x0005FF76],
    0x000908E0: [0x0007226C],
    0x00090A50: [0x00072278],
    0x00070498: [0x00094292],
    0x0005D2EC: [0x00070554, 0x00070560],
    0x00094270: [0x000722C4],
    0x00096634: [0x000942F6],
    0x00094698: [0x00096680, 0x00096742],
    0x0004C6DC: [0x0007221C],
    0x00029382: [0x0007224C],
    0x0002938A: [0x00072230],
    0x0006825C: [0x00029386],
    0x00067488: [0x0002938E],
    0x000676E0: [0x000674B2, 0x00068288, 0x0008896E],
    0x00080F88: [
        0x00088A46, 0x00088A5C,
        0x00090D42, 0x00090D58, 0x00090D78, 0x00090D8E,
    ],
    0x00090C54: [0x0008149A, 0x0008897C, 0x00088990],
    0x000888A0: [0x000674EC, 0x00068314],
    0x00069D20: [0x00069D92, 0x00088914],
    0x00067470: [0x000889FE],
    0x00069D80: [0x00088A14],
    0x000695A8: [0x00088A2A],
    0x000568AC: [0x00069DF8, 0x00081448],
    0x0006818C: [0x00068DC4, 0x00069E48],
    0x00068420: [0x00069E52, 0x00081470],
    0x0006808C: [0x00068DAE, 0x00069E3C],
    0x000675DC: [0x00068180],
    0x00058C7A: [0x00067636, 0x00067640],
    0x00058C40: [
        0x00067662, 0x0006766C, 0x0006767E, 0x000676A0, 0x000676AA,
    ],
    0x00056C2A: [0x0006761E, 0x00067650, 0x0006768E, 0x000676BA],
    0x00077E48: [0x00067600, 0x0006760E],
    0x000908AC: [0x000676CA],
    0x00090EFC: [0x00068144],
    0x00068D18: [0x00081466, 0x000814B4],
    0x00069DC8: [0x00081486],
    0x0008141C: [0x000674F8, 0x00068320],
    0x000384C8: [0x00058C8E],
    0x00038774: [0x000682AC, 0x000888E2],
    0x00038A5C: [
        0x00058CC6, 0x000682C0, 0x000682F4,
        0x000711E4, 0x00071200, 0x00071234, 0x000712A8,
        0x000717D4, 0x00071816, 0x0007194A,
        0x000888EA, 0x00088902,
    ],
    0x0003AE04: [
        0x00058CD6, 0x00068300,
        0x0007121C, 0x0007124C, 0x000712B4,
        0x000717E0, 0x00071822, 0x00071956,
    ],
}


def flash_bytes(image: bytes, base: int, start: int, end: int) -> bytes:
    offset = mapped_offset(start, base, len(image))
    return image[offset:offset + (end - start)]


def summarize(image_path: Path, base: int) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != IMAGE_SHA256:
        raise ValueError(f"unexpected image SHA-256: {digest}")

    verified_ranges = []
    for (start, end), expected in EXPECTED_RANGE_SHA256.items():
        actual = hashlib.sha256(flash_bytes(image, base, start, end)).hexdigest()
        if actual != expected:
            raise ValueError(
                f"unexpected dormant-estimator range 0x{start:08x}...0x{end:08x}: {actual}"
            )
        verified_ranges.append({
            "start": f"0x{start:08x}",
            "end_exclusive": f"0x{end:08x}",
            "sha256": actual,
        })

    branches: dict[str, list[str]] = {}
    for target, expected in EXPECTED_DIRECT_BRANCHES.items():
        actual = [address for address, _ in direct_thumb_branches_to(image, base, target)]
        if actual != expected:
            raise ValueError(
                f"unexpected branches to 0x{target:08x}: {actual} != {expected}"
            )
        branches[f"0x{target:08x}"] = [f"0x{address:08x}" for address in actual]

    time_error = struct.unpack("<i", flash_bytes(image, base, 0x00096E70, 0x00096E74))[0]
    fatal_output_error = struct.unpack(
        "<i", flash_bytes(image, base, 0x00069FA4, 0x00069FA8)
    )[0]
    if time_error != -1016 or fatal_output_error != -1008:
        raise ValueError(
            f"unexpected estimator errors: {time_error}, {fatal_output_error}"
        )
    initializer_literals = struct.unpack(
        "<ff", flash_bytes(image, base, 0x000717A4, 0x000717AC)
    )
    if initializer_literals != (-999999.0, -999.0):
        raise ValueError(f"unexpected engine sentinel literals: {initializer_literals}")
    speed_filter_literals = struct.unpack(
        "<ffff", flash_bytes(image, base, 0x00090A40, 0x00090A50)
    )
    expected_speed_filter_bits = (0x41DD851F, 0x4039999A, 0, 0x3EEAA64C)
    actual_speed_filter_bits = tuple(
        struct.unpack("<I", struct.pack("<f", value))[0]
        for value in speed_filter_literals
    )
    if actual_speed_filter_bits != expected_speed_filter_bits:
        raise ValueError(
            f"unexpected dormant speed-filter literals: {actual_speed_filter_bits}"
        )
    heart_rate_filter_literals = struct.unpack(
        "<III", flash_bytes(image, base, 0x00070620, 0x0007062C)
    )
    if heart_rate_filter_literals != (0, 0x40C00000, 0xC0E00000):
        raise ValueError(
            f"unexpected dormant HR-filter literals: {heart_rate_filter_literals}"
        )
    ratio_accumulator_literals = struct.unpack(
        "<IIII", flash_bytes(image, base, 0x00096790, 0x000967A0)
    )
    if ratio_accumulator_literals != (
        0x3FA8F5C3, 0x41F00000, 0, 0x3F9C28F6
    ):
        raise ValueError(
            f"unexpected dormant ratio-accumulator literals: {ratio_accumulator_literals}"
        )
    speed_smoother_literals = struct.unpack(
        "<II", flash_bytes(image, base, 0x0004C814, 0x0004C81C)
    )
    if speed_smoother_literals != (0x3EB33333, 0x3F266666):
        raise ValueError(
            f"unexpected dormant speed-smoother literals: {speed_smoother_literals}"
        )
    per_iteration_literals = struct.unpack(
        "<Ii", flash_bytes(image, base, 0x000722E4, 0x000722EC)
    )
    if per_iteration_literals != (0, -1016):
        raise ValueError(
            f"unexpected dormant per-iteration literals: {per_iteration_literals}"
        )
    mode_zero_literals = struct.unpack(
        "<IIII", flash_bytes(image, base, 0x00068344, 0x00068354)
    )
    if mode_zero_literals != (0x43250000, 0x40666666, 0, 0x42C80000):
        raise ValueError(
            f"unexpected dormant mode-zero route literals: {mode_zero_literals}"
        )
    mode_one_literals = struct.unpack(
        "<III", flash_bytes(image, base, 0x0006754C, 0x00067558)
    )
    if mode_one_literals != (0x43250000, 0x40666666, 0):
        raise ValueError(
            f"unexpected dormant mode-one route literals: {mode_one_literals}"
        )
    decimal_rounder_literals = struct.unpack(
        "<II", flash_bytes(image, base, 0x00080FEC, 0x00080FF4)
    )
    if decimal_rounder_literals != (0, 0x3ECCCCCD):
        raise ValueError(
            f"unexpected dormant decimal-rounder literals: {decimal_rounder_literals}"
        )
    speed_baseline_literals = struct.unpack(
        "<12I", flash_bytes(image, base, 0x00090DA4, 0x00090DD4)
    )
    if speed_baseline_literals != (
        0, 0x3E1704FF, 0x3FA00000, 0x3CBD230C,
        0xBAAA3573, 0x3AFD428B, 0x3E91BAD6, 0x3FE6B205,
        0x42700000, 0x411CF5C3, 0x3D1A2C67, 0x3F0DD2F2,
    ):
        raise ValueError(
            f"unexpected dormant speed-baseline literals: {speed_baseline_literals}"
        )
    speed_reducer_literals = struct.unpack(
        "<6I", flash_bytes(image, base, 0x00088A94, 0x00088AAC)
    )
    if speed_reducer_literals != (
        0, 0x3FA147AE, 0x43250000, 0x411CCCCD, 0x3DCCCCCD, 0x3F0DD2F2
    ):
        raise ValueError(
            f"unexpected dormant speed-reducer literals: {speed_reducer_literals}"
        )
    speed_calibration_literals = struct.unpack(
        "<6I", flash_bytes(image, base, 0x00069D68, 0x00069D80)
    )
    if speed_calibration_literals != (
        0x3FA00000, 0x3CBD230C, 0xBAAA3573,
        0x3AFD428B, 0x3E91BAD6, 0x3FE6B205,
    ):
        raise ValueError(
            f"unexpected dormant speed-calibration literals: {speed_calibration_literals}"
        )
    speed_cubic_literals = struct.unpack(
        "<I", flash_bytes(image, base, 0x00067484, 0x00067488)
    )
    if speed_cubic_literals != (0x3E1704FF,):
        raise ValueError(f"unexpected dormant speed-cubic literal: {speed_cubic_literals}")
    speed_linear_literals = struct.unpack(
        "<2I", flash_bytes(image, base, 0x00069DC0, 0x00069DC8)
    )
    if speed_linear_literals != (0x411CF5C3, 0x42700000):
        raise ValueError(f"unexpected dormant speed-linear literals: {speed_linear_literals}")
    speed_change_literals = struct.unpack(
        "<4I", flash_bytes(image, base, 0x00069634, 0x00069644)
    )
    if speed_change_literals != (0x40600000, 0xBE924745, 0x3C9BA5E3, 0x42700000):
        raise ValueError(f"unexpected dormant speed-change literals: {speed_change_literals}")
    dimensionless_literals = struct.unpack(
        "<4I", flash_bytes(image, base, 0x000568E0, 0x000568F0)
    )
    if dimensionless_literals != (0x3E16277C, 0x42C80000, 0x3E20FBA9, 0x42700000):
        raise ValueError(f"unexpected dormant dimensionless literals: {dimensionless_literals}")
    quadratic_literals = struct.unpack(
        "<I", flash_bytes(image, base, 0x00068234, 0x00068238)
    )
    if quadratic_literals != (0,):
        raise ValueError(f"unexpected dormant quadratic literal: {quadratic_literals}")
    root_selector_literals = struct.unpack(
        "<I", flash_bytes(image, base, 0x000684B0, 0x000684B4)
    )
    if root_selector_literals != (0,):
        raise ValueError(f"unexpected dormant root-selector literal: {root_selector_literals}")
    cubic_literals = struct.unpack(
        "<2I", flash_bytes(image, base, 0x000676D8, 0x000676E0)
    )
    if cubic_literals != (0x358637BD, 0x3EAAAAAB):
        raise ValueError(f"unexpected dormant cubic literals: {cubic_literals}")
    real_cube_root_literals = struct.unpack(
        "<2I", flash_bytes(image, base, 0x00077E90, 0x00077E98)
    )
    if real_cube_root_literals != (0x3EAAAAAB, 0):
        raise ValueError(
            f"unexpected dormant real-cube-root literals: {real_cube_root_literals}"
        )
    cubic_writer_literals = struct.unpack(
        "<I", flash_bytes(image, base, 0x000908DC, 0x000908E0)
    )
    if cubic_writer_literals != (0x3727C5AC,):
        raise ValueError(f"unexpected dormant cubic-writer literal: {cubic_writer_literals}")
    complex_sqrt_literals = struct.unpack(
        "<I", flash_bytes(image, base, 0x00090F40, 0x00090F44)
    )
    if complex_sqrt_literals != (0,):
        raise ValueError(f"unexpected dormant complex-sqrt literal: {complex_sqrt_literals}")
    root_builder_literals = struct.unpack(
        "<6I", flash_bytes(image, base, 0x00068DC8, 0x00068DE0)
    )
    if root_builder_literals != (
        0, 0x3A252696, 0x39B7CCB5,
        0x3D5385D9, 0x3E1704FF, 0x39770E14,
    ):
        raise ValueError(
            f"unexpected dormant root-builder literals: {root_builder_literals}"
        )
    alternate_root_literals = struct.unpack(
        "<6I", flash_bytes(image, base, 0x00069E7C, 0x00069E94)
    )
    if alternate_root_literals != (
        0, 0x3A252696, 0x3BF76450,
        0x3E1704FF, 0x3FA00000, 0x3F333333,
    ):
        raise ValueError(
            f"unexpected dormant alternate-root literals: {alternate_root_literals}"
        )
    speed_finalizer_literals = struct.unpack(
        "<3I", flash_bytes(image, base, 0x00081560, 0x0008156C)
    )
    if speed_finalizer_literals != (0, 0x3F0DD2F2, 0x3FA00000):
        raise ValueError(
            f"unexpected dormant speed-finalizer literals: {speed_finalizer_literals}"
        )
    atan2_literals = struct.unpack(
        "<22I", flash_bytes(image, base, 0x0003871C, 0x00038774)
    )
    if atan2_literals != (
        0xBFC90FDB, 0x3FC90FDB, 0x40490FDB, 0xC0490FDB,
        0xBFC90000, 0xB9FDAA22, 0x3FC90000, 0x39FDAA22,
        0x3EED6000, 0x37CE0AC3, 0,
        0xC0490000, 0xBA7DAA22, 0x40490000, 0x3A7DAA22,
        0xBD65AD2D, 0x3DD5B88F, 0xBE11B50F, 0x3E4CC861, 0xBEAAAAA8,
        0x4F800000, 0x2F800000,
    ):
        raise ValueError(f"unexpected dormant atan2 literals: {atan2_literals}")
    atan_literals = struct.unpack(
        "<14I", flash_bytes(image, base, 0x0003889C, 0x000388D4)
    )
    if atan_literals != (
        0, 0xBFC90000, 0xB9FDAA22, 0x3FC90000, 0x39FDAA22,
        0x3EED6000, 0x37CE0AC3,
        0xBD65AD2D, 0x3DD5B88F, 0xBE11B50F, 0x3E4CC861, 0xBEAAAAA8,
        0xBFC90FDB, 0x3FC90FDB,
    ):
        raise ValueError(f"unexpected dormant atan literals: {atan_literals}")
    cosine_literals = struct.unpack(
        "<15I", flash_bytes(image, base, 0x00038B74, 0x00038BB0)
    )
    if cosine_literals != (
        0x7E921FB6, 0x394C6D33, 0x3C0882DA, 0xBE2AAAA0,
        0x46490E49, 0x3F22F983, 0x4B000000,
        0x3FC90000, 0x39FDA000, 0x33A22000, 0x2C34611A,
        0xBAB23AB9, 0x3D2A9FCA, 0xBEFFFFDD, 0,
    ):
        raise ValueError(f"unexpected dormant cosine literals: {cosine_literals}")
    sine_literals = struct.unpack(
        "<14I", flash_bytes(image, base, 0x0003AF5C, 0x0003AF94)
    )
    if sine_literals != (
        0x7E921FB6, 0xBAB23AB9, 0x3D2A9FCA, 0xBEFFFFDD,
        0x46490E49, 0x3F22F983, 0x4B000000,
        0x3FC90000, 0x39FDA000, 0x33A22000, 0x2C34611A,
        0x394C6D33, 0x3C0882DA, 0xBE2AAAA0,
    ):
        raise ValueError(f"unexpected dormant sine literals: {sine_literals}")

    copied_status = [
        field for field in OUTPUT_FIELDS
        if field["engine_offset"] == 0x182 and field["io_offset"] == 0x81
    ]
    if copied_status != [{
        "engine_offset": 0x182,
        "io_offset": 0x81,
        "width": 1,
        "storage": "uint8",
        "semantic": "dormant_estimator_status_low_byte",
    }]:
        raise ValueError(f"unexpected copied estimator status definition: {copied_status}")

    return {
        "image": str(image_path),
        "image_sha256": digest,
        "load_base": f"0x{base:08x}",
        "stage": {
            "semantic_name_in_image": None,
            "wrapper": "0x0005feb8",
            "state_engine_offset": "0x0cb4",
            "state_bytes": 828,
            "initializer": "0x000715f8",
            "initializer_zeroes_state": True,
            "control_layout": {
                "scheduler_cursor_uint32": "0x048",
                "scheduled_iteration_count_uint32": "0x04c",
                "accumulated_elapsed_uint32": "0x328",
                "update_count_uint32": "0x32c",
                "mode_uint32": "0x330",
                "force_invalid_inputs_uint8": "0x334",
                "previous_state_pointer_uint32": "0x338",
            },
            "previous_state_source_byte_offset": 24,
            "stock_mode": 0,
            "stock_mode_writer_found": False,
            "force_invalid_writer_found": False,
            "mode_behavior": {
                "zero": "return 1 without changing state or output",
                "one": "run replay scheduler/core and output-status helper",
                "other_nonzero": "increment update count and return 0 without core/output helper",
            },
        },
        "inputs": {
            "current_time_engine_offset": "0x050",
            "selected_heart_rate_engine_offset": "0x104",
            "selected_speed_engine_offset": "0x0e4",
            "internal_config_engine_offsets": ["0x054", "0x058", "0x05c", "0x068"],
            "stock_internal_config_float32": [-999.0, -999.0, -999999.0, 0.0],
            "internal_config_is_user_profile": False,
            "internal_config_post_initializer_writer_found": False,
            "unresolved_auxiliary_engine_offsets": ["0x014", "0x018", "0x01c"],
            "stock_unresolved_auxiliary_float32": [-1.0, -1.0, -1.0],
            "unresolved_auxiliary_post_initializer_writer_found": False,
            "total_energy_engine_offset": "0x114",
            "force_invalid_substitution": {"heart_rate_int32": -1, "speed_float32": -1.0},
        },
        "scheduler": {
            "function": "0x00096e0c",
            "per_iteration_function": "0x000721b4",
            "initial_cursor": "0xffffffff",
            "ordinary_deltas": [0, 1],
            "replayed_delta_minimum": 2,
            "replayed_delta_maximum": 15,
            "replay_first_sample": "prior cursor plus one",
            "replay_last_sample": "accumulated elapsed",
            "replay_final_cursor": "accumulated elapsed plus one",
            "single_sample_final_cursor": "effective sample index",
            "per_iteration_return_is_ignored_for_loop_control": True,
            "per_iteration_mutated_heart_rate_is_reused": True,
            "per_iteration_mutated_primary_config_is_reused": True,
            "larger_discontinuity_status": time_error - 11,
        },
        "wrapper_composition": {
            "complete": True,
            "function": "0x0005feb8",
            "scheduler": "0x00096e0c",
            "per_iteration": "0x000721b4",
            "status_helper": "0x00069f80",
            "disabled_mode_returns_before_input_reads_or_state_changes": True,
            "first_nonzero_call_ignores_elapsed_argument": True,
            "later_nonzero_calls_add_elapsed_with_uint32_wrap": True,
            "heart_rate_conversion": {
                "instruction": "VCVT.S32.F32",
                "rounding": "toward zero",
                "nan": 0,
                "positive_overflow_or_infinity": "0x7fffffff",
                "negative_overflow_or_infinity": "0x80000000",
            },
            "force_invalid_substitution_after_conversion": {
                "heart_rate_int32": -1,
                "selected_speed_float32": -1.0,
            },
            "per_iteration_input_mapping": {
                "current_time": "engine+0x050",
                "sample_index": "scheduler effective time",
                "heart_rate": "converted selected HR, then caller-mutated",
                "selected_speed": "engine+0x0e4, or forced -1",
                "current_auxiliary": "engine+0x018",
                "copied_auxiliary_1": "engine+0x014",
                "copied_auxiliary_2": "engine+0x01c",
                "primary_config": "engine+0x05c, then caller-mutated",
                "alternate_config": "engine+0x068",
                "trailing_unused": "engine+0x114 total energy",
            },
            "active_mode_calls_status_helper_after_scheduler_error_or_success": True,
            "other_nonzero_modes_skip_scheduler_and_status_helper": True,
            "all_nonzero_modes_increment_update_count": True,
            "wrapper_ignores_scheduler_return": True,
            "output_prefix_is_retained_unless_fatal_state_is_nonzero": True,
        },
        "active_only_per_iteration_heart_rate_gate": {
            "stock_reachable": False,
            "function": "0x000721b4",
            "validation_latch_state_offset": "0x060",
            "status_int16_state_offset": "0x052",
            "selected_heart_rate_int32_state_offset": "0x01c",
            "previous_heart_rate_int32_state_offset": "0x020",
            "validation_index_maximum_exclusive": 30,
            "accepted_heart_rate_inclusive": [36, 249],
            "validation_error": time_error,
            "validation_runs_only_while_latch_is_zero": True,
            "valid_sample_sets_latch_to_one": True,
            "zero_carry_starts_at_index": 1,
            "zero_carry_requires_validation_to_have_passed_or_be_skipped": True,
            "index_zero_never_carries_previous": True,
            "index_thirty_and_later_skip_validation": True,
            "successful_downstream_completion_status": 0,
        },
        "active_only_per_iteration_composition": {
            "complete": True,
            "function": "0x000721b4",
            "heart_rate_wrapper": "0x00094270",
            "stock_reachable": False,
            "call_order": [
                "copy selected speed and three auxiliary words",
                "route/smoother/target",
                "flag-dependent speed gate 0x000908e0",
                "five-sample speed average 0x00090a50",
                "integer HR validation/carry",
                "HR filter 0x00070498 with raw fallback",
                "optional ratio accumulator 0x00096634",
                "copy selected HR/speed/auxiliary to previous slots",
                "clear status",
            ],
            "invalid_heart_rate_early_exit": {
                "raw_status": -1016,
                "route_and_speed_filter_mutations_are_retained": True,
                "heart_rate_filter_and_ratio_are_not_called": True,
                "previous_hr_speed_auxiliary_are_not_copied": True,
            },
            "fixed_filter_interval_milliseconds": 1000,
            "trailing_float_input_is_loaded_but_unused_by_wrapper": True,
            "route_flag_word_is_separate_from_dynamics_flag_word": True,
            "modeled_capture_state_bytes": 828,
        },
        "active_only_speed_filters": {
            "stock_reachable": False,
            "flag_dependent_gate_function": "0x000908e0",
            "five_sample_moving_average_function": "0x00090a50",
            "call_order": ["flag_dependent_gate", "five_sample_moving_average"],
            "shared_state_offset": "0x184",
            "shared_history_float32_count": 6,
            "moving_average_history_float32_count": 5,
            "flag_mask": "0x1444",
            "first_sample_rejected_at_or_above": 15.0,
            "first_sample_nan_is_preserved": True,
            "average_override_threshold_float32_bits": "0x41dd851f",
            "secondary_average_threshold": 15.0,
            "secondary_rise_threshold_float32_bits": "0x4039999a",
            "flagged_rise_intercept": 5.5,
            "flagged_previous_multiplier_float32_bits": "0x3eeaa64c",
            "history_is_reused_between_filters": True,
        },
        "active_only_speed_smoother": {
            "stock_reachable": False,
            "function": "0x0004c6dc",
            "only_callsite": "0x0007221c",
            "state_offset": "0x2dc",
            "state_bytes": 32,
            "produced_value_state_offset": "0x034",
            "input_config_offset": "0x008",
            "enable_byte_initial_value": 0,
            "enable_or_limit_writer_found": False,
            "accepted_interval_milliseconds": [700, 1300],
            "warmup_sample_count": 10,
            "warmup_operation": "prefix mean of raw-slew-limited inputs",
            "ema_input_weight_float32_bits": "0x3eb33333",
            "ema_previous_weight_float32_bits": "0x3f266666",
            "raw_slew_limits_state_offsets": ["0x010", "0x014"],
            "output_slew_limits_state_offsets": ["0x018", "0x01c"],
            "raw_slew_starts_after_two_prior_samples": True,
            "previous_raw_slot_keeps_unclamped_input": True,
            "stable_or_clamped_flag_semantics": {
                "one": "output was clamped or candidate exactly equaled prior output",
                "zero": "candidate changed without output clamp",
            },
            "statuses": {
                "success": "0xffffffff",
                "inactive": "0x1389",
                "invalid_interval": "0x138a",
                "invalid_configuration": "0x138b",
            },
            "caller_ignores_status": True,
            "unused_output_pointer_is_never_written": True,
            "stock_produced_value": 0,
        },
        "active_only_speed_dynamics_routes": {
            "stock_reachable": False,
            "dominant_mode_one_flag_mask": "0x1444",
            "primary_config_zero_flag": "0x0004",
            "mode_zero_flag": "0x0008",
            "route_priority": ["flags & 0x1444 -> mode one", "else flags & 8 -> mode zero", "bypass"],
            "primary_config_offset": "0x008",
            "alternate_config_offset": "0x00c",
            "mode_one_receives_smoother_output": True,
            "mode_zero_receives_alternate_config_directly": True,
            "shared_state_offset": "0x2fc",
            "shared_state_bytes": 44,
            "mode_zero": {
                "veneer": "0x00029382",
                "veneer_mode_argument": 0,
                "target": "0x0006825c",
                "scale_float32_bits": "0x40666666",
                "angle_divisor_float32_bits": "0x42c80000",
                "default_integer_constant_float32_bits": "0x43250000",
            },
            "mode_one": {
                "veneer": "0x0002938a",
                "veneer_mode_argument": 1,
                "target": "0x00067488",
                "scale_float32_bits": "0x40666666",
                "default_integer_constant_float32_bits": "0x43250000",
            },
            "initialized_byte_offset": "0x026",
            "state_is_zero_initialized": True,
            "flag_word_initial_value": "0x0000",
            "flag_word_writer_found": False,
            "semantic_name_in_image": None,
            "target_helper_graph_complete": True,
            "caller_composition_complete": True,
            "caller_composition": {
                "function": "0x000721b4",
                "smoother_interval_milliseconds": 1000,
                "smoother_status_is_ignored": True,
                "unwritten_smoother_output_uses_caller_initialized_zero": True,
                "mode_one_order": [
                    "optional primary config zero",
                    "smoother 0x0004c6dc",
                    "mode-one target 0x00067488",
                ],
                "mode_zero_order": ["alternate config", "mode-zero target 0x0006825c"],
                "bypass_preserves_selected_speed": True,
                "route_flag_word_is_separate_from_target_state_flag_word": True,
            },
            "target_execution": {
                "common_selected_speed_divisor_float32_bits": "0x40666666",
                "common_default_auxiliary_float32_bits": "0x43250000",
                "flagged_auxiliary_converter": "0x000676e0",
                "root_slots_cleared_on_every_call": ["0x018", "0x01c", "0x020"],
                "initialized_byte_is_set_to_one_only_when_zero": True,
                "mode_one": {
                    "first_input_role": "current value stored at state+0x00c",
                    "secondary_reducer_input": "current minus previous; zero on first call",
                    "primary_reducer_input": "selected_speed/3.6",
                },
                "mode_zero": {
                    "geometry_input": "first_input/100",
                    "geometry_angle": "atanf geometry input",
                    "primary_reducer_input": "selected_speed/3.6*cosf(angle)",
                    "secondary_reducer_input": "selected_speed/3.6*sinf(angle)",
                },
                "initial_history": {
                    "previous_transformed_state_offset": "0x008",
                    "previous_power_state_offset": "0x010",
                    "previous_power_formula": "powf(primary,2)*state1*0.5",
                },
                "common_pipeline": ["0x000888a0", "0x0008141c"],
                "final_scale_float32_bits": "0x40666666",
                "final_clamp": "ordered negative only; NaN is retained",
                "production_math": [
                    "atan2f@0x000384c8", "atanf@0x00038774",
                    "cosf@0x00038a5c", "sinf@0x0003ae04", "powf@0x0003a620",
                ],
            },
        },
        "active_only_flagged_threshold_converter": {
            "stock_reachable": False,
            "function": "0x000676e0",
            "required_dynamics_flag_mask": "0x0440",
            "state_first_parameter_offset": "0x000",
            "state_first_parameter_writer_found": False,
            "formula": "input / (state0 * (intercept + (abs(input) - 2.5) * slope) * 100) * 60",
            "absolute_offset": 2.5,
            "slope_float32_bits": "0x3e20fba9",
            "intercept_float32_bits": "0x3f0a2728",
            "denominator_scale_float32_bits": "0x42c80000",
            "numerator_scale_float32_bits": "0x42700000",
            "cap_float32_bits": "0x435c0000",
            "cap_comparison": "signed comparison of raw Float32 bits",
            "negative_results_are_not_numerically_lower-clamped": True,
        },
        "active_only_decimal_rounder": {
            "function": "0x00080f88",
            "callers_are_within_speed_dynamics_graph": True,
            "factor": "powf(10, decimal_places_float32)",
            "factor_zero_returns": 0,
            "nonnegative_bias": 0.5,
            "negative_bias_float32_bits": "0x3ecccccd",
            "integer_conversion": "saturating Float32-to-Int32 truncation toward zero",
            "nan_integer_conversion": 0,
            "positive_overflow_integer_conversion": "0x7fffffff",
            "negative_overflow_integer_conversion": "0x80000000",
            "negative_half_behavior_is_asymmetric": True,
        },
        "active_only_speed_dynamics_baseline": {
            "stock_reachable": False,
            "function": "0x00090c54",
            "callers": ["0x0008149a", "0x0008897c", "0x00088990"],
            "input_negative_or_unordered_returns_zero": True,
            "subunit_normalization_threshold": 1.0,
            "subunit_normalized_input": 1.0,
            "unflagged_subunit_output_is_rescaled_by_original_input": True,
            "flag_mask": "0x0440",
            "flagged_calibration_threshold_float32_bits": "0x3fa00000",
            "flagged_calibration_float32_bits": "0x3cbd230c",
            "cubic_coefficient_float32_bits": "0x3e1704ff",
            "ordinary_calibration_coefficients_float32_bits": [
                "0xbaaa3573", "0x3afd428b", "0x3e91bad6", "0x3fe6b205",
            ],
            "auxiliary_divisor_float32_bits": "0x42700000",
            "gravity_float32_bits": "0x411cf5c3",
            "quadratic_coefficient_float32_bits": "0x3d1a2c67",
            "decimal_places": 5,
            "nonpositive_rounded_sum_returns_zero": True,
            "output_scale_float32_bits": "0x3f0dd2f2",
            "state_parameter_offsets": ["0x000", "0x004"],
            "state_parameter_writers_found": False,
            "semantic_name_in_image": None,
        },
        "active_only_speed_dynamics_reducer": {
            "stock_reachable": False,
            "function": "0x000888a0",
            "callers": ["0x000674ec", "0x00068314"],
            "inputs": [
                "unlabeled_primary_float32", "unlabeled_secondary_float32",
                "unlabeled_auxiliary_float32",
            ],
            "secondary_nonzero_projection": "primary / cosf(atanf(secondary / primary))",
            "projection_ratio_is_zero_unless_primary_is_positive": True,
            "subunit_secondary_suppression": "zero when abs(secondary) is below twice calibration",
            "low_input_maximum_float32_bits_inclusive": "0x3f800000",
            "high_input_state_writes": {
                "transformed_primary": "0x008",
                "transformed_power": "0x010",
            },
            "high_input_components": [
                "power_delta", "secondary_linear", "calibration_linear",
                "transformed_change", "optional_cubic",
            ],
            "falling_power_multiplier_float32_bits": "0x3dcccccd",
            "transformed_difference_cap_float32_bits": "0x40600000",
            "transformed_difference_coefficient_float32_bits": "0xbe924745",
            "transformed_reduction_float32_bits": "0x3c9ba5e3",
            "decimal_places": 3,
            "output_scale_float32_bits": "0x3f0dd2f2",
            "transitive_helpers": [
                "0x00069d20", "0x00067470", "0x00069d80", "0x000695a8",
            ],
            "state_parameter_writers_found": False,
            "semantic_name_in_image": None,
        },
        "active_only_speed_dynamics_root_primitives": {
            "stock_reachable": False,
            "dimensionless_transform": {
                "function": "0x000568ac",
                "formula": "input*0.146635*state0*100/(60-input*0.15721*state0*100)",
                "numerator_coefficient_float32_bits": "0x3e16277c",
                "denominator_coefficient_float32_bits": "0x3e20fba9",
            },
            "quadratic_positive_root_writer": {
                "function": "0x0006818c",
                "root_state_offsets": ["0x018", "0x01c", "0x020"],
                "invalid_discriminant_or_zero_a_clears": ["0x018", "0x01c"],
                "nonpositive_candidate_retains_prior_slot": True,
                "third_root_is_never_changed": True,
                "square_root_implementation": "powf(discriminant, 0.5)",
            },
            "nearest_root_selector": {
                "function": "0x00068420",
                "zero_is_initial_candidate_when_root0_is_zero": True,
                "later_equal_distance_candidate_wins": True,
                "captured_negative_nonzero_root_is_considered": True,
                "distance_comparison": "absolute Float32 subtraction promoted to binary64",
            },
            "root_state_writer_found_outside_dormant_graph": False,
            "semantic_names_in_image": None,
        },
        "active_only_speed_dynamics_cubic_solver": {
            "stock_reachable": False,
            "coefficient_solver": "0x0006808c",
            "cardano_assembler": "0x000675dc",
            "complex_power": "0x00058c7a",
            "complex_multiply": "0x00058c40",
            "adjusted_complex_sum": "0x00056c2a",
            "real_cube_root": "0x00077e48",
            "candidate_writer": "0x000908ac",
            "real_or_imaginary_square_root": "0x00090efc",
            "one_third_float32_bits": "0x3eaaaaab",
            "real_discriminant_first_imaginary_bias_float32_bits": "0x358637bd",
            "candidate_imaginary_tolerance_float32_bits": "0x3727c5ac",
            "candidate_imaginary_comparison": "signed Int32 comparison of raw Float32 bits",
            "negative_imaginary_candidates_of_any_magnitude_pass_tolerance": True,
            "candidate_real_requirement": "ordered greater than or equal to zero",
            "failed_candidate_retains_prior_root_slot": True,
            "production_libm_sequence": [
                "atan2f", "sqrtf", "logf", "expf", "cosf", "sinf",
            ],
            "semantic_name_in_image": None,
        },
        "active_only_speed_dynamics_root_builder": {
            "stock_reachable": False,
            "function": "0x00068d18",
            "callers": ["0x00081466", "0x000814b4"],
            "inputs": [
                "unlabeled_primary_float32", "unlabeled_auxiliary_float32",
                "state_parameter_0_float32", "state_parameter_1_float32",
                "three_retained_root_slots", "mode_int32",
            ],
            "mode_zero_dispatch": "quadratic positive-root writer 0x0006818c",
            "nonzero_mode_dispatch": "Cardano-style cubic writer 0x0006808c",
            "mode_zero_coefficients_float32_bits": [
                "state1*0x3a252696*auxiliary",
                "0x39b7ccb5*auxiliary*state1*state0",
                "0x3d5385d9*auxiliary*state1*state0"
                "-powf(auxiliary,2)*0x39770e14*state1*state0-primary",
            ],
            "nonzero_mode_leading_coefficient_float32_bits": "0x3e1704ff",
            "root_state_offsets": ["0x018", "0x01c", "0x020"],
            "failed_or_nonpositive_candidates_preserve_solver_specific_slots": True,
            "state_parameter_writers_found": False,
            "semantic_name_in_image": None,
        },
        "active_only_speed_dynamics_alternate_root_solver": {
            "stock_reachable": False,
            "function": "0x00069dc8",
            "only_caller": "0x00081486",
            "dimensionless_target_function": "0x000568ac",
            "mode_zero_dispatch": "quadratic positive-root writer 0x0006818c",
            "nonzero_mode_dispatch": "Cardano-style cubic writer 0x0006808c",
            "nearest_root_selector": "0x00068420",
            "first_coefficient": "state1*0x3a252696*auxiliary",
            "zero_middle_coefficient_float32_bits": "0x00000000",
            "final_coefficient": (
                "state0*0x3bf76450*state1*auxiliary-primary"
            ),
            "nonzero_mode_leading_coefficient_float32_bits": "0x3e1704ff",
            "attenuation_threshold_float32_bits": "0x3fa00000",
            "attenuation_threshold_comparison": "signed Int32 comparison of raw Float32 bits",
            "attenuation_factor_float32_bits": "0x3f333333",
            "exact_threshold_is_not_attenuated": True,
            "nonpositive_or_unordered_result_returns_zero": True,
            "root_state_offsets": ["0x018", "0x01c", "0x020"],
            "state_parameter_writers_found": False,
            "semantic_name_in_image": None,
        },
        "active_only_speed_dynamics_finalizer": {
            "stock_reachable": False,
            "function": "0x0008141c",
            "callers": ["0x000674f8", "0x00068320"],
            "input_divisor_float32_bits": "0x3f0dd2f2",
            "flag_mask": "0x0440",
            "unflagged_baseline_function": "0x00090c54",
            "unflagged_baseline_input_float32_bits": "0x3f800000",
            "unflagged_below_baseline_result": "normalized_input/baseline when ordered positive",
            "unordered_baseline_comparison_takes_below_branch": True,
            "unflagged_root_builder": "0x00068d18",
            "unflagged_root_reduction": {
                "all_zero": 0,
                "root_zero_only": "root0",
                "mode_zero_otherwise": "(root0+root1)*0.5; root2 excluded",
                "nonzero_mode_otherwise": "(root0+root1+root2)/3",
            },
            "unflagged_nonpositive_or_unordered_result_returns_zero": True,
            "flagged_dimensionless_target": "0x000568ac",
            "flagged_target_threshold_float32_bits": "0x3fa00000",
            "flagged_target_comparison": "signed Int32 comparison of raw Float32 bits",
            "flagged_below_threshold_solver": "0x00069dc8",
            "flagged_at_or_above_threshold_path": ["0x00068d18", "0x00068420"],
            "flagged_direct_nearest_root_has_no_final_positivity_clamp": True,
            "root_state_offsets": ["0x018", "0x01c", "0x020"],
            "state_parameter_writers_found": False,
            "semantic_name_in_image": None,
        },
        "active_only_heart_rate_filter": {
            "stock_reachable": False,
            "wrapper": "0x00094270",
            "filter": "0x00070498",
            "reset_helper": "0x0005d2ec",
            "state_offset": "0x278",
            "state_bytes": 100,
            "enable_byte_initial_value": 0,
            "enable_byte_writer_found": False,
            "wrapper_interval_milliseconds": 1000,
            "accepted_interval_milliseconds": [700, 1300],
            "maximum_rise_per_update": 6,
            "maximum_fall_per_update": -7,
            "history_float32_count": 20,
            "rolling_threshold_count": 19,
            "maximum_missing_count": 3,
            "maximum_unchanged_count": 20,
            "statuses": {
                "success": 1,
                "invalid_interval": 0x1771,
                "inactive": 0x1772,
                "reset_after_missing_run": 0x1773,
                "unchanged_run_exceeded": 0x1774,
                "reset_on_initial_invalid": 0x1775,
            },
            "wrapper_uses_filtered_only_for_status": 1,
            "stock_wrapper_falls_back_to_raw_input": True,
        },
        "active_only_ratio_accumulator": {
            "stock_reachable": False,
            "accumulator": "0x00096634",
            "bin_helper": "0x00094698",
            "forbidden_flag_mask": "0x4203",
            "required_flag_mask": "0x040c",
            "stock_flag_word": "0x0000",
            "flag_word_writer_found": False,
            "profile_flag_state_offset": "0x00d",
            "stock_profile_flag": 0,
            "profile_flag_writer_found": False,
            "threshold_state_offset": "0x170",
            "threshold_float32_count": 5,
            "stock_threshold_float32": [0, 0, 0, 0, 0],
            "threshold_writer_found": False,
            "bin_count": 6,
            "speed_qualifier_float32_bits_exclusive": "0x40800000",
            "profile_zero_first_bin_weight_float32_bits": "0x3f9c28f6",
            "profile_nonzero_first_bin_weight_float32_bits": "0x3fa8f5c3",
            "minimum_qualified_count_float32_bits": "0x41f00000",
            "maximum_dispersion_float32_bits": "0x3f7fffff",
            "all_mean_offsets": ["0x210", "0x214"],
            "qualified_moment_offsets": ["0x218", "0x21c", "0x220", "0x224"],
            "primary_bin_offsets": ["0x1c0", "0x1d8"],
            "secondary_bin_offsets": ["0x228", "0x240"],
            "ratio": "selected_speed / heart_rate",
            "semantic_name_in_image": None,
        },
        "output": {
            "engine_offset": "0x140",
            "bytes": 68,
            "opaque_prefix_bytes": 66,
            "status_int16_offset": 66,
            "status_helper": "0x00069f80",
            "status_helper_writes_prefix": False,
            "nonzero_fatal_halfword_clears_entire_record": True,
            "fatal_helper_return": fatal_output_error,
            "copied_status_low_byte_engine_offset": "0x182",
            "copied_status_low_byte_io_offset": "0x81",
            "stock_copied_value": 0,
            "stock_host_reader_found": False,
        },
        "verified_ranges": verified_ranges,
        "direct_branches": branches,
        "safety": {
            "engine_execution": False,
            "live_sram_read": False,
            "stage_activation": False,
            "input_injection": False,
            "firmware_write": False,
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
