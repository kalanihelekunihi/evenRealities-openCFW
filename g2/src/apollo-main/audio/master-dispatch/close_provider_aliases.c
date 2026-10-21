#include <stdint.h>

extern uint32_t audio_ble_privacy_rewrite_record(uint8_t *);
extern uint8_t audio_ble_pair_record_validate(uint8_t *);

/* The close chain's native 0x479b74 call uses the same AppDb NVM provider. */
void audio_ble_master_close_child_479b74(uint32_t address)
{
    (void)audio_ble_privacy_rewrite_record((uint8_t *)(uintptr_t)address);
}

/* The close chain's native 0x47b730 call uses AppDbVerifyMramWrite. */
void audio_ble_master_close_child_47b730(uint32_t address)
{
    (void)audio_ble_pair_record_validate((uint8_t *)(uintptr_t)address);
}
