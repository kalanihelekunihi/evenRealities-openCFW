#!/usr/bin/env python3
"""Authenticate and compile-qualify the G2 Ambiq LVGL draw backend.

This builder keeps the exact upstream source snapshots immutable.  It stages
the recovered LVGL compatibility ceiling, applies the separately authenticated
draw-buffer ABI patch and the narrow C-conformance patch, then compiles the 11
Ambiq translation units retained by G2 plus the cache-free radius-mask provider
for Cortex-M55.  The resulting archive is a qualification artifact, not a
production firmware admission: Nema archives, target stack qualification, and
live Apollo510 behavior remain external gates.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LVGL_ROOT = ROOT / "third_party/lvgl"
BACKEND_ROOT = ROOT / "third_party/lvgl-ambiq-backend"
NEMA_ROOT = ROOT / "third_party/nema-sdk-headers"
FREETYPE_ROOT = ROOT / "third_party/freetype"
APOLLO_ROOT = ROOT / "third_party/ambiqsuite-apollo510"
CMSIS_ROOT = ROOT / "third_party/cmsis-core/CMSIS/Core/Include"
SOURCE_MANIFEST = ROOT / "tools/manifests/g2-lvgl-ambiq-source-provenance.json"
NEMA_MANIFEST = ROOT / "tools/manifests/g2-nemagfx-ambiq-provenance.json"
ABI_PATCH = ROOT / "tools/patches/lvgl-g2-ambiq-draw-buffer-abi.patch"
HYBRID_PATCH = BACKEND_ROOT / "g2-compat/lvgl-g2-hybrid-compile.patch"
COMPAT_HEADER = BACKEND_ROOT / "g2-compat/lvgl_ambiq_nema_compat.h"
SW_MASK_COMPAT_HEADER = BACKEND_ROOT / "g2-compat/lvgl_ambiq_sw_mask_compat.h"
SW_MASK_PROVIDER = BACKEND_ROOT / "g2-compat/lvgl_ambiq_sw_mask_cache_free.c"
SW_MASK_UPSTREAM = BACKEND_ROOT / "g2-compat/upstream/lv_draw_sw_mask.c"
OFFICIAL_IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"

EXPECTED_BACKEND_TREE = "1e774257495fa43177e04fc5c8a42a77c2d7d619"
EXPECTED_BACKEND_FILES = 16
EXPECTED_BACKEND_BYTES = 170_833
EXPECTED_NEMA_FILES = 32
EXPECTED_NEMA_BYTES = 251_655
EXPECTED_NEMA_DIGEST = "186008f77de1bfa3942b4ad0de8f2a8932fcc834558fb1641d87e94f3ccd36a8"
EXPECTED_OFFICIAL_IMAGE = {
    "size": 3_523_396,
    "sha256": "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863",
    "load_base": 0x00437FE0,
}
EXPECTED_DRAW_THREAD_STACK = {
    "bytes": 32_768,
    "function_start": 0x004C73D6,
    "function_end": 0x004C74EE,
    "function_sha256": "7b7d08b910da49cd2484e09b80e18b3183c11cf356b7e6ea44d5eb1212da0c17",
    "argument_slice_start": 0x004C74CE,
    "argument_slice_end": 0x004C74EA,
    "argument_slice_hex": "206801904ff4004000900ff225232822dff85c1420682c300df093f8",
    "argument_slice_sha256": "2a3ef9a3527acc2d6ad14b5c6b823bf4e05ee8b550b1b295f5f1fa874ab56177",
    "thread_init_target": 0x004D4610,
}
NEMA_PAYLOAD_DIRECTORIES = (
    "headers/NemaGFX/Nema/",
    "headers/include/tsi/NemaGFX/",
    "headers/include/tsi/NemaVG/",
    "headers/include/tsi/common/",
)
NEMA_PAYLOAD_FILES = frozenset(
    {
        "extensions/gpu_patch.h",
        "headers/LICENSE",
        "port/nema_sys_defs.h",
    }
)
EXPECTED_PATCHES = {
    "lvgl-g2-ambiq-draw-buffer-abi.patch": "17dedb9b304817621a0312d8231aa7426732e089c88403ea6ace98e746d31e4b",
    "lvgl-g2-hybrid-compile.patch": "bd31e6967c795ba21a3c4320d30262fe71f0a297d6c2970979c51dbbb3cf6b7c",
    "lvgl_ambiq_nema_compat.h": "a1f5246e2546de30452071951d18047043ba0f5c94095f66c76af52e74aa449d",
    "lvgl_ambiq_sw_mask_compat.h": "5eefc7bd1ff7f58f228a03452a704c47141da84b3137629900b8ce6cec895f56",
    "lvgl_ambiq_sw_mask_cache_free.c": "b87383f4e05d775cb808e94851fdc8c99d27f7f9508e43454aad81ad20f3e643",
}
EXPECTED_SW_MASK_UPSTREAM = {
    "commit": "344c7c318047b7348e1be8572a9fd4260c251cfa",
    "path": "src/draw/sw/lv_draw_sw_mask.c",
    "size": 43_443,
    "sha256": "8a5075210d3a59c4fa7ea00e5675205a6a2e7e8e98305c26045c30c2e77846a6",
    "git_blob_sha1": "0e1a17a67f15e44fe294a26b18f7be5da7c2acb2",
}

# Exactly the Ambiq units named by the 11 retained G2 source paths.  The exact
# subtree also contains border, line, and vector units, but no retained path
# authenticates those three as linked into G2.
G2_LINKED_UNITS = (
    "lv_draw_ambiq.c",
    "lv_draw_ambiq_arc.c",
    "lv_draw_ambiq_box_shadow.c",
    "lv_draw_ambiq_buffer.c",
    "lv_draw_ambiq_fill.c",
    "lv_draw_ambiq_img.c",
    "lv_draw_ambiq_letter.c",
    "lv_draw_ambiq_mask_rect.c",
    "lv_draw_ambiq_private.c",
    "lv_draw_ambiq_triangle.c",
    "lv_draw_ambiq_vector_font.c",
)
QUALIFICATION_UNITS = G2_LINKED_UNITS + ("lvgl_ambiq_sw_mask_cache_free.c",)


class BuildError(RuntimeError):
    """Raised when source identity or Cortex-M55 compilation fails."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_blob(data: bytes) -> str:
    prefix = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(prefix + data, usedforsecurity=False).hexdigest()


