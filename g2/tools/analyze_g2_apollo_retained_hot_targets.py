#!/usr/bin/env python3
"""Disassemble retained Apollo targets referenced by the AM pull-through frontier."""

from __future__ import annotations

import json
import sys
import hashlib
import re
from collections import Counter
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_GRP_CALL, CS_GRP_JUMP
from capstone import CS_MODE_LITTLE_ENDIAN, CS_MODE_MCLASS, CS_MODE_THUMB, Cs
from capstone.arm_const import ARM_OP_IMM


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import analyze_g2_source_closure_blocker_index as closure_index


IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
CORE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
APOLLO_OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
OUT = ROOT / "tools/manifests/g2-apollo-retained-hot-targets.json"
PC_BOUNDARY = ROOT / "tools/manifests/g2-am-pc-boundary-blockers.json"
AM142_SEMANTIC_REFERENCE = (
    ROOT /
    "components/apollo_main/core_overlay/runtime_liblc3_am142_semantic_model.c"
)
AM142_SEMANTIC_TEST = (
    ROOT / "tests/test_runtime_liblc3_am142_semantic_model.py"
)
AM142_PULLTHROUGH_CANDIDATE = (
    ROOT / "tools/manifests/g2-apollo-am142-pullthrough-candidate.json"
)
WINDOW_BYTES = 96
SPAN_LIMIT_BYTES = 512
CORE_REG_RE = re.compile(r"\b(?:r(?:1[0-2]|[0-9])|sp|lr|pc|ip|sl|fp|sb)\b")
VFP_REG_RE = re.compile(r"\b[sd](?:[12]?[0-9]|3[01])\b")
MEM_RE = re.compile(
    r"\[(?P<base>r(?:1[0-2]|[0-9])|sp|lr|ip|sl|fp|sb|pc)"
    r"(?:,\s*#(?P<offset>-?0x[0-9a-f]+|-?\d+))?\]"
)


def _apollo_main_regions() -> list[dict[str, object]]:
    manifest = json.loads(CORE_MANIFEST.read_text())
    return manifest["component_overrides"]["apollo_main"]["regions"]


def _apollo_overlay_source_paths() -> set[str]:
    manifest = json.loads(APOLLO_OVERLAY.read_text())
    return {
        str(row["path"])
        for row in manifest.get("sources", [])
        if isinstance(row, dict) and "path" in row
    }


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _am142_pullthrough_candidate_receipt() -> dict[str, object]:
    if not AM142_PULLTHROUGH_CANDIDATE.exists():
        return {
            "available": False,
            "reason": "run tools/verify_g2_apollo_am142_pullthrough_candidate.py",
        }
    receipt = json.loads(AM142_PULLTHROUGH_CANDIDATE.read_text(encoding="utf-8"))
    if receipt.get("source") != str(AM142_SEMANTIC_REFERENCE.relative_to(ROOT)):
        raise RuntimeError("AM142 pull-through receipt source changed")
    if receipt.get("source_sha256") != _file_sha256(AM142_SEMANTIC_REFERENCE):
        raise RuntimeError("AM142 pull-through receipt source digest changed")
    expected_symbols = [
        "open_cfw_am142_0x4ec718_semantic_model",
        "open_cfw_am142_0x4ec774_semantic_model",
        "open_cfw_am142_0x59a312_semantic_model",
        "open_cfw_am142_0x59a3d2_semantic_model",
        "open_cfw_am142_0x59aa84_semantic_model",
        "open_cfw_am142_0x59aec8_semantic_model",
        "open_cfw_am142_0x59af1e_semantic_model",
        "open_cfw_am142_0x59af42_semantic_model",
        "open_cfw_am142_0x59af54_semantic_model",
        "open_cfw_am142_0x59afa0_semantic_model",
        "open_cfw_am142_0x59b00e_semantic_model",
        "open_cfw_am142_0x59b272_semantic_model",
        "open_cfw_am142_0x59b2aa_semantic_model",
        "open_cfw_am142_0x59b33e_semantic_model",
        "open_cfw_am142_0x59b382_semantic_model",
        "open_cfw_am142_0x59b3de_semantic_model",
        "open_cfw_am142_0x59b454_semantic_model",
        "open_cfw_am142_0x59b52c_semantic_model",
        "open_cfw_am142_0x59b53c_semantic_model",
        "open_cfw_am142_0x59b654_semantic_model",
        "open_cfw_am142_0x59ba4a_semantic_model",
        "open_cfw_am142_0x59c052_semantic_model",
        "open_cfw_am142_0x59c060_semantic_model",
        "open_cfw_am142_0x59c530_semantic_model",
        "open_cfw_am142_0x59cb1e_semantic_model",
        "open_cfw_am142_0x59cb44_semantic_model",
        "open_cfw_am142_0x59cb6c_semantic_model",
        "open_cfw_am142_0x59cb98_semantic_model",
    ]
    if receipt.get("exported_text_symbols") != expected_symbols:
        raise RuntimeError("AM142 pull-through receipt symbols changed")
    return {
        "available": True,
        "manifest": str(AM142_PULLTHROUGH_CANDIDATE.relative_to(ROOT)),
        "source": receipt["source"],
        "source_sha256": receipt["source_sha256"],
        "toolchain_profile": receipt["toolchain_profile"],
        "target": receipt["target"],
        "object_size": receipt["object_size"],
        "object_sha256": receipt["object_sha256"],
        "symbol_count": receipt["symbol_count"],
        "undefined_symbol_count": len(receipt["undefined_symbols"]),
        "relocation_count": receipt["relocation_count"],
        "relocation_summary": receipt["relocation_summary"],
        "target_compile_verified": receipt["target_compile_verified"],
        "firmware_routing_status": receipt["firmware_routing_status"],
    }


def _firmware_base(regions: list[dict[str, object]]) -> int:
    bases = {
        int(region["target_address"]) - int(region["file_offset"])
        for region in regions
        if "target_address" in region and "file_offset" in region
    }
    if len(bases) != 1:
        raise RuntimeError(f"ambiguous Apollo address/file bases: {sorted(bases)}")
    return bases.pop()


def _region_for_address(
    regions: list[dict[str, object]],
    address: int,
) -> dict[str, object] | None:
    for region in regions:
        if "target_address" not in region:
            continue
        start = int(region.get("target_address", -1))
        end = start + int(region.get("size", 0))
        if start <= address < end:
            return region
    return None


