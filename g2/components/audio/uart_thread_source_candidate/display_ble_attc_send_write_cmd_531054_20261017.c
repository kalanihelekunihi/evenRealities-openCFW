/* Cordio attcSendWriteCmd at stock Main 0x531054. */
#include <stdint.h>

extern void audio_ble_attc_send_simple_530e30(uint8_t *);
extern void audio_ble_attc_exec_callback_531ad6(uint8_t, uint8_t, uint16_t, uint8_t);
extern void audio_ble_attc_set_pending_write_530dbe(uint8_t *);

void audio_ble_attc_send_write_cmd_531054(uint8_t *ccb)
{
    audio_ble_attc_send_simple_530e30(ccb);
    uint8_t *main_ccb = *(uint8_t **)ccb;
    if ((main_ccb[(uint32_t)ccb[0x0eu] * 4u + 2u] & 2u) == 0u) {
        const uint16_t handle =
            (uint16_t)ccb[0x0cu] | ((uint16_t)ccb[0x0du] << 8);
        audio_ble_attc_exec_callback_531ad6(main_ccb[0x0eu], 10u, handle, 0u);
    } else {
        audio_ble_attc_set_pending_write_530dbe(ccb);
    }
    ccb[6u] = 0u;
}
