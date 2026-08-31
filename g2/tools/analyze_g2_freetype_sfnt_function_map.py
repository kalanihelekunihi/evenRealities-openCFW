#!/usr/bin/env python3
"""Build a fail-closed function map for the stock G2 FreeType 2.9.1 SFNT module.

The map is research evidence only.  It does not emit an overlay, rewrite a
callsite, or assert compiler byte identity.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import struct
import sys
from pathlib import Path
from typing import Any


G2 = Path(__file__).resolve().parents[1]
IMAGE = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
GHIDRA = G2 / "research/corpus/apollo-main/ghidra/decomp/functions.jsonl"
SOURCE_ADMISSION = G2 / "tools/analyze_g2_cordio_ll_sea_none_source_admission.py"
BATCH10 = G2 / "tools/analyze_g2_cordio_ll_sea_none_batch10_candidate.py"
SFNT = G2 / "third_party/freetype/src/sfnt"
SFNT_HEADER = G2 / "third_party/freetype/include/freetype/internal/sfnt.h"

LOAD_BASE = 0x00437FE0
IMAGE_PIN = (3_523_396, "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863")
GHIDRA_PIN = (3_270_703, "9fd9c1c34e17abb977f2ccb32a931d9b96743db2db10707de19bf9ea6ae42662")
SOURCE_MAPPING_SHA256 = "6fb586837c60efec60ac5dc603315cfc25bab6809cda67b90fece419658beb56"

MODULE_CLASS = 0x0075A3F8
MODULE_NAME = 0x0078E6A4
INTERFACE_TABLE = 0x0069CA14
ENVELOPE = (0x005DA1E8, 0x005E1594)

SOURCE_PINS = {
    "sfnt.c": (1_544, "b562b9d52c72fdd48ae92ed52fc843d2fe12f59e95f1e832814e56105b915803"),
    "sfdriver.c": (34_308, "79c368e8d3a933bb1353295046aa991d342ee272fb9b3654fb852ced396b10be"),
    "sfobjs.c": (58_595, "87999f1d3183a70e406e28d93f6b77e9a158f0e635cb3fb725af0655b7e6c402"),
    "ttbdf.c": (7_083, "ea44af46d27e96590681f72273273da12e146968d9c61711ca8fa73c6c99ed23"),
    "ttcmap.c": (120_864, "e321c3d6cac43fa450698f5a98456fd8e84d7da0b37ea75531ad79c3cecfe5fb"),
    "ttkern.c": (8_081, "7df687ce36895754b3b3cec950409255bb1f00b26d0c2c8107743cef47112a26"),
    "ttload.c": (52_871, "fff297b78a470479cc41994f005a7ae5acba78ab50b1aa0fdfad7b1f7ec28ef7"),
    "ttmtx.c": (12_312, "0ccf75bfa5f2306be72650425bfae36a86f3fc92c80987cdc80d59deeabc589d"),
    "ttpost.c": (17_199, "9ff630ae5a4da8558507f40ac8cce5ee132117f017568c1e23398a3cb4764bc1"),
    "ttsbit.c": (49_324, "3f4605f0bc48656411d5452999637de1e25dc559fd8d1f12df2982192d265fda"),
}
HEADER_PIN = (46_042, "14c68938a1da61653b0188a49407f621f0845e203ac27eb24481c5d9ba2438d6")

SFNT_MODULES = {
    "sfdriver.c", "sfobjs.c", "ttbdf.c", "ttcmap.c", "ttkern.c",
    "ttload.c", "ttmtx.c", "ttpost.c",
}
PSAUX_MODULES = {"cffdecode.c", "psconv.c", "psft.c", "psobjs.c", "t1cmap.c", "t1decode.c"}

# slot, symbol, module, entry, mapped end, boundary evidence
INTERFACE_SPECS = (
    (0, "tt_face_goto_table", "ttload.c", 0x005DF182, 0x005DF1AE, "ghidra-body"),
    (1, "sfnt_init_face", "sfobjs.c", 0x005DB578, 0x005DB92A, "ghidra-body"),
    (2, "sfnt_load_face", "sfobjs.c", 0x005DB960, 0x005DC138, "adjacent-source-order"),
    (3, "sfnt_done_face", "sfobjs.c", 0x005DC138, 0x005DC266, "adjacent-source-order"),
    (4, "sfnt_get_interface", "sfdriver.c", 0x005DAB82, 0x005DAB8E, "adjacent-source-order"),
    (5, "tt_face_load_any", "ttload.c", 0x005DF484, 0x005DF4D4, "ghidra-body"),
    (6, "tt_face_load_head", "ttload.c", 0x005DF504, 0x005DF510, "ghidra-body"),
    (7, "tt_face_load_hhea", "ttmtx.c", 0x005DFB18, 0x005DFB9C, "adjacent-source-order"),
    (8, "tt_face_load_cmap", "ttload.c", 0x005DF8B2, 0x005DF8F0, "adjacent-source-order"),
    (9, "tt_face_load_maxp", "ttload.c", 0x005DF51C, 0x005DF5B6, "adjacent-source-order"),
    (10, "tt_face_load_os2", "ttload.c", 0x005DF8F0, 0x005DF9A6, "adjacent-source-order"),
    (11, "tt_face_load_post", "ttload.c", 0x005DF9A6, 0x005DF9D8, "adjacent-source-order"),
    (12, "tt_face_load_name", "ttload.c", 0x005DF5B6, 0x005DF832, "ghidra-body"),
    (13, "tt_face_free_name", "ttload.c", 0x005DF832, 0x005DF8B2, "adjacent-source-order"),
    (14, "tt_face_load_kern", "ttkern.c", 0x005DEE2A, 0x005DEFB6, "adjacent-source-order"),
    (15, "tt_face_load_gasp", "ttload.c", 0x005DFA0C, 0x005DFAD8, "adjacent-source-order"),
    (16, "tt_face_load_pclt", "ttload.c", 0x005DF9D8, 0x005DFA0C, "adjacent-source-order"),
    (17, "tt_face_load_bhed", "ttload.c", 0x005DF510, 0x005DF51C, "adjacent-source-order"),
    (18, "tt_face_load_sbit_image", "ttsbit.c", 0x005E14A4, 0x005E1594, "ghidra-body"),
    (19, "tt_face_get_ps_name", "ttpost.c", 0x005E010E, 0x005E01EA, "ghidra-body"),
    (20, "tt_face_free_ps_names", "ttpost.c", 0x005E0088, 0x005E010E, "adjacent-source-order"),
    (21, "tt_face_get_kerning", "ttkern.c", 0x005DEFDE, 0x005DF158, "ghidra-body"),
    (22, "tt_face_load_font_dir", "ttload.c", 0x005DF2F2, 0x005DF484, "ghidra-body"),
    (23, "tt_face_load_hmtx", "ttmtx.c", 0x005DFAD8, 0x005DFB18, "adjacent-source-order"),
    (24, "tt_face_load_sbit", "ttsbit.c", 0x005E01EA, 0x005E04AA, "ghidra-body"),
    (25, "tt_face_free_sbit", "ttsbit.c", 0x005E04E4, 0x005E0506, "adjacent-source-order"),
    (26, "tt_face_set_sbit_strike", "ttsbit.c", 0x005E0506, 0x005E0512, "adjacent-source-order"),
    (27, "tt_face_load_strike_metrics", "ttsbit.c", 0x005E0512, 0x005E072A, "ghidra-body"),
    (28, "tt_face_get_metrics", "ttmtx.c", 0x005DFB9C, 0x005DFD20, "ghidra-body"),
    (29, "tt_face_get_name", "sfobjs.c", 0x005DAC40, 0x005DADEE, "ghidra-body"),
    (30, "sfnt_get_name_id", "sfdriver.c", 0x005DA5D6, 0x005DA656, "ghidra-body"),
)

# Private rows are deliberately medium confidence: their identities have
# source-order and call-graph support but no stock exported-table pointer.
TTSBIT_PRIVATE = (
    ("tt_sbit_decoder_init", 0x005E072A, ()),
    ("tt_sbit_decoder_done", 0x005E0816, ()),
    ("tt_sbit_decoder_alloc_bitmap", 0x005E0818, ()),
    ("tt_sbit_decoder_load_metrics", 0x005E08D0, ()),
    ("tt_sbit_decoder_load_byte_aligned", 0x005E093A, ()),
    ("tt_sbit_decoder_load_compound", 0x005E0C48, (0x005E0EB4,)),
    ("tt_sbit_decoder_load_bitmap", 0x005E0D30, (0x005E0818, 0x005E08D0, 0x005E0C48)),
    ("tt_sbit_decoder_load_image", 0x005E0EB4, (0x005E08D0, 0x005E0D30)),
    ("tt_face_load_sbix_image", 0x005E12C8, (0x005DFB9C,)),
)

# symbol, module, start, end, source signature, body hash, anchor kind
RECOVERED_HIGH = (
    (
        "tt_face_load_bdf_props", "ttbdf.c", 0x005DC290, 0x005DC38A,
        "FT_Error ( TT_Face face, FT_Stream stream )",
        "852570bd7508b5b4dc07396b385164ee540560f51e721eb6c99ed2ec6b25e9dd",
        "direct-thumb-call",
    ),
    (
        "tt_face_find_bdf_prop", "ttbdf.c", 0x005DC3C4, 0x005DC53C,
        "FT_Error ( TT_Face face, const char* property_name, BDF_PropertyRec* aprop )",
        "bf122132e068cb63d89aba2e2ada8c21032be643fc60ecfa96a6a9f3f6de673e",
        "stock-service-table",
    ),
    (
        "tt_cmap_init", "ttcmap.c", 0x005DC53C, 0x005DC542,
        "FT_Error ( TT_CMap cmap, FT_Byte* table )",
        "c5e328d89f53179b3ebce06235ac0e47f1d4fbfc23027d806822d57cd3f4e290",
        "stock-cmap-class-tables",
    ),
    (
        "tt_sbit_decoder_load_bit_aligned", "ttsbit.c", 0x005E0A70, 0x005E0C48,
        "FT_Error ( TT_SBitDecoder decoder, FT_Byte* p, FT_Byte* limit, FT_Int x_pos, FT_Int y_pos, FT_UInt recurse_count )",
        "570f4c16619b4c02a929efeb9302f4196d17955d590a41139cd4e2e376f03fac",
        "stock-sbit-loader-table",
    ),
)

# The stock cmap class layout is the 13-word FT_DEFINE_TT_CMAP layout:
# class size, init, done, char_index, char_next, five variation callbacks,
# format, validate, and get_cmap_info.  Each row below binds a pointer slot to
# an exact FreeType 2.9.1 definition and to a complete hashed Thumb body.
# Non-cmap rows use equally direct stock service or function-literal anchors.
#
# symbol, module, start, end, source signature, body hash, table kind,
# table base, slot index, slot name, pointer reference
TABLE_CALLBACKS = (
    ("sfnt_get_charset_id", "sfdriver.c", 0x005DAB3A, 0x005DAB82,
     "FT_Error ( TT_Face face, const char** acharset_encoding, const char** acharset_registry )",
     "c77a0e8d379683d0440eaec24c5797b97d38e45c14b1f73e7416c5e525e9d2f9",
     "sfnt-bdf-service", 0x0078E6B4, 0, "get_charset_id", 0x0078E6B4),
    ("sfnt_stream_close", "sfobjs.c", 0x005DAE54, 0x005DAE72,
     "void ( FT_Stream stream )",
     "3c5e54c1998461fbc733a6b41f353ada948a1a3d684f80320c75a8656f38b3f2",
     "woff-function-literal", 0x005DB948, 0, "stream_close", 0x005DB948),
    ("compare_offsets", "sfobjs.c", 0x005DAE72, 0x005DAE90,
     "int ( const void* a, const void* b )",
     "62b57160e204099b845ceb09e98a14fd862cad61c02f4ccc01dc2568e054ba30",
     "woff-function-literal", 0x005DB944, 0, "qsort_compare", 0x005DB944),
    ("tt_cmap0_char_index", "ttcmap.c", 0x005DC5B4, 0x005DC5C6,
     "FT_UInt ( TT_CMap cmap, FT_UInt32 char_code )",
     "66a993919d9687b9de2035dd2ceadb1045e5c210686c6e54ee6d495fbb4fffc7",
     "cmap-format-0", 0x0072DD74, 3, "char_index", 0x0072DD80),
    ("tt_cmap0_char_next", "ttcmap.c", 0x005DC5C6, 0x005DC5E8,
     "FT_UInt32 ( TT_CMap cmap, FT_UInt32* pchar_code )",
     "65ae7c723624a3d6a00728d05bca510738f0ecb6ef76f6b6ab0c7034848c8ae7",
     "cmap-format-0", 0x0072DD74, 4, "char_next", 0x0072DD84),
    ("tt_cmap0_get_info", "ttcmap.c", 0x005DC5E8, 0x005DC600,
     "FT_Error ( TT_CMap cmap, TT_CMapInfo* cmap_info )",
     "200781a24bd312842278459a003dd8927e74081b92dac025b96991b28753033f",
     "cmap-format-0", 0x0072DD74, 12, "get_cmap_info", 0x0072DDA4),
    ("tt_cmap2_char_index", "ttcmap.c", 0x005DC7E2, 0x005DC85A,
     "FT_UInt ( TT_CMap cmap, FT_UInt32 char_code )",
     "c1e80d4345478f13832b86ea284f33482c12e9e43ee94fddde63a68830f90727",
     "cmap-format-2", 0x0072DDA8, 3, "char_index", 0x0072DDB4),
    ("tt_cmap2_char_next", "ttcmap.c", 0x005DC85A, 0x005DC962,
     "FT_UInt32 ( TT_CMap cmap, FT_UInt32* pchar_code )",
     "b8e649155d46c89f1ec6435b31cabde50b4b6460169cf442cde0fca49c460290",
     "cmap-format-2", 0x0072DDA8, 4, "char_next", 0x0072DDB8),
    ("tt_cmap2_get_info", "ttcmap.c", 0x005DC962, 0x005DC97A,
     "FT_Error ( TT_CMap cmap, TT_CMapInfo* cmap_info )",
     "3f9c1456f1ec5b73a2420324db0c383487e2cdf65a545db17d62e65f24297ebc",
     "cmap-format-2", 0x0072DDA8, 12, "get_cmap_info", 0x0072DDD8),
    ("tt_cmap4_init", "ttcmap.c", 0x005DC97A, 0x005DC99C,
     "FT_Error ( TT_CMap4 cmap, FT_Byte* table )",
     "53f22460ac477692fd4ff24063b174bbeb8257ba020a066df5819cd38402a93d",
     "cmap-format-4", 0x0072DDDC, 1, "init", 0x0072DDE0),
    ("tt_cmap4_char_next", "ttcmap.c", 0x005DD3C6, 0x005DD40E,
     "FT_UInt32 ( TT_CMap cmap, FT_UInt32* pchar_code )",
     "799e55c9a5121fbcd20bf90d94909d324e79fb9a13b787975953f5ba7fa5c740",
     "cmap-format-4", 0x0072DDDC, 4, "char_next", 0x0072DDEC),
    ("tt_cmap4_get_info", "ttcmap.c", 0x005DD40E, 0x005DD426,
     "FT_Error ( TT_CMap cmap, TT_CMapInfo* cmap_info )",
     "250abbabde2a03898b988d04c8fe45d383fbfd5b1c51d13c6f818833975d430c",
     "cmap-format-4", 0x0072DDDC, 12, "get_cmap_info", 0x0072DE0C),
    ("tt_cmap6_validate", "ttcmap.c", 0x005DD426, 0x005DD4B6,
     "FT_Error ( FT_Byte* table, FT_Validator valid )",
     "c4c10aa96c82e46208500ec7c6fa317ad0bcd6628bdaeba0be4c0c3600214265",
     "cmap-format-6", 0x0072DE10, 11, "validate", 0x0072DE3C),
    ("tt_cmap6_char_index", "ttcmap.c", 0x005DD4B6, 0x005DD4F6,
     "FT_UInt ( TT_CMap cmap, FT_UInt32 char_code )",
     "a900b0558413209960446ec979433f4357ecc9e1fc9ed874ac0ad90ed85d261e",
     "cmap-format-6", 0x0072DE10, 3, "char_index", 0x0072DE1C),
    ("tt_cmap6_char_next", "ttcmap.c", 0x005DD4F6, 0x005DD56C,
     "FT_UInt32 ( TT_CMap cmap, FT_UInt32* pchar_code )",
     "060eaa346081d4b7975a31fbd5754533e2f249b8c0bc35d68830268d2fc151b2",
     "cmap-format-6", 0x0072DE10, 4, "char_next", 0x0072DE20),
    ("tt_cmap6_get_info", "ttcmap.c", 0x005DD56C, 0x005DD584,
     "FT_Error ( TT_CMap cmap, TT_CMapInfo* cmap_info )",
     "4e62d5313e8df01726f5469df03c9f73517b684cd097bfd769a025807d68bfea",
     "cmap-format-6", 0x0072DE10, 12, "get_cmap_info", 0x0072DE40),
    ("tt_cmap8_get_info", "ttcmap.c", 0x005DD934, 0x005DD956,
     "FT_Error ( TT_CMap cmap, TT_CMapInfo* cmap_info )",
     "89d144f2e2f894b507a0ff426e9195ab10f1627e9113719012b895b2edfd5c7d",
     "cmap-format-8", 0x0072DE44, 12, "get_cmap_info", 0x0072DE74),
    ("tt_cmap10_validate", "ttcmap.c", 0x005DD956, 0x005DDA04,
     "FT_Error ( FT_Byte* table, FT_Validator valid )",
     "9c257cbca885ed741e230e834b6e3ff80581cfbc097532131887936afa8c135d",
     "cmap-format-10", 0x0072DE78, 11, "validate", 0x0072DEA4),
    ("tt_cmap10_char_index", "ttcmap.c", 0x005DDA04, 0x005DDA68,
     "FT_UInt ( TT_CMap cmap, FT_UInt32 char_code )",
     "c7cadab00c018f6e5d333d0a366a14074c66d0417075f1870bf9a3e20a8f8054",
     "cmap-format-10", 0x0072DE78, 3, "char_index", 0x0072DE84),
    ("tt_cmap10_char_next", "ttcmap.c", 0x005DDA68, 0x005DDAF6,
     "FT_UInt32 ( TT_CMap cmap, FT_UInt32* pchar_code )",
     "1f9de8e5d5377064c276038387f9bb9f29b27c51ec6796bf00d82a99ce7a7709",
     "cmap-format-10", 0x0072DE78, 4, "char_next", 0x0072DE88),
    ("tt_cmap10_get_info", "ttcmap.c", 0x005DDAF6, 0x005DDB18,
     "FT_Error ( TT_CMap cmap, TT_CMapInfo* cmap_info )",
     "3beb66a0af6ec88b9bb6c8505fda4555ffd0c47ea6980c31ff0a2d75a09d7029",
     "cmap-format-10", 0x0072DE78, 12, "get_cmap_info", 0x0072DEA8),
    ("tt_cmap12_init", "ttcmap.c", 0x005DDB18, 0x005DDB3A,
     "FT_Error ( TT_CMap12 cmap, FT_Byte* table )",
     "794ad98f7ef960f9da7c1648e89e44db96c22dfbcd4b3d36bf6e713537f38b4b",
     "cmap-format-12", 0x0072DEAC, 1, "init", 0x0072DEB0),
    ("tt_cmap12_char_index", "ttcmap.c", 0x005DDE72, 0x005DDE7E,
     "FT_UInt ( TT_CMap cmap, FT_UInt32 char_code )",
     "7bf19507b1deb2a1047df20781a6fdcb8fe069b7caae5d66482d8853e8774aa8",
     "cmap-format-12", 0x0072DEAC, 3, "char_index", 0x0072DEB8),
    ("tt_cmap12_char_next", "ttcmap.c", 0x005DDE7E, 0x005DDEB4,
     "FT_UInt32 ( TT_CMap cmap, FT_UInt32* pchar_code )",
     "89c7ba6d54b0e6b6acea5c6652b96c9e31db407548930d88d73fa5ae4c753129",
     "cmap-format-12", 0x0072DEAC, 4, "char_next", 0x0072DEBC),
    ("tt_cmap12_get_info", "ttcmap.c", 0x005DDEB4, 0x005DDED6,
     "FT_Error ( TT_CMap cmap, TT_CMapInfo* cmap_info )",
     "878bc9a508889c802fcc171a8e089c42a310def5db04342e37bd1a5c273a916e",
     "cmap-format-12", 0x0072DEAC, 12, "get_cmap_info", 0x0072DEDC),
    ("tt_cmap13_init", "ttcmap.c", 0x005DDED6, 0x005DDEF8,
     "FT_Error ( TT_CMap13 cmap, FT_Byte* table )",
     "794ad98f7ef960f9da7c1648e89e44db96c22dfbcd4b3d36bf6e713537f38b4b",
     "cmap-format-13", 0x0072DEE0, 1, "init", 0x0072DEE4),
    ("tt_cmap13_char_index", "ttcmap.c", 0x005DE1EC, 0x005DE1F8,
     "FT_UInt ( TT_CMap cmap, FT_UInt32 char_code )",
     "acf96337e1eb9e732edb0f173d46f4d19aec98046192d1f32f5b855d533e519c",
     "cmap-format-13", 0x0072DEE0, 3, "char_index", 0x0072DEEC),
    ("tt_cmap13_char_next", "ttcmap.c", 0x005DE1F8, 0x005DE22E,
     "FT_UInt32 ( TT_CMap cmap, FT_UInt32* pchar_code )",
     "da218569d572c6932f201390ea546440c0303be3600861f3d55b85c8aa1bba4d",
     "cmap-format-13", 0x0072DEE0, 4, "char_next", 0x0072DEF0),
    ("tt_cmap13_get_info", "ttcmap.c", 0x005DE22E, 0x005DE250,
     "FT_Error ( TT_CMap cmap, TT_CMapInfo* cmap_info )",
     "35d5c96579f470744135230f39029008879d208759872287148fd77224b370eb",
     "cmap-format-13", 0x0072DEE0, 12, "get_cmap_info", 0x0072DF10),
    ("tt_cmap14_done", "ttcmap.c", 0x005DE250, 0x005DE270,
     "void ( TT_CMap14 cmap )",
     "6a9480fa9f5520308603a74ac700b46fbcd010c5d269da92dd23d588c423d61e",
     "cmap-format-14", 0x0072DF14, 2, "done", 0x0072DF1C),
    ("tt_cmap14_init", "ttcmap.c", 0x005DE2A8, 0x005DE2CE,
     "FT_Error ( TT_CMap14 cmap, FT_Byte* table )",
     "4684c42647c5f14b91f337e21d4545165393ff79e328b379c907d25c08acc357",
     "cmap-format-14", 0x0072DF14, 1, "init", 0x0072DF18),
    ("tt_cmap14_char_index", "ttcmap.c", 0x005DE576, 0x005DE57A,
     "FT_UInt ( TT_CMap cmap, FT_UInt32 char_code )",
     "a7ddd513d149ea16fdd4db3f82267f83087aeaddd06b5dde5468adb704205fc4",
     "cmap-format-14", 0x0072DF14, 3, "char_index", 0x0072DF20),
    ("tt_cmap14_char_next", "ttcmap.c", 0x005DE57A, 0x005DE582,
     "FT_UInt32 ( TT_CMap cmap, FT_UInt32* pchar_code )",
     "e2511d9fbd2d993240467f8a546d700a027b6f6bbedc0729a648995bcb33f03e",
     "cmap-format-14", 0x0072DF14, 4, "char_next", 0x0072DF24),
    ("tt_cmap14_get_info", "ttcmap.c", 0x005DE582, 0x005DE590,
     "FT_Error ( TT_CMap cmap, TT_CMapInfo* cmap_info )",
     "17b1355462d380041428e6fd3d8aa4155dd4dc5ab3ad5c22a0bc5ef5982beb98",
     "cmap-format-14", 0x0072DF14, 12, "get_cmap_info", 0x0072DF44),
    ("tt_cmap14_char_var_isdefault", "ttcmap.c", 0x005DE72A, 0x005DE7B2,
     "FT_Int ( TT_CMap cmap, FT_UInt32 char_code, FT_UInt32 variant_selector )",
     "bfee7b05184e419c559f27bd1b7fa00c1215c1b42658ddd0ab74c741980f96d1",
     "cmap-format-14", 0x0072DF14, 6, "char_var_isdefault", 0x0072DF2C),
    ("tt_cmap14_variants", "ttcmap.c", 0x005DE7B2, 0x005DE802,
     "FT_UInt32* ( TT_CMap cmap, FT_Memory memory )",
     "31752ca463a6a5b1d7f59ad486a3cd3cf580edb39c7fcf35dd1ddf903e62548d",
     "cmap-format-14", 0x0072DF14, 7, "variants", 0x0072DF30),
    ("tt_cmap14_char_variants", "ttcmap.c", 0x005DE802, 0x005DE8C2,
     "FT_UInt32* ( TT_CMap cmap, FT_Memory memory, FT_UInt32 char_code )",
     "e9d73cb16930f4db30b75043086c7fbdb239ebcd8551bc354894761993173725",
     "cmap-format-14", 0x0072DF14, 8, "char_variants", 0x0072DF34),
    ("tt_get_cmap_info", "ttcmap.c", 0x005DEE14, 0x005DEE2A,
     "FT_Error ( FT_CharMap charmap, TT_CMapInfo* cmap_info )",
     "3bd085ecec387711d4ada54cf7bfced17f878632174a60056eaec0644bd7934b",
     "tt-cmap-info-service", 0x0078F3F8, 0, "get_cmap_info", 0x0078F3F8),
)

CMAP_SLOT_CASTS = {
    1: "FT_CMap_InitFunc",
    2: "FT_CMap_DoneFunc",
    3: "FT_CMap_CharIndexFunc",
    4: "FT_CMap_CharNextFunc",
    5: "FT_CMap_CharVarIndexFunc",
    6: "FT_CMap_CharVarIsDefaultFunc",
    7: "FT_CMap_VariantListFunc",
    8: "FT_CMap_CharVariantListFunc",
    9: "FT_CMap_VariantCharListFunc",
    11: "TT_CMap_ValidateFunc",
    12: "TT_CMap_Info_GetFunc",
}

# Private format 12/13 binary mappers have no table slot of their own.  Their
# public table-dispatched char_index and char_next wrappers provide two direct
# calls each, while the mapper body calls the already authenticated per-format
# `next` helper.  The semantic marker pins are reviewed Thumb encodings for
# the one material source difference: format 12 computes start_id + delta with
# overflow rejection; format 13 returns the group's constant glyph id.
#
# symbol, start, end, body hash, wrapper BLs, internal BL, internal target,
# format-specific semantic marker address/end/bytes
PRIVATE_CMAP_HELPERS = (
    (
        "tt_cmap12_char_map_binary", 0x005DDD38, 0x005DDE72,
        "32ad681b5d6209e28aa786de81ecff0f29d6b5de02672ef467a58262f5a5d6bb",
        (0x005DDE78, 0x005DDEAE), 0x005DDE58, 0x005DDC74,
        0x005DDE12, 0x005DDE2A,
        "5ff0ff356d1a18eb0505a54201d2002402e00c19b4eb0804",
    ),
    (
        "tt_cmap13_char_map_binary", 0x005DE0CA, 0x005DE1EC,
        "ed274e27af9e48ca088daae54e334b07f8ad9aff81da6d56a9ac6e00f71e5027",
        (0x005DE1F2, 0x005DE228), 0x005DE1D2, 0x005DE026,
        0x005DE188, 0x005DE1A6,
        "99f8004099f801502d0455ea046599f8024055ea042599f803402c43d2b2",
    ),
)

# start, end, physical category, evidence label, pointer targets and locations.
# These records cover the complete mapped-function complement without claiming
# source identity for code envelopes whose callable corpus records are absent.
PHYSICAL_SPECS = (
    (0x005DADEE, 0x005DADF0, "alignment-padding", "zero-alignment", ()),
    (0x005DADF0, 0x005DADF8, "literal-constant-pool", "adjacent-source-literals", ()),
    (0x005DAE28, 0x005DAE54, "literal-constant-pool", "sfobjs-local-constant-table", ()),
    (0x005DB3DE, 0x005DB3E0, "alignment-padding", "zero-alignment", ()),
    (0x005DB3E0, 0x005DB3EC, "literal-constant-pool", "adjacent-source-literals", ()),
    (0x005DB562, 0x005DB564, "alignment-padding", "zero-alignment", ()),
    (0x005DB564, 0x005DB578, "literal-constant-pool", "adjacent-source-literals", ()),
    (0x005DB92A, 0x005DB92C, "alignment-padding", "zero-alignment", ()),
    (0x005DB92C, 0x005DB960, "literal-constant-pool", "sfnt-tag-and-pointer-literals", ()),
    (0x005DC38A, 0x005DC38C, "alignment-padding", "zero-alignment", ()),
    (0x005DC38C, 0x005DC3C4, "literal-constant-pool", "sfnt-tag-literals", ()),
    (0x005E0068, 0x005E0088, "literal-constant-pool", "postscript-name-pointer-literals", ()),
    (0x005E04AA, 0x005E04AC, "alignment-padding", "zero-alignment", ()),
    (0x005E04AC, 0x005E04E4, "literal-constant-pool", "sbit-tag-and-pointer-literals", ()),
    (0x005E0E98, 0x005E0EB4, "literal-constant-pool", "sbit-tag-literals", ()),
    (0x005E1482, 0x005E1484, "alignment-padding", "zero-alignment", ()),
    (0x005E1484, 0x005E1490, "function-pointer-table", "sbit-loader-callback-table", ((0x005E093A, 0x005E1484), (0x005E0A70, 0x005E1488), (0x005E0C48, 0x005E148C))),
    (0x005E1490, 0x005E14A4, "literal-constant-pool", "sbit-graphic-type-tags", ()),
)


class MapError(RuntimeError):
    pass


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _pinned(path: Path, pin: tuple[int, str]) -> bytes:
    data = path.read_bytes()
    if (len(data), _sha(data)) != pin:
        raise MapError(f"pin drift: {path}")
    return data


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise MapError(f"analyzer dependency unavailable: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _slice(image: bytes, start: int, end: int) -> bytes:
    if not (LOAD_BASE <= start < end):
        raise MapError("invalid image interval")
    body = image[start - LOAD_BASE:end - LOAD_BASE]
    if len(body) != end - start:
        raise MapError(f"image interval unavailable: 0x{start:08X}-0x{end:08X}")
    return body


def _u32(image: bytes, address: int) -> int:
    return struct.unpack("<I", _slice(image, address, address + 4))[0]


def _thumb_bl_target(image: bytes, address: int) -> int:
    first, second = struct.unpack("<HH", _slice(image, address, address + 4))
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
        raise MapError(f"0x{address:08X}: expected Thumb BL encoding")
    sign = (first >> 10) & 1
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    i1 = (~(j1 ^ sign)) & 1
    i2 = (~(j2 ^ sign)) & 1
    immediate = (
        (sign << 24) | (i1 << 23) | (i2 << 22) |
        ((first & 0x3FF) << 12) | ((second & 0x7FF) << 1)
    )
    if immediate & (1 << 24):
        immediate -= 1 << 25
    return address + 4 + immediate


def _record(
    image: bytes,
    symbol: str,
    module: str,
    start: int,
    end: int,
    confidence: str,
    evidence: list[str],
    span_kind: str,
) -> dict[str, Any]:
    body = _slice(image, start, end)
    return {
        "symbol": symbol,
        "module": module,
        "start": f"0x{start:08X}",
        "end_exclusive": f"0x{end:08X}",
        "bytes": len(body),
        "body_sha256": _sha(body),
        "confidence": confidence,
        "evidence": evidence,
        "span_kind": span_kind,
        "compiler_byte_identity_claimed": False,
    }


def _complement(intervals: list[tuple[int, int]], start: int, end: int) -> list[tuple[int, int]]:
    merged: list[list[int]] = []
    for left, right in sorted(intervals):
        if left < start or right > end or left >= right:
            raise MapError("mapped interval escaped SFNT envelope")
        if not merged or left > merged[-1][1]:
            merged.append([left, right])
        else:
            if left < merged[-1][1]:
                raise MapError("mapped function intervals overlap")
            merged[-1][1] = right
    out = []
    cursor = start
    for left, right in merged:
        if left > cursor:
            out.append((cursor, left))
        cursor = right
    if cursor < end:
        out.append((cursor, end))
    return out


def run_audit() -> dict[str, Any]:
    image = _pinned(IMAGE, IMAGE_PIN)
    ghidra_data = _pinned(GHIDRA, GHIDRA_PIN)
    source_text = {
        name: _pinned(SFNT / name, pin).decode("utf-8")
        for name, pin in SOURCE_PINS.items()
    }
    header = _pinned(SFNT_HEADER, HEADER_PIN).decode("utf-8")

    # Authenticate the stock module class, its human-readable name, and the
    # interface pointer before interpreting any function slot.
    class_words = struct.unpack("<9I", _slice(image, MODULE_CLASS, MODULE_CLASS + 36))
    expected_class = (0, 12, MODULE_NAME, 0x00010000, 0x00020000, INTERFACE_TABLE, 0, 0, 0x005DAB83)
    if class_words != expected_class or _slice(image, MODULE_NAME, MODULE_NAME + 5) != b"sfnt\0":
        raise MapError("stock sfnt module class/string anchor drift")
    table_words = struct.unpack("<32I", _slice(image, INTERFACE_TABLE, INTERFACE_TABLE + 128))
    if table_words[31] != 0:
        raise MapError("sfnt interface terminator/padding drift")

    # The 2.9.1 struct and initializer must still contain exactly the reviewed
    # 31 slots, in the same order as the stock table.
    interface_names = [row[1] for row in INTERFACE_SPECS]
    macro_start = source_text["sfdriver.c"].find("FT_DEFINE_SFNT_INTERFACE(")
    macro_end = source_text["sfdriver.c"].find("FT_DEFINE_MODULE(", macro_start)
    macro = source_text["sfdriver.c"][macro_start:macro_end]
    positions = [
        (match.start() if (match := re.search(rf"\b{re.escape(name)}\b", macro)) else -1)
        for name in interface_names
    ]
    if macro_start < 0 or macro_end < 0 or -1 in positions or positions != sorted(positions):
        raise MapError("FreeType 2.9.1 SFNT initializer order drift")
    header_fields = re.findall(
        r"^\s+(?:TT|FT)_[A-Za-z0-9_]+\s+([a-z0-9_]+);\s*$",
        header[header.find("typedef struct  SFNT_Interface_"):header.find("} SFNT_Interface;")],
        re.MULTILINE,
    )
    if len(header_fields) != 31:
        raise MapError("SFNT_Interface field count drift")
    include_order = [
        source_text["sfnt.c"].find(f'#include "{name}"')
        for name in ("sfdriver.c", "sfobjs.c", "ttbdf.c", "ttcmap.c", "ttkern.c", "ttload.c", "ttmtx.c", "ttpost.c", "ttsbit.c")
    ]
    if -1 in include_order or include_order != sorted(include_order):
        raise MapError("sfnt.c single-object source order drift")

    ghidra_rows: dict[int, dict[str, Any]] = {}
    for line in ghidra_data.splitlines():
        raw = json.loads(line)
        entry = int(raw["entry"], 16)
        if entry in ghidra_rows:
            raise MapError(f"duplicate Ghidra entry: 0x{entry:08X}")
        ghidra_rows[entry] = raw

    source_report = _load(SOURCE_ADMISSION, "open_cfw_sfnt_source_dependency").run_audit()
    if source_report["census"]["mapping_sha256"] != SOURCE_MAPPING_SHA256:
        raise MapError("closed source-admission mapping drift")
    batch10 = _load(BATCH10, "open_cfw_sfnt_batch10_dependency").run_audit()

    high = []
    high_starts = set()
    census_overlap = set()
    for slot, symbol, module, start, end, boundary in INTERFACE_SPECS:
        if table_words[slot] != start | 1:
            raise MapError(f"SFNT interface slot {slot} pointer drift")
        if re.search(rf"(?m)^  {re.escape(symbol)}\s*\(", source_text[module]) is None:
            raise MapError(f"{module}:{symbol}: definition missing")
        evidence = [
            "stock-interface-table",
            "stock-sfnt-name-string",
            "freetype-2.9.1-slot-order",
        ]
        if boundary == "ghidra-body":
            row = ghidra_rows.get(start)
            if row is None or int(row["body_start"], 16) != start or int(row["body_end_inclusive"], 16) + 1 != end:
                raise MapError(f"{symbol}: Ghidra body boundary drift")
            if row["body_sha256"] != _sha(_slice(image, start, end)):
                raise MapError(f"{symbol}: Ghidra/image body hash mismatch")
            evidence.append("pinned-ghidra-body")
        else:
            if start in ghidra_rows:
                raise MapError(f"{symbol}: expected missing Ghidra row is now present")
            evidence.append("adjacent-single-object-source-order")
        record = _record(image, symbol, module, start, end, "high", evidence, boundary)
        record["interface_slot"] = slot
        record["thumb_pointer"] = f"0x{table_words[slot]:08X}"
        high.append(record)
        high_starts.add(start)

    medium = []
    sfnt_census = []
    psaux_counts = [0, 0]
    for row in source_report["census"]["records"]:
        if row["provider"] != "freetype-2.9.1-ftl":
            continue
        if row["module"] in PSAUX_MODULES:
            psaux_counts[0] += 1
            psaux_counts[1] += row["bytes"]
        if row["module"] not in SFNT_MODULES:
            continue
        sfnt_census.append(row)
        start = int(row["start"], 16)
        if start in high_starts:
            census_overlap.add(start)
            continue
        end = int(row["end_exclusive"], 16)
        ghidra = ghidra_rows.get(start)
        if ghidra is None or ghidra["body_sha256"] != row["body_sha256"] or ghidra["body_bytes"] != row["bytes"]:
            raise MapError(f"{row['symbol']}: source census/Ghidra drift")
        medium.append(_record(
            image, row["symbol"], row["module"], start, end, "medium",
            ["closed-source-admission-census", "single-object-source-order", "pinned-ghidra-body"],
            "ghidra-body",
        ))
    if (len(sfnt_census), sum(row["bytes"] for row in sfnt_census)) != (61, 16_520):
        raise MapError("SFNT source census accounting drift")
    if tuple(psaux_counts) != (57, 7_114):
        raise MapError("PSAux candidate accounting drift")
    if (len(census_overlap), sum(row["bytes"] for row in sfnt_census if int(row["start"], 16) in census_overlap)) != (10, 3_444):
        raise MapError("SFNT interface/source-census overlap drift")

    outside = batch10["authenticated_outside_none_census"]
    if (outside["functions"], outside["bytes"], len(outside["records"])) != (1, 102, 1):
        raise MapError("authenticated ttpost wrapper accounting drift")
    post = outside["records"][0]
    if (post["start"], post["end_exclusive"], post["upstream_module"], post["upstream_function"]) != (
        0x005E0002, 0x005E0068, "ttpost.c", "load_post_names"
    ):
        raise MapError("authenticated ttpost wrapper identity drift")
    post_ghidra = ghidra_rows.get(post["start"])
    if post_ghidra is None or post_ghidra["body_sha256"] != post["sha256"]:
        raise MapError("authenticated ttpost wrapper/Ghidra drift")
    medium.append(_record(
        image, "load_post_names", "ttpost.c", post["start"], post["end_exclusive"], "medium",
        ["batch10-semantic-signature", "ttpost-source-order", "pinned-ghidra-call-graph"],
        "ghidra-body",
    ))

    private_positions = []
    for symbol, start, required_callees in TTSBIT_PRIVATE:
        matches = list(re.finditer(rf"(?m)^  {re.escape(symbol)}\s*\(", source_text["ttsbit.c"]))
        if not matches:
            raise MapError(f"ttsbit.c:{symbol}: definition missing")
        # load_image has an earlier forward declaration; the last occurrence
        # is the implementation participating in single-object source order.
        private_positions.append(matches[-1].start())
        ghidra = ghidra_rows.get(start)
        if ghidra is None:
            raise MapError(f"{symbol}: Ghidra row missing")
        actual_callees = {int(value, 16) for value in ghidra["callees"]}
        if not set(required_callees).issubset(actual_callees):
            raise MapError(f"{symbol}: Ghidra call evidence drift")
        end = int(ghidra["body_end_inclusive"], 16) + 1
        if ghidra["body_sha256"] != _sha(_slice(image, start, end)):
            raise MapError(f"{symbol}: Ghidra/image body hash mismatch")
        medium.append(_record(
            image, symbol, "ttsbit.c", start, end, "medium",
            ["ttsbit-source-order", "pinned-ghidra-body", "pinned-ghidra-call-graph"],
            "ghidra-body",
        ))
    if private_positions != sorted(private_positions):
        raise MapError("ttsbit private source order drift")
    public = ghidra_rows[0x005E14A4]
    if not {0x005E072A, 0x005E0816, 0x005E0EB4, 0x005E12C8}.issubset({int(x, 16) for x in public["callees"]}):
        raise MapError("public sbit loader/private call graph drift")

    # Four complete callable records are recovered from stock pointer/call
    # anchors that the harvested Ghidra function relation omitted.
    source_order_groups = (
        ("ttbdf.c", ("tt_face_load_bdf_props", "tt_face_find_bdf_prop")),
        ("ttcmap.c", ("tt_cmap_init", "tt_cmap0_validate")),
        ("ttsbit.c", ("tt_sbit_decoder_load_byte_aligned", "tt_sbit_decoder_load_bit_aligned", "tt_sbit_decoder_load_compound")),
    )
    for module, symbols in source_order_groups:
        positions = []
        for symbol in symbols:
            matches = list(re.finditer(rf"(?m)^  {re.escape(symbol)}\s*\(", source_text[module]))
            if not matches:
                raise MapError(f"{module}:{symbol}: definition missing")
            positions.append(matches[-1].start())
        if positions != sorted(positions):
            raise MapError(f"{module}: recovered source order drift")

    if _thumb_bl_target(image, 0x005DC3E4) != 0x005DC290:
        raise MapError("BDF find-to-load direct call edge drift")
    if _u32(image, 0x0078E6B8) != 0x005DC3C5:
        raise MapError("BDF property stock service pointer drift")
    cmap_refs = (0x0072DD78, 0x0072DDAC, 0x0072DE14, 0x0072DE48, 0x0072DE7C)
    if any(_u32(image, ref) != 0x005DC53D for ref in cmap_refs):
        raise MapError("shared tt_cmap_init class pointers drift")
    if struct.unpack("<3I", _slice(image, 0x005E1484, 0x005E1490)) != (
        0x005E093B, 0x005E0A71, 0x005E0C49
    ):
        raise MapError("sbit loader callback table drift")

    for symbol, module, start, end, signature, digest, anchor in RECOVERED_HIGH:
        if start in ghidra_rows:
            raise MapError(f"{symbol}: expected omitted Ghidra row is now present")
        body = _slice(image, start, end)
        if _sha(body) != digest:
            raise MapError(f"{symbol}: recovered body boundary/hash drift")
        evidence = [
            "exact-freetype-2.9.1-source-order",
            "complete-thumb-body-boundary",
            anchor,
        ]
        record = _record(
            image, symbol, module, start, end, "high", evidence,
            "recovered-callable-body",
        )
        record["source_signature"] = signature
        record["mapping_origin"] = "recovered-after-initial-sfnt-map"
        high.append(record)
        high_starts.add(start)

    # Resolve the complete pointer-referenced callback frontier.  A row is
    # admitted only when the stock pointer, exact 2.9.1 source definition,
    # source table slot type (for cmap classes), full body bounds, and full
    # body hash all agree.  None of these entries exists in the harvested
    # Ghidra function relation, so the independent stock pointer is essential.
    callback_positions = []
    pointer_ledger = []
    callback_targets = []
    digest_groups: dict[str, list[str]] = {}
    for (
        symbol, module, start, end, signature, digest, table_kind,
        table_base, slot, slot_name, reference,
    ) in TABLE_CALLBACKS:
        if start in high_starts or start in ghidra_rows:
            raise MapError(f"{symbol}: callback frontier entry overlap/drift")
        matches = list(re.finditer(rf"(?m)^  {re.escape(symbol)}\s*\(", source_text[module]))
        if not matches:
            raise MapError(f"{module}:{symbol}: callback definition missing")
        if module == "ttcmap.c":
            callback_positions.append((start, matches[-1].start()))
        body = _slice(image, start, end)
        if _sha(body) != digest:
            raise MapError(f"{symbol}: callback body boundary/hash drift")
        if _u32(image, reference) != start | 1:
            raise MapError(f"{symbol}: stock callback pointer drift")

        evidence = [
            "stock-table-or-function-pointer",
            "exact-freetype-2.9.1-definition",
            "exact-freetype-2.9.1-source-order",
            "complete-thumb-body-boundary",
            "whole-body-sha256",
        ]
        if table_kind.startswith("cmap-format-"):
            cmap_format = int(table_kind.removeprefix("cmap-format-"))
            if reference != table_base + slot * 4 or _u32(image, table_base + 40) != cmap_format:
                raise MapError(f"{symbol}: cmap class layout/format drift")
            class_name = f"tt_cmap{cmap_format}_class_rec"
            block_start = source_text["ttcmap.c"].find(
                "FT_DEFINE_TT_CMAP(",
                source_text["ttcmap.c"].find(class_name) - 32,
            )
            block_end = source_text["ttcmap.c"].find("\n  )", block_start)
            if block_start < 0 or block_end < 0:
                raise MapError(f"{class_name}: source initializer missing")
            initializer = source_text["ttcmap.c"][block_start:block_end]
            cast = CMAP_SLOT_CASTS[slot]
            if re.search(rf"\({re.escape(cast)}\)\s*{re.escape(symbol)}\b", initializer) is None:
                raise MapError(f"{symbol}: FreeType cmap slot type drift")
            evidence.extend(("stock-cmap-class-slot", "freetype-2.9.1-cmap-slot-type"))
        elif table_kind == "sfnt-bdf-service":
            if re.search(
                rf"\(FT_BDF_GetCharsetIdFunc\)\s*{re.escape(symbol)}\b",
                source_text["sfdriver.c"],
            ) is None:
                raise MapError("SFNT BDF source service slot drift")
            evidence.append("stock-sfnt-bdf-service-slot")
        elif table_kind == "tt-cmap-info-service":
            if re.search(
                rf"\(TT_CMap_Info_GetFunc\)\s*{re.escape(symbol)}\b",
                source_text["sfdriver.c"],
            ) is None:
                raise MapError("TT cmap-info source service slot drift")
            evidence.append("stock-tt-cmap-info-service-slot")
        else:
            evidence.append("stock-woff-function-literal")

        record = _record(
            image, symbol, module, start, end, "high", evidence,
            "recovered-table-callback-body",
        )
        record.update({
            "source_signature": signature,
            "mapping_origin": "resolved-pointer-referenced-sfnt-frontier",
            "table_kind": table_kind,
            "table_base": f"0x{table_base:08X}",
            "table_slot": slot,
            "table_slot_name": slot_name,
            "pointer_reference": f"0x{reference:08X}",
            "thumb_pointer": f"0x{start | 1:08X}",
        })
        high.append(record)
        high_starts.add(start)
        callback_targets.append(start)
        digest_groups.setdefault(digest, []).append(symbol)
        pointer_ledger.append({
            "reference": f"0x{reference:08X}",
            "target": f"0x{start:08X}",
            "symbol": symbol,
            "body_start": f"0x{start:08X}",
            "body_end_exclusive": f"0x{end:08X}",
            "body_bytes": end - start,
            "body_sha256": digest,
            "table_kind": table_kind,
            "table_slot": slot,
            "table_slot_name": slot_name,
            "resolution": "high",
        })

    if [position for _, position in sorted(callback_positions)] != sorted(
        position for _, position in callback_positions
    ):
        raise MapError("recovered ttcmap callback source/address order drift")
    if (len(callback_targets), len(set(callback_targets)), sum(row[3] - row[2] for row in TABLE_CALLBACKS)) != (
        38, 38, 2_374
    ):
        raise MapError("table callback target/byte accounting drift")
    pointer_alias_groups: list[dict[str, Any]] = []
    identical_body_groups = [
        {"body_sha256": digest, "symbols": symbols, "pointer_alias": False}
        for digest, symbols in sorted(digest_groups.items())
        if len(symbols) > 1
    ]
    if identical_body_groups != [{
        "body_sha256": "794ad98f7ef960f9da7c1648e89e44db96c22dfbcd4b3d36bf6e713537f38b4b",
        "symbols": ["tt_cmap12_init", "tt_cmap13_init"],
        "pointer_alias": False,
    }]:
        raise MapError("identical callback body grouping drift")

    private_helper_ledger = []
    for (
        symbol, start, end, digest, wrapper_calls, internal_call,
        internal_target, marker_start, marker_end, marker_hex,
    ) in PRIVATE_CMAP_HELPERS:
        if start in high_starts or start in ghidra_rows:
            raise MapError(f"{symbol}: private cmap helper overlap/drift")
        body = _slice(image, start, end)
        if _sha(body) != digest:
            raise MapError(f"{symbol}: private cmap helper body hash drift")
        if body[:4] != bytes.fromhex("2de9f047") or body[-4:] != bytes.fromhex("bde8f087"):
            raise MapError(f"{symbol}: private cmap helper entry/return boundary drift")
        if any(_thumb_bl_target(image, call) != start for call in wrapper_calls):
            raise MapError(f"{symbol}: public wrapper call edge drift")
        if _thumb_bl_target(image, internal_call) != internal_target:
            raise MapError(f"{symbol}: private next-helper call edge drift")
        if _slice(image, marker_start, marker_end) != bytes.fromhex(marker_hex):
            raise MapError(f"{symbol}: format-specific Thumb semantic marker drift")
        # char_index passes next=0 and a stack char-code pointer; char_next's
        # fallback passes next=1 and its caller-owned pointer.
        first_call, second_call = wrapper_calls
        if _slice(image, first_call - 4, first_call) != bytes.fromhex("00226946"):
            raise MapError(f"{symbol}: char_index argument setup drift")
        if _slice(image, second_call - 4, second_call) != bytes.fromhex("01222100"):
            raise MapError(f"{symbol}: char_next argument setup drift")

        definition = list(re.finditer(rf"(?m)^  {re.escape(symbol)}\s*\(", source_text["ttcmap.c"]))
        if len(definition) != 1:
            raise MapError(f"ttcmap.c:{symbol}: private definition drift")
        format_number = 12 if "cmap12" in symbol else 13
        source_neighbors = (
            f"tt_cmap{format_number}_next", symbol,
            f"tt_cmap{format_number}_char_index", f"tt_cmap{format_number}_char_next",
        )
        source_positions = []
        for neighbor in source_neighbors:
            matches = list(re.finditer(rf"(?m)^  {re.escape(neighbor)}\s*\(", source_text["ttcmap.c"]))
            if not matches:
                raise MapError(f"ttcmap.c:{neighbor}: source-order anchor missing")
            source_positions.append(matches[-1].start())
        if source_positions != sorted(source_positions):
            raise MapError(f"{symbol}: source-order neighborhood drift")

        semantics = {
            "group_record_bytes": 12,
            "num_groups_offset": 12,
            "groups_offset": 16,
            "big_endian_group_fields": True,
            "binary_search": True,
            "next_state_offsets": [24, 28, 32, 36],
            "glyph_mapping": (
                "start_id_plus_character_delta_with_overflow_rejection"
                if format_number == 12 else "constant_group_glyph_id"
            ),
        }
        evidence = [
            "two-decoded-public-wrapper-bl-edges",
            "decoded-private-next-helper-bl-edge",
            "complete-thumb-prologue-to-pop-pc-boundary",
            "whole-body-sha256",
            "exact-freetype-2.9.1-source-neighborhood",
            "reviewed-thumb-binary-search-semantics",
            "format-specific-glyph-mapping-marker",
        ]
        record = _record(
            image, symbol, "ttcmap.c", start, end, "high", evidence,
            "recovered-private-cmap-helper-body",
        )
        record.update({
            "source_signature": "FT_UInt ( TT_CMap cmap, FT_UInt32* pchar_code, FT_Bool next )",
            "mapping_origin": "resolved-private-cmap-binary-helper",
            "direct_callers": [f"0x{call:08X}" for call in wrapper_calls],
            "private_next_call": f"0x{internal_call:08X}",
            "private_next_target": f"0x{internal_target:08X}",
            "semantic_comparison": semantics,
        })
        high.append(record)
        high_starts.add(start)
        private_helper_ledger.append({
            "symbol": symbol,
            "start": f"0x{start:08X}",
            "end_exclusive": f"0x{end:08X}",
            "bytes": end - start,
            "body_sha256": digest,
            "wrapper_call_sites": [f"0x{call:08X}" for call in wrapper_calls],
            "internal_next_call_site": f"0x{internal_call:08X}",
            "internal_next_target": f"0x{internal_target:08X}",
            "semantic_comparison": semantics,
            "resolution": "high",
        })

    if (len(private_helper_ledger), sum(row["bytes"] for row in private_helper_ledger)) != (2, 604):
        raise MapError("private cmap helper accounting drift")

    high.sort(key=lambda row: int(row["start"], 16))
    medium.sort(key=lambda row: int(row["start"], 16))
    if (len(high), sum(row["bytes"] for row in high)) != (75, 13_164):
        raise MapError("high-confidence SFNT accounting drift")
    if (len(medium), sum(row["bytes"] for row in medium)) != (61, 16_094):
        raise MapError("medium-confidence SFNT accounting drift")

    mapped = high + medium
    mapped_starts = {int(row["start"], 16) for row in mapped}
    if len(mapped_starts) != len(mapped):
        raise MapError("duplicate mapped function entry")
    ghidra_scope = {
        entry: row for entry, row in ghidra_rows.items()
        if ENVELOPE[0] <= entry < ENVELOPE[1]
    }
    if (len(ghidra_scope), sum(row["body_bytes"] for row in ghidra_scope.values())) != (75, 21_238):
        raise MapError("SFNT-envelope Ghidra census drift")
    if set(ghidra_scope) - mapped_starts:
        raise MapError("recognized SFNT-envelope Ghidra function left unresolved")

    mapped_intervals = [
        (int(row["start"], 16), int(row["end_exclusive"], 16))
        for row in mapped
    ]
    residual_pairs = _complement(mapped_intervals, *ENVELOPE)
    physical = []
    compressed_physical: list[list[int]] = []
    category_bytes: dict[str, int] = {}
    for start, end, category, evidence, pointer_records in PHYSICAL_SPECS:
        if compressed_physical and start < compressed_physical[-1][1]:
            raise MapError("physical classification intervals overlap")
        if not compressed_physical or start > compressed_physical[-1][1]:
            compressed_physical.append([start, end])
        else:
            compressed_physical[-1][1] = end
        for target, reference in pointer_records:
            target_in_interval = start <= target < end
            if (category == "unresolved-callable-code" and not target_in_interval) or _u32(image, reference) != target | 1:
                raise MapError(f"0x{target:08X}: physical pointer evidence drift")
            if category == "unresolved-callable-code":
                raise MapError("unresolved private code must not claim a table pointer")
        body = _slice(image, start, end)
        if category == "alignment-padding" and body != bytes(len(body)):
            raise MapError(f"0x{start:08X}: nonzero alignment classification")
        category_bytes[category] = category_bytes.get(category, 0) + len(body)
        physical.append({
            "start": f"0x{start:08X}",
            "end_exclusive": f"0x{end:08X}",
            "bytes": len(body),
            "body_sha256": _sha(body),
            "category": category,
            "evidence": evidence,
            "pointer_records": [
                {"target": f"0x{target:08X}", "reference": f"0x{reference:08X}"}
                for target, reference in pointer_records
            ],
            "source_identity_claimed": False,
        })
    if tuple(map(tuple, compressed_physical)) != tuple(residual_pairs):
        raise MapError("physical classifications do not partition mapped complement")
    expected_categories = {
        "literal-constant-pool": 328,
        "function-pointer-table": 12,
        "alignment-padding": 14,
    }
    if category_bytes != expected_categories:
        raise MapError("physical classification accounting drift")
    if (len(physical), sum(row["bytes"] for row in physical)) != (18, 354):
        raise MapError("physical residual accounting drift")
    formerly_unparsed = {
        "bytes": 3_274,
        "recovered_table_callback_code": 2_374,
        "recovered_private_helper_code": 604,
        "literal_constant_pool": 272,
        "function_pointer_table": 12,
        "alignment_padding": 12,
        "unclassified": 0,
    }
    if sum(value for key, value in formerly_unparsed.items() if key not in {"bytes", "unclassified"}) != formerly_unparsed["bytes"]:
        raise MapError("former physical residue classification drift")

    # Direct-callback counts provide a second, stock-image-authenticated
    # tie-breaker for candidates not represented in the closed census.
    autofit_words = struct.unpack("<9I", _slice(image, 0x00752520, 0x00752520 + 36))
    if autofit_words[6:9] != (0x005AB997, 0x005AB9D5, 0x005AB98D):
        raise MapError("autofit class anchor drift")
    smooth_callbacks = set()
    for address, render in ((0x00718D9C, 0x005E2649), (0x00718DD8, 0x005E2661), (0x00718E14, 0x005E266F)):
        words = struct.unpack("<15I", _slice(image, address, address + 60))
        if words[6] != 0x005E225D or words[9] != 0x6F75746C or words[10] != render or words[11:14] != (0x005E2283, 0x005E22B9, 0x005E2273):
            raise MapError("smooth renderer class anchor drift")
        smooth_callbacks.update((words[6], words[10], words[11], words[12], words[13]))
    if len(smooth_callbacks) != 7:
        raise MapError("smooth direct callback count drift")

    exact = {"functions": 0, "bytes": 0, "reason": "no compiler-byte identity proof"}
    high_total = {"functions": len(high), "bytes": sum(row["bytes"] for row in high)}
    medium_total = {"functions": len(medium), "bytes": sum(row["bytes"] for row in medium)}
    unresolved_total = {"functions": 0, "bytes": 0}
    unresolved_code = {
        "pointer_referenced_entries": 0,
        "private_helper_envelopes": 0,
        "envelope_bytes": 0,
        "source_identities_complete": True,
    }
    mapping_sha = _sha(json.dumps(high + medium + physical, sort_keys=True, separators=(",", ":")).encode())
    return {
        "status": "fail-closed-sfnt-function-map",
        "read_only": True,
        "hardware_operations": False,
        "production_routed": False,
        "binary_overlay_ready": False,
        "compiler_byte_identity_claimed": False,
        "selected_module": "sfnt",
        "selection": {
            "method": "largest authenticated closed-census source attribution; stock direct callbacks are a tie-breaker",
            "candidates": [
                {"module": "sfnt", "source_backed_functions": 61, "source_backed_bytes": 16_520, "direct_callback_slots": 31},
                {"module": "psaux", "source_backed_functions": 57, "source_backed_bytes": 7_114, "direct_callback_slots": None},
                {"module": "smooth", "source_backed_functions": 0, "source_backed_bytes": 0, "direct_callback_slots": 7},
                {"module": "autofit", "source_backed_functions": 0, "source_backed_bytes": 0, "direct_callback_slots": 3},
            ],
        },
        "anchors": {
            "image": {"path": str(IMAGE.relative_to(G2)), "bytes": IMAGE_PIN[0], "sha256": IMAGE_PIN[1], "load_base": f"0x{LOAD_BASE:08X}"},
            "ghidra": {"path": str(GHIDRA.relative_to(G2)), "bytes": GHIDRA_PIN[0], "sha256": GHIDRA_PIN[1]},
            "module_class": f"0x{MODULE_CLASS:08X}",
            "module_name": "sfnt",
            "module_name_address": f"0x{MODULE_NAME:08X}",
            "interface_table": f"0x{INTERFACE_TABLE:08X}",
            "interface_slots": 31,
            "freetype_version": "2.9.1",
            "freetype_tag": "VER-2-9-1",
            "freetype_commit": "86bc8a95056c97a810986434a3f268cbe67f2902",
        },
        "scope": {
            "start": f"0x{ENVELOPE[0]:08X}",
            "end_exclusive": f"0x{ENVELOPE[1]:08X}",
            "bytes": ENVELOPE[1] - ENVELOPE[0],
            "ghidra_recognized": {"functions": len(ghidra_scope), "bytes": sum(row["body_bytes"] for row in ghidra_scope.values()), "unmapped_functions": 0},
            "residual_physical": {
                "intervals": len(residual_pairs),
                "classification_records": len(physical),
                "bytes": sum(row["bytes"] for row in physical),
                "category_bytes": category_bytes,
                "unclassified_bytes": 0,
                "formerly_unparsed_3274": formerly_unparsed,
            },
        },
        "confidence": {
            "exact": exact,
            "high": high_total,
            "medium": medium_total,
            "unresolved_known_candidates": unresolved_total,
            "unresolved_code": unresolved_code,
            "mapped_total": {"functions": len(mapped), "bytes": sum(row["bytes"] for row in mapped)},
        },
        "movement": {
            "new_beyond_closed_census": {"functions": 75, "bytes": 12_738},
            "resolved_table_pointer_frontier": {"functions": 38, "bytes": 2_374},
            "resolved_private_cmap_helpers": {"functions": 2, "bytes": 604},
            "initial_high_table_callbacks": {"functions": 21, "bytes": 5_638},
            "new_medium_private_or_outside_census": {"functions": 10, "bytes": 3_018},
            "retained_census_promoted_to_high": {"functions": 10, "bytes": 3_444},
            "retained_census_medium": {"functions": 51, "bytes": 13_076},
            "recovered_named_candidates": {"functions": 3, "bytes": 1_098},
            "recovered_adjacent_cmap_callback": {"functions": 1, "bytes": 6},
            "remaining_known_unresolved": unresolved_total,
        },
        "table_pointer_resolution": {
            "input_pointer_records": len(pointer_ledger),
            "distinct_targets": len(set(callback_targets)),
            "alias_pointer_records": len(pointer_ledger) - len(set(callback_targets)),
            "resolved_high": {"functions": len(pointer_ledger), "bytes": sum(row["body_bytes"] for row in pointer_ledger)},
            "unresolved": {"functions": 0, "bytes": 0},
            "pointer_alias_groups": pointer_alias_groups,
            "identical_body_groups": identical_body_groups,
            "shared_callback_aliases_outside_frontier": [{
                "symbol": "tt_cmap_init",
                "target": "0x005DC53C",
                "references": [f"0x{ref:08X}" for ref in cmap_refs],
                "pointer_records": len(cmap_refs),
                "note": "one previously mapped callback shared by five cmap class init slots",
            }],
            "records": pointer_ledger,
        },
        "private_helper_resolution": {
            "input_candidates": 2,
            "resolved_high": {"functions": 2, "bytes": 604},
            "unresolved": {"functions": 0, "bytes": 0},
            "records": private_helper_ledger,
        },
        "mapping_sha256": mapping_sha,
        "records": {"high": high, "medium": medium, "physical_classification": physical},
        "source_pins": {
            name: {"bytes": pin[0], "sha256": pin[1]}
            for name, pin in SOURCE_PINS.items()
        },
        "blockers": [
            "original compiler/version/options, product macros, ABI details, and LTO state are not recovered",
            "no authenticated stock callsite rewrite or overlay placement manifest routes this map",
            "no live hardware execution was performed",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run_audit(), indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
