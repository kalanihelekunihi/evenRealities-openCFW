#!/usr/bin/env python3
"""Fail-closed audit for the linked G2 Cordio DM connection manager."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
BUILD_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
SOURCE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
SOURCE = ROOT / "components/shared/cordio/runtime_cordio_dm_conn.c"
HEADER = ROOT / "components/shared/cordio/runtime_cordio_dm_conn.h"
DM_DEV_HEADER = ROOT / "components/shared/cordio/runtime_cordio_dm_conn_dm_dev.h"
WSF_MSG_HEADER = ROOT / "components/shared/cordio/runtime_cordio_dm_conn_wsf_msg.h"
RUNTIME_TEST = ROOT / "tests/test_runtime_cordio_dm_conn.py"
PACKAGE = ROOT / "build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
FLASH_PLAN = ROOT / "build/source/flash-plan.json"
LOAD_BASE = 0x00437FE0
IMAGE_BYTES = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
READINESS_MANIFEST = ROOT / "research/readiness/dm-conn/SHA256SUMS"
READINESS_BYTES = 1_213
READINESS_SHA256 = "f056c5a9df9d769f782dd03c7fb60b451002119e7a91d30d9fba4523159ccc7e"
PINNED_INPUTS = {
    ROOT / "tools/manifests/packetcraft-cordio-dm-conn-function-map.tsv": "6c8c2f4bc569e534a05a658cff97709630cbd329f5c2edf1ffafc95dc083fd2d",
    ROOT / "tools/manifests/packetcraft-cordio-dm-conn-provenance.tsv": "58c994082bbadfbd844d1dbc6827ba9ebebf9c3ed74fac21daf71093307b4f7b",
    ROOT / "tools/manifests/readiness-cordio-dm-conn-build-results.tsv": "f04096a49c678eef52df9ddec5dc68ba275b23057f0cf73718bde6ee0e65ba74",
    ROOT / "tools/manifests/readiness-cordio-dm-conn-closure-results.tsv": "2981afe9a3b48a139f1079f237f8e9136316061c71049e147b49137505e1c0ef",
    ROOT / "tools/manifests/readiness-cordio-dm-conn-include-closure.tsv": "9311cab0efd370cd30ab051067ac9f842a5508552c8fef6e0388d9874d8ae932",
    ROOT / "tools/manifests/readiness-cordio-dm-conn-source-identities.tsv": "b0cb1935b7bc4399b709fe16a48e52d43628c8043ec7c2edec051460c09f0413",
    ROOT / "tools/manifests/readiness-cordio-dm-conn-undefined-providers.tsv": "4df1a30bc9d4ccfacbe35f13ffd9bf09ff8d0ef1a9e513f1d6aab6e423fc5145",
}

FUNCTIONS = [
    ("dmConnCmplStates", 0x004B5B24, 0x004B5C78, "ce503526bb1f88789c398a8f70e65fee70294ca2b02ad46b735d20b27ad6cb54"),
    ("dmConnCcbAlloc", 0x004B5C78, 0x004B5EEA, "022515e620a28f57768156598fa8e6e46d660b24a8bf7a9a6de771a0b95fb31a"),
    ("dmConnCcbDealloc", 0x004B5EF0, 0x004B6012, "79a073268ea26e1ac4000aee4dcb755ce68fa4d8f0b834f458e901f23d60cff8"),
    ("dmConnCcbByHandle", 0x004B601C, 0x004B6166, "f260e15e6cbe9d5dd6c508c440bc7de462961ef7bcd664531c558a013298941f"),
    ("dmConnCcbByBdAddr", 0x004B6170, 0x004B62A8, "350d89da95c9fe5333c83d0ee257996ff36902157d7bb31dd2406fc1260ae3e1"),
    ("dmConnCcbById", 0x004B62A8, 0x004B62CA, "3831366a64cd437a15b98c1b252627c44f08c2d966fee0eb85b4ddb9a201e1fd"),
    ("dmConnNum", 0x004B62CA, 0x004B62EA, "4daa881ecc18516245ed5ca59dc0293955ab2f393be6cfa062a4783930a167c3"),
    ("dmConnExecCback", 0x004B62EA, 0x004B6320, "2170583c2ecc0a0f4c7296adde734ee009184e86204abe2288a7c0b002774a96"),
    ("dmConnOpenAccept", 0x004B6324, 0x004B63CA, "52d449574049f13ac1c4b853cec15606c54a85211a8caf9ed3b0d14ee2ffe7d9"),
    ("dmConnSmActNone", 0x004B63CA, 0x004B63CC, "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"),
    ("dmConnSmActClose", 0x004B63CC, 0x004B63D8, "719427d25cdf22bfb04fef0848602265bdb1f67730b3ec1b14c5507dddd8a151"),
    ("dmConnSmActConnOpened", 0x004B63D8, 0x004B6484, "5925d613985f6b5ae2f161cc045fd1ec1a7c3a82e0754196ce139934e794c00d"),
    ("dmConnSmActConnFailed", 0x004B6488, 0x004B64CE, "349e2a5a5788a8aad14f25faf17e9cc2c6591cdbc8606e925e82985b2b726a9b"),
    ("dmConnSmActConnClosed", 0x004B64CE, 0x004B6508, "799755830ed1d65f90bf478dc4c139b5ba855c9702222bc601f503d01d926808"),
    ("dmConnSmActHciUpdated", 0x004B6508, 0x004B651A, "8971a65b8fb5614b8e086ec2f293792e29df71e60999686cd8efc250933e5555"),
    ("dmConnUpdActNone", 0x004B6530, 0x004B6532, "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"),
    ("dmConnUpdExecute", 0x004B6532, 0x004B67CA, "4fd855b479ad55c2edacd8ca7ab07348dd109641ed4ac9d194ec84433c010100"),
    ("dmConnReset", 0x004B67EC, 0x004B687E, "90539a1f6549c3ebf38cbb6cfe5b4ff26dc4911da89ccc1b87b95a622fd657b2"),
    ("dmConnMsgHandler", 0x004B6888, 0x004B68A4, "491effc39cce2306e232a003fef0ea04bc0a240556821b99ee5ae8ae8f7fda82"),
    ("dmConnHciHandler", 0x004B68A4, 0x004B6914, "be097a83a931265ea34a7f346ded43f86fc466fd678e4c9590252972418a6441"),
    ("dmConn2MsgHandler", 0x004B6914, 0x004B6990, "09505437ae0a0821777771e9f8b5ffa66b6bba953a44227555d7be23e2cbecab"),
    ("dmConn2HciHandler", 0x004B6990, 0x004B6A16, "c635f69ff7a2ba57377e2fbd5992d89b717b0ae3c54f99aabe48348b482c151a"),
    ("dmConnUpdMsgHandler", 0x004B6A16, 0x004B6A38, "5770a3331b880b0679cabe18561df91ff60a0ccb4641ae847711e403d8b270f2"),
    ("dmConn2ActRssiRead", 0x004B6A38, 0x004B6A6E, "d510057f146768606955fe38dc13f7d19583e659c1e18c4246c140b8e3f9030f"),
    ("dmConn2ActRemoteConnParamReq", 0x004B6A6E, 0x004B6AB0, "b73c951d1a12f28a8b4cf16063636405079a41f055bfe2e5c800b6c3eaf757f4"),
    ("dmConn2ActDataLenChange", 0x004B6AB8, 0x004B6AFA, "152acc011be97acc1d723c4a9d4d2a2873aa897301c83c7dc128527a4e1fa445"),
    ("dmConn2ActWriteAuthToCmpl", 0x004B6AFA, 0x004B6B28, "f88edf3bb49bdc9dbd17d10d57a98039dd86689a375b7b7a30bae91748d9d345"),
    ("dmConn2ActAuthToExpired", 0x004B6B28, 0x004B6B50, "48e1458b10790d862bf36341a85baae376a3363710c04098af9a8ee3af2a6c90"),
    ("dmConn2ActReadRemoteFeaturesCmpl", 0x004B6B50, 0x004B6BA6, "8a4b493969b1d55b20ca5732404ff096d2b90582c5162f85bb5636ca4d04b910"),
    ("dmConn2ActReadRemoteVerInfoCmpl", 0x004B6BAC, 0x004B6BEE, "e7a53db7964dbe59c9721c077b23ecfe438f803ff781fecb5265984ea2cd64e3"),
    ("dmConn2ActReqPeerSca", 0x004B6BEE, 0x004B6C24, "f0ee383d112d289365db4b66173d7bc195bd7d2ed984c178ca02394bd9d6a3b8"),
    ("DmConnInit", 0x004B6C28, 0x004B6C5E, "3da3eece6b1e2832d809916eef75615fe10042da256f94f60a545ca7e78ecdfb"),
    ("DmConnRegister", 0x004B6C64, 0x004B6C82, "308fbf629182897349d5ec11c32113b72c7f667f7092a5aa52389525ad4c2177"),
    ("DmConnClose", 0x004B6C82, 0x004B6CB0, "83270604af11a1c7b7f305bf48416e517abd361856e8be1f475e0329ff5a8867"),
    ("DmReadRemoteFeatures", 0x004B6CB0, 0x004B6D26, "89af16c12e47a7cb07710f2b0e00c5caacdb9f4db6e08bf0acdada0cdb989c2e"),
    ("DmConnUpdate", 0x004B6D26, 0x004B6D68, "8c3ca78b0330a14cf509b517b8ba4c798ffca024ccd5f8ba7041c4428dc2a16b"),
    ("dmConnSetConnSpec", 0x004B6D68, 0x004B6D96, "d1a7fbb3c2d8f9b086d259463aabbfa63ff477a8198e5f52f58147c5fce414a5"),
    ("dmConnSetScanInterval", 0x004B6D96, 0x004B6DCA, "c4e701678873f63beaddd3ef20abb23790ab784188c622c40f0775f9e26bca24"),
    ("DmConnSetScanInterval", 0x004B6DD4, 0x004B6DE6, "4fe87973349185229575dbb33d7de762581e21b8523a298df037005f622d185f"),
    ("DmConnSetConnSpec", 0x004B6DE6, 0x004B6DF2, "0c81bfe618a50b36bb36ff18152b8d8de692d1631a1bce41ce722e02eb0a37e5"),
    ("DmConnReadRssi", 0x004B6DF2, 0x004B6E14, "ae0db46a54703576fd0935ede681cbc7d90a74926c3d47a8b107b5cf255233a5"),
    ("DmRemoteConnParamReqReply", 0x004B6E14, 0x004B6E46, "e21500704b42d6598f89febc2b2ae13cfd6590185844e3dee25433032d353345"),
    ("DmRemoteConnParamReqNegReply", 0x004B6E46, 0x004B6E6C, "006bf33a20907abb2bbaa8255d5a64fa17206da0924efd23b7d36c298e1f79fd"),
    ("DmConnSetDataLen", 0x004B6E6C, 0x004B6E96, "f7092d7a5b06519b956df362435a59048fe1bb61aab37545d9069163957b3d38"),
    ("DmConnIdByHandle", 0x004B6E96, 0x004B6EC6, "8dabfd34d24479662c7f500069f8602add075f2c93d572d3467a56763f55a0d4"),
    ("DmConnInUse", 0x004B6EC6, 0x004B6ED8, "79b5672edbbaa230e743f8a5b977e2a2686b395f3207f66ae03524712ea70456"),
    ("DmConnPeerAddrType", 0x004B6ED8, 0x004B6EEA, "5bc964510fc31029896fe9c02d515faaf5904b166d5cf77d6c25b75546c41023"),
    ("DmConnPeerAddr", 0x004B6EEA, 0x004B6EFA, "9d835a56ef7832c5d3bb9c34a1b754d8550a03965c8d885fe30da36b6f08d8dd"),
    ("DmConnLocalAddrType", 0x004B6EFA, 0x004B6F0C, "3d7388cb7060eabeb9d12225460d0b233c4b5d955e84f6122bd85dc257d3a1e7"),
    ("DmConnLocalAddr", 0x004B6F0C, 0x004B6F1C, "84185a2df5bf4b4d88ee650950dfccea84d548dd8c7f0cc7ece692351e4158b2"),
    ("DmConnPeerRpa", 0x004B6F28, 0x004B706E, "c9a89604163cd81aaadce32a77d67d5032bcd7329acaa21deef78b242f47cc96"),
    ("DmConnLocalRpa", 0x004B707C, 0x004B71B2, "dfa6a88395d9d0a98b7630a40ad302c7e407d87e2f2d37a3ec57eae462b3fd7d"),
    ("DmConnSecLevel", 0x004B71B2, 0x004B71C2, "9c498ec025ce45d9fe151d8d338601f4f149a660fa07ed552b04648ad8ef66f3"),
    ("DmConnSetIdle", 0x004B71DC, 0x004B73A2, "9878b1ff7d08ac1950168630c24760c2aedb7737b7da072fb1597ad861a852b2"),
    ("DmConnCheckIdle", 0x004B73A2, 0x004B73C4, "482a1dbf7d611166c9a6e0c4e76ba6c27eb36f598be1a64eed4cd5b9eb134713"),
    ("DmConnRole", 0x004B73C4, 0x004B73E8, "aa08098f8c152a022a9e29fe6b36a3f1b9369f5a2e41944aa9a45bde69147b74"),
    ("vendorCcbInitLike", 0x004B73E8, 0x004B7426, "23e38581dfb944943c7ce9eb257d270f1bbf737a455ef177f6ec38f26f5c9aca"),
]

CALLERS: dict[str, list[int]] = {
    "dmConnCmplStates": [0x004B68C6],
    "dmConnCcbAlloc": [0x004B6344, 0x004B68E2],
    "dmConnCcbDealloc": [0x004B63BC, 0x004B6490, 0x004B64DE],
    "dmConnCcbByHandle": [0x004B68FA, 0x004B6996, 0x004C5748, 0x004D236C, 0x0055BCA0, 0x0056E586],
    "dmConnCcbByBdAddr": [0x004B6338, 0x004B68BA],
    "dmConnCcbById": [0x004B6890, 0x004B691C, 0x004B6A1E, 0x004B6CB4, 0x004C5822, 0x004D2448, 0x0055BBCC, 0x005E2686, 0x005E270A],
    "dmConnNum": [0x004B645C, 0x004B64A6, 0x004B64E8],
    "dmConnExecCback": [0x004B647E, 0x004B64C8, 0x004B6502],
    "dmConnOpenAccept": [0x0055BCDE],
    "dmConnSmActConnOpened": [0x00536AFE],
    "dmConnSmActConnFailed": [0x00536AEA, 0x00536B12],
    "dmConnUpdExecute": [0x004B6A32, 0x0055BCBA, 0x0056E59E],
    "dmConnHciHandler": [0x004B681C],
    "dmConn2ActRssiRead": [0x004B69C8],
    "dmConn2ActRemoteConnParamReq": [0x004B69D2],
    "dmConn2ActDataLenChange": [0x004B69DC],
    "dmConn2ActWriteAuthToCmpl": [0x004B69E6],
    "dmConn2ActAuthToExpired": [0x004B69F0],
    "dmConn2ActReadRemoteFeaturesCmpl": [0x004B69FA],
    "dmConn2ActReadRemoteVerInfoCmpl": [0x004B6A04],
    "dmConn2ActReqPeerSca": [0x004B6A0E],
    "DmConnInit": [0x004B801A],
    "DmConnRegister": [0x004B5140, 0x004B7ED2, 0x00537CF2],
    "DmConnClose": [0x004BB054],
    "DmReadRemoteFeatures": [0x004BACE8],
    "DmConnUpdate": [0x00476D86],
    "dmConnSetConnSpec": [0x004B6DEC],
    "dmConnSetScanInterval": [0x004B6DE0],
    "DmConnSetScanInterval": [0x0049F98E, 0x004A0446],
    "DmConnSetConnSpec": [0x0049F982],
    "DmConnReadRssi": [0x004A0A6A, 0x004A1482],
    "DmRemoteConnParamReqReply": [0x004B392C, 0x00503B5E],
    "DmRemoteConnParamReqNegReply": [0x004B393E, 0x00503B70],
    "DmConnSetDataLen": [0x004B3FC0],
    "DmConnIdByHandle": [0x00530784, 0x00530AAA, 0x00531A82, 0x005351AE, 0x00536C6C, 0x00536EAE, 0x005375CC],
    "DmConnInUse": [0x004B71EC, 0x004C4702, 0x0053195A, 0x00535062],
    "DmConnPeerAddrType": [0x004B3A32, 0x004B3A52, 0x005034FA, 0x00503516, 0x00532ACE, 0x0053778A, 0x005377A8, 0x00541FCA],
    "DmConnPeerAddr": [0x004A0F00, 0x004A1D82, 0x004A28AA, 0x004B369C, 0x004B3898, 0x004B38BC, 0x004B3A2A, 0x004D8F70, 0x005034F0, 0x00532AC4, 0x005378B6, 0x005378D6, 0x00541FDA],
    "DmConnLocalAddrType": [0x0053776C, 0x005377C6],
    "DmConnLocalAddr": [0x00537898, 0x005378F4],
    "DmConnPeerRpa": [0x00537776, 0x00537794, 0x005378A2, 0x005378C2],
    "DmConnLocalRpa": [0x00537758, 0x005377B2, 0x00537884, 0x005378E0],
    "DmConnSecLevel": [0x004B468C, 0x0050382A, 0x00503FDA, 0x0052C632, 0x00532D50, 0x0056C6A6, 0x0056E680],
    "DmConnSetIdle": [0x004D23C8, 0x004D23F4, 0x004D2464, 0x004D249A, 0x00532142, 0x00532C32, 0x00532D02, 0x00532E38, 0x00533198, 0x0053341C, 0x005335D8, 0x00534C52, 0x00534D1E, 0x0056CFFA, 0x0056D064, 0x0056D0B8, 0x0056D10C, 0x0056E666, 0x0056EE40, 0x005E3126, 0x005E3A24],
    "DmConnCheckIdle": [0x00476CC6, 0x00476CDE, 0x00476D1E, 0x00534AEE],
    "DmConnRole": [0x0046E118, 0x0046E12E, 0x0046E2C2, 0x0046E32A, 0x0046E4D4, 0x00477AF4, 0x00477B32, 0x00477CBE, 0x004785A6, 0x004A0768, 0x004A0786, 0x004A08DA, 0x004A094A, 0x004A098A, 0x004A09B0, 0x004A0A7E, 0x004A0B4E, 0x004A0B8E, 0x004A0BB6, 0x004A0EEA, 0x004A117E, 0x004A13B0, 0x004A1424, 0x004A14AC, 0x004A1D72, 0x004B6D3C, 0x004B7720, 0x004B77BE, 0x004B7AF0, 0x004B7BFC, 0x004B7D6A, 0x004B7DA8, 0x004B7DCA, 0x004B7DE8, 0x004BAD06, 0x004BDC86, 0x004BDF2A, 0x004BE2A2, 0x004BE474, 0x004BE7C0, 0x004BF7F0, 0x004BF80A, 0x004C4A6A, 0x004C4A7E, 0x004C4B40, 0x00530796, 0x00531368, 0x00532AB2, 0x00535628, 0x00535662, 0x0053567C, 0x005357B0, 0x00535818, 0x0053585E, 0x005358A8, 0x005358EA, 0x0053593A, 0x005359E6, 0x00535ABE, 0x00535AE2, 0x00535B28, 0x00535F46, 0x00535FCE, 0x005374C8, 0x005374E0, 0x0053751A, 0x0056E97A, 0x0056F0F0],
    "vendorCcbInitLike": [0x004B80F2],
}

CODE_SPAN = (0x004B5B24, 0x004B7426)
CODE_SPAN_SHA256 = "f27a2e992a01a2485dc94cfd982022f36f9264645e47fa7bba182c1e45ab33ab"
BODY_SHA256 = "0d23d0e293c47d791d1022ed70fd70795f6e1329b46740c10e6dd39f9c188e5a"
TRAILING_POOL = (0x004B7426, 0x004B7478)
TRAILING_POOL_SHA256 = "c2eaf1b6030c2459cb65801ba0cfacecfcc51a9ea0a28a241c41708e64a38e77"
PHYSICAL_SPAN = (0x004B5B24, 0x004B7478)
PHYSICAL_SPAN_SHA256 = "0fa4bda2fd946ce20605f08b8f824a9818367e29eb9df709f3393f2e8952d77f"
SOURCE_PATH = 0x006DFFB4
SOURCE_PATH_BYTES = (
    b"D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\"
    b"ble-host\\sources\\stack\\dm\\dm_conn.c\x00"
)
SOURCE_PATH_SHA256 = "fb0c5cd7e73cdea3137a824f1c8d0145162d5045e61ccbffc6620e5fc2664381"
SOURCE_PATH_POINTER_CELLS = [0x004B652C, 0x004B67E8, 0x004B7460]

TABLES = [
    ("main_actions", 0x00776A84, "<6I", [0x004B63CB, 0x004B63CD, 0x004B63D9, 0x004B6489, 0x004B64CF, 0x004B6509], "2c2e775c29d848cb785fbf15f8aa77cb18dd20071cdb886895df9ed7e7e9ef91"),
    ("update_main_action", 0x0078EFEC, "<I", [0x004B6531], "a284d2e8df91047c695bbd971efe1620ba0e24452dbb3e7c3f02a6b7d8f70997"),
    ("update_action_map", 0x0078EFF0, "<4B", [0x10, 0x20, 0x11, 0x21], "2ddcbe8db040031c70d8f302e8ac00e958995aba6dbfd3305d1152d72af76714"),
    ("connection_defaults", 0x0078A814, "<6H", [24, 40, 0, 2000, 0, 0], "05eb3c6f5d8fcf2525762b800755a2aebb5dd6037dd71783666a3085a7a39ef3"),
    ("main_interface", 0x0078A820, "<3I", [0x004B67ED, 0x004B68A5, 0x004B6889], "a1d09c077ae5b9eb381e563660a4f7516a71d0c69b45f4b45503ecdfd6fc442c"),
    ("secondary_interface", 0x0078A82C, "<3I", [0x004D29BF, 0x004B6991, 0x004B6915], "5fa0889f47b5b8d0fcafecc5e01c49f4df10d0ed306c899c246b55bd169820b3"),
    ("update_interface", 0x0078A838, "<3I", [0x004D29BF, 0x004D29C1, 0x004B6A17], "4571701c8d79f59c4d8e8296969adcd270a2f2d945e6fd4b04473c638218af33"),
]

EXPECTED_ENTRY_POINTERS = {
    0x00776A84: 0x004B63CB, 0x00776A88: 0x004B63CD,
    0x00776A8C: 0x004B63D9, 0x00776A90: 0x004B6489,
    0x00776A94: 0x004B64CF, 0x00776A98: 0x004B6509,
    0x0078EFEC: 0x004B6531,
    0x0078A820: 0x004B67ED, 0x0078A824: 0x004B68A5,
    0x0078A828: 0x004B6889, 0x0078A830: 0x004B6991,
    0x0078A834: 0x004B6915, 0x0078A840: 0x004B6A17,
}
EXPECTED_UNALIGNED_ACCIDENTALS = {0x006448D7: 0x004B6C00}

PRODUCTION_FILES = {
    SOURCE: (57_608, "dddabc1e01fffd815f1e496ea8a50927dd62a8ef01b15a944312cf3cc2110437"),
    HEADER: (1_232, "6a4d0cd43f27a39934de68c56f4ed750ac941b5a82290af7f68bcc18ef3ac7fe"),
    DM_DEV_HEADER: (5_940, "a8bd504dfeae6b7d450a3512b6af3801201c56235f7b8ca2bb40cd9652d05e90"),
    WSF_MSG_HEADER: (5_294, "3b0b6fd4a07b3b98ff4463c2e570da2e4b2d3dfaef5c161c12be838002aa058b"),
    RUNTIME_TEST: (10_450, "d7941f51e9779b266307b7efdbbd1ff812c0a06a794e26d0d68b1ce0fb8ba54b"),
}
PRODUCTION_OVERLAY = (362_272, "8c80c3fa53a89c77d145533f59f63389dfa31f968642f783323ed81ac81be5ae")
PRODUCTION_COMPONENT = (3_956_672, "79323dd5ae9211e9d1c393f26593c98c96c53d928c44c4447c946e67ef0fbeef")
PRODUCTION_PACKAGE = (4_750_780, "49c61010614d5db51c9e97f3ca549e47644a32805411d0ff5dc96ea7445d3e27")
PRODUCTION_FLASH_PLAN = (4_961_300, "f2625775d8a7b3c81c8862db00979cdcf4965eeb003e4b6b84e8cb2d8c1293b9")

SOURCE_ONLY = [
    "DmReadRemoteVerInfo", "DmExtConnSetScanInterval",
    "DmExtConnSetConnSpec", "DmWriteAuthPayloadTimeout",
    "DmConnRequestPeerSca",
]


class AuditError(RuntimeError):
    """Raised when authenticated DM connection-manager evidence changes."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - LOAD_BASE:end - LOAD_BASE]


