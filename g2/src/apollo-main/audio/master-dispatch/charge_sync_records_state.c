/* Storage touched by the selected native CHG_InitBatterySync C reduction. */
#include <stdint.h>

void *audio_charge_sync_mutex;
/* audio_charge_sync_record: stock 0x20073b30 is one cell; defined as an alias of
 * audio_charger_state in charger_state_minimum.c (Fix 33). */
uint8_t audio_charge_sync_peer_record[8u];
