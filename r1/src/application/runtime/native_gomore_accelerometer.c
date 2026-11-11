#include <stdint.h>
#include <stddef.h>
#include "../board/native_battery_memory.h"
#include "../goodix/stock_gsensor_callbacks.h"

volatile uint8_t r1_gomore_accelerometer_count __attribute__((section(".r1.gomore.accelerometer.count")))=0;
volatile uint32_t r1_gomore_accelerometer_handle __attribute__((section(".r1.gomore.accelerometer.handle"),aligned(4)))=0;
volatile int16_t r1_gomore_accelerometer_samples[75] __attribute__((section(".bss.r1.gomore.accelerometer.samples"),aligned(2)));
extern uint32_t r1_sensor_stream_register_by_name(const char *,const char *,uintptr_t,uint32_t,uint32_t);
extern void r1_sensor_stream_unregister_by_name(const char *,uint32_t);
extern void *r1_native_memory_move(void *,const void *,size_t);

static uint16_t signed_half(uint16_t value)
{ return (uint16_t)((value>>1)|(value&0x8000u)); }

/* Native stream-dispatch ABI. The first and third arguments are unused. */
void r1_native_gomore_accelerometer_sample(void *node __attribute__((unused)),
        uint32_t payload,uint32_t length __attribute__((unused)))
{
    volatile uint8_t *input=(volatile uint8_t *)(uintptr_t)payload;
    if (read16(input+180)>25u) write16(input+180,25);
    uint32_t index=0;
    while (read16(input+180)>index) {
        uint32_t offset=index*6u;
        volatile uint8_t *source=(volatile uint8_t *)(uintptr_t)(payload+offset);
        volatile uint8_t *dest=(volatile uint8_t *)(uintptr_t)
            ((uint32_t)(uintptr_t)r1_gomore_accelerometer_samples+offset);
        /* Each source read follows the preceding destination store. */
        write16(dest,signed_half(read16(source)));
        write16(dest+2,signed_half(read16(source+2)));
        write16(dest+4,signed_half(read16(source+4)));
        index=(uint8_t)(index+1u);
    }
    r1_gomore_accelerometer_count=input[180];
}
void r1_native_gomore_accelerometer_read(int16_t *samples,uint16_t *count)
{
    uint32_t captured=r1_gomore_accelerometer_count;
    write16((volatile uint8_t *)count,captured);
    (void)r1_native_memory_move(samples,(const void *)(uintptr_t)r1_gomore_accelerometer_samples,captured*6u);
}
void r1_native_gomore_accelerometer_open(void)
{
    if (!r1_gomore_accelerometer_handle)
        r1_gomore_accelerometer_handle=r1_sensor_stream_register_by_name(
            "acc","gh",(uintptr_t)r1_native_gomore_accelerometer_sample,1,0);
}
void r1_native_gomore_accelerometer_close(void)
{
    uint32_t handle=r1_gomore_accelerometer_handle;
    if (handle) {
        r1_sensor_stream_unregister_by_name("acc",handle);
        r1_gomore_accelerometer_handle=0;
    }
}
uint32_t r1_native_health_handlers_register(void)
{
    return r1_goodix_gsensor_register((uintptr_t)r1_native_gomore_accelerometer_open,
        (uintptr_t)r1_native_gomore_accelerometer_close,
        (uintptr_t)r1_native_gomore_accelerometer_read);
}
