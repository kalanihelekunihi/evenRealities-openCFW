#include "openr1/r1_crypto.h"

#include <stdint.h>
#include <string.h>

#if defined(R1_USE_TINYCRYPT)
#include <tinycrypt/aes.h>
#else
#include "aes.h"
#endif

static void secure_clear(void *storage, size_t length);

#if defined(R1_USE_TINYCRYPT)
typedef struct tc_aes_key_sched_struct r1_aes_context;

static void r1_aes_initialize(r1_aes_context *context,
                              const uint8_t key[R1_AES_BLOCK_BYTES]) {
    (void)tc_aes128_set_decrypt_key(context, key);
}

static void r1_aes_decrypt(r1_aes_context *context,
                           uint8_t block[R1_AES_BLOCK_BYTES]) {
    uint8_t plaintext[R1_AES_BLOCK_BYTES];
    (void)tc_aes_decrypt(plaintext, block, context);
    memcpy(block, plaintext, sizeof plaintext);
    secure_clear(plaintext, sizeof plaintext);
}
#else
typedef struct AES_ctx r1_aes_context;

static void r1_aes_initialize(r1_aes_context *context,
                              const uint8_t key[R1_AES_BLOCK_BYTES]) {
    AES_init_ctx(context, key);
}

static void r1_aes_decrypt(r1_aes_context *context,
                           uint8_t block[R1_AES_BLOCK_BYTES]) {
    AES_ECB_decrypt(context, block);
}
#endif

static void xor_block(uint8_t block[R1_AES_BLOCK_BYTES], const uint8_t *chain) {
    for (size_t index = 0u; index < R1_AES_BLOCK_BYTES; ++index) {
        block[index] ^= chain[index];
    }
}

static void secure_clear(void *storage, size_t length) {
    volatile uint8_t *bytes = (volatile uint8_t *)storage;
    while (length != 0u) {
        *bytes = 0u;
        ++bytes;
        --length;
    }
}

static int ranges_overlap(const uint8_t *left, const uint8_t *right, size_t length) {
    const uintptr_t left_address = (uintptr_t)left;
    const uintptr_t right_address = (uintptr_t)right;
    if (left_address >= right_address) {
        return left_address - right_address < length;
    }
    return right_address - left_address < length;
}

r1_error r1_dual_aes128_decrypt(const uint8_t *input, size_t length,
                                const uint8_t key[R1_DUAL_AES_KEY_BYTES],
                                uint8_t *output, size_t capacity,
                                size_t *written) {
    if (key == NULL || output == NULL || written == NULL ||
            (input == NULL && length != 0u)) {
        return R1_ERROR_ARGUMENT;
    }
    *written = 0u;
    if (length > capacity) {
        return R1_ERROR_CAPACITY;
    }
    if (length % R1_AES_BLOCK_BYTES != 0u) {
        return R1_ERROR_LENGTH;
    }
    if (length == 0u) {
        return R1_OK;
    }
    if (length != 0u && ranges_overlap(input, output, length)) {
        return R1_ERROR_ARGUMENT;
    }

    memcpy(output, input, length);

    r1_aes_context context;
    r1_aes_initialize(&context, key + R1_AES_BLOCK_BYTES);
    const uint8_t *chain = key;
    size_t block = length / R1_AES_BLOCK_BYTES;
    while (block != 0u) {
        --block;
        uint8_t *current = output + block * R1_AES_BLOCK_BYTES;
        r1_aes_decrypt(&context, current);
        xor_block(current, chain);
        chain = input + block * R1_AES_BLOCK_BYTES;
    }

    r1_aes_initialize(&context, key);
    uint8_t chain_block[R1_AES_BLOCK_BYTES];
    memcpy(chain_block, key + R1_AES_BLOCK_BYTES, sizeof chain_block);
    uint8_t previous[R1_AES_BLOCK_BYTES];
    for (block = 0u; block < length / R1_AES_BLOCK_BYTES; ++block) {
        uint8_t *current = output + block * R1_AES_BLOCK_BYTES;
        memcpy(previous, current, sizeof previous);
        r1_aes_decrypt(&context, current);
        xor_block(current, chain_block);
        memcpy(chain_block, previous, sizeof chain_block);
    }

    secure_clear(chain_block, sizeof chain_block);
    secure_clear(previous, sizeof previous);
    secure_clear(&context, sizeof context);
    *written = length;
    return R1_OK;
}
