/* Native Cordio SmpDmEncryptInd at Apollo Main 0x537be6. */
#include <stdint.h>
extern void audio_ble_smp_handler_537d0c(uint32_t, uint8_t *);

void audio_ble_smp_encrypt_ind_537be6(void *event_ptr)
{
    uint8_t *const event = (uint8_t *)event_ptr;
    event[2u] = event[3u] == 0u ? 8u : 9u;
    audio_ble_smp_handler_537d0c(0u, event);
}
