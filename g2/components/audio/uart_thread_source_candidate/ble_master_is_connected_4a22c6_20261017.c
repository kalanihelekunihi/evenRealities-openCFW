/* Stock Main APP_MasterIsConnected, 0x4a22c6. */
#include <stdint.h>
extern uint8_t *audio_ble_master_context; /* stock pointer cell 0x200742fc */

uint32_t audio_ble_master_is_connected_4a22c6(void)
{
    return audio_ble_master_context[0x55u]!=0u ? 1u : 0u;
}
