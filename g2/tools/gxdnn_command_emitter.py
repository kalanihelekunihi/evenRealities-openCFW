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
  * ReLU and sigmoid activation modes of opcode-1 subtype 0, and the
    three opcode-1 general-operation subtypes whose full 40-byte
    payload field layout is completely decoded: copy (subtype 2),
    tensor_vector (subtype 4) and tensor_tensor (subtype 5), including
    their address/extent/stride/immediate fields and the arithmetic
    selector resolved in gx8002-gxdnn-arithmetic-dispatch.json;
  * batch normalization (opcode-1 subtype 8): input, scale, bias,
    destination, extents, and strides, corroborated by the upstream cmodel;
  * opcode-0x43 transpose: source/destination addresses, mode, dimensions,
    and two pitch fields in the pinned cmodel parser's field order;
  * opcode-1 reduce, activation mode 4, and format conversion fields from
    the cmodel parsers, with the activation's exact function name unresolved;
  * opcode-0x40 fully connected, 0x41 convolution, and 0x42 depthwise
    convolution fields in the pinned cmodel parsers' field order. Some
    geometry-axis and control-bit meanings remain unresolved.

Unrecognized opcode-1 subtypes (other active modes/pool/tensor_scalar) and
unclassified variants of the typed opcodes are preserved as `RawCommand`
payloads. Encoding a program built only from typed classes produces a
source-authored command stream; the unresolved subfields remain explicit.

The twelve activation commands, 152 copy/tensor commands, 18 batch norm
commands, 14 transpose commands, three special opcode-1 commands, and 13
matrix/convolution commands are represented as typed C source in
g2/src/codec/npu/. All 212 command records are covered. The 120,800-byte
weight block is not supplied as source. See
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
ACTIVATION_MODE = {'relu': 1, 'sigmoid': 2}
ACTIVATION_NAME = {value: name for name, value in ACTIVATION_MODE.items()}

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
class ActivationCommand:
    """Opcode 1, subtype 0, mode 1 (ReLU) or 2 (sigmoid). The upstream
    cmodel's parse_op_active_cmd reads the source, destination, extent and
    stride fields; calc_op_active dispatches modes 1/2 to active_relu and
    active_sigmoid. Other modes remain opaque."""
    kind: str
    source: Tuple[int, int]
    destination: Tuple[int, int]
    extents: Tuple[int, int, int]
    source_strides: Tuple[int, int]
    destination_strides: Tuple[int, int]


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


@dataclass(frozen=True)
class BatchNormCommand:
    """Opcode 1, subtype 8. The upstream parse_op_bn_cmd reads four
    addresses, three extents and two stride pairs; calc_op_bn multiplies
    input by scale and adds bias using half-float arithmetic."""
    source: Tuple[int, int]
    scale: Tuple[int, int]
    bias: Tuple[int, int]
    destination: Tuple[int, int]
    extents: Tuple[int, int, int]
    source_strides: Tuple[int, int]
    destination_strides: Tuple[int, int]


@dataclass(frozen=True)
class TransposeCommand:
    """Opcode 0x43. Field order follows the pinned cmodel's
    parse_transpose_cmd; exact axis convention has not been verified."""
    source: Tuple[int, int]
    destination: Tuple[int, int]
    mode: int
    dimensions: Tuple[int, int, int, int]
    first_pitch: int
    second_pitch: int


@dataclass(frozen=True)
class ReduceCommand:
    """Opcode 1, subtype 3. The cmodel sums across the selected extent
    and divides by a half-float divisor."""
    source: Tuple[int, int]
    destination: Tuple[int, int]
    extents: Tuple[int, int, int]
    source_strides: Tuple[int, int]
    destination_strides: Tuple[int, int]
    axis: int
    divisor_half: int


@dataclass(frozen=True)
class ActivationMode4Command:
    """Opcode 1, subtype 0, mode 4. The cmodel reads three half-float
    parameters; the exact operation name is not yet established."""
    source: Tuple[int, int]
    destination: Tuple[int, int]
    extents: Tuple[int, int, int]
    source_strides: Tuple[int, int]
    destination_strides: Tuple[int, int]
    parameter0_half: int
    parameter1_half: int
    parameter2_half: int


