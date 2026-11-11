/* Reconstructed from locked R1 2.2.6.0009: replay 0x88170 and six native
 * daily-cache writers. This is ordinary C, not original vendor source.
 * SRAM accesses retain native widths/order; mapped valid storage is required. */
#include "native_health_daily_replay.h"
#include "native_health_database.h"
#include "../board/native_battery_memory.h"
#include <stddef.h>
extern const uint8_t r1_health_sync_kind0[2],r1_health_sync_kind1[2],r1_health_sync_kind2[2],r1_health_sync_kind3[2],r1_health_sync_kind4[2],r1_health_sync_kind5[2];
extern volatile uint8_t *r1_activity_daily_cache_accessor(void);
extern volatile uint8_t *r1_hr_daily_cache_accessor(void);
extern volatile uint8_t *r1_spo2_daily_cache_accessor(void);
extern volatile uint8_t *r1_hrv_daily_cache_accessor(void);
#include "native_hourly_state.h"
extern uint32_t r1_health_storage_hour_index(uint32_t);
_Static_assert(sizeof(struct fdb_blob)==20,"native blob ABI");

volatile uint8_t *r1_stress_daily_cache_accessor(void)
{
    return r1_health_storage_stress_prefix;
}

static void copy_three(volatile uint8_t *base,uint32_t hour,
                       const volatile uint8_t *value)
{
    volatile uint8_t *to=(volatile uint8_t *)(uintptr_t)
        ((uint32_t)(uintptr_t)base+hour*3u);
    write16(to,read16(value));
    to[2]=value[2];
}

void r1_heart_rate_daily_cache_write(uint32_t hour,const volatile uint8_t *value)
{
    copy_three(r1_hr_daily_cache_accessor(),hour,value);
}
void r1_spo2_daily_cache_write(uint32_t hour,const volatile uint8_t *value)
{
    copy_three(r1_spo2_daily_cache_accessor(),hour,value);
}
void r1_temperature_daily_cache_write(uint32_t hour,const volatile uint8_t *value)
{
    copy_three(r1_temperature_daily_cache_accessor(),hour,value);
}
void r1_stress_daily_cache_write(uint32_t hour,const volatile uint8_t *value)
{
    copy_three(r1_stress_daily_cache_accessor(),hour,value);
}
void r1_activity_daily_cache_write(uint32_t hour,const volatile uint8_t *value)
{
    uint32_t address=(uint32_t)(uintptr_t)r1_activity_daily_cache_accessor()+hour*24u;
    uint32_t source=(uint32_t)(uintptr_t)value;
    volatile uint8_t *to=(volatile uint8_t *)(uintptr_t)address;
    if(address-source<24u){
        for(uint32_t i=24;i!=0;--i)to[i-1u]=value[i-1u];
    }else if(((address|source)&3u)==0){
        for(uint32_t i=0;i<24;i+=4)write32(to+i,read32(value+i));
    }else{
        for(uint32_t i=0;i<24;++i)to[i]=value[i];
    }
}
void r1_hrv_daily_cache_write(uint32_t hour,const volatile uint8_t *value)
{
    volatile uint8_t *to=(volatile uint8_t *)(uintptr_t)
        ((uint32_t)(uintptr_t)r1_hrv_daily_cache_accessor()+hour*6u);
    write32(to,read32(value));
    write16(to+4,read16(value+4));
}

struct r1_health_replay_descriptor {
    const volatile uint8_t *kind_size;
    void (*write)(uint32_t,const volatile uint8_t *);
};
static const struct r1_health_replay_descriptor replay_descriptors[6]={
    {r1_health_sync_kind0,r1_heart_rate_daily_cache_write},
    {r1_health_sync_kind1,r1_spo2_daily_cache_write},
    {r1_health_sync_kind2,r1_temperature_daily_cache_write},
    {r1_health_sync_kind3,r1_stress_daily_cache_write},
    {r1_health_sync_kind4,r1_activity_daily_cache_write},
    {r1_health_sync_kind5,r1_hrv_daily_cache_write}
};

bool r1_health_daily_record_replay(fdb_tsl_t tsl,void *argument)
{
    if(!argument)return true;
    struct fdb_blob blob;
    fdb_blob_t view=fdb_blob_make(&blob,argument,128);
    view=fdb_tsl_to_blob(tsl,view);
    if((uint16_t)fdb_blob_read((fdb_db_t)&r1_health_database_storage.database,view)!=128)
        return true;
    const volatile uint8_t *record=argument;
    uint32_t hour=r1_health_storage_hour_index(read32(record+4));
    uint32_t slot=hour?(uint8_t)(hour-1u):23u;
    uint32_t cursor=(uint32_t)(uintptr_t)argument+8u;
    for(uint32_t i=0;i<6;++i){
        const volatile struct r1_health_replay_descriptor *entry=&replay_descriptors[i];
        void (*write)(uint32_t,const volatile uint8_t *)=entry->write;
        if(write){
            write(slot,(const volatile uint8_t *)(uintptr_t)cursor);
            /* Stock reloads the size only after the callback returns. */
            cursor+=entry->kind_size[1];
        }
    }
    return false;
}
