/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern int printf(const char *,...);
const char open_cfw_gx8002_mic_invalid[] __attribute__((aligned(1)))="ERR: invalid param for gx_audio_get_mic_buffer\n";
const char open_cfw_gx8002_mic_large[] __attribute__((aligned(1)))="ERR: buf_len_per_ctx too large for mic buffer\n";
/* Header word offsets recovered from stock; multiplication wraps at32 bits.
 * Zero divisors are not silently repaired; target behavior needs qualification. */
int open_cfw_gx8002_mic_buffer(const uint32_t *header,uint32_t microphone,uint32_t context_index,uint32_t *address,uint32_t *length)
{
    if (!header || !address || !length || microphone>=header[2]) {
        printf(open_cfw_gx8002_mic_invalid);
        return -1;
    }
    uint32_t bytes=(header[7]*header[9]*2u*header[8])/1000u;
    uint32_t per_mic=header[21]/header[2];
    uint32_t slots=per_mic/bytes;
    if (!slots) { printf(open_cfw_gx8002_mic_large); return -1; }
    *address=header[20]+microphone*per_mic+(context_index%slots)*bytes;
    *length=bytes;
    return 0;
}