@dataclass(frozen=True)
class FormatCommand:
    """Opcode 1, subtype 7, half-to-float32 or float32-to-half conversion."""
    source: Tuple[int, int]
    destination: Tuple[int, int]
    extents: Tuple[int, int, int]
    source_strides: Tuple[int, int]
    destination_strides: Tuple[int, int]
    to_float32: bool


@dataclass(frozen=True)
class FullyConnectedCommand:
    """Opcode 0x40, parser-backed field order. Tile and final control
    semantics remain incomplete."""
    source: Tuple[int, int]
    weights: Tuple[int, int]
    destination: Tuple[int, int]
    bias: Tuple[int, int]
    dimensions: Tuple[int, int]
    tile: Tuple[int, int, int, int]
    coefficients: Tuple[int, int]
    final_control_low16: int


@dataclass(frozen=True)
class ConvolutionCommand:
    """Opcode 0x41, parser-backed geometry and control fields."""
    source: Tuple[int, int]
    weights: Tuple[int, int]
    destination: Tuple[int, int]
    bias: Tuple[int, int]
    dimensions: Tuple[int, int]
    tile: Tuple[int, int, int, int]
    pitches: Tuple[int, int]
    geometry_control0: int
    geometry_control1: int
    kernel_control: int
    coefficients: Tuple[int, int]
    final_control_low16: int


@dataclass(frozen=True)
class DepthwiseConvolutionCommand:
    """Opcode 0x42, parser-backed geometry and control fields."""
    source: Tuple[int, int]
    weights: Tuple[int, int]
    destination: Tuple[int, int]
    geometry0: Tuple[int, int, int, int]
    geometry1: Tuple[int, int, int, int]
    geometry2: Tuple[int, int, int, int]
    pitches: Tuple[int, int]
    geometry_control: int
    kernel_control0: int
    kernel_control1: int


CommandBody = Union[RawCommand, CopyCommand, ActivationCommand, TensorOpCommand,
                    BatchNormCommand, TransposeCommand, ReduceCommand,
                    ActivationMode4Command, FormatCommand, FullyConnectedCommand,
                    ConvolutionCommand, DepthwiseConvolutionCommand]


@dataclass(frozen=True)
class Command:
    body: CommandBody
    interrupt: bool = False       # header bit 22: request a completion interrupt
    header_reserved: int = 0      # any header bits outside opcode/16/17/22; meaning not established, preserved verbatim
    link: Optional[Tuple[int, int]] = None  # None => sequential advance; else an explicit relative link target


def _opcode_of(body: CommandBody) -> int:
    if isinstance(body, RawCommand):
        return body.opcode
    if isinstance(body, TransposeCommand):
        return 0x43
    if isinstance(body, FullyConnectedCommand):
        return 0x40
    if isinstance(body, ConvolutionCommand):
        return 0x41
    if isinstance(body, DepthwiseConvolutionCommand):
        return 0x42
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


def _encode_activation_payload(cmd: ActivationCommand) -> bytes:
    if cmd.kind not in ACTIVATION_MODE:
        raise CommandFormatError(f'unsupported activation {cmd.kind!r}')
    return _encode_generic_op_payload(
        encode_address(*cmd.source), 0, encode_address(*cmd.destination),
        ACTIVATION_MODE[cmd.kind] << 4, cmd.extents,
        cmd.source_strides, cmd.destination_strides, 0)


def _decode_activation_payload(payload: bytes) -> ActivationCommand:
    src, second, dst, ctrl, extents, src_strides, dst_strides, immediate = _decode_generic_op_payload(payload)
    if second != 0 or immediate != 0 or ctrl not in (0x10, 0x20):
        raise CommandFormatError('activation has unclassified fields')
    return ActivationCommand(kind=ACTIVATION_NAME[ctrl >> 4],
                             source=decode_address(src), destination=decode_address(dst),
                             extents=extents, source_strides=src_strides,
                             destination_strides=dst_strides)


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