def _git_tree(files: dict[str, bytes]) -> str:
    body = b"".join(
        b"100644 " + name.encode("utf-8") + b"\0" + bytes.fromhex(_git_blob(data))
        for name, data in sorted(files.items())
    )
    prefix = f"tree {len(body)}\0".encode("ascii")
    return hashlib.sha1(prefix + body, usedforsecurity=False).hexdigest()


def _inventory(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        data = path.read_bytes()
        rows.append(
            {
                "path": path.relative_to(root).as_posix(),
                "size": len(data),
                "sha256": _sha256(data),
                "git_blob_sha1": _git_blob(data),
            }
        )
    return rows


def _nema_payload_inventory(root: Path) -> list[dict[str, Any]]:
    """Inventory the authenticated interface payload, excluding local notes."""

    rows = _inventory(root)
    return [
        row
        for row in rows
        if row["path"] in NEMA_PAYLOAD_FILES
        or any(row["path"].startswith(prefix) for prefix in NEMA_PAYLOAD_DIRECTORIES)
    ]


def _canonical_digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return _sha256(encoded)


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise BuildError(f"cannot load {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise BuildError(f"JSON root is not an object: {path}")
    return value


def audit_inputs(
    backend_root: Path = BACKEND_ROOT,
    nema_root: Path = NEMA_ROOT,
    source_manifest: Path = SOURCE_MANIFEST,
    nema_manifest: Path = NEMA_MANIFEST,
    official_image: Path = OFFICIAL_IMAGE,
) -> dict[str, Any]:
    source = _load_json(source_manifest)
    candidates = source.get("candidate_files")
    if not isinstance(candidates, list) or len(candidates) != EXPECTED_BACKEND_FILES:
        raise BuildError("Ambiq source manifest census changed")

    source_dir = backend_root / "src/draw/ambiq"
    actual_names = {path.name for path in source_dir.iterdir() if path.is_file()}
    expected_names = {Path(item["path"]).name for item in candidates}
    if actual_names != expected_names:
        raise BuildError("Ambiq source snapshot path set changed")

    tree_files: dict[str, bytes] = {}
    for item in candidates:
        path = backend_root / item["path"]
        data = path.read_bytes()
        if len(data) != item["size"] or _sha256(data) != item["sha256"]:
            raise BuildError(f"Ambiq source identity changed: {item['path']}")
        if _git_blob(data) != item["git_blob_sha1"]:
            raise BuildError(f"Ambiq Git blob identity changed: {item['path']}")
        tree_files[path.name] = data
    if sum(len(data) for data in tree_files.values()) != EXPECTED_BACKEND_BYTES:
        raise BuildError("Ambiq source byte census changed")
    if _git_tree(tree_files) != EXPECTED_BACKEND_TREE:
        raise BuildError("Ambiq source subtree identity changed")

    license_info = source.get("license", {})
    license_data = (backend_root / "LICENCE.txt").read_bytes()
    if (
        len(license_data) != license_info.get("size")
        or _sha256(license_data) != license_info.get("sha256")
        or _git_blob(license_data) != license_info.get("git_blob_sha1")
    ):
        raise BuildError("Ambiq LVGL license identity changed")

    nema_rows = _nema_payload_inventory(nema_root)
    if len(nema_rows) != EXPECTED_NEMA_FILES:
        raise BuildError("Nema interface file census changed")
    if sum(item["size"] for item in nema_rows) != EXPECTED_NEMA_BYTES:
        raise BuildError("Nema interface byte census changed")
    if _canonical_digest(nema_rows) != EXPECTED_NEMA_DIGEST:
        raise BuildError("Nema interface snapshot identity changed")

    public_nema = _load_json(nema_manifest)
    selected = {item["path"]: item for item in public_nema.get("selected_artifacts", [])}
    for relative in (
        "headers/LICENSE",
        "headers/include/tsi/NemaGFX/nema_version.h",
        "headers/include/tsi/NemaVG/nema_vg_version.h",
        "extensions/gpu_patch.h",
        "port/nema_sys_defs.h",
    ):
        item = selected.get(relative)
        data = (nema_root / relative).read_bytes()
        if item is None or len(data) != item["size"] or _sha256(data) != item["sha256"]:
            raise BuildError(f"selected Nema artifact identity changed: {relative}")

    patch_paths = {
        "lvgl-g2-ambiq-draw-buffer-abi.patch": ABI_PATCH,
        "lvgl-g2-hybrid-compile.patch": HYBRID_PATCH,
        "lvgl_ambiq_nema_compat.h": COMPAT_HEADER,
        "lvgl_ambiq_sw_mask_compat.h": SW_MASK_COMPAT_HEADER,
        "lvgl_ambiq_sw_mask_cache_free.c": SW_MASK_PROVIDER,
    }
    for name, path in patch_paths.items():
        if _sha256(path.read_bytes()) != EXPECTED_PATCHES[name]:
            raise BuildError(f"G2 Ambiq compatibility input changed: {name}")

    upstream_mask = SW_MASK_UPSTREAM.read_bytes()
    if (
        len(upstream_mask) != EXPECTED_SW_MASK_UPSTREAM["size"]
        or _sha256(upstream_mask) != EXPECTED_SW_MASK_UPSTREAM["sha256"]
        or _git_blob(upstream_mask) != EXPECTED_SW_MASK_UPSTREAM["git_blob_sha1"]
    ):
        raise BuildError("authenticated upstream LVGL radius-mask source changed")

    image = official_image.read_bytes()
    if (
        len(image) != EXPECTED_OFFICIAL_IMAGE["size"]
        or _sha256(image) != EXPECTED_OFFICIAL_IMAGE["sha256"]
    ):
        raise BuildError("official G2 firmware image identity changed")
    load_base = EXPECTED_OFFICIAL_IMAGE["load_base"]
    function = image[
        EXPECTED_DRAW_THREAD_STACK["function_start"] - load_base:
        EXPECTED_DRAW_THREAD_STACK["function_end"] - load_base
    ]
    argument_slice = image[
        EXPECTED_DRAW_THREAD_STACK["argument_slice_start"] - load_base:
        EXPECTED_DRAW_THREAD_STACK["argument_slice_end"] - load_base
    ]
    if _sha256(function) != EXPECTED_DRAW_THREAD_STACK["function_sha256"]:
        raise BuildError("stock lv_draw_ambiq_init function identity changed")
    if (
        argument_slice.hex() != EXPECTED_DRAW_THREAD_STACK["argument_slice_hex"]
        or _sha256(argument_slice) != EXPECTED_DRAW_THREAD_STACK["argument_slice_sha256"]
    ):
        raise BuildError("stock draw-thread stack argument evidence changed")

    return {
        "schema_version": 1,
        "analysis_mode": "offline source authentication and target compile; no hardware or flash operation",
        "component": "G2 Ambiq LVGL draw backend source readiness",
        "source": {
            "repository": source["repository"],
            "canonical_commit": source["source_state"]["canonical_default_branch_commit"],
            "equivalent_replay_commit": source["source_state"]["equivalent_replay_commit"],
            "subtree_git_tree_sha1": EXPECTED_BACKEND_TREE,
            "files": EXPECTED_BACKEND_FILES,
            "bytes": EXPECTED_BACKEND_BYTES,
            "linked_g2_translation_units": list(G2_LINKED_UNITS),
        },
        "nema_interface": {
            "repository": public_nema["repository"],
            "reproduction_commit": public_nema["public_source_state"]["first_complete_exact_commit"],
            "full_sdk_subtree_git_tree_sha1": public_nema["public_source_state"]["subtree_git_tree_sha1"],
            "imported_interface_files": EXPECTED_NEMA_FILES,
            "imported_interface_bytes": EXPECTED_NEMA_BYTES,
            "imported_interface_digest": EXPECTED_NEMA_DIGEST,
            "nemagfx_version": public_nema["ambiqsuite_candidate"]["versions"]["nemagfx"]["semantic_version"],
            "nemavg_version": public_nema["ambiqsuite_candidate"]["versions"]["nemavg"]["semantic_version"],
        },
        "compatibility_inputs": EXPECTED_PATCHES,
        "cache_free_radius_mask": {
            "upstream": {
                **EXPECTED_SW_MASK_UPSTREAM,
                "repository": "https://github.com/lvgl/lvgl.git",
            },
            "provider": {
                "path": "third_party/lvgl-ambiq-backend/g2-compat/lvgl_ambiq_sw_mask_cache_free.c",
                "sha256": EXPECTED_PATCHES["lvgl_ambiq_sw_mask_cache_free.c"],
                "exports": [
                    "lv_draw_sw_mask_radius_init",
                    "lv_draw_sw_mask_free_param",
                ],
                "global_cache_dependency": False,
                "maximum_representable_radius": 65_535,
                "g2_display": {"width": 576, "height": 288},
                "arm_parameter_size": 36,
                "arm_circle_descriptor_size": 28,
                "arm_parameter_offsets": {"cfg": 8, "radius": 24, "circle": 32},
                "host_verification_contract": {
                    "authenticated_reference_parity_cases": 1_505,
                    "allocation_failure_sites": 3,
                    "maximum_visible_g2_radius": 144,
                    "peak_allocation_upper_bound_bytes": 3_296,
                    "allocation_failure_result": "transparent with output buffer unchanged",
                },
            },
        },
        "draw_thread_stack": {
            "bytes": EXPECTED_DRAW_THREAD_STACK["bytes"],
            "source_macro": "LV_DRAW_THREAD_STACK_SIZE",
            "official_image": {
                "path": "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin",
                "size": EXPECTED_OFFICIAL_IMAGE["size"],
                "sha256": EXPECTED_OFFICIAL_IMAGE["sha256"],
                "load_base": f"0x{load_base:08X}",
            },
            "stock_function": {
                "name": "lv_draw_ambiq_init",
                "start": f"0x{EXPECTED_DRAW_THREAD_STACK['function_start']:08X}",
                "end_exclusive": f"0x{EXPECTED_DRAW_THREAD_STACK['function_end']:08X}",
                "size": len(function),
                "sha256": EXPECTED_DRAW_THREAD_STACK["function_sha256"],
            },
            "argument_evidence": {
                "start": f"0x{EXPECTED_DRAW_THREAD_STACK['argument_slice_start']:08X}",
                "end_exclusive": f"0x{EXPECTED_DRAW_THREAD_STACK['argument_slice_end']:08X}",
                "bytes_hex": EXPECTED_DRAW_THREAD_STACK["argument_slice_hex"],
                "sha256": EXPECTED_DRAW_THREAD_STACK["argument_slice_sha256"],
                "decoded_sequence": "mov.w r0,#0x8000; str r0,[sp]; ...; bl lv_thread_init",
                "argument_role": "AAPCS fifth argument to lv_thread_init",
                "thread_init_target": f"0x{EXPECTED_DRAW_THREAD_STACK['thread_init_target']:08X}",
            },
            "hardware_stack_qualified": False,
        },
        "software_status": {
            "exact_source_imported": True,
            "active_g2_translation_units": len(G2_LINKED_UNITS),
            "cache_free_radius_mask_provider": True,
            "cortex_m55_compile_gate": "enforced by this builder",
            "lv_draw_sw_complex": 0,
            "production_overlay_registered": False,
            "production_ready": False,
        },
        "remaining_gates": [
            "atomic link admission of the public NemaGFX/NemaVG and GPU-patch archives or admitted source equivalents",
            "32 KiB draw-thread worst-case and runtime stack qualification with FreeType enabled",
            "stock-IAR versus maintained-GNU archive policy",
            "Apollo510 command-list, cache, power-retention, antialiasing, and display-output hardware validation",
        ],
    }


def _run(command: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode != 0:
        raise BuildError(f"command failed ({result.returncode}): {' '.join(command)}\n{result.stdout}")
    return result.stdout


def _llvm_tool(name: str) -> str:
    direct = shutil.which(name)
    if direct is not None:
        return direct
    xcrun = shutil.which("xcrun")
    if xcrun is not None:
        result = subprocess.run(
            [xcrun, "-f", name], text=True, capture_output=True, check=False
        )
        candidate = result.stdout.strip()
        if result.returncode == 0 and Path(candidate).is_file():
            return candidate
    raise BuildError(f"Cortex-M55 relocation gate requires {name}")


def _external_symbols(nm: str, obj: Path, *, undefined: bool) -> set[str]:
    options = ["--undefined-only"] if undefined else ["--defined-only", "--extern-only"]
    output = _run([nm, *options, str(obj)])
    return {
        line.split()[-1]
        for line in output.splitlines()
        if line.strip() and not line.rstrip().endswith(":")
    }


def _write_stubs(root: Path) -> None:
    stubs = {
        "inttypes.h": "#include <stdint.h>\n#define PRIu32 \"u\"\n#define PRId32 \"d\"\n#define PRIx32 \"x\"\n#define PRIX32 \"X\"\n#define PRIu64 \"llu\"\n#define PRId64 \"lld\"\n",
        "stdio.h": "int printf(const char *, ...);\n",
        "math.h": "#define M_PI 3.14159265358979323846\n#define M_PI_2 1.57079632679489661923\ndouble fmod(double, double);\ndouble sqrt(double);\nfloat sqrtf(float);\nfloat sinf(float);\nfloat cosf(float);\nfloat atan2f(float, float);\nfloat fabsf(float);\nfloat roundf(float);\n",
        "stdlib.h": "#include <stddef.h>\nvoid *malloc(size_t);\nvoid free(void *);\n",
        "string.h": "#include <stddef.h>\nvoid *memcpy(void *, const void *, size_t);\nvoid *memset(void *, int, size_t);\n",
        "setjmp.h": "typedef int jmp_buf[32];\nint setjmp(jmp_buf);\nvoid longjmp(jmp_buf, int);\n",
        "limits.h": "#define CHAR_BIT 8\n#define INT_MAX 2147483647\n#define INT_MIN (-INT_MAX-1)\n#define UINT_MAX 4294967295U\n#define LONG_MAX 2147483647L\n#define LONG_MIN (-LONG_MAX-1L)\n#define ULONG_MAX 4294967295UL\n",
        "FreeRTOS.h": "#include <stdint.h>\ntypedef int BaseType_t;\ntypedef unsigned int UBaseType_t;\ntypedef uint32_t TickType_t;\ntypedef void *TaskHandle_t;\ntypedef void *SemaphoreHandle_t;\n#define portMAX_DELAY UINT32_MAX\n",
        "task.h": "#include \"FreeRTOS.h\"\nBaseType_t xTaskNotifyWait(uint32_t, uint32_t, uint32_t *, TickType_t);\n",
        "semphr.h": "#include \"FreeRTOS.h\"\n",
    }
    root.mkdir(parents=True)
    for name, text in stubs.items():
        guard = "OPENCFW_STUB_" + name.replace(".", "_").upper()
        (root / name).write_text(f"#ifndef {guard}\n#define {guard}\n{text}#endif\n", encoding="ascii")


def _stage_tree(stage: Path, backend_root: Path = BACKEND_ROOT) -> Path:
    lvgl = stage / "lvgl"
    shutil.copytree(LVGL_ROOT, lvgl)
    ambiq = lvgl / "src/draw/ambiq"
    shutil.copytree(backend_root / "src/draw/ambiq", ambiq)
    shutil.copy2(COMPAT_HEADER, ambiq / COMPAT_HEADER.name)
    shutil.copy2(SW_MASK_COMPAT_HEADER, ambiq / SW_MASK_COMPAT_HEADER.name)
    shutil.copy2(SW_MASK_PROVIDER, ambiq / SW_MASK_PROVIDER.name)
    _run(["patch", "-s", "-p1", "-i", str(ABI_PATCH)], cwd=lvgl)
    _run(["patch", "-s", "-p1", "-i", str(HYBRID_PATCH)], cwd=lvgl)
    return lvgl


def _compiler_flags(clang: str, stage: Path, lvgl: Path, stubs: Path) -> list[str]:
    nema_includes = (
        NEMA_ROOT / "port",
        NEMA_ROOT / "headers/include/tsi/NemaGFX",
        NEMA_ROOT / "headers/include/tsi/NemaVG",
        NEMA_ROOT / "headers/include/tsi/common",
        NEMA_ROOT / "headers/NemaGFX/Nema",
        NEMA_ROOT / "extensions",
    )
    includes = (
        stubs,
        lvgl,
        lvgl / "src",
        FREETYPE_ROOT / "include",
        APOLLO_ROOT / "mcu/apollo510",
        APOLLO_ROOT / "CMSIS/AmbiqMicro/Include",
        CMSIS_ROOT,
        *nema_includes,
    )
    macros = (
        "LV_CONF_SKIP=1",
        "LV_COLOR_DEPTH=8",
        "LV_USE_OS=LV_OS_FREERTOS",
        "LV_USE_FREETYPE=1",
        "LV_USE_FLEX=1",
        "LV_USE_GRID=1",
        "LV_USE_FS_LITTLEFS=1",
        "LV_USE_BMP=1",
        "LV_USE_LOG=1",
        "LV_LOG_LEVEL=LV_LOG_LEVEL_WARN",
        "LV_USE_ASSERT_NULL=1",
        "LV_BIG_ENDIAN_SYSTEM=0",
        # Preserve G2's authenticated cache-free lv_global layout.  The local
        # compatibility provider owns radius-mask circle state per parameter.
        "LV_DRAW_SW_COMPLEX=0",
        # Recovered from the authenticated stock lv_draw_ambiq_init machine code.
        "LV_DRAW_THREAD_STACK_SIZE=32768",
        "LV_USE_STDLIB_MALLOC=LV_STDLIB_CUSTOM",
        "LV_USE_SPAN=1",
        "LV_USE_OBJ_ID_BUILTIN=1",
        "LV_USE_DRAW_AMBIQ=1",
        "LV_USE_AMBIQ_VG=1",
        "LV_USE_VECTOR_GRAPHIC=1",
        "LV_USE_MATRIX=1",
        "LV_USE_FLOAT=1",
        "LV_AMBIQ_COMMAND_LIST_SECTOR=100",
        "LV_AMBIQ_COMMAND_LIST_SECTOR_SIZE=1024",
        "NEMAGFX_POWER_SAVE=1",
    )
    return [
        clang,
        "--target=arm-none-eabi",
        "-mcpu=cortex-m55",
        "-mthumb",
        "-ffreestanding",
        "-fshort-enums",
        "-std=gnu11",
        "-O2",
        "-ffunction-sections",
        "-fdata-sections",
        "-fno-common",
        f"-ffile-prefix-map={stage}=/openCFW/g2/lvgl-ambiq-stage",
        "-Werror=implicit-function-declaration",
        "-Werror=return-type",
        "-Werror=incompatible-pointer-types",
        *[item for path in includes for item in ("-I", str(path))],
        *[f"-D{macro}" for macro in macros],
    ]


def compile_backend(
    output_dir: Path,
    clang: str | None = None,
) -> dict[str, Any]:
    # Keep the callable API fail-closed too; callers must not be able to bypass
    # the source and interface identity gate by invoking compile_backend()
    # directly instead of going through main().
    audit_inputs()
    clang = clang or os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
    if clang is None:
        raise BuildError("Cortex-M55 compile requires clang")

    output_dir.mkdir(parents=True, exist_ok=True)
    llvm_nm = _llvm_tool("llvm-nm")
    llvm_objdump = _llvm_tool("llvm-objdump")
    with tempfile.TemporaryDirectory(prefix="opencfw-lvgl-ambiq-build-") as temp:
        stage = Path(temp)
        lvgl = _stage_tree(stage)
        stubs = stage / "stubs"
        _write_stubs(stubs)
        objects = output_dir / "objects"
        objects.mkdir(parents=True, exist_ok=True)
        flags = _compiler_flags(clang, stage, lvgl, stubs)
        compile_output: list[str] = []
        object_rows: list[dict[str, Any]] = []
        for unit in QUALIFICATION_UNITS:
            source = lvgl / "src/draw/ambiq" / unit
            obj = objects / (Path(unit).stem + ".o")
            compile_output.append(_run([*flags, "-c", str(source), "-o", str(obj)], cwd=stage))
            data = obj.read_bytes()
            object_rows.append({"unit": unit, "size": len(data), "sha256": _sha256(data)})

        abi_source = stage / "radius-mask-abi.c"
        abi_source.write_text(
            "#include <stddef.h>\n"
            "#include \"src/draw/ambiq/lvgl_ambiq_sw_mask_compat.h\"\n"
            "_Static_assert(sizeof(lv_draw_sw_mask_common_dsc_t) == 8, \"common ABI\");\n"
            "_Static_assert(sizeof(lv_draw_sw_mask_radius_circle_dsc_t) == 28, \"circle ABI\");\n"
            "_Static_assert(sizeof(lv_draw_sw_mask_radius_param_t) == 36, \"parameter ABI\");\n"
            "_Static_assert(offsetof(lv_draw_sw_mask_radius_param_t, cfg) == 8, \"cfg ABI\");\n"
            "_Static_assert(offsetof(lv_draw_sw_mask_radius_param_t, cfg.radius) == 24, \"radius ABI\");\n"
            "_Static_assert(offsetof(lv_draw_sw_mask_radius_param_t, circle) == 32, \"circle pointer ABI\");\n",
            encoding="ascii",
        )
        abi_object = output_dir / "radius-mask-abi.o"
        compile_output.append(
            _run([*flags, "-c", str(abi_source), "-o", str(abi_object)], cwd=stage)
        )

        box_shadow = objects / "lv_draw_ambiq_box_shadow.o"
        provider = objects / "lvgl_ambiq_sw_mask_cache_free.o"
        required_radius_symbols = {
            "lv_draw_sw_mask_free_param",
            "lv_draw_sw_mask_radius_init",
        }
        box_undefined = _external_symbols(llvm_nm, box_shadow, undefined=True)
        provider_defined = _external_symbols(llvm_nm, provider, undefined=False)
        if not required_radius_symbols.issubset(box_undefined):
            raise BuildError("Ambiq box shadow radius-mask imports changed")
        if not required_radius_symbols.issubset(provider_defined):
            raise BuildError("cache-free radius-mask exports changed")
        relocation_output = _run([llvm_objdump, "-r", str(box_shadow)])
        relocation_rows = [
            line.strip()
            for line in relocation_output.splitlines()
            if any(symbol in line for symbol in required_radius_symbols)
        ]
        for symbol in required_radius_symbols:
            rows = [line for line in relocation_rows if symbol in line]
            if len(rows) != 1 or "R_ARM_THM_CALL" not in rows[0]:
                raise BuildError(f"Ambiq box shadow relocation changed: {symbol}")

        provider_undefined = _external_symbols(llvm_nm, provider, undefined=True)
        expected_provider_undefined = {
            "lv_free",
            "lv_malloc",
            "lv_malloc_zeroed",
            "lv_memset",
        }
        if provider_undefined != expected_provider_undefined:
            raise BuildError(
                "cache-free radius-mask provider imports changed: "
                + ", ".join(sorted(provider_undefined))
            )

        archive = output_dir / "libopen_cfw_lvgl_ambiq_backend.a"
        archive_data = bytearray(b"!<arch>\n")
        for unit in QUALIFICATION_UNITS:
            obj = objects / (Path(unit).stem + ".o")
            name = obj.name.encode("ascii")
            data = obj.read_bytes()
            member_size = len(name) + len(data)
            # Deterministic BSD extended-name ar member.  An integration
            # toolchain must add its target-specific symbol index; this
            # qualification archive intentionally carries no host ranlib
            # table because macOS ranlib rejects Cortex-M ELF objects.
            fields = (
                f"#1/{len(name)}".encode("ascii").ljust(16),
                b"0".ljust(12),
                b"0".ljust(6),
                b"0".ljust(6),
                b"100644".ljust(8),
                str(member_size).encode("ascii").ljust(10),
                b"`\n",
            )
            header = b"".join(fields)
            if len(header) != 60:
                raise BuildError("internal ar header size changed")
            body = name + data
            archive_data.extend(header)
            archive_data.extend(body)
            if len(body) & 1:
                archive_data.extend(b"\n")
        archive.write_bytes(archive_data)
        warnings = [
            line.strip()
            for line in "\n".join(compile_output).splitlines()
            if "warning:" in line
        ]
        if warnings:
            raise BuildError(
                "unexpected Ambiq backend compile warning:\n"
                + "\n".join(warnings)
            )
        return {
            "compiler": _run([clang, "--version"]).splitlines()[0],
            "target": "arm-none-eabi/cortex-m55/thumb/short-enums/gnu11",
            "objects": object_rows,
            "object_count": len(object_rows),
            "object_bytes": sum(item["size"] for item in object_rows),
            "archive": {
                "path": archive.name,
                "size": len(archive_data),
                "sha256": _sha256(bytes(archive_data)),
                "member_count": len(QUALIFICATION_UNITS),
                "symbol_index": False,
            },
            "radius_mask": {
                "abi_object_size": abi_object.stat().st_size,
                "abi_object_sha256": _sha256(abi_object.read_bytes()),
                "box_shadow_imports": sorted(required_radius_symbols),
                "provider_exports": sorted(required_radius_symbols),
                "provider_external_dependencies": sorted(provider_undefined),
                "box_shadow_relocations": relocation_rows,
                "global_cache_dependency": False,
            },
            "warning_count": len(warnings),
            "warnings": warnings,
            "unresolved_stack_warning_count": 0,
            "qualification_only": True,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--write-manifest", type=Path)
    parser.add_argument("--clang")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        report = audit_inputs()
        if args.output_dir is not None:
            report["compile"] = compile_backend(args.output_dir, args.clang)
            (args.output_dir / "build-report.json").write_text(
                json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
        if args.write_manifest is not None:
            args.write_manifest.parent.mkdir(parents=True, exist_ok=True)
            args.write_manifest.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except (OSError, BuildError) as exc:
        parser.error(str(exc))

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("G2 Ambiq LVGL backend source readiness: PASS")
        print(f"  exact subtree: {report['source']['subtree_git_tree_sha1']}")
        print(f"  linked units: {report['software_status']['active_g2_translation_units']}")
        if "compile" in report:
            print(f"  Cortex-M55 objects: {report['compile']['object_count']}")
            print(f"  qualification archive: {report['compile']['archive']['sha256']}")
        print("  production overlay: not registered")
        print("  hardware/flash operations: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
