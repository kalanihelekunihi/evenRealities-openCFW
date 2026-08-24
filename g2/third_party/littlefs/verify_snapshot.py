#!/usr/bin/env python3
"""Offline verification for the pinned littlefs source-equivalent snapshot.

This tool only reads source, provenance, and optional official firmware files.
It never imports or invokes littlefs and cannot format, erase, or mutate an
image or device.
"""

from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
OPENCFW_ROOT = HERE.parents[1]
PROVENANCE_PATH = HERE / "PROVENANCE.json"

EXPECTED_REPOSITORY = "https://github.com/littlefs-project/littlefs.git"
EXPECTED_REF = "refs/tags/v2.10.1"
EXPECTED_TAG = "v2.10.1"
EXPECTED_COMMIT = "0494ce7169f06a734a7bd7585f49a9fa91fa7318"
EXPECTED_TREE = "06dd0162169d3cb550cd24a3e34d0e4d02983ad3"

EXPECTED_FILES = {
    "lfs.c": {
        "size": 196753,
        "sha256": "81a209e8551754d13b24fc0a2b6707fb3b2475e14feba00bf0df722b98a31398",
        "git_blob_sha1": "7520f2ea7eb1d3d29ab29422ca3d6d0a3057397a",
    },
    "lfs.h": {
        "size": 26439,
        "sha256": "ee44e99d6b19119b3e577b969b80c9d5e6f96410c9593794afddf6d4b314c486",
        "git_blob_sha1": "45315603e4498249266b78bbaff540520ef10429",
    },
    "lfs_util.c": {
        "size": 988,
        "sha256": "f2fbde533670560434bd9f5a547174cc7c5a4670a02c47b4bd85180dced8b2ec",
        "git_blob_sha1": "dac72abc3c101dc720727d3379723548d46dae1e",
    },
    "lfs_util.h": {
        "size": 7954,
        "sha256": "f5d249326646c818e62af3cefefe8a57e7b484446a0f48d1050b95e60925088e",
        "git_blob_sha1": "0aec48855359df6e39d2f5bb3c45ca22b4a28811",
    },
    "LICENSE.md": {
        "size": 1523,
        "sha256": "0cb4ff1daf5fdc1359c6a6ee3116092f08fc100c9d58b1b77ab17bfd801f856d",
        "git_blob_sha1": "e6c3a7bac1d8b3ed2ff3160a5bb49abebdd6fe7e",
    },
}

EXPECTED_PRODUCTION_SOURCE_PATHS = (
    "components/apollo_main/core_overlay/runtime_littlefs_file_tell_private.c",
    "components/apollo_main/core_overlay/runtime_littlefs_scmp.c",
    "components/apollo_main/core_overlay/runtime_littlefs_alloc_ckpoint.c",
    "components/apollo_main/core_overlay/runtime_littlefs_alloc_drop.c",
    "components/apollo_main/core_overlay/runtime_littlefs_disk_version.c",
    "components/apollo_main/core_overlay/runtime_littlefs_mlist_append.c",
    "components/apollo_main/core_overlay/runtime_littlefs_mlist_remove.c",
    "components/apollo_main/core_overlay/runtime_littlefs_util.c",
    "components/apollo_main/core_overlay/runtime_littlefs_util_bitops.c",
    "components/apollo_main/core_overlay/runtime_littlefs_mlist_isopen.c",
    "components/apollo_main/core_overlay/runtime_littlefs_util_endian.c",
    "components/apollo_main/core_overlay/runtime_littlefs_disk_version_parts.c",
    "components/apollo_main/core_overlay/runtime_littlefs_alloc_lookahead.c",
    "components/apollo_main/core_overlay/runtime_littlefs_file_size_private.c",
    "components/apollo_main/core_overlay/runtime_littlefs_file_size_private.h",
    "components/apollo_main/core_overlay/runtime_littlefs_file_rewind_private.c",
    "components/apollo_main/core_overlay/runtime_littlefs_file_rewind_private.h",
    "components/bootloader/core_overlay/runtime_littlefs_scmp.c",
    "components/bootloader/core_overlay/runtime_littlefs_alloc_ckpoint.c",
    "components/bootloader/core_overlay/runtime_littlefs_alloc_drop.c",
    "components/shared/littlefs/runtime_littlefs_tag_type2.c",
    "components/shared/littlefs/runtime_littlefs_tag_type2.h",
    "components/shared/littlefs/runtime_littlefs_tag_chunk.c",
    "components/shared/littlefs/runtime_littlefs_tag_chunk.h",
    "components/shared/littlefs/runtime_littlefs_tag_isvalid.c",
    "components/shared/littlefs/runtime_littlefs_tag_isvalid.h",
    "components/shared/littlefs/runtime_littlefs_tag_type1.c",
    "components/shared/littlefs/runtime_littlefs_tag_type1.h",
    "components/shared/littlefs/runtime_littlefs_tag_type3.c",
    "components/shared/littlefs/runtime_littlefs_tag_type3.h",
    "components/shared/littlefs/runtime_littlefs_tag_id.c",
    "components/shared/littlefs/runtime_littlefs_tag_id.h",
    "components/shared/littlefs/runtime_littlefs_tag_size.c",
    "components/shared/littlefs/runtime_littlefs_tag_size.h",
    "components/apollo_main/core_overlay/runtime_littlefs_file_size_public.c",
)

EXPECTED_PRODUCTION_SYMBOLS = (
    "open_cfw_littlefs_file_tell_private",
    "open_cfw_littlefs_scmp",
    "open_cfw_littlefs_alloc_ckpoint",
    "open_cfw_littlefs_alloc_drop",
    "open_cfw_littlefs_disk_version",
    "open_cfw_littlefs_mlist_append",
    "open_cfw_littlefs_mlist_remove",
    "open_cfw_littlefs_util_max",
    "open_cfw_littlefs_util_min",
    "open_cfw_littlefs_util_aligndown",
    "open_cfw_littlefs_util_alignup",
    "open_cfw_littlefs_util_npw2",
    "open_cfw_littlefs_util_ctz",
    "open_cfw_littlefs_util_popc",
    "open_cfw_littlefs_mlist_isopen",
    "open_cfw_littlefs_util_fromle32",
    "open_cfw_littlefs_util_tole32",
    "open_cfw_littlefs_util_frombe32",
    "open_cfw_littlefs_util_tobe32",
    "open_cfw_littlefs_disk_version_major",
    "open_cfw_littlefs_disk_version_minor",
    "open_cfw_littlefs_alloc_lookahead",
    "open_cfw_littlefs_file_size_private",
    "open_cfw_littlefs_file_rewind_private",
    "open_cfw_littlefs_tag_type2",
    "open_cfw_littlefs_tag_chunk",
    "open_cfw_littlefs_tag_isvalid",
    "open_cfw_littlefs_tag_type1",
    "open_cfw_littlefs_tag_type3",
    "open_cfw_littlefs_tag_id",
    "open_cfw_littlefs_tag_size",
    "open_cfw_littlefs_file_size_public",
)

EXPECTED_OVERLAY_PRODUCTION_PATHS = {
    "components/apollo_main/core_overlay/overlay.json": {
        *EXPECTED_PRODUCTION_SOURCE_PATHS[:14],
        EXPECTED_PRODUCTION_SOURCE_PATHS[15],
        EXPECTED_PRODUCTION_SOURCE_PATHS[20],
        EXPECTED_PRODUCTION_SOURCE_PATHS[22],
        EXPECTED_PRODUCTION_SOURCE_PATHS[24],
        EXPECTED_PRODUCTION_SOURCE_PATHS[26],
        EXPECTED_PRODUCTION_SOURCE_PATHS[28],
        EXPECTED_PRODUCTION_SOURCE_PATHS[30],
        EXPECTED_PRODUCTION_SOURCE_PATHS[32],
        EXPECTED_PRODUCTION_SOURCE_PATHS[34],
    },
    "components/bootloader/core_overlay/overlay.json": {
        *EXPECTED_PRODUCTION_SOURCE_PATHS[4:13],
        *EXPECTED_PRODUCTION_SOURCE_PATHS[17:20],
        EXPECTED_PRODUCTION_SOURCE_PATHS[22],
        EXPECTED_PRODUCTION_SOURCE_PATHS[24],
        EXPECTED_PRODUCTION_SOURCE_PATHS[26],
        EXPECTED_PRODUCTION_SOURCE_PATHS[28],
        EXPECTED_PRODUCTION_SOURCE_PATHS[30],
        EXPECTED_PRODUCTION_SOURCE_PATHS[32],
    },
}

EXPECTED_OVERLAY_PRODUCTION_SYMBOLS = {
    "components/apollo_main/core_overlay/overlay.json": set(
        EXPECTED_PRODUCTION_SYMBOLS
    ),
    "components/bootloader/core_overlay/overlay.json": set(
        EXPECTED_PRODUCTION_SYMBOLS[1:22]
    ) | set(EXPECTED_PRODUCTION_SYMBOLS[25:31]),
}

EXPECTED_REWIND_UPSTREAM = {
    "offset": 118157,
    "size": 192,
    "sha256": "74638292061613417c2ce7c6bbed200d2bee046c35a7a835fb4d9bb183ab755a",
}
EXPECTED_REWIND_SOURCE = {
    "path": "components/apollo_main/core_overlay/runtime_littlefs_file_rewind_private.c",
    "size": 1239,
    "sha256": "e6afb5b67671b3219971b19c20290c601568752d814064147f5ccd4118f5acc8",
}
EXPECTED_REWIND_HEADER = {
    "path": "components/apollo_main/core_overlay/runtime_littlefs_file_rewind_private.h",
    "size": 1743,
    "sha256": "7430dcd1ad1ea3973d619f2d67d8d8b11a688018d48a3bc26a40e407d1fedb56",
}
EXPECTED_REWIND_STOCK = {
    "start": 0x004CE460,
    "end": 0x004CE472,
    "size": 18,
    "sha256": "be02691b2e7339d7dd1d54b31712c3e8563e5a86f4406a469888640fad9435cd",
    "seek_seam": 0x004CE3BC,
}
EXPECTED_OVERLAY_RUNTIME_ADDRESS = 0x00794324
EXPECTED_REWIND_RELOCATION = {
    "offset": 6,
    "type": "R_ARM_THM_CALL",
    "symbol": "open_cfw_littlefs_file_seek_private",
    "symbol_type": "STT_NOTYPE",
    "target_address": EXPECTED_REWIND_STOCK["seek_seam"],
}
EXPECTED_REWIND_PROFILES = {
    "apple-clang": {
        "size": 16,
        "offset": 124480,
        "runtime_address": 0x007B2964,
        "sha256": "1c2e2b1fded0de515345b90fe34de51a9c0f08a02a5ad983c1120481c51c5783",
        "unrelocated_sha256": "46e8bab056ad39ced45edb5da2612f6470674ab5a428df7f08822f6c2d9e184b",
    },
    "linux-clang": {
        "size": 16,
        "offset": 126300,
        "runtime_address": 0x007B3080,
        "sha256": "9731cbf3ff15be31186591ed148d009ae8985cb18bdfca3ba365aeb0897e3fd1",
        "unrelocated_sha256": "46e8bab056ad39ced45edb5da2612f6470674ab5a428df7f08822f6c2d9e184b",
    },
}

EXPECTED_TAG_TYPE2_UPSTREAM = {
    "offset": 10326,
    "size": 92,
    "sha256": "65f614cf5ed7152f7ad2176547453c329b1f15442e550ef6632b0f7773970f78",
}
EXPECTED_TAG_TYPE2_SOURCE = {
    "path": "components/shared/littlefs/runtime_littlefs_tag_type2.c",
    "size": 789,
    "sha256": "c2ea0965e62aa126fb4b8e752526b8a926a9088739811cba09dcf7d1ed6f3940",
}
EXPECTED_TAG_TYPE2_HEADER = {
    "path": "components/shared/littlefs/runtime_littlefs_tag_type2.h",
    "size": 883,
    "sha256": "17915b900db79e3e611379645a8780723410e5c826f6bfa7619d86bac28f0b13",
}
EXPECTED_TAG_TYPE2_STOCK = {
    "start": 0x004CAE90,
    "end": 0x004CAE98,
    "size": 8,
    "sha256": "a017094f8fc58d202d8c5a588f66dd319248578fa39e0f392ba3c7857d3500ef",
    "callers": (
        (0x004CBB26, "fff7b3f9"),
        (0x004CBC38, "fff72af9"),
    ),
}
EXPECTED_TAG_TYPE2_PROFILES = {
    "apple-clang": {
        "size": 10,
        "offset": 124548,
        "runtime_address": 0x007B29A8,
        "sha256": "88be40d05d37142bf0bae8306026d8c405a4f8f441aabd87ee6731557d4149fd",
    },
    "linux-clang": {
        "size": 10,
        "offset": 126368,
        "runtime_address": 0x007B30C4,
        "sha256": "88be40d05d37142bf0bae8306026d8c405a4f8f441aabd87ee6731557d4149fd",
    },
}

EXPECTED_TAG_CHUNK_UPSTREAM = {
    "offset": 10514,
    "size": 93,
    "sha256": "406b74c2d10482c959cf1048d9589d00d8b416ee4661203bd339144baa74cd09",
}
EXPECTED_TAG_CHUNK_TYPEDEF = {
    "offset": 9602,
    "size": 27,
    "sha256": "cb4dcd6212b1a269371d86dddf98ed74853e2eb43753c5d8f8659abbca167ce2",
}
EXPECTED_TAG_CHUNK_SOURCE = {
    "path": "components/shared/littlefs/runtime_littlefs_tag_chunk.c",
    "size": 773,
    "sha256": "71851bd05e26e703b8697b9994b556db46511c37e9500da98e3406b37a92c8da",
}
EXPECTED_TAG_CHUNK_HEADER = {
    "path": "components/shared/littlefs/runtime_littlefs_tag_chunk.h",
    "size": 879,
    "sha256": "1061f5d68ff6f81a6f1853bfefe37b77f5f3b8b09e627b1bfa0d191842d1f6f5",
}
EXPECTED_TAG_CHUNK_TEXT_SHA256 = (
    "db1dfda72afb267e96cd4e11eaf5d44659195b0afecbdcd8ed8572c34049df74"
)
EXPECTED_TAG_CHUNK_STOCK = {
    "size": 6,
    "sha256": "63fc572597119c756fa5d4ee0904c8c34dfa545495b77bba02e2ff3298ce23ae",
    "apollo_main": {
        "start": 0x004CAEA0,
        "end": 0x004CAEA6,
        "file_offset": 601792,
        "callers": (
            (0x004CAEA8, "fff7faff"),
            (0x004CBB68, "fff79af9"),
            (0x004CBD1E, "fff7bff8"),
            (0x004CCBC4, "fef76cf9"),
        ),
    },
    "apollo_bootloader": {
        "start": 0x00410BA8,
        "end": 0x00410BAE,
        "file_offset": 2984,
        "callers": (
            (0x00410BB0, "fff7faff"),
            (0x00411870, "fff79af9"),
            (0x00411A26, "fff7bff8"),
            (0x004127C8, "fef7eef9"),
        ),
    },
}