def _encode_batch_norm_payload(cmd: BatchNormCommand) -> bytes:
    for name, value in (('source outer stride', cmd.source_strides[0]),
                        ('source middle stride', cmd.source_strides[1]),
                        ('destination outer stride', cmd.destination_strides[0]),
                        ('destination middle stride', cmd.destination_strides[1])):
        _check_u16(name, value)
    return (
        struct.pack('<IIIII', encode_address(*cmd.source), encode_address(*cmd.scale),
                    encode_address(*cmd.bias), encode_address(*cmd.destination), 8) +
        struct.pack('<I', encode_extents(*cmd.extents)) +
        struct.pack('<HHHH', cmd.source_strides[1], cmd.source_strides[0],
                    cmd.destination_strides[1], cmd.destination_strides[0]) +
        b'\x00' * 8
    )


def _decode_batch_norm_payload(payload: bytes) -> BatchNormCommand:
    if len(payload) != 40:
        raise CommandFormatError('batch norm payload must be 40 bytes')
    source, scale, bias, destination, ctrl, extents = struct.unpack_from('<IIIIII', payload)
    if ctrl != 8 or payload[32:] != b'\x00' * 8:
        raise CommandFormatError('batch norm has unclassified control or tail fields')
    src_middle, src_outer, dst_middle, dst_outer = struct.unpack_from('<HHHH', payload, 24)
    return BatchNormCommand(source=decode_address(source), scale=decode_address(scale),
                            bias=decode_address(bias), destination=decode_address(destination),
                            extents=decode_extents(extents),
                            source_strides=(src_outer, src_middle),
                            destination_strides=(dst_outer, dst_middle))


def _encode_transpose_payload(cmd: TransposeCommand) -> bytes:
    if not (0 <= cmd.mode < 256) or len(cmd.dimensions) != 4 or any(
            not (0 <= value < 256) for value in cmd.dimensions):
        raise CommandFormatError('transpose mode and dimensions must fit bytes')
    _check_u16('first pitch', cmd.first_pitch)
    _check_u16('second pitch', cmd.second_pitch)
    return (struct.pack('<II', encode_address(*cmd.source), encode_address(*cmd.destination)) +
            bytes((cmd.mode, 0, 0, 0)) + bytes(cmd.dimensions) +
            struct.pack('<HH', cmd.first_pitch, cmd.second_pitch))


def _decode_transpose_payload(payload: bytes) -> TransposeCommand:
    if len(payload) != 20 or payload[9:12] != b'\x00' * 3:
        raise CommandFormatError('transpose has unclassified reserved bytes')
    source, destination = struct.unpack_from('<II', payload)
    first_pitch, second_pitch = struct.unpack_from('<HH', payload, 16)
    return TransposeCommand(source=decode_address(source),
                            destination=decode_address(destination), mode=payload[8],
                            dimensions=tuple(payload[12:16]),
                            first_pitch=first_pitch, second_pitch=second_pitch)


def _encode_reduce_payload(cmd: ReduceCommand) -> bytes:
    if not (0 <= cmd.axis <= 2):
        raise CommandFormatError('reduce axis must select one of three extents')
    return _encode_generic_op_payload(
        encode_address(*cmd.source), 0, encode_address(*cmd.destination),
        3 | (cmd.axis << 7), cmd.extents, cmd.source_strides,
        cmd.destination_strides, cmd.divisor_half)


def _decode_reduce_payload(payload: bytes) -> ReduceCommand:
    src, second, dst, ctrl, extents, src_strides, dst_strides, divisor = _decode_generic_op_payload(payload)
    if second != 0 or (ctrl & 0xF) != 3 or ctrl & ~(0xF | (3 << 7)) or ((ctrl >> 7) & 3) > 2:
        raise CommandFormatError('reduce has unclassified fields')
    return ReduceCommand(source=decode_address(src), destination=decode_address(dst),
                         extents=extents, source_strides=src_strides,
                         destination_strides=dst_strides, axis=(ctrl >> 7) & 3,
                         divisor_half=divisor)


