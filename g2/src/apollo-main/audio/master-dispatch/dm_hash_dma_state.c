/* Source-owned live RAM used by the selected DM hash path. */
#include <stdint.h>

/* The native copy path writes sixteen bytes from the database hash pointer. */
uint8_t audio_ble_dm_database_hash_20068215[16];

/* RAM 0x2006ef28 (12 x 0x2c CMDQ state rows) is gAmHalCmdq, defined by
 * AmbiqSuite 5.1.0 hal/mcu/am_hal_cmdq.c. */
