/* Native DmConnInUse 0x4b6ec6, pinned Cordio dm_conn.c. */
#include <stdint.h>
extern uint8_t audio_dm_connection_records[]; /* native dmConnCb RAM */
uint8_t DmConnInUse(uint8_t connection) {
    uintptr_t address=(uintptr_t)audio_dm_connection_records
        +(uint32_t)connection*0x30u-0x1au;
    return *(const uint8_t *)address;
}