def _encode_activation_mode4_payload(cmd: ActivationMode4Command) -> bytes:
    for name, value in (('parameter 0', cmd.parameter0_half),
                        ('parameter 1', cmd.parameter1_half),
                        ('parameter 2', cmd.parameter2_half)):
        _check_u16(name, value)
    payload = bytearray(_encode_generic_op_payload(
        encode_address(*cmd.source), 0, encode_address(*cmd.destination),
        0x40, cmd.extents, cmd.source_strides,
        cmd.destination_strides, cmd.parameter0_half))
    struct.pack_into('<HH', payload, 36, cmd.parameter1_half, cmd.parameter2_half)
    return bytes(payload)


def _decode_activation_mode4_payload(payload: bytes) -> ActivationMode4Command:
    if len(payload) != 40 or payload[8:12] != b'\x00' * 4 or payload[34:36] != b'\x00' * 2:
        raise CommandFormatError('activation mode 4 has unclassified reserved bytes')
    src, second, reserved, dst, ctrl, extents = struct.unpack_from('<IIIIII', payload)
    if second != 0 or reserved != 0 or ctrl != 0x40:
        raise CommandFormatError('activation mode 4 has unclassified control fields')
    src_middle, src_outer, dst_middle, dst_outer = struct.unpack_from('<HHHH', payload, 24)
    p0 = struct.unpack_from('<H', payload, 32)[0]
    p1, p2 = struct.unpack_from('<HH', payload, 36)
    return ActivationMode4Command(source=decode_address(src), destination=decode_address(dst),
                                  extents=decode_extents(extents),
                                  source_strides=(src_outer, src_middle),
                                  destination_strides=(dst_outer, dst_middle),
                                  parameter0_half=p0, parameter1_half=p1,
                                  parameter2_half=p2)


def _encode_format_payload(cmd: FormatCommand) -> bytes:
    return _encode_generic_op_payload(
        encode_address(*cmd.source), 0, encode_address(*cmd.destination),
        7 | (int(cmd.to_float32) << 16), cmd.extents,
        cmd.source_strides, cmd.destination_strides, 0)


def _decode_format_payload(payload: bytes) -> FormatCommand:
    src, second, dst, ctrl, extents, src_strides, dst_strides, immediate = _decode_generic_op_payload(payload)
    if second != 0 or immediate != 0 or ctrl not in (7, 0x10007):
        raise CommandFormatError('format conversion has unclassified fields')
    return FormatCommand(source=decode_address(src), destination=decode_address(dst),
                         extents=extents, source_strides=src_strides,
                         destination_strides=dst_strides,
                         to_float32=bool(ctrl & (1 << 16)))


def _field_bytes(name: str, values: Tuple[int, ...], count: int) -> bytes:
    if len(values) != count or any(not (0 <= value < 256) for value in values):
        raise CommandFormatError(f'{name} must contain {count} byte values')
    return bytes(values)


def _field_u16s(name: str, values: Tuple[int, ...], count: int) -> bytes:
    if len(values) != count:
        raise CommandFormatError(f'{name} must contain {count} 16-bit values')
    for value in values:
        _check_u16(name, value)
    return struct.pack('<' + 'H' * count, *values)


def _encode_fc_payload(cmd: FullyConnectedCommand) -> bytes:
    _check_u16('FC final control', cmd.final_control_low16)
    out = bytearray(44)
    struct.pack_into('<IIIII', out, 0, encode_address(*cmd.source),
                     encode_address(*cmd.weights), encode_address(*cmd.destination),
                     0, encode_address(*cmd.bias))
    out[20:24] = _field_u16s('FC dimensions', cmd.dimensions, 2)
    out[24:28] = _field_bytes('FC tile', cmd.tile, 4)
    out[31] = 1
    out[36:40] = _field_u16s('FC coefficients', cmd.coefficients, 2)
    struct.pack_into('<HH', out, 40, cmd.final_control_low16, 0x8000)
    return bytes(out)


