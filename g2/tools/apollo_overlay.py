#!/usr/bin/env python3
"""Compile, mini-link, and inject a source-owned Apollo510B openCFW overlay."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path
from typing import Any


class BuildError(RuntimeError):
    """The source, compiler output, patch ABI, or base image was unexpected."""


SHT_PROGBITS = 1
SHT_SYMTAB = 2
SHT_RELA = 4
SHT_NOBITS = 8
SHT_REL = 9
SHT_ARM_EXIDX = 0x70000001
SHF_WRITE = 0x1
SHF_ALLOC = 0x2
SHF_EXECINSTR = 0x4
STT_NOTYPE = 0
STT_FUNC = 2
STT_OBJECT = 1
STT_SECTION = 3
STB_LOCAL = 0
STB_GLOBAL = 1
EM_ARM = 40
R_ARM_REL32 = 3
R_ARM_THM_CALL = 10
R_ARM_THM_PC8 = 11
R_ARM_THM_JUMP24 = 30
R_ARM_PREL31 = 42
R_ARM_THM_MOVW_ABS_NC = 47
R_ARM_THM_MOVT_ABS = 48
R_ARM_THM_MOVW_PREL_NC = 49
R_ARM_THM_MOVT_PREL = 50

IN_PLACE_RELOCATION_TYPES = {
    "R_ARM_THM_CALL": R_ARM_THM_CALL,
    "R_ARM_THM_PC8": R_ARM_THM_PC8,
    "R_ARM_THM_JUMP24": R_ARM_THM_JUMP24,
    "R_ARM_THM_MOVW_ABS_NC": R_ARM_THM_MOVW_ABS_NC,
    "R_ARM_THM_MOVT_ABS": R_ARM_THM_MOVT_ABS,
    "R_ARM_THM_MOVW_PREL_NC": R_ARM_THM_MOVW_PREL_NC,
    "R_ARM_THM_MOVT_PREL": R_ARM_THM_MOVT_PREL,
}

ABSOLUTE_MOVWT_TYPES = {
    "R_ARM_THM_MOVW_ABS_NC",
    "R_ARM_THM_MOVT_ABS",
}

PREL_MOVWT_TYPES = {
    "R_ARM_THM_MOVW_PREL_NC",
    "R_ARM_THM_MOVT_PREL",
}

STRICT_EXTERNAL_SYMBOL_TYPES = {
    "STT_NOTYPE": STT_NOTYPE,
    "STT_OBJECT": STT_OBJECT,
    "STT_FUNC": STT_FUNC,
}


def authenticated_cantunwind_companion_indexes(
    data: bytes,
    sections: list[dict[str, Any]],
    symbols: list[dict[str, Any]],
    function_section: dict[str, Any],
) -> frozenset[int]:
    """Authenticate Clang's selected-function ``.ARM.exidx`` companion.

    Bare-metal ARM ELF objects retain one allocated CANTUNWIND row even with
    both unwind-table switches disabled.  Strict leaf extraction may discard
    that compiler metadata only when its section name, flags, bytes, and sole
    PREL31 section relocation bind exactly to the selected text section.
    """

    expected_name = ".ARM.exidx" + str(function_section["name"])
    matches = [
        section for section in sections
        if str(section["name"]) == expected_name and int(section["size"])
    ]
    if not matches:
        return frozenset()
    if len(matches) != 1:
        raise BuildError(
            f"selected function has {len(matches)} CANTUNWIND companions"
        )
    companion = matches[0]
    start = int(companion["offset"])
    if (
        int(companion["type"]) != SHT_ARM_EXIDX
        or int(companion["flags"]) != (SHF_ALLOC | 0x80)
        or int(companion["link"]) != int(function_section["index"])
        or int(companion["alignment"]) != 4
        or int(companion["size"]) != 8
        or data[start:start + 8] != b"\0\0\0\0\1\0\0\0"
    ):
        raise BuildError(
            f"selected-function CANTUNWIND companion {expected_name} differs "
            "from the reviewed canonical row"
        )
    relocation_sections = [
        section for section in sections
        if int(section["type"]) == SHT_REL
        and int(section["info"]) == int(companion["index"])
        and int(section["size"])
    ]
    if len(relocation_sections) != 1 or int(
        relocation_sections[0]["size"]
    ) != 8:
        raise BuildError(
            f"selected-function CANTUNWIND companion {expected_name} must "
            "have one REL entry"
        )
    relocation = relocation_sections[0]
    offset, information = struct.unpack_from("<II", data, int(relocation["offset"]))
    symbol_index = information >> 8
    if symbol_index >= len(symbols):
        raise BuildError(
            f"selected-function CANTUNWIND companion {expected_name} has an "
            "invalid relocation symbol"
        )
    symbol = symbols[symbol_index]
    if (
        offset != 0
        or information & 0xFF != R_ARM_PREL31
        or int(symbol["type"]) != STT_SECTION
        or int(symbol["binding"]) != STB_LOCAL
        or int(symbol["visibility"]) != 0
        or int(symbol["section_index"]) != int(function_section["index"])
    ):
        raise BuildError(
            f"selected-function CANTUNWIND companion {expected_name} does "
            "not bind canonically to the selected text section"
        )
    return frozenset({int(companion["index"])})


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def u32le(data: bytes, offset: int) -> int:
    if offset < 0 or offset + 4 > len(data):
        raise BuildError(f"word at 0x{offset:x} is outside the image")
    return struct.unpack_from("<I", data, offset)[0]


def align_up(value: int, alignment: int) -> int:
    if alignment < 1 or alignment & (alignment - 1):
        raise BuildError("overlay alignment must be a power of two")
    return (value + alignment - 1) & ~(alignment - 1)


def resolve_below(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as error:
        raise BuildError(f"path escapes openCFW root: {relative}") from error
    return path


def resolve_toolchain_include_dirs(
    root: Path,
    toolchain: dict[str, Any],
) -> tuple[list[Path], list[str] | None]:
    if "include_dirs" not in toolchain:
        return [], None

    include_dirs = toolchain["include_dirs"]
    if not isinstance(include_dirs, list):
        raise BuildError("toolchain.include_dirs must be a list")

    resolved_root = root.resolve()
    resolved_dirs: list[Path] = []
    normalized_dirs: list[str] = []
    for index, relative in enumerate(include_dirs):
        if not isinstance(relative, str) or not relative.strip():
            raise BuildError(
                "toolchain.include_dirs entries must be nonempty strings"
            )
        if Path(relative).is_absolute():
            raise BuildError(
                "toolchain.include_dirs entries must be openCFW-root-relative: "
                f"{relative}"
            )
        directory = resolve_below(resolved_root, relative)
        if not directory.is_dir():
            raise BuildError(
                f"toolchain.include_dirs[{index}] is not a directory: {relative}"
            )
        resolved_dirs.append(directory)
        normalized_dirs.append(directory.relative_to(resolved_root).as_posix())

    return resolved_dirs, normalized_dirs


def load_config(path: Path) -> dict[str, Any]:
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise BuildError(f"cannot read {path}: {error}") from error
    if config.get("schema_version") != 1:
        raise BuildError("unsupported overlay schema")
    return config


def compiler_version(clang: str) -> str:
    completed = subprocess.run(
        [clang, "--version"],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode:
        raise BuildError(
            completed.stderr.strip() or f"cannot execute compiler {clang}"
        )
    first_line = completed.stdout.splitlines()
    if not first_line:
        raise BuildError(f"compiler {clang} returned no version")
    return first_line[0].strip()


def validate_compiler_version(
    toolchain: dict[str, Any],
    observed_version: str,
) -> None:
    reviewed_version = toolchain.get("reviewed_version")
    reviewed_version_prefix = toolchain.get("reviewed_version_prefix")
    if reviewed_version and reviewed_version_prefix:
        raise BuildError(
            "toolchain cannot set both reviewed_version and "
            "reviewed_version_prefix"
        )
    if reviewed_version and observed_version != reviewed_version:
        raise BuildError(
            "compiler version differs from the reviewed toolchain:\n"
            f"  expected: {reviewed_version}\n"
            f"  observed: {observed_version}"
        )
    if reviewed_version_prefix and not observed_version.startswith(
        reviewed_version_prefix
    ):
        raise BuildError(
            "compiler version differs from the reviewed toolchain family:\n"
            f"  expected prefix: {reviewed_version_prefix}\n"
            f"  observed: {observed_version}"
        )


def compiler_source_prefix_flags(
    root: Path,
    toolchain: dict[str, Any],
) -> list[str]:
    """Map the active openCFW root to its reviewed profile spelling."""

    flags = toolchain.get("flags", [])
    if not isinstance(flags, list):
        raise BuildError("toolchain.flags must be a list")
    if any(not isinstance(flag, str) or not flag for flag in flags):
        raise BuildError(
            "toolchain.flags entries must be nonempty strings"
        )
    if any(flag.startswith("@") for flag in flags):
        raise BuildError("toolchain.flags cannot use response files")
    if any(flag.startswith("-ffile-prefix-map=") for flag in flags):
        raise BuildError("toolchain.flags cannot set -ffile-prefix-map")

    reviewed_root = toolchain.get("reviewed_source_root")
    if reviewed_root is None:
        return []
    if not isinstance(reviewed_root, str):
        raise BuildError(
            "toolchain.reviewed_source_root must be an absolute path string"
        )
    if not Path(reviewed_root).is_absolute():
        raise BuildError(
            "toolchain.reviewed_source_root must be an absolute path"
        )

    actual_root = str(root.resolve())
    if actual_root == reviewed_root:
        return []
    return [f"-ffile-prefix-map={actual_root}={reviewed_root}"]


#: The canonical, reviewed macOS toolchain profile.  Its pins are the
#: config's own ``toolchain`` and ``expected`` blocks and stay byte-identical
#: to the reviewed Apple-clang reference.  Alternate reproducible toolchains
#: (for example a Linux Homebrew clang) live under ``toolchain_profiles`` and
#: carry their own independently recorded, fail-closed pins.
DEFAULT_TOOLCHAIN_PROFILE = "apple-clang"


def resolve_toolchain_profile(
    config: dict[str, Any],
    profile_id: str | None,
    *,
    record: bool = False,
) -> tuple[dict[str, Any], dict[str, Any], str]:
    """Select the active toolchain profile.

    Returns the effective ``toolchain`` block, the effective ``expected``
    pin block, and the resolved profile id.  The canonical ``apple-clang``
    profile returns the config's own blocks unchanged so the reviewed
    reference path is never perturbed.  A named alternate profile inherits
    the base toolchain and may override the reviewed compiler family, source
    root, flags, target, include dirs, and expected pins.

    When ``record`` is set, the compiler-version gate and expected pins are
    intentionally dropped so the actual compiler output can be captured and
    written back as the new profile pins.  The canonical profile can never be
    recorded.
    """

    base_toolchain = config["toolchain"]
    base_expected = config.get("expected", {})
    resolved = profile_id or DEFAULT_TOOLCHAIN_PROFILE

    if record:
        if resolved == DEFAULT_TOOLCHAIN_PROFILE:
            raise BuildError(
                "cannot record the canonical apple-clang profile; its pins "
                "are the reviewed reference"
            )
        profiles = config.get("toolchain_profiles") or {}
        profile = profiles.get(resolved, {})
        if not isinstance(profile, dict):
            raise BuildError(
                f"toolchain profile {resolved!r} must be an object"
            )
        effective = dict(base_toolchain)
        for key in (
            "flags",
            "target",
            "include_dirs",
            "reviewed_source_root",
        ):
            if key in profile:
                effective[key] = profile[key]
        # Accept whatever compiler is present so its output can be pinned.
        effective.pop("reviewed_version", None)
        effective.pop("reviewed_version_prefix", None)
        return effective, {}, resolved

    if resolved == DEFAULT_TOOLCHAIN_PROFILE:
        return base_toolchain, base_expected, resolved

    profiles = config.get("toolchain_profiles")
    if profiles is None:
        # A config that declares no profiles is profile-unaware (synthetic test
        # fixtures, the reference profile): honor the canonical pins regardless
        # of the requested profile rather than failing closed.
        return base_toolchain, base_expected, DEFAULT_TOOLCHAIN_PROFILE
    if not isinstance(profiles, dict) or resolved not in profiles:
        raise BuildError(
            f"unknown toolchain profile {resolved!r}; define it under "
            "toolchain_profiles or record it first"
        )
    profile = profiles[resolved]
    if not isinstance(profile, dict):
        raise BuildError(f"toolchain profile {resolved!r} must be an object")

    effective_toolchain = dict(base_toolchain)
    for key in (
        "reviewed_version",
        "reviewed_version_prefix",
        "flags",
        "target",
        "include_dirs",
        "reviewed_source_root",
    ):
        if key in profile:
            effective_toolchain[key] = profile[key]
    # A profile pins exactly one of reviewed_version / reviewed_version_prefix;
    # drop the inherited one if the profile pins the other.
    if "reviewed_version" in profile:
        effective_toolchain.pop("reviewed_version_prefix", None)
    elif "reviewed_version_prefix" in profile:
        effective_toolchain.pop("reviewed_version", None)

    effective_expected = profile.get("expected", {})
    if not isinstance(effective_expected, dict):
        raise BuildError(
            f"toolchain profile {resolved!r} expected must be an object"
        )
    return effective_toolchain, effective_expected, resolved


def resolve_leaf_profile(
    leaf_config: dict[str, Any],
    profile_id: str | None,
    *,
    record: bool = False,
) -> dict[str, Any]:
    """Return a leaf config specialized for the active toolchain profile.

    Leaves carry the same ``toolchain``/``expected`` shape as the primary
    overlay, plus optional ``toolchain_profiles`` entries.  Unlike the overlay,
    a leaf profile's ``expected`` is *optional*: assembly leaves (`.S`) and any
    leaf whose compiled bytes are compiler-independent keep the canonical
    ``expected`` and only relax the reviewed compiler family.  Only leaves whose
    bytes actually differ under the profile record their own ``expected``.

    When ``record`` is set the reviewed compiler gate is dropped (so the current
    compiler is accepted) and the caller skips the final observed-vs-pin
    comparison.  An existing named profile still supplies its structural and
    compilation choices: recording is allowed to refresh pins, but must not
    silently switch an already reviewed leaf back to the canonical profile's
    closure, relocations, flags, target, include paths, or expected layout.  A
    leaf with no entry for the requested profile starts from its canonical
    configuration so new leaves can be recorded incrementally.
    """

    function = leaf_config.get("function")
    base_toolchain = leaf_config.get("toolchain")
    if not isinstance(base_toolchain, dict):
        raise BuildError(f"leaf {function!r} requires a toolchain")

    resolved = profile_id or DEFAULT_TOOLCHAIN_PROFILE
    if resolved == DEFAULT_TOOLCHAIN_PROFILE and not record:
        return leaf_config

    profiles = leaf_config.get("toolchain_profiles")
    if profiles is None:
        # Profile-unaware synthetic fixtures use canonical pins during normal
        # builds.  During recording, an absent profile is also the expected
        # state for a newly introduced leaf.
        if not record:
            return leaf_config
        profile: dict[str, Any] = {}
    else:
        if not isinstance(profiles, dict):
            raise BuildError(
                f"leaf {function!r} toolchain_profiles must be an object"
            )
        missing = object()
        selected = profiles.get(resolved, missing)
        if selected is missing:
            if not record:
                raise BuildError(
                    f"leaf {function!r} has no {resolved!r} toolchain "
                    "profile; record it first"
                )
            profile = {}
        elif not isinstance(selected, dict):
            raise BuildError(
                f"leaf {function!r} profile {resolved!r} must be an object"
            )
        else:
            profile = selected

    allowed_profile_fields = {
        "reviewed_version",
        "reviewed_version_prefix",
        "flags",
        "target",
        "include_dirs",
        "expected",
        "relocations",
        "closure",
    }
    unknown_profile_fields = set(profile) - allowed_profile_fields
    if unknown_profile_fields:
        raise BuildError(
            f"leaf {function!r} profile {resolved!r} has unknown fields "
            f"{sorted(unknown_profile_fields)}"
        )
    if "reviewed_version" in profile and "reviewed_version_prefix" in profile:
        raise BuildError(
            f"leaf {function!r} profile {resolved!r} cannot set both "
            "reviewed_version and reviewed_version_prefix"
        )

    toolchain = dict(base_toolchain)
    if "reviewed_version" in profile:
        toolchain["reviewed_version"] = profile["reviewed_version"]
        toolchain.pop("reviewed_version_prefix", None)
    elif "reviewed_version_prefix" in profile:
        toolchain["reviewed_version_prefix"] = profile["reviewed_version_prefix"]
        toolchain.pop("reviewed_version", None)
    for key in ("flags", "target", "include_dirs"):
        if key in profile:
            toolchain[key] = profile[key]
    if record:
        # Version pins authenticate normal builds.  Record mode intentionally
        # accepts the compiler being measured, but keeps every other selected
        # profile input intact.
        toolchain.pop("reviewed_version", None)
        toolchain.pop("reviewed_version_prefix", None)

    effective = {**leaf_config, "toolchain": toolchain}
    if "expected" in profile:
        # A recorded, profile-specific compiled leaf overrides the canonical
        # pins.  Absent means the bytes are identical across toolchains.
        if not isinstance(profile["expected"], dict):
            raise BuildError(
                f"leaf {function!r} profile {resolved!r} expected must be an "
                "object"
            )
        effective["expected"] = profile["expected"]
    if "relocations" in profile:
        # Relocated leaves whose outgoing-call offsets shifted under this
        # toolchain carry their observed relocation offsets here; the call
        # targets and ordering are unchanged.
        if not isinstance(profile["relocations"], list):
            raise BuildError(
                f"leaf {function!r} profile {resolved!r} relocations must be a "
                "list"
            )
        effective["relocations"] = profile["relocations"]
    if "closure" in profile:
        if not isinstance(profile["closure"], dict):
            raise BuildError(
                f"leaf {function!r} profile {resolved!r} closure must be an "
                "object"
            )
        base_closure = leaf_config.get("closure")
        if not isinstance(base_closure, dict):
            raise BuildError(
                f"leaf {function!r} profile {resolved!r} cannot override a "
                "missing canonical closure"
            )
        closure = {**base_closure, **profile["closure"]}
        if "rodata" in profile["closure"]:
            if not isinstance(base_closure.get("rodata"), dict) or not isinstance(
                profile["closure"]["rodata"], dict
            ):
                raise BuildError(
                    f"leaf {function!r} profile {resolved!r} closure.rodata "
                    "must be an object"
                )
            closure["rodata"] = {
                **base_closure["rodata"],
                **profile["closure"]["rodata"],
            }
        effective["closure"] = closure
    return effective


def _active_for_profile(item: dict[str, Any], profile_id: str) -> bool:
    """Whether a leaf/patch-site is included under the active toolchain profile.

    An item with no ``profiles`` key is included everywhere (the default). An
    item that lists ``profiles`` is included only when the active profile is in
    the list — so a source replacement recorded only for, say, ``linux-clang``
    is absent under ``apple-clang`` and leaves that profile's overlay
    byte-identical.
    """

    profiles = item.get("profiles")
    if profiles is None:
        return True
    if not isinstance(profiles, list) or any(
        not isinstance(name, str) for name in profiles
    ):
        raise BuildError("item 'profiles' must be a list of profile ids")
    return profile_id in profiles


def filter_config_for_profile(
    config: dict[str, Any],
    profile_id: str,
) -> dict[str, Any]:
    """Drop profile-gated leaves, patch sites, and their functions.

    Leaves and patch sites may carry a ``profiles`` allow-list; those not active
    for ``profile_id`` are removed, and any overlay function contributed only by
    a removed leaf is dropped from the function ABI. Profiles that gate nothing
    (the common case, e.g. the canonical apple-clang set) are unaffected.
    """

    excluded_functions: set[str] = set()
    filtered = dict(config)
    for key in ("isolated_leaves", "relocated_leaves", "in_place_leaves"):
        leaves = config.get(key)
        if not isinstance(leaves, list):
            continue  # leave malformed config untouched for downstream schema checks
        kept = []
        for leaf in leaves:
            if isinstance(leaf, dict) and not _active_for_profile(leaf, profile_id):
                name = leaf.get("function")
                if isinstance(name, str):
                    excluded_functions.add(name)
                continue
            kept.append(leaf)
        filtered[key] = kept
    if isinstance(config.get("patch_sites"), list):
        filtered["patch_sites"] = [
            site
            for site in config["patch_sites"]
            if not isinstance(site, dict)
            or _active_for_profile(site, profile_id)
        ]
    functions = config.get("functions")
    if excluded_functions and isinstance(functions, list):
        filtered["functions"] = [
            name for name in functions if name not in excluded_functions
        ]
    return filtered


def parse_elf32(path: Path) -> tuple[bytes, list[dict[str, int | str]]]:
    data = path.read_bytes()
    if (
        len(data) < 0x34
        or data[:4] != b"\x7fELF"
        or data[4] != 1
        or data[5] != 1
    ):
        raise BuildError("compiler output is not ELF32 little-endian")
    machine = struct.unpack_from("<H", data, 0x12)[0]
    if machine != EM_ARM:
        raise BuildError(f"compiler output machine is {machine}, expected ARM")
    section_offset = u32le(data, 0x20)
    section_entry_size, section_count, names_index = struct.unpack_from(
        "<HHH", data, 0x2E
    )
    if (
        section_entry_size != 40
        or section_count < 1
        or names_index >= section_count
        or section_offset + section_entry_size * section_count > len(data)
    ):
        raise BuildError("ELF section table is invalid")
    sections: list[dict[str, int | str]] = []
    for index in range(section_count):
        fields = struct.unpack_from(
            "<IIIIIIIIII",
            data,
            section_offset + index * section_entry_size,
        )
        sections.append(
            {
                "index": index,
                "name_offset": fields[0],
                "type": fields[1],
                "flags": fields[2],
                "address": fields[3],
                "offset": fields[4],
                "size": fields[5],
                "link": fields[6],
                "info": fields[7],
                "alignment": fields[8],
                "entry_size": fields[9],
            }
        )
    names = sections[names_index]
    names_start = int(names["offset"])
    names_end = names_start + int(names["size"])
    if names_end > len(data):
        raise BuildError("ELF section-name table is invalid")
    names_data = data[names_start:names_end]
    for section in sections:
        offset = int(section["name_offset"])
        if offset >= len(names_data):
            raise BuildError("ELF section name exceeds the string table")
        end = names_data.find(b"\0", offset)
        if end < 0:
            raise BuildError("unterminated ELF section name")
        section["name"] = names_data[offset:end].decode("ascii")
        payload_end = int(section["offset"]) + int(section["size"])
        if int(section["type"]) != SHT_NOBITS and payload_end > len(data):
            raise BuildError(f"ELF section {section['name']} exceeds the file")
    return data, sections


def section_named(
    sections: list[dict[str, int | str]],
    name: str,
) -> dict[str, int | str]:
    matches = [section for section in sections if section["name"] == name]
    if len(matches) != 1:
        raise BuildError(f"expected one {name} section, observed {len(matches)}")
    return matches[0]


def elf_string(data: bytes, offset: int, label: str) -> str:
    if offset >= len(data):
        raise BuildError(f"{label} exceeds its ELF string table")
    end = data.find(b"\0", offset)
    if end < 0:
        raise BuildError(f"unterminated {label}")
    try:
        return data[offset:end].decode("ascii")
    except UnicodeDecodeError as error:
        raise BuildError(f"non-ASCII {label}") from error


def parse_elf32_symbols(
    data: bytes,
    sections: list[dict[str, int | str]],
) -> list[dict[str, int | str]]:
    symbol_sections = [
        section for section in sections if int(section["type"]) == SHT_SYMTAB
    ]
    if len(symbol_sections) != 1:
        raise BuildError("compiled object must contain one symbol table")
    symbols = symbol_sections[0]
    symbol_size = int(symbols["entry_size"])
    if symbol_size != 16 or int(symbols["link"]) >= len(sections):
        raise BuildError("ELF symbol table is invalid")
    strings = sections[int(symbols["link"])]
    string_data = data[
        int(strings["offset"]):int(strings["offset"]) + int(strings["size"])
    ]

    parsed_symbols: list[dict[str, int | str]] = []
    symbol_count = int(symbols["size"]) // symbol_size
    for index in range(symbol_count):
        base = int(symbols["offset"]) + index * symbol_size
        (
            name_offset,
            value,
            size,
            info,
            other,
            section_index,
        ) = struct.unpack_from("<IIIBBH", data, base)
        parsed_symbols.append(
            {
                "name": elf_string(string_data, name_offset, "symbol name"),
                "value": value,
                "size": size,
                "binding": info >> 4,
                "type": info & 0x0F,
                "visibility": other & 0x03,
                "section_index": section_index,
            }
        )
    return parsed_symbols


def is_rodata(section: dict[str, int | str]) -> bool:
    flags = int(section["flags"])
    return (
        int(section["type"]) == SHT_PROGBITS
        and bool(flags & SHF_ALLOC)
        and not bool(flags & (SHF_WRITE | SHF_EXECINSTR))
    )


def thumb_movwt_immediate(first: int, second: int) -> int:
    return (
        ((first & 0x000F) << 12)
        | (((first >> 10) & 1) << 11)
        | (((second >> 12) & 7) << 8)
        | (second & 0x00FF)
    )


def thumb_movwt_with_immediate(first: int, second: int, value: int) -> tuple[int, int]:
    value &= 0xFFFF
    first = (
        (first & ~((1 << 10) | 0x000F))
        | (((value >> 11) & 1) << 10)
        | ((value >> 12) & 0x000F)
    )
    second = (
        (second & ~((7 << 12) | 0x00FF))
        | (((value >> 8) & 7) << 12)
        | (value & 0x00FF)
    )
    return first, second


def resolve_absolute_movwt(
    blob: bytearray,
    site: int,
    symbol_address: int,
    *,
    high: bool,
) -> None:
    """Resolve one zero-addend Thumb MOVW/MOVT absolute relocation."""

    if site < 0 or site + 4 > len(blob):
        raise BuildError("absolute MOVW/MOVT relocation exceeds the overlay")
    first, second = struct.unpack_from("<HH", blob, site)
    expected_opcode = 0xF2C0 if high else 0xF240
    if (
        first & 0xFBF0 != expected_opcode
        or second & 0x8000
        or thumb_movwt_immediate(first, second) != 0
    ):
        raise BuildError(
            "absolute MOVW/MOVT relocation requires its canonical zero-addend "
            "Thumb instruction"
        )
    if high:
        if site < 4:
            raise BuildError("absolute MOVT relocation is missing its MOVW pair")
        _low_first, low_second = struct.unpack_from("<HH", blob, site - 4)
        if (low_second & 0x0F00) != (second & 0x0F00):
            raise BuildError(
                "absolute MOVW/MOVT pair must use the same destination register"
            )
    value = symbol_address >> 16 if high else symbol_address
    first, second = thumb_movwt_with_immediate(first, second, value)
    struct.pack_into("<HH", blob, site, first, second)


def validate_absolute_movwt_pairs(
    relocations: list[dict[str, Any]],
    *,
    context: str,
) -> None:
    """Require adjacent, same-symbol low/high absolute materialization pairs."""

    for index, relocation in enumerate(relocations):
        relocation_type = relocation["type"]
        if relocation_type == "R_ARM_THM_MOVW_ABS_NC":
            if index + 1 >= len(relocations):
                raise BuildError(f"{context} has an unpaired absolute MOVW")
            partner = relocations[index + 1]
            if (
                partner["type"] != "R_ARM_THM_MOVT_ABS"
                or partner["offset"] != relocation["offset"] + 4
                or partner["symbol"] != relocation["symbol"]
                or partner.get("target_address")
                != relocation.get("target_address")
            ):
                raise BuildError(
                    f"{context} absolute MOVW/MOVT must be an adjacent "
                    "same-symbol, same-target pair"
                )
        elif relocation_type == "R_ARM_THM_MOVT_ABS":
            if index == 0 or relocations[index - 1]["type"] != (
                "R_ARM_THM_MOVW_ABS_NC"
            ):
                raise BuildError(f"{context} has an unpaired absolute MOVT")


def validate_prel_movwt_pairs(
    relocations: list[dict[str, Any]],
    *,
    context: str,
) -> None:
    """Require ordered same-symbol MOVW/MOVT PREL relocation pairs."""

    for index, relocation in enumerate(relocations):
        relocation_type = relocation["type"]
        if relocation_type == "R_ARM_THM_MOVW_PREL_NC":
            if index + 1 >= len(relocations):
                raise BuildError(f"{context} has an unpaired PREL MOVW")
            partner = relocations[index + 1]
            if (
                partner["type"] != "R_ARM_THM_MOVT_PREL"
                or partner["offset"] <= relocation["offset"]
                or partner["symbol"] != relocation["symbol"]
                or partner.get("target_address")
                != relocation.get("target_address")
            ):
                raise BuildError(
                    f"{context} PREL MOVW/MOVT must be an adjacent "
                    "same-symbol pair in relocation order with the same target"
                )
        elif relocation_type == "R_ARM_THM_MOVT_PREL":
            if index == 0 or relocations[index - 1]["type"] != (
                "R_ARM_THM_MOVW_PREL_NC"
            ):
                raise BuildError(f"{context} has an unpaired PREL MOVT")


def resolve_prel_movwt_pair(
    blob: bytearray,
    low_site: int,
    symbol_offset: int,
    *,
    high_site: int | None = None,
    symbol_thumb: bool = False,
) -> dict[str, int | str]:
    """Resolve one authenticated Thumb PREL MOVW/MOVT REL pair.

    AAELF32 defines a distinct signed 16-bit implicit addend in each REL
    instruction.  Reconstruct both complete relocation expressions before
    modifying either instruction so malformed or independently-authored
    halves cannot be accepted as one address.  Reviewed closure pairs are
    adjacent; the combined legacy overlay also contains compiler-scheduled
    pairs with unrelated instructions between the two sites.
    """

    if high_site is None:
        high_site = low_site + 4
    if (
        low_site < 0
        or high_site <= low_site
        or low_site + 4 > len(blob)
        or high_site + 4 > len(blob)
    ):
        raise BuildError("PREL MOVW/MOVT pair exceeds the overlay")
    if not 0 <= symbol_offset <= 0xFFFFFFFF:
        raise BuildError("PREL MOVW/MOVT symbol offset is outside ELF32 range")

    low_first, low_second = struct.unpack_from("<HH", blob, low_site)
    high_first, high_second = struct.unpack_from("<HH", blob, high_site)
    if low_first & 0xFBF0 != 0xF240 or low_second & 0x8000:
        raise BuildError(
            "PREL MOVW/MOVT pair requires a canonical Thumb MOVW instruction"
        )
    if high_first & 0xFBF0 != 0xF2C0 or high_second & 0x8000:
        raise BuildError(
            "PREL MOVW/MOVT pair requires a canonical Thumb MOVT instruction"
        )
    low_register = (low_second >> 8) & 0x0F
    high_register = (high_second >> 8) & 0x0F
    if low_register != high_register:
        raise BuildError(
            "PREL MOVW/MOVT pair must use the same destination register"
        )

    low_addend = thumb_movwt_immediate(low_first, low_second)
    high_addend = thumb_movwt_immediate(high_first, high_second)
    if low_addend & 0x8000:
        low_addend -= 0x10000
    if high_addend & 0x8000:
        high_addend -= 0x10000

    # AAELF32 applies the two REL records independently:
    #
    #   MOVW_PREL_NC: X = ((S + A) | T) - P; encode X[15:0]
    #   MOVT_PREL:    X =   S + A       - P; encode X[31:16]
    #
    # The static relocation table specifies no overflow check, so each X is
    # reduced modulo 2**32.  A compiler normally compensates for the MOVT
    # later P in A_high, making the two X values identical.  For an adjacent
    # pair this means A_high = A_low + 4.  A zero/zero pair is well-defined by
    # the ABI and is emitted exactly as lld does: its values differ by four.
    # It is safe only while both computations select the same upper half;
    # otherwise the two instructions would silently materialize a hybrid
    # across a 64-KiB carry/borrow boundary.
    low_result = (
        ((symbol_offset + low_addend) | int(symbol_thumb)) - low_site
    ) & 0xFFFFFFFF
    high_result = (
        symbol_offset + high_addend - high_site
    ) & 0xFFFFFFFF
    if low_result >> 16 != high_result >> 16:
        raise BuildError(
            "PREL MOVW/MOVT pair halves do not select the same upper "
            "16-bit relocation result"
        )
    materialized = (high_result & 0xFFFF0000) | (low_result & 0xFFFF)

    low_first, low_second = thumb_movwt_with_immediate(
        low_first,
        low_second,
        low_result,
    )
    high_first, high_second = thumb_movwt_with_immediate(
        high_first,
        high_second,
        high_result >> 16,
    )
    struct.pack_into("<HH", blob, low_site, low_first, low_second)
    struct.pack_into("<HH", blob, high_site, high_first, high_second)
    return {
        "low_addend": low_addend,
        "high_addend": high_addend,
        "low_result": low_result,
        "low_result_hex": f"0x{low_result:08X}",
        "high_result": high_result,
        "high_result_hex": f"0x{high_result:08X}",
        "result": materialized,
        "result_hex": f"0x{materialized:08X}",
        "register": low_register,
    }


def resolve_rel32(
    blob: bytearray,
    site: int,
    symbol_address: int,
) -> None:
    """Resolve an ARM REL32 record within one position-independent blob."""

    if site < 0 or site + 4 > len(blob):
        raise BuildError("REL32 relocation exceeds the overlay")
    addend = struct.unpack_from("<i", blob, site)[0]
    struct.pack_into(
        "<I",
        blob,
        site,
        (symbol_address + addend - site) & 0xFFFFFFFF,
    )


def resolve_internal_thumb_branch(
    blob: bytearray,
    site: int,
    target: int,
) -> None:
    if site < 0 or site + 4 > len(blob):
        raise BuildError("Thumb relocation exceeds the overlay")
    _first, old_second = struct.unpack_from("<HH", blob, site)
    link = bool(old_second & 0x4000)
    blob[site:site + 4] = encode_thumb_branch(site, target, link=link)


def extract_linked_overlay(
    object_path: Path,
) -> tuple[bytes, dict[str, dict[str, int]], dict[str, Any]]:
    data, sections = parse_elf32(object_path)
    text_section = section_named(sections, ".text")
    text_index = int(text_section["index"])
    text_start = int(text_section["offset"])
    text_size = int(text_section["size"])
    blob = bytearray(data[text_start:text_start + text_size])
    if not blob:
        raise BuildError("compiled overlay has an empty .text section")

    for section in sections:
        flags = int(section["flags"])
        if (
            flags & (SHF_ALLOC | SHF_WRITE) == (SHF_ALLOC | SHF_WRITE)
            and int(section["size"])
        ):
            raise BuildError(
                f"compiled overlay has writable section {section['name']}; "
                "persistent state must use an explicitly reviewed firmware RAM ABI"
            )

    section_bases: dict[int, int] = {text_index: 0}
    rodata_sections: list[dict[str, Any]] = []
    for section in sections:
        if not is_rodata(section):
            continue
        alignment = max(1, int(section["alignment"]))
        blob.extend(b"\0" * (align_up(len(blob), alignment) - len(blob)))
        section_index = int(section["index"])
        section_bases[section_index] = len(blob)
        start = int(section["offset"])
        size = int(section["size"])
        blob.extend(data[start:start + size])
        rodata_sections.append(
            {
                "name": section["name"],
                "offset": section_bases[section_index],
                "size": size,
                "alignment": alignment,
            }
        )

    parsed_symbols = parse_elf32_symbols(data, sections)

    resolved_relocations: list[dict[str, Any]] = []
    for relocation_section in sections:
        if int(relocation_section["type"]) != SHT_REL:
            continue
        target_section_index = int(relocation_section["info"])
        if target_section_index not in section_bases:
            continue
        entry_size = int(relocation_section["entry_size"])
        if entry_size != 8 or int(relocation_section["size"]) % entry_size:
            raise BuildError(f"invalid relocation table {relocation_section['name']}")
        count = int(relocation_section["size"]) // entry_size
        relocation_records: list[tuple[int, int, int]] = []
        for index in range(count):
            entry = int(relocation_section["offset"]) + index * entry_size
            relative_offset, info = struct.unpack_from("<II", data, entry)
            relocation_records.append((relative_offset, info & 0xFF, info >> 8))
        relocation_records.sort(key=lambda item: item[0])
        prel_pair_details: dict[int, dict[str, int | str]] = {}
        paired_high_indexes: set[int] = set()
        for low_index, (low_offset, low_type, symbol_index) in enumerate(
            relocation_records
        ):
            if low_type != R_ARM_THM_MOVW_PREL_NC:
                continue
            following_prel_indexes = [
                high_index
                for high_index, (_high_offset, high_type, _high_symbol_index)
                in enumerate(relocation_records[low_index + 1:], low_index + 1)
                if high_type in (
                    R_ARM_THM_MOVW_PREL_NC,
                    R_ARM_THM_MOVT_PREL,
                )
            ]
            high_index = (
                following_prel_indexes[0] if following_prel_indexes else -1
            )
            high_record = (
                relocation_records[high_index] if high_index >= 0 else None
            )
            if (
                high_record is None
                or high_record[1] != R_ARM_THM_MOVT_PREL
                or high_record[2] != symbol_index
                or high_index in paired_high_indexes
            ):
                raise BuildError(
                    "compiled overlay PREL MOVW/MOVT must be an ordered "
                    f"same-symbol pair; MOVW at +0x{low_offset:X} has no "
                    "matching next PREL record"
                )
            if symbol_index >= len(parsed_symbols):
                raise BuildError("relocation references an invalid symbol")
            symbol = parsed_symbols[symbol_index]
            symbol_section_index = int(symbol["section_index"])
            if symbol_section_index not in section_bases:
                raise BuildError(
                    "compiled overlay PREL MOVW/MOVT target is outside "
                    "the linked overlay"
                )
            symbol_value = int(symbol["value"])
            symbol_thumb = int(symbol["type"]) == STT_FUNC
            target = section_bases[symbol_section_index] + (
                symbol_value & ~1 if symbol_thumb else symbol_value
            )
            details = resolve_prel_movwt_pair(
                blob,
                section_bases[target_section_index] + low_offset,
                target,
                high_site=(
                    section_bases[target_section_index] + high_record[0]
                ),
                symbol_thumb=symbol_thumb,
            )
            prel_pair_details[low_index] = details
            prel_pair_details[high_index] = details
            paired_high_indexes.add(high_index)
        for high_index, (_offset, relocation_type, _symbol_index) in enumerate(
            relocation_records
        ):
            if (
                relocation_type == R_ARM_THM_MOVT_PREL
                and high_index not in paired_high_indexes
            ):
                raise BuildError("compiled overlay has an unpaired PREL MOVT")
        index = 0
        while index < count:
            relative_offset, relocation_type, symbol_index = relocation_records[
                index
            ]
            if symbol_index >= len(parsed_symbols):
                raise BuildError("relocation references an invalid symbol")
            symbol = parsed_symbols[symbol_index]
            symbol_section_index = int(symbol["section_index"])
            site = section_bases[target_section_index] + relative_offset
            if (
                relocation_type in (R_ARM_THM_CALL, R_ARM_THM_JUMP24)
                and target_section_index == text_index
                and symbol_section_index == text_index
            ):
                target = int(symbol["value"]) & ~1
                resolve_internal_thumb_branch(blob, site, target)
            elif relocation_type in (
                R_ARM_THM_MOVW_PREL_NC,
                R_ARM_THM_MOVT_PREL,
            ):
                if index not in prel_pair_details:
                    raise BuildError("compiled overlay has an unpaired PREL MOVW")
            elif (
                relocation_type == R_ARM_REL32
                and symbol_section_index in section_bases
            ):
                target = section_bases[symbol_section_index] + int(
                    symbol["value"]
                )
                resolve_rel32(blob, site, target)
            else:
                raise BuildError(
                    f"unresolvable relocation {relocation_section['name']}+"
                    f"0x{relative_offset:x} type {relocation_type} to "
                    f"{symbol['name']!r}; only internal Thumb branches and "
                    "-fropi read-only-data references are supported"
                )
            resolved_relocations.append(
                {
                    "section": relocation_section["name"],
                    "site": site,
                    "type": relocation_type,
                    "symbol": symbol["name"],
                    **prel_pair_details.get(index, {}),
                }
            )
            index += 1

    functions: dict[str, dict[str, int]] = {}
    for symbol in parsed_symbols:
        if (
            int(symbol["type"]) != STT_FUNC
            or int(symbol["section_index"]) != text_index
        ):
            continue
        name = str(symbol["name"])
        offset = int(symbol["value"]) & ~1
        size = int(symbol["size"])
        if offset + size > text_size:
            raise BuildError(f"function {name} exceeds .text")
        if name in functions:
            raise BuildError(f"duplicate function symbol {name}")
        functions[name] = {"offset": offset, "size": size}
    if not functions:
        raise BuildError("compiled overlay contains no function symbols")
    return (
        bytes(blob),
        functions,
        {
            "text_size": text_size,
            "rodata_size": len(blob) - text_size,
            "rodata_sections": rodata_sections,
            "resolved_relocation_count": len(resolved_relocations),
            "resolved_relocations": resolved_relocations,
        },
    )


def compile_overlay(
    *,
    clang: str,
    source_path: Path,
    object_path: Path,
    config: dict[str, Any],
    include_dirs: list[Path] | tuple[Path, ...] = (),
    expected_functions: set[str] | None = None,
) -> tuple[bytes, dict[str, dict[str, int]], str, dict[str, Any]]:
    version = compiler_version(clang)
    validate_compiler_version(config["toolchain"], version)
    include_arguments: list[str] = []
    for include_dir in include_dirs:
        if not include_dir.is_absolute():
            raise BuildError("compiler include directories must be absolute")
        include_arguments.extend(("-I", str(include_dir)))
    command = [
        clang,
        f"--target={config['toolchain']['target']}",
        *config["toolchain"]["flags"],
        *include_arguments,
        "-c",
        str(source_path),
        "-o",
        str(object_path),
    ]
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode:
        raise BuildError(
            "overlay compilation failed:\n"
            + (completed.stderr.strip() or completed.stdout.strip())
        )
    overlay, functions, link_report = extract_linked_overlay(object_path)
    reviewed_functions = (
        set(config["functions"])
        if expected_functions is None
        else set(expected_functions)
    )
    if set(functions) != reviewed_functions:
        raise BuildError(
            f"function ABI changed: expected {sorted(reviewed_functions)}, "
            f"observed {sorted(functions)}"
        )
    return overlay, functions, version, link_report


def extract_isolated_function_section(
    object_path: Path,
    function_name: str,
) -> tuple[bytes, dict[str, Any]]:
    """Extract one dependency-free function section from a full ARM object.

    This deliberately does not perform ELF garbage collection or link the
    translation unit.  Only the named function's dedicated section is copied,
    and any relocation that applies to that section is a hard failure.  Other
    functions, writable data, unwind tables, and unresolved symbols may exist
    in the source object, but cannot enter the returned bytes.
    """

    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", function_name):
        raise BuildError("isolated leaf function must be a C identifier")

    data, sections = parse_elf32(object_path)
    section_name = f".text.{function_name}"
    function_section = section_named(sections, section_name)
    section_index = int(function_section["index"])
    flags = int(function_section["flags"])
    if (
        int(function_section["type"]) != SHT_PROGBITS
        or flags & (SHF_ALLOC | SHF_EXECINSTR) != (SHF_ALLOC | SHF_EXECINSTR)
        or flags & SHF_WRITE
    ):
        raise BuildError(
            f"isolated leaf section {section_name} is not read-only executable "
            "PROGBITS"
        )
    section_size = int(function_section["size"])
    if section_size < 1:
        raise BuildError(f"isolated leaf section {section_name} is empty")
    alignment = int(function_section["alignment"])
    if alignment < 1 or alignment & (alignment - 1):
        raise BuildError(
            f"isolated leaf section {section_name} has invalid alignment "
            f"{alignment}"
        )

    relocation_sections = [
        section
        for section in sections
        if int(section["type"]) in (SHT_REL, SHT_RELA)
        and int(section["info"]) == section_index
        and int(section["size"])
    ]
    if relocation_sections:
        names = ", ".join(str(section["name"]) for section in relocation_sections)
        raise BuildError(
            f"isolated leaf {function_name} has relocations in {names}; "
            "only dependency-free function sections can be imported"
        )

    symbols = parse_elf32_symbols(data, sections)
    matches = [
        symbol
        for symbol in symbols
        if symbol["name"] == function_name
        and int(symbol["type"]) == STT_FUNC
    ]
    if len(matches) != 1:
        raise BuildError(
            f"expected one function symbol {function_name!r}, "
            f"observed {len(matches)}"
        )
    symbol = matches[0]
    if int(symbol["section_index"]) != section_index:
        raise BuildError(
            f"isolated leaf symbol {function_name} is not defined in "
            f"{section_name}"
        )
    if int(symbol["binding"]) != STB_GLOBAL or int(symbol["visibility"]) != 0:
        raise BuildError(
            f"isolated leaf symbol {function_name} must be global with default "
            "visibility"
        )
    symbol_offset = int(symbol["value"]) & ~1
    symbol_size = int(symbol["size"])
    if not int(symbol["value"]) & 1:
        raise BuildError(f"isolated leaf symbol {function_name} is not Thumb code")
    if symbol_offset != 0 or symbol_size != section_size:
        raise BuildError(
            f"isolated leaf symbol {function_name} does not occupy its whole "
            f"section: offset={symbol_offset}, symbol_size={symbol_size}, "
            f"section_size={section_size}"
        )

    start = int(function_section["offset"])
    leaf = data[start:start + section_size]
    discarded_alloc_sections = [
        {
            "name": str(section["name"]),
            "size": int(section["size"]),
            "flags": int(section["flags"]),
        }
        for section in sections
        if int(section["index"]) != section_index
        and int(section["flags"]) & SHF_ALLOC
        and int(section["size"])
    ]
    return (
        leaf,
        {
            "function": function_name,
            "section": section_name,
            "size": len(leaf),
            "sha256": sha256(leaf),
            "alignment": alignment,
            "relocation_count": 0,
            "discarded_alloc_section_count": len(discarded_alloc_sections),
            "discarded_alloc_section_bytes": sum(
                int(section["size"]) for section in discarded_alloc_sections
            ),
            "discarded_alloc_sections": discarded_alloc_sections,
        },
    )


def compile_isolated_leaf(
    *,
    root: Path,
    clang: str,
    leaf_config: dict[str, Any],
    object_path: Path,
    toolchain_profile: str | None = None,
    record: bool = False,
) -> tuple[bytes, dict[str, Any]]:
    """Compile an authenticated upstream TU and retain one reviewed leaf."""

    function_name = leaf_config.get("function")
    if not isinstance(function_name, str):
        raise BuildError("isolated leaf requires a function name")
    leaf_config = resolve_leaf_profile(
        leaf_config, toolchain_profile, record=record
    )
    source_config = leaf_config.get("source")
    if not isinstance(source_config, dict):
        raise BuildError(f"isolated leaf {function_name} requires a source record")
    source_relative = source_config.get("path")
    source_pin = source_config.get("sha256")
    if not isinstance(source_relative, str) or not source_relative:
        raise BuildError(f"isolated leaf {function_name} requires source.path")
    if not isinstance(source_pin, str) or not re.fullmatch(
        r"[0-9a-f]{64}",
        source_pin,
    ):
        raise BuildError(
            f"isolated leaf {function_name} requires a lowercase source SHA-256"
        )
    source_path = resolve_below(root, source_relative)
    source = source_path.read_bytes()
    source_digest = sha256(source)
    if source_digest != source_pin:
        raise BuildError(
            f"{source_relative}: isolated leaf source SHA-256 differs from config"
        )

    toolchain = leaf_config.get("toolchain")
    if not isinstance(toolchain, dict):
        raise BuildError(f"isolated leaf {function_name} requires a toolchain")
    target = toolchain.get("target")
    flags = toolchain.get("flags")
    if not isinstance(target, str) or not target:
        raise BuildError(
            f"isolated leaf {function_name} requires toolchain.target"
        )
    if (
        not isinstance(flags, list)
        or any(not isinstance(flag, str) or not flag for flag in flags)
    ):
        raise BuildError(
            f"isolated leaf {function_name} toolchain.flags must be strings"
        )
    if "-ffunction-sections" not in flags:
        raise BuildError(
            f"isolated leaf {function_name} requires -ffunction-sections"
        )
    if "-fdata-sections" not in flags:
        raise BuildError(
            f"isolated leaf {function_name} requires -fdata-sections"
        )
    if "-fno-function-sections" in flags or any(
        flag == "-flto" or flag.startswith("-flto=") for flag in flags
    ):
        raise BuildError(
            f"isolated leaf {function_name} cannot disable function sections "
            "or use LTO"
        )

    include_dirs, normalized_include_dirs = resolve_toolchain_include_dirs(
        root,
        toolchain,
    )
    version = compiler_version(clang)
    validate_compiler_version(toolchain, version)
    command = [
        clang,
        f"--target={target}",
        *flags,
    ]
    for include_dir in include_dirs:
        command.extend(("-I", str(include_dir)))
    command.extend(("-c", str(source_path), "-o", str(object_path)))
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode:
        raise BuildError(
            f"isolated leaf {function_name} compilation failed:\n"
            + (completed.stderr.strip() or completed.stdout.strip())
        )

    leaf, extraction = extract_isolated_function_section(
        object_path,
        function_name,
    )
    expected = leaf_config.get("expected")
    if not isinstance(expected, dict):
        raise BuildError(
            f"isolated leaf {function_name} requires expected output pins"
        )
    expected_size = expected.get("size")
    expected_sha256 = expected.get("sha256")
    if (
        not isinstance(expected_size, int)
        or expected_size < 1
        or not isinstance(expected_sha256, str)
        or not re.fullmatch(r"[0-9a-f]{64}", expected_sha256)
    ):
        raise BuildError(
            f"isolated leaf {function_name} expected pins require size and "
            "lowercase SHA-256"
        )
    if not record and (
        len(leaf) != expected_size or sha256(leaf) != expected_sha256
    ):
        raise BuildError(
            f"isolated leaf {function_name} output differs from reviewed pins: "
            f"expected {expected_size} bytes/{expected_sha256}, observed "
            f"{len(leaf)} bytes/{sha256(leaf)}"
        )

    source_record: dict[str, Any] = {
        "path": source_path.relative_to(root.resolve()).as_posix(),
        "size": len(source),
        "sha256": source_digest,
    }
    for key in (
        "license",
        "origin",
        "upstream",
        "upstream_commit",
        "evidence",
    ):
        if key in source_config:
            source_record[key] = source_config[key]
    toolchain_record: dict[str, Any] = {
        "executable": clang,
        "version": version,
        "target": target,
        "flags": flags,
    }
    if normalized_include_dirs is not None:
        toolchain_record["include_dirs"] = normalized_include_dirs
    return (
        leaf,
        {
            "source": source_record,
            "toolchain": toolchain_record,
            "extraction": extraction,
            "pins": {"size": len(leaf), "sha256": sha256(leaf)},
        },
    )


def extract_in_place_function_section(
    object_path: Path,
    function_name: str,
    *,
    runtime_address: int,
    relocation_configs: list[dict[str, Any]],
    record: bool = False,
    allowed_defined_relocation_targets: frozenset[str] = frozenset(),
    thumb_prel_symbols: frozenset[str] = frozenset(),
    strict_relocation_contract: bool = False,
    allow_local_function: bool = False,
    allow_local_relocation_targets: bool = False,
) -> tuple[bytes, dict[str, Any]]:
    """Extract and relocate one reviewed function for its fixed stock address."""

    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", function_name):
        raise BuildError("in-place leaf function must be a C identifier")
    if not isinstance(strict_relocation_contract, bool):
        raise BuildError(
            f"in-place leaf {function_name} strict_relocation_contract must "
            "be boolean"
        )
    if not isinstance(allow_local_function, bool):
        raise BuildError(
            f"in-place leaf {function_name} allow_local_function must be boolean"
        )
    if not isinstance(allow_local_relocation_targets, bool):
        raise BuildError(
            f"in-place leaf {function_name} "
            "allow_local_relocation_targets must be boolean"
        )
    if (
        not isinstance(runtime_address, int)
        or runtime_address < 0
        or runtime_address > 0xFFFFFFFF
        or runtime_address & 1
    ):
        raise BuildError(
            f"in-place leaf {function_name} runtime_address must be a "
            "nonnegative halfword-aligned integer"
        )
    if (
        not isinstance(relocation_configs, list)
        or any(not isinstance(item, dict) for item in relocation_configs)
    ):
        raise BuildError(
            f"in-place leaf {function_name} relocations must be a list "
            "of records"
        )

    allowed_fields = {
        "offset",
        "type",
        "symbol",
        "target_address",
        "target_expected_hex",
        "symbol_type",
    }
    reviewed_relocations: list[dict[str, Any]] = []
    reviewed_offsets: list[int] = []
    for index, relocation in enumerate(relocation_configs):
        unknown_fields = set(relocation) - allowed_fields
        if unknown_fields:
            raise BuildError(
                f"in-place leaf {function_name} relocation {index} has "
                f"unknown fields {sorted(unknown_fields)}"
            )
        offset = relocation.get("offset")
        relocation_name = relocation.get("type")
        symbol = relocation.get("symbol")
        target_address = relocation.get("target_address")
        symbol_type = relocation.get("symbol_type")
        if not isinstance(offset, int) or offset < 0 or offset & 1:
            raise BuildError(
                f"in-place leaf {function_name} relocation {index} offset "
                "must be a nonnegative halfword-aligned integer"
            )
        if relocation_name not in IN_PLACE_RELOCATION_TYPES:
            raise BuildError(
                f"in-place leaf {function_name} relocation {index} has "
                f"unsupported type {relocation_name!r}"
            )
        if not isinstance(symbol, str) or not re.fullmatch(
            r"[A-Za-z_][A-Za-z0-9_]*",
            symbol,
        ):
            raise BuildError(
                f"in-place leaf {function_name} relocation {index} "
                "requires a C-identifier symbol"
            )
        if (
            not isinstance(target_address, int)
            or target_address < 0
            or target_address > 0xFFFFFFFF
        ):
            raise BuildError(
                f"in-place leaf {function_name} relocation {index} "
                "requires a nonnegative target_address"
            )
        if strict_relocation_contract:
            if symbol_type not in STRICT_EXTERNAL_SYMBOL_TYPES:
                raise BuildError(
                    f"in-place leaf {function_name} relocation {index} strict "
                    "contract requires an exact symbol_type"
                )
        elif symbol_type is not None:
            raise BuildError(
                f"in-place leaf {function_name} relocation {index} "
                "symbol_type requires strict_relocation_contract"
            )

        target_expected_hex = relocation.get("target_expected_hex")
        if relocation_name == "R_ARM_THM_PC8":
            if target_address & 3:
                raise BuildError(
                    f"in-place leaf {function_name} relocation {index} "
                    "PC8 target must be word aligned"
                )
            if (
                not isinstance(target_expected_hex, str)
                or not re.fullmatch(r"[0-9a-fA-F]{8}", target_expected_hex)
            ):
                raise BuildError(
                    f"in-place leaf {function_name} relocation {index} "
                    "PC8 target requires exactly four expected literal bytes"
                )
            target_expected_hex = target_expected_hex.lower()
        elif relocation_name not in ABSOLUTE_MOVWT_TYPES:
            if target_address & 1:
                raise BuildError(
                    f"in-place leaf {function_name} relocation {index} "
                    "Thumb target must be halfword aligned"
                )
        if relocation_name != "R_ARM_THM_PC8" and target_expected_hex is not None:
            raise BuildError(
                f"in-place leaf {function_name} relocation {index} "
                "target_expected_hex is only valid for PC8 literals"
            )

        reviewed_offsets.append(offset)
        reviewed_relocations.append(
            {
                "offset": offset,
                "type": relocation_name,
                "type_id": IN_PLACE_RELOCATION_TYPES[relocation_name],
                "symbol": symbol,
                "target_address": target_address,
                **(
                    {"symbol_type": symbol_type}
                    if symbol_type is not None
                    else {}
                ),
                **(
                    {"target_expected_hex": target_expected_hex}
                    if target_expected_hex is not None
                    else {}
                ),
            }
        )

    if reviewed_offsets != sorted(reviewed_offsets):
        raise BuildError(
            f"in-place leaf {function_name} relocations must be ordered "
            "by offset"
        )
    if len(set(reviewed_offsets)) != len(reviewed_offsets):
        raise BuildError(
            f"in-place leaf {function_name} has duplicate relocation offsets"
        )
    validate_absolute_movwt_pairs(
        reviewed_relocations,
        context=f"in-place leaf {function_name}",
    )

    data, sections = parse_elf32(object_path)
    section_name = f".text.{function_name}"
    function_section = section_named(sections, section_name)
    section_index = int(function_section["index"])
    flags = int(function_section["flags"])
    if (
        int(function_section["type"]) != SHT_PROGBITS
        or flags & (SHF_ALLOC | SHF_EXECINSTR) != (SHF_ALLOC | SHF_EXECINSTR)
        or flags & SHF_WRITE
    ):
        raise BuildError(
            f"in-place leaf section {section_name} is not read-only "
            "executable PROGBITS"
        )
    section_size = int(function_section["size"])
    if section_size < 1 or section_size & 1:
        raise BuildError(
            f"in-place leaf section {section_name} must have a positive "
            "even size"
        )
    alignment = int(function_section["alignment"])
    if alignment < 1 or alignment & (alignment - 1):
        raise BuildError(
            f"in-place leaf section {section_name} has invalid alignment "
            f"{alignment}"
        )
    if runtime_address % alignment:
        raise BuildError(
            f"in-place leaf {function_name} runtime address "
            f"0x{runtime_address:08X} violates section alignment {alignment}"
        )

    symbols = parse_elf32_symbols(data, sections)
    matches = [
        symbol
        for symbol in symbols
        if symbol["name"] == function_name
        and int(symbol["type"]) == STT_FUNC
    ]
    if len(matches) != 1:
        raise BuildError(
            f"expected one function symbol {function_name!r}, "
            f"observed {len(matches)}"
        )
    function_symbol = matches[0]
    if int(function_symbol["section_index"]) != section_index:
        raise BuildError(
            f"in-place leaf symbol {function_name} is not defined in "
            f"{section_name}"
        )
    allowed_bindings = {STB_GLOBAL, STB_LOCAL} if allow_local_function else {STB_GLOBAL}
    if (
        int(function_symbol["binding"]) not in allowed_bindings
        or int(function_symbol["visibility"]) != 0
    ):
        raise BuildError(
            f"in-place leaf symbol {function_name} must have a reviewed "
            "binding with default visibility"
        )
    symbol_offset = int(function_symbol["value"]) & ~1
    symbol_size = int(function_symbol["size"])
    if not int(function_symbol["value"]) & 1:
        raise BuildError(f"in-place leaf symbol {function_name} is not Thumb code")
    if symbol_offset != 0 or symbol_size != section_size:
        raise BuildError(
            f"in-place leaf symbol {function_name} does not occupy its whole "
            f"section: offset={symbol_offset}, symbol_size={symbol_size}, "
            f"section_size={section_size}"
        )

    relocation_sections = [
        section
        for section in sections
        if int(section["type"]) in (SHT_REL, SHT_RELA)
        and int(section["info"]) == section_index
    ]
    rela_sections = [
        section
        for section in relocation_sections
        if int(section["type"]) == SHT_RELA
    ]
    if rela_sections:
        raise BuildError(
            f"in-place leaf {function_name} uses unsupported RELA "
            f"relocations in {', '.join(str(item['name']) for item in rela_sections)}"
        )

    observed_relocations: list[dict[str, Any]] = []
    relocation_names_by_id = {
        value: name for name, value in IN_PLACE_RELOCATION_TYPES.items()
    }
    for relocation_section in relocation_sections:
        if not int(relocation_section["size"]):
            continue
        entry_size = int(relocation_section["entry_size"])
        if entry_size != 8 or int(relocation_section["size"]) % entry_size:
            raise BuildError(
                f"invalid relocation table {relocation_section['name']}"
            )
        count = int(relocation_section["size"]) // entry_size
        for index in range(count):
            entry = int(relocation_section["offset"]) + index * entry_size
            offset, info = struct.unpack_from("<II", data, entry)
            relocation_type = info & 0xFF
            symbol_index = info >> 8
            if symbol_index >= len(symbols):
                raise BuildError("relocation references an invalid symbol")
            relocation_symbol = symbols[symbol_index]
            relocation_name = relocation_names_by_id.get(relocation_type)
            if relocation_name is None:
                raise BuildError(
                    f"in-place leaf {function_name} has unsupported "
                    f"relocation type {relocation_type} at +0x{offset:X}"
                )
            is_global_undefined = (
                int(relocation_symbol["section_index"]) == 0
                and int(relocation_symbol["binding"]) == STB_GLOBAL
            )
            is_reviewed_defined_sibling = False
            relocation_symbol_name = str(relocation_symbol["name"])
            if (
                not is_global_undefined
                and relocation_symbol_name
                in allowed_defined_relocation_targets
            ):
                sibling_section_index = int(
                    relocation_symbol["section_index"]
                )
                if 0 < sibling_section_index < len(sections):
                    sibling_section = sections[sibling_section_index]
                    sibling_offset = int(relocation_symbol["value"]) & ~1
                    sibling_size = int(relocation_symbol["size"])
                    sibling_section_size = int(sibling_section["size"])
                    is_reviewed_defined_sibling = (
                        int(relocation_symbol["binding"])
                        in (
                            (STB_GLOBAL, STB_LOCAL)
                            if allow_local_relocation_targets
                            else (STB_GLOBAL,)
                        )
                        and int(relocation_symbol["visibility"]) == 0
                        and int(relocation_symbol["type"]) == STT_FUNC
                        and sibling_section_index != section_index
                        and int(sibling_section["flags"])
                        & (SHF_ALLOC | SHF_EXECINSTR)
                        == (SHF_ALLOC | SHF_EXECINSTR)
                        and str(sibling_section["name"])
                        == f".text.{relocation_symbol_name}"
                        and bool(int(relocation_symbol["value"]) & 1)
                        and sibling_offset == 0
                        and sibling_size == sibling_section_size
                    )
            if relocation_name in ABSOLUTE_MOVWT_TYPES:
                is_reviewed_defined_sibling = False
            if not is_global_undefined and not is_reviewed_defined_sibling:
                raise BuildError(
                    f"in-place leaf {function_name} relocation at "
                    f"+0x{offset:X} must reference a global undefined symbol "
                    "or an explicitly selected whole global sibling function; "
                    f"observed {relocation_symbol['name']!r}"
                )
            observed_relocations.append(
                {
                    "offset": offset,
                    "type": relocation_name,
                    "type_id": relocation_type,
                    "symbol": str(relocation_symbol["name"]),
                    "_symbol_type": int(relocation_symbol["type"]),
                    "_symbol_binding": int(relocation_symbol["binding"]),
                    "_symbol_visibility": int(relocation_symbol["visibility"]),
                }
            )

    if strict_relocation_contract:
        observed_sorted_for_contract = sorted(
            observed_relocations,
            key=lambda item: item["offset"],
        )
        if len(observed_sorted_for_contract) != len(reviewed_relocations):
            raise BuildError(
                f"in-place leaf {function_name} strict external symbol "
                "metadata count differs from reviewed relocations"
            )
        for reviewed, observed in zip(
            reviewed_relocations,
            observed_sorted_for_contract,
        ):
            if (
                observed["_symbol_binding"] != STB_GLOBAL
                or observed["_symbol_visibility"] != 0
                or observed["_symbol_type"]
                != STRICT_EXTERNAL_SYMBOL_TYPES[reviewed["symbol_type"]]
            ):
                raise BuildError(
                    f"in-place leaf {function_name} strict external symbol "
                    f"metadata differs for {observed['symbol']!r}: expected "
                    f"global/default/{reviewed['symbol_type']}"
                )
    for observed in observed_relocations:
        observed.pop("_symbol_type", None)
        observed.pop("_symbol_binding", None)
        observed.pop("_symbol_visibility", None)

    if record:
        # Under an alternate toolchain the outgoing-call *offsets* within the
        # leaf may shift, but the ordered (type, symbol) call sequence is fixed
        # by the source.  Adopt the observed offsets while keeping each reviewed
        # target, so the leaf is relocated correctly and the observed offsets
        # can be recorded as this profile's relocation pins.  A changed call
        # sequence is still a hard error.
        reviewed_signature = [
            (item["type"], item["symbol"]) for item in reviewed_relocations
        ]
        observed_sorted = sorted(
            observed_relocations, key=lambda item: item["offset"]
        )
        observed_signature = [
            (item["type"], item["symbol"]) for item in observed_sorted
        ]
        if observed_signature != reviewed_signature:
            raise BuildError(
                f"in-place leaf {function_name} outgoing-call sequence differs "
                f"under this toolchain: expected {reviewed_signature}, observed "
                f"{observed_signature}"
            )
        for reviewed, observed in zip(reviewed_relocations, observed_sorted):
            reviewed["offset"] = int(observed["offset"])
        reviewed_offsets = [item["offset"] for item in reviewed_relocations]
        if reviewed_offsets != sorted(reviewed_offsets) or len(
            set(reviewed_offsets)
        ) != len(reviewed_offsets):
            raise BuildError(
                f"in-place leaf {function_name} observed relocation offsets are "
                "not strictly ordered"
            )
        validate_absolute_movwt_pairs(
            reviewed_relocations,
            context=f"in-place leaf {function_name}",
        )
        validate_prel_movwt_pairs(
            reviewed_relocations,
            context=f"in-place leaf {function_name}",
        )
    else:
        # Relocations apply independently at their own offsets, so the ELF
        # relocation-table order is not semantically meaningful and varies by
        # assembler.  Compare the full (offset, type, symbol) set ordered by
        # offset: identity is still fully verified, only table order is
        # normalized.
        expected_identity = sorted(
            (item["offset"], item["type"], item["symbol"])
            for item in reviewed_relocations
        )
        observed_identity = sorted(
            (item["offset"], item["type"], item["symbol"])
            for item in observed_relocations
        )
        if observed_identity != expected_identity:
            raise BuildError(
                f"in-place leaf {function_name} relocation list differs from "
                f"reviewed config: expected {expected_identity}, "
                f"observed {observed_identity}"
            )
        validate_absolute_movwt_pairs(
            reviewed_relocations,
            context=f"in-place leaf {function_name}",
        )
        validate_prel_movwt_pairs(
            reviewed_relocations,
            context=f"in-place leaf {function_name}",
        )

    start = int(function_section["offset"])
    leaf = bytearray(data[start:start + section_size])
    unrelocated_sha256 = sha256(bytes(leaf))
    prel_pair_details: dict[int, dict[str, int | str]] = {}
    for index, relocation in enumerate(reviewed_relocations):
        if relocation["type"] != "R_ARM_THM_MOVW_PREL_NC":
            continue
        partner = reviewed_relocations[index + 1]
        low_offset = int(relocation["offset"])
        high_offset = int(partner["offset"])
        target_address = int(relocation["target_address"])
        details = resolve_prel_movwt_pair(
            leaf,
            low_offset,
            (target_address - runtime_address) & 0xFFFFFFFF,
            high_site=high_offset,
            symbol_thumb=(
                relocation.get("symbol_type") == "STT_FUNC"
                or relocation.get("symbol") in thumb_prel_symbols
            ),
        )
        prel_pair_details[low_offset] = details
        prel_pair_details[high_offset] = details
    resolved_relocations: list[dict[str, Any]] = []
    for relocation in reviewed_relocations:
        offset = int(relocation["offset"])
        relocation_name = str(relocation["type"])
        site_address = runtime_address + offset
        target_address = int(relocation["target_address"])
        if relocation_name == "R_ARM_THM_PC8":
            if offset + 2 > len(leaf):
                raise BuildError(
                    f"in-place leaf {function_name} PC8 relocation at "
                    f"+0x{offset:X} exceeds its section"
                )
            instruction = struct.unpack_from("<H", leaf, offset)[0]
            if instruction & 0xF800 != 0x4800 or instruction & 0x00FF:
                raise BuildError(
                    f"in-place leaf {function_name} PC8 relocation at "
                    f"+0x{offset:X} requires a canonical narrow LDR literal "
                    "with a zero addend"
                )
            pc_base = (site_address + 4) & ~3
            displacement = target_address - pc_base
            if displacement < 0 or displacement > 1020 or displacement & 3:
                raise BuildError(
                    f"in-place leaf {function_name} PC8 target "
                    f"0x{target_address:08X} is outside its aligned "
                    "0..1020-byte range"
                )
            struct.pack_into(
                "<H",
                leaf,
                offset,
                instruction | (displacement >> 2),
            )
        elif relocation_name in ABSOLUTE_MOVWT_TYPES:
            if offset + 4 > len(leaf):
                raise BuildError(
                    f"in-place leaf {function_name} absolute MOVW/MOVT "
                    f"relocation at +0x{offset:X} exceeds its section"
                )
            resolve_absolute_movwt(
                leaf,
                offset,
                target_address,
                high=relocation_name == "R_ARM_THM_MOVT_ABS",
            )
        elif relocation_name in PREL_MOVWT_TYPES:
            if offset + 4 > len(leaf):
                raise BuildError(
                    f"in-place leaf {function_name} PREL MOVW/MOVT "
                    f"relocation at +0x{offset:X} exceeds its section"
                )
            if offset not in prel_pair_details:
                raise BuildError(
                    f"in-place leaf {function_name} has an unpaired PREL "
                    f"relocation at +0x{offset:X}"
                )
        else:
            if offset + 4 > len(leaf):
                raise BuildError(
                    f"in-place leaf {function_name} branch relocation at "
                    f"+0x{offset:X} exceeds its section"
                )
            link = relocation_name == "R_ARM_THM_CALL"
            canonical = encode_thumb_branch(0, 0, link=link)
            if bytes(leaf[offset:offset + 4]) != canonical:
                raise BuildError(
                    f"in-place leaf {function_name} {relocation_name} at "
                    f"+0x{offset:X} does not use the canonical zero-symbol "
                    "REL placeholder"
                )
            leaf[offset:offset + 4] = encode_thumb_branch(
                site_address,
                target_address,
                link=link,
            )
        resolved_relocations.append(
            {
                **relocation,
                "runtime_address": site_address,
                "runtime_address_hex": f"0x{site_address:08X}",
                "target_address_hex": f"0x{target_address:08X}",
                **prel_pair_details.get(offset, {}),
            }
        )

    discarded_alloc_sections = [
        {
            "name": str(section["name"]),
            "size": int(section["size"]),
            "flags": int(section["flags"]),
        }
        for section in sections
        if int(section["index"]) != section_index
        and int(section["flags"]) & SHF_ALLOC
        and int(section["size"])
    ]
    authenticated_cantunwind_indexes = (
        authenticated_cantunwind_companion_indexes(
            data,
            sections,
            symbols,
            function_section,
        )
        if strict_relocation_contract
        else frozenset()
    )
    authenticated_cantunwind_discards = [
        {
            "name": str(section["name"]),
            "size": int(section["size"]),
            "policy": (
                "authenticated selected-function CANTUNWIND/R_ARM_PREL31 "
                "metadata deliberately discarded, not executable closure data"
            ),
        }
        for section in sections
        if int(section["index"]) in authenticated_cantunwind_indexes
    ]
    unexpected_alloc_sections = [
        section for section in sections
        if int(section["index"]) != section_index
        and int(section["flags"]) & SHF_ALLOC
        and int(section["size"])
        and int(section["index"]) not in authenticated_cantunwind_indexes
    ]
    if strict_relocation_contract and unexpected_alloc_sections:
        raise BuildError(
            f"in-place leaf {function_name} strict relocation contract rejects "
            "unexpected allocated sections: "
            + ", ".join(
                str(section["name"]) for section in unexpected_alloc_sections
            )
        )
    return (
        bytes(leaf),
        {
            "function": function_name,
            "section": section_name,
            "runtime_address": runtime_address,
            "runtime_address_hex": f"0x{runtime_address:08X}",
            "size": len(leaf),
            "sha256": sha256(leaf),
            "unrelocated_sha256": unrelocated_sha256,
            "alignment": alignment,
            "relocation_count": len(resolved_relocations),
            "relocations": resolved_relocations,
            "discarded_alloc_section_count": len(discarded_alloc_sections),
            "discarded_alloc_section_bytes": sum(
                int(section["size"]) for section in discarded_alloc_sections
            ),
            "discarded_alloc_sections": discarded_alloc_sections,
            "authenticated_cantunwind_discard_count": len(
                authenticated_cantunwind_discards
            ),
            "authenticated_cantunwind_discards": (
                authenticated_cantunwind_discards
            ),
        },
    )


def extract_relocated_function_closure(
    object_path: Path,
    function_name: str,
    *,
    runtime_address: int,
    closure_config: dict[str, Any],
    relocation_configs: list[dict[str, Any]],
    record: bool = False,
    strict_relocation_contract: bool = False,
    allow_local_function: bool = False,
    allowed_defined_relocation_targets: frozenset[str] = frozenset(),
    allow_local_relocation_targets: bool = False,
) -> tuple[bytes, dict[str, Any]]:
    """Extract one function plus one authenticated read-only-data closure.

    This is intentionally narrower than a general ELF linker.  The caller
    names the exact executable and read-only sections, every object retained
    from the latter, every relocation applied to the former, and every fixed
    external Thumb target.  Anything outside that closed allow-list is either
    discarded as unrelated or rejected if the selected function depends on it.
    """

    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", function_name):
        raise BuildError("relocated closure function must be a C identifier")
    if not isinstance(strict_relocation_contract, bool):
        raise BuildError(
            f"relocated closure {function_name} strict_relocation_contract "
            "must be boolean"
        )
    if not isinstance(allow_local_function, bool):
        raise BuildError(
            f"relocated closure {function_name} allow_local_function must be boolean"
        )
    if not isinstance(allow_local_relocation_targets, bool):
        raise BuildError(
            f"relocated closure {function_name} "
            "allow_local_relocation_targets must be boolean"
        )
    if (
        not isinstance(runtime_address, int)
        or runtime_address < 0
        or runtime_address > 0xFFFFFFFF
        or runtime_address & 1
    ):
        raise BuildError(
            f"relocated closure {function_name} runtime_address must be a "
            "nonnegative halfword-aligned integer"
        )
    if not isinstance(closure_config, dict):
        raise BuildError(f"relocated closure {function_name} must be an object")
    unknown_closure_fields = set(closure_config) - {"text_section", "rodata"}
    if unknown_closure_fields:
        raise BuildError(
            f"relocated closure {function_name} has unknown fields "
            f"{sorted(unknown_closure_fields)}"
        )
    text_section_name = closure_config.get("text_section")
    rodata_config = closure_config.get("rodata")
    if not isinstance(text_section_name, str) or not text_section_name:
        raise BuildError(
            f"relocated closure {function_name} requires text_section"
        )
    if not isinstance(rodata_config, dict):
        raise BuildError(f"relocated closure {function_name} requires rodata")
    unknown_rodata_fields = set(rodata_config) - {
        "section",
        "size",
        "sha256",
        "alignment",
        "symbols",
    }
    if unknown_rodata_fields:
        raise BuildError(
            f"relocated closure {function_name} rodata has unknown fields "
            f"{sorted(unknown_rodata_fields)}"
        )
    rodata_section_name = rodata_config.get("section")
    rodata_size_pin = rodata_config.get("size")
    rodata_sha256_pin = rodata_config.get("sha256")
    rodata_alignment_pin = rodata_config.get("alignment")
    symbol_configs = rodata_config.get("symbols")
    if not isinstance(rodata_section_name, str) or not rodata_section_name:
        raise BuildError(
            f"relocated closure {function_name} rodata requires section"
        )
    if (
        not isinstance(rodata_size_pin, int)
        or rodata_size_pin < 1
        or not isinstance(rodata_sha256_pin, str)
        or not re.fullmatch(r"[0-9a-f]{64}", rodata_sha256_pin)
        or not isinstance(rodata_alignment_pin, int)
        or rodata_alignment_pin < 1
        or rodata_alignment_pin & (rodata_alignment_pin - 1)
    ):
        raise BuildError(
            f"relocated closure {function_name} rodata requires positive "
            "size, lowercase SHA-256, and power-of-two alignment"
        )
    if (
        not isinstance(symbol_configs, list)
        or not symbol_configs
        or any(not isinstance(item, dict) for item in symbol_configs)
    ):
        raise BuildError(
            f"relocated closure {function_name} rodata symbols must be a "
            "nonempty list of records"
        )
    reviewed_symbols: list[dict[str, Any]] = []
    for index, item in enumerate(symbol_configs):
        unknown_fields = set(item) - {"name", "offset", "size"}
        if unknown_fields:
            raise BuildError(
                f"relocated closure {function_name} rodata symbol {index} "
                f"has unknown fields {sorted(unknown_fields)}"
            )
        name = item.get("name")
        offset = item.get("offset")
        size = item.get("size")
        if not isinstance(name, str) or not (
            re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name)
            or re.fullmatch(r"\.L\.str(?:\.[0-9]+)?", name)
        ):
            raise BuildError(
                f"relocated closure {function_name} rodata symbol {index} "
                "requires a C identifier or Clang .L.str[.N] local name"
            )
        if (
            not isinstance(offset, int)
            or offset < 0
            or not isinstance(size, int)
            or size < 1
            or offset + size > rodata_size_pin
        ):
            raise BuildError(
                f"relocated closure {function_name} rodata symbol {name} "
                "has an invalid pinned span"
            )
        reviewed_symbols.append({"name": name, "offset": offset, "size": size})
    if [item["offset"] for item in reviewed_symbols] != sorted(
        item["offset"] for item in reviewed_symbols
    ):
        raise BuildError(
            f"relocated closure {function_name} rodata symbols must be "
            "ordered by offset"
        )
    if len({item["name"] for item in reviewed_symbols}) != len(reviewed_symbols):
        raise BuildError(
            f"relocated closure {function_name} has duplicate rodata symbols"
        )
    cursor = 0
    for item in reviewed_symbols:
        if item["offset"] != cursor:
            raise BuildError(
                f"relocated closure {function_name} rodata symbols must "
                "exactly cover the pinned section"
            )
        cursor += item["size"]
    if cursor != rodata_size_pin:
        raise BuildError(
            f"relocated closure {function_name} rodata symbols must exactly "
            "cover the pinned section"
        )

    if (
        not isinstance(relocation_configs, list)
        or any(not isinstance(item, dict) for item in relocation_configs)
    ):
        raise BuildError(
            f"relocated closure {function_name} relocations must be a list "
            "of records"
        )
    relocation_types = {
        "R_ARM_REL32": R_ARM_REL32,
        "R_ARM_THM_CALL": R_ARM_THM_CALL,
        "R_ARM_THM_JUMP24": R_ARM_THM_JUMP24,
        "R_ARM_THM_MOVW_ABS_NC": R_ARM_THM_MOVW_ABS_NC,
        "R_ARM_THM_MOVT_ABS": R_ARM_THM_MOVT_ABS,
        "R_ARM_THM_MOVW_PREL_NC": R_ARM_THM_MOVW_PREL_NC,
        "R_ARM_THM_MOVT_PREL": R_ARM_THM_MOVT_PREL,
    }
    external_branch_types = {"R_ARM_THM_CALL", "R_ARM_THM_JUMP24"}
    external_types = external_branch_types | ABSOLUTE_MOVWT_TYPES
    local_types = {
        "R_ARM_REL32",
        "R_ARM_THM_MOVW_PREL_NC",
        "R_ARM_THM_MOVT_PREL",
    }
    local_symbol_names = {item["name"] for item in reviewed_symbols}
    reviewed_relocations: list[dict[str, Any]] = []
    for index, item in enumerate(relocation_configs):
        unknown_fields = set(item) - {
            "offset",
            "type",
            "symbol",
            "target_address",
            "symbol_type",
        }
        if unknown_fields:
            raise BuildError(
                f"relocated closure {function_name} relocation {index} has "
                f"unknown fields {sorted(unknown_fields)}"
            )
        offset = item.get("offset")
        relocation_name = item.get("type")
        symbol = item.get("symbol")
        target_address = item.get("target_address")
        symbol_type = item.get("symbol_type")
        if not isinstance(offset, int) or offset < 0 or offset & 1:
            raise BuildError(
                f"relocated closure {function_name} relocation {index} "
                "offset must be a nonnegative halfword-aligned integer"
            )
        if relocation_name not in relocation_types:
            raise BuildError(
                f"relocated closure {function_name} relocation {index} has "
                f"unsupported type {relocation_name!r}"
            )
        if not isinstance(symbol, str) or not (
            re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", symbol)
            or symbol in local_symbol_names
        ):
            raise BuildError(
                f"relocated closure {function_name} relocation {index} "
                "requires a reviewed symbol name"
            )
        if relocation_name in external_types:
            if (
                not isinstance(target_address, int)
                or target_address < 0
                or target_address > 0xFFFFFFFF
            ):
                raise BuildError(
                    f"relocated closure {function_name} relocation {index} "
                    + (
                        "requires a fixed halfword-aligned target_address"
                        if relocation_name in external_branch_types
                        else "requires a fixed target_address"
                    )
                )
            if relocation_name in external_branch_types and target_address & 1:
                raise BuildError(
                    f"relocated closure {function_name} relocation {index} "
                    "requires a halfword-aligned branch target_address"
                )
            if symbol in local_symbol_names:
                raise BuildError(
                    f"relocated closure {function_name} relocation {index} "
                    "cannot call a local rodata symbol"
                )
            if strict_relocation_contract:
                if symbol_type not in STRICT_EXTERNAL_SYMBOL_TYPES:
                    raise BuildError(
                        f"relocated closure {function_name} relocation {index} "
                        "strict contract requires an exact symbol_type"
                    )
            elif symbol_type is not None:
                raise BuildError(
                    f"relocated closure {function_name} relocation {index} "
                    "symbol_type requires strict_relocation_contract"
                )
        else:
            if symbol not in local_symbol_names:
                raise BuildError(
                    f"relocated closure {function_name} relocation {index} "
                    f"references unlisted local symbol {symbol!r}"
                )
            if target_address is not None:
                raise BuildError(
                    f"relocated closure {function_name} relocation {index} "
                    "local table target_address is derived, not configurable"
                )
            if symbol_type is not None:
                raise BuildError(
                    f"relocated closure {function_name} relocation {index} "
                    "local symbol_type is derived, not configurable"
                )
        reviewed_relocations.append(
            {
                "offset": offset,
                "type": relocation_name,
                "type_id": relocation_types[relocation_name],
                "symbol": symbol,
                **(
                    {"target_address": target_address}
                    if relocation_name in external_types
                    else {}
                ),
                **(
                    {"symbol_type": symbol_type}
                    if symbol_type is not None
                    else {}
                ),
            }
        )
    reviewed_offsets = [item["offset"] for item in reviewed_relocations]
    if reviewed_offsets != sorted(reviewed_offsets):
        raise BuildError(
            f"relocated closure {function_name} relocations must be ordered "
            "by offset"
        )
    if len(set(reviewed_offsets)) != len(reviewed_offsets):
        raise BuildError(
            f"relocated closure {function_name} has duplicate relocation offsets"
        )
    validate_absolute_movwt_pairs(
        reviewed_relocations,
        context=f"relocated closure {function_name}",
    )
    validate_prel_movwt_pairs(
        reviewed_relocations,
        context=f"relocated closure {function_name}",
    )

    data, sections = parse_elf32(object_path)
    symbols = parse_elf32_symbols(data, sections)
    if record:
        function_symbols_for_record = [
            symbol
            for symbol in symbols
            if symbol["name"] == function_name
            and int(symbol["type"]) == STT_FUNC
            and int(symbol["section_index"]) != 0
        ]
        if len(function_symbols_for_record) != 1:
            raise BuildError(
                f"expected one defined function symbol {function_name!r} "
                f"while recording, observed {len(function_symbols_for_record)}"
            )
        recorded_section_index = int(
            function_symbols_for_record[0]["section_index"]
        )
        if recorded_section_index >= len(sections):
            raise BuildError(
                f"relocated closure {function_name} symbol references an "
                "invalid section"
            )
        function_section = sections[recorded_section_index]
        text_section_name = str(function_section["name"])
    else:
        try:
            function_section = section_named(sections, text_section_name)
        except BuildError as error:
            raise BuildError(
                f"relocated closure {function_name} {error}"
            ) from error
    function_section_index = int(function_section["index"])
    function_flags = int(function_section["flags"])
    if (
        int(function_section["type"]) != SHT_PROGBITS
        or function_flags & (SHF_ALLOC | SHF_EXECINSTR)
        != (SHF_ALLOC | SHF_EXECINSTR)
        or function_flags & SHF_WRITE
    ):
        raise BuildError(
            f"relocated closure section {text_section_name} is not read-only "
            "executable PROGBITS"
        )
    function_size = int(function_section["size"])
    function_alignment = int(function_section["alignment"])
    if function_size < 1 or function_size & 1:
        raise BuildError(
            f"relocated closure section {text_section_name} must have a "
            "positive even size"
        )
    if (
        function_alignment < 1
        or function_alignment & (function_alignment - 1)
        or runtime_address % function_alignment
    ):
        raise BuildError(
            f"relocated closure {function_name} has invalid or violated text "
            f"alignment {function_alignment}"
        )

    try:
        rodata_section = section_named(sections, rodata_section_name)
    except BuildError as error:
        raise BuildError(
            f"relocated closure {function_name} {error}"
        ) from error
    rodata_section_index = int(rodata_section["index"])
    if not is_rodata(rodata_section):
        raise BuildError(
            f"relocated closure section {rodata_section_name} is not "
            "read-only allocated PROGBITS"
        )
    rodata_start = int(rodata_section["offset"])
    rodata_bytes = data[rodata_start:rodata_start + int(rodata_section["size"])]
    if (
        len(rodata_bytes) != rodata_size_pin
        or sha256(rodata_bytes) != rodata_sha256_pin
        or int(rodata_section["alignment"]) != rodata_alignment_pin
    ):
        raise BuildError(
            f"relocated closure {function_name} rodata differs from reviewed "
            "size, SHA-256, or alignment pins"
        )

    function_matches = [
        symbol
        for symbol in symbols
        if symbol["name"] == function_name and int(symbol["type"]) == STT_FUNC
    ]
    if len(function_matches) != 1:
        raise BuildError(
            f"expected one function symbol {function_name!r}, observed "
            f"{len(function_matches)}"
        )
    function_symbol = function_matches[0]
    allowed_bindings = {STB_GLOBAL, STB_LOCAL} if allow_local_function else {STB_GLOBAL}
    if (
        int(function_symbol["section_index"]) != function_section_index
        or int(function_symbol["binding"]) not in allowed_bindings
        or int(function_symbol["visibility"]) != 0
        or not int(function_symbol["value"]) & 1
        or int(function_symbol["value"]) & ~1
        or int(function_symbol["size"]) != function_size
    ):
        raise BuildError(
            f"relocated closure function symbol {function_name} does not "
            "exactly occupy its reviewed Thumb section"
        )

    observed_rodata_symbols = []
    for symbol in symbols:
        if (
            int(symbol["section_index"]) != rodata_section_index
            or int(symbol["type"]) != STT_OBJECT
            or not symbol["name"]
        ):
            continue
        if (
            int(symbol["binding"]) != STB_LOCAL
            or int(symbol["visibility"]) != 0
        ):
            raise BuildError(
                f"relocated closure rodata symbol {symbol['name']!r} is not "
                "local with default visibility"
            )
        observed_rodata_symbols.append(
            {
                "name": str(symbol["name"]),
                "offset": int(symbol["value"]),
                "size": int(symbol["size"]),
            }
        )
    observed_rodata_symbols.sort(key=lambda item: item["offset"])
    if observed_rodata_symbols != reviewed_symbols:
        raise BuildError(
            f"relocated closure {function_name} rodata symbols differ from "
            f"reviewed config: expected {reviewed_symbols}, observed "
            f"{observed_rodata_symbols}"
        )

    selected_relocation_sections = [
        section
        for section in sections
        if int(section["type"]) in (SHT_REL, SHT_RELA)
        and int(section["info"]) in (function_section_index, rodata_section_index)
        and int(section["size"])
    ]
    rela_sections = [
        section
        for section in selected_relocation_sections
        if int(section["type"]) == SHT_RELA
    ]
    if rela_sections:
        raise BuildError(
            f"relocated closure {function_name} uses unsupported RELA "
            f"relocations in {', '.join(str(item['name']) for item in rela_sections)}"
        )
    rodata_relocations = [
        section
        for section in selected_relocation_sections
        if int(section["info"]) == rodata_section_index
    ]
    if rodata_relocations:
        raise BuildError(
            f"relocated closure {function_name} has unlisted rodata "
            f"relocations in {', '.join(str(item['name']) for item in rodata_relocations)}"
        )

    relocation_names_by_id = {
        value: name for name, value in relocation_types.items()
    }
    observed_relocations: list[dict[str, Any]] = []
    for relocation_section in selected_relocation_sections:
        if int(relocation_section["info"]) != function_section_index:
            continue
        entry_size = int(relocation_section["entry_size"])
        if entry_size != 8 or int(relocation_section["size"]) % entry_size:
            raise BuildError(f"invalid relocation table {relocation_section['name']}")
        for index in range(int(relocation_section["size"]) // entry_size):
            entry = int(relocation_section["offset"]) + index * entry_size
            offset, info = struct.unpack_from("<II", data, entry)
            relocation_type = info & 0xFF
            symbol_index = info >> 8
            if symbol_index >= len(symbols):
                raise BuildError("relocation references an invalid symbol")
            relocation_symbol = symbols[symbol_index]
            relocation_name = relocation_names_by_id.get(relocation_type)
            if relocation_name is None:
                raise BuildError(
                    f"relocated closure {function_name} has unsupported "
                    f"relocation type {relocation_type} at +0x{offset:X}"
                )
            symbol_name = str(relocation_symbol["name"])
            if relocation_name in external_types:
                is_exact_selected_function_self_call = (
                    relocation_name == "R_ARM_THM_CALL"
                    and symbol_name == function_name
                    and int(relocation_symbol["section_index"])
                    == function_section_index
                    and int(relocation_symbol["binding"]) == STB_GLOBAL
                    and int(relocation_symbol["visibility"]) == 0
                    and int(relocation_symbol["type"]) == STT_FUNC
                    and int(relocation_symbol["value"]) & ~1 == 0
                    and bool(int(relocation_symbol["value"]) & 1)
                    and int(relocation_symbol["size"]) == function_size
                    and any(
                        item["type"] == "R_ARM_THM_CALL"
                        and item["symbol"] == function_name
                        and item.get("target_address") == runtime_address
                        for item in reviewed_relocations
                    )
                    and all(
                        item.get("target_address") == runtime_address
                        for item in reviewed_relocations
                        if item["type"] == "R_ARM_THM_CALL"
                        and item["symbol"] == function_name
                    )
                )
                is_global_undefined = (
                    int(relocation_symbol["section_index"]) == 0
                    and int(relocation_symbol["binding"]) == STB_GLOBAL
                    and int(relocation_symbol["visibility"]) == 0
                    and symbol_name not in local_symbol_names
                )
                is_reviewed_defined_sibling = False
                if (
                    not is_global_undefined
                    and symbol_name in allowed_defined_relocation_targets
                ):
                    sibling_section_index = int(relocation_symbol["section_index"])
                    if 0 < sibling_section_index < len(sections):
                        sibling_section = sections[sibling_section_index]
                        is_reviewed_defined_sibling = (
                            int(relocation_symbol["binding"])
                            in (
                                (STB_GLOBAL, STB_LOCAL)
                                if allow_local_relocation_targets
                                else (STB_GLOBAL,)
                            )
                            and int(relocation_symbol["visibility"]) == 0
                            and int(relocation_symbol["type"]) == STT_FUNC
                            and sibling_section_index != function_section_index
                            and int(sibling_section["flags"]) & (SHF_ALLOC | SHF_EXECINSTR)
                            == (SHF_ALLOC | SHF_EXECINSTR)
                            and str(sibling_section["name"]) == f".text.{symbol_name}"
                            and bool(int(relocation_symbol["value"]) & 1)
                            and int(relocation_symbol["value"]) & ~1 == 0
                            and int(relocation_symbol["size"]) == int(sibling_section["size"])
                        )
                if (
                    not is_global_undefined
                    and not is_exact_selected_function_self_call
                    and not is_reviewed_defined_sibling
                ):
                    raise BuildError(
                        f"relocated closure {function_name} external relocation "
                        f"at +0x{offset:X} must reference an unlisted global "
                        "undefined symbol or its exact selected-function self-call"
                    )
            elif (
                int(relocation_symbol["section_index"]) != rodata_section_index
                or symbol_name not in local_symbol_names
            ):
                raise BuildError(
                    f"relocated closure {function_name} local relocation at "
                    f"+0x{offset:X} references unlisted section or symbol "
                    f"{symbol_name!r}"
                )
            observed_relocations.append(
                {
                    "offset": offset,
                    "type": relocation_name,
                    "type_id": relocation_type,
                    "symbol": symbol_name,
                    "_symbol_type": int(relocation_symbol["type"]),
                    "_symbol_binding": int(relocation_symbol["binding"]),
                    "_symbol_visibility": int(relocation_symbol["visibility"]),
                }
            )

    observed_sorted_for_contract = sorted(
        observed_relocations,
        key=lambda item: item["offset"],
    )
    if strict_relocation_contract:
        reviewed_external_for_contract = [
            item for item in reviewed_relocations if item["type"] in external_types
        ]
        observed_external_for_contract = [
            item
            for item in observed_sorted_for_contract
            if item["type"] in external_types
        ]
        if len(reviewed_external_for_contract) != len(
            observed_external_for_contract
        ):
            raise BuildError(
                f"relocated closure {function_name} strict external symbol "
                "metadata count differs from reviewed relocations"
            )
        for reviewed, observed in zip(
            reviewed_external_for_contract,
            observed_external_for_contract,
        ):
            if (
                (reviewed["type"], reviewed["symbol"])
                != (observed["type"], observed["symbol"])
                or observed["_symbol_binding"] != STB_GLOBAL
                or observed["_symbol_visibility"] != 0
                or observed["_symbol_type"]
                != STRICT_EXTERNAL_SYMBOL_TYPES[reviewed["symbol_type"]]
            ):
                raise BuildError(
                    f"relocated closure {function_name} strict external "
                    f"symbol metadata differs for {observed['symbol']!r}: "
                    f"expected global/default/{reviewed['symbol_type']}"
                )
    for observed in observed_relocations:
        observed.pop("_symbol_type", None)
        observed.pop("_symbol_binding", None)
        observed.pop("_symbol_visibility", None)

    if record:
        reviewed_signature = [
            (item["type"], item["symbol"])
            for item in reviewed_relocations
        ]
        observed_sorted = sorted(
            observed_relocations,
            key=lambda item: item["offset"],
        )
        observed_signature = [
            (item["type"], item["symbol"])
            for item in observed_sorted
        ]
        if observed_signature != reviewed_signature:
            raise BuildError(
                f"relocated closure {function_name} relocation sequence "
                f"differs under this toolchain: expected {reviewed_signature}, "
                f"observed {observed_signature}"
            )
        reviewed_relocations = [
            {
                **observed,
                **(
                    {"target_address": reviewed["target_address"]}
                    if reviewed["type"] in external_types
                    else {}
                ),
                **(
                    {"symbol_type": reviewed["symbol_type"]}
                    if "symbol_type" in reviewed
                    else {}
                ),
            }
            for reviewed, observed in zip(
                reviewed_relocations,
                observed_sorted,
            )
        ]
        validate_absolute_movwt_pairs(
            reviewed_relocations,
            context=f"relocated closure {function_name}",
        )
        validate_prel_movwt_pairs(
            reviewed_relocations,
            context=f"relocated closure {function_name}",
        )
    else:
        expected_identity = sorted(
            (item["offset"], item["type"], item["symbol"])
            for item in reviewed_relocations
        )
        observed_identity = sorted(
            (item["offset"], item["type"], item["symbol"])
            for item in observed_relocations
        )
        if observed_identity != expected_identity:
            raise BuildError(
                f"relocated closure {function_name} relocation list differs "
                f"from reviewed config: expected {expected_identity}, "
                f"observed {observed_identity}"
            )

    function_start = int(function_section["offset"])
    code = data[function_start:function_start + function_size]
    unrelocated_sha256 = sha256(code)
    rodata_offset = align_up(function_size, rodata_alignment_pin)
    blob = bytearray(code)
    blob.extend(b"\0" * (rodata_offset - len(blob)))
    blob.extend(rodata_bytes)
    rodata_runtime_address = runtime_address + rodata_offset
    symbol_offsets = {
        item["name"]: rodata_offset + item["offset"]
        for item in reviewed_symbols
    }
    prel_pair_details: dict[int, dict[str, int | str]] = {}
    for index, item in enumerate(reviewed_relocations):
        if item["type"] != "R_ARM_THM_MOVW_PREL_NC":
            continue
        low_offset = int(item["offset"])
        high_offset = int(reviewed_relocations[index + 1]["offset"])
        if low_offset + 4 > function_size or high_offset + 4 > function_size:
            raise BuildError(
                f"relocated closure {function_name} PREL MOVW/MOVT pair "
                f"at +0x{low_offset:X} exceeds its text section"
            )
        details = resolve_prel_movwt_pair(
            blob,
            low_offset,
            symbol_offsets[item["symbol"]],
            high_site=high_offset,
        )
        pair_report = {
            "prel_pair_offset": low_offset,
            "prel_pair_offset_hex": f"0x{low_offset:X}",
            "prel_low_addend": details["low_addend"],
            "prel_high_addend": details["high_addend"],
            "prel_result": details["result"],
            "prel_result_hex": details["result_hex"],
            "prel_register": details["register"],
        }
        prel_pair_details[low_offset] = pair_report
        prel_pair_details[high_offset] = pair_report
    resolved_relocations: list[dict[str, Any]] = []
    for item in reviewed_relocations:
        offset = int(item["offset"])
        relocation_name = str(item["type"])
        site_address = runtime_address + offset
        if relocation_name in external_branch_types:
            if offset + 4 > function_size:
                raise BuildError(
                    f"relocated closure {function_name} branch relocation at "
                    f"+0x{offset:X} exceeds its text section"
                )
            link = relocation_name == "R_ARM_THM_CALL"
            canonical = encode_thumb_branch(0, 0, link=link)
            if bytes(blob[offset:offset + 4]) != canonical:
                raise BuildError(
                    f"relocated closure {function_name} {relocation_name} at "
                    f"+0x{offset:X} does not use the canonical zero-symbol "
                    "REL placeholder"
                )
            target_address = int(item["target_address"])
            blob[offset:offset + 4] = encode_thumb_branch(
                site_address,
                target_address,
                link=link,
            )
            target_offset = None
        elif relocation_name in ABSOLUTE_MOVWT_TYPES:
            if offset + 4 > function_size:
                raise BuildError(
                    f"relocated closure {function_name} absolute MOVW/MOVT "
                    f"relocation at +0x{offset:X} exceeds its text section"
                )
            target_address = int(item["target_address"])
            resolve_absolute_movwt(
                blob,
                offset,
                target_address,
                high=relocation_name == "R_ARM_THM_MOVT_ABS",
            )
            target_offset = None
        else:
            if offset + 4 > function_size:
                raise BuildError(
                    f"relocated closure {function_name} local relocation at "
                    f"+0x{offset:X} exceeds its text section"
                )
            target_offset = symbol_offsets[item["symbol"]]
            target_address = runtime_address + target_offset
            if relocation_name == "R_ARM_REL32":
                resolve_rel32(blob, offset, target_offset)
        resolved_relocations.append(
            {
                **item,
                "runtime_address": site_address,
                "runtime_address_hex": f"0x{site_address:08X}",
                "target_address": target_address,
                "target_address_hex": f"0x{target_address:08X}",
                **(
                    {"target_offset": target_offset}
                    if target_offset is not None
                    else {}
                ),
                **prel_pair_details.get(offset, {}),
            }
        )

    discarded_alloc_sections = [
        {
            "name": str(section["name"]),
            "size": int(section["size"]),
            "flags": int(section["flags"]),
        }
        for section in sections
        if int(section["index"])
        not in (function_section_index, rodata_section_index)
        and int(section["flags"]) & SHF_ALLOC
        and int(section["size"])
    ]
    authenticated_cantunwind_indexes = (
        authenticated_cantunwind_companion_indexes(
            data,
            sections,
            symbols,
            function_section,
        )
        if strict_relocation_contract
        else frozenset()
    )
    authenticated_cantunwind_discards = [
        {
            "name": str(section["name"]),
            "size": int(section["size"]),
            "policy": (
                "authenticated selected-function CANTUNWIND/R_ARM_PREL31 "
                "metadata deliberately discarded, not executable closure data"
            ),
        }
        for section in sections
        if int(section["index"]) in authenticated_cantunwind_indexes
    ]
    unexpected_alloc_sections = [
        section for section in sections
        if int(section["index"])
        not in (function_section_index, rodata_section_index)
        and int(section["flags"]) & SHF_ALLOC
        and int(section["size"])
        and int(section["index"]) not in authenticated_cantunwind_indexes
    ]
    if strict_relocation_contract and unexpected_alloc_sections:
        raise BuildError(
            f"relocated closure {function_name} strict relocation contract "
            "rejects unexpected allocated sections: "
            + ", ".join(
                str(section["name"]) for section in unexpected_alloc_sections
            )
        )
    relocated_code = bytes(blob[:function_size])
    return (
        bytes(blob),
        {
            "function": function_name,
            "section": text_section_name,
            "runtime_address": runtime_address,
            "runtime_address_hex": f"0x{runtime_address:08X}",
            "size": function_size,
            "sha256": sha256(relocated_code),
            "unrelocated_sha256": unrelocated_sha256,
            "alignment": function_alignment,
            "closure_size": len(blob),
            "closure_sha256": sha256(blob),
            "internal_padding_size": rodata_offset - function_size,
            "rodata": {
                "section": rodata_section_name,
                "offset": rodata_offset,
                "runtime_address": rodata_runtime_address,
                "runtime_address_hex": f"0x{rodata_runtime_address:08X}",
                "size": len(rodata_bytes),
                "sha256": sha256(rodata_bytes),
                "alignment": rodata_alignment_pin,
                "symbols": [
                    {
                        **item,
                        "closure_offset": rodata_offset + item["offset"],
                        "runtime_address": (
                            rodata_runtime_address + item["offset"]
                        ),
                        "runtime_address_hex": (
                            f"0x{rodata_runtime_address + item['offset']:08X}"
                        ),
                    }
                    for item in reviewed_symbols
                ],
            },
            "relocation_count": len(resolved_relocations),
            "relocations": resolved_relocations,
            "discarded_alloc_section_count": len(discarded_alloc_sections),
            "discarded_alloc_section_bytes": sum(
                int(section["size"]) for section in discarded_alloc_sections
            ),
            "discarded_alloc_sections": discarded_alloc_sections,
            "authenticated_cantunwind_discard_count": len(
                authenticated_cantunwind_discards
            ),
            "authenticated_cantunwind_discards": (
                authenticated_cantunwind_discards
            ),
        },
    )


def compile_relocated_closure_leaf(
    *,
    root: Path,
    clang: str,
    leaf_config: dict[str, Any],
    object_path: Path,
    runtime_address: int,
    record: bool = False,
    allowed_defined_relocation_targets: frozenset[str] = frozenset(),
) -> tuple[bytes, dict[str, Any]]:
    """Compile and authenticate one closure-aware relocated leaf."""

    function_name = leaf_config.get("function")
    if not isinstance(function_name, str):
        raise BuildError("relocated closure requires a function name")
    strict_relocation_contract = leaf_config.get(
        "strict_relocation_contract",
        False,
    )
    allow_local_function = leaf_config.get("allow_local_function", False)
    allow_local_relocation_targets = leaf_config.get(
        "allow_local_relocation_targets",
        False,
    )
    if not isinstance(strict_relocation_contract, bool):
        raise BuildError(
            f"relocated closure {function_name} strict_relocation_contract "
            "must be boolean"
        )
    source_config = leaf_config.get("source")
    if not isinstance(source_config, dict):
        raise BuildError(
            f"relocated closure {function_name} requires a source record"
        )
    source_relative = source_config.get("path")
    source_pin = source_config.get("sha256")
    if not isinstance(source_relative, str) or not source_relative:
        raise BuildError(
            f"relocated closure {function_name} requires source.path"
        )
    if not isinstance(source_pin, str) or not re.fullmatch(
        r"[0-9a-f]{64}", source_pin
    ):
        raise BuildError(
            f"relocated closure {function_name} requires a lowercase source "
            "SHA-256"
        )
    source_path = resolve_below(root, source_relative)
    source = source_path.read_bytes()
    source_digest = sha256(source)
    source_size = source_config.get("size")
    if source_size is not None and (
        not isinstance(source_size, int)
        or source_size < 1
        or source_size != len(source)
    ):
        raise BuildError(
            f"{source_relative}: relocated closure {function_name} source "
            "size differs from config"
        )
    if source_digest != source_pin:
        raise BuildError(
            f"{source_relative}: relocated closure {function_name} source "
            "SHA-256 differs from config"
        )

    toolchain = leaf_config.get("toolchain")
    if not isinstance(toolchain, dict):
        raise BuildError(
            f"relocated closure {function_name} requires a toolchain"
        )
    target = toolchain.get("target")
    flags = toolchain.get("flags")
    if not isinstance(target, str) or not target:
        raise BuildError(
            f"relocated closure {function_name} requires toolchain.target"
        )
    if (
        not isinstance(flags, list)
        or any(not isinstance(flag, str) or not flag for flag in flags)
    ):
        raise BuildError(
            f"relocated closure {function_name} toolchain.flags must be "
            "strings"
        )
    if "-ffunction-sections" not in flags or "-fdata-sections" not in flags:
        raise BuildError(
            f"relocated closure {function_name} requires "
            "-ffunction-sections and -fdata-sections"
        )
    if "-fno-function-sections" in flags or any(
        flag == "-flto" or flag.startswith("-flto=") for flag in flags
    ):
        raise BuildError(
            f"relocated closure {function_name} cannot disable function "
            "sections or use LTO"
        )

    expected = leaf_config.get("expected")
    if not isinstance(expected, dict):
        raise BuildError(
            f"relocated closure {function_name} requires expected pins"
        )
    expected_fields = (
        "size",
        "sha256",
        "closure_size",
        "closure_sha256",
        "rodata_offset",
    )
    if (
        not isinstance(expected.get("size"), int)
        or expected["size"] < 1
        or not isinstance(expected.get("sha256"), str)
        or not re.fullmatch(r"[0-9a-f]{64}", expected["sha256"])
        or not isinstance(expected.get("closure_size"), int)
        or expected["closure_size"] < expected["size"]
        or not isinstance(expected.get("closure_sha256"), str)
        or not re.fullmatch(r"[0-9a-f]{64}", expected["closure_sha256"])
        or not isinstance(expected.get("rodata_offset"), int)
        or expected["rodata_offset"] < expected["size"]
    ):
        raise BuildError(
            f"relocated closure {function_name} expected pins require "
            + ", ".join(expected_fields)
        )
    closure_config = leaf_config.get("closure")
    relocation_configs = leaf_config.get("relocations")
    if not isinstance(closure_config, dict):
        raise BuildError(f"relocated closure {function_name} requires closure")
    if not isinstance(relocation_configs, list):
        raise BuildError(
            f"relocated closure {function_name} requires relocations"
        )

    include_dirs, normalized_include_dirs = resolve_toolchain_include_dirs(
        root, toolchain
    )
    version = compiler_version(clang)
    validate_compiler_version(toolchain, version)
    command = [clang, f"--target={target}", *flags]
    for include_dir in include_dirs:
        command.extend(("-I", str(include_dir)))
    command.extend(("-c", str(source_path), "-o", str(object_path)))
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode:
        raise BuildError(
            f"relocated closure {function_name} compilation failed:\n"
            + (completed.stderr.strip() or completed.stdout.strip())
        )

    leaf, extraction = extract_relocated_function_closure(
        object_path,
        function_name,
        runtime_address=runtime_address,
        closure_config=closure_config,
        relocation_configs=relocation_configs,
        record=record,
        strict_relocation_contract=strict_relocation_contract,
        allow_local_function=allow_local_function,
        allowed_defined_relocation_targets=allowed_defined_relocation_targets,
        allow_local_relocation_targets=allow_local_relocation_targets,
    )
    observed = {
        "size": extraction["size"],
        "sha256": extraction["sha256"],
        "closure_size": extraction["closure_size"],
        "closure_sha256": extraction["closure_sha256"],
        "rodata_offset": extraction["rodata"]["offset"],
    }
    if not record and any(expected[key] != value for key, value in observed.items()):
        raise BuildError(
            f"relocated closure {function_name} output differs from reviewed "
            f"pins: expected { {key: expected[key] for key in observed} }, "
            f"observed {observed}"
        )

    source_record: dict[str, Any] = {
        "path": source_path.relative_to(root.resolve()).as_posix(),
        "size": len(source),
        "sha256": source_digest,
    }
    for key in (
        "license",
        "origin",
        "upstream",
        "upstream_commit",
        "evidence",
    ):
        if key in source_config:
            source_record[key] = source_config[key]
    toolchain_record: dict[str, Any] = {
        "executable": clang,
        "version": version,
        "target": target,
        "flags": flags,
    }
    if normalized_include_dirs is not None:
        toolchain_record["include_dirs"] = normalized_include_dirs
    return (
        leaf,
        {
            "source": source_record,
            "toolchain": toolchain_record,
            "extraction": extraction,
            "pins": {
                **observed,
                "unrelocated_sha256": extraction["unrelocated_sha256"],
                "alignment": extraction["alignment"],
                "rodata": extraction["rodata"],
                "relocations": extraction["relocations"],
            },
        },
    )


def compile_in_place_leaf(
    *,
    root: Path,
    clang: str,
    leaf_config: dict[str, Any],
    object_path: Path,
    toolchain_profile: str | None = None,
    record: bool = False,
    enforce_stock_fit: bool = True,
    allowed_defined_relocation_targets: frozenset[str] = frozenset(),
    thumb_prel_symbols: frozenset[str] = frozenset(),
) -> tuple[bytes, dict[str, Any]]:
    """Compile and resolve an authenticated leaf for one fixed stock address."""

    function_name = leaf_config.get("function")
    if not isinstance(function_name, str):
        raise BuildError("in-place leaf requires a function name")
    leaf_config = resolve_leaf_profile(
        leaf_config, toolchain_profile, record=record
    )
    strict_relocation_contract = leaf_config.get(
        "strict_relocation_contract",
        False,
    )
    if not isinstance(strict_relocation_contract, bool):
        raise BuildError(
            f"in-place leaf {function_name} strict_relocation_contract must "
            "be boolean"
        )
    runtime_address = leaf_config.get("runtime_address")
    if not isinstance(runtime_address, int):
        raise BuildError(
            f"in-place leaf {function_name} requires runtime_address"
        )
    relocation_configs = leaf_config.get("relocations")
    if not isinstance(relocation_configs, list):
        raise BuildError(
            f"in-place leaf {function_name} requires an explicit "
            "relocations list"
        )

    source_config = leaf_config.get("source")
    if not isinstance(source_config, dict):
        raise BuildError(f"in-place leaf {function_name} requires a source record")
    source_relative = source_config.get("path")
    source_pin = source_config.get("sha256")
    if not isinstance(source_relative, str) or not source_relative:
        raise BuildError(f"in-place leaf {function_name} requires source.path")
    if not isinstance(source_pin, str) or not re.fullmatch(
        r"[0-9a-f]{64}",
        source_pin,
    ):
        raise BuildError(
            f"in-place leaf {function_name} requires a lowercase source SHA-256"
        )
    source_path = resolve_below(root, source_relative)
    source = source_path.read_bytes()
    source_digest = sha256(source)
    source_size = source_config.get("size")
    if source_size is not None and (
        not isinstance(source_size, int)
        or source_size < 1
        or source_size != len(source)
    ):
        raise BuildError(
            f"{source_relative}: in-place leaf source size differs from config"
        )
    if source_digest != source_pin:
        raise BuildError(
            f"{source_relative}: in-place leaf source SHA-256 differs from config"
        )

    toolchain = leaf_config.get("toolchain")
    if not isinstance(toolchain, dict):
        raise BuildError(f"in-place leaf {function_name} requires a toolchain")
    target = toolchain.get("target")
    flags = toolchain.get("flags")
    if not isinstance(target, str) or not target:
        raise BuildError(
            f"in-place leaf {function_name} requires toolchain.target"
        )
    if (
        not isinstance(flags, list)
        or any(not isinstance(flag, str) or not flag for flag in flags)
    ):
        raise BuildError(
            f"in-place leaf {function_name} toolchain.flags must be strings"
        )
    if "-ffunction-sections" not in flags:
        raise BuildError(
            f"in-place leaf {function_name} requires -ffunction-sections"
        )
    if "-fdata-sections" not in flags:
        raise BuildError(
            f"in-place leaf {function_name} requires -fdata-sections"
        )
    if "-fno-function-sections" in flags or any(
        flag == "-flto" or flag.startswith("-flto=") for flag in flags
    ):
        raise BuildError(
            f"in-place leaf {function_name} cannot disable function sections "
            "or use LTO"
        )

    expected = leaf_config.get("expected")
    stock = leaf_config.get("stock")
    for label, pins in (("expected", expected), ("stock", stock)):
        if not isinstance(pins, dict):
            raise BuildError(
                f"in-place leaf {function_name} requires {label} pins"
            )
        pinned_size = pins.get("size")
        pinned_sha256 = pins.get("sha256")
        if (
            not isinstance(pinned_size, int)
            or pinned_size < 1
            or not isinstance(pinned_sha256, str)
            or not re.fullmatch(r"[0-9a-f]{64}", pinned_sha256)
        ):
            raise BuildError(
                f"in-place leaf {function_name} {label} pins require size "
                "and lowercase SHA-256"
            )
    if expected["size"] != stock["size"]:
        raise BuildError(
            f"in-place leaf {function_name} expected and stock spans must "
            "have the same size"
        )

    include_dirs, normalized_include_dirs = resolve_toolchain_include_dirs(
        root,
        toolchain,
    )
    version = compiler_version(clang)
    validate_compiler_version(toolchain, version)
    command = [
        clang,
        f"--target={target}",
        *flags,
    ]
    for include_dir in include_dirs:
        command.extend(("-I", str(include_dir)))
    command.extend(("-c", str(source_path), "-o", str(object_path)))
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode:
        raise BuildError(
            f"in-place leaf {function_name} compilation failed:\n"
            + (completed.stderr.strip() or completed.stdout.strip())
        )

    leaf, extraction = extract_in_place_function_section(
        object_path,
        function_name,
        runtime_address=runtime_address,
        relocation_configs=relocation_configs,
        record=record,
        allowed_defined_relocation_targets=(
            allowed_defined_relocation_targets
        ),
        thumb_prel_symbols=thumb_prel_symbols,
        strict_relocation_contract=strict_relocation_contract,
        allow_local_function=leaf_config.get("allow_local_function", False),
        allow_local_relocation_targets=leaf_config.get(
            "allow_local_relocation_targets",
            False,
        ),
    )
    if not record and (
        len(leaf) != expected["size"]
        or sha256(leaf) != expected["sha256"]
    ):
        raise BuildError(
            f"in-place leaf {function_name} output differs from reviewed pins: "
            f"expected {expected['size']} bytes/{expected['sha256']}, observed "
            f"{len(leaf)} bytes/{sha256(leaf)}"
        )
    if record and enforce_stock_fit and len(leaf) != stock["size"]:
        raise BuildError(
            f"in-place leaf {function_name} compiled to {len(leaf)} bytes but "
            f"must fit the {stock['size']}-byte stock span; this leaf cannot be "
            "an in-place replacement under this toolchain"
        )

    source_record: dict[str, Any] = {
        "path": source_path.relative_to(root.resolve()).as_posix(),
        "size": len(source),
        "sha256": source_digest,
    }
    for key in (
        "license",
        "origin",
        "upstream",
        "upstream_commit",
        "evidence",
    ):
        if key in source_config:
            source_record[key] = source_config[key]
    toolchain_record: dict[str, Any] = {
        "executable": clang,
        "version": version,
        "target": target,
        "flags": flags,
    }
    if normalized_include_dirs is not None:
        toolchain_record["include_dirs"] = normalized_include_dirs
    return (
        leaf,
        {
            "source": source_record,
            "toolchain": toolchain_record,
            "stock": {
                "size": int(stock["size"]),
                "sha256": str(stock["sha256"]),
            },
            "extraction": extraction,
            "pins": {"size": len(leaf), "sha256": sha256(leaf)},
        },
    )


def append_isolated_leaves(
    *,
    overlay: bytes,
    functions: dict[str, dict[str, int]],
    link_report: dict[str, Any],
    leaves: list[tuple[bytes, dict[str, Any]]],
) -> tuple[
    bytes,
    dict[str, dict[str, int]],
    dict[str, Any],
    list[dict[str, Any]],
]:
    """Append dependency-free leaf text after the primary linked payload."""

    combined = bytearray(overlay)
    combined_functions = dict(functions)
    combined_link_report = dict(link_report)
    placement_reports: list[dict[str, Any]] = []
    padding_size = 0
    text_size = 0
    for leaf, report in leaves:
        extraction = report["extraction"]
        function_name = extraction["function"]
        if function_name in combined_functions:
            raise BuildError(f"duplicate overlay function {function_name}")
        alignment = int(extraction["alignment"])
        offset = align_up(len(combined), alignment)
        padding = offset - len(combined)
        combined.extend(b"\0" * padding)
        combined.extend(leaf)
        combined_functions[function_name] = {
            "offset": offset,
            "size": len(leaf),
        }
        placement = {
            **report,
            "placement": {
                "offset": offset,
                "size": len(leaf),
                "alignment": alignment,
                "padding_before": padding,
            },
        }
        placement_reports.append(placement)
        padding_size += padding
        text_size += len(leaf)

    if leaves:
        combined_link_report["isolated_text_size"] = text_size
        combined_link_report["isolated_padding_size"] = padding_size
        combined_link_report["isolated_functions"] = [
            {
                "function": report["extraction"]["function"],
                **report["placement"],
            }
            for report in placement_reports
        ]
    return (
        bytes(combined),
        combined_functions,
        combined_link_report,
        placement_reports,
    )


def append_relocated_leaves(
    *,
    root: Path,
    clang: str,
    overlay: bytes,
    overlay_runtime_address: int,
    functions: dict[str, dict[str, int]],
    link_report: dict[str, Any],
    leaf_configs: list[dict[str, Any]],
    object_root: Path,
    toolchain_profile: str | None = None,
    record: bool = False,
) -> tuple[
    bytes,
    dict[str, dict[str, int]],
    dict[str, Any],
    list[dict[str, Any]],
]:
    """Compile, resolve, and append independently reviewed function leaves.

    Relocated leaves are compiled as independent translation units so the
    compiler cannot fold their reviewed external dependencies through another
    source file in the primary combined translation unit.  Their explicit
    relocation list may be empty for a call-free leaf; every retained
    relocation is resolved directly to an already placed overlay ABI function.
    """

    if (
        not isinstance(overlay_runtime_address, int)
        or overlay_runtime_address < 0
        or overlay_runtime_address > 0xFFFFFFFF
        or overlay_runtime_address & 1
    ):
        raise BuildError(
            "relocated leaves require a nonnegative halfword-aligned "
            "overlay runtime address"
        )
    if (
        not isinstance(leaf_configs, list)
        or any(not isinstance(item, dict) for item in leaf_configs)
    ):
        raise BuildError("relocated_leaves must be a list of records")
    selected_relocated_functions = frozenset(
        item.get("function")
        for item in leaf_configs
        if isinstance(item.get("function"), str)
    )

    combined = bytearray(overlay)
    combined_functions = dict(functions)
    combined_link_report = dict(link_report)
    placement_reports: list[dict[str, Any]] = []
    total_padding = 0
    total_text = 0
    total_rodata = 0
    total_closure_padding = 0
    for index, leaf_config in enumerate(leaf_configs):
        function_name = leaf_config.get("function")
        if not isinstance(function_name, str) or not re.fullmatch(
            r"[A-Za-z_][A-Za-z0-9_]*",
            function_name,
        ):
            raise BuildError(
                f"relocated leaf {index} requires a C-identifier function"
            )
        if function_name in combined_functions:
            raise BuildError(
                f"duplicate overlay function {function_name}"
            )

        leaf_config = resolve_leaf_profile(
            leaf_config, toolchain_profile, record=record
        )
        expected = leaf_config.get("expected")
        if not isinstance(expected, dict):
            raise BuildError(
                f"relocated leaf {function_name} requires expected pins"
            )
        expected_size = expected.get("size")
        expected_sha256 = expected.get("sha256")
        expected_alignment = expected.get("alignment")
        expected_offset = expected.get("offset")
        expected_unrelocated_sha256 = expected.get(
            "unrelocated_sha256"
        )
        if (
            not isinstance(expected_size, int)
            or expected_size < 1
            or not isinstance(expected_sha256, str)
            or not re.fullmatch(r"[0-9a-f]{64}", expected_sha256)
            or not isinstance(expected_alignment, int)
            or expected_alignment < 1
            or expected_alignment & (expected_alignment - 1)
        ):
            raise BuildError(
                f"relocated leaf {function_name} expected pins require "
                "positive size, lowercase SHA-256, and power-of-two alignment"
            )

        padding = (
            align_up(len(combined), expected_alignment) - len(combined)
        )
        offset = len(combined) + padding
        if not record and expected_offset is not None and (
            not isinstance(expected_offset, int)
            or expected_offset < 0
            or expected_offset != offset
        ):
            raise BuildError(
                f"relocated leaf {function_name} offset differs from "
                f"reviewed {expected_offset}: observed {offset}"
            )
        if expected_unrelocated_sha256 is not None and (
            not isinstance(expected_unrelocated_sha256, str)
            or not re.fullmatch(
                r"[0-9a-f]{64}",
                expected_unrelocated_sha256,
            )
        ):
            raise BuildError(
                f"relocated leaf {function_name} unrelocated SHA-256 pin "
                "must be lowercase hexadecimal"
            )
        runtime_address = overlay_runtime_address + offset
        relocation_configs = leaf_config.get("relocations")
        if (
            not isinstance(relocation_configs, list)
            or any(not isinstance(item, dict) for item in relocation_configs)
        ):
            raise BuildError(
                f"relocated leaf {function_name} requires an explicit "
                "relocations list"
            )
        source = leaf_config.get("source")
        if not isinstance(source, dict) or not isinstance(
            source.get("size"),
            int,
        ):
            raise BuildError(
                f"relocated leaf {function_name} requires source.size"
            )
        closure_config = leaf_config.get("closure")
        target_functions: list[str | None] = []
        if closure_config is not None:
            if not isinstance(closure_config, dict):
                raise BuildError(
                    f"relocated leaf {function_name} closure must be an object"
                )
            resolved_configs = []
            selected_defined_sibling_targets: set[str] = set()
            allowed_relocation_fields = {
                "offset",
                "type",
                "symbol",
                "target_address",
                "target_function",
                "symbol_type",
            }
            for relocation_index, relocation in enumerate(relocation_configs):
                unknown_fields = set(relocation) - allowed_relocation_fields
                if unknown_fields:
                    raise BuildError(
                        f"relocated closure {function_name} relocation "
                        f"{relocation_index} has unknown fields "
                        f"{sorted(unknown_fields)}"
                    )
                relocation_type = relocation.get("type")
                symbol = relocation.get("symbol")
                target_function = relocation.get("target_function")
                target_address = relocation.get("target_address")
                resolved = {
                    key: value
                    for key, value in relocation.items()
                    if key != "target_function"
                }
                if relocation_type in (
                    "R_ARM_THM_CALL",
                    "R_ARM_THM_JUMP24",
                ):
                    has_function = target_function is not None
                    has_address = target_address is not None
                    if has_function == has_address:
                        raise BuildError(
                            f"relocated closure {function_name} relocation "
                            f"{relocation_index} requires exactly one of "
                            "target_function or target_address"
                        )
                    if has_function:
                        if (
                            not isinstance(symbol, str)
                            or not isinstance(target_function, str)
                            or symbol != target_function
                        ):
                            raise BuildError(
                                f"relocated closure {function_name} relocation "
                                f"{relocation_index} must bind its exact symbol "
                                "to the same target_function name"
                            )
                        if target_function == function_name:
                            if relocation_type != "R_ARM_THM_CALL":
                                raise BuildError(
                                    f"relocated closure {function_name} "
                                    "selected-function self relocation must be "
                                    "R_ARM_THM_CALL"
                                )
                            resolved["target_address"] = runtime_address
                        else:
                            target = combined_functions.get(target_function)
                            if target is None:
                                raise BuildError(
                                    f"relocated closure {function_name} "
                                    f"relocation {relocation_index} targets "
                                    "unavailable prior overlay function "
                                    f"{target_function!r}"
                                )
                            resolved["target_address"] = (
                                overlay_runtime_address + int(target["offset"])
                            )
                    target_functions.append(
                        target_function if isinstance(target_function, str) else None
                    )
                    if (
                        isinstance(target_function, str)
                        and target_function in selected_relocated_functions
                    ):
                        selected_defined_sibling_targets.add(target_function)
                elif relocation_type in ABSOLUTE_MOVWT_TYPES:
                    if target_function is not None:
                        raise BuildError(
                            f"relocated closure {function_name} absolute "
                            f"relocation {relocation_index} cannot target a "
                            "function"
                        )
                    target_functions.append(None)
                else:
                    if target_function is not None:
                        raise BuildError(
                            f"relocated closure {function_name} local "
                            f"relocation {relocation_index} cannot target a "
                            "function"
                        )
                    target_functions.append(None)
                resolved_configs.append(resolved)
            compiled_config = {**leaf_config, "relocations": resolved_configs}
            leaf, report = compile_relocated_closure_leaf(
                root=root,
                clang=clang,
                leaf_config=compiled_config,
                object_path=object_root / f"relocated-leaf-{index}.o",
                runtime_address=runtime_address,
                record=record,
                allowed_defined_relocation_targets=frozenset(
                    selected_defined_sibling_targets
                ),
            )
        else:
            resolved_configs: list[dict[str, Any]] = []
            selected_defined_sibling_targets: set[str] = set()
            thumb_prel_symbols: set[str] = set()
            allowed_relocation_fields = {
                "offset",
                "type",
                "symbol",
                "target_function",
                "target_address",
                "symbol_type",
            }
            for relocation_index, relocation in enumerate(relocation_configs):
                unknown_fields = set(relocation) - allowed_relocation_fields
                if unknown_fields:
                    raise BuildError(
                        f"relocated leaf {function_name} relocation "
                        f"{relocation_index} has unknown fields "
                        f"{sorted(unknown_fields)}"
                    )
                symbol = relocation.get("symbol")
                target_function = relocation.get("target_function")
                target_address = relocation.get("target_address")
                relocation_type = relocation.get("type")
                if relocation_type not in (
                    "R_ARM_THM_CALL",
                    "R_ARM_THM_JUMP24",
                    *ABSOLUTE_MOVWT_TYPES,
                    *PREL_MOVWT_TYPES,
                ):
                    raise BuildError(
                        f"relocated leaf {function_name} relocation "
                        f"{relocation_index} has unsupported appended-leaf type "
                        f"{relocation_type!r}"
                    )
                if relocation_type in ABSOLUTE_MOVWT_TYPES:
                    if target_function is not None or target_address is None:
                        raise BuildError(
                            f"relocated leaf {function_name} absolute "
                            f"relocation {relocation_index} requires only a "
                            "fixed target_address"
                        )
                    resolved_target_address = target_address
                    target_functions.append(None)
                else:
                    has_function = target_function is not None
                    has_address = target_address is not None
                    if has_function == has_address:
                        raise BuildError(
                            f"relocated leaf {function_name} relocation "
                            f"{relocation_index} requires exactly one of "
                            "target_function or target_address"
                        )
                    if has_function:
                        if (
                            not isinstance(symbol, str)
                            or not isinstance(target_function, str)
                            or symbol != target_function
                        ):
                            raise BuildError(
                                f"relocated leaf {function_name} relocation "
                                f"{relocation_index} must bind its exact symbol "
                                "to the same target_function name"
                            )
                        target = combined_functions.get(target_function)
                        if target is None:
                            raise BuildError(
                                f"relocated leaf {function_name} relocation "
                                f"{relocation_index} targets unavailable prior "
                                f"overlay function {target_function!r}"
                            )
                        resolved_target_address = (
                            overlay_runtime_address + int(target["offset"])
                        )
                        if relocation_type in PREL_MOVWT_TYPES and (
                            relocation.get("symbol_type") not in (None, "STT_FUNC")
                        ):
                            raise BuildError(
                                f"relocated leaf {function_name} PREL function "
                                f"relocation {relocation_index} must use "
                                "symbol_type STT_FUNC"
                            )
                        if relocation_type in PREL_MOVWT_TYPES:
                            thumb_prel_symbols.add(target_function)
                    else:
                        resolved_target_address = target_address
                    target_functions.append(
                        target_function if isinstance(target_function, str) else None
                    )
                resolved_configs.append(
                    {
                        "offset": relocation.get("offset"),
                        "type": relocation.get("type"),
                        "symbol": symbol,
                        "target_address": resolved_target_address,
                        **(
                            {"symbol_type": relocation["symbol_type"]}
                            if "symbol_type" in relocation
                            else {}
                        ),
                    }
                )
                if (
                    isinstance(target_function, str)
                    and target_function in selected_relocated_functions
                ):
                    selected_defined_sibling_targets.add(target_function)

            synthetic_config = {
                "function": function_name,
                "runtime_address": runtime_address,
                "source": source,
                "toolchain": leaf_config.get("toolchain"),
                "expected": {
                    "size": expected_size,
                    "sha256": expected_sha256,
                },
                # compile_in_place_leaf shares the exact source/toolchain,
                # relocation, and final-byte authentication contract.  The
                # synthetic equality pin is discarded below; relocated leaves
                # do not claim to replace a same-sized stock span in place.
                "stock": {
                    "size": expected_size,
                    "sha256": expected_sha256,
                },
                "relocations": resolved_configs,
                "strict_relocation_contract": leaf_config.get(
                    "strict_relocation_contract",
                    False,
                ),
                "allow_local_function": leaf_config.get(
                    "allow_local_function",
                    False,
                ),
                "allow_local_relocation_targets": leaf_config.get(
                    "allow_local_relocation_targets",
                    False,
                ),
            }
            leaf, report = compile_in_place_leaf(
                root=root,
                clang=clang,
                leaf_config=synthetic_config,
                object_path=object_root / f"relocated-leaf-{index}.o",
                record=record,
                enforce_stock_fit=False,
                allowed_defined_relocation_targets=frozenset(
                    selected_defined_sibling_targets
                ),
                thumb_prel_symbols=frozenset(thumb_prel_symbols),
            )
        extraction = report.get("extraction")
        if not isinstance(extraction, dict):
            raise BuildError(
                f"relocated leaf {function_name} extraction report is invalid"
            )
        observed_alignment = extraction.get("alignment")
        if not record and observed_alignment != expected_alignment:
            raise BuildError(
                f"relocated leaf {function_name} alignment differs from "
                f"reviewed {expected_alignment}: observed "
                f"{observed_alignment}"
            )
        if (
            not record
            and expected_unrelocated_sha256 is not None
            and extraction.get("unrelocated_sha256")
            != expected_unrelocated_sha256
        ):
            raise BuildError(
                f"relocated leaf {function_name} unrelocated SHA-256 "
                "differs from reviewed pin"
            )
        observed_relocations = extraction.get("relocations")
        if not isinstance(observed_relocations, list):
            raise BuildError(
                f"relocated leaf {function_name} relocation report is invalid"
            )
        if closure_config is not None:
            configured_external = [
                (relocation, target_function)
                for relocation, target_function in zip(
                    relocation_configs,
                    target_functions,
                )
                if relocation.get("type") in (
                    "R_ARM_THM_CALL",
                    "R_ARM_THM_JUMP24",
                    *ABSOLUTE_MOVWT_TYPES,
                )
            ]
            observed_external = [
                relocation
                for relocation in observed_relocations
                if relocation.get("type") in (
                    "R_ARM_THM_CALL",
                    "R_ARM_THM_JUMP24",
                    *ABSOLUTE_MOVWT_TYPES,
                )
            ]
            if len(configured_external) != len(observed_external):
                raise BuildError(
                    f"relocated closure {function_name} external relocation "
                    "report is invalid"
                )
            for observed, (configured, target_function) in zip(
                observed_external,
                configured_external,
            ):
                if (
                    observed.get("type"),
                    observed.get("symbol"),
                ) != (
                    configured.get("type"),
                    configured.get("symbol"),
                ):
                    raise BuildError(
                        f"relocated closure {function_name} external relocation "
                        "report identity is invalid"
                    )
                if target_function is not None:
                    observed["target_function"] = target_function
        else:
            if len(observed_relocations) != len(target_functions):
                raise BuildError(
                    f"relocated leaf {function_name} relocation report is invalid"
                )
            for relocation, target_function in zip(
                observed_relocations,
                target_functions,
            ):
                if target_function is not None:
                    relocation["target_function"] = target_function

        combined.extend(b"\0" * padding)
        combined.extend(leaf)
        combined_functions[function_name] = {
            "offset": offset,
            "size": int(extraction["size"]),
        }
        report.pop("stock", None)
        placement = {
            **report,
            "placement": {
                "offset": offset,
                "size": len(leaf),
                **(
                    {"text_size": int(extraction["size"])}
                    if closure_config is not None
                    else {}
                ),
                "alignment": expected_alignment,
                "padding_before": padding,
                "runtime_address": runtime_address,
                "runtime_address_hex": f"0x{runtime_address:08X}",
            },
            # Actual profile-recordable pins for this relocated leaf.
            "pins": {
                "size": int(extraction["size"]),
                "sha256": str(extraction["sha256"]),
                "alignment": observed_alignment,
                "offset": offset,
                "unrelocated_sha256": extraction.get("unrelocated_sha256"),
                "relocations": [
                    {
                        "offset": int(relocation["offset"]),
                        "type": relocation["type"],
                        "symbol": relocation["symbol"],
                        **(
                            {"symbol_type": relocation["symbol_type"]}
                            if "symbol_type" in relocation
                            else {}
                        ),
                        **(
                            {
                                "target_function": relocation[
                                    "target_function"
                                ]
                            }
                            if "target_function" in relocation
                            else {}
                        ),
                        **(
                            {"target_address": relocation["target_address"]}
                            if "target_function" not in relocation
                            and relocation["type"] in (
                                "R_ARM_THM_CALL",
                                "R_ARM_THM_JUMP24",
                                *ABSOLUTE_MOVWT_TYPES,
                            )
                            else {}
                        ),
                    }
                    for relocation in extraction.get("relocations", [])
                ],
                **(
                    {
                        "closure_size": int(extraction["closure_size"]),
                        "closure_sha256": str(extraction["closure_sha256"]),
                        "rodata_offset": int(extraction["rodata"]["offset"]),
                        "rodata": extraction["rodata"],
                    }
                    if closure_config is not None
                    else {}
                ),
            },
        }
        placement_reports.append(placement)
        total_padding += padding
        total_text += int(extraction["size"])
        if closure_config is not None:
            total_rodata += int(extraction["rodata"]["size"])
            total_closure_padding += int(extraction["internal_padding_size"])

    if leaf_configs:
        combined_link_report["relocated_text_size"] = total_text
        combined_link_report["relocated_padding_size"] = total_padding
        if total_rodata or total_closure_padding:
            combined_link_report["relocated_rodata_size"] = total_rodata
            combined_link_report["relocated_closure_padding_size"] = (
                total_closure_padding
            )
        combined_link_report["relocated_functions"] = [
            {
                "function": report["extraction"]["function"],
                **report["placement"],
            }
            for report in placement_reports
        ]
    return (
        bytes(combined),
        combined_functions,
        combined_link_report,
        placement_reports,
    )


def encode_thumb_branch(
    instruction_address: int,
    target_address: int,
    *,
    link: bool,
) -> bytes:
    displacement = target_address - (instruction_address + 4)
    if displacement % 2:
        raise BuildError("Thumb branch target is not halfword aligned")
    if not -(1 << 24) <= displacement < (1 << 24):
        raise BuildError("Thumb branch target is outside the +/-16 MiB range")
    immediate = (displacement >> 1) & 0xFFFFFF
    sign = (immediate >> 23) & 1
    i1 = (immediate >> 22) & 1
    i2 = (immediate >> 21) & 1
    imm10 = (immediate >> 11) & 0x3FF
    imm11 = immediate & 0x7FF
    j1 = (~(i1 ^ sign)) & 1
    j2 = (~(i2 ^ sign)) & 1
    first = 0xF000 | (sign << 10) | imm10
    second_base = 0xD000 if link else 0x9000
    second = second_base | (j1 << 13) | (j2 << 11) | imm11
    return struct.pack("<HH", first, second)


def encode_thumb_bl(instruction_address: int, target_address: int) -> bytes:
    return encode_thumb_branch(instruction_address, target_address, link=True)


def encode_thumb_b_w(instruction_address: int, target_address: int) -> bytes:
    return encode_thumb_branch(instruction_address, target_address, link=False)


def decode_thumb_branch(
    instruction_address: int,
    encoded: bytes,
    *,
    link: bool | None = None,
) -> int:
    if len(encoded) != 4:
        raise BuildError("Thumb branch encoding must be four bytes")
    first, second = struct.unpack("<HH", encoded)
    if first & 0xF800 != 0xF000 or second & 0x9000 != 0x9000:
        raise BuildError("instruction is not a Thumb-2 B.W/BL")
    observed_link = bool(second & 0x4000)
    if link is not None and observed_link != link:
        raise BuildError(
            "instruction link bit differs from the expected Thumb branch kind"
        )
    sign = (first >> 10) & 1
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    i1 = (~(j1 ^ sign)) & 1
    i2 = (~(j2 ^ sign)) & 1
    immediate = (
        (sign << 24)
        | (i1 << 23)
        | (i2 << 22)
        | ((first & 0x03FF) << 12)
        | ((second & 0x07FF) << 1)
    )
    if immediate & (1 << 24):
        immediate -= 1 << 25
    return instruction_address + 4 + immediate


def decode_thumb_bl(instruction_address: int, encoded: bytes) -> int:
    return decode_thumb_branch(instruction_address, encoded, link=True)


def validate_scatter_literal_patch(
    *,
    image: bytes | bytearray,
    run_base: int,
    preamble_bytes: int,
    site: dict[str, Any],
    expected_size: int,
) -> dict[str, Any] | None:
    scatter = site.get("scatter_literal")
    if scatter is None:
        return None
    if not isinstance(scatter, dict):
        raise BuildError(f"{site['name']}: scatter_literal must be an object")

    fields = (
        "record_address",
        "handler_address",
        "stream_address",
        "stream_size",
        "destination_address",
        "runtime_address",
    )
    if any(not isinstance(scatter.get(field), int) for field in fields):
        raise BuildError(
            f"{site['name']}: scatter_literal requires integer "
            + ", ".join(fields)
        )
    record_address = int(scatter["record_address"])
    handler_address = int(scatter["handler_address"])
    stream_address = int(scatter["stream_address"])
    stream_size = int(scatter["stream_size"])
    destination_address = int(scatter["destination_address"])
    runtime_address = int(scatter["runtime_address"])
    if stream_size < 2:
        raise BuildError(f"{site['name']}: scatter stream is too short")

    def payload_offset(address: int, size: int) -> int:
        offset = preamble_bytes + address - run_base
        if offset < 0 or offset + size > len(image):
            raise BuildError(
                f"{site['name']}: scatter address 0x{address:08X} "
                "exceeds the Apollo component"
            )
        return offset

    record_offset = payload_offset(record_address, 16)
    handler_relative = struct.unpack_from("<i", image, record_offset)[0]
    observed_handler = (record_address + handler_relative) & ~1
    if observed_handler != handler_address:
        raise BuildError(
            f"{site['name']}: scatter handler resolved to "
            f"0x{observed_handler:08X}, expected 0x{handler_address:08X}"
        )

    stream_relative = struct.unpack_from("<i", image, record_offset + 4)[0]
    observed_stream = record_address + 4 + stream_relative
    if observed_stream != stream_address:
        raise BuildError(
            f"{site['name']}: scatter stream resolved to "
            f"0x{observed_stream:08X}, expected 0x{stream_address:08X}"
        )
    encoded_size = u32le(image, record_offset + 8)
    if encoded_size != stream_size * 2:
        raise BuildError(
            f"{site['name']}: scatter encoded size 0x{encoded_size:X} "
            f"does not describe {stream_size} bytes"
        )
    observed_destination = u32le(image, record_offset + 12)
    if observed_destination != destination_address:
        raise BuildError(
            f"{site['name']}: scatter destination is "
            f"0x{observed_destination:08X}, expected "
            f"0x{destination_address:08X}"
        )

    stream_offset = payload_offset(stream_address, stream_size)
    token = image[stream_offset]
    literal_length = token & 0x03
    literal_data_offset = 1
    if literal_length == 0:
        literal_length = image[stream_offset + 1] + 3
        literal_data_offset = 2
    literal_start = stream_address + literal_data_offset
    literal_end = literal_start + literal_length
    patch_address = int(site["runtime_address"])
    if (
        patch_address < literal_start
        or patch_address + expected_size > literal_end
        or literal_end > stream_address + stream_size
    ):
        raise BuildError(
            f"{site['name']}: source-copy span is not contained in the "
            "scatter stream's first literal run"
        )
    observed_runtime_address = (
        destination_address + patch_address - literal_start
    )
    if observed_runtime_address != runtime_address:
        raise BuildError(
            f"{site['name']}: scatter literal resolves to runtime "
            f"0x{observed_runtime_address:08X}, expected "
            f"0x{runtime_address:08X}"
        )

    return {
        "record_address": record_address,
        "record_address_hex": f"0x{record_address:08X}",
        "handler_address": observed_handler,
        "handler_address_hex": f"0x{observed_handler:08X}",
        "stream_address": observed_stream,
        "stream_address_hex": f"0x{observed_stream:08X}",
        "stream_size": stream_size,
        "literal_data_offset": literal_data_offset,
        "literal_length": literal_length,
        "destination_address": destination_address,
        "destination_address_hex": f"0x{destination_address:08X}",
        "runtime_address": observed_runtime_address,
        "runtime_address_hex": f"0x{observed_runtime_address:08X}",
    }


def verify_expected(
    label: str,
    actual_size: int,
    actual_sha256: str,
    expected_size: int | None,
    expected_sha256: str | None,
) -> None:
    if expected_size is not None and actual_size != expected_size:
        raise BuildError(
            f"{label} size {actual_size} differs from reviewed {expected_size}"
        )
    if expected_sha256 is not None and actual_sha256 != expected_sha256:
        raise BuildError(
            f"{label} SHA-256 {actual_sha256} differs from reviewed "
            f"{expected_sha256}"
        )


def patch_component(
    *,
    base: bytes,
    overlay: bytes,
    functions: dict[str, dict[str, int]],
    config: dict[str, Any],
    in_place_leaves: (
        list[tuple[bytes, dict[str, Any]]]
        | tuple[tuple[bytes, dict[str, Any]], ...]
    ) = (),
) -> tuple[bytes, dict[str, Any]]:
    run_base = int(config["run_base"])
    preamble_bytes = int(config["preamble_bytes"])
    alignment = int(config["alignment"])
    if len(base) < preamble_bytes + 8:
        raise BuildError("base Apollo main payload is too short")
    if u32le(base, 0) & 0x00FFFFFF != len(base):
        raise BuildError("base Apollo main preamble size is invalid")
    if u32le(base, 4) != zlib.crc32(base[8:]) & 0xFFFFFFFF:
        raise BuildError("base Apollo main preamble CRC-32 is invalid")
    if (
        preamble_bytes != 0x20
        or u32le(base, 0x10) != 0xCB
        or u32le(base, 0x14) != run_base
        or any(u32le(base, offset) != 0 for offset in (0x08, 0x0C, 0x18, 0x1C))
    ):
        raise BuildError("base Apollo main preamble layout changed")

    overlay_payload_offset = align_up(len(base), alignment)
    overlay_runtime_address = (
        run_base + overlay_payload_offset - preamble_bytes
    )
    patched = bytearray(
        struct.pack(
            "<IIIIIIII",
            (u32le(base, 0) & 0xFF000000) | len(base),
            0,
            0,
            0,
            0xCB,
            run_base,
            0,
            0,
        )
        + base[preamble_bytes:]
    )
    patched.extend(b"\0" * (overlay_payload_offset - len(patched)))
    patched.extend(overlay)

    original = bytes(patched)
    in_place_plans: list[dict[str, Any]] = []
    in_place_ranges: list[tuple[int, int, str]] = []
    protected_literal_ranges: list[tuple[int, int, str]] = []
    in_place_names: set[str] = set()
    for leaf, report in in_place_leaves:
        extraction = report.get("extraction")
        stock = report.get("stock")
        if not isinstance(extraction, dict) or not isinstance(stock, dict):
            raise BuildError("in-place leaf report is incomplete")
        function_name = extraction.get("function")
        runtime_address = extraction.get("runtime_address")
        if not isinstance(function_name, str) or not isinstance(
            runtime_address,
            int,
        ):
            raise BuildError("in-place leaf extraction report is invalid")
        if not leaf:
            raise BuildError(f"in-place leaf {function_name} is empty")
        if function_name in in_place_names or function_name in functions:
            raise BuildError(
                f"ambiguous in-place leaf registration for {function_name}"
            )
        in_place_names.add(function_name)
        span_start = runtime_address
        span_end = span_start + len(leaf)
        payload_offset = preamble_bytes + span_start - run_base
        if (
            span_start < run_base
            or payload_offset < preamble_bytes
            or payload_offset + len(leaf) > len(base)
        ):
            raise BuildError(
                f"in-place leaf {function_name} span "
                f"[0x{span_start:08X},0x{span_end:08X}) exceeds the stock "
                "Apollo payload"
            )
        for other_start, other_end, other_name in in_place_ranges:
            if span_start < other_end and other_start < span_end:
                raise BuildError(
                    f"in-place leaf {function_name} overlaps in-place leaf "
                    f"{other_name}"
                )
        in_place_ranges.append((span_start, span_end, function_name))

        stock_size = stock.get("size")
        stock_sha256 = stock.get("sha256")
        if stock_size != len(leaf) or not isinstance(stock_sha256, str):
            raise BuildError(
                f"in-place leaf {function_name} stock pins do not describe "
                "its replacement span"
            )
        observed_stock = original[payload_offset:payload_offset + len(leaf)]
        observed_stock_sha256 = sha256(observed_stock)
        if observed_stock_sha256 != stock_sha256:
            raise BuildError(
                f"in-place leaf {function_name} stock SHA-256 differs at "
                f"0x{span_start:08X}: expected {stock_sha256}, observed "
                f"{observed_stock_sha256}"
            )

        literal_dependencies: list[dict[str, Any]] = []
        relocations = extraction.get("relocations")
        if not isinstance(relocations, list):
            raise BuildError(
                f"in-place leaf {function_name} relocation report is invalid"
            )
        for relocation in relocations:
            target_expected_hex = relocation.get("target_expected_hex")
            if target_expected_hex is None:
                continue
            target_address = relocation.get("target_address")
            if not isinstance(target_address, int):
                raise BuildError(
                    f"in-place leaf {function_name} literal target is invalid"
                )
            try:
                expected_literal = bytes.fromhex(str(target_expected_hex))
            except ValueError as error:
                raise BuildError(
                    f"in-place leaf {function_name} literal target bytes "
                    "are invalid hexadecimal"
                ) from error
            if not expected_literal:
                raise BuildError(
                    f"in-place leaf {function_name} literal target bytes "
                    "cannot be empty"
                )
            target_offset = (
                preamble_bytes + target_address - run_base
            )
            target_end = target_address + len(expected_literal)
            if (
                target_address < run_base
                or target_offset < preamble_bytes
                or target_offset + len(expected_literal) > len(base)
            ):
                raise BuildError(
                    f"in-place leaf {function_name} literal target "
                    f"0x{target_address:08X} exceeds the stock Apollo payload"
                )
            observed_literal = original[
                target_offset:target_offset + len(expected_literal)
            ]
            if observed_literal != expected_literal:
                raise BuildError(
                    f"in-place leaf {function_name} literal target "
                    f"0x{target_address:08X}: expected "
                    f"{expected_literal.hex()}, observed "
                    f"{observed_literal.hex()}"
                )
            protected_literal_ranges.append(
                (target_address, target_end, function_name)
            )
            literal_dependencies.append(
                {
                    "runtime_address": target_address,
                    "runtime_address_hex": f"0x{target_address:08X}",
                    "expected_hex": expected_literal.hex(),
                }
            )

        in_place_plans.append(
            {
                "function": function_name,
                "runtime_address": span_start,
                "runtime_address_hex": f"0x{span_start:08X}",
                "end_exclusive": span_end,
                "end_exclusive_hex": f"0x{span_end:08X}",
                "payload_offset": payload_offset,
                "size": len(leaf),
                "stock_sha256": observed_stock_sha256,
                "replacement_sha256": sha256(leaf),
                "replacement_hex": leaf.hex(),
                "literal_dependencies": literal_dependencies,
                "_leaf": leaf,
            }
        )

    for span_start, span_end, function_name in in_place_ranges:
        for target_start, target_end, dependency_owner in (
            protected_literal_ranges
        ):
            if span_start < target_end and target_start < span_end:
                raise BuildError(
                    f"in-place leaf {function_name} overlaps protected "
                    f"literal bytes required by {dependency_owner}"
                )

    for plan in in_place_plans:
        payload_offset = int(plan["payload_offset"])
        leaf = bytes(plan.pop("_leaf"))
        patched[payload_offset:payload_offset + len(leaf)] = leaf

    patched_sites: list[dict[str, Any]] = []
    for site in config["patch_sites"]:
        instruction_address = int(site["runtime_address"])
        payload_offset = (
            preamble_bytes + instruction_address - run_base
        )
        expected_hex = site.get("expected_hex")
        expected_size = site.get("expected_size")
        expected_sha256 = site.get("expected_sha256")
        if isinstance(expected_hex, str):
            if expected_size is not None or expected_sha256 is not None:
                raise BuildError(
                    f"{site['name']}: expected_hex cannot be combined with "
                    "expected_size/expected_sha256"
                )
            try:
                expected = bytes.fromhex(expected_hex)
            except ValueError as error:
                raise BuildError(
                    f"{site['name']}: expected_hex is not valid hexadecimal"
                ) from error
            expected_report = {"expected_hex": expected.hex()}
        else:
            if (
                not isinstance(expected_size, int)
                or expected_size < 1
                or not isinstance(expected_sha256, str)
                or len(expected_sha256) != 64
            ):
                raise BuildError(
                    f"{site['name']}: patch site requires expected_hex or "
                    "positive expected_size plus a SHA-256 digest"
                )
            if payload_offset < 0 or payload_offset + expected_size > len(patched):
                raise BuildError(
                    f"{site['name']} at 0x{instruction_address:08X}: "
                    "expected span exceeds the Apollo component"
                )
            expected = bytes(
                patched[payload_offset:payload_offset + expected_size]
            )
            observed_sha256 = sha256(expected)
            if observed_sha256 != expected_sha256:
                raise BuildError(
                    f"{site['name']} at 0x{instruction_address:08X}: expected "
                    f"SHA-256 {expected_sha256}, found {observed_sha256}"
                )
            expected_report = {
                "expected_size": expected_size,
                "expected_sha256": expected_sha256,
            }
        patch_end = instruction_address + len(expected)
        for span_start, span_end, function_name in in_place_ranges:
            if instruction_address < span_end and span_start < patch_end:
                raise BuildError(
                    f"{site['name']}: patch span overlaps in-place leaf "
                    f"{function_name}"
                )
        for target_start, target_end, dependency_owner in (
            protected_literal_ranges
        ):
            if instruction_address < target_end and target_start < patch_end:
                raise BuildError(
                    f"{site['name']}: patch span overlaps protected literal "
                    f"bytes required by {dependency_owner}"
                )
        if bytes(patched[payload_offset:payload_offset + len(expected)]) != expected:
            found = bytes(
                patched[payload_offset:payload_offset + len(expected)]
            ).hex()
            raise BuildError(
                f"{site['name']} at 0x{instruction_address:08X}: expected "
                f"{expected.hex()}, found {found}"
            )
        scatter_report = validate_scatter_literal_patch(
            image=patched,
            run_base=run_base,
            preamble_bytes=preamble_bytes,
            site=site,
            expected_size=len(expected),
        )
        function = functions.get(site["target_function"])
        if function is None:
            raise BuildError(f"missing function {site['target_function']}")
        target = overlay_runtime_address + function["offset"]
        branch = site["branch"]
        if branch == "bl":
            replacement = encode_thumb_bl(instruction_address, target)
            if len(expected) != 4:
                raise BuildError("Thumb BL patch site must be exactly four bytes")
            decoded = decode_thumb_branch(
                instruction_address,
                replacement,
                link=True,
            )
        elif branch == "b_w":
            if len(expected) < 4 or len(expected) % 2:
                raise BuildError(
                    "function-entry B.W replacement requires an even span of "
                    "at least four bytes"
                )
            replacement = (
                encode_thumb_b_w(instruction_address, target)
                + b"\x00\xbf" * ((len(expected) - 4) // 2)
            )
            decoded = decode_thumb_branch(
                instruction_address,
                replacement[:4],
                link=False,
            )
        elif branch == "copy":
            function_offset = int(function["offset"])
            function_size = int(function["size"])
            if len(expected) != function_size:
                raise BuildError(
                    "in-place source copy span must equal the compiled "
                    "function size"
                )
            replacement = overlay[
                function_offset:function_offset + function_size
            ]
            target = instruction_address
            decoded = instruction_address
        else:
            raise BuildError(f"unsupported branch encoding {branch}")
        if decoded != target:
            raise BuildError("generated Thumb branch failed its round-trip check")
        patched[payload_offset:payload_offset + len(expected)] = replacement
        patched_sites.append(
            {
                "name": site["name"],
                "runtime_address": instruction_address,
                "runtime_address_hex": f"0x{instruction_address:08X}",
                "payload_offset": payload_offset,
                "branch": branch,
                "replacement_hex": replacement.hex(),
                "target_function": site["target_function"],
                "target_address": target,
                "target_address_hex": f"0x{target:08X}",
                **(
                    {"scatter_literal": scatter_report}
                    if scatter_report is not None
                    else {}
                ),
                **expected_report,
            }
        )

    if len(patched) > 0x00FFFFFF:
        raise BuildError("patched Apollo main exceeds its 24-bit size field")
    first_word = u32le(patched, 0)
    struct.pack_into(
        "<I",
        patched,
        0,
        (first_word & 0xFF000000) | len(patched),
    )
    struct.pack_into(
        "<I",
        patched,
        4,
        zlib.crc32(patched[8:]) & 0xFFFFFFFF,
    )
    if run_base + len(patched) - preamble_bytes > 0x007F0000:
        raise BuildError("source overlay exceeds the conservative Apollo MRAM ceiling")

    details: dict[str, Any] = {
        "overlay_payload_offset": overlay_payload_offset,
        "overlay_runtime_address": overlay_runtime_address,
        "overlay_runtime_address_hex": f"0x{overlay_runtime_address:08X}",
        "overlay_end_exclusive": overlay_runtime_address + len(overlay),
        "overlay_end_exclusive_hex": (
            f"0x{overlay_runtime_address + len(overlay):08X}"
        ),
        "patched_sites": patched_sites,
    }
    if in_place_plans:
        details["patched_in_place_leaves"] = in_place_plans
    return bytes(patched), details


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(data)
    temporary.replace(path)


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write(
        path,
        (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8"),
    )


def build(
    *,
    root: Path,
    config_path: Path,
    output_dir: Path,
    clang: str,
    toolchain_profile: str | None = None,
    record_profile: bool = False,
) -> dict[str, Any]:
    config = load_config(config_path)
    if toolchain_profile is None:
        toolchain_profile = os.environ.get("OPENCFW_TOOLCHAIN_PROFILE")
    effective_toolchain, effective_expected, resolved_profile = (
        resolve_toolchain_profile(
            config,
            toolchain_profile,
            record=record_profile,
        )
    )
    primary_toolchain = dict(effective_toolchain)
    primary_flags = list(effective_toolchain["flags"])
    primary_flags.extend(
        compiler_source_prefix_flags(root, effective_toolchain)
    )
    primary_toolchain["flags"] = primary_flags
    config = {
        **config,
        "toolchain": primary_toolchain,
        "expected": effective_expected,
    }
    config = filter_config_for_profile(config, resolved_profile)
    include_dirs, normalized_include_dirs = resolve_toolchain_include_dirs(
        root,
        config["toolchain"],
    )
    isolated_leaf_configs = config.get("isolated_leaves", [])
    if (
        not isinstance(isolated_leaf_configs, list)
        or any(not isinstance(item, dict) for item in isolated_leaf_configs)
    ):
        raise BuildError("isolated_leaves must be a list of records")
    isolated_function_names = [
        item.get("function") for item in isolated_leaf_configs
    ]
    if any(not isinstance(name, str) for name in isolated_function_names):
        raise BuildError("every isolated leaf requires a function name")
    if len(set(isolated_function_names)) != len(isolated_function_names):
        raise BuildError("isolated leaf function names must be unique")
    relocated_leaf_configs = config.get("relocated_leaves", [])
    if (
        not isinstance(relocated_leaf_configs, list)
        or any(not isinstance(item, dict) for item in relocated_leaf_configs)
    ):
        raise BuildError("relocated_leaves must be a list of records")
    relocated_function_names = [
        item.get("function") for item in relocated_leaf_configs
    ]
    if any(not isinstance(name, str) for name in relocated_function_names):
        raise BuildError("every relocated leaf requires a function name")
    if len(set(relocated_function_names)) != len(relocated_function_names):
        raise BuildError("relocated leaf function names must be unique")
    in_place_leaf_configs = config.get("in_place_leaves", [])
    if (
        not isinstance(in_place_leaf_configs, list)
        or any(not isinstance(item, dict) for item in in_place_leaf_configs)
    ):
        raise BuildError("in_place_leaves must be a list of records")
    in_place_function_names = [
        item.get("function") for item in in_place_leaf_configs
    ]
    if any(not isinstance(name, str) for name in in_place_function_names):
        raise BuildError("every in-place leaf requires a function name")
    if len(set(in_place_function_names)) != len(in_place_function_names):
        raise BuildError("in-place leaf function names must be unique")
    configured_functions = config.get("functions")
    if (
        not isinstance(configured_functions, list)
        or any(not isinstance(name, str) for name in configured_functions)
    ):
        raise BuildError("overlay functions must be a list of names")
    unknown_isolated_functions = (
        set(isolated_function_names) - set(configured_functions)
    )
    if unknown_isolated_functions:
        raise BuildError(
            "isolated leaves are absent from the overlay function ABI: "
            f"{sorted(unknown_isolated_functions)}"
        )
    unknown_relocated_functions = (
        set(relocated_function_names) - set(configured_functions)
    )
    if unknown_relocated_functions:
        raise BuildError(
            "relocated leaves are absent from the overlay function ABI: "
            f"{sorted(unknown_relocated_functions)}"
        )
    ambiguous_appended_functions = set(isolated_function_names) & set(
        relocated_function_names
    )
    if ambiguous_appended_functions:
        raise BuildError(
            "functions cannot be both isolated and relocated leaves: "
            f"{sorted(ambiguous_appended_functions)}"
        )
    ambiguous_in_place_functions = set(in_place_function_names) & set(
        configured_functions
    )
    if ambiguous_in_place_functions:
        raise BuildError(
            "in-place leaves cannot be registered in the overlay function ABI: "
            f"{sorted(ambiguous_in_place_functions)}"
        )
    in_place_patch_targets = {
        site.get("target_function")
        for site in config.get("patch_sites", [])
        if isinstance(site, dict)
        and site.get("target_function") in set(in_place_function_names)
    }
    if in_place_patch_targets:
        raise BuildError(
            "patch sites cannot target fixed-address in-place leaves: "
            f"{sorted(in_place_patch_targets)}"
        )
    primary_functions = set(configured_functions) - set(
        isolated_function_names
    ) - set(relocated_function_names)
    if not primary_functions:
        raise BuildError("overlay requires at least one primary source function")

    source_configs = config.get("sources")
    if source_configs is None:
        source_configs = [config.get("source")]
    if (
        not isinstance(source_configs, list)
        or not source_configs
        or any(not isinstance(item, dict) for item in source_configs)
    ):
        raise BuildError("overlay config requires one or more source records")
    primary_source_paths = {
        resolve_below(root, item["path"]).resolve()
        for item in source_configs
        if isinstance(item.get("path"), str)
    }
    relocated_source_paths = {
        resolve_below(root, item["source"]["path"]).resolve()
        for item in relocated_leaf_configs
        if isinstance(item.get("source"), dict)
        and isinstance(item["source"].get("path"), str)
    }
    ambiguous_relocated_sources = (
        primary_source_paths & relocated_source_paths
    )
    if ambiguous_relocated_sources:
        raise BuildError(
            "relocated leaf source cannot enter the primary combined "
            "translation unit: "
            f"{sorted(str(path) for path in ambiguous_relocated_sources)}"
        )

    source_records: list[dict[str, Any]] = []
    source_paths: list[Path] = []
    for source_config in source_configs:
        source_relative = source_config.get("path")
        if not isinstance(source_relative, str):
            raise BuildError("every source record requires a path")
        source_path = resolve_below(root, source_relative)
        source = source_path.read_bytes()
        source_digest = sha256(source)
        if source_config.get("sha256") not in (None, source_digest):
            raise BuildError(f"{source_relative}: source SHA-256 differs from config")
        source_paths.append(source_path)
        record = {
            "path": str(source_path.relative_to(root)),
            "size": len(source),
            "sha256": source_digest,
        }
        for key in (
            "license",
            "origin",
            "upstream",
            "upstream_commit",
            "evidence",
        ):
            if key in source_config:
                record[key] = source_config[key]
        source_records.append(record)

    base_path = resolve_below(root, config["base"]["path"])
    base = base_path.read_bytes()
    base_digest = sha256(base)
    if len(base) != config["base"]["size"] or base_digest != config["base"]["sha256"]:
        raise BuildError("base Apollo main blob differs from overlay.json")

    output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=f"openCFW-{config['name']}-"
    ) as directory:
        temporary_root = Path(directory)
        if len(source_paths) == 1:
            translation_unit = source_paths[0]
        else:
            translation_unit = temporary_root / "overlay_translation_unit.c"
            includes = []
            for source_path in source_paths:
                source_text = str(source_path)
                if '"' in source_text or "\\" in source_text:
                    raise BuildError("source path cannot be represented in a C include")
                includes.append(f'#include "{source_text}"')
            atomic_write(
                translation_unit,
                ("\n".join(includes) + "\n").encode("utf-8"),
            )
        object_path = temporary_root / "overlay.o"
        overlay, functions, version, link_report = compile_overlay(
            clang=clang,
            source_path=translation_unit,
            object_path=object_path,
            config=config,
            include_dirs=include_dirs,
            expected_functions=primary_functions,
        )
        isolated_leaves = []
        for index, leaf_config in enumerate(isolated_leaf_configs):
            isolated_leaves.append(
                compile_isolated_leaf(
                    root=root,
                    clang=clang,
                    leaf_config=leaf_config,
                    object_path=temporary_root / f"isolated-leaf-{index}.o",
                    toolchain_profile=resolved_profile,
                    record=record_profile,
                )
            )
        (
            overlay,
            functions,
            link_report,
            isolated_leaf_reports,
        ) = append_isolated_leaves(
            overlay=overlay,
            functions=functions,
            link_report=link_report,
            leaves=isolated_leaves,
        )
        relocated_leaf_reports: list[dict[str, Any]] = []
        if relocated_leaf_configs:
            overlay_payload_offset = align_up(
                len(base),
                int(config["alignment"]),
            )
            overlay_runtime_address = (
                int(config["run_base"])
                + overlay_payload_offset
                - int(config["preamble_bytes"])
            )
            (
                overlay,
                functions,
                link_report,
                relocated_leaf_reports,
            ) = append_relocated_leaves(
                root=root,
                clang=clang,
                overlay=overlay,
                overlay_runtime_address=overlay_runtime_address,
                functions=functions,
                link_report=link_report,
                leaf_configs=relocated_leaf_configs,
                object_root=temporary_root,
                toolchain_profile=resolved_profile,
                record=record_profile,
            )
        in_place_leaves = []
        for index, leaf_config in enumerate(in_place_leaf_configs):
            in_place_leaves.append(
                compile_in_place_leaf(
                    root=root,
                    clang=clang,
                    leaf_config=leaf_config,
                    object_path=temporary_root / f"in-place-leaf-{index}.o",
                    toolchain_profile=resolved_profile,
                    record=record_profile,
                )
            )
    overlay_digest = sha256(overlay)
    expected = config["expected"]
    verify_expected(
        "overlay",
        len(overlay),
        overlay_digest,
        expected.get("overlay_size"),
        expected.get("overlay_sha256"),
    )
    component, details = patch_component(
        base=base,
        overlay=overlay,
        functions=functions,
        config=config,
        in_place_leaves=in_place_leaves,
    )
    component_digest = sha256(component)
    verify_expected(
        "component",
        len(component),
        component_digest,
        expected.get("component_size"),
        expected.get("component_sha256"),
    )

    overlay_artifact_name = config.get(
        "overlay_artifact",
        f"{config['name']}.text.bin",
    )
    if (
        not isinstance(overlay_artifact_name, str)
        or Path(overlay_artifact_name).name != overlay_artifact_name
    ):
        raise BuildError("overlay_artifact must be a plain filename")
    overlay_path = output_dir / overlay_artifact_name
    component_path = output_dir / "ota_s200_firmware_ota.bin"
    atomic_write(overlay_path, overlay)
    atomic_write(component_path, component)
    toolchain_report = {
        "executable": clang,
        "version": version,
        "profile": resolved_profile,
        "target": config["toolchain"]["target"],
        "flags": config["toolchain"]["flags"],
    }
    if normalized_include_dirs is not None:
        toolchain_report["include_dirs"] = normalized_include_dirs

    patched_in_place_leaves = details.get("patched_in_place_leaves", [])
    if len(patched_in_place_leaves) != len(in_place_leaves):
        raise BuildError("in-place leaf patch report count changed")
    in_place_leaf_reports: list[dict[str, Any]] = []
    for (_leaf, compile_report), patch_report in zip(
        in_place_leaves,
        patched_in_place_leaves,
    ):
        if (
            compile_report["extraction"]["function"]
            != patch_report["function"]
        ):
            raise BuildError("in-place leaf patch report order changed")
        in_place_leaf_reports.append(
            {
                **compile_report,
                "placement": patch_report,
            }
        )
    source_owned_in_place_bytes = sum(
        int(item["placement"]["size"]) for item in in_place_leaf_reports
    )
    patched_site_bytes = sum(
        len(bytes.fromhex(site["replacement_hex"]))
        for site in details["patched_sites"]
    )

    report = {
        "schema_version": 1,
        "name": config["name"],
        "firmware_version": config["firmware_version"],
        "sources": source_records,
        "toolchain": toolchain_report,
        "base": {
            "path": str(base_path.relative_to(root)),
            "size": len(base),
            "sha256": base_digest,
        },
        "overlay": {
            "artifact": str(overlay_path.relative_to(root)),
            "size": len(overlay),
            "sha256": overlay_digest,
            "functions": functions,
            "link": link_report,
            **details,
        },
        "component": {
            "artifact": str(component_path.relative_to(root)),
            "size": len(component),
            "sha256": component_digest,
            "opaque_base_bytes": (
                len(base)
                - int(config["preamble_bytes"])
                - patched_site_bytes
                - source_owned_in_place_bytes
            ),
            "source_owned_bytes": (
                len(overlay) + source_owned_in_place_bytes
            ),
            **(
                {
                    "source_owned_in_place_bytes": (
                        source_owned_in_place_bytes
                    )
                }
                if in_place_leaf_reports
                else {}
            ),
            "generated_wrapper_bytes": int(config["preamble_bytes"]),
            "generated_patch_site_bytes": patched_site_bytes,
            "replaced_stock_function_bytes": (
                source_owned_in_place_bytes
                + sum(
                    len(bytes.fromhex(site["replacement_hex"]))
                for site in details["patched_sites"]
                if site["branch"] in ("b_w", "copy")
                )
            ),
        },
    }
    if isolated_leaf_reports:
        report["isolated_leaves"] = isolated_leaf_reports
    if relocated_leaf_reports:
        report["relocated_leaves"] = relocated_leaf_reports
    if in_place_leaf_reports:
        report["in_place_leaves"] = in_place_leaf_reports
    if len(source_records) == 1:
        report["source"] = source_records[0]
    atomic_write_json(output_dir / "build-report.json", report)
    return report


def record_toolchain_profile_pins(
    config_path: Path,
    profile_id: str,
    report: dict[str, Any],
) -> None:
    """Persist observed overlay/component pins for a non-canonical profile.

    The config's own top-level ``toolchain``/``expected`` blocks (the reviewed
    ``apple-clang`` reference) are never touched.  The recorded profile is
    appended under ``toolchain_profiles`` with the exact compiler-version
    string as its reviewed family and the observed fail-closed pins.  The
    write preserves the hand-authored key order so the diff stays minimal.
    """

    if profile_id == DEFAULT_TOOLCHAIN_PROFILE:
        raise BuildError(
            "cannot record the canonical apple-clang profile; its pins are "
            "the reviewed reference"
        )
    data = json.loads(config_path.read_text(encoding="utf-8"))
    profiles = data.setdefault("toolchain_profiles", {})
    if not isinstance(profiles, dict):
        raise BuildError("toolchain_profiles must be an object")
    profile = profiles.get(profile_id)
    if not isinstance(profile, dict):
        profile = {}
    version = report["toolchain"]["version"]
    profile["reviewed_version_prefix"] = version
    profile["expected"] = {
        "overlay_size": report["overlay"]["size"],
        "overlay_sha256": report["overlay"]["sha256"],
        "component_size": report["component"]["size"],
        "component_sha256": report["component"]["sha256"],
    }
    profiles[profile_id] = profile

    record_leaf_profile_pins(data, profile_id, version, report)

    atomic_write(
        config_path,
        (json.dumps(data, indent=2) + "\n").encode("utf-8"),
    )


def record_leaf_profile_pins(
    data: dict[str, Any],
    profile_id: str,
    version: str,
    report: dict[str, Any],
) -> None:
    """Write per-leaf profile pins, suppressing entries identical to canonical.

    Assembly and other compiler-independent leaves keep the canonical pins and
    only record the reviewed compiler family; leaves whose bytes, placement, or
    relocation offsets shift under this toolchain record their own values.
    """

    def indexed(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
        result: dict[str, dict[str, Any]] = {}
        for item in items:
            function = item.get("extraction", {}).get("function")
            if isinstance(function, str):
                result[function] = item
        return result

    for config_key, kind in (
        ("isolated_leaves", "scalar"),
        ("in_place_leaves", "scalar"),
        ("relocated_leaves", "relocated"),
    ):
        reported = indexed(report.get(config_key, []))
        for leaf in data.get(config_key, []):
            if not isinstance(leaf, dict):
                continue
            item = reported.get(leaf.get("function"))
            if item is None:
                continue
            pins = item.get("pins", {})
            canonical = leaf.get("expected", {})
            leaf_profiles = leaf.setdefault("toolchain_profiles", {})
            entry = leaf_profiles.get(profile_id)
            if not isinstance(entry, dict):
                entry = {}
            entry["reviewed_version_prefix"] = version
            entry.pop("reviewed_version", None)
            entry.pop("expected", None)
            entry.pop("relocations", None)
            entry.pop("closure", None)

            if kind == "scalar":
                expected = {"size": pins["size"], "sha256": pins["sha256"]}
                if (
                    canonical.get("size") != expected["size"]
                    or canonical.get("sha256") != expected["sha256"]
                ):
                    entry["expected"] = expected
            else:
                expected = {
                    "size": pins["size"],
                    "sha256": pins["sha256"],
                    "alignment": pins["alignment"],
                    "offset": pins["offset"],
                    "unrelocated_sha256": pins["unrelocated_sha256"],
                }
                is_closure = isinstance(leaf.get("closure"), dict)
                if is_closure:
                    expected.update(
                        {
                            "closure_size": pins["closure_size"],
                            "closure_sha256": pins["closure_sha256"],
                            "rodata_offset": pins["rodata_offset"],
                        }
                    )
                    relocations = [
                        {
                            "offset": item_reloc["offset"],
                            "type": item_reloc["type"],
                            "symbol": item_reloc["symbol"],
                            **(
                                {"symbol_type": item_reloc["symbol_type"]}
                                if "symbol_type" in item_reloc
                                else {}
                            ),
                            **(
                                {
                                    "target_function": item_reloc[
                                        "target_function"
                                    ]
                                }
                                if "target_function" in item_reloc
                                else {}
                            ),
                            **(
                                {"target_address": item_reloc["target_address"]}
                                if "target_function" not in item_reloc
                                and item_reloc["type"] in (
                                    "R_ARM_THM_CALL",
                                    "R_ARM_THM_JUMP24",
                                    *ABSOLUTE_MOVWT_TYPES,
                                )
                                else {}
                            ),
                        }
                        for item_reloc in pins.get("relocations", [])
                    ]
                else:
                    relocations = [
                        {
                            "offset": item_reloc["offset"],
                            "type": item_reloc["type"],
                            "symbol": item_reloc["symbol"],
                            **(
                                {"symbol_type": item_reloc["symbol_type"]}
                                if "symbol_type" in item_reloc
                                else {}
                            ),
                            **(
                                {
                                    "target_function": item_reloc[
                                        "target_function"
                                    ]
                                }
                                if "target_function" in item_reloc
                                else {"target_address": item_reloc["target_address"]}
                            ),
                        }
                        for item_reloc in pins.get("relocations", [])
                    ]
                canonical_relocations = [
                    {
                        "offset": reloc.get("offset"),
                        "type": reloc.get("type"),
                        **(
                            {"symbol_type": reloc.get("symbol_type")}
                            if "symbol_type" in reloc
                            else {}
                        ),
                        **(
                            {
                                "symbol": reloc.get("symbol"),
                                **(
                                    {
                                        "target_function": reloc.get(
                                            "target_function"
                                        )
                                    }
                                    if "target_function" in reloc
                                    else {
                                        "target_address": reloc.get(
                                            "target_address"
                                        )
                                    }
                                ),
                            }
                            if is_closure
                            else {
                                "symbol": reloc.get("symbol"),
                                **(
                                    {
                                        "target_function": reloc.get(
                                            "target_function"
                                        )
                                    }
                                    if "target_function" in reloc
                                    else {
                                        "target_address": reloc.get(
                                            "target_address"
                                        )
                                    }
                                ),
                            }
                        ),
                    }
                    for reloc in leaf.get("relocations", [])
                ]
                observed_relocations = [
                    {
                        "offset": reloc["offset"],
                        "type": reloc["type"],
                        **(
                            {"symbol_type": reloc["symbol_type"]}
                            if "symbol_type" in reloc
                            else {}
                        ),
                        **(
                            {
                                "symbol": reloc["symbol"],
                                **(
                                    {
                                        "target_function": reloc[
                                            "target_function"
                                        ]
                                    }
                                    if "target_function" in reloc
                                    else {
                                        "target_address": reloc.get(
                                            "target_address"
                                        )
                                    }
                                ),
                            }
                            if is_closure
                            else {
                                "symbol": reloc["symbol"],
                                **(
                                    {
                                        "target_function": reloc[
                                            "target_function"
                                        ]
                                    }
                                    if "target_function" in reloc
                                    else {
                                        "target_address": reloc.get(
                                            "target_address"
                                        )
                                    }
                                ),
                            }
                        ),
                    }
                    for reloc in relocations
                ]
                expected_matches = all(
                    canonical.get(key) == expected[key] for key in expected
                )
                if not (
                    expected_matches
                    and canonical_relocations == observed_relocations
                ):
                    entry["expected"] = expected
                    entry["relocations"] = relocations
                if is_closure:
                    extraction = item.get("extraction", {})
                    observed_rodata = pins.get("rodata", {})
                    canonical_closure = leaf.get("closure", {})
                    canonical_rodata = canonical_closure.get("rodata", {})
                    closure_override: dict[str, Any] = {}
                    if extraction.get("section") != canonical_closure.get(
                        "text_section"
                    ):
                        closure_override["text_section"] = extraction.get(
                            "section"
                        )
                    observed_rodata_config = {
                        "section": observed_rodata.get("section"),
                        "size": observed_rodata.get("size"),
                        "sha256": observed_rodata.get("sha256"),
                        "alignment": observed_rodata.get("alignment"),
                        "symbols": [
                            {
                                "name": symbol.get("name"),
                                "offset": symbol.get("offset"),
                                "size": symbol.get("size"),
                            }
                            for symbol in observed_rodata.get("symbols", [])
                        ],
                    }
                    if observed_rodata_config != canonical_rodata:
                        closure_override["rodata"] = observed_rodata_config
                    if closure_override:
                        entry["closure"] = closure_override

            leaf_profiles[profile_id] = entry


def main(argv: list[str] | None = None) -> int:
    open_cfw_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--clang",
        default=os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
    )
    parser.add_argument(
        "--toolchain-profile",
        default=os.environ.get("OPENCFW_TOOLCHAIN_PROFILE"),
        help=(
            "reviewed toolchain profile to build and verify against "
            f"(default {DEFAULT_TOOLCHAIN_PROFILE!r}, the reviewed macOS "
            "reference)"
        ),
    )
    parser.add_argument(
        "--record-profile",
        action="store_true",
        help=(
            "compile with the current compiler, skip the reviewed pins, and "
            "write the observed overlay/component pins back into "
            "toolchain_profiles[<--toolchain-profile>]"
        ),
    )
    args = parser.parse_args(argv)
    config_path = args.config.resolve()
    if args.record_profile and not args.toolchain_profile:
        parser.error("--record-profile requires --toolchain-profile")
    report = build(
        root=open_cfw_root,
        config_path=config_path,
        output_dir=args.output_dir.resolve(),
        clang=args.clang,
        toolchain_profile=args.toolchain_profile,
        record_profile=args.record_profile,
    )
    overlay = report["overlay"]
    component = report["component"]
    if args.record_profile:
        record_toolchain_profile_pins(
            config_path,
            args.toolchain_profile,
            report,
        )
        print(
            f"Recorded toolchain profile {args.toolchain_profile!r} into "
            f"{config_path.name}"
        )
    print(
        f"Built {report['name']} source overlay: {overlay['size']} bytes at "
        f"{overlay['overlay_runtime_address_hex']} "
        f"[profile {report['toolchain']['profile']}]"
    )
    print(f"  overlay sha256: {overlay['sha256']}")
    print(
        f"  component: {component['size']} bytes, sha256 "
        f"{component['sha256']}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (BuildError, OSError) as error:
        print(f"openCFW component build: error: {error}", file=sys.stderr)
        raise SystemExit(1)
