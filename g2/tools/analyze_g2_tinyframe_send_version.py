#!/usr/bin/env python3
"""Fail-closed TinyFrame send-path and upstream-lineage audit for G2 2.2.6.10.

This analyzer is deliberately read-only.  It authenticates the pinned official
Apollo-main image, verifies complete function bodies and direct-call topology,
and reports only the TinyFrame claims established by those bytes.  It contains
no device transport, signer, programmer, erase operation, or flash write path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = (
    ROOT / "blobs" / "official" / "g2-2.2.6.10" / "ota_s200_firmware_ota.bin"
)
IMAGE_SIZE = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
LOAD_BASE = 0x00437FE0


class AuditError(RuntimeError):
    """Raised when an authenticated image invariant does not hold."""


PINNED_SPANS = {
    # Receive-side anchors are repeated here rather than trusted transitively
    # from the earlier wire-format audit.
    "TF_CksumStart": (
        0x0049172C,
        0x00491730,
        "a7ddd513d149ea16fdd4db3f82267f83087aeaddd06b5dde5468adb704205fc4",
    ),
    "TF_CksumAdd": (
        0x00491730,
        0x0049174E,
        "3e32b81bf34333123c6f8fb83abb9b00315de14d9a5b962f0ba93b4bfd8d5da8",
    ),
    "TF_CksumEnd": (
        0x0049174E,
        0x00491752,
        "952beac4ed6fe10a2de94037d8295a333b4a796f6ce6ed3a09b86d74e60004ca",
    ),
    "TF_InitStatic_vendor": (
        0x00491752,
        0x004917D2,
        "956ed0e3a9c60365f19970258b2f5d064a07bbac9dc72f561425567dabb9341b",
    ),
    "TF_Init": (
        0x004917D2,
        0x00491838,
        "7f082a0db4325685eb4f10cd204d75b80f337e1826dd9b0fc0f80be1192902b0",
    ),
    "renew_id_listener": (
        0x00491838,
        0x0049183E,
        "8727836ca31657f51795e2ce7b3cfe85c5c121d7ad273c3fe6fbcd67e9bc358d",
    ),
    "cleanup_id_listener": (
        0x0049183E,
        0x0049188E,
        "93cc3419b367a87fc8575a996e213302fc962776b2dd4877c4d9f0fe0835659a",
    ),
    "cleanup_type_listener": (
        0x0049188E,
        0x004918A8,
        "ab8e8d36700beaf6c7a04a95c661bd2293d1d235e60628cdff7f3310a934b6fb",
    ),
    "cleanup_generic_listener": (
        0x004918A8,
        0x004918C2,
        "c0e1ad8f62839c2f954a6bf4030658b398fe903254b91319de2e50f03636f6bd",
    ),
    "TF_AddIdListener": (
        0x004918C2,
        0x00491962,
        "a2d9522a7dd6ef26cfc9826e29a95da22d32f34c5513f12703b47b53e928731f",
    ),
    "TF_AddTypeListener": (
        0x00491962,
        0x004919E8,
        "c9c8b421386f03fc2023ffbab7d5445806706e664ff6742d51f8439b7d9e0458",
    ),
    "TF_HandleReceivedMessage": (
        0x004919E8,
        0x00491B9A,
        "52d0c9eb07c779a6afe46c62ba80fd8c397caf55ee2189b894516bf055ea69b5",
    ),
    "TF_Accept": (
        0x00491B9A,
        0x00491BB6,
        "1de5d783b0057911ee9ac3a9802e556bec5f8d85f9223fe421fd3a70797fd3d9",
    ),
    "pars_begin_frame": (
        0x00491BB6,
        0x00491BE4,
        "1a04cffc10ac6ae3e927ad4c901268b28083d8c0b4dfc902f428ec16d9464b5f",
    ),
    "TF_AcceptChar": (
        0x00491BE4,
        0x00491ED8,
        "47764bdbb61eb9c1d1710f1d35051e9c351ba54a4e2efbc0291b4bf902db00ca",
    ),
    # Complete send-side closure.
    "TF_ClaimTx_soft_lock": (
        0x004916C8,
        0x00491722,
        "b5f0508cbb1efc151513afa92c0c172824f55f82d0ce4ffa25e6303075bc16e2",
    ),
    "TF_ReleaseTx_soft_lock": (
        0x00491722,
        0x0049172C,
        "b177facafe9a96ba339dde25abc5989cc030d7b0f9174f5467bb8466df2eb3c7",
    ),
    "TF_ComposeHead": (
        0x00491F54,
        0x00492032,
        "b99f03cff24a278355d37e299be5c7b57ae84ac7d02ac0f625b708e678aaf940",
    ),
    "TF_ComposeBody": (
        0x00492032,
        0x0049207A,
        "9c4fb7cece798d4910878de02fc5c2bb5e300eb3c51a793a2e9a176d72a33ebc",
    ),
    "TF_ComposeTail": (
        0x0049207A,
        0x004920AA,
        "935d106799c49ded9f420e45c9a7af162d6d9287a56b30b79b3824c82ae5a5cc",
    ),
    "TF_SendFrame_Begin": (
        0x004920AA,
        0x00492114,
        "88cc7683407387bd3a05b874cc5854bda1143fe052aeb8813bfd9fa681c7f155",
    ),
    "TF_SendFrame_Chunk": (
        0x00492114,
        0x00492198,
        "8a9f0fd729f9c8b16f1fa57661c747ff5d116e10b45eaa10e6d0d243f6eb3792",
    ),
    "TF_SendFrame_End": (
        0x00492198,
        0x00492200,
        "3f4560ef0982ed99c25f49100ed1ee3cdef726853c2256ef73879d9d657988db",
    ),
    "TF_SendFrame": (
        0x00492200,
        0x0049223C,
        "66163f20aba56809b0eb52f5db199aae616d6f233284ba47c8654c0e9db1addc",
    ),
    "TF_Send": (
        0x0049223C,
        0x0049224C,
        "5b1e502cd5ab6ccc920021d8100ba9d015b7d25bbbdb0cf32dac78d381221d39",
    ),
    "TF_Query": (
        0x0049224C,
        0x0049225A,
        "e348f1aa2d888197ead654f4cbdc689ea964af5ff8b1d03b647317353ecd3823",
    ),
    "TF_Respond": (
        0x0049225A,
        0x00492266,
        "d1ce93ac47083fe0ab1104e930ef6142d439bf44cd6e596ba499ea13da9c59d7",
    ),
    "TF_Query_Multipart": (
        0x00492266,
        0x00492278,
        "c53c52b0b4e741bba45b981b405b6040f5e92c965b69c95958c2d26776d56372",
    ),
    "TF_Multipart_Payload": (
        0x00492278,
        0x00492280,
        "ce3a5e1407dc2a68941ca1cb5bf191dfa48a9a176d735efb69b747aab42e6bf4",
    ),
    "TF_Multipart_Close": (
        0x00492280,
        0x00492288,
        "2e7f95a6afa0b18c10a346869a17a8a73c9f4a38221115f3556303d98e48c201",
    ),
    "TF_Tick": (
        0x00492288,
        0x004922F6,
        "cbcbcd5beaf3a2a68aeac10c9e1d2989b062be0369d37d16a6f2da25409e49d0",
    ),
    # This is the application-owned port boundary, not TinyFrame source.
    "TF_WriteImpl_local_wrapper": (
        0x004D9522,
        0x004D9530,
        "12611160fc8e6ee3552e451f338ef1a611ad59ddf77254c51b5a1685d9d7c7f9",
    ),
}


TINYFRAME_LINKED_SPAN_NAMES = (
    "TF_ClaimTx_soft_lock",
    "TF_ReleaseTx_soft_lock",
    "TF_CksumStart",
    "TF_CksumAdd",
    "TF_CksumEnd",
    "TF_InitStatic_vendor",
    "TF_Init",
    "renew_id_listener",
    "cleanup_id_listener",
    "cleanup_type_listener",
    "cleanup_generic_listener",
    "TF_AddIdListener",
    "TF_AddTypeListener",
    "TF_HandleReceivedMessage",
    "TF_Accept",
    "pars_begin_frame",
    "TF_AcceptChar",
    "TF_ComposeHead",
    "TF_ComposeBody",
    "TF_ComposeTail",
    "TF_SendFrame_Begin",
    "TF_SendFrame_Chunk",
    "TF_SendFrame_End",
    "TF_SendFrame",
    "TF_Send",
    "TF_Query",
    "TF_Respond",
    "TF_Query_Multipart",
    "TF_Multipart_Payload",
    "TF_Multipart_Close",
    "TF_Tick",
)

TINYFRAME_LITERAL_POOL = (
    0x00491ED8,
    0x00491F54,
    "fb922d9523d1afd800c10195240574f3fab0541a9655fd09ceab91990b2e82d0",
)


CRC16_TABLE = (
    0x006C0950,
    0x006C0B50,
    "961656eaf43bdf70937151a003627324be86c28ca32285f58edd5f5c73c51b79",
)


SYNC_APPLICATION_SPANS = {
    "sync_tinyframe_tick_loop": (
        0x0045D4B8,
        0x0045D4D8,
        "9c676f32678132146ba5d7a6dfd8191ac94b23b86acf782e7cf5c939166eed3e",
    ),
    "sync_tinyframe_accept_ingress": (
        0x0045D4DC,
        0x0045D536,
        "669a484b5cf30ab962a12255f85b4082b9a792f2b83096473a3caac998ff520b",
    ),
    "SyncModuleInit": (
        0x0045E8D0,
        0x0045EB76,
        "62326c6a631f068f05f8141a8960aeab9a11242ab9f559507e9adf1b21e72360",
    ),
}

TINYFRAME_INSTANCE_SLOT = 0x200749C4
TINYFRAME_INSTANCE_SLOT_LITERAL_RUNS = [0x0045DD64, 0x0045EBDC]

FIRST_PARTY_TRANSPORT_SPANS = {
    "sync_write_wrapper": (
        0x00541790,
        0x005417A4,
        "f9ba82957a18e3ae966a6f8b6af0d7160d2ba237a61024b98cd5c938b8734d67",
    ),
    "transport_provider": (
        0x00584C98,
        0x00584DB6,
        "0a13941f278f566dff230b8fea27c85b231070ed2109d5b490ef48aa1943d18c",
    ),
}
FIRST_PARTY_TRANSPORT_CALLERS = [0x004D952A, 0x005730F8]


# Semantics-bearing operands inside complete hash-pinned functions.
INSTRUCTION_PINS = {
    # G2 vendor bookends: object size 0x7160; magic at +0 and +0x715c.
    0x004917A8: bytes.fromhex("47f26011"),
    0x004917BC: bytes.fromhex("5ff0a5302060"),
    0x004917C2: bytes.fromhex("5ff05a30"),
    0x004917C6: bytes.fromhex("47f25c11"),
    # Soft-lock byte at +0x642e (therefore TF_USE_MUTEX == 0).
    0x004916CA: bytes.fromhex("46f22e42"),
    0x00491724: bytes.fromhex("46f22e42"),
    # Request ID mask/peer bit: retain low 15 bits, OR bit 15 for peer 1.
    0x00491F76: bytes.fromhex("b8f80e70781ca8f80e007f047f0c"),
    0x00491F84: bytes.fromhex("98f80c00002801d057f40047"),
    # Recovered Tx buffer and state offsets, plus the 1024-byte flush limit.
    0x004920C4: bytes.fromhex("46f22100"),
    0x004920D2: bytes.fromhex("46f22441"),
    0x004920DA: bytes.fromhex("46f22841"),
    0x0049210A: bytes.fromhex("46f22c41"),
    0x0049215C: bytes.fromhex("b0f5806f"),
    # Local TF_WriteImpl drops the TinyFrame pointer and applies timeout 100.
    0x004D9522: bytes.fromhex("80b508001100642268f031f901bd"),
    # SyncModuleInit role 1 stores TF_Init(TF_MASTER); role 2 stores
    # TF_Init(TF_SLAVE), both in the single global instance slot.
    0x0045E926: bytes.fromhex("ad4c012032f052ff2060"),
    0x0045EA28: bytes.fromhex("6c4c002032f0d1fe2060"),
    # The only non-library instance consumers load the opaque pointer before
    # TF_Tick, TF_Accept, or multipart public entry calls.
    0x0045D4BC: bytes.fromhex("dff8a408006834f0e1fe"),
    0x0045D4DE: bytes.fromhex("dff884381a68"),
}


TARGETS = {
    "TF_ClaimTx_soft_lock": 0x004916C8,
    "TF_ReleaseTx_soft_lock": 0x00491722,
    "TF_CksumStart": 0x0049172C,
    "TF_CksumAdd": 0x00491730,
    "TF_CksumEnd": 0x0049174E,
    "TF_InitStatic_vendor": 0x00491752,
    "TF_Init": 0x004917D2,
    "renew_id_listener": 0x00491838,
    "cleanup_id_listener": 0x0049183E,
    "cleanup_type_listener": 0x0049188E,
    "cleanup_generic_listener": 0x004918A8,
    "TF_AddIdListener": 0x004918C2,
    "TF_AddTypeListener": 0x00491962,
    "TF_HandleReceivedMessage": 0x004919E8,
    "TF_Accept": 0x00491B9A,
    "pars_begin_frame": 0x00491BB6,
    "TF_AcceptChar": 0x00491BE4,
    "TF_ComposeHead": 0x00491F54,
    "TF_ComposeBody": 0x00492032,
    "TF_ComposeTail": 0x0049207A,
    "TF_SendFrame_Begin": 0x004920AA,
    "TF_SendFrame_Chunk": 0x00492114,
    "TF_SendFrame_End": 0x00492198,
    "TF_SendFrame": 0x00492200,
    "TF_Send": 0x0049223C,
    "TF_Query": 0x0049224C,
    "TF_Respond": 0x0049225A,
    "TF_Query_Multipart": 0x00492266,
    "TF_Multipart_Payload": 0x00492278,
    "TF_Multipart_Close": 0x00492280,
    "TF_WriteImpl_local_wrapper": 0x004D9522,
}


EXPECTED_DIRECT_CALLERS = {
    "TF_ClaimTx_soft_lock": [0x004920B6],
    "TF_ReleaseTx_soft_lock": [0x004920FE, 0x004921FA],
    "TF_CksumStart": [
        0x00491BBE,
        0x00491DA2,
        0x00491F68,
        0x00491F92,
        0x00492106,
    ],
    "TF_CksumAdd": [
        0x00491BC8,
        0x00491C74,
        0x00491CA8,
        0x00491CDC,
        0x00491E1C,
        0x00491FA0,
        0x00491FBC,
        0x00491FDE,
        0x00491FFE,
        0x0049205E,
    ],
    "TF_CksumEnd": [0x00491D36, 0x00491E76, 0x0049200E, 0x00492088],
    "TF_InitStatic_vendor": [0x00491830],
    "TF_Init": [0x0045E92A, 0x0045EA2C],
    "renew_id_listener": [0x00491A78],
    "cleanup_id_listener": [0x00491A94, 0x004922BE],
    "cleanup_type_listener": [0x00491AF4],
    "cleanup_generic_listener": [0x00491B42],
    "TF_AddIdListener": [0x004920F4],
    "TF_AddTypeListener": [
        0x0045E980,
        0x0045E98A,
        0x0045E994,
        0x0045EA7E,
        0x0045EA88,
        0x0045EA92,
        0x0045EA9C,
    ],
    "TF_HandleReceivedMessage": [0x00491D8E, 0x00491E90],
    "TF_Accept": [0x0045D530],
    "pars_begin_frame": [0x00491C64],
    "TF_AcceptChar": [0x00491BAA],
    "TF_ComposeHead": [0x004920CE],
    "TF_ComposeBody": [0x00492140],
    "TF_ComposeTail": [0x004921DA],
    "TF_SendFrame_Begin": [0x00492210],
    "TF_SendFrame_Chunk": [0x0049222E, 0x0049227A],
    "TF_SendFrame_End": [0x00492234, 0x00492282],
    "TF_SendFrame": [0x00492246, 0x00492254],
    "TF_Send": [0x00492260],
    "TF_Query": [0x00492272],
    "TF_Respond": [
        0x0045AEE2,
        0x0045AF74,
        0x0045B006,
        0x0045B094,
        0x0045B2C2,
        0x0045B35E,
        0x0045B3F0,
        0x0045B48C,
        0x0045B524,
        0x0045B66E,
        0x0045B7D2,
        0x0045B9C6,
    ],
    "TF_Query_Multipart": [0x0045E76A],
    "TF_Multipart_Payload": [0x0045E808],
    "TF_Multipart_Close": [0x0045E858],
    "TF_WriteImpl_local_wrapper": [0x0049216C, 0x004921C0, 0x004921F4],
}


IDENTITY_STRINGS = {
    0x006FE474: r"D:\01_workspace\s200_ap510b_iar_git\third_party\TinyFrame\TinyFrame.c",
    0x0071A188: "[TinyFrame][TF] :error TF_InitStatic() failed, tf is null.\n",
    0x0071924C: "[sync.module.framework]TF_Multipart_Payload send, len = %d",
    0x00765970: "Sync module start up as Master",
    0x00765990: "Sync module start up as Slave",
}


# IAR retained the source line passed by G2's TF_Error replacement.  The ten
# sites below cross the one-line cleanup_id_listener formatting change between
# 44ecc068 and eb75483e, so they recover textual source state that ordinary
# machine-code comparison cannot distinguish.  The instruction pins include
# the immediate materialization and stack store used for the line argument.
SOURCE_LINE_PINS = {
    "TF_ClaimTx_locked": {
        "run": 0x004916E2,
        "instruction": bytes.fromhex("23200090"),
        "stock_line": 35,
        "floor_line": 32,
        "successor_line": 32,
        "message": "TF already locked for tx!",
    },
    "TF_InitStatic_null": {
        "run": 0x0049176C,
        "instruction": bytes.fromhex("dc200090"),
        "stock_line": 220,
        "floor_line": 217,
        "successor_line": 217,
        "message": "TF_InitStatic() failed, tf is null.",
    },
    "TF_Init_alloc": {
        "run": 0x004917F2,
        "instruction": bytes.fromhex("f4200090"),
        "stock_line": 244,
        "floor_line": 239,
        "successor_line": 239,
        "message": "TF_Init() failed, out of memory.",
    },
    "TF_AddIdListener_full": {
        "run": 0x00491928,
        "instruction": bytes.fromhex("4ff4a6700090"),
        "stock_line": 332,
        "floor_line": 326,
        "successor_line": 327,
        "message": "Failed to add ID listener",
    },
    "TF_AddTypeListener_full": {
        "run": 0x004919AE,
        "instruction": bytes.fromhex("4ff4b1700090"),
        "stock_line": 354,
        "floor_line": 348,
        "successor_line": 349,
        "message": "Failed to add type listener",
    },
    "TF_HandleReceivedMessage_unhandled": {
        "run": 0x00491B5C,
        "instruction": bytes.fromhex("40f211200090"),
        "stock_line": 529,
        "floor_line": 523,
        "successor_line": 524,
        "message": "Unhandled message, type %d",
    },
    "TF_AcceptChar_timeout": {
        "run": 0x00491C0A,
        "instruction": bytes.fromhex("40f251200090"),
        "stock_line": 593,
        "floor_line": 587,
        "successor_line": 588,
        "message": "Parser timeout",
    },
    "TF_AcceptChar_head_checksum": {
        "run": 0x00491D50,
        "instruction": bytes.fromhex("40f292200090"),
        "stock_line": 658,
        "floor_line": 652,
        "successor_line": 653,
        "message": "Rx head cksum mismatch",
    },
    "TF_AcceptChar_payload_too_long": {
        "run": 0x00491DC2,
        "instruction": bytes.fromhex("40f2a5200090"),
        "stock_line": 677,
        "floor_line": 671,
        "successor_line": 672,
        "message": "Rx payload too long: %d",
    },
    "TF_AcceptChar_body_checksum": {
        "run": 0x00491EA2,
        "instruction": bytes.fromhex("40f2ca200090"),
        "stock_line": 714,
        "floor_line": 708,
        "successor_line": 709,
        "message": "Body cksum mismatch",
    },
}


UPSTREAM = {
    "repository": "https://github.com/MightyPork/TinyFrame.git",
    "license": {
        "spdx": "MIT",
        "path": "LICENSE",
        "git_blob_sha1": "22acaabc6b85723107caae262ec537e710c19aac",
        "size": 1072,
        "sha256": "eb7b9df3ca390100d31f9aac23f2d8dfe0183a63987112675fc58af9a42f6874",
    },
    "latest_release_reference": {
        "tag": "2.3.0",
        "tag_kind": "lightweight",
        "commit": "74d6451d5076136ed05abb486bacb850ae75d1a9",
        "tree": "3314102973f01c77583b997f0b5cdfb0acaccb41",
        "date": "2018-01-26T14:46:36+01:00",
        "TinyFrame.c_blob": "34899420d6f407c9f4be713647601c2fe51b4741",
        "TinyFrame.h_blob": "5f6943c92b8eca5c2c81f449a3490633438de277",
    },
    "source_equivalence_floor": {
        "commit": "44ecc0686c6a6b89ec357b6ab187763089e2b2bc",
        "tree": "4cb10d005bc934172a62a5a2301946fc971bb66b",
        "date": "2021-12-09T19:29:14+08:00",
        "subject": "support listener timeout function",
        "TinyFrame.c_blob": "771bc1d2c6ffbae6024f542e455a0c10209a5b2f",
        "TinyFrame.h_blob": "ca66433759f42b09edef526ca9594892283532b0",
        "TinyFrame.c_sha256": "d38ab2367f2a0eb88bd8f4f437bf063f5ad3dab69eff2c8665d78760f2e94c75",
        "TinyFrame.h_sha256": "252a093001f65cf1959da58e147bb261f36c4d47840bbc44ec292a49a3925690",
    },
    "formatting_successor": {
        "commit": "eb75483e035916ef9f3e9fce0d2ae389cb09785f",
        "tree": "0e166ad5f97162b1dbcbcafd2bfef144f68aff13",
        "date": "2021-12-09T13:29:04+01:00",
        "subject": "formatting fixes, fix demo",
        "TinyFrame.c_blob": "ac64150369dd155f26d1e47c1f5a10f92887298b",
        "TinyFrame.h_blob": "a142b4bba086f27565bd26282055c357364616b3",
        "TinyFrame.c_sha256": "24c2712966df846fadf54067ac5ed4061e4a19adf11dab1af3f203e17bf41eab",
        "TinyFrame.h_sha256": "e70ea75c3642fff3f1b28463d4b564402efcd09824b51db7b556cf3a04319b7f",
    },
    "source_equivalence_ceiling": {
        "commit": "a29167a69f052975b0e0134a73b4d31d03afa8fa",
        "tree": "2d9843138511c81f81b42b64524ff4e6b3e2fb86",
        "date": "2021-12-09T13:33:34+01:00",
        "subject": "simple demo fix",
        "TinyFrame.c_blob": "ac64150369dd155f26d1e47c1f5a10f92887298b",
        "TinyFrame.h_blob": "a142b4bba086f27565bd26282055c357364616b3",
    },
    "stable_auxiliary_blobs": {
        "TF_Config.example.h": "099d026bfd4c8c7705647958127dee002f1bac88",
        "TF_Integration.example.c": "1e1b3572021629891682e49dcf50c1e4d33bbfb6",
        "LICENSE": "22acaabc6b85723107caae262ec537e710c19aac",
    },
}


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _slice(data: bytes, start: int, end: int) -> bytes:
    first = start - LOAD_BASE
    last = end - LOAD_BASE
    if first < 0 or last < first or last > len(data):
        raise AuditError(f"run span 0x{start:08x}..0x{end:08x} is outside image")
    return data[first:last]


def _cstr(data: bytes, run: int, limit: int = 256) -> str:
    raw = _slice(data, run, min(run + limit, LOAD_BASE + len(data)))
    end = raw.find(b"\0")
    if end < 0:
        raise AuditError(f"unterminated string at 0x{run:08x}")
    try:
        return raw[:end].decode("ascii")
    except UnicodeDecodeError as exc:
        raise AuditError(f"non-ASCII string at 0x{run:08x}") from exc


def _thumb_branch_target(data: bytes, run: int) -> tuple[str, int] | None:
    first, second = struct.unpack("<HH", _slice(data, run, run + 4))
    branch_class = second & 0xD000
    if first & 0xF800 != 0xF000 or branch_class not in (0x9000, 0xD000):
        return None
    sign = (first >> 10) & 1
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    i1 = (~(j1 ^ sign)) & 1
    i2 = (~(j2 ^ sign)) & 1
    immediate = (
        (sign << 24)
        | (i1 << 23)
        | (i2 << 22)
        | ((first & 0x3FF) << 12)
        | ((second & 0x7FF) << 1)
    )
    if immediate & (1 << 24):
        immediate -= 1 << 25
    kind = "BL" if branch_class == 0xD000 else "B.W"
    return kind, (run + 4 + immediate) & 0xFFFFFFFF


def _direct_callers_for_targets(
    data: bytes, targets: dict[str, int]
) -> dict[str, list[int]]:
    names_by_target = {target: name for name, target in targets.items()}
    callers = {name: [] for name in targets}
    for offset in range(0, len(data) - 3, 2):
        run = LOAD_BASE + offset
        decoded = _thumb_branch_target(data, run)
        if decoded is None or decoded[0] != "BL":
            continue
        name = names_by_target.get(decoded[1])
        if name is not None:
            callers[name].append(run)
    return callers


def crc16_arc(data: bytes) -> int:
    """Return TinyFrame's CRC-16/ARC (init 0, xorout 0) for *data*."""

    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ (0xA001 if crc & 1 else 0)
    return crc & 0xFFFF


