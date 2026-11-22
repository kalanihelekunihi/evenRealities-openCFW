/* Software AES-128 block provider for a C-built Nordic service layer.
 * The stock-compatible build continues to call the S140 SVC gateway. */
#include "nrf_soc.h"
#include "nrf_error.h"
#include "aes.h"
#include <string.h>

#if defined(SVCALL_AS_NORMAL_FUNCTION)
_Static_assert(sizeof(soc_ecb_key_t) == AES_KEYLEN, "ECB key length");
_Static_assert(sizeof(soc_ecb_cleartext_t) == AES_BLOCKLEN, "ECB input length");
_Static_assert(sizeof(soc_ecb_ciphertext_t) == AES_BLOCKLEN, "ECB output length");

uint32_t sd_ecb_block_encrypt(nrf_ecb_hal_data_t *data)
{
    struct AES_ctx context;
    AES_init_ctx(&context, data->key);
    memcpy(data->ciphertext, data->cleartext, AES_BLOCKLEN);
    AES_ECB_encrypt(&context, data->ciphertext);
    volatile uint8_t *round_keys = (volatile uint8_t *)&context;
    for (size_t i = 0; i < sizeof(context); ++i) round_keys[i] = 0;
    return NRF_SUCCESS;
}
#endif
