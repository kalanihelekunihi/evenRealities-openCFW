from __future__ import annotations

import os

import hashlib
import importlib.util
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
COMPONENT = ROOT / "components" / "bootloader" / "core_overlay"
CONFIG_PATH = COMPONENT / "overlay.json"
BUILDER_PATH = COMPONENT / "build_component.py"
CORE_SOURCE_MANIFEST_PATH = (
    ROOT / "manifests" / "g2-2.2.6.10-core-source.json"
)
OFFICIAL_PATH = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_bootloader.bin"
)

RUN_BASE = 0x00410000
MAIN_BOUNDARY = 0x00438000
STOCK_END = 0x00434477
LITTLEFS_UTIL_MAX_ADDRESS = 0x00410400
LITTLEFS_UTIL_MIN_ADDRESS = 0x00410408
LITTLEFS_UTIL_ALIGNDOWN_ADDRESS = 0x00410410
LITTLEFS_UTIL_ALIGNUP_ADDRESS = 0x0041041C
LITTLEFS_UTIL_NPW2_ADDRESS = 0x00410428
LITTLEFS_UTIL_CTZ_ADDRESS = 0x00410482
LITTLEFS_UTIL_POPC_ADDRESS = 0x00410492
SCMP_ADDRESS = 0x004104BA
SCMP_CALLER_ADDRESS = 0x004116D2
ALLOC_ADDRESS = 0x00410DE8
ALLOC_CALLERS = (
    (0x00413004, "fdf7f0fe"),
    (0x00413988, "fdf72efa"),
    (0x00413D44, "fdf750f8"),
    (0x00413DA6, "fdf71ff8"),
    (0x00414564, "fcf740fc"),
)
ALLOC_DROP_ADDRESS = 0x00410DEE
ALLOC_DROP_CALLERS = (
    (0x00410E82, "fff7b4ff"),
    (0x0041493E, "fcf756fa"),
)
MLIST_REMOVE_ADDRESS = 0x00410DA8
MLIST_REMOVE_CALLERS = (
    (0x0041320A, "fdf7cdfd"),
    (0x00413848, "fdf7aefa"),
)
MLIST_ISOPEN_ADDRESS = 0x00410D8A
MLIST_ISOPEN_CALLERS = (
    (0x00415156, "fbf718fe"),
    (0x0041518C, "fbf7fdfd"),
    (0x004151D0, "fbf7dbfd"),
    (0x0041520C, "fbf7bdfd"),
    (0x00415242, "fbf7a2fd"),
    (0x00415296, "fbf778fd"),
)
MLIST_APPEND_ADDRESS = 0x00410DC4
MLIST_APPEND_CALLERS = (
    (0x004131F8, "fdf7e4fd"),
    (0x004135FA, "fdf7e3fb"),
)
DISK_VERSION_ADDRESS = 0x00410DCC
DISK_VERSION_MAJOR_ADDRESS = 0x00410DD2
DISK_VERSION_MINOR_ADDRESS = 0x00410DDE
ALLOC_LOOKAHEAD_ADDRESS = 0x00410DFE
DISK_VERSION_CALLERS = (
    (0x00414578, "fcf728fc"),
    (0x00414D5A, "fcf737f8"),
)
MSPI_INTERRUPT_CLEAR_ADDRESS = 0x00426506
MSPI_INTERRUPT_CLEAR_CALLERS = (
    (0x0041FE1A, "06f074fb"),
    (0x004203CC, "06f09bf8"),
)
OVERLAY_ADDRESS = 0x00434478
SCMP_TARGET = OVERLAY_ADDRESS
ALLOC_TARGET = 0x0043447C
ALLOC_DROP_TARGET = 0x00434482
DISK_VERSION_TARGET = 0x00434490
MLIST_APPEND_TARGET = 0x00434498
MLIST_REMOVE_TARGET = 0x004344A0
LITTLEFS_UTIL_MAX_TARGET = 0x004344B2
LITTLEFS_UTIL_MIN_TARGET = 0x004344BA
LITTLEFS_UTIL_ALIGNDOWN_TARGET = 0x004344C2
LITTLEFS_UTIL_ALIGNUP_TARGET = 0x004344CA
LITTLEFS_UTIL_NPW2_TARGET = 0x004344D2
LITTLEFS_UTIL_CTZ_TARGET = 0x0043450A
LITTLEFS_UTIL_POPC_TARGET = 0x0043451A
MSPI_INTERRUPT_CLEAR_TARGET = 0x00434544
MLIST_ISOPEN_TARGET = 0x00434574
LITTLEFS_UTIL_FROMLE32_ADDRESS = 0x004104BE
LITTLEFS_UTIL_TOLE32_ADDRESS = 0x004104E0
LITTLEFS_UTIL_FROMBE32_ADDRESS = 0x004104E8
LITTLEFS_UTIL_TOBE32_ADDRESS = 0x0041050A
LITTLEFS_UTIL_FROMLE32_TARGET = 0x00434586
LITTLEFS_UTIL_TOLE32_TARGET = 0x00434588
LITTLEFS_UTIL_FROMBE32_TARGET = 0x0043458A
LITTLEFS_UTIL_TOBE32_TARGET = 0x0043458E
DISK_VERSION_MAJOR_TARGET = 0x00434592
DISK_VERSION_MINOR_TARGET = 0x0043459C
ALLOC_LOOKAHEAD_TARGET = 0x004345A6
EASYLOGGER_GET_LOGGER_TARGET = 0x004345D8
EASYLOGGER_ASSERT_FAILED_TARGET = 0x004345E0
EASYLOGGER_GET_FMT_TARGET = 0x00434664
EASYLOGGER_GET_FMT_U32_TARGET = 0x0043468A
EASYLOGGER_GET_FMT_PTR_TARGET = 0x0043469E
EASYLOGGER_STRCPY_TARGET = 0x004346B2
EASYLOGGER_GET_FMT_ADDRESS = 0x00417AD4
EASYLOGGER_GET_FMT_U32_ADDRESS = 0x00417B48
EASYLOGGER_GET_FMT_PTR_ADDRESS = 0x00417B62
EASYLOGGER_STRCPY_ADDRESS = 0x0041B158
LITTLEFS_TAG_CHUNK_ADDRESS = 0x00410BA8
LITTLEFS_TAG_CHUNK_TARGET = 0x004346E6
LITTLEFS_TAG_ISVALID_ADDRESS = 0x00410B72
LITTLEFS_TAG_ISVALID_TARGET = 0x004346EC
LITTLEFS_TAG_TYPE1_ADDRESS = 0x00410B90
LITTLEFS_TAG_TYPE1_TARGET = 0x004346F2
LITTLEFS_TAG_TYPE3_ADDRESS = 0x00410BA0
LITTLEFS_TAG_TYPE3_TARGET = 0x004346FC
LITTLEFS_TAG_ID_ADDRESS = 0x00410BB8
LITTLEFS_TAG_ID_TARGET = 0x00434702
LITTLEFS_TAG_SIZE_ADDRESS = 0x00410BC0
LITTLEFS_TAG_SIZE_TARGET = 0x00434708
REDIRECT_INIT_ADDRESS = 0x00415590
REDIRECT_INIT_TARGET = 0x00434710
AEABI_MEMSET_ADDRESS = 0x0041560C
AEABI_MEMSET_TARGET = 0x00434824
AEABI_MEMCPY_ADDRESS = 0x0041568C
AEABI_MEMCPY_TARGET = 0x00434830
MEMCMP_ADDRESS = 0x00415758
MEMCMP_TARGET = 0x00434840
CRC32_ADDRESS = 0x004157C0
CRC32_TARGET = 0x00434898
STORE_200270CC_ADDRESS = 0x0041583C
STORE_200270CC_TARGET = 0x004348C4
UDIV10_ADDRESS = 0x00415844
UDIV10_TARGET = 0x004348D0
UDEC_DIGITS_ADDRESS = 0x00415900
UDEC_DIGITS_TARGET = 0x0043493A
SDEC_DIGITS_ADDRESS = 0x00415924
SDEC_DIGITS_TARGET = 0x00434956
HEX_DIGITS_ADDRESS = 0x00415936
HEX_DIGITS_TARGET = 0x0043496A
PARSE_DEC_ADDRESS = 0x0041595C
PARSE_DEC_TARGET = 0x00434982
U64_TO_DEC_ADDRESS = 0x004159A0
U64_TO_DEC_TARGET = 0x004349B2
U64_TO_HEX_ADDRESS = 0x00415A08
U64_TO_HEX_TARGET = 0x004349FC
NULLABLE_STRLEN_ADDRESS = 0x00415A7C
NULLABLE_STRLEN_TARGET = 0x00434A44
REPEAT_CHAR_ADDRESS = 0x00415A94
REPEAT_CHAR_TARGET = 0x00434A58
FLOAT_TO_FIXED_ADDRESS = 0x00415AB6
FLOAT_TO_FIXED_TARGET = 0x00434A78
STRCSPN_ADDRESS = 0x004157F8
STRCSPN_TARGET = 0x0043485C
STRSPN_ADDRESS = 0x0041581A
STRSPN_TARGET = 0x0043487A
OVERLAY_END = 0x00434BB8
LITTLEFS_UTIL_MAX_OFFSET = LITTLEFS_UTIL_MAX_ADDRESS - RUN_BASE
LITTLEFS_UTIL_MIN_OFFSET = LITTLEFS_UTIL_MIN_ADDRESS - RUN_BASE
LITTLEFS_UTIL_ALIGNDOWN_OFFSET = (
    LITTLEFS_UTIL_ALIGNDOWN_ADDRESS - RUN_BASE
)
LITTLEFS_UTIL_ALIGNUP_OFFSET = LITTLEFS_UTIL_ALIGNUP_ADDRESS - RUN_BASE
LITTLEFS_UTIL_NPW2_OFFSET = LITTLEFS_UTIL_NPW2_ADDRESS - RUN_BASE
LITTLEFS_UTIL_CTZ_OFFSET = LITTLEFS_UTIL_CTZ_ADDRESS - RUN_BASE
LITTLEFS_UTIL_POPC_OFFSET = LITTLEFS_UTIL_POPC_ADDRESS - RUN_BASE
LITTLEFS_UTIL_FROMLE32_OFFSET = LITTLEFS_UTIL_FROMLE32_ADDRESS - RUN_BASE
LITTLEFS_UTIL_TOLE32_OFFSET = LITTLEFS_UTIL_TOLE32_ADDRESS - RUN_BASE
LITTLEFS_UTIL_FROMBE32_OFFSET = LITTLEFS_UTIL_FROMBE32_ADDRESS - RUN_BASE
LITTLEFS_UTIL_TOBE32_OFFSET = LITTLEFS_UTIL_TOBE32_ADDRESS - RUN_BASE
SCMP_OFFSET = SCMP_ADDRESS - RUN_BASE
SCMP_CALLER_OFFSET = SCMP_CALLER_ADDRESS - RUN_BASE
ALLOC_OFFSET = ALLOC_ADDRESS - RUN_BASE
ALLOC_DROP_OFFSET = ALLOC_DROP_ADDRESS - RUN_BASE
MLIST_REMOVE_OFFSET = MLIST_REMOVE_ADDRESS - RUN_BASE
MLIST_ISOPEN_OFFSET = MLIST_ISOPEN_ADDRESS - RUN_BASE
MLIST_APPEND_OFFSET = MLIST_APPEND_ADDRESS - RUN_BASE
DISK_VERSION_OFFSET = DISK_VERSION_ADDRESS - RUN_BASE
DISK_VERSION_MAJOR_OFFSET = DISK_VERSION_MAJOR_ADDRESS - RUN_BASE
DISK_VERSION_MINOR_OFFSET = DISK_VERSION_MINOR_ADDRESS - RUN_BASE
ALLOC_LOOKAHEAD_OFFSET = ALLOC_LOOKAHEAD_ADDRESS - RUN_BASE
MSPI_INTERRUPT_CLEAR_OFFSET = MSPI_INTERRUPT_CLEAR_ADDRESS - RUN_BASE
EASYLOGGER_GET_FMT_OFFSET = EASYLOGGER_GET_FMT_ADDRESS - RUN_BASE
EASYLOGGER_GET_FMT_U32_OFFSET = EASYLOGGER_GET_FMT_U32_ADDRESS - RUN_BASE
EASYLOGGER_GET_FMT_PTR_OFFSET = EASYLOGGER_GET_FMT_PTR_ADDRESS - RUN_BASE
EASYLOGGER_STRCPY_OFFSET = EASYLOGGER_STRCPY_ADDRESS - RUN_BASE
REDIRECT_INIT_OFFSET = REDIRECT_INIT_ADDRESS - RUN_BASE
AEABI_MEMSET_OFFSET = AEABI_MEMSET_ADDRESS - RUN_BASE
AEABI_MEMCPY_OFFSET = AEABI_MEMCPY_ADDRESS - RUN_BASE
MEMCMP_OFFSET = MEMCMP_ADDRESS - RUN_BASE
CRC32_OFFSET = CRC32_ADDRESS - RUN_BASE
STORE_200270CC_OFFSET = STORE_200270CC_ADDRESS - RUN_BASE
UDIV10_OFFSET = UDIV10_ADDRESS - RUN_BASE
UDEC_DIGITS_OFFSET = UDEC_DIGITS_ADDRESS - RUN_BASE
SDEC_DIGITS_OFFSET = SDEC_DIGITS_ADDRESS - RUN_BASE
HEX_DIGITS_OFFSET = HEX_DIGITS_ADDRESS - RUN_BASE
PARSE_DEC_OFFSET = PARSE_DEC_ADDRESS - RUN_BASE
U64_TO_DEC_OFFSET = U64_TO_DEC_ADDRESS - RUN_BASE
U64_TO_HEX_OFFSET = U64_TO_HEX_ADDRESS - RUN_BASE
NULLABLE_STRLEN_OFFSET = NULLABLE_STRLEN_ADDRESS - RUN_BASE
REPEAT_CHAR_OFFSET = REPEAT_CHAR_ADDRESS - RUN_BASE
FLOAT_TO_FIXED_OFFSET = FLOAT_TO_FIXED_ADDRESS - RUN_BASE
STRCSPN_OFFSET = STRCSPN_ADDRESS - RUN_BASE
STRSPN_OFFSET = STRSPN_ADDRESS - RUN_BASE
LITTLEFS_TAG_CHUNK_OFFSET = LITTLEFS_TAG_CHUNK_ADDRESS - RUN_BASE
LITTLEFS_TAG_ISVALID_OFFSET = LITTLEFS_TAG_ISVALID_ADDRESS - RUN_BASE
LITTLEFS_TAG_TYPE1_OFFSET = LITTLEFS_TAG_TYPE1_ADDRESS - RUN_BASE
LITTLEFS_TAG_TYPE3_OFFSET = LITTLEFS_TAG_TYPE3_ADDRESS - RUN_BASE
LITTLEFS_TAG_ID_OFFSET = LITTLEFS_TAG_ID_ADDRESS - RUN_BASE
LITTLEFS_TAG_SIZE_OFFSET = LITTLEFS_TAG_SIZE_ADDRESS - RUN_BASE
STOCK_SHA256 = (
    "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
)
PROVIDER_SHA256 = (
    "cb3ea4265d21ae37c0f7ec3671d67440f90cd0f05e3360b472716e69962aeb2d"
)
OVERLAY_SHA256 = (
    "6693a0fec4dfd7c9ba82639de56264a1ba1519768b6aa90b40885092f6fe4913"
)
SCMP_SHA256 = (
    "787fad2973d1b4f1c6c585f29ee07707e6951499c3772a9e8e4e1bc997ba94fe"
)
ALLOC_SHA256 = (
    "74d41d77541fa368dfc90160c9fc3a8dfd62d891ea72f29ef9c115465b71a32c"
)
ALLOC_DROP_STOCK_SHA256 = (
    "55b7d516bb75d425ebbc077729c8c03aef31b93897d422450084cfed8a771f66"
)
ALLOC_DROP_SOURCE_BODY_SHA256 = (
    "e5e78109621631cb174d82b06ba2542dfa669e1919c3d80982ab059844e5c4f8"
)
MLIST_REMOVE_STOCK_SHA256 = (
    "55bb19e48e301285459cecc31d6177555f04d0b41ea3ae3c1ed3225fd357a8bd"
)
MLIST_REMOVE_SOURCE_BODY_SHA256 = (
    "bb4d51fd66c1638dae0c38615feffb08286027539aede7f65197306491d44e4f"
)
MLIST_ISOPEN_STOCK_SHA256 = (
    "e4963bfc9db9aa487d15261ebce9dd5b1429c708f6fe78ff47968718821c0c4e"
)
MLIST_ISOPEN_SOURCE_BODY_SHA256 = (
    "9b7caac591f8aea5d0eff0dc2b5ff7ff15ba85ab156ba5f95d47b1e4181db489"
)
MLIST_ISOPEN_SOURCE_SHA256 = (
    "7d0bc398c8ecd85fd00b34cc6dcc2b9fc75c754e1aed0bfbca01dd58ae9d6e0c"
)
LITTLEFS_UTIL_ENDIAN_SOURCE_SHA256 = (
    "830d49b043181d270ac0aedda432c5e232ce8d6ce65e8e537b80b1a706fd6cac"
)
LITTLEFS_UTIL_IDENTITY_SOURCE_SHA256 = (
    "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"
)
LITTLEFS_UTIL_SWAP_SOURCE_SHA256 = (
    "7a8f0cc1ae130c65908d3dbd4e89f7c7bd898743a4ee62deced9203383df3d11"
)
MLIST_APPEND_SHA256 = (
    "e3ed290e4e62fc9cce34b0530080dbc08efbca65f80ca1b7d182e18bb20c24b9"
)
DISK_VERSION_STOCK_SHA256 = (
    "1ff8f5ac86a29e52674a91191c4ed763fe635aed200e701063e8224aa15c3870"
)
DISK_VERSION_SOURCE_BODY_SHA256 = (
    "72eba3f48315967708b8128a1c2c9b4273ac363d25ec821bb9a03ea58ed9ce24"
)
ALLOC_LOOKAHEAD_STOCK_SHA256 = (
    "58285c138461a673be0bed2c5376f8d739e40e2aea753ad05d5061bfbc9265cf"
)
ALLOC_LOOKAHEAD_SOURCE_BODY_SHA256 = (
    "bd8e7c926d98a940f215cd41a2fb5932bfbf1abcf7378839dcadd537ae55324d"
)
MSPI_INTERRUPT_CLEAR_STOCK_SHA256 = (
    "4b01a25a8075cf158eb59da277f8730e36c751ee01c67bae86bc172ec877bd48"
)
MSPI_INTERRUPT_CLEAR_SOURCE_SHA256 = (
    "87505e035fa5fe7c0dfd7c4d85b66c6b8f3b57ced45dc7afd787db6c52b0fd7b"
)
LITTLEFS_UTIL_MAX_SOURCE_SHA256 = (
    "00cbab254132bf12554d58b011edf1b5e3b1e36ff5d55a671d2ab04e5b8428a5"
)
LITTLEFS_UTIL_MIN_SOURCE_SHA256 = (
    "36bb5e2d905d59628b5170a2cfecbf56f3200abb3207bfa30b50eaf3b4b44ab4"
)
LITTLEFS_UTIL_ALIGNDOWN_SOURCE_SHA256 = (
    "965ce09e34fe2ef897bc091faf02f8211bf344c025d769cf440c747fb5f555ee"
)
LITTLEFS_UTIL_ALIGNUP_SOURCE_SHA256 = (
    "bd71bfb42c8823db97acf83f489ed0e97d581e3742a1f754c4048298de1c4e71"
)
LITTLEFS_UTIL_MAX_STOCK_SHA256 = (
    "3caa49d8a68e47b2cd91fcb01cae26b6262c904e8b96d8b3ba35f7fb33d07464"
)
LITTLEFS_UTIL_MIN_STOCK_SHA256 = (
    "7ec81166f84c44a60f4ecf93ad37d93f52ec00c77bb5db5a7dda659b1319c8a3"
)
LITTLEFS_UTIL_ALIGNDOWN_STOCK_SHA256 = (
    "d0d7407bcf93abaef33623047467d1230d2176ce9b4a4e93bfcd8adde884f349"
)
LITTLEFS_UTIL_ALIGNUP_STOCK_SHA256 = (
    "18874b0eb5cf5c7bd6f20b2b29f787157294b9e9be16d14ab0d9064d44a97c37"
)
PROVIDER_CRC32C_MSB = 0x9698B4C4


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "open_cfw_bootloader_core_overlay_builder",
        BUILDER_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load bootloader core-overlay builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_ACTIVE_PROFILE = os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang"


