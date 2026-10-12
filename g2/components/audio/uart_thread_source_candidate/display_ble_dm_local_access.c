/* Native DmConnLocalAddr/LocalAddrType 0x4b6f0c/0x4b6efa. */
#include <stdint.h>
extern uint8_t audio_dm_connection_records[]; /* native dmConnCb 0x200712a4 */
uint8_t *DmConnLocalAddr(uint8_t connection)
{
    uintptr_t address=(uintptr_t)audio_dm_connection_records
        +(uint32_t)connection*0x30u-0x2au;
    return (uint8_t *)address;
}
uint8_t DmConnLocalAddrType(uint8_t connection)
{
    uintptr_t address=(uintptr_t)audio_dm_connection_records
        +(uint32_t)connection*0x30u-0x1cu;
    return *(const volatile uint8_t *)address;
}