def _owner_key(owner: dict[str, object] | None) -> str:
    if owner is None:
        return "unresolved:target_owner_missing"
    return (
        f"{owner['component']}:{owner['region']}:"
        f"{owner['address_status']}"
    )


def _target_owner(
    regions: list[dict[str, object]],
    address: int,
) -> dict[str, object] | None:
    region = _region_for_address(regions, address)
    if region is None:
        return None
    return {
        "component": "apollo_main",
        "region": region["name"],
        "address_status": region["address_status"],
        "region_start": region["target_address"],
        "offset_in_region": address - int(region["target_address"]),
    }


def _instruction_rows(
    md: Cs,
    image: bytes,
    base: int,
    address: int,
    region: dict[str, object],
    regions: list[dict[str, object]],
) -> list[dict[str, object]]:
    region_end = int(region["target_address"]) + int(region["size"])
    window_end = min(address + WINDOW_BYTES, region_end)
    file_offset = address - base
    data = image[file_offset:file_offset + (window_end - address)]
    rows = []
    for insn in md.disasm(data, address):
        groups = []
        if insn.group(CS_GRP_CALL):
            groups.append("call")
        if insn.group(CS_GRP_JUMP):
            groups.append("jump")
        target = None
        target_owner = None
        if insn.operands and insn.operands[-1].type == ARM_OP_IMM:
            target = insn.operands[-1].imm & ~1
            target_owner = _target_owner(regions, target)
        rows.append({
            "address": insn.address,
            "offset": insn.address - address,
            "instruction": f"{insn.mnemonic} {insn.op_str}".strip(),
            "size": insn.size,
            "groups": groups,
            "target_address": target,
            "target_owner": target_owner,
        })
    return rows


def _decode_rows(
    md: Cs,
    data: bytes,
    address: int,
    regions: list[dict[str, object]],
) -> list[dict[str, object]]:
    rows = []
    for insn in md.disasm(data, address):
        groups = []
        if insn.group(CS_GRP_CALL):
            groups.append("call")
        if insn.group(CS_GRP_JUMP):
            groups.append("jump")
        target = None
        target_owner = None
        if insn.operands and insn.operands[-1].type == ARM_OP_IMM:
            target = insn.operands[-1].imm & ~1
            target_owner = _target_owner(regions, target)
        rows.append({
            "address": insn.address,
            "offset": insn.address - address,
            "instruction": f"{insn.mnemonic} {insn.op_str}".strip(),
            "size": insn.size,
            "groups": groups,
            "target_address": target,
            "target_owner": target_owner,
        })
    return rows


def _bounded_span(
    md: Cs,
    image: bytes,
    base: int,
    address: int,
    region: dict[str, object],
    regions: list[dict[str, object]],
) -> dict[str, object]:
    region_end = int(region["target_address"]) + int(region["size"])
    limit_end = min(address + SPAN_LIMIT_BYTES, region_end)
    file_offset = address - base
    data = image[file_offset:file_offset + (limit_end - address)]
    rows = []
    terminal = None
    for row in _decode_rows(md, data, address, regions):
        rows.append(row)
        if row["groups"]:
            terminal = row
            break
    if rows:
        size = rows[-1]["offset"] + rows[-1]["size"]
    else:
        size = 0
    if terminal is None and size == len(data):
        status = "limit_reached_without_control_flow"
    elif terminal is None:
        status = "decode_stopped_without_control_flow"
    else:
        status = "terminated_at_control_flow"
    span_bytes = image[file_offset:file_offset + size]
    features = _feature_summary(rows)
    return {
        "status": status,
        "byte_length": size,
        "sha256": hashlib.sha256(span_bytes).hexdigest() if span_bytes else None,
        "instruction_count": len(rows),
        "terminal_instruction": terminal,
        "control_flow_counts": _control_flow_counts(rows),
        "control_flow_owner_counts": _control_flow_owner_counts(rows),
        "feature_summary": features,
        "arithmetic_motif": _arithmetic_motif_summary(rows, features),
        "instructions": rows,
    }


def _memory_key(base: str, offset: int) -> str:
    if offset < 0:
        return f"{base}-0x{-offset:x}"
    return f"{base}+0x{offset:x}"


def _feature_summary(instructions: list[dict[str, object]]) -> dict[str, object]:
    core_reads: Counter[str] = Counter()
    core_writes: Counter[str] = Counter()
    vfp_reads: Counter[str] = Counter()
    vfp_writes: Counter[str] = Counter()
    memory_reads: Counter[str] = Counter()
    memory_writes: Counter[str] = Counter()
    immediates: Counter[int] = Counter()
    for row in instructions:
        instruction = str(row["instruction"]).lower()
        if " " not in instruction:
            continue
        mnemonic, operand_text = instruction.split(" ", 1)
        operands = [operand.strip() for operand in operand_text.split(",")]
        if not operands:
            continue
        destination = operands[0]
        is_store = mnemonic.startswith("str") or mnemonic.startswith("vstr")
        for match in re.finditer(r"#(-?0x[0-9a-f]+|-?\d+)", instruction):
            immediates[int(match.group(1), 0)] += 1
        for match in MEM_RE.finditer(instruction):
            base = match.group("base")
            offset = int(match.group("offset"), 0) if match.group("offset") else 0
            key = _memory_key(base, offset)
            if is_store:
                memory_writes[key] += 1
            else:
                memory_reads[key] += 1
            core_reads[base] += 1
        if re.fullmatch(CORE_REG_RE, destination):
            core_writes[destination] += 1
        elif re.fullmatch(VFP_REG_RE, destination):
            vfp_writes[destination] += 1
        for index, operand in enumerate(operands):
            if index == 0 and not is_store:
                continue
            for reg in CORE_REG_RE.findall(operand):
                if is_store or reg != destination:
                    core_reads[reg] += 1
            for reg in VFP_REG_RE.findall(operand):
                if is_store or reg != destination:
                    vfp_reads[reg] += 1
        if is_store:
            for reg in CORE_REG_RE.findall(destination):
                core_reads[reg] += 1
            for reg in VFP_REG_RE.findall(destination):
                vfp_reads[reg] += 1
    return {
        "core_reads": dict(sorted(core_reads.items())),
        "core_writes": dict(sorted(core_writes.items())),
        "vfp_reads": dict(sorted(vfp_reads.items())),
        "vfp_writes": dict(sorted(vfp_writes.items())),
        "memory_reads": dict(sorted(memory_reads.items())),
        "memory_writes": dict(sorted(memory_writes.items())),
        "immediates": [
            {"value": value, "count": count}
            for value, count in sorted(immediates.items())
        ],
    }


