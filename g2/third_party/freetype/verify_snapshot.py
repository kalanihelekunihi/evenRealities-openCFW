#!/usr/bin/env python3
"""Fail-closed offline verification for the FreeType 2.9.1 snapshot."""

from __future__ import annotations

import hashlib
import json
import stat
import struct
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROVENANCE_PATH = HERE / "PROVENANCE.json"
EXPECTED_SOURCE_RECORDS_SHA256 = (
    "62e233bc18e6ada5974c98d65dfc4faaf15058e39edbc435662337d60549ec32"
)
EXPECTED_SOURCE_FILE_COUNT = 297
EXPECTED_LICENSE = {
    "local_path": "LICENSE",
    "upstream_path": "docs/FTL.TXT",
    "git_mode": "100644",
    "size": 6743,
    "sha256": "08c135755dd589039470f1fdbb400daaabaaa50d0b366d19cebff4d22986baa1",
    "git_blob_sha1": "c406d150fa57aaf7a5b950b6cf302daeba1d0bb9",
}
EXPECTED_UPSTREAM = {
    "repository": "https://gitlab.freedesktop.org/freetype/freetype.git",
    "repository_web": "https://gitlab.freedesktop.org/freetype/freetype",
    "selected_ref": "refs/tags/VER-2-9-1",
    "selected_tag": "VER-2-9-1",
    "annotated_tag_object": "ad55868d889b6ba8d2aed846b4b4b460f8a83e42",
    "annotated_tag_type": "tag",
    "annotated_tag_payload_path": "upstream/VER-2-9-1.tag",
    "annotated_tag_payload_size": 308,
    "annotated_tag_payload_sha256": (
        "63e19c1cbd64f317780b1d283129c27bd7ba936dcda7e34225e57dda95a32972"
    ),
    "tag_signature": {
        "present": True,
        "format": "OpenPGP",
        "issuer_key_id": "C1A60EACE707FDA5",
        "signature_bytes_pinned": True,
        "signer_trust_verified": False,
        "qualification": (
            "The exact signed tag payload is pinned, but its public key is not "
            "vendored and signer trust is not claimed."
        ),
    },
    "peeled_commit": "86bc8a95056c97a810986434a3f268cbe67f2902",
    "commit_object_payload_path": (
        "upstream/86bc8a95056c97a810986434a3f268cbe67f2902.commit"
    ),
    "commit_object_payload_size": 1263,
    "commit_object_payload_sha256": (
        "536d12bb9cab202da8e724505b1bcdf836a963132153c1df571e6c41117ea0cb"
    ),
    "selected_tree": "34694611454c8e95bd398d54da805ffb4e94577b",
    "parent_commit": "ac97a29653e2a551064705891bc578c53ecf056d",
    "author_date": "2018-05-01T20:27:24+02:00",
    "committer_date": "2018-05-01T20:37:24+02:00",
    "declared_library_version": "2.9.1",
    "declared_version_macros": {
        "FREETYPE_MAJOR": 2,
        "FREETYPE_MINOR": 9,
        "FREETYPE_PATCH": 1,
    },
}
EXPECTED_EXCLUDED_HELPERS = [
    "src/autofit/Jamfile",
    "src/autofit/afblue.cin",
    "src/autofit/afblue.dat",
    "src/autofit/afblue.hin",
    "src/autofit/module.mk",
    "src/autofit/rules.mk",
    "src/base/Jamfile",
    "src/base/ftver.rc",
    "src/base/rules.mk",
    "src/cff/Jamfile",
    "src/cff/module.mk",
    "src/cff/rules.mk",
    "src/psaux/Jamfile",
    "src/psaux/module.mk",
    "src/psaux/rules.mk",
    "src/pshinter/Jamfile",
    "src/pshinter/module.mk",
    "src/pshinter/rules.mk",
    "src/psnames/Jamfile",
    "src/psnames/module.mk",
    "src/psnames/rules.mk",
    "src/sfnt/Jamfile",
    "src/sfnt/module.mk",
    "src/sfnt/rules.mk",
    "src/smooth/Jamfile",
    "src/smooth/module.mk",
    "src/smooth/rules.mk",
    "src/truetype/Jamfile",
    "src/truetype/module.mk",
    "src/truetype/rules.mk",
]
EXPECTED_SELECTION = {
    "classification": (
        "authenticated upstream release snapshot; production-excluded source candidate"
    ),
    "exact_g2_checkout_proven": False,
    "qualification": (
        "G2 numeric constants prove FreeType 2.9.1, but do not prove an unpatched "
        "upstream checkout or its complete build configuration."
    ),
    "selected_file_count": EXPECTED_SOURCE_FILE_COUNT,
    "selected_roots": [
        "include",
        "src/autofit",
        "src/base",
        "src/cff",
        "src/psaux",
        "src/pshinter",
        "src/psnames",
        "src/sfnt",
        "src/smooth",
        "src/truetype",
    ],
    "selection_rule": (
        "All .h files under include plus all .c/.h files in the nine source module "
        "directories used by the recovered G2 module table; unchanged docs/FTL.TXT "
        "is retained locally as LICENSE."
    ),
    "excluded_upstream_build_helper_count": 30,
    "excluded_upstream_build_helpers": EXPECTED_EXCLUDED_HELPERS,
    "source_records_sha256": EXPECTED_SOURCE_RECORDS_SHA256,
    "integration_status": (
        "authenticated and verified offline; not production-configured"
    ),
}
EXPECTED_MODULES = [
    (0, "autofit_module_class", "autofitter", 0x00752520, 0x00000004, 56),
    (1, "tt_driver_class", "truetype", 0x006DED34, 0x00000501, 68),
    (2, "cff_driver_class", "cff", 0x006DCB74, 0x00000D01, 72),
    (3, "psaux_module_class", "psaux", 0x00758A18, 0x00000000, 12),
    (4, "psnames_module_class", "psnames", 0x00758A60, 0x00000000, 12),
    (5, "pshinter_module_class", "pshinter", 0x00758A3C, 0x00000000, 168),
    (6, "sfnt_module_class", "sfnt", 0x0075A3F8, 0x00000000, 12),
    (7, "ft_smooth_renderer_class", "smooth", 0x00718D9C, 0x00000002, 64),
    (
        8,
        "ft_smooth_lcd_renderer_class",
        "smooth-lcd",
        0x00718DD8,
        0x00000002,
        64,
    ),
    (
        9,
        "ft_smooth_lcdv_renderer_class",
        "smooth-lcdv",
        0x00718E14,
        0x00000002,
        64,
    ),
]
EXPECTED_RECOVERED_CONFIGURATION = {
    "base": {
        "FT_CONFIG_OPTION_ENVIRONMENT_PROPERTIES": False,
        "FT_CONFIG_OPTION_INCREMENTAL": True,
        "FT_CONFIG_OPTION_PIC": False,
        "FT_CONFIG_OPTION_SUBPIXEL_RENDERING": False,
        "stream_support": True,
    },
    "cff": {
        "CFF_CONFIG_OPTION_OLD_ENGINE": False,
        "default_hinting_engine": "Adobe",
    },
    "autofit": {
        "AF_CONFIG_OPTION_CJK": True,
        "AF_CONFIG_OPTION_INDIC": True,
        "AF_CONFIG_OPTION_USE_WARPER": True,
        "fallback_style": {
            "name": "AF_STYLE_HANI_DFLT",
            "enum": 83,
            "qualification": (
                "HANI_DFLT is 79 without the four guarded Indic styles and 83 "
                "with them in authenticated 2.9.1"
            ),
        },
    },
    "true_type": {
        "interpreter_default": 40,
        "supported_interpreter_versions": [35, 40],
        "TT_CONFIG_OPTION_SUBPIXEL_HINTING": 2,
        "TT_CONFIG_OPTION_GX_VAR_SUPPORT": True,
        "TT_CONFIG_OPTION_EMBEDDED_BITMAPS": True,
    },
    "gx_variations": {
        "multi_masters_record": "0x007505A4",
        "multi_masters_callable_slots": 8,
        "metrics_variations_record": "0x00767290",
        "metrics_variations_callable_slots": 3,
    },
    "allocator_lifecycle": {
        "FT_Memory_size": 16,
        "heap_descriptor": "0x20000354",
        "generic_allocate": "0x00484180",
        "generic_reallocate": "0x00484234",
        "generic_free": "0x0048429E",
        "callbacks": {
            "alloc": "0x005676D4",
            "realloc": "0x005676E0",
            "free": "0x005676EC",
        },
        "lifecycle": {
            "FT_Init_FreeType": "0x0052431C",
            "FT_New_Memory": "0x005676A0",
            "FT_Done_Memory": "0x005676C6",
            "FT_New_Library": "0x005274B2",
            "FT_Add_Default_Modules": "0x005242FC",
            "FT_Done_Face": {
                "entry": "0x00526814",
                "end": "0x0052687E",
                "direct_callers": [
                    {"address": "0x004B2310", "kind": "BL"},
                    {"address": "0x0052659C", "kind": "BL"},
                    {"address": "0x005267D0", "kind": "BL"},
                ],
                "caller_roles": [
                    "LVGL/FTC face-cache destructor",
                    "FT_Open_Face failure cleanup",
                    "FT_Open_Face no-output cleanup",
                ],
            },
            "lv_freetype_font_create": "0x004B1C9C",
            "lv_freetype_font_delete": "0x004B1EF6",
        },
    },
    "font_registration": {
        "font_chain_entries_per_role": 4,
        "configuration_arrays": {
            "background": "0x20002C48",
            "foreground": "0x20002C78",
        },
        "configuration_record": {
            "size": 12,
            "type": {"offset": 0, "size": 1},
            "font_pointer_or_face_path": {"offset": 4, "size": 4},
            "pixel_size": {"offset": 8, "size": 2},
            "style": {"offset": 10, "size": 1},
            "type_semantics": {
                "0": "native lv_font_t pointer",
                "1": "FreeType face path passed to lv_freetype_font_create",
                "2": "binary-font path disabled in this build",
            },
        },
    },
}
EXPECTED_UNRESOLVED = [
    "complete FT_CONFIG_OPTION_* state outside the proven subset",
    "optional compression helpers",
    "an exact stock FT_Done_FreeType entry (no conventional retained topology was found)",
    "IAR version and exact compiler/linker flags",
    "external font payload identities and runtime configuration-array contents",
]
EXPECTED_PROMOTION_STATUS = (
    "production-excluded; source configuration and explicit promotion review still required"
)
EXPECTED_MODULE_HEADER = (
    HERE / "g2-config" / "freetype" / "config" / "ftmodule.h"
)
EXPECTED_MODULE_HEADER_SIZE = 876
EXPECTED_MODULE_HEADER_SHA256 = (
    "522c1d358dce8a141b2f8afec7020f66bf800d3d829a1ad22f3418ebf3f05d74"
)
EXPECTED_IMAGE = ROOT / "blobs" / "official" / "g2-2.2.6.10" / "ota_s200_firmware_ota.bin"
EXPECTED_IMAGE_SIZE = 3523396
EXPECTED_IMAGE_SHA256 = (
    "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
)
MAPPING_BIAS = 0x00437FE0
MODULE_TABLE_ADDRESS = 0x0073EEF8
MODULE_TABLE_TERMINATOR = 0x0073EF20
METADATA_PATHS = {
    "PROVENANCE.json",
    "README.openCFW.md",
    "verify_snapshot.py",
    "upstream/VER-2-9-1.tag",
    "upstream/86bc8a95056c97a810986434a3f268cbe67f2902.commit",
    "g2-config/freetype/config/ftmodule.h",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_object_sha1(kind: str, data: bytes) -> str:
    header = f"{kind} {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    return git_object_sha1("blob", data)


def canonical_sha256(value: Any) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(data)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FreeType snapshot verification failed: {message}")


def verify_provenance() -> dict[str, Any]:
    provenance = json.loads(PROVENANCE_PATH.read_text(encoding="utf-8"))
    require(
        set(provenance) == {
            "schema_version",
            "component",
            "license",
            "upstream",
            "selection",
            "g2_boundary",
            "files",
        },
        "top-level provenance schema changed",
    )
    require(provenance["schema_version"] == 1, "unknown provenance schema")
    require(provenance["component"] == "freetype", "component changed")
    require(provenance["license"] == "FTL", "license choice changed")
    require(provenance["upstream"] == EXPECTED_UPSTREAM, "upstream identity changed")
    require(provenance["selection"] == EXPECTED_SELECTION, "selection policy changed")
    return provenance


def verify_upstream_objects() -> None:
    tag = (HERE / EXPECTED_UPSTREAM["annotated_tag_payload_path"]).read_bytes()
    commit = (HERE / EXPECTED_UPSTREAM["commit_object_payload_path"]).read_bytes()
    require(len(tag) == 308, "annotated tag payload size changed")
    require(sha256(tag) == EXPECTED_UPSTREAM["annotated_tag_payload_sha256"], "tag payload changed")
    require(
        git_object_sha1("tag", tag) == EXPECTED_UPSTREAM["annotated_tag_object"],
        "annotated tag object ID changed",
    )
    require(len(commit) == 1263, "commit payload size changed")
    require(
        sha256(commit) == EXPECTED_UPSTREAM["commit_object_payload_sha256"],
        "commit payload changed",
    )
    require(
        git_object_sha1("commit", commit) == EXPECTED_UPSTREAM["peeled_commit"],
        "peeled commit object ID changed",
    )
    require(
        tag.startswith(
            b"object 86bc8a95056c97a810986434a3f268cbe67f2902\n"
            b"type commit\ntag VER-2-9-1\n"
        ),
        "tag no longer names the selected commit/ref",
    )
    require(b"-----BEGIN PGP SIGNATURE-----" in tag, "tag signature missing")
    require(b"-----END PGP SIGNATURE-----\n" in tag, "tag signature truncated")
    require(
        commit.startswith(
            b"tree 34694611454c8e95bd398d54da805ffb4e94577b\n"
            b"parent ac97a29653e2a551064705891bc578c53ecf056d\n"
        ),
        "commit tree/parent changed",
    )


def verify_source_files(provenance: dict[str, Any]) -> None:
    records = provenance["files"]
    require(isinstance(records, list), "file records are not a list")
    require(len(records) == EXPECTED_SOURCE_FILE_COUNT, "selected file count changed")
    require(
        canonical_sha256(records) == EXPECTED_SOURCE_RECORDS_SHA256,
        "per-file provenance records changed",
    )
    require(records[0] == EXPECTED_LICENSE, "FTL license provenance changed")
    local_paths = [record["local_path"] for record in records]
    require(local_paths == sorted(local_paths), "file records are not canonical-sorted")
    require(len(local_paths) == len(set(local_paths)), "duplicate local file record")
    for record in records:
        require(
            set(record) == {
                "local_path",
                "upstream_path",
                "git_mode",
                "size",
                "sha256",
                "git_blob_sha1",
            },
            f"file record schema changed: {record.get('local_path', '<missing>')}",
        )
        path = HERE / record["local_path"]
        require(path.is_file() and not path.is_symlink(), f"file missing or symlinked: {path}")
        require(stat.S_IMODE(path.stat().st_mode) == 0o644, f"local mode changed: {path}")
        data = path.read_bytes()
        require(record["git_mode"] == "100644", f"upstream mode changed: {path}")
        require(len(data) == record["size"], f"size changed: {path}")
        require(sha256(data) == record["sha256"], f"SHA-256 changed: {path}")
        require(
            git_blob_sha1(data) == record["git_blob_sha1"],
            f"Git blob identity changed: {path}",
        )
        require(b"\r" not in data, f"line endings changed: {path}")
        require(data.endswith(b"\n"), f"terminal LF missing: {path}")
    for name in METADATA_PATHS:
        path = HERE / name
        require(path.is_file() and not path.is_symlink(), f"metadata missing or symlinked: {path}")
        require(stat.S_IMODE(path.stat().st_mode) == 0o644, f"metadata mode changed: {path}")
    actual = {
        path.relative_to(HERE).as_posix()
        for path in HERE.rglob("*")
        if path.is_file()
    }
    require(actual == set(local_paths) | METADATA_PATHS, "snapshot subtree inventory changed")


def verify_markers_and_module_header(provenance: dict[str, Any]) -> None:
    header = (HERE / "include" / "freetype" / "freetype.h").read_text(encoding="utf-8")
    for marker in (
        "#define FREETYPE_MAJOR  2",
        "#define FREETYPE_MINOR  9",
        "#define FREETYPE_PATCH  1",
    ):
        require(marker in header, f"version marker missing: {marker}")
    license_text = (HERE / "LICENSE").read_text(encoding="utf-8")
    require("The FreeType Project LICENSE" in license_text, "FTL title missing")
    require("`AS IS' WITHOUT" in license_text, "FTL disclaimer missing")

    module_header = EXPECTED_MODULE_HEADER.read_bytes()
    require(len(module_header) == EXPECTED_MODULE_HEADER_SIZE, "G2 module header size changed")
    require(sha256(module_header) == EXPECTED_MODULE_HEADER_SHA256, "G2 module header changed")
    macro_lines = [
        line.strip()
        for line in module_header.decode("utf-8").splitlines()
        if line.strip().startswith("FT_USE_MODULE(")
    ]
    expected_lines = [
        f"FT_USE_MODULE( {class_type}, {symbol} )"
        for class_type, symbol in (
            ("FT_Module_Class", "autofit_module_class"),
            ("FT_Driver_ClassRec", "tt_driver_class"),
            ("FT_Driver_ClassRec", "cff_driver_class"),
            ("FT_Module_Class", "psaux_module_class"),
            ("FT_Module_Class", "psnames_module_class"),
            ("FT_Module_Class", "pshinter_module_class"),
            ("FT_Module_Class", "sfnt_module_class"),
            ("FT_Renderer_Class", "ft_smooth_renderer_class"),
            ("FT_Renderer_Class", "ft_smooth_lcd_renderer_class"),
            ("FT_Renderer_Class", "ft_smooth_lcdv_renderer_class"),
        )
    ]
    require(macro_lines == expected_lines, "G2 module macro order changed")

    g2 = provenance["g2_boundary"]
    require(
        set(g2) == {
            "evidence",
            "official_image",
            "official_image_size",
            "official_image_sha256",
            "load_mapping",
            "version_constructor",
            "default_module_table",
            "recovered_module_header",
            "recovered_module_header_size",
            "recovered_module_header_sha256",
            "configuration_evidence",
            "modules",
            "recovered_configuration",
            "unresolved",
            "promotion_status",
        },
        "G2 boundary schema changed",
    )
    require(g2["evidence"] == "docs/research/freetype-recovery-audit.md", "evidence path changed")
    require(g2["official_image"] == "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin", "image path changed")
    require(g2["official_image_size"] == EXPECTED_IMAGE_SIZE, "image size pin changed")
    require(g2["official_image_sha256"] == EXPECTED_IMAGE_SHA256, "image hash pin changed")
    require(g2["load_mapping"] == "run_address = file_offset + 0x00437fe0", "mapping changed")
    require(g2["version_constructor"] == "FT_New_Library at 0x005274B2", "version evidence changed")
    require(
        g2["default_module_table"]
        == {"run_address": "0x0073EEF8", "terminator_address": "0x0073EF20", "entry_count": 10},
        "module table boundary changed",
    )
    require(g2["recovered_module_header"] == "g2-config/freetype/config/ftmodule.h", "module header path changed")
    require(g2["recovered_module_header_size"] == EXPECTED_MODULE_HEADER_SIZE, "module header size pin changed")
    require(g2["recovered_module_header_sha256"] == EXPECTED_MODULE_HEADER_SHA256, "module header hash pin changed")
    require(
        g2["configuration_evidence"] == "tools/freetype_g2_config_audit.py",
        "configuration evidence path changed",
    )
    expected_records = [
        {
            "order": order,
            "class_symbol": symbol,
            "module_name": name,
            "class_address": f"0x{address:08X}",
            "flags": f"0x{flags:08X}",
            "object_size": size,
        }
        for order, symbol, name, address, flags, size in EXPECTED_MODULES
    ]
    require(g2["modules"] == expected_records, "recovered module records changed")
    require(
        g2["recovered_configuration"] == EXPECTED_RECOVERED_CONFIGURATION,
        "recovered configuration changed",
    )
    require(g2["unresolved"] == EXPECTED_UNRESOLVED, "unresolved boundary changed")
    require(g2["promotion_status"] == EXPECTED_PROMOTION_STATUS, "promotion status changed")


def image_slice(image: bytes, start: int, size: int) -> bytes:
    offset = start - MAPPING_BIAS
    require(offset >= 0 and offset + size <= len(image), f"image range invalid at 0x{start:08X}")
    return image[offset : offset + size]


def read_u32(image: bytes, address: int) -> int:
    return struct.unpack("<I", image_slice(image, address, 4))[0]


def read_c_string(image: bytes, address: int) -> str:
    offset = address - MAPPING_BIAS
    require(0 <= offset < len(image), f"string pointer invalid at 0x{address:08X}")
    end = image.find(b"\0", offset, min(len(image), offset + 128))
    require(end >= 0, f"unterminated string at 0x{address:08X}")
    return image[offset:end].decode("ascii")


def verify_g2_image_if_present() -> None:
    if not EXPECTED_IMAGE.exists():
        return
    image = EXPECTED_IMAGE.read_bytes()
    require(len(image) == EXPECTED_IMAGE_SIZE, "official image size changed")
    require(sha256(image) == EXPECTED_IMAGE_SHA256, "official image SHA-256 changed")
    class_addresses = [read_u32(image, MODULE_TABLE_ADDRESS + 4 * index) for index in range(10)]
    require(
        class_addresses == [record[3] for record in EXPECTED_MODULES],
        "official module-table pointers changed",
    )
    require(read_u32(image, MODULE_TABLE_TERMINATOR) == 0, "module table lost NULL terminator")
    for _, _, expected_name, address, expected_flags, expected_size in EXPECTED_MODULES:
        require(read_u32(image, address) == expected_flags, f"{expected_name} flags changed")
        require(read_u32(image, address + 4) == expected_size, f"{expected_name} size changed")
        name_pointer = read_u32(image, address + 8)
        require(read_c_string(image, name_pointer) == expected_name, f"{expected_name} name changed")


def json_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for child in value for item in json_strings(child)]
    if isinstance(value, dict):
        return [
            item
            for key, child in value.items()
            for item in [*json_strings(key), *json_strings(child)]
        ]
    return []


def verify_production_isolation() -> None:
    production_json = list((ROOT / "manifests").glob("*.json"))
    production_json.extend(
        path
        for path in (ROOT / "components").glob("**/*.json")
        if "build" not in path.relative_to(ROOT / "components").parts
    )
    for path in production_json:
        value = json.loads(path.read_text(encoding="utf-8"))
        require(
            all("freetype" not in item.lower() for item in json_strings(value)),
            f"snapshot configured by {path}",
        )

    source_suffixes = {".c", ".h", ".py", ".s", ".S", ".ld", ".lds", ".mk"}
    production_sources = [
        path
        for path in (ROOT / "components").glob("**/*")
        if path.is_file()
        and path.suffix in source_suffixes
        and "build" not in path.relative_to(ROOT / "components").parts
    ]
    for path in production_sources:
        require(
            "freetype" not in path.read_text(encoding="utf-8").lower(),
            f"snapshot referenced by production source {path}",
        )


def main() -> None:
    provenance = verify_provenance()
    verify_upstream_objects()
    verify_source_files(provenance)
    verify_markers_and_module_header(provenance)
    verify_g2_image_if_present()
    verify_production_isolation()
    print("FreeType 2.9.1 snapshot verification passed")


if __name__ == "__main__":
    main()