def resolve_request_id(next_id: int, peer_bit: int) -> tuple[int, int]:
    """Apply the exact G2 request-ID expression and uint16 counter update."""

    if not 0 <= next_id <= 0xFFFF:
        raise ValueError("next_id must fit uint16_t")
    if peer_bit not in (0, 1):
        raise ValueError("peer_bit must be 0 or 1")
    frame_id = (next_id & 0x7FFF) | (0x8000 if peer_bit else 0)
    return frame_id, (next_id + 1) & 0xFFFF


def compose_reference(
    *,
    frame_type: int,
    payload: bytes,
    next_id: int = 0,
    peer_bit: int = 0,
    is_response: bool = False,
    response_id: int = 0,
) -> tuple[bytes, int, int]:
    """Compose a G2 frame from the authenticated send-side contract.

    The return tuple is ``(wire_bytes, resolved_frame_id, next_id_after)``.
    This is a host reference only; it is not part of the production firmware.
    """

    if not 0 <= frame_type <= 0xFFFF:
        raise ValueError("frame_type must fit uint16_t")
    if len(payload) > 0xFFFF:
        raise ValueError("payload length must fit uint16_t")
    if is_response:
        if not 0 <= response_id <= 0xFFFF:
            raise ValueError("response_id must fit uint16_t")
        frame_id = response_id
        next_after = next_id
    else:
        frame_id, next_after = resolve_request_id(next_id, peer_bit)

    header = (
        b"\x01"
        + frame_id.to_bytes(2, "big")
        + len(payload).to_bytes(2, "big")
        + frame_type.to_bytes(2, "big")
    )
    wire = header + crc16_arc(header).to_bytes(2, "big")
    if payload:
        wire += payload + crc16_arc(payload).to_bytes(2, "big")
    return wire, frame_id, next_after


