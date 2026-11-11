/* SPDX-License-Identifier: MIT
 * Three opcode-1 commands in the locked GXNPU KWS graph. The cmodel's
 * parse_op_reduce_cmd, parse_op_active_cmd and parse_op_format_cmd establish
 * the field layout. calc_op_reduce divides its sum by the half-float divisor;
 * calc_op_format selects half-to-float conversion. Activation mode 4 uses
 * the three half-float parameters; its mathematical name remains unresolved.
 * No opaque instruction bytes or model weights are stored here.
 */
#include "kws_special_commands.h"

enum g2_special_kind { G2_REDUCE = 3, G2_ACTIVATION_MODE4 = 0, G2_FORMAT = 7 };
struct g2_address { uint8_t slot; uint32_t offset; };
struct g2_extent { uint16_t outer; uint16_t middle; uint8_t inner; };
struct g2_stride { uint16_t outer; uint16_t middle; };
struct g2_special_spec {
    uint16_t program_index;
    uint8_t kind;
    struct g2_address source;
    struct g2_address destination;
    struct g2_extent extent;
    struct g2_stride source_stride;
    struct g2_stride destination_stride;
    uint16_t divisor_or_parameter0;
    uint16_t parameter1;
    uint16_t parameter2;
};

static const struct g2_special_spec special[G2_KWS_SPECIAL_COMMAND_COUNT] = {
    {142, G2_REDUCE, {1, 0}, {1, 5376}, {1, 11, 64},
     {704, 64}, {64, 64}, 0x3c00, 0, 0},
    {146, G2_ACTIVATION_MODE4, {1, 5376}, {1, 7124}, {1, 2, 64},
     {128, 64}, {128, 64}, 0x3c34, 0xbf08, 0x3f08},
    {150, G2_FORMAT, {1, 5376}, {4, 7424}, {1, 1, 2},
     {2, 2}, {2, 2}, 0, 0, 0},
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

static uint32_t address_word(struct g2_address address)
{
    return ((uint32_t)address.slot << 28) | address.offset;
}

int g2_kws_emit_special(unsigned ordinal, uint8_t *out, size_t capacity,
                         unsigned *program_index)
{
    const struct g2_special_spec *spec;
    uint32_t control, extents;
    unsigned i;
    if (ordinal >= G2_KWS_SPECIAL_COMMAND_COUNT || out == 0 ||
        capacity < G2_KWS_SPECIAL_COMMAND_BYTES)
        return -1;
    spec = &special[ordinal];
    for (i = 0; i < G2_KWS_SPECIAL_COMMAND_BYTES; ++i)
        out[i] = 0;
    put32(out, UINT32_C(1) | (UINT32_C(1) << 17) | UINT32_C(0x100));
    put32(out + 4, address_word(spec->source));
    put32(out + 16, address_word(spec->destination));
    control = spec->kind;
    if (spec->kind == G2_REDUCE)
        control |= UINT32_C(1) << 7; /* Reduce over the middle extent. */
    else if (spec->kind == G2_ACTIVATION_MODE4)
        control |= UINT32_C(4) << 4;
    else
        control |= UINT32_C(1) << 16; /* Half-float input to float output. */
    put32(out + 20, control);
    extents = ((uint32_t)spec->extent.outer << 20) |
              ((uint32_t)spec->extent.middle << 8) | spec->extent.inner;
    put32(out + 24, extents);
    put16(out + 28, spec->source_stride.middle);
    put16(out + 30, spec->source_stride.outer);
    put16(out + 32, spec->destination_stride.middle);
    put16(out + 34, spec->destination_stride.outer);
    put16(out + 36, spec->divisor_or_parameter0);
    if (spec->kind == G2_ACTIVATION_MODE4) {
        put16(out + 40, spec->parameter1);
        put16(out + 42, spec->parameter2);
    }
    if (program_index != 0)
        *program_index = spec->program_index;
    return 0;
}
