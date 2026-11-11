/* SPDX-License-Identifier: MIT
 * Field-level opcode-0x41 convolution and opcode-0x42 depthwise convolution
 * records from the locked KWS graph. The pinned cmodel dispatches these to
 * parse_conv2d_cmd and parse_ds_conv2d_cmd, respectively. Parser field
 * offsets establish addresses, geometry, pitches, coefficients and controls.
 * Some geometry-axis and control-bit meanings are unresolved; the descriptors
 * retain parser field order. This file contains no opaque opcode byte array
 * or model weights.
 */
#include "kws_conv_commands.h"

struct g2_address { uint8_t slot; uint32_t offset; };
struct g2_dimensions { uint16_t first; uint16_t second; };
struct g2_pitches { uint16_t first; uint16_t second; };
struct g2_conv_spec {
    uint16_t program_index;
    struct g2_address input;
    struct g2_address weights;
    struct g2_address destination;
    struct g2_address bias;
    struct g2_dimensions dimensions;
    uint8_t tile[4];
    struct g2_pitches pitches;
    uint8_t geometry_control0;
    uint8_t geometry_control1;
    uint8_t kernel_control;
    uint16_t coefficient0;
    uint16_t coefficient1;
    uint16_t final_control_low16;
};
struct g2_depthwise_spec {
    uint16_t program_index;
    struct g2_address input;
    struct g2_address weights;
    struct g2_address destination;
    uint8_t geometry0[4];
    uint8_t geometry1[4];
    uint8_t geometry2[4];
    struct g2_pitches pitches;
    uint8_t geometry_control;
    uint8_t kernel_control0;
    uint8_t kernel_control1;
};

static const struct g2_conv_spec conv[G2_KWS_CONV_COMMAND_COUNT] = {
    {2, {1, 1408}, {6, 102226}, {1, 0}, {6, 98386},
     {96, 40}, {32, 8, 3, 2}, {13, 1}, 0x15, 0x12, 0x05, 0xb25d, 0x162c, 0x7800},
    {18, {1, 192}, {6, 86384}, {1, 384}, {6, 84848},
     {128, 96}, {32, 32, 4, 3}, {1, 1}, 0x11, 0x11, 0x01, 0xb47d, 0x1839, 0x3000},
    {49, {1, 512}, {6, 66302}, {1, 256}, {6, 64254},
     {128, 128}, {32, 32, 4, 4}, {1, 1}, 0x11, 0x11, 0x01, 0xb1eb, 0x16a5, 0x4000},
    {83, {1, 0}, {6, 45192}, {1, 512}, {6, 43144},
     {128, 128}, {32, 32, 4, 4}, {1, 1}, 0x11, 0x11, 0x01, 0xb476, 0x17e0, 0x4000},
    {119, {1, 0}, {6, 23504}, {1, 256}, {6, 21456},
     {128, 128}, {32, 32, 4, 4}, {1, 1}, 0x11, 0x11, 0x01, 0xb034, 0x142c, 0x4000},
};
static const struct g2_depthwise_spec depthwise[G2_KWS_DEPTHWISE_COMMAND_COUNT] = {
    {10, {1, 0}, {6, 97042}, {1, 1920},
     {5, 1, 1, 1}, {1, 1, 14, 32}, {14, 32, 28, 32}, {5, 1}, 0x60, 0x12, 0x15},
    {42, {1, 256}, {6, 82288}, {1, 5376},
     {8, 1, 1, 1}, {1, 1, 25, 32}, {25, 32, 25, 32}, {8, 1}, 0x80, 0x11, 0x18},
    {76, {1, 5376}, {6, 61438}, {1, 0},
     {9, 1, 1, 1}, {1, 1, 24, 32}, {24, 32, 24, 32}, {9, 1}, 0x80, 0x11, 0x19},
    {112, {1, 5376}, {6, 40072}, {1, 0},
     {10, 1, 1, 1}, {1, 1, 23, 32}, {23, 32, 23, 32}, {10, 1}, 0x80, 0x11, 0x1a},
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

int g2_kws_emit_conv(unsigned ordinal, uint8_t *out, size_t capacity,
                      unsigned *program_index)
{
    const struct g2_conv_spec *spec;
    unsigned i;
    if (ordinal >= G2_KWS_CONV_COMMAND_COUNT || out == 0 ||
        capacity < G2_KWS_CONV_COMMAND_BYTES)
        return -1;
    spec = &conv[ordinal];
    for (i = 0; i < G2_KWS_CONV_COMMAND_BYTES; ++i)
        out[i] = 0;
    put32(out, UINT32_C(0x41) | (UINT32_C(1) << 17) | UINT32_C(0x100));
    put32(out + 4, address_word(spec->input));
    put32(out + 8, address_word(spec->weights));
    put32(out + 12, address_word(spec->destination));
    put32(out + 20, address_word(spec->bias));
    put16(out + 24, spec->dimensions.first);
    put16(out + 26, spec->dimensions.second);
    for (i = 0; i < 4; ++i)
        out[28 + i] = spec->tile[i];
    put16(out + 32, spec->pitches.first);
    put16(out + 34, spec->pitches.second);
    out[36] = spec->geometry_control0;
    out[37] = 0x11;
    out[39] = 1;
    out[43] = spec->geometry_control1;
    out[44] = spec->kernel_control;
    out[46] = 1;
    put16(out + 52, spec->coefficient0);
    put16(out + 54, spec->coefficient1);
    put16(out + 56, spec->final_control_low16);
    put16(out + 58, UINT16_C(0x8000));
    if (program_index != 0)
        *program_index = spec->program_index;
    return 0;
}

int g2_kws_emit_depthwise(unsigned ordinal, uint8_t *out, size_t capacity,
                           unsigned *program_index)
{
    const struct g2_depthwise_spec *spec;
    unsigned i;
    if (ordinal >= G2_KWS_DEPTHWISE_COMMAND_COUNT || out == 0 ||
        capacity < G2_KWS_DEPTHWISE_COMMAND_BYTES)
        return -1;
    spec = &depthwise[ordinal];
    for (i = 0; i < G2_KWS_DEPTHWISE_COMMAND_BYTES; ++i)
        out[i] = 0;
    put32(out, UINT32_C(0x42) | (UINT32_C(1) << 17) | UINT32_C(0x100));
    put32(out + 4, address_word(spec->input));
    put32(out + 8, address_word(spec->weights));
    put32(out + 12, address_word(spec->destination));
    for (i = 0; i < 4; ++i) {
        out[20 + i] = spec->geometry0[i];
        out[24 + i] = spec->geometry1[i];
        out[28 + i] = spec->geometry2[i];
    }
    put16(out + 32, spec->pitches.first);
    put16(out + 34, spec->pitches.second);
    out[36] = spec->geometry_control;
    out[38] = 1;
    put16(out + 40, 1);
    put16(out + 42, 1);
    out[44] = spec->kernel_control0;
    out[45] = spec->kernel_control1;
    out[46] = 1;
    if (program_index != 0)
        *program_index = spec->program_index;
    return 0;
}
