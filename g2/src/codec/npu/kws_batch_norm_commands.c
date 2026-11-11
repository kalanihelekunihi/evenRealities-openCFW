/* SPDX-License-Identifier: MIT
 * Typed GXNPU batch-normalization commands for the locked G2 KWS graph.
 * The upstream cmodel's parse_op_bn_cmd identifies the four operand
 * addresses, extents and strides; calc_op_bn multiplies input by scale,
 * then adds bias, using half-float arithmetic. Header bits 8/9 retain
 * their observed values because their full precision semantics are open.
 * No opaque instruction bytes or model weights are stored here.
 */
#include "kws_batch_norm_commands.h"

struct g2_address { uint8_t slot; uint32_t offset; };
struct g2_extent { uint16_t outer; uint16_t middle; uint8_t inner; };
struct g2_stride { uint16_t outer; uint16_t middle; };
struct g2_bn_spec {
    uint16_t program_index;
    uint16_t header_flags;
    struct g2_address input;
    struct g2_address scale;
    struct g2_address bias;
    struct g2_address destination;
    struct g2_extent extent;
    struct g2_stride input_stride;
    struct g2_stride destination_stride;
};

static const struct g2_bn_spec batch_norm[G2_KWS_BATCH_NORM_COMMAND_COUNT] = {
    {  5, 0x300, {1, 960}, {6, 98194}, {6, 98002}, {1, 0}, {1, 5, 64}, {480, 96}, {480, 96}},
    {  6, 0x000, {1, 1088}, {6, 98322}, {6, 98130}, {1, 128}, {1, 5, 32}, {480, 96}, {480, 96}},
    { 14, 0x300, {1, 960}, {6, 96850}, {6, 96658}, {1, 0}, {1, 1, 64}, {96, 96}, {96, 96}},
    { 15, 0x000, {1, 1088}, {6, 96978}, {6, 96786}, {1, 128}, {1, 1, 32}, {96, 96}, {96, 96}},
    { 21, 0x300, {1, 0}, {6, 84592}, {6, 84336}, {1, 256}, {1, 1, 64}, {128, 128}, {128, 128}},
    { 22, 0x000, {1, 128}, {6, 84720}, {6, 84464}, {1, 384}, {1, 1, 64}, {128, 128}, {128, 128}},
    { 46, 0x300, {1, 5376}, {6, 82032}, {6, 81776}, {1, 256}, {1, 1, 64}, {128, 128}, {128, 128}},
    { 47, 0x000, {1, 5504}, {6, 82160}, {6, 81904}, {1, 384}, {1, 1, 64}, {128, 128}, {128, 128}},
    { 52, 0x300, {1, 512}, {6, 63998}, {6, 63742}, {1, 256}, {1, 1, 64}, {128, 128}, {128, 128}},
    { 53, 0x000, {1, 640}, {6, 64126}, {6, 63870}, {1, 384}, {1, 1, 64}, {128, 128}, {128, 128}},
    { 80, 0x300, {1, 0}, {6, 61182}, {6, 60926}, {1, 512}, {1, 1, 64}, {128, 128}, {128, 128}},
    { 81, 0x000, {1, 128}, {6, 61310}, {6, 61054}, {1, 640}, {1, 1, 64}, {128, 128}, {128, 128}},
    { 86, 0x300, {1, 0}, {6, 42888}, {6, 42632}, {1, 512}, {1, 1, 64}, {128, 128}, {128, 128}},
    { 87, 0x000, {1, 128}, {6, 43016}, {6, 42760}, {1, 640}, {1, 1, 64}, {128, 128}, {128, 128}},
    {116, 0x300, {1, 0}, {6, 39816}, {6, 39560}, {1, 256}, {1, 1, 64}, {128, 128}, {128, 128}},
    {117, 0x000, {1, 128}, {6, 39944}, {6, 39688}, {1, 384}, {1, 1, 64}, {128, 128}, {128, 128}},
    {122, 0x300, {1, 0}, {6, 21200}, {6, 20944}, {1, 256}, {1, 1, 64}, {128, 128}, {128, 128}},
    {123, 0x000, {1, 128}, {6, 21328}, {6, 21072}, {1, 384}, {1, 1, 64}, {128, 128}, {128, 128}},
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

int g2_kws_emit_batch_norm(unsigned ordinal, uint8_t *out, size_t capacity,
                           unsigned *program_index)
{
    const struct g2_bn_spec *spec;
    uint32_t extents;
    unsigned i;
    if (ordinal >= G2_KWS_BATCH_NORM_COMMAND_COUNT || out == 0 ||
        capacity < G2_KWS_BATCH_NORM_COMMAND_BYTES)
        return -1;
    spec = &batch_norm[ordinal];
    for (i = 0; i < G2_KWS_BATCH_NORM_COMMAND_BYTES; ++i)
        out[i] = 0;
    put32(out, UINT32_C(1) | (UINT32_C(1) << 17) | spec->header_flags);
    put32(out + 4, address_word(spec->input));
    put32(out + 8, address_word(spec->scale));
    put32(out + 12, address_word(spec->bias));
    put32(out + 16, address_word(spec->destination));
    put32(out + 20, UINT32_C(8)); /* general-operation subtype: batch norm */
    extents = ((uint32_t)spec->extent.outer << 20) |
              ((uint32_t)spec->extent.middle << 8) | spec->extent.inner;
    put32(out + 24, extents);
    put16(out + 28, spec->input_stride.middle);
    put16(out + 30, spec->input_stride.outer);
    put16(out + 32, spec->destination_stride.middle);
    put16(out + 34, spec->destination_stride.outer);
    if (program_index != 0)
        *program_index = spec->program_index;
    return 0;
}
