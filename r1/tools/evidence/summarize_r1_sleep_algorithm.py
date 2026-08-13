#!/usr/bin/env python3
"""Validate R1 sleep stages, postprocessing, statistics, score, temperature, and public ABI.

This parser is static, read-only, and pinned to application 2.2.6.0009. It verifies the complete
sleep-stage/interval/finalization chain, the classifier feature/decision boundary, both embedded
model inventories, and can cross-check the recovered first-party controller app enum objects. It
never runs the proprietary classifier, reads live SRAM, controls PPG, or starts the temperature
timing service.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import struct
from pathlib import Path
from typing import Any

from summarize_r1_adc_registry import DEFAULT_BASE, mapped_offset
from summarize_r1_gomore_call_graph import direct_thumb_branches_to
from summarize_r1_gomore_output_abi import FIELDS as OUTPUT_FIELDS, IMAGE_SHA256


EXPECTED_FIRST_PARTY_OBJECTS_SHA256 = (
    "4ef3494669dfc5788b32e661231305eb30ee08a9455e2e2f57f2dc6c21b86209"
)

EXPECTED_RANGE_SHA256 = {
    (0x00060B80, 0x00060DC2): "828077a17339e6bc16d6ebe03928c943b7cd1082814d34ae614c385820830671",
    (0x00060DC4, 0x000610BE): "37097a9f2b9fd50f489637a25b004b48f4955d6342d553d64eae4b61e20a302b",
    (0x00067558, 0x000675DA): "7e240d4c82e834f8fc3dd1399c300b9bfd93b31ee276dcba8926cd3f379d85db",
    (0x000692E4, 0x000694EA): "1c546888e33ff9d062036986b8f6f9d90b5afb5ea1a4e71bf7355cdab4d849a7",
    (0x00058B70, 0x00058C38): "87d08976835376549e5bab7e13da07212ebcff651fa99ebfcd78662bbe52c1b4",
    (0x0005C19C, 0x0005C3F6): "e7e33708f50892a7d4c8046a573042166f2f6453193445d73dbb9aaf8c0349d8",
    (0x00088450, 0x0008889E): "daa79d5c7cdf1ca4d1dbe17ac3f60a6568064957d72345b17e7d4f0afb94b433",
    (0x000684B4, 0x000684F8): "1793933811ece9b370921112db61d5ec1afda9bcc6c29ce89df85292248adf8a",
    (0x0008ED2C, 0x0008ED5C): "9ad616620c8b5912223e87d343482b95a48bf183fae60634399be632e266f42a",
    (0x00064174, 0x000641C0): "8f57877ed9e0f80046ba43931104edbc037b2d1e0db2ae257be74838a2abd28c",
    (0x00069644, 0x0006982C): "52c8c02346ed2c9884eacf16748ab6c5eff64cb83f734d000c24d498553fda28",
    (0x0008FA3C, 0x0008FC04): "911b449775ba6e13dd05f6ce00e8e6668bb4bfb62746e73375b1e743082f0a81",
    (0x0008F728, 0x0008F780): "70053885e974a76be0bf8f4ceb72766445f41c632fcfc289ea27646619b517e3",
    (0x0006C294, 0x0006C456): "878e793fcc609eb152861de0bbe30e8fea40307cc98e819b13932716aa1b12e2",
    (0x00067BBC, 0x00067C2A): "3d467a358cd30e0d79b07931877c8c6e8717fee2711f43496a69d934fbaf230d",
    (0x0004A704, 0x0004A78A): "27704d1f5294b814fd2ba6be219f3dd716876ff3645ff96585d1ef9a225944d6",
    (0x00068F8C, 0x000692E4): "e0e528a6b45e4838d049914efc5d35d9ef5443b0dccc4b437ef46f0a7b77829a",
    (0x0006778C, 0x00067A40): "9c5b5d3e8c40990d739b7782675fb39075e697de917614197e1cd7dc524c084c",
    (0x00072AF0, 0x00072B34): "1de1935875541210e0e8e58c246e7fb2ef1254841788bd43ecb99153ebbe9d37",
    (0x000748D4, 0x00074914): "f43d3858a6da1bafbdeae6dc6bb78ddd717fad491d8b06f26938a3642bc878f2",
    (0x0004B4B0, 0x0004B560): "12b6f933a9720395ec7c56804a35c193fbddd0ecf530a1a16f434e8e56d19df7",
    (0x0004B5B0, 0x0004B698): "2764e24d411b90d5f88b11d2037b7100c5ec7ec64ed85303da981fe0fbda80c4",
    (0x0004B698, 0x0004BD54): "e231ed80789def5305ed4cd39aff6886a6d62f190afac35d720b29592d4f20fc",
    (0x00081040, 0x000813CC): "7cda2106a0834fd98614f96f67dcbdeabf9d14e2ae8eb0aaf76ddb96512a34eb",
    (0x0008F0F0, 0x0008F230): "ff72b615604fb6a692535be2ce9b74a7a78891bac62c90f9da83f7d06cf6ef7b",
    (0x000881F4, 0x00088262): "bd1e7245cc3afdd4fb7bce66df7d9783e042811f3d09524c104239cdd5c23a9a",
    (0x00064CC8, 0x00064EEC): "8d7b0b545daf965812da604cbf7e3256d2dce271d8736f5746b3978dcf2dbe2e",
    (0x00069546, 0x00069644): "452a82b18dc924ccc11f269931df974397b6d2c6e616dee27689cb300b9f302a",
    (0x000B1BDE, 0x000B1C2B): "f7f1e779b990f9a42babc7265060ebd86c078a9499e836c4afb6e8435d638407",
    (0x00088AAC, 0x00088BD0): "9fc4b441384995e0725eee7fa4f98ff0ce49f0b5cedcdccb257dcd01c4e5c8e0",
    (0x00074D60, 0x00074F1C): "08125f60fc8703ce02d40c81bd2f156b4091558c92943745fe73b7dc4a18fb02",
    (0x00076502, 0x0007655E): "1624f5f2c14b887720f2e7ceec2462061a318cab0c0f41ef715a5747f05f3a30",
    (0x00064B06, 0x00064B28): "8fd451003756af10cdccefa1b4f06667f7d34902614fc656e8df8ca1b4c2b100",
    (0x0007D0A8, 0x0007D0D8): "ad58000e495863cd583274552f7c1eb660731deb839f8a44b13394d7bf7186fd",
    (0x0004ECE0, 0x0004ED14): "093da9a6e7e7a28a2caed013aaec827eb655f72191f15684031b3e197b009e0e",
    (0x0005F264, 0x0005F3D8): "110113dfb4503676837f280da4ab0d2e75ade17c539286c70f163f056ffc8e5d",
    (0x0005F3D8, 0x0005F4B6): "4d4ed646ba3e8cad56053fe854ab539f026a8f0371ae59ce066d246c54b2f581",
    (0x000B1C4C, 0x000B2444): "9031bf8dfb015b6a34cbbce0e7b868324d766bf4ab0e98fc40aff55b2ad36d19",
    (0x000B2444, 0x000B2458): "56abcfa859f970cbcb89f2c3911a95931b38cfd109c25230e949015851e2e529",
    (0x000B2458, 0x000B7998): "da353b02976da84378f6321b2f5ec7cbc4c184eb706b1d6a7fad5499258c4861",
    (0x000B7998, 0x000BCED8): "09f807f0c73daae139a0f2aa39ec37b4c57db8c6a7178e943aec6bd8913ee82c",
    (0x000651A4, 0x0006570A): "525847e4d689e0fada041cdfff4bcc2bc4c32ae5ae4db99d0b6171601b31d029",
    (0x00070758, 0x00070778): "be5f41c0c9c9a80ec7b6d6d72ded886cc0b9d2a3ccb578f2c4e5ff830ec75bb4",
    (0x000711AA, 0x000711B4): "8a280cb99ccdcf46c2d7928851c6c1c236f5502c17bc1510074831ca1b1e15db",
    (0x00071594, 0x000715D4): "6dc0407609e63fe7bc85ae7b25a7c6a8bf28cf7f3795f1cf7c0fdad1d28e9a8a",
    (0x00071618, 0x000716FE): "92521e5a222f60332ff7fd43616c271d343efe7d7d71eedce9885c6a8ccd8168",
    (0x00071A10, 0x00071A32): "2b9a1c5dd08952a823e2dec5432529b5a4ff1272a8873e6fce4ee32a67799d8b",
    (0x0009196E, 0x00091F4E): "cda26899a038b1f79895b43f0e6d17b2a2043d6507543665e3d6dd8b6bb03234",
    (0x0008F49C, 0x0008F4B4): "4a6d354d9870c5323d26f51a42612488eccd79558d670938dae0574926e17aa2",
    (0x0007D09C, 0x0007D0A8): "90e8db1c4218cea4a6d0b8bfb3599ff589e62348c9b0160696c2decc158a8687",
    (0x00038F08, 0x000390B2): "4f3d4ee50c320aecc71bcb95e91a94f1eb69a88f1ba1c662cad4bebbb31e50a7",
    (0x00090F44, 0x00090FA6): "0f731bfb323eca39e4dee9f1a7f0d7efdcefdbf3ae78cfe98b2628b3195fd323",
    (0x0005D360, 0x0005D370): "a90e9243a5b0fade62ae83172371078aff5d0f411d6fc43318875f9f21f595d8",
    (0x00060AF4, 0x00060B80): "12d3035001204a689ec65ffb69d895aa9492a06ea921af23bb0f45b26432ba12",
    (0x0008EE3A, 0x0008EEBA): "2e75714d8700c08b91663d04cf7ae21702f3f5de6f69e4542870ea47ecb065e9",
    (0x00058AB8, 0x00058AEE): "eb5e7a1631f2af8cdf31b6c00fd306cf2822e5400920fa6cc8a5422658a0552e",
    (0x00064A28, 0x00064A80): "b6012b791726b3721741085e4bb8ad8a7ed5fce98a0ffa29857e8f311ae260ee",
    (0x000649BC, 0x00064A1E): "a6bbbbc8fdedeb244391b3bf3b071e0168f56398ccb9d0ba116dada6f60ec74d",
    (0x0004EC6C, 0x0004EC9C): "edca9db7a6c2fa45f3f015b5a79629284215735eededee3a8ce33000d3f2a3cd",
    (0x00088264, 0x000882AC): "2092d6055a351ac27acfa87b6f1133a8461796f08ffcdf9bce9028d0b2b37afd",
    (0x00059D70, 0x00059D9A): "dd789b1d2f28bc7cd6df262383a403c4de13c19c45d8aadef67779734e074f5a",
    (0x000641F0, 0x00064274): "6c0b833717454f2abb2366d9e030e1190883d78be762f50caa6ba5a61329745e",
    (0x000711B4, 0x0007158A): "1a926930d168d429b5bf2cfdcd4cfeae2ac63e26936b9fa31db5da0a7ed4a046",
    (0x00071CA0, 0x00071CCE): "4ffc52c78f0ce3cd0c977f35da4cd71c0cb8aa2e2de6009e46d1bb24523c810d",
    (0x00071D62, 0x00071D96): "ae74a6fa9963d9ba6f11e63ff88960f538d9fad9b4ac4872777a1eb3d88b4405",
    (0x000882EC, 0x000883AC): "d7f3bc6c0b31c30f3af85fba0dfa4c3396441c98c71bb42602693c0e8e1c37b4",
    (0x0006B228, 0x0006B272): "ab337651b4344af149b261e8c0e733690a02df92bffcb5b79ee4370e7b8b3134",
    (0x00094590, 0x00094694): "e0ec2adb814118836f143c52750a75bc91ffc913845942ddab6de0f7f9a82fb8",
    (0x00060A14, 0x00060ADC): "713f3edee450b41bc42c1e03614a6b0c734b81c7dde98f7c3cfad68d166d109c",
    (0x0008247E, 0x000824A0): "56d908ecf435762995f15ab709bc7eda434df7e298ac106117c2a5a8eca3bacb",
    (0x00071C38, 0x00071C96): "041775ed84150275910c3dcfd3938a74a8889a5f65f53cd0e0bb63307ff33741",
    (0x0006FEA0, 0x0006FFCE): "482c62c9526c4a26994f6d69906e68b5186edbac94e1b5b5e62ba523b6e6b7c6",
    (0x0006B114, 0x0006B1B8): "12d48128ccaab3563434e1020cafeae53af5c37848aa5e7df228776cfd3139e4",
    (0x00060990, 0x00060A14): "4b59a597ae573618dd97e248ea64a263f52946ea76678790a038cb45ac5e7879",
    (0x0008245C, 0x0008247E): "014afbbf7c8ef87df68c1938c85c69169e0198d890f9880d36d4ad296e1a26a2",
    (0x00058464, 0x0005847E): "10df81361601ab0879c25ecda7c3a5ba0c3cfa1804c4af1a32eff8e9e2f5b9a9",
    (0x00071154, 0x0007116C): "dfeb49ccade56d1a7d39b99b77113520a753bb063f56b4cd51cd9d76b6f32822",
    (0x0007116C, 0x0007118C): "9d6091053bdd7f7048d8628502977886e2af17f33a6c398e574674a62942bc10",
    (0x000764DC, 0x00076502): "3172097e69cac5f368437a4de46b752bf9da3dfd89b2e4deb7fd9680a7f59bc0",
    (0x00074914, 0x00074A20): "7a1a5fa63af5300303ba5d36b25dee6a21a83237ee1baa5e46309148b3ad3fed",
    (0x0005CBC0, 0x0005CBF0): "3ccffc940440de8c3a86809669f28352b60bd5cc68820e2de1a615d4d841a3d7",
    (0x00059E60, 0x00059EE4): "a080b9878de3957dc2575f23f5a81851fbfad4e2111ad1dc50995fde46c11d48",
    (0x00039220, 0x00039290): "3e0962080c766b9f40a3e86e78268df6a4c5fd863bea8533b277842c9cd5290b",
    (0x0008F688, 0x0008F6F8): "0d44a5a63e86d138583e1e9539803ee265eca5d3ae07d56cfb7511ccc4c92b69",
    (0x00067750, 0x0006778C): "ad7700c32f6c85325f0c84cf406bc90fe9d690cd4460a7929dd89781969a2991",
    (0x000B1A6C, 0x000B1A94): "42afd065e32ea1883731a6ddb6af540bc2ff8f3e8f2d4015af844dedbb8951a0",
    (0x000BD2E4, 0x000BD32C): "ac3058f6d4a563a47ab135c98abccc616cb92f5e9d68949a24a50ab285e01031",
}

EXPECTED_DIRECT_BRANCHES = {
    0x00060B80: [0x000603BA, 0x000603E4],
    0x00060DC4: [0x00060480, 0x00060498],
    0x00067558: [0x00060D08, 0x000724BC, 0x000725EA],
    0x000692E4: [0x0006757C],
    0x00058B70: [0x0006759E],
    0x0005C19C: [0x00060C90],
    0x00088450: [0x00060EB4],
    0x0008ED2C: [0x00060E30, 0x00061040, 0x000641AE, 0x00068394, 0x000683B8,
                0x000726B2],
    0x00064174: [0x00060DE8],
    0x00069644: [0x000726F0],
    0x0008FA3C: [0x0004A710],
    0x0008F728: [0x0008FBFA],
    0x0006C294: [0x0006B104],
    0x00067BBC: [0x0006B5F6, 0x0006C39E],
    0x0004A704: [0x0006B5FE, 0x0006C3A6],
    0x00068F8C: [0x00068FC4],
    0x00068FBC: [0x0006971E, 0x000697A8, 0x00081156, 0x00081216, 0x0008130E,
                0x00081366],
    0x00068FD4: [0x00068FA4],
    0x00069128: [0x00068FB4],
    0x0006778C: [0x00068FCA],
    0x00072AF0: [0x0006966A],
    0x000748D4: [0x0006978E],
    0x0004B4B0: [0x0004B9E6, 0x0004BCCC],
    0x0004B5B0: [0x0008FBE6],
    0x0004B698: [0x0004A238],
    0x0004BAD0: [0x0004BD58],
    0x00081040: [0x00069708],
    0x0008F0F0: [0x00081120, 0x0008112C],
    0x000881F4: [0x00081134],
    0x00064CC8: [0x000811EE, 0x000811FC],
    0x00069546: [0x00064CF2, 0x00064DBC, 0x00064E14, 0x0008F114],
    0x00088AAC: [0x00060E8A],
    0x00076502: [0x00060E96],
    0x00074D60: [0x00088B96],
    0x00064B06: [0x00074D90, 0x00074F08],
    0x0007D0A8: [0x00088874],
    0x0004ECE0: [0x00060EF2, 0x00060F74, 0x00060FCA, 0x00091A5A],
    0x0005F264: [0x00060342, 0x00060356],
    0x0005F3D8: [0x0006018C, 0x0006019C],
    0x00090F44: [0x00060DFC],
    0x0005D360: [0x00060E10, 0x000726BA, 0x00090F52],
    0x00060AF4: [0x00060426, 0x00060436],
    0x0008EE3A: [0x00060B22],
    0x00058AB8: [0x00060B2A],
    0x00064A28: [0x00060B3A],
    0x000649BC: [0x00060B4A],
    0x0004EC6C: [0x000649F0],
    0x00088264: [0x00060B5A],
    0x00059D70: [0x00060B64],
    0x000641F0: [0x00058AEA, 0x00082476, 0x0008249C, 0x0009492C],
    0x000711B4: [0x00071D84],
    0x00071CA0: [0x00071AC2, 0x0008EE4C],
    0x00071D62: [0x00071C62, 0x00071C82, 0x00071CC6, 0x00071E24],
    0x000882EC: [0x00058ADC, 0x0005F42E, 0x000614F8, 0x0008246C, 0x0008248E],
    0x00094590: [0x000944AE],
    0x00060A14: [0x000945BC],
    0x0008247E: [0x00060A72],
    0x00071C38: [0x0006FF62],
    0x0006FEA0: [0x0004BF9A, 0x0004BFE6],
    0x00060990: [0x00094646],
    0x0008245C: [0x000609D6],
    0x00058464: [0x0005F402, 0x00071172],
    0x0007116C: [0x00071A7A],
    0x000764DC: [0x0005F436],
    0x00074914: [0x0005F44A],
    0x0005CBC0: [0x0005F454],
    0x00059E60: [0x0005F45A],
    0x00039220: [0x00035E96, 0x0003644E, 0x000365D6, 0x00059EAE, 0x000767FC,
                 0x00076808],
    0x0008F688: [0x0005F470],
    0x00071154: [0x0005F340, 0x00071AE2],
    0x00067750: [0x0005F36A],
}

EXPECTED_FLOAT32 = {
    0x00058C38: 0.0,
    0x00058C3C: 0.32,
    0x000694EC: 0.7,
    0x000694F0: 100.0,
    0x000694F4: 0.85,
    0x000694F8: 0.21,
    0x000694FC: 0.0,
    0x0005C3F8: 0.96,
    0x0005C3FC: 0.0,
    0x0005C400: 100.0,
    0x0005C404: 0.4,
    0x0005C408: 0.3,
    0x0006911C: 0.0,
    0x00069120: 2880.0,
    0x00069124: 2880.0,
    0x000692D8: 0.0,
    0x000692DC: 2880.0,
    0x000692E0: 2880.0,
    0x000679D0: 0.0,
    0x000679D8: 95.0,
    0x000679E4: 89.0,
    0x000679F0: 74.0,
    0x000679F4: 59.0,
    0x000679F8: 60.0,
    0x000679FC: 100.0,
    0x00067A00: 40.0,
    0x00067A04: 1.1,
    0x00067A08: 0.11,
    0x00067A0C: 3.26,
    0x00067A14: 0.1,
    0x00067A1C: 0.2,
    0x00067A20: 0.3,
    0x00067A24: 0.4,
    0x00067A34: 0.05,
    0x00067A3C: 100.0,
    0x0006982C: 0.0,
    0x00069830: 10.0,
    0x0008FC64: 100.0,
    0x0008FC68: 60.0,
    0x000813CC: 0.18,
    0x000813D0: 0.225,
    0x000813D4: 0.1,
    0x000813DC: 0.35,
    0x00088BC4: 37.5,
    0x00088BC8: 60.0,
    0x00088BCC: 0.2,
    0x00074F1C: 60.0,
    0x0007D0D4: 0.01,
    0x000610C0: 0.01,
    0x000610C4: 1.496979475,
    0x0004ED10: -1_000_000_000.0,
    0x00071CD0: 0.016,
    0x00071CD4: 0.16,
    0x0007158C: 3.1415927410125732,
    0x00071C98: 0.0104,
    0x00071C9C: 0.96,
}

EXPECTED_UINT32 = {
    0x000679D4: 0xBC4C0000,  # -Float32-bit-pattern(360)
    0x000679DC: 0xBC6A0000,  # -Float32-bit-pattern(300)
    0x000679E0: 0xBC100000,  # -Float32-bit-pattern(480)
    0x000679E8: 0xBC790000,  # -Float32-bit-pattern(270)
    0x000679EC: 0xBC010000,  # -Float32-bit-pattern(510)
    0x00067A10: 0xC2333333,  # -Float32-bit-pattern(0.1)
    0x00067A18: 0xC1E66666,  # -Float32-bit-pattern(0.15)
    0x00067A28: 0x0099999A,
    0x00067A2C: 0xC1B33333,  # -Float32-bit-pattern(0.2)
    0x00067A30: 0x004CCCCE,
    0x00067A38: 0x00666667,
    0x00072B30: 86_400,
    0x000813D8: 0x00B33332,  # Float-bit distance from 0.1 through 0.25
    0x0008F230: 0x80000001,  # parity mask; only bit zero is reachable for run lengths
}

POSTPROCESSOR_PROFILE_TABLE_ADDRESS = 0x000B1BDE
CLASSIFIER_DESCRIPTOR_TABLES = {
    "modes_below_100": (0x000B1C4C, 0x000B2458, 0x000B7998),
    "modes_at_least_100": (0x000B2048, 0x000B7998, 0x000BCED8),
}
CLASSIFIER_DESCRIPTOR_COUNT = 51
CLASSIFIER_DESCRIPTOR_BYTES = 20
EXPECTED_POSTPROCESSOR_PROFILES = {
    0: bytes.fromhex("00010700020064ec0a000a"),
    1: bytes.fromhex("01000000000278000a07ef"),
    2: bytes.fromhex("02000b00060278000a07ef"),
    3: bytes.fromhex("03000b000a03a0000a00f6"),
    100: bytes.fromhex("64010700020078e711f90f"),
    101: bytes.fromhex("64010700060078e711f90f"),
    102: bytes.fromhex("64010700020078e711f90f"),
}

EXPECTED_FLOAT64 = {
    0x0004B550: 0.01,
    0x0004B558: 0.1,
    0x0004B690: 0.1,
    0x00064A20: 7.5,
}

OPTICAL_FILTER_NUMERATOR_BITS = [
    0x3D1D6014, 0x00000000, 0xBD9D6014, 0x00000000, 0x3D1D6014,
]
OPTICAL_FILTER_DENOMINATOR_BITS = [
    0x3F800000, 0xC0552C25, 0x408676E0, 0xC01980F5, 0x3F071CB3,
]
RAW_OPTICAL_PREFILTER_NUMERATOR_BITS = [
    0x3F64E157, 0x00000000, 0xBFE4E157, 0x00000000, 0x3F64E157,
]
RAW_OPTICAL_PREFILTER_DENOMINATOR_BITS = [
    0x3F800000, 0xBE0647AA, 0xBFE271CE, 0x3DD66071, 0x3F4CA43A,
]
RAW_ACCELEROMETER_PREFILTER_NUMERATOR_BITS = [
    0x3F6A3B6A, 0x3FEA3B6A, 0x3F6A3B6A,
]
RAW_ACCELEROMETER_PREFILTER_DENOMINATOR_BITS = [
    0x3F800000, 0x3FE94E11, 0x3F565189,
]
MOTION_FILTER_NUMERATOR_BITS = [
    0x3C87D6D4, 0x00000000, 0xBD07D6D4, 0x00000000, 0x3C87D6D4,
]
MOTION_FILTER_DENOMINATOR_BITS = [
    0x3F800000, 0xC06425DA, 0x4099D857, 0xC03A6D39, 0x3F2BA321,
]
MOTION_GATE_WEIGHT_BITS = [
    0xBC74E45F, 0xBC307364, 0xBC3AABE4, 0xBC425615, 0xBC36586D,
    0xBC2E6D76, 0xBC2ABB77, 0xBC3C334A, 0xBC5C10B1, 0xBC43123B,
    0xBC3D049D, 0xBC5251C5, 0xBC50B8CE, 0xBC795147, 0xBC92BF25,
    0xBCD9F826, 0xBD120A28, 0xBD8D8A4A,
]

EXPECTED_DIAGNOSTICS = {
    0x0006C467: " [RING]Sleep Period On, %d",
    0x0006C484: "Sleep Period On, %d",
    0x0006C498: "[RING]Sleep Period Off, %d",
    0x0006C4B4: "Sleep Period Off, %d",
    0x0006C50C: "[RING]Sleep Stage PPG On",
    0x0006C528: "Sleep Stage PPG On",
    0x0008FC04: "[RING]stage_num:%d",
    0x0008FC20: "stage_num:%d",
    0x0004B8CC: "[RING]algo temp timing mode timer %d create",
    0x0004B8F8: "algo temp timing mode timer %d create",
    0x0004BB80: "[RING]algo temp sleep status change: %d",
    0x0004BBB0: "algo temp sleep status change: %d",
    0x0008DF9C: "[RING]efficiency:%d, score:%d, total_time:%d, body_temp:%d",
    0x0008DFD8: "efficiency:%d, score:%d, total_time:%d, body_temp:%d",
}


def flash_bytes(image: bytes, base: int, start: int, end: int) -> bytes:
    offset = mapped_offset(start, base, len(image))
    return image[offset:offset + (end - start)]


def unpack_float32(image: bytes, base: int, address: int) -> float:
    return struct.unpack("<f", flash_bytes(image, base, address, address + 4))[0]


def unpack_uint32(image: bytes, base: int, address: int) -> int:
    return struct.unpack("<I", flash_bytes(image, base, address, address + 4))[0]


def unpack_float64(image: bytes, base: int, address: int) -> float:
    return struct.unpack("<d", flash_bytes(image, base, address, address + 8))[0]


def c_string(image: bytes, base: int, address: int) -> str:
    offset = mapped_offset(address, base, len(image))
    return image[offset:image.index(b"\0", offset)].decode("ascii")


def enum_objects(text: str, class_name: str) -> dict[str, dict[str, int]]:
    pattern = re.compile(
        rf"Obj!{re.escape(class_name)}@[^ ]+ : \{{\s*"
        rf"Super!_Enum : \{{\s*off_8: int\((0x[0-9a-f]+)\),\s*"
        rf'off_10: "([^"]+)"\s*\}},\s*off_14: int\((0x[0-9a-f]+)\)',
        re.IGNORECASE,
    )
    result: dict[str, dict[str, int]] = {}
    for ordinal, name, wire_value in pattern.findall(text):
        result[name] = {"ordinal": int(ordinal, 0), "wire_value": int(wire_value, 0)}
    return result


def summarize(image_path: Path, base: int, first_party_objects: Path | None) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != IMAGE_SHA256:
        raise ValueError(f"unexpected image SHA-256: {digest}")

    verified_ranges = []
    for (start, end), expected_digest in EXPECTED_RANGE_SHA256.items():
        actual = hashlib.sha256(flash_bytes(image, base, start, end)).hexdigest()
        if actual != expected_digest:
            raise ValueError(
                f"unexpected sleep range 0x{start:08x}...0x{end:08x}: {actual}"
            )
        verified_ranges.append({
            "start": f"0x{start:08x}",
            "end_exclusive": f"0x{end:08x}",
            "sha256": actual,
        })

    branches: dict[str, list[str]] = {}
    for target, expected_callsites in EXPECTED_DIRECT_BRANCHES.items():
        actual = [address for address, _ in direct_thumb_branches_to(image, base, target)]
        if actual != expected_callsites:
            raise ValueError(
                f"unexpected branches to 0x{target:08x}: {actual} != {expected_callsites}"
            )
        branches[f"0x{target:08x}"] = [f"0x{item:08x}" for item in actual]

    constants: dict[str, float | int] = {}
    for address, expected in EXPECTED_FLOAT32.items():
        actual = unpack_float32(image, base, address)
        if not math.isclose(actual, expected, rel_tol=0, abs_tol=1e-6):
            raise ValueError(f"unexpected Float32 at 0x{address:08x}: {actual}")
        constants[f"0x{address:08x}"] = actual
    for address, expected in EXPECTED_UINT32.items():
        actual = unpack_uint32(image, base, address)
        if actual != expected:
            raise ValueError(f"unexpected UInt32 at 0x{address:08x}: 0x{actual:08x}")
        constants[f"0x{address:08x}"] = actual
    for address, expected in EXPECTED_FLOAT64.items():
        actual = unpack_float64(image, base, address)
        if not math.isclose(actual, expected, rel_tol=0, abs_tol=1e-12):
            raise ValueError(f"unexpected Float64 at 0x{address:08x}: {actual}")
        constants[f"0x{address:08x}"] = actual
    reset_gap = unpack_uint32(image, base, 0x000641C0)
    if reset_gap != 86_400:
        raise ValueError(f"unexpected stage-history reset gap: {reset_gap}")
    constants["0x000641c0"] = reset_gap

    postprocessor_profiles: dict[str, dict[str, Any]] = {}
    for index, (mode, expected) in enumerate(EXPECTED_POSTPROCESSOR_PROFILES.items()):
        start = POSTPROCESSOR_PROFILE_TABLE_ADDRESS + index * 11
        actual = flash_bytes(image, base, start, start + 11)
        if actual != expected:
            raise ValueError(
                f"unexpected postprocessor profile {mode} at 0x{start:08x}: {actual.hex()}"
            )
        postprocessor_profiles[str(mode)] = {
            "address": f"0x{start:08x}",
            "raw_record": actual.hex(),
            "source_start_offset_epochs": actual[1],
            "moving_majority_radius": actual[2],
            "chunk_majority_width": actual[4],
            "force_last_epoch_awake": bool(actual[3] & 1),
            "classifier_model_family": "modes_below_100" if mode < 100 else "modes_at_least_100",
            "motion_gate_mode": actual[5],
            "motion_gate_threshold_raw": actual[6],
            "motion_gate_threshold": actual[6] * 0.01 * 1.496979475,
            "score_offset_hundredths": list(struct.unpack("<bbbb", actual[7:11])),
        }

    fallback = flash_bytes(image, base, 0x000B2444, 0x000B2458)
    expected_fallback = struct.pack("<ffffBxxx", -1.0, -1.0, -1.0, -1.0, 0xFF)
    if fallback != expected_fallback:
        raise ValueError(f"unexpected classifier fallback output: {fallback.hex()}")

    classifier_models: dict[str, Any] = {}
    common_layout: list[tuple[int, int, int]] | None = None
    for family, (table_address, data_start, data_end) in CLASSIFIER_DESCRIPTOR_TABLES.items():
        descriptors = []
        cursor = data_start
        layout: list[tuple[int, int, int]] = []
        for index in range(CLASSIFIER_DESCRIPTOR_COUNT):
            start = table_address + index * CLASSIFIER_DESCRIPTOR_BYTES
            data_address, element_count, shape, storage, scale_bits = struct.unpack(
                "<IIIII", flash_bytes(image, base, start, start + CLASSIFIER_DESCRIPTOR_BYTES)
            )
            storage_code = storage >> 16
            element_bytes = 1 if storage_code == 0x0E else 2
            if storage_code not in {0x05, 0x07, 0x0E}:
                raise ValueError(
                    f"unexpected classifier storage 0x{storage:08x} at descriptor {index}"
                )
            if data_address != cursor:
                raise ValueError(
                    f"non-contiguous classifier data at {family} descriptor {index}: "
                    f"0x{data_address:08x} != 0x{cursor:08x}"
                )
            scale = struct.unpack("<f", struct.pack("<I", scale_bits))[0]
            if storage_code == 0x0E and not scale > 0:
                raise ValueError(f"non-positive quantization scale at {family} descriptor {index}")
            if storage_code != 0x0E and scale_bits != 0:
                raise ValueError(f"unexpected Float16 scale at {family} descriptor {index}")
            cursor += element_count * element_bytes
            layout.append((element_count, shape, storage))
            descriptors.append({
                "index": index,
                "data_address": f"0x{data_address:08x}",
                "element_count": element_count,
                "shape_raw": f"0x{shape:08x}",
                "storage_raw": f"0x{storage:08x}",
                "quantization_scale": scale if storage_code == 0x0E else None,
            })
        if cursor != data_end:
            raise ValueError(
                f"unexpected classifier data end for {family}: 0x{cursor:08x}"
            )
        if common_layout is None:
            common_layout = layout
        elif layout != common_layout:
            raise ValueError("classifier families do not share the same tensor layout")
        classifier_models[family] = {
            "descriptor_table_address": f"0x{table_address:08x}",
            "descriptor_count": CLASSIFIER_DESCRIPTOR_COUNT,
            "descriptor_bytes": CLASSIFIER_DESCRIPTOR_BYTES,
            "model_data_start": f"0x{data_start:08x}",
            "model_data_end_exclusive": f"0x{data_end:08x}",
            "model_data_bytes": data_end - data_start,
            "model_data_sha256": hashlib.sha256(
                flash_bytes(image, base, data_start, data_end)
            ).hexdigest(),
            "descriptors": descriptors,
        }

    diagnostics = {}
    for address, expected in EXPECTED_DIAGNOSTICS.items():
        actual = c_string(image, base, address)
        if actual != expected:
            raise ValueError(f"unexpected diagnostic at 0x{address:08x}: {actual!r}")
        diagnostics[f"0x{address:08x}"] = actual

    sleep_fields = [
        field for field in OUTPUT_FIELDS
        if field["io_offset"] in {0x60, 0x61, 0x62, 0x68, 0x6C, 0x70, 0x71, 0x72, 0x73}
    ]
    expected_sleep_fields = [
        (0x2F5, 0x60, 1), (0x2F6, 0x61, 1), (0x2F7, 0x62, 1),
        (0x2C4, 0x68, 4), (0x2C8, 0x6C, 4), (0x2DE, 0x70, 1),
        (0x2DF, 0x71, 1), (0x2E0, 0x72, 1), (0x2E1, 0x73, 1),
    ]
    if [(f["engine_offset"], f["io_offset"], f["width"]) for f in sleep_fields] \
            != expected_sleep_fields:
        raise ValueError(f"unexpected sleep output ABI: {sleep_fields}")

    first_party: dict[str, Any] | None = None
    if first_party_objects is not None:
        objects = first_party_objects.read_bytes()
        objects_digest = hashlib.sha256(objects).hexdigest()
        if objects_digest != EXPECTED_FIRST_PARTY_OBJECTS_SHA256:
            raise ValueError(f"unexpected first-party objects SHA-256: {objects_digest}")
        text = objects.decode("utf-8")
        sleep_types = enum_objects(text, "BleRing1SleepType")
        stage_types = enum_objects(text, "BleRing1SleepStageType")
        expected_sleep_types = {
            "long": {"ordinal": 0, "wire_value": 1},
            "short": {"ordinal": 1, "wire_value": 2},
        }
        expected_stage_types = {
            "awake": {"ordinal": 0, "wire_value": 0},
            "rem": {"ordinal": 1, "wire_value": 1},
            "light": {"ordinal": 2, "wire_value": 2},
            "deep": {"ordinal": 3, "wire_value": 3},
        }
        if sleep_types != expected_sleep_types:
            raise ValueError(f"unexpected first-party sleep types: {sleep_types}")
        if stage_types != expected_stage_types:
            raise ValueError(f"unexpected first-party sleep stages: {stage_types}")
        first_party = {
            "objects_path": str(first_party_objects),
            "objects_sha256": objects_digest,
            "sleep_types": sleep_types,
            "sleep_stage_types": stage_types,
        }

    return {
        "image": str(image_path),
        "image_sha256": digest,
        "load_base": f"0x{base:08x}",
        "first_party_cross_check": first_party,
        "copied_output_fields": sleep_fields,
        "stage_pipeline": {
            "stage_codes": {"awake": 0, "rem": 1, "light": 2, "deep": 3},
            "epoch_seconds": 30,
            "circular_epoch_count": 2880,
            "history_bytes": 720,
            "bits_per_epoch": 2,
            "history_index": "(unix_seconds / 30) % 2880",
            "emitted_stage_index": "((unix_seconds / 30) - 1 with UInt32 wrap) % 2880",
            "missing_epochs_receive_previous_stage": True,
            "history_reset_gap_seconds": reset_gap,
            "updated_byte_is_one_only_for_fresh_classifier_result": True,
            "inactive_period_forces_awake_and_ppg_off": True,
            "classifier_is_proprietary_network": True,
        },
        "ppg_request": {
            "mode_below_100": "continuous while sleep period is on",
            "other_modes": "counter modulo 6 is below 3",
            "mode_101": "counter modulo 9 is below 3",
            "mode_102": "counter modulo 12 is below 3",
            "counter_wall_clock_unit_proven": False,
        },
        "classifier_boundary": {
            "feature_coordinator_function": "0x00088aac",
            "feature_interpolator_function": "0x00074d60",
            "peak_retention_function": "0x00076502",
            "valid_interval_function": "0x00064b06",
            "classifier_function": "0x00088450",
            "score_offset_function": "0x0007d0a8",
            "argmax_function": "0x0004ece0",
            "motion_gate_aggregator_function": "0x0005f264",
            "motion_feature_function": "0x0005f3d8",
            "source_blocks": 32,
            "source_samples_per_block": 25,
            "peak_capacity": 136,
            "valid_peak_spacing_inclusive": [10, 37],
            "feature_batch_count": 30,
            "feature_window_count": 90,
            "default_bpm": 60.0,
            "normalization": "(bpm - 60) * 0.2",
            "feature_bin_start": 2,
            "feature_window_on_ppg": "replace final 30 values",
            "feature_window_without_ppg": "rotate [A,B,C] to [B,C,A]",
            "feature_window_after_inference": "copy [B,C] over first 60, retaining C",
            "retained_peaks": "sorted trailing positions > 749; subtract 750; preserve high bit",
            "next_source_block_index": 2,
            "fallback_output": {
                "scores": [-1.0, -1.0, -1.0, -1.0],
                "stage_raw": 255,
            },
            "optical_peak_source": {
                "raw_optical_input_lane": {
                    "internal_topic_name": "raw_hr",
                    "topic_record": "count UInt8, alignment bytes, up to 30 UInt32 words",
                    "topic_callback_function": "0x0006b228",
                    "callback_clamps_to_samples": 25,
                    "callback_conversion": "unsigned UInt32 to Float32",
                    "common_input_adapter_function": "0x00094590",
                    "raw_optical_adapter_function": "0x00060a14",
                    "resample_filter_function": "0x0008247e",
                    "common_filter_bank_initializer": "0x00071c38",
                    "common_engine_open_function": "0x0006fea0",
                    "io_offsets": {"pointer": 0x18, "count": 0x1C, "channel_count": 0x1D},
                    "engine_offsets": {"filtered_pointer": 0x170, "invalid": 0x174},
                    "channel_count_set_by_stock_adapter": 1,
                    "resampled_output_samples": 25,
                    "resampler": "linear interpolation at input_count / 25 positions",
                    "empty_input": "25 zeros, invalid flag one, filter histories unchanged",
                    "prefilter_order": 4,
                    "prefilter_normalized_cutoffs": [0.0104, 0.96],
                    "prefilter_numerator_bits": [
                        f"0x{item:08x}" for item in RAW_OPTICAL_PREFILTER_NUMERATOR_BITS
                    ],
                    "prefilter_denominator_bits": [
                        f"0x{item:08x}" for item in RAW_OPTICAL_PREFILTER_DENOMINATOR_BITS
                    ],
                    "prefilter_coefficient_validation": (
                        "bit-exact state captured after isolated Thumb execution of 0x71c38"
                    ),
                    "feeds_sleep_peak_detector": True,
                    "physical_word_meaning_or_wavelength_proven": False,
                    "live_topic_subscription_exposed": False,
                },
                "coordinator_function": "0x00060af4",
                "history_advance_function": "0x0008ee3a",
                "input_adapter_function": "0x00058ab8",
                "equal_length_resampler_function": "0x000882ec",
                "iir_filter_function": "0x000641f0",
                "iir_designer_function": "0x000711b4",
                "state_reset_function": "0x00071ca0",
                "filter_initializer_function": "0x00071d62",
                "valley_candidate_function": "0x00064a28",
                "peak_selection_function": "0x000649bc",
                "strict_maximum_function": "0x0004ec6c",
                "deduplication_function": "0x00088264",
                "record_encoder_function": "0x00059d70",
                "state_bytes": 0x18C,
                "filter_state_bytes": 0x50,
                "filtered_window_offset": 0x50,
                "filtered_window_samples": 75,
                "retained_window_samples": 50,
                "append_offset": 0x118,
                "source_block_samples": 25,
                "persisted_peak_offset": 0x17C,
                "persisted_peak_count_offset": 0x188,
                "peak_capacity": 12,
                "record_bytes": 17,
                "record_header": "byte 16 = 0x80 | count; positions begin at byte 0",
                "maximum_elapsed_blocks_without_full_reset": 2,
                "invalid_block_behavior": (
                    "zero the appended 25-Float slot without advancing IIR histories"
                ),
                "filter_order": 4,
                "normalized_cutoffs": [0.016, 0.16],
                "numerator_bits": [f"0x{item:08x}" for item in OPTICAL_FILTER_NUMERATOR_BITS],
                "denominator_bits": [
                    f"0x{item:08x}" for item in OPTICAL_FILTER_DENOMINATOR_BITS
                ],
                "numerator": [
                    struct.unpack("<f", struct.pack("<I", item))[0]
                    for item in OPTICAL_FILTER_NUMERATOR_BITS
                ],
                "denominator": [
                    struct.unpack("<f", struct.pack("<I", item))[0]
                    for item in OPTICAL_FILTER_DENOMINATOR_BITS
                ],
                "coefficient_validation": (
                    "bit-exact state captured after isolated Thumb execution of 0x71ca0"
                ),
                "candidate_rule": (
                    "current <= previous, current < next, positive second difference"
                ),
                "minimum_valley_spacing": "strictly greater than 7.5 samples (integer >= 8)",
                "peak_rule": (
                    "earliest strict maximum in each half-open adjacent-valley interval; "
                    "discard if selected value equals zero"
                ),
                "deduplication_rule": "drop new positions at or before prior last position",
                "offline_stateful_detector_implemented": True,
                "offline_raw_topic_to_peak_pipeline_implemented": True,
                "physical_input_channel_or_unit_proven": False,
                "starts_live_ppg": False,
            },
            "motion_gate_source": {
                "internal_topic_name": "acc",
                "topic_record": "30 packed signed Int16 XYZ triples followed by count UInt8",
                "topic_callback_function": "0x0006b114",
                "topic_capacity": 30,
                "callback_clamps_to_samples": 25,
                "callback_axis_mapping": ["-source_y", "source_x", "source_z"],
                "callback_float32_scale": 0.9765625,
                "common_input_adapter_function": "0x00060990",
                "resample_filter_function": "0x0008245c",
                "common_filter_bank_initializer": "0x00071c38",
                "empty_input": "three zero 25-Float axes, invalid flag one, histories unchanged",
                "resampled_output_samples_per_axis": 25,
                "prefilter_order": 2,
                "prefilter_normalized_cutoff": 0.96,
                "prefilter_numerator_bits": [
                    f"0x{item:08x}" for item in RAW_ACCELEROMETER_PREFILTER_NUMERATOR_BITS
                ],
                "prefilter_denominator_bits": [
                    f"0x{item:08x}" for item in RAW_ACCELEROMETER_PREFILTER_DENOMINATOR_BITS
                ],
                "feature": {
                    "function": "0x0005f3d8",
                    "state_initializer": "0x0007116c",
                    "state_reset": "0x00058464",
                    "state_bytes": 0x80,
                    "axis_input_history_floats": 5,
                    "axis_output_history_floats": 5,
                    "warmup_valid_calls": 5,
                    "reset_on_invalid_or_elapsed_above_seconds": 1,
                    "resample": "25 to 30 by linear interpolation",
                    "input_scale": 0.001,
                    "filter_function": "0x00074914",
                    "filter_order": 4,
                    "filter_numerator_bits": [
                        f"0x{item:08x}" for item in MOTION_FILTER_NUMERATOR_BITS
                    ],
                    "filter_denominator_bits": [
                        f"0x{item:08x}" for item in MOTION_FILTER_DENOMINATOR_BITS
                    ],
                    "downsample": "take indices 0,3,...,27 to ten values per axis",
                    "absolute_magnitude_clamp": 2.130000114440918,
                    "feature_scale": 60.975608825683594,
                    "primary_dead_band": 0.06800000369548798,
                    "primary_quantization": "truncate each scaled value toward zero before sum",
                    "secondary_dead_band": 0.013000000268220901,
                    "axis_combination": "sqrt(sum of squared per-axis sums)",
                },
                "aggregator": {
                    "function": "0x0005f264",
                    "state_reset": "0x00071154",
                    "weighted_score_function": "0x00067750",
                    "bucket_seconds": 30,
                    "bucket_count": 18,
                    "bucket_storage": "truncate average primary feature to UInt8 after 0...255 clamp",
                    "short_gap_behavior": "repeat last bucket through crossed boundaries",
                    "reset_gap_seconds_inclusive": 540,
                    "weight_bits_oldest_to_newest_rotation": [
                        f"0x{item:08x}" for item in MOTION_GATE_WEIGHT_BITS
                    ],
                    "ready_only_on_crossed_30_second_boundary": True,
                    "firmware_baseline_predicate": "score + 1.496979475 > 0",
                },
                "production_thumb_fixture_seconds": 51,
                "production_thumb_fixture_boundary_score_bits": [
                    "0xc18cfcc0", "0xc1d5b8cf",
                ],
                "offline_full_motion_gate_pipeline_implemented": True,
                "physical_ring_orientation_proven": False,
                "live_topic_subscription_exposed": False,
                "starts_live_accelerometer": False,
            },
            "models": classifier_models,
            "architecture": {
                "input": [1, 90],
                "convolution_output_channels": [4, 8, 8, 8, 8, 8, 8],
                "convolution_kernel_width": 3,
                "convolution_padding": 1,
                "convolution_stride": 1,
                "batch_normalization_after_each_convolution": True,
                "leaky_relu_half_bits": "0x31d1",
                "leaky_relu_slope": 0.1817626953125,
                "average_pool_kernels_and_strides": [2, 3],
                "flattened_width": 120,
                "dense_widths_before_gru": [32, 32],
                "stateful_gru_layers": 2,
                "gru_hidden_width": 32,
                "dense_width_after_gru": 32,
                "output_width": 4,
                "quantized_matrices": "signed int8 with per-tensor Float32 scale",
                "other_parameters": "Float16",
                "firmware_half_decoder_function": "0x00070758",
                "batch_normalization_epsilon_half_bits": "0x00a8",
                "batch_normalization_epsilon": 0.00003552436828613281,
                "softmax": True,
            },
            "gru_gate_order": ["reset", "update", "candidate"],
            "gru_candidate": "tanh(input + reset * recurrent)",
            "gru_state_update": "update * previous + (1 - update) * candidate",
            "recurrent_state_slots": 2,
            "recurrent_state_width_each": 32,
            "engine_open_function": "0x00090f44",
            "engine_close_function": "0x0005d360",
            "workspace_bytes_zeroed_on_open": 0x1B90,
            "recurrent_state_pointer_offsets": [0x554, 0x558],
            "recurrent_state_resets_on_every_engine_open": True,
            "engine_close_only_clears_active_flag": True,
            "profile_score_offset_scale": 0.01,
            "argmax_ties_select_earliest_class": True,
            "class_order": ["awake", "REM", "light", "deep"],
            "active_period_replaces_awake_with_best_non_awake": True,
            "motion_gate_threshold_scale": 1.496979475,
            "motion_gate_uses_accelerometer_derived_score": True,
            "motion_gate_score_physical_unit_proven": False,
            "embedded_parameters_fully_present": True,
            "offline_full_network_runner_implemented": True,
            "offline_runner_requires_caller_supplied_firmware_or_exact_slices": True,
            "offline_runner_starts_live_sensors": False,
            "offline_runner_compared_with_live_firmware_outputs": False,
        },
        "lifecycle_flags": {
            "0x01": "transition target period state is on; stock host does not branch on it",
            "0x02": "Sleep Period On and public status bridge(1)",
            "0x04": "Sleep Period Off and public status bridge(0)",
            "0x08": "nested final-result build/store/publish",
            "0x10": "final public type 1 long rather than type 2 short",
        },
        "transition": {
            "event_codes": {"none": 0, "period_end": 1, "ordinary_start": 2,
                            "reason_5_special_start": 4},
            "reason_code_range_constructed": [0, 8],
            "reason_5_selects_special_start": True,
            "human_reason_labels_found": False,
        },
        "interval_classification": {
            "0": "accepted at effective long threshold; adds flags 0x18",
            "1": "rejected when counter is at least 100",
            "2": "rejected when duration is at least 900 minutes and ratio exceeds 0.21",
            "3": "accepted short interval inside configured hours; adds flag 0x08",
            "4": "rejected below configured minimum or outside the short-window hours",
            "inside_window_long_threshold_minutes": 180,
            "outside_window_long_threshold_minutes": 20,
        },
        "interval_reconciliation": {
            "0": "no action or merge using previous start",
            "1": "accepted pair combined span is at least 43201 seconds",
            "2": "previous interval is not accepted",
            "3": "gap exceeds configured separation minutes",
            "5": "dense evidence and gap is at least 1801 seconds",
            "merge_adds_long_flag_when_combined_span_exceeds_seconds": 10799,
            "minimum_dense_evidence_count": 1800,
            "dense_evidence_ratio_threshold": 0.32,
            "code_4_producer_found": False,
        },
        "stage_statistics": {
            "functions": ["0x00068f8c", "0x00068fd4", "0x00069128"],
            "maximum_epoch_denominator": 2880,
            "epoch_minutes": 0.5,
            "first_block": [
                "interval minutes", "leading awake minutes", "non-awake sleep minutes",
                "middle awake minutes", "awake after sleep onset minutes",
                "non-awake plus middle-awake minutes", "sleep efficiency fraction",
            ],
            "second_block": [
                "NREM fraction", "REM fraction", "light fraction", "deep fraction",
                "REM/NREM", "deep/light", "deep/REM", "deep/NREM", "wake minutes",
                "REM minutes", "light minutes", "deep minutes",
            ],
            "all_awake_or_invalid_first_block_sentinel": -1.0,
            "zero_ratio_denominator_result": 0.0,
            "unknown_nonzero_stage_counts_as_sleep_only_in_first_block": True,
        },
        "stage_postprocessor": {
            "profile_lookup_function": "0x000684b4",
            "function": "0x00081040",
            "run_collector_function": "0x00069546",
            "edge_repair_function": "0x0008f0f0",
            "deep_awake_repair_function": "0x000881f4",
            "proportion_adjustment_function": "0x00064cc8",
            "profiles": postprocessor_profiles,
            "ordered_phases": [
                "centered moving-majority vote with awake selected at three votes",
                "awake-run bidirectional edge fill except the leading run",
                "light relabeling at both edges of REM runs at least 41 epochs",
                "deep/awake boundary repair of at most six epochs",
                "up to ten REM/deep proportion-correction passes",
                "fixed-width chunk-majority vote",
                "reverse deep-to-light conversion while the working ratio is at least 0.35",
                "forward REM-to-light conversion while the working ratio is at least 0.25",
                "optional last-epoch awake flag (clear in all seven official profiles)",
            ],
            "moving_vote_tie_priority": ["deep", "light", "REM", "awake"],
            "awake_vote_threshold": 3,
            "maximum_recorded_runs_per_helper": 40,
            "target_fractions": {"REM": 0.225, "deep": 0.18},
            "target_moves_halfway_from_current_fraction": True,
            "proportion_deadband_epochs_inclusive": [-6, 6],
            "maximum_proportion_passes": 10,
            "repeat_when": "REM <= 0.1 or REM >= 0.25 or deep <= 0.1 among sleep",
            "stock_one_past_end_deep_cap_read": True,
            "stock_awake_to_deep_prefix_write_can_precede_logical_array": True,
            "stock_short_run_negative_deficit_moves_away_from_zero": True,
            "stock_preceding_expansion_guard_includes_target_and_is_unreachable": True,
            "offline_model_clips_writes_to_caller_supplied_array": True,
        },
        "score": {
            "function": "0x0006778c",
            "duration_shape": "baseline - factor * tanh(abs(sleep_minutes / 60 - target_hours))",
            "duration_bands": [
                {"minutes": "<270", "baseline": 59, "target_hours": 4.5, "factor": 15},
                {"minutes": "270..<300", "baseline": 74, "target_hours": 5, "factor": 15},
                {"minutes": "300..<360", "baseline": 89, "target_hours": 6, "factor": 15},
                {"minutes": "360..<480", "baseline": 95, "target_hours": 7, "factor": 6},
                {"minutes": "480..<510", "baseline": 89, "target_hours": 8, "factor": 15},
                {"minutes": "510..<540", "baseline": 74, "target_hours": 8.5, "factor": 15},
                {"minutes": ">540", "baseline": 59, "target_hours": 9, "factor": 15},
            ],
            "exact_540_minute_parameters": {"baseline": 0, "target_hours": 0, "factor": 0},
            "exact_540_minute_branch_hole_present": True,
            "wake_ratio": "awake-after-sleep-onset minutes / non-awake sleep minutes",
            "wake_divisor_below_40_percent": "powf(1.1, wake_ratio + 0.11)",
            "wake_divisor_at_least_40_percent": "powf(1.1, wake_ratio + 3.26)",
            "rem_additive_weights": {
                "outside_0.10_through_0.40": 0.1,
                "0.10_to_0.15_or_0.35_to_0.40": 0.2,
                "0.15_to_0.20_or_0.30_to_0.35": 0.4,
                "0.20_through_0.30": 0.3,
            },
            "deep_additive_weights": {
                "below_0.05": 0.1,
                "0.05_to_0.10": 0.2,
                "0.15_through_0.25": 0.4,
                "other": 0.3,
            },
            "final_clamp": [0, 100],
            "public_conversion": "Float32 to unsigned integer toward zero, then low byte",
        },
        "final_interval_validator": {
            "function": "0x00072af0",
            "requires_interval_flag": "0x08",
            "minimum_duration_seconds": 900,
            "maximum_duration_seconds": 86400,
            "requires_current_at_or_after_end": True,
            "requires_current_strictly_before_start_plus_seconds": 86400,
        },
        "leading_awake_extension": {
            "function": "0x000748d4",
            "selected_minutes": "truncate_to_half_minute(clamp(leading_awake_minutes * 0.5, 0.5, 10))",
            "prepended_stage": "awake",
            "relabels_early_non_awake_to_light_until_first_light": True,
            "maximum_relabels": 21,
        },
        "sleep_temperature": {
            "history_runtime_address": "0x2001e3ea",
            "history_bytes": 106,
            "layout": {"active": 0, "prior_temperature_mode": 1, "count": 2,
                       "samples": 4, "cached_reduction": 104},
            "history_capacity": 50,
            "sleep_start_clears_history": True,
            "sleep_owned_temperature_mode": 1,
            "timing_period_argument_raw": 600,
            "batch_input_to_history_scale_float64": 0.1,
            "minimum_result_samples": 12,
            "sorts_ascending": True,
            "trims_each_side": "floor(count / 10)",
            "trimmed_mean_uses_integer_division": True,
            "median_even_uses_integer_average": True,
            "maximum_inclusive_mean_median_delta_raw": 100,
            "accepted_history_to_public_scale_float64": 0.1,
            "first_party_upload_key": "body_temp",
            "physical_celsius_scale_proven_end_to_end": False,
        },
        "public_result": {
            "long_wire_value": 1,
            "short_wire_value": 2,
            "efficiency_byte": "sleep efficiency fraction * 100, converted toward zero",
            "score_byte": "clamped score converted toward zero",
            "reserved_byte_3": 0,
            "ratio_bytes_4_through_7": ["wake", "REM", "light", "deep"],
            "body_temperature_bytes": [8, 9],
            "utc_offset_minutes_bytes": [10, 11],
            "total_time_is_non_awake_sleep_minutes": True,
            "duration_fields_minutes": ["total(non-awake)", "wake", "REM", "light", "deep"],
            "stage_compaction": "low 2 bits stage; high 6 bits run length, maximum 63",
            "first_party_uploaded_keys": [
                "efficiency", "score", "body_temp", "start_ts", "end_ts", "total_time",
                "wake_time", "rem_time", "light_time", "deep_time", "stages",
            ],
            "first_party_drops_ratio_bytes_and_utc_offset_from_upload_map": True,
            "first_party_wire_cross_check_required_for_label_claim": True,
        },
        "constants": constants,
        "diagnostics": diagnostics,
        "verified_ranges": verified_ranges,
        "direct_branches": branches,
        "safety": {
            "static_read_only": True,
            "health_consent_required_for_captured_values": True,
            "live_sram_reader_exposed": False,
            "live_ppg_control_exposed": False,
            "live_temperature_mode_control_exposed": False,
            "vendor_classifier_execution_exposed": False,
            "bounded_host_classifier_execution_available": True,
            "bounded_host_optical_peak_detection_available": True,
            "bounded_host_raw_optical_to_peak_pipeline_available": True,
            "bounded_host_raw_accelerometer_to_motion_gate_pipeline_available": True,
            "clinical_claims_permitted": False,
            "raw_unknown_codes_should_be_preserved": True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--base", type=lambda value: int(value, 0), default=DEFAULT_BASE)
    parser.add_argument(
        "--first-party-objects",
        type=Path,
        help="optional blutter objs.txt from the first-party controller app",
    )
    args = parser.parse_args()
    print(json.dumps(
        summarize(args.image, args.base, args.first_party_objects),
        indent=2,
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()
