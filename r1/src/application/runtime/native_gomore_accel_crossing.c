#include "native_gomore_accel_crossing.h"
#include "native_gomore_accel_crossing_period.h"
static int32_t half(uint32_t at) { return *(volatile int16_t *)(uintptr_t)at; }
static uint32_t index(uint32_t cursor, uint32_t distance, uint32_t length)
{
    uint32_t position = cursor - distance;
    if ((int32_t)position < 0) position += length;
    return (uint32_t)(int32_t)(int8_t)position;
}
static __attribute__((always_inline)) inline uint32_t positive_fill(uint32_t input, uint32_t length,
                                           uint32_t cursor, uint32_t begin,
                                           uint32_t end)
{
    uint32_t carried = 0, total = 0;
    for (uint32_t distance = length; (int32_t)distance >= (int32_t)(end + 1u); distance--) {
        int32_t value = half(input + index(cursor, distance, length) * 2u);
        if (value > 0) carried = (uint32_t)value;
    }
    for (uint32_t distance = end; (int32_t)distance >= (int32_t)begin; distance--) {
        int32_t value = half(input + index(cursor, distance, length) * 2u);
        if (value > 0) carried = (uint32_t)value;
        total += carried;
    }
    uint32_t count = end - begin + 1u;
    uint32_t mean = 0;
    if (count != 0) {
        if (total == 0x80000000u && count == UINT32_MAX) mean = total;
        else mean = (uint32_t)((int32_t)total / (int32_t)count);
    }
    return (uint32_t)(int32_t)(int16_t)mean;
}
uint32_t r1_gomore_accel_positive_fill_native(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e){return positive_fill(a,b,c,d,e);}
static __attribute__((noinline,noclone)) uint32_t accepted(uint32_t value)
{
    return value + 0xbd900000u <= 0x01000000u ? value : 0;
}
uint32_t r1_gomore_accel_crossing_native(uint32_t state, uint32_t input,
                                       uint32_t mode2_output, uint32_t mode1_output)
{
    /* The shared inline baseline and this reserved word give the recorded
       GCC9 -O1 build a 40-byte frame, exposing mode1 at entry SP-36 and
       mode2 at entry SP-32 to the native period boundary. */
    volatile struct {uint32_t mode1, mode2, pad;} frame;
    frame.mode2 = 0; frame.mode1 = 0;
    uint32_t cursor = (uint32_t)(int32_t)*(volatile int8_t *)(uintptr_t)(state + 82u);
    uint32_t baseline = positive_fill(state + 50u, 8, cursor, 1, 8);
    (void)r1_gomore_accel_crossing_period_native(-1.0f,input,(uint32_t)(uintptr_t)&frame.mode2,2,baseline);
    (void)r1_gomore_accel_crossing_period_native(-1.0f,input,(uint32_t)(uintptr_t)&frame.mode1,1,baseline);
    uint32_t value = frame.mode2;
    *(volatile uint32_t *)(uintptr_t)mode2_output = accepted(value);
    value = frame.mode1;
    *(volatile uint32_t *)(uintptr_t)mode1_output = accepted(value);
    return 0;
}