def _load_decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("dm_conn_thumb", path)
    if spec is None or spec.loader is None:
        raise AuditError("cannot load Thumb decoder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _all_callers(blob: bytes, decoder: Any) -> dict[int, list[int]]:
    callers = {start: [] for _, start, _, _ in FUNCTIONS}
    for address in range(LOAD_BASE, LOAD_BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in callers:
            callers[target].append(address)
    return callers


def _occurrences(blob: bytes, value: int) -> list[int]:
    packed = struct.pack("<I", value)
    return [
        LOAD_BASE + offset
        for offset in range(len(blob) - 3)
        if blob[offset:offset + 4] == packed
    ]


def _verify_entry_pointers(blob: bytes) -> None:
    targets = {
        address | thumb
        for _, start, end, _ in FUNCTIONS
        for address in range(start, end, 2)
        for thumb in (0, 1)
    }
    found: dict[int, int] = {}
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        if value in targets:
            found[LOAD_BASE + offset] = value
    if found != EXPECTED_ENTRY_POINTERS | EXPECTED_UNALIGNED_ACCIDENTALS:
        raise AuditError("DM connection stored entry/interior pointer closure changed")


def _verify_file(path: Path, expected: tuple[int, str], label: str) -> None:
    data = path.read_bytes()
    if (len(data), _sha256(data)) != expected:
        raise AuditError(f"{label} changed")


def _verify_production() -> dict[str, Any]:
    for path, expected in PRODUCTION_FILES.items():
        _verify_file(path, expected, f"DM connection production input {path.name}")

    names = [name for name, _start, _end, _hash in FUNCTIONS]
    source_path = SOURCE.relative_to(ROOT).as_posix()
    config = json.loads(CONFIG.read_text())
    if (
        config.get("expected", {}).get("overlay_size") != PRODUCTION_OVERLAY[0]
        or config.get("expected", {}).get("overlay_sha256") != PRODUCTION_OVERLAY[1]
        or config.get("expected", {}).get("component_size") != PRODUCTION_COMPONENT[0]
        or config.get("expected", {}).get("component_sha256") != PRODUCTION_COMPONENT[1]
    ):
        raise AuditError("DM connection production aggregate pins changed")

    leaves = [
        row for row in config.get("relocated_leaves", [])
        if row.get("source", {}).get("path") == source_path
    ]
    if [row.get("function") for row in leaves] != names:
        raise AuditError("DM connection production leaf inventory changed")
    if any(
        row.get("strict_relocation_contract") is not True
        or row.get("allow_discarded_alloc_sections") is not True
        for row in leaves
    ):
        raise AuditError("DM connection whole-translation-unit policy changed")

    sites = [
        row for row in config.get("patch_sites", [])
        if row.get("name", "").startswith("replace_cordio_dm_conn_core_")
    ]
    if len(sites) != len(FUNCTIONS):
        raise AuditError("DM connection production route count changed")
    for index, ((name, start, end, expected_hash), site) in enumerate(
        zip(FUNCTIONS, sites), 1
    ):
        expected_branch = "copy" if index in (10, 16) else "b_w"
        if site != {
            "branch": expected_branch,
            "expected_sha256": expected_hash,
            "expected_size": end - start,
            "name": f"replace_cordio_dm_conn_core_{index:02d}",
            "profiles": ["apple-clang"],
            "runtime_address": start,
            "target_function": name,
        }:
            raise AuditError(f"DM connection production route changed: {name}")

    report = json.loads(BUILD_REPORT.read_text())
    built = [
        row for row in report.get("relocated_leaves", [])
        if row.get("source", {}).get("path") == source_path
    ]
    metrics = (
        len(built),
        sum(row["extraction"]["size"] for row in built),
        sum(row["placement"]["padding_before"] for row in built),
        sum(row["extraction"]["relocation_count"] for row in built),
    )
    if metrics != (57, 4_540, 54, 92):
        raise AuditError("DM connection production leaf metrics changed")
    if (
        (report["overlay"]["size"], report["overlay"]["sha256"])
        != PRODUCTION_OVERLAY
        or (report["component"]["size"], report["component"]["sha256"])
        != PRODUCTION_COMPONENT
    ):
        raise AuditError("DM connection production build changed")

    manifest = json.loads(SOURCE_MANIFEST.read_text())
    override = manifest["component_overrides"]["apollo_main"]
    provider = override["provider"]
    if (provider.get("size"), provider.get("sha256")) != PRODUCTION_COMPONENT:
        raise AuditError("DM connection production provider changed")
    regions = [
        row for row in override["regions"]
        if row["name"].startswith("cordio_dm_conn_core_")
    ]
    statuses = {
        status: sum(row["address_status"] == status for row in regions)
        for status in (
            "generated_source_entry_replacement",
            "source_compiled",
            "generated_alignment",
        )
    }
    if len(regions) != 141 or statuses != {
        "generated_source_entry_replacement": 57,
        "source_compiled": 57,
        "generated_alignment": 27,
    }:
        raise AuditError("DM connection production manifest ownership changed")

    _verify_file(PACKAGE, PRODUCTION_PACKAGE, "DM connection package")
    _verify_file(FLASH_PLAN, PRODUCTION_FLASH_PLAN, "DM connection flash plan")
    flash = json.loads(FLASH_PLAN.read_text())
    counts = tuple(len(flash[key]) for key in (
        "flash_regions", "unresolved_flash_regions",
        "container_only_regions", "protected_regions",
    ))
    if counts != (7104, 0, 8, 6):
        raise AuditError("DM connection flash-plan counts changed")
    return {
        "status": "production-routed",
        "production_owned_stock_functions": 57,
        "guarded_redirects": 55,
        "exact_in_place_copies": 2,
        "production_owned_stock_bytes": 6_216,
        "source_owned_bytes_added": 4_540,
        "alignment_bytes_added": 54,
        "strict_relocations": 92,
        "manifest_regions": 141,
        "source_only_functions_compiled": 5,
        "flash_plan_counts": counts,
    }


def analyze(image: Path = IMAGE) -> dict[str, Any]:
    if image.stat().st_size != IMAGE_BYTES:
        raise AuditError("official G2 image size changed")
    blob = image.read_bytes()
    if _sha256(blob) != IMAGE_SHA256:
        raise AuditError("official G2 image SHA-256 changed")
    if READINESS_MANIFEST.stat().st_size != READINESS_BYTES:
        raise AuditError("Lorelei DM connection artifact size changed")
    if _sha256(READINESS_MANIFEST.read_bytes()) != READINESS_SHA256:
        raise AuditError("Lorelei DM connection artifact changed")
    for path, expected in PINNED_INPUTS.items():
        if _sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned DM connection input changed: {path}")

    decoder = _load_decoder()
    all_callers = _all_callers(blob, decoder)
    bodies = []
    reports = []
    for name, start, end, expected_hash in FUNCTIONS:
        body = _slice(blob, start, end)
        if _sha256(body) != expected_hash:
            raise AuditError(f"DM connection stock span changed at 0x{start:08x}")
        expected_callers = CALLERS.get(name, [])
        if all_callers[start] != expected_callers:
            raise AuditError(f"DM connection caller closure changed for {name}")
        bodies.append(body)
        reports.append({
            "name": name,
            "start": start,
            "end_exclusive": end,
            "size": end - start,
            "sha256": expected_hash,
            "direct_bl_callers": expected_callers,
        })
    if _sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("DM connection concatenated body identity changed")
    if _sha256(_slice(blob, *CODE_SPAN)) != CODE_SPAN_SHA256:
        raise AuditError("DM connection code/data interval changed")
    if _sha256(_slice(blob, *TRAILING_POOL)) != TRAILING_POOL_SHA256:
        raise AuditError("DM connection trailing pool changed")
    if _sha256(_slice(blob, *PHYSICAL_SPAN)) != PHYSICAL_SPAN_SHA256:
        raise AuditError("DM connection physical interval changed")

    table_reports = []
    for name, address, fmt, values, expected_hash in TABLES:
        size = struct.calcsize(fmt)
        data = _slice(blob, address, address + size)
        if _sha256(data) != expected_hash or list(struct.unpack(fmt, data)) != values:
            raise AuditError(f"DM connection table changed: {name}")
        table_reports.append({"name": name, "address": address, "bytes": size})
    if _slice(blob, SOURCE_PATH, SOURCE_PATH + len(SOURCE_PATH_BYTES)) != SOURCE_PATH_BYTES:
        raise AuditError("DM connection retained source path changed")
    if _sha256(SOURCE_PATH_BYTES) != SOURCE_PATH_SHA256:
        raise AuditError("DM connection source-path hash changed")
    if _occurrences(blob, SOURCE_PATH) != SOURCE_PATH_POINTER_CELLS:
        raise AuditError("DM connection source-path pointer closure changed")
    _verify_entry_pointers(blob)

    linked_bytes = sum(end - start for _, start, end, _ in FUNCTIONS)
    direct_sites = sum(len(CALLERS.get(name, [])) for name, *_ in FUNCTIONS)
    return {
        "schema_version": 1,
        "image": {"path": str(image), "sha256": IMAGE_SHA256},
        "module": {
            "start": CODE_SPAN[0],
            "code_end_exclusive": CODE_SPAN[1],
            "physical_end_exclusive": PHYSICAL_SPAN[1],
            "physical_bytes": PHYSICAL_SPAN[1] - PHYSICAL_SPAN[0],
            "linked_function_count": len(FUNCTIONS),
            "linked_public_source_functions": 56,
            "linked_vendor_helpers": 1,
            "linked_function_bytes": linked_bytes,
            "interstitial_bytes": (CODE_SPAN[1] - CODE_SPAN[0]) - linked_bytes,
            "trailing_pool_bytes": TRAILING_POOL[1] - TRAILING_POOL[0],
            "direct_bl_ingress_sites": direct_sites,
            "stored_entry_pointers": len(EXPECTED_ENTRY_POINTERS),
            "rejected_unaligned_nonpointer_sequences": len(EXPECTED_UNALIGNED_ACCIDENTALS),
            "unexpected_entry_or_interior_pointers": 0,
            "unexpected_exterior_interior_branches": 0,
            "functions": reports,
            "tables": table_reports,
            "source_only_dead_stripped": SOURCE_ONLY,
        },
        "upstream": {
            "selected_commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "earliest_compatible_commit": "eeb34839755da1c19cc85b8795cc863483c16ef0",
            "selected_blob": "746a7c107ac779a296552056c27488d3f94acd21",
            "selected_sha256": "4bc0ba3452eeab625a763f0597fe6e85e4b0c12c3c47c8368af412cc88480a69",
            "classification": "r20.05 architecture plus Ambiq 2.5.1 trace suppression and product validation patches",
            "license": "Apache-2.0",
        },
        "abi": {
            "dm_conn_max": 3,
            "dm_client_id_max": 5,
            "dm_num_phys": 2,
            "ccb_size": 0x30,
            "control_block_address": 0x200712A4,
            "control_block_size": 0xC4,
            "callback_array_offset": 0x90,
            "connection_specs_offset": 0xA4,
            "scan_interval_offset": 0xBC,
            "scan_window_offset": 0xC0,
            "message_allocation_bytes": 0x24,
        },
        "readiness": {
            "archive_sha256": READINESS_SHA256,
            "source_inventory_functions": 61,
            "conservative_anchor_functions": 9,
            "conservative_anchor_bytes": 3652,
            "compiler_profiles": 2,
            "provider_seams": 30,
            "valid_non_vacuous_closures": 2,
            "linked_unresolved_symbols": 0,
        },
        "production": _verify_production(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=IMAGE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = analyze(args.image)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        module = report["module"]
        print(
            f"dm_conn: {module['linked_function_count']} functions, "
            f"{module['linked_function_bytes']} code bytes, "
            f"{len(module['source_only_dead_stripped'])} source-only APIs"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