def _decode_fc_payload(payload: bytes) -> FullyConnectedCommand:
    if (len(payload) != 44 or payload[12:16] != b'\x00' * 4 or
            payload[28:32] != b'\x00\x00\x00\x01' or
            payload[32:36] != b'\x00' * 4 or payload[42:44] != b'\x00\x80'):
        raise CommandFormatError('FC command has unclassified control fields')
    source, weights, destination = struct.unpack_from('<III', payload)
    bias = struct.unpack_from('<I', payload, 16)[0]
    return FullyConnectedCommand(
        source=decode_address(source), weights=decode_address(weights),
        destination=decode_address(destination), bias=decode_address(bias),
        dimensions=struct.unpack_from('<HH', payload, 20),
        tile=tuple(payload[24:28]),
        coefficients=struct.unpack_from('<HH', payload, 36),
        final_control_low16=struct.unpack_from('<H', payload, 40)[0])


def _encode_conv_payload(cmd: ConvolutionCommand) -> bytes:
    for name, value in (('geometry control 0', cmd.geometry_control0),
                        ('geometry control 1', cmd.geometry_control1),
                        ('kernel control', cmd.kernel_control)):
        if not (0 <= value < 256):
            raise CommandFormatError(f'{name} must fit one byte')
    _check_u16('convolution final control', cmd.final_control_low16)
    out = bytearray(56)
    struct.pack_into('<IIIII', out, 0, encode_address(*cmd.source),
                     encode_address(*cmd.weights), encode_address(*cmd.destination),
                     0, encode_address(*cmd.bias))
    out[20:24] = _field_u16s('convolution dimensions', cmd.dimensions, 2)
    out[24:28] = _field_bytes('convolution tile', cmd.tile, 4)
    out[28:32] = _field_u16s('convolution pitches', cmd.pitches, 2)
    out[32:36] = bytes((cmd.geometry_control0, 0x11, 0, 1))
    out[36:40] = bytes((0, 0, 0, cmd.geometry_control1))
    out[40:44] = bytes((cmd.kernel_control, 0, 1, 0))
    out[48:52] = _field_u16s('convolution coefficients', cmd.coefficients, 2)
    struct.pack_into('<HH', out, 52, cmd.final_control_low16, 0x8000)
    return bytes(out)


def _decode_conv_payload(payload: bytes) -> ConvolutionCommand:
    if (len(payload) != 56 or payload[12:16] != b'\x00' * 4 or
            payload[33:36] != b'\x11\x00\x01' or
            payload[36:39] != b'\x00' * 3 or
            payload[41:44] != b'\x00\x01\x00' or
            payload[44:48] != b'\x00' * 4 or
            payload[54:56] != b'\x00\x80'):
        raise CommandFormatError('convolution has unclassified control fields')
    source, weights, destination = struct.unpack_from('<III', payload)
    bias = struct.unpack_from('<I', payload, 16)[0]
    return ConvolutionCommand(
        source=decode_address(source), weights=decode_address(weights),
        destination=decode_address(destination), bias=decode_address(bias),
        dimensions=struct.unpack_from('<HH', payload, 20),
        tile=tuple(payload[24:28]), pitches=struct.unpack_from('<HH', payload, 28),
        geometry_control0=payload[32], geometry_control1=payload[39],
        kernel_control=payload[40], coefficients=struct.unpack_from('<HH', payload, 48),
        final_control_low16=struct.unpack_from('<H', payload, 52)[0])


def _encode_depthwise_payload(cmd: DepthwiseConvolutionCommand) -> bytes:
    for name, value in (('depthwise geometry control', cmd.geometry_control),
                        ('depthwise kernel control 0', cmd.kernel_control0),
                        ('depthwise kernel control 1', cmd.kernel_control1)):
        if not (0 <= value < 256):
            raise CommandFormatError(f'{name} must fit one byte')
    out = bytearray(44)
    struct.pack_into('<IIII', out, 0, encode_address(*cmd.source),
                     encode_address(*cmd.weights), encode_address(*cmd.destination), 0)
    out[16:20] = _field_bytes('depthwise geometry 0', cmd.geometry0, 4)
    out[20:24] = _field_bytes('depthwise geometry 1', cmd.geometry1, 4)
    out[24:28] = _field_bytes('depthwise geometry 2', cmd.geometry2, 4)
    out[28:32] = _field_u16s('depthwise pitches', cmd.pitches, 2)
    out[32:36] = bytes((cmd.geometry_control, 0, 1, 0))
    out[36:40] = _field_u16s('depthwise fixed coefficients', (1, 1), 2)
    out[40:44] = bytes((cmd.kernel_control0, cmd.kernel_control1, 1, 0))
    return bytes(out)


