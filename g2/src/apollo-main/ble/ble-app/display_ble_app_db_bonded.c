/* Pinned Cordio app_db.c AppDbCheckBonded, native Main 0x47a600. */
#include <stdint.h>
extern uint8_t audio_ble_privacy_rows[10u*200u]; /* native RAM 0x20067a30 */
uint8_t AppDbCheckBonded(void)
{
    for (uint8_t i=0u;i<10u;i++) {
        const uint8_t *row=audio_ble_privacy_rows+(uint32_t)i*200u;
        if (row[0x2fu] && !row[0xc3u]) return 1u;
    }
    return 0u;
}
