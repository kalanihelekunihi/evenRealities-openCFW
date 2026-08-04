#!/usr/bin/env python3
"""Fail-closed offline verification for the nanopb 0.4.9 snapshot."""

from __future__ import annotations

import hashlib
import json
import stat
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROVENANCE = HERE / "PROVENANCE.json"
EXPECTED_PROVENANCE_SIZE = 56997
EXPECTED_PROVENANCE_SHA256 = "b4341b0ed98a697a0156d9d0c9fca2a03bed304ca890f56ea70c7eb590fa4283"
EXPECTED_RECORDS_SHA256 = "bb36791b9ae9a6cff412516db0b93911240fff8e8109d56136ca76173ac3a3e0"
EXPECTED_TAG_OBJECT = "b3056c326da0e6cf702fd13ae2fe63225caa0801"
EXPECTED_TAG_SIZE = 151
EXPECTED_TAG_SHA256 = "155ac515df4fdf4d006e096008c6c9ee1e50894b829187f7cb1b214804646152"
EXPECTED_COMMIT = "98bf4db69897b53434f3d0ba72e0a3ab1a902824"
EXPECTED_COMMIT_SIZE = 250
EXPECTED_COMMIT_SHA256 = "e6ecbdf1157055f4327b9083265e0cd807e51211d5cd767ea6d2ae7f172dbdce"
EXPECTED_PARENT = "2c50b0298dbb2008d0123f340dff7b522d315cea"
EXPECTED_TREE = "2c4c260bcff3f9f7081238d377274dd385d76582"
EXPECTED_TREE_CLOSURE_SIZE = 6558
EXPECTED_TREE_CLOSURE_SHA256 = "7604008d26767601712b60dc125baa7da9ebfdea907556b79ea677b79137c16e"
EXPECTED_ROOT_ENTRY_COUNT = 38
EXPECTED_CONFIG_SIZE = 1551
EXPECTED_CONFIG_SHA256 = "ae758999d239e49e2d5c5bf6de3f4aef3aab5cd3c29d8de65c4db301c62899db"
EXPECTED_IMAGE_SIZE = 3_523_396
EXPECTED_IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
EXPECTED_RUNTIME_SHA256 = "ff42ff15a4574a6485b8b3e16de986679f059f2358d5d354b29f713760f43ea2"
EXPECTED_SKIP_SOURCE_PATH = "components/shared/nanopb/runtime_nanopb_skip_varint.c"
EXPECTED_SKIP_SOURCE_SIZE = 1925
EXPECTED_SKIP_SOURCE_SHA256 = "89e53ebc01a2d28c4a94ac4a38313b8213788a23ed55bf767a9e8a5c6d961225"
EXPECTED_SKIP_HEADER_PATH = "components/shared/nanopb/runtime_nanopb_skip_varint.h"
EXPECTED_SKIP_HEADER_SIZE = 2401
EXPECTED_SKIP_HEADER_SHA256 = "30a8aea087894af29396746a31bbebfc9195e12ee4d66e79b4b637828eeab103"
EXPECTED_SKIP_UPSTREAM_START = 8160
EXPECTED_SKIP_UPSTREAM_END = 8360
EXPECTED_SKIP_UPSTREAM_SHA256 = "4c9c2629d6c8bf7e8e986a8cb54413d39a804ddb0e848c64aae009d3b10aac62"
EXPECTED_CLOSE_SOURCE_PATH = (
    "components/shared/nanopb/runtime_nanopb_close_string_substream.c"
)
EXPECTED_CLOSE_SOURCE_SIZE = 2061
EXPECTED_CLOSE_SOURCE_SHA256 = "736e7ec228f9282ba5b093fd482441e6e2017fff860d989dc3aadb2bdeff0fcb"
EXPECTED_CLOSE_HEADER_PATH = (
    "components/shared/nanopb/runtime_nanopb_close_string_substream.h"
)
EXPECTED_CLOSE_HEADER_SIZE = 2537
EXPECTED_CLOSE_HEADER_SHA256 = "851af370162d79f4bd0be8b8bb9a5731d47cf02527078b9e278019340f2d65d4"
EXPECTED_CLOSE_UPSTREAM_START = 11223
EXPECTED_CLOSE_UPSTREAM_END = 11568
EXPECTED_CLOSE_UPSTREAM_SHA256 = "527e5ca208a04366c0911baf793af7dc7045fd73014eefc6e31ce3a8b6dc332f"
EXPECTED_FIXED32_SOURCE_PATH = (
    "components/shared/nanopb/runtime_nanopb_decode_fixed32.c"
)
EXPECTED_FIXED32_SOURCE_SIZE = 1975
EXPECTED_FIXED32_SOURCE_SHA256 = "fefd8a899174fb9332c366df691dc2c8ec6f4792f3fd464b65dbb573ace8ee19"
EXPECTED_FIXED32_HEADER_PATH = (
    "components/shared/nanopb/runtime_nanopb_decode_fixed32.h"
)
EXPECTED_FIXED32_HEADER_SIZE = 1750
EXPECTED_FIXED32_HEADER_SHA256 = "738e4c7d4ea983b0ba967fa42cdcc61cb2e20837531bc6176b7f95a5fe8e2460"
EXPECTED_FIXED32_UPSTREAM_START = 43210
EXPECTED_FIXED32_UPSTREAM_END = 43828
EXPECTED_FIXED32_UPSTREAM_SHA256 = "1952ee1f743334c82f206c910392f63b2e7fdd702cbdd404dae04367aa8ae518"
EXPECTED_FIXED64_SOURCE_PATH = (
    "components/shared/nanopb/runtime_nanopb_decode_fixed64.c"
)
EXPECTED_FIXED64_SOURCE_SIZE = 2083
EXPECTED_FIXED64_SOURCE_SHA256 = "865fa587e7b783e83f24107e52bf3010053d0660b06dc0ac2e7f72bb8ad969bc"
EXPECTED_FIXED64_HEADER_PATH = (
    "components/shared/nanopb/runtime_nanopb_decode_fixed64.h"
)
EXPECTED_FIXED64_HEADER_SIZE = 1726
EXPECTED_FIXED64_HEADER_SHA256 = "6394df89057700817341e0550ae21033629d3a1ea458d5a68a6edc2b233cc6bd"
EXPECTED_FIXED64_UPSTREAM_START = 43854
EXPECTED_FIXED64_UPSTREAM_END = 44688
EXPECTED_FIXED64_UPSTREAM_SHA256 = "7f9da692a631280aa5b91a5d08440ac68f5060a64814997dde8dcbdb2f0b4974"
EXPECTED_READ_SOURCE_PATH = "components/shared/nanopb/runtime_nanopb_read.c"
EXPECTED_READ_SOURCE_SIZE = 2944
EXPECTED_READ_SOURCE_SHA256 = "e4f99df8121553d4cb6d6c2f94aa7ef1b1445efd200cee4d872dd75894d24089"
EXPECTED_READ_HEADER_PATH = "components/shared/nanopb/runtime_nanopb_read.h"
EXPECTED_READ_HEADER_SIZE = 2032
EXPECTED_READ_HEADER_SHA256 = "22203e33b8cd9e07b94d24477ffb8a6f096a9ea8393c5723071b5f12c3ec4296"
EXPECTED_READ_UPSTREAM_START = 3745
EXPECTED_READ_UPSTREAM_END = 4559
EXPECTED_READ_UPSTREAM_SHA256 = "3b69f6f4eb56a87c3f8a7f9ac30ac7573328c560047cbc5b2295daceef18fb1c"
EXPECTED_BUF_SOURCE_PATH = "components/shared/nanopb/runtime_nanopb_buf_read.c"
EXPECTED_BUF_SOURCE_SIZE = 1685
EXPECTED_BUF_SOURCE_SHA256 = "d7e464755bb4eff09207d33f1eb6b98ea49b43a91291001652d867f27bcd1bec"
EXPECTED_READBYTE_SOURCE_PATH = "components/shared/nanopb/runtime_nanopb_readbyte.c"
EXPECTED_READBYTE_SOURCE_SIZE = 2065
EXPECTED_READBYTE_SOURCE_SHA256 = "f0cfa08ee31a67544f225830a023c38dd2c2e2903bfe6466ddcfc0a9dfb4bdbb"
EXPECTED_PRIVATE_HEADER_PATH = (
    "components/shared/nanopb/runtime_nanopb_private_read_pair.h"
)
EXPECTED_PRIVATE_HEADER_SIZE = 2046
EXPECTED_PRIVATE_HEADER_SHA256 = "00bb2c9885f951a711d60c37b02b77f3e679742ddce4255b0f108cec280535e4"
EXPECTED_PRIVATE_AUDIT_PATH = (
    "docs/research/nanopb-private-read-pair-source-audit.md"
)
EXPECTED_PRIVATE_AUDIT_SIZE = 11344
EXPECTED_PRIVATE_AUDIT_SHA256 = (
    "f025b71ce15c5b8f959524d34296e985a490cbcd43e81fc2f15428504526d075"
)
EXPECTED_ISTREAM_SOURCE_PATH = (
    "components/shared/nanopb/runtime_nanopb_istream_from_buffer.c"
)
EXPECTED_ISTREAM_SOURCE_SIZE = 1741
EXPECTED_ISTREAM_SOURCE_SHA256 = (
    "f56a603644c5e9cd85781f8d3be2c69e85e458c48fa7ecd8633d6c6a9dbda3d9"
)
EXPECTED_ISTREAM_HEADER_PATH = (
    "components/shared/nanopb/runtime_nanopb_istream_from_buffer.h"
)
EXPECTED_ISTREAM_HEADER_SIZE = 1290
EXPECTED_ISTREAM_HEADER_SHA256 = (
    "b72524945afeec8eb3f304b8a7e0002c0d842598a908ddb82f59cc4894fc773f"
)
EXPECTED_ISTREAM_AUDIT_PATH = (
    "docs/research/nanopb-istream-from-buffer-source-audit.md"
)
EXPECTED_ISTREAM_AUDIT_SIZE = 5333
EXPECTED_ISTREAM_AUDIT_SHA256 = (
    "5904de4d352cb2d891f17e56568e6feb6dd94f5251a35c012d32eb3478947278"
)
EXPECTED_ISTREAM_UPSTREAM_START = 5114
EXPECTED_ISTREAM_UPSTREAM_END = 5692
EXPECTED_ISTREAM_UPSTREAM_SHA256 = (
    "087c2b851d9ea55d5a81d70a37a88385ee7fe8db86daef34ea3d0584183b0b13"
)
EXPECTED_SVARINT_SOURCE_PATH = (
    "components/shared/nanopb/runtime_nanopb_decode_svarint.c"
)
EXPECTED_SVARINT_SOURCE_SIZE = 1943
EXPECTED_SVARINT_SOURCE_SHA256 = (
    "f361cafc8813257e16fafb9ee986c88c632eb2c7edc604dcb02e27ec85a7df4d"
)
EXPECTED_SVARINT_HEADER_PATH = (
    "components/shared/nanopb/runtime_nanopb_decode_svarint.h"
)
EXPECTED_SVARINT_HEADER_SIZE = 1789
EXPECTED_SVARINT_HEADER_SHA256 = (
    "d1ca3c0520784c4837c9570416934c7884eeeba2eba2a42091cd040d5222e72c"
)
EXPECTED_SVARINT_AUDIT_PATH = (
    "docs/research/nanopb-decode-svarint-source-audit.md"
)
EXPECTED_SVARINT_AUDIT_SIZE = 12820
EXPECTED_SVARINT_AUDIT_SHA256 = (
    "b483e5b1915f54e99e8aefd047ece54153aadc6df4af51cdc4ef1cf81cc983d0"
)
EXPECTED_SVARINT_UPSTREAM_START = 42912
EXPECTED_SVARINT_UPSTREAM_END = 43210
EXPECTED_SVARINT_UPSTREAM_SHA256 = (
    "df1caa71053163bdefaea7d6b19bdc72f10c63f09430003b88f10fb7dac3ff6e"
)
EXPECTED_VARINT32_SOURCE_PATH = (
    "components/shared/nanopb/runtime_nanopb_decode_varint32.c"
)
EXPECTED_VARINT32_SOURCE_SIZE = 3642
EXPECTED_VARINT32_SOURCE_SHA256 = (
    "6938f17fc8faefdc1006cc05f9b7959e80fba771749ca0d9e67716e9ed0d2e04"
)
EXPECTED_VARINT32_HEADER_PATH = (
    "components/shared/nanopb/runtime_nanopb_decode_varint32.h"
)
EXPECTED_VARINT32_HEADER_SIZE = 1543
EXPECTED_VARINT32_HEADER_SHA256 = (
    "46ad826405762ed52cee0797b0d93fc22f74b6f92aa012d26adf1b70609c4f7c"
)
EXPECTED_VARINT32_AUDIT_PATH = (
    "docs/research/nanopb-decode-varint32-pair-source-audit.md"
)
EXPECTED_VARINT32_AUDIT_SIZE = 8938
EXPECTED_VARINT32_AUDIT_SHA256 = (
    "be0511c1dd4162585aa0478c5242c25e0d34d08ea6331d297c67636f784a8893"
)
EXPECTED_SKIP_STRING_SOURCE_PATH = (
    "components/shared/nanopb/runtime_nanopb_skip_string.c"
)
EXPECTED_SKIP_STRING_SOURCE_SIZE = 1688
EXPECTED_SKIP_STRING_SOURCE_SHA256 = (
    "b1f492b0358e51ce89db622e4af13a7f1eef7ffce9fc81fd954609cdcd934876"
)
EXPECTED_SKIP_STRING_HEADER_PATH = (
    "components/shared/nanopb/runtime_nanopb_skip_string.h"
)
EXPECTED_SKIP_STRING_HEADER_SIZE = 1732
EXPECTED_SKIP_STRING_HEADER_SHA256 = (
    "807fb52ae19de372024ebea64268aca011e573e9ad6d4247e911b2e037058303"
)
EXPECTED_SKIP_STRING_AUDIT_PATH = (
    "docs/research/nanopb-skip-string-source-audit.md"
)
EXPECTED_SKIP_STRING_AUDIT_SIZE = 6632
EXPECTED_SKIP_STRING_AUDIT_SHA256 = (
    "e1465b8f8fc220907f811df2c354e91a2e1a4e7149edeb4c56ffa7d94246e2ee"
)
EXPECTED_SKIP_STRING_RECORD_SHA256 = (
    "81d86cfab165d8cc7735fca11da10d9ca149c1d7cb5f1118ca0b652a896fa6bc"
)
EXPECTED_SKIP_STRING_UPSTREAM_START = 8362
EXPECTED_SKIP_STRING_UPSTREAM_END = 8661
EXPECTED_SKIP_STRING_UPSTREAM_SHA256 = (
    "8da14b4cc741fc15884b11d3447d0c2c529f65c31b3823170837229d36f81585"
)
LOAD_BASE = 0x00437FE0
RUNTIME_START = 0x0048F000
RUNTIME_END = 0x00491400

