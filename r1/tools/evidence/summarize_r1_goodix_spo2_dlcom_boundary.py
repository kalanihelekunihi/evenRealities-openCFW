#!/usr/bin/env python3
"""Pin the recovered Goodix GH_SPO2/dlCom processing boundary.

This is an ownership census only.  It emits no SpO2 implementation, neural
network, model weights, or vendor-derived clean-room product source.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x00027000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"
EXPECTED_ENTRY_SET_SHA256 = "42e317fc0bf13d4814c084d0af899aba3f3b0cb3d5f3e6f92ce9eafbfe27f425"
EXPECTED_BODY_SET_SHA256 = "107ad3747990d7168fe491cb0a23798f47817769d04edd8a46297309c44908e5"
EXPECTED_CALLMAP_SHA256 = "eacc1655ab0bfb2ab9267b9c4bfc55142677f59b9cab44edbfcee8ceb8bcdf24"


def _role(entry: int) -> str:
    if entry == 0x0006C6A8:
        return "GH_SPO2/dlCom processing root"
    if entry == 0x0006CCC0:
        return "GH_SPO2/dlCom input diagnostic formatter"
    if entry == 0x00028AD4:
        return "dlCom model-graph dispatcher"
    if entry in (0x0005D01C, 0x000742E4):
        return "dlCom generated model-graph builder"
    if entry == 0x00074A20:
        return "dlCom quantized recurrent-layer constructor"
    if entry == 0x000739A8:
        return "dlCom quantized recurrent-layer executor"
    if entry == 0x000617F8:
        return "dormant dlCom generated model-graph executor"
    if entry == 0x000876C8:
        return "dormant dlCom quantized neural-layer executor"
    if entry in (0x0006EB94, 0x0002F624, 0x00036C26):
        return "GH_SPO2/dlCom generated-model initialization bridge"
    if entry == 0x0004387C:
        return "GH_SPO2/dlCom generated model-graph builder"
    if entry in (0x000290DC, 0x00036408, 0x00036590, 0x0006FDE0, 0x0007405C):
        return "dlCom quantized recurrent-runtime helper"
    return "GH_SPO2/dlCom closed-callgraph helper"


def _function(
    entry: int,
    end_exclusive: int,
    size: int,
    sha256: str,
    segments: tuple[tuple[int, int], ...] = (),
) -> dict[str, Any]:
    return {
        "entry": entry,
        "end_exclusive": end_exclusive,
        "size": size,
        "role": _role(entry),
        "sha256": sha256,
        "segments": segments or ((entry, end_exclusive),),
        "inventory": "ghidra_function",
        "provider_family": "goodix_gh3x2x_candidate",
        "source_disposition": "vendor_source_required_not_redistributable",
    }


# Direct formerly-unclassified descendants of the existing Goodix callsite at
# 0x0002CA24, plus the model builders selected by the byte-pinned dispatcher
# table at 0x000BCF58.  Descriptive roles are boundary labels, not private
# Goodix symbols. Compiler-scattered functions explicitly list only their
# executable ranges so intervening literal pools and unrelated code are not
# attributed to this provider.
GOODIX_SPO2_DLCOM_FUNCTIONS = (
    _function(0x00028AD4, 0x00028B12, 62, "9553c81cf675a3cc8368f18f40fc8914ef791613301d5b23f9d940b365b2155b"),
    _function(0x00028CF4, 0x00028DBC, 200, "164cbd79501afbb9b72b048e1094951615a83f569a6f1c8165e840e513381b7b"),
    _function(0x00028DDA, 0x00036392, 164, "33f6d23fa8fcb6b04da7e8e46aa7b29df1cc6b00ae0d178660d13130050cd289", ((0x00028DDA, 0x00028DE0), (0x000362F4, 0x00036392))),
    _function(0x00028DE6, 0x0004FE5C, 106, "a42ddf3c0da1fd4de3a55b24eadc6c08ca48ba5b5a67f8c7136c270d6f978f5d", ((0x00028DE6, 0x00028DEC), (0x0004FDF8, 0x0004FE5C))),
    _function(0x000290DC, 0x000290FE, 34, "bdec0f3376563581f2578e7e253ebd0d44f950cb7cffaf4fe0eac54aafafdead"),
    _function(0x00029394, 0x000293F4, 96, "e0f3bab9737157c10729bc09c4ba1d2084667a7bd600a6ac491015665906b349"),
    _function(0x0002951A, 0x000295DE, 196, "794b7eeaaa22a942ad358f960302d3649646dc4829948b0c018b220a8d3a84ef"),
    _function(0x0002F624, 0x0002F658, 52, "02fbe9a3862a6d3cc7a74c3bb57b5deff29675b1651e17d2a24da3206cb889fb"),
    _function(0x00029AD8, 0x00098FFC, 340, "927d45c96beae6a19ae6ec497db8974e166128f49cbe1bc044a3f6ee3c0b2035", ((0x00029AD8, 0x00029BB4), (0x00098F84, 0x00098FFC))),
    _function(0x0002F65C, 0x0002F660, 4, "7a9b0e73c2cbb0f774b6843fc2a8811f3877d742ee2247b8014baf435e57542c"),
    _function(0x0002FF10, 0x00030062, 338, "9870d22542b55c4bd8728f0c7e7dedaa03a9ca3be47ed634899a2e7fb94683bb"),
    _function(0x00030800, 0x0003096C, 364, "c27dc0c687730f3b5243f6de5903fd22ef61b09ae51e62bf7855adc369c8dec8"),
    _function(0x0003113C, 0x00031624, 1240, "96f4fe901ef2933d58e73b36d5532d8bc3623246beee03d37969cc472b695935", ((0x0003113C, 0x00031554), (0x00031564, 0x00031624))),
    _function(0x00031774, 0x000317C6, 82, "5416fb9c2b46924cf811e1f86c7d066db0d660d837d5f01fe8f16710e36084d0"),
    _function(0x00034500, 0x0003497C, 1102, "bc76647d6dc27ce40c9742402fc03ed2a819c12381e489ab7057d04d78fc0350", ((0x00034500, 0x00034902), (0x00034930, 0x0003497C))),
    _function(0x00034B54, 0x00034CB0, 348, "7de0e5fef3708a2c06e6e16bef351fe723e61b819276be35ba110d5ff69a96fe"),
    _function(0x00035772, 0x000357A2, 48, "e005daf5ba730462cffd5647eeb6fdbb90b691bc89dce2f56611dd5aabf22a59"),
    _function(0x00035D6E, 0x00035E32, 196, "4c82c8b34b3a69f614ffd352e9a3c9e86919e62c7face0750c833461be77eaf5"),
    _function(0x00035F44, 0x00035F70, 44, "9dd2cb6879f1b5f3d678d9dcaf218e36907cd7ef527d7fd8deadccb776028268"),
    _function(0x00036408, 0x00036574, 364, "d2cd6481da472aaf79ca79207e390525e94b7eaa4fef2e0ee08941540285ea86"),
    _function(0x00036590, 0x000366FC, 364, "7a5924b07eb3bb6587ae894a0152b69b2197ee0930f5fb4fd4f19c6d08f7a393"),
    _function(0x00036C26, 0x00099110, 262, "aab59ab5cd51f780c64928fb118215cefa6eb8f14a41281c1551669946a6e2fa", ((0x00036C26, 0x00036C30), (0x00099014, 0x00099110))),
    _function(0x00036718, 0x00036732, 26, "7fb828ad9170a236624fe330f63d5c321740288410c83a915a35e4acf6552951"),
    _function(0x000367C4, 0x000368AA, 230, "0bcada5b2fdfa8702e88e5bf486c28bed123c84e2b48390ab1970706a767ac22"),
    _function(0x000368D0, 0x00036970, 160, "91ba9551fce0b826df8eb4d954c6bb590c1d8cc144a17b47fcdabfcb7922b84f"),
    _function(0x00036B58, 0x00036BCC, 116, "ba00c3b4c2d6677380a1bf43573682283af819568ed8d25e26aea26a8290e718"),
    _function(0x00036EB4, 0x00036EFC, 72, "abf8aff9149e240c87c36f5d33af86959cbbdaf11b8ebbbca1ec1a5dee22597f"),
    _function(0x000372B0, 0x00037386, 214, "d42e8a809fc6c16c0df39783e113a365b4ba6f2cb8b9db5d3450a13fed506c54"),
    _function(0x0003754A, 0x0003754C, 2, "3c6bb99d72288bf7d4dcf28669fdeef032b9a16faab9095ded29c043ebd51700"),
    _function(0x00037DB4, 0x00037DEC, 56, "e322aa6ed078ea9c84cc684d9758e5f8f656bfb17be1096727db12b72ebbb18d"),
    _function(0x00037F54, 0x00038022, 206, "8cd4d7d36fd358edd5a25a9d2fd9636902b103814ad1b7cf69e342505cb3b346"),
    _function(0x0003F740, 0x0003F7E8, 168, "efe2cb3b2ae59e287b7e948f7ecd9d0e8f4612b86d7c0bc71ff895763239b11e"),
    _function(0x0003F7F8, 0x0003F89C, 164, "abe91fc6bfcd8277c5573b71c7fd511b62e4daa2d6f75b6f74cc79cecb2d8764"),
    _function(0x00041F4C, 0x0004201E, 210, "6ee6ddb1e09b54f6d640ded96ea636db0119d669314d240bcc4fa44c13c1727c"),
    _function(0x00042024, 0x00042108, 228, "453623b4de393024f19251144049340696db4eb6fee357d3b1260c0f27a91aba"),
    _function(0x0004304C, 0x0004307E, 50, "f390e0eb9e709092226073abf52b4b7e76d1f1458e307417e6a725f0ef8aa8e1"),
    _function(0x0004387C, 0x00043B2A, 686, "079e62118ecb45b7a5545d1889e7943d4263f5149253e69f96e92b00209877c9"),
    _function(0x0005CDF8, 0x0005CE8E, 150, "67ad7f343df2a0662bcd65403c955bf8e704a7590a0d7b1a381d21cdf0171b82"),
    _function(0x0005CEA8, 0x0005CED0, 40, "a4d6962fcf8fbe9c078b0186a103aa32551968b7d3ff0f16f14754b3ae904037"),
    _function(0x0005D01C, 0x0005D1AC, 400, "638dc3ae58fba04273b97f5834e9dbd0ab8acc08527c0db825f1120f08b5b70f"),
    _function(0x0005D5D0, 0x0005D5E0, 16, "f5593105ef89c79e14844da61a044b23755966034f31b5d549e61718d5f7d7c9"),
    _function(0x000617F8, 0x00061C44, 1100, "a546d7866e50baeeb61ed62cb90172e426ab93ace3928134208d4ac0d4263d6f"),
    _function(0x00061EF2, 0x00061F02, 16, "c34ae5a795c5f6a04f806f527e596560214ce655f41d7141cbcd635aa5df7204"),
    _function(0x00061F04, 0x00061F8E, 138, "e0e711289689f0266de39b97bce843174679214bbbe109afd55d48451db2c769"),
    _function(0x00061FEA, 0x00062000, 22, "a52fecd7188f73087ad80b3f768ff1d1060d4c8c10cbfe6d655523425edbee73"),
    _function(0x000662DA, 0x000662EA, 16, "e50595fbf68829ccf50181bd9f6e2a00430eb5e9ad78df504792582742bd535c"),
    _function(0x000663B4, 0x0006642C, 120, "ef0c41fa7d06a3a1c9a91a603a261b221d07a6885c388bf0ec063fdb8fb9613f"),
    _function(0x00066430, 0x00066452, 34, "6a9a6f8e99f80cc577aa227fd11c559b64a6daff10cf59683ff1ffbba6519d8c"),
    _function(0x00066470, 0x00092984, 68, "3f2d225b2cce845d3757627009dd9e2102bbf2485ed0da0c23eba4bb343a9245", ((0x00066470, 0x0006648C), (0x0009295C, 0x00092984))),
    _function(0x00066494, 0x000664F0, 92, "3a9cb3cf974e22b9954bd751f1f966fc71848f973d4820895e5184851c4a59da"),
    _function(0x0006652A, 0x00066560, 54, "f04c89f9664605d7fc5619773ec133d2a19ce2f1bf8181c2c8974dc356a7e993"),
    _function(0x00066560, 0x000665A0, 64, "a7e0ef16a686c3e1861a5a21bc74a0f1f13aa340574474e47824588994c8c505"),
    _function(0x00066608, 0x000666A2, 154, "31f6f949131e3043076d9738e7a0a56968a4a935e8fb722e7653e828bcaf8c04"),
    _function(0x0006671C, 0x000928CA, 266, "90de9c418583f14db5701083be7b3041f16eb759186ccec9a71e74260c28cc7d", ((0x0006671C, 0x000667BA), (0x0009285E, 0x000928CA))),
    _function(0x000668A4, 0x000668D6, 50, "cb3828527fc04a0ceb3a8d4adbe0b79fbdb1a2edcde22f1936a1051a6895e869"),
    _function(0x00066C18, 0x00066C48, 48, "5e7830a0d540589f832bd29a0a912f1b41718142ba470a1c216c125403d5de40"),
    _function(0x0006C6A8, 0x0006CC02, 1370, "400fd57d9c750bef559ccbc41301602007192f79f8cc13cebadd528795011d2c"),
    _function(0x0006CCC0, 0x0006D098, 984, "bab60e2e6fdbd5958cac9cd00efc6f13ec921e6af437ea9af500a9a84cd95d7c"),
    _function(0x0006EB94, 0x0006EC14, 128, "fc0c411a07eb55ee1f1428cbbd1f2bd2973745d49979c1f4d8d33948fc13a5a3"),
    _function(0x0006FDE0, 0x0006FE16, 54, "e72f647e3dd3f7c49ad9a43709431728049ee071efbbfa7150e4c20882d5be74"),
    _function(0x000708F8, 0x00070AEA, 498, "4745061192d0a2f917fc248783366631f72a451e42c2905a4b22704ef93740b5"),
    _function(0x000739A8, 0x00073E08, 1120, "bebf02c21566df78fc923c003b9c296083641f1c4d35a7e5ed5e908993c0772b"),
    _function(0x0007400C, 0x0007405C, 80, "8e512a9057dad09c6e64cb9f353c8dbe4ec7a1c23a8432177cef9eb2e8fb7fca"),
    _function(0x0007405C, 0x0007412C, 208, "12c3a0c808e08c1f7da7e37c2a9e68fd8155cfaa243eb5f636d2b44bfcec73b5"),
    _function(0x000742E4, 0x0007487E, 1426, "5e9af846a05aaee97a362d4b37c034a4d914c70c448aa206ca486120ca128997", ((0x000742E4, 0x000747B4), (0x000747BC, 0x0007487E))),
    _function(0x00074AA4, 0x00074AA8, 4, "06936d0536d64e86c623270163a043c1b484bbc978af8fbf56cd1650cbfb6587"),
    _function(0x00074A20, 0x00074A98, 120, "61f972049745685b7d904d44d1e4a3ee90c8e0f6183052a0a0908b792ea9ca4c"),
    _function(0x00074B44, 0x00074BD4, 144, "4601cf0eb18977f2e39e981a4772fd0ec6c53d24fe07d65b480f1f3a2f87517e"),
    _function(0x00074C6C, 0x00074C8A, 30, "a0e429fbedac3cf956c04e4de5639e9e5844a71b3c8d9a2c0a2b0d0ad9cc5dcf"),
    _function(0x00074C90, 0x00074C94, 4, "06936d0536d64e86c623270163a043c1b484bbc978af8fbf56cd1650cbfb6587"),
    _function(0x00074CB4, 0x00074CD6, 34, "19c814be0a5cea685bdccfe62fb60f3a4b0ae84742ffd7fcb9a61445ae218c19"),
    _function(0x00074CE4, 0x00074D02, 30, "24c1b5e11fc2eda22cbd3bb0e786a2a5ef94513939778248292da18085cc3cfe"),
    _function(0x00075E1C, 0x00075F5A, 318, "1fde480764a5001d5e150bfcb909bae10e1100095e48360a2ad25986d64b7201"),
    _function(0x000768B8, 0x00076A44, 396, "b6f75be28ee093792341fb32c8268cc244544825bd7fda42c1eca5e9fd4ecafc"),
    _function(0x0007DD18, 0x0007DD52, 58, "7e19e7a5b2600011c0102e23006788b2cb80ba545bdda8a19729c8291e3f9396"),
    _function(0x00085CA4, 0x00085CBA, 22, "04668193125893e7982e9a488b76f3d94f56d8198e81781f4ae56b6ca9b5869b"),
    _function(0x000876C8, 0x00087A6C, 932, "7dec1022bd53800d5023c0922403a25581fa07a7bf419cf82a6f55b38a265d93"),
    _function(0x000928CA, 0x000928CC, 2, "23edb5b5af45e9490920bc4d068ce5836ebe10c64d6134b01ce11a831e358b87"),
    _function(0x000929D6, 0x00092A04, 46, "b894095fe1a1fd73113ccdd740f22687ec59f3e2e29907357f96ff5a1ba5c6ee"),
    _function(0x00092B68, 0x00092B94, 44, "5bad915aeeed2dd2e13e3bd3c680f6770efcf382d1be4432072ab798c6913e8f"),
    _function(0x00095B04, 0x00095B1A, 22, "c92c4558a496d32c933d09a658b162e9eba992244f68d04c5150b0612b2679f2"),
    _function(0x00099010, 0x00099014, 4, "52a4fc091a8e5ce8b3b6724c5c1480453c2faf469ae9da6cf31ceca48837184a"),
)


def _wrapper(entry: int, sha256: str) -> dict[str, Any]:
    item = _function(entry, entry + 16, 16, sha256)
    item.update(
        role="dlCom graph-builder table wrapper",
        inventory="manual_provenance_supplement",
    )
    return item


# Ghidra omitted these three valid Thumb functions even though their odd
# pointers are present in the exact dispatcher table and each wrapper directly
# invokes 0x000742E4 before returning.
GOODIX_SPO2_DLCOM_WRAPPERS = (
    _wrapper(0x0003007E, "b0fc7c9b1e8a17ab8df57f7f5fabe58cb459ee83706dd8983bac7e7a1df17ffc"),
    _wrapper(0x00038050, "3acba21493cf30ca238d8c4ee8961c87049df180325f23b883fbdff5204ddc9c"),
    _wrapper(0x000417F0, "6fdb26420fafc865cc4f0643d7182c426cfb1a9f126cf32852adb5ae70c017e5"),
)

GOODIX_SPO2_DLCOM_ALL_FUNCTIONS = tuple(sorted(
    GOODIX_SPO2_DLCOM_FUNCTIONS + GOODIX_SPO2_DLCOM_WRAPPERS,
    key=lambda item: int(item["entry"]),
))


def _body(image: bytes, function: dict[str, Any]) -> bytes:
    return b"".join(
        image[int(start) - LOAD_BASE:int(end) - LOAD_BASE]
        for start, end in function["segments"]
    )


def summarize(image_path: Path) -> dict[str, object]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected application image SHA-256: {digest}")

    entries = tuple(int(item["entry"]) for item in GOODIX_SPO2_DLCOM_ALL_FUNCTIONS)
    entry_digest = hashlib.sha256(b"".join(
        entry.to_bytes(4, "little") for entry in entries
    )).hexdigest()
    if entry_digest != EXPECTED_ENTRY_SET_SHA256:
        raise ValueError("Goodix GH_SPO2/dlCom entry set changed")

    output = []
    bodies = []
    callmap = []
    for function in GOODIX_SPO2_DLCOM_ALL_FUNCTIONS:
        entry = int(function["entry"])
        body = _body(image, function)
        if len(body) != int(function["size"]) or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise ValueError(f"Goodix GH_SPO2/dlCom body changed at 0x{entry:08x}")
        bodies.append(body)
        calls = tuple(address for address, _ in direct_thumb_branches_to(
            image, LOAD_BASE, entry))
        callmap.append([f"0x{entry:08x}", [f"0x{x:08x}" for x in calls]])
        output.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{int(function['end_exclusive']):08x}",
            "callsites": [f"0x{address:08x}" for address in calls],
            "segments": [
                {
                    "start": f"0x{start:08x}",
                    "end_exclusive": f"0x{end:08x}",
                    "size": end - start,
                }
                for start, end in function["segments"]
            ],
        })

    body_digest = hashlib.sha256(b"".join(bodies)).hexdigest()
    callmap_digest = hashlib.sha256(json.dumps(
        callmap, separators=(",", ":")
    ).encode()).hexdigest()
    if body_digest != EXPECTED_BODY_SET_SHA256 or \
            callmap_digest != EXPECTED_CALLMAP_SHA256:
        raise ValueError("Goodix GH_SPO2/dlCom aggregate boundary changed")

    table = image[0x000BCF58 - LOAD_BASE:0x000BCF74 - LOAD_BASE]
    expected_table = bytes.fromhex(
        "1dd00500518003007f000300f1170400000000000000000000000000"
    )
    if table != expected_table:
        raise ValueError("Goodix dlCom dispatcher table changed")

    recurrent_pointer = int.from_bytes(
        image[0x00074A98 - LOAD_BASE:0x00074A9C - LOAD_BASE], "little"
    )
    if recurrent_pointer != 0x000739A9:
        raise ValueError("Goodix dlCom recurrent-layer callback pointer changed")
    recurrent_chain = {
        0x0006EB94: (0x0006EC86,),
        0x0002F624: (0x0006EC00,),
        0x00036C26: (0x0002F650,),
        0x00074A20: (0x000340D2, 0x000340FE, 0x0003411A, 0x000990AE),
    }
    for target, expected_calls in recurrent_chain.items():
        calls = tuple(address for address, _ in direct_thumb_branches_to(
            image, LOAD_BASE, target
        ))
        if calls != expected_calls:
            raise ValueError(
                f"Goodix dlCom recurrent-runtime chain changed at 0x{target:08x}"
            )

    # The otherwise unregistered 0x000617F8 graph executor and the admitted
    # 0x000742E4 builder load the same generated-model configuration object.
    # The inner 0x000876C8 executor is reachable only from 0x000617F8 and
    # directly selects the admitted Goodix runtime callback through
    # 0x00074C90. These are ownership edges, not private symbol claims.
    for address in (0x00061C44, 0x000747B8):
        actual = int.from_bytes(
            image[address - LOAD_BASE:address - LOAD_BASE + 4], "little"
        )
        if actual != 0x000BD668:
            raise ValueError(
                f"Goodix dlCom model-config literal changed at 0x{address:08x}"
            )
    neural_layer_calls = tuple(address for address, _ in direct_thumb_branches_to(
        image, LOAD_BASE, 0x000876C8
    ))
    if neural_layer_calls != (
        0x00061956, 0x000619E2, 0x00061B1E, 0x00061B56, 0x00061B8E,
    ):
        raise ValueError("Goodix dlCom dormant neural-layer callsites changed")
    callback_calls = tuple(address for address, _ in direct_thumb_branches_to(
        image, LOAD_BASE, 0x00074C90
    ))
    if 0x000878B2 not in callback_calls:
        raise ValueError("Goodix dlCom dormant provider callback edge changed")

    # A raw Thumb-BL scan finds 0x0003007A as an apparent caller of 0x617F8,
    # but that address is inside the literal pool immediately preceding the
    # real table-selected function at 0x0003007E. Pin the bytes so it cannot be
    # mistaken for product reachability. No raw 0x617F8/0x617F9 word exists in
    # the application image either.
    if image[0x00030078 - LOAD_BASE:0x0003007E - LOAD_BASE] != bytes.fromhex(
        "009b31f0bdbb"
    ):
        raise ValueError("Goodix dlCom dormant-executor literal pool changed")
    if any(
        value.to_bytes(4, "little") in image for value in (0x000617F8, 0x000617F9)
    ):
        raise ValueError("Goodix dlCom dormant executor gained a raw entry pointer")

    exact_markers = {
        0x00066814: b"dlCom_pre2exc",
        0x00066829: b"v1.3.0",
        0x00066834: b"c00c91c9",
        0x0006ED48: b"GH_SPO2_pre_pv_v2.1.10.0",
        0x0006ED70: b"277e89de",
        0x0006ED80: b"net_",
        0x0006ED88: b"1f1cf98b",
    }
    for address, expected in exact_markers.items():
        actual = image[address - LOAD_BASE:address - LOAD_BASE + len(expected)]
        if actual != expected:
            raise ValueError(f"Goodix component marker changed at 0x{address:08x}")

    # The existing Goodix-gated input wrapper invokes this diagnostic sibling
    # immediately after the GH_SPO2/dlCom processing root. Its provider input
    # field names and sole direct caller establish ownership without treating
    # the formatter as product telemetry or recreating its callback ABI.
    diagnostic_calls = tuple(address for address, _ in direct_thumb_branches_to(
        image, LOAD_BASE, 0x0006CCC0
    ))
    if diagnostic_calls != (0x0002CA2C,):
        raise ValueError("Goodix GH_SPO2/dlCom diagnostic callsite changed")
    diagnostic_markers = {
        0x0006D0A8: b"alg:mode=%d\n",
        0x0006D128: b"alg:raw_ppg_scale=%d\n",
        0x0006D1E0: b"alg:groy_x=%d,groy_y=%d,groy_z=%d\n\n",
    }
    for address, expected in diagnostic_markers.items():
        actual = image[address - LOAD_BASE:address - LOAD_BASE + len(expected)]
        if actual != expected:
            raise ValueError(
                f"Goodix GH_SPO2/dlCom diagnostic marker changed at 0x{address:08x}"
            )

    ghidra = [item for item in output if item["inventory"] == "ghidra_function"]
    manual = [item for item in output if item["inventory"] == "manual_provenance_supplement"]
    return {
        "analysis": "Goodix GH_SPO2/dlCom processing provider-boundary closure",
        "image": str(image_path),
        "image_sha256": digest,
        "entry_set_sha256": entry_digest,
        "body_set_sha256": body_digest,
        "callmap_sha256": callmap_digest,
        "function_count": len(output),
        "function_bytes": sum(int(item["size"]) for item in output),
        "ghidra_function_count": len(ghidra),
        "ghidra_function_bytes": sum(int(item["size"]) for item in ghidra),
        "manual_supplement_count": len(manual),
        "manual_supplement_bytes": sum(int(item["size"]) for item in manual),
        "functions": output,
        "identity": {
            "component": "Goodix GH_SPO2 and dlCom",
            "existing_provider_entry": "0x0002c944",
            "root_callsite": "0x0002ca24",
            "processing_root": "0x0006c6a8",
            "input_diagnostic_formatter": "0x0006ccc0",
            "input_diagnostic_callsite": "0x0002ca2c",
            "dlcom_version": "v1.3.0",
            "dlcom_hash": "c00c91c9",
            "spo2_version": "v2.1.10.0",
            "spo2_hash": "277e89de",
            "network_hash": "1f1cf98b",
            "dispatcher_table": "0x000bcf58",
            "largest_graph_builder": "0x000742e4",
            "recurrent_executor": "0x000739a8",
            "recurrent_executor_pointer": "0x000739a9",
            "recurrent_pointer_address": "0x00074a98",
            "dormant_graph_executor": "0x000617f8",
            "dormant_neural_layer_executor": "0x000876c8",
            "shared_model_configuration": "0x000bd668",
        },
        "closure": {
            "direct_root_descendants": 56,
            "direct_root_descendant_bytes": 9922,
            "maximum_direct_call_depth": 5,
            "table_selected_builder_entries": [
                "0x0005d01c", "0x0003007e", "0x00038050", "0x000417f0"
            ],
            "shared_runtime_helpers_present": True,
            "outside_caller_exclusivity_claimed": False,
            "toolchain_runtime_and_sensor_heap_excluded": True,
            "recurrent_runtime_function_count": 7,
            "recurrent_runtime_bytes": 2264,
            "dormant_graph_function_count": 2,
            "dormant_graph_bytes": 2032,
            "dormant_graph_product_reachability": False,
            "input_diagnostic_function_count": 1,
            "input_diagnostic_bytes": 984,
        },
        "boundary": {
            "provider_family": "goodix_gh3x2x_candidate",
            "source_disposition": "vendor_source_required_not_redistributable",
            "licensed_provider_required": True,
            "local_algorithm_reimplementation_authorized": False,
            "neural_network_reconstruction_authorized": False,
        },
        "safety": {
            "static_parser_only": True,
            "algorithm_reimplementation_emitted": False,
            "model_weights_emitted": False,
            "live_sensor_access": False,
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))
