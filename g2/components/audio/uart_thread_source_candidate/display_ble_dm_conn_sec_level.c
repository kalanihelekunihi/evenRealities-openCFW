/* Native DmConnSecLevel 0x4b71b2; dmConnCb.ccb rows are 0x30 bytes each. */
#include <stdint.h>
extern uint8_t audio_dm_connection_records[]; /* live RAM 0x200712a4 */
uint8_t DmConnSecLevel(uint8_t connection) {
    uintptr_t address=(uintptr_t)audio_dm_connection_records
        +(uint32_t)connection*0x30u-0x19u;
    return *(const uint8_t *)address;
}