def _offsets_for_base(keys: dict[str, int], base: str) -> list[int]:
    offsets = []
    prefix = f"{base}+0x"
    for key in keys:
        if key.startswith(prefix):
            offsets.append(int(key[len(prefix):], 16))
    return sorted(offsets)


def _semantic_reference_evidence() -> dict[str, object]:
    reference_path = str(AM142_SEMANTIC_REFERENCE.relative_to(ROOT))
    reference_is_routed = reference_path in _apollo_overlay_source_paths()
    return {
        "source_sha256": _file_sha256(AM142_SEMANTIC_REFERENCE),
        "test_sha256": _file_sha256(AM142_SEMANTIC_TEST),
        "overlay_source_listed": reference_is_routed,
        "host_test_command": (
            "python3 -m unittest "
            "tests.test_runtime_liblc3_am142_semantic_model"
        ),
        "host_test_platform": "macOS clang shared-library build",
        "firmware_routing_status": (
            "routed_into_overlay"
            if reference_is_routed else
            "not_yet_routed_into_overlay"
        ),
    }


def _integer_affine_motif_summary(
    instructions: list[dict[str, object]],
    features: dict[str, object],
) -> dict[str, object] | None:
    sequence = [str(row["instruction"]) for row in instructions]
    expected = [
        "sub.w lr, sl, ip",
        "sub.w ip, r1, ip",
        "sub.w r2, sl, r3",
        "mul r2, r2, ip",
        "mla r2, lr, r3, r2",
        "add.w r3, lr, lr, lsl #1",
        "lsls r3, r3, #4",
        "b #0x59c086",
    ]
    if sequence != expected:
        return None
    terminal = instructions[-1]
    abi_contract = {
        "integer_inputs": ["r1", "r3", "ip", "sl"],
        "integer_outputs": ["r2", "r3", "ip", "lr"],
        "integer_temporaries": [],
        "wraparound_semantics": "uint32_t low-word ARM arithmetic",
        "branch_condition": {
            "comparison": "unconditional",
            "target_address": 0x0059C086,
        },
    }
    return {
        "kind": "integer_affine_index_update",
        "terminal_branch": {
            "instruction": terminal["instruction"],
            "branch_target": terminal["target_address"],
        },
        "source_model": {
            "summary": (
                "derive an affine integer accumulator from sl/ip/r1/r3, "
                "scale the lr-derived index by forty-eight, and branch "
                "unconditionally into the same retained interval"
            ),
            "state_inputs": ["r1", "r3", "ip", "sl"],
            "operations": [
                "lr = sl - ip",
                "ip = r1 - ip",
                "r2 = (sl - r3) * ip",
                "r2 += lr * r3",
                "r3 = (lr + (lr << 1)) << 4",
                "branch to 0x59c086",
            ],
            "abi_contract": abi_contract,
            "abi_validation": {
                "matches_decoded_features": (
                    terminal["target_address"] == 0x0059C086
                    and features["memory_reads"] == {}
                    and features["memory_writes"] == {}
                    and features["vfp_reads"] == {}
                    and features["vfp_writes"] == {}
                ),
                "observed_branch_target": terminal["target_address"],
                "observed_instruction_sequence": sequence,
            },
            "c_translation_status": (
                "semantic_model_ready_requires_same_interval_routing"
            ),
            "reference_source": (
                "components/apollo_main/core_overlay/"
                "runtime_liblc3_am142_semantic_model.c"
            ),
            "reference_tests": [
                "tests/test_runtime_liblc3_am142_semantic_model.py",
            ],
            "reference_evidence": _semantic_reference_evidence(),
        },
    }


def _threshold_offset_branch_motif_summary(
    instructions: list[dict[str, object]],
    features: dict[str, object],
) -> dict[str, object] | None:
    sequence = [str(row["instruction"]) for row in instructions]
    expected = [
        "add.w r0, r1, #0x400",
        "cmp r4, #1",
        "ble.w #0x59b8b2",
    ]
    if sequence != expected:
        return None
    terminal = instructions[-1]
    abi_contract = {
        "integer_inputs": ["r1", "r4"],
        "integer_outputs": ["r0"],
        "integer_temporaries": [],
        "wraparound_semantics": "uint32_t low-word add for r0",
        "branch_condition": {
            "comparison": "signed r4 <= 1",
            "target_address": 0x0059B8B2,
        },
    }
    return {
        "kind": "threshold_offset_branch",
        "terminal_branch": {
            "instruction": terminal["instruction"],
            "branch_target": terminal["target_address"],
        },
        "source_model": {
            "summary": (
                "add the fixed 0x400 offset to r1 and branch into the same "
                "retained interval when signed r4 is at most one"
            ),
            "state_inputs": ["r1", "r4"],
            "operations": [
                "r0 = r1 + 0x400",
                "branch to 0x59b8b2 when signed r4 <= 1",
            ],
            "abi_contract": abi_contract,
            "abi_validation": {
                "matches_decoded_features": (
                    terminal["target_address"] == 0x0059B8B2
                    and features["memory_reads"] == {}
                    and features["memory_writes"] == {}
                    and features["vfp_reads"] == {}
                    and features["vfp_writes"] == {}
                ),
                "observed_branch_target": terminal["target_address"],
                "observed_instruction_sequence": sequence,
            },
            "c_translation_status": (
                "semantic_model_ready_requires_same_interval_routing"
            ),
            "reference_source": (
                "components/apollo_main/core_overlay/"
                "runtime_liblc3_am142_semantic_model.c"
            ),
            "reference_tests": [
                "tests/test_runtime_liblc3_am142_semantic_model.py",
            ],
            "reference_evidence": _semantic_reference_evidence(),
        },
    }


