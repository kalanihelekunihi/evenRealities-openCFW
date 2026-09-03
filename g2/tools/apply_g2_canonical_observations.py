#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Verify or atomically admit reproducible G2 Apollo canonical observations.

This tool never compiles, signs, flashes, or contacts a device.  It consumes
two independently recorded receipts for each supported toolchain, proves that
they describe one unchanged source generation, reconstructs the Apple region
map, and prepares one transactional config/manifest/live-Apple-generation
publication.  Writes require the explicit ``--apply`` switch; verification is
the default.
"""

from __future__ import annotations

import argparse
import copy
import errno
import fcntl
import importlib.util
import json
import os
import re
import secrets
import stat
import subprocess
import sys
import zlib
from hashlib import sha256
from contextlib import contextmanager
from pathlib import Path
from typing import Any


G2_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = G2_ROOT
CORE_CONFIG = G2_ROOT / "components/apollo_main/core_overlay/overlay.json"
CORE_MANIFEST = G2_ROOT / "manifests/g2-2.2.6.10-core-source.json"
APPLE_PROFILE = "apple-clang"
LINUX_PROFILE = "linux-clang"
IMU_RUNTIME_START = 0x004A35B0
IMU_RUNTIME_END = 0x004A6644
FORBIDDEN_APPENDED_PREFIX = "imu_icm45608_"
FORBIDDEN_SOURCE_MARKERS = (
    "third_party/invensense",
    "imu_icm45608.c",
    "imu_icm45608.h",
)
PT_SOURCE_PROVIDER_ROUTE_COUNT = 40
PT_STOCK_DIRECT_SITE = 0x00538716
PT_SOURCE_UART_ENTRY_REDIRECT = 0x0053A0B6
PT_RETIRED_SOURCE_UART_SITES = (0x0053A218, 0x0053A356)
PT_LEGACY_ENTRY = 0x0056F4A0
PT_LEGACY_POSTPROCESS = 0x0056F92C
PT_THUMB_NOP_PAIR = b"\x00\xbf\x00\xbf"
PT_DONOR_INGRESS_SHA256 = {
    PT_STOCK_DIRECT_SITE: (
        "267faa858eddf585c646efe4df6ce8542d4b7195fcf160f4e06aae2be5ed6027"
    ),
    PT_RETIRED_SOURCE_UART_SITES[0]: (
        "62465f14c927473c321cc2a74d6dd5053712946f5f33f80d10f20ea4840f67e3"
    ),
    PT_RETIRED_SOURCE_UART_SITES[1]: (
        "420d937eec298e2ce5cd1e318f597363c60093ace0238a59a1c46a86a3b9d924"
    ),
}
PT_DONOR_INGRESS_EVIDENCE = "authenticated donor BL retained byte-for-byte"
PT_SOURCE_UART_EVIDENCE = "authenticated core-stage relocation to legacy ABI"
PT_AGGREGATE_LICENSE = "MIT AND Apache-2.0"
PT_APACHE_SOURCE = (
    "components/apollo_main/core_overlay/pt_protocol_lc3_setup.c"
)
PT_SOURCE_LICENSE_COUNTS = {"MIT": 28, "Apache-2.0": 1}
PT_APACHE_SOURCE_METADATA = {
    "upstream": "Google/liblc3",
    "upstream_commit": "96a3af0beb5487aca3b98a4b992a539a1f6d80d1",
    "license_path": "third_party/liblc3/LICENSE",
    "license_sha256": (
        "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"
    ),
}
DEFERRED_HARDWARE_POLICY = {
    "validation": "blocked by unavailable physical evidence",
    "qualification_complete": False,
}
LIBLC3_HISTORICAL_NON_CORPUS_ROUTING = {
    "0x00438400": False,
    "0x00438604": False,
}
CFF_LICENSE = "FTL AND MIT"
CFF_SECTION_NAMES = (
    ".cff_stock_rodata", ".cff_stock_text",
    ".cff_tail_text", ".cff_tail_exidx",
)
CFF_STOCK_CLASS_BYTES = bytes.fromhex("74cb6d00")
CFF_REPLACEMENT_CLASS_BYTES = bytes.fromhex("14c05a00")
CFF_UPDATE_FLAG = 0x007FE000

# Reviewed compatibility aliases whose historical rows describe one exact
# closure-rodata part.  These are identities, not suffix heuristics.
LEGACY_RODATA_ALIASES = {
    "open_cfw_g2_easylogger_async_record_build_single_owner": "apollo_easylogger_async_record_builder_source_rodata",
    "open_cfw_easylogger_output": "apollo_easylogger_output_source_rodata",
    "open_cfw_g2_easylogger_async_record_build_level_less_single_owner": "apollo_easylogger_level_less_record_builder_source_rodata",
    "open_cfw_easylogger_hexdump": "apollo_easylogger_hexdump_source_rodata",
    "open_cfw_nanopb_decode_varint": "apollo_nanopb_decode_varint_source_rodata",
    "open_cfw_freertos_cli_console_process_command": "apollo_freertos_cli_console_process_command_source_rodata",
    "open_cfw_nanopb_decode_varint32_eof": "apollo_nanopb_decode_varint32_overflow_rodata",
    "open_cfw_nanopb_skip_field": "apollo_nanopb_skip_field_error_rodata",
    "open_cfw_nanopb_read_raw_value": "apollo_nanopb_read_raw_value_error_rodata",
    "open_cfw_nanopb_make_string_substream": "apollo_nanopb_make_string_substream_error_rodata",
    "open_cfw_nanopb_dec_varint": "apollo_nanopb_dec_varint_error_rodata",
    "open_cfw_nanopb_dec_bytes": "apollo_nanopb_dec_bytes_error_rodata",
    "open_cfw_nanopb_dec_string": "apollo_nanopb_dec_string_error_rodata",
    "open_cfw_nanopb_dec_submessage": "apollo_nanopb_dec_submessage_error_rodata",
    "open_cfw_nanopb_decode_inner": "apollo_nanopb_decode_inner_error_rodata",
    "open_cfw_kvdb_als_scale_load_and_migrate": "kvdb_als_scale_load_and_migrate_source_rodata",
    "open_cfw_kvdb_write_als_scale": "kvdb_write_als_scale_source_rodata",
    "open_cfw_nvdb_sensor_caldata_check": "nvdb_sensor_caldata_check_source_rodata",
    "open_cfw_kvdb_write_setting": "kvdb_write_setting_source_rodata",
    "open_cfw_kvdb_setting_load_and_migrate": "kvdb_setting_load_and_migrate_source_rodata",
    "open_cfw_kvdb_write_time": "kvdb_write_time_source_rodata",
    "open_cfw_kvdb_time_load_and_migrate": "kvdb_time_load_and_migrate_source_rodata",
    "open_cfw_kvdb_write_time_format": "kvdb_write_time_format_source_rodata",
    "open_cfw_kvdb_time_format_load_and_migrate": "kvdb_time_format_load_and_migrate_source_rodata",
    "open_cfw_kvdb_write_temperature_unit": "kvdb_write_temperature_unit_source_rodata",
    "open_cfw_kvdb_temperature_unit_load_and_migrate": "kvdb_temperature_unit_load_and_migrate_source_rodata",
    "open_cfw_kvdb_write_universal_setting": "kvdb_write_universal_setting_source_rodata",
    "open_cfw_kvdb_universal_setting_load_and_migrate": "kvdb_universal_setting_load_and_migrate_source_rodata",
    "open_cfw_kvdb_write_terminal_mode": "kvdb_write_terminal_mode_source_rodata",
    "open_cfw_kvdb_terminal_mode_load_and_migrate": "kvdb_terminal_mode_load_and_migrate_source_rodata",
    "open_cfw_kvdb_onboarding_config_persist": "kvdb_onboarding_config_persist_source_rodata",
    "open_cfw_kvdb_onboarding_config_update_and_persist": "kvdb_onboarding_config_update_and_persist_source_rodata",
    "open_cfw_kvdb_onboarding_config_read": "kvdb_onboarding_config_read_source_rodata",
    "open_cfw_kvdb_write_ring": "kvdb_write_ring_source_rodata",
    "open_cfw_kvdb_ring_load_and_migrate": "kvdb_ring_load_and_migrate_source_rodata",
    "open_cfw_kvdb_read_language": "kvdb_read_language_source_rodata",
    "open_cfw_kvdb_write_language": "kvdb_write_language_source_rodata",
    "open_cfw_kvdb_read_dashboard_auto_close": "kvdb_read_dashboard_auto_close_source_rodata",
    "open_cfw_kvdb_write_dashboard_auto_close": "kvdb_write_dashboard_auto_close_source_rodata",
    "open_cfw_kvdb_read_menu_configuration": "kvdb_read_menu_configuration_source_rodata",
    "open_cfw_kvdb_write_menu_configuration": "kvdb_write_menu_configuration_source_rodata",
    "open_cfw_nvdb_sys_dt_manufacturer_name": "nvdb_sys_dt_manufacturer_name_source_rodata",
    "open_cfw_nvdb_sys_dt_month": "nvdb_sys_dt_month_source_rodata",
    "open_cfw_uled_buffer_sync_to_fb": "uled_display_preprocess_source_rodata",
    "open_cfw_bq27427_update_dm_block": "chg_bq27427_update_dm_block_source_rodata",
    "open_cfw_bq27427_settings_apply_defaults": "chg_bq27427_settings_apply_defaults_source_rodata",
    "open_cfw_bq27427_hardware_init": "chg_bq27427_hardware_init_source_rodata",
    "open_cfw_cordio_smp_sc_event_string": "cordio_smp_sc_event_string_source_rodata",
    "open_cfw_cordio_smpi_sc_state_string": "smpi_sc_sm_state_names_source_rodata",
    "open_cfw_cordio_smpr_sc_state_string": "smpr_sc_sm_state_names_source_rodata",
    "open_cfw_system_alert_reflash_event_handler": "system_alert_overlay_reflash_event_source_rodata",
    "open_cfw_cli_fs_ls": "freertos_cli_filesystem_overlay_02_source_rodata",
    "open_cfw_cli_fs_cat": "freertos_cli_filesystem_overlay_03_source_rodata",
    "open_cfw_cli_fs_rm": "freertos_cli_filesystem_overlay_04_source_rodata",
    "open_cfw_cli_fs_cd": "freertos_cli_filesystem_overlay_05_source_rodata",
    "open_cfw_cli_fs_mkdir": "freertos_cli_filesystem_overlay_06_source_rodata",
    "open_cfw_cli_fs_touch": "freertos_cli_filesystem_overlay_07_source_rodata",
    "open_cfw_cli_fs_pwd": "freertos_cli_filesystem_overlay_08_source_rodata",
    "open_cfw_cli_fs_mv": "freertos_cli_filesystem_overlay_09_source_rodata",
    "open_cfw_cli_fs_md5": "freertos_cli_filesystem_overlay_10_source_rodata",
    "open_cfw_cli_fs_df": "freertos_cli_filesystem_overlay_11_source_rodata",
    "open_cfw_health_page_build_summary": "ui_health_page_build-summary_source_rodata",
    "open_cfw_health_page_build_detail": "ui_health_page_build-detail_source_rodata",
}
LEGACY_SPECIAL_RODATA_ALIASES = {
    "LZ4_decompress_safe": "apollo_lz4_upstream_decompress_tables_source_data",
    "TF_AcceptChar": "apollo_tinyframe_tf_acceptchar_crc16_table",
    "TF_SendFrame": "apollo_tinyframe_tf_sendframe_crc16_table",
    "TF_Multipart_Payload": "apollo_tinyframe_tf_multipart_payload_crc16_table",
    "open_cfw_als_bucket_brightness": "als_curve_source_data",
}
LEGACY_COALESCED_CLOSURE_ALIASES = {
    "open_cfw_nanopb_decode_field": "apollo_nanopb_decode_field_source_closure",
    "open_cfw_nanopb_default_extension_decoder": "apollo_nanopb_default_extension_decoder_source_closure",
    "open_cfw_nanopb_dec_fixed_length_bytes": "apollo_nanopb_dec_fixed_length_bytes_source_closure",
    "open_cfw_nanopb_decode_basic_field": "apollo_nanopb_decode_basic_field_source_closure",
    "open_cfw_nanopb_decode_static_field": "apollo_nanopb_decode_static_field_source_closure",
    "open_cfw_nanopb_decode_pointer_field": "apollo_nanopb_decode_pointer_field_source_closure",
    "open_cfw_nanopb_decode_callback_field": "apollo_nanopb_decode_callback_field_source_closure",
}
LEGACY_MULTI_OWNER_ALIASES = {
    "iar_format_input_source_closure": (
        "__aeabi_dadd", "__aeabi_dmul", "__aeabi_ddiv", "__aeabi_ui2d",
        "__aeabi_d2f", "open_cfw_runtime_strtod_bounded",
        "open_cfw_runtime_strtod", "open_cfw_runtime_scanset_match",
        "open_cfw_runtime_vsscanf", "open_cfw_runtime_sscanf",
        "open_cfw_runtime_iar_scanf_core",
    ),
    "iar_format_output_source_closure": (
        "open_cfw_runtime_iar_vsnprintf_engine",
        "open_cfw_runtime_iar_format_bridge",
        "open_cfw_runtime_iar_vformat",
        "open_cfw_runtime_iar_printf_core",
    ),
}
LEGACY_RETIRED_ALIGNMENT_ALIASES = {
    "apollo_ambiq_mspi_interrupt_clear_overlay_alignment",
}

sys.path.insert(0, str(G2_ROOT / "tools"))
from apollo_overlay import (  # noqa: E402
    BuildError,
    atomic_write,
    decode_thumb_branch,
    encode_thumb_branch,
    filter_config_for_profile,
    hermetic_compiler_environment,
    resolve_leaf_profile,
)
import open_cfw  # noqa: E402


class AdmissionError(RuntimeError):
    """A canonical observation or synchronization proof failed."""


def _digest(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def _is_normalized_absolute_path(value: str) -> bool:
    """Accept one exact POSIX absolute spelling without resolving symlinks."""
    return (
        os.path.isabs(value)
        and os.path.abspath(value) == value
        and not value.startswith(os.sep * 2)
    )


def _read_stable_regular_with_identity(
    path: Path, role: str, *, require_single_link: bool
) -> tuple[bytes, tuple[int, int, int, int, int]]:
    """Read once through O_NOFOLLOW and return its stable fstat identity."""
    descriptor: int | None = None
    try:
        if not stat.S_ISREG(path.lstat().st_mode) or path.is_symlink():
            raise AdmissionError(f"{role} is not a regular non-symlink file")
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise AdmissionError(f"{role} changed file type while reading")
        if require_single_link and before.st_nlink != 1:
            raise AdmissionError(f"{role} must have exactly one hard link")
        with os.fdopen(descriptor, "rb") as handle:
            descriptor = None
            payload = handle.read()
            after = os.fstat(handle.fileno())
        before_identity = (
            before.st_dev, before.st_ino, before.st_size,
            before.st_mtime_ns, before.st_ctime_ns,
        )
        after_identity = (
            after.st_dev, after.st_ino, after.st_size,
            after.st_mtime_ns, after.st_ctime_ns,
        )
        if (
            before_identity != after_identity
            or before.st_nlink != after.st_nlink
            or (require_single_link and after.st_nlink != 1)
            or len(payload) != after.st_size
        ):
            raise AdmissionError(f"{role} changed while reading")
        return payload, after_identity
    except OSError as error:
        raise AdmissionError(f"cannot read {role}: {error}") from error
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _read_regular_with_identity(
    path: Path, role: str
) -> tuple[bytes, tuple[int, int, int, int, int]]:
    """Read one unique-link report, artifact, provider, or publication input."""
    return _read_stable_regular_with_identity(
        path, role, require_single_link=True
    )


def _read_authenticated_executable_with_identity(
    path: Path, role: str
) -> tuple[bytes, tuple[int, int, int, int, int]]:
    """Read a stable executable, allowing legitimate platform hard links."""
    return _read_stable_regular_with_identity(
        path, role, require_single_link=False
    )


def _read_authenticated_resource_header_with_identity(
    path: Path, role: str
) -> tuple[bytes, tuple[int, int, int, int, int]]:
    """Read a stable compiler header, allowing platform-owned hard links."""
    return _read_stable_regular_with_identity(
        path, role, require_single_link=False
    )


def _read_regular(path: Path, role: str) -> bytes:
    return _read_regular_with_identity(path, role)[0]


def _read_json(path: Path, role: str) -> tuple[bytes, dict[str, Any]]:
    payload, _identity = _read_regular_with_identity(path, role)
    return payload, _decode_json_object(payload, role)


def _decode_json_object(payload: bytes, role: str) -> dict[str, Any]:
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise AdmissionError(f"{role} is not valid UTF-8 JSON: {error}") from error
    if not isinstance(value, dict):
        raise AdmissionError(f"{role} must contain a JSON object")
    return value


def _observation_path(path: Path) -> Path:
    """Require recorder-compatible, G2-local, symlink-free observation paths."""
    root = PROJECT_ROOT.resolve()
    lexical = Path(os.path.abspath(path))
    try:
        lexical.relative_to(root)
        resolved = lexical.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, ValueError, RuntimeError) as error:
        raise AdmissionError("canonical observation must be inside the G2 tree") \
            from error
    if lexical != resolved:
        raise AdmissionError("canonical observation path contains a symlink")
    return resolved


def _read_json_with_identity(
    path: Path, role: str
) -> tuple[bytes, dict[str, Any], tuple[int, int, int, int, int]]:
    payload, identity = _read_regular_with_identity(path, role)
    return payload, _decode_json_object(payload, role), identity


@contextmanager
def _admission_lock():
    """Serialize admission through one descriptor-relative repository lock."""
    root = PROJECT_ROOT.resolve()
    lock_dir = root / "components/apollo_main/core_overlay/build"
    lock_name = ".open-cfw-canonical-admission.lock"
    directory_descriptors: list[int] = []
    directory_descriptor: int | None = None
    directory_identity: tuple[int, int] | None = None
    descriptor: int | None = None

    def require_named_lock_parent() -> None:
        if directory_descriptor is None or directory_identity is None:
            raise AdmissionError("canonical admission lock directory is missing")
        opened = os.fstat(directory_descriptor)
        try:
            named = os.stat(lock_dir, follow_symlinks=False)
        except OSError as error:
            raise AdmissionError("canonical admission lock directory changed") \
                from error
        if (
            not stat.S_ISDIR(opened.st_mode)
            or not stat.S_ISDIR(named.st_mode)
            or (opened.st_dev, opened.st_ino) != directory_identity
            or (named.st_dev, named.st_ino) != directory_identity
        ):
            raise AdmissionError("canonical admission lock directory changed")

    def require_single_lock_domain() -> None:
        if descriptor is None or directory_descriptor is None:
            raise AdmissionError("canonical admission lock descriptor is missing")
        require_named_lock_parent()
        opened = os.fstat(descriptor)
        try:
            named = os.stat(
                lock_name, dir_fd=directory_descriptor, follow_symlinks=False
            )
        except OSError as error:
            raise AdmissionError("canonical admission lock path changed") from error
        if (
            not stat.S_ISREG(opened.st_mode)
            or not stat.S_ISREG(named.st_mode)
            or opened.st_nlink != 1
            or named.st_nlink != 1
            or (opened.st_dev, opened.st_ino) != (named.st_dev, named.st_ino)
        ):
            raise AdmissionError("canonical admission lock has multiple lock domains")

    try:
        directory_flags = (
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        )
        directory_descriptors.append(os.open(root, directory_flags))
        cursor_descriptor = directory_descriptors[0]
        for part in lock_dir.relative_to(root).parts:
            cursor_descriptor = os.open(
                part, directory_flags, dir_fd=cursor_descriptor
            )
            directory_descriptors.append(cursor_descriptor)
        directory_descriptor = directory_descriptors[-1]
        opened_directory = os.fstat(directory_descriptor)
        directory_identity = (opened_directory.st_dev, opened_directory.st_ino)
        require_named_lock_parent()
        descriptor = os.open(
            lock_name,
            os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0),
            0o600,
            dir_fd=directory_descriptor,
        )
        require_single_lock_domain()
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        require_single_lock_domain()
        yield require_single_lock_domain
        require_single_lock_domain()
    except OSError as error:
        if isinstance(error, NotADirectoryError) or error.errno in (
            errno.ELOOP,
        ):
            raise AdmissionError(
                "canonical admission lock directory contains a symlink or non-directory"
            ) from error
        raise AdmissionError(f"cannot acquire canonical admission lock: {error}") \
            from error
    finally:
        if descriptor is not None:
            try:
                fcntl.flock(descriptor, fcntl.LOCK_UN)
            finally:
                os.close(descriptor)
        for directory_descriptor in reversed(directory_descriptors):
            os.close(directory_descriptor)


def _artifact_path(report_path: Path, value: Any, role: str) -> Path:
    if (
        not isinstance(value, str)
        or not value
        or Path(value).name != value
        or value in (".", "..")
    ):
        raise AdmissionError(f"{role} artifact path is missing")
    candidate = report_path.resolve().parent / value
    lexical = Path(os.path.abspath(candidate))
    try:
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise AdmissionError(f"cannot resolve {role} artifact") from error
    if lexical != resolved:
        raise AdmissionError(f"{role} artifact path contains a symlink")
    if resolved.parent != report_path.resolve().parent:
        raise AdmissionError(f"{role} artifact is not beside its observation")
    return resolved


def _pin(record: Any, size_key: str, hash_key: str, role: str) -> tuple[int, str]:
    if not isinstance(record, dict):
        raise AdmissionError(f"{role} pin record is missing")
    size = record.get(size_key)
    digest = record.get(hash_key)
    if (
        type(size) is not int
        or size <= 0
        or not isinstance(digest, str)
        or re.fullmatch(r"[0-9a-f]{64}", digest) is None
    ):
        raise AdmissionError(f"{role} pin is incomplete")
    return size, digest


def _tool_query(
    invocation: Path, arguments: list[str], role: str
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            [str(invocation), *arguments],
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
            env=hermetic_compiler_environment(),
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        raise AdmissionError(f"{role} cannot be independently re-derived") from error


def _validate_toolchain_identity(value: Any, toolchain: Any) -> None:
    identity = _require_exact_keys(
        value,
        {"schema_version", "executables", "compiler_resource_headers"},
        "toolchain identity",
    )
    if identity["schema_version"] != 2:
        raise AdmissionError("toolchain identity schema changed")
    executables = _require_exact_keys(
        identity["executables"], {"compiler", "pt_linker", "pt_nm"},
        "toolchain executables",
    )
    resolved_executables: dict[
        str, tuple[Path, Path, bytes, tuple[int, int, int, int, int]]
    ] = {}
    for role, record in executables.items():
        record = _require_exact_keys(
            record,
            {"invocation_path", "resolved_path", "size", "sha256", "version"},
            f"{role} executable identity",
        )
        invocation = record["invocation_path"]
        resolved_value = record["resolved_path"]
        if (
            not isinstance(invocation, str)
            or not isinstance(resolved_value, str)
            or not isinstance(record["version"], str)
            or not record["version"]
        ):
            raise AdmissionError(f"{role} executable identity is incomplete")
        if (
            not _is_normalized_absolute_path(invocation)
            or not _is_normalized_absolute_path(resolved_value)
        ):
            raise AdmissionError(
                f"{role} executable paths must be absolute and normalized"
            )
        try:
            invocation_path = Path(invocation)
            recorded_resolved = Path(resolved_value)
            resolved = recorded_resolved.resolve(strict=True)
            if recorded_resolved != resolved:
                raise AdmissionError(
                    f"{role} resolved executable path is not canonical"
                )
            if invocation_path.resolve(strict=True) != resolved:
                raise AdmissionError(f"{role} invocation path changed target")
        except AdmissionError:
            raise
        except (OSError, RuntimeError) as error:
            raise AdmissionError(f"{role} executable path cannot be resolved") from error
        payload, executable_identity = _read_authenticated_executable_with_identity(
            resolved, f"{role} executable"
        )
        size, digest = _pin(record, "size", "sha256", f"{role} executable")
        if len(payload) != size or _digest(payload) != digest:
            raise AdmissionError(f"{role} executable differs from its receipt")
        version_arguments = (
            ["--no-default-config", "--version"]
            if role == "compiler" else ["--version"]
        )
        completed = _tool_query(
            invocation_path, version_arguments, f"{role} version"
        )
        version = (completed.stdout or completed.stderr).strip()
        if role == "compiler" and version:
            version = version.splitlines()[0].strip()
        if not version or version != record["version"]:
            raise AdmissionError(f"{role} version differs from its receipt")
        try:
            if invocation_path.resolve(strict=True) != resolved:
                raise AdmissionError(f"{role} invocation path changed target")
        except AdmissionError:
            raise
        except (OSError, RuntimeError) as error:
            raise AdmissionError(f"{role} executable path cannot be resolved") from error
        after_payload, after_identity = _read_authenticated_executable_with_identity(
            resolved, f"{role} executable"
        )
        if after_payload != payload or after_identity != executable_identity:
            raise AdmissionError(f"{role} executable changed during identity query")
        resolved_executables[role] = (
            invocation_path, resolved, payload, executable_identity
        )
    if (
        not isinstance(toolchain, dict)
        or toolchain.get("version") != executables["compiler"]["version"]
        or toolchain.get("executable")
        != executables["compiler"]["invocation_path"]
    ):
        raise AdmissionError("compiler toolchain receipts disagree")

    headers = _require_exact_keys(
        identity["compiler_resource_headers"],
        {"resource_dir", "entry_count", "total_size", "sha256", "entries"},
        "compiler resource-header closure",
    )
    resource_dir_value = headers["resource_dir"]
    entries = headers["entries"]
    if not isinstance(resource_dir_value, str) or not isinstance(entries, list):
        raise AdmissionError("compiler resource-header closure is incomplete")
    try:
        recorded_resource = Path(resource_dir_value)
        if not _is_normalized_absolute_path(resource_dir_value):
            raise AdmissionError("compiler resource-header directory is unsafe")
        resource_lexical = Path(os.path.abspath(recorded_resource))
        resource_dir = recorded_resource.resolve(strict=True)
        include_lexical = resource_dir / "include"
        include_dir = include_lexical.resolve(strict=True)
        include_dir.relative_to(resource_dir)
    except (OSError, ValueError, RuntimeError) as error:
        raise AdmissionError("compiler resource-header directory is unsafe") from error
    if (
        recorded_resource != resource_lexical
        or resource_lexical != resource_dir
        or include_lexical != include_dir
    ):
        raise AdmissionError("compiler resource-header directory contains a symlink")
    if (
        not stat.S_ISDIR(resource_dir.lstat().st_mode)
        or not stat.S_ISDIR(include_dir.lstat().st_mode)
    ):
        raise AdmissionError("compiler resource-header directory is unsafe")
    try:
        resource_initial = os.stat(resource_dir, follow_symlinks=False)
        include_initial = os.stat(include_dir, follow_symlinks=False)
    except OSError as error:
        raise AdmissionError(
            "compiler resource-header directory changed"
        ) from error
    resource_identity = (resource_initial.st_dev, resource_initial.st_ino)
    include_identity = (include_initial.st_dev, include_initial.st_ino)

    def require_resource_identities() -> None:
        try:
            resource_current = os.stat(resource_dir, follow_symlinks=False)
            include_current = os.stat(include_dir, follow_symlinks=False)
        except OSError as error:
            raise AdmissionError(
                "compiler resource-header directory changed"
            ) from error
        if (
            not stat.S_ISDIR(resource_current.st_mode)
            or not stat.S_ISDIR(include_current.st_mode)
            or (resource_current.st_dev, resource_current.st_ino) != resource_identity
            or (include_current.st_dev, include_current.st_ino) != include_identity
        ):
            raise AdmissionError("compiler resource-header directory changed")

    compiler_invocation, compiler_resolved, compiler_payload, compiler_identity = (
        resolved_executables["compiler"]
    )
    require_resource_identities()
    completed = _tool_query(
        compiler_invocation,
        ["--no-default-config", "-print-resource-dir"],
        "compiler resource directory",
    )
    reported_resource = completed.stdout.strip()
    if not reported_resource or "\n" in reported_resource:
        raise AdmissionError("compiler resource directory response is malformed")
    try:
        derived_resource = Path(reported_resource).resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise AdmissionError("compiler resource directory cannot be resolved") from error
    if derived_resource != resource_dir:
        raise AdmissionError("compiler resource directory differs from its receipt")
    compiler_after, compiler_after_identity = _read_authenticated_executable_with_identity(
        compiler_resolved, "compiler executable"
    )
    if (
        compiler_invocation.resolve(strict=True) != compiler_resolved
        or compiler_after != compiler_payload
        or compiler_after_identity != compiler_identity
    ):
        raise AdmissionError("compiler changed during resource discovery")
    require_resource_identities()
    paths: set[str] = set()
    for entry in entries:
        entry = _require_exact_keys(
            entry, {"path", "size", "sha256"}, "compiler resource header"
        )
        relative = entry["path"]
        if (
            not isinstance(relative, str)
            or not relative
            or relative in paths
            or Path(relative).is_absolute()
            or ".." in Path(relative).parts
        ):
            raise AdmissionError("compiler resource-header path is unsafe")
        paths.add(relative)
    if entries != sorted(entries, key=lambda item: item["path"]):
        raise AdmissionError("compiler resource-header entries are not ordered")
    def scan_resource_headers() -> tuple[
        list[dict[str, Any]],
        dict[str, tuple[int, int, int, int, int]],
    ]:
        require_resource_identities()
        try:
            candidates = sorted(
                include_dir.rglob("*"), key=lambda item: item.as_posix()
            )
        except OSError as error:
            raise AdmissionError(
                "compiler resource-header closure cannot be enumerated"
            ) from error
        observed: list[dict[str, Any]] = []
        identities: dict[str, tuple[int, int, int, int, int]] = {}
        for candidate in candidates:
            if candidate.is_symlink():
                raise AdmissionError(
                    "compiler resource-header closure contains a symlink"
                )
            try:
                mode = candidate.lstat().st_mode
            except OSError as error:
                raise AdmissionError(
                    "compiler resource-header closure changed"
                ) from error
            if stat.S_ISDIR(mode):
                continue
            if not stat.S_ISREG(mode):
                raise AdmissionError(
                    "compiler resource-header closure contains a special file"
                )
            relative = candidate.relative_to(include_dir).as_posix()
            payload, identity = (
                _read_authenticated_resource_header_with_identity(
                    candidate, "compiler resource header"
                )
            )
            observed.append({
                "path": relative,
                "size": len(payload),
                "sha256": _digest(payload),
            })
            identities[relative] = identity
        require_resource_identities()
        return observed, identities

    observed_entries, observed_identities = scan_resource_headers()
    if observed_entries != entries:
        raise AdmissionError("compiler resource-header closure entries changed")
    if (
        headers["entry_count"] != len(observed_entries)
        or headers["total_size"] != sum(item["size"] for item in observed_entries)
        or headers["sha256"] != _digest(_canonical(observed_entries))
    ):
        raise AdmissionError("compiler resource-header closure digest changed")
    verified_entries, verified_identities = scan_resource_headers()
    if (
        verified_entries != observed_entries
        or verified_identities != observed_identities
    ):
        raise AdmissionError(
            "compiler resource-header closure changed during authentication"
        )


def _validate_core_stage_schema(stage: Any) -> None:
    stage = _require_exact_keys(
        stage,
        {
            "expected", "functions", "isolated_leaves", "relocated_leaves",
            "in_place_leaves", "in_place_data",
        },
        "core-stage receipt",
    )
    if not isinstance(stage["functions"], dict):
        raise AdmissionError("core-stage function receipt is malformed")
    _require_exact_keys(
        stage["expected"],
        {"overlay_size", "overlay_sha256", "component_size", "component_sha256"},
        "core-stage expected",
    )
    category_contracts = {
        "isolated_leaves": {
            "item": {"extraction", "pins", "placement", "toolchain"},
            "extraction": {
                "alignment", "discarded_alloc_section_bytes",
                "discarded_alloc_section_count", "discarded_alloc_sections",
                "function", "relocation_count", "section", "sha256", "size",
            },
            "placement": {"alignment", "offset", "padding_before", "size"},
        },
        "relocated_leaves": {
            "item": {"extraction", "pins", "placement", "toolchain"},
            "extraction_base": {
                "alignment", "authenticated_cantunwind_discard_count",
                "authenticated_cantunwind_discards", "discarded_alloc_section_bytes",
                "discarded_alloc_section_count", "discarded_alloc_sections",
                "function", "relocation_count", "relocations", "runtime_address",
                "runtime_address_hex", "section", "sha256", "size",
                "unrelocated_sha256",
            },
            "extraction_closure": {
                "closure_sha256", "closure_size", "internal_padding_size", "rodata"
            },
            "placement_base": {
                "alignment", "offset", "padding_before", "runtime_address",
                "runtime_address_hex", "size",
            },
        },
        "in_place_leaves": {
            "item": {"extraction", "pins", "placement", "toolchain"},
            "extraction": {
                "alignment", "authenticated_cantunwind_discard_count",
                "authenticated_cantunwind_discards", "discarded_alloc_section_bytes",
                "discarded_alloc_section_count", "discarded_alloc_sections",
                "function", "relocation_count", "relocations", "runtime_address",
                "runtime_address_hex", "section", "sha256", "size",
                "unrelocated_sha256",
            },
            "placement": {
                "end_exclusive", "end_exclusive_hex", "function",
                "literal_dependencies", "payload_offset", "replacement_hex",
                "replacement_sha256", "runtime_address", "runtime_address_hex",
                "size", "stock_sha256",
            },
        },
        "in_place_data": {
            "item": {"extraction", "pins", "toolchain"},
            "extraction": {
                "alignment", "placements", "relocation_count", "section",
                "sha256", "size", "symbol",
            },
        },
    }
    for category, contract in category_contracts.items():
        items = stage[category]
        if not isinstance(items, list):
            raise AdmissionError(f"core-stage {category} receipt is missing")
        for item in items:
            _require_exact_keys(item, contract["item"], f"{category} item")
            extraction_keys = set(item.get("extraction", {}))
            if category == "relocated_leaves":
                allowed = set(contract["extraction_base"])
                if "closure_size" in extraction_keys:
                    allowed.update(contract["extraction_closure"])
                if extraction_keys != allowed:
                    raise AdmissionError("relocated leaf extraction fields changed")
                placement_keys = set(item.get("placement", {}))
                allowed_placement = set(contract["placement_base"])
                if "closure_size" in extraction_keys:
                    allowed_placement.add("text_size")
                if placement_keys != allowed_placement:
                    raise AdmissionError("relocated leaf placement fields changed")
                pin_keys = {
                    "size", "sha256", "alignment", "offset",
                    "unrelocated_sha256", "relocations",
                }
                if "closure_size" in extraction_keys:
                    pin_keys.update({
                        "closure_size", "closure_sha256", "rodata_offset", "rodata"
                    })
                _require_exact_keys(item.get("pins"), pin_keys, "relocated leaf pins")
            else:
                _require_exact_keys(
                    item.get("extraction"), contract["extraction"],
                    f"{category} extraction",
                )
                if "placement" in contract:
                    _require_exact_keys(
                        item.get("placement"), contract["placement"],
                        f"{category} placement",
                    )
                pin_keys = (
                    {"size", "sha256", "alignment"}
                    if category == "in_place_data"
                    else {"size", "sha256"}
                )
                _require_exact_keys(
                    item.get("pins"), pin_keys, f"{category} pins"
                )
            toolchain = item.get("toolchain")
            allowed_toolchain = {"executable", "flags", "target", "version"}
            if isinstance(toolchain, dict) and "include_dirs" in toolchain:
                allowed_toolchain.add("include_dirs")
            _require_exact_keys(toolchain, allowed_toolchain, f"{category} toolchain")


def _validate_liblc3_schema(value: Any) -> None:
    lib = _require_exact_keys(
        value,
        {
            "license", "payload_size", "payload_sha256", "component_size",
            "component_sha256", "placement", "historical_non_corpus_routing",
        },
        "liblc3 receipt",
    )
    placement = lib["placement"]
    if lib["license"] != "Apache-2.0":
        raise AdmissionError("liblc3 license receipt changed")
    if lib["historical_non_corpus_routing"] != LIBLC3_HISTORICAL_NON_CORPUS_ROUTING:
        raise AdmissionError("liblc3 historical routing receipt changed")
    base_keys = {
        "entry", "entry_hex", "file_offset", "runtime_address",
        "runtime_address_hex",
    }
    if not isinstance(placement, dict):
        raise AdmissionError("liblc3 placement is malformed")
    allowed = set(base_keys)
    if "sections" in placement:
        allowed.add("sections")
    _require_exact_keys(placement, allowed, "liblc3 placement")
    if "sections" in placement:
        sections = _require_exact_keys(
            placement["sections"], {"text", "rodata"}, "liblc3 cave sections"
        )
        for name, section in sections.items():
            _require_exact_keys(
                section,
                {"capacity", "file_offset", "runtime_address", "size", "sha256"},
                f"liblc3 {name} section",
            )


def _validate_liblc3_service_schema(value: Any) -> dict[str, Any]:
    service = _require_exact_keys(
        value,
        {"license", "component", "suffix", "target_runtime",
         "lc3_finalization", "service_audio_entry_guards", "routing",
         "hardware"},
        "liblc3 service-audio receipt",
    )
    if (
        service["license"] != "Apache-2.0 AND MIT"
        or service["hardware"] != DEFERRED_HARDWARE_POLICY
        or service["routing"] != {
            "production_placement": True,
            "service_audio_routed": True,
            "firmware_image_emitted": True,
            "hardware_operations": False,
        }
    ):
        raise AdmissionError("liblc3 service-audio routing boundary changed")
    component = _require_exact_keys(
        service["component"],
        {"size", "sha256", "runtime_end_exclusive", "nested_crc32"},
        "liblc3 service-audio component",
    )
    _pin(component, "size", "sha256", "liblc3 service-audio component")
    if (
        component["runtime_end_exclusive"] != 0x007FDFA0
        or re.fullmatch(r"0x[0-9A-F]{8}", str(component["nested_crc32"])) is None
        or service["target_runtime"].get("undefined_symbols") != []
        or service["target_runtime"].get("output_relocations") != 0
        or service["lc3_finalization"].get("output_relocations") != 0
        or service["lc3_finalization"].get("all_input_relocations_applied")
           is not True
        or len(service["service_audio_entry_guards"]) != 2
    ):
        raise AdmissionError("liblc3 service-audio closure receipt changed")
    return service


def _validate_freetype_cff_schema(value: Any) -> dict[str, Any]:
    """Reject incomplete or extensible CFF stage receipts before reading bytes."""
    cff = _require_exact_keys(
        value,
        {
            "license", "component", "placement", "module_class_patch",
            "scatter_manifest", "receipt_sha256", "hardware",
            "section_artifacts",
        },
        "FreeType CFF receipt",
    )
    if cff["license"] != CFF_LICENSE or cff["hardware"] != DEFERRED_HARDWARE_POLICY:
        raise AdmissionError("FreeType CFF license or hardware boundary changed")
    component = _require_exact_keys(
        cff["component"],
        {
            "size", "sha256", "runtime_start", "runtime_end_exclusive",
            "growth_bytes", "nested_crc32",
        },
        "FreeType CFF component receipt",
    )
    _pin(component, "size", "sha256", "FreeType CFF component")
    if (
        type(component["runtime_start"]) is not int
        or type(component["runtime_end_exclusive"]) is not int
        or type(component["growth_bytes"]) is not int
        or component["growth_bytes"] < 0
        or re.fullmatch(r"0x[0-9A-F]{8}", str(component["nested_crc32"])) is None
    ):
        raise AdmissionError("FreeType CFF component extent is malformed")

    placement = cff["placement"]
    host_scatter = isinstance(placement, dict) and \
        placement.get("host_scatter") is True
    placement_keys = {
        "base_runtime_end_exclusive", "runtime_end_exclusive",
        "nested_crc32", "sections", "unused_scattered_table_pool_bytes",
        "unused_scattered_table_pool_consumed",
    }
    placement_keys.update(
        {"host_slot_count", "host_scatter", "host_slots_available",
         "host_slot_capacity_bytes", "host_slot_receipt_sha256",
         "host_packing"}
        if host_scatter else
        {"erased_gap_start", "erased_gap_end_exclusive",
         "erased_gap_size", "erased_gap_byte"}
    )
    placement = _require_exact_keys(
        placement, placement_keys, "FreeType CFF placement receipt")
    address_keys = ["base_runtime_end_exclusive", "runtime_end_exclusive"]
    if not host_scatter:
        address_keys.extend(("erased_gap_start", "erased_gap_end_exclusive"))
    for key in address_keys:
        if re.fullmatch(r"0x[0-9A-F]{8}", str(placement[key])) is None:
            raise AdmissionError("FreeType CFF placement address is malformed")
    if (
        type(placement["nested_crc32"]) is not int
        or not 0 <= placement["nested_crc32"] <= 0xFFFFFFFF
        or placement["unused_scattered_table_pool_bytes"] != 360
        or placement["unused_scattered_table_pool_consumed"] != 0
    ):
        raise AdmissionError("FreeType CFF padding or table-pool receipt changed")
    if host_scatter:
        if (
            component["growth_bytes"] != 0
            or placement["host_slot_count"] !=
               placement["host_slots_available"]
            or type(placement["host_slot_capacity_bytes"]) is not int
            or placement["host_slot_capacity_bytes"] <= 0
            or re.fullmatch(r"[0-9a-f]{64}", str(
                placement["host_slot_receipt_sha256"])) is None
            or not isinstance(placement["host_packing"], list)
        ):
            raise AdmissionError("FreeType CFF host-scatter receipt changed")
    elif (
        type(placement["erased_gap_size"]) is not int
        or placement["erased_gap_size"] < 0
        or placement["erased_gap_byte"] != 0xFF
    ):
        raise AdmissionError("FreeType CFF erased-gap receipt changed")
    sections = placement["sections"]
    if not isinstance(sections, list) or len(sections) < 4:
        raise AdmissionError("FreeType CFF section receipt count changed")
    previous_end = -1
    section_names: list[str] = []
    for section in sections:
        expected_name = section.get("name") if isinstance(section, dict) else "?"
        keys = {"name", "start", "end_exclusive", "size", "alignment", "sha256"}
        if host_scatter and str(expected_name).startswith(".cff_host_"):
            keys.add("input_section")
        section = _require_exact_keys(
            section, keys,
            f"FreeType CFF section {expected_name}",
        )
        _pin(section, "size", "sha256", f"FreeType CFF section {expected_name}")
        start = section["start"]
        end = section["end_exclusive"]
        alignment = section["alignment"]
        if (
            type(start) is not int
            or type(end) is not int
            or end - start != section["size"]
            or start < previous_end
            or type(alignment) is not int
            or alignment <= 0
            or alignment & (alignment - 1)
            or start % alignment
        ):
            raise AdmissionError(f"FreeType CFF section {expected_name} changed")
        section_names.append(section["name"])
        previous_end = end
    if host_scatter:
        if (
            section_names[-3:] != [".cff_stock_rodata", ".cff_stock_text",
                                   ".cff_stock_exidx"]
            or not section_names[0].startswith(".cff_host_")
        ):
            raise AdmissionError("FreeType CFF host section ordering changed")
    elif tuple(section_names) != CFF_SECTION_NAMES:
        raise AdmissionError("FreeType CFF legacy section ordering changed")

    patch = _require_exact_keys(
        cff["module_class_patch"],
        {
            "runtime_address", "expected_hex", "replacement_hex",
            "compare_before_write", "applied_after_all_preflight_checks",
        },
        "FreeType CFF module-class patch",
    )
    if (
        re.fullmatch(r"0x[0-9A-F]{8}", str(patch["runtime_address"])) is None
        or patch["expected_hex"] != CFF_STOCK_CLASS_BYTES.hex()
        or patch["replacement_hex"] != CFF_REPLACEMENT_CLASS_BYTES.hex()
        or patch["compare_before_write"] is not True
        or patch["applied_after_all_preflight_checks"] is not True
    ):
        raise AdmissionError("FreeType CFF module-class patch contract changed")

    scatter = _require_exact_keys(
        cff["scatter_manifest"],
        {
            "size", "sha256", "profile_final_elf",
            "undefined_symbols", "relocations",
        },
        "FreeType CFF scatter receipt",
    )
    _pin(scatter, "size", "sha256", "FreeType CFF scatter manifest")
    elf = _require_exact_keys(
        scatter["profile_final_elf"], {"bytes", "sha256"},
        "FreeType CFF final ELF",
    )
    _pin(elf, "bytes", "sha256", "FreeType CFF final ELF")
    relocations = _require_exact_keys(
        scatter["relocations"],
        {
            "total", "internal", "external", "by_type",
            "external_by_symbol", "records_sha256",
        },
        "FreeType CFF final relocations",
    )
    if (
        scatter["undefined_symbols"] != []
        or relocations != {
            "total": 0,
            "internal": 0,
            "external": 0,
            "by_type": {},
            "external_by_symbol": {},
            "records_sha256": _digest(b"[]"),
        }
        or re.fullmatch(r"[0-9a-f]{64}", str(cff["receipt_sha256"])) is None
    ):
        raise AdmissionError("FreeType CFF final link is not closed")

    artifacts = _require_exact_keys(
        cff["section_artifacts"], set(section_names),
        "FreeType CFF section artifact mapping",
    )
    for name in section_names:
        _require_exact_keys(
            artifacts[name], {"artifact", "size", "sha256"},
            f"FreeType CFF section artifact {name}",
        )
    return cff


def _validate_freetype_cff_contract(
    observation: dict[str, Any],
    base_component: bytes,
    final_component: bytes,
    section_artifacts: dict[str, bytes],
) -> None:
    """Replay every admitted CFF mutation and require the exact final image."""
    cff = observation["freetype_cff"]
    mapping = observation["image_mapping"]
    run_base = mapping["run_base"]
    preamble = mapping["preamble_bytes"]

    def address(value: Any, role: str) -> int:
        if not isinstance(value, str) or re.fullmatch(r"0x[0-9A-F]{8}", value) is None:
            raise AdmissionError(f"{role} is not a canonical runtime address")
        return int(value, 16)

    final_pin = {
        "size": observation["final"]["component_size"],
        "sha256": observation["final"]["component_sha256"],
    }
    component = cff["component"]
    if component["size"] != final_pin["size"] or component["sha256"] != final_pin[
        "sha256"
    ]:
        raise AdmissionError("FreeType CFF and final component receipts disagree")
    if len(final_component) != component["size"] or _digest(final_component) != component[
        "sha256"
    ]:
        raise AdmissionError("FreeType CFF final component bytes changed")
    base_end = run_base + len(base_component) - preamble
    final_end = run_base + len(final_component) - preamble
    if (
        component["runtime_start"] != run_base
        or component["runtime_end_exclusive"] != final_end
        or component["growth_bytes"] != len(final_component) - len(base_component)
        or component["growth_bytes"] < 0
        or final_end >= CFF_UPDATE_FLAG
    ):
        raise AdmissionError("FreeType CFF component mapping changed")

    placement = cff["placement"]
    host_scatter = placement.get("host_scatter") is True
    if (
        address(
            placement["base_runtime_end_exclusive"], "CFF base runtime end"
        ) != base_end
        or address(placement["runtime_end_exclusive"], "CFF runtime end")
        != final_end
        or placement["nested_crc32"]
        != int(component["nested_crc32"], 16)
    ):
        raise AdmissionError("FreeType CFF stage-chain extent changed")

    section_names = [row["name"] for row in placement["sections"]]
    if set(section_artifacts) != set(section_names):
        raise AdmissionError("FreeType CFF section artifact set changed")
    output = bytearray(base_component)
    output.extend(b"\xff" * (len(final_component) - len(output)))
    ranges: list[tuple[int, int]] = []
    for section in placement["sections"]:
        name = section["name"]
        body = section_artifacts[name]
        record = cff["section_artifacts"][name]
        if (
            len(body) != section["size"]
            or _digest(body) != section["sha256"]
            or record["size"] != len(body)
            or record["sha256"] != _digest(body)
        ):
            raise AdmissionError(f"FreeType CFF section {name} artifact changed")
        start = preamble + section["start"] - run_base
        end = preamble + section["end_exclusive"] - run_base
        if start < preamble or end > len(output) or end - start != len(body):
            raise AdmissionError(f"FreeType CFF section {name} escaped Apollo image")
        ranges.append((start, end))
        output[start:end] = body
    if any(left[1] > right[0] for left, right in zip(ranges, ranges[1:])):
        raise AdmissionError("FreeType CFF section artifacts overlap")
    if not host_scatter:
        erased_start = address(
            placement["erased_gap_start"], "CFF erased-gap start")
        erased_end = address(
            placement["erased_gap_end_exclusive"], "CFF erased-gap end")
        tail_start = placement["sections"][2]["start"]
        if (
            erased_start != base_end
            or erased_end - erased_start != placement["erased_gap_size"]
            or erased_end != tail_start
            or any(byte != 0xFF for byte in final_component[
                preamble + erased_start - run_base:
                preamble + erased_end - run_base])
        ):
            raise AdmissionError("FreeType CFF erased-gap bytes changed")

    patch = cff["module_class_patch"]
    patch_runtime = address(patch["runtime_address"], "CFF module-class patch")
    patch_offset = preamble + patch_runtime - run_base
    if (
        base_component[patch_offset:patch_offset + 4] != CFF_STOCK_CLASS_BYTES
        or final_component[patch_offset:patch_offset + 4]
        != CFF_REPLACEMENT_CLASS_BYTES
    ):
        raise AdmissionError("FreeType CFF module-class compare-before-write guard changed")
    output[patch_offset:patch_offset + 4] = CFF_REPLACEMENT_CLASS_BYTES
    output[0:4] = (0x04000000 | len(output)).to_bytes(4, "little")
    output[4:8] = b"\x00\x00\x00\x00"
    nested_crc = zlib.crc32(output[8:]) & 0xFFFFFFFF
    output[4:8] = nested_crc.to_bytes(4, "little")
    if nested_crc != placement["nested_crc32"] or bytes(output) != final_component:
        raise AdmissionError("FreeType CFF mutation replay does not produce final component")


def load_observation(path: Path, expected_profile: str) -> dict[str, Any]:
    """Load one complete receipt and authenticate both generated artifacts."""
    path = _observation_path(path)
    _payload, report, report_identity = _read_json_with_identity(
        path, "canonical observation"
    )
    observation = report.get("canonical_observation")
    legacy_observation_keys = {
        "schema_version", "complete", "profile", "source_inputs",
        "image_mapping", "toolchain", "toolchain_identity", "core_stage",
        "liblc3_ltpf", "pt_protocol", "final", "final_artifacts",
        "intermediate_artifacts",
    }
    cff_observation_keys = legacy_observation_keys | {"freetype_cff"}
    routed_observation_keys = cff_observation_keys | {
        "liblc3_service_audio"
    }
    schema_version = (
        observation.get("schema_version") if isinstance(observation, dict) else None
    )
    expected_keys = (
        (legacy_observation_keys if schema_version == 2 else
         cff_observation_keys if schema_version == 3 else
         routed_observation_keys)
    )
    if (
        not isinstance(observation, dict)
        or schema_version not in (2, 3, 4)
        or set(observation) != expected_keys
        or observation.get("complete") is not True
        or observation.get("profile") != expected_profile
    ):
        raise AdmissionError(
            f"canonical observation is incomplete or not {expected_profile!r}"
        )
    toolchain = observation.get("toolchain")
    allowed_toolchain = {"executable", "version", "profile", "target", "flags"}
    if isinstance(toolchain, dict) and "include_dirs" in toolchain:
        allowed_toolchain.add("include_dirs")
    if (
        not isinstance(toolchain, dict)
        or set(toolchain) != allowed_toolchain
        or toolchain.get("profile") != expected_profile
        or not isinstance(toolchain.get("version"), str)
        or not toolchain["version"]
    ):
        raise AdmissionError("canonical observation toolchain identity is incomplete")
    _validate_toolchain_identity(observation["toolchain_identity"], toolchain)
    image_mapping = _require_exact_keys(
        observation["image_mapping"],
        {"base_size", "run_base", "preamble_bytes"},
        "canonical image mapping",
    )
    if any(not isinstance(value, int) or value < 0 for value in image_mapping.values()):
        raise AdmissionError("canonical image mapping is invalid")
    source_inputs = observation.get("source_inputs")
    _require_exact_keys(
        source_inputs, {"entries", "sha256"}, "canonical source closure"
    )
    entries = source_inputs.get("entries") if isinstance(source_inputs, dict) else None
    if not isinstance(entries, list) or not entries:
        raise AdmissionError("canonical observation source closure is incomplete")
    paths: set[str] = set()
    for entry in entries:
        if (
            not isinstance(entry, dict)
            or set(entry) != {"path", "size", "sha256"}
            or not isinstance(entry.get("path"), str)
            or entry["path"] in paths
        ):
            raise AdmissionError("canonical observation source closure is ambiguous")
        paths.add(entry["path"])
        _pin(entry, "size", "sha256", "canonical source input")
    if source_inputs.get("sha256") != _digest(_canonical(entries)):
        raise AdmissionError("canonical observation source closure digest changed")
    lowered_paths = "\n".join(paths).lower()
    if any(marker in lowered_paths for marker in FORBIDDEN_SOURCE_MARKERS):
        raise AdmissionError("restricted IMU source entered the canonical source closure")

    artifacts: dict[str, bytes] = {}
    intermediate_artifacts: dict[str, bytes] = {}
    cff_artifacts: dict[str, bytes] = {}
    artifact_paths: dict[str, Path] = {}
    artifact_identities: dict[str, tuple[int, int, int, int, int]] = {}
    final_records = _require_exact_keys(
        observation["final_artifacts"], {"overlay", "component"},
        "final artifact mapping",
    )
    intermediate_keys = {
        "core_stage_overlay", "core_stage_component",
        "liblc3_payload", "liblc3_component",
    }
    if schema_version >= 3:
        intermediate_keys.add("pt_component")
    if schema_version >= 4:
        intermediate_keys.add("liblc3_service_component")
    intermediate_records = _require_exact_keys(
        observation["intermediate_artifacts"],
        intermediate_keys,
        "intermediate artifact mapping",
    )
    cff = (
        _validate_freetype_cff_schema(observation["freetype_cff"])
        if schema_version >= 3 else None
    )
    lc3_service = (
        _validate_liblc3_service_schema(
            observation["liblc3_service_audio"])
        if schema_version >= 4 else None
    )
    if cff is not None:
        scatter_inputs = [
            entry for entry in entries
            if entry["path"]
            == "tools/manifests/g2-freetype-cff-scatter-link.json"
        ]
        if len(scatter_inputs) != 1 or any(
            scatter_inputs[0][key] != cff["scatter_manifest"][key]
            for key in ("size", "sha256")
        ):
            raise AdmissionError(
                "FreeType CFF scatter receipt is not bound to source closure"
            )
    all_records = [
        (key, final_records[key], artifacts)
        for key in ("overlay", "component")
    ] + [
        (key, intermediate_records[key], intermediate_artifacts)
        for key in sorted(intermediate_keys)
    ]
    if cff is not None:
        all_records.extend(
            (name, record, cff_artifacts)
            for name, record in cff["section_artifacts"].items()
        )
    for key, outer, destination in all_records:
        _require_exact_keys(
            outer, {"artifact", "size", "sha256"}, f"observed {key} artifact"
        )
        size, digest = _pin(outer, "size", "sha256", f"observed {key}")
        artifact = _artifact_path(path, outer.get("artifact"), key)
        payload, identity = _read_regular_with_identity(
            artifact, f"observed {key} artifact"
        )
        if len(payload) != size or _digest(payload) != digest:
            raise AdmissionError(f"observed {key} artifact differs from its receipt")
        destination[key] = payload
        artifact_paths[key] = artifact
        artifact_identities[key] = identity
    generation_inodes = [report_identity[:2], *(
        artifact_identities[key][:2] for key, _outer, _destination in all_records
    )]
    if len(set(generation_inodes)) != len(generation_inodes):
        raise AdmissionError(
            "canonical observation artifacts require distinct inodes"
        )
    final_size, final_digest = _pin(
        observation.get("final"), "component_size", "component_sha256", "final"
    )
    if len(artifacts["component"]) != final_size or _digest(
        artifacts["component"]
    ) != final_digest:
        raise AdmissionError("final aggregate differs from the component artifact")
    final_overlay_size, final_overlay_digest = _pin(
        observation.get("final"), "overlay_size", "overlay_sha256", "final overlay"
    )
    if len(artifacts["overlay"]) != final_overlay_size or _digest(
        artifacts["overlay"]
    ) != final_overlay_digest:
        raise AdmissionError("final aggregate differs from the overlay artifact")
    core_stage = observation.get("core_stage")
    _validate_core_stage_schema(core_stage)
    core_overlay_size, core_overlay_digest = _pin(
        core_stage.get("expected"), "overlay_size", "overlay_sha256", "core stage"
    )
    core_component_size, core_component_digest = _pin(
        core_stage.get("expected"), "component_size", "component_sha256", "core stage"
    )
    if (
        len(intermediate_artifacts["core_stage_overlay"]) != core_overlay_size
        or _digest(intermediate_artifacts["core_stage_overlay"]) != core_overlay_digest
        or len(intermediate_artifacts["core_stage_component"]) != core_component_size
        or _digest(intermediate_artifacts["core_stage_component"])
        != core_component_digest
    ):
        raise AdmissionError("core-stage artifacts differ from persisted pins")
    if core_component_size - core_overlay_size != image_mapping["base_size"]:
        raise AdmissionError("core-stage artifact extent differs from image mapping")
    liblc3 = observation.get("liblc3_ltpf")
    _validate_liblc3_schema(liblc3)
    lib_size, lib_digest = _pin(
        liblc3, "payload_size", "payload_sha256", "liblc3 payload"
    )
    lib_component_size, lib_component_digest = _pin(
        liblc3, "component_size", "component_sha256", "liblc3 component"
    )
    if (
        len(intermediate_artifacts["liblc3_payload"]) != lib_size
        or _digest(intermediate_artifacts["liblc3_payload"]) != lib_digest
        or len(intermediate_artifacts["liblc3_component"]) != lib_component_size
        or _digest(intermediate_artifacts["liblc3_component"])
        != lib_component_digest
    ):
        raise AdmissionError("liblc3 artifacts differ from persisted pins")
    pt = observation.get("pt_protocol")
    _pin(pt, "payload_size", "payload_sha256", "PT payload")
    if not isinstance(pt, dict) or re.fullmatch(
        r"[0-9a-f]{64}", str(pt.get("interval_sha256", ""))
    ) is None:
        raise AdmissionError("PT interval pin is incomplete")
    placement = pt.get("placement") if isinstance(pt, dict) else None
    if not isinstance(placement, dict) or not isinstance(
        placement.get("sections"), dict
    ):
        raise AdmissionError("PT placement/section receipt is incomplete")
    if cff is not None:
        cff_base = intermediate_artifacts[
            "liblc3_service_component"
        ] if lc3_service is not None else intermediate_artifacts["pt_component"]
        if lc3_service is not None:
            expected = lc3_service["component"]
            if (len(cff_base), _digest(cff_base)) != (
                expected["size"], expected["sha256"]
            ):
                raise AdmissionError(
                    "liblc3 service-audio intermediate artifact changed"
                )
        _validate_freetype_cff_contract(
            observation,
            cff_base,
            artifacts["component"],
            cff_artifacts,
        )
    return {
        "path": path.resolve(),
        "report_payload": _payload,
        "report_identity": report_identity,
        "report": report,
        "observation": observation,
        "artifacts": artifacts,
        "intermediate_artifacts": intermediate_artifacts,
        "cff_artifacts": cff_artifacts,
        "artifact_paths": artifact_paths,
        "artifact_identities": artifact_identities,
    }


def admit_reproducible_pair(
    paths: list[Path], expected_profile: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Authenticate and return both independent receipts for one profile."""
    if len(paths) != 2 or paths[0].resolve() == paths[1].resolve():
        raise AdmissionError(
            f"{expected_profile} requires two distinct observation reports"
        )
    first = load_observation(paths[0], expected_profile)
    second = load_observation(paths[1], expected_profile)
    validate_observation_independence((first, second))
    if first["observation"] != second["observation"]:
        raise AdmissionError(
            f"{expected_profile} observations are not byte-for-byte reproducible"
        )
    for domain in ("artifacts", "intermediate_artifacts", "cff_artifacts"):
        if set(first[domain]) != set(second[domain]):
            raise AdmissionError(
                f"{expected_profile} {domain} artifact set is not reproducible"
            )
        for key in first[domain]:
            if first[domain][key] != second[domain][key]:
                raise AdmissionError(
                    f"{expected_profile} {key} artifacts are not reproducible"
                )
    return first, second


