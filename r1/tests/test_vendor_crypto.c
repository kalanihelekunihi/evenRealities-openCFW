#include <assert.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "aes.h"
#include "openr1/r1_crypto.h"

static void test_tiny_aes_ecb_vector(void) {
    static const uint8_t key[16] = {
        0x00u, 0x01u, 0x02u, 0x03u, 0x04u, 0x05u, 0x06u, 0x07u,
        0x08u, 0x09u, 0x0au, 0x0bu, 0x0cu, 0x0du, 0x0eu, 0x0fu,
    };
    static const uint8_t plaintext[16] = {
        0x00u, 0x11u, 0x22u, 0x33u, 0x44u, 0x55u, 0x66u, 0x77u,
        0x88u, 0x99u, 0xaau, 0xbbu, 0xccu, 0xddu, 0xeeu, 0xffu,
    };
    uint8_t block[16] = {
        0x69u, 0xc4u, 0xe0u, 0xd8u, 0x6au, 0x7bu, 0x04u, 0x30u,
        0xd8u, 0xcdu, 0xb7u, 0x80u, 0x70u, 0xb4u, 0xc5u, 0x5au,
    };
    struct AES_ctx context;
    AES_init_ctx(&context, key);
    AES_ECB_decrypt(&context, block);
    assert(memcmp(block, plaintext, sizeof block) == 0);
}

static void test_r1_dual_pass_vector(void) {
    static const uint8_t expected[32] = {
        0xb9u, 0x7au, 0xd8u, 0xb7u, 0xcbu, 0x5bu, 0x2fu, 0x97u,
        0xd0u, 0xf8u, 0xc5u, 0x13u, 0x2cu, 0x92u, 0x8eu, 0x9bu,
        0xafu, 0x37u, 0x7bu, 0x6cu, 0xe1u, 0x4bu, 0x8cu, 0xb4u,
        0x5bu, 0x86u, 0x36u, 0x45u, 0xcfu, 0x34u, 0xcbu, 0xebu,
    };
    uint8_t input[32];
    uint8_t key[32];
    uint8_t output[32];
    for (size_t index = 0u; index < sizeof input; ++index) {
        input[index] = (uint8_t)index;
        key[index] = (uint8_t)(index + 0x20u);
    }
    size_t written = 0u;
    assert(r1_dual_aes128_decrypt(input, sizeof input, key, output,
                                  sizeof output, &written) == R1_OK);
    assert(written == sizeof output);
    assert(memcmp(output, expected, sizeof output) == 0);
    assert(r1_dual_aes128_decrypt(input, sizeof input - 1u, key, output,
                                  sizeof output, &written) == R1_ERROR_LENGTH);
    assert(r1_dual_aes128_decrypt(input, sizeof input, key, input,
                                  sizeof input, &written) == R1_ERROR_ARGUMENT);
}

int main(void) {
    test_tiny_aes_ecb_vector();
    test_r1_dual_pass_vector();
    puts("openR1: tiny-AES-c provider and R1 adapter tests passed");
    return 0;
}
