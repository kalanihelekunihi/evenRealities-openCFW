/* Native dmConnCcbById 0x4b62a8, pinned Cordio dm_conn.c. */
#include <stdint.h>
extern uint8_t audio_dm_connection_records[]; /* native 0x200712a4 */
uint8_t *dmConnCcbById(uint8_t connection)
{
    uint32_t index=(uint8_t)(connection-1u);
    uint8_t *record=audio_dm_connection_records+index*0x30u;
    return record[0x16u]==0u?0:record;
}
