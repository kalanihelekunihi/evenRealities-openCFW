#!/usr/bin/env python3
"""Authenticate the G2 NemaGFX/NemaVG and Ambiq GPU dependency boundary.

The default audit is fully offline and read-only.  It checks the authenticated
G2 image, the recovered stock function/string/path evidence, and the public
artifact manifest.  ``--sdk-root`` additionally authenticates an AmbiqSuite
5.1.0 checkout by reconstructing its Git tree and hashing selected artifacts.
There is no transport, signer, programmer, erase, or device-write path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
MANIFEST = ROOT / "tools/manifests/g2-nemagfx-ambiq-provenance.json"
LOAD_BASE = 0x0043_7FE0
IMAGE_SIZE = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
MANIFEST_CANONICAL_SHA256 = "76b713f3bf2b7be1a2075463ac212781be44cd7c7f1a6c4e558cc580440eae6a"

EXPECTED_REPOSITORY = "https://github.com/AmbiqMicro/ambiqhal_ambiq.git"
EXPECTED_PUBLIC_COMMIT = "b853fded7e545f005727e13bf2ce83018c7e242d"
EXPECTED_PUBLIC_TREE = "e690768a6e7b4d6a8d526fc75e8278a2764deff3"
EXPECTED_NEMA_ARCHIVE_COMMIT = "c6f54a9587fcdc3cd10a9af5db0b602f34d5304f"
EXPECTED_GPU_PATCH_COMMIT = "e3eec7f3c1148fee3dfa33ca861be176de66c584"
EXPECTED_SDK_REVISION = "release_sdk5p1p0-634f7c117b"


class AuditError(RuntimeError):
    """Raised when an authenticated input or recovered invariant changes."""


PINNED_SPANS = {
    "lv_ambiq_common_start": (
        0x004B_092A,
        0x004B_0B5A,
        "a2af413262a255a98e249c5e436cefd3f9d8f5f7f35550ee629c89e51902f4fc",
    ),
    "lv_draw_ambiq_init": (
        0x004C_73D6,
        0x004C_74EE,
        "7b7d08b910da49cd2484e09b80e18b3183c11cf356b7e6ea44d5eb1212da0c17",
    ),
    "nema_get_last_cl_id": (
        0x0051_418E,
        0x0051_4194,
        "d3e8c911f7f7e0d2eb62ee4748a793dabd6bde1a3454660995b42cb6f90f5340",
    ),
    "nema_get_last_submission_id": (
        0x0051_4194,
        0x0051_419A,
        "a51abe05402e6b85d6e6a095137c24e4ba804005bb8c4d14dd92e7acd8ea0fbb",
    ),
    "nemagfx_power_control": (
        0x0051_419A,
        0x0051_4238,
        "788b0b59874a5651f3017f75fee7d98216c1b5a7f2c6be5af3dc4351267bc01a",
    ),
    "nema_cl_create_sized": (
        0x0051_4278,
        0x0051_42EE,
        "4417eff112be0539a1c890375387eeb866b9d0a638e118f5edf9232a632e038b",
    ),
    "nema_cl_rewind": (
        0x0051_4384,
        0x0051_43D4,
        "b0733ab3843dc9140923a56f1b4578c87c2ab80483c22d2d42449bc00201c1a6",
    ),
    "nema_cl_bind_sectored_circular": (
        0x0051_43D4,
        0x0051_44BA,
        "1b72806af461fbd44dc0a8928e9a4b4493d124242f8f89f7d5820d0c8c692b6d",
    ),
    "nema_cl_get_bound": (
        0x0051_44FA,
        0x0051_450A,
        "e08f10355a207b47e44411be7bf443449dc4d4fc54a1d7d3ca05bfeeca01d54a",
    ),
    "lv_ambiq_gradient_create": (
        0x005F_A238,
        0x005F_A7C0,
        "82d1ae24eff6da055d251b067ce54e002940cd90a8283af0063381448ea6dc93",
    ),
    "lv_ambiq_dashline_create": (
        0x005F_A7C0,
        0x005F_A84A,
        "aeda115cd2ea2bba4eee91b8510ec396bdb40b94184a16d51bfc86ba12ae70c0",
    ),
}

RETAINED_PATHS = {
    0x004B_1054: (
        0x006D_8E14,
        r"D:\01_workspace\s200_ap510b_iar_git\third_party\lvgl_v9.3\LVGL\src\draw\ambiq\lv_draw_ambiq_private.c",
    ),
    0x004C_7938: (
        0x006D_D8F4,
        r"D:\01_workspace\s200_ap510b_iar_git\third_party\lvgl_v9.3\LVGL\src\draw\ambiq\lv_draw_ambiq.c",
    ),
}

RETAINED_STRINGS = {
    0x0076_C8E8: "INVALID_SECTORED_CL_SIZE",
    0x0076_C904: "lv_draw_ambiq_common_start",
    0x0076_C920: "Power control failed: %d\r\n",
    0x0078_D8E4: "AMBIQ",
}

EXPECTED_GPU_PATCH_EXPORTS = {
    "lv_ambiq_create_corner_mask",
    "lv_ambiq_dashline_create",
    "lv_ambiq_draw_bitmap_glyph",
    "lv_ambiq_get_glyph",
    "lv_ambiq_get_path_aabb",
    "lv_ambiq_get_path_vbuf",
    "lv_ambiq_get_vg_paint_tex",
    "lv_ambiq_gradient_create",
    "lv_ambiq_l8_l4_convert",
    "lv_ambiq_shadow_blur_corner",
    "lv_ambiq_shadow_blur_corner_vg",
}

EXPECTED_GPU_PATCH_ACCESSORS = {
    "lv_ambiq_get_vg_paint_tex": (
        301,
        16,
        "f3a3a1a552751faddd5cc8a53cbcd5a030048dc39572004d56221486e5d44633",
    ),
    "lv_ambiq_get_path_aabb": (
        313,
        24,
        "e51f6519f355e32c18447d6b26329e6da16cd2e54f0515586f883171de7e2e5c",
    ),
    "lv_ambiq_get_path_vbuf": (
        326,
        28,
        "bdf5a63391e7b275cff1f7b393b3f34ee7bb564d6733dd023e7d107dcecef2af",
    ),
}

EXPECTED_GPU_PRIVATE_LAYOUTS = {
    "nema_vg_paint_tex_t": 0x30,
    "nema_vg_paint_t": 0xE0,
    "nema_vg_path_bbox_t": 0x50,
    "nema_vbuf_t_": 0x60,
    "nema_vg_path_t": 0x88,
}

EXPECTED_GPU_PATCH_DASHLINE = (
    268,
    144,
    "9f465e5e7bc8c95a022a491d937c46f461071479093ad7f7101581c4a902f20b",
)


def _canonical_digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise AuditError(f"cannot load {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise AuditError(f"manifest root is not an object: {path}")
    return value


def _slice(data: bytes, start: int, end: int) -> bytes:
    first = start - LOAD_BASE
    last = end - LOAD_BASE
    if first < 0 or last < first or last > len(data):
        raise AuditError(f"span 0x{start:08X}..0x{end:08X} lies outside image")
    return data[first:last]


def _word(data: bytes, run: int) -> int:
    return struct.unpack("<I", _slice(data, run, run + 4))[0]


def _cstr(data: bytes, run: int, limit: int = 256) -> str:
    raw = _slice(data, run, min(run + limit, LOAD_BASE + len(data)))
    end = raw.find(b"\0")
    if end < 0:
        raise AuditError(f"unterminated string at 0x{run:08X}")
    try:
        return raw[:end].decode("ascii")
    except UnicodeDecodeError as exc:
        raise AuditError(f"non-ASCII string at 0x{run:08X}") from exc


def _git_object_id(kind: str, body: bytes) -> bytes:
    header = f"{kind} {len(body)}\0".encode("ascii")
    return hashlib.sha1(header + body).digest()


def _git_tree_id(directory: Path) -> bytes:
    """Reconstruct a regular-file Git tree without requiring a Git checkout."""

    entries: list[tuple[bytes, bytes]] = []
    try:
        children = list(directory.iterdir())
    except OSError as exc:
        raise AuditError(f"cannot enumerate SDK directory {directory}: {exc}") from exc
    for child in children:
        name = child.name.encode("utf-8")
        if child.is_dir():
            mode = b"40000"
            object_id = _git_tree_id(child)
            sort_key = name + b"/"
        elif child.is_file():
            mode = b"100644"
            try:
                body = child.read_bytes()
            except OSError as exc:
                raise AuditError(f"cannot read SDK file {child}: {exc}") from exc
            object_id = _git_object_id("blob", body)
            sort_key = name
        else:
            raise AuditError(f"unsupported SDK tree entry: {child}")
        entries.append((sort_key, mode + b" " + name + b"\0" + object_id))
    body = b"".join(entry for _, entry in sorted(entries, key=lambda item: item[0]))
    return _git_object_id("tree", body)


def _ar_member(data: bytes, wanted: str) -> bytes:
    """Return one member from a GNU/SysV archive without external tools."""

    if not data.startswith(b"!<arch>\n"):
        raise AuditError("GPU patch artifact is not an ar archive")
    offset = 8
    long_names = b""
    members: dict[str, bytes] = {}
    while offset < len(data):
        if offset + 60 > len(data):
            raise AuditError("truncated GPU patch ar header")
        header = data[offset:offset + 60]
        if header[58:60] != b"`\n":
            raise AuditError("invalid GPU patch ar member trailer")
        try:
            size = int(header[48:58].decode("ascii").strip())
        except (UnicodeDecodeError, ValueError) as exc:
            raise AuditError("invalid GPU patch ar member size") from exc
        first = offset + 60
        last = first + size
        if last > len(data):
            raise AuditError("truncated GPU patch ar member")
        raw_name = header[:16].decode("ascii", errors="strict").strip()
        body = data[first:last]
        if raw_name == "//":
            long_names = body
        elif raw_name.startswith("/") and raw_name[1:].isdigit():
            name_offset = int(raw_name[1:])
            if name_offset >= len(long_names):
                raise AuditError("invalid GPU patch long-name offset")
            terminator = long_names.find(b"/\n", name_offset)
            if terminator < 0:
                raise AuditError("unterminated GPU patch long member name")
            name = long_names[name_offset:terminator].decode("utf-8")
            members[name] = body
        elif raw_name not in {"/", ""}:
            members[raw_name.rstrip("/")] = body
        offset = last + (size & 1)
    try:
        return members[wanted]
    except KeyError as exc:
        raise AuditError(f"GPU patch archive member missing: {wanted}") from exc


def _elf32_sections(data: bytes) -> dict[str, bytes]:
    """Extract named ELF32 section bodies needed for archive authentication."""

    if len(data) < 52 or data[:5] != b"\x7fELF\x01" or data[5] != 1:
        raise AuditError("GPU patch member is not little-endian ELF32")
    section_offset = struct.unpack_from("<I", data, 32)[0]
    entry_size, count, strings_index = struct.unpack_from("<HHH", data, 46)
    if entry_size != 40 or count == 0 or strings_index >= count:
        raise AuditError("invalid GPU patch ELF section table")
    if section_offset + count * entry_size > len(data):
        raise AuditError("truncated GPU patch ELF section table")
    headers = [
        struct.unpack_from("<IIIIIIIIII", data, section_offset + index * entry_size)
        for index in range(count)
    ]
    string_header = headers[strings_index]
    strings = data[string_header[4]:string_header[4] + string_header[5]]
    result: dict[str, bytes] = {}
    for header in headers:
        name_offset = header[0]
        if name_offset >= len(strings):
            raise AuditError("invalid GPU patch ELF section name")
        terminator = strings.find(b"\0", name_offset)
        if terminator < 0:
            raise AuditError("unterminated GPU patch ELF section name")
        name = strings[name_offset:terminator].decode("utf-8")
        body_offset, body_size = header[4], header[5]
        if body_offset + body_size > len(data):
            raise AuditError(f"truncated GPU patch ELF section: {name}")
        result[name] = data[body_offset:body_offset + body_size]
    return result


def _elf32_function_inventory(data: bytes, exports: set[str]) -> dict[str, dict[str, Any]]:
    """Recover exact function sections, symbols, and REL targets from ELF32."""

    if len(data) < 52 or data[:5] != b"\x7fELF\x01" or data[5] != 1:
        raise AuditError("GPU patch member is not little-endian ELF32")
    section_offset = struct.unpack_from("<I", data, 32)[0]
    entry_size, count, strings_index = struct.unpack_from("<HHH", data, 46)
    if entry_size != 40 or count == 0 or strings_index >= count:
        raise AuditError("invalid GPU patch ELF section table")
    if section_offset + count * entry_size > len(data):
        raise AuditError("truncated GPU patch ELF section table")
    headers = [
        struct.unpack_from("<IIIIIIIIII", data, section_offset + index * entry_size)
        for index in range(count)
    ]

    def table_string(table: bytes, offset: int, kind: str) -> str:
        if offset >= len(table):
            raise AuditError(f"invalid GPU patch ELF {kind} offset")
        terminator = table.find(b"\0", offset)
        if terminator < 0:
            raise AuditError(f"unterminated GPU patch ELF {kind}")
        return table[offset:terminator].decode("utf-8")

    names_header = headers[strings_index]
    section_strings = data[
        names_header[4]:names_header[4] + names_header[5]
    ]
    section_names = [
        table_string(section_strings, header[0], "section name")
        for header in headers
    ]
    symtab_indexes = [index for index, header in enumerate(headers) if header[1] == 2]
    if len(symtab_indexes) != 1:
        raise AuditError("GPU patch ELF must contain one symbol table")
    symtab = headers[symtab_indexes[0]]
    if symtab[6] >= count or symtab[9] != 16 or symtab[4] + symtab[5] > len(data):
        raise AuditError("invalid GPU patch ELF symbol table")
    strings_header = headers[symtab[6]]
    symbol_strings = data[
        strings_header[4]:strings_header[4] + strings_header[5]
    ]
    symbols: list[tuple[str, tuple[int, int, int, int, int, int]]] = []
    for offset in range(symtab[4], symtab[4] + symtab[5], symtab[9]):
        fields = struct.unpack_from("<IIIBBH", data, offset)
        name = table_string(symbol_strings, fields[0], "symbol name")
        if not name and fields[3] & 0x0F == 3 and fields[5] < count:
            name = section_names[fields[5]]
        symbols.append((name, fields))

    result: dict[str, dict[str, Any]] = {}
    for export in sorted(exports):
        matches = [(index, fields) for index, (name, fields) in enumerate(symbols) if name == export]
        if len(matches) != 1:
            raise AuditError(f"GPU patch export symbol census changed: {export}")
        _, symbol = matches[0]
        section_index = symbol[5]
        if section_index >= count:
            raise AuditError(f"GPU patch export section changed: {export}")
        section = headers[section_index]
        if section[4] + section[5] > len(data):
            raise AuditError(f"truncated GPU patch export section: {export}")
        body = data[section[4]:section[4] + section[5]]
        relocation_targets: list[str] = []
        for relocation in headers:
            if relocation[1] != 9 or relocation[7] != section_index:
                continue
            if relocation[9] != 8 or relocation[4] + relocation[5] > len(data):
                raise AuditError(f"invalid GPU patch relocation table: {export}")
            for offset in range(relocation[4], relocation[4] + relocation[5], 8):
                _, information = struct.unpack_from("<II", data, offset)
                symbol_index = information >> 8
                if symbol_index >= len(symbols):
                    raise AuditError(f"invalid GPU patch relocation symbol: {export}")
                relocation_targets.append(symbols[symbol_index][0])
        result[export] = {
            "section_size": len(body),
            "symbol_size": symbol[2],
            "section_sha256": hashlib.sha256(body).hexdigest(),
            "relocation_count": len(relocation_targets),
            "relocation_targets": sorted(set(relocation_targets)),
        }
    return result


def _resolve_sdk_component(sdk_root: Path) -> tuple[Path, Path | None]:
    component = sdk_root / "components/graphics/NemaGFX_SDK"
    if component.is_dir():
        return component, sdk_root / "mcu/am_sdk_version.h"
    if sdk_root.name == "NemaGFX_SDK" and sdk_root.is_dir():
        return sdk_root, None
    raise AuditError(
        "--sdk-root must be an AmbiqSuite root or its components/graphics/NemaGFX_SDK directory"
    )


def _audit_sdk(sdk_root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    component, sdk_version_header = _resolve_sdk_component(sdk_root)
    files = sorted(path for path in component.rglob("*") if path.is_file())
    file_count = len(files)
    byte_count = sum(path.stat().st_size for path in files)
    tree_sha1 = _git_tree_id(component).hex()
    state = manifest["public_source_state"]
    if file_count != state["file_count"] or byte_count != state["byte_count"]:
        raise AuditError("AmbiqSuite NemaGFX_SDK file/byte census changed")
    if tree_sha1 != state["subtree_git_tree_sha1"]:
        raise AuditError("AmbiqSuite NemaGFX_SDK Git tree changed")

    verified: list[dict[str, Any]] = []
    for item in manifest["selected_artifacts"]:
        relative = Path(item["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise AuditError(f"unsafe selected artifact path: {item['path']}")
        path = component / relative
        try:
            body = path.read_bytes()
        except OSError as exc:
            raise AuditError(f"cannot read selected SDK artifact {path}: {exc}") from exc
        digest = hashlib.sha256(body).hexdigest()
        blob = _git_object_id("blob", body).hex()
        if len(body) != item["size"] or digest != item["sha256"] or blob != item["git_blob_sha1"]:
            raise AuditError(f"selected SDK artifact changed: {item['path']}")
        verified.append(
            {"path": item["path"], "size": len(body), "sha256": digest, "git_blob_sha1": blob}
        )

    if sdk_version_header is not None:
        try:
            sdk_version = sdk_version_header.read_text(encoding="utf-8")
        except OSError as exc:
            raise AuditError(f"cannot read AmbiqSuite version header: {exc}") from exc
        required = (
            EXPECTED_SDK_REVISION,
            "#define AM_HAL_VERSION_MAJ      5",
            "#define AM_HAL_VERSION_MIN      1",
            "#define AM_HAL_VERSION_REV      0",
        )
        if any(token not in sdk_version for token in required):
            raise AuditError("AmbiqSuite 5.1.0 revision identity changed")

    archive = (component / "libraries/lib_nema_apollo5x_nemagfx.a").read_bytes()
    for marker in (
        b"GNU C99 13.2.1 20231009",
        b"-mcpu=cortex-m55",
        b"-march=armv8.1-m.main+fp.dp+mve.fp",
        b"third_party\\ThinkSi\\config\\apollo5b_nemagfx\\gcc",
        b"NemaGFX_SDK/NemaGFX/Nema/nema_blender.c",
    ):
        if marker not in archive:
            raise AuditError(f"Nema archive metadata marker changed: {marker!r}")

    patch_archive = (component / "extensions/gpu_patch.a").read_bytes()
    missing_exports = sorted(
        symbol for symbol in EXPECTED_GPU_PATCH_EXPORTS if symbol.encode("ascii") not in patch_archive
    )
    if missing_exports:
        raise AuditError(f"GPU patch archive export markers missing: {missing_exports}")
    patch_object = _ar_member(patch_archive, "ambiq_nema_extension.o")
    patch_sections = _elf32_sections(patch_object)
    for function, (_, size, digest) in EXPECTED_GPU_PATCH_ACCESSORS.items():
        section_name = ".text." + function
        try:
            body = patch_sections[section_name]
        except KeyError as exc:
            raise AuditError(f"GPU patch accessor section missing: {section_name}") from exc
        if len(body) != size or hashlib.sha256(body).hexdigest() != digest:
            raise AuditError(f"GPU patch accessor section changed: {function}")
    _, dashline_size, dashline_digest = EXPECTED_GPU_PATCH_DASHLINE
    dashline_body = patch_sections.get(".text.lv_ambiq_dashline_create", b"")
    if (
        len(dashline_body) != dashline_size
        or hashlib.sha256(dashline_body).hexdigest() != dashline_digest
    ):
        raise AuditError("GPU patch dash-line section changed")
    recovered_census = manifest["gpu_patch"]["binary_recovery"]["function_census"]
    expected_inventory = {
        item["function"]: {
            "section_size": item["section_size"],
            "symbol_size": item["symbol_size"],
            "section_sha256": item["section_sha256"],
            "relocation_count": item["relocation_count"],
            "relocation_targets": item["relocation_targets"],
        }
        for item in recovered_census
    }
    actual_inventory = _elf32_function_inventory(
        patch_object, EXPECTED_GPU_PATCH_EXPORTS
    )
    if actual_inventory != expected_inventory:
        raise AuditError("complete GPU patch function-section census changed")

    return {
        "sdk_root": str(sdk_root.resolve()),
        "sdk_revision": EXPECTED_SDK_REVISION if sdk_version_header is not None else None,
        "component_root": str(component.resolve()),
        "file_count": file_count,
        "byte_count": byte_count,
        "subtree_git_tree_sha1": tree_sha1,
        "selected_artifacts_verified": len(verified),
        "gpu_patch_functions_verified": len(actual_inventory),
    }


def audit(
    data: bytes,
    manifest: dict[str, Any],
    sdk_root: Path | None = None,
) -> dict[str, Any]:
    image_digest = hashlib.sha256(data).hexdigest()
    if len(data) != IMAGE_SIZE or image_digest != IMAGE_SHA256:
        raise AuditError("official G2 image identity changed")
    if _canonical_digest(manifest) != MANIFEST_CANONICAL_SHA256:
        raise AuditError("Nema/Ambiq provenance manifest changed")

    state = manifest.get("public_source_state", {})
    history = manifest.get("public_artifact_history", {})
    if manifest.get("repository") != EXPECTED_REPOSITORY:
        raise AuditError("public Ambiq repository identity changed")
    if state.get("first_complete_exact_commit") != EXPECTED_PUBLIC_COMMIT:
        raise AuditError("complete public NemaSDK commit changed")
    if state.get("subtree_git_tree_sha1") != EXPECTED_PUBLIC_TREE:
        raise AuditError("complete public NemaSDK tree changed")
    if history.get("apollo5_archive_first_commit", {}).get("commit") != EXPECTED_NEMA_ARCHIVE_COMMIT:
        raise AuditError("Apollo5 Nema archive origin commit changed")
    if history.get("gpu_patch_archive_first_commit", {}).get("commit") != EXPECTED_GPU_PATCH_COMMIT:
        raise AuditError("GPU patch origin commit changed")

    artifacts = manifest.get("selected_artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 10:
        raise AuditError("selected NemaSDK artifact census changed")
    paths = [item.get("path") for item in artifacts]
    if len(set(paths)) != len(paths):
        raise AuditError("selected NemaSDK artifact paths are not unique")
    for item in artifacts:
        if not isinstance(item.get("size"), int) or item["size"] <= 0:
            raise AuditError(f"invalid selected artifact size: {item.get('path')}")
        if len(item.get("sha256", "")) != 64 or len(item.get("git_blob_sha1", "")) != 40:
            raise AuditError(f"invalid selected artifact identity: {item.get('path')}")

    exports = set(manifest.get("gpu_patch", {}).get("exported_functions", []))
    required = set(manifest.get("gpu_patch", {}).get("functions_required_by_recovered_lvgl_subtree", []))
    if exports != EXPECTED_GPU_PATCH_EXPORTS or not required <= exports or len(required) != 6:
        raise AuditError("GPU patch export/requirement census changed")
    recovery = manifest.get("gpu_patch", {}).get("binary_recovery", {})
    if recovery.get("private_layouts") != EXPECTED_GPU_PRIVATE_LAYOUTS:
        raise AuditError("GPU patch private layout recovery changed")
    accessors = recovery.get("accessors", [])
    observed_accessors = {
        item.get("function"): (
            item.get("source_line"), item.get("section_size"), item.get("section_sha256")
        )
        for item in accessors
        if isinstance(item, dict)
    }
    if observed_accessors != EXPECTED_GPU_PATCH_ACCESSORS or len(accessors) != 3:
        raise AuditError("GPU patch accessor recovery changed")
    if recovery.get("dwarf_source") != "gpu_patch/ambiq_nema_extension.c":
        raise AuditError("GPU patch recovered source path changed")
    dashline = recovery.get("dashline", {})
    observed_dashline = (
        dashline.get("source_line"),
        dashline.get("section_size"),
        dashline.get("section_sha256"),
    )
    if observed_dashline != EXPECTED_GPU_PATCH_DASHLINE:
        raise AuditError("GPU patch dash-line recovery changed")
    if dashline.get("relocations") != 8 or dashline.get("function_relocations") != 7:
        raise AuditError("GPU patch dash-line relocation census changed")
    if dashline.get("variables") != ["dash_buffer_size_pixel", "ratio", "w"]:
        raise AuditError("GPU patch dash-line variable recovery changed")
    census = recovery.get("function_census", [])
    census_by_name = {
        item.get("function"): item for item in census if isinstance(item, dict)
    }
    if set(census_by_name) != EXPECTED_GPU_PATCH_EXPORTS or len(census) != 11:
        raise AuditError("complete GPU patch function census changed")
    for name, item in census_by_name.items():
        if (
            not isinstance(item.get("source_line"), int)
            or not isinstance(item.get("section_size"), int)
            or not isinstance(item.get("symbol_size"), int)
            or not isinstance(item.get("relocation_count"), int)
            or len(item.get("section_sha256", "")) != 64
            or item.get("relocation_targets") != sorted(set(item.get("relocation_targets", [])))
            or item.get("required_by_recovered_lvgl") != (name in required)
        ):
            raise AuditError(f"invalid GPU patch function census row: {name}")
    source_statuses = [item["source_status"] for item in census]
    if source_statuses.count("bounded-clean-room-candidate") != 11:
        raise AuditError("GPU patch source-candidate census changed")
    if source_statuses.count("exact-binary-only") != 0:
        raise AuditError("GPU patch binary-only census changed")
    glyph = recovery.get("get_glyph", {})
    if (
        glyph.get("source_line") != 818
        or glyph.get("glyph_size") != 0x24
        or glyph.get("range_size") != 0x0C
        or glyph.get("font_ranges_offset") != 0x04
    ):
        raise AuditError("GPU patch glyph lookup recovery changed")
    gradient = recovery.get("gradient", {})
    if (
        gradient.get("source_line") != 138
        or gradient.get("section_size") != 1_416
        or gradient.get("section_sha256")
        != "5870d79c49ee8bd0dfa4b5bf8f6f39b04ed45148c0c00b774467149292d83ae4"
        or gradient.get("relocations") != 16
        or gradient.get("recovered_lvgl_max_stops") != 2
    ):
        raise AuditError("GPU patch gradient recovery changed")
    shadow = recovery.get("shadow_blur_corner", {})
    if (
        shadow.get("source_line") != 383
        or shadow.get("section_size") != 668
        or shadow.get("section_sha256")
        != "cea1f3cb0efe575af62a887e8daec87479bc94807355f14df019cf02613faef8"
        or shadow.get("relocations") != 39
    ):
        raise AuditError("GPU patch shadow-blur recovery changed")
    small = recovery.get("small_raster", {})
    if small.get("functions") != [
        "lv_ambiq_create_corner_mask", "lv_ambiq_l8_l4_convert"
    ]:
        raise AuditError("GPU patch small-raster recovery changed")
    shadow_vg = recovery.get("shadow_blur_corner_vg", {})
    if (
        shadow_vg.get("source_line") != 454
        or shadow_vg.get("section_size") != 324
        or shadow_vg.get("section_sha256")
        != "a600d42433a84fe56934d36b167177bf1c617ce3cb8fafcbfecb9ca1948b9974"
        or shadow_vg.get("relocations") != 15
    ):
        raise AuditError("GPU patch VG shadow recovery changed")
    bitmap = recovery.get("bitmap_glyph", {})
    if (
        bitmap.get("source_line") != 590
        or bitmap.get("section_size") != 1_036
        or bitmap.get("section_sha256")
        != "37ad8ca8a082a00d04feae707022535448d1920940335db4819130901c47f0a1"
        or bitmap.get("relocations") != 34
    ):
        raise AuditError("GPU patch bitmap-glyph recovery changed")

    spans: dict[str, dict[str, Any]] = {}
    for name, (start, end, expected) in PINNED_SPANS.items():
        actual = hashlib.sha256(_slice(data, start, end)).hexdigest()
        if actual != expected:
            raise AuditError(f"stock Nema/Ambiq span changed: {name}")
        spans[name] = {
            "start": start,
            "end_exclusive": end,
            "size": end - start,
            "sha256": actual,
        }

    retained_paths: list[dict[str, Any]] = []
    for pointer_cell, (run, expected) in RETAINED_PATHS.items():
        if _word(data, pointer_cell) != run:
            raise AuditError(f"retained path pointer changed at 0x{pointer_cell:08X}")
        actual = _cstr(data, run)
        if actual != expected:
            raise AuditError(f"retained path changed at 0x{run:08X}")
        retained_paths.append({"pointer_cell": pointer_cell, "run": run, "path": actual})

    retained_strings: list[dict[str, Any]] = []
    for run, expected in RETAINED_STRINGS.items():
        actual = _cstr(data, run)
        if actual != expected:
            raise AuditError(f"retained Nema/Ambiq string changed at 0x{run:08X}")
        retained_strings.append({"run": run, "text": actual})

    config = manifest["stock_evidence"]["recovered_configuration"]
    if config != {
        "LV_USE_DRAW_AMBIQ": 1,
        "LV_USE_AMBIQ_VG": 1,
        "LV_AMBIQ_COMMAND_LIST_SECTOR": 100,
        "LV_AMBIQ_COMMAND_LIST_SECTOR_SIZE": 1024,
        "command_list_bytes": 102400,
        "NEMAGFX_POWER_SAVE": 1,
        "power_wake_retain_state": True,
    }:
        raise AuditError("recovered Ambiq/Nema configuration changed")
    if config["LV_AMBIQ_COMMAND_LIST_SECTOR"] * config["LV_AMBIQ_COMMAND_LIST_SECTOR_SIZE"] != config["command_list_bytes"]:
        raise AuditError("recovered command-list geometry is inconsistent")

    versions = manifest["ambiqsuite_candidate"]["versions"]
    if versions["nemagfx"]["semantic_version"] != "1.4.12":
        raise AuditError("NemaGFX version candidate changed")
    if versions["nemavg"]["semantic_version"] != "1.1.8":
        raise AuditError("NemaVG version candidate changed")

    sdk_report = _audit_sdk(sdk_root, manifest) if sdk_root is not None else None
    return {
        "schema_version": 1,
        "analysis_mode": "read-only; no hardware or flash operation",
        "image": {"size": len(data), "sha256": image_digest},
        "dependency_identity": {
            "repository": manifest["repository"],
            "public_reproduction_commit": EXPECTED_PUBLIC_COMMIT,
            "public_subtree_git_tree_sha1": EXPECTED_PUBLIC_TREE,
            "apollo5_archive_first_commit": EXPECTED_NEMA_ARCHIVE_COMMIT,
            "gpu_patch_first_commit": EXPECTED_GPU_PATCH_COMMIT,
            "ambiqsuite_version": manifest["ambiqsuite_candidate"]["sdk_version"],
            "ambiqsuite_revision": manifest["ambiqsuite_candidate"]["sdk_revision"],
            "nemagfx_version": versions["nemagfx"],
            "nemavg_version": versions["nemavg"],
        },
        "stock_configuration": config,
        "gpu_patch": manifest["gpu_patch"],
        "archive_metadata": manifest["archive_metadata"],
        "licenses": manifest["licenses"],
        "pinned_spans": spans,
        "retained_paths": retained_paths,
        "retained_strings": retained_strings,
        "sdk_candidate_verification": sdk_report,
        "integration_status": manifest["integration_status"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=IMAGE)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument(
        "--sdk-root",
        type=Path,
        help="optional AmbiqSuite 5.1.0 root (or NemaGFX_SDK component) to authenticate",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        report = audit(args.image.read_bytes(), _load_json(args.manifest), args.sdk_root)
    except (OSError, AuditError) as exc:
        parser.error(str(exc))
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        identity = report["dependency_identity"]
        config = report["stock_configuration"]
        print("G2 NemaGFX/Ambiq dependency audit: PASS")
        print(f"NemaGFX: {identity['nemagfx_version']['semantic_version']}")
        print(f"NemaVG: {identity['nemavg_version']['semantic_version']}")
        print(f"public reproduction commit: {identity['public_reproduction_commit']}")
        print(
            "command list: %d bytes (%d x %d)"
            % (
                config["command_list_bytes"],
                config["LV_AMBIQ_COMMAND_LIST_SECTOR"],
                config["LV_AMBIQ_COMMAND_LIST_SECTOR_SIZE"],
            )
        )
        if report["sdk_candidate_verification"] is not None:
            print(
                "SDK tree: "
                + report["sdk_candidate_verification"]["subtree_git_tree_sha1"]
            )
        print("hardware/flash operations: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
