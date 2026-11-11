# SPDX-License-Identifier: MIT
"""Round-trip and oracle-fidelity tests for the gxDNN command emitter.

These tests validate the encoder/decoder pair in gxdnn_command_emitter.py:
that it is a correct, lossless implementation of the documented wire format
for synthetic programs, and that decoding the authenticated shipped command
block and re-encoding it reproduces the exact original bytes (an encoder
fidelity check against the real oracle, not a claim that the shipped
program's specific graph is source-authored -- see
docs/research/gx8002-command-emitter-generator.md).
"""
import random
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from gxdnn_command_emitter import (
    Command, CopyCommand, ActivationCommand, TensorOpCommand, BatchNormCommand,
    TransposeCommand, ReduceCommand, ActivationMode4Command, FormatCommand,
    FullyConnectedCommand, ConvolutionCommand, DepthwiseConvolutionCommand,
    RawCommand, CommandFormatError,
    OPCODE_SIZES, TERMINAL_SELF_LINK,
    encode_address, decode_address, encode_extents, decode_extents,
    encode_command, decode_command, emit_program, decode_program,
)

from tests.official_payloads import require as _require_official

_require_official('firmware_codec.bin')


def _random_address(rng):
    return (rng.randrange(16), rng.randrange(1 << 28))


def _random_extents(rng):
    return (rng.randrange(4096), rng.randrange(4096), rng.randrange(256))


def _random_strides(rng):
    return (rng.randrange(0x10000), rng.randrange(0x10000))


class AddressAndExtentCodecTests(unittest.TestCase):
    def test_address_round_trip(self):
        rng = random.Random(1)
        for _ in range(2000):
            base_slot, offset = rng.randrange(16), rng.randrange(1 << 28)
            self.assertEqual((base_slot, offset), decode_address(encode_address(base_slot, offset)))

    def test_address_rejects_out_of_range(self):
        with self.assertRaises(CommandFormatError):
            encode_address(16, 0)
        with self.assertRaises(CommandFormatError):
            encode_address(0, 1 << 28)

    def test_extents_round_trip(self):
        rng = random.Random(2)
        for _ in range(2000):
            extents = _random_extents(rng)
            self.assertEqual(extents, decode_extents(encode_extents(*extents)))

    def test_extents_rejects_out_of_range(self):
        with self.assertRaises(CommandFormatError):
            encode_extents(4096, 0, 0)
        with self.assertRaises(CommandFormatError):
            encode_extents(0, 0, 256)


class CopyCommandTests(unittest.TestCase):
    def test_round_trip_sequential(self):
        rng = random.Random(3)
        for _ in range(500):
            body = CopyCommand(source=_random_address(rng), destination=_random_address(rng),
                                extents=_random_extents(rng), source_strides=_random_strides(rng),
                                destination_strides=_random_strides(rng), immediate=rng.randrange(0x10000))
            cmd = Command(body=body)
            encoded = encode_command(cmd)
            self.assertEqual(len(encoded), OPCODE_SIZES[0x01])
            decoded, consumed = decode_command(encoded)
            self.assertEqual(consumed, len(encoded))
            self.assertEqual(decoded, cmd)

    def test_round_trip_linked_with_interrupt(self):
        body = CopyCommand(source=(1, 6996), destination=(4, 7296), extents=(1, 1, 64),
                            source_strides=(64, 64), destination_strides=(64, 64))
        cmd = Command(body=body, interrupt=True, link=TERMINAL_SELF_LINK)
        encoded = encode_command(cmd)
        self.assertEqual(len(encoded), OPCODE_SIZES[0x01] + 4)
        decoded, consumed = decode_command(encoded)
        self.assertEqual(consumed, len(encoded))
        self.assertEqual(decoded, cmd)

    def test_rejects_nonzero_reserved_word(self):
        payload = bytearray(_encode(CopyCommand(source=(0, 0), destination=(0, 0), extents=(1, 1, 1),
                                                  source_strides=(0, 0), destination_strides=(0, 0))))
        payload[8] = 1  # payload+4 within the command body (after the 4-byte header)
        with self.assertRaises(CommandFormatError):
            decode_command(bytes(payload))