def _decode_depthwise_payload(payload: bytes) -> DepthwiseConvolutionCommand:
    if (len(payload) != 44 or payload[12:16] != b'\x00' * 4 or
            payload[33:36] != b'\x00\x01\x00' or
            payload[36:40] != b'\x01\x00\x01\x00' or
            payload[42:44] != b'\x01\x00'):
        raise CommandFormatError('depthwise convolution has unclassified control fields')
    source, weights, destination = struct.unpack_from('<III', payload)
    return DepthwiseConvolutionCommand(
        source=decode_address(source), weights=decode_address(weights),
        destination=decode_address(destination),
        geometry0=tuple(payload[16:20]), geometry1=tuple(payload[20:24]),
        geometry2=tuple(payload[24:28]), pitches=struct.unpack_from('<HH', payload, 28),
        geometry_control=payload[32], kernel_control0=payload[40],
        kernel_control1=payload[41])


_HEADER_KNOWN_BITS = 0xFF | (1 << 16) | (1 << 17) | (1 << 22)


def encode_command(cmd: Command) -> bytes:
    body = cmd.body
    if isinstance(body, RawCommand):
        opcode, payload = body.opcode, body.payload
    elif isinstance(body, CopyCommand):
        opcode, payload = 0x01, _encode_copy_payload(body)
    elif isinstance(body, ActivationCommand):
        opcode, payload = 0x01, _encode_activation_payload(body)
    elif isinstance(body, TensorOpCommand):
        opcode, payload = 0x01, _encode_tensor_payload(body)
    elif isinstance(body, BatchNormCommand):
        opcode, payload = 0x01, _encode_batch_norm_payload(body)
    elif isinstance(body, TransposeCommand):
        opcode, payload = 0x43, _encode_transpose_payload(body)
    elif isinstance(body, ReduceCommand):
        opcode, payload = 0x01, _encode_reduce_payload(body)
    elif isinstance(body, ActivationMode4Command):
        opcode, payload = 0x01, _encode_activation_mode4_payload(body)
    elif isinstance(body, FormatCommand):
        opcode, payload = 0x01, _encode_format_payload(body)
    elif isinstance(body, FullyConnectedCommand):
        opcode, payload = 0x40, _encode_fc_payload(body)
    elif isinstance(body, ConvolutionCommand):
        opcode, payload = 0x41, _encode_conv_payload(body)
    elif isinstance(body, DepthwiseConvolutionCommand):
        opcode, payload = 0x42, _encode_depthwise_payload(body)
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
    if opcode == 0x01 and (payload[16] & 0x0F) == 0 and struct.unpack_from('<I', payload, 16)[0] in (0x10, 0x20):
        body = _decode_activation_payload(payload)
    elif opcode == 0x01 and struct.unpack_from('<I', payload, 16)[0] == 0x40:
        body = _decode_activation_mode4_payload(payload)
    elif opcode == 0x01 and (payload[16] & 0x0F) in (2, 4, 5):
        subtype = payload[16] & 0x0F
        body = _decode_copy_payload(payload) if subtype == 2 else _decode_tensor_payload(payload, subtype)
    elif opcode == 0x01 and struct.unpack_from('<I', payload, 16)[0] == 8:
        body = _decode_batch_norm_payload(payload)
    elif opcode == 0x01 and (payload[16] & 0x0F) == 3:
        body = _decode_reduce_payload(payload)
    elif opcode == 0x01 and (payload[16] & 0x0F) == 7:
        body = _decode_format_payload(payload)
    elif opcode == 0x43:
        body = _decode_transpose_payload(payload)
    elif opcode in (0x40, 0x41, 0x42):
        decoder = {0x40: _decode_fc_payload,
                   0x41: _decode_conv_payload,
                   0x42: _decode_depthwise_payload}[opcode]
        try:
            body = decoder(payload)
        except CommandFormatError:
            body = RawCommand(opcode=opcode, payload=payload)
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
