#include <stdint.h>
#include "native_float_to_signed.h"
#include "../board/native_battery_memory.h"

extern volatile uint8_t r1_wear_adt_history[20],r1_wear_adt_active,r1_wear_adt_status;
extern volatile uint8_t r1_wear_sleep_status,r1_health_mode_byte;
extern volatile uint32_t r1_wear_adt_stream;
volatile uint32_t r1_wear_living_stream
    __attribute__((section(".r1.wear.living.stream"),aligned(4)))=0;
volatile uint32_t r1_wear_living_timestamp
    __attribute__((section(".bss.r1.wear.living.timestamp"),aligned(4)));
volatile uint8_t r1_wear_living_status __attribute__((section(".bss.r1.wear.living.status")));
volatile uint8_t r1_wear_ir_off_count __attribute__((section(".bss.r1.wear.ir_off.count")));
volatile uint8_t r1_wear_quiet_count __attribute__((section(".bss.r1.wear.quiet.count")));
extern uint32_t osKernelGetTickCount(void),r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
extern uint32_t r1_sensor_stream_register_by_name(const char *,const char *,uintptr_t,uint32_t,uint32_t);
extern void r1_sensor_stream_unregister_by_name(const char *,uint32_t);
extern void r1_wear_living_topic_callback(uint32_t,uint32_t,uint32_t);

static uint32_t latest_at(uint32_t index)
{
    uintptr_t address=(uintptr_t)r1_wear_adt_history+index*4u-4u;
    return read32((const volatile uint8_t *)address);
}
/* GCC strict FP preserves the native signaling comparison and FPSCR. */
__attribute__((noinline,noclone)) static int variance_below(float value)
{
    return value < 40.0f;
}
static uint32_t truncate_bits(float value)
{
    return r1_native_float_to_signed32(value);
}
static void change_mode_and_release(void)
{
    uint32_t sleep=r1_wear_sleep_status;
    r1_health_mode_byte=sleep==1?1:0;
    if (sleep!=1) {
        uint32_t stream=r1_wear_living_stream;
        if (stream) {
            r1_sensor_stream_unregister_by_name("wear",stream);
            r1_wear_living_stream=0;
        }
    }
}

void r1_wear_off_decision(void *statistics)
{
    uint32_t now=osKernelGetTickCount();
    if ((uint32_t)(now-r1_wear_living_timestamp)>2048u && r1_health_mode_byte==1 &&
        !r1_wear_adt_status && !r1_wear_living_stream) {
        uint32_t stream=r1_sensor_stream_register_by_name("wear","algo",
            (uintptr_t)r1_wear_living_topic_callback,1,1);
        r1_wear_living_stream=stream;
    }
    if ((uint32_t)(now-r1_wear_living_timestamp)<=2048u) {
        uint32_t status=r1_wear_living_status;
        if (!status) r1_health_mode_byte=0;
        else if (status==1) r1_health_mode_byte=2;
        r1_wear_ir_off_count=0;r1_wear_quiet_count=0;
        return;
    }
    uint32_t active;
    if (r1_wear_adt_stream && (active=r1_wear_adt_active)!=0 &&
        latest_at(active)<UINT32_C(0x8a1790)) {
        uint32_t count=(uint8_t)(r1_wear_ir_off_count+1u);
        r1_wear_ir_off_count=(uint8_t)count;
        if (count>=5) {
            change_mode_and_release();
            r1_wear_ir_off_count=0;
            if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) {
                uint32_t sleep=r1_wear_sleep_status,latest=latest_at(r1_wear_adt_active);
                (void)r1_structured_log_format(0x0c800000,
                    "[RING]algo wear ir-off: %d, sleep_status: %d",
                    "[RING]algo wear ir-off: %d, sleep_status: %d",latest,sleep);
            }
            if (r1_structured_log_mode_get()&2u) {
                uint32_t index=r1_wear_adt_active,sleep=r1_wear_sleep_status;
                uint32_t latest=latest_at(index);
                nrf_log_frontend_std_2(0x001c0003,"algo wear ir-off: %d, sleep_status: %d",latest,sleep);
            }
        }
        r1_wear_quiet_count=0;
        return;
    }
    volatile float *values=(volatile float *)statistics;
    union {float f;uint32_t u;} mean={.f=values[1]};
    uint32_t magnitude=mean.u&UINT32_C(0x7fffffff);
    int quiet=0;
    if ((uint32_t)(magnitude+UINT32_C(0xbb8cffff))<UINT32_C(0x137fff) &&
        variance_below(values[3]) && variance_below(values[4]) && variance_below(values[5])) quiet=1;
    r1_wear_ir_off_count=0;
    if (!quiet) {r1_wear_quiet_count=0;return;}
    uint32_t count=(uint8_t)(r1_wear_quiet_count+1u);
    r1_wear_quiet_count=(uint8_t)count;
    if (count<60) return;
    change_mode_and_release();
    r1_wear_quiet_count=0;
    uint32_t converted=truncate_bits(values[1]);
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) {
        uint32_t sleep=r1_wear_sleep_status;
        (void)r1_structured_log_format(0x0c800000,
            "[RING]algo wear table-off: %d, sleep_status: %d",
            "[RING]algo wear table-off: %d, sleep_status: %d",converted,sleep);
    }
    if (r1_structured_log_mode_get()&2u) {
        uint32_t sleep=r1_wear_sleep_status;
        nrf_log_frontend_std_2(0x001c0003,"algo wear table-off: %d, sleep_status: %d",converted,sleep);
    }
}