EXPECTED_DUAL_TAG_LEAVES = {
    "tag_isvalid_leaf": {
        "function": "open_cfw_littlefs_tag_isvalid",
        "upstream_function": "lfs_tag_isvalid",
        "upstream": {
            "offset": 10042,
            "size": 87,
            "sha256": "bb8e571d6dbddd1fe446ec7b4838979a4ab9bd6d6184e2f8d9b6c00cc0835b13",
            "definition": (
                b"static inline bool lfs_tag_isvalid(lfs_tag_t tag) {\n"
                b"    return !(tag & 0x80000000);\n"
                b"}\n\n"
            ),
        },
        "source": {
            "path": "components/shared/littlefs/runtime_littlefs_tag_isvalid.c",
            "size": 848,
            "sha256": "a91417d6193cdfb9589cd9e62f9b6eebe65e1e11a75ca36d0f42d85c36d907a2",
        },
        "header": {
            "path": "components/shared/littlefs/runtime_littlefs_tag_isvalid.h",
            "size": 928,
            "sha256": "6efcd1b229fb0477285f8fbdfbc6f1c92701a787fb17995a6115bfa5a944c6cd",
        },
        "leaf_size": 6,
        "text_sha256": "65e477818b1c6002b2ceb88812da258524e438ded36dfa059e034c3bce19624e",
        "stock": {
            "size": 10,
            "sha256": "0249b2c9c987097c7c0e628917a7dd6b67d4d1ee24f64339a7e0dd11977e4c9e",
            "apollo_main": {
                "start": 0x004CAE6A,
                "end": 0x004CAE74,
                "file_offset": 601738,
                "callers": (
                    (0x004CBB06, "fff7b0f9"),
                    (0x004CBE92, "fef7eaff"),
                    (0x004CF230, "fbf71bfe"),
                ),
            },
            "apollo_bootloader": {
                "start": 0x00410B72,
                "end": 0x00410B7C,
                "file_offset": 2930,
                "callers": (
                    (0x0041180E, "fff7b0f9"),
                    (0x00411B9A, "fef7eaff"),
                    (0x00414908, "fcf733f9"),
                ),
            },
        },
        "profiles": {
            "apple-clang": {
                "apollo_main": (124568, 0x007B29BC),
                "apollo_bootloader": (628, 0x004346EC),
            },
            "linux-clang": {
                "apollo_main": (126388, 0x007B30D8),
                "apollo_bootloader": (628, 0x004346EC),
            },
        },
    },
    "tag_type1_leaf": {
        "function": "open_cfw_littlefs_tag_type1",
        "upstream_function": "lfs_tag_type1",
        "upstream": {
            "offset": 10232,
            "size": 94,
            "sha256": "ebf0229d6e0f78175c43641b09906fea19575fc3f34ac8862ae60159df1ec743",
            "definition": (
                b"static inline uint16_t lfs_tag_type1(lfs_tag_t tag) {\n"
                b"    return (tag & 0x70000000) >> 20;\n"
                b"}\n\n"
            ),
        },
        "source": {
            "path": "components/shared/littlefs/runtime_littlefs_tag_type1.c",
            "size": 857,
            "sha256": "7c0df44bd2ebce1eae4cacbfa174c0f963dd03dcc5719ab386c0400201357b46",
        },
        "header": {
            "path": "components/shared/littlefs/runtime_littlefs_tag_type1.h",
            "size": 893,
            "sha256": "0993093546ead7b159179c7aaebbef926be24b39ca5202d04b17f0569ca830f6",
        },
        "leaf_size": 10,
        "text_sha256": "079f868da6ae04c0d4ace93e9e9d9132247224f81903b57fba51d407f49ddfcf",
        "stock": {
            "size": 8,
            "sha256": "fc26e04a6784b91dc07f170f8a3bd23096f7caa92c15430a179edf215b509fdd",
            "apollo_main": {
                "start": 0x004CAE88,
                "end": 0x004CAE90,
                "file_offset": 601768,
                "callers": (
                    (0x004CAF32, "fff7a9ff"),
                    (0x004CAF64, "fff790ff"),
                    (0x004CB2F0, "fff7cafd"),
                    (0x004CB560, "fff792fc"),
                    (0x004CBC94, "fff7f8f8"),
                    (0x004CBCBA, "fff7e5f8"),
                    (0x004CBD12, "fff7b9f8"),
                    (0x004CCBA2, "fef771f9"),
                ),
            },
            "apollo_bootloader": {
                "start": 0x00410B90,
                "end": 0x00410B98,
                "file_offset": 2960,
                "callers": (
                    (0x00410C3A, "fff7a9ff"),
                    (0x00410C6C, "fff790ff"),
                    (0x00410FF8, "fff7cafd"),
                    (0x00411268, "fff792fc"),
                    (0x0041199C, "fff7f8f8"),
                    (0x004119C2, "fff7e5f8"),
                    (0x00411A1A, "fff7b9f8"),
                    (0x004127A6, "fef7f3f9"),
                ),
            },
        },
        "profiles": {
            "apple-clang": {
                "apollo_main": (124576, 0x007B29C4),
                "apollo_bootloader": (634, 0x004346F2),
            },
            "linux-clang": {
                "apollo_main": (126396, 0x007B30E0),
                "apollo_bootloader": (634, 0x004346F2),
            },
        },
    },
    "tag_type3_leaf": {
        "function": "open_cfw_littlefs_tag_type3",
        "upstream_function": "lfs_tag_type3",
        "upstream": {
            "offset": 10420,
            "size": 94,
            "sha256": "3cc2c9ec46ebb7fc3d3d71c6b39b235a5da0cde23adf2c182cafd24d6410b53e",
            "definition": (
                b"static inline uint16_t lfs_tag_type3(lfs_tag_t tag) {\n"
                b"    return (tag & 0x7ff00000) >> 20;\n"
                b"}\n\n"
            ),
        },
        "source": {
            "path": "components/shared/littlefs/runtime_littlefs_tag_type3.c",
            "size": 857,
            "sha256": "6940b4ac0622dc1f2b84a0c663dc1522dfc7b198f59d6f452828adfd299e37c8",
        },
        "header": {
            "path": "components/shared/littlefs/runtime_littlefs_tag_type3.h",
            "size": 893,
            "sha256": "4e3b70d5ad8e8fce0e5dc2bd43fc8459c62c742d84a93f949bf0dd4fb44fe869",
        },
        "leaf_size": 6,
        "text_sha256": "a6781f0a92086cca25476ca00824d8f0fd736ac7d800aa9e3f6e4d6544490921",
        "stock": {
            "size": 8,
            "sha256": "818012c47ba81ee18e2996d51a8a29a96a78ced50854b6fefcebf92e7b9ed9d6",
            "apollo_main": {
                "start": 0x004CAE98,
                "end": 0x004CAEA0,
                "file_offset": 601784,
                "callers": (
                    (0x004CB70A, "fff7c5fb"),
                    (0x004CB716, "fff7bffb"),
                    (0x004CB7C0, "fff76afb"),
                    (0x004CBD5E, "fff79bf8"),
                    (0x004CBF82, "fef789ff"),
                    (0x004CBFB2, "fef771ff"),
                    (0x004CBFC6, "fef767ff"),
                    (0x004CC07E, "fef70bff"),
                    (0x004CC12E, "fef7b3fe"),
                    (0x004CCBDC, "fef75cf9"),
                    (0x004CCC18, "fef73ef9"),
                    (0x004CCE72, "fef711f8"),
                    (0x004CCEB2, "fdf7f1ff"),
                    (0x004CCEF8, "fdf7ceff"),
                    (0x004CD57A, "fdf78dfc"),
                    (0x004CDB46, "fdf7a7f9"),
                    (0x004CDC4C, "fdf724f9"),
                    (0x004CE4B6, "fcf7effc"),
                    (0x004CE520, "fcf7bafc"),
                    (0x004CE5C8, "fcf766fc"),
                    (0x004CE6C6, "fcf7e7fb"),
                    (0x004CE702, "fcf7c9fb"),
                    (0x004CE70A, "fcf7c5fb"),
                    (0x004CE718, "fcf7befb"),
                    (0x004CE746, "fcf7a7fb"),
                    (0x004CE802, "fcf749fb"),
                    (0x004CE8CA, "fcf7e5fa"),
                    (0x004CF346, "fbf7a7fd"),
                    (0x004CF376, "fbf78ffd"),
                    (0x004CF726, "fbf7b7fb"),
                ),
            },
            "apollo_bootloader": {
                "start": 0x00410BA0,
                "end": 0x00410BA8,
                "file_offset": 2976,
                "callers": (
                    (0x00411412, "fff7c5fb"),
                    (0x0041141E, "fff7bffb"),
                    (0x004114C8, "fff76afb"),
                    (0x00411A66, "fff79bf8"),
                    (0x00411CDE, "fef75fff"),
                    (0x00411D8E, "fef707ff"),
                    (0x004127E0, "fef7def9"),
                    (0x0041281C, "fef7c0f9"),
                    (0x00412A76, "fef793f8"),
                    (0x00412AB6, "fef773f8"),
                    (0x00412AFC, "fef750f8"),
                    (0x0041317E, "fdf70ffd"),
                    (0x00413696, "fdf783fa"),
                    (0x0041379C, "fdf700fa"),
                    (0x00414A16, "fcf7c3f8"),
                    (0x00414A46, "fcf7abf8"),
                    (0x00414DF6, "fbf7d3fe"),
                ),
            },
        },
        "profiles": {
            "apple-clang": {
                "apollo_main": (124588, 0x007B29D0),
                "apollo_bootloader": (644, 0x004346FC),
            },
            "linux-clang": {
                "apollo_main": (126408, 0x007B30EC),
                "apollo_bootloader": (644, 0x004346FC),
            },
        },
    },
    "tag_id_leaf": {
        "function": "open_cfw_littlefs_tag_id",
        "upstream_function": "lfs_tag_id",
        "upstream": {
            "offset": 10702,
            "size": 91,
            "sha256": "50140c563689852013dfad180ec3b6464c6b6c5b22854f5492d63cf5de57fbe2",
            "definition": (
                b"static inline uint16_t lfs_tag_id(lfs_tag_t tag) {\n"
                b"    return (tag & 0x000ffc00) >> 10;\n"
                b"}\n\n"
            ),
        },
        "source": {
            "path": "components/shared/littlefs/runtime_littlefs_tag_id.c",
            "size": 845,
            "sha256": "5b6c3ce0f4236d6c6bc0a12891e41929e9034a7ddc2f68bd4f6a1d5d4fa07638",
        },
        "header": {
            "path": "components/shared/littlefs/runtime_littlefs_tag_id.h",
            "size": 872,
            "sha256": "5d6d1c5df9a0fb31f80ad0f6a876795cb154b039fa72df17c615b38cd5e2099e",
        },
        "leaf_size": 6,
        "text_sha256": "6194594e24288e708887a0e938b2a54401c8c732210d91af7a5927d03bd3604c",
        "stock": {
            "size": 8,
            "sha256": "0843abb3e9ef39afac8e69ae1e181efa0b5b5c8ebf53e20844b53fdf245b1036",
            "apollo_main": {
                "start": 0x004CAEB0,
                "end": 0x004CAEB8,
                "file_offset": 601808,
                "callers": (
                    (0x004CB262, "fff725fe"),
                    (0x004CB26C, "fff720fe"),
                    (0x004CB274, "fff71cfe"),
                    (0x004CB286, "fff713fe"),
                    (0x004CB28E, "fff70ffe"),
                    (0x004CB2E6, "fff7e3fd"),
                    (0x004CB2FE, "fff7d7fd"),
                    (0x004CB306, "fff7d3fd"),
                    (0x004CB56C, "fff7a0fc"),
                    (0x004CB574, "fff79cfc"),
                    (0x004CB64A, "fff731fc"),
                    (0x004CB786, "fff793fb"),
                    (0x004CB7EA, "fff761fb"),
                    (0x004CB92A, "fff7c1fa"),
                    (0x004CB936, "fff7bbfa"),
                    (0x004CB944, "fff7b4fa"),
                    (0x004CBC9E, "fff707f9"),
                    (0x004CBCAC, "fff700f9"),
                    (0x004CBCEE, "fff7dff8"),
                    (0x004CBCF8, "fff7daf8"),
                    (0x004CBDF8, "fff75af8"),
                    (0x004CBE02, "fff755f8"),
                    (0x004CBE3A, "fff739f8"),
                    (0x004CBE42, "fff735f8"),
                    (0x004CBE60, "fff726f8"),
                    (0x004CBE68, "fff722f8"),
                    (0x004CBE82, "fff715f8"),
                    (0x004CBEA0, "fff706f8"),
                    (0x004CC138, "fef7bafe"),
                    (0x004CC146, "fef7b3fe"),
                    (0x004CCE82, "fef715f8"),
                    (0x004CCEBE, "fdf7f7ff"),
                    (0x004CCF04, "fdf7d4ff"),
                    (0x004CD184, "fdf794fe"),
                    (0x004CD1B6, "fdf77bfe"),
                    (0x004CD2A8, "fdf702fe"),
                    (0x004CD58A, "fdf791fc"),
                    (0x004CD5A2, "fdf785fc"),
                    (0x004CE4C6, "fcf7f3fc"),
                    (0x004CE502, "fcf7d5fc"),
                    (0x004CE52A, "fcf7c1fc"),
                    (0x004CE59E, "fcf787fc"),
                    (0x004CE63C, "fcf738fc"),
                    (0x004CE66A, "fcf721fc"),
                    (0x004CE6A8, "fcf702fc"),
                    (0x004CE82C, "fcf740fb"),
                    (0x004CE89C, "fcf708fb"),
                    (0x004CF700, "fbf7d6fb"),
                    (0x004CF756, "fbf7abfb"),
                    (0x004CF894, "fbf70cfb"),
                ),
            },
            "apollo_bootloader": {
                "start": 0x00410BB8,
                "end": 0x00410BC0,
                "file_offset": 3000,
                "callers": (
                    (0x00410F6A, "fff725fe"),
                    (0x00410F74, "fff720fe"),
                    (0x00410F7C, "fff71cfe"),
                    (0x00410F8E, "fff713fe"),
                    (0x00410F96, "fff70ffe"),
                    (0x00410FEE, "fff7e3fd"),
                    (0x00411006, "fff7d7fd"),
                    (0x0041100E, "fff7d3fd"),
                    (0x00411274, "fff7a0fc"),
                    (0x0041127C, "fff79cfc"),
                    (0x00411352, "fff731fc"),
                    (0x0041148E, "fff793fb"),
                    (0x004114F2, "fff761fb"),
                    (0x00411632, "fff7c1fa"),
                    (0x0041163E, "fff7bbfa"),
                    (0x0041164C, "fff7b4fa"),
                    (0x004119A6, "fff707f9"),
                    (0x004119B4, "fff700f9"),
                    (0x004119F6, "fff7dff8"),
                    (0x00411A00, "fff7daf8"),
                    (0x00411B00, "fff75af8"),
                    (0x00411B0A, "fff755f8"),
                    (0x00411B42, "fff739f8"),
                    (0x00411B4A, "fff735f8"),
                    (0x00411B68, "fff726f8"),
                    (0x00411B70, "fff722f8"),
                    (0x00411B8A, "fff715f8"),
                    (0x00411BA8, "fff706f8"),
                    (0x00411D98, "fef70eff"),
                    (0x00411DA6, "fef707ff"),
                    (0x00412A86, "fef797f8"),
                    (0x00412AC2, "fef779f8"),
                    (0x00412B08, "fef756f8"),
                    (0x00412D88, "fdf716ff"),
                    (0x00412DBA, "fdf7fdfe"),
                    (0x00412EAC, "fdf784fe"),
                    (0x0041318E, "fdf713fd"),
                    (0x004131A6, "fdf707fd"),
                    (0x00414DD0, "fbf7f2fe"),
                    (0x00414E26, "fbf7c7fe"),
                    (0x00414F64, "fbf728fe"),
                ),
            },
        },
        "profiles": {
            "apple-clang": {
                "apollo_main": (124596, 0x007B29D8),
                "apollo_bootloader": (650, 0x00434702),
            },
            "linux-clang": {
                "apollo_main": (126416, 0x007B30F4),
                "apollo_bootloader": (650, 0x00434702),
            },
        },
    },
    "tag_size_leaf": {
        "function": "open_cfw_littlefs_tag_size",
        "upstream_function": "lfs_tag_size",
        "upstream": {
            "offset": 10793,
            "size": 87,
            "sha256": "9df85bc43ca9f90ef58c425c5fd9bbbbf53585093be5fad0cc580fc88814ea5c",
            "definition": (
                b"static inline lfs_size_t lfs_tag_size(lfs_tag_t tag) {\n"
                b"    return tag & 0x000003ff;\n"
                b"}\n\n"
            ),
        },
        "source": {
            "path": "components/shared/littlefs/runtime_littlefs_tag_size.c",
            "size": 854,
            "sha256": "533bbfcbfc2440e02b79692a2a7ccff87c3cb62cbb0788c1d5bf806fd3bca849",
        },
        "header": {
            "path": "components/shared/littlefs/runtime_littlefs_tag_size.h",
            "size": 1000,
            "sha256": "0f29febdc25b081de1821a41c9065870c02154375985bf648d8e1b63f6cc3528",
        },
        "leaf_size": 6,
        "text_sha256": "35890ebcdee5cb7f51b3e8d874201b7e0214f6111eebe56c772133f259cf9b54",
        "stock": {
            "size": 6,
            "sha256": "8596106584e598a657aea7fdd2e1156a748158d2d63d9c121c92587fabbdf8ca",
            "apollo_main": {
                "start": 0x004CAEB8,
                "end": 0x004CAEBE,
                "file_offset": 601816,
                "callers": (
                    (0x004CAECC, "fff7f4ff"),
                    (0x004CAF10, "fff7d2ff"),
                    (0x004CAF26, "fff7c7ff"),
                    (0x004CAF48, "fff7b6ff"),
                    (0x004CB368, "fff7a6fd"),
                    (0x004CB3D4, "fff770fd"),
                    (0x004CB77E, "fff79bfb"),
                    (0x004CB7DA, "fff76dfb"),
                    (0x004CBFD4, "fef770ff"),
                    (0x004CBFFA, "fef75dff"),
                    (0x004CC026, "fef747ff"),
                    (0x004CC032, "fef741ff"),
                    (0x004CDC5C, "fdf72cf9"),
                    (0x004CF578, "fbf79efc"),
                    (0x004CF59E, "fbf78bfc"),
                ),
            },
            "apollo_bootloader": {
                "start": 0x00410BC0,
                "end": 0x00410BC6,
                "file_offset": 3008,
                "callers": (
                    (0x00410BD4, "fff7f4ff"),
                    (0x00410C18, "fff7d2ff"),
                    (0x00410C2E, "fff7c7ff"),
                    (0x00410C50, "fff7b6ff"),
                    (0x00411070, "fff7a6fd"),
                    (0x004110DC, "fff770fd"),
                    (0x00411486, "fff79bfb"),
                    (0x004114E2, "fff76dfb"),
                    (0x00411C5A, "fef7b1ff"),
                    (0x00411C86, "fef79bff"),
                    (0x00411C92, "fef795ff"),
                    (0x004137AC, "fdf708fa"),
                    (0x00414C48, "fbf7baff"),
                    (0x00414C6E, "fbf7a7ff"),
                ),
            },
        },
        "profiles": {
            "apple-clang": {
                "apollo_main": (124604, 0x007B29E0),
                "apollo_bootloader": (656, 0x00434708),
            },
            "linux-clang": {
                "apollo_main": (126424, 0x007B30FC),
                "apollo_bootloader": (656, 0x00434708),
            },
        },
    },
}

