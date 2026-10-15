/* R1-owned orchestration from authenticated application 2.2.6.0009.
 * Stock: 0x48B02 (162 bytes), 0x891A4 (20), 0x98E22 (22).
 * AES bodies remain owned by the pinned upstream tiny-AES-c implementation.
 * See r1/docs/correlation/TINY-AES-CORRELATION.md. */
#include "stock_two_pass.h"
#include "aes.h"

_Static_assert(AES_BLOCKLEN == 16, "stock AES block width");
_Static_assert(AES_KEYLEN == 16, "stock AES-128 key width");
_Static_assert(AES_keyExpSize == 176, "stock expanded key extent");
_Static_assert(sizeof(struct AES_ctx) == 176, "stock schedule without CBC/CTR state");

void r1_stock_xor(uint8_t *output, const uint8_t *chain, int32_t length) {
    for (int32_t i = 0; i < length; ++i)
        output[i] ^= chain[i];
}

void r1_stock_two_pass(const uint8_t *input, int32_t length,
                      const uint8_t second_key[16], const uint8_t first_key[16],
                      uint8_t *output, int32_t *output_length) {
    struct AES_ctx context;
    uint8_t previous[16];
    uint8_t saved[16];
    *output_length = length;
    for (int32_t i = 0; i < length; ++i)
        output[i] = input[i];
    AES_init_ctx(&context, second_key);
    const int32_t blocks = length / 16;
    const uint8_t *chain = first_key;
    for (int32_t block = blocks; block > 0;) {
        --block;
        uint8_t *current = output + block * 16;
        AES_ECB_decrypt(&context, current);
        r1_stock_xor(current, chain, 16);
        chain = input + block * 16;
    }
    AES_init_ctx(&context, first_key);
    chain = second_key;
    for (int32_t block = 0; block < blocks; ++block) {
        uint8_t *current = output + block * 16;
        for (int32_t i = 0; i < 16; ++i)
            saved[i] = current[i];
        AES_ECB_decrypt(&context, current);
        r1_stock_xor(current, chain, 16);
        for (int32_t i = 0; i < 16; ++i)
            previous[i] = saved[i];
        chain = previous;
    }
}

uint32_t r1_stock_two_pass_callback(const uint8_t *input, int32_t length,
                                  const uint8_t key[32], uint8_t *output,
                                  int32_t *output_length) {
    r1_stock_two_pass(input, length, key + 16, key, output, output_length);
    return 0;
}
