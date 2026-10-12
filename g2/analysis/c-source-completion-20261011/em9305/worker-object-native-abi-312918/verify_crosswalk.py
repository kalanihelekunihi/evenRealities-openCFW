#!/usr/bin/env python3
"""Verify the complete native 312918 instruction and ARC object crosswalk."""
import collections
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
NATIVE = ROOT / "g2/build/c-firmware/20261011/em-inspection-full.arcem.txt"
CHILDREN = {
    "312b88": "opencfw_em9305_radio_duration_piece_312b88",
    "303f80": "opencfw_em9305_auxiliary_guard_interval",
    "312c5c": "opencfw_em9305_channel_timing_adjust_312c5c",
    "312be4": "opencfw_em9305_radio_duration_312be4",
}
BASELINE = {"312922": "sub", "312956": "asl", "3129cc": "asl", "312b48": "asl"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def native_rows():
    rows = []
    active = False
    for line in NATIVE.read_text().splitlines():
        columns = line.split("\t")
        match = re.fullmatch(r"\s*([0-9a-f]{6}):", columns[0])
        if not match:
            continue
        address = match.group(1)
        if address == "312918":
            active = True
        if not active:
            continue
        words = columns[1].split()
        bits = b"".join(bytes.fromhex(word)[::-1] for word in words)
        mnemonic = columns[2].strip() if len(columns) > 2 else ""
        operands = "\t".join(columns[3:]).strip() if len(columns) > 3 else ""
        if address == "3129f6":
            assert not mnemonic
            mnemonic, operands = "mpywhl", "r0,r0,r12"
        assert mnemonic, address
        rows.append((address, bits, mnemonic, operands))
        if address == "312b84":
            break
    assert len(rows) == 221 and rows[-1][0] == "312b84"
    return rows


def source_rows(source: str):
    asm = re.findall(r'^"(.*)\\n"(?:\s*/\*.*\*/)?$', source, re.M)
    rows = []
    for index, line in enumerate(asm):
        if line == "opencfw_em9305_associated_object_init_312918:":
            address = "312918"
        elif re.fullmatch(r"L[0-9a-f]{6}:", line):
            address = line[1:-1]
        else:
            continue
        instruction = asm[index + 1]
        parts = instruction.split(None, 1)
        rows.append((address, parts[0], parts[1] if len(parts) > 1 else ""))
    return rows


def main():
    native = native_rows()
    source_path = HERE / "source.c"
    source = source_rows(source_path.read_text())
    assert len(source) == len(native)
    for (address, _bits, mnemonic, operands), (source_address, source_mnemonic, source_operands) in zip(native, source):
        assert address == source_address
        if address in BASELINE:
            assert source_mnemonic == BASELINE[address]
        else:
            assert source_mnemonic == mnemonic, (address, mnemonic, source_mnemonic)
        if ";0x" in operands:
            target = operands.split(";0x", 1)[1]
            expected = CHILDREN[target] if mnemonic.startswith("bl") else "L" + target
            assert source_operands.split(",")[-1] == expected, (address, source_operands, expected)
        elif address != "3129f6" and address not in BASELINE:
            assert source_operands.replace("\t", "") == operands.replace("\t", ""), (address, operands, source_operands)

    disassembly = (HERE / "target/source.dis").read_text()
    object_path = HERE / "target/source.o"
    compiled = HERE / "target/source.text.bin"
    relocations = re.findall(r"R_ARC_S25W_PCREL\s+(\S+)", disassembly)
    assert collections.Counter(relocations) == collections.Counter({
        CHILDREN["312b88"]: 9, CHILDREN["303f80"]: 1,
        CHILDREN["312c5c"]: 1, CHILDREN["312be4"]: 1,
    })
    offsets = {}
    for match in re.finditer(r"^([0-9a-f]+) <L([0-9a-f]{6})>:", disassembly, re.M):
        offsets[match.group(2)] = int(match.group(1), 16)
    assert all(address in offsets for address, *_ in native[1:])
    jump_slots = [offsets[f"3129{address:02x}"] for address in range(0x30, 0x50, 4)]
    assert jump_slots == list(range(26, 58, 4))
    assert len(compiled.read_bytes()) == 630
    receipt = {
        "status": "PASS_TARGET_COMPILE_FULL_NATIVE_INSTRUCTION_CROSSWALK_BASELINE_ENCODING",
        "selected": False,
        "native_range": "312918..312b84",
        "native_instruction_count": len(native),
        "source_instruction_and_branch_targets_equal_native": True,
        "bi_jump_table_slot_offsets": jump_slots,
        "bi_jump_table_stride_bytes": 4,
        "child_relocations": dict(collections.Counter(relocations)),
        "source_sha256": sha(source_path),
        "object_sha256": sha(object_path),
        "compiled_text_bytes": compiled.stat().st_size,
        "native_text_bytes": sum(len(row[1]) for row in native),
        "compiled_text_sha256": sha(compiled),
        "baseline_full_instruction_substitutions": BASELINE,
        "limits": [
            "Four baseline full instructions add eight bytes and shift branch displacements; compiled bytes are not native-equal",
            "Twelve BL relocations resolve through genuine source children",
            "Native execution, whole image equality, and hardware remain unverified",
        ],
    }
    (HERE / "target/receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
