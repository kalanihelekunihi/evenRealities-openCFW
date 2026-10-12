/* Native DmSecGetLocalCsrk 0x4d251e reads state slot 0x20074118. */
#include <stdint.h>
extern const void *audio_ble_dm_security_state[2]; /* native 0x20074114 */
const uint8_t *DmSecGetLocalCsrk(void)
{
    return (const uint8_t *)audio_ble_dm_security_state[1];
}
