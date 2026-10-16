/* Cordio DmConnNum 0x4b62ca: three 0x30-byte CCB slots, live flag +0x16. */
#include <stdint.h>

extern uint8_t audio_dm_connection_records[]; /* RAM 0x200712a4 */

uint32_t audio_ble_dm_conn_num_4b62ca(void)
{
    uint32_t count = 0u;
    for (uint32_t i = 0u; i < 3u; ++i)
        if (audio_dm_connection_records[i * 0x30u + 0x16u] != 0u)
            ++count;
    return count;
}
