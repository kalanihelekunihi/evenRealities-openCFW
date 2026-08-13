#ifndef OPENR1_R1_CRYPTO_H
#define OPENR1_R1_CRYPTO_H

#include <stddef.h>
#include <stdint.h>

#include "openr1/r1_protocol.h"

#define R1_AES_BLOCK_BYTES 16u
#define R1_DUAL_AES_KEY_BYTES 32u

/*
 * Recovered R1 two-pass transform. The first key half is also the reverse-pass
 * tail chain and the second key half is the forward-pass initial chain.
 * tiny-AES-c supplies every AES-128 block operation; this API owns only R1's
 * chaining order, validation, output copy, and key-schedule cleanup.
 */
r1_error r1_dual_aes128_decrypt(const uint8_t *input, size_t length,
                                const uint8_t key[R1_DUAL_AES_KEY_BYTES],
                                uint8_t *output, size_t capacity,
                                size_t *written);

#endif
