/* Reconstructed from locked R1 2.2.6.0009, native time transition 0x5e698.
 * Unsigned wrapped local-day arithmetic and strict threshold edges are native. */
#include "native_health_time_storage.h"
#include "native_health_database.h"
#include "native_health_daily_replay.h"
#include "native_health_hour_storage.h"
#include "time_calendar/time_calendar.h"
#include <stddef.h>
#include <string.h>
_Static_assert(sizeof(struct r1_health_time_transition)==12 && offsetof(struct r1_health_time_transition,new_timestamp)==8,"native transition ABI");
extern uint32_t r1_health_record_read(void *),r1_health_record_write(const void *);
extern uint32_t r1_time_local_day_start(void);
extern int32_t r1_time_utc_offset_get(void);
extern uint32_t r1_activity_daily_cache_reset(uint32_t,uint32_t),r1_heart_rate_daily_cache_reset(uint32_t,uint32_t),r1_spo2_daily_cache_reset(uint32_t,uint32_t),r1_hrv_daily_cache_reset(uint32_t,uint32_t);
extern void r1_health_sync_provider_00063ad8(fdb_tsdb_t,fdb_time_t,fdb_time_t,fdb_tsl_cb,void *);
extern void *pvPortMalloc(size_t);
extern void vPortFree(void *);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *),nrf_log_frontend_std_1(uint32_t,const char *,uint32_t),nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
static uint32_t ring_enabled(void){return (r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u);}
static void log_zero(uint32_t level,uint32_t metadata,const char *ring,const char *sdk)
{
    if(ring_enabled())(void)r1_structured_log_format(level,ring,ring);
    if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(metadata,sdk);
}
static uint32_t (*const resetters[6])(uint32_t,uint32_t)={r1_heart_rate_daily_cache_reset,r1_spo2_daily_cache_reset,r1_temperature_daily_cache_reset,r1_stress_daily_cache_reset,r1_activity_daily_cache_reset,r1_hrv_daily_cache_reset};
void r1_health_time_transition_storage_orchestrator(const volatile struct r1_health_time_transition *change)
{
    if(!change)return;
    uint32_t old_timestamp=change->old_timestamp,new_timestamp=change->new_timestamp;
    if(new_timestamp<old_timestamp && old_timestamp-new_timestamp>=3600u){
        log_zero(0x0c000000,0x001c0003,"[RING]flashdb ts change, reinit flashdb","flashdb ts change, reinit flashdb");
        fdb_tsl_clean(&r1_health_database_storage.database);
        uint32_t record[6]={0};
        (void)r1_health_record_read(record);
        record[0]=0;record[1]=0;record[3]=0;record[4]=0;
        (void)r1_health_record_write(record);
        log_zero(0x08000000,0x001c0002,"[RING]update_time: tsdb wiped, reset 4 sync ts","update_time: tsdb wiped, reset 4 sync ts");
    }
    if(old_timestamp<UINT32_C(0x38640900)){
        if(new_timestamp>=UINT32_C(0x38640900)){
            int32_t offset=change->new_offset;
            time_calendar_datetime calendar={0};
            (void)time_calendar_utc_to_calendar((int32_t)new_timestamp,offset,&calendar);
            calendar.hour=0;calendar.minute=0;calendar.second=0;
            uint32_t midnight=(uint32_t)time_calendar_to_utc(&calendar,offset);
            if(ring_enabled())(void)r1_structured_log_format(0x0c800000,"[RING]db_storage time sync from 1970, recover data, zero_time:%d, new_ts:%d","[RING]db_storage time sync from 1970, recover data, zero_time:%d, new_ts:%d",midnight,new_timestamp);
            if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_2(0x001c0003,"db_storage time sync from 1970, recover data, zero_time:%d, new_ts:%d",midnight,new_timestamp);
            void *buffer=pvPortMalloc(128);
            if(!buffer){log_zero(0x0c000000,0x001c0003,"[RING]db_storage recover malloc failed","db_storage recover malloc failed");return;}
            memset(buffer,0,128);
            r1_health_sync_provider_00063ad8(&r1_health_database_storage.database,(fdb_time_t)midnight,(fdb_time_t)new_timestamp,r1_health_daily_record_replay,buffer);
            vPortFree(buffer);
        }else{
            if(ring_enabled())(void)r1_structured_log_format(0x0c400000,"[RING]skip cross day check, old_ts invalid: %d","[RING]skip cross day check, old_ts invalid: %d",old_timestamp);
            if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(0x001c0003,"skip cross day check, old_ts invalid: %d",old_timestamp);
        }
        return;
    }
    /* Inputs reload here after wipe/read/write/log providers, as in stock. */
    uint32_t new_local=change->new_timestamp+(uint32_t)((int32_t)change->new_offset*60);
    uint32_t old_local=change->old_timestamp+(uint32_t)((int32_t)change->old_offset*60);
    if(new_local/86400u!=old_local/86400u){
        uint32_t midnight=r1_time_local_day_start();uint32_t offset=(uint16_t)r1_time_utc_offset_get();
        if(ring_enabled())(void)r1_structured_log_format(0x0c800000,"[RING]db_storage cross day, clean all data, zero_ts:%d,%d","[RING]db_storage cross day, clean all data, zero_ts:%d,%d",midnight,offset);
        if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_2(0x001c0003,"db_storage cross day, clean all data, zero_ts:%d,%d",midnight,offset);
        for(uint32_t i=0;i<6;++i){uint32_t (*reset)(uint32_t,uint32_t)=((uint32_t (*const volatile *)(uint32_t,uint32_t))resetters)[i];if(reset)(void)reset(midnight,offset);}
    }
    if(new_timestamp<=UINT32_C(0x38640900))return;
    uint32_t record[6]={0};
    (void)r1_health_record_read(record);
    uint32_t dirty=0;
    const uint8_t indices[4]={0,1,3,4};
    for(uint32_t i=0;i<4;++i){uint32_t index=indices[i];if(record[index]>new_timestamp){record[index]=new_timestamp;dirty=1;}}
    if(!dirty)return;
    (void)r1_health_record_write(record);
    if(ring_enabled())(void)r1_structured_log_format(0x08400000,"[RING]update_time: clamp future sync ts to %u","[RING]update_time: clamp future sync ts to %u",new_timestamp);
    if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(0x001c0002,"update_time: clamp future sync ts to %u",new_timestamp);
}
