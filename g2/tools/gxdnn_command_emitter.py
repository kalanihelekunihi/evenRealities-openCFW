#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Source-authored gxDNN/SNPU command-stream encoder and decoder.

This is a generator (assembler) for the accelerator command-stream wire
format already decoded and documented in
docs/research/gx8002-gxdnn-cmodel.md and reproduced read-only by
analyze_gx8002_model_command_chain.py:

  * the 32-bit base-slot/offset addressing scheme (top 4 bits select one of
    16 base slots, low 28 bits are a byte offset);
  * per-command header framing: low byte opcode, bit 17 selects sequential
    advancement versus an explicit link word, bit 16 selects a host
    absolute pointer (unresolved; rejected here) versus the understood
    32-bit relative link, and bit 22 requests a completion interrupt
    (cmd_process.o, "Execution-model corroboration");
  * the three opcode-1 general-operation subtypes whose full 40-byte
    payload field layout is completely decoded: copy (subtype 2),
    tensor_vector (subtype 4) and tensor_tensor (subtype 5), including
    their address/extent/stride/immediate fields and the arithmetic
    selector resolved in gx8002-gxdnn-arithmetic-dispatch.json.

Every other opcode (0x40/0x41/0x42/0x43) and opcode-1 subtype
(active/pool/reduce/tensor_scalar/format/bn) has no established field
semantics anywhere in this tree, so this module never invents any: it
round-trips them as an explicitly opaque `RawCommand` payload. Encoding a
program built only from `CopyCommand`/`TensorOpCommand` produces a fully
understood, fully source-authored byte stream with no opaque content.

This module does not supply, admit, or reproduce the GX8002 codec's shipped
9,164-byte KWS command stream or 120,800-byte weight block as source. See
docs/research/gx8002-command-emitter-generator.md for what this closes and
what remains open.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Union

# Total command size in bytes for the sequential (no explicit link word)
# framing, keyed by opcode. Confirmed by the exhaustive structural walk of
# the authenticated 9,164-byte command block (gx8002-model-command-chain.json):
# every one of its 212 commands consumes exactly this many bytes, plus 4 more
# when using an explicit (non-sequential) link word.
OPCODE_SIZES = {0x01: 44, 0x40: 48, 0x41: 60, 0x42: 48, 0x43: 24}

OPCODE1_SUBTYPE_NAMES = {
    0: 'active', 1: 'pool', 2: 'copy', 3: 'reduce', 4: 'tensor_vector',
    5: 'tensor_tensor', 6: 'tensor_scalar', 7: 'format', 8: 'bn',
}

# calc.o's choose_calc_func dispatch table (gx8002-gxdnn-arithmetic-dispatch.json)
# resolves seven selectors, but the opcode-1 tensor control word only carries a
# two-bit selector field (bits 9:10 for tensor_vector, 11:12 for tensor_tensor),
# so only these four are reachable through that field.
ARITHMETIC_SELECTOR = {'add': 0, 'sub': 1, 'mul': 2, 'div': 3}
ARITHMETIC_NAME = {v: k for k, v in ARITHMETIC_SELECTOR.items()}
TENSOR_SUBTYPE = {'tensor_vector': 4, 'tensor_tensor': 5}
TENSOR_SELECTOR_SHIFT = {'tensor_vector': 9, 'tensor_tensor': 11}

# Observed terminal self-link in the shipped command block: the last, linked
# opcode-1 command's relative link resolves to base slot 7 offset 0, the slot
# run_task assigns the completion descriptor. This is a convention taken from
# that observation, not an ISA requirement; callers may link anywhere.
TERMINAL_SELF_LINK = (7, 0)


class CommandFormatError(ValueError):
    pass


def encode_address(base_slot: int, offset: int) -> int:
    if not (0 <= base_slot < 16):
        raise CommandFormatError(f'base_slot {base_slot!r} out of 4-bit range')
    if not (0 <= offset < (1 << 28)):
        raise CommandFormatError(f'offset {offset!r} out of 28-bit range')
    return (base_slot << 28) | offset


def decode_address(word: int) -> Tuple[int, int]:
    return (word >> 28, word & 0xFFFFFFF)


def encode_extents(e0: int, e1: int, e2: int) -> int:
    if not (0 <= e0 < 4096):
        raise CommandFormatError('extent 0 must fit 12 bits')
    if not (0 <= e1 < 4096):
        raise CommandFormatError('extent 1 must fit 12 bits')
    if not (0 <= e2 < 256):
        raise CommandFormatError('extent 2 must fit 8 bits')
    return (e0 << 20) | (e1 << 8) | e2


def decode_extents(word: int) -> Tuple[int, int, int]:
    return (word >> 20, (word >> 8) & 0xFFF, word & 0xFF)


def _check_u16(name: str, value: int) -> None:
    if not (0 <= value < 0x10000):
        raise CommandFormatError(f'{name} must fit 16 bits')