def validate_observation_independence(
    observations: tuple[dict[str, Any], ...],
) -> None:
    """Require every report and persisted artifact to own a distinct inode."""
    legacy_artifact_keys = {
        "overlay", "component", "core_stage_overlay", "core_stage_component",
        "liblc3_payload", "liblc3_component",
    }
    identities: list[tuple[int, int]] = []
    for observation in observations:
        report_identity = observation.get("report_identity")
        artifact_identities = observation.get("artifact_identities")
        schema_version = observation.get("observation", {}).get("schema_version")
        artifact_keys = set(legacy_artifact_keys)
        if isinstance(schema_version, int) and schema_version >= 3:
            artifact_keys.add("pt_component")
            cff = observation.get("observation", {}).get("freetype_cff")
            section_artifacts = (
                cff.get("section_artifacts") if isinstance(cff, dict) else None
            )
            if not isinstance(section_artifacts, dict):
                raise AdmissionError(
                    "canonical observation inode evidence is incomplete"
                )
            artifact_keys.update(section_artifacts)
        if isinstance(schema_version, int) and schema_version >= 4:
            artifact_keys.add("liblc3_service_component")
        if (
            not isinstance(report_identity, tuple)
            or len(report_identity) < 2
            or not isinstance(artifact_identities, dict)
            or set(artifact_identities) != artifact_keys
        ):
            raise AdmissionError("canonical observation inode evidence is incomplete")
        identities.append(report_identity[:2])
        for key in sorted(artifact_keys):
            identity = artifact_identities[key]
            if not isinstance(identity, tuple) or len(identity) < 2:
                raise AdmissionError(
                    "canonical observation inode evidence is incomplete"
                )
            identities.append(identity[:2])
    if len(set(identities)) != len(identities):
        raise AdmissionError(
            "canonical observations and artifacts require globally distinct inodes"
        )


