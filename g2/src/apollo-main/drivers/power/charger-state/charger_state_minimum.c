/* Minimum observed live charger state at 0x20073b30.
 * Native getters read the SOC word at +0x10 and signed charging byte +0x14.
 * The complete product allocation and startup state remain unknown. */
#include <stdint.h>

/* Fix 33: 0x18 bytes, since stock CHG_InitBatterySync clears 24 bytes here
 * (movs r1,#24 / ldr r4,=0x20073b30 / bl 0x43c0e4 at 0x4ad016-0x4ad022). */
uint8_t audio_charger_state[0x18]
    __attribute__((section(".g2_ram_20073b30")));
/* Stock 0x20073b30 is a single cell: one literal-pool word 0x4ad908 is loaded by
 * CHG_InitBatterySync 0x4ad01a, CHG_CompareAndUpdateSoc 0x4ad1ca, CHG_GetSoc 0x4ad8fa and
 * CHG_GetIsCharging 0x4ad900. Alias the sync record onto it (Fix 33). */
extern uint8_t audio_charge_sync_record[24u] __attribute__((alias("audio_charger_state")));
