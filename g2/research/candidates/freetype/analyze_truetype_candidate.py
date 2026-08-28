#!/usr/bin/env python3
"""Authenticate the G2 FreeType 2.9.1 TrueType driver entry surface.

SPDX-License-Identifier: MIT

This read-only analyzer binds the official ``tt_driver_class`` record to the
authenticated upstream ``FT_DEFINE_DRIVER`` declaration, then verifies every
non-null class callback by exact image span and source definition.  It does not
claim compiler byte identity or ownership of callbacks outside that class.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from pathlib import Path


G2 = Path(__file__).resolve().parents[3]
SNAPSHOT = G2 / "third_party/freetype"
PROVENANCE = SNAPSHOT / "PROVENANCE.json"
IMAGE = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
DECOMP = G2 / "research/corpus/apollo-main/ghidra/decomp/bundles"
LOAD_BASE = 0x00437FE0
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
CLASS_ADDRESS = 0x006DED34
CLASS_SHA256 = "08612018ea9cb61fdaea5bbceb785d6d58f2f3c6eb55da1ca7d2ab92a3d134b6"


class AdmissionError(RuntimeError):
    pass


# class word: (entry, size, body sha256, symbol, source, instruction prefix)
DRIVER_SURFACE = {
    6: (0x005F903C, 12, "e9fa34c7e36a2d040315b03e434364a291c604ba644338fdcd2e3de12e37ecab", "tt_driver_init", "src/truetype/ttobjs.c", "23210164"),
    7: (0x005F9048, 2, "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8", "tt_driver_done", "src/truetype/ttobjs.c", "7047"),
    8: (0x005EF2FA, 72, "44331d802a60c6d0611a664d91da64bfba3ed972013a15946eff3d704f5973bc", "tt_get_interface", "src/truetype/ttdriver.c", "38b50400"),
    12: (0x005F881C, 416, "ee0eaf014c79add25f39f03baba24d2c24d7982e2f1f8d239bf7ca8e01b3ee10", "tt_face_init", "src/truetype/ttobjs.c", "2de9f84f"),
    13: (0x005F89BC, 124, "65439a936c6054e2deb4ab9679df1c8bf86c7bba9ffc20467bacab76d7c6e20f", "tt_face_done", "src/truetype/ttobjs.c", "f8b50400"),
    14: (0x005F8F08, 26, "795a83b277b6b93cd6f3aad909b0dc72fe97bf4b0f278b2aea77e5895e6c253e", "tt_size_init", "src/truetype/ttobjs.c", "01000020"),
    15: (0x005F8F22, 16, "7243da9e2953c9597dea6b8060171725a1a9b5ca5575904a65959871edf9ccc0", "tt_size_done", "src/truetype/ttobjs.c", "10b50400"),
    16: (0x005F904A, 14, "57c75f4f69e2b2c3c5418ef516a196f3c93bcd5bf2defdc64abc303f75831d76", "tt_slot_init", "src/truetype/ttobjs.c", "80b5d0f8"),
    18: (0x005EF280, 122, "447502b4dbae6ac52b6b9e1742aad94e695d2ac1bd92a1cf1fadfd9e96f7bde0", "tt_glyph_load", "src/truetype/ttdriver.c", "70b50400"),
    19: (0x005EF100, 30, "89f0db6bf37d26c04f21689bc27d62e2d4b3f7416226229b862f1f8b508e6635", "tt_get_kerning", "src/truetype/ttdriver.c", "38b51c00"),
    21: (0x005EF11E, 158, "9caeca8c6d7fef031e22d1c4ae2ff716889ea1fc4bb5cd8a8959ff3c70ac1138", "tt_get_advances", "src/truetype/ttdriver.c", "2de9fc41"),
    22: (0x005EF1FC, 132, "bb8977e9fd133b94a9d183931e93f0d1ca055630cc498f65d1adff9148d8cf56", "tt_size_request", "src/truetype/ttdriver.c", "f8b50500"),
    23: (0x005EF1BC, 64, "cc6b3c4c27196da90d8d6adb98a0af6557a56df20059b2c72f7daa240101551f", "tt_size_select", "src/truetype/ttdriver.c", "38b50368"),
}

NULL_DRIVER_SLOTS = {5, 17, 20}
DECOMPILER_PINS = {
    0x005F881C: ("FUN_005273f2", "FUN_005288e0", "param_2 + 0x94"),
    0x005F89BC: ("FUN_005f9292", "FUN_005f952c", "param_1 + 0x29c"),
    0x005EF1FC: ("FUN_005ef1bc", "FUN_00526b04", "param_1[0x1e]"),
    0x005EF1BC: ("FUN_00526a9c", "FUN_005f8f32", "param_1[0x1d]"),
}

# Private callbacks reached immediately below the class surface, plus the
# small second-level identity helpers needed to close trick-font and loca
# dispatch.  entry: (size, sha256, symbol, source, semantic pins, callers,
# call depth).  Caller bodies are checked below; two class callbacks absent
# from Ghidra's standalone-function corpus use decoded Thumb BL edges.
PRIVATE_HELPERS = {
    0x005EF342: (20, "be44473bff66c6a4a727e7cf18efd0983e7477d12d0d991e9c246f70362bc15a", "TT_Get_HMetrics", "src/truetype/ttgload.c", ("+ 0x21c", "+ 0x70", "param_1,0"), (), 1),
    0x005EF356: (136, "e06e59019f30335517350e218f19d5219179ec3c3aa97dc8cfde5ccef74f41d1", "TT_Get_VMetrics", "src/truetype/ttgload.c", ("param_1 + 0x124", "param_1 + 0x174", "+ 0x21c"), (), 1),
    0x005EF3DE: (150, "6a7000e991b8b6504e8554bbed21f1df2162b24392d9038950e73e45239f1186", "tt_get_metrics", "src/truetype/ttgload.c", ("FUN_005ef342", "FUN_005ef356", "param_1[0x2b]"), (0x005F031C,), 3),
    0x005EF474: (132, "cc8f1e728a4f13dc3a63bf01b1d96445a98b14aa90260b669ad499593cfdcd54", "tt_get_metrics_incr_overrides", "src/truetype/ttgload.c", ("+ 0x80", "+ 0x34", "param_1[0x2b] = 0"), (0x005F031C,), 3),
    0x005EFAD0: (42, "1dd24a37a092094a79ad70b5c928ab79c86fb4978e5917a12dd310606e2f88b7", "TT_Init_Glyph_Loading", "src/truetype/ttgload.c", ("param_1 + 0x208", "DAT_005eff38", "param_1 + 0x218"), (0x005F881C,), 1),
    0x005EFB04: (60, "9b398b39e4f3dc89472492b36def80a52bbcbeb659a37e8065f1ee2667966dca", "tt_prepare_zone", "src/truetype/ttgload.c", ("param_1 + 0xc", "param_2 + 10", "param_1 + 0x20"), (0x005EFD2A, 0x005F006A), 4),
    0x005EFB40: (490, "1cb5c12669b55713e80a478c454e48d70a24f505b32875b0cf3a9658c7905e7a", "TT_Hint_Glyph", "src/truetype/ttgload.c", ("FUN_005f423c", "FUN_005f452e", "param_1[0x27] + 0x120"), (0x005EFD2A, 0x005F006A), 4),
    0x005EFD2A: (518, "7eb3829ba879bbcfa780bb1bbea8300c4a641ae1db82450fe9c6b743b4521aa2", "TT_Process_Simple_Glyph", "src/truetype/ttgload.c", ("FUN_005efb04", "FUN_005efb40", "FUN_005f3960"), (0x005F031C,), 3),
    0x005EFF4C: (286, "4f163cfd49052f6ed5f798269168b5c7b33ad669ee03dfa666c032616fd0f19d", "TT_Process_Composite_Component", "src/truetype/ttgload.c", ("FUN_00527ba0", "FUN_00527b2e", "param_2 + 0x10"), (0x005F031C,), 3),
    0x005F006A: (488, "30d1c7d402158435033215ef3125e3f558bc9ba2426dabfc7ad77eaa5c3a5fdb", "TT_Process_Composite_Glyph", "src/truetype/ttgload.c", ("FUN_005efb04", "FUN_005efb40", "FUN_005f4334"), (0x005F031C,), 3),
    0x005F0252: (172, "1cb09fa17c777c2772770960330bb519d9703cf934ee60c5e179d18a30e00142", "tt_loader_set_pp", "src/truetype/ttgload.c", ("param_1[0x11]", "param_1[0x2d]", "param_1[0x30]"), (0x005F031C,), 3),
    0x005F02FE: (30, "a1da531c54f2ef080a82c6453d002a70cc1a055d97001f3c48c3b0ce5aad958f", "ft_list_get_node_at", "src/truetype/ttgload.c", ("iVar1 + 4", "param_2 + -1", "return iVar1"), (0x005F031C,), 3),
    0x005F031C: (2054, "468e1801a44aa1bf05b433784f9f366d48d5bfddad9fe15c74c441393f117e54", "load_truetype_glyph", "src/truetype/ttgload.c", ("FUN_005ef3de", "FUN_005f3960", "FUN_005f919c"), (), 2),
    0x005F0B28: (434, "6d34481f3cda240dfa9ee10639062b20f2f9c0cdd7e97cd7f5762c31832c228b", "compute_glyph_metrics", "src/truetype/ttgload.c", ("DAT_005f1558", "FUN_00527ace", "FUN_005f954e"), (), 2),
    0x005F0CDA: (158, "60765d8ba51e519ec7c69f5d0fee9c6e44cbf5c9d95383e491d69508b751e4c7", "load_sbit_image", "src/truetype/ttgload.c", ("+ 0x21c", "DAT_005f1560", "param_2 + 0x48"), (), 2),
    0x005F0D78: (564, "6bfdaf97418b1f28a4a074e27ab9af9b9f1f7ac73f3cf3a18bb46d377d4b029b", "tt_loader_init", "src/truetype/ttgload.c", ("FUN_005f8e40", "FUN_005f436e", "FUN_005f8afa"), (), 2),
    0x005F0FC6: (662, "924623c9a1e6b7be2f4881fc0a1d40373729232bf44771481d517571943c6d0f", "TT_Load_Glyph", "src/truetype/ttgload.c", (), (), 1),
    0x005F0FB4: (18, "c846c61aab481fe45bccb5dc61dd3b9bfddab3095b2844b9ef9272eed856b1a4", "tt_loader_done", "src/truetype/ttgload.c", (), (), 2),
    0x005F125C: (262, "573d8eb9a0d6236cbb74f6a62560e7db7315b303afec464ea5ad956438eeee03", "ft_var_readpackedpoints", "src/truetype/ttgxvar.c", ("FUN_00528a86", "FUN_0052919c", "*param_3 = 0"), (0x005F336C,), 3),
    0x005F1362: (202, "0bade8f7d1978e5cb7d4ed6fbbe2ce4d5d47c9292116c4398fcd7e8dcbe3e4c6", "ft_var_readpackeddeltas", "src/truetype/ttgxvar.c", ("FUN_00528a86", "FUN_0052919c", "uVar4 & 0x3f"), (0x005F336C,), 3),
    0x005F142C: (298, "e902aef3efe51ccd012360e9a732aa7f567ebe5114f9df68d6a0d640e1a1fb78", "ft_var_load_avar", "src/truetype/ttgxvar.c", ("param_1 + 700", "DAT_005f2094", "FUN_005289d0"), (0x005F289E, 0x005F309E), 3),
    0x005F1564: (932, "c2664ceff1d8ed8b1c658d058f9c7944df5ebe24596f910019bd210856f1af56", "ft_var_load_item_variation_store", "src/truetype/ttgxvar.c", ("param_1 + 700", "FUN_00528ba8", "*param_3"), (0x005F2098,), 4),
    0x005F1BAC: (342, "da0d74df71ab371077d6fe6e84c4ab7d0ace27c502d55ed0f8d24838c1816543", "ft_var_get_item_delta", "src/truetype/ttgxvar.c", ("param_1 + 700", "FUN_00524754", "param_4 * iVar5 * 2"), (0x005F225E,), 2),
    0x005F1DE4: (686, "aa36f9f5adb0f1f4f2ab2e6b2903106b26b9f7fdbc9dc6efb11d7ce4026a003f", "ft_var_get_value_pointer", "src/truetype/ttgxvar.c", ("DAT_005f252c", "param_1 + 0x234", "param_1 + 0x1ce"), (0x005F225E,), 2),
    0x005F2098: (440, "53bfe5e09bde898b4c17d6fe4e28ff81fbd01a45a79f2ce6870836287525d4a1", "ft_var_load_mvar", "src/truetype/ttgxvar.c", ("param_1 + 700", "DAT_005f2d90", "FUN_005f1564"), (0x005F289E,), 3),
    0x005F225E: (224, "0d48677dc4d410c79029b12ed2f071982f287a24a00acf2705b1e7b15074a826", "tt_apply_mvar", "src/truetype/ttgxvar.c", ("param_1 + 0x2c0", "FUN_005f1de4", "param_1 + 0x1e4"), (0x005F881C,), 1),
    0x005F233E: (486, "2fb43638b93e6f7c2409535318fb1a6b334bf4336450e6fd058475f932fe534e", "ft_var_load_gvar", "src/truetype/ttgxvar.c", ("DAT_005f2fdc", "DAT_005f2fe0", "param_1 + 700"), (0x005F2D94,), 4),
    0x005F2560: (254, "9275d1f14043a7e60d2c8a5d00602fbbb050f0001a5bc638955201292e6cc7a1", "ft_var_apply_tuple", "src/truetype/ttgxvar.c", ("0x10000", "param_1[2]", "FUN_00524606"), (0x005F336C,), 3),
    0x005F265E: (304, "ab3064a2116586a67f2f88755e0017fb3e831f4ab2cebb26f2bb51dc0336299a", "ft_var_to_normalized", "src/truetype/ttgxvar.c", ("param_1 + 700", "FUN_00524754", "uVar7 < param_2"), (0x005F289E, 0x005F309E), 3),
    0x005F278E: (272, "3980cea8d7114a06b4e2204c89b3599bafb9d50078482983f60d3362103bf993", "ft_var_to_design", "src/truetype/ttgxvar.c", ("param_1 + 700", "FUN_00524606", "FUN_005246f8"), (0x005F2D94,), 4),
    0x005F289E: (1264, "de8d2e41d417d7fac2a5d5f347e1b514a6692848b330e8995cac68dcdf52d11b", "TT_Get_MM_Var", "src/truetype/ttgxvar.c", ("param_1 + 700", "FUN_005f2098", "FUN_005f265e"), (0x005F309E, 0x005F32CC), 2),
    0x005F2D94: (580, "d5b3e604285e081130a159923d816c640ab9d8442347fec21740ec3b70506ccd", "tt_set_mm_blend", "src/truetype/ttgxvar.c", ("param_1 + 700", "FUN_005f233e", "FUN_005f278e"), (0x005F309E,), 3),
    0x005F309E: (406, "c13ad500ea2790ba655b4aa0a9646efbf559deffed1ed99fc6036d74b6ff7af7", "TT_Set_Var_Design", "src/truetype/ttgxvar.c", ("param_1 + 700", "FUN_005f289e", "FUN_005f2d94"), (0x005F32CC,), 2),
    0x005F32CC: (160, "1be0d1804f4e4b2be3ed09a9d47c814976790ac34860a7bf7cb8c0e03ce71844", "TT_Set_Named_Instance", "src/truetype/ttgxvar.c", ("param_1 + 700", "FUN_005f289e", "FUN_005f309e"), (0x005F881C,), 1),
    0x005F336C: (938, "df1ba50cb4a4ba231f859c50453e9253b3f3603a6f72474cae4469c48109c9c9", "tt_face_vary_cvt", "src/truetype/ttgxvar.c", ("param_1 + 0x29c", "FUN_005f125c", "FUN_005f1362"), (0x005F92A8,), 2),
    0x005F3748: (122, "4e1ff293ecece5383f38e271ebf85a5e7836813f8ea0a72c760fcfacdccee187", "tt_delta_shift", "src/truetype/ttgxvar.c", ("param_4 + param_3 * 8", "param_5 + param_3 * 8", "param_3 + 1"), (0x005F3890,), 5),
    0x005F37C2: (206, "a3e5f7704605879448c33fd2e1213d93b6a8e53482a4b4c856d470c5394692a9", "tt_delta_interpolate", "src/truetype/ttgxvar.c", ("FUN_00524754", "FUN_005246f8", "iVar6 < 2"), (0x005F3890,), 5),
    0x005F3890: (208, "c34097f56cb9c4a88349d0588c99d2868b3d59b31012bd19dd648d95c6dc00ca", "tt_interpolate_deltas", "src/truetype/ttgxvar.c", ("FUN_005f3748", "FUN_005f37c2", "*param_1"), (0x005F3960,), 4),
    0x005F3960: (1680, "969b4b3564ea17938d13b108dc4f69103c426a586b2054c569a2d095919b21a8", "TT_Vary_Apply_Glyph_Deltas", "src/truetype/ttgxvar.c", ("param_1 + 700", "FUN_005f3890", "FUN_005f2560"), (0x005F031C,), 3),
    0x005F404E: (136, "c227dc16cf8524ffb766499f214aeaa6427969344a9b5851bb520bc34c8e11ae", "ft_var_done_item_variation_store", "src/truetype/ttgxvar.c", ("param_2[1]", "param_2[4]", "FUN_00529256"), (0x005F40D6,), 2),
    0x005F40D6: (324, "37801a88bbe77c58e2ee8bfe16c801ad3bbabde3ab14b21f40a9578e7a1fe4b4", "tt_done_blend", "src/truetype/ttgxvar.c", ("param_1 + 700", "FUN_005f404e", "iVar1 + 0x48"), (0x005F89BC,), 1),
    0x005F421A: (34, "080762b63ecd778a4cbcdef86a79f687429a06f2d47e3a0eaa2fc967ecc0c8b7", "TT_Goto_CodeRange", "src/truetype/ttinterp.c", ("param_1 + 0x168", "param_1 + 0x170", "param_1 + 0x164"), (0x005F8AFA,), 4),
    0x005F423C: (22, "346370ad187e395f5760845e3af9b07a31fcf8114155d74b327db6a03c0b1d32", "TT_Set_CodeRange", "src/truetype/ttinterp.c", ("param_2 * 8 + 0x1b8", "param_2 * 8 + 0x1bc"), (0x005EFB40, 0x005F8AFA), 4),
    0x005F4252: (22, "0e50073b5730c47dd3c20c0dd3dc92a06ff9004c5cd65dee90fc9a7c3fff929f", "TT_Clear_CodeRange", "src/truetype/ttinterp.c", ("param_2 * 8 + 0x1b8", "param_2 * 8 + 0x1bc"), (0x005F8AFA,), 4),
    0x005F4268: (104, "53b2e3202444645b92d498c8635220fa485a9227844ce95b7528754a6b83c4af", "TT_Done_Context", "src/truetype/ttinterp.c", ("param_1[0x6e]", "param_1[99]", "FUN_00529256"), (0x005F8BCA,), 2),
    0x005F42D0: (100, "35489420d5a8eafc23b6d89caf57fdc5960f5335926a53bbc8a65e4dea0a1aa1", "Init_Context", "src/truetype/ttinterp.c", ("param_1[0x6d] = 0x20", "FUN_0052919c", "FUN_005f4268"), (0x005F45C0,), 6),
    0x005F4334: (58, "62af06917a5b2959f1be938dd86796bb5bc7cbcd2eefa6cd9ffc28fa65f0b577", "Update_Max", "src/truetype/ttinterp.c", ("param_3 * *param_2", "param_3 * param_5", "*param_2 = param_5"), (0x005F006A, 0x005F436E), 4),
    0x005F436E: (380, "707c3791bd4fc5dfb468d9c5e0a5c29d4e8fe7bfb73b4960ceeb6ada9a13a4af", "TT_Load_Context", "src/truetype/ttinterp.c", ("param_1[0x65]", "FUN_005f4334", "param_1 + 0x2d"), (0x005F0D78,), 3),
    0x005F44EA: (68, "103314af073623ae64dd6a2a70cd38f4f11c9313bf33ed0203c6f295ab9b9b9b", "TT_Save_Context", "src/truetype/ttinterp.c", ("param_2 + 0x7c", "param_2 + 0x94", "iVar3 < 3"), (0x005F8AFA,), 4),
    0x005F452E: (146, "bbb41063316bd8ddb145f806d49006f96630cb8931e40275388cbb32f729e701", "TT_Run_Context", "src/truetype/ttinterp.c", ("FUN_005f421a", "param_1 + 0x24", "param_1 + 0x12"), (0x005EFB40,), 5),
    0x005F45C0: (58, "c49b760fdb45552954f24247649fac324c3eac4c074d04722bd04531d06efeaf", "TT_New_Context", "src/truetype/ttinterp.c", ("FUN_00529148", "FUN_005f42d0", "return CONCAT44"), (0x005F8C6C,), 5),
    0x005F83EC: (92, "f8d483feb495d1e8f629e70a4cad1a5766d23ed450c0e2b364d344069e8dffa6", "tt_glyphzone_done", "src/truetype/ttobjs.c", ("param_1[7]", "param_1[3]", "param_1[5]"), (0x005F8BCA,), 2),
    0x005F8448: (208, "286a12e6735624282b43156304a12b13b90d8290cdbd173ca77bb4faa690b3b1", "tt_glyphzone_new", "src/truetype/ttobjs.c", ("FUN_0052919c", "FUN_005f83ec", "FUN_0043c0e4"), (0x005F8C6C,), 5),
    0x005F8518: (44, "78383e6211efd31b45012670d68bdd96604e92726aa5bec9dac820364b6607e9", "tt_check_trickyness_family", "src/truetype/ttobjs.c", ("0x19", "FUN_0044b63a", "DAT_005f9194"), (0x005F876C,), 2),
    0x005F8568: (76, "89981c072d9e9c4b5d21e0419079defbfe0099f2001483cb0b51230198af0a04", "tt_synth_sfnt_checksum", "src/truetype/ttobjs.c", ("FUN_00528ac6", "FUN_00528a86", "FUN_00528a66"), (0x005F85B4,), 4),
    0x005F85B4: (70, "be334f02d65e517fb6b9bf44d25cf0f834fed9590e53738ff66aaa644c48c0e1", "tt_get_sfnt_checksum", "src/truetype/ttobjs.c", ("param_1 + 0x204", "FUN_005f8568", "param_1 + 0x9c"), (0x005F85FA,), 3),
    0x005F85FA: (364, "a2e40569ef80ac3c43ebe70690b1c762c4d6fe11d2e2762f8821a21ff5b38381", "tt_check_trickyness_sfnt_ids", "src/truetype/ttobjs.c", ("local_a0", "0x1c", "DAT_005f93a0"), (0x005F876C,), 2),
    0x005F876C: (50, "92c55058b0b11cadd78878b70ce72912e4a12be10e38686f38e5cd05b25f50af", "tt_check_trickyness", "src/truetype/ttobjs.c", ("FUN_005f8518", "FUN_005f85fa", "param_1 + 0x14"), (0x005F881C,), 1),
    0x005F879E: (126, "c3a9c0a0452192d9897f5b76f4a20a19a9f891384f9deade9c4b83dfb9b9a1a7", "tt_check_single_notdef", "src/truetype/ttobjs.c", ("FUN_005f919c", "FUN_00526f74", "DAT_005f94ec"), (0x005F881C,), 1),
    0x005F8A38: (194, "d34cba0b50d0ae96fc2ec06e4bf468d3881fcaa0abe071b3992a4041b4554ce5", "tt_size_run_fpgm", "src/truetype/ttobjs.c", ("FUN_005f436e", "FUN_005f423c", "FUN_005f44ea"), (0x005F8C6C,), 5),
    0x005F8AFA: (208, "0e4f753f07be31524a01cff38216f3f0187d21aa085da9d7a77f12e58eb37b46", "tt_size_run_prep", "src/truetype/ttobjs.c", ("FUN_005f436e", "FUN_005f423c", "FUN_005f44ea"), (0x005F0D78, 0x005F8E40), 3),
    0x005F8BCA: (162, "673803959f87b6deb5d39b469a891c2cebcf159915fb110f0ce13031e14c8370", "tt_size_done_bytecode", "src/truetype/ttobjs.c", ("FUN_005f4268", "FUN_005f83ec", "param_1[0x4c]"), (), 1),
    0x005F8C6C: (468, "8cbd65b79e00e1b4aad21bd542a4fcf60d4cf5fda2d36fa6db2db32c8e07a46d", "tt_size_init_bytecode", "src/truetype/ttobjs.c", ("FUN_005f45c0", "FUN_005f8448", "FUN_005f8a38"), (0x005F8E40,), 4),
    0x005F8E40: (196, "e287de68a9643725aae751b29ec3917f00a7e90aed5a55409fb490f00e5d14fa", "tt_size_ready_bytecode", "src/truetype/ttobjs.c", ("FUN_005f8c6c", "DAT_005f9500", "FUN_005f8afa"), (0x005F0D78,), 3),
    0x005F8F32: (266, "cc54ed4c3897fd04d80d222a1d15091a18602854272fbae05d17db5ad65e1a4e", "tt_size_reset", "src/truetype/ttobjs.c", ("param_1 + 0x1c", "FUN_005246f8", "FUN_00524754"), (0x005EF1BC, 0x005EF1FC), 1),
    0x005F9058: (316, "02a00c0e301dca3420a44f7daa980b8c567b1cbf567f0b1ed359cf7e65c02598", "tt_face_load_loca", "src/truetype/ttpload.c", ("param_1 + 0x2b0", "param_1 + 0x2d4", "FUN_00528992"), (0x005F881C,), 1),
    0x005F919C: (246, "8dc4208b8b7a995f3df31aef3dcfd32277dc15a881a208d807fa736673bcc599", "tt_face_get_location", "src/truetype/ttpload.c", ("param_1 + 0x2d8", "param_1 + 0x2d4", "*param_3"), (0x005F879E,), 2),
    0x005F9292: (22, "219174615e777ad68a7720c635834bdae501124320408817c94d888de6feb8b6", "tt_face_done_loca", "src/truetype/ttpload.c", ("FUN_005289b0", "param_1 + 0x2d8", "param_1 + 0x2d4"), (0x005F89BC,), 1),
    0x005F92A8: (170, "ba1e47bb48d0ef397fd09930e70151d5b013fd031dae4c6b364f44615ce30230", "tt_face_load_cvt", "src/truetype/ttpload.c", ("FUN_0052919c", "FUN_005289d0", "FUN_005f336c"), (0x005F881C,), 1),
    0x005F935C: (68, "f96f2945f3e725af74bb9a3e1322397c5733b4f86f414216056b76d21ad22528", "tt_face_load_fpgm", "src/truetype/ttpload.c", ("param_1 + 0x288", "param_1 + 0x28c", "FUN_00528992"), (0x005F881C,), 1),
    0x005F93A4: (68, "d9512676e604d74700fac4f76c9baf1b0636e471bf74b60696002000eddc98ef", "tt_face_load_prep", "src/truetype/ttpload.c", ("param_1 + 0x290", "param_1 + 0x294", "FUN_00528992"), (0x005F881C,), 1),
    0x005F93E8: (260, "acf1cacd18a9ea4fa945c784f7a8fbbfb325aa80133f1644ee132dc633720c15", "tt_face_load_hdmx", "src/truetype/ttpload.c", ("param_1 + 0x2dc", "param_1 + 0x2ec", "param_1 + 0x2e4"), (0x005F881C,), 1),
    0x005F952C: (34, "07f1d4befe90024ab459908b7ed42e3c995718f8085fcce834d1c5c6160acf79", "tt_face_free_hdmx", "src/truetype/ttpload.c", ("param_1 + 0x2ec", "param_1 + 0x2dc", "FUN_005289b0"), (0x005F89BC,), 1),
    0x005F954E: (60, "55165bd76a240e3fd66b1d4022fbf6b8e52398242c63378930731651ea59525e", "tt_face_get_device_metrics", "src/truetype/ttpload.c", ("param_1 + 0x2e4", "param_1 + 0x2ec", "param_1 + 0x2dc"), (0x005F0B28,), 3),
}

RAW_CALL_EDGES = {
    (0x005EF11E, 158): {0x005EF342, 0x005EF356},
    (0x005EF280, 122): {0x005F0FC6},
    (0x005F0FC6, 662): {
        0x005F031C,
        0x005F0B28,
        0x005F0CDA,
        0x005F0D78,
        0x005F0FB4,
    },
    (0x005F8F22, 16): {0x005F8BCA},
}

PRIVATE_FRONTIER = {}

# The compiler preserves source order exactly from Ins_MPPEM through
# TT_RunIns.  The digest pins address, size, image-body digest, and upstream
# symbol for all 126 bodies without duplicating a fragile generated list.
INTERPRETER_BODY_FIRST = 0x005F4EE4
INTERPRETER_BODY_LAST = 0x005F7980
INTERPRETER_MAPPING_SHA256 = (
    "ee11f49b4c410aa71584a4a40009751af389aa8ab54031a98ef11a217b927f4d"
)

# Standalone support bodies reached by the opcode engine but located before
# the source-ordered handler run.  entry: (size, sha256, symbol).
INTERPRETER_SUPPORT = {
    0x005F45FA: (62, "e19dbdc1b2d9f6dad98c92cde4eaaab9f8924cc13d75dadb8539436f81c79c15", "TT_MulFix14"),
    0x005F4638: (128, "f206185d5d2678d5b5b65340adec810a4850c93fe4cc02ff025751e21e1d5c3c", "TT_DotFix14"),
    0x005F46B8: (92, "ab134d2afae33cdaf71a2ad4c4b58ee4afc810b23b737ac8376c1823e47d1168", "Current_Ratio"),
    0x005F47BE: (48, "f7b53fd106247d56bc0d0a30e277ff986f83c7d8809b5ea28f3426d3139a7125", "GetShortIns"),
    0x005F47EE: (78, "643aa6b969f7e34bcaa9a147314edfdde0c4b0d4dc8675bf9da024475320250b", "Ins_Goto_CodeRange"),
    0x005F4C14: (110, "40bd859f43f3bd1bf2406a21e8bd036065f1d043b25f090f290dc0f3ad0492c3", "Compute_Round"),
    0x005F4C82: (216, "7830fb3a7e3e97b314cb1adef8c9772f7e51cc4fc6f0a7417e1a505d81162066", "SetSuperRound"),
    0x005F4D8E: (292, "c46c890165367d3c175a10c8b39282f17240556c1b9df2145c26fcfdab72a2b6", "Compute_Funcs"),
    0x005F4EB2: (50, "57a2d914551261d78c61002a7afcff33d8c64c0a2127d3533ee39b8089ecc088", "Normalize"),
}

# Bodies entered exclusively through TT_ExecContext function pointers.
# entry: (size, sha256).  Identity is supplied by CALLBACK_POINTERS.
CALLBACK_BODIES = {
    0x005F4714: (6, "4cbb9d85fc782d01faa2f334e6f591f7940cab9d2137a0edc5af5e4ac6619912"),
    0x005F471A: (22, "27e212a74cf4195ac4735066a9155cd180b337a8702c1e41c46530da366309e9"),
    0x005F4730: (10, "ddac8fcf1933d30d830603324d6a7cf63e009bd8742893930971dcc4e4f413ff"),
    0x005F473A: (28, "037e0dd276e3eb193ee5a672e4a2accee51c5283b3ff5f536d1feade81aae417"),
    0x005F4756: (10, "e25d9800ebbe0369c216c85eb4f3e604848ebbd43d044ea7d82a7a5cc087e5c1"),
    0x005F4760: (32, "fca4264bdb4708387d7f1580493fdd4d5e2c44bccaf54bdc2ca7ad4c36ec8aad"),
    0x005F4780: (20, "3bb94867a83f869aa102a2ad54459e2ced040f12399cf3d1990bb9e303cbade5"),
    0x005F4794: (42, "c0a39b64a037c2b4a5eacb0f18589b35cfee255fdaf09a9f512c40380f9f596b"),
    0x005F483C: (230, "e213ad27bd221ae57cc12d10e9ecf8839c7c5beb32ba25d19c82a71b71cd4e6f"),
    0x005F4922: (94, "1751f519ed62fde2160d87f3d3f213284754ec54bd498e4f3c74b64c35228a4b"),
    0x005F4980: (98, "6679f105e41d1e40d753ac7594685a8687a6971119e8f6fffcedc9f16c3c9bff"),
    0x005F49E2: (84, "36f7950652682ed8a3a7a189ad73b911c8df80fdd5e5353fc9c9124525fabd06"),
    0x005F4A36: (26, "d8dbf7c35fa00c0db0128d7d5f908f43d4714765243924b6db9cc260a9518b3d"),
    0x005F4A50: (30, "e4b47ba00d03a543948b04ca0309b3e383e127a9a303e47a8d2f8e2dd5dc8a04"),
    0x005F4A6E: (26, "a3cc2a5560908ce65dad97f07be136dd5a3f93d0739a9560589fae8badaad478"),
    0x005F4A88: (40, "68fe65f3088df45dc29b1b067e846d7bab523a6e6a1f36eb039573de705c220e"),
    0x005F4AB0: (42, "f90f6bda54b486858f04a959847484bc234c094da0e0a0565ebec0e3ecdd4b42"),
    0x005F4ADA: (36, "8a067ecfd05ec855a4e579fcd10abdf402ab4cffc4e96b820def0f18b008060f"),
    0x005F4AFE: (40, "9ac735271a4a16593fe6947d478ce05effe9328d478a32ced0963804e9357325"),
    0x005F4B26: (40, "3737e484a43a2266d56a4b42677503e9b54a9a4422176dfe0bed0e190de0c2b8"),
    0x005F4B4E: (92, "8d34fe3cf06ff071546322fcf8bd7ad6a4beaa98ffafe88c0960920a0f266dbd"),
    0x005F4BAA: (106, "a0f08817baf0196c191afebbf7738fda88ffb7d62162da16455bf0108d7f11f8"),
    0x005F4D5A: (22, "a480a25cbd67aa71e2df790b27b60bbeaa163064bbd3ca5409a98f16fced2332"),
    0x005F4D70: (22, "43cf03ebd1bb9c849d7687ae314be9afe4692db21813110dd7e87a63f1bebbd6"),
    0x005F4D86: (4, "3fcd8c24536770ad653e50315cb985488ae1cfc3ff3bd739a4764f4f6d004633"),
    0x005F4D8A: (4, "ecec3e4c87657f68661fadf17bbec0a160a04a5a346c7a993dc25f9f28284d85"),
}

# literal slot: (Thumb target without state bit, source identity, role)
CALLBACK_POINTERS = {
    0x005F9504: (0x005F7980, "TT_RunIns", "face-interpreter-fallback"),
    0x005F8544: (0x005F471A, "Current_Ppem_Stretched", "current-ppem-stretched"),
    0x005F8548: (0x005F473A, "Read_CVT_Stretched", "read-cvt-stretched"),
    0x005F854C: (0x005F4760, "Write_CVT_Stretched", "write-cvt-stretched"),
    0x005F8550: (0x005F4794, "Move_CVT_Stretched", "move-cvt-stretched"),
    0x005F8554: (0x005F4714, "Current_Ppem", "current-ppem"),
    0x005F8558: (0x005F4730, "Read_CVT", "read-cvt"),
    0x005F855C: (0x005F4756, "Write_CVT", "write-cvt"),
    0x005F8560: (0x005F4780, "Move_CVT", "move-cvt"),
    0x005F5300: (0x005F4A6E, "Round_None", "round-off"),
    0x005F5304: (0x005F4A88, "Round_To_Grid", "round-grid"),
    0x005F5308: (0x005F4AFE, "Round_Up_To_Grid", "round-up"),
    0x005F530C: (0x005F4ADA, "Round_Down_To_Grid", "round-down"),
    0x005F5310: (0x005F4AB0, "Round_To_Half_Grid", "round-half-grid"),
    0x005F5314: (0x005F4B26, "Round_To_Double_Grid", "round-double-grid"),
    0x005F5318: (0x005F4B4E, "Round_Super", "round-super"),
    0x005F531C: (0x005F4BAA, "Round_Super_45", "round-super-45"),
    0x005F5320: (0x005F4D86, "Project_x", "project-x"),
    0x005F5324: (0x005F4D8A, "Project_y", "project-y"),
    0x005F5328: (0x005F4D5A, "Project", "project-general"),
    0x005F532C: (0x005F4D70, "Dual_Project", "dual-project-general"),
    0x005F5330: (0x005F483C, "Direct_Move", "move-general"),
    0x005F5334: (0x005F4922, "Direct_Move_Orig", "move-original-general"),
    0x005F5AE4: (0x005F4980, "Direct_Move_X", "move-x"),
    0x005F5AE8: (0x005F4A36, "Direct_Move_Orig_X", "move-original-x"),
    0x005F5AFC: (0x005F49E2, "Direct_Move_Y", "move-y"),
    0x005F5B10: (0x005F4A50, "Direct_Move_Orig_Y", "move-original-y"),
}

INTERPRETER_TABLES = {
    "pop_push_count": (0x005F8768, 0x006CFBB8, 256, "4bf082b7e7418bc5dc1c19456f393e050e798832578cd3cfc4c8e16a5bf9cb6b"),
    "opcode_length": (0x005F8564, 0x006CFCB8, 256, "788161124339fcf2da9571c636621aa06e3f1646cff70d0afb78678092413afa"),
}


def _decompiled_functions() -> dict[int, str]:
    functions: dict[int, str] = {}
    marker = re.compile(r"/\* FUN 0x([0-9a-f]{8}) .*?(?=/\* FUN 0x|\Z)", re.S)
    for path in sorted(DECOMP.glob("apollo-decomp-*.c")):
        for match in marker.finditer(path.read_text(errors="replace")):
            functions[int(match.group(1), 16)] = match.group(0)
    return functions


def _decompiled_metadata() -> dict[int, tuple[int, str]]:
    metadata: dict[int, tuple[int, str]] = {}
    marker = re.compile(
        r"/\* FUN 0x([0-9a-f]{8}) FUN_[0-9a-f]{8} "
        r"bytes=(\d+) sha256=([0-9a-f]{64})"
    )
    for path in sorted(DECOMP.glob("apollo-decomp-*.c")):
        for match in marker.finditer(path.read_text(errors="replace")):
            metadata[int(match.group(1), 16)] = (
                int(match.group(2)),
                match.group(3),
            )
    return metadata


def _interpreter_source_symbols() -> list[str]:
    source = (SNAPSHOT / "src/truetype/ttinterp.c").read_text(errors="replace")
    definitions = re.compile(
        r"(?m)^  (?:FT_LOCAL_DEF\([^\n]+\)|FT_EXPORT_DEF\([^\n]+\)|"
        r"static(?: __attribute__\(\([^\n]+\)\))?"
        r"(?: [A-Za-z_][\w* ]*)?)\n  ([A-Za-z_][A-Za-z0-9_]*)\s*\("
    )
    symbols = [match.group(1) for match in definitions.finditer(source)]
    first = symbols.index("Ins_MPPEM")
    last = symbols.index("TT_RunIns")
    return symbols[first:last + 1]


def _admit_interpreter_dispatch(
    image: bytes, decompiled: dict[int, str]
) -> dict[str, object]:
    source_path = "src/truetype/ttinterp.c"
    source = (SNAPSHOT / source_path).read_text(errors="replace")
    metadata = _decompiled_metadata()
    bodies = [
        (entry, size, digest)
        for entry, (size, digest) in sorted(metadata.items())
        if INTERPRETER_BODY_FIRST <= entry <= INTERPRETER_BODY_LAST
    ]
    symbols = _interpreter_source_symbols()
    if len(bodies) != 126 or len(symbols) != 126:
        raise AdmissionError("interpreter source/body census changed")
    mapping_material = "\n".join(
        f"{entry:08x}:{size}:{digest}:{symbol}"
        for (entry, size, digest), symbol in zip(bodies, symbols)
    ).encode()
    if hashlib.sha256(mapping_material).hexdigest() != INTERPRETER_MAPPING_SHA256:
        raise AdmissionError("interpreter source-order identity mapping changed")

    opcode_rows = []
    opcode_entries = set()
    for (entry, size, digest), symbol in zip(bodies, symbols):
        body = image[entry - LOAD_BASE:entry - LOAD_BASE + size]
        if hashlib.sha256(body).hexdigest() != digest:
            raise AdmissionError(f"interpreter opcode body changed: {symbol}")
        if re.search(rf"\b{re.escape(symbol)}\s*\(", source) is None:
            raise AdmissionError(f"interpreter upstream definition missing: {symbol}")
        opcode_entries.add(entry)
        opcode_rows.append({
            "entry": f"0x{entry:08X}",
            "bytes": size,
            "symbol": symbol,
            "source": source_path,
            "classification": "authenticated-upstream-interpreter-body",
            "license": "FTL",
        })

    # Every body in the ordered run is reachable from TT_RunIns.  Six are
    # helper bodies reached by handlers rather than the main switch itself.
    call_graph: dict[int, set[int]] = {}
    for entry in opcode_entries:
        text = decompiled.get(entry, "")
        call_graph[entry] = {
            int(target, 16)
            for target in re.findall(r"FUN_([0-9a-f]{8})", text)
            if int(target, 16) in opcode_entries and int(target, 16) != entry
        }
    reachable = {INTERPRETER_BODY_LAST}
    pending = [INTERPRETER_BODY_LAST]
    while pending:
        for target in call_graph[pending.pop()] - reachable:
            reachable.add(target)
            pending.append(target)
    if reachable != opcode_entries:
        missing = sorted(opcode_entries - reachable)
        raise AdmissionError(f"interpreter handler reachability changed: {missing!r}")
    direct_main = call_graph[INTERPRETER_BODY_LAST]
    if len(direct_main) != 119:
        raise AdmissionError("TT_RunIns direct handler census changed")

    support_rows = []
    for entry, (size, digest, symbol) in sorted(INTERPRETER_SUPPORT.items()):
        body = image[entry - LOAD_BASE:entry - LOAD_BASE + size]
        if hashlib.sha256(body).hexdigest() != digest:
            raise AdmissionError(f"interpreter support body changed: {symbol}")
        if re.search(rf"\b{re.escape(symbol)}\s*\(", source) is None:
            raise AdmissionError(f"interpreter support definition missing: {symbol}")
        support_rows.append({
            "entry": f"0x{entry:08X}",
            "bytes": size,
            "symbol": symbol,
            "source": source_path,
            "classification": "authenticated-upstream-interpreter-support",
            "license": "FTL",
        })

    identities: dict[int, str] = {}
    pointer_rows = []
    for slot, (target, symbol, role) in sorted(CALLBACK_POINTERS.items()):
        pointer = struct.unpack_from("<I", image, slot - LOAD_BASE)[0]
        if pointer != target | 1:
            raise AdmissionError(f"interpreter callback pointer changed: {role}")
        if re.search(rf"\b{re.escape(symbol)}\s*\(", source) is None:
            raise AdmissionError(f"interpreter callback definition missing: {symbol}")
        previous = identities.setdefault(target, symbol)
        if previous != symbol:
            raise AdmissionError(f"conflicting callback identity: 0x{target:08X}")
        pointer_rows.append({
            "literal": f"0x{slot:08X}",
            "target": f"0x{target:08X}",
            "symbol": symbol,
            "role": role,
            "thumb": True,
            "license": "FTL",
        })
    if len(pointer_rows) != 27 or len(identities) != 27:
        raise AdmissionError("interpreter callback pointer census changed")

    callback_rows = []
    for entry, (size, digest) in sorted(CALLBACK_BODIES.items()):
        body = image[entry - LOAD_BASE:entry - LOAD_BASE + size]
        if hashlib.sha256(body).hexdigest() != digest:
            raise AdmissionError(
                f"interpreter callback body changed: {identities.get(entry, entry)}"
            )
        symbol = identities.get(entry)
        if symbol is None:
            raise AdmissionError(f"unidentified interpreter callback: 0x{entry:08X}")
        callback_rows.append({
            "entry": f"0x{entry:08X}",
            "bytes": size,
            "symbol": symbol,
            "source": source_path,
            "classification": "authenticated-upstream-indirect-callback",
            "license": "FTL",
        })

    table_rows = []
    for name, (literal, address, size, digest) in sorted(INTERPRETER_TABLES.items()):
        resolved = struct.unpack_from("<I", image, literal - LOAD_BASE)[0]
        if resolved != address:
            raise AdmissionError(f"interpreter table literal changed: {name}")
        data = image[address - LOAD_BASE:address - LOAD_BASE + size]
        if hashlib.sha256(data).hexdigest() != digest:
            raise AdmissionError(f"interpreter table changed: {name}")
        table_rows.append({
            "name": name,
            "literal": f"0x{literal:08X}",
            "address": f"0x{address:08X}",
            "bytes": size,
            "sha256": digest,
            "source": source_path,
            "license": "FTL",
        })

    # The only runtime-open target is FreeType's internal debug hook.  The
    # clean candidate exposes no setter and therefore retains the upstream
    # null default, which deterministically selects the authenticated
    # TT_RunIns fallback at literal 0x005F9504.
    if "library->debug_hooks[FT_DEBUG_HOOK_TRUETYPE]" not in (
        SNAPSHOT / "src/truetype/ttobjs.c"
    ).read_text(errors="replace"):
        raise AdmissionError("TrueType debug-hook policy boundary changed")
    if "(**(code **)(*param_1 + 0x2a0))(param_1)" not in decompiled[0x005F452E]:
        raise AdmissionError("TT_Run_Context indirect callback edge changed")
    if "DAT_005f9504" not in decompiled[0x005F8C6C]:
        raise AdmissionError("TT_RunIns fallback initializer changed")

    opcode_bytes = sum(row["bytes"] for row in opcode_rows)
    support_bytes = sum(row["bytes"] for row in support_rows)
    callback_bytes = sum(row["bytes"] for row in callback_rows)
    if (opcode_bytes, support_bytes, callback_bytes) != (13_458, 1_076, 1_206):
        raise AdmissionError("interpreter byte census changed")
    return {
        "functions": len(opcode_rows) + len(support_rows) + len(callback_rows),
        "bytes": opcode_bytes + support_bytes + callback_bytes,
        "opcode_engine": {
            "functions": len(opcode_rows),
            "bytes": opcode_bytes,
            "direct_main_targets": len(direct_main),
            "transitive_handler_helpers": len(opcode_entries) - 1 - len(direct_main),
            "source_order_mapping_sha256": INTERPRETER_MAPPING_SHA256,
        },
        "support_bodies": support_rows,
        "opcode_bodies": opcode_rows,
        "callback_bodies": callback_rows,
        "callback_edges": pointer_rows,
        "tables": table_rows,
        "policy_boundary": {
            "name": "FT_DEBUG_HOOK_TRUETYPE",
            "candidate_default": "null",
            "fallback": "TT_RunIns",
            "status": "fail-closed; no candidate setter is exposed",
        },
        "unresolved_dispatch_targets": [],
    }


def _verify_sources() -> None:
    provenance = json.loads(PROVENANCE.read_text())
    records = {row["local_path"]: row for row in provenance["files"]}
    sources = (
        {row[4] for row in DRIVER_SURFACE.values()}
        | {row[3] for row in PRIVATE_HELPERS.values()}
        | {"LICENSE"}
    )
    for source in sources:
        if source not in records:
            raise AdmissionError(f"source absent from provenance: {source}")
        if hashlib.sha256((SNAPSHOT / source).read_bytes()).hexdigest() != records[source]["sha256"]:
            raise AdmissionError(f"authenticated source changed: {source}")


def _thumb_bl_targets(body: bytes, address: int) -> set[int]:
    targets: set[int] = set()
    for offset in range(0, len(body) - 3, 2):
        first, second = struct.unpack_from("<HH", body, offset)
        if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
            continue
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
        targets.add((address + offset + 4 + immediate) & 0xFFFFFFFF)
    return targets


def analyze() -> dict[str, object]:
    _verify_sources()
    image = IMAGE.read_bytes()
    if hashlib.sha256(image).hexdigest() != IMAGE_SHA256:
        raise AdmissionError("official image hash changed")
    class_offset = CLASS_ADDRESS - LOAD_BASE
    class_bytes = image[class_offset:class_offset + 96]
    if hashlib.sha256(class_bytes).hexdigest() != CLASS_SHA256:
        raise AdmissionError("tt_driver_class record changed")
    words = struct.unpack("<24I", class_bytes)
    if words[:6] != (0x501, 0x44, 0x0078C7E8, 0x10000, 0x20000, 0):
        raise AdmissionError("TrueType driver class header changed")
    if words[9:12] != (0x340, 0x138, 0xA0):
        raise AdmissionError("TrueType driver object sizes changed")
    if any(words[index] != 0 for index in NULL_DRIVER_SLOTS):
        raise AdmissionError("expected null TrueType class slot became callable")

    driver_source = (SNAPSHOT / "src/truetype/ttdriver.c").read_text(errors="replace")
    declaration = driver_source[driver_source.rfind("FT_DEFINE_DRIVER("):]
    expected_order = [
        "TT_SIZE_SELECT" if class_word == 23 else row[3]
        for class_word, row in sorted(DRIVER_SURFACE.items())
    ]
    cursor = 0
    for symbol in expected_order:
        location = declaration.find(symbol, cursor)
        if location < 0:
            raise AdmissionError(f"TrueType class source order changed: {symbol}")
        cursor = location + len(symbol)

    decompiled = _decompiled_functions()
    admitted = []
    for class_word, (entry, size, digest, symbol, source, prefix) in sorted(DRIVER_SURFACE.items()):
        if words[class_word] != entry | 1:
            raise AdmissionError(f"class pointer changed at word {class_word}: {symbol}")
        body_offset = entry - LOAD_BASE
        body = image[body_offset:body_offset + size]
        if hashlib.sha256(body).hexdigest() != digest:
            raise AdmissionError(f"official body changed: {symbol}")
        if not body.startswith(bytes.fromhex(prefix)):
            raise AdmissionError(f"instruction prefix changed: {symbol}")
        source_text = (SNAPSHOT / source).read_text(errors="replace")
        if re.search(rf"\b{re.escape(symbol)}\s*\(", source_text) is None:
            raise AdmissionError(f"upstream definition missing: {symbol}")
        pins = DECOMPILER_PINS.get(entry)
        if pins is not None:
            stock = decompiled.get(entry, "")
            if not stock or any(pin not in stock for pin in pins):
                raise AdmissionError(f"decompiler semantics changed: {symbol}")
        admitted.append({
            "class_word": class_word,
            "entry": f"0x{entry:08X}",
            "bytes": size,
            "symbol": symbol,
            "source": source,
            "classification": "authenticated-upstream-class-callback",
            "license": "FTL",
            "decompiler_pinned": pins is not None,
        })

    admitted_bytes = sum(row["bytes"] for row in admitted)
    if len(admitted) != 13 or admitted_bytes != 1_188:
        raise AdmissionError("TrueType driver surface census changed")

    for (caller, size), expected_targets in RAW_CALL_EDGES.items():
        caller_offset = caller - LOAD_BASE
        targets = _thumb_bl_targets(image[caller_offset:caller_offset + size], caller)
        if not expected_targets <= targets:
            raise AdmissionError(f"raw TrueType call edge changed: 0x{caller:08X}")

    private = []
    for entry, (size, digest, symbol, source, pins, callers, depth) in sorted(
        PRIVATE_HELPERS.items()
    ):
        body_offset = entry - LOAD_BASE
        body = image[body_offset:body_offset + size]
        if hashlib.sha256(body).hexdigest() != digest:
            raise AdmissionError(f"private helper body changed: {symbol}")
        source_text = (SNAPSHOT / source).read_text(errors="replace")
        if re.search(rf"\b{re.escape(symbol)}\s*\(", source_text) is None:
            raise AdmissionError(f"private upstream definition missing: {symbol}")
        stock = decompiled.get(entry, "")
        if pins and (not stock or any(pin not in stock for pin in pins)):
            raise AdmissionError(f"private helper semantics changed: {symbol}")
        for caller in callers:
            caller_text = decompiled.get(caller, "")
            if f"FUN_{entry:08x}" not in caller_text:
                raise AdmissionError(
                    f"private helper call edge changed: 0x{caller:08X} -> {symbol}"
                )
        private.append({
            "entry": f"0x{entry:08X}",
            "bytes": size,
            "symbol": symbol,
            "source": source,
            "call_depth": depth,
            "classification": "authenticated-upstream-private-helper",
            "license": "FTL",
        })

    private_bytes = sum(row["bytes"] for row in private)
    if len(private) != 74 or private_bytes != 21_900:
        raise AdmissionError("TrueType private-helper tranche changed")
    interpreter = _admit_interpreter_dispatch(image, decompiled)
    return {
        "schema_version": 1,
        "analysis_mode": "read-only; software evidence only",
        "module": "truetype",
        "upstream_version": "2.9.1",
        "class_address": f"0x{CLASS_ADDRESS:08X}",
        "class_callbacks": {"functions": len(admitted), "bytes": admitted_bytes},
        "private_helpers": {"functions": len(private), "bytes": private_bytes},
        "admitted_driver_graph": {
            "functions": len(admitted) + len(private) + interpreter["functions"],
            "bytes": admitted_bytes + private_bytes + interpreter["bytes"],
        },
        "null_class_words": sorted(NULL_DRIVER_SLOTS),
        "callbacks": admitted,
        "helpers": private,
        "interpreter_dispatch": interpreter,
        "private_frontier": [
            {"entry": f"0x{entry:08X}", "expected_identity": identity}
            for entry, identity in sorted(PRIVATE_FRONTIER.items())
        ],
        "limitations": [
            "source admission establishes attributable replacement, not compiler byte identity",
            "the direct and indirect interpreter dispatch frontiers are empty under the fail-closed null debug-hook policy",
            "font payload identities and production linker placement remain outside this software-only admission",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        report = analyze()
    except (AdmissionError, KeyError, OSError, ValueError) as error:
        print(f"FreeType TrueType source admission: FAIL: {error}")
        return 1
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        callbacks = report["class_callbacks"]
        private = report["private_helpers"]
        print("FreeType TrueType source admission: PASS")
        print(f"  driver callbacks: {callbacks['functions']} functions, {callbacks['bytes']} bytes")
        print(f"  private helpers: {private['functions']} functions, {private['bytes']} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