def admit_pair(
    paths: list[Path], expected_profile: str
) -> dict[str, Any]:
    """Authenticate a reproducible pair and return its canonical first receipt."""
    return admit_reproducible_pair(paths, expected_profile)[0]


def validate_generation(
    apple: dict[str, Any], linux: dict[str, Any]
) -> None:
    apple_inputs = apple["observation"]["source_inputs"]
    linux_inputs = linux["observation"]["source_inputs"]
    if apple_inputs != linux_inputs:
        raise AdmissionError("Apple/Linux observations use different source inputs")
    apple_compiler = apple["observation"]["toolchain_identity"]["executables"][
        "compiler"
    ]
    linux_compiler = linux["observation"]["toolchain_identity"]["executables"][
        "compiler"
    ]
    if (
        apple_compiler["sha256"] == linux_compiler["sha256"]
        or apple_compiler["version"] == linux_compiler["version"]
    ):
        raise AdmissionError(
            "Apple/Linux observations require distinct compiler payloads and versions"
        )


def validate_current_inputs(
    expected: dict[str, Any], observed: dict[str, tuple[int, str]]
) -> None:
    actual = {
        "entries": [
            {"path": path, "size": size, "sha256": digest}
            for path, (size, digest) in sorted(observed.items())
        ]
    }
    actual["sha256"] = _digest(_canonical(actual["entries"]))
    if actual != expected:
        raise AdmissionError("canonical observations are stale for current source inputs")


def current_source_input_report(
    config_path: Path = CORE_CONFIG,
) -> dict[str, Any]:
    """Return the exact current builder source closure without compiling or writing."""
    builder = _load_core_builder()
    _payload, _config, snapshot = _current_input_state(
        builder, config_path.resolve()
    )
    entries = [
        {"path": path, "size": size, "sha256": digest}
        for path, (size, digest) in sorted(snapshot.items())
    ]
    return {
        "entries": entries,
        "sha256": _digest(_canonical(entries)),
    }


def _identity(item: dict[str, Any], data: bool = False) -> str:
    extraction = item.get("extraction")
    if not isinstance(extraction, dict):
        raise AdmissionError("observed leaf extraction is missing")
    key = "symbol" if data else "function"
    value = extraction.get(key)
    if not isinstance(value, str) or not value:
        raise AdmissionError("observed leaf identity is missing")
    return value


def _observation_as_stage_report(observation: dict[str, Any]) -> dict[str, Any]:
    stage = observation["core_stage"]
    expected = stage["expected"]
    return {
        "toolchain": observation["toolchain"],
        "overlay": {
            "size": expected["overlay_size"],
            "sha256": expected["overlay_sha256"],
            "functions": stage["functions"],
        },
        "component": {
            "size": expected["component_size"],
            "sha256": expected["component_sha256"],
        },
        **{
            key: copy.deepcopy(stage[key])
            for key in ("isolated_leaves", "relocated_leaves", "in_place_leaves")
        },
    }


