/* SPDX-License-Identifier: MIT */
/*
 * Clean-room typed provider boundary for proprietary GX8002 KWS weights.
 * No model byte, vendor implementation, or production route is included.
 */
#include "runtime_gx8002_kws_model_boundary.h"

typedef struct open_cfw_sha256_context {
    uint32_t state[8];
    uint64_t bit_count;
    uint8_t block[64];
    size_t used;
} open_cfw_sha256_context;

static uint32_t rotr32(uint32_t value, uint32_t count)
{
    return (value >> count) | (value << (32U - count));
}

static uint32_t load_be32(const uint8_t *source)
{
    return ((uint32_t)source[0] << 24) | ((uint32_t)source[1] << 16) |
           ((uint32_t)source[2] << 8) | (uint32_t)source[3];
}

static void store_be32(uint8_t *destination, uint32_t value)
{
    destination[0] = (uint8_t)(value >> 24);
    destination[1] = (uint8_t)(value >> 16);
    destination[2] = (uint8_t)(value >> 8);
    destination[3] = (uint8_t)value;
}

static void sha256_compress(open_cfw_sha256_context *context,
                            const uint8_t block[64])
{
    static const uint32_t constants[64] = {
        0x428a2f98U, 0x71374491U, 0xb5c0fbcfU, 0xe9b5dba5U,
        0x3956c25bU, 0x59f111f1U, 0x923f82a4U, 0xab1c5ed5U,
        0xd807aa98U, 0x12835b01U, 0x243185beU, 0x550c7dc3U,
        0x72be5d74U, 0x80deb1feU, 0x9bdc06a7U, 0xc19bf174U,
        0xe49b69c1U, 0xefbe4786U, 0x0fc19dc6U, 0x240ca1ccU,
        0x2de92c6fU, 0x4a7484aaU, 0x5cb0a9dcU, 0x76f988daU,
        0x983e5152U, 0xa831c66dU, 0xb00327c8U, 0xbf597fc7U,
        0xc6e00bf3U, 0xd5a79147U, 0x06ca6351U, 0x14292967U,
        0x27b70a85U, 0x2e1b2138U, 0x4d2c6dfcU, 0x53380d13U,
        0x650a7354U, 0x766a0abbU, 0x81c2c92eU, 0x92722c85U,
        0xa2bfe8a1U, 0xa81a664bU, 0xc24b8b70U, 0xc76c51a3U,
        0xd192e819U, 0xd6990624U, 0xf40e3585U, 0x106aa070U,
        0x19a4c116U, 0x1e376c08U, 0x2748774cU, 0x34b0bcb5U,
        0x391c0cb3U, 0x4ed8aa4aU, 0x5b9cca4fU, 0x682e6ff3U,
        0x748f82eeU, 0x78a5636fU, 0x84c87814U, 0x8cc70208U,
        0x90befffaU, 0xa4506cebU, 0xbef9a3f7U, 0xc67178f2U
    };
    uint32_t words[64];
    uint32_t a, b, c, d, e, f, g, h;
    size_t index;

    for (index = 0; index < 16U; ++index) {
        words[index] = load_be32(block + index * 4U);
    }
    for (; index < 64U; ++index) {
        uint32_t s0 = rotr32(words[index - 15U], 7U) ^
                      rotr32(words[index - 15U], 18U) ^
                      (words[index - 15U] >> 3U);
        uint32_t s1 = rotr32(words[index - 2U], 17U) ^
                      rotr32(words[index - 2U], 19U) ^
                      (words[index - 2U] >> 10U);
        words[index] = words[index - 16U] + s0 + words[index - 7U] + s1;
    }

    a = context->state[0]; b = context->state[1];
    c = context->state[2]; d = context->state[3];
    e = context->state[4]; f = context->state[5];
    g = context->state[6]; h = context->state[7];
    for (index = 0; index < 64U; ++index) {
        uint32_t upper = rotr32(a, 2U) ^ rotr32(a, 13U) ^ rotr32(a, 22U);
        uint32_t majority = (a & b) ^ (a & c) ^ (b & c);
        uint32_t lower = rotr32(e, 6U) ^ rotr32(e, 11U) ^ rotr32(e, 25U);
        uint32_t choose = (e & f) ^ ((~e) & g);
        uint32_t first = h + lower + choose + constants[index] + words[index];
        uint32_t second = upper + majority;
        h = g; g = f; f = e; e = d + first;
        d = c; c = b; b = a; a = first + second;
    }
    context->state[0] += a; context->state[1] += b;
    context->state[2] += c; context->state[3] += d;
    context->state[4] += e; context->state[5] += f;
    context->state[6] += g; context->state[7] += h;
}

