/* SPDX-License-Identifier: MIT
 * Field-level opcode-0x40 fully connected commands for the locked KWS graph.
 * The pinned cmodel maps this opcode to parse_fc_cmd, which reads five
 * address fields, two 16-bit dimensions, four tile bytes, and coefficient
 * and control fields. The fourth address is zero in all four records.
 * Tile-axis and final control-bit semantics remain unresolved, so this is
 * not a claim of full execution equivalence. No opaque opcode byte array or
 * model weights are included.
 */
#include "kws_fc_commands.h"

struct g2_address { uint8_t slot; uint32_t offset; };
struct g2_fc_spec {
    uint16_t program_index;
    struct g2_address input;
    struct g2_address weights;
    struct g2_address destination;
    struct g2_address bias;
    uint16_t input_dimension;
    uint16_t output_dimension;
    uint8_t tile[4];
    uint16_t coefficient0;
    uint16_t coefficient1;
    uint16_t final_control_low16;
};

static const struct g2_fc_spec fc[G2_KWS_FC_COMMAND_COUNT] = {
    {126, {1, 256}, {6, 15622}, {1, 0}, {6, 14598},
     42, 128, {10, 32, 2, 4}, 0xb00b, 0x1413, 0x2000},
    {128, {1, 5376}, {6, 11900}, {1, 5460}, {6, 11388},
     64, 42, {32, 10, 2, 2}, 0xb29e, 0x16ab, 0x1000},
    {144, {1, 5504}, {6, 2046}, {1, 7124}, {6, 1022},
     128, 64, {32, 32, 4, 2}, 0xb02a, 0x142a, 0x2000},
    {147, {1, 7124}, {6, 516}, {1, 5376}, {6, 4},
     2, 128, {2, 32, 1, 4}, 0xb111, 0x151b, 0x1000},
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

int g2_kws_emit_fc(unsigned ordinal, uint8_t *out, size_t capacity,
                   unsigned *program_index)
{
    const struct g2_fc_spec *spec;
    unsigned i;
    if (ordinal >= G2_KWS_FC_COMMAND_COUNT || out == 0 ||
        capacity < G2_KWS_FC_COMMAND_BYTES)
        return -1;
    spec = &fc[ordinal];
    for (i = 0; i < G2_KWS_FC_COMMAND_BYTES; ++i)
        out[i] = 0;
    put32(out, UINT32_C(0x40) | (UINT32_C(1) << 17) | UINT32_C(0x100));
    put32(out + 4, address_word(spec->input));
    put32(out + 8, address_word(spec->weights));
    put32(out + 12, address_word(spec->destination));
    put32(out + 20, address_word(spec->bias));
    put16(out + 24, spec->input_dimension);
    put16(out + 26, spec->output_dimension);
    for (i = 0; i < 4; ++i)
        out[28 + i] = spec->tile[i];
    out[35] = 1; /* Parser reads the bit at body+31 as one. */
    put16(out + 40, spec->coefficient0);
    put16(out + 42, spec->coefficient1);
    put16(out + 44, spec->final_control_low16);
    put16(out + 46, UINT16_C(0x8000));
    if (program_index != 0)
        *program_index = spec->program_index;
    return 0;
}
