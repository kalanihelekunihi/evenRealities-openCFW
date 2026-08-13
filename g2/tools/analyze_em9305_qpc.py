#!/usr/bin/env python3
"""Fail-closed QP/C provenance audit for the stock EM9305 controller image."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = ROOT / "blobs/official/g2-2.2.6.10/firmware_ble_em9305.bin"
IMAGE_SIZE = 211_948
IMAGE_SHA256 = "91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9"
PACKAGE_MAP_BASE = 0x0030_1FDC
APP_FILE_OFFSET = 0x424
APP_BASE = 0x0030_2400
APP_END = 0x0033_5BC8
APP_SHA256 = "0de6e945a56ec886a92e44d4eaefe02fbca6db11f8747876e30bffb45cffce03"

MODULES = (
    ("MyApp", 0x0033_4514),
    ("qk", 0x0033_451C),
    ("qf_dyn", 0x0033_4520),
    ("qf_act", 0x0033_4528),
    ("qep_hsm", 0x0033_4530),
    ("qf_actq", 0x0033_4538),
    ("qf_mem", 0x0033_4540),
    ("WsfOs", 0x0033_4548),
)
MODULE_TABLE = (
    0x0033_4514,
    0x0033_4550,
    "781612bc1eedf1760f7edb368325fb83cc2ecc88fbe042aeb678e2804da6805b",
)
QPC_CLUSTER = (
    0x0031_0C00,
    0x0031_17EC,
    "9c5803cd925d3b575e05f7fed8b1d6c42eaac000368fc191d2092c71c65b65da",
)
QK_ACTIVATE_CANDIDATE = (
    0x0031_1554,
    0x0031_15E4,
    "844ab98ae09414027139ea278dc2cf5ae92757eed0fb7cda0d25efd06b898e2c",
)
QACTIVE_POST_CANDIDATE = (
    0x0031_0E28,
    0x0031_0EE4,
    "7b97ff5fc12c7d8504c997bc6ab414aa756a5fd9e10af97e775ffc83bad8127d",
)
QK_IDLE_POWER_MANAGER = (
    0x0031_26E0,
    0x0031_28E4,
    "3a2edcd4b08f74c6cc592a19916938ff1a96216555d0b1ca055ebb1a90366f4a",
)
QK_PORT_CLUSTER = (
    0x0030_2518,
    0x0030_2664,
    "176b59324b400252aee4955eebb6e7cc8f5899a98592fe41010478170178a3e9",
)
PROT_TIMER_SET_HW_TRIGGER_ENABLE = (
    0x0031_0BE0,
    0x0031_0C08,
    "d35349294b8affe439537a98d627f4bcea3543e3d32b71cc5e00cf51dbdb574b",
)
SLEEP_MANAGER_RCCAL_CALLBACK = (
    0x0031_28E4,
    0x0031_2918,
    "44956422195791d75f34b28115b61b7fe344318d5c00e71f0bf3f0cc477cdef5",
)
QK_IDLE_POWER_MANAGER_CALL = (0x0031_1610, 0x0031_26E0, "d2088000")
Q_ON_ASSERT_EXT = (
    0x0031_17E8,
    0x0031_17F8,
    "2deea6b7a791969cebd7a54d6da705031b568ae3bfc5bdce8bd0a7e338813727",
)
HOOK_POINTER_TABLE = (
    0x0033_5B94,
    0x0033_5BB8,
    "1370d2789d143388ecbd5c84edf4dfaaaf2c059ff69ec59e0f68ff0df0514b51",
)
HOOK_POINTERS = (
    ("vendor_resume_extension", 0x0030_EB8C),
    ("vendor_startup_extension", 0x0030_ECF8),
    ("QF_onResumeExt", 0x0031_114C),
    ("QF_onResumeInternalHook", 0x0031_1150),
    ("QF_onStartupExt", 0x0031_11A0),
    ("QF_onStartupInternalHook", 0x0031_11A4),
    ("QK_onIdleExt", 0x0031_161C),
    ("QK_onIdleInternalHook", 0x0031_1620),
    ("Q_onAssertExt", 0x0031_17E8),
)
CALLBACK_GLOBALS = {
    "gQF_onResumeExt": 0x0080_FE04,
    "gQF_onResumeInternalHook": 0x0080_FE08,
    "gQF_onStartupExt": 0x0080_FE0C,
    "gQF_onStartupInternalHook": 0x0080_FE10,
    "gQK_onIdleExt": 0x0080_FE14,
    "gQK_onIdleInternalHook": 0x0080_FE18,
    "gQ_onAssertExt": 0x0080_FE1C,
}
SDK_IDENTIFIED_FUNCTIONS = (
    # name, start, end, SHA-256, comparison state
    ("qkPortDummy", 0x00302518, 0x0030251C, "2e7fd7b5f00443c190d8da5eebe59c152a2e443091ddecc1f1e4b45ec1657024", "sdk_archive_exact_stock_retained"),
    ("IRQHandler_SWI0", 0x0030251C, 0x003025CE, "81e73e4d8f99277cb85946d38385783ba56b21799802725baa3fa856a3b394b7", "sdk_archive_exact_relocation_normalized_stock_retained"),
    ("QK_noPreemption", 0x003025D0, 0x003025DC, "224b69a9694b70940c1d2cbcddc95e0300a1145edda9d9c9d1dcf6be46e431b6", "sdk_archive_exact_stock_retained"),
    ("QK_restoreContext", 0x003025DC, 0x003025F6, "6dd6f29745d64ee9a95923c377a4beb3125a3c69cf4344fba88a39beadffaca4", "sdk_archive_exact_relocation_normalized_stock_retained"),
    ("IRQHandler_SWI1", 0x003025F8, 0x00302664, "0c6aed7c4510573166a2d799fc13534d19f52dcf88ebdc3f8725d7f592b42203", "sdk_archive_exact_stock_retained"),
    ("BSP_Init", 0x00302E80, 0x00302E8E, "603d7625823b10f1135cba6f7340bebea6f41fd66064c8e43da4604843e369b5", "sdk_archive_exact_stock_retained"),
    ("ProtTimer_SetHwTriggerEnable", 0x00310BE0, 0x00310C08, "d35349294b8affe439537a98d627f4bcea3543e3d32b71cc5e00cf51dbdb574b", "sdk_symbol_identified_vendor_modified_stock_retained"),
    ("ProtTimer_StoreConfig", 0x00310C08, 0x00310CEA, "bb01d2d97fa0e751dc69648a660ff23dd4acc36fa94ed180e605120493c4c0f1", "sdk_archive_exact_relocation_normalized_stock_retained"),
    ("ProtTimer_UpdateRestartTime", 0x00310CEC, 0x00310D18, "23675c6226a70a6c2e61e5bd988f3cd834174bc928aacd7d833be8340691e648", "sdk_archive_exact_relocation_normalized_stock_retained"),
    ("SLEEP_MANAGER_GoToSleep", 0x003126E0, 0x003128E4, "3a2edcd4b08f74c6cc592a19916938ff1a96216555d0b1ca055ebb1a90366f4a", "sdk_symbol_identified_vendor_configured_stock_retained"),
    ("SLEEP_MANAGER_RCCAL_Callback", 0x003128E4, 0x00312918, "44956422195791d75f34b28115b61b7fe344318d5c00e71f0bf3f0cc477cdef5", "sdk_archive_exact_relocation_normalized_stock_retained"),
)
ASSERT_HANDLER = 0x0031_17D8
ABSENT_PORTABLE_MODULE_STRINGS = (b"qf_time\0",)

# Twenty-two portable functions are now bounded through assertion IDs, vtable
# entries, direct-call topology, and object-field semantics. Alignment islands
# and the intervening vendor/port routines are deliberately excluded.
PORTABLE_FUNCTIONS = (
    # module, function, start, end, SHA-256
    ("qf_qact", "QActive_ctor", 0x00310D18, 0x00310D36, "2d2c9fa26180ae3469e08e2f4b8df666a70df8a7b100841031c2047857f041d1"),
    ("qf_actq", "QActive_get_", 0x00310D38, 0x00310D9E, "ac6e10996639006548882911215837668b4eecd61f2e54e33cf9682e419c885f"),
    ("qf_actq", "QActive_postLIFO_", 0x00310DA0, 0x00310E26, "16da468f413c6504456c976784e0f1fd7bf80a0b1927f45515303d133be9ff8e"),
    ("qf_actq", "QActive_post_", 0x00310E28, 0x00310EE4, "7b97ff5fc12c7d8504c997bc6ab414aa756a5fd9e10af97e775ffc83bad8127d"),
    ("qk", "QActive_start_", 0x00310EE4, 0x00310F5A, "e8540163650051435eef60be6e61393de2298b595ec41a0ce6c3a82a2326ba22"),
    ("qf_qeq", "QEQueue_init", 0x00310F5C, 0x00310F74, "455385f66072cf7e1939132ba2f3716b5789a1b2a4ff64cef5a05afb5a302243"),
    ("qf_act", "QF_add_", 0x00310F74, 0x00310FAA, "a803aeee9fc3b2f9bf0330c34245b5dacc32c775f567bcd901e61784ea8acb43"),
    ("qf_act", "QF_bzero", 0x00310FAC, 0x00310FB8, "5d459d510b9136f3bc1f9d6c08e5f0e55987d5dd71c509751f0b9c361396422e"),
    ("qf_dyn", "QF_gc", 0x00310FB8, 0x00311014, "001a064d42cd90b47c80cbdf61e67d5a97302471920cff0b1d9287e29bdf0888"),
    ("qk", "QF_init", 0x00311014, 0x0031105E, "7c2c6121563f5064d1b825d389a509c43179861edd0804a96e52f1ec5038a241"),
    ("qf_dyn", "QF_newX_", 0x00311060, 0x003110F2, "55759337c5340c61bf9f9e66f31a3073f0d610a70ca681dc7e23a19c31586ea5"),
    ("qf_dyn", "QF_poolInit", 0x003111A8, 0x00311216, "8ff8719eb0852c8f1084a38ba6c8b23f10cb2c7f11ffd130b9603e8c9405ffe0"),
    ("qk", "QF_run", 0x00311230, 0x0031125E, "277e58ff4a83447e1a40656c599b0c116490e024c9b419e541eddca30bc3ed96"),
    ("qep_hsm", "QHsm_ctor", 0x00311260, 0x00311274, "7b1d1a04edebb93068a017ec627eb6c448d9ee983e66a3ad9270f486568d717e"),
    ("qep_hsm", "QHsm_dispatch_", 0x00311274, 0x00311490, "550b43c7ada4f7bccc6cc3aa2d75c6fda943a1c9c253f8e239215c873c1f0291"),
    ("qep_hsm", "QHsm_init_", 0x00311490, 0x00311550, "31a67e19570ad09b2cd6ecf6c03276e24cabcb2a609b9fcdec31da8ffe6d1997"),
    ("qep_hsm", "QHsm_top", 0x00311550, 0x00311554, "983724828bc6035507b697719569e3c8cce215b0aadc28af9830ba7ee7847b65"),
    ("qk", "QK_activate_", 0x00311554, 0x003115E4, "844ab98ae09414027139ea278dc2cf5ae92757eed0fb7cda0d25efd06b898e2c"),
    ("qk", "QK_sched_", 0x00311634, 0x0031166C, "b6f3e65ef805f6b4e7dbe52ef652b95bea32067832c54f586d07a12f8cd49ce7"),
    ("qf_mem", "QMPool_get", 0x0031166C, 0x003116F4, "a8511b4d5b4ff89277fca7e818455f973750663beeef5af6dfb66195c5865ab2"),
    ("qf_mem", "QMPool_init", 0x003116F4, 0x00311798, "b4c6cf60e1f1105c7e51d8f597535f93301f1e7242ac352cd4b79b6cbccb3aa4"),
    ("qf_mem", "QMPool_put", 0x00311798, 0x003117D8, "e2e6562528771f82264fc7ac168a2200ea7a5184fb2fa0cc563bd87191f86e59"),
)

# Exact complement of PORTABLE_FUNCTIONS inside QPC_CLUSTER. These ranges keep
# uncertainty local: a recovered function boundary does not promote adjacent
# vendor code to portable QP/C, and padding remains distinguishable from code.
CLUSTER_REMAINDER_SEGMENTS = (
    # name, start, end, SHA-256, state
    ("prot_timer_set_hw_trigger_enable_tail", 0x00310C00, 0x00310C08, "cc066efe77cabad85a576326fa2e63f8f67674a05749427676f3ca2e66615c6c", "sdk_symbol_identified_vendor_modified_stock_retained"),
    ("prot_timer_store_config", 0x00310C08, 0x00310CEA, "bb01d2d97fa0e751dc69648a660ff23dd4acc36fa94ed180e605120493c4c0f1", "sdk_archive_exact_relocation_normalized_stock_retained"),
    ("alignment_00310cea", 0x00310CEA, 0x00310CEC, "ccf84481747c192349a30f8109c0a9bb223ace52c88de4e176315967424df8c2", "compiler_alignment_stock_retained"),
    ("prot_timer_update_restart_time", 0x00310CEC, 0x00310D18, "23675c6226a70a6c2e61e5bd988f3cd834174bc928aacd7d833be8340691e648", "sdk_archive_exact_relocation_normalized_stock_retained"),
    ("alignment_00310d36", 0x00310D36, 0x00310D38, "ccf84481747c192349a30f8109c0a9bb223ace52c88de4e176315967424df8c2", "compiler_alignment_stock_retained"),
    ("alignment_00310d9e", 0x00310D9E, 0x00310DA0, "ccf84481747c192349a30f8109c0a9bb223ace52c88de4e176315967424df8c2", "compiler_alignment_stock_retained"),
    ("alignment_00310e26", 0x00310E26, 0x00310E28, "ccf84481747c192349a30f8109c0a9bb223ace52c88de4e176315967424df8c2", "compiler_alignment_stock_retained"),
    ("alignment_00310f5a", 0x00310F5A, 0x00310F5C, "ccf84481747c192349a30f8109c0a9bb223ace52c88de4e176315967424df8c2", "compiler_alignment_stock_retained"),
    ("alignment_00310faa", 0x00310FAA, 0x00310FAC, "ccf84481747c192349a30f8109c0a9bb223ace52c88de4e176315967424df8c2", "compiler_alignment_stock_retained"),
    ("alignment_0031105e", 0x0031105E, 0x00311060, "ccf84481747c192349a30f8109c0a9bb223ace52c88de4e176315967424df8c2", "compiler_alignment_stock_retained"),
    ("alignment_003110f2", 0x003110F2, 0x003110F4, "ccf84481747c192349a30f8109c0a9bb223ace52c88de4e176315967424df8c2", "compiler_alignment_stock_retained"),
    ("qf_on_resume", 0x003110F4, 0x0031114C, "89542bf43e268d69a205340f917cb680faf5060f6ce8f2d3f0624832fb1b0e2f", "source_oracle_identified_partially_reverse_engineered_stock_retained"),
    ("qf_on_resume_ext", 0x0031114C, 0x00311150, "edfeb981f4b027bc93163843f0d3cb3bd46cf8ea6ad690caf387525ed1c8379f", "source_oracle_identified_stock_retained"),
    ("qf_on_resume_internal_hook", 0x00311150, 0x00311154, "7766b559c480d3129860a74a673038b9db4a622de9bb71c7957ee5e1837047de", "source_oracle_identified_stock_retained"),
    ("qf_on_startup", 0x00311154, 0x0031119E, "df9babba5234d1afd6e2d94ec8ab2dd60a2885f1ce137e382c283f357b0ba9db", "source_oracle_identified_partially_reverse_engineered_stock_retained"),
    ("alignment_0031119e", 0x0031119E, 0x003111A0, "ccf84481747c192349a30f8109c0a9bb223ace52c88de4e176315967424df8c2", "compiler_alignment_stock_retained"),
    ("qf_on_startup_ext", 0x003111A0, 0x003111A4, "edfeb981f4b027bc93163843f0d3cb3bd46cf8ea6ad690caf387525ed1c8379f", "source_oracle_identified_stock_retained"),
    ("qf_on_startup_internal_hook", 0x003111A4, 0x003111A8, "5c2ae05832a4449cd2bb20f41b843eb22dae95f3f95d0d30b0236e77ebcf5f1e", "source_oracle_identified_stock_retained"),
    ("alignment_00311216", 0x00311216, 0x00311218, "ccf84481747c192349a30f8109c0a9bb223ace52c88de4e176315967424df8c2", "compiler_alignment_stock_retained"),
    ("qf_resume", 0x00311218, 0x00311230, "79c59ee34198251f4fcbb0108ccc99c05a04e81029ea60e597c7333b997d5146", "source_oracle_identified_stock_retained"),
    ("alignment_0031125e", 0x0031125E, 0x00311260, "ccf84481747c192349a30f8109c0a9bb223ace52c88de4e176315967424df8c2", "compiler_alignment_stock_retained"),
    ("qk_on_idle", 0x003115E4, 0x0031161C, "483a78c9aaaae0415c9eb3c2e213a4b46da85030342e04e0f9dc597c97e340e5", "source_oracle_identified_partially_reverse_engineered_stock_retained"),
    ("qk_on_idle_ext", 0x0031161C, 0x00311620, "edfeb981f4b027bc93163843f0d3cb3bd46cf8ea6ad690caf387525ed1c8379f", "source_oracle_identified_stock_retained"),
    ("qk_on_idle_internal_hook", 0x00311620, 0x00311634, "fbb0316db14f6fc107f338a4cbf5852049003c2def1230d9f5e117e7a0a2abe4", "source_oracle_identified_partially_reverse_engineered_stock_retained"),
    ("q_on_assert", 0x003117D8, 0x003117E8, "fd33c8f3f22dc8b98020d17c59a47a0d3a069a87c3f63974fcf46c7946b6a582", "source_oracle_identified_fully_reverse_engineered_stock_retained"),
    ("q_on_assert_ext_prefix", 0x003117E8, 0x003117EC, "6695a9b36d9b56eb8d62e8a52c22ee8dbf4ba520be45d0361d93951abf5e9439", "source_oracle_identified_boundary_stock_retained"),
)

# ARCv2 EM uses halfword-oriented instruction encoding.  In particular, the
# six-byte short-register/long-immediate form is decoded greedily and
# incorrectly by the currently available Rizin and experimental Ghidra ARC
# analyzers when analysis starts at an earlier instruction.  Pin the raw
# module-reference instructions and independently scan every two-byte aligned
# ARC branch-and-link encoding instead of trusting global xrefs.
MODULE_REFERENCES = (
    ("MyApp",   0x0030_EAC8, "r0",  "c34033001445"),
    ("qf_actq", 0x0031_0D48, "r0",  "c34033003845"),
    ("qf_actq", 0x0031_0D72, "r0",  "c34033003845"),
    ("qf_actq", 0x0031_0DB8, "r0",  "c34033003845"),
    ("qf_actq", 0x0031_0E30, "r17", "d34133003845"),
    ("qk",      0x0031_0F06, "r0",  "c34033001c45"),
    ("qk",      0x0031_0F2C, "r0",  "c34033001c45"),
    ("qf_act",  0x0031_0F8C, "r0",  "c34033002845"),
    ("qf_dyn",  0x0031_0FF6, "r0",  "c34033002045"),
    ("qf_dyn",  0x0031_1070, "r16", "d34033002045"),
    ("qf_dyn",  0x0031_11BE, "r0",  "c34033002045"),
    ("qf_dyn",  0x0031_11E4, "r0",  "c34033002045"),
    ("qep_hsm", 0x0031_127E, "r19", "d34333003045"),
    ("qep_hsm", 0x0031_149C, "r20", "d34433003045"),
    ("qk",      0x0031_1564, "r0",  "0a20800f33001c45"),
    ("qk",      0x0031_15D0, "r0",  "c34033001c45"),
    ("qk",      0x0031_165A, "r0",  "c34033001c45"),
    ("qf_mem",  0x0031_1686, "r16", "d34033004045"),
    ("qf_mem",  0x0031_170A, "r0",  "c34033004045"),
    ("qf_mem",  0x0031_1756, "r0",  "c34033004045"),
    ("qf_mem",  0x0031_17B2, "r0",  "c34033004045"),
    ("WsfOs",   0x0031_40DC, "r0",  "c34033004845"),
)
ASSERT_CALLS = (
    # address, module, assertion ID, governing module reference, raw BL bytes
    (0x0030_EACE, "MyApp",   181, 0x0030_EAC8, "0e0d6001"),
    (0x0031_0D4E, "qf_actq", 110, 0x0031_0D48, "8e0a6000"),
    (0x0031_0D78, "qf_actq", 310, 0x0031_0D72, "620a6000"),
    (0x0031_0DBE, "qf_actq", 210, 0x0031_0DB8, "1e0a6000"),
    (0x0031_0E3A, "qf_actq", 100, 0x0031_0E30, "a2096000"),
    (0x0031_0E60, "qf_actq", 110, 0x0031_0E30, "7a096000"),
    (0x0031_0F0C, "qk",      300, 0x0031_0F06, "ce086000"),
    (0x0031_0F32, "qk",      189, 0x0031_0F2C, "aa086000"),
    (0x0031_0F92, "qf_act",  100, 0x0031_0F8C, "4a086000"),
    (0x0031_0FFC, "qf_dyn",  410, 0x0031_0FF6, "de0f0000"),
    (0x0031_10A8, "qf_dyn",  310, 0x0031_1070, "320f2000"),
    (0x0031_10E8, "qf_dyn",  320, 0x0031_1070, "f20e2000"),
    (0x0031_11C4, "qf_dyn",  200, 0x0031_11BE, "160e2000"),
    (0x0031_11EA, "qf_dyn",  201, 0x0031_11E4, "f20d0000"),
    (0x0031_1290, "qep_hsm", 400, 0x0031_127E, "4a0d2000"),
    (0x0031_1414, "qep_hsm", 410, 0x0031_127E, "c60b2000"),
    (0x0031_1478, "qep_hsm", 520, 0x0031_127E, "620b2000"),
    (0x0031_1488, "qep_hsm", 510, 0x0031_127E, "520b2000"),
    (0x0031_14B4, "qep_hsm", 200, 0x0031_149C, "260b2000"),
    (0x0031_14C8, "qep_hsm", 210, 0x0031_149C, "120b2000"),
    (0x0031_1502, "qep_hsm", 220, 0x0031_149C, "da0a2000"),
    (0x0031_156C, "qk",      500, 0x0031_1564, "6e0a2000"),
    (0x0031_15D6, "qk",      510, 0x0031_15D0, "060a0000"),
    (0x0031_1660, "qk",      410, 0x0031_165A, "7a090000"),
    (0x0031_1698, "qf_mem",  310, 0x0031_1686, "42092000"),
    (0x0031_16C0, "qf_mem",  330, 0x0031_1686, "1a092000"),
    (0x0031_16E0, "qf_mem",  320, 0x0031_1686, "fa082000"),
    (0x0031_1710, "qf_mem",  100, 0x0031_170A, "ca082000"),
    (0x0031_175C, "qf_mem",  110, 0x0031_1756, "7e080000"),
    (0x0031_17B8, "qf_mem",  200, 0x0031_17B2, "22082000"),
    (0x0031_40E2, "WsfOs",   653, 0x0031_40DC, "fa0eaffe"),
)

PORTABLE_ASSERTION_CONSTELLATION = {
    "qf_actq": {"linked": (100, 110, 210, 310), "not_linked": (400, 900)},
    "qf_dyn": {"linked": (200, 201, 310, 320, 410), "not_linked": (100, 500)},
    "qf_act": {"linked": (100,), "not_linked": (200,)},
    "qep_hsm": {"linked": (200, 210, 220, 400, 410, 510, 520), "not_linked": (600, 810)},
    "qf_mem": {"linked": (100, 110, 200, 310, 320, 330), "not_linked": (400,)},
    "qk": {"linked": (300, 410, 500, 510), "not_linked": (600, 700)},
}

RECOVERED_CONFIGURATION = {
    "QF_MAX_TICK_RATE": {
        "value": 0,
        "confidence": "high",
        "evidence": "QF_init calls QF_bzero at QF_timeEvtHead_ with length zero, then reuses the address for QK_attr_",
    },
    "QF_MAX_ACTIVE": {
        "value": 16,
        "confidence": "high",
        "evidence": "priority-minus-one is bounded against 16; QK checks p below 17",
    },
    "QF_MAX_EPOOL": {
        "value": 2,
        "confidence": "high",
        "evidence": "QF_poolInit path accepts QF_maxPool_ only while it is below 2",
    },
    "Q_SIGNAL_SIZE": {
        "value": 2,
        "confidence": "high",
        "evidence": "allocated QEvt writes a halfword signal at +0 and byte pool/ref counters at +2/+3",
    },
    "QF_EQUEUE_CTR_SIZE": {
        "value": 1,
        "confidence": "high",
        "evidence": "qf_actq queue counters use byte loads/stores",
    },
    "QF_MPOOL_SIZ_SIZE": {
        "value": 2,
        "confidence": "high",
        "evidence": "20-byte QMPool layout stores block size as a halfword",
    },
    "QF_MPOOL_CTR_SIZE": {
        "value": 2,
        "confidence": "high",
        "evidence": "QMPool nTot/nFree/nMin fields use halfword loads/stores",
    },
    "QK_READY_SET_BITS": {
        "value": 16,
        "confidence": "high",
        "evidence": "QK ready-set operations use halfword loads/stores with priorities 1..16",
    },
    "QACTIVE_SIZE": {
        "value": 36,
        "confidence": "high",
        "evidence": "QActive_ctor clears exactly 0x24 bytes before QHsm_ctor and vtable installation",
    },
    "QK_ATTR_SIZE": {
        "value": 8,
        "confidence": "high",
        "evidence": "QF_init clears eight bytes at 0x00801394 and sets lockCeil at offset +2",
    },
}

UPSTREAM = {
    "repository": "https://github.com/QuantumLeaps/qpc",
    "selected_release_tag": "v6.5.1",
    "selected_release_commit": "416dcec8820b9cdb5827497e645d0d9375db53c6",
    "release_identification_proven": True,
    "checked_history_floor_tag": "v6.0.1",
    "checked_history_floor_commit": "25636b87b0dbf4ccb015cb6eb9fb42aeb6010ef6",
    "portable_ancestry_floor_tag": "v6.3.6",
    "portable_ancestry_floor_commit": "5550cca87dedf72d45250ad01e9cdeee8c4140ba",
    "last_earlier_incompatible_tag": "v6.3.4",
    "last_earlier_incompatible_commit": "2b231b3383d98b36585435030e7440dbade3da9b",
    "compatible_ceiling_tag": "v6.6.0+",
    "compatible_ceiling_commit": "a280d203c0f55753b18dd9fc76104936729e471a",
    "first_excluded_tag": "v6.7.0",
    "first_excluded_commit": "af0b6f2f00f96b9753aa1dcbe734284e6f99f25c",
    "exact_vendor_checkout_proven": False,
}

EM9305_SDK_ORACLE = {
    "repository": "https://github.com/C0R3YY2/em9305_original",
    "commit": "e4412bc98d4e76d441d1226ca3696e53cfae5f54",
    "tree": "f5cb9ba00df71c2612d6d64cf39e05615a2feb64",
    "status": "third-party public source oracle; not an authoritative vendor repository or exact shipped checkout",
}
EM9305_SDK_ORACLE_FILES = {
    "emcore/bin/v4.2/standard/includes/qep.h": (
        "129bcda2ee271406a21a5197763974c822c2ad6e",
        "94c999cea695d2803d95cf418151dd0847c4d484f84b664e81af5428cefbd986",
        ('Last updated for version 6.5.1', '#define QP_VERSION      651U', '#define QP_VERSION_STR  "6.5.1"', '#define QP_RELEASE      0x8E7055B4U'),
    ),
    "emcore/bin/v4.2/standard/includes/bsp.h": (
        "cd9fa65df3a6b33fbf8325adc7fd166aed8d473f",
        "76e6d4af7f3bb3ea01cdb085405cd66291813118645732edcd8f5541aa43a896",
        ("static ALWAYS_INLINE int_t QF_resume(void)", "QF_onResume();", "QK_onIdle();"),
    ),
    "emcore/bin/v4.2/standard/emcore_standard.sym": (
        "7955274387f9d7a85708b8e18f06a977b42c168e",
        "c27c8dce8445e13845c9c1d9f32db76ca30f0cffc4ceeadb0a85cf8979775828",
        (
            "QF_onResume=0x306e04 0x58",
            "QF_onStartup=0x306e64 0x4a",
            "QK_onIdle=0x307544 0x38",
            "Q_onAssert=0x30797c 0xe",
            "Q_onAssertExt=0x30798c 0xe",
            "gQF_onResumeExt=0x80fe04 0x4",
            "gQF_onResumeInternalHook=0x80fe08 0x4",
            "gQF_onStartupExt=0x80fe0c 0x4",
            "gQF_onStartupInternalHook=0x80fe10 0x4",
            "gQK_onIdleExt=0x80fe14 0x4",
            "gQK_onIdleInternalHook=0x80fe18 0x4",
            "gQ_onAssertExt=0x80fe1c 0x4",
        ),
    ),
    "emcore/custom/source/emcore_bsp.c": (
        "4cbe32d2c661346fb54b8502a729d3c2d8b1af10",
        "45c0f2c7f9fe135bc2a6d96a64abeb73dcfc1b1e90e1424f1cff13ca6f0ba345",
        ("void EMCORE_QF_onStartupExt(void)", "void EMCORE_QF_onResumeExt(void)", "void EMCORE_QK_onIdleExt(void)"),
    ),
}
EM9305_SDK_ORACLE_BINARY_FILES = {
    "libs/third_party/QPC/lib_QPC.a": (
        "26fc11bf0144caab77608fa5794e544d4d1d8a38",
        "c8b5834ca8c3b42fde7e2f8447772800561ddd5897123918e8353807242f8db5",
    ),
    "libs/pml/lib_pml.a": (
        "45c88f15bc6367dc15e3cdcabb9a23be74bb9934",
        "e57be8e7fd4352e99c3437bbea0563e1b1add61228781925f7212a07f0a04ce2",
    ),
    "libs/sleep_manager/lib_sleep_manager.a": (
        "05af021ac9132dc8c727913c4382eba9019aebdb",
        "82968846c25b2a6685aa357386ad1dcb6bbe33bb138359de66ce91d10d600856",
    ),
    "libs/sleep_timer/lib_sleep_timer.a": (
        "3713f176b7f1614920a3043c4dcb41ba730e3fe0",
        "cbf143b6d90832b349925bc1cfdd0963c2a7102b66c11b6aee9277739dcbe1b9",
    ),
    "libs/prot_timer/lib_prot_timer.a": (
        "cf8f1f22ea840568c83c6a2662c86e7d95b6581a",
        "8ea99f2afa095f90d1c9555d748908bb6e03805db87d38a80a51f640f11788c7",
    ),
    "libs/unitimer/lib_unitimer.a": (
        "07ed4df5a464637adf024d383bc89d2fd0b57bb0",
        "8699c09a59e65fec8f349a67fc445b8ab931a9e736d4bfabe01ebd773c005bd4",
    ),
}

PORTABLE_SOURCE_FILES = (
    "src/qf/qf_actq.c",
    "src/qf/qf_dyn.c",
    "src/qf/qf_act.c",
    "src/qf/qep_hsm.c",
    "src/qf/qf_mem.c",
    "src/qk/qk.c",
    "src/qf/qf_qact.c",
    "src/qf/qf_qeq.c",
)
CHECKED_TAG_COMMITS = {
    "v6.0.1": "25636b87b0dbf4ccb015cb6eb9fb42aeb6010ef6",
    "v6.0.4": "a1acc1d0e296780686d7246adb3c5c305b4c347d",
    "v6.2.0": "7bfce82cc98ec6306ebb2fe9a72a49ebb1f1a77e",
    "v6.3.0": "feb55738fe6ec0fcc505bf2d11760a7481c858c8",
    "v6.3.1": "58f80da3a7c2a2c9ba29637a76d4eda3f9488c7d",
    "v6.3.2": "952101792d5fccf6db6f353b0426039910311851",
    "v6.3.3": "76bd2c751a0fb491cec9c76cdd1001b984da1ca3",
    "v6.3.3a": "be570aa3ecf9d1451d0dbdc52e5ccf4220093c65",
    "v6.3.4": "2b231b3383d98b36585435030e7440dbade3da9b",
    "v6.3.6": "5550cca87dedf72d45250ad01e9cdeee8c4140ba",
    "v6.3.7": "21787336e81748423d9e88d8b780728bb65e7ee0",
    "v6.3.8": "a39a56b5ef3482aeaa7aa9d749d1368a5899d417",
    "v6.4.0": "5d14aa368a014be23dc51ca7b0be9f20cb3e15a5",
    "v6.5.0": "076a8d5d6f9c093c8bc49a331f923668de52f10d",
    "v6.5.1": "416dcec8820b9cdb5827497e645d0d9375db53c6",
    "v6.6.0+": "a280d203c0f55753b18dd9fc76104936729e471a",
}
SOURCE_EPOCH_TAG_GROUPS = (
    ("v6.0.1",),
    ("v6.0.4",),
    ("v6.2.0", "v6.3.0", "v6.3.1"),
    ("v6.3.2", "v6.3.3", "v6.3.3a", "v6.3.4"),
    ("v6.3.6",),
    ("v6.3.7", "v6.3.8"),
    ("v6.4.0",),
    ("v6.5.0",),
    ("v6.5.1",),
    ("v6.6.0+",),
)
STOCK_COMPATIBLE_SOURCE_TAGS = (
    "v6.3.6",
    "v6.3.7",
    "v6.3.8",
    "v6.4.0",
    "v6.5.0",
    "v6.5.1",
    "v6.6.0+",
)
STOCK_COMPATIBLE_SOURCE_EPOCH_TAG_GROUPS = tuple(
    group for group in SOURCE_EPOCH_TAG_GROUPS
    if any(tag in STOCK_COMPATIBLE_SOURCE_TAGS for tag in group)
)

# These two source-level changes have unambiguous stock instruction effects.
# v6.3.2 introduced the critical-section assertion wrappers, which restore the
# saved interrupt state before calling Q_onAssert().  v6.3.6 moved the dynamic
# event reference increment ahead of the post-status branch.  The stock
# QActive_post_ body exhibits both changes.
EXPECTED_QACTIVE_POST_LINEAGE = {
    "v6.0.1": (False, False),
    "v6.0.4": (False, False),
    "v6.2.0": (False, False),
    "v6.3.0": (False, False),
    "v6.3.1": (False, False),
    "v6.3.2": (True, False),
    "v6.3.3": (True, False),
    "v6.3.3a": (True, False),
    "v6.3.4": (True, False),
    "v6.3.6": (True, True),
    "v6.3.7": (True, True),
    "v6.3.8": (True, True),
    "v6.4.0": (True, True),
    "v6.5.0": (True, True),
    "v6.5.1": (True, True),
    "v6.6.0+": (True, True),
}


class AuditError(RuntimeError):
    """Raised when an authenticated EM9305/QP invariant changes."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def installed_slice(blob: bytes, start: int, end: int) -> bytes:
    begin = APP_FILE_OFFSET + start - APP_BASE
    finish = APP_FILE_OFFSET + end - APP_BASE
    return blob[begin:finish]


