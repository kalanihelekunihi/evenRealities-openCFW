/* Locked R1 registry: reuse the reset/resolver table, mutex and sequence owners. */
#include "native_ack_registry.h"
#include "../board/native_battery_memory.h"
extern volatile uint16_t r1_protocol_sequence;
extern uint32_t r1_ack_table_lock(void),r1_ack_table_unlock(void),osKernelGetTickCount(void);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *),nrf_log_frontend_std_4(uint32_t,const char *,uint32_t,uint32_t,uint32_t,uint32_t),nrf_log_frontend_std_5(uint32_t,const char *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern void vPortFree(void *);
static uint32_t ring_enabled(void){return (r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u);}
uint32_t r1_ack_record_insert(uint32_t first,uint32_t second,uint32_t third,uint32_t sequence,uint32_t callback,uint32_t argument)
{
    for(uint32_t i=0;i<32;i++){
        volatile uint8_t *record=r1_protocol_reset_workspace+20*i;
        if(record[0])continue;
        record[0]=1;record[1]=(uint8_t)first;record[2]=(uint8_t)second;record[3]=(uint8_t)third;
        write16(record+4,sequence);write32(record+8,callback);write32(record+12,argument);
        write32(record+16,osKernelGetTickCount());return 1;
    }
    return 0;
}
uint32_t r1_ack_record_remove(uint32_t first,uint32_t second,uint32_t third,uint32_t sequence)
{
    (void)r1_ack_table_lock();
    for(uint32_t i=0;i<32;i++){
        volatile uint8_t *record=r1_protocol_reset_workspace+20*i;
        if(!record[0] || record[1]!=first || record[2]!=second || record[3]!=third || read16(record+4)!=sequence)continue;
        record[0]=0;write32(record+8,0);write32(record+12,0);
        const char *ring="[RING]ack removed: module=%d cmd=%d sub=%d seq=%d";
        if(ring_enabled())(void)r1_structured_log_format(0x0d000000,ring,ring,first,second,third,sequence);
        if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_4(0x001c0003,"ack removed: module=%d cmd=%d sub=%d seq=%d",first,second,third,sequence);
        break;
    }
    return r1_ack_table_unlock();
}
uint32_t r1_ack_timeout_reaper(void)
{
    uint32_t now=osKernelGetTickCount();
    (void)r1_ack_table_lock();
    for(uint32_t i=0;i<32;i++){
        volatile uint8_t *record=r1_protocol_reset_workspace+20*i;
        if(!record[0] || now-read32(record+16)<10000u)continue;
        const char *ring="[RING]ack timeout: module=%d cmd=%d sub=%d seq=%d, free param=%p";
        if(ring_enabled())(void)r1_structured_log_format(0x09400000,ring,ring,record[1],record[2],record[3],read16(record+4),read32(record+12));
        if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_5(0x001c0002,"ack timeout: module=%d cmd=%d sub=%d seq=%d, free param=%p",record[1],record[2],record[3],read16(record+4),read32(record+12));
        uint32_t argument=read32(record+12);
        if(argument)vPortFree((void *)(uintptr_t)argument);
        record[0]=0;write32(record+8,0);write32(record+12,0);
    }
    return r1_ack_table_unlock();
}
uint32_t r1_ack_record_register(const volatile uint8_t *header,uint32_t callback,volatile uint8_t *argument,volatile uint16_t *identifier)
{
    if(!header || !callback)return 0;
    uint32_t sequence=(header[0]&1u)?read16(header+4):r1_protocol_sequence;
    (void)r1_ack_table_lock();
    uint32_t result=r1_ack_record_insert(header[1],header[2],header[3],sequence,callback,(uint32_t)(uintptr_t)argument);
    (void)r1_ack_table_unlock();
    if(!result){
        (void)r1_ack_timeout_reaper();
        (void)r1_ack_table_lock();
        result=r1_ack_record_insert(header[1],header[2],header[3],sequence,callback,(uint32_t)(uintptr_t)argument);
        (void)r1_ack_table_unlock();
    }
    if(result){if(identifier)write16((volatile uint8_t *)identifier,sequence);return 1;}
    const char *ring="[RING]ack table full, callback dropped";
    if(ring_enabled())(void)r1_structured_log_format(0x04000000,ring,ring);
    if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(0x001c0001,"ack table full, callback dropped");
    return 0;
}
