#include <stdint.h>
#include <string.h>
#include "native_battery_memory.h"
#include "../../source/include/r1_stock_checksums.h"
extern volatile uint16_t r1_protocol_sequence;
extern volatile uint8_t r1_protocol_version_map[4];
uint32_t r1_model_encode(void *destination,uint32_t capacity,uint32_t version,uint32_t operation_high,uint32_t operation_low,uint32_t flags,uint32_t explicit_sequence,const void *payload,uint32_t length)
{
    volatile uint8_t *d=destination;
    if (!d || !capacity || version>=4u) return 2;
    /* Native subtracts in32 bits, including underflow when capacity<12. */
    if (length>capacity-12u) return 1;
    write32(d,0);write32(d+4,0);write32(d+8,0);
    d[0]=100;d[1]=(uint8_t)version;d[2]=r1_protocol_version_map[version];
    uint32_t sequence=r1_protocol_sequence;
    uint32_t total=length+12u;
    write16(d+3,(flags&1u) ? explicit_sequence:sequence);
    d[5]=(uint8_t)flags;d[6]=(uint8_t)operation_high;d[7]=(uint8_t)operation_low;
    write16(d+8,total);
    if (!(flags&1u)) r1_protocol_sequence=(uint16_t)(sequence+1u);
    if (payload && length) (void)memmove((void *)(d+12),payload,length);
    uint16_t crc=r1_stock_crc16_modbus((const uint8_t *)d,(uint16_t)total);
    write16(d+10,crc);return 0;
}
