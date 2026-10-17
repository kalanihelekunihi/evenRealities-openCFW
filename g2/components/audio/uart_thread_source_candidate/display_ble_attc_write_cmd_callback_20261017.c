/* Cordio attcWriteCmdCallback, stock 0x530de6..0x530e30.
 * This image uses one simultaneous pending write command slot. */
#include <stdint.h>

extern void audio_ble_attc_exec_callback_531ad6(uint8_t, uint8_t,
                                                  uint16_t, uint8_t);

void audio_ble_attc_write_cmd_callback_530de6(uint8_t connection,
                                                void *ccb_arg, uint8_t status)
{
    uint8_t *const ccb = (uint8_t *)ccb_arg;
    uint16_t *const pending = (uint16_t *)(void *)(ccb + 0x2au);
    if (*pending != 0u) {
        audio_ble_attc_exec_callback_531ad6(connection, 0x0au,
                                             *pending, status);
        *pending = 0u;
    }
}