EXPECTED_TAG_ID_MANIFEST_REGIONS = {
    "apollo_main": (
        (
            "opaque_between_littlefs_tag_chunk_and_littlefs_tag_id",
            601798,
            10,
            0x004CAEA6,
            "official_blob",
        ),
        (
            "littlefs_tag_id_source_replacement",
            601808,
            8,
            0x004CAEB0,
            "generated_source_entry_replacement",
        ),
        (
            "littlefs_tag_size_source_replacement",
            601816,
            6,
            0x004CAEB8,
            "generated_source_entry_replacement",
        ),
        (
            "opaque_between_littlefs_tag_size_and_littlefs_mlist_isopen",
            601822,
            452,
            0x004CAEBE,
            "official_blob",
        ),
        (
            "apollo_littlefs_tag_id_source_alignment",
            3647990,
            2,
            0x007B29D6,
            "generated_alignment",
        ),
        (
            "apollo_littlefs_tag_id_source_leaf",
            3647992,
            6,
            0x007B29D8,
            "source_compiled",
        ),
        (
            "apollo_littlefs_tag_size_source_alignment",
            3647998,
            2,
            0x007B29DE,
            "generated_alignment",
        ),
        (
            "apollo_littlefs_tag_size_source_leaf",
            3648000,
            6,
            0x007B29E0,
            "source_compiled",
        ),
    ),
    "apollo_bootloader": (
        (
            "bootloader_opaque_between_littlefs_tag_chunk_and_tag_id",
            2990,
            10,
            0x00410BAE,
            "official_blob",
        ),
        (
            "bootloader_littlefs_tag_id_source_replacement",
            3000,
            8,
            0x00410BB8,
            "generated_source_entry_replacement",
        ),
        (
            "bootloader_littlefs_tag_size_source_replacement",
            3008,
            6,
            0x00410BC0,
            "generated_source_entry_replacement",
        ),
        (
            "bootloader_opaque_between_littlefs_tag_size_and_mlist_isopen",
            3014,
            452,
            0x00410BC6,
            "official_blob",
        ),
        (
            "bootloader_littlefs_tag_id_source_leaf",
            149250,
            6,
            0x00434702,
            "source_compiled",
        ),
        (
            "bootloader_littlefs_tag_size_source_leaf",
            149256,
            6,
            0x00434708,
            "source_compiled",
        ),
    ),
}

EXPECTED_TAG_ID_MANIFEST_PROVIDERS = {
    "apollo_main": {
        "kind": "source_build",
        "path": "components/apollo_main/core_overlay/build/ota_s200_firmware_ota.bin",
        "size": 3764088,
        "sha256": "b3ee7d2fb560f134bd5c4a27eb8203abdc0dd9482816319be0b03320fc2067ed",
        "profiles": {
            "linux-clang": {
                "size": 3668604,
                "sha256": "378c868e151060a59ab91b0de1a722e8678b8e1da8eede248c5702ccf8902798",
            },
        },
    },
    "apollo_bootloader": {
        "kind": "source_build",
        "path": "components/bootloader/core_overlay/build/ota_s200_bootloader.bin",
        "size": 149262,
        "sha256": "695688b7cc4d9583e9e5c854db44980acab9a58d367bc7e02fa5e51eb00e3267",
        "profiles": {
            "linux-clang": {
                "size": 149262,
                "sha256": "fc3d07c8a59e1c33f26965cdb1888114412c3ca671d6137f7c3166acc81c8d74",
            },
        },
    },
}

EXPECTED_SUBTREE_FILES = {
    ".gitattributes",
    "LICENSE.md",
    "PROVENANCE.json",
    "README.openCFW.md",
    "lfs.c",
    "lfs.h",
    "lfs_util.c",
    "lfs_util.h",
    "verify_snapshot.py",
}

EXPECTED_COMMON_CONFIG_WORDS = (
    16,    # read_size
    256,   # prog_size
    4096,  # block_size
    3008,  # block_count
    500,   # block_cycles
    4096,  # cache_size
    256,   # lookahead_size
    0,     # compact_thresh
    0,     # read_buffer
    0,     # prog_buffer
    0,     # lookahead_buffer
    0,     # name_max
    0,     # file_max
    0,     # attr_max
    0,     # metadata_max
    0,     # inline_max
)

EXPECTED_IMAGES = (
    {
        "name": "Apollo main",
        "path": "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin",
        "image_sha256": "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863",
        "load_address": 0x00438000,
        "payload_offset": 0x20,
        "config_address": 0x006E83A4,
        "config_size": 84,
        "config_sha256": "f38bd899e180d29ee60609a2452d25c2d2d6c6fef4eb455064e23a6ca7c6e813",
        "callbacks": (0x004763B9, 0x004763F1, 0x00476429, 0x004764DD),
    },
    {
        "name": "bootloader",
        "path": "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin",
        "image_sha256": "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5",
        "load_address": 0x00410000,
        "payload_offset": 0,
        "config_address": 0x00431070,
        "config_size": 84,
        "config_sha256": "724c351d2136e3c2f10b59ad84d547da4632739ea1f20eb839e9af2cfbd5b6e8",
        "callbacks": (0x004212D9, 0x00421311, 0x00421349, 0x004213D5),
    },
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"littlefs snapshot verification failed: {message}")


def verify_provenance() -> dict[str, Any]:
    provenance = json.loads(PROVENANCE_PATH.read_text(encoding="utf-8"))
    require(provenance["schema_version"] == 1, "unknown provenance schema")
    require(provenance["component"] == "littlefs", "component name changed")
    require(provenance["license"] == "BSD-3-Clause", "license changed")

    upstream = provenance["upstream"]
    require(upstream["repository"] == EXPECTED_REPOSITORY, "repository changed")
    require(upstream["selected_ref"] == EXPECTED_REF, "selected ref changed")
    require(upstream["selected_tag"] == EXPECTED_TAG, "selected tag changed")
    require(upstream["selected_commit"] == EXPECTED_COMMIT, "commit changed")
    require(upstream["selected_tree"] == EXPECTED_TREE, "tree changed")
    require(
        upstream["declared_library_version_hex"] == "0x0002000a",
        "library version declaration changed",
    )
    require(
        upstream["declared_disk_version_hex"] == "0x00020001",
        "disk version declaration changed",
    )

    selection = provenance["selection"]
    require(
        selection["classification"] == "source-equivalent release baseline",
        "source-equivalence classification changed",
    )
    require(
        selection["exact_historical_checkout_proven"] is False,
        "metadata must not claim the exact historical G2 checkout",
    )
    require(
        {candidate["commit"] for candidate in selection["equivalent_candidate_source_states"]}
        == {
            "366100b1403d2b680ed7a0f3bd0ba982c34d5c07",
            "152d03043ccab2ca6c454dd6cef43dc072d5810a",
            "936919d13488f307731fa203981ffb62d9e43479",
        },
        "source-equivalence candidate record changed",
    )

    safety = provenance["safety"]
    require(
        safety["integration_status"]
        == "selected audited bounded leaves are integrated into openCFW overlays; the pristine library translation units and G2 block-device port remain reference-only",
        "snapshot unexpectedly marked integrated",
    )
    require(
        safety["includes_g2_block_device_port"] is False,
        "snapshot must not include a G2 block-device port",
    )
    require(
        safety["permits_hardware_format"] is False,
        "hardware format must remain prohibited",
    )
    require(
        safety["permits_hardware_erase"] is False,
        "hardware erase must remain prohibited",
    )

    recorded_files = {
        entry["path"]: {
            "size": entry["size"],
            "sha256": entry["sha256"],
            "git_blob_sha1": entry["git_blob_sha1"],
        }
        for entry in provenance["files"]
    }
    require(recorded_files == EXPECTED_FILES, "provenance file inventory changed")
    return provenance