def _indexed_leaves(
    stage: dict[str, Any], key: str, *, data: bool = False
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for item in stage[key]:
        identity = _identity(item, data=data)
        if identity in result:
            raise AdmissionError(f"duplicate observed leaf identity: {identity}")
        if not isinstance(item.get("pins"), dict) or not isinstance(
            item.get("toolchain"), dict
        ):
            raise AdmissionError(f"observed leaf {identity!r} lacks pins/toolchain")
        result[identity] = item
    return result


def _require_exact_keys(value: Any, keys: set[str], role: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise AdmissionError(f"{role} fields changed")
    return value


def _require_reviewed_version(
    toolchain: Any, observed_version: Any, role: str
) -> None:
    if not isinstance(toolchain, dict) or not isinstance(observed_version, str):
        raise AdmissionError(f"{role} toolchain receipt is incomplete")
    exact = toolchain.get("reviewed_version")
    prefix = toolchain.get("reviewed_version_prefix")
    if isinstance(exact, str):
        matches = observed_version == exact
    elif isinstance(prefix, str):
        matches = observed_version.startswith(prefix)
    else:
        matches = False
    if not matches:
        raise AdmissionError(
            f"{role} compiler differs from the current reviewed pin; "
            "a future explicit compiler-pin review is required"
        )


def _require_reviewed_closure_rodata(
    config: dict[str, Any],
    identity: str,
    item: dict[str, Any],
    pins: dict[str, Any],
    configured: Any,
) -> None:
    """Compare stable rodata pins and independently prove derived addresses."""
    configured = _require_exact_keys(
        configured,
        {"alignment", "section", "sha256", "size", "symbols"},
        f"{identity} configured rodata",
    )
    observed = _require_exact_keys(
        pins.get("rodata"),
        {
            "alignment", "offset", "runtime_address", "runtime_address_hex",
            "section", "sha256", "size", "symbols",
        },
        f"{identity} observed rodata",
    )
    configured_symbols = configured["symbols"]
    observed_symbols = observed["symbols"]
    if not isinstance(configured_symbols, list) or not isinstance(
        observed_symbols, list
    ):
        raise AdmissionError(f"{identity} rodata symbols are malformed")
    normalized_configured_symbols = []
    normalized_observed_symbols = []
    for symbol in configured_symbols:
        normalized_configured_symbols.append(copy.deepcopy(_require_exact_keys(
            symbol, {"name", "offset", "size"},
            f"{identity} configured rodata symbol",
        )))
    for symbol in observed_symbols:
        symbol = _require_exact_keys(
            symbol,
            {
                "closure_offset", "name", "offset", "runtime_address",
                "runtime_address_hex", "size",
            },
            f"{identity} observed rodata symbol",
        )
        normalized_observed_symbols.append({
            key: symbol[key] for key in ("name", "offset", "size")
        })
    normalized_observed = {
        key: observed[key]
        for key in ("alignment", "section", "sha256", "size")
    }
    normalized_observed["symbols"] = normalized_observed_symbols
    normalized_configured = {
        **{key: configured[key] for key in (
            "alignment", "section", "sha256", "size"
        )},
        "symbols": normalized_configured_symbols,
    }
    if normalized_observed != normalized_configured:
        raise AdmissionError(
            f"{identity} closure rodata differs from current reviewed pins"
        )

    alignment = observed["alignment"]
    rodata_size = observed["size"]
    rodata_offset = observed["offset"]
    if (
        not isinstance(alignment, int)
        or alignment <= 0
        or alignment & (alignment - 1)
        or not isinstance(rodata_size, int)
        or rodata_size <= 0
        or not isinstance(rodata_offset, int)
        or rodata_offset < pins.get("size", -1)
        or rodata_offset % alignment
        or rodata_offset != pins.get("rodata_offset")
        or rodata_offset + rodata_size != pins.get("closure_size")
    ):
        raise AdmissionError(f"{identity} derived rodata extent changed")
    placement = item.get("placement")
    if not isinstance(placement, dict):
        raise AdmissionError(f"{identity} closure placement is missing")
    run_base = config.get("run_base")
    preamble = config.get("preamble_bytes")
    base_size = config.get("base", {}).get("size")
    text_runtime = placement.get("runtime_address")
    expected_text_runtime = (
        run_base + base_size + pins["offset"] - preamble
        if all(isinstance(value, int) for value in (run_base, base_size, preamble))
        else None
    )
    if (
        placement.get("alignment") != pins.get("alignment")
        or placement.get("offset") != pins.get("offset")
        or placement.get("size") != pins.get("closure_size")
        or placement.get("text_size") != pins.get("size")
        or not isinstance(text_runtime, int)
        or not isinstance(expected_text_runtime, int)
        or text_runtime != expected_text_runtime
        or placement.get("runtime_address_hex") != f"0x{text_runtime:08X}"
    ):
        raise AdmissionError(f"{identity} derived closure placement changed")
    rodata_runtime = text_runtime + rodata_offset
    if (
        observed["runtime_address"] != rodata_runtime
        or observed["runtime_address_hex"] != f"0x{rodata_runtime:08X}"
        or item.get("extraction", {}).get("rodata") != observed
    ):
        raise AdmissionError(f"{identity} derived rodata address changed")
    cursor = 0
    names: set[str] = set()
    for configured_symbol, observed_symbol in zip(
        normalized_configured_symbols, observed_symbols
    ):
        name = configured_symbol["name"]
        offset = configured_symbol["offset"]
        size = configured_symbol["size"]
        if (
            not isinstance(name, str)
            or not name
            or name in names
            or not isinstance(offset, int)
            or not isinstance(size, int)
            or size <= 0
            or offset < cursor
            or offset + size > rodata_size
            or observed_symbol["closure_offset"] != rodata_offset + offset
            or observed_symbol["runtime_address"] != rodata_runtime + offset
            or observed_symbol["runtime_address_hex"]
            != f"0x{rodata_runtime + offset:08X}"
        ):
            raise AdmissionError(f"{identity} derived rodata symbol changed")
        names.add(name)
        cursor = offset + size


def _require_reviewed_core_leaf_pins(
    config: dict[str, Any], profile: str, observation: dict[str, Any]
) -> None:
    stage = observation["core_stage"]
    filtered = filter_config_for_profile(config, profile)
    specifications = (
        ("isolated_leaves", False, {"size", "sha256"}),
        ("relocated_leaves", False, None),
        ("in_place_leaves", False, {"size", "sha256"}),
        ("in_place_data", True, {"size", "sha256", "alignment"}),
    )
    for key, data, scalar_keys in specifications:
        observed = _indexed_leaves(stage, key, data=data)
        configured: dict[str, dict[str, Any]] = {}
        for leaf in filtered.get(key, []):
            if not isinstance(leaf, dict):
                raise AdmissionError(f"configured {key} entry is malformed")
            identity = leaf.get("symbol" if data else "function")
            if not isinstance(identity, str) or identity in configured:
                raise AdmissionError(f"configured {key} identities are ambiguous")
            try:
                configured[identity] = resolve_leaf_profile(leaf, profile)
            except BuildError as error:
                raise AdmissionError(str(error)) from error
        if set(observed) != set(configured):
            raise AdmissionError(
                f"observed {key} differ from the current reviewed leaf set"
            )
        for identity, item in observed.items():
            effective = configured[identity]
            pins = item["pins"]
            expected = effective.get("expected")
            if scalar_keys is not None:
                _require_exact_keys(pins, scalar_keys, f"{identity} pins")
                if pins != expected:
                    raise AdmissionError(
                        f"{identity} differs from current reviewed pins; "
                        "a future explicit leaf-pin review is required"
                    )
            else:
                base_keys = {
                    "size", "sha256", "alignment", "offset",
                    "unrelocated_sha256", "relocations",
                }
                closure = effective.get("closure")
                allowed = set(base_keys)
                if isinstance(closure, dict):
                    allowed.update(
                        {"closure_size", "closure_sha256", "rodata_offset", "rodata"}
                    )
                _require_exact_keys(pins, allowed, f"{identity} pins")
                pin_expected = {
                    name: pins[name] for name in pins
                    if name not in ("relocations", "rodata")
                }
                if pin_expected != expected or pins["relocations"] != effective.get(
                    "relocations"
                ):
                    raise AdmissionError(
                        f"{identity} differs from current reviewed pins; "
                        "a future explicit leaf-pin review is required"
                    )
                if isinstance(closure, dict):
                    if (
                        item.get("extraction", {}).get("section")
                        != closure.get("text_section")
                    ):
                        raise AdmissionError(
                            f"{identity} closure differs from current reviewed pins"
                        )
                    _require_reviewed_closure_rodata(
                        config, identity, item, pins, closure.get("rodata")
                    )
            _require_reviewed_version(
                effective.get("toolchain"),
                item.get("toolchain", {}).get("version"),
                identity,
            )


def update_profile_pins(
    config: dict[str, Any], profile: str, observation: dict[str, Any]
) -> None:
    """Update only byte-proven final/PT pins; retain reviewed compiler pins."""
    stage = observation["core_stage"]
    stage_expected = _require_exact_keys(
        stage.get("expected"),
        {"overlay_size", "overlay_sha256", "component_size", "component_sha256"},
        "core-stage expected",
    )
    final = _require_exact_keys(
        observation.get("final"),
        {"overlay_size", "overlay_sha256", "component_size", "component_sha256"},
        "final expected",
    )
    if profile == APPLE_PROFILE:
        reviewed_stage = config.get("core_stage_expected")
        selected_toolchain = config.get("toolchain")
        config["expected"] = copy.deepcopy(final)
    else:
        selected = config.get("toolchain_profiles", {}).get(profile)
        if not isinstance(selected, dict):
            raise AdmissionError(f"config lacks profile {profile!r}")
        reviewed_stage = selected.get("core_stage_expected")
        selected_toolchain = {**config.get("toolchain", {}), **selected}
        selected["expected"] = copy.deepcopy(final)
    if stage_expected != reviewed_stage:
        raise AdmissionError(
            "core-stage pins differ from the current reviewed generation; "
            "a future explicit core-pin review is required"
        )
    _require_reviewed_version(
        selected_toolchain, observation.get("toolchain", {}).get("version"),
        f"{profile} core stage",
    )

    providers = config.get("post_link_providers")
    if not isinstance(providers, dict):
        raise AdmissionError("config post-link providers are missing")
    lib_profile = providers.get("liblc3_ltpf", {}).get("profiles", {}).get(profile)
    pt_profile = providers.get("pt_protocol", {}).get("profiles", {}).get(profile)
    if not isinstance(lib_profile, dict) or not isinstance(pt_profile, dict):
        raise AdmissionError(f"config provider pins are missing for {profile!r}")
    lib_observed = observation["liblc3_ltpf"]
    observed_overlay = {
        "size": lib_observed["payload_size"],
        "sha256": lib_observed["payload_sha256"],
    }
    observed_component = {
        "size": lib_observed["component_size"],
        "sha256": lib_observed["component_sha256"],
    }
    if (
        observed_overlay != lib_profile.get("overlay")
        or observed_component != lib_profile.get("component")
    ):
        raise AdmissionError(
            "liblc3 pins differ from the current reviewed generation; "
            "a future explicit liblc3-pin review is required"
        )
    if "placement" in lib_profile:
        sections = lib_observed.get("placement", {}).get("sections")
        if not isinstance(sections, dict):
            raise AdmissionError("curated liblc3 cave placement disappeared")
        for name, configured in lib_profile["placement"].items():
            observed = sections.get(name)
            if not isinstance(configured, dict) or not isinstance(observed, dict):
                raise AdmissionError("curated liblc3 cave placement changed")
            for field in ("file_offset", "runtime_address", "capacity"):
                if observed.get(field) != configured.get(field):
                    raise AdmissionError("curated liblc3 cave placement changed")
    elif isinstance(lib_observed.get("placement", {}).get("sections"), dict):
        raise AdmissionError("unexpected liblc3 cave placement appeared")
    pt_profile.clear()
    pt_profile.update(
        {
            "payload_size": observation["pt_protocol"]["payload_size"],
            "payload_sha256": observation["pt_protocol"]["payload_sha256"],
            "interval_sha256": observation["pt_protocol"]["interval_sha256"],
        }
    )
    configured_cff = providers.get("freetype_cff")
    observed_cff = observation.get("freetype_cff")
    if configured_cff is not None or observed_cff is not None:
        if not isinstance(configured_cff, dict) or not isinstance(observed_cff, dict):
            raise AdmissionError(
                "FreeType CFF config and canonical observation must be admitted together"
            )
        configured_placement = _require_exact_keys(
            configured_cff.get("placement"),
            {
                "stock_start", "stock_end_exclusive", "tail_start",
                "tail_end_exclusive", "module_class_pointer",
            },
            "configured FreeType CFF placement",
        )
        observed_sections = observed_cff["placement"]["sections"]
        stock_sections = [row for row in observed_sections
                          if row["name"].startswith(".cff_stock_")]
        host_sections = [row for row in observed_sections
                         if row["name"].startswith(".cff_host_")]
        observed_patch = int(
            observed_cff["module_class_patch"]["runtime_address"], 16
        )
        host_scatter = observed_cff["placement"].get("host_scatter") is True
        placement_valid = (
            len(stock_sections) == 3
            and stock_sections[0]["start"] == configured_placement["stock_start"]
            and stock_sections[-1]["end_exclusive"]
                <= configured_placement["stock_end_exclusive"]
            and observed_patch == configured_placement["module_class_pointer"]
        )
        if not host_scatter:
            tail_sections = observed_sections[2:]
            placement_valid = placement_valid and (
                tail_sections[0]["start"] >= configured_placement["tail_start"]
                and tail_sections[-1]["end_exclusive"]
                    == configured_placement["tail_end_exclusive"]
            )
        else:
            placement_valid = placement_valid and bool(host_sections)
        if (
            configured_cff.get("license") != CFF_LICENSE
            or configured_cff.get("hardware") != DEFERRED_HARDWARE_POLICY
            or not placement_valid
        ):
            raise AdmissionError("FreeType CFF fixed placement contract changed")
    _require_reviewed_core_leaf_pins(config, profile, observation)


def _derived_imu_span(config: dict[str, Any]) -> tuple[int, int]:
    run_base = config.get("run_base")
    preamble = config.get("preamble_bytes")
    if not isinstance(run_base, int) or not isinstance(preamble, int):
        raise AdmissionError("Apollo run-base/preamble contract is missing")
    start = preamble + IMU_RUNTIME_START - run_base
    end = preamble + IMU_RUNTIME_END - run_base
    if start < preamble or end <= start:
        raise AdmissionError("derived stock IMU donor span is invalid")
    return start, end


def _partition(regions: list[dict[str, Any]], size: int, role: str) -> None:
    cursor = 0
    outputs: set[str] = set()
    for region in sorted(regions, key=lambda item: item.get("file_offset", -1)):
        offset = region.get("file_offset")
        length = region.get("size")
        output = region.get("output")
        if (
            not isinstance(offset, int)
            or not isinstance(length, int)
            or length <= 0
            or offset != cursor
        ):
            raise AdmissionError(f"{role} has a duplicate, gap, or overlap at {cursor}")
        if not isinstance(output, str) or output in outputs:
            raise AdmissionError(f"{role} has a duplicate/invalid output path")
        outputs.add(output)
        cursor += length
    if cursor != size:
        raise AdmissionError(f"{role} covers {cursor} of {size} bytes")


def _retarget_output(value: str, target: int) -> str:
    return re.sub(r"-0x[0-9a-fA-F]+(?=\.bin$)", f"-0x{target:08x}", value)


def _runtime_file_offset(config: dict[str, Any], runtime_address: int) -> int:
    return config["preamble_bytes"] + runtime_address - config["run_base"]


def _replace_exact_interval(
    regions: list[dict[str, Any]],
    start: int,
    end: int,
    replacement: list[dict[str, Any]],
    role: str,
) -> list[dict[str, Any]]:
    overlapping = [
        (index, region)
        for index, region in enumerate(regions)
        if region["file_offset"] < end
        and region["file_offset"] + region["size"] > start
    ]
    if not overlapping:
        raise AdmissionError(f"{role} is absent from the manifest")
    cursor = start
    for _index, region in overlapping:
        if region["file_offset"] != cursor:
            raise AdmissionError(f"manifest does not exactly tile {role}")
        cursor += region["size"]
    if cursor != end:
        raise AdmissionError(f"manifest {role} has a wrong offset or size")
    first = overlapping[0][0]
    last = overlapping[-1][0]
    return regions[:first] + replacement + regions[last + 1 :]


def _validate_pt_contract(
    config: dict[str, Any],
    profile: str,
    observation: dict[str, Any],
    component: bytes,
    core_stage_component: bytes,
    liblc3_component: bytes,
    pt_component: bytes | None = None,
) -> None:
    def exact_int(value: Any, role: str, *, minimum: int = 0) -> int:
        if type(value) is not int or value < minimum:
            raise AdmissionError(f"{role} is not a reviewed integer")
        return value

    final_size, final_digest = _pin(
        observation.get("final"), "component_size", "component_sha256",
        "PT final component",
    )
    core_size, core_digest = _pin(
        observation.get("core_stage", {}).get("expected"),
        "component_size", "component_sha256", "PT core-stage component",
    )
    liblc3_size, liblc3_digest = _pin(
        observation.get("liblc3_ltpf"),
        "component_size", "component_sha256", "PT liblc3 component",
    )
    if len(component) != final_size or _digest(component) != final_digest:
        raise AdmissionError(
            "PT final component differs from its authenticated receipt"
        )
    if int(observation.get("schema_version", 0)) >= 3:
        pt_record = _require_exact_keys(
            observation.get("intermediate_artifacts", {}).get("pt_component"),
            {"artifact", "size", "sha256"},
            "PT intermediate component",
        )
        pt_size, pt_digest = _pin(
            pt_record, "size", "sha256", "PT intermediate component",
        )
        if pt_component is None:
            raise AdmissionError("PT intermediate component is absent")
        final_pt_stage = (
            "PT intermediate", pt_component, pt_size, pt_digest,
        )
    else:
        final_pt_stage = ("final", component, final_size, final_digest)
    stages = (
        ("core stage", core_stage_component, core_size, core_digest),
        ("liblc3 intermediate", liblc3_component, liblc3_size, liblc3_digest),
        final_pt_stage,
    )
    for stage_name, stage, expected_size, expected_digest in stages:
        if len(stage) != expected_size or _digest(stage) != expected_digest:
            raise AdmissionError(
                f"PT {stage_name} component differs from its authenticated receipt"
            )

    pt = _require_exact_keys(
        observation.get("pt_protocol"),
        {
            "license", "payload_size", "payload_sha256", "interval_sha256",
            "placement", "source_provider_routes", "patch_sites",
            "writable_bytes", "hardware", "ingress_sites",
            "source_uart_route_receipt", "sources",
        },
        "PT observation",
    )
    configured_pt = config.get("post_link_providers", {}).get("pt_protocol", {})
    configured_sources = configured_pt.get("sources")
    observed_sources = pt["sources"]
    if (
        not isinstance(configured_sources, list)
        or observed_sources != configured_sources
        or len(configured_sources) != 29
    ):
        raise AdmissionError("PT source license records changed")
    source_paths: set[str] = set()
    license_counts = {
        license_id: 0 for license_id in PT_SOURCE_LICENSE_COUNTS
    }
    for record in configured_sources:
        if not isinstance(record, dict):
            raise AdmissionError("PT source license record changed")
        license_id = record.get("license")
        expected_keys = {"path", "size", "sha256", "license"}
        if license_id == "Apache-2.0":
            expected_keys.update(PT_APACHE_SOURCE_METADATA)
        if set(record) != expected_keys:
            raise AdmissionError("PT source license record changed")
        path = record["path"]
        size = record["size"]
        source_sha256 = record["sha256"]
        if (
            not isinstance(path, str)
            or path in source_paths
            or type(size) is not int
            or size <= 0
            or not isinstance(source_sha256, str)
            or re.fullmatch(r"[0-9a-f]{64}", source_sha256) is None
            or license_id not in license_counts
        ):
            raise AdmissionError("PT source license record changed")
        source_paths.add(path)
        license_counts[license_id] += 1
    apache_paths = {
        record["path"] for record in configured_sources
        if record["license"] == "Apache-2.0"
    }
    if (
        pt["license"] != configured_pt.get("license")
        or pt["license"] != PT_AGGREGATE_LICENSE
        or license_counts != PT_SOURCE_LICENSE_COUNTS
        or apache_paths != {PT_APACHE_SOURCE}
        or any(
            record.get(key) != value
            for record in configured_sources
            if record["path"] == PT_APACHE_SOURCE
            for key, value in PT_APACHE_SOURCE_METADATA.items()
        )
        or [record["path"] for record in configured_sources]
        != sorted(source_paths)
        or pt["hardware"] != DEFERRED_HARDWARE_POLICY
        or configured_pt.get("hardware") != DEFERRED_HARDWARE_POLICY
        or pt["patch_sites"] != 0
        or pt["writable_bytes"] != 0
        or pt["source_provider_routes"] != PT_SOURCE_PROVIDER_ROUTE_COUNT
    ):
        raise AdmissionError("PT policy, licensing, or route-count receipt changed")
    placement = _require_exact_keys(
        pt["placement"],
        {
            "runtime_start", "runtime_end_exclusive", "capacity",
            "linked_start", "linked_end_exclusive", "loadable_size",
            "padding_size", "writable_bytes", "payload_sha256",
            "interval_sha256", "sections",
        },
        "PT placement",
    )
    if (
        placement["payload_sha256"] != pt["payload_sha256"]
        or placement["interval_sha256"] != pt["interval_sha256"]
        or placement["loadable_size"] != pt["payload_size"]
        or placement["writable_bytes"] != pt["writable_bytes"]
    ):
        raise AdmissionError("PT top-level and placement receipts disagree")
    configured_placement = configured_pt.get("placement")
    if not isinstance(configured_placement, dict) or any(
        placement.get(key) != configured_placement.get(key)
        for key in ("runtime_start", "runtime_end_exclusive", "capacity")
    ):
        raise AdmissionError("PT placement differs from the configured fixed interval")
    configured_ingress = configured_pt.get("legacy_ingress")
    if configured_ingress != {
        "entry": PT_LEGACY_ENTRY,
        "postprocess": PT_LEGACY_POSTPROCESS,
    }:
        raise AdmissionError("configured PT legacy ingress changed")
    legacy_sections = {
        ".pt_legacy_entry": configured_ingress.get("entry"),
        ".pt_legacy_postprocess": configured_ingress.get("postprocess"),
    }
    sections = placement["sections"]
    if not isinstance(sections, dict) or not sections:
        raise AdmissionError("PT section receipt is empty")
    safe_section = re.compile(
        r"\.(?:pt_legacy_entry|pt_legacy_postprocess|text(?:\.[A-Za-z0-9_]+)*|"
        r"rodata(?:\.[A-Za-z0-9_]+)*)\Z"
    )
    for name, record in sections.items():
        if not isinstance(name, str) or safe_section.fullmatch(name) is None:
            raise AdmissionError("PT section name is unsafe or unsupported")
        _require_exact_keys(
            record, {"runtime_address", "size", "sha256"}, f"PT section {name}"
        )
        _pin(record, "size", "sha256", f"PT section {name}")
    if any(
        not isinstance(address, int)
        or not isinstance(sections.get(name), dict)
        or sections[name].get("runtime_address") != address
        for name, address in legacy_sections.items()
    ):
        raise AdmissionError("PT legacy ABI sections differ from configured ingress")

    route = _require_exact_keys(
        pt["source_uart_route_receipt"],
        {
            "mode", "profile", "function", "strict_relocation_contract",
            "profile_route_active", "stage_overlay", "leaf", "relocations",
        },
        "PT source-UART route receipt",
    )
    expected_route_active = profile == APPLE_PROFILE
    expected_route_mode = (
        "source_overlay_relocation"
        if expected_route_active else "authenticated_donor_direct"
    )
    if (
        not isinstance(route, dict)
        or route.get("profile") != profile
        or route.get("strict_relocation_contract") is not True
        or route.get("profile_route_active") is not expected_route_active
        or route.get("mode") != expected_route_mode
        or route.get("function") != "open_cfw_box_uart_handle"
    ):
        raise AdmissionError("PT source-UART route receipt changed")
    _require_exact_keys(
        route["stage_overlay"], {"size", "sha256"},
        "PT source-UART stage overlay",
    )
    _require_exact_keys(
        route["leaf"], {"size", "sha256", "unrelocated_sha256", "alignment", "offset"},
        "PT source-UART leaf receipt",
    )
    stage_expected = observation.get("core_stage", {}).get("expected")
    expected_stage_overlay = (
        {
            "size": stage_expected.get("overlay_size"),
            "sha256": stage_expected.get("overlay_sha256"),
        }
        if isinstance(stage_expected, dict) else None
    )
    if route["stage_overlay"] != expected_stage_overlay:
        raise AdmissionError("PT source-UART stage identity is not bound to core stage")
    configured_leaves = [
        item for item in config.get("relocated_leaves", [])
        if isinstance(item, dict) and item.get("function") == route["function"]
    ]
    if len(configured_leaves) != 1:
        raise AdmissionError("configured PT source-UART leaf identity is ambiguous")
    configured_leaf = configured_leaves[0]
    if (
        configured_leaf.get("strict_relocation_contract") is not True
        or configured_leaf.get("profiles") != [APPLE_PROFILE]
    ):
        raise AdmissionError("configured PT source-UART leaf routing changed")
    expected_leaf = configured_leaf.get("expected")
    if not isinstance(expected_leaf, dict) or route["leaf"] != {
        key: expected_leaf.get(key)
        for key in ("size", "sha256", "unrelocated_sha256", "alignment", "offset")
    }:
        raise AdmissionError("PT source-UART leaf identity differs from reviewed pins")
    if expected_route_active:
        observed_leaves = [
            item for item in observation.get("core_stage", {}).get(
                "relocated_leaves", []
            )
            if isinstance(item, dict)
            and item.get("extraction", {}).get("function") == route["function"]
        ]
        if len(observed_leaves) != 1 or any(
            observed_leaves[0].get("pins", {}).get(key) != route["leaf"][key]
            for key in route["leaf"]
        ):
            raise AdmissionError("PT source-UART leaf identity is not bound to core stage")
    relocations = route["relocations"]
    if not isinstance(relocations, list) or len(relocations) != 2:
        raise AdmissionError("PT source-UART relocation receipt count changed")
    route_targets = []
    route_contract = []
    for relocation in relocations:
        relocation = _require_exact_keys(
            relocation,
            {"symbol", "type", "target_address", "offset", "type_id"},
            "PT source-UART relocation",
        )
        if relocation.get("type") != "R_ARM_THM_CALL" or relocation.get("type_id") != 10:
            raise AdmissionError("PT source-UART relocation kind changed")
        route_targets.append((relocation.get("symbol"), relocation.get("target_address")))
        route_contract.append({
            key: relocation[key]
            for key in ("symbol", "type", "target_address", "offset")
        })
    if sorted(route_targets) != sorted((
        ("open_cfw_retained_box_uart_product_test", configured_ingress["entry"]),
        ("open_cfw_retained_box_uart_execute", configured_ingress["postprocess"]),
    )):
        raise AdmissionError("PT source-UART relocation targets changed")
    route_symbols = {item[0] for item in route_targets}
    configured_relocations = [
        {
            key: item.get(key)
            for key in ("symbol", "type", "target_address", "offset")
        }
        for item in configured_leaf.get("relocations", [])
        if isinstance(item, dict) and item.get("symbol") in route_symbols
    ]
    if sorted(route_contract, key=lambda item: item["symbol"]) != sorted(
        configured_relocations, key=lambda item: item["symbol"]
    ):
        raise AdmissionError("PT source-UART relocation offsets differ from reviewed pins")

    mapping = _require_exact_keys(
        observation.get("image_mapping"),
        {"base_size", "run_base", "preamble_bytes"},
        "PT image mapping",
    )
    run_base = exact_int(config.get("run_base"), "Apollo run base")
    preamble = exact_int(config.get("preamble_bytes"), "Apollo preamble")
    base_size = exact_int(config.get("base", {}).get("size"), "Apollo base size", minimum=1)
    if mapping != {
        "base_size": base_size,
        "run_base": run_base,
        "preamble_bytes": preamble,
    }:
        raise AdmissionError("PT image mapping differs from reviewed config")
    leaf_offset = exact_int(route["leaf"].get("offset"), "PT leaf offset")
    leaf_size = exact_int(route["leaf"].get("size"), "PT leaf size", minimum=1)
    leaf_runtime = run_base + base_size + leaf_offset - preamble
    if leaf_runtime % 2:
        raise AdmissionError("PT source-UART leaf runtime is not halfword aligned")
    leaf_file_offset = _runtime_file_offset(config, leaf_runtime)
    if expected_route_active:
        for stage_name, stage, _expected_size, _expected_digest in stages:
            leaf_bytes = stage[leaf_file_offset:leaf_file_offset + leaf_size]
            if (
                len(leaf_bytes) != leaf_size
                or _digest(leaf_bytes) != route["leaf"]["sha256"]
            ):
                raise AdmissionError(
                    f"PT source-UART leaf differs in {stage_name} component"
                )

    by_symbol = {item["symbol"]: item for item in relocations}
    expected_symbols = {
        "open_cfw_retained_box_uart_product_test",
        "open_cfw_retained_box_uart_execute",
    }
    if set(by_symbol) != expected_symbols:
        raise AdmissionError("PT source-UART relocation symbols changed")
    product_site = leaf_runtime + exact_int(
        by_symbol["open_cfw_retained_box_uart_product_test"]["offset"],
        "PT product-test relocation offset",
    )
    execute_site = leaf_runtime + exact_int(
        by_symbol["open_cfw_retained_box_uart_execute"]["offset"],
        "PT execute relocation offset",
    )

    common_site = (
        PT_STOCK_DIRECT_SITE,
        PT_LEGACY_ENTRY,
        "open_cfw_pt_protocol_legacy_entry",
        "stock_direct_call",
        PT_DONOR_INGRESS_EVIDENCE,
        PT_DONOR_INGRESS_SHA256[PT_STOCK_DIRECT_SITE],
    )
    if expected_route_active:
        expected_sites = (
            common_site,
            (
                product_site, PT_LEGACY_ENTRY,
                "open_cfw_pt_protocol_legacy_entry",
                "source_uart_relocation", PT_SOURCE_UART_EVIDENCE, None,
            ),
            (
                execute_site, PT_LEGACY_POSTPROCESS,
                "open_cfw_pt_protocol_legacy_postprocess",
                "source_uart_relocation", PT_SOURCE_UART_EVIDENCE, None,
            ),
        )
    else:
        expected_sites = (
            common_site,
            (
                PT_RETIRED_SOURCE_UART_SITES[0], PT_LEGACY_ENTRY,
                "open_cfw_pt_protocol_legacy_entry",
                "source_uart_relocation", PT_DONOR_INGRESS_EVIDENCE,
                PT_DONOR_INGRESS_SHA256[PT_RETIRED_SOURCE_UART_SITES[0]],
            ),
            (
                PT_RETIRED_SOURCE_UART_SITES[1], PT_LEGACY_POSTPROCESS,
                "open_cfw_pt_protocol_legacy_postprocess",
                "source_uart_relocation", PT_DONOR_INGRESS_EVIDENCE,
                PT_DONOR_INGRESS_SHA256[PT_RETIRED_SOURCE_UART_SITES[1]],
            ),
        )

    ingress = pt["ingress_sites"]
    if not isinstance(ingress, list) or len(ingress) != len(expected_sites):
        raise AdmissionError("PT legacy ingress receipt count changed")
    observed_sites: dict[int, dict[str, Any]] = {}
    for item in ingress:
        site = _require_exact_keys(
            item,
            {
                "runtime_address", "target_address", "target_function", "route",
                "evidence", "authenticated_size", "authenticated_sha256",
            },
            "PT legacy ingress site",
        )
        runtime = exact_int(site["runtime_address"], "PT ingress runtime")
        target = exact_int(site["target_address"], "PT ingress target")
        if runtime in observed_sites or type(site["authenticated_size"]) is not int:
            raise AdmissionError("PT legacy ingress site is ambiguous")
        observed_sites[runtime] = site
        if site["authenticated_size"] != 4:
            raise AdmissionError("PT legacy ingress instruction size changed")
        for stage_name, stage, _expected_size, _expected_digest in stages:
            offset = _runtime_file_offset(config, runtime)
            encoded = stage[offset:offset + 4]
            try:
                decoded = decode_thumb_branch(runtime, encoded, link=True)
                canonical = encode_thumb_branch(runtime, target, link=True)
            except BuildError as error:
                raise AdmissionError(
                    f"PT ingress is not an authenticated BL in {stage_name}"
                ) from error
            if len(encoded) != 4 or decoded != target or encoded != canonical:
                raise AdmissionError(
                    f"PT ingress BL differs in {stage_name} component"
                )
            if _digest(encoded) != site["authenticated_sha256"]:
                raise AdmissionError("PT legacy ingress bytes differ from receipt")

    for runtime, target, function, route_name, evidence, donor_digest in expected_sites:
        site = observed_sites.get(runtime)
        if site is None or (
            site["target_address"], site["target_function"], site["route"],
            site["evidence"],
        ) != (target, function, route_name, evidence):
            raise AdmissionError("PT legacy ingress runtime/route/target contract changed")
        if donor_digest is not None and site["authenticated_sha256"] != donor_digest:
            raise AdmissionError("PT donor ingress hash changed")

    if expected_route_active:
        replacements = [
            item for item in config.get("patch_sites", [])
            if isinstance(item, dict) and (
                item.get("runtime_address") == PT_SOURCE_UART_ENTRY_REDIRECT
                or item.get("name") == "replace_box_uart_mgr_05"
                or item.get("target_function") == "open_cfw_box_uart_handle"
            )
        ]
        if len(replacements) != 1 or replacements[0] != {
            "branch": "b_w",
            "expected_sha256": (
                "8cf6dda5fc9dd79b3f28467c08eb9272255de756ecddfaccbec74399e53cc2d1"
            ),
            "expected_size": 750,
            "name": "replace_box_uart_mgr_05",
            "profiles": [APPLE_PROFILE],
            "runtime_address": PT_SOURCE_UART_ENTRY_REDIRECT,
            "target_function": "open_cfw_box_uart_handle",
        }:
            raise AdmissionError("PT source-UART entry replacement contract changed")
        for stage_name, stage, _expected_size, _expected_digest in stages:
            entry_offset = _runtime_file_offset(config, PT_SOURCE_UART_ENTRY_REDIRECT)
            entry = stage[entry_offset:entry_offset + 4]
            try:
                target = decode_thumb_branch(
                    PT_SOURCE_UART_ENTRY_REDIRECT, entry, link=False
                )
                canonical = encode_thumb_branch(
                    PT_SOURCE_UART_ENTRY_REDIRECT, leaf_runtime, link=False
                )
            except BuildError as error:
                raise AdmissionError(
                    f"PT source-UART entry is not a B.W in {stage_name}"
                ) from error
            if target != leaf_runtime or entry != canonical:
                raise AdmissionError(
                    f"PT source-UART entry redirect changed in {stage_name}"
                )
            for retired in PT_RETIRED_SOURCE_UART_SITES:
                retired_offset = _runtime_file_offset(config, retired)
                if stage[retired_offset:retired_offset + 4] != PT_THUMB_NOP_PAIR:
                    raise AdmissionError(
                        f"retired PT source-UART site is not NOP fill in {stage_name}"
                    )
    else:
        if any(
            len(stage) > leaf_file_offset
            for _name, stage, _size, _digest_value in stages
        ):
            raise AdmissionError("Linux component unexpectedly contains Apple source-UART leaf")


def _synchronize_pt_interval(
    regions: list[dict[str, Any]],
    config: dict[str, Any],
    observation: dict[str, Any],
    component: bytes,
) -> list[dict[str, Any]]:
    pt = observation["pt_protocol"]
    placement = pt["placement"]
    runtime_start = placement.get("runtime_start")
    runtime_end = placement.get("runtime_end_exclusive")
    capacity = placement.get("capacity")
    loadable_size = placement.get("loadable_size")
    padding_size = placement.get("padding_size")
    if (
        not all(
            isinstance(value, int)
            for value in (
                runtime_start,
                runtime_end,
                capacity,
                loadable_size,
                padding_size,
            )
        )
        or runtime_end - runtime_start != capacity
        or loadable_size + padding_size != capacity
        or placement.get("writable_bytes") != 0
    ):
        raise AdmissionError("PT fixed-interval capacity accounting changed")
    start = _runtime_file_offset(config, runtime_start)
    end = _runtime_file_offset(config, runtime_end)
    interval = component[start:end]
    if len(interval) != capacity or _digest(interval) != pt["interval_sha256"]:
        raise AdmissionError("PT fixed-interval artifact bytes differ from receipt")

    sections = []
    for name, record in placement["sections"].items():
        if (
            not isinstance(name, str)
            or not isinstance(record, dict)
            or not isinstance(record.get("runtime_address"), int)
        ):
            raise AdmissionError("PT section receipt is malformed")
        size, section_digest = _pin(record, "size", "sha256", f"PT section {name}")
        sections.append(
            (record["runtime_address"], name, size, section_digest)
        )
    sections.sort()
    if not sections:
        raise AdmissionError("PT section receipt is empty")
    if placement.get("linked_start") != sections[0][0] or placement.get(
        "linked_end_exclusive"
    ) != sections[-1][0] + sections[-1][2]:
        raise AdmissionError("PT linked section extent changed")
    if sum(size for _address, _name, size, _digest_value in sections) != loadable_size:
        raise AdmissionError("PT source-section sum differs from loadable_size")

    cursor = runtime_start
    source_payload = bytearray()
    rebuilt: list[dict[str, Any]] = []

    def append_gap(gap_start: int, gap_end: int) -> None:
        if gap_end <= gap_start:
            return
        file_offset = _runtime_file_offset(config, gap_start)
        gap = component[file_offset:file_offset + gap_end - gap_start]
        if set(gap) != {0xFF}:
            raise AdmissionError("PT generated padding contains non-erased bytes")
        rebuilt.append(
            {
                "address_status": "generated_padding",
                "file_offset": file_offset,
                "function": "Generated erased padding around fixed-address PT source",
                "name": f"pt_protocol_in_place_generated_gap_{gap_start:08x}",
                "output": (
                    "apollo510b/main-pt-generated_gap_"
                    f"{gap_start:08x}-0x{gap_start:08x}.bin"
                ),
                "size": gap_end - gap_start,
                "target": "apollo510b_internal_mram",
                "target_address": gap_start,
            }
        )

    for runtime_address, name, size, section_digest in sections:
        if runtime_address < cursor or runtime_address + size > runtime_end:
            raise AdmissionError("PT sections duplicate, overlap, or escape capacity")
        append_gap(cursor, runtime_address)
        file_offset = _runtime_file_offset(config, runtime_address)
        payload = component[file_offset:file_offset + size]
        if len(payload) != size or _digest(payload) != section_digest:
            raise AdmissionError(f"PT section {name} differs from artifact bytes")
        source_payload.extend(payload)
        slug = name.lstrip(".").replace(".", "-").replace("_", "-")
        status = (
            "source_compiled_rodata"
            if name.startswith(".rodata")
            else "source_compiled"
        )
        rebuilt.append(
            {
                "address_status": status,
                "file_offset": file_offset,
                "function": (
                    "Compiled MIT AND Apache-2.0 aggregate G2 PT provider "
                    f"section {name}"
                ),
                "name": f"pt_protocol_in_place_source_{slug}",
                "output": (
                    f"apollo510b/main-pt-source_{slug}-0x{runtime_address:08x}.bin"
                ),
                "size": size,
                "target": "apollo510b_internal_mram",
                "target_address": runtime_address,
            }
        )
        cursor = runtime_address + size
    append_gap(cursor, runtime_end)
    if _digest(bytes(source_payload)) != pt["payload_sha256"]:
        raise AdmissionError("PT concatenated source sections differ from payload pin")
    source_sum = sum(
        row["size"] for row in rebuilt
        if row["address_status"].startswith("source_compiled")
    )
    padding_sum = sum(
        row["size"] for row in rebuilt
        if row["address_status"] == "generated_padding"
    )
    if source_sum != loadable_size or padding_sum != padding_size:
        raise AdmissionError("PT manifest source/padding accounting changed")
    synchronized = _replace_exact_interval(
        regions, start, end, rebuilt, "PT fixed interval"
    )
    following = [row for row in synchronized if row["file_offset"] >= end]
    if (
        not following
        or following[0]["file_offset"] != end
        or (
            "target_address" in following[0]
            and following[0]["target_address"] != runtime_end
        )
    ):
        raise AdmissionError("PT next fixed-address boundary changed")
    return synchronized


def _synchronize_liblc3_cave_regions(
    regions: list[dict[str, Any]],
    config: dict[str, Any],
    observation: dict[str, Any],
    final_component: bytes,
    core_stage_component: bytes,
    liblc3_component: bytes,
) -> list[dict[str, Any]]:
    def exact_int(value: Any, role: str, *, minimum: int = 0) -> int:
        if type(value) is not int or value < minimum:
            raise AdmissionError(f"{role} is not a reviewed integer")
        return value

    final_size, final_digest = _pin(
        observation.get("final"), "component_size", "component_sha256",
        "Apple final component",
    )
    if (
        len(final_component) != final_size
        or _digest(final_component) != final_digest
    ):
        raise AdmissionError("Apple final component differs from its receipt")
    core_size, core_digest = _pin(
        observation.get("core_stage", {}).get("expected"),
        "component_size", "component_sha256", "Apple core-stage component",
    )
    lib_size, lib_digest = _pin(
        observation.get("liblc3_ltpf"),
        "component_size", "component_sha256", "Apple liblc3 component",
    )
    if (
        len(core_stage_component) != core_size
        or _digest(core_stage_component) != core_digest
        or len(liblc3_component) != lib_size
        or _digest(liblc3_component) != lib_digest
    ):
        raise AdmissionError("Apple liblc3 stage artifacts differ from their receipts")
    liblc3 = observation["liblc3_ltpf"]
    sections = liblc3.get("placement", {}).get("sections")
    if not isinstance(sections, dict):
        raise AdmissionError("Apple liblc3 cave section receipt is missing")
    expected_names = {
        "text": {
            "source_name": "liblc3_ltpf_source_text",
            "source_function": (
                "Apache-2.0 Google liblc3 v1.1.3 LTPF text closure placed in "
                "the authenticated reclaimed _fileCmdParse tail"
            ),
            "source_output": (
                "apollo510b/main-source-liblc3-ltpf-text-0x00445664.bin"
            ),
            "tail_name": "liblc3_ltpf_text_cave_tail",
            "tail_function": (
                "Unused generated NOP fill remaining after the bounded liblc3 "
                "LTPF text closure"
            ),
            "tail_output": "apollo510b/main-source-liblc3-ltpf-text-tail.bin",
        },
        "rodata": {
            "source_name": "liblc3_ltpf_source_rodata",
            "source_function": (
                "Apache-2.0 Google liblc3 v1.1.3 LTPF dispatch and filter tables "
                "placed in the authenticated reclaimed health-detail tail"
            ),
            "source_output": (
                "apollo510b/main-source-liblc3-ltpf-rodata-0x004fc648.bin"
            ),
            "tail_name": "liblc3_ltpf_rodata_cave_tail",
            "tail_function": (
                "Unused generated NOP fill remaining after the bounded liblc3 "
                "LTPF table closure"
            ),
            "tail_output": "apollo510b/main-source-liblc3-ltpf-rodata-tail.bin",
        },
    }
    run_base = exact_int(config.get("run_base"), "liblc3 run base")
    preamble = exact_int(config.get("preamble_bytes"), "liblc3 preamble")
    reviewed = (
        config.get("post_link_providers", {})
        .get("liblc3_ltpf", {})
        .get("profiles", {})
        .get(APPLE_PROFILE, {})
        .get("placement")
    )
    if not isinstance(reviewed, dict) or set(reviewed) != set(expected_names):
        raise AdmissionError("reviewed Apple liblc3 cave placement changed")
    result = copy.deepcopy(regions)
    observed_payload = bytearray()
    matched: set[str] = set()
    extents: list[tuple[int, int, str]] = []
    for section_name, identities in expected_names.items():
        manifest_name = identities["source_name"]
        tail_name = identities["tail_name"]
        section = _require_exact_keys(
            sections.get(section_name),
            {"capacity", "file_offset", "runtime_address", "size", "sha256"},
            f"liblc3 {section_name} cave receipt",
        )
        size, section_digest = _pin(
            section, "size", "sha256", f"liblc3 {section_name} cave section"
        )
        size = exact_int(size, f"liblc3 {section_name} source size", minimum=1)
        file_offset = exact_int(
            section.get("file_offset"), f"liblc3 {section_name} file offset"
        )
        runtime_address = exact_int(
            section.get("runtime_address"), f"liblc3 {section_name} runtime"
        )
        capacity = exact_int(
            section.get("capacity"), f"liblc3 {section_name} capacity", minimum=1
        )
        configured = reviewed.get(section_name)
        if (
            not isinstance(configured, dict)
            or any(
                section[field] != configured.get(field)
                for field in ("file_offset", "runtime_address", "capacity")
            )
            or not isinstance(configured.get("expected_sha256"), str)
            or re.fullmatch(r"[0-9a-f]{64}", configured["expected_sha256"]) is None
            or runtime_address != run_base + file_offset - preamble
            or file_offset % 4
            or runtime_address % 4
            or size % 4
            or capacity % 2
            or size > capacity
        ):
            raise AdmissionError(
                f"liblc3 {section_name} cave mapping differs from reviewed placement"
            )
        matches = [row for row in result if row.get("name") == manifest_name]
        if len(matches) != 1:
            raise AdmissionError(f"liblc3 {section_name} manifest row is ambiguous")
        row = _require_exact_keys(
            matches[0],
            {
                "address_status", "file_offset", "function", "name", "output",
                "size", "target", "target_address",
            },
            f"liblc3 {section_name} source row",
        )
        if row != {
            "address_status": "source_compiled",
            "file_offset": file_offset,
            "function": identities["source_function"],
            "name": manifest_name,
            "output": identities["source_output"],
            "size": size,
            "target": "apollo510b_internal_mram",
            "target_address": runtime_address,
        }:
            raise AdmissionError(f"liblc3 {section_name} cave row changed")
        core_preimage = core_stage_component[file_offset:file_offset + size]
        lib_payload = liblc3_component[file_offset:file_offset + size]
        final_payload = final_component[file_offset:file_offset + size]
        if (
            len(core_preimage) != size
            or _digest(core_preimage) != configured["expected_sha256"]
            or core_preimage != b"\x00\xbf" * (size // 2)
        ):
            raise AdmissionError(
                f"liblc3 {section_name} core-stage preimage differs from reviewed pins"
            )
        if (
            len(lib_payload) != size
            or len(final_payload) != size
            or lib_payload != final_payload
            or _digest(lib_payload) != section_digest
        ):
            raise AdmissionError(f"liblc3 {section_name} cave bytes changed")
        observed_payload.extend(lib_payload)
        matched.add(manifest_name)
        tail_size = capacity - size
        tails = [item for item in result if item.get("name") == tail_name]
        if tail_size <= 0 or tail_size % 2:
            raise AdmissionError(
                f"liblc3 {section_name} cave tail is empty or not halfword-sized"
            )
        if len(tails) != 1:
            raise AdmissionError(f"liblc3 {section_name} cave tail is ambiguous")
        tail = _require_exact_keys(
            tails[0],
            {
                "address_status", "file_offset", "function", "name", "output",
                "size", "target", "target_address",
            },
            f"liblc3 {section_name} cave tail row",
        )
        tail_start = file_offset + size
        tail_runtime = runtime_address + size
        if (
            type(tail.get("file_offset")) is not int
            or type(tail.get("size")) is not int
            or type(tail.get("target_address")) is not int
            or tail.get("address_status") != "generated_alignment"
            or tail.get("file_offset") != tail_start
            or tail.get("size") != tail_size
            or tail.get("target_address") != tail_runtime
            or tail_start % 2
            or tail_runtime % 2
            or tail.get("function") != identities["tail_function"]
            or tail.get("output") != identities["tail_output"]
            or tail.get("target") != "apollo510b_internal_mram"
        ):
            raise AdmissionError(
                f"liblc3 {section_name} cave tail span/address/ownership changed"
            )
        expected_tail = b"\x00\xbf" * (tail_size // 2)
        stage_tail = core_stage_component[tail_start:tail_start + tail_size]
        liblc3_tail = liblc3_component[tail_start:tail_start + tail_size]
        final_tail = final_component[tail_start:tail_start + tail_size]
        if (
            len(stage_tail) != tail_size
            or len(liblc3_tail) != tail_size
            or len(final_tail) != tail_size
            or stage_tail != expected_tail
            or liblc3_tail != expected_tail
            or final_tail != expected_tail
        ):
            raise AdmissionError(
                f"liblc3 {section_name} cave tail differs from generated Thumb-NOP padding"
            )
        tail["address_status"] = "generated_alignment"
        tail["function"] = identities["tail_function"]
        matched.add(tail_name)
        extents.append((file_offset, file_offset + capacity, section_name))
    if len(extents) != 2 or extents != sorted(extents) or extents[0][1] > extents[1][0]:
        raise AdmissionError("liblc3 cave sections overlap or changed order")
    all_rows = {
        row.get("name") for row in regions
        if str(row.get("name", "")).startswith("liblc3_ltpf_")
    }
    if all_rows != matched:
        raise AdmissionError("unexpected liblc3 cave source/status rows remain")
    if len(observed_payload) != liblc3["payload_size"] or _digest(
        bytes(observed_payload)
    ) != liblc3["payload_sha256"]:
        raise AdmissionError("liblc3 cave rows do not reconstruct its payload")
    return result


def _linux_cff_profile_replacements(
    regions: list[dict[str, Any]],
    config: dict[str, Any],
    observation: dict[str, Any],
    donor: bytes,
    component: bytes,
) -> list[dict[str, Any]]:
    """Describe Linux CFF stock overwrites without reusing Apple text sizes."""
    cff = observation.get("freetype_cff")
    if cff is None:
        return []
    if not isinstance(cff, dict):
        raise AdmissionError("Linux FreeType CFF receipt is malformed")
    configured = config.get("post_link_providers", {}).get("freetype_cff", {})
    placement = configured.get("placement") if isinstance(configured, dict) else None
    if not isinstance(placement, dict):
        raise AdmissionError("configured FreeType CFF placement is missing")
    run_base = config["run_base"]
    preamble = config["preamble_bytes"]

    def file_offset(runtime: int) -> int:
        return preamble + runtime - run_base

    stock_start = file_offset(placement["stock_start"])
    stock_end = file_offset(placement["stock_end_exclusive"])
    stock_overlap = [
        row for row in regions
        if row["file_offset"] < stock_end
        and row["file_offset"] + row["size"] > stock_start
    ]
    if not stock_overlap:
        raise AdmissionError("Apple CFF stock rows are absent")
    capture_start = stock_overlap[0]["file_offset"]
    capture_end = stock_overlap[-1]["file_offset"] + stock_overlap[-1]["size"]
    sections = cff["placement"]["sections"][:2]
    rows: list[dict[str, Any]] = []
    cursor = capture_start

    def retained(start: int, end: int) -> None:
        if end <= start:
            return
        if component[start:end] != donor[start:end]:
            raise AdmissionError("Linux CFF retained stock bytes differ from donor")
        rows.append({
            "name": f"freetype_cff_retained_linux_{start:08x}_{end:08x}",
            "function": "Authenticated donor bytes retained around Linux CFF scatter",
            "file_offset": start,
            "size": end - start,
            "address_status": "official_blob",
            "output": f"apollo510b/cff-scatter-linux-retained-{start:08x}-{end:08x}.bin",
            "target": "apollo510b_internal_mram",
            "target_address": run_base + start - preamble,
        })

    for section in sections:
        start = file_offset(section["start"])
        end = file_offset(section["end_exclusive"])
        if start < stock_start or start < cursor or end > stock_end:
            raise AdmissionError("Linux CFF stock section escaped fixed interval")
        retained(cursor, start)
        payload = component[start:end]
        if len(payload) != section["size"] or _digest(payload) != section["sha256"]:
            raise AdmissionError("Linux CFF stock section differs from final component")
        slug = section["name"].removeprefix(".").replace(".", "-")
        rows.append({
            "name": f"freetype_cff_{slug}_linux",
            "function": f"Compiled FreeType 2.9.1 CFF scatter section {section['name']}",
            "file_offset": start,
            "size": end - start,
            "address_status": "source_compiled",
            "output": f"apollo510b/cff-scatter-linux-{slug}.bin",
            "target": "apollo510b_internal_mram",
            "target_address": section["start"],
        })
        cursor = end
    retained(cursor, capture_end)
    if not rows or rows[0]["file_offset"] != capture_start or sum(
        row["size"] for row in rows
    ) != capture_end - capture_start:
        raise AdmissionError("Linux CFF stock replacement does not tile interval")

    pointer_runtime = placement["module_class_pointer"]
    pointer_start = file_offset(pointer_runtime)
    pointer_end = pointer_start + len(CFF_REPLACEMENT_CLASS_BYTES)
    if (
        donor[pointer_start:pointer_end] != CFF_STOCK_CLASS_BYTES
        or component[pointer_start:pointer_end] != CFF_REPLACEMENT_CLASS_BYTES
    ):
        raise AdmissionError("Linux CFF class-pointer region changed")
    pointer_row = {
        "name": "freetype_cff_module_class_pointer_linux",
        "function": "Guarded CFF module-class pointer route",
        "file_offset": pointer_start,
        "size": pointer_end - pointer_start,
        "address_status": "generated_source_data_replacement",
        "output": "apollo510b/cff-scatter-linux-module-class-pointer.bin",
        "target": "apollo510b_internal_mram",
        "target_address": pointer_runtime,
    }
    result = [
        {
            "start": capture_start,
            "end_exclusive": capture_end,
            "regions": rows,
        },
        {
            "start": pointer_start,
            "end_exclusive": pointer_end,
            "regions": [pointer_row],
        },
    ]
    for replacement in result:
        overlaps = [
            row for row in regions
            if row["file_offset"] < replacement["end_exclusive"]
            and row["file_offset"] + row["size"] > replacement["start"]
        ]
        if (
            not overlaps
            or overlaps[0]["file_offset"] != replacement["start"]
            or sum(row["size"] for row in overlaps)
            != replacement["end_exclusive"] - replacement["start"]
        ):
            raise AdmissionError("Apple CFF rows do not admit Linux replacement")
    return result


def _linux_profile_region_replacements(
    regions: list[dict[str, Any]],
    config: dict[str, Any],
    observation: dict[str, Any],
    donor: bytes,
    component: bytes,
) -> list[dict[str, Any]]:
    """Build exact Linux base-region classifications from its receipt bytes."""
    if observation.get("liblc3_service_audio") is not None:
        boundary = int(config["base"]["size"])
        return [{
            "start": 0,
            "end_exclusive": boundary,
            "regions": [
                {
                    "name": "apollo_main_linux_ota_preamble",
                    "function": "Generated 32-byte LLVM-profile staging header",
                    "file_offset": 0,
                    "size": int(config["preamble_bytes"]),
                    "address_status": "container_only",
                    "output": "apollo510b/main-linux-ota-preamble.bin",
                },
                {
                    "name": "apollo_main_linux_canonical_lc3_cff_image",
                    "function": (
                        "Deterministic LLVM-profile Apollo source image with LC3 "
                        "service-audio and FreeType CFF host-scatter routing"
                    ),
                    "file_offset": int(config["preamble_bytes"]),
                    "size": boundary - int(config["preamble_bytes"]),
                    "address_status": "generated_source_data_replacement",
                    "output": "apollo510b/main-linux-canonical-lc3-cff.bin",
                    "target": "apollo510b_internal_mram",
                    "target_address": int(config["run_base"]),
                },
            ],
        }]
    replacements: list[dict[str, Any]] = []
    liblc3 = observation.get("liblc3_ltpf")
    placement = liblc3.get("placement") if isinstance(liblc3, dict) else None
    if not isinstance(placement, dict):
        raise AdmissionError("Linux liblc3 placement receipt is missing")
    payload_size, payload_digest = _pin(
        liblc3, "payload_size", "payload_sha256", "Linux liblc3 payload"
    )
    appended_offset = placement.get("file_offset")
    if (
        not isinstance(appended_offset, int)
        or appended_offset < config["base"]["size"]
        or component[appended_offset:appended_offset + payload_size] == b""
    ):
        raise AdmissionError("Linux liblc3 appended placement is invalid")
    appended = component[appended_offset:appended_offset + payload_size]
    if len(appended) != payload_size or _digest(appended) != payload_digest:
        raise AdmissionError("Linux appended liblc3 bytes differ from receipt")

    for source_name, tail_name in (
        ("liblc3_ltpf_source_text", "liblc3_ltpf_text_cave_tail"),
        ("liblc3_ltpf_source_rodata", "liblc3_ltpf_rodata_cave_tail"),
    ):
        selected = [
            row for row in regions if row.get("name") in (source_name, tail_name)
        ]
        selected.sort(key=lambda row: row.get("file_offset", -1))
        if (
            len(selected) not in (1, 2)
            or selected[0].get("name") != source_name
            or (len(selected) == 2 and selected[1].get("name") != tail_name)
        ):
            raise AdmissionError(f"Linux liblc3 base cave {source_name} is ambiguous")
        start = selected[0]["file_offset"]
        end = selected[-1]["file_offset"] + selected[-1]["size"]
        if (
            len(selected) == 2
            and selected[0]["file_offset"] + selected[0]["size"]
            != selected[1]["file_offset"]
        ):
            raise AdmissionError("Linux liblc3 base cave does not tile its capacity")
        if component[start:end] != donor[start:end]:
            raise AdmissionError("Linux liblc3 base cave differs from donor bytes")
        replacements_rows = copy.deepcopy(selected)
        for replacement in replacements_rows:
            replacement["address_status"] = "official_blob"
            replacement["function"] = (
                "Authenticated donor bytes retained for Linux; the compiled "
                "liblc3 provider is in the appended source tail"
            )
        replacements.append(
            {"start": start, "end_exclusive": end, "regions": replacements_rows}
        )

    linux_pt_regions = _synchronize_pt_interval(
        regions, config, observation, component
    )
    pt_placement = observation["pt_protocol"]["placement"]
    pt_start = _runtime_file_offset(config, pt_placement["runtime_start"])
    pt_end = _runtime_file_offset(config, pt_placement["runtime_end_exclusive"])
    pt_rows = [
        copy.deepcopy(row) for row in linux_pt_regions
        if row["file_offset"] >= pt_start
        and row["file_offset"] + row["size"] <= pt_end
    ]
    if not pt_rows or sum(row["size"] for row in pt_rows) != pt_end - pt_start:
        raise AdmissionError("Linux PT profile replacement does not tile capacity")
    replacements.append(
        {"start": pt_start, "end_exclusive": pt_end, "regions": pt_rows}
    )
    replacements.extend(
        _linux_cff_profile_replacements(
            regions, config, observation, donor, component
        )
    )
    replacements.sort(key=lambda item: item["start"])
    for previous, current in zip(replacements, replacements[1:]):
        if previous["end_exclusive"] > current["start"]:
            raise AdmissionError("Linux profile base replacements overlap")
    return replacements


def _leaf_segments(
    stage: dict[str, Any], boundary: int, component: bytes
) -> list[dict[str, Any]]:
    """Reconstruct and authenticate the compiler-owned appended leaf tail."""
    expected = stage.get("expected")
    overlay_size, overlay_digest = _pin(
        expected, "overlay_size", "overlay_sha256", "core-stage overlay"
    )
    component_size, _component_digest = _pin(
        expected, "component_size", "component_sha256", "core-stage component"
    )
    if component_size != len(component) or overlay_size != len(component) - boundary:
        raise AdmissionError("core-stage appended-tail extent changed")
    if _digest(component[boundary:]) != overlay_digest:
        raise AdmissionError("core-stage appended-tail bytes differ from receipt")

    result: list[dict[str, Any]] = []
    identities: set[str] = set()
    for key, kind in (
        ("isolated_leaves", "isolated"),
        ("relocated_leaves", "relocated"),
    ):
        items = stage.get(key)
        if not isinstance(items, list):
            raise AdmissionError(f"core-stage {key} receipt is missing")
        for item in items:
            placement = item.get("placement")
            extraction = item.get("extraction")
            pins = item.get("pins")
            if (
                not isinstance(placement, dict)
                or not isinstance(extraction, dict)
                or not isinstance(pins, dict)
            ):
                raise AdmissionError("appended leaf placement receipt is missing")
            identity = extraction.get("function")
            if (
                not isinstance(identity, str)
                or re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", identity) is None
            ):
                raise AdmissionError("appended leaf identity is not a safe C symbol")
            if identity in identities:
                raise AdmissionError("appended leaf identity is duplicated")
            identities.add(identity)
            offset = placement.get("offset")
            padding = placement.get("padding_before")
            total = placement.get("size")
            text_size = placement.get("text_size", extraction.get("size"))
            if any(not isinstance(value, int) for value in (offset, padding, total, text_size)):
                raise AdmissionError("appended leaf placement contains a non-integer")
            if offset < padding or total < text_size or text_size <= 0:
                raise AdmissionError("appended leaf placement is invalid")
            text_digest = pins.get("sha256")
            if (
                pins.get("size") != text_size
                or extraction.get("size") != text_size
                or extraction.get("sha256") != text_digest
                or not isinstance(text_digest, str)
                or re.fullmatch(r"[0-9a-f]{64}", text_digest) is None
            ):
                raise AdmissionError("appended leaf text receipt is inconsistent")
            if "offset" in pins and pins["offset"] != offset:
                raise AdmissionError("appended leaf pin/placement offset changed")
            if padding:
                result.append(
                    {
                        "status": "generated_alignment",
                        "file_offset": boundary + offset - padding,
                        "size": padding,
                        "identity": identity,
                        "kind": kind,
                        "part": "alignment_before",
                    }
                )
            result.append(
                {
                    "status": "source_compiled",
                    "file_offset": boundary + offset,
                    "size": text_size,
                    "identity": identity,
                    "kind": kind,
                    "part": "text",
                    "sha256": text_digest,
                }
            )
            if total > text_size:
                rodata_offset = pins.get("rodata_offset")
                if (
                    not isinstance(rodata_offset, int)
                    or rodata_offset < text_size
                    or rodata_offset >= total
                ):
                    raise AdmissionError("closure rodata offset overlaps or escapes text")
                rodata = pins.get("rodata")
                extracted_rodata = extraction.get("rodata")
                rodata_size = total - rodata_offset
                if (
                    pins.get("closure_size") != total
                    or extraction.get("closure_size") != total
                    or not isinstance(rodata, dict)
                    or not isinstance(extracted_rodata, dict)
                    or rodata.get("offset") != rodata_offset
                    or rodata.get("size") != rodata_size
                    or extracted_rodata.get("offset") != rodata_offset
                    or extracted_rodata.get("size") != rodata_size
                    or extracted_rodata.get("sha256") != rodata.get("sha256")
                    or pins.get("closure_sha256") != extraction.get("closure_sha256")
                ):
                    raise AdmissionError("closure rodata receipt is inconsistent")
                rodata_digest = rodata.get("sha256")
                closure_digest = pins.get("closure_sha256")
                if (
                    not isinstance(rodata_digest, str)
                    or re.fullmatch(r"[0-9a-f]{64}", rodata_digest) is None
                    or not isinstance(closure_digest, str)
                    or re.fullmatch(r"[0-9a-f]{64}", closure_digest) is None
                ):
                    raise AdmissionError("closure hash receipt is incomplete")
                internal_padding = rodata_offset - text_size
                if internal_padding:
                    result.append(
                        {
                            "status": "generated_alignment",
                            "file_offset": boundary + offset + text_size,
                            "size": internal_padding,
                            "identity": identity,
                            "kind": kind,
                            "part": "alignment_internal",
                        }
                    )
                result.append(
                    {
                        "status": "source_compiled_rodata",
                        "file_offset": boundary + offset + rodata_offset,
                        "size": rodata_size,
                        "identity": identity,
                        "kind": kind,
                        "part": "rodata",
                        "sha256": rodata_digest,
                    }
                )
                closure = component[
                    boundary + offset:boundary + offset + total
                ]
                if len(closure) != total or _digest(closure) != closure_digest:
                    raise AdmissionError(
                        f"appended closure {identity} differs from artifact bytes"
                    )
            elif any(
                key_name in pins
                for key_name in ("closure_size", "closure_sha256", "rodata_offset", "rodata")
            ):
                raise AdmissionError("text-only leaf carries an ambiguous closure receipt")

    result.sort(key=lambda segment: segment["file_offset"])
    if not result:
        raise AdmissionError("canonical appended leaf receipt is empty")
    cursor = result[0]["file_offset"]
    if cursor < boundary:
        raise AdmissionError("canonical appended leaf starts before its boundary")
    for segment in result:
        start = segment["file_offset"]
        end = start + segment["size"]
        if start != cursor or end > len(component):
            raise AdmissionError("appended leaf placements duplicate, overlap, or contain a gap")
        payload = component[start:end]
        if segment["status"] == "generated_alignment":
            if payload != b"\x00" * segment["size"]:
                raise AdmissionError("appended generated alignment contains source bytes")
        elif _digest(payload) != segment["sha256"]:
            raise AdmissionError(
                f"appended leaf {segment['identity']} differs from artifact bytes"
            )
        cursor = end
    if cursor != len(component):
        raise AdmissionError("appended leaf placements do not reach component end")
    return result


def _legacy_compatible_tail(
    templates: list[dict[str, Any]],
    segments: list[dict[str, Any]],
    config: dict[str, Any],
    *,
    allow_schema_migration: bool = False,
) -> list[dict[str, Any]]:
    """Bind authenticated leaf parts to reviewed public presentation aliases."""
    original_templates = copy.deepcopy(templates)
    retired = [
        template for template in templates
        if template.get("name") in LEGACY_RETIRED_ALIGNMENT_ALIASES
    ]
    retired_names = {template.get("name") for template in retired}
    canonical_replay = bool(LEGACY_RETIRED_ALIGNMENT_ALIASES) and not retired
    if retired and (
        retired_names != LEGACY_RETIRED_ALIGNMENT_ALIASES
        or any(
            template.get("address_status") != "generated_alignment"
            for template in retired
        )
    ):
        raise AdmissionError("retired legacy alignment alias contract changed")
    templates = [
        template for template in templates
        if template.get("name") not in LEGACY_RETIRED_ALIGNMENT_ALIASES
    ]
    by_name: dict[str, dict[str, Any]] = {}
    for template in templates:
        name = template.get("name")
        if not isinstance(name, str) or name in by_name:
            raise AdmissionError("legacy appended-tail aliases are duplicated")
        by_name[name] = template
    by_part: dict[tuple[str, str], dict[str, Any]] = {}
    for segment in segments:
        key = (segment["identity"], segment["part"])
        if key in by_part:
            raise AdmissionError("canonical appended-tail parts are duplicated")
        by_part[key] = segment

    consumed_templates: set[str] = set()
    consumed_parts: set[tuple[str, str]] = set()
    bindings: dict[str, dict[str, Any]] = {}

    def bind_parts(
        alias: str,
        owner_parts: list[tuple[str, str]],
        *,
        require_legacy_size: bool = True,
    ) -> None:
        template = by_name.get(alias)
        if template is None or alias in consumed_templates:
            raise AdmissionError(f"legacy appended-tail alias {alias!r} is missing")
        selected: list[dict[str, Any]] = []
        for key in owner_parts:
            segment = by_part.get(key)
            if segment is None or key in consumed_parts:
                raise AdmissionError(
                    f"legacy alias {alias!r} has no unique canonical owner part"
                )
            selected.append(segment)
        selected.sort(key=lambda item: item["file_offset"])
        cursor = selected[0]["file_offset"]
        start = cursor
        for segment in selected:
            if segment["file_offset"] != cursor:
                raise AdmissionError(
                    f"legacy alias {alias!r} owner parts are not contiguous"
                )
            cursor += segment["size"]
        size = cursor - start
        if require_legacy_size and template.get("size") != size:
            raise AdmissionError(f"legacy alias {alias!r} byte extent changed")
        parts = {segment["part"] for segment in selected}
        if parts <= {"alignment_before", "alignment_internal"}:
            allowed_statuses = {"generated_alignment"}
        elif "text" in parts:
            allowed_statuses = {"source_compiled"}
        elif parts == {"rodata"}:
            # Two historical state-name rows deliberately use the explicit
            # rodata status; other reviewed rodata aliases retain their
            # source_compiled compatibility status.
            allowed_statuses = {"source_compiled", "source_compiled_rodata"}
        else:
            raise AdmissionError(f"legacy alias {alias!r} part status is ambiguous")
        if template.get("address_status") not in allowed_statuses:
            raise AdmissionError(
                f"legacy alias {alias!r} address status is incompatible"
            )
        bindings[alias] = {"file_offset": start, "size": size}
        consumed_templates.add(alias)
        consumed_parts.update(owner_parts)

    for owner, alias in LEGACY_RODATA_ALIASES.items():
        bind_parts(alias, [(owner, "rodata")])
    for owner, alias in LEGACY_SPECIAL_RODATA_ALIASES.items():
        bind_parts(alias, [(owner, "rodata")])
    for owner, alias in LEGACY_COALESCED_CLOSURE_ALIASES.items():
        parts = [(owner, "text")]
        if (owner, "alignment_internal") in by_part:
            parts.append((owner, "alignment_internal"))
        parts.append((owner, "rodata"))
        bind_parts(alias, parts)
    for alias, owners in LEGACY_MULTI_OWNER_ALIASES.items():
        parts: list[tuple[str, str]] = []
        for index, owner in enumerate(owners):
            allowed = {
                part for identity, part in by_part if identity == owner
            }
            expected = {"text"}
            if index and "alignment_before" in allowed:
                expected.add("alignment_before")
            if allowed != expected:
                raise AdmissionError(
                    f"legacy multi-owner alias {alias!r} part vector changed"
                )
            if index and "alignment_before" in allowed:
                parts.append((owner, "alignment_before"))
            parts.append((owner, "text"))
        bind_parts(alias, parts)

    remaining_templates = [
        template for template in templates
        if template["name"] not in consumed_templates
    ]
    remaining_parts = [
        segment for segment in segments
        if (segment["identity"], segment["part"]) not in consumed_parts
    ]
    template_alignments = [
        template for template in remaining_templates
        if template.get("address_status") == "generated_alignment"
    ]
    template_text = [
        template for template in remaining_templates
        if template.get("address_status") != "generated_alignment"
    ]
    part_alignments = [
        segment for segment in remaining_parts
        if segment["status"] == "generated_alignment"
    ]
    part_text = [
        segment for segment in remaining_parts
        if segment["part"] == "text"
    ]
    unexpected = [
        segment for segment in remaining_parts
        if segment not in part_alignments and segment not in part_text
    ]
    vector_changed = (
        unexpected
        or len(template_alignments) != len(part_alignments)
        or len(template_text) != len(part_text)
    )
    if vector_changed and not allow_schema_migration:
        part_offsets = {item["file_offset"] for item in part_text}
        template_offsets = {item["file_offset"] for item in template_text}
        unmatched_templates = [
            (item.get("name"), item.get("file_offset"), item.get("size"))
            for item in template_text if item.get("file_offset") not in part_offsets
        ][:12]
        unmatched_parts = [
            (item.get("identity"), item.get("file_offset"), item.get("size"))
            for item in part_text if item.get("file_offset") not in template_offsets
        ][:12]
        raise AdmissionError(
            "legacy appended-tail aliases do not bijectively cover canonical parts: "
            f"templates(alignment={len(template_alignments)},text={len(template_text)}), "
            f"parts(alignment={len(part_alignments)},text={len(part_text)},"
            f"unexpected={[(item['identity'], item['part']) for item in unexpected]}), "
            f"unmatched_templates={unmatched_templates}, "
            f"unmatched_parts={unmatched_parts}"
        )
    if vector_changed:
        if unexpected:
            raise AdmissionError(
                "canonical tail schema migration contains an unsupported leaf part"
            )

        # A source admission may split an existing compiler closure, add a
        # leaf, or introduce a new alignment interval.  The ordinary path
        # deliberately rejects those cardinality changes.  This explicit
        # migration path is reached only from the four-observation admission
        # command and therefore derives presentation aliases from already
        # authenticated leaf/part receipts.  Exact unchanged aliases are
        # retained; stale generic aliases are retired rather than guessed by
        # ordinal position.
        remaining_by_extent: dict[
            tuple[int, int, str], list[dict[str, Any]]
        ] = {}
        for template in remaining_templates:
            status = template.get("address_status")
            category = (
                "alignment" if status == "generated_alignment" else
                "text" if status == "source_compiled" else
                "rodata" if status == "source_compiled_rodata" else
                ""
            )
            if category:
                remaining_by_extent.setdefault(
                    (template["file_offset"], template["size"], category), []
                ).append(template)

        synthesized: list[dict[str, Any]] = []
        for segment in remaining_parts:
            category = (
                "alignment" if segment["status"] == "generated_alignment" else
                "rodata" if segment["part"] == "rodata" else
                "text"
            )
            candidates = remaining_by_extent.get(
                (segment["file_offset"], segment["size"], category), []
            )
            candidates = [
                item for item in candidates
                if item["name"] not in consumed_templates
            ]
            if len(candidates) > 1:
                raise AdmissionError(
                    "canonical tail schema migration found ambiguous legacy aliases"
                )
            if candidates:
                alias = candidates[0]["name"]
            else:
                identity = segment["identity"]
                part = segment["part"]
                slug = re.sub(r"[^A-Za-z0-9]+", "-", identity).strip("-").lower()
                slug = (slug[:48] or "leaf")
                suffix = _digest(f"{identity}\0{part}".encode())[:10]
                alias = (
                    f"apollo_core_canonical_{slug}_{part}_{suffix}"
                )
                if alias in by_name:
                    raise AdmissionError(
                        "canonical tail schema migration alias collision"
                    )
                offset = segment["file_offset"]
                if category == "alignment":
                    function = f"Generated alignment for {identity} ({part})"
                elif category == "rodata":
                    function = (
                        f"Production source-owned {identity} compiled rodata"
                    )
                else:
                    function = (
                        f"Production source-owned {identity} compiled from maintained C"
                    )
                template = {
                    "name": alias,
                    "function": function,
                    "file_offset": offset,
                    "size": segment["size"],
                    "address_status": segment["status"],
                    "output": (
                        "apollo510b/main-source-canonical-"
                        f"{slug}-{part}-{suffix}.bin"
                    ),
                    "target": "apollo510b_internal_mram",
                    "target_address": (
                        config["run_base"] + offset - config["preamble_bytes"]
                    ),
                }
                by_name[alias] = template
                synthesized.append(template)
            bind_parts(
                alias,
                [(segment["identity"], segment["part"])],
                require_legacy_size=True,
            )
        templates = [
            template for template in templates
            if template["name"] in consumed_templates
        ] + synthesized
        canonical_replay = False
    else:
        for template, segment in zip(template_alignments, part_alignments):
            bind_parts(
                template["name"],
                [(segment["identity"], segment["part"])],
                require_legacy_size=False,
            )
        for template, segment in zip(template_text, part_text):
            bind_parts(
                template["name"],
                [(segment["identity"], segment["part"])],
                require_legacy_size=False,
            )
    if len(bindings) != len(templates) or len(consumed_parts) != len(segments):
        raise AdmissionError("legacy appended-tail alias consumption is incomplete")

    run_base = config["run_base"]
    preamble = config["preamble_bytes"]
    rebuilt: list[dict[str, Any]] = []
    for template in templates:
        binding = bindings[template["name"]]
        updated = copy.deepcopy(template)
        updated["file_offset"] = binding["file_offset"]
        updated["size"] = binding["size"]
        if "target_address" in updated:
            updated["target_address"] = (
                run_base + binding["file_offset"] - preamble
            )
        rebuilt.append(updated)
    rebuilt.sort(key=lambda item: item["file_offset"])
    if canonical_replay:
        # A legacy input must still carry every reviewed retired alias.  Its
        # absence is admissible only for the synchronizer's own canonical
        # fixed point, where replaying every authenticated binding is an exact
        # no-op.  This preserves the legacy tamper check while making a second
        # no-write verification idempotent after publication.
        canonical_input = sorted(
            original_templates, key=lambda item: item.get("file_offset", -1)
        )
        if canonical_input != rebuilt:
            raise AdmissionError("retired legacy alignment alias contract changed")
    return rebuilt


def _transition_regions(regions: list[dict[str, Any]], base: bytes,
                        final: bytes, config: dict[str, Any], *,
                        prefix: str, function: str) -> list[dict[str, Any]]:
    """Split a tiled map around one authenticated same-component transition."""
    _partition(regions, len(base), f"{prefix} input region map")
    if len(final) < len(base):
        raise AdmissionError(f"{prefix} unexpectedly shrank the component")
    virtual = base + b"\xFF" * (len(final) - len(base))
    raw: list[tuple[int, int]] = []
    start: int | None = None
    for index, (before, after) in enumerate(zip(virtual, final)):
        if before != after and start is None:
            start = index
        elif before == after and start is not None:
            raw.append((start, index))
            start = None
    if start is not None:
        raw.append((start, len(final)))
    if len(final) > len(base):
        raw.append((len(base), len(final)))
    raw.sort()
    mutations: list[tuple[int, int]] = []
    for left, right in raw:
        if mutations and left <= mutations[-1][1] + 8:
            mutations[-1] = (mutations[-1][0], max(mutations[-1][1], right))
        else:
            mutations.append((left, right))
    if any(virtual[index] != final[index] and not any(
            left <= index < right for left, right in mutations)
           for index in range(len(final))):
        raise AdmissionError(f"{prefix} mutation coverage is incomplete")

    boundaries = {0, len(final)}
    for row in regions:
        boundaries.add(int(row["file_offset"]))
        boundaries.add(int(row["file_offset"]) + int(row["size"]))
    for left, right in mutations:
        boundaries.add(left)
        boundaries.add(right)
    points = sorted(boundaries)
    result = []
    run_base = int(config["run_base"])
    preamble = int(config["preamble_bytes"])
    mutation_index = 0
    for left, right in zip(points, points[1:]):
        if left >= len(final) or right <= left:
            continue
        changed = next((interval for interval in mutations
                        if interval[0] <= left and right <= interval[1]), None)
        source = next((row for row in regions
                       if int(row["file_offset"]) <= left and
                       right <= int(row["file_offset"]) + int(row["size"])), None)
        if changed is None and source is not None:
            row = copy.deepcopy(source)
            row["file_offset"] = left
            row["size"] = right - left
            if left != int(source["file_offset"]) or right != (
                int(source["file_offset"]) + int(source["size"])
            ):
                row["name"] = f"{source['name']}_split_{left:08x}_{right:08x}"
                row["output"] = f"apollo510b/{prefix}-retained-{left:08x}-{right:08x}.bin"
            if "target_address" in row:
                row["target_address"] = run_base + left - preamble
            result.append(row)
            continue
        if changed is None:
            raise AdmissionError(f"{prefix} left an unmapped appended interval")
        mutation_row = {
            "name": f"{prefix}_{mutation_index:04d}_{left:08x}_{right:08x}",
            "function": function,
            "file_offset": left,
            "size": right - left,
            "address_status": "generated_source_data_replacement",
            "output": f"apollo510b/{prefix}-{mutation_index:04d}-{left:08x}-{right:08x}.bin",
        }
        if right <= preamble:
            mutation_row["address_status"] = "container_only"
        else:
            if left < preamble:
                raise AdmissionError(
                    f"{prefix} mutation crosses the staging preamble")
            mutation_row["target"] = "apollo510b_internal_mram"
            mutation_row["target_address"] = run_base + left - preamble
        result.append(mutation_row)
        mutation_index += 1
    _partition(result, len(final), f"{prefix} output region map")
    return result


def synchronize_apollo_regions(
    regions: list[dict[str, Any]],
    config: dict[str, Any],
    apple_observation: dict[str, Any],
    donor: bytes,
    apple_component: bytes,
    linux_component: bytes,
    apple_core_stage_component: bytes,
    apple_liblc3_component: bytes,
    apple_pt_component: bytes | None = None,
    apple_liblc3_service_component: bytes | None = None,
    *,
    allow_tail_schema_migration: bool = False,
) -> list[dict[str, Any]]:
    """Rebuild the admitted core/PT/liblc3 map, then apply exact CFF scatter."""
    original = copy.deepcopy(regions)
    if not original:
        raise AdmissionError("current Apollo region map is empty")
    current_size = max(
        region.get("file_offset", -1) + region.get("size", -1)
        for region in original
    )
    _partition(original, current_size, "current Apollo region map")
    imu_start, imu_end = _derived_imu_span(config)
    if imu_end > len(donor):
        raise AdmissionError("derived stock IMU donor span exceeds the donor")
    overlapping = [
        (index, region)
        for index, region in enumerate(original)
        if region["file_offset"] < imu_end
        and region["file_offset"] + region["size"] > imu_start
    ]
    if not overlapping:
        raise AdmissionError("stock IMU donor span is absent from the manifest")
    ordered_overlap = [region for _index, region in overlapping]
    cursor = imu_start
    for region in ordered_overlap:
        if region["file_offset"] != cursor:
            raise AdmissionError("manifest does not exactly tile the derived IMU span")
        cursor += region["size"]
    if cursor != imu_end:
        raise AdmissionError("manifest IMU donor span has a wrong offset or size")
    donor_slice = donor[imu_start:imu_end]
    if (
        apple_component[imu_start:imu_end] != donor_slice
        or linux_component[imu_start:imu_end] != donor_slice
    ):
        raise AdmissionError("canonical component changed authenticated donor IMU bytes")
    replacement = {
        "address_status": "official_blob",
        "file_offset": imu_start,
        "function": "Authenticated donor-stock G2 IMU implementation retained unchanged",
        "name": "apollo_main_stock_imu_donor",
        "output": "apollo510b/main-stock-imu-0x004a35b0.bin",
        "size": imu_end - imu_start,
        "target": "apollo510b_internal_mram",
        "target_address": IMU_RUNTIME_START,
    }
    first = overlapping[0][0]
    last = overlapping[-1][0]
    result = original[:first] + [replacement] + original[last + 1 :]
    result = _synchronize_pt_interval(
        result, config, apple_observation, apple_component
    )
    result = _synchronize_liblc3_cave_regions(
        result,
        config,
        apple_observation,
        apple_component,
        apple_core_stage_component,
        apple_liblc3_component,
    )

    boundary = config["base"]["size"]
    tail_indexes = [
        index for index, region in enumerate(result)
        if region["file_offset"] >= boundary
    ]
    if not tail_indexes:
        raise AdmissionError("manifest compiler-owned appended tail is missing")
    tail_start = tail_indexes[0]
    tail = result[tail_start:]
    if tail[0]["file_offset"] != boundary or tail[0].get("name") != "apollo_core_source_overlay":
        raise AdmissionError("manifest appended-tail boundary identity changed")
    observed_segments = _leaf_segments(
        apple_observation["core_stage"], boundary, apple_core_stage_component
    )
    rebuilt_tail: list[dict[str, Any]] = []
    first_leaf_offset = observed_segments[0]["file_offset"]
    primary = copy.deepcopy(tail[0])
    if primary.get("address_status") != "source_compiled":
        raise AdmissionError("manifest appended-tail primary source row changed")
    primary["size"] = first_leaf_offset - boundary
    if primary["size"] <= 0:
        raise AdmissionError("canonical primary source overlay is empty")
    stale = (
        ", and IMU source; pristine TDK ICM45608 1.1.2 transport, FIFO, "
        "eDMP, I2CM, MRM, SIF, and GAF implementation"
    )
    primary["function"] = primary["function"].replace(stale, "")
    rebuilt_tail.append(primary)
    templates = [
        region for region in tail[1:]
        if not str(region.get("name", "")).startswith(FORBIDDEN_APPENDED_PREFIX)
        and not str(region.get("name", "")).startswith("freetype_cff_")
    ]
    rebuilt_tail.extend(
        _legacy_compatible_tail(
            templates,
            observed_segments,
            config,
            allow_schema_migration=allow_tail_schema_migration,
        )
    )
    result = result[:tail_start] + rebuilt_tail
    expected_size = apple_observation["core_stage"]["expected"]["component_size"]
    if expected_size != len(apple_core_stage_component):
        raise AdmissionError(
            "Apple core-stage placement does not match its detailed tail"
        )
    _partition(result, expected_size, "synchronized Apollo region map")
    tail_text = _canonical(result[tail_start:]).decode("utf-8").lower()
    if "pristine tdk" in tail_text or '"name":"imu_icm45608_' in tail_text:
        raise AdmissionError("restricted IMU appended regions remain after synchronization")
    cff = apple_observation.get("freetype_cff")
    if cff is None:
        if len(apple_component) != expected_size:
            raise AdmissionError(
                "legacy Apple post-link placement is not in-place"
            )
        return result
    if not isinstance(cff, dict):
        raise AdmissionError("Apple canonical FreeType CFF receipt is malformed")
    if apple_pt_component is None or len(apple_pt_component) != expected_size:
        raise AdmissionError(
            "Apple pre-CFF providers changed size; detailed CFF base cannot be proven"
        )
    if apple_liblc3_service_component is None:
        raise AdmissionError("Apple LC3 service-audio component is absent")
    result = _transition_regions(
        result, apple_pt_component, apple_liblc3_service_component, config,
        prefix="liblc3_service_audio",
        function=("Compiled LC3 service-audio closure, exact relocation replay, "
                  "runtime providers, guarded veneers, and integrity data"),
    )
    result = _transition_regions(
        result, apple_liblc3_service_component, apple_component, config,
        prefix="freetype_cff_host_scatter",
        function=("Compiled FreeType 2.9.1 CFF host-tail scatter closure and "
                  "guarded module-class routing"),
    )
    _partition(result, len(apple_component), "CFF-integrated Apollo region map")
    return result


def _load_core_builder() -> Any:
    path = G2_ROOT / "components/apollo_main/core_overlay/build_component.py"
    spec = importlib.util.spec_from_file_location("open_cfw_core_builder_admission", path)
    if spec is None or spec.loader is None:
        raise AdmissionError("cannot load the canonical core input enumerator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_cff_builder() -> Any:
    path = (
        G2_ROOT
        / "components/apollo_main/freetype_cff_scatter/build_component.py"
    )
    spec = importlib.util.spec_from_file_location(
        "open_cfw_cff_builder_admission", path
    )
    if spec is None or spec.loader is None:
        raise AdmissionError("cannot load the FreeType CFF region enumerator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _manifest_inheritance_snapshot(
    path: Path, raw: dict[str, Any]
) -> dict[str, Any]:
    """Read every inherited manifest once and retain bytes plus stable identity."""
    manifest_root = path.resolve().parent
    records: list[dict[str, Any]] = []
    active: set[Path] = set()
    leaf_parent_effective: dict[str, Any] | None = None

    def resolve(current_path: Path, current: dict[str, Any]) -> dict[str, Any]:
        nonlocal leaf_parent_effective
        extends = current.get("extends")
        if extends is None:
            return copy.deepcopy(current)
        if not isinstance(extends, str) or not extends:
            raise AdmissionError("manifest extends path is invalid")
        lexical = Path(os.path.abspath(current_path.parent / extends))
        try:
            parent_path = (current_path.parent / extends).resolve(strict=True)
            parent_path.relative_to(manifest_root)
        except (OSError, ValueError, RuntimeError) as error:
            raise AdmissionError("manifest parent escapes the manifests directory") \
                from error
        if lexical != parent_path:
            raise AdmissionError("manifest inheritance path contains a symlink")
        if parent_path in active:
            raise AdmissionError("manifest inheritance cycle detected")
        active.add(parent_path)
        payload, parent, identity = _read_json_with_identity(
            parent_path, "inherited release manifest"
        )
        inherited = resolve(parent_path, parent)
        active.remove(parent_path)
        records.append(
            {"path": parent_path, "payload": payload, "identity": identity}
        )
        if current_path.resolve() == path.resolve():
            leaf_parent_effective = copy.deepcopy(inherited)
        return open_cfw.merge_manifest(inherited, current)

    effective = resolve(path.resolve(), raw)
    if not records:
        raise AdmissionError("core-source manifest must extend its reviewed base")
    if leaf_parent_effective is None:
        raise AdmissionError("core-source manifest parent snapshot is incomplete")
    return {
        "effective": effective,
        "parent_effective": leaf_parent_effective,
        "manifests": records,
    }


def _merged_manifest(
    path: Path,
    raw: dict[str, Any],
    inheritance: dict[str, Any] | None = None,
) -> dict[str, Any]:
    inherited = inheritance or _manifest_inheritance_snapshot(path, raw)
    return open_cfw.merge_manifest(inherited["parent_effective"], raw)


def _non_apollo_provider_snapshot(
    manifest: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    root = PROJECT_ROOT.resolve()
    for component in manifest.get("components", []):
        if not isinstance(component, dict) or component.get("name") == "apollo_main":
            continue
        name = component.get("name")
        provider = component.get("provider")
        relative = provider.get("path") if isinstance(provider, dict) else None
        if not isinstance(name, str) or not isinstance(relative, str):
            raise AdmissionError("non-Apollo provider contract is incomplete")
        if name in result:
            raise AdmissionError("non-Apollo provider component is duplicated")
        path = _contained_regular_path(root, relative, f"{name} provider")
        payload, identity = _read_regular_with_identity(path, f"{name} provider")
        result[name] = {
            "path": path,
            "relative": relative,
            "payload": payload,
            "identity": identity,
        }
    return result


def _dependency_snapshot(
    path: Path, raw: dict[str, Any]
) -> dict[str, Any]:
    inheritance = _manifest_inheritance_snapshot(path, raw)
    return {
        "inheritance": inheritance,
        "providers": _non_apollo_provider_snapshot(inheritance["effective"]),
    }


def _same_dependencies(first: dict[str, Any], second: dict[str, Any]) -> bool:
    def manifests(value: dict[str, Any]) -> list[tuple[str, bytes, Any]]:
        return [
            (str(item["path"]), item["payload"], item["identity"])
            for item in value["inheritance"]["manifests"]
        ]

    def providers(value: dict[str, Any]) -> dict[str, tuple[str, bytes, Any]]:
        return {
            name: (str(item["path"]), item["payload"], item["identity"])
            for name, item in value["providers"].items()
        }

    return manifests(first) == manifests(second) and providers(first) == providers(second)


def load_profile_provider_inputs(
    specifications: list[tuple[str, str, Path]],
) -> dict[tuple[str, str], dict[str, Any]]:
    """Read explicit auxiliary profile providers below the G2 project root."""
    result: dict[tuple[str, str], dict[str, Any]] = {}
    root = PROJECT_ROOT.resolve()
    for profile, component, supplied_path in specifications:
        if profile not in (APPLE_PROFILE, LINUX_PROFILE):
            raise AdmissionError(f"unknown auxiliary provider profile {profile!r}")
        if (
            not isinstance(component, str)
            or re.fullmatch(r"[a-z][a-z0-9_]*", component) is None
            or component == "apollo_main"
        ):
            raise AdmissionError("auxiliary provider component name is invalid")
        key = (profile, component)
        if key in result:
            raise AdmissionError("auxiliary profile provider is duplicated")
        candidate = supplied_path if supplied_path.is_absolute() else root / supplied_path
        try:
            resolved = candidate.resolve(strict=True)
            resolved.relative_to(root)
        except (OSError, ValueError, RuntimeError) as error:
            raise AdmissionError(
                f"auxiliary {profile}/{component} provider escapes the G2 root"
            ) from error
        lexical = Path(os.path.abspath(candidate))
        if candidate.is_symlink() or lexical != resolved:
            raise AdmissionError(
                f"auxiliary {profile}/{component} provider path contains a symlink"
            )
        payload, identity = _read_regular_with_identity(
            candidate, f"auxiliary {profile}/{component} provider"
        )
        result[key] = {"path": resolved, "payload": payload, "identity": identity}
    return result


def _selected_provider_pin(
    component: dict[str, Any], profile: str
) -> tuple[int, str]:
    provider = component.get("provider")
    if not isinstance(provider, dict):
        raise AdmissionError(f"{component.get('name')}: provider contract is missing")
    selected = open_cfw.profile_pins(provider, profile)
    if (
        profile != open_cfw.DEFAULT_TOOLCHAIN_PROFILE
        and provider.get("kind") == "source_build"
        and selected is None
    ):
        raise AdmissionError(
            f"{component.get('name')}: profile {profile!r} pins are mandatory"
        )
    return _pin(
        selected if selected is not None else provider,
        "size",
        "sha256",
        f"{component.get('name')} provider for {profile}",
    )


def select_profile_payloads(
    manifest: dict[str, Any],
    profile: str,
    admitted_apollo: bytes,
    auxiliary: dict[tuple[str, str], dict[str, Any]],
    consumed: set[tuple[str, str]],
    live_providers: dict[str, dict[str, Any]] | None = None,
) -> dict[str, bytes]:
    """Select exact provider bytes, demanding explicit profile substitutions."""
    payloads: dict[str, bytes] = {}
    project_root = PROJECT_ROOT.resolve()
    component_names = {
        component.get("name") for component in manifest.get("components", [])
        if isinstance(component, dict)
    }
    unknown = sorted(
        component for auxiliary_profile, component in auxiliary
        if auxiliary_profile == profile and component not in component_names
    )
    if unknown:
        raise AdmissionError(
            f"auxiliary provider {profile}/{unknown[0]} names no manifest component"
        )
    for component in manifest["components"]:
        name = component.get("name")
        if not isinstance(name, str):
            raise AdmissionError("manifest component name is invalid")
        expected_size, expected_digest = _selected_provider_pin(component, profile)
        key = (profile, name)
        if name == "apollo_main":
            if key in auxiliary:
                raise AdmissionError("Apollo provider must come from admitted observations")
            payload = admitted_apollo
        else:
            provider = component.get("provider", {})
            provider_path = provider.get("path")
            if not isinstance(provider_path, str):
                raise AdmissionError(f"{name}: provider path is missing")
            if live_providers is not None:
                record = live_providers.get(name)
                if (
                    not isinstance(record, dict)
                    or record.get("relative") != provider_path
                    or not isinstance(record.get("payload"), bytes)
                ):
                    raise AdmissionError(f"{name}: provider dependency snapshot changed")
                live = record["payload"]
                live_error = None
            else:
                try:
                    live = open_cfw._read_regular_file_below(  # noqa: SLF001
                        project_root, provider_path, f"{name} provider"
                    )
                except open_cfw.OpenCFWError as error:
                    live = None
                    live_error = error
                else:
                    live_error = None
            if (
                live is not None
                and len(live) == expected_size
                and _digest(live) == expected_digest
            ):
                payload = live
            else:
                supplied = auxiliary.get(key)
                if supplied is None:
                    detail = str(live_error) if live_error is not None else (
                        "live provider does not match the active profile pin"
                    )
                    raise AdmissionError(
                        f"{profile}/{name}: explicit auxiliary provider required: {detail}"
                    )
                payload = supplied["payload"]
                consumed.add(key)
        if len(payload) != expected_size or _digest(payload) != expected_digest:
            raise AdmissionError(
                f"{profile}/{name}: selected provider differs from active manifest pins"
            )
        open_cfw.validate_component_payload(component, payload)
        open_cfw.validate_region_partition(component, payload, profile)
        payloads[name] = payload
    return payloads


def _preserve_source_appended_boundary(
    override: dict[str, Any], config: dict[str, Any]
) -> None:
    boundary = config.get("base", {}).get("size")
    if not isinstance(boundary, int) or boundary <= 0:
        raise AdmissionError("authenticated donor size is missing")
    if override.get("source_appended_boundary") != boundary:
        raise AdmissionError(
            "Apollo source_appended_boundary differs from authenticated donor size"
        )
    override["source_appended_boundary"] = boundary


def _assemble_validated_package(
    manifest: dict[str, Any], profile: str, payloads: dict[str, bytes]
) -> bytes:
    open_cfw.validate_release_manifest(
        manifest, toolchain_profile=profile, payloads=payloads
    )
    effective = copy.deepcopy(manifest)
    for component in effective["components"]:
        component["regions"] = open_cfw.effective_component_regions(
            component, len(payloads[component["name"]]), profile
        )
        component.pop("profile_region_replacements", None)
    open_cfw.validate_flash_layout(effective)
    package, _entries = open_cfw.assemble_evenota(manifest, payloads)
    return package


def _apollo_provider_path(raw: dict[str, Any]) -> Path:
    override = raw.get("component_overrides", {}).get("apollo_main")
    provider = override.get("provider") if isinstance(override, dict) else None
    relative = provider.get("path") if isinstance(provider, dict) else None
    if not isinstance(relative, str) or not relative:
        raise AdmissionError("Apollo source provider path is missing")
    return _contained_regular_path(
        PROJECT_ROOT.resolve(), relative, "live Apollo provider"
    )


def _contained_regular_path(root: Path, relative: str, role: str) -> Path:
    root = root.resolve()
    try:
        resolved = open_cfw.resolve_below(root, relative)
    except open_cfw.OpenCFWError as error:
        raise AdmissionError(str(error)) from error
    lexical = Path(os.path.abspath(root / relative))
    if lexical != resolved:
        raise AdmissionError(f"{role} path contains a symlink")
    _read_regular(resolved, role)
    return resolved


def synchronize_manifest(
    raw: dict[str, Any],
    manifest_path: Path,
    config: dict[str, Any],
    apple: dict[str, Any],
    linux: dict[str, Any],
    auxiliary: dict[tuple[str, str], dict[str, Any]],
    dependencies: dict[str, Any] | None = None,
    *,
    allow_tail_schema_migration: bool = False,
) -> dict[str, Any]:
    if dependencies is None:
        dependencies = _dependency_snapshot(manifest_path, raw)
    updated = copy.deepcopy(raw)
    override = updated.get("component_overrides", {}).get("apollo_main")
    if not isinstance(override, dict):
        raise AdmissionError("core-source manifest lacks Apollo override")
    provider = override.get("provider")
    if not isinstance(provider, dict) or provider.get("kind") != "source_build":
        raise AdmissionError("Apollo source provider contract changed")
    _preserve_source_appended_boundary(override, config)
    tail_schema_version = override.get("canonical_tail_schema_version")
    if tail_schema_version not in (None, 2):
        raise AdmissionError("Apollo canonical tail schema version changed")
    migrate_tail = allow_tail_schema_migration or tail_schema_version == 2
    if allow_tail_schema_migration:
        override["canonical_tail_schema_version"] = 2
    # The live provider may still carry the prior admitted generation.  The
    # authenticated observation bytes drive all validation and are published
    # transactionally with config and manifest only when --apply is selected.
    _apollo_provider_path(updated)
    donor_path = PROJECT_ROOT / config["base"]["path"]
    donor = _read_regular(donor_path.resolve(), "authenticated Apollo donor")
    if len(donor) != config["base"]["size"] or _digest(donor) != config["base"]["sha256"]:
        raise AdmissionError("authenticated Apollo donor differs from core pins")
    override["regions"] = synchronize_apollo_regions(
        override["regions"],
        config,
        apple["observation"],
        donor,
        apple["artifacts"]["component"],
        linux["artifacts"]["component"],
        apple["intermediate_artifacts"]["core_stage_component"],
        apple["intermediate_artifacts"]["liblc3_component"],
        apple["intermediate_artifacts"].get("pt_component", b""),
        apple["intermediate_artifacts"].get(
            "liblc3_service_component", b""
        ),
        allow_tail_schema_migration=migrate_tail,
    )
    region_profiles = override.setdefault("profile_region_replacements", {})
    if not isinstance(region_profiles, dict):
        raise AdmissionError("Apollo profile_region_replacements contract changed")
    region_profiles[LINUX_PROFILE] = _linux_profile_region_replacements(
        override["regions"],
        config,
        linux["observation"],
        donor,
        linux["artifacts"]["component"],
    )
    provider["size"] = len(apple["artifacts"]["component"])
    provider["sha256"] = _digest(apple["artifacts"]["component"])
    profiles = provider.get("profiles")
    if not isinstance(profiles, dict) or not isinstance(profiles.get(LINUX_PROFILE), dict):
        raise AdmissionError("Apollo Linux provider profile is missing")
    linux_profile = profiles[LINUX_PROFILE]
    linux_provider_path = linux_profile.get("path")
    if linux_provider_path is not None:
        if not isinstance(linux_provider_path, str) or not linux_provider_path:
            raise AdmissionError("Apollo Linux provider path is invalid")
        linux_provider = _contained_regular_path(
            PROJECT_ROOT.resolve(), linux_provider_path,
            "live Linux Apollo provider",
        )
        linux_provider_payload = _read_regular(
            linux_provider, "live Linux Apollo provider"
        )
        if linux_provider_payload != linux["artifacts"]["component"]:
            raise AdmissionError(
                "live Linux Apollo provider differs from admitted observations"
            )
    profiles[LINUX_PROFILE] = {
        "size": len(linux["artifacts"]["component"]),
        "sha256": _digest(linux["artifacts"]["component"]),
    }
    if linux_provider_path is not None:
        profiles[LINUX_PROFILE]["path"] = linux_provider_path

    # Package pins are derived from the exact selected provider bytes; no
    # package bytes are written by this synchronizer.
    consumed: set[tuple[str, str]] = set()
    for profile, admitted in (
        (APPLE_PROFILE, apple),
        (LINUX_PROFILE, linux),
    ):
        _validate_pt_contract(
            config, profile, admitted["observation"],
            admitted["artifacts"]["component"],
            admitted["intermediate_artifacts"]["core_stage_component"],
            admitted["intermediate_artifacts"]["liblc3_component"],
            admitted["intermediate_artifacts"].get("pt_component"),
        )
        merged = _merged_manifest(
            manifest_path, updated, dependencies["inheritance"]
        )
        payloads = select_profile_payloads(
            merged,
            profile,
            admitted["artifacts"]["component"],
            auxiliary,
            consumed,
            dependencies["providers"],
        )
        if payloads["apollo_main"] != admitted["artifacts"]["component"]:
            raise AdmissionError(f"{profile} manifest selected a stale Apollo provider")
        package = _assemble_validated_package(merged, profile, payloads)
        pin = {"expected_size": len(package), "expected_sha256": _digest(package)}
        if profile == APPLE_PROFILE:
            updated["package"].update(pin)
        else:
            package_profiles = updated["package"].setdefault("profiles", {})
            if not isinstance(package_profiles.get(profile), dict):
                raise AdmissionError(f"package profile {profile!r} is missing")
            package_profiles[profile].update(pin)
    unused = set(auxiliary) - consumed
    if unused:
        profile, component = sorted(unused)[0]
        raise AdmissionError(
            f"auxiliary provider {profile}/{component} was not required or recognized"
        )
    return updated


def _require_publication_parent(
    parent: Path, descriptor: int, expected: tuple[int, int]
) -> None:
    """Bind one held publication directory to its current lexical name."""
    try:
        opened = os.fstat(descriptor)
        named = os.stat(parent, follow_symlinks=False)
    except OSError as error:
        raise AdmissionError("canonical publication parent changed") from error
    if (
        not stat.S_ISDIR(opened.st_mode)
        or not stat.S_ISDIR(named.st_mode)
        or (opened.st_dev, opened.st_ino) != expected
        or (named.st_dev, named.st_ino) != expected
    ):
        raise AdmissionError("canonical publication parent changed")


def _read_publication_file(
    directory_fd: int, name: str, role: str
) -> tuple[bytes, tuple[int, int, int, int, int]]:
    """Read one target through its held parent without following a link."""
    if not name or Path(name).name != name or name in (".", ".."):
        raise AdmissionError(f"{role} path is unsafe")
    descriptor: int | None = None
    try:
        named = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
        if not stat.S_ISREG(named.st_mode) or named.st_nlink != 1:
            raise AdmissionError(f"{role} is not a regular single-link file")
        descriptor = os.open(
            name,
            os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=directory_fd,
        )
        before = os.fstat(descriptor)
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_nlink != 1
            or (before.st_dev, before.st_ino) != (named.st_dev, named.st_ino)
        ):
            raise AdmissionError(f"{role} identity changed")
        chunks = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(descriptor)
        before_identity = (
            before.st_dev, before.st_ino, before.st_size,
            before.st_mtime_ns, before.st_ctime_ns,
        )
        after_identity = (
            after.st_dev, after.st_ino, after.st_size,
            after.st_mtime_ns, after.st_ctime_ns,
        )
        payload = b"".join(chunks)
        if (
            before_identity != after_identity
            or after.st_nlink != 1
            or len(payload) != after.st_size
        ):
            raise AdmissionError(f"{role} changed while reading")
        return payload, after_identity
    except OSError as error:
        raise AdmissionError(f"cannot read {role}: {error}") from error
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _atomic_write_publication(
    parent: Path,
    directory_fd: int,
    parent_identity: tuple[int, int],
    name: str,
    expected_payload: bytes,
    expected_identity: tuple[int, int, int, int, int],
    payload: bytes,
    *,
    validate_named_parent: bool = True,
) -> tuple[int, int, int, int, int]:
    """Conditionally replace one target relative to its held parent inode."""
    temporary = f".{name}.{secrets.token_hex(16)}"
    descriptor: int | None = None
    created = False
    try:
        if validate_named_parent:
            _require_publication_parent(parent, directory_fd, parent_identity)
        current, current_identity = _read_publication_file(
            directory_fd, name, "canonical publication input"
        )
        if current != expected_payload or current_identity != expected_identity:
            raise AdmissionError("canonical publication input changed")
        mode_descriptor = os.open(
            name,
            os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=directory_fd,
        )
        try:
            mode_state = os.fstat(mode_descriptor)
            if (
                not stat.S_ISREG(mode_state.st_mode)
                or mode_state.st_nlink != 1
                or (mode_state.st_dev, mode_state.st_ino)
                != expected_identity[:2]
            ):
                raise AdmissionError("canonical publication input changed")
            mode = stat.S_IMODE(mode_state.st_mode)
        finally:
            os.close(mode_descriptor)
        descriptor = os.open(
            temporary,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL
            | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
            0o600,
            dir_fd=directory_fd,
        )
        created = True
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise AdmissionError("canonical publication write made no progress")
            view = view[written:]
        os.fchmod(descriptor, mode)
        os.fsync(descriptor)
        os.close(descriptor)
        descriptor = None
        current, current_identity = _read_publication_file(
            directory_fd, name, "canonical publication input"
        )
        if current != expected_payload or current_identity != expected_identity:
            raise AdmissionError("canonical publication input changed")
        if validate_named_parent:
            _require_publication_parent(parent, directory_fd, parent_identity)
        os.replace(
            temporary, name,
            src_dir_fd=directory_fd, dst_dir_fd=directory_fd,
        )
        created = False
        os.fsync(directory_fd)
        written, identity = _read_publication_file(
            directory_fd, name, "canonical publication output"
        )
        if written != payload:
            raise AdmissionError("canonical publication readback changed")
        if validate_named_parent:
            _require_publication_parent(parent, directory_fd, parent_identity)
        return identity
    except OSError as error:
        raise AdmissionError(f"canonical publication write failed: {error}") from error
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if created:
            try:
                os.unlink(temporary, dir_fd=directory_fd)
            except FileNotFoundError:
                pass


def _canonical_live_report(
    admitted: dict[str, Any],
    overlay_path: Path,
    provider_path: Path,
) -> bytes:
    """Normalize an admitted Apple observation into a live build commit marker."""
    report = copy.deepcopy(admitted.get("report"))
    if not isinstance(report, dict):
        raise AdmissionError("canonical Apple build report is missing")
    report.pop("canonical_observation", None)
    overlay = report.get("overlay")
    component = report.get("component")
    if not isinstance(overlay, dict) or not isinstance(component, dict):
        raise AdmissionError("canonical Apple build report artifacts are missing")
    try:
        overlay_relative = overlay_path.relative_to(PROJECT_ROOT.resolve())
        provider_relative = provider_path.relative_to(PROJECT_ROOT.resolve())
    except ValueError as error:
        raise AdmissionError("canonical live build report escapes the G2 tree") \
            from error
    overlay_payload = admitted.get("artifacts", {}).get("overlay")
    provider_payload = admitted.get("artifacts", {}).get("component")
    if (
        not isinstance(overlay_payload, bytes)
        or not isinstance(provider_payload, bytes)
    ):
        raise AdmissionError("canonical Apple build artifacts are missing")
    expected = (
        (overlay, overlay_relative.as_posix(), overlay_payload),
        (component, provider_relative.as_posix(), provider_payload),
    )
    for record, artifact, payload in expected:
        if (
            record.get("size") != len(payload)
            or record.get("sha256") != _digest(payload)
        ):
            raise AdmissionError("canonical Apple build report identity changed")
        record["artifact"] = artifact
    return (json.dumps(report, indent=2, sort_keys=True) + "\n").encode()


def _atomic_generation(
    config_path: Path,
    config: dict[str, Any],
    manifest_path: Path,
    manifest: dict[str, Any],
    provider_path: Path,
    provider_payload: bytes,
    *,
    expected_config_payload: bytes | None = None,
    expected_manifest_payload: bytes | None = None,
    expected_provider_payload: bytes | None = None,
    overlay_path: Path | None = None,
    overlay_payload: bytes | None = None,
    expected_overlay_payload: bytes | None = None,
    report_path: Path | None = None,
    report_payload: bytes | None = None,
    expected_report_payload: bytes | None = None,
) -> None:
    optional_values = (
        overlay_path, overlay_payload, expected_overlay_payload,
        report_path, report_payload, expected_report_payload,
    )
    if any(value is not None for value in optional_values) and any(
        value is None for value in optional_values
    ):
        raise AdmissionError(
            "canonical overlay/report publication contract is incomplete"
        )
    generation_paths = (
        (overlay_path, report_path)
        if overlay_path is not None and report_path is not None else ()
    )
    requested_paths = (
        config_path, manifest_path, provider_path, *generation_paths
    )
    if any(
        not _is_normalized_absolute_path(str(path))
        for path in requested_paths
    ):
        raise AdmissionError(
            "canonical publication targets must be absolute and normalized"
        )
    normalized_paths = tuple(Path(path) for path in requested_paths)
    if len(set(normalized_paths)) != len(normalized_paths):
        raise AdmissionError("canonical publication paths must be distinct")
    publication_root = PROJECT_ROOT.resolve()
    try:
        for path in normalized_paths:
            relative = path.relative_to(publication_root)
            parent_relative = path.parent.relative_to(publication_root)
            if (
                relative == Path(".")
                or parent_relative == Path(".")
                or not relative.parts
                or not parent_relative.parts
            ):
                raise ValueError
    except ValueError as error:
        raise AdmissionError(
            "canonical publication target is not strictly below the G2 tree"
        ) from error
    for path in normalized_paths:
        try:
            resolved_target = path.resolve(strict=True)
        except (OSError, RuntimeError) as error:
            raise AdmissionError("canonical publication target is unsafe") from error
        if resolved_target != path:
            raise AdmissionError("canonical publication target contains a symlink")
        try:
            resolved_target.relative_to(publication_root)
        except ValueError as error:
            raise AdmissionError(
                "canonical publication target resolves outside the G2 tree"
            ) from error
    config_path, manifest_path, provider_path = normalized_paths[:3]
    if generation_paths:
        overlay_path, report_path = normalized_paths[3:]
    config_payload = (json.dumps(config, indent=2) + "\n").encode()
    manifest_payload = (json.dumps(manifest, indent=2) + "\n").encode()
    parent_descriptors: dict[Path, tuple[int, tuple[int, int]]] = {}
    try:
        for parent in dict.fromkeys(path.parent for path in normalized_paths):
            try:
                resolved = parent.resolve(strict=True)
            except (OSError, RuntimeError) as error:
                raise AdmissionError("canonical publication parent is unsafe") from error
            if parent != resolved:
                raise AdmissionError("canonical publication parent contains a symlink")
            try:
                descriptor = os.open(
                    parent,
                    os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                    | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
                )
            except OSError as error:
                raise AdmissionError("canonical publication parent is unsafe") from error
            try:
                opened = os.fstat(descriptor)
                identity = (opened.st_dev, opened.st_ino)
                parent_descriptors[parent] = (descriptor, identity)
                _require_publication_parent(parent, descriptor, identity)
            except Exception:
                if parent not in parent_descriptors:
                    os.close(descriptor)
                raise

        targets = {
            path: (*parent_descriptors[path.parent], path.name)
            for path in normalized_paths
        }
        roles = [
            (config_path, "current core config"),
            (manifest_path, "current core manifest"),
            (provider_path, "live Apollo provider"),
        ]
        if generation_paths:
            roles.extend((
                (overlay_path, "live Apollo overlay"),
                (report_path, "live Apollo build report"),
            ))
        previous_with_identity = {
            path: _read_publication_file(
                targets[path][0], targets[path][2], role
            )
            for path, role in roles
        }
        previous = {
            path: payload for path, (payload, _identity) in previous_with_identity.items()
        }
        if (
            expected_config_payload is not None
            and previous[config_path] != expected_config_payload
        ) or (
            expected_manifest_payload is not None
            and previous[manifest_path] != expected_manifest_payload
        ) or (
            expected_provider_payload is not None
            and previous[provider_path] != expected_provider_payload
        ) or (
            expected_overlay_payload is not None
            and previous[overlay_path] != expected_overlay_payload
        ) or (
            expected_report_payload is not None
            and previous[report_path] != expected_report_payload
        ):
            raise AdmissionError("canonical publication inputs changed during admission")
        # Manifest is the public commit marker.  Publishing the complete live
        # component generation before config and manifest leaves every
        # process-death prefix fail-closed against an old report or pin set.
        replacements = [(provider_path, provider_payload)]
        if generation_paths:
            replacements.extend((
                (overlay_path, overlay_payload),
                (report_path, report_payload),
            ))
        replacements.extend((
            (config_path, config_payload),
            (manifest_path, manifest_payload),
        ))
        attempted: list[tuple[Path, bytes]] = []
        try:
            for path, payload in replacements:
                attempted.append((path, payload))
                descriptor, parent_identity, name = targets[path]
                _atomic_write_publication(
                    path.parent, descriptor, parent_identity, name,
                    previous[path], previous_with_identity[path][1], payload,
                )
            for parent, (descriptor, identity) in parent_descriptors.items():
                _require_publication_parent(parent, descriptor, identity)
            if any(
                _read_publication_file(
                    targets[path][0], targets[path][2],
                    "canonical publication output",
                )[0] != payload
                for path, payload in replacements
            ):
                raise AdmissionError("canonical publication readback changed")
        except Exception:
            conflicts: list[Path] = []
            try:
                for path, published_payload in reversed(attempted):
                    descriptor, parent_identity, name = targets[path]
                    current, current_identity = _read_publication_file(
                        descriptor, name, "canonical rollback candidate"
                    )
                    if current == previous[path]:
                        continue
                    if current != published_payload:
                        conflicts.append(path)
                        continue
                    _atomic_write_publication(
                        path.parent, descriptor, parent_identity, name,
                        current, current_identity, previous[path],
                        validate_named_parent=False,
                    )
                if any(
                    _read_publication_file(
                        targets[path][0], targets[path][2],
                        "canonical rollback output",
                    )[0] != payload
                    for path, payload in previous.items()
                    if path not in conflicts
                ):
                    raise AdmissionError("canonical publication rollback failed")
                if conflicts:
                    raise AdmissionError(
                        "conditional rollback refused to overwrite a concurrent edit: "
                        + ", ".join(str(path) for path in conflicts)
                    )
            except AdmissionError as rollback_error:
                if "conditional rollback refused" in str(rollback_error):
                    raise
                raise AdmissionError("canonical publication rollback failed") \
                    from rollback_error
            except Exception as rollback_error:
                raise AdmissionError("canonical publication rollback failed") \
                    from rollback_error
            raise
    finally:
        for descriptor, _identity in parent_descriptors.values():
            os.close(descriptor)


def _current_input_state(
    builder: Any,
    config_path: Path,
    expected_config_payload: bytes | None = None,
) -> tuple[bytes, dict[str, Any], dict[str, tuple[int, str]]]:
    """Snapshot inputs from the current parsed config, rejecting config races."""
    try:
        payload, config, snapshot = builder._canonical_input_state(  # noqa: SLF001
            PROJECT_ROOT, config_path
        )
    except (BuildError, OSError) as error:
        raise AdmissionError("canonical inputs changed during admission") from error
    if expected_config_payload is not None and payload != expected_config_payload:
        raise AdmissionError("canonical core config changed during admission")
    return payload, config, snapshot


def _run_locked(
    args: argparse.Namespace,
    apple: dict[str, Any],
    linux: dict[str, Any],
    lock_validator: Any,
) -> dict[str, Any]:
    auxiliary_specs = list(getattr(args, "profile_provider", []) or [])
    auxiliary = load_profile_provider_inputs(auxiliary_specs)
    config_payload, parsed_config = _read_json(args.config, "canonical core config")
    builder = _load_core_builder()
    _stable_payload, config, snapshot = _current_input_state(
        builder, args.config.resolve(), config_payload
    )
    if config != parsed_config:
        raise AdmissionError("canonical core config changed during admission")
    configured_mapping = {
        "base_size": config.get("base", {}).get("size"),
        "run_base": config.get("run_base"),
        "preamble_bytes": config.get("preamble_bytes"),
    }
    if any(
        admitted["observation"].get("image_mapping") != configured_mapping
        for admitted in (apple, linux)
    ):
        raise AdmissionError("canonical image mapping differs from reviewed config")
    validate_current_inputs(apple["observation"]["source_inputs"], snapshot)
    updated_config = copy.deepcopy(config)
    update_profile_pins(updated_config, APPLE_PROFILE, apple["observation"])
    update_profile_pins(updated_config, LINUX_PROFILE, linux["observation"])
    manifest_payload, raw_manifest = _read_json(args.manifest, "core-source manifest")
    dependencies = _dependency_snapshot(args.manifest.resolve(), raw_manifest)
    provider_path = _apollo_provider_path(raw_manifest)
    provider_payload = _read_regular(provider_path, "live Apollo provider")
    overlay_path = provider_path.with_name("apollo_core_overlay.bin")
    report_path = provider_path.with_name("build-report.json")
    overlay_payload = _read_regular(overlay_path, "live Apollo overlay")
    report_payload = _read_regular(report_path, "live Apollo build report")
    published_report_payload = _canonical_live_report(
        apple, overlay_path, provider_path
    )
    updated_manifest = synchronize_manifest(
        raw_manifest,
        args.manifest.resolve(),
        updated_config,
        apple,
        linux,
        auxiliary,
        dependencies,
        allow_tail_schema_migration=bool(
            getattr(args, "allow_tail_schema_migration", False)
        ),
    )
    if args.apply:
        # Repeat every mutable external-input proof immediately before the
        # atomic writes.  A concurrent source/provider edit cannot inherit a
        # package or profile pin calculated from an earlier generation.
        _current_payload, current_config, current_snapshot = _current_input_state(
            builder, args.config.resolve(), config_payload
        )
        if current_config != config:
            raise AdmissionError("canonical core config changed during admission")
        validate_current_inputs(
            apple["observation"]["source_inputs"], current_snapshot
        )
        if _read_regular(provider_path, "live Apollo provider") != provider_payload:
            raise AdmissionError("live Apollo provider changed during admission")
        if _read_regular(overlay_path, "live Apollo overlay") != overlay_payload:
            raise AdmissionError("live Apollo overlay changed during admission")
        if _read_regular(report_path, "live Apollo build report") != report_payload:
            raise AdmissionError("live Apollo build report changed during admission")
        current_manifest_payload, current_raw_manifest = _read_json(
            args.manifest, "core-source manifest"
        )
        if (
            current_manifest_payload != manifest_payload
            or current_raw_manifest != raw_manifest
        ):
            raise AdmissionError("canonical core manifest changed during admission")
        repeated_dependencies = _dependency_snapshot(
            args.manifest.resolve(), current_raw_manifest
        )
        if not _same_dependencies(dependencies, repeated_dependencies):
            raise AdmissionError(
                "inherited manifest or non-Apollo provider changed during admission"
            )
        repeated_auxiliary = load_profile_provider_inputs(auxiliary_specs)
        if repeated_auxiliary != auxiliary:
            raise AdmissionError("auxiliary provider changed during admission")
        repeated_manifest = synchronize_manifest(
            current_raw_manifest,
            args.manifest.resolve(),
            updated_config,
            apple,
            linux,
            repeated_auxiliary,
            repeated_dependencies,
            allow_tail_schema_migration=bool(
                getattr(args, "allow_tail_schema_migration", False)
            ),
        )
        if repeated_manifest != updated_manifest:
            raise AdmissionError("canonical providers changed during admission")
        # Reject a renamed/replaced lock domain immediately before the first
        # publication write, rather than only after the transaction body.
        lock_validator()
        _atomic_generation(
            args.config.resolve(),
            updated_config,
            args.manifest.resolve(),
            updated_manifest,
            provider_path,
            apple["artifacts"]["component"],
            expected_config_payload=config_payload,
            expected_manifest_payload=manifest_payload,
            expected_provider_payload=provider_payload,
            overlay_path=overlay_path,
            overlay_payload=apple["artifacts"]["overlay"],
            expected_overlay_payload=overlay_payload,
            report_path=report_path,
            report_payload=published_report_payload,
            expected_report_payload=report_payload,
        )
    return {
        "mode": "applied" if args.apply else "verified",
        "source_inputs_sha256": apple["observation"]["source_inputs"]["sha256"],
        "profiles": {
            APPLE_PROFILE: apple["observation"]["final"],
            LINUX_PROFILE: linux["observation"]["final"],
        },
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    apple_pair = admit_reproducible_pair(args.apple_observation, APPLE_PROFILE)
    linux_pair = admit_reproducible_pair(args.linux_observation, LINUX_PROFILE)
    validate_observation_independence((*apple_pair, *linux_pair))
    apple = apple_pair[0]
    linux = linux_pair[0]
    validate_generation(apple, linux)
    with _admission_lock() as lock_validator:
        return _run_locked(args, apple, linux, lock_validator)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apple-observation", type=Path, nargs=2, required=True,
        metavar=("RUN1", "RUN2"),
    )
    parser.add_argument(
        "--linux-observation", type=Path, nargs=2, required=True,
        metavar=("RUN1", "RUN2"),
    )
    parser.add_argument("--config", type=Path, default=CORE_CONFIG)
    parser.add_argument("--manifest", type=Path, default=CORE_MANIFEST)
    parser.add_argument(
        "--profile-provider",
        nargs=3,
        action="append",
        default=[],
        metavar=("PROFILE", "COMPONENT", "PATH"),
        type=str,
        help=(
            "explicit authenticated non-Apollo provider for one toolchain "
            "profile; PATH must remain below the G2 root"
        ),
    )
    parser.add_argument("--apply", action="store_true")
    parser.add_argument(
        "--allow-tail-schema-migration",
        action="store_true",
        help=(
            "explicitly permit authenticated four-observation migration when "
            "the compiler-owned leaf/part vector changed"
        ),
    )
    args = parser.parse_args(argv)
    args.profile_provider = [
        (profile, component, Path(path))
        for profile, component, path in args.profile_provider
    ]
    result = run(args)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AdmissionError, BuildError, open_cfw.OpenCFWError, OSError, KeyError) as error:
        print(f"G2 canonical observation admission: error: {error}", file=sys.stderr)
        raise SystemExit(1)