@unittest.skipUnless(
    _ACTIVE_PROFILE == "apple-clang",
    "byte-exact Apple-clang reference suite; Linux (linux-clang) byte "
    "reproduction is verified end-to-end by tests/test_toolchain_profiles.py",
)
class BootloaderCoreOverlayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder()
        cls.config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        cls.official = OFFICIAL_PATH.read_bytes()
        cls.temporary = tempfile.TemporaryDirectory()
        cls.output = Path(cls.temporary.name) / "first"
        cls.report = cls.builder.build(
            root=ROOT,
            config_path=CONFIG_PATH,
            output_dir=cls.output,
            clang=os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
        )
        cls.provider = (cls.output / "ota_s200_bootloader.bin").read_bytes()
        cls.overlay = (cls.output / "bootloader_core_overlay.bin").read_bytes()
        cls.contract = json.loads(
            (cls.output / "provider-contract.json").read_text(encoding="utf-8")
        )
        cls.core_source_manifest = json.loads(
            CORE_SOURCE_MANIFEST_PATH.read_text(encoding="utf-8")
        )

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay
        import open_cfw

        cls.apollo_overlay = apollo_overlay
        cls.open_cfw = open_cfw

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_authenticated_raw_layout_and_headroom(self) -> None:
        self.assertEqual(len(self.official), 148599)
        self.assertEqual(hashlib.sha256(self.official).hexdigest(), STOCK_SHA256)
        self.assertEqual(RUN_BASE + len(self.official), STOCK_END)
        self.assertEqual(MAIN_BOUNDARY - STOCK_END, 0x3B89)

        initial_sp, reset_vector = struct.unpack_from("<II", self.official, 0)
        self.assertEqual(initial_sp, 0x2007FB00)
        self.assertEqual(reset_vector, 0x0043291B)
        self.assertEqual(self.config["preamble_bytes"], 0)
        self.assertTrue(self.report["overlay"]["raw_provider"])
        self.assertEqual(self.report["overlay"]["internal_header_bytes"], 0)

    def test_overlay_compiles_to_exact_upstream_leaves(self) -> None:
        self.assertEqual(
            self.overlay[:350],
            bytes.fromhex(
                "401a7047"
                "c16e01667047"
                "0021c1658165c16e01667047"
                "00bf"
                "0048704701000200"
                "826a0a6081627047"
                "28300246006818b18842fad1006810607047"
                "884250ea81807047"
                "884250ea31807047"
                "b0fbf1f048437047"
                "08440138fff7f8bf"
                "10b5013800230024010c18bf1021c840"
                "0022ff2888bf0823d8400f2888bf0424"
                "e040032888bf0222d04041ea50001843"
                "20431043013010bd"
                "80b5414208400130fff7deff013880bd"
                "4ff0553101ea5001401a4ff0333101ea9"
                "00120f0cc3008444ff0013100eb101020"
                "f0f0304843000e7047"
                "78b10268084b22f07e429a4209d14068"
                "064a02eb0030c0f80812d0f804020020"
                "70470220704700bfbebebe0100000640"
                "28b1884204bf012070470068f8e700207047"
                "7047704700ba704700ba7047"
                "80b5fff77cff000c80bd"
                "80b5fff777ff80b280bd"
                "10b5426dc46e836d891a2144b1fbf4f2"
                "02fb1411994209d2406e01f007020123"
                "c90803fa02f2435c1a434254002010bd"
            ),
        )
        self.assertEqual(hashlib.sha256(self.overlay).hexdigest(), OVERLAY_SHA256)
        self.assertEqual(
            self.report["overlay"]["functions"]["open_cfw_littlefs_scmp"],
            {"offset": 0, "size": 4},
        )
        self.assertEqual(
            self.report["overlay"]["functions"][
                "open_cfw_littlefs_alloc_ckpoint"
            ],
            {"offset": 4, "size": 6},
        )
        self.assertEqual(
            self.report["overlay"]["functions"][
                "open_cfw_littlefs_alloc_drop"
            ],
            {"offset": 10, "size": 12},
        )
        self.assertEqual(
            self.report["overlay"]["functions"][
                "open_cfw_littlefs_disk_version"
            ],
            {"offset": 24, "size": 8},
        )
        self.assertEqual(
            self.report["overlay"]["functions"][
                "open_cfw_littlefs_mlist_append"
            ],
            {"offset": 32, "size": 8},
        )
        self.assertEqual(
            self.report["overlay"]["functions"][
                "open_cfw_littlefs_mlist_remove"
            ],
            {"offset": 40, "size": 18},
        )
        self.assertEqual(
            self.report["overlay"]["functions"][
                "open_cfw_littlefs_util_max"
            ],
            {"offset": 58, "size": 8},
        )
        self.assertEqual(
            self.report["overlay"]["functions"][
                "open_cfw_littlefs_util_min"
            ],
            {"offset": 66, "size": 8},
        )
        self.assertEqual(
            self.report["overlay"]["functions"][
                "open_cfw_littlefs_util_aligndown"
            ],
            {"offset": 74, "size": 8},
        )
        self.assertEqual(
            self.report["overlay"]["functions"][
                "open_cfw_littlefs_util_alignup"
            ],
            {"offset": 82, "size": 8},
        )
        self.assertEqual(
            self.report["overlay"]["functions"][
                "open_cfw_littlefs_util_npw2"
            ],
            {"offset": 90, "size": 56},
        )
        self.assertEqual(
            self.report["overlay"]["functions"][
                "open_cfw_littlefs_util_ctz"
            ],
            {"offset": 146, "size": 16},
        )
        self.assertEqual(
            self.report["overlay"]["functions"][
                "open_cfw_littlefs_util_popc"
            ],
            {"offset": 162, "size": 42},
        )
        self.assertEqual(
            self.report["overlay"]["functions"][
                "am_hal_mspi_interrupt_clear"
            ],
            {"offset": 204, "size": 48},
        )
        self.assertEqual(
            self.report["overlay"]["functions"][
                "open_cfw_littlefs_mlist_isopen"
            ],
            {"offset": 252, "size": 18},
        )
        endian_functions = {
            name: self.report["overlay"]["functions"][name]
            for name in (
                "open_cfw_littlefs_util_fromle32",
                "open_cfw_littlefs_util_tole32",
                "open_cfw_littlefs_util_frombe32",
                "open_cfw_littlefs_util_tobe32",
            )
        }
        self.assertEqual(
            endian_functions,
            {
                "open_cfw_littlefs_util_fromle32": {
                    "offset": 270,
                    "size": 2,
                },
                "open_cfw_littlefs_util_tole32": {
                    "offset": 272,
                    "size": 2,
                },
                "open_cfw_littlefs_util_frombe32": {
                    "offset": 274,
                    "size": 4,
                },
                "open_cfw_littlefs_util_tobe32": {
                    "offset": 278,
                    "size": 4,
                },
            },
        )
        self.assertEqual(
            self.report["overlay"]["functions"][
                "open_cfw_littlefs_alloc_lookahead"
            ],
            {"offset": 302, "size": 48},
        )
        self.assertEqual(
            {
                name: self.report["overlay"]["functions"][name]
                for name in (
                    "open_cfw_easylogger_helpers_get_logger",
                    "open_cfw_easylogger_helpers_assert_failed",
                    "open_cfw_easylogger_get_fmt_enabled",
                    "open_cfw_easylogger_get_fmt_used_and_enabled_u32",
                    "open_cfw_easylogger_get_fmt_used_and_enabled_ptr",
                    "open_cfw_easylogger_strcpy",
                )
            },
            {
                "open_cfw_easylogger_helpers_get_logger": {
                    "offset": 352,
                    "size": 8,
                },
                "open_cfw_easylogger_helpers_assert_failed": {
                    "offset": 360,
                    "size": 132,
                },
                "open_cfw_easylogger_get_fmt_enabled": {
                    "offset": 492,
                    "size": 38,
                },
                "open_cfw_easylogger_get_fmt_used_and_enabled_u32": {
                    "offset": 530,
                    "size": 20,
                },
                "open_cfw_easylogger_get_fmt_used_and_enabled_ptr": {
                    "offset": 550,
                    "size": 20,
                },
                "open_cfw_easylogger_strcpy": {
                    "offset": 570,
                    "size": 52,
                },
            },
        )
        self.assertEqual(
            self.report["overlay"]["functions"][
                "open_cfw_littlefs_tag_chunk"
            ],
            {"offset": 622, "size": 6},
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[:4]).hexdigest(),
            SCMP_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[4:10]).hexdigest(),
            ALLOC_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[10:22]).hexdigest(),
            ALLOC_DROP_SOURCE_BODY_SHA256,
        )
        self.assertEqual(self.overlay[22:24], bytes.fromhex("00bf"))
        self.assertEqual(
            hashlib.sha256(self.overlay[24:32]).hexdigest(),
            DISK_VERSION_SOURCE_BODY_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[32:40]).hexdigest(),
            MLIST_APPEND_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[40:58]).hexdigest(),
            MLIST_REMOVE_SOURCE_BODY_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[58:66]).hexdigest(),
            LITTLEFS_UTIL_MAX_SOURCE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[66:74]).hexdigest(),
            LITTLEFS_UTIL_MIN_SOURCE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[74:82]).hexdigest(),
            LITTLEFS_UTIL_ALIGNDOWN_SOURCE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[82:90]).hexdigest(),
            LITTLEFS_UTIL_ALIGNUP_SOURCE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[90:146]).hexdigest(),
            (
                "1048afe6eb2c306231e410f0a864ab5b"
                "fab3c9b0567e1fba6ec61f8bae53094a"
            ),
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[146:162]).hexdigest(),
            (
                "a5616df42c6d3705e9906d0cdce4d6d5"
                "b59d0f02b647c59efeb6594c64004ab1"
            ),
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[162:204]).hexdigest(),
            (
                "e537e00ef37eced668a9d421f28e84d54"
                "a2b6ea09ea1cfda00f96ec1d65891f7"
            ),
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[204:252]).hexdigest(),
            MSPI_INTERRUPT_CLEAR_SOURCE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[252:270]).hexdigest(),
            MLIST_ISOPEN_SOURCE_BODY_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[270:272]).hexdigest(),
            LITTLEFS_UTIL_IDENTITY_SOURCE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[272:274]).hexdigest(),
            LITTLEFS_UTIL_IDENTITY_SOURCE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[274:278]).hexdigest(),
            LITTLEFS_UTIL_SWAP_SOURCE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[278:282]).hexdigest(),
            LITTLEFS_UTIL_SWAP_SOURCE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[302:350]).hexdigest(),
            ALLOC_LOOKAHEAD_SOURCE_BODY_SHA256,
        )
        self.assertEqual(self.overlay[350:352], b"\x00\x00")
        easylogger_leaf_hashes = {
            (352, 360): (
                "3f32a69299002872bb9364f79744be13"
                "11bcb8bce47f24f43558806931990064"
            ),
            (360, 492): (
                "f57622ddc7fdbe8555760ca15bf049b8"
                "fb68abfb3203aa290500e22bbbf82b7a"
            ),
            (492, 530): (
                "8d2909984779762c0abf28369b018b99"
                "b4b30f8d23391fe8670e57f43a166697"
            ),
            (530, 550): (
                "7663e51e49d8c5099f140e85a2f898c"
                "64083a0f02d1574db69294745ee8e5a93"
            ),
            (550, 570): (
                "b5f581ef33404949889812a73244d6b5"
                "c7807ad5707074228a188df7d89ad898"
            ),
            (570, 622): (
                "d19a927665be77d79bd2df6a64575431"
                "db8962aa023f0546f5c3fe5f47805752"
            ),
        }
        for (start, end), expected_hash in easylogger_leaf_hashes.items():
            with self.subTest(easylogger_leaf=f"{start}:{end}"):
                self.assertEqual(
                    hashlib.sha256(self.overlay[start:end]).hexdigest(),
                    expected_hash,
                )
        load, store, return_ = struct.unpack("<HHH", self.overlay[4:10])
        self.assertEqual((load >> 6 & 0x1F) * 4, 0x6C)
        self.assertEqual((store >> 6 & 0x1F) * 4, 0x60)
        self.assertEqual(return_, 0x4770)
        (
            zero,
            first_zero_store,
            second_zero_store,
            drop_load,
            drop_store,
            drop_return,
        ) = struct.unpack("<HHHHHH", self.overlay[10:22])
        self.assertEqual(zero, 0x2100)
        self.assertEqual(
            (
                (first_zero_store >> 6 & 0x1F) * 4,
                (second_zero_store >> 6 & 0x1F) * 4,
            ),
            (0x5C, 0x58),
        )
        self.assertEqual((drop_load >> 6 & 0x1F) * 4, 0x6C)
        self.assertEqual((drop_store >> 6 & 0x1F) * 4, 0x60)
        self.assertEqual(drop_return, 0x4770)
        disk_load, disk_return, disk_version = struct.unpack(
            "<HHI",
            self.overlay[24:32],
        )
        self.assertEqual(disk_load, 0x4800)
        self.assertEqual(disk_return, 0x4770)
        self.assertEqual(disk_version, 0x00020001)
        append_load, append_next, append_head, append_return = struct.unpack(
            "<HHHH",
            self.overlay[32:40],
        )
        self.assertEqual(
            (append_load, append_next, append_head, append_return),
            (0x6A82, 0x600A, 0x6281, 0x4770),
        )
        self.assertEqual(self.overlay[40:44], bytes.fromhex("28300246"))
        self.assertEqual(self.overlay[56:58], bytes.fromhex("7047"))
        link = self.report["overlay"]["link"]
        self.assertEqual(link["text_size"], 204)
        self.assertEqual(link["rodata_size"], 0)
        self.assertEqual(link["resolved_relocation_count"], 2)
        self.assertEqual(
            link["resolved_relocations"],
            [
                {
                    "section": ".rel.text",
                    "site": 86,
                    "symbol": "open_cfw_littlefs_util_aligndown",
                    "type": 30,
                },
                {
                    "section": ".rel.text",
                    "site": 154,
                    "symbol": "open_cfw_littlefs_util_npw2",
                    "type": 10,
                }
            ],
        )
        self.assertEqual(link["isolated_text_size"], 78)
        self.assertEqual(link["isolated_padding_size"], 0)
        self.assertEqual(
            link["isolated_functions"],
            [
                {
                    "function": "am_hal_mspi_interrupt_clear",
                    "offset": 204,
                    "size": 48,
                    "alignment": 4,
                    "padding_before": 0,
                },
                {
                    "function": "open_cfw_littlefs_mlist_isopen",
                    "offset": 252,
                    "size": 18,
                    "alignment": 2,
                    "padding_before": 0,
                },
                {
                    "function": "open_cfw_littlefs_util_fromle32",
                    "offset": 270,
                    "size": 2,
                    "alignment": 2,
                    "padding_before": 0,
                },
                {
                    "function": "open_cfw_littlefs_util_tole32",
                    "offset": 272,
                    "size": 2,
                    "alignment": 2,
                    "padding_before": 0,
                },
                {
                    "function": "open_cfw_littlefs_util_frombe32",
                    "offset": 274,
                    "size": 4,
                    "alignment": 2,
                    "padding_before": 0,
                },
                {
                    "function": "open_cfw_littlefs_util_tobe32",
                    "offset": 278,
                    "size": 4,
                    "alignment": 2,
                    "padding_before": 0,
                },
            ],
        )
        self.assertEqual(link["relocated_text_size"], 1424)
        self.assertEqual(link["relocated_rodata_size"], 143)
        self.assertEqual(link["relocated_padding_size"], 7)
        self.assertEqual(
            link["relocated_functions"],
            [
                {
                    "function": "open_cfw_littlefs_disk_version_major",
                    "offset": 282,
                    "size": 10,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00434592,
                    "runtime_address_hex": "0x00434592",
                },
                {
                    "function": "open_cfw_littlefs_disk_version_minor",
                    "offset": 292,
                    "size": 10,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x0043459C,
                    "runtime_address_hex": "0x0043459C",
                },
                {
                    "function": "open_cfw_littlefs_alloc_lookahead",
                    "offset": 302,
                    "size": 48,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x004345A6,
                    "runtime_address_hex": "0x004345A6",
                },
                {
                    "function": "open_cfw_easylogger_helpers_get_logger",
                    "offset": 352,
                    "size": 8,
                    "alignment": 4,
                    "padding_before": 2,
                    "runtime_address": 0x004345D8,
                    "runtime_address_hex": "0x004345D8",
                },
                {
                    "function": "open_cfw_easylogger_helpers_assert_failed",
                    "offset": 360,
                    "size": 132,
                    "alignment": 4,
                    "padding_before": 0,
                    "runtime_address": 0x004345E0,
                    "runtime_address_hex": "0x004345E0",
                },
                {
                    "function": "open_cfw_easylogger_get_fmt_enabled",
                    "offset": 492,
                    "size": 38,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00434664,
                    "runtime_address_hex": "0x00434664",
                },
                {
                    "function": (
                        "open_cfw_easylogger_get_fmt_used_and_enabled_u32"
                    ),
                    "offset": 530,
                    "size": 20,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x0043468A,
                    "runtime_address_hex": "0x0043468A",
                },
                {
                    "function": (
                        "open_cfw_easylogger_get_fmt_used_and_enabled_ptr"
                    ),
                    "offset": 550,
                    "size": 20,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x0043469E,
                    "runtime_address_hex": "0x0043469E",
                },
                {
                    "function": "open_cfw_easylogger_strcpy",
                    "offset": 570,
                    "size": 52,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x004346B2,
                    "runtime_address_hex": "0x004346B2",
                },
                {
                    "function": "open_cfw_littlefs_tag_chunk",
                    "offset": 622,
                    "size": 6,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x004346E6,
                    "runtime_address_hex": "0x004346E6",
                },
                {
                    "function": "open_cfw_littlefs_tag_isvalid",
                    "offset": 628,
                    "size": 6,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x004346EC,
                    "runtime_address_hex": "0x004346EC",
                },
                {
                    "function": "open_cfw_littlefs_tag_type1",
                    "offset": 634,
                    "size": 10,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x004346F2,
                    "runtime_address_hex": "0x004346F2",
                },
                {
                    "function": "open_cfw_littlefs_tag_type3",
                    "offset": 644,
                    "size": 6,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x004346FC,
                    "runtime_address_hex": "0x004346FC",
                },
                {
                    "function": "open_cfw_littlefs_tag_id",
                    "offset": 650,
                    "size": 6,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00434702,
                    "runtime_address_hex": "0x00434702",
                },
                {
                    "function": "open_cfw_littlefs_tag_size",
                    "offset": 656,
                    "size": 6,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00434708,
                    "runtime_address_hex": "0x00434708",
                },
                {
                    "function": "open_cfw_bootloader_redirect_init",
                    "offset": 664,
                    "size": 275,
                    "text_size": 132,
                    "alignment": 4,
                    "padding_before": 2,
                    "runtime_address": 0x00434710,
                    "runtime_address_hex": "0x00434710",
                },
                {
                    "function": "open_cfw_bootloader_aeabi_memset",
                    "offset": 940,
                    "size": 12,
                    "alignment": 2,
                    "padding_before": 1,
                    "runtime_address": 0x00434824,
                    "runtime_address_hex": "0x00434824",
                },
                {
                    "function": "open_cfw_bootloader_aeabi_memcpy",
                    "offset": 952,
                    "size": 16,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00434830,
                    "runtime_address_hex": "0x00434830",
                },
                {
                    "function": "open_cfw_bootloader_memcmp",
                    "offset": 968,
                    "size": 28,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00434840,
                    "runtime_address_hex": "0x00434840",
                },
                {
                    "function": "open_cfw_bootloader_strcspn",
                    "offset": 996,
                    "size": 30,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x0043485C,
                    "runtime_address_hex": "0x0043485C",
                },
                {
                    "function": "open_cfw_bootloader_strspn",
                    "offset": 1026,
                    "size": 28,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x0043487A,
                    "runtime_address_hex": "0x0043487A",
                },
                {
                    "function": "open_cfw_bootloader_crc32",
                    "offset": 1056,
                    "size": 44,
                    "alignment": 4,
                    "padding_before": 2,
                    "runtime_address": 0x00434898,
                    "runtime_address_hex": "0x00434898",
                },
                {
                    "function": "open_cfw_bootloader_store_200270cc",
                    "offset": 1100,
                    "size": 12,
                    "alignment": 4,
                    "padding_before": 0,
                    "runtime_address": 0x004348C4,
                    "runtime_address_hex": "0x004348C4",
                },
                {
                    "function": "open_cfw_bootloader_udiv10",
                    "offset": 1112,
                    "size": 106,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x004348D0,
                    "runtime_address_hex": "0x004348D0",
                },
                {
                    "function": "open_cfw_bootloader_udec_digits",
                    "offset": 1218,
                    "size": 28,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x0043493A,
                    "runtime_address_hex": "0x0043493A",
                },
                {
                    "function": "open_cfw_bootloader_sdec_digits",
                    "offset": 1246,
                    "size": 20,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00434956,
                    "runtime_address_hex": "0x00434956",
                },
                {
                    "function": "open_cfw_bootloader_hex_digits",
                    "offset": 1266,
                    "size": 24,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x0043496A,
                    "runtime_address_hex": "0x0043496A",
                },
                {
                    "function": "open_cfw_bootloader_parse_dec",
                    "offset": 1290,
                    "size": 48,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00434982,
                    "runtime_address_hex": "0x00434982",
                },
                {
                    "function": "open_cfw_bootloader_u64_to_dec",
                    "offset": 1338,
                    "size": 74,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x004349B2,
                    "runtime_address_hex": "0x004349B2",
                },
                {
                    "function": "open_cfw_bootloader_u64_to_hex",
                    "offset": 1412,
                    "size": 72,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x004349FC,
                    "runtime_address_hex": "0x004349FC",
                },
                {
                    "function": "open_cfw_bootloader_nullable_strlen",
                    "offset": 1484,
                    "size": 20,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00434A44,
                    "runtime_address_hex": "0x00434A44",
                },
                {
                    "function": "open_cfw_bootloader_repeat_char",
                    "offset": 1504,
                    "size": 32,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00434A58,
                    "runtime_address_hex": "0x00434A58",
                },
                {
                    "function": "open_cfw_bootloader_float_to_fixed",
                    "offset": 1536,
                    "size": 320,
                    "alignment": 8,
                    "padding_before": 0,
                    "runtime_address": 0x00434A78,
                    "runtime_address_hex": "0x00434A78",
                },
            ],
        )

    def test_exact_declared_mutation_set(self) -> None:
        self.assertEqual(len(self.provider), 150456)
        self.assertEqual(
            hashlib.sha256(self.provider).hexdigest(),
            PROVIDER_SHA256,
        )

        changed = [
            offset
            for offset, (stock, generated) in enumerate(
                zip(self.official, self.provider)
            )
            if stock != generated
        ]
        self.assertEqual(
            changed,
            list(
                range(
                    LITTLEFS_UTIL_MAX_OFFSET,
                    LITTLEFS_UTIL_ALIGNDOWN_OFFSET + 6,
                )
            )
            + list(
                range(
                    LITTLEFS_UTIL_ALIGNDOWN_OFFSET + 7,
                    LITTLEFS_UTIL_ALIGNUP_OFFSET + 12,
                )
            )
            + list(
                range(
                    LITTLEFS_UTIL_NPW2_OFFSET,
                    LITTLEFS_UTIL_NPW2_OFFSET + 14,
                )
            )
            + list(
                range(
                    LITTLEFS_UTIL_NPW2_OFFSET + 15,
                    LITTLEFS_UTIL_NPW2_OFFSET + 16,
                )
            )
            + list(
                range(
                    LITTLEFS_UTIL_NPW2_OFFSET + 17,
                    LITTLEFS_UTIL_NPW2_OFFSET + 34,
                )
            )
            + list(
                range(
                    LITTLEFS_UTIL_NPW2_OFFSET + 35,
                    LITTLEFS_UTIL_NPW2_OFFSET + 36,
                )
            )
            + list(
                range(
                    LITTLEFS_UTIL_NPW2_OFFSET + 37,
                    LITTLEFS_UTIL_NPW2_OFFSET + 52,
                )
            )
            + list(
                range(
                    LITTLEFS_UTIL_NPW2_OFFSET + 53,
                    LITTLEFS_UTIL_NPW2_OFFSET + 54,
                )
            )
            + list(
                range(
                    LITTLEFS_UTIL_NPW2_OFFSET + 55,
                    LITTLEFS_UTIL_NPW2_OFFSET + 70,
                )
            )
            + list(
                range(
                    LITTLEFS_UTIL_NPW2_OFFSET + 71,
                    LITTLEFS_UTIL_NPW2_OFFSET + 72,
                )
            )
            + list(
                range(
                    LITTLEFS_UTIL_NPW2_OFFSET + 73,
                    LITTLEFS_UTIL_NPW2_OFFSET + 90,
                )
            )
            + list(
                range(
                    LITTLEFS_UTIL_CTZ_OFFSET,
                    LITTLEFS_UTIL_CTZ_OFFSET + 16,
                )
            )
            + list(
                range(
                    LITTLEFS_UTIL_POPC_OFFSET,
                    LITTLEFS_UTIL_POPC_OFFSET + 36,
                )
            )
            + list(
                range(
                    LITTLEFS_UTIL_POPC_OFFSET + 37,
                    LITTLEFS_UTIL_POPC_OFFSET + 40,
                )
            )
            + list(range(SCMP_OFFSET, SCMP_OFFSET + 4))
            + list(
                range(
                    LITTLEFS_UTIL_FROMLE32_OFFSET,
                    LITTLEFS_UTIL_FROMLE32_OFFSET + 4,
                )
            )
            + list(
                range(
                    LITTLEFS_UTIL_FROMLE32_OFFSET + 5,
                    LITTLEFS_UTIL_FROMBE32_OFFSET + 4,
                )
            )
            + list(
                range(
                    LITTLEFS_UTIL_FROMBE32_OFFSET + 5,
                    LITTLEFS_UTIL_FROMBE32_OFFSET + 10,
                )
            )
            + list(
                range(
                    LITTLEFS_UTIL_FROMBE32_OFFSET + 11,
                    LITTLEFS_UTIL_TOBE32_OFFSET + 8,
                )
            )
            + list(
                range(
                    LITTLEFS_TAG_ISVALID_OFFSET,
                    LITTLEFS_TAG_ISVALID_OFFSET + 10,
                )
            )
            + list(
                range(
                    LITTLEFS_TAG_TYPE1_OFFSET,
                    LITTLEFS_TAG_TYPE1_OFFSET + 8,
                )
            )
            + list(
                range(
                    LITTLEFS_TAG_TYPE3_OFFSET,
                    LITTLEFS_TAG_TYPE3_OFFSET + 8,
                )
            )
            + list(
                range(
                    LITTLEFS_TAG_CHUNK_OFFSET,
                    LITTLEFS_TAG_CHUNK_OFFSET + 6,
                )
            )
            + list(
                range(
                    LITTLEFS_TAG_ID_OFFSET,
                    LITTLEFS_TAG_ID_OFFSET + 8,
                )
            )
            + list(
                range(
                    LITTLEFS_TAG_SIZE_OFFSET,
                    LITTLEFS_TAG_SIZE_OFFSET + 6,
                )
            )
            + list(range(MLIST_ISOPEN_OFFSET, MLIST_ISOPEN_OFFSET + 4))
            + list(
                range(
                    MLIST_ISOPEN_OFFSET + 5,
                    MLIST_ISOPEN_OFFSET + 10,
                )
            )
            + list(
                range(
                    MLIST_ISOPEN_OFFSET + 11,
                    MLIST_ISOPEN_OFFSET + 22,
                )
            )
            + list(
                range(
                    MLIST_ISOPEN_OFFSET + 23,
                    MLIST_ISOPEN_OFFSET + 24,
                )
            )
            + list(
                range(
                    MLIST_ISOPEN_OFFSET + 25,
                    MLIST_ISOPEN_OFFSET + 30,
                )
            )
            + list(range(MLIST_REMOVE_OFFSET, MLIST_REMOVE_OFFSET + 4))
            + list(
                range(
                    MLIST_REMOVE_OFFSET + 5,
                    MLIST_REMOVE_OFFSET + 10,
                )
            )
            + list(
                range(
                    MLIST_REMOVE_OFFSET + 11,
                    MLIST_REMOVE_OFFSET + 22,
                )
            )
            + list(
                range(
                    MLIST_REMOVE_OFFSET + 23,
                    DISK_VERSION_OFFSET + 6,
                )
            )
            + list(
                range(
                    DISK_VERSION_MAJOR_OFFSET,
                    DISK_VERSION_MAJOR_OFFSET + 6,
                )
            )
            + list(
                range(
                    DISK_VERSION_MAJOR_OFFSET + 7,
                    DISK_VERSION_MINOR_OFFSET + 10,
                )
            )
            + list(range(ALLOC_OFFSET, ALLOC_OFFSET + 6))
            + list(range(ALLOC_DROP_OFFSET, ALLOC_DROP_OFFSET + 6))
            + list(range(ALLOC_DROP_OFFSET + 7, ALLOC_DROP_OFFSET + 16))
            + list(
                range(
                    ALLOC_LOOKAHEAD_OFFSET,
                    ALLOC_LOOKAHEAD_OFFSET + 50,
                )
            )
            + list(
                range(
                    ALLOC_LOOKAHEAD_OFFSET + 51,
                    ALLOC_LOOKAHEAD_OFFSET + 56,
                )
            )
            + list(range(REDIRECT_INIT_OFFSET, REDIRECT_INIT_OFFSET + 4))
            + list(range(REDIRECT_INIT_OFFSET + 5, REDIRECT_INIT_OFFSET + 14))
            + list(range(REDIRECT_INIT_OFFSET + 15, REDIRECT_INIT_OFFSET + 24))
            + list(range(REDIRECT_INIT_OFFSET + 25, REDIRECT_INIT_OFFSET + 30))
            + list(range(REDIRECT_INIT_OFFSET + 31, REDIRECT_INIT_OFFSET + 42))
            + list(range(REDIRECT_INIT_OFFSET + 43, REDIRECT_INIT_OFFSET + 70))
            + list(range(REDIRECT_INIT_OFFSET + 71, REDIRECT_INIT_OFFSET + 84))
            + list(range(REDIRECT_INIT_OFFSET + 85, REDIRECT_INIT_OFFSET + 88))
            + list(range(AEABI_MEMSET_OFFSET, AEABI_MEMSET_OFFSET + 23))
            + list(range(AEABI_MEMSET_OFFSET + 25, AEABI_MEMSET_OFFSET + 29))
            + list(range(AEABI_MEMSET_OFFSET + 30, AEABI_MEMSET_OFFSET + 45))
            + list(range(AEABI_MEMSET_OFFSET + 46, AEABI_MEMSET_OFFSET + 55))
            + list(range(AEABI_MEMSET_OFFSET + 56, AEABI_MEMSET_OFFSET + 61))
            + list(range(AEABI_MEMSET_OFFSET + 62, AEABI_MEMSET_OFFSET + 69))
            + list(range(AEABI_MEMSET_OFFSET + 70, AEABI_MEMSET_OFFSET + 75))
            + list(range(AEABI_MEMSET_OFFSET + 77, AEABI_MEMSET_OFFSET + 87))
            + list(range(AEABI_MEMSET_OFFSET + 89, AEABI_MEMSET_OFFSET + 95))
            + list(range(AEABI_MEMSET_OFFSET + 97, AEABI_MEMSET_OFFSET + 102))
            + list(range(AEABI_MEMCPY_OFFSET, AEABI_MEMCPY_OFFSET + 12))
            + list(range(AEABI_MEMCPY_OFFSET + 13, AEABI_MEMCPY_OFFSET + 16))
            + list(range(AEABI_MEMCPY_OFFSET + 17, AEABI_MEMCPY_OFFSET + 30))
            + list(range(AEABI_MEMCPY_OFFSET + 32, AEABI_MEMCPY_OFFSET + 55))
            + list(range(AEABI_MEMCPY_OFFSET + 56, AEABI_MEMCPY_OFFSET + 65))
            + list(range(AEABI_MEMCPY_OFFSET + 66, AEABI_MEMCPY_OFFSET + 77))
            + list(range(AEABI_MEMCPY_OFFSET + 78, AEABI_MEMCPY_OFFSET + 87))
            + list(range(AEABI_MEMCPY_OFFSET + 88, AEABI_MEMCPY_OFFSET + 126))
            + list(range(AEABI_MEMCPY_OFFSET + 127, AEABI_MEMCPY_OFFSET + 140))
            + list(range(AEABI_MEMCPY_OFFSET + 141, AEABI_MEMCPY_OFFSET + 147))
            + list(range(AEABI_MEMCPY_OFFSET + 148, AEABI_MEMCPY_OFFSET + 153))
            + list(range(AEABI_MEMCPY_OFFSET + 154, AEABI_MEMCPY_OFFSET + 158))
            + list(range(AEABI_MEMCPY_OFFSET + 159, AEABI_MEMCPY_OFFSET + 166))
            + list(range(MEMCMP_OFFSET, MEMCMP_OFFSET + 13))
            + list(range(MEMCMP_OFFSET + 14, MEMCMP_OFFSET + 39))
            + list(range(MEMCMP_OFFSET + 40, MEMCMP_OFFSET + 56))
            + list(range(MEMCMP_OFFSET + 57, MEMCMP_OFFSET + 67))
            + list(range(MEMCMP_OFFSET + 68, MEMCMP_OFFSET + 70))
            + list(range(MEMCMP_OFFSET + 71, MEMCMP_OFFSET + 73))
            + list(range(MEMCMP_OFFSET + 74, MEMCMP_OFFSET + 81))
            + list(range(MEMCMP_OFFSET + 82, MEMCMP_OFFSET + 99))
            + list(range(MEMCMP_OFFSET + 100, MEMCMP_OFFSET + 104))
            + list(range(CRC32_OFFSET, CRC32_OFFSET + 56))
            + list(range(STRCSPN_OFFSET, STRCSPN_OFFSET + 4))
            + list(range(STRCSPN_OFFSET + 5, STRCSPN_OFFSET + 16))
            + list(range(STRCSPN_OFFSET + 17, STRCSPN_OFFSET + 34))
            + list(range(STRSPN_OFFSET, STRSPN_OFFSET + 4))
            + list(range(STRSPN_OFFSET + 5, STRSPN_OFFSET + 34))
            + list(range(STORE_200270CC_OFFSET, STORE_200270CC_OFFSET + 8))
            + list(range(UDIV10_OFFSET, UDIV10_OFFSET + 86))
            + list(range(UDIV10_OFFSET + 87, UDIV10_OFFSET + 128))
            + [UDIV10_OFFSET + 129]
            + list(range(UDIV10_OFFSET + 131, UDIV10_OFFSET + 174))
            + list(range(UDIV10_OFFSET + 175, UDIV10_OFFSET + 182))
            + list(range(UDIV10_OFFSET + 183, UDIV10_OFFSET + 188))
            + list(range(UDEC_DIGITS_OFFSET, UDEC_DIGITS_OFFSET + 6))
            + list(range(UDEC_DIGITS_OFFSET + 7, UDEC_DIGITS_OFFSET + 10))
            + list(range(UDEC_DIGITS_OFFSET + 11, UDEC_DIGITS_OFFSET + 24))
            + list(range(UDEC_DIGITS_OFFSET + 25, UDEC_DIGITS_OFFSET + 28))
            + list(range(UDEC_DIGITS_OFFSET + 29, UDEC_DIGITS_OFFSET + 36))
            + list(range(SDEC_DIGITS_OFFSET, SDEC_DIGITS_OFFSET + 18))
            + list(range(HEX_DIGITS_OFFSET, HEX_DIGITS_OFFSET + 4))
            + list(range(HEX_DIGITS_OFFSET + 5, HEX_DIGITS_OFFSET + 8))
            + list(range(HEX_DIGITS_OFFSET + 9, HEX_DIGITS_OFFSET + 16))
            + list(range(HEX_DIGITS_OFFSET + 17, HEX_DIGITS_OFFSET + 26))
            + list(range(HEX_DIGITS_OFFSET + 27, HEX_DIGITS_OFFSET + 30))
            + list(range(HEX_DIGITS_OFFSET + 31, HEX_DIGITS_OFFSET + 38))
            + list(range(PARSE_DEC_OFFSET, PARSE_DEC_OFFSET + 4))
            + [PARSE_DEC_OFFSET + 5, PARSE_DEC_OFFSET + 7]
            + list(range(PARSE_DEC_OFFSET + 9, PARSE_DEC_OFFSET + 48))
            + [PARSE_DEC_OFFSET + 49]
            + list(range(PARSE_DEC_OFFSET + 51, PARSE_DEC_OFFSET + 56))
            + list(range(PARSE_DEC_OFFSET + 57, PARSE_DEC_OFFSET + 68))
            + list(range(U64_TO_DEC_OFFSET, U64_TO_DEC_OFFSET + 12))
            + [U64_TO_DEC_OFFSET + 13]
            + list(range(U64_TO_DEC_OFFSET + 15, U64_TO_DEC_OFFSET + 34))
            + list(range(U64_TO_DEC_OFFSET + 35, U64_TO_DEC_OFFSET + 42))
            + list(range(U64_TO_DEC_OFFSET + 43, U64_TO_DEC_OFFSET + 64))
            + list(range(U64_TO_DEC_OFFSET + 65, U64_TO_DEC_OFFSET + 68))
            + list(range(U64_TO_DEC_OFFSET + 69, U64_TO_DEC_OFFSET + 74))
            + list(range(U64_TO_DEC_OFFSET + 75, U64_TO_DEC_OFFSET + 90))
            + list(range(U64_TO_DEC_OFFSET + 91, U64_TO_DEC_OFFSET + 94))
            + list(range(U64_TO_DEC_OFFSET + 95, U64_TO_DEC_OFFSET + 104))
            + list(range(U64_TO_HEX_OFFSET, U64_TO_HEX_OFFSET + 4))
            + [U64_TO_HEX_OFFSET + 5]
            + list(range(U64_TO_HEX_OFFSET + 7, U64_TO_HEX_OFFSET + 10))
            + list(range(U64_TO_HEX_OFFSET + 11, U64_TO_HEX_OFFSET + 46))
            + list(range(U64_TO_HEX_OFFSET + 47, U64_TO_HEX_OFFSET + 62))
            + list(range(U64_TO_HEX_OFFSET + 63, U64_TO_HEX_OFFSET + 70))
            + list(range(U64_TO_HEX_OFFSET + 71, U64_TO_HEX_OFFSET + 74))
            + [U64_TO_HEX_OFFSET + 75]
            + list(range(U64_TO_HEX_OFFSET + 77, U64_TO_HEX_OFFSET + 82))
            + list(range(U64_TO_HEX_OFFSET + 83, U64_TO_HEX_OFFSET + 90))
            + list(range(U64_TO_HEX_OFFSET + 91, U64_TO_HEX_OFFSET + 100))
            + list(range(U64_TO_HEX_OFFSET + 101, U64_TO_HEX_OFFSET + 104))
            + list(range(U64_TO_HEX_OFFSET + 105, U64_TO_HEX_OFFSET + 116))
            + list(range(NULLABLE_STRLEN_OFFSET, NULLABLE_STRLEN_OFFSET + 4))
            + list(range(NULLABLE_STRLEN_OFFSET + 5, NULLABLE_STRLEN_OFFSET + 18))
            + list(range(NULLABLE_STRLEN_OFFSET + 19, NULLABLE_STRLEN_OFFSET + 24))
            + list(range(REPEAT_CHAR_OFFSET, REPEAT_CHAR_OFFSET + 4))
            + list(range(REPEAT_CHAR_OFFSET + 5, REPEAT_CHAR_OFFSET + 12))
            + list(range(REPEAT_CHAR_OFFSET + 13, REPEAT_CHAR_OFFSET + 26))
            + list(range(REPEAT_CHAR_OFFSET + 27, REPEAT_CHAR_OFFSET + 34))
            + list(range(FLOAT_TO_FIXED_OFFSET, FLOAT_TO_FIXED_OFFSET + 44))
            + [FLOAT_TO_FIXED_OFFSET + 45]
            + list(range(FLOAT_TO_FIXED_OFFSET + 47, FLOAT_TO_FIXED_OFFSET + 54))
            + list(range(FLOAT_TO_FIXED_OFFSET + 55, FLOAT_TO_FIXED_OFFSET + 62))
            + [FLOAT_TO_FIXED_OFFSET + 63, FLOAT_TO_FIXED_OFFSET + 65]
            + list(range(FLOAT_TO_FIXED_OFFSET + 67, FLOAT_TO_FIXED_OFFSET + 104))
            + list(range(FLOAT_TO_FIXED_OFFSET + 105, FLOAT_TO_FIXED_OFFSET + 142))
            + [FLOAT_TO_FIXED_OFFSET + 143]
            + list(range(FLOAT_TO_FIXED_OFFSET + 145, FLOAT_TO_FIXED_OFFSET + 154))
            + list(range(FLOAT_TO_FIXED_OFFSET + 155, FLOAT_TO_FIXED_OFFSET + 196))
            + list(range(FLOAT_TO_FIXED_OFFSET + 197, FLOAT_TO_FIXED_OFFSET + 202))
            + list(range(FLOAT_TO_FIXED_OFFSET + 203, FLOAT_TO_FIXED_OFFSET + 212))
            + list(range(FLOAT_TO_FIXED_OFFSET + 213, FLOAT_TO_FIXED_OFFSET + 234))
            + list(range(FLOAT_TO_FIXED_OFFSET + 235, FLOAT_TO_FIXED_OFFSET + 238))
            + list(range(FLOAT_TO_FIXED_OFFSET + 239, FLOAT_TO_FIXED_OFFSET + 308))
            + list(range(FLOAT_TO_FIXED_OFFSET + 309, FLOAT_TO_FIXED_OFFSET + 320))
            + list(
                range(
                    EASYLOGGER_GET_FMT_OFFSET,
                    EASYLOGGER_GET_FMT_OFFSET + 20,
                )
            )
            + list(
                range(
                    EASYLOGGER_GET_FMT_OFFSET + 21,
                    EASYLOGGER_GET_FMT_OFFSET + 46,
                )
            )
            + list(
                range(
                    EASYLOGGER_GET_FMT_OFFSET + 47,
                    EASYLOGGER_GET_FMT_OFFSET + 52,
                )
            )
            + list(
                range(
                    EASYLOGGER_GET_FMT_OFFSET + 53,
                    EASYLOGGER_GET_FMT_OFFSET + 84,
                )
            )
            + list(
                range(
                    EASYLOGGER_GET_FMT_OFFSET + 85,
                    EASYLOGGER_GET_FMT_OFFSET + 98,
                )
            )
            + [EASYLOGGER_GET_FMT_OFFSET + 99]
            + list(
                range(
                    EASYLOGGER_GET_FMT_OFFSET + 101,
                    EASYLOGGER_GET_FMT_OFFSET + 106,
                )
            )
            + list(
                range(
                    EASYLOGGER_GET_FMT_U32_OFFSET,
                    EASYLOGGER_GET_FMT_U32_OFFSET + 12,
                )
            )
            + list(
                range(
                    EASYLOGGER_GET_FMT_U32_OFFSET + 13,
                    EASYLOGGER_GET_FMT_U32_OFFSET + 18,
                )
            )
            + [EASYLOGGER_GET_FMT_U32_OFFSET + 19]
            + list(
                range(
                    EASYLOGGER_GET_FMT_U32_OFFSET + 21,
                    EASYLOGGER_GET_FMT_U32_OFFSET + 26,
                )
            )
            + list(
                range(
                    EASYLOGGER_GET_FMT_PTR_OFFSET,
                    EASYLOGGER_GET_FMT_PTR_OFFSET + 12,
                )
            )
            + list(
                range(
                    EASYLOGGER_GET_FMT_PTR_OFFSET + 13,
                    EASYLOGGER_GET_FMT_PTR_OFFSET + 18,
                )
            )
            + [EASYLOGGER_GET_FMT_PTR_OFFSET + 19]
            + list(
                range(
                    EASYLOGGER_GET_FMT_PTR_OFFSET + 21,
                    EASYLOGGER_GET_FMT_PTR_OFFSET + 26,
                )
            )
            + list(
                range(
                    EASYLOGGER_STRCPY_OFFSET,
                    EASYLOGGER_STRCPY_OFFSET + 12,
                )
            )
            + list(
                range(
                    EASYLOGGER_STRCPY_OFFSET + 13,
                    EASYLOGGER_STRCPY_OFFSET + 20,
                )
            )
            + list(
                range(
                    EASYLOGGER_STRCPY_OFFSET + 21,
                    EASYLOGGER_STRCPY_OFFSET + 42,
                )
            )
            + list(
                range(
                    EASYLOGGER_STRCPY_OFFSET + 43,
                    EASYLOGGER_STRCPY_OFFSET + 48,
                )
            )
            + list(
                range(
                    EASYLOGGER_STRCPY_OFFSET + 49,
                    EASYLOGGER_STRCPY_OFFSET + 70,
                )
            )
            + list(
                range(
                    EASYLOGGER_STRCPY_OFFSET + 71,
                    EASYLOGGER_STRCPY_OFFSET + 78,
                )
            )
            + list(
                range(
                    EASYLOGGER_STRCPY_OFFSET + 79,
                    EASYLOGGER_STRCPY_OFFSET + 100,
                )
            )
            + list(
                range(
                    EASYLOGGER_STRCPY_OFFSET + 101,
                    EASYLOGGER_STRCPY_OFFSET + 106,
                )
            )
            + list(
                range(
                    EASYLOGGER_STRCPY_OFFSET + 107,
                    EASYLOGGER_STRCPY_OFFSET + 140,
                )
            )
            + list(
                range(
                    EASYLOGGER_STRCPY_OFFSET + 141,
                    EASYLOGGER_STRCPY_OFFSET + 162,
                )
            )
            + list(
                range(
                    MSPI_INTERRUPT_CLEAR_OFFSET,
                    MSPI_INTERRUPT_CLEAR_OFFSET + 6,
                )
            )
            + list(
                range(
                    MSPI_INTERRUPT_CLEAR_OFFSET + 7,
                    MSPI_INTERRUPT_CLEAR_OFFSET + 30,
                )
            )
            + list(
                range(
                    MSPI_INTERRUPT_CLEAR_OFFSET + 31,
                    MSPI_INTERRUPT_CLEAR_OFFSET + 38,
                )
            )
            + list(
                range(
                    MSPI_INTERRUPT_CLEAR_OFFSET + 39,
                    MSPI_INTERRUPT_CLEAR_OFFSET + 44,
                )
            )
            + list(
                range(
                    MSPI_INTERRUPT_CLEAR_OFFSET + 45,
                    MSPI_INTERRUPT_CLEAR_OFFSET + 48,
                )
            ),
        )
        utility_stock_expectations = (
            (
                LITTLEFS_UTIL_MAX_OFFSET,
                bytes.fromhex("814200d308007047"),
                LITTLEFS_UTIL_MAX_STOCK_SHA256,
            ),
            (
                LITTLEFS_UTIL_MIN_OFFSET,
                bytes.fromhex("884200d308007047"),
                LITTLEFS_UTIL_MIN_STOCK_SHA256,
            ),
            (
                LITTLEFS_UTIL_ALIGNDOWN_OFFSET,
                bytes.fromhex("b0fbf1f001fb00f108007047"),
                LITTLEFS_UTIL_ALIGNDOWN_STOCK_SHA256,
            ),
            (
                LITTLEFS_UTIL_ALIGNUP_OFFSET,
                bytes.fromhex("80b50818401efff7f5ff02bd"),
                LITTLEFS_UTIL_ALIGNUP_STOCK_SHA256,
            ),
            (
                LITTLEFS_UTIL_NPW2_OFFSET,
                bytes.fromhex(
                    "01000020491eb1f5803f01d3012200e00022d2b21201d140"
                    "1043b1f5807f01d3012200e00022d2b2d200d14010431029"
                    "01d3012200e00022d2b29200d1401043042901d3012200e0"
                    "0022d2b25200d140104350ea5100401c7047"
                ),
                (
                    "291ab0ccd15efe1085ce5bcdc6551581"
                    "ed4eccf67fa84f6560c4500fd68b8b63"
                ),
            ),
            (
                LITTLEFS_UTIL_CTZ_OFFSET,
                bytes.fromhex(
                    "80b541420840401cfff7cdff401e02bd"
                ),
                (
                    "4ae07bfa492e5dfad5869ea491ca43f7"
                    "20e6fc153315a126e2e686313c3de08c"
                ),
            ),
            (
                LITTLEFS_UTIL_POPC_OFFSET,
                bytes.fromhex(
                    "0100490831f0aa31401a30f0cc31800830f0cc30401810eb"
                    "101030f0f0305ff001314843000e7047"
                ),
                (
                    "2cc25090f38dd5c2121cb4bfc7ddf0bd"
                    "71df984312c9b9c52e87feeef5aea872"
                ),
            ),
        )
        for offset, stock, expected_sha256 in utility_stock_expectations:
            with self.subTest(utility_stock_offset=offset):
                self.assertEqual(
                    self.official[offset:offset + len(stock)],
                    stock,
                )
                self.assertEqual(
                    hashlib.sha256(stock).hexdigest(),
                    expected_sha256,
                )
        self.assertEqual(
            self.official[SCMP_OFFSET:SCMP_OFFSET + 4],
            bytes.fromhex("401a7047"),
        )
        self.assertEqual(
            self.official[ALLOC_OFFSET:ALLOC_OFFSET + 6],
            bytes.fromhex("c16e01667047"),
        )
        self.assertEqual(
            self.official[ALLOC_DROP_OFFSET:ALLOC_DROP_OFFSET + 16],
            bytes.fromhex("80b5002181650021c165fff7f6ff01bd"),
        )
        self.assertEqual(
            hashlib.sha256(
                self.official[
                    ALLOC_DROP_OFFSET:ALLOC_DROP_OFFSET + 16
                ]
            ).hexdigest(),
            ALLOC_DROP_STOCK_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(
                self.official[
                    ALLOC_LOOKAHEAD_OFFSET:ALLOC_LOOKAHEAD_OFFSET + 56
                ]
            ).hexdigest(),
            ALLOC_LOOKAHEAD_STOCK_SHA256,
        )
        self.assertEqual(
            self.official[
                MLIST_ISOPEN_OFFSET:MLIST_ISOPEN_OFFSET + 30
            ],
            bytes.fromhex(
                "01b46a4600e012681068002804d01068"
                "8842f8d1012000e0002001b07047"
            ),
        )
        self.assertEqual(
            hashlib.sha256(
                self.official[
                    MLIST_ISOPEN_OFFSET:MLIST_ISOPEN_OFFSET + 30
                ]
            ).hexdigest(),
            MLIST_ISOPEN_STOCK_SHA256,
        )
        self.assertEqual(
            self.official[
                MLIST_REMOVE_OFFSET:MLIST_REMOVE_OFFSET + 28
            ],
            bytes.fromhex(
                "10f1280200e012681068002805d01068"
                "8842f8d11068006810607047"
            ),
        )
        self.assertEqual(
            hashlib.sha256(
                self.official[
                    MLIST_REMOVE_OFFSET:MLIST_REMOVE_OFFSET + 28
                ]
            ).hexdigest(),
            MLIST_REMOVE_STOCK_SHA256,
        )
        self.assertEqual(
            self.official[
                MLIST_APPEND_OFFSET:MLIST_APPEND_OFFSET + 8
            ],
            bytes.fromhex("826a0a6081627047"),
        )
        self.assertEqual(
            hashlib.sha256(
                self.official[
                    MLIST_APPEND_OFFSET:MLIST_APPEND_OFFSET + 8
                ]
            ).hexdigest(),
            MLIST_APPEND_SHA256,
        )
        self.assertEqual(
            self.official[
                DISK_VERSION_OFFSET:DISK_VERSION_OFFSET + 6
            ],
            bytes.fromhex("dff89c087047"),
        )
        self.assertEqual(
            hashlib.sha256(
                self.official[
                    DISK_VERSION_OFFSET:DISK_VERSION_OFFSET + 6
                ]
            ).hexdigest(),
            DISK_VERSION_STOCK_SHA256,
        )
        self.assertEqual(
            self.official[
                MSPI_INTERRUPT_CLEAR_OFFSET:
                MSPI_INTERRUPT_CLEAR_OFFSET + 48
            ],
            bytes.fromhex(
                "0200002806d0006820f07e40dff8f036"
                "984201d002200ae05068b84a12eb0033"
                "c3f8081212eb0032d2f8040200207047"
            ),
        )
        self.assertEqual(
            hashlib.sha256(
                self.official[
                    MSPI_INTERRUPT_CLEAR_OFFSET:
                    MSPI_INTERRUPT_CLEAR_OFFSET + 48
                ]
            ).hexdigest(),
            MSPI_INTERRUPT_CLEAR_STOCK_SHA256,
        )
        allowed = set(
            range(LITTLEFS_UTIL_MAX_OFFSET, LITTLEFS_UTIL_MAX_OFFSET + 8)
        )
        allowed.update(
            range(LITTLEFS_UTIL_MIN_OFFSET, LITTLEFS_UTIL_MIN_OFFSET + 8)
        )
        allowed.update(
            range(
                LITTLEFS_UTIL_ALIGNDOWN_OFFSET,
                LITTLEFS_UTIL_ALIGNDOWN_OFFSET + 12,
            )
        )
        allowed.update(
            range(
                LITTLEFS_UTIL_ALIGNUP_OFFSET,
                LITTLEFS_UTIL_ALIGNUP_OFFSET + 12,
            )
        )
        allowed.update(
            range(
                LITTLEFS_UTIL_NPW2_OFFSET,
                LITTLEFS_UTIL_NPW2_OFFSET + 90,
            )
        )
        allowed.update(
            range(
                LITTLEFS_UTIL_CTZ_OFFSET,
                LITTLEFS_UTIL_CTZ_OFFSET + 16,
            )
        )
        allowed.update(
            range(
                LITTLEFS_UTIL_POPC_OFFSET,
                LITTLEFS_UTIL_POPC_OFFSET + 40,
            )
        )
        allowed.update(range(SCMP_OFFSET, SCMP_OFFSET + 4))
        allowed.update(
            range(
                LITTLEFS_UTIL_FROMLE32_OFFSET,
                LITTLEFS_UTIL_FROMLE32_OFFSET + 34,
            )
        )
        allowed.update(
            range(
                LITTLEFS_UTIL_TOLE32_OFFSET,
                LITTLEFS_UTIL_TOLE32_OFFSET + 8,
            )
        )
        allowed.update(
            range(
                LITTLEFS_UTIL_FROMBE32_OFFSET,
                LITTLEFS_UTIL_FROMBE32_OFFSET + 34,
            )
        )
        allowed.update(
            range(
                LITTLEFS_UTIL_TOBE32_OFFSET,
                LITTLEFS_UTIL_TOBE32_OFFSET + 8,
            )
        )
        allowed.update(
            range(MLIST_ISOPEN_OFFSET, MLIST_ISOPEN_OFFSET + 30)
        )
        allowed.update(
            range(MLIST_REMOVE_OFFSET, MLIST_REMOVE_OFFSET + 28)
        )
        allowed.update(
            range(MLIST_APPEND_OFFSET, MLIST_APPEND_OFFSET + 8)
        )
        allowed.update(
            range(DISK_VERSION_OFFSET, DISK_VERSION_OFFSET + 6)
        )
        allowed.update(
            range(
                DISK_VERSION_MAJOR_OFFSET,
                DISK_VERSION_MAJOR_OFFSET + 12,
            )
        )
        allowed.update(
            range(
                DISK_VERSION_MINOR_OFFSET,
                DISK_VERSION_MINOR_OFFSET + 10,
            )
        )
        allowed.update(range(ALLOC_OFFSET, ALLOC_OFFSET + 6))
        allowed.update(range(ALLOC_DROP_OFFSET, ALLOC_DROP_OFFSET + 16))
        allowed.update(
            range(
                ALLOC_LOOKAHEAD_OFFSET,
                ALLOC_LOOKAHEAD_OFFSET + 56,
            )
        )
        allowed.update(
            range(REDIRECT_INIT_OFFSET, REDIRECT_INIT_OFFSET + 88)
        )
        allowed.update(
            range(AEABI_MEMSET_OFFSET, AEABI_MEMSET_OFFSET + 102)
        )
        allowed.update(
            range(AEABI_MEMCPY_OFFSET, AEABI_MEMCPY_OFFSET + 166)
        )
        allowed.update(range(MEMCMP_OFFSET, MEMCMP_OFFSET + 104))
        allowed.update(range(CRC32_OFFSET, CRC32_OFFSET + 56))
        allowed.update(range(STRCSPN_OFFSET, STRCSPN_OFFSET + 34))
        allowed.update(range(STRSPN_OFFSET, STRSPN_OFFSET + 34))
        allowed.update(range(STORE_200270CC_OFFSET, STORE_200270CC_OFFSET + 8))
        allowed.update(range(UDIV10_OFFSET, UDIV10_OFFSET + 188))
        allowed.update(range(UDEC_DIGITS_OFFSET, UDEC_DIGITS_OFFSET + 36))
        allowed.update(range(SDEC_DIGITS_OFFSET, SDEC_DIGITS_OFFSET + 18))
        allowed.update(range(HEX_DIGITS_OFFSET, HEX_DIGITS_OFFSET + 38))
        allowed.update(range(PARSE_DEC_OFFSET, PARSE_DEC_OFFSET + 68))
        allowed.update(range(U64_TO_DEC_OFFSET, U64_TO_DEC_OFFSET + 104))
        allowed.update(range(U64_TO_HEX_OFFSET, U64_TO_HEX_OFFSET + 116))
        allowed.update(range(NULLABLE_STRLEN_OFFSET, NULLABLE_STRLEN_OFFSET + 24))
        allowed.update(range(REPEAT_CHAR_OFFSET, REPEAT_CHAR_OFFSET + 34))
        allowed.update(range(FLOAT_TO_FIXED_OFFSET, FLOAT_TO_FIXED_OFFSET + 320))
        allowed.update(
            range(
                EASYLOGGER_GET_FMT_OFFSET,
                EASYLOGGER_GET_FMT_OFFSET + 106,
            )
        )
        allowed.update(
            range(
                EASYLOGGER_GET_FMT_U32_OFFSET,
                EASYLOGGER_GET_FMT_U32_OFFSET + 26,
            )
        )
        allowed.update(
            range(
                EASYLOGGER_GET_FMT_PTR_OFFSET,
                EASYLOGGER_GET_FMT_PTR_OFFSET + 26,
            )
        )
        allowed.update(
            range(
                EASYLOGGER_STRCPY_OFFSET,
                EASYLOGGER_STRCPY_OFFSET + 162,
            )
        )
        allowed.update(
            range(
                MSPI_INTERRUPT_CLEAR_OFFSET,
                MSPI_INTERRUPT_CLEAR_OFFSET + 48,
            )
        )
        allowed.update(
            range(
                LITTLEFS_TAG_ISVALID_OFFSET,
                LITTLEFS_TAG_ISVALID_OFFSET + 10,
            )
        )
        allowed.update(
            range(
                LITTLEFS_TAG_TYPE1_OFFSET,
                LITTLEFS_TAG_TYPE1_OFFSET + 8,
            )
        )
        allowed.update(
            range(
                LITTLEFS_TAG_TYPE3_OFFSET,
                LITTLEFS_TAG_TYPE3_OFFSET + 8,
            )
        )
        allowed.update(
            range(
                LITTLEFS_TAG_ID_OFFSET,
                LITTLEFS_TAG_ID_OFFSET + 8,
            )
        )
        allowed.update(
            range(
                LITTLEFS_TAG_SIZE_OFFSET,
                LITTLEFS_TAG_SIZE_OFFSET + 6,
            )
        )
        allowed.update(
            range(
                LITTLEFS_TAG_CHUNK_OFFSET,
                LITTLEFS_TAG_CHUNK_OFFSET + 6,
            )
        )
        for offset, stock in enumerate(self.official):
            if offset not in allowed:
                self.assertEqual(self.provider[offset], stock)
        self.assertEqual(
            self.provider[
                LITTLEFS_UTIL_MAX_OFFSET:LITTLEFS_UTIL_MAX_OFFSET + 8
            ],
            bytes.fromhex("24f057b800bf00bf"),
        )
        self.assertEqual(
            self.provider[
                LITTLEFS_UTIL_MIN_OFFSET:LITTLEFS_UTIL_MIN_OFFSET + 8
            ],
            bytes.fromhex("24f057b800bf00bf"),
        )
        self.assertEqual(
            self.provider[
                LITTLEFS_UTIL_ALIGNDOWN_OFFSET:
                LITTLEFS_UTIL_ALIGNDOWN_OFFSET + 12
            ],
            bytes.fromhex("24f057b800bf00bf00bf00bf"),
        )
        self.assertEqual(
            self.provider[
                LITTLEFS_UTIL_ALIGNUP_OFFSET:
                LITTLEFS_UTIL_ALIGNUP_OFFSET + 12
            ],
            bytes.fromhex("24f055b800bf00bf00bf00bf"),
        )
        self.assertEqual(
            self.provider[
                LITTLEFS_UTIL_NPW2_OFFSET:
                LITTLEFS_UTIL_NPW2_OFFSET + 90
            ],
            bytes.fromhex(
                "24f053b8" + "00bf" * 43
            ),
        )
        self.assertEqual(
            self.provider[
                LITTLEFS_UTIL_CTZ_OFFSET:
                LITTLEFS_UTIL_CTZ_OFFSET + 16
            ],
            bytes.fromhex(
                "24f042b8" + "00bf" * 6
            ),
        )
        self.assertEqual(
            self.provider[
                LITTLEFS_UTIL_POPC_OFFSET:
                LITTLEFS_UTIL_POPC_OFFSET + 40
            ],
            bytes.fromhex(
                "24f042b8" + "00bf" * 18
            ),
        )
        self.assertEqual(
            self.provider[SCMP_OFFSET:SCMP_OFFSET + 4],
            bytes.fromhex("23f0ddbf"),
        )
        self.assertEqual(
            self.provider[
                LITTLEFS_UTIL_FROMLE32_OFFSET:
                LITTLEFS_UTIL_FROMLE32_OFFSET + 34
            ],
            bytes.fromhex(
                "24f062b8"
                "00bf00bf00bf00bf00bf00bf00bf00bf"
                "00bf00bf00bf00bf00bf00bf00bf"
            ),
        )
        self.assertEqual(
            self.provider[
                LITTLEFS_UTIL_TOLE32_OFFSET:
                LITTLEFS_UTIL_TOLE32_OFFSET + 8
            ],
            bytes.fromhex("24f052b800bf00bf"),
        )
        self.assertEqual(
            self.provider[
                LITTLEFS_UTIL_FROMBE32_OFFSET:
                LITTLEFS_UTIL_FROMBE32_OFFSET + 34
            ],
            bytes.fromhex(
                "24f04fb8"
                "00bf00bf00bf00bf00bf00bf00bf00bf"
                "00bf00bf00bf00bf00bf00bf00bf"
            ),
        )
        self.assertEqual(
            self.provider[
                LITTLEFS_UTIL_TOBE32_OFFSET:
                LITTLEFS_UTIL_TOBE32_OFFSET + 8
            ],
            bytes.fromhex("24f040b800bf00bf"),
        )
        self.assertEqual(
            self.provider[ALLOC_OFFSET:ALLOC_OFFSET + 6],
            bytes.fromhex("23f048bb00bf"),
        )
        self.assertEqual(
            self.provider[
                MLIST_ISOPEN_OFFSET:MLIST_ISOPEN_OFFSET + 30
            ],
            bytes.fromhex(
                "23f0f3bb00bf00bf00bf00bf00bf00bf"
                "00bf00bf00bf00bf00bf00bf00bf"
            ),
        )
        self.assertEqual(
            self.provider[
                MLIST_REMOVE_OFFSET:MLIST_REMOVE_OFFSET + 28
            ],
            bytes.fromhex(
                "23f07abb00bf00bf00bf00bf00bf00bf"
                "00bf00bf00bf00bf00bf00bf"
            ),
        )
        self.assertEqual(
            self.provider[
                MLIST_APPEND_OFFSET:MLIST_APPEND_OFFSET + 8
            ],
            bytes.fromhex("23f068bb00bf00bf"),
        )
        self.assertEqual(
            self.provider[
                DISK_VERSION_OFFSET:DISK_VERSION_OFFSET + 6
            ],
            bytes.fromhex("23f060bb00bf"),
        )
        self.assertEqual(
            self.provider[
                DISK_VERSION_MAJOR_OFFSET:DISK_VERSION_MAJOR_OFFSET + 12
            ],
            bytes.fromhex("23f0debb00bf00bf00bf00bf"),
        )
        self.assertEqual(
            self.provider[
                DISK_VERSION_MINOR_OFFSET:DISK_VERSION_MINOR_OFFSET + 10
            ],
            bytes.fromhex("23f0ddbb00bf00bf00bf"),
        )
        self.assertEqual(
            self.provider[
                ALLOC_DROP_OFFSET:ALLOC_DROP_OFFSET + 16
            ],
            bytes.fromhex("23f048bb00bf00bf00bf00bf00bf00bf"),
        )
        self.assertEqual(
            self.provider[
                ALLOC_LOOKAHEAD_OFFSET:ALLOC_LOOKAHEAD_OFFSET + 56
            ],
            bytes.fromhex("23f0d2bb" + "00bf" * 26),
        )
        self.assertEqual(
            self.provider[
                MSPI_INTERRUPT_CLEAR_OFFSET:
                MSPI_INTERRUPT_CLEAR_OFFSET + 48
            ],
            bytes.fromhex(
                "0ef01db8"
                "00bf00bf00bf00bf00bf00bf00bf00bf"
                "00bf00bf00bf00bf00bf00bf00bf00bf"
                "00bf00bf00bf00bf00bf00bf"
            ),
        )
        self.assertEqual(
            self.provider[
                LITTLEFS_TAG_ID_OFFSET:LITTLEFS_TAG_ID_OFFSET + 8
            ],
            bytes.fromhex("23f0a3bd00bf00bf"),
        )
        self.assertEqual(
            self.provider[
                LITTLEFS_TAG_SIZE_OFFSET:LITTLEFS_TAG_SIZE_OFFSET + 6
            ],
            bytes.fromhex("23f0a2bd00bf"),
        )
        self.assertEqual(
            self.provider[
                REDIRECT_INIT_OFFSET:REDIRECT_INIT_OFFSET + 88
            ],
            bytes.fromhex("1ff0beb8" + "00bf" * 42),
        )
        self.assertEqual(
            self.provider[AEABI_MEMCPY_OFFSET:AEABI_MEMCPY_OFFSET + 166],
            bytes.fromhex("1ff0d0b8" + "00bf" * 81),
        )
        self.assertEqual(
            self.provider[MEMCMP_OFFSET:MEMCMP_OFFSET + 104],
            bytes.fromhex("1ff072b8" + "00bf" * 50),
        )
        self.assertEqual(
            self.provider[CRC32_OFFSET:CRC32_OFFSET + 56],
            bytes.fromhex("1ff06ab8" + "00bf" * 26),
        )
        self.assertEqual(
            self.provider[STRCSPN_OFFSET:STRCSPN_OFFSET + 34],
            bytes.fromhex("1ff030b8" + "00bf" * 15),
        )
        self.assertEqual(
            self.provider[STRSPN_OFFSET:STRSPN_OFFSET + 34],
            bytes.fromhex("1ff02eb8" + "00bf" * 15),
        )
        self.assertEqual(
            self.provider[STORE_200270CC_OFFSET:STORE_200270CC_OFFSET + 8],
            bytes.fromhex("1ff042b800bf00bf"),
        )
        self.assertEqual(
            self.provider[UDIV10_OFFSET:UDIV10_OFFSET + 188],
            bytes.fromhex("1ff044b8" + "00bf" * 92),
        )
        self.assertEqual(
            self.provider[UDEC_DIGITS_OFFSET:UDEC_DIGITS_OFFSET + 36],
            bytes.fromhex("1ff01bb8" + "00bf" * 16),
        )
        self.assertEqual(
            self.provider[SDEC_DIGITS_OFFSET:SDEC_DIGITS_OFFSET + 18],
            bytes.fromhex("1ff017b8" + "00bf" * 7),
        )
        self.assertEqual(
            self.provider[HEX_DIGITS_OFFSET:HEX_DIGITS_OFFSET + 38],
            bytes.fromhex("1ff018b8" + "00bf" * 17),
        )
        self.assertEqual(
            self.provider[PARSE_DEC_OFFSET:PARSE_DEC_OFFSET + 68],
            bytes.fromhex("1ff011b8" + "00bf" * 32),
        )
        self.assertEqual(
            self.provider[U64_TO_DEC_OFFSET:U64_TO_DEC_OFFSET + 104],
            bytes.fromhex("1ff007b8" + "00bf" * 50),
        )
        self.assertEqual(
            self.provider[U64_TO_HEX_OFFSET:U64_TO_HEX_OFFSET + 116],
            bytes.fromhex("1ef0f8bf" + "00bf" * 56),
        )
        self.assertEqual(
            self.provider[NULLABLE_STRLEN_OFFSET:NULLABLE_STRLEN_OFFSET + 24],
            bytes.fromhex("1ef0e2bf" + "00bf" * 10),
        )
        self.assertEqual(
            self.provider[REPEAT_CHAR_OFFSET:REPEAT_CHAR_OFFSET + 34],
            bytes.fromhex("1ef0e0bf" + "00bf" * 15),
        )
        self.assertEqual(
            self.provider[FLOAT_TO_FIXED_OFFSET:FLOAT_TO_FIXED_OFFSET + 320],
            bytes.fromhex("1ef0dfbf" + "00bf" * 158),
        )
        self.assertEqual(
            self.provider[len(self.official):],
            b"\x00" + self.overlay,
        )
        component = self.report["component"]
        self.assertEqual(component["generated_patch_site_bytes"], 2398)
        self.assertEqual(component["opaque_base_bytes"], 146201)
        self.assertEqual(component["generated_alignment_bytes"], 8)
        self.assertEqual(
            component["generated_stock_to_overlay_alignment_bytes"],
            1,
        )
        self.assertEqual(component["generated_isolated_alignment_bytes"], 0)
        self.assertEqual(component["generated_relocated_alignment_bytes"], 7)
        self.assertEqual(component["source_owned_bytes"], 1849)

    def test_redirect_and_original_call_edge_round_trip(self) -> None:
        sites = {
            site["name"]: site
            for site in self.report["overlay"]["patched_sites"]
        }
        expectations = (
            (
                "replace_littlefs_util_max",
                LITTLEFS_UTIL_MAX_ADDRESS,
                LITTLEFS_UTIL_MAX_TARGET,
                "24f057b800bf00bf",
                147630,
            ),
            (
                "replace_littlefs_util_min",
                LITTLEFS_UTIL_MIN_ADDRESS,
                LITTLEFS_UTIL_MIN_TARGET,
                "24f057b800bf00bf",
                147630,
            ),
            (
                "replace_littlefs_util_aligndown",
                LITTLEFS_UTIL_ALIGNDOWN_ADDRESS,
                LITTLEFS_UTIL_ALIGNDOWN_TARGET,
                "24f057b800bf00bf00bf00bf",
                147630,
            ),
            (
                "replace_littlefs_util_alignup",
                LITTLEFS_UTIL_ALIGNUP_ADDRESS,
                LITTLEFS_UTIL_ALIGNUP_TARGET,
                "24f055b800bf00bf00bf00bf",
                147626,
            ),
            (
                "replace_littlefs_util_npw2",
                LITTLEFS_UTIL_NPW2_ADDRESS,
                LITTLEFS_UTIL_NPW2_TARGET,
                "24f053b8" + "00bf" * 43,
                147622,
            ),
            (
                "replace_littlefs_util_ctz",
                LITTLEFS_UTIL_CTZ_ADDRESS,
                LITTLEFS_UTIL_CTZ_TARGET,
                "24f042b8" + "00bf" * 6,
                147588,
            ),
            (
                "replace_littlefs_util_popc",
                LITTLEFS_UTIL_POPC_ADDRESS,
                LITTLEFS_UTIL_POPC_TARGET,
                "24f042b8" + "00bf" * 18,
                147588,
            ),
            (
                "replace_littlefs_scmp",
                SCMP_ADDRESS,
                SCMP_TARGET,
                "23f0ddbf",
                147386,
            ),
            (
                "replace_littlefs_util_fromle32",
                LITTLEFS_UTIL_FROMLE32_ADDRESS,
                LITTLEFS_UTIL_FROMLE32_TARGET,
                "24f062b8"
                "00bf00bf00bf00bf00bf00bf00bf00bf"
                "00bf00bf00bf00bf00bf00bf00bf",
                147652,
            ),
            (
                "replace_littlefs_util_tole32",
                LITTLEFS_UTIL_TOLE32_ADDRESS,
                LITTLEFS_UTIL_TOLE32_TARGET,
                "24f052b800bf00bf",
                147620,
            ),
            (
                "replace_littlefs_util_frombe32",
                LITTLEFS_UTIL_FROMBE32_ADDRESS,
                LITTLEFS_UTIL_FROMBE32_TARGET,
                "24f04fb8"
                "00bf00bf00bf00bf00bf00bf00bf00bf"
                "00bf00bf00bf00bf00bf00bf00bf",
                147614,
            ),
            (
                "replace_littlefs_util_tobe32",
                LITTLEFS_UTIL_TOBE32_ADDRESS,
                LITTLEFS_UTIL_TOBE32_TARGET,
                "24f040b800bf00bf",
                147584,
            ),
            (
                "replace_littlefs_tag_isvalid",
                LITTLEFS_TAG_ISVALID_ADDRESS,
                LITTLEFS_TAG_ISVALID_TARGET,
                "23f0bbbd00bf00bf00bf",
                146294,
            ),
            (
                "replace_littlefs_tag_type1",
                LITTLEFS_TAG_TYPE1_ADDRESS,
                LITTLEFS_TAG_TYPE1_TARGET,
                "23f0afbd00bf00bf",
                146270,
            ),
            (
                "replace_littlefs_tag_type3",
                LITTLEFS_TAG_TYPE3_ADDRESS,
                LITTLEFS_TAG_TYPE3_TARGET,
                "23f0acbd00bf00bf",
                146264,
            ),
            (
                "replace_littlefs_tag_id",
                LITTLEFS_TAG_ID_ADDRESS,
                LITTLEFS_TAG_ID_TARGET,
                "23f0a3bd00bf00bf",
                146246,
            ),
            (
                "replace_littlefs_tag_size",
                LITTLEFS_TAG_SIZE_ADDRESS,
                LITTLEFS_TAG_SIZE_TARGET,
                "23f0a2bd00bf",
                146244,
            ),
            (
                "replace_littlefs_tag_chunk",
                LITTLEFS_TAG_CHUNK_ADDRESS,
                LITTLEFS_TAG_CHUNK_TARGET,
                "23f09dbd00bf",
                146234,
            ),
            (
                "replace_littlefs_mlist_isopen",
                MLIST_ISOPEN_ADDRESS,
                MLIST_ISOPEN_TARGET,
                "23f0f3bb00bf00bf00bf00bf00bf00bf"
                "00bf00bf00bf00bf00bf00bf00bf",
                145382,
            ),
            (
                "replace_littlefs_mlist_remove",
                MLIST_REMOVE_ADDRESS,
                MLIST_REMOVE_TARGET,
                "23f07abb00bf00bf00bf00bf00bf00bf"
                "00bf00bf00bf00bf00bf00bf",
                145140,
            ),
            (
                "replace_littlefs_mlist_append",
                MLIST_APPEND_ADDRESS,
                MLIST_APPEND_TARGET,
                "23f068bb00bf00bf",
                145104,
            ),
            (
                "replace_littlefs_disk_version",
                DISK_VERSION_ADDRESS,
                DISK_VERSION_TARGET,
                "23f060bb00bf",
                145088,
            ),
            (
                "replace_littlefs_disk_version_major",
                DISK_VERSION_MAJOR_ADDRESS,
                DISK_VERSION_MAJOR_TARGET,
                "23f0debb00bf00bf00bf00bf",
                145340,
            ),
            (
                "replace_littlefs_disk_version_minor",
                DISK_VERSION_MINOR_ADDRESS,
                DISK_VERSION_MINOR_TARGET,
                "23f0ddbb00bf00bf00bf",
                145338,
            ),
            (
                "replace_littlefs_alloc_ckpoint",
                ALLOC_ADDRESS,
                ALLOC_TARGET,
                "23f048bb00bf",
                145040,
            ),
            (
                "replace_littlefs_alloc_drop",
                ALLOC_DROP_ADDRESS,
                ALLOC_DROP_TARGET,
                "23f048bb00bf00bf00bf00bf00bf00bf",
                145040,
            ),
            (
                "replace_littlefs_alloc_lookahead",
                ALLOC_LOOKAHEAD_ADDRESS,
                ALLOC_LOOKAHEAD_TARGET,
                "23f0d2bb" + "00bf" * 26,
                145316,
            ),
            (
                "replace_bootloader_redirect_init",
                REDIRECT_INIT_ADDRESS,
                REDIRECT_INIT_TARGET,
                "1ff0beb8" + "00bf" * 42,
                127356,
            ),
            (
                "replace_bootloader_aeabi_memset",
                AEABI_MEMSET_ADDRESS,
                AEABI_MEMSET_TARGET,
                "1ff00ab9" + "00bf" * 49,
                127508,
            ),
            (
                "replace_bootloader_aeabi_memcpy",
                AEABI_MEMCPY_ADDRESS,
                AEABI_MEMCPY_TARGET,
                "1ff0d0b8" + "00bf" * 81,
                127392,
            ),
            (
                "replace_bootloader_memcmp",
                MEMCMP_ADDRESS,
                MEMCMP_TARGET,
                "1ff072b8" + "00bf" * 50,
                127204,
            ),
            (
                "replace_bootloader_crc32",
                CRC32_ADDRESS,
                CRC32_TARGET,
                "1ff06ab8" + "00bf" * 26,
                127188,
            ),
            (
                "replace_bootloader_strcspn",
                STRCSPN_ADDRESS,
                STRCSPN_TARGET,
                "1ff030b8" + "00bf" * 15,
                127072,
            ),
            (
                "replace_bootloader_strspn",
                STRSPN_ADDRESS,
                STRSPN_TARGET,
                "1ff02eb8" + "00bf" * 15,
                127068,
            ),
            (
                "replace_bootloader_store_200270cc",
                STORE_200270CC_ADDRESS,
                STORE_200270CC_TARGET,
                "1ff042b800bf00bf",
                127108,
            ),
            (
                "replace_bootloader_udiv10",
                UDIV10_ADDRESS,
                UDIV10_TARGET,
                "1ff044b8" + "00bf" * 92,
                127112,
            ),
            (
                "replace_bootloader_udec_digits",
                UDEC_DIGITS_ADDRESS,
                UDEC_DIGITS_TARGET,
                "1ff01bb8" + "00bf" * 16,
                127030,
            ),
            (
                "replace_bootloader_sdec_digits",
                SDEC_DIGITS_ADDRESS,
                SDEC_DIGITS_TARGET,
                "1ff017b8" + "00bf" * 7,
                127022,
            ),
            (
                "replace_bootloader_hex_digits",
                HEX_DIGITS_ADDRESS,
                HEX_DIGITS_TARGET,
                "1ff018b8" + "00bf" * 17,
                127024,
            ),
            (
                "replace_bootloader_parse_dec",
                PARSE_DEC_ADDRESS,
                PARSE_DEC_TARGET,
                "1ff011b8" + "00bf" * 32,
                127010,
            ),
            (
                "replace_bootloader_u64_to_dec",
                U64_TO_DEC_ADDRESS,
                U64_TO_DEC_TARGET,
                "1ff007b8" + "00bf" * 50,
                126990,
            ),
            (
                "replace_bootloader_u64_to_hex",
                U64_TO_HEX_ADDRESS,
                U64_TO_HEX_TARGET,
                "1ef0f8bf" + "00bf" * 56,
                126960,
            ),
            (
                "replace_bootloader_nullable_strlen",
                NULLABLE_STRLEN_ADDRESS,
                NULLABLE_STRLEN_TARGET,
                "1ef0e2bf" + "00bf" * 10,
                126916,
            ),
            (
                "replace_bootloader_repeat_char",
                REPEAT_CHAR_ADDRESS,
                REPEAT_CHAR_TARGET,
                "1ef0e0bf" + "00bf" * 15,
                126912,
            ),
            (
                "replace_bootloader_float_to_fixed",
                FLOAT_TO_FIXED_ADDRESS,
                FLOAT_TO_FIXED_TARGET,
                "1ef0dfbf" + "00bf" * 158,
                126910,
            ),
            (
                "replace_easylogger_get_fmt_enabled",
                EASYLOGGER_GET_FMT_ADDRESS,
                EASYLOGGER_GET_FMT_TARGET,
                "1cf0c6bd" + "00bf" * 51,
                117644,
            ),
            (
                "replace_easylogger_get_fmt_used_and_enabled_u32",
                EASYLOGGER_GET_FMT_U32_ADDRESS,
                EASYLOGGER_GET_FMT_U32_TARGET,
                "1cf09fbd" + "00bf" * 11,
                117566,
            ),
            (
                "replace_easylogger_get_fmt_used_and_enabled_ptr",
                EASYLOGGER_GET_FMT_PTR_ADDRESS,
                EASYLOGGER_GET_FMT_PTR_TARGET,
                "1cf09cbd" + "00bf" * 11,
                117560,
            ),
            (
                "replace_easylogger_strcpy",
                EASYLOGGER_STRCPY_ADDRESS,
                EASYLOGGER_STRCPY_TARGET,
                "19f0abba" + "00bf" * 79,
                103766,
            ),
            (
                "replace_ambiq_mspi_interrupt_clear",
                MSPI_INTERRUPT_CLEAR_ADDRESS,
                MSPI_INTERRUPT_CLEAR_TARGET,
                "0ef01db8"
                "00bf00bf00bf00bf00bf00bf00bf00bf"
                "00bf00bf00bf00bf00bf00bf00bf00bf"
                "00bf00bf00bf00bf00bf00bf",
                57402,
            ),
        )
        self.assertEqual(
            set(sites),
            {expectation[0] for expectation in expectations},
        )
        for name, address, target, replacement_hex, displacement in expectations:
            with self.subTest(site=name):
                site = sites[name]
                replacement = bytes.fromhex(site["replacement_hex"])
                self.assertEqual(replacement.hex(), replacement_hex)
                self.assertEqual(
                    self.apollo_overlay.decode_thumb_branch(
                        address,
                        replacement[:4],
                        link=False,
                    ),
                    target,
                )
                self.assertEqual(site["displacement"], displacement)
                self.assertGreaterEqual(site["displacement"], -(1 << 24))
                self.assertLess(site["displacement"], 1 << 24)

        caller = self.provider[
            SCMP_CALLER_OFFSET:SCMP_CALLER_OFFSET + 4
        ]
        self.assertEqual(caller, bytes.fromhex("fef7f2fe"))
        self.assertEqual(
            self.apollo_overlay.decode_thumb_branch(
                SCMP_CALLER_ADDRESS,
                caller,
                link=True,
            ),
            SCMP_ADDRESS,
        )
        for address, expected_hex in ALLOC_CALLERS:
            offset = address - RUN_BASE
            encoded = self.provider[offset:offset + 4]
            with self.subTest(caller=f"0x{address:08X}"):
                self.assertEqual(encoded.hex(), expected_hex)
                self.assertEqual(
                    self.apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=True,
                    ),
                    ALLOC_ADDRESS,
                )
        for address, expected_hex in ALLOC_DROP_CALLERS:
            offset = address - RUN_BASE
            encoded = self.provider[offset:offset + 4]
            with self.subTest(alloc_drop_caller=f"0x{address:08X}"):
                self.assertEqual(encoded.hex(), expected_hex)
                self.assertEqual(
                    self.apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=True,
                    ),
                    ALLOC_DROP_ADDRESS,
                )
        caller_sets = (
            (MLIST_ISOPEN_CALLERS, MLIST_ISOPEN_ADDRESS),
            (MLIST_REMOVE_CALLERS, MLIST_REMOVE_ADDRESS),
            (MLIST_APPEND_CALLERS, MLIST_APPEND_ADDRESS),
            (DISK_VERSION_CALLERS, DISK_VERSION_ADDRESS),
            (
                MSPI_INTERRUPT_CLEAR_CALLERS,
                MSPI_INTERRUPT_CLEAR_ADDRESS,
            ),
        )
        for callers, target in caller_sets:
            for address, expected_hex in callers:
                offset = address - RUN_BASE
                encoded = self.provider[offset:offset + 4]
                with self.subTest(
                    caller=f"0x{address:08X}",
                    target=f"0x{target:08X}",
                ):
                    self.assertEqual(encoded.hex(), expected_hex)
                    self.assertEqual(
                        self.apollo_overlay.decode_thumb_branch(
                            address,
                            encoded,
                            link=True,
                        ),
                        target,
                    )

    def test_provider_closes_before_main_and_passes_validator(self) -> None:
        self.assertEqual(RUN_BASE + len(self.provider), OVERLAY_END)
        self.assertEqual(MAIN_BOUNDARY - OVERLAY_END, 0x3448)
        self.assertEqual(
            self.report["overlay"]["remaining_headroom_bytes"],
            0x3448,
        )
        self.open_cfw.validate_apollo_bootloader(self.provider)

    def test_provider_regions_are_contiguous_and_address_exact(self) -> None:
        regions = self.contract["regions"]
        cursor = 0
        for region in regions:
            with self.subTest(region=region["name"]):
                self.assertEqual(region["file_offset"], cursor)
                self.assertEqual(region["target_address"], RUN_BASE + cursor)
                cursor += region["size"]
        self.assertEqual(cursor, len(self.provider))
        self.assertEqual(
            [region["size"] for region in regions],
            [
                1024,
                8,
                8,
                12,
                12,
                90,
                16,
                40,
                4,
                34,
                8,
                34,
                8,
                1632,
                10,
                20,
                8,
                8,
                8,
                6,
                10,
                8,
                6,
                452,
                30,
                28,
                8,
                6,
                12,
                10,
                6,
                16,
                56,
                18266,
                88,
                36,
                102,
                26,
                166,
                38,
                104,
                56,
                34,
                34,
                8,
                188,
                36,
                18,
                38,
                68,
                104,
                116,
                24,
                34,
                320,
                7902,
                106,
                10,
                26,
                26,
                13788,
                162,
                45836,
                48,
                57153,
                1,
                204,
                48,
                18,
                2,
                2,
                4,
                4,
                10,
                10,
                48,
                2,
                8,
                132,
                38,
                20,
                20,
                52,
                6,
                6,
                10,
                6,
                6,
                6,
                2,
                275,
                1,
                12,
                16,
                28,
                30,
                28,
                2,
                44,
                12,
                106,
                28,
                20,
                24,
                48,
                74,
                72,
                20,
                32,
                320,
            ],
        )
        self.assertEqual(
            [region["address_status"] for region in regions],
            [
                (
                    "official_blob"
                    if region["name"].startswith("opaque_")
                    else "generated_source_entry_replacement"
                    if region["name"].endswith("_source_redirect")
                    else "generated_alignment"
                    if "alignment_padding" in region["name"]
                    else "source_compiled"
                )
                for region in regions
            ],
        )

    def test_manifest_tracks_dual_image_littlefs_utility_replacements(
        self,
    ) -> None:
        overrides = self.core_source_manifest["component_overrides"]
        expected = {
            "apollo_bootloader": {
                "bootloader_littlefs_util_max_source_replacement": (
                    1024,
                    8,
                    0x00410400,
                ),
                "bootloader_littlefs_util_min_source_replacement": (
                    1032,
                    8,
                    0x00410408,
                ),
                "bootloader_littlefs_util_aligndown_source_replacement": (
                    1040,
                    12,
                    0x00410410,
                ),
                "bootloader_littlefs_util_alignup_source_replacement": (
                    1052,
                    12,
                    0x0041041C,
                ),
                "bootloader_littlefs_util_npw2_source_replacement": (
                    1064,
                    90,
                    0x00410428,
                ),
                "bootloader_littlefs_util_ctz_source_replacement": (
                    1154,
                    16,
                    0x00410482,
                ),
                "bootloader_littlefs_util_popc_source_replacement": (
                    1170,
                    40,
                    0x00410492,
                ),
                "bootloader_littlefs_util_fromle32_source_replacement": (
                    1214,
                    34,
                    0x004104BE,
                ),
                "bootloader_littlefs_util_tole32_source_replacement": (
                    1248,
                    8,
                    0x004104E0,
                ),
                "bootloader_littlefs_util_frombe32_source_replacement": (
                    1256,
                    34,
                    0x004104E8,
                ),
                "bootloader_littlefs_util_tobe32_source_replacement": (
                    1290,
                    8,
                    0x0041050A,
                ),
            },
            "apollo_main": {
                "littlefs_util_max_source_replacement": (
                    599832,
                    8,
                    0x004CA6F8,
                ),
                "littlefs_util_min_source_replacement": (
                    599840,
                    8,
                    0x004CA700,
                ),
                "littlefs_util_aligndown_source_replacement": (
                    599848,
                    12,
                    0x004CA708,
                ),
                "littlefs_util_alignup_source_replacement": (
                    599860,
                    12,
                    0x004CA714,
                ),
                "littlefs_util_npw2_source_replacement": (
                    599872,
                    90,
                    0x004CA720,
                ),
                "littlefs_util_ctz_source_replacement": (
                    599962,
                    16,
                    0x004CA77A,
                ),
                "littlefs_util_popc_source_replacement": (
                    599978,
                    40,
                    0x004CA78A,
                ),
                "littlefs_util_fromle32_source_replacement": (
                    600022,
                    34,
                    0x004CA7B6,
                ),
                "littlefs_util_tole32_source_replacement": (
                    600056,
                    8,
                    0x004CA7D8,
                ),
                "littlefs_util_frombe32_source_replacement": (
                    600064,
                    34,
                    0x004CA7E0,
                ),
                "littlefs_util_tobe32_source_replacement": (
                    600098,
                    8,
                    0x004CA802,
                ),
            },
        }
        for component_name, expected_regions in expected.items():
            actual_regions = {
                region["name"]: (
                    region["file_offset"],
                    region["size"],
                    region["target_address"],
                )
                for region in overrides[component_name]["regions"]
                if "littlefs_util_" in region["name"]
                and region["name"].endswith("_source_replacement")
            }
            with self.subTest(component=component_name):
                self.assertEqual(actual_regions, expected_regions)
                self.assertTrue(
                    all(
                        region["address_status"]
                        == "generated_source_entry_replacement"
                        for region in overrides[component_name]["regions"]
                        if "littlefs_util_" in region["name"]
                        and region["name"].endswith("_source_replacement")
                    )
                )

    def test_all_sources_are_the_authenticated_candidates(self) -> None:
        boot_source = (
            COMPONENT / "runtime_littlefs_alloc_ckpoint.c"
        ).read_bytes()
        main_candidate = (
            ROOT
            / "components"
            / "apollo_main"
            / "core_overlay"
            / "runtime_littlefs_alloc_ckpoint.c"
        ).read_bytes()
        self.assertEqual(boot_source, main_candidate)
        self.assertEqual(
            hashlib.sha256(boot_source).hexdigest(),
            "16acfce3da9211512631113cb717abd012a0d551ceed36c57b4af300c21e7395",
        )
        source = boot_source.decode("utf-8")
        self.assertIn("lookahead\n    ) +", source)
        self.assertIn("checkpoint\n        ) == 0x60U", source)
        self.assertIn("block_count\n    ) == 0x6CU", source)
        self.assertIn(
            "lfs->lookahead.checkpoint = lfs->block_count;",
            source,
        )

        alloc_drop_source = (
            COMPONENT / "runtime_littlefs_alloc_drop.c"
        ).read_bytes()
        self.assertEqual(
            hashlib.sha256(alloc_drop_source).hexdigest(),
            "38904bccaac4ef0fd39ad49374f287023e"
            "5f03d9b28dc0957d70f460ddfc07ee",
        )
        alloc_drop_text = alloc_drop_source.decode("utf-8")
        self.assertIn("lfs->lookahead.size = 0;", alloc_drop_text)
        self.assertIn("lfs->lookahead.next = 0;", alloc_drop_text)
        self.assertIn(
            "lfs->lookahead.checkpoint = lfs->block_count;",
            alloc_drop_text,
        )
        shared_sources = {
            "runtime_littlefs_disk_version.c": (
                "736a87363e5e009cb29f338c3245c22c0"
                "2df375e275207f3c6e107b456c26d00"
            ),
            "runtime_littlefs_mlist_append.c": (
                "e5423adbe01a734a67944b577bbd543a9"
                "50aefecccd14708bec5e951c58a2f8b"
            ),
            "runtime_littlefs_mlist_remove.c": (
                "be21546c80eaec4d8ad738ea6875bb67"
                "60fae7a873105658bd94a2a751b0bd7d"
            ),
            "runtime_littlefs_mlist_isopen.c": MLIST_ISOPEN_SOURCE_SHA256,
            "runtime_littlefs_util_endian.c": (
                LITTLEFS_UTIL_ENDIAN_SOURCE_SHA256
            ),
            "runtime_littlefs_util.c": (
                "2730d0f39e02d7b6e07396894b796b26"
                "d9f73332deff23a685b5a06da0f7fb22"
            ),
            "runtime_littlefs_util_bitops.c": (
                "405092c6e8fc65a740f951cb2affaad8"
                "766e2553c7b8d290ff58f435e8830f47"
            ),
        }
        for filename, expected_sha256 in shared_sources.items():
            with self.subTest(source=filename):
                source_path = (
                    ROOT
                    / "components"
                    / "apollo_main"
                    / "core_overlay"
                    / filename
                )
                self.assertEqual(
                    hashlib.sha256(source_path.read_bytes()).hexdigest(),
                    expected_sha256,
                )
        self.assertEqual(
            {
                source["path"]: source["sha256"]
                for source in self.report["sources"]
            },
            {
                source["path"]: source["sha256"]
                for source in self.config["sources"]
            },
        )
        for source in self.config["sources"]:
            with self.subTest(configured_source=source["path"]):
                self.assertEqual(
                    hashlib.sha256(
                        (ROOT / source["path"]).read_bytes()
                    ).hexdigest(),
                    source["sha256"],
                )
        self.assertEqual(len(self.config["isolated_leaves"]), 6)
        isolated_configs = {
            leaf["function"]: leaf
            for leaf in self.config["isolated_leaves"]
        }
        isolated_reports = {
            leaf["extraction"]["function"]: leaf
            for leaf in self.report["isolated_leaves"]
        }
        self.assertEqual(
            set(isolated_configs),
            {
                "am_hal_mspi_interrupt_clear",
                "open_cfw_littlefs_mlist_isopen",
                "open_cfw_littlefs_util_fromle32",
                "open_cfw_littlefs_util_tole32",
                "open_cfw_littlefs_util_frombe32",
                "open_cfw_littlefs_util_tobe32",
            },
        )
        self.assertEqual(set(isolated_reports), set(isolated_configs))
        isolated_config = isolated_configs["am_hal_mspi_interrupt_clear"]
        isolated_report = isolated_reports["am_hal_mspi_interrupt_clear"]
        self.assertEqual(
            isolated_config["function"],
            "am_hal_mspi_interrupt_clear",
        )
        self.assertEqual(
            isolated_config["source"]["sha256"],
            (
                "5a91ab0c67bda4bd61c7d436b94b5a7c"
                "81693b948a331d282ae10e88cc5bf85f"
            ),
        )
        self.assertEqual(
            hashlib.sha256(
                (ROOT / isolated_config["source"]["path"]).read_bytes()
            ).hexdigest(),
            isolated_config["source"]["sha256"],
        )
        self.assertEqual(
            isolated_report["source"]["sha256"],
            isolated_config["source"]["sha256"],
        )
        self.assertEqual(
            isolated_report["extraction"]["sha256"],
            MSPI_INTERRUPT_CLEAR_SOURCE_SHA256,
        )
        self.assertEqual(
            isolated_report["extraction"]["relocation_count"],
            0,
        )
        mlist_config = isolated_configs[
            "open_cfw_littlefs_mlist_isopen"
        ]
        mlist_report = isolated_reports[
            "open_cfw_littlefs_mlist_isopen"
        ]
        self.assertEqual(
            mlist_config["source"]["sha256"],
            MLIST_ISOPEN_SOURCE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(
                (ROOT / mlist_config["source"]["path"]).read_bytes()
            ).hexdigest(),
            MLIST_ISOPEN_SOURCE_SHA256,
        )
        self.assertEqual(
            mlist_config["expected"],
            {
                "size": 18,
                "sha256": MLIST_ISOPEN_SOURCE_BODY_SHA256,
            },
        )
        self.assertEqual(
            mlist_report["extraction"]["sha256"],
            MLIST_ISOPEN_SOURCE_BODY_SHA256,
        )
        self.assertEqual(mlist_report["extraction"]["relocation_count"], 0)
        self.assertEqual(
            mlist_report["placement"],
            {
                "offset": 252,
                "size": 18,
                "alignment": 2,
                "padding_before": 0,
            },
        )
        endian_expectations = {
            "open_cfw_littlefs_util_fromle32": (
                270,
                2,
                LITTLEFS_UTIL_IDENTITY_SOURCE_SHA256,
            ),
            "open_cfw_littlefs_util_tole32": (
                272,
                2,
                LITTLEFS_UTIL_IDENTITY_SOURCE_SHA256,
            ),
            "open_cfw_littlefs_util_frombe32": (
                274,
                4,
                LITTLEFS_UTIL_SWAP_SOURCE_SHA256,
            ),
            "open_cfw_littlefs_util_tobe32": (
                278,
                4,
                LITTLEFS_UTIL_SWAP_SOURCE_SHA256,
            ),
        }
        for function_name, (
            expected_offset,
            expected_size,
            expected_sha256,
        ) in endian_expectations.items():
            with self.subTest(isolated_endian_leaf=function_name):
                config = isolated_configs[function_name]
                report = isolated_reports[function_name]
                self.assertEqual(
                    config["source"]["sha256"],
                    LITTLEFS_UTIL_ENDIAN_SOURCE_SHA256,
                )
                self.assertEqual(
                    report["extraction"]["sha256"],
                    expected_sha256,
                )
                self.assertEqual(
                    report["extraction"]["relocation_count"],
                    0,
                )
                self.assertEqual(
                    report["placement"],
                    {
                        "offset": expected_offset,
                        "size": expected_size,
                        "alignment": 2,
                        "padding_before": 0,
                    },
                )

    def test_easylogger_relocated_leaf_config_report_and_artifact_are_exact(
        self,
    ) -> None:
        self.assertEqual(len(self.config["relocated_leaves"]), 33)
        expected = {
            "open_cfw_easylogger_helpers_get_logger": {
                "source": (
                    "78dc5aa9a7eb4f072b3169ae18378550"
                    "07f25e1adccec7deaefecc486c8f0823"
                ),
                "offset": 352,
                "size": 8,
                "alignment": 4,
                "padding": 2,
                "runtime": EASYLOGGER_GET_LOGGER_TARGET,
                "raw": (
                    "3f32a69299002872bb9364f79744be13"
                    "11bcb8bce47f24f43558806931990064"
                ),
                "final": (
                    "3f32a69299002872bb9364f79744be13"
                    "11bcb8bce47f24f43558806931990064"
                ),
                "relocations": [],
            },
            "open_cfw_easylogger_helpers_assert_failed": {
                "source": (
                    "78dc5aa9a7eb4f072b3169ae18378550"
                    "07f25e1adccec7deaefecc486c8f0823"
                ),
                "offset": 360,
                "size": 132,
                "alignment": 4,
                "padding": 0,
                "runtime": EASYLOGGER_ASSERT_FAILED_TARGET,
                "raw": (
                    "f57622ddc7fdbe8555760ca15bf049b8"
                    "fb68abfb3203aa290500e22bbbf82b7a"
                ),
                "final": (
                    "f57622ddc7fdbe8555760ca15bf049b8"
                    "fb68abfb3203aa290500e22bbbf82b7a"
                ),
                "relocations": [],
            },
            "open_cfw_easylogger_get_fmt_enabled": {
                "source": (
                    "8f2850f789fba3b08bdc3e1fa8f3a46"
                    "46aaef7e4b16862f3be53478071aa22b5"
                ),
                "offset": 492,
                "size": 38,
                "alignment": 2,
                "padding": 0,
                "runtime": EASYLOGGER_GET_FMT_TARGET,
                "raw": (
                    "563bc931557c5aae324ecfb98dbc4aa23"
                    "42c43c90163d462bea5e215c0de6390"
                ),
                "final": (
                    "8d2909984779762c0abf28369b018b99"
                    "b4b30f8d23391fe8670e57f43a166697"
                ),
                "relocations": [
                    (
                        14,
                        "R_ARM_THM_CALL",
                        "open_cfw_easylogger_helpers_assert_failed",
                        EASYLOGGER_ASSERT_FAILED_TARGET,
                    ),
                    (
                        18,
                        "R_ARM_THM_CALL",
                        "open_cfw_easylogger_helpers_get_logger",
                        EASYLOGGER_GET_LOGGER_TARGET,
                    ),
                ],
            },
            "open_cfw_easylogger_get_fmt_used_and_enabled_u32": {
                "source": (
                    "8f2850f789fba3b08bdc3e1fa8f3a46"
                    "46aaef7e4b16862f3be53478071aa22b5"
                ),
                "offset": 530,
                "size": 20,
                "alignment": 2,
                "padding": 0,
                "runtime": EASYLOGGER_GET_FMT_U32_TARGET,
                "raw": (
                    "3e6f46ecf152d9192ec638cd0eafa92f"
                    "9c8adcfe7b36e8581add1a865234629a"
                ),
                "final": (
                    "7663e51e49d8c5099f140e85a2f898c"
                    "64083a0f02d1574db69294745ee8e5a93"
                ),
                "relocations": [
                    (
                        4,
                        "R_ARM_THM_CALL",
                        "open_cfw_easylogger_get_fmt_enabled",
                        EASYLOGGER_GET_FMT_TARGET,
                    ),
                ],
            },
            "open_cfw_easylogger_get_fmt_used_and_enabled_ptr": {
                "source": (
                    "8f2850f789fba3b08bdc3e1fa8f3a46"
                    "46aaef7e4b16862f3be53478071aa22b5"
                ),
                "offset": 550,
                "size": 20,
                "alignment": 2,
                "padding": 0,
                "runtime": EASYLOGGER_GET_FMT_PTR_TARGET,
                "raw": (
                    "3e6f46ecf152d9192ec638cd0eafa92f"
                    "9c8adcfe7b36e8581add1a865234629a"
                ),
                "final": (
                    "b5f581ef33404949889812a73244d6b5"
                    "c7807ad5707074228a188df7d89ad898"
                ),
                "relocations": [
                    (
                        4,
                        "R_ARM_THM_CALL",
                        "open_cfw_easylogger_get_fmt_enabled",
                        EASYLOGGER_GET_FMT_TARGET,
                    ),
                ],
            },
            "open_cfw_easylogger_strcpy": {
                "source": (
                    "8f2850f789fba3b08bdc3e1fa8f3a46"
                    "46aaef7e4b16862f3be53478071aa22b5"
                ),
                "offset": 570,
                "size": 52,
                "alignment": 2,
                "padding": 0,
                "runtime": EASYLOGGER_STRCPY_TARGET,
                "raw": (
                    "1fac8de3a83876460e17014da0f84538"
                    "4b253a88d5b79e25f6e5e838e6f46013"
                ),
                "final": (
                    "d19a927665be77d79bd2df6a64575431"
                    "db8962aa023f0546f5c3fe5f47805752"
                ),
                "relocations": [
                    (
                        12,
                        "R_ARM_THM_CALL",
                        "open_cfw_easylogger_helpers_assert_failed",
                        EASYLOGGER_ASSERT_FAILED_TARGET,
                    ),
                    (
                        20,
                        "R_ARM_THM_CALL",
                        "open_cfw_easylogger_helpers_assert_failed",
                        EASYLOGGER_ASSERT_FAILED_TARGET,
                    ),
                ],
            },
        }
        config_by_name = {
            leaf["function"]: leaf
            for leaf in self.config["relocated_leaves"]
            if leaf["function"] in expected
        }
        report_by_name = {
            leaf["extraction"]["function"]: leaf
            for leaf in self.report["relocated_leaves"]
            if leaf["extraction"]["function"] in expected
        }
        self.assertEqual(set(config_by_name), set(expected))
        self.assertEqual(set(report_by_name), set(expected))

        for name, pin in expected.items():
            with self.subTest(easylogger_relocated_leaf=name):
                config = config_by_name[name]
                report = report_by_name[name]
                self.assertEqual(
                    hashlib.sha256(
                        (ROOT / config["source"]["path"]).read_bytes()
                    ).hexdigest(),
                    pin["source"],
                )
                self.assertEqual(config["source"]["sha256"], pin["source"])
                self.assertEqual(report["source"]["sha256"], pin["source"])
                self.assertEqual(
                    report["placement"],
                    {
                        "offset": pin["offset"],
                        "size": pin["size"],
                        "alignment": pin["alignment"],
                        "padding_before": pin["padding"],
                        "runtime_address": pin["runtime"],
                        "runtime_address_hex": f"0x{pin['runtime']:08X}",
                    },
                )
                extraction = report["extraction"]
                self.assertEqual(extraction["size"], pin["size"])
                self.assertEqual(
                    extraction["unrelocated_sha256"],
                    pin["raw"],
                )
                self.assertEqual(extraction["sha256"], pin["final"])
                self.assertEqual(
                    [
                        (
                            relocation["offset"],
                            relocation["type"],
                            relocation["symbol"],
                            relocation["target_address"],
                        )
                        for relocation in extraction["relocations"]
                    ],
                    pin["relocations"],
                )
                self.assertEqual(
                    hashlib.sha256(
                        self.overlay[
                            pin["offset"]:pin["offset"] + pin["size"]
                        ]
                    ).hexdigest(),
                    pin["final"],
                )

    def test_evenota_wrapper_integrity_is_external_and_regenerated(self) -> None:
        transport = self.contract["transport"]
        component = {
            "package_filename": transport["package_filename"],
            "type_id": transport["type_id"],
            "storage_type": transport["storage_type"],
        }
        header = self.open_cfw.component_header(component, self.provider)
        checksum = self.open_cfw.crc32c_msb(self.provider)
        self.assertEqual(checksum, PROVIDER_CRC32C_MSB)
        self.assertEqual(len(header), 128)
        self.assertEqual(struct.unpack_from("<I", header, 8)[0], len(self.provider))
        self.assertEqual(struct.unpack_from("<I", header, 12)[0], checksum)
        self.assertEqual(struct.unpack_from("<I", header, 0x14)[0], 0x4E455645)
        self.assertNotEqual(checksum, self.open_cfw.crc32c_msb(self.official))
        self.assertEqual(
            transport["toc_entry_size_field"],
            "component_header_bytes + payload_size",
        )

    def test_provider_contract_is_manifest_ready_and_hardware_free(self) -> None:
        provider = self.contract["provider"]
        self.assertEqual(provider["kind"], "source_build")
        self.assertEqual(provider["size"], len(self.provider))
        self.assertEqual(provider["sha256"], PROVIDER_SHA256)
        manifest_override = self.core_source_manifest["component_overrides"][
            "apollo_bootloader"
        ]
        self.assertEqual(
            {
                key: manifest_override["provider"][key]
                for key in ("kind", "path", "size", "sha256")
            },
            provider,
        )
        self.assertEqual(
            manifest_override["provider"]["profiles"]["linux-clang"],
            {
                "size": 150456,
                "sha256": (
                    "df6ec98c263e1e5d4f16244af450171"
                    "e149be673eb0347f076f997b8de326187"
                ),
            },
        )
        ownership_fields = (
            "file_offset",
            "size",
            "target_address",
            "address_status",
        )
        self.assertEqual(
            [
                tuple(region[field] for field in ownership_fields)
                for region in manifest_override["regions"]
            ],
            [
                tuple(region[field] for field in ownership_fields)
                for region in self.contract["regions"]
            ],
        )
        self.assertTrue(
            all(
                region["target"] == "apollo510b_internal_mram"
                for region in manifest_override["regions"]
            )
        )
        self.assertEqual(self.contract["hardware_operations"], [])
        self.assertEqual(self.report["safety"]["hardware_operations"], [])
        self.assertFalse(self.report["safety"]["package_assembly_performed"])
        self.assertFalse(self.report["safety"]["flashing_performed"])
        self.assertFalse(self.report["safety"]["erasing_performed"])

        self.assertEqual(
            sorted(path.name for path in self.output.iterdir()),
            [
                "bootloader_core_overlay.bin",
                "build-report.json",
                "ota_s200_bootloader.bin",
                "provider-contract.json",
            ],
        )

    def test_rebuild_is_deterministic(self) -> None:
        second = Path(self.temporary.name) / "second"
        report = self.builder.build(
            root=ROOT,
            config_path=CONFIG_PATH,
            output_dir=second,
            clang=os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
        )
        self.assertEqual(
            (second / "ota_s200_bootloader.bin").read_bytes(),
            self.provider,
        )
        self.assertEqual(
            (second / "bootloader_core_overlay.bin").read_bytes(),
            self.overlay,
        )
        self.assertEqual(report["component"]["sha256"], PROVIDER_SHA256)


if __name__ == "__main__":
    unittest.main()