def verify_dual_tag_leaf_provenance(
    integration: dict[str, Any],
    upstream: bytes,
) -> None:
    expected_keys = {
        "upstream_function",
        "upstream_source",
        "upstream_commit",
        "upstream_definition_span",
        "upstream_definition_offset",
        "upstream_definition_size",
        "upstream_definition_sha256",
        "upstream_tag_typedef_span",
        "upstream_tag_typedef_offset",
        "upstream_tag_typedef_size",
        "upstream_tag_typedef_sha256",
        "local_source",
        "local_source_size",
        "local_source_sha256",
        "local_header",
        "local_header_size",
        "local_header_sha256",
        "stock_size",
        "stock_sha256",
        "stock_images",
        "production_profiles",
        "relocations",
        "qualification",
    }
    for integration_key, expected in EXPECTED_DUAL_TAG_LEAVES.items():
        leaf = integration[integration_key]
        function = expected["upstream_function"]
        require(set(leaf) == expected_keys, f"{function} provenance schema changed")
        upstream_expected = expected["upstream"]
        require(
            leaf["upstream_function"] == function
            and leaf["upstream_source"] == "lfs.c"
            and leaf["upstream_commit"] == EXPECTED_COMMIT
            and leaf["upstream_definition_span"]
            == (
                f"lfs.c bytes [{upstream_expected['offset']},"
                f"{upstream_expected['offset'] + upstream_expected['size']})"
            )
            and leaf["upstream_definition_offset"] == upstream_expected["offset"]
            and leaf["upstream_definition_size"] == upstream_expected["size"]
            and leaf["upstream_definition_sha256"] == upstream_expected["sha256"],
            f"{function} upstream definition pins changed",
        )
        require(
            leaf["upstream_tag_typedef_span"] == "lfs.c bytes [9602,9629)"
            and leaf["upstream_tag_typedef_offset"]
            == EXPECTED_TAG_CHUNK_TYPEDEF["offset"]
            and leaf["upstream_tag_typedef_size"]
            == EXPECTED_TAG_CHUNK_TYPEDEF["size"]
            and leaf["upstream_tag_typedef_sha256"]
            == EXPECTED_TAG_CHUNK_TYPEDEF["sha256"],
            f"{function} lfs_tag_t typedef pins changed",
        )
        for prefix in ("source", "header"):
            local_prefix = f"local_{prefix}"
            local_expected = expected[prefix]
            require(
                leaf[local_prefix] == local_expected["path"]
                and leaf[f"{local_prefix}_size"] == local_expected["size"]
                and leaf[f"{local_prefix}_sha256"] == local_expected["sha256"],
                f"{function} local {prefix} pins changed",
            )
            local_path = OPENCFW_ROOT / local_expected["path"]
            data = local_path.read_bytes()
            require(
                len(data) == local_expected["size"]
                and sha256(data) == local_expected["sha256"],
                f"{function} bounded production {prefix} changed",
            )
        stock = expected["stock"]
        require(
            leaf["stock_size"] == stock["size"]
            and leaf["stock_sha256"] == stock["sha256"],
            f"{function} stock body pins changed",
        )
        expected_stock_images = {
            image_name: {
                "stock_span": (
                    f"[0x{image['start']:08X},0x{image['end']:08X})"
                ),
                "stock_file_offset": image["file_offset"],
                "stock_callers": [
                    {"address": f"0x{address:08X}", "encoding": encoding}
                    for address, encoding in image["callers"]
                ],
            }
            for image_name, image in (
                (name, stock[name])
                for name in ("apollo_main", "apollo_bootloader")
            )
        }
        require(
            leaf["stock_images"] == expected_stock_images,
            f"{function} dual-image stock topology changed",
        )
        expected_profiles = {
            profile_name: {
                image_name: {
                    "leaf_size": expected["leaf_size"],
                    "overlay_offset": offset,
                    "runtime_address": f"0x{runtime_address:08X}",
                    "relocated_sha256": expected["text_sha256"],
                    "unrelocated_sha256": expected["text_sha256"],
                }
                for image_name, (offset, runtime_address) in images.items()
            }
            for profile_name, images in expected["profiles"].items()
        }
        require(
            leaf["production_profiles"] == expected_profiles,
            f"{function} dual-image/toolchain placement pins changed",
        )
        require(leaf["relocations"] == [], f"{function} gained a relocation")
        require(
            "source-equivalent baseline" in leaf["qualification"]
            and "not proof of the exact historical vendor checkout"
            in leaf["qualification"]
            and "atomically registered in Apollo main and bootloader"
            in leaf["qualification"]
            and "remain unregistered" in leaf["qualification"],
            f"{function} qualification changed",
        )
        start = upstream_expected["offset"]
        definition = upstream[start:start + upstream_expected["size"]]
        require(
            sha256(definition) == upstream_expected["sha256"]
            and definition == upstream_expected["definition"],
            f"authenticated upstream {function} definition changed",
        )


def verify_production_integration(provenance: dict[str, Any]) -> None:
    integration = provenance["production_integration"]
    require(
        set(integration)
        == {
            "qualification",
            "allowed_production_source_paths",
            "allowed_production_symbols",
            "rewind_leaf",
            "tag_type2_leaf",
            "tag_chunk_leaf",
            "tag_isvalid_leaf",
            "tag_type1_leaf",
            "tag_type3_leaf",
            "tag_id_leaf",
            "tag_size_leaf",
        },
        "production-integration schema changed",
    )
    require(
        "source-equivalent v2.10.1 baseline" in integration["qualification"]
        and "not proof" in integration["qualification"]
        and "historical vendor checkout" in integration["qualification"]
        and "remain unregistered" in integration["qualification"],
        "source-equivalent/not-exact-vendor qualification changed",
    )
    require(
        integration["allowed_production_source_paths"]
        == list(EXPECTED_PRODUCTION_SOURCE_PATHS),
        "bounded littlefs production source/header allowlist changed",
    )
    require(
        integration["allowed_production_symbols"]
        == list(EXPECTED_PRODUCTION_SYMBOLS),
        "bounded littlefs production symbol allowlist changed",
    )

    rewind = integration["rewind_leaf"]
    require(
        set(rewind)
        == {
            "upstream_function",
            "upstream_source",
            "upstream_commit",
            "upstream_definition_span",
            "upstream_definition_offset",
            "upstream_definition_size",
            "upstream_definition_sha256",
            "local_source",
            "local_source_size",
            "local_source_sha256",
            "local_header",
            "local_header_size",
            "local_header_sha256",
            "stock_span",
            "stock_size",
            "stock_sha256",
            "stock_seek_seams",
            "production_profiles",
            "sole_relocation",
            "qualification",
        },
        "lfs_file_rewind_ provenance schema changed",
    )
    require(
        rewind["upstream_function"] == "lfs_file_rewind_"
        and rewind["upstream_source"] == "lfs.c"
        and rewind["upstream_commit"] == EXPECTED_COMMIT,
        "lfs_file_rewind_ upstream identity changed",
    )
    require(
        rewind["upstream_definition_span"] == "lfs.c bytes [118157,118349)"
        and rewind["upstream_definition_offset"]
        == EXPECTED_REWIND_UPSTREAM["offset"]
        and rewind["upstream_definition_size"]
        == EXPECTED_REWIND_UPSTREAM["size"]
        and rewind["upstream_definition_sha256"]
        == EXPECTED_REWIND_UPSTREAM["sha256"],
        "lfs_file_rewind_ upstream definition pin changed",
    )
    for prefix, expected in (
        ("local_source", EXPECTED_REWIND_SOURCE),
        ("local_header", EXPECTED_REWIND_HEADER),
    ):
        require(rewind[prefix] == expected["path"], f"{prefix} path changed")
        require(
            rewind[f"{prefix}_size"] == expected["size"],
            f"{prefix} size pin changed",
        )
        require(
            rewind[f"{prefix}_sha256"] == expected["sha256"],
            f"{prefix} SHA-256 pin changed",
        )
    require(
        rewind["stock_span"] == "[0x004CE460,0x004CE472)"
        and rewind["stock_size"] == EXPECTED_REWIND_STOCK["size"]
        and rewind["stock_sha256"] == EXPECTED_REWIND_STOCK["sha256"]
        and rewind["stock_seek_seams"] == ["0x004CE3BC"],
        "lfs_file_rewind_ stock boundary changed",
    )
    expected_profiles = {
        name: {
            "leaf_size": profile["size"],
            "overlay_offset": profile["offset"],
            "runtime_address": f"0x{profile['runtime_address']:08X}",
            "relocated_sha256": profile["sha256"],
            "unrelocated_sha256": profile["unrelocated_sha256"],
        }
        for name, profile in EXPECTED_REWIND_PROFILES.items()
    }
    require(
        rewind["production_profiles"] == expected_profiles,
        "lfs_file_rewind_ dual-toolchain placement/text pins changed",
    )
    require(
        rewind["sole_relocation"]
        == {
            **EXPECTED_REWIND_RELOCATION,
            "target_address": "0x004CE3BC",
        },
        "lfs_file_rewind_ sole seek relocation changed",
    )
    require(
        "source-equivalent baseline" in rewind["qualification"]
        and "not proof of the exact historical vendor checkout"
        in rewind["qualification"]
        and "remain unregistered" in rewind["qualification"],
        "lfs_file_rewind_ qualification changed",
    )

    for expected in (EXPECTED_REWIND_SOURCE, EXPECTED_REWIND_HEADER):
        path = OPENCFW_ROOT / expected["path"]
        require(path.is_file(), f"bounded production file missing: {expected['path']}")
        data = path.read_bytes()
        require(len(data) == expected["size"], f"size changed: {expected['path']}")
        require(
            sha256(data) == expected["sha256"],
            f"SHA-256 changed: {expected['path']}",
        )

    upstream = (HERE / "lfs.c").read_bytes()
    start = EXPECTED_REWIND_UPSTREAM["offset"]
    definition = upstream[start:start + EXPECTED_REWIND_UPSTREAM["size"]]
    require(
        len(definition) == EXPECTED_REWIND_UPSTREAM["size"]
        and sha256(definition) == EXPECTED_REWIND_UPSTREAM["sha256"],
        "authenticated upstream lfs_file_rewind_ definition changed",
    )
    require(
        definition.startswith(
            b"static int lfs_file_rewind_(lfs_t *lfs, lfs_file_t *file) {\n"
        )
        and definition.endswith(b"    return 0;\n}\n"),
        "authenticated upstream lfs_file_rewind_ definition boundary changed",
    )

    tag_type2 = integration["tag_type2_leaf"]
    require(
        set(tag_type2)
        == {
            "upstream_function",
            "upstream_source",
            "upstream_commit",
            "upstream_definition_span",
            "upstream_definition_offset",
            "upstream_definition_size",
            "upstream_definition_sha256",
            "local_source",
            "local_source_size",
            "local_source_sha256",
            "local_header",
            "local_header_size",
            "local_header_sha256",
            "stock_span",
            "stock_size",
            "stock_sha256",
            "stock_callers",
            "production_profiles",
            "relocations",
            "qualification",
        },
        "lfs_tag_type2 provenance schema changed",
    )
    require(
        tag_type2["upstream_function"] == "lfs_tag_type2"
        and tag_type2["upstream_source"] == "lfs.c"
        and tag_type2["upstream_commit"] == EXPECTED_COMMIT,
        "lfs_tag_type2 upstream identity changed",
    )
    require(
        tag_type2["upstream_definition_span"] == "lfs.c bytes [10326,10418)"
        and tag_type2["upstream_definition_offset"]
        == EXPECTED_TAG_TYPE2_UPSTREAM["offset"]
        and tag_type2["upstream_definition_size"]
        == EXPECTED_TAG_TYPE2_UPSTREAM["size"]
        and tag_type2["upstream_definition_sha256"]
        == EXPECTED_TAG_TYPE2_UPSTREAM["sha256"],
        "lfs_tag_type2 upstream definition pin changed",
    )
    for prefix, expected in (
        ("local_source", EXPECTED_TAG_TYPE2_SOURCE),
        ("local_header", EXPECTED_TAG_TYPE2_HEADER),
    ):
        require(tag_type2[prefix] == expected["path"], f"{prefix} path changed")
        require(
            tag_type2[f"{prefix}_size"] == expected["size"],
            f"{prefix} size pin changed",
        )
        require(
            tag_type2[f"{prefix}_sha256"] == expected["sha256"],
            f"{prefix} SHA-256 pin changed",
        )
    require(
        tag_type2["stock_span"] == "[0x004CAE90,0x004CAE98)"
        and tag_type2["stock_size"] == EXPECTED_TAG_TYPE2_STOCK["size"]
        and tag_type2["stock_sha256"] == EXPECTED_TAG_TYPE2_STOCK["sha256"],
        "lfs_tag_type2 stock boundary changed",
    )
    require(
        tag_type2["stock_callers"]
        == [
            {"address": f"0x{address:08X}", "encoding": encoding}
            for address, encoding in EXPECTED_TAG_TYPE2_STOCK["callers"]
        ],
        "lfs_tag_type2 stock caller pins changed",
    )
    require(
        tag_type2["production_profiles"]
        == {
            name: {
                "leaf_size": profile["size"],
                "overlay_offset": profile["offset"],
                "runtime_address": f"0x{profile['runtime_address']:08X}",
                "relocated_sha256": profile["sha256"],
                "unrelocated_sha256": profile["sha256"],
            }
            for name, profile in EXPECTED_TAG_TYPE2_PROFILES.items()
        },
        "lfs_tag_type2 dual-toolchain placement/text pins changed",
    )
    require(tag_type2["relocations"] == [], "lfs_tag_type2 gained a relocation")
    require(
        "source-equivalent baseline" in tag_type2["qualification"]
        and "not proof of the exact historical vendor checkout"
        in tag_type2["qualification"]
        and "remain unregistered" in tag_type2["qualification"],
        "lfs_tag_type2 qualification changed",
    )

    for expected in (EXPECTED_TAG_TYPE2_SOURCE, EXPECTED_TAG_TYPE2_HEADER):
        path = OPENCFW_ROOT / expected["path"]
        require(path.is_file(), f"bounded production file missing: {expected['path']}")
        data = path.read_bytes()
        require(len(data) == expected["size"], f"size changed: {expected['path']}")
        require(
            sha256(data) == expected["sha256"],
            f"SHA-256 changed: {expected['path']}",
        )

    start = EXPECTED_TAG_TYPE2_UPSTREAM["offset"]
    definition = upstream[start:start + EXPECTED_TAG_TYPE2_UPSTREAM["size"]]
    require(
        len(definition) == EXPECTED_TAG_TYPE2_UPSTREAM["size"]
        and sha256(definition) == EXPECTED_TAG_TYPE2_UPSTREAM["sha256"],
        "authenticated upstream lfs_tag_type2 definition changed",
    )
    require(
        definition
        == (
            b"static inline uint16_t lfs_tag_type2(lfs_tag_t tag) {\n"
            b"    return (tag & 0x78000000) >> 20;\n"
            b"}"
        ),
        "authenticated upstream lfs_tag_type2 definition boundary changed",
    )

    tag_chunk = integration["tag_chunk_leaf"]
    require(
        set(tag_chunk)
        == {
            "upstream_function",
            "upstream_source",
            "upstream_commit",
            "upstream_definition_span",
            "upstream_definition_offset",
            "upstream_definition_size",
            "upstream_definition_sha256",
            "upstream_tag_typedef_span",
            "upstream_tag_typedef_offset",
            "upstream_tag_typedef_size",
            "upstream_tag_typedef_sha256",
            "local_source",
            "local_source_size",
            "local_source_sha256",
            "local_header",
            "local_header_size",
            "local_header_sha256",
            "stock_size",
            "stock_sha256",
            "stock_images",
            "production_profiles",
            "relocations",
            "qualification",
        },
        "lfs_tag_chunk provenance schema changed",
    )
    require(
        tag_chunk["upstream_function"] == "lfs_tag_chunk"
        and tag_chunk["upstream_source"] == "lfs.c"
        and tag_chunk["upstream_commit"] == EXPECTED_COMMIT
        and tag_chunk["upstream_definition_span"]
        == "lfs.c bytes [10514,10607)"
        and tag_chunk["upstream_definition_offset"]
        == EXPECTED_TAG_CHUNK_UPSTREAM["offset"]
        and tag_chunk["upstream_definition_size"]
        == EXPECTED_TAG_CHUNK_UPSTREAM["size"]
        and tag_chunk["upstream_definition_sha256"]
        == EXPECTED_TAG_CHUNK_UPSTREAM["sha256"],
        "lfs_tag_chunk upstream identity changed",
    )
    require(
        tag_chunk["upstream_tag_typedef_span"] == "lfs.c bytes [9602,9629)"
        and tag_chunk["upstream_tag_typedef_offset"]
        == EXPECTED_TAG_CHUNK_TYPEDEF["offset"]
        and tag_chunk["upstream_tag_typedef_size"]
        == EXPECTED_TAG_CHUNK_TYPEDEF["size"]
        and tag_chunk["upstream_tag_typedef_sha256"]
        == EXPECTED_TAG_CHUNK_TYPEDEF["sha256"],
        "lfs_tag_t upstream typedef identity changed",
    )
    for prefix, expected in (
        ("local_source", EXPECTED_TAG_CHUNK_SOURCE),
        ("local_header", EXPECTED_TAG_CHUNK_HEADER),
    ):
        require(tag_chunk[prefix] == expected["path"], f"{prefix} path changed")
        require(
            tag_chunk[f"{prefix}_size"] == expected["size"]
            and tag_chunk[f"{prefix}_sha256"] == expected["sha256"],
            f"{prefix} pin changed",
        )
        path = OPENCFW_ROOT / expected["path"]
        data = path.read_bytes()
        require(
            len(data) == expected["size"] and sha256(data) == expected["sha256"],
            f"bounded production file changed: {expected['path']}",
        )
    require(
        tag_chunk["stock_size"] == EXPECTED_TAG_CHUNK_STOCK["size"]
        and tag_chunk["stock_sha256"] == EXPECTED_TAG_CHUNK_STOCK["sha256"],
        "lfs_tag_chunk stock pins changed",
    )
    expected_stock_images = {}
    for image_name in ("apollo_main", "apollo_bootloader"):
        expected = EXPECTED_TAG_CHUNK_STOCK[image_name]
        expected_stock_images[image_name] = {
            "stock_span": (
                f"[0x{expected['start']:08X},0x{expected['end']:08X})"
            ),
            "stock_file_offset": expected["file_offset"],
            "stock_callers": [
                {"address": f"0x{address:08X}", "encoding": encoding}
                for address, encoding in expected["callers"]
            ],
        }
    require(
        tag_chunk["stock_images"] == expected_stock_images,
        "lfs_tag_chunk dual-image stock topology changed",
    )
    expected_profiles = {
        "apple-clang": {
            "apollo_main": (124560, "0x007B29B4"),
            "apollo_bootloader": (622, "0x004346E6"),
        },
        "linux-clang": {
            "apollo_main": (126380, "0x007B30D0"),
            "apollo_bootloader": (622, "0x004346E6"),
        },
    }
    require(
        tag_chunk["production_profiles"]
        == {
            profile: {
                component: {
                    "leaf_size": 6,
                    "overlay_offset": offset,
                    "runtime_address": runtime,
                    "relocated_sha256": EXPECTED_TAG_CHUNK_TEXT_SHA256,
                    "unrelocated_sha256": EXPECTED_TAG_CHUNK_TEXT_SHA256,
                }
                for component, (offset, runtime) in components.items()
            }
            for profile, components in expected_profiles.items()
        },
        "lfs_tag_chunk dual-image/toolchain placement pins changed",
    )
    require(tag_chunk["relocations"] == [], "lfs_tag_chunk gained a relocation")
    require(
        "source-equivalent baseline" in tag_chunk["qualification"]
        and "not proof of the exact historical vendor checkout"
        in tag_chunk["qualification"]
        and "remain unregistered" in tag_chunk["qualification"],
        "lfs_tag_chunk qualification changed",
    )
    start = EXPECTED_TAG_CHUNK_UPSTREAM["offset"]
    definition = upstream[start:start + EXPECTED_TAG_CHUNK_UPSTREAM["size"]]
    require(
        sha256(definition) == EXPECTED_TAG_CHUNK_UPSTREAM["sha256"]
        and definition
        == (
            b"static inline uint8_t lfs_tag_chunk(lfs_tag_t tag) {\n"
            b"    return (tag & 0x0ff00000) >> 20;\n"
            b"}\n\n"
        ),
        "authenticated upstream lfs_tag_chunk definition changed",
    )
    typedef_start = EXPECTED_TAG_CHUNK_TYPEDEF["offset"]
    typedef = upstream[
        typedef_start:typedef_start + EXPECTED_TAG_CHUNK_TYPEDEF["size"]
    ]
    require(
        sha256(typedef) == EXPECTED_TAG_CHUNK_TYPEDEF["sha256"]
        and typedef == b"typedef uint32_t lfs_tag_t;",
        "authenticated upstream lfs_tag_t typedef changed",
    )
    verify_dual_tag_leaf_provenance(integration, upstream)


