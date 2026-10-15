/* Relink-only replacement for the inlined pre-correction Apollo Main body.
 * The authoritative source remains display_ble_stack_lowers.c. */
#include <stdint.h>

extern uint8_t audio_ble_dm_config[];
extern uint8_t audio_ble_dm_privacy_state[];
extern uint8_t audio_ble_dm_stack_rows_200738dc[];
extern const uint8_t audio_ble_dm_stack_table_78a88c[];
extern void WsfTaskLock(void);
extern void WsfTaskUnlock(void);

void audio_ble_dm_stack_state_init(void)
{
    uint8_t *rows=audio_ble_dm_stack_rows_200738dc;
    for(uint32_t i=0;i<2u;i++) {
        *(uint16_t *)(void *)(rows+0x10u+2u*i)=0x60u;
        *(uint16_t *)(void *)(rows+0x14u+2u*i)=0x30u;
    }
    audio_ble_dm_privacy_state[0x13u]=0u;
    rows[0x0cu]=audio_ble_dm_privacy_state[0x0cu];
    rows[0x18u]=0u;
    audio_ble_dm_privacy_state[0x0fu]=0u;
}

void audio_ble_stack_lower_5369ea(void)
{
    WsfTaskLock();
    *(const void **)(void *)(audio_ble_dm_config+8u)=audio_ble_dm_stack_table_78a88c;
    audio_ble_dm_stack_state_init();
    WsfTaskUnlock();
}