@dataclass(frozen=True)
class RawCommand:
    """An opaque command payload for an opcode or opcode-1 subtype whose
    field semantics are not established anywhere in this tree. `payload` is
    the exact `OPCODE_SIZES[opcode] - 4` byte body; nothing about its
    content is interpreted or claimed as understood."""
    opcode: int
    payload: bytes


@dataclass(frozen=True)
class CopyCommand:
    """Opcode 1, subtype 2 (copy). Fields per gx8002-gxdnn-cmodel.md,
    "General-operation subtypes and copy fields" / "Copy access geometry"."""
    source: Tuple[int, int]
    destination: Tuple[int, int]
    extents: Tuple[int, int, int]
    source_strides: Tuple[int, int]       # (outer, middle); inner stride is 1
    destination_strides: Tuple[int, int]  # (outer, middle); inner stride is 1
    immediate: int = 0


@dataclass(frozen=True)
class TensorOpCommand:
    """Opcode 1, subtype 4 (tensor_vector, source_b broadcasts with implicit
    zero strides) or subtype 5 (tensor_tensor). Fields per
    gx8002-gxdnn-cmodel.md, "Tensor operand fields" / "Tensor indexing and
    broadcast", arithmetic selector per gx8002-gxdnn-arithmetic-dispatch.json."""
    kind: str  # 'tensor_vector' or 'tensor_tensor'
    arithmetic: str  # one of ARITHMETIC_SELECTOR
    source_a: Tuple[int, int]
    source_b: Tuple[int, int]
    destination: Tuple[int, int]
    extents: Tuple[int, int, int]
    source_strides: Tuple[int, int]
    destination_strides: Tuple[int, int]
    immediate: int = 0


CommandBody = Union[RawCommand, CopyCommand, TensorOpCommand]


@dataclass(frozen=True)
class Command:
    body: CommandBody
    interrupt: bool = False       # header bit 22: request a completion interrupt
    header_reserved: int = 0      # any header bits outside opcode/16/17/22; meaning not established, preserved verbatim
    link: Optional[Tuple[int, int]] = None  # None => sequential advance; else an explicit relative link target


def _opcode_of(body: CommandBody) -> int:
    if isinstance(body, RawCommand):
        return body.opcode
    return 0x01


def _encode_generic_op_payload(a_word: int, b_word: int, dst_word: int, ctrl: int,
                                extents: Tuple[int, int, int],
                                source_strides: Tuple[int, int],
                                destination_strides: Tuple[int, int],
                                immediate: int) -> bytes:
    src_outer, src_middle = source_strides
    dst_outer, dst_middle = destination_strides
    for name, value in (('source outer stride', src_outer), ('source middle stride', src_middle),
                         ('destination outer stride', dst_outer), ('destination middle stride', dst_middle),
                         ('immediate', immediate)):
        _check_u16(name, value)
    return (
        struct.pack('<I', a_word) + struct.pack('<I', b_word) + b'\x00\x00\x00\x00' +
        struct.pack('<I', dst_word) + struct.pack('<I', ctrl) +
        struct.pack('<I', encode_extents(*extents)) +
        struct.pack('<HH', src_middle, src_outer) + struct.pack('<HH', dst_middle, dst_outer) +
        struct.pack('<H', immediate) + b'\x00' * 6
    )


def _decode_generic_op_payload(payload: bytes):
    if len(payload) != 40:
        raise CommandFormatError('opcode-1 payload must be 40 bytes')
    a_word, b_word, reserved8, dst_word, ctrl, extents_word = struct.unpack_from('<IIIIII', payload, 0)
    if reserved8 != 0:
        raise CommandFormatError('unclassified opcode-1 reserved word (payload+8) is nonzero')
    src_middle, src_outer, dst_middle, dst_outer, immediate = struct.unpack_from('<HHHHH', payload, 24)
    if payload[34:40] != b'\x00' * 6:
        raise CommandFormatError('unclassified opcode-1 tail bytes (payload+34..40) are nonzero')
    return a_word, b_word, dst_word, ctrl, decode_extents(extents_word), (src_outer, src_middle), (dst_outer, dst_middle), immediate


def _encode_copy_payload(cmd: CopyCommand) -> bytes:
    return _encode_generic_op_payload(
        encode_address(*cmd.source), 0, encode_address(*cmd.destination), 2,
        cmd.extents, cmd.source_strides, cmd.destination_strides, cmd.immediate)


def _decode_copy_payload(payload: bytes) -> CopyCommand:
    a_word, b_word, dst_word, ctrl, extents, src_strides, dst_strides, immediate = _decode_generic_op_payload(payload)
    if b_word != 0:
        raise CommandFormatError('unclassified copy reserved word (payload+4) is nonzero')
    if ctrl != 2:
        raise CommandFormatError('copy control word must equal subtype 2 with no other bits')
    return CopyCommand(source=decode_address(a_word), destination=decode_address(dst_word),
                        extents=extents, source_strides=src_strides, destination_strides=dst_strides,
                        immediate=immediate)