def c_string(blob: bytes, address: int) -> str:
    offset = APP_FILE_OFFSET + address - APP_BASE
    end = blob.index(0, offset)
    return blob[offset:end].decode("ascii")


def sign_extend(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return (value ^ sign) - sign


def arc_bl_target(word: int, address: int) -> int | None:
    """Decode an ARC 32-bit PC-relative branch-and-link target.

    The bit fields follow the ARC S19/S23 BL forms.  The file bytes can be
    read as a little-endian integer even though ARC instruction dumps display
    the two 16-bit halfwords in architectural order.
    """
    if ((word >> 11) & 0x1F) != 0x01 or (word & 0x1) != 0:
        return None
    if ((word >> 1) & 0x1) == 0:
        if ((word >> 16) & 0x1F) != 0:
            return None
        displacement = (((word >> 2) & 0x1FF) << 2) + (
            sign_extend((word >> 22) & 0x3FF, 10) << 11
        )
    else:
        if ((word >> 20) & 0x1) != 0:
            return None
        displacement = (
            (((word >> 2) & 0x1FF) << 2)
            + (((word >> 22) & 0x3FF) << 11)
            + (sign_extend((word >> 16) & 0xF, 4) << 21)
        )
    return ((address & ~0x3) + displacement) & 0xFFFF_FFFF


def scan_arc_bl_calls(blob: bytes, target: int) -> tuple[int, ...]:
    calls = []
    for offset in range(APP_FILE_OFFSET, len(blob) - 3, 2):
        address = PACKAGE_MAP_BASE + offset
        word = int.from_bytes(blob[offset:offset + 4], "little")
        if arc_bl_target(word, address) == target:
            calls.append(address)
    return tuple(calls)


def git_output(checkout: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", "-C", str(checkout), *arguments],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def git_bytes(checkout: Path, *arguments: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(checkout), *arguments],
        check=True,
        capture_output=True,
    ).stdout


def run_qpc_source_epoch_audit(checkout: Path) -> dict[str, Any]:
    origin = git_output(checkout, "remote", "get-url", "origin")
    if origin not in {
        "https://github.com/QuantumLeaps/qpc",
        "https://github.com/QuantumLeaps/qpc.git",
        "git@github.com:QuantumLeaps/qpc.git",
    }:
        raise AuditError(f"QP/C checkout is not the official repository: {origin!r}")

    observed_commits = {
        tag: git_output(checkout, "rev-list", "-n", "1", tag)
        for tag in CHECKED_TAG_COMMITS
    }
    if observed_commits != CHECKED_TAG_COMMITS:
        raise AuditError("checked QP/C tag commits changed")

    signatures = {
        tag: tuple(git_output(checkout, "rev-parse", f"{tag}:{path}") for path in PORTABLE_SOURCE_FILES)
        for tag in CHECKED_TAG_COMMITS
    }
    groups: list[tuple[str, ...]] = []
    for tag in CHECKED_TAG_COMMITS:
        if groups and signatures[tag] == signatures[groups[-1][0]]:
            groups[-1] = (*groups[-1], tag)
        else:
            groups.append((tag,))
    if tuple(groups) != SOURCE_EPOCH_TAG_GROUPS:
        raise AuditError(f"QP/C portable-source epochs changed: {groups!r}")

    qactive_post_lineage = {}
    for tag in CHECKED_TAG_COMMITS:
        source = git_output(checkout, "show", f"{tag}:src/qf/qf_actq.c")
        reference_increment = source.find("QF_EVT_REF_CTR_INC_(e)")
        status_branch = source.find("if (status)")
        if reference_increment < 0 or status_branch < 0:
            raise AuditError(f"QActive_post_ lineage anchors are missing at {tag}")
        observed = (
            "Q_ERROR_CRIT_(110)" in source,
            reference_increment < status_branch,
        )
        if observed != EXPECTED_QACTIVE_POST_LINEAGE[tag]:
            raise AuditError(f"QActive_post_ lineage changed at {tag}: {observed!r}")
        qactive_post_lineage[tag] = {
            "critical_assert_restores_interrupt_state": observed[0],
            "dynamic_reference_increment_precedes_status_branch": observed[1],
            "stock_compatible": tag in STOCK_COMPATIBLE_SOURCE_TAGS,
        }
    qf_time_assertion_sources = {}
    for tag in STOCK_COMPATIBLE_SOURCE_TAGS:
        source = git_output(checkout, "show", f"{tag}:src/qf/qf_time.c")
        required = (
            'Q_DEFINE_THIS_MODULE("qf_time")',
            "Q_ASSERT_CRIT_(110",
            "Q_REQUIRE_ID(300",
            "Q_REQUIRE_ID(400",
        )
        if not all(fragment in source for fragment in required):
            raise AuditError(f"qf_time assertion closure changed at {tag}")
        qf_time_assertion_sources[tag] = required
    return {
        "repository": origin,
        "portable_files": PORTABLE_SOURCE_FILES,
        "checked_tag_count": len(CHECKED_TAG_COMMITS),
        "distinct_source_epoch_count": len(groups),
        "stock_compatible_tag_count": len(STOCK_COMPATIBLE_SOURCE_TAGS),
        "stock_compatible_source_epoch_count": len(STOCK_COMPATIBLE_SOURCE_EPOCH_TAG_GROUPS),
        "stock_compatible_tags": STOCK_COMPATIBLE_SOURCE_TAGS,
        "qactive_post_lineage": qactive_post_lineage,
        "qf_time_assertion_sources": qf_time_assertion_sources,
        "epochs": [
            {
                "tags": group,
                "representative": group[-1],
                "representative_commit": CHECKED_TAG_COMMITS[group[-1]],
                "blob_ids": signatures[group[-1]],
            }
            for group in groups
        ],
    }


def run_em9305_sdk_oracle_audit(checkout: Path) -> dict[str, Any]:
    """Authenticate the public SDK snapshot used only as a naming/version oracle."""
    origin = git_output(checkout, "remote", "get-url", "origin")
    if origin not in {
        "https://github.com/C0R3YY2/em9305_original",
        "https://github.com/C0R3YY2/em9305_original.git",
        "git@github.com:C0R3YY2/em9305_original.git",
    }:
        raise AuditError(f"EM9305 SDK oracle checkout has unexpected origin: {origin!r}")
    commit = git_output(checkout, "rev-parse", "HEAD")
    tree = git_output(checkout, "rev-parse", "HEAD^{tree}")
    if commit != EM9305_SDK_ORACLE["commit"] or tree != EM9305_SDK_ORACLE["tree"]:
        raise AuditError(f"EM9305 SDK oracle identity changed: {commit}/{tree}")

    files = {}
    for path, (expected_blob, expected_sha, fragments) in EM9305_SDK_ORACLE_FILES.items():
        observed_blob = git_output(checkout, "rev-parse", f"HEAD:{path}")
        body = git_bytes(checkout, "show", f"HEAD:{path}")
        if observed_blob != expected_blob or sha256(body) != expected_sha:
            raise AuditError(f"EM9305 SDK oracle file changed: {path}")
        source = body.decode("utf-8", errors="strict")
        missing = tuple(fragment for fragment in fragments if fragment not in source)
        if missing:
            raise AuditError(f"EM9305 SDK oracle anchors missing from {path}: {missing!r}")
        files[path] = {
            "kind": "source_or_symbol",
            "git_blob": expected_blob,
            "sha256": expected_sha,
            "required_fragment_count": len(fragments),
        }
    for path, (expected_blob, expected_sha) in EM9305_SDK_ORACLE_BINARY_FILES.items():
        observed_blob = git_output(checkout, "rev-parse", f"HEAD:{path}")
        body = git_bytes(checkout, "show", f"HEAD:{path}")
        if observed_blob != expected_blob or sha256(body) != expected_sha:
            raise AuditError(f"EM9305 SDK oracle binary changed: {path}")
        files[path] = {
            "kind": "binary_archive",
            "git_blob": expected_blob,
            "sha256": expected_sha,
        }
    return {
        **EM9305_SDK_ORACLE,
        "observed_origin": origin,
        "files": files,
        "qp_version": "6.5.1",
        "qp_release": "0x8E7055B4",
        "qp_release_date": "2019-05-24",
        "authoritative_vendor_checkout": False,
    }


def run_rizin_audit(image: Path, rizin: str = "rizin") -> dict[str, Any]:
    common = [
        rizin,
        "-2", "-q", "-n", "-a", "arc", "-b", "16", "-E", "little",
        "-m", hex(PACKAGE_MAP_BASE),
    ]
    call_commands = []
    for address, _module, _assertion_id, _reference, _body in ASSERT_CALLS:
        call_commands.extend(("-c", f"pdj 1 @ {hex(address)}"))
    refs_result = subprocess.run(
        common + call_commands + ["-c", "q", str(image)],
        check=True,
        capture_output=True,
        text=True,
    )
    decoded = [json.loads(line)[0] for line in refs_result.stdout.splitlines() if line.startswith("[")]
    expected = tuple((address, body) for address, _module, _id, _reference, body in ASSERT_CALLS)
    observed = tuple((record["offset"], record["bytes"]) for record in decoded)
    if observed != expected or any(
        record.get("type") != "call" or record.get("jump") != ASSERT_HANDLER
        for record in decoded
    ):
        raise AuditError(f"Rizin exact-address assertion decode changed: {observed!r}")

    qk_result = subprocess.run(
        common + ["-c", "pdj 6 @ 0x311560", "-c", "q", str(image)],
        check=True,
        capture_output=True,
        text=True,
    )
    qk = json.loads(qk_result.stdout)
    fingerprint = tuple((record["offset"], record["size"], record["disasm"], record["bytes"]) for record in qk)
    expected_fingerprint = (
        (0x0031_1560, 2, "ldb_s r13, [r14, 1]", "a18e"),
        (0x0031_1562, 2, "brne_s r13, 0,0x00311574", "8aed"),
        (0x0031_1564, 8, "mov r0, 0x0033451c", "0a20800f33001c45"),
        (0x0031_156C, 4, "bl.d 0x003117d8", "6e0a2000"),
        (0x0031_1570, 4, "mov r1, 0x1f4", "8a21070d"),
        (0x0031_1574, 4, "stb r0, [r14, 1]", "011e0310"),
    )
    if fingerprint != expected_fingerprint:
        raise AuditError(f"Rizin QK discriminator changed: {fingerprint!r}")
    return {
        "version": subprocess.run(
            [rizin, "-v"], check=True, capture_output=True, text=True
        ).stdout.splitlines()[0],
        "assert_handler": ASSERT_HANDLER,
        "exact_address_call_count": len(observed),
        "exact_address_calls": observed,
        "global_xrefs_authoritative": False,
        "decoder_caveat": "global analysis misses ARCv2 EM short-register/long-immediate boundaries",
        "qk_discriminator": fingerprint,
    }


def analyze(
    image: Path = DEFAULT_IMAGE,
    *,
    with_rizin: bool = False,
    qpc_checkout: Path | None = None,
    em9305_sdk_checkout: Path | None = None,
) -> dict[str, Any]:
    blob = image.read_bytes()
    if len(blob) != IMAGE_SIZE or sha256(blob) != IMAGE_SHA256:
        raise AuditError("official EM9305 image identity mismatch")
    app = blob[APP_FILE_OFFSET:]
    if len(app) != APP_END - APP_BASE or sha256(app) != APP_SHA256:
        raise AuditError("EM9305 application record changed")

    regions = []
    for name, (start, end, digest), state in (
        ("module_table", MODULE_TABLE, "fully_classified_stock_retained"),
        ("qpc_cluster", QPC_CLUSTER, "reverse_engineered_boundary_stock_retained"),
        ("qk_port_cluster", QK_PORT_CLUSTER, "sdk_archive_identified_stock_retained"),
        ("prot_timer_set_hw_trigger_enable", PROT_TIMER_SET_HW_TRIGGER_ENABLE, "sdk_symbol_identified_vendor_modified_stock_retained"),
        ("qk_activate_candidate", QK_ACTIVATE_CANDIDATE, "reverse_engineered_boundary_stock_retained"),
        ("qactive_post_candidate", QACTIVE_POST_CANDIDATE, "reverse_engineered_boundary_stock_retained"),
        ("sleep_manager_go_to_sleep", QK_IDLE_POWER_MANAGER, "sdk_symbol_identified_vendor_configured_stock_retained"),
        ("sleep_manager_rccal_callback", SLEEP_MANAGER_RCCAL_CALLBACK, "sdk_archive_exact_relocation_normalized_stock_retained"),
        ("q_on_assert_ext", Q_ON_ASSERT_EXT, "source_oracle_identified_boundary_stock_retained"),
        ("hook_pointer_table", HOOK_POINTER_TABLE, "fully_classified_stock_retained"),
    ):
        body = installed_slice(blob, start, end)
        if sha256(body) != digest:
            raise AuditError(f"{name} boundary changed")
        regions.append({
            "name": name,
            "start": start,
            "end": end,
            "size": len(body),
            "sha256": digest,
            "state": state,
        })

    hook_table = installed_slice(blob, HOOK_POINTER_TABLE[0], HOOK_POINTER_TABLE[1])
    observed_hook_pointers = tuple(
        int.from_bytes(hook_table[offset:offset + 4], "little")
        for offset in range(0, len(hook_table), 4)
    )
    if observed_hook_pointers != tuple(address for _name, address in HOOK_POINTERS):
        raise AuditError(f"EM9305 callback pointer table changed: {observed_hook_pointers!r}")

    observed_modules = tuple((name, c_string(blob, address)) for name, address in MODULES)
    if any(expected != observed for expected, observed in observed_modules):
        raise AuditError("QP/C module-name table changed")
    for absent in ABSENT_PORTABLE_MODULE_STRINGS:
        if absent in app:
            raise AuditError(f"unexpected portable module string appeared: {absent!r}")
    for module, address, _register, expected_bytes in MODULE_REFERENCES:
        body = installed_slice(blob, address, address + len(expected_bytes) // 2)
        if body.hex() != expected_bytes:
            raise AuditError(f"{module} module reference changed at 0x{address:08X}")
    for address, _module, _assertion_id, _reference, expected_bytes in ASSERT_CALLS:
        if installed_slice(blob, address, address + 4).hex() != expected_bytes:
            raise AuditError(f"assertion call changed at 0x{address:08X}")
    observed_calls = scan_arc_bl_calls(blob, ASSERT_HANDLER)
    expected_calls = tuple(address for address, _module, _id, _reference, _body in ASSERT_CALLS)
    if observed_calls != expected_calls:
        raise AuditError(f"raw ARC assertion-handler topology changed: {observed_calls!r}")
    idle_call, idle_target, idle_bytes = QK_IDLE_POWER_MANAGER_CALL
    if installed_slice(blob, idle_call, idle_call + 4).hex() != idle_bytes:
        raise AuditError("QK_onIdle power-manager call changed")
    if scan_arc_bl_calls(blob, idle_target) != (idle_call,):
        raise AuditError("QK_onIdle power-manager call topology changed")
    portable_functions = []
    for module, function, start, end, digest in PORTABLE_FUNCTIONS:
        body = installed_slice(blob, start, end)
        if sha256(body) != digest:
            raise AuditError(f"portable function boundary changed: {module}:{function}")
        portable_functions.append({
            "module": module,
            "function": function,
            "start": start,
            "end": end,
            "size": len(body),
            "sha256": digest,
            "state": "reverse_engineered_boundary_stock_retained",
        })
    remainder_segments = []
    for name, start, end, digest, state in CLUSTER_REMAINDER_SEGMENTS:
        body = installed_slice(blob, start, end)
        if sha256(body) != digest:
            raise AuditError(f"cluster remainder segment changed: {name}")
        remainder_segments.append({
            "name": name,
            "start": start,
            "end": end,
            "size": len(body),
            "sha256": digest,
            "state": state,
        })

    sdk_identified_functions = []
    for name, start, end, digest, state in SDK_IDENTIFIED_FUNCTIONS:
        body = installed_slice(blob, start, end)
        if sha256(body) != digest:
            raise AuditError(f"SDK-identified function changed: {name}")
        sdk_identified_functions.append({
            "name": name,
            "start": start,
            "end": end,
            "size": len(body),
            "sha256": digest,
            "state": state,
        })

    cluster_partition = sorted(
        [(item["start"], item["end"], f"portable:{item['function']}") for item in portable_functions]
        + [(item["start"], item["end"], f"remainder:{item['name']}") for item in remainder_segments]
    )
    cursor = QPC_CLUSTER[0]
    for start, end, name in cluster_partition:
        if start != cursor or end <= start:
            raise AuditError(
                f"QP/C cluster partition has a gap/overlap at {name}: "
                f"expected 0x{cursor:08X}, observed 0x{start:08X}"
            )
        cursor = end
    if cursor != QPC_CLUSTER[1]:
        raise AuditError(
            f"QP/C cluster partition ends at 0x{cursor:08X}, "
            f"expected 0x{QPC_CLUSTER[1]:08X}"
        )

    rizin_report = None
    if with_rizin:
        executable = shutil.which("rizin")
        if executable is None:
            raise AuditError("Rizin was requested but is not installed")
        rizin_report = run_rizin_audit(image, executable)
    source_epoch_report = (
        run_qpc_source_epoch_audit(qpc_checkout) if qpc_checkout is not None else None
    )
    sdk_oracle_report = (
        run_em9305_sdk_oracle_audit(em9305_sdk_checkout)
        if em9305_sdk_checkout is not None else None
    )

    return {
        "identity": {
            "controller": "EM Microelectronic EM9305",
            "architecture": "Synopsys ARC EM7D / ARCompact",
            "framework": "Quantum Leaps QP/C with vendor ARC port/customizations",
            "application_start": APP_BASE,
            "application_end": APP_END,
            "application_size": len(app),
            "application_sha256": APP_SHA256,
        },
        "upstream": {
            **UPSTREAM,
            "checked_interval_status": "exact QP/C release 6.5.1; independently compatible portable-body ancestry v6.3.6 through v6.6.0+",
            "pre_v6_possible": False,
            "vendor_backport_or_cherry_pick_possible": True,
            "floor_discriminator": "QActive_post_ combines v6.3.2 critical-assert restoration with the v6.3.6 pre-status dynamic-reference increment",
            "ceiling_discriminator": "QK assertion 500 checks only p != 0; v6.7.0 adds pin/p bounds",
            "checked_tag_count": len(CHECKED_TAG_COMMITS),
            "portable_source_epoch_count": len(SOURCE_EPOCH_TAG_GROUPS),
            "stock_compatible_tag_count": len(STOCK_COMPATIBLE_SOURCE_TAGS),
            "stock_compatible_source_epoch_count": len(STOCK_COMPATIBLE_SOURCE_EPOCH_TAG_GROUPS),
            "stock_compatible_tags": STOCK_COMPATIBLE_SOURCE_TAGS,
            "source_epoch_audit": source_epoch_report,
            "em9305_sdk_source_oracle": {
                **EM9305_SDK_ORACLE,
                "audit": sdk_oracle_report,
            },
            "em9305_sdk_archive_comparison": {
                "compiler": "Synopsys MetaWare ARC Compiler T-2022.09 build 004 / LLVM 14.0.6 (EM-Micro)",
                "optimization": "-Os",
                "archive_count": len(EM9305_SDK_ORACLE_BINARY_FILES),
                "confirmed_exact_function_count": 98,
                "confirmed_exact_function_bytes": 7172,
                "unique_exact_function_count": 92,
                "unique_exact_function_bytes": 7146,
                "qpc_known_address_matches": 36,
                "qpc_known_address_candidates": 39,
                "qpc_intentional_vendor_modified_hooks": (
                    "QF_onResumeInternalHook",
                    "QF_onStartupInternalHook",
                    "QK_onIdleInternalHook",
                ),
                "comparison_tool": "tools/compare_em9305_sdk_archive.py",
            },
        },
        "modules": [{"name": name, "address": address} for name, address in MODULES],
        "portable_functions": portable_functions,
        "cluster_remainder_segments": remainder_segments,
        "sdk_identified_functions": sdk_identified_functions,
        "regions": regions,
        "hooks": {
            "pointer_table": {
                "start": HOOK_POINTER_TABLE[0],
                "end": HOOK_POINTER_TABLE[1],
                "sha256": HOOK_POINTER_TABLE[2],
                "entries": [
                    {"name": name, "address": address}
                    for name, address in HOOK_POINTERS
                ],
            },
            "callback_globals": CALLBACK_GLOBALS,
            "source_oracle_boundary_match": (
                "stock QF/QK hook sizes and callback-global addresses match the EM9305 SDK v4.2 symbol vocabulary"
            ),
        },
        "assertions": {
            "handler": ASSERT_HANDLER,
            "discovery_method": "exhaustive two-byte-aligned ARC BL scan plus raw module-reference pins",
            "module_references": [
                {"module": module, "address": address, "register": register, "bytes": body}
                for module, address, register, body in MODULE_REFERENCES
            ],
            "direct_calls": [
                {
                    "address": address,
                    "module": module,
                    "id": assertion_id,
                    "module_reference": reference,
                    "bytes": body,
                }
                for address, module, assertion_id, reference, body in ASSERT_CALLS
            ],
            "portable_constellation": PORTABLE_ASSERTION_CONSTELLATION,
            "portable_call_count": sum(
                1 for _address, module, _id, _reference, _body in ASSERT_CALLS
                if module not in {"MyApp", "WsfOs"}
            ),
            "all_calls_assigned_to_module": True,
            "qk_macro_callsite_id": 189,
            "qk_macro_callsite_source_line": "QF_CRIT_ENTRY_() at qk.c:189 in all checked v6.0.1..v6.6.0+ tags",
            "qk_module_reference": 0x0033_451C,
            "qk_assertion_id": 500,
            "qk_precondition": "selected priority p is nonzero",
        },
        "configuration": {
            "recovered": RECOVERED_CONFIGURATION,
            "port_and_build": {
                "Q_SPY": {
                    "value": False,
                    "confidence": "high",
                    "evidence": "QActive_post_ has the non-Q_SPY three-argument ABI and no QS record path",
                },
                "QF_CRIT_STAT_TYPE": {
                    "value": "32-bit ARC status register value",
                    "confidence": "high",
                    "evidence": "QActive_post_ saves CLRI into r18, executes SYNC, and restores with SETI r18",
                },
                "critical_assertion_exit": {
                    "value": "restore saved interrupt status before Q_onAssert",
                    "confidence": "high",
                    "evidence": "SETI r18 precedes qf_actq assertion 110 at 0x00310E60",
                },
                "QF_onStartup": {
                    "value": 0x0031_1154,
                    "confidence": "high",
                    "evidence": "QF_run calls this vendor callback after initial-event scheduling and before SETI",
                },
                "QK_onIdle": {
                    "value": 0x0031_15E4,
                    "confidence": "high",
                    "evidence": "both run loops call this vendor callback indefinitely after enabling interrupts",
                },
                "QK_onIdle_interrupt_race_guard": {
                    "value": "ILINK sentinel; enter sleep manager only if no interrupt rewrites ILINK",
                    "confidence": "high",
                    "evidence": "QK_onIdle clears ILINK, runs optional callbacks, executes CLRI/SYNC, and conditionally calls 0x003126E0",
                },
                "ARC_toolchain": {
                    "value": "Synopsys MetaWare ARC Compiler T-2022.09 build 004 / LLVM 14.0.6 (EM-Micro), -Os",
                    "confidence": "high",
                    "evidence": "all 26 nontrivial known QP/C bodies uniquely match the authenticated relocation-bearing SDK archive outside relocation fields",
                },
                "QK_port": {
                    "value": "qkPortDummy, IRQHandler_SWI0, QK_noPreemption, QK_restoreContext, IRQHandler_SWI1",
                    "confidence": "high",
                    "evidence": "authenticated SDK qk_port.s object matches the stock 0x00302518..0x00302664 cluster",
                },
            },
            "not_observable_from_linked_portable_corpus": {
                "QF_TIMEEVT_CTR_SIZE_and_layout": {
                    "reason": "QF_MAX_TICK_RATE is zero and the upstream tick/constructor/arm closure is not linked",
                    "evidence": "the zero-length QF_timeEvtHead_ array exposes no counter field accesses",
                },
            },
            "unresolved": (
                "vendor timer or time-event substitute, if any",
                "non-QK vendor ISR entry/exit bookkeeping beyond the exact SDK-matched SWI0/SWI1 port",
            ),
        },
        "power_management": {
            "qk_on_idle": 0x0031_15E4,
            "interrupt_occurrence_sentinel": "ILINK",
            "optional_callback_slots": (0x0080_FE18, 0x0080_FE14),
            "sleep_manager": 0x0031_26E0,
            "sleep_manager_name": "SLEEP_MANAGER_GoToSleep",
            "sleep_manager_size": QK_IDLE_POWER_MANAGER[1] - QK_IDLE_POWER_MANAGER[0],
            "sleep_manager_state": "sdk_symbol_identified_vendor_configured_stock_retained",
            "rccal_callback": 0x0031_28E4,
            "rccal_callback_size": 52,
            "rccal_callback_state": "sdk_archive_exact_relocation_normalized_stock_retained",
            "sleep_instructions": (0x0031_280E, 0x0031_2816),
            "direct_callers": (0x0031_1610,),
        },
        "rizin": rizin_report,
        "recovery": {
            "family_identification_percent": 100,
            "release_identification_percent": 100,
            "configuration_identification_percent": "90-95",
            "release_configuration_identification_percent": "95-100",
            "bounded_cluster_bytes": QPC_CLUSTER[1] - QPC_CLUSTER[0],
            "bounded_cluster_identification_percent": 100,
            "bounded_cluster_reverse_engineered_percent": "80-90",
            "portable_function_count": len(portable_functions),
            "portable_function_bytes": sum(item["size"] for item in portable_functions),
            "cluster_remainder_bytes": sum(item["size"] for item in remainder_segments),
            "cluster_remainder_segment_count": len(remainder_segments),
            "anonymous_executable_cluster_bytes": 0,
            "cluster_partition_complete": True,
            "production_source_replacement_percent": 0,
            "opaque_or_stock_retained_application_bytes": len(app),
        },
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument(
        "--rizin",
        action="store_true",
        help="re-run exact-address ARC call and QK fingerprint checks",
    )
    parser.add_argument(
        "--qpc-checkout",
        type=Path,
        help="verify official tag commits and eight-file portable-source epochs",
    )
    parser.add_argument(
        "--em9305-sdk-checkout",
        type=Path,
        help="authenticate the pinned third-party EM9305 SDK v4.2 source oracle",
    )
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    report = analyze(
        args.image,
        with_rizin=args.rizin,
        qpc_checkout=args.qpc_checkout,
        em9305_sdk_checkout=args.em9305_sdk_checkout,
    )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("EM9305 QP/C audit: PASS")
        print(json.dumps(report["recovery"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