def _generated_crc_table() -> bytes:
    words = [crc16_arc(bytes((value,))) for value in range(256)]
    return struct.pack("<256H", *words)


def _load(path: Path = DEFAULT_IMAGE) -> bytes:
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise AuditError(f"cannot read official image: {path}") from exc
    if len(data) != IMAGE_SIZE:
        raise AuditError(f"official image size mismatch: {len(data)} != {IMAGE_SIZE}")
    digest = _sha256(data)
    if digest != IMAGE_SHA256:
        raise AuditError(f"official image SHA-256 mismatch: {digest}")
    return data


def audit(data: bytes) -> dict[str, Any]:
    if len(data) != IMAGE_SIZE or _sha256(data) != IMAGE_SHA256:
        raise AuditError("input is not the pinned G2 2.2.6.10 Apollo-main image")

    spans: dict[str, dict[str, Any]] = {}
    for name, (start, end, expected) in PINNED_SPANS.items():
        body = _slice(data, start, end)
        actual = _sha256(body)
        if actual != expected:
            raise AuditError(f"{name} span drift: {actual}")
        spans[name] = {
            "start": start,
            "end": end,
            "size": end - start,
            "sha256": actual,
        }

    if len(TINYFRAME_LINKED_SPAN_NAMES) != 31:
        raise AuditError("TinyFrame linked-function count changed")
    if not set(TINYFRAME_LINKED_SPAN_NAMES).issubset(spans):
        raise AuditError("TinyFrame linked-function span inventory is incomplete")
    linked_spans = [spans[name] for name in TINYFRAME_LINKED_SPAN_NAMES]
    if sum(item["size"] for item in linked_spans) != 2994:
        raise AuditError("TinyFrame linked code-byte count changed")
    pool_start, pool_end, pool_digest = TINYFRAME_LITERAL_POOL
    pool = _slice(data, pool_start, pool_end)
    if _sha256(pool) != pool_digest:
        raise AuditError("TinyFrame literal pool drift")
    pool_words = list(struct.unpack(f"<{len(pool) // 4}I", pool))
    if pool_words[0] != 0 or any(
        word != 0 and not (LOAD_BASE <= word < LOAD_BASE + len(data))
        for word in pool_words
    ):
        raise AuditError("TinyFrame literal pool contains an unexpected word")
    if linked_spans[0]["start"] != 0x004916C8 or linked_spans[-1]["end"] != 0x004922F6:
        raise AuditError("TinyFrame physical boundary changed")
    cursor = linked_spans[0]["start"]
    for item in linked_spans:
        if cursor == pool_start:
            cursor = pool_end
        if item["start"] != cursor:
            raise AuditError(f"TinyFrame physical tiling gap before 0x{item['start']:08x}")
        cursor = item["end"]
    if cursor != 0x004922F6:
        raise AuditError("TinyFrame physical tiling end changed")

    for run, expected in INSTRUCTION_PINS.items():
        actual = _slice(data, run, run + len(expected))
        if actual != expected:
            raise AuditError(f"instruction pin drift at 0x{run:08x}")

    sync_spans: dict[str, dict[str, Any]] = {}
    for name, (start, end, expected) in SYNC_APPLICATION_SPANS.items():
        actual = _sha256(_slice(data, start, end))
        if actual != expected:
            raise AuditError(f"{name} span drift: {actual}")
        sync_spans[name] = {
            "start": start,
            "end": end,
            "size": end - start,
            "sha256": actual,
        }

    slot_bytes = struct.pack("<I", TINYFRAME_INSTANCE_SLOT)
    slot_literal_runs = [
        LOAD_BASE + offset
        for offset in range(len(data))
        if data.startswith(slot_bytes, offset)
    ]
    if slot_literal_runs != TINYFRAME_INSTANCE_SLOT_LITERAL_RUNS:
        raise AuditError(
            "TinyFrame instance-slot literal census drift: "
            f"{[hex(run) for run in slot_literal_runs]}"
        )

    table_start, table_end, table_sha = CRC16_TABLE
    table = _slice(data, table_start, table_end)
    if _sha256(table) != table_sha or table != _generated_crc_table():
        raise AuditError("TinyFrame CRC-16/ARC table is not canonical")

    strings: list[dict[str, Any]] = []
    for run, expected in IDENTITY_STRINGS.items():
        actual = _cstr(data, run)
        if actual != expected:
            raise AuditError(f"identity string drift at 0x{run:08x}")
        strings.append({"run": run, "value": actual})

    source_lines: list[dict[str, Any]] = []
    for name, pin in SOURCE_LINE_PINS.items():
        expected = pin["instruction"]
        actual = _slice(data, pin["run"], pin["run"] + len(expected))
        if actual != expected:
            raise AuditError(f"source-line instruction drift for {name}")
        source_lines.append(
            {
                "name": name,
                "run": pin["run"],
                "stock_line": pin["stock_line"],
                "floor_line": pin["floor_line"],
                "successor_line": pin["successor_line"],
                "floor_delta": pin["stock_line"] - pin["floor_line"],
                "successor_delta": pin["stock_line"] - pin["successor_line"],
                "message": pin["message"],
            }
        )

    if [item["successor_delta"] for item in source_lines] != [
        3,
        3,
        5,
        5,
        5,
        5,
        5,
        5,
        5,
        5,
    ]:
        raise AuditError("TinyFrame successor source-line delta pattern changed")
    if [item["floor_delta"] for item in source_lines] != [
        3,
        3,
        5,
        6,
        6,
        6,
        6,
        6,
        6,
        6,
    ]:
        raise AuditError("TinyFrame floor source-line delta pattern changed")

    topology: dict[str, dict[str, Any]] = {}
    all_callers = _direct_callers_for_targets(data, TARGETS)
    for name, target in TARGETS.items():
        actual_callers = all_callers[name]
        expected_callers = EXPECTED_DIRECT_CALLERS[name]
        if actual_callers != expected_callers:
            raise AuditError(
                f"{name} caller topology drift: "
                f"{[hex(x) for x in actual_callers]} != "
                f"{[hex(x) for x in expected_callers]}"
            )
        topology[name] = {"entry": target, "direct_callers": actual_callers}

    local_write_call = _thumb_branch_target(data, 0x004D952A)
    if local_write_call != ("BL", 0x00541790):
        raise AuditError("TF_WriteImpl local transport target drift")

    transport_spans: dict[str, dict[str, Any]] = {}
    for name, (start, end, expected) in FIRST_PARTY_TRANSPORT_SPANS.items():
        body = _slice(data, start, end)
        actual = _sha256(body)
        if actual != expected:
            raise AuditError(f"{name} span drift: {actual}")
        transport_spans[name] = {
            "start": start,
            "end": end,
            "size": end - start,
            "sha256": actual,
        }
    transport_callers = _direct_callers_for_targets(
        data, {"sync_write_wrapper": 0x00541790}
    )["sync_write_wrapper"]
    if transport_callers != FIRST_PARTY_TRANSPORT_CALLERS:
        raise AuditError("first-party TinyFrame transport caller topology drift")
    if _thumb_branch_target(data, 0x00541792) != ("BL", 0x00584C98):
        raise AuditError("first-party TinyFrame transport provider target drift")
    stored_transport_pointers = []
    for offset in range(0, len(data) - 3):
        value = struct.unpack_from("<I", data, offset)[0]
        if value in (0x00541790, 0x00541791):
            stored_transport_pointers.append(LOAD_BASE + offset)
    if stored_transport_pointers:
        raise AuditError("first-party TinyFrame transport acquired a stored pointer")

    slave_golden, _, _ = compose_reference(
        frame_type=0x1234, payload=b"\x10\x20", peer_bit=0
    )
    master_golden, _, _ = compose_reference(
        frame_type=0x1234, payload=b"\x10\x20", peer_bit=1
    )
    empty_response, _, _ = compose_reference(
        frame_type=0x2222,
        payload=b"",
        is_response=True,
        response_id=0xBEEF,
    )

    return {
        "component": "TinyFrame post-2.3.0 vendor fork",
        "analysis_mode": "read-only; no hardware or flash operation",
        "image": {
            "path": str(DEFAULT_IMAGE.relative_to(ROOT)),
            "size": len(data),
            "sha256": _sha256(data),
            "load_base": LOAD_BASE,
        },
        "identity_strings": strings,
        "source_line_discriminator": {
            "sites": source_lines,
            "selected_minimum_patch_baseline": UPSTREAM["formatting_successor"][
                "commit"
            ],
            "selected_core_blobs": {
                "TinyFrame.c": UPSTREAM["formatting_successor"]["TinyFrame.c_blob"],
                "TinyFrame.h": UPSTREAM["formatting_successor"]["TinyFrame.h_blob"],
            },
            "qualification": (
                "the stable +5 delta after TF_Init matches eb75483e's one-line "
                "cleanup formatting successor plus the known G2 insertions; using "
                "44ecc068 would require an additional independent formatting-only "
                "vendor edit at the same location"
            ),
        },
        "wire_contract": {
            "SOF": {"enabled": True, "value": 0x01, "bytes": 1},
            "ID": {"bytes": 2, "wire_endian": "big"},
            "LEN": {"bytes": 2, "wire_endian": "big"},
            "TYPE": {"bytes": 2, "wire_endian": "big"},
            "HEAD_CKSUM": {
                "bytes": 2,
                "wire_endian": "big",
                "algorithm": "CRC-16/ARC",
                "coverage": "SOF || ID || LEN || TYPE",
            },
            "DATA_CKSUM": {
                "bytes": 2,
                "wire_endian": "big",
                "algorithm": "CRC-16/ARC",
                "coverage": "DATA",
                "present_only_when_len_nonzero": True,
            },
            "CRC_parameters": {
                "polynomial_normal": 0x8005,
                "polynomial_reflected": 0xA001,
                "init": 0,
                "xorout": 0,
                "reflected": True,
            },
            "RX_payload_cap": 0x6000,
            "TX_encoded_length_limit": 0xFFFF,
            "TX_explicit_payload_guard": None,
            "qualification": (
                "TinyFrame encodes uint16_t LEN but does not verify multipart bytes "
                "equal the declared length"
            ),
        },
        "peer_id_policy": {
            "request_expression": (
                "(next_id++ & 0x7fff) | (peer_bit ? 0x8000 : 0)"
            ),
            "peer_bit_mask": 0x8000,
            "counter_mask": 0x7FFF,
            "next_id_storage_bits": 16,
            "wire_request_id_period": 0x8000,
            "raw_counter_rollover": "0xffff -> 0x0000",
            "response_policy": "preserve full received frame_id; do not change peer bit",
        },
        "runtime_instance_census": {
            "instance_count": 1,
            "global_pointer_slot": TINYFRAME_INSTANCE_SLOT,
            "slot_literal_runs": slot_literal_runs,
            "allocation": {
                "kind": "dynamic",
                "vendor_bytes": 0x7160,
                "constructor_calls": [0x0045E92A, 0x0045EA2C],
            },
            "role_mapping": {
                "role_1": {
                    "name": "Master",
                    "peer_bit": 1,
                    "constructor_call": 0x0045E92A,
                },
                "role_2": {
                    "name": "Slave",
                    "peer_bit": 0,
                    "constructor_call": 0x0045EA2C,
                },
                "other": "initialization failure",
            },
            "application_pointer_uses": {
                "TF_Tick": 0x0045D4C2,
                "TF_Accept": 0x0045D530,
                "TF_Query_Multipart": 0x0045E76A,
                "TF_Multipart_Payload": 0x0045E808,
                "TF_Multipart_Close": 0x0045E858,
                "listener_registration": EXPECTED_DIRECT_CALLERS[
                    "TF_AddTypeListener"
                ],
            },
            "application_spans": sync_spans,
            "pointer_qualification": (
                "all whole-image direct entry topology and both instance-slot "
                "literal clusters use the instance as an opaque TinyFrame public-API "
                "argument; no application field dereference is retained"
            ),
            "admission_consequence": (
                "an atomic redirect set may expose the pristine core pointer at "
                "vendor allocation base + 4 while retaining the two magic words "
                "outside the core; callbacks and timeout callbacks return that same "
                "opaque core pointer"
            ),
        },
        "tx_configuration": {
            "TF_USE_MUTEX": 0,
            "lock_policy": "per-instance non-atomic soft lock; reject nested Tx",
            "TF_SENDBUF_LEN": 0x400,
            "chunk_policy": "fill 1024-byte sendbuf and flush; append body CRC at close",
            "object_fields": {
                "peer_bit": {"offset": 0x0C, "size": 1},
                "next_id": {"offset": 0x0E, "size": 2},
                "sendbuf": {"offset": 0x6021, "size": 0x400},
                "tx_pos": {"offset": 0x6424, "size": 4},
                "tx_len": {"offset": 0x6428, "size": 4},
                "tx_cksum": {"offset": 0x642C, "size": 2},
                "soft_lock": {"offset": 0x642E, "size": 1},
            },
        },
        "golden_reference_frames": {
            "slave_request_id_0_type_0x1234_data_1020": slave_golden.hex(),
            "master_request_id_0_type_0x1234_data_1020": master_golden.hex(),
            "empty_response_id_0xbeef_type_0x2222": empty_response.hex(),
        },
        "pinned_spans": spans,
        "linked_translation_unit": {
            "range": [0x004916C8, 0x004922F6],
            "physical_bytes": 3118,
            "linked_functions": len(TINYFRAME_LINKED_SPAN_NAMES),
            "code_bytes": sum(item["size"] for item in linked_spans),
            "literal_pool": {
                "range": [pool_start, pool_end],
                "size": len(pool),
                "sha256": pool_digest,
                "word_count": len(pool_words),
                "classification": "alignment word plus image-address literal pool; no executable body",
            },
            "function_names": list(TINYFRAME_LINKED_SPAN_NAMES),
            "dead_stripped_upstream_apis": [
                "TF_DeInit",
                "TF_AddGenericListener",
                "TF_RemoveIdListener",
                "TF_RemoveTypeListener",
                "TF_RemoveGenericListener",
                "TF_RenewIdListener",
                "TF_ResetParser (standalone body; calls are inlined)",
                "TF_SendSimple",
                "TF_QuerySimple",
                "TF_Send_Multipart",
                "TF_SendSimple_Multipart",
                "TF_QuerySimple_Multipart",
                "TF_Respond_Multipart",
            ],
            "qualification": (
                "the exact upstream core commit supplies every linked function name "
                "and source definition; vendor magic/logging/transport remain separate"
            ),
        },
        "direct_call_topology": topology,
        "local_boundaries": {
            "TF_WriteImpl": {
                "range": [0x004D9522, 0x004D9530],
                "behavior": (
                    "ignores TinyFrame* and forwards (buffer, length, timeout=100) "
                    "to first-party entry 0x00541790"
                ),
                "classification": "application transport; not upstream TinyFrame",
            },
            "first_party_transport": {
                "wrapper": transport_spans["sync_write_wrapper"],
                "direct_callers": transport_callers,
                "provider": transport_spans["transport_provider"],
                "provider_entry": 0x00584C98,
                "stored_entry_pointers": stored_transport_pointers,
                "abi": "(buffer, length, timeout) -> 0 on provider success, -1 otherwise",
                "classification": (
                    "complete reusable first-party wrapper over an authenticated retained "
                    "transport provider; no TinyFrame object-layout dependency"
                ),
            },
            "application_send_callers": {
                "response_builder_calls": EXPECTED_DIRECT_CALLERS["TF_Respond"],
                "sync_multipart_begin": 0x0045E76A,
                "sync_multipart_payload": 0x0045E808,
                "sync_multipart_close": 0x0045E858,
            },
            "callbacks": (
                "message/listener callbacks and timeout callbacks are application-owned; "
                "only their TinyFrame registration/invocation ABI is in scope"
            ),
        },
        "upstream_provenance": UPSTREAM,
        "version_recovery": {
            "classification": "post-2.3.0 official TinyFrame lineage with vendor patches",
            "exact_vendor_commit_or_tree": None,
            "exact_released_tag": None,
            "narrowest_official_core_source_state_interval": {
                "first": UPSTREAM["formatting_successor"]["commit"],
                "last": UPSTREAM["source_equivalence_ceiling"]["commit"],
                "first_date": UPSTREAM["formatting_successor"]["date"],
                "last_date": UPSTREAM["source_equivalence_ceiling"]["date"],
            },
            "exact_core_blob_introducing_commit": UPSTREAM["formatting_successor"][
                "commit"
            ],
            "exact_core_blobs": {
                "TinyFrame.c": UPSTREAM["formatting_successor"]["TinyFrame.c_blob"],
                "TinyFrame.h": UPSTREAM["formatting_successor"]["TinyFrame.h_blob"],
            },
            "lower_bound": (
                "the G2 five-argument SendFrame/Query path carries both listener and "
                "listener-timeout callback; official history first completes that "
                "send-side ABI at 44ecc068"
            ),
            "why_release_2_3_0_is_excluded": (
                "tag 2.3.0 predates TF_Listener_Timeout and its five-argument "
                "TF_SendFrame/TF_Query topology"
            ),
            "source_line_discriminator": (
                "ten retained TF_Error __LINE__ values select eb75483e's textual core "
                "layout as the minimum-patch baseline and exclude 44ecc068 from the "
                "narrowed reusable core interval"
            ),
            "why_checkout_commit_remains_ambiguous": (
                "a29167a changes only demo content and retains eb75483e's exact "
                "TinyFrame.c/TinyFrame.h blobs, so linked firmware cannot distinguish "
                "the two repository checkouts"
            ),
            "vendor_divergences": [
                "G2 adds object magic values 0xa5a5a5a5 at +0 and 0x5a5a5a5a at +0x715c",
                "the magic prefix shifts upstream public/internal object fields by four bytes",
                "G2 replaces TF_Error and TF_WriteImpl with application logging/transport glue",
                "G2 uses a private TF_Config.h absent from official history",
            ],
            "vendoring_decision": (
                "reuse official MIT TinyFrame send sources from the authenticated interval, "
                "but keep G2 configuration, magic bookends, transport, logging and callbacks "
                "in a reviewed port/vendor patch layer; do not claim a pristine tag drop-in"
            ),
        },
        "remaining_validation": [
            "capture real G2 frames and compare them to the host reference vectors",
            "bind the now-authenticated retained first-party transport wrapper in the atomic source promotion",
        ],
    }


def _render_text(report: dict[str, Any]) -> str:
    version = report["version_recovery"]
    interval = version["narrowest_official_core_source_state_interval"]
    return "\n".join(
        [
            "G2 TinyFrame send/version recovery: PASS",
            f"  image: {report['image']['sha256']}",
            "  wire: SOF(01) + ID/LEN/TYPE(2-byte BE) + CRC-16/ARC",
            "  head CRC coverage: SOF || ID || LEN || TYPE",
            "  TX buffer / lock: 1024 bytes / per-instance soft lock",
            f"  official core-source interval: {interval['first'][:8]}..{interval['last'][:8]}",
            "  core blob introducing commit: eb75483e",
            "  exact vendor checkout/tag: unresolved (a29167a is core-identical)",
            "  tag 2.3.0: excluded by listener-timeout send ABI",
            "  local TF_WriteImpl: isolated at 0x004d9522 -> 0x00541790",
            "  hardware operations: none",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--json", action="store_true", help="emit JSON report")
    args = parser.parse_args()
    report = audit(_load(args.image))
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(_render_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
