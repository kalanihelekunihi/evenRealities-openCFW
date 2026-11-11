/* Stock 0x58914, 0x58980, 0x58a24, 0x5a28c: retained crash recovery. */
#include "native_crash_recovery.h"
#include "../../include/r1_stock_checksums.h"
#include <stddef.h>
extern volatile uint32_t r1_reset_trace_context[6];
extern void __aeabi_memclr(void *,size_t);
static uint32_t word(uint32_t at) { return *(volatile uint32_t *)(uintptr_t)at; }
static uint16_t half(uint32_t at) { return *(volatile uint16_t *)(uintptr_t)at; }
uint32_t r1_health_crash_provider_blob_clear(void) {
    uint32_t base=r1_reset_trace_context[2];
    __aeabi_memclr((void *)(uintptr_t)(base+12u),900);
    uint32_t crc=r1_stock_crc16_modbus((const uint8_t *)(uintptr_t)base,964);
    *(volatile uint16_t *)(uintptr_t)(base+964u)=(uint16_t)crc;
    return crc;
}
uint32_t r1_health_crash_record_validator(void) {
    uint32_t base=r1_reset_trace_context[2];
    if (word(base)!=UINT32_C(0x5a5a5a5a)) return 0;
    uint32_t crc=r1_stock_crc16_modbus((const uint8_t *)(uintptr_t)base,964);
    return half(base+964u)==crc;
}
uint32_t r1_health_crash_provider_blob_accessor(volatile uint16_t *length) {
    if (!length || !r1_health_crash_record_validator()) return 0;
    uint32_t base=r1_reset_trace_context[2];
    if (word(base+908u)!=UINT32_C(0x5a5a5a5a)) return 0;
    *length=896;
    return base+12u;
}
uint32_t r1_health_crash_record_magic_probe(void) {
    uint32_t marker=r1_reset_trace_context[1];
    r1_reset_trace_context[4]=marker;
    return word(marker)==UINT32_C(0x5a5a5a5a);
}
/* Stock 0x58960: clear time metadata, then refresh the same retained CRC. */
uint32_t r1_health_crash_time_clear(void) {
    uint32_t base=r1_reset_trace_context[2];
    *(volatile uint32_t *)(uintptr_t)(base+4u)=0;
    *(volatile uint32_t *)(uintptr_t)(base+8u)=0;
    uint32_t crc=r1_stock_crc16_modbus((const uint8_t *)(uintptr_t)base,964);
    *(volatile uint16_t *)(uintptr_t)(base+964u)=(uint16_t)crc;
    return crc;
}
/* Stock 0x589e8: outputs are ordered and can alias retained/context storage. */
uint32_t r1_health_crash_time_accessor(volatile uint32_t *timestamp,
                                     volatile uint16_t *offset,
                                     volatile uint8_t *pending) {
    if (!timestamp || !offset || !pending) return 0;
    if (!r1_health_crash_record_validator()) return 0;
    uint32_t base=r1_reset_trace_context[2];
    uint32_t value=word(base+8u);
    if (!value) return 0;
    *timestamp=value;
    *offset=half(base+6u);
    *pending=*(volatile uint8_t *)(uintptr_t)(base+4u)&1u;
    return 1;
}

/* Stock 0x5893c: clear only the 52-byte snapshot and refresh retained CRC. */
uint32_t r1_health_crash_snapshot_clear(void) {
    uint32_t base=r1_reset_trace_context[2];
    for(uint32_t i=0;i<52;++i)*(volatile uint8_t *)(uintptr_t)(base+912u+i)=0;
    uint32_t crc=r1_stock_crc16_modbus((const uint8_t *)(uintptr_t)base,964);
    *(volatile uint16_t *)(uintptr_t)(base+964u)=(uint16_t)crc;
    return crc;
}
/* Stock 0x589b0: native overlap-aware SRAM copy, not C memcpy alias UB. */
uint32_t r1_health_crash_snapshot_accessor(volatile uint8_t *output) {
    if(!output || !r1_health_crash_record_validator())return 0;
    uint32_t base=r1_reset_trace_context[2];
    if(!*(volatile uint8_t *)(uintptr_t)(base+957u) ||
       *(volatile uint8_t *)(uintptr_t)(base+956u)>=24u)return 0;
    uint32_t source=base+912u,destination=(uint32_t)(uintptr_t)output;
    const volatile uint8_t *from=(const volatile uint8_t *)(uintptr_t)source;
    if(destination-source<52u){
        for(uint32_t i=52;i!=0;--i)output[i-1u]=from[i-1u];
    }else if(((source|destination)&3u)==0){
        for(uint32_t i=0;i<52;i+=4)
            *(volatile uint32_t *)(uintptr_t)(destination+i)=word(source+i);
    }else{
        for(uint32_t i=0;i<52;++i)output[i]=from[i];
    }
    return 1;
}