class TensorOpCommandTests(unittest.TestCase):
    def test_round_trip_all_arithmetic_kinds(self):
        rng = random.Random(4)
        for kind in ('tensor_vector', 'tensor_tensor'):
            for arithmetic in ('add', 'sub', 'mul', 'div'):
                body = TensorOpCommand(kind=kind, arithmetic=arithmetic,
                                        source_a=_random_address(rng), source_b=_random_address(rng),
                                        destination=_random_address(rng), extents=_random_extents(rng),
                                        source_strides=_random_strides(rng),
                                        destination_strides=_random_strides(rng),
                                        immediate=rng.randrange(0x10000))
                cmd = Command(body=body)
                decoded, consumed = decode_command(encode_command(cmd))
                self.assertEqual(consumed, OPCODE_SIZES[0x01])
                self.assertEqual(decoded, cmd)

    def test_rejects_unsupported_arithmetic(self):
        body = TensorOpCommand(kind='tensor_vector', arithmetic='pow', source_a=(0, 0), source_b=(0, 0),
                                destination=(0, 0), extents=(1, 1, 1), source_strides=(0, 0),
                                destination_strides=(0, 0))
        with self.assertRaises(CommandFormatError):
            encode_command(Command(body=body))

    def test_shipped_first_command_matches_decoded_semantics(self):
        # gx8002-model-command-chain.json command 0: tensor_vector sub,
        # slot3[0:1040) - slot6[118544:118624) -> slot1[0:1040), extents 1/13/40.
        body = TensorOpCommand(kind='tensor_vector', arithmetic='sub', source_a=(3, 0), source_b=(6, 118544),
                                destination=(1, 0), extents=(1, 13, 40), source_strides=(520, 40),
                                destination_strides=(520, 40))
        encoded = encode_command(Command(body=body))
        decoded, _ = decode_command(encoded)
        self.assertEqual(decoded.body, body)


class ActivationCommandTests(unittest.TestCase):
    def test_shipped_relu_and_sigmoid_fields(self):
        image = (Path(__file__).resolve().parents[1] /
                 'blobs/official/g2-2.2.6.10/firmware_codec.bin').read_bytes()
        commands = decode_program(image[0x18d90:0x18d90 + 9164])
        self.assertEqual(commands[7].body, ActivationCommand(
            kind='relu', source=(1, 0), destination=(1, 960),
            extents=(1, 7, 64), source_strides=(448, 64),
            destination_strides=(448, 64)))
        self.assertEqual(commands[149].body, ActivationCommand(
            kind='sigmoid', source=(1, 5380), destination=(1, 5376),
            extents=(1, 1, 2), source_strides=(2, 2),
            destination_strides=(2, 2)))

    def test_mode4_activation_parameters(self):
        image = (Path(__file__).resolve().parents[1] /
                 'blobs/official/g2-2.2.6.10/firmware_codec.bin').read_bytes()
        commands = decode_program(image[0x18d90:0x18d90 + 9164])
        self.assertEqual(commands[146].body, ActivationMode4Command(
            source=(1, 5376), destination=(1, 7124), extents=(1, 2, 64),
            source_strides=(128, 64), destination_strides=(128, 64),
            parameter0_half=0x3c34, parameter1_half=0xbf08,
            parameter2_half=0x3f08))

    def test_shipped_reduce_and_format(self):
        image = (Path(__file__).resolve().parents[1] /
                 'blobs/official/g2-2.2.6.10/firmware_codec.bin').read_bytes()
        commands = decode_program(image[0x18d90:0x18d90 + 9164])
        self.assertEqual(commands[142].body, ReduceCommand(
            source=(1, 0), destination=(1, 5376), extents=(1, 11, 64),
            source_strides=(704, 64), destination_strides=(64, 64),
            axis=1, divisor_half=0x3c00))
        self.assertEqual(commands[150].body, FormatCommand(
            source=(1, 5376), destination=(4, 7424), extents=(1, 1, 2),
            source_strides=(2, 2), destination_strides=(2, 2),
            to_float32=True))


