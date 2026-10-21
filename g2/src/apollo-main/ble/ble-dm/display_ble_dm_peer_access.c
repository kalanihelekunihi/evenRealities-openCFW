/* Native DM peer record accessors 0x4b6ed8 and 0x4b6eea. */
#include <stdint.h>
extern uint8_t audio_dm_connection_records[]; /* live 0x200712a4 */
uint8_t DmConnPeerAddrType(uint8_t conn) {
    uintptr_t address=(uintptr_t)audio_dm_connection_records+(uint32_t)conn*48u-0x1du;
    return *(const volatile uint8_t *)address;
}
const uint8_t *DmConnPeerAddr(uint8_t conn) {
    uintptr_t address=(uintptr_t)audio_dm_connection_records+(uint32_t)conn*48u-48u;
    return (const uint8_t *)address;
}