EXPECTED_SOURCE_PATHS = [
    "LICENSE.txt",
    "pb.h",
    "pb_common.c",
    "pb_common.h",
    "pb_decode.c",
    "pb_decode.h",
    "pb_encode.c",
    "pb_encode.h",
]
METADATA_PATHS = {
    ".gitattributes",
    "PROVENANCE.json",
    "README.openCFW.md",
    "g2-config/pb_g2_options.h",
    "upstream/98bf4db69897b53434f3d0ba72e0a3ab1a902824.commit",
    "upstream/b3056c326da0e6cf702fd13ae2fe63225caa0801.tag",
    "upstream/trees.json",
    "verify_snapshot.py",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_object_sha1(kind: str, data: bytes) -> str:
    header = f"{kind} {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data, usedforsecurity=False).hexdigest()


def canonical_sha256(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(raw)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"nanopb snapshot verification failed: {message}")


def verify_istream_provenance(selection: dict[str, Any]) -> None:
    production = selection["production_istream_from_buffer_leaf"]
    require(
        set(production)
        == {
            "upstream_function", "upstream_source", "upstream_commit",
            "upstream_definition_span", "upstream_definition_size",
            "upstream_definition_sha256", "local_source",
            "local_source_size", "local_source_sha256", "local_header",
            "local_header_size", "local_header_sha256", "stock_span",
            "stock_size", "stock_sha256", "stock_topology",
            "canonical_callback_identity", "relocations",
            "toolchain_profiles", "manifest_regions", "evidence",
            "evidence_size", "evidence_sha256", "bootloader_homolog",
            "configuration", "qualification",
        },
        "bounded pb_istream_from_buffer provenance schema changed",
    )
    require(
        {
            key: production[key]
            for key in (
                "upstream_function", "upstream_source", "upstream_commit",
                "upstream_definition_span", "upstream_definition_size",
                "upstream_definition_sha256", "local_source",
                "local_source_size", "local_source_sha256", "local_header",
                "local_header_size", "local_header_sha256", "stock_span",
                "stock_size", "stock_sha256", "canonical_callback_identity",
                "manifest_regions", "evidence", "evidence_size",
                "evidence_sha256", "bootloader_homolog", "configuration",
            )
        }
        == {
            "upstream_function": "pb_istream_from_buffer",
            "upstream_source": "pb_decode.c",
            "upstream_commit": EXPECTED_COMMIT,
            "upstream_definition_span": "pb_decode.c bytes [5114,5692)",
            "upstream_definition_size": 578,
            "upstream_definition_sha256": EXPECTED_ISTREAM_UPSTREAM_SHA256,
            "local_source": EXPECTED_ISTREAM_SOURCE_PATH,
            "local_source_size": EXPECTED_ISTREAM_SOURCE_SIZE,
            "local_source_sha256": EXPECTED_ISTREAM_SOURCE_SHA256,
            "local_header": EXPECTED_ISTREAM_HEADER_PATH,
            "local_header_size": EXPECTED_ISTREAM_HEADER_SIZE,
            "local_header_sha256": EXPECTED_ISTREAM_HEADER_SHA256,
            "stock_span": "[0x0048F49C,0x0048F4B8)",
            "stock_size": 28,
            "stock_sha256": (
                "852314bb8f86dcbd550deb0f51bc285b"
                "662e39c1b4fae66690c44a7bf4f7a674"
            ),
            "canonical_callback_identity": "0x0048F3A5",
            "manifest_regions": {
                "entry_replacement": (
                    "nanopb_istream_from_buffer_source_replacement"
                ),
                "source_leaf": (
                    "apollo_nanopb_istream_from_buffer_source_leaf"
                ),
            },
            "evidence": EXPECTED_ISTREAM_AUDIT_PATH,
            "evidence_size": EXPECTED_ISTREAM_AUDIT_SIZE,
            "evidence_sha256": EXPECTED_ISTREAM_AUDIT_SHA256,
            "bootloader_homolog": False,
            "configuration": "g2-config/pb_g2_options.h",
        },
        "bounded pb_istream_from_buffer provenance changed",
    )
    require(
        production["stock_topology"]
        == {
            "direct_caller_count": 30,
            "alternate_ingress_count": 0,
            "interior_ingress_count": 0,
            "stored_pointer_ingress_count": 0,
        },
        "pb_istream_from_buffer topology changed",
    )
    relocations = [
        {
            "offset": offset,
            "type": kind,
            "symbol": "open_cfw_nanopb_stock_buffer_read_identity",
            "target_address": "0x0048F3A5",
        }
        for offset, kind in (
            (0, "R_ARM_THM_MOVW_ABS_NC"),
            (4, "R_ARM_THM_MOVT_ABS"),
        )
    ]
    require(
        production["relocations"] == relocations,
        "pb_istream_from_buffer relocation provenance changed",
    )
    require(
        production["toolchain_profiles"]
        == {
            "apple-clang": {
                "size": 20, "alignment": 4, "offset": 124896,
                "runtime_address": "0x007B2B04",
                "unrelocated_sha256": (
                    "d106ce1009ddcbd4d39a7c56edbcd51f"
                    "50d4cfa6768f78d224ea988aa9a416d7"
                ),
                "relocated_sha256": (
                    "af3357e8178ab650d5476d0ad0fbfee0"
                    "b44cdb288d9251da909b3ba7a1de92c4"
                ),
                "entry_patch_sha256": (
                    "e2e120080f18fdd443e08a5def120575"
                    "a2eae21139a5276f3f8fbb53e1aea6dd"
                ),
            },
            "linux-clang": {
                "size": 22, "alignment": 4, "offset": 126720,
                "runtime_address": "0x007B3224",
                "unrelocated_sha256": (
                    "6c23e37c9468d866db2e2cb6bf0ce8e"
                    "103fb34df1078e740b4b8d5d799c257ff"
                ),
                "relocated_sha256": (
                    "59438f30232883560f65ad4e58ff97c0"
                    "5dcdffdb6287fffcb7c1b79487df436d"
                ),
                "entry_patch_sha256": (
                    "902daf1332ace8eae1d3f71e324ddbc0"
                    "3ec2542d93530fa876f24228d40c86ed"
                ),
            },
        },
        "pb_istream_from_buffer profile provenance changed",
    )


def verify_svarint_provenance(selection: dict[str, Any]) -> None:
    """Authenticate signed-varint source, topology, placement, and ownership."""
    production = selection["production_decode_svarint_leaf"]
    require(
        {
            key: production[key]
            for key in (
                "upstream_function", "upstream_source", "upstream_commit",
                "upstream_definition_span", "upstream_definition_size",
                "upstream_definition_sha256", "local_source",
                "local_source_size", "local_source_sha256", "local_header",
                "local_header_size", "local_header_sha256", "stock_span",
                "stock_size", "stock_sha256", "source_dependency",
                "manifest_regions", "evidence", "evidence_size",
                "evidence_sha256", "bootloader_homolog", "configuration",
            )
        }
        == {
            "upstream_function": "pb_decode_svarint",
            "upstream_source": "pb_decode.c",
            "upstream_commit": EXPECTED_COMMIT,
            "upstream_definition_span": "pb_decode.c bytes [42912,43210)",
            "upstream_definition_size": 298,
            "upstream_definition_sha256": EXPECTED_SVARINT_UPSTREAM_SHA256,
            "local_source": EXPECTED_SVARINT_SOURCE_PATH,
            "local_source_size": EXPECTED_SVARINT_SOURCE_SIZE,
            "local_source_sha256": EXPECTED_SVARINT_SOURCE_SHA256,
            "local_header": EXPECTED_SVARINT_HEADER_PATH,
            "local_header_size": EXPECTED_SVARINT_HEADER_SIZE,
            "local_header_sha256": EXPECTED_SVARINT_HEADER_SHA256,
            "stock_span": "[0x00490150,0x00490190)",
            "stock_size": 64,
            "stock_sha256": (
                "80b24be422cf924f3ae1b79669312535d"
                "c0d5a56dd88be8a6b9e4ee5ff064048"
            ),
            "source_dependency": "open_cfw_nanopb_decode_varint",
            "manifest_regions": {
                "entry_replacement": "nanopb_decode_svarint_source_replacement",
                "source_leaf": "apollo_nanopb_decode_svarint_source_leaf",
            },
            "evidence": EXPECTED_SVARINT_AUDIT_PATH,
            "evidence_size": EXPECTED_SVARINT_AUDIT_SIZE,
            "evidence_sha256": EXPECTED_SVARINT_AUDIT_SHA256,
            "bootloader_homolog": False,
            "configuration": "g2-config/pb_g2_options.h",
        },
        "bounded pb_decode_svarint provenance changed",
    )
    require(
        production["stock_topology"]
        == {
            "direct_callers": ["0x00490290"],
            "direct_caller_count": 1,
            "alternate_ingress_count": 0,
            "interior_ingress_count": 0,
            "stored_pointer_ingress_count": 0,
        },
        "pb_decode_svarint topology changed",
    )
    direct_call = [{
        "offset": 8,
        "type": "R_ARM_THM_CALL",
        "symbol": "open_cfw_nanopb_decode_varint",
        "target_function": "open_cfw_nanopb_decode_varint",
    }]
    require(
        production["relocations"] == direct_call,
        "pb_decode_svarint relocation provenance changed",
    )
    require(
        production["toolchain_profiles"]
        == {
            "apple-clang": {
                "compiler": "Apple clang version 21.0.0 (clang-2100.3.27.1)",
                "object_size": 972,
                "object_sha256": (
                    "ac61ef30926a714ee4338414dcdc0de3"
                    "04d50b866f69a3f7c625b12c5d5a8435"
                ),
                "size": 54,
                "alignment": 4,
                "offset": 124916,
                "runtime_address": "0x007B2B18",
                "unrelocated_sha256": (
                    "19e103f83ab8879d36eb1b0513bf5416"
                    "01e40bc82e69e0dc252308c0646d1286"
                ),
                "relocated_sha256": (
                    "1b181a82adbbb72dc6fc09b1b70dd48f"
                    "4c0eefdf25a8c4e71701710cb12dae3f"
                ),
                "entry_patch_sha256": (
                    "e8c5601b86e9a38362fb292b0a8ba702"
                    "50d2ccc3094d0c8c117b1c33f5bf11cc"
                ),
            },
            "linux-clang": {
                "compiler": "Homebrew clang version 22.1.8",
                "reviewed_source_root": (
                    "/Users/kalani/Repo/SybilSightABCD/openCFW"
                ),
                "object_size": 968,
                "object_sha256": (
                    "866820ef347453a3cbf2feed221eeab0"
                    "b571a9b79b6988cc17d2861b1aeaced5"
                ),
                "size": 50,
                "alignment": 4,
                "offset": 126744,
                "runtime_address": "0x007B323C",
                "unrelocated_sha256": (
                    "3617ea95d4a2cbabf3a1abb375e57232"
                    "3fffcebfa68cb4e19874cb4a831d9662"
                ),
                "relocated_sha256": (
                    "63e4707f5fd537094855d38f6b4df857"
                    "8b77644c131e180db2e682d32fbc1fab"
                ),
                "entry_patch_sha256": (
                    "e6bb4ee4baec73757a5f465cf99a32e7"
                    "87fb25bd651b2b16e2e76fda4c6d18fd"
                ),
            }
        },
        "pb_decode_svarint toolchain profile provenance changed",
    )
    require(
        "not proof" in production["qualification"]
        and "broader pristine" in production["qualification"],
        "pb_decode_svarint qualification changed",
    )


def verify_varint32_provenance(selection: dict[str, Any]) -> None:
    """Authenticate both varint32 leaves independently and their shared closure."""
    private = selection["production_decode_varint32_eof_leaf"]
    public = selection["production_decode_varint32_leaf"]
    common_keys = {
        "license", "upstream_function", "pair_order", "upstream_source",
        "upstream_commit", "upstream_definition_span",
        "upstream_definition_size", "upstream_definition_sha256",
        "upstream_extraction_rule", "local_source", "local_source_size",
        "local_source_sha256", "local_header", "local_header_size",
        "local_header_sha256", "stock_span", "stock_size", "stock_sha256",
        "patch_region", "stock_topology", "source_dependency_calls",
        "relocations", "toolchain_profiles", "manifest_regions", "evidence",
        "evidence_size", "evidence_sha256", "bootloader_homolog",
        "configuration", "qualification",
    }
    require(set(private) == common_keys | {"literal_closure"},
            "private pb_decode_varint32 provenance schema changed")
    require(set(public) == common_keys,
            "public pb_decode_varint32 provenance schema changed")
    common = {
        "license": "Zlib",
        "upstream_source": "pb_decode.c",
        "upstream_commit": EXPECTED_COMMIT,
        "local_source": EXPECTED_VARINT32_SOURCE_PATH,
        "local_source_size": EXPECTED_VARINT32_SOURCE_SIZE,
        "local_source_sha256": EXPECTED_VARINT32_SOURCE_SHA256,
        "local_header": EXPECTED_VARINT32_HEADER_PATH,
        "local_header_size": EXPECTED_VARINT32_HEADER_SIZE,
        "local_header_sha256": EXPECTED_VARINT32_HEADER_SHA256,
        "evidence": EXPECTED_VARINT32_AUDIT_PATH,
        "evidence_size": EXPECTED_VARINT32_AUDIT_SIZE,
        "evidence_sha256": EXPECTED_VARINT32_AUDIT_SHA256,
        "bootloader_homolog": False,
        "configuration": "g2-config/pb_g2_options.h",
    }
    for name, record in (("private", private), ("public", public)):
        require(
            all(record.get(key) == value for key, value in common.items()),
            f"pb_decode_varint32 {name} source/header/evidence contract changed",
        )
        require(
            "compatibility baseline" in record["qualification"]
            and "not proof" in record["qualification"]
            and "No bootloader homolog" in record["qualification"]
            and "hardware execution remain deferred" in record["qualification"],
            f"pb_decode_varint32 {name} qualification changed",
        )
        require(
            "Brace-balanced C definition" in record["upstream_extraction_rule"]
            and "stop immediately after" in record["upstream_extraction_rule"],
            f"pb_decode_varint32 {name} extraction rule changed",
        )

    require(
        [private["pair_order"], public["pair_order"]] == [0, 1],
        "pb_decode_varint32 pair ordering changed",
    )
    require(
        {
            key: private[key]
            for key in (
                "upstream_function", "upstream_definition_span",
                "upstream_definition_size", "upstream_definition_sha256",
                "stock_span", "stock_size", "stock_sha256",
                "patch_region", "source_dependency_calls", "manifest_regions",
            )
        }
        == {
            "upstream_function": "pb_decode_varint32_eof",
            "upstream_definition_span": "pb_decode.c bytes [5762,7483)",
            "upstream_definition_size": 1721,
            "upstream_definition_sha256": (
                "66833ae2defb892aa17162625ef107bda"
                "03be44e73f0b120d48e6d2b52770e2c"
            ),
            "stock_span": "[0x0048F4B8,0x0048F5AE)",
            "stock_size": 246,
            "stock_sha256": (
                "8583fa17383d72bbdcab6c2a7a20369d"
                "c0598d3ac3061feaf8a7b29dfa520150"
            ),
            "patch_region": {
                "name": "replace_nanopb_decode_varint32_eof",
                "runtime_address": "0x0048F4B8", "size": 246,
                "stock_sha256": (
                    "8583fa17383d72bbdcab6c2a7a20369d"
                    "c0598d3ac3061feaf8a7b29dfa520150"
                ),
            },
            "source_dependency_calls": [
                "open_cfw_nanopb_readbyte", "open_cfw_nanopb_readbyte"
            ],
            "manifest_regions": {
                "entry_replacement": "nanopb_decode_varint32_eof_source_replacement",
                "source_alignment": "apollo_nanopb_decode_varint32_eof_source_alignment",
                "source_leaf": "apollo_nanopb_decode_varint32_eof_source_leaf",
                "literal_closure": "apollo_nanopb_decode_varint32_overflow_rodata",
            },
        },
        "private pb_decode_varint32 provenance changed",
    )
    require(
        {
            key: public[key]
            for key in (
                "upstream_function", "upstream_definition_span",
                "upstream_definition_size", "upstream_definition_sha256",
                "stock_span", "stock_size", "stock_sha256",
                "patch_region", "source_dependency_calls", "manifest_regions",
            )
        }
        == {
            "upstream_function": "pb_decode_varint32",
            "upstream_definition_span": "pb_decode.c bytes [7485,7617)",
            "upstream_definition_size": 132,
            "upstream_definition_sha256": (
                "ef3f2bd19c12b07ca055ab63f8e82ea6"
                "f4b34e67aefb277435092e7485834f0f"
            ),
            "stock_span": "[0x0048F5AE,0x0048F5B8)",
            "stock_size": 10,
            "stock_sha256": (
                "48218a658cffd7aeddfb623c9d0e7bd0"
                "38ceb2a6898e9f8d08b10d5779f4f79b"
            ),
            "patch_region": {
                "name": "replace_nanopb_decode_varint32",
                "runtime_address": "0x0048F5AE", "size": 10,
                "stock_sha256": (
                    "48218a658cffd7aeddfb623c9d0e7bd0"
                    "38ceb2a6898e9f8d08b10d5779f4f79b"
                ),
            },
            "source_dependency_calls": ["open_cfw_nanopb_decode_varint32_eof"],
            "manifest_regions": {
                "entry_replacement": "nanopb_decode_varint32_source_replacement",
                "source_alignment": "apollo_nanopb_decode_varint32_source_alignment",
                "source_leaf": "apollo_nanopb_decode_varint32_source_leaf",
            },
        },
        "public pb_decode_varint32 provenance changed",
    )
    require(
        private["stock_topology"] == {
            "direct_callers": ["0x0048F5B2", "0x0048F682"],
            "direct_caller_count": 2,
            "alternate_ingress_count": 0,
            "interior_ingress_count": 0,
            "stored_pointer_ingress_count": 0,
        }
        and public["stock_topology"] == {
            "direct_callers": [
                "0x0048F654", "0x0048F788", "0x00490132",
                "0x00490362", "0x004903F6", "0x00490546",
            ],
            "direct_caller_count": 6,
            "alternate_ingress_count": 0,
            "interior_ingress_count": 0,
            "stored_pointer_ingress_count": 0,
        },
        "pb_decode_varint32 caller closure changed",
    )
    private_calls = [
        {"offset": offset, "type": "R_ARM_THM_CALL",
         "symbol": "open_cfw_nanopb_readbyte",
         "target_function": "open_cfw_nanopb_readbyte"}
        for offset in (16, 106)
    ]
    private_literals = [
        {"offset": 208, "type": "R_ARM_THM_MOVW_PREL_NC",
         "symbol": "open_cfw_nanopb_varint32_overflow_error"},
        {"offset": 212, "type": "R_ARM_THM_MOVT_PREL",
         "symbol": "open_cfw_nanopb_varint32_overflow_error"},
    ]
    public_call = [{
        "offset": 4, "type": "R_ARM_THM_CALL",
        "symbol": "open_cfw_nanopb_decode_varint32_eof",
        "target_function": "open_cfw_nanopb_decode_varint32_eof",
    }]
    require(
        private["relocations"] == private_calls + private_literals,
        "private pb_decode_varint32 dependency closure changed",
    )
    require(
        public["relocations"] == public_call,
        "public pb_decode_varint32 dependency closure changed",
    )
    require(
        all(
            "target_address" not in item
            for item in private["relocations"][:2] + public["relocations"]
        ),
        "pb_decode_varint32 calls must resolve source-to-source",
    )
    require(
        private["literal_closure"] == {
            "symbol": "open_cfw_nanopb_varint32_overflow_error",
            "contents": "varint overflow\0", "size": 16, "alignment": 1,
            "sha256": (
                "e9b62825b028cfc32f718b48de14fcbc"
                "783a9009279d2c88cf4394d54767141d"
            ),
        },
        "private pb_decode_varint32 literal closure changed",
    )
    require(set(private["toolchain_profiles"]) == {"apple-clang", "linux-clang"},
            "private pb_decode_varint32 profile set changed")
    require(set(public["toolchain_profiles"]) == {"apple-clang", "linux-clang"},
            "public pb_decode_varint32 profile set changed")
    require(
        private["toolchain_profiles"]["apple-clang"] == {
            "compiler": "Apple clang version 21.0.0 (clang-2100.3.27.1)",
            "object_size": 1628,
            "object_sha256": (
                "626893ac400caac8fa733f5740b272d21"
                "8a1e32572fad4bfa636a4bce142c166"
            ),
            "text_size": 222, "text_alignment": 4, "text_offset": 124972,
            "text_runtime_address": "0x007B2B50",
            "text_unrelocated_sha256": (
                "5296b608c55171bca9d5f4d162cf53d0"
                "e6aa5f724e1cb82499a7311f2a6cc9ff"
            ),
            "text_relocated_sha256": (
                "36bb0167f4d3407b99ed2255cc9e77dd"
                "60dc1e9070781a257bfea59abc408171"
            ),
            "closure_size": 238,
            "closure_sha256": (
                "2c49567cfe23e36c504586218719c2e5"
                "90163bec804353c8106680328d64a480"
            ),
            "leading_alignment_size": 2,
            "leading_alignment_sha256": (
                "96a296d224f285c67bee93c30f8a30915"
                "7f0daa35dc5b87e410b78630a09cfc7"
            ),
            "rodata_size": 16, "rodata_alignment": 1,
            "rodata_offset": 125194, "rodata_runtime_address": "0x007B2C2E",
            "rodata_sha256": (
                "e9b62825b028cfc32f718b48de14fcbc"
                "783a9009279d2c88cf4394d54767141d"
            ),
            "entry_patch_sha256": (
                "39cbc613617df123fca8a706d6d8664f"
                "110ed5075f6586ade5947db3d7ea6450"
            ),
        },
        "private pb_decode_varint32 Apple object/placement changed",
    )
    require(
        public["toolchain_profiles"]["apple-clang"] == {
            "compiler": "Apple clang version 21.0.0 (clang-2100.3.27.1)",
            "object_size": 1628,
            "object_sha256": (
                "626893ac400caac8fa733f5740b272d21"
                "8a1e32572fad4bfa636a4bce142c166"
            ),
            "text_size": 10, "text_alignment": 4, "text_offset": 125212,
            "text_runtime_address": "0x007B2C40",
            "text_unrelocated_sha256": (
                "e9ec8b612503f867aabf2467e3abfac4"
                "4753c5576a247a00cbc4309e2a023f93"
            ),
            "text_relocated_sha256": (
                "1f0924d25c50933e7cd5aac05d718da6"
                "d44b7a20d4af901fa833c555eca6ff1a"
            ),
            "leading_alignment_size": 2,
            "leading_alignment_sha256": (
                "96a296d224f285c67bee93c30f8a30915"
                "7f0daa35dc5b87e410b78630a09cfc7"
            ),
            "entry_patch_sha256": (
                "d9ece4c36d9d25d448b14b93d091760"
                "14efb56468d4c4570be54a232522a04aa"
            ),
        },
        "public pb_decode_varint32 Apple object/placement changed",
    )
    linux_common = {
        "compiler": "Homebrew clang version 22.1.8",
        "source_root": "/Users/kalani/Repo/SybilSightABCD/openCFW",
        "object_size": 1628,
        "object_sha256": (
            "626893ac400caac8fa733f5740b272d21"
            "8a1e32572fad4bfa636a4bce142c166"
        ),
        "leading_alignment_size": 2,
        "leading_alignment_sha256": (
            "96a296d224f285c67bee93c30f8a30915"
            "7f0daa35dc5b87e410b78630a09cfc7"
        ),
        "exidx_result": (
            "CANTUNWIND with exactly one same-function R_ARM_PREL31 relocation; "
            "authenticated 8-byte metadata deliberately discarded"
        ),
        "exidx_size": 8,
        "exidx_sha256": (
            "01acecb507abfe1a354aa8064f4af5d3"
            "f1acd019e37db3c11c97523b71c76e9d"
        ),
    }
    require(
        private["toolchain_profiles"]["linux-clang"] == {
            **linux_common,
            "text_size": 222, "text_alignment": 4, "text_offset": 126796,
            "text_runtime_address": "0x007B3270",
            "text_unrelocated_sha256": (
                "5296b608c55171bca9d5f4d162cf53d0"
                "e6aa5f724e1cb82499a7311f2a6cc9ff"
            ),
            "text_relocated_sha256": (
                "36bb0167f4d3407b99ed2255cc9e77dd"
                "60dc1e9070781a257bfea59abc408171"
            ),
            "closure_size": 238,
            "closure_sha256": (
                "2c49567cfe23e36c504586218719c2e5"
                "90163bec804353c8106680328d64a480"
            ),
            "rodata_size": 16, "rodata_alignment": 1,
            "rodata_offset": 127018, "rodata_runtime_address": "0x007B334E",
            "rodata_sha256": (
                "e9b62825b028cfc32f718b48de14fcbc"
                "783a9009279d2c88cf4394d54767141d"
            ),
            "entry_patch_sha256": (
                "1f64403d69443c2467c739594a66bd4f"
                "251ab9ad13cd55a2e6a42cb147788eba"
            ),
        },
        "private pb_decode_varint32 Linux object/placement changed",
    )
    require(
        public["toolchain_profiles"]["linux-clang"] == {
            **linux_common,
            "text_size": 10, "text_alignment": 4, "text_offset": 127036,
            "text_runtime_address": "0x007B3360",
            "text_unrelocated_sha256": (
                "e9ec8b612503f867aabf2467e3abfac4"
                "4753c5576a247a00cbc4309e2a023f93"
            ),
            "text_relocated_sha256": (
                "1f0924d25c50933e7cd5aac05d718da6"
                "d44b7a20d4af901fa833c555eca6ff1a"
            ),
            "entry_patch_sha256": (
                "7f1122db2b85b3c028dbe0c818caa26"
                "e7fee00d0e772f9ae423e369ec1d49309"
            ),
        },
        "public pb_decode_varint32 Linux object/placement changed",
    )
    require(
        selection["production_varint32_apple_aggregate"] == {
            "configuration_inventory": {"functions": 663, "patch_sites": 612, "relocated_leaves": 94},
            "emitted_report": {"functions": 659, "patch_sites": 608, "relocated_leaves": 90},
            "manifest_region_count": 957,
            "overlay": {"size": 125222, "sha256": "a21779625714a5c029652287e38939ac4290306b3a8781045501839d385a1c62"},
            "component": {"size": 3648618, "sha256": "99b1718f989695a4fe39655e8cf31ea7ef19ce97ed96b70fc1796c847bd2dead"},
            "package": {"size": 4427112, "sha256": "92d1d9a2f2d80b503b2b68d1533a1c990da5a215381a0a22b604e63b6f7fb229"},
            "build_report": {"size": 2323, "sha256": "eb0c87492532f136569cb529b2202805bd8bd84a45f76e0538b4ec1822bfe1b7"},
            "flash_plan": {"size": 738871, "sha256": "1ee4d8d5a21a2b0d79173c5b78bcdf752407ae0e26d086ea5c5df4b504c939d9", "programmed": 1029, "preserved": 2, "skipped": 5},
            "package_ownership": {"source_owned": 125994, "generated": 88625, "opaque": 4212493},
        },
        "pb_decode_varint32 Apple aggregate pins changed",
    )
    require(
        selection["production_varint32_linux_aggregate"] == {
            "compiler": "Homebrew clang version 22.1.8",
            "source_root": "/Users/kalani/Repo/SybilSightABCD/openCFW",
            "configuration_inventory": {"functions": 663, "patch_sites": 612, "relocated_leaves": 94},
            "emitted_report": {"functions": 663, "patch_sites": 612, "relocated_leaves": 94},
            "manifest_region_count": 957,
            "effective_flash_region_count": 847,
            "overlay": {"size": 127046, "sha256": "593833cbe89b7f195f97d0e9bef8b57c98c4efe4b7cf13a035b4604738c38364"},
            "component": {"size": 3650442, "sha256": "2712b0ca1feef4e75cb25c0d619814273d06d4aa82fbe85feb29dd874107c5ef"},
            "package": {"size": 4428936, "sha256": "2a3c7b0298f3dcd52dc05fc3b0cbcf0bd3e282daa9c3b93ba47e4deff442865b"},
            "component_build_report": {"size": 1540536, "sha256": "37f414b756c38766a2894dde6174efdb9ed174a8253071963d57c032b42f3592"},
            "package_build_report": {"size": 2322, "sha256": "e79568709dcd979a2a06ed986b8fcc0d717bca88772e82e67d91ba4a475d048d"},
            "flash_plan": {"size": 604887, "sha256": "de21f80249bcfda259e017512b8b25ba9e07437926cbe05d1e8e558f1177f424", "programmed": 847, "preserved": 2, "skipped": 5},
            "package_ownership": {"source_owned": 127927, "generated": 88516, "opaque": 4212493},
        },
        "pb_decode_varint32 Linux aggregate pins changed",
    )


def verify_skip_string_provenance(selection: dict[str, Any]) -> None:
    """Pin every scalar in the current dual-profile pb_skip_string record."""
    production = selection.get("production_skip_string_leaf")
    require(isinstance(production, dict), "pb_skip_string production record missing")
    require(
        canonical_sha256(production) == EXPECTED_SKIP_STRING_RECORD_SHA256,
        "pb_skip_string production provenance changed",
    )


def verify_skip_string_source_pins() -> None:
    for path, size, digest, label in (
        (
            EXPECTED_SKIP_STRING_SOURCE_PATH,
            EXPECTED_SKIP_STRING_SOURCE_SIZE,
            EXPECTED_SKIP_STRING_SOURCE_SHA256,
            "source",
        ),
        (
            EXPECTED_SKIP_STRING_HEADER_PATH,
            EXPECTED_SKIP_STRING_HEADER_SIZE,
            EXPECTED_SKIP_STRING_HEADER_SHA256,
            "header",
        ),
        (
            EXPECTED_SKIP_STRING_AUDIT_PATH,
            EXPECTED_SKIP_STRING_AUDIT_SIZE,
            EXPECTED_SKIP_STRING_AUDIT_SHA256,
            "evidence",
        ),
    ):
        data = (ROOT / path).read_bytes()
        require(len(data) == size, f"pb_skip_string {label} size changed")
        require(sha256(data) == digest, f"pb_skip_string {label} hash changed")
    upstream = (HERE / "pb_decode.c").read_bytes()
    signature = b"bool checkreturn pb_skip_string(pb_istream_t *stream)\n{"
    require(
        brace_balanced_definition(upstream, signature)
        == (EXPECTED_SKIP_STRING_UPSTREAM_START, EXPECTED_SKIP_STRING_UPSTREAM_END),
        "upstream pb_skip_string extraction span changed",
    )
    definition = upstream[
        EXPECTED_SKIP_STRING_UPSTREAM_START:EXPECTED_SKIP_STRING_UPSTREAM_END
    ]
    require(len(definition) == 299, "upstream pb_skip_string size changed")
    require(
        sha256(definition) == EXPECTED_SKIP_STRING_UPSTREAM_SHA256,
        "upstream pb_skip_string hash changed",
    )


def verify_provenance() -> dict[str, Any]:
    raw = PROVENANCE.read_bytes()
    require(len(raw) == EXPECTED_PROVENANCE_SIZE, "provenance size changed")
    require(sha256(raw) == EXPECTED_PROVENANCE_SHA256, "provenance bytes changed")
    value = json.loads(raw)
    require(
        set(value)
        == {"schema_version", "component", "license", "upstream", "selection", "g2_boundary", "files"},
        "provenance schema changed",
    )
    require(value["schema_version"] == 1, "schema version changed")
    require(value["component"] == "nanopb", "component changed")
    require(value["license"] == "Zlib", "license changed")

    upstream = value["upstream"]
    require(upstream["repository"] == "https://github.com/nanopb/nanopb.git", "repository changed")
    require(upstream["selected_ref"] == "refs/tags/nanopb-0.4.9", "selected ref changed")
    require(upstream["selected_tag"] == "nanopb-0.4.9", "selected tag changed")
    require(upstream["tag_type"] == "annotated", "tag type changed")
    require(upstream["tag_object"] == EXPECTED_TAG_OBJECT, "tag object changed")
    require(upstream["tag_target"] == EXPECTED_COMMIT, "tag target changed")
    require(upstream["selected_commit"] == EXPECTED_COMMIT, "commit changed")
    require(upstream["selected_tree"] == EXPECTED_TREE, "tree changed")
    require(upstream["parent_commit"] == EXPECTED_PARENT, "parent changed")
    require(upstream["tag_signature"]["present"] is False, "unsigned tag claim changed")
    require(upstream["tag_signature"]["signer_trust_verified"] is False, "unsupported tag trust claim")
    require(upstream["commit_signature"]["present"] is False, "unsigned commit claim changed")
    require(upstream["commit_signature"]["signer_trust_verified"] is False, "unsupported commit trust claim")
    require(upstream["tree_object_count"] == 1, "tree object count changed")
    require(upstream["root_tree_entry_count"] == EXPECTED_ROOT_ENTRY_COUNT, "root entry count changed")
    require(upstream["declared_library_version"] == "0.4.9", "declared version changed")

    selection = value["selection"]
    require(selection["compatibility_choice"] == "nanopb-0.4.9", "compatibility choice changed")
    require(selection["exact_g2_point_release_proven"] is False, "metadata claims an exact G2 point release")
    require(
        selection["g2_compatible_pristine_release_range"] == ["0.4.7", "0.4.8", "0.4.9"],
        "G2-compatible release range changed",
    )
    require(selection["selected_file_count"] == 8, "selected file count changed")
    require(selection["source_records_sha256"] == EXPECTED_RECORDS_SHA256, "stored source-record digest changed")
    require(
        selection["integration_status"]
        == (
            "authenticated and verified offline; thirteen bounded altered "
            "production functions registered: pb_istream_from_buffer, "
            "pb_decode_varint, pb_decode_svarint, private "
            "pb_decode_varint32_eof, pb_decode_varint32, pb_skip_varint, "
            "pb_skip_string, "
            "pb_close_string_substream, "
            "pb_decode_fixed32, pb_decode_fixed64, pb_read, private "
            "buf_read, and private pb_readbyte"
        ),
        "snapshot production boundary changed",
    )
    verify_istream_provenance(selection)
    verify_svarint_provenance(selection)
    verify_varint32_provenance(selection)
    verify_skip_string_provenance(selection)
    production = selection["production_leaf"]
    require(
        production
        == {
            "upstream_function": "pb_decode_varint",
            "local_source": (
                "components/shared/nanopb/"
                "runtime_nanopb_decode_varint.c"
            ),
            "local_source_size": 2224,
            "local_source_sha256": (
                "b1de68b98ee043bd07d1e10706166a13b"
                "13693534e382705bbad6866411fbe05"
            ),
            "stock_span": "[0x0048F5B8,0x0048F628)",
            "stock_sha256": (
                "f93d678981f92603982c9afc6c6f9976"
                "ca14d1a7a7e0bfc949d3ff73f2791ff2"
            ),
            "source_backed_readbyte_entry": "0x0048F454",
            "configuration": "g2-config/pb_g2_options.h",
            "qualification": (
                "Altered local source selected against the authenticated "
                "0.4.9 compatibility baseline; not a claim that the vendor "
                "used nanopb 0.4.9. Its read-byte call retains stable entry "
                "0x0048F454, whose complete body redirects to the separately "
                "pinned production_private_read_pair. The broader pristine pb_common, "
                "pb_decode, and pb_encode translation units remain "
                "unregistered."
            ),
        },
        "bounded production leaf contract changed",
    )
    skip_production = selection["production_skip_varint_leaf"]
    require(
        skip_production
        == {
            "upstream_function": "pb_skip_varint",
            "upstream_source": "pb_decode.c",
            "upstream_commit": EXPECTED_COMMIT,
            "upstream_definition_span": "pb_decode.c bytes [8160,8360)",
            "upstream_definition_size": 200,
            "upstream_definition_sha256": EXPECTED_SKIP_UPSTREAM_SHA256,
            "local_source": EXPECTED_SKIP_SOURCE_PATH,
            "local_source_size": EXPECTED_SKIP_SOURCE_SIZE,
            "local_source_sha256": EXPECTED_SKIP_SOURCE_SHA256,
            "local_header": EXPECTED_SKIP_HEADER_PATH,
            "local_header_size": EXPECTED_SKIP_HEADER_SIZE,
            "local_header_sha256": EXPECTED_SKIP_HEADER_SHA256,
            "stock_span": "[0x0048F628,0x0048F64C)",
            "stock_size": 36,
            "stock_sha256": (
                "fae83b1a62a07bb9c7a3d3f6c398bc13"
                "433ebe1cd75d01945f83f30e6fcc9c5d"
            ),
            "stock_read_seam": "0x0048F3BE",
            "configuration": "g2-config/pb_g2_options.h",
            "qualification": (
                "Altered local source selected against authenticated nanopb "
                "0.4.9 as a compatibility baseline within the authenticated "
                "0.4.7-0.4.9 range; not proof of the vendor nanopb revision "
                "or checkout. The broader pristine pb_common, pb_decode, and "
                "pb_encode translation units remain unregistered."
            ),
        },
        "bounded pb_skip_varint production leaf contract changed",
    )
    close_production = selection["production_close_string_substream_leaf"]
    require(
        close_production
        == {
            "upstream_function": "pb_close_string_substream",
            "upstream_source": "pb_decode.c",
            "upstream_commit": EXPECTED_COMMIT,
            "upstream_definition_span": "pb_decode.c bytes [11223,11568)",
            "upstream_definition_size": 345,
            "upstream_definition_sha256": EXPECTED_CLOSE_UPSTREAM_SHA256,
            "local_source": EXPECTED_CLOSE_SOURCE_PATH,
            "local_source_size": EXPECTED_CLOSE_SOURCE_SIZE,
            "local_source_sha256": EXPECTED_CLOSE_SOURCE_SHA256,
            "local_header": EXPECTED_CLOSE_HEADER_PATH,
            "local_header_size": EXPECTED_CLOSE_HEADER_SIZE,
            "local_header_sha256": EXPECTED_CLOSE_HEADER_SHA256,
            "stock_span": "[0x0048F7CA,0x0048F7F4)",
            "stock_size": 42,
            "stock_sha256": (
                "439bbeecb6a0b8266dc3dcd913e987933"
                "52b6b346a7a58cdd44322c734621818"
            ),
            "stock_read_seam": "0x0048F3BE",
            "configuration": "g2-config/pb_g2_options.h",
            "qualification": (
                "Altered local source selected against authenticated nanopb "
                "0.4.9 as a compatibility baseline within the authenticated "
                "0.4.7-0.4.9 range; not proof of the vendor nanopb revision "
                "or checkout. The broader pristine pb_common, pb_decode, and "
                "pb_encode translation units remain unregistered."
            ),
        },
        "bounded pb_close_string_substream production leaf contract changed",
    )
    fixed32_production = selection["production_decode_fixed32_leaf"]
    require(
        fixed32_production
        == {
            "upstream_function": "pb_decode_fixed32",
            "upstream_source": "pb_decode.c",
            "upstream_commit": EXPECTED_COMMIT,
            "upstream_definition_span": "pb_decode.c bytes [43210,43828)",
            "upstream_definition_size": 618,
            "upstream_definition_sha256": EXPECTED_FIXED32_UPSTREAM_SHA256,
            "local_source": EXPECTED_FIXED32_SOURCE_PATH,
            "local_source_size": EXPECTED_FIXED32_SOURCE_SIZE,
            "local_source_sha256": EXPECTED_FIXED32_SOURCE_SHA256,
            "local_header": EXPECTED_FIXED32_HEADER_PATH,
            "local_header_size": EXPECTED_FIXED32_HEADER_SIZE,
            "local_header_sha256": EXPECTED_FIXED32_HEADER_SHA256,
            "stock_span": "[0x00490190,0x004901AC)",
            "stock_size": 28,
            "stock_sha256": (
                "1ee27599a8ac5b8d2a0cbaac59986fb4"
                "9be7b24c348a960a216b8cbbecce5bf3"
            ),
            "stock_read_seam": "0x0048F3BE",
            "configuration": "g2-config/pb_g2_options.h",
            "qualification": (
                "Altered local source selected against authenticated nanopb "
                "0.4.9 as a compatibility baseline within the authenticated "
                "0.4.7-0.4.9 range; not proof of the vendor nanopb revision "
                "or checkout. The broader pristine pb_common, pb_decode, and "
                "pb_encode translation units remain unregistered."
            ),
        },
        "bounded pb_decode_fixed32 production leaf contract changed",
    )
    fixed64_production = selection["production_decode_fixed64_leaf"]
    require(
        fixed64_production
        == {
            "upstream_function": "pb_decode_fixed64",
            "upstream_source": "pb_decode.c",
            "upstream_commit": EXPECTED_COMMIT,
            "upstream_definition_span": "pb_decode.c bytes [43854,44688)",
            "upstream_definition_size": 834,
            "upstream_definition_sha256": EXPECTED_FIXED64_UPSTREAM_SHA256,
            "local_source": EXPECTED_FIXED64_SOURCE_PATH,
            "local_source_size": EXPECTED_FIXED64_SOURCE_SIZE,
            "local_source_sha256": EXPECTED_FIXED64_SOURCE_SHA256,
            "local_header": EXPECTED_FIXED64_HEADER_PATH,
            "local_header_size": EXPECTED_FIXED64_HEADER_SIZE,
            "local_header_sha256": EXPECTED_FIXED64_HEADER_SHA256,
            "stock_span": "[0x004901AC,0x004901CC)",
            "stock_size": 32,
            "stock_sha256": (
                "96228dfbdfe30665d79281ba0fd5ba3b3"
                "af38701396671cd20b77623ffd82d54"
            ),
            "stock_read_seam": "0x0048F3BE",
            "configuration": "g2-config/pb_g2_options.h",
            "qualification": (
                "Altered local source selected against authenticated nanopb "
                "0.4.9 as a compatibility baseline within the authenticated "
                "0.4.7-0.4.9 range; not proof of the vendor nanopb revision "
                "or checkout. Its pb_read ABI entry now redirects to the "
                "separately pinned production_read_leaf, while that provider "
                "retains three authenticated stock identity/data seams. The "
                "broader pristine pb_common, "
                "pb_decode, and pb_encode translation units remain "
                "unregistered."
            ),
        },
        "bounded pb_decode_fixed64 production leaf contract changed",
    )
    read_production = selection["production_read_leaf"]
    require(
        set(read_production)
        == {
            "upstream_function",
            "upstream_source",
            "upstream_commit",
            "authenticated_release_definitions",
            "local_source",
            "local_source_size",
            "local_source_sha256",
            "local_header",
            "local_header_size",
            "local_header_sha256",
            "stock_span",
            "stock_size",
            "stock_sha256",
            "stock_topology",
            "retained_stock_seams",
            "relocations",
            "toolchain_profiles",
            "bootloader_homolog",
            "configuration",
            "qualification",
        },
        "bounded pb_read provenance schema changed",
    )
    require(
        {
            key: read_production[key]
            for key in (
                "upstream_function",
                "upstream_source",
                "upstream_commit",
                "local_source",
                "local_source_size",
                "local_source_sha256",
                "local_header",
                "local_header_size",
                "local_header_sha256",
                "stock_span",
                "stock_size",
                "stock_sha256",
                "configuration",
                "qualification",
            )
        }
        == {
            "upstream_function": "pb_read",
            "upstream_source": "pb_decode.c",
            "upstream_commit": EXPECTED_COMMIT,
            "local_source": EXPECTED_READ_SOURCE_PATH,
            "local_source_size": EXPECTED_READ_SOURCE_SIZE,
            "local_source_sha256": EXPECTED_READ_SOURCE_SHA256,
            "local_header": EXPECTED_READ_HEADER_PATH,
            "local_header_size": EXPECTED_READ_HEADER_SIZE,
            "local_header_sha256": EXPECTED_READ_HEADER_SHA256,
            "stock_span": "[0x0048F3BE,0x0048F454)",
            "stock_size": 150,
            "stock_sha256": (
                "69aecb900c749fd98bd2d05e2229e9a3"
                "d6829bd36f3e393f624e3579a9b4af7f"
            ),
            "configuration": "g2-config/pb_g2_options.h",
            "qualification": (
                "Altered local source selected against authenticated nanopb "
                "0.4.9 as a compatibility baseline within the authenticated "
                "0.4.7-0.4.9 range; not proof of the vendor nanopb revision "
                "or checkout. The production leaf preserves canonical buf_read "
                "function-pointer identity 0x0048F3A5 through the source-backed "
                "stock entry and retains three explicit retained seams: that identity "
                "and two stock error strings. The broader pristine "
                "pb_common, pb_decode, and pb_encode translation units remain "
                "unregistered."
            ),
        },
        "bounded pb_read production leaf contract changed",
    )
    require(
        read_production["authenticated_release_definitions"]
        == [
            {
                "release": "0.4.7",
                "commit": "b97aa657a706d3ba4a9a6ccca7043c9d6fe41cba",
                "span": "pb_decode.c bytes [3659,4473)",
                "size": 814,
                "sha256": EXPECTED_READ_UPSTREAM_SHA256,
            },
            {
                "release": "0.4.8",
                "commit": "6cfe48d6f1593f8fa5c0f90437f5e6522587745e",
                "span": "pb_decode.c bytes [3659,4473)",
                "size": 814,
                "sha256": EXPECTED_READ_UPSTREAM_SHA256,
            },
            {
                "release": "0.4.9",
                "commit": EXPECTED_COMMIT,
                "span": "pb_decode.c bytes [3745,4559)",
                "size": 814,
                "sha256": EXPECTED_READ_UPSTREAM_SHA256,
            },
        ],
        "authenticated pb_read release definitions changed",
    )
    require(
        read_production["stock_topology"]
        == {
            "internal_recursive_calls": ["0x0048F3EA", "0x0048F3FC"],
            "external_direct_callers": [
                "0x0048F632",
                "0x0048F666",
                "0x0048F6C0",
                "0x0048F6D0",
                "0x0048F71A",
                "0x0048F754",
                "0x0048F764",
                "0x0048F7DC",
                "0x00490198",
                "0x004901B4",
                "0x004903E4",
                "0x00490478",
                "0x004905A2",
            ],
            "external_direct_caller_count": 13,
            "interior_ingress_count": 0,
            "stored_pointer_ingress_count": 0,
        },
        "pb_read stock topology changed",
    )
    require(
        read_production["retained_stock_seams"]
        == [
            {
                "symbol": "open_cfw_nanopb_end_of_stream_error",
                "kind": "NUL-terminated data",
                "target_address": "0x00787C70",
                "size": 14,
                "sha256": (
                    "e167d4f2ec31a2197c7bc32affd9865a"
                    "c8609d7dae984d0916e01f044fcc67b4"
                ),
            },
            {
                "symbol": "open_cfw_nanopb_stock_buffer_read_identity",
                "kind": "Thumb function-pointer identity",
                "stock_span": "[0x0048F3A4,0x0048F3BE)",
                "stock_size": 26,
                "stock_sha256": (
                    "9d6c6690294b82bbafba82ec0f63a6bb"
                    "5b78e4146543db3a30fac92469ace723"
                ),
                "target_address": "0x0048F3A5",
            },
            {
                "symbol": "open_cfw_nanopb_io_error",
                "kind": "NUL-terminated data",
                "target_address": "0x0078B690",
                "size": 9,
                "sha256": (
                    "3faaf40b4ee3e3b23823ed9851dc77bf"
                    "6fc2d7c7c330240eeaed08bd9d084ec1"
                ),
            },
        ],
        "pb_read retained stock seams changed",
    )
    require(
        read_production["relocations"]
        == [
            {
                "offset": offset,
                "type": kind,
                "symbol": symbol,
                "target_address": address,
            }
            for offset, kind, symbol, address in (
                (28, "R_ARM_THM_MOVW_ABS_NC", "open_cfw_nanopb_end_of_stream_error", "0x00787C70"),
                (32, "R_ARM_THM_MOVT_ABS", "open_cfw_nanopb_end_of_stream_error", "0x00787C70"),
                (66, "R_ARM_THM_MOVW_ABS_NC", "open_cfw_nanopb_stock_buffer_read_identity", "0x0048F3A5"),
                (70, "R_ARM_THM_MOVT_ABS", "open_cfw_nanopb_stock_buffer_read_identity", "0x0048F3A5"),
                (134, "R_ARM_THM_MOVW_ABS_NC", "open_cfw_nanopb_io_error", "0x0078B690"),
                (138, "R_ARM_THM_MOVT_ABS", "open_cfw_nanopb_io_error", "0x0078B690"),
            )
        ],
        "pb_read retained-seam relocation contract changed",
    )
    require(
        read_production["toolchain_profiles"]
        == {
            "apple-clang": {
                "size": 158,
                "alignment": 4,
                "offset": 124640,
                "runtime_address": "0x007B2A04",
                "unrelocated_sha256": (
                    "06def086733fd9801b712161943b0da64"
                    "e3b2bdf82e6f5962ee9207c738c00b1"
                ),
                "relocated_sha256": (
                    "8b3de44a2cf7ca2e07715c913db0fa45"
                    "4ef65cbc453366190b12736e455aa7a8"
                ),
                "entry_patch_sha256": (
                    "c2c44419ee24c41c8d0e8bc7f04689b"
                    "b7f1c18b1f7ec3d7304e04c37579938a1"
                ),
            },
            "linux-clang": {
                "size": 158,
                "alignment": 4,
                "offset": 126464,
                "runtime_address": "0x007B3124",
                "unrelocated_sha256": (
                    "06def086733fd9801b712161943b0da64"
                    "e3b2bdf82e6f5962ee9207c738c00b1"
                ),
                "relocated_sha256": (
                    "8b3de44a2cf7ca2e07715c913db0fa45"
                    "4ef65cbc453366190b12736e455aa7a8"
                ),
                "entry_patch_sha256": (
                    "4dc433588344c12d1a0abfab8c5f1673"
                    "c24f6702d8f285f67fb0fd8b8e6e3eab"
                ),
            },
        },
        "pb_read profile contracts changed",
    )
    require(
        read_production["bootloader_homolog"]
        == {
            "found": False,
            "official_image_size": 148599,
            "official_image_sha256": (
                "f89a4c4657537cec6bfc572bdb831886"
                "6309b90a5d180c4307680d39824167b5"
            ),
            "qualification": (
                "No full stock pb_read provider body, private buf_read body, "
                "or nanopb runtime error strings occur in the authenticated "
                "bootloader."
            ),
        },
        "pb_read bootloader-homolog boundary changed",
    )
    private_pair = selection["production_private_read_pair"]
    require(
        set(private_pair)
        == {
            "upstream_source", "upstream_commit",
            "authenticated_release_range", "upstream_definitions",
            "local_sources", "local_header", "local_header_size",
            "local_header_sha256", "stock_providers",
            "retained_stock_seams", "toolchain_profiles",
            "constructor_identity", "bootloader_homolog", "configuration",
            "evidence", "evidence_size", "evidence_sha256", "qualification",
        },
        "private read-pair provenance schema changed",
    )
    require(
        private_pair["local_sources"]
        == [
            {
                "function": "open_cfw_nanopb_buf_read",
                "path": EXPECTED_BUF_SOURCE_PATH,
                "size": EXPECTED_BUF_SOURCE_SIZE,
                "sha256": EXPECTED_BUF_SOURCE_SHA256,
            },
            {
                "function": "open_cfw_nanopb_readbyte",
                "path": EXPECTED_READBYTE_SOURCE_PATH,
                "size": EXPECTED_READBYTE_SOURCE_SIZE,
                "sha256": EXPECTED_READBYTE_SOURCE_SHA256,
            },
        ],
        "private read-pair local sources changed",
    )
    require(
        (
            private_pair["local_header"],
            private_pair["local_header_size"],
            private_pair["local_header_sha256"],
        )
        == (
            EXPECTED_PRIVATE_HEADER_PATH,
            EXPECTED_PRIVATE_HEADER_SIZE,
            EXPECTED_PRIVATE_HEADER_SHA256,
        ),
        "private read-pair header changed",
    )
    require(
        (
            private_pair["evidence"],
            private_pair["evidence_size"],
            private_pair["evidence_sha256"],
        )
        == (
            EXPECTED_PRIVATE_AUDIT_PATH,
            EXPECTED_PRIVATE_AUDIT_SIZE,
            EXPECTED_PRIVATE_AUDIT_SHA256,
        ),
        "private read-pair evidence changed",
    )
    require(
        private_pair["toolchain_profiles"]["apple-clang"]
        == {
            "buf_read": {
                "offset": 124800,
                "runtime_address": "0x007B2AA4",
                "size": 30,
                "unrelocated_sha256": (
                    "db26e5bd51f3d313907af94bfe545cc99"
                    "62b867ed18285f2025c401e8613700a"
                ),
                "relocated_sha256": (
                    "f312e087cf1fbecf19bd5fa0052d3a63"
                    "ca91287c811de169aaf2a09322e0115e"
                ),
                "entry_patch_sha256": (
                    "7b95b1a632ce6362c74c2a3f3ae2e9e"
                    "f15f5abb6800d1dd8ca1dd4586b4f73ac"
                ),
            },
            "pb_readbyte": {
                "offset": 124832,
                "runtime_address": "0x007B2AC4",
                "size": 64,
                "unrelocated_sha256": (
                    "eda66d0ae6274a2078b6eceaefc0e773"
                    "169d5e15b26bce650a8d48b818e4f2b8"
                ),
                "relocated_sha256": (
                    "f3395a19a7406016e6b1f1daf14969de"
                    "e91ccde4e9a98ba4eeaba0016e131871"
                ),
                "entry_patch_sha256": (
                    "ed8460907148368a780a57a2abab8bb4"
                    "8cc80a78b980c38b0097e1b81ce1967e"
                ),
            },
        },
        "private read-pair Apple profile changed",
    )
    require(
        private_pair["toolchain_profiles"]["linux-clang"]
        == {
            "buf_read": {
                "offset": 126624,
                "runtime_address": "0x007B31C4",
                "size": 30,
                "unrelocated_sha256": (
                    "db26e5bd51f3d313907af94bfe545cc99"
                    "62b867ed18285f2025c401e8613700a"
                ),
                "relocated_sha256": (
                    "a6b4d3a4e969f078683f1cde3a4043b7"
                    "0d8495d577f550ae35c6c2789ff470de"
                ),
                "entry_patch_sha256": (
                    "db7d0da006d031b33b6858a4b829d684"
                    "03c9039f66d2ac4db576b00bdef94bec"
                ),
            },
            "pb_readbyte": {
                "offset": 126656,
                "runtime_address": "0x007B31E4",
                "size": 64,
                "unrelocated_sha256": (
                    "eda66d0ae6274a2078b6eceaefc0e773"
                    "169d5e15b26bce650a8d48b818e4f2b8"
                ),
                "relocated_sha256": (
                    "f3395a19a7406016e6b1f1daf14969de"
                    "e91ccde4e9a98ba4eeaba0016e131871"
                ),
                "entry_patch_sha256": (
                    "b571a49431ddbdd7c71059acf67da1227"
                    "af1eecba58b09fafea45177eda87fd0"
                ),
            },
        },
        "private read-pair Linux profile changed",
    )
    require(
        private_pair["constructor_identity"]["stored_thumb_pointer"]
        == "0x0048F3A5"
        and private_pair["constructor_identity"]["constructor_replaced"] is True,
        "private read-pair constructor identity changed",
    )
    boundary = value["g2_boundary"]
    require(boundary["first_party_glue"]["included"] is False, "first-party message glue must remain excluded")
    return value


def verify_tag_and_commit(provenance: dict[str, Any]) -> None:
    upstream = provenance["upstream"]
    tag = (HERE / upstream["tag_object_payload_path"]).read_bytes()
    require(len(tag) == EXPECTED_TAG_SIZE, "tag payload size changed")
    require(sha256(tag) == EXPECTED_TAG_SHA256, "tag payload changed")
    require(git_object_sha1("tag", tag) == EXPECTED_TAG_OBJECT, "tag object ID changed")
    require(
        tag
        == (
            f"object {EXPECTED_COMMIT}\n"
            "type commit\n"
            "tag nanopb-0.4.9\n"
            "tagger Petteri Aimonen <jpa@git.mail.kapsi.fi> 1726743400 +0300\n"
            "\n"
            "ver0.4.9\n"
        ).encode("ascii"),
        "annotated tag semantics changed",
    )

    commit = (HERE / upstream["commit_object_payload_path"]).read_bytes()
    require(len(commit) == EXPECTED_COMMIT_SIZE, "commit payload size changed")
    require(sha256(commit) == EXPECTED_COMMIT_SHA256, "commit payload changed")
    require(git_object_sha1("commit", commit) == EXPECTED_COMMIT, "commit object ID changed")
    require(
        commit
        == (
            f"tree {EXPECTED_TREE}\n"
            f"parent {EXPECTED_PARENT}\n"
            "author Petteri Aimonen <jpa@git.mail.kapsi.fi> 1726743379 +0300\n"
            "committer Petteri Aimonen <jpa@git.mail.kapsi.fi> 1726743379 +0300\n"
            "\n"
            "Publishing nanopb-0.4.9\n"
        ).encode("ascii"),
        "commit semantics changed",
    )


def verify_tree_closure(
    provenance: dict[str, Any], closure: dict[str, Any] | None = None
) -> None:
    """Reconstruct the root tree and prove every selected blob membership."""
    if closure is None:
        upstream = provenance["upstream"]
        raw = (HERE / upstream["tree_closure_path"]).read_bytes()
        require(len(raw) == EXPECTED_TREE_CLOSURE_SIZE, "tree closure size changed")
        require(sha256(raw) == EXPECTED_TREE_CLOSURE_SHA256, "tree closure bytes changed")
        closure = json.loads(raw)

    require(set(closure) == {"schema_version", "root_tree", "trees"}, "tree closure schema changed")
    require(closure["schema_version"] == 1, "tree closure schema version changed")
    require(closure["root_tree"] == EXPECTED_TREE, "tree closure root changed")
    require(len(closure["trees"]) == 1, "only the selected root tree is expected")
    tree = closure["trees"][0]
    require(set(tree) == {"oid", "entries"}, "tree record schema changed")
    require(tree["oid"] == EXPECTED_TREE, "root tree object changed")
    require(len(tree["entries"]) == EXPECTED_ROOT_ENTRY_COUNT, "root tree entry count changed")

    payload = bytearray()
    names: set[str] = set()
    entries: dict[str, dict[str, str]] = {}
    for entry in tree["entries"]:
        require(set(entry) == {"mode", "type", "oid", "name"}, "tree entry schema changed")
        mode, kind, oid, name = (entry[key] for key in ("mode", "type", "oid", "name"))
        require((mode, kind) in {("040000", "tree"), ("100644", "blob")}, "unsupported tree entry")
        require(isinstance(oid, str) and len(oid) == 40 and all(c in "0123456789abcdef" for c in oid), "invalid child object ID")
        require(isinstance(name, str) and name and "/" not in name and "\0" not in name, "invalid tree entry name")
        require(name not in names, f"duplicate tree entry: {name}")
        names.add(name)
        entries[name] = entry
        payload.extend(f"{'40000' if kind == 'tree' else mode} {name}".encode("utf-8"))
        payload.append(0)
        payload.extend(bytes.fromhex(oid))
    require(git_object_sha1("tree", bytes(payload)) == EXPECTED_TREE, "root tree object ID mismatch")

    for source in provenance["files"]:
        path = source["upstream_path"]
        require("/" not in path, f"unexpected non-root selected path: {path}")
        require(path in entries, f"selected path absent from root tree: {path}")
        entry = entries[path]
        require(entry["type"] == "blob", f"selected path is not a blob: {path}")
        require(entry["mode"] == source["git_mode"], f"tree mode mismatch: {path}")
        require(entry["oid"] == source["git_blob_sha1"], f"tree blob mismatch: {path}")


def verify_source_files(provenance: dict[str, Any]) -> None:
    records = provenance["files"]
    require([item["local_path"] for item in records] == EXPECTED_SOURCE_PATHS, "source order/path set changed")
    require(canonical_sha256(records) == EXPECTED_RECORDS_SHA256, "source records changed")
    for item in records:
        require(
            set(item) == {"local_path", "upstream_path", "git_mode", "size", "sha256", "git_blob_sha1"},
            f"source record schema changed: {item['local_path']}",
        )
        require(item["local_path"] == item["upstream_path"], f"path remapping changed: {item['local_path']}")
        require(item["git_mode"] == "100644", f"source Git mode changed: {item['local_path']}")
        path = HERE / item["local_path"]
        data = path.read_bytes()
        require(path.is_file(), f"source file missing: {item['local_path']}")
        require(not (path.stat().st_mode & stat.S_IXUSR), f"source became executable: {item['local_path']}")
        require(len(data) == item["size"], f"size changed: {item['local_path']}")
        require(sha256(data) == item["sha256"], f"SHA-256 changed: {item['local_path']}")
        require(git_object_sha1("blob", data) == item["git_blob_sha1"], f"Git blob changed: {item['local_path']}")

    actual = {
        path.relative_to(HERE).as_posix()
        for path in HERE.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }
    require(actual == set(EXPECTED_SOURCE_PATHS) | METADATA_PATHS, "snapshot file set changed")
    require(
        (HERE / ".gitattributes").read_bytes() == b"* -text whitespace=-trailing-space\n",
        "snapshot byte/whitespace attributes changed",
    )


def verify_runtime_and_config_markers(provenance: dict[str, Any]) -> None:
    header = (HERE / "pb.h").read_text(encoding="utf-8")
    require('#define NANOPB_VERSION "nanopb-0.4.9"' in header, "version macro changed")
    require("#define PB_MAX_REQUIRED_FIELDS 64" in header, "upstream required-field default changed")
    common_source = (HERE / "pb_common.c").read_text(encoding="utf-8")
    common_header = (HERE / "pb_common.h").read_text(encoding="utf-8")
    require('#include "pb_common.h"' in common_source, "common source dependency changed")
    require('#include "pb.h"' in common_header, "common header dependency changed")
    require('#include "pb_decode.h"' in (HERE / "pb_decode.c").read_text(encoding="utf-8"), "decode dependency changed")
    require('#include "pb_encode.h"' in (HERE / "pb_encode.c").read_text(encoding="utf-8"), "encode dependency changed")
    license_text = (HERE / "LICENSE.txt").read_text(encoding="utf-8")
    require("This software is provided 'as-is'" in license_text, "Zlib license text changed")
    require("Altered source versions must be plainly marked" in license_text, "Zlib license terms changed")

    boundary = provenance["g2_boundary"]
    config = (HERE / boundary["recovered_config_header"]).read_bytes()
    require(len(config) == EXPECTED_CONFIG_SIZE, "G2 option header size changed")
    require(sha256(config) == EXPECTED_CONFIG_SHA256, "G2 option header changed")
    text = config.decode("ascii")
    require(text.count("#define PB_MAX_REQUIRED_FIELDS 64") == 1, "required-field option changed")
    for option in (
        "PB_ENABLE_MALLOC",
        "PB_FIELD_32BIT",
        "PB_WITHOUT_64BIT",
        "PB_CONVERT_DOUBLE_FLOAT",
        "PB_VALIDATE_UTF8",
        "PB_NO_PACKED_STRUCTS",
        "PB_ENCODE_ARRAYS_UNPACKED",
        "PB_BUFFER_ONLY",
        "PB_NO_ERRMSG",
    ):
        require(f"#if defined({option})" in text, f"missing fail-closed option check: {option}")
        require(f"#define {option}" not in text, f"forbidden option became enabled: {option}")
    config_record = boundary["configuration"]
    require(config_record["pb_size_t_bits"] == 16, "pb_size_t ABI changed")
    require(config_record["native_double_bits"] == 64, "native double ABI changed")
    require(config_record["PB_MAX_REQUIRED_FIELDS"] == 64, "required-field limit changed")
    require(config_record["callback_streams"] is True, "callback streams disabled")


def verify_optional_official_image(provenance: dict[str, Any]) -> bool:
    image_path = ROOT / provenance["g2_boundary"]["official_image"]
    if not image_path.is_file():
        return False
    image = image_path.read_bytes()
    require(len(image) == EXPECTED_IMAGE_SIZE, "official image size changed")
    require(sha256(image) == EXPECTED_IMAGE_SHA256, "official image SHA-256 changed")
    first = RUNTIME_START - LOAD_BASE
    last = RUNTIME_END - LOAD_BASE
    require(sha256(image[first:last]) == EXPECTED_RUNTIME_SHA256, "nanopb runtime span changed")
    return True


def verify_skip_varint_source_pins() -> None:
    """Authenticate the bounded altered leaf, header, and upstream function."""
    source_path = ROOT / EXPECTED_SKIP_SOURCE_PATH
    require(source_path.is_file(), "bounded pb_skip_varint source is missing")
    source = source_path.read_bytes()
    require(len(source) == EXPECTED_SKIP_SOURCE_SIZE, "bounded pb_skip_varint source size changed")
    require(sha256(source) == EXPECTED_SKIP_SOURCE_SHA256, "bounded pb_skip_varint source bytes changed")

    header_path = ROOT / EXPECTED_SKIP_HEADER_PATH
    require(header_path.is_file(), "bounded pb_skip_varint header is missing")
    header = header_path.read_bytes()
    require(len(header) == EXPECTED_SKIP_HEADER_SIZE, "bounded pb_skip_varint header size changed")
    require(sha256(header) == EXPECTED_SKIP_HEADER_SHA256, "bounded pb_skip_varint header bytes changed")

    upstream = (HERE / "pb_decode.c").read_bytes()
    definition = upstream[EXPECTED_SKIP_UPSTREAM_START:EXPECTED_SKIP_UPSTREAM_END]
    require(len(definition) == 200, "upstream pb_skip_varint definition size changed")
    require(
        sha256(definition) == EXPECTED_SKIP_UPSTREAM_SHA256,
        "upstream pb_skip_varint definition bytes changed",
    )
    require(
        definition.startswith(b"bool checkreturn pb_skip_varint(pb_istream_t *stream)\n{"),
        "upstream pb_skip_varint definition start changed",
    )
    require(
        definition.endswith(b"    return true;\n}"),
        "upstream pb_skip_varint definition end changed",
    )


def verify_close_string_substream_source_pins() -> None:
    """Authenticate the bounded close leaf, header, and upstream function."""
    source_path = ROOT / EXPECTED_CLOSE_SOURCE_PATH
    require(source_path.is_file(), "bounded pb_close_string_substream source is missing")
    source = source_path.read_bytes()
    require(
        len(source) == EXPECTED_CLOSE_SOURCE_SIZE,
        "bounded pb_close_string_substream source size changed",
    )
    require(
        sha256(source) == EXPECTED_CLOSE_SOURCE_SHA256,
        "bounded pb_close_string_substream source bytes changed",
    )

    header_path = ROOT / EXPECTED_CLOSE_HEADER_PATH
    require(header_path.is_file(), "bounded pb_close_string_substream header is missing")
    header = header_path.read_bytes()
    require(
        len(header) == EXPECTED_CLOSE_HEADER_SIZE,
        "bounded pb_close_string_substream header size changed",
    )
    require(
        sha256(header) == EXPECTED_CLOSE_HEADER_SHA256,
        "bounded pb_close_string_substream header bytes changed",
    )

    upstream = (HERE / "pb_decode.c").read_bytes()
    definition = upstream[EXPECTED_CLOSE_UPSTREAM_START:EXPECTED_CLOSE_UPSTREAM_END]
    require(len(definition) == 345, "upstream pb_close_string_substream definition size changed")
    require(
        sha256(definition) == EXPECTED_CLOSE_UPSTREAM_SHA256,
        "upstream pb_close_string_substream definition bytes changed",
    )
    require(
        definition.startswith(
            b"bool checkreturn pb_close_string_substream(pb_istream_t *stream, "
            b"pb_istream_t *substream)\n{"
        ),
        "upstream pb_close_string_substream definition start changed",
    )
    require(
        definition.endswith(b"    return true;\n}"),
        "upstream pb_close_string_substream definition end changed",
    )


def verify_decode_fixed32_source_pins() -> None:
    """Authenticate the bounded fixed32 leaf, header, and upstream function."""
    source_path = ROOT / EXPECTED_FIXED32_SOURCE_PATH
    require(source_path.is_file(), "bounded pb_decode_fixed32 source is missing")
    source = source_path.read_bytes()
    require(
        len(source) == EXPECTED_FIXED32_SOURCE_SIZE,
        "bounded pb_decode_fixed32 source size changed",
    )
    require(
        sha256(source) == EXPECTED_FIXED32_SOURCE_SHA256,
        "bounded pb_decode_fixed32 source bytes changed",
    )

    header_path = ROOT / EXPECTED_FIXED32_HEADER_PATH
    require(header_path.is_file(), "bounded pb_decode_fixed32 header is missing")
    header = header_path.read_bytes()
    require(
        len(header) == EXPECTED_FIXED32_HEADER_SIZE,
        "bounded pb_decode_fixed32 header size changed",
    )
    require(
        sha256(header) == EXPECTED_FIXED32_HEADER_SHA256,
        "bounded pb_decode_fixed32 header bytes changed",
    )

    upstream = (HERE / "pb_decode.c").read_bytes()
    definition = upstream[
        EXPECTED_FIXED32_UPSTREAM_START:EXPECTED_FIXED32_UPSTREAM_END
    ]
    require(len(definition) == 618, "upstream pb_decode_fixed32 definition size changed")
    require(
        sha256(definition) == EXPECTED_FIXED32_UPSTREAM_SHA256,
        "upstream pb_decode_fixed32 definition bytes changed",
    )
    require(
        definition.startswith(
            b"bool pb_decode_fixed32(pb_istream_t *stream, void *dest)\n{"
        ),
        "upstream pb_decode_fixed32 definition start changed",
    )
    require(
        definition.endswith(b"    return true;\n}\n"),
        "upstream pb_decode_fixed32 definition end changed",
    )


def verify_decode_fixed64_source_pins() -> None:
    """Authenticate the bounded fixed64 leaf, header, and upstream function."""
    source_path = ROOT / EXPECTED_FIXED64_SOURCE_PATH
    require(source_path.is_file(), "bounded pb_decode_fixed64 source is missing")
    source = source_path.read_bytes()
    require(
        len(source) == EXPECTED_FIXED64_SOURCE_SIZE,
        "bounded pb_decode_fixed64 source size changed",
    )
    require(
        sha256(source) == EXPECTED_FIXED64_SOURCE_SHA256,
        "bounded pb_decode_fixed64 source bytes changed",
    )

    header_path = ROOT / EXPECTED_FIXED64_HEADER_PATH
    require(header_path.is_file(), "bounded pb_decode_fixed64 header is missing")
    header = header_path.read_bytes()
    require(
        len(header) == EXPECTED_FIXED64_HEADER_SIZE,
        "bounded pb_decode_fixed64 header size changed",
    )
    require(
        sha256(header) == EXPECTED_FIXED64_HEADER_SHA256,
        "bounded pb_decode_fixed64 header bytes changed",
    )

    upstream = (HERE / "pb_decode.c").read_bytes()
    definition = upstream[
        EXPECTED_FIXED64_UPSTREAM_START:EXPECTED_FIXED64_UPSTREAM_END
    ]
    require(len(definition) == 834, "upstream pb_decode_fixed64 definition size changed")
    require(
        sha256(definition) == EXPECTED_FIXED64_UPSTREAM_SHA256,
        "upstream pb_decode_fixed64 definition bytes changed",
    )
    require(
        definition.startswith(
            b"bool pb_decode_fixed64(pb_istream_t *stream, void *dest)\n{"
        ),
        "upstream pb_decode_fixed64 definition start changed",
    )
    require(
        definition.endswith(b"    return true;\n}\n"),
        "upstream pb_decode_fixed64 definition end changed",
    )


def verify_read_source_pins() -> None:
    """Authenticate the bounded pb_read leaf, header, and upstream body."""
    source_path = ROOT / EXPECTED_READ_SOURCE_PATH
    require(source_path.is_file(), "bounded pb_read source is missing")
    source = source_path.read_bytes()
    require(
        len(source) == EXPECTED_READ_SOURCE_SIZE,
        "bounded pb_read source size changed",
    )
    require(
        sha256(source) == EXPECTED_READ_SOURCE_SHA256,
        "bounded pb_read source bytes changed",
    )

    header_path = ROOT / EXPECTED_READ_HEADER_PATH
    require(header_path.is_file(), "bounded pb_read header is missing")
    header = header_path.read_bytes()
    require(
        len(header) == EXPECTED_READ_HEADER_SIZE,
        "bounded pb_read header size changed",
    )
    require(
        sha256(header) == EXPECTED_READ_HEADER_SHA256,
        "bounded pb_read header bytes changed",
    )

    upstream = (HERE / "pb_decode.c").read_bytes()
    definition = upstream[EXPECTED_READ_UPSTREAM_START:EXPECTED_READ_UPSTREAM_END]
    require(len(definition) == 814, "upstream pb_read definition size changed")
    require(
        sha256(definition) == EXPECTED_READ_UPSTREAM_SHA256,
        "upstream pb_read definition bytes changed",
    )
    require(
        definition.startswith(b"bool checkreturn pb_read(pb_istream_t *stream,"),
        "upstream pb_read definition start changed",
    )
    require(
        definition.endswith(b"    return true;\n}"),
        "upstream pb_read definition end changed",
    )


def verify_istream_source_pins() -> None:
    """Authenticate the bounded constructor, header, audit, and upstream body."""
    for path, size, digest, label in (
        (
            EXPECTED_ISTREAM_SOURCE_PATH, EXPECTED_ISTREAM_SOURCE_SIZE,
            EXPECTED_ISTREAM_SOURCE_SHA256, "source",
        ),
        (
            EXPECTED_ISTREAM_HEADER_PATH, EXPECTED_ISTREAM_HEADER_SIZE,
            EXPECTED_ISTREAM_HEADER_SHA256, "header",
        ),
        (
            EXPECTED_ISTREAM_AUDIT_PATH, EXPECTED_ISTREAM_AUDIT_SIZE,
            EXPECTED_ISTREAM_AUDIT_SHA256, "audit",
        ),
    ):
        candidate = ROOT / path
        require(candidate.is_file(), f"bounded pb_istream_from_buffer {label} is missing")
        data = candidate.read_bytes()
        require(len(data) == size, f"bounded pb_istream_from_buffer {label} size changed")
        require(sha256(data) == digest, f"bounded pb_istream_from_buffer {label} bytes changed")

    upstream = (HERE / "pb_decode.c").read_bytes()
    definition = upstream[EXPECTED_ISTREAM_UPSTREAM_START:EXPECTED_ISTREAM_UPSTREAM_END]
    require(len(definition) == 578, "upstream pb_istream_from_buffer definition size changed")
    require(
        sha256(definition) == EXPECTED_ISTREAM_UPSTREAM_SHA256,
        "upstream pb_istream_from_buffer definition bytes changed",
    )
    require(
        definition.startswith(b"pb_istream_t pb_istream_from_buffer("),
        "upstream pb_istream_from_buffer definition start changed",
    )


def verify_svarint_source_pins() -> None:
    """Authenticate the bounded signed-varint source, header, audit, and upstream body."""
    for path, size, digest, label in (
        (
            EXPECTED_SVARINT_SOURCE_PATH, EXPECTED_SVARINT_SOURCE_SIZE,
            EXPECTED_SVARINT_SOURCE_SHA256, "source",
        ),
        (
            EXPECTED_SVARINT_HEADER_PATH, EXPECTED_SVARINT_HEADER_SIZE,
            EXPECTED_SVARINT_HEADER_SHA256, "header",
        ),
        (
            EXPECTED_SVARINT_AUDIT_PATH, EXPECTED_SVARINT_AUDIT_SIZE,
            EXPECTED_SVARINT_AUDIT_SHA256, "audit",
        ),
    ):
        candidate = ROOT / path
        require(candidate.is_file(), f"bounded pb_decode_svarint {label} is missing")
        data = candidate.read_bytes()
        require(len(data) == size, f"bounded pb_decode_svarint {label} size changed")
        require(sha256(data) == digest, f"bounded pb_decode_svarint {label} bytes changed")

    upstream = (HERE / "pb_decode.c").read_bytes()
    definition = upstream[EXPECTED_SVARINT_UPSTREAM_START:EXPECTED_SVARINT_UPSTREAM_END]
    require(len(definition) == 298, "upstream pb_decode_svarint definition size changed")
    require(
        sha256(definition) == EXPECTED_SVARINT_UPSTREAM_SHA256,
        "upstream pb_decode_svarint definition bytes changed",
    )
    require(
        definition.startswith(b"bool pb_decode_svarint("),
        "upstream pb_decode_svarint definition start changed",
    )


def brace_balanced_definition(source: bytes, signature: bytes) -> tuple[int, int]:
    """Extract one C definition while ignoring braces in comments/literals."""
    start = source.index(signature)
    opening = source.index(b"{", start)
    depth = 0
    state = "code"
    escaped = False
    index = opening
    while index < len(source):
        current = source[index]
        following = source[index + 1] if index + 1 < len(source) else None
        if state in ("string", "character"):
            if escaped:
                escaped = False
            elif current == ord("\\"):
                escaped = True
            elif current == (ord('"') if state == "string" else ord("'")):
                state = "code"
        elif state == "line-comment":
            if current == ord("\n"):
                state = "code"
        elif state == "block-comment":
            if current == ord("*") and following == ord("/"):
                state = "code"
                index += 1
        elif current == ord("/") and following == ord("/"):
            state = "line-comment"
            index += 1
        elif current == ord("/") and following == ord("*"):
            state = "block-comment"
            index += 1
        elif current == ord('"'):
            state = "string"
        elif current == ord("'"):
            state = "character"
        elif current == ord("{"):
            depth += 1
        elif current == ord("}"):
            depth -= 1
            if depth == 0:
                return start, index + 1
        index += 1
    raise ValueError("unterminated C definition")


def verify_varint32_source_pins() -> None:
    """Authenticate altered C/H, evidence, and both canonical definitions."""
    for path, size, digest, label in (
        (EXPECTED_VARINT32_SOURCE_PATH, EXPECTED_VARINT32_SOURCE_SIZE,
         EXPECTED_VARINT32_SOURCE_SHA256, "source"),
        (EXPECTED_VARINT32_HEADER_PATH, EXPECTED_VARINT32_HEADER_SIZE,
         EXPECTED_VARINT32_HEADER_SHA256, "header"),
        (EXPECTED_VARINT32_AUDIT_PATH, EXPECTED_VARINT32_AUDIT_SIZE,
         EXPECTED_VARINT32_AUDIT_SHA256, "evidence"),
    ):
        candidate = ROOT / path
        require(candidate.is_file(), f"pb_decode_varint32 {label} is missing")
        data = candidate.read_bytes()
        require(len(data) == size, f"pb_decode_varint32 {label} size changed")
        require(sha256(data) == digest, f"pb_decode_varint32 {label} hash changed")
    upstream = (HERE / "pb_decode.c").read_bytes()
    definitions = (
        (
            b"static bool checkreturn pb_decode_varint32_eof(pb_istream_t *stream, uint32_t *dest, bool *eof)\n{",
            5762, 7483, 1721,
            "66833ae2defb892aa17162625ef107bda03be44e73f0b120d48e6d2b52770e2c",
            "private",
        ),
        (
            b"bool checkreturn pb_decode_varint32(pb_istream_t *stream, uint32_t *dest)\n{",
            7485, 7617, 132,
            "ef3f2bd19c12b07ca055ab63f8e82ea6f4b34e67aefb277435092e7485834f0f",
            "public",
        ),
    )
    for signature, start, end, size, digest, label in definitions:
        require(
            brace_balanced_definition(upstream, signature) == (start, end),
            f"upstream pb_decode_varint32 {label} extraction span changed",
        )
        body = upstream[start:end]
        require(len(body) == size,
                f"upstream pb_decode_varint32 {label} size changed")
        require(sha256(body) == digest,
                f"upstream pb_decode_varint32 {label} hash changed")


def generated_build_path(path: Path, root: Path) -> bool:
    """Return whether a configuration lives below generated build output."""
    return any(
        part == "build" or part.startswith("build-")
        for part in path.relative_to(root).parts
    )


def verify_production_exclusion() -> None:
    """Reject broad snapshot linkage; permit thirteen pinned altered functions."""
    reference_tokens = (
        "third_party/nanopb",
        "NANOPB_DIR",
        "pb_common.c",
        "pb_decode.c",
        "pb_encode.c",
    )

    # The snapshot verifier may be registered with ``vendor-snapshots``.  Only
    # these exact directory/recipe lines are metadata verification; every
    # other Makefile use remains a production integration and fails closed.
    makefile = ROOT / "Makefile"
    if makefile.is_file():
        allowed_makefile_references = {
            "NANOPB_DIR := third_party/nanopb",
            "\t$(PYTHON) $(NANOPB_DIR)/verify_snapshot.py",
        }
        for line_number, line in enumerate(
            makefile.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            if any(token in line for token in reference_tokens):
                require(
                    line in allowed_makefile_references,
                    f"snapshot is production-configured by Makefile:{line_number}",
                )

    configured: set[Path] = set()
    manifests = ROOT / "manifests"
    if manifests.is_dir():
        configured.update(
            path
            for path in manifests.rglob("*")
            if path.is_file() and not generated_build_path(path, manifests)
        )

    component_suffixes = {
        ".asm",
        ".c",
        ".h",
        ".json",
        ".ld",
        ".lds",
        ".mk",
        ".py",
        ".s",
    }
    components = ROOT / "components"
    if components.is_dir():
        configured.update(
            path
            for path in components.rglob("*")
            if path.is_file()
            and not generated_build_path(path, components)
            and (path.suffix.lower() in component_suffixes or path.name == "Makefile")
        )

    configured.update(
        {
            ROOT / "tools" / "apollo_overlay.py",
            ROOT / "tools" / "open_cfw.py",
        }
    )
    allowed_upstream_url = (
        "https://github.com/nanopb/nanopb/blob/"
        f"{EXPECTED_COMMIT}/pb_decode.c"
    )
    overlay_path = ROOT / "components/apollo_main/core_overlay/overlay.json"
    for path in sorted(configured):
        if not path.is_file():
            continue
        if path == overlay_path:
            continue
        content = path.read_text(encoding="utf-8")
        require(
            not any(token in content for token in reference_tokens),
            f"snapshot is production-configured by {path.relative_to(ROOT)}",
        )

    require(overlay_path.is_file(), "bounded nanopb production overlay is missing")
    overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
    expected_functions = {
        "open_cfw_nanopb_decode_varint",
        "open_cfw_nanopb_skip_varint",
        "open_cfw_nanopb_close_string_substream",
        "open_cfw_nanopb_decode_fixed32",
        "open_cfw_nanopb_decode_fixed64",
        "open_cfw_nanopb_read",
        "open_cfw_nanopb_buf_read",
        "open_cfw_nanopb_readbyte",
        "open_cfw_nanopb_istream_from_buffer",
        "open_cfw_nanopb_decode_svarint",
        "open_cfw_nanopb_decode_varint32_eof",
        "open_cfw_nanopb_decode_varint32",
        "open_cfw_nanopb_skip_string",
    }
    production = [
        item
        for item in overlay.get("relocated_leaves", [])
        if item.get("function") in expected_functions
        or allowed_upstream_url in json.dumps(item)
    ]
    require(len(production) == 13, "nanopb production leaf set is not exact")
    require(
        {item.get("function") for item in production} == expected_functions,
        "nanopb production function changed",
    )
    leaves = {item["function"]: item for item in production}
    leaf = leaves["open_cfw_nanopb_decode_varint"]
    skip_leaf = leaves["open_cfw_nanopb_skip_varint"]
    close_leaf = leaves["open_cfw_nanopb_close_string_substream"]
    fixed32_leaf = leaves["open_cfw_nanopb_decode_fixed32"]
    fixed64_leaf = leaves["open_cfw_nanopb_decode_fixed64"]
    read_leaf = leaves["open_cfw_nanopb_read"]
    buf_leaf = leaves["open_cfw_nanopb_buf_read"]
    readbyte_leaf = leaves["open_cfw_nanopb_readbyte"]
    istream_leaf = leaves["open_cfw_nanopb_istream_from_buffer"]
    svarint_leaf = leaves["open_cfw_nanopb_decode_svarint"]
    varint32_private_leaf = leaves["open_cfw_nanopb_decode_varint32_eof"]
    varint32_public_leaf = leaves["open_cfw_nanopb_decode_varint32"]
    skip_string_leaf = leaves["open_cfw_nanopb_skip_string"]
    other_overlay = dict(overlay)
    other_overlay["relocated_leaves"] = [
        item for item in overlay.get("relocated_leaves", []) if item not in production
    ]
    require(
        not any(
            token in json.dumps(other_overlay, sort_keys=True)
            for token in reference_tokens
        ),
        "broad nanopb runtime reference exists outside the bounded leaves",
    )
    require(
        leaf.get("function") == "open_cfw_nanopb_decode_varint",
        "nanopb production function changed",
    )
    require(
        leaf.get("source")
        == {
            "path": (
                "components/shared/nanopb/"
                "runtime_nanopb_decode_varint.c"
            ),
            "size": 2224,
            "sha256": (
                "b1de68b98ee043bd07d1e10706166a13b"
                "13693534e382705bbad6866411fbe05"
            ),
            "license": "Zlib",
            "origin": (
                "altered production adaptation of authenticated nanopb "
                "0.4.9 pb_decode_varint, selected as a compatibility "
                "baseline for the recovered G2 ABI"
            ),
            "upstream": allowed_upstream_url,
            "upstream_commit": EXPECTED_COMMIT,
            "evidence": (
                "docs/research/"
                "nanopb-decode-varint-source-candidate-audit.md"
            ),
        },
        "nanopb production source registration changed",
    )
    scrubbed_leaf = json.loads(json.dumps(leaf))
    scrubbed_leaf["source"]["upstream"] = ""
    require(
        not any(
            token in json.dumps(scrubbed_leaf, sort_keys=True)
            for token in reference_tokens
        ),
        "broad nanopb runtime reference exists inside the bounded leaf",
    )
    require(
        leaf.get("strict_relocation_contract") is True,
        "nanopb production relocation contract is not strict",
    )
    expected_call = {
            "offset": 24,
            "type": "R_ARM_THM_CALL",
            "symbol": "open_cfw_nanopb_readbyte",
            "symbol_type": "STT_NOTYPE",
            "target_address": 0x0048F454,
    }
    require(
        leaf.get("relocations")
        == [
            expected_call,
            {
                "offset": 108,
                "type": "R_ARM_THM_MOVW_PREL_NC",
                "symbol": ".L.str",
            },
            {
                "offset": 112,
                "type": "R_ARM_THM_MOVT_PREL",
                "symbol": ".L.str",
            },
        ],
        "nanopb canonical relocation closure changed",
    )
    require(
        leaf.get("toolchain_profiles", {}).get("linux-clang", {}).get(
            "relocations"
        )
        == [
            expected_call,
            {
                "offset": 104,
                "type": "R_ARM_THM_MOVW_PREL_NC",
                "symbol": ".L.str",
            },
            {
                "offset": 108,
                "type": "R_ARM_THM_MOVT_PREL",
                "symbol": ".L.str",
            },
        ],
        "nanopb Linux relocation closure changed",
    )
    require(
        leaf.get("closure")
        == {
            "text_section": ".text.open_cfw_nanopb_decode_varint",
            "rodata": {
                "section": ".rodata.str1.1",
                "size": 16,
                "sha256": (
                    "e9b62825b028cfc32f718b48de14fcbc"
                    "783a9009279d2c88cf4394d54767141d"
                ),
                "alignment": 1,
                "symbols": [{"name": ".L.str", "offset": 0, "size": 16}],
            },
        },
        "nanopb local read-only-data closure changed",
    )
    source_path = ROOT / leaf["source"]["path"]
    require(source_path.is_file(), "bounded nanopb production source is missing")
    source = source_path.read_bytes()
    require(len(source) == 2224, "bounded nanopb production source size changed")
    require(
        sha256(source)
        == "b1de68b98ee043bd07d1e10706166a13b13693534e382705bbad6866411fbe05",
        "bounded nanopb production source bytes changed",
    )

    require(
        skip_leaf.get("source")
        == {
            "path": EXPECTED_SKIP_SOURCE_PATH,
            "size": EXPECTED_SKIP_SOURCE_SIZE,
            "sha256": EXPECTED_SKIP_SOURCE_SHA256,
            "license": "Zlib",
            "origin": (
                "altered production adaptation of authenticated nanopb "
                "0.4.9 pb_skip_varint, selected as a compatibility "
                "baseline for the recovered G2 ABI"
            ),
            "upstream": allowed_upstream_url,
            "upstream_commit": EXPECTED_COMMIT,
            "evidence": "docs/research/nanopb-skip-varint-source-audit.md",
        },
        "pb_skip_varint production source registration changed",
    )
    scrubbed_skip_leaf = json.loads(json.dumps(skip_leaf))
    scrubbed_skip_leaf["source"]["upstream"] = ""
    require(
        not any(
            token in json.dumps(scrubbed_skip_leaf, sort_keys=True)
            for token in reference_tokens
        ),
        "broad nanopb runtime reference exists inside the bounded pb_skip_varint leaf",
    )
    require(
        skip_leaf.get("strict_relocation_contract") is True,
        "pb_skip_varint production relocation contract is not strict",
    )
    skip_call = {
        "offset": 18,
        "type": "R_ARM_THM_CALL",
        "symbol": "open_cfw_nanopb_read",
        "symbol_type": "STT_NOTYPE",
        "target_address": 0x0048F3BE,
    }
    require(
        skip_leaf.get("relocations") == [skip_call],
        "pb_skip_varint canonical relocation closure changed",
    )
    require(
        skip_leaf.get("toolchain_profiles", {}).get("linux-clang", {}).get(
            "relocations"
        )
        == [skip_call],
        "pb_skip_varint Linux relocation closure changed",
    )
    require(
        skip_leaf.get("expected")
        == {
            "size": 36,
            "sha256": "d3a60ee83a801c7f7ae58b45d0a1e7b6d85fd920484f738ea5698b1196897df7",
            "alignment": 4,
            "offset": 124300,
            "unrelocated_sha256": (
                "7e2f6a8b3dca56e4c2d0499a6d4f12a"
                "d97dc4bc7f127ff6f4c31b8d379f0ba3b"
            ),
        },
        "pb_skip_varint canonical text contract changed",
    )

    skip_string_call_decode = {
        "offset": 8,
        "type": "R_ARM_THM_CALL",
        "symbol": "open_cfw_nanopb_decode_varint32",
        "symbol_type": "STT_NOTYPE",
        "target_function": "open_cfw_nanopb_decode_varint32",
    }
    skip_string_call_read = {
        "offset": 20,
        "type": "R_ARM_THM_CALL",
        "symbol": "open_cfw_nanopb_read",
        "symbol_type": "STT_NOTYPE",
        "target_function": "open_cfw_nanopb_read",
    }
    require(
        skip_string_leaf.get("source")
        == {
            "path": EXPECTED_SKIP_STRING_SOURCE_PATH,
            "size": EXPECTED_SKIP_STRING_SOURCE_SIZE,
            "sha256": EXPECTED_SKIP_STRING_SOURCE_SHA256,
            "license": "Zlib",
            "origin": (
                "altered production adaptation of authenticated nanopb "
                "0.4.9 pb_skip_string"
            ),
            "upstream": allowed_upstream_url,
            "upstream_commit": EXPECTED_COMMIT,
            "evidence": EXPECTED_SKIP_STRING_AUDIT_PATH,
        },
        "pb_skip_string production source registration changed",
    )
    require(
        skip_string_leaf.get("strict_relocation_contract") is True,
        "pb_skip_string production relocation contract is not strict",
    )
    require(
        skip_string_leaf.get("expected")
        == {
            "size": 34,
            "sha256": "3b1a0dbe465d562770e02d5afe04357087a6bfee22342a0f6844986a0161f547",
            "alignment": 4,
            "offset": 125224,
            "unrelocated_sha256": "d3216f569354900680dae5d78350af7668be4d8fbdae64a47afc4f440b0df920",
        },
        "pb_skip_string Apple text contract changed",
    )
    require(
        skip_string_leaf.get("relocations")
        == [skip_string_call_decode, skip_string_call_read],
        "pb_skip_string Apple relocation closure changed",
    )
    require(
        skip_string_leaf.get("toolchain_profiles")
        == {
            "linux-clang": {
                "reviewed_version_prefix": "Homebrew clang version 22.1.8",
                "expected": {
                    "size": 34,
                    "sha256": "3b1a0dbe465d562770e02d5afe04357087a6bfee22342a0f6844986a0161f547",
                    "alignment": 4,
                    "offset": 127048,
                    "unrelocated_sha256": "d3216f569354900680dae5d78350af7668be4d8fbdae64a47afc4f440b0df920",
                },
                "relocations": [skip_string_call_decode, skip_string_call_read],
            }
        },
        "pb_skip_string Linux configuration contract changed",
    )

    require(
        set(close_leaf)
        == {
            "function",
            "source",
            "toolchain",
            "strict_relocation_contract",
            "expected",
            "relocations",
            "toolchain_profiles",
        },
        "pb_close_string_substream production leaf schema changed",
    )
    require(
        close_leaf.get("source")
        == {
            "path": EXPECTED_CLOSE_SOURCE_PATH,
            "size": EXPECTED_CLOSE_SOURCE_SIZE,
            "sha256": EXPECTED_CLOSE_SOURCE_SHA256,
            "license": "Zlib",
            "origin": (
                "altered production adaptation of authenticated nanopb "
                "0.4.9 pb_close_string_substream, selected as a "
                "compatibility baseline for the recovered G2 stream ABI"
            ),
            "upstream": allowed_upstream_url,
            "upstream_commit": EXPECTED_COMMIT,
            "evidence": (
                "docs/research/"
                "nanopb-close-string-substream-source-audit.md"
            ),
        },
        "pb_close_string_substream production source registration changed",
    )
    scrubbed_close_leaf = json.loads(json.dumps(close_leaf))
    scrubbed_close_leaf["source"]["upstream"] = ""
    require(
        not any(
            token in json.dumps(scrubbed_close_leaf, sort_keys=True)
            for token in reference_tokens
        ),
        (
            "broad nanopb runtime reference exists inside the bounded "
            "pb_close_string_substream leaf"
        ),
    )
    require(
        close_leaf.get("toolchain")
        == {
            "target": "thumbv7em-none-eabi",
            "reviewed_version_prefix": "Apple clang version 21.0.0",
            "flags": [
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
            ],
        },
        "pb_close_string_substream production toolchain contract changed",
    )
    require(
        close_leaf.get("strict_relocation_contract") is True,
        "pb_close_string_substream production relocation contract is not strict",
    )
    close_call = {
        "offset": 16,
        "type": "R_ARM_THM_CALL",
        "symbol": "open_cfw_nanopb_read",
        "symbol_type": "STT_NOTYPE",
        "target_address": 0x0048F3BE,
    }
    require(
        close_leaf.get("expected")
        == {
            "size": 36,
            "sha256": "c838be0dfb478fe7fa03d9d71069a200a6477eb5783b631d7d977cd501475438",
            "alignment": 4,
            "offset": 124444,
            "unrelocated_sha256": (
                "5e6ee5f441e5ba91e0e0147b8453a311"
                "86f3ce4bd0efc114edda60f00093a51e"
            ),
        },
        "pb_close_string_substream canonical text contract changed",
    )
    require(
        close_leaf.get("relocations") == [close_call],
        "pb_close_string_substream canonical relocation closure changed",
    )
    require(
        close_leaf.get("toolchain_profiles")
        == {
            "linux-clang": {
                "reviewed_version_prefix": "Homebrew clang version 22.1.8",
                "expected": {
                    "size": 36,
                    "sha256": (
                        "a90a09f0f98c5b4cf7d885af34c914ae"
                        "5d492ac7352b5e359ba68ad482cb3044"
                    ),
                    "alignment": 4,
                    "offset": 126264,
                    "unrelocated_sha256": (
                        "5e6ee5f441e5ba91e0e0147b8453a311"
                        "86f3ce4bd0efc114edda60f00093a51e"
                    ),
                },
                "relocations": [close_call],
            }
        },
        "pb_close_string_substream Linux configuration contract changed",
    )
    fixed32_source = fixed32_leaf.get("source", {})
    require(
        {
            "path": fixed32_source.get("path"),
            "size": fixed32_source.get("size"),
            "sha256": fixed32_source.get("sha256"),
            "license": fixed32_source.get("license"),
            "upstream_commit": fixed32_source.get("upstream_commit"),
        }
        == {
            "path": EXPECTED_FIXED32_SOURCE_PATH,
            "size": EXPECTED_FIXED32_SOURCE_SIZE,
            "sha256": EXPECTED_FIXED32_SOURCE_SHA256,
            "license": "Zlib",
            "upstream_commit": EXPECTED_COMMIT,
        },
        "pb_decode_fixed32 production source registration changed",
    )
    require(
        fixed32_leaf.get("strict_relocation_contract") is True,
        "pb_decode_fixed32 production relocation contract is not strict",
    )
    fixed32_call = {
        "offset": 10,
        "type": "R_ARM_THM_CALL",
        "symbol": "open_cfw_nanopb_read",
        "symbol_type": "STT_NOTYPE",
        "target_address": 0x0048F3BE,
    }
    require(
        fixed32_leaf.get("relocations") == [fixed32_call],
        "pb_decode_fixed32 canonical relocation closure changed",
    )
    require(
        fixed32_leaf.get("toolchain_profiles", {})
        .get("linux-clang", {})
        .get("relocations")
        == [fixed32_call],
        "pb_decode_fixed32 Linux relocation closure changed",
    )
    require(
        fixed32_leaf.get("expected")
        == {
            "size": 50,
            "sha256": (
                "c9fc88c025ec843fa3ad3f77b4e1bfb8"
                "4126fd397a81d96c271646eb70632539"
            ),
            "alignment": 4,
            "offset": 124496,
            "unrelocated_sha256": (
                "798f8f7cbed57f6ba11dad46a6de9d25"
                "cb1f1710eb4fa904d79b6fe449952a04"
            ),
        },
        "pb_decode_fixed32 canonical text contract changed",
    )
    require(
        fixed32_leaf.get("toolchain_profiles", {})
        .get("linux-clang", {})
        .get("expected")
        == {
            "size": 50,
            "sha256": (
                "53a1961d2df94674da6890611087ab865"
                "498084ced6a6f0c6850dcee23c7bf60"
            ),
            "alignment": 4,
            "offset": 126316,
            "unrelocated_sha256": (
                "798f8f7cbed57f6ba11dad46a6de9d25"
                "cb1f1710eb4fa904d79b6fe449952a04"
            ),
        },
        "pb_decode_fixed32 Linux text contract changed",
    )
    fixed32_patches = [
        item
        for item in overlay.get("patch_sites", [])
        if item.get("target_function") == "open_cfw_nanopb_decode_fixed32"
    ]
    require(len(fixed32_patches) == 1, "pb_decode_fixed32 stock patch is not unique")
    require(
        {
            "runtime_address": fixed32_patches[0].get("runtime_address"),
            "expected_size": fixed32_patches[0].get("expected_size"),
            "expected_sha256": fixed32_patches[0].get("expected_sha256"),
            "branch": fixed32_patches[0].get("branch"),
        }
        == {
            "runtime_address": 0x00490190,
            "expected_size": 28,
            "expected_sha256": (
                "1ee27599a8ac5b8d2a0cbaac59986fb4"
                "9be7b24c348a960a216b8cbbecce5bf3"
            ),
            "branch": "b_w",
        },
        "pb_decode_fixed32 stock patch contract changed",
    )

    fixed64_source = fixed64_leaf.get("source", {})
    require(
        fixed64_source
        == {
            "path": EXPECTED_FIXED64_SOURCE_PATH,
            "size": EXPECTED_FIXED64_SOURCE_SIZE,
            "sha256": EXPECTED_FIXED64_SOURCE_SHA256,
            "license": "Zlib",
            "origin": (
                "altered production adaptation of authenticated nanopb "
                "0.4.9 pb_decode_fixed64, selected as a compatibility "
                "baseline for the recovered G2 stream ABI"
            ),
            "upstream": allowed_upstream_url,
            "upstream_commit": EXPECTED_COMMIT,
            "evidence": (
                "docs/research/nanopb-decode-fixed64-candidate-audit.md"
            ),
        },
        "pb_decode_fixed64 production source registration changed",
    )
    require(
        fixed64_leaf.get("strict_relocation_contract") is True,
        "pb_decode_fixed64 production relocation contract is not strict",
    )
    fixed64_call = {
        "offset": 10,
        "type": "R_ARM_THM_CALL",
        "symbol": "open_cfw_nanopb_read",
        "symbol_type": "STT_NOTYPE",
        "target_address": 0x0048F3BE,
    }
    require(
        fixed64_leaf.get("relocations") == [fixed64_call],
        "pb_decode_fixed64 canonical relocation closure changed",
    )
    require(
        fixed64_leaf.get("toolchain_profiles", {})
        .get("linux-clang", {})
        .get("relocations")
        == [fixed64_call],
        "pb_decode_fixed64 Linux relocation closure changed",
    )
    require(
        fixed64_leaf.get("expected")
        == {
            "size": 28,
            "sha256": (
                "6e970db6346919f9937f459489b5699b1"
                "b5bf5e0d2b4f19a327cbbe6d2b4adb0"
            ),
            "alignment": 4,
            "offset": 124612,
            "unrelocated_sha256": (
                "c4cfb6fece88a057c874d8f2ffcce961"
                "df9ef15fb16c78421f48396f0cceff2c"
            ),
        },
        "pb_decode_fixed64 canonical text contract changed",
    )
    require(
        fixed64_leaf.get("toolchain_profiles", {})
        .get("linux-clang", {})
        .get("expected")
        == {
            "size": 30,
            "sha256": (
                "4e067bc2e9e3cb63335507bd64f3e733"
                "21c24294ec3313c72f57cd801a9b8968"
            ),
            "alignment": 4,
            "offset": 126432,
            "unrelocated_sha256": (
                "bfaf01f7496cce042c84c35708421508"
                "fbf2fa5acd9d9fcb209753901e09af10"
            ),
        },
        "pb_decode_fixed64 Linux text contract changed",
    )
    fixed64_patches = [
        item
        for item in overlay.get("patch_sites", [])
        if item.get("target_function") == "open_cfw_nanopb_decode_fixed64"
    ]
    require(len(fixed64_patches) == 1, "pb_decode_fixed64 stock patch is not unique")
    require(
        {
            "runtime_address": fixed64_patches[0].get("runtime_address"),
            "expected_size": fixed64_patches[0].get("expected_size"),
            "expected_sha256": fixed64_patches[0].get("expected_sha256"),
            "branch": fixed64_patches[0].get("branch"),
        }
        == {
            "runtime_address": 0x004901AC,
            "expected_size": 32,
            "expected_sha256": (
                "96228dfbdfe30665d79281ba0fd5ba3b3"
                "af38701396671cd20b77623ffd82d54"
            ),
            "branch": "b_w",
        },
        "pb_decode_fixed64 stock patch contract changed",
    )
    require(
        read_leaf.get("source")
        == {
            "path": EXPECTED_READ_SOURCE_PATH,
            "size": EXPECTED_READ_SOURCE_SIZE,
            "sha256": EXPECTED_READ_SOURCE_SHA256,
            "license": "Zlib",
            "origin": (
                "altered production adaptation of authenticated nanopb "
                "0.4.9 pb_read, byte-identical at source level in "
                "authenticated nanopb 0.4.7 through 0.4.9"
            ),
            "upstream": allowed_upstream_url,
            "upstream_commit": EXPECTED_COMMIT,
            "evidence": "docs/research/nanopb-read-source-candidate-audit.md",
        },
        "pb_read production source registration changed",
    )
    require(
        read_leaf.get("strict_relocation_contract") is True,
        "pb_read production relocation contract is not strict",
    )
    read_relocations = [
        {
            "offset": offset,
            "type": kind,
            "symbol": symbol,
            "symbol_type": "STT_NOTYPE",
            "target_address": address,
        }
        for offset, kind, symbol, address in (
            (28, "R_ARM_THM_MOVW_ABS_NC", "open_cfw_nanopb_end_of_stream_error", 0x00787C70),
            (32, "R_ARM_THM_MOVT_ABS", "open_cfw_nanopb_end_of_stream_error", 0x00787C70),
            (66, "R_ARM_THM_MOVW_ABS_NC", "open_cfw_nanopb_stock_buffer_read_identity", 0x0048F3A5),
            (70, "R_ARM_THM_MOVT_ABS", "open_cfw_nanopb_stock_buffer_read_identity", 0x0048F3A5),
            (134, "R_ARM_THM_MOVW_ABS_NC", "open_cfw_nanopb_io_error", 0x0078B690),
            (138, "R_ARM_THM_MOVT_ABS", "open_cfw_nanopb_io_error", 0x0078B690),
        )
    ]
    require(
        read_leaf.get("relocations") == read_relocations,
        "pb_read retained-seam relocation closure changed",
    )
    expected_read = {
        "size": 158,
        "sha256": (
            "8b3de44a2cf7ca2e07715c913db0fa45"
            "4ef65cbc453366190b12736e455aa7a8"
        ),
        "alignment": 4,
        "offset": 124640,
        "unrelocated_sha256": (
            "06def086733fd9801b712161943b0da64"
            "e3b2bdf82e6f5962ee9207c738c00b1"
        ),
    }
    require(
        read_leaf.get("expected") == expected_read,
        "pb_read canonical text contract changed",
    )
    expected_read["offset"] = 126464
    require(
        read_leaf.get("toolchain_profiles", {})
        .get("linux-clang", {})
        .get("expected")
        == expected_read,
        "pb_read Linux text contract changed",
    )
    read_patches = [
        item
        for item in overlay.get("patch_sites", [])
        if item.get("target_function") == "open_cfw_nanopb_read"
    ]
    require(len(read_patches) == 1, "pb_read stock patch is not unique")
    require(
        read_patches[0]
        == {
            "name": "replace_nanopb_read",
            "runtime_address": 0x0048F3BE,
            "expected_size": 150,
            "expected_sha256": (
                "69aecb900c749fd98bd2d05e2229e9a3"
                "d6829bd36f3e393f624e3579a9b4af7f"
            ),
            "branch": "b_w",
            "target_function": "open_cfw_nanopb_read",
        },
        "pb_read stock patch contract changed",
    )
    pair_sources = (
        (
            buf_leaf,
            "open_cfw_nanopb_buf_read",
            EXPECTED_BUF_SOURCE_PATH,
            EXPECTED_BUF_SOURCE_SIZE,
            EXPECTED_BUF_SOURCE_SHA256,
            "altered production adaptation of authenticated nanopb 0.4.9 "
            "private buf_read, byte-identical at source level in authenticated "
            "nanopb 0.4.7 through 0.4.9",
        ),
        (
            readbyte_leaf,
            "open_cfw_nanopb_readbyte",
            EXPECTED_READBYTE_SOURCE_PATH,
            EXPECTED_READBYTE_SOURCE_SIZE,
            EXPECTED_READBYTE_SOURCE_SHA256,
            "altered production adaptation of authenticated nanopb 0.4.9 "
            "private pb_readbyte, byte-identical at source level in authenticated "
            "nanopb 0.4.7 through 0.4.9",
        ),
    )
    for item, function, path, size, digest, origin in pair_sources:
        require(
            item.get("source")
            == {
                "path": path,
                "size": size,
                "sha256": digest,
                "license": "Zlib",
                "origin": origin,
                "upstream": allowed_upstream_url,
                "upstream_commit": EXPECTED_COMMIT,
                "evidence": "docs/research/nanopb-private-read-pair-source-audit.md",
            },
            f"{function} source registration changed",
        )
        require(
            item.get("strict_relocation_contract") is True,
            f"{function} relocation contract is not strict",
        )
    require(
        buf_leaf.get("expected")
        == {
            "size": 30,
            "sha256": "f312e087cf1fbecf19bd5fa0052d3a63ca91287c811de169aaf2a09322e0115e",
            "alignment": 4,
            "offset": 124800,
            "unrelocated_sha256": "db26e5bd51f3d313907af94bfe545cc9962b867ed18285f2025c401e8613700a",
        }
        and buf_leaf.get("relocations")
        == [{
            "offset": 18,
            "type": "R_ARM_THM_CALL",
            "symbol": "__aeabi_memcpy",
            "symbol_type": "STT_NOTYPE",
            "target_address": 0x00439BE4,
        }],
        "buf_read Apple text/relocation contract changed",
    )
    require(
        readbyte_leaf.get("expected")
        == {
            "size": 64,
            "sha256": "f3395a19a7406016e6b1f1daf14969dee91ccde4e9a98ba4eeaba0016e131871",
            "alignment": 4,
            "offset": 124832,
            "unrelocated_sha256": "eda66d0ae6274a2078b6eceaefc0e773169d5e15b26bce650a8d48b818e4f2b8",
        },
        "pb_readbyte Apple text contract changed",
    )
    pair_patches = {
        item.get("target_function"): item
        for item in overlay.get("patch_sites", [])
        if item.get("target_function") in {
            "open_cfw_nanopb_buf_read", "open_cfw_nanopb_readbyte"
        }
    }
    require(
        pair_patches
        == {
            "open_cfw_nanopb_buf_read": {
                "name": "replace_nanopb_buf_read",
                "runtime_address": 0x0048F3A4,
                "expected_size": 26,
                "expected_sha256": "9d6c6690294b82bbafba82ec0f63a6bb5b78e4146543db3a30fac92469ace723",
                "branch": "b_w",
                "target_function": "open_cfw_nanopb_buf_read",
            },
            "open_cfw_nanopb_readbyte": {
                "name": "replace_nanopb_readbyte",
                "runtime_address": 0x0048F454,
                "expected_size": 72,
                "expected_sha256": "15c8303c5c1dbf1b3f143142c6169026cb8bc56b37a6291dd0457b3664b67ae5",
                "branch": "b_w",
                "target_function": "open_cfw_nanopb_readbyte",
            },
        },
        "private read-pair stock patches changed",
    )
    require(
        istream_leaf.get("source")
        == {
            "path": EXPECTED_ISTREAM_SOURCE_PATH,
            "size": EXPECTED_ISTREAM_SOURCE_SIZE,
            "sha256": EXPECTED_ISTREAM_SOURCE_SHA256,
            "license": "Zlib",
            "origin": (
                "altered production adaptation of authenticated nanopb 0.4.9 "
                "pb_istream_from_buffer, byte-identical at source level in "
                "authenticated nanopb 0.4.7 through 0.4.9"
            ),
            "upstream": allowed_upstream_url,
            "upstream_commit": EXPECTED_COMMIT,
            "evidence": EXPECTED_ISTREAM_AUDIT_PATH,
        },
        "pb_istream_from_buffer source registration changed",
    )
    identity_relocations = [
        {
            "offset": offset,
            "type": kind,
            "symbol": "open_cfw_nanopb_stock_buffer_read_identity",
            "symbol_type": "STT_NOTYPE",
            "target_address": 0x0048F3A5,
        }
        for offset, kind in (
            (0, "R_ARM_THM_MOVW_ABS_NC"),
            (4, "R_ARM_THM_MOVT_ABS"),
        )
    ]
    require(
        istream_leaf.get("strict_relocation_contract") is True
        and istream_leaf.get("relocations") == identity_relocations
        and istream_leaf.get("expected")
        == {
            "size": 20,
            "sha256": (
                "af3357e8178ab650d5476d0ad0fbfee0"
                "b44cdb288d9251da909b3ba7a1de92c4"
            ),
            "alignment": 4,
            "offset": 124896,
            "unrelocated_sha256": (
                "d106ce1009ddcbd4d39a7c56edbcd51f"
                "50d4cfa6768f78d224ea988aa9a416d7"
            ),
        },
        "pb_istream_from_buffer Apple text/relocation contract changed",
    )
    linux_istream = istream_leaf.get("toolchain_profiles", {}).get("linux-clang", {})
    require(
        linux_istream.get("relocations") == identity_relocations
        and linux_istream.get("expected")
        == {
            "size": 22,
            "sha256": (
                "59438f30232883560f65ad4e58ff97c0"
                "5dcdffdb6287fffcb7c1b79487df436d"
            ),
            "alignment": 4,
            "offset": 126720,
            "unrelocated_sha256": (
                "6c23e37c9468d866db2e2cb6bf0ce8e"
                "103fb34df1078e740b4b8d5d799c257ff"
            ),
        },
        "pb_istream_from_buffer Linux text/relocation contract changed",
    )
    istream_patches = [
        item for item in overlay.get("patch_sites", [])
        if item.get("target_function") == "open_cfw_nanopb_istream_from_buffer"
    ]
    require(
        istream_patches
        == [{
            "name": "replace_nanopb_istream_from_buffer",
            "runtime_address": 0x0048F49C,
            "expected_size": 28,
            "expected_sha256": (
                "852314bb8f86dcbd550deb0f51bc285b"
                "662e39c1b4fae66690c44a7bf4f7a674"
            ),
            "branch": "b_w",
            "target_function": "open_cfw_nanopb_istream_from_buffer",
        }],
        "pb_istream_from_buffer stock patch contract changed",
    )
    require(
        svarint_leaf.get("source")
        == {
            "path": EXPECTED_SVARINT_SOURCE_PATH,
            "size": EXPECTED_SVARINT_SOURCE_SIZE,
            "sha256": EXPECTED_SVARINT_SOURCE_SHA256,
            "license": "Zlib",
            "origin": (
                "altered production adaptation of authenticated nanopb 0.4.9 "
                "pb_decode_svarint, selected as a compatibility baseline for "
                "the recovered G2 ABI"
            ),
            "upstream": allowed_upstream_url,
            "upstream_commit": EXPECTED_COMMIT,
            "evidence": EXPECTED_SVARINT_AUDIT_PATH,
        },
        "pb_decode_svarint production source registration changed",
    )
    svarint_call = {
        "offset": 8,
        "type": "R_ARM_THM_CALL",
        "symbol": "open_cfw_nanopb_decode_varint",
        "symbol_type": "STT_NOTYPE",
        "target_function": "open_cfw_nanopb_decode_varint",
    }
    require(
        svarint_leaf.get("strict_relocation_contract") is True
        and svarint_leaf.get("relocations") == [svarint_call]
        and svarint_leaf.get("expected")
        == {
            "size": 54,
            "sha256": (
                "1b181a82adbbb72dc6fc09b1b70dd48f"
                "4c0eefdf25a8c4e71701710cb12dae3f"
            ),
            "alignment": 4,
            "offset": 124916,
            "unrelocated_sha256": (
                "19e103f83ab8879d36eb1b0513bf5416"
                "01e40bc82e69e0dc252308c0646d1286"
            ),
        },
        "pb_decode_svarint Apple text/relocation contract changed",
    )
    require(
        "target_address" not in svarint_call,
        "pb_decode_svarint call must resolve source-to-source",
    )
    require(
        svarint_leaf.get("toolchain_profiles", {}).get("linux-clang")
        == {
            "reviewed_version_prefix": "Homebrew clang version 22.1.8",
            "expected": {
                "size": 50,
                "sha256": (
                    "63e4707f5fd537094855d38f6b4df857"
                    "8b77644c131e180db2e682d32fbc1fab"
                ),
                "alignment": 4,
                "offset": 126744,
                "unrelocated_sha256": (
                    "3617ea95d4a2cbabf3a1abb375e57232"
                    "3fffcebfa68cb4e19874cb4a831d9662"
                ),
            },
            "relocations": [svarint_call],
        },
        "pb_decode_svarint Linux text/relocation contract changed",
    )
    svarint_patches = [
        item for item in overlay.get("patch_sites", [])
        if item.get("target_function") == "open_cfw_nanopb_decode_svarint"
    ]
    require(
        svarint_patches
        == [{
            "name": "replace_nanopb_decode_svarint",
            "runtime_address": 0x00490150,
            "expected_size": 64,
            "expected_sha256": (
                "80b24be422cf924f3ae1b79669312535d"
                "c0d5a56dd88be8a6b9e4ee5ff064048"
            ),
            "branch": "b_w",
            "target_function": "open_cfw_nanopb_decode_svarint",
        }],
        "pb_decode_svarint stock patch contract changed",
    )
    varint32_source = {
        "path": EXPECTED_VARINT32_SOURCE_PATH,
        "size": EXPECTED_VARINT32_SOURCE_SIZE,
        "sha256": EXPECTED_VARINT32_SOURCE_SHA256,
        "license": "Zlib",
        "origin": (
            "altered production adaptation of authenticated nanopb 0.4.9 "
            "pb_decode_varint32_eof and pb_decode_varint32"
        ),
        "upstream": allowed_upstream_url,
        "upstream_commit": EXPECTED_COMMIT,
        "evidence": EXPECTED_VARINT32_AUDIT_PATH,
    }
    require(
        varint32_private_leaf.get("source") == varint32_source
        and varint32_public_leaf.get("source") == varint32_source,
        "pb_decode_varint32 source registration changed",
    )
    private_calls = [
        {"offset": offset, "type": "R_ARM_THM_CALL",
         "symbol": "open_cfw_nanopb_readbyte", "symbol_type": "STT_NOTYPE",
         "target_function": "open_cfw_nanopb_readbyte"}
        for offset in (16, 106)
    ]
    private_literals = [
        {"offset": 208, "type": "R_ARM_THM_MOVW_PREL_NC",
         "symbol": "open_cfw_nanopb_varint32_overflow_error"},
        {"offset": 212, "type": "R_ARM_THM_MOVT_PREL",
         "symbol": "open_cfw_nanopb_varint32_overflow_error"},
    ]
    public_call = [{
        "offset": 4, "type": "R_ARM_THM_CALL",
        "symbol": "open_cfw_nanopb_decode_varint32_eof",
        "symbol_type": "STT_NOTYPE",
        "target_function": "open_cfw_nanopb_decode_varint32_eof",
    }]
    require(
        varint32_private_leaf.get("strict_relocation_contract") is True
        and varint32_private_leaf.get("relocations")
        == private_calls + private_literals
        and varint32_private_leaf.get("expected") == {
            "size": 222,
            "sha256": "36bb0167f4d3407b99ed2255cc9e77dd60dc1e9070781a257bfea59abc408171",
            "alignment": 4, "offset": 124972,
            "unrelocated_sha256": "5296b608c55171bca9d5f4d162cf53d0e6aa5f724e1cb82499a7311f2a6cc9ff",
            "closure_size": 238,
            "closure_sha256": "2c49567cfe23e36c504586218719c2e590163bec804353c8106680328d64a480",
            "rodata_offset": 222,
        }
        and varint32_private_leaf.get("closure") == {
            "text_section": ".text.open_cfw_nanopb_decode_varint32_eof",
            "rodata": {
                "section": ".rodata.open_cfw_nanopb_varint32_overflow_error",
                "size": 16,
                "sha256": "e9b62825b028cfc32f718b48de14fcbc783a9009279d2c88cf4394d54767141d",
                "alignment": 1,
                "symbols": [{
                    "name": "open_cfw_nanopb_varint32_overflow_error",
                    "offset": 0, "size": 16,
                }],
            },
        },
        "private pb_decode_varint32 Apple text/literal contract changed",
    )
    require(
        varint32_public_leaf.get("strict_relocation_contract") is True
        and varint32_public_leaf.get("relocations") == public_call
        and varint32_public_leaf.get("expected") == {
            "size": 10,
            "sha256": "1f0924d25c50933e7cd5aac05d718da6d44b7a20d4af901fa833c555eca6ff1a",
            "alignment": 4, "offset": 125212,
            "unrelocated_sha256": "e9ec8b612503f867aabf2467e3abfac44753c5576a247a00cbc4309e2a023f93",
        },
        "public pb_decode_varint32 Apple text contract changed",
    )
    require(
        varint32_private_leaf.get("toolchain_profiles", {}).get("linux-clang")
        == {
            "reviewed_version_prefix": "Homebrew clang version 22.1.8",
            "expected": {
                "size": 222,
                "sha256": "36bb0167f4d3407b99ed2255cc9e77dd60dc1e9070781a257bfea59abc408171",
                "alignment": 4, "offset": 126796,
                "unrelocated_sha256": "5296b608c55171bca9d5f4d162cf53d0e6aa5f724e1cb82499a7311f2a6cc9ff",
                "closure_size": 238,
                "closure_sha256": "2c49567cfe23e36c504586218719c2e590163bec804353c8106680328d64a480",
                "rodata_offset": 222,
            },
            "relocations": private_calls + private_literals,
        },
        "private pb_decode_varint32 Linux text/literal contract changed",
    )
    require(
        varint32_public_leaf.get("toolchain_profiles", {}).get("linux-clang")
        == {
            "reviewed_version_prefix": "Homebrew clang version 22.1.8",
            "expected": {
                "size": 10,
                "sha256": "1f0924d25c50933e7cd5aac05d718da6d44b7a20d4af901fa833c555eca6ff1a",
                "alignment": 4, "offset": 127036,
                "unrelocated_sha256": "e9ec8b612503f867aabf2467e3abfac44753c5576a247a00cbc4309e2a023f93",
            },
            "relocations": public_call,
        },
        "public pb_decode_varint32 Linux text contract changed",
    )
    varint32_patch_list = [
        item for item in overlay.get("patch_sites", [])
        if item.get("target_function") in {
            "open_cfw_nanopb_decode_varint32_eof",
            "open_cfw_nanopb_decode_varint32",
        }
    ]
    varint32_patches = {
        item["target_function"]: item for item in varint32_patch_list
    }
    require(
        len(varint32_patch_list) == 2
        and len({item["name"] for item in varint32_patch_list}) == 2
        and len(varint32_patches) == 2,
        "pb_decode_varint32 stock patches are not unique",
    )
    require(
        varint32_patches == {
            "open_cfw_nanopb_decode_varint32_eof": {
                "name": "replace_nanopb_decode_varint32_eof",
                "runtime_address": 0x0048F4B8, "expected_size": 246,
                "expected_sha256": "8583fa17383d72bbdcab6c2a7a20369dc0598d3ac3061feaf8a7b29dfa520150",
                "branch": "b_w",
                "target_function": "open_cfw_nanopb_decode_varint32_eof",
            },
            "open_cfw_nanopb_decode_varint32": {
                "name": "replace_nanopb_decode_varint32",
                "runtime_address": 0x0048F5AE, "expected_size": 10,
                "expected_sha256": "48218a658cffd7aeddfb623c9d0e7bd038ceb2a6898e9f8d08b10d5779f4f79b",
                "branch": "b_w",
                "target_function": "open_cfw_nanopb_decode_varint32",
            },
        },
        "pb_decode_varint32 stock patch contracts changed",
    )
    skip_string_patches = [
        item for item in overlay.get("patch_sites", [])
        if item.get("target_function") == "open_cfw_nanopb_skip_string"
    ]
    require(
        skip_string_patches
        == [{
            "name": "replace_nanopb_skip_string",
            "runtime_address": 0x0048F64C,
            "expected_size": 32,
            "expected_sha256": "03afe2d60436676fffba342c7b8c9504992fa903d7cba768396fd1de2c6c66cd",
            "branch": "b_w",
            "target_function": "open_cfw_nanopb_skip_string",
        }],
        "pb_skip_string stock patch contract changed",
    )
    manifest = json.loads(
        (ROOT / "manifests/g2-2.2.6.10-core-source.json").read_text(
            encoding="utf-8"
        )
    )
    regions = manifest["component_overrides"]["apollo_main"]["regions"]
    by_name = {item["name"]: item for item in regions}
    require(
        len(by_name) == len(regions),
        "Apollo-main manifest region names are not unique",
    )
    require(
        by_name.get("nanopb_istream_from_buffer_source_replacement")
        == {
            "name": "nanopb_istream_from_buffer_source_replacement",
            "function": (
                "Generated non-linking entry redirect and full Thumb NOP fill "
                "replacing the complete nanopb pb_istream_from_buffer "
                "constructor span"
            ),
            "file_offset": 357564,
            "size": 28,
            "target": "apollo510b_internal_mram",
            "target_address": 0x0048F49C,
            "address_status": "generated_source_entry_replacement",
            "output": (
                "apollo510b/source-entry-nanopb-istream-from-buffer-"
                "0x0048f49c.bin"
            ),
        },
        "pb_istream_from_buffer manifest entry ownership changed",
    )
    source_region = by_name.get("apollo_nanopb_istream_from_buffer_source_leaf", {})
    require(
        {
            key: source_region.get(key)
            for key in (
                "function", "file_offset", "size", "target",
                "target_address", "address_status", "output",
            )
        }
        == {
            "function": (
                "Zlib-licensed nanopb 0.4.9 pb_istream_from_buffer "
                "compatibility leaf preserving the recovered 16-byte stream "
                "ABI and canonical stock buffer callback identity"
            ),
            "file_offset": 3648292,
            "size": 20,
            "target": "apollo510b_internal_mram",
            "target_address": 0x007B2B04,
            "address_status": "source_compiled",
            "output": (
                "apollo510b/main-source-nanopb-istream-from-buffer-"
                "0x007b2b04.bin"
            ),
        },
        "pb_istream_from_buffer manifest source ownership changed",
    )
    require(
        by_name.get("nanopb_decode_svarint_source_replacement")
        == {
            "name": "nanopb_decode_svarint_source_replacement",
            "function": (
                "Generated entry redirect and full Thumb NOP fill replacing "
                "the complete recovered nanopb pb_decode_svarint span"
            ),
            "file_offset": 360816,
            "size": 64,
            "target": "apollo510b_internal_mram",
            "target_address": 0x00490150,
            "address_status": "generated_source_entry_replacement",
            "output": (
                "apollo510b/source-entry-nanopb-decode-svarint-"
                "0x00490150.bin"
            ),
        },
        "pb_decode_svarint manifest entry ownership changed",
    )
    require(
        by_name.get("apollo_nanopb_decode_svarint_source_leaf")
        == {
            "name": "apollo_nanopb_decode_svarint_source_leaf",
            "function": (
                "Zlib-licensed nanopb 0.4.9 pb_decode_svarint compatibility "
                "leaf closed directly over the source-owned unsigned-varint "
                "decoder"
            ),
            "file_offset": 3648312,
            "size": 54,
            "target": "apollo510b_internal_mram",
            "target_address": 0x007B2B18,
            "address_status": "source_compiled",
            "output": (
                "apollo510b/main-source-nanopb-decode-svarint-"
                "0x007b2b18.bin"
            ),
        },
        "pb_decode_svarint manifest source ownership changed",
    )
    varint32_manifest = [
        {
            "name": "nanopb_decode_varint32_eof_source_replacement",
            "function": "Generated entry redirect and full Thumb NOP fill replacing the complete private nanopb pb_decode_varint32_eof span",
            "file_offset": 357592, "size": 246,
            "target": "apollo510b_internal_mram", "target_address": 0x0048F4B8,
            "address_status": "generated_source_entry_replacement",
            "output": "apollo510b/source-entry-nanopb-decode-varint32-eof-0x0048f4b8.bin",
        },
        {
            "name": "nanopb_decode_varint32_source_replacement",
            "function": "Generated entry redirect and full Thumb NOP fill replacing the complete public nanopb pb_decode_varint32 span",
            "file_offset": 357838, "size": 10,
            "target": "apollo510b_internal_mram", "target_address": 0x0048F5AE,
            "address_status": "generated_source_entry_replacement",
            "output": "apollo510b/source-entry-nanopb-decode-varint32-0x0048f5ae.bin",
        },
        {
            "name": "apollo_nanopb_decode_varint32_eof_source_alignment",
            "function": "Generated zero padding aligning the private nanopb pb_decode_varint32_eof source leaf",
            "file_offset": 3648366, "size": 2,
            "target": "apollo510b_internal_mram", "target_address": 0x007B2B4E,
            "address_status": "generated_alignment",
            "output": "apollo510b/main-source-nanopb-decode-varint32-eof-alignment-0x007b2b4e.bin",
        },
        {
            "name": "apollo_nanopb_decode_varint32_eof_source_leaf",
            "function": "Zlib-licensed nanopb 0.4.9 private pb_decode_varint32_eof compatibility text leaf closed over the source-owned pb_readbyte implementation",
            "file_offset": 3648368, "size": 222,
            "target": "apollo510b_internal_mram", "target_address": 0x007B2B50,
            "address_status": "source_compiled",
            "output": "apollo510b/main-source-nanopb-decode-varint32-eof-0x007b2b50.bin",
        },
        {
            "name": "apollo_nanopb_decode_varint32_overflow_rodata",
            "function": "Zlib-licensed source-owned 16-byte nanopb varint overflow literal closure for the private pb_decode_varint32_eof leaf",
            "file_offset": 3648590, "size": 16,
            "target": "apollo510b_internal_mram", "target_address": 0x007B2C2E,
            "address_status": "source_compiled",
            "output": "apollo510b/main-source-nanopb-varint32-overflow-0x007b2c2e.bin",
        },
        {
            "name": "apollo_nanopb_decode_varint32_source_alignment",
            "function": "Generated zero padding aligning the public nanopb pb_decode_varint32 source leaf",
            "file_offset": 3648606, "size": 2,
            "target": "apollo510b_internal_mram", "target_address": 0x007B2C3E,
            "address_status": "generated_alignment",
            "output": "apollo510b/main-source-nanopb-decode-varint32-alignment-0x007b2c3e.bin",
        },
        {
            "name": "apollo_nanopb_decode_varint32_source_leaf",
            "function": "Zlib-licensed nanopb 0.4.9 public pb_decode_varint32 compatibility text leaf calling the private source-owned decoder directly",
            "file_offset": 3648608, "size": 10,
            "target": "apollo510b_internal_mram", "target_address": 0x007B2C40,
            "address_status": "source_compiled",
            "output": "apollo510b/main-source-nanopb-decode-varint32-0x007b2c40.bin",
        },
    ]
    require(
        [by_name.get(item["name"]) for item in varint32_manifest]
        == varint32_manifest,
        "pb_decode_varint32 manifest ownership changed",
    )
    skip_string_manifest = {
        "nanopb_skip_string_source_replacement": (
            357996, 32, 0x0048F64C, "generated_source_entry_replacement"
        ),
        "opaque_application_between_nanopb_skip_string_and_nanopb_close_string_substream": (
            358028, 350, 0x0048F66C, "official_blob"
        ),
        "apollo_nanopb_skip_string_source_alignment": (
            3648618, 2, 0x007B2C4A, "generated_alignment"
        ),
        "apollo_nanopb_skip_string_source_leaf": (
            3648620, 34, 0x007B2C4C, "source_compiled"
        ),
    }
    require(
        {
            name: (
                by_name.get(name, {}).get("file_offset"),
                by_name.get(name, {}).get("size"),
                by_name.get(name, {}).get("target_address"),
                by_name.get(name, {}).get("address_status"),
            )
            for name in skip_string_manifest
        }
        == skip_string_manifest,
        "pb_skip_string manifest ownership changed",
    )
    require(len(regions) == 960, "Apollo-main manifest region count changed")
    verify_istream_source_pins()
    verify_svarint_source_pins()
    verify_varint32_source_pins()
    verify_skip_string_source_pins()
    verify_skip_varint_source_pins()
    verify_close_string_substream_source_pins()
    verify_decode_fixed32_source_pins()
    verify_decode_fixed64_source_pins()
    verify_read_source_pins()
    for path, size, digest in (
        (EXPECTED_BUF_SOURCE_PATH, EXPECTED_BUF_SOURCE_SIZE, EXPECTED_BUF_SOURCE_SHA256),
        (EXPECTED_READBYTE_SOURCE_PATH, EXPECTED_READBYTE_SOURCE_SIZE, EXPECTED_READBYTE_SOURCE_SHA256),
        (EXPECTED_PRIVATE_HEADER_PATH, EXPECTED_PRIVATE_HEADER_SIZE, EXPECTED_PRIVATE_HEADER_SHA256),
        (EXPECTED_PRIVATE_AUDIT_PATH, EXPECTED_PRIVATE_AUDIT_SIZE, EXPECTED_PRIVATE_AUDIT_SHA256),
    ):
        source = ROOT / path
        require(source.is_file(), f"missing private read-pair file {path}")
        require(source.stat().st_size == size, f"private read-pair size changed: {path}")
        require(sha256(source.read_bytes()) == digest, f"private read-pair hash changed: {path}")


def main() -> int:
    provenance = verify_provenance()
    verify_tag_and_commit(provenance)
    verify_tree_closure(provenance)
    verify_source_files(provenance)
    verify_runtime_and_config_markers(provenance)
    verify_optional_official_image(provenance)
    verify_production_exclusion()
    print("nanopb 0.4.9 compatibility snapshot verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
