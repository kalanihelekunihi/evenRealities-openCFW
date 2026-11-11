/* SPDX-License-Identifier: MIT
 * Typed GXNPU transpose commands for the locked G2 KWS graph.
 * The pinned cmodel's opcode-0x43 dispatch calls parse_transpose_cmd,
 * which reads source/destination addresses, a mode byte, four dimension
 * bytes and two 16-bit pitch fields. Their exact axis convention remains
 * unverified; the descriptor retains the parser's field order. No opaque
 * command bytes or model weights are included.
 */
#include "kws_transpose_commands.h"

struct g2_address { uint8_t slot; uint32_t offset; };
struct g2_transpose_spec {
    uint16_t program_index;
    struct g2_address source;
    struct g2_address destination;
    uint8_t dimensions[4];
    uint16_t first_pitch;
    uint16_t second_pitch;
};

static const struct g2_transpose_spec transpose[G2_KWS_TRANSPOSE_COMMAND_COUNT] = {
    {  9, {1, 960}, {1, 0}, {32, 5, 3, 1}, 96, 5},
    { 11, {1, 1920}, {1, 0}, {1, 32, 1, 3}, 1, 96},
    { 24, {3, 1040}, {1, 256}, {7, 32, 1, 4}, 7, 128},
    { 41, {1, 2816}, {1, 256}, {32, 8, 4, 1}, 128, 8},
    { 43, {1, 5376}, {1, 256}, {1, 32, 1, 4}, 1, 128},
    { 56, {3, 2832}, {1, 5376}, {8, 32, 1, 4}, 8, 128},
    { 75, {1, 7936}, {1, 5376}, {32, 9, 4, 1}, 128, 9},
    { 77, {1, 0}, {1, 5376}, {1, 32, 1, 4}, 1, 128},
    { 90, {3, 4880}, {1, 5376}, {9, 32, 1, 4}, 9, 128},
    {111, {1, 10496}, {1, 5376}, {32, 10, 4, 1}, 128, 10},
    {113, {1, 0}, {1, 5376}, {1, 32, 1, 4}, 1, 128},
    {151, {1, 3072}, {1, 0}, {32, 7, 4, 1}, 128, 7},
    {166, {1, 8192}, {1, 2560}, {32, 8, 4, 1}, 128, 8},
    {183, {1, 10752}, {1, 7124}, {32, 9, 4, 1}, 128, 9},
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

int g2_kws_emit_transpose(unsigned ordinal, uint8_t *out, size_t capacity,
                          unsigned *program_index)
{
    const struct g2_transpose_spec *spec;
    unsigned i;
    if (ordinal >= G2_KWS_TRANSPOSE_COMMAND_COUNT || out == 0 ||
        capacity < G2_KWS_TRANSPOSE_COMMAND_BYTES)
        return -1;
    spec = &transpose[ordinal];
    for (i = 0; i < G2_KWS_TRANSPOSE_COMMAND_BYTES; ++i)
        out[i] = 0;
    put32(out, UINT32_C(0x43) | (UINT32_C(1) << 17) | UINT32_C(0x100));
    put32(out + 4, address_word(spec->source));
    put32(out + 8, address_word(spec->destination));
    out[12] = 1; /* Mode byte observed in all 14 locked records. */
    for (i = 0; i < 4; ++i)
        out[16 + i] = spec->dimensions[i];
    put16(out + 20, spec->first_pitch);
    put16(out + 22, spec->second_pitch);
    if (program_index != 0)
        *program_index = spec->program_index;
    return 0;
}