class BatchNormCommandTests(unittest.TestCase):
    def test_shipped_batch_norm_fields_and_round_trip(self):
        image = (Path(__file__).resolve().parents[1] /
                 'blobs/official/g2-2.2.6.10/firmware_codec.bin').read_bytes()
        commands = decode_program(image[0x18d90:0x18d90 + 9164])
        self.assertEqual(commands[5].body, BatchNormCommand(
            source=(1, 960), scale=(6, 98194), bias=(6, 98002),
            destination=(1, 0), extents=(1, 5, 64),
            source_strides=(480, 96), destination_strides=(480, 96)))
        record_offset = sum(len(encode_command(command)) for command in commands[:5])
        self.assertEqual(encode_command(commands[5]),
                         image[0x18d90 + record_offset:0x18d90 + record_offset + 44])

    def test_rejects_nonzero_unclassified_tail(self):
        body = BatchNormCommand(source=(1, 0), scale=(6, 0), bias=(6, 2),
                                destination=(1, 4), extents=(1, 1, 1),
                                source_strides=(2, 2), destination_strides=(2, 2))
        encoded = bytearray(encode_command(Command(body=body)))
        encoded[-1] = 1
        with self.assertRaises(CommandFormatError):
            decode_command(bytes(encoded))


class TransposeCommandTests(unittest.TestCase):
    def test_shipped_transpose_fields_and_round_trip(self):
        image = (Path(__file__).resolve().parents[1] /
                 'blobs/official/g2-2.2.6.10/firmware_codec.bin').read_bytes()
        commands = decode_program(image[0x18d90:0x18d90 + 9164])
        self.assertEqual(commands[9].body, TransposeCommand(
            source=(1, 960), destination=(1, 0), mode=1,
            dimensions=(32, 5, 3, 1), first_pitch=96, second_pitch=5))
        record_offset = sum(len(encode_command(command)) for command in commands[:9])
        self.assertEqual(encode_command(commands[9]),
                         image[0x18d90 + record_offset:0x18d90 + record_offset + 24])

    def test_rejects_unclassified_reserved_byte(self):
        body = TransposeCommand(source=(1, 0), destination=(1, 128), mode=1,
                                dimensions=(4, 8, 1, 1), first_pitch=16,
                                second_pitch=8)
        encoded = bytearray(encode_command(Command(body=body)))
        encoded[4 + 9] = 1
        with self.assertRaises(CommandFormatError):
            decode_command(bytes(encoded))


class MatrixCommandTests(unittest.TestCase):
    def test_shipped_matrix_families_are_typed(self):
        image = (Path(__file__).resolve().parents[1] /
                 'blobs/official/g2-2.2.6.10/firmware_codec.bin').read_bytes()
        commands = decode_program(image[0x18d90:0x18d90 + 9164])
        self.assertEqual(commands[126].body, FullyConnectedCommand(
            source=(1, 256), weights=(6, 15622), destination=(1, 0),
            bias=(6, 14598), dimensions=(42, 128), tile=(10, 32, 2, 4),
            coefficients=(0xb00b, 0x1413), final_control_low16=0x2000))
        self.assertEqual(commands[2].body, ConvolutionCommand(
            source=(1, 1408), weights=(6, 102226), destination=(1, 0),
            bias=(6, 98386), dimensions=(96, 40), tile=(32, 8, 3, 2),
            pitches=(13, 1), geometry_control0=0x15,
            geometry_control1=0x12, kernel_control=5,
            coefficients=(0xb25d, 0x162c), final_control_low16=0x7800))
        self.assertEqual(commands[10].body, DepthwiseConvolutionCommand(
            source=(1, 0), weights=(6, 97042), destination=(1, 1920),
            geometry0=(5, 1, 1, 1), geometry1=(1, 1, 14, 32),
            geometry2=(14, 32, 28, 32), pitches=(5, 1),
            geometry_control=0x60, kernel_control0=0x12,
            kernel_control1=0x15))

    def test_unclassified_matrix_variant_stays_raw(self):
        command = Command(body=RawCommand(opcode=0x40, payload=bytes(44)))
        decoded, _ = decode_command(encode_command(command))
        self.assertEqual(decoded, command)


