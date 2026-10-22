/* Native Cordio DmConnRegister 0x4b6c64 and SmpDbInit 0x542288. */
#include <stdint.h>
extern uint8_t audio_ble_dm_connection_registry[]; /* live RAM 0x200712a4; full extent unproven */
uint8_t audio_ble_smp_database[0x100u]; /* RAM 0x200708ec */
extern uint8_t audio_ble_smp_handler_state[]; /* RAM 0x20070aec */
extern void WsfTaskLock(void);
extern void WsfTaskUnlock(void);
extern void WsfTimerStop(void *); /* native 0x52a4d2 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* selected 0x43c0e4 */

/* Native SmpDbInit 0x542288. */
void SmpDbInit(void) {
    if(audio_ble_smp_database[0xfdu]==1u)
        WsfTimerStop(audio_ble_smp_database+0xf0u);
    audio_uart_buffer_zero(audio_ble_smp_database,0x100u,0u);
    audio_ble_smp_database[0xfcu]=audio_ble_smp_handler_state[0xecu];
    audio_ble_smp_database[0xfau]=0x20u;
}
