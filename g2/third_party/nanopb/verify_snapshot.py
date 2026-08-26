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
EXPECTED_PROVENANCE_SIZE = 125493
EXPECTED_PROVENANCE_SHA256 = "8a75937b09ed3f3fa8af8fa285b4bdf1774216379a42c1f9b5f61efedd39106b"
EXPECTED_APPLE_OVERLAY_PLACEMENT_DELTA = 59848
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
EXPECTED_SKIP_FIELD_SOURCE_PATH = (
    "components/shared/nanopb/runtime_nanopb_skip_field.c"
)
EXPECTED_SKIP_FIELD_SOURCE_SIZE = 2417
EXPECTED_SKIP_FIELD_SOURCE_SHA256 = (
    "b0fbb6fc99f0a47a40e53662393a43c88b01d29d4b4457910b9f6be8063e7353"
)
EXPECTED_SKIP_FIELD_HEADER_PATH = (
    "components/shared/nanopb/runtime_nanopb_skip_field.h"
)
EXPECTED_SKIP_FIELD_HEADER_SIZE = 2152
EXPECTED_SKIP_FIELD_HEADER_SHA256 = (
    "9a76c3455119f814be099085c5fac2e2394c4a293e10c2e74d9bc33cf21866a4"
)
EXPECTED_SKIP_FIELD_AUDIT_PATH = (
    "docs/research/nanopb-skip-field-source-candidate-audit.md"
)
EXPECTED_SKIP_FIELD_AUDIT_SIZE = 5382
EXPECTED_SKIP_FIELD_AUDIT_SHA256 = (
    "9358ffec368cf8a9d27947ed554083f08bbe03d6b2c619090f82827fe6b31b86"
)
EXPECTED_SKIP_FIELD_RECORD_SHA256 = (
    "fd8bca683f9595aefb0c75fc10fcfaf8b1a4c1f06e27ee875b398677b85be49b"
)
EXPECTED_SKIP_FIELD_UPSTREAM_START = 9043
EXPECTED_SKIP_FIELD_UPSTREAM_END = 9458
EXPECTED_SKIP_FIELD_UPSTREAM_SHA256 = (
    "4f447e98f77d58030aa39bf1d0e936b01253f828440f362336f96a8d7c679be1"
)
EXPECTED_READ_RAW_SOURCE_PATH = (
    "components/shared/nanopb/runtime_nanopb_read_raw_value.c"
)
EXPECTED_READ_RAW_SOURCE_SIZE = 2762
EXPECTED_READ_RAW_SOURCE_SHA256 = (
    "e8d9e5da342086614ef842849bba068daf72bbca52a24a24293f3ec7ac6e20f5"
)
EXPECTED_READ_RAW_HEADER_PATH = (
    "components/shared/nanopb/runtime_nanopb_read_raw_value.h"
)
EXPECTED_READ_RAW_HEADER_SIZE = 1719
EXPECTED_READ_RAW_HEADER_SHA256 = (
    "59caa890004c376aa08d9eff6fe6525694a05d0cc878484be7a83b51c413aca4"
)
EXPECTED_READ_RAW_AUDIT_PATH = (
    "docs/research/nanopb-raw-substream-boundary-audit.md"
)
EXPECTED_READ_RAW_AUDIT_SIZE = 6345
EXPECTED_READ_RAW_AUDIT_SHA256 = (
    "e962d5bcd0bdaf2f9a75f25372901502b4e0fde04766d850ffddb844c987fd31"
)
EXPECTED_READ_RAW_RECORD_SHA256 = (
    "54aebe0dfcf6b1678638ee2c23f8e0835773829f01ac8de18e5499d62de5724e"
)
EXPECTED_READ_RAW_UPSTREAM_START = 9612
EXPECTED_READ_RAW_UPSTREAM_END = 10656
EXPECTED_READ_RAW_UPSTREAM_SHA256 = (
    "a4c975f632934b80ee707520096f428a670516d4dc7368ac6c9a5959da83ded6"
)
EXPECTED_SUBSTREAM_SOURCE_PATH = (
    "components/shared/nanopb/runtime_nanopb_make_string_substream.c"
)
EXPECTED_SUBSTREAM_SOURCE_SIZE = 2734
EXPECTED_SUBSTREAM_SOURCE_SHA256 = (
    "85f543a33de5b543ac29a5422983eaf7cd06af4e236a2453a3f658020ecba15b"
)
EXPECTED_SUBSTREAM_HEADER_PATH = (
    "components/shared/nanopb/runtime_nanopb_make_string_substream.h"
)
EXPECTED_SUBSTREAM_HEADER_SIZE = 1551
EXPECTED_SUBSTREAM_HEADER_SHA256 = (
    "92e7c1eb37799fd09b4682a0ee45ba496d8c37f08ce7047a7b62bc1a73b8cda7"
)
EXPECTED_SUBSTREAM_RECORD_SHA256 = (
    "d5335ad11e404d4057d7e6ea60c5e0f14feba1c358c7f7ea42d7e376d61d7901"
)
EXPECTED_BOOL_RECORD_SHA256 = (
    "f853425c92c2699a077acbba9703e3298a11a002780620fb12db2aa2206d5d80"
)
EXPECTED_BOOL_FILES = (
    (
        "components/shared/nanopb/runtime_nanopb_decode_bool.c",
        1592,
        "ac020d4746af6c6e68dbf10eb796475f3e39fbc63e253fa4320a265f508ca286",
    ),
    (
        "components/shared/nanopb/runtime_nanopb_decode_bool.h",
        1632,
        "9dfa4eb516bf8394af1d68fdd294ba60d3e7531301a1a2e20fc1474446ae455a",
    ),
    (
        "components/shared/nanopb/runtime_nanopb_dec_bool.c",
        1508,
        "8f2c510bba9eb1fdec823b0855fb17ee08aad39bae6e863369a9877cdb700674",
    ),
    (
        "components/shared/nanopb/runtime_nanopb_dec_bool.h",
        2038,
        "d6867428ea9adfe2552199d9716c72e7fb83db6f116c0c390051c7e82132a34a",
    ),
    (
        "docs/research/nanopb-bool-cluster-source-audit.md",
        6950,
        "31aeeb4298afd3adf5ffbede5516d34dc3b277fbc731c300f28a14fe245d3130",
    ),
)
EXPECTED_DEC_VARINT_RECORD_SHA256 = (
    "ecf86e436171934ee083b7907ed1ba2d847758ec13cf7c365713caf8072d4474"
)
EXPECTED_DEC_VARINT_FILES = (
    (
        "components/shared/nanopb/runtime_nanopb_dec_varint.c",
        4579,
        "e5638a305dde899b62aa7965015eece645cd2e892fa37c31430ee84e02886092",
    ),
    (
        "components/shared/nanopb/runtime_nanopb_dec_varint.h",
        2126,
        "a3454bd8400f38da67f9b4a74dc2bf9c3365f0b1b63b2df8a085c50fcff7154a",
    ),
    (
        "docs/research/nanopb-dec-varint-source-audit.md",
        6035,
        "4665f2eb07438f40937d3c46852c0266cda854ce73056bdd8687f835567c0117",
    ),
)
EXPECTED_DEC_BYTES_RECORD_SHA256 = (
    "49a34c4ebea651de86c2c593e0ffb50c78b4ee5ea57b013a8b54fe19ed7b1ae0"
)
EXPECTED_DEC_BYTES_FILES = (
    (
        "components/shared/nanopb/runtime_nanopb_dec_bytes.c",
        3163,
        "16156212768637a22587c72d3aec916e1b011c4deae4974c7cb73417e3d57ddc",
    ),
    (
        "components/shared/nanopb/runtime_nanopb_dec_bytes.h",
        1801,
        "5b7955c8dfd4606a95ed58319a0a8f860e37bc2642444db648ca8cff638c5910",
    ),
    (
        "docs/research/nanopb-dec-bytes-source-audit.md",
        5651,
        "10663d614f4608f01db281dc61f73e0774218df79d0c143621693d5fcdf3cd55",
    ),
)
EXPECTED_DEC_STRING_RECORD_SHA256 = (
    "6fed6b83205bacefd2f29ec16abfe303d56aff36f4935b32e711385fdfe83811"
)
EXPECTED_DEC_STRING_FILES = (
    (
        "components/shared/nanopb/runtime_nanopb_dec_string.c",
        3110,
        "6b023235be31a1917f1a3466e5b5ad1ed3294f91dc4fb3764f411b5c0278d20c",
    ),
    (
        "components/shared/nanopb/runtime_nanopb_dec_string.h",
        1347,
        "67edc0b05ce695d7e286a4099f5d3b8b793f4c14ded91e8e4fbeb13cf3151661",
    ),
    (
        "docs/research/nanopb-dec-string-source-audit.md",
        5241,
        "a1f4959746491cd090fc9bbe7537c5429557b9d8bbad588122fe0301b13b4b78",
    ),
)
EXPECTED_DEC_SUBMESSAGE_RECORD_SHA256 = (
    "d2a7b0e2671f9111d48f27354ec29464df293b71563eb6a03d9692bb339e2fb5"
)
EXPECTED_DEC_SUBMESSAGE_FILES = (
    ("components/shared/nanopb/runtime_nanopb_dec_submessage.c", 3010,
     "afcc411be858e82fff816b2354cae4698069e1ca3d277022f6ef4d64a00a2d87"),
    ("components/shared/nanopb/runtime_nanopb_dec_submessage.h", 1736,
     "4ab90681e293268fd0ad3798b3e4902fdb942bd59394ea48d374c409b9583234"),
    ("docs/research/nanopb-dec-submessage-source-audit.md", 4113,
     "7c3644bf04f4d89ac0984227d41cb42c2b67962fd045629cc364b19b023083bf"),
)
EXPECTED_DECODE_INNER_RECORD_SHA256 = (
    "5df09327cd306a93122248bf63623abf3156bd3df2f168eb8e10e8e38d8920b8"
)
EXPECTED_DECODE_INNER_FILES = (
    ("components/shared/nanopb/runtime_nanopb_decode_inner.c", 7049,
     "791c5e45b5f3cf53bcb2f7a0bb8f2877dc112bd4c08c0c4603acca2da0d8f1b1"),
    ("components/shared/nanopb/runtime_nanopb_decode_inner.h", 2308,
     "9058eb4bdabefcff3c1e79edbfbf6fe0e2111b2d8f78fcef3599d7a9ff7768d6"),
    ("docs/research/nanopb-decode-inner-source-audit.md", 4107,
     "cc380241ee099906919f73f9bc55d9e8560aa9e70f5077a6a9da439d24824ac3"),
    ("tools/analyze_g2_nanopb_decode_inner.py", 12737,
     "2f1610679f1fc7d551c046b43caab4db92b73bdc3c356c0bc62fcd749f442534"),
)
EXPECTED_DECODE_TAG_RECORD_SHA256 = (
    "2027a362529b8998dde81c5a9036085fa87d57a0dce61a5b4a8a89d0d8b98698"
)
EXPECTED_DECODE_TAG_FILES = (
    ("components/shared/nanopb/runtime_nanopb_decode_tag.c", 1223,
     "4975c11d7435c31fa236063e0b3304b5c425726deb660343fd9304c0ae91b20d"),
    ("components/shared/nanopb/runtime_nanopb_decode_tag.h", 1080,
     "95f5f45c357410df5a0a65ca56139107f86fe13f389b832da7708d743dcb1f3c"),
    ("docs/research/nanopb-decode-tag-source-audit.md", 2575,
     "58661d21beab70bc0fd9d8e7dadcf13e4847fae583550e84145860ca3a5136cd"),
    ("tools/analyze_g2_nanopb_decode_tag.py", 7668,
     "d89e04abf3698c159689e333715c6374328a9d4cf41a3b04aa0eb0034d8be91e"),
)
EXPECTED_ITERATOR_FILES = (
    ("components/shared/nanopb/runtime_nanopb_iterator_cluster.c", 13395,
     "edcff9480ae181a22aba9eb28641257fe62fb9652c1268cd3ef1658e5a3690eb"),
    ("components/shared/nanopb/runtime_nanopb_iterator_cluster.h", 2995,
     "f9664d9eb409a731dbf1a7c664ee91f10b58b3b0f818844eab5f77fbaac8f0b2"),
)
EXPECTED_ITERATOR_RECORD_SHA256 = (
    "d1b5ddf81b549a4751a37d854866f5d08363ed5a3f2ce33923551507a767ec3e"
)
EXPECTED_DEFAULTS_RECORD_SHA256 = (
    "fb5b0ee919aa415be75a78202552f1d9b6328c968a5ad012363ee9e2730466d2"
)
EXPECTED_DEFAULTS_FILES = (
    ("components/shared/nanopb/runtime_nanopb_defaults_pair.c", 6284,
     "76dc1344eb1187f8631e935613246724287c6b1e917efd795dabe17ec5d84491"),
    ("components/shared/nanopb/runtime_nanopb_defaults_pair.h", 867,
     "fd49a5df94ff89c5c0032f72c304f5efd4ec0bf4ecd5908742c6ef0810e51ab9"),
    ("docs/research/nanopb-field-default-source-audit.md", 4891,
     "064e1f8901cffff3b21ca554373ee9bb298a970eb23731cebee2f8a040579707"),
    ("docs/research/nanopb-message-defaults-source-audit.md", 4042,
     "769615938888d4f8cbfa516669aa739ae5e260516cb0189e6f60766dfe64b86c"),
    ("tools/analyze_g2_nanopb_field_default.py", 8233,
     "d80ce526a8de93c36ec3829246c4eeb5fb96a58e6c0be5100528ae9244e3e7cb"),
    ("tools/analyze_g2_nanopb_message_defaults.py", 8382,
     "b2b497057181f108499ad625d4c292fc80856c075363ee90b7b4c5f1031de1ad"),
)
EXPECTED_DISPATCH_RECORD_SHA256 = (
    "0b8d428a72cd0a117507991661e7db74147d101e2276db3a5947e27da1f78ce6"
)
EXPECTED_DISPATCH_FILES = (
    ("components/shared/nanopb/runtime_nanopb_dispatch_extension.c", 3804,
     "b4a6620fdc79fdbb3b3891166d6248176b396cf18b7157cd3d300d66ee15de96"),
    ("components/shared/nanopb/runtime_nanopb_dispatch_extension.h", 1560,
     "f6918d0d89b223e9ad33601de800931a73a0c9ad5ac66177ea83c435441c2ec8"),
    ("docs/research/nanopb-dispatch-extension-source-audit.md", 5498,
     "cba2ab3edb607aa85d57803da2dba92765290fab0bc9a1fba48e2e345746e2f1"),
    ("tools/analyze_g2_nanopb_dispatch_extension.py", 15651,
     "919bdfe79d539ba96543d7f0d51b722a22224fb4c8e0ad3afeae3e6b159652eb"),
)
EXPECTED_FIELD_DECODER_RECORD_SHA256 = (
    "752a172f9b1be9b5aaa73a246b275a240c4e1312043eb7db58ea7083b047ac6a"
)
EXPECTED_FIELD_DECODER_FILES = (
    ("components/shared/nanopb/runtime_nanopb_field_decoder_cluster.c", 14057,
     "6c34245f6d3c305499ffb6be2bae69508fe6c6f4c4b79e8306d3b998f84c9901"),
    ("components/shared/nanopb/runtime_nanopb_field_decoder_cluster.h", 888,
     "812560e152e879f3181bcb20a2b65b0a6c81673aa4bebe46ff3bb6c99de1a8ac"),
    ("tests/fixtures/runtime_nanopb_field_decoder_cluster_host.c", 9211,
     "c3fee7a4ff21332c33629d63fb003c45de8b37cdbb026dc2f8a78ea57d9d2682"),
    ("docs/research/nanopb-field-decoder-cluster-boundary-audit.md", 9099,
     "22ff59f6d848e8460de845e49210aa9bf6305bd88aaeff5b5e194bff34aa8010"),
    ("tools/analyze_g2_nanopb_field_decoder_cluster.py", 18685,
     "99467e10049473efb18e26f025664ec60553bb1ec209289625f21832d29195b6"),
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
                "size": 20, "alignment": 4, "offset": 184744,
                "runtime_address": "0x007C14CC",
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
                "offset": 184764,
                "runtime_address": "0x007C14E0",
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
                "offset": 186496,
                "runtime_address": "0x007C1BA4",
                "unrelocated_sha256": (
                    "3617ea95d4a2cbabf3a1abb375e57232"
                    "3fffcebfa68cb4e19874cb4a831d9662"
                ),
                "relocated_sha256": (
                    "63e4707f5fd537094855d38f6b4df857"
                    "8b77644c131e180db2e682d32fbc1fab"
                ),
                "entry_patch_sha256": (
                    "f8b98a0113ee5658769fd2310f0bc570"
                    "196efffc5a8e4892b671cd4e2d756182"
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


def verify_skip_field_provenance(selection: dict[str, Any]) -> None:
    """Pin the Apple-reviewed leaf and explicit pending Linux boundary."""
    production = selection.get("production_skip_field_leaf")
    require(isinstance(production, dict), "pb_skip_field production record missing")
    require(
        canonical_sha256(production) == EXPECTED_SKIP_FIELD_RECORD_SHA256,
        "pb_skip_field production provenance changed",
    )


def verify_skip_field_source_pins() -> None:
    for path, size, digest, label in (
        (
            EXPECTED_SKIP_FIELD_SOURCE_PATH,
            EXPECTED_SKIP_FIELD_SOURCE_SIZE,
            EXPECTED_SKIP_FIELD_SOURCE_SHA256,
            "source",
        ),
        (
            EXPECTED_SKIP_FIELD_HEADER_PATH,
            EXPECTED_SKIP_FIELD_HEADER_SIZE,
            EXPECTED_SKIP_FIELD_HEADER_SHA256,
            "header",
        ),
        (
            EXPECTED_SKIP_FIELD_AUDIT_PATH,
            EXPECTED_SKIP_FIELD_AUDIT_SIZE,
            EXPECTED_SKIP_FIELD_AUDIT_SHA256,
            "evidence",
        ),
    ):
        data = (ROOT / path).read_bytes()
        require(len(data) == size, f"pb_skip_field {label} size changed")
        require(sha256(data) == digest, f"pb_skip_field {label} hash changed")
    upstream = (HERE / "pb_decode.c").read_bytes()
    signature = b"bool checkreturn pb_skip_field(pb_istream_t *stream, pb_wire_type_t wire_type)\n{"
    require(
        brace_balanced_definition(upstream, signature)
        == (
            EXPECTED_SKIP_FIELD_UPSTREAM_START,
            EXPECTED_SKIP_FIELD_UPSTREAM_END - 1,
        ),
        "upstream pb_skip_field extraction span changed",
    )
    definition = upstream[
        EXPECTED_SKIP_FIELD_UPSTREAM_START:EXPECTED_SKIP_FIELD_UPSTREAM_END
    ]
    require(len(definition) == 415, "upstream pb_skip_field size changed")
    require(
        sha256(definition) == EXPECTED_SKIP_FIELD_UPSTREAM_SHA256,
        "upstream pb_skip_field hash changed",
    )


def verify_read_raw_provenance(selection: dict[str, Any]) -> None:
    """Pin the Apple-reviewed private read_raw_value leaf."""
    production = selection.get("production_read_raw_value_leaf")
    require(isinstance(production, dict), "read_raw_value production record missing")
    require(
        canonical_sha256(production) == EXPECTED_READ_RAW_RECORD_SHA256,
        "read_raw_value production provenance changed",
    )


def verify_read_raw_source_pins() -> None:
    for path, size, digest, label in (
        (
            EXPECTED_READ_RAW_SOURCE_PATH,
            EXPECTED_READ_RAW_SOURCE_SIZE,
            EXPECTED_READ_RAW_SOURCE_SHA256,
            "source",
        ),
        (
            EXPECTED_READ_RAW_HEADER_PATH,
            EXPECTED_READ_RAW_HEADER_SIZE,
            EXPECTED_READ_RAW_HEADER_SHA256,
            "header",
        ),
        (
            EXPECTED_READ_RAW_AUDIT_PATH,
            EXPECTED_READ_RAW_AUDIT_SIZE,
            EXPECTED_READ_RAW_AUDIT_SHA256,
            "evidence",
        ),
    ):
        data = (ROOT / path).read_bytes()
        require(len(data) == size, f"read_raw_value {label} size changed")
        require(sha256(data) == digest, f"read_raw_value {label} hash changed")
    upstream = (HERE / "pb_decode.c").read_bytes()
    signature = (
        b"static bool checkreturn read_raw_value(pb_istream_t *stream, "
        b"pb_wire_type_t wire_type, pb_byte_t *buf, size_t *size)\n{"
    )
    require(
        brace_balanced_definition(upstream, signature)
        == (EXPECTED_READ_RAW_UPSTREAM_START, EXPECTED_READ_RAW_UPSTREAM_END - 1),
        "upstream read_raw_value extraction span changed",
    )
    definition = upstream[
        EXPECTED_READ_RAW_UPSTREAM_START:EXPECTED_READ_RAW_UPSTREAM_END
    ]
    require(len(definition) == 1044, "upstream read_raw_value size changed")
    require(
        sha256(definition) == EXPECTED_READ_RAW_UPSTREAM_SHA256,
        "upstream read_raw_value hash changed",
    )


def verify_bool_cluster_provenance(selection: dict[str, Any]) -> None:
    production = selection.get("production_bool_cluster")
    require(isinstance(production, dict), "Boolean-cluster production record missing")
    require(
        canonical_sha256(production) == EXPECTED_BOOL_RECORD_SHA256,
        "Boolean-cluster production provenance changed",
    )


def verify_bool_cluster_source_pins() -> None:
    for path, size, digest in EXPECTED_BOOL_FILES:
        candidate = ROOT / path
        require(candidate.is_file(), f"Boolean-cluster file is missing: {path}")
        data = candidate.read_bytes()
        require(len(data) == size, f"Boolean-cluster file size changed: {path}")
        require(sha256(data) == digest, f"Boolean-cluster file hash changed: {path}")

    upstream = (HERE / "pb_decode.c").read_bytes()
    definitions = (
        (
            b"bool pb_decode_bool(pb_istream_t *stream, bool *dest)\n{",
            42715, 42910, 42911,
            "5db66c94774daecd96a5daf5d83ff441462e4793a76638ef096f82d1c3a9c38f",
            "public",
        ),
        (
            b"static bool checkreturn pb_dec_bool(pb_istream_t *stream, const pb_field_iter_t *field)\n{",
            44696, 44843, 44844,
            "e3e930719ed531df7d647cdf9ecd002c522c2d4d55e6f8299c258532713f6e6c",
            "adapter",
        ),
    )
    for signature, start, brace_end, slice_end, digest, label in definitions:
        require(
            brace_balanced_definition(upstream, signature) == (start, brace_end),
            f"upstream Boolean {label} extraction span changed",
        )
        require(
            sha256(upstream[start:slice_end]) == digest,
            f"upstream Boolean {label} definition hash changed",
        )


def verify_dec_varint_provenance(selection: dict[str, Any]) -> None:
    production = selection.get("production_dec_varint_leaf")
    require(isinstance(production, dict), "pb_dec_varint production record missing")
    require(
        canonical_sha256(production) == EXPECTED_DEC_VARINT_RECORD_SHA256,
        "pb_dec_varint production provenance changed",
    )


def verify_dec_varint_source_pins() -> None:
    for path, size, digest in EXPECTED_DEC_VARINT_FILES:
        candidate = ROOT / path
        require(candidate.is_file(), f"pb_dec_varint file is missing: {path}")
        data = candidate.read_bytes()
        require(len(data) == size, f"pb_dec_varint file size changed: {path}")
        require(sha256(data) == digest, f"pb_dec_varint file hash changed: {path}")

    upstream = (HERE / "pb_decode.c").read_bytes()
    signature = (
        b"static bool checkreturn pb_dec_varint(pb_istream_t *stream, "
        b"const pb_field_iter_t *field)\n{"
    )
    require(
        brace_balanced_definition(upstream, signature) == (44845, 47569),
        "upstream pb_dec_varint extraction span changed",
    )
    require(
        sha256(upstream[44845:47571])
        == "be9044f37413d5f5ccacf8b94473552824d913037aa23ff853c59bd77c111b93",
        "upstream pb_dec_varint definition hash changed",
    )


def verify_dec_bytes_provenance(selection: dict[str, Any]) -> None:
    production = selection.get("production_dec_bytes_leaf")
    require(isinstance(production, dict), "pb_dec_bytes production record missing")
    require(
        canonical_sha256(production) == EXPECTED_DEC_BYTES_RECORD_SHA256,
        "pb_dec_bytes production provenance changed",
    )


def verify_dec_bytes_source_pins() -> None:
    for path, size, digest in EXPECTED_DEC_BYTES_FILES:
        candidate = ROOT / path
        require(candidate.is_file(), f"pb_dec_bytes file is missing: {path}")
        data = candidate.read_bytes()
        require(len(data) == size, f"pb_dec_bytes file size changed: {path}")
        require(sha256(data) == digest, f"pb_dec_bytes file hash changed: {path}")

    upstream = (HERE / "pb_decode.c").read_bytes()
    signature = (
        b"static bool checkreturn pb_dec_bytes(pb_istream_t *stream, "
        b"const pb_field_iter_t *field)\n{"
    )
    require(
        brace_balanced_definition(upstream, signature) == (47571, 48675),
        "upstream pb_dec_bytes extraction span changed",
    )
    require(
        sha256(upstream[47571:48677])
        == "343c9c20cbd27012513eac9e7950d3c7d03733bb318d608be2f2538c44705374",
        "upstream pb_dec_bytes definition hash changed",
    )


def verify_dec_string_provenance(selection: dict[str, Any]) -> None:
    production = selection.get("production_dec_string_leaf")
    require(isinstance(production, dict), "pb_dec_string production record missing")
    require(
        canonical_sha256(production) == EXPECTED_DEC_STRING_RECORD_SHA256,
        "pb_dec_string production provenance changed",
    )


def verify_dec_string_source_pins() -> None:
    for path, size, digest in EXPECTED_DEC_STRING_FILES:
        candidate = ROOT / path
        require(candidate.is_file(), f"pb_dec_string file is missing: {path}")
        data = candidate.read_bytes()
        require(len(data) == size, f"pb_dec_string file size changed: {path}")
        require(sha256(data) == digest, f"pb_dec_string file hash changed: {path}")

    upstream = (HERE / "pb_decode.c").read_bytes()
    signature = (
        b"static bool checkreturn pb_dec_string(pb_istream_t *stream, "
        b"const pb_field_iter_t *field)\n{"
    )
    require(
        brace_balanced_definition(upstream, signature) == (48677, 49906),
        "upstream pb_dec_string extraction span changed",
    )
    require(
        sha256(upstream[48677:49908])
        == "73375d35f4938cd170ac34eb6f32668fcdf253c9b850955524e3a8e5357f8646",
        "upstream pb_dec_string definition hash changed",
    )


def verify_dec_submessage_provenance(selection: dict[str, Any]) -> None:
    production = selection.get("production_dec_submessage_leaf")
    require(isinstance(production, dict), "pb_dec_submessage production record missing")
    require(canonical_sha256(production) == EXPECTED_DEC_SUBMESSAGE_RECORD_SHA256,
            "pb_dec_submessage production provenance changed")


def verify_dec_submessage_source_pins() -> None:
    for path, size, digest in EXPECTED_DEC_SUBMESSAGE_FILES:
        candidate = ROOT / path
        require(candidate.is_file(), f"pb_dec_submessage file is missing: {path}")
        data = candidate.read_bytes()
        require(len(data) == size, f"pb_dec_submessage file size changed: {path}")
        require(sha256(data) == digest, f"pb_dec_submessage file hash changed: {path}")
    upstream = (HERE / "pb_decode.c").read_bytes()
    signature = (b"static bool checkreturn pb_dec_submessage(pb_istream_t *stream, "
                 b"const pb_field_iter_t *field)\n{")
    require(brace_balanced_definition(upstream, signature) == (49908, 51555),
            "upstream pb_dec_submessage extraction span changed")
    require(sha256(upstream[49908:51557]) ==
            "94000cbd5547153805c6b687cb80650a6f57cf9a030434cbf179cfde94ae3f4e",
            "upstream pb_dec_submessage definition hash changed")


def verify_decode_inner_and_tag_provenance(selection: dict[str, Any]) -> None:
    for key, digest, label in (
        ("production_decode_inner_leaf", EXPECTED_DECODE_INNER_RECORD_SHA256,
         "pb_decode_inner"),
        ("production_decode_tag_leaf", EXPECTED_DECODE_TAG_RECORD_SHA256,
         "pb_decode_tag"),
    ):
        production = selection.get(key)
        require(isinstance(production, dict), f"{label} production record missing")
        require(canonical_sha256(production) == digest,
                f"{label} production provenance changed")


def verify_iterator_provenance(selection: dict[str, Any]) -> None:
    production = selection.get("production_iterator_cluster")
    require(isinstance(production, dict),
            "nanopb iterator production record missing")
    require(canonical_sha256(production) == EXPECTED_ITERATOR_RECORD_SHA256,
            "nanopb iterator production provenance changed")


def verify_defaults_provenance(selection: dict[str, Any]) -> None:
    production = selection.get("production_defaults_pair")
    require(isinstance(production, dict),
            "nanopb defaults-pair production record missing")
    require(canonical_sha256(production) == EXPECTED_DEFAULTS_RECORD_SHA256,
            "nanopb defaults-pair production provenance changed")


def verify_dispatch_provenance(selection: dict[str, Any]) -> None:
    production = selection.get("production_dispatch_extension")
    require(isinstance(production, dict),
            "nanopb dispatch/extension production record missing")
    require(canonical_sha256(production) == EXPECTED_DISPATCH_RECORD_SHA256,
            "nanopb dispatch/extension production provenance changed")


def verify_field_decoder_provenance(selection: dict[str, Any]) -> None:
    production = selection.get("production_field_decoder_cluster")
    require(isinstance(production, dict),
            "nanopb field-decoder production record missing")
    require(canonical_sha256(production) == EXPECTED_FIELD_DECODER_RECORD_SHA256,
            "nanopb field-decoder production provenance changed")


def verify_dispatch_source_pins() -> None:
    for path, size, digest in EXPECTED_DISPATCH_FILES:
        data = (ROOT / path).read_bytes()
        require(len(data) == size and sha256(data) == digest,
                f"nanopb dispatch/extension file pin changed: {path}")
    upstream = (HERE / "pb_decode.c").read_bytes()
    for start, end, digest, label in (
        (26221, 27053, "1c6111be8313e278c2b1753401a701245c1baa7c90acd085f18c1eb277d7e42d", "decode_field"),
        (27227, 27659, "175e06435cc0c7e7f0bf3d44aa6b2d3e0f5f9bc8384ce52d28c80bf21777a691", "default_extension_decoder"),
        (27810, 28413, "3229a97ca148e192ca3b1d0fd33df3a1654b6405bd247e0b6f6320041460f7da", "decode_extension"),
    ):
        require(sha256(upstream[start:end]) == digest,
                f"upstream {label} definition changed")


def verify_field_decoder_source_pins() -> None:
    for path, size, digest in EXPECTED_FIELD_DECODER_FILES:
        data = (ROOT / path).read_bytes()
        require(len(data) == size and sha256(data) == digest,
                f"nanopb field-decoder file pin changed: {path}")
    upstream = (HERE / "pb_decode.c").read_bytes()
    for start, end, digest, label in (
        (11653, 13922, "c4465869ffee60864637b4710e393a7bb5c60c00a847e6f28137f4b480c5af71", "decode_basic_field"),
        (13922, 17541, "64eb9ced4f650be17dbb7db6fa58f45ccdb9036460ae6d7aa355c3cfb8bcb24e", "decode_static_field"),
        (19783, 24704, "06f716c1f96bb2c77c5651b26a9ec5e465958258395e687c1d87dfbd01d70477", "decode_pointer_field"),
        (24704, 26221, "45c67a796415dd023421f9108696478250e175837956c48fe8f960e3535afa24", "decode_callback_field"),
        (51557, 52223, "3ede65e67d2d4dd729e53b5ef5a55d109e7479368ada22bf87760b072563e6ce", "pb_dec_fixed_length_bytes"),
    ):
        require(sha256(upstream[start:end]) == digest,
                f"upstream {label} definition changed")


def verify_defaults_source_pins() -> None:
    for path, size, digest in EXPECTED_DEFAULTS_FILES:
        data = (ROOT / path).read_bytes()
        require(len(data) == size and sha256(data) == digest,
                f"nanopb defaults-pair file pin changed: {path}")
    upstream = (HERE / "pb_decode.c").read_bytes()
    require(sha256(upstream[28476:31080]) ==
            "dced6e406d8c2c657a90cd599a60457a83bbc123b6ddfbfb9bff71778a773265",
            "upstream pb_field_set_to_default definition changed")
    require(sha256(upstream[31080:32048]) ==
            "b907b8141e8f0376e9d5e86bf58efde7465d2a16ca3d30ece27ffda16d3afe9e",
            "upstream pb_message_set_to_defaults definition changed")


def verify_decode_inner_and_tag_source_pins() -> None:
    for label, files in (
        ("pb_decode_inner", EXPECTED_DECODE_INNER_FILES),
        ("pb_decode_tag", EXPECTED_DECODE_TAG_FILES),
    ):
        for path, size, digest in files:
            candidate = ROOT / path
            require(candidate.is_file(), f"{label} file is missing: {path}")
            data = candidate.read_bytes()
            require(len(data) == size, f"{label} file size changed: {path}")
            require(sha256(data) == digest, f"{label} file hash changed: {path}")
    upstream = (HERE / "pb_decode.c").read_bytes()
    require(sha256(upstream[32121:37346]) ==
            "01b0015f6b8450e27d38a5f60e57708d9007d005d9ece2ef3fdb287b27ed23f4",
            "upstream pb_decode_inner definition hash changed")
    require(sha256(upstream[8663:9043]) ==
            "6cb0e89f976070f9d561474343e0ef46414107bbf64cbb17302be46dba412cfb",
            "upstream pb_decode_tag definition hash changed")


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
        selection["g2_compatible_pristine_release_range"] == [
            "0.4.7", "0.4.8", "0.4.9", "0.4.9.1"
        ],
        "G2-compatible release range changed",
    )
    require(selection["selected_file_count"] == 8, "selected file count changed")
    require(selection["source_records_sha256"] == EXPECTED_RECORDS_SHA256, "stored source-record digest changed")
    require(
        selection["integration_status"]
        == (
            "authenticated and verified offline; forty-three bounded altered "
            "production functions registered, including the nine-leaf pb_common "
            "iterator closure, the paired private defaults routines, the field/"
            "extension dispatch trio, the five-function field-decoder closure, "
            "pb_decode_tag with its recovered one-byte "
            "wire-type ABI, and private pb_decode_inner"
        ),
        "snapshot production boundary changed",
    )
    verify_istream_provenance(selection)
    verify_svarint_provenance(selection)
    verify_varint32_provenance(selection)
    verify_skip_string_provenance(selection)
    verify_skip_field_provenance(selection)
    verify_read_raw_provenance(selection)
    verify_bool_cluster_provenance(selection)
    verify_dec_varint_provenance(selection)
    verify_dec_bytes_provenance(selection)
    verify_dec_string_provenance(selection)
    verify_dec_submessage_provenance(selection)
    verify_decode_inner_and_tag_provenance(selection)
    verify_iterator_provenance(selection)
    verify_defaults_provenance(selection)
    verify_dispatch_provenance(selection)
    verify_field_decoder_provenance(selection)
    require(
        canonical_sha256(selection["production_make_string_substream_leaf"])
        == EXPECTED_SUBSTREAM_RECORD_SHA256,
        "pb_make_string_substream production provenance changed",
    )
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
    """Return whether a path is generated output or an evidence-only record.

    Recorded overlay configurations deliberately retain production tokens so
    compiler-profile experiments can be replayed.  Their ``*-record*.json``
    names are not canonical build inputs and must not be mistaken for a second
    production overlay; canonical admission remains fail-closed on
    ``components/apollo_main/core_overlay/overlay.json`` below.
    """
    relative = path.relative_to(root)
    return any(
        part == "build" or part.startswith("build-")
        for part in relative.parts
    ) or (
        path.suffix.lower() == ".json"
        and path.name.startswith("overlay-")
        and "record" in path.stem.split("-")
    )


def verify_production_exclusion() -> None:
    """Reject broad snapshot linkage; permit nineteen pinned altered functions."""
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
    }
    production = [
        item
        for item in overlay.get("relocated_leaves", [])
        if item.get("function") in expected_functions
        or allowed_upstream_url in json.dumps(item)
    ]
    require(len(production) == 43, "nanopb production leaf set is not exact")
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
    skip_field_leaf = leaves["open_cfw_nanopb_skip_field"]
    read_raw_leaf = leaves["open_cfw_nanopb_read_raw_value"]
    substream_leaf = leaves["open_cfw_nanopb_make_string_substream"]
    bool_leaf = leaves["open_cfw_nanopb_decode_bool"]
    dec_bool_leaf = leaves["open_cfw_nanopb_dec_bool"]
    dec_varint_leaf = leaves["open_cfw_nanopb_dec_varint"]
    dec_bytes_leaf = leaves["open_cfw_nanopb_dec_bytes"]
    dec_string_leaf = leaves["open_cfw_nanopb_dec_string"]
    dec_submessage_leaf = leaves["open_cfw_nanopb_dec_submessage"]
    decode_inner_leaf = leaves["open_cfw_nanopb_decode_inner"]
    decode_tag_leaf = leaves["open_cfw_nanopb_decode_tag"]
    message_defaults_leaf = leaves["open_cfw_nanopb_message_set_to_defaults"]
    field_default_leaf = leaves["open_cfw_nanopb_field_set_to_default"]
    decode_field_leaf = leaves["open_cfw_nanopb_decode_field"]
    default_extension_leaf = leaves["open_cfw_nanopb_default_extension_decoder"]
    decode_extension_leaf = leaves["open_cfw_nanopb_decode_extension"]
    iterator_functions = (
        "open_cfw_nanopb_load_descriptor_values",
        "open_cfw_nanopb_field_iter_begin",
        "open_cfw_nanopb_field_iter_begin_extension",
        "open_cfw_nanopb_field_iter_next",
        "open_cfw_nanopb_field_iter_find",
        "open_cfw_nanopb_field_iter_find_extension",
        "open_cfw_nanopb_field_iter_begin_const",
        "open_cfw_nanopb_field_iter_begin_extension_const",
        "open_cfw_nanopb_default_field_callback",
    )
    iterator_leaves = {name: leaves[name] for name in iterator_functions}
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
            "sha256": "d17af55fb1fdaa83d98bada51e8a7c5369ee78bd9eaa83d313dd43841ab4edc7",
            "alignment": 4,
            "offset": 184148,
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
            "offset": 185072,
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
        skip_string_leaf.get("toolchain_profiles", {}).get("linux-clang")
        == {
                "reviewed_version_prefix": "Homebrew clang version 22.1.8",
                "expected": {
                    "size": 34,
                    "sha256": "3b1a0dbe465d562770e02d5afe04357087a6bfee22342a0f6844986a0161f547",
                    "alignment": 4,
                    "offset": 186800,
                    "unrelocated_sha256": "d3216f569354900680dae5d78350af7668be4d8fbdae64a47afc4f440b0df920",
                },
                "relocations": [skip_string_call_decode, skip_string_call_read],
        },
        "pb_skip_string Linux configuration contract changed",
    )

    skip_field_relocations = [
        {"offset": 14, "type": "R_ARM_THM_JUMP24", "symbol": "open_cfw_nanopb_read", "symbol_type": "STT_NOTYPE", "target_function": "open_cfw_nanopb_read"},
        {"offset": 30, "type": "R_ARM_THM_JUMP24", "symbol": "open_cfw_nanopb_read", "symbol_type": "STT_NOTYPE", "target_function": "open_cfw_nanopb_read"},
        {"offset": 42, "type": "R_ARM_THM_JUMP24", "symbol": "open_cfw_nanopb_skip_varint", "symbol_type": "STT_NOTYPE", "target_function": "open_cfw_nanopb_skip_varint"},
        {"offset": 46, "type": "R_ARM_THM_JUMP24", "symbol": "open_cfw_nanopb_skip_string", "symbol_type": "STT_NOTYPE", "target_function": "open_cfw_nanopb_skip_string"},
        {"offset": 50, "type": "R_ARM_THM_MOVW_PREL_NC", "symbol": "open_cfw_nanopb_invalid_wire_type_error"},
        {"offset": 54, "type": "R_ARM_THM_MOVT_PREL", "symbol": "open_cfw_nanopb_invalid_wire_type_error"},
    ]
    require(
        set(skip_field_leaf)
        == {"function", "source", "toolchain", "closure", "strict_relocation_contract", "expected", "relocations", "toolchain_profiles"},
        "pb_skip_field production leaf schema changed",
    )
    require(
        skip_field_leaf.get("source")
        == {
            "path": EXPECTED_SKIP_FIELD_SOURCE_PATH,
            "size": EXPECTED_SKIP_FIELD_SOURCE_SIZE,
            "sha256": EXPECTED_SKIP_FIELD_SOURCE_SHA256,
            "license": "Zlib",
            "origin": "altered production adaptation of authenticated nanopb 0.4.9 pb_skip_field",
            "upstream": allowed_upstream_url,
            "upstream_commit": EXPECTED_COMMIT,
            "evidence": EXPECTED_SKIP_FIELD_AUDIT_PATH,
        },
        "pb_skip_field production source registration changed",
    )
    require(
        skip_field_leaf.get("closure")
        == {
            "text_section": ".text.open_cfw_nanopb_skip_field",
            "rodata": {
                "section": ".rodata.open_cfw_nanopb_invalid_wire_type_error",
                "size": 18,
                "sha256": "6e35ebc2e585a3ca08ee2d60871a7d16749421ae2b6c1a33bb20c50175e1048a",
                "alignment": 1,
                "symbols": [{"name": "open_cfw_nanopb_invalid_wire_type_error", "offset": 0, "size": 18}],
            },
        },
        "pb_skip_field source closure changed",
    )
    require(
        skip_field_leaf.get("strict_relocation_contract") is True
        and skip_field_leaf.get("expected")
        == {
            "size": 66,
            "sha256": "31037e87e7a667852271b7fa3be6543232376b1ee6e10443517d75f1dc4126ca",
            "alignment": 4,
            "offset": 185108,
            "unrelocated_sha256": "893a37e8366996cbea7d54f63bcc81700e7feab62c4414d01b1f818aa9b77dd4",
            "closure_size": 84,
            "closure_sha256": "72fad2dba75d1fbbc06b3c0e3d250579b5116a1cb793b7886ff5c62b49f3004e",
            "rodata_offset": 66,
        }
        and skip_field_leaf.get("relocations") == skip_field_relocations,
        "pb_skip_field Apple placement or relocation contract changed",
    )

    read_raw_relocations = [
        {"offset": 44, "type": "R_ARM_THM_CALL", "symbol": "open_cfw_nanopb_read", "symbol_type": "STT_NOTYPE", "target_function": "open_cfw_nanopb_read"},
        {"offset": 90, "type": "R_ARM_THM_JUMP24", "symbol": "open_cfw_nanopb_read", "symbol_type": "STT_NOTYPE", "target_function": "open_cfw_nanopb_read"},
        {"offset": 98, "type": "R_ARM_THM_MOVW_PREL_NC", "symbol": "open_cfw_nanopb_raw_errors"},
        {"offset": 102, "type": "R_ARM_THM_MOVT_PREL", "symbol": "open_cfw_nanopb_raw_errors"},
        {"offset": 116, "type": "R_ARM_THM_MOVW_PREL_NC", "symbol": "open_cfw_nanopb_raw_errors"},
        {"offset": 120, "type": "R_ARM_THM_MOVT_PREL", "symbol": "open_cfw_nanopb_raw_errors"},
    ]
    require(
        set(read_raw_leaf)
        == {"function", "source", "toolchain", "closure", "strict_relocation_contract", "expected", "relocations", "toolchain_profiles"},
        "read_raw_value production leaf schema changed",
    )
    require(
        read_raw_leaf.get("source")
        == {
            "path": EXPECTED_READ_RAW_SOURCE_PATH,
            "size": EXPECTED_READ_RAW_SOURCE_SIZE,
            "sha256": EXPECTED_READ_RAW_SOURCE_SHA256,
            "license": "Zlib",
            "origin": "altered production adaptation of authenticated nanopb 0.4.9 private read_raw_value",
            "upstream": allowed_upstream_url,
            "upstream_commit": EXPECTED_COMMIT,
            "evidence": EXPECTED_READ_RAW_AUDIT_PATH,
        },
        "read_raw_value production source registration changed",
    )
    require(
        read_raw_leaf.get("closure")
        == {
            "text_section": ".text.open_cfw_nanopb_read_raw_value",
            "rodata": {
                "section": ".rodata.open_cfw_nanopb_raw_errors",
                "size": 34,
                "sha256": "00cc371a291caa8db335b89568275a82eda4075b086c285c8fafb674f6cb09f7",
                "alignment": 1,
                "symbols": [{"name": "open_cfw_nanopb_raw_errors", "offset": 0, "size": 34}],
            },
        },
        "read_raw_value source closure changed",
    )
    require(
        read_raw_leaf.get("strict_relocation_contract") is True
        and read_raw_leaf.get("expected")
        == {
            "size": 134,
            "sha256": "9bb42749b65a0adeefd2fa4136a441cd638a9120d1d8c94715ccf79302d8bba8",
            "alignment": 4,
            "offset": 185192,
            "unrelocated_sha256": "6c851acf04b751f90e485e687dc606e02c0bdde0a9dbc8729a915b3937599356",
            "closure_size": 168,
            "closure_sha256": "cffa185a70f039bc04ae9e095e8a40b1b95f14df0c1525a7091e411c8ec230e4",
            "rodata_offset": 134,
        }
        and read_raw_leaf.get("relocations") == read_raw_relocations,
        "read_raw_value Apple placement or relocation contract changed",
    )
    require(
        substream_leaf.get("source", {}).get("path") == EXPECTED_SUBSTREAM_SOURCE_PATH
        and substream_leaf.get("source", {}).get("size") == EXPECTED_SUBSTREAM_SOURCE_SIZE
        and substream_leaf.get("source", {}).get("sha256") == EXPECTED_SUBSTREAM_SOURCE_SHA256
        and substream_leaf.get("expected")
        == {
            "size": 72,
            "sha256": "ee2437609fdbd2cde3b07e1bd5534c5b44feb06ba27a27318ef814568162dc01",
            "alignment": 4,
            "offset": 185360,
            "unrelocated_sha256": "edbbae60795141997eaee9a0050783071d26c61c845dff5a222e013cd7b62825",
            "closure_size": 96,
            "closure_sha256": "b04439cdc14874d78b48ed35be5797455cb3be7c3fb2b811adf3397e06256202",
            "rodata_offset": 72,
        }
        and not any("memcpy" in item.get("symbol", "") for item in substream_leaf.get("relocations", [])),
        "pb_make_string_substream production closure changed",
    )
    for path, size, digest in (
        (EXPECTED_SUBSTREAM_SOURCE_PATH, EXPECTED_SUBSTREAM_SOURCE_SIZE, EXPECTED_SUBSTREAM_SOURCE_SHA256),
        (EXPECTED_SUBSTREAM_HEADER_PATH, EXPECTED_SUBSTREAM_HEADER_SIZE, EXPECTED_SUBSTREAM_HEADER_SHA256),
    ):
        data = (ROOT / path).read_bytes()
        require(len(data) == size and sha256(data) == digest, f"pb_make_string_substream source pin changed: {path}")

    bool_expected = {
        "size": 28,
        "sha256": "740079cb6d09fc781988afdffaef731dcc7b3f077270cc6838d640f3bd442dfb",
        "alignment": 4,
        "offset": 185456,
        "unrelocated_sha256": "78ba0cb5e4d04780ccf342901f5b391cb7e83c1ddaea2f4c16568b2046c55565",
    }
    dec_bool_expected = {
        "size": 6,
        "sha256": "f167416fe762edc4e2f78fa03d83a26df55774635ae39a3e641596a15af26d64",
        "alignment": 4,
        "offset": 185484,
        "unrelocated_sha256": "9b19b7f735da3d5d0e070ed5728ee0ece919d6a6a40891554cb611112067b452",
    }
    require(
        bool_leaf.get("source", {}).get("path") == EXPECTED_BOOL_FILES[0][0]
        and bool_leaf.get("source", {}).get("size") == EXPECTED_BOOL_FILES[0][1]
        and bool_leaf.get("source", {}).get("sha256") == EXPECTED_BOOL_FILES[0][2]
        and bool_leaf.get("strict_relocation_contract") is True
        and bool_leaf.get("expected") == bool_expected
        and bool_leaf.get("relocations")
        == [{
            "offset": 8,
            "type": "R_ARM_THM_CALL",
            "symbol": "open_cfw_nanopb_decode_varint32",
            "symbol_type": "STT_NOTYPE",
            "target_function": "open_cfw_nanopb_decode_varint32",
        }],
        "pb_decode_bool production closure changed",
    )
    require(
        dec_bool_leaf.get("source", {}).get("path") == EXPECTED_BOOL_FILES[2][0]
        and dec_bool_leaf.get("source", {}).get("size") == EXPECTED_BOOL_FILES[2][1]
        and dec_bool_leaf.get("source", {}).get("sha256") == EXPECTED_BOOL_FILES[2][2]
        and dec_bool_leaf.get("strict_relocation_contract") is True
        and dec_bool_leaf.get("expected") == dec_bool_expected
        and dec_bool_leaf.get("relocations")
        == [{
            "offset": 2,
            "type": "R_ARM_THM_JUMP24",
            "symbol": "open_cfw_nanopb_decode_bool",
            "symbol_type": "STT_NOTYPE",
            "target_function": "open_cfw_nanopb_decode_bool",
        }],
        "private pb_dec_bool production closure changed",
    )
    dec_varint_expected = {
        "size": 304,
        "sha256": "b1e508ee7571c033c7beb95301e6323e226b5865e7c9a9c45fd11a2c7c590125",
        "alignment": 4,
        "offset": 185492,
        "unrelocated_sha256": "87d285297c00b55c45b2ec5705495c772f80f1331ab54667fb7d9f4b3196efad",
        "closure_size": 340,
        "closure_sha256": "b015c63f85d575a9d181d2c8c51b5387c86b8759ec6b29e81f48824b2b1dfaca",
        "rodata_offset": 304,
    }
    dec_varint_relocations = [
        {"offset": 22, "type": "R_ARM_THM_CALL", "symbol": "open_cfw_nanopb_decode_varint", "symbol_type": "STT_NOTYPE", "target_function": "open_cfw_nanopb_decode_varint"},
        {"offset": 68, "type": "R_ARM_THM_CALL", "symbol": "open_cfw_nanopb_decode_svarint", "symbol_type": "STT_NOTYPE", "target_function": "open_cfw_nanopb_decode_svarint"},
        {"offset": 108, "type": "R_ARM_THM_CALL", "symbol": "open_cfw_nanopb_decode_varint", "symbol_type": "STT_NOTYPE", "target_function": "open_cfw_nanopb_decode_varint"},
        {"offset": 182, "type": "R_ARM_THM_MOVW_PREL_NC", "symbol": "open_cfw_nanopb_dec_varint_errors"},
        {"offset": 186, "type": "R_ARM_THM_MOVT_PREL", "symbol": "open_cfw_nanopb_dec_varint_errors"},
        {"offset": 226, "type": "R_ARM_THM_MOVW_PREL_NC", "symbol": "open_cfw_nanopb_dec_varint_errors"},
        {"offset": 230, "type": "R_ARM_THM_MOVT_PREL", "symbol": "open_cfw_nanopb_dec_varint_errors"},
        {"offset": 284, "type": "R_ARM_THM_MOVW_PREL_NC", "symbol": "open_cfw_nanopb_dec_varint_errors"},
        {"offset": 288, "type": "R_ARM_THM_MOVT_PREL", "symbol": "open_cfw_nanopb_dec_varint_errors"},
    ]
    require(
        dec_varint_leaf.get("source", {}).get("path") == EXPECTED_DEC_VARINT_FILES[0][0]
        and dec_varint_leaf.get("source", {}).get("size") == EXPECTED_DEC_VARINT_FILES[0][1]
        and dec_varint_leaf.get("source", {}).get("sha256") == EXPECTED_DEC_VARINT_FILES[0][2]
        and dec_varint_leaf.get("strict_relocation_contract") is True
        and dec_varint_leaf.get("expected") == dec_varint_expected
        and dec_varint_leaf.get("closure", {}).get("rodata", {}).get("sha256")
        == "42b784209d1e9ff26348f821c401beb47dfdda57c3a399c0c28b002f52540f0f"
        and dec_varint_leaf.get("relocations") == dec_varint_relocations,
        "private pb_dec_varint production closure changed",
    )
    dec_bytes_expected = {
        "size": 98,
        "sha256": "5ea32d890eb894b11cc01c95edddef23f6e8f7560a44f77878f8884f8ec11f70",
        "alignment": 4,
        "offset": 185832,
        "unrelocated_sha256": "015e10515e87a2993c78839e9152a5d1bdc4cc864a7d5b6f4a12945595168506",
        "closure_size": 146,
        "closure_sha256": "8e35a40f624a8356e7b158fb442afdeb76eba54fe663a5b812cd7dd3cdb368d5",
        "rodata_offset": 98,
    }
    dec_bytes_relocations = [
        {"offset": 10, "type": "R_ARM_THM_CALL", "symbol": "open_cfw_nanopb_decode_varint32", "symbol_type": "STT_NOTYPE", "target_function": "open_cfw_nanopb_decode_varint32"},
        {"offset": 28, "type": "R_ARM_THM_MOVW_PREL_NC", "symbol": "open_cfw_nanopb_dec_bytes_errors"},
        {"offset": 32, "type": "R_ARM_THM_MOVT_PREL", "symbol": "open_cfw_nanopb_dec_bytes_errors"},
        {"offset": 54, "type": "R_ARM_THM_MOVW_PREL_NC", "symbol": "open_cfw_nanopb_dec_bytes_errors"},
        {"offset": 58, "type": "R_ARM_THM_MOVT_PREL", "symbol": "open_cfw_nanopb_dec_bytes_errors"},
        {"offset": 90, "type": "R_ARM_THM_CALL", "symbol": "open_cfw_nanopb_read", "symbol_type": "STT_NOTYPE", "target_function": "open_cfw_nanopb_read"},
    ]
    require(
        dec_bytes_leaf.get("source", {}).get("path") == EXPECTED_DEC_BYTES_FILES[0][0]
        and dec_bytes_leaf.get("source", {}).get("size") == EXPECTED_DEC_BYTES_FILES[0][1]
        and dec_bytes_leaf.get("source", {}).get("sha256") == EXPECTED_DEC_BYTES_FILES[0][2]
        and dec_bytes_leaf.get("strict_relocation_contract") is True
        and dec_bytes_leaf.get("expected") == dec_bytes_expected
        and dec_bytes_leaf.get("closure", {}).get("rodata", {}).get("sha256")
        == "718eead5f51032fc1fbec902f9720d51167ad6c95bca4d7314a30e8226a5f255"
        and dec_bytes_leaf.get("relocations") == dec_bytes_relocations,
        "private pb_dec_bytes production closure changed",
    )
    dec_string_expected = {
        "size": 114,
        "sha256": "7fd11bd5b7f323722739a9f0a19ccba696e5b04659b2d917ec8bd69ae96161c4",
        "alignment": 4,
        "offset": 185980,
        "unrelocated_sha256": "8bb5ae7a48ad06f4f7d8748ca7b39c1274ac997d3eca59a8cb2e08ca5a40af58",
        "closure_size": 163,
        "closure_sha256": "c0be9fa4a77f3390c9e37325512cb946fe2e673224c0b7d05c3558111926b5cf",
        "rodata_offset": 114,
    }
    dec_string_relocations = [
        {"offset": 12, "type": "R_ARM_THM_CALL", "symbol": "open_cfw_nanopb_decode_varint32", "symbol_type": "STT_NOTYPE", "target_function": "open_cfw_nanopb_decode_varint32"},
        {"offset": 38, "type": "R_ARM_THM_MOVW_PREL_NC", "symbol": "open_cfw_nanopb_dec_string_errors"},
        {"offset": 42, "type": "R_ARM_THM_MOVT_PREL", "symbol": "open_cfw_nanopb_dec_string_errors"},
        {"offset": 56, "type": "R_ARM_THM_MOVW_PREL_NC", "symbol": "open_cfw_nanopb_dec_string_errors"},
        {"offset": 60, "type": "R_ARM_THM_MOVT_PREL", "symbol": "open_cfw_nanopb_dec_string_errors"},
        {"offset": 82, "type": "R_ARM_THM_CALL", "symbol": "open_cfw_nanopb_read", "symbol_type": "STT_NOTYPE", "target_function": "open_cfw_nanopb_read"},
        {"offset": 94, "type": "R_ARM_THM_MOVW_PREL_NC", "symbol": "open_cfw_nanopb_dec_string_errors"},
        {"offset": 98, "type": "R_ARM_THM_MOVT_PREL", "symbol": "open_cfw_nanopb_dec_string_errors"},
    ]
    require(
        dec_string_leaf.get("source", {}).get("path") == EXPECTED_DEC_STRING_FILES[0][0]
        and dec_string_leaf.get("source", {}).get("size") == EXPECTED_DEC_STRING_FILES[0][1]
        and dec_string_leaf.get("source", {}).get("sha256") == EXPECTED_DEC_STRING_FILES[0][2]
        and dec_string_leaf.get("strict_relocation_contract") is True
        and dec_string_leaf.get("expected") == dec_string_expected
        and dec_string_leaf.get("closure", {}).get("rodata", {}).get("sha256")
        == "997f0ec78270c8595ea07bc75acc9467b3adb246d10a6ad02da619d1d4686161"
        and dec_string_leaf.get("relocations") == dec_string_relocations,
        "private pb_dec_string production closure changed",
    )
    dec_submessage_expected = {
        "size": 138,
        "sha256": "5630f2edfbe9b51e86a1a8f7c52fe0098ec7140da55a3fdfe7bd92388678ebaa",
        "alignment": 4,
        "offset": 186144,
        "unrelocated_sha256": "ae1d41d5b11734d754d8511f0e782434d757d4fa097b0431ef46c64e1344018c",
        "closure_size": 163,
        "closure_sha256": "78f5a8f12cb6736ae37adedd4efde8d74e72a4aab4eb8f44d3861903a22f1c67",
        "rodata_offset": 138,
    }
    dec_submessage_relocations = [
        {"offset": 10, "type": "R_ARM_THM_CALL", "symbol": "open_cfw_nanopb_make_string_substream", "symbol_type": "STT_NOTYPE", "target_function": "open_cfw_nanopb_make_string_substream"},
        {"offset": 96, "type": "R_ARM_THM_CALL", "symbol": "open_cfw_nanopb_decode_inner", "symbol_type": "STT_NOTYPE", "target_address": 0x0048FE98},
        {"offset": 106, "type": "R_ARM_THM_CALL", "symbol": "open_cfw_nanopb_close_string_substream", "symbol_type": "STT_NOTYPE", "target_function": "open_cfw_nanopb_close_string_substream"},
        {"offset": 120, "type": "R_ARM_THM_MOVW_PREL_NC", "symbol": "open_cfw_nanopb_dec_submessage_error"},
        {"offset": 124, "type": "R_ARM_THM_MOVT_PREL", "symbol": "open_cfw_nanopb_dec_submessage_error"},
    ]
    require(
        dec_submessage_leaf.get("source", {}).get("path") == EXPECTED_DEC_SUBMESSAGE_FILES[0][0]
        and dec_submessage_leaf.get("source", {}).get("size") == EXPECTED_DEC_SUBMESSAGE_FILES[0][1]
        and dec_submessage_leaf.get("source", {}).get("sha256") == EXPECTED_DEC_SUBMESSAGE_FILES[0][2]
        and dec_submessage_leaf.get("strict_relocation_contract") is True
        and dec_submessage_leaf.get("expected") == dec_submessage_expected
        and dec_submessage_leaf.get("closure", {}).get("rodata", {}).get("sha256")
        == "4a8ee02adbdcb9935acc0b5869b671767c30b19fb114043d2327edb45d3085fc"
        and dec_submessage_leaf.get("relocations") == dec_submessage_relocations,
        "private pb_dec_submessage production closure changed",
    )
    decode_inner_expected = {
        "size": 530,
        "sha256": "4723c6aa8bfcc5ab0c41b5b629263f81e445d8eec2549549ceb419f924c23186",
        "alignment": 4,
        "offset": 186308,
        "unrelocated_sha256": "94760bea8227002de63284f309e2dce73a798932a5dab28e97650cf2695d3035",
        "closure_size": 618,
        "closure_sha256": "d73449dc3c9ee8c97f9f24922ddb2425c7554600b28cf63b1171c3ff4acf5d73",
        "rodata_offset": 530,
    }
    require(
        decode_inner_leaf.get("source", {}).get("path") == EXPECTED_DECODE_INNER_FILES[0][0]
        and decode_inner_leaf.get("source", {}).get("size") == EXPECTED_DECODE_INNER_FILES[0][1]
        and decode_inner_leaf.get("source", {}).get("sha256") == EXPECTED_DECODE_INNER_FILES[0][2]
        and decode_inner_leaf.get("strict_relocation_contract") is True
        and decode_inner_leaf.get("expected") == decode_inner_expected
        and decode_inner_leaf.get("closure", {}).get("rodata", {}).get("sha256")
        == "993d8d66d07a300c6c9d5492209c05f66129ed68b6a0cb109782cb8f79581025"
        and decode_inner_leaf.get("relocations", [])[2].get("symbol")
        == "open_cfw_nanopb_decode_tag"
        and decode_inner_leaf.get("relocations", [])[5].get("target_address")
        == 0x007B39CC
        and decode_inner_leaf.get("relocations", [])[6].get("target_address")
        == 0x007B3A70
        and decode_inner_leaf.get("relocations", [])[7].get("target_function")
        == "open_cfw_nanopb_skip_field",
        "private pb_decode_inner production closure changed",
    )
    require(
        decode_tag_leaf.get("source", {}).get("path") == EXPECTED_DECODE_TAG_FILES[0][0]
        and decode_tag_leaf.get("source", {}).get("size") == EXPECTED_DECODE_TAG_FILES[0][1]
        and decode_tag_leaf.get("source", {}).get("sha256") == EXPECTED_DECODE_TAG_FILES[0][2]
        and decode_tag_leaf.get("strict_relocation_contract") is True
        and decode_tag_leaf.get("expected") == {
            "size": 42,
            "sha256": "f36301a6c133d6fcb0842f674a4c794a100d708843997b01ce57180b387ebaab",
            "alignment": 4,
            "offset": 186928,
            "unrelocated_sha256": "1c1c3627e3f4e4e31029f32513dfe2a10e09a15c8c49f6e3cd5946a50ea753bc",
        }
        and decode_tag_leaf.get("relocations") == [{
            "offset": 20,
            "type": "R_ARM_THM_CALL",
            "symbol": "open_cfw_nanopb_decode_varint32_eof",
            "symbol_type": "STT_NOTYPE",
            "target_function": "open_cfw_nanopb_decode_varint32_eof",
        }],
        "pb_decode_tag production closure changed",
    )

    iterator_source = {
        "path": "components/shared/nanopb/runtime_nanopb_iterator_cluster.c",
        "size": 13395,
        "sha256": "edcff9480ae181a22aba9eb28641257fe62fb9652c1268cd3ef1658e5a3690eb",
        "license": "Zlib",
        "origin": "altered production adaptation of authenticated nanopb 0.4.9 compact descriptor iterator cluster",
        "upstream": (
            "https://github.com/nanopb/nanopb/blob/"
            f"{EXPECTED_COMMIT}/pb_common.c"
        ),
        "upstream_commit": EXPECTED_COMMIT,
        "evidence": "docs/research/nanopb-iterator-cluster-source-audit.md",
    }
    iterator_expected = {
        "open_cfw_nanopb_load_descriptor_values": (238, "dd89dd6ffde3de21c0761e98ceb645ed494903aef88394b34fea22213b322ad3", 186972, "dd89dd6ffde3de21c0761e98ceb645ed494903aef88394b34fea22213b322ad3"),
        "open_cfw_nanopb_field_iter_begin": (90, "5f4fcc5b84f6faba49befdbe75413ccd2d8939b4e9c90451444787c415209bf0", 187212, "86f81edf759d4296942d140c7bcff3aff52521f6109e27c747351e411cdada21"),
        "open_cfw_nanopb_field_iter_begin_extension": (128, "935aa5befe64f3245660bd14b389b5958ea3a0c32d590d4de91fdc3f4d574bc9", 187304, "fbfc98ea658e87c9e5c9bc321cd2b251803ba142f4148b2ac0632470c1f5559d"),
        "open_cfw_nanopb_field_iter_next": (94, "c76863d1be4231d87a7e6be3f6a58ac573b2f0e88c7b996181352147478f1422", 187432, "9b96d379b1d65b4ca49145f1a37b4e7f7daa2b175c895a36135814318494d88f"),
        "open_cfw_nanopb_field_iter_find": (172, "2c87d46723943e4c2e1694965dd1d184e7dde2a032c66e9e7cc4eb37a3999f36", 187528, "8293e795cffeadf2f99b1a1add45a25ce4e7390da1548b6cfdddd45b81460ba3"),
        "open_cfw_nanopb_field_iter_find_extension": (140, "f952a663532a706ed555a920d7f2712fc72291dfb8c6b8fceb40558499bfced2", 187700, "e9ae95af19120813d841e27eca3c95ce53c418b0b75f84a2f6b0aad019118f7b"),
        "open_cfw_nanopb_field_iter_begin_const": (90, "b7df04a3e1dbd3d8a73ecf7f972770a142b0bc559054e6b46966b6f7f6f4bdee", 187840, "86f81edf759d4296942d140c7bcff3aff52521f6109e27c747351e411cdada21"),
        "open_cfw_nanopb_field_iter_begin_extension_const": (128, "e8b3f3355eb5883503e20ac7ff91b0446b08c8bfd9bb917053f76d62513b1119", 187932, "fbfc98ea658e87c9e5c9bc321cd2b251803ba142f4148b2ac0632470c1f5559d"),
        "open_cfw_nanopb_default_field_callback": (52, "f30bc45aa5c3c6fd6f933e4f9d849976e25a267f9ebec2dd05600b9fb5f5a89d", 188060, "f30bc45aa5c3c6fd6f933e4f9d849976e25a267f9ebec2dd05600b9fb5f5a89d"),
    }
    iterator_relocations = {
        "open_cfw_nanopb_load_descriptor_values": [],
        "open_cfw_nanopb_field_iter_begin": [(86, "R_ARM_THM_JUMP24")],
        "open_cfw_nanopb_field_iter_begin_extension": [(116, "R_ARM_THM_CALL")],
        "open_cfw_nanopb_field_iter_next": [(80, "R_ARM_THM_CALL")],
        "open_cfw_nanopb_field_iter_find": [(138, "R_ARM_THM_CALL"), (162, "R_ARM_THM_CALL")],
        "open_cfw_nanopb_field_iter_find_extension": [(118, "R_ARM_THM_CALL"), (136, "R_ARM_THM_JUMP24")],
        "open_cfw_nanopb_field_iter_begin_const": [(86, "R_ARM_THM_JUMP24")],
        "open_cfw_nanopb_field_iter_begin_extension_const": [(116, "R_ARM_THM_CALL")],
        "open_cfw_nanopb_default_field_callback": [],
    }
    for selection, name in enumerate(iterator_functions):
        iterator_leaf = iterator_leaves[name]
        size, digest, offset, unrelocated = iterator_expected[name]
        require(iterator_leaf.get("source") == iterator_source,
                f"nanopb iterator source registration changed: {name}")
        require(iterator_leaf.get("strict_relocation_contract") is True,
                f"nanopb iterator relocation contract changed: {name}")
        require(iterator_leaf.get("expected") == {
            "size": size, "sha256": digest, "alignment": 4,
            "offset": offset, "unrelocated_sha256": unrelocated,
        }, f"nanopb iterator text pin changed: {name}")
        require(
            iterator_leaf.get("toolchain", {}).get("flags", [])[-1]
            == f"-DOPEN_CFW_NANOPB_ITERATOR_SELECTION={selection}",
            f"nanopb iterator isolated compilation selector changed: {name}",
        )
        expected_relocations = [
            {
                "offset": relocation_offset,
                "type": relocation_type,
                "symbol": "open_cfw_nanopb_load_descriptor_values",
                "symbol_type": "STT_NOTYPE",
                "target_function": "open_cfw_nanopb_load_descriptor_values",
            }
            for relocation_offset, relocation_type in iterator_relocations[name]
        ]
        require(iterator_leaf.get("relocations") == expected_relocations,
                f"nanopb iterator relocation set changed: {name}")
    for path, size, digest in EXPECTED_ITERATOR_FILES:
        data = (ROOT / path).read_bytes()
        require(len(data) == size and sha256(data) == digest,
                f"nanopb iterator source pin changed: {path}")

    iterator_patch_specs = (
        ("field_iter_begin", 0x004D9384, 32, "cc5525b596a66b8ba09f2c055d96c08c8ce4a0679efb6f36ce042626a3dc4277"),
        ("field_iter_begin_extension", 0x004D93A4, 52, "fee54683c36fc5510dace567fdb198ab01b619da62d24244e1ee7461b3f32026"),
        ("field_iter_next", 0x004D93D8, 32, "fd4a858244f26a7c27bc2b11fbfa49a29ff434037e663491696b821876fc71f7"),
        ("field_iter_find", 0x004D93F8, 118, "08bc6b102be2bef55978dc3504dda4d6e2d5ea42fe1c5dd213608c07754e8005"),
        ("field_iter_find_extension", 0x004D946E, 74, "6551f77748e3d2271292923b2939c0cf68782df4f731e76a441f30cf531f7bde"),
        ("field_iter_begin_const", 0x004D94BA, 24, "1d71a0692ecf47bbf9b742cf2676484f20ce989b0d3750679a17df23e12a4827"),
        ("field_iter_begin_extension_const", 0x004D94D2, 20, "f67d2e9c40793f2decfc532705dc3d4719f6d8212f7efef381dd9f42f417758e"),
        ("default_field_callback", 0x004D94E6, 60, "1ec35a15769044d8effbad2c20328d0da966cf4af14b9ba890b6d17850813d03"),
    )
    iterator_patches = [
        item for item in overlay.get("patch_sites", [])
        if item.get("target_function") in iterator_functions
    ]
    require(iterator_patches == [
        {
            "name": f"replace_nanopb_{suffix}",
            "runtime_address": address,
            "expected_size": size,
            "expected_sha256": digest,
            "branch": "b_w",
            "target_function": f"open_cfw_nanopb_{suffix}",
        }
        for suffix, address, size, digest in iterator_patch_specs
    ], "nanopb iterator stock patch contract changed")

    defaults_source_common = {
        "path": "components/shared/nanopb/runtime_nanopb_defaults_pair.c",
        "size": 6284,
        "sha256": "76dc1344eb1187f8631e935613246724287c6b1e917efd795dabe17ec5d84491",
        "license": "Zlib",
        "upstream": (
            "https://github.com/nanopb/nanopb/blob/"
            f"{EXPECTED_COMMIT}/pb_decode.c"
        ),
        "upstream_commit": EXPECTED_COMMIT,
    }
    for leaf_record, function, origin_suffix, evidence, selector, expected in (
        (
            message_defaults_leaf,
            "open_cfw_nanopb_message_set_to_defaults",
            "pb_message_set_to_defaults",
            "docs/research/nanopb-message-defaults-source-audit.md",
            1,
            {"size": 158, "sha256": "23ebd977db1eabae81e33dd789fb984c128ec23b3bcd7c253f4b54f882055596", "alignment": 4, "offset": 188112, "unrelocated_sha256": "dc70ed59c4f28728251ce41b219a3d145e52dec7b98ec3940bd88e5cdbcc105c"},
        ),
        (
            field_default_leaf,
            "open_cfw_nanopb_field_set_to_default",
            "pb_field_set_to_default",
            "docs/research/nanopb-field-default-source-audit.md",
            0,
            {"size": 256, "sha256": "5cfe4525760f82d39ca487e4a4dfb5120b30401ddaca71b49d73ad81fc6a409a", "alignment": 4, "offset": 188272, "unrelocated_sha256": "5450f92492613c95ce01f97ab9da3450a9142a33acaa64790c85453d2ce314d9"},
        ),
    ):
        source = dict(defaults_source_common)
        source["origin"] = (
            "altered production adaptation of authenticated nanopb 0.4.9 "
            f"private {origin_suffix}"
        )
        source["evidence"] = evidence
        require(
            leaf_record.get("function") == function
            and leaf_record.get("source") == source
            and leaf_record.get("strict_relocation_contract") is True
            and leaf_record.get("expected") == expected
            and leaf_record.get("toolchain", {}).get("flags", [])[-1]
            == f"-DOPEN_CFW_NANOPB_DEFAULTS_SELECTION={selector}",
            f"nanopb defaults production leaf changed: {function}",
        )

    require(
        message_defaults_leaf.get("relocations") == [
            {"offset": 38, "type": "R_ARM_THM_CALL", "symbol": "open_cfw_nanopb_istream_from_buffer", "symbol_type": "STT_NOTYPE", "target_function": "open_cfw_nanopb_istream_from_buffer"},
            {"offset": 54, "type": "R_ARM_THM_CALL", "symbol": "open_cfw_nanopb_decode_tag", "symbol_type": "STT_NOTYPE", "target_function": "open_cfw_nanopb_decode_tag"},
            {"offset": 78, "type": "R_ARM_THM_CALL", "symbol": "open_cfw_nanopb_field_iter_next", "symbol_type": "STT_NOTYPE", "target_function": "open_cfw_nanopb_field_iter_next"},
            {"offset": 86, "type": "R_ARM_THM_CALL", "symbol": "open_cfw_nanopb_field_set_to_default", "symbol_type": "STT_NOTYPE", "target_address": 0x007B38CC},
            {"offset": 112, "type": "R_ARM_THM_CALL", "symbol": "open_cfw_nanopb_decode_field", "symbol_type": "STT_NOTYPE", "target_address": 0x007B39CC},
            {"offset": 126, "type": "R_ARM_THM_CALL", "symbol": "open_cfw_nanopb_decode_tag", "symbol_type": "STT_NOTYPE", "target_function": "open_cfw_nanopb_decode_tag"},
        ],
        "nanopb message-default relocation contract changed",
    )
    require(
        field_default_leaf.get("relocations") == [
            {"offset": 38, "type": "R_ARM_THM_CALL", "symbol": "open_cfw_nanopb_field_iter_begin_extension", "symbol_type": "STT_NOTYPE", "target_function": "open_cfw_nanopb_field_iter_begin_extension"},
            {"offset": 50, "type": "R_ARM_THM_CALL", "symbol": "open_cfw_nanopb_message_set_to_defaults", "symbol_type": "STT_NOTYPE", "target_function": "open_cfw_nanopb_message_set_to_defaults"},
            {"offset": 144, "type": "R_ARM_THM_CALL", "symbol": "open_cfw_nanopb_field_iter_begin", "symbol_type": "STT_NOTYPE", "target_function": "open_cfw_nanopb_field_iter_begin"},
            {"offset": 152, "type": "R_ARM_THM_CALL", "symbol": "open_cfw_nanopb_message_set_to_defaults", "symbol_type": "STT_NOTYPE", "target_function": "open_cfw_nanopb_message_set_to_defaults"},
        ],
        "nanopb field-default relocation contract changed",
    )
    defaults_patches = [
        item for item in overlay.get("patch_sites", [])
        if item.get("target_function") in {
            "open_cfw_nanopb_field_set_to_default",
            "open_cfw_nanopb_message_set_to_defaults",
        }
    ]
    require(defaults_patches == [
        {"name": "replace_nanopb_field_set_to_default", "runtime_address": 0x0048FCE2, "expected_size": 272, "expected_sha256": "0d0dd0be0ae68f84bb20e39f7c95f500656316563d95b6d5cc3e290d4b131728", "branch": "b_w", "target_function": "open_cfw_nanopb_field_set_to_default"},
        {"name": "replace_nanopb_message_set_to_defaults", "runtime_address": 0x0048FDF2, "expected_size": 166, "expected_sha256": "1409633f121586a45b076e247e2f1f33f6120be85044245f42ca777955bd34e4", "branch": "b_w", "target_function": "open_cfw_nanopb_message_set_to_defaults"},
    ], "nanopb defaults stock patch contract changed")

    dispatch_source_common = {
        "path": "components/shared/nanopb/runtime_nanopb_dispatch_extension.c",
        "size": 3804,
        "sha256": "b4a6620fdc79fdbb3b3891166d6248176b396cf18b7157cd3d300d66ee15de96",
        "license": "Zlib",
        "upstream": allowed_upstream_url,
        "upstream_commit": EXPECTED_COMMIT,
        "evidence": "docs/research/nanopb-dispatch-extension-source-audit.md",
    }
    dispatch_specs = (
        (
            decode_field_leaf, "open_cfw_nanopb_decode_field", 0,
            "altered production adaptation of authenticated nanopb 0.4.9 private decode_field dispatcher",
            {"size": 52, "sha256": "98ab7f89b2e0495a37751849c7f50be480612533e355ea28df776e90baf6d70a", "alignment": 4, "offset": 188528, "unrelocated_sha256": "041eeef52b7cee972328166a448d95454de480aff4f79da472479075af403648", "closure_size": 71, "closure_sha256": "73449efad731ed0efcbc1746ba5153f3393dafe7109bac1fde9aa0668a5cd1a3", "rodata_offset": 52},
        ),
        (
            default_extension_leaf,
            "open_cfw_nanopb_default_extension_decoder", 1,
            "altered production adaptation of authenticated nanopb 0.4.9 private default_extension_decoder",
            {"size": 74, "sha256": "cc38007d8f49563214acec19b8dcbe0f984198d793b50a8e8c4bd550c4d4de94", "alignment": 4, "offset": 188600, "unrelocated_sha256": "e343e1706c3cf67b596f0c50bdf7a6379f7a22baa23bcfb5402206345c44830d", "closure_size": 92, "closure_sha256": "569b19bc1745605dd3cb19da57ff5b22ba4caecf08287664a125d0dd964bc6a1", "rodata_offset": 74},
        ),
        (
            decode_extension_leaf, "open_cfw_nanopb_decode_extension", 2,
            "altered production adaptation of authenticated nanopb 0.4.9 private decode_extension",
            {"size": 80, "sha256": "50d9c17ea04afb7b55f05269eadae500e4036c505a9311cccf9eb10a1fc2f154", "alignment": 4, "offset": 188692, "unrelocated_sha256": "6b7b562d0571411689c7ea1402ffba86cfd8255d6aed6bca349288a7d89887da"},
        ),
    )
    for dispatch_leaf, function, selector, origin, expected in dispatch_specs:
        source = dict(dispatch_source_common)
        source["origin"] = origin
        require(
            dispatch_leaf.get("source") == source
            and dispatch_leaf.get("strict_relocation_contract") is True
            and dispatch_leaf.get("expected") == expected
            and dispatch_leaf.get("toolchain", {}).get("flags", [])[-1]
            == f"-DOPEN_CFW_NANOPB_DISPATCH_SELECTION={selector}",
            f"nanopb dispatch production leaf changed: {function}",
        )
    require(
        decode_field_leaf.get("closure", {}).get("rodata", {}).get("sha256")
        == "6a8abe1a00cdabc842420e076e863e2b2fb23c5982f5a7cda7a2b29aea70f521"
        and decode_field_leaf.get("relocations") == [
            {"offset": 12, "type": "R_ARM_THM_JUMP24", "symbol": "open_cfw_nanopb_decode_callback_field", "symbol_type": "STT_NOTYPE", "target_address": 0x0048FB30},
            {"offset": 16, "type": "R_ARM_THM_JUMP24", "symbol": "open_cfw_nanopb_decode_static_field", "symbol_type": "STT_NOTYPE", "target_address": 0x0048F968},
            {"offset": 24, "type": "R_ARM_THM_JUMP24", "symbol": "open_cfw_nanopb_decode_pointer_field", "symbol_type": "STT_NOTYPE", "target_address": 0x0048FB1C},
            {"offset": 36, "type": "R_ARM_THM_MOVW_PREL_NC", "symbol": ".L.str"},
            {"offset": 40, "type": "R_ARM_THM_MOVT_PREL", "symbol": ".L.str"},
        ],
        "nanopb decode_field closure changed",
    )
    require(
        default_extension_leaf.get("closure", {}).get("rodata", {}).get("sha256")
        == "00cb39165079aa30025e126d2c619e8460de55b101e8acf0d114742383d30faf"
        and default_extension_leaf.get("relocations") == [
            {"offset": 14, "type": "R_ARM_THM_CALL", "symbol": "open_cfw_nanopb_field_iter_begin_extension", "symbol_type": "STT_NOTYPE", "target_function": "open_cfw_nanopb_field_iter_begin_extension"},
            {"offset": 44, "type": "R_ARM_THM_CALL", "symbol": "open_cfw_nanopb_decode_field", "symbol_type": "STT_NOTYPE", "target_function": "open_cfw_nanopb_decode_field"},
            {"offset": 56, "type": "R_ARM_THM_MOVW_PREL_NC", "symbol": ".L.str"},
            {"offset": 60, "type": "R_ARM_THM_MOVT_PREL", "symbol": ".L.str"},
        ]
        and decode_extension_leaf.get("relocations") == [
            {"offset": 30, "type": "R_ARM_THM_CALL", "symbol": "open_cfw_nanopb_default_extension_decoder", "symbol_type": "STT_NOTYPE", "target_function": "open_cfw_nanopb_default_extension_decoder"},
        ],
        "nanopb extension dispatch relocation contract changed",
    )
    dispatch_patches = [
        item for item in overlay.get("patch_sites", [])
        if item.get("target_function") in {
            "open_cfw_nanopb_decode_field",
            "open_cfw_nanopb_default_extension_decoder",
            "open_cfw_nanopb_decode_extension",
        }
    ]
    require(dispatch_patches == [
        {"name": "replace_nanopb_decode_field", "runtime_address": 0x0048FBE4, "expected_size": 66, "expected_sha256": "a7e2136d4de19007cab84722398b120c6cf806ec558163447cf11d33064e8479", "branch": "b_w", "target_function": "open_cfw_nanopb_decode_field"},
        {"name": "replace_nanopb_default_extension_decoder", "runtime_address": 0x0048FC26, "expected_size": 82, "expected_sha256": "dbd41534fcd6ff0fc27f1bf87225f233020ba5c904e4aa4a5c9c85a83bd988d6", "branch": "b_w", "target_function": "open_cfw_nanopb_default_extension_decoder"},
        {"name": "replace_nanopb_decode_extension", "runtime_address": 0x0048FC88, "expected_size": 90, "expected_sha256": "0f630c1173971762af8df1ec82ed50cff6f292a9b77eafae06e56b9f3b659472", "branch": "b_w", "target_function": "open_cfw_nanopb_decode_extension"},
    ], "nanopb dispatch stock patch contract changed")

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
            "sha256": "a22848a6dceebd34b168abfcf228528f9685722f2e19a2283230d91ccd47101b",
            "alignment": 4,
            "offset": 184292,
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
        close_leaf.get("toolchain_profiles", {}).get("linux-clang")
        == {
                "reviewed_version_prefix": "Homebrew clang version 22.1.8",
                "expected": {
                    "size": 36,
                    "sha256": (
                        "230981d03cad6160f2cb07ec8179c8bb0"
                        "3b562123df5319e3b339447fa5e8eaa"
                    ),
                    "alignment": 4,
                    "offset": 186016,
                    "unrelocated_sha256": (
                        "5e6ee5f441e5ba91e0e0147b8453a311"
                        "86f3ce4bd0efc114edda60f00093a51e"
                    ),
                },
                "relocations": [close_call],
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
                "65cd86293fd56b00206068dc1063abb83"
                "8b0226f672b9dfc841cd5445295a0a3"
            ),
            "alignment": 4,
            "offset": 184344,
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
                "11a61606490ff9e8f3b7765132a579739"
                "5c567893e2607f1231f35d04201058e"
            ),
            "alignment": 4,
            "offset": 186068,
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
                "1a807b643995c339947925fd3bc95385b"
                "0f201fe6c541aafd03548256f37cb0f"
            ),
            "alignment": 4,
            "offset": 184460,
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
                "2cc26838da46672ae8cd5d9a4b8d5ee5"
                "40d543993a04fc1e37a68c5ddded11c1"
            ),
            "alignment": 4,
            "offset": 186184,
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
        "offset": 184488,
        "unrelocated_sha256": (
            "06def086733fd9801b712161943b0da64"
            "e3b2bdf82e6f5962ee9207c738c00b1"
        ),
    }
    require(
        read_leaf.get("expected") == expected_read,
        "pb_read canonical text contract changed",
    )
    expected_read["offset"] = 186216
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
            "sha256": "e4c289e7f56d555e684722566f4076a03a67bdfd5cf6b45c39f6cb9c53c354f8",
            "alignment": 4,
            "offset": 184648,
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
            "offset": 184680,
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
            "offset": 184744,
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
            "offset": 186472,
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
            "offset": 184764,
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
                "offset": 186496,
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
            "alignment": 4, "offset": 184820,
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
            "alignment": 4, "offset": 185060,
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
                "alignment": 4, "offset": 186548,
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
                "alignment": 4, "offset": 186788,
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
    skip_field_patches = [
        item for item in overlay.get("patch_sites", [])
        if item.get("target_function") == "open_cfw_nanopb_skip_field"
    ]
    require(
        skip_field_patches
        == [{
            "name": "replace_nanopb_skip_field",
            "runtime_address": 0x0048F6A0,
            "expected_size": 74,
            "expected_sha256": "36089daffbbc82abad65d97ae0fd64b58b8ad227ed585aa704611bc30369912d",
            "branch": "b_w",
            "target_function": "open_cfw_nanopb_skip_field",
        }],
        "pb_skip_field stock patch contract changed",
    )
    read_raw_patches = [
        item for item in overlay.get("patch_sites", [])
        if item.get("target_function") == "open_cfw_nanopb_read_raw_value"
    ]
    require(
        read_raw_patches
        == [{
            "name": "replace_nanopb_read_raw_value",
            "runtime_address": 0x0048F6EA,
            "expected_size": 148,
            "expected_sha256": "1e970a9b198943e309550811010fc1ba4008d671d023abfc5c893b965fee2bc9",
            "branch": "b_w",
            "target_function": "open_cfw_nanopb_read_raw_value",
        }],
        "read_raw_value stock patch contract changed",
    )
    substream_patches = [
        item for item in overlay.get("patch_sites", [])
        if item.get("target_function") == "open_cfw_nanopb_make_string_substream"
    ]
    require(
        substream_patches
        == [{
            "name": "replace_nanopb_make_string_substream",
            "runtime_address": 0x0048F77E,
            "expected_size": 76,
            "expected_sha256": "db925e0c532bac2f2e38f398c7b7d99669afe4d41e6690b08116e9f06ec7d88d",
            "branch": "b_w",
            "target_function": "open_cfw_nanopb_make_string_substream",
        }],
        "pb_make_string_substream stock patch contract changed",
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
            "file_offset": 3708140,
            "size": 20,
            "target": "apollo510b_internal_mram",
            "target_address": 0x007C14CC,
            "address_status": "source_compiled",
            "output": (
                "apollo510b/main-source-nanopb-istream-from-buffer-"
                "0x007c14cc.bin"
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
            "file_offset": 3708160,
            "size": 54,
            "target": "apollo510b_internal_mram",
            "target_address": 0x007C14E0,
            "address_status": "source_compiled",
            "output": (
                "apollo510b/main-source-nanopb-decode-svarint-"
                "0x007c14e0.bin"
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
    for record in varint32_manifest:
        old_address = record["target_address"]
        if old_address >= 0x007B0000:
            new_address = old_address + EXPECTED_APPLE_OVERLAY_PLACEMENT_DELTA
            record["file_offset"] += EXPECTED_APPLE_OVERLAY_PLACEMENT_DELTA
            record["target_address"] = new_address
            record["output"] = record["output"].replace(
                f"0x{old_address:08x}", f"0x{new_address:08x}"
            )
    require(
        [by_name.get(item["name"]) for item in varint32_manifest]
        == varint32_manifest,
        "pb_decode_varint32 manifest ownership changed",
    )
    # The authenticated nanopb text and source-entry spans are unchanged.  The
    # DM advertising admission prepends this exact byte count to the Apple
    # overlay, so normalize only source-owned overlay placements before
    # comparing the remaining historical manifest ownership pins below.
    normalized_by_name = {}
    for name, region in by_name.items():
        normalized = dict(region)
        address = normalized.get("target_address", 0)
        if address >= 0x007C0000:
            normalized["file_offset"] -= EXPECTED_APPLE_OVERLAY_PLACEMENT_DELTA
            normalized["target_address"] -= EXPECTED_APPLE_OVERLAY_PLACEMENT_DELTA
        normalized_by_name[name] = normalized
    by_name = normalized_by_name
    skip_string_manifest = {
        "nanopb_skip_string_source_replacement": (
            357996, 32, 0x0048F64C, "generated_source_entry_replacement"
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
    skip_field_manifest = {
        "nanopb_skip_field_source_replacement": (
            358080, 74, 0x0048F6A0, "generated_source_entry_replacement"
        ),
        "apollo_nanopb_skip_field_source_alignment": (
            3648654, 2, 0x007B2C6E, "generated_alignment"
        ),
        "apollo_nanopb_skip_field_source_leaf": (
            3648656, 66, 0x007B2C70, "source_compiled"
        ),
        "apollo_nanopb_skip_field_error_rodata": (
            3648722, 18, 0x007B2CB2, "source_compiled"
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
            for name in skip_field_manifest
        }
        == skip_field_manifest,
        "pb_skip_field manifest ownership changed",
    )
    read_raw_manifest = {
        "nanopb_read_raw_value_source_replacement": (
            358154, 148, 0x0048F6EA, "generated_source_entry_replacement"
        ),
        "apollo_nanopb_read_raw_value_source_leaf": (
            3648740, 134, 0x007B2CC4, "source_compiled"
        ),
        "apollo_nanopb_read_raw_value_error_rodata": (
            3648874, 34, 0x007B2D4A, "source_compiled"
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
            for name in read_raw_manifest
        }
        == read_raw_manifest,
        "read_raw_value manifest ownership changed",
    )
    substream_manifest = {
        "nanopb_make_string_substream_source_replacement": (
            358302, 76, 0x0048F77E, "generated_source_entry_replacement"
        ),
        "apollo_nanopb_make_string_substream_source_leaf": (
            3648908, 72, 0x007B2D6C, "source_compiled"
        ),
        "apollo_nanopb_make_string_substream_error_rodata": (
            3648980, 24, 0x007B2DB4, "source_compiled"
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
            for name in substream_manifest
        }
        == substream_manifest,
        "pb_make_string_substream manifest ownership changed",
    )
    bool_manifest = {
        "nanopb_decode_bool_source_replacement": (
            360780, 36, 0x0049012C, "generated_source_entry_replacement"
        ),
        "nanopb_dec_bool_source_replacement": (
            360940, 10, 0x004901CC, "generated_source_entry_replacement"
        ),
        "apollo_nanopb_decode_bool_source_leaf": (
            3649004, 28, 0x007B2DCC, "source_compiled"
        ),
        "apollo_nanopb_dec_bool_source_leaf": (
            3649032, 6, 0x007B2DE8, "source_compiled"
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
            for name in bool_manifest
        }
        == bool_manifest,
        "Boolean-cluster manifest ownership changed",
    )
    dec_varint_manifest = {
        "nanopb_dec_varint_source_replacement": (
            360950, 380, 0x004901D6, "generated_source_entry_replacement"
        ),
        "apollo_nanopb_dec_varint_source_alignment": (
            3649038, 2, 0x007B2DEE, "generated_alignment"
        ),
        "apollo_nanopb_dec_varint_source_leaf": (
            3649040, 304, 0x007B2DF0, "source_compiled"
        ),
        "apollo_nanopb_dec_varint_error_rodata": (
            3649344, 36, 0x007B2F20, "source_compiled"
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
            for name in dec_varint_manifest
        }
        == dec_varint_manifest,
        "pb_dec_varint manifest ownership changed",
    )
    dec_bytes_manifest = {
        "nanopb_dec_bytes_source_replacement": (
            361336, 146, 0x00490358, "generated_source_entry_replacement"
        ),
        "apollo_nanopb_dec_bytes_source_leaf": (
            3649380, 98, 0x007B2F44, "source_compiled"
        ),
        "apollo_nanopb_dec_bytes_error_rodata": (
            3649478, 48, 0x007B2FA6, "source_compiled"
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
            for name in dec_bytes_manifest
        }
        == dec_bytes_manifest,
        "pb_dec_bytes manifest ownership changed",
    )
    dec_string_manifest = {
        "nanopb_dec_string_source_replacement": (
            361482, 158, 0x004903EA, "generated_source_entry_replacement"
        ),
        "apollo_nanopb_dec_string_source_alignment": (
            3649526, 2, 0x007B2FD6, "generated_alignment"
        ),
        "apollo_nanopb_dec_string_source_leaf": (
            3649528, 114, 0x007B2FD8, "source_compiled"
        ),
        "apollo_nanopb_dec_string_error_rodata": (
            3649642, 49, 0x007B304A, "source_compiled"
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
            for name in dec_string_manifest
        }
        == dec_string_manifest,
        "pb_dec_string manifest ownership changed",
    )
    dec_submessage_manifest = {
        "nanopb_dec_submessage_source_replacement": (361644, 172, 0x0049048C, "generated_source_entry_replacement"),
        "apollo_nanopb_dec_submessage_source_alignment": (3649691, 1, 0x007B307B, "generated_alignment"),
        "apollo_nanopb_dec_submessage_source_leaf": (3649692, 138, 0x007B307C, "source_compiled"),
        "apollo_nanopb_dec_submessage_error_rodata": (3649830, 25, 0x007B3106, "source_compiled"),
    }
    require({name: (by_name.get(name, {}).get("file_offset"),
                    by_name.get(name, {}).get("size"),
                    by_name.get(name, {}).get("target_address"),
                    by_name.get(name, {}).get("address_status"))
             for name in dec_submessage_manifest} == dec_submessage_manifest,
            "pb_dec_submessage manifest ownership changed")
    decode_inner_manifest = {
        "nanopb_decode_inner_source_replacement": (360120, 634, 0x0048FE98, "generated_source_entry_replacement"),
        "apollo_nanopb_decode_inner_source_alignment": (3649855, 1, 0x007B311F, "generated_alignment"),
        "apollo_nanopb_decode_inner_source_leaf": (3649856, 530, 0x007B3120, "source_compiled"),
        "apollo_nanopb_decode_inner_error_rodata": (3650386, 88, 0x007B3332, "source_compiled"),
    }
    require({name: (by_name.get(name, {}).get("file_offset"),
                    by_name.get(name, {}).get("size"),
                    by_name.get(name, {}).get("target_address"),
                    by_name.get(name, {}).get("address_status"))
             for name in decode_inner_manifest} == decode_inner_manifest,
            "pb_decode_inner manifest ownership changed")
    decode_tag_manifest = {
        "nanopb_decode_tag_source_replacement": (358028, 52, 0x0048F66C, "generated_source_entry_replacement"),
        "apollo_nanopb_decode_tag_source_alignment": (3650474, 2, 0x007B338A, "generated_alignment"),
        "apollo_nanopb_decode_tag_source_leaf": (3650476, 42, 0x007B338C, "source_compiled"),
    }
    require({name: (by_name.get(name, {}).get("file_offset"),
                    by_name.get(name, {}).get("size"),
                    by_name.get(name, {}).get("target_address"),
                    by_name.get(name, {}).get("address_status"))
             for name in decode_tag_manifest} == decode_tag_manifest,
            "pb_decode_tag manifest ownership changed")
    iterator_manifest = {
        "nanopb_field_iter_begin_source_replacement": (660388, 32, 0x004D9384, "generated_source_entry_replacement"),
        "nanopb_field_iter_begin_extension_source_replacement": (660420, 52, 0x004D93A4, "generated_source_entry_replacement"),
        "nanopb_field_iter_next_source_replacement": (660472, 32, 0x004D93D8, "generated_source_entry_replacement"),
        "nanopb_field_iter_find_source_replacement": (660504, 118, 0x004D93F8, "generated_source_entry_replacement"),
        "nanopb_field_iter_find_extension_source_replacement": (660622, 74, 0x004D946E, "generated_source_entry_replacement"),
        "nanopb_iterator_const_cast_opaque": (660696, 2, 0x004D94B8, "official_blob"),
        "nanopb_field_iter_begin_const_source_replacement": (660698, 24, 0x004D94BA, "generated_source_entry_replacement"),
        "nanopb_field_iter_begin_extension_const_source_replacement": (660722, 20, 0x004D94D2, "generated_source_entry_replacement"),
        "nanopb_default_field_callback_source_replacement": (660742, 60, 0x004D94E6, "generated_source_entry_replacement"),
        "apollo_nanopb_iterator_provider_alignment": (3650518, 2, 0x007B33B6, "generated_alignment"),
        "apollo_nanopb_iterator_provider_source_leaf": (3650520, 238, 0x007B33B8, "source_compiled"),
        "apollo_nanopb_field_iter_begin_alignment": (3650758, 2, 0x007B34A6, "generated_alignment"),
        "apollo_nanopb_field_iter_begin_source_leaf": (3650760, 90, 0x007B34A8, "source_compiled"),
        "apollo_nanopb_field_iter_begin_extension_alignment": (3650850, 2, 0x007B3502, "generated_alignment"),
        "apollo_nanopb_field_iter_begin_extension_source_leaf": (3650852, 128, 0x007B3504, "source_compiled"),
        "apollo_nanopb_field_iter_next_source_leaf": (3650980, 94, 0x007B3584, "source_compiled"),
        "apollo_nanopb_field_iter_find_alignment": (3651074, 2, 0x007B35E2, "generated_alignment"),
        "apollo_nanopb_field_iter_find_source_leaf": (3651076, 172, 0x007B35E4, "source_compiled"),
        "apollo_nanopb_field_iter_find_extension_source_leaf": (3651248, 140, 0x007B3690, "source_compiled"),
        "apollo_nanopb_field_iter_begin_const_source_leaf": (3651388, 90, 0x007B371C, "source_compiled"),
        "apollo_nanopb_field_iter_begin_extension_const_alignment": (3651478, 2, 0x007B3776, "generated_alignment"),
        "apollo_nanopb_field_iter_begin_extension_const_source_leaf": (3651480, 128, 0x007B3778, "source_compiled"),
        "apollo_nanopb_default_field_callback_source_leaf": (3651608, 52, 0x007B37F8, "source_compiled"),
    }
    require({name: (by_name.get(name, {}).get("file_offset"),
                    by_name.get(name, {}).get("size"),
                    by_name.get(name, {}).get("target_address"),
                    by_name.get(name, {}).get("address_status"))
             for name in iterator_manifest} == iterator_manifest,
            "nanopb iterator manifest ownership changed")
    defaults_manifest = {
        "nanopb_field_set_to_default_source_replacement": (359682, 272, 0x0048FCE2, "generated_source_entry_replacement"),
        "nanopb_message_set_to_defaults_source_replacement": (359954, 166, 0x0048FDF2, "generated_source_entry_replacement"),
        "apollo_nanopb_message_set_to_defaults_source_leaf": (3651660, 158, 0x007B382C, "source_compiled"),
        "apollo_nanopb_field_set_to_default_alignment": (3651818, 2, 0x007B38CA, "generated_alignment"),
        "apollo_nanopb_field_set_to_default_source_leaf": (3651820, 256, 0x007B38CC, "source_compiled"),
    }
    require({name: (by_name.get(name, {}).get("file_offset"),
                    by_name.get(name, {}).get("size"),
                    by_name.get(name, {}).get("target_address"),
                    by_name.get(name, {}).get("address_status"))
             for name in defaults_manifest} == defaults_manifest,
            "nanopb defaults manifest ownership changed")
    dispatch_manifest = {
        "nanopb_decode_field_source_replacement": (359428, 66, 0x0048FBE4, "generated_source_entry_replacement"),
        "nanopb_default_extension_decoder_source_replacement": (359494, 82, 0x0048FC26, "generated_source_entry_replacement"),
        "nanopb_dispatch_literal_island": (359576, 16, 0x0048FC78, "official_blob"),
        "nanopb_decode_extension_source_replacement": (359592, 90, 0x0048FC88, "generated_source_entry_replacement"),
        "apollo_nanopb_decode_field_source_closure": (3652076, 71, 0x007B39CC, "source_compiled"),
        "apollo_nanopb_default_extension_decoder_alignment": (3652147, 1, 0x007B3A13, "generated_alignment"),
        "apollo_nanopb_default_extension_decoder_source_closure": (3652148, 92, 0x007B3A14, "source_compiled"),
        "apollo_nanopb_decode_extension_source_leaf": (3652240, 80, 0x007B3A70, "source_compiled"),
    }
    require({name: (by_name.get(name, {}).get("file_offset"),
                    by_name.get(name, {}).get("size"),
                    by_name.get(name, {}).get("target_address"),
                    by_name.get(name, {}).get("address_status"))
             for name in dispatch_manifest} == dispatch_manifest,
            "nanopb dispatch manifest ownership changed")
    field_decoder_manifest = {
        "nanopb_decode_basic_field_source_replacement": (358420, 372, 0x0048F7F4, "generated_source_entry_replacement"),
        "nanopb_decode_static_field_source_replacement": (358792, 436, 0x0048F968, "generated_source_entry_replacement"),
        "nanopb_decode_pointer_field_source_replacement": (359228, 20, 0x0048FB1C, "generated_source_entry_replacement"),
        "nanopb_decode_callback_field_source_replacement": (359248, 180, 0x0048FB30, "generated_source_entry_replacement"),
        "nanopb_dec_fixed_length_bytes_source_replacement": (361820, 108, 0x0049053C, "generated_source_entry_replacement"),
        "apollo_nanopb_dec_fixed_length_bytes_source_closure": (3652320, 219, 0x007B3AC0, "source_compiled"),
        "apollo_nanopb_decode_basic_field_alignment": (3652539, 1, 0x007B3B9B, "generated_alignment"),
        "apollo_nanopb_decode_basic_field_source_closure": (3652540, 245, 0x007B3B9C, "source_compiled"),
        "apollo_nanopb_decode_static_field_alignment": (3652785, 3, 0x007B3C91, "generated_alignment"),
        "apollo_nanopb_decode_static_field_source_closure": (3652788, 446, 0x007B3C94, "source_compiled"),
        "apollo_nanopb_decode_pointer_field_alignment": (3653234, 2, 0x007B3E52, "generated_alignment"),
        "apollo_nanopb_decode_pointer_field_source_closure": (3653236, 42, 0x007B3E54, "source_compiled"),
        "apollo_nanopb_decode_callback_field_alignment": (3653278, 2, 0x007B3E7E, "generated_alignment"),
        "apollo_nanopb_decode_callback_field_source_closure": (3653280, 180, 0x007B3E80, "source_compiled"),
    }
    require({name: (by_name.get(name, {}).get("file_offset"),
                    by_name.get(name, {}).get("size"),
                    by_name.get(name, {}).get("target_address"),
                    by_name.get(name, {}).get("address_status"))
             for name in field_decoder_manifest} == field_decoder_manifest,
            "nanopb field-decoder manifest ownership changed")
    # Nanopb owns the named-region checks above.  Other dependencies may append
    # independently audited regions, so only fail if the reviewed baseline was
    # truncated rather than pinning the whole Apollo manifest forever.
    require(len(regions) >= 1106, "Apollo-main manifest lost reviewed regions")
    verify_istream_source_pins()
    verify_svarint_source_pins()
    verify_varint32_source_pins()
    verify_skip_string_source_pins()
    verify_skip_field_source_pins()
    verify_read_raw_source_pins()
    verify_bool_cluster_source_pins()
    verify_dec_varint_source_pins()
    verify_dec_bytes_source_pins()
    verify_dec_string_source_pins()
    verify_dec_submessage_source_pins()
    verify_decode_inner_and_tag_source_pins()
    verify_defaults_source_pins()
    verify_dispatch_source_pins()
    verify_field_decoder_source_pins()
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