class HeaderFramingTests(unittest.TestCase):
    def test_header_reserved_round_trip(self):
        body = RawCommand(opcode=0x40, payload=bytes(OPCODE_SIZES[0x40] - 4))
        cmd = Command(body=body, header_reserved=0x300)
        decoded, _ = decode_command(encode_command(cmd))
        self.assertEqual(decoded, cmd)

    def test_rejects_absolute_link_bit(self):
        header = 0x01 | (1 << 16)
        data = struct.pack('<I', header) + bytes(48)
        with self.assertRaises(CommandFormatError):
            decode_command(data)

    def test_rejects_reserved_overlapping_known_bits(self):
        with self.assertRaises(CommandFormatError):
            encode_command(Command(body=RawCommand(opcode=0x43, payload=bytes(20)), header_reserved=1))


class ProgramRoundTripTests(unittest.TestCase):
    def test_random_synthetic_program(self):
        rng = random.Random(5)
        commands = []
        for i in range(50):
            last = i == 49
            if rng.random() < 0.5:
                body = CopyCommand(source=_random_address(rng), destination=_random_address(rng),
                                    extents=_random_extents(rng), source_strides=_random_strides(rng),
                                    destination_strides=_random_strides(rng))
            else:
                kind = rng.choice(('tensor_vector', 'tensor_tensor'))
                body = TensorOpCommand(kind=kind, arithmetic=rng.choice(('add', 'sub', 'mul', 'div')),
                                        source_a=_random_address(rng), source_b=_random_address(rng),
                                        destination=_random_address(rng), extents=_random_extents(rng),
                                        source_strides=_random_strides(rng),
                                        destination_strides=_random_strides(rng))
            commands.append(Command(body=body, link=TERMINAL_SELF_LINK if last else None))
        data = emit_program(commands)
        self.assertEqual(decode_program(data), commands)


class ShippedCommandBlockOracleTests(unittest.TestCase):
    """Decode the authenticated shipped 9,164-byte command block and
    re-encode it; this qualifies the emitter's byte-exact fidelity to the
    real ISA. It does not admit the shipped graph or any of its bytes as
    source -- see g2/docs/reference/toolchains.md and firmware-formats.md."""

    @classmethod
    def setUpClass(cls):
        import hashlib
        image_path = Path(__file__).resolve().parents[1] / 'blobs/official/g2-2.2.6.10/firmware_codec.bin'
        image_sha = 'b06dfef7faa2f1e52d2aacd07958d4b96ffc36dca5077ac9149e48f19fc9c4d0'
        sha = lambda data: hashlib.sha256(data).hexdigest()
        image = image_path.read_bytes()
        IMAGE_SHA = image_sha
        if sha(image) != IMAGE_SHA:
            raise AssertionError('firmware image authentication failed')
        cls.data = image[0x18d90:0x18d90 + 9164]
        expected_sha = 'c38ed6d22c7c0b6178288678364acd10bd5730aa382c1e19a32f6cf2bd1430b9'
        if sha(cls.data) != expected_sha:
            raise AssertionError('command block authentication failed')

    def test_decode_then_reencode_matches_oracle_exactly(self):
        commands = decode_program(self.data)
        self.assertEqual(len(commands), 212)
        reencoded = emit_program(commands)
        self.assertEqual(reencoded, self.data)

    def test_shipped_block_uses_typed_bodies(self):
        commands = decode_program(self.data)
        kinds = {type(c.body).__name__ for c in commands}
        self.assertEqual(kinds, {'CopyCommand', 'TensorOpCommand', 'ActivationCommand',
                                 'BatchNormCommand', 'TransposeCommand', 'ReduceCommand',
                                 'ActivationMode4Command', 'FormatCommand',
                                 'FullyConnectedCommand', 'ConvolutionCommand',
                                 'DepthwiseConvolutionCommand'})
        typed = sum(1 for c in commands if not isinstance(c.body, RawCommand))
        self.assertEqual(typed, 212)


def _encode(body):
    return encode_command(Command(body=body))


if __name__ == '__main__':
    unittest.main()