def _stack_parabolic_compare_motif_summary(
    instructions: list[dict[str, object]],
    features: dict[str, object],
) -> dict[str, object] | None:
    sequence = [str(row["instruction"]) for row in instructions]
    expected = [
        "movs r2, #1",
        "add.w r3, sp, #0x4c",
        "add.w ip, sp, #0x10c",
        "ldr.w lr, [ip]",
        "vldr s9, [r3]",
        "vadd.f32 s9, s16, s9",
        "lsl.w lr, lr, #1",
        "vmov s10, lr",
        "vcvt.f32.s32 s10, s10",
        "vadd.f32 s10, s10, s6",
        "vmov.f32 s11, #1.000000e+00",
        "vmul.f32 s9, s9, s9",
        "vadd.f32 s10, s10, s11",
        "vmul.f32 s11, s9, s8",
        "vmul.f32 s12, s10, s7",
        "vcmp.f32 s12, s11",
        "vmrs apsr_nzcv, fpscr",
        "bpl #0x59a420",
    ]
    if sequence != expected:
        return None
    terminal = instructions[-1]
    abi_contract = {
        "integer_inputs": ["sp"],
        "integer_outputs": ["r2", "r3", "ip", "lr"],
        "vfp_inputs": ["s6", "s7", "s8", "s16"],
        "vfp_outputs": ["s9", "s10", "s11", "s12"],
        "memory_inputs": [
            {"base": "sp", "offset": 0x4C, "role": "stack_float"},
            {"base": "sp", "offset": 0x10C, "role": "stack_word"},
        ],
        "branch_condition": {
            "comparison": "(float((int32_t)(stack_word << 1)) + s6 + 1.0f) * s7 >= (s16 + stack_float)^2 * s8",
            "target_address": 0x0059A420,
        },
    }
    return {
        "kind": "stack_parabolic_compare_branch",
        "terminal_branch": {
            "instruction": terminal["instruction"],
            "branch_target": terminal["target_address"],
        },
        "source_model": {
            "summary": (
                "load one integer and one float from the caller stack frame, "
                "square the s16-adjusted float term, compare the two scaled "
                "products, and branch when the VFP compare result is nonnegative"
            ),
            "state_inputs": [
                "int32_t *(sp+0x10c)",
                "float *(sp+0x4c)",
                "s6",
                "s7",
                "s8",
                "s16",
            ],
            "operations": [
                "r2 = 1",
                "lr = (int32_t)((uint32_t)load32(sp + 0x10c) << 1)",
                "s9 = s16 + load_float(sp + 0x4c)",
                "s10 = float(lr) + s6 + 1.0f",
                "s9 = s9 * s9",
                "s11 = s9 * s8",
                "s12 = s10 * s7",
                "branch to 0x59a420 when s12 >= s11",
            ],
            "abi_contract": abi_contract,
            "abi_validation": {
                "matches_decoded_features": (
                    terminal["target_address"] == 0x0059A420
                    and features["memory_reads"] == {
                        "ip+0x0": 1,
                        "r3+0x0": 1,
                    }
                    and features["vfp_writes"].get("s12") == 2
                ),
                "observed_branch_target": terminal["target_address"],
                "observed_instruction_sequence": sequence,
            },
            "c_translation_status": (
                "semantic_model_ready_requires_same_interval_routing"
            ),
            "reference_source": (
                "components/apollo_main/core_overlay/"
                "runtime_liblc3_am142_semantic_model.c"
            ),
            "reference_tests": [
                "tests/test_runtime_liblc3_am142_semantic_model.py",
            ],
            "reference_evidence": _semantic_reference_evidence(),
        },
    }


def _call_shim_motif_summary(
    instructions: list[dict[str, object]],
    features: dict[str, object],
) -> dict[str, object] | None:
    sequence = [str(row["instruction"]) for row in instructions]
    shim_specs = {
        (
            "mov r0, sl",
            "bl #0x44104c",
        ): {
            "summary": (
                "forward sl as r0 into the retained helper at 0x0044104c"
            ),
            "state_inputs": ["sl"],
            "operations": [
                "r0 = sl",
                "call 0x0044104c",
            ],
            "integer_inputs": ["sl"],
            "integer_outputs": ["r0"],
            "argument_registers": {"r0": "sl"},
            "call_target": 0x0044104C,
        },
        (
            "mov sb, r0",
            "movs r2, #3",
            "movs r1, #0",
            "mov r0, sb",
            "bl #0x43f09a",
        ): {
            "summary": (
                "save the incoming r0 in sb, set fixed arguments r1=0 and "
                "r2=3, restore r0, and call the retained helper at 0x0043f09a"
            ),
            "state_inputs": ["r0"],
            "operations": [
                "sb = r0",
                "r2 = 3",
                "r1 = 0",
                "r0 = sb",
                "call 0x0043f09a",
            ],
            "integer_inputs": ["r0"],
            "integer_outputs": ["r0", "r1", "r2", "sb"],
            "argument_registers": {"r0": "incoming r0", "r1": 0, "r2": 3},
            "call_target": 0x0043F09A,
        },
    }
    spec = shim_specs.get(tuple(sequence))
    if spec is None:
        return None
    terminal = instructions[-1]
    call_target = int(spec["call_target"])
    abi_contract = {
        "integer_inputs": spec["integer_inputs"],
        "integer_outputs": spec["integer_outputs"],
        "argument_registers": spec["argument_registers"],
        "terminal_call_target": call_target,
        "callee_ownership": "retained_external_owner",
    }
    return {
        "kind": "call_shim_to_retained_helper",
        "terminal_call": {
            "instruction": terminal["instruction"],
            "call_target": terminal["target_address"],
            "callee_owner": terminal["target_owner"],
        },
        "source_model": {
            "summary": spec["summary"],
            "state_inputs": spec["state_inputs"],
            "operations": spec["operations"],
            "abi_contract": abi_contract,
            "abi_validation": {
                "matches_decoded_features": (
                    terminal["target_address"] == call_target
                    and features["memory_reads"] == {}
                    and features["memory_writes"] == {}
                    and features["vfp_reads"] == {}
                    and features["vfp_writes"] == {}
                ),
                "observed_call_target": terminal["target_address"],
                "observed_instruction_sequence": sequence,
            },
            "c_translation_status": (
                "semantic_model_ready_requires_cross_retained_callee_resolution"
            ),
            "reference_source": (
                "components/apollo_main/core_overlay/"
                "runtime_liblc3_am142_semantic_model.c"
            ),
            "reference_tests": [
                "tests/test_runtime_liblc3_am142_semantic_model.py",
            ],
            "reference_evidence": _semantic_reference_evidence(),
        },
    }


