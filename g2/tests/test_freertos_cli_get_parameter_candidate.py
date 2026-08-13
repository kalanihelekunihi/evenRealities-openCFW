from __future__ import annotations

import ctypes
from collections import Counter
import hashlib
import importlib.util
import itertools
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT / "components" / "shared" / "freertos_cli"
    / "runtime_freertos_cli_get_parameter_candidate.c"
)
HEADER = SOURCE.with_suffix(".h")
PRODUCTION_SOURCE = (
    ROOT / "components" / "shared" / "freertos_cli"
    / "runtime_freertos_cli_get_parameter.c"
)
PRODUCTION_HEADER = PRODUCTION_SOURCE.with_suffix(".h")
CAPACITY_PATCH_SOURCE = (
    ROOT / "components" / "apollo_main" / "core_overlay"
    / "runtime_freertos_cli_collector_capacity_patch.S"
)
HOST_FIXTURE = (
    ROOT / "tests" / "fixtures"
    / "runtime_freertos_cli_get_parameter_candidate_host.c"
)
ORACLE_INCLUDE = (
    ROOT / "tests" / "fixtures" / "freertos_cli_get_parameter_oracle"
)
ORACLE_FREERTOS = ORACLE_INCLUDE / "FreeRTOS.h"
ORACLE_TASK = ORACLE_INCLUDE / "task.h"
UPSTREAM_ROOT = ROOT / "third_party" / "freertos-plus-cli"
UPSTREAM_SOURCE = UPSTREAM_ROOT / "FreeRTOS_CLI.c"
UPSTREAM_HEADER = UPSTREAM_ROOT / "FreeRTOS_CLI.h"
UPSTREAM_VERIFIER = UPSTREAM_ROOT / "verify_snapshot.py"
AUDIT = (
    ROOT / "docs" / "research"
    / "freertos-cli-get-parameter-source-candidate-audit.md"
)
OFFICIAL = (
    ROOT / "blobs" / "official" / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
OVERLAY = ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"
MANIFESTS = ROOT / "manifests"
MAKEFILE = ROOT / "Makefile"
CLI_ANALYZER = ROOT / "tools" / "analyze_g2_freertos_plus_cli.py"

BASE = 0x0043_8000
PACKAGE_PREAMBLE = 32
PACKAGE_SIZE = 3_523_396
PACKAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
APPLICATION_SHA256 = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"

START = 0x0058_48FC
END = 0x0058_4960
STOCK_SHA256 = "35c6a4ce194bbea2a6044c3ab8f1108bb6c88806bafbf196fdb88c49a983a6f4"
STOCK_BYTES = (
    "30b4030000250024002010608d4226d200e05b1c1878002802d018782028f8d1"
    "1878002804d01878202801d15b1cf7e71878002813d06d1c8d42e7d11c0003e0"
    "1068401c10605b1c1878002802d018782028f5d11068002800d10024ffe72000"
    "30bc7047"
)
PREDECESSOR_TAIL_START = 0x0058_48F4
PREDECESSOR_TAIL_SHA256 = "55e991a5166aaf1ba985d30f4cd65c23c29dbc5253bce1b72144bb9731089ee0"
PREDECESSOR_TAIL_BYTES = "00242000bde8f087"
SUCCESSOR_END = 0x0058_498E
SUCCESSOR_SHA256 = "7603491ef1e11c9a1163028ac35a5800f53402536eb99633a45fee477948a32c"
MAX_INDEX_WINDOW = (0x0058_0AF4, 0x0058_0B1C)
MAX_INDEX_WINDOW_SHA256 = "8a19c2866a484db48995aedef803a5d404ec12a03cdae35ac7f466b30a19318f"
INPUT_LIMIT_WINDOW = (0x0054_1704, 0x0054_171C)
INPUT_LIMIT_WINDOW_SHA256 = "93ed4e2a27efe979fcfe6ec2158443550f9bc1176be6fc7a814e693b78b97284"

CALLERS = (
    0x0057E42C, 0x0057E49A, 0x0057E508, 0x0057E566,
    0x0057E93A, 0x0057EA24, 0x0057EBB0, 0x0057EC96,
    0x0057ED40, 0x0057F290, 0x0057F6AA, 0x0057F6B6,
    0x0057F8C6, 0x0057F8D2, 0x0057F9AC, 0x0057F9B8,
    0x0057FCDC, 0x0057FCE8, 0x0057FCF4, 0x0058010A,
    0x0058011A, 0x0058012A, 0x0058014E, 0x0058015C,
    0x0058016C, 0x005801BE, 0x005801CE, 0x005801F6,
    0x00580226, 0x00580236, 0x0058025E, 0x0058027E,
    0x0058029C, 0x005802A8, 0x005802D0, 0x005802E0,
    0x00580306, 0x00580336, 0x0058037E, 0x00580438,
    0x005804C8, 0x0058052C, 0x00580538, 0x00580836,
    0x00580852, 0x00580886, 0x005808BA, 0x00580914,
    0x00580A48, 0x00580A7C, 0x00580AC8, 0x00580B14,
    0x00580B4E, 0x00580B72, 0x00580B9E, 0x00580BAE,
    0x00580C90, 0x00580CAC, 0x00580CD2, 0x00580D2C,
    0x00580D38, 0x00580E3E, 0x005810AA, 0x005810FE,
    0x00581198, 0x0058126E, 0x0058137E, 0x0058138A,
    0x005814E6, 0x00581574, 0x0058177E, 0x0058178A,
    0x00581864, 0x0058188A, 0x005818B0, 0x0058191A,
    0x00581A5E, 0x00581A6A, 0x00581A76, 0x00581D1E,
    0x00581D2A, 0x00581EF4, 0x00581F00, 0x00581F0C,
    0x00581F18, 0x005822F4, 0x0058246E, 0x0058247A,
    0x00582486, 0x00582492, 0x005824CC, 0x005824D8,
    0x00582B32, 0x00582B3E, 0x00582B4A, 0x00582B56,
    0x0058392C, 0x00583950, 0x005839D0, 0x00583A0E,
    0x00583A6A, 0x00583E0E, 0x00583E36, 0x00583E42,
    0x00583E4E, 0x00583ECE, 0x00583F0A, 0x00583F16,
    0x0058403E, 0x0058404A, 0x00584136, 0x00584226,
    0x0058436E, 0x005843C8, 0x0058450C,
)
# The whole-program proof below closes R0 to the sole console input array at
# every caller.  Stock NUL termination remains conditional at exactly 128
# accepted bytes, so promotion still requires the separate collector patch.
R0_PROVENANCE_CLOSED_CALLERS = CALLERS
STOCK_TERMINATION_RISK_CALLERS = CALLERS
CALLER_ADDRESS_SHA256 = "e43d8a1d82be6ce7313378790a1c74156806f3c0d1d6f1f9db1251d6a8ffee69"
CALLER_RECORD_SHA256 = "00271d27ae69620b273eaa6d1824990df438fc3550fade8401200da774c32ce8"
CALLER_PRE_CALL_BYTES = 16
CALLER_WINDOW_RECORD_SHA256 = "e19714e9aecd89167144a65f49c4d6ec5bfa6f4dfe6b23b8339270e95a9c0d71"
CALLER_WINDOW_DIGEST_RECORD_SHA256 = "c2693e4d02cc2f5db9cdd8d1fcc6e660ddac9eddd277e322db783d13f1374dcf"
CALLER_ABI_CLASSIFICATION_SHA256 = "641e283917a4da175037b8a0eebc7f6ae93c33b1fc9754d3d6ff7c6aae21182c"
CALLER_INDEX_HISTOGRAM = (
    ((1, 1), 55),
    ((2, 2), 36),
    ((3, 3), 14),
    ((3, 5), 2),
    ((3, 7), 1),
    ((3, 11), 1),
    ((4, 4), 4),
    ((5, 5), 1),
    ((6, 6), 1),
)
CALLER_R2_STACK_OFFSET_HISTOGRAM = (
    (0, 60),
    (4, 20),
    (8, 7),
    (12, 5),
    (16, 14),
    (20, 2),
    (24, 3),
    (28, 2),
    (32, 1),
    (36, 1),
)

# The only non-immediate R1 constructions are bounded by these exact stock
# windows.  The tuple fields are start, end, inclusive index bounds, and SHA.
DYNAMIC_INDEX_PROOFS = {
    0x0058_0A7C: (
        0x0058_0A5C,
        0x0058_0A80,
        3,
        5,
        "c6513159fb2210bed62e6c240869100acf2512816e373af29d96d5108d9b7e4c",
    ),
    0x0058_0AC8: (
        0x0058_0AA8,
        0x0058_0ACC,
        3,
        5,
        "467d589b69acf53887a1f96de29f739155d7954be7fe7d88d280b06dc128a465",
    ),
    0x0058_0B14: (
        0x0058_0AF4,
        0x0058_0B18,
        3,
        11,
        "4d96b7ab8313a8e8c90985433a81909af15887f24642382f997adc9c1edaac70",
    ),
    0x0058_191A: (
        0x0058_18CA,
        0x0058_191E,
        3,
        7,
        "e61574f553b20eba5d55ac01a3621d65aef8d6806bcd3ca8ff996f49f9ad3bef",
    ),
}

PROCESS_ENTRY = 0x0058_47FE
PROCESS_CALL = 0x0054_166E
PROCESS_CALLBACK_WINDOW = (0x0058_48A4, 0x0058_48BC)
PROCESS_CALLBACK_WINDOW_SHA256 = "131ab6846509750583837a737d44c940c3fe0ec3c4e758950b7a434b0d9b5f56"
CONSOLE_TASK = (0x0054_1600, 0x0054_171C)
CONSOLE_TASK_SHA256 = "c1b9332fb9c932550478f1c2fa80546883aae78259aa887a0ec23ffb007338ef"
CONSOLE_COLLECT_DISPATCH = (0x0054_165E, 0x0054_171C)
CONSOLE_COLLECT_DISPATCH_SHA256 = "e0e237ca437e66333fd76287f76ab48dae97a1f2263a35958ba58d7429f3625a"
CONSOLE_PROCESS_AND_FULL_CLEAR = (0x0054_1664, 0x0054_1694)
CONSOLE_PROCESS_AND_FULL_CLEAR_SHA256 = "87977ac7163fc502cee45aeba30abdad55598eb15d115b55e8fd65e0d3a2027a"
CONSOLE_CONTROL_WINDOW = (0x0054_16A4, 0x0054_16E2)
CONSOLE_CONTROL_WINDOW_SHA256 = "9e94d6214533e5b464237ee15f31df70cfde886ed43e705bf38812ff1332f912"
CONSOLE_BACKSPACE_WINDOW = (0x0054_16E2, 0x0054_1704)
CONSOLE_BACKSPACE_WINDOW_SHA256 = "bf6d2faa9b4c9093249bec9fc5fa934892a1345be26c842b4cbd894402fa21df"
CONSOLE_INPUT_CLEAR = (0x0054_1688, 0x0054_1694)
CONSOLE_INPUT_CLEAR_SHA256 = "466b6be4c3569f60381d2b1ae9c9ae06bacf7621d82b32af27fbda1a754ad7f3"
CONSOLE_TASK_POINTER = (0x0054_178C, 0x0054_1601)
CONSOLE_INPUT_LITERAL = (0x0054_1778, 0x2007_1BC8)
CONSOLE_OUTPUT_LITERAL = (0x0054_1774, 0x2007_1B48)
CONSOLE_ADJACENT_OBJECT = (0x0047_21F8, 0x2007_1C48)
COLLECTOR_CAPACITY_PATCH = (0x0054_1708, bytes.fromhex("8028"), bytes.fromhex("7f28"))
HARDENED_CONSOLE_TASK_SHA256 = "518c83a818d6cd6eb34a7f1da015010adaf10637e42b7830a3f365adaf28bb5f"
STARTUP_ZERO_GATE = (0x005E_4228, bytes.fromhex("06480749086001207047"))
STARTUP_ZERO_GATE_SHA256 = "bee8bcf07546d7e7b549b10cfe4fc3c6519a6a49dc357d32179df469f5a8e36c"
STARTUP_SCATTER_CALL_WINDOW = (
    0x005E_4294,
    bytes.fromhex("fff7c8ff002801d000f00af8"),
)
SCATTER_ZERO_RECORD = (0x0075_D3C8, 0x0075_D3E0)
SCATTER_ZERO_RECORD_SHA256 = "2a52162870b1f1b036f1769e75dabcf475f17eb6c37c85ffcabcb9dcfd064e15"
SCATTER_ZERO_HANDLER = (0x005F_A01E, 0x005F_A056)
SCATTER_ZERO_HANDLER_SHA256 = "8b74bda81d1262930007b87bd980ccaebc6028472d7dd7413c20cc1f281b1b67"
SCATTER_ZERO_RANGE = (0x2000_4558, 0x2007_5048)

# Each entry is (registered callback entry, command name, command-input
# carrier, complete FreeRTOS_CLIGetParameter call tuple).  R0 means that the
# handler moves callback R2 directly into R0 and keeps it live to the call.
R0_HANDLER_GROUPS = (
    (0x0057E420, "SetGPIO", "r0", (0x0057E42C,)),
    (0x0057E48E, "ResetGPIO", "r0", (0x0057E49A,)),
    (0x0057E4FC, "ProductControlCodec", "r0", (0x0057E508,)),
    (0x0057E55A, "ChargerControl", "r0", (0x0057E566,)),
    (0x0057E920, "cat", "r0", (0x0057E93A,)),
    (0x0057EA0A, "rm", "r0", (0x0057EA24,)),
    (0x0057EB94, "cd", "r0", (0x0057EBB0,)),
    (0x0057EC7C, "mkdir", "r0", (0x0057EC96,)),
    (0x0057ED26, "touch", "r0", (0x0057ED40,)),
    (0x0057F274, "md5", "r0", (0x0057F290,)),
    (0x0057F68C, "rename", "r4", (0x0057F6AA, 0x0057F6B6)),
    (0x0057F8BC, "xip", "r4", (0x0057F8C6, 0x0057F8D2)),
    (0x0057F980, "file2xip", "r4", (0x0057F9AC, 0x0057F9B8)),
    (0x0057FCAC, "xip2file", "r4", (0x0057FCDC, 0x0057FCE8, 0x0057FCF4)),
    (0x00580100, "input", "r4", (0x0058010A, 0x0058011A, 0x0058012A)),
    (0x00580144, "sinput", "r4", (0x0058014E, 0x0058015C, 0x0058016C)),
    (0x005801B4, "udata", "r4", (0x005801BE, 0x005801CE)),
    (0x005801EE, "syncTest", "r0", (0x005801F6,)),
    (0x0058021C, "pdata", "r4", (0x00580226, 0x00580236)),
    (0x00580256, "dispStart", "r0", (0x0058025E,)),
    (0x00580276, "singleStart", "r0", (0x0058027E,)),
    (0x00580292, "singleReflash", "r4", (0x0058029C, 0x005802A8)),
    (0x005802C6, "dispReflash", "r4", (0x005802D0, 0x005802E0)),
    (0x005802FE, "dispStop", "r0", (0x00580306,)),
    (0x0058032A, "dispBlockEn", "r0", (0x00580336,)),
    (0x00580376, "singleStop", "r0", (0x0058037E,)),
    (0x00580430, "logcat", "r0", (0x00580438,)),
    (0x005804C0, "logf", "r0", (0x005804C8,)),
    (0x00580518, "AT^LOGTYPE", "r4", (0x0058052C, 0x00580538)),
    (0x00580824, "imu", "r5", (
        0x00580836, 0x00580852, 0x00580886, 0x005808BA,
        0x00580914, 0x00580A48, 0x00580A7C, 0x00580AC8,
        0x00580B14, 0x00580B4E, 0x00580B72, 0x00580B9E,
        0x00580BAE,
    )),
    (0x00580C7C, "audm", "r4", (0x00580C90, 0x00580CAC, 0x00580CD2)),
    (0x00580D18, "codec", "r4", (0x00580D2C, 0x00580D38, 0x00580E3E)),
    (0x0058109C, "AT^psn", "r0", (0x005810AA,)),
    (0x005810F0, "pdm", "r0", (0x005810FE,)),
    (0x0058118A, "AT^BLES", "r0", (0x00581198,)),
    (0x0058125E, "AT^BLEM", "r4", (0x0058126E,)),
    (0x0058136C, "AT^BLEMC", "r4", (0x0058137E, 0x0058138A)),
    (0x005814D4, "AT^BLERingSend", "r4", (0x005814E6,)),
    (0x00581564, "AT^BLEADV", "r4", (0x00581574,)),
    (0x00581774, "xmodem", "r4", (0x0058177E, 0x0058178A)),
    (0x0058185C, "alert", "r0", (0x00581864,)),
    (0x00581874, "dashboard_layout", "r6", (0x0058188A, 0x005818B0, 0x0058191A)),
    (0x00581A40, "tp", "r5", (0x00581A5E, 0x00581A6A, 0x00581A76)),
    (0x00581D08, "weardetect", "r4", (0x00581D1E, 0x00581D2A)),
    (0x00581ED0, "conversate", "r6", (0x00581EF4, 0x00581F00, 0x00581F0C, 0x00581F18)),
    (0x005822E6, "translate", "r0", (0x005822F4,)),
    (0x00582448, "teleprompt", "r8", (
        0x0058246E, 0x0058247A, 0x00582486,
        0x00582492, 0x005824CC, 0x005824D8,
    )),
    (0x00582B0C, "terminal", "r6", (0x00582B32, 0x00582B3E, 0x00582B4A, 0x00582B56)),
    (0x00583918, "set", "r6", (0x0058392C, 0x00583950, 0x005839D0, 0x00583A0E, 0x00583A6A)),
    (0x00583DF8, "buzzer", "r7", (
        0x00583E0E, 0x00583E36, 0x00583E42, 0x00583E4E,
        0x00583ECE, 0x00583F0A, 0x00583F16,
    )),
    (0x0058402A, "gpio", "r4", (0x0058403E, 0x0058404A)),
    (0x00584128, "box_force_out", "r0", (0x00584136,)),
    (0x0058421C, "SetLanguage", "r0", (0x00584226,)),
    (0x0058435C, "onboarding", "r5", (0x0058436E, 0x005843C8)),
    (0x005844FE, "get", "r0", (0x0058450C,)),
)
R0_HANDLER_GROUP_SHA256 = "99ce1c81159593bd505566b495198a1ab9b36a0856dcafd415a9bf904a654eaa"
R0_HANDLER_PREFIX_SHA256 = "73123df6c9ec6f8b14ef8e9ab1ec120318b54b15af90a084d5d2856924572843"
R0_CALL_BINDING_SHA256 = "6b67204cb7d5dcf06b1f550020857e2b8b9ecfa67f0177afd4b657130690f044"
R0_GUARDED_DIRECT_HANDLERS = (
    0x0057E920, 0x0057EA0A, 0x0057EB94,
    0x0057EC7C, 0x0057ED26, 0x0057F274,
)
R0_SOURCE_CODES = {"r0": 0, "r4": 4, "r5": 5, "r6": 6, "r7": 7, "r8": 8}
R0_INPUT_BINDINGS = {
    "r0": bytes.fromhex("1000"),
    "r4": bytes.fromhex("1400"),
    "r5": bytes.fromhex("1500"),
    "r6": bytes.fromhex("1600"),
    "r7": bytes.fromhex("1700"),
    "r8": bytes.fromhex("9046"),
}
R0_CALL_RELOADS = {
    "r4": bytes.fromhex("2000"),
    "r5": bytes.fromhex("2800"),
    "r6": bytes.fromhex("3000"),
    "r7": bytes.fromhex("3800"),
    "r8": bytes.fromhex("4046"),
}

# A byte-granular scan has one numerical collision.  It is the unaligned
# ASCII bytes ``RIX\0`` inside "NON_INVERTIBLE_MATRIX", not a stored code
# pointer.  Aligned words and odd Thumb pointers have no matches.
STORED_VALUE_COLLISION = (0x0077_8176, 0x0058_4952)
STORED_VALUE_STRING = (0x0077_8164, b"NON_INVERTIBLE_MATRIX")

UPSTREAM_SOURCE_SIZE = 11_623
UPSTREAM_SOURCE_SHA256 = "1719b355951afaf3349a371ff633d9dd4867a3e3442b91552fd3550082ef93f4"
UPSTREAM_HEADER_SIZE = 4_972
UPSTREAM_HEADER_SHA256 = "c60d23b875d04429ba745b340d934b6c5eae89ce3be2b3a4aa92a034e6176890"
UPSTREAM_FUNCTION_SIZE = 1_316
UPSTREAM_FUNCTION_SHA256 = "b9e95de63ffd212c6dd455159839b6f9d6507d40662493f5b5e3832919d0094b"

LOCAL_PINS = {
    SOURCE: (2_819, "c31899da1a03e88d2505ce3d3ac3a1b52509f9bfab842ddd0b2cf9464e8f2930"),
    HEADER: (1_294, "d05f89bb3c4b8344b81659a875cf77aec74ffc427d6f4c0ef58447fdf0d74f70"),
    PRODUCTION_SOURCE: (
        2_847,
        "7f04ecb4318ba255b0d65d82c5fd1fceafd7939e89c93113b5fb1f69e6ef8552",
    ),
    PRODUCTION_HEADER: (
        1_308,
        "531fbe4e2e6ecab0f32da159864ce963b40851e1ddb6e80406d99e780a80d17c",
    ),
    HOST_FIXTURE: (1_629, "441a7eac2938ba271c89d3472e591aeae7020e09a62fed89a4c0a021a4e5aa40"),
    ORACLE_FREERTOS: (545, "d7d26580be8ae3121f518bb6d6f1d616bd5f2900bc8db2bb5aa514becd39c906"),
    ORACLE_TASK: (188, "2f91fdb1f93aa6a34feb166b8f8cf4b6327e6a893df12fd739dc7a8d9e9a936f"),
    CAPACITY_PATCH_SOURCE: (
        1_086,
        "1d99c7e22eccd2148bec103c1b538261adfeedee66df79ec7d79afd46c293630",
    ),
    AUDIT: (20_704, "00e7a24c96b7d3c65fbf669ae70998fe3cacdfc0471ad8257b69a78e1a4674aa"),
}

FUNCTION = "open_cfw_freertos_cli_get_parameter_candidate"
PRODUCTION_FUNCTION = "open_cfw_freertos_cli_get_parameter"
FUNCTION_SECTION = ".text." + FUNCTION
EXIDX_SECTION = ".ARM.exidx" + FUNCTION_SECTION
TARGET_FUNCTION_HEX = (
    "80b54ff0000cc2f800c009e0bef1000f04bf002080bd00bf0cf1010c8c453fd0"
    "8c453bd0037813f0df0f13d0437813f0df0f09d0837813f0df0f07d0c37813f0"
    "df0f05d00430ede7013003e0023001e0033000bf5ffa83febef1200fd6d14378"
    "202b09d18378202b0cd1c378202b0fd110f8043feee700bf002b04bf002080bd"
    "0130c9e7002b04bf002080bd0230c3e7002b04bf002080bd0330bde7002080bd"
    "4ff0020c13f0df0f20d0acf10103136000eb0c0313f8011c11f0df0f19d0c2f8"
    "00c010f80c1011f0df0f12d00cf101011160597811f0df0f0bd00cf102011160"
    "9b780cf1040c13f0df0fded1acf1020100e00121002908bf084680bd"
)
EXIDX_BYTES = bytes.fromhex("0000000001000000")
TARGET_PROFILES = {
    "apple-clang": {
        "compiler": "/usr/bin/clang",
        "version": "Apple clang version 21.0.0 (clang-2100.3.30.1)",
        "object": (1_064, "aeef70e13e386f34dd78548a0dbfe211fb883ee2b1e5146f209e7bef78318832"),
        "function": (252, 4, "7b77ccc3441cb8e725fa8a97a8197e0f993a00456925c6eb0126e77fb00f9914"),
        "exidx": (8, "01acecb507abfe1a354aa8064f4af5d3f1acd019e37db3c11c97523b71c76e9d"),
    },
    "linux-clang": {
        "compiler": "/home/linuxbrew/.linuxbrew/bin/clang",
        "version": "Homebrew clang version 22.1.8",
        "object": (1_064, "aeef70e13e386f34dd78548a0dbfe211fb883ee2b1e5146f209e7bef78318832"),
        "function": (252, 4, "7b77ccc3441cb8e725fa8a97a8197e0f993a00456925c6eb0126e77fb00f9914"),
        "exidx": (8, "01acecb507abfe1a354aa8064f4af5d3f1acd019e37db3c11c97523b71c76e9d"),
    },
}
TARGET_FLAGS = [
    "--target=thumbv7em-none-eabi",
    "-mthumb",
    "-O2",
    "-ffreestanding",
    "-fno-jump-tables",
    "-fomit-frame-pointer",
    "-fno-builtin",
    "-mno-unaligned-access",
    "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables",
    "-fropi",
    "-ffunction-sections",
    "-fdata-sections",
    "-Wall",
    "-Wextra",
    "-Werror",
    "-fno-ident",
]
CAPACITY_PATCH_FUNCTION = "open_cfw_freertos_cli_collector_capacity_patch"
CAPACITY_PATCH_HEX = "7f28"
CAPACITY_PATCH_SHA256 = "dbf2d8a1ffb886d7964cf470133c8a289aff606c14e6d75fd258678de0f47495"
CAPACITY_PATCH_FLAGS = [
    "--target=arm-none-eabi",
    "-mcpu=cortex-m55",
    "-mthumb",
    "-ffreestanding",
    "-fno-builtin",
    "-ffunction-sections",
    "-fdata-sections",
    "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables",
    "-Wall",
    "-Wextra",
    "-Werror",
]


def sha256(data: bytes | Path) -> str:
    if isinstance(data, Path):
        data = data.read_bytes()
    return hashlib.sha256(data).hexdigest()


def library_name(stem: str) -> str:
    return stem + (".dylib" if sys.platform == "darwin" else ".so")


def wide_branch_target(
    application: bytes,
    address: int,
    *,
    link: bool,
) -> int | None:
    first, second = struct.unpack_from("<HH", application, address - BASE)
    if first & 0xF800 != 0xF000:
        return None
    if second & 0xD000 != (0xD000 if link else 0x9000):
        return None
    sign = (first >> 10) & 1
    immediate_10 = first & 0x03FF
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    i1 = (~(j1 ^ sign)) & 1
    i2 = (~(j2 ^ sign)) & 1
    immediate = (
        sign << 24
        | i1 << 23
        | i2 << 22
        | immediate_10 << 12
        | (second & 0x07FF) << 1
    )
    if sign:
        immediate -= 1 << 25
    return address + 4 + immediate


def wide_conditional_target(application: bytes, address: int) -> int | None:
    first, second = struct.unpack_from("<HH", application, address - BASE)
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0x8000:
        return None
    if ((first >> 6) & 0x0F) >= 0x0E:
        return None
    sign = (first >> 10) & 1
    immediate = (
        sign << 20
        | ((second >> 11) & 1) << 19
        | ((second >> 13) & 1) << 18
        | (first & 0x003F) << 12
        | (second & 0x07FF) << 1
    )
    if sign:
        immediate -= 1 << 21
    return address + 4 + immediate


def narrow_targets(address: int, halfword: int) -> tuple[int, ...]:
    if halfword & 0xF800 == 0xE000:
        immediate = halfword & 0x07FF
        if immediate & 0x0400:
            immediate -= 0x0800
        return (address + 4 + (immediate << 1),)
    if halfword & 0xF000 == 0xD000 and halfword & 0x0F00 != 0x0F00:
        immediate = halfword & 0x00FF
        if immediate & 0x0080:
            immediate -= 0x0100
        return (address + 4 + (immediate << 1),)
    if halfword & 0xF500 == 0xB100:
        immediate = (
            ((halfword >> 9) & 1) << 6
            | ((halfword >> 3) & 0x1F) << 1
        )
        return (address + 4 + immediate,)
    return ()


class FreeRTOSCLIGetParameterCandidateTests(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        build = ROOT / "build"
        build.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(dir=build)
        temporary = Path(cls.temporary.name)
        cls.clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        version_output = subprocess.run(
            [cls.clang, "--version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        cls.compiler_version = version_output.splitlines()[0]
        if cls.compiler_version.startswith("Apple clang version 21.0.0"):
            cls.profile = "apple-clang"
        elif cls.compiler_version.startswith("Homebrew clang version 22.1.8"):
            cls.profile = "linux-clang"
        else:
            raise AssertionError(f"unreviewed compiler: {cls.compiler_version!r}")
        configured_profile = os.environ.get("OPENCFW_TOOLCHAIN_PROFILE")
        if configured_profile is not None:
            if configured_profile != cls.profile:
                raise AssertionError(
                    f"profile/compiler mismatch: {configured_profile!r} vs {cls.profile!r}"
                )
        expected_compiler = TARGET_PROFILES[cls.profile]["compiler"]
        if cls.clang != expected_compiler:
            raise AssertionError(
                f"unreviewed compiler root: {cls.clang!r} vs {expected_compiler!r}"
            )

        library = temporary / library_name("freertos_cli_get_parameter")
        host_command = [
            cls.clang,
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-I",
            str(ORACLE_INCLUDE),
            str(SOURCE),
            str(PRODUCTION_SOURCE),
            str(HOST_FIXTURE),
            str(UPSTREAM_SOURCE),
        ]
        if sys.platform == "darwin":
            host_command.extend(["-dynamiclib", "-o", str(library)])
        else:
            host_command.extend(["-shared", "-fPIC", "-o", str(library)])
        subprocess.run(host_command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.candidate = (
            cls.loaded.open_cfw_test_freertos_cli_get_parameter_candidate
        )
        cls.oracle = cls.loaded.open_cfw_test_freertos_cli_get_parameter_upstream
        for function in (cls.candidate, cls.oracle):
            function.argtypes = [
                ctypes.c_void_p,
                ctypes.c_uint32,
                ctypes.POINTER(ctypes.c_int32),
            ]
            function.restype = ctypes.c_int32

        cls.target_objects = [temporary / "candidate-1.o", temporary / "candidate-2.o"]
        for output in cls.target_objects:
            subprocess.run(
                [cls.clang, *TARGET_FLAGS, "-c", str(SOURCE), "-o", str(output)],
                check=True,
                capture_output=True,
                text=True,
            )

        cls.capacity_patch_objects = [
            temporary / "capacity-patch-1.o",
            temporary / "capacity-patch-2.o",
        ]
        for output in cls.capacity_patch_objects:
            subprocess.run(
                [
                    cls.clang,
                    *CAPACITY_PATCH_FLAGS,
                    "-c",
                    str(CAPACITY_PATCH_SOURCE),
                    "-o",
                    str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

        spec = importlib.util.spec_from_file_location(
            "open_cfw_apollo_overlay",
            ROOT / "tools" / "apollo_overlay.py",
        )
        assert spec is not None and spec.loader is not None
        cls.apollo_overlay = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.apollo_overlay)
        cls.object_data, cls.sections = cls.apollo_overlay.parse_elf32(
            cls.target_objects[0]
        )
        symbol_table = cls.apollo_overlay.section_named(cls.sections, ".symtab")
        string_table = cls.sections[int(symbol_table["link"])]
        strings = cls.object_data[
            int(string_table["offset"]):
            int(string_table["offset"]) + int(string_table["size"])
        ]
        cls.symbols = []
        for index in range(int(symbol_table["size"]) // 16):
            fields = struct.unpack_from(
                "<IIIBBH",
                cls.object_data,
                int(symbol_table["offset"]) + index * 16,
            )
            name = cls.apollo_overlay.elf_string(strings, fields[0], "symbol")
            cls.symbols.append((name, fields))

        cls.relocations = []
        for relocation_section in cls.sections:
            if int(relocation_section["type"]) != 9:
                continue
            target = cls.sections[int(relocation_section["info"])]
            for index in range(int(relocation_section["size"]) // 8):
                offset, information = struct.unpack_from(
                    "<II",
                    cls.object_data,
                    int(relocation_section["offset"]) + index * 8,
                )
                cls.relocations.append(
                    (
                        str(relocation_section["name"]),
                        str(target["name"]),
                        offset,
                        information & 0xFF,
                        cls.symbols[information >> 8][0],
                        cls.symbols[information >> 8][1][5],
                    )
                )

        cls.package = OFFICIAL.read_bytes()
        cls.application = cls.package[PACKAGE_PREAMBLE:]
        cli_spec = importlib.util.spec_from_file_location(
            "open_cfw_freertos_cli_analyzer",
            CLI_ANALYZER,
        )
        assert cli_spec is not None and cli_spec.loader is not None
        cls.cli_analyzer = importlib.util.module_from_spec(cli_spec)
        sys.modules[cli_spec.name] = cls.cli_analyzer
        cli_spec.loader.exec_module(cls.cli_analyzer)
        cls.cli_report = cls.cli_analyzer.audit_image(cls.package)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def span(cls, start: int, end: int) -> bytes:
        return cls.application[start - BASE:end - BASE]

    @staticmethod
    def invoke(function, raw: bytes, wanted: int) -> tuple[int, int]:
        buffer = ctypes.create_string_buffer(raw + b"\0")
        length = ctypes.c_int32(-0x1234567)
        offset = int(function(buffer, wanted, ctypes.byref(length)))
        return offset, int(length.value)

    def test_authenticated_upstream_snapshot_and_local_artifacts_are_pinned(self) -> None:
        self.assertEqual(UPSTREAM_SOURCE.stat().st_size, UPSTREAM_SOURCE_SIZE)
        self.assertEqual(sha256(UPSTREAM_SOURCE), UPSTREAM_SOURCE_SHA256)
        self.assertEqual(UPSTREAM_HEADER.stat().st_size, UPSTREAM_HEADER_SIZE)
        self.assertEqual(sha256(UPSTREAM_HEADER), UPSTREAM_HEADER_SHA256)

        upstream = UPSTREAM_SOURCE.read_bytes()
        start = upstream.index(b"const char *FreeRTOS_CLIGetParameter(")
        end = upstream.index(b"/*-----------------------------------------------------------*/", start)
        function = upstream[start:end]
        self.assertEqual(len(function), UPSTREAM_FUNCTION_SIZE)
        self.assertEqual(sha256(function), UPSTREAM_FUNCTION_SHA256)

        verifier = subprocess.run(
            [sys.executable, str(UPSTREAM_VERIFIER)],
            check=True,
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        self.assertEqual(
            verifier.stdout,
            "FreeRTOS+CLI source snapshot verification passed\n",
        )
        for path, (size, digest) in LOCAL_PINS.items():
            with self.subTest(path=path.name):
                self.assertEqual(path.stat().st_size, size)
                self.assertEqual(sha256(path), digest)

    def test_recovered_32_bit_abi_and_source_contract_are_explicit(self) -> None:
        header = HEADER.read_text(encoding="utf-8")
        source = SOURCE.read_text(encoding="utf-8")
        for token in (
            "typedef __UINT32_TYPE__ open_cfw_freertos_cli_ubase_type;",
            "typedef __INT32_TYPE__ open_cfw_freertos_cli_base_type;",
            "sizeof(open_cfw_freertos_cli_ubase_type) == 4U",
            "sizeof(open_cfw_freertos_cli_base_type) == 4U",
            "Parameter numbering starts at one",
            "performs no independent bounds check",
        ):
            self.assertIn(token, header)
        for token in (
            "*parameter_length = 0;",
            "parameters_found < wanted_parameter",
            "*pc_command != '\\0' && *pc_command != ' '",
            "parameters_found == wanted_parameter",
            "(*parameter_length)++;",
        ):
            self.assertIn(token, source)

        # The stock entry immediately treats R0 as the byte cursor, R1 as the
        # wanted 32-bit index, and R2 as a writable 32-bit length pointer.
        stock = bytes.fromhex(STOCK_BYTES)
        self.assertEqual(stock[:12].hex(), "30b403000025002400201060")
        self.assertEqual(stock[-6:].hex(), "200030bc7047")

    def test_candidate_is_differentially_exact_to_compiled_upstream_oracle(self) -> None:
        cases = (
            (b"", 0, (-1, 0)),
            (b"", 1, (-1, 0)),
            (b"cmd", 0, (-1, 0)),
            (b"cmd", 1, (-1, 0)),
            (b"cmd one", 1, (4, 3)),
            (b"cmd one", 2, (-1, 0)),
            (b"cmd  one   two ", 1, (5, 3)),
            (b"cmd  one   two ", 2, (11, 3)),
            (b"cmd  one   two ", 3, (-1, 0)),
            (b"   cmd value", 1, (3, 3)),
            (b"   cmd value", 2, (7, 5)),
            (b"cmd value   ", 2, (-1, 0)),
            (b"cmd\tone two", 1, (8, 3)),
            (b"cmd " + b"x" * 255, 1, (4, 255)),
            (b"cmd one", 0xFFFF_FFFF, (-1, 0)),
        )
        for raw, wanted, expected in cases:
            with self.subTest(raw=raw, wanted=wanted):
                candidate = self.invoke(self.candidate, raw, wanted)
                oracle = self.invoke(self.oracle, raw, wanted)
                self.assertEqual(candidate, oracle)
                self.assertEqual(candidate, expected)

    def test_bounded_input_space_is_exhaustively_differential(self) -> None:
        # Exhaust every string through six bytes over delimiter, ordinary,
        # and non-delimiter whitespace symbols.  The maximum 32-bit index is
        # included alongside all indices that can succeed in this corpus.
        alphabet = (b"a", b"b", b" ", b"\t")
        wanted_values = (0, 1, 2, 3, 4, 5, 6, 0xFFFF_FFFF)
        compared = 0
        for size in range(7):
            for symbols in itertools.product(alphabet, repeat=size):
                raw = b"".join(symbols)
                for wanted in wanted_values:
                    self.assertEqual(
                        self.invoke(self.candidate, raw, wanted),
                        self.invoke(self.oracle, raw, wanted),
                        (raw, wanted),
                    )
                    compared += 1
        self.assertEqual(compared, 43_688)

    def test_128_byte_nonterminated_caller_hazard_has_safe_backing_witness(self) -> None:
        # The first 128 bytes model the logical G2 console array.  Bytes 128
        # and 129 are deliberately allocated witness backing, so this test
        # characterizes the stock over-read contract without performing an
        # out-of-bounds host access.
        backing = ctypes.create_string_buffer(130)
        ctypes.memset(backing, ord("A"), 127)
        backing[127] = b" "
        backing[128] = b"Z"
        backing[129] = b"\0"
        for function in (self.candidate, self.oracle):
            length = ctypes.c_int32(-1)
            offset = int(function(backing, 1, ctypes.byref(length)))
            self.assertEqual((offset, int(length.value)), (128, 1))

        start, end = INPUT_LIMIT_WINDOW
        window = self.span(start, end)
        self.assertEqual(len(window), 24)
        self.assertEqual(sha256(window), INPUT_LIMIT_WINDOW_SHA256)
        self.assertEqual(
            window.hex(),
            "2000c0b28028c3da9df8000019492200d2b28854641cbbe7",
        )

    def test_official_body_predecessor_successor_and_fallthrough_are_exact(self) -> None:
        self.assertEqual(len(self.package), PACKAGE_SIZE)
        self.assertEqual(sha256(self.package), PACKAGE_SHA256)
        self.assertEqual(sha256(self.application), APPLICATION_SHA256)

        stock = self.span(START, END)
        self.assertEqual(len(stock), 100)
        self.assertEqual(stock.hex(), STOCK_BYTES)
        self.assertEqual(sha256(stock), STOCK_SHA256)
        predecessor = self.span(PREDECESSOR_TAIL_START, START)
        self.assertEqual(predecessor.hex(), PREDECESSOR_TAIL_BYTES)
        self.assertEqual(sha256(predecessor), PREDECESSOR_TAIL_SHA256)
        successor = self.span(END, SUCCESSOR_END)
        self.assertEqual(len(successor), 46)
        self.assertEqual(sha256(successor), SUCCESSOR_SHA256)

        # Predecessor returns with POP.W {...,pc}; candidate returns with BX
        # LR; successor starts a new function with PUSH {r4,lr}.
        self.assertEqual(predecessor[-4:].hex(), "bde8f087")
        self.assertEqual(stock[-2:].hex(), "7047")
        self.assertEqual(successor[:2].hex(), "10b5")

        outgoing = []
        for offset in range(0, len(stock) - 3, 2):
            address = START + offset
            for link in (True, False):
                target = wide_branch_target(self.application, address, link=link)
                if target is not None and not START <= target < END:
                    outgoing.append((address, target, link))
            target = wide_conditional_target(self.application, address)
            if target is not None and not START <= target < END:
                outgoing.append((address, target, "conditional"))
        for offset in range(0, len(stock), 2):
            address = START + offset
            halfword = struct.unpack_from("<H", stock, offset)[0]
            for target in narrow_targets(address, halfword):
                if not START <= target < END:
                    outgoing.append((address, target, halfword))
        self.assertEqual(outgoing, [])

    def test_all_115_callers_and_every_external_branch_ingress_are_closed(self) -> None:
        direct_bl = []
        direct_bw = []
        wide_conditional_entries = []
        external_interiors = []
        for offset in range(0, len(self.application) - 3, 2):
            address = BASE + offset
            encoding = self.application[offset:offset + 4]
            for link in (True, False):
                target = wide_branch_target(self.application, address, link=link)
                if target == START:
                    (direct_bl if link else direct_bw).append(
                        (address, encoding)
                    )
                if (
                    target is not None
                    and START < target < END
                    and not START <= address < END
                ):
                    external_interiors.append((address, target, link))
            target = wide_conditional_target(self.application, address)
            if target == START and not START <= address < END:
                wide_conditional_entries.append(address)
            if (
                target is not None
                and START < target < END
                and not START <= address < END
            ):
                external_interiors.append((address, target, "conditional"))

        narrow_entries = []
        narrow_interiors = []
        for offset in range(0, len(self.application) - 1, 2):
            address = BASE + offset
            halfword = struct.unpack_from("<H", self.application, offset)[0]
            for target in narrow_targets(address, halfword):
                if target == START and not START <= address < END:
                    narrow_entries.append((address, halfword))
                if (
                    START < target < END
                    and not START <= address < END
                ):
                    narrow_interiors.append((address, target, halfword))

        self.assertEqual(tuple(address for address, _ in direct_bl), CALLERS)
        self.assertEqual(len(direct_bl), 115)
        caller_addresses = b"".join(
            struct.pack("<I", address) for address, _ in direct_bl
        )
        caller_records = b"".join(
            struct.pack("<I", address) + encoding
            for address, encoding in direct_bl
        )
        self.assertEqual(sha256(caller_addresses), CALLER_ADDRESS_SHA256)
        self.assertEqual(sha256(caller_records), CALLER_RECORD_SHA256)
        self.assertEqual(direct_bw, [])
        self.assertEqual(wide_conditional_entries, [])
        self.assertEqual(external_interiors, [])
        self.assertEqual(narrow_entries, [])
        self.assertEqual(narrow_interiors, [])

    def test_every_caller_window_has_statically_closed_r1_and_r2_setup(self) -> None:
        # Each canonical record contains the call address, 16 bounded bytes
        # preceding it, and the four-byte BL.  This catches drift in argument
        # setup even when a call continues to resolve to the same entry.
        window_records = []
        window_digest_records = []
        classifications = []
        unresolved = []
        for call in CALLERS:
            window = self.span(call - CALLER_PRE_CALL_BYTES, call + 4)
            self.assertEqual(len(window), CALLER_PRE_CALL_BYTES + 4)
            self.assertEqual(
                wide_branch_target(self.application, call, link=True),
                START,
            )
            window_records.append(struct.pack("<I", call) + window)
            window_digest_records.append(
                struct.pack("<I", call)
                + bytes.fromhex(sha256(window))
            )

            # All stock R2 setups in the final eight bytes use either
            # MOV R2,SP or ADD R2,SP,#imm.  Both produce an aligned writable
            # word in the active caller stack frame.
            suffix = self.span(call - 8, call)
            r2_setups = []
            immediate_r1_setups = []
            for offset in range(0, len(suffix), 2):
                halfword = struct.unpack_from("<H", suffix, offset)[0]
                if halfword == 0x466A:
                    r2_setups.append((offset, 0))
                elif halfword & 0xFF00 == 0xAA00:
                    r2_setups.append((offset, (halfword & 0xFF) * 4))
                if halfword & 0xFF00 == 0x2100:
                    immediate_r1_setups.append((offset, halfword & 0xFF))
            if len(r2_setups) != 1:
                unresolved.append((call, "R2", suffix))
                continue
            r2_position, stack_offset = r2_setups[0]
            self.assertEqual(stack_offset % 4, 0)

            if call in DYNAMIC_INDEX_PROOFS:
                _, _, index_low, index_high, _ = DYNAMIC_INDEX_PROOFS[call]
                if call == 0x0058_191A:
                    r1_encoding = bytes.fromhex("19f10301")
                else:
                    r1_encoding = bytes.fromhex("e11c")
                r1_position = suffix.find(r1_encoding)
                if r1_position < 0:
                    unresolved.append((call, "R1-dynamic", suffix))
                    continue
            else:
                if not immediate_r1_setups:
                    unresolved.append((call, "R1-immediate", suffix))
                    continue
                r1_position, index_low = immediate_r1_setups[-1]
                index_high = index_low
            self.assertLess(r2_position, r1_position)
            classifications.append(
                (call, index_low, index_high, stack_offset)
            )

        self.assertEqual(unresolved, [])
        self.assertEqual(len(window_records), 115)
        self.assertEqual(
            sha256(b"".join(window_records)),
            CALLER_WINDOW_RECORD_SHA256,
        )
        self.assertEqual(
            sha256(b"".join(window_digest_records)),
            CALLER_WINDOW_DIGEST_RECORD_SHA256,
        )
        classification_stream = b"".join(
            struct.pack("<IIII", *record) for record in classifications
        )
        self.assertEqual(
            sha256(classification_stream),
            CALLER_ABI_CLASSIFICATION_SHA256,
        )
        self.assertEqual(
            tuple(sorted(Counter(
                (low, high) for _, low, high, _ in classifications
            ).items())),
            CALLER_INDEX_HISTOGRAM,
        )
        self.assertEqual(
            tuple(sorted(Counter(
                offset for *_, offset in classifications
            ).items())),
            CALLER_R2_STACK_OFFSET_HISTOGRAM,
        )
        self.assertEqual(max(high for _, _, high, _ in classifications), 11)
        self.assertEqual(
            [call for call, _, high, _ in classifications if high == 11],
            [0x0058_0B14],
        )
        self.assertEqual(R0_PROVENANCE_CLOSED_CALLERS, CALLERS)
        self.assertEqual(STOCK_TERMINATION_RISK_CALLERS, CALLERS)

    def test_four_dynamic_index_callers_have_exact_static_bounds(self) -> None:
        for call, (start, end, low, high, digest) in DYNAMIC_INDEX_PROOFS.items():
            with self.subTest(call=hex(call)):
                window = self.span(start, end)
                self.assertEqual(end, call + 4)
                self.assertEqual(sha256(window), digest)
                self.assertLessEqual(1, low)
                self.assertLessEqual(low, high)

        # R4 begins at zero, is incremented, compared against three/nine,
        # and contributes R1=R4+3 at the first three dynamic sites.
        self.assertEqual(
            self.span(0x0058_0A70, 0x0058_0A7C).hex(),
            "641c032c0bd204aae11c2800",
        )
        self.assertEqual(
            self.span(0x0058_0ABC, 0x0058_0AC8).hex(),
            "641c032c0bd204aae11c2800",
        )
        self.assertEqual(
            self.span(0x0058_0B08, 0x0058_0B14).hex(),
            "641c092c0bd204aae11c2800",
        )

        # The fourth site clamps R8 to 0..5, initializes SB to zero, then
        # requests R1=SB+3 while SB<R8: its complete request range is 3..7.
        self.assertEqual(
            self.span(0x0058_18CA, 0x0058_18E0).hex(),
            "8046b8f1000f01d55ff00008b8f1060f01db5ff00508",
        )
        self.assertEqual(
            self.span(0x0058_18FA, 0x0058_1900).hex(),
            "5ff0000906e0",
        )
        self.assertEqual(
            self.span(0x0058_190A, 0x0058_191A).hex(),
            "19f10109c1450fda01aa19f103013000",
        )

    def test_all_115_r0_values_trace_to_registered_callback_input(self) -> None:
        abi = self.cli_report["abi"]
        self.assertEqual(
            abi["callback_arguments"],
            ["char *output", "uint32_t output_len", "const char *input"],
        )
        descriptors = {
            item["callback"] & ~1: item["command"]
            for item in self.cli_report["vendor_glue"]["commands"]
        }

        group_stream = bytearray()
        prefix_stream = bytearray()
        binding_stream = bytearray()
        grouped_calls = []
        handler_sources = Counter()
        call_sources = Counter()
        for entry, command, source, calls in R0_HANDLER_GROUPS:
            self.assertEqual(descriptors[entry], command)
            self.assertGreaterEqual(len(calls), 1)
            self.assertEqual(tuple(sorted(calls)), calls)

            source_code = R0_SOURCE_CODES[source]
            command_bytes = command.encode("ascii")
            group_stream.extend(
                struct.pack("<IBB", entry, source_code, len(command_bytes))
            )
            group_stream.extend(command_bytes)
            group_stream.extend(struct.pack("<B", len(calls)))
            group_stream.extend(
                b"".join(struct.pack("<I", call) for call in calls)
            )

            prefix = self.span(entry, calls[0] + 4)
            prefix_stream.extend(
                struct.pack("<III", entry, calls[0], len(prefix)) + prefix
            )
            self.assertIn(
                R0_INPUT_BINDINGS[source],
                self.span(entry, min(entry + 16, calls[0])),
            )

            if source == "r0":
                if entry in R0_GUARDED_DIRECT_HANDLERS:
                    call = calls[0]
                    # The success BEQ skips the only R0 clobber and lands at
                    # the R2/R1 setup.  The clobber path branches to exit.
                    self.assertEqual(self.span(call - 12, call - 8).hex(), "012901d0")
                    conditional = struct.unpack(
                        "<H", self.span(call - 10, call - 8)
                    )[0]
                    self.assertEqual(
                        narrow_targets(call - 10, conditional),
                        (call - 4,),
                    )
                    self.assertEqual(self.span(call - 8, call - 6).hex(), "0020")
                    exit_branch = struct.unpack(
                        "<H", self.span(call - 6, call - 4)
                    )[0]
                    self.assertGreater(narrow_targets(call - 6, exit_branch)[0], call)
                    self.assertEqual(self.span(call - 2, call).hex(), "0121")
                else:
                    self.assertLessEqual(calls[0] - entry, 14)
            else:
                for call in calls:
                    self.assertEqual(
                        self.span(call - 2, call),
                        R0_CALL_RELOADS[source],
                    )

            for call in calls:
                grouped_calls.append(call)
                call_sources[source] += 1
                binding_stream.extend(
                    struct.pack("<IB", call, source_code)
                    + self.span(call - 2, call)
                )
            handler_sources[source] += 1

        self.assertEqual(len(R0_HANDLER_GROUPS), 55)
        self.assertEqual(tuple(grouped_calls), CALLERS)
        self.assertEqual(
            handler_sources,
            Counter({"r0": 26, "r4": 20, "r6": 4, "r5": 3, "r8": 1, "r7": 1}),
        )
        self.assertEqual(
            call_sources,
            Counter({"r4": 42, "r0": 26, "r5": 18, "r6": 16, "r7": 7, "r8": 6}),
        )
        self.assertEqual(sha256(bytes(group_stream)), R0_HANDLER_GROUP_SHA256)
        self.assertEqual(sha256(bytes(prefix_stream)), R0_HANDLER_PREFIX_SHA256)
        self.assertEqual(sha256(bytes(binding_stream)), R0_CALL_BINDING_SHA256)

    def test_single_process_dispatch_preserves_console_input_through_callback_r2(self) -> None:
        self.assertEqual(
            self.cli_analyzer.thumb_bl_calls_to(self.package, PROCESS_ENTRY),
            [PROCESS_CALL],
        )
        self.assertEqual(
            self.span(0x0054_1664, 0x0054_1672).hex(),
            "434e444d80223100280043f0c6f8",
        )
        self.assertEqual(
            self.span(0x0058_47FE, 0x0058_4808).hex(),
            "2de9f04705000e001700",
        )
        start, end = PROCESS_CALLBACK_WINDOW
        callback = self.span(start, end)
        self.assertEqual(sha256(callback), PROCESS_CALLBACK_WINDOW_SHA256)
        self.assertEqual(
            callback.hex(),
            "d8f8000000280ed02a0039003000d8f800301b689b689847",
        )
        # ProcessCommand preserves its R0/R1/R2 as R5/R6/R7.  The indirect
        # callback dispatch restores output/length/input as R0/R1/R2.
        self.assertEqual(self.span(0x0058_48AC, 0x0058_48B2).hex(), "2a0039003000")
        self.assertEqual(
            self.cli_analyzer.u32(self.package, CONSOLE_INPUT_LITERAL[0]),
            CONSOLE_INPUT_LITERAL[1],
        )
        self.assertEqual(
            self.cli_analyzer.u32(self.package, CONSOLE_OUTPUT_LITERAL[0]),
            CONSOLE_OUTPUT_LITERAL[1],
        )

    def test_console_collector_exact_full_line_hazard_and_minimal_patch_are_closed(self) -> None:
        for (start, end), digest in (
            (CONSOLE_TASK, CONSOLE_TASK_SHA256),
            (CONSOLE_COLLECT_DISPATCH, CONSOLE_COLLECT_DISPATCH_SHA256),
            (CONSOLE_PROCESS_AND_FULL_CLEAR, CONSOLE_PROCESS_AND_FULL_CLEAR_SHA256),
            (CONSOLE_CONTROL_WINDOW, CONSOLE_CONTROL_WINDOW_SHA256),
            (CONSOLE_BACKSPACE_WINDOW, CONSOLE_BACKSPACE_WINDOW_SHA256),
            (CONSOLE_INPUT_CLEAR, CONSOLE_INPUT_CLEAR_SHA256),
        ):
            with self.subTest(start=hex(start), end=hex(end)):
                self.assertEqual(sha256(self.span(start, end)), digest)

        task_start, task_end = CONSOLE_TASK
        task = self.span(task_start, task_end)
        self.assertEqual(len(task), 284)
        self.assertEqual(wide_branch_target(self.application, PROCESS_CALL, link=True), PROCESS_ENTRY)
        self.assertEqual(
            wide_branch_target(self.application, 0x0054_1690, link=True),
            0x0043_C0E4,
        )
        self.assertEqual(
            self.cli_analyzer.u32(self.package, CONSOLE_TASK_POINTER[0]),
            CONSOLE_TASK_POINTER[1],
        )
        self.assertEqual(
            self.cli_analyzer.u32(self.package, CONSOLE_ADJACENT_OBJECT[0]),
            CONSOLE_ADJACENT_OBJECT[1],
        )

        input_pointer_hits = []
        for offset in range(0, len(self.application) - 3):
            if struct.unpack_from("<I", self.application, offset)[0] == CONSOLE_INPUT_LITERAL[1]:
                input_pointer_hits.append(BASE + offset)
        self.assertEqual(input_pointer_hits, [CONSOLE_INPUT_LITERAL[0]])

        patch_address, stock_compare, safe_compare = COLLECTOR_CAPACITY_PATCH
        self.assertEqual(self.span(patch_address, patch_address + 2), stock_compare)
        # This is one complete Thumb instruction reached only by fallthrough:
        # MOV R0,R4; UXTB R0,R0; CMP; then the unchanged BGE back to the
        # receive loop.  No direct branch can bypass the producer instructions
        # and enter at the replacement halfword.
        self.assertEqual(
            self.span(patch_address - 4, patch_address + 4).hex(),
            "2000c0b28028c3da",
        )
        capacity_branch = struct.unpack(
            "<H", self.span(patch_address + 2, patch_address + 4)
        )[0]
        self.assertEqual(
            narrow_targets(patch_address + 2, capacity_branch),
            (0x0054_1694,),
        )
        patch_ingress = []
        for offset in range(0, len(self.application) - 3, 2):
            address = BASE + offset
            for link in (True, False):
                if wide_branch_target(self.application, address, link=link) == patch_address:
                    patch_ingress.append((address, link))
            if wide_conditional_target(self.application, address) == patch_address:
                patch_ingress.append((address, "conditional"))
        for offset in range(0, len(self.application) - 1, 2):
            address = BASE + offset
            halfword = struct.unpack_from("<H", self.application, offset)[0]
            if patch_address in narrow_targets(address, halfword):
                patch_ingress.append((address, halfword))
        self.assertEqual(patch_ingress, [])

        hardened = bytearray(task)
        hardened[patch_address - task_start:patch_address - task_start + 2] = safe_compare
        self.assertEqual(sha256(hardened), HARDENED_CONSOLE_TASK_SHA256)

        def append(buffer: bytearray, length: int, value: int, limit: int) -> int:
            index = length & 0xFF
            if index >= limit:
                return length
            buffer[index] = value
            return length + 1

        for payload_size in range(128):
            stock_buffer = bytearray(128)
            safe_buffer = bytearray(128)
            stock_length = safe_length = 0
            for _ in range(payload_size):
                stock_length = append(stock_buffer, stock_length, ord("A"), 128)
                safe_length = append(safe_buffer, safe_length, ord("A"), 127)
            self.assertEqual((safe_buffer, safe_length), (stock_buffer, stock_length))
            self.assertEqual(safe_buffer[safe_length], 0)

        stock_buffer = bytearray(128)
        safe_buffer = bytearray(128)
        stock_length = safe_length = 0
        for _ in range(128):
            stock_length = append(stock_buffer, stock_length, ord("A"), 128)
            safe_length = append(safe_buffer, safe_length, ord("A"), 127)
        self.assertEqual(stock_length, 128)
        self.assertNotIn(0, stock_buffer)
        self.assertEqual(safe_length, 127)
        self.assertEqual(safe_buffer[127], 0)

        # The exact stock backspace path decrements a nonzero length and
        # writes NUL at the new index, so backing out of full state is safe.
        stock_length -= 1
        stock_buffer[stock_length & 0xFF] = 0
        self.assertEqual(stock_length, 127)
        self.assertEqual(stock_buffer[127], 0)

    def test_startup_scatter_zeroes_the_console_input_before_first_command(self) -> None:
        startup_address, startup = STARTUP_ZERO_GATE
        self.assertEqual(self.span(startup_address, startup_address + len(startup)), startup)
        self.assertEqual(sha256(startup), STARTUP_ZERO_GATE_SHA256)
        self.assertEqual(
            wide_branch_target(self.application, 0x005E_4294, link=True),
            startup_address,
        )
        call_address, call_window = STARTUP_SCATTER_CALL_WINDOW
        self.assertEqual(self.span(call_address, call_address + len(call_window)), call_window)
        self.assertEqual(
            wide_branch_target(self.application, 0x005E_429C, link=True),
            0x005E_42B4,
        )

        record_start, record_end = SCATTER_ZERO_RECORD
        record = self.span(record_start, record_end)
        self.assertEqual(sha256(record), SCATTER_ZERO_RECORD_SHA256)
        handler_relative, byte_count, destination = struct.unpack_from(
            "<iII", record, 0
        )
        self.assertEqual(
            (record_start + handler_relative) & ~1,
            SCATTER_ZERO_HANDLER[0],
        )
        self.assertEqual(
            (destination, destination + byte_count),
            SCATTER_ZERO_RANGE,
        )
        self.assertLessEqual(destination, CONSOLE_INPUT_LITERAL[1])
        self.assertGreaterEqual(
            destination + byte_count,
            CONSOLE_INPUT_LITERAL[1] + 128,
        )

        handler_start, handler_end = SCATTER_ZERO_HANDLER
        handler = self.span(handler_start, handler_end)
        self.assertEqual(len(handler), 56)
        self.assertEqual(sha256(handler), SCATTER_ZERO_HANDLER_SHA256)

    def test_stored_pointer_scan_records_and_classifies_the_only_collision(self) -> None:
        collisions = []
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            if START <= (value & ~1) < END:
                collisions.append((BASE + offset, value))
        self.assertEqual(collisions, [STORED_VALUE_COLLISION])
        self.assertEqual(STORED_VALUE_COLLISION[0] % 4, 2)
        self.assertEqual(STORED_VALUE_COLLISION[1] & 1, 0)
        self.assertEqual(
            [item for item in collisions if item[0] % 4 == 0],
            [],
        )
        self.assertEqual(
            [item for item in collisions if item[1] & 1],
            [],
        )
        string_start, expected = STORED_VALUE_STRING
        raw = self.application[string_start - BASE:]
        self.assertEqual(raw[:raw.index(b"\0")], expected)
        collision_offset = STORED_VALUE_COLLISION[0] - BASE
        self.assertEqual(
            self.application[collision_offset:collision_offset + 4],
            b"RIX\0",
        )

    def test_maximum_parameter_index_11_call_window_is_exact(self) -> None:
        start, end = MAX_INDEX_WINDOW
        window = self.span(start, end)
        self.assertEqual(len(window), 40)
        self.assertEqual(sha256(window), MAX_INDEX_WINDOW_SHA256)
        self.assertEqual(wide_branch_target(self.application, 0x0058_0B14, link=True), START)
        # r4 starts at zero, increments, is required to be below nine, then
        # R1 is formed as r4 + 3: the requests are exactly indices 3..11.
        self.assertEqual(self.span(0x0058_0B08, 0x0058_0B0E).hex(), "641c092c0bd2")
        self.assertEqual(self.span(0x0058_0B10, 0x0058_0B12).hex(), "e11c")

    def test_target_function_object_relocation_and_exidx_are_strictly_pinned(self) -> None:
        profile = TARGET_PROFILES[self.profile]
        self.assertEqual(self.compiler_version, profile["version"])
        object_records = [
            (path.stat().st_size, sha256(path)) for path in self.target_objects
        ]
        self.assertEqual(object_records, [profile["object"], profile["object"]])

        text = self.apollo_overlay.section_named(self.sections, FUNCTION_SECTION)
        body = self.object_data[
            int(text["offset"]):int(text["offset"]) + int(text["size"])
        ]
        self.assertEqual(
            (len(body), int(text["alignment"]), sha256(body)),
            profile["function"],
        )
        self.assertEqual(body.hex(), TARGET_FUNCTION_HEX)
        self.assertEqual(int(text["type"]), 1)
        self.assertEqual(int(text["flags"]), 0x6)

        executable = [
            section["name"]
            for section in self.sections
            if int(section["size"]) > 0 and int(section["flags"]) & 0x4
        ]
        self.assertEqual(executable, [FUNCTION_SECTION])
        writable_allocated = [
            section["name"]
            for section in self.sections
            if int(section["size"]) > 0
            and int(section["flags"]) & 0x2
            and int(section["flags"]) & 0x1
        ]
        self.assertEqual(writable_allocated, [])

        function_symbols = [
            fields
            for name, fields in self.symbols
            if name == FUNCTION
        ]
        self.assertEqual(len(function_symbols), 1)
        symbol = function_symbols[0]
        self.assertEqual(symbol[1] & 1, 1)
        self.assertEqual(symbol[2], profile["function"][0])
        self.assertEqual(symbol[3] >> 4, 1)
        self.assertEqual(symbol[3] & 0x0F, 2)
        self.assertEqual(symbol[5], int(text["index"]))
        undefined = [
            name for name, fields in self.symbols
            if name and fields[5] == 0
        ]
        self.assertEqual(undefined, [])

        exidx = self.apollo_overlay.section_named(self.sections, EXIDX_SECTION)
        exidx_bytes = self.object_data[
            int(exidx["offset"]):int(exidx["offset"]) + int(exidx["size"])
        ]
        self.assertEqual(exidx_bytes, EXIDX_BYTES)
        self.assertEqual((len(exidx_bytes), sha256(exidx_bytes)), profile["exidx"])
        self.assertEqual(struct.unpack_from("<I", exidx_bytes, 4)[0], 1)
        self.assertEqual(
            self.relocations,
            [
                (
                    ".rel" + EXIDX_SECTION,
                    EXIDX_SECTION,
                    0,
                    42,
                    "",
                    int(text["index"]),
                )
            ],
        )
        self.assertFalse(any(target == FUNCTION_SECTION for _, target, *_ in self.relocations))

    def test_collector_capacity_fragment_is_exact_relocation_free_thumb_text(self) -> None:
        extracted = []
        reports = []
        for path in self.capacity_patch_objects:
            body, report = self.apollo_overlay.extract_isolated_function_section(
                path,
                CAPACITY_PATCH_FUNCTION,
            )
            extracted.append(body)
            reports.append(report)

        expected = bytes.fromhex(CAPACITY_PATCH_HEX)
        self.assertEqual(extracted, [expected, expected])
        self.assertEqual(sha256(expected), CAPACITY_PATCH_SHA256)
        self.assertEqual(reports[0], reports[1])
        self.assertEqual(
            reports[0],
            {
                "function": CAPACITY_PATCH_FUNCTION,
                "section": ".text." + CAPACITY_PATCH_FUNCTION,
                "size": 2,
                "sha256": CAPACITY_PATCH_SHA256,
                "alignment": 2,
                "relocation_count": 0,
                "discarded_alloc_section_count": 0,
                "discarded_alloc_section_bytes": 0,
                "discarded_alloc_sections": [],
            },
        )

    def test_candidate_is_absent_from_every_production_registration(self) -> None:
        forbidden = (
            SOURCE.name,
            HEADER.name,
            FUNCTION,
            SOURCE.relative_to(ROOT).as_posix(),
        )
        production = [OVERLAY, MAKEFILE]
        production.extend(
            path for path in MANIFESTS.rglob("*") if path.is_file()
        )
        for path in production:
            text = path.read_text(encoding="utf-8")
            for token in forbidden:
                with self.subTest(path=path, token=token):
                    self.assertNotIn(token, text)
        overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
        self.assertNotIn(FUNCTION, overlay["functions"])
        self.assertFalse(any(
            item.get("target_function") == FUNCTION
            for item in overlay["patch_sites"]
        ))
        promoted_entry_sites = [
            item
            for item in overlay["patch_sites"]
            if item.get("runtime_address") == START
        ]
        self.assertEqual(
            [
                (item["name"], item["target_function"])
                for item in promoted_entry_sites
            ],
            [("replace_freertos_cli_get_parameter", PRODUCTION_FUNCTION)],
        )

    def test_candidate_audit_records_exclusion_and_completed_promotion(self) -> None:
        text = AUDIT.read_text(encoding="utf-8")
        for token in (
            "[0x005848FC,0x00584960)",
            "115",
            "0x00580B14",
            "NON_INVERTIBLE_MATRIX",
            "R_ARM_PREL31",
            "CANTUNWIND",
            "production-excluded",
            "128-byte logical boundary",
            "R0 provenance is now closed for all 115 calls",
            "0x00541708",
            "Accessor promotion remains complete and fail-closed",
            "5598cb1f2a3b9a8b6101f61afcc5e24de54b01c3d5aa45396bf161344b3618bb",
            "No hardware",
        ):
            self.assertIn(token, text)

    def test_mutations_fail_closed_without_exercising_undefined_host_input(self) -> None:
        changed = bytearray(self.span(START, END))
        changed[len(changed) // 2] ^= 1
        self.assertNotEqual(sha256(changed), STOCK_SHA256)

        source = SOURCE.read_bytes()
        self.assertNotEqual(sha256(source + b"\n"), LOCAL_PINS[SOURCE][1])
        self.assertNotEqual(len(source) + 1, LOCAL_PINS[SOURCE][0])

        # The hazard test above uses 130 allocated bytes.  Do not add a test
        # that passes an actually unterminated 128-byte allocation to either
        # implementation; that would invoke the very undefined read being
        # characterized.
        self.assertIn(
            "performs no independent bounds check",
            HEADER.read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
