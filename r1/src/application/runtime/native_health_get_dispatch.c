/* Health GET dispatcher at stock 0x8b8e8. Sample wire records are assembled
 * from the stock template's timezone, timestamp, marker and sample fields. */
#include <stdint.h>
#include "../board/native_battery_memory.h"
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
extern uint32_t r1_time_backend_timestamp(void);
extern int32_t r1_time_utc_offset_get(void);
extern volatile uint32_t r1_health_notification_last_timestamp;
extern uint32_t r1_hr_latest_sample(void *);
extern uint32_t r1_spo2_latest_sample(void *);
extern uint32_t r1_hrv_latest_sample(void *);
extern uint32_t r1_health_get_hr_encode(const volatile uint8_t *,uint32_t,uint32_t);
extern uint32_t r1_health_get_spo2_encode(const volatile uint8_t *,uint32_t,uint32_t);
extern uint32_t r1_health_get_hrv_encode(const volatile uint8_t *,uint32_t,uint32_t);
extern void r1_health_notification_stage_0008c150(uint32_t,uint32_t);
extern void r1_health_notification_stage_0008cd60(uint32_t,uint32_t);
extern void r1_health_notification_stage_0008c750(uint32_t,uint32_t);
extern void r1_health_notification_stage_0008baec(uint32_t,uint32_t);
extern void r1_health_notification_stage_0008b818(uint32_t,uint32_t);
extern uint32_t r1_event_publish(uint32_t,const void *,uint32_t);

const uint32_t r1_health_get_templates[7]
    __attribute__((section(".r1.health.get.templates"),aligned(4)))=
    {0,0x10000,0,0x10000,0,0x10000,0};

static void sample_header(volatile uint8_t *wire,uint32_t timestamp,
                          uint32_t type)
{
    const volatile uint8_t *source=(const volatile uint8_t *)
        &r1_health_get_templates[type==0u?0u:(type==1u?2u:4u)];
    for(uint32_t i=0;i<(type==5u?9u:8u);i++)wire[i]=source[i];
    write16(wire,(uint16_t)r1_time_utc_offset_get());
    write32(wire+2,timestamp);
}

void r1_event_service_0008b8e8(const void *payload)
{
    const volatile uint8_t *request=payload;
    const char *ring="[RING]proto health get module:%d, data_type:%d";
    if ((r1_structured_log_mode_get()&1u) ||
        (r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c800000u,ring,ring,
            request[0],request[1]);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_2(0x001c0003u,
            "proto health get module:%d, data_type:%d",request[0],request[1]);
    r1_health_notification_last_timestamp=r1_time_backend_timestamp();
    uint32_t type=request[0],data_type=request[1],sequence=read16(request+2);
    if(type==0u || type==1u || type==5u) {
        if(data_type==1u) {
            if(type==0u)r1_health_notification_stage_0008c150(sequence,0);
            else if(type==1u)r1_health_notification_stage_0008cd60(sequence,0);
            else r1_health_notification_stage_0008c750(sequence,0);
            return;
        }
        if(data_type!=0u)return;
        uint8_t sample[8]={0};
        uint8_t wire[9]={0};
        uint32_t found;
        if(type==0u)found=r1_hr_latest_sample(sample);
        else if(type==1u)found=r1_spo2_latest_sample(sample);
        else found=r1_hrv_latest_sample(sample);
        if(type==1u && found && (uint32_t)(sample[0]-70u)>30u)found=0;
        if(found) {
            sample_header(wire,read32((const volatile uint8_t *)sample+4),type);
            if(type==5u) {
                wire[7]=sample[0];wire[8]=sample[1];
                (void)r1_health_get_hrv_encode(wire,0,sequence);
            } else {
                wire[7]=sample[0];
                if(type==0u)(void)r1_health_get_hr_encode(wire,0,sequence);
                else (void)r1_health_get_spo2_encode(wire,0,sequence);
            }
        } else {
            if(type==0u)(void)r1_health_get_hr_encode(0,0,sequence);
            else if(type==1u)(void)r1_health_get_spo2_encode(0,0,sequence);
            else (void)r1_health_get_hrv_encode(0,0,sequence);
        }
        return;
    }
    if(type==4u) {
        if(data_type==1u)r1_health_notification_stage_0008baec(sequence,0);
        else if(data_type==0u)(void)r1_event_publish(4105,0,0);
    } else if(type==6u && data_type==1u) {
        r1_health_notification_stage_0008b818(1,sequence);
    }
}