def littlefs_source_records(overlay: dict[str, Any]):
    for record in overlay.get("sources", []):
        source_path = record.get("path", "")
        if (
            record.get("upstream_commit") == EXPECTED_COMMIT
            or "runtime_littlefs_" in source_path
        ):
            yield None, record
    for collection in ("isolated_leaves", "relocated_leaves", "in_place_leaves"):
        for leaf in overlay.get(collection, []):
            source = leaf.get("source", {})
            source_path = source.get("path", "")
            if (
                leaf.get("function", "").startswith("open_cfw_littlefs_")
                or source.get("upstream_commit") == EXPECTED_COMMIT
                or "runtime_littlefs_" in source_path
            ):
                yield leaf.get("function"), source


def verify_production_allowlist() -> None:
    allowed_paths = set(EXPECTED_PRODUCTION_SOURCE_PATHS)
    allowed_symbols = set(EXPECTED_PRODUCTION_SYMBOLS)
    all_recorded_paths: set[str] = set()
    all_recorded_symbols: set[str] = set()
    apollo_overlay: dict[str, Any] | None = None
    production_overlays: dict[str, dict[str, Any]] = {}

    for relative_path, expected_paths in EXPECTED_OVERLAY_PRODUCTION_PATHS.items():
        overlay_path = OPENCFW_ROOT / relative_path
        require(overlay_path.is_file(), f"littlefs production overlay missing: {relative_path}")
        overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
        production_overlays[relative_path] = overlay
        if relative_path.startswith("components/apollo_main/"):
            apollo_overlay = overlay

        functions = {
            name
            for name in overlay.get("functions", [])
            if name.startswith("open_cfw_littlefs_")
        }
        require(
            functions == EXPECTED_OVERLAY_PRODUCTION_SYMBOLS[relative_path],
            f"littlefs production symbol set changed in {relative_path}",
        )
        all_recorded_symbols.update(functions)

        records = list(littlefs_source_records(overlay))
        paths = {record.get("path") for _, record in records}
        require(
            paths == expected_paths,
            f"littlefs production source path set changed in {relative_path}",
        )
        for symbol, record in records:
            source_path = record.get("path")
            require(source_path in allowed_paths, f"unallowlisted littlefs source: {source_path}")
            if symbol is not None:
                require(symbol in allowed_symbols, f"unallowlisted littlefs symbol: {symbol}")
            path = OPENCFW_ROOT / source_path
            require(path.is_file(), f"registered littlefs source missing: {source_path}")
            require(
                record.get("sha256") == sha256(path.read_bytes()),
                f"registered littlefs source hash changed: {source_path}",
            )
            require(
                not source_path.startswith("third_party/littlefs/"),
                "pristine littlefs translation unit entered production",
            )
            all_recorded_paths.add(source_path)

    require(
        all_recorded_symbols == allowed_symbols,
        "combined littlefs production symbol allowlist changed",
    )
    require(
        all_recorded_paths
        == allowed_paths
        - {
            EXPECTED_PRODUCTION_SOURCE_PATHS[14],
            EXPECTED_PRODUCTION_SOURCE_PATHS[16],
            EXPECTED_PRODUCTION_SOURCE_PATHS[21],
            EXPECTED_PRODUCTION_SOURCE_PATHS[23],
            EXPECTED_PRODUCTION_SOURCE_PATHS[25],
            EXPECTED_PRODUCTION_SOURCE_PATHS[27],
            EXPECTED_PRODUCTION_SOURCE_PATHS[29],
            EXPECTED_PRODUCTION_SOURCE_PATHS[31],
            EXPECTED_PRODUCTION_SOURCE_PATHS[33],
        },
        "combined littlefs production source allowlist changed",
    )
    require(apollo_overlay is not None, "Apollo littlefs production overlay missing")
    leaves = [
        leaf
        for leaf in apollo_overlay.get("relocated_leaves", [])
        if leaf.get("function") == "open_cfw_littlefs_file_rewind_private"
    ]
    require(len(leaves) == 1, "lfs_file_rewind_ production leaf is not unique")
    verify_rewind_overlay_leaf(leaves[0])
    tag_type2_leaves = [
        leaf
        for leaf in apollo_overlay.get("relocated_leaves", [])
        if leaf.get("function") == "open_cfw_littlefs_tag_type2"
    ]
    require(
        len(tag_type2_leaves) == 1,
        "lfs_tag_type2 production leaf is not unique",
    )
    verify_tag_type2_overlay_leaf(tag_type2_leaves[0])
    patch_sites = [
        site
        for site in apollo_overlay.get("patch_sites", [])
        if site.get("target_function") == "open_cfw_littlefs_tag_type2"
    ]
    require(
        patch_sites
        == [
            {
                "name": "replace_littlefs_tag_type2",
                "runtime_address": EXPECTED_TAG_TYPE2_STOCK["start"],
                "expected_size": EXPECTED_TAG_TYPE2_STOCK["size"],
                "expected_sha256": EXPECTED_TAG_TYPE2_STOCK["sha256"],
                "branch": "b_w",
                "target_function": "open_cfw_littlefs_tag_type2",
            }
        ],
        "lfs_tag_type2 production patch registration changed",
    )
    tag_chunk_components = {
        "components/apollo_main/core_overlay/overlay.json": {
            "offset": 124560,
            "alignment": 4,
            "stock_start": 0x004CAEA0,
            "linux_expected": {
                "size": 6,
                "sha256": EXPECTED_TAG_CHUNK_TEXT_SHA256,
                "alignment": 4,
                "offset": 126380,
                "unrelocated_sha256": EXPECTED_TAG_CHUNK_TEXT_SHA256,
            },
            "linux_artifact": {
                "overlay_size": 145208,
                "overlay_sha256": "fac5b48b6ae2eac985a0a65ddb8d1595dd10e2abcbdd0c6a3bb562f72e43a826",
                "component_size": 3668604,
                "component_sha256": "378c868e151060a59ab91b0de1a722e8678b8e1da8eede248c5702ccf8902798",
            },
        },
        "components/bootloader/core_overlay/overlay.json": {
            "offset": 622,
            "alignment": 2,
            "stock_start": 0x00410BA8,
            "linux_expected": None,
            "linux_artifact": {
                "overlay_size": 662,
                "overlay_sha256": "e4c743531f56c190b7e3129768d410480a2f3433a5b680c7bf432ef0b05a7021",
                "component_size": 149262,
                "component_sha256": "fc3d07c8a59e1c33f26965cdb1888114412c3ca671d6137f7c3166acc81c8d74",
            },
        },
    }
    for relative_path, expected in tag_chunk_components.items():
        overlay = production_overlays[relative_path]
        leaves = [
            (collection, leaf)
            for collection in ("isolated_leaves", "relocated_leaves")
            for leaf in overlay.get(collection, [])
            if leaf.get("function") == "open_cfw_littlefs_tag_chunk"
        ]
        require(
            len(leaves) == 1,
            f"lfs_tag_chunk production leaf is not unique in {relative_path}",
        )
        collection, leaf = leaves[0]
        require(
            collection == "relocated_leaves",
            f"lfs_tag_chunk leaf category changed in {relative_path}",
        )
        require(
            overlay["toolchain_profiles"]["linux-clang"]["expected"]
            == expected["linux_artifact"],
            f"Linux lfs_tag_chunk aggregate pins changed in {relative_path}",
        )
        source = leaf.get("source", {})
        require(
            source.get("path") == EXPECTED_TAG_CHUNK_SOURCE["path"]
            and source.get("size") == EXPECTED_TAG_CHUNK_SOURCE["size"]
            and source.get("sha256") == EXPECTED_TAG_CHUNK_SOURCE["sha256"]
            and source.get("license") == "BSD-3-Clause"
            and source.get("upstream_commit") == EXPECTED_COMMIT,
            f"lfs_tag_chunk source registration changed in {relative_path}",
        )
        require(
            leaf.get("strict_relocation_contract") is True
            and leaf.get("expected")
            == {
                "size": 6,
                "sha256": EXPECTED_TAG_CHUNK_TEXT_SHA256,
                "alignment": expected["alignment"],
                "offset": expected["offset"],
                "unrelocated_sha256": EXPECTED_TAG_CHUNK_TEXT_SHA256,
            }
            and leaf.get("relocations") == [],
            f"lfs_tag_chunk leaf pins changed in {relative_path}",
        )
        linux_profile = leaf.get("toolchain_profiles", {}).get("linux-clang")
        if expected["linux_expected"] is None:
            require(
                linux_profile
                == {"reviewed_version_prefix": "Homebrew clang version 22.1.8"}
                and overlay["function_profiles"]["linux-clang"]
                ["open_cfw_littlefs_tag_chunk"]
                == {"expected_offset": 622, "expected_size": 6},
                f"inherited Linux lfs_tag_chunk pins changed in {relative_path}",
            )
        else:
            require(
                linux_profile
                == {
                    "reviewed_version_prefix": "Homebrew clang version 22.1.8",
                    "expected": expected["linux_expected"],
                    "relocations": [],
                },
                f"Linux lfs_tag_chunk leaf pins changed in {relative_path}",
            )
        patch_sites = [
            site
            for site in overlay.get("patch_sites", [])
            if site.get("target_function") == "open_cfw_littlefs_tag_chunk"
        ]
        require(
            patch_sites
            == [{
                "name": "replace_littlefs_tag_chunk",
                "runtime_address": expected["stock_start"],
                "expected_size": EXPECTED_TAG_CHUNK_STOCK["size"],
                "expected_sha256": EXPECTED_TAG_CHUNK_STOCK["sha256"],
                "branch": "b_w",
                "target_function": "open_cfw_littlefs_tag_chunk",
            }],
            f"lfs_tag_chunk patch registration changed in {relative_path}",
        )

    expected_tail = [
        expected["function"] for expected in EXPECTED_DUAL_TAG_LEAVES.values()
    ]
    expected_successors = {
        "components/apollo_main/core_overlay/overlay.json": [
            "open_cfw_nanopb_decode_fixed64",
            "open_cfw_nanopb_read",
            "open_cfw_nanopb_buf_read",
            "open_cfw_nanopb_readbyte",
            "open_cfw_nanopb_istream_from_buffer",
            "open_cfw_nanopb_decode_svarint",
            "open_cfw_nanopb_decode_varint32_eof",
            "open_cfw_nanopb_decode_varint32",
            "open_cfw_nanopb_skip_string",
            "open_cfw_nanopb_skip_field",
            "open_cfw_nanopb_read_raw_value",
            "open_cfw_nanopb_make_string_substream",
            "open_cfw_nanopb_decode_bool",
            "open_cfw_nanopb_dec_bool",
            "open_cfw_nanopb_dec_varint",
            "open_cfw_nanopb_dec_bytes",
            "open_cfw_nanopb_dec_string",
            "open_cfw_nanopb_dec_submessage",
            "open_cfw_nanopb_decode_inner",
            "open_cfw_nanopb_decode_tag",
            "open_cfw_nanopb_load_descriptor_values",
            "open_cfw_nanopb_field_iter_begin",
            "open_cfw_nanopb_field_iter_begin_extension",
            "open_cfw_nanopb_field_iter_next",
            "open_cfw_nanopb_field_iter_find",
            "open_cfw_nanopb_field_iter_find_extension",
            "open_cfw_nanopb_field_iter_begin_const",
            "open_cfw_nanopb_field_iter_begin_extension_const",
            "open_cfw_nanopb_default_field_callback",
            "open_cfw_nanopb_message_set_to_defaults",
            "open_cfw_nanopb_field_set_to_default",
            "open_cfw_nanopb_decode_field",
            "open_cfw_nanopb_default_extension_decoder",
            "open_cfw_nanopb_decode_extension",
            "open_cfw_nanopb_dec_fixed_length_bytes",
            "open_cfw_nanopb_decode_basic_field",
            "open_cfw_nanopb_decode_static_field",
            "open_cfw_nanopb_decode_pointer_field",
            "open_cfw_nanopb_decode_callback_field",
            "open_cfw_ring_buffer_is_empty",
            "open_cfw_ring_buffer_is_full",
            "open_cfw_ring_buffer_init",
            "open_cfw_ring_buffer_queue",
            "open_cfw_ring_buffer_queue_arr",
            "open_cfw_ring_buffer_dequeue",
            "open_cfw_ring_buffer_dequeue_arr",
            "open_cfw_iar_memcpy_void",
            "open_cfw_iar_memcpy_aligned_void",
            "open_cfw_iar_memmove_void",
            "open_cfw_iar_domain_error",
            "open_cfw_iar_sqrtf",
            "open_cfw_iar_range_error",
            "open_cfw_iar_errno_address",
            "open_cfw_copy_advertised_name_pair_suffix",
            "open_cfw_cmsis_irq_context",
            "open_cfw_cmsis_kernel_get_tick_count",
            "open_cfw_cmsis_thread_get_id",
            "open_cfw_cmsis_message_queue_get_capacity",
            "open_cfw_cmsis_semaphore_get_count",
            "open_cfw_cmsis_message_queue_get_count",
            "open_cfw_cmsis_message_queue_delete",
            "open_cfw_cmsis_thread_yield",
            "open_cfw_cmsis_kernel_get_state",
            "open_cfw_cmsis_mutex_delete",
            "open_cfw_cmsis_timer_is_running",
            "open_cfw_cmsis_mutex_acquire",
            "open_cfw_cmsis_mutex_release",
            "open_cfw_cmsis_semaphore_release",
            "open_cfw_cmsis_timer_start",
            "open_cfw_cmsis_timer_stop",
            "open_cfw_cmsis_timer_delete",
            "open_cfw_cmsis_event_flags_new",
            "open_cfw_cmsis_event_flags_set",
            "open_cfw_cmsis_event_flags_clear",
            "open_cfw_cmsis_event_flags_wait",
            "open_cfw_cmsis_timer_callback",
            "open_cfw_cmsis_timer_new",
            "open_cfw_cmsis_memory_pool_new",
            "open_cfw_freertos_queue_copy_data_from_queue",
            "open_cfw_freertos_queue_receive_from_isr",
            "open_cfw_cmsis_semaphore_acquire",
            "open_cfw_cmsis_memory_pool_create_block",
            "open_cfw_cmsis_memory_pool_alloc_block",
            "open_cfw_cmsis_memory_pool_free_block",
            "open_cfw_cmsis_memory_pool_alloc",
            "open_cfw_cmsis_memory_pool_free",
            "open_cfw_freertos_task_priority_disinherit",
            "open_cfw_freertos_queue_copy_data_to_queue",
            "open_cfw_freertos_queue_generic_send_from_isr",
            "open_cfw_cmsis_message_queue_put",
            "open_cfw_freertos_task_add_current_to_delayed_list",
            "open_cfw_freertos_task_place_on_event_list",
            "open_cfw_freertos_queue_unlock",
            "open_cfw_freertos_queue_receive",
            "open_cfw_cmsis_message_queue_get",
            "open_cfw_freertos_task_delay",
            "open_cfw_cmsis_delay",
            "open_cfw_freertos_task_priority_set",
            "open_cfw_cmsis_thread_set_priority",
            "open_cfw_freertos_task_get_state",
            "open_cfw_freertos_task_delete_tcb",
            "open_cfw_freertos_task_delete",
            "open_cfw_cmsis_thread_terminate",
            "open_cfw_freertos_task_notify_wait",
            "open_cfw_freertos_task_notify",
            "open_cfw_freertos_task_notify_from_isr",
            "open_cfw_cmsis_thread_flags_set",
            "open_cfw_cmsis_thread_flags_wait",
            "open_cfw_cmsis_thread_new",
            "open_cfw_cmsis_kernel_initialize",
            "open_cfw_cmsis_kernel_start",
            "open_cfw_tinyframe_g2_memory_set",
            "TF_WriteImpl",
            "open_cfw_tinyframe_upstream_init_static",
            "TF_Init",
            "TF_HandleReceivedMessage",
            "TF_AcceptChar",
            "TF_Accept",
            "TF_AddTypeListener",
            "TF_SendFrame",
            "TF_Respond",
            "TF_Query_Multipart",
            "TF_Multipart_Payload",
            "TF_Multipart_Close",
            "TF_Tick",
        ],
        "components/bootloader/core_overlay/overlay.json": [],
    }
    aggregate_pins = {
        "components/apollo_main/core_overlay/overlay.json": {
            "apple-clang": {
                "overlay_size": 240692,
                "overlay_sha256": "2db11ff707bf253280eb07667c3d76954347cc9e31796c7589faf788fed629ae",
                "component_size": 3764088,
                "component_sha256": "b3ee7d2fb560f134bd5c4a27eb8203abdc0dd9482816319be0b03320fc2067ed",
            },
            "linux-clang": {
                "overlay_size": 145208,
                "overlay_sha256": "fac5b48b6ae2eac985a0a65ddb8d1595dd10e2abcbdd0c6a3bb562f72e43a826",
                "component_size": 3668604,
                "component_sha256": "378c868e151060a59ab91b0de1a722e8678b8e1da8eede248c5702ccf8902798",
            },
        },
        "components/bootloader/core_overlay/overlay.json": {
            "apple-clang": {
                "overlay_size": 662,
                "overlay_sha256": "7cb3c17a03dda3b8576d8288ffa61df1332d89f1f24d6c5877bf0143e233902b",
                "component_size": 149262,
                "component_sha256": "695688b7cc4d9583e9e5c854db44980acab9a58d367bc7e02fa5e51eb00e3267",
            },
            "linux-clang": {
                "overlay_size": 662,
                "overlay_sha256": "e4c743531f56c190b7e3129768d410480a2f3433a5b680c7bf432ef0b05a7021",
                "component_size": 149262,
                "component_sha256": "fc3d07c8a59e1c33f26965cdb1888114412c3ca671d6137f7c3166acc81c8d74",
            },
        },
    }
    for relative_path, overlay in production_overlays.items():
        component_name = (
            "apollo_main"
            if relative_path.startswith("components/apollo_main/")
            else "apollo_bootloader"
        )
        alignment = 4 if component_name == "apollo_main" else 2
        require(
            overlay["expected"] == aggregate_pins[relative_path]["apple-clang"]
            and overlay["toolchain_profiles"]["linux-clang"]["expected"]
            == aggregate_pins[relative_path]["linux-clang"],
            f"atomic littlefs scalar tag aggregate pins changed in {relative_path}",
        )
        # The scalar tag leaves must remain one atomic ordered tranche, but
        # unrelated source leaves may be appended after them as OpenCFW gains
        # ownership.  Do not turn this dependency verifier into a pin for the
        # whole component tail.
        expected_sequence = expected_tail
        relocated_functions = [
            leaf.get("function") for leaf in overlay.get("relocated_leaves", [])
        ]
        relocated_matches = [
            index for index in range(len(relocated_functions) - len(expected_sequence) + 1)
            if relocated_functions[index:index + len(expected_sequence)] == expected_sequence
        ]
        require(
            len(relocated_matches) == 1,
            f"atomic littlefs scalar tag tail order changed in {relative_path}",
        )
        expected_function_sequence = list(expected_sequence)
        if (
            relative_path.startswith("components/apollo_main/")
            and "open_cfw_iar_domain_error" in expected_function_sequence
        ):
            domain_index = expected_function_sequence.index(
                "open_cfw_iar_domain_error"
            )
            sqrt_index = expected_function_sequence.index("open_cfw_iar_sqrtf")
            expected_function_sequence[domain_index], expected_function_sequence[sqrt_index] = (
                expected_function_sequence[sqrt_index],
                expected_function_sequence[domain_index],
            )
        function_names = list(overlay.get("functions", {}))
        function_matches = [
            index for index in range(len(function_names) - len(expected_function_sequence) + 1)
            if function_names[index:index + len(expected_function_sequence)]
            == expected_function_sequence
        ]
        require(
            len(function_matches) == 1,
            f"atomic littlefs scalar tag function order changed in {relative_path}",
        )
        for expected in EXPECTED_DUAL_TAG_LEAVES.values():
            function = expected["function"]
            leaves = [
                leaf
                for leaf in overlay.get("relocated_leaves", [])
                if leaf.get("function") == function
            ]
            require(
                len(leaves) == 1,
                f"{function} production leaf is not unique in {relative_path}",
            )
            leaf = leaves[0]
            source = leaf.get("source", {})
            source_expected = expected["source"]
            require(
                source.get("path") == source_expected["path"]
                and source.get("size") == source_expected["size"]
                and source.get("sha256") == source_expected["sha256"]
                and source.get("license") == "BSD-3-Clause"
                and source.get("upstream_commit") == EXPECTED_COMMIT
                and source.get("evidence") == "third_party/littlefs/PROVENANCE.json",
                f"{function} source registration changed in {relative_path}",
            )
            apple_offset = expected["profiles"]["apple-clang"][component_name][0]
            require(
                leaf.get("strict_relocation_contract") is True
                and leaf.get("expected")
                == {
                    "size": expected["leaf_size"],
                    "sha256": expected["text_sha256"],
                    "alignment": alignment,
                    "offset": apple_offset,
                    "unrelocated_sha256": expected["text_sha256"],
                }
                and leaf.get("relocations") == [],
                f"{function} Apple placement/text pins changed in {relative_path}",
            )
            linux_profile = leaf.get("toolchain_profiles", {}).get("linux-clang")
            linux_offset = expected["profiles"]["linux-clang"][component_name][0]
            if component_name == "apollo_main":
                require(
                    linux_profile
                    == {
                        "reviewed_version_prefix": "Homebrew clang version 22.1.8",
                        "expected": {
                            "size": expected["leaf_size"],
                            "sha256": expected["text_sha256"],
                            "alignment": alignment,
                            "offset": linux_offset,
                            "unrelocated_sha256": expected["text_sha256"],
                        },
                        "relocations": [],
                    },
                    f"{function} Linux placement/text pins changed in {relative_path}",
                )
            else:
                require(
                    linux_profile
                    == {"reviewed_version_prefix": "Homebrew clang version 22.1.8"}
                    and overlay["function_profiles"]["linux-clang"][function]
                    == {
                        "expected_offset": linux_offset,
                        "expected_size": expected["leaf_size"],
                    },
                    f"{function} inherited Linux pins changed in {relative_path}",
                )
            stock = expected["stock"]
            patch_sites = [
                site
                for site in overlay.get("patch_sites", [])
                if site.get("target_function") == function
            ]
            require(
                patch_sites
                == [{
                    "name": f"replace_{function.removeprefix('open_cfw_')}",
                    "runtime_address": stock[component_name]["start"],
                    "expected_size": stock["size"],
                    "expected_sha256": stock["sha256"],
                    "branch": "b_w",
                    "target_function": function,
                }],
                f"{function} patch registration changed in {relative_path}",
            )


