/* SPDX-License-Identifier: MIT
 * Typed source for the twelve ReLU/sigmoid GXNPU commands in the locked
 * G2 KWS graph. The other 200 commands and model weights are not supplied
 * by this unit. In particular, this file contains no retained opcode array.
 *
 * Format: NationalChip gxDNN grus libcmodel.a parse_op_active_cmd reads
 * source/destination, extents, and strides. calc_op_active dispatches mode
 * 1 to active_relu and mode 2 to active_sigmoid. The command framing and
 * fields are corroborated by the locked 9,164-byte stream and the gxDNN
 * command emitter. All twelve commands are sequential, slot-1 addresses,
 * with equal source/destination strides and no immediate parameter.
 */
#include "kws_activation_commands.h"

enum { G2_ACTIVATION_RELU = 1, G2_ACTIVATION_SIGMOID = 2 };

struct activation_spec {
    uint16_t program_index;
    uint16_t source_offset;
    uint16_t destination_offset;
    uint16_t middle_extent;
    uint16_t inner_extent;
    uint16_t outer_stride;
    uint16_t middle_stride;
    uint8_t mode;
};

static const struct activation_spec activations[G2_KWS_ACTIVATION_COUNT] = {
    {  7,    0,  960, 7, 64, 448, 64, G2_ACTIVATION_RELU },
    {  8,  896, 1856, 1, 32,  32, 32, G2_ACTIVATION_RELU },
    { 16,    0,  192, 1, 64,  64, 64, G2_ACTIVATION_RELU },
    { 17,  128,  320, 1, 32,  32, 32, G2_ACTIVATION_RELU },
    { 23,  256,    0, 2, 64, 128, 64, G2_ACTIVATION_RELU },
    { 48,  256,  512, 2, 64, 128, 64, G2_ACTIVATION_RELU },
    { 54,  256,  512, 2, 64, 128, 64, G2_ACTIVATION_RELU },
    { 82,  512,    0, 2, 64, 128, 64, G2_ACTIVATION_RELU },
    { 88,  512,    0, 2, 64, 128, 64, G2_ACTIVATION_RELU },
    {118,  256,    0, 2, 64, 128, 64, G2_ACTIVATION_RELU },
    {124,  256,    0, 2, 64, 128, 64, G2_ACTIVATION_RELU },
    {149, 5380, 5376, 1,  2,   2,  2, G2_ACTIVATION_SIGMOID }
};

static void put16(uint8_t *out, uint16_t value)
{
    out[0] = (uint8_t)value;
    out[1] = (uint8_t)(value >> 8);
}

static void put32(uint8_t *out, uint32_t value)
{
    put16(out, (uint16_t)value);
    put16(out + 2, (uint16_t)(value >> 16));
}

int g2_kws_emit_activation(unsigned ordinal, uint8_t *out, size_t capacity,
                           unsigned *program_index)
{
    const struct activation_spec *spec;
    unsigned i;
    uint32_t extents;
    if (ordinal >= G2_KWS_ACTIVATION_COUNT || out == 0 ||
        capacity < G2_KWS_ACTIVATION_COMMAND_BYTES)
        return -1;
    spec = &activations[ordinal];
    for (i = 0; i < G2_KWS_ACTIVATION_COMMAND_BYTES; ++i)
        out[i] = 0;
    /* Opcode 1, sequential link, and the stock precision/header flag. */
    put32(out, UINT32_C(1) | (UINT32_C(1) << 8) |
                   (UINT32_C(1) << 17));
    put32(out + 4, UINT32_C(0x10000000) | spec->source_offset);
    put32(out + 16, UINT32_C(0x10000000) | spec->destination_offset);
    put32(out + 20, (uint32_t)spec->mode << 4);
    extents = (UINT32_C(1) << 20) |
              ((uint32_t)spec->middle_extent << 8) |
              spec->inner_extent;
    put32(out + 24, extents);
    put16(out + 28, spec->middle_stride);
    put16(out + 30, spec->outer_stride);
    put16(out + 32, spec->middle_stride);
    put16(out + 34, spec->outer_stride);
    if (program_index != 0)
        *program_index = spec->program_index;
    return 0;
}
