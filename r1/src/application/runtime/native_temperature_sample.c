#include <stdint.h>

extern volatile uint8_t r1_temperature_timing_record[14];
extern volatile uint32_t r1_temperature_mode_handles[3];
extern volatile uint8_t r1_health_mode_byte;
/* ZI106 @2001e3ea; ends exactly before the next native system state. */
volatile uint8_t r1_temperature_sleep_capture[106]
    __attribute__((section(".bss.r1.temperature.sleep.capture"),aligned(2)));
struct __attribute__((packed,may_alias)) temperature_half { uint16_t value; };
static uint16_t read_half(const volatile void *p)
{ return ((const volatile struct temperature_half *)p)->value; }
static void write_half(volatile void *p,uint16_t value)
{ ((volatile struct temperature_half *)p)->value=value; }
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void r1_sensor_stream_unregister_by_name(const char *,uint32_t);
extern uint32_t r1_event_publish(uint32_t,const void *,uint32_t);

uint32_t r1_health_mode_is_2(void)
{ return r1_health_mode_byte==2; }

uint32_t r1_temperature_sample_valid(const volatile void *sample)
{ return (uint32_t)(read_half(sample)-30000u)<20001u; }

uint32_t r1_temperature_sample_consistent(uint32_t sample)
{
    uint32_t count=r1_temperature_timing_record[10];
    for (uint32_t i=0;i<count;i++) {
        uint32_t previous=read_half((const volatile void *)(uintptr_t)
            ((uint32_t)(uintptr_t)r1_temperature_timing_record+(i<<1)));
        uint32_t difference=previous<sample ? sample-previous : previous-sample;
        if ((uint16_t)difference>300) return 0;
    }
    return 1;
}

void r1_temperature_timing_publish(void)
{
    if (r1_temperature_timing_record[10]<5) return;
    uint32_t sum=0;
    for (uint32_t i=0;i<5;i++)
        sum+=read_half(r1_temperature_timing_record+(i<<1));
    uint32_t average=(uint16_t)(sum/5);
    volatile uint32_t packet[2]={0,0};
    uint16_t first=(uint16_t)(uint32_t)((double)average*0.01);
    write_half(packet,first);
    uint16_t second=(uint16_t)(uint32_t)((double)average*0.1);
    if (r1_temperature_sleep_capture[0]==1 && r1_temperature_sleep_capture[2]<50) {
        uint32_t index=r1_temperature_sleep_capture[2];
        write_half(r1_temperature_sleep_capture+4+(index<<1),second);
        r1_temperature_sleep_capture[2]=(uint8_t)(r1_temperature_sleep_capture[2]+1u);
    }
    if (r1_health_mode_is_2())
        (void)r1_event_publish(9,(const void *)packet,8);
}

void r1_temperature_stream_sample_callback(uint32_t handle,uint32_t data,uint32_t length)
{
    (void)length;
    uint32_t attempts=(uint8_t)(r1_temperature_timing_record[11]+1u);
    r1_temperature_timing_record[11]=(uint8_t)attempts;
    if (attempts>30) {
        if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
            (void)r1_structured_log_format(0x08400000,"[RING]Temperature measurement timeout after %d calls","[RING]Temperature measurement timeout after %d calls",30);
        if (r1_structured_log_mode_get()&2u)
            nrf_log_frontend_std_1(0x001c0002,"Temperature measurement timeout after %d calls",30);
    } else {
        const volatile void *sample=(const volatile void *)(uintptr_t)data;
        if (!r1_temperature_sample_valid(sample)) return;
        if (!r1_temperature_sample_consistent(read_half(sample))) {
            r1_temperature_timing_record[10]=0;
            return;
        }
        uint32_t index=r1_temperature_timing_record[10];
        write_half((volatile void *)(uintptr_t)
            ((uint32_t)(uintptr_t)r1_temperature_timing_record+(index<<1)),read_half(sample));
        uint32_t count=(uint8_t)(r1_temperature_timing_record[10]+1u);
        r1_temperature_timing_record[10]=(uint8_t)count;
        if (count<5) return;
        r1_temperature_timing_publish();
    }
    r1_sensor_stream_unregister_by_name("temp",handle);
    r1_temperature_mode_handles[1]=0;
}