def verify_tag_id_manifest() -> None:
    manifest_path = OPENCFW_ROOT / "manifests/g2-2.2.6.10-core-source.json"
    require(manifest_path.is_file(), "production source manifest is missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    components = manifest.get("component_overrides", {})
    for component_name, expected_regions in EXPECTED_TAG_ID_MANIFEST_REGIONS.items():
        component = components.get(component_name, {})
        regions = component.get("regions", [])
        names = [region.get("name") for region in regions]
        expected_names = [expected[0] for expected in expected_regions]
        for name in expected_names:
            require(
                names.count(name) == 1,
                f"{component_name} scalar-tag manifest region is not unique: {name}",
            )
        for name, file_offset, size, target_address, address_status in expected_regions:
            region = regions[names.index(name)]
            require(
                (
                    region.get("file_offset"),
                    region.get("size"),
                    region.get("target_address"),
                    region.get("address_status"),
                )
                == (file_offset, size, target_address, address_status),
                f"{component_name} scalar-tag manifest region changed: {name}",
            )
        stock_region_count = 4
        stock_positions = [
            names.index(name) for name in expected_names[:stock_region_count]
        ]
        require(
            stock_positions
            == list(
                range(
                    stock_positions[0],
                    stock_positions[0] + stock_region_count,
                )
            ),
            f"{component_name} scalar-tag stock split order changed",
        )
        expected_tail = expected_names[stock_region_count:]
        expected_tail += {
            "apollo_main": [
                "apollo_nanopb_decode_fixed64_source_alignment",
                "apollo_nanopb_decode_fixed64_source_leaf",
                "apollo_nanopb_read_source_leaf",
                "apollo_nanopb_buf_read_source_alignment",
                "apollo_nanopb_buf_read_source_leaf",
                "apollo_nanopb_readbyte_source_alignment",
                "apollo_nanopb_readbyte_source_leaf",
                "apollo_nanopb_istream_from_buffer_source_leaf",
                "apollo_nanopb_decode_svarint_source_leaf",
                "apollo_nanopb_decode_varint32_eof_source_alignment",
                "apollo_nanopb_decode_varint32_eof_source_leaf",
                "apollo_nanopb_decode_varint32_overflow_rodata",
                "apollo_nanopb_decode_varint32_source_alignment",
                "apollo_nanopb_decode_varint32_source_leaf",
                "apollo_nanopb_skip_string_source_alignment",
                "apollo_nanopb_skip_string_source_leaf",
                "apollo_nanopb_skip_field_source_alignment",
                "apollo_nanopb_skip_field_source_leaf",
                "apollo_nanopb_skip_field_error_rodata",
                "apollo_nanopb_read_raw_value_source_leaf",
                "apollo_nanopb_read_raw_value_error_rodata",
                "apollo_nanopb_make_string_substream_source_leaf",
                "apollo_nanopb_make_string_substream_error_rodata",
                "apollo_nanopb_decode_bool_source_leaf",
                "apollo_nanopb_dec_bool_source_leaf",
                "apollo_nanopb_dec_varint_source_alignment",
                "apollo_nanopb_dec_varint_source_leaf",
                "apollo_nanopb_dec_varint_error_rodata",
                "apollo_nanopb_dec_bytes_source_leaf",
                "apollo_nanopb_dec_bytes_error_rodata",
                "apollo_nanopb_dec_string_source_alignment",
                "apollo_nanopb_dec_string_source_leaf",
                "apollo_nanopb_dec_string_error_rodata",
                "apollo_nanopb_dec_submessage_source_alignment",
                "apollo_nanopb_dec_submessage_source_leaf",
                "apollo_nanopb_dec_submessage_error_rodata",
                "apollo_nanopb_decode_inner_source_alignment",
                "apollo_nanopb_decode_inner_source_leaf",
                "apollo_nanopb_decode_inner_error_rodata",
                "apollo_nanopb_decode_tag_source_alignment",
                "apollo_nanopb_decode_tag_source_leaf",
                "apollo_nanopb_iterator_provider_alignment",
                "apollo_nanopb_iterator_provider_source_leaf",
                "apollo_nanopb_field_iter_begin_alignment",
                "apollo_nanopb_field_iter_begin_source_leaf",
                "apollo_nanopb_field_iter_begin_extension_alignment",
                "apollo_nanopb_field_iter_begin_extension_source_leaf",
                "apollo_nanopb_field_iter_next_source_leaf",
                "apollo_nanopb_field_iter_find_alignment",
                "apollo_nanopb_field_iter_find_source_leaf",
                "apollo_nanopb_field_iter_find_extension_source_leaf",
                "apollo_nanopb_field_iter_begin_const_source_leaf",
                "apollo_nanopb_field_iter_begin_extension_const_alignment",
                "apollo_nanopb_field_iter_begin_extension_const_source_leaf",
                "apollo_nanopb_default_field_callback_source_leaf",
                "apollo_nanopb_message_set_to_defaults_source_leaf",
                "apollo_nanopb_field_set_to_default_alignment",
                "apollo_nanopb_field_set_to_default_source_leaf",
                "apollo_nanopb_decode_field_source_closure",
                "apollo_nanopb_default_extension_decoder_alignment",
                "apollo_nanopb_default_extension_decoder_source_closure",
                "apollo_nanopb_decode_extension_source_leaf",
                "apollo_nanopb_dec_fixed_length_bytes_source_closure",
                "apollo_nanopb_decode_basic_field_alignment",
                "apollo_nanopb_decode_basic_field_source_closure",
                "apollo_nanopb_decode_static_field_alignment",
                "apollo_nanopb_decode_static_field_source_closure",
                "apollo_nanopb_decode_pointer_field_alignment",
                "apollo_nanopb_decode_pointer_field_source_closure",
                "apollo_nanopb_decode_callback_field_alignment",
                "apollo_nanopb_decode_callback_field_source_closure",
                "apollo_ring_buffer_is_empty_source_leaf",
                "apollo_ring_buffer_is_full_alignment",
                "apollo_ring_buffer_is_full_source_leaf",
                "apollo_ring_buffer_init_alignment",
                "apollo_ring_buffer_init_source_leaf",
                "apollo_ring_buffer_queue_source_leaf",
                "apollo_ring_buffer_queue_arr_source_leaf",
                "apollo_ring_buffer_dequeue_source_leaf",
                "apollo_ring_buffer_dequeue_arr_source_leaf",
                "apollo_iar_memcpy_void_source_leaf",
                "apollo_iar_memcpy_aligned_void_source_leaf",
                "apollo_iar_memmove_void_source_leaf",
                "apollo_iar_domain_error_source_leaf",
                "apollo_iar_sqrtf_source_leaf",
                "apollo_iar_range_error_source_leaf",
                "apollo_iar_errno_address_source_leaf",
                "apollo_g2_advertised_name_serial_suffix_hook",
                "apollo_cmsis_irq_context_source_leaf",
                "apollo_cmsis_kernel_get_tick_count_alignment",
                "apollo_cmsis_kernel_get_tick_count_source_leaf",
                "apollo_cmsis_thread_get_id_source_leaf",
                "apollo_cmsis_message_queue_get_capacity_source_leaf",
                "apollo_cmsis_count_leaves_alignment",
                "apollo_cmsis_semaphore_get_count_source_leaf",
                "apollo_cmsis_message_queue_get_count_source_leaf",
                "apollo_cmsis_message_queue_delete_source_leaf",
                "apollo_cmsis_thread_yield_source_leaf",
                "apollo_cmsis_kernel_get_state_source_leaf",
                "apollo_cmsis_mutex_delete_alignment",
                "apollo_cmsis_mutex_delete_source_leaf",
                "apollo_cmsis_timer_is_running_alignment",
                "apollo_cmsis_timer_is_running_source_leaf",
                "apollo_cmsis_sync_ops_alignment",
                "apollo_cmsis_mutex_acquire_source_leaf",
                "apollo_cmsis_mutex_release_source_leaf",
                "apollo_cmsis_semaphore_release_source_leaf",
            ],
            "apollo_bootloader": [],
        }[component_name]
        matches = [
            index for index in range(len(names) - len(expected_tail) + 1)
            if names[index:index + len(expected_tail)] == expected_tail
        ]
        require(
            len(matches) == 1,
            f"{component_name} scalar-tag manifest tail order changed",
        )
        require(
            component.get("provider")
            == EXPECTED_TAG_ID_MANIFEST_PROVIDERS[component_name],
            f"{component_name} scalar-tag manifest provider pins changed",
        )


def verify_rewind_overlay_leaf(leaf: dict[str, Any]) -> None:
    source = leaf.get("source")
    require(
        source
        == {
            "path": EXPECTED_REWIND_SOURCE["path"],
            "size": EXPECTED_REWIND_SOURCE["size"],
            "sha256": EXPECTED_REWIND_SOURCE["sha256"],
            "license": "BSD-3-Clause",
            "origin": (
                "bounded freestanding adaptation of authenticated littlefs "
                "v2.10.1 lfs_file_rewind_ with a retained private "
                "lfs_file_seek_ provider seam"
            ),
            "upstream": (
                "https://github.com/littlefs-project/littlefs/blob/"
                f"{EXPECTED_COMMIT}/lfs.c"
            ),
            "upstream_commit": EXPECTED_COMMIT,
            "evidence": "docs/research/littlefs-file-rewind-source-audit.md",
        },
        "lfs_file_rewind_ production source registration changed",
    )
    require(
        leaf.get("strict_relocation_contract") is True,
        "lfs_file_rewind_ relocation contract is not strict",
    )
    require(
        leaf.get("relocations") == [EXPECTED_REWIND_RELOCATION],
        "lfs_file_rewind_ Apple relocation closure changed",
    )
    apple = EXPECTED_REWIND_PROFILES["apple-clang"]
    require(
        leaf.get("expected")
        == {
            "size": apple["size"],
            "sha256": apple["sha256"],
            "alignment": 4,
            "offset": apple["offset"],
            "unrelocated_sha256": apple["unrelocated_sha256"],
        },
        "lfs_file_rewind_ Apple placement/text contract changed",
    )
    linux = EXPECTED_REWIND_PROFILES["linux-clang"]
    require(
        leaf.get("toolchain_profiles", {}).get("linux-clang")
        == {
            "reviewed_version_prefix": "Homebrew clang version 22.1.8",
            "expected": {
                "size": linux["size"],
                "sha256": linux["sha256"],
                "alignment": 4,
                "offset": linux["offset"],
                "unrelocated_sha256": linux["unrelocated_sha256"],
            },
            "relocations": [EXPECTED_REWIND_RELOCATION],
        },
        "lfs_file_rewind_ Linux placement/text contract changed",
    )
    for profile in EXPECTED_REWIND_PROFILES.values():
        require(
            EXPECTED_OVERLAY_RUNTIME_ADDRESS + profile["offset"]
            == profile["runtime_address"],
            "lfs_file_rewind_ overlay/runtime placement relation changed",
        )


def verify_tag_type2_overlay_leaf(leaf: dict[str, Any]) -> None:
    require(
        leaf.get("source")
        == {
            "path": EXPECTED_TAG_TYPE2_SOURCE["path"],
            "size": EXPECTED_TAG_TYPE2_SOURCE["size"],
            "sha256": EXPECTED_TAG_TYPE2_SOURCE["sha256"],
            "license": "BSD-3-Clause",
            "origin": (
                "altered production adaptation of authenticated littlefs "
                "v2.10.1 lfs_tag_type2 using the recovered 32-bit "
                "lfs_tag_t ABI"
            ),
            "upstream": (
                "https://github.com/littlefs-project/littlefs/blob/"
                f"{EXPECTED_COMMIT}/lfs.c"
            ),
            "upstream_commit": EXPECTED_COMMIT,
            "evidence": "docs/research/littlefs-tag-type2-source-audit.md",
        },
        "lfs_tag_type2 production source registration changed",
    )
    require(
        leaf.get("strict_relocation_contract") is True,
        "lfs_tag_type2 relocation contract is not strict",
    )
    require(leaf.get("relocations") == [], "lfs_tag_type2 gained a relocation")
    apple = EXPECTED_TAG_TYPE2_PROFILES["apple-clang"]
    require(
        leaf.get("expected")
        == {
            "size": apple["size"],
            "sha256": apple["sha256"],
            "alignment": 4,
            "offset": apple["offset"],
            "unrelocated_sha256": apple["sha256"],
        },
        "lfs_tag_type2 Apple placement/text contract changed",
    )
    linux = EXPECTED_TAG_TYPE2_PROFILES["linux-clang"]
    require(
        leaf.get("toolchain_profiles", {}).get("linux-clang")
        == {
            "reviewed_version_prefix": "Homebrew clang version 22.1.8",
            "expected": {
                "size": linux["size"],
                "sha256": linux["sha256"],
                "alignment": 4,
                "offset": linux["offset"],
                "unrelocated_sha256": linux["sha256"],
            },
            "relocations": [],
        },
        "lfs_tag_type2 Linux placement/text contract changed",
    )
    for profile in EXPECTED_TAG_TYPE2_PROFILES.values():
        require(
            EXPECTED_OVERLAY_RUNTIME_ADDRESS + profile["offset"]
            == profile["runtime_address"],
            "lfs_tag_type2 overlay/runtime placement relation changed",
        )


def wide_branch_target(address: int, first: int, second: int) -> int | None:
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
        return None
    sign = (first >> 10) & 1
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    immediate = (
        (sign << 24)
        | ((1 ^ (j1 ^ sign)) << 23)
        | ((1 ^ (j2 ^ sign)) << 22)
        | ((first & 0x03FF) << 12)
        | ((second & 0x07FF) << 1)
    )
    if sign:
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFF_FFFF


def verify_rewind_stock_if_available() -> bool:
    expected_image = EXPECTED_IMAGES[0]
    image_path = OPENCFW_ROOT / expected_image["path"]
    if not image_path.is_file():
        return False
    image = image_path.read_bytes()
    require(
        sha256(image) == expected_image["image_sha256"],
        "Apollo main is not the pinned official image",
    )
    start = (
        expected_image["payload_offset"]
        + EXPECTED_REWIND_STOCK["start"]
        - expected_image["load_address"]
    )
    require(
        EXPECTED_REWIND_STOCK["end"] - EXPECTED_REWIND_STOCK["start"]
        == EXPECTED_REWIND_STOCK["size"],
        "Apollo stock lfs_file_rewind_ span size changed",
    )
    stock = image[start:start + EXPECTED_REWIND_STOCK["size"]]
    require(
        len(stock) == EXPECTED_REWIND_STOCK["size"]
        and sha256(stock) == EXPECTED_REWIND_STOCK["sha256"],
        "Apollo stock lfs_file_rewind_ span changed",
    )
    call_seams = []
    for offset in range(0, len(stock) - 3, 2):
        first, second = struct.unpack_from("<HH", stock, offset)
        target = wide_branch_target(
            EXPECTED_REWIND_STOCK["start"] + offset,
            first,
            second,
        )
        if target is not None:
            call_seams.append((offset, target))
    require(
        call_seams == [(6, EXPECTED_REWIND_STOCK["seek_seam"])],
        "Apollo stock lfs_file_rewind_ seek seam changed",
    )
    return True


def verify_tag_type2_stock_if_available() -> bool:
    expected_image = EXPECTED_IMAGES[0]
    image_path = OPENCFW_ROOT / expected_image["path"]
    if not image_path.is_file():
        return False
    image = image_path.read_bytes()
    require(
        sha256(image) == expected_image["image_sha256"],
        "Apollo main is not the pinned official image",
    )
    start = (
        expected_image["payload_offset"]
        + EXPECTED_TAG_TYPE2_STOCK["start"]
        - expected_image["load_address"]
    )
    require(
        EXPECTED_TAG_TYPE2_STOCK["end"] - EXPECTED_TAG_TYPE2_STOCK["start"]
        == EXPECTED_TAG_TYPE2_STOCK["size"],
        "Apollo stock lfs_tag_type2 span size changed",
    )
    stock = image[start:start + EXPECTED_TAG_TYPE2_STOCK["size"]]
    require(
        len(stock) == EXPECTED_TAG_TYPE2_STOCK["size"]
        and sha256(stock) == EXPECTED_TAG_TYPE2_STOCK["sha256"],
        "Apollo stock lfs_tag_type2 span changed",
    )
    require(
        stock == bytes.fromhex("000d10f4f0607047"),
        "Apollo stock lfs_tag_type2 instruction bytes changed",
    )

    payload = image[expected_image["payload_offset"]:]
    callers = []
    for offset in range(0, len(payload) - 3, 2):
        first, second = struct.unpack_from("<HH", payload, offset)
        address = expected_image["load_address"] + offset
        if (
            wide_branch_target(address, first, second)
            == EXPECTED_TAG_TYPE2_STOCK["start"]
        ):
            callers.append((address, payload[offset:offset + 4].hex()))
    require(
        callers == list(EXPECTED_TAG_TYPE2_STOCK["callers"]),
        "Apollo stock lfs_tag_type2 direct caller set changed",
    )

    outgoing = []
    for offset in range(0, len(stock) - 3, 2):
        first, second = struct.unpack_from("<HH", stock, offset)
        target = wide_branch_target(
            EXPECTED_TAG_TYPE2_STOCK["start"] + offset,
            first,
            second,
        )
        if target is not None:
            outgoing.append((offset, target))
    require(outgoing == [], "Apollo stock lfs_tag_type2 gained a call seam")
    return True


def verify_tag_id_stock_if_available() -> list[str]:
    checked: list[str] = []
    expected_stock = EXPECTED_DUAL_TAG_LEAVES["tag_id_leaf"]["stock"]
    for expected_image, component_name in zip(
        EXPECTED_IMAGES,
        ("apollo_main", "apollo_bootloader"),
    ):
        image_path = OPENCFW_ROOT / expected_image["path"]
        if not image_path.is_file():
            continue
        image = image_path.read_bytes()
        require(
            sha256(image) == expected_image["image_sha256"],
            f"{expected_image['name']} is not the pinned official image",
        )
        component = expected_stock[component_name]
        start = (
            expected_image["payload_offset"]
            + component["start"]
            - expected_image["load_address"]
        )
        require(
            start == component["file_offset"]
            and component["end"] - component["start"] == expected_stock["size"],
            f"{expected_image['name']} lfs_tag_id stock boundary changed",
        )
        stock = image[start:start + expected_stock["size"]]
        require(
            stock == bytes.fromhex("800a8005800d7047")
            and sha256(stock) == expected_stock["sha256"],
            f"{expected_image['name']} lfs_tag_id stock body changed",
        )
        payload = image[expected_image["payload_offset"]:]
        callers = []
        for offset in range(0, len(payload) - 3, 2):
            first, second = struct.unpack_from("<HH", payload, offset)
            address = expected_image["load_address"] + offset
            if wide_branch_target(address, first, second) == component["start"]:
                callers.append((address, payload[offset:offset + 4].hex()))
        require(
            callers == list(component["callers"]),
            f"{expected_image['name']} lfs_tag_id direct caller set changed",
        )
        outgoing = []
        for offset in range(0, len(stock) - 3, 2):
            first, second = struct.unpack_from("<HH", stock, offset)
            target = wide_branch_target(component["start"] + offset, first, second)
            if target is not None:
                outgoing.append((offset, target))
        require(
            outgoing == [],
            f"{expected_image['name']} lfs_tag_id gained a call seam",
        )
        checked.append(expected_image["name"])
    return checked


def verify_tag_size_stock_if_available() -> list[str]:
    checked: list[str] = []
    expected_stock = EXPECTED_DUAL_TAG_LEAVES["tag_size_leaf"]["stock"]
    for expected_image, component_name in zip(
        EXPECTED_IMAGES,
        ("apollo_main", "apollo_bootloader"),
    ):
        image_path = OPENCFW_ROOT / expected_image["path"]
        if not image_path.is_file():
            continue
        image = image_path.read_bytes()
        require(
            sha256(image) == expected_image["image_sha256"],
            f"{expected_image['name']} is not the pinned official image",
        )
        component = expected_stock[component_name]
        start = (
            expected_image["payload_offset"]
            + component["start"]
            - expected_image["load_address"]
        )
        require(
            start == component["file_offset"]
            and component["end"] - component["start"] == expected_stock["size"],
            f"{expected_image['name']} lfs_tag_size stock boundary changed",
        )
        stock = image[start:start + expected_stock["size"]]
        require(
            stock == bytes.fromhex("8005800d7047")
            and sha256(stock) == expected_stock["sha256"],
            f"{expected_image['name']} lfs_tag_size stock body changed",
        )
        payload = image[expected_image["payload_offset"]:]
        callers = []
        for offset in range(0, len(payload) - 3, 2):
            first, second = struct.unpack_from("<HH", payload, offset)
            address = expected_image["load_address"] + offset
            if wide_branch_target(address, first, second) == component["start"]:
                callers.append((address, payload[offset:offset + 4].hex()))
        require(
            callers == list(component["callers"]),
            f"{expected_image['name']} lfs_tag_size direct caller set changed",
        )
        outgoing = []
        for offset in range(0, len(stock) - 3, 2):
            first, second = struct.unpack_from("<HH", stock, offset)
            target = wide_branch_target(component["start"] + offset, first, second)
            if target is not None:
                outgoing.append((offset, target))
        require(
            outgoing == [],
            f"{expected_image['name']} lfs_tag_size gained a call seam",
        )
        checked.append(expected_image["name"])
    return checked


def verify_upstream_files() -> None:
    actual_subtree_files = {
        path.relative_to(HERE).as_posix()
        for path in HERE.rglob("*")
        if path.is_file()
    }
    require(
        actual_subtree_files == EXPECTED_SUBTREE_FILES,
        "reference-only subtree inventory changed; a port or build input may "
        "have been added",
    )

    for relative_path, expected in EXPECTED_FILES.items():
        data = (HERE / relative_path).read_bytes()
        require(len(data) == expected["size"], f"{relative_path} size changed")
        require(
            sha256(data) == expected["sha256"],
            f"{relative_path} differs from the v2.10.1 snapshot",
        )
        require(
            git_blob_sha1(data) == expected["git_blob_sha1"],
            f"{relative_path} Git blob identity changed",
        )
        require(
            b"\r" not in data,
            f"{relative_path} no longer has the upstream LF-only bytes",
        )
        require(data.endswith(b"\n"), f"{relative_path} lost its terminal LF")


def verify_version_and_config_markers() -> None:
    header = (HERE / "lfs.h").read_text(encoding="ascii")
    source = (HERE / "lfs.c").read_text(encoding="ascii")
    license_text = (HERE / "LICENSE.md").read_text(encoding="ascii")

    for marker in (
        "#define LFS_VERSION 0x0002000a",
        "#define LFS_DISK_VERSION 0x00020001",
        "struct lfs_config {",
        "#ifdef LFS_THREADSAFE",
        "int (*lock)(const struct lfs_config *c);",
        "int (*unlock)(const struct lfs_config *c);",
        "lfs_size_t compact_thresh;",
        "void *read_buffer;",
        "void *prog_buffer;",
        "void *lookahead_buffer;",
        "lfs_size_t metadata_max;",
        "lfs_size_t inline_max;",
        "#ifdef LFS_MULTIVERSION",
        "uint32_t disk_version;",
    ):
        require(marker in header, f"lfs.h lost configuration marker {marker!r}")

    config_start = header.index("struct lfs_config {")
    config_end = header.index("\n};", config_start)
    config = header[config_start:config_end]
    ordered_fields = (
        "void *context;",
        "int (*read)",
        "int (*prog)",
        "int (*erase)",
        "int (*sync)",
        "lfs_size_t read_size;",
        "lfs_size_t prog_size;",
        "lfs_size_t block_size;",
        "lfs_size_t block_count;",
        "int32_t block_cycles;",
        "lfs_size_t cache_size;",
        "lfs_size_t lookahead_size;",
        "lfs_size_t compact_thresh;",
        "void *read_buffer;",
        "void *prog_buffer;",
        "void *lookahead_buffer;",
        "lfs_size_t name_max;",
        "lfs_size_t file_max;",
        "lfs_size_t attr_max;",
        "lfs_size_t metadata_max;",
        "lfs_size_t inline_max;",
        "uint32_t disk_version;",
    )
    cursor = 0
    for field in ordered_fields:
        position = config.find(field, cursor)
        require(position >= 0, f"lfs_config field order lost {field!r}")
        cursor = position + len(field)

    # With 32-bit pointers and both optional blocks disabled, the 21 base
    # words above occupy the exact 84-byte ABI observed in both G2 images.
    base_word_count = len(ordered_fields) - 1
    require(base_word_count * 4 == 84, "recovered 84-byte ABI derivation changed")

    for marker in (
        "int lfs_format(lfs_t *lfs, const struct lfs_config *cfg)",
        "int lfs_mount(lfs_t *lfs, const struct lfs_config *cfg)",
        "LFS_ASSERT(lfs->cfg->compact_thresh",
        "LFS_ASSERT(cfg->block_count != 0);",
    ):
        require(marker in source, f"lfs.c lost source marker {marker!r}")

    for fragment in (
        "Copyright (c) 2022, The littlefs authors.",
        "Copyright (c) 2017, Arm Limited. All rights reserved.",
        "Redistribution and use in source and binary forms",
        'THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"',
    ):
        require(fragment in license_text, f"BSD-3-Clause text lost {fragment!r}")


def verify_recorded_configuration(provenance: dict[str, Any]) -> None:
    config = provenance["recovered_g2_configuration"]
    require(config["config_abi_size"] == 84, "recorded config size changed")
    require(config["target_pointer_size"] == 4, "target pointer size changed")
    require(config["target_endianness"] == "little", "target endian changed")
    require(config["read_size"] == 16, "read size changed")
    require(config["prog_size"] == 256, "program size changed")
    require(config["block_size"] == 4096, "block size changed")
    require(config["block_count"] == 3008, "block count changed")
    require(config["block_cycles"] == 500, "block cycles changed")
    require(config["cache_size"] == 4096, "cache size changed")
    require(config["lookahead_size"] == 256, "lookahead size changed")
    require(config["compact_thresh"] == 0, "compact threshold changed")
    require(config["build_options"]["LFS_THREADSAFE"] is False, "thread safety changed")
    require(
        config["build_options"]["LFS_MULTIVERSION"] is False,
        "multiversion setting changed",
    )
    require(config["build_options"]["LFS_YES_TRACE"] is False, "trace setting changed")

    recorded_images = config["official_images"]
    require(len(recorded_images) == len(EXPECTED_IMAGES), "image inventory changed")
    for recorded, expected in zip(recorded_images, EXPECTED_IMAGES):
        require(recorded["name"] == expected["name"], "image order/name changed")
        require(recorded["path"] == expected["path"], "image path changed")
        require(
            recorded["image_sha256"] == expected["image_sha256"],
            f"{expected['name']} image hash changed",
        )
        require(
            int(recorded["load_address"], 16) == expected["load_address"],
            f"{expected['name']} load address changed",
        )
        require(
            recorded["payload_offset"] == expected["payload_offset"],
            f"{expected['name']} payload offset changed",
        )
        require(
            int(recorded["config_address"], 16) == expected["config_address"],
            f"{expected['name']} config address changed",
        )
        require(
            recorded["config_size"] == expected["config_size"],
            f"{expected['name']} config size changed",
        )
        require(
            recorded["config_sha256"] == expected["config_sha256"],
            f"{expected['name']} config hash changed",
        )


def verify_official_image_configs() -> list[str]:
    checked: list[str] = []
    for expected in EXPECTED_IMAGES:
        image_path = OPENCFW_ROOT / expected["path"]
        if not image_path.is_file():
            continue

        image = image_path.read_bytes()
        require(
            sha256(image) == expected["image_sha256"],
            f"{expected['name']} is not the pinned official image",
        )

        start = (
            expected["payload_offset"]
            + expected["config_address"]
            - expected["load_address"]
        )
        end = start + expected["config_size"]
        require(
            0 <= start < end <= len(image),
            f"{expected['name']} config span is outside the image",
        )
        span = image[start:end]
        require(
            sha256(span) == expected["config_sha256"],
            f"{expected['name']} 84-byte config-span hash changed",
        )

        words = struct.unpack("<21I", span)
        expected_words = (
            0,
            *expected["callbacks"],
            *EXPECTED_COMMON_CONFIG_WORDS,
        )
        require(
            words == expected_words,
            f"{expected['name']} decoded lfs_config words changed",
        )
        checked.append(expected["name"])
    return checked


def main() -> None:
    provenance = verify_provenance()
    verify_production_integration(provenance)
    verify_upstream_files()
    verify_version_and_config_markers()
    verify_recorded_configuration(provenance)
    verify_production_allowlist()
    verify_tag_id_manifest()
    checked = verify_official_image_configs()
    rewind_stock_checked = verify_rewind_stock_if_available()
    tag_type2_stock_checked = verify_tag_type2_stock_if_available()
    tag_id_stock_checked = verify_tag_id_stock_if_available()
    tag_size_stock_checked = verify_tag_size_stock_if_available()
    image_status = (
        f"; official config spans checked: {', '.join(checked)}"
        if checked
        else "; official images absent, config-span checks skipped"
    )
    rewind_status = (
        "; Apollo rewind stock span/seam checked"
        if rewind_stock_checked
        else "; official Apollo image absent, rewind stock check skipped"
    )
    tag_type2_status = (
        "; Apollo lfs_tag_type2 stock span/callers checked"
        if tag_type2_stock_checked
        else "; official Apollo image absent, lfs_tag_type2 stock check skipped"
    )
    tag_id_status = (
        f"; lfs_tag_id stock spans/callers checked: {', '.join(tag_id_stock_checked)}"
        if tag_id_stock_checked
        else "; official images absent, lfs_tag_id stock checks skipped"
    )
    tag_size_status = (
        "; lfs_tag_size stock spans/callers checked: "
        f"{', '.join(tag_size_stock_checked)}"
        if tag_size_stock_checked
        else "; official images absent, lfs_tag_size stock checks skipped"
    )
    print(
        "littlefs v2.10.1 source-equivalent snapshot, BSD-3-Clause notice, "
        "bounded production allowlist, "
        "rewind/tag-validity/type1/type2/type3/id/size/chunk "
        "provenance, hashes, ABI, and no-format/no-erase policy: "
        f"OK{image_status}{rewind_status}{tag_type2_status}"
        f"{tag_id_status}{tag_size_status}"
    )


if __name__ == "__main__":
    main()
