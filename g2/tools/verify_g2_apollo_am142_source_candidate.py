#!/usr/bin/env python3
"""Verify source-owned AM142 helpers routed out of the retained transcript."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import apollo_overlay

RAW_SOURCE = (
    ROOT /
    "components/apollo_main/core_overlay/runtime_liblc3_am142_helpers.c"
)
RAW_SOURCE_SHA256 = (
    "e39ba9e6f865a35db1761c5c17c0ede5469a70eedaf6d971709c8795fb24f085"
)
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
OUT = ROOT / "tools/manifests/g2-apollo-am142-source-candidate.json"

CLANG = "/usr/bin/clang"
TARGET = "thumbv7em-none-eabi"
FLAGS = [
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
    "-Wall",
    "-Wextra",
    "-Werror",
    "-ffunction-sections",
    "-fdata-sections",
]

HELPERS = [
    {
        "function": "open_cfw_runtime_am142_0x0059aa84",
        "runtime_address": 0x0059AA84,
        "source": (
            "components/apollo_main/core_overlay/"
            "runtime_liblc3_am142_0x59aa84.c"),
        "size": 2610,
        "sha256": (
            "6c28993d7ef3b66e3acc96f6ae3de5cb6c9c489526d874fb1330aa57d4788e7a"),
        "bytes": (
            '029181690191c06905900499a218100051f740fe8346584651f743fd0090300051f73ffd0100'
            '009809182e2902db0198000403e03100584651f72cfeb0eb074f07da31005fea0848404651f7'
            '51fe28605fe0b0eb094f1edab9eb070000900398b0eb0800069031003f04380051f740febbeb'
            '00000099002910d0009a069951f790fd070031005fea0848404651f730fec7192f603de0b0eb'
            '0a4f1ddabaeb0907ddf808800398b8eb000831005fea0949484651f71dfebbeb0000002f10d0'
            '3a00414651f76efd070031000398000451f70ffec7192f601ce00199b0eb014f12da019fb7eb'
            '0a07ddf814800298b8eb000831005fea0a4a504651f7fafdbbeb000b5846002f14d131000598'
            '000451f7f0fd286004994900286851f7eafd28602968022094fbf0f04118296007b0bde8f08f'
            '3a00414651f735fd070031000298000451f7d6fdc7192f60e3e72de9f04f85b004000d00d4f8'
            'b06000270020d4f88880d4f88c90002004900020039000206060300000f02ffb8246d4f8b400'
            '504502d0c4f8b4a00127207a002839d1d4f824b2300000f022fb0068002801d0012000e00020'
            'c0b200282bd003aa04a9300000f01efb60606068002840f0f380039b049adaf824121af50b70'
            'dbf80cc0e047002808d0039b049a5146d6f81402dbf80470b8470127daf830022066002084f8'
            '5d00daf82402a0670498e0670398c4f88000300000f0fffaa16d814201d0a0650127207b10f0'
            '010084f8b800102214f110012800a2f69ffa002819d014f110002900182266f6b5ff00206062'
            '606a206214f128002900182266f6abff5ff48030e064e06c20640020a064a06c6064012794f8'
            'ba00217b11f00201884205d0207b10f0020084f8ba000127ffb2002f00f09180d4f88450002d'
            '01d14ff47a75a06db0f5802f02da5ff4802700e0a76d5ff07a7090fbf5fa300000f0b2fac4f8'
            'dc00d4f8dc00012806da51465ff4960051f718fdc4f8dc00b8f1010f1bdb3900280451f70ffd'
            '404501da404604e039002d04280051f706fd14f1bc01029100210191009014f1e403d4f8dc20'
            '39005046fff75afe0fe014f1bc00029094f8ba0001900020009014f1e403d4f8dc2039005046'
            'fff749fe300000f079fa01280cdb4000d4f8dc10884207da51465ff4960051f7d8fcc4f8e000'
            '06e051465ff4dc0051f7d0fcc4f8e00014f1bc00029094f8ba000190cdf8009014f1e803d4f8'
            'e02039005046fff720fed4f8e400002803d1d4f8e800002803d0012084f8b90002e0002084f8'
            'b900002084f8ec00210014f1f000fff709fb05b0bde8f08f2de9f84187b004000d001e000027'
            '00200490106905905069069011002000fff7c0fe606800282fd1002084f8ec0094f8b9800de0'
            '5ffa88f8b8f1000f1fd0d4f8a00000281cd5012084f8ec005ff0000814f1900000f054fb04a8'
            '039000200290002001900020009005ab14f190022900200002f027f860680028dbd004e0ffe7'
            '14f1900000f044fb049830603900201dfff7b5fd606808b0bde8f08110b504002068012802db'
            'e068012801da242012e0b1f5004f01dba4200de009045ff0fa6051f742fc2168884202dbe168'
            '884201daa42000e0002010bdc26992f83000002806d111f50041090c09b2d2f8200201607047'
            '38b50400002c0cd02568e16e280056f7a3f90020e066616f280056f79df90020606731bd10b5'
            'c4692000fef72dfd002084f82c0010bd70b504000d002000c66996f82c0000280dd16a682968'
            '3000fef704fd002806d0a1690968002901d1a16908600de0ea68a9683000fef7aefc002806d0'
            'a1690968002901d1a1690860ffe770bd70b504000d002000c66996f82c0000280dd16a682968'
            '3000fef7defc002806d0a1690968002901d1a16908601ee003213000fef754fc002806d0a169'
            '0968002901d1a169086011e00023ea68a9683000fef75bfc00236a6929693000fef755fc0123'
            'ea69a9693000fef74ffc70bdf8b504000d001600202100222700380069f671f86561a6618848'
            '2060884860608848e060f1bd000088ff30b4029c856895f8a0501d70856895f8a15025701b78'
            '002b10d08368d3f8a4302033402493fbf4f30b608068d0f8a8002030402190fbf1f0106003e0'
            '4ff480600860106030bc70474068b0f8440070472de9f04f8fb005000f0090460020029095f8'
            '30603000c0b2002805d0d5f81802002801d10820c8e0d5f80090d5f81c020468d5f81c020068'
            '002824d16348d5f81c12486002aa4ff40a71484656f748f8d5f81c120860029800284ed1d5f8'
            '1c020468c4f800903000c0b2002805d1d5f81402d0f8100cc4f82402221d216814f19000fff7'
            '80ffcdf810800097c4f8b050c4f8ac50aa46daf80400076e97f82080daf80400d0f8800090f9'
            '38900020102100220df1140b584668f6e0ff0098089008980690009804990844079018210022'
            '0df1240b584668f6d1ff01a800900df105030caa09a92800fff762ff3000c0b2002804d00020'
            '607206e040205de0daf8040090f8b802607226720020e0609df80500002803d0e06850f00100'
            'e0609df80400002811d0484640b2002809d04ffa89f9b9f1000f08d55ffa88f8b8f1000f03d1'
            'e06850f00200e060786ac4f8bc00b86ac4f8c000f86ac4f8c400386bc4f8c800786bc4f8cc00'
            'b86bc4f8d000f86bc4f8d400386cc4f8d8002800fff73cffc4f884009df80400002806d0d4f8'
            '841009a8fff755fe00280fd103ab09aa05a92000fff7fffd002801d0032005e0039914f19000'
            'fff762fe00200fb0bde8f08f232f5d00352f5d00812f5d00ff2e5d00d0f818027047d0f81402'
            '00f628407047d0f81402d0f8140670471cb513004068d0f82442002200920022246aa04716bd'
            '4068806dc08900047047d0f81802d0f8900100047047d0f81802d0f88c0100047047f8b50500'
            '0e0017001c005ff07a71d5f81802d0f8800151f758fa3060d5f81802d0f8840100043860d5f8'
            '1802d0f8880100042060f1bdd0f8183293f8bc300b60d0f81802c03010607047d0f8183293f8'
            'bd300b60d0f81802f83010607047d0f8183293f8be300b60d0f8180210f5907010607047d0f8'
            '183293f8bf300b60d0f8180210f5ac7010607047d0f81802d0f80c027047f8b504000e001500'
            '102100222f00380068f6d9fed4f838028619d4f83002864201d301200de0d4f8400250f82600'
            'e860e8686860d4f8400200eb86004068a8600020f2bdfeb505000e0014001021002227003800'
            '68f6b7fe6868d0f88000406b002809d001ab6a4631006868d5f85052a84700280ad012e03100'
            'd5f81402fef7fbfe0600002eedd5122008e000986060009801990844a0606068e0600020febd'
            '80b503008a684868121a091d5868d3f85432984701bd2de9fc4115000024426812f18400d2f8'
            '8020536b002b06d06a4658681b681b689847040009e0d0f8282152f821200092d0f82c0150f8'
            '21000190002c0dd1009e019f10210022a846404668f661feee60e868686006eb0700a8602000'
            'bde8f681e0b54268486800908b6848681b1a0193d2f88000406b00280ad06946d2f88000406b'
            '4068d2f88020526b12685268904707bdf8b505000e001400102100222700380068f635fed5f8'
            '34028619d5f82c02864201d3012032e0d5f83c0250f826006060'),
    },
    {
        "function": "open_cfw_runtime_am142_0x0059b4b8",
        "runtime_address": 0x0059B4B8,
        "source": (
            "components/apollo_main/core_overlay/"
            "runtime_liblc3_am142_0x59b4b8.c"),
        "size": 258,
        "sha256": (
            "3d5ca82a9e4d55722d6bf93aaf72c2e79f606b4066aeca75ded6856a8aa9fe35"),
        "bytes": (
            "3000002820d0d5f86002002807d06068d5f8601251f826100844a06010e0d5f8"
            "5c02002802d4d5f85c0200e00020616808446060d5f83c0200eb86004068a060"
            "6068002806d105e0d5f83c0200eb86004068a0606068e0600020f2bdd0f81802"
            "d0f81c0200047047d0f81802d0f820020004704780b5c16900220261c86851f7"
            "47fb01bd10b5c4692000fef730fae06851f7a7fc10bd10b404005b1a14fb33f0"
            "141b11fb34f1401a10bc70472de9f84305000f00160098460a9c14210022a946"
            "484668f6c3fd31003800fef72aff0700b9687868091a11f5a81f0ad1e4b2002c"
            "04d0b868a860012028602be00020286028e011f5a01f0ad1e4b2002c02d00020"
            "2860"),
    },
    {
        "function": "open_cfw_runtime_am142_0x0059b6a0",
        "runtime_address": 0x0059B6A0,
        "source": (
            "components/apollo_main/core_overlay/"
            "runtime_liblc3_am142_0x59b6a0.c"),
        "size": 4,
        "sha256": (
            "dd0175750064b59435d9763a100d21415aa1e2b8e5dca9a2ebc58f37ab3c9ed5"),
        "bytes": "c0b27047",
    },
    {
        "function": "open_cfw_runtime_am142_0x0059b6ac",
        "runtime_address": 0x0059B6AC,
        "source": (
            "components/apollo_main/core_overlay/"
            "runtime_liblc3_am142_0x59b6ac.c"),
        "size": 36,
        "sha256": (
            "c36b486eb54b818ee988fed935e3d68f513ca5b35ddc513b9bab5b52e5474b00"),
        "bytes": (
            "012000e00020c0b270470068000910f00100c0b270470068400910f00100"
            "c0b270470168"),
    },
    {
        "function": "open_cfw_runtime_am142_0x0059c866",
        "runtime_address": 0x0059C866,
        "source": (
            "components/apollo_main/core_overlay/"
            "runtime_liblc3_am142_0x59c866.c"),
        "size": 16,
        "sha256": (
            "2048d977f64e6c5282c4200259d7ff087f920796149a37e0ec6f405ce712f67a"),
        "bytes": "41180891049810eb0a00059003984019",
    },
    {
        "function": "open_cfw_runtime_am142_0x0059c876",
        "runtime_address": 0x0059C876,
        "source": (
            "components/apollo_main/core_overlay/"
            "runtime_liblc3_am142_0x59c876.c"),
        "size": 266,
        "sha256": (
            "7870453c77680d83a392c1b5078a094c187ecbeb18304b919368cace73916bc0"),
        "bytes": (
            "069042f6935914f80900002813d0dde907010a0001002000fff74ffe002004f8"
            "0900012042f690516054dde9050114f53752c2e9000142f6e05914f809000028"
            "0bd000200190dde905010091030007aa14f108012000fff737fd012004f80900"
            "022042f6e4516050dde9070142f6e8522244c2e90001dde9050142f6f0522244"
            "c2e90001f6b2002e11d00020019042f6a0502058009054f80b3042f698502258"
            "42f69450215814f10800fff783f944f807a044f8085009b0bde8f08f2de9f34f"
            "8fb0040091469a46ddf868b01b9d1c9e42f6c85742f6cc5805a8029006a80190"
            "cdf80090109b54f80820e1592000fff71dfe03a8029004a8019000962b005a46"
            "51462000fff712fe5b46"),
    },
    {
        "function": "open_cfw_runtime_am142_0x0059c800",
        "runtime_address": 0x0059C800,
        "source": (
            "components/apollo_main/core_overlay/"
            "runtime_liblc3_am142_0x59c800.c"),
        "size": 28,
        "sha256": (
            "a777c40748a4b317ff3be1a8caea6c5dcd13cca2b0ad1b9f34a5fe4da643debd"),
        "bytes": (
            "42f69c5b54f80b0000f096f9002806d042f69150205c002801d10126"),
    },
    {
        "function": "open_cfw_runtime_am142_0x0059c820",
        "runtime_address": 0x0059C820,
        "source": (
            "components/apollo_main/core_overlay/"
            "runtime_liblc3_am142_0x59c820.c"),
        "size": 30,
        "sha256": (
            "e268db317f93633da2da90f121fa1fd77d5bcf153b5c3921d4a320acc805bf37"),
        "bytes": (
            "42f6c857e059504508d142f6cc502058a84203d13000c0b2002877d042f6"),
    },
    {
        "function": "open_cfw_runtime_am142_0x0059c83e",
        "runtime_address": 0x0059C83E,
        "source": (
            "components/apollo_main/core_overlay/"
            "runtime_liblc3_am142_0x59c83e.c"),
        "size": 40,
        "sha256": (
            "1dfaa617fc5ad26783d4be6be3ef44d59ea0d0fa978af407d2fe3511af63e708"),
        "bytes": (
            "cc5803a8029004a801900095534654f80820e1592000fff7a5fee159049841180"
            "79154f808100398"),
    },
    {
        "function": "open_cfw_runtime_am142_0x0059cafc",
        "runtime_address": 0x0059CAFC,
        "source": (
            "components/apollo_main/core_overlay/"
            "runtime_liblc3_am142_0x59cafc.c"),
        "size": 70,
        "sha256": (
            "4e96c3fd1b208daaf4827b0f49df8c26894d49ab487dfe1dd4b74e7ef5d922ac"),
        "bytes": (
            "000214f108012000fff71bfc012042f693516054002060550020a0550020e055"
            "f7bd70b504000d001c2100222600300067f6eafa256070bd0079704740797047"
            "417170471030"),
    },
    {
        "function": "open_cfw_runtime_am142_0x0059cb42",
        "runtime_address": 0x0059CB42,
        "source": (
            "components/apollo_main/core_overlay/"
            "runtime_liblc3_am142_0x59cb42.c"),
        "size": 254,
        "sha256": (
            "8a3388a45a1a6a10dfb0a33843682d97f869e7fb5f54f3f50503126e5f5c0fd1"),
        "bytes": (
            "704780b5612905d312210068fdf76cff002009e081608268d21dd208c260012202"
            "7101224271080002bd70b504000d0011002000fff7e5ff00280bd0002606e0280"
            "002f018f904eb06010874761ce0688642f5d370bd38b5040001250800404210f0"
            "070085406d1e2000fff7caff002811d0002004e0ff2104eb00021174401ce168"
            "8842f7d3e0682044c07b30ea0505e0682044c57331bd2de9f84f86b004000d"
            "0016009b46109fddf844a0280002f038f9804618f00109207a002807d0d4f8"
            "b000d0f8d401002801d138780028207a002813d14846c0b200280fd038780028"
            "0cd10021280002f096f90090d4f8b000fef775fc00994018cbf80000d4f8"),
    },
    {
        "function": "open_cfw_runtime_am142_0x0059b6d0",
        "runtime_address": 0x0059B6D0,
        "source": (
            "components/apollo_main/core_overlay/"
            "runtime_liblc3_am142_0x59b6d0.c"),
        "size": 66,
        "sha256": (
            "c3a4e2bc8eda535845902f78064ccd08d9d078ce56e9f35b3716ca5aa68c3980"),
        "bytes": (
            "51f01001016070472de9f84304000d0016001f00ddf8208040f61c710022a1"
            "46484668f607fd95f8b8006073c4f8108025606660a760bde8f183007b7047"
            "704770b5"),
    },
    {
        "function": "open_cfw_runtime_am142_0x0059c7ac",
        "runtime_address": 0x0059C7AC,
        "source": (
            "components/apollo_main/core_overlay/"
            "runtime_liblc3_am142_0x59c7ac.c"),
        "size": 84,
        "sha256": (
            "06c4107ad68d47490ca50146dc5f8633a5ac1870ea4698e43b662c45e52d6578"),
        "bytes": (
            "06d042f69c50205800f0c0f9002812d00020019042f6a0502058009042f69c"
            "50235842f69850225842f69450215814f10800fff724fa04f6247014f1080140"
            "f61c7265f619fa73bd2de9f04f89b004008a461500"),
    },
    {
        "function": "open_cfw_runtime_am142_0x0059c1c4",
        "runtime_address": 0x0059C1C4,
        "source": (
            "components/apollo_main/core_overlay/"
            "runtime_liblc3_am142_0x59c1c4.c"),
        "size": 62,
        "sha256": (
            "b33e965e05a4e7092d68b930c302b70c81f5f6a0baee6eee64a47d0f11cdca81"),
        "bytes": (
            "daf80000091a03e0daf800103068091a42f6b4502858814202da3068caf800"
            "0070687968884216d1daf804107068091a002904d57168daf80400091a03e0"),
    },
    {
        "function": "open_cfw_runtime_am142_0x0059c204",
        "runtime_address": 0x0059C204,
        "source": (
            "components/apollo_main/core_overlay/"
            "runtime_liblc3_am142_0x59c204.c"),
        "size": 1416,
        "sha256": (
            "816457866cfa8970665d2971efec07b4aa18cd696c60166c56f7d462f64fbfa2"),
        "bytes": (
            "04107068091a42f6b4502858814202da7068caf80400d8f80000d9f800108842"
            "1ad1daf80010d8f80000091a002905d5d8f80010daf80000091a04e0daf80010"
            "d8f80000091a42f6b4502858814203dad8f80000caf80000d8f80400d9f80410"
            "88421ad1daf80410d8f80400091a002905d5d8f80410daf80400091a04e0daf8"
            "0410d8f80400091a42f6b4502858814203dad8f80400caf80400daf800103a68"
            "d8f800008218022092fbf0f0091a00290ad53968d8f800004118022091fbf0f2"
            "daf80000121a09e0daf800203968d8f800004118022091fbf0f0121a42f6b051"
            "6858904223dbdaf804207b68d8f80400c318022093fbf0f0121a002a0ad57a68"
            "d8f804008218022092fbf0f2daf80400121a09e0daf804207b68d8f80400c318"
            "022093fbf0f0121a6858904201da002000e0012007b0bde8f08f08b42de9f047"
            "8db00500894616000821002202ac200067f6d6fe002742f6e45a55f80a000228"
            "08d142f6e85005eb000142f6f05005eb000405e042f6f85005eb000115f53854"
            "20683268904203d160687268904211d002a8019015a80090330022002800fff7"
            "9dfe07003800c0b2002803d0dde90201c4e9000142f6d05805eb0802d2e90001"
            "cde90401179c55f80a00022802d0042834d064e002200c902000c0b200280dd0"
            "42f6f4502858009042f6f0502b5806aa05f624712800fff731fe0be042f6f450"
            "2858009042f6f0502b5806aa49462800fff724fe04980699884203d105980799"
            "88420ad004a968686a6852689047dde9060105eb0802c2e9000130e004200c90"
            "42f6f4502858009042f6f0502b5806aa49462800fff702fe42f6fc5028580090"
            "42f6f8502b5808aa49462800fff7f6fd42f604602858009015f5385003680aaa"
            "49462800fff7eafd04a968686a68d2689047dde90a0105eb0802c2e900013800"
            "c0b2002803d02000c0b2002832d0e4b2002c09d070680090336806aa05f62471"
            "2800fff7cbfd07e070680090336806aa49462800fff7c2fd069855f808108842"
            "05d1079842f6d4516958884212d002200c9005eb0802d2e90001cde9040104a9"
            "68686a6852689047dde9060105eb0802c2e90001ffb2002f03d0dde90201c6e9"
            "00010db0bde8f0075df808fbf8b58ab006000c0015000120099042f6d05706eb"
            "0700d0e90023cde9012316f10800fff7daf8002808d142f6dc50325842f6d850"
            "3158300000f004f928000090230003aa16f108013000fff771fd01a970687268"
            "12689047dde9030106eb0702c2e9000142f6b8503044c0e900450bb0f0bd2de9"
            "f84305000c0011001a00089b161b5f1a286890f8ec00002801d076427f42ddf8"
            "2880ddf824900020c8f80000d8f80000c9f8000042f69250285c002800f0c180"
            "2000fef7b2ff69680969401869680861002e58d4002f2ad47800b04206da0020"
            "c9f800000020c8f80000aae07600be420ada42f6a8502858c9f8000042f6ac50"
            "2858c8f800009ce042f6a85029584bf2333050f76ff8c9f8000042f6ac502958"
            "44f6cd4050f766f8c8f8000089e078004042b04206da0020c9f800000020c8f8"
            "00007ee07600fe420bda42f6a85028584042c9f8000042f6ac502858c8f80000"
            "6fe042f6a8502958374850f743f8c9f8000042f6ac50295844f6cd4050f73af8"
            "c8f800005de0002f2dd47800f04209da0020c9f8000042f6ac5028584000c8f8"
            "00004ee076007642be420ada42f6a8502858c9f8000042f6ac502858c8f80000"
            "3fe042f6a85029584bf2333050f712f8c9f8000042f6ac5029581c4850f70af8"
            "c8f800002de078004042f04209da0020c9f8000042f6ac5028584000c8f80000"
            "1fe076007642fe420bda42f6a85028584042c9f8000042f6ac502858c8f80000"
            "0fe042f6a850295807484ff7e3ffc9f8000042f6ac50295804484ff7dbffc8f8"
            "0000bde8f1830000ce4cffff33b301007cb504000d001600200000f099f942f6"
            "d850255042f6c850"),
    },
    {
        "function": "open_cfw_runtime_am142_0x0059b80c",
        "runtime_address": 0x0059B80C,
        "source": (
            "components/apollo_main/core_overlay/"
            "runtime_liblc3_am142_0x59b80c.c"),
        "size": 70,
        "sha256": (
            "5fa12a37b989fe9316500ae319014486992bfc89730aee7855ec056b9a015b0d"),
        "bytes": (
            "08fb07f03044c0f828a0002c21d008fb04f03044406a08fb04f1314409698842"
            "17d008fb04f03044416a08fb04f030440069091a08fb04f03044806a08fb04f2"
            "32445269801a"),
    },
    {
        "function": "open_cfw_runtime_am142_0x0059b852",
        "runtime_address": 0x0059B852,
        "source": (
            "components/apollo_main/core_overlay/"
            "runtime_liblc3_am142_0x59b852.c"),
        "size": 580,
        "sha256": (
            "5c32fab6b5ed0573afc81373fb72a005fb0e946ed333eadd2dea9b8c042bbc4c"),
        "bytes": (
            "50f78fff08fb04f1314488615ffa89f9b9f1000f23d008fb07f03044406a08fb"
            "07f131440969884218d008fb07f03044416a08fb07f030440069091a08fb07f0"
            "3044806a08fb07f232445269801a50f768ff08fb07f706eb07018861641c641c"
            "7069844280f089805ff0140808fb04f030441c30fff7d5fe81464846c0b20028"
            "01d0671c00e0270008fb04f030441c30fff7e8fe002895d108fb04f03044806a"
            "08fb04f13144896a6ff30f01401a08fb07f131448d6a08fb07f13144896a6ff3"
            "0f016d1a41426a42002801d1002001e0d0f58030002d01d1002501e0d5f58035"
            "a84201da0500ffe78a4200db11004ff400431a000020d6f814c0bcf1010c6745"
            "0fd208fb07fcb444dcf83cc008fb07feb644def828e015eb0e0e13eb0e039c45"
            "16db002c0bd008fb04f333449b6acb189a1a08fb04f333445b699a4206db4a42"
            "aa4201da8a460de7aa460be7aa4609e7002c0cd008fb04f03044806a0818821a"
            "08fb04f0304440698242fff6f6ae8a46cd42bff6f6ae0120f4e6b068fef700fd"
            "040035e0611eb068fef7fefc8046d8f80050142707fb05f03044c16b07fb05f0"
            "3044826ad8f80400821812f5004291421ddb07fb05f03044816ad8f804004118"
            "07fb05f03044816207fb05f030441c30fff727fe00280ad007fb05f030444169"
            "d8f8040041187d4306eb05004161641e002cc7d1bde8f3872de9f84f05000c00"
            "914601262700c8462000fff702fe002802d14f46002605e04846fff7fafd0028"
            "00d100263000c0b2002805d0d9f80800a1688842c0f2ce80002400e0641c6869"
            "844207d2"),
    },
    {
        "function": "open_cfw_runtime_am142_0x0059d380",
        "runtime_address": 0x0059D380,
        "source": (
            "components/apollo_main/core_overlay/"
            "runtime_liblc3_am142_0x59d380.c"),
        "size": 50,
        "sha256": (
            "03d6a2973c8f968952530352612d0c31ae9c87116edc63adb64a4f53f2cbc365"),
        "bytes": (
            "b81281f85d0099e60df57050d0f8b802007a002805d115a8fff7ccfb0028"
            "41f098820df57050d0f8b802007a002802d0306a"),
    },
    {
        "function": "open_cfw_runtime_am142_0x0059ba96",
        "runtime_address": 0x0059BA96,
        "source": (
            "components/apollo_main/core_overlay/"
            "runtime_liblc3_am142_0x59ba96.c"),
        "size": 78,
        "sha256": (
            "064b28a3856c65f74d8511eb196ed81f9fb0de41dd63096db3dc299ae8fe820f"),
        "bytes": (
            "142000fb04f02844406ab9688842f3db3000c0b20028686984421ed2142000"
            "fb04f12944496aba68914200f0b1803100c9b2002908d0d8f8081000fb04f2"
            "2a44526a914280f2a48000fb04f02844"),
    },
    {
        "function": "open_cfw_runtime_am142_0x0059bae4",
        "runtime_address": 0x0059BAE4,
        "source": (
            "components/apollo_main/core_overlay/"
            "runtime_liblc3_am142_0x59bae4.c"),
        "size": 1666,
        "sha256": (
            "1607ff3882b913be4a8fddb0a47c5d373e7be05407cd32c4c0044e2d70ae58eb"),
        "bytes": (
            "1c30fff7cefd002840f09b806868fff70afe00282ad03800fff7dbfd002825d1"
            "3000c0b200281cd0d8f80810b8684118022091fbf0f16868fff7f8fd81462969"
            "d8f80820b868121a022092fbf0f050f7f1fdb9eb0001f96010eb0909c8f80c90"
            "04e0b9686868fff7e1fdf860002c07d0f868142101fb04f129444969884260db"
            "6869844215d23000c0b2002809d0142000fb04f02844806ad8f80c10884208da"
            "4fe0142000fb04f02844806af968884247dbd5f81490b9f101093000c0b20028"
            "04d0d5f814a01af1010a01e0d5f814a0d5f814b0bbeb040bbaf1c00f10d330e0"
            "142101fb0af028441c3001fb09f129441c31142266f624f8b9f10109baf1010a"
            "5846b0f1010b0028ead15ff0140909fb04f028441c303900142266f611f86869"
            "401c6861f6b2002e0bd009fb04f405eb040030304146142266f602f86869401c"
            "6861bde8f18f2de9f84faab004000d0090461e00ddf8d4b027685846c0b20028"
            "12d16068fff75ffd00280dd1316823a800f063ff012001903498009023ab4246"
            "29006068fff7dfff300000f061ff00281ad12800fef7abfb81464046fef7a7fb"
            "10eb09094946300000f084ff300000f04fff002808d1387a002804d000203168"
            "0860002060731ee1002060610020a06123a831001c2265f6b3ff23a800f03eff"
            "80462800fef783fb0390b06803998842c0f0098197f8f90000280ed01ea8fff7"
            "b7fc1eaa17f590712000fff7acfe17f586721ea92000fff7a6fe5ff000095ff0"
            "800a48e05ffa8afa5fea5a0a41e098f800101aea010f34d00120029020690190"
            "349800903b004a4629000aa8fff718fc0020029020690190349800903b004a46"
            "290005a8fff70cfc0aa8fff7b2fc00280cd105a8fff7adfc002807d105aa0aa9"
            "17f1f000fef76efd00280ad005aa0aa92000fff768fe98f8000030ea0a0088f8"
            "000019f007000728bcd118f101085ff0800a19f1010903988145b8d35846c0b2"
            "00282cd0606900280ad0606a012807da61691420414304eb0100006900280ed5"
            "6846fff745fc312000902069049019a8fff73efc19aa69462000fff734fe2000"
            "fff793fc2000fff7d7fc2000fff78dfc5ffa8bfbbbf1000f6fd100276ae023a8"
            "00f09cfe80465ff000095ff0800a04e05ffa8afa5fea5a0a2ce003988145ded2"
            "98f800101aea010f1cd00120029020690190349800903b004a46290014a8fff7"
            "8ffb0020029020690190349800903b004a4629000fa8fff783fb0faa14a92000"
            "fff7f1fd19f007000728d1d118f101085ff0800a19f10109cfe708fb07f804eb"
            "0800806ac9f80c0020e05ff0140808fb07f020441c30fff712fc002819d108fb"
            "07f02044016a2800fef795fa814608fb07f020441c30fff7eafb0028ddd008fb"
            "07f804eb0800806ac9f81000012089f800007f1c60698742d7d3012020730021"
            "300000f029fe2bb0bde8f08f2de9fe4f04000d009346ddf830a00d9e0e9fddf8"
            "3c80ddf8409042f6086100220094009868f6f6f800982560c4f804b042f65c5b"
            "08232a1d296804eb0b00fef7f0f90298009004eb0b0314f5f252290014f5f250"
            "fff7c8fb0298009004eb0b0314f5f252290004f62470fff7bdfb0298009004eb"
            "0b0314f5f252290014f10800fff7b2fba86a42f67c516050286b14f536510860"
            "686b42f684516050119ad2e9000142f688522244c2e9000142f6945044f800a0"
            "42f69850265042f69c50275042f6a05044f8008042f6a45044f8009095f8b900"
            "42f69251605442f6a850d5f8e410215042f6ac51d5f8e82062506258002a02d5"
            "6258524200e062582358002b02d523585b4200e023589a4207da2158002902d5"
            "2058404208e0205806e06058002802d56058404200e06058400042f6b0516050"
            "41f69a1042f6b4516050012042f693516054002042f690516054002042f69151"
            "6054002042f6e0516054bde8f78f80b542f65c510844fef768f901bd2de9fc41"
            "05000e001400089f190042f67c50285850f750fb8046390015f53650006850f7"
            "49fb10eb0808cdf8008039003000fff73dfb019000992868006c50f73bfb0600"
            "01992868806c50f735fb861942f6885028588619266000992868406c50f72afb"
            "060001992868c06c50f724fb861942f68c50285886196660bde8f3812de9f84f"
            "86b005000e0017009846ddf8409039683068091a10314911029179687068091a"
            "103149110391d9f80010d8f80000091a103149110091d9f80410d8f80400091a"
            "103149110191d8f800103068091a103149110491d8f804107068091a10314911"
            "05910199029850f7e5fa04000099039850f7e0fa241a002c01d10020eae0ddf8"
            "44a0"),
    },
    {
        "function": "open_cfw_runtime_am142_0x0059d3b2",
        "runtime_address": 0x0059D3B2,
        "source": (
            "components/apollo_main/core_overlay/"
            "runtime_liblc3_am142_0x59d3b2.c"),
        "size": 78,
        "sha256": (
            "5a5a8798f05b5f76a370e73991222fe2e57809223d2a7751e7b58c31ddfd147f"),
        "bytes": (
            "406800e00020019006a800900df57053d3f8f43224aa29000df57050d0f8b802"
            "fff702fc96f82402002801d101f078ba37e60df57050d0f8b802007a002805"
            "d115a8fff79efb002841f06a820df5"),
    },
    {
        "function": "open_cfw_runtime_am142_0x0059b714",
        "runtime_address": 0x0059B714,
        "source": (
            "components/apollo_main/core_overlay/"
            "runtime_liblc3_am142_0x59b714.c"),
        "size": 86,
        "sha256": (
            "51534b5383ff5110f5a83d59b9687be1f194c58cc2ed814525bd203a92a50c36"),
        "bytes": (
            "08006969002902d0697b002903d1296950f7f8ff37e0ac6900e0641c6969"
            "491e8c4206d2142101fb04f12944896b8842f3da002c08d0142101fb04f1"
            "2944496a884201da641ef4e7ac61002c0ad1696a884207da2969"),
    },
    {
        "function": "open_cfw_runtime_am142_0x0059cd86",
        "runtime_address": 0x0059CD86,
        "source": (
            "components/apollo_main/core_overlay/"
            "runtime_liblc3_am142_0x59cd86.c"),
        "size": 152,
        "sha256": (
            "f58ad2de6ddc3efdebb1e5a99ce054b25c8679ffb1d9061c713330ce6abfaed5"),
        "bytes": (
            "5ffa89f9b9f1000f05d0b96a401838632868786326e021683963f96a401878"
            "6320e0b87a00280ad04146039802f0d1f818f1010804a98a6a8018086301"
            "e020681090f87a00280bd004afd7f82c904146039802f0bef810eb0909c7"
            "f8349001e02868119000272be0062004a900fb07f201eb8201c969029104"
            "a900fb07f201eb82018969019104a900fb07f201eb82014969009104a900fb"),
    },
    {
        "function": "open_cfw_runtime_am142_0x0059b76c",
        "runtime_address": 0x0059B76C,
        "source": (
            "components/apollo_main/core_overlay/"
            "runtime_liblc3_am142_0x59b76c.c"),
        "size": 156,
        "sha256": (
            "4342b63ebc8f581c85fe0084571aad2680c4cf68b8e3220c289429c4ef9179d3"),
        "bytes": (
            "801a50f7d3ffa96a081810e0142606fb04f12944c96a06fb04f22a44526"
            "a801a50f7c4ff744305eb0401896a081870bd2de9fc470600b068fef712"
            "fe002482e05ff0000a012000e00020c0b2002813d07069401e87420fd2"
            "08fb07f030443030fff773ff002807d10097b5eb0a0501956946b068fe"
            "f70bfe08fb04f03044806a1aeb000008fb04f1314488624846c0b20028"
            "0ad008fb07f03044806a"),
    },
    {
        "function": "open_cfw_runtime_am142_0x0059cc40",
        "runtime_address": 0x0059CC40,
        "source": (
            "components/apollo_main/core_overlay/"
            "runtime_liblc3_am142_0x59cc40.c"),
        "size": 156,
        "sha256": (
            "eeff754f237efaa6928bf18c8de6359252885bd942ac002dad566d7d5081e412"),
        "bytes": (
            "b00090f82402002829d15ffa89f9b9f1000f01d001241de000241be021002"
            "80002f07af910eb0a0acdf808a0611c280002f072f910eb0a0acdf80ca0"
            "00208df80400002004900498059001a93000fdf7b4fba41c4445e1d32800"
            "02f00ffa0120387007b0bde8f08f2de9f84f92b00c0015001e001c9f2"
            "1680491296805915ff00008797a002902d15ff0010901e05ff000094946"
            "c9b2002902d05ff0"),
    },
    {
        "function": "open_cfw_runtime_am142_0x0059ccdc",
        "runtime_address": 0x0059CCDC,
        "source": (
            "components/apollo_main/core_overlay/"
            "runtime_liblc3_am142_0x59ccdc.c"),
        "size": 170,
        "sha256": (
            "8f167bd354c0197381dc97cada11d4d449594ba2ee0e6faee1e20d9443602eae"),
        "bytes": (
            "090a01e05ff00a0a5ff0000b03901be004a850f82b0004a901eb8b0188"
            "6017f80b0000280ed04146039802f027f918f1010804a901eb8b018968"
            "401804a901eb8b0188601bf1010bd345e1db5ffa89f9b9f1000f01d0"
            "28680f901d98c0b2002834d004aff96a2868091a002903d52968f86a"
            "091a02e0f96a2868091aba6a2068121a002a03d52268b86a121a02e0"
            "ba6a2068121a914202da5ff0010901e05ff000094146039802f0e9f8"),
    },
    {
        "function": "open_cfw_runtime_am142_0x0059c980",
        "runtime_address": 0x0059C980,
        "source": (
            "components/apollo_main/core_overlay/"
            "runtime_liblc3_am142_0x59c980.c"),
        "size": 172,
        "sha256": (
            "12eb7ac8527c52c37ba35c87ecf221aa4b9c9ba5ae3dbfad4bc8f850fb5a4a24"),
        "bytes": (
            "524649461098fef7e2fd61680969401861680861e15906984118099154f80"
            "810059841180a911099069841180791059810eb0909cdf82090049810eb"
            "0a0acdf834a0039810eb0b0bcdf838b0049840190b90039880190c9042"
            "f6935914f80900002813d0dde909010a0001002000fff79ffd002004f8"
            "0900012042f690516054dde9070114f53752c2e9000142f6e05914f809"
            "0000280bd000200190dde907010091030009aa14f108012000"),
    },
    {
        "function": "open_cfw_runtime_am142_0x0059b5c4",
        "runtime_address": 0x0059B5C4,
        "source": (
            "components/apollo_main/core_overlay/"
            "runtime_liblc3_am142_0x59b5c4.c"),
        "size": 196,
        "sha256": (
            "7dc569c3ff72226e93d14e5eb8fe4f23007ef974cd05a7d00637160e006481bf"),
        "bytes": (
            "1ae000290cd5e4b2002c04d0b868a8600420286010e07868a86008202860"
            "0be0e4b2002c04d07868a8600420286003e0b868a86008202860280000f0"
            "48f8002805d0a868d8f8e81010eb4100a86009990898aa688018a86029"
            "616e602868002810d0387800280dd0280000f030f8002802d03869e860"
            "01e0f868e860280000f044f803e0a86851f765f8e860bde8f18310b5"
            "040014210022200068f651fd10bd0068002801d0012000e00020c0b270"
            "47007810f00c0f01d0012000e00020c0b270470068"),
    },
    {
        "function": "open_cfw_runtime_am142_0x0059ca2c",
        "runtime_address": 0x0059CA2C,
        "source": (
            "components/apollo_main/core_overlay/"
            "runtime_liblc3_am142_0x59ca2c.c"),
        "size": 208,
        "sha256": (
            "08f700259d377451d69780f4bff0c91ec29af88780b7b0f1d4ed26f9bad3cad4"),
        "bytes": (
            "fff787fc012004f80900042042f6e4516050dde9090142f6e8522244c2"
            "e90001dde9070142f6f0522244c2e90001dde90d0142f6f8522244c2"
            "e90001dde90b0114f53852c2e9000142f69c5954f8090000f05cf80028"
            "11d00020019042f6a0502058009054f8093042f69850225842f6945021"
            "5814f10800fff7c1f8e55144f8086011b0bde8f08ffeb5040042f690"
            "55605d00282cd042f691560120a05542f6dc50225842f6d850215820"
            "00fff78cfe42f6e057e05d002810d00120019014f53752d2e9000100"
            "91030042f6b85004eb"),
    },
    {
        "function": "open_cfw_runtime_am142_0x0059d8f0",
        "runtime_address": 0x0059D8F0,
        "source": (
            "components/apollo_main/core_overlay/"
            "runtime_liblc3_am142_0x59d8f0.c"),
        "size": 228,
        "sha256": (
            "51ca59c91cec06e4f7bebddec0ba97a73d0e2d6329f0886e66cf3a71ecb8a0a5"),
        "bytes": (
            "3e820c2800f049820e2800f06c820f2800f07c82102800f08b821128"
            "00f0c684122800f0e384142800f0e584152800f0f284162800f0fe84"
            "172800f01385182800f026851a2800f033851b2800f051851c2800f0"
            "5c851d2800f06b851e2800f08685212800f09185e1e1e0e10df57050"
            "d0f8b802007a00284fd0c9b2012901d1012700e000270021280001f0"
            "edfa81460221280001f0e8fa82460421280001f0e3fa834601212800"
            "01f0defabaeb0909b9eb00094a460221280001f008fb0321280001f0"
            "d1fabbeb0a0abaeb000a52460421280001f0fbfa3800c0b2002802d0"
            "306a0068"),
    },
    {
        "function": "open_cfw_runtime_am142_0x0059ce1e",
        "runtime_address": 0x0059CE1E,
        "source": (
            "components/apollo_main/core_overlay/"
            "runtime_liblc3_am142_0x59ce1e.c"),
        "size": 252,
        "sha256": (
            "ee9066685ccf21a8e19c36503171f421685b59fafd65a288b14eabd1fbc57e3d"),
        "bytes": (
            "07f201eb82010b6904a900fb07f201eb8201ca6804a900fb07f001eb80008168"
            "3000fff777fd7f1c022fd1db039802f036f904a8016b2160406b286013b0bde8"
            "f08f2de9f14f82b00c0015000298406900fb05f00090200001f0f5ff06000098"
            "361aaf195ff000081be03900200002f064f87f1c0100daf800004ff73efc1af1"
            "040a10eb0b0b19f10109029840698145ebd35a4616eb0801200002f081f818f1"
            "0108a8450cd20298806910f1040a16eb0801200002f041f883465ff00109e4e7"
            "0098451b2900200002f081f8bde8f78f00002de9fd4fadf5785daeb00f000024"
            "0df57050d0f8b802d0f8b0600df57050d0f8b802001d07900df57050"),
    },
    {
        "function": "open_cfw_runtime_am142_0x0059cf1a",
        "runtime_address": 0x0059CF1A,
        "source": (
            "components/apollo_main/core_overlay/"
            "runtime_liblc3_am142_0x59cf1a.c"),
        "size": 572,
        "sha256": (
            "65b337d7ca3d4a7ac004e3ec399088c2163ee79bdcdc6c33fed78f87424cb8d9"),
        "bytes": (
            "d0f8b80205680df57050d0f8b802406b10903000fef7f7fa0d905ff000080020"
            "8df81a0000208df81900002008900df57050d0f8f00209900020dff8500c0e90"
            "00205ff0ff308021002243f63469e944484667f6caf80c2100220df1e8094846"
            "67f6c3f8182100220df1d009484667f6bcf81023079a29002ca8fdf7bdf91423"
            "079a290024a8fdf7b7f91423079a29001ca8fdf7b1f9079915a8fff7b3fd0df5"
            "7050d0f8c00205900df57050d0f8b802f03004900998039015a802901ca80190"
            "24a80090109b0df57052d2f8bc220df57051d1f8b81241f22c006844fef77bff"
            "0df57050d0f8b802407a002803d001208df8180002e000208df818003000fef7"
            "7cfa0df57051d1f8f41208600df57050d0f8b802407a002804d03000fef717f9"
            "0f9001e030200f900f9a0799280001f0cffe0500002d1dd1402421000798fdf7"
            "e7fc07980068002841f22c006844fef7f3ff1ca8fdf75ef924a8fdf75bf92ca8"
            "fdf758f9280001f0dffe0df5785d31b0bde8f08f11212ca8fdf78df92ca8fdf7"
            "9df9039003983900102264f6befd0020059007980068002803d0cee7280002f0"
            "00f80df57050d0f8b802007a0028039801f085fe002806d00598002801d00b27"
            "15e00e2713e0039801f069fe07003800c0b20b2803d03800c0b20e2807d10df5"
            "7050d0f8b802407a002800d000270df57050d0f8b802007a002847d09df81900"
            "00281fd13800c0b201281bd03800c0b2032817d03800c0b20d2813d03800c0b2"
            "0a280fd03800c0b20b280bd03800c0b20c2807d03800c0b20e2803d0"),
    },
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _overlay_entry(function: str) -> dict[str, object]:
    overlay = json.loads(OVERLAY.read_text())
    return next(
        row for row in overlay["in_place_leaves"]
        if row.get("function") == function
    )


def _compile_and_extract(helper: dict[str, object]) -> tuple[bytes, dict[str, object]]:
    source = ROOT / str(helper["source"])
    with tempfile.TemporaryDirectory(prefix="g2-am142-source-candidate-") as tmp:
        object_path = Path(tmp) / (source.stem + ".o")
        subprocess.run(
            [
                CLANG,
                f"--target={TARGET}",
                *FLAGS,
                "-c",
                str(source),
                "-o",
                str(object_path),
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return apollo_overlay.extract_in_place_function_section(
            object_path,
            str(helper["function"]),
            runtime_address=int(helper["runtime_address"]),
            relocation_configs=[],
            strict_relocation_contract=True,
            allow_halfword_placement=True,
            allow_discarded_alloc_sections=True,
            record=True,
        )


def analyze() -> dict[str, object]:
    rows = []
    for helper in HELPERS:
        leaf, extraction = _compile_and_extract(helper)
        digest = hashlib.sha256(leaf).hexdigest()
        source = ROOT / str(helper["source"])
        overlay_entry = _overlay_entry(str(helper["function"]))
        stock = overlay_entry["stock"]
        source_record = overlay_entry["source"]
        routed = (
            source_record["path"] == helper["source"]
            and stock["size"] == len(leaf)
            and stock["sha256"] == digest
        )
        rows.append({
            "function": helper["function"],
            "runtime_address": f"0x{int(helper['runtime_address']):08x}",
            "source": helper["source"],
            "source_sha256": _sha256(source),
            "candidate_size": len(leaf),
            "candidate_sha256": digest,
            "candidate_bytes": leaf.hex(),
            "expected_size": helper["size"],
            "expected_sha256": helper["sha256"],
            "expected_bytes": helper["bytes"],
            "matches_expected": (
                len(leaf) == helper["size"]
                and digest == helper["sha256"]
                and leaf.hex() == helper["bytes"]
            ),
            "routing_status": (
                "routed_into_overlay" if routed
                else "not_yet_routed_into_overlay"),
            "extraction": extraction,
        })

    routed_count = sum(
        1 for row in rows
        if row["routing_status"] == "routed_into_overlay"
    )
    report = {
        "schema_version": 2,
        "raw_helper_source": str(RAW_SOURCE.relative_to(ROOT)),
        "raw_helper_source_sha256": (
            _sha256(RAW_SOURCE) if RAW_SOURCE.exists()
            else RAW_SOURCE_SHA256),
        "raw_helper_source_status": (
            "present" if RAW_SOURCE.exists()
            else "retired_digest_only"),
        "toolchain_profile": "apple-clang",
        "compiler": CLANG,
        "target": TARGET,
        "helper_count": len(rows),
        "routed_helper_count": routed_count,
        "source_owned_helper_bytes": sum(
            int(row["candidate_size"]) for row in rows
            if row["routing_status"] == "routed_into_overlay"
        ),
        "all_helpers_match_expected": all(
            bool(row["matches_expected"]) for row in rows),
        "all_helpers_routed": routed_count == len(rows),
        "next_remediation": (
            "continue replacing the remaining AM142 raw helper spans"),
        "helpers": rows,
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def main() -> None:
    report = analyze()
    print(json.dumps({
        "all_helpers_match_expected": report["all_helpers_match_expected"],
        "all_helpers_routed": report["all_helpers_routed"],
        "helper_count": report["helper_count"],
        "routed_helper_count": report["routed_helper_count"],
        "source_owned_helper_bytes": report["source_owned_helper_bytes"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
