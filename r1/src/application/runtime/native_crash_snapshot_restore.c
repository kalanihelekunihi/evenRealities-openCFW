/* Stock 0x59ee4, locked R1 application 2.2.6.0009. Reconstructed C.
 * Uses the existing retained context, cache accessors and hourly record owner. */
#include "native_crash_recovery.h"
#include "../board/native_battery_memory.h"
extern volatile uint8_t *r1_activity_daily_cache_accessor(void),*r1_hr_daily_cache_accessor(void),*r1_spo2_daily_cache_accessor(void),*r1_hrv_daily_cache_accessor(void);
extern void r1_shared_hourly_accumulator_restore(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t),nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t),nrf_log_frontend_std_5(uint32_t,const char *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
static uint32_t ring_enabled(void){return (r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u);}
static volatile uint8_t *at(volatile uint8_t *base,uint32_t offset){return (volatile uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)base+offset);}
void r1_health_crash_snapshot_restore(void)
{
    if(!r1_health_crash_record_magic_probe())return;
    volatile uint8_t snapshot[52];
    if(!r1_health_crash_snapshot_accessor(snapshot))return;
    uint32_t hour=snapshot[44];
    volatile uint8_t *cache;
    if((snapshot[45]&8u) && (cache=r1_activity_daily_cache_accessor())){
        uint32_t first=((hour*3u)&127u)*2u;
        for(uint32_t i=0;i<6;++i){
            volatile uint8_t *entry=at(cache,(first+i)*4u);
            const volatile uint8_t *value=snapshot+16u+i*4u;
            uint32_t packed=read32(entry);
            packed=(packed&~0xfffu)|((packed+read16(value))&0xfffu);
            write32(entry,packed);
            uint32_t field=(packed>>12)+(read16(value+1)>>4);
            packed=(packed&~0x003ff000u)|((field&0x3ffu)<<12);
            write32(entry,packed);
            field=(packed>>22)+(read16(value+2)>>6);
            packed=(packed&0x003fffffu)|((field&0x3ffu)<<22);
            write32(entry,packed);
        }
        if(ring_enabled())(void)r1_structured_log_format(0x0c400000,"[RING]db_storage crash activity restore, hour:%d","[RING]db_storage crash activity restore, hour:%d",hour);
        if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(0x001c0003,"db_storage crash activity restore, hour:%d",hour);
    }
    if((snapshot[45]&1u) && (cache=r1_hr_daily_cache_accessor())){
        volatile uint8_t *entry=at(cache,hour*3u);
        uint32_t value=snapshot[46];if(value)entry[0]=(uint8_t)value;
        value=snapshot[47];if(value>entry[1])entry[1]=(uint8_t)value;
        value=snapshot[48];if(value && (!entry[2] || value<entry[2]))entry[2]=(uint8_t)value;
        value=snapshot[49];if(value){cache[75]=(uint8_t)value;write32(cache+76,read32(snapshot));}
        uint32_t count=read16(snapshot+40);
        if(count)r1_shared_hourly_accumulator_restore(0,hour,read32(snapshot+4),count);
        if(ring_enabled())(void)r1_structured_log_format(0x0d400000,"[RING]db_storage crash hr restore, hour:%d avg:%d max:%d min:%d cnt:%d","[RING]db_storage crash hr restore, hour:%d avg:%d max:%d min:%d cnt:%d",hour,entry[0],entry[1],entry[2],read16(snapshot+40));
        if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_5(0x001c0003,"db_storage crash hr restore, hour:%d avg:%d max:%d min:%d cnt:%d",hour,entry[0],entry[1],entry[2],read16(snapshot+40));
    }
    if((snapshot[45]&2u) && (cache=r1_spo2_daily_cache_accessor()) && snapshot[50]){
        volatile uint8_t *entry=at(cache,hour*3u);
        if(!entry[0]){entry[0]=snapshot[50];entry[1]=snapshot[50];entry[2]=snapshot[50];}
        cache[75]=snapshot[50];write32(cache+76,read32(snapshot+8));
        if(ring_enabled())(void)r1_structured_log_format(0x0c800000,"[RING]db_storage crash spo2 restore, hour:%d spo2:%d","[RING]db_storage crash spo2 restore, hour:%d spo2:%d",hour,snapshot[50]);
        if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_2(0x001c0003,"db_storage crash spo2 restore, hour:%d spo2:%d",hour,snapshot[50]);
    }
    if((snapshot[45]&4u) && (cache=r1_hrv_daily_cache_accessor()) && read16(snapshot+42)){
        volatile uint8_t *entry=at(cache,hour*6u);
        if(!read16(entry)){write16(entry,read16(snapshot+42));write16(entry+2,read16(snapshot+42));write16(entry+4,read16(snapshot+42));}
        write16(cache+147,read16(snapshot+42));write32(cache+149,read32(snapshot+12));
        if(ring_enabled())(void)r1_structured_log_format(0x0c800000,"[RING]db_storage crash hrv restore, hour:%d hrv:%d","[RING]db_storage crash hrv restore, hour:%d hrv:%d",hour,read16(snapshot+42));
        if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_2(0x001c0003,"db_storage crash hrv restore, hour:%d hrv:%d",hour,read16(snapshot+42));
    }
    (void)r1_health_crash_snapshot_clear();
}
