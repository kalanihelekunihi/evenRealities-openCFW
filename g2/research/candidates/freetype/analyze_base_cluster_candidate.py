#!/usr/bin/env python3
"""Authenticate the next FreeType base-module source-admission tranche.

SPDX-License-Identifier: MIT

This read-only analyzer narrows the existing 83-function/7,874-byte base
community.  It admits the 17 direct-call-graph rows only where an official
image span, a distinctive decompiler shape, and a hash-authenticated FreeType
2.9.1 definition agree.  It separately classifies the seven-function Mac
resource loader chain: those bodies are upstream mechanics outside the
83-row census; only the caller's fallback policy remains an integration
choice.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


G2 = Path(__file__).resolve().parents[3]
ROOT = G2.parent
SNAPSHOT = G2 / "third_party/freetype"
PROVENANCE = SNAPSHOT / "PROVENANCE.json"
IMAGE = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
CENSUS = G2 / "tools/manifests/g2-freetype-engine-census.tsv"
DECOMP = G2 / "research/corpus/apollo-main/ghidra/decomp/bundles"
LOAD_BASE = 0x00437FE0
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"


class AdmissionError(RuntimeError):
    pass


# entry: (size, sha256, upstream symbol, source, distinctive decompiler pins)
DIRECT_SOURCE = {
    0x0052502A: (34, "cdaf0ebc791b6fd86856c53ad3a2f19133904792dd2d86bd93b052e581fdc395", "FT_Stream_Free", "src/base/ftobjs.c", ("FUN_005288ce", "FUN_00529256", "+ 0x1c")),
    0x00525386: (110, "93dc63300cafb48fa0474b90ce471392fcfc317ccabba46a13f0d72e00fd6c20", "FT_New_GlyphSlot", "src/base/ftobjs.c", ("FUN_0052504c", "FUN_00525334", "+ 0x54")),
    0x005253F4: (80, "4a43d7539153ccf4bf9fc97736669b7f4e718433128f0f3f5c6a299dc466c0c6", "FT_Done_GlyphSlot", "src/base/ftobjs.c", ("FUN_00525334", "FUN_00529256", "+ 0x14")),
    0x0052586E: (58, "6fe948cdc825a413d8332d94ff9f9e07c32861ef2a66533549af0b6af89ead14", "destroy_charmaps", "src/base/ftobjs.c", ("FUN_00526e38", "+ 0x24", "+ 0x28")),
    0x0052594A: (116, "fd0dcfcd0d71963c3b95f747787d4fc3997c2f0850c5173fff391962856cd7d8", "find_unicode_charmap", "src/base/ftobjs.c", ("DAT_005262a4", "+ 0x5c", "+ 0x24")),
    0x00525ADE: (36, "8833a4662f2f92465d2e2829b621c8d0903d495c0f4d636f49fe4d65cce26db4", "FT_New_Memory_Face", "src/base/ftobjs.c", ("local_2c[0] = 4", "FUN_005264a6")),
    0x00525B6E: (154, "34aff3bfdf050dd604750d4b08d5274590d30dbb7a238ce4dbb3c0dc315c4355", "open_face_from_buffer", "src/base/ftobjs.c", ("FUN_00525b20", "FUN_005264a6", "0xfffffbff")),
    0x0052687E: (198, "9a540f53540768a926e65ad6d90f3401554a250f33011f163e01948fbd0388dd", "FT_New_Size", "src/base/ftobjs.c", ("FUN_00529304", "+ 0x6c", "+ 0x38")),
    0x005270D2: (154, "d7d8a82822821970301f3f4e40f2429178904ff85d71cfd837e549d424fe0af2", "ft_add_renderer", "src/base/ftobjs.c", ("FUN_00529304", "+ 0x25", "DAT_00527500")),
    0x00527466: (76, "2385ace46863930fad43257decc4f2116c6f87685d42d8ef1296819f674121b8", "FT_Remove_Module", "src/base/ftobjs.c", ("FUN_0052724c", "+ 0x14", "+ 0x10")),
    0x005288E0: (52, "93f13c86f4e60aec61415a43150a112c7e1fb44b6c8cdc4333530dc3d70aae8f", "FT_Stream_Seek", "src/base/ftstream.c", ("+ 0x14", "+ 8", "0x55")),
    0x00529148: (46, "b8cbad1dd23bba5db3469c66ee6aff6c225e8c6db18228f33f25fcd99cf63d52", "ft_mem_alloc", "src/base/ftutil.c", ("FUN_00529176", "FUN_0043c0e4")),
    0x00529256: (12, "91bfa7a2a63e084067d8a3221f52e3a51cce08e7dc7df4ab11cf3ba0614cb8ca", "ft_mem_free", "src/base/ftutil.c", ("param_1 + 8", "param_2 != 0")),
    0x005292E6: (30, "c6cc7217bbc0070bee7acaaebbdee0d1aea7282dc5ffc5fa36be1bbfa73fa4d5", "FT_List_Find", "src/base/ftutil.c", ("param_1", "iVar1 + 4", "iVar1 + 8")),
    0x00529304: (32, "f72fa6e2fb4dc828a6e058533a67dc668d3953f9a31b76ae86ca7edb2b45f051", "FT_List_Add", "src/base/ftutil.c", ("param_1[1]", "param_2[1]")),
    0x00529324: (36, "8b44b259cba1b73a77fb75f1534d4ccd08500d852eb02e7e94cc6220680be00a", "FT_List_Remove", "src/base/ftutil.c", ("*param_1", "param_1[1]", "param_2[1]")),
    0x00529378: (70, "e2b2335fc6559739d766441e8fcfd245769c47a19c6a80e98071ab6abfa498a1", "FT_List_Finalize", "src/base/ftutil.c", ("param_2", "FUN_00529256", "param_1[1] = 0")),
}

# A second source-identification tier for low-confidence community rows whose
# complete bounded semantics are standard upstream stream/memory operations.
# They remain distinct from the direct-call tranche so the inherited evidence
# tier is never silently promoted.
INDIRECT_SOURCE = {
    0x00524B88: (32, "4fb665df07e7148ae08655aa152f79b30c70a54a2fa97f469afdc9948216aea3", "FT_GlyphLoader_New", "src/base/ftgloadr.c", ("FUN_00529148", "0x60", "*param_2")),
    0x00524BA8: (28, "76e629f036c99f2c93010b8fa866abf78458c278fce1003e900db23cb7351fd3", "FT_GlyphLoader_Rewind", "src/base/ftgloadr.c", ("param_1 + 0x16", "param_1 + 0x30", "FUN_00439c04")),
    0x00524BC4: (90, "8453ebd12bb74be761c6a6e6d21003f57cb6a8cd6782894f0f4b9e63f2a62981", "FT_GlyphLoader_Reset", "src/base/ftgloadr.c", ("FUN_00529256", "param_1[0xd]", "FUN_00524ba8")),
    0x00524C1E: (28, "b15046c2bc1abe815e36680183c2bfec330c87b1aeeb53076ccdb2a56edd31a8", "FT_GlyphLoader_Done", "src/base/ftgloadr.c", ("FUN_00524bc4", "FUN_00529256")),
    0x00524C3A: (78, "c532fa985e3f2db81a07172c27f6ee83b23dd12f9a7c1e0c4c8fb774e3aec32c", "FT_GlyphLoader_Adjust_Points", "src/base/ftgloadr.c", ("param_1 + 0x3c", "param_1 + 0x44", "param_1 + 0x50")),
    0x00524C88: (60, "e28044509b79f3fd8f97bc862bfe98b102e4f89daf2c08125ad4aecd5947caf3", "FT_GlyphLoader_CreateExtra", "src/base/ftgloadr.c", ("FUN_0052919c", "param_1[0xb]", "FUN_00524c3a")),
    0x00524CC4: (18, "8cc6957226499bb1718773567a6ddac71c7636892c7c1de4a546106e30465246", "FT_GlyphLoader_Adjust_Subglyphs", "src/base/ftgloadr.c", ("param_1 + 0x58", "param_1 + 0x30")),
    0x00524CD6: (306, "61d353006de5c6be7fcf260bb5fabc8bab71bad109ac79d9f96d4ad17a926f8c", "FT_GlyphLoader_CheckPoints", "src/base/ftgloadr.c", ("FUN_0052919c", "FUN_00524c3a", "FUN_00524bc4")),
    0x00524E08: (80, "2557e0e600a3cd491a0b877cac8febfbf14bb5622b3369d787c63b197c61c1c6", "FT_GlyphLoader_CheckSubGlyphs", "src/base/ftgloadr.c", ("FUN_0052919c", "0x20", "FUN_00524cc4")),
    0x00524E58: (34, "c0b4ec07f151b6a308d2ad8a7e7940ade2d60b7d1880a442ec2e690233ba40f5", "FT_GlyphLoader_Prepare", "src/base/ftgloadr.c", ("param_1 + 0x3a", "FUN_00524c3a", "FUN_00524cc4")),
    0x00524E7A: (76, "d4c084e3c0d06a838b9793c863d33e0efcd16f45823b0c7c064295b5d03dda8e", "FT_GlyphLoader_Add", "src/base/ftgloadr.c", ("param_1 + 0x38", "param_1 + 0x30", "FUN_00524e58")),
    0x0052504C: (86, "5cb7cc43e9d48a5b6b54af989f8a24e6f919e54d1ef84b38e015df21da25399b", "ft_glyphslot_init", "src/base/ftobjs.c", ("FUN_00529148", "FUN_00524b88", "+ 0x40")),
    0x005250A2: (60, "8bffeb23c23b6a2ae0d5fe09e6de7d9b6c8793d2ae5dae76011990ed12e4f464", "ft_glyphslot_free_bitmap", "src/base/ftobjs.c", ("param_1 + 0x9c", "FUN_00529256", "0xfffffffe")),
    0x0052525C: (16, "0caf54a49219e763a6d818bc01e170bb164016bc61dd83fec8af1d502ba493c1", "ft_glyphslot_set_bitmap", "src/base/ftobjs.c", ("FUN_005250a2", "param_1 + 0x58")),
    0x0052526C: (80, "d823cec44dd18e470b66468562486606e56c5fffd3d459c8d61d787816464351", "ft_glyphslot_alloc_bitmap", "src/base/ftobjs.c", ("FUN_00529256", "FUN_00529148", "param_1 + 0x58")),
    0x005252BC: (120, "6b424c7df1e6d0037b3df2944fafb69b3e8cee7bc25ea9d1a9a8f27d8f1aed34", "ft_glyphslot_clear", "src/base/ftobjs.c", ("FUN_005250a2", "param_1 + 0x18", "param_1 + 0x6c")),
    0x00525334: (82, "27db35a356f664ce6f360d37d088b9047b808817eb47aacf3e137405a0b5d983", "ft_glyphslot_done", "src/base/ftobjs.c", ("FUN_005250a2", "FUN_00524c1e", "FUN_00529256")),
    0x00525832: (60, "04dc31f341f8753abf0d64a487b8829c4a2c12a0b032119cd21056840b2e2149", "destroy_size", "src/base/ftobjs.c", ("param_2 + 8", "param_3 + 0xc", "FUN_00529256")),
    0x00525936: (20, "0e4021b8728230f834bc3a03d773edb42f0b64bd6461fd5644b614d7b782832b", "Destroy_Driver", "src/base/ftobjs.c", ("FUN_00529378", "DAT_005262a0", "param_1 + 0x10")),
    0x00525B02: (30, "764e0efbc583a387c8c2d974a3314be8a4b7cf981fc665cf1248b69394e956f8", "memory_stream_close", "src/base/ftobjs.c", ("FUN_00529256", "param_1[7]", "param_1[6] = 0")),
    0x00525B20: (78, "e97488fe336d71ac5691b72cd5c728d5c58ce2f67be217c895d3d70f936234dd", "new_memory_stream", "src/base/ftobjs.c", ("FUN_00529148", "0x28", "FUN_005288b8")),
    0x00525C08: (298, "a7d18313fd9d5be2b661922bb6e06f3b3a215d5c65d26093183cbe89ee2da87d", "ft_lookup_PS_in_sfnt_stream", "src/base/ftobjs.c", ("FUN_00528ba8", "FUN_00528b4a", "0x8e")),
    0x00526DA2: (76, "fd9e5e4901d85371fae6b3949099774cd83200f236dfe23fe0f385c7f36ddcd1", "FT_Select_Charmap", "src/base/ftobjs.c", ("DAT_005273b4", "FUN_0052594a", "param_1 + 0x5c")),
    0x00526E38: (34, "ce637b530b2e43e73c3da4e1c8db6dcf883a78c6ca1d25e6c9c457a8856f67b4", "ft_cmap_done_internal", "src/base/ftobjs.c", ("param_1[3] + 8", "FUN_00529256", "*param_1 + 100")),
    0x00526E5A: (182, "8479a7a565fb9a5605ebe68d968f470f6f3ee6faf41b98ffdbd83402bc37d539", "FT_CMap_New", "src/base/ftobjs.c", ("FUN_00529148", "FUN_0052919c", "FUN_00526e38")),
    0x0052705A: (60, "a85df35a4fb3c96d228233a5420dad4ae825b032af5880fed2e2877c783db150", "FT_Lookup_Renderer", "src/base/ftobjs.c", ("param_1 + 0x94", "param_3", "iVar1 + 8")),
    0x00527096: (38, "b8e682322ff1b54294378607106178c50232ec813315e8a15881c09b4e6aeef4", "ft_lookup_glyph_renderer", "src/base/ftobjs.c", ("FUN_0052705a", "param_1 + 0x48", "iVar2 + 0x9c")),
    0x005270BC: (22, "6c8018e86f2a4907e751f6dfdc6e5bcee5ed74acf8f7df162787979dfdbbc566", "ft_set_current_renderer", "src/base/ftobjs.c", ("FUN_0052705a", "DAT_00527500", "param_1 + 0x9c")),
    0x0052716C: (84, "97b96a68948d01de5edcd932c2edfe87dfca76a906172ae709ad3ad605286edc", "ft_remove_renderer", "src/base/ftobjs.c", ("FUN_005292e6", "FUN_00529324", "FUN_005270bc")),
    0x005271C0: (104, "81d8298b74bd97e14ff8af86b710ee88e13daf0b090cc9429899d61275baf39b", "FT_Render_Glyph_Internal", "src/base/ftobjs.c", ("FUN_0052705a", "+ 0x3c", "0x13")),
    0x00527228: (36, "3d30a3401cce41469fcbaadd58918e8d9d5afb6463d312baeb68ee227236fe6c", "FT_Render_Glyph", "src/base/ftobjs.c", ("param_1 + 4", "FUN_005271c0", "uVar1 = 6")),
    0x0052724C: (80, "e6eaec6231e5518e23806b1c9016c80422902eb541d91ea9501a8a5217c2f262", "Destroy_Module", "src/base/ftobjs.c", ("FUN_0052716c", "FUN_00525936", "FUN_00529256")),
    0x005273B8: (58, "8a0aa10123cc17d7329767818c00f022644aa038573e724888c476edb6d82713", "FT_Get_Module", "src/base/ftobjs.c", ("FUN_0046cacc", "param_1 + 0x14", "param_1 + 0x10")),
    0x005273F2: (20, "c249e9f907c3264861ccbd163f99c024101ccc5ebc68c630214fc8c91a5b5c75", "FT_Get_Module_Interface", "src/base/ftobjs.c", ("FUN_005273b8", "*piVar1 + 0x14", "uVar2 = 0")),
    0x00528470: (110, "4fb20ca911dcfd09cbfe41b11bda915a4adc58a8bda40516e32089fb634ec45c", "FT_Raccess_Guess", "src/base/ftrfork.c", ("iVar2 < 9", "FUN_005288e0", "DAT_00528714")),
    0x00528508: (28, "bef130cdecb72f7e8380af3ce7e71d90c5346a418d00e5d226fee4563f066a07", "raccess_guess_apple_double", "src/base/ftrfork.c", ("*param_4 = 0", "uVar1 = 0x51", "FUN_00528720")),
    0x00528524: (28, "0a5e7115320a95428e641d041b5c5045208c29ca76057d5319351995ce1d2fe5", "raccess_guess_apple_single", "src/base/ftrfork.c", ("*param_4 = 0", "uVar1 = 0x51", "FUN_00528720")),
    0x005285D4: (88, "66de7f8a3b3c3578eadaf2f9113ec6ac99a01572527df7c9f472a9c5623b447d", "raccess_guess_darwin_newvfs", "src/base/ftrfork.c", ("iVar1 + 0x12", "DAT_00528ed8", "FUN_00439be4")),
    0x0052862C: (36, "9f746d6a54419fa68a8cd488cba8108c31d8cf9a87346b7da5fae8af70f221d7", "raccess_guess_vfat", "src/base/ftrfork.c", ("FUN_00528842", "DAT_00528edc", "0x40")),
    0x00528720: (226, "e102bbf664f203dbfd256a8d856b36e775f3cf3eb8268595ed94a66abcd68801", "raccess_guess_apple_generic", "src/base/ftrfork.c", ("FUN_00528ba8", "FUN_00528914", "iVar4 == 2")),
    0x00528842: (118, "e5a7c369cb522205ffedab9dd325ecd6dcf8fb504005bf23a22dbabca539b8d8", "raccess_make_file_name", "src/base/ftrfork.c", ("FUN_00567c64", "FUN_00567c80", "FUN_0044b5a0")),
    0x005288B8: (22, "f46abd333cc4957ee3ee4042aa6f3c5aace088eab404b173a01c49cba07bc706", "FT_Stream_OpenMemory", "src/base/ftstream.c", ("param_1[1]", "param_1[2] = 0", "param_1[8] = 0")),
    0x005288CE: (18, "b49eb6596fdb9d689f810eceeaf6ce31e934c6b31ea2bdbd6e1703cdb742de87", "FT_Stream_Close", "src/base/ftstream.c", ("param_1 + 0x18", "param_1 != 0")),
    0x00528914: (20, "79a8778196c0cd152e25fc6abbb0e25c9bef7577f7d2863ea405c06c5a542972", "FT_Stream_Skip", "src/base/ftstream.c", ("param_2 < 0", "FUN_005288e0", "param_1 + 8")),
    0x00528992: (30, "4f1dc483b74c4bfd7376feffc370ad087e8dcbcb826485c4dd02e261dabb6170", "FT_Stream_ExtractFrame", "src/base/ftstream.c", ("FUN_005289d0", "+ 0x20", "+ 0x24")),
    0x005289B0: (32, "8ba0c53eaf5edd452b96a30613f77a9e8786bfb8cb3a970c7f2ec5c5d59b8c47", "FT_Stream_ReleaseFrame", "src/base/ftstream.c", ("FUN_00529256", "+ 0x1c", "*param_2 = 0")),
    0x005289D0: (150, "f7fd9b1b3562340ee287a351de311989653427f2a759c5703b71e6b51697a6b3", "FT_Stream_EnterFrame", "src/base/ftstream.c", ("FUN_00529176", "FUN_00529256", "param_1[8]")),
    0x00528A66: (32, "1834e348c3ae52b01c72c24c6a1db383821d5429c0db370e4b690ec1511c98dd", "FT_Stream_ExitFrame", "src/base/ftstream.c", ("FUN_00529256", "param_1[8] = 0", "param_1[9] = 0")),
    0x00528B4A: (94, "7b5360247a7fa77559df053a65f8522b298c40cbaf09a89f85f871787aaebe54", "FT_Stream_ReadUShort", "src/base/ftstream.c", ("puVar2", "param_1[2] + 2", "0x55")),
    0x00528BA8: (108, "d8eaa0dac5b3d107169fa2570eb516b828c34d8e268fa4256fcfec94337e7a63", "FT_Stream_ReadULong", "src/base/ftstream.c", ("pbVar2[3]", "param_1[2] + 4", "0x55")),
    0x00528C14: (420, "189c1664e251ec3ea10b389a481f1f5ffb50512389de6a319c3c9c11ae6e9c6d", "FT_Stream_ReadFields", "src/base/ftstream.c", ("param_2 + 4", "FUN_005289d0", "FUN_00528a66")),
    0x00529176: (38, "a83833f1537646e1b7af31be2924458b6f7478f328f4de0836b52603ec41fd08", "ft_mem_qalloc", "src/base/ftutil.c", ("param_1 + 4", "param_2 < 0", "0x40")),
    0x0052919C: (72, "ad1b0a5e68aecb96532b17fca443ce57f1a26ddf6d89f7f4f4830ff01c0df3f3", "ft_mem_realloc", "src/base/ftutil.c", ("FUN_005291e4", "FUN_0043c0e4", "param_3 < param_4")),
    0x005291E4: (114, "ca779e2ed7514edd14761ee541a89890f4dff96cca4759e240465ddb793eaf72", "ft_mem_qrealloc", "src/base/ftutil.c", ("FUN_00529256", "0x7fffffff", "param_1 + 0xc")),
    0x00529262: (52, "c06ebbe09ee3b95c76124baae07bb2a19021ee7d2263b2a16b8df085bfc2ea00", "ft_mem_dup", "src/base/ftutil.c", ("FUN_00529176", "FUN_00439be4")),
    0x00529296: (38, "2c22d035544710a9c69e7967b8b9102df78b77508ec339c37542043037ce79ab", "ft_mem_strdup", "src/base/ftutil.c", ("FUN_0044a43c", "FUN_00529262")),
}

# Ghidra loses the fourth argument to the shared Apple wrapper in its recovered
# call signature.  The two body hashes are therefore supplemented with the
# literal load encoded by each body and the corresponding in-image magic word.
# This distinguishes AppleDouble (0x00051607) from AppleSingle (0x00051600)
# without relying on function-address order alone.
APPLE_WRAPPER_MAGIC_EVIDENCE = {
    0x00528508: (b"\x83\x4c", 0x00528718, 0x00051607),
    0x00528524: (b"\x7d\x4c", 0x0052871C, 0x00051600),
}

# These upstream bodies are outside the inherited 83-row census.  They are
# authenticated here to prevent the nine-slot chain being mistaken for an
# opaque Even implementation.
UPSTREAM_FALLBACK_MECHANICS = {
    0x00525D32: (228, "2eba5089aa1585c3d4d0586a6a69c4a9820206a21413906a16854ec310ec6a94", "open_face_PS_from_sfnt_stream", ("FUN_00525c08", "FUN_00525b6e")),
    0x00525E16: (646, "478218e663ee2642b1635ab6876e015f7049ec77369eba514f69822ec8741830", "Mac_Read_POST_Resource", ("0x80", "FUN_00525b6e")),
    0x005260A4: (260, "9df79973a59e76b56fafc184a181e8a45a0fd50391a3be126107c9fd31432b8c", "Mac_Read_sfnt_Resource", ("FUN_004751c8", "FUN_00525b6e")),
    0x005261AC: (222, "85bf2388f8e74aeedd8943eba7a320a6761b8277e8c63d4e070769c98158e71e", "IsMacResource", ("FUN_00528064", "FUN_00528298")),
    0x005262AC: (170, "6dd393c1a15e9c510ce2f68732b8420fee1654e81c3fae6edbbd81d0bf18fc2e", "IsMacBinary", ("0x80", "FUN_005261ac")),
    0x00526356: (252, "a99e24ec376a04157a09486461454e60e3d0a909f768c9e805e59b63c189fa84", "load_face_in_embedded_rfork", ("uVar5 < 9", "FUN_00524f96", "FUN_0052502a")),
    0x00526452: (84, "4630af0edb217f922a8e3dabf3571b75ad65ef91a86d2bd468e9303bf7846ac4", "load_mac_face", ("FUN_005262ac", "FUN_005261ac", "FUN_00526356")),
}

BASELINE_FUNCTIONS = 10
BASELINE_BYTES = 2_152
BASELINE_ENTRIES = {
    0x005242FC,
    0x0052431C,
    0x005258A8,
    0x005259BE,
    0x005264A6,
    0x00526814,
    0x0052729C,
    0x005274B2,
    0x00527F0A,
    0x00527FF2,
}
CLUSTER_FUNCTIONS = 83
CLUSTER_BYTES = 7_874


def _census_rows() -> dict[int, dict[str, str]]:
    lines = [line for line in CENSUS.read_text().splitlines() if not line.startswith("#")]
    return {
        int(row["entry"], 16): row
        for row in csv.DictReader(lines, delimiter="\t")
    }


def _decompiled_functions() -> dict[int, str]:
    functions: dict[int, str] = {}
    marker = re.compile(r"/\* FUN 0x([0-9a-f]{8}) .*?(?=/\* FUN 0x|\Z)", re.S)
    for path in sorted(DECOMP.glob("apollo-decomp-*.c")):
        for match in marker.finditer(path.read_text(errors="replace")):
            functions[int(match.group(1), 16)] = match.group(0)
    return functions


def _verify_sources() -> None:
    provenance = json.loads(PROVENANCE.read_text())
    records = {row["local_path"]: row for row in provenance["files"]}
    source_names = (
        {row[3] for row in DIRECT_SOURCE.values()}
        | {row[3] for row in INDIRECT_SOURCE.values()}
        | {"src/base/ftobjs.c"}
    )
    for source in source_names:
        if source not in records:
            raise AdmissionError(f"source absent from provenance: {source}")
        data = (SNAPSHOT / source).read_bytes()
        if hashlib.sha256(data).hexdigest() != records[source]["sha256"]:
            raise AdmissionError(f"source hash changed: {source}")
    license_data = (SNAPSHOT / "LICENSE").read_bytes()
    if hashlib.sha256(license_data).hexdigest() != records["LICENSE"]["sha256"]:
        raise AdmissionError("FTL license hash changed")


def analyze() -> dict[str, object]:
    _verify_sources()
    image = IMAGE.read_bytes()
    if hashlib.sha256(image).hexdigest() != IMAGE_SHA256:
        raise AdmissionError("official image hash changed")
    rows = _census_rows()
    decompiled = _decompiled_functions()
    baseline_bytes = sum(
        int(rows[entry]["official_opaque_bytes"])
        for entry in BASELINE_ENTRIES
    )
    if len(BASELINE_ENTRIES) != BASELINE_FUNCTIONS or baseline_bytes != BASELINE_BYTES:
        raise AdmissionError("baseline anchor census changed")

    admitted = []
    for entry, (size, digest, symbol, source, pins) in DIRECT_SOURCE.items():
        row = rows.get(entry)
        if row is None or row["evidence"] != "base-call-graph-direct":
            raise AdmissionError(f"direct census row changed: 0x{entry:08X}")
        if int(row["official_opaque_bytes"]) != size:
            raise AdmissionError(f"direct row size changed: 0x{entry:08X}")
        body = image[entry - LOAD_BASE:entry - LOAD_BASE + size]
        if hashlib.sha256(body).hexdigest() != digest:
            raise AdmissionError(f"official body changed: 0x{entry:08X}")
        source_text = (SNAPSHOT / source).read_text(errors="replace")
        if re.search(rf"\b{re.escape(symbol)}\s*\(", source_text) is None:
            raise AdmissionError(f"upstream definition missing: {symbol}")
        stock = decompiled.get(entry, "")
        if not stock or any(pin not in stock for pin in pins):
            raise AdmissionError(f"semantic pins changed: 0x{entry:08X} {symbol}")
        admitted.append({
            "entry": f"0x{entry:08X}",
            "bytes": size,
            "symbol": symbol,
            "source": source,
            "classification": "authenticated-upstream-source",
            "license": "FTL",
        })

    admitted_indirect = []
    for entry, (size, digest, symbol, source, pins) in INDIRECT_SOURCE.items():
        row = rows.get(entry)
        if row is None or row["evidence"] != "base-call-graph-indirect":
            raise AdmissionError(f"indirect census row changed: 0x{entry:08X}")
        if int(row["official_opaque_bytes"]) != size:
            raise AdmissionError(f"indirect row size changed: 0x{entry:08X}")
        body = image[entry - LOAD_BASE:entry - LOAD_BASE + size]
        if hashlib.sha256(body).hexdigest() != digest:
            raise AdmissionError(f"official body changed: 0x{entry:08X}")
        source_text = (SNAPSHOT / source).read_text(errors="replace")
        if re.search(rf"\b{re.escape(symbol)}\s*\(", source_text) is None:
            raise AdmissionError(f"upstream definition missing: {symbol}")
        stock = decompiled.get(entry, "")
        if not stock or any(pin not in stock for pin in pins):
            raise AdmissionError(f"semantic pins changed: 0x{entry:08X} {symbol}")
        admitted_indirect.append({
            "entry": f"0x{entry:08X}",
            "bytes": size,
            "symbol": symbol,
            "source": source,
            "classification": "authenticated-upstream-source",
            "inherited_evidence_tier": "base-call-graph-indirect",
            "license": "FTL",
        })

    ftrfork = (SNAPSHOT / "src/base/ftrfork.c").read_text(errors="replace")
    if re.search(
        r"CONST_FT_RFORK_RULE_ARRAY_ENTRY\(apple_double,\s+apple_double\)\s*"
        r"CONST_FT_RFORK_RULE_ARRAY_ENTRY\(apple_single,\s+apple_single\)",
        ftrfork,
    ) is None:
        raise AdmissionError("upstream Apple wrapper rule order changed")
    for entry, (literal_load, literal_address, magic) in APPLE_WRAPPER_MAGIC_EVIDENCE.items():
        body_offset = entry - LOAD_BASE
        if image[body_offset + 2:body_offset + 4] != literal_load:
            raise AdmissionError(f"Apple wrapper literal load changed: 0x{entry:08X}")
        literal_offset = literal_address - LOAD_BASE
        observed_magic = int.from_bytes(image[literal_offset:literal_offset + 4], "little")
        if observed_magic != magic:
            raise AdmissionError(f"Apple wrapper magic changed: 0x{entry:08X}")

    fallback = []
    ftobjs = (SNAPSHOT / "src/base/ftobjs.c").read_text(errors="replace")
    for entry, (size, digest, symbol, pins) in UPSTREAM_FALLBACK_MECHANICS.items():
        body = image[entry - LOAD_BASE:entry - LOAD_BASE + size]
        if hashlib.sha256(body).hexdigest() != digest:
            raise AdmissionError(f"fallback body changed: 0x{entry:08X}")
        if re.search(rf"\b{re.escape(symbol)}\s*\(", ftobjs) is None:
            raise AdmissionError(f"fallback source definition missing: {symbol}")
        stock = decompiled.get(entry, "")
        if not stock or any(pin not in stock for pin in pins):
            raise AdmissionError(f"fallback semantic pins changed: {symbol}")
        fallback.append({
            "entry": f"0x{entry:08X}",
            "bytes": size,
            "symbol": symbol,
            "classification": "authenticated-upstream-fallback-mechanics",
            "license": "FTL",
            "inside_83_function_census": False,
        })

    rules = (SNAPSHOT / "include/freetype/internal/ftrfork.h").read_text()
    if re.search(r"#define\s+FT_RACCESS_N_RULES\s+9\b", rules) is None:
        raise AdmissionError("upstream fallback rule count changed")
    admitted_bytes = sum(row["bytes"] for row in admitted)
    if len(admitted) != 17 or admitted_bytes != 1_294:
        raise AdmissionError("direct source tranche census changed")
    if len(fallback) != 7 or sum(row["bytes"] for row in fallback) != 1_862:
        raise AdmissionError("fallback mechanics census changed")
    indirect_bytes = sum(row["bytes"] for row in admitted_indirect)
    if len(admitted_indirect) != 56 or indirect_bytes != 4_428:
        raise AdmissionError("indirect source tranche census changed")

    total_admitted_functions = BASELINE_FUNCTIONS + len(admitted) + len(admitted_indirect)
    total_admitted_bytes = BASELINE_BYTES + admitted_bytes + indirect_bytes
    cluster_entries = {
        entry
        for entry, row in rows.items()
        if row["module"] == "base" and row["status"] != "investigation-required"
    }
    if len(cluster_entries) != CLUSTER_FUNCTIONS:
        raise AdmissionError("83-function base cluster changed")
    remaining_entries = sorted(
        cluster_entries - BASELINE_ENTRIES - set(DIRECT_SOURCE) - set(INDIRECT_SOURCE)
    )
    remaining_rows = [
        {
            "entry": f"0x{entry:08X}",
            "bytes": int(rows[entry]["official_opaque_bytes"]),
            "inherited_evidence_tier": rows[entry]["evidence"],
        }
        for entry in remaining_entries
    ]
    if len(remaining_rows) != CLUSTER_FUNCTIONS - total_admitted_functions or sum(
        row["bytes"] for row in remaining_rows
    ) != CLUSTER_BYTES - total_admitted_bytes:
        raise AdmissionError("remaining base cluster reconciliation changed")

    return {
        "schema_version": 1,
        "analysis_mode": "read-only; software evidence only",
        "baseline": {"functions": BASELINE_FUNCTIONS, "bytes": BASELINE_BYTES},
        "new_direct_source_tranche": {"functions": 17, "bytes": admitted_bytes},
        "new_indirect_source_tranche": {
            "functions": len(admitted_indirect),
            "bytes": indirect_bytes,
        },
        "admitted_cluster": {
            "functions": total_admitted_functions,
            "bytes": total_admitted_bytes,
        },
        "remaining_cluster": {
            "functions": CLUSTER_FUNCTIONS - total_admitted_functions,
            "bytes": CLUSTER_BYTES - total_admitted_bytes,
            "rows": remaining_rows,
        },
        "fallback_policy": {
            "stock_selection": "upstream autodetect with Mac/rfork fallback enabled",
            "upstream_rule_count": 9,
            "mechanics_functions": len(fallback),
            "mechanics_bytes": sum(row["bytes"] for row in fallback),
            "even_specific_loader_code_found": False,
            "candidate_boundary": "autodetect, truetype-only, or cff-only",
        },
        "direct_source": admitted,
        "indirect_source": admitted_indirect,
        "fallback_mechanics": fallback,
        "limitations": [
            "source admission establishes attributable replacement, not compiler byte identity",
            "no rows remain in the bounded 83-function base-module census",
            "the seven fallback bodies are outside the inherited 83-row census and are not subtracted twice",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        report = analyze()
    except (AdmissionError, KeyError, OSError, ValueError) as error:
        print(f"FreeType base cluster admission: FAIL: {error}")
        return 1
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        admitted = report["admitted_cluster"]
        remaining = report["remaining_cluster"]
        print("FreeType base cluster admission: PASS")
        print(f"  admitted: {admitted['functions']} functions, {admitted['bytes']} bytes")
        print(f"  remaining: {remaining['functions']} functions, {remaining['bytes']} bytes")
        print("  fallback: 7 authenticated upstream functions; policy isolated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
