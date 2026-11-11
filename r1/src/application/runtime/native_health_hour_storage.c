/* Reconstructed stock R1 2.2.6.0009 hourly storage 0x5dce8, six cache
 * readers and stress/temperature resets. SRAM-only access widths/order. */
#include "native_health_hour_storage.h"
#include "native_health_database.h"
#include "native_health_daily_replay.h"
#include "native_hourly_state.h"
#include "../board/native_battery_memory.h"
#include <stddef.h>
#include <string.h>
extern const uint8_t r1_health_sync_kind0[2],r1_health_sync_kind1[2],r1_health_sync_kind2[2],r1_health_sync_kind3[2],r1_health_sync_kind4[2],r1_health_sync_kind5[2];
extern volatile uint8_t *r1_activity_daily_cache_accessor(void),*r1_hr_daily_cache_accessor(void),*r1_spo2_daily_cache_accessor(void),*r1_hrv_daily_cache_accessor(void);
extern uint32_t r1_activity_daily_cache_reset(uint32_t,uint32_t),r1_heart_rate_daily_cache_reset(uint32_t,uint32_t),r1_spo2_daily_cache_reset(uint32_t,uint32_t),r1_hrv_daily_cache_reset(uint32_t,uint32_t);
extern volatile uint32_t r1_daily_stress_timestamp,r1_daily_temperature_timestamp;
extern uint32_t r1_time_status_get(void),r1_time_backend_timestamp(void),r1_time_local_day_start(void);
extern int32_t r1_time_utc_offset_get(void);
#include "native_health_offline_queue.h"
extern void *pvPortMalloc(size_t);
extern void vPortFree(void *);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t),nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
static uint32_t ring_enabled(void){return (r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u);}
static volatile uint8_t *at(volatile uint8_t *p,uint32_t n){return (volatile uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)p+n);}
static void clear(volatile uint8_t *p,uint32_t n){for(uint32_t i=0;i<n;++i)p[i]=0;}
static void copy(volatile uint8_t *to,const volatile uint8_t *from,uint32_t n)
{
    uint32_t dst=(uint32_t)(uintptr_t)to,src=(uint32_t)(uintptr_t)from;
    if(dst-src<n){for(uint32_t i=n;i;--i)to[i-1u]=from[i-1u];}
    else if(((dst|src)&3u)==0){uint32_t i=0;for(;n-i>=4;i+=4)write32(to+i,read32(from+i));for(;i<n;++i)to[i]=from[i];}
    else for(uint32_t i=0;i<n;++i)to[i]=from[i];
}
static void read_three(volatile uint8_t *base,uint32_t hour,volatile uint8_t *out)
{
    volatile uint8_t *entry=at(base,hour*3u);
    write16(out,read16(entry));out[2]=entry[2];
}
typedef void (*future_guard)(uint32_t,uint32_t,uint32_t,volatile uint8_t *,uint32_t);
static void guarded_three(volatile uint8_t *base,uint32_t hour,volatile uint8_t *out,future_guard guard)
{
    read_three(base,hour,out);
    if(r1_time_status_get())return;
    uint32_t now=r1_time_backend_timestamp();
    if(now>UINT32_C(0x38640900) || !out[0])return;
    uint32_t offset_hours=read16(base+72)/60u;
    if(hour>=offset_hours)guard(0,0,(uint8_t)(hour-offset_hours),out,now);
    write16(out,0);out[2]=0;
}
void r1_heart_rate_daily_cache_read(uint32_t hour,volatile uint8_t *out,uint32_t size)
{(void)size;guarded_three(r1_hr_daily_cache_accessor(),hour,out,r1_hr_cache_future_record_guard);}
void r1_spo2_daily_cache_read(uint32_t hour,volatile uint8_t *out,uint32_t size)
{(void)size;guarded_three(r1_spo2_daily_cache_accessor(),hour,out,r1_spo2_cache_future_record_guard);}
void r1_stress_daily_cache_read(uint32_t hour,volatile uint8_t *out,uint32_t size)
{(void)size;read_three(r1_stress_daily_cache_accessor(),hour,out);}
void r1_temperature_daily_cache_read(uint32_t hour,volatile uint8_t *out,uint32_t size)
{
    (void)size;read_three(r1_temperature_daily_cache_accessor(),hour,out);
    if(r1_time_status_get())return;
    uint32_t now=r1_time_backend_timestamp();
    if(now<=UINT32_C(0x38640900) && out[0]){write16(out,0);out[2]=0;}
}
void r1_hrv_daily_cache_read(uint32_t hour,volatile uint8_t *out,uint32_t size)
{
    (void)size;volatile uint8_t *base=r1_hrv_daily_cache_accessor();
    if(!base){write32(out,0);write16(out+4,0);return;}
    volatile uint8_t *entry=at(base,hour*6u);write32(out,read32(entry));write16(out+4,read16(entry+4));
    if(r1_time_status_get())return;
    uint32_t now=r1_time_backend_timestamp();
    if(now>UINT32_C(0x38640900) || !read16(out))return;
    uint32_t offset_hours=read16(base+144)/60u;
    if(hour>=offset_hours)r1_hrv_cache_future_record_guard(0,0,(uint8_t)(hour-offset_hours),out,now);
    write32(out,0);write16(out+4,0);
}
void r1_activity_daily_cache_read(uint32_t hour,volatile uint8_t *out,uint32_t size)
{
    (void)size;volatile uint8_t *base=r1_activity_daily_cache_accessor();
    if(!base){clear(out,24);return;}
    copy(out,at(base,hour*24u),24);
    if(r1_time_status_get())return;
    uint32_t now=r1_time_backend_timestamp();
    if(now>UINT32_C(0x38640900))return;
    for(uint32_t i=0;i<6;++i){
        if(!read32(out+i*4u))continue;
        uint32_t offset_hours=read16(base+576)/60u;
        if(hour>=offset_hours)r1_activity_flash_record_enqueue_plan(0,0,(uint8_t)(hour-offset_hours),out,now);
        clear(out,24);return;
    }
}
uint32_t r1_stress_daily_cache_reset(uint32_t timestamp,uint32_t offset)
{
    volatile uint8_t *base=r1_stress_daily_cache_accessor();clear(base,72);write16(base+72,offset);r1_daily_stress_timestamp=timestamp;return (uint32_t)(uintptr_t)base+72u;
}
uint32_t r1_temperature_daily_cache_reset(uint32_t timestamp,uint32_t offset)
{
    volatile uint8_t *base=r1_temperature_daily_cache_accessor();clear(base,72);write16(base+72,offset);r1_daily_temperature_timestamp=timestamp;return (uint32_t)(uintptr_t)base+72u;
}
struct hour_descriptor {const volatile uint8_t *meta;void (*read)(uint32_t,volatile uint8_t *,uint32_t);uint32_t (*reset)(uint32_t,uint32_t);};
static const struct hour_descriptor descriptors[6]={
 {r1_health_sync_kind0,r1_heart_rate_daily_cache_read,r1_heart_rate_daily_cache_reset},
 {r1_health_sync_kind1,r1_spo2_daily_cache_read,r1_spo2_daily_cache_reset},
 {r1_health_sync_kind2,r1_temperature_daily_cache_read,r1_temperature_daily_cache_reset},
 {r1_health_sync_kind3,r1_stress_daily_cache_read,r1_stress_daily_cache_reset},
 {r1_health_sync_kind4,r1_activity_daily_cache_read,r1_activity_daily_cache_reset},
 {r1_health_sync_kind5,r1_hrv_daily_cache_read,r1_hrv_daily_cache_reset}
};
static void log_error(uint32_t value,const char *ring,const char *sdk)
{
    if(ring_enabled())(void)r1_structured_log_format(0x0c400000,ring,ring,value);
    if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(0x001c0003,sdk,value);
}
void r1_health_hour_boundary_storage_orchestrator(uint32_t argument)
{
    uint32_t hour=(uint8_t)argument;
    log_error(hour,"[RING]db_storage append hour:%d","db_storage append hour:%d");
    if(hour>=24)return;
    uint32_t slot=hour?hour-1u:23u;
    uint8_t *buffer=pvPortMalloc(128);
    if(!buffer)return;
    memset(buffer,0,128);
    write16(buffer,(uint32_t)r1_time_utc_offset_get());write32(buffer+4,r1_time_backend_timestamp());
    uint32_t cursor=(uint32_t)(uintptr_t)buffer+8u;
    for(uint32_t i=0;i<6;++i){
        const volatile struct hour_descriptor *entry=&descriptors[i];
        void (*reader)(uint32_t,volatile uint8_t *,uint32_t)=entry->read;
        if(reader)reader(slot,(volatile uint8_t *)(uintptr_t)cursor,entry->meta[1]);
        cursor+=entry->meta[1];
    }
    struct fdb_blob blob;
    fdb_err_t status=fdb_tsl_append(&r1_health_database_storage.database,fdb_blob_make(&blob,buffer,128));
    if(status!=FDB_NO_ERR){
        log_error(status,"[RING]db_storage append failed, error:%d","db_storage append failed, error:%d");
        if(status==3){
            fdb_tsl_clean(&r1_health_database_storage.database);
            status=fdb_tsl_append(&r1_health_database_storage.database,fdb_blob_make(&blob,buffer,128));
            log_error(status,"[RING]retry append result:%d","retry append result:%d");
        }
    }
    vPortFree(buffer);
    if(slot!=23)return;
    uint32_t midnight=r1_time_local_day_start();uint32_t offset=(uint16_t)r1_time_utc_offset_get();
    if(ring_enabled())(void)r1_structured_log_format(0x0c800000,"[RING]db_storage clean cache data, zero_ts:%d,%d","[RING]db_storage clean cache data, zero_ts:%d,%d",midnight,offset);
    if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_2(0x001c0003,"db_storage clean cache data, zero_ts:%d,%d",midnight,offset);
    for(uint32_t i=0;i<6;++i){uint32_t (*reset)(uint32_t,uint32_t)=((const volatile struct hour_descriptor *)descriptors)[i].reset;if(reset)(void)reset(midnight,offset);}
}
