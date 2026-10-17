/* Cordio DmConnCheckIdle; stock Main 0x4b73a2. */
#include <stdint.h>
extern uint8_t audio_dm_connection_records[];
extern void WsfTaskLock(void);
extern void WsfTaskUnlock(void);
uint16_t audio_ble_dm_conn_check_idle_4b73a2(uint8_t connection)
{
    WsfTaskLock();
    const uint8_t *slot = (const uint8_t *)(uintptr_t)
        ((uintptr_t)audio_dm_connection_records + (uint32_t)connection * 0x30u - 0x22u);
    const uint16_t mask = (uint16_t)slot[0] | ((uint16_t)slot[1] << 8);
    WsfTaskUnlock();
    return mask;
}
