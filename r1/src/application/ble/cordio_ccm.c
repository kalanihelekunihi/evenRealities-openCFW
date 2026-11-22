/* Source-only AES-CCM provider for the Cordio Nordic PAL's CC_AESCCM call.
 * This does not initialize CryptoCell or replace the PAL's clock/radio setup.
 * AES blocks use the already-pinned tiny-aes-c source in this payload. */
#include <stdint.h>
#include <stddef.h>
#include "aes.h"
#include "crys_aesccm.h"
#include "crys_aesccm_error.h"

static void ccm_block(struct AES_ctx *aes, uint8_t mac[16], const uint8_t block[16])
{
    for (unsigned i = 0; i < 16; ++i) mac[i] ^= block[i];
    AES_ECB_encrypt(aes, mac);
}

static void ccm_bytes(struct AES_ctx *aes, uint8_t mac[16],
                      const uint8_t *data, uint32_t size, const uint8_t *prefix,
                      unsigned prefix_size)
{
    uint8_t block[16] = {0};
    unsigned used = 0;
    for (unsigned i = 0; i < prefix_size; ++i) {
        block[used++] = prefix[i];
        if (used == 16) { ccm_block(aes, mac, block); used = 0; }
    }
    for (uint32_t i = 0; i < size; ++i) {
        block[used++] = data[i];
        if (used == 16) { ccm_block(aes, mac, block); used = 0; }
    }
    if (used) {
        for (unsigned i = used; i < 16; ++i) block[i] = 0;
        ccm_block(aes, mac, block);
    }
}

static void ccm_counter(struct AES_ctx *aes, const uint8_t *nonce,
                        uint8_t nonce_size, uint32_t count, uint8_t out[16])
{
    unsigned len_size = 15u - nonce_size;
    out[0] = (uint8_t)(len_size - 1u);
    for (unsigned i = 0; i < nonce_size; ++i) out[i + 1] = nonce[i];
    for (unsigned i = 0; i < len_size; ++i) {
        out[15u - i] = (uint8_t)count;
        count >>= 8;
    }
    AES_ECB_encrypt(aes, out);
}

static void ccm_erase(void *address, size_t size)
{
    volatile uint8_t *bytes = address;
    while (size--) *bytes++ = 0;
}

CRYSError_t CC_AESCCM(SaSiAesEncryptMode_t direction, CRYS_AESCCM_Key_t key,
                     CRYS_AESCCM_KeySize_t key_size, uint8_t *nonce,
                     uint8_t nonce_size, uint8_t *aad, uint32_t aad_size,
                     uint8_t *input, uint32_t text_size, uint8_t *output,
                     uint8_t tag_size, CRYS_AESCCM_Mac_Res_t tag,
                     uint32_t mode)
{
    if (mode != CRYS_AESCCM_MODE_CCM) return CRYS_AESCCM_IS_NOT_SUPPORTED;
    if (key_size != CRYS_AES_Key128BitSize) return CRYS_AESCCM_ILLEGAL_KEY_SIZE_ERROR;
    if (!key) return CRYS_AESCCM_INVALID_KEY_POINTER_ERROR;
    if (direction != SASI_AES_ENCRYPT && direction != SASI_AES_DECRYPT)
        return CRYS_AESCCM_INVALID_ENCRYPT_MODE_ERROR;
    if (!nonce || nonce_size < 7 || nonce_size > 13)
        return CRYS_AESCCM_ILLEGAL_NONCE_SIZE_ERROR;
    if (tag_size < 4 || tag_size > 16 || (tag_size & 1u) || !tag)
        return CRYS_AESCCM_ILLEGAL_TAG_SIZE_ERROR;
    if ((aad_size && !aad) || (text_size && (!input || !output)))
        return CRYS_AESCCM_ILLEGAL_PARAMETER_ERROR;
    unsigned len_size = 15u - nonce_size;
    if (len_size < 4 && text_size >= (1u << (len_size * 8u)))
        return CRYS_AESCCM_ILLEGAL_PARAMETER_ERROR;

    struct AES_ctx aes;
    AES_init_ctx(&aes, key);
    uint8_t mac[16] = {0};
    uint8_t block[16] = {0};
    block[0] = (uint8_t)((aad_size ? 0x40u : 0u) |
                         (((tag_size - 2u) / 2u) << 3u) | (len_size - 1u));
    for (unsigned i = 0; i < nonce_size; ++i) block[i + 1] = nonce[i];
    uint32_t length = text_size;
    for (unsigned i = 0; i < len_size; ++i) {
        block[15u - i] = (uint8_t)length;
        length >>= 8;
    }
    ccm_block(&aes, mac, block);
    if (aad_size) {
        uint8_t prefix[6];
        unsigned prefix_size;
        if (aad_size < 0xff00u) {
            prefix[0] = (uint8_t)(aad_size >> 8);
            prefix[1] = (uint8_t)aad_size;
            prefix_size = 2;
        } else {
            prefix[0] = 0xff; prefix[1] = 0xfe;
            for (unsigned i = 0; i < 4; ++i)
                prefix[5u - i] = (uint8_t)(aad_size >> (i * 8u));
            prefix_size = 6;
        }
        ccm_bytes(&aes, mac, aad, aad_size, prefix, prefix_size);
    }
    if (direction == SASI_AES_DECRYPT) {
        for (uint32_t offset = 0, counter = 1; offset < text_size; ++counter) {
            uint8_t stream[16];
            ccm_counter(&aes, nonce, nonce_size, counter, stream);
            for (unsigned i = 0; i < 16 && offset < text_size; ++i, ++offset)
                output[offset] = input[offset] ^ stream[i];
        }
        ccm_bytes(&aes, mac, output, text_size, NULL, 0);
    } else {
        ccm_bytes(&aes, mac, input, text_size, NULL, 0);
    }
    uint8_t stream0[16];
    ccm_counter(&aes, nonce, nonce_size, 0, stream0);
    CRYSError_t result = CRYS_OK;
    if (direction == SASI_AES_ENCRYPT) {
        for (unsigned i = 0; i < tag_size; ++i) tag[i] = mac[i] ^ stream0[i];
        for (uint32_t offset = 0, counter = 1; offset < text_size; ++counter) {
            uint8_t stream[16];
            ccm_counter(&aes, nonce, nonce_size, counter, stream);
            for (unsigned i = 0; i < 16 && offset < text_size; ++i, ++offset)
                output[offset] = input[offset] ^ stream[i];
        }
    } else {
        uint8_t mismatch = 0;
        for (unsigned i = 0; i < tag_size; ++i)
            mismatch |= (uint8_t)(tag[i] ^ mac[i] ^ stream0[i]);
        if (mismatch) {
            for (uint32_t i = 0; i < text_size; ++i) output[i] = 0;
            result = CRYS_AESCCM_CCM_MAC_INVALID_ERROR;
        }
    }
    ccm_erase(&aes, sizeof aes);
    ccm_erase(mac, sizeof mac);
    ccm_erase(block, sizeof block);
    ccm_erase(stream0, sizeof stream0);
    return result;
}