static void sha256_initialize(open_cfw_sha256_context *context)
{
    static const uint32_t initial[8] = {
        0x6a09e667U, 0xbb67ae85U, 0x3c6ef372U, 0xa54ff53aU,
        0x510e527fU, 0x9b05688cU, 0x1f83d9abU, 0x5be0cd19U
    };
    size_t index;
    for (index = 0; index < 8U; ++index) context->state[index] = initial[index];
    context->bit_count = 0U;
    context->used = 0U;
}

static void sha256_update(open_cfw_sha256_context *context,
                          const uint8_t *source, size_t size)
{
    while (size != 0U) {
        size_t room = 64U - context->used;
        size_t take = size < room ? size : room;
        size_t index;
        for (index = 0; index < take; ++index) {
            context->block[context->used + index] = source[index];
        }
        context->used += take;
        context->bit_count += (uint64_t)take * 8U;
        source += take;
        size -= take;
        if (context->used == 64U) {
            sha256_compress(context, context->block);
            context->used = 0U;
        }
    }
}

static void sha256_finish(open_cfw_sha256_context *context, uint8_t digest[32])
{
    uint64_t bit_count = context->bit_count;
    size_t index;
    context->block[context->used++] = 0x80U;
    if (context->used > 56U) {
        while (context->used < 64U) context->block[context->used++] = 0U;
        sha256_compress(context, context->block);
        context->used = 0U;
    }
    while (context->used < 56U) context->block[context->used++] = 0U;
    for (index = 0; index < 8U; ++index) {
        context->block[63U - index] = (uint8_t)(bit_count >> (index * 8U));
    }
    sha256_compress(context, context->block);
    for (index = 0; index < 8U; ++index) {
        store_be32(digest + index * 4U, context->state[index]);
    }
}

static void clear_segment(uint8_t *destination, size_t size)
{
    volatile uint8_t *cursor = destination;
    size_t index;
    for (index = 0; index < size; ++index) {
        cursor[index] = 0U;
    }
}

static int digest_is_expected(const uint8_t digest[32],
                              const uint8_t expected[32])
{
    uint32_t difference = 0U;
    size_t index;
    for (index = 0; index < 32U; ++index) difference |= digest[index] ^ expected[index];
    return difference == 0U;
}

int32_t open_cfw_gx8002_authenticated_segment_load(
    const open_cfw_gx8002_segment_ports *ports,
    uint8_t *destination,
    size_t capacity,
    size_t expected_size,
    const uint8_t expected_sha256[32])
{
    open_cfw_sha256_context hash;
    uint8_t digest[32];
    size_t bytes_written = 0U;
    int32_t provider_status;

    if (ports == 0 || destination == 0 || expected_sha256 == 0 || expected_size == 0U ||
        capacity < expected_size) {
        return OPEN_CFW_GX8002_MODEL_INVALID;
    }
    if (ports->provider == 0) return OPEN_CFW_GX8002_MODEL_UNSUPPORTED;

    provider_status = ports->provider(ports->context, destination,
                                      expected_size, &bytes_written);
    if (provider_status != 0) {
        clear_segment(destination, expected_size);
        return OPEN_CFW_GX8002_MODEL_PROVIDER_FAILED;
    }
    if (bytes_written != expected_size) {
        clear_segment(destination, expected_size);
        return OPEN_CFW_GX8002_MODEL_IDENTITY_MISMATCH;
    }
    sha256_initialize(&hash);
    sha256_update(&hash, destination, bytes_written);
    sha256_finish(&hash, digest);
    if (!digest_is_expected(digest, expected_sha256)) {
        clear_segment(destination, expected_size);
        return OPEN_CFW_GX8002_MODEL_IDENTITY_MISMATCH;
    }
    return OPEN_CFW_GX8002_MODEL_OK;
}

int32_t open_cfw_gx8002_kws_model_load(
    const open_cfw_gx8002_kws_model_ports *ports,
    uint8_t *destination,
    size_t capacity)
{
    static const uint8_t expected[32] = {
        0x39U, 0x79U, 0x71U, 0x42U, 0x7dU, 0x70U, 0x97U, 0x18U,
        0x0dU, 0x07U, 0xebU, 0x63U, 0xf9U, 0x82U, 0x29U, 0x04U,
        0xa5U, 0x55U, 0xe5U, 0x1fU, 0x76U, 0x43U, 0xd9U, 0x46U,
        0xebU, 0xb3U, 0x8dU, 0x71U, 0xa9U, 0x67U, 0xf8U, 0xcfU
    };
    return open_cfw_gx8002_authenticated_segment_load(
        ports, destination, capacity, OPEN_CFW_GX8002_KWS_WEIGHT_SIZE, expected);
}
