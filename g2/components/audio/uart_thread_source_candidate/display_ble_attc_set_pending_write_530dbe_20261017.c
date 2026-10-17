/* Cordio attcSetPendWriteCmd at stock Main 0x530dbe: one pending slot. */
#include <stdint.h>

void audio_ble_attc_set_pending_write_530dbe(uint8_t *ccb)
{
    if (ccb[0x2au] == 0u && ccb[0x2bu] == 0u) {
        ccb[0x2au] = ccb[0x0cu];
        ccb[0x2bu] = ccb[0x0du];
    }
}