def _arithmetic_motif_summary(
    instructions: list[dict[str, object]],
    features: dict[str, object],
) -> dict[str, object] | None:
    memory_reads = features["memory_reads"]
    memory_writes = features["memory_writes"]
    r5_offsets = _offsets_for_base(memory_reads, "r5")
    r6_offsets = _offsets_for_base(memory_reads, "r6")
    stack_offsets = _offsets_for_base(memory_writes, "sp")
    terminal = next((row for row in reversed(instructions) if row["groups"]), None)
    if not r5_offsets or not r6_offsets:
        return (
            _integer_affine_motif_summary(instructions, features)
            or _threshold_offset_branch_motif_summary(instructions, features)
            or _stack_parabolic_compare_motif_summary(instructions, features)
            or _call_shim_motif_summary(instructions, features)
        )
    lanes = []
    for index, (value_offset, coeff_offset) in enumerate(
        zip(r5_offsets, r6_offsets),
        start=1,
    ):
        lanes.append({
            "lane": index,
            "value_base": "r5",
            "value_offset": value_offset,
            "coefficient_base": "r6",
            "coefficient_offset": coeff_offset,
            "stack_zero_offset": (
                stack_offsets[index - 1]
                if index - 1 < len(stack_offsets) else None
            ),
        })
    branch_target = None if terminal is None else terminal["target_address"]
    abi_contract = {
        "integer_inputs": ["r0", "r1", "r5", "r6"],
        "integer_outputs": ["r0", "r2", "r4"],
        "integer_temporaries": ["r1"],
        "vfp_inputs": ["s2", "s3", "s4", "s16"],
        "vfp_outputs": ["s4", "s5", "s6", "s7", "s16"],
        "stack_zero_writes": [
            {"offset": 0x13C, "value": 0},
            {"offset": 0x140, "value": 0},
            {"offset": 0x144, "value": 0},
        ],
        "memory_inputs": [
            {"base": "r5", "offset": 0xB4, "role": "delta_1"},
            {"base": "r5", "offset": 0xB8, "role": "delta_2"},
            {"base": "r5", "offset": 0xBC, "role": "delta_3"},
            {"base": "r6", "offset": 0x34, "role": "coefficient_1"},
            {"base": "r6", "offset": 0x38, "role": "coefficient_2"},
            {"base": "r6", "offset": 0x3C, "role": "coefficient_3"},
        ],
        "branch_condition": {
            "residual_register": "r2",
            "comparison": "r2 >= 10",
            "target_address": 0x0059A45C,
        },
    }
    abi_validation = {
        "matches_decoded_features": (
            r5_offsets == [0xB4, 0xB8, 0xBC]
            and r6_offsets == [0x34, 0x38, 0x3C]
            and stack_offsets == [0x13C, 0x140, 0x144]
            and branch_target == 0x0059A45C
            and features["vfp_writes"].get("s16") == 4
        ),
        "observed_r5_offsets": r5_offsets,
        "observed_r6_offsets": r6_offsets,
        "observed_stack_zero_offsets": stack_offsets,
        "observed_branch_target": branch_target,
        "observed_s16_write_count": features["vfp_writes"].get("s16", 0),
    }
    return {
        "kind": "squared_delta_accumulator",
        "initial_integer_delta": "r1-r0",
        "accumulator_register": "s16",
        "input_value_count": len(r5_offsets),
        "coefficient_count": len(r6_offsets),
        "stack_zero_count": len(stack_offsets),
        "lanes": lanes,
        "terminal_compare": {
            "instruction": (
                None if len(instructions) < 2 else
                instructions[-2]["instruction"]
            ),
            "branch_instruction": None if terminal is None else terminal[
                "instruction"],
            "branch_target": None if terminal is None else terminal[
                "target_address"],
        },
        "source_model": {
            "summary": (
                "accumulate four weighted squared/delta terms, derive a "
                "terminal residual integer delta, and branch when that "
                "residual is at least ten"
            ),
            "state_inputs": [
                "r0",
                "r1",
                "s2",
                "s3",
                "s16",
                "uint32_t *(r5+0xb4..0xbc)",
                "float *(r6+0x34..0x3c)",
            ],
            "operations": [
                "r4 = r1 - r0",
                "s16 -= float(s4) * s2",
                "stack[0x13c] = 0",
                "d1 = load32(r5 + 0xb4); r0 -= d1; s16 -= float(d1) * coeff[0]",
                "stack[0x140] = 0",
                "d2 = load32(r5 + 0xb8); r0 -= d2; s16 -= float(d2) * coeff[1]",
                "stack[0x144] = 0",
                "d3 = load32(r5 + 0xbc); residual = r0 - d3; s16 -= float(d3) * coeff[2]",
                "branch to 0x59a45c when residual >= 10",
            ],
            "abi_contract": abi_contract,
            "abi_validation": abi_validation,
            "c_translation_status": "semantic_model_ready_requires_register_abi_mapping",
            "reference_source": (
                "components/apollo_main/core_overlay/"
                "runtime_liblc3_am142_semantic_model.c"
            ),
            "reference_tests": [
                "tests/test_runtime_liblc3_am142_semantic_model.py",
            ],
            "reference_evidence": _semantic_reference_evidence(),
        },
    }


