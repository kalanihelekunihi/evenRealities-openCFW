/* Native smpDbStartServiceTimer 0x541e34; pinned Cordio smp_db.c. */
#include <stdint.h>
extern uint8_t audio_ble_smp_database[]; /* native 0x200708ec */
extern void WsfTimerStartMs(void *timer,uint32_t milliseconds);
void smpDbStartServiceTimer(void)
{
    if (audio_ble_smp_database[0xfdu]==0u)
        WsfTimerStartMs(audio_ble_smp_database+0xf0u,1000u);
}