def _encode_tensor_payload(cmd: TensorOpCommand) -> bytes:
    if cmd.kind not in TENSOR_SUBTYPE:
        raise CommandFormatError(f'unknown tensor kind {cmd.kind!r}')
    if cmd.arithmetic not in ARITHMETIC_SELECTOR:
        raise CommandFormatError(
            f'arithmetic {cmd.arithmetic!r} unsupported: the opcode-1 tensor control word only '
            'carries a 2-bit selector (add/sub/mul/div); pow/exp/log are known from calc.o but '
            'have no confirmed encoding in this field')
    ctrl = TENSOR_SUBTYPE[cmd.kind] | (ARITHMETIC_SELECTOR[cmd.arithmetic] << TENSOR_SELECTOR_SHIFT[cmd.kind])
    return _encode_generic_op_payload(
        encode_address(*cmd.source_a), encode_address(*cmd.source_b), encode_address(*cmd.destination),
        ctrl, cmd.extents, cmd.source_strides, cmd.destination_strides, cmd.immediate)


def _decode_tensor_payload(payload: bytes, subtype: int) -> TensorOpCommand:
    a_word, b_word, dst_word, ctrl, extents, src_strides, dst_strides, immediate = _decode_generic_op_payload(payload)
    kind = 'tensor_vector' if subtype == 4 else 'tensor_tensor'
    shift = TENSOR_SELECTOR_SHIFT[kind]
    if ctrl & ~(0x0F | (3 << shift)):
        raise CommandFormatError('unclassified tensor control bits set')
    selector = (ctrl >> shift) & 3
    if selector not in ARITHMETIC_NAME:
        raise CommandFormatError('unresolved arithmetic selector')
    return TensorOpCommand(kind=kind, arithmetic=ARITHMETIC_NAME[selector],
                            source_a=decode_address(a_word), source_b=decode_address(b_word),
                            destination=decode_address(dst_word), extents=extents,
                            source_strides=src_strides, destination_strides=dst_strides,
                            immediate=immediate)


_HEADER_KNOWN_BITS = 0xFF | (1 << 16) | (1 << 17) | (1 << 22)


def encode_command(cmd: Command) -> bytes:
    body = cmd.body
    if isinstance(body, RawCommand):
        opcode, payload = body.opcode, body.payload
    elif isinstance(body, CopyCommand):
        opcode, payload = 0x01, _encode_copy_payload(body)
    elif isinstance(body, TensorOpCommand):
        opcode, payload = 0x01, _encode_tensor_payload(body)
    else:
        raise TypeError(f'unsupported command body type {type(body)!r}')
    if opcode not in OPCODE_SIZES:
        raise CommandFormatError(f'unsupported opcode {opcode:#x}')
    expected = OPCODE_SIZES[opcode] - 4
    if len(payload) != expected:
        raise CommandFormatError(f'opcode {opcode:#x} payload must be {expected} bytes, got {len(payload)}')
    if cmd.header_reserved & _HEADER_KNOWN_BITS:
        raise CommandFormatError('header_reserved must not overlap opcode/absolute/sequential/interrupt bits')
    header = opcode | cmd.header_reserved
    if cmd.interrupt:
        header |= (1 << 22)
    out = bytearray()
    if cmd.link is None:
        header |= (1 << 17)
        out += struct.pack('<I', header)
    else:
        out += struct.pack('<I', header)
        out += struct.pack('<I', encode_address(*cmd.link))
    out += payload
    return bytes(out)


def decode_command(data: bytes, offset: int = 0) -> Tuple[Command, int]:
    if offset + 4 > len(data):
        raise CommandFormatError('truncated command header')
    header = struct.unpack_from('<I', data, offset)[0]
    opcode = header & 0xFF
    if opcode not in OPCODE_SIZES:
        raise CommandFormatError(f'unresolved opcode {opcode:#x}')
    sequential = bool(header & (1 << 17))
    if header & (1 << 16):
        raise CommandFormatError('absolute link representation unresolved')
    interrupt = bool(header & (1 << 22))
    header_reserved = header & ~_HEADER_KNOWN_BITS
    total = OPCODE_SIZES[opcode] + (0 if sequential else 4)
    if offset + total > len(data):
        raise CommandFormatError('command exceeds buffer bounds')
    link = None
    payload_start = offset + 4
    if not sequential:
        link = decode_address(struct.unpack_from('<I', data, offset + 4)[0])
        payload_start += 4
    payload = data[payload_start:offset + total]
    if opcode == 0x01 and (payload[16] & 0x0F) in (2, 4, 5):
        subtype = payload[16] & 0x0F
        body = _decode_copy_payload(payload) if subtype == 2 else _decode_tensor_payload(payload, subtype)
    else:
        body = RawCommand(opcode=opcode, payload=payload)
    return Command(body=body, interrupt=interrupt, header_reserved=header_reserved, link=link), offset + total


def emit_program(commands: List[Command]) -> bytes:
    return b''.join(encode_command(c) for c in commands)


def decode_program(data: bytes) -> List[Command]:
    commands = []
    offset = 0
    while offset < len(data):
        cmd, offset = decode_command(data, offset)
        commands.append(cmd)
    if offset != len(data):
        raise CommandFormatError('command stream did not end on a command boundary')
    return commands