def _call_relation_counts(call_site_examples: list[dict[str, object]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for site in call_site_examples:
        relation = str(site["target_relation"])
        counts[relation] = counts.get(relation, 0) + 1
    return dict(sorted(counts.items()))


def _control_flow_counts(instructions: list[dict[str, object]]) -> dict[str, int]:
    counts = {"call": 0, "jump": 0}
    for insn in instructions:
        groups = insn["groups"]
        if "call" in groups:
            counts["call"] += 1
        if "jump" in groups:
            counts["jump"] += 1
    return {key: value for key, value in counts.items() if value}


def _control_flow_owner_counts(
    instructions: list[dict[str, object]],
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for insn in instructions:
        if not insn["groups"] or insn["target_address"] is None:
            continue
        key = _owner_key(insn["target_owner"])
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _window_bytes(
    image: bytes,
    base: int,
    address: int,
    region: dict[str, object],
) -> bytes:
    region_end = int(region["target_address"]) + int(region["size"])
    window_end = min(address + WINDOW_BYTES, region_end)
    file_offset = address - base
    return image[file_offset:file_offset + (window_end - address)]


def _target_shape(
    call_site_examples: list[dict[str, object]],
    instructions: list[dict[str, object]],
) -> str:
    relation_counts = _call_relation_counts(call_site_examples)
    if not instructions:
        return "nondecoding_branch_target"
    first = str(instructions[0]["instruction"]).split(" ", 1)[0]
    if first.startswith("b"):
        return "branch_trampoline_or_midblock_label"
    if relation_counts.get("outside_function", 0) == len(call_site_examples):
        return "direct_subroutine_entry"
    return "mixed_entry_or_internal_label"


def _dependency_class(row: dict[str, object]) -> str:
    owner_counts = row["control_flow_owner_counts"]
    if not owner_counts:
        return "isolated_window"
    owners = set(owner_counts)
    if owners == {row["owner"]}:
        return "same_retained_interval_only"
    return "cross_retained_dependency"


def _pull_through_sort_key(row: dict[str, object]) -> tuple[int, int, int]:
    class_rank = {
        "isolated_window": 0,
        "same_retained_interval_only": 1,
        "cross_retained_dependency": 2,
    }[_dependency_class(row)]
    return (class_rank, -int(row["count"]), int(row["target_address"]))


def _cluster_sort_key(cluster: dict[str, object]) -> tuple[int, int, int]:
    class_rank = {
        "isolated_window": 0,
        "same_retained_interval_only": 1,
        "cross_retained_dependency": 2,
    }[str(cluster["dependency_class"])]
    return (
        class_rank,
        -int(cluster["total_call_site_count"]),
        int(cluster["start_address"]),
    )


def _source_recovery_status(
    cluster: dict[str, object],
    targets: list[dict[str, object]],
    instructions: list[dict[str, object]],
) -> dict[str, object]:
    terminal = instructions[-1] if instructions and instructions[-1]["groups"] else None
    mnemonics = Counter(
        str(row["instruction"]).split(" ", 1)[0]
        for row in instructions
        if row.get("instruction")
    )
    memory_instruction_count = sum(
        1 for row in instructions
        if "[" in str(row.get("instruction", ""))
        and "]" in str(row.get("instruction", ""))
    )
    vfp_instruction_count = sum(
        1 for row in instructions
        if str(row.get("instruction", "")).startswith("v")
    )
    return {
        "status": "requires_c_pull_through",
        "current_representation": "retained_exact_helper_bytes",
        "decoded": bool(instructions),
        "start_address": cluster["start_address"],
        "end_address": cluster["end_address"],
        "byte_length": int(cluster["end_address"]) - int(cluster["start_address"]),
        "entrypoints": [
            {
                "target_address": target["target_address"],
                "bounded_span_byte_length": target["bounded_span"][
                    "byte_length"],
                "call_site_count": target["ingress_summary"][
                    "call_site_count"],
            }
            for target in targets
        ],
        "terminal_branch": (
            None if terminal is None else {
                "instruction": terminal["instruction"],
                "target_address": terminal["target_address"],
                "target_owner": terminal["target_owner"],
            }
        ),
        "translation_summary": {
            "shape": (
                "straight_line_to_terminal_branch"
                if terminal is not None else
                "straight_line_without_terminal_branch"
            ),
            "instruction_count": len(instructions),
            "memory_instruction_count": memory_instruction_count,
            "vfp_instruction_count": vfp_instruction_count,
            "mnemonic_counts": dict(sorted(mnemonics.items())),
            "first_instruction": (
                None if not instructions else instructions[0]["instruction"]),
            "last_instruction": (
                None if not instructions else instructions[-1]["instruction"]),
        },
        "source_obligations": [
            "preserve all listed entrypoint addresses or provide equivalent overlay routing",
            "preserve live register and VFP side effects used by the retained callers",
            "preserve terminal branch target and condition",
            "remove retained .inst transcript bytes from the final source-owned implementation",
        ],
        "next_action": (
            "replace this retained helper-byte span with source-owned C "
            "that preserves both entrypoints and the terminal branch contract"
        ),
    }


def _merge_direct_subroutine_clusters(
    direct_subroutines: list[dict[str, object]],
    md: Cs,
    image: bytes,
    base: int,
    regions: list[dict[str, object]],
) -> list[dict[str, object]]:
    clusters = []
    for row in sorted(
        direct_subroutines,
        key=lambda item: (str(item["region"]), int(item["target_address"])),
    ):
        start = int(row["target_address"])
        end = start + int(row["bounded_span"]["byte_length"])
        if not clusters or clusters[-1]["region"] != row["region"] or start > clusters[-1]["end_address"]:
            clusters.append({
                "region": row["region"],
                "start_address": start,
                "end_address": end,
                "targets": [],
            })
        cluster = clusters[-1]
        cluster["end_address"] = max(int(cluster["end_address"]), end)
        cluster["targets"].append(row)
    for cluster in clusters:
        targets = cluster["targets"]
        start = int(cluster["start_address"])
        end = int(cluster["end_address"])
        span = image[start - base:end - base]
        instructions = _decode_rows(md, span, start, regions)
        classes = [str(target["dependency_class"]) for target in targets]
        if "cross_retained_dependency" in classes:
            dependency_class = "cross_retained_dependency"
        elif "same_retained_interval_only" in classes:
            dependency_class = "same_retained_interval_only"
        else:
            dependency_class = "isolated_window"
        caller_counts: dict[str, int] = {}
        for target in targets:
            for caller in target["ingress_summary"]["caller_functions"]:
                function = str(caller["function"])
                caller_counts[function] = caller_counts.get(function, 0) + int(
                    caller["count"])
        cluster.update({
            "target_count": len(targets),
            "byte_length": end - start,
            "sha256": hashlib.sha256(span).hexdigest(),
            "instruction_count": len(instructions),
            "instructions": instructions,
            "source_recovery_status": _source_recovery_status(
                cluster,
                targets,
                instructions,
            ),
            "feature_summary": max(
                targets,
                key=lambda target: int(target["bounded_span"]["byte_length"]),
            )["bounded_span"]["feature_summary"],
            "arithmetic_motif": max(
                targets,
                key=lambda target: int(target["bounded_span"]["byte_length"]),
            )["bounded_span"]["arithmetic_motif"],
            "dependency_class": dependency_class,
            "total_call_site_count": sum(
                int(target["ingress_summary"]["call_site_count"])
                for target in targets
            ),
            "targets": [
                {
                    "target_address": target["target_address"],
                    "count": target["count"],
                    "first_instruction": target["instructions"][0][
                        "instruction"],
                    "bounded_span_byte_length": target["bounded_span"][
                        "byte_length"],
                    "bounded_span_sha256": target["bounded_span"]["sha256"],
                }
                for target in targets
            ],
            "caller_functions": [
                {"function": function, "count": count}
                for function, count in sorted(
                    caller_counts.items(),
                    key=lambda item: (-item[1], item[0]),
                )
            ],
        })
    return sorted(clusters, key=_cluster_sort_key)


def _recovery_rollup(clusters: list[dict[str, object]]) -> dict[str, object]:
    status_counts: dict[str, int] = {}
    dependency_counts: dict[str, int] = {}
    readiness_counts: dict[str, int] = {}
    motif_counts: dict[str, int] = {}
    model_routing_counts: dict[str, int] = {}
    work_items = []
    for priority, cluster in enumerate(clusters, start=1):
        status = str(cluster["source_recovery_status"]["status"])
        dependency_class = str(cluster["dependency_class"])
        translation = cluster["source_recovery_status"]["translation_summary"]
        motif = cluster.get("arithmetic_motif")
        motif_kind = None if motif is None else str(motif["kind"])
        if motif_kind is None:
            motif_counts["unmodeled"] = motif_counts.get("unmodeled", 0) + 1
        else:
            motif_counts[motif_kind] = motif_counts.get(motif_kind, 0) + 1
            evidence = motif["source_model"]["reference_evidence"]
            routing_status = str(evidence["firmware_routing_status"])
            model_routing_counts[routing_status] = (
                model_routing_counts.get(routing_status, 0) + 1)
        if dependency_class == "isolated_window":
            readiness = "ready_for_direct_c_translation"
            barrier = None
        elif dependency_class == "same_retained_interval_only":
            readiness = "needs_same_interval_context"
            barrier = "terminal target stays inside the same retained interval"
        else:
            readiness = "needs_cross_retained_dependency_resolution"
            barrier = "terminal target depends on a different retained owner"
        status_counts[status] = status_counts.get(status, 0) + 1
        dependency_counts[dependency_class] = (
            dependency_counts.get(dependency_class, 0) + 1)
        readiness_counts[readiness] = readiness_counts.get(readiness, 0) + 1
        work_items.append({
            "priority": priority,
            "start_address": cluster["start_address"],
            "end_address": cluster["end_address"],
            "byte_length": cluster["byte_length"],
            "instruction_count": cluster["instruction_count"],
            "dependency_class": dependency_class,
            "status": status,
            "implementation_readiness": readiness,
            "dependency_barrier": barrier,
            "translation_shape": translation["shape"],
            "memory_instruction_count": translation[
                "memory_instruction_count"],
            "vfp_instruction_count": translation["vfp_instruction_count"],
            "entrypoint_count": len(
                cluster["source_recovery_status"]["entrypoints"]),
            "terminal_instruction": (
                None if cluster["source_recovery_status"][
                    "terminal_branch"] is None else
                cluster["source_recovery_status"]["terminal_branch"][
                    "instruction"]
            ),
            "arithmetic_motif_kind": motif_kind,
        })
    modeled_count = sum(
        count for kind, count in motif_counts.items()
        if kind != "unmodeled"
    )
    return {
        "cluster_count": len(clusters),
        "byte_length": sum(int(cluster["byte_length"]) for cluster in clusters),
        "instruction_count": sum(
            int(cluster.get("instruction_count", 0)) for cluster in clusters),
        "status_counts": dict(sorted(status_counts.items())),
        "dependency_class_counts": dict(sorted(dependency_counts.items())),
        "implementation_readiness_counts": dict(sorted(
            readiness_counts.items())),
        "semantic_model_contract_count": modeled_count,
        "semantic_model_contract_complete": (
            bool(clusters) and modeled_count == len(clusters)
        ),
        "semantic_model_kind_counts": dict(sorted(motif_counts.items())),
        "semantic_model_firmware_routing_status_counts": dict(sorted(
            model_routing_counts.items())),
        "all_require_c_pull_through": (
            bool(clusters)
            and set(status_counts) == {"requires_c_pull_through"}
        ),
        "work_items": work_items,
    }


def _focused_frontier() -> dict[str, object]:
    report = closure_index.analyze()
    return report["next_pull_through_frontier"]["apollo_main_priority"][
        "focused_source_function_frontier"]


def _ingress_summary_by_target() -> dict[int, dict[str, object]]:
    if not PC_BOUNDARY.exists():
        return {}
    report = json.loads(PC_BOUNDARY.read_text())
    by_target: dict[int, dict[str, object]] = {}
    for blocker in report["blockers"]:
        for segment in blocker["largest_return_terminated_segments"]:
            for site in segment.get("branch_target_site_frontier", []):
                target = int(site["target_address"])
                summary = by_target.setdefault(target, {
                    "source_count": 0,
                    "call_site_count": 0,
                    "caller_functions": {},
                    "segments": [],
                    "call_site_examples": [],
                })
                count = int(site["count"])
                summary["call_site_count"] += count
                function = str(blocker["function"])
                callers = summary["caller_functions"]
                callers[function] = callers.get(function, 0) + count
                summary["segments"].append({
                    "source": blocker["source"],
                    "function": function,
                    "start_offset": segment["start_offset"],
                    "end_offset": segment["end_offset"],
                    "byte_length": segment["byte_length"],
                    "count": count,
                })
                examples = summary["call_site_examples"]
                for example in site.get("call_site_examples", []):
                    if len(examples) >= 8:
                        break
                    examples.append({
                        **example,
                        "source": blocker["source"],
                        "function": function,
                        "segment_start_offset": segment["start_offset"],
                        "segment_end_offset": segment["end_offset"],
                    })
    for summary in by_target.values():
        callers = summary["caller_functions"]
        summary["source_count"] = len(callers)
        summary["caller_functions"] = [
            {"function": function, "count": count}
            for function, count in sorted(
                callers.items(),
                key=lambda item: (-item[1], item[0]),
            )
        ]
        summary["segments"] = sorted(
            summary["segments"],
            key=lambda row: (
                -int(row["count"]),
                str(row["function"]),
                int(row["start_offset"]),
            ),
        )
    return by_target


def analyze() -> dict[str, object]:
    regions = _apollo_main_regions()
    base = _firmware_base(regions)
    image = IMAGE.read_bytes()
    ingress_by_target = _ingress_summary_by_target()
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS | CS_MODE_LITTLE_ENDIAN)
    md.detail = True
    hot_targets = []
    for site in _focused_frontier()["branch_target_site_frontier"][:12]:
        target = int(site["target_address"])
        region = _region_for_address(regions, target)
        if region is None or region.get("address_status") != "official_blob":
            continue
        call_site_examples = site["call_site_examples"][:8]
        target_window = _window_bytes(image, base, target, region)
        instructions = _instruction_rows(
            md, image, base, target, region, regions)
        hot_targets.append({
            "target_address": target,
            "owner": site["owner"],
            "count": site["count"],
            "call_site_examples": call_site_examples,
            "call_relation_counts": _call_relation_counts(call_site_examples),
            "region": region["name"],
            "region_file_offset": region["file_offset"],
            "region_target_address": region["target_address"],
            "offset_in_region": target - int(region["target_address"]),
            "region_size": region["size"],
            "region_function": region["function"],
            "region_output": region["output"],
            "file_offset": target - base,
            "window_bytes": WINDOW_BYTES,
            "window_sha256": hashlib.sha256(target_window).hexdigest(),
            "target_shape": _target_shape(call_site_examples, instructions),
            "instruction_count": len(instructions),
            "control_flow_counts": _control_flow_counts(instructions),
            "control_flow_owner_counts": _control_flow_owner_counts(
                instructions),
            "instructions": instructions,
            "bounded_span": _bounded_span(
                md, image, base, target, region, regions),
            "ingress_summary": ingress_by_target.get(target, {
                "source_count": 0,
                "call_site_count": 0,
                "caller_functions": [],
                "segments": [],
                "call_site_examples": [],
            }),
        })
    for row in hot_targets:
        row["dependency_class"] = (
            _dependency_class(row)
            if row["target_shape"] == "direct_subroutine_entry"
            else "not_direct_subroutine"
        )
        row["external_dependency_count"] = sum(
            count
            for owner, count in row["control_flow_owner_counts"].items()
            if owner != row["owner"]
        )
    shape_counts = Counter(row["target_shape"] for row in hot_targets)
    direct_subroutines = [
        row for row in hot_targets
        if row["target_shape"] == "direct_subroutine_entry"
    ]
    direct_clusters = _merge_direct_subroutine_clusters(
        direct_subroutines,
        md,
        image,
        base,
        regions,
    )
    return {
        "schema_version": 1,
        "source": "focused AM142 branch target-site frontier",
        "firmware_base": base,
        "window_bytes": WINDOW_BYTES,
        "hot_target_count": len(hot_targets),
        "target_shape_counts": dict(sorted(shape_counts.items())),
        "direct_subroutine_frontier": [
            {
                "count": row["count"],
                "target_address": row["target_address"],
                "region": row["region"],
                "offset_in_region": row["offset_in_region"],
                "instruction_count": row["instruction_count"],
                "window_sha256": row["window_sha256"],
                "bounded_span": {
                    "status": row["bounded_span"]["status"],
                    "byte_length": row["bounded_span"]["byte_length"],
                    "sha256": row["bounded_span"]["sha256"],
                    "instruction_count": row["bounded_span"][
                        "instruction_count"],
                    "terminal_instruction": row["bounded_span"][
                        "terminal_instruction"],
                },
                "ingress_summary": row["ingress_summary"],
                "control_flow_counts": row["control_flow_counts"],
                "control_flow_owner_counts": row[
                    "control_flow_owner_counts"],
                "dependency_class": row["dependency_class"],
                "external_dependency_count": row["external_dependency_count"],
                "first_instruction": row["instructions"][0]["instruction"],
            }
            for row in direct_subroutines
        ],
        "source_pull_through_queue": [
            {
                "priority": priority,
                "target_address": row["target_address"],
                "count": row["count"],
                "region": row["region"],
                "offset_in_region": row["offset_in_region"],
                "dependency_class": row["dependency_class"],
                "external_dependency_count": row["external_dependency_count"],
                "instruction_count": row["instruction_count"],
                "bounded_span_byte_length": row["bounded_span"][
                    "byte_length"],
                "bounded_span_sha256": row["bounded_span"]["sha256"],
                "bounded_span_status": row["bounded_span"]["status"],
                "ingress_call_site_count": row["ingress_summary"][
                    "call_site_count"],
                "ingress_caller_functions": row["ingress_summary"][
                    "caller_functions"][:3],
                "window_sha256": row["window_sha256"],
                "first_instruction": row["instructions"][0]["instruction"],
            }
            for priority, row in enumerate(
                sorted(direct_subroutines, key=_pull_through_sort_key),
                start=1,
            )
        ],
        "source_pull_through_clusters": [
            {
                "priority": priority,
                **cluster,
            }
            for priority, cluster in enumerate(direct_clusters, start=1)
        ],
        "source_pull_through_recovery_rollup": {
            **_recovery_rollup(direct_clusters),
            "am142_target_compile_receipt": (
                _am142_pullthrough_candidate_receipt()),
        },
        "hot_targets": hot_targets,
    }


def main() -> int:
    report = analyze()
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "hot_target_count": report["hot_target_count"],
        "top_targets": [
            {
                "count": row["count"],
                "target_address": row["target_address"],
                "region": row["region"],
                "offset_in_region": row["offset_in_region"],
                "first_instruction": (
                    None if not row["instructions"] else
                    row["instructions"][0]["instruction"]
                ),
            }
            for row in report["hot_targets"][:5]
        ],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
