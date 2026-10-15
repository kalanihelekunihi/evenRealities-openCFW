#include <stdint.h>

/* Native ROM 0x7856b0..0x7856bf. At 0x7856c0 the distinct
 * "callback.mgr" string begins. DmSecInit installs this table in RAM. */
const uint8_t audio_ble_dm_security_state_table[16] = {0};
