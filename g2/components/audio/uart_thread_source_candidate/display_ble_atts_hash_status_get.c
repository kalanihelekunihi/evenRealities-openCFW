/* Native attsCsfGetHashUpdateStatus 0x52c914; pinned Cordio atts_csf.c. */
#include <stdint.h>
extern uint8_t audio_ble_connection_state_table[]; /* live CSF state 0x20073e04 */
uint8_t attsCsfGetHashUpdateStatus(void)
{
    return audio_ble_connection_state_table[0x0cu];
}
